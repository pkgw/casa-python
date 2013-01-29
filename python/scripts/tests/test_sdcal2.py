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

# to rethrow exception 
import inspect
g = sys._getframe(len(inspect.stack())-1).f_globals
g['__rethrow_casa_exceptions'] = True
from sdcal2_cli import sdcal2_cli as sdcal2
#from sdcal import sdcal
import asap as sd

#
# Unit test of sdcal task.
# 

###
# Base class for sdcal unit test
###
class sdcal2_unittest_base:
    """
    Base class for sdcal unit test
    """
    taskname='sdcal2'
    datapath=os.environ.get('CASAPATH').split()[0] + '/data/regression/unittest/sdcal2/'
    tolerance=1.0e-15

    def _checkfile(self, name):
        isthere=os.path.exists(name)
        self.assertEqual(isthere,True,
                         msg='output file %s was not created because of the task failure'%(name))
        

    def _getspectra( self, name ):
        isthere=os.path.exists(name)
        self.assertEqual(isthere,True,
                         msg='file %s does not exist'%(name))        
        tb.open(name)
        sp=tb.getcol('SPECTRA').transpose()
        tb.close()
        return sp

    def _checkshape( self, sp, ref ):
        # check array dimension 
        self.assertEqual( sp.ndim, ref.ndim,
                          msg='array dimension differ' )
        # check number of spectra
        self.assertEqual( sp.shape[0], ref.shape[0],
                          msg='number of spectra differ' )
        # check number of channel
        self.assertEqual( sp.shape[1], ref.shape[1],
                          msg='number of channel differ' )

    def _diff(self, sp, ref):
        diff=abs((sp-ref)/ref)
        idx=numpy.argwhere(numpy.isnan(diff))
        #print idx
        if len(idx) > 0:
            diff[idx]=sp[idx]
        return diff
        

###
# Base class for calibration test
###
class sdcal2_caltest_base(sdcal2_unittest_base):
    """
    Base class for calibration test
    """
    def _comparecal(self, out, ref, col='SPECTRA'):
        self._checkfile(out)
        tout = tbtool()
        tref = tbtool()
        try:
            tout.open(out)
            tref.open(ref)
            self.assertEqual(tout.nrows(), tref.nrows(),
                             msg='number of rows differ.')
            # check meta data
            meta = ['SCANNO','IFNO','POLNO','TIME','ELEVATION']
            for name in meta:
                vout = tout.getcol(name)
                vref = tref.getcol(name)
                self.assertTrue(numpy.all(vout==vref),
                                msg='column %s differ'%(name))

            # check calibration data
            for irow in xrange(tout.nrows()):
                sp = tout.getcell(col, irow)
                spref = tref.getcell(col, irow)
                diff=self._diff(sp,spref)
                self.assertTrue(numpy.all(diff < 0.01),
                                msg='calibrated result is wrong (irow=%s): maxdiff=%s'%(irow,diff.max()) )
        except Exception, e:
            raise e
        finally:
            tout.close()
            tref.close()

    def _compare(self, out, ref, tsys=False):
        self._checkfile(out)
        tout = tbtool()
        tref = tbtool()
        try:
            tout.open(out)
            tref.open(ref)
            self.assertEqual(tout.nrows(), tref.nrows(),
                             msg='number of rows differ.')
            # check SPECTRA
            col = 'SPECTRA'
            for irow in xrange(tout.nrows()):
                sp = tout.getcell(col, irow)
                spref = tref.getcell(col, irow)
                diff=self._diff(sp,spref)
                self.assertTrue(numpy.all(diff < 0.01),
                                msg='calibrated result is wrong (irow=%s): maxdiff=%s'%(irow,diff.max()) )

            # check Tsys if necessary
            if tsys:
                col = 'TSYS'
                for irow in xrange(tout.nrows()):
                    sp = tout.getcell(col, irow)
                    spref = tref.getcell(col, irow)
                    self.assertEqual(len(sp), len(spref),
                                     msg='Tsys is wrong (irow=%s): shape mismatch'%(irow))
                    diff=self._diff(sp,spref)
                    self.assertTrue(numpy.all(diff < 0.01),
                                    msg='Tsys is wrong (irow=%s): maxdiff=%s'%(irow,diff.max()) )
                
        except Exception, e:
            raise e
        finally:
            tout.close()
            tref.close()
        

