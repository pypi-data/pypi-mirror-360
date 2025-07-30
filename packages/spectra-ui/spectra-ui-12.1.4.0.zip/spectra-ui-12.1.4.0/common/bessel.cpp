#include <stdlib.h>
#include <math.h>
#include "bessel.h"

Bessel::Bessel()
{
	m_jn.resize(2);
}

//! Input an argument (x) for integer-order Bessel functions. The constructor
//! automatically determines the maxium order, above which Jn(x) are less than 10^-8,
//! and computes all Bessel functions recursively up to the maximum order. The
//! results are stored in a private member.
//! @param n; Argument of the integer-order Bessel function
Bessel::Bessel(double x)
{
	SetArgument(x);
}

#define HUGEBES 1.0e+30

void Bessel::SetArgument(double x)
{
	double ax, rx, rsum;
	int n, nn;

	ax = fabs(x);

	if(ax < MIN_BESSEL_VALUE){
		m_jmax = 1;
		m_jn[1] = 0.0;
		m_jn[0] = 1.0;
		return;
	}

	m_jmax = (int)ceil(7.74145+0.97411*ax+2.63384*pow(ax, 0.48891));

	if(m_jmax%2) m_jmax++;
	if(m_jn.size() < m_jmax+1){
		m_jn.resize(m_jmax+1);
	}

	rx = 2.0/ax;
	m_jn[m_jmax] = rsum = 0.0;
	m_jn[m_jmax-1] = 1.0;
	for(n = m_jmax-1; n > 0; n--){
		m_jn[n-1] = n*rx*m_jn[n]-m_jn[n+1];
		if(fabs(m_jn[n-1]) > HUGEBES){
			for(nn = n-1; nn <= m_jmax-1; nn++){
				m_jn[nn] /= HUGEBES;
			}
		}
	}
	for(n = 2; n <= m_jmax; n+= 2){
		rsum += m_jn[n];
	}
	rsum = 2*rsum+m_jn[0];
	for(n = 0; n <= m_jmax; n++){
		m_jn[n] /= (x < 0.0 && n%2) ? -rsum : rsum;
	}
}

#undef HUGEBES

//! Computes an integer-order Bessel function. It actually simply extract a value
//! stored in a private memaber with an adequate sign.
//! @param n; Order of the Bessel function
//! @return Jn(x); Integer-order Bessel function
double Bessel::Jn(int n)
{
	int na = abs(n);
	if(na > m_jmax) return 0.0;
	return n < 0 ? (na%2 ? -m_jn[na] : m_jn[na]) : m_jn[na];
}

/// 1st-order Bessel function
double Bessel::J1(double x)
{
	double ax, z, xx, y, ans, ans1, ans2;

	if((ax=fabs(x)) < 8.0){
		y=x*x;
		ans1=x*(72362614232.0+y*(-7895059235.0+y*(242396853.1
				+y*(-2972611.439+y*(15704.48260+y*(-30.16036606))))));
		ans2=144725228442.0+y*(2300535178.0+y*(18583304.74
				+y*(99447.43394+y*(376.9991397+y*1.0))));
		ans=ans1/ans2;
	}
	else {
		z=8.0/ax;
		y=z*z;
		xx=ax-2.356194491;
		ans1=1.0+y*(0.183105e-2+y*(-0.3516396496e-4
				+y*(0.2457520174e-5+y*(-0.240337019e-6))));
		ans2=0.04687499995+y*(-0.2002690873e-3
				+y*(0.8449199096e-5+y*(-0.88228987e-6
				+y*0.105787412e-6)));
		ans=sqrt(0.636619772/ax)*(cos(xx)*ans1-z*sin(xx)*ans2);
		if (x < 0.0) ans = -ans;
	}
	return ans;
}

