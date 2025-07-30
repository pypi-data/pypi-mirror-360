#include <algorithm>
#include <iomanip>
#include <limits>
#include <time.h>
#include "flux_density_conv.h"
#include "filter_operation.h"
#include "trajectory.h"
#include "function_digitizer.h"
#include "spectra_debug.h"
//#include "particle_distribution.h"

#define EPLOWLIMEPS 1.0e-4
#define TOTALITEMSSAVED 18
// 2D integration x (maxorder x 2 + 1)
#define MEMORYLIMIT 2.0e+9

FluxDensityConv::FluxDensityConv(SpectraSolver &spsolver, Trajectory *trajectory, FilterOperation *filter)
    : SpectraSolver(spsolver)
{
	m_isef_accel = m_iscoherent;
	m_isavgd = true;

	m_ntaupoints = 0;
	m_nfftmax = m_nfft = 0;
    m_fft = nullptr;
    for(int j = 0; j < 2; j++){
        m_EwFFT[j] = nullptr;
    }
    m_trajectory = trajectory;
    m_ntotorbit = trajectory->GetOrbitPoints();
	f_AllocNTauPoints(m_ntotorbit);

    m_XYZ[2] = m_conf[slit_dist_];
    f_SetupCondition(filter);

	if(m_confsel[faalog_] == ConfigWiggApLabel){
		m_trajectory->AllocateProjectedXPosision();
	}
}

FluxDensityConv::~FluxDensityConv()
{
	for(int j = 0; j < 2; j++){
		if(m_EwFFT[j] != nullptr){
			free(m_EwFFT[j]);
		}
	}
	for(int j = 0; j < m_ffts.size(); j++){
		delete m_ffts[j];
	}
}

void FluxDensityConv::GetFluxItemsAt(double *xy, vector<double> *values, bool isfar)
{
	if(isfar){
		f_SetXYAngle(xy);
	}
	else{
		f_SetXYPosition(xy);
	}
    if(m_confsel[faalog_] == ConfigWiggApLabel){
        f_AllocateFieldWiggler();
    }
    else{
        f_AllocateElectricField(m_isef_accel, m_isavgd, true, isfar);
		if(!f_SetupFTConfig()){
			throw exception("Not enough memory available for FFT.");
			return;
		}
		f_AllocateComplexFieldByFFT();
    }
    f_GetFluxItems(values);
}

int FluxDensityConv::GetEnergyArray(vector<double> *energy)
{
	*energy = m_ep;
    return m_ndata4output;
}

void FluxDensityConv::AllocateOrbitComponents()
{
    m_trajectory->GetTrajectory(&m_orbit);
}

void FluxDensityConv::GetSingleElectricField(vector<vector<double> > *Ereim)
{
    double dt, tau, tr, D3;

    f_SetXYPosition(m_center);
    f_AllocateElectricField(true, false, true);

    dt = (m_confv[trange_][1]-m_confv[trange_][0])/(m_conf[tmesh_]-1);

	int tmesh = (int)floor(m_conf[tmesh_]+0.5);
    Ereim->resize(2); 
	for(int j = 0; j < 2; j++){
		(*Ereim)[j].resize(tmesh); 
	}

	if(m_calcstatus){
		m_calcstatus->SetSubstepNumber(0, tmesh);
	}

    for(int n = 0; n < tmesh; n++){
        tr = m_confv[trange_][0]+dt*(double)(n-1);
		tr *= 1.0e-15; // fsec  -> sec
		tau  = tr*(2.0*m_gamma*m_gamma*CC);

        (*Ereim)[0][n] = tr*1.0e+15; // sec -> fsec
		if(tau < m_tau[1] || tau > m_tau[m_ntaupoints]){
			(*Ereim)[1][n] = (*Ereim)[2][n] = 0;
			continue;
		}
        D3 = m_DSpline.GetValue(tau);
        D3 *= D3*D3;
		for(int j = 0; j < 2; j++){
			(*Ereim)[j][n] = m_EtSpline[j].GetValue(tau)/D3;
		}
		if(m_calcstatus){
			m_calcstatus->PutSteps(0, n);
		}	
	}
}

