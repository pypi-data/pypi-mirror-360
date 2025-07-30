#include <algorithm>
#include "bm_wiggler_radiation.h"
#include "power_density.h"

// files for debugging
string PDAlongZ;

#define POINTS_FOR_STEPPER 1000

PowerDensity::PowerDensity(SpectraSolver &spsolver, Trajectory *trajectory)
    : FunctionDigitizer(1), SpectraSolver(spsolver)
{
#ifdef _DEBUG
//PDAlongZ  = "..\\debug\\pd_alongz.dat";
#endif

	m_isglancing = contains(m_calctype, menu::spdens);
	m_pdarray.resize(1);

    if(m_isfar){
        m_npoints = (16<<(m_accuracy[accdisctra_]-1))+1;
        m_points_max_dz  = 5+(int)sqrt(m_K2);
        m_minimum_dz = 1.0/(double)m_points_max_dz;
    }
    else{
        m_pdtmp.resize(1);
        trajectory->GetZCoordinate(&m_zorbit);
        AllocateOrbitComponents(trajectory);
        m_ntotorbit = trajectory->GetOrbitPoints();
        for(int j = 0; j < 2; j++){
            m_Theta[j].resize(m_ntotorbit);
        }
        m_pdarray[0].resize(m_ntotorbit);
        m_pdtmp[0].resize(2*POINTS_FOR_STEPPER);
        m_R.resize(m_ntotorbit);
        m_accsq.resize(m_ntotorbit);
        m_acctheta.resize(m_ntotorbit);
        m_xyz[2] = m_conf[slit_dist_];
        m_Dratio = (double)(3<<(m_accuracy[acclimtra_]-1));
        m_z.resize(m_ntotorbit);
        m_ztmp.resize(2*POINTS_FOR_STEPPER);

		if(m_isglancing){
			vector<double> xy(m_ntotorbit);
            for(int j = 0; j < 2; j++){
                for (int n = 0; n < m_ntotorbit; n++){
                    xy[n] = m_orbit[n]._xy[j];
                }
                m_xyorbspline[j].SetSpline(m_ntotorbit, &m_zorbit, &xy);
            }
		}
    }
}

void PowerDensity::GetPowerDensity(double x, double y, vector<double> *pd)
{
    if(m_isfar){
        if(m_isbm){
            f_GetPowerDensityBM(y, pd);
        }
        else{
            f_GetPowerDensityFar(x, y, pd);
        }
    }
    else{
        f_GetPowerDensityNear(x, y, pd);
    }
}

void PowerDensity::AllocateOrbitComponents(Trajectory *trajectory)
{
    trajectory->GetTrajectory(&m_orbit);
}

void PowerDensity::SetObserverPositionAngle(vector<double> &XYZ, vector<double> &exyz)
{
	m_xyz[2] = XYZ[2];
	m_exyz[2] = exyz[2];
	for(int j = 0; j < 2; j++){
        m_center[j] = XYZ[j];
		m_exyz[j] = exyz[j];
	}
}