/// 0th-order Bessel function
double Bessel::J0(double x)
{
	double ax, z, xx, y, ans, ans1, ans2;

	if((ax=fabs(x)) < 8.0){
		y=x*x;
		ans1=57568490574.0+y*(-13362590354.0+y*(651619640.7
			+y*(-11214424.18+y*(77392.33017+y*(-184.9052456)))));
		ans2=57568490411.0+y*(1029532985.0+y*(9494680.718
			+y*(59272.64853+y*(267.8532712+y*1.0))));
		ans=ans1/ans2;
	}
	else{
		z=8.0/ax;
		y=z*z;
		xx=ax-0.785398164;
		ans1=1.0+y*(-0.1098628627e-2+y*(0.2734510407e-4
				+y*(-0.2073370639e-5+y*0.2093887211e-6)));
		ans2 = -0.1562499995e-1+y*(0.1430488765e-3
				+y*(-0.6911147651e-5+y*(0.7621095161e-6
				-y*0.934935152e-7)));
		ans=sqrt(0.636619772/ax)*(cos(xx)*ans1-z*sin(xx)*ans2);
	}
	return ans;
}


#define UMIN 0.001
#define UMAX 20.0
#define POLYORDER 9

double Bessel::IK53_u(double u)
	// u*int K_5/3
{
	double f5cn[POLYORDER+1] = 
		{-0.4285698554,-0.6847872650,-0.4773500067,-0.1596000544,-0.04042691030,
		-0.007689177948,-0.001054080080,-9.730028418E-05,-5.366663830E-06,-1.327666475E-07};
	double f5cp[POLYORDER+1] = 
		{-0.4285960215,-0.6851417530,-0.4784594193,-0.1620666148,-0.04127900131,
		-0.009669798543,-6.726607357E-04,-4.795528779E-04,4.850955940E-05,-1.241293618E-05};

	double pcoef= 1.0/3.0, f = 0.0, uln, uu;

	if(u <= 0){
		return 0;
	}
	if(u <= UMIN){
		uln = log(UMIN);
	}
	else if(u >= UMAX){
		uln = log(UMAX);
	}
	else{
		uln = log(u);
	}

	f = 0;
	uu = 1.0;
	for(int n = 0; n <= POLYORDER; n++){
		if(uln <0){
			f += f5cn[n]*uu;
		}
		else{
			f += f5cp[n]*uu;
		}
		uu *= uln;
	}


	f = exp(f);
	if(u <= UMIN){
		f *= pow(u/UMIN, pcoef);
	}
	else if(u >= UMAX){
		f *= exp(-(u-UMAX));
	}
	return f;
}

double Bessel::K23_u(double u)
	//	u*K_2/3
{
	double pcoef = 1.0/3.0, f = 0.0, uln;
	double f2cn[POLYORDER+1] = 
		{-0.7042293377,-0.5529369378,-0.4827112345,-0.1655252102,-0.03960070931,
		-0.006868543480,-8.589978687E-04,-7.369116283E-05,-3.864029526E-06,-9.266861469E-08};
	double f2cp[POLYORDER+1] = 
		{-0.7042582060,-0.5533399544,-0.4840564900,-0.1685632199,-0.04102706807,
		-0.009398224914,-5.779531477E-04,-5.460245481E-04,6.094444892E-05,-1.323164791E-05};

	if(u <= 0){
		return 0;
	}
	if(u <= UMIN){
		uln = log(UMIN);
	}
	else if(u >= UMAX){
		uln = log(UMAX);
	}
	else{
		uln = log(u);
	}

	if(uln < 0){
		f = ((((((((f2cn[9]
			*uln+f2cn[8])
			*uln+f2cn[7])
			*uln+f2cn[6])
			*uln+f2cn[5])
			*uln+f2cn[4])
			*uln+f2cn[3])
			*uln+f2cn[2])
			*uln+f2cn[1])
			*uln+f2cn[0];
	}
	else{
		f = ((((((((f2cp[9]
			*uln+f2cp[8])
			*uln+f2cp[7])
			*uln+f2cp[6])
			*uln+f2cp[5])
			*uln+f2cp[4])
			*uln+f2cp[3])
			*uln+f2cp[2])
			*uln+f2cp[1])
			*uln+f2cp[0];
	}


	f = exp(f);
	if(u <= UMIN){
		f *= pow(u/UMIN, pcoef);
	}
	else if(u >= UMAX){
		f *= exp(-(u-UMAX));
	}
	return f;
}

