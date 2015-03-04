/***
 * Framework independent implementation file for linearmosaic...
 *
 *   Implemention of the linearmosaic component
 *    linearmosaic.xml.
 * 
 *
 * @author Kumar Golap
 * @version $Id$
 ***/

#include <iostream>
#include <linearmosaic_cmpt.h>
#include <images/Images/PagedImage.h>
#include <images/Images/TempImage.h>
#include <synthesis/MeasurementEquations/LinearMosaic.h>
#include <casa/Logging/LogIO.h>
#include <casa/Utilities/Assert.h>

#include <casa/BasicSL/String.h>
#include <casa/Containers/Record.h>


using namespace std;
using namespace casa;

namespace casac {

linearmosaic::linearmosaic() 
 
{
  // Default constructor
  itsLog = new casa::LogIO();
  itsMos = new casa::LinearMosaic();
}

linearmosaic::~linearmosaic()
{
  delete itsMos;
  itsMos=NULL;
  delete itsLog;
  itsLog=NULL;
}


bool 
linearmosaic::defineoutputimage(const int nx,
		      const int ny, 
		      const ::casac::variant& cellx,
		      const ::casac::variant& celly,
		      const ::casac::variant& imagecenter,
		      const std::string& outputimage, const std::string& outputweight) {

  Bool rstat(False);
  try {
    if(itsMos) delete itsMos;
    itsMos=NULL;
    casa::MDirection imcen;
    if(!casaMDirection(imagecenter, imcen)){
    	    throw(AipsError("Could not interprete phasecenter parameter"));
    }
    Int nX, nY;
    nX=nx;
    nY=ny;
    if(nY < 1)
    nY=nx;
    casa::Quantity cellX=casaQuantity(cellx);
    casa::Quantity cellY=casaQuantity(celly);
    itsMos=new LinearMosaic(outputimage, outputweight, imcen, nX, nY,
    			  cellX, cellY);
    rstat = True;
  } catch  (AipsError x) {

    *itsLog << LogIO::SEVERE << "Exception Reported: " << x.getMesg() << LogIO::POST;
    RETHROW(x);
  }
  return rstat;
}
//-------------------------------------------------------------------------
bool linearmosaic::setoutputimage(const  string& outputimage, const  string& outputweight,  int  imageweight){
	 Bool rstat(False);
	  try {
		  	  itsMos->setOutImages(outputimage, outputweight, imageweight);

		  	  rstat = True;
		  } catch  (AipsError x) {

		    *itsLog << LogIO::SEVERE << "Exception Reported: " << x.getMesg() << LogIO::POST;
		    RETHROW(x);
		  }
		  return rstat;

}

  // ---------------------------------------------------------------------
  bool linearmosaic::makemosaic(const casac::variant& inimages,  const casac::variant& inweightimages, const int wgttype){

 Bool rstat(True);
  try {

	  casa::Vector<String> images, weightimages;
	  images=toVectorString(toVectorString(inimages, "images"));
	  weightimages=toVectorString(toVectorString(inweightimages, "weightimages"));

	  if(images.nelements() != weightimages.nelements())
		  throw(AipsError("number of images and weightimages not equal"));
	  Vector<CountedPtr<ImageInterface<Float> > > im(1), wgt(1);
	  for (uInt k=0; k < images.nelements(); ++k){


		  wgt[0]=new casa::PagedImage<Float>(weightimages[k]);
		  if(wgttype==1)
			  im[0]=new casa::PagedImage<Float>(images[k]);
		  else if(wgttype==0){
			  PagedImage<Float>tmp(images[k]);
			  im[0]=new casa::TempImage<Float>(tmp.shape(), tmp.coordinates());
			  im[0]->copyData((LatticeExpr<Float>)(tmp*(*wgt[0])));
		  }
		  else if(wgttype==2){
			  PagedImage<Float>tmp(images[k]);
			  im[0]=new casa::TempImage<Float>(tmp.shape(), tmp.coordinates());
			  im[0]->copyData((LatticeExpr<Float>)(iif(*(wgt[0]) > (0.0),
			  						       (tmp/(*wgt[0])), 0)));
		  }
		  else
			  throw(AipsError("image is weighted in an unknown fashion"));
		  rstat=rstat && itsMos->makeMosaic(im, wgt);
	  }
    
  } catch  (AipsError x) {

    *itsLog << LogIO::SEVERE << "Exception Reported: " << x.getMesg() << LogIO::POST;
    RETHROW(x);
  }
  return rstat;

  }

//

//----------------------------------------------------------------------------

} // casac namespace
