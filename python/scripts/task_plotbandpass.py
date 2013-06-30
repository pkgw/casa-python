#########################################################################
#
#  task_plotbandpass.py
#
#  Developed at the NAASC, this is a generic task to display CASA Tsys and 
#  bandpass solution tables with options to overlay them in various
#  combinations, and/or with an atmospheric transmission or sky temperature
#  model.  It works with both the 'new' (casa 3.4) and 'old' calibration
#  table formats, and allows for mixed mode spws (e.g. TDM and FDM for ALMA).
#  It uses the new msmd tool to access the information about an ms.
#
#  Todd R. Hunter  February 2013
#
# To test:
#  os.system('buildmytasks')
#  execfile('mytasks.py')
#
# Some regression commands to run after making major changes:
# ALMA data:
#    casa 3.3 tables
# cd /net/yildun/export/data_1/thunter/alma/data/SciVer/TWHya
# au.plotbandpass('bandpass.bcal',showtsky=F,xaxis='freq',yaxis='amp',overlay='antenna',spw='',field='')
# au.plotbandpass('bandpass.bcal',showtsky=F,xaxis='freq',yaxis='amp',overlay='antenna,time',spw='',field='')
# au.plotbandpass('bandpass.bcal',showtsky=F,xaxis='freq',yaxis='both',phase=[-180,180],plotrange=[0,0,0,2])
# au.plotbandpass('bandpass.bcal',showtsky=F,xaxis='freq',yaxis='amp',overlay='antenna',spw='',field='',chanrange='1200~2000')
# au.plotbandpass('bandpass.bcal',showatm=T,xaxis='chan',yaxis='amp',overlay='antenna',spw='',field='',plotrange=[1200,2000,0,0])
# au.plotbandpass('bandpass.bcal',showatm=T,xaxis='chan',yaxis='amp',spw='',field='',plotrange=[1200,3840,0,0])
# au.plotbandpass('bandpass.bcal',showtsky=F,xaxis='chan',yaxis='amp',overlay='antenna',spw='',field='',showatm=T)
# au.plotbandpass('bandpass.bcal',showtsky=F,xaxis='freq',yaxis='phase',overlay='antenna',spw='',field='')
# au.plotbandpass('bandpass.bcal',showtsky=F,xaxis='freq',yaxis='phase',overlay='antenna',spw='',field='',chanrange='1200~1800')
# au.plotbandpass('bandpass.bcal',overlay='antenna',yaxis='amp',field='0~1,4',xaxis='freq',showtsky=T)
# au.plotbandpass('bandpass_b_skipspw19high.bcal',yaxis='amp',field='0',xaxis='freq',caltable2='bandpass_bpoly_skipspw19high.bcal',showpoints=True,spw=0,figfile='bpoly_overlay')
# au.plotbandpass('bandpass_b_skipspw19high.bcal',yaxis='phase',field='0',xaxis='freq',caltable2='bandpass_bpoly_skipspw19high.bcal',showpoints=True,spw=0,figfile='bpoly_overlay',caltable3='bandpass_bpoly_skipspw19high.bcal')
# au.plotbandpass('bandpass_b_skipspw19high.bcal',yaxis='both',field='0',xaxis='freq',caltable2='bandpass_bpoly_skipspw19high.bcal',showpoints=True,spw=0,figfile='bpoly_overlay',caltable3='bandpass_bpoly_skipspw19high.bcal')
# au.plotbandpass('X3c1.tsys.fdm',overlay='antenna',yaxis='amp',field='1',xaxis='chan',figfile='tsys.png',showtsky=T) 
# au.plotbandpass('X3c1.tsys.fdm',overlay='antenna',yaxis='amp',field='1',xaxis='chan',figfile='tsys.png',poln='y')
# au.plotbandpass('X3c1.tsys',overlay='antenna',yaxis='amp',field='0~1,4',xaxis='chan',figfile='tsys.png')
# au.plotbandpass('X3c1.tsys',overlay='time',yaxis='amp',field='2',xaxis='chan')
# au.plotbandpass('X3c1.tsys',overlay='',yaxis='amp',field='',xaxis='freq',showfdm=True)
# au.plotbandpass('X3c1.tsys',overlay='',yaxis='amp',field='2',xaxis='freq',chanrange='45~65')
# au.plotbandpass('bandpass_bpoly_skipspw19high.bcal')
# au.plotbandpass('bandpass.bcal',caltable2='bandpass.bcal_smooth',xaxis='freq')  
# au.plotbandpass('bandpass.bcal',caltable2='bandpass.bcal_smooth',yaxis='phase', xaxis='freq')
# au.plotbandpass('bandpass.bcal',caltable2='bandpass.bcal_smooth',xaxis='freq',chanrange='1000~3000')
# au.plotbandpass('bandpass.bcal',caltable2='bandpass.bcal_smooth',xaxis='freq',showtsky=T)
# au.plotbandpass('bandpass.bcal',caltable2='bandpass.bcal_smooth',xaxis='freq',poln='x',showflagged=True) 
# au.plotbandpass('bandpass.bcal',caltable2='bandpass.bcal_smooth',xaxis='freq',poln='x',showflagged=True, showtsky=T)
# au.plotbandpass(caltable='X3c1.tsys.fdm',caltable2='X3c1.tsys',    yaxis='amp',xaxis='freq',figfile='tsys.png') 
# au.plotbandpass(caltable='X3c1.tsys.fdm',caltable2='X3c1.tsys',    yaxis='amp',xaxis='freq',figfile='tsys.png', showtsky=T)  
# au.plotbandpass(caltable='X3c1.tsys',    caltable2='X3c1.tsys.fdm',yaxis='amp',xaxis='freq',figfile='tsys.png')
# au.plotbandpass(caltable='X3c1.tsys',    caltable2='X3c1.tsys.fdm',yaxis='amp',xaxis='freq',figfile='tsys.png', showtsky=T) 
# au.plotbandpass(caltable='X3c1.tsys',caltable2='X3c1.tsys.fdm',    yaxis='both',xaxis='freq',figfile='tsys.png',chanrange='1000~3000')
# au.plotbandpass(caltable='X3c1.tsys.fdm',caltable2='X3c1.tsys',    yaxis='both',xaxis='freq',figfile='tsys.png',chanrange='1000~3000')
# au.plotbandpass(caltable='X3c1.tsys.fdm',caltable2='X3c1.tsys',    yaxis='both',xaxis='freq',figfile='tsys.png',chanrange='1000~3000',showtsky=T) 
# au.plotbandpass(caltable='X3c1.tsys',    caltable2='X3c1.tsys.fdm',yaxis='both',xaxis='freq',figfile='tsys.png')  
# au.plotbandpass(caltable='X3c1.tsys',    caltable2='X3c1.tsys.fdm',yaxis='both',xaxis='freq',figfile='tsys.png', showtsky=T)  
# au.plotbandpass(caltable='X3c1.tsys.fdm',caltable2='X3c1.tsys',    yaxis='both',xaxis='freq',figfile='tsys.png',zoom='intersect')
# au.plotbandpass(caltable='X3c1.tsys',    caltable2='X3c1.tsys.fdm',yaxis='both',xaxis='freq',figfile='tsys.png',zoom='intersect')
# au.plotbandpass(caltable='X3c1.tsys.fdm',caltable2='X3c1.tsys',yaxis='amp',xaxis='freq',figfile='tsys.png',poln='XX') 
# au.plotbandpass(caltable='X3c1.tsys.fdm',caltable2='X3c1.tsys',yaxis='amp',field='1',xaxis='freq',figfile='tsys.png',poln='YY',zoom='intersect')
# au.plotbandpass(caltable='X3c1.tsys.fdm',caltable2='X3c1.tsys',yaxis='amp',field='1',xaxis='freq',figfile='tsys.png',poln='YY',zoom='intersect',showatm=T)
# au.plotbandpass(caltable='X3c1.tsys.fdm',yaxis='amp',field='1',xaxis='chan',figfile='tsys.png',poln='YY',zoom='intersect',showatm=T,showimage=T)
#
# tests for multi-field solution overlay: in SciVer/TWHya
# au.plotbandpass('band7multi_a6p7_titan.bcal',caltable2='band7multi_b.bcal',debug=F,xaxis='freq',yaxis='amp',chanrange='')
# au.plotbandpass(caltable='band7multi_b.bcal',caltable3='band7multi_bpoly_a6p7_titan.bcal',caltable2='band7multi_bpoly.bcal',xaxis='freq',yaxis='both')
#
# ALMA data, casa 3.4 tables:
# cd /lustre/naasc/thunter/alma/SV_data_TWHya/3.4guide
# au.plotbandpass(caltable='bandpass_all_bpoly_dv04',xaxis='freq',yaxis='both')       
# au.plotbandpass(caltable='bandpass_all_b_odd_dv04',caltable2='bandpass_all_bpoly_dv04',xaxis='freq',yaxis='both')
# ALMA data, FDM+TDM in same caltable
# au.plotbandpass(caltable='bandpass_all_b_odd_dv04',xaxis='freq',yaxis='phase',chanrange='', showatm=True)
# au.plotbandpass(caltable='bandpass_all_b_odd_dv04',xaxis='freq',yaxis='phase',chanrange='', channeldiff=5)
#
# ALMA 1-pol data:
# cd /lustre/naasc/thunter/singlePol
# au.plotbandpass('uid___A002_X494155_X23a.ms.split.bandpass',xaxis='freq')
#
# ALMA 4-pol data:
# cd /lustre/naasc/nmarceli/pipeline/root/2011.0.00054.CSV_2013_04_18T17_19_00.609/MOUS_uid___A002_X576a5e_X1e/SBS_uid___A002_X576a5e_X21/working
# au.plotbandpass('uid___A002_X61068c_Xc3.ms.spw1_3_5_7.solintinf_7_8125MHz.bcal.s9_2.tbl',xaxis='freq')
#
# EVLA dual-pol data:
#  cd /lustre/naasc/thunter/evla/10C-186/K_BnA_cont
#  au.plotbandpass('bandpasspcal.bcal',poln='',yaxis='both')
#  au.plotbandpass('bandpasspcal.bcal',poln='',yaxis='phase',overlay='antenna')
#  au.plotbandpass('bandpasspcal.bcal',poln='',yaxis='amp',overlay='antenna', chanrange='0~30',xaxis='freq')
#  au.plotbandpass('bandpasspcal.bcal',poln='',yaxis='both',showatm=T)
#  au.plotbandpass('bandpasspcal.bcal',poln='LL',yaxis='both')
#
# EVLA single-pol data:
#  cd /lustre/naasc/thunter/evla/AB1346/g19.36
#  au.plotbandpass('bandpass.bcal',caltable2='bandpass_bpoly.bcal',yaxis='both',xaxis='freq')
#
PLOTBANDPASS_REVISION_STRING = "$Id: task_plotbandpass.py,v 1.27 2013/06/30 17:14:54 thunter Exp $" 
import pylab as pb
import math, os, sys, re
import time as timeUtilities
import numpy as np
import re  # used for testing if a string is a float
import casadef     # necessary to read the casa version strings
from taskinit import * # necessary for tb.open() to work
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, ScalarFormatter

TOP_MARGIN  = 0.25   # Used if showatm=T or showtksy=T
BOTTOM_MARGIN = 0.25 # Used if showfdm=T
MAX_ATM_CALC_CHANNELS = 512

# This is a color sequence found online which has distinguishable colors
overlayColors = [
      [0.00,  0.00,  0.00],
      [0.00,  0.00,  1.00],
      [0.00,  0.50,  0.00],
      [1.00,  0.00,  0.00],
      [0.00,  0.75,  0.75],
#      [0.75,  0.00,  0.75], # magenta, same as atmcolor
      [0.25,  0.25,  0.25],
      [0.75,  0.25,  0.25],
      [0.95,  0.95,  0.00],
      [0.25,  0.25,  0.75],
#      [0.75,  0.75,  0.75],  this color is invisible for some reason
      [0.00,  1.00,  0.00],
      [0.76,  0.57,  0.17],
      [0.54,  0.63,  0.22],
      [0.34,  0.57,  0.92],
      [1.00,  0.10,  0.60],
#      [0.88,  0.75,  0.73],  invisible
      [0.10,  0.49,  0.47],
      [0.66,  0.34,  0.65],
      [0.99,  0.41,  0.23]]
overlayColors += overlayColors + overlayColors  # 17*3 = 51 total colors
overlayColors += overlayColors + overlayColors # try to support antenna,time
overlayColors += overlayColors + overlayColors # try to support antenna,time
overlayColors += overlayColors + overlayColors # try to support antenna,time
overlayColors += overlayColors + overlayColors # try to support antenna,time

# Enumeration to keep track of plot pages
PAGE_ANT = 0
PAGE_SPW = 1
PAGE_TIME = 2
PAGE_AP = 3

# Used to parse command line arguments
myValidCharacterList = ['~', ',', ' ', '*',] + [str(m) for m in range(10)]
myValidCharacterListWithBang = ['~', ',', ' ', '*', '!',] + [str(m) for m in range(10)]
LARGE_POSITIVE = +1e20
LARGE_NEGATIVE = -1e20
maxAntennaNamesAcrossTheTop = 17
maxTimesAcrossTheTop = 17
antennaVerticalSpacing = 0.018 # 0.016
antennaHorizontalSpacing = 0.05
xstartTitle = 0.07
ystartTitle = 0.95
xstartPolLabel = 0.05
ystartOverlayLegend = 0.933
opaqueSky = 270. # Kelvin, used for scaling TebbSky

developerEmail = "thunter@nrao.edu"

#class Polarization:
    # taken from Stokes.h in casa, for reference only
#    (Undefined, I,Q,U,V,RR,RL,LR,LL,XX,XY,YX,YY) = range(13)  

def refTypeToString(rtype):
    rtypes = ['REST','LSRK','LSRD','BARY','GEO','TOPO','GALACTO','LGROUP','CMB']
    return(rtypes[rtype])

def corrTypeToString(ptype):
    ptypes = ['Undefined','I','Q','U','V','RR','RL','LR','LL','XX','XY','YX','YY']
    mystring = ptypes[ptype]
#    print "mystring = %s" % (mystring)
    return(mystring)
    
def buildAntString(antID,msFound,msAnt):
    if (msFound):
        antstring = msAnt[antID]
    else:
        antstring = str(antID)
    if (antstring.isdigit()):
        Antstring = "Ant %s" % antstring
    else:
        Antstring = antstring
    return(antstring, Antstring)
      
      
def makeplot(figfile,msFound,msAnt,overlayAntennas,pages,pagectr,density,
             interactive,antennasToPlot,spwsToPlot,overlayTimes,
             locationCalledFrom,debug):
    if (type(figfile) == str):
        if (figfile.find('/')>=0):
            directories = figfile.split('/')
            directory = ''
            for d in range(len(directories)-1):
                directory += directories[d] + '/'
            if (os.path.exists(directory)==False):
                casalogPost(debug,"Making directory = %s" % (directory))
                os.system("mkdir -p %s" % directory)
    debug = False
    if (debug):
        print "makeplot(%d): pagectr=%d, len(pages)=%d, len(spwsToPlot)=%d, pages=" % (locationCalledFrom,
                                                              pagectr, len(pages),len(spwsToPlot)), pages
    ispw = spwsToPlot[pages[pagectr][PAGE_SPW]]
    t = pages[pagectr][PAGE_TIME] # + 1
    antstring, Antstring = buildAntString(antennasToPlot[pages[pagectr][PAGE_ANT]], msFound, msAnt)
    figfile = figfile.split('.png')[0]
    if (msFound):
        if (overlayAntennas):
            plotfilename = figfile+'.spw%02d'%(ispw)+'.t'+str(t)
        elif (overlayTimes):
            plotfilename = figfile+'.'+antstring+'.spw%02d'%(ispw)
        else:
            plotfilename = figfile+'.'+antstring+'.spw%02d'%(ispw)+'.t'+str(t)
    else:
        if (overlayAntennas):
            plotfilename = figfile+'.spw%02d'%(ispw)+'.t'+str(t)
        elif (overlayTimes):
            plotfilename = figfile+'.ant'+antstring+'.spw%02d'%(ispw)
        else:
            plotfilename = figfile+'.ant'+antstring+'.spw%02d'%(ispw)+'.t'+str(t)
    plotfilename += '.png'
    if (interactive == False or True):
        casalogPost(debug,"Building %s" % (plotfilename))
    pb.savefig(plotfilename, format='png', dpi=density)
    return(plotfilename)

def utdatestring(mjdsec):
    (mjd, dateTimeString) = mjdSecondsToMJDandUT(mjdsec)
    tokens = dateTimeString.split()
    return(tokens[0])

def mjdsecArrayToUTString(timerangeListTimes):
    """
    accepts [4866334935, 4866335281] etc.
    returns '08:04:10, 09:03:00' etc.
    """
    timerangeListTimesString = ''  
    for t in timerangeListTimes:
        timerangeListTimesString += utstring(t,3) + ' '
    return(timerangeListTimesString)

def utstring(mjdsec, xframeStart=110):
    (mjd, dateTimeString) = au.mjdSecondsToMJDandUT(mjdsec)
    tokens = dateTimeString.split()
    hoursMinutes = tokens[1][0:len(tokens[1])-3]
    hoursMinutesSeconds = tokens[1][0:len(tokens[1])]
    if (xframeStart == 110):  # 2011-01-01 UT 00:00
        return(tokens[0]+' '+tokens[2]+' '+hoursMinutes)
    elif (xframeStart == 3):
        return(hoursMinutesSeconds)
    else:  # 00:00
        return(hoursMinutes)
    
def utstring(mjdsec, xframeStart=110):
#    print "utstring(%f)" % mjdsec
    (mjd, dateTimeString) = mjdSecondsToMJDandUT(mjdsec)
    tokens = dateTimeString.split()
    hoursMinutes = tokens[1][0:len(tokens[1])-3]
    hoursMinutesSeconds = tokens[1][0:len(tokens[1])]
    if (xframeStart == 110):  # 2011-01-01 UT 00:00
        return(tokens[0]+' '+tokens[2]+' '+hoursMinutes)
    elif (xframeStart == 3):
        return(hoursMinutesSeconds)
    else:  # 00:00
        return(hoursMinutes)
    
def openBpolyFile(caltable, debug):
   mytb = createCasaTool(tbtool)
   mytb.open(caltable)
   desc = mytb.getdesc()
   if ('POLY_MODE' in desc):
      polyMode = mytb.getcol('POLY_MODE')
      casalogPost(debug,"This is a BPOLY solution = %s" % (polyMode[0]))
      polyType = mytb.getcol('POLY_TYPE')
      scaleFactor = mytb.getcol('SCALE_FACTOR')
      antenna1 = mytb.getcol('ANTENNA1')
      times = mytb.getcol('TIME')
      cal_desc_id = mytb.getcol('CAL_DESC_ID')
      nRows = len(polyType)
      for pType in polyType:
          if (pType != 'CHEBYSHEV'):
              casalogPost(debug,"I do not recognized polynomial type = %s" % (pType))
              return
      # Here we assume that all spws have been solved with the same mode
      uniqueTimesBP = np.unique(mytb.getcol('TIME'))
      nUniqueTimesBP = len(uniqueTimesBP)
      mystring = "There are %d unique times in the BPOLY solution: " % (nUniqueTimesBP)
      for u in uniqueTimesBP:
          mystring += '%.3f, ' % (u)
      casalogPost(debug,mystring)
      if (nUniqueTimesBP == 2):
          casalogPost(debug,"differing by %g seconds" % (uniqueTimesBP[1]-uniqueTimesBP[0]))
      nPolyAmp = mytb.getcol('N_POLY_AMP')
      nPolyPhase = mytb.getcol('N_POLY_PHASE')
      frequencyLimits = mytb.getcol('VALID_DOMAIN')
      increments = 0.001*(frequencyLimits[1,:]-frequencyLimits[0,:])
      frequenciesGHz = []
      for i in range(len(increments)):
         freqs = (1e-9)*np.arange(frequencyLimits[0,i],frequencyLimits[1,i],increments[i])
         frequenciesGHz.append(freqs)
      polynomialAmplitude = []
      polynomialPhase = []
      for i in range(len(polyMode)):
          polynomialAmplitude.append([1])
          polynomialPhase.append([0])
          if (polyMode[i] == 'A&P' or polyMode[i] == 'A'):
              polynomialAmplitude[i]  = mytb.getcell('POLY_COEFF_AMP',i)[0][0][0]
          if (polyMode[i] == 'A&P' or polyMode[i] == 'P'):
              polynomialPhase[i] = mytb.getcell('POLY_COEFF_PHASE',i)[0][0][0]

      mytb.close()
      mytb.open(caltable+'/CAL_DESC')
      nSpws = len(mytb.getcol('NUM_SPW'))
      spws = mytb.getcol('SPECTRAL_WINDOW_ID')
      spwBP = []
      for c in cal_desc_id:
          spwBP.append(spws[0][c])
      if (debug): casalog.post("Calling mytb.done 0")
      mytb.done()
      return([polyMode, polyType, nPolyAmp, nPolyPhase, scaleFactor, nRows, nSpws, nUniqueTimesBP,
              uniqueTimesBP, frequencyLimits, increments, frequenciesGHz,
              polynomialPhase, polynomialAmplitude, times, antenna1, cal_desc_id, spwBP])
   else:
      if (debug): casalog.post("Calling mytb.done 1")
      mytb.done()
      return([])
   # end of openBpolyFile()

def displayTimesArray(uniqueTimesPerFieldPerSpw):
    """
    Builds a string from an array of MJD second timestamps as UT timestamps
    """
    legendString = ''
    for s in uniqueTimesPerFieldPerSpw:
        legendString += "["
        for f in s:
            legendString += "["
            for t in f:
                legendString += "%s" % utstring(t,2)
                if (t != f[-1]):
                    legendString += ", "
            legendString += "]"
            if (f != s[-1]):
                legendString += ', '
        legendString += "], "
        if (s != uniqueTimesPerFieldPerSpw[-1]):
            legendString += ', '
    return(legendString)

def checkPolsToPlot(polsToPlot, corr_type_string, debug):
    firstFailure = 0
    for pol in polsToPlot:
        if ((pol in corr_type_string) == False):
            casalogPost(debug,"Polarization product %s is not in the ms" % (pol))
            firstFailure += 1
            if (pol in ['XX','YY']):
                polsToPlot = ['RR','LL']
            else:
                polsToPlot = ['XX','YY']
            break
    if (firstFailure>0):
       casalogPost(debug,"Looking for instead: %s" % (str(polsToPlot)))
       for pol in polsToPlot:
          if ((pol in corr_type_string) == False):
              casalogPost(debug,"Polarization product %s is not in the ms" % (pol))
              firstFailure += 1
              if (pol in ['XX']):
                  polsToPlot = ['YY']
              elif (pol in ['YY']):
                  polsToPlot = ['XX']
              elif (pol in ['RR']):
                  polsToPlot = ['LL']
              elif (pol in ['LL']):
                  polsToPlot = ['RR']
              break
    if (firstFailure > 1):
        casalogPost(debug,"Looking for instead: %s" % (str(polsToPlot)))
        for pol in polsToPlot:
            if ((pol in corr_type_string) == False):
                casalogPost(debug,"Polarization product %s is not in the ms" % (pol))
                return([])
    return(polsToPlot)

def getCorrType(msName, spwsToPlot, mymsmd, debug=False):
    """
    Open the DATA_DESCRIPTION_ID table.  Find the polarization_id of the first
    spw in the list of spwsToPlot, then read the CORR_TYPE from the POLARIZATION
    table.
    """
    mytb = createCasaTool(tbtool)
    mytb.open(msName+'/DATA_DESCRIPTION')
    spws = mytb.getcol('SPECTRAL_WINDOW_ID')
    polarization_id = mytb.getcol('POLARIZATION_ID')
    mytb.close()
    pol_id = 0
    telescopeName = mymsmd.observatorynames()[0]
    mytb.open(msName+'/POLARIZATION')
    for myspw in spwsToPlot:
#        print "looking for %d in %s" % (myspw, str(spws))
        row = list(spws).index(myspw)
        if (row >= 0):
            pol_id = polarization_id[row]
            corr_type = mytb.getcell('CORR_TYPE',pol_id)
            if (corr_type[0] >= 5 or (telescopeName.find('ALMA')<0 and telescopeName.find('VLA')<0)):
                # Undefined, I, Q, U, V, which ALMA and VLA never use
                # Need to allow non-VLA, non-ALMA to stop here
                break
    mytb.close()
    mytb.done()
    corr_type_string = []
    if (len(corr_type) == 4):
        casalogPost(debug,"This is a 4-polarization dataset.")
        if (corr_type[0] in [5,6,7,8]):
            corr_type = [5,8]
        elif (corr_type[0] in [9,10,11,12]):
            corr_type = [9,12]
        else:
            print "Unsupported polarization types = ", corr_type
            return(corr_type, corr_type_string)
    # This overrides the len(gain_table) because it can have length=2 even when only 1 pol present
    nPolarizations = len(corr_type)
    for ct in corr_type:
        corr_type_string.append(corrTypeToString(ct))
    if (debug):
        print "corr_types = ", corr_type,  " = ", corr_type_string
    return(corr_type, corr_type_string, nPolarizations)

def writeArgument(f,name,arg):
    if (type(arg) == str):
        s = "%-18s = '%s'" % (name,arg)
        t = "%s='%s'" % (name,arg)
    else:
        s = "%-18s = %s" % (name,str(arg))
        t = "%s=%s" % (name,arg)
    f.write(s+'\n')
    return(t)

def channelDifferences(y, x):
    """
    Takes a vector, and computes the channel-to-channel derivative.
    - Todd Hunter
    """
    x = np.array(x)
    y = np.array(y)
    if (len(x) > 1):
        channelWidth = x[1]-x[0]
        d = (np.diff(y)/np.diff(x))
        d *= channelWidth 
        newx = (x[1:]+x[:-1])/2.  # midpoints of input x-axis
        return(d, newx)
    else:
        return(y,x)

def getDataColumnName(inputMs, debug):
    mytb = createCasaTool(tbtool)
    mytb.open(inputMs)
    colnames = mytb.colnames()
    correctedDataColumnName = ''
    modelDataColumnName = ''
    if 'FLOAT_DATA' in colnames:
        dataColumnName = 'FLOAT_DATA'
        correctedDataColumnName = 'FLOAT_DATA'
    elif 'DATA' in colnames:
        dataColumnName = 'DATA'
    if 'CORRECTED_DATA' in colnames:
        correctedDataColumnName = 'CORRECTED_DATA'
    if 'MODEL_DATA' in colnames:
        modelDataColumnName = 'MODEL_DATA'
    if (debug): casalog.post("Calling mytb.done 2")
    mytb.done()
    return(dataColumnName)

def doPolarizations(mymsmd, inputMs, debug=False) :
    # This function is obsolete. There may be no OBSERVE_TARGET intents in a dataset!
    # Determine the number of polarizations for the first OBSERVE_TARGET intent.
    # Used by plotbandpass for BPOLY plots since the number of pols cannot be inferred
    # correctly from the caltable alone.  You cannot not simply use the first row, because
    # it may be a pointing scan which may have different number of polarizations than what
    # the TARGET and BANDPASS calibrator will have.
    # -- T. Hunter
    if (debug): print "doPolarizations()"
    myscan = -1
    starttime = timeUtilities.time()
    for s in range(1,mymsmd.nscans()+1):
        if (debug): print "s = %s" % (str(s))
        intents = mymsmd.intentsforscan(s)
        for i in intents:
            if (i.find('OBSERVE_TARGET')>=0):
                myscan = s
#                print "First OBSERVE_TARGET scan = %s" % (str(myscan))
                break
        if (myscan >= 0):
            break
    if (myscan == -1):
        # if there is no OBSERVE_TARGET, then just use the first scan
        myscan = 0
    dataColumnName = getDataColumnName(inputMs,debug)
    if (debug): print "dataColumnName = %s" % (dataColumnName)
    mytb = createCasaTool(tbtool)
    mytb.open("%s" % inputMs)
    if (myscan == 0):
        # assume the first row in the table is for the first scan, to save time
        nPolarizations = np.shape(mytb.getcell(dataColumnName,0))[0]
    else:
        scans = mytb.getcol('SCAN_NUMBER')
        nPolarizations = 0
        for s in range(len(scans)):
            if (scans[s]==myscan):
                nPolarizations = np.shape(mytb.getcell(dataColumnName,s))[0]
                break
    mytb.close()
    donetime = timeUtilities.time()
    return(nPolarizations)

def getnspw(mymsmd):
    if (casadef.subversion_revision > '22653'):
        return(mymsmd.nspw(False))
    else:
        return(mymsmd.nspw())
        

def drawOverlayTimeLegends(xframe,firstFrame,xstartTitle,ystartTitle,caltable,titlesize,
                           fieldIndicesToPlot,ispwInCalTable,uniqueTimesPerFieldPerSpw,
                           timerangeListTimes, solutionTimeThresholdSeconds,debugSloppyMatch,
                           ystartOverlayLegend,debug,mysize, fieldsToPlot,myUniqueColor,
                           timeHorizontalSpacing, fieldIndex,overlayColors,
                           antennaVerticalSpacing, overlayAntennas, timerangeList, caltableTitle):
    """
    Draws the legend at the top of the page, if it is the correct time to do so,
    including the overlayTimes, the 'UT' label, and the caltable name.
    """
    if (xframe == firstFrame):
#      if (overlayAntennas == False):
        # draw title including caltable name
        pb.text(xstartTitle, ystartTitle, caltableTitle, size=titlesize,
                color='k', transform=pb.gcf().transFigure)
        # support multi-fields with overlay='time'
        uTPFPS = []
        uTPFPStimerange = []
        for f in fieldIndicesToPlot:
            for t in uniqueTimesPerFieldPerSpw[ispwInCalTable][f]:
                matched, mymatch = sloppyMatch(t, timerangeListTimes, solutionTimeThresholdSeconds,
                                               myprint=debugSloppyMatch, whichone=True)
                if (matched):
                    uTPFPS.append(t)
                    uTPFPStimerange.append(mymatch)
        uTPFPS = np.sort(uTPFPS)
        for a in range(len(uTPFPS)):
            legendString = utstring(uTPFPS[a],220)
            if (debug): print "----> Defined legendString: %s" % (legendString)
            if (a==0):
                pb.text(xstartTitle-0.02, ystartOverlayLegend, 'UT',color='k',fontsize=mysize,
                        transform=pb.gcf().transFigure)
            if (a < maxTimesAcrossTheTop):
                x0 = xstartTitle + (a*timeHorizontalSpacing)
                y0 = ystartOverlayLegend
            else:
                # start going down the righthand side
                x0 = xstartTitle + (maxTimesAcrossTheTop*timeHorizontalSpacing)
                y0 = ystartOverlayLegend-(a-maxTimesAcrossTheTop)*antennaVerticalSpacing
            for tlt in timerangeListTimes:
                if (debug):
                    print "3)checking time %d" % (t)
                if (sloppyMatch(uTPFPS[a],timerangeListTimes,solutionTimeThresholdSeconds,debugSloppyMatch)):
                    myUniqueTime = uTPFPS[a]
                    if (debug):
                        print "3)setting myUniqueTime to %d" % (myUniqueTime)
            if (debug): print "----> Drawing legendString: %s" % (legendString)
            if (len(fieldsToPlot) > 1 or len(timerangeList) > 1):
                if (debug):
                    print "len(uTPFPS)=%d, a=%d, len(myUniqueColor)=%d" % (len(uTPFPS),a,len(myUniqueColor))
#                pb.text(x0, y0, legendString,color=overlayColors[timerangeList[a]],fontsize=mysize,
#                        transform=pb.gcf().transFigure)
                pb.text(x0, y0, legendString,color=overlayColors[timerangeList[uTPFPStimerange[a]]],fontsize=mysize,
                        transform=pb.gcf().transFigure)
            else:
                pb.text(x0, y0, legendString,fontsize=mysize, transform=pb.gcf().transFigure)

def drawAtmosphereAndFDM(showatm, showtsky, atmString, subplotRows, mysize, TebbSky,
                         TebbSkyImage,plotrange, xaxis, atmchan, atmfreq, transmission,
                         subplotCols, showatmPoints,xframe, channels,LO1,atmchanImage,
                         atmfreqImage,transmissionImage, firstFrame,showfdm,nChannels,tableFormat,
                         originalSpw_casa33, chanFreqGHz_casa33,originalSpw,chanFreqGHz,
                         overlayTimes, overlayAntennas, xant, antennasToPlot):
    """
    If requested by the user at the command line, draw the atmospheric curve
    and the FDM window locations.
    """
    if ((showatm or showtsky) and len(atmString) > 0): 
        DrawAtmosphere(showatm, showtsky, subplotRows, atmString,
                       mysize, TebbSky, plotrange, xaxis, atmchan,
                       atmfreq, transmission, subplotCols,
                       showatmPoints=showatmPoints, xframe=xframe, channels=channels)
        if (LO1 != ''):
            # Now draw the image band
            DrawAtmosphere(showatm,showtsky, subplotRows, atmString,
                mysize, TebbSkyImage, plotrange, xaxis,
                atmchanImage, atmfreqImage, transmissionImage,
                subplotCols, LO1, xframe, firstFrame, showatmPoints, channels=channels)
    # The following case is needed for the case that overlay='antenna,time' and
    # the final timerange is flagged on the final antenna.
#    if (overlayTimes==False or overlayAntennas==False or xant==antennasToPlot[-1]):
    # Because this function is now only called from one place, setting this to
    # True is what we want. - 18-Jun-2013
    if (True):
        if (xaxis.find('freq')>=0 and showfdm and nChannels <= 256):
            if (tableFormat == 33):
                showFDM(originalSpw_casa33, chanFreqGHz_casa33)
            else:
                showFDM(originalSpw, chanFreqGHz)

def DrawPolarizationLabelsForOverlayTime(xstartPolLabel,ystartPolLabel,corr_type,polsToPlot,
                                         channeldiff,ystartMadLabel,subplotRows,gamp_mad,mysize,
                                         ampmarkstyle,markersize,ampmarkstyle2):
    """
    Currently this is only called for amp vs. X plots. The corresponding code for phase
    vs. X plots is still inside plotbandpass().  But this is okay because overlay='time'
    is mainly intended for Tsys plots.
    """
    x0 = xstartPolLabel
    y0 = ystartPolLabel
    if (corrTypeToString(corr_type[0]) in polsToPlot):
        if (channeldiff > 0):
            pb.text(x0, ystartMadLabel-0.03*subplotRows*0,
                    corrTypeToString(corr_type[0])+' MAD = %.4f'%(gamp_mad[0]['mad']),
                    color='k',size=mysize, transform=pb.gca().transAxes)
        if (ampmarkstyle.find('-')>=0):
            pb.text(x0, y0, corrTypeToString(corr_type[0])+' solid', color='k',
                    size=mysize, transform=pb.gca().transAxes)
        else:
            pb.text(x0+0.02, y0, corrTypeToString(corr_type[0]), color='k',
                    size=mysize, transform=pb.gca().transAxes)
            pdesc = pb.plot([x0-0.1], [y0], '%sk'%ampmarkstyle, markersize=markersize,
                            scalex=False,scaley=False, transform=pb.gca().transAxes)
    if (len(corr_type) > 1):
        if (corrTypeToString(corr_type[1]) in polsToPlot):
            if (channeldiff > 0):
                pb.text(x0, ystartMadLabel-0.03*subplotRows*1,
                        corrTypeToString(corr_type[1])+' MAD = %.4f'%(gamp_mad[1]['mad']),
                        color='k',size=mysize, transform=pb.gca().transAxes)
            if (ampmarkstyle2.find('--')>=0):
                pb.text(x0, y0-0.03*subplotRows, corrTypeToString(corr_type[1])+' dashed',
                        color='k', size=mysize, transform=pb.gca().transAxes)
            else:
                pb.text(x0+0.02*xrange, y0-0.03*subplotRows, corrTypeToString(corr_type[1]),
                        color='k', size=mysize, transform=pb.gca().transAxes)
                pdesc = pb.plot([x0-0.1], [y0-0.03*subplotRows], '%sk'%ampmarkstyle2,
                                markersize=markersize, scalex=False,scaley=False, transform=pb.gca().transAxes)

def plural(u):
    """
    If the length of the array passed is > 1, return 's', otherwise return ''.
    """
    if (len(u) > 1):
        return('s')
    else:
        return('')

def casalogPost(debug,mystring):
    casalog.post(mystring)
    if (debug): print mystring
    