double Bessel::K13_u(double u)
	//	u*K_1/3
{
	double pcoef = 2.0/3.0, f = 0.0, uln;
	double f1cn[POLYORDER+1] = 
		{-0.8245261262,-0.4608026189,-0.5106020245,-0.1631012259,-0.03941756858,
		-0.007202867932,-9.585298174E-04,-8.674116809E-05,-4.726123162E-06,-1.161104862E-07};
	double f1cp[POLYORDER+1] = 
		{-0.8245533201,-0.4611773687,-0.5118133646,-0.1658444642,-0.04053043907,
		-0.009498539839,-6.081220822E-04,-5.330526091E-04,5.911019255E-05,-1.313411721E-05};

	if(u <= 0){
		return 0;
	}
	if(u <= UMIN){
		uln = log(UMIN);
	}
	else if(u >= UMAX){
		uln = log(UMAX);
	}
	else{
		uln = log(u);
	}

	if(uln < 0){
		f = ((((((((f1cn[9]
			*uln+f1cn[8])
			*uln+f1cn[7])
			*uln+f1cn[6])
			*uln+f1cn[5])
			*uln+f1cn[4])
			*uln+f1cn[3])
			*uln+f1cn[2])
			*uln+f1cn[1])
			*uln+f1cn[0];
	}
	else{
		f = ((((((((f1cp[9]
			*uln+f1cp[8])
			*uln+f1cp[7])
			*uln+f1cp[6])
			*uln+f1cp[5])
			*uln+f1cp[4])
			*uln+f1cp[3])
			*uln+f1cp[2])
			*uln+f1cp[1])
			*uln+f1cp[0];
	}
	f = exp(f);

	if(u <= UMIN){
		f *= pow(u/UMIN, pcoef);
	}
	else if(u >= UMAX){
		f *= exp(-(u-UMAX));
	}
	return f;
}

#undef UMIN
#undef UMAX

#define AIUMIN -3.33
#define AIPUMIN -4.0

double Bessel::Ai(double u)
{
	double aic[POLYORDER+1] = 
		{0.3550142910, - 0.2593488506, - 0.004511874805, 0.04313192105,	-0.05137661679, 
		-0.03212050870, -0.01896099288, -0.008703555693, -0.001772415699, -1.252968876E-4};
	if(u > 0){
		double xsq = 2.0*pow(u, 1.5)/3.0;
		return sqrt(3.0)/PI2/u*K13_u(xsq);
	}
	else if(u < AIUMIN){
		double xa = sqrt(-u);
		return sin(xa*xa*xa*2.0/3.0+PI/4.0)/SQRTPI/sqrt(xa);
	}
	double uu = 1.0, f = 0;
	for(int n = 0; n <= POLYORDER; n++){
		f += aic[n]*uu;
		uu *= u;
	}
	return f;
}

double Bessel::AiP(double u)
{
	double aipc[POLYORDER+1] = 
		{-0.2591209961, -0.009146110905, 0.1163753548, -0.2547473412, -0.2384228356, 
		-0.1785805588, -0.09155182869, -0.02240135555, -0.002290430350, -6.680892237E-5};
	if(u > 0){
		double xsq = 2.0*pow(u, 1.5)/3.0;
		return -sqrt(3.0)/PI2/sqrt(u)*K23_u(xsq);
	}
	else if(u < AIPUMIN){
		double xq = pow(-u, 0.75);
		double xa = xq*xq*2.0/3.0+PI/4.0;
		return -(xq*cos(xa)-sin(xa)/xq/4.0)/sqrt(-PI*u);
	}
	double uu = 1.0, f = 0;
	for(int n = 0; n <= POLYORDER; n++){
		f += aipc[n]*uu;
		uu *= u;
	}
	return f;
}

#undef POLYORDER
#undef AIPUMIN
#undef AIUMIN

#define J1SinAmpitude 0.5819
#define J1SinArgument 0.8537

double Bessel::J1inv(double x)
{
	if(x < -J1SinAmpitude){
		x = -PId2/J1SinArgument;
	}
	else if(x > J1SinAmpitude){
		x = PId2/J1SinArgument;
	}
	else{
		x= asin(x/J1SinAmpitude)/J1SinArgument;
	}
	return x;
}

#undef J1SinAmpitude
#undef J1SinArgument
