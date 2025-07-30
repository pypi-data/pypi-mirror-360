#include <math.h>
#include "orbit_components_operation.h"
#include "particle_generator.h"
#include "common.h"

OrbitComponents::OrbitComponents()
{
	Clear();
}

void OrbitComponents::Clear()
{
    _acc[0] = _acc[1] = _beta[0] = _beta[1] = _xy[0] = _xy[1] = _rz = 0.0;
	_tsqrt = 1.0;
}

void OrbitComponents::SetComponents(double acc[], double betaxy[], double xy[], double rz)
{
	for(int j = 0; j < 2; j++){
		_acc[j] = acc[j];
		_beta[j] = betaxy[j];
		_xy[j] = xy[j];
	}
    _rz = rz;
}

void OrbitComponents::SetComponents(OrbitComponents *orbit)
{
	for(int j = 0; j < 2; j++){
		_acc[j] = orbit->_acc[j];
		_beta[j] = orbit->_beta[j];
		_xy[j] = orbit->_xy[j];
	}
    _rz = orbit->_rz;
	_tsqrt = orbit->_tsqrt;
}

void OrbitComponents::SetComponents(Particle *particle)
{
	for(int j = 0; j < 2; j++){
		_acc[j] = 0;
		_beta[j] = particle->_qxy[j];
		_xy[j] = particle->_xy[j];
	}
	_tsqrt = 1.0+particle->_tE[1];
    _rz = 0;
}

void OrbitComponents::Flip()
{
	for (int j = 0; j < 2; j++){
		_acc[j] = -_acc[j];
		_beta[j] = -_beta[j];
		_xy[j] = -_xy[j];
	}
    _rz = -_rz;
}

double OrbitComponents::GetPsi4FarField(double z, double gtxy[], double gt2, double K2)
{
    return ((1.0+gt2)*z+_rz-2.0*(_xy[0]*gtxy[0]+_xy[1]*gtxy[1]))/(1.0+K2+gt2)*PI2;
}

double OrbitComponents::GetPDFunc4FarField(double gtxy[], double *D)
{
    double pd, XY[2];

    XY[0] = gtxy[0]-_beta[0];
    XY[1] = gtxy[1]-_beta[1];
    *D = 1.0+XY[0]*XY[0]+XY[1]*XY[1];
    pd = (_acc[0]*_acc[0]+_acc[1]*_acc[1])/(*D)/(*D)/(*D)
        -4.0*pow(XY[0]*_acc[0]+XY[1]*_acc[1], 2.0)/pow(*D, 5.0);
    return pd;
}

void OrbitComponents::GetRelativeCoordinate(double z, double gamma2,
        double *XYZ, double *tau, double *Theta, double *D, double *R)
{
    double X, Y, Z, XY, Z2;
    double xr, yr, zr;
	bool isnear = false;

	xr = _xy[0];
	yr = _xy[1];
	zr = z;

    X = XYZ[0]-xr;
    Y = XYZ[1]-yr;
    Z = XYZ[2]-zr;

	XY = X*X+Y*Y;
	Z2 = Z*Z;
    *R = sqrt(XY+Z2);

	if(*R < INFINITESIMAL){
		Z = INFINITESIMAL;
	    Theta[0] = -_beta[0];
		Theta[1] = -_beta[1];
	}
	else if(Z2 < 100.0*XY || Z < INFINITESIMAL){
		isnear = true;
	    Theta[0] = atan2(X, Z)-_beta[0];
		Theta[1] = atan2(Y, Z)-_beta[1];
	}
	else{
	    Theta[0] = X/Z-_beta[0];
		Theta[1] = Y/Z-_beta[1];
	}

	double tsq = _tsqrt*_tsqrt;
	*D = 1.0/tsq+hypotsq(Theta[0], Theta[1])*gamma2;
	if(isnear){
	    *tau = zr/tsq+(_rz+2.0*((*R)-Z))*gamma2;
	}
	else{
	    *tau = zr/tsq+(_rz+(X*X+Y*Y)/Z)*gamma2;
	}
}

void OrbitComponents::GetRelativeCoordinateFar(
	double z, double gamma2, double *theta, double *tau, double *Theta, double *D, 
	double *Zobs, double *xyorb)
{
	double xyr[2];
	for(int j = 0; j < 2; j++){
		Theta[j] = theta[j]-_beta[j];
		if(xyorb == nullptr){
			xyr[j] = _xy[j];
		}
		else{
			xyr[j] = _xy[j]-xyorb[j];
		}
	}
	double tsq = _tsqrt*_tsqrt;
	*D = 1.0/tsq+hypotsq(Theta[0], Theta[1])*gamma2;
	double zo = Zobs != nullptr ? *Zobs : 0;
	*tau = z/tsq+(z-zo)*hypotsq(theta[0], theta[1])*gamma2
		+(_rz-2.0*(xyr[0]*theta[0]+xyr[1]*theta[1]))*gamma2;
}