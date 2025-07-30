#include <algorithm>
#include <iomanip>
#include <limits>
#include <climits>
#include <time.h>
#include "flux_density.h"
#include "filter_operation.h"
#include "trajectory.h"
#include "function_digitizer.h"
#include "particle_generator.h"

// files for debugging
string EFieldProfile;
string BeforeFFT;
string AfterFFT;
string AfterFFTPJ;
string FDWigglerApprox;
string FDensTempProf;
string BefESmooth;
string AftESmooth;

#define STEP_UPPER_LIMIT 2.0 // allowable step for tau (at the final position)
#define EPLOWLIMEPS 1.0e-10
#define TOTALITEMSSAVED 8
// (simpson:maxorder x 2)

FluxDensity::FluxDensity(SpectraSolver &spsolver, Trajectory *trajectory, FilterOperation *filter)
    : SpectraSolver(spsolver)
{
	Initialize();
	InitFluxDensity(trajectory, filter);
}

FluxDensity::FluxDensity(SpectraSolver &spsolver)
    : SpectraSolver(spsolver)
{
	Initialize();
}

void FluxDensity::Initialize()
{
#ifdef _CPUTIME
	m_cputime.resize(4, 0.0);
	m_rlabel.resize(4);
	m_rlabel[0] = "E-Field";
	m_rlabel[1] = "Interpolation(1)";
	m_rlabel[2] = "Interpolation(2)";
	m_rlabel[3] = "FFT";
	m_nrep = 0;
#endif

	m_isrealft = false;
	m_dim = m_isfel ? 3 : 2;
	m_isef_accel = m_iscoherent && m_istime && m_accb[singlee_];
	m_nepointsmin = -1;
	if(contains(m_calctype, menu::wigner)){
		m_nepointsmin = 8*m_accuracy[accinpE_]+1;
	}
}

void FluxDensity::InitFluxDensity(
	Trajectory *trajectory, FilterOperation *filter)
{
#ifdef _DEBUG
EFieldProfile = "..\\debug\\alloc_efield.dat";
//BeforeFFT = "..\\debug\\before_fft.dat";
//AfterFFT = "..\\debug\\after_fft.dat";
//AfterFFTPJ = "..\\debug\\after_fft_phase_adj.dat";
//FDWigglerApprox  = "..\\debug\\wiggler_approx_fd.dat";
//BefESmooth = "..\\debug\\bef_esmooth.dat";
//AftESmooth = "..\\debug\\aft_esmooth.dat";
//FDensTempProf = "..\\debug\\fdens_temp.dat";
#endif

	m_nfftmax = m_nfft = 0;
    m_fft = nullptr;
    for(int j = 0; j < 3; j++){
        m_EwFFT[j] = nullptr;
		m_EwBuf[j] = nullptr;
    }
    m_trajectory = trajectory;
	m_norbpoints = trajectory->GetOrbitPoints();
	f_AllocNTauPoints();
    m_conv_dtau2ep = 2.0*m_gamma2*CC*PLANCK;
	m_time2tau = 2.0*CC*m_gamma2;

    m_XYZ[2] = m_conf[slit_dist_];
	if(f_SetupCondition(filter) == false){
		throw runtime_error("Allowable memory (per process) is lower than required.");
		return;
	}
	if(m_customwiggler){
		m_trajectory->AllocateProjectedXPosision();
	}
}

FluxDensity::~FluxDensity()
{
	for(int j = 0; j < 3; j++){
		if(m_EwFFT[j] != nullptr){
			free(m_EwFFT[j]);
		}
		if(m_EwBuf[j] != nullptr){
			free(m_EwBuf[j]);
		}
	}
	for(int j = 0; j < m_ffts.size(); j++){
		delete m_ffts[j];
	}
}

void FluxDensity::GetFluxItemsAt(double *xy, 
	vector<double> *values, bool isfar, int *zfixrange, double *XY)
{
	if(isfar){
		f_SetXYAngle(xy);
	}
	else{
		f_SetXYPosition(xy);
	}
    if(m_customwiggler){
        f_AllocateFieldWiggler();
    }
    else{
        f_AllocateElectricField(false, true, isfar, nullptr, nullptr, XY);
		
		if(!f_SetupFTConfig()){
			throw runtime_error("Not enough memory available for FFT.");
			return;
		}
		
		f_AllocateComplexField(false, false, false, zfixrange, isfar, nullptr, nullptr, XY);
		if(m_confb[esmooth_]){
			double fx[2], fy[2];
			vector<double> fxy(4);
			for(int n = 0; n < m_nfd; n++){
				for(int j = 0; j < 2; j++){
					fx[j] = m_Fxy[j][n];
					fy[j] = m_Fxy[j+2][n];
				}
				stokes(fx, fy, &fxy);
				for(int j = 0; j < 4; j++){
					m_Fxy[j][n] = fxy[j];
				}
			}
#ifdef _DEBUG
			vector<string> titles{"Energy", "Fx", "Fy", "Fc", "F45"};
			vector<double> items(5);
			if(!BefESmooth.empty()){
				ofstream debug_out(BefESmooth);
				PrintDebugItems(debug_out, titles);
				for(int n = 0; n < m_nfd; n++){
					items[0] = m_ep[n];
					for(int j = 0; j < 4; j++){
						items[j+1] = m_Fxy[j][n];
					}
					PrintDebugItems(debug_out, items);
				}
				debug_out.close();
			}
#endif

			for(int j = 0; j < 4; j++){
				fill(m_eplogfd[j].begin(), m_eplogfd[j].end(), 0.0);
				for(int n = 0; n < m_eplogidx.size()-1; n++){					
					for(int i = m_eplogidx[n]; i < m_eplogidx[n+1]; i++){
						m_eplogfd[j][n] += m_Fxy[j][i];
					}
					m_eplogfd[j][n] /= (m_eplogidx[n+1]-m_eplogidx[n]);
				}
			}

#ifdef _DEBUG
			if(!AftESmooth.empty()){
				ofstream debug_out(AftESmooth);
				PrintDebugItems(debug_out, titles);
				for(int n = 0; n < m_eplog.size(); n++){
					items[0] = m_eplog[n];
					for(int j = 0; j < 4; j++){
						items[j+1] = m_eplogfd[j][n];
					}
					PrintDebugItems(debug_out, items);
				}
				debug_out.close();
			}
#endif
		}
	}
    f_GetFluxItems(values);
}

