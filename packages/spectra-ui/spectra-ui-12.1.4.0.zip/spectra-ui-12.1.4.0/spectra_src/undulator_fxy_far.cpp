#include <algorithm>
#include "common.h"
#include "undulator_fxy_far.h"
#include "fast_fourier_transform.h"

string IntegFxyCustom;
string SpectrumWiggArrange;

#define INITIAL_MAXIMUM_ORDER 5000

UndulatorFxyFarfield::UndulatorFxyFarfield(SpectraSolver &spconf)
	: SpectraSolver(spconf)
{
#ifdef _DEBUG
//IntegFxyCustom = "..\\debug\\fxy_integ.dat";
//SpectrumWiggArrange = "..\\debug\\wigg_approx_arrange.dat";
#endif

	InitializeQGauss(INITIAL_MAXIMUM_ORDER, 4);

	if(m_srctype == LIN_UND || m_srctype == VERTICAL_UND){
		f_Fxy = &UndulatorFxyFarfield::f_LinearFxy;
	}
	else if(m_srctype == HELICAL_UND){
		f_Fxy = &UndulatorFxyFarfield::f_HelicalFxy;
	}
	else if(m_srctype == ELLIPTIC_UND){
		f_Fxy = &UndulatorFxyFarfield::f_EllipticFxy;
	}
	else{
		f_Fxy = &UndulatorFxyFarfield::f_CustomFxy;
	}
	m_nfft = 0;
	m_fft = nullptr;
	m_data = nullptr;
}

#undef INITIAL_MAXIMUM_ORDER

UndulatorFxyFarfield::~UndulatorFxyFarfield()
{
	if(m_fft != nullptr){
		delete m_fft;
		delete[] m_data;
	}
}

void UndulatorFxyFarfield::SetCondition(int nh, double gt)
{
	m_nh = nh;
	m_gt = gt;
	m_gt2 = gt*gt;
	m_gsi = (double)nh/(1.0+m_K2+m_gt2);
	if(m_srctype == LIN_UND || m_srctype == ELLIPTIC_UND){
		m_z = (m_Kxy[1][1]*m_Kxy[1][1]-m_Kxy[0][1]*m_Kxy[0][1])*m_gsi/4.0;
		m_bjz.SetArgument(m_z);
	}
	else if(m_srctype == VERTICAL_UND){
		m_z = m_Kxy[0][1]*m_Kxy[0][1]*m_gsi/4.0;
		m_bjz.SetArgument(m_z);
	}
}


