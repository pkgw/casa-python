import os
from taskinit import *

import sdutil
import asap as sd
from asap._asap import Scantable
from asap import _to_list
from asap.scantable import is_scantable
import math
import pylab as pl

def sdbaseline(infile, antenna, fluxunit, telescopeparm, specunit, restfreq, frame, doppler, scanlist, field, iflist, pollist, tau, masklist, maskmode, thresh, avg_limit, edge, blfunc, order, npiece, applyfft, fftmethod, fftthresh, addwn, rejwn, clipthresh, clipniter, verify, verbose, bloutput, blformat, showprogress, minnrow, outfile, outform, overwrite, plotlevel):
    
    casalog.origin('sdbaseline')
    
    try:
        worker = sdbaseline_worker(**locals())
        worker.initialize()
        worker.execute()
        worker.finalize()
	
    except Exception, instance:
        sdutil.process_exception(instance)
        raise Exception, instance

class sdbaseline_worker(sdutil.sdtask_template):
    def __init__(self, **kwargs):
        super(sdbaseline_worker,self).__init__(**kwargs)
        self.suffix = '_bs'

    def initialize_scan(self):
        sorg = sd.scantable(self.infile, average=False, antenna=self.antenna)
        
        sel = self.get_selector()
        sorg.set_selection(sel)
        del sel

        # Copy scantable when usign disk storage not to modify
        # the original table.
        if is_scantable(self.infile) and \
               sd.rcParams['scantable.storage'] == 'disk':
            self.scan = sorg.copy()
        else:
            self.scan = sorg
        del sorg

    def execute(self):
        prior_plot(self.scan, self.plotlevel)

        # check if the data contains spectra
        if (self.scan.nchan()==1):
           s = "Cannot process the input data. It contains only single channel data."
           raise Exception, s
   
        # set various attributes to self.scan
        self.set_to_scan()
        
        scanns = self.scan.getscannos()
        sn=list(scanns)
        casalog.post( "Number of scans to be processed: %d" % (len(sn)) )
        
        # Warning for multi-IF data
        #if ( len(s.getifnos()) > 1 and not maskmode == 'auto' ):
        if ( len(self.scan.getifnos()) > 1 and isinstance(self.masklist,list) and not self.maskmode == 'auto' ):
            casalog.post( 'The scantable contains multiple IF data.', priority = 'WARN' )
            casalog.post( 'Note the same mask(s) are applied to all IFs based on CHANNELS.', priority = 'WARN' )
            casalog.post( 'Baseline ranges may be incorrect for all but IF=%d.' % (self.scan.getif(0)), priority = 'WARN' )
            
        # do opacity (atmospheric optical depth) correction
        sdutil.doopacity(self.scan, self.tau)
    
        if (self.order < 0):
            casalog.post('Negative order of baseline polynomial given. Exit without baselining.', priority = 'WARN')
            return
        self.blfile = init_blfile(**self.__dict__)

        dobaseline(**self.__dict__)

        # Plot final spectrum
        posterior_plot(self.scan, self.project, self.plotlevel)

    def save(self):
        sdutil.save(self.scan, self.project, self.outform, self.overwrite)

def init_blfile(scan=None, infile=None, project=None, **kwargs):
    maskmode = kwargs['maskmode']
    blfunc = kwargs['blfunc']
    modeparams = {'auto': ['thresh', 'avg_limit', 'edge'],
                  'list': ['masklist'],
                  'clip': ['clipthresh', 'clipniter']}
    blfparams = {'poly': ['order'],
                 'chevishev': ['order']+modeparams['clip'],
                 'cspline': ['npiece']+modeparams['clip'],
                 'sinusoid': ['applyfft', 'fftmethod', 'fftthresh',
                              'addwn', 'rejwn']+modeparams['clip']}
              

