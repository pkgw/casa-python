import os
import sys
import shutil
from __main__ import default
from tasks import *
from taskinit import *
import unittest
import sha
import time
import numpy
import re
import string

from sdimaging import sdimaging
import asap as sd

#
# Unit test of sdimaging task.
# 

###
# Base class for sdimaging unit test
###
class sdimaging_unittest_base:
    """
    Base class for sdimaging unit test

    Test data is originally FLS3_all_newcal_SP and created
    by the following script:

    asap_init()
    sd.rc('scantable',storage='disk')
    s=sd.scantable('FLS3_all_newcal_SP',average=False,getpt=False)
    s0=s.get_scan('FLS3a')
    s0.save('FLS3a_HI.asap')
    del s,s0
    s=sd.scantable('FLS3a_HI.asap',average=False)
    s.set_fluxunit('K')
    scannos=s.getscannos()
    res=sd.calfs(s,scannos)
    del s
    res.save('FLS3a_calfs','MS2')
    tb.open('FLS3a_calfs')
    tbsel=tb.query('SCAN_NUMBER<100')
    tbc=tbsel.copy('sdimaging.ms',deep=True,valuecopy=True)
    tbsel.close()
    tb.close()
    tbc.close()

    Furthermore, SYSCAL and POINTING tables are downsized.
    
    """
    taskname='sdimaging'
    datapath=os.environ.get('CASAPATH').split()[0] + '/data/regression/unittest/sdimaging/'
    rawfile='sdimaging.ms'
    postfix='.im'
    phasecenter='J2000 17:18:29 +59.31.23'
    imsize=[75,75]
    cell=['3.0arcmin','3.0arcmin']
    gridfunction='PB'
    statsinteg={'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                'blcf': '17:32:18.690, +57.37.28.536, I, 1.42064e+09Hz',
                'max': numpy.array([ 0.6109162]),
                'maxpos': numpy.array([4, 62,  0,  0], dtype=numpy.int32),
                'maxposf': '17:31:59.439, +60.43.52.421, I, 1.42064e+09Hz',
                'mean': numpy.array([ 0.39524983]),
                'min': numpy.array([ 0.]),
                'minpos': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                'minposf': '17:32:18.690, +57.37.28.536, I, 1.42064e+09Hz',
                'npts': numpy.array([ 5625.]),
                'rms': numpy.array([ 0.43127564]),
                'sigma': numpy.array([ 0.17257331]),
                'sum': numpy.array([ 2223.28028646]),
                'sumsq': numpy.array([ 1046.2425779]),
                'trc': numpy.array([74, 74,  0,  0], dtype=numpy.int32),
                'trcf': '17:03:03.151, +61.19.10.757, I, 1.42064e+09Hz'}
    keys=['max','mean','min','npts','rms','blc','blcf','trc','trcf','sigma','sum','sumsq']

    def _checkfile( self, name ):
        isthere=os.path.exists(name)
        self.assertEqual(isthere,True,
                         msg='output file %s was not created because of the task failure'%(name))

    def _checkshape(self,name,nx,ny,npol,nchan):
        self._checkfile(name)
        ia.open(name)
        imshape=ia.shape()
        ia.close()
        self.assertEqual(nx,imshape[0],
                    msg='nx does not match')
        self.assertEqual(ny,imshape[1],
                    msg='ny does not match')
        self.assertEqual(npol,imshape[2],
                    msg='npol does not match')
        self.assertEqual(nchan,imshape[3],
                    msg='nchan does not match')
        
    def _checkstats(self,name,ref):
        self._checkfile(name)
        ia.open(name)
        stats=ia.statistics()
        ia.close()
        #for key in stats.keys():
        for key in self.keys:
            message='statistics \'%s\' does not match'%(key)
            if type(stats[key])==str:
                self.assertEqual(stats[key],ref[key],
                                 msg=message)
            else:
                #print stats[key]-ref[key]
                ret=numpy.allclose(stats[key],ref[key])
                self.assertEqual(ret,True,
                                 msg=message)

