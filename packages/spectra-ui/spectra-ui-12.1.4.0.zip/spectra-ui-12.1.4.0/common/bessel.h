#ifndef bessel_h
#define bessel_h

#include <valarray>

#include "numerical_common_definitions.h"


using namespace std;

/// Bessel function utilities

//! This class provides methods to compute Bessel functions necessary for
//! SR photon flux calculation. Integer-order Bessel functions, Jn(x),
//! and 1/3-th- and 2/3-th-order modified Bessel functions are contained.
class Bessel {
public:
	/// Default Constructor
	Bessel();

	/// Constructor
	Bessel(double x);

	/// Set the argument
	void SetArgument(double x);

	/// Integer-order Bessel functions.
	double Jn(int n);

	/// 1st Bessel functions
	static double J1(double x);

	/// 0th Bessel functions
	static double J0(double x);

	/// Modified Bessel functions.
	static void Kn(double x, double *bsk1, double *bsk2);

	static double K13_u(double u);
	static double K23_u(double u);
	static double IK53_u(double u);
	static double Ai(double x);
	static double AiP(double x);

	static double J1inv(double x);

private:
	int m_jmax;
	valarray<double> m_jn;
};

#endif