def plotbandpass(caltable='', antenna='', field='', spw='', yaxis='amp',
                 xaxis='chan', figfile='', plotrange=[0,0,0,0], 
                 caltable2='', overlay='', showflagged=False, timeranges='',
                 buildpdf=False, caltable3='', markersize=3, density=108,
                 interactive=True, showpoints='auto', showlines='auto',
                 subplot='22', zoom='', poln='', showatm=False, pwv='auto',
                 gs='gs', convert='convert', chanrange='',
                 solutionTimeThresholdSeconds=30.0, debug=False,
                 phase='',  vis='', showtsky=False, showfdm=False,showatmfield='',
                 lo1='', showimage=False, showatmPoints=False, parentms='', 
                 pdftk='pdftk', channeldiff=False, edge=8):
    """
    This is a task to plot bandpass and Tsys calibration tables faster and more
    flexibly than plotcal, including the ability to overlay the atmospheric transmission,
    and to create multi-page plots as pngs and combine them into single PDF documents.
    It works with both the old style and new style cal tables.  The source code
    is in task_plotbandpass.py.  For more detailed help, see examples at:
    http://casaguides.nrao.edu/index.php?title=Plotbandpass
    -- Todd Hunter
    """
    casalog.origin('plotbandpass')
    casalogPost(debug,"%s" % (PLOTBANDPASS_REVISION_STRING))
    DEBUG = debug
    help = False
    vm = '' # unused variable, now that msmd is available in casa
    if (help):
        print "Usage: plotbandpass(caltable='', antenna='', field='', spw='', yaxis='amp',"
        print "   xaxis='chan', figfile='', plotrange=[0,0,0,0], caltable2=''," 
        print "   overlay='', showflagged=False, timeranges='', buildpdf=False, caltable3='',"
        print "   markersize=3, density=108, interactive=True, showpoints='auto',"
        print "   showlines='auto', subplot='22', zoom='', poln='', showatm=False, pwv='auto',"
        print "   gs='gs', convert='convert', chanrange='', debug=False,"
        print "   solutionTimeThresholdSeconds=30.0, phase='', vis='', showtsky=False,"
        print "   showfdm=False, showatmfield='', lo1='', showimage=False,"
        print "   showatmPoints=False, parentms='', pdftk='pdftk')"
        print " antenna: must be either an ID (int or string or list), or a single antenna name or list"
        print " buildpdf: True/False, if True and figfile is set, assemble pngs into a pdf"
        print " caltable: a bandpass table, of type B or BPOLY"
        print " caltable2: a second cal table, of type BPOLY or B, to overlay on a B table"
        print " caltable3: a third cal table, of type BPOLY, to overlay on the first two"
        print " chanrange: set xrange ('5~100') over which to autoscale y-axis for xaxis='freq'"
        print " channeldiff: set to value > 0 (sigma) to plot derivatives of amplitude"
        print " convert: full path for convert command (in case it's not found)"
        print " density: dpi to use in creating PNGs and PDFs (default=108)"
        print " edge: the number of edge channels to ignore in finding outliers (for channeldiff>0)"
        print " field: must be an ID, source name, or list thereof; can use trailing *: 'J*'"
        print " figfile: the base_name of the png files to save: base_name.antX.spwY.png"
        print " gs: full path for ghostscript command (in case it's not found)"
        print " interactive: if False, then figfile will run to completion automatically and no gui"
        print " lo1: specify the LO1 setting (in GHz) for the observation"
        print " overlay: 'antenna' or 'time', make 1 plot with different items in colors"
        print " showflagged:  show the values of data, even if flagged"
        print " markersize: size of points (default=3)"
        print " vis: name of the ms for this table, in case it does not match the string in the caltable"
        print " parentms: name of the parent ms, in case the ms has been previously split"
        print " pdftk: full path for pdftk command (in case it's not found)"
        print " phase: the y-axis limits to use for phase plots when yaxis='both'"
        print " plotrange: define axis limits: [x0,x1,y0,y1] where 0,0 means auto"
        print " poln: polarizations to plot (e.g. 'XX','YY','RR','LL' or '' for both)"
        print " pwv: define the pwv to use for the showatm option: 'auto' or value in mm"
        print " showatm: compute and overlay the atmospheric transmission curve"
        print " showatmfield: for overlay='time', use first observation of this fieldID or name"
        print " showatmPoints: draw atmospheric curve with points instead of a line"
        print " showfdm: when showing TDM spws with xaxis='freq', draw locations of FDM spws"
        print " showimage: also show the atmospheric curve for the image sideband (in black)"
        print " showtsky: compute and overlay the sky temperature curve instead of transmission"
        print " showlines: draw lines connecting the data (default=T for amp, F for phase)"
        print " showpoints: draw points for the data (default=F for amp, T for phase)"
        print " solutionTimeThresholdSeconds: consider 2 solutions simultaneous if within this interval (default=30)"
        print " spw: must be single ID or list or range (e.g. 0~4, not the original ID)"
        print " subplot: 11,22,32 or 42 for RowsxColumns (default=22), any 3rd digit is ignored"
        print " timeranges: show only these timeranges, the first timerange being 0"
        print " xaxis: 'chan' or 'freq'"
        print " yaxis: 'amp', 'tsys', 'phase', or 'both' amp&phase == 'ap'; append 'db' for dB"
        print " zoom: 'intersect' will zoom to overlap region of caltable with caltable2"
        return()
    mytimestamp = timeUtilities.time()
    debugSloppyMatch = debug
    doneOverlayTime = False  # changed from True on 08-nov-2012
    missingCalWVRErrorPrinted = False
  
    # initialize the arguments to DrawAtmosphereAndFDM() 
    TebbSky = None      
    TebbSkyImage = None 
    atmchan = None      
    atmfreq = None      
    transmission = None 
    atmchanImage = None      
    atmfreqImage = None      
    transmissionImage = None 
    originalSpw_casa33 = None
    originalSpw = None       
    chanFreqGHz_casa33 = None
    chanFreqGHz = None
    # initialize arguments to DrawPolarizationLabelsForOverlayTime()
    gamp_mad = None
    
    if (False):
      # Write a .last file
      if (os.access('plotbandpass.last',os.W_OK)):
        cmd = 'plotbandpass'
        lastfile = open('%s.last'%cmd,'w')
        lastfile.write('taskname           = "%s"\n'%cmd)
        cmd += '(' + writeArgument(lastfile, "caltable", caltable)
        cmd += ',' + writeArgument(lastfile, "antenna" , antenna)
        cmd += ',' + writeArgument(lastfile, "field" , field)
        cmd += ',' + writeArgument(lastfile, "spw" , spw)
        cmd += ',' + writeArgument(lastfile, "yaxis", yaxis)
        cmd += ',' + writeArgument(lastfile, "xaxis", xaxis)
        cmd += ',' + writeArgument(lastfile, "figfile", figfile)
        cmd += ',' + writeArgument(lastfile, "plotrange" , plotrange)
        cmd += ',' + writeArgument(lastfile, "caltable2", caltable2)
        cmd += ',' + writeArgument(lastfile, "overlay", overlay)
        cmd += ',' + writeArgument(lastfile, "showflagged", showflagged)
        cmd += ',' + writeArgument(lastfile, "timeranges", timeranges)
        cmd += ',' + writeArgument(lastfile, "buildpdf", buildpdf)
        cmd += ',' + writeArgument(lastfile, "caltable3", caltable3)
        cmd += ',' + writeArgument(lastfile, "markersize", markersize)
        cmd += ',' + writeArgument(lastfile, "density", density)
        cmd += ',' + writeArgument(lastfile, "interactive", interactive)
        cmd += ',' + writeArgument(lastfile, "showpoints", showpoints)
        cmd += ',' + writeArgument(lastfile, "showlines", showlines)
        cmd += ',' + writeArgument(lastfile, "subplot", subplot)
        cmd += ',' + writeArgument(lastfile, "zoom", zoom)
        cmd += ',' + writeArgument(lastfile, "poln", poln)
        cmd += ',' + writeArgument(lastfile, "showatm", showatm)
        cmd += ',' + writeArgument(lastfile, "showatmfield", showatmfield)
        cmd += ',' + writeArgument(lastfile, "pwv", pwv)
        cmd += ',' + writeArgument(lastfile, "gs", gs)
        cmd += ',' + writeArgument(lastfile, "convert", convert)
        cmd += ',' + writeArgument(lastfile, "chanrange", chanrange)
        cmd += ',' + writeArgument(lastfile, "solutionTimeThresholdSeconds", solutionTimeThresholdSeconds)
        cmd += ',' + writeArgument(lastfile, "debug", debug)
        #  cmd += ',' + writeArgument(lastfile, "vm", vm)
        cmd += ',' + writeArgument(lastfile, "phase", phase)
        cmd += ',' + writeArgument(lastfile, "vis", vis)
        cmd += ',' + writeArgument(lastfile, "parentms", parentms)
        cmd += ',' + writeArgument(lastfile, "lo1", lo1)
        cmd += ',' + writeArgument(lastfile, "showimage", showimage)
        cmd += ',' + writeArgument(lastfile, "showtsky", showtsky)
        cmd += ',' + writeArgument(lastfile, "showatmPoints", showatmPoints)
        cmd += ',' + writeArgument(lastfile, "showfdm", showfdm)
        cmd += ',' + writeArgument(lastfile, "pdftk", pdftk) + ')'
        lastfile.write('#%s\n'%(cmd))
        lastfile.close()
    if (showimage == False):
        LO1 = lo1 = ''
    elif (lo1 != ''):
        if re.match("^\d+?\.\d+?$", lo1) is None:
                print "lo1 must be a float (entered as a string or number)"
                return
        lo1 = float(lo1)
        if (lo1 > 1e6):
            # convert from Hz to GHz
            lo1 *= 1e-9
    if (showatm and showtsky):
        print "You have selected both showatm and showtsky!  Defaulting to showatm=True only."
        showtsky = False
    if (showatm==False and showtsky==False and showatmfield!=''):
        print "Defaulting to showatm=True because showatmfield was specified."
        showatm = True
    if (showatm==False and showtsky==False and showimage==True):
        print "Defaulting to showatm=True because showimage was True."
        showatm = True
    if (overlay.find('time') < 0 and showatmfield != ''):
        print "The showatmfield only has meaning for overlay='time'."
        return()
    
    if (plotrange=='' or plotrange==[]):
        plotrange = [0,0,0,0]
    if (type(plotrange) != list):
        print "plotrange must be an array:  [0,1,-180,180]"
        return()
    if (len(plotrange) < 4):
        print "plotrange must be an array:  [0,1,-180,180]"
        return()
    if (phase != ''):
        if (type(phase) != list):
            print "phase must be either '' or 2 values: [x,y]"
            return()
        if (len(phase) != 2):
            print "phase must be either '' or 2 values: [x,y]"
            return()
  
    if (edge < 0):
        print "edge must be >= 0"
        return(vm)
    
    if (buildpdf and figfile==''):
        print "With buildPDF=True, you must specify figfile='yourFileName' (.png will be appended if necessary)."
        return()
  
    if (interactive==False and figfile=='' and channeldiff == False):
        print "With interactive=False and channeldiff=False, you must specify figfile='yourFileName' (.png will be appended if necessary)."
        return()
  
    pxl = 0 # polarization number to use for setting xlimits if plotrange=[0,0...]
    if (type(chanrange) != str):
        if (type(chanrange) != list):
            print "Chanrange must be a string or list:  '8~120' or [8,120]"
            return()
        elif (len(chanrange) != 2):
            print "Chanrange must be a string or list:  '8~120' or [8,120]"
            return()
        elif ((type(chanrange[0]) != int) or (type(chanrange[1]) != int)):
            print "Chanrange list members must be integers, not %s, %s" % (type(chanrange[0]), type(chanrange[1]))
            return
    elif (len(chanrange) < 1):
        chanrange = [0,0]
    else:
        if (chanrange.find('~')<0):
            print "Invalid chanrange string, no tilde found"
            return()
        tokens = chanrange.split('~')
        if (len(tokens) < 2):
            print "Invalid chanrange string, too few tokens"
            return()
        if (xaxis.find('chan')>=0):
                print "The chanrange parameter is only valid for xaxis='freq', and only if the plotrange is [0,0,0,0]."
                return()
        try:
            chanrange = [int(tokens[0]),int(tokens[1])]
            if (DEBUG):
                print "Using chanrange = %s" % (str(chanrange))
        except:
            print "Invalid chanrange, not integers"
            return()
    if (chanrange[0] < 0):
        print "Invalid chanrange, cannot be negative"
        return()
    if ((chanrange[0] != 0 or chanrange[1] != 0) and (plotrange[0] != 0 or plotrange[1] != 0 or plotrange[2] != 0 or plotrange[3] != 0)):
        print "If chanrange is specified, then plotrange must be all zeros."
        return()
        
    if (pwv==''):
        pwv = 1.0
    if (type(poln) != list):
          poln = poln.upper()
    if (poln == 'X'):
          poln = 'XX'
    if (poln == 'Y'):
          poln = 'YY'
    if (poln == 'X,Y' or poln=='Y,X'):
          poln = 'XX,YY'
    if (poln == 'R'):
          poln = 'RR'
    if (poln == 'L'):
          poln = 'LL'
    if (poln == 'R,L' or poln=='L,R'):
          poln = 'RR,LL'
  
    # Parse the polarizations to plot from the command line
    # Prior to opening the .ms (later), we cannot tell which products are actually present
    useAllPols = False
    if (poln == ''):
        useAllPols = True
        polsToPlot = ['XX','YY']  # assume ALMA initially
    elif (type(poln) == list):
        polsToPlot = poln
    else:
        if ((poln in ['','RR','RL','LR','LL','XX','XY','YX','YY','RR,LL','XX,YY']) == False):
            print "Unrecognized polarization option = %s" % (poln)
            return()
        if (poln.find(',')>0):
            polsToPlot = poln.split(',')
        else:
            polsToPlot = [poln]
        
          
    if ((overlay in ['antenna', 'time', '', 'antenna,time', 'time,antenna']) == False): # try to support antenna,time
       print "Unrecognized option for overlay: only 'antenna' and 'time' are supported, not both."
       return()
       
    allowedFrames = [11,22,32,42]
    if (int(subplot) > 100):
        # This will accept 111, 221, 321, 421, etc.
        subplot /= 10
    if ((int(subplot) in allowedFrames)==False):
      print "Subplot choice (rows x columns) must be one of %s" % (str(allowedFrames))
      print "(with an optional trailing digit that is ignored)."
      return()
  
    if (subplot == 11):
        timeHorizontalSpacing = 0.06
    else:
        timeHorizontalSpacing = 0.05

    if (yaxis.find('both')<0 and yaxis.find('ap')<0 and yaxis.find('tsys')<0 and
        yaxis.find('amp')<0 and yaxis.find('phase')<0):
        print "Invalid yaxis.  Must be 'amp', 'tsys', 'phase' or 'both'."
        return()
  
    if (yaxis.find('tsys')>=0):
        yaxis = 'amp'
  
    if (xaxis.find('chan')<0 and xaxis.find('freq')<0):
        print "Invalid xaxis.  Must be 'chan' or 'freq'."
        return()
  
    if (showatm and showtsky):
        print "showatm=True and showtsky=True are mutually exclusive options"
        return()
  
    if (showfdm and xaxis.find('freq')<0):
        print "The option showfdm=True requires xaxis='freq'."
        return()
  
    # Plotting settings
    minPhaseRange = 0.2
    plotfiles = []
    if (int(subplot) == 11):
      mysize = '10'
      titlesize = '10'
    elif (int(subplot) == 22 or int(subplot) == 32):
      mysize = '8'
      titlesize = '8'
    else:
      mysize = '7'
      titlesize = '8'
    if (type(subplot) == str):
        subplot = int(subplot)
    validSubplots = [11,22,32,42]
    if (subplot in validSubplots == False):
        print "Invalid subplot = %d.  Valid options are: %s" % (subplot,str(validSubplots))
        return()
    xframeStart = int(subplot)*10  # i.e. 110 or 220 or 420
    firstFrame = xframeStart + 1
    lastFrame = xframeStart + (subplot/10)*(subplot%10)
    bottomRowFrames = [111,223,224,325,326,427,428]  # try to make this more general
    leftColumnFrames = [111,221,223,321,323,325,421,423,425,427]
    rightColumnFrames = [111,222,224,322,324,326,422,424,426,428]
    subplotCols = subplot % 10
    subplotRows = subplot/10
    ystartPolLabel = 1.0-0.04*subplotRows
    ystartMadLabel = 0.04*subplotRows
    if (subplotCols == 1):
        fstringLimit = 40 # character length of multi-field overlay title string
    elif (subplotCols == 2):
        fstringLimit = 12 # character length of multi-field overlay title string
    
    xframe = xframeStart
    xcolor = 'b'
    ycolor = 'g'
    pcolor = ['b','g']
    x2color = 'k'
    y2color = 'c'
    p2color = ['k','c']
    x3color = 'm'
    y3color = 'r'
    p3color = ['m','r']
    if (showpoints == 'auto'):
        if (showlines == 'auto'):
            ampmarkstyle = '-'
            phasemarkstyle = '.'
            if (len(polsToPlot) == 1):
                  ampmarkstyle2 = '-'
            else:
                  ampmarkstyle2 = '--'
            phasemarkstyle2 = 'o'
        elif (showlines == False):
            ampmarkstyle = '.'
            ampmarkstyle2 = 'o'
            phasemarkstyle = '.'
            phasemarkstyle2 = 'o'
        else:
            ampmarkstyle = '-'
            phasemarkstyle = '-'
            if (len(polsToPlot) == 1):
                  ampmarkstyle2 = '-'
                  phasemarkstyle2 = '-'
            else:
                  ampmarkstyle2 = '--'
                  phasemarkstyle2 = '--'
    elif (showpoints == True):
        if (showlines == 'auto'):
            ampmarkstyle = '.-'
            phasemarkstyle = '.'
            if (len(polsToPlot) == 1):
                  ampmarkstyle2 = 'o-'
            else:
                  ampmarkstyle2 = 'o--'
            phasemarkstyle2 = 'o'
        elif (showlines == False):
            ampmarkstyle = '.'
            ampmarkstyle2 = 'o'
            phasemarkstyle = '.'
            phasemarkstyle2 = 'o'
        else:
            ampmarkstyle = '.-'
            phasemarkstyle = '.-'
            if (len(polsToPlot) == 1):
                  ampmarkstyle2 = 'o-'
                  phasemarkstyle2 = 'o-'
            else:
                  ampmarkstyle2 = 'o--'
                  phasemarkstyle2 = 'o--'
    else:  # showpoints == False
        if (showlines == False):
            print 'You must have either showpoints or showlines set True or auto, assuming showlines=T'
        ampmarkstyle = '-'
        phasemarkstyle = '-'
        if (len(polsToPlot) == 1):
              ampmarkstyle2 = '-'
              phasemarkstyle2 = '-'
        else:
              ampmarkstyle2 = '--'
              phasemarkstyle2 = '--'
  
    ampmarkstyles = [ampmarkstyle,ampmarkstyle2]
    phasemarkstyles = [phasemarkstyle,phasemarkstyle2]
    # bpoly solutions should always be shown as lines, not dots or dots+lines
    bpolymarkstyle = '-'
  
    amplitudeWithPhase = (yaxis.find('both')>=0 or yaxis.find('ap')>=0)
    if (amplitudeWithPhase):
        myhspace = 0.30
        if (overlay.find('antenna')>=0 or overlay.find('time')>=0):
            print "Option 'overlay' is incompatible with yaxis='both'.  Pick either amp or phase."
            return()
    else:
        myhspace = 0.30
    if (subplot/10 > 2):
        myhspace = 0.4
    if (subplot/10 > 3):
        myhspace = 0.6
    mywspace = 0.25
    
    # Now open the Bandpass solution table
    if (len(caltable) < 1):
        print "You need to specify a caltable."
        return(vm)
    if (caltable[-1] == '/'):
        print "Stripping off the trailing '/' from the caltable name."
        caltable = caltable[:-1]
    mytb = createCasaTool(tbtool)
    try:
        if (DEBUG): print "Trying to open: %s." % (caltable)
        mytb.open(caltable)
    except:
        print "Could not open the caltable = %s" % (caltable)
        return()
    if (len(caltable) > 100):
        caltableTitle = '...' + caltable[-100:]
    else:
        caltableTitle = caltable
    names = mytb.colnames()
    ant = mytb.getcol('ANTENNA1')
    fields = mytb.getcol('FIELD_ID')
    if (DEBUG):
        print "FIELD_ID column = %s" % (str(fields))
    validFields = False
    for f in fields:
        if (f != -1):
            validFields = True
    if (validFields == False):
        print "The field_id is -1 (invalid) for all rows of this caltable."
        print "Did you remember to run assignFieldAndScanToSolution()?"
        return()
    try:
        flags = {}
        for f in range(len(fields)):
            flags[f] = mytb.getcell('FLAG',f)
    except:
        print "No Flag column found. Are you sure this is a bandpass solution file, or is it the .ms?"
        print "If it is a solution file, does it contain solutions for both TDM and FDM spws?"
        return()
  
    times = mytb.getcol('TIME')
    intervals = mytb.getcol('INTERVAL')
    if ('SPECTRAL_WINDOW_ID' not in names):
        tableFormat = 33
        cal_desc_id = mytb.getcol('CAL_DESC_ID')
        VisCal = (mytb.info())['subType']
        if (VisCal == "BPOLY"):
            casalogPost(debug,"This appears to be a BPOLY cal table written in the casa 3.3/3.4 style.")
        else:
            casalogPost(debug,"This appears to be an old-format cal table from casa 3.3 or earlier.")
        if (debug): print "VisCal = %s" % (VisCal)
        mytb.close()
        ParType = "unknown"  # i.e. not Complex
        calDesc = mytb.open(caltable+'/CAL_DESC')
        originalSpws = mytb.getcol('SPECTRAL_WINDOW_ID')  # [[0,1,2,3]]
        if debug: print "originalSpws = %s" % (str(originalSpws))
        originalSpw = originalSpws[0]                   # [0,1,2,3]
        if debug: print "originalSpw = %s" % (str(originalSpw))
        msName = mytb.getcol('MS_NAME')[0]
        if debug: print "msName in table = %s" % (msName)
        if (vis != ''):
            msName = vis
        # This appears to be the channel range extracted from the original spw, but is
        # only present in B solutions.  
        if (VisCal == "BPOLY"):
            originalChannelStart = np.zeros(len(originalSpw))
        else:
            originalChannelRange = mytb.getcol('CHAN_RANGE')
            originalChannelStart = originalChannelRange[0][0][:][0]
        mytb.close()
    else:  # 3.4
        tableFormat = 34
        cal_desc_id = mytb.getcol('SPECTRAL_WINDOW_ID')
        ParType = mytb.getkeyword('ParType')    # string = 'Complex'
        msName = mytb.getkeyword('MSName')      
        VisCal = mytb.getkeyword('VisCal')      # string = 'B TSYS'
        PolBasis = mytb.getkeyword('PolBasis')  # string = 'LINEAR'
        spectralWindowTable = mytb.getkeyword('SPECTRAL_WINDOW').split()[1]
        mytb.close()
        mytb.open(spectralWindowTable)
        chanFreqGHz = []
        originalSpws = range(len(mytb.getcol('MEAS_FREQ_REF')))
        originalSpw = originalSpws  # may need to do a global replace of this
        originalSpwNames = mytb.getcol('NAME')
        for i in originalSpws:
            # They array shapes can vary.
            chanFreqGHz.append(1e-9 * mytb.getcell('CHAN_FREQ',i))
        mytb.close()
  
    # Now open the associated ms tables via msmd tool
    msAnt = []
    if (debug): print  "creating msmd tool"
    if (casadef.casa_version < '4.1.0'):
        print "This version of casa is too old to use the msmd tool.  Use au.plotbandpass instead."
        return
    mymsmd = createCasaTool(msmdtool)
    if (debug): print  "msName = %s." % (msName)
    if (os.path.exists(msName) or os.path.exists(os.path.dirname(caltable)+'/'+msName)):
        if (os.path.exists(msName) == False):
            msName = os.path.dirname(caltable)+'/'+msName
            if (debug): print  "found msName = %s." % (msName)
        if (casadef.casa_version < '4.1.0'):
            print "This version of casa is too old to use the msmd tool.  Use au.plotbandpass instead."
            return
        try:
            if (debug): print "Running mymsmd on %s..." % (msName)
            mymsmd.open(msName)
            donetime = timeUtilities.time()
            if (debug): print "%.1f sec elapsed" % (donetime-mytimestamp)
            mytimestamp = timeUtilities.time()
            if (debug): print "time = %s" % (str(mytimestamp))
            msAnt = mymsmd.antennanames(range(mymsmd.nantennas()))
            if (debug): print "msAnt = %s" % (str(msAnt))
#            msFields = mymsmd.namesforfields(range(mymsmd.nfields())) # bombs if split has been run on subset of fields
            msFields = mymsmd.namesforfields()
            casalogPost(debug,"Available antennas = %s" % (str(msAnt)))
        except:
            print "1)Could not open the associated measurement set tables (%s). Will not translate antenna names or frequencies." % (msName)
            return
    else:
        if (vis==''):
            print "Could not find the associated measurement set (%s). Will not translate antenna names or frequencies." % (msName)
        elif (os.path.exists(vis)):
            # Use the ms name passed in from the command line
            msName = vis
# #          print "************* 2) Set msName to %s" % (msName)
            try:
                mymsmd.open(msName)
                donetime = timeUtilities.time()
                if (debug): print "%.1f sec elapsed" % (donetime-mytimestamp)
                mytimestamp = timeUtilities.time()
                msAnt = mymsmd.antennanames(range(mymsmd.nantennas()))
#                msFields = mymsmd.namesforfields(range(mymsmd.nfields())) # bombs if split has been run on subset of fields
                msFields = mymsmd.namesforfields()
                casalogPost(debug,"Available antennas = %s" % (str(msAnt)))
            except:
                print "1b) Could not open the associated measurement set tables (%s). Will not translate antenna names or channels to frequencies." % (msName)
        else:
            print "1b) Could not open the associated measurement set tables (%s). Will not translate antenna names or channels to frequencies." % (msName)
    msFound =  False
    if (len(msAnt) > 0):
          msFound = True
          casalogPost(debug,"Fields in ms  = %s" % (str(msFields)))
    if (tableFormat == 33 and msFound):  # casa 3.3
        # Now open the associated ms tables via ValueMapping to figure out channel freqs
        chanFreqGHz = []
        for ictr in range(len(originalSpw)):
            if debug: print "ictr = %d" % (ictr)
            if debug: print "nspw = %d, np.max(originalSpw) = %d" % (getnspw(mymsmd),np.max(originalSpw))
            if (getnspw(mymsmd) < np.max(originalSpw)): # waiting on CAS-4285
                # Then there was an extra split
                i = ictr
            else:
                i = originalSpw[ictr]
            nchan = mymsmd.nchan(i)
            if (nchan > 1):
                missingFrequencyWidth = originalChannelStart[ictr]*(mymsmd.chanfreqs(i)[-1]-mymsmd.chanfreqs(i)[0])/(nchan-1)
            else:
                missingFrequencyWidth = 0
            if (missingFrequencyWidth > 0):
                if (DEBUG):
                    print "Correcting for channels flagged prior to running bandpass by %f GHz" % (missingFrequencyWidth*1e-9)
            newfreqs = 1e-9*(mymsmd.chanfreqs(i)) + missingFrequencyWidth*1e-9
            if debug: print "Appending onto chanFreqGHz: %s" % (str(newfreqs))
            chanFreqGHz.append(newfreqs)
  
    uniqueSpwsInCalTable = np.unique(cal_desc_id)
    uniqueTimes = sloppyUnique(np.unique(times), solutionTimeThresholdSeconds)
    nUniqueTimes = len(uniqueTimes)
    if (nUniqueTimes == 1):
        casalogPost(debug,"Found solutions with %d unique time within a threshold of %d seconds." % (nUniqueTimes,solutionTimeThresholdSeconds))
    else:
        casalogPost(debug,"Found solutions with %d unique times (within a threshold of %d seconds)." % (nUniqueTimes,solutionTimeThresholdSeconds))
    mystring = ''
    if (debug):
       for u in uniqueTimes:
           mystring += '%.6f, ' % (u)
       print mystring
    uniqueAntennaIds = np.unique(ant)
    uniqueFields = np.unique(fields)
    if (debug): print "uniqueFields = %s" % (str(uniqueFields))
    nFields = len(uniqueFields)
    spwlist = []
    uniqueTimesPerFieldPerSpw = []
    for s in uniqueSpwsInCalTable:
        uniqueTimesPerField = []
        for f in uniqueFields:
            timelist = []
            for row in range(len(fields)):
                if (fields[row] == f and cal_desc_id[row] == s):
                    if (sloppyMatch(times[row], timelist, solutionTimeThresholdSeconds) == False):
                        timelist.append(times[row])
                        spwlist.append(cal_desc_id)
            uniqueTimesPerField.append(timelist)
        uniqueTimesPerFieldPerSpw.append(uniqueTimesPerField)
  
    if (debug): print "about to call casalogPost"
    casalogPost(debug,displayTimesArray([[uniqueTimes]]))
  
    # Parse the spws to plot from the command line
    if (spw==''):
       spwsToPlot = uniqueSpwsInCalTable
    else:
       if (type(spw) == str):
             if (spw.find('!')>=0):
                   print "The ! modifier is not (yet) supported"
                   return()
             tokens = spw.split(',')
             spwsToPlot = []
             for token in tokens:
                   if (len(token) > 0):
                         if (token.find('*')>=0):
                               spwsToPlot = uniqueSpwsInCalTable
                               break
                         elif (token.find('~')>0):
                               (start,finish) = token.split('~')
                               spwsToPlot +=  range(int(start),int(finish)+1)
                         else:
                               spwsToPlot.append(int(token))
       elif (type(spw) == list):
           spwsToPlot = np.sort(spw)
       else:
           spwsToPlot = [spw]
           
    casalogPost(debug,"%d spw%s in the solution = %s" % (len(uniqueSpwsInCalTable), plural(uniqueSpwsInCalTable), str(uniqueSpwsInCalTable)))
    for myspw in spwsToPlot:
        if (myspw not in uniqueSpwsInCalTable):
            print "spw %d is not in the solution" % (myspw)
            return
        
    casalogPost(debug,"%d field%s in the solution = %s" % (len(uniqueFields), plural(uniqueFields), str(uniqueFields)))
    
    # Figure out which kind of Bandpass solution this is.
    bOverlay = False  # Am I trying to overlay a second B-type solution?
    if (os.path.exists(caltable) == False):
          print "Caltable does not exist = %s" % (caltable)
          return()
    try:
        ([polyMode, polyType, nPolyAmp, nPolyPhase, scaleFactor, nRows, nSpws, nUniqueTimesBP, uniqueTimesBP,
# #        nPolarizations,
          frequencyLimits, increments, frequenciesGHz, polynomialPhase,
          polynomialAmplitude, timesBP, antennasBP, cal_desc_idBP, spwBP]) = openBpolyFile(caltable,debug)
        bpoly = True
        bpolyOverlay = bpolyOverlay2 = False
        if (xaxis.find('chan') >= 0):
            print "Sorry, but BPOLY solutions cannot be plotted with xaxis='chan'. Proceeding with xaxis='freq'."
            xaxis = 'freq'
        if (chanrange[0] != 0 or chanrange[1] != 0):
            print "The chanrange parameter only applies if the first caltable is a B solution, not a BPOLY."
            return()
        if (len(caltable2) > 0):
            try:
                # figure out if the next file is a BPOLY or another B solution to pick the proper error message.
                ([polyMode, polyType, nPolyAmp, nPolyPhase, scaleFactor, nRows, nSpws, nUniqueTimesBP, uniqueTimesBP,
# #                nPolarizations,
                  frequencyLimits, increments, frequenciesGHz, polynomialPhase,
                  polynomialAmplitude, timesBP, antennasBP, cal_desc_idBP, spwBP]) = openBpolyFile(caltable2,debug)
                print "Sorry, but you cannot overlay two BPOLY solutions (unless caltable is a B solution and caltable2 and 3 are BPOLYs)."
            except:
                print "Sorry, but for overlays, caltable must be a B solution, whlie caltable2 and 3 can be either type."
            return()
    except:
        casalogPost(debug,"This is a %s solution." % (VisCal))
        bpoly = bpolyOverlay = bpolyOverlay2 = False
  
        # Now check if there is a second file to overlay
        if (len(caltable2) > 0):
          if (os.path.exists(caltable2) == False):
                print "Caltable2 does not exist = %s" % (caltable2)
                return()
          try:
            # figure out if the next file is a BPOLY or another B solution
            ([polyMode, polyType, nPolyAmp, nPolyPhase, scaleFactor, nRows, nSpws, nUniqueTimesBP, uniqueTimesBP,
# #            nPolarizations,
              frequencyLimits, increments, frequenciesGHz, polynomialPhase,
              polynomialAmplitude, timesBP, antennasBP, cal_desc_idBP, spwBP]) = openBpolyFile(caltable2,debug)
            bpolyOverlay = True
            casalogPost(debug,"Overlay the BPOLY solution")
            if (xaxis.find('chan')>=0):
                print "Sorry, but overlap of BPOLY is currently possible only with xaxis='freq'"
                return()
            if (len(caltable3) > 0):
               if (os.path.exists(caltable3) == False):
                     print "Caltable3 does not exist = %s" % (caltable3)
                     return()
               bpolyOverlay2 = True
               casalogPost(debug,"Overlay the second BPOLY solution")
               ([polyMode2, polyType2, nPolyAmp2, nPolyPhase2, scaleFactor2, nRows2, nSpws2,
                 nUniqueTimesBP2, uniqueTimesBP2,
# #               nPolarizations2,
                 frequencyLimits2, increments2, frequenciesGHz2, polynomialPhase2,
                 polynomialAmplitude2, timesBP2, antennasBP2, cal_desc_idBP2, spwBP2]) = openBpolyFile(caltable3,debug)
          except:
              # this is another B solution
              casalogPost(debug,"Overlay another %s solution" % (VisCal))
              bOverlay = True
              if (xaxis.find('freq')<0):
                    print "Currently, you must use xaxis='freq' to overlay two B solutions."
                    return()
              if (len(caltable3) > 0):
                    print "You cannot overlay caltable3 because caltable2 is a B solution."
                    return()
        elif (len(caltable3) > 0):
            print "You cannot have a caltable3 argument without a caltable2 argument."
            return()
            
    if (overlay.find('antenna')>=0):
        overlayAntennas = True
        if (bpoly == True):
              print "The overlay of times or antennas is not supported with BPOLY solutions"
              return()
        if (len(caltable2)>0):
              print "The overlay of times or antennas not supported when overlaying a B or BPOLY solution"
              return()
        casalogPost(debug,"Will overlay solutions from different antennas")
    else:
        overlayAntennas = False
  
    if (overlay.find('time')>=0):
        overlayTimes = True
        if (bpoly == True):
              print "The overlay of times or antennas is not supported with BPOLY solutions"
              return()
        if (len(caltable2)>0):
              print "The overlay of times or antennas not supported when overlaying a B or BPOLY solution"
              return()
        casalogPost(debug,"Will overlay solutions from different times")
    else:
        overlayTimes = False
        
    if (bOverlay):        
          # Now open the Bandpass solution table
          try:
                mytb.open(caltable2)
          except:
                print "Could not open the second caltable = %s" % (caltable2)
                return()
          names = mytb.colnames()
          ant2 = mytb.getcol('ANTENNA1')
          fields2 = mytb.getcol('FIELD_ID')
          times2 = mytb.getcol('TIME')
          if ('SPECTRAL_WINDOW_ID' not in names):
              if ('SNR' not in names):
                  print "This does not appear to be a cal table."
                  return()
              else:
                  tableFormat2 = 33
                  casalogPost(debug,"This appears to be an old-format cal table from casa 3.3 or earlier.")
                  cal_desc_id2 = mytb.getcol('CAL_DESC_ID')
                  VisCal2 = (mytb.info())['subType']
                  mytb.close()
                  ParType = "unknown"  # i.e. not Complex
                  calDesc2 = mytb.open(caltable2+'/CAL_DESC')
                  originalSpws2 = mytb.getcol('SPECTRAL_WINDOW_ID')  # [[0,1,2,3]]
                  originalSpw2 = originalSpws2[0]                   # [0,1,2,3]
                  msName2 = mytb.getcol('MS_NAME')[0]
                  mytb.close()
                  # Now open the associated ms tables via ValueMapping to figure out channel freqs
                  chanFreqGHz2 = []
                  for ictr in range(len(originalSpw2)):
                      if debug: print "ictr = %d" % (ictr)
                      if debug: print "nspw = %d, np.max(originalSpw) = %d" % (getnspw(mymsmd),np.max(originalSpw2))
                      if (getnspw(mymsmd) < np.max(originalSpw2)):
                          # Then there was an extra split
                          i = ictr
                      else:
                          i = originalSpw2[ictr]
                      nchan = mymsmd.nchan(i)
                      if (nchan > 1):
                          missingFrequencyWidth = originalChannelStart[ictr]*(mymsmd.chanfreqs(i)[-1]-mymsmd.chanfreqs(i)[0])/(nchan-1)
                      else:
                          missingFrequencyWidth = 0
                      if (missingFrequencyWidth > 0):
                          if (DEBUG):
                              print "Correcting for channels flagged prior to running bandpass by %f GHz" % (missingFrequencyWidth*1e-9)
                      newfreqs = 1e-9*(mymsmd.chanfreqs(i)) + missingFrequencyWidth*1e-9
                      if debug: print "Appending onto chanFreqGHz: %s" % (str(newfreqs))
                      chanFreqGHz2.append(newfreqs)
          else:
              tableFormat2 = 34
              cal_desc_id2 = mytb.getcol('SPECTRAL_WINDOW_ID')
              msName2 = mytb.getkeyword('MSName')      
              ParType2 = mytb.getkeyword('ParType')    # string = 'Complex'
              VisCal2 = mytb.getkeyword('VisCal')      # string = 'B TSYS'
              PolBasis2 = mytb.getkeyword('PolBasis')  # string = 'LINEAR'
              spectralWindowTable2 = mytb.getkeyword('SPECTRAL_WINDOW').split()[1]
              mytb.close()
              mytb.open(spectralWindowTable2)
              chanFreqGHz2 = []
              originalSpws2 = range(len(mytb.getcol('MEAS_FREQ_REF')))
              for i in originalSpws2:
                  # The array shapes can vary.
                  chanFreqGHz2.append(1e-9 * mytb.getcell('CHAN_FREQ',i))
              originalSpws2 = range(len(mytb.getcol('MEAS_FREQ_REF')))
              originalSpw2 = originalSpws2  # may want to do a global replace of this <----------------------------------
  
          uniqueSpwsInCalTable2 = np.unique(cal_desc_id2)
          mytb.open(caltable2)
          try:
              flags2 = {}
              for f in range(len(fields2)):
                  flags2[f] = mytb.getcell('FLAG',f)
          except:
              print "bOverlay: No Flag column found. Are you sure this is a bandpass solution file, or is it the .ms?"
              print "If it is a solution file, does it contain solutions for both TDM and FDM spws?"
              return()
          uniqueTimes2 = sloppyUnique(np.unique(times2), solutionTimeThresholdSeconds)
          nUniqueTimes2 = len(uniqueTimes2)