//---------- private functions ----------
void PowerDensity::f_GetPowerDensityNear(double x, double y, vector<double> *pd)
{
    int n, k, nstep = 0, ndata, n1, n2;
    double Theta[2], acc[2], R, acctheta, accsq, fRDP, Thetasq, Dinvmax = 0.0;
    double D, tau1 = 0, tau2 = 0, Dav, dzmin;

    m_xyz[0] = x;
    m_xyz[1] = y;
    dzmin = m_zorbit[1]-m_zorbit[0];
    for(n = 0; n < m_ntotorbit; n++){
        m_orbit[n].GetRelativeCoordinate(m_zorbit[n], m_gamma2, m_xyz, &tau2, Theta, &D, &m_R[n]);
        if(n == 0){
            tau1 = tau2;
        }
        for(int j = 0; j < 2; j++){
            m_Theta[j][n] = Theta[j];
            acc[j] = m_orbit[n]._acc[j];
        }
        m_acctheta[n] = (acc[0]*Theta[0]+acc[1]*Theta[1]);
        m_accsq[n] = hypotsq(acc[0], acc[1]);
        Dinvmax = max(Dinvmax, 1.0/D);
        if(n > 1){
            dzmin = min(dzmin, m_zorbit[n]-m_zorbit[n-1]);
        }
    }
    dzmin *= 1.0e-4;
    Dav = (tau2-tau1)/(m_zorbit[m_ntotorbit-1]-m_zorbit[0]);
    for(int j = 0; j < 2; j++){
        m_Thetaspline[j].SetSpline(m_ntotorbit, &m_zorbit, &m_Theta[j]);
    }
    m_accsqspline.SetSpline(m_ntotorbit, &m_zorbit, &m_accsq);
    m_accthetaspline.SetSpline(m_ntotorbit, &m_zorbit, &m_acctheta);
    m_Rspline.SetSpline(m_ntotorbit, &m_zorbit, &m_R);

    for(n = 0; n < m_ntotorbit; n++){
        D = 1.0+m_gamma2*hypotsq(m_Theta[0][n], m_Theta[1][n]);
        if(D > Dav*m_Dratio){
            continue;
        }
        Thetasq = hypotsq(m_Theta[0][n], m_Theta[1][n]);
        R = m_Rspline.GetXYItem(n, false);
        acctheta = m_accthetaspline.GetXYItem(n, false);
        accsq = m_accsqspline.GetXYItem(n, false);
        fRDP = (4.0*(Thetasq/R/R-m_gamma2*acctheta*acctheta)+D*D*accsq)/R/R;
		m_z[nstep] = m_zorbit[n];
        m_pdarray[0][nstep] = fRDP/pow(D, 5.0);
		if(m_isglancing){
            m_pdarray[0][nstep] *= f_GetGlancingAngle(m_z[nstep]);
		}
        nstep++;
    }

	double xrange[NumberFStepXrange];
	double eps[2] = {0.1, 0};

	xrange[FstepDx] = 0.0;
	xrange[FstepXlim] = dzmin;
    (*pd)[0] = 0.0;
    n1 = 0;
    do{
        n2 = n1+POINTS_FOR_STEPPER;
        if(n2 > nstep-POINTS_FOR_STEPPER/2){
            n2 = nstep-1;
        }
        ndata = n2-n1+1;
        for(k = n1; k <= n2; k++){
            m_ztmp[k-n1] = m_z[k];
            m_pdtmp[0][k-n1] = m_pdarray[0][k];
        }
		xrange[FstepXini] = xrange[FstepXref] = m_ztmp[0];
		xrange[FstepXfin] = m_ztmp[ndata-1];

		ndata = RunDigitizer(
				FUNC_DIGIT_BASE|FUNC_DIGIT_XINI_ALLOC|FUNC_DIGIT_YINI_ALLOC,
				&m_ztmp, &m_pdtmp, xrange, ndata, eps, nullptr, 0, PDAlongZ);
        if(ndata < 3){
            (*pd)[0] += 0.5*(m_ztmp[1]-m_ztmp[0])*(m_pdtmp[0][0]+m_pdtmp[0][1]);
        }
        else{
            m_splpd.SetSpline(ndata, &m_ztmp, &m_pdtmp[0]);
            (*pd)[0] += m_splpd.Integrate();
        }

        n1 = n2;
    }while(n2 < nstep-1);

}

