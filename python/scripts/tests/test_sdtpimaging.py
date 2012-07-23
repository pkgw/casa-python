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

from sdtpimaging_cli import sdtpimaging_cli as sdtpimaging
import asap as sd

# Unit test of sdtpimaging task.

###
# Base class for sdtpimaging unit test
###
class sdtpimaging_unittest_base:
    """
    Base class for sdtpimaging unit test.
    """
    taskname='sdtpimaging'
    datapath=os.environ.get('CASAPATH').split()[0] + '/data/regression/unittest/sdtpimaging/'
    allowance=0.01
    
    def _compare(self, refdata, outdata):
        self._checkfile(outdata)
        refstat = imstat( imagename=refdata )
        outstat = imstat( imagename=outdata )
        keys = ['max', 'min', 'mean', 'maxpos', 'minpos', 'rms' ]
        for key in keys:
            ref = refstat[key]
            out = outstat[key]
            print 'stat %s: ref %s, out %s'%(key,ref,out)
            for i in xrange( len(ref) ):
                if ref[i] != 0.0:
                    diff = (out[i]-ref[i])/ref[i]
                    self.assertTrue( all( abs(diff.flatten()) < self.allowance ),
                                     msg='statistics %s differ: reference %s, output %s'%(key,ref,out) )
                else:
                    self.assertTrue( out[i] == 0.0,
                                     msg='statistics %s differ: reference %s, output %s'%(key,ref,out) )

    def _checkfile( self, name ):
        isthere=os.path.exists(name)
        self.assertEqual(isthere,True,
                         msg='output file %s was not created because of the task failure'%(name))


###
# Test on bad parameter settings, data selection, ...
###
class sdtpimaging_test0(unittest.TestCase,sdtpimaging_unittest_base):
    """
    Test on bad parameter settings
    """
    # Input and output names
    infile='tpimaging.ms'
    prefix=sdtpimaging_unittest_base.taskname+'Test0'
    outfile=prefix+'.ms'
    outimage=prefix+'.im'

    def setUp(self):
        self.res=None
        if (not os.path.exists(self.infile)):
            shutil.copytree(self.datapath+self.infile, self.infile)

        default(sdtpimaging)

    def tearDown(self):
        if (os.path.exists(self.infile)):
            shutil.rmtree(self.infile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test000(self):
        """Test 000: Default parameters"""
        self.res=sdtpimaging()
        self.assertFalse(self.res)
        
    def test001(self):
        """Test 001: Bad antenna id"""
        self.res=sdtpimaging(infile=self.infile,antenna='99')
        self.assertFalse(self.res)        

    def test002(self):
        """Test 002: Bad stokes string"""
        self.res=sdtpimaging(infile=self.infile,stokes='J')
        self.assertFalse(self.res)
        
    def test003(self):
        """Test 003: Try to create image without output image name"""
        self.res=sdtpimaging(infile=self.infile,createimage=True,outfile='')
        self.assertFalse(self.res)

    def test004(self):
        """Test 004: Negative imsize"""
        self.res=sdtpimaging(infile=self.infile,createimage=True,outfile=self.outimage,imsize=[-1])
        self.assertFalse(self.res)

    def test005(self):
        """Test 005: Negative cell size"""
        self.res=sdtpimaging(infile=self.infile,createimage=True,outfile=self.outimage,cell=[-1])
        self.assertFalse(self.res)

    def test006(self):
        """Test 006: Bad phase center string"""
        self.res=sdtpimaging(infile=self.infile,createimage=True,outfile=self.outimage,phasecenter='XXX')
        self.assertFalse(self.res)

    def test007(self):
        """Test 007: Bad pointing column name"""
        self.res=sdtpimaging(infile=self.infile,createimage=True,outfile=self.outimage,pointingcolumn='XXX')
        self.assertFalse(self.res)

    def test008(self):
        """Test 008: Unexisting grid function"""
        self.res=sdtpimaging(infile=self.infile,createimage=True,outfile=self.outimage,gridfunction='XXX')
        self.assertFalse(self.res)
 
    def test009(self):
        """Test 009: Invalid calmode"""
        self.res=sdtpimaging(infile=self.infile,calmode='ps')
        self.assertFalse(self.res)
 

###
# Test to image data without spatial baseline subtraction
###
class sdtpimaging_test1(unittest.TestCase,sdtpimaging_unittest_base):
    """
    Test to image data without spatial baseline subtraction
    """
    # Input and output names
    infile='tpimaging.ms'
    prefix=sdtpimaging_unittest_base.taskname+'Test1'
    outfile=prefix+'.ms'
    outimage=prefix+'.im'
    refimage='nobaseline.im'

    def setUp(self):
        self.res=None
        if (not os.path.exists(self.infile)):
            shutil.copytree(self.datapath+self.infile, self.infile)
        if (not os.path.exists(self.refimage)):
            shutil.copytree(self.datapath+self.refimage, self.refimage)

        default(sdtpimaging)

    def tearDown(self):
        if (os.path.exists(self.infile)):
            shutil.rmtree(self.infile)
        if (os.path.exists(self.refimage)):
            shutil.rmtree(self.refimage)
        os.system( 'rm -rf '+self.prefix+'*' )
        os.system( 'rm -rf '+self.infile+'*' )

    def test100(self):
        """Test 100: test to image data without spatial baseline subtraction"""
        self.res=sdtpimaging(infile=self.infile,calmode='none',stokes='XX',spw=2,createimage=True,outfile=self.outimage,imsize=[64],cell=['15arcsec'],phasecenter='J2000 05h35m07s -5d21m00s',pointingcolumn='direction',gridfunction='SF')
        self.assertEqual(self.res,None)
        self._compare(self.refimage,self.outimage)
                
        
###
# Test to image data with spatial baseline subtraction
###
class sdtpimaging_test2(unittest.TestCase,sdtpimaging_unittest_base):
    """
    Test to image data with spatial baseline subtraction
    """
    # Input and output names
    infile='tpimaging.ms'
    prefix=sdtpimaging_unittest_base.taskname+'Test2'
    outfile=prefix+'.ms'
    outimage=prefix+'.im'
    refimage='dobaseline.im'

    def setUp(self):
        self.res=None
        if (not os.path.exists(self.infile)):
            shutil.copytree(self.datapath+self.infile, self.infile)
        if (not os.path.exists(self.refimage)):
            shutil.copytree(self.datapath+self.refimage, self.refimage)

        default(sdtpimaging)

    def tearDown(self):
        if (os.path.exists(self.infile)):
            shutil.rmtree(self.infile)
        if (os.path.exists(self.refimage)):
            shutil.rmtree(self.refimage)
        os.system( 'rm -rf '+self.prefix+'*' )
        os.system( 'rm -rf '+self.infile+'*' )

    def test200(self):
        """Test 200: test to image data with spatial baseline subtraction"""
        self.res=sdtpimaging(infile=self.infile,calmode='baseline',masklist=[10,10],blpoly=1,stokes='XX',spw=2,createimage=True,outfile=self.outimage,imsize=[64],cell=['15arcsec'],phasecenter='J2000 05h35m07s -5d21m00s',pointingcolumn='direction',gridfunction='SF')
        self.assertEqual(self.res,None)
        self._compare(self.refimage,self.outimage)
        

def suite():
    return [sdtpimaging_test0,sdtpimaging_test1,sdtpimaging_test2]