void FluxDensity::GetEnergyArray(vector<double> &energy)
{
	if(m_confb[esmooth_]){
		energy = m_eplog;
	}
	else{
		energy = m_ep;
	}
}

void FluxDensity::AllocateOrbitComponents()
{
    m_trajectory->GetTrajectory(&m_orbit);
}

//---------- private functions ----------
bool FluxDensity::f_SetupCondition(FilterOperation *filter)
{
    vector<double> zarray4bg;
    double epmin, epmax, erange[2], defrac, eps_erange, ecr;

    m_trajectory->GetZCoordinate(&m_zorbit);
    AllocateOrbitComponents();
    eps_erange = 1.0e-2/(1<<(m_accuracy[acclimpE_]-1));
	ecr = m_trajectory->GetCriticalEnergy();

	if(m_iscoherent && m_accb[singlee_] && !m_istime){
		// single e- complex amplitude
		m_isfixep = true;
	}
	else{
		m_isfixep = !m_confb[esmooth_] && !m_iscoherent && m_isfixepitem
			&& (m_iszspread || m_isskipespread || m_customwiggler);
	}
    if(m_isfixep){
		m_erange[0] = m_erange[1] = m_fixep;
		m_nfd = 1;
		m_ep.resize(1, m_fixep);
		m_deFT = 0;
		f_AllocMemory();
        return true;
    }
    else{
		if(m_isenergy || m_isvpdens){
            epmax = max(m_confv[erange_][0], m_confv[erange_][1]);
            epmin = min(m_confv[erange_][0], m_confv[erange_][1]);
        }
        else if(m_ispower && m_isfilter){
            if(filter->IsGeneric()){
				filter->GetEnergyRange4Power(ecr, eps_erange, erange);
				epmin = erange[0]; epmax = erange[1];
            }
            else{
                filter->GetEnergyRange(&epmin, &epmax);
            }
        }
        else{
            epmin = epmax = m_fixep;
        }
		if(m_iscoherent){
			double blen_sec = GetTypicalBunchLength();
			double frac = 1.0e-8/(1<<(m_accuracy[acclimpE_]-1));
			double pepmax = ecr*20.0*m_accuracy[acclimpE_];
			double emaxcoh = GetEnergyCoherent(blen_sec, frac);
			double etypcoh = GetEnergyCoherent(blen_sec, 0.5);
			if(!m_accb[singlee_]){
				pepmax = min(pepmax, emaxcoh);
			}
			if(m_isfel){
				epmin = 0;
				epmax = m_epmax_fel;
			}
			else if(m_istime){
				double trange = 2*max(fabs(m_confv[trange_][0]), fabs(m_confv[trange_][1]));
				trange *= 1.0e-15; // fs -> s
				epmin = min(pepmax*1e-2, PLANCK/trange)/m_accuracy[acclimtra_];
				epmax = pepmax;
			}
			else if(m_ispower){
				// power by integrating spectrum
				// cover whole spectral range
				epmin = pepmax*0.01/m_accuracy[acclimpE_];
				epmax = pepmax;
			}
			else{
				epmin = min(etypcoh*0.1/m_accuracy[acclimpE_], epmin);
				epmax = max(epmax, epmin+4.0*etypcoh*(1<<(m_accuracy[acclimpE_]-1)));
			}
		}
		else{
			if(m_confb[esmooth_]){
				epmin /= 1+m_conf[smoothwin_]*0.01;
				epmax *= 1+m_conf[smoothwin_]*0.01;
			}
			defrac = 1.0+1.0e-6;
			// 1e-6: to guarantee the energy range
			if (!m_isskipespread){
				defrac += 2.0*GetEspreadRange();
			}
			epmax *= defrac;
			epmin /= defrac;
		}
    }
	if(m_customwiggler){
		if(m_ispower && !m_isvpdens){
			m_nfd = 100<<(m_accuracy[accinpE_]-1);
			m_ep.resize(m_nfd);
			for(int n = 0; n < m_nfd; n++){
				m_ep[n] = epmin+(epmax-epmin)/(m_nfd-1)*n;
			}
		}
		else{
			m_nfd = (int)m_eparray.size();
			m_ep = m_eparray;
		}
		f_AllocMemory();
		return true;
	}

	m_erange[0] = epmin;
	m_erange[1] = epmax;

	double tautemp[3];
	// evaluate on axis
	f_SetXYPosition();
	f_AllocateElectricField(true, false, false);
	// force acc.-based evaluation to define the comp. range
	f_GetZrange(m_ispower, false, tautemp);
	m_taurange[0] = tautemp[0];
	m_taurange[2] = tautemp[1]-tautemp[0];

	// evaluate at ~ maximum observation angle
	f_SetXYPosition(m_xyfar);
	f_AllocateElectricField(true, false, false);
	f_GetZrange(m_ispower, false, tautemp);
	m_taurange[1] = tautemp[1];

	m_taurange[2] = max(m_taurange[2], tautemp[1]-tautemp[0]);

	return f_SetupFTBase(false);
}