# #        print "Found %d solutions in time: MJD seconds = " % (nUniqueTimes2), uniqueTimes2
          spacing = ''
          for i in range(1,nUniqueTimes2):
              spacing += '%.0f, ' % (np.abs(uniqueTimes2[i]-uniqueTimes2[i-1]))
          casalogPost(debug,"Found %d solutions in time, spaced by seconds: %s" % (nUniqueTimes2, str(spacing)))
          casalogPost(debug,displayTimesArray([[uniqueTimes2]]))
          uniqueAntennaIds2 = np.unique(ant2)
          uniqueFields2 = np.unique(fields2)
          nFields2 = len(uniqueFields2)
  
          casalogPost(debug,"(boverlay) original unique spws in the second dataset = %s" % (str(np.unique(originalSpw2))))
  
          uniqueTimesPerFieldPerSpw2 = []
          for s in uniqueSpwsInCalTable2:
            uniqueTimesPerField2 = []
            for f in uniqueFields2:
                timelist2 = []
                for row in range(len(fields2)):
                      if (fields2[row] == f and cal_desc_id2[row] == s):
                            if (sloppyMatch(times2[row], timelist2, solutionTimeThresholdSeconds) == False):
                                  timelist2.append(times2[row])
                uniqueTimesPerField2.append(timelist2)
            uniqueTimesPerFieldPerSpw2.append(uniqueTimesPerField2)
          casalogPost(debug,"uniqueTimesPerFieldPerSpw2 = %s" % (displayTimesArray(uniqueTimesPerFieldPerSpw2)))
          casalogPost(debug,"%d spw%s in the second solution = %s" % (len(uniqueSpwsInCalTable2), plural(uniqueSpwsInCalTable2), str(uniqueSpwsInCalTable2)))
          casalogPost(debug,"%d field%s in the solution = %s" % (len(uniqueFields2), plural(uniqueFields2), str(uniqueFields2)))
  
    # Parse the timeranges field from the command line
    if (type(timeranges) == str):
        # a list of antenna numbers was given
        tokens = timeranges.split(',')
        timerangeList = []
        removeTime = []
        for token in tokens:
            if (len(token) > 0):
                if (token.find('!')==0):
                    timerangeList = range(len(uniqueTimes))
                    removeTime.append(int(token[1:]))
                elif (token.find('~')>0):
                    (start,finish) = token.split('~')
                    timerangeList +=  range(int(start),int(finish)+1)
                else:
                    timerangeList.append(int(token))
        timerangeList = np.array(timerangeList)
        for rt in removeTime:
            timerangeList = timerangeList[np.where(timerangeList != rt)[0]]
        timerangeList = list(timerangeList)
        if (len(timerangeList) < 1):
            if (len(removeTime) > 0):
                print "Too many negated timeranges -- there are none left to plot."
                return
            else:
                # then a blank list was specified
                timerangeList = range(len(uniqueTimes))
    elif (type(timeranges) == list):
        # it's already a list of integers
        timerangeList = timeranges
    else:
        # It's a single, integer entry
        timerangeList = [timeranges]
  
    timerangeListTimes = np.array(uniqueTimes)[timerangeList]
    timerangeListTimesString = mjdsecArrayToUTString(timerangeListTimes)
    casalogPost(debug,"UT times to plot: %s" % (timerangeListTimesString))
    casalogPost(debug,"Corresponding time IDs (0-based): %s" % (str(timerangeList)))
  
    # Check for mismatch
    if (bpolyOverlay):
        if (len(timerangeListTimes) > nUniqueTimesBP):
            print "There are more timeranges (%d) to plot from %s than exist in the caltable2=%s (%d)" % (len(timerangeListTimes), caltable,caltable2, nUniqueTimesBP)
            for i in timerangeList:
                if (sloppyMatch(timerangeListTimes[i],uniqueTimesBP[0],
                                solutionTimeThresholdSeconds)):
                    print "Try adding 'timeranges=%d'" % (i+1)
            return()
        if (bpolyOverlay2):
            if (len(timerangeListTimes) > nUniqueTimesBP2):
                print "There are more timeranges to plot (%d) from %s than exist in the caltable3=%s (%d)" % (len(timerangeListTimes), caltable, caltable3, nUniqueTimesBP2)
                return()
            
    # Parse the antenna string to emulate plotms
    if (type(antenna) == str):
       if (len(antenna) == sum([m in myValidCharacterListWithBang for m in antenna])):
           # a simple list of antenna numbers was given 
           tokens = antenna.split(',')
           antlist = []
           removeAntenna = []
           for token in tokens:
               if (len(token) > 0):
                   if (token.find('*')==0 and len(token)==1):
                       antlist = uniqueAntennaIds
                       break
                   elif (token.find('!')==0):
                       antlist = uniqueAntennaIds
                       removeAntenna.append(int(token[1:]))
                   elif (token.find('~')>0):
                       (start,finish) = token.split('~')
                       antlist +=  range(int(start),int(finish)+1)
                   else:
                       antlist.append(int(token))
           antlist = np.array(antlist)
           for rm in removeAntenna:
               antlist = antlist[np.where(antlist != rm)[0]]
           antlist = list(antlist)
           if (len(antlist) < 1 and len(removeAntenna)>0):
               print "Too many negated antennas -- there are no antennas left to plot."
               return()
       else:
           # The antenna name (or list of names) was specified
           tokens = antenna.split(',')
           if (msFound):
               antlist = []
               removeAntenna = []
               for token in tokens:
                   if (token in mymsmd.antennanames(range(mymsmd.nantennas()))):
                       antlist = list(antlist)  # needed in case preceding antenna had ! modifier
                       antlist.append(mymsmd.antennaids(token)[0])
                   elif (token[0] == '!'):
                       if (token[1:] in mymsmd.antennanames(range(mymsmd.nantennas()))):
                           antlist = range(mymsmd.nantennas())
                           removeAntenna.append(mymsmd.antennaids(token[1:])[0])
                       else:
                           print "Antenna %s is not in the ms. It contains: %s" % (token, str(range(mymsmd.nantennas())))
                           return()
                   else:
                       print "Antenna %s is not in the ms. It contains: %s" % (token, str(range(mymsmd.nantennas())))
                       return()
               antlist = np.array(antlist)
               for rm in removeAntenna:
                   antlist = antlist[np.where(antlist != rm)[0]]
               antlist = list(antlist)
               if (len(antlist) < 1 and len(removeAntenna)>0):
                   print "Too many negated antennas -- there are no antennas left to plot."
                   return()
           else:
               print "Antennas cannot be specified my name if the ms is not found."
               return()
    elif (type(antenna) == list):
        # it's a list of integers
        antlist = antenna
    else:
        # It's a single, integer entry
        antlist = [antenna]
    casalogPost(debug,"antlist = %s" % (str(antlist)))
    if (len(antlist) > 0):
       antennasToPlot = np.intersect1d(uniqueAntennaIds,antlist)
    else:
       antennasToPlot = uniqueAntennaIds
    if (len(antennasToPlot) < 2 and overlayAntennas):
        print "More than 1 antenna is required for overlay='antenna'."
        return()
    casalogPost(debug,"antennasToPlot = %s" % (str(antennasToPlot)))
  
    # Parse the field string to emulate plotms
    removeField = []
    if (type(field) == str):
       if (len(field) == sum([m in myValidCharacterListWithBang for m in field])):
           casalogPost(debug,"a list of field numbers was given")
           # a list of field numbers was given
           tokens = field.split(',')
           fieldlist = []
           for token in tokens:
               if (token.find('*')>=0):
                   fieldlist = uniqueFields
                   break
               elif (token.find('!')==0):
                   fieldlist = uniqueFields
                   removeField.append(int(token[1:]))
               elif (len(token) > 0):
                   if (token.find('~')>0):
                       (start,finish) = token.split('~')
                       fieldlist +=  range(int(start),int(finish)+1)
                   else:
                       fieldlist.append(int(token))
           fieldlist = np.array(fieldlist)
           for rm in removeField:
               fieldlist = fieldlist[np.where(fieldlist != rm)[0]]
           fieldlist = list(fieldlist)
           if (len(fieldlist) < 1 and len(removeField)>0):
               print "Too many negated fields -- there are no fields left to plot."
               return()
       else:
           casalogPost(debug,"The field name, or list of names was given")
           # The field name (or list of names, or wildcard) was specified
           tokens = field.split(',')
           if (msFound):
               fieldlist = []
               removeField = []
               for token in tokens:
                   myloc = token.find('*')
                   casalogPost(debug,"token=%s, myloc=%d" % (token,myloc))
                   if (myloc > 0):
                       casalogPost(debug,"Saw wildcard in the name")
                       for u in uniqueFields:
                           if (token[0:myloc]==mymsmd.namesforfields(u)[0:myloc]):
                               if (DEBUG):
                                   print "Found wildcard match = %s" % mymsmd.namesforfields(u)
                               fieldlist.append(u)
                           else:
                               if (DEBUG):
                                   print "No wildcard match with = %s" % mymsmd.namesforfields(u)
                   elif (myloc==0):
                       casalogPost(debug,"Saw wildcard at start of name")
                       for u in uniqueFields:
                           fieldlist.append(u)
                   elif (token in mymsmd.namesforfields()):
                       fieldlist = list(fieldlist)  # needed in case preceding field had ! modifier
                       fieldlist.append(mymsmd.fieldsforname(token))
                   elif (token[0] == '!'):
                       if (token[1:] in range(mymsmd.nfields())):
                           fieldlist = range(mymsmd.nfields())
                           removeField.append(mymsmd.fieldsforname(token[1:]))
                       else:
                           print "Field %s is not in the ms. It contains: %s" % (token, str(range(mymsmd.nfields())))
                           return()
                   else:
                       casalogPost(debug,"Field not in ms")
                       print "Field %s is not in the ms. It contains: %s" % (token, str(range(mymsmd.nfields())))
                       return()
               fieldlist = np.array(fieldlist)
               for rm in removeField:
                   fieldlist = fieldlist[np.where(fieldlist != rm)[0]]
               fieldlist = list(fieldlist)
               if (len(fieldlist) < 1 and len(removeField)>0):
                   print "Too many negated fields -- there are no fields left to plot."
                   return()
           else:
               print "Fields cannot be specified my name if the ms is not found."
               return()
    elif (type(field) == list):
        # it's a list of integers
        fieldlist = field
    else:
        # It's a single, integer entry
        fieldlist = [field]
  
    casalogPost(debug,"fieldlist = %s" % (str(fieldlist)))

    if (len(fieldlist) > 0):
        if (DEBUG):
            print "Finding intersection of %s with %s" % (str(uniqueFields), str(fieldlist))
        fieldsToPlot = np.intersect1d(uniqueFields,np.array(fieldlist))
        if (bOverlay):
            fieldsToPlot = np.intersect1d(np.union1d(uniqueFields,uniqueFields2),np.array(fieldlist))
        if (len(fieldsToPlot) < 1):
            print "Requested field not found in solution"
            return()
    else:
        fieldsToPlot = uniqueFields  # use all fields if none are specified
        if (bOverlay):
            fieldsToPlot = np.union1d(uniqueFields,uniqueFields2)
        if (DEBUG):
            print "bOverlay = %s" % (bOverlay)
            print "set fieldsToPlot to uniqueFields = %s" % (str(fieldsToPlot))
    fieldIndicesToPlot = []
    casalogPost(debug,"fieldsToPlot = %s" % (str(fieldsToPlot)))
  
    if (showatmfield == ''):
        showatmfield = fieldsToPlot[0]
    else:
        if (str.isdigit(str(showatmfield))):
            showatmfield = int(str(showatmfield))
            if (showatmfield not in fieldsToPlot):
                print "The showatmfield (%d) is not in the list of fields to plot: %s" % (showatmfield, str(fieldsToPlot))
                return()
        else:
            showatmfieldName = showatmfield
            showatmfield = mymsmd.fieldsforname(showatmfield)
            if (list(showatmfield) == []):
                print "The showatmfield (%s) is not in the ms." %(showatmfieldName)
                return()
            if (type(showatmfield) == type(np.ndarray(0))):
                # more than one field IDs exist for this source name, so pick the first
                showatmfield = showatmfield[0]
            if (showatmfield not in fieldsToPlot):
                print "The showatmfield (%d=%s) is not in the list of fields to plot: %s" % (showatmfield, showatmfieldName, str(fieldsToPlot))
                return()
  
    for i in fieldsToPlot:
        match = np.where(i==uniqueFields)[0]
        if (len(match) < 1 and bOverlay):
            match = np.where(i==uniqueFields2)[0]
        fieldIndicesToPlot.append(match[0])
        
    if (overlayTimes and len(fieldsToPlot)>1 and 1==0):
          print "Times cannot be overlaid if more than one field is specified"
          return()
#    if (overlayTimes and len(fieldsToPlot)>1):
#        multiFieldsWithOverlayTime = True
#    else:
#        multiFieldsWithOverlayTime = False
  
# #  print "Antennas to plot = ", antennasToPlot
    casalogPost(debug,"spws to plot = %s" % (str(spwsToPlot)))
    casalogPost(debug,"Field IDs to plot: %s" % (str(fieldsToPlot)))
# #  print "Field indices to plot: ", fieldIndicesToPlot
  
    redisplay = False
    myap = 0  # this variable is necessary to make the 'b' option work for 
              # subplot=11, yaxis=both.  It keeps track of whether 'amp' or 
              # 'phase' was the first plot on the page.
  
    # I added pb.ion() because Remy suggested it.
    if (interactive):
        pb.ion()  # This will open a new window if not present.
    else:
        pb.ioff() # This will not destroy an existing window or prevent new plots from appearing there.
# # The call to pb.figure() causes an additional new window everytime.
# #  pb.figure()
  
    newylimits = [LARGE_POSITIVE, LARGE_NEGATIVE]
    
    pb.clf()
    if (bpoly):
      # The number of polarizations cannot be reliably inferred from the shape of
      # the GAIN column in the caltable.  Must use the shape of the DATA column 
      # in the ms.
      if (debug): print "in bpoly"
      if (msFound):
          (corr_type, corr_type_string, nPolarizations) = getCorrType(msName, spwsToPlot, mymsmd, debug)
          casalogPost(debug,"nPolarizations in first spw to plot = %s" % (str(nPolarizations)))
      else:
          print "With no ms available, I will assume ALMA data: XX, YY, and refFreq=first channel."
#          chanFreqGHz = []
          corr_type_string = ['XX','YY']
          corr_type = [9,12]
          nPolarizations = 2
      nPolarizations2 = nPolarizations
      if (corr_type_string == []):
          return()
      polsToPlot = checkPolsToPlot(polsToPlot, corr_type_string, debug)
      if (polsToPlot == []):
          return()
      # Here we are only plotting one BPOLY solution, no overlays implemented.
      overlayAntennas = False
      # rows in the table are: antennas 0..nAnt for first spw, antennas 0..nAnt 
      # for 2nd spw...
      pagectr = 0
      pages = []
      xctr = 0
      newpage = 1
      while (xctr < len(antennasToPlot)):
        xant = antennasToPlot[xctr]
        antstring, Antstring = buildAntString(xant,msFound,msAnt)
        spwctr = 0
        while (spwctr < len(spwsToPlot)):
         ispw = spwsToPlot[spwctr]
         mytime = 0
         while (mytime < nUniqueTimes):
           if (len(uniqueTimes) > 0 and (sloppyMatch(mytime,timerangeList,solutionTimeThresholdSeconds,myprint=debugSloppyMatch)==False)):
               if (debug):
                   print "@@@@@@@@@@@@@@@  Skipping mytime=%d" % (mytime)
               mytime += 1
               continue
           if (newpage == 1):
              pages.append([xctr,spwctr,mytime,0])
#              print "appending [%d,%d,%d,%d]" % (xctr,spwctr,mytime,0)
              newpage = 0
           antennaString = 'Ant%2d: %s,  ' % (xant,antstring)
           for index in range(nRows):
              # Find this antenna, spw, and timerange combination in the table
              if (xant==ant[index] and sloppyMatch(uniqueTimes[mytime],times[index],solutionTimeThresholdSeconds,myprint=debugSloppyMatch) and
                  (ispw == cal_desc_id[index]) and (fields[index] in fieldsToPlot)):
                  fieldIndex = np.where(fields[index] == uniqueFields)[0]
                  validDomain = [frequencyLimits[0,index], frequencyLimits[1,index]]
                  if (msFound):
                      fieldString = msFields[uniqueFields[fieldIndex]]
                  else:
                      fieldString = str(field)
                  timeString = ',  t%d/%d  %s' % (mytime,nUniqueTimes-1,utstring(uniqueTimes[mytime],3))
                  if ((yaxis.find('amp')>=0 or amplitudeWithPhase) and myap==0):
                    xframe += 1
                    myUniqueColor = []
                    if (debug):
                        print "v) incrementing xframe to %d" % xframe
                    adesc = pb.subplot(xframe)
                    if (ispw==originalSpw[ispw]):
                        # all this was added mistakenly here.  If it causes a bug, remove it.
                        if (overlayTimes and len(fieldsToPlot) > 1):
                          indices = fstring = ''
                          for f in fieldIndicesToPlot:
                              if (f != fieldIndicesToPlot[0]):
                                  indices += ','
                                  fstring += ','
                              indices += str(uniqueFields[f])
                              if (msFound):
                                  fstring += msFields[uniqueFields[f]]
                          if (len(fstring) > fstringLimit):
                              fstring = fstring[0:fstringLimit] + '...'
                          pb.title("%sspw%d,  fields %s: %s%s" % (antennaString,ispw,
                                  indices, fstring, timeString), size=titlesize)
                        else:
                          pb.title("%sspw%d,  field %d: %s%s" % (antennaString,ispw,
                                  uniqueFields[fieldIndex],fieldString,timeString), size=titlesize)
                    else:
                        if (overlayTimes and len(fieldsToPlot) > 1):
                          indices = fstring = ''
                          for f in fieldIndicesToPlot:
                              if (f != fieldIndicesToPlot[0]):
                                  indices += ','
                                  fstring += ','
                              indices += str(uniqueFields[f])
                              if (msFound):
                                  fstring += msFields[uniqueFields[f]]
                          if (len(fstring) > fstringLimit):
                              fstring = fstring[0:fstringLimit] + '...'
                          pb.title("%sspw%d (%d),  fields %s: %s%s" % (antennaString,ispw,originalSpw[ispw],
                                  indices, fstring, timeString), size=titlesize)
                        else:
                          pb.title("%sspw%d (%d),  field %d: %s%s" % (antennaString,ispw,originalSpw[ispw],
                                  uniqueFields[fieldIndex],fieldString,timeString), size=titlesize)
                    amplitudeSolutionX = np.real(scaleFactor[index])+calcChebyshev(polynomialAmplitude[index][0:nPolyAmp[index]], validDomain, frequenciesGHz[index]*1e+9)
                    amplitudeSolutionY = np.real(scaleFactor[index])+calcChebyshev(polynomialAmplitude[index][nPolyAmp[index]:2*nPolyAmp[index]], validDomain, frequenciesGHz[index]*1e+9)
                    amplitudeSolutionX += 1 - np.mean(amplitudeSolutionX)
                    amplitudeSolutionY += 1 - np.mean(amplitudeSolutionY)
                    if (yaxis.lower().find('db') >= 0):
                        amplitudeSolutionX = 10*np.log10(amplitudeSolutionX)
                        amplitudeSolutionY = 10*np.log10(amplitudeSolutionY)
                    if (nPolarizations == 1):
                        pb.plot(frequenciesGHz[index], amplitudeSolutionX, '%s%s'%(xcolor,bpolymarkstyle))
                    else:
                        pb.plot(frequenciesGHz[index], amplitudeSolutionX, '%s%s'%(xcolor,bpolymarkstyle), frequenciesGHz[index], amplitudeSolutionY, '%s%s'%(ycolor,bpolymarkstyle))
                    if (plotrange[0] != 0 or plotrange[1] != 0):
                        SetNewXLimits([plotrange[0],plotrange[1]])
                    if (plotrange[2] != 0 or plotrange[3] != 0):
                        SetNewYLimits([plotrange[2],plotrange[3]])
                    xlim=pb.xlim()
                    ylim=pb.ylim()
                    ResizeFonts(adesc,mysize)
                    adesc.xaxis.grid(True,which='major')
                    adesc.yaxis.grid(True,which='major')
                    if (yaxis.lower().find('db')>=0):
                        pb.ylabel('Amplitude (dB)', size=mysize)
                    else:
                        pb.ylabel('Amplitude', size=mysize)
                    pb.xlabel('Frequency (GHz)', size=mysize)
                    if (xframe == firstFrame):
                        DrawBottomLegendPageCoords(msName, uniqueTimes[mytime], mysize)
                        pb.text(xstartTitle, ystartTitle,
                                '%s (degamp=%d, degphase=%d)'%(caltableTitle,nPolyAmp[index]-1,
                                nPolyPhase[index]-1),size=mysize,
                                transform=pb.gcf().transFigure) 
                    # draw polarization labels
                    x0 = xstartPolLabel
                    y0 = ystartPolLabel
                    for p in range(nPolarizations):
                        if (corrTypeToString(corr_type[p]) in polsToPlot):
                            pb.text(x0, y0-0.03*subplotRows*p, corrTypeToString(corr_type[p])+'',
                                    color=pcolor[p],size=mysize, transform=pb.gca().transAxes)
                    if (xframe == 111 and amplitudeWithPhase):
                       if (len(figfile) > 0):
                           # We need to make a new figure page
                           plotfiles.append(makeplot(figfile,msFound,msAnt,
                                            overlayAntennas,pages,pagectr,
                                            density,interactive,antennasToPlot,
                                            spwsToPlot,overlayTimes,0,debug))
                       donetime = timeUtilities.time()
                       if (interactive):
                          pb.draw()
# #                        myinput = raw_input("(%.1f sec) Press return for next page (b for backwards, q to quit): "%(donetime-mytimestamp))
                          myinput = raw_input("Press return for next page (b for backwards, q to quit): ")
                       else:
                          myinput = ''
                       skippingSpwMessageSent = 0
                       mytimestamp = timeUtilities.time()
                       if (myinput.find('q') >= 0):
                           return()
                       if (myinput.find('b') >= 0):
                           if (pagectr > 0):
                               pagectr -= 1
                           #redisplay the current page by setting ctrs back to the value they had at start of that page
                           xctr = pages[pagectr][PAGE_ANT]
                           spwctr = pages[pagectr][PAGE_SPW]
                           mytime = pages[pagectr][PAGE_TIME]
                           myap = pages[pagectr][PAGE_AP]
                           xant = antennasToPlot[xctr]
                           antstring, Antstring = buildAntString(xant,msFound,msAnt)
                           ispw = spwsToPlot[spwctr]
                           redisplay = True
                       else:
                           pagectr += 1
                           if (pagectr >= len(pages)):
                                 pages.append([xctr,spwctr,mytime,1])
#                                 print "appending [%d,%d,%d,%d]" % (xctr,spwctr,mytime,1)
                                 newpage = 0
                       pb.clf()
  
                  if (yaxis.find('phase')>=0 or amplitudeWithPhase):
                    xframe += 1
                    myUniqueColor = []
# #                  print "w) incrementing xframe to %d" % xframe
                    adesc = pb.subplot(xframe)
                    if (ispw==originalSpw[ispw]):
                          pb.title("%sspw%d,  field %d: %s%s" % (antennaString,ispw,
                                 uniqueFields[fieldIndex],fieldString,timeString), size=titlesize)
                    else:
                          pb.title("%sspw%d (%d),  field %d: %s%s" % (antennaString,ispw,originalSpw[ispw],
                                 uniqueFields[fieldIndex],fieldString,timeString), size=titlesize)
                    phaseSolutionX = calcChebyshev(polynomialPhase[index][0:nPolyPhase[index]], validDomain, frequenciesGHz[index]*1e+9) * 180/math.pi
                    phaseSolutionY = calcChebyshev(polynomialPhase[index][nPolyPhase[index]:2*nPolyPhase[index]], validDomain, frequenciesGHz[index]*1e+9) * 180/math.pi
                    if (nPolarizations == 1):
                        pb.plot(frequenciesGHz[index], phaseSolutionX, '%s%s'%(xcolor,bpolymarkstyle))
                    else:
                        pb.plot(frequenciesGHz[index], phaseSolutionX, '%s%s'%(xcolor,bpolymarkstyle), frequenciesGHz[index], phaseSolutionY, '%s%s'%(ycolor,bpolymarkstyle))
                    ResizeFonts(adesc,mysize)
                    adesc.xaxis.grid(True,which='major')
                    adesc.yaxis.grid(True,which='major')
                    pb.ylabel('Phase (deg)', size=mysize)
                    pb.xlabel('Frequency (GHz)', size=mysize)
                    if (plotrange[0] != 0 or plotrange[1] != 0):
                        SetNewXLimits([plotrange[0],plotrange[1]])
                    if (plotrange[2] != 0 or plotrange[3] != 0):
                        SetNewYLimits([plotrange[2],plotrange[3]])
                    if (amplitudeWithPhase and phase != ''):
                        if (phase[0] != 0 or phase[1] != 0):
                            SetNewYLimits(phase)
                    if (xframe == firstFrame):
                        pb.text(xstartTitle, ystartTitle,
                                '%s (degamp=%d, degphase=%d)'%(caltable,
                                nPolyAmp[index]-1,nPolyPhase[index]-1),
                                size=mysize, transform=pb.gcf().transFigure)
                    # draw polarization labels
                    x0 = xstartPolLabel
                    y0 = ystartPolLabel
                    for p in range(nPolarizations):
                        if (corrTypeToString(corr_type[p]) in polsToPlot):
                            pb.text(x0, y0-0.03*p*subplotRows, corrTypeToString(corr_type[p])+'',
                                    color=pcolor[p],size=mysize, transform=pb.gca().transAxes)
                        
           # end of 'for' loop over rows
           redisplay = False
           pb.subplots_adjust(hspace=myhspace, wspace=mywspace)
           if (xframe == lastFrame):
              if (len(figfile) > 0):
                  plotfiles.append(makeplot(figfile,msFound,msAnt,
                                    overlayAntennas,pages,pagectr,
                                    density,interactive,antennasToPlot,
                                    spwsToPlot,overlayTimes,1,debug))
              donetime = timeUtilities.time()
              if (interactive):
                 pb.draw()
# #               myinput = raw_input("(%.1f sec) Press return for next page (b for backwards, q to quit): "%(donetime-mytimestamp))
                 myinput = raw_input("Press return for next page (b for backwards, q to quit): ")
              else:
                 myinput = ''
              skippingSpwMessageSent = 0
              mytimestamp = timeUtilities.time()
              if (myinput.find('q') >= 0):
                  return()
              if (myinput.find('b') >= 0):
                  if (pagectr > 0):
                      pagectr -= 1
                  #redisplay the current page by setting ctrs back to the value they had at start of that page
                  xctr = pages[pagectr][PAGE_ANT]
                  spwctr = pages[pagectr][PAGE_SPW]
                  mytime = pages[pagectr][PAGE_TIME]
                  myap = pages[pagectr][PAGE_AP]
                  xant = antennasToPlot[xctr]
                  antstring, Antstring = buildAntString(xant,msFound,msAnt)
                  ispw = spwsToPlot[spwctr]
                  redisplay = True
              else:
                  pagectr += 1
                  if (pagectr >= len(pages)):
                      newpage = 1
                  else:
                      newpage = 0
              if (debug):
                  print "1)Setting xframe to %d" % xframeStart
              xframe = xframeStart
              if (xctr+1 < len(antennasToPlot)):
                  # don't clear the final plot when finished
                  pb.clf()
              if (spwctr+1<len(spwsToPlot) or mytime+1<nUniqueTimes):
                  # don't clear the final plot when finished
                  pb.clf()
              pb.subplots_adjust(hspace=myhspace, wspace=mywspace)
           if (redisplay == False):
               mytime += 1
               if (debug):
                   print "Incrementing mytime to %d" % (mytime)
         # end while(mytime)
         if (redisplay == False):
             spwctr +=1
             if (debug):
                 print "Incrementing spwctr to %d" % (spwctr)
        # end while(spwctr)
        if (redisplay == False):
            xctr += 1
      # end while(xctr)
      if (len(figfile) > 0 and pagectr<len(pages)):
         plotfiles.append(makeplot(figfile,msFound,msAnt,overlayAntennas,pages,
                                   pagectr,density,interactive,antennasToPlot,
                                   spwsToPlot,overlayTimes,2,debug))
      if (len(plotfiles) > 0 and buildpdf):
          pdfname = figfile+'.pdf'
          filelist = ''
          plotfiles = np.unique(plotfiles)
          for i in range(len(plotfiles)):
              mystatus = os.system('%s -density %d %s %s.pdf' % (convert,density,plotfiles[i],plotfiles[i].split('.png')[0]))
              if (mystatus != 0):
                  break
# #            filelist += plotfiles[i].split('.png')[0] + '.pdf '
              filelist += plotfiles[i] + '.pdf '
          if (mystatus != 0):
              print "ImageMagick is missing, no PDF created"
              buildpdf = False
          if (buildpdf==True):
              cmd = '%s -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=%s %s' % (gs,pdfname,filelist)
              casalogPost(debug,"Running command = %s" % (cmd))
              mystatus = os.system(cmd)
              if (mystatus == 0):
                  print "PDF left in %s" % (pdfname)
                  os.system("rm -f %s" % filelist)
              else:
                  print "ghostscript is missing, no PDF created"
      return()
  
####################################################################################
# # bpoly == false
#################
    msFound = False
    mytb.open(caltable)
    if (ParType == 'Complex'):  # casa >= 3.4
        gain = {}
        for f in range(len(fields)):
            gain[f] = mytb.getcell('CPARAM',f)
    else: # casa 3.3
        gain = {}
# #      gain = mytb.getcol('FPARAM')       # 2,128,576
        if ('FPARAM' in mytb.colnames()):
            for f in range(len(fields)):
                gain[f] = mytb.getcell('FPARAM',f)
        else:
            for f in range(len(fields)):
                gain[f] = mytb.getcell('GAIN',f)
    nPolarizations =  len(gain[0])
    if (debug):
        print "(1)Set nPolarizations = %d" % nPolarizations
    ggx = {}
    for g in range(len(gain)):
        ggx[g] =  gain[g][0]
    if (nPolarizations == 2):
        ggy = {}
        for g in range(len(gain)):
            ggy[g] =  gain[g][1]
    mytb.close()
  
    if (debug):
      print "nPolarizations = %s" % (str(nPolarizations))
    nRows = len(gain)
    if (bOverlay):
          mytb.open(caltable2)
          gain2 = {}
          if (ParType == 'Complex'):
# #            gain2 = mytb.getcol('CPARAM')
              for f in range(len(fields)):
                  gain2[f] = mytb.getcell('CPARAM',f)
          else:
# #            gain2 = mytb.getcol('FPARAM')
              for f in range(len(fields)):
                  if (tableFormat2 == 34):
                      gain2[f] = mytb.getcell('FPARAM',f)
                  else:
                      gain2[f] = mytb.getcell('GAIN',f)
          mytb.close()
          ggx2 = {}
          for g in range(len(gain2)):
# #            print "Appending to ggx: ", gain2[g][0]
              ggx2[g] = gain2[g][0]
          nPolarizations2 = len(gain2[0])
          if (nPolarizations == 2):
              ggy2 = {}
              for g in range(len(gain2)):
                  ggy2[g] = gain2[g][1]
          nRows2 = len(gain2)
          if (debug): print "nRows2 = %s" % (str(nRows2))
  
    try:
        if (DEBUG):
            print "Trying to open %s" % (msName+'/SPECTRAL_WINDOW')
        mytb.open(msName+'/SPECTRAL_WINDOW')
        refFreq = mytb.getcol('REF_FREQUENCY')
        net_sideband = mytb.getcol('NET_SIDEBAND')
        measFreqRef = mytb.getcol('MEAS_FREQ_REF')
        mytb.close()
        
        (corr_type, corr_type_string, nPolarizations) = getCorrType(msName, spwsToPlot, mymsmd, debug)
        if (corr_type_string == []):
            return()
    except:
        print "4) Could not open the associated measurement set tables (%s). Will not translate antenna names." % (msName)
        print "I will assume ALMA data: XX, YY, and refFreq=first channel."
        chanFreqGHz = []
        corr_type_string = ['XX','YY']
        corr_type = [9,12]
  
    if (len(polsToPlot) > len(corr_type)):
        # Necessary for SMA (single-pol) data
        polsToPlot = corr_type_string
    casalogPost(debug,"Polarizations to plot = %s" % (str(polsToPlot)))
    polsToPlot = checkPolsToPlot(polsToPlot, corr_type_string, debug)
    if (polsToPlot == []):
        return()
  
    if (len(msAnt) > 0):
        msFound = True
    else:
        if (xaxis.find('freq')>=0):
            print "Because I could not open the .ms, you cannot use xaxis='freq'."
            return()
        if (showatm == True or showtsky==True):
            print "Because I could not open the .ms, you cannot use showatm or showtsky."
            return()
    
    if (bpoly == False):
        if (debug):
            print "nPolarizations = %s" % (nPolarizations)
            print "nFields = %d = %s" % (nFields, str(uniqueFields))
  
    if (bOverlay and debug):
          print "nPolarizations2 = %s" % (str(nPolarizations2))
          print "nFields2 = %d = %s" % (nFields2, str(uniqueFields2))
          print "nRows2 = %s" % (str(nRows2))
    uniqueAntennaIds = np.sort(np.unique(ant))
  
    yPhaseLabel = 'Phase (deg)'
    tsysPercent = True
    ampPercent = True
    if (VisCal.lower().find('tsys') >= 0):
        if (channeldiff > 0):
            if (tsysPercent):
                yAmplitudeLabel = "Tsys derivative (%_of_median/channel)"
            else:
                yAmplitudeLabel = "Tsys derivative (K/channel)"
        else:
            yAmplitudeLabel = "Tsys (K)"
    else:
        if (yaxis.lower().find('db')>=0):
            yAmplitudeLabel = "Amplitude (dB)"
        else:
            if (channeldiff > 0):
                if (ampPercent):
                    yAmplitudeLabel = "Amp derivative (%_of_median/channel)"
                else:
                    yAmplitudeLabel = "Amplitude derivative"
                yPhaseLabel = 'Phase derivative (deg/channel)'
            else:
                yAmplitudeLabel = "Amplitude"
  
    madsigma = channeldiff # for option channeldiff>0, sets threshold for finding outliers
    ampMin = LARGE_POSITIVE
    ampMax = LARGE_NEGATIVE
    PHASE_ABS_SUM_THRESHOLD = 2e-3  # in degrees, used to avoid printing MAD statistics for refant
  
    TDMisSecond = False
    pagectr = 0
    drewAtmosphereOnFlaggedAntenna = True  # may not be necessary, but just to be safe
    newpage = 1
    pages =  []
    xctr = 0
    myap = 0  # determines whether an amp or phase plot starts the page (in the case of 'both')
              # zero means amplitude, 1 means phase
    redisplay = False
    matchctr = 0
    myUniqueColor = []
    # for the overlay=antenna case, start by assuming the first antenna is not flagged
    firstUnflaggedAntennaToPlot = 0
    lastUnflaggedAntennaToPlot = len(antennasToPlot)
    computedAtmSpw = -1
    computedAtmTime = -1
    computedAtmField = -1
    skippingSpwMessageSent = 0
    atmString = ''
    if (showimage and lo1==''):
        # We only need to run this once per execution.
        if (debug):
            print "Calling getLOs"
        getLOsReturnValue = getLOs(msName, verbose=debug)
        if (getLOsReturnValue != []):
            if (debug):
                print "Calling interpret LOs"
            lo1s = interpretLOs(msName,parentms,verbose=debug)
            if (debug):
                print "Done interpretLOs"
            foundLO1Message = []  # Initialize so that message is only displayed once per spw
  
    if (channeldiff>0):
        # build blank dictionary:  madstats['DV01']['spw']['time']['pol']['amp' or 'phase' or both]
        #                          where spw, time, pol are each integers
        if (len(msAnt) > 0):
            madstats = dict.fromkeys(mymsmd.antennanames(antennasToPlot))
        else:
            madstats = dict.fromkeys(['Ant '+str(i) for i in range(len(uniqueAntennaIds))])

        for i in range(len(madstats)):
            madstats[madstats.keys()[i]] = dict.fromkeys(spwsToPlot)
            for j in range(len(spwsToPlot)):
                madstats[madstats.keys()[i]][spwsToPlot[j]] = dict.fromkeys(timerangeList) # dict.fromkeys(range(len(uniqueTimes)))
                for k in timerangeList: # range(len(uniqueTimes)):
                    madstats[madstats.keys()[i]][spwsToPlot[j]][k] = dict.fromkeys(range(nPolarizations))
                    for l in range(nPolarizations):
                        if (yaxis == 'both'):
                            madstats[madstats.keys()[i]][spwsToPlot[j]][k][l] = {'amp': None, 'phase': None}
                        elif (yaxis == 'phase'):
                            madstats[madstats.keys()[i]][spwsToPlot[j]][k][l] = {'phase': None}
                        else:
                            # this includes tsys and amp
                            madstats[madstats.keys()[i]][spwsToPlot[j]][k][l] = {'amp': None}
# #      print "madstats = ", madstats
    myinput = ''
    atmEverBeenShown = False
    while (xctr < len(antennasToPlot)):
      xant = antennasToPlot[xctr]
      spwctr = 0
      antstring, Antstring = buildAntString(xant,msFound,msAnt)
      while (spwctr < len(spwsToPlot)):
        ispw = spwsToPlot[spwctr]
        ispwInCalTable = list(uniqueSpwsInCalTable).index(ispw)
        mytime = 0
        if (debug):
            print "+++++++ set mytime=0 for ispw=%d, len(chanFreqGHz) = %d" % (ispw, len(chanFreqGHz))
        if (overlayAntennas):
            xctr = -1
        firstTimeMatch = -1
        while (mytime < nUniqueTimes):
          if (debug):
              print "mytime = %d < %d, uniqueTimes[mytime] = %s" % (mytime,nUniqueTimes,str(uniqueTimes[mytime]))
              print "timerangeList = %s" % (str(timerangeList))
              print "timerangeListTimes = %s" % (str(timerangeListTimes))
              print "debugSloppyMatch = %s" % (str(debugSloppyMatch))
              print "solutionTimeThresholdSeconds = %s" % (str(solutionTimeThresholdSeconds))
          if (len(timerangeList) > 0 and (sloppyMatch(uniqueTimes[mytime],timerangeListTimes,solutionTimeThresholdSeconds,myprint=debugSloppyMatch)==False)):
              if (debug):
                  print "Skipping time %d because it is not in the list: %s" % (mytime, str(timerangeList))
              mytime += 1
              if (mytime == nUniqueTimes and overlayTimes and overlayAntennas):  
                  # added March 14, 2013 to support the case when final timerange is flagged
                  doneOverlayTime = False
                  if (debug):
                      print "$$$$$$$$$$$$$$$$$$$$$$  Setting doneOverlayTime=False" % (xframe)
              continue
          if (overlayAntennas):
              xctr += 1
              if (xctr >= len(antennasToPlot)):
                  xctr = 0
              xant = antennasToPlot[xctr]
              if (debug):
                  print "mytime=%d, Set xant to %d" % (mytime,xant)
              antennaString = ''
          else:
              antennaString = 'Ant%2d: %s,  ' % (xant,antstring)
          # This used to be above the previous if/else block
          if (newpage==1):
              # add the current page (being created here) to the list
              pages.append([xctr,spwctr,mytime,0])
              if (debug):
                  print "top: appending [%d,%d,%d,%d]" % (xctr,spwctr,mytime,0)
              newpage = 0
          gplotx = []
          gploty = []
          channels = []
          xchannels = []
          ychannels = []
          frequencies = []
          xfrequencies = []
          yfrequencies = []
          channels2 = []
          xchannels2 = []
          ychannels2 = []
          frequencies2 = []
          xfrequencies2 = []
          yfrequencies2 = []
          gplotx2 = []
          gploty2 = []
          xflag = []
          yflag = []
          xflag2 = []
          yflag2 = []
          matchFound = False
          for i in range(nRows):
              sm = sloppyMatch(uniqueTimes[mytime],times[i],solutionTimeThresholdSeconds,myprint=False)
              if ((ant[i]==xant) and (cal_desc_id[i]==ispw) and sm
                  and (mytime in timerangeList)   # this test was added to support multiFieldInTimeOverlay
                  ):
                  if (debug): print "len(chanFreqGHz)=%d, ispw=%d" % (len(chanFreqGHz),ispw)
                  if (msFound):
                      if (len(chanFreqGHz[ispw]) == 1):
                          if ((skippingSpwMessageSent & (1<<ispw)) == 0):
                              casalogPost(debug,"Skipping spw=%d because it has only 1 channel." % (ispw))
                              skippingSpwMessageSent |= (1<<ispw)
                          break
                  if (fields[i] in fieldsToPlot):
                      interval = intervals[i] # used for CalcAtmTransmission
                      fieldIndex = np.where(fields[i] == uniqueFields)[0]
                      if (debug):
                          print "%d Found match at field,ant,spw,mytime,time = %d(index=%d),%d,%d,%d,%f=%s" % (matchctr,fields[i],fieldIndex,xant,ispw,mytime,uniqueTimes[mytime],utstring(uniqueTimes[mytime],4))
                      if (matchFound):
                          print "WARNING: This cal table has multiple rows for field=%d,ant=%d,spw=%d,time=%d=%.0f=%s. Only showing the first one." % (fields[i],xant,ispw,mytime,uniqueTimes[mytime],utstring(uniqueTimes[mytime],3))
                      else:
                          matchFound = True
                          if (msFound):
                              nChannels = len(chanFreqGHz[ispw])
                          else:
                              nChannels = len(ggx[0])
                          xflag.append(flags[i][0][:])
                          yflag.append(flags[i][1][:])
                          BRowNumber = i
                          for j in range(nChannels):   # len(chanFreqGHz[ispw])):
                              channels.append(j)  # both flagged and unflagged
                              if (msFound):
                                  frequencies.append(chanFreqGHz[ispw][j])
                                  if (j==0 and debug):
                                      print "found match: ispw=%d, j=%d, len(chanFreqGHz)=%d, chanFreqGHz[0]=%f" % (ispw,j, len(chanFreqGHz),chanFreqGHz[ispw][0])
                              if (showflagged or (showflagged == False and flags[i][0][j]==0)):
                                  gplotx.append(ggx[i][j])
                                  xchannels.append(j)
                                  if (msFound):
                                      xfrequencies.append(chanFreqGHz[ispw][j])
                              if (nPolarizations == 2):
                                  if (showflagged or (showflagged == False and flags[i][1][j]==0)):
                                      gploty.append(ggy[i][j])
                                      ychannels.append(j)
                                      if (msFound):
                                          yfrequencies.append(chanFreqGHz[ispw][j])
          # end 'for i'
          myspw = originalSpw[ispw]
          if (msFound):
              if debug: 
                  print "myspw=%s" % (str(myspw))
                  print "len(refFreq)=%d" % (len(refFreq))
              if (myspw >= len(refFreq)):
                  myspw = ispw
          if (msFound and refFreq[myspw]*1e-9 > 60):
            # Then this cannot be EVLA data.  But I should really check the telescope name!
            if (refFreq[myspw]*1e-9 > np.mean(frequencies)):
                sideband = -1
                xlabelString = "%s LSB Frequency (GHz)" % refTypeToString(measFreqRef[myspw])
            else:
                sideband = +1
                xlabelString = "%s USB Frequency (GHz)" % refTypeToString(measFreqRef[myspw])
          else:
              sideband = -1
              xlabelString = "Frequency (GHz)"
          if ((len(frequencies)>0) and (chanrange[1] > len(frequencies))):
              print "Invalid chanrange (%d-%d) for spw%d in caltable1. Valid range = 0-%d" % (chanrange[0],chanrange[1],ispw,len(frequencies)-1)
              return()
          pchannels = [xchannels,ychannels]
          pfrequencies = [xfrequencies,yfrequencies]
          gplot = [gplotx,gploty]
          # We only need to compute the atmospheric transmission if:
          #   * we have been asked to show it,
          #   * there is a non-trivial number of channels, 
          #   * the current field is the one for which we should calculate it (if times are being overlaied)
          #       But this will cause no atmcurve to appear if that field is flagged on the first
          #       antenna; so, I added the atmEverBeenShown flag to deal with this.
          #   * the previous calculation is not identical to what this one will be
          #
          if ((showatm or showtsky) and (len(xchannels)>1 or len(ychannels)>1) and
              (uniqueFields[fieldIndex]==showatmfield or overlayTimes==False or atmEverBeenShown==False) and
              ((overlayTimes==False and computedAtmField!=fieldIndex) or (computedAtmSpw!=ispw) or
               (overlayTimes==False and computedAtmTime!=mytime))):
            atmEverBeenShown = True
            # The following 'if' is used to avoid wasting time since atm is not shown for
            # overlay='antenna,time'.
            if (overlayTimes==False or overlayAntennas==False or True):  # support showatm for overlay='antenna,time'