//---------- private functions ----------
bool FluxDensityConv::f_SetupCondition(FilterOperation *filter)
{
    vector<double> zarray4bg;
    double epmin, epmax, defrac, eps_erange, ecr, deFT;
    int j;

    m_trajectory->GetZCoordinate(&m_zorbit);
    AllocateOrbitComponents();
    eps_erange = 1.0e-2/m_accfrac;

	double trange = 0;
	if(contains(m_calctype, menu::temporal)){
		trange = max(fabs(m_confv[trange_][0]), fabs(m_confv[trange_][1]));
		trange *= 1.0e-15; // fsec -> sec
	}

	ecr = m_trajectory->GetCriticalEnergy();

	if(m_iscoherent){
		m_isfixep = m_isfixepitem;
	}
	else{
	    m_isfixep = m_isfixepitem && (m_iszspread || m_isskipespread);
	}
    if(m_isfixep){
		m_eming = m_fixep;
        return true;
    }
    else{
		if(m_isenergy){
            epmax = max(m_confv[erange_][0], m_confv[erange_][1]);
            epmin = min(m_confv[erange_][0], m_confv[erange_][1]);
        }
		else if(m_iscoherent){
			if(contains(m_calctype, menu::temporal)){
				epmin = photon_energy(trange*CC);
			}
			else{
				epmin = 0.0;
			}
			epmax = GetMaximumEnergy4Coherent();
			if(m_isfilter){
	            if(filter->IsGeneric()){
		            epmax = min(epmax, 
						filter->GetMaxEnergyAndAllocateMethod4Power(ecr, eps_erange));
			    }
	            else{
		            filter->GetEnergyRange(&epmin, &ecr);
					epmax = min(epmax, ecr);
			    }
			}			
		}
        else if(m_ispower && m_isfilter){
            if(filter->IsGeneric()){
                epmin = 0.0;
                epmax = ecr;
                epmax = filter->GetMaxEnergyAndAllocateMethod4Power(epmax, eps_erange);
            }
            else{
                filter->GetEnergyRange(&epmin, &epmax);
            }
        }
		else if(contains(m_calctype, menu::temporal)){
			epmin = photon_energy(trange*CC);
			epmax = ecr;
		}
        else{
            epmin = epmax = m_fixep;
        }
		if(!m_isskipespread){
	        defrac = 1.0+2.0*GetEspreadRange()+1.0e-6;
		         // 1e-6: to ensure energy range
			epmax *= defrac;
			epmin /= defrac;
		}
    }
	m_eming = epmin;
    m_conv_dtau2ep = 2.0*m_gamma2*CC*PLANCK;

	if(m_isskipespread && epmin > ecr*EPLOWLIMEPS){
		deFT = ecr*1.0e-3;
	}
	else{
		double xy[2] = {0,0}, tautemp[3];
		f_SetXYPosition(xy);
		f_AllocateElectricField(m_isef_accel, true, false, false);
		f_GetZrange(m_ispower, tautemp);
		m_taurange[0] = tautemp[0];

		f_SetXYPosition(m_xyfar);
		f_AllocateElectricField(m_isef_accel, true, false, false);
		f_GetZrange(m_ispower, tautemp);
		m_taurange[1] = tautemp[1];

		m_taurange[2] = m_taurange[1]-m_taurange[0];
		double brange, Deltau = m_taurange[2];
		if(m_iscoherent){
			GetTypicalBunchLength(&brange);
			brange *= (2.0*m_gamma2*CC);
			Deltau = sqrt(hypotsq(Deltau, brange*GAUSSIAN_MAX_REGION));
		}
		deFT = m_conv_dtau2ep/(4.0*Deltau);
	}
	deFT /= m_accfrac;

	int Ns = 16*m_acclevel;
	int ndiv = 0;
	double dsize;
	do{
		ndiv++;
		m_ndata4output = 2*(int)ceil(epmax/2.0/deFT/ndiv)+1;
		m_nfftbase = 1;
		unsigned ns = m_ndata4output*Ns;
		while(m_nfftbase < ns && m_nfftbase < INT_MAX){
			m_nfftbase <<= 1;
		}
		dsize = (double)m_nfftbase*sizeof(double)*2.0;
		dsize *= 4.0*TOTALITEMSSAVED;
	} while(dsize > MEMORYLIMIT);

	if(ndiv > 1){
		return false;
	}

	m_deFT = epmax/ndiv/(double)(m_ndata4output-1);
	m_dtau = m_conv_dtau2ep/(m_nfftbase*m_deFT);
	m_ep.resize(m_ndata4output);

	for(int n = 0; n < m_ndata4output; n++){
		m_ep[n] = m_deFT*n;
	}

	for(j = 0; j < 4; j++){
        m_Fxy[j].resize(m_ndata4output);
    }

	return true;
}