bool FluxDensity::f_SetupFTBase(bool negblen)
{
	double Dtaucsr = 0, deFT;

	if(m_iscoherent && !negblen && !m_accb[singlee_]){
		double blen_sec = GetTypicalBunchLength();
		Dtaucsr = max(m_seedtwin, blen_sec*m_nlimit[acclimtra_]);
		if(m_istime){
			double trange = 2*max(fabs(m_confv[trange_][0]), fabs(m_confv[trange_][1]));
			trange *= 1.0e-15; // fs -> s
			Dtaucsr = trange+Dtaucsr;
		}
		if(m_isfel){
			double twindow = 0;
			if(m_isEtprof){
				vector<double> tgrid;
				m_Etprof.GetVariable(0, &tgrid);
				twindow = tgrid.back()-tgrid.front();
			}
			else if(m_iscurrprof){
				vector<double> tgrid;
				m_currprof.GetVariable(0, &tgrid);
				twindow = tgrid.back()-tgrid.front();
			}
			twindow = max(twindow, m_seedtwin);
			Dtaucsr = max(twindow, Dtaucsr);
		}
		Dtaucsr *= 2.0*m_gamma2*CC; // normalize time
	}

	double Deltau = sqrt(hypotsq(Dtaucsr, m_taurange[2]));
	deFT = m_conv_dtau2ep/(4.0*Deltau)/(1<<(m_accuracy[accinpE_]-1));

	double erange = m_erange[1]-m_erange[0];
	int minpoints = 51;
	if(m_nepointsmin >= 0){
		minpoints = m_nepointsmin;
	}
	int epoints = max(minpoints, 2*(int)ceil(erange/2.0/deFT)+1);
	m_nfftbase = 64;
	while(m_nfftbase*deFT < 4.0*erange && m_nfftbase < INT_MAX){
		m_nfftbase <<= 1;
	}
	m_nfftbase <<= (m_accuracy[accinpE_]-1);

	m_deFT = erange/(double)(epoints-1);
	if(m_isund){
		// adjust energy interval and range to catch the harmonic energy
		double e1st = GetE1st();
		m_deFT = e1st/floor(e1st/m_deFT);
		m_erange[0] = m_deFT*floor(m_erange[0]/m_deFT);
		m_erange[1] = m_erange[0]+(epoints-1)*m_deFT;
	}
	if(m_isrealft){
		m_nini4ep = (int)floor(m_erange[0]/m_deFT);
		m_erange[0] = m_nini4ep*m_deFT;
	}
	else{
		m_nini4ep = 0;
	}
	m_dtau = m_conv_dtau2ep/(m_nfftbase*m_deFT);
	m_nfd = epoints;
	m_ep.resize(m_nfd);
	for(int n = 0; n < m_nfd; n++){
		m_ep[n] = m_erange[0]+m_deFT*n;
	}
	f_AllocMemory();

	if(m_confb[esmooth_]){
		double de;
		int index = 0;
		m_eplogidx.push_back(index);
		while(1) {
			de = max(m_deFT, m_ep[index]*m_conf[smoothwin_]*0.01);
			int incr = (int)floor(0.5+de/m_deFT);
			if(index+2*incr >= m_nfd){
				index = m_nfd;
			}
			else{
				index = min(m_nfd, index+incr);
			}
			m_eplogidx.push_back(index);
			if(index == m_nfd){
				break;
			}
		};
		m_eplog.resize(m_eplogidx.size()-1);
		for(int j = 0; j < 4; j++){
			m_eplogfd[j].resize(m_eplogidx.size()-1);
		}
		for(int n = 0; n < m_eplogidx.size()-1; n++){
			m_eplog[n] = (m_ep[m_eplogidx[n]]+m_ep[m_eplogidx[n+1]-1])/2;
		}
	}

	return true;
}

void FluxDensity::f_AllocMemory()
{
	m_Fxy.resize(2*m_dim);
	for(int j = 0; j < 2*m_dim; j++){
		m_Fxy[j].resize(m_nfd);
	}
	if(m_iscoherent){
		m_Fbuf.resize(4);
		for(int j = 0; j < 4; j++){
			m_Fbuf[j].resize(m_nfd, 0.0);
		}
	}
}

