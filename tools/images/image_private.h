/* Private parts of image component */
public:

// Allow other components that return image tool to open an image
//bool open(const casa::ImageInterface<casa::Float>* inImage);

// The constructed object will manage the input pointer with a
// shared_ptr
image(casa::ImageInterface<casa::Float> * inImage);

image(std::tr1::shared_ptr<casa::ImageInterface<casa::Float> > inImage);

private:


mutable casa::LogIO _log;
std::auto_ptr<casa::ImageAnalysis> _image;
std::auto_ptr<casa::ImageStatsCalculator> _stats;

static const casa::String _class;

// Private ImageInterface constructor to make components on the fly

//image(casa::ImageInterface<casa::Float>* inImage, const bool cloneInputPointer);


// Having private version of IS and IH means that they will
// only recreate storage images if they have to

// Prints an error message if the image DO is detached and returns True.
bool detached() const;

casac::record* recordFromQuantity(casa::Quantity q);
casac::record* recordFromQuantity(const casa::Quantum<casa::Vector<casa::Double> >& q);
casa::Quantity casaQuantityFromVar(const ::casac::variant& theVar);
std::auto_ptr<casa::Record> _getRegion(const variant& region, const bool nullIfEmpty) const;