bool FluxDensityConv::f_SetupFTConfig()
{
	f_GetZrange(m_ispower, m_taurange);
    unsigned nfft = m_nfftbase;
	m_fft_nskip = 1;
	while(m_taurange[2] > (double)nfft*m_dtau){
		nfft <<= 1;
		m_fft_nskip <<= 1;
		if(nfft > INT_MAX){
			return false;
		}
	}

	if(nfft > m_nfftmax){
        for(int j = 0; j < 2; j++){
            m_EwFFT[j] = (double *)realloc_chk(m_EwFFT[j], sizeof(double)*nfft);
            if(m_EwFFT[j] == nullptr){
                if(j == 1){
                    free(m_EwFFT[1]);
					m_EwFFT[0] = nullptr;
                }
                return false;
            }
        }
		m_nfftmax = nfft;
	}

	if(nfft != m_nfft){
		for(int j = 0; j < m_nffts.size(); j++){
			if(m_nffts[j] == nfft){
				m_fft = m_ffts[j];
				m_nfft = nfft;
				return true;
			}
		}
        m_fft = new FastFourierTransform(1, nfft);
		m_ffts.push_back(m_fft);
		m_nffts.push_back(nfft);
		m_nfft = nfft;
    }
	return true;
}

void FluxDensityConv::f_SetXYPosition(double *xy)
{
    m_XYZ[0] = xy[0];
    m_XYZ[1] = xy[1];
}

void FluxDensityConv::f_SetXYAngle(double *qxy)
{
    m_qxqy[0] = qxy[0];
    m_qxqy[1] = qxy[1];
}

void FluxDensityConv::f_GetZrange(bool ispower, double taurange[])
{
	double tautyp = ispower ? 0.0 : m_conv_dtau2ep/(TINY+m_eming);
	double eps, tauq, Elim;

	if(m_iscoherent){
		eps = 1.0e-3;
	}
	else{
		eps = 1.0e-10;
	}
	eps /= pow(10.0, (double)(m_acclevel-1)*0.5);
	Elim = eps*m_Etmax;

	if(m_Etmax == 0){
		taurange[0] = m_tau[0];
		taurange[1] = m_tau[m_ntaupoints-1];
		taurange[2] = TINY;
		return;
	}

	for(int n = 0; n < m_ntaupoints; n++){
		tauq = fabs(m_tau[n]-m_tau[m_ntmax]);
		if(m_Et[2][n] >= Elim || tauq < tautyp){
			taurange[0] = m_tau[n];
			break;
		}
	}

	for(int n = m_ntaupoints-1; n >= 0 ; n--){
		tauq = fabs(m_tau[n]-m_tau[m_ntmax]);
		if(m_Et[2][n] >= Elim || tauq < tautyp){
			taurange[1] = m_tau[n];
			break;
		}
	}
	taurange[2] = taurange[1]-taurange[0];
}

void FluxDensityConv::f_AllocateElectricField(
	bool accbase, // formura based on acceleration 
	bool divdfactor, // divide by the D factor
	bool allocspl, // allocate spline
	bool isfar, vector<double> *ppz, double *cxy)

