import os
from taskinit import *

import sdutil
import asap as sd
from asap.flagplotter import flagplotter
import pylab as pl
from numpy import ma, array, logical_not, logical_and

def sdflag(infile, antenna, specunit, restfreq, frame, doppler, scanlist, field, iflist, pollist, maskflag, flagrow, clip, clipminmax, clipoutside, flagmode, interactive, showflagged, outfile, outform, overwrite, plotlevel):

        casalog.origin('sdflag')

        try:
            myp=None
            if infile=='':
                raise Exception, 'infile is undefined'

            filename = os.path.expandvars(infile)
            filename = os.path.expanduser(filename)
            if not os.path.exists(filename):
                s = "File '%s' not found." % (filename)
                raise Exception, s

	    if (outfile != ''):
	        project = outfile.rstrip('/')
	    else:
	        project = infile.rstrip('/')
	        if not overwrite:
		    project = project + '_f'

            outfilename = os.path.expandvars(project)
            outfilename = os.path.expanduser(outfilename)
            if not overwrite and os.path.exists(outfilename):
		    s = "Output file '%s' exists." % (outfilename)
                    raise Exception, s

            sorg = sd.scantable(infile,average=False,antenna=antenna)

	    # Copy the original data (CAS-3987)
	    if (sd.rcParams['scantable.storage'] == 'disk') and (project != infile.rstrip('/')):
		    s = sorg.copy()
	    else:
		    s = sorg
	    del sorg

	    # set restfreq
	    modified_molid = False
	    if (specunit == 'km/s'):
		    if (restfreq == '') and (len(s.get_restfreqs()[0]) == 0):
			    mesg = "Restfreq must be given."
			    raise Exception, mesg
		    elif (len(str(restfreq)) > 0):
			    molids = s._getmolidcol_list()
			    s.set_restfreqs(sdutil.normalise_restfreq(restfreq))
			    modified_molid = True

            #check the format of the infile
            if isinstance(infile, str):
		    if os.path.isdir(filename) and os.path.exists(filename+'/table.info'):
			    if os.path.exists(filename+'/table.f1'):
				    format = 'MS2'
			    else:
				    format = 'ASAP'
		    else:
			    format = 'SDFITS'

	    # Check the formats of infile and outfile are identical when overwrite=True.
	    # (CAS-3096). If not, print warning message and exit.
	    outformat = outform.upper()
	    if (outformat == 'MS'): outformat = 'MS2'
	    if overwrite and (project == infile.rstrip('/')) and (outformat != format):
		    msg = "The input and output data format must be identical when "
		    msg += "their names are identical and overwrite=True. "
		    msg += "%s and %s given for input and output, respectively." % (format, outformat)
	            raise Exception, msg
	    
            # Do at least one
	    docmdflag = True
	    if (len(flagrow) == 0) and (len(maskflag) == 0) and (not clip):
                    if not interactive:
			    raise Exception, 'No flag operation specified.'
		    # interactive flagging only
                    docmdflag = False

            if ( abs(plotlevel) > 1 ):
                    casalog.post( "Initial Scantable:" )
                    #casalog.post( s._summary() )
                    s._summary()

            # Default file name
            #if ( outfile == '' ):
            #        project = infile + '_f'
            #elif ( outfile == 'none' ):
            #        project = infile 
            #        outform = format
            #        overwrite=True
            #else:
            #        project = outfile

            # get telescope name
            #'ATPKSMB', 'ATPKSHOH', 'ATMOPRA', 'DSS-43' (Tid), 'CEDUNA', and 'HOBART'

            unit_in=s.get_unit()
	    # set default spectral axis unit
	    if ( specunit != '' ):
		    s.set_unit(specunit)

	    # reset frame and doppler if needed
	    if ( frame != '' ):
		    s.set_freqframe(frame)
	    else:
		    casalog.post( 'Using current frequency frame' )
	    
	    if ( doppler != '' ):
		    if ( doppler == 'radio' ):
			    ddoppler = 'RADIO'
		    elif ( doppler == 'optical' ):
			    ddoppler = 'OPTICAL'
		    elif ( doppler == 'z' ):
			    ddoppler = 'Z'
		    else:
			    ddoppler = doppler
			
		    s.set_doppler(ddoppler)
	    else:
		    casalog.post( 'Using current doppler convention' )


            # Select scan and field
            sel = sd.selector()


            # Set up scanlist
            if ( type(scanlist) == list ):
                    # is a list
                    scans = scanlist
            else:
                    # is a single int, make into list
                    scans = [ scanlist ]
            # Now select them
            if ( len(scans) > 0 ):
                    sel.set_scans(scans)

            # Select source names
            if ( field != '' ):
                    sel.set_name(field)
                    # NOTE: currently can only select one
                    # set of names this way, will probably
                    # need to do a set_query eventually

            # Select IFs
            if ( type(iflist) == list ):
                    # is a list
                    ifs = iflist
            else:
                    # is a single int, make into list
                    ifs = [ iflist ]
            if ( len(ifs) > 0 ):
                    # Do any IF selection
                    sel.set_ifs(ifs)

            # Select Pol
            if ( type(pollist) == list ):
                    pols = pollist
            else:
                    pols = [ pollist ] 
            if ( len(pols) > 0 ):
                    sel.set_polarisations(pols)

            try:
		    #Apply the selection
		    s.set_selection(sel)
	    except Exception, instance:
		    casalog.post( str(instance), priority = 'ERROR' )
		    raise Exception, instance


            # flag mode
	    flgmode = flagmode.lower()
            if (flgmode == 'flag'):
                    unflag = False
            elif (flgmode == 'unflag'):
                    unflag = True
            else:
                    raise Exception, 'unexpected flagmode'

            nr=s.nrow()

            if clip:
                    casalog.post("Number of spectra to be flagged: %d" % (nr) )
                    casalog.post("Applying clipping...")
                    if len(flagrow) > 0 or len(maskflag) > 0:
                            casalog.post("flagrow and maskflag will be ignored",priority = 'WARN')
            elif len(flagrow) == 0:
                    # Channel based flag
                    casalog.post( "Number of spectra to be flagged: %d" % (nr) )
                    casalog.post( "Applying channel flagging..." )
            else:
                    # Row flagging
                    casalog.post( "Number of rows to be flagged: %d" % (len(flagrow)) )
                    casalog.post( "Applying row flagging..." )
                    if len(maskflag) > 0:
                            casalog.post("maskflag will be ignored",priority = 'WARN')


	    dthres = uthres = None
	    if isinstance(clipminmax, list):
		    if (len(clipminmax) == 2):
			    dthres = min(clipminmax)
			    uthres = max(clipminmax)
			    
	    
            #channel flag
            if (len(maskflag) > 0):
                    masks = s.create_mask(maskflag)

            #for row in range(ns):
            if docmdflag and ( abs(plotlevel) > 0 ):
                    from matplotlib import rc as rcp
                    rcp('lines', linewidth=1)
                    #sc=s.copy()
		    # Plot final spectrum
                    np = nr
		    if nr >16:
                            np = 16
			    casalog.post( "Only first 16 spectra is plotted.", priority = 'WARN' )

                    #if not myp or myp.is_dead:
                    if not (myp and myp._alive()):
                        from asap.asapplotter import new_asaplot
                        if plotlevel > 0:
                            visible = sd.rcParams['plotter.gui']
                        else:
                            visible = False                        
                        myp = new_asaplot(visible=visible)

                    myp.hold()
                    myp.clear()
                    myp.set_panels(rows=np,cols=0,nplots=np)
                    myp.legend(loc=1)
                    colours = ["green","red","#dddddd","#777777"]
                    rowlist = range(np)
                    for row in rowlist:
                        myp.subplot(row)
                        myp.palette(0,colours)
                        if row==rowlist[0]:
                          myp.set_line(label='Spectrum')
                        else:
                          myp.set_line(label='spec')
                        x = s._getabcissa(row)
                        y = s._getspectrum(row)
                        nchan = len(y)
			
			if s._getflagrow(row):
				oldmskarr = array([False]*(nchan))
			else:
				oldmskarr = array(s._getmask(row))
				
			if clip:
			  if (uthres != None) and (dthres != None) and (uthres > dthres):
			    masks = array(s._getclipmask(row, uthres, dthres, clipoutside, unflag))
			  else:
			    masks = [False]*(nchan)
			elif (len(flagrow) > 0):
			  found = False
			  for i in range(0, len(flagrow)):
			    if (row == flagrow[i]):
			      found = True
			      break
			  masks = [found and not(unflag)]*(nchan)
			#marr = array(masks)
			
			marr = logical_not(array(masks))
			allmsk = logical_and(marr,oldmskarr)
                        ym = ma.masked_array(y,mask=logical_not(allmsk))
                        myp.plot(x,ym)
                        myp.palette(2)
                        if row==rowlist[0]:
                          myp.set_line(label='previously flagged data')
                        else:
                          myp.set_line(label='prev')
                        #oldmskarr = logical_not(oldmskarr)
                        ym = ma.masked_array(y,mask=oldmskarr)
                        myp.plot(x,ym)
                        myp.palette(1)
                        if row==rowlist[0]:
                          myp.set_line(label='current flag masks')
                        else:
                          myp.set_line(label='flag')
                        ym = ma.masked_array(y,mask=marr)
                        myp.plot(x,ym)
                        xlim=[min(x),max(x)]
                        myp.axes.set_xlim(xlim)
                    myp.release()

                    #Apply flag
                    if plotlevel > 0 and sd.rcParams['plotter.gui']:
                            ans=raw_input("Apply %s (y/N)?: " % flgmode)
                    else:
                            casalog.post("Applying selected flags")
                            ans = 'Y'
            else:
                    ans='Y'
            if docmdflag and ans.upper() == 'Y':
                    if (clip):
                            if (uthres != None) and (dthres != None) and (uthres > dthres):
                                    s.clip(uthres, dthres, clipoutside, unflag)
                    elif (len(flagrow) == 0):
                            s.flag(mask=masks,unflag=unflag)
                    else:
                            s.flag_row(flagrow, unflag)

                    params={}
                    if ( vars()['pols'] == [] ):
                            params['pols']=list(s.getpolnos())
                    else:
                            params['pols']=vars()['pols']
                    if ( vars()['ifs'] == [] ):
                            params['ifs']=list(s.getifnos())
                    else:
                            params['ifs']=vars()['ifs']
                    if ( vars()['scans'] == [] ):
                            params['scans']=list(s.getscannos())
                    else:
                            params['scans']=vars()['scans']
                    params['mode']=vars()['flagmode']
                    params['maskflag']=vars()['maskflag']
                    #print "input parameters:\n", params
                    s._add_history( "sdflag", params ) 


            anyflag = docmdflag
            if interactive:
                    from matplotlib import rc as rcp
                    rcp('lines', linewidth=1)
                    guiflagger = flagplotter(visible=True)
                    #guiflagger.set_legend(loc=1,refresh=False)
                    guiflagger.set_showflagged(showflagged)
                    guiflagger.plot(s)
                    finish=raw_input("Press enter to finish interactive flagging:")
                    guiflagger._plotter.unmap()
                    anyflag = (anyflag or guiflagger._ismodified)
                    guiflagger._plotter = None
                    del guiflagger

            if not anyflag:
                    del s, sel
                    raise Exception, 'No flag operation. Finish without saving'

            if ( abs(plotlevel) > 0 ):
                    #Plot the result
                    #print "Showing only the first spectrum..."
                    casalog.post( "Showing only the first spectrum..." )
                    #row=rowlist[0]
                    row=0
                    #if not myp or myp.is_dead:
                    if not (myp and myp._alive()):
                        from matplotlib import rc as rcp
                        rcp('lines', linewidth=1)
                        from asap.asapplotter import new_asaplot
                        myp = new_asaplot(visible=sd.rcParams['plotter.gui'])

                    myp.hold()
                    myp.clear()
                    colours = ["green","red","#dddddd","#777777"]
                    myp.palette(0,colours)
                    myp.set_panels()
                    myp.set_line(label="Spectrum after %s" % flgmode+'ging')
                    x = s._getabcissa(row)
                    y = s._getspectrum(row)
                    allmskarr=array(s._getmask(row))
                    #y = ma.masked_array(y,mask=marr)
                    ym = ma.masked_array(y,mask=logical_not(allmskarr))
                    myp.plot(x,ym)
                    myp.palette(2)
                    myp.set_line(label="Flagged")
                    #allmsk = logical_and(marr,oldmskarr)
                    #y = ma.masked_array(y,mask=logical_not(allmsk))
                    ym = ma.masked_array(y,mask=allmskarr)
                    myp.plot(x,ym)
                    xlim=[min(x),max(x)]
                    myp.axes.set_xlim(xlim)
                    if ( plotlevel < 0 ):
                            # Hardcopy - currently no way w/o screen display first
                            pltfile=project+'_flag.eps'
                            myp.save(pltfile)
                    myp.release()


            # Now save the spectrum and write out final ms
            if ( (outform == 'ASCII') or (outform == 'ascii') ):
                    outform = 'ASCII'
                    spefile = project + '_'
            elif ( (outform == 'ASAP') or (outform == 'asap') ):
                    outform = 'ASAP'
                    spefile = project
            elif ( (outform == 'SDFITS') or (outform == 'sdfits') ):
                    outform = 'SDFITS'
                    spefile = project
            elif ( (outform == 'MS') or (outform == 'ms') or (outform == 'MS2') or (outform == 'ms2') ):
                    outform = 'MS2'
                    spefile = project
            else:
                    outform = 'ASAP'
                    spefile = project

	    # Commented out on 19 Apr 2012. (CAS-3986)
            #if overwrite and os.path.exists(outfilename):
            #        os.system('rm -rf %s' % outfilename)
            
            #put back original spectral unit
            s.set_unit(unit_in) 
            sel.reset()
            s.set_selection(sel)

	    #restore the original moleculeID column
	    if modified_molid:
		    s._setmolidcol_list(molids)
	    
            s.save(spefile,outform,overwrite)
	    
            if outform!='ASCII':
                    casalog.post( "Wrote output "+outform+" file "+spefile )

            del s, sel

        except Exception, instance:
                casalog.post( str(instance), priority = 'ERROR' )
		raise Exception, instance
        finally:
                casalog.post('')
