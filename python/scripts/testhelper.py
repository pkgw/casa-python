from casac import casac
import os
import sys
import commands
import math
import shutil
import string
import time
from taskinit import casalog,tb
import numpy as np

'''
A set of common helper functions for unit tests:
   compTables - compare two CASA tables
   compVarColTables - Compare a variable column of two tables
   DictDiffer - a class with methods to take a difference of two 
                Python dictionaries
   verify_ms - Function to verify spw and channels information in an MS   
   create_input - Save the string in a text file with the given name           
'''

def compTables(referencetab, testtab, excludecols, tolerance=0.001):

    """
    compTables - compare two CASA tables
    
       referencetab - the table which is assumed to be correct

       testtab - the table which is to be compared to referencetab

       excludecols - list of column names which are to be ignored

       tolerance - permitted fractional difference (default 0.001 = 0.1 percent)
    """

    rval = True

    tb2 = casac.table()

    tb.open(referencetab)
    cnames = tb.colnames()

    #print cnames

    tb2.open(testtab)

    try:
        for c in cnames:
            if c in excludecols:
                continue
            print c
            a = 0
            try:
                a = tb.getcol(c)
            except:
                rval = False
                print 'Error accessing column ', c, ' in table ', referencetab
                print sys.exc_info()[0]
                break
            #print a
            b = 0
            try:
                b = tb2.getcol(c)
            except:
                rval = False
                print 'Error accessing column ', c, ' in table ', testtab
                print sys.exc_info()[0]
                break
            #print b
            if not (len(a)==len(b)):
                print 'Column ',c,' has different length in tables ', referencetab, ' and ', testtab
                print a
                print b
                rval = False
                break
            else:
                if not (a==b).all():
                    differs = False
                    for i in range(0,len(a)):
                        if (type(a[i])==float):
                            if (abs(a[i]-b[i]) > tolerance*abs(a[i]+b[i])):
                                print 'Column ',c,' differs in tables ', referencetab, ' and ', testtab
                                print i
                                print a[i]
                                print b[i]
                                differs = True
                                break
                        elif (type(a[i])==int):
                            if (abs(a[i]-b[i]) > 0):
                                print 'Column ',c,' differs in tables ', referencetab, ' and ', testtab
                                print i
                                print a[i]
                                print b[i]
                                differs = True
                                break
                        elif (type(a[i])==str):
                            if not (a[i]==b[i]):
                                print 'Column ',c,' differs in tables ', referencetab, ' and ', testtab
                                print i
                                print a[i]
                                print b[i]
                                differs = True
                                break
                        elif (type(a[i])==list or type(a[i])==np.ndarray):
                            for j in range(0,len(a[i])):
                                if (type(a[i][j])==float or type(a[i][j])==int):
                                    if (abs(a[i][j]-b[i][j]) > tolerance*abs(a[i][j]+b[i][j])):
                                        print 'Column ',c,' differs in tables ', referencetab, ' and ', testtab
                                        print i, j
                                        print a[i][j]
                                        print b[i][j]
                                        differs = True
                                        break
                                elif (type(a[i][j])==list or type(a[i][j])==np.ndarray):
                                    for k in range(0,len(a[i][j])):
                                        if (abs(a[i][j][k]-b[i][j][k]) > tolerance*abs(a[i][j][k]+b[i][j][k])):
                                            print 'Column ',c,' differs in tables ', referencetab, ' and ', testtab
                                            print i, j, k
                                            print a[i][j][k]
                                            print b[i][j][k]
                                            differs = True
                                            break
                    if differs:
                        rval = False
                        break
    finally:
        tb.close()
        tb2.close()

    if rval:
        print 'Tables ', referencetab, ' and ', testtab, ' agree.'

    return rval

    
def compVarColTables(referencetab, testtab, varcol, tolerance=0.):
    '''Compare a variable column of two tables.
       referencetab  --> a reference table
       testtab       --> a table to verify
       varcol        --> the name of a variable column (str)
       Returns True or False.
    '''
    
    retval = True
    tb2 = casac.table()

    tb.open(referencetab)
    cnames = tb.colnames()

    tb2.open(testtab)
    col = varcol
    if tb.isvarcol(col) and tb2.isvarcol(col):
        try:
            # First check
            if tb.nrows() != tb2.nrows():
                print 'Length of %s differ from %s, %s!=%s'%(referencetab,testtab,len(rk),len(tk))
                retval = False
            else:
                for therow in xrange(tb.nrows()):
            
                    rdata = tb.getcell(col,therow)
                    tdata = tb2.getcell(col,therow)

#                    if not (rdata==tdata).all():
                    if not rdata.all()==tdata.all():
                        if (tolerance>0.):
                            differs=False
                            for j in range(0,len(rdata)):
                                if (type(rdata[j])==float or type(rdata[j])==int):
                                    if (abs(rdata[j]-tdata[j]) > tolerance*abs(rdata[j]+tdata[j])):
#                                        print 'Column ', col,' differs in tables ', referencetab, ' and ', testtab
#                                        print therow, j
#                                        print rdata[j]
#                                        print tdata[j]
                                        differs = True
                                elif (type(rdata[j])==list or type(rdata[j])==np.ndarray):
                                    for k in range(0,len(rdata[j])):
                                        if (abs(rdata[j][k]-tdata[j][k]) > tolerance*abs(rdata[j][k]+tdata[j][k])):
