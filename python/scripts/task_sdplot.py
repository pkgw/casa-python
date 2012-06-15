import os
from taskinit import *

import asap as sd
import pylab as pl
from asap import _to_list
from asap.scantable import is_scantable

def sdplot(infile, antenna, fluxunit, telescopeparm, specunit, restfreq, frame, doppler, scanlist, field, iflist, pollist, beamlist, scanaverage, timeaverage, tweight, polaverage, pweight, kernel, kwidth, plottype, stack, panel, flrange, sprange, linecat, linedop, subplot, colormap, linestyles, linewidth, histogram, header, headsize, plotstyle, margin, legendloc, outfile, overwrite):

        casalog.origin('sdplot')

        ###
        ### Now the actual task code
        ###
        try:
            if infile=='':
                raise Exception, 'infile is undefined'

            filename = os.path.expandvars(infile)
            filename = os.path.expanduser(filename)
            if not os.path.exists(filename):
                s = "File '%s' not found." % (filename)
                raise Exception, s
            if not overwrite and not outfile=='':
                outfilename = os.path.expandvars(outfile)
                outfilename = os.path.expanduser(outfilename)
                if os.path.exists(outfilename):
                    s = "Output file '%s' exist." % (outfilename)
                    raise Exception, s
            isScantable = is_scantable(infile)

            #load the data without time/pol averaging
            sorg = sd.scantable(infile,average=scanaverage,antenna=antenna)

            doCopy = (frame != '') or (doppler != '') or (restfreq != '') \
                     or (fluxunit != '' and fluxunit != sorg.get_fluxunit()) \
                     or (specunit != '' and specunit != sorg.get_unit())
            doCopy = doCopy and isScantable

            # A scantable selection
            # Scan selection
            scans = _to_list(scanlist,int) or []

            # IF selection
            ifs = _to_list(iflist,int) or []

            # Select polarizations
            pols = _to_list(pollist,int) or []

            # Beam selection
            beams = _to_list(beamlist,int) or []

            # Actual selection
            sel = sd.selector(scans=scans, ifs=ifs, pols=pols, beams=beams)

            # Select source names
            if ( field != '' ):
                    sel.set_name(field)
                    # NOTE: currently can only select one
                    # set of names this way, will probably
                    # need to do a set_query eventually

            try:
                #Apply the selection
                sorg.set_selection(sel)
            except Exception, instance:
                casalog.post( str(instance), priority = 'ERROR' )
                return
	    # For printing header information
	    ssel=sel.__str__()
            del sel

            # Copy scantable when usign disk storage not to modify
            # the original table.
            if doCopy and sd.rcParams['scantable.storage'] == 'disk':
                    s = sorg.copy()
            else:
                    s = sorg
            del sorg

            # get telescope name
            #'ATPKSMB', 'ATPKSHOH', 'ATMOPRA', 'DSS-43' (Tid), 'CEDUNA', and 'HOBART'
            antennaname = s.get_antennaname()

            # determine current fluxunit
            fluxunit_now = s.get_fluxunit()
            if ( antennaname == 'GBT'):
                            if (fluxunit_now == ''):
                                    casalog.post( "no fluxunit in the data. Set to Kelvin." )
                                    s.set_fluxunit('K')
                                    fluxunit_now = s.get_fluxunit()
            casalog.post( "Current fluxunit = "+fluxunit_now )

            # set flux unit string (be more permissive than ASAP)
            if ( fluxunit == 'k' ):
                    fluxunit = 'K'
            elif ( fluxunit == 'JY' or fluxunit == 'jy' ):
                    fluxunit = 'Jy'

            # fix the fluxunit if necessary
            if ( telescopeparm == 'FIX' or telescopeparm == 'fix' ):
                            if ( fluxunit != '' ):
                                    if ( fluxunit == fluxunit_now ):
                                            casalog.post( "No need to change default fluxunits" )
                                    else:
                                            s.set_fluxunit(fluxunit)
                                            casalog.post( "Reset default fluxunit to "+fluxunit )
                                            fluxunit_now = s.get_fluxunit()
                            else:
                                    casalog.post( "no fluxunit for set_fluxunit", priority = 'WARN' )


            elif ( fluxunit=='' or fluxunit==fluxunit_now ):
                    if ( fluxunit==fluxunit_now ):
                            casalog.post( "No need to convert fluxunits" )

            elif ( type(telescopeparm) == list ):
                    # User input telescope params
                    if ( len(telescopeparm) > 1 ):
                            D = telescopeparm[0]
                            eta = telescopeparm[1]
                            casalog.post( "Use phys.diam D = %5.1f m" % (D) )
                            casalog.post( "Use ap.eff. eta = %5.3f " % (eta) )
                            s.convert_flux(eta=eta,d=D,insitu=True)
                    elif ( len(telescopeparm) > 0 ):
                            jypk = telescopeparm[0]
                            casalog.post( "Use gain = %6.4f Jy/K " % (jypk) )
                            s.convert_flux(jyperk=jypk,insitu=True)
                    else:
                            casalog.post( "Empty telescope list" )

            elif ( telescopeparm=='' ):
                    if ( antennaname == 'GBT'):
                            # needs eventually to be in ASAP source code
                            casalog.post( "Convert fluxunit to "+fluxunit )
                            # THIS IS THE CHEESY PART
                            # Calculate ap.eff eta at rest freq
                            # Use Ruze law
                            #   eta=eta_0*exp(-(4pi*eps/lambda)**2)
                            # with
                            casalog.post( "Using GBT parameters" )
                            eps = 0.390  # mm
                            eta_0 = 0.71 # at infinite wavelength
                            # Ideally would use a freq in center of
                            # band, but rest freq is what I have
                            rf = s.get_restfreqs()[0][0]*1.0e-9 # GHz
                            eta = eta_0*pl.exp(-0.001757*(eps*rf)**2)
                            casalog.post( "Calculated ap.eff. eta = %5.3f " % (eta) )
                            casalog.post( "At rest frequency %5.3f GHz" % (rf) )
                            D = 104.9 # 100m x 110m
                            casalog.post( "Assume phys.diam D = %5.1f m" % (D) )
                            s.convert_flux(eta=eta,d=D,insitu=True)

                            casalog.post( "Successfully converted fluxunit to "+fluxunit )
                    elif ( antennaname in ['AT','ATPKSMB', 'ATPKSHOH', 'ATMOPRA', 'DSS-43', 'CEDUNA', 'HOBART']):
                            s.convert_flux(insitu=True)

                    else:
                            # Unknown telescope type
                            casalog.post( "Unknown telescope - cannot convert", priority = 'WARN' )


            # set spectral axis unit
            if ( specunit != '' ):
                    casalog.post( "Changing spectral axis to "+specunit )
                    s.set_unit(specunit)

            # set rest frequency
            if ( specunit == 'km/s' and restfreq != '' ):
                    if ( type(restfreq) == float ):
                            fval = restfreq
                    elif qa.compare(restfreq, 'Hz'):
                            qrfhz = qa.convert(restfreq, 'Hz')
                            fval = qrfhz['value']
                    else:
                            errstr = "Invalid rest frequency %s. Must be in the unit of '*Hz' " % restfreq
                            raise Exception, errstr
                    casalog.post( 'Set rest frequency to %d Hz' %(fval) )
                    s.set_restfreqs(freqs=fval)

            # reset frame and doppler if needed
            if ( frame != '' ):
                    casalog.post( "Changing frequency frame to "+frame )
                    s.set_freqframe(frame)
            else:
                    casalog.post( 'Using current frequency frame' )

            if ( doppler != '' ):
                    if ( doppler == 'radio' ):
                            ddoppler = 'RADIO'
                    elif ( doppler == 'optical' ):
                            ddoppler = 'OPTICAL'
                    elif ( doppler == 'z' ):
                            ddoppler = 'Z'
                    else:
                            ddoppler = doppler

                    s.set_doppler(ddoppler)
            else:
                    casalog.post( 'Using current doppler convention' )

            # Averaging
            # average over time (scantable is already scan averaged if necessary)
            if ( timeaverage and not scanaverage):
                    if tweight=='none':
                            del s
                            errmsg = "Please specify weight type of time averaging"
                            raise Exception,errmsg
                    stave=sd.average_time(s,scanav=scanaverage, weight=tweight)
            else:
                    # No time averaging
                    stave = s
            del s

            # average over polarization
            if ( polaverage ):
                    if pweight=='none':
                            del stave
                            errmsg = "Please specify weight type of polarization averaging"
                            raise Exception,errmsg
                    np = stave.npol()
                    if ( np > 1 ):
                            spave=stave.average_pol(weight=pweight)
                    else:
                            # only single polarization
                            casalog.post( "Single polarization data - no need to average" )
                            spave=stave
            else:
                    # No pol averaging
                    spave=stave
            del stave


	    # Reload plotter if necessary
            sd.plotter._assert_plotter(action="reload")

	    # Set subplot layout
            if subplot > 10:
                    row = int(subplot/10)
                    col = (subplot % 10)
                    sd.plotter.set_layout(rows=row,cols=col,refresh=False)
	    else:
                    if subplot > -1:
                            casalog.post(("Invalid subplot value, %d, is ignored. It should be in between 11 and 99." % subplot),priority="WARN")
                    sd.plotter.set_layout(refresh=False)

	    # Set subplot margins
	    if margin != sd.plotter._margins:
		    sd.plotter.set_margin(margin=margin,refresh=False)

            # Plotting
	    asaplot=False
            if plottype=='pointing':
                    if outfile != '': 
                           sd.plotter.plotpointing(spave,outfile)
                    else:
                           sd.plotter.plotpointing(spave)
                    del spave
            elif plottype=='azel':
                    if outfile != '': 
                           sd.plotter.plotazel(spave,outfile)
                    else:
                           sd.plotter.plotazel(spave)
                    del spave
            elif plottype=='totalpower':
		    asaplot=True
                    sd.plotter.plottp(spave)
                    del spave
            else:
		    asaplot=True
                    if spave.nchan()==1:
                           errmsg="Trying to plot the continuum/total power data in 'spectra' mode,\
                                   please use other plottype options" 
                           raise Exception,errmsg

                    # Smooth the spectrum (if desired)

                    if kernel == '': kernel = 'none'
                    if ( kernel != 'none' and (not (kwidth<=0 and kernel!='hanning'))):
                            casalog.post( "Smoothing spectrum with kernel "+kernel )
                            spave.smooth(kernel,kwidth)

                    # Plot final spectrum
                    # each IF is separate panel, pols stacked
		    refresh=False
                    #sd.plotter.plot(spave)
                    sd.plotter.set_data(spave,refresh=refresh)
                    del spave
                    sd.plotter.set_mode(stacking=stack,panelling=panel,refresh=refresh)

		    # Set colormap, linestyles, and linewidth of plots
		    
		    ncolor = 0
		    if colormap != 'none': 
			    colmap = colormap
			    ncolor=len(colmap.split())
		    elif linestyles == 'none': 
			    colmap = "green red black cyan magenta orange blue purple yellow pink"
			    ucm = sd.rcParams['plotter.colours']
			    if isinstance(ucm,str) and len(ucm) > 0: colmap = ucm
			    ncolor=len(colmap.split())
			    del ucm
		    else: colmap=None

		    if linestyles != 'none': lines=linestyles
		    elif ncolor <= 1: 
			    lines = "line dashed dotted dashdot"
			    uls = sd.rcParams['plotter.linestyles']
			    if isinstance(uls,str) and len(uls) > 0: lines = uls
			    del uls
		    else: lines=None
		
		    if isinstance(linewidth,int) or isinstance (linewidth,float):
			    lwidth = linewidth
		    else:
                            casalog.post( "Invalid linewidth. linewidth is ignored and set to 1.", priority = 'WARN' )
			    lwidth = 1

		    # set plot colors
		    if colmap is not None:
			    if ncolor > 1 and lines is not None:
                                    casalog.post( "'linestyles' is valid only for single colour plot.\n...Ignoring 'linestyles'.", priority = 'WARN' )
			    sd.plotter.set_colors(colmap,refresh=refresh)
		    else:
			    if lines is not None:
				    tmpcol="black"
				    #print "INFO: plot colour is set to '",tmpcol,"'"
                                    casalog.post( "plot colour is set to '"+tmpcol+"'" )
				    sd.plotter.set_colors(tmpcol,refresh=refresh)
		    # set linestyles and/or linewidth
		    # so far, linestyles can be specified only if a color is assigned
		    #if lines is not None or linewidth is not None:
		    #        sd.plotter.set_linestyles(lines, linewidth,refresh=refresh)
		    sd.plotter.set_linestyles(lines, lwidth,refresh=refresh)
                    # Plot red x-axis at y=0 (currently disabled)
                    # sd.plotter.axhline(color='r',linewidth=2)
		    sd.plotter.set_histogram(hist=histogram,refresh=refresh)

                    # Set axis ranges (if requested)
                    if len(flrange)==1:
                            #print "flrange needs 2 limits - ignoring"
                            casalog.post( "flrange needs 2 limits - ignoring" )
                    if len(sprange)==1:
                            #print "sprange needs 2 limits - ignoring"
                            casalog.post( "sprange needs 2 limits - ignoring" )
                    if ( len(sprange) > 1 ):
                            if ( len(flrange) > 1 ):
                                    sd.plotter.set_range(sprange[0],sprange[1],flrange[0],flrange[1],refresh=refresh)
                            else:
				    sd.plotter.set_range(sprange[0],sprange[1],refresh=refresh)
                    elif ( len(flrange) > 1 ):
			    sd.plotter.set_range(ystart=flrange[0],yend=flrange[1],refresh=refresh)
                    else:
                    # Set default range explicitly (in case range was ever set)
                            sd.plotter.set_range(refresh=refresh)

		    # legend position
		    loc=1
		    if plotstyle: loc=legendloc
		    sd.plotter.set_legend(mode=loc,refresh=refresh)
		    
		    # The actual plotting
		    sd.plotter.plot()
		    
                    # Line catalog
                    dolinc=False
                    if ( linecat != 'none' and linecat != '' ):
                            # Use jpl catalog for now (later allow custom catalogs)

                            casapath=os.environ['CASAPATH'].split()
                            catpath=casapath[0]+'/data/catalogs/lines'
                            catname=catpath+'/jpl_asap.tbl'
                            # TEMPORARY: hard-wire to my version
                            # catname='/home/sandrock/smyers/NAUG/Tasks/jpl.tbl'
                            # FOR LOCAL CATALOGS:
                            # catname='jpl.tbl'
                            try:
                                    linc=sd.linecatalog(catname)
                                    dolinc=True
                            except:
                                    casalog.post( "Could not find catalog at "+catname, priority = False )
                                    dolinc=False
                            if ( dolinc ):
                                    if ( len(sprange)>1 ):
                                            if ( specunit=='GHz' or specunit=='MHz' ):
                                                    linc.set_frequency_limits(sprange[0],sprange[1],specunit)
                                            else:
                                                    casalog.post( "sd.linecatalog.set_frequency_limits accepts onlyGHz and MHz", priority = 'WARN' )
                                                    casalog.post( "continuing without sprange selection on catalog", priority = 'WARN' )
                                    if ( linecat != 'all' and linecat != 'ALL' ):
                                            # do some molecule selection
                                            linc.set_name(linecat)
                                    # Plot up the selected part of the line catalog
                                    # use doppler offset
                                    sd.plotter.plot_lines(linc,doppler=linedop)
                                    del linc

	    # List observation header
	    if header and (not plotstyle or margin==[]):
		    # set margin for the header
		    sd.plotter._plotter.figure.subplots_adjust(top=0.8)
	    datname='Data File:     '+infile
	    sd.plotter.print_header(plot=(header and asaplot),fontsize=headsize,
	                            logger=True,selstr=ssel,extrastr=datname)
	    del ssel, datname

            # Hardcopy
            if ( plottype in ['spectra','totalpower'] and outfile != '' ):
                    # currently no way w/o screen display first
                    sd.plotter.save(outfile)

            # Do some clean up
            #import gc
            #gc.collect()

            # DONE

        except Exception, instance:
                casalog.post( str(instance), priority = 'ERROR' )
                return