###
# Test on bad parameter settings
###
class sdimaging_test0(sdimaging_unittest_base,unittest.TestCase):
    """
    Test on bad parameter setting
    """
    # Input and output names
    prefix=sdimaging_unittest_base.taskname+'Test0'
    badid=99
    outfile=prefix+sdimaging_unittest_base.postfix

    def setUp(self):
        if os.path.exists(self.rawfile):
            shutil.rmtree(self.rawfile)
        shutil.copytree(self.datapath+self.rawfile, self.rawfile)

        default(sdimaging)

    def tearDown(self):
        if (os.path.exists(self.rawfile)):
            shutil.rmtree(self.rawfile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test000(self):
        """Test 000: Default parameters"""
        # argument verification error
        res=sdimaging()
        self.assertFalse(res)

    def test001(self):
        """Test001: Bad specunit"""
        # argument verification error
        res=sdimaging(infile=self.rawfile,specunit='frequency',outfile=self.outfile)
        self.assertFalse(res)

    def test002(self):
        """Test002: Bad field id"""
        outfile=self.prefix+self.postfix
        try:
            res=sdimaging(infile=self.rawfile,field=self.badid,outfile=self.outfile)
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('field id %s does not exist'%(self.badid))
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test003(self):
        """Test003: Bad spectral window id"""
        try:
            res=sdimaging(infile=self.rawfile,spw=self.badid,outfile=self.outfile)
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('spw id %s does not exist'%(self.badid))
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test004(self):
        """Test004: Bad antenna id"""
        # not throw any exception, but return False
        res=sdimaging(infile=self.rawfile,antenna=self.badid,outfile=self.outfile)
        self.assertFalse(res)
        
    def test005(self):
        """Test005: Bad stokes parameter"""
        try:
            res=sdimaging(infile=self.rawfile,stokes='BAD',outfile=self.outfile)
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('Stokes selection BAD is currently not supported.')
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))
        
    def test006(self):
        """Test006: Bad gridfunction"""
        # argument verification error
        res=sdimaging(infile=self.rawfile,gridfunction='BAD',outfile=self.outfile)
        self.assertFalse(res)

    def test007(self):
        """Test007: Bad scanlist"""
        # empty selection, but not throw exception
        res=sdimaging(infile=self.rawfile,scanlist=[self.badid],outfile=self.outfile)
        self.assertFalse(res)

    def test008(self):
        """Test008: Existing outfile with overwrite=False"""
        f=open(self.outfile,'w')
        print >> f, 'existing file'
        f.close()
        try:
            res=sdimaging(infile=self.rawfile,outfile=self.outfile)
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('Output file \'%s\' exists.'%(self.outfile))
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test009(self):
        """Test009: Bad phasecenter string"""
        try:
            res=sdimaging(infile=self.rawfile,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter='This is bad')
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('Empty QuantumHolder argument for asQuantumDouble')
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test010(self):
        """Test010: Bad phasecenter reference (J2000 is assumed)"""
        # default for unknown direction frame is J2000 
        refimage=self.outfile+'2'
        sdimaging(infile=self.rawfile,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter.replace('J2000','J3000'))
        sdimaging(infile=self.rawfile,outfile=refimage,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter)
        tb.open(self.outfile)
        chunk=tb.getcol('map')
        tb.close()
        tb.open(refimage)
        refchunk=tb.getcol('map')
        tb.close()
        ret=all(chunk.flatten()==refchunk.flatten())
        #print ret
        self.assertTrue(ret)

    def test011(self):
        """Test011: Bad pointingcolumn name"""
        # argument verification error
        res=sdimaging(infile=self.rawfile,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,pointingcolumn='non_exist')
        self.assertFalse(res)

    def test012(self):
        """Test012: Bad imsize"""
        try:
            res=sdimaging(infile=self.rawfile,outfile=self.outfile,cell=self.cell,imsize=[0,0],phasecenter=self.phasecenter)
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('%s does not exist'%(self.outfile))
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))
        
    def test013(self):
        """Test013: Bad cell size"""
        # empty image will be created
        res=sdimaging(infile=self.rawfile,outfile=self.outfile,cell=[0.,0.],imsize=self.imsize,phasecenter=self.phasecenter)
        self.assertFalse(res)

    def test014(self):
        """Test014: Too fine resolution (smaller than original channel width"""
        try:
            res=sdimaging(infile=self.rawfile,specunit='GHz',outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction=self.gridfunction,dochannelmap=True,nchan=10,start=1.4202,step=1.0e-10)
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('calcChanFreqs failed, check input start and width parameters')
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))