{
    double Theta[3], R, acc[3], acctheta, Dn, D3, et[3];
    vector<double> ztmp;
    Spline etspl[3];
#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(5);
	if(EFieldProfile != nullptr){
		debug_out.open(EFieldProfile);
		if(debug_out){
			debug_out << setw(15) << setprecision(10);
		}
	}
#endif

	m_Etmax = 0;
	m_ntmax = 1;

    for(int n = 0; n < m_ntotorbit; n++){
		if(isfar){
	        m_orbit[n].GetRelativeCoordinateFar(
				m_zorbit[n], m_gamma2, m_qxqy, &m_tau[n], Theta, &m_D[n], ppz);
			R = 1.0;
		}
		else{
	        m_orbit[n].GetRelativeCoordinate(
		        m_zorbit[n], m_gamma2, m_XYZ, &m_tau[n], Theta, &m_D[n], &R, ppz, cxy);
		}
		Dn = m_D[n];
		D3 = Dn*Dn*Dn;
		for(int j = 0; j < 2; j++){
			acc[j] = m_orbit[n]._acc[j];
		}
		acctheta = (acc[0]*Theta[0]+acc[1]*Theta[1])*m_gamma2;
		for(int j = 0; j < 2; j++){
			et[j] = (2.0*acctheta*Theta[j]-m_D[n]*acc[j])/R;
		}
		m_Et[2][n] = sqrt(hypotsq(et[0], et[1]))/D3;
		if(m_Et[2][n] > m_Etmax){
			m_Etmax = m_Et[2][n];
			m_ntmax = n;
		}
        if(accbase){
			for(int j = 0; j < 2; j++){
				m_Et[j][n] = et[j];
			}
            if(n == 0){
                m_Dmin = m_D[n];
            }
            else{
                m_Dmin = min(m_Dmin, m_D[n]);
            }
			Dn = D3;
        }
		else{
			for(int j = 0; j < 2; j++){
				m_Et[j][n] = -Theta[j]/R;
			}
        }
#ifdef _DEBUG
		if (EFieldProfile != nullptr){
			items[0] = m_zorbit[n];
			for (int j = 0; j < 3; j++){
				items[j+1] = m_Et[j][n]/Dn;
			}
			items[4] = m_D[n];
			PrintDebugItems(debug_out, m_tau[n], items);
		}
#endif
		if(divdfactor){
			for(int j = 0; j < 2; j++){
				m_Et[j][n] /= Dn;
			}
		}
    }
	m_ntaupoints = m_ntotorbit;

    if(allocspl){
		if(m_isbm || m_iswshifter){
	        m_DSpline.SetSpline(m_ntaupoints, &m_tau, &m_D);
			for(int j = 0; j < 2; j++){
				m_EtSpline[j].SetSpline(m_ntaupoints, &m_tau, &m_Et[j]);
			}
	    }
		else{
	        m_DSpline.Initialize(m_ntaupoints, &m_tau, &m_D);
			for(int j = 0; j < 2; j++){
				m_EtSpline[j].Initialize(m_ntaupoints, &m_tau, &m_Et[j]);
			}
		}
	}
}

