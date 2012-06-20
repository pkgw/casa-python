#include <iostream>
#include <memory>
#include <sys/wait.h>
#include <image_cmpt.h>
#include <casa/Arrays/ArrayIO.h>
#include <casa/Arrays/ArrayMath.h>
#include <casa/Arrays/ArrayUtil.h>
#include <casa/Arrays/MaskedArray.h>
#include <casa/BasicMath/Random.h>
#include <casa/BasicSL/String.h>
#include <casa/Containers/Record.h>
#include <casa/Exceptions/Error.h>
#include <casa/fstream.h>
#include <casa/Logging/LogFilter.h>
#include <casa/Logging/LogIO.h>
#include <casa/Logging/LogOrigin.h>
#include <casa/OS/Directory.h>
#include <casa/OS/EnvVar.h>
#include <casa/OS/HostInfo.h>
#include <casa/OS/RegularFile.h>
#include <casa/OS/SymLink.h>
#include <casa/Quanta/QuantumHolder.h>
#include <casa/Utilities/Assert.h>
#include <components/ComponentModels/ComponentList.h>
#include <components/ComponentModels/ComponentShape.h>
#include <components/ComponentModels/GaussianShape.h>
#include <components/ComponentModels/SkyComponent.h>
#include <components/ComponentModels/SkyCompRep.h>
#include <components/ComponentModels/TwoSidedShape.h>
#include <components/SpectralComponents/SpectralElement.h>
#include <coordinates/Coordinates/CoordinateSystem.h>
#include <coordinates/Coordinates/StokesCoordinate.h>
#include <coordinates/Coordinates/CoordinateUtil.h>
#include <coordinates/Coordinates/DirectionCoordinate.h>
#include <coordinates/Coordinates/GaussianConvert.h>
#include <coordinates/Coordinates/LinearCoordinate.h>

#include <images/Images/ComponentImager.h>
#include <images/Images/Image2DConvolver.h>
#include <images/Images/ImageConcat.h>
#include <images/Images/ImageConvolver.h>
#include <images/Images/ImageDecomposer.h>
#include <images/Images/ImageExpr.h>
#include <images/Images/ImageExprParse.h>
#include <images/Images/ImageFFT.h>
#include <images/Images/ImageFITSConverter.h>
#include <images/Images/ImageHistograms.h>
#include <images/Images/ImageInterface.h>
#include <images/Images/ImageMoments.h>
#include <images/Images/ImageRegrid.h>
#include <images/Images/ImageSourceFinder.h>
#include <images/Images/ImageStatistics.h>
#include <images/Images/ImageSummary.h>
#include <images/Images/ImageTwoPtCorr.h>
#include <images/Images/ImageUtilities.h>
#include <images/Images/LELImageCoord.h>
#include <images/Images/PagedImage.h>
#include <images/Images/RebinImage.h>
#include <images/Images/SepImageConvolver.h>
#include <images/Images/SubImage.h>
#include <images/Images/TempImage.h>
#include <images/Images/ImageAnalysis.h>
#include <images/Regions/ImageRegion.h>
#include <images/Regions/WCLELMask.h>
#include <lattices/LatticeMath/Fit2D.h>
#include <lattices/LatticeMath/LatticeFit.h>
#include <lattices/Lattices/LatticeAddNoise.h>
#include <lattices/Lattices/LatticeExprNode.h>
#include <lattices/Lattices/LatticeExprNode.h>
#include <lattices/Lattices/LatticeIterator.h>
#include <lattices/Lattices/LatticeRegion.h>
#include <lattices/Lattices/LatticeSlice1D.h>
#include <lattices/Lattices/LatticeUtilities.h>
#include <lattices/Lattices/LCBox.h>
#include <lattices/Lattices/LCSlicer.h>
#include <lattices/Lattices/MaskedLatticeIterator.h>
#include <lattices/Lattices/PixelCurve1D.h>
#include <lattices/Lattices/RegionType.h>
#include <lattices/Lattices/TiledLineStepper.h>
#include <measures/Measures/Stokes.h>
#include <scimath/Fitting/LinearFitSVD.h>
#include <scimath/Functionals/Polynomial.h>
#include <scimath/Mathematics/VectorKernel.h>
#include <tables/LogTables/NewFile.h>

#include <imageanalysis/ImageAnalysis/ImageCollapser.h>
#include <imageanalysis/ImageAnalysis/ImageFitter.h>
#include <imageanalysis/ImageAnalysis/ImageProfileFitter.h>
#include <imageanalysis/ImageAnalysis/ImagePrimaryBeamCorrector.h>
#include <imageanalysis/ImageAnalysis/ImageStatsCalculator.h>

#include <imageanalysis/ImageAnalysis/ImageTransposer.h>

#include <stdcasa/version.h>

#include <casa/namespace.h>

#include <memory>

using namespace std;

#define _ORIGIN LogOrigin(_class, __FUNCTION__, WHERE)