#            if (overlayTimes==False or overlayAntennas==False):
# #            print "CAF, CAS, CAT = ", computedAtmField, computedAtmSpw, computedAtmTime
              computedAtmField = fieldIndex
              computedAtmSpw = ispw
              computedAtmTime = mytime
              atmtime = timeUtilities.time()
              asdm = ''
# #            print "A) uniqueFields[%d] = " % (fieldIndex), uniqueFields[fieldIndex]
              uFFI = uniqueFields[fieldIndex]
              if (type(uFFI) == type(np.ndarray(0))):
                  uFFI = uFFI[0]
                  if (debug): print "converting uFFI from array to %s" % (str(type(uFFI)))
              (atmfreq,atmchan,transmission,pwvmean,atmairmass,TebbSky,missingCalWVRErrorPrinted) = \
                 CalcAtmTransmission(channels, frequencies, xaxis, pwv,
                         vm, mymsmd, msName, asdm, xant, uniqueTimes[mytime],
                         interval, uFFI, refFreq[originalSpw[ispw]],
                         net_sideband[originalSpw[ispw]], mytime, 
                         missingCalWVRErrorPrinted, verbose=DEBUG)
              if (showimage):
                  if (lo1 != ''):
                      LO1 = lo1
                  else:
                    if (getLOsReturnValue == []):
                      if (lo1 == ''):
                          print "Because you do not have the ASDM_RECEIVER table, if you want the showimage"
                          print "option to work, then you must specify the LO1 frequency with lo1=."
# #                        return()
                      LO1 = lo1
                    else:
                      if (lo1s == None or lo1s == {}):
                          print "Failed to get LO1, disabling showimage.  Alternatively, you can use printLOsFromASDM and supply the lo1 parameter to plotbandpass."
                          showimage = False
                          LO1 = ''
                      else:
                          LO1 = lo1s[originalSpw[ispw]]*1e-9  
                          if (ispw not in foundLO1Message):
                              casalogPost(debug,"For spw %d (%d), found LO1 = %.6f GHz" % (ispw,originalSpw[ispw],LO1))
                              foundLO1Message.append(ispw)
              if (LO1 != ''):
                  frequenciesImage = list(2*LO1 - np.array(frequencies))
                  xfrequenciesImage = list(2*LO1 - np.array(pfrequencies[0]))
                  yfrequenciesImage = list(2*LO1 - np.array(pfrequencies[1]))
                  pfrequenciesImage = [xfrequenciesImage, yfrequenciesImage]
                  if (debug):
                     print "B) uniqueFields[%d] = %s" % (fieldIndex, str(uniqueFields[fieldIndex]))
                  uFFI = uniqueFields[fieldIndex]
                  if (debug):
                     print "type(uFFI) = %s" % (str(type(uFFI)))
                  if (type(uFFI) == list or type(uFFI) == type(np.ndarray(0))):
                     uFFI = uFFI[0]
                  if (debug):
                     print "uFFI = %s" % (str(uFFI))
                  (atmfreqImage,atmchanImage,transmissionImage,pwvmean,atmairmass,TebbSkyImage,missingCalWVRErrorPrinted) = \
                      CalcAtmTransmission(channels, frequenciesImage, xaxis,
                                          pwv, vm, mymsmd, msName, asdm, xant, uniqueTimes[mytime],
                                          interval, uFFI, refFreq[originalSpw[ispw]],
                                          net_sideband[originalSpw[ispw]], mytime, 
                                          missingCalWVRErrorPrinted, verbose=DEBUG)
                  atmfreqImage = list(2*LO1 - np.array(atmfreqImage))
                  atmfreqImage.reverse()
                  atmchanImage.reverse()
  
              if (overlayTimes):
                  atmString = 'PWV %.2fmm, airmass %.2f (field %d)' % (pwvmean,atmairmass,showatmfield)
              else:
                  atmString = 'PWV %.2fmm, airmass %.3f' % (pwvmean,atmairmass)
          if (bOverlay):
            for i in range(nRows2):
              if ((ant2[i]==xant) and (cal_desc_id2[i]==ispw) and sloppyMatch(uniqueTimes2[mytime],times2[i],solutionTimeThresholdSeconds,myprint=debugSloppyMatch)):
                  if (fields2[i] in fieldsToPlot):
                        xflag2.append(flags2[i][0][:])
                        yflag2.append(flags2[i][1][:])
                        # With solint='2ch' or more, the following loop should not be over
                        # chanFreqGHz2 but over the channels in the solution.
                        for j in range(len(chanFreqGHz2[ispw])):
                          channels2.append(j)
                          frequencies2.append(chanFreqGHz2[ispw][j])
# #                        print "len(chanFreqGHz2[%d])=%d, i=%d,j=%d, len(ggx2)=%d, len(ggx2[0])=%d, shape(ggx2) = " % (ispw,len(chanFreqGHz2[ispw]),i,j,len(ggx2),len(ggx2[0])), np.shape(np.array(ggx2))
                          if (showflagged or (showflagged == False and flags2[i][0][j]==0)):
                              gplotx2.append(ggx2[i][j])
                              xchannels2.append(j)
                              xfrequencies2.append(chanFreqGHz2[ispw][j])
# #                            print "appending %f to xfrequencies2" % (chanFreqGHz2[ispw][j])
# #                        else:
# #                            if (debug):  # The following crashes
# #                                print "********* flags2[0,%d,%d] = %d, showflagged=" % (j,i,flags2[0,j,i]), showflagged
                          if (nPolarizations2 == 2):
                              if (showflagged or (showflagged == False and flags2[i][1][j]==0)):
                                  gploty2.append(ggy2[i][j])
                                  ychannels2.append(j)
                                  yfrequencies2.append(chanFreqGHz2[ispw][j])
            # end 'for i'
            pchannels2 = [xchannels2,ychannels2]
            pfrequencies2 = [xfrequencies2,yfrequencies2]
            gplot2 = [gplotx2,gploty2]
# #
# #  Don't check here, because chanrange refers only to caltable, not caltable2.
# #          if (len(frequencies2)>0 and (chanrange[1] > len(frequencies2))):
# #              print "Invalid chanrange for spw%d in caltable2. Valid range = 0-%d" % (ispw,len(frequencies2))
# #              return()
                
# # Prevents crash if long value is set for solutionTimeThresholdSeconds, but prints a lot of
# # messages for Tsys with overlay='antenna'.
# #        if (len(xchannels) < 1):
# #            print "No unflagged data found for (ant,spw,mytime,time) = %d,%d,%d,%.1f=%s" % (xant,ispw,mytime,uniqueTimes[mytime],utstring(uniqueTimes[mytime],4))
# #            matchFound = False
  
          if (matchFound==False):
              if (overlayAntennas==False or (overlayAntennas==True and xctr+1 >= len(antennasToPlot))):
                  mytime += 1
                  if (debug):
                      print "a) xctr=%d, Incrementing mytime to %d" % (xctr, mytime)
              continue
          #  The following variable allows color legend of UT times to match line plot
          myUniqueTime = []
          if (True):  # multiFieldsWithOverlayTime):
              # support multi-fields with overlay='time'
              uTPFPS = []
              for f in fieldIndicesToPlot:
                  for t in uniqueTimesPerFieldPerSpw[ispwInCalTable][f]:
                      if (sloppyMatch(t, timerangeListTimes, solutionTimeThresholdSeconds,myprint=debugSloppyMatch)):
                          uTPFPS.append(t)
              uTPFPS = np.sort(uTPFPS)
              ctr = 0
              for t in uTPFPS:
                  if (debug and False):
                      print "1)checking time %d" % (t)
                  if (sloppyMatch(t, uniqueTimes[mytime], solutionTimeThresholdSeconds,myprint=debugSloppyMatch)):
                      if (debug):
                          print "1)setting myUniqueTime to %d" % (mytime)
                      myUniqueTime = mytime
                      ctr += 1
              if (ctr > 1 and bOverlay==False):
                  print "multi-field time overlay ***************  why are there 2 matches?"
# #            if (ctr == 0):
# #                print "No match for %.1f in "%(t), uTPFPS
          else:
# #          print "ispw=%d, fieldIndex=%d, len(uTPFPS)=%d" % (ispw,fieldIndex,len(uniqueTimesPerFieldPerSpw))
            for t in uniqueTimesPerFieldPerSpw[ispwInCalTable][fieldIndex]:
              if (debug):
                  print "2)checking time %d" % (t)
              if (sloppyMatch(t, uniqueTimes[mytime], solutionTimeThresholdSeconds,myprint=debugSloppyMatch) == True):
                  myUniqueTime = mytime  # was t
                  if (debug):
                      print "2)setting myUniqueTime to %d" % (mytime)
          
# #        print "Overlay antenna %d, myUniqueTime=%d" % (xctr, myUniqueTime)
          if (xframe == xframeStart):
                pb.clf()
          xflag = [item for sublist in xflag for item in sublist]
          yflag = [item for sublist in yflag for item in sublist]
#          pflag = [xflag, yflag]
#          flagfrequencies = [frequencies, frequencies2]
          antstring, Antstring = buildAntString(xant,msFound,msAnt)
          if (msFound):
              fieldString = msFields[uniqueFields[fieldIndex]]
          else:
              fieldString = str(field)
          if (overlayTimes):
              timeString =''
          else:
              timeString = ',  t%d/%d  %s' % (mytime,nUniqueTimes-1,utstring(uniqueTimes[mytime],3))
          if (ispw==originalSpw[ispw]):
                titleString = "%sspw%2d,  field %d: %s%s" % (antennaString,ispw,uniqueFields[fieldIndex],fieldString,timeString)
          else:
                titleString = "%sspw%2d (%d),  field %d: %s%s" % (antennaString,ispw,originalSpw[ispw],uniqueFields[fieldIndex],fieldString,timeString)
          if (sum(xflag)==nChannels and sum(yflag)==nChannels and showflagged==False):
                  if (overlayTimes):
                      print "Skip %s (%s) for time%d=%s all data flagged" % (antstring, titleString,mytime,utstring(uniqueTimes[mytime],3))
                      # need to set doneOverlayTime = True if this is the final time
                      if (debug):
                          print "########## uniqueTimes[%d]=%d,  timerangeListTimes[-1]=%d" % (mytime,uniqueTimes[mytime],timerangeListTimes[-1])
                      if (sloppyMatch(timerangeListTimes[-1], uniqueTimes[mytime], solutionTimeThresholdSeconds,myprint=debugSloppyMatch)):
                          doneOverlayTime = True  # 08-Nov-2012
                          if (debug):
                              print "###### set doneOverlayTime = %s" % (str(doneOverlayTime))
  
                          # draw labels
                          # try adding the following 'if' statement on Jun 18, 2013; it works.
                          if (drewAtmosphereOnFlaggedAntenna==False or overlayAntennas==False):
                              drewAtmosphereOnFlaggedAntenna = True
                              drawOverlayTimeLegends(xframe,firstFrame,xstartTitle,ystartTitle,caltable,titlesize,
                                  fieldIndicesToPlot,ispwInCalTable,uniqueTimesPerFieldPerSpw,timerangeListTimes,
                                  solutionTimeThresholdSeconds,debugSloppyMatch,ystartOverlayLegend,debug,mysize,
                                  fieldsToPlot,myUniqueColor,timeHorizontalSpacing,fieldIndex,overlayColors,
                                  antennaVerticalSpacing, overlayAntennas, timerangeList, caltableTitle)
                              drawAtmosphereAndFDM(showatm,showtsky,atmString,subplotRows,mysize,TebbSky,TebbSkyImage,
                                               plotrange, xaxis,atmchan,atmfreq,transmission,subplotCols,
                                               showatmPoints,xframe, channels,LO1,atmchanImage,atmfreqImage,
                                               transmissionImage, firstFrame,showfdm,nChannels,tableFormat,
                                               originalSpw_casa33, chanFreqGHz_casa33,originalSpw,chanFreqGHz,
                                               overlayTimes, overlayAntennas, xant, antennasToPlot)
                          DrawPolarizationLabelsForOverlayTime(xstartPolLabel,ystartPolLabel,corr_type,polsToPlot,
                                                               channeldiff,ystartMadLabel,subplotRows,gamp_mad,mysize,
                                                               ampmarkstyle,markersize,ampmarkstyle2)
                  else:
                      print "Skip %s (%s) all data flagged" % (antstring, titleString)
                      if (myinput == 'b'):
                          redisplay = False # This prevents infinite loop when htting 'b' on first screen when ant0 flagged. 2013-03-08
                  if (overlayAntennas==False):
                    if (doneOverlayTime==False or overlayTimes==False):  # added on 08-Nov-2012
                      mytime += 1
                      if (debug):
                          print "F) incrementing mytime to %d" % mytime
                  if (overlayAntennas):
                      if (xctr == firstUnflaggedAntennaToPlot):
                          firstUnflaggedAntennaToPlot += 1
                          if (firstUnflaggedAntennaToPlot >= len(antennasToPlot)):
                              firstUnflaggedAntennaToPlot = 0
                              mytime += 1
                          if (debug):
                              print "----- Resetting firstUnflaggedAntennaToPlot from %d to %d = %d" % (firstUnflaggedAntennaToPlot-1, firstUnflaggedAntennaToPlot, antennasToPlot[firstUnflaggedAntennaToPlot])
                          continue # Try this on Apr 2, 2012 to fix bug.
                  if (overlayAntennas==False and subplot==11):
                        # added the case (subplot==11) on April 22, 2012 to prevent crash on multi-antenna subplot=421
                        if (debug):
                            print "#######  removing [%d,%d,%d,%d]" % (pages[len(pages)-1][PAGE_ANT],
                                                              pages[len(pages)-1][PAGE_SPW],
                                                              pages[len(pages)-1][PAGE_TIME],
                                                              pages[len(pages)-1][PAGE_AP])
                        pages = pages[0:len(pages)-1]
                        newpage = 1
                  if (overlayAntennas==False):
                      if (doneOverlayTime==False):  # inserted on 08-Nov-2012
                          continue
                      elif (debug):
                          print "=========== Not continuing because doneOverlayTime=%s" % (str(doneOverlayTime))
                  
          if (firstTimeMatch == -1):
                firstTimeMatch = mytime
                if (debug):
                    print "Setting firstTimeMatch from -1 to %s" % (str(firstTimeMatch))
  
########### Here is the amplitude plotting ############
          if (yaxis.find('amp')>=0 or yaxis.find('both')>=0 or yaxis.find('ap')>=0) and doneOverlayTime==False:
  
            if (debug):
                print "amp: xctr=%d, xant=%d, myap=%d, mytime=%d(%s), firstTimeMatch=%d, bOverlay=" % (xctr, xant, myap, mytime, utstring(uniqueTimes[mytime],3), firstTimeMatch), bOverlay
            if (myap==1):
              if (overlayTimes == False or mytime==firstTimeMatch):
                  if (overlayAntennas==False or xctr==firstUnflaggedAntennaToPlot
                      or xctr==antennasToPlot[-1]):  # 2012-05-24, to fix the case where all ants flagged on one timerange
                      xframe += 1
                      if (debug):
                          print "y) incrementing xframe to %d" % xframe
                          print "mytime=%d  ==  firstTimeMatch=%d" % (mytime, firstTimeMatch)
                          print "xctr=%d  ==  firstUnflaggedAntennaToPlot=%d,  antennastoPlot[-1]=%d" % (xctr, firstUnflaggedAntennaToPlot,antennasToPlot[-1])
                      myUniqueColor = []
                      newylimits = [LARGE_POSITIVE, LARGE_NEGATIVE]
            else: # (myap == 0)
              if (overlayTimes == False or mytime==firstTimeMatch):
                  if (overlayAntennas==False or xctr==firstUnflaggedAntennaToPlot
                      or xctr>antennasToPlot[-1]):  # 2012-05-24, to fix the case where all ants flagged on one timerange
                      xframe += 1
                      if (debug):
                          print "Y) incrementing xframe to %d" % xframe
                          print "mytime=%d  ==  firstTimeMatch=%d" % (mytime, firstTimeMatch)
                          print "xctr=%d  ==  firstUnflaggedAntennaToPlot=%d,  antennasToPlot[-1]=%d" % (xctr, firstUnflaggedAntennaToPlot,antennasToPlot[-1])
                      myUniqueColor = []
                      newylimits = [LARGE_POSITIVE, LARGE_NEGATIVE]
                      if (debug):
                          print "myap=%d, mytime == firstTimeMatch=%d" % (myap, firstTimeMatch)
              if (debug):
                  print "$$$$$$$$$$$$$$$$$$$$$$$  ready to plot amp on xframe %d" % (xframe)
# #            print ",,,,,,,,,,,,,,,, Starting with newylimits = ", newylimits
              adesc = pb.subplot(xframe)
              drewAtmosphereOnFlaggedAntenna = False
              pb.hold(overlayAntennas or overlayTimes)
              gampx = np.abs(gplotx)
              if (nPolarizations == 2):
                  gampy = np.abs(gploty)
                  if (yaxis.lower().find('db') >= 0):
                      gamp = [10*np.log10(gampx), 10*np.log10(gampy)]
                  else:
                      if (channeldiff>0):
                          if (debug): print "Computing derivatives"
                          if (xaxis == 'chan'):
                              gamp0, newx0 = channelDifferences(gampx, pchannels[0])
                              gamp1, newx1 = channelDifferences(gampy, pchannels[1])
                              pchannels = [newx0, newx1]
                          else:
                              gamp0, newx0 = channelDifferences(gampx, pfrequencies[0])
                              gamp1, newx1 = channelDifferences(gampy, pfrequencies[1])
                              pfrequencies = [newx0, newx1]
                          gamp = [gamp0, gamp1]
                          if (VisCal.lower().find('tsys') >= 0 and tsysPercent):
                              gamp = [100*gamp0/np.median(gampx), 100*gamp1/np.median(gampy)]
                          elif (VisCal.lower().find('tsys') < 0 and ampPercent):
                              gamp = [100*gamp0/np.median(gampx), 100*gamp1/np.median(gampy)]
                          gamp_mad = [madInfo(gamp[0],madsigma,edge), madInfo(gamp[1],madsigma,edge)]
                          if (debug): print "gamp_mad done"
                          for p in [0,1]:
                              if (debug):
                                  print "gamp_mad[%d] = %s" % (p, str(gamp_mad[p]))
                                  print "madstats[%s][%d] = %s" % (Antstring,ispw, str(madstats[Antstring][ispw]))
                              madstats[Antstring][ispw][mytime][p]['amp'] = gamp_mad[p]['mad']
                              if (gamp_mad[p]['nchan'] > 0):
                                  casalogPost(debug, "%s, Pol %d, spw %2d, %s, amp: %4d points exceed %.1f sigma (worst=%.2f at chan %d)" % (Antstring, p, ispw, utstring(uniqueTimes[mytime],0), gamp_mad[p]['nchan'], madsigma, gamp_mad[p]['outlierValue'], gamp_mad[p]['outlierChannel']+pchannels[p][0]))
                          if (debug): print "madstats done"
                      else:
                          gamp = [gampx,gampy]
              else:
                  if (yaxis.lower().find('db') >= 0):
                      gamp = [10*np.log10(gampx)]
                  else:
                      if (channeldiff>0):
                          if (xaxis == 'chan'):
                              gamp0, newx0 = channelDifferences(gampx, pchannels[0])
                              pchannels = [newx0]
                          else:
                              gamp0, newx0 = channelDifferences(gampx, pfrequencies[0])
                              pfrequencies = [newx0]
                          gamp = [gamp0]
                          if (VisCal.lower().find('tsys') >= 0 and tsysPercent):
                              gamp = [100*gamp0/np.median(gampx)]
                          elif (VisCal.lower().find('tsys') < 0 and ampPercent):
                              gamp = [100*gamp0/np.median(gampx)]
                          p = 0
                          gamp_mad = [madInfo(gamp[p], madsigma,edge)]
                          madstats[Antstring][ispw][mytime][p]['amp'] = gamp_mad[p]['mad']
                          if (gamp_mad[p]['nchan'] > 0):
                              casalogPost(debug, "%s, Pol %d, spw %2d, %s, amp: %4d points exceed %.1f sigma (worst=%.2f at chan %d)" % (Antstring, p, ispw, utstring(uniqueTimes[mytime],0), gamp_mad[p]['nchan'], madsigma, gamp_mad[p]['outlierValue'], gamp_mad[p]['outlierChannel']+pchannels[p][0]))
                      else:
                          gamp = [gampx]
              if (bOverlay):
                    gampx2 = np.abs(gplotx2)
                    if (nPolarizations2 == 2):
                      gampy2 = np.abs(gploty2)
                      if (yaxis.lower().find('db') >= 0):
                          gamp2 = [10*np.log10(gampx2), 10*np.log10(gampy2)]
                      else:
                          if (channeldiff>0):
                              if (xaxis == 'chan'):
                                  gamp2_0, newx0 = channelDifferences(gampx2, pchannels2[0])
                                  gamp2_1, newx1 = channelDifferences(gampy2, pchannels2[1])
                                  pchannels2 = [newx0, newx1]
                              else:
                                  gamp2_0, newx0 = channelDifferences(gampx2, pfrequencies2[0])
                                  gamp2_1, newx1 = channelDifferences(gampy2, pfrequencies2[1])
                                  pfrequencies2 = [newx0, newx1]
                              gamp2 = [gamp2_0, gamp2_1]
                              if (VisCal.lower().find('tsys') >= 0 and tsysPercent):
                                  gamp2 = [100*gamp2_0/np.median(gampx2), 100*gamp2_1/np.median(gampy2)]
                              elif (VisCal.lower().find('tsys') < 0 and ampPercent):
                                  gamp2 = [100*gamp2_0/np.median(gampx2), 100*gamp2_1/np.median(gampy2)]
                          else:
                              gamp2 = [gampx2, gampy2]
                    else:
                      if (yaxis.lower().find('db') >= 0):
                          gamp2 = [10*np.log10(gampx2)]
                      else:
                          if (channeldiff>0):
                              if (xaxis == 'chan'):
                                  gamp2_0, newx0 = channelDifferences(gampx2, pchannels[0])
                                  pchannels2 = [newx0]
                              else:
                                  gamp2_0, newx0 = channelDifferences(gampx2, pfrequencies[0])
                                  pfrequencies2 = [newx0]
                              gamp2 = [gamp2_0]
                              if (VisCal.lower().find('tsys') >= 0 and tsysPercent):
                                  gamp2 = [100*gamp2_0/np.median(gampx2)]
                              elif (VisCal.lower().find('tsys') < 0 and ampPercent):
                                  gamp2 = [100*gamp2_0/np.median(gampx2)]
                          else:
                              gamp2 = [gampx2]
              if (xaxis.find('chan')>=0 or msFound==False):    #  'amp'
                  if (debug):
                      print "amp: plot vs. channel **********************"
                  pb.hold(True)
                  for p in range(nPolarizations):
                      if (overlayAntennas or overlayTimes):
                          if (corr_type_string[p] in polsToPlot):
                                pdesc = pb.plot(pchannels[p],gamp[p],'%s'%ampmarkstyles[p],
                                                markersize=markersize,
                                                markerfacecolor=overlayColors[xctr])
                                newylimits =  recalcYlimits(plotrange,newylimits,gamp[p])
                                if (overlayAntennas and overlayTimes==False):
                                    pb.setp(pdesc, color=overlayColors[xctr])
                                elif (overlayTimes and overlayAntennas==False):
                                    pb.setp(pdesc, color=overlayColors[mytime])
                                elif (overlayTimes and overlayAntennas): # try to support time,antenna
                                    if (debug):
                                        print "p=%d, len(fieldsToPlot)=%d, len(timerangeList)=%d" % (p,len(fieldsToPlot),len(timerangeList))
                                    if (myUniqueTime != [] and (len(fieldsToPlot) > 1 or len(timerangeList)>1)):
                                        pb.setp(pdesc, color=overlayColors[myUniqueTime])
# #                                      print "pb.setp: myUniqueTime, overlayColors = ", myUniqueTime, overlayColors[myUniqueTime]
                                        # The third 'or' below is needed if pol='0' is flagged on antenna 0. -- 2012/10/12
                                        if (p==0 or len(polsToPlot)==1 or myUniqueColor==[]):
                                            myUniqueColor.append(overlayColors[len(myUniqueColor)])
                                        pb.setp(pdesc, color=myUniqueColor[-1])
                      else:
                          if (corr_type_string[p] in polsToPlot):
# #                          print "pcolor[%d]=%s" % (p,pcolor)
                            pb.plot(pchannels[p],gamp[p],'%s%s'%(pcolor[p],ampmarkstyle), markersize=markersize)
                            newylimits =  recalcYlimits(plotrange,newylimits,gamp[p])
                  if (sum(xflag)>0):
                      xrange = np.max(channels)-np.min(channels)
                      SetNewXLimits([np.min(channels)-xrange/20, np.max(channels)+xrange/20])
# #                    print "amp: Resetting xaxis channel range to counteract flagged data"
                  if (xframe in bottomRowFrames or (xctr+1==len(antennasToPlot) and ispw==spwsToPlot[-1])):
                      pb.xlabel("Channel", size=mysize)
              elif (xaxis.find('freq')>=0):   # amp
                  if (bOverlay):
                        pb.hold(True)
                        xrange = np.abs(xfrequencies[0]-xfrequencies[-1])
                        try:
                            xrange2 = np.abs(xfrequencies2[0]-xfrequencies2[-1])
                        except:
                            print "No amp data found in second solution.  Try increasing the solutionTimeThresholdSeconds above %.0f." % (solutionTimeThresholdSeconds)
                            print "If this doesn't work, email the developer (%s)." % (developerEmail)
                            return()
  
                        if (np.abs(xrange/xrange2 - 1) > 0.05 + len(xflag)/len(xchannels)):  # 0.0666 is 2000/1875-1
                           # These line widths are optimal for visualizing FDM over TDM
                           width1 = 1
                           width2 = 4
                           # solutions differ in frequency width
                           if (xrange < xrange2):
                              for p in range(nPolarizations):
                                    if (corrTypeToString(corr_type[p]) in polsToPlot):
                                          pb.plot(pfrequencies[p], gamp[p], '%s%s'%(pcolor[p],ampmarkstyle), linewidth=width2, markersize=markersize)
                                          newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp[p], sideband,plotrange,xchannels)
                              for p in range(nPolarizations):
                                    if (corrTypeToString(corr_type[p]) in polsToPlot):
                                          pb.plot(pfrequencies2[p], gamp2[p], '%s%s'%(p2color[p],ampmarkstyle), linewidth=width1, markersize=markersize)
                                          newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp2[p], sideband,plotrange,xchannels2)
                           else:
                              for p in range(nPolarizations):
                                    if (corrTypeToString(corr_type[p]) in polsToPlot):
                                          pb.plot(pfrequencies2[p], gamp2[p], '%s%s'%(p2color[p],ampmarkstyle), linewidth=width2, markersize=markersize)
                                          newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp2[p], sideband,plotrange,xchannels2)
                              for p in range(nPolarizations):
                                    if (corrTypeToString(corr_type[p]) in polsToPlot):
                                          pb.plot(pfrequencies[p], gamp[p], '%s%s'%(pcolor[p],ampmarkstyle), linewidth=width1, markersize=markersize)
                                          newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp[p], sideband,plotrange,xchannels)
                        else:
                           width1 = 1
                           width2 = 2  # Just enough to distinguish one line from the other.
                           # solutions may be different level of smoothing, so plot highest rms first
                           if (np.std(gamp[0]) < np.std(gamp2[0])):
                              for p in range(nPolarizations):
                                  if (corrTypeToString(corr_type[p]) in polsToPlot):
                                      pb.plot(pfrequencies2[p], gamp2[p], '%s%s'%(p2color[p],ampmarkstyle), linewidth=width1, markersize=markersize)
                                      newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp2[p], sideband,plotrange,xchannels2)
                              for p in range(nPolarizations):
                                  if (corrTypeToString(corr_type[p]) in polsToPlot):
                                      pb.plot(pfrequencies[p], gamp[p], '%s%s'%(pcolor[p],ampmarkstyle), linewidth=width2, markersize=markersize)
                                      newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp[p], sideband,plotrange,xchannels)
                           else:
                              for p in range(nPolarizations):
                                  if (corrTypeToString(corr_type[p]) in polsToPlot):
                                      pb.plot(pfrequencies[p], gamp[p], '%s%s'%(pcolor[p],ampmarkstyle), linewidth=width2, markersize=markersize)
                                      newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp[p], sideband,plotrange,xchannels)
                              for p in range(nPolarizations):
                                  if (corrTypeToString(corr_type[p]) in polsToPlot):
                                      pb.plot(pfrequencies2[p], gamp2[p], '%s%s'%(p2color[p],ampmarkstyle), linewidth=width1, markersize=markersize)
                                      newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp2[p], sideband,plotrange,xchannels2)
                        # must set new limits after plotting  'amp'
                        if (zoom=='intersect'):
                            if (xrange < xrange2):
                                SetNewXLimits([min(xfrequencies[0],xfrequencies[-1])-xrange*0.1, max(xfrequencies[0],xfrequencies[-1])+xrange*0.1])
                                SetLimits(plotrange, chanrange, newylimits, channels, frequencies,
                                          pfrequencies, ampMin, ampMax, xaxis, pxl)
                            else:
# #                              print "len(xfrequencies2) = ", len(xfrequencies2)
                                SetNewXLimits([min(xfrequencies2[0],xfrequencies2[-1])-xrange2*0.1, max(xfrequencies2[0],xfrequencies2[-1])+xrange2*0.1])
                                slstatus = SetLimits(plotrange, chanrange, newylimits, channels, frequencies2,
                                          pfrequencies2, ampMin, ampMax, xaxis, pxl)
                        else:
                            if (xrange < xrange2):
                                SetLimits(plotrange, chanrange, newylimits, channels, frequencies,
                                          pfrequencies, ampMin, ampMax, xaxis, pxl)
                            else:
                                SetLimits(plotrange, chanrange, newylimits, channels, frequencies2,
                                          pfrequencies2, ampMin, ampMax, xaxis, pxl)
                        # draw polarization and spw labels
                        if (xframe == firstFrame):
                            # draw title including caltable name
                            caltableList = 'c1 = ' + caltable + ',  c2 = ' + caltable2 + ' (%s)'%(utstring(uniqueTimes2[mytime],3))
                            pb.text(xstartTitle, ystartTitle, caltableList, size=titlesize,
                                    color='k', transform=pb.gcf().transFigure)
                  elif (bpolyOverlay):
                      if (debug):
                          print "in bpolyOverlay **********************************"
                      matches1 = []
                      for tbp in range(len(timesBP)):
                          if (sloppyMatch(uniqueTimes[mytime], timesBP[tbp], solutionTimeThresholdSeconds,myprint=debugSloppyMatch)):
                              matches1.append(tbp)
                      matches1 = np.array(matches1)
                      if (len(matches1) < 1):
                          print "No time match found between %.1f and %s" % (uniqueTimes[mytime], str(timesBP))
                          print "If you are sure the solutions correspond to the same data, you can set solutionTimeThresholdSeconds>=%.0f" % (1+np.ceil(np.abs(timesBP[0]-uniqueTimes[mytime])))
                          return()
                      matches2 = np.where(xant == np.array(antennasBP))[0]
                      if (len(matches2) < 1):
                          print "No antenna match found: %s" % (str(xant), str(antennasBP))
                      if (tableFormat == 33):
                          matches3 = np.where(ispw == np.array(cal_desc_idBP))[0]
                          if (len(matches3) < 1):
                              print "No spw match found: %d not in %s" % (ispw, str(cal_desc_idBP))
                      else:
                          matches3 = np.where(ispw == np.array(spwBP))[0]
                          if (len(matches3) < 1):
                              print "No spw match found: %d not in %s" % (ispw, str(spwBP))
                      matches12 = np.intersect1d(matches1,matches2)
                      if (len(matches12) < 1):
                          print "No time+antenna match between: %s and %s" % (str(matches1), str(matches2))
                      matches = np.intersect1d(matches12, matches3)
                      if (len(matches) < 1):
                          print "No time+antenna+spw match between: %s and %s" % (str(matches12), str(matches3))
                      try:
                          index = matches[0]
                          if (debug):
                              print "Match = %d ***********************************" % (index)
                      except:
                          print "No match found for time=%.6f, xant=%d, ispw=%d"  % (uniqueTimes[mytime],xant,ispw)
                          print "antennasBP = %s" % (str(antennasBP))
                          print "cal_desc_idBP = %s" % (str(cal_desc_idBP))
                          timesBPstring = 'timesBP = '
                          for i in timesBP:
                              timesBPstring += "%.6f, " % i
                          print timesBPstring
                          return()
                      validDomain = [frequencyLimits[0,index], frequencyLimits[1,index]]
                      cc = calcChebyshev(polynomialAmplitude[index][0:nPolyAmp[index]], validDomain, frequenciesGHz[index]*1e+9)
                      fa = np.array(frequenciesGHz[index])
                      if (xfrequencies[0] < xfrequencies[-1]):
                          matches = np.where(fa>xfrequencies[0])[0]
                          matches2 = np.where(fa<xfrequencies[-1])[0]
                      else:
                          matches = np.where(fa>xfrequencies[-1])[0]
                          matches2 = np.where(fa<xfrequencies[0])[0]
                      if (len(matches) < 1):
                          print "looking for %f-%f GHz inside %f-%f" % (xfrequencies[0],xfrequencies[-1],fa[0],fa[-1])
                      amplitudeSolutionX = np.mean(gampx)*(cc-np.mean(cc)+1)
  
                      cc = calcChebyshev(polynomialAmplitude[index][nPolyAmp[index]:2*nPolyAmp[index]], validDomain, frequenciesGHz[index]*1e+9)
                      if (nPolarizations > 1):
                        if (yfrequencies[0] < yfrequencies[-1]):
                          matches = np.where(fa>yfrequencies[0])[0]
                          matches2 = np.where(fa<yfrequencies[-1])[0]
                        else:
                          matches = np.where(fa>yfrequencies[-1])[0]
                          matches2 = np.where(fa<yfrequencies[0])[0]
                        amplitudeSolutionY = np.mean(gampy)*(cc-np.mean(cc)+1)
                      if (bpolyOverlay2):
                          validDomain = [frequencyLimits2[0,index], frequencyLimits2[1,index]]
                          cc = calcChebyshev(polynomialAmplitude2[index][0:nPolyAmp2[index]],
                                             validDomain, frequenciesGHz2[index]*1e+9)
                          fa = np.array(frequenciesGHz2[index])
                          if (xfrequencies[0] < xfrequencies[-1]):
                              matches = np.where(fa>xfrequencies[0])[0]
                              matches2 = np.where(fa<xfrequencies[-1])[0]
                          else:
                              matches = np.where(fa>xfrequencies[-1])[0]
                              matches2 = np.where(fa<xfrequencies[0])[0]
                          amplitudeSolution2X = np.mean(gampx)*(cc-np.mean(cc)+1)
  
                          cc = calcChebyshev(polynomialAmplitude2[index][nPolyAmp2[index]:2*nPolyAmp2[index]],
                                             validDomain, frequenciesGHz2[index]*1e+9)
                          fa = np.array(frequenciesGHz2[index])
                          if (yfrequencies[0] < yfrequencies[-1]):
                              matches = np.where(fa>yfrequencies[0])[0]
                              matches2 = np.where(fa<yfrequencies[-1])[0]
                          else:
                              matches = np.where(fa>yfrequencies[-1])[0]
                              matches2 = np.where(fa<yfrequencies[0])[0]
                          amplitudeSolution2Y = np.mean(gampy)*(cc-np.mean(cc)+1)
  
                          pb.hold(True)
                          for p in range(nPolarizations):
                              if (corrTypeToString(corr_type[p]) in polsToPlot):
                                  pb.plot(pfrequencies[p], gamp[p],'%s%s'%(pcolor[p],ampmarkstyle), markersize=markersize)
                                  newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp[p], sideband,plotrange,xchannels)
                          if (corrTypeToString(corr_type[0]) in polsToPlot):
                              pb.plot(frequenciesGHz[index], amplitudeSolutionX,'%s%s'%(p2color[0],bpolymarkstyle))
                              newylimits = recalcYlimitsFreq(chanrange, newylimits, amplitudeSolutionX, sideband,plotrange,xchannels)
                              pb.plot(frequenciesGHz2[index], amplitudeSolution2X, '%s%s'%(p3color[0],bpolymarkstyle))
                              newylimits = recalcYlimitsFreq(chanrange, newylimits, amplitudeSolution2X, sideband,plotrange,xchannels2)
                          if (nPolarizations == 2):
                             if (corrTypeToString(corr_type[1]) in polsToPlot):
                                pb.plot(frequenciesGHz[index], amplitudeSolutionY,'%s%s'%(p2color[1],bpolymarkstyle))
                                pb.plot(frequenciesGHz2[index], amplitudeSolution2Y, '%s%s'%(p3color[1],bpolymarkstyle))
                      else:
                          pb.hold(True)
                          for p in range(nPolarizations):
                              if (corrTypeToString(corr_type[p]) in polsToPlot):
                                  pb.plot(pfrequencies[p], gamp[p],'%s%s'%(pcolor[p],ampmarkstyle), markersize=markersize)
                                  newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp[p], sideband,plotrange,xchannels)
                          if (corrTypeToString(corr_type[0]) in polsToPlot):
                              pb.plot(frequenciesGHz[index], amplitudeSolutionX,'%s%s'%(p2color[0],bpolymarkstyle))
                              newylimits = recalcYlimitsFreq(chanrange, newylimits, amplitudeSolutionX, sideband,plotrange,xchannels)
                          if (nPolarizations == 2):
                             if (corrTypeToString(corr_type[1]) in polsToPlot):
                                pb.plot(frequenciesGHz[index], amplitudeSolutionY,'%s%s'%(p2color[1],bpolymarkstyle))
                                newylimits = recalcYlimitsFreq(chanrange, newylimits, amplitudeSolutionY, sideband,plotrange,ychannels)
                      # endif (bpolyOverlay2)
                  else:
                      # we are not overlaying any B or polynomial solutions      'amp vs. freq'
                      if (showflagged):
                          # Also show the flagged data to see where the flags are
                          pb.hold(True)  # Matches line 2326 for xaxis='chan'
                          for p in range(nPolarizations):
                            if (corrTypeToString(corr_type[p]) in polsToPlot):
                              if (overlayAntennas or overlayTimes):
                                pdesc1 = pb.plot(pfrequencies[p], gamp[p], '%s'%ampmarkstyles[p], markersize=markersize)
                                newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp[p], sideband,plotrange,xchannels)
                                if (overlayAntennas and overlayTimes==False):
                                    pb.setp(pdesc1, color=overlayColors[xctr])
                                elif (overlayTimes and overlayAntennas==False):
                                    pb.setp(pdesc1, color=overlayColors[mytime])
                                elif (overlayTimes and overlayAntennas): # try to support antenna,time
                                    if (myUniqueTime != []):
                                        pb.setp(pdesc1, color=overlayColors[myUniqueTime])
                                        # The third 'or' below is needed if pol='0' is flagged on antenna 0. -- 2012/10/12 (original spot)
                                        if (p==0 or len(polsToPlot)==1 or myUniqueColor==[]):
                                            myUniqueColor.append(overlayColors[len(myUniqueColor)])
                                        pb.setp(pdesc1, color=myUniqueColor[-1])
                              else:
                                pb.plot(pfrequencies[p], gamp[p], '%s%s'%(pcolor[p],ampmarkstyles[p]), markersize=markersize)
                                newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp[p], sideband,plotrange,xchannels)
                      else:   # showing only unflagged data    'amp vs. freq'
                          pb.hold(True)
                          for p in range(nPolarizations):
                            if (debug):
                                print "p=%d, polsToPlot=%s, len(fieldsToPlot)=%d, len(timerangeList)=%d, myUniqueTime=%s" % (p,str(polsToPlot),len(fieldsToPlot),len(timerangeList), str(myUniqueTime))
                            if (corrTypeToString(corr_type[p]) in polsToPlot):
                              if (len(gamp[p]) == 0):  # Try this on Apr 2, 2012