void FluxDensityConv::f_AllocateComplexFieldByFFT(bool iscsr)
{
    double D, tau, tauavgr[2], ewre, ewim;
	double dThx[2], dThy[2], taur[2];
	double *dTh[2] = {dThx, dThy};

#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(2);
	if(BeforeFFT != nullptr){
		debug_out.open(BeforeFFT);
	}
#endif

	if(m_isfixep){
		if (iscsr){
			for (int j = 0; j < 2; j++){
				m_EtSpline[j].AllocateGderiv();
			}
		}
		else{
			f_SetInterpolationEt(0.0, taur, dTh);
		}
        double w = m_fixep*PI2/m_conv_dtau2ep;
        for(int j = 0; j < 2; j++){
            m_EtSpline[j].IntegrateGtEiwt(w, &ewre, &ewim);
			f_GetFieldCommon(false, ewre, ewim, m_fixep, taur, dTh[j], &m_Fxy[2*j][0], &m_Fxy[2*j+1][0]);
        }
		return;
	}

//-------->>>>>>>
//m_isavgd = false;

	taur[0] = m_taurange[0]-m_dtau*0.5; // m_dtau*0.5 means half the bin size for FFT
    for(unsigned n = 0; n < m_nfft; n++){
		tau = m_taurange[0]+m_dtau*(double)n;
		if(tau-m_dtau*0.5 > m_taurange[1]){
			m_EwFFT[0][n] = m_EwFFT[1][n] = 0.0;
			continue;
		}
		taur[1] = tau+m_dtau*0.5;
		if(m_isavgd){			
			tauavgr[0] = tau-0.5*m_dtau;
			tauavgr[1] = tau+0.5*m_dtau;
			m_EwFFT[0][n] = m_EwFFT[1][n] = 0;
			if(tauavgr[0] < m_taurange[0]){
				for (int j = 0; j < 2; j++){
					m_EwFFT[j][n] += (m_taurange[0]-tauavgr[0])*m_EtSpline[j].GetIniXY(false);
				}				
			}
			if(tauavgr[1] > m_taurange[1]){
				for (int j = 0; j < 2; j++){
					m_EwFFT[j][n] += (tauavgr[1]-m_taurange[1])*m_EtSpline[j].GetFinXY(false);
				}
			}
			tauavgr[0] = max(tau-0.5*m_dtau, m_taurange[0]);
			tauavgr[1] = min(tau+0.5*m_dtau, m_taurange[1]);
			for (int j = 0; j < 2; j++){
				m_EwFFT[j][n] += m_EtSpline[j].Integrate(tauavgr);
				m_EwFFT[j][n] /= m_dtau;
			}
		}
		else{
			D = iscsr ? 1.0 : m_DSpline.GetValue(tau);
			if(m_isef_accel){
				D *= D*D;
			}
			for (int j = 0; j < 2; j++){
				m_EwFFT[j][n] = m_EtSpline[j].GetValue(tau)/D;
			}
		}
#ifdef _DEBUG
		if (BeforeFFT != nullptr){
			items[0] = m_EwFFT[0][n];
			items[1] = m_EwFFT[1][n];
			PrintDebugItems(debug_out, tau, items);
		}
#endif
    }

	for(int k = 0; k < 2 && m_isef_accel == false; k++){
		D = m_isavgd ? 1.0 : m_DSpline.GetValue(taur[k]);
		for(int j = 0; j < 2; j++){
			dTh[j][k] = m_EtSpline[j].GetValue(taur[k], true)/D;
		}
	}

	for(int j = 0; j < 2; j++){
		m_fft->DoRealFFT(m_EwFFT[j], 1);
	}

#ifdef _DEBUG
	if(BeforeFFT != nullptr && debug_out){
		debug_out.close();
	}
	if(AfterFFT != nullptr){
		debug_out.open(AfterFFT);
		if(debug_out){
			vector<double> items(4);
			double epr, cr;
			for (unsigned n = 0; n < m_nfft/2; n++){
				epr = (double)n*m_deFT;
				cr = m_isef_accel?m_dtau*m_gamma2/PI:m_dtau/wave_length(epr);
				for(int j = 0; j < 2; j++){
					items[2*j] = cr*m_EwFFT[j][2*n];
				}
				if(n == 0){
					items[1] = items[3] = 0;
				}
				else{
					for (int j = 0; j < 2; j++){
						items[2*j+1] = cr*m_EwFFT[j][2*n+1];
					}
				}
				PrintDebugItems(debug_out, epr, items);
			}
			debug_out.close();
		}
	}
	if(AfterFFTPJ != nullptr){
		items.resize(6);
		debug_out.open(AfterFFTPJ);
	}
#endif

    for(int n = 0; n < m_ndata4output; n++){
        for(int j = 0; j < 2; j++){
			ewre = m_EwFFT[j][2*n*m_fft_nskip];
			if(n == 0){
				ewim = 0;
			}
			else{
				ewim = m_EwFFT[j][2*n*m_fft_nskip+1];
			}
			f_AdjustPhase4TimeShift(m_taurange[0], m_ep[n], &ewre, &ewim);
			f_GetFieldCommon(true, ewre, ewim, m_ep[n], taur, dTh[j], &m_Fxy[2*j][n], &m_Fxy[2*j+1][n]);
        }
#ifdef _DEBUG
		if (AfterFFTPJ != nullptr){
			for(int j = 0; j < 4; j++){
				items[j] = m_Fxy[j][n];
			}
			items[4] =  atan2(m_Fxy[1][n], m_Fxy[0][n]+TINY);
			items[5] =  atan2(m_Fxy[3][n], m_Fxy[2][n]+TINY);
			PrintDebugItems(debug_out, m_ep[n], items);
		}
#endif
    }
}

void FluxDensityConv::f_GetFieldCommon(bool isfft,
	double rein, double imin, double ep, double taur[], double dTh[], double *reout, double *imout)
{
	double dtau = isfft ? m_dtau : 1.0;
	if(m_isef_accel){
		*reout = imin*dtau*m_gamma2/PI;
        *imout = -rein*dtau*m_gamma2/PI;
	}
	else{
		double ovalues[2];
		f_GetBoundaryTerm(ep, taur, dTh, ovalues);
		*reout = ovalues[0];
		*imout = ovalues[1];
		if(ep > TINY){
	        double dwavel = dtau/wave_length(ep);
			*reout += rein*dwavel;
			*imout += imin*dwavel;
		}
	}
}