bool FluxDensity::f_SetupFTConfig()
{
	if(m_isfixep){
		return true;
	}
	if(!m_isfel){
		f_GetZrange(m_ispower, m_iscoherent, m_taurange);
	}
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
        for(int j = 0; j < m_dim; j++){
            m_EwFFT[j] = (double *)realloc_chk(m_EwFFT[j], sizeof(double)*nfft*2);
            if(m_EwFFT[j] == nullptr){
                return false;
            }
			if(m_iscoherent){
				m_EwBuf[j] = (double *)realloc_chk(m_EwBuf[j], sizeof(double)*nfft*2);
				if (m_EwBuf[j] == nullptr){
					return false;
				}
			}
        }
		m_nfftmax = nfft;
	}
	f_SwitchFFT(nfft);
	return true;
}

void FluxDensity::f_SwitchFFT(int nfft)
{
	if(nfft != m_nfft){
		for(int j = 0; j < m_nffts.size(); j++){
			if(m_nffts[j] == nfft){
				m_fft = m_ffts[j];
				m_nfft = nfft;
				return;
			}
		}
        m_fft = new FastFourierTransform(1, nfft);
		m_ffts.push_back(m_fft);
		m_nffts.push_back(nfft);
		m_nfft = nfft;
    }
}


void FluxDensity::f_SetXYPosition(double *xy)
{
	if(xy == nullptr){
		m_XYZ[0] = m_XYZ[1] = 0;
	}
	else{
		m_XYZ[0] = xy[0];
		m_XYZ[1] = xy[1];
	}
}

void FluxDensity::f_SetXYAngle(double *qxy)
{
    m_qxqy[0] = qxy[0];
    m_qxqy[1] = qxy[1];
}

void FluxDensity::f_GetZrange(bool ispower, bool iscsr, double taurange[])
	// f_AllocateElectricField() should be called before
{
	double tautyp = 0;

	if(!ispower){
		if(m_erange[0] > 0){
			tautyp = m_conv_dtau2ep/(INFINITESIMAL+m_erange[0]);
		}
		else{
			tautyp = m_tau[m_ntaupoints-1]-m_tau[0];
		}
	}

	double eps, tauq, Elim;

	eps = 1.0e-6/pow(10.0, (double)(m_accuracy[acclimtra_]-1)*0.5);
	Elim = eps*m_Etmax;

	if(m_Etmax == 0){
		taurange[0] = m_tau[0];
		taurange[1] = m_tau[m_ntaupoints-1];
		taurange[2] = INFINITESIMAL;
		return;
	}

	for(int n = 0; n < m_ntaupoints; n++){
		tauq = fabs(m_tau[n]-m_tau[m_ntmax]);
		if(m_EtPw[n] >= Elim || tauq < tautyp){
			taurange[0] = m_tau[n];
			break;
		}
	}

	for(int n = m_ntaupoints-1; n >= 0 ; n--){
		tauq = fabs(m_tau[n]-m_tau[m_ntmax]);
		if(m_EtPw[n] >= Elim || tauq < tautyp){
			taurange[1] = m_tau[n];
			break;
		}
	}
	if(iscsr){
		if(m_istime){
			double taucsr[2] = {min(m_confv[trange_][0], m_confv[trange_][1]),
				max(m_confv[trange_][0], m_confv[trange_][1])};
			for(int j = 0; j < 2; j++){
				taucsr[j] *= 1.0e-15; // fs -> s
				taucsr[j] *= 2.0*m_gamma2*CC; // normalize time
			}
			taurange[0] = min(taurange[0], taucsr[0]);
			taurange[1] = max(taurange[1], taucsr[1]);
		}

		double brange, divrange;
		brange = GetTypicalBunchLength();
		brange *= 2.0*m_gamma2*CC*m_nlimit[acclimtra_]; // expand for bunch length
		divrange = hypotsq(m_div[0]*m_nlimit[acclimobs_], m_div[1]*m_nlimit[acclimobs_])*(2.0*m_gamma2); // for divergence
		double rrq = sqrt(hypotsq(m_Esize[0]*m_nlimit[acclimobs_], m_Esize[1]*m_nlimit[acclimobs_]));
		if(rrq > 0){
			double rrange = min(atan2(rrq, m_conf[slit_dist_]), 1/m_gamma);
			brange += rrange*rrange*fabs(m_conf[slit_dist_])*(2.0*m_gamma2);
		}

		taurange[0] += m_zorbit[0]*divrange-brange;
		taurange[1] += m_zorbit[m_ntaupoints-1]*divrange+brange;
	}

	taurange[2] = taurange[1]-taurange[0];
}

void FluxDensity::f_AllocateElectricField(
	bool forceaccl, // force acc.-based formula
	bool allocspl, // allocate spline
	bool isfar, double *zobs, double *tdelay, double *xyorb)

{
    double Theta[3], R, acc[3], acctheta, D3, D2, et[3], eto[3], tauoffset = 0;
	double dz = m_zorbit[1]-m_zorbit[0];
    vector<double> ztmp;
    Spline etspl[3];
#ifdef _DEBUG
	ofstream debug_out;
	vector<string> titles {"tau", "z", "Ex", "Ey", "Etpow", "D"};
	if(m_dim == 3){
		titles.insert(titles.begin()+4, "Ez");
	}
	vector<double> items(titles.size());
	if(!EFieldProfile.empty()){
		debug_out.open(EFieldProfile);
		if(debug_out){
			debug_out << setw(15) << setprecision(10);
		}
		PrintDebugItems(debug_out, titles);
	}
#endif

	if(tdelay != nullptr){
		tauoffset = (*tdelay)*m_time2tau;
	}

	m_Etmax = 0;
	m_ntmax = 1;

#ifdef _CPUTIME
	MeasureTime();
#endif

	int n;
    for(n = 0; n < m_norbpoints; n++){
		if(isfar){
	        m_orbit[n].GetRelativeCoordinateFar(
				m_zorbit[n], m_gamma2, m_qxqy, &m_tau[n], Theta, &m_D[n], zobs, xyorb);
			R = 1.0;
		}
		else{
	        m_orbit[n].GetRelativeCoordinate(
		        m_zorbit[n], m_gamma2, m_XYZ, &m_tau[n], Theta, &m_D[n], &R);
			if(R < dz/2){
				R = dz/2;
			}
		}
		m_tau[n] += tauoffset; // add temporal delay if any
		D2 = m_D[n]*m_D[n];
		D3 = m_D[n]*D2;
		for(int j = 0; j < 2; j++){
			acc[j] = m_orbit[n]._acc[j];
		}
		acctheta = (acc[0]*Theta[0]+acc[1]*Theta[1])*m_gamma2;
		if(m_dim == 3){
			Theta[2] = (1/m_gamma2
				+hypotsq(m_orbit[n]._beta[0], m_orbit[n]._beta[1])
				-hypotsq(Theta[0]+m_orbit[n]._beta[0], Theta[1]+m_orbit[n]._beta[1])
				)/2;
			acc[2] = -m_orbit[n]._beta[0]*acc[0]-m_orbit[n]._beta[1]*acc[1];
		}
		for(int j = 0; j < m_dim; j++){
			et[j] = (2.0*acctheta*Theta[j]-m_D[n]*acc[j])/R;
		}

		m_EtPw[n] = sqrt(hypotsq(et[0], et[1]))/D3;
		if(m_EtPw[n] > m_Etmax){
			m_Etmax = m_EtPw[n];
			m_ntmax = n;
		}
        if(m_isef_accel || forceaccl){
			for(int j = 0; j < m_dim; j++){
				m_Et[j][n] = et[j]/D3;
			}
            if(n == 0){
                m_Dmin = m_D[n];
            }
            else{
                m_Dmin = min(m_Dmin, m_D[n]);
            }
        }
		else{
			for(int j = 0; j < m_dim; j++){
				if(n == 0){
					m_Et[j][n] = eto[j] = 0;
				}
				else{
					m_Et[j][n] = m_Et[j][n-1]-(eto[j]+et[j]/D2)*0.5*dz;
					eto[j] = et[j]/D2;
				}
			}
		}

		if(n == m_norbpoints-1 && m_norbpoints > 1){
			// observation angle can be potentially too large
			double dtau0 = m_tau[n-1]-m_tau[n-2];
			double dtau1 = m_tau[n]-m_tau[n-1];
			if(dtau1 > dtau0*STEP_UPPER_LIMIT){
				break;
			}
		}

#ifdef _DEBUG
		if(!EFieldProfile.empty()){
			items[0] = m_tau[n];
			items[1] = m_zorbit[n];
			for (int j = 0; j < m_dim; j++){
				items[j+2] = m_Et[j][n];
			}
			items[m_dim+2] = m_EtPw[n];
			items[m_dim+3] = m_D[n];
			PrintDebugItems(debug_out, items);
		}
#endif
    }
	m_ntaupoints = n;	

#ifdef _CPUTIME
	MeasureTime(0);
#endif

#ifdef _DEBUG
	if(!EFieldProfile.empty()){
		debug_out.close();
	}
#endif

#ifdef _CPUTIME
	MeasureTime();
#endif

    if(allocspl){
		// revised to always use spline interpolation: 2023/03/26
		for(int j = 0; j < m_dim; j++){
			m_EtSpline[j].SetSpline(m_ntaupoints, &m_tau, &m_Et[j]);
		}
		for(int j = 0; j < m_dim; j++){
			m_EtSpline[j].AllocateGderiv();
		}
	}

#ifdef _CPUTIME
	MeasureTime(1);
#endif
}

