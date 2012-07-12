import os
import sys
import shutil
from __main__ import default
from tasks import *
from taskinit import *
from asap_init import * 
import unittest
import sha
import time
import numpy

asap_init()
from sdsave import sdsave
import asap as sd

# Unit test of sdsave task.
# 
# Currently, the test only examine if supported types of data can be
# read, and if supporeted types of data can be written.
# 
# The test on data selection and data averaging will not be done.

###
# Base class for all testing classes
###
class sdsave_unittest_base:
    """
    Base class for testing classes.
    Implements several methods to compare the results.
    """
    taskname='sdsave'
    datapath=os.environ.get('CASAPATH').split()[0] + '/data/regression/unittest/sdsave/'
    basefile='OrionS_rawACSmod_cal2123.asap'
    summaryStr = None
    firstSpec = None
    nrow = None
    ifno = None
    cycleno = None
    scanno = None

    def _checkfile( self, name ):
        isthere=os.path.exists(name)
        self.assertEqual(isthere,True,
                         msg='output file %s was not created because of the task failure'%(name))

    def _setAttributes(self):
        """
        Set summary string from the original data.
        """
        tb.open(self.basefile)
        #s=sd.scantable(self.basefile,False)
        #self.summaryStr=s._summary()
        #self.firstSpec=numpy.array(s._getspectrum(0))
        #self.nrow=s.nrow()
        self.firstSpec=tb.getcell('SPECTRA',0)
        self.nrow=tb.nrows()
        self.scanno=tb.getcell('SCANNO',0)
        self.ifno=tb.getcell('IFNO',0)
        self.cycleno=tb.getcell('CYCLENO',0)
        self.npol=tb.getkeyword('nPol')
        #del s
        tb.close()


    def _compare(self,filename):
        """
        Compare results

           - check number of rows
           - check first spectrum
        """
        [nrow,sp0] = self._get(filename)
        #casalog.post('nrow=%s'%nrow)
        #casalog.post('maxdiff=%s'%((abs(self.firstSpec-sp0)).max()))
        if nrow != self.nrow:
            return False
        if any((abs(self.firstSpec-sp0))>1.0e-6):
            return False
        return True

    def _get(self,filename):
        """
        """
        n=None
        st=filename.split('.')
        extension=st[-1]
        #casalog.post('filename='+filename)
        if extension == 'asap' or extension == 'ms' or extension == 'fits':
            self._checkfile(filename)
            s=sd.scantable(filename,False)
            n=s.nrow()
            sp=numpy.array(s._getspectrum(0))
            del s
        else:
            import commands
            wcout=commands.getoutput('ls '+st[0]+'*.txt'+' | wc')
            n=int(wcout.split()[0])*self.npol
            filein=st[0]+'_SCAN%d_CYCLE%d_IF%d.txt'%(self.scanno,self.cycleno,self.ifno)
            self._checkfile(filein)
            f=open(filein)
            sp=[]
            line = f.readline()
            while ( line != '' ):
                if line[0] != '#' and line[0] != 'x':
                    lines = line.split()
                    sp.append(float(lines[1]))
                line = f.readline()
            sp = numpy.array(sp)
            f.close()
        return [n,sp]            


