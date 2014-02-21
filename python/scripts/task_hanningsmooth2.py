import os
import shutil
import string
import copy
import math
from taskinit import *
from task_mstransform import MSTHelper
import testhelper as th

def hanningsmooth2(vis=None, 
                   outputvis=None,
                   createmms=None,
                   separationaxis=None,
                   numsubms=None,
                   parallel=None,
                   ddistart=None,        # to be used by mstransform internally. Hidden parameter!
                   field=None,
                   spw=None, 
                   scan=None, 
                   antenna=None, 
                   correlation=None,
                   timerange=None, 
                   intent=None,
                   array=None,
                   uvrange=None,
                   observation=None,
                   feed=None,
                   datacolumn=None, 
                   ):

    """Hanning smooth frequency channel data to remove Gibbs ringing

    """

    casalog.origin('hanningsmooth2')
    
    
    # Initiate the helper class    
    msth = MSTHelper(locals()) 
    
    # Validate input and output parameters
    try:
        msth.setupIO()
    except Exception, instance:
        casalog.post('%s'%instance,'ERROR')
        return False

    # Create an output MMS
    if createmms:   
        
        # The user decides to run in parallel or sequential
        if not parallel:
            casalog.post('Will process the MS in sequential')
            msth.bypassParallelProcessing(1)
        else:
            msth.bypassParallelProcessing(0)
            casalog.post('Will process the MS in parallel')

        # Get a cluster
        msth.setupCluster(thistask='hanningsmooth2')
        
        # Execute the jobs using simple_cluster
        try:
            msth.go()
        except Exception, instance:
            casalog.post('%s'%instance,'ERROR')
            return False
                    
        return True

    # Actual task code starts here

    # Create local copies of the MSTransform and ms tools
    mtlocal = mttool()
    mslocal = mstool()

    # Specifics for this task, different from mstransform
    # default datacolumn='all'
    # default createmms=False
    # outputvis is TBD
    # copying of other vis columns to output is TBD
    # if requested datacolumn=CORRECTED doesn't exist, it uses DATA

    try:
                    
        # Gather all the parameters in a dictionary.        
        config = {}
        config = msth.setupParameters(inputms=vis, outputms=outputvis, field=field, 
                    spw=spw, array=array, scan=scan, antenna=antenna, correlation=correlation,
                    uvrange=uvrange,timerange=timerange, intent=intent, observation=observation)
        
        # ddistart will be used in the tool when re-indexing the spw table
        config['ddistart'] = ddistart
        
        # Check if CORRECTED column exists, when requested
        datacolumn = datacolumn.upper()
        if datacolumn == 'CORRECTED':
            dc = 'CORRECTED_DATA'
            if th.getColDesc(vis,dc) == {}:
                casalog.post('Input CORRECTED_DATA does not exist. Will use DATA','WARN')
                datacolumn = 'DATA'
             
        casalog.post('Will use datacolumn = %s'%datacolumn, 'DEBUG')
        config['datacolumn'] = datacolumn
        
        # Call MSTransform framework with hanning=True
        config['hanning'] = True

        # Configure the tool 
        casalog.post('%s'%config, 'DEBUG1')
        mtlocal.config(config)
        
        # Open the MS, select the data and configure the output
        mtlocal.open()
        
        # Run the tool
        casalog.post('Apply Hanning smoothing on data')
        mtlocal.run()        
            
        mtlocal.done()
                    
    except Exception, instance:
        mtlocal.done()
        casalog.post('%s'%instance,'ERROR')
        return False

    # Write history to output MS, not the input ms.
    try:
        param_names = hanningsmooth2.func_code.co_varnames[:hanningsmooth2.func_code.co_argcount]
        param_vals = [eval(p) for p in param_names]
        casalog.post('Updating the history in the output', 'DEBUG1')
        write_history(mslocal, outputvis, 'hanningsmooth2', param_names,
                      param_vals, casalog)
    except Exception, instance:
        casalog.post("*** Error \'%s\' updating HISTORY" % (instance),
                     'WARN')
        return False

    mslocal = None
    
    return True
 
 
   
# OLD CODE. DELETE LATER

#     try:
#         casalog.origin('hanningsmooth2')
#         casalog.post('vis=\''+vis+'\', datacolumn=\''+datacolumn+'\', outputvis=\''+outputvis+'\'', 'INFO')
#         newvis = vis;
#         
#         if os.path.exists(outputvis):
#             ms.close()
#             raise Exception, "Output MS %s already exists - will not overwrite." % outputvis
# 
#         if(type(outputvis)==str and not outputvis==''):
#             newvis = outputvis
#             casalog.post('copying '+vis+' to '+newvis , 'INFO')
#             tb.open(vis)
#             tmptb = tb.copy(newvis, deep=True, valuecopy=True)
#             tmptb.close()
#             # note that the resulting copy is writable even if the original was read-only
#             tb.close()
#         else:
#             newvis = vis
# 
#         if ((type(newvis)==str) & (os.path.exists(newvis))):
#             ms.open(thems=newvis,nomodify=False)
#         else:
#             raise Exception, 'Visibility data set not found - please verify the name'
#         
#         ms.hanningsmooth2(datacolumn=str.lower(datacolumn))
#         
#         # write history
#         ms.writehistory(message='taskname = hanningsmooth2',origin='hanningsmooth2')
#         ms.writehistory(message='vis         = "'+str(vis)+'"',origin='hanningsmooth2')
#         ms.writehistory(message='datacolumn  = "'+str(datacolumn)+'"',origin='hanningsmooth2')
#         ms.writehistory(message='outputvis   = "'+str(outputvis)+'"',origin='hanningsmooth2')
#         ms.close()
#         
#     except Exception, instance:
#         print '*** Error ***',instance
#         return