void FluxDensity::f_AllocateComplexField(bool step, bool skipft, bool fixtau, 
	int *zidxrange,	bool isfar, double *zobs, double *tdelay, double *xyorb)
{
    double tau, tauspl[2], tauavgr[3], Gr, Gi;
	bool issectioned = zidxrange != nullptr;
	bool isborder[2];

	tauspl[0] = m_EtSpline[0].GetIniXY();
	tauspl[1] = m_EtSpline[0].GetFinXY();
	if(fixtau){
		m_taur[0] = m_taurange[0]-m_dtau;
		m_taur[1] = m_taurange[1]+m_dtau;
	}
	else if(issectioned){
		double Theta[2], dummy, R;
		for(int j = 0; j < 2; j++){
			if(isfar){
				m_orbit[zidxrange[j]].GetRelativeCoordinateFar(
					m_zorbit[zidxrange[j]], m_gamma2, m_qxqy, 
					&m_taurange[j], Theta, &dummy, zobs, xyorb);
			}
			else{
				m_orbit[zidxrange[j]].GetRelativeCoordinate(
					m_zorbit[zidxrange[j]], m_gamma2, m_XYZ, &m_taurange[j], Theta, &dummy, &R);
			}
			if(tdelay != nullptr){
				m_taurange[j] += (*tdelay)*m_time2tau;
			}
		}
		m_taur[0] = max(m_taurange[0], tauspl[0]);
		m_taur[1] = min(m_taurange[1], tauspl[1]);
	}
	else{
		m_taur[0] = max(m_taurange[0]-m_dtau/2, tauspl[0]);
		m_taur[1] = min(m_taurange[1]+m_dtau/2, tauspl[1]);
	}
	if(m_isfixep){
		f_SetInterpolationEt(issectioned?m_taurange:nullptr);
		f_GetFT();
		return;
	}
	m_taur[1] = min(m_taur[1], m_taurange[0]+m_dtau*(double)(m_nfft-0.5));

	double ecenter = (m_erange[0]+m_erange[1])*0.5;
	if(skipft || m_isrealft){
		ecenter = 0.0;
	}

#ifdef _CPUTIME
	MeasureTime();
#endif

	double wcenter = ecenter*PI2/m_conv_dtau2ep;
	int nini = -1;
    for(unsigned n = 0; n < m_nfft; n++){
		tau = m_taurange[0]+m_dtau*(double)n;
		for(int j = 0; j < m_dim; j++){
			if(m_isrealft){
				m_EwFFT[j][n] = 0.0;
			}
			else{
				m_EwFFT[j][2*n] = m_EwFFT[j][2*n+1] = 0.0;
			}
		}
		tauavgr[0] = tau-0.5*m_dtau;
		tauavgr[1] = tau+0.5*m_dtau;
		if(tauavgr[1] < m_taur[0] || tauavgr[0] > m_taur[1]){
			continue;
		}
		if(fixtau){
			int nn = m_isrealft ? n : 2*n;
			if(tauavgr[1] < tauspl[0]){
				for(int j = 0; j < m_dim; j++){
					m_EwFFT[j][nn] = m_isef_accel ? 0 : m_EtSpline[j].GetIniXY(false);
				}
				continue;
			}
			else if(tauavgr[0] > tauspl[1]){
				for(int j = 0; j < m_dim; j++){
					m_EwFFT[j][nn] = m_isef_accel ? 0 : m_EtSpline[j].GetFinXY(false);
				}
				continue;
			}
		}
		for(int j = 0; j < 2; j++){
			isborder[j] = tauavgr[0] < m_taur[j] && tauavgr[1] > m_taur[j];
			if(isborder[j]){
				// shrink the average range
				tauavgr[j] = m_taur[j];
			}
		}
		if(nini < 0){
			nini = m_EtSpline[0].GetIndexXcoord(tauavgr[0]);
		}

		int nininew;
		for (int j = 0; j < m_dim; j++){
			if(step){
				nininew = m_EtSpline[j].IntegrateGtEiwtStep(nini, tauavgr, wcenter, &Gr, &Gi);
			}
			else{
				nininew = m_EtSpline[j].IntegrateGtEiwt(nini, tauavgr, wcenter, &Gr, &Gi);
			}
			if(m_isrealft){
				m_EwFFT[j][n] = Gr/m_dtau;
			}
			else{
				m_EwFFT[j][2*n] = Gr/m_dtau;
				m_EwFFT[j][2*n+1] = Gi/m_dtau;
			}
		}
		nini = nininew;
    }

	for(int j = 0; j < m_dim; j++){
		for(int k = 0; k < 2; k++){
			// assign the boundary term
			m_dTh[j][k] = m_EtSpline[j].GetValue(m_taur[k], true);
		}
	}

#ifdef _DEBUG
	if(!BeforeFFT.empty() && !skipft){
		vector<string> titles {"tau", "Ex.re", "Ex.im", "Ey.re", "Ey.im"};
		if(m_dim == 3){
			titles.push_back("Ez.re");
			titles.push_back("Ez.im");
		}
		vector<double> items(titles.size()-1);
		ofstream debug_out(BeforeFFT);
		PrintDebugItems(debug_out, titles);
		for (unsigned n = 0; n < m_nfft; n++){
			tau = m_taurange[0]+m_dtau*(double)n;
			tauavgr[0] = tau-0.5*m_dtau;
			tauavgr[1] = tau+0.5*m_dtau;
			if(tauavgr[1] < m_taur[0] || tauavgr[0] > m_taur[1]){
				continue;
			}
			for(int j = 0; j < m_dim; j++){
				if(m_isrealft){
					items[2*j] = m_EwFFT[j][n];
					items[2*j+1] = 0;
				}
				else{
					items[2*j] = m_EwFFT[j][2*n];
					items[2*j+1] = m_EwFFT[j][2*n+1];
				}
			}
			PrintDebugItems(debug_out, tau, items);
		}
		debug_out.close();
	}
#endif

#ifdef _CPUTIME
	MeasureTime(2);
	MeasureTime();
#endif

	if(!skipft){
		f_GetSpectrum();
	}

#ifdef _CPUTIME
	MeasureTime(3);
#endif
}