###
# Test channel imaging
###
class sdimaging_test1(sdimaging_unittest_base,unittest.TestCase):
    """
    Test channel imaging

       - integrated image
       - full channel image
       - selected channel image
       - BOX and SF imaging (default is PB)
       - two polarization imaging (XX and YY, default is Stokes I)
       - empty phasecenter
       
    """
    # Input and output names
    prefix=sdimaging_unittest_base.taskname+'Test1'
    outfile=prefix+sdimaging_unittest_base.postfix
    mode='channel'

    def setUp(self):
        if os.path.exists(self.rawfile):
            shutil.rmtree(self.rawfile)
        shutil.copytree(self.datapath+self.rawfile, self.rawfile)

        default(sdimaging)

    def tearDown(self):
        if (os.path.exists(self.rawfile)):
            shutil.rmtree(self.rawfile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test100(self):
        """Test 100: Integrated image (dochannelmap=False)"""
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction=self.gridfunction,dochannelmap=False)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,1)
        refstats=self.statsinteg
        self._checkstats(self.outfile,refstats)

    def test101(self):
        """Test 101: Integrated image (dochannelmap=True,nchan=-1)"""
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction=self.gridfunction,dochannelmap=True,nchan=-1,start=0,step=1)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,1)
##         refstats={'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
##                   'blcf': '17:32:18.690, +57.37.28.536, I, 1.419395e+09Hz',
##                   'max': numpy.array([ 0.03589965]),
##                   'maxpos': numpy.array([60, 71,  0,  0], dtype=numpy.int32),
##                   'maxposf': '17:08:55.879, +61.12.09.501, I, 1.419395e+09Hz',
##                   'mean': numpy.array([ 0.01769218]),
##                   'min': numpy.array([ 0.]),
##                   'minpos': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
##                   'minposf': '17:32:18.690, +57.37.28.536, I, 1.419395e+09Hz',
##                   'npts': numpy.array([ 5625.]),
##                   'rms': numpy.array([ 0.01939845]),
##                   'sigma': numpy.array([ 0.007956]),
##                   'sum': numpy.array([ 99.51852731]),
##                   'sumsq': numpy.array([ 2.11668729]),
##                   'trc': numpy.array([74, 74,  0,  0], dtype=numpy.int32),
##                   'trcf': '17:03:03.151, +61.19.10.757, I, 1.419395e+09Hz'}
        refstats = {'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                    'blcf': '17:32:18.690, +57.37.28.536, I, 1.42064e+09Hz',
                    'max': numpy.array([ 0.6109162]),
                    'maxpos': numpy.array([ 4, 62,  0,  0], dtype=numpy.int32),
                    'maxposf': '17:31:59.439, +60.43.52.421, I, 1.42064e+09Hz',
                    'mean': numpy.array([ 0.39524983]),
                    'min': numpy.array([ 0.]),
                    'minpos': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                    'minposf': '17:32:18.690, +57.37.28.536, I, 1.42064e+09Hz',
                    'npts': numpy.array([ 5625.]),
                    'rms': numpy.array([ 0.43127564]),
                    'sigma': numpy.array([ 0.17257331]),
                    'sum': numpy.array([ 2223.28028646]),
                    'sumsq': numpy.array([ 1046.2425779]),
                    'trc': numpy.array([74, 74,  0,  0], dtype=numpy.int32),
                    'trcf': '17:03:03.151, +61.19.10.757, I, 1.42064e+09Hz'}
        self._checkstats(self.outfile,refstats)
        
    def test102(self):
        """Test 102: Full channel image"""
        tb.open(self.rawfile)
        if 'FLOAT_DATA' in tb.colnames():
            nchan=tb.getcell('FLOAT_DATA').shape[1]
        else:
            nchan=tb.getcell('DATA').shape[1]
        tb.close()
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction=self.gridfunction,dochannelmap=True,nchan=nchan,start=0,step=1)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,nchan)
        refstats={'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                  'blcf': '17:32:18.690, +57.37.28.536, I, 1.419395e+09Hz',
                  'max': numpy.array([ 24.77152824]),
                  'maxpos': numpy.array([ 59,  21,   0, 605], dtype=numpy.int32),
                  'maxposf': '17:10:00.642, +58.42.19.808, I, 1.420872e+09Hz',
                  'mean': numpy.array([ 0.39542111]),
                  'min': numpy.array([-1.84636593]),
                  'minpos': numpy.array([  73,    6,    0, 1023], dtype=numpy.int32),
                  'minposf': '17:04:54.966, +57.55.36.907, I, 1.421893e+09Hz',
                  'npts': numpy.array([ 5760000.]),
                  'rms': numpy.array([ 1.01357317]),
                  'sigma': numpy.array([ 0.93325921]),
                  'sum': numpy.array([ 2277625.60731485]),
                  'sumsq': numpy.array([ 5917423.42281288]),
                  'trc': numpy.array([  74,   74,    0, 1023], dtype=numpy.int32),
                  'trcf': '17:03:03.151, +61.19.10.757, I, 1.421893e+09Hz'}
        self._checkstats(self.outfile,refstats)

    def test103(self):
        """Test 103: Selected channel image"""
        nchan=40
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction=self.gridfunction,dochannelmap=True,nchan=nchan,start=400,step=10)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,nchan)
        refstats={'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                  'blcf': '17:32:18.690, +57.37.28.536, I, 1.42038e+09Hz',
                  'max': numpy.array([ 14.79568005]),
                  'maxpos': numpy.array([57, 20,  0, 20], dtype=numpy.int32),
                  'maxposf': '17:10:47.496, +58.39.30.813, I, 1.42087e+09Hz',
                  'mean': numpy.array([ 0.82293006]),
                  'min': numpy.array([-0.08763941]),
                  'minpos': numpy.array([61, 71,  0, 35], dtype=numpy.int32),
                  'minposf': '17:08:30.980, +61.12.02.893, I, 1.42124e+09Hz',
                  'npts': numpy.array([ 225000.]),
                  'rms': numpy.array([ 1.54734671]),
                  'sigma': numpy.array([ 1.31037237]),
                  'sum': numpy.array([ 185159.263672]),
                  'sumsq': numpy.array([ 538713.45272028]),
                  'trc': numpy.array([74, 74,  0, 39], dtype=numpy.int32),
                  'trcf': '17:03:03.151, +61.19.10.757, I, 1.42133e+09Hz'}
        self._checkstats(self.outfile,refstats)

    def test104(self):
        """Test 104: Box-car gridding"""
        nchan=40
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction='BOX',dochannelmap=True,nchan=nchan,start=400,step=10)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,nchan)
        refstats={'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                  'blcf': '17:32:18.690, +57.37.28.536, I, 1.42038e+09Hz',
                  'max': numpy.array([ 15.64525127]),
                  'maxpos': numpy.array([58, 20,  0, 20], dtype=numpy.int32),
                  'maxposf': '17:10:24.433, +58.39.25.476, I, 1.42087e+09Hz',
                  'mean': numpy.array([ 0.66097592]),
                  'min': numpy.array([-0.42533547]),
                  'minpos': numpy.array([69, 62,  0, 38], dtype=numpy.int32),
                  'minposf': '17:05:23.086, +60.44.01.427, I, 1.42131e+09Hz',
                  'npts': numpy.array([ 225000.]),
                  'rms': numpy.array([ 1.38591599]),
                  'sigma': numpy.array([ 1.2181464]),
                  'sum': numpy.array([ 148719.58227018]),
                  'sumsq': numpy.array([ 432171.72687429]),
                  'trc': numpy.array([74, 74,  0, 39], dtype=numpy.int32),
                  'trcf': '17:03:03.151, +61.19.10.757, I, 1.42133e+09Hz'}
        self._checkstats(self.outfile,refstats)

    def test105(self):
        """Test 105: Prolate Spheroidal gridding"""
        nchan=40
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction='SF',dochannelmap=True,nchan=nchan,start=400,step=10)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,nchan)
        refstats={'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                  'blcf': '17:32:18.690, +57.37.28.536, I, 1.42038e+09Hz',
                  'max': numpy.array([ 15.13189793]),
                  'maxpos': numpy.array([58, 21,  0, 20], dtype=numpy.int32),
                  'maxposf': '17:10:23.737, +58.42.25.413, I, 1.42087e+09Hz',
                  'mean': numpy.array([ 0.773227]),
                  'min': numpy.array([-0.07284018]),
                  'minpos': numpy.array([ 5, 67,  0, 30], dtype=numpy.int32),
                  'minposf': '17:31:41.090, +60.59.00.556, I, 1.42112e+09Hz',
                  'npts': numpy.array([ 225000.]),
                  'rms': numpy.array([ 1.49926317]),
                  'sigma': numpy.array([ 1.28449107]),
                  'sum': numpy.array([ 173976.07570213]),
                  'sumsq': numpy.array([ 505752.74505987]),
                  'trc': numpy.array([74, 74,  0, 39], dtype=numpy.int32),
                  'trcf': '17:03:03.151, +61.19.10.757, I, 1.42133e+09Hz'}
        self._checkstats(self.outfile,refstats)

    def test106(self):
        """Test 106: Imaging two polarization separately (XX and YY, not Stokes I)"""
        nchan=40
        res=sdimaging(infile=self.rawfile,specunit=self.mode,stokes='XXYY',outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction='PB',dochannelmap=True,nchan=nchan,start=400,step=10)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],2,nchan)
        refstats={'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                  'blcf': '17:32:18.690, +57.37.28.536, XX, 1.42038e+09Hz',
                  'max': numpy.array([ 15.057868]),
                  'maxpos': numpy.array([57, 20,  1, 20], dtype=numpy.int32),
                  'maxposf': '17:10:47.496, +58.39.30.813, YY, 1.42087e+09Hz',
                  'mean': numpy.array([ 0.82292841]),
                  'min': numpy.array([-0.41953856]),
                  'minpos': numpy.array([10,  3,  1, 31], dtype=numpy.int32),
                  'minposf': '17:28:37.170, +57.47.49.422, YY, 1.42114e+09Hz',
                  'npts': numpy.array([ 450000.]),
                  'rms': numpy.array([ 1.55436146]),
                  'sigma': numpy.array([ 1.31864787]),
                  'sum': numpy.array([ 370317.78554221]),
                  'sumsq': numpy.array([ 1087217.77687839]),
                  'trc': numpy.array([74, 74,  1, 39], dtype=numpy.int32),
                  'trcf': '17:03:03.151, +61.19.10.757, YY, 1.42133e+09Hz'}
        self._checkstats(self.outfile,refstats)

    def test107(self):
        """Test 107: Gaussian gridding"""
        nchan=40
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction='GAUSS',dochannelmap=True,nchan=nchan,start=400,step=10)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,nchan)
        refstats={'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                  'blcf': '17:32:18.690, +57.37.28.536, I, 1.42038e+09Hz',
                  'max': numpy.array([ 15.28046036]),
                  'maxpos': numpy.array([58, 21,  0, 20], dtype=numpy.int32),
                  'maxposf': '17:10:23.737, +58.42.25.413, I, 1.42087e+09Hz',
                  'mean': numpy.array([ 0.75082603]),
                  'min': numpy.array([-0.14009152]),
                  'minpos': numpy.array([34, 69,  0, 33], dtype=numpy.int32),
                  'minposf': '17:19:43.545, +61.07.22.487, I, 1.42119e+09Hz',
                  'npts': numpy.array([ 225000.]),
                  'rms': numpy.array([ 1.47686982]),
                  'sigma': numpy.array([ 1.2717751]),
                  'sum': numpy.array([ 168935.85698331]),
                  'sumsq': numpy.array([ 490757.49952306]),
                  'trc': numpy.array([74, 74,  0, 39], dtype=numpy.int32),
                  'trcf': '17:03:03.151, +61.19.10.757, I, 1.42133e+09Hz'}
        self._checkstats(self.outfile,refstats)

    def test108(self):
        """Test 108: Gaussian*Jinc gridding"""
        nchan=40
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction='GJINC',dochannelmap=True,nchan=nchan,start=400,step=10)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,nchan)
        refstats={'blc':numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                  'blcf': '17:32:18.690, +57.37.28.536, I, 1.42038e+09Hz',
                  'max':numpy.array([ 15.31498909]),
                  'maxpos':numpy.array([58, 21,  0, 20], dtype=numpy.int32),
                  'maxposf': '17:10:23.737, +58.42.25.413, I, 1.42087e+09Hz',
                  'mean':numpy.array([ 0.72415226]),
                  'min':numpy.array([-0.16245638]),
                  'minpos':numpy.array([68, 69,  0, 36], dtype=numpy.int32),
                  'minposf': '17:05:39.206, +61.05.09.055, I, 1.42126e+09Hz',
                  'npts':numpy.array([ 225000.]),
                  'rms':numpy.array([ 1.44985926]),
                  'sigma':numpy.array([ 1.25606618]),
                  'sum':numpy.array([ 162934.25891985]),
                  'sumsq':numpy.array([ 472970.63791706]),
                  'trc':numpy.array([74, 74,  0, 39], dtype=numpy.int32),
                  'trcf': '17:03:03.151, +61.19.10.757, I, 1.42133e+09Hz'}
        self._checkstats(self.outfile,refstats)

    def test109(self):
        """Test 109: Empty phasecenter (auto-calculation)"""
        nchan=40
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,dochannelmap=True,nchan=nchan,start=400,step=10)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,nchan)
        refstats={'blc':numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                  'blcf': '17:31:48.804, +57.36.05.613, I, 1.42038e+09Hz',
                  'max':numpy.array([ 15.64525127]),
                  'maxpos':numpy.array([57, 20,  0, 20], dtype=numpy.int32),
                  'maxposf': '17:10:18.441, +58.38.07.786, I, 1.42087e+09Hz',
                  'mean':numpy.array([ 0.66039691]),
                  'min':numpy.array([-0.42533547]),
                  'minpos':numpy.array([68, 63,  0, 38], dtype=numpy.int32),
                  'minposf': '17:05:17.614, +60.45.47.043, I, 1.42131e+09Hz',
                  'npts':numpy.array([ 225000.]),
                  'rms':numpy.array([ 1.38528216]),
                  'sigma':numpy.array([ 1.21773941]),
                  'sum':numpy.array([ 148589.30382503]),
                  'sumsq':numpy.array([ 431776.51775705]),
                  'trc':numpy.array([74, 74,  0, 39], dtype=numpy.int32),
                  'trcf': '17:02:34.472, +61.17.47.871, I, 1.42133e+09Hz'}
        self._checkstats(self.outfile,refstats)
        