def init_blfile(scan=None, infile=None, project=None, masklist=None, maskmode=None, thresh=None, avg_limit=None, edge=None, blfunc=None, order=None, npiece=None, applyfft=None, fftmethod=None, fftthresh=None, addwn=None, rejwn=None, clipthresh=None, clipniter=None, bloutput=None, blformat=None, **kwargs):
        if bloutput:
                blfile = project + "_blparam.txt"

                if (blformat.lower() != "csv"):
                        blf = open(blfile, "w")

                        # Header data for saving parameters of baseline fit
                        header =  "Source Table: "+infile+"\n"
                        header += " Output File: "+project+"\n"
                        header += "   Flux Unit: "+scan.get_fluxunit()+"\n"
                        header += "    Abscissa: "+scan.get_unit()+"\n"
                        header += "    Function: "+blfunc+"\n"
                        if blfunc == 'poly':
                                header += "   Fit order: %d\n"%(order)
                        elif blfunc == 'chebyshev':
                                header += "   Fit order: %d\n"%(order)
                                header += "  clipThresh: %f\n"%(clipthresh)
                                header += "   clipNIter: %d\n"%(clipniter)
                        elif blfunc == 'cspline':
                                header += "      nPiece: %d\n"%(npiece)
                                header += "  clipThresh: %f\n"%(clipthresh)
                                header += "   clipNIter: %d\n"%(clipniter)
                        elif blfunc == 'sinusoid':
                                header += "    applyFFT: "+str(applyfft)+"\n"
                                header += "   fftMethod: "+fftmethod+"\n"
                                header += "   fftThresh: "+str(fftthresh)+"\n"
                                header += "    addWaveN: "+str(addwn)+"\n"
                                header += "    rejWaveN: "+str(rejwn)+"\n"
                                header += "  clipThresh: %f\n"%(clipthresh)
                                header += "   clipNIter: %d\n"%(clipniter)
                        header += "   Mask mode: "+maskmode+"\n"
                        if maskmode == 'auto':
                                header += "   Threshold: %f\n"%(thresh)
                                header += "   avg_limit: %d\n"%(avg_limit)
                                header += "        Edge: "+str(edge)+"\n"
                        elif maskmode == 'list':
                                header += "   Fit Range: "+str(masklist)+"\n"

                        separator = "#"*60 + "\n"

                        blf.write(separator)
                        blf.write(header)
                        blf.write(separator)
                        blf.close()
        else:
                blfile = ""
        return blfile
        