###
# Test if the task raises exception properly
###
class sdcal2_exceptions(sdcal2_unittest_base,unittest.TestCase):
    """
    Test on bad parameter setting
    """
    # Input and output names
    rawfile='sdcal2Test.ps.asap'
    prefix=sdcal2_unittest_base.taskname+'Test.ps'
    outfile=prefix+'.asap.out'
    skytable=prefix+'.sky'
    tsystable=prefix+'.tsys'
    ifmap={1:[5,6]}

    def setUp(self):
        self.res=None
        if (not os.path.exists(self.rawfile)):
            shutil.copytree(self.datapath+self.rawfile, self.rawfile)
        if (not os.path.exists(self.skytable)):
            shutil.copytree(self.datapath+self.skytable, self.skytable)
        if (not os.path.exists(self.tsystable)):
            shutil.copytree(self.datapath+self.tsystable, self.tsystable)

        default(sdcal2)

    def tearDown(self):
        if (os.path.exists(self.rawfile)):
            shutil.rmtree(self.rawfile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test_exception00(self):
        """test_exception00: Default parameters"""
        # argument verification error
        try:
            self.res=sdcal2()
            #self.assertFalse(self.res)
            self.fail("The task must throw exception.")
        except Exception, e:
            pos=str(e).find("Parameter verification failed")
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))
        
    def test_exception01(self):
        """test_exception01: apply calibration without skytable"""
        try:
            self.res=sdcal2(infile=self.rawfile,calmode='apply')
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('Name of the sky table must be given.')
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test_exception02(self):
        """test_exception02: invalid interp string"""
        interp='invalid_interpolation'
        try:
            self.res=sdcal2(infile=self.rawfile,calmode='apply',skytable=self.skytable,tsystable=self.tsystable,interp=interp,ifmap=self.ifmap)
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('Interpolation type \'%s\' is invalid or not supported yet.'%(interp))
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test_exception03(self):
        """test_exception03: Invalid calibration mode"""
        # argument verification error
        try:
            self.res=sdcal2(infile=self.rawfile,calmode='invalid',outfile=self.outfile)
            #self.assertFalse(self.res)
            self.fail("The task must throw exception.")
        except Exception, e:
            pos=str(e).find("Parameter verification failed")
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test_exception04(self):
        """test_exception04: Existing outfile with overwrite=False"""
        if (not os.path.exists(self.outfile)):
            shutil.copytree(self.rawfile, self.outfile)
        try:
            self.res=sdcal2(infile=self.rawfile,calmode='ps',outfile=self.outfile,overwrite=False)
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('Output file \'%s\' exists.'%(self.outfile))
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))
##         finally:
##             os.system( 'rm -rf %s'%outfile )        

    def test_exception05(self):
        """test_exception05: Empty ifmap"""
        try:
            self.res=sdcal2(infile=self.rawfile,calmode='apply',ifmap={},skytable=self.skytable,tsystable=self.tsystable,outfile=self.outfile)
            #self.assertFalse(self.res)
            self.fail("The task must throw exception.")
        except Exception, e:
            pos=str(e).find("ifmap must be non-empty dictionary.")
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test_exception06(self):
        """test_exception06: Non-existing sky table"""
        dummytable='dummy.sky'
        try:
            self.res=sdcal2(infile=self.rawfile,calmode='apply',ifmap=self.ifmap,skytable=dummytable,tsystable=self.tsystable,outfile=self.outfile)
            #self.assertFalse(self.res)
            self.fail("The task must throw exception.")
        except Exception, e:
            pos=str(e).find("Sky table \'%s\' does not exist."%(dummytable))
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test_exception07(self):
        """test_exception07: Non-existing tsys table"""
        dummytable='dummy.tsys'
        try:
            self.res=sdcal2(infile=self.rawfile,calmode='apply',ifmap=self.ifmap,skytable=self.skytable,tsystable=dummytable,outfile=self.outfile)
            #self.assertFalse(self.res)
            self.fail("The task must throw exception.")
        except Exception, e:
            pos=str(e).find("Tsys table \'%s\' does not exist."%(dummytable))
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test_exception08(self):
        """test_exception08: Invalid interp string format (more than one comma)"""
        interp='linear,linear,linear'
        try:
            self.res=sdcal2(infile=self.rawfile,calmode='apply',skytable=self.skytable,tsystable=self.tsystable,interp=interp,ifmap=self.ifmap)
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('Invalid format of the parameter interp: \'%s\''%(interp))
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test_exception09(self):
        """test_exception09: Update infile without setting overwrite to False"""
        try:
            self.res=sdcal2(infile=self.rawfile,calmode='apply',skytable=self.skytable,tsystable=self.tsystable,ifmap=self.ifmap)
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('You should set overwrite to True if you want to update infile.')
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test_exception10(self):
        """test_exception10: Empty iflist for Tsys calibration"""
        try:
            self.res=sdcal2(infile=self.rawfile,calmode='tsys',iflist=[],outfile=self.outfile)
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('You must specify iflist as a list of IFNOs for Tsys calibration.')
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

    def test_exception11(self):
        """test_exception11: non-scantable input"""
        try:
            self.res=sdcal2(infile=self.skytable,calmode='ps',outfile=self.outfile)
            self.assertTrue(False,
                            msg='The task must throw exception')
        except Exception, e:
            pos=str(e).find('infile must be in scantable format.')
            self.assertNotEqual(pos,-1,
                                msg='Unexpected exception was thrown: %s'%(str(e)))