###
# Test frequency imaging
###
class sdimaging_test2(sdimaging_unittest_base,unittest.TestCase):
    """
    Test frequency imaging

       - integrated image
       - selected frequency image
       
    """
    # Input and output names
    prefix=sdimaging_unittest_base.taskname+'Test2'
    outfile=prefix+sdimaging_unittest_base.postfix
    mode='GHz'

    def setUp(self):
        if os.path.exists(self.rawfile):
            shutil.rmtree(self.rawfile)
        shutil.copytree(self.datapath+self.rawfile, self.rawfile)

        default(sdimaging)

    def tearDown(self):
        if (os.path.exists(self.rawfile)):
            shutil.rmtree(self.rawfile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test200(self):
        """Test 200: Integrated image (dochannelmap=False)"""
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction=self.gridfunction,dochannelmap=False)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,1)
        refstats=self.statsinteg
        self._checkstats(self.outfile,refstats)
        
    def test201(self):
        """Test 201: Selected frequency image"""
        nchan=100
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction=self.gridfunction,dochannelmap=True,nchan=nchan,start=1.4202,step=1.0e-5)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,nchan)
        refstats={'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                  'blcf': '17:32:18.690, +57.37.28.536, I, 1.4202e+09Hz',
                  'max': numpy.array([ 21.55560875]),
                  'maxpos': numpy.array([59, 21,  0, 67], dtype=numpy.int32),
                  'maxposf': '17:10:00.642, +58.42.19.808, I, 1.42087e+09Hz',
                  'mean': numpy.array([ 0.80467233]),
                  'min': numpy.array([-0.27736959]),
                  'minpos': numpy.array([58, 71,  0, 10], dtype=numpy.int32),
                  'minposf': '17:09:45.684, +61.12.21.875, I, 1.4203e+09Hz',
                  'npts': numpy.array([ 562500.]),
                  'rms': numpy.array([ 1.56429076]),
                  'sigma': numpy.array([ 1.3414586]),
                  'sum': numpy.array([ 452628.18628213]),
                  'sumsq': numpy.array([ 1376440.6075593]),
                  'trc': numpy.array([74, 74,  0, 99], dtype=numpy.int32),
                  'trcf': '17:03:03.151, +61.19.10.757, I, 1.42119e+09Hz'}
        self._checkstats(self.outfile,refstats)
        
    def test202(self):
        """Test 202: Selected frequency image with other frequency unit"""
        nchan=100
        res=sdimaging(infile=self.rawfile,specunit='MHz',outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction=self.gridfunction,dochannelmap=True,nchan=nchan,start=1420.2,step=0.01)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,nchan)
        refstats={'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                  'blcf': '17:32:18.690, +57.37.28.536, I, 1.4202e+09Hz',
                  'max': numpy.array([ 21.55560875]),
                  'maxpos': numpy.array([59, 21,  0, 67], dtype=numpy.int32),
                  'maxposf': '17:10:00.642, +58.42.19.808, I, 1.42087e+09Hz',
                  'mean': numpy.array([ 0.80467233]),
                  'min': numpy.array([-0.27736959]),
                  'minpos': numpy.array([58, 71,  0, 10], dtype=numpy.int32),
                  'minposf': '17:09:45.684, +61.12.21.875, I, 1.4203e+09Hz',
                  'npts': numpy.array([ 562500.]),
                  'rms': numpy.array([ 1.56429076]),
                  'sigma': numpy.array([ 1.3414586]),
                  'sum': numpy.array([ 452628.18628213]),
                  'sumsq': numpy.array([ 1376440.6075593]),
                  'trc': numpy.array([74, 74,  0, 99], dtype=numpy.int32),
                  'trcf': '17:03:03.151, +61.19.10.757, I, 1.42119e+09Hz'}
        self._checkstats(self.outfile,refstats)
        