namespace casac {

const String image::_class = "image";

image::image() :
_log(new LogIO()), _image(new ImageAnalysis()) {
try {
    *_log << _ORIGIN;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

// private ImageInterface constructor for on the fly components
image::image(const casa::ImageInterface<casa::Float>* inImage) :
	_log(new LogIO()), _image(new ImageAnalysis(inImage)) {
	try {
		*_log << _ORIGIN;

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

// private ImageInterface constructor for on the fly components
image::image(casa::ImageInterface<casa::Float>* inImage,
		const bool cloneInputPointer) :
	_log(new LogIO()), _image(new ImageAnalysis(inImage, cloneInputPointer)) {
	try {
		*_log << LogOrigin("image", "image");
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

image::~image() {
}

Bool isunset(const ::casac::variant &theVar) {
	Bool rstat(False);
	if ((theVar.type() == ::casac::variant::BOOLVEC) && (theVar.size() == 0))
		rstat = True;
	return rstat;
}

::casac::record*
image::torecord() {
	::casac::record *rstat = new ::casac::record();
	*_log << LogOrigin("image", "torecord");
	if (detached())
		return rstat;
	try {
		Record rec;
		if (!_image->toRecord(rec)) {
			*_log << "Could not convert to record " << LogIO::EXCEPTION;
		}

		// Put it in a ::casac::record
		delete rstat;
		rstat = 0;
		rstat = fromRecord(rec);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;

}
bool image::fromrecord(const record& imrecord, const string& outfile) {
	try {
		*_log << _ORIGIN;
		auto_ptr<Record> tmpRecord(toRecord(imrecord));
		if (_image.get() == 0) {
			_image.reset(new ImageAnalysis());
		}
		if (
			! _image->fromRecord(*tmpRecord, casa::String(outfile))
		) {
			*_log << "Failed to create a valid image from this record"
					<< LogIO::EXCEPTION;
		}
		return True;
	} catch (AipsError x) {
		RETHROW(x);
	}
}

bool image::addnoise(const std::string& type, const std::vector<double>& pars,
		const ::casac::record& region, const bool zeroIt) {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "addnoise");
		if (detached())
			return rstat;

		Record *pRegion = toRecord(region);

		_image->addnoise(type, pars, *pRegion, zeroIt);
		rstat = true;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

// FIXME need to support region records as input
casac::image * image::collapse(
	const string& function, const variant& axes,
	const string& outfile, const string& region, const string& box,
	const string& chans, const string& stokes, const string& mask,
	const bool overwrite, const bool stretch
) {
	*_log << _ORIGIN;
	if (detached()) {
		return 0;
	}
	try {
		IPosition myAxes;
		if (axes.type() == variant::INT) {
			myAxes = IPosition(1, axes.toInt());
		}
		else if (axes.type() == variant::INTVEC) {
			myAxes = IPosition(axes.getIntVec());
		}
		else if (
			axes.type() == variant::STRINGVEC
			|| axes.type() == variant::STRING
		) {
			Vector<String> axVec = (axes.type() == variant::STRING)
				? Vector<String> (1, axes.getString())
				: toVectorString(axes.toStringVec());
			myAxes = IPosition(
				_image->getImage()->coordinates().getWorldAxesOrder(
					axVec, False
				)
			);
			for (
				IPosition::iterator iter = myAxes.begin();
				iter != myAxes.end(); iter++
			) {
				if (*iter < 0) {
					throw AipsError(
							"At least one specified axis does not exist");
				}
			}
		}
		else {
			*_log << "Unsupported type for parameter axes" << LogIO::EXCEPTION;
		}
		String aggString = function;
		aggString.trim();
		aggString.downcase();
		if (aggString == "avdev") {
			*_log << "avdev currently not supported. Let us know if you have a need for it"
				<< LogIO::EXCEPTION;
		}
		ImageCollapser collapser(
			aggString, _image->getImage(), region, 0, box,
			chans, stokes, mask, myAxes, outfile, overwrite
		);
		collapser.setStretch(stretch);
		return new image(collapser.collapse(True), False);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

image* image::imagecalc(
	const string& outfile, const string& pixels,
	const bool overwrite
) {
	try {
		std::auto_ptr<ImageAnalysis> ia(new ImageAnalysis());
		return new image(ia->imagecalc(outfile, pixels, overwrite));
	}
	catch (AipsError x) {
		RETHROW(x);
	}
}

image* image::imageconcat(
	const string& outfile, const variant& infiles,
	const int axis, const bool relax, const bool tempclose,
	const bool overwrite
) {
	try {
		Vector<String> inFiles;
		if (infiles.type() == ::casac::variant::BOOLVEC) {
			inFiles.resize(0); // unset
		}
		else if (infiles.type() == ::casac::variant::STRING) {
			sepCommaEmptyToVectorStrings(inFiles, infiles.toString());
		}
		else if (infiles.type() == variant::STRINGVEC) {
			inFiles = toVectorString(infiles.toStringVec());
		}
		else {
			*_log << "Unrecognized infiles datatype" << LogIO::EXCEPTION;
		}
		std::auto_ptr<ImageAnalysis> ia(new ImageAnalysis());
		return new image(
			ia->imageconcat(
				outfile, inFiles, axis,	relax, tempclose, overwrite
			)
		);
	}
	catch (AipsError x) {
		RETHROW(x);
	}
}

bool image::fromarray(const std::string& outfile,
		const ::casac::variant& pixels, const ::casac::record& csys,
		const bool linear, const bool overwrite, const bool log) {
	try {
		if (_log.get() == 0) {
			_log.reset(new LogIO());
		}
		_image.reset(new ImageAnalysis());
		*_log << _ORIGIN;

		Vector<Int> shape = pixels.arrayshape();
		uInt ndim = shape.size();
		if (ndim == 0) {
			*_log << "The pixels array is empty" << LogIO::EXCEPTION;
		}
		for (uInt i = 0; i < ndim; i++) {
			if (shape(i) <= 0) {
				*_log << "The shape of the pixels array is invalid"
						<< LogIO::EXCEPTION;
			}
		}

		Array<Float> pixelsArray;
		if (pixels.type() == variant::DOUBLEVEC) {
			std::vector<double> pixelVector = pixels.getDoubleVec();
			Vector<Int> shape = pixels.arrayshape();
			pixelsArray.resize(IPosition(shape));
			Vector<Double> localpix(pixelVector);
			convertArray(pixelsArray, localpix.reform(IPosition(shape)));
		} else if (pixels.type() == ::casac::variant::INTVEC) {
			vector<int> pixelVector = pixels.getIntVec();
			Vector<Int> shape = pixels.arrayshape();
			pixelsArray.resize(IPosition(shape));
			Vector<Int> localpix(pixelVector);
			convertArray(pixelsArray, localpix.reform(IPosition(shape)));
		} else {
			*_log << "pixels is not understood, try using an array "
					<< LogIO::EXCEPTION;
			return False;
		}

		auto_ptr<Record> coordinates(toRecord(csys));
		return _image->imagefromarray(outfile, pixelsArray, *coordinates,
				linear, overwrite, log);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

bool image::fromascii(const string& outfile, const string& infile,
		const vector<int>& shape, const string& sep, const record& csys,
		const bool linear, const bool overwrite) {
	try {
		if (_log.get() == 0) {
			_log.reset(new LogIO());
		}
		*_log << _ORIGIN;

		if (infile == "") {
			*_log << LogIO::SEVERE << "infile must be specified" << LogIO::POST;
			return false;
		}
		if (shape.size() == 1 && shape[0] == -1) {
			*_log << LogIO::SEVERE << "Image shape must be specified"
					<< LogIO::POST;
			return false;
		}

		if (_image.get() == 0) {
			_image.reset(new ImageAnalysis());
		}
		auto_ptr<Record> coordsys(toRecord(csys));
		return _image->imagefromascii(outfile, infile, Vector<Int> (shape),
				sep, *coordsys, linear, overwrite);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

bool image::fromfits(const std::string& outfile, const std::string& fitsfile,
		const int whichrep, const int whichhdu, const bool zeroBlanks,
		const bool overwrite) {
	try {
		if (_log.get() == 0) {
			_log.reset(new LogIO());
		}
		_image.reset(new ImageAnalysis());

		*_log << _ORIGIN;
		return _image->imagefromfits(outfile, fitsfile, whichrep, whichhdu,
				zeroBlanks, overwrite);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

bool image::fromimage(const string& outfile, const string& infile,
		const record& region, const variant& mask, const bool dropdeg,
		const bool overwrite) {
	try {
		if (_log.get() == 0) {
			_log.reset(new LogIO());
		}
		_image.reset(new ImageAnalysis());
		*_log << _ORIGIN;
		String theMask;
		if (mask.type() == variant::BOOLVEC) {
			theMask = "";
		} else if (mask.type() == variant::STRING) {
			theMask = mask.toString();
		} else if (mask.type() == variant::RECORD) {
			*_log << LogIO::SEVERE
					<< "Don't support region masking yet, only valid LEL "
					<< LogIO::POST;
			return False;
		} else {
			*_log << LogIO::SEVERE
					<< "Mask is not understood, try a valid LEL string "
					<< LogIO::POST;
			return False;
		}

		auto_ptr<Record> regionPtr(toRecord(region));
		return _image->imagefromimage(outfile, infile, *regionPtr, theMask,
				dropdeg, overwrite);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

bool image::fromshape(const string& outfile, const vector<int>& shape,
		const record& csys, const bool linear, const bool overwrite,
		const bool log) {
	try {
		if (_log.get() == 0) {
			_log.reset(new LogIO());
		}
		_image.reset(new ImageAnalysis());
		*_log << _ORIGIN;
		auto_ptr<Record> coordinates(toRecord(csys));
		return _image->imagefromshape(outfile, Vector<Int> (shape),
				*coordinates, linear, overwrite, log);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::image *
image::adddegaxes(const std::string& outfile, const bool direction,
		const bool spectral, const std::string& stokes, const bool linear,
		const bool tabular, const bool overwrite) {
	::casac::image *rstat = 0;
	try {
		*_log << _ORIGIN;
		if (detached())
			return rstat;

		PtrHolder<ImageInterface<Float> > outimage;
		_image->adddegaxes(outfile, outimage, direction, spectral, stokes,
				linear, tabular, overwrite);
		rstat = new ::casac::image(outimage.ptr());
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::image *
image::convolve(
	const std::string& outFile, const ::casac::variant& kernel,
	const double in_scale, const ::casac::record& region,
	const ::casac::variant& vmask, const bool overwrite,
	const bool stretch, const bool async
) {
	try {
		*_log << _ORIGIN;
		if (detached()) {
			return 0;
		}

		Array<Float> kernelArray;
		String kernelFileName = "";
		if (kernel.type() == ::casac::variant::DOUBLEVEC) {
			std::vector<double> kernelVector = kernel.toDoubleVec();
			Vector<Int> shape = kernel.arrayshape();
			kernelArray.resize(IPosition(shape));
			Vector<Double> localkern(kernelVector);
			casa::convertArray(kernelArray, localkern.reform(IPosition(shape)));
		}
		else if (kernel.type() == ::casac::variant::INTVEC) {
			std::vector<int> kernelVector = kernel.toIntVec();
			Vector<Int> shape = kernel.arrayshape();
			kernelArray.resize(IPosition(shape));
			Vector<Int> localkern(kernelVector);
			casa::convertArray(kernelArray, localkern.reform(IPosition(shape)));
		}
		else if (kernel.type() == ::casac::variant::STRING || kernel.type()
				== ::casac::variant::STRINGVEC) {

			kernelFileName = kernel.toString();
		}
		else {
			*_log << LogIO::SEVERE
					<< "kernel is not understood, try using an array or an image "
					<< LogIO::POST;
			return 0;
		}

		String theMask;
		Record *theMaskRegion;
		if (vmask.type() == ::casac::variant::BOOLVEC) {
			theMask = "";
		}
		else if (vmask.type() == ::casac::variant::STRING || vmask.type()
				== ::casac::variant::STRINGVEC) {
			theMask = vmask.toString();
		}
		else if (vmask.type() == ::casac::variant::RECORD) {
			::casac::variant localvar(vmask);
			theMaskRegion = toRecord(localvar.asRecord());
			*_log << LogIO::SEVERE
					<< "Don't support region masking yet, only valid LEL "
					<< LogIO::POST;
			return 0;
		}
		else {
			*_log << LogIO::SEVERE
					<< "Mask is not understood, try a valid LEL string "
					<< LogIO::POST;
			return 0;
		}

		Record *Region = toRecord(region);

		std::auto_ptr<ImageInterface<Float> > tmpIm(
			_image->convolve(
				outFile, kernelArray,
				kernelFileName, in_scale, *Region,
				theMask, overwrite, async, stretch
			)
		);
		return new ::casac::image(tmpIm.get());
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::record*
image::boundingbox(const ::casac::record& region) {
	::casac::record *rstat = 0;
	try {
		*_log << _ORIGIN;
		if (detached())
			return rstat;
		Record *Region = toRecord(region);
		rstat = fromRecord(*_image->boundingbox(*Region));
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

std::string image::brightnessunit() {
	std::string rstat;
	try {
		*_log << _ORIGIN;
		if (!detached()) {
			rstat = _image->brightnessunit();
		} else {
			rstat = "";
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::calc(const std::string& expr) {
	try {
		*_log << _ORIGIN;
		if (detached()) {
			return False;
		}
		return _image->calc(expr);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
			<< LogIO::POST;
		RETHROW(x);
	}
}

bool image::calcmask(const std::string& mask, const std::string& maskName,
		const bool makeDefault) {
	bool rstat(false);
	try {
		*_log << _ORIGIN;
		if (detached())
			return rstat;

		//For now not passing the Regions record...when this is done then
		//replace this temporary Record  here... it should be a Record of Records..
		//each element a given region
		Record regions;

		rstat = _image->calcmask(mask, regions, maskName, makeDefault);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::close() {
	try {
		*_log << _ORIGIN;
		if (_image.get() != 0) {
			_image.reset(0);
		} else {
			*_log << LogIO::WARN << "Image is already closed" << LogIO::POST;
		}
		return True;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::image *
image::continuumsub(const std::string& outline, const std::string& outcont,
		const ::casac::record& region, const std::vector<int>& channels,
		const std::string& pol, const int in_fitorder, const bool overwrite) {
	::casac::image *rstat = 0;
	try {
		*_log << _ORIGIN;
		if (detached())
			return rstat;

		Record * leRegion = toRecord(region);
		Vector<Int> theChannels(channels);
		if (theChannels.size() == 1 && theChannels[0] == -1) {
			theChannels.resize(0);
		}
		ImageInterface<Float> * theResid = _image->continuumsub(outline,
				outcont, *leRegion, theChannels, pol, in_fitorder, overwrite);
		if (!theResid) {
			*_log << LogIO::SEVERE << "continuumsub failed " << LogIO::POST;
		} else {
			rstat = new ::casac::image(theResid);
			delete theResid;
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::record *
image::convertflux(const ::casac::variant& qvalue,
		const ::casac::variant& major, const ::casac::variant& minor,
		const std::string& type, const bool toPeak) {
	::casac::record *rstat = 0;

	try {
		*_log << _ORIGIN;
		if (detached())
			return rstat;

		Quantum<Double> value = casaQuantity(qvalue);
		Quantum<Double> majorAxis = casaQuantity(major);
		Quantum<Double> minorAxis = casaQuantity(minor);

		//

		Bool noBeam = False;
		casa::Quantity rtn = _image->convertflux(noBeam, value, majorAxis,
				minorAxis, type, toPeak);
		rstat = recordFromQuantity(rtn);

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

image* image::convolve2d(
	const string& outFile, const vector<int>& axes,
	const string& type, const variant& major, const variant& minor,
	const variant& pa, const double in_scale, const record& region,
	const variant& vmask, const bool overwrite, const bool stretch
) {
	try {
		*_log << _ORIGIN;
		if (detached()) {
			return 0;
		}
		UnitMap::putUser("pix", UnitVal(1.0), "pixel units");
		Record *Region = toRecord(region);
		String mask = vmask.toString();

		if (mask == "[]") {
			mask = "";
		}
		String kernel(type);
		casa::Quantity majorKernel = casaQuantityFromVar(major);
		casa::Quantity minorKernel = casaQuantityFromVar(minor);
		casa::Quantity paKernel = casaQuantityFromVar(pa);
		*_log << _ORIGIN;

		Vector<Int> Axes(axes);
		if (Axes.size() == 0) {
			Axes.resize(2);
			Axes[0] = 0;
			Axes[1] = 1;
		}
		std::auto_ptr<ImageInterface<Float> > tmpIm(
			_image->convolve2d(
				outFile, Axes, type, majorKernel, minorKernel,
				paKernel, in_scale, *Region, mask, overwrite,
				stretch
			)
		);
		return new image(tmpIm.get());
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::coordsys *
image::coordsys(const std::vector<int>& pixelAxes) {
	::casac::coordsys *rstat = 0;
	*_log << _ORIGIN;

	try {
		if (detached())
			return rstat;

		// Return coordsys object
		rstat = new ::casac::coordsys();
		CoordinateSystem csys = _image->coordsys(Vector<Int> (pixelAxes));
		rstat->setcoordsys(csys);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::record*
image::coordmeasures(const std::vector<double>&pixel) {
	::casac::record *rstat = 0;
	try {
		*_log << _ORIGIN;
		if (detached())
			return rstat;

		casa::Record theDir;
		casa::Record theFreq;
		casa::Record theVel;
		casa::Record* retval;
		casa::Quantity theInt;
		Vector<Double> vpixel;
		if (!(pixel.size() == 1 && pixel[0] == -1)) {
			vpixel = pixel;
		}
		retval = _image->coordmeasures(theInt, theDir, theFreq, theVel, vpixel);

		String error;
		Record R;
		if (QuantumHolder(theInt).toRecord(error, R)) {
			retval->defineRecord(RecordFieldId("intensity"), R);
		} else {
			*_log << LogIO::SEVERE << "Could not convert intensity to record. "
					<< error << LogIO::POST;
		}
		rstat = fromRecord(*retval);

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::record*
image::decompose(const ::casac::record& region, const ::casac::variant& vmask,
	const bool simple, const double Threshold, const int nContour,
	const int minRange, const int nAxis, const bool fit,
	const double maxrms, const int maxRetry, const int maxIter,
	const double convCriteria, const bool stretch
) {
	try {
		*_log << _ORIGIN;
		if (detached()) {
			return 0;
		}
		if (Threshold < 0) {
			throw AipsError(
				"Threshold = " + String::toString(Threshold)
				+ ". You must specify a nonnegative threshold"
			);
		}
		Record *Region = toRecord(region);
		String mask = vmask.toString();
		if (mask == "[]") {
			mask = "";
		}
		Matrix<Int> blcs;
		Matrix<Int> trcs;

		Matrix<Float> cl = _image->decompose(
			blcs, trcs, *Region, mask, simple, Threshold,
			nContour, minRange, nAxis, fit, maxrms,
			maxRetry, maxIter, convCriteria, stretch
		);

		casa::Record outrec1;
		outrec1.define("components", cl);
		outrec1.define("blc", blcs);
		outrec1.define("trc", trcs);
		return fromRecord(outrec1);

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
			<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::record *
image::deconvolvecomponentlist(const ::casac::record& complist) {
	::casac::record *rstat = 0;
	try {
		*_log << _ORIGIN;
		if (detached())
			return rstat;

		String error;
		Record *compList = toRecord(complist);
		Record outRec = _image->deconvolvecomponentlist(*compList);
		rstat = fromRecord(outRec);

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::record *
image::deconvolvefrombeam(const ::casac::variant& source,
		const ::casac::variant& beam) {

	::casac::record *rstat = 0;
	try {
		*_log << LogOrigin("image", "decovolvefrombeam");
		casa::Vector<casa::Quantity> sourceParam;
		casa::Vector<casa::Quantity> beamParam;
		if (!toCasaVectorQuantity(source, sourceParam)
				|| (sourceParam.nelements() == 0)) {
			throw(AipsError("Cannot understand source values"));
		} else {
			if (sourceParam.nelements() == 1) {
				sourceParam.resize(3, True);
				sourceParam[1] = sourceParam[0];
				sourceParam[2] = casa::Quantity(0.0, "deg");
			}
			if (sourceParam.nelements() == 2) {
				sourceParam.resize(3, True);
				sourceParam[2] = casa::Quantity(0.0, "deg");
			}

		}
		if (!toCasaVectorQuantity(beam, beamParam) || (beamParam.nelements()
				== 0)) {
			throw(AipsError("Cannot understand beam values"));
		} else {
			if (beamParam.nelements() == 1) {
				beamParam.resize(3, True);
				beamParam[1] = beamParam[0];
				beamParam[2] = casa::Quantity(0.0, "deg");
			}
			if (beamParam.nelements() == 2) {
				beamParam.resize(3, True);
				beamParam[2] = casa::Quantity(0.0, "deg");
			}

		}

		Bool success = False;
		Bool retval = _image->deconvolveFromBeam(sourceParam[0],
				sourceParam[1], sourceParam[2], success, beamParam);

		casa::Record outrec1;
		casa::Record deconval;
		casa::Record tmprec;
		casa::String error;
		QuantumHolder(sourceParam[0]).toRecord(error, tmprec);
		deconval.defineRecord("major", tmprec);
		QuantumHolder(sourceParam[1]).toRecord(error, tmprec);
		deconval.defineRecord("minor", tmprec);
		QuantumHolder(sourceParam[2]).toRecord(error, tmprec);
		deconval.defineRecord("pa", tmprec);
		deconval.define("success", success);
		outrec1.define("return", retval);
		outrec1.defineRecord("fit", deconval);
		rstat = fromRecord(outrec1);

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;

}
bool image::remove(const bool finished, const bool verbose) {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "remove");

		if (detached())
			return rstat;

		if (_image->remove(verbose)) {
			// Now done the image tool if desired.
			if (finished)
				done();
			rstat = true;
		} else {
			rstat = false;
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::removefile(const std::string& filename) {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "removefile");

		String fileName(filename);
		if (fileName.empty()) {
			*_log << LogIO::WARN << "Empty filename" << LogIO::POST;
			return rstat;
		}
		File f(fileName);
		if (!f.exists()) {
			*_log << LogIO::WARN << fileName << " does not exist."
					<< LogIO::POST;
			return rstat;
		}

		// Now try and blow it away.  If it's open, tabledelete won't delete it.
		String message;
		if (Table::canDeleteTable(message, fileName, True)) {
			Table::deleteTable(fileName, True);
			rstat = true;
		} else {
			*_log << LogIO::WARN << "Cannot delete file " << fileName
					<< " because " << message << LogIO::POST;
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::done(const bool remove, const bool verbose) {
	try {
		*_log << _ORIGIN;
		if (remove && !detached()) {
			if (!_image->remove(verbose)) {
				*_log << LogIO::WARN << "Failed to remove image file"
						<< LogIO::POST;
			}
		}
		_image.reset(0);
		return True;

		/*
		 Don't delete _log! bad things happen if you do, because the component is
		 not released from memory...i.e done == close
		 */

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

bool image::fft(
	const string& realOut, const string& imagOut,
	const string& ampOut, const string& phaseOut,
	const std::vector<int>& axes, const ::casac::record& region,
	const ::casac::variant& vmask, const bool stretch
) {
	try {
		*_log << LogOrigin(_class, __FUNCTION__);
		if (detached()) {
			return false;
		}

		Record *Region = toRecord(region);
		String mask = vmask.toString();
		if (mask == "[]") {
			mask = "";
		}

		// if default value change it to empty vector
		Vector<Int> leAxes(axes);
		if (leAxes.size() == 1 && leAxes[0] == -1) {
			leAxes.resize();
		}

		return _image->fft(
			realOut, imagOut, ampOut, phaseOut,
			leAxes, *Region, mask, stretch
		);

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
			<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::record*
image::findsources(const int nMax, const double cutoff,
		const ::casac::record& region, const ::casac::variant& vmask,
		const bool point, const int width, const bool absFind) {
	::casac::record *rstat = 0;
	try {
		*_log << LogOrigin("image", "findsources");
		if (detached())
			return rstat;

		Record *Region = toRecord(region);
		String mask = vmask.toString();
		if (mask == "[]")
			mask = "";

		Record listOut = _image->findsources(nMax, cutoff, *Region, mask,
				point, width, absFind);
		rstat = fromRecord(listOut);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

record* image::fitprofile(const string& box, const variant& region,
	const string& chans, const string& stokes, const int axis,
	const variant& vmask, int ngauss, const int poly,
	const string& estimates, const int minpts, const bool multifit,
	const string& model, const string& residual, const string& amp,
	const string& amperr, const string& center, const string& centererr,
	const string& fwhm, const string& fwhmerr,
	const string& integral, const string& integralerr, const bool stretch,
	const bool logResults, const variant& pampest,
	const variant& pcenterest, const variant& pfwhmest,
	const variant& pfix, const variant& gmncomps,
    const variant& gmampcon, const variant& gmcentercon,
    const variant& gmfwhmcon, const vector<double>& gmampest,
    const vector<double>& gmcenterest, const vector<double>& gmfwhmest,
    const variant& gmfix, const string& logfile, const bool append,
    const variant& pfunc, const vector<double>& goodamprange,
    const vector<double>& goodcenterrange,
    const vector<double>& goodfwhmrange, const variant& sigma,
    const string& outsigma
) {
	*_log << LogOrigin(_class, __FUNCTION__);
	if (detached()) {
		return 0;
	}
	String regionName;
	std::auto_ptr<Record> regionPtr(0);
	_getRegion(regionName, regionPtr, region);
	if (ngauss < 0) {
		*_log << LogIO::WARN
			<< "ngauss < 0 is meaningless. Setting ngauss = 0 "
			<< LogIO::POST;
		ngauss = 0;
	}
	try {
		vector<double> myampest = toVectorDouble(pampest, "pampest");
		vector<double> mycenterest = toVectorDouble(pcenterest, "pcenterest");
		vector<double> myfwhmest = toVectorDouble(pfwhmest, "pfwhmest");
		vector<string> myfix = toVectorString(pfix, "pfix");
		vector<string> myfunc = toVectorString(pfunc, "pfunc");

		vector<int> mygmncomps = gmncomps.type() == variant::INT
			&& gmncomps.toInt() == 0
				? vector<int>(0)
				: toVectorInt(gmncomps, "gmncomps");
		vector<double> mygmampcon = toVectorDouble(gmampcon, "gmampcon");
		vector<double> mygmcentercon = toVectorDouble(gmcentercon, "gmcentercon");
		vector<double> mygmfwhmcon = toVectorDouble(gmfwhmcon, "gmfwhmcon");
		vector<string> mygmfix = toVectorString(gmfix, "gmfix");

		vector<double> mygoodamps = toVectorDouble(goodamprange, "goodamprange");
		if (mygoodamps.size() > 2) {
			*_log << "Too many elements in goodamprange" << LogIO::EXCEPTION;
		}
		vector<double> mygoodcenters = toVectorDouble(goodcenterrange, "goodcenterrange");
		if (mygoodcenters.size() > 2) {
			*_log << "Too many elements in goodcenterrange" << LogIO::EXCEPTION;
		}
		vector<double> mygoodfwhms = toVectorDouble(goodfwhmrange, "goodcenterrange");
		if (mygoodfwhms.size() > 2) {
			*_log << "Too many elements in goodfwhmrange" << LogIO::EXCEPTION;
		}
		Bool makeSpectralList = (
			mygmncomps.size() > 0
			|| ! (
				myampest.size() == 0
				&& mycenterest.size() == 0
				&& myfwhmest.size() == 0
			)
		);
		SpectralList spectralList;
		Bool gfixSpecified = (myfix.size() > 0);
		if (makeSpectralList) {
			if (! estimates.empty()) {
				*_log << "You cannot specify both an "
					<< "estimates file and set estimates "
					<< "directly. You may only do one or "
					<< "the either (or neither in which "
					<< "case you must specify ngauss and/or poly)"
					<< LogIO::EXCEPTION;
			}
			uInt mynpcf = myampest.size();
			if (myfunc.size() == 0) {
				myfunc.resize(myampest.size(), "G");
			}
			if (
				mycenterest.size() != mynpcf
				|| myfwhmest.size() != mynpcf
				|| myfunc.size() != mynpcf
			) {
				*_log << "pampest, pcenterest, pfwhmest, and pfunc arrays "
					<< "must all be the same length" << LogIO::EXCEPTION;
			}
			if (gfixSpecified && myfix.size() != mynpcf) {
				*_log << "If the gfix array is specified the number of "
					<< "elements it has must be the same as the number of elements "
					<< "in the ampest array even if some elements are empty strings"
					<< LogIO::EXCEPTION;
			}
			if (mygmncomps.size() > 0) {
				uInt sum = 0;
				for (uInt i=0; i<mygmncomps.size(); i++) {
					if (mygmncomps <= 0) {
						*_log << "All elements of gmncomps must be greater than 0" << LogIO::EXCEPTION;
					}
					sum += mygmncomps[i];
				}
				if (gmampest.size() != sum) {
					*_log << "gmampest must have exactly "
						<< sum << " elements" << LogIO::EXCEPTION;
				}
				if (gmcenterest.size() != sum) {
					*_log << "gmcenterest must have exactly "
						<< sum << " elements" << LogIO::EXCEPTION;
				}
				if (gmfwhmest.size() != sum) {
					*_log << "gmfwhmest must have exactly "
						<< sum << " elements" << LogIO::EXCEPTION;
				}
				if (mygmfix.size() > 0 && mygmfix.size() != sum) {
					*_log << "gmfwhmest must have either zero or " << sum
						<< " elements, even if some are empty strings."
						<< LogIO::EXCEPTION;
				}
				uInt nConstraints = sum - mygmncomps.size();
				if (mygmampcon.size() == 0) {
					mygmampcon = vector<double>(nConstraints, 0);
				}
				else if (
					mygmampcon.size() > 0
					&& mygmampcon.size() != nConstraints
				) {
					*_log << "If specified, gmampcon must have exactly "
						<< nConstraints << " elements, even if some are zero"
						<< LogIO::EXCEPTION;
				}
				if (mygmcentercon.size() == 0) {
					mygmcentercon = vector<double>(nConstraints, 0);
				}
				else if (
					mygmcentercon.size() > 0
					&& mygmcentercon.size() != nConstraints
				) {
					*_log << "If specified, gmcentercon must have exactly "
						<< nConstraints << " elements, even if some are zero"
						<< LogIO::EXCEPTION;
				}
				if (mygmfwhmcon.size() == 0) {
					mygmfwhmcon = vector<double>(nConstraints, 0);
				}
				else if (
					mygmfwhmcon.size() > 0
					&& mygmfwhmcon.size() != nConstraints
				) {
					*_log << "If specified, gmfwhmcon must have exactly "
						<< nConstraints << " elements, even if some are zero"
						<< LogIO::EXCEPTION;
				}
			}
			for (uInt i=0; i<mynpcf; i++) {
				String func(myfunc[i]);
				func.upcase();
				Bool doGauss = func.startsWith("G");
				Bool doLorentz = func.startsWith("L");
				if (! doGauss && ! doLorentz) {
					*_log << myfunc[i] << " does not minimally match 'gaussian' or 'lorentzian'"
						<< LogIO::EXCEPTION;
				}
				std::auto_ptr<PCFSpectralElement> pcf(
					doGauss
					? dynamic_cast<PCFSpectralElement*>(
						new GaussianSpectralElement(
						myampest[i], mycenterest[i],
						GaussianSpectralElement::sigmaFromFWHM(myfwhmest[i])
						)
					)
					: doLorentz
					  ? dynamic_cast<PCFSpectralElement*>(
							  new LorentzianSpectralElement(
								myampest[i], mycenterest[i], myfwhmest[i]
						)
					  )
					  : 0
				);
				if (gfixSpecified) {
					pcf->fixByString(myfix[i]);
				}
				if (! spectralList.add(*pcf)) {
					*_log << "Unable to add element to spectral list"
						<< LogIO::EXCEPTION;
				}
			}
			uInt compNumber = 0;
			for (uInt i=0; i<mygmncomps.size(); i++) {
				if (mygmncomps[i] < 0) {
					*_log << "All elements of gmncomps must be positive"
						<< LogIO::EXCEPTION;
				}
				Vector<GaussianSpectralElement> g(mygmncomps[i]);
				Matrix<Double> constraints(mygmncomps[i] - 1, 3);
				for (uInt j=0; j<(uInt)mygmncomps[i]; j++) {
					g[j] = GaussianSpectralElement(
						gmampest[compNumber], gmcenterest[compNumber],
						GaussianSpectralElement::sigmaFromFWHM(gmfwhmest[compNumber])
					);
					if (mygmfix.size() > 0) {
						g[j].fixByString(mygmfix[compNumber]);
					}
					if (j > 0) {
						constraints(j-1, 0) = mygmampcon[compNumber - (i+1)];
						constraints(j-1, 1) = mygmcentercon[compNumber - (i+1)];
						constraints(j-1, 2) = mygmfwhmcon[compNumber - (i+1)];
					}
					compNumber++;
				}
				if (
					! spectralList.add(
						GaussianMultipletSpectralElement(g, constraints)
					)
				) {
					*_log << "Unable to add gaussian multiplet to spectral list"
						<< LogIO::EXCEPTION;
				}
			}
		}
		else if (gfixSpecified) {
			*_log << "The fix array is specified but no corresponding estimates are "
				<< "set via ampest, centerest, and fwhmest. The fix array will be ignored."
				<< LogIO::WARN;
		}
		String mask = vmask.toString();
		if (mask == "[]") {
			mask = "";
		}
		std::auto_ptr<Array<Float> > sigmaArray(0);
		std::auto_ptr<PagedImage<Float> > sigmaImage(0);
		if (sigma.type() == variant::STRING) {
			String sigmaName = sigma.toString();
			if (! sigmaName.empty()) {
				sigmaImage.reset(new PagedImage<Float>(sigmaName));
			}
		}
		else if (
			sigma.type() == variant::DOUBLEVEC
			|| sigma.type() == variant::INTVEC
		) {
			sigmaArray.reset(new Array<Float>());
			vector<double> sigmaVector = sigma.getDoubleVec();
			Vector<Int> shape = sigma.arrayshape();
			sigmaArray->resize(IPosition(shape));
			convertArray(
				*sigmaArray,
				Vector<Double>(sigmaVector).reform(IPosition(shape))
			);
		}
		else if (sigma.type() == variant::BOOLVEC) {
			// nothing to do
		}
		else {
			*_log << LogIO::SEVERE
				<< "Unrecognized type for sigma. Use either a string (image name) or a numpy array"
				<< LogIO::POST;
			return 0;
		}
		ImageProfileFitter fitter(
			_image->getImage(), regionName, regionPtr.get(),
			box, chans, stokes, mask, axis,
			ngauss, estimates, spectralList
		);
		fitter.setDoMultiFit(multifit);
		fitter.setPolyOrder(poly);
		fitter.setModel(model);
		fitter.setResidual(residual);
		fitter.setAmpName(amp);
		fitter.setAmpErrName(amperr);
		fitter.setCenterName(center);
		fitter.setCenterErrName(centererr);
		fitter.setFWHMName(fwhm);
		fitter.setFWHMErrName(fwhmerr);
		fitter.setIntegralName(integral);
		fitter.setIntegralErrName(integralerr);
		fitter.setMinGoodPoints(minpts > 0 ? minpts : 0);
		fitter.setStretch(stretch);
		fitter.setLogResults(logResults);
		if (! logfile.empty()) {
			fitter.setLogfile(logfile);
			fitter.setLogfileAppend(append);
		}
		if (mygoodamps.size() == 2) {
			fitter.setGoodAmpRange(mygoodamps[0], mygoodamps[1]);
		}
		if (mygoodcenters.size() == 2) {
			fitter.setGoodCenterRange(mygoodcenters[0], mygoodcenters[1]);
		}
		if (mygoodfwhms.size() == 2) {
			fitter.setGoodFWHMRange(mygoodfwhms[0], mygoodfwhms[1]);
		}
		if (sigmaImage.get()) {
			fitter.setSigma(sigmaImage.get());
		}
		else if (sigmaArray.get()) {
			fitter.setSigma(*sigmaArray);
		}
		if (! outsigma.empty()) {
			if (sigmaImage.get() || sigmaArray.get()) {
				fitter.setOutputSigmaImage(outsigma);
			}
			else {
				*_log << LogIO::WARN
					<< "outsigma specified but no sigma image "
					<< "or array specified. outsigma will be ignored"
					<< LogIO::POST;
			}
		}
		return fromRecord(fitter.fit());
	}
	catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
			<< LogIO::POST;
		RETHROW(x);
	}
}

image* image::reorder(
	const std::string& outfile,
	const variant& order
) {
	*_log << LogOrigin(_class, __FUNCTION__);
	*_log << LogIO::WARN << "DEPRECATION WARNING: ia.reorder() has been deprecated and will be "
		<< "removed in an upcoming version. Please use ia.transpose() instead." << LogIO::POST;
	return transpose(outfile, order);
}

image* image::transpose(
	const std::string& outfile,
	const variant& order
) {
	try {
		*_log << LogOrigin("image", __FUNCTION__);
		if (detached()) {
			return 0;
		}
		std::auto_ptr<ImageTransposer> transposer(0);
		switch(order.type()) {
		case variant::INT:
			transposer.reset(
				new ImageTransposer(
					_image->getImage(),
					order.toInt(), outfile
				)
			);
			break;
		case variant::STRING:
			transposer.reset(
				new ImageTransposer(
					_image->getImage(),
					order.toString(), outfile
				)
			);
			break;
		case variant::STRINGVEC:
			{
				Vector<String> orderVec = toVectorString(order.toStringVec());
				transposer.reset(
					new ImageTransposer(
						_image->getImage(), orderVec,
						outfile
					)
				);
			}
			break;
		default:
			*_log << "Unsupported type for order parameter " << order.type()
					<< ". Supported types are a non-negative integer, a single "
					<< "string containing all digits or a list of strings which "
					<< "unambiguously match the image axis names."
					<< LogIO::EXCEPTION;
		}
		return new image(
			transposer->transpose(), False
		);
	} catch (AipsError x) {
		RETHROW(x);
	}
}

::casac::record* image::fitcomponents(
		const string& box, const variant& region, const variant& chans,
		const string& stokes, const variant& vmask,
		const vector<double>& in_includepix,
		const vector<double>& in_excludepix, const string& residual,
		const string& model, const string& estimates,
		const string& logfile, const bool append,
		const string& newestimates, const string& complist,
		const bool overwrite, const bool dooff, const double offset,
		const bool offsetisfixed, const bool stretch
) {
	if (detached()) {
		return 0;
	}
	int num = in_includepix.size();
	Vector<Float> includepix(num);
	num = in_excludepix.size();
	Vector<Float> excludepix(num);
	convertArray(includepix, Vector<Double> (in_includepix));
	convertArray(excludepix, Vector<Double> (in_excludepix));
	if (includepix.size() == 1 && includepix[0] == -1) {
		includepix.resize();
	}
	if (excludepix.size() == 1 && excludepix[0] == -1) {
		excludepix.resize();
	}
	*_log << LogOrigin(_class, __FUNCTION__);
	String mask = vmask.toString();
	if (mask == "[]") {
		mask = "";
	}
	try {
		std::auto_ptr<ImageFitter> fitter;
		const ImageInterface<Float> *image = _image->getImage();
		ImageFitter::CompListWriteControl writeControl =
			complist.empty()
			? ImageFitter::NO_WRITE
			: overwrite
				? ImageFitter::OVERWRITE
				: ImageFitter::WRITE_NO_REPLACE;
		String sChans;
		if (chans.type() == variant::BOOLVEC) {
			// for some reason which eludes me, the default variant type is boolvec
			sChans = "";
		}
		else if (chans.type() == variant::STRING) {
			sChans = chans.toString();
		}
		else if (chans.type() == variant::INT) {
			sChans = String::toString(chans.toInt());
		}
		else {
			*_log
				<< "Unsupported type for chans. chans must be either an integer or a string"
				<< LogIO::EXCEPTION;
		}
		std::auto_ptr<Record> regionRecord(0);
		String regionString;
		_getRegion(regionString, regionRecord, region);
		fitter.reset(
			new ImageFitter(
				image, regionString, regionRecord.get(), box, sChans,
				stokes, mask, includepix, excludepix, residual, model,
				estimates, newestimates, complist, writeControl
			)
		);
		fitter->setStretch(stretch);
		if (! logfile.empty()) {
			fitter->setLogfile(logfile);
			fitter->setLogfileAppend(append);
		}
		if (dooff) {
			fitter->setZeroLevelEstimate(offset, offsetisfixed);
		}
		ComponentList compList = fitter->fit();
		Vector<casa::Quantity> flux;
		Vector<Bool> converged = fitter->converged();
		Record returnRecord, compListRecord;
		String error;

		Vector<String> allowFluxUnits(1, "Jy.km/s");
		FluxRep<Double>::setAllowedUnits(allowFluxUnits);

		if (!compList.toRecord(error, compListRecord)) {
			*_log << "Failed to generate output record from result. " << error
				<< LogIO::EXCEPTION;
		}
		FluxRep<Double>::clearAllowedUnits();
		returnRecord.defineRecord("results", compListRecord);
		returnRecord.define("converged", converged);
		if (dooff) {
			vector<Double> zeroSol, zeroErr;
			fitter->getZeroLevelSolution(zeroSol, zeroErr);
			returnRecord.define("zerooff", Vector<Double>(zeroSol));
			returnRecord.define("zeroofferr", Vector<Double>(zeroErr));
		}
		return fromRecord(returnRecord);
	}
	catch (AipsError x) {
		FluxRep<Double>::clearAllowedUnits();
		*_log << "Exception Reported: " << x.getMesg()
			<< LogIO::EXCEPTION;
		RETHROW(x);
	}
}

::casac::variant*
image::getchunk(const std::vector<int>& blc, const std::vector<int>& trc,
		const std::vector<int>& inc, const std::vector<int>& axes,
		const bool list, const bool dropdeg, const bool getmask) {

	// Recover some pixels from the image from a simple strided box
	::casac::variant *rstat = 0;
	try {
		*_log << LogOrigin("image", "getchunk");
		if (detached())
			return rstat;

		//
		Array<Float> pixels;
		Array<Bool> pixelMask;
		Vector<Int> iaxes(axes);
		// if default value change it to empty vector
		if (iaxes.size() == 1) {
			if (iaxes[0] < 0)
				iaxes.resize();
		}
		_image->getchunk(pixels, pixelMask, Vector<Int> (blc),
				Vector<Int> (trc), Vector<Int> (inc), iaxes, list, dropdeg,
				getmask);

		if (getmask) {
			std::vector<bool> s_pixelmask;
			std::vector<int> s_shape;
			pixelMask.tovector(s_pixelmask);
			pixels.shape().asVector().tovector(s_shape);
			rstat = new ::casac::variant(s_pixelmask, s_shape);
		} else {
			std::vector<int> s_shape;
			pixels.shape().asVector().tovector(s_shape);
			std::vector<double> d_pixels(pixels.nelements());
			int i(0);
			for (Array<Float>::iterator iter = pixels.begin(); iter
					!= pixels.end(); iter++)
				d_pixels[i++] = *iter;
			rstat = new ::casac::variant(d_pixels, s_shape);
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

image* image::pbcor(
	const variant& pbimage, const string& outfile,
	const bool overwrite, const string& box,
	const variant& region, const string& chans,
	const string& stokes, const string& mask,
	const string& mode, const float cutoff,
	const bool stretch
) {
	if (detached()) {
		return 0;
	}
	try {
		*_log << _ORIGIN;
		Array<Float> pbPixels;
		ImageInterface<Float> *pb = 0;
		if (pbimage.type() == variant::DOUBLEVEC) {
			Vector<Int> shape = pbimage.arrayshape();
			pbPixels.resize(IPosition(shape));
			Vector<Double> localpix(pbimage.getDoubleVec());
			casa::convertArray(pbPixels, localpix.reform(IPosition(shape)));
		}
		else if (pbimage.type() == variant::STRING) {
			ImageUtilities::openImage(pb, pbimage.getString(), *_log);
			if (pb == 0) {
				*_log << "Unable to open primary beam image " << pbimage.getString()
					<< LogIO::EXCEPTION;
			}
		}
		else {
			*_log << "Unsupported type " << pbimage.typeString()
				<< " for pbimage" << LogIO::EXCEPTION;
		}
		auto_ptr<ImageInterface<Float> > pbManager(pb);
		String regionString = "";
		auto_ptr<Record> regionRecord(0);
		if (region.type() == variant::STRING || region.size() == 0) {
			regionString = (region.size() == 0) ? "" : region.toString();
		}
		else if (region.type() == variant::RECORD) {
			regionRecord.reset(toRecord(region.clone()->asRecord()));
		}
		else {
			*_log << "Unsupported type for region " << region.type()
				<< LogIO::EXCEPTION;
		}
		String modecopy = mode;
		modecopy.downcase();
		modecopy.trim();
		if (! modecopy.startsWith("d") && ! modecopy.startsWith("m")) {
			throw AipsError("Unknown mode " + mode);
		}
		ImagePrimaryBeamCorrector::Mode myMode = modecopy.startsWith("d")
			? ImagePrimaryBeamCorrector::DIVIDE
			: ImagePrimaryBeamCorrector::MULTIPLY;
		Bool useCutoff = cutoff >= 0.0;
		std::auto_ptr<ImagePrimaryBeamCorrector> pbcor(
			(pb == 0)
			? new ImagePrimaryBeamCorrector(
				_image->getImage(), pbPixels, regionRecord.get(),
				regionString, box, chans, stokes, mask, outfile, overwrite,
				cutoff, useCutoff, myMode
			)
			: new ImagePrimaryBeamCorrector(
				_image->getImage(), pb, regionRecord.get(),
				regionString, box, chans, stokes, mask, outfile, overwrite,
				cutoff, useCutoff, myMode
			)
		);
		pbcor->setStretch(stretch);
		auto_ptr<ImageInterface<Float> > corrected(pbcor->correct(True));
		return new image(corrected.get());
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
			<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::variant* image::getregion(
	const ::casac::record& region, const std::vector<int>& axes,
	const ::casac::variant& mask, const bool list, const bool dropdeg,
	const bool getmask, const bool stretch
) {
	// Recover some pixels and their mask from a region in the image
	try {
		*_log << LogOrigin(_class, __FUNCTION__);
		if (detached())
			return false;

		Array<Float> pixels;
		Array<Bool> pixelmask;

		Record *Region = toRecord(region);
		String Mask;
		if (mask.type() == ::casac::variant::BOOLVEC) {
			Mask = "";
		}
		else if (
			mask.type() == ::casac::variant::STRING
			|| mask.type() == ::casac::variant::STRINGVEC
		) {
			Mask = mask.toString();
		}
		else {
			*_log << LogIO::WARN
				<< "Only LEL string handled for mask...region is yet to come"
				<< LogIO::POST;
			Mask = "";
		}
		Vector<Int> iaxes(axes);
		// if default value change it to empty vector
		if (iaxes.size() == 1 && iaxes[0] < 0) {
			iaxes.resize();
		}
		_image->getregion(
			pixels, pixelmask, *Region, iaxes,
			Mask, list, dropdeg, getmask, stretch
		);
		if (getmask) {
			std::vector<bool> s_pixelmask;
			std::vector<int> s_shape;
			pixelmask.tovector(s_pixelmask);
			pixels.shape().asVector().tovector(s_shape);
			return new ::casac::variant(s_pixelmask, s_shape);
		}
		else {
			std::vector<int> s_shape;
			pixels.shape().asVector().tovector(s_shape);
			std::vector<double> d_pixels(pixels.nelements());
			int i(0);
			for (
				Array<Float>::iterator iter = pixels.begin();
				iter != pixels.end(); iter++
			) {
				d_pixels[i++] = *iter;
			}
			return new ::casac::variant(d_pixels, s_shape);
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::record*
image::getslice(const std::vector<double>& x, const std::vector<double>& y,
		const std::vector<int>& axes, const std::vector<int>& coord,
		const int npts, const std::string& method) {
	::casac::record *rstat = 0;
	try {
		*_log << LogOrigin("image", "getslice");
		if (detached())
			return rstat;

		// handle default coord
		std::vector<int> ncoord(coord);
		if (ncoord.size() == 1 && ncoord[0] == -1) {
			int n = (_image->getImage()->shape()).size();
			ncoord.resize(n);
			for (int i = 0; i < n; i++) {
				//ncoord[i]=i;
				ncoord[i] = 0;
			}
		}

		Record *outRec = _image->getslice(Vector<Double> (x),
				Vector<Double> (y), Vector<Int> (axes), Vector<Int> (ncoord),
				npts, method);
		rstat = fromRecord(*outRec);
		delete outRec;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::image* image::hanning(
	const string& outFile, const ::casac::record& region,
	const ::casac::variant& vmask, const int axis, const bool drop,
	const bool overwrite, const bool /* async */, const bool stretch
) {
	*_log << LogOrigin(_class, __FUNCTION__);
	if (detached()) {
		return 0;
	}
	try {
		Record *Region = toRecord(region);
		String mask = vmask.toString();
		if (mask == "[]") {
			mask = "";
		}

		std::auto_ptr<ImageInterface<Float> > pImOut(
			_image->hanning(
				outFile, *Region, mask, axis, drop,
				overwrite, stretch
			)
		);
		// Return handle to new file
		return new image(pImOut.get());
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
			<< LogIO::POST;
		RETHROW(x);
	}
}

std::vector<bool> image::haslock() {
	std::vector<bool> rstat;
	try {
		*_log << LogOrigin("image", "haslock");
		if (detached())
			return rstat;

		_image->haslock().tovector(rstat);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

record* image::histograms(
	const vector<int>& axes,
	const record& region, const variant& mask,
	const int nbins, const vector<double>& includepix,
	const bool gauss, const bool cumu, const bool log, const bool list,
	const string& plotter, const int nx, const int ny,
	const vector<int>& size, const bool force, const bool disk,
	const bool /* async */, bool stretch
) {
	*_log << LogOrigin(_class, __FUNCTION__);
	if (detached()) {
		return 0;
	}
	try {
		std::auto_ptr<Record> regionRec(toRecord(region));
		String Mask;
		if (mask.type() == ::casac::variant::BOOLVEC) {
			Mask = "";
		}
		else if (
			mask.type() == ::casac::variant::STRING
			|| mask.type() == ::casac::variant::STRINGVEC
		) {
			Mask = mask.toString();
		}
		else {
			*_log << LogIO::WARN
					<< "Only LEL string handled for mask...region is yet to come"
					<< LogIO::POST;
			Mask = "";
		}
		Record retval;
		Vector<Int> naxes;
		if (!(axes.size() == 1 && axes[0] == -1)) {
			naxes.resize(axes.size());
			naxes = Vector<Int> (axes);
		}
		Vector<Double> includePix;
		if (!(includepix.size() == 1 && includepix[0] == -1)) {
			includePix.resize(includepix.size());
			includePix = Vector<Double> (includepix);
		}
        _image->histograms(
			retval, naxes, *regionRec, Mask, nbins, includePix,
			gauss, cumu, log, list, plotter, nx, ny,
			Vector<Int> (size), force, disk, stretch
		);
		return fromRecord(retval);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

std::vector<std::string> image::history(const bool list, const bool browse) {
	std::vector<string> rstat;
	try {
		*_log << LogOrigin("image", "history");
		if (detached())
			return rstat;

		rstat = fromVectorString(_image->history(list, browse));
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::image *
image::insert(const std::string& infile, const ::casac::record& region,
		const std::vector<double>& locate) {
	::casac::image *rstat = 0;
	try {
		*_log << LogOrigin("image", "insert");
		if (detached())
			return rstat;

		Vector<Double> locatePixel(locate);
		if (locatePixel.size() == 1) {
			if (locatePixel[0] < 0)
				locatePixel.resize(0);
		}
		Record *Region = toRecord(region);
		rstat
				= new ::casac::image(_image->insert(infile, *Region,
						locatePixel));
		delete Region;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::isopen() {
	try {
		*_log << _ORIGIN;

		if (_image.get() != 0 && !_image->detached()) {
			return True;
		} else {
			return False;
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

bool image::ispersistent() {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "ispersistent");
		if (detached())
			return rstat;

		rstat = _image->ispersistent();
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::lock(const bool writelock, const int nattempts) {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "lock");
		if (detached())
			return rstat;
		rstat = _image->lock(writelock, nattempts);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::makecomplex(const std::string& outFile,
		const std::string& imagFile, const ::casac::record& region,
		const bool overwrite) {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "makecomplex");
		if (detached())
			return rstat;

		Record *Region = toRecord(region);

		rstat = _image->makecomplex(outFile, imagFile, *Region, overwrite);
		delete Region;

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

std::vector<std::string> image::maskhandler(const std::string& op,
		const std::vector<std::string>& name) {
	std::vector<string> rstat;
	try {
		*_log << LogOrigin("image", "maskhandler");
		if (detached())
			return rstat;

		Vector<String> namesOut;
		Vector<String> namesIn = toVectorString(name);
		namesOut = _image->maskhandler(op, namesIn);
		if (namesOut.size() == 0) {
			namesOut.resize(1);
			namesOut[0] = "T";
		}
		rstat = fromVectorString(namesOut);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::record*
image::miscinfo() {
	::casac::record *rstat = 0;
	try {
		*_log << LogOrigin("image", "miscinfo");
		if (detached())
			return rstat;

		rstat = fromRecord(_image->miscinfo());
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::modify(
	const ::casac::record& model, const ::casac::record& region,
	const ::casac::variant& vmask, const bool subtract, const bool list,
	const bool /* async */, bool stretch
) {
	*_log << LogOrigin(_class, __FUNCTION__);
	if (detached()) {
		return false;
	}
	try {
		String error;
		std::auto_ptr<Record> Model(toRecord(model));
		std::auto_ptr<Record> Region(toRecord(region));
		String mask = vmask.toString();
		if (mask == "[]") {
			mask = "";
		}
		return _image->modify(
			*Model, *Region, mask, subtract,
			list, stretch
		);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::record*
image::maxfit(const ::casac::record& region, const bool doPoint,
		const int width, const bool absFind, const bool list) {
	::casac::record *rstat = 0;
	try {
		*_log << LogOrigin("image", "maxfit");
		if (detached())
			return rstat;

		Record *Region = toRecord(region);
		rstat = fromRecord(_image->maxfit(*Region, doPoint, width, absFind,
				list));

		delete Region;

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::image *
image::moments(
		const std::vector<int>& moments, const int axis,
		const ::casac::record& region, const ::casac::variant& vmask,
		const std::vector<std::string>& in_method,
		const std::vector<int>& smoothaxes,
		const ::casac::variant& smoothtypes,
		const std::vector<double>& smoothwidths,
		const std::vector<double>& d_includepix,
		const std::vector<double>& d_excludepix, const double peaksnr,
		const double stddev, const std::string& velocityType,
		const std::string& out, const std::string& smoothout,
		const std::string& pgdevice, const int nx, const int ny,
		const bool yind, const bool overwrite, const bool removeAxis,
		const bool stretch, const bool /* async */
) {
	try {
		*_log << LogOrigin("image", __FUNCTION__);
		if (detached()) {
			return 0;
		}

		UnitMap::putUser("pix", UnitVal(1.0), "pixel units");
		Vector<Int> whichmoments(moments);
		std::auto_ptr<Record> Region(toRecord(region));
		String mask = vmask.toString();
		if (mask == "[]") {
			mask = "";
		}
		Vector<String> method = toVectorString(in_method);

		Vector<String> kernels;
		if (smoothtypes.type() == ::casac::variant::BOOLVEC) {
			kernels.resize(0); // unset
		}
		else if (smoothtypes.type() == ::casac::variant::STRING) {
			sepCommaEmptyToVectorStrings(kernels, smoothtypes.toString());
		}
		else if (smoothtypes.type() == ::casac::variant::STRINGVEC) {
			kernels = toVectorString(smoothtypes.toStringVec());
		}
		else {
			*_log << LogIO::WARN << "Unrecognized smoothtypes datatype"
				<< LogIO::POST;
		}
		int num = kernels.size();

		Vector<Quantum<Double> > kernelwidths(num);
		Unit u("pix");
		for (int i = 0; i < num; i++) {
			kernelwidths[i] = casa::Quantity(smoothwidths[i], u);
		}
		Vector<Float> includepix;
		num = d_includepix.size();
		if (!(num == 1 && d_includepix[0] == -1)) {
			includepix.resize(num);
			for (int i = 0; i < num; i++)
				includepix[i] = d_includepix[i];
		}
		Vector<Float> excludepix;
		num = d_excludepix.size();
		if (!(num == 1 && d_excludepix[0] == -1)) {
			excludepix.resize(num);
			for (int i = 0; i < num; i++)
				excludepix[i] = d_excludepix[i];
		}

		std::auto_ptr<ImageInterface<Float> > outIm(
			_image->moments(
				whichmoments, axis,
				*Region, mask, method, Vector<Int> (smoothaxes), kernels,
				kernelwidths, includepix, excludepix, peaksnr, stddev,
				velocityType, out, smoothout, pgdevice, nx, ny, yind,
				overwrite, removeAxis, stretch
			)
		);

		return new ::casac::image(outIm.get());
	}
	catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

std::string image::name(const bool strippath) {
	std::string rstat;
	try {
		*_log << LogOrigin("image", "name");
		if (detached()) {
			rstat = "none";
		} else {
			rstat = _image->name(strippath);
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::open(const std::string& infile) {
	try {
		if (_log.get() == 0) {
			_log.reset(new LogIO());
		}
		_image.reset(new ImageAnalysis());

		*_log << _ORIGIN;
		return _image->open(infile);

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

bool image::open(const casa::ImageInterface<casa::Float>* inImage) {
	try {
		if (_log.get() == 0) {
			_log.reset(new LogIO());
		}
		*_log << _ORIGIN;
		_image.reset(new ImageAnalysis(inImage));
		return True;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::record*
image::pixelvalue(const std::vector<int>& pixel) {
	::casac::record *rstat = 0;
	try {
		*_log << LogOrigin("image", "pixelvalue");
		if (detached())
			return rstat;

		Record *outRec = _image->pixelvalue(Vector<Int> (pixel));
		rstat = fromRecord(*outRec);
		delete outRec;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::putchunk(const ::casac::variant& pixels,
		const std::vector<int>& blc, const std::vector<int>& inc,
		const bool list, const bool locking, const bool replicate) {
	bool rstat(false);
	try {
		*_log << _ORIGIN;
		if (detached())
			return rstat;

		Array<Float> pixelsArray;

		if (pixels.type() == ::casac::variant::DOUBLEVEC) {
			std::vector<double> pixelVector = pixels.getDoubleVec();
			Vector<Int> shape = pixels.arrayshape();
			pixelsArray.resize(IPosition(shape));
			Vector<Double> localpix(pixelVector);
			casa::convertArray(pixelsArray, localpix.reform(IPosition(shape)));
		} else if (pixels.type() == ::casac::variant::INTVEC) {
			std::vector<int> pixelVector = pixels.getIntVec();
			Vector<Int> shape = pixels.arrayshape();
			pixelsArray.resize(IPosition(shape));
			Vector<Int> localpix(pixelVector);
			casa::convertArray(pixelsArray, localpix.reform(IPosition(shape)));
		} else {
			*_log << LogIO::SEVERE
					<< "pixels is not understood, try using an array "
					<< LogIO::POST;
			return rstat;
		}

		rstat = _image->putchunk(pixelsArray, Vector<Int> (blc), Vector<Int> (
				inc), list, locking, replicate);

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::putregion(const ::casac::variant& v_pixels,
		const ::casac::variant& v_pixelmask, const ::casac::record& region,
		const bool list, const bool usemask, const bool locking,
		const bool replicateArray) {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "putregion");
		if (detached())
			return rstat;

		// create Array<Float> pixels
		Array<Float> pixels;
		if (isunset(v_pixels)) {
			// do nothing
		} else if (v_pixels.type() == ::casac::variant::DOUBLEVEC) {
			std::vector<double> pixelVector = v_pixels.getDoubleVec();
			Vector<Int> shape = v_pixels.arrayshape();
			pixels.resize(IPosition(shape));
			Vector<Double> localpix(pixelVector);
			casa::convertArray(pixels, localpix.reform(IPosition(shape)));
		} else if (v_pixels.type() == ::casac::variant::INTVEC) {
			std::vector<int> pixelVector = v_pixels.getIntVec();
			Vector<Int> shape = v_pixels.arrayshape();
			pixels.resize(IPosition(shape));
			Vector<Int> localpix(pixelVector);
			casa::convertArray(pixels, localpix.reform(IPosition(shape)));
		} else {
			*_log << LogIO::SEVERE
					<< "pixels is not understood, try using an array "
					<< LogIO::POST;
			return rstat;
		}

		// create Array<Bool> mask
		Array<Bool> mask;
		if (isunset(v_pixelmask)) {
			// do nothing
		} else if (v_pixelmask.type() == ::casac::variant::DOUBLEVEC) {
			std::vector<double> maskVector = v_pixelmask.getDoubleVec();
			Vector<Int> shape = v_pixelmask.arrayshape();
			mask.resize(IPosition(shape));
			Vector<Double> localmask(maskVector);
			casa::convertArray(mask, localmask.reform(IPosition(shape)));
		} else if (v_pixelmask.type() == ::casac::variant::INTVEC) {
			std::vector<int> maskVector = v_pixelmask.getIntVec();
			Vector<Int> shape = v_pixelmask.arrayshape();
			mask.resize(IPosition(shape));
			Vector<Int> localmask(maskVector);
			casa::convertArray(mask, localmask.reform(IPosition(shape)));
		} else if (v_pixelmask.type() == ::casac::variant::BOOLVEC) {
			std::vector<bool> maskVector = v_pixelmask.getBoolVec();
			Vector<Int> shape = v_pixelmask.arrayshape();
			mask.resize(IPosition(shape));
			Vector<Bool> localmask(maskVector);
			// casa::convertArray(mask,localmask.reform(IPosition(shape)));
			mask = localmask.reform(IPosition(shape));
		} else {
			*_log << LogIO::SEVERE
					<< "mask is not understood, try using an array "
					<< LogIO::POST;
			return rstat;
		}

		if (pixels.size() == 0 && mask.size() == 0) {
			*_log << "You must specify at least either the pixels or the mask"
					<< LogIO::POST;
			return rstat;
		}

		Record * theRegion = toRecord(region);
		rstat = _image->putregion(pixels, mask, *theRegion, list, usemask,
				locking, replicateArray);
		delete theRegion;

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::image* image::rebin(
	const std::string& outfile, const std::vector<int>& bin,
	const ::casac::record& region, const ::casac::variant& vmask,
	const bool dropdeg, const bool overwrite, const bool /* async */,
	const bool stretch
) {
	*_log << _ORIGIN;
	if (detached()) {
		return 0;
	}
	try {
		String outFile(outfile);
		Vector<Int> factors(bin);
		std::auto_ptr<Record> Region(toRecord(region));
		String mask = vmask.toString();
		if (mask == "[]") {
			mask = "";
		}
		std::auto_ptr<ImageInterface<Float> > pImOut(
			_image->rebin(
				outFile, factors, *Region,
				mask, dropdeg, overwrite, stretch
			)
		);
		return new ::casac::image(pImOut.get());
	}
	catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

image* image::regrid(
	const string& outfile, const vector<int>& inshape,
	const record& csys, const vector<int>& inaxes,
	const record& region, const variant& vmask,
	const string& method, const int decimate, const bool replicate,
	const bool doRefChange, const bool dropDegenerateAxes,
	const bool overwrite, const bool forceRegrid,
	const bool specAsVelocity, const bool /* async */,
	const bool stretch
) {
	try {
		*_log << _ORIGIN;
		if (detached()) {
			return 0;
		}
		std::auto_ptr<Record> coordinates(toRecord(csys));
		String methodU(method);
		std::auto_ptr<Record> Region(toRecord(region));
		String mask = vmask.toString();
		if (mask == "[]") {
			mask = "";
		}
		Vector<Int> axes;
		if (!((inaxes.size() == 1) && (inaxes[0] == -1))) {
			axes = inaxes;
		}
		std::auto_ptr<ImageInterface<Float> >pImOut(
			_image->regrid(
				outfile, Vector<Int> (inshape), *coordinates,
				axes, *Region, mask, methodU, decimate, replicate,
				doRefChange, dropDegenerateAxes, overwrite,
				forceRegrid, specAsVelocity, stretch
			)
		);
		return new image(pImOut.get());
	} catch (AipsError x) {
		RETHROW(x);
	}
}

::casac::image* image::rotate(
	const std::string& outfile, const std::vector<int>& inshape,
	const ::casac::variant& inpa, const ::casac::record& region,
	const ::casac::variant& vmask, const std::string& method,
	const int decimate, const bool replicate, const bool dropdeg,
	const bool overwrite, const bool /* async */, const bool stretch
) {
	try {
		*_log << _ORIGIN;
		if (detached()) {
			return 0;
		}
		Vector<Int> shape(inshape);
		Quantum<Double> pa(casaQuantityFromVar(inpa));
		std::auto_ptr<Record> Region(toRecord(region));
		String mask = vmask.toString();
		if (mask == "[]") {
			mask = "";
		}
		std::auto_ptr<ImageInterface<Float> > pImOut(
			_image->rotate(
				outfile, shape, pa, *Region, mask, method,
				decimate, replicate, dropdeg, overwrite, stretch
			)
		);
		return new ::casac::image(pImOut.get());
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

bool image::rename(const std::string& name, const bool overwrite) {
	bool rstat(false);
	try {
		*_log << _ORIGIN;
		if (detached())
			return rstat;

		rstat = _image->rename(name, overwrite);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::replacemaskedpixels(
	const variant& vpixels,
	const record& region, const variant& vmask,
	const bool updateMask, const bool list,
	const bool stretch
) {
	*_log << _ORIGIN;
	if (detached()) {
		return False;
	}
	try {
		String pixels = vpixels.toString();
		std::auto_ptr<Record> pRegion(toRecord(region));
		String maskRegion = vmask.toString();
		if (maskRegion == "[]") {
			maskRegion = "";
		}
		return _image->replacemaskedpixels(
			pixels, *pRegion, maskRegion,
			updateMask, list, stretch
		);
	}
	catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::record*
image::restoringbeam() {
	::casac::record *rstat = 0;
	try {
		*_log << LogOrigin("image", "restoringbeam");
		if (detached())
			return rstat;

		rstat = fromRecord(_image->restoringbeam());
		return rstat;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::image* image::sepconvolve(
	const std::string& outFile, const std::vector<int>& axes,
	const std::vector<std::string>& types,
	const ::casac::variant& widths,
	const double Scale, const ::casac::record& region,
	const ::casac::variant& vmask, const bool overwrite,
	const bool /* async */, const bool stretch
) {
	*_log << _ORIGIN;
	if (detached()) {
		return 0;
	}
	try {
		UnitMap::putUser("pix", UnitVal(1.0), "pixel units");
		std::auto_ptr<Record> pRegion(toRecord(region));
		String mask = vmask.toString();
		if (mask == "[]") {
			mask = "";
		}
		Vector<Int> smoothaxes(axes);
		Vector<String> kernels = toVectorString(types);

		int num = 0;
		Vector<Quantum<Double> > kernelwidths;
		if (widths.type() == ::casac::variant::INTVEC) {
			std::vector<int> widthsIVec = widths.toIntVec();
			num = widthsIVec.size();
			std::vector<double> widthsVec(num);
			for (int i = 0; i < num; i++)
				widthsVec[i] = widthsIVec[i];
			kernelwidths.resize(num);
			Unit u("pix");
			for (int i = 0; i < num; i++) {
				kernelwidths[i] = casa::Quantity(widthsVec[i], u);
			}
		}
		else if (widths.type() == ::casac::variant::DOUBLEVEC) {
			std::vector<double> widthsVec = widths.toDoubleVec();
			num = widthsVec.size();
			kernelwidths.resize(num);
			Unit u("pix");
			for (int i = 0; i < num; i++) {
				kernelwidths[i] = casa::Quantity(widthsVec[i], u);
			}
		}
		else if (widths.type() == ::casac::variant::STRING || widths.type()
				== ::casac::variant::STRINGVEC) {
			toCasaVectorQuantity(widths, kernelwidths);
			num = kernelwidths.size();
		}
		else {
			*_log << LogIO::WARN << "Unrecognized kernelwidth datatype"
					<< LogIO::POST;
			return 0;
		}
		if (kernels.size() == 1 && kernels[0] == "") {
			kernels.resize(num);
			for (int i = 0; i < num; i++) {
				kernels[i] = "gauss";
			}
		}
		if (
			smoothaxes.size() == 0 || ((smoothaxes.size() == 1)
			&& (smoothaxes[0] = -1))
		) {
			smoothaxes.resize(num);
			for (int i = 0; i < num; i++) {
				smoothaxes[i] = i;
			}
		}
		std::auto_ptr<ImageInterface<Float> > pImOut(
			_image->sepconvolve(outFile,
				smoothaxes, kernels, kernelwidths,
				Scale, *pRegion, mask, overwrite,
				stretch
			)
		);
		return new ::casac::image(pImOut.get());
	}
	catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

bool image::set(const ::casac::variant& vpixels, const int pixelmask,
		const ::casac::record& region, const bool list) {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "set");
		if (detached())
			return rstat;

		String pixels = vpixels.toString();
		if (pixels == "[]")
			pixels = "";
		Record *pRegion = toRecord(region);

		if (pixels == "" && pixelmask == -1) {
			*_log << LogIO::WARN
					<< "You must specify at least either the pixels or the mask to set"
					<< LogIO::POST;
			return rstat;
		}
		rstat = _image->set(pixels, pixelmask, *pRegion, list);
		delete pRegion;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::setbrightnessunit(const std::string& unit) {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "setbrightnessunit");
		if (detached())
			return rstat;

		rstat = _image->setbrightnessunit(unit);
		if (!rstat) {
			*_log << "Unable to set brightness units" << LogIO::EXCEPTION;
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::setcoordsys(const ::casac::record& csys) {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "setcoordsys");
		if (detached())
			return rstat;

		Record *coordinates = toRecord(csys);
		rstat = _image->setcoordsys(*coordinates);
		delete coordinates;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::sethistory(const std::string& origin,
		const std::vector<std::string>& history) {
	bool rstat(false);
	try {
		if (detached()) {
			return false;
		}
		if ((history.size() == 1) && (history[0].size() == 0)) {
			LogOrigin lor("image", "sethistory");
			*_log << lor << "history string is empty" << LogIO::POST;
		} else {
			Vector<String> History = toVectorString(history);
			rstat = _image->sethistory(origin, History);
		}
	} catch (AipsError x) {
		LogOrigin lor("image", "sethistory");
		*_log << lor << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::setmiscinfo(const ::casac::record& info) {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "setmiscinfo");
		if (detached())
			return rstat;

		Record *tmp = toRecord(info);
		rstat = _image->setmiscinfo(*tmp);
		delete tmp;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

std::vector<int> image::shape() {
	std::vector<int> rstat(0);
	*_log << LogOrigin("image", "shape");
	if (detached())
		return rstat;
	try {
		Vector<Int> dummy = _image->getImage()->shape().asVector();
		dummy.tovector(rstat);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::setrestoringbeam(const ::casac::variant& major,
		const ::casac::variant& minor, const ::casac::variant& pa,
		const ::casac::record& beam, const bool deleteIt, const bool log) {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "setrestoringbeam");
		if (detached())
			return rstat;

		//
		casa::Quantity beam0(casaQuantityFromVar(major));
		casa::Quantity beam1(casaQuantityFromVar(minor));
		casa::Quantity beam2(casaQuantityFromVar(pa));

		Record *rec = toRecord(beam);
		rstat = _image->setrestoringbeam(beam0, beam1, beam2, *rec, deleteIt,
				log);
		delete rec;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::record* image::statistics(
	const std::vector<int>& axes, const ::casac::record& region,
	const ::casac::variant& mask,
	const std::vector<std::string>& plotstats,
	const std::vector<double>& includepix,
	const std::vector<double>& excludepix, const std::string& plotter,
	const int nx, const int ny, const bool list, const bool force,
	const bool disk, const bool robust, const bool verbose,
	const bool /* async */, const bool stretch, const string& logfile,
	const bool append
) {
	*_log << _ORIGIN;
	if (detached()) {
		*_log << "Image not attached" << LogIO::POST;
		return 0;
	}
	try {
		std::auto_ptr<Record> regionRec(toRecord(region));
		if (regionRec->nfields() == 0) {
			regionRec.reset(0);
		}
		String mtmp = mask.toString();
		if (mtmp == "false" || mtmp == "[]") {
			mtmp = "";
		}

		Vector<String> plotStats = toVectorString(plotstats);
		if (plotStats.size() == 0) {
			plotStats.resize(2);
			plotStats[0] = "mean";
			plotStats[1] = "sigma";
		}

		Vector<Int> tmpaxes(axes);
		if (tmpaxes.size() == 1 && tmpaxes[0] == -1) {
			tmpaxes.resize(0);
		}
		Vector<Float> tmpinclude;
		Vector<Float> tmpexclude;
		if (
			!(
				includepix.size() == 1
				&& includepix[0] == -1
			)
		) {
			tmpinclude.resize(includepix.size());
			for (uInt i=0; i<includepix.size(); i++) {
				tmpinclude[i] = includepix[i];
			}
		}
		if (!(excludepix.size() == 1 && excludepix[0] == -1)) {
			tmpexclude.resize(excludepix.size());
			for (uInt i = 0; i < excludepix.size(); i++) {
				tmpexclude[i] = excludepix[i];
			}
		}
		*_log << LogIO::NORMAL << "Determining stats for image "
				<< _image->name(True) << LogIO::POST;
		Record ret;
		ImageStatsCalculator calculator(
			_image.get(), "", regionRec.get(), "", "", "", mtmp
		);
		calculator.setPlotStats(plotStats);
		calculator.setAxes(tmpaxes);
		calculator.setIncludePix(tmpinclude);
		calculator.setPlotter(plotter);
		calculator.setExcludePix(tmpexclude);
		calculator.setNXNY(nx, ny);
		calculator.setList(list);
		calculator.setForce(force);
		calculator.setDisk(disk);
		calculator.setRobust(robust);
		calculator.setVerbose(verbose);
		calculator.setStretch(stretch);
		calculator.setLogfile(logfile);
		calculator.setLogfileAppend(append);
		return fromRecord(calculator.calculate());

		/*
		Record retval;
		if (
			! _image->statistics(
				retval, tmpaxes, *regionRec, mtmp,
				plotStats, tmpinclude, tmpexclude, plotter,
				nx, ny, list, force, disk, robust, False,
				stretch
			)
		) {
			return 0;
		}
		if (verbose || ! logfile.empty()) {
			ImageCollapser collapsed(
				_image->getImage(), axes, False,
				ImageCollapser::ZERO, "", False
			);
			std::auto_ptr<ImageInterface<Float> > tempIm(
				collapsed.collapse(True)
			);
			CoordinateSystem csys = tempIm->coordinates();
			Vector<String> worldAxes = csys.worldAxisNames();
			IPosition imShape = tempIm->shape();
			vector<uInt> colwidth;
			Int stokesCol = -1;
			Int freqCol = -1;
			Int raCol = -1;
			Int decCol = -1;
			IPosition otherCol;
			for (Int i=worldAxes.size()-1; i>=0; i--) {
				String gg = worldAxes[i];
				gg.upcase();
				if (gg == "RIGHT ASCENSION") {
					raCol = i;
				}
				else if (gg == "DECLINATION") {
					decCol = i;
				}
				else if (gg == "FREQUENCY") {
					freqCol = i;
				}
				else if (gg == "STOKES") {
					stokesCol = i;
				}
				else {
					otherCol.append(IPosition(1, i));
				}
			}
			IPosition idx(worldAxes.size(), 0);
			uInt myloc = 0;
			IPosition reportAxes;

			if (stokesCol >= 0) {
				idx[myloc] = stokesCol;
				if (imShape[stokesCol] > 1) {
					reportAxes.prepend(IPosition(1, stokesCol));
				}
				myloc++;
			}
			if (freqCol >= 0) {
				idx[myloc] = freqCol;
				if (imShape[freqCol] > 1) {
					reportAxes.prepend(IPosition(1, freqCol));
				}
				myloc++;
			}
			if (decCol >= 0) {
				idx[myloc] = decCol;
				if (imShape[decCol] > 1) {
					reportAxes.prepend(IPosition(1, decCol));
				}
				myloc++;
			}
			if (raCol >= 0) {
				idx[myloc] = raCol;
				if (imShape[raCol] > 1) {
					reportAxes.prepend(IPosition(1, raCol));
				}
				myloc++;
			}
			if (otherCol.nelements() > 0) {
				idx.prepend(otherCol);
				for (uInt i=0; i<otherCol.nelements(); i++) {
					if (imShape[otherCol[i] > 1]) {
						reportAxes.append(IPosition(1, otherCol[i]));
					}
				}
			}
			ostringstream oss;
			for (uInt i=0; i<reportAxes.nelements(); i++) {
				String gg = worldAxes[reportAxes[i]];
				gg.upcase();
				uInt width = gg == "STOKES" ? 6 : gg == "FREQUENCY"?  16: 15;
				colwidth.push_back(width);
				oss << setw(width) << worldAxes[reportAxes[i]] << "(Pixel)" << " ";
				width = 6;
				colwidth.push_back(width);
			}
			Vector<Int> axesMap = reportAxes.asVector();
			GenSort<Int>::sort(axesMap);
			oss << "Npts          Sum           Mean          Rms           Std dev       Minimum       Maximum     " << endl;
			for (uInt i=0; i<7; i++) {
				colwidth.push_back(12);
			}
			TileStepper ts(
				tempIm->niceCursorShape(),
				IPosition(tempIm->ndim(), 1), idx
			);
			RO_MaskedLatticeIterator<Float> inIter(
				*tempIm, ts
			);
			Vector<Double> world;
			IPosition arrayIndex(axesMap.nelements(), 0);
			IPosition position(tempIm->ndim(), 0);
			oss << std::scientific;
			uInt width = 13;
			Vector<Vector<String> > coords(reportAxes.size());
			for (uInt i=0; i<reportAxes.size(); i++) {
				Vector<Double> indices(imShape[reportAxes[i]]);
				indgen(indices);
				uInt prec = reportAxes[i] == freqCol ? 9 : 5;
				ImageUtilities::pixToWorld(
					coords[i], csys, reportAxes[i], axes,
					IPosition(imShape.nelements(),0), imShape-1, indices, prec
				);
			}
			for (inIter.reset(); ! inIter.atEnd(); inIter++) {
				position = inIter.position();
				csys.toWorld(world, position);
				uInt colNum = 0;
				for (uInt i=0; i<reportAxes.nelements(); i++) {
					oss << setw(colwidth[colNum]);
					oss	<< coords[i][position[reportAxes[i]]];// world[reportAxes[i]];
					colNum++;
					oss << " " << setw(colwidth[colNum])
						<< position[reportAxes[i]] << " ";
					colNum++;
				}
				for (uInt i=0; i<axesMap.nelements(); i++) {
					arrayIndex[i] = position[axesMap[i]];
				}
				oss << std::setw(width) << retval.asArrayDouble("npts")(arrayIndex) << " "
					<< std::setw(width) << retval.asArrayDouble("sum")(arrayIndex) << " "
					<< std::setw(width) << retval.asArrayDouble("mean")(arrayIndex) << " "
					<< std::setw(width) << retval.asArrayDouble("rms")(arrayIndex) << " "
					<< std::setw(width) << retval.asArrayDouble("sigma")(arrayIndex) << " "
					<< std::setw(width) << retval.asArrayDouble("min")(arrayIndex) << " "
					<< std::setw(width) << retval.asArrayDouble("max")(arrayIndex) << endl;
			}
			if (verbose) {
				*_log << LogIO::NORMAL << oss.str() << LogIO::POST;
			}
		}

		return fromRecord(retval);
		*/
	}
	catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

bool image::twopointcorrelation(
	const std::string& outfile,
	const ::casac::record& region, const ::casac::variant& vmask,
	const std::vector<int>& axes, const std::string& method,
	const bool overwrite, const bool stretch
) {
	*_log << _ORIGIN;
	if (detached()) {
		return false;
	}
	try {
		String outFile(outfile);
		std::auto_ptr<Record> Region(toRecord(region));
		String mask = vmask.toString();
		if (mask == "[]")
			mask = "";
		Vector<Int> iAxes;
		if (!(axes.size() == 1 && axes[0] == -1)) {
			iAxes = axes;
		}
		return _image->twopointcorrelation(
			outFile, *Region, mask, iAxes,
			method, overwrite, stretch
		);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::image* image::subimage(
	const string& outfile, const record& region,
	const variant& vmask, const bool dropDegenerateAxes,
	const bool overwrite, const bool list, const bool stretch
) {
	try {
		*_log << LogOrigin("image", __FUNCTION__);
		if (detached()) {
			return 0;
		}
		std::auto_ptr<Record> regionRec(toRecord(region));
		String mask = vmask.toString();
		if (mask == "[]") {
			mask = "";
		}
		std::auto_ptr<ImageInterface<Float> > tmpIm(
			_image->subimage(
				outfile, *regionRec, mask, dropDegenerateAxes,
				overwrite, list, stretch
			)
		);
		return new image(tmpIm.get());
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

std::vector<std::string> image::summary( const std::string& doppler, const bool list,
	       	const bool pixelorder, casac::record& header) {
	std::vector<string> rstat;
	try {
		*_log << LogOrigin("image", "summary");
		if (detached()) {
			return rstat;
		}
		Record retval;
		rstat = fromVectorString(_image->summary(retval, doppler, list,
				pixelorder));
		header = *fromRecord(retval);

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::tofits(
	const std::string& fitsfile, const bool velocity,
	const bool optical, const int bitpix, const double minpix,
	const double maxpix, const ::casac::record& region,
	const ::casac::variant& vmask, const bool overwrite,
	const bool dropdeg, const bool deglast, const bool dropstokes,
	const bool stokeslast, const bool wavelength, const bool airwavelength,
	const bool /* async */, const bool stretch
) {
	*_log << _ORIGIN;
	if (detached()) {
		return false;
	}
	try {
		if (fitsfile.empty()) {
			*_log << "fitsfile must be specified" << LogIO::EXCEPTION;
		}
		if (fitsfile == "." || fitsfile == "..") {
			*_log << "Invalid fitsfile name " << fitsfile << LogIO::EXCEPTION;
		}
		std::auto_ptr<Record> pRegion(toRecord(region));
		String mask = vmask.toString();
		if (mask == "[]") {
			mask = "";
		}

		String origin;
		{
			ostringstream buffer;
			buffer << "CASA ";
			VersionInfo::report(buffer);
			origin = String(buffer);
		}
		return _image->tofits(
			fitsfile, velocity, optical, bitpix, minpix,
			maxpix, *pRegion, mask, overwrite, dropdeg, deglast,
			dropstokes, stokeslast, wavelength, airwavelength, origin,
			stretch
		);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
			<< LogIO::POST;
		RETHROW(x);
	}
}

bool image::toASCII(const std::string& outfile, const ::casac::record& region,
		const ::casac::variant& mask, const std::string& sep,
		const std::string& format, const double maskvalue, const bool overwrite,
		const bool stretch) {
	// sep is hard-wired as ' ' which is what imagefromascii expects
	*_log << _ORIGIN;
	if (detached()) {
		return False;
	}

	try {
		String Mask;
		if (mask.type() == ::casac::variant::BOOLVEC) {
			Mask = "";
		}
		else if (
			mask.type() == ::casac::variant::STRING
			|| mask.type() == ::casac::variant::STRINGVEC
		) {
			Mask = mask.toString();
		}
		std::auto_ptr<Record> pRegion(toRecord(region));
		return _image->toASCII(
			outfile, *pRegion, Mask, sep, format,
			maskvalue, overwrite, stretch
		);
	}
	catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

std::string image::type() {
	return "image";
}

//std::vector<double>
::casac::record*
image::topixel(const ::casac::variant& value) {
	//  std::vector<double> rstat;
	::casac::record *rstat = 0;
	try {
		*_log << LogOrigin("image", "topixel");
		if (detached())
			return rstat;

		Vector<Int> bla;
		CoordinateSystem cSys = _image->coordsys(bla);
		::casac::coordsys mycoords;
		//NOT using _image->toworld as most of the math is in casac namespace
		//in coordsys...should revisit this when casac::coordsys is cleaned
		mycoords.setcoordsys(cSys);
		rstat = mycoords.topixel(value);

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

::casac::record*
image::toworld(const ::casac::variant& value, const std::string& format) {
	::casac::record *rstat = 0;
	try {
		*_log << LogOrigin("image", "toworld");
		if (detached())
			return rstat;

		Vector<Double> pixel;
		if (isunset(value)) {
			pixel.resize(0);
		} else if (value.type() == ::casac::variant::DOUBLEVEC) {
			//cout << "double vec " << endl;
			pixel = value.getDoubleVec();
		} else if (value.type() == ::casac::variant::INTVEC) {
			//cout << "int vec " << endl;

			variant vcopy = value;
			Vector<Int> ipixel = vcopy.asIntVec();
			//cout << "* ipixel " << ipixel << endl;
			Int n = ipixel.size();
			pixel.resize(n);
			for (int i = 0; i < n; i++)
				pixel[i] = ipixel[i];
		} else if (value.type() == ::casac::variant::RECORD) {
			//cout << "record " << endl;
			::casac::variant localvar(value);
			Record *tmp = toRecord(localvar.asRecord());
			if (tmp->isDefined("numeric")) {
				pixel = tmp->asArrayDouble("numeric");
			} else {
				*_log << LogIO::SEVERE << "unsupported record type for value"
						<< LogIO::EXCEPTION;
				return rstat;
			}
			delete tmp;
		} else {
			*_log << LogIO::SEVERE << "unsupported data type for value"
					<< LogIO::EXCEPTION;
			return rstat;
		}
		//cout << "*** pixel " << pixel << endl;
		rstat = fromRecord(_image->toworld(pixel, format));

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::unlock() {
	bool rstat(false);
	try {
		*_log << LogOrigin("image", "unlock");
		if (detached())
			return rstat;

		rstat = _image->unlock();
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::detached() const {
	if (_image.get() == 0 || _image->detached()) {
		*_log << _ORIGIN;
		*_log << LogIO::SEVERE
				<< "Image is detached - cannot perform operation." << endl
				<< "Call image.open('filename') to reattach." << LogIO::POST;
		return True;
	}
	return False;
}

::casac::record*
image::setboxregion(const std::vector<double>& blc,
		const std::vector<double>& trc, const bool frac,
		const std::string& infile) {
	casac::record* rstat = 0;
	try {

		*_log << LogOrigin("image", "setboxregion");
		if (detached())
			return rstat;

		Record tempR(_image->setboxregion(Vector<Double> (blc),
				Vector<Double> (trc), frac, infile));
		rstat = fromRecord(tempR);

	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return rstat;
}

bool image::maketestimage(
	const std::string& outfile, const bool overwrite
) {
	try {
		if (_log.get() == 0)
			_log.reset(new LogIO());
		_image.reset(new ImageAnalysis());
		*_log << _ORIGIN;
		return _image->maketestimage(outfile, overwrite);
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
			<< LogIO::POST;
		RETHROW(x);
	}
}

image* image::newimagefromimage(
	const string& infile, const string& outfile,
	const record& region, const variant& vmask,
	const bool dropdeg, const bool overwrite
) {
	try {
		if (_log.get() == 0) {
			_log.reset(new LogIO());
		}
		std::auto_ptr<ImageAnalysis> newImage(new ImageAnalysis());
		*_log << _ORIGIN;

		String mask;

		if (vmask.type() == variant::BOOLVEC) {
			mask = "";
		}
		else if (
			vmask.type() == variant::STRING
			|| vmask.type() == variant::STRINGVEC
		) {
			mask = vmask.toString();
		}
		else if (vmask.type() == ::casac::variant::RECORD) {
			*_log << LogIO::SEVERE
					<< "Don't support region masking yet, only valid LEL "
					<< LogIO::POST;
			return 0;
		}
		else {
			*_log << LogIO::SEVERE
					<< "Mask is not understood, try a valid LEL string "
					<< LogIO::POST;
			return 0;
		}

		std::auto_ptr<Record> regionPtr(toRecord(region));
		auto_ptr<ImageInterface<Float> >outIm(
			newImage->newimage(
				infile, outfile,*regionPtr,
				mask, dropdeg, overwrite
			)
		);
		if (outIm.get() != 0) {
			return new image(outIm.get());
		} else {
			return new image();
		}
	}
	catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
			<< LogIO::POST;
		RETHROW(x);
	}
}

image* image::newimagefromfile(const std::string& fileName) {
	try {
		if (_log.get() == 0) {
			_log.reset(new LogIO());
		}
		std::auto_ptr<ImageAnalysis> newImage(new ImageAnalysis());
		*_log << _ORIGIN;
		std::auto_ptr<ImageInterface<Float> > outIm(
			newImage->newimagefromfile(fileName)
		);
		if (outIm.get() != 0) {
			return new image(outIm.get());
		} else {
			return new image();
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
			<< LogIO::POST;
		RETHROW(x);
	}
}

image* image::newimage(const string& fileName) {
	return newimagefromfile(fileName);
}

image* image::newimagefromarray(
	const string& outfile, const variant& pixels,
	const record& csys, const bool linear,
	const bool overwrite, const bool log
) {
	try {
		if (_log.get() != 0) {
			_log.reset(new LogIO());
		}
		auto_ptr<ImageAnalysis> newImage(
			new ImageAnalysis()
		);
		*_log << _ORIGIN;
		// Some protection.  Note that a Glish array, [], will
		// propagate through to here to have ndim=1 and shape=0
		Vector<Int> shape = pixels.arrayshape();
		uInt ndim = shape.size();
		if (ndim == 0) {
			*_log << "The pixels array is empty" << LogIO::EXCEPTION;
		}
		for (uInt i = 0; i < ndim; i++) {
			if (shape(i) <= 0) {
				*_log << "The shape of the pixels array is invalid"
						<< LogIO::EXCEPTION;
			}
		}
		Array<Float> pixelsArray;
		if (pixels.type() == variant::DOUBLEVEC) {
			vector<double> pixelVector = pixels.getDoubleVec();
			Vector<Int> shape = pixels.arrayshape();
			pixelsArray.resize(IPosition(shape));
			Vector<Double> localpix(pixelVector);
			convertArray(pixelsArray, localpix.reform(IPosition(shape)));
		}
		else if (pixels.type() == ::casac::variant::INTVEC) {
			vector<int> pixelVector = pixels.getIntVec();
			Vector<Int> shape = pixels.arrayshape();
			pixelsArray.resize(IPosition(shape));
			Vector<Int> localpix(pixelVector);
			convertArray(pixelsArray, localpix.reform(IPosition(shape)));
		}
		else {
			*_log << LogIO::SEVERE
					<< "pixels is not understood, try using an array "
					<< LogIO::POST;
			return new image();
		}
		auto_ptr<Record> coordinates(toRecord(csys));
		auto_ptr<ImageInterface<Float> > outIm(
			newImage->newimagefromarray(
				outfile, pixelsArray, *coordinates,
				linear, overwrite, log
			)
		);
		if (outIm.get() != 0) {
			return new image(outIm.get());
		} else {
			return new image();
		}
	}
	catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

image* image::newimagefromshape(
	const string& outfile, const vector<int>& shape,
	const record& csys, const bool linear,
	const bool overwrite, const bool log
) {
	try {
		if (_log.get() != 0) {
			_log.reset(new LogIO());
		}
		auto_ptr<ImageAnalysis> newImage(new ImageAnalysis());
		*_log << _ORIGIN;
		auto_ptr<Record> coordinates(toRecord(csys));
		auto_ptr<ImageInterface<Float> > outIm(
			newImage->newimagefromshape(
				outfile, Vector<Int>(shape), *coordinates,
				linear, overwrite, log
			)
		);
		if (outIm.get() != 0) {
			return new image(outIm.get());
		} else {
			return new image();
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
			<< LogIO::POST;
		RETHROW(x);
	}
}

image* image::newimagefromfits(
	const string& outfile, const string& fitsfile,
	const int whichrep, const int whichhdu,
	const bool zeroBlanks, const bool overwrite
) {
	try {
		if (_log.get() == 0) {
			_log.reset(new LogIO());
		}
		auto_ptr<ImageAnalysis> newImage(new ImageAnalysis());
		*_log << _ORIGIN;
		auto_ptr<ImageInterface<Float> > outIm(
			newImage->newimagefromfits(
				outfile,
				fitsfile, whichrep, whichhdu, zeroBlanks, overwrite
			)
		);
		if (outIm.get() != 0) {
			return new image(outIm.get());
		} else {
			return new image();
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}

::casac::variant*
image::makearray(const double v, const std::vector<int>& shape) {
	int ndim = shape.size();
	int nelem = 1;
	for (int i = 0; i < ndim; i++)
		nelem *= shape[i];
	std::vector<double> element(nelem);
	for (int i = 0; i < nelem; i++)
		element[i] = v;
	return new ::casac::variant(element, shape);
}

::casac::record* image::echo(const ::casac::record& v, const bool godeep) {
	casac::record* rstat = 0;
	try {
		Record *tempo = toRecord(v);
		rstat = fromRecord(*(_image->echo(*tempo, godeep)));

		delete tempo;

	} catch (AipsError x) {
		*_log << LogOrigin("image", "echo");
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}

	return rstat;
}

void image::outputvariant(::casac::variant& v) {
	try {
		int len = 5;
		std::vector<int> vi(len);
		for (uInt i = 0; i < vi.size(); i++) {
			vi[i] = i;
		}
		std::vector<int> vi_shape = *new std::vector<int>(1);
		vi_shape[0] = len;
		v = new ::casac::variant(vi, vi_shape);
	} catch (AipsError x) {
		*_log << LogOrigin("image", "outputvariant");
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	//cout << "all is well so far" << endl;
}

casac::record*
image::recordFromQuantity(const casa::Quantity q) {
	::casac::record *r = 0;
	try {
		*_log << LogOrigin("image", "recordFromQuantity");
		String error;
		casa::Record R;
		if (QuantumHolder(q).toRecord(error, R)) {
			r = fromRecord(R);
		} else {
			*_log << LogIO::SEVERE << "Could not convert quantity to record."
					<< LogIO::POST;
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return r;
}

::casac::record*
image::recordFromQuantity(const Quantum<Vector<Double> >& q) {
	::casac::record *r = 0;
	try {
		*_log << LogOrigin("image", "recordFromQuantity");
		String error;
		casa::Record R;
		if (QuantumHolder(q).toRecord(error, R)) {
			r = fromRecord(R);
		} else {
			*_log << LogIO::SEVERE << "Could not convert quantity to record."
					<< LogIO::POST;
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return r;
}

casa::Quantity image::casaQuantityFromVar(const ::casac::variant& theVar) {
	casa::Quantity retval;
	try {
		*_log << LogOrigin("image", "casaQuantityFromVar");
		casa::QuantumHolder qh;
		String error;
		if (theVar.type() == ::casac::variant::STRING || theVar.type()
				== ::casac::variant::STRINGVEC) {
			if (!qh.fromString(error, theVar.toString())) {
				*_log << LogIO::SEVERE << "Error " << error
						<< " in converting quantity " << LogIO::POST;
			}
			retval = qh.asQuantity();
		}
		if (theVar.type() == ::casac::variant::RECORD) {
			//NOW the record has to be compatible with QuantumHolder::toRecord
			::casac::variant localvar(theVar); //cause its const
			Record * ptrRec = toRecord(localvar.asRecord());
			if (!qh.fromRecord(error, *ptrRec)) {
				*_log << LogIO::SEVERE << "Error " << error
						<< " in converting quantity " << LogIO::POST;
			}
			delete ptrRec;
			retval = qh.asQuantity();
		}
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
	return retval;
}

bool image::isconform(const string& other) {
	*_log << LogOrigin("image", __FUNCTION__);

	if (detached()) {
		return False;
	}
	try {

		ImageInterface<Float> *oth = 0;
		ImageUtilities::openImage(oth, String(other), *_log);
		if (oth == 0) {
			throw AipsError("Unable to open image " + other);
		}
		std::auto_ptr<ImageInterface<Float> > x(oth);
		const ImageInterface<Float> *mine = _image->getImage();
		if (mine->shape().isEqual(x->shape()) && mine->coordinates().near(
				x->coordinates())) {
			Vector<String> mc = mine->coordinates().worldAxisNames();
			Vector<String> oc = x->coordinates().worldAxisNames();
			if (mc.size() != oc.size()) {
				return False;
			}
			for (uInt i = 0; i < mc.size(); i++) {
				if (mc[i] != oc[i]) {
					return False;
				}
			}
			return True;
		}
		return False;
	} catch (AipsError x) {
		*_log << LogIO::SEVERE << "Exception Reported: " << x.getMesg()
				<< LogIO::POST;
		RETHROW(x);
	}
}
void image::_getRegion(
	String& regionName, std::auto_ptr<Record>& regionRecord,
	const variant& region
) const {

	if (
		region.type() != variant::BOOLVEC
		&& region.type() != variant::STRING
		&& region.type() != variant::RECORD
	) {
		*_log << "Unsupported type for region " << region.type()
			<< LogIO::EXCEPTION;
	}

	regionRecord.reset(0);
	regionName = (
		region.type() == variant::STRING || region.size() == 0
	)
		? region.size() == 0
			? ""
			: region.toString()
		: "";
	if (region.type() == variant::RECORD) {
		variant regionCopy = region;
		regionRecord.reset(
			toRecord(regionCopy.asRecord())
		);
	}
}


} // casac namespace
