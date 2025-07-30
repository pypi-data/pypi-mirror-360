#ifndef numerical_common_definitions_h
#define numerical_common_definitions_h

#define MC2MeV 0.510999 // electron rest energy
#define COEF_K_VALUE 93.3729 // Peak Field -> K value
#define COEF_E1ST 9.49634 /* energy of 1st harmonic */
#define COEF_EC 665.025 /* critical energy */
#define PI 3.1415926535897932384626433832795 // pi
#define PId2 1.5707963267948966192313216916398 // pi/2
#define PI2 6.283185307179586476925286766559 // 2pi 
#define PISQ 9.8696044010893586188344909998762 // pi^2 
#define PISQ4 97.409091034002437236440332688705 // pi^4
#define DEGREE2RADIAN 0.017453292519943295769236907684886 /* PI/180 */
#define QE 1.60217733e-19 /* electron charge */
#define CC 2.9979246e+8 /* velocity of light */
#define PLANCK 4.1356692e-15 /* Planck constant eV/sec^(-1): not divided by 2pi */
#define PLANKCC 1.97327053e-07 /* Planck constant/2pi * CC; k -> energy */
#define ONE_ANGSTROM_eV 12398.4247 /* 10^(-10)m = ??eV */
#define COEF_BPEAK 1.80063 /* Halbach array peak field */

#define INFINITESIMAL 1.0e-30 // small number (abs < 0 means 0)
#define MAXIMUM_EXPONENT 100.0
#define GAUSSIAN_MAX_REGION 4.0
#define MAX_ARG_SN_APPROX 1.0e-3 /* if lower than this, sn is calculated by
								   approximated expression */

#define SQRT2 1.4142135623730950488016887242097 /* sqrt(2) */
#define SQRTPI2 2.506628274631000502415765284811 /* sqrt(2pi) */
#define SQRTPI 1.7724538509055160272981674833411 /* sqrt(pi) */
#define SQRT3 1.7320508075688772935274463415059 /* sqrt(3) */
#define LN2DIV2PI 0.110318 /* ln2/2/pi */

#define Sigma2FWHM 2.354820045 /* 2sqrt(2ln2) */
#define GAUSSIAN2LORENTZIAN 4.717444523 /* conversion for Gaussian<->Lorentzian */

#define FFT_FILTER_GAUSSIAN 5.0 /* cut of for smoothing a noisy profile with FFT filter */
#define RMS_CUTOFF 0.05 /* evaluate the r.m.s. with cutoff */

#define EXP2AVOID_ROUNDING_ERROR 1.0e-4

#define CSR_GAUISSIAN_MAX_REGION 3.0
#define SINC_MAX_DIVISION_POW2 4
#define SINC_INTEG_DIVISION 3.0
#define GAUSSIAN_MIN_DIVISION 0.5
#define RADIATION_POWER_SPREAD_LIMIT 10.0
#define BEAM_HALLO_DIMENSION 3.0
#define MAX_EP_EC_BM 30.0 /* maximum ratio ep/ec for B.M. */
#define LOG1E6 13.816
#define LOG2 0.301029995
#define MAXIMUM_ENERGY4POWER_CRITICAL 10.0

#define MIN_BESSEL_VALUE 1.0e-10
#define MAX_ARG_BES_NEG 1.0e-3
#define MAX_ARG_BES_APPROX 1.0e-4
#define BESSUM_EPS 3.0e-3 // accuracy for calculation of bessel function summation
#define DXY_LOWER_LIMIT 1.0e-10

#define COEF_K_VALUE 93.3729 /* K value */
#define COEF_TOTAL_POWER_ID 3.6284427e-5 /* total power from ID */
#define Z0VAC 376.7303 /* vacuum impedence */
#define COEF_ACC_FAR_BT 586.679 // B(Tesla) to gamma*d(beta)/dz
#define COEF_BM_RADIUS 3.33564 /* bending magnet radius */
#define KX_EXIST 1.0e-10 /* judge EMPW or not */
#define ERadius 2.817938e-15 /* classical electron radius */

#define COEF_PWDNS_ID_FAR 1.34447e-5 /* power density from an ID for far field */
#define COEF_PWDNS_NEAR  51.488 /* power density for near field */
#define COEF_PWDNS_BM 5.4206e-3 /* power density form B.M.*/
#define COEF_FLUX_UND	1.7443e+14 /* flux density from undulator */
#define COEF_FLUX_BM 1.325e+13 /* flux density from B.M.*/
#define COEF_TOT_FLUX_BM 1.5438e+17 /* total flux denisty from B.M. */
#define COEF_LINPWD 4.2208e-3 /* linear power density */

#define COEF_ALPHA 7.29735308e-3 /* fine-structure constant */
#define ALFVEN_CURR 1.7037e+4 /* Alfven current in A */

#endif

