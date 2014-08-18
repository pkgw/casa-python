from taskinit import casalog, gentools
import pylab as pl
import numpy
import os

import asap as sd

tb = gentools(['tb'])[0]

class Raster(object):
    def __init__(self, infile):
        self.infile = infile
        self.rows = None
        self.mjd_range = None
        self.spw = None
        self.pol = None
        self.gaplist = []
        self.ngap = 0

    @property
    def nominal_spw(self):
        if hasattr(self, '_nominal_spw') and getattr(self, '_nominal_spw') is not None:
            return self._nominal_spw
        
        self._nominal_spw = None
        tb.open(self.infile)
        tsel = tb.query('SRCTYPE==0') # on-source
        spw_list = numpy.unique(tsel.getcol('IFNO'))
        for spw in spw_list:
            tsel = tb.query('IFNO==%s'%(spw))
            if tsel.nrows() > 0:
                nchan = len(tsel.getcell('SPECTRA',0))
                if nchan > 4: # ignore channel-averaged and WVR
                    self._nominal_spw = spw
                    tsel.close()
                    break
            tsel.close()
        tb.close()
        return self._nominal_spw

    @property
    def nominal_pol(self):
        if hasattr(self, '_nominal_pol') and getattr(self, '_nominal_pol') is not None:
            return self._nominal_pol

        self._nominal_pol = None
        nominal_spw = self.nominal_spw
        tb.open(self.infile)
        tsel = tb.query('SRCTYPE==0 && IFNO==%s'%(nominal_spw))
        if tsel.nrows() > 0:
            self._nominal_pol = tsel.getcell('POLNO', 0)
        tsel.close()
        tb.close()
        return self._nominal_pol

    def detect(self, spw=None, pol=None):
        if spw is None:
            self.spw = self.nominal_spw
        else:
            self.spw = spw
        if pol is None:
            self.pol = self.nominal_pol
        else:
            self.pol = pol
        casalog.post('spw, pol = %s, %s'%(self.spw, self.pol))
        self.gaplist = detect_gap(self.infile, self.spw, self.pol)
        self.ngap = len(self.gaplist)
    
        casalog.post('gaplist=%s (length %s)'%(self.gaplist, self.ngap), priority='DEBUG')
        casalog.post('%s rows detected'%(self.ngap), priority='INFO')
        
    def select(self, rowid):
        if rowid >= self.ngap - 1:
            raise IndexError('row index %s is out of range (number of rows detected: %s)'%(rowid,ngap-1))

        tb.open(self.infile)
        tsel = tb.query('SRCTYPE==0 && IFNO==%s && POLNO==%s'%(self.spw,self.pol))
        allrows = tsel.rownumbers()
        alltimes = tsel.getcol('TIME')
        allintervals = tsel.getcol('INTERVAL')
        tsel.close()
        tb.close()

        rows = allrows[self.gaplist[rowid]:self.gaplist[rowid+1]]
        casalog.post('rownumber list for rowid %s: %s'%(rowid, rows), priority='DEBUG')
        times = alltimes[self.gaplist[rowid]:self.gaplist[rowid+1]]
        mean_interval = allintervals.mean() / 86400.0

        self.mjd_range = (times.min() - 0.1 * mean_interval, times.max() + 0.1 * mean_interval,)
        casalog.post('time range: %s ~ %s'%(self.mjd_range), priority='DEBUG')
        
        if len(rows) > 0:
            self.rows = map(int, rows)
    
        return rows

    def asscantable(self, rowid=None):
        s = sd.scantable(self.infile, average=False)
        sel = self.asselector(rowid)
        s.set_selection(sel)
        return s

    def astaql(self, rowid=None):
        rows = self.select(rowid)

        taql = 'TIME > %s && TIME < %s'%(self.mjd_range)
        return taql
    
    def asselector(self, rowid=None, input_selector=None):
        taql = self.astaql(rowid)
        
        if input_selector is None:
            sel = sd.selector(query=taql)
        else:
            sel = sd.selector(input_selector)
            input_query = sel.get_query()
            if len(input_query) == 0:
                sel.set_query(taql)
            else:
                new_query = '(%s) && (%s)'%(input_query,taql)
                sel.set_query(new_query)
        return sel

    def plot_row(self, rowid):
        taql = self.astaql(rowid)

        tb.open(self.infile)
        tsel = tb.query('SRCTYPE==0 && IFNO==%s && POLNO==%s'%(self.spw,self.pol))
        alldir = tsel.getcol('DIRECTION')
        tsel.close()
        
        tsel = tb.query(taql)
        tsel.nrows()
        dirs = tsel.getcol('DIRECTION')
        tsel.close()
        tb.close()
   
        pl.clf()
        pl.plot(alldir[0], alldir[1], 'o', color='#aaaaaa', markeredgewidth=0)
        pl.plot(dirs[0], dirs[1], 'o', color='g')        
                
def detect_gap(infile, spw, pol):
    tb.open(infile)
    tsel = tb.query('SRCTYPE==0 && IFNO==%s && POLNO==%s'%(spw,pol))
    alldir = tsel.getcol('DIRECTION')
    timestamp = tsel.getcol('TIME')
    interval = tsel.getcol('INTERVAL')
    rows = tsel.rownumbers()
    tsel.close()
    tb.close()

    return _detect_gap(timestamp)


def _detect_gap(timestamp, threshold=None):
    nrow = len(timestamp)

    if nrow == 0:
        gaplist = []
    elif nrow == 1:
        gaplist = [0,1]
    else:
        dt=(timestamp[1:]-timestamp[:-1])*86400.0
        if threshold is None:
            # detect gap with threshold of 5 * median value
            dtm = 5.0 * numpy.median(dt[dt.nonzero()])
        else:
            dtm = threshold
        gaplist=[0]
        gap=(dt>dtm)
        gaplist.extend(numpy.where(dt > dtm * 5)[0] + 1)
        if gaplist[-1] != nrow:
            gaplist.append(nrow)

    return gaplist
