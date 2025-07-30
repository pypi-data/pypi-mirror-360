#ifndef orbit_components_operation_h
#define orbit_components_operation_h

#include <vector>
#include "numerical_common_definitions.h"

using namespace std;

class Particle;

class OrbitComponents {
public:
	OrbitComponents();
	void Clear();
	void SetComponents(double acc[], double betaxy[], double xy[], double rz);
	void SetComponents(OrbitComponents* orbit);
	void SetComponents(Particle *particle);
	void Flip();
	double GetPsi4FarField(double z, double gtxy[], double gt2, double K2);
	double GetPDFunc4FarField(double gtxy[], double *D);
	void GetRelativeCoordinateFar(double z,double gamma2, 
		double *theta, double *tau, double *Theta, double *D, 
		double *Zobs = nullptr, double *xyorb = nullptr);
	void GetRelativeCoordinate(double z, double gamma2,
		double *XYZ, double *tau, double *Theta, double *D, double *R);

	double _acc[2];
	double _beta[2];
	double _xy[2];
	double _rz;
	double _tsqrt;
};


#endif