# #                                print "=============== Skipping flagged data on antenna %d = %s" % (xant,antstring)
                                  continue
                              if (overlayAntennas or overlayTimes):
                                pdesc = pb.plot(pfrequencies[p], gamp[p], '%s'%ampmarkstyles[p], markersize=markersize)
                                newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp[p], sideband,plotrange,xchannels)
                                if (overlayAntennas and overlayTimes==False):
                                    pb.setp(pdesc, color=overlayColors[xctr])
                                elif (overlayTimes and overlayAntennas==False):
                                    pb.setp(pdesc, color=overlayColors[mytime])
                                elif (overlayTimes and overlayAntennas):     #  try to support antenna,time
                                    if (myUniqueTime != []):
                                        pb.setp(pdesc, color=overlayColors[myUniqueTime])
                                        # The third 'or' below is needed if pol='0' is flagged on antenna 0. -- 2012/10/12 (original spot)
                                        if (p==0 or len(polsToPlot)==1 or myUniqueColor==[]):
                                            myUniqueColor.append(overlayColors[len(myUniqueColor)])
                                        if (debug):
                                            print "myUniqueColor = %s" % (str(myUniqueColor))
                                        pb.setp(pdesc, color=myUniqueColor[-1])
                              else:
                                 if (corrTypeToString(corr_type[p]) in polsToPlot):
                                    # since there is no overlay, don't use dashed line, so zero ------v
                                    pb.plot(pfrequencies[p], gamp[p], '%s%s'%(pcolor[p],ampmarkstyles[0]),markersize=markersize)
                                    newylimits = recalcYlimitsFreq(chanrange, newylimits, gamp[p], sideband,plotrange,xchannels)
# #                        print "newylimits for amp = ", newylimits
                          if (sum(xflag)>0):
# #                            print "amp: Resetting xaxis frequency range to counteract flagged data"
                              xrange = np.max(frequencies)-np.min(frequencies)
                              SetNewXLimits([np.min(frequencies)-0.15*xrange, np.max(frequencies)+0.15*xrange])
                              
                  if (1==1 or (xframe in bottomRowFrames) or (xctr+1==len(antennasToPlot) and ispw==spwsToPlot[-1])):
                      # use 1==1 because spw might change between top row and bottom row of frames
                      pb.xlabel(xlabelString, size=mysize)
              # endif (xaxis=='chan' elif xaxis=='freq'  for 'amp')
              if (overlayTimes):
                  timeString =''
              else:
                  if (len(uniqueTimes) > mytime):
                      timeString = ',  t%d/%d  %s' % (mytime,nUniqueTimes-1,utstring(uniqueTimes[mytime],3))
              if (ispw==originalSpw[ispw]):
                  if (overlayTimes and len(fieldsToPlot) > 1):
                        indices = fstring = ''
                        for f in fieldIndicesToPlot:
                            if (f != fieldIndicesToPlot[0]):
                                indices += ','
                                fstring += ','
                            indices += str(uniqueFields[f])
                            if (msFound):
                                fstring += msFields[uniqueFields[f]]
                        if (len(fstring) > fstringLimit):
                              fstring = fstring[0:fstringLimit] + '...'
                        titleString = "%sspw%2d,  fields %s: %s%s" % (antennaString,ispw,
                                  indices, fstring, timeString)
                  else:
                        titleString = "%sspw%2d,  field %d: %s%s" % (antennaString,ispw,uniqueFields[fieldIndex],fieldString,timeString)
              else:
                  if (overlayTimes and len(fieldsToPlot) > 1):
                      indices = fstring = ''
                      for f in fieldIndicesToPlot:
                          if (f != fieldIndicesToPlot[0]):
                              indices += ','
                              fstring += ','
                          indices += str(uniqueFields[f])
                          if (msFound):
                              fstring += msFields[uniqueFields[f]]
                      if (len(fstring) > fstringLimit):
                              fstring = fstring[0:fstringLimit] + '...'
                      titleString = "%sspw%2d (%d),  fields %s: %s%s" % (antennaString,ispw,originalSpw[ispw],
                                  indices, fstring, timeString)
                  else:
                      titleString = "%sspw%2d (%d),  field %d: %s%s" % (antennaString,ispw,originalSpw[ispw],uniqueFields[fieldIndex],fieldString,timeString)
              pb.title(titleString, size=titlesize)
              if (abs(plotrange[0]) > 0 or abs(plotrange[1]) > 0):
                  SetNewXLimits([plotrange[0],plotrange[1]])
              else:
                  # Here is 1st place where we eliminate white space on right and left edge of the plots: 'amp'
                  if (xaxis.find('chan')>=0):
                      SetNewXLimits([channels[0],channels[-1]])
                  else:
                      if (zoom != 'intersect'):
                          SetNewXLimits([frequencies[0], frequencies[-1]])
                      if (bOverlay):
                          if (xrange2 > xrange+0.1 and zoom != 'intersect'):
                              TDMisSecond = True
              if (abs(plotrange[2]) > 0 or abs(plotrange[3]) > 0):
                  SetNewYLimits([plotrange[2],plotrange[3]])
  
              ResizeFonts(adesc,mysize)
              adesc.xaxis.grid(True,which='major')
              adesc.yaxis.grid(True,which='major')
              pb.ylabel(yAmplitudeLabel, size=mysize)
              pb.subplots_adjust(hspace=myhspace, wspace=mywspace)
              xlim = pb.xlim()
              ylim = pb.ylim()
              xrange = xlim[1]-xlim[0]
              yrange = ylim[1]-ylim[0]
# #            print "amp: ylim, yrange = ",  ylim, yrange
              if (overlayAntennas == False and overlayTimes == False and bOverlay == False):
                  # draw polarization labels for no overlay
                  x0 = xstartPolLabel
                  y0 = ystartPolLabel
                  for p in range(nPolarizations):
                     if (corrTypeToString(corr_type[p]) in polsToPlot):
                        pb.text(x0, y0-subplotRows*p*0.03, corrTypeToString(corr_type[p]),
                                color=pcolor[p],size=mysize, transform=pb.gca().transAxes)
                        if (channeldiff > 0):
                            pb.text(x0, ystartMadLabel-0.03*subplotRows*p,
                                    corrTypeToString(corr_type[p])+' MAD = %.4f'%(gamp_mad[p]['mad']),
                                    color=pcolor[p],size=mysize, transform=pb.gca().transAxes)
                  if (xframe == firstFrame):
                        # draw title including caltable name
                        caltableList = caltableTitle
                        if (bpolyOverlay):
                              caltableList += ', ' + caltable2 + ' (degamp=%d, degphase=%d)'%(nPolyAmp[index]-1,nPolyPhase[index]-1)
                              if (bpolyOverlay2):
                                    caltableList += ', ' + caltable3 + ' (degamp=%d, degphase=%d)'%(nPolyAmp2[index]-1,nPolyPhase2[index]-1)
                        pb.text(xstartTitle, ystartTitle, caltableList, size=titlesize,
                                color='k', transform=pb.gcf().transFigure)
  
              elif (overlayAntennas==True and xant==antennasToPlot[-1] and bOverlay == False   # ):
                    and overlayTimes==False):  # try to support antenna,time  avoid antenna labels 'phase'
                      # We do this last, because by then, the limits will be stable.
                      x0 = xstartPolLabel
                      y0 = ystartPolLabel
                      # draw polarization labels
                      if (corrTypeToString(corr_type[0]) in polsToPlot):
                        if (channeldiff > 0):
                            pb.text(x0, ystartMadLabel-0.03*subplotRows*0,
                                    corrTypeToString(corr_type[0])+' MAD = %.4f'%(gamp_mad[0]['mad']),
                                    color=overlayColors[0],size=mysize, transform=pb.gca().transAxes)
                        if (ampmarkstyle.find('-')>=0):
                            pb.text(x0, y0, corrTypeToString(corr_type[0])+' solid', color=overlayColors[0],size=mysize,
                                    transform=pb.gca().transAxes)
                        else:
                            pb.text(x0+0.02, y0, corrTypeToString(corr_type[0]), color=overlayColors[0],size=mysize,
                                    transform=pb.gca().transAxes)
                            pdesc = pb.plot([x0-0.01], [y0], '%sk'%ampmarkstyle, markersize=markersize,
                                            scalex=False,scaley=False, transform=pb.gca().transAxes)
                      if (len(corr_type) > 1):
                       if (corrTypeToString(corr_type[1]) in polsToPlot):
                        if (channeldiff > 0):
                            pb.text(x0, ystartMadLabel-0.03*subplotRows*1,
                                    corrTypeToString(corr_type[1])+' MAD = %.4f'%(gamp_mad[1]['mad']),
                                    color=overlayColors[0],size=mysize, transform=pb.gca().transAxes)
                        if (ampmarkstyle2.find('--')>=0):
                          pb.text(x0, y0-0.03*subplotRows, corrTypeToString(corr_type[1])+' dashed',
                                  color=overlayColors[0],size=mysize, transform=pb.gca().transAxes)
                        else:
                          pb.text(x0+0.02, y0-0.03*subplotRows, corrTypeToString(corr_type[1]),
                                  color=overlayColors[0],size=mysize, transform=pb.gca().transAxes)
                          pdesc = pb.plot([x0-0.01], [y0-0.03*subplotRows], '%sk'%ampmarkstyle2,
                                          markersize=markersize, scalex=False,scaley=False)
                      if (xframe == firstFrame):
                          # draw title including caltable name
                          pb.text(xstartTitle, ystartTitle, caltableTitle, size=titlesize, color='k',
                                  transform=pb.gcf().transFigure)
                          DrawAntennaNames(msAnt, antennasToPlot, msFound, mysize)
              elif (overlayTimes==True and bOverlay == False
                    and overlayAntennas==False):  # try to support antenna,time
                  doneOverlayTime = True  # assumed until proven otherwise in the 'for' loop
                  for f in fieldIndicesToPlot:
                    if (len(uniqueTimesPerFieldPerSpw[ispwInCalTable][f]) > 0):
                      if ((uniqueTimes[mytime] < uniqueTimesPerFieldPerSpw[ispwInCalTable][f][-1]-solutionTimeThresholdSeconds) and
                          (uniqueTimes[mytime] < timerangeListTimes[-1])):
                          if (debug):
                              print "-----------Not done because %.0f < %.0f-%d for fieldIndex=%d and <%.0f" % (uniqueTimes[mytime], uniqueTimesPerFieldPerSpw[ispwInCalTable][f][-1], solutionTimeThresholdSeconds, f, timerangeListTimes[-1])
                              print "-----------ispwInCalTable=%d, mytime=%d, len(uniqueTimes) = %d" % (ispwInCalTable, mytime, len(uniqueTimes))
                          doneOverlayTime = False
                  if (debug):
                      print "------doneOverlayTime = %s" % (str(doneOverlayTime))
                  if (doneOverlayTime):
                  # either it is the last time of any times in solution, or the last time in the list of times to plot
                      if (debug):
                          print "*** on last time = %d for last fieldIndex %d  or %d>=%d" % (mytime,fieldIndex,mytime,timerangeList[-1])
                      mytime = nUniqueTimes-1
                      # We do this last, because by then, the limits will be broad enought and stable.
                      # draw polarization labels
                      DrawPolarizationLabelsForOverlayTime(xstartPolLabel,ystartPolLabel,corr_type,polsToPlot,
                                                           channeldiff,ystartMadLabel,subplotRows,gamp_mad,mysize,
                                                           ampmarkstyle,markersize,ampmarkstyle2)
                      if (xframe == firstFrame):
                          # draw title including caltable name
                          pb.text(xstartTitle, ystartTitle, caltableTitle, size=titlesize,
                                  color='k', transform=pb.gcf().transFigure)
                          drawOverlayTimeLegends(xframe,firstFrame,xstartTitle,ystartTitle,
                                                 caltable,titlesize,fieldIndicesToPlot,
                                                 ispwInCalTable,uniqueTimesPerFieldPerSpw,
                                                 timerangeListTimes, solutionTimeThresholdSeconds,
                                                 debugSloppyMatch,ystartOverlayLegend,debug,mysize,
                                                 fieldsToPlot,myUniqueColor,timeHorizontalSpacing,
                                                 fieldIndex,overlayColors, antennaVerticalSpacing,
                                                 overlayAntennas, timerangeList, caltableTitle)
              elif (overlayAntennas and overlayTimes):  # Oct 23, 2012
                  # This will only happen for overlay='antenna,time'
                  if (xframe == firstFrame and mytime == 0 and xctr==firstUnflaggedAntennaToPlot and bOverlay==False):
                      # draw title including caltable name
                      pb.text(xstartTitle, ystartTitle, caltableTitle, size=titlesize, color='k',
                              transform=pb.gcf().transFigure)
                      DrawBottomLegendPageCoords(msName, uniqueTimes[mytime], mysize)
                  # Adding the following 'for' loop on Mar 13, 2013 to support the case of
                  # single time range with overlay='antenna,time'
                  if (xant==antennasToPlot[-1]):
                    doneOverlayTime = True  # assumed until proven otherwise in the 'for' loop
                    for f in fieldIndicesToPlot:
                        if (len(uniqueTimesPerFieldPerSpw[ispwInCalTable][f]) > 0):
                            if ((uniqueTimes[mytime] < uniqueTimesPerFieldPerSpw[ispwInCalTable][f][-1]-solutionTimeThresholdSeconds) and
                                (uniqueTimes[mytime] < timerangeListTimes[-1])):
                                if (debug):
                                    print "-----------Not done because %.0f < %.0f-%d for fieldIndex=%d and <%.0f" % (uniqueTimes[mytime], uniqueTimesPerFieldPerSpw[ispwInCalTable][f][-1], solutionTimeThresholdSeconds, f, timerangeListTimes[-1])
                                    print "-----------ispwInCalTable=%d, mytime=%d, len(uniqueTimes) = %d" % (ispwInCalTable, mytime, len(uniqueTimes))
                                doneOverlayTime = False
                    if (doneOverlayTime):
                        # This is necessary for the case that no antennas were flagged for the single timerange selected
                        drawOverlayTimeLegends(xframe,firstFrame,xstartTitle,ystartTitle,caltable,titlesize,
                                               fieldIndicesToPlot,ispwInCalTable,uniqueTimesPerFieldPerSpw,
                                               timerangeListTimes, solutionTimeThresholdSeconds,
                                               debugSloppyMatch,ystartOverlayLegend,debug,mysize,
                                               fieldsToPlot,myUniqueColor,timeHorizontalSpacing,
                                               fieldIndex,overlayColors, antennaVerticalSpacing,
                                               overlayAntennas, timerangeList, caltableTitle)

  
              # Here is 2nd place where we eliminate any white space on the right and left edge of the plots: 'amp'
              # 
              if (abs(plotrange[2]) > 0 or abs(plotrange[3]) > 0):
                  SetNewYLimits([plotrange[2],plotrange[3]])
              if (plotrange[0]==0 and plotrange[1]==0):
                  if (xaxis.find('chan')>=0):
                      SetNewXLimits([channels[0],channels[-1]])
                  else:
                      if (zoom != 'intersect'):
                          SetNewXLimits([frequencies[0], frequencies[-1]])
                      if (bOverlay):
# #                        print "Checking if %f >= %f" % (xrange2, xrange)
                          if (xrange2 >= xrange and zoom != 'intersect'):
                              # This is necessary if caltable2=TDM and caltable=FDM
                              SetNewXLimits([frequencies2[0], frequencies2[-1]])
                          if (xrange2 > xrange+0.1 and zoom != 'intersect'):
                              TDMisSecond = True
              else:
                  SetNewXLimits([plotrange[0], plotrange[1]])
  
              # I need the following line for chanrange to work
              if (chanrange[0] != 0 or chanrange[1] != 0):
                  SetLimits(plotrange, chanrange, newylimits, channels, frequencies, pfrequencies, ampMin, ampMax, xaxis,pxl)
  
              # Finally, draw the atmosphere and FDM windows, if requested.
              if ((overlayAntennas==False and overlayTimes==False) or
                  (overlayAntennas==True and overlayTimes==False and xant==antennasToPlot[-1]) or
                  (overlayTimes==True and overlayAntennas==False and doneOverlayTime) or
                  (xant==antennasToPlot[-1] and doneOverlayTime) # support showatm with overlay='antenna,time'
                  ):
                  if ((showatm or showtsky) and len(atmString) > 0): 
                      DrawAtmosphere(showatm, showtsky, subplotRows, atmString,
                                     mysize, TebbSky, plotrange, xaxis, atmchan,
                                     atmfreq, transmission, subplotCols,
                                     showatmPoints=showatmPoints, xframe=xframe, channels=channels)
                      if (LO1 != ''):
                          # Now draw the image band
                          DrawAtmosphere(showatm,showtsky, subplotRows, atmString,
                              mysize, TebbSkyImage, plotrange, xaxis,
                              atmchanImage, atmfreqImage, transmissionImage,
                              subplotCols, LO1, xframe, firstFrame, showatmPoints, channels=channels)
                  if (xaxis.find('freq')>=0 and showfdm and nChannels <= 256):
                      if (tableFormat == 33):
                          showFDM(originalSpw_casa33, chanFreqGHz_casa33)
                      else:
                          showFDM(originalSpw, chanFreqGHz)
  
              if (bOverlay):
                  # draw polarization labels
                  x0 = xstartPolLabel
                  y0 = ystartPolLabel
                  for p in range(nPolarizations):
                      if (corrTypeToString(corr_type[p]) in polsToPlot):
                          pb.text(x0, y0-p*0.03*subplotRows, corrTypeToString(corr_type[p])+'-c1',
                                  color=pcolor[p],size=mysize,transform=pb.gca().transAxes)
                          pb.text(x0, y0-p*0.03*subplotRows-0.06*subplotRows, corrTypeToString(corr_type[p])+'-c2',
                                  color=p2color[p],size=mysize,transform=pb.gca().transAxes)
              if (bpolyOverlay and xaxis.find('freq')>=0):
                  # draw polarization labels
                  x0 = xstartPolLabel
                  y0 = ystartPolLabel
                  if (x2color != xcolor):
                        for p in range(nPolarizations):
                            if (corrTypeToString(corr_type[0]) in polsToPlot):
                                pb.text(x0+0.1, y0-p*0.03*subplotRows, corrTypeToString(corr_type[p]), color=p2color[p],
                                        size=mysize,transform=pb.gca().transAxes)
                  if (bpolyOverlay2):
                        for p in range(nPolarizations):
                              if (corrTypeToString(corr_type[0]) in polsToPlot):
                                    pb.text(x0+0.2, y0-p*0.03*subplotRows, corrTypeToString(corr_type[p]),
                                            color=p3color[p], size=mysize,transform=pb.gca().transAxes)
                  
# #            if (xframe == 111 and amplitudeWithPhase):
              myIndexTime = uniqueTimesPerFieldPerSpw[ispwInCalTable][fieldIndex][-1]
              matched,mymatch = sloppyMatch(myIndexTime,uniqueTimes,solutionTimeThresholdSeconds,whichone=True)
              if (matched == False):
                  print "---------- 1) Did not find %f in %s" % (myIndexTime,str(uniqueTimes))
                  print "Try re-running with a smaller solutionTimeThresholdSeconds (currently %f)" % (solutionTimeThresholdSeconds)
                  return
              if ((xframe == 111 and amplitudeWithPhase) or
                  # Following case is needed to make subplot=11 to work for: try to support overlay='antenna,time'
                  (xframe == lastFrame and overlayTimes and overlayAntennas and
                   xctr+1==len(antennasToPlot) and
#                   mytime+1==len(uniqueTimes) and  # this worked for nspw <= 4
                   mytime==mymatch and
                   spwctr+1<len(spwsToPlot))):
                       if (debug):
                           print "xframe=%d  ==  lastFrame=%d,  amplitudeWithPhase=%s" % (xframe, lastFrame, str(amplitudeWithPhase))
                           print "xctr+1=%d == len(antennasToPlot)=%d"  % (xctr+1,len(antennasToPlot))
                           print "mytime+1=%d == len(uniqueTimes)=%d"  % (mytime+1,len(uniqueTimes))
                           print "spwctr+1=%d < len(spwsToPlot)=%d"  % (spwctr+1,len(spwsToPlot))
                       if (len(figfile) > 0):
                             plotfiles.append(makeplot(figfile,msFound,msAnt,
                                              overlayAntennas,pages,pagectr,
                                              density,interactive,antennasToPlot,
                                              spwsToPlot,overlayTimes,3,debug))
                       donetime = timeUtilities.time()
                       if (interactive):
                          pb.draw()
# #                        myinput = raw_input(":(%.1f sec) Press return for next page (b for backwards, q to quit): "%(donetime-mytimestamp))
                          myinput = raw_input("Press return for next page (b for backwards, q to quit): ")
                       else:
                          myinput = ''
                       skippingSpwMessageSent = 0
                       mytimestamp = timeUtilities.time()
                       if (myinput.find('q') >= 0):
                           return()
                       if (myinput.find('b') >= 0):
                           if (pagectr > 0):
                               if (debug):
                                   print "Decrementing pagectr from %d to %d" % (pagectr, pagectr-1)
                               pagectr -= 1
                           else:
                               if (debug):
                                   print "Not decrementing pagectr=%d" % (pagectr)

                           redisplay = True
                           #redisplay the current page by setting ctrs back to the value they had at start of that page
                           xctr = pages[pagectr][PAGE_ANT]
                           spwctr = pages[pagectr][PAGE_SPW]
                           mytime = pages[pagectr][PAGE_TIME]
                           myap = pages[pagectr][PAGE_AP]
                           xant = antennasToPlot[xctr]
                           antstring, Antstring = buildAntString(xant,msFound,msAnt)
                           ispw = spwsToPlot[spwctr]
# #                         print "Returning to [%d,%d,%d,%d]" % (xctr,spwctr,mytime,myap)
#                           redisplay = True
                           if (xctr==pages[0][PAGE_ANT] and spwctr==pages[0][PAGE_SPW] and mytime==pages[0][PAGE_TIME] and pages[0][PAGE_AP]==myap):
                             pb.clf()
                             if (debug):
                                 print "2)Setting xframe to %d" % xframeStart
                             xframe = xframeStart
                             myUniqueColor = []
                             continue
                       else:
                           pagectr += 1
                           if (pagectr >= len(pages)):
                             pages.append([xctr,spwctr,mytime,1])
                             if (debug):
                                 print "amp: appending [%d,%d,%d,%d]" % (xctr,spwctr,mytime,1)
                             newpage = 0
                       pb.clf()
                       if (debug):
                           print "3)Setting xframe to %d" % xframeStart
                       xframe = xframeStart
                       myUniqueColor = []
###################################################
########### Here is the phase plotting ############
###################################################
          if (yaxis.find('phase')>=0 or amplitudeWithPhase) and doneOverlayTime==False:
              if (channeldiff > 0):
                  pchannels = [xchannels,ychannels]  # this is necessary because np.diff reduces nchan by 1
                  pfrequencies = [xfrequencies,yfrequencies]  # this is necessary because np.diff reduces nchan by 1
                  if (bOverlay):
                      pchannels2 = [xchannels2,ychannels2]  # this is necessary because np.diff reduces nchan by 1
                      pfrequencies2 = [xfrequencies2,yfrequencies2]  # this is necessary because np.diff reduces nchan by 1
              if (overlayTimes == False or mytime==firstTimeMatch):  
                  if (overlayAntennas==False or xctr==firstUnflaggedAntennaToPlot
                      or xctr>antennasToPlot[-1]):  # 2012-05-24, to fix the case where all ants flagged on one timerange
                      xframe += 1
# #                    print "u) incrementing xframe to %d" % xframe
                      myUniqueColor = []
                      newylimits = [LARGE_POSITIVE, LARGE_NEGATIVE]
                      if (phase != ''):
                          if ((phase[0] != 0 or phase[1] != 0) and amplitudeWithPhase):
                              newylimits = phase
              if (debug):
                  print "$$$$$$$$$$$$$$$$$$$$$$$  ready to plot phase on xframe %d" % (xframe)
              adesc = pb.subplot(xframe)
              drewAtmosphereOnFlaggedAntenna = False
              pb.hold(overlayAntennas or overlayTimes)
              gphsx = np.arctan2(np.imag(gplotx),np.real(gplotx))*180.0/math.pi
              if (nPolarizations == 2):
                  gphsy = np.arctan2(np.imag(gploty),np.real(gploty))*180.0/math.pi
                  if (channeldiff>0):
                      if (xaxis == 'chan'):
                          gphs0, newx0 = channelDifferences(gphsx, pchannels[0])
                          gphs1, newx1 = channelDifferences(gphsy, pchannels[1])
                          pchannels = [newx0,newx1]
                      else:
                          gphs0, newx0 = channelDifferences(gphsx, pfrequencies[0])
                          gphs1, newx1 = channelDifferences(gphsy, pfrequencies[1])
                          pfrequencies = [newx0,newx1]
                      gphs = [gphs0, gphs1]
                      gphs_mad = [madInfo(gphs[0],madsigma,edge), madInfo(gphs[1],madsigma,edge)]
                      for p in [0,1]:
                          madstats[Antstring][ispw][mytime][p]['phase'] = gphs_mad[p]['mad']
                          if (gphs_mad[p]['nchan'] > 0):
                              checkAbsSum = np.sum(np.abs(gphs[p]))
                              if (checkAbsSum < PHASE_ABS_SUM_THRESHOLD):
                                  if (debug): print "%s, Pol %d, spw %d, %s, phs: not printing because abs sum of all values near zero (%f)" % (Antstring, p, ispw, utstring(uniqueTimes[mytime],0), checkAbsSum)
                              else:
                                  casalogPost(debug, "%s, Pol %d, spw %2d, %s, phs: %4d points exceed %.1f sigma (worst=%.2f at chan %d)" % (Antstring, p, ispw, utstring(uniqueTimes[mytime],0), gphs_mad[p]['nchan'], madsigma, gphs_mad[p]['outlierValue'], gphs_mad[p]['outlierChannel']+pchannels[p][0]))
                  else:
                      gphs = [gphsx,gphsy]
              else:  # 1-pol
                  if (channeldiff>0):
                      if (xaxis == 'chan'):
                          gphs0, newx0 = channelDifferences(gphsx, pchannels[0])
                          pchannels = [newx0]
                      else:
                          gphs0, newx0 = channelDifferences(gphsx, pfrequencies[0])
                          pfrequencies = [newx0]
                      gphs = [gphs0]
                      p = 0
                      gphs_mad = [madInfo(gphs[p], madsigma, edge)]
                      madstats[Antstring][ispw][mytime][p]['phase'] = gphs_mad[p]['mad']
                      if (gphs_mad[p]['nchan'] > 0):
                          checkAbsSum = np.sum(np.abs(gphs[p]))
                          if (checkAbsSum < PHASE_ABS_SUM_THRESHOLD):
                              if (debug): print "%s, Pol %d, spw %d, %s, phs: not printing because all values near zero (%f)" % (Antstring, p, ispw, utstring(uniqueTimes[mytime],0), checkAbsSum)
                          else:
                              casalogPost(debug, "%s, Pol %d, spw %2d, %s, phs: %4d points exceed %.1f sigma (worst=%.2f at chan %d)" % (Antstring, p, ispw, utstring(uniqueTimes[mytime],0), gphs_mad[p]['nchan'], madsigma, gphs_mad[p]['outlierValue'], gphs_mad[p]['outlierChannel']+pchannels[p][0]))
                  else:
                      gphs = [gphsx]
              if (bOverlay):
                    if (debug):
                        print "computing phase for second table"
                    gphsx2 = np.arctan2(np.imag(gplotx2),np.real(gplotx2))*180.0/math.pi
                    if (nPolarizations == 2):
                        gphsy2 = np.arctan2(np.imag(gploty2),np.real(gploty2))*180.0/math.pi
                        if (channeldiff>0):
                            if (xaxis == 'chan'):
                                gphs2_0, newx0 = channelDifferences(gphsx2, pchannels2[0])
                                gphs2_1, newx1 = channelDifferences(gphsy2, pchannels2[1])
                                pchannels2 = [newx0, newx1]
                            else:
                                gphs2_0, newx0 = channelDifferences(gphsx2, pfrequencies2[0])
                                gphs2_1, newx1 = channelDifferences(gphsy2, pfrequencies2[1])
                                pfrequencies2 = [newx0, newx1]
                            gphs2 = [gphs2_0, gphs2_1]
                        else:
                            gphs2 = [gphsx2, gphsy2]
                    else:
                        if (channeldiff>0):
                            if (xaxis == 'chan'):
                                gphs2_0, newx0 = channelDifferences(gphsx2, pchannels2[0])
                                pchannels2 = [newx0]
                            else:
                                gphs2_0, newx0 = channelDifferences(gphsx2, pfrequencies2[0])
                                pfrequencies2 = [newx0]
                            gphs2 = [gphs2_0]
                        else:
                            gphs2 = [gphsx2]
              else:
                    if (debug):
                        print "bOverlay is FALSE ==========================="
                  
              if (xaxis.find('chan')>=0 or len(xfrequencies) < 1):    # 'phase'
                  pb.hold(True)
                  for p in range(nPolarizations):
                    if (corrTypeToString(corr_type[p]) in polsToPlot):
                      if (overlayAntennas or overlayTimes):
                          pdesc = pb.plot(pchannels[p],gphs[p],'%s'%(phasemarkstyles[p]),markersize=markersize)
                          newylimits =  recalcYlimits(plotrange,newylimits,gphs[p])  # 10/27/2011
                          if (newylimits[1]-newylimits[0] < minPhaseRange):
                              newylimits = [-minPhaseRange,minPhaseRange]
                          if (phase != ''):
                              if ((phase[0] != 0 or phase[1] != 0) and amplitudeWithPhase):
                                  newylimits = phase
  
                          if (overlayAntennas and overlayTimes==False):
                              pb.setp(pdesc, color=overlayColors[xctr])
                          elif (overlayTimes and overlayAntennas==False):
                              pb.setp(pdesc, color=overlayColors[mytime])
                          elif (overlayTimes):   # try to support antenna,time
                              if (myUniqueTime != []):
                                  pb.setp(pdesc, color=overlayColors[myUniqueTime])
                                  # The third 'or' below is needed if pol='0' is flagged on antenna 0. -- 2012/10/12 (original spot)
                                  if (p==0 or len(polsToPlot)==1 or myUniqueColor==[]):
                                      myUniqueColor.append(overlayColors[len(myUniqueColor)])
                                  pb.setp(pdesc, color=myUniqueColor[-1])
                      else:
                          pb.plot(pchannels[p],gphs[p],'%s%s'%(pcolor[p],phasemarkstyles[0]), markersize=markersize)
                          newylimits =  recalcYlimits(plotrange,newylimits,gphs[p]) # 10/27/2011
                          if (newylimits[1]-newylimits[0] < minPhaseRange):
                              newylimits = [-minPhaseRange,minPhaseRange]
                          if (phase != ''):
                              if ((phase[0] != 0 or phase[1] != 0) and amplitudeWithPhase):
                                  newylimits = phase
                  if (sum(xflag)>0):