void FluxDensity::f_GetFT()
{
	double ewre, ewim;
	for(int n = 0; n < m_nfd; n++){ 
		double w = m_ep[n]*PI2/m_conv_dtau2ep;
		for (int j = 0; j < 2; j++){
			m_EtSpline[j].IntegrateGtEiwt(w, &ewre, &ewim);
			f_GetFieldCommon(j, false, ewre, ewim, m_ep[n], &m_Fxy[2*j][n], &m_Fxy[2*j+1][n]);
		}
	}
}

void FluxDensity::f_GetSpectrum()
{
	double ewre, ewim;

	for(int j = 0; j < m_dim; j++){
		if(m_isrealft){
			m_fft->DoRealFFT(m_EwFFT[j], 1);
		}
		else{
			m_fft->DoFFT(m_EwFFT[j], 1);
		}
	}

#ifdef _DEBUG
	ofstream debug_out;
	if(!AfterFFT.empty()){
		double ecenter = m_isrealft ? 0 : (m_erange[0]+m_erange[1])*0.5;
		debug_out.open(AfterFFT);
		if(debug_out){
			vector<string> titles{"ep", "Ex.re", "Ex.im", "Ey.re", "Ey.im"};
			if(m_dim == 3){
				titles.push_back("Ez.re");
				titles.push_back("Ez.im");
			}
			vector<double> items(titles.size()-1);
			PrintDebugItems(debug_out, titles);
			double epr, cr;
			for (unsigned n = 0; n < (m_isrealft?(m_nfft/2):m_nfft); n++){
				epr = fft_index(n, m_nfft, 1)*m_deFT+ecenter;
				if(epr <= 0){
					continue;
				}
				cr = m_isef_accel?m_dtau*m_gamma2/PI:m_dtau/wave_length(fabs(epr));
				for(int j = 0; j < m_dim; j++){
					items[2*j] = cr*m_EwFFT[j][2*n];
					items[2*j+1] = (m_isrealft&&n==0) ? 0 : cr*m_EwFFT[j][2*n+1];
				}
				PrintDebugItems(debug_out, epr, items);
			}
			debug_out.close();
		}
	}
	vector<double> items;
	if(!AfterFFTPJ.empty()){
		debug_out.open(AfterFFTPJ);
		vector<string> titles {"ep", "Ex.re", "Ex.im", "Ey.re", "Ey.im"};
		if(m_dim == 3){
			titles.push_back("Ez.re");
			titles.push_back("Ez.im");
		}
		items.resize(titles.size()-1);
		PrintDebugItems(debug_out, titles);
	}
#endif

	int nh = 0, noffset = 0;
	if(m_isrealft){
		noffset = m_nini4ep;
	}
	else{
		nh = (m_nfd-1)/2;
	}

    for(int n = 0; n < m_nfd; n++){
		int nskip = m_fft_nskip*(n-nh+noffset);
		int nr = fft_index(nskip, m_nfft, -1);
        for(int j = 0; j < m_dim; j++){
			if(m_isrealft && n >= (int)m_nfft/2){
				ewre = ewim = 0;
			}
			else{
				ewre = m_EwFFT[j][2*nr];
				ewim = m_EwFFT[j][2*nr+1];
				if(m_isrealft && n == 0){
					ewim = 0;
				}
			}
			f_AdjustPhase4TimeShift(m_taurange[0], (n-nh)*m_deFT, &ewre, &ewim);
			f_GetFieldCommon(j, true, ewre, ewim, m_ep[n], &m_Fxy[2*j][n], &m_Fxy[2*j+1][n]);
        }
#ifdef _DEBUG
		if(!AfterFFTPJ.empty()){
			for(int j = 0; j < 2*m_dim; j++){
				items[j] = m_Fxy[j][n];
			}
			PrintDebugItems(debug_out, m_ep[n], items);
		}
#endif
    }
#ifdef _DEBUG
	if(!AfterFFTPJ.empty()){
		debug_out.close();
	}
#endif
}