void FluxDensityConv::f_GetBoundaryTerm(double ep, double *taur, double *dTh, double *values)
{
	double w = PI2*ep/m_conv_dtau2ep;
	values[0] = values[1] = 0;

	double wt, cf = -m_gamma2/PI;
	for(int i = 0; i < 2; i++){
		wt = w*taur[i]+PId2;
		values[0] += dTh[i]*cos(wt)*cf;
		values[1] += dTh[i]*sin(wt)*cf;
		cf = -cf; // flip sign for [integrand]_tau1^tau2
	}
}

void FluxDensityConv::f_AllocNTauPoints(int ntaupoints)
{
	if(m_ntaupoints < ntaupoints){
		m_tau.resize(ntaupoints);
		m_D.resize(ntaupoints);
		for(int j = 0; j < 3; j++){
		    m_Et[j].resize(ntaupoints, 0.0);
		}
		m_EtDFT[0].resize(ntaupoints, 0.0);
		m_EtDFT[1].resize(ntaupoints, 0.0);
	}
	m_ntaupoints = ntaupoints;
}

void FluxDensityConv::f_AdjustPhase4TimeShift(
    double tauini, double ep, double *ere, double *eim)
{
    double phishift, temp, cs, sn;

    phishift = PI2*tauini*ep/m_conv_dtau2ep;
    cs = cos(phishift);
    sn = sin(phishift);
    temp = *ere;
    *ere = cs*temp-sn*(*eim);
    *eim = sn*temp+cs*(*eim);
}

void FluxDensityConv::f_SetInterpolationEt(double w, double *taur, double **dTh)
{
	vector<double> tautmp(m_ntaupoints);
	int nvalid;

    for(int j = 0; j < 2; j++){
		nvalid = 0;
		for(int n = 0; n < m_ntaupoints; n++){
			if(m_tau[n] >= m_taurange[0] && m_tau[n] <= m_taurange[1]){
				if(j == 0){
					tautmp[nvalid] = m_tau[n];
				}
				m_EtDFT[j][nvalid] = m_Et[j][n];
				nvalid++;
			}
		}
        m_EtSpline[j].SetSpline(nvalid, &tautmp, &m_EtDFT[j]);
        m_EtSpline[j].AllocateGderiv();
    }
	if(!m_isef_accel){
		taur[0] = tautmp[0];
		taur[1] = tautmp[nvalid-1];
	    for(int j = 0; j < 2; j++){
			dTh[j][0] = m_EtDFT[j][0];
			dTh[j][1] = m_EtDFT[j][nvalid-1];
		}
	}
}

void FluxDensityConv::f_AllocateFieldWiggler()
{
    double fd[4];

    for(int n = 0; n < m_ndata4output; n++){
        m_trajectory->GetStokesWigglerApprox(m_XYZ, m_ep[n], fd);
        for(int j = 0; j < 4; j++){
            m_Fxy[j][n] = fd[j];
        }
    }

#ifdef _DEBUG
	if(FDWigglerApprox != nullptr){
		ofstream debug_out(FDWigglerApprox);
		vector<vector<double>> items;
		for(int j = 0; j < 4; j++){
			items.push_back(m_Fxy[j]);
		}
		PrintDebugRows(debug_out, m_ep, items, m_ndata4output);
	}
#endif
}

void FluxDensityConv::f_GetFluxItems(vector<double> *values)
{
    double fx[2], fy[2];
    vector<double> fxy(4);

    for(int n = 0; n < m_ndata4output; n++){
		if(m_isfluxamp){
			for (int j = 0; j < 4; j++){
				(*values)[n+j*m_ndata4output] = m_Fxy[j][n];
			}
		}
		else if(m_isfluxs0){
                if(m_iswigapprox){
                    (*values)[n] = m_Fxy[0][n]+m_Fxy[1][n];
                }
                else{
                    (*values)[n] = hypotsq(m_Fxy[0][n], m_Fxy[1][n])
                                    +hypotsq(m_Fxy[2][n], m_Fxy[3][n]);
                }
		}
		else{
			if(m_iswigapprox){
				for (int j = 0; j < 4; j++){
					fxy[j] = m_Fxy[j][n];
				}
			}
			else{
				for (int j = 0; j < 2; j++){
					fx[j] = m_Fxy[j][n];
					fy[j] = m_Fxy[j+2][n];
				}
				stokes(fx, fy, &fxy);
			}
			for (int j = 0; j < 4; j++){
				(*values)[n+j*m_ndata4output] = fxy[j];
			}
		}
    }
}