# #                    print "phase: Resetting xaxis channel range to counteract flagged data"
                      xrange = np.max(channels)-np.min(channels)
                      SetNewXLimits([np.min(channels)-xrange/20, np.max(channels)+xrange/20])
                  if (xframe in bottomRowFrames or (xctr+1==len(antennasToPlot) and ispw==spwsToPlot[-1])):
                      pb.xlabel("Channel", size=mysize)
              elif (xaxis.find('freq')>=0):     # 'phase'
                  if (bOverlay):
                        pb.hold(True)
                        if (debug):
                            print "Preparing to plot phase from %f-%f for pols: %s" % (xfrequencies[0],xfrequencies[-1],str(polsToPlot))
                            print "Preparing to plot phase from %f-%f for pols: %s" % (pfrequencies[p][0],pfrequencies[p][-1],str(polsToPlot))
                            print "Preparing to plot phase from %f-%f for pols: %s" % (pfrequencies2[p][0],pfrequencies2[p][-1],str(polsToPlot))
                        xrange = np.abs(xfrequencies[0]-xfrequencies[-1])
                        try:
                            xrange2 = np.abs(xfrequencies2[0]-xfrequencies2[-1])
                        except:
                            print "No phase data found in second solution.  Try increasing the solutionTimeThresholdSeconds above %.0f." % (solutionTimeThresholdSeconds)
                            print "If this doesn't work, email the developer (%s)." % (developerEmail)
                            return()
                        if (np.abs(xrange/xrange2 - 1) > 0.05 + len(xflag)/len(xchannels)):  # 0.0666 is 2000/1875-1
                           # These line widths are optimal for visualizing FDM over TDM
                           width1 = 1
                           width2 = 4
                           # solutions differ in frequency width, so show the narrower one first
                           if (xrange < xrange2):
                             for p in range(nPolarizations):
                               if (corrTypeToString(corr_type[p]) in polsToPlot):
                                  if (debug): print "pb.plot 1"
                                  pb.plot(pfrequencies[p], gphs[p], '%s%s'%(pcolor[p],phasemarkstyle), linewidth=width2, markersize=markersize)
                                  newylimits = recalcYlimitsFreq(chanrange, newylimits, gphs[p], sideband,plotrange,xchannels)
                             for p in range(nPolarizations):
                               if (corrTypeToString(corr_type[p]) in polsToPlot):
                                  if (debug): print "pb.plot 2"
                                  pb.plot(pfrequencies2[p], gphs2[p], '%s%s'%(p2color[p],phasemarkstyle), linewidth=width1, markersize=markersize)
                                  newylimits = recalcYlimitsFreq(chanrange, newylimits, gphs2[p], sideband,plotrange,xchannels2)
                           else:
                             for p in range(nPolarizations):
                               if (corrTypeToString(corr_type[p]) in polsToPlot):
                                   if (debug): print "pb.plot 3"
                                   pb.plot(pfrequencies2[p], gphs2[p], '%s%s'%(p2color[p],phasemarkstyle), linewidth=width2, markersize=markersize)
                                   newylimits = recalcYlimitsFreq(chanrange, newylimits, gphs2[p], sideband,plotrange,xchannels2)
                             for p in range(nPolarizations):
                               if (corrTypeToString(corr_type[p]) in polsToPlot):
                                   if (debug): print "pb.plot 4"
                                   pb.plot(pfrequencies[p], gphs[p], '%s%s'%(pcolor[p],phasemarkstyle), linewidth=width1, markersize=markersize)
                                   newylimits = recalcYlimitsFreq(chanrange, newylimits, gphs[p], sideband,plotrange,xchannels)
                        else:
                           width1 = 1
                           width2 = 1
                           # solutions may be different level of smoothing, so plot highest rms first
                           pb.hold(True)
                           if (np.std(gphsx) < np.std(gphsx2)):
                             for p in range(nPolarizations):
                               if (corrTypeToString(corr_type[p]) in polsToPlot):
                                 if (debug): print "pb.plot 5"
                                 pb.plot(pfrequencies2[p], gphs2[p], '%s%s'%(p2color[p],phasemarkstyle), linewidth=width1, markersize=markersize)
                                 newylimits = recalcYlimitsFreq(chanrange, newylimits, gphs2[p], sideband,plotrange,xchannels2)
                             for p in range(nPolarizations):
                               if (corrTypeToString(corr_type[p]) in polsToPlot):
                                 if (debug): print "pb.plot 6"
                                 pb.plot(pfrequencies[p], gphs[p], '%s%s'%(pcolor[p],phasemarkstyle), linewidth=width2, markersize=markersize)
                                 newylimits = recalcYlimitsFreq(chanrange, newylimits, gphs[p], sideband,plotrange,xchannels)
                           else:
                             for p in range(nPolarizations):
                               if (corrTypeToString(corr_type[p]) in polsToPlot):
                                 if (debug): print "pb.plot 7"
                                 pb.plot(pfrequencies[p], gphs[p], '%s%s'%(pcolor[p],phasemarkstyle), linewidth=width2, markersize=markersize)
                                 newylimits = recalcYlimitsFreq(chanrange, newylimits, gphs[p], sideband,plotrange,xchannels)
                             for p in range(nPolarizations):
                               if (corrTypeToString(corr_type[p]) in polsToPlot):
                                 if (debug): print "pb.plot 9"
                                 pb.plot(pfrequencies2[p], gphs2[p], '%s%s'%(p2color[p],phasemarkstyle), linewidth=width1, markersize=markersize)
                                 newylimits = recalcYlimitsFreq(chanrange, newylimits, gphs2[p], sideband,plotrange,xchannels2)
                        # must set new limits after plotting  'phase'
                        (y0,y1) = pb.ylim()
                        if (y1-y0 < minPhaseRange):
                              # this must come before defining ticks 
                              SetNewYLimits([-minPhaseRange,minPhaseRange])
                        if (zoom=='intersect'):
                            if (xrange < xrange2):
                                SetNewXLimits([min(xfrequencies[0],xfrequencies[-1])-xrange*0.1, max(xfrequencies[0],xfrequencies[-1])+xrange*0.1])
                                SetLimits(plotrange, chanrange, newylimits, channels, frequencies,
                                          pfrequencies, ampMin, ampMax, xaxis,pxl)
                            else:
                                SetNewXLimits([min(xfrequencies2[0],xfrequencies2[-1])-xrange2*0.1, max(xfrequencies2[0],xfrequencies2[-1])+xrange2*0.1])
                                SetLimits(plotrange, chanrange, newylimits, channels, frequencies2,
                                          pfrequencies2, ampMin, ampMax, xaxis,pxl)
                        else:
                            if (xrange < xrange2):
                                SetLimits(plotrange, chanrange, newylimits, channels, frequencies,
                                          pfrequencies, ampMin, ampMax, xaxis,pxl)
                            else:
                                SetLimits(plotrange, chanrange, newylimits, channels, frequencies2,
                                          pfrequencies2, ampMin, ampMax, xaxis,pxl)
                        # draw polarization and spw labels
                        if (xframe == firstFrame):
                            # draw title including caltable name
                            caltableList = 'c1 = ' + caltable + ',  c2 = ' + caltable2 + ' (%s)'%(utstring(uniqueTimes2[mytime],3))
                            pb.text(xstartTitle, ystartTitle, caltableList, size=titlesize,
                                    color='k', transform=pb.gcf().transFigure)
                  elif (bpolyOverlay):
                          matches1 = []
                          for tbp in range(len(timesBP)):
                              if (sloppyMatch(uniqueTimes[mytime], timesBP[tbp], solutionTimeThresholdSeconds, myprint=debugSloppyMatch)):
                                  matches1.append(tbp)
                          matches1 = np.array(matches1)
# #                        print "time matches: matches1 = ", matches1
                          if (len(matches1) < 1):
                              print "No time match found"
                              print "If you are sure the solutions correspond to the same data, you can set solutionTimeThresholdSeconds=%.0f" % (1+np.ceil(np.abs(timesBP[0]-uniqueTimes[mytime])))
                              return()
# #                        matches1 = np.where(np.floor(uniqueTimes[mytime]) == np.floor(np.array(timesBP)))[0]
                          matches2 = np.where(xant == np.array(antennasBP))[0]
                          if (len(matches2) < 1):
                              print "No antenna match found between %s and %s" % (str(xant), str(antennasBP))
# #                        print "antenna matches: matches2 = ", matches2
  
                          if (tableFormat == 33):
                              matches3 = np.where(ispw == np.array(cal_desc_idBP))[0]
                              if (len(matches3) < 1):
                                  print "No spw match found: %d not in %s" % (ispw, str(cal_desc_idBP))
                          else:
                              matches3 = np.where(ispw == np.array(spwBP))[0]
                              if (len(matches3) < 1):
                                  print "No spw match found: %d not in %s" % (ispw, str(spwBP))
# #                        print "spw matches: matches3 = ", matches3
  
                          matches12 = np.intersect1d(matches1,matches2)
                          if (len(matches12) < 1):
                              print "No match between: %s and %s" % (str(matches1), str(matches2))
# #                        print "antenna&time matches: matches12 = ", matches12
  
                          matches = np.intersect1d(matches12, matches3)
                          if (len(matches) < 1):
                              print "No match between: %s and %s" % (str(matches12), str(matches3))
# #                        print "antenna&time&spw matches: matches = ", matches
  
                          try:
                              index = matches[0]  # holds the row number of the matching solution in the BPOLY table
                          except:
                              print "No match found for time=%.6f, xant=%d, ispw=%d"  % (uniqueTimes[mytime],xant,ispw)
                              print "antennasBP = %s" % (str(antennasBP))
                              print "cal_desc_idBP = %s" % (str(cal_desc_idBP))
                              timesBPstring = "timesBP = "
                              for i in timesBP:
                                  timesBPstring += "%.6f, " % i
                              print timesBPstring
                              return()
# #                        print "phase: Using index = %d/%d (mytime=%d), domain=%.3f,%.3f" % (index,len(polynomialPhase),mytime,frequencyLimits[0,index]*1e-9,frequencyLimits[1,index]*1e-9)
                          if (debug): print "BRowNumber = %d, BPolyRowNumber = %d"  % (BRowNumber, index)
                          validDomain = [frequencyLimits[0,index], frequencyLimits[1,index]]
                          cc = calcChebyshev(polynomialPhase[index][0:nPolyPhase[index]], validDomain, frequenciesGHz[index]*1e+9) * 180/math.pi
                          fa = np.array(frequenciesGHz[index])
                          if (xfrequencies[0] < xfrequencies[-1]):
                              matches = np.where(fa>xfrequencies[0])[0]
                              matches2 = np.where(fa<xfrequencies[-1])[0]
                          else:
                              matches = np.where(fa>xfrequencies[-1])[0]
                              matches2 = np.where(fa<xfrequencies[0])[0]
# #                        print "xfrequencies[0] = %f, xfrequencies[-1] = %f" % (xfrequencies[0], xfrequencies[-1])
# #                        print "len(matches)=%d, len(matches2)=%d" % (len(matches), len(matches2))
# #                        print "fa = ", fa
                          mymean = complexMeanDeg(np.array(cc)[matches[0]:matches2[-1]+1])
                          phaseSolutionX = np.mean(gphsx) - mymean + cc
  
                          cc = calcChebyshev(polynomialPhase[index][nPolyPhase[index]:2*nPolyPhase[index]], validDomain, frequenciesGHz[index]*1e+9) * 180/math.pi
                          if (nPolarizations > 1):
                            if (yfrequencies[0] < yfrequencies[-1]):
                              matches = np.where(fa>yfrequencies[0])[0]
                              matches2 = np.where(fa<yfrequencies[-1])[0]
                            else:
                              matches = np.where(fa>yfrequencies[-1])[0]
                              matches2 = np.where(fa<yfrequencies[0])[0]
                            mymean = complexMeanDeg(np.array(cc)[matches[0]:matches2[-1]+1])
                            phaseSolutionY = np.mean(gphsy) - mymean + cc
                          if (bpolyOverlay2):
                              validDomain = [frequencyLimits2[0,index], frequencyLimits2[1,index]]
                              cc = calcChebyshev(polynomialPhase2[index][0:nPolyPhase2[index]], validDomain, frequenciesGHz2[index]*1e+9) * 180/math.pi
                              fa = np.array(frequenciesGHz2[index])
                              if (xfrequencies[0] < xfrequencies[-1]):
                                  matches = np.where(fa>xfrequencies[0])[0]
                                  matches2 = np.where(fa<xfrequencies[-1])[0]
                              else:
                                  matches = np.where(fa>xfrequencies[-1])[0]
                                  matches2 = np.where(fa<xfrequencies[0])[0]
                              mymean = complexMeanDeg(np.array(cc)[matches[0]:matches2[-1]+1])
                              phaseSolution2X = np.mean(gphsx) + cc - mymean
  
                              cc = calcChebyshev(polynomialPhase2[index][nPolyPhase2[index]:2*nPolyPhase2[index]], validDomain, frequenciesGHz2[index]*1e+9) * 180/math.pi
                              if (yfrequencies[0] < yfrequencies[-1]):
                                  matches = np.where(fa>yfrequencies[0])[0]
                                  matches2 = np.where(fa<yfrequencies[-1])[0]
                              else:
                                  matches = np.where(fa>yfrequencies[-1])[0]
                                  matches2 = np.where(fa<yfrequencies[0])[0]
                              mymean = complexMeanDeg(np.array(cc)[matches[0]:matches2[-1]+1])
                              phaseSolution2Y = np.mean(gphsy) + cc - mymean
                              pb.hold(True)
                              for p in range(nPolarizations):
                                  if (corrTypeToString(corr_type[p]) in polsToPlot):
                                      pb.plot(pfrequencies[p], gphs[p],'%s%s' % (pcolor[p],phasemarkstyle), markersize=markersize)
                                      newylimits = recalcYlimitsFreq(chanrange, newylimits, gphs[p], sideband,plotrange,xchannels)
                              if (corrTypeToString(corr_type[0]) in polsToPlot):
                                  pb.plot(frequenciesGHz[index],phaseSolutionX,'%s%s'%(x2color,bpolymarkstyle))
                                  newylimits = recalcYlimitsFreq(chanrange, newylimits, phaseSolutionX, sideband,plotrange,xchannels)
                                  pb.plot(frequenciesGHz2[index],phaseSolution2X,'%s%s'%(x3color,bpolymarkstyle))
                                  newylimits = recalcYlimitsFreq(chanrange, newylimits, phaseSolution2X, sideband,plotrange,xchannels2)
                              if (nPolarizations == 2):
                                 if (corrTypeToString(corr_type[1]) in polsToPlot):
                                    pb.plot(frequenciesGHz[index],phaseSolutionY,'%s%s'%(y2color,bpolymarkstyle))
                                    newylimits = recalcYlimitsFreq(chanrange, newylimits, phaseSolutionY, sideband,plotrange,xchannels)
                                    pb.plot(frequenciesGHz2[index],phaseSolution2Y,'%s%s'%(y3color,bpolymarkstyle))
                                    newylimits = recalcYlimitsFreq(chanrange, newylimits, phaseSolution2Y, sideband,plotrange,xchannels2)
                          else:
                              pb.hold(True)
                              for p in range(nPolarizations):
                                  if (corrTypeToString(corr_type[p]) in polsToPlot):
                                      pb.plot(pfrequencies[p], gphs[p],'%s%s'%(pcolor[p],phasemarkstyle), markersize=markersize)
                                      newylimits = recalcYlimitsFreq(chanrange, newylimits, gphs[p], sideband,plotrange,xchannels)
                              if (corrTypeToString(corr_type[0]) in polsToPlot):
                                 pb.plot(frequenciesGHz[index],phaseSolutionX,'%s%s'%(x2color,bpolymarkstyle))
                                 newylimits = recalcYlimitsFreq(chanrange, newylimits, phaseSolutionX, sideband,plotrange,xchannels)
                              if (nPolarizations == 2):
                                 if (corrTypeToString(corr_type[1]) in polsToPlot):
                                    pb.plot(frequenciesGHz[index],phaseSolutionY,'%s%s'%(y2color,bpolymarkstyle))
                                    newylimits = recalcYlimitsFreq(chanrange, newylimits, phaseSolutionY, sideband,plotrange,xchannels)
                          # endif (bpolyOverlay2)
                          # Adding the following 4 lines on March 14, 2013
                          (y0,y1) = pb.ylim()
                          if (y1-y0 < minPhaseRange):
                              # this must come before defining ticks 
                              SetNewYLimits([-minPhaseRange,minPhaseRange])
                  else:
                      # we are not overlaying any B or polynomial solutions   'phase vs. freq'
                      pb.hold(True)
                      for p in range(nPolarizations):
                          if (corrTypeToString(corr_type[p]) in polsToPlot):
                              if (overlayAntennas or overlayTimes):
                                pdesc = pb.plot(pfrequencies[p], gphs[p],'%s'%(phasemarkstyles[p]), markersize=markersize)
                                newylimits = recalcYlimitsFreq(chanrange, newylimits, gphs[p], sideband,plotrange,xchannels) # Apr 2, 2012
                                if (overlayAntennas and overlayTimes==False):
                                    pb.setp(pdesc, color=overlayColors[xctr])
                                elif (overlayTimes and overlayAntennas==False):
                                    pb.setp(pdesc, color=overlayColors[mytime])
                                elif (overlayTimes): # try to support antenna,time
                                    if (myUniqueTime != []):
                                        pb.setp(pdesc, color=overlayColors[myUniqueTime])
                                        # The third 'or' below is needed if pol='0' is flagged on antenna 0. -- 2012/10/12 (original spot)
                                        if (p==0 or len(polsToPlot)==1 or myUniqueColor==[]):
                                            myUniqueColor.append(overlayColors[len(myUniqueColor)])
                                        pb.setp(pdesc, color=myUniqueColor[-1])
                              else:
                                pb.plot(pfrequencies[p], gphs[p],'%s%s'%(pcolor[p],phasemarkstyles[0]), markersize=markersize)
                                newylimits = recalcYlimitsFreq(chanrange, newylimits, gphs[p], sideband, plotrange,xchannels)
                          if (sum(xflag)>0):
# #                            print "phase frame %d: Resetting xaxis frequency range to counteract flagged data" % (xframe)
                              xrange = np.max(frequencies)-np.min(frequencies)
                              SetNewXLimits([np.min(frequencies)-0.15*xrange, np.max(frequencies)+0.15*xrange])
                          if (len(gphs[p]) > 0):
                              if (np.max(gphs[p]) < minPhaseRange and np.min(gphs[p]) > -minPhaseRange):
                                  SetNewYLimits([-minPhaseRange,minPhaseRange])
                  #endif bOverlay
  
                  if (1==1):
                      pb.xlabel(xlabelString, size=mysize)
              #endif xaxis='chan'/freq  for 'phase'
              if (overlayTimes):
                  timeString =''
              else:
                  timeString = ',  t%d/%d  %s' % (mytime+1,nUniqueTimes,utstring(uniqueTimes[mytime],3))
              if (ispw==originalSpw[ispw]):
                    titleString = "%sspw%2d,  field %d: %s%s" % (antennaString,ispw,
                                                                uniqueFields[fieldIndex],fieldString,timeString)
              else:
                    titleString = "%sspw%2d (%d),  field %d: %s%s" % (antennaString,ispw,originalSpw[ispw],
                                                                uniqueFields[fieldIndex],fieldString,timeString)
              pb.title(titleString,size=titlesize)
              if (abs(plotrange[0]) > 0 or abs(plotrange[1]) > 0):
                  SetNewXLimits([plotrange[0],plotrange[1]])
  
              # Here is 1st place where we eliminate any white space on the right and left edge of the plots: 'phase'
              else:
                  if (xaxis.find('chan')>=0):
                      SetNewXLimits([channels[0],channels[-1]])
                  else:
                      if (zoom != 'intersect'):
                          SetNewXLimits([frequencies[0], frequencies[-1]])
                      if (bOverlay):
                          if (xrange2 > xrange+0.1 and zoom != 'intersect'):
                              TDMisSecond = True
  
              if (abs(plotrange[2]) > 0 or abs(plotrange[3]) > 0):
                  if (amplitudeWithPhase == False or phase == ''):
                      SetNewYLimits([plotrange[2],plotrange[3]])
              if (amplitudeWithPhase and phase != ''):
                  if (phase[0] != 0 or phase[1] != 0):
                      SetNewYLimits(phase)
                  
  
              (y0,y1) = pb.ylim()
              if (y1-y0 < minPhaseRange):
                    # this must come before defining ticks
                    SetNewYLimits([-minPhaseRange,minPhaseRange])
                    SetNewYLimits(newylimits)  # added 10/2/2012 for the case of only 1 data point
              if (amplitudeWithPhase and phase != ''):
                  if (phase[0] != 0 or phase[1] != 0):
                      SetNewYLimits(phase)
              (y0,y1) = pb.ylim()
              ResizeFonts(adesc,mysize)
              adesc.xaxis.grid(True,which='major')
              adesc.yaxis.grid(True,which='major')
              pb.ylabel(yPhaseLabel, size=mysize)
              pb.subplots_adjust(hspace=myhspace, wspace=mywspace)
              ylim = pb.ylim()
              xlim = pb.xlim()
              xrange = xlim[1]-xlim[0]
              yrange = ylim[1]-ylim[0]
# #            print "phase: ylim, yrange = ",  ylim, yrange
              myap = 0
              if (overlayAntennas == False and overlayTimes == False and bOverlay == False):
                  # draw polarization labels
                  x0 = xstartPolLabel
                  y0 = ystartPolLabel
                  for p in range(nPolarizations):
                        if (corrTypeToString(corr_type[p]) in polsToPlot):
                            pb.text(x0, y0-0.03*subplotRows*p, corrTypeToString(corr_type[p]), color=pcolor[p],
                                    size=mysize, transform=pb.gca().transAxes)
                            if (channeldiff > 0):
                                pb.text(x0, ystartMadLabel-0.03*subplotRows*p,
                                        corrTypeToString(corr_type[p])+' MAD = %.4f'%(gphs_mad[p]['mad']),
                                        color=pcolor[p],size=mysize, transform=pb.gca().transAxes)
                  if (xframe == firstFrame):
                        # draw title including caltable name
                        caltableList = caltableTitle
                        if (bpolyOverlay):
                              caltableList += ', ' + caltable2 + ' (degamp=%d, degphase=%d)'%(nPolyAmp[index]-1,nPolyPhase[index]-1)
                              if (bpolyOverlay2):
                                    caltableList += ', ' + caltable3 + ' (degamp=%d, degphase=%d)'%(nPolyAmp2[index]-1,nPolyPhase2[index]-1)
                        pb.text(xstartTitle, ystartTitle, caltableList, size=titlesize,
                                color='k', transform=pb.gcf().transFigure)
              elif (overlayAntennas==True and xant==antennasToPlot[-1] and bOverlay==False  # ):
                    and overlayTimes==False):  # try to support antenna,time   avoid antenna labels 'phase'
                  # We do this last, because by then, the limits will be stable.
                  x0 = xstartPolLabel
                  y0 = ystartPolLabel
                  if (corrTypeToString(corr_type[0]) in polsToPlot):
                      if (channeldiff > 0):
                          pb.text(x0, ystartMadLabel-0.03*subplotRows*p,
                                  corrTypeToString(corr_type[p])+' MAD = %.4f'%(gphs_mad[p]['mad']),
                                  color=overlayColors[0], size=mysize, transform=pb.gca().transAxes)
                      if (phasemarkstyle.find('-')>=0):
                          pb.text(x0, y0-0.03*subplotRows*0, corrTypeToString(corr_type[0])+' solid', color=overlayColors[0],
                                  fontsize=mysize, transform=pb.gca().transAxes)
                      else:
                          pb.text(x0+0.02, y0-0.03*subplotRows*0, corrTypeToString(corr_type[0]), color=overlayColors[0],
                                  fontsize=mysize, transform=pb.gca().transAxes)
                          pdesc = pb.plot([x0], [y0+0.015-0*0.03*subplotRows], '%sk'%phasemarkstyle, markersize=markersize,
                                          scalex=False,scaley=False, transform=pb.gca().transAxes)
                  if (len(corr_type) > 1):
                    if (corrTypeToString(corr_type[1]) in polsToPlot):
                      if (channeldiff > 0):
                          pb.text(x0, ystartMadLabel-0.03*subplotRows*p,
                                  corrTypeToString(corr_type[p])+' MAD = %.4f'%(gphs_mad[p]['mad']),
                                  color=overlayColors[0], size=mysize, transform=pb.gca().transAxes)
                      if (phasemarkstyle2.find('--')>=0):
                          pb.text(x0, y0-0.03*subplotRows*1, corrTypeToString(corr_type[1])+' dashed', color=overlayColors[0],
                                  fontsize=mysize, transform=pb.gca().transAxes)
                      else:
                          pb.text(x0+0.02, y0-0.03*subplotRows*1, corrTypeToString(corr_type[1]), color=overlayColors[0],
                                  fontsize=mysize, transform=pb.gca().transAxes)
                          pdesc = pb.plot([x0], [y0+0.015*subplotRows-0.03*subplotRows*1],'%sk'%phasemarkstyle2, markersize=markersize,
                                          scalex=False,scaley=False, transform=pb.gca().transAxes)
                  if (xframe == firstFrame):
                      # draw title including caltable name
                      pb.text(xstartTitle, ystartTitle, caltableTitle, size=titlesize, color='k',
                              transform=pb.gcf().transFigure)
                      DrawAntennaNames(msAnt, antennasToPlot, msFound, mysize)
              elif (overlayTimes==True and bOverlay == False 
                    and overlayAntennas==False):  # try to support antenna,time
                  doneOverlayTime = True # assumed until proven otherwise in the 'for' loop
                  for f in fieldIndicesToPlot:
                      if (uniqueTimes[mytime] < uniqueTimesPerFieldPerSpw[ispwInCalTable][f][-1]-solutionTimeThresholdSeconds and
                          uniqueTimes[mytime] < timerangeListTimes[-1]):
                          doneOverlayTime = False
                  if (doneOverlayTime):
                      # either it is the last time of any times in solution, or the last time in the list of times to plot
                      mytime = nUniqueTimes-1
                      # We do this last, because by then, the limits will be broad enough and stable.
                      x0 = xstartPolLabel
                      y0 = ystartPolLabel
                      if (corrTypeToString(corr_type[0]) in polsToPlot):
                        if (channeldiff > 0):
                            p = 0
                            pb.text(x0, ystartMadLabel-0.03*subplotRows*p,
                                    corrTypeToString(corr_type[p])+' MAD = %.4f'%(gphs_mad[p]['mad']),
                                    color='k', size=mysize, transform=pb.gca().transAxes)
                        if (phasemarkstyle.find('-')>=0):
                            pb.text(x0, y0, corrTypeToString(corr_type[0])+' solid', color='k',
                                    fontsize=mysize, transform=pb.gca().transAxes)
                        else:
                            pb.text(x0+0.02, y0, corrTypeToString(corr_type[0]), color='k',
                                    fontsize=mysize, transform=pb.gca().transAxes)
                            pdesc = pb.plot([x0], [y0+0.015*subplotRows], '%sk'%phasemarkstyle, markersize=markersize,
                                            scalex=False,scaley=False, transform=pb.gca().transAxes)
                      if (len(corr_type) > 1):
                        if (corrTypeToString(corr_type[1]) in polsToPlot):
                          if (channeldiff > 0):
                              p = 1
                              pb.text(x0, ystartMadLabel-0.03*subplotRows*p,
                                      corrTypeToString(corr_type[p])+' MAD = %.4f'%(gphs_mad[p]['mad']),
                                      color='k', size=mysize, transform=pb.gca().transAxes)
                          if (phasemarkstyle2.find('--')>=0):
                              pb.text(x0, y0-0.03*subplotRows, corrTypeToString(corr_type[1])+' dashed',
                                      color='k',fontsize=mysize, transform=pb.gca().transAxes)
                          else:
                              pb.text(x0+0.02, y0-0.03*subplotRows, corrTypeToString(corr_type[1]),
                                      color='k', fontsize=mysize, transform=pb.gca().transAxes)
                              pdesc = pb.plot([x0], [y0+0.015*subplotRows-0.03*subplotRows], '%sk'%phasemarkstyle2,
                                              markersize=markersize, scalex=False,scaley=False, transform=pb.gca().transAxes)
                      if (xframe == firstFrame):
                          # draw title including caltable name
                          pb.text(xstartTitle, ystartTitle, caltableTitle, size=titlesize, color='k',
                                  transform=pb.gcf().transFigure)
                          drawOverlayTimeLegends(xframe,firstFrame,xstartTitle,ystartTitle,
                                                 caltable,titlesize,fieldIndicesToPlot,
                                                 ispwInCalTable,uniqueTimesPerFieldPerSpw,
                                                 timerangeListTimes, solutionTimeThresholdSeconds,
                                                 debugSloppyMatch,ystartOverlayLegend,debug,mysize,
                                                 fieldsToPlot,myUniqueColor,timeHorizontalSpacing,
                                                 fieldIndex,overlayColors, antennaVerticalSpacing,
                                                 overlayAntennas, timerangeList, caltableTitle)
              elif (overlayAntennas and overlayTimes):  # Oct 23, 2012
# #            else:
                  # This will only happen for: try to support overlay='antenna,time'
                  if (xframe == firstFrame and mytime==0 and xctr==firstUnflaggedAntennaToPlot and bOverlay==False):
                      # draw title including caltable name
                      pb.text(xstartTitle, ystartTitle, caltableTitle, size=titlesize, color='k',
                              transform=pb.gcf().transFigure)
                      DrawBottomLegendPageCoords(msName, uniqueTimes[mytime], mysize)
                  
              #endif (overlayAntennas == False and overlayTimes == False and bOverlay == False)
              
              # Here is 2nd place where we eliminate any white space on the right and left edge of the plots: 'phase'
              if (abs(plotrange[2]) > 0 or abs(plotrange[3]) > 0):
                  if (amplitudeWithPhase == False or phase == ''):
                      SetNewYLimits([plotrange[2],plotrange[3]])
              if (phase != '' and amplitudeWithPhase):
                  if (phase[0] != 0 or phase[1] != 0):
                      SetNewYLimits(phase)
              if (plotrange[0]==0 and plotrange[1]==0):
                  if (xaxis.find('chan')>=0):
                      SetNewXLimits([channels[0],channels[-1]])
                  else:
                      if (zoom != 'intersect'):
                          SetNewXLimits([frequencies[0], frequencies[-1]])
                      if (bOverlay):
                          if (xrange2 >= xrange and zoom != 'intersect'):
                              # This is necessary if caltable2=TDM and caltable=FDM
                              SetNewXLimits([frequencies2[0], frequencies2[-1]])
                          if (xrange2 > xrange+0.1 and zoom != 'intersect'):
                              TDMisSecond = True
              else:
                  SetNewXLimits([plotrange[0], plotrange[1]])
  
              # I need the following line for chanrange to work
              if (chanrange[0] != 0 or chanrange[1] != 0):
                  SetLimits(plotrange, chanrange, newylimits, channels, frequencies, pfrequencies, ampMin, ampMax, xaxis,pxl)
  
              # Finally, draw the atmosphere and FDM windows, if requested.
              if ((overlayAntennas==False and overlayTimes==False) or
                  (overlayAntennas==True and overlayTimes==False and xant==antennasToPlot[-1]) or
                  (overlayTimes==True and overlayAntennas==False and doneOverlayTime) or
                  (xant==antennasToPlot[-1] and doneOverlayTime)
                  ):
                  if ((showatm or showtsky) and len(atmString)>0):
                      DrawAtmosphere(showatm, showtsky, subplotRows, atmString,
                                     mysize, TebbSky, plotrange, xaxis, atmchan,
                                     atmfreq, transmission, subplotCols,
                                     showatmPoints=showatmPoints, xframe=xframe, channels=channels)
                      if (LO1 != ''):
                          DrawAtmosphere(showatm,showtsky, subplotRows, atmString,
                                  mysize, TebbSky, plotrange, xaxis, atmchanImage,
                                  atmfreqImage, transmissionImage, subplotCols,
                                  LO1, xframe, firstFrame, showatmPoints, channels=channels)
              
                  if (xaxis.find('freq')>=0 and showfdm and nChannels <= 256):
                      if (tableFormat == 33):
                          showFDM(originalSpw_casa33, chanFreqGHz_casa33)
                      else:
                          showFDM(originalSpw, chanFreqGHz)
  
              if (bOverlay):
                  # draw polarization labels
                  x0 = xstartPolLabel
                  y0 = ystartPolLabel
                  for p in range(nPolarizations):
                      if (corrTypeToString(corr_type[p]) in polsToPlot):
                          pb.text(x0, y0-p*0.03*subplotRows, corrTypeToString(corr_type[p])+'-c1',
                                  color=pcolor[p],size=mysize,transform=pb.gca().transAxes)
                          pb.text(x0, y0-(p*0.03+0.06)*subplotRows, corrTypeToString(corr_type[p])+'-c2',
                                  color=p2color[p],size=mysize, transform=pb.gca().transAxes)
              if (bpolyOverlay and xaxis.find('freq')>=0):
                  x0 = xstartPolLabel
                  y0 = ystartPolLabel
                  if (xcolor != x2color):
                      for p in range(nPolarizations):
                          if (corrTypeToString(corr_type[p]) in polsToPlot):
                              pb.text(x0+0.1, y0-p*0.03*subplotRows, corrTypeToString(corr_type[p]), color=p2color[p],
                                      size=mysize, transform=pb.gca().transAxes)
                  if (bpolyOverlay2):
                      for p in range(nPolarizations):
                            if (corrTypeToString(corr_type[p]) in polsToPlot):
                                  pb.text(x0+0.2, y0-p*0.03*subplotRows, corrTypeToString(corr_type[p]), color=p3color[p],
                                          size=mysize, transform=pb.gca().transAxes)
  
          # endif (yaxis='phase')
  
          redisplay = False
  
          if (xframe == lastFrame):
            if (debug):
                print "*** mytime+1=%d,  nUniqueTimes=%d, timerangeList[-1]=%d, doneOverlayTime=%s" % (mytime+1, nUniqueTimes,timerangeList[-1],doneOverlayTime)
                print "*** xant=%d, antennasToPlot[-1]=%d, overlayAntennas=%s, overlayTimes=%s" % (xant,antennasToPlot[-1],overlayAntennas,overlayTimes)
                print "*** xframe=%d, lastFrame=%d, xctr=%d, spwctr=%d, len(antennasToPlot)=%d, len(spwsToPlot)=%d" % (xframe,lastFrame,xctr,spwctr,len(antennasToPlot), len(spwsToPlot))
            myIndexTime = uniqueTimesPerFieldPerSpw[ispwInCalTable][fieldIndex][-1]
            matched,mymatch = sloppyMatch(myIndexTime,uniqueTimes,solutionTimeThresholdSeconds,whichone=True)
            if (matched==False):
                print "---------- 2) Did not find %f within %.1f seconds of anything in %s" % (myIndexTime,solutionTimeThresholdSeconds,str(uniqueTimes))
                print "Try re-running with a smaller solutionTimeThresholdSeconds (currently %f)" % (solutionTimeThresholdSeconds)
                return
            else:
                mytimeTest = mytime==mymatch
            if ((overlayAntennas==False and overlayTimes==False)
                # either it is the last time of any, or the last time in the list of times to plot
                or (overlayAntennas==False and (mytime+1==nUniqueTimes or mytime == timerangeList[-1] or mytimeTest)) 
                or (xant==antennasToPlot[-1] and overlayAntennas==True and overlayTimes==False)  
                # Following case is needed to make subplot=11 to work for: try to support overlay='antenna,time'
                or (xframe == lastFrame and overlayTimes and overlayAntennas and
                   xctr+1==len(antennasToPlot) and
                   mytimeTest and
                   spwctr+1<len(spwsToPlot))
                or (doneOverlayTime and overlayTimes==True
                    and overlayAntennas==False 
                    )):
              DrawBottomLegendPageCoords(msName, uniqueTimes[mytime], mysize)
  
              if (len(figfile) > 0):
                    plotfiles.append(makeplot(figfile,msFound,msAnt,
                                              overlayAntennas,pages,pagectr,
                                              density,interactive,antennasToPlot,
                                              spwsToPlot,overlayTimes,4,debug))
              myinput = ''
              donetime = timeUtilities.time()
              if (interactive):
                  pb.draw()
# #                myinput = raw_input("(%.1f sec) Press return for next screen (b for backwards, q to quit): "%(donetime-mytimestamp))
                  myinput = raw_input("Press return for next page (b for backwards, q to quit): ")
              else:
                  myinput = ''
              skippingSpwMessageSent = 0
              mytimestamp = timeUtilities.time()
              if (myinput.find('q') >= 0):
                  mytime = len(uniqueTimes)
                  spwctr = len(spwsToPlot)
                  xctr = len(antennasToPlot)
                  break
              if (debug):
                  print "4)Setting xframe to %d" % (xframeStart)
              xframe = xframeStart
              myUniqueColor = []
              pb.subplots_adjust(hspace=myhspace, wspace=mywspace)
              if (myinput.find('b') >= 0):
                  if (pagectr > 0):
                      if (debug):
                          print "Decrementing pagectr from %d to %d" % (pagectr, pagectr-1)
                      pagectr -= 1
                  else:
                      if (debug):
                          print "Not decrementing pagectr=%d" % (pagectr)
                  redisplay = True
                  #redisplay the current page by setting ctrs back to the value they had at start of that page
                  xctr = pages[pagectr][PAGE_ANT]
                  spwctr = pages[pagectr][PAGE_SPW]
                  mytime = pages[pagectr][PAGE_TIME]
                  myap = pages[pagectr][PAGE_AP]
                  xant = antennasToPlot[xctr]
                  antstring, Antstring = buildAntString(xant,msFound,msAnt)
                  ispw = spwsToPlot[spwctr]
# #                print "Returning to [%d,%d,%d,%d]" % (xctr,spwctr,mytime,myap)
              else:
                  pagectr += 1
                  if (pagectr >= len(pages)):
                      newpage = 1
                  else:
                      newpage = 0
              if (overlayTimes==True and sloppyMatch(uniqueTimesPerFieldPerSpw[ispwInCalTable][fieldIndex][-1],uniqueTimes[mytime],solutionTimeThresholdSeconds,myprint=debugSloppyMatch)):
                  # be sure to avoid any more loops through mytime which will cause 'b' button to fail
                  mytime = nUniqueTimes
# #          else:
# #              print "Not going to new page, uniqueTimes[mytime]=%.1f, uniqueTimesPerFieldPerSpw[ispwInCalTable][fieldIndex][-1]=%.1f" % (uniqueTimes[mytime],uniqueTimesPerFieldPerSpw[ispwInCalTable][fieldIndex][-1])
          if (redisplay == False):
              if (xctr+1 >= len(antennasToPlot) or overlayAntennas==False): 
                  mytime += 1
                  if (debug):
                      print "AT BOTTOM OF LOOP: Incrementing mytime to %d, setting firstUnflaggedAntennaToPlot to 0" % (mytime)
                  firstUnflaggedAntennaToPlot = 0  # try this
                  doneOverlayTime = False  # added on 08-nov-2012
        # end of while(mytime) loop
        if (redisplay == False):
            spwctr += 1
            if (debug):
                print "Incrementing spwctr to %d" % (spwctr)
        else:
            if (debug):
                print "redisplay = True"
      # end of while(spwctr) loop
      if (xant >= antennasToPlot[-1] and xframe != xframeStart):
          # this is the last antenna, so make a final plot
          if (len(figfile) > 0):
                plotfiles.append(makeplot(figfile,msFound,msAnt,overlayAntennas,
                                       pages,pagectr,density,interactive,
                                       antennasToPlot,spwsToPlot,overlayTimes,5,debug))
      if (redisplay == False):
          xctr += 1
# #        print "Incrementing xctr to %d" % (xctr)
      if (overlayAntennas):
# #        print "Breaking out of antenna loop because we are done -------------------"
          break
    # end of while(xant) loop
    pb.draw()
    if (len(plotfiles) > 0 and buildpdf):
      pdfname = figfile+'.pdf'
      filelist = ''
      plotfiles = np.unique(plotfiles)
      for i in range(len(plotfiles)):
        cmd = '%s -density %d %s %s.pdf' % (convert,density,plotfiles[i],plotfiles[i].split('.png')[0])
        casalogPost(debug,"Running command = %s" % (cmd))
        mystatus = os.system(cmd)
        if (mystatus != 0):
            print "ImageMagick's convert command not found, no PDF built"
            buildpdf = False
            break
        filelist += plotfiles[i].split('.png')[0] + '.pdf '
      if (buildpdf):
          cmd = '%s %s cat output %s' % (pdftk, filelist, pdfname)
          casalogPost(debug,"Running command = %s" % (cmd))
          mystatus = os.system(cmd)
          if (mystatus != 0):
              cmd = '%s -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile=%s %s' % (gs,pdfname,filelist)
              casalogPost(debug,"Running command = %s" % (cmd))
              mystatus = os.system(cmd)
          if (mystatus == 0):
              casalogPost(debug,"PDF left in %s" % (pdfname))
              print "PDF left in %s" % (pdfname)
              os.system("rm -f %s" % filelist)
          else:
              print "Both pdftk and ghostscript are missing, so no PDF built."
    if (channeldiff>0):
        # Compute median over all antennas, or at least those completed before 'q' was hit
        madstats['median'] = dict.fromkeys(spwsToPlot)
        spwvalue = {}
        spwvalue['amp'] = []
        spwvalue['phase'] = []
        for j in spwsToPlot:
            madstats['median'][j] = dict.fromkeys(timerangeList) # dict.fromkeys(range(len(uniqueTimes)))
            for k in timerangeList: # range(len(uniqueTimes)):
                madstats['median'][j][k] = dict.fromkeys(range(nPolarizations))
                for l in range(nPolarizations):
                    if (yaxis == 'both'):
                        madstats['median'][j][k][l] = {'amp': None, 'phase': None}
                    elif (yaxis == 'phase'):
                        madstats['median'][j][k][l] = {'phase': None}
                    else:
                        # this includes tsys and amp
                        madstats['median'][j][k][l] = {'amp': None}
                    for m in madstats['median'][j][k][l].keys():
                        value = []
                        for i in madstats.keys():  # loop over antennas
                            if (i != 'median'):
                                if (madstats[i][j][k][l][m] != None):
# #                                  print "madstats[%s][%d][%d][%d][%s] = " % (i,j,k,l,m), madstats[i][j][k][l][m]
                                    value.append(madstats[i][j][k][l][m])
                                    spwvalue[m].append(madstats[i][j][k][l][m])
                        madstats['median'][j][k][l][m] = np.median(value)
        # now add another spw which is the median over spw,time,polarization
        if (yaxis == 'both'):
            madstats['median']['median']={'amp': np.median(spwvalue['amp']),
                                          'phase': np.median(spwvalue['phase'])}
        elif (yaxis == 'phase'):
            madstats['median'][j][k][l] = {'phase': np.median(spwvalue['phase'])}
        else:
            madstats['median']['median'] = {'amp': np.median(spwvalue['amp'])}
        
        return(madstats)
    else:
        return()

def calcChebyshev(coeff, validDomain, x):
    """
    Given a set of coefficients,
    this method evaluates a Chebyshev approximation.
    """
    if (type(x) == float or type(x) == int):
         x = [x]
    xrange = validDomain[1] - validDomain[0]
    x = -1 + 2*(x-validDomain[0])/xrange
    coeff[0] = 0
    if (1==1):
      v = np.polynomial.chebval(x,coeff)
    else:
      # manual approach, before I found chebval()
      v = np.zeros(len(x))
      if (len(coeff) > 0):
          v += coeff[0] * 1
      if (len(coeff) > 1):
          v += coeff[1] * (x)
      if (len(coeff) > 2):
          v += coeff[2] * (2*x**2 - 1)
      if (len(coeff) > 3):
          v += coeff[3] * (4*x**3 - 3*x)
      if (len(coeff) > 4):
          v += coeff[4] * (8*x**4 - 8*x**2 + 1)
      if (len(coeff) > 5):
          v += coeff[5] * (16*x**5 - 20*x**3 + 5*x)
      if (len(coeff) > 6):
          v += coeff[6] * (32*x**6 - 48*x**4 + 18*x**2 - 1)
      if (len(coeff) > 7):
          v += coeff[7] * (64*x**7 -112*x**5 + 56*x**3 - 7*x)
      if (len(coeff) > 8):
          v += coeff[8] * (128*x**8 -256*x**6 +160*x**5 - 32*x**2 + 1)
      if (len(coeff) > 9):
          v += coeff[9] * (256*x**9 -576*x**7 +432*x**5 - 120*x**3 + 9*x)
      if (len(coeff) > 10):
          print "Chebyshev polynomials with degree > 10 are not implemented"
  
    return(v)
    
def ResizeFonts(adesc,fontsize):
#    print "Called ResizeFonts()"
    yFormat = ScalarFormatter(useOffset=False)
    adesc.yaxis.set_major_formatter(yFormat)
    adesc.xaxis.set_major_formatter(yFormat)
    pb.setp(adesc.get_xticklabels(), fontsize=fontsize)
    pb.setp(adesc.get_yticklabels(), fontsize=fontsize)

def complexMeanRad(phases):
    # convert back to real and imaginary, take mean, then convert back to phase
    meanSin = np.mean(np.sin(phases))
    meanCos = np.mean(np.cos(phases))
    return(180*np.arctan2(meanSin, meanCos)/math.pi)

def complexMeanDeg(phases):
    # convert back to real and imaginary, take mean, then convert back to phase
    phases *= math.pi/180
    meanSin = np.mean(np.sin(phases))
    meanCos = np.mean(np.cos(phases))
    return(180*np.arctan2(meanSin, meanCos)/math.pi)

def CalcAtmTransmission(chans,freqs,xaxis,pwv,vm, mymsmd,vis,asdm,antenna,timestamp,
                        interval,field,refFreqInTable, net_sideband,
                        mytime, missingCalWVRErrorPrinted,
                        verbose=False):
    """
    chans: all channels, regardless of whether they are flagged
    freqs: frequencies corresponding to chans
    xaxis: what we are plotting on the xaxis: 'chan' or 'freq'
    """
#    print "CalcAtm, field = ", field
#    print "interval = ", interval
#    print "refFreqInTable = ", refFreqInTable
    telescopeName = mymsmd.observatorynames()[0]
    if (telescopeName.find('ALMA') >= 0):
        defaultPWV = 1.0   # a reasonable value for ALMA in case it cannot be found
    elif (telescopeName.find('VLA') >= 0):
        defaultPWV = 5.0  
    else:
        defaultPWV = 5.0  
    if (type(pwv) == str):
      if (pwv.find('auto')>=0):
        if (os.path.exists(vis+'/ASDM_CALWVR') or os.path.exists(vis+'/ASDM_CALATMOSPHERE') or
            os.path.exists('CalWVR.xml')):
              if (verbose):
                  print "*** Computing atmospheric transmission using measured PWV, field %d, time %d (%f). ***" % (field,mytime,timestamp)
              timerange = [timestamp-interval/2, timestamp+interval/2]
              if (os.path.exists(vis+'/ASDM_CALWVR') or os.path.exists(vis+'/ASDM_CALATMOSPHERE')):
                  [pwvmean, pwvstd]  = getMedianPWV(vis,timerange,asdm,verbose=False)
              else:
                  [pwvmean, pwvstd]  = getMedianPWV('.',timerange,asdm='',verbose=False)
              if (verbose):
                  print "retrieved pwvmean = %f" % pwvmean
              retrievedPWV = pwvmean
              if (pwvmean < 0.00001):
                  pwvmean = defaultPWV
        else:
              pwvmean = defaultPWV
              if (missingCalWVRErrorPrinted == False):
                  missingCalWVRErrorPrinted = True
                  if (telescopeName.find('ALMA')>=0):
                      print "No ASDM_CALWVR, ASDM_CALATMOSPHERE, or CalWVR.xml table found.  Using PWV %.1fmm." % pwvmean
                  else:
                      print "This telescope has no WVR to provide a PWV measurement. Using PWV %.1fmm." % pwvmean
      else:
          try:
              pwvmean = float(pwv)
          except:
              pwvmean = defaultPWV
    else:
          try:
              pwvmean = float(pwv)
          except:
              pwvmean = defaultPWV

    if (verbose):
        print "Using PWV = %.2f mm" % pwvmean

    # default values in case we can't find them below
    airmass = 1.5
    P = 563.0
    H = 20.0
    T = 273.0

    if (verbose):
        print "Looking for scans for field integer = %d" % (field)
    scans = mymsmd.scansforfield(field)
    if (verbose):
        print "For field %s, Got scans = " % str(field),scans
    scantimes = mymsmd.timesforscans(scans) # is often longer than the scans array
    scans = getScansForTimes(mymsmd,scantimes) # be sure that each scantime has a scan associated
    if (verbose): print "scantimes = %s" % (str(scantimes))
    if (verbose): print "scans = %s" % (str(scans))
    mindiff = 1e20
    for i in range(len(scantimes)):
        stime = scantimes[i]
        meantime = np.mean(stime)
        tdiff = np.abs(meantime-timestamp)
#        if (verbose): print "tdiff = %s" % (str(tdiff))
        if (tdiff < mindiff):
            bestscan = scans[i]
            if (verbose): print "bestscan = %s" % (str(bestscan))
            mindiff = tdiff
    if (verbose):
          print "For timestamp=%.1f, got closest scan = %d, %.0f sec away" %(timestamp, bestscan,mindiff)
    if (verbose): print "Calling getWeather()"
    [conditions,myTimes] = getWeather(vis,bestscan,antenna,verbose,mymsmd)
    if (verbose): print "Done getWeather()"
    P = conditions['pressure']
    H = conditions['humidity']
    T = conditions['temperature']+273.15
    if (P <= 0.0):
        P = 563
    if (H <= 0.0):
        H = 20
    if (('elevation' in conditions.keys()) == False):
        # Someone cleared the POINTING table, so calculate elevation from Ra/Dec/MJD
#        myfieldId =  mymsmd.fieldsforname(mymsmd.fieldsforscan(bestscan))
        myfieldId =  mymsmd.fieldsforscan(bestscan)[0]
        myscantime = np.mean(mymsmd.timesforscan(bestscan))
        mydirection = getRADecForField(vis, myfieldId, verbose)
        if (verbose):
            print "myfieldId = %s" % (str(myfieldId))
            print "mydirection = %s" % (str(mydirection))
            print "Scan =  %d, time = %.1f,  Field = %d, direction = %s" % (bestscan, myscantime, myfieldId, str(mydirection))
        telescopeName = mymsmd.observatorynames()[0]
        if (len(telescopeName) < 1):
            telescopeName = 'ALMA'
        print "telescope = %s" % (telescopeName)
        myazel = computeAzElFromRADecMJD(mydirection, myscantime/86400., telescopeName)
        conditions['elevation'] = myazel[1] * 180/math.pi
        conditions['azimuth'] = myazel[0] * 180/math.pi
        if (verbose):
            print "Computed elevation = %.1f deg" % (conditions['elevation'])
        
    if (verbose):
          print "CalcAtm: found elevation=%f (airmass=%.3f) for scan: %s" % (conditions['elevation'],1/np.sin(conditions['elevation']*np.pi/180.), str(bestscan))
          print "P,H,T = %f,%f,%f" % (P,H,T)
    if (conditions['elevation'] <= 3):
        print "Using 45 deg elevation instead"
        airmass = 1.0/math.cos(45*math.pi/180.)
    else:
        airmass = 1.0/math.cos((90-conditions['elevation'])*math.pi/180.)

    tropical = 1
    midLatitudeSummer = 2
    midLatitudeWinter = 3
    numchan = len(freqs)
    reffreq=0.5*(freqs[numchan/2-1]+freqs[numchan/2])
    originalnumchan = numchan
    while (numchan > MAX_ATM_CALC_CHANNELS):
        numchan /= 2
#        print "Reducing numchan to ", numchan
        chans = range(0,originalnumchan,(originalnumchan/numchan))

    chansep = (freqs[-1]-freqs[0])/(numchan-1)
    nbands = 1
    if (verbose): print "Opening casac.atmosphere()"
    if (type(casac.Quantity) != type):  # casa 4.x
        myat = casac.atmosphere()
    else:
        myat = createCasaTool(attool)
    if (verbose): print "Opened"
    if (type(casac.Quantity) == type):  # casa 3.x
        fCenter = casac.Quantity(reffreq,'GHz')
        fResolution = casac.Quantity(chansep,'GHz')
        fWidth = casac.Quantity(numchan*chansep,'GHz')
        myat.initAtmProfile(humidity=H,temperature=casac.Quantity(T,"K"),altitude=casac.Quantity(5059,"m"),pressure=casac.Quantity(P,'mbar'),atmType=midLatitudeWinter)
        myat.initSpectralWindow(nbands,fCenter,fWidth,fResolution)
        myat.setUserWH2O(casac.Quantity(pwvmean,'mm'))
    else:   # casa 4.0
        myqa = qatool()
        fCenter = myqa.quantity(reffreq,'GHz')
        fResolution = myqa.quantity(chansep,'GHz')
        fWidth = myqa.quantity(numchan*chansep,'GHz')
        myat.initAtmProfile(humidity=H,temperature=myqa.quantity(T,"K"),altitude=myqa.quantity(5059,"m"),pressure=myqa.quantity(P,'mbar'),atmType=midLatitudeWinter)
        myat.initSpectralWindow(nbands,fCenter,fWidth,fResolution)
        myat.setUserWH2O(myqa.quantity(pwvmean,'mm'))

#    myat.setAirMass()  # This does not affect the opacity, but it does effect TebbSky, so do it manually.

    rc = myat.getRefChan()
    n = myat.getNumChan()
    if (verbose): print "numchan = %s" % (str(n))
    try:     # casa 3.x
        dry = np.array(myat.getDryOpacitySpec(0)['dryOpacity'])
        wet = np.array(myat.getWetOpacitySpec(0)['wetOpacity'].value)
        TebbSky = []
        for chan in range(n):  # do NOT use numchan here, use n
            TebbSky.append(myat.getTebbSky(nc=chan, spwid=0).value)
        TebbSky = np.array(TebbSky)
        # readback the values to be sure they got set
        rf = myat.getRefFreq().value
        cs = myat.getChanSep().value
    except:   # casa 4.0
        dry = np.array(myat.getDryOpacitySpec(0)[1])
        wet = np.array(myat.getWetOpacitySpec(0)[1]['value'])
        TebbSky = myat.getTebbSkySpec(spwid=0)[1]['value']
        # readback the values to be sure they got set
        rf = myat.getRefFreq()['value']
        cs = myat.getChanSep()['value']
        if (myat.getRefFreq()['unit'] != 'GHz'):
            print "There is a unit mismatch for refFreq in the code."
        if (myat.getChanSep()['unit'] != 'MHz'):
            print "There is a unit mismatch for chanSep in the code."

    chans = range(n)
    transmission = np.exp(-airmass*(wet+dry))
    TebbSky *= (1-np.exp(-airmass*(wet+dry)))/(1-np.exp(-wet-dry))

    if (refFreqInTable*1e-9>np.mean(freqs)):
        if ((net_sideband % 2) == 0):
            sense = 1
        else:
            sense = 2
    else:
        if ((net_sideband % 2) == 0):
            sense = 2
        else:
            sense = 1

    if (sense == 1):
        # The following looks right for LSB   sense=1
#        freq = rf.value + cs.value*0.001*(0.5*n-1-np.array(range(n)))
        freq = rf + cs*0.001*(0.5*n-1-np.array(range(n)))
        if (xaxis.find('chan')>=0):
            trans = np.zeros(len(transmission))
            Tebb = np.zeros(len(TebbSky))
            for i in range(len(transmission)):
                trans[i] = transmission[len(transmission)-1-i]
                Tebb[i] = TebbSky[len(TebbSky)-1-i]
            transmission = trans
            TebbSky = Tebb
    else:
        # Using numchan can cause an inconsistency for small number of channels
#        freq = rf.value+cs.value*0.001*(np.array(range(numchan))-0.5*numchan+1)
        # The following looks right for USB  sense=2
        freq = rf+cs*0.001*(np.array(range(n))-0.5*n+1)
        
    if (verbose): print "Done CalcAtmTransmission"
    return(freq, chans, transmission, pwvmean, airmass, TebbSky, missingCalWVRErrorPrinted)

def RescaleTrans(trans, lim, subplotRows, lo1='', xframe=0):
    # Input: the array of transmission or TebbSky values and current limits
    # Returns: arrays of the rescaled transmission values and the zero point
    #          values in units of the frame, and in amplitude.
    debug = False
    yrange = lim[1]-lim[0]
    if (lo1 == ''):
        labelgap = 0.6 # Use this fraction of the margin for the PWV ATM label
    else:
        labelgap = 0.5 # Use this fraction of the margin to separate the top
                       # curve from the upper y-axis
    y2 = lim[1] - labelgap*yrange*TOP_MARGIN/(1.0+TOP_MARGIN)
    y1 = lim[1] - yrange*TOP_MARGIN/(1.0+TOP_MARGIN)
    transmissionRange = np.max(trans)-np.min(trans)
    if (transmissionRange < 0.05):
          # force there to be a minimum range of transmission display 
          # overemphasize tiny ozone lines
          transmissionRange = 0.05

    if (transmissionRange > 1 and transmissionRange < 10):
          # force there to be a minimum range of Tebbsky (10K) to display
          transmissionRange = 10

    # convert transmission to amplitude
    newtrans = y2 - (y2-y1)*(np.max(trans)-trans)/transmissionRange

    # Use edge values
    edgeValueTransmission = trans[-1]
    otherEdgeValueTransmission = trans[0]

    # Now convert the edge channels' transmission values into amplitude
    edgeValueAmplitude = y2 - (y2-y1)*(np.max(trans)-trans[-1])/transmissionRange
    otherEdgeValueAmplitude = y2 - (y2-y1)*(np.max(trans)-trans[0])/transmissionRange

    # Now convert amplitude to frame units, offsetting downward by half
    # the font size
    fontoffset = 0.01*subplotRows
    edgeValueFrame = (edgeValueAmplitude - lim[0])/yrange  - fontoffset
    otherEdgeValueFrame = (otherEdgeValueAmplitude - lim[0])/yrange  - fontoffset

    # scaleFactor is how large the plot is from the bottom x-axis
    # up to the labelgap, in units of the transmissionRange
    scaleFactor = (1+TOP_MARGIN*(1-labelgap)) / (TOP_MARGIN*(1-labelgap))

    # compute the transmission at the bottom of the plot, and label it
    y0transmission = np.max(trans) - transmissionRange*scaleFactor
    y0transmissionFrame = 0
    y0transmissionAmplitude = lim[0]

    if (y0transmission <= 0):
        # If the bottom of the plot is below zero transmission, then label
        # the location of zero transmission instead.
        if (debug):
            print "--------- y0transmission original = %f, (y1,y2)=(%f,%f)" % (y0transmission,y1,y2)
        y0transmissionAmplitude = y1-(y2-y1)*(np.min(trans)/transmissionRange)
        y0transmissionFrame = (y0transmissionAmplitude-lim[0]) / (lim[1]-lim[0])
        y0transmission = 0
    if (debug):
        print "-------- xframe=%d, scaleFactor = %s" % (xframe, str(scaleFactor))
        print "edgeValueFrame, other = %s, %s" % (str(edgeValueFrame), str(otherEdgeValueFrame))
        print "edgeValueTransmission, other = %s, %s" % (str(edgeValueTransmission), str(otherEdgeValueTransmission))
        print "edgeValueAmplitude, otherEdgeValueAmplitude = %s, %s" % (str(edgeValueAmplitude), str(otherEdgeValueAmplitude))
        print "y0transmission = %f, y0transmissionFrame = %f" % (y0transmission,y0transmissionFrame)
        print "y0transmissionAmplitude = %s" % (str(y0transmissionAmplitude))
        print "transmissionRange = %s" % (str(transmissionRange))
    return(newtrans, edgeValueFrame, y0transmission, y0transmissionFrame,
           otherEdgeValueFrame, edgeValueTransmission,
           otherEdgeValueTransmission, edgeValueAmplitude,
           otherEdgeValueAmplitude, y0transmissionAmplitude)

def RescaleX(chans, lim, plotrange, channels):
    # This function is now only used by DrawAtmosphere when xaxis='chan'.
    # It is only really necessary when len(chans)>MAX_ATM_CALC_CHANNELS.
    #  - September 2012
    # If the user specified a plotrange, then rescale to this range,
    # otherwise rescale to the automatically-determined range.

    # chans = 0..N where N=number of channels in the ATM_CALC
    # channels = 0..X where X=number of channels in the spw, regardless of flagging

    if (len(chans) != len(channels)):
        if (chans[1] > chans[0]):
            atmchanrange = chans[-1]-chans[0]
        else:
            atmchanrange = chans[0]-chans[-1]

        if (channels[1] > channels[0]):
            chanrange = channels[-1]-channels[0]
        else:
            chanrange = channels[0]-channels[-1]
        
        newchans = np.array(chans)*chanrange/atmchanrange
        return(newchans)
    else:
        return(chans)  

def recalcYlimitsFreq(chanrange, ylimits, amp, sideband,plotrange,xchannels):
    # Used by plots with xaxis='freq'
    # xchannels are the actual channel numbers of unflagged data, i.e. displayed points
    # amp is actual data plotted
    ylim_debug = False
    if (len(amp) < 1):
        return(pb.ylim()) # ylimits)
    if (chanrange[0]==0 and chanrange[1] == 0 and plotrange[2] == 0 and plotrange[3]==0):
        if (len(amp) == 1):
            if (ylim_debug):
                print "amp = %s" % (str(amp))
            ylimits = [amp[0]-0.2, amp[0]+0.2]
        else:
            newmin = np.min(amp)
            newmax = np.max(amp)
            newmin = np.min([ylimits[0],newmin])
            newmax = np.max([ylimits[1],newmax])
            ylimits = [newmin, newmax]
    elif ((abs(chanrange[0]) > 0 or abs(chanrange[1]) > 0)):
        plottedChannels = np.intersect1d(xchannels, range(chanrange[0],chanrange[1]+1))
        if (len(plottedChannels) < 1):
            return(ylimits)
        mylist = np.arange(xchannels.index(plottedChannels[0]), 1+xchannels.index(plottedChannels[-1]))
        if (mylist[-1] >= len(amp)):
            # prevent crash if many channels are flagged
            return(ylimits)
        if (ylim_debug):
            print "Starting with limits = %s" % (str(ylimits))
            print "Examining channels: %s" % (str(mylist))
            print "len(amp): %d" % (len(amp))
            print "Examining values: amp[mylist] = %s" % (str(amp[mylist]))
        newmin = np.min(amp[mylist])
        newmax = np.max(amp[mylist])
        newmin = np.min([ylimits[0],newmin])
        newmax = np.max([ylimits[1],newmax])
        #  The following presents a problem with overlays, as it keeps widening forever
# #      newmin -= 0.05*(newmax-newmin)
# #      newmax += 0.05*(newmax-newmin)
        ylimits = [newmin, newmax]
    if (ylim_debug):
        print "Returning with limits = %s" % (str(ylimits))
    return ylimits

def recalcYlimits(plotrange, ylimits, amp):
    # Used by plots with xaxis='chan'
    if (len(amp) < 1):
        return(pb.ylim())
    if ((abs(plotrange[0]) > 0 or abs(plotrange[1]) > 0) and (plotrange[2] == 0 and plotrange[3] == 0)):
        x0 = plotrange[0]
        x1 = plotrange[1]
        if (x0 < 0):
            x0 = 0
        if (x1 > len(amp)-1):
            x1 = len(amp)-1
        if (len(amp) > x1 and x0 < x1):
            newmin = np.min(amp[x0:x1])
            newmax = np.max(amp[x0:x1])
            newmin = np.min([ylimits[0],newmin])
            newmax = np.max([ylimits[1],newmax])
            ylimits = [newmin, newmax]
    else:
        ylimits = pb.ylim()  # added on 10/27/2011
# #      print "current ylimits = ", ylimits
    return(ylimits)

def SetNewYLimits(newylimits):
#    print "Entered SetNewYLimits with ", newylimits 
    newrange = newylimits[1]-newylimits[0]
    pb.ylim([newylimits[0]-0.0*newrange, newylimits[1]+0.0*newrange])

def SetNewXLimits(newxlimits):
#    print "Entered SetNewXLimits with range = %.3f" % (np.max(newxlimits)-np.min(newxlimits))
    xrange = np.abs(newxlimits[1]-newxlimits[0])
    buffer = 0.01
    if (newxlimits[0] < newxlimits[1]):
        pb.xlim([newxlimits[0]-xrange*buffer,newxlimits[1]+xrange*buffer] )
    else:
#        print "Swapping xlimits order"
        pb.xlim(newxlimits[1]-xrange*buffer, newxlimits[0]+xrange*buffer)

def sloppyMatch(newvalue, mylist, threshold, myprint=False, whichone=False):
    matched = False
    if (type(mylist) != list and type(mylist)!=type(np.ndarray(0))):
	mylist = [mylist]
    mymatch = -1
    for i in range(len(mylist)):
        v = mylist[i]
        if (abs(newvalue-v) < threshold):
            matched = True
            mymatch = i
    
    if (matched == False and myprint==True):
        casalogPost(myprint,"sloppyMatch: %.0f is not within %.0f of anything in %s" % (newvalue,threshold, str(mylist)))
#        print "Returning matched = ", matched
    elif (myprint==True):
        casalogPost(myprint,"sloppyMatch: %.0f is within %.0f of something in %s" % (newvalue,threshold, str(mylist)))
#        print "Returning matched = ", matched
    if (whichone == False):
        return(matched)
    else:
        return(matched,mymatch)

def sloppyUnique(t, thresholdSeconds):
    """
    Takes a list of numbers and returns a list of unique values, subject to a threshold difference.
    """
    # start with the first entry, and only add a new entry if it is more than the threshold from prior
    sloppyList = [t[0]]
    for i in range(1,len(t)):
        keepit = True
        for j in range(0,i):
            if (abs(t[i]-t[j]) < thresholdSeconds):
                keepit = False
        if (keepit):
            sloppyList.append(t[i])
#    print "sloppyUnique returns %d values from the original %d" % (len(sloppyList), len(t))
    return(sloppyList)

def SetLimits(plotrange, chanrange, newylimits, channels, frequencies, pfrequencies, ampMin, ampMax, xaxis, pxl):
    if (abs(plotrange[0]) > 0 or abs(plotrange[1]) > 0):
        SetNewXLimits([plotrange[0],plotrange[1]])
        if (plotrange[2] == 0 and plotrange[3] == 0):
            # reset the ylimits based on the channel range shown (selected via plotrange)
            SetNewYLimits(newylimits)
    else: # set xlimits to full range
        if (xaxis.find('chan')>=0):
            SetNewXLimits([channels[0],channels[-1]])
        else:
#            print "SetLimits(): Setting x limits to full range (%f-%f)" % (frequencies[0], frequencies[-1])
            SetNewXLimits([frequencies[0], frequencies[-1]])
    if (chanrange[0] != 0 or chanrange[1] != 0):
        # reset the ylimits based on the channel range specified (selected via chanrange)
        if (newylimits != [LARGE_POSITIVE, LARGE_NEGATIVE]):
            SetNewYLimits(newylimits)
#        print "pxl=%d, chanrange[0]=%d, chanrange[1]=%d, shape(pfreq), shape(freq)=" % (pxl, chanrange[0], chanrange[1]), np.shape(pfrequencies),np.shape(frequencies)
        # Use frequencies instead of pfrequencies, because frequencies are not flagged and
        # will continue to work if chanranze is specified and data are flagged.
        try:
            SetNewXLimits([frequencies[chanrange[0]], frequencies[chanrange[1]]])  # Apr 3, 2012
#            SetNewXLimits([pfrequencies[pxl][chanrange[0]], pfrequencies[pxl][chanrange[1]]])
        except:
            print "Invalid chanrange (%d-%d). Valid range = 0-%d" % (chanrange[0],chanrange[1],len(frequencies)-1)
            return(-1)
    if (abs(plotrange[2]) > 0 or abs(plotrange[3]) > 0):
        SetNewYLimits([plotrange[2],plotrange[3]])
    return(0)
    
def showFDM(originalSpw, chanFreqGHz):
    """
    Draws a horizontal bar indicating the location of FDM spws in the dataset.

    originalSpw should contain all spws in the dataset, not just the ones
    in the caltable
    """

    # add some space at the bottom -- Apr 25, 2012
    ylim = pb.ylim()
    yrange = ylim[1]-ylim[0]
    pb.ylim([ylim[0]-BOTTOM_MARGIN*yrange, ylim[1]])

    sdebug = False
    if (sdebug): print "Showing FDM (%d) %s" % (len(originalSpw), str(originalSpw))
    fdmctr = -1
    x0,x1 = pb.xlim()
    y0,y1 = pb.ylim()
    yrange = y1 - y0
    xrange = x1 - x0
    pb.hold(True)
    labelAbove = False  # False means label to the right
    for i in range(len(originalSpw)):
        nchan = len(chanFreqGHz[i])
        if (nchan >= 15 and nchan not in [256,128,64,32,16]):
            fdmctr += 1
            verticalOffset = fdmctr*0.04*yrange
            y1a = y0 + 0.03*yrange + verticalOffset
            if (labelAbove):
                y2 = y1a + 0.01*yrange
            else:
                y2 = y1a - 0.016*yrange
#            print "chan=%d: Drawing line at y=%f (y0=%f) from x=%f to %f" % (len(chanFreqGHz[i]),
#                                              y1a,y0,chanFreqGHz[i][0], chanFreqGHz[i][-1])
            f0 = chanFreqGHz[i][0]
            f1 = chanFreqGHz[i][-1]
            if (f1 < f0):
                swap = f1
                f1 = f0
                f0 = swap
            v0 = np.max([f0,x0])
            v1 = np.min([f1,x1])
            if (v1 > v0):
                if (labelAbove):
                    xlabel = 0.5*(v0+v1)
                    if (xlabel < x0):
                        xlabel = x0
                    if (xlabel > x1):
                        xlabel = x1
                else:
                    xlabel = v1+0.02*xrange
                pb.plot([v0,v1], [y1a,y1a], '-',
                        linewidth=4, color=overlayColors[fdmctr])
                pb.text(xlabel, y2, "spw%d"%(i), size=7)  
                if (sdebug): print "Plotting spw %d (%d)" % (i, originalSpw[i])
            else:
                if (sdebug): print "Not plotting spw %d (%d) because %f < %f" % (i,originalSpw[i],v0,v1)
        else:
            if (sdebug): print "Not plotting spw %d (%d) because fewer than 256 channels (%d)" % (i,originalSpw[i],nchan)
    if (fdmctr > -1):
        pb.ylim([y0,y1])
        pb.xlim([x0,x1])

def DrawAtmosphere(showatm, showtsky, subplotRows, atmString, mysize,
                   TebbSky, plotrange, xaxis, atmchan, atmfreq, transmission,
                   subplotCols, lo1='', xframe=0, firstFrame=0,
                   showatmPoints=False, channels=[0]):
    """
    Draws atmospheric transmission or Tsky on an amplitude vs. chan or freq plot.
    """
    xlim = pb.xlim()
    ylim = pb.ylim()
    xrange = xlim[1]-xlim[0]
    yrange = ylim[1]-ylim[0]

    if (lo1 == ''):
        # add some space at the top -- Apr 16, 2012
        pb.ylim([ylim[0], ylim[1]+TOP_MARGIN*yrange])
    else:
        pb.ylim([ylim[0], ylim[1]+TOP_MARGIN*yrange*0.5])
    ylim = pb.ylim()
    yrange = ylim[1]-ylim[0]
    #
    ystartPolLabel = 1.0-0.04*subplotRows
    if (lo1 == ''):
        transmissionColor = 'm'
        tskyColor = 'm'
    else:
        transmissionColor = 'k'
        tskyColor = 'k'
    if (showatmPoints):
        atmline = '.'
    else:
        atmline = '-'
    if (showatm or showtsky):
        if (showatm):
            atmcolor = transmissionColor
        else:
            atmcolor = tskyColor
        if (lo1 == ''):
            pb.text(0.25, ystartPolLabel, atmString, color=atmcolor, size=mysize, transform=pb.gca().transAxes)

        if (showtsky):
            rescaledY, edgeYvalue, zeroValue, zeroYValue, otherEdgeYvalue, edgeT, otherEdgeT, edgeValueAmplitude, otherEdgeValueAmplitude, zeroValueAmplitude = RescaleTrans(TebbSky, ylim, subplotRows, lo1, xframe)
        else:
            rescaledY, edgeYvalue, zeroValue, zeroYValue, otherEdgeYvalue, edgeT, otherEdgeT, edgeValueAmplitude, otherEdgeValueAmplitude, zeroValueAmplitude = RescaleTrans(transmission, ylim, subplotRows, lo1, xframe)
        if (xaxis.find('chan')>=0):
            rescaledX = RescaleX(atmchan, xlim, plotrange, channels)
#            rescaledX = atmchan  
            pb.plot(rescaledX, rescaledY,'%s%s'%(atmcolor,atmline))
            tindex = -1
        elif (xaxis.find('freq')>=0):
            pb.plot(atmfreq, rescaledY, '%s%s'%(atmcolor,atmline))
            if (atmfreq[0]<atmfreq[1]):
                tindex = -1
            else:
                tindex = 0
        if (lo1 == ''):
              xEdgeLabel = 1.01
        else:
            if (xframe == firstFrame):
                xEdgeLabel = -0.10*subplotCols # avoids overwriting y-axis label
            else:
                xEdgeLabel = -0.10*subplotCols
        SetNewXLimits(xlim)  # necessary for zoom='intersect'
        SetNewYLimits(ylim)
        # Now draw the percentage on right edge of plot
        if (showtsky):
            if (lo1 == ''):
#                pb.text(xEdgeLabel, edgeYvalue,'%.0fK'%(edgeT),color=atmcolor,
#                        size=mysize, transform=pb.gca().transAxes)
#                pb.text(1.01, zeroYValue,'%.0fK'%(zeroValue), color=atmcolor,
#                        size=mysize, transform=pb.gca().transAxes)
                # This must be done in user coordinates since another curve
                # is plotted following this one.
                pb.text(xlim[1]+0.06*xrange/subplotCols, edgeValueAmplitude,
                        '%.0fK'%(edgeT), color=atmcolor, size=mysize)
                pb.text(xlim[1]+0.06*xrange/subplotCols, zeroValueAmplitude,
                        '%.0fK'%(zeroValue), color=atmcolor,
                        size=mysize)
            else:
                # This can remain in axes units since it is the final plot.
                pb.text(xEdgeLabel, otherEdgeYvalue,'%.0fK'%(otherEdgeT),
                        color=atmcolor,
                        size=mysize, transform=pb.gca().transAxes)
                pb.text(xEdgeLabel, zeroYValue,'%.0fK'%(zeroValue),
                        color=atmcolor,
                        size=mysize, transform=pb.gca().transAxes)
        else:
            # showatm=True
            if (lo1 == ''):
#                pb.text(xEdgeLabel, edgeYvalue,'%.0f%%'%(edgeT*100),
#                        color=atmcolor,
#                        size=mysize, transform=pb.gca().transAxes)
                # This must be done in user coordinates since another curve
                # is plotted following this one.
                pb.text(xlim[1]+0.05*xrange/subplotCols, edgeValueAmplitude,
                        '%.0f%%'%(edgeT*100), color=atmcolor, size=mysize)
                pb.text(xlim[1]+0.05*xrange/subplotCols, zeroValueAmplitude,
                        '%.0f%%'%(zeroValue*100), color=atmcolor,
                        size=mysize)
            else:
                # This can remain in axes units since it is the final plot.
                pb.text(xEdgeLabel, otherEdgeYvalue,'%.0f%%'%(otherEdgeT*100),
                        color=atmcolor,
                        size=mysize, transform=pb.gca().transAxes)
                pb.text(xEdgeLabel, zeroYValue,'%.0f%%'%(zeroValue*100),
                        color=atmcolor,
                        size=mysize, transform=pb.gca().transAxes)
        if (lo1 != ''):
            if (xframe == firstFrame):
                pb.text(+0.96-0.08*subplotCols, -0.07*subplotRows,
                        'Signal Sideband', color='m', size=mysize,
                        transform=pb.gca().transAxes)
                pb.text(-0.08*subplotCols, -0.07*subplotRows,
                        'Image Sideband', color='k', size=mysize,
                        transform=pb.gca().transAxes)
                

def DrawBottomLegendPageCoords(msName, uniqueTimesMytime, mysize):
    msName = msName.split('/')[-1]
    bottomLegend = msName + '  ObsDate=' + utdatestring(uniqueTimesMytime) + '   plotbandpass v' \
                  + PLOTBANDPASS_REVISION_STRING.split()[2] + ' = ' \
                  + PLOTBANDPASS_REVISION_STRING.split()[3] + ' ' \
                  + PLOTBANDPASS_REVISION_STRING.split()[4]
    pb.text(0.1, 0.02, bottomLegend, size=mysize, transform=pb.gcf().transFigure)

def DrawAntennaNames(msAnt, antennasToPlot, msFound, mysize):
    for a in range(len(antennasToPlot)):
        if (msFound):
            legendString = msAnt[antennasToPlot[a]]
        else:
            legendString = str(antennasToPlot[a])
        if (a<maxAntennaNamesAcrossTheTop):
            x0 = xstartTitle+(a*antennaHorizontalSpacing)
            y0 = ystartOverlayLegend
        else:
            # start going down the righthand side
            x0 = xstartTitle+(maxAntennaNamesAcrossTheTop*antennaHorizontalSpacing)
            y0 = ystartOverlayLegend-(a-maxAntennaNamesAcrossTheTop)*antennaVerticalSpacing
        pb.text(x0, y0, legendString,color=overlayColors[a],fontsize=mysize,
                transform=pb.gcf().transFigure)
    
def fixGapInSpws(spws, verbose=False):
    # find gap in spectralWindowId numbering in ASDM_RECEIVER
    gap = 0
    for i in range(len(spws)):
        if (spws[i] > 0):
            gap = spws[i] - 1
            break
    for i in range(len(spws)):
        if (spws[i] > 0):
            if (verbose):
                print "Renaming spw%d to spw%d" % (spws[i],spws[i]-gap)
            spws[i] -= gap
    return(spws)

def madInfo(a, madsigma=3, edge=0):
    """
    Computes the MAD of a list, then returns the value, plus the number and list
    of channels that exceed madsigma*MAD, and the worst outlier.
    """
    info = {}
    if (edge >= len(a)/2):  # protect against too large of an edge value
        originalEdge = edge
        if (len(a) == 2*(len(a)/2)):
            edge = len(a)/2 - 1 # use middle 2 points
        else:
            edge = len(a)/2  # use central point
        print "WARNING edge value is too large, reducing it from %d to %d." % (originalEdge, edge)
    info['mad'] = mad(a[edge:len(a)-edge])
    chan = []
    outlierValue = 0
    outlierChannel = None
    for i in range(edge,len(a)-edge):
        if (np.abs(a[i]) > madsigma*info['mad']):
            chan.append(i)
        if (np.abs(a[i]) > np.abs(outlierValue)):
            outlierValue = a[i]
            outlierChannel = i
    info['nchan'] = len(chan)
    info['chan'] = chan
    info['outlierValue'] = outlierValue/info['mad']
    info['outlierChannel'] = outlierChannel
    return(info)
    
def mad(a, c=0.6745, axis=0):
    """
    Median Absolute Deviation along given axis of an array:

    median(abs(a - median(a))) / c

    c = 0.6745 is the constant to convert from MAD to std; it is used by
    default

    """
    a = np.array(a)
    good = (a==a)
    a = np.asarray(a, np.float64)
    if a.ndim == 1:
        d = np.median(a[good])
        m = np.median(np.fabs(a[good] - d) / c)
#        print  "mad = %f" % (m)
    else:
        d = np.median(a[good], axis=axis)
        # I don't want the array to change so I have to copy it?
        if axis > 0:
            aswp = swapaxes(a[good],0,axis)
        else:
            aswp = a[good]
        m = np.median(np.fabs(aswp - d) / c, axis=0)

    return m

def createCasaTool(mytool):
    """
    A wrapper to handle the changing ways in which casa tools are invoked.
    Todd Hunter
    """
    if (type(casac.Quantity) != type):  # casa 4.x
        myt = mytool()
    else:  # casa 3.x
        myt = mytool.create()
    return(myt)

def getLOs(inputMs, verbose=True):
    """
    Reads the LO information from an ms's ASDM_RECEIVER table.  It returns
    a list of four lists: [freqLO,band,spws,names]
    The logic for converting this raw list into sensible association with
    spw numbers is in printLOs().

    Todd Hunter
    """
    if (os.path.exists(inputMs)):
        if (os.path.exists("%s/ASDM_RECEIVER" % inputMs)):
            try:
                mytb = createCasaTool(tbtool)
                mytb.open("%s/ASDM_RECEIVER" % inputMs)
            except:
                print "Could not open the existing ASDM_RECEIVER table"
                return([])
        else:
            if (verbose):
                print "The ASDM_RECEIVER table for this ms does not exist."
            return([])
    else:
        print "This ms does not exist = %s." % (inputMs)
        return([])
        
    numLO = mytb.getcol('numLO')
    freqLO = []
    band = []
    spws = []
    names = []
    sidebands = []
    receiverIds = []
    for i in range(len(numLO)):
        freqLO.append(mytb.getcell('freqLO',i))
        band.append(mytb.getcell('frequencyBand',i))
        spws.append(int((mytb.getcell('spectralWindowId',i).split('_')[1])))
        names.append(mytb.getcell('name',i))
        sidebands.append(mytb.getcell('sidebandLO',i))
        receiverIds.append(int(mytb.getcell('receiverId',i)))
    mytb.close()
    mytb.open("%s/SPECTRAL_WINDOW" % inputMs)
    spwNames = mytb.getcol("NAME")
    mytb.close()
    return([freqLO,band,spws,names,sidebands,receiverIds,spwNames])
    