void PowerDensity::f_GetPowerDensityFar(double x, double y, vector<double> *pd)
{
    double zini, zfin, zlim, dz, zr, Dav, D;
    int nstep;
    bool isend;

    x *= m_conv2gt;
    y *= m_conv2gt;

    zini = 0.0;
    zfin = m_lu;
    zlim = (zfin-zini)*1e-4;
    m_xyz[0] = x;
    m_xyz[1] = y;
    Dav = 1.0+m_K2+x*x+y*y;

    if(m_z.size() <= m_points_max_dz*m_npoints){
        m_z.resize(m_points_max_dz*m_npoints);
        m_pdarray[0].resize(m_points_max_dz*m_npoints);
    }
    dz = (zfin-zini)/(double)(m_npoints-1);

	double xrange[NumberFStepXrange] = {0.0, zini, zfin, zini, zlim};
	double eps[2] = {0.05, 0};
    (*pd)[0] = 0.0;
    for(int m = 0; m <= (m_issrc2?1:0); m++){
        m_segidx = m;
        zr = zini;
        int n = 0;
        isend = false;
        do{
            if(zr >= zfin-m_minimum_dz*dz*0.1){
                zr = zfin;
                isend = true;
            }
            m_z[n] = zr;
            GetIdealOrbit(zr, &m_orbittmp, m > 0);
            m_pdarray[0][n] = m_orbittmp.GetPDFunc4FarField(m_xyz, &D);
            zr += max(D/Dav, m_minimum_dz)*dz;
            n++;
        }while(!isend);

		nstep = RunDigitizer(
				FUNC_DIGIT_BASE|FUNC_DIGIT_XINI_ALLOC|FUNC_DIGIT_YINI_ALLOC,
				&m_z, &m_pdarray, xrange, n, eps, nullptr, 0, PDAlongZ);

        if(nstep < 3){
            (*pd)[0] += 0.5*(m_z[1]-m_z[0])*(m_pdarray[0][0]+m_pdarray[0][1]);
        }
        else{
            m_splpd.SetSpline(nstep, &m_z, &m_pdarray[0]);
            (*pd)[0] += m_splpd.Integrate();
        }
    }
}

void PowerDensity::f_GetPowerDensityBM(double y, vector<double> *pd)
{
    y *= m_conv2gt;
    BMWigglerRadiation::BMPowerDensity(y, pd);
}

double PowerDensity::Function4Digitizer(double z, vector<double> *y)
{
    double D, fRDP, accsq, acctheta, R, Thetasq;

    if(m_isfar){
        GetIdealOrbit(z, &m_orbittmp, m_segidx > 0);
        (*y)[0] = m_orbittmp.GetPDFunc4FarField(m_xyz, &D);
    }
    else {
        Thetasq = hypotsq(m_Thetaspline[0].GetValue(z), m_Thetaspline[1].GetValue(z));
        D = 1.0+m_gamma2*Thetasq;
        R = m_Rspline.GetValue(z);
        acctheta = m_accthetaspline.GetValue(z);
        accsq = m_accsqspline.GetValue(z);
        fRDP = (4.0*(Thetasq/R/R-m_gamma2*acctheta*acctheta)+D*D*accsq)/R/R;
        (*y)[0] =fRDP/pow(D, 5.0);

		if(m_isglancing){
			(*y)[0] *= f_GetGlancingAngle(z);
		}
    }
    return (*y)[0];
}


double PowerDensity::f_GetGlancingAngle(double z)
{
	double Dz = 0.0;
	double Zz = m_xyz[2]-z;
	double A = sqrt(hypotsq(m_exyz[0]*m_Ediv[0], m_exyz[1]*m_Ediv[1]));
	double Iz;
	bool singlep = m_accb[zeroemitt_] || m_ismap3d;

	if(fabs(Zz) < INFINITESIMAL){
		return 0.0;
	}

    double xy[3];

	for(int j = 0; j < 2; j++){
		double xye = m_xyorbspline[j].GetValue(z, true);
        int zfix = max(1, min(m_ntotorbit-2, SearchIndex(m_ntotorbit, true, m_zorbit, z)));
        for(int i = 0; i < 3; i++){
            xy[i] = m_orbit[zfix+i-1]._xy[j];
        }
        xye = lagrange(z, m_zorbit[zfix-1], m_zorbit[zfix], m_zorbit[zfix+1], xy[0], xy[1], xy[2]);

		double at = (m_xyz[j]-xye)/Zz;
		if(m_Esize[j] > INFINITESIMAL && (!singlep)){
			at += -m_Ealpha[j]/m_Esize[j]/m_Esize[j]*(m_center[j]-m_xyz[j]);
		}
		if(fabs(at) > 1.0){ // angle should be much less than 1
			return 0.0;
		}
		Dz += at*m_exyz[j];
	}
	Dz += m_exyz[2];
    if(Dz < 0){
        return 0.0;
    }
	if(A < INFINITESIMAL || singlep){
		return Dz;
	}
	Dz /= SQRT2*A;

	Iz = SQRTPI*Dz*(1.0-errf(-Dz));
	if(Dz*Dz < MAXIMUM_EXPONENT){
		Iz += exp(-Dz*Dz);
	}
	Iz *= A/SQRTPI2;

	return Iz;
}