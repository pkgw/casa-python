import os, re
import string
import time
import shutil
from taskinit import casalog, mstool, qa, tbtool, write_history
from update_spw import update_spwchan
from parallel.parallel_task_helper import ParallelTaskHelper
import partitionhelper as ph

def split(vis, outputvis, datacolumn, field, spw, width, antenna,
          timebin, timerange, scan, intent, array, uvrange,
          correlation, observation, combine, keepflags, keepmms):
    """Create a visibility subset from an existing visibility set:

    Keyword arguments:
    vis -- Name of input visibility file (MS)
            default: none; example: vis='ngc5921.ms'
    outputvis -- Name of output visibility file (MS)
                  default: none; example: outputvis='ngc5921_src.ms'
    datacolumn -- Which data column to split out
                  default='corrected'; example: datacolumn='data'
                  Options: 'data', 'corrected', 'model', 'all',
                  'float_data', 'lag_data', 'float_data,data', and
                  'lag_data,data'.
                  note: 'all' = whichever of the above that are present.
    field -- Field name
              default: field = '' means  use all sources
              field = 1 # will get field_id=1 (if you give it an
                          integer, it will retrieve the source with that index)
              field = '1328+307' specifies source '1328+307'.
                 Minimum match can be used, egs  field = '13*' will
                 retrieve '1328+307' if it is unique or exists.
                 Source names with imbedded blanks cannot be included.
    spw -- Spectral window index identifier
            default=-1 (all); example: spw=1
    antenna -- antenna names
               default '' (all),
               antenna = '3 & 7' gives one baseline with antennaid = 3,7.
    timebin -- Interval width for time averaging.
               default: '0s' or '-1s' (no averaging)
               example: timebin='30s'
    timerange -- Time range
                 default='' means all times.  examples:
                 timerange = 'YYYY/MM/DD/hh:mm:ss~YYYY/MM/DD/hh:mm:ss'
                 timerange='< YYYY/MM/DD/HH:MM:SS.sss'
                 timerange='> YYYY/MM/DD/HH:MM:SS.sss'
                 timerange='< ddd/HH:MM:SS.sss'
                 timerange='> ddd/HH:MM:SS.sss'
    scan -- Scan numbers to select.
            default '' (all).
    intent -- Scan intents to select.
            default '' (all).
    array -- (Sub)array IDs to select.     
             default '' (all).
    uvrange -- uv distance range to select.
               default '' (all).
    correlation -- Select correlations, e.g. 'rr, ll' or ['XY', 'YX'].
                   default '' (all).
    observation -- Select by observation ID(s).
                   default '' (all).
    combine -- Data descriptors that time averaging can ignore:
                  scan, and/or state
                  Default '' (none)
    keepflags -- Keep flagged data, if possible
                 Default True

    keepmms -- If the input is a multi-MS, make the output one, too. (experimental)
               Default: False
                 
    """

    casalog.origin('split')
    rval = True
    try:

        if (keepmms and ParallelTaskHelper.isParallelMS(vis)): 
            if (timebin!='0s' and timebin!='-1s'): 
                casalog.post('Averaging over time and keeping the MMS structure may lead to time averaging results\n'
                             +'different from those obtained with keepmms=False.', 'WARN')
                            
            myms = mstool()
            myms.open(vis)
            mses = myms.getreferencedtables()
            myms.close() 
            mses.sort()

            retval = {}
            nfail = 0
            if os.path.exists(outputvis):
                raise ValueError, "Output MS %s already exists - will not overwrite." % outputvis
            tempout = outputvis+str(time.time())
            os.mkdir(tempout)
            successfulmses = []
            mastersubms = ''
            masterptab = ''
            emptyptab = tempout+'/EMPTY_POINTING'
            nochangeinpointing = (str(antenna)+str(timerange)=='')
                
            for m in mses:
                # resulting pointing table is the same for all
                #  -> replace by empty table if it is a link and won't be modified anyway
                #     and put back original into the master after split
                theptab = m+'/POINTING'
                replaced = False
                if nochangeinpointing:
                    if(os.path.islink(theptab)):
                        os.remove(theptab)
                        shutil.copytree(emptyptab, theptab)
                        replaced=True
                    elif(masterptab==''):
                        mastersubms = m
                        masterptab = m+'/POINTING'
                        # save time by not copying the POINTING table len(mses) times
                        mytb = tbtool()
                        mytb.open(masterptab)
                        tmpp = mytb.copy(newtablename=emptyptab, norows=True)
                        mytb.close()
                        tmpp.close()
                        
                outvis = tempout+'/'+os.path.basename(m)
                print 'Running split_core on ', m
                try:
                    retval[m] = split_core(m, outvis, datacolumn, field, spw, width, antenna,
                                           timebin, timerange, scan, intent, array, uvrange,
                                           correlation, observation, combine, keepflags)
                except Exception, instance:
                    casalog.post("*** Error while processing SubMS "+m+": %s" % (instance), 'SEVERE')
                    raise
       
                if replaced:
                    # restore link
                    shutil.rmtree(theptab, ignore_errors=True)
                    os.symlink('../'+os.path.basename(mastersubms)+'/POINTING', theptab)
                    # (link in target will be created my makeMMS)

                if not retval[m]:
                    nfail+=1
                else:
                    successfulmses.append(outvis)

            if nfail>0:
                if len(successfulmses)==0:
                    casalog.post('Split failed in all subMSs.', 'WARN')
                    rval=False
                else:
                    casalog.post('*** Summary: there were failures in '+str(nfail)+' SUBMSs:', 'WARN')
                    casalog.post('*** (these may be harmless if they are caused by selection):', 'WARN')
                    for m in mses:
                        if not retval[m]:
                            casalog.post(os.path.basename(m)+': '+str(retval[m]), 'WARN')
                        else:
                            casalog.post(os.path.basename(m)+': '+str(retval[m]), 'NORMAL') 

                    casalog.post('Will construct MMS from subMSs with successful selection ...', 'NORMAL')

                    if nochangeinpointing: # need to take care of POINTING table
                        # in case the master subms did not make it
                        if not (tempout+'/'+os.path.basename(mastersubms) in successfulmses):
                            # old master subms was not selected.
                            # copy the original masterptab into the new master
                            shutil.rmtree(successfulmses[0]+'/POINTING')
                            shutil.copytree(masterptab, successfulmses[0]+'/POINTING')
                    
            if rval:
                # construct new MMS from the output
                if(width==1 and str(field)+str(spw)+str(antenna)+str(timerange)+str(scan)+str(intent)\
                   +str(array)+str(uvrange)+str(correlation)+str(observation)==''):
                    ph.makeMMS(outputvis, successfulmses)
                else:
                    myms.open(successfulmses[0], nomodify=False)
                    auxfile = "split_aux_"+str(time.time())
                    for i in xrange(1,len(successfulmses)):
                        myms.virtconcatenate(successfulmses[i], auxfile, '1Hz', '10mas')
                    myms.close()
                    os.remove(auxfile)
                    ph.makeMMS(outputvis, successfulmses, True, ['POINTING']) 


            shutil.rmtree(tempout, ignore_errors=True)



        else: # do not output an MMS

            rval = split_core(vis, outputvis, datacolumn, field, spw, width, antenna,
                              timebin, timerange, scan, intent, array, uvrange,
                              correlation, observation, combine, keepflags)

    except Exception, instance:
            casalog.post("*** Error: %s" % (instance), 'SEVERE')
            rval = False
       

    return rval