def dobaseline(scan=None, blfile=None, masklist=None, maskmode=None, thresh=None, avg_limit=None, edge=None, blfunc=None, order=None, npiece=None, applyfft=None, fftmethod=None, fftthresh=None, addwn=None, rejwn=None, clipthresh=None, clipniter=None, verify=None, verbose=None, blformat=None, showprogress=None, minnrow=None, **kwargs):
        if (order < 0):
                casalog.post('Negative order of baseline polynomial given. Exit without baselining.', priority = 'WARN')
                return

        csvformat = (blformat.lower() == "csv")

        nrow = scan.nrow()

        # parse string masklist
        if isinstance(masklist,list):
                maskdict = {'': masklist}
        else:
                maskdict = scan.parse_maskexpr(masklist)
        basesel = scan.get_selection()
        for sif, lmask in maskdict.iteritems():
                if len(sif) > 0:
                        #s.set_selection(selection=(basesel+sd.selector(ifs=[int(sif)])))
                        sel = sd.selector(basesel)
                        sel.set_ifs([int(sif)])
                        scan.set_selection(sel)
                        del sel
                        msg = "Working on IF%s" % (sif)
                        casalog.post(msg)
                        if (maskmode == 'interact'): print "===%s===" % (msg)
                        del msg

                msk = None

                if (maskmode == 'interact'):
                        msk = sdutil.interactive_mask(s, lmask, False, purpose='to baseline spectra')
                        msks = scan.get_masklist(msk)
                        if len(msks) < 1:
                                casalog.post( 'No channel is selected. Exit without baselining.', priority = 'WARN' )
                                return

                        casalog.post( 'final mask list ('+scan._getabcissalabel()+') ='+str(msks) )
                        #header += "   Fit Range: "+str(msks)+"\n"
                        del msks
                else:
                        # Use baseline mask for regions to INCLUDE in baseline fit
                        # Create mask using list, e.g. masklist=[[500,3500],[5000,7500]]
                        if (len(lmask) > 0): msk = scan.create_mask(lmask)


                if (maskmode == 'auto'):
                        if (blfunc == 'poly'):
                                scan.auto_poly_baseline(mask=msk,order=order,edge=edge,threshold=thresh,chan_avg_limit=avg_limit,plot=verify,showprogress=showprogress,minnrow=minnrow,outlog=verbose,blfile=blfile,csvformat=csvformat,insitu=True)
                        elif (blfunc == 'chebyshev'):
                                scan.auto_chebyshev_baseline(mask=msk,order=order,clipthresh=clipthresh,clipniter=clipniter,edge=edge,threshold=thresh,chan_avg_limit=avg_limit,plot=verify,showprogress=showprogress,minnrow=minnrow,outlog=verbose,blfile=blfile,csvformat=csvformat,insitu=True)
                        elif (blfunc == 'cspline'):
                                scan.auto_cspline_baseline(mask=msk,npiece=npiece,clipthresh=clipthresh,clipniter=clipniter,edge=edge,threshold=thresh,chan_avg_limit=avg_limit,plot=verify,showprogress=showprogress,minnrow=minnrow,outlog=verbose,blfile=blfile,csvformat=csvformat,insitu=True)
                        elif (blfunc == 'sinusoid'):
                                scan.auto_sinusoid_baseline(mask=msk,applyfft=applyfft,fftmethod=fftmethod,fftthresh=fftthresh,addwn=addwn,rejwn=rejwn,clipthresh=clipthresh,clipniter=clipniter,edge=edge,threshold=thresh,chan_avg_limit=avg_limit,plot=verify,showprogress=showprogress,minnrow=minnrow,outlog=verbose,blfile=blfile,csvformat=csvformat,insitu=True)
                else:
                        if (blfunc == 'poly'):
                                scan.poly_baseline(mask=msk,order=order,plot=verify,showprogress=showprogress,minnrow=minnrow,outlog=verbose,blfile=blfile,csvformat=csvformat,insitu=True)
                        elif (blfunc == 'chebyshev'):
                                scan.chebyshev_baseline(mask=msk,order=order,clipthresh=clipthresh,clipniter=clipniter,plot=verify,showprogress=showprogress,minnrow=minnrow,outlog=verbose,blfile=blfile,csvformat=csvformat,insitu=True)
                        elif (blfunc == 'cspline'):
                                scan.cspline_baseline(mask=msk,npiece=npiece,clipthresh=clipthresh,clipniter=clipniter,plot=verify,showprogress=showprogress,minnrow=minnrow,outlog=verbose,blfile=blfile,csvformat=csvformat,insitu=True)
                        elif (blfunc == 'sinusoid'):
                                scan.sinusoid_baseline(mask=msk,applyfft=applyfft,fftmethod=fftmethod,fftthresh=fftthresh,addwn=addwn,rejwn=rejwn,clipthresh=clipthresh,clipniter=clipniter,plot=verify,showprogress=showprogress,minnrow=minnrow,outlog=verbose,blfile=blfile,csvformat=csvformat,insitu=True)

                # the above 14 lines will eventually shrink into the following 2 commands:
                #
                #sbinfo = s.create_sbinfo(blfunc=blfunc,order=order,npiece=npiece,applyfft=applyfft,fftmethod=fftmethod,fftthresh=fftthresh,addwn=addwn,rejwn=rejwn,\
                #                         masklist=masklist,maskmode=maskmode,edge=edge,threshold=threshold,chan_avg_limit=chan_avg_limit,\
                #                         clipthresh=clipthresh,clipniter=clipniter)
                #s.sub_baseline(sbinfo=sbinfo,plot=verify,showprogress=showprogress,minnrow=minnrow,outlog=verbose,blfile=blfile)
                #
                # where
                # sbinfo = {'func':funcinfo, 'mask':maskinfo, 'clip':clipinfo}
                # and
                # funcinfo should be one of the follows:
                #     funcinfo = {'type':'poly', 'params':{'order':order}}
                #     funcinfo = {'type':'cspline', 'params':{'npiece':npiece}}
                #     funcinfo = {'type':'sspline', 'params':{'lambda':lambda}}
                #     funcinfo = {'type':'sinusoid', 'params':{'applyfft':applyfft, 'fftmethod':fftmethod, 'fftthresh':fftthresh, 'addwn':addwn, 'rejwn':rejwn}}
                # maskinfo should be one of the follows:
                #     maskinfo = {'base':masklist, 'aux':{'type':'auto', 'params':{'edge':edge, 'threshold':thresh, 'chan_avg_limit':avg_limit}}}
                #     maskinfo = {'base':masklist, 'aux':{'type':'list'}}
                #     maskinfo = {'base':masklist, 'aux':{'type':'interactive'}}
                # clipinfo should be:
                #     clipinfo = {'clipthresh':clipthresh, 'clipniter':clipniter}

                del msk

                # reset selection
                if len(sif) > 0: scan.set_selection(basesel)

        ### END of IF loop
        del basesel

def prior_plot(s, plotlevel):
    if ( abs(plotlevel) > 1 ):
        casalog.post( "Initial Raw Scantable:" )
        s._summary()

def posterior_plot(s, project, plotlevel):
    if ( abs(plotlevel) > 0 ):
        pltfile=project+'_bsspec.eps'
        sdutil.plot_scantable(s, pltfile, plotlevel)