###
# Test sky calibration (calmode='ps')
###
class sdcal2_skycal_ps(sdcal2_caltest_base,unittest.TestCase):
    """
    Test sky calibration (calmode='ps')
    """
    # Input and output names
    rawfile='sdcal2Test.ps.asap'
    prefix=sdcal2_unittest_base.taskname+'Test.ps'
    outfile=prefix+'.sky.out'
    skytable=prefix+'.sky'
    calmode='ps'

    def setUp(self):
        self.res=None
        if (not os.path.exists(self.rawfile)):
            shutil.copytree(self.datapath+self.rawfile, self.rawfile)
        if (not os.path.exists(self.skytable)):
            shutil.copytree(self.datapath+self.skytable, self.skytable)

        default(sdcal2)

    def tearDown(self):
        if (os.path.exists(self.rawfile)):
            shutil.rmtree(self.rawfile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test_skycal_ps00(self):
        """test_skycal_ps00: Sky calibration for calmode='ps' (ALMA)"""
        sdcal2(infile=self.rawfile,calmode=self.calmode,outfile=self.outfile)

        self._comparecal(self.outfile, self.skytable)
        
    def test_skycal_ps01(self):
        """test_skycal_ps01: Sky calibration for calmode='ps' (ALMA), overwrite existing table"""
        if (not os.path.exists(self.skytable)):
            shutil.copytree(self.rawfile, self.outfile)
        sdcal2(infile=self.rawfile,calmode=self.calmode,outfile=self.outfile,overwrite=True)

        self._comparecal(self.outfile, self.skytable)
        
###
# Test Tsys calibration (calmode='tsys')
###
class sdcal2_tsyscal(sdcal2_caltest_base,unittest.TestCase):
    """
    Test Tsys calibration
    """
    # Input and output names
    rawfile='sdcal2Test.ps.asap'
    prefix=sdcal2_unittest_base.taskname+'Test.ps'
    outfile=prefix+'.tsys.out'
    tsystable=prefix+'.tsys'
    calmode='tsys'
    iflist=[1]
    
    def setUp(self):
        self.res=None
        if (not os.path.exists(self.rawfile)):
            shutil.copytree(self.datapath+self.rawfile, self.rawfile)
        if (not os.path.exists(self.tsystable)):
            shutil.copytree(self.datapath+self.tsystable, self.tsystable)

        default(sdcal2)

    def tearDown(self):
        if (os.path.exists(self.rawfile)):
            shutil.rmtree(self.rawfile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test_tsyscal00(self):
        """test_tsyscal00: Tsys calibration"""
        sdcal2(infile=self.rawfile,calmode=self.calmode,iflist=self.iflist,outfile=self.outfile)

        self._comparecal(self.outfile, self.tsystable, 'TSYS')
        
    def test_tsyscal01(self):
        """test_tsyscal01: Tsys calibration, overwrite existing table"""
        if (not os.path.exists(self.tsystable)):
            shutil.copytree(self.rawfile, self.outfile)
        sdcal2(infile=self.rawfile,calmode=self.calmode,iflist=self.iflist,outfile=self.outfile,overwrite=True)

        self._comparecal(self.outfile, self.tsystable, 'TSYS')

###
# Test apply calibration
###
class sdcal2_applycal(sdcal2_caltest_base,unittest.TestCase):
    """
    Test apply calibration
    """
    # Input and output names
    rawfile='sdcal2Test.ps.asap'
    prefix=sdcal2_unittest_base.taskname+'Test.ps'
    outfile=prefix+'.asap.out'
    skytable=prefix+'.sky'
    tsystable=prefix+'.tsys'
    reftables=[prefix+'.asap.ref',prefix+'.asap.noTsys.ref',prefix+'.asap.cspline.ref']
    calmode='apply'
    iflist=[1]
    ifmap={1:[5,6]}
    
    def setUp(self):
        self.res=None
        if (not os.path.exists(self.rawfile)):
            shutil.copytree(self.datapath+self.rawfile, self.rawfile)
        if (not os.path.exists(self.skytable)):
            shutil.copytree(self.datapath+self.skytable, self.skytable)
        if (not os.path.exists(self.tsystable)):
            shutil.copytree(self.datapath+self.tsystable, self.tsystable)
        for ref in self.reftables:
            if (not os.path.exists(ref)):
                shutil.copytree(self.datapath+ref, ref)
                
        default(sdcal2)

    def tearDown(self):
        if (os.path.exists(self.rawfile)):
            shutil.rmtree(self.rawfile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test_applycal00(self):
        """test_applycal00: apply existing sky table and Tsys table"""
        sdcal2(infile=self.rawfile,calmode=self.calmode,skytable=self.skytable,tsystable=self.tsystable,ifmap=self.ifmap,outfile=self.outfile)

        self._compare(self.outfile, self.reftables[0], True)
        
    def test_applycal01(self):
        """test_applycal01: apply existing skytable"""
        sdcal2(infile=self.rawfile,calmode=self.calmode,skytable=self.skytable,ifmap=self.ifmap,outfile=self.outfile)

        self._compare(self.outfile, self.reftables[1], False)

    def test_applycal02(self):
        """test_applycal02: apply existing sky table and Tsys table with cubic spline interpolation along frequency axis"""
        sdcal2(infile=self.rawfile,calmode=self.calmode,skytable=self.skytable,tsystable=self.tsystable,interp='linear,cspline',ifmap=self.ifmap,outfile=self.outfile)

        self._compare(self.outfile, self.reftables[2], True)

    def test_applycal03(self):
        """test_applycal03: test update mode (overwrite infile)"""
        sdcal2(infile=self.rawfile,calmode=self.calmode,skytable=self.skytable,tsystable=self.tsystable,ifmap=self.ifmap,overwrite=True)

        tb.open(self.rawfile)
        tsel=tb.query('IFNO IN [5,6] && SRCTYPE==0')
        tsel.copy(self.outfile)
        tsel.close()
        tb.close()
        self._compare(self.outfile, self.reftables[0], True)

    def test_applycal04(self):
        """test_applycal04: calibrate sky and apply it on-the-fly"""
        self.calmode='ps,apply'
        sdcal2(infile=self.rawfile,calmode=self.calmode,outfile=self.outfile)

        self._compare(self.outfile, self.reftables[1], False)

    def test_applycal05(self):
        """test_applycal05: calibrate sky and apply it on-the-fly with existing Tsys table"""
        self.calmode='ps,apply'
        sdcal2(infile=self.rawfile,calmode=self.calmode,ifmap=self.ifmap,tsystable=self.tsystable,outfile=self.outfile)

        self._compare(self.outfile, self.reftables[0], 'TSYS')

    def test_applycal06(self):
        """test_applycal06: calibrate sky as well as Tsys and apply them on-the-fly"""
        self.calmode='ps,tsys,apply'
        sdcal2(infile=self.rawfile,calmode=self.calmode,iflist=self.iflist,ifmap=self.ifmap,outfile=self.outfile)

        self._compare(self.outfile, self.reftables[0], 'TSYS')

    def test_applycal07(self):
        """test_applycal07: overwrite existing scantable"""
        if not os.path.exists(self.outfile):
            shutil.copytree(self.rawfile, self.outfile)
        sdcal2(infile=self.rawfile,calmode=self.calmode,skytable=self.skytable,tsystable=self.tsystable,ifmap=self.ifmap,outfile=self.outfile,overwrite=True)

        self._compare(self.outfile, self.reftables[0], 'TSYS')

def suite():
    return [sdcal2_exceptions, sdcal2_skycal_ps,
            sdcal2_tsyscal, sdcal2_applycal]