###
# Test velocity imaging
###
class sdimaging_test3(sdimaging_unittest_base,unittest.TestCase):
    """
    Test velocity imaging

       - integrated image
       - selected velocity image
       
    """
    # Input and output names
    prefix=sdimaging_unittest_base.taskname+'Test3'
    outfile=prefix+sdimaging_unittest_base.postfix
    mode='km/s'

    def setUp(self):
        if os.path.exists(self.rawfile):
            shutil.rmtree(self.rawfile)
        shutil.copytree(self.datapath+self.rawfile, self.rawfile)

        default(sdimaging)

    def tearDown(self):
        if (os.path.exists(self.rawfile)):
            shutil.rmtree(self.rawfile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test300(self):
        """Test 300: Integrated image (dochannelmap=False)"""
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction=self.gridfunction,dochannelmap=False)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,1)
        refstats=self.statsinteg
        self._checkstats(self.outfile,refstats)
        
    def test301(self):
        """Test 301: Selected velocity image"""
        nchan=100
        res=sdimaging(infile=self.rawfile,specunit=self.mode,outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction=self.gridfunction,dochannelmap=True,nchan=nchan,start=-200.0,step=2.0)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,nchan)
        refstats={'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                  'blcf': '17:32:18.690, +57.37.28.536, I, 1.421353e+09Hz',
                  'max': numpy.array([ 21.97223091]),
                  'maxpos': numpy.array([ 4,  5,  0, 50], dtype=numpy.int32),
                  'maxposf': '17:30:54.243, +57.53.03.440, I, 1.42088e+09Hz',
                  'mean': numpy.array([ 0.84673187]),
                  'min': numpy.array([-0.27300295]),
                  'minpos': numpy.array([61, 71,  0, 16], dtype=numpy.int32),
                  'minposf': '17:08:30.980, +61.12.02.893, I, 1.421202e+09Hz',
                  'npts': numpy.array([ 562500.]),
                  'rms': numpy.array([ 1.6305207]),
                  'sigma': numpy.array([ 1.3934297]),
                  'sum': numpy.array([ 476286.67594505]),
                  'sumsq': numpy.array([ 1495461.22406453]),
                  'trc': numpy.array([74, 74,  0, 99], dtype=numpy.int32),
                  'trcf': '17:03:03.151, +61.19.10.757, I, 1.420415e+09Hz'}
        self._checkstats(self.outfile,refstats)

    def test302(self):
        """Test 302: Selected velocity image (different rest frequency)"""
        nchan=100
        res=sdimaging(infile=self.rawfile,specunit=self.mode,restfreq='1.420GHz',outfile=self.outfile,cell=self.cell,imsize=self.imsize,phasecenter=self.phasecenter,gridfunction=self.gridfunction,dochannelmap=True,nchan=nchan,start=-100.0,step=2.0)
        self.assertEqual(res,None,
                         msg='Any error occurred during imaging')
        self._checkshape(self.outfile,self.imsize[0],self.imsize[1],1,nchan)
        refstats={'blc': numpy.array([0, 0, 0, 0], dtype=numpy.int32),
                  'blcf': '17:32:18.690, +57.37.28.536, I, 1.420474e+09Hz',
                  'max': numpy.array([ 1.61916351]),
                  'maxpos': numpy.array([ 4, 52,  0, 33], dtype=numpy.int32),
                  'maxposf': '17:31:47.043, +60.13.54.473, I, 1.420161e+09Hz',
                  'mean': numpy.array([ 0.12395606]),
                  'min': numpy.array([-0.41655564]),
                  'minpos': numpy.array([60, 71,  0, 93], dtype=numpy.int32),
                  'minposf': '17:08:55.879, +61.12.09.501, I, 1.419593e+09Hz',
                  'npts': numpy.array([ 562500.]),
                  'rms': numpy.array([ 0.19268371]),
                  'sigma': numpy.array([ 0.14751931]),
                  'sum': numpy.array([ 69725.28195545]),
                  'sumsq': numpy.array([ 20883.94443161]),
                  'trc': numpy.array([74, 74,  0, 99], dtype=numpy.int32),
                  'trcf': '17:03:03.151, +61.19.10.757, I, 1.419536e+09Hz'}
        self._checkstats(self.outfile,refstats)

def suite():
    return [sdimaging_test0,sdimaging_test1,
            sdimaging_test2,sdimaging_test3]
