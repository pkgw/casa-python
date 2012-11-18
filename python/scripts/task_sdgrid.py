# sd task for imaging
import os
import numpy
import pylab as pl
import asap as sd
from taskinit import *
import sdutil

@sdutil.sdtask_decorator
def sdgrid(infile, antenna, scanlist, ifno, pollist, gridfunction, convsupport, truncate, gwidth, jwidth, weight, clipminmax, outfile, overwrite, npix, cell, center, plot):
    worker = sdgrid_worker(**locals())
    worker.initialize()
    worker.execute()
    worker.finalize()
        

class sdgrid_worker(sdutil.sdtask_interface):
    def __init__(self, **kwargs):
        super(sdgrid_worker,self).__init__(**kwargs)
        self.suffix = '.grid'
        self.gridder = None

    def initialize(self):
        self.parameter_check()
        self.__summarize_raw_inputs()
        self.__compile()
        self.__summarize_compiled_inputs()

        # create gridder
        self.gridder = sd.asapgrid(infile=self.infile)

    def parameter_check(self):
        if self.gridfunction.upper() == 'PB':
            msg='Sorry. PB gridding is not implemented yet.'
            raise Exception, msg
        elif self.gridfunction.upper() == 'BOX':
            casalog.post('convsupport is automatically set to -1 for BOX gridding.', priority='WARN')
            self.convsupport = -1

    def execute(self):
        # actual gridding
        self.gridder.setPolList(self.pols)
        self.gridder.setScanList(self.scans)
        if self.ifno >= 0:
            self.gridder.setIF(self.ifno)
        if self.clipminmax:
            self.gridder.enableClip()
        else:
            self.gridder.disableClip()
        self.gridder.setWeight(self.weight) 
        self.gridder.defineImage(nx=self.nx, ny=self.ny,
                                 cellx=self.cellx, celly=self.celly,
                                 center=self.mapcenter)
        self.gridder.setFunc(func=self.gridfunction,
                             convsupport=self.convsupport,
                             truncate=str(self.truncate),
                             gwidth=str(self.gwidth),
                             jwidth=str(self.jwidth))
        self.gridder.grid()

    def finalize(self):
        # save result
        self.gridder.save(outfile=self.outname)

        # plot result if necessary
        if self.plot:
            self.gridder.plot()
            
    def __compile(self):
        # infile
        if isinstance(self.infile, str):
            self.infile = [self.infile]

        # scanlist
        self.scans = sdutil._to_list(self.scanlist, int)

        # pollist
        self.pols = sdutil._to_list(self.pollist, int)

        # outfile
        self.outname = sdutil.get_default_outfile_name(self.infile[0],
                                                       self.outfile,
                                                       self.suffix)
        sdutil.assert_outfile_canoverwrite_or_nonexistent(self.outname,
                                                          'ASAP',
                                                          self.overwrite)
        
        # nx and ny
        (self.nx, self.ny) = sdutil.get_nx_ny(self.npix)

        # cellx and celly
        (self.cellx, self.celly) = sdutil.get_cellx_celly(self.cell)

        # map center
        self.mapcenter = sdutil.get_map_center(self.center)

    def __summarize_raw_inputs(self):
        params = ['infile', 'antenna', 'scanlist', 'ifno',
                  'pollist', 'gridfunction', 'convsupport',
                  'truncate', 'gwidth', 'jwidth', 'weight',
                  'clipminmax', 'outfile', 'overwrite',
                  'npix', 'cell', 'center', 'plot']
        summary = self.__generate_summary(header='Input Parameter Summary',
                                          params=params)
        casalog.post(summary, priority='DEBUG')

    def __summarize_compiled_inputs(self):
        params = ['infile', 'ifno', 'scans', 'pols',
                  'gridfunction', 'convsupport',
                  'truncate', 'gwidth', 'jwidth', 'weight',
                  'clipminmax', 'outname', 'overwrite',
                  'nx', 'ny', 'cellx', 'celly',
                  'mapcenter', 'plot']
        summary = self.__generate_summary(header='Grid Parameter Summary',
                                          params=params)
        casalog.post(summary, priority='DEBUG')
        
    def __generate_summary(self, header, params):
        summary = header+':\n'
        for p in params:
            summary += '   %12s = %s\n'%(p,getattr(self,p))
        return summary

    
