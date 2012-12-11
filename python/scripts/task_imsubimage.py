from taskinit import *

def imsubimage(
    imagename, outfile, region, mask, dropdeg,
    overwrite, verbose, stretch, wantreturn
):
    casalog.origin('imsubimage')
    myia = iatool()
    outia = None
    try:
        if (not myia.open(imagename)):
            raise Exception, "Cannot create image analysis tool using " + imagename
        outia = myia.subimage(
            outfile=outfile, region=region, mask=mask, dropdeg=dropdeg,
            overwrite=overwrite, list=verbose, stretch=stretch
        )
        if (wantreturn):
            return outia
        else:
            outia.done()
            return True
    except Exception, instance:
        if (outia):
            outia.done()
        casalog.post( str( '*** Error ***') + str(instance), 'SEVERE')
        raise
    finally:
        if (myia):
            myia.done()
        
