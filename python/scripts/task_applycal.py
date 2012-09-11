import os
import time
import numpy as np
from taskinit import *
from parallel.parallel_task_helper import ParallelTaskHelper

def applycal(vis=None,
	     field=None,
	     spw=None,
	     intent=None,
	     selectdata=None,
	     timerange=None,
	     uvrange=None,
	     antenna=None,
	     scan=None,
             observation=None,
	     msselect=None,
	     gaintable=None,
	     gainfield=None,
	     interp=None,
	     spwmap=None,
	     gaincurve=None,
	     opacity=None,
	     parang=None,
	     calwt=None,
	     applymode=None,
	     flagbackup=None):

	#Python script
        casalog.origin('applycal')

        # Take care of the trivial parallelization
        if ParallelTaskHelper.isParallelMS(vis):
                # To be safe convert file names to absolute paths.
                gaintable = ParallelTaskHelper.findAbsPath(gaintable)
                helper = ParallelTaskHelper('applycal', locals())
                helper.go()
                return

	try:
                mycb = cbtool()
                if ((type(vis)==str) & (os.path.exists(vis))):
			# add CORRECTED_DATA column
                        mycb.open(filename=vis,compress=False,
				  addcorr=True,addmodel=False)
                else:
                        raise Exception, 'Visibility data set not found - please verify the name'

		# enforce default if unspecified
		if applymode=='':
			applymode='calflag'
			
		# Back up the flags, if requested (and if necessary)
		if (flagbackup and
		    (applymode!='calonly' and
		     applymode!='trial') ):
			tflocal = casac.testflagger()
			tflocal.open(vis)
			backup_flags(tflocal)
			tflocal.done()

		# Do data selection according to selectdata
		if (selectdata):
			# pass all data selection parameters in as specified
			mycb.selectvis(time=timerange,spw=spw,scan=scan,field=field,
				     intent=intent, observation=str(observation),
				     baseline=antenna,uvrange=uvrange,chanmode='none',
				     msselect=msselect);
		else:
			# selectdata=F, so time,scan,baseline,uvrange,msselect=''
			# using spw and field specifications only
			mycb.selectvis(time='',spw=spw,scan='',field=field,intent=intent,
                                     observation='', baseline='',uvrange='',
                                     chanmode='none', msselect='')

		# Arrange all of the applies
		# NB: calwt and interp apply to all; spwmap to gain only
		# TBD: interp and spwmap probably should be hardwired here?
		# TBD: trap case of ngainfield>ngaintab, etc.
		# First other tables...

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
						interp[igt]=thisinterp;
					thisinterp=interp[igt];
					
				mycb.setapply(t=0.0,table=gaintable[igt],field=thisgainfield,
					    calwt=calwt,spwmap=thisspwmap,interp=thisinterp)

		# ...and now the specialized terms
		# (BTW, interp irrelevant for these, since they are evaluated)

		# opacity (if non-trivially specified and any >0.0)
		opacarr=np.array(opacity)   # as numpy array for uniformity
		if (np.sum(opacarr)>0.0):
			# opacity transmitted as a list in all cases
			mycb.setapply(type='TOPAC',t=-1,opacity=opacarr.tolist(),calwt=calwt)

		if gaincurve: mycb.setapply(type='GAINCURVE',t=-1,calwt=calwt)

		# Apply parallactic angle, if requested
		if parang: mycb.setapply(type='P')

		mycb.correct(applymode)

		# report what the flags did
		reportflags(mycb.activityrec())
		
		mycb.close()

	        #write history
                try:
                        param_names = applycal.func_code.co_varnames[:applycal.func_code.co_argcount]
                        param_vals = [eval(p) for p in param_names]
                        write_history(mstool(), vis, 'applycal', param_names,
                                      param_vals, casalog)
                except Exception, instance:
                        casalog.post("*** Error \'%s\' updating HISTORY" % (instance),
                                     'WARN')

	except Exception, instance:
		print '*** Error ***',instance
		mycb.close()
		raise Exception, instance


def backup_flags(tflocal):

        # Create names like this:
        # before_applycal_1,
        # before_applycal_2,
        # before_applycal_3,
        # etc
        #
        # Generally  before_applycal_<i>, where i is the smallest
        # integer giving a name, which does not already exist
       
        existing = tflocal.getflagversionlist(printflags=False)

	# remove comments from strings
	existing = [x[0:x.find(' : ')] for x in existing]
	i = 1
	while True:
		versionname = "before_applycal_" + str(i)

		if not versionname in existing:
			break
		else:
			i = i + 1

        time_string = str(time.strftime('%Y-%m-%d %H:%M:%S'))

        tflocal.saveflagversion(versionname=versionname,
                           comment='Flag backup before applycal on ' + time_string,
                           merge='replace')


def reportflags(rec):
	if (rec.keys().count('origin')==1 and
	    rec['origin']=='Calibrater::correct' and
	    rec.keys().count('VisEquation')==1):
		casalog.post("Calibration apply flagging statistics:")
		VE=rec['VisEquation']
		nterm=len(VE)
		if nterm>0:
			casalog.post("  Total selected visibilities = "+str(VE['*1']['ndata']))
			casalog.post("  Flags:")
			for iterm in range(nterm):
				VEi=VE['*'+str(iterm+1)]
				flstr='   '+VEi['type']
				flstr+=': '
				flstr+='In: '+str(VEi['nflagIn'])
				flstr+=' ('+str(100.*VEi['nflagIn']/VEi['ndata'])+'%) --> '
				flstr+='Out: '+str(VEi['nflagOut'])
				flstr+=' ('+str(100.*VEi['nflagOut']/VEi['ndata'])+'%)'
				if (VEi.keys().count('table')>0):
					flstr+=' ('+VEi['table']+')'
				casalog.post(flstr)