def split_core(vis, outputvis, datacolumn, field, spw, width, antenna,
               timebin, timerange, scan, intent, array, uvrange,
               correlation, observation, combine, keepflags):

    retval = True

    if not outputvis or outputvis.isspace():
        raise ValueError, 'Please specify outputvis'

    myms = mstool()
    if ((type(vis)==str) & (os.path.exists(vis))):
        myms.open(vis, nomodify=True)
    else:
        raise ValueError, 'Visibility data set not found - please verify the name'
    if os.path.exists(outputvis):
        myms.close()
        raise ValueError, "Output MS %s already exists - will not overwrite." % outputvis

    # No longer needed.  When did it get put in?  Note that the default
    # spw='*' in myms.split ends up as '' since the default type for a variant
    # is BOOLVEC.  (Of course!)  Therefore both split and myms.split must
    # work properly when spw=''.
    #if(spw == ''):
    #    spw = '*'
    
    if(type(antenna) == list):
        antenna = ', '.join([str(ant) for ant in antenna])

    ## Accept digits without units ...assume seconds
    timebin = qa.convert(qa.quantity(timebin), 's')['value']
    timebin = str(timebin) + 's'
    
    if timebin == '0s':
        timebin = '-1s'

    # MSStateGram is picky ('CALIBRATE_WVR.REFERENCE, OBSERVE_TARGET_ON_SOURCE'
    # doesn't work, but 'CALIBRATE_WVR.REFERENCE,OBSERVE_TARGET_ON_SOURCE'
    # does), and I don't want to mess with bison now.  A .upper() might be a
    # good idea too, but the MS def'n v.2 does not say whether OBS_MODE should
    # be case-insensitive.
    intent = intent.replace(', ', ',')

    if '^' in spw:
        casalog.post("The interpretation of ^n in split's spw strings has changed from 'average n' to 'skip n' channels!", 'WARN')
        casalog.post("Watch for Slicer errors", 'WARN')
        
    if type(width) == str:
        try:
            if(width.isdigit()):
                width=[string.atoi(width)]
            elif(width.count('[') == 1 and width.count(']') == 1):
                width = width.replace('[', '')
                width = width.replace(']', '')
                splitwidth = width.split(',')
                width = []
                for ws in splitwidth:
                    if(ws.isdigit()):
                        width.append(string.atoi(ws)) 
            else:
                width = [1]
        except:
            raise TypeError, 'parameter width is invalid...using 1'

    if type(correlation) == list:
        correlation = ', '.join(correlation)
    correlation = correlation.upper()

    if hasattr(combine, '__iter__'):
        combine = ', '.join(combine)

    if type(spw) == list:
        spw = ','.join([str(s) for s in spw])
    elif type(spw) == int:
        spw = str(spw)
    do_chan_mod = spw.find('^') > -1     # '0:2~11^1' would be pointless.
    if not do_chan_mod:                  # ...look in width.
        if type(width) == int and width > 1:
            do_chan_mod = True
        elif hasattr(width, '__iter__'):
            for w in width:
                if w > 1:
                    do_chan_mod = True
                    break

    do_both_chan_and_time_mod = (do_chan_mod and
                                 string.atof(timebin[:-1]) > 0.0)
    if do_both_chan_and_time_mod:
        # Do channel averaging first because it might be included in the spw
        # string.
        import tempfile
        # We want the directory outputvis is in, not /tmp, because /tmp
        # might not have enough space.
        # outputvis is itself a directory, so strip off a trailing slash if
        # it is present.
        # I don't know if giving tempfile an absolute directory is necessary -
        # dir='' is effectively '.' in Ubuntu.
        workingdir = os.path.abspath(os.path.dirname(outputvis.rstrip('/')))
        cavms = tempfile.mkdtemp(suffix=outputvis, dir=workingdir)

        casalog.post('Channel averaging to ' + cavms)
        if not myms.split(outputms=cavms,     field=field,
                          spw=spw,            step=width,
                          baseline=antenna,   subarray=array,
                          timebin='',         time=timerange,
                          whichcol=datacolumn,
                          scan=scan,          uvrange=uvrange,
                          combine=combine,
                          correlation=correlation, intent=intent,
                          obs=str(observation)):
            myms.close()
            if os.path.isdir(cavms):
                import shutil
                shutil.rmtree(cavms)
            return False
        
        # The selection was already made, so blank them before time averaging.
        field = ''
        spw = ''
        width = [1]
        antenna = ''
        array = ''
        timerange = ''
        datacolumn = 'all'
        scan = ''
        intent = ''
        uvrange = ''
        observation = ''

        myms.close()
        myms.open(cavms)
        casalog.post('Starting time averaging')

    if keepflags:
        taqlstr = ''
    else:
        taqlstr = 'NOT (FLAG_ROW OR ALL(FLAG))'

    if not myms.split(outputms=outputvis,  field=field,
                      spw=spw,             step=width,
                      baseline=antenna,    subarray=array,
                      timebin=timebin,     time=timerange,
                      whichcol=datacolumn,
                      scan=scan,           uvrange=uvrange,
                      combine=combine,
                      correlation=correlation,
                      taql=taqlstr, intent=intent,
                      obs=str(observation)):
        myms.close()
        return False
    myms.close()

    if do_both_chan_and_time_mod:
        import shutil
        shutil.rmtree(cavms)

    # Write history to output MS, not the input ms.
    try:
        param_names = split_core.func_code.co_varnames[:split_core.func_code.co_argcount]
        param_vals = [eval(p) for p in param_names]   
        retval &= write_history(myms, outputvis, 'split', param_names, param_vals,
                                casalog)
    except Exception, instance:
        casalog.post("*** Error \'%s\' updating HISTORY" % (instance),
                     'WARN')

    # Update FLAG_CMD if necessary.
    if ((spw != '') and (spw != '*')) or do_chan_mod:
        isopen = False
        try:
            mytb = tbtool()
            mytb.open(outputvis + '/FLAG_CMD', nomodify=False)
            isopen = True
            #print "is open"
            nflgcmds = mytb.nrows()
            #print "nflgcmds =", nflgcmds
            if nflgcmds > 0:
                mademod = False
                cmds = mytb.getcol('COMMAND')
                widths = {}
                #print "width =", width
                if hasattr(width, 'has_key'):
                    widths = width
                else:
                    if hasattr(width, '__iter__') and len(width) > 1:
                        for i in xrange(len(width)):
                            widths[i] = width[i]
                    elif width != 1:
                        #print 'using myms.msseltoindex + a scalar width'
                        nspw = len(myms.msseltoindex(vis=vis,
                                                     spw='*')['spw'])
                        if hasattr(width, '__iter__'):
                            w = width[0]
                        else:
                            w = width
                        for i in xrange(nspw):
                            widths[i] = w
                #print 'widths =', widths 
                for rownum in xrange(nflgcmds):
                    # Matches a bare number or a string quoted any way.
                    spwmatch = re.search(r'spw\s*=\s*(\S+)', cmds[rownum])
                    if spwmatch:
                        sch1 = spwmatch.groups()[0]
                        sch1 = re.sub(r"[\'\"]", '', sch1)  # Dequote
                        # Provide a default in case the split selection excludes
                        # cmds[rownum].  update_spwchan() will throw an exception
                        # in that case.
                        cmd = ''
                        try:
                            #print 'sch1 =', sch1
                            sch2 = update_spwchan(vis, spw, sch1, truncate=True,
                                                  widths=widths)
                            #print 'sch2 =', sch2
                            ##print 'spwmatch.group() =', spwmatch.group()
                            if sch2:
                                repl = ''
                                if sch2 != '*':
                                    repl = "spw='" + sch2 + "'"
                                cmd = cmds[rownum].replace(spwmatch.group(), repl)
                        #except: # cmd[rownum] no longer applies.
                        except Exception, e:
                            casalog.post(
                                "Error %s updating row %d of FLAG_CMD" % (e,
                                                                          rownum),
                                         'WARN')
                            casalog.post('sch1 = ' + sch1, 'DEBUG1')
                            casalog.post('cmd = ' + cmd, 'DEBUG1')
                        if cmd != cmds[rownum]:
                            mademod = True
                            cmds[rownum] = cmd
                if mademod:
                    casalog.post('Updating FLAG_CMD', 'INFO')
                    mytb.putcol('COMMAND', cmds)

            
        except Exception, instance:
            casalog.post("*** Error \'%s\' updating FLAG_CMD" % (instance),
                         'SEVERE')
            retval = False
        finally:
            if isopen:
                casalog.post('Closing FLAG_CMD', 'DEBUG1')
                mytb.close()
    return retval