###
# Test on bad parameter settings, data selection, data averaging, ...
###
class sdsave_test0(unittest.TestCase,sdsave_unittest_base):
    """
    Test on data selection, data averaging...
    """
    # Input and output names
    infile='OrionS_rawACSmod_cal2123.asap'
    prefix=sdsave_unittest_base.taskname+'Test0'
    outfile=prefix+'.asap'

    def setUp(self):
        self.res=None
        if (not os.path.exists(self.infile)):
            shutil.copytree(self.datapath+self.infile, self.infile)

        default(sdsave)

    def tearDown(self):
        if (os.path.exists(self.infile)):
            shutil.rmtree(self.infile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test000(self):
        """Test 000: Default parameters"""
        self.res=sdsave()
        self.assertFalse(self.res)
        
    def test001(self):
        """Test 001: Time averaging without weight"""
        self.res=sdsave(infile=self.infile,timeaverage=True,outfile=self.outfile)
        self.assertFalse(self.res)        

    def test002(self):
        """Test 002: Polarization averaging without weight"""
        self.res=sdsave(infile=self.infile,polaverage=True,outfile=self.outfile)
        self.assertFalse(self.res)        


###
# Test to read scantable and write various types of format
###
class sdsave_test1(unittest.TestCase,sdsave_unittest_base):
    """
    Read scantable data, write various types of format.
    """
    # Input and output names
    infile='OrionS_rawACSmod_cal2123.asap'
    prefix=sdsave_unittest_base.taskname+'Test1'
    outfile0=prefix+'.asap'
    outfile1=prefix+'.ms'
    outfile2=prefix+'.fits'
    outfile3=prefix

    def setUp(self):
        self.res=None
        if (not os.path.exists(self.infile)):
            shutil.copytree(self.datapath+self.infile, self.infile)
        if (not os.path.exists(self.basefile)):
            shutil.copytree(self.datapath+self.basefile, self.basefile)

        default(sdsave)
        self._setAttributes()

    def tearDown(self):
        if (os.path.exists(self.infile)):
            shutil.rmtree(self.infile)
        if (os.path.exists(self.basefile)):
            shutil.rmtree(self.basefile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test100(self):
        """Test 100: test to read scantable and to write as scantable"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile0,outform='ASAP')
        self.assertEqual(self.res,None)
        self.assertTrue(self._compare(self.outfile0))

    def test101(self):
        """Test 101: test to read scantable and to write as MS"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile1,outform='MS2')
        self.assertEqual(self.res,None)
        self.assertTrue(self._compare(self.outfile1))
        
    def test102(self):
        """Test 102: test to read scantable and to write as SDFITS"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile2,outform='SDFITS')
        self.assertEqual(self.res,None)
        self.assertTrue(self._compare(self.outfile2))

    def test103(self):
        """Test 103: test to read scantable and to write as ASCII"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile3,outform='ASCII')
        self.assertEqual(self.res,None)
        self.assertTrue(self._compare(self.outfile3))
        

###
# Test to read MS and write various types of format
###
class sdsave_test2(unittest.TestCase,sdsave_unittest_base):
    """
    Read MS data, write various types of format.
    """
    # Input and output names
    infile='OrionS_rawACSmod_cal2123.ms'
    prefix=sdsave_unittest_base.taskname+'Test2'
    outfile0=prefix+'.asap'
    outfile1=prefix+'.ms'
    outfile2=prefix+'.fits'
    outfile3=prefix

    def setUp(self):
        self.res=None
        if (not os.path.exists(self.infile)):
            shutil.copytree(self.datapath+self.infile, self.infile)
        if (not os.path.exists(self.basefile)):
            shutil.copytree(self.datapath+self.basefile, self.basefile)

        default(sdsave)
        self._setAttributes()
        self.scanno=0

    def tearDown(self):
        if (os.path.exists(self.infile)):
            shutil.rmtree(self.infile)
        if (os.path.exists(self.basefile)):
            shutil.rmtree(self.basefile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test200(self):
        """Test 200: test to read MS and to write as scantable"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile0,outform='ASAP')
        self.assertEqual(self.res,None)
        self.assertTrue(self._compare(self.outfile0))
        
    def test201(self):
        """Test 201: test to read MS and to write as MS"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile1,outform='MS2')
        self.assertEqual(self.res,None)
        self.assertTrue(self._compare(self.outfile1))
        
    def test202(self):
        """Test 202: test to read MS and to write as SDFITS"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile2,outform='SDFITS')
        self.assertEqual(self.res,None)
        self.assertTrue(self._compare(self.outfile2))

    def test203(self):
        """Test 203: test to read MS and to write as ASCII"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile3,outform='ASCII')
        self.assertEqual(self.res,None)
        self.assertTrue(self._compare(self.outfile3))

    def test204(self):
        """Test 204: test failure case that unexisting antenna is specified"""
        self.res=sdsave(infile=self.infile,antenna='ROSWELL',outfile=self.outfile0,outform='ASAP')
        self.assertFalse(self.res,False)

    def test205(self):
        """Test 205: test to read USB spectral window"""
        self.__spwtest()
        
    def test206(self):
        """Test 206: test to read LSB spectral window"""
        tb.open('%s/SPECTRAL_WINDOW'%(self.infile),nomodify=False)
        chanw = tb.getcol('CHAN_WIDTH')
        chanf = tb.getcol('CHAN_FREQ')
        chanw *= -1.0
        chanf = numpy.flipud(chanf)
        tb.putcol('CHAN_WIDTH',chanw)
        tb.putcol('CHAN_FREQ',chanf)
        netsb = numpy.ones( tb.nrows(), int )
        tb.putcol('NET_SIDEBAND', netsb )
        tb.close()
        self.__spwtest()

    def __spwtest(self):
        self.res=sdsave(infile=self.infile,outfile=self.outfile0,outform='ASAP')
        self.assertFalse(self.res,False)
        self.__compareIncrement( self.outfile0, self.infile )
        self.res=sdsave(infile=self.outfile0,outfile=self.outfile1,outform='MS2')
        self.assertFalse(self.res,False)
        self.__compareIncrement( self.outfile0, self.outfile1 )        

    def __compareIncrement(self,stdata,msdata):
        tb.open('%s/FREQUENCIES'%(stdata))
        incr=tb.getcol('INCREMENT')
        tb.close()
        tb.open('%s/SPECTRAL_WINDOW'%(msdata))
        chanw=tb.getcol('CHAN_WIDTH')
        tb.close()
        for i in xrange(len(incr)):
            #print 'incr[%s]=%s,chanw[0][%s]=%s(diff=%s)'%(i,incr[i],i,chanw[0][i],(incr[i]-chanw[0][i]))
            self.assertEqual(incr[i],chanw[0][i])
        
###
# Test to read ATNF SDFITS and write various types of format
###
class sdsave_test3(unittest.TestCase,sdsave_unittest_base):
    """
    Read ATNF SDFITS data, write various types of format.
    """
    # Input and output names
    infile='OrionS_rawACSmod_cal2123.fits'
    prefix=sdsave_unittest_base.taskname+'Test3'
    outfile0=prefix+'.asap'
    outfile1=prefix+'.ms'
    outfile2=prefix+'.fits'
    outfile3=prefix

    def setUp(self):
        self.res=None
        if (not os.path.exists(self.infile)):
            shutil.copy(self.datapath+self.infile, self.infile)
        if (not os.path.exists(self.basefile)):
            shutil.copytree(self.datapath+self.basefile, self.basefile)

        default(sdsave)
        self._setAttributes()
        self.scanno=0

    def tearDown(self):
        if (os.path.exists(self.infile)):
            os.system( 'rm -f '+self.infile )
        if (os.path.exists(self.basefile)):
            shutil.rmtree(self.basefile)
        os.system( 'rm -rf '+self.prefix+'*' )

    def test300(self):
        """Test 300: test to read ATNF SDFITS and to write as scantable"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile0,outform='ASAP')
        self.assertEqual(self.res,None)
        self.assertTrue(self._compare(self.outfile0))

    def test301(self):
        """Test 301: test to read ATNF SDFITS and to write as MS"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile1,outform='MS2')
        self.assertEqual(self.res,None)
        self.assertTrue(self._compare(self.outfile1))
        
    def test302(self):
        """Test 302: test to read ATNF SDFITS and to write as SDFITS"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile2,outform='SDFITS')
        self.assertEqual(self.res,None)
        self.assertTrue(self._compare(self.outfile2))

    def test303(self):
        """Test 303: test to read ATNF SDFITS and to write as ASCII"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile3,outform='ASCII')
        self.assertEqual(self.res,None)
        self.assertTrue(self._compare(self.outfile3))
        

###
# Test to read GBT SDFITS and write various types of format
###
class sdsave_test4(unittest.TestCase,sdsave_unittest_base):
    """
    Read GBT SDFITS data, write various types of format.
    """
    # Input and output names
    infile='AGBT06A_sliced.fits'
    prefix=sdsave_unittest_base.taskname+'Test4'
    outfile0=prefix+'.asap'
    outfile1=prefix+'.ms'
    outfile2=prefix+'.fits'
    outfile3=prefix

    def setUp(self):
        self.res=None
        if (not os.path.exists(self.infile)):
            shutil.copy(self.datapath+self.infile, self.infile)

        default(sdsave)
        #self._setAttributes()

    def tearDown(self):
        if (os.path.exists(self.infile)):
            os.system( 'rm -f '+self.infile )
        os.system( 'rm -rf '+self.prefix+'*' )

    def test400(self):
        """Test 400: test to read GBT SDFITS and to write as scantable"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile0,outform='ASAP')
        self.assertEqual(self.res,None)
        #self.assertTrue(self._compare(self.outfile0))
        self.assertTrue(self._compare())

    def test401(self):
        """Test 401: test to read GBT SDFITS and to write as MS"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile1,outform='MS2')
        self.assertEqual(self.res,None)
        #self.assertTrue(self._compare(self.outfile1))
        
    def test402(self):
        """Test 402: test to read GBT SDFITS and to write as SDFITS"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile2,outform='SDFITS')
        self.assertEqual(self.res,None)
        #self.assertTrue(self._compare(self.outfile2))

    def test403(self):
        """Test 403: test to read GBT SDFITS and to write as ASCII"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile3,outform='ASCII')
        self.assertEqual(self.res,None)
        #self.assertTrue(self._compare(self.outfile3))

    def _compare(self,filename=''):
        """
        Check a few things for the data.
        """
        s=sd.scantable(self.infile,False)
        if ( s.nrow() != 48 ):
            return False
        if ( s.nif() != 6 ):
            return False
        if ( s.nchan(0) != 4096 ):
            return False
        if ( s.nchan(2) != 8192 ):
            return False
        if ( s.npol() != 1 ):
            return False
        return True
        
###
# Test to read NROFITS and write various types of format
###
class sdsave_test5(unittest.TestCase,sdsave_unittest_base):
    """
    Read NROFITS data, write various types of format.
    """
    # Input and output names
    infile='B68test.nro'
    prefix=sdsave_unittest_base.taskname+'Test5'
    outfile0=prefix+'.asap'
    outfile1=prefix+'.ms'
    outfile2=prefix+'.fits'
    outfile3=prefix

    def setUp(self):
        self.res=None
        if (not os.path.exists(self.infile)):
            shutil.copy(self.datapath+self.infile, self.infile)

        default(sdsave)
        #self._setAttributes()

    def tearDown(self):
        if (os.path.exists(self.infile)):
            os.system( 'rm -f '+self.infile )
        os.system( 'rm -rf '+self.prefix+'*' )

    def test500(self):
        """Test 500: test to read NROFITS and to write as scantable"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile0,outform='ASAP')
        self.assertEqual(self.res,None)
        #self.assertTrue(self._compare(self.outfile0))
        self.assertTrue(self._compare())

    def test501(self):
        """Test 501: test to read NROFITS and to write as MS"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile1,outform='MS2')
        self.assertEqual(self.res,None)
        #self.assertTrue(self._compare(self.outfile1))
        
    def test502(self):
        """Test 502: test to read NROFITS and to write as SDFITS"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile2,outform='SDFITS')
        self.assertEqual(self.res,None)
        #self.assertTrue(self._compare(self.outfile2))

    def test503(self):
        """Test 503: test to read NROFITS and to write as ASCII"""
        self.res=sdsave(infile=self.infile,outfile=self.outfile3,outform='ASCII')
        self.assertEqual(self.res,None)
        #self.assertTrue(self._compare(self.outfile3))
        
    def _compare(self,filename=''):
        """
        Check a few things for the data.
        """
        s=sd.scantable(self.infile,False)
        if ( s.nrow() != 36 ):
            return False
        if ( s.nif() != 4 ):
            return False
        if ( s.nchan() != 2048 ):
            return False
        if ( s.npol() != 1 ):
            return False
        return True        


###
# Test getpt parameter
###
class sdsave_test6( unittest.TestCase, sdsave_unittest_base ):
    """
    Test getpt parameter

    1) import MS to Scantable format with getpt=True 
       1-1) check POINTING table keyword is missing
       1-2) export Scantable to MS format
       1-3) compare POINTING table
    2) import MS to Scantable format with getpt=False
       1-1) check POINTING table keyword exists
       1-2) export Scantable to MS format
       1-3) compare POINTING table

    """
    # Input and output names
    infile='OrionS_rawACSmod_cal2123.ms'
    prefix=sdsave_unittest_base.taskname+'Test6'
    outfile0=prefix+'.asap'
    outfile1=prefix+'.ms'

    def setUp(self):
        self.res=None
        if (not os.path.exists(self.infile)):
            shutil.copytree(self.datapath+self.infile, self.infile)

        default(sdsave)
        #self._setAttributes()

    def tearDown(self):
        if (os.path.exists(self.infile)):
            os.system( 'rm -rf '+self.infile )
        os.system( 'rm -rf '+self.prefix+'*' )

    def test600(self):
        """Test 600: test getpt=True"""
        self.res=sdsave(infile=self.infile,getpt=True,outfile=self.outfile0,outform='ASAP')
        self.assertEqual(self.res,None)
        self.assertFalse(self._pointingKeywordExists())
        self.res=sdsave(infile=self.outfile0,outfile=self.outfile1,outform='MS2')
        self.assertTrue(self._compare())

    def test601(self):
        """Test 601: test getpt=False"""
        self.res=sdsave(infile=self.infile,getpt=False,outfile=self.outfile0,outform='ASAP')
        self.assertEqual(self.res,None)
        self.assertTrue(self._pointingKeywordExists())
        self.res=sdsave(infile=self.outfile0,outfile=self.outfile1,outform='MS2')
        self.assertTrue(self._compare())

    def _pointingKeywordExists(self):
        _tb=tbtool()
        _tb.open(self.outfile0)
        keys=_tb.getkeywords()
        _tb.close()
        del _tb
        return 'POINTING' in keys

    def _compare(self):
        ret = True
        _tb1=tbtool()
        _tb2=tbtool()
        _tb1.open(self.infile)
        #ptab1=_tb1.getkeyword('POINTING').split()[-1]
        ptab1=_tb1.getkeyword('POINTING').lstrip('Table: ')
        _tb1.close()
        _tb1.open(ptab1)
        _tb2.open(self.outfile1)
        #ptab2=_tb2.getkeyword('POINTING').split()[-1]
        ptab2=_tb2.getkeyword('POINTING').lstrip('Table: ')
        _tb2.close()
        _tb2.open(ptab1)
        badcols = []
        for col in _tb1.colnames():
            if not all(_tb1.getcol(col).flatten()==_tb2.getcol(col).flatten()):
                badcols.append( col )
        _tb1.close()
        _tb2.close()
        del _tb1, _tb2
        if len(badcols) != 0:
            print 'Bad column: %s'%(badcols)
            ret = False
        return ret
    
class sdsave_storageTest( sdsave_unittest_base, unittest.TestCase ):
    """
    Unit tests for task sdsave. Test scantable sotrage and insitu
    parameters

    The list of tests:
    testMT  --- storage = 'memory', insitu = True
    testMF  --- storage = 'memory', insitu = False
    testDT  --- storage = 'disk', insitu = True
    testDF  --- storage = 'disk', insitu = False

    Note on handlings of disk storage:
       Task script restores MOLECULE_ID column.

    Tested items:
       1. Number of rows in tables and list of IDs of output scantable.
       2. Units and coordinates of output scantable.
       3. units and coordinates of input scantables before/after run.
    """
    # Input and output names
    infile = 'OrionS_rawACSmod_cal2123.asap'
    outname = sdsave_unittest_base.taskname+'_test'
    pollist = [1]
    iflist = [2]
    restfreq = [44.075e9]
    # Reference data of output scantable
    refout = {"nRow": 8, "SCANNOS": [21,23], "POLNOS": pollist,\
              "IFNOS": iflist, "MOLNOS": [1], "RestFreq": restfreq}

    def setUp( self ):
        # copy input scantables
        if os.path.exists(self.infile):
            shutil.rmtree(self.infile)
        shutil.copytree(self.datapath+self.infile, self.infile)
        # back up the original settings
        self.storage = sd.rcParams['scantable.storage']
        self.insitu = sd.rcParams['insitu']

        default(sdsave)

    def tearDown( self ):
        # restore settings
        sd.rcParams['scantable.storage'] = self.storage
        sd.rcParams['insitu'] = self.insitu
        if (os.path.exists(self.infile)):
            shutil.rmtree(self.infile)


    # Helper functions for testing
    def _get_scantable_params( self, scanname ):
        self._checkfile(scanname)
        res = {}
        testvals = ["scannos", "polnos", "ifnos", "molnos"]
        scan = sd.scantable(scanname,average=False)
        res['nRow'] = scan.nrow()
        for val in testvals:
            res[val.upper()] =  getattr(scan,"get"+val)()
        # rest frequencies
        rflist = []
        for molno in res["MOLNOS"]:
            rflist.append(scan.get_restfreqs(molno)[0])
        res["RestFreq"] = rflist
        del scan
        return res

    def _compare_scantable_params( self, test , refval):
        if type(test) == str:
            testval = self._get_scantable_params(test)
        elif type(test) == dict:
            testval = test
        else:
            msg = "Invalid test value (should be either dict or file name)."
            raise Exception, msg
        #print "Test data = ", testval
        #print "Ref data =  ", refval
        if not type(refval) == dict:
            raise Exception, "The reference data should be a dictionary"
        for key, rval in refval.iteritems():
            if not testval.has_key(key):
                raise KeyError, "Test data does not have key, '%s'" % key
            if type(rval) in [list, tuple, numpy.ndarray]:
                self.assertEqual(len(testval[key]), len(rval), \
                                 msg = "Number of elements in '%s' differs." % key)
                for i in range(len(rval)):
                    rv = rval[i]
                    if type(rv) == float:
                        self.assertAlmostEqual(testval[key][i], rv, \
                                               msg = "%s[%d] differs: %s (expected: %s) "\
                                               % (key, i, str(testval[key][i]), str(rv)))
                    else:
                        self.assertEqual(testval[key][i], rv, \
                                         msg = "%s[%d] differs: %s (expected: %s) "\
                                         % (key, i, str(testval[key][i]), str(rv)))
            else:
                if type(rval) == float:
                    self.assertAlmostEqual(testval[key], rval, \
                                     msg = "%s differs: %s (expected: %s)" \
                                     % (key, str(testval[key]), rval))
                else:
                    self.assertEqual(testval[key], rval, \
                                     msg = "%s differs: %s (expected: %s)" \
                                     % (key, str(testval[key]), rval))
    

    # Actual tests
    def testMT( self ):
        """Storage Test MT: sdsave on storage='memory' and insitu=T"""
        tid = "MT"
        infile = self.infile
        outfile = self.outname+tid
        iflist = self.iflist
        pollist = self.pollist
        restfreq = self.restfreq

        # Backup units and coords of input scantable before run.
        initval = self._get_scantable_params(infile)

        sd.rcParams['scantable.storage'] = 'memory'
        sd.rcParams['insitu'] = True
        print "Running test with storage='%s' and insitu=%s" % \
              (sd.rcParams['scantable.storage'], str(sd.rcParams['insitu']))
        result = sdsave(infile=infile,outfile=outfile,\
                        scanaverage=False,timeaverage=False,polaverage=False,\
                        iflist=iflist,pollist=pollist,restfreq=restfreq)

        self.assertEqual(result,None)
        self.assertTrue(os.path.exists(outfile),msg="No output written")
        print "Testing output scantable"
        self._compare_scantable_params(outfile,self.refout)

        print "Comparing input scantable before/after run"
        self._compare_scantable_params(infile,initval)


    def testMF( self ):
        """Storage Test MF: sdsave on storage='memory' and insitu=F"""
        tid = "MF"
        infile = self.infile
        outfile = self.outname+tid
        iflist = self.iflist
        pollist = self.pollist
        restfreq = self.restfreq

        # Backup units and coords of input scantable before run.
        initval = self._get_scantable_params(infile)

        sd.rcParams['scantable.storage'] = 'memory'
        sd.rcParams['insitu'] = False
        print "Running test with storage='%s' and insitu=%s" % \
              (sd.rcParams['scantable.storage'], str(sd.rcParams['insitu']))
        result = sdsave(infile=infile,outfile=outfile,\
                        scanaverage=False,timeaverage=False,polaverage=False,\
                        iflist=iflist,pollist=pollist,restfreq=restfreq)

        self.assertEqual(result,None)
        self.assertTrue(os.path.exists(outfile),msg="No output written")
        print "Testing output scantable"
        self._compare_scantable_params(outfile,self.refout)

        print "Comparing input scantable before/after run"
        self._compare_scantable_params(infile,initval)


    def testDT( self ):
        """Storage Test DT: sdsave on storage='disk' and insitu=T"""
        tid = "DT"
        infile = self.infile
        outfile = self.outname+tid
        iflist = self.iflist
        pollist = self.pollist
        restfreq = self.restfreq

        # Backup units and coords of input scantable before run.
        initval = self._get_scantable_params(infile)

        sd.rcParams['scantable.storage'] = 'disk'
        sd.rcParams['insitu'] = True
        print "Running test with storage='%s' and insitu=%s" % \
              (sd.rcParams['scantable.storage'], str(sd.rcParams['insitu']))
        result = sdsave(infile=infile,outfile=outfile,\
                        scanaverage=False,timeaverage=False,polaverage=False,\
                        iflist=iflist,pollist=pollist,restfreq=restfreq)

        self.assertEqual(result,None)
        self.assertTrue(os.path.exists(outfile),msg="No output written")
        print "Testing output scantable"
        self._compare_scantable_params(outfile,self.refout)

        print "Comparing input scantable before/after run"
        self._compare_scantable_params(infile,initval)


    def testDF( self ):
        """Storage Test DF: sdsave on storage='disk' and insitu=F"""
        tid = "DF"
        infile = self.infile
        outfile = self.outname+tid
        iflist = self.iflist
        pollist = self.pollist
        restfreq = self.restfreq

        # Backup units and coords of input scantable before run.
        initval = self._get_scantable_params(infile)

        sd.rcParams['scantable.storage'] = 'disk'
        sd.rcParams['insitu'] = False
        print "Running test with storage='%s' and insitu=%s" % \
              (sd.rcParams['scantable.storage'], str(sd.rcParams['insitu']))
        result = sdsave(infile=infile,outfile=outfile,\
                        scanaverage=False,timeaverage=False,polaverage=False,\
                        iflist=iflist,pollist=pollist,restfreq=restfreq)

        self.assertEqual(result,None)
        self.assertTrue(os.path.exists(outfile),msg="No output written")
        print "Testing output scantable"
        self._compare_scantable_params(outfile,self.refout)

        print "Comparing input scantable before/after run"
        self._compare_scantable_params(infile,initval)



def suite():
    return [sdsave_test0,sdsave_test1,sdsave_test2,
            sdsave_test3,sdsave_test4,sdsave_test5,
            sdsave_test6,sdsave_storageTest]
