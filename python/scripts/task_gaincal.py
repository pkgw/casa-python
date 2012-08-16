import os
import numpy as np
from taskinit import *

def gaincal(vis=None,caltable=None,
	    field=None,spw=None,intent=None,
	    selectdata=None,timerange=None,uvrange=None,antenna=None,scan=None,
            observation=None, msselect=None,
	    solint=None,combine=None,preavg=None,refant=None,minblperant=None,
	    minsnr=None,solnorm=None,
	    gaintype=None,smodel=None,calmode=None,append=None,
	    splinetime=None,npointaver=None,phasewrap=None,
	    gaintable=None,gainfield=None,interp=None,spwmap=None,
	    gaincurve=None,opacity=None,parang=None):

	#Python script
        casalog.origin('gaincal')

	try: 
                mycb = cbtool()
                if ((type(vis)==str) & (os.path.exists(vis))):
                        mycb.open(filename=vis,compress=False,addcorr=False,addmodel=False)
                else:
                        raise Exception, 'Visibility data set not found - please verify the name'

		# Do data selection according to selectdata
		if (selectdata):
			# pass all data selection parameters in as specified
			mycb.selectvis(time=timerange,spw=spw, scan=scan, field=field,
				     intent=intent, observation=str(observation),
				     baseline=antenna,uvrange=uvrange,chanmode='none',
				     msselect=msselect);
		else:
			# selectdata=F, so time,scan,baseline,uvrange,msselect=''
			# using spw and field specifications only
			mycb.selectvis(time='',spw=spw,scan='',field=field,intent=intent,
                                     observation='', baseline='', uvrange='',
                                     chanmode='none', msselect='')

		# set the model, if specified
		if (len(smodel)>0):
			mycb.setptmodel(smodel);



		# Arrange apply of existing other calibrations 
		# First do the existing cal tables...
		ngaintab = 0;
		if (gaintable!=['']):
			ngaintab=len(gaintable)
		ngainfld = len(gainfield)
		nspwmap = len(spwmap)
		ninterp = len(interp)

		# handle list of list issues with spwmap
		if (nspwmap>0):
			if (type(spwmap[0])!=list):
				# first element not a list, only one spwmap specified
				# make it a list of list
				spwmap=[spwmap];
				nspwmap=1;

		for igt in range(ngaintab):
			if (gaintable[igt]!=''):

				# field selection is null unless specified
				thisgainfield=''
				if (igt<ngainfld):
					thisgainfield=gainfield[igt]
					
				# spwmap is null unless specifed
				thisspwmap=[-1]
				if (igt<nspwmap):
					thisspwmap=spwmap[igt];

				# interp is 'linear' unless specified
				thisinterp='linear'
				if (igt<ninterp):
					if (interp[igt]==''):
						interp[igt]=thisinterp
					thisinterp=interp[igt];

				mycb.setapply(t=0.0,table=gaintable[igt],field=thisgainfield,
					    calwt=True,spwmap=thisspwmap,interp=thisinterp)
		
		# ...and now the specialized terms
		# (BTW, interp irrelevant for these, since they are evaluated)

		# opacity (if non-trivially specified and any >0.0)
		opacarr=np.array(opacity)   # as numpy array for uniformity
		if (np.sum(opacarr)>0.0):
			# opacity transmitted as a list in all cases
			mycb.setapply(type='TOPAC',t=-1,opacity=opacarr.tolist(),calwt=True)

		if gaincurve: mycb.setapply(type='GAINCURVE',t=-1,calwt=True)

		# Apply parallactic angle, if requested
		if parang: mycb.setapply(type='P')

		# Set up for solving:  
		phaseonly=False
		if (gaintype=='G'):
			mycb.setsolve(type='G',t=solint,combine=combine,preavg=preavg,refant=refant,
				    minblperant=minblperant,
				    solnorm=solnorm,minsnr=minsnr,table=caltable,
				    apmode=calmode,phaseonly=phaseonly,append=append)
		elif (gaintype=='T'):
			mycb.setsolve(type='T',t=solint,combine=combine,preavg=preavg,refant=refant,
				    minblperant=minblperant,
				    solnorm=solnorm,minsnr=minsnr,table=caltable,
				    apmode=calmode,phaseonly=phaseonly,append=append)
		elif (gaintype=='K' or gaintype=='KCROSS' or gaintype=='XY+QU' or gaintype=='XYf+QU'):
			mycb.setsolve(type=gaintype,t=solint,combine=combine,preavg=preavg,refant=refant,
				    minblperant=minblperant,
				    solnorm=solnorm,minsnr=minsnr,table=caltable,
				    apmode=calmode,phaseonly=phaseonly,append=append)
		elif (gaintype=='GSPLINE'):
			mycb.setsolvegainspline(table=caltable,append=append,mode=calmode,
					      refant=refant,splinetime=splinetime,preavg=preavg,
					      npointaver=npointaver,phasewrap=phasewrap)
		mycb.solve()
		mycb.close()

	except Exception, instance:
		print '*** Error ***',instance
		mycb.close()
		raise Exception, instance