void UndulatorFxyFarfield::SetObservation4Wiggler(int nhmax, double gtxy[])
{
	nhmax = max(10, nhmax);
	int npoints = 16*(nhmax+1)*m_accuracy[accdisctra_]+1;
	vector<double> phiarr[2], fxy[4];
	double dz = m_lu/(npoints-1), D, z;
	OrbitComponents orbit;

	phiarr[0].resize(npoints);
	for(int j = 0; j < 2; j++){
		fxy[j].resize(npoints);
		m_gtxy[j] = gtxy[j];
	}
	if(m_issrc2){
		phiarr[1].resize(npoints);
		for (int j = 2; j < 4; j++){
			fxy[j].resize(npoints);
		}
	}
	m_gt2 = hypotsq(m_gtxy[0], m_gtxy[1]);
	for(int n = 0; n < npoints; n++){
		z = dz*n;
		for(int i = 0; i < (m_issrc2?2:1); i++){
			GetIdealOrbit(z, &orbit, i>0);
			phiarr[i][n] = orbit.GetPsi4FarField(z, m_gtxy, m_gt2, m_K2)/m_lu;
			D = PI*(1.0+hypotsq(m_gtxy[0]-orbit._beta[0], m_gtxy[1]-orbit._beta[1]));
			for(int j = 0; j < 2; j++){
				fxy[j+2*i][n] = (orbit._beta[j]-m_gtxy[j])/D;
			}
		}
	}
	Spline spltmp[4];
	for(int i = 0; i < (m_issrc2?2:1); i++){
		for (int j = 0; j < 2; j++){
			spltmp[j+2*i].SetSpline(npoints, &phiarr[i], &fxy[j+2*i]);
		}
	}

	int nfft = fft_number(npoints, 3+m_accuracy[accdisctra_]);
	if(nfft > m_nfft){
		if(m_fft != nullptr){
			delete m_fft;
			delete[] m_data;
		}
		m_nfft = nfft;
		m_fft = new FastFourierTransform(1, m_nfft);
		m_data = new double[m_nfft];
	}

	vector<double> dnh(nhmax+2), fdnh[8], s(4);
	double ftmp[4];
	for(int j = 0; j < (m_issrc2?8:4); j++){
		fdnh[j].resize(nhmax+2, 0.0);
	}

	double dphi = PI2/m_nfft;
	for(int i = 0; i < (m_issrc2?2:1); i++){
		for (int j = 0; j < 2; j++){
			for (int n = 0; n < m_nfft; n++){
				m_data[n] = spltmp[j+2*i].GetValue(dphi*n+phiarr[i][0])*dphi;
			}
			m_fft->DoRealFFT(m_data);
			for (int n = 1; n <= nhmax+1; n++){
				if(hypotsq(m_data[2*n], m_data[2*n+1]) < 1e-18){
					continue;
				}
				fdnh[2*j+4*i][n] += n*m_data[2*n];
				fdnh[2*j+1+4*i][n] += n*m_data[2*n+1];
			}
		}
	}

	for (int n = 1; n <= nhmax+1; n++){
		dnh[n] = n;
		for (int i = 0; i < (m_issrc2?2:1); i++){
			for (int j = 0; j < 4; j++){
				ftmp[j] = fdnh[j+4*i][n];
			}
			stokes(ftmp, ftmp+2, &s);
			for (int j = 0; j < 4; j++){
				fdnh[j+4*i][n] = s[j];
			}
		}
		if(m_issrc2){
			for (int j = 0; j < 4; j++){
				fdnh[j][n] += fdnh[j+4][n];
			}
		}
	}

	for(int j = 0; j < 4; j++){
		m_splfxy[j].Initialize(&dnh, &fdnh[j], true);
	}

#ifdef _DEBUG
    if(!SpectrumWiggArrange.empty()){
        ofstream debug_out(SpectrumWiggArrange);
        vector<double> items(9), fxyid(12);
		double phi = m_gt2 > 0 ? atan2(gtxy[1], gtxy[0]) : 0;
		for (int nh = 1; nh <= nhmax+1; nh++){
			SetCondition(nh, sqrt(m_gt2));
			GetFxy(phi, &fxyid);
            items[0] = nh;
            for(int j = 0; j < 4; j++){
                items[j+1] = fdnh[j][nh];
            }
            for(int j = 0; j < 4; j++){
                items[j+5] = fxyid[j];
            }
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif
}

void UndulatorFxyFarfield::GetFlux4Wiggler(double nh, vector<double> *fhvc)
{
	for(int j = 0; j < 4; j++){
		(*fhvc)[j] = m_splfxy[j].GetValue(nh);
	}
}

void UndulatorFxyFarfield::GetFxy(double phi, vector<double> *fxy, bool isamp)
{
	double fx[2][2], fy[2][2];

	(this->*f_Fxy)(phi, fx[0], fy[0], false);
	if(m_issegu&&m_issrc2){
		(this->*f_Fxy)(phi, fx[1], fy[1], true);
	}

	if(isamp){
		(*fxy)[0] = fx[0][0];
		(*fxy)[1] = fx[0][1];
		(*fxy)[2] = fy[0][0];
		(*fxy)[3] = fy[0][1];
	}
	else if(m_issegu&&m_issrc2){
		(*fxy)[0] = hypotsq(fx[0][0], fx[0][1])+hypotsq(fx[1][0], fx[1][1]);
		(*fxy)[1] = hypotsq(fy[0][0], fy[0][1])+hypotsq(fy[1][0], fy[1][1]);
		(*fxy)[2] = 2.0*(fx[0][1]*fy[0][0]-fx[0][0]*fy[0][1]+fx[1][1]*fy[1][0]-fx[1][0]*fy[1][1]);
		(*fxy)[3] = 2.0*(fx[0][0]*fy[0][0]+fx[0][1]*fy[0][1]+fx[1][0]*fy[1][0]+fx[1][1]*fy[1][1]);
		(*fxy)[4] = 2.0*(fx[0][0]*fx[1][0]+fx[0][1]*fx[1][1]);
		(*fxy)[5] = 2.0*(fy[0][0]*fy[1][0]+fy[0][1]*fy[1][1]);
		(*fxy)[6] = 2.0*(fx[0][1]*fx[1][0]-fx[0][0]*fx[1][1]);
		(*fxy)[7] = 2.0*(fy[0][1]*fy[1][0]-fy[0][0]*fy[1][1]);
		(*fxy)[8] = 2.0*(fx[1][0]*fy[0][0]+fx[1][1]*fy[0][1]+fx[0][0]*fy[1][0]+fx[0][1]*fy[1][1]);
		(*fxy)[9] = 2.0*(fx[1][1]*fy[0][0]-fx[1][0]*fy[0][1]+fx[0][1]*fy[1][0]-fx[0][0]*fy[1][1]);
		(*fxy)[10] = 2.0*(fx[0][0]*fy[1][0]+fx[0][1]*fy[1][1]-fx[1][0]*fy[0][0]-fx[1][1]*fy[0][1]);
		(*fxy)[11] = 2.0*(fx[0][1]*fy[1][0]-fx[0][0]*fy[1][1]-fx[1][1]*fy[0][0]+fx[1][0]*fy[0][1]);
	}
	else{
		stokes(fx[0], fy[0], fxy);
	}
}

// private functions
void UndulatorFxyFarfield::f_LinearFxy(double phi, double *fx, double *fy, bool issec)
{
	double bjx, dnh;
	double bjz1, bjz2;
	double u, v, x;
	double s1, s2, ds1, ds2, ds1a, fds;
	double ssum, dssum, K;
	double *fx0, *fy0;
	int ia, ib, naa, nbb, ncc, nn, n2, m;
	vector<double> *kxy = issec ? m_KxyS : m_Kxy;
	bool isvertical = fabs(kxy[0][1]) > fabs(kxy[1][1]);

	if(isvertical){
		K = kxy[0][1];
		phi += PId2;
		fy0 = fx; fx0 = fy;
	}
	else{
		K = kxy[1][1];
		fx0 = fx; fy0 = fy;
	}
	dnh = (double)m_nh;
	u = cos(phi);
	v = sin(phi);
	x = 2.0*m_gt*K*m_gsi*u;
	m_bjx.SetArgument(x);

	if(fabs(x) > MAX_ARG_BES_NEG){
		// X != 0 
		if(m_nh%2){
			s1 = INFINITESIMAL;
			s2 = INFINITESIMAL;
			ssum = INFINITESIMAL;
			ds1a = s1;
			m = 1;
			do{
				ia = (2*m-1-m_nh)/2;
				ib = (-2*m+1-m_nh)/2;
				bjz1 = m_bjz.Jn(ia);
				bjz2 = m_bjz.Jn(ib);
				nn = 2*m-1;
				bjx = m_bjx.Jn(nn);
				ds1 = bjx*(bjz1-bjz2);
				ds2 = bjx*((double)ia*bjz1-(double)ib*bjz2);
				s1 += ds1;
				s2 += ds2;

				dssum = fabs(bjx)+fabs(bjz1)+fabs(bjz2);
				ssum += fabs(dssum);
				fds = (dssum+ds1a)/ssum;
				ds1a = dssum;

				fds = max(fds, max(fabs(ds1/(s1+INFINITESIMAL)), fabs(ds2/(s2+INFINITESIMAL))));
				m++;
			}while(fds > BESSUM_EPS);
		}
		else{
			n2 = m_nh/2;
			s1 = m_bjx.Jn(0)*m_bjz.Jn(-n2);
			ssum = fabs(s1)+INFINITESIMAL;
			s2 = -(double)n2*s1;
			if(fabs(s1) < INFINITESIMAL) s1 = INFINITESIMAL;
			ds1a = s1;
			m = 1;
			do{
				ia = -n2+m;
				ib = -n2-m;
				nn = 2*m;
				bjx = m_bjx.Jn(nn);
				bjz1 = m_bjz.Jn(ia);
				bjz2 = m_bjz.Jn(ib);
				ds1 = bjx*(bjz1+bjz2);
				ds2 = bjx*((double)ia*bjz1+(double)ib*bjz2);
				s1 += ds1;
				s2 += ds2;

				dssum = fabs(bjx)+fabs(bjz1)+fabs(bjz2);
				ssum += fabs(dssum);
				fds = (dssum+ds1a)/ssum;
				ds1a = dssum;

				fds = max(fds, max(fabs(ds1/(s1+INFINITESIMAL)), fabs(ds2/(s2+INFINITESIMAL))));
				m++;

			}while(fds > BESSUM_EPS);
		}

		fx0[0] = -(dnh*s1+2.0*s2)/m_gt/u+2.0*m_gt*m_gsi*s1*u;
		fy0[0] = 2.0*s1*m_gt*v*m_gsi;
		fx0[1] = 0.0;
		fy0[1] = 0.0;
	}
	else{
		// X ~= 0 
		if(m_nh%2){
			naa = (-m_nh-1)/2;
			nbb = (-m_nh+1)/2;
			s1 = m_bjx.Jn(1)*(m_bjz.Jn(nbb)-m_bjz.Jn(naa));
			s2 = m_bjz.Jn(naa)+m_bjz.Jn(nbb);
		}
		else{
			naa = (-m_nh-2)/2;
			nbb = (-m_nh+2)/2;
			ncc = -m_nh/2;
			s1 = m_bjz.Jn(ncc);
			s2 = m_bjx.Jn(1)*(m_bjz.Jn(nbb)-m_bjz.Jn(naa));
		}
		if(fabs(m_z) < MAX_ARG_BES_NEG){
			if(m_nh > 2){
				s1 += m_bjx.Jn(m_nh);
				s2 += m_bjx.Jn(m_nh+1)+m_bjx.Jn(m_nh-1);
			}
			else if(m_nh == 2){
				s1 += m_bjx.Jn(m_nh);
			}
		}
		fx0[0] = m_gsi*(2.0*s1*m_gt*u-K*s2);
		fy0[0] = 2.0*m_gsi*s1*m_gt*v;
		fx0[1] = 0.0;
		fy0[1] = 0.0;
	}
}

void UndulatorFxyFarfield::f_HelicalFxy(double phi, double *fx, double *fy, bool issec)
{
	double tefx[2], tefy[2];
	double x, uk;
	int nh1, nh2, ih1, ih2,ih;
	double u, v, aj0, aj0x, ajm, ajp, fq, signx, signy, cs, sn, dummy;
	vector<double> *kxy = issec ? m_KxyS : m_Kxy;

	signx = kxy[0][1] < 0.0 ? -1.0 : 1.0;
	signy = kxy[1][1] < 0.0 ? -1.0 : 1.0;

	uk = fabs(kxy[0][1]);
	x = 2.0*m_gt*uk*m_gsi;
	nh1=m_nh-1;
	nh2=m_nh+1;

	m_bjx.SetArgument(x);
	if (x > MAX_ARG_BES_APPROX){
		ajm = m_bjx.Jn(nh1);
		ajp = m_bjx.Jn(nh2);
	}
	else{
		if (nh1 == 0){
			ajm=1.0;
		}
		else{
			ajm = x/pow(2.0, (double)nh1);
			ih1 = nh1;
			while(ih1 > 1){
			   ajm *= x/(double)ih1;
			   ih1--;
			};
		}
		ajp = x/pow(2.0, (double)nh2);
		ih2 = nh2;
		while(ih2 > 1){
			ajp *= x/(double)ih2;
			ih2--;
		};
	}
	u=cos(phi);
	v=sin(phi) ;

	tefy[0] = 0.0;
	tefx[0] = 0.0;
	tefy[1] = uk*u*(ajm-ajp);
	tefx[1] = -uk*v*(ajm-ajp);
	if (x > MAX_ARG_BES_NEG){
		aj0 = m_bjx.Jn(m_nh);
		aj0x = aj0/x;
	}
	else{
		aj0x = 1.0/pow(2.0, (double)m_nh);
		ih = m_nh;
		while(ih > 1){
			aj0x *= x/(double)ih;
			ih--;
		};
	}
	fq = 2.0*aj0x*(m_gt*x-(double)m_nh*uk);
	fx[0] = fq*u*m_gsi;
	fy[0] = fq*v*m_gsi;
	fx[1] = tefx[1]*m_gsi*signx*signy;
	fy[1] = tefy[1]*m_gsi*signx*signy;

	cs = cos(-phi*signx*signy);
	sn = sin(-phi*signx*signy);

	fx[0] = (dummy=fx[0])*cs-sn*fx[1];
	fx[1] = cs*fx[1]+dummy*sn;
	fy[0] = (dummy=fy[0])*cs-sn*fy[1];
	fy[1] = cs*fy[1]+dummy*sn;
}

void UndulatorFxyFarfield::f_EllipticFxy(double phi, double *fx, double *fy, bool issec)
{
	int jq, jt, na, nb, nhh, ib, nn, n2, m, ia;
	double u, v, x, sssin, cccos, delta, bjx, fds;
	double by0, byp, bym;
	double exp_delta[3], sum[3], ds[3], ds1a, efx[3], efy[3];
	double pls[3], pmn[3], sas[4][3];
	double tmp1[3], tmp2[3], tmp3[3], tmp0;
	double bjz1, bjz2;
	double ssum, dssum;
	vector<double> *kxy = issec ? m_KxyS : m_Kxy;

	u = cos(phi);
	v = sin(phi);
	x = 2.0*m_gsi*m_gt*sqrt(hypotsq(kxy[1][1]*u, kxy[0][1]*v));
	m_bjx.SetArgument(x);
	sssin = kxy[0][1]*v;
	cccos = kxy[1][1]*u;
	delta = atan2(sssin,cccos);

	if(fabs(x) > MAX_ARG_BES_NEG){
		// X != 0
		for(jq = -1; jq <= 1; jq++){
			jt = m_nh+jq;
			if(jt%2){
				sum[1] = INFINITESIMAL;
				sum[2] = INFINITESIMAL;
				ssum = INFINITESIMAL;

				m = 1;
				ds1a = 1.0e+20;
				do{
					ia = (2*m-1-jt)/2;
					ib = (-2*m+1-jt)/2;
					nn = 2*m-1;
					exp_delta[1] = cos((double)nn*delta);
					exp_delta[2] = -sin((double)nn*delta);
					bjx = m_bjx.Jn(nn);
					bjz1 = m_bjz.Jn(ia);
					bjz2 = m_bjz.Jn(ib);
					ds[1] = bjx*exp_delta[1]*(bjz1-bjz2);
					ds[2] = bjx*exp_delta[2]*(bjz1+bjz2);
					sum[1] += ds[1];
					sum[2] += ds[2];
					dssum = fabs(bjx)+fabs(bjz1)+fabs(bjz2);
					ssum += fabs(dssum);
					fds = (dssum+ds1a)/ssum;
					ds1a = dssum;
					m++;
				}while(fds > BESSUM_EPS);
			}
			else{
				sum[1] = 0.0;
				sum[2] = 0.0;
				n2 = jt/2;
				sum[1] = m_bjx.Jn(0)*m_bjz.Jn(-n2);
				ssum = fabs(sum[1])+INFINITESIMAL;
				sum[2] = 0.0;
				if(fabs(sum[1]) < INFINITESIMAL) sum[1] = INFINITESIMAL;

				m = 1;
				ds1a = 1.0e+20;
				do{
					ia = -n2+m;
					ib = -n2-m;
					nn = 2*m;
					exp_delta[1] = cos((double)nn*delta);
					exp_delta[2] = -sin((double)nn*delta);
					bjx = m_bjx.Jn(nn);
					bjz1 = m_bjz.Jn(ia);
					bjz2 = m_bjz.Jn(ib);
					ds[1] = bjx*exp_delta[1]*(bjz1+bjz2);
					ds[2] = bjx*exp_delta[2]*(bjz1-bjz2);
					sum[1] += ds[1];
					sum[2] += ds[2];
					dssum = fabs(bjx)+fabs(bjz1)+fabs(bjz2);
					ssum += fabs(dssum);
					fds = (dssum+ds1a)/ssum;
					ds1a = dssum;
					m++;
				}while(fds > BESSUM_EPS);
			}
			sas[2+jq][1] = sum[1];
			sas[2+jq][2] = sum[2];
		}
		pls[1] = sas[3][1]+sas[1][1];
		pls[2] = sas[3][2]+sas[1][2];
		pmn[1] = sas[3][1]-sas[1][1];
		pmn[2] = sas[3][2]-sas[1][2];
		efx[1] = 2.0*sas[2][1]*m_gt*u-kxy[1][1]*pls[1];
		efx[2] = 2.0*sas[2][2]*m_gt*u-kxy[1][1]*pls[2];
		efy[1] = 2.0*sas[2][1]*m_gt*v+kxy[0][1]*pmn[2];
		efy[2] = 2.0*sas[2][2]*m_gt*v-kxy[0][1]*pmn[1];
	}
	else{
		// X ~= 0
		if(m_nh%2){
			na = (m_nh-1)/2;
			nb = (m_nh+1)/2;
			efx[1] = kxy[1][1]*(m_bjz.Jn(na)-m_bjz.Jn(nb))*(nb%2 > 0 ? -1.0 : 1.0);
			efy[2] = -kxy[0][1]*(m_bjz.Jn(na)+m_bjz.Jn(nb))*(nb%2 > 0 ? -1.0 : 1.0);
			efx[2] = 0.0;
			efy[1] = 0.0;
		}
		else{
			nhh = m_nh/2;
			by0 = m_bjz.Jn(-nhh);
			byp = m_bjz.Jn(-nhh+1);
			bym = m_bjz.Jn(-nhh-1);
			sas[2][1] = by0;
			sas[2][2] = 0.0;
			tmp1[1] = 0.0;
			tmp1[2] = by0*sin(delta)*2.0;
			tmp2[1] = bym*cos(delta);
			tmp2[2] = bym*sin(delta);
			tmp3[1] = byp*cos(delta);
			tmp3[2] = -byp*sin(delta);
			tmp0 = by0*cos(delta)*2.0;
			pls[1] = (-tmp1[1]-tmp2[1]+tmp3[1])*x/2.;
			pls[2] = (-tmp1[2]-tmp2[2]+tmp3[2])*x/2.;
			pmn[1] = (tmp0-tmp2[1]-tmp3[1])*x/2.;
			pmn[2] = (-tmp2[2]-tmp3[2])*x/2.;
			efx[1] = 2.0*sas[2][1]*m_gt*u-kxy[1][1]*pls[1];
			efx[2] = 2.0*sas[2][2]*m_gt*u-kxy[1][1]*pls[2];
			efy[1] = 2.0*sas[2][1]*m_gt*v+kxy[0][1]*pmn[2];
			efy[2] = 2.0*sas[2][2]*m_gt*v-kxy[0][1]*pmn[1];
		}
	}
	fx[0] = efx[1]*m_gsi;
	fx[1] = efx[2]*m_gsi;
	fy[0] = efy[1]*m_gsi;
	fy[1] = efy[2]*m_gsi;
}

void UndulatorFxyFarfield::f_CustomFxy(double phi, double *fx, double *fy, bool issec)
{
	vector<double> fxy(5);
	int npoints = 12*m_nh*m_accuracy[accdisctra_]+1;

	m_issec = issec;
	m_gtxy[0] = m_gt*cos(phi);
	m_gtxy[1] = m_gt*sin(phi);
	IntegrateGauss(npoints, 0.0, m_lu, &fxy, IntegFxyCustom);

	double coef = GetCoefFxy();
	fx[0] = fxy[0]*coef;
	fx[1] = fxy[1]*coef;
	fy[0] = fxy[2]*coef;
	fy[1] = fxy[3]*coef;
}

void UndulatorFxyFarfield::IntegrandGauss(double z, vector<double> *fxy)
{
    OrbitComponents orbit;
	GetIdealOrbit(z, &orbit, m_issec);

	double psi, cs, sn;
	psi =  (double)m_nh*orbit.GetPsi4FarField(z, m_gtxy, m_gt2, m_K2)/m_lu;
	cs = cos(psi);
	sn = sin(psi);
	for(int j = 0; j < 2; j++){
		double fxyr = orbit._beta[j]-m_gtxy[j];
		(*fxy)[2*j] = fxyr*cs;
		(*fxy)[2*j+1] = fxyr*sn;
	}
}

double UndulatorFxyFarfield::GetCoefFxy()
{
	return 2.0*m_gsi/m_lu;
}

