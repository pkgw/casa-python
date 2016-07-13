/* Private parts for atmosphere */

/* 
   Assert ATM type is in permissive range of enum, typeAtm_t
 */
void check_atmtype_enum(int atmtype);

/* 
   Assert int value is positive or zero.
   This function is necessary because tool interface does not
   support parameter in unsigned integer.
 */
void assert_unsigned_int(int value);

atm::AtmProfile *pAtmProfile;
atm::SpectralGrid *pSpectralGrid;
atm::RefractiveIndexProfile *pRefractiveIndexProfile;
atm::SkyStatus *pSkyStatus;
casa::LogIO *itsLog;