#                                            print 'Column ', col,' differs in tables ', referencetab, ' and ', testtab
#                                            print therow, j, k
#                                            print rdata[j][k]
#                                            print tdata[j][k]
                                            differs = True
                                if differs:
                                    print 'ERROR: Column %s of %s and %s do not agree within tolerance %s'%(col,referencetab, testtab, tolerance)
                                    retval = False
                                    break
                        else:
                            print 'ERROR: Column %s of %s and %s do not agree.'%(col,referencetab, testtab)
                            print 'ERROR: First row to differ is row=%s'%therow
                            retval = False
                            break
        finally:
            tb.close()
            tb2.close()
    
    else:
        print 'Columns are not varcolumns.'
        retval = False

    if retval:
        print 'Column %s of %s and %s agree'%(col,referencetab, testtab)
        
    return retval

    
        
class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    Example:
            mydiff = DictDiffer(dict1, dict2)
            mydiff.changed()  # to show what has changed
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect 
    def removed(self):
        return self.set_past - self.intersect 
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])            
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])


def verifyMS(msname, expnumspws, expnumchan, inspw, expchanfreqs=[], ignoreflags=False):
    '''Function to verify spw and channels information in an MS
       msname        --> name of MS to verify
       expnumspws    --> expected number of SPWs in the MS
       expnumchan    --> expected number of channels in spw
       inspw         --> SPW ID
       expchanfreqs  --> numpy array with expected channel frequencies
       ignoreflags   --> do not check the FLAG column
           Returns a list with True or False and a state message'''
    
    msg = ''
    tb.open(msname+'/SPECTRAL_WINDOW')
    nc = tb.getcell("NUM_CHAN", inspw)
    nr = tb.nrows()
    cf = tb.getcell("CHAN_FREQ", inspw)
    tb.close()
    # After channel selection/average, need to know the exact row number to check,
    # ignore this check in these cases.
    if not ignoreflags:
        tb.open(msname)
        dimdata = tb.getcell("FLAG", 0)[0].size
        tb.close()
        
    if not (nr==expnumspws):
        msg =  "Found "+str(nr)+", expected "+str(expnumspws)+" spectral windows in "+msname
        return [False,msg]
    if not (nc == expnumchan):
        msg = "Found "+ str(nc) +", expected "+str(expnumchan)+" channels in spw "+str(inspw)+" in "+msname
        return [False,msg]
    if not ignoreflags and (dimdata != expnumchan):
        msg = "Found "+ str(dimdata) +", expected "+str(expnumchan)+" channels in FLAG column in "+msname
        return [False,msg]

    if not (expchanfreqs==[]):
        print "Testing channel frequencies ..."
#        print cf
#        print expchanfreqs
        if not (expchanfreqs.size == expnumchan):
            msg =  "Internal error: array of expected channel freqs should have dimension ", expnumchan
            return [False,msg]
        df = (cf - expchanfreqs)/expchanfreqs
        if not (abs(df) < 1E-8).all:
            msg = "channel frequencies in spw "+str(inspw)+" differ from expected values by (relative error) "+str(df)
            return [False,msg]

    return [True,msg]


def getChannels(msname, spwid, chanlist):
    '''From a list of channel indices, return their frequencies
       msname       --> name of MS
       spwid        --> spw ID
       chanlist     --> list of channel indices
    Return a numpy array, the same size of chanlist, with the frequencies'''
    
    try:
        try:
            tb.open(msname+'/SPECTRAL_WINDOW')
        except:
            print 'Cannot open table '+msname+'SPECTRAL_WINDOW'
            
        cf = tb.getcell("CHAN_FREQ", spwid)
        
        # Get only the requested channels
        b = [cf[i] for i in chanlist]
        selchans = np.array(b)
    
    finally:
        tb.close()
        
    return selchans
    
    
def getColDesc(table, colname):
    '''Get the description of a column in a table
       table    --> name of table or MS
       colname  --> column name
    Return a dictionary with the column description'''
    
    coldesc = {}
    try:
        try:
            tb.open(table)            
            tcols = tb.colnames()
            if tcols.__contains__(colname):
                coldesc = tb.getcoldesc(colname)
        except:
            pass                        
    finally:
        tb.close()
        
    return coldesc

def getVarCol(table, colname):
    '''Return the requested variable column
       table    --> name of table or MS
       colname  --> column name
    Return the column as a dictionary'''
    
    col = {}
    try:
        try:
            tb.open(table)
            col = tb.getvarcol(colname)
        except:
            print 'Cannot open table '+table

    finally:
        tb.close()
        
    return col
   
def createInput(str_text, filename):
    '''Save the string in a text file with the given name
    str_text    --> string to save
    filename    --> name of the file to save
            It will remove the filename if it exist!'''
    
    inp = filename    
    cmd = str_text
    
    # remove file first
    if os.path.exists(inp):
        os.system('rm -f '+ inp)
    
    try:
        # save to a file    
        with open(inp, 'w') as f:
            f.write(cmd)
            
    finally:  
        f.close()
    
    return

def calculateHanning(dataB,data,dataA):
    '''Calculate the Hanning smoothing of each element'''
    const0 = 0.25
    const1 = 0.5
    const2 = 0.25
    S = const0*dataB + const1*data + const2*dataA
    return S


def getTileShape(mydict, column='DATA'):
    '''Return the value of TileShape for a given column
       in the dictionary from data managers (tb.getdminfo).
       mydict --> dictionary from tb.getdminfo()
       column --> column where to look for TileShape'''
    
    tsh = {}
    for key, value in mydict.items():
        if mydict[key]['COLUMNS'][0] == column:
             # Dictionary for requested column
            hyp = mydict[key]['SPEC']['HYPERCUBES']
                    
             # This is the HYPERCUBES dictionary
            for hk in hyp.keys():
                tsh = hyp[hk]['TileShape']
                break
                    
            break
    
    return tsh
                    