void FluxDensity::f_GetTemporal()
{
	double dnu = 2.0/(m_dtau*m_nfftbase); // 2.0: inverse real fft
	dnu *= PI/m_gamma2;

	for(int j = 0; j < m_dim; j++){
		m_EwFFT[j][0] = m_EwFFT[j][1] = 0.0;
		for(int n = 1; n < (int)(m_nfft/2); n++){
			if(n >= m_nfd){
				m_EwFFT[j][2*n] = m_EwFFT[j][2*n+1] = 0.0;
			}
			else{
				// Fw = Dw * (i Pi/gamma^2)
				m_EwFFT[j][2*n] = -m_Fbuf[2*j+1][n]*dnu;
				m_EwFFT[j][2*n+1] = m_Fbuf[2*j][n]*dnu;
			}
		}
		m_fft->DoRealFFT(m_EwFFT[j], -1);
	}

#ifdef _DEBUG
	if(!FDensTempProf.empty()){
		ofstream debug_out(FDensTempProf);
		vector<string> titles(m_dim+1);
		vector<double> items(m_dim+1);
		titles[0] = "tau";
		titles[1] = "Ex";
		titles[2] = "Ey";
		if(m_dim == 3){
			titles[3] = "Ez";
		}
		PrintDebugItems(debug_out, titles);
		for(int n = 0; n < (int)m_nfft; n++){
			items[0] = n*m_dtau/m_fft_nskip;
			for(int j = 0; j < m_dim; j++){
				items[j+1] = m_EwFFT[j][n];
			}
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif

}

void FluxDensity::f_GetFieldCommon(int jxy, bool isfft,
	double rein, double imin, double ep, double *reout, double *imout)
{
	double dtau = isfft ? m_dtau : 1.0;
	if(m_isef_accel){ // Dw = Fw * gamma^2/(i Pi)
		*reout = imin*dtau*m_gamma2/PI;
        *imout = -rein*dtau*m_gamma2/PI;
	}
	else{
		double ovalues[2];
		f_GetBoundaryTerm(jxy, ep, ovalues);
		*reout = ovalues[0];
		*imout = ovalues[1];
		if(ep > INFINITESIMAL){
	        double dwavel = dtau/wave_length(ep);
			*reout += rein*dwavel;
			*imout += imin*dwavel;
		}
	}
}

void FluxDensity::f_GetBoundaryTerm(int jxy, double ep, double *values)
{
	double w = PI2*ep/m_conv_dtau2ep;
	values[0] = values[1] = 0;

	double wt, cf = -m_gamma2/PI;
	for(int i = 0; i < 2; i++){
		wt = w*m_taur[i]+PId2;
		values[0] += m_dTh[jxy][i]*cos(wt)*cf;
		values[1] += m_dTh[jxy][i]*sin(wt)*cf;
		cf = -cf; // flip sign for [integrand]_tau1^tau2
	}
}

void FluxDensity::f_AllocNTauPoints()
{
	if(m_tau.size() < m_norbpoints){
		m_tau.resize(m_norbpoints);
		m_D.resize(m_norbpoints);
		for(int j = 0; j < 3; j++){
		    m_Et[j].resize(m_norbpoints, 0.0);
		}
		m_EtPw.resize(m_norbpoints, 0.0);
		m_EtDFT[0].resize(m_norbpoints, 0.0);
		m_EtDFT[1].resize(m_norbpoints, 0.0);
	}
}

void FluxDensity::f_AdjustPhase4TimeShift(
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

void FluxDensity::f_SetInterpolationEt(double *taurange)
{
	vector<double> tautmp(m_ntaupoints);
	int nvalid = 0;

	if(m_isfixep && taurange == nullptr){
		nvalid = m_ntaupoints;
		tautmp = m_tau;
	}

    for(int j = 0; j < 2; j++){
		if(m_isfixep && taurange == nullptr){
			m_EtDFT[j] = m_Et[j];
		}
		else{
			nvalid = 0;
			for (int n = 0; n < m_ntaupoints; n++){
				if (m_tau[n] >= taurange[0] && m_tau[n] <= taurange[1]){
					if (j == 0){
						tautmp[nvalid] = m_tau[n];
					}
					m_EtDFT[j][nvalid] = m_Et[j][n];
					nvalid++;
				}
			}
		}
		m_EtSpline[j].SetSpline(nvalid, &tautmp, &m_EtDFT[j]);
        m_EtSpline[j].AllocateGderiv();
    }
	if(!m_isef_accel){
		m_taur[0] = tautmp[0];
		m_taur[1] = tautmp[nvalid-1];
	    for(int j = 0; j < 2; j++){
			m_dTh[j][0] = m_EtDFT[j][0];
			m_dTh[j][1] = m_EtDFT[j][nvalid-1];
		}
	}
}

void FluxDensity::f_AllocateFieldWiggler()
{
	m_trajectory->GetStokesWigglerApprox2D(m_XYZ, m_nfd, m_ep, m_Fxy);

#ifdef _DEBUG
	if(!FDWigglerApprox.empty()){
		ofstream debug_out(FDWigglerApprox);
		vector<vector<double>> items;
		for(int j = 0; j < 4; j++){
			items.push_back(m_Fxy[j]);
		}
		PrintDebugRows(debug_out, m_ep, items, m_nfd);
	}
#endif
}

void FluxDensity::f_GetFluxItems(vector<double> *values)
{
    double fx[2], fy[2];
    vector<double> fxy(4);

	int nfd = m_confb[esmooth_] ? (int)m_eplog.size() : m_nfd;

    for(int n = 0; n < nfd; n++){
		if(m_isfluxamp){
			for (int j = 0; j < 4; j++){
				(*values)[n+j*m_nfd] = m_Fxy[j][n];
			}
		}
		else if(m_isfluxs0){
			if(m_confb[esmooth_]){
				(*values)[n] = m_eplogfd[0][n]+m_eplogfd[1][n];
			}
			else if(m_customwiggler){
				(*values)[n] = m_Fxy[0][n]+m_Fxy[1][n];
			}
			else{
				(*values)[n] = hypotsq(m_Fxy[0][n], m_Fxy[1][n])
					+hypotsq(m_Fxy[2][n], m_Fxy[3][n]);
			}
		}
		else{
			if(m_confb[esmooth_]){
				for (int j = 0; j < 4; j++){
					fxy[j] = m_eplogfd[j][n];
				}
			}
			else if(m_customwiggler){
				for(int j = 0; j < 4; j++){
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
				(*values)[n+j*nfd] = fxy[j];
			}
		}
    }
}