def readPWVFromASDM_CALATMOSPHERE(vis):
    """
    Reads the PWV via the water column of the ASDM_CALATMOSPHERE table.
    - Todd Hunter
    """
    mytb = createCasaTool(tbtool)
    mytb.open("%s/ASDM_CALATMOSPHERE" % vis)
    pwvtime = mytb.getcol('startValidTime')  # mjdsec
    antenna = mytb.getcol('antennaName')
    pwv = mytb.getcol('water')[0]  # There seem to be 2 identical entries per row, so take first one.
    mytb.close()
    return(pwvtime, antenna, pwv)
    
def getMedianPWV(vis='.', myTimes=[0,999999999999], asdm='', verbose=False):
    """
    Extracts the PWV measurements from the WVR on all antennas for the
    specified time range.  The time range is input as a two-element list of
    MJD seconds (default = all times).  First, it tries to find the ASDM_CALWVR
    table in the ms.  If that fails, it then tries to find CalWVR.xml in the
    specified ASDM, or failing that, an ASDM of the same name (-.ms).  If neither of 
    these exist, then it tries to find CalWVR.xml in the present working directory.
    If it still fails, it looks for CalWVR.xml in the .ms directory.  Thus,
    you only need to copy this xml file from the ASDM into your ms, rather
    than the entire ASDM. Returns the median and standard deviation in millimeters.
    For further help and examples, see https://safe.nrao.edu/wiki/bin/view/ALMA/GetMedianPWV
    -- Todd Hunter
    """
    pwvmean = 0
    success = False
    mytb = createCasaTool(tbtool)
    if (verbose):
        print "in getMedianPWV with myTimes = %s" % (str(myTimes))
    try:
      if (os.path.exists("%s/ASDM_CALWVR"%vis)):
          mytb.open("%s/ASDM_CALWVR" % vis)
          pwvtime = mytb.getcol('startValidTime')  # mjdsec
          antenna = mytb.getcol('antennaName')
          pwv = mytb.getcol('water')
          mytb.close()
          success = True
          if (len(pwv) < 1):
              print "Found no data in ASDM_CALWVR table"
              return(0,-1)
          if (verbose):
              print "Opened ASDM_CALWVR table, len(pwvtime)=%s" % (str(len(pwvtime)))
      else:
          if (verbose):
              print "Did not find ASDM_CALWVR table in the ms. Will look for ASDM_CALATMOSPHERE next."
          if (os.path.exists("%s/ASDM_CALATMOSPHERE" % vis)):
              pwvtime, antenna, pwv = readPWVFromASDM_CALATMOSPHERE(vis)
              success = True
              if (len(pwv) < 1):
                  print "Found no data in ASDM_CALATMOSPHERE table"
                  return(0,-1)
          else:
              if (verbose):
                  print "Did not find ASDM_CALATMOSPHERE in the ms"
    except:
        if (verbose):
            print "Could not open ASDM_CALWVR table in the ms"
    finally:
     # try to find the ASDM table
     if (success == False):
       if (len(asdm) > 0):
           if (os.path.exists(asdm) == False):
               print "Could not open ASDM = %s" % (asdm)
               if (verbose): casalog.post("Calling mytb.done 3")
               mytb.done()
               return(0,-1)
           try:
               [pwvtime,pwv,antenna] = readpwv(asdm)
           except:
               if (verbose):
                   print "Could not open ASDM = %s" % (asdm)
                   casalog.post("Calling mytb.done 4")
               mytb.done()
               return(pwvmean,-1)
       else:
           try:
               tryasdm = vis.split('.ms')[0]
               if (verbose):
                   print "No ASDM name provided, so I will try this name = %s" % (tryasdm)
               [pwvtime,pwv,antenna] = readpwv(tryasdm)
           except:
               try:
                   if (verbose):
                       print "Still did not find it.  Will look for CalWVR.xml in current directory."
                   [pwvtime, pwv, antenna] = readpwv('.')
               except:
                   try:
                       if (verbose):
                           print "Still did not find it.  Will look for CalWVR.xml in the .ms directory."
                       [pwvtime, pwv, antenna] = readpwv('%s/'%vis)
                   except:
                       if (verbose):
                           print "No CalWVR.xml file found, so no PWV retrieved. Copy it to this directory and try again."
                           casalog.post("Calling mytb.done 5")
                       mytb.done()
                       return(pwvmean,-1)
    try:
        matches = np.where(np.array(pwvtime)>myTimes[0])[0]
    except:
        print "Found no times > %d" % (myTimes[0])
        if (verbose): casalog.post("Calling mytb.done 6")
        mytb.done()
        return(0,-1)
    if (len(pwv) < 1):
        print "Found no PWV data"
        return(0,-1)
    ptime = np.array(pwvtime)[matches]
    matchedpwv = np.array(pwv)[matches]
    matches2 = np.where(ptime<myTimes[-1])[0]
    if (len(matches2) < 1):
        # look for the value with the closest start time
        mindiff = 1e12
        for i in range(len(pwvtime)):
            if (abs(myTimes[0]-pwvtime[i]) < mindiff):
                mindiff = abs(myTimes[0]-pwvtime[i])
                pwvmean = pwv[i]*1000
        matchedpwv = []
        for i in range(len(pwvtime)):
            if (abs(abs(myTimes[0]-pwvtime[i]) - mindiff) < 1.0):
                matchedpwv.append(pwv[i])
        pwvmean = 1000*np.median(matchedpwv)
        if (verbose):
            print "Taking the median of %d pwv measurements from all antennas = %.3f mm" % (len(matchedpwv),pwvmean)
        pwvstd = np.std(matchedpwv)
    else:
        pwvmean = 1000*np.median(matchedpwv[matches2])
        pwvstd = np.std(matchedpwv[matches2])
        if (verbose):
            print "Taking the median of %d pwv measurements from all antennas = %.3f mm" % (len(matches2),pwvmean)
#    mytb.done()
    return(pwvmean,pwvstd)
# end of getMedianPWV

def computeAzElFromRADecMJD(raDec, mjd, observatory='ALMA'):
    """
    Computes the az/el for a specified J2000 RA/Dec, MJD and observatory.

    raDec must be in radians: [ra,dec]
    mjd must be in days
    returns the [az,el] in radians
    - Todd Hunter
    """
    myme = createCasaTool(metool)
    myqa = createCasaTool(qatool)
    mydir = myme.direction('J2000', myqa.quantity(raDec[0],'rad'), myqa.quantity(raDec[1],'rad'))
    myme.doframe(myme.epoch('mjd', myqa.quantity(mjd, 'd')))
    myme.doframe(myme.observatory(observatory))
    myazel = myme.measure(mydir,'azel')
    myqa.done()
    myme.done()
    return([myazel['m0']['value'], myazel['m1']['value']])

def getRADecForField(ms, myfieldId, debug):
    """
    Returns RA,Dec in radians for the specified field in the specified ms.
    -- Todd Hunter
    """
    mytb = createCasaTool(tbtool)
    try:
        mytb.open(ms+'/FIELD')
    except:
        print "Could not open FIELD table for ms=%s" % (ms)
        return([0,0])
    mydir = mytb.getcell('DELAY_DIR',myfieldId)
#    if (mydir[0] < 0):
#        mydir[0] += 2*math.pi
#    mytb.close()
    if (debug): casalog.post("Calling mytb.done 7")
    mytb.done()
    return(mydir)

def getWeather(vis='', scan='', antenna='0',verbose=False, mymsmd=None):
    """
    Queries the WEATHER and ANTENNA tables of an .ms by scan number or
    list of scan numbers in order to return mean values of: angleToSun,
      pressure, temperature, humidity, dew point, wind speed, wind direction,
      azimuth, elevation, solarangle, solarelev, solarazim.
    If the sun is below the horizon, the solarangle returned is negated.
    -- Todd Hunter
    """
    if (verbose):
        print "Entered getWeather with vis,scan,antenna = %s,%s,%s" % (str(vis), str(scan), str(antenna))
    try:
        if str(antenna).isdigit():
            antennaName = mymsmd.antennanames(antenna)[0]
        else:
            antennaName = antenna
            try:
                antenna = mymsmd.antennaids(antennaName)[0]
            except:
                antennaName = string.upper(antenna)
                antenna = mymsmd.antennaids(antennaName)[0]
    except:
        print "Either the ANTENNA table does not exist or antenna %s does not exist" % (antenna)
        return([0,[]])
    mytb = createCasaTool(tbtool)
    try:
        mytb.open("%s/POINTING" % vis)
    except:
        print "POINTING table does not exist"
        if (verbose): casalog.post("Calling mytb.done 8")
        mytb.done()
        return([0,0])
    subtable = mytb.query("ANTENNA_ID == %s" % antenna)
    mytb.close()
    try:
        mytb.open("%s/OBSERVATION" % vis)
        observatory = mytb.getcell("TELESCOPE_NAME",0)
        mytb.close()
    except:
        print "OBSERVATION table does not exist, assuming observatory == ALMA"
        observatory = "ALMA"
    if (scan == ''):
        scan = mymsmd.scannumbers()
    conditions = {}
    conditions['pressure']=conditions['temperature']=conditions['humidity']=conditions['dewpoint']=conditions['windspeed']=conditions['winddirection'] = 0
    conditions['scan'] = scan
    if (type(scan) == str):
        if (scan.find('~')>0):
            tokens = scan.split('~')
            scan = [int(k) for k in range(int(tokens[0]),int(tokens[1])+1)]
        else:
            scan = [int(k) for k in scan.split(',')]
    if (type(scan) == type(np.ndarray(0))):
        scan = list(scan)
    if (type(scan) == list):
        myTimes = np.array([])
        for sc in scan:
            try:
                print "calling timesforscan"
                newTimes = mymsmd.timesforscan(sc)
                print "times = %s" % (str(newTimes))
            except:
                print "Error reading scan %d, is it in the data?" % (sc)
                if (verbose): casalog.post("Calling mytb.done 9")
                mytb.done()
                return([conditions,[]])
            myTimes = np.concatenate((myTimes,newTimes))
    elif (scan != None):
        try:
            myTimes = mymsmd.timesforscan(scan)
        except:
            print "Error reading scan %d, is it in the data?" % (scan)
            if (verbose): casalog.post("Calling mytb.done 10")
            mytb.done()
            return([conditions,[]])
    else:
        if (verbose): casalog.post("Calling mytb.done 11")
        mytb.done()
        return([conditions,[]])
    if (type(scan) == str):
        scan = [int(k) for k in scan.split(',')]
    if (type(scan) == list):
        listscan = ""
        listfield = []
        for sc in scan:
#            print "Processing scan ", sc
            listfield.append(mymsmd.fieldsforscan(sc))
            listscan += "%d" % sc
            if (sc != scan[-1]):
                listscan += ","
#        print "listfield = ", listfield
        listfields = np.unique(listfield[0])
        listfield = ""
        for field in listfields:
            listfield += "%s" % field
            if (field != listfields[-1]):
                listfield += ","
    else:
        listscan = str(scan)
        listfield = mymsmd.fieldsforscan(scan)
    [az,el] = ComputeSolarAzElForObservatory(myTimes[0], mymsmd)
    [az2,el2] = ComputeSolarAzElForObservatory(myTimes[-1], mymsmd)
    azsun = np.mean([az,az2])
    elsun = np.mean([el,el2])
    direction = subtable.getcol("DIRECTION")
    azeltime = subtable.getcol("TIME")
    subtable.close()
    telescopeName = mymsmd.observatorynames()[0]
    if (len(direction) > 0 and telescopeName.find('VLA') < 0):
      azimuth = direction[0][0]*180.0/math.pi
      elevation = direction[1][0]*180.0/math.pi
      npat = np.array(azeltime)
      matches = np.where(npat>myTimes[0])[0]
      matches2 = np.where(npat<myTimes[-1])[0]
      conditions['azimuth'] = np.mean(azimuth[matches[0]:matches2[-1]+1])
      conditions['elevation'] = np.mean(elevation[matches[0]:matches2[-1]+1])
      conditions['solarangle'] = angularSeparation(azsun,elsun,conditions['azimuth'],conditions['elevation'])
      conditions['solarelev'] = elsun
      conditions['solarazim'] = azsun
      if (verbose):
          print "Using antenna = %s to retrieve mean azimuth and elevation" % (antennaName)
          print "Separation from sun = %f deg" % (abs(conditions['solarangle']))
      if (elsun<0):
        conditions['solarangle'] = -conditions['solarangle']
        if (verbose):
            print "Sun is below horizon (elev=%.1f deg)" % (elsun)
      else:
        if (verbose):
            print "Sun is above horizon (elev=%.1f deg)" % (elsun)
      if (verbose):
          print "Average azimuth = %.2f, elevation = %.2f degrees" % (conditions['azimuth'],conditions['elevation'])
    else:
      if (verbose): print "The POINTING table is blank."
      if (type(scan) == int or type(scan)==np.int32):
          # compute Az/El for this scan
        myfieldId = mymsmd.fieldsforscan(scan)
        if (type(myfieldId) == list or type(myfieldId) == type(np.ndarray(0))):
            myfieldId = myfieldId[0]
        fieldName = mymsmd.namesforfields(myfieldId)
        if (type(fieldName) == list or type(fieldName) == type(np.ndarray(0))):
            fieldName = fieldName[0]
#        print "A) fieldname = ", fieldName
#        print "myfieldId = ", myfieldId
        myscantime = np.mean(mymsmd.timesforscan(scan))
#        print "Calling getRADecForField"
        mydirection = getRADecForField(vis, myfieldId, verbose)
        if (verbose): print "mydirection= %s" % (str(mydirection))
        if (len(telescopeName) < 1):
            telescopeName = 'ALMA'
        myazel = computeAzElFromRADecMJD(mydirection, myscantime/86400., telescopeName)
        conditions['elevation'] = myazel[1] * 180/math.pi
        conditions['azimuth'] = myazel[0] * 180/math.pi
        conditions['solarangle'] = angularSeparation(azsun,elsun,conditions['azimuth'],conditions['elevation'])
        conditions['solarelev'] = elsun
        conditions['solarazim'] = azsun
        if (verbose):
            print "Separation from sun = %f deg" % (abs(conditions['solarangle']))
        if (elsun<0):
            conditions['solarangle'] = -conditions['solarangle']
            if (verbose):
                print "Sun is below horizon (elev=%.1f deg)" % (elsun)
        else:
            if (verbose):
                print "Sun is above horizon (elev=%.1f deg)" % (elsun)
        if (verbose):
            print "Average azimuth = %.2f, elevation = %.2f degrees" % (conditions['azimuth'],conditions['elevation'])
      elif (type(scan) == list):
          myaz = []
          myel = []
          if (verbose):
              print "Scans to loop over = %s" % (str(scan))
          for s in scan:
              fieldName = mymsmd.fieldsforscan(s)
              if (type(fieldName) == list):
                  # take only the first pointing in the mosaic
                  fieldName = fieldName[0]
              myfieldId = mymsmd.fieldsforname(fieldName)
              if (type(myfieldId) == list or type(myfieldId)==type(np.ndarray(0))):
                  # If the same field name has two IDs (this happens in EVLA data)
                  myfieldId = myfieldId[0]
              myscantime = np.mean(mymsmd.timesforscan(s))
              mydirection = getRADecForField(vis, myfieldId, verbose)
              telescopeName = mymsmd.observatorynames()[0]
              if (len(telescopeName) < 1):
                  telescopeName = 'ALMA'
              myazel = computeAzElFromRADecMJD(mydirection, myscantime/86400., telescopeName)
              myaz.append(myazel[0]*180/math.pi)
              myel.append(myazel[1]*180/math.pi)
          conditions['azimuth'] = np.mean(myaz)
          conditions['elevation'] = np.mean(myel)
          conditions['solarangle'] = angularSeparation(azsun,elsun,conditions['azimuth'],conditions['elevation'])
          conditions['solarelev'] = elsun
          conditions['solarazim'] = azsun
          if (verbose):
              print "Using antenna = %s to retrieve mean azimuth and elevation" % (antennaName)
              print "Separation from sun = %f deg" % (abs(conditions['solarangle']))
          if (elsun<0):
              conditions['solarangle'] = -conditions['solarangle']
              if (verbose):
                  print "Sun is below horizon (elev=%.1f deg)" % (elsun)
          else:
              if (verbose):
                  print "Sun is above horizon (elev=%.1f deg)" % (elsun)
          if (verbose):
              print "Average azimuth = %.2f, elevation = %.2f degrees" % (conditions['azimuth'],conditions['elevation'])
          
              
    # now, get the weather
    try:
        mytb.open("%s/WEATHER" % vis)
    except:
        print "Could not open the WEATHER table for this ms."
        if (verbose): casalog.post("Calling mytb.done 12")
        mytb.done()
        return([conditions,myTimes])
    if (True):
        mjdsec = mytb.getcol('TIME')
        indices = np.argsort(mjdsec)
        mjd = mjdsec/86400.
        pressure = mytb.getcol('PRESSURE')
        relativeHumidity = mytb.getcol('REL_HUMIDITY')
        temperature = mytb.getcol('TEMPERATURE')
        if (np.mean(temperature) > 100):
            # must be in units of Kelvin, so convert to C
            temperature -= 273.15        
        dewPoint = mytb.getcol('DEW_POINT')
        if (np.mean(dewPoint) > 100):
            # must be in units of Kelvin, so convert to C
            dewPoint -= 273.15        
        if (np.mean(dewPoint) == 0):
            # assume it is not measured and use NOAA formula to compute from humidity:
            dewPoint = ComputeDewPointCFromRHAndTempC(relativeHumidity, temperature)
        sinWindDirection = np.sin(mytb.getcol('WIND_DIRECTION'))
        cosWindDirection = np.cos(mytb.getcol('WIND_DIRECTION'))
        windSpeed = mytb.getcol('WIND_SPEED')
        if (verbose): casalog.post("Calling mytb.done 13")
        mytb.done()
        
        # put values into time order (they mostly are, but there can be small differences)
        mjdsec = np.array(mjdsec)[indices]
        pressure = np.array(pressure)[indices]
        relativeHumidity = np.array(relativeHumidity)[indices]
        temperature = np.array(temperature)[indices]
        dewPoint = np.array(dewPoint)[indices]
        windSpeed = np.array(windSpeed)[indices]
        sinWindDirection = np.array(sinWindDirection)[indices]
        cosWindDirection = np.array(cosWindDirection)[indices]

        # find the overlap of weather measurement times and scan times
        matches = np.where(mjdsec>=np.min(myTimes))[0]
        matches2 = np.where(mjdsec<=np.max(myTimes))[0]
#            print "len(matches)=%d, len(matches2)=%d" % (len(matches), len(matches2))
        noWeatherData = False
        if (len(matches)>0 and len(matches2) > 0):
            # average the weather points enclosed by the scan time range
            selectedValues = range(matches[0], matches2[-1]+1)
            if (selectedValues == []):
                # there was a either gap in the weather data, or an incredibly short scan duration
                if (verbose):
                    print "----  Finding the nearest weather value --------------------------- "
                selectedValues = findClosestTime(mjdsec, myTimes[0])
        elif (len(matches)>0):
            # all points are greater than myTime, so take the first one
            selectedValues = matches[0]
        elif (len(matches2)>0):
            # all points are less than myTime, so take the last one
            selectedValues = matches2[-1]
        else:
            # table has no weather data!
            noWeatherData = True
        if (noWeatherData):
            conditions['pressure'] = 563.0
            conditions['temperature'] = 0  # Celsius is expected
            conditions['humidity'] = 20.0
            conditions['dewpoint'] = -20.0
            conditions['windspeed'] = 0
            conditions['winddirection'] = 0
            print "WARNING: No weather data found in the WEATHER table!"
        else:
          if (type(selectedValues) == np.int64 or type(selectedValues) == np.int32 or  
              type(selectedValues) == np.int):
              conditions['readings'] = 1
              if (verbose):
                  print "selectedValues=%d, myTimes[0]=%.0f, myTimes[1]=%.0f, len(matches)=%d, len(matches2)=%d" % (selectedValues,
                     myTimes[0],myTimes[1], len(matches), len(matches2))
                  if (len(matches) > 0):
                      print "matches[0]=%f, matches[-1]=%f" % (matches[0], matches[-1])
                  if (len(matches2) > 0):
                      print "matches2[0]=%f, matches2[-1]=%d" % (matches2[0], matches2[-1])
          else:
              conditions['readings'] = len(selectedValues)
          conditions['pressure'] = np.mean(pressure[selectedValues])
          if (conditions['pressure'] != conditions['pressure']):
              # A nan value got through, due to no selected values (should be impossible)"
              if (verbose):
                  print ">>>>>>>>>>>>>>>>>>>>>>>>  selectedValues = %s" % (str(selectedValues))
                  print "len(matches)=%d, len(matches2)=%d" % (len(matches), len(matches2))
                  print "matches[0]=%f, matches[-1]=%f, matches2[0]=%f, matches2[-1]=%d" % (matches[0], matches[-1], matches2[0], matches2[-1])
          conditions['temperature'] = np.mean(temperature[selectedValues])
          conditions['humidity'] = np.mean(relativeHumidity[selectedValues])
          conditions['dewpoint'] = np.mean(dewPoint[selectedValues])
          conditions['windspeed'] = np.mean(windSpeed[selectedValues])
          conditions['winddirection'] = (180./math.pi)*np.arctan2(np.mean(sinWindDirection[selectedValues]),np.mean(cosWindDirection[selectedValues]))
          if (conditions['winddirection'] < 0):
              conditions['winddirection'] += 360
          if (verbose):
              print "Mean weather values for scan %s (field %s)" % (listscan,listfield)
              print "  Pressure = %.2f mb" % (conditions['pressure'])
              print "  Temperature = %.2f C" % (conditions['temperature'])
              print "  Dew point = %.2f C" % (conditions['dewpoint'])
              print "  Relative Humidity = %.2f %%" % (conditions['humidity'])
              print "  Wind speed = %.2f m/s" % (conditions['windspeed'])
              print "  Wind direction = %.2f deg" % (conditions['winddirection'])

#    if (verbose): casalog.post("Calling mytb.done 14")
#    mytb.done()
    return([conditions,myTimes])
    # end of getWeather

def getBasebandNumbers(vis):
    mymsmd = createCasaTool(msmdtool)
    mymsmd.open(vis)
    bbc = []
    for spw in range(mymsmd.nspw()):
        bbc.append(mymsmd.baseband(spw))
    mymsmd.done()
    return(bbc)


def yigHarmonic(bandString):
    """
    Returns the YIG harmonic for the specified ALMA band, given as a string 
    used in casa tables.
    For example:  yigHarmonic('ALMA_RB_03')  returns the integer 6.
    Todd Hunter
    """
    # remove any leading spaces
    #bandString = bandString[bandString.find('ALMA_RB'):]
    harmonics = {'ALMA_RB_03':6, 'ALMA_RB_04':6, 'ALMA_RB_06': 18, 
                 'ALMA_RB_07': 18, 'ALMA_RB_08':18, 'ALMA_RB_09':27}
    try:
        harmonic = harmonics[bandString]
    except:
        harmonic = -1
    return(harmonic)

def interpretLOs(vis, parentms='', showWVR=False,
                 showCentralFreq=False, verbose=False, show=False):
    """
    Interpret (and optionally print) the LO settings for an MS.
    Options:
    showCentralFreq: if True, then show the mean frequency of each spw,
                     otherwise show the frequency of the first channel
    showWVR: include the WVR spw in the list
    parentms:  if the dataset has been split from a parent dataset, then
               you may also need to specify the name of the parent ms.
    
    Returns: a dictionary of the LO1 values (in Hz) for each spw, keyed by
             integer

    A typical band 7 TDM dataset (prior to splitting) looks like this:
    SPECTRAL_WINDOW table has 39 rows:   row
           WVR                           0
           8 band 3 windows (pointing)   1-8
           8 band 7 windows              9-16
           22 WVR windows                17-38
    The corresponding ASDM_RECEIVER table has only 18 rows:
           WVR                           0
           8 band 3 windows              1-8
           WVR                           9          
           8 band 7 windows              10-17
    After splitting, the ASDM_RECEIVER table remains the same, but the 
    SPECTRAL WINDOW table then has only 4 rows, as the pointing spws and 
    the channel-averaged data are dropped:
           4 band 7 windows               

    Todd Hunter
    """
    mytb = createCasaTool(tbtool)
    lo1s = {} # initialize dictionary to be returned
    try:
        if (verbose):
            print "Calling getLOs"
        retval =  getLOs(vis)
        if (verbose):
            print "Done getLOs"
        [LOs,bands,spws,names,sidebands,receiverIds,spwNames] = retval
#        spws typically is =  [0,1,2,3,4,5,6,7,8,0,9,10,11,12,13,14,15,16]
    except:
        print "getLOs failed"
        return(retval)
    # find gap in spectralWindowId numbering in ASDM_RECEIVER
    gap = 0
    maxSpw = np.max(spws)
    for i in range(len(spws)):
        if (spws[i] > 0):
            gap = spws[i] - 1
            break
    for i in range(len(spws)):
        if (spws[i] > 0):
            if (verbose):
                print "Renaming spw%d to spw%d" % (spws[i],spws[i]-gap)
            spws[i] -= gap
    index = range(len(spws))

    mytb.open(vis+'/SPECTRAL_WINDOW')
    # If the data have been split into an ms with fewer spws, then this 
    # table will be smaller (in rows) than the parent MS's table.
    spwNames = mytb.getcol('NAME')
    mytb.close()
    splitted = False
    if (maxSpw != len(spwNames)-1):
        splitted = True
        if (verbose): 
            print "maxSpw=%d != len(spwNames)=%d)" % (maxSpw, len(spwNames))
        if (parentms == ''):
            print "You appear to have split these data.  Please provide the parentms as an argument."
            return
        mytb.open(parentms+'/SPECTRAL_WINDOW')
        parentSpwNames = mytb.getcol('NAME')
        mytb.close()
        extractedRows = []
        index = []
        for s in range(len(spwNames)):
            if (len(spwNames[s]) == 0):
                print "This is an old dataset lacking values in the NAME column of the SPECTRAL_WINDOW table."
                return
            if (verbose): 
                print "Checking for %s in %s" % (spwNames[s], str(parentSpwNames))
            extractedRows.append(np.where(parentSpwNames == spwNames[s])[0][0])
            index.append(spws.index(extractedRows[-1]))
            if (verbose): 
                print "spw %d came from spw %d" % (s, extractedRows[-1])
# extractedRows = the row of the parent SPECTRAL_WINDOW table that matches 
#                 the split-out spw
#     index = the row of the ASDM_RECEIVER table that matches the split-out spw
        vis = parentms
    if (verbose): 
        print "spwNames = %s" % (str(spwNames))
        print "spws = %s" % (str(spws))
        print "bands = %s" % (str(bands))
        outputString = "LOs = "
        for LO in LOs:
            outputString += "%.3f, " % (LO[0]*1e-9)
        print outputString
        print "names = %s" % (str(names))
        print "index = %s" % (str(index))

    bbc = getBasebandNumbers(vis)
    if (verbose):
        print "basebands = %s" % (str(bbc))
    if (show): 
        print 'Row refers to the row number in the ASDM_RECEIVER table (starting at 0).'
        if (showCentralFreq):
            print 'Row spw BB RxBand CenFreq Nchan LO1(GHz) LO2(GHz) Sampler YIG(GHz) TFBoffset(MHz)'
        else:
            print 'Row spw BB RxBand Ch1Freq Nchan LO1(GHz) LO2(GHz) Sampler YIG(GHz) TFBoffset(MHz)'

    # Loop over all rows in the ASDM_RECEIVER table, unless we've split, in 
    # which case this will loop over the N spws in the table.
    mymsmd = createCasaTool(msmdtool)
    mymsmd.open(vis)
    for i in range(len(index)):
        if (verbose): 
            print "index[%d]=%d" % (i,index[i])
            print "spws[%d] = %d" % (index[i], spws[index[i]])
        myspw = spws[index[i]]
        meanFreqGHz = mymsmd.meanfreq(myspw) * (1e-9)
        if (verbose): 
            print "meanFreq = %f" % (meanFreqGHz)
        if (bands[index[i]].split('_')[-1].isdigit()):
            rxband = bands[index[i]].split('_')[-1]
        elif (showWVR):
            rxband = 'WVR'
        else:
            continue
        if (verbose): 
            print "rxband = %s" % (rxband)
        line = "%2d  %2d  %d %3s " % (spws.index(myspw), myspw, bbc[myspw], rxband)
        if (verbose): 
            print "line = %s" % (rxband)
        if (showCentralFreq):
            line += "%10.6f %4d " % (meanFreqGHz,len(mymsmd.chanfreqs(myspw)))
        else:
            line += "%10.6f %4d " % (mymsmd.chanfreqs(myspw)[0],len(mymsmd.chanfreqs(myspw)))
        if (receiverIds[index[i]] != 0):
            # receiverIds > 0 seem to be bogus repeats of spws
            continue
        if (LOs[index[i]][0] < 0):
            if (show): print line
            continue
        if (bbc[myspw] > 0):
            if (splitted):
                lo1s[i] = LOs[index[i]][0]
            else:
                lo1s[myspw] = LOs[index[i]][0]
            for j in range(len(LOs[index[i]])):
                if (j != 2):
                    line = line + '%10.6f' % (LOs[index[i]][j]*1e-9)
                else:
                    line = line + '%5.2f' % (LOs[index[i]][j]*1e-9)
        if (verbose):
            print "calling yigHarmonic"
        yig = LOs[index[i]][0] / yigHarmonic(bands[index[i]])
        if (verbose): 
            print "yig = %s" % (str(yig))
        if (yig > 0):
            line = line + ' %.6f' % (yig*1e-9)
        if (len(mymsmd.chanfreqs(myspw)) > 256):
            # work out what LO4 must have been
            LO1 = LOs[index[i]][0]
            LO2 = LOs[index[i]][1]
            LO3 = LOs[index[i]][2]
            if (sidebands[index[i]][0] == 'USB'):
                IFlocation = LO3 - (LO2 - (meanFreqGHz*1e9 - LO1))
            else:
                IFlocation = LO3 - (LO2 - (LO1 -  meanFreqGHz*1e9))
            LO4 = 2e9 + IFlocation
            TFBLOoffset = LO4 - 3e9
            line += '%9.3f %+8.3f' % (LO4 * 1e-6,  TFBLOoffset * 1e-6)
            
        if (bands[index[i]] == 'ALMA_RB_06'):
            if (len(LOs[index[i]]) > 1):
                if (LOs[index[i]][1] < 11.3e9 and LOs[index[i]][1] > 10.5e9):
                    line = line + ' YIG may leak into this spw'
                    yigLeakage = LOs[index[i]][0] + (LOs[index[i]][1] - LOs[index[i]][2]) + (yig - LOs[index[i]][1])
                    if (yigLeakage > 0):
                        line = line + ' at %.6f' % (yigLeakage*1e-9)
        if (show): print line
    if (verbose): 
        print "done 'for' loop"
    mymsmd.done()
    return(lo1s)

def mjdSecondsToMJDandUT(mjdsec):
    """
    Converts a value of MJD seconds into MJD, and into a UT date/time string.
    example: (56000.0, '2012-03-14 00:00:00 UT')
    Caveat: only works for a scalar input value
    Todd Hunter
    """
    myme = createCasaTool(metool)
    today = myme.epoch('utc','today')
    mjd = np.array(mjdsec) / 86400.
    today['m0']['value'] =  mjd
    myqa = createCasaTool(qatool)
    hhmmss = myqa.time(today['m0'], form='', prec=0, showform=False)[0]
#    print "hhmmss = ", hhmmss
    date = myqa.splitdate(today['m0'])
    myqa.done()
    utstring = "%s-%02d-%02d %s UT" % (date['year'],date['month'],date['monthday'],hhmmss)
    myme.done()
    return(mjd, utstring)

def ComputeSolarAzElForObservatory(mjdsec, mymsmd):
    pos =  mymsmd.observatoryposition()
    longitude = pos['m0']['value'] * 180/np.pi
    latitude = pos['m1']['value'] * 180/np.pi
    return(ComputeSolarAzElLatLong(mjdsec,latitude,longitude))
    
def ComputeSolarAzElLatLong(mjdsec,latitude,longitude):
    """
    Computes the apparent Az,El of the Sun for a specified time and location
    on Earth.  Latitude and longitude must arrive in degrees, with positive
    longitude meaning east of Greenwich.
    -- Todd Hunter
    """
    DEG_TO_RAD = math.pi/180.
    RAD_TO_DEG = 180/math.pi
    HRS_TO_RAD = math.pi/12.
    [RA,Dec] = ComputeSolarRADec(mjdsec)
    LST = ComputeLST(mjdsec, longitude)

    phi = latitude*DEG_TO_RAD
    hourAngle = HRS_TO_RAD*(LST - RA)
    azimuth = RAD_TO_DEG*math.atan2(math.sin(hourAngle), (math.cos(hourAngle)*math.sin(phi) - math.tan(Dec*DEG_TO_RAD)*math.cos(phi)))

    # the following is to convert from South=0 (which the French formula uses)
    # to North=0, which is what the rest of the world uses */
    azimuth += 180.0;

    if (azimuth > 360.0):
        azimuth -= 360.0
    if (azimuth < 0.0):
        azimuth += 360.0

    argument = math.sin(phi)*math.sin(Dec*DEG_TO_RAD) + math.cos(phi)*math.cos(Dec*DEG_TO_RAD) * math.cos(hourAngle);
    elevation = RAD_TO_DEG*math.asin(argument);
    return([azimuth,elevation])
    
def ComputeSolarRADec(mjdsec):
    """
    Computes the RA,Dec of the Sun for a specified time. -- Todd Hunter
    """   
    jd = mjdToJD(mjdsec/86400.)
    RAD_TO_DEG = 180/math.pi
    RAD_TO_HRS = (1.0/0.2617993877991509)
    DEG_TO_RAD = math.pi/180.
    T = (jd - 2451545.0) / 36525.0
    Lo = 280.46646 + 36000.76983*T + 0.0003032*T*T
    M = 357.52911 + 35999.05029*T - 0.0001537*T*T
    Mrad = M * DEG_TO_RAD
    e = 0.016708634 - 0.000042037*T - 0.0000001267*T*T
    C = (1.914602 - 0.004817*T - 0.000014*T*T) * math.sin(Mrad) +  (0.019993 - 0.000101*T) * math.sin(2*Mrad) + 0.000289*math.sin(3*Mrad)
    L = Lo + C
    nu = DEG_TO_RAD*(M + C)
    R = 1.000001018 * (1-e*e) / (1 + e*math.cos(nu))
    Omega = DEG_TO_RAD*(125.04 - 1934.136*T)
    mylambda = DEG_TO_RAD*(L - 0.00569 - 0.00478 * math.sin(Omega))  
    epsilon0 = (84381.448 - 46.8150*T - 0.00059*T*T + 0.001813*T*T*T) / 3600.
    epsilon = (epsilon0 + 0.00256 * math.cos(Omega)) * DEG_TO_RAD
    rightAscension = RAD_TO_HRS*math.atan2(math.cos(epsilon)*math.sin(mylambda), math.cos(mylambda))
    if (rightAscension < 0):
        rightAscension += 24.0
    argument = math.sin(epsilon) * math.sin(mylambda)
    declination = RAD_TO_DEG*math.asin(argument)
    return([rightAscension, declination])
    
def angularSeparation(ra0,dec0,ra1,dec1, returnComponents=False):
    """
    Usage:  angularSeparation(ra0,dec0,ra1,dec1)
    Computes the great circle angle between two celestial coordinates.
    using the Vincenty formula (from wikipedia) which is correct for all
    angles, as long as you use atan2() to handle a zero denominator.  
    See  http://en.wikipedia.org/wiki/Great_circle_distance
    ra,dec must be given in degrees, as is the output.
    It also works for the az,el coordinate system.
    Comopnent separations are field_0 minus field_1.
    See also angularSeparationRadians()
    -- Todd Hunter
    """
    ra0 *= math.pi/180.
    dec0 *= math.pi/180.
    ra1 *= math.pi/180.
    dec1 *= math.pi/180.
    deltaLong = ra0-ra1
    argument1 = (((math.cos(dec1)*math.sin(deltaLong))**2) +
                 ((math.cos(dec0)*math.sin(dec1)-math.sin(dec0)*math.cos(dec1)*math.cos(deltaLong))**2))**0.5
    argument2 = math.sin(dec0)*math.sin(dec1) + math.cos(dec0)*math.cos(dec1)*math.cos(deltaLong)
    angle = math.atan2(argument1, argument2) / (math.pi/180.)
    if (returnComponents):
        radegrees = (ra0-ra1)*180/math.pi
        decdegrees = (dec0-dec1)*180/math.pi
        retval = angle,radegrees,decdegrees
    else:
        retval = angle
    return(retval)

def ComputeDewPointCFromRHAndTempC(relativeHumidity, temperature):
    """
    inputs:  relativeHumidity in percentage, temperature in C
    output: in degrees C
    Uses formula from http://en.wikipedia.org/wiki/Dew_point#Calculating_the_dew_point
    Todd Hunter
    """
    temperature = np.array(temperature)            # protect against it being a list
    relativeHumidity = np.array(relativeHumidity)  # protect against it being a list
    es = 6.112*np.exp(17.67*temperature/(temperature+243.5))
    e = relativeHumidity*0.01*es
    dewPoint = 243.5*np.log(e/6.112)/(17.67-np.log(e/6.112))
    return(dewPoint)

def ComputeLST(mjdsec, longitude):
    """
    Computes the LST (in hours) for a specified time and longitude. 
    The input longitude is in degrees, where east of Greenwich is positive.
    -- Todd Hunter
    """
    JD = mjdToJD(mjdsec/86400.)
    T = (JD - 2451545.0) / 36525.0
    sidereal = 280.46061837 + 360.98564736629*(JD - 2451545.0) + 0.000387933*T*T - T*T*T/38710000.
    # now we have LST in Greenwich, need to scale back to site
    sidereal += longitude
    sidereal /= 360.
    sidereal -= np.floor(sidereal)
    sidereal *= 24.0
    if (sidereal < 0):
        sidereal += 24
    if (sidereal >= 24):
        sidereal -= 24
    return(sidereal)

def mjdToJD(MJD):
    """
    Converts an MJD value to JD
    """
    JD = MJD + 2400000.5
    return(JD)

def getScansForTimes(mymsmd, scantimes):
    scans = []
#    print "len(scantimes) = ", len(scantimes)
    for t in scantimes:
        scan = mymsmd.scansfortimes(t)[0]
#        print "scansfortime(%f) = " % (t), scan
        scans.append(scan)
    return(scans)
