import os
import sys
import shutil
from __main__ import default
from tasks import *
from taskinit import *
import unittest
#
#import listing
#from numpy import array

import asap as sd
from sdreduceold import sdreduceold
#from sdstatold import sdstatold

class sdreduceold_test(unittest.TestCase):
    """
    Basic unit tests for task sdreduceold. No interactive testing.

    The list of tests:
    test00    --- default parameters (raises an errror)
    test01    --- Default parameters + valid input filename
    test02    --- operate all 3 steps (mostly with default parameters)
    test03    --- explicitly specify all parameters
    test04-07 --- do one of calibration, average, baseline, or smooth
    test08-10 --- skip one of of calibration and average, baseline, or smooth
    
    Note: input data (infile0) is generated from a single dish regression data,
    'OrionS_rawACSmod', as follows:
      default(sdsave)
      sdsave(infile='OrionS_rawACSmod',outfile=self.infile0,outform='ASAP')
    -> Just converted to scantable to eliminate errors by data conversion.
    """
    # Data path of input/output
    datapath=os.environ.get('CASAPATH').split()[0] + '/data/regression/unittest/sdreduce/'
    # Input and output names
    # uncalibrated data
    infile0 = 'OrionS_rawACSmod.asap'
    # uncalibrated data
    infile1 = 'OrionS_rawACSmod_cal2123.asap'
    infiles = [infile0, infile1]
    outroot = 'sdreduceold_test'

    def setUp(self):
        for file in self.infiles:
            if os.path.exists(file):
                shutil.rmtree(file)
            shutil.copytree(self.datapath+file, file)
        default(sdreduceold)

    def tearDown(self):
        for file in self.infiles:
            if (os.path.exists(file)):
                shutil.rmtree(file)

    def _row0_stats(self,file):
        scan = sd.scantable(file,average=False)
        stats=["max","min","sum","rms","stddev","max_abc","min_abc"]
        edge = 500
        chanrange = [edge, scan.nchan()-edge-1]
        mask = scan.create_mask(chanrange)
        statdict = {}
        for stat in stats:
            statdict[stat] = scan.stats(stat,mask=mask,row=0)[0]
        del scan
        print "\nCurrent run: "+str(statdict)
        return statdict

    def _teststats0(self,teststat,refstat,places=4):
        for stat, refval in refstat.iteritems():
            self.assertTrue(teststat.has_key(stat),
                            msg = "'%s' is not defined in the current run" % stat)
            allowdiff = 0.01
            #print "Comparing '%s': %f (current run), %f (reference)" % \
            #      (stat,testdict[stat],refval)
            reldiff = (teststat[stat]-refval)/refval
            self.assertTrue(reldiff < allowdiff,\
                            msg="'%s' differs: %f (ref) != %f" % \
                            (stat, refval, teststat[stat]))

    def test00(self):
        """Test 0: Default parameters (raises an errror)"""
        #print blfunc
        result = sdreduceold()
        self.assertFalse(result)

    def test01(self):
        """Test 1: Default parameters + valid input filename (do nothing)"""
        self.tid="01"
        infile = self.infile0
        outfile = self.outroot+self.tid+'.asap'

        result = sdreduceold(infile=infile,outfile=outfile)
        self.assertEqual(result,None,
                         msg="The task returned '"+str(result)+"' instead of None")
        self.assertTrue(os.path.exists(outfile),
                         msg="Output file '"+str(outfile)+"' doesn't exists")
        refstat = {'rms': 0.55389463901519775, 'min': 0.26541909575462341,
                   'max_abc': 773.0, 'max': 0.91243284940719604,
                   'sum': 3802.1259765625, 'stddev': 0.16529126465320587,
                   'min_abc': 7356.0}
        teststat = self._row0_stats(outfile)
        self._teststats0(teststat,refstat)

    def test02(self):
        """
        Test 2: operate all steps (mostly with default parameters)
        testing if default parameter values are changed
        """
        # Don't average GBT ps data at the same time of calibration.
        self.tid="02"
        infile = self.infile0
        outfile = self.outroot+self.tid+'.asap'
        calmode = 'ps'
        kernel = 'hanning'
        blfunc='poly'


        result = sdreduceold(infile=infile,outfile=outfile,calmode=calmode,
                       kernel=kernel,blfunc=blfunc)
        self.assertEqual(result,None,
                         msg="The task returned '"+str(result)+"' instead of None")
        self.assertTrue(os.path.exists(outfile),
                         msg="Output file '"+str(outfile)+"' doesn't exists")

        refstat = {'rms': 0.21985267102718353, 'min': -0.70194435119628906,
                   'max_abc': 4093.0, 'max': 0.96840262413024902,
                   'sum': 5.4850387573242188, 'stddev': 0.21986636519432068,
                   'min_abc': 7623.0}
        teststat = self._row0_stats(outfile)
        self._teststats0(teststat,refstat)
        

    def test03(self):
        """
        Test 3:  explicitly specify all parameters
        testing if parameter names are changed
        """
        self.tid="03"
        infile = self.infile0
        outfile = self.outroot+self.tid+'.asap'

        result = sdreduceold(infile=infile,
                       antenna=0,
                       fluxunit='K',
                       telescopeparm='',
                       specunit='GHz',
                       frame='',
                       doppler='',
                       calmode='ps',
                       scanlist=[20,21,22,23],
                       field='OrionS*',
                       iflist=[0],
                       pollist=[],
                       channelrange=[],
                       average=False,
                       scanaverage=False,
                       timeaverage=False,
                       tweight='none',
                       averageall=False,
                       polaverage=False,
                       pweight='none',
                       tau=0.0,
                       kernel='hanning',
                       kwidth=5,
                       blfunc='poly',
                       order=5,
                       npiece=2,
                       clipthresh=3.0,
                       clipniter=1,
                       masklist=[],
                       maskmode='auto',
                       thresh=5.0,
                       avg_limit=4,
                       edge=[0],
                       verifycal=False,
                       verifysm=False,
                       verifybl=False,
                       verbosebl=True,
                       outfile=outfile,
                       outform='ASAP',
                       overwrite=False,
                       plotlevel=0)
        self.assertEqual(result,None,
                         msg="The task returned '"+str(result)+"' instead of None")
        self.assertTrue(os.path.exists(outfile),
                         msg="Output file '"+str(outfile)+"' doesn't exists")

    def test04(self):
        """ Test 4:  operate only calibration step """
        self.tid="04"
        infile = self.infile0
        outfile = self.outroot+self.tid+'.asap'
        calmode = 'ps'

        result = sdreduceold(infile=infile,outfile=outfile,calmode=calmode)
        self.assertEqual(result,None,
                         msg="The task returned '"+str(result)+"' instead of None")
        self.assertTrue(os.path.exists(outfile),
                         msg="Output file '"+str(outfile)+"' doesn't exists")
        refstat = {'rms': 2.1299083232879639, 'min': 1.2246102094650269,
                   'max_abc': 4093.0, 'max': 3.1902554035186768,
                   'sum': 15209.119140625, 'stddev': 0.25390961766242981,
                   'min_abc': 7434.0}
        teststat = self._row0_stats(outfile)
        self._teststats0(teststat,refstat)

    def test05(self):
        """ Test 5:  operate only averaging step """
        self.tid="05"
        infile = self.infile1
        outfile = self.outroot+self.tid+'.asap'
        average = True
        # need to run one of average
        scanaverage = True

        result = sdreduceold(infile=infile,outfile=outfile,
                       average=average,scanaverage=scanaverage)
        self.assertEqual(result,None,
                         msg="The task returned '"+str(result)+"' instead of None")
        self.assertTrue(os.path.exists(outfile),
                         msg="Output file '"+str(outfile)+"' doesn't exists")

        refstat = {'rms': 4.1353230476379395, 'min': 3.2386586666107178,
                   'max_abc': 4093.0, 'max': 5.6874399185180664,
                   'sum': 29690.876953125, 'stddev': 0.24056948721408844,
                   'min_abc': 2452.0}
        teststat = self._row0_stats(outfile)
        self._teststats0(teststat,refstat)

    def test06(self):
        """ Test 6:  operate only smoothing step """
        self.tid="06"
        infile = self.infile1
        outfile = self.outroot+self.tid+'.asap'
        kernel = 'hanning'

        result = sdreduceold(infile=infile,outfile=outfile,kernel=kernel)
        self.assertEqual(result,None,
                         msg="The task returned '"+str(result)+"' instead of None")
        self.assertTrue(os.path.exists(outfile),
                         msg="Output file '"+str(outfile)+"' doesn't exists")

        refstat = {'rms': 3.5979659557342529, 'min': 2.3542881011962891,
                   'max_abc': 4093.0, 'max': 5.2421674728393555,
                   'sum': 25737.166015625, 'stddev': 0.37295544147491455,
                   'min_abc': 6472.0}
        teststat = self._row0_stats(outfile)
        self._teststats0(teststat,refstat)

    def test07(self):
        """ Test 7:  operate only baseline step """
        self.tid="07"
        infile = self.infile1
        outfile = self.outroot+self.tid+'.asap'
        blfunc = 'poly'

        result = sdreduceold(infile=infile,outfile=outfile,blfunc=blfunc)
        self.assertEqual(result,None,
                         msg="The task returned '"+str(result)+"' instead of None")
        self.assertTrue(os.path.exists(outfile),
                         msg="Output file '"+str(outfile)+"' doesn't exists")

        refstat =  {'rms': 0.42929685115814209, 'min': -1.4878685474395752,
                    'max_abc': 4093.0, 'max': 1.8000495433807373,
                    'sum': 6.9646663665771484, 'stddev': 0.42932614684104919,
                    'min_abc': 7434.0}
        teststat = self._row0_stats(outfile)
        self._teststats0(teststat,refstat)

    def test08(self):
        """ Test 8:  skip calibration and averaging """
        self.tid="08"
        infile = self.infile1
        outfile = self.outroot+self.tid+'.asap'
        calmode = 'none'
        average = False
        kernel = 'hanning'
        blfunc = 'poly'

        result = sdreduceold(infile=infile,outfile=outfile,calmode=calmode,
                       average=average,kernel=kernel,blfunc=blfunc)
        self.assertEqual(result,None,
                         msg="The task returned '"+str(result)+"' instead of None")
        self.assertTrue(os.path.exists(outfile),
                         msg="Output file '"+str(outfile)+"' doesn't exists")
        refstat = {'rms': 0.37204021215438843, 'min': -1.1878492832183838,
                   'max_abc': 4093.0, 'max': 1.6387548446655273,
                   'sum': 9.2789239883422852, 'stddev': 0.3720642626285553,
                   'min_abc': 7623.0}
        teststat = self._row0_stats(outfile)
        self._teststats0(teststat,refstat)

    def test09(self):
        """ Test 9:  skip smoothing"""
        self.tid="09"
        infile = self.infile0
        outfile = self.outroot+self.tid+'.asap'
        calmode = 'ps'
        kernel = 'none'
        blfunc = 'poly'

        result = sdreduceold(infile=infile,outfile=outfile,calmode=calmode,
                       kernel=kernel,blfunc=blfunc)
        self.assertEqual(result,None,
                         msg="The task returned '"+str(result)+"' instead of None")
        self.assertTrue(os.path.exists(outfile),
                         msg="Output file '"+str(outfile)+"' doesn't exists")

        refstat = {'rms': 0.25368797779083252, 'min': -0.87923824787139893,
                   'max_abc': 4093.0, 'max': 1.0637180805206299,
                   'sum': 4.11566162109375, 'stddev': 0.25370475649833679,
                   'min_abc': 7434.0}
        teststat = self._row0_stats(outfile)
        self._teststats0(teststat,refstat)

    def test10(self):
        """ Test 10:  skip baseline"""
        self.tid="10"
        infile = self.infile0
        outfile = self.outroot+self.tid+'.asap'
        calmode = 'ps'
        kernel = 'hanning'
        blfunc = 'none'

        result = sdreduceold(infile=infile,outfile=outfile,calmode=calmode,
                       kernel=kernel,blfunc=blfunc)
        self.assertEqual(result,None,
                         msg="The task returned '"+str(result)+"' instead of None")
        self.assertTrue(os.path.exists(outfile),
                         msg="Output file '"+str(outfile)+"' doesn't exists")

        refstat = {'rms': 2.126171350479126, 'min': 1.3912382125854492,
                   'max_abc': 4093.0, 'max': 3.0977959632873535,
                   'sum': 15209.0869140625, 'stddev': 0.2203933447599411,
                   'min_abc': 6472.0}
        teststat = self._row0_stats(outfile)
        self._teststats0(teststat,refstat)

def suite():
    return [sdreduceold_test]