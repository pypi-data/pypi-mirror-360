#ifdef _DEBUG
#include <sstream>
#endif

#include "spectra_solver.h"
#include "undulator_flux_far.h"
#include "bm_wiggler_radiation.h"
#include "beam_convolution.h"
#include "spatial_convolution.h"
#include "density_fixed_point.h"
#include "trajectory.h"
#include "filter_operation.h"
#include "spatial_convolution_fft.h"
#include "coherent_radiation.h"
#include "wigner_function.h"
#include "output_utility.h"
#include "json_writer.h"
#include "volume_power_density.h"
#include "kvalue_operation.h"
#include "hg_modal_decomp_ctrl.h"
#include "fel_amplifier.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

// files for debugging
string SpsolverEtProfile;

SpectraSolver::SpectraSolver(SpectraConfig &spconf, int thid, MPIbyThread *thread)
	: SpectraConfig(spconf)
{
#ifdef _DEBUG
//SpsolverEtProfile = "..\\debug\\spsolver_etprofile.dat";
#endif

	m_thread = thread;
	if(m_thread != nullptr){
		m_rank = thid;
		m_mpiprocesses = thread->GetThreads();
	}
	m_calcstatus = new PrintCalculationStatus(true, m_rank, m_serno);
	m_calcstatus->InitializeStatus(5);

	m_bmconv = new BeamConvolution();
	for(int j = 0; j < 6; j++){
		m_partbuf[j] = nullptr;
	}

	m_isgaussbeam = m_accsel[bunchtype_] == GaussianLabel;
	m_iscurrprof = m_accsel[bunchtype_] == CustomCurrent;
	m_isEtprof = m_accsel[bunchtype_] == CustomEt;
	m_isparticle = m_accsel[bunchtype_] == CustomParticle;

	m_isfar = contains(m_calctype, menu::far);
	m_circslit = contains(m_calctype, menu::slitcirc);
	m_rectslit = contains(m_calctype, menu::slitrect);
	m_totalslit = contains(m_calctype, menu::tflux);
	m_ispower = contains(m_calctype, menu::powercv);
	m_isfldamp = contains(m_calctype, menu::camp);
	m_isenergy = contains(m_calctype, menu::energy);
	m_isvpdens = contains(m_calctype, menu::vpdens);
	m_istime = contains(m_calctype, menu::temporal);
	m_isrespow = contains(m_calctype, menu::pdensr);
	m_issrcpoint = contains(m_calctype, menu::srcpoint) 
		|| contains(m_calctype, menu::wigner);
	m_isefield = contains(m_calctype, menu::efield);
	m_iscoherent = contains(m_calctype, menu::cohrad);
	m_isfilter = m_confsel[filter_] != NoneLabel;

	m_isfel = m_confsel[fel_] != NoneLabel;

	m_seedtwin = 0;
	if(m_isfel){
		m_confb[exportEt_] = m_confb[exportEt_] && 
			(m_confb[R56Bunch_] || m_confb[exportInt_]);
		if(m_confb[exportEt_]){
			m_d_eta = m_conf[edevstep_];
		}
		if(m_confsel[fel_] == FELSeedLabel || m_confsel[fel_] == FELCPSeedLabel){
			if(m_confsel[fel_] == FELSeedLabel){
				m_seedtwin = fabs(m_conf[pulselen_]);
			}
			else{
				double GDD = m_conf[gdd_], pstretch, alpha;
				get_chirp(GDD, fabs(m_conf[tlpulselen_]), &pstretch, &alpha);
				m_seedtwin = fabs(m_conf[tlpulselen_])*pstretch;
			}
			m_seedtwin = (m_seedtwin*GAUSSIAN_MAX_REGION*2+fabs(m_conf[timing_]))*1e-15;
		}
	}

    m_ismapaxis = m_srctype == CUSTOM || m_srctype == CUSTOM_PERIODIC;
    m_isdefault = !m_ismapaxis && !m_ismap3d && !m_isbm && !m_iswshifter;   
	m_issymmetric = m_srcsel[field_str_] == SymmLabel || m_isoddpole;
    m_isnatfoc[0] = m_srcsel[natfocus_] == BxOnlyLabel || m_srcsel[natfocus_] == BothLabel;
    m_isnatfoc[1] = m_srcsel[natfocus_] == ByOnlyLabel || m_srcsel[natfocus_] == BothLabel;
	m_iszspread = m_accb[zerosprd_] || fabs(m_acc[espread_]) < INFINITESIMAL;

	m_customwiggler = m_srctype == CUSTOM && m_confb[wiggapprox_];
	m_isskipespread = !m_iscoherent && 
		(m_isbm || m_iswshifter || m_customwiggler || m_confb[wiggapprox_]);

	m_isfixepitem = 
		contains(m_calctype, menu::phasespace) ||
		contains(m_calctype, menu::camp) ||
		contains(m_calctype, menu::CMD2d) ||
		contains(m_calctype, menu::CMDPP) ||
		(contains(m_calctype, menu::srcpoint) 
			&& contains(m_calctype, menu::sprof)) ||
		((IsFixedPoint() || contains(m_calctype, menu::spatial)) && 
			(contains(m_calctype, menu::fdensa) || contains(m_calctype, menu::fdenss)));

	// target item in flux calculation
	m_isfluxamp = (m_iscoherent && m_isfldamp) || m_issrcpoint;
	m_isfluxs0 = m_ispower && (m_isfilter || m_iscoherent);

	// settings for computation accuracy
    m_spfftlevel = m_accuracy[accinobs_]+1;
    if(m_ispower && !m_isfilter){
        m_spfftlevel -= 2;
    }
	m_tol_spint = 0.2/(1<<(m_accuracy[accinobs_]-1));
    if(m_isfar){
		m_tol_spint *= 0.5;
    }

	double charge;
	if(m_iscurrprof){
		charge = m_currprof.GetVolume(0);
	}
	else if(m_isEtprof){
		if(fabs(m_acc[R56add_]) > 0){
			double r56 = -m_acc[R56add_]/CC;
			// dispersion (m) to R56 (s)
			m_Etprof.ApplyDispersion(r56);
		}

		charge = m_Etprof.GetVolume(0);
		double sigma[2], area, alpha;
		m_Etprof.GetStatistics(sigma, &area, &alpha, 0);
		m_acc[espread_] = sigma[1];

		vector<double> eprof, edev;
		m_Etprof.GetProjection(1, 0, &eprof);
		m_Etprof.GetVariable(1, &edev);
		eprof /= charge;
		m_eprofile[0].Initialize((int)edev.size(), &edev, &eprof, true);
		m_eprofile[0].Integrate(&eprof);
		m_eprofile[1].Initialize((int)edev.size(), &edev, &eprof, true);

#ifdef _DEBUG
        if(!SpsolverEtProfile.empty()){
            ofstream debug_out(SpsolverEtProfile);
			vector<vector<double>> eprofs(2);
			m_eprofile[0].GetArrays(nullptr, &eprofs[0]);
			eprofs[1] = eprof;
            PrintDebugRows(debug_out, edev, eprofs, (int)edev.size());
        }
#endif
	}
	else if(m_isparticle){
		charge = f_LoadParticleData(m_accs[bunchdata_]);
	}
	else{
		charge = m_acc[bunchcharge_]*1.0e-9;
	}

	if(m_acctype == RING){
		m_AvCurr = m_acc[imA_]*0.001; // mA -> A
		if(m_isgaussbeam){
			charge = m_AvCurr/(CC/m_acc[cirm_]/m_acc[bunches_]);
		}
	}
	else{
		m_AvCurr = charge*m_acc[pulsepps_];
	}
	m_bunchelectrons = charge/QE;
	m_gamma2 = m_gamma*m_gamma;

	ApplyConditions();
	f_SetAutoRange();

	// variables for time- or energy-dependence
	if(m_istime){
		SetTimePoints();
	}
	if(m_isenergy || m_isvpdens){
		SetEnergyPoints();
	}
}

void SpectraSolver::ApplyConditions(bool setconv)
{
	// parameters related to K values and observation conditions
	SetObservation(setconv);
	if(m_issegu){
        m_Ldrift = m_src[interval_]-m_lu*(double)m_N;
        if(m_Ldrift < 0.0){
            m_Ldrift = 0.0;
            m_src[interval_] = m_lu*(double)m_N;
        }
        m_pslip = floor(m_Ldrift/m_lu/(1.0+m_K2));
		double pfactor = m_isf8 ? 0.5 : 1.0;
        if(m_issrc2){
            m_segphase[1] = PI*(m_pslip*2.0+pfactor*m_srcv[phi12_][0]);
            m_segphase[2] = PI*(m_pslip*2.0+pfactor*m_srcv[phi12_][1]);
        }
        else{
            m_segphase[0] = PI*(m_pslip*2.0+pfactor*m_src[phi0_]);
        }
	}

    m_fcoef_obspoint = 1.0e+3; // m -> mm
    if(m_confsel[defobs_] == ObsPointAngle){
        m_fcoef_obspoint /= m_conf[slit_dist_]; // mm -> mrad
    }

	if(m_isund && (m_isfixepitem || contains(m_calctype, menu::fixed))){
		double e1st = GetE1st();
		if(contains(m_calctype, menu::srcpoint)
			|| contains(m_calctype, menu::wigner)
			|| contains(m_calctype, menu::CMD2d)
			|| contains(m_calctype, menu::CMDPP)
			){
			m_fixep = e1st*(1.0+m_conf[detune_])*m_conf[hfix_];
			if(m_isf8){
				m_fixep *= 2.0;
			}
		}
		else if(m_confb[normenergy_]){
			m_fixep = e1st*m_conf[nefix_];
			if(m_isf8){
				m_fixep *= 2.0;
			}
		}
		else{
			m_fixep = m_conf[efix_];
		}
	}
	else{
		m_fixep = m_conf[efix_];
	}
}

void SpectraSolver::DeleteInstances()
{
	for(int j = 0; j < 6; j++){
		if(m_partbuf[j] != nullptr){
			delete m_partbuf[j];
		}
	}
	delete m_calcstatus;
	delete m_bmconv;
}

double SpectraSolver::GetE1st(double gt)
{
	return f_GetE1stBase(m_K2+gt*gt);
}

double SpectraSolver::GetKperp(double e1st)
{
	if(m_isf8){
		e1st /= 2;
	}
	double K2 = COEF_E1ST*m_acc[eGeV_]*m_acc[eGeV_]/m_lu/e1st-1.0;
	if(K2 < 0){
		return 0.0;
	}
    return sqrt(2.0*K2);
}

double SpectraSolver::GetCriticalEnergy(double *Bptr)
{
	double B;
	if(Bptr == nullptr){
		B = m_Bmax;
	}
	else{
		B = *Bptr;
	}
	return COEF_EC*m_acc[eGeV_]*m_acc[eGeV_]*B;
}

double SpectraSolver::GetEspreadRange()
{
	if(m_isEtprof){
		vector<double> earr;
		m_Etprof.GetVariable(1, &earr);
		return max(fabs(earr[0]), fabs(earr[earr.size()-1]));
	}
	return (m_accb[zerosprd_] ? 0.0 : m_acc[espread_])*m_nlimit[acclimpE_]; 
		// not AccTypesEE, return value is always used for "photon energy convolution"
}

void SpectraSolver::SetTimePoints()
{
	int tmesh = max(2, (int)floor(m_conf[tmesh_]+0.5));
	double dt = (m_confv[trange_][1]-m_confv[trange_][0])/(double)(tmesh-1);
	m_tarray.resize(tmesh);
    for(int n = 0; n < tmesh; n++){
		m_tarray[n] = m_confv[trange_][0]+dt*(double)n;
		m_tarray[n] *= 1.0e-15; // fs -> s
    }
}

void SpectraSolver::SetObservation(bool setconv)
{
	bool iswhole = contains(m_calctype, menu::tflux);
	bool isxymesh = contains(m_calctype, menu::meshxy);
	bool isxyalong = contains(m_calctype, menu::along);
	bool isrphimesh = contains(m_calctype, menu::meshrphi);
	
	m_center[0] = m_center[1] = 0.0;
	double apt[2] = {0, 0}, radius[2];
	m_xyfar[0] = m_xyfar[1] = 0.0;

	bool isangle = m_confsel[defobs_] == ObsPointAngle;

	if(m_rectslit && m_confsel[aperture_] == NormSlitLabel && m_isund){
		int tgtnh = 1;
		if(m_isf8){
			tgtnh = 2;
		}
		double ep = tgtnh*GetE1st();
		double divxy[2], sizexy[2], Divxy[2], Sizexy[2];

		SincFuncEspreadProfile snesprd(*this);
		double peaksn, divr;
		snesprd.GetPeakValueStdDeviation(tgtnh, &peaksn, &divr);
		divr /= m_gamma;
		GetSrcDivSize(ep, divxy, sizexy, Divxy, Sizexy, nullptr);
		for(int j = 0; j < 2; j++){
			sizexy[j] = sqrt(hypotsq(sizexy[j], m_conf[slit_dist_]*divr));
			Sizexy[j] = sqrt(hypotsq(m_Esize[j], sizexy[j]));
			Sizexy[j] *= 1000.0; // m -> mm
			m_confv[slitapt_][j] = Sizexy[j]*m_confv[nslitapt_][j];
			m_confv[qslitapt_][j] = m_confv[slitapt_][j]/m_conf[slit_dist_];
		}
		if(m_confb[powlimit_]){
			SetPowerLimit();
		}
		setconv = true;
		// aperture changed, so reset m_bmconv
	}

	m_slitapt[0] = m_slitapt[1] = 0;
	if(m_circslit || m_rectslit){
		for(int j = 0; j < 2; j++){
			m_center[j] = isangle ? m_conf[slit_dist_]*m_confv[qslitpos_][j] : m_confv[slitpos_][j];
			if(m_circslit){
				radius[j] = isangle ? m_conf[slit_dist_]*m_confv[slitq_][j] : m_confv[slitr_][j];
				m_xyfar[0] = max(m_xyfar[0], fabs(m_center[j])+fabs(radius[j]));
				m_xyfar[1] = m_xyfar[0];
				radius[j] *= 0.001; // mm -> m
			}
			else{
				apt[j] = isangle ? m_conf[slit_dist_]*m_confv[qslitapt_][j] : m_confv[slitapt_][j];
				m_xyfar[j] = fabs(m_center[j])+fabs(apt[j])*0.5;
				apt[j] *= 0.001;  // mm -> m
			}
		}
		if(m_circslit){
			m_slitapt[0] = m_slitapt[1] = 2.0*max(radius[0], radius[1]);
			for (int j = 0; j < 2; j++){
				m_slitr[j] = radius[j];
			}
		}
		else{
			for (int j = 0; j < 2; j++){
				m_slitapt[j] = apt[j];
			}
		}
	}
	else if(isrphimesh){
		for(int j = 0; j < 2; j++){
			m_xyfar[0] = max(m_xyfar[0], fabs(isangle ? m_conf[slit_dist_]*m_confv[qrange_][j] : m_confv[rrange_][j]));
		}
		m_xyfar[1] = m_xyfar[0];
	}
	else if(isxymesh || isxyalong){
		for(int j = 0; j < 2; j++){
			m_xyfar[0] = max(m_xyfar[0], fabs(isangle ? m_conf[slit_dist_]*m_confv[qxrange_][j] : m_confv[xrange_][j]));
			m_xyfar[1] = max(m_xyfar[1], fabs(isangle ? m_conf[slit_dist_]*m_confv[qyrange_][j] : m_confv[yrange_][j]));
		}
	}
	else if(iswhole){
		for(int j = 0; j < 2; j++){
			m_xyfar[j] = m_GT[1-j]*RADIATION_POWER_SPREAD_LIMIT*m_accuracy[acclimobs_];
			m_xyfar[j] *= 1000.0/m_conv2gt; 
			// define the far point in mm to be consistent with other conditions
		}
	}
	else{
		for(int j = 0; j < 2; j++){
			m_center[j] = isangle ? m_conf[slit_dist_]*m_confv[qxyfix_][j] : m_confv[xyfix_][j];
			m_xyfar[j] = fabs(m_center[j]);
		}
	}
	for(int j = 0; j < 2; j++){ // mm -> m
		m_center[j] *= 0.001;
		m_xyfar[j] *= 0.001;
	}
	if(iswhole){
		m_gttypical = max(m_GT[0], m_GT[1])*m_nlimit[acclimobs_];
		m_slitapt[0] = m_slitapt[1] = m_gttypical/m_gamma;
	}
	else{
		m_gttypical = max(m_xyfar[0]+m_Esize[0], m_xyfar[1]+m_Esize[1])*m_conv2gt;
	}

	if(setconv){
		if (m_circslit){ // circular slit
			m_bmconv->SetCondition(m_Esize, m_accb[zeroemitt_], m_center, radius, nullptr, m_accuracy[accinobs_]);
			m_bmconv->AllocateConvolutedValue();
		}
		else if (m_rectslit){
			m_bmconv->SetCondition(m_Esize, m_accb[zeroemitt_], m_center, nullptr, apt, m_accuracy[accinobs_]);
		}
		else if (iswhole || m_accb[zeroemitt_]){
			m_bmconv->Disable();
		}
		else{
			m_bmconv->SetCondition(m_Esize, m_accb[zeroemitt_], m_center, nullptr, nullptr, m_accuracy[accinobs_]);
		}
	}

	m_gtcenter = sqrt(hypotsq(m_center[0], m_center[1]))*m_conv2gt;
	for(int j = 0; j < 2; j++){
		if (!contains(m_calctype, menu::tflux) && !m_isfel){
			m_xyfar[j] += m_Esize[j]*m_nlimit[acclimobs_];
		}
	}
	m_gtmax = sqrt(hypotsq(m_xyfar[0], m_xyfar[1]))*m_conv2gt;
}


void SpectraSolver::SetEnergyPoints(bool isfix, bool forcemesh)
{
	if(isfix){
		m_eparray.resize(1);
		m_eparray[0] = m_fixep;
		return;
	}

	int emesh = max(2, (int)floor(m_conf[emesh_]+0.5));
	double epmin = min(m_confv[erange_][0], m_confv[erange_][1]);
	double epmax = max(m_confv[erange_][0], m_confv[erange_][1]);
	double de;
	bool islog = m_confsel[estep_] == LogLabel;
	if(islog){
        if(epmin <= 0.0 && epmax <= 0.0){
			epmin = epmax = 0.0;
            de = 0.0;
        }
        else{
            if(epmin <= 0.0){
                epmin = epmax/(double)emesh*0.1;
            }
            de = exp(log(epmax/epmin)/(double)(emesh-1));
        }
	}
	else{
		if(forcemesh || m_confb[wiggapprox_] || 
			m_iswiggler || m_srctype == BM || m_srctype == WLEN_SHIFTER){
			de = (epmax-epmin)/(double)(emesh-1);
		}
		else{
			de = m_conf[de_];
			emesh = (int)floor((epmax-epmin)/de+0.5)+1;
		}
	}
	m_eparray.resize(emesh);
    for(int n = 0; n < emesh; n++){
        if(islog){
            m_eparray[n] = epmin*pow(de, (double)n);
        }
        else{
            m_eparray[n] = epmin+de*(double)n;
        }
    }
}

void SpectraSolver::ResetEnergyPrms(double emin, double emax)
// set energy range, energy interval and turn off log. scale
{
	double e1st = GetE1st();
	double de = e1st/(double)(m_accuracy[accinpE_]*16*m_N*m_M);
	m_confv[erange_][0] = emin;
	m_confv[erange_][1] = emax;
	m_conf[de_] = de;
	m_confsel[estep_] = LinearLabel;
	SetEnergyPoints();
}

void SpectraSolver::GetSincFunctions(int nh, double epr, vector<double> *snc)
{
    double snarg0, snarg1, snarg2, dN = (double)m_N;

    if(nh > 0){
        snarg0 = PI*dN*(epr-(double)nh);
        (*snc)[0] = sincsq(snarg0);
    }
    else{
        (*snc)[0] = 1.0;
    }
    if(m_issegu){
        if(m_issrc2){
            snarg1 = PI2*dN+m_segphase[1];
            snarg2 = PI2*dN+m_segphase[1]*0.5+m_segphase[2]*0.5;
            snarg1 *= epr;
            snarg2 *= epr;
        }
        else{
            snarg1 = 0.0;
            snarg2 = (PI*dN+0.5*m_segphase[0])*epr;
        }
        (*snc)[0] *= sinfunc(m_M, snarg2);
        if(m_issrc2){
            (*snc)[1] = (*snc)[0]*cos(snarg1);
            (*snc)[2] = -(*snc)[0]*sin(snarg1); // to be consistent with the helicity in the near-zone
        }
    }
}

void SpectraSolver::MultiplySincFunctions(
    vector<double> *fxyin, vector<double> *sn, vector<double> *fxyout)
{
    int j;

    for(j = 0; j < 4; j++){
        (*fxyout)[j] = (*fxyin)[j]*(*sn)[0];
    }
    if(m_issegu && m_issrc2){
        (*fxyout)[0] += (*fxyin)[4]*(*sn)[1]+(*fxyin)[6]*(*sn)[2];
        (*fxyout)[1] += (*fxyin)[5]*(*sn)[1]+(*fxyin)[7]*(*sn)[2];
        (*fxyout)[2] += (*fxyin)[9]*(*sn)[1]+(*fxyin)[10]*(*sn)[2];
        (*fxyout)[3] += (*fxyin)[8]*(*sn)[1]-(*fxyin)[11]*(*sn)[2];
    }
}

double SpectraSolver::EnergyProfile(double epref, double ep, double deavg)
{
	double frac, tex;
	double eprel = epref-ep;
    // consider the gamma dependence of flux
	double gfactor = 1.0+eprel/epref;
	if(m_isEtprof){
		if(deavg == 0){
			frac = m_eprofile[0].GetValue(eprel/epref/2.0)/2.0/epref;
		}
		else{
			frac = m_eprofile[1].GetValue((eprel+0.5*deavg)/epref/2.0)
				-m_eprofile[1].GetValue((eprel-0.5*deavg)/epref/2.0);
			frac /= deavg;
		}

	}
	else{
		double esigma = EnergySpreadSigma(epref);
		if(esigma == 0){
			return 0;
		}
		else if(deavg == 0){
			tex = eprel/esigma;
			tex *= tex*0.5;
			frac = (tex < MAXIMUM_EXPONENT)?exp(-tex)/SQRTPI2/esigma:0.0;
		}
		else{
			frac = 0.5*(errf((eprel+deavg*0.5)/SQRT2/esigma)-errf((eprel-deavg*0.5)/SQRT2/esigma))/deavg;
		}
	}
	return frac*gfactor;
}

double SpectraSolver::EnergySpreadSigma(double epref)
{
    if(m_accb[zerosprd_]){
        return 0.0;
    }
	if(epref > 0){
		return 2.0*epref*m_acc[espread_];
	}
	return m_acc[espread_];
}

int SpectraSolver::GetNumberOfItems()
{
    int items;
    if(m_ispower){
        if(m_isrespow){
            items = 3;
        }
        else if(m_isfilter){
            items = 2;
        }
        else{
            items = 1;
        }
    }
	else if(m_issrcpoint){
		items = 1;
	}
	else if(m_isefield){
		items = 2;
	}
    else{
        items = 4;
    }
    return items;
}

void SpectraSolver::GetEBeamSize(double *size)
{
	for(int j = 0; j < 2; j++){
		if(m_accb[zeroemitt_]){
			size[j] = 0;
		}
		else if(m_issrcpoint){
			size[j] = m_size[j];
		}
		else{
			size[j] = m_Esize[j];
		}
	}
}

bool SpectraSolver::IsSmoothSprofile()
{
    return (!m_issrcpoint) && (!m_iscoherent) && (m_ispower)
            && (!m_isfilter) && (!m_isrespow);
}

void SpectraSolver::GetGridContents(int type, bool ismesh,
	double *xyini, double *dxy, double *dxyspl, int *mesh, int wigtype, bool ism)
{
	int rindex = 0, qindex = 0,  mindex = 0;

	if(wigtype >= 0){
		switch(wigtype){
			case WignerFuncType4DX:
			case WignerFuncType2DX:
				rindex = type > 0 ?  Xprange_ : Xrange_;
				mindex = type > 0 ?  Xpmesh_ : Xmesh_;
				break;
			case WignerFuncType4DY:
			case WignerFuncType2DY:
				rindex = type > 0 ?  Yprange_ : Yrange_;
				mindex = type > 0 ?  Ypmesh_ : Ymesh_;
				break;
			case WignerFuncTypeXY:
				rindex = type > 0 ?  Yrange_ : Xrange_;
				mindex = type > 0 ?  Ymesh_ : Xmesh_;
				break;
			case WignerFuncTypeXpYp:
				rindex = type > 0 ?  Yprange_ : Xprange_;
				mindex = type > 0 ?  Ypmesh_ : Xpmesh_;
				break;
		}
	}
	else if(m_issrcpoint){
		rindex = type > 0 ?  Yrange_ : Xrange_;
		mindex = GetIndexXYMesh(type);
	}
	else if(contains(m_calctype, menu::meshrphi)){
		rindex = rrange_;
		qindex = qrange_;
		if(m_confsel[defobs_] == ObsPointAngle){
			mindex = qphimesh_;
		}
		else{
			mindex = rphimesh_;
		}
		if (type > 0){
			rindex = phirange_;
			qindex = phirange_;
			mindex = phimesh_;
		}
	}
	else{
		if(type > 0){
			rindex = yrange_;
			qindex = qyrange_;
		}
		else{
			rindex = xrange_;
			qindex = qxrange_;
		}
		mindex = GetIndexXYMesh(type);
	}

	*xyini = 0;
	*mesh = 1;
	*dxy = 0.0;
    if(ismesh){
		double Dxy;
		if(wigtype < 0 && m_confsel[defobs_] == ObsPointAngle){
			*xyini = min(m_confv[qindex][0], m_confv[qindex][1]);
			*xyini *= m_conf[slit_dist_];
			Dxy = fabs(m_confv[qindex][0]-m_confv[qindex][1]);
			if(qindex != phirange_){
				Dxy *= m_conf[slit_dist_];
			}
		}
		else{
			*xyini = min(m_confv[rindex][0], m_confv[rindex][1]);
			Dxy = fabs(m_confv[rindex][0]-m_confv[rindex][1]);
		}
		*mesh = (int)floor(0.5+m_conf[mindex]);
		if(*mesh > 1){
			*dxy = Dxy/(double)((*mesh)-1);
		}
		if(ism){
			*dxy *= 0.001;
			*xyini *= 0.001;
		}
    }

    *dxyspl = *dxy;
    if(m_ispower){
        *dxyspl = m_conf[slit_dist_]/m_gamma;
    }
}

void SpectraSolver::GetSPDConditions(
		vector<vector<double>> &obs, vector<vector<double>> &xyz, vector<vector<double>> &exyz)
{
	obs.resize(2);
	if(IsFixedPoint()){
		xyz.resize(1); xyz[0].resize(3);
		exyz.resize(1); exyz[0].resize(3);
		xyz[0][2] = m_conf[slit_dist_];
		for(int j = 0; j < 2; j++){
			xyz[0][j] = m_confv[xyfix_][j]*0.001;
		}
        double ntheta = PId2-m_conf[Qnorm_]*DEGREE2RADIAN;
        double nphi = m_conf[Phinorm_]*DEGREE2RADIAN;
        exyz[0][0] = sin(ntheta)*cos(nphi);
        exyz[0][1] = sin(ntheta)*sin(nphi);
        exyz[0][2] = cos(ntheta);
		return;
	}

	int mesh[2], varidx[2];
	mesh[1] = (int)floor(0.5+m_conf[zmesh_]);
	varidx[1] = zrange_;
	bool isx = false, isy = false, isr = false;
    if(contains(m_calctype, menu::xzplane)){
		mesh[0] = (int)floor(0.5+m_conf[xmesh_]);
		varidx[0] = xrange_;
		isx = true;
    }
    if(contains(m_calctype, menu::yzplane)){
		mesh[0] = (int)floor(0.5+m_conf[ymesh_]);
		varidx[0] = yrange_;
		isy = true;
    }
    if(contains(m_calctype, menu::pipe)){
		mesh[0] = (int)floor(0.5+m_conf[phimesh_]);
		varidx[0] = phirange_;
		isr = true;
    }
	double dvar = 0;
	for(int j = 0; j < 2; j++){
		if(mesh[j] > 1){
			dvar = (m_confv[varidx[j]][1]-m_confv[varidx[j]][0])/(mesh[j]-1);
		}
		obs[j].resize(mesh[j]);
		for(int n = 0; n < mesh[j]; n++){
			obs[j][n] = m_confv[varidx[j]][0]+dvar*n;
			if(fabs(obs[j][n]) < DXY_LOWER_LIMIT*fabs(dvar)){
				obs[j][n] = 0;
			}
		}
	}
	int ntotal = mesh[0]*mesh[1];
	xyz.resize(ntotal);
	exyz.resize(ntotal);

	double efix[2] = {0, 0};

	if(isx){
		efix[0] = 0.0;
		efix[1] = m_conf[spdyfix_] > 0 ? 1.0 : 0.0;
	}
	else if(isy){
		efix[0] = m_conf[spdxfix_] > 0 ? 1.0 : 0.0;
		efix[1] = 0;
	}

	for(int m = 0; m < mesh[1]; m++){
		for (int n = 0; n < mesh[0]; n++){
			int nt = m*mesh[0]+n;
			xyz[nt].resize(3);
			exyz[nt].resize(3);
			if(isr){
				double phi = obs[0][n]*DEGREE2RADIAN;
				exyz[nt][0] = xyz[nt][0] = cos(phi);
				exyz[nt][1] = xyz[nt][1] = sin(phi);
				for(int j = 0; j < 2; j++){
					xyz[nt][j] *= m_conf[spdrfix_]*0.001;
				}
			}
			else{
				for(int j = 0; j < 2; j++){
					exyz[nt][j] = efix[j];
				}
				if (isx){
					xyz[nt][0] = obs[0][n]*0.001;
					xyz[nt][1] = m_conf[spdyfix_]*0.001;
				}
				else{
					xyz[nt][0] = m_conf[spdxfix_]*0.001;
					xyz[nt][1] = obs[0][n]*0.001;
				}
			}
			xyz[nt][2] = obs[1][m];
			exyz[nt][2] = 0;
		}
	}
}

int SpectraSolver::GetIndexXYMesh(int type)
{
	int mindex;
	if(m_issrcpoint){
		mindex = type > 0 ?  Ymesh_ : Xmesh_;
	}
	else{
		mindex = type > 0 ?  ymesh_ : xmesh_;
	}
	return mindex;
}

void SpectraSolver::ArrangeMeshSettings(
	vector<vector<double>> &xyrp, vector<vector<double>> &xyobs)
{
	int mesh[2];
	double dummy, pini[2], dp[2];

	for(int j = 0; j < 2; j++){
		GetGridContents(j, true, &pini[j], &dp[j], &dummy, &mesh[j], -1, false);
	}

	xyrp.resize(2);
	for(int j = 0; j < 2; j++){
		xyrp[j].resize(mesh[j]);
		for(int m = 0; m < mesh[j]; m++){
			xyrp[j][m] = pini[j]+dp[j]*m;
			if (fabs(xyrp[j][m]) < fabs(dp[j])*DXY_LOWER_LIMIT){
				xyrp[j][m] = 0.0;
			}
		}
	}
	// xyrp: grid positions in mm and degree (in position)

	xyobs.resize(2);
    if(contains(m_calctype, menu::along)){
		int mini[2] = {0, mesh[0]};
		int mfin[2] = {mesh[0], mesh[0]+mesh[1]};
		for(int j = 0; j < 2; j++){
			xyobs[j].resize(mesh[0]+mesh[1], 0.0);
			for(int m = mini[j]; m < mfin[j]; m++){
				xyobs[j][m] = xyrp[j][m-mini[j]]*0.001;
			}
		}
	}
	else{
		for(int j = 0; j < 2; j++){
			xyobs[j].resize(mesh[0]*mesh[1]);
		}
		for(int n = 0; n < mesh[1]; n++){
			for(int m = 0; m < mesh[0]; m++){
				int index = n*mesh[0]+m;
				if(contains(m_calctype, menu::meshrphi)){
					xyobs[0][index] = xyrp[0][m]*cos(xyrp[1][n]*DEGREE2RADIAN);
					xyobs[1][index] = xyrp[0][m]*sin(xyrp[1][n]*DEGREE2RADIAN);
					for(int j = 0; j < 2; j++){
						xyobs[j][index] *= 0.001;
					}
				}
				else{
					xyobs[0][index] = xyrp[0][m]*0.001;
					xyobs[1][index] = xyrp[1][n]*0.001;
				}
			}
		}
	}

	if(m_confsel[defobs_] == ObsPointAngle){
		xyrp[0] /= m_conf[slit_dist_];
		if(!contains(m_calctype, menu::meshrphi)){
			xyrp[1] /= m_conf[slit_dist_];
		}
	}
}

void SpectraSolver::GetAccuracySpFFT(double *tol, int *level, double *nglim)
{
	*tol = m_tol_spint;
	*nglim = m_nlimit[acclimobs_];
	*level = m_spfftlevel;
}

double SpectraSolver::GetTotalPowerID()
{
    double K2sum = 0.0, tpower;

	for(int j = 0; j < 2; j++){
		for (int k = 1; k < m_Kxy[j].size(); k++){
			K2sum += m_Kxy[j][k]*m_Kxy[j][k]*(double)(k*k);
		}
	}
	tpower = 2.0*K2sum/m_lu;
	if(m_issrc2){
		tpower *= 2.0;
	}
	if(m_issegu){
		tpower *= (double)m_M;
	}
    return tpower*((double)m_N-(m_isoddpole?0.5:0.0))
		*COEF_TOTAL_POWER_ID*m_acc[eGeV_]*m_acc[eGeV_]*m_AvCurr;
}


double SpectraSolver::GetFluxCoef(bool isbmtot)
{
	double coef;
	if(m_isfar || isbmtot){
		if(m_isbm || m_iswiggler || isbmtot){
			double dN = m_N;
			if(m_iswiggler && m_isoddpole){
				dN -= 0.5;
			}
			if(m_totalslit || isbmtot){
				coef = COEF_TOT_FLUX_BM*m_acc[eGeV_]*m_AvCurr/PI2;
				if(m_isbm){
					coef *= m_conf[horizacc_]*1.0e-3; // mrad - > rad
				}
				else{
					coef *= dN/m_gamma;
				}
				return coef;
			}
			else{
				coef = COEF_FLUX_BM*m_acc[eGeV_]*m_acc[eGeV_];
			}
			if(m_iswiggler){
				coef *= 2.0*dN;
			}
		}
		else{
			if(m_confb[wiggapprox_]){
				if(m_totalslit){
					coef = COEF_TOT_FLUX_BM*m_acc[eGeV_]*m_AvCurr/PI2*m_M*m_N/m_gamma;
					return coef;
				}
				else{
					coef = COEF_FLUX_UND*m_acc[eGeV_]*m_acc[eGeV_]*m_N*m_M;
				}
			}
			else{
				coef = COEF_FLUX_UND*m_acc[eGeV_]*m_acc[eGeV_]*m_N*m_N;
			}
		}
	}
	else if(m_customwiggler){
        coef = COEF_FLUX_BM*m_acc[eGeV_]*m_acc[eGeV_];
        coef /= m_conf[slit_dist_]*m_conf[slit_dist_]; // mrad^2->mm^2
	}
	else{
        coef = COEF_ALPHA/1.0E+9/QE;
	}
	coef *= m_AvCurr;
	if(m_iscoherent){
		coef *= m_bunchelectrons;
	}
	if(m_rectslit || m_circslit || m_totalslit){
		if(m_isfar){
			coef /= m_conf[slit_dist_]*m_conf[slit_dist_]; // /mrad^2 -> /mm^2
		}
		coef *= 1.0e+6; // /mm^2 -> /m^2
	}
	return coef;
}

double SpectraSolver::GetPowerCoef()
{
	double coef;
	if(m_isfar){
		if(m_isbm){
			coef = COEF_PWDNS_BM*m_Bmax*pow(m_acc[eGeV_], 4.0);
		}
		else{
			coef = COEF_PWDNS_ID_FAR*m_M*m_N*pow(m_acc[eGeV_], 4.0);
		}
	}
	else{
		coef = COEF_PWDNS_NEAR*pow(m_acc[eGeV_], 6.0);
	}
	coef *= m_AvCurr;
	if(m_iscoherent){
		coef *= m_bunchelectrons;
	}
	if(m_rectslit || m_circslit){
		if(m_isfar){
			coef /= m_conf[slit_dist_]*m_conf[slit_dist_]; // /mrad^2 -> /mm^2
		}
		coef *= 1.0e+6; // /mm^2 -> /m^2
	}
	return coef;
}

double SpectraSolver::GetTempCoef(bool forcefield)
{
	double coef = 4.0e-7*CC*CC*m_gamma2*m_gamma2*QE;
	if(!m_accb[singlee_]){
		coef *= m_bunchelectrons;
	}
	if(m_ispower && !forcefield){
		coef *= coef/Z0VAC;
		coef *= 1.0e-9; // W/m^2 -> kW/mm^2 or W/rad^2 -> kW/mrad^2
		if(m_rectslit || m_circslit){
			coef *= 1.0e+6; // kW/mm^2 -> kW/m^2
		}
	}
	return coef;
}

double SpectraSolver::GetFldAmpCoef()
{
	double coef = 1.0e-7*PI2*QE*CC;
	if(!m_accb[singlee_]){
		coef *= m_bunchelectrons;
	}
	return coef;
}

double SpectraSolver::GetPConvFactor()
{
	return QE*GetFluxCoef()/GetPowerCoef();
}

double SpectraSolver::GetOrbitRadius()
{
    return COEF_BM_RADIUS*m_acc[eGeV_]/m_Bmax;
}

double SpectraSolver::GetAverageFieldSquared(int jxy, bool issec)
{
    double bavsq, Bxy;

    if(m_srctype == CUSTOM || m_srctype == CUSTOM_PERIODIC){
		DataContainer &dcont = m_srctype == CUSTOM ? m_fvsz : m_fvsz1per;
		vector<double> bsq, z;
		dcont.GetArray1D(0, &z);
		dcont.GetArray1D(jxy+1, &bsq);
		for(int n = 0; n < z.size(); n++){
			bsq[n] = bsq[n]*bsq[n];
		}
		Spline bspl;
		bspl.SetSpline((int)z.size(), &z, &bsq);
		bavsq = bspl.Integrate()/(z.back()-z.front());
    }
    else{
        bavsq = 0.0;
        vector<double> &kxy = issec ? m_KxyS[jxy] : m_Kxy[jxy];
        for(int k = 1; k < kxy.size(); k++){
            Bxy = kxy[k]*(double)k/m_lu/COEF_K_VALUE;
            bavsq += Bxy*Bxy*0.5;
        }
    }
    return bavsq;
}

double SpectraSolver::GetEnergyCoherent(double blen_sec, double frac)
{
	double lfrac = sqrt(-log(frac)/PI/PI2);
	double ep = photon_energy(blen_sec*CC/lfrac)*(1<<(m_accuracy[acclimpE_]-1));
    return ep;
}

double SpectraSolver::GetTypicalBunchLength()
{
	double blen = m_acc[bunchlength_]*1.0e-3/CC;
	if(m_isgaussbeam || m_isparticle){
		return blen;
	}
	vector<double> tinv;
	vector<vector<double>> FT;
	if(m_iscurrprof){
		m_currprof.GetFT(0, tinv, FT, 0, &blen);
	}
	else if(m_isEtprof){
		m_Etprof.GetFT(0, tinv, FT, 0, &blen);
	}
	return blen;
}

void SpectraSolver::GetTypicalDivergence(double *xydiv)
{
	xydiv[0] = xydiv[1] = 1.0/m_gamma;
	if(m_isund && !m_ispower){
		double ep = GetE1st();
		double sizexy[2];
		GetNaturalSrcDivSize(ep, xydiv, sizexy);
	}
}

void SpectraSolver::GetNaturalSrcDivSize(double ep, 
	double *divxy, double *sizexy, double *sizeslice, double detune, bool qsize)
{
    double wavel, L;
    double radius, epsilon, dXYdUV = 1, sigmaUV[2] = {0, 0};

	double ec = GetCriticalEnergy();
	if(sizeslice != nullptr && (m_isbm || m_iswiggler)){
		epsilon = GetEpsilonBMWiggler(ep);
		double dqduv = 1.0/(epsilon*m_gamma);
		double bendr = GetOrbitRadius();
		dXYdUV = bendr*0.5*dqduv*dqduv;
		sigmaUV[0] = (0.99+1.58e-4*pow(epsilon, 3.72))*2/Sigma2FWHM;
		sigmaUV[1] = (1.26+0.346*pow(epsilon, 0.91))*2/Sigma2FWHM;
	}

    if(m_isbm){
		double cofactor = sqrt(12.0);
		double Dthetax = m_conf[horizacc_]*0.001;
        radius = GetOrbitRadius();

		divxy[1] = BMWigglerRadiation::GetDivergence(ep/ec)/m_gamma;
		divxy[0] = sqrt(hypotsq(divxy[1], Dthetax/cofactor));
		double sigr = wave_length(ep)/4.0/PI/divxy[1];
		if(sizeslice != nullptr){
			for(int j = 0; j < 2; j++){
				sizeslice[j] = sigmaUV[j]*dXYdUV;
			}
		}
		sizexy[1] = sqrt(hypotsq(sigr, radius*Dthetax*divxy[1]/cofactor));
		sizexy[0] = sqrt(hypotsq(sizexy[1], radius*Dthetax*Dthetax/sqrt(720.0)));
    }
    else if(m_isund){
		wavel = wave_length(ep/(1+detune));
		L = m_lu*(double)(m_N*m_M);
		if(m_issegu && m_issrc2){
			L *= 2.0;
		}
		natural_usrc(L, wavel, divxy, sizexy);
		if(detune < 0){
			int nh = (int)floor(0.5+ep/(1+detune)/GetE1st());
			double Nnu = nh*(m_N*m_M)*detune;
			double rf = (sqrt(1-Nnu)-sqrt(-Nnu))/sqrt(1+detune);
			divxy[0] *= rf;
			double qpk = sqrt(-detune*(1+m_K2)/(1+detune))/m_gamma;
			if(qsize){
				sizexy[0] /= rf;
			}
			else{
				sizexy[0] = min(sizexy[0], wavel/4/PI/qpk);
			}
		}
		divxy[1] = divxy[0];
		sizexy[1] = sizexy[0];
		if (sizeslice != nullptr){
			sizeslice[1] = sizeslice[0] = sizexy[0];
		}
    }
	else{
		natural_wsrc(m_lu, m_N, m_Kxy[0][1], m_Kxy[1][1],
			m_gamma, ep/ec, sizexy, divxy);
		if(sizeslice != nullptr){
			sizeslice[1] = sigmaUV[1]*dXYdUV;
			double xamp = m_lu*m_Kxy[1][1]/PI2/m_gamma;
			sizeslice[0] = sqrt(hypotsq(xamp, sigmaUV[0]*dXYdUV));
		}
	}
}

void SpectraSolver::GetSrcDivSize(double ep,
    double *divxy, double *sizexy, double *Divxy, double *Sizexy,
	double *divrc, double *SizeSlice, double detune, bool qsize)
{
    double L, dtmp[2], prjct_len_xy[] = {0.0, 0.0};
    int j;

    if(m_isund){
        L = m_lu*(double)(m_N*m_M);
        if(m_issegu && m_issrc2){
            L *= 2.0;
        }
        for(j = 0; j < 2; j++){
            prjct_len_xy[j] = L/m_conf[slit_dist_]/2.0*m_center[j];
        }
    }

    GetNaturalSrcDivSize(ep, divxy, sizexy, SizeSlice, detune, qsize);
    if(divrc != nullptr){
		for(int j = 0; j < 2; j++){
			dtmp[j] = divxy[j];
			divxy[j] = (*divrc);
		}
    }
    for(j = 0; j < 2; j++){
		double esize = m_accb[zeroemitt_] ? 0 : m_size[j];
		double ediv =  m_accb[zeroemitt_] ? 0 : m_div[j];
        Sizexy[j] = sqrt(hypotsq(prjct_len_xy[j], esize, sizexy[j]));
        Divxy[j] = sqrt(hypotsq(ediv, divxy[j]));
		if(SizeSlice != nullptr){
			SizeSlice[j] = sqrt(hypotsq(esize, SizeSlice[j]));
		}
    }
    if(divrc != NULL){
		for(int j = 0; j < 2; j++){
			divxy[j] = dtmp[j];
		}
    }
}

void SpectraSolver::GetDegreeOfCoherence4D(
	vector<vector<double>> &vararray, vector<double> &W, double *separability, double cohdeg[])
{
	double wavel = wave_length(m_fixep);
	vector<vector<double>> Wprj[2];
	double Dxy[2], Dqxy[2], dV, tf, sprj, sslice, norm, normxy[2];
	int xymesh[2], qxymesh[2], tmesh[4], n[4], index;

	dV = 1.0;
	for(int j = 0; j < 2; j++){
		Dxy[j] = vararray[j][1]-vararray[j][0];
		Dqxy[j] = vararray[j+2][1]-vararray[j+2][0];
		dV *= Dxy[j]*Dqxy[j];
		tmesh[j] = xymesh[j] = (int)vararray[j].size();
		tmesh[j+2] = qxymesh[j] = (int)vararray[j+2].size();
		Wprj[j].resize(xymesh[j]);
		for(int i = 0; i < xymesh[j]; i++){
			Wprj[j][i].resize(qxymesh[j], 0.0);
		}
	}
	norm = sslice = sprj = tf = 0;
	for(n[0] = 0; n[0] < xymesh[0]; n[0]++){
		for (n[1] = 0; n[1] < xymesh[1]; n[1]++){
			for (n[2] = 0; n[2] < qxymesh[0]; n[2]++){
				for (n[3] = 0; n[3] < qxymesh[1]; n[3]++){
					index = GetIndexMDV(tmesh, n, 4);
					for(int j = 0; j < 2; j++){
						Wprj[j][n[j]][n[j+2]] += W[index]*Dxy[1-j]*Dqxy[1-j];
					}
					tf += W[index]*dV;
				}
			}
		}
	}

	for(int j = 0; j < 2; j++){
		normxy[j] = 0;
		for (n[0] = 0; n[0] < xymesh[j]; n[0]++){
			for (n[1] = 0; n[1] < qxymesh[j]; n[1]++){
				normxy[j] += Wprj[j][n[0]][n[1]]*Wprj[j][n[0]][n[1]]*Dxy[j]*Dqxy[j];
			}
		}
		normxy[j] *= 1.0e+6;
		// (/mm/mrad) -> (/m/rad)
		cohdeg[j] = wavel*normxy[j]/tf/tf;
	}

	for(n[0] = 0; n[0] < xymesh[0]; n[0]++){
		for (n[1] = 0; n[1] < xymesh[1]; n[1]++){
			for (n[2] = 0; n[2] < qxymesh[0]; n[2]++){
				for (n[3] = 0; n[3] < qxymesh[1]; n[3]++){
					index = GetIndexMDV(tmesh, n, 4);
					double wbyp = Wprj[0][n[0]][n[2]]*Wprj[1][n[1]][n[3]]/tf;
					sprj += (wbyp-W[index])*(wbyp-W[index]);
					sslice += W[index]*W[index];
					norm += W[index]*W[index]*dV;
				}
			}
		}
	}
	norm *= 1.0e+12;
	// (/mm^2/mrad^2) -> (/m^2/rad^2)

	*separability = 1.0-sqrt(sprj/sslice);
	cohdeg[2] = wavel*wavel*norm/tf/tf;
}

void SpectraSolver::GetDegreeOfCoherence2D(
	vector<vector<double>> &vararray, vector<double> &W, double *cohdeg)
{
	double wavel = wave_length(m_fixep);
	double Dxy[2], tf, normxy;
	int xymesh[2], n[2];

	for(int j = 0; j < 2; j++){
		Dxy[j] = vararray[j][1]-vararray[j][0];
		xymesh[j] = (int)vararray[j].size();
	}

	tf = normxy = 0;
	for (n[1] = 0; n[1] < xymesh[1]; n[1]++){
		for (n[0] = 0; n[0] < xymesh[0]; n[0]++){
			int index = n[1]*xymesh[0]+n[0];
			normxy += W[index]*W[index]*Dxy[0]*Dxy[1];
			tf += W[index]*Dxy[0]*Dxy[1];
		}
	}
	normxy *= 1.0e+6;
	// (/mm/mrad) -> (/m/rad)
	*cohdeg = wavel*normxy/tf/tf;

}

double SpectraSolver::GetEpsilonBMWiggler(double ep)
{
	double ec = GetCriticalEnergy();
	double epsilon = ep/ec*0.75;
	return pow(epsilon, 1.0/3.0);
}

void SpectraSolver::GetWignerType(
	vector<int> &wigtypes, vector<vector<int>> &indices)
{
	wigtypes.clear();
	indices.clear();
	if(contains(m_calctype, menu::XXpslice)){
		wigtypes.push_back(WignerFuncType4DX);
		indices.push_back(vector<int> {SrcVarX, SrcVarXp});
	}
	else if(contains(m_calctype, menu::XXpprj)){
		wigtypes.push_back(WignerFuncType2DX);
		indices.push_back(vector<int> {SrcVarX, SrcVarXp});
	}
	else if(contains(m_calctype, menu::YYpslice)){
		wigtypes.push_back(WignerFuncType4DY);
		indices.push_back(vector<int> {SrcVarY, SrcVarYp});
	}
	else if(contains(m_calctype, menu::YYpprj)){
		wigtypes.push_back(WignerFuncType2DY);
		indices.push_back(vector<int> {SrcVarY, SrcVarYp});
	}
	else if(contains(m_calctype, menu::XXpYYp) 
		|| contains(m_calctype, menu::Wrel)){
		wigtypes.push_back(WignerFuncTypeXY);
		wigtypes.push_back(WignerFuncTypeXpYp);
		indices.push_back(vector<int> {SrcVarX, SrcVarY});
		indices.push_back(vector<int> {SrcVarXp, SrcVarYp});
	}
	else if(contains(m_calctype, menu::Wslice)){
		wigtypes.push_back(WignerFuncType4DX);
	}
	else if(contains(m_calctype, menu::WprjX)){
		wigtypes.push_back(WignerFuncType2DX);
	}
	else if(contains(m_calctype, menu::WprjY)){
		wigtypes.push_back(WignerFuncType2DY);
	}
}

bool SpectraSolver::IsMonteCarlo()
{
	if(IsPreprocess()){
		return false;
	}
	if(m_iscoherent){
		return false;
	}
	if(m_accsel[bunchtype_] == CustomParticle){
		return true;
	}
	if(m_is3dsrc){
		return true;
	}
	return false;
}

void SpectraSolver::GetSpectrum(
	vector<double> &energy, vector<vector<double>> &flux,
	int layer, int rank, int mpiprocesses,
	vector<string> &subresults, vector<string> &categories)
{
	if(m_iscoherent){
		Trajectory trajec(*this);
		FilterOperation filter(*this);
		CoherentRadiationCtrl cohctrl(*this, &trajec, &filter);
		cohctrl.GetValues(layer, &flux, rank, mpiprocesses);
		energy = m_eparray;
		cohctrl.GetFELData(subresults, categories);
	}
	else if(m_isfar && m_isund && !m_confb[wiggapprox_]){
		UndulatorFluxFarField ufar(*this, layer, rank, mpiprocesses);
		ufar.GetUSpectrum(&energy, &flux, layer, rank, mpiprocesses);
	}
	else if(contains(m_calctype, menu::tflux)){
		FilterOperation filter(*this);
		BMWigglerRadiation bmwig(*this, &filter);
		double fcoef = GetFluxCoef();
		double tf[3];
		flux.resize(4);
		energy = m_eparray;
		for(int j = 0; j < 4; j++){
			flux[j].resize(m_eparray.size());
		}
		for(int n = 0; n < m_eparray.size(); n++){
			bmwig.TotalFlux(m_eparray[n], tf);
			flux[0][n] = tf[0]*fcoef;
			flux[1][n] = tf[1]*fcoef;
			flux[2][n] = flux[3][n] = 0;
		}
	}
	else if(m_isfar){
		DensityFixedPoint densfix(*this, nullptr, nullptr);
		SpatialConvolution spconv(*this, &densfix, layer, rank, mpiprocesses);
		spconv.GetValue(&flux);
		energy = m_eparray;
	}
	else if(contains(m_calctype, menu::wigner)){
		WignerFunctionCtrl wigctrl(*this, layer+1);
		vector<double> W;
		vector<vector<double>> XYtmp;
		flux.resize(1);
		flux[0].resize(m_eparray.size());
		m_calcstatus->SetSubstepNumber(layer, (int)ceil((double)m_eparray.size()/mpiprocesses));
		for(int n = 0; n < m_eparray.size(); n++){
			if(rank != n%mpiprocesses){
				continue;
			}
			wigctrl.SetPhotonEnergy(m_eparray[n]);
			wigctrl.GetPhaseSpaceProfile(XYtmp, W);
			flux[0][n] = W[0];
			if (m_rank == 0){
				m_calcstatus->AdvanceStep(0);
			}
		}
		if(mpiprocesses > 1){
			f_GatherMPI(1, flux, rank, mpiprocesses);
		}
		energy = m_eparray;
		return;
	}
	else{
		Trajectory trajec(*this);
		DensityFixedPoint densfix(*this, &trajec, nullptr);
		SpatialConvolution spconv(*this, &densfix, layer, rank, mpiprocesses);
		spconv.GetValue(&flux);
		energy = m_eparray;
#ifdef _CPUTIME
		densfix.GetMeasuredTime(m_rlabel, m_cputime);
#endif
	}

	vector<double> ftmp(4);
	for(int n = 0; n < energy.size(); n++){
		for(int j = 0; j < 4; j++){
			ftmp[j] = flux[j][n];
		}
		stokes(ftmp);
		for(int j = 0; j < 4; j++){
			flux[j][n] = ftmp[j];
		}
	}
	if(m_isfar && contains(m_calctype, menu::fdensa)){
		double divxy[2], sizexy[2], Divxy[2], Sizexy[2], SizeSlice[2], srcarea;
		vector<double> gabrill(flux[0]);
		for(int n = 0; n < energy.size(); n++){
			GetSrcDivSize(energy[n], divxy, sizexy, Divxy, Sizexy, nullptr, SizeSlice);
			srcarea = SizeSlice[0]*SizeSlice[1]*PI2*1.0e+6;
			gabrill[n] /= srcarea;
		}
		flux.insert(flux.begin()+1, gabrill);
	}
	if(m_isfilter){
		FilterOperation filter(*this);
		vector<double> fflux(energy.size());
		for(int n = 0; n < energy.size(); n++){
			fflux[n] = flux[0][n]*filter.GetTransmissionRateF(energy[n]);
		}
		flux.push_back(fflux);
	}
}

void SpectraSolver::GetSpatialProfile(
	vector<vector<double>> &xy, vector<vector<vector<double>>> &dens,
	int layer, int rank, int mpiprocesses,
	vector<string> &subresults, vector<string> &categories)
{
	Trajectory trajec(*this);
	FilterOperation filter(*this);
	bool alongxy = contains(m_calctype, menu::along);

	if(m_iscoherent){
		vector<vector<double>> xyobs, density;
		CoherentRadiationCtrl cohctrl(*this, &trajec, &filter);
		ArrangeMeshSettings(xy, xyobs);
		cohctrl.GetCohSpatialProfile(layer, &xyobs, &density, rank, mpiprocesses);
		int nitems = (int)density[0].size();
		int mesh[2] = {(int)xy[0].size(), (int)xy[1].size()};
		dens.resize(nitems);
		if(alongxy){
			dens.resize(2);
			for(int j = 0; j < 2; j++){
				dens[j].resize(nitems);
				for (int i = 0; i < nitems; i++){
					dens[j][i].resize(mesh[j]);
					for (int n = 0; n < mesh[j]; n++){
						dens[j][i][n] = density[j*mesh[0]+n][i];
					}
				}
			}
		}
		else{
			for (int i = 0; i < nitems; i++){
				dens[i].resize(mesh[0]);
				for (int n = 0; n < mesh[0]; n++){
					dens[i][n].resize(mesh[1]);
					for (int m = 0; m < mesh[1]; m++){
						dens[i][n][m] = density[m*mesh[0]+n][i];
					}
				}
			}
		}
		cohctrl.GetFELData(subresults, categories);
	}
	else{
		DensityFixedPoint densfix(*this, &trajec, &filter);
		if(alongxy){
			if(rank == 0){
				m_calcstatus->SetSubstepNumber(layer, 2);
			}
			for(int j = 0; j < 2; j++){
				vector<double> xytmp[2];
				vector<vector<vector<double>>> denstmp;
				vector<vector<double>> dens1d;
				SpatialConvolutionFFT spfft(j,
					*this, &densfix, layer+1, rank, mpiprocesses);
				spfft.Run2DConvolution();
				spfft.GetXYArrays(&xytmp[0], &xytmp[1]);
				xy[j] = xytmp[j];
				spfft.GetValues(&denstmp);
				int nitems = (int)denstmp.size();
				dens1d.resize(nitems);
				for(int i = 0; i < nitems; i++){
					dens1d[i].resize(xytmp[j].size());
					for(int n = 0; n < xytmp[j].size(); n++){
						if(j == 0){
							dens1d[i][n] = denstmp[i][n][0];
						}
						else{
							dens1d[i][n] = denstmp[i][0][n];
						}
					}
				}
				dens.push_back(dens1d);
				if(rank == 0){
					m_calcstatus->AdvanceStep(layer);
				}
			}
		}
		else{
			SpatialConvolutionFFT spfft(SPATIAL_CONVOLUTION_MESH, 
				*this, &densfix, layer, rank, mpiprocesses);
			spfft.Run2DConvolution();
			spfft.GetXYArrays(&xy[0], &xy[1]);
			spfft.GetValues(&dens);
			if(contains(m_calctype, menu::meshrphi)){
				vector<vector<double>> xyvar(xy);
				vector<vector<vector<double>>> densr(dens);
				double rpini[2], drp[2], dummy;
				int mesh[2];
				for(int j = 0; j < 2; j++){
				    GetGridContents(j, true, &rpini[j], &drp[j], &dummy, &mesh[j], -1, false);
					if(m_confsel[defobs_] == ObsPointAngle && j == 0){
						rpini[j] /= m_conf[slit_dist_];
						drp[j] /= m_conf[slit_dist_];
					}
					xy[j].resize(mesh[j]);
					for(int n = 0; n < mesh[j]; n++){
						xy[j][n] = rpini[j]+drp[j]*n;
						if(fabs(xy[j][n]) < drp[j]*DXY_LOWER_LIMIT){
							xy[j][n] = 0;
						}
					}
				}
				for(int i = 0; i < dens.size(); i++){
					dens[i].resize(mesh[0]);
					for(int n = 0; n < mesh[0]; n++){
						dens[i][n].resize(mesh[1]);
					}
				}
				double xyr[2], dindex[2], dxy[2];
				for(int j = 0; j < 2; j++){
					dxy[j] = xyvar[j][1]-xyvar[j][0];
				}
				for(int n = 0; n < mesh[0]; n++){
					for(int m = 0; m < mesh[1]; m++){
						double phi = xy[1][m]*DEGREE2RADIAN;
						xyr[0] = xy[0][n]*cos(phi);
						xyr[1] = xy[0][n]*sin(phi);
						for(int j = 0; j < 2; j++){
							dindex[j] = (xyr[j]-xyvar[j][0])/dxy[j];
						}
						for(int i = 0; i < dens.size(); i++){
							dens[i][n][m] = lagrange2d(densr[i], dindex, nullptr);
						}
					}
				}
			}
		}
	}
	if(contains(m_calctype, menu::fdensa) || contains(m_calctype, menu::fdenss)){
		f_ToStokes(xy, dens);
	}
}

void SpectraSolver::GetSurfacePowerDensity(
		vector<vector<double>> &obs, vector<double> &dens,
		int layer, int rank, int mpiprocesses)
{
	vector<vector<double>> xyz, exyz, value;
	GetSPDConditions(obs, xyz, exyz);

	Trajectory trajec(*this);
	FilterOperation filter(*this);
	dens.resize(xyz.size());
	m_calcstatus->SetSubstepNumber(layer, (int)xyz.size());
	vector<vector<double>> items;
	if(mpiprocesses > 1){
		items.resize(1);
		items[0].resize(xyz.size());
	}
	for(int n = 0; n < xyz.size(); n++){
		if(rank != n%mpiprocesses){
			if(rank == 0){
				m_calcstatus->AdvanceStep(layer);
			}
			continue;
		}
		m_conf[slit_dist_] = xyz[n][2];
		for(int j = 0; j < 2; j++){
			m_confv[xyfix_][j] = xyz[n][j]*1000.0;
			// m -> mm
		}
		Initialize(); // to modify electron beam projection
		SetObservation(); // to modify the observation position
		DensityFixedPoint densfix(*this, &trajec, &filter);
		SpatialConvolution spconv(*this, &densfix, layer+1);
		densfix.SetObserverPositionAngle(xyz[n], exyz[n]);
		spconv.GetValue(&value);
		dens[n] = value[0][0];
		if (mpiprocesses > 1){
			items[0][n] = dens[n];
		}
		m_calcstatus->AdvanceStep(layer);
	}
	if(mpiprocesses > 1){
		f_GatherMPI(1, items, rank, mpiprocesses);
		for (int n = 0; n < xyz.size(); n++){
			dens[n] = items[0][n];
		}
	}
}

void SpectraSolver::f_ToStokes(
	vector<vector<double>> &xy, vector<vector<vector<double>>> &dens)
{
	vector<double> ftmp(4);
	int nf;
	vector<int> mf;

	bool alongxy = contains(m_calctype, menu::along);
	if(alongxy){
		nf = 2;
		mf.resize(2);
		for(int j = 0; j < 2; j++){
			mf[j] = (int)xy[j].size();
		}
	}
	else{
		nf = (int)xy[0].size();
		mf.resize(nf, (int)xy[1].size());
	}
	for(int n = 0; n < nf; n++){
		for (int m = 0; m < mf[n]; m++){
			for (int j = 0; j < 4; j++){
				if(alongxy){
					ftmp[j] = dens[n][j][m];
				}
				else{
					ftmp[j] = dens[j][n][m];
				}
			}
			stokes(ftmp);
			for (int j = 0; j < 4; j++){
				if(alongxy){
					dens[n][j][m] = ftmp[j];
				}
				else{
					dens[j][n][m] = ftmp[j];
				}
			}
		}
	}
}

void SpectraSolver::GetWignerFunction(
	vector<vector<double>> &XY, vector<double> &W,
	int layer, int rank, int mpiprocesses)
{
	WignerFunctionCtrl wigctrl(*this, layer);
	vector<vector<double>> XYtmp;
	wigctrl.GetPhaseSpaceProfile(XYtmp, W, rank, mpiprocesses);

	vector<int> wigtypes;
	vector<vector<int>> indices;
	GetWignerType(wigtypes, indices);
	XY.clear();
	for(int j = 0; j < indices.size(); j++){
		for (int k = 0; k < indices[j].size(); k++){
			XY.push_back(XYtmp[indices[j][k]]);
			XY.back() *= 1000.0; // m, rad -> mm, mrad
		}
	}
}

void SpectraSolver::GetFixedPoint(
	vector<double> &values, int layer, int rank, int mpiprocesses)
{
	if(m_ispower){
		Trajectory trajec(*this);
		FilterOperation filter(*this);
		DensityFixedPoint densfix(*this, &trajec, &filter);
		SpatialConvolution spconv(*this, &densfix, layer, rank, mpiprocesses);
		vector<vector<double>> vtmp;
		spconv.GetValue(&vtmp);
		values.resize(vtmp.size());
		for(int j = 0; j < vtmp.size(); j++){
			values[j] = vtmp[j][0];
		}
	}
	else if(contains(m_calctype, menu::wigner)){
		vector<vector<double>> XY;
		GetWignerFunction(XY, values, layer, rank, mpiprocesses);
	}
	else if(contains(m_calctype, menu::simpcalc)){
		vector<double> vararray;
		vector<vector<double>> items;
		vector<string> details;
		KValueOperation kv(*this);
		kv.GetSrcPerformance(vararray, items, details);
		values.resize(items.size());
		for(int j = 0; j < items.size(); j++){
			values[j] = items[j][0];
		}
	}
	else{
		vector<double> etmp;
		vector<vector<double>> vtmp;
		vector<string> dummy[2];
		m_confv[erange_][0] = m_confv[erange_][1] = m_fixep;
		SetEnergyPoints(true);
		GetSpectrum(etmp, vtmp, layer, rank, mpiprocesses, dummy[0], dummy[1]);
		values.resize(vtmp.size());
		for(int j = 0; j < vtmp.size(); j++){
			values[j] = vtmp[j][0];
		}
	}
}

void SpectraSolver::RunSingle(int &dimension,	
	vector<string> &titles, vector<string> &units,
	vector<vector<double>> &vararray, vector<vector<double>> &data,
	vector<string> &details, vector<int> &nvars, 
	vector<string> &subresults, vector<string> &categories)
	// data[item][independent variable(multi dimension)]
{
	subresults = vector<string> {""};
	categories = vector<string> {OutputLabel};

	f_GetTitles(titles, units);
	m_suppltitle.clear(); m_suppldata.clear();

	if(m_ispreproc){
		dimension = 1;
		vararray.resize(1);
		categories[0] = m_pptype;
	}
    if(m_pptype == PPBetaLabel 
		|| m_pptype == PPFDlabel
		|| m_pptype == PP1stIntLabel
		|| m_pptype == PP2ndIntLabel
		|| m_pptype == PPPhaseErrLabel
		|| m_pptype == PPRedFlux)
	{
		Trajectory trajec(*this, true);
		if(m_pptype == PPFDlabel){
			data.resize(3);
		}
		else if(m_pptype == PPPhaseErrLabel){
			data.resize(1);
		}
		else{
			data.resize(2);
		}
		if(m_pptype == PPBetaLabel){
			trajec.TransferTwissParamaters(nullptr, nullptr, &data);
			trajec.GetZCoordinate(&vararray[0]);
		}
		else if(m_pptype == PPFDlabel){
			trajec.GetTrajectory(vararray[0], &data, nullptr, nullptr);
		}
		else if(m_pptype == PP1stIntLabel){
			trajec.GetTrajectory(vararray[0], nullptr, &data, nullptr);
		}
		else if(m_pptype == PP2ndIntLabel){
			trajec.GetTrajectory(vararray[0], nullptr, nullptr, &data);
		}
		else{
			vector<vector<double>> temp(2);
			vector<double> zpeak;
			double thresh = m_ppconf[thresh_];
			string coord = m_ppconfsel[zcoord_];
			thresh *= 0.01;
			if(m_pptype == PPPhaseErrLabel){
				double phaseerr = trajec.GetPhaseError(zpeak, data[0], thresh, temp);
				m_suppltitle.push_back("RMS "+PPPhaseErrLabel+" (deg.)");
				m_suppldata.push_back(phaseerr);
			}
			else{
				trajec.GetPhaseError(zpeak, temp[0], thresh, data);
			}
			if(coord == PhaseErrZPole || m_pptype == PPRedFlux){
				vararray[0].resize(data[0].size());
				for(int n = 0; n < vararray[0].size(); n++){
					vararray[0][n] = n+1;
				}
			}
			else{
				vararray[0] = zpeak;
			}
		}
        return;
    }
    else if(m_pptype == PPTransLabel)
	{
		data.resize(1);
		FilterOperation filter(*this, m_pptype == PPAbsLabel);
		filter.GetTransmissionData(vararray[0], data[0]);
        return;
    }
    else if(m_pptype == PPAbsLabel)
	{
		data.resize(1);
		FilterOperation filter(*this, m_pptype == PPAbsLabel);
		filter.GetTransmissionData(vararray[0], data[0]);
		GenericAbsorber absorber(m_absorbers, m_materials);
		for (int n = 0; n < vararray[0].size(); n++){
			data[0][n] = absorber.GetTotalAbsorption(vararray[0][n]);
		}
        return;
    }

	bool iscmd = false;
	bool isprop = false;
	if(IsSkipOutput()){
		if(contains(m_calctype, menu::propagate)){
			isprop = true;
		}
		else{
			iscmd = true;
		}
		subresults.clear();
		categories.clear();
		titles.clear();
		units.clear();
		vararray.clear();
		data.clear();
		dimension = 0;
	}
	else if(m_isvpdens){
		FilterOperation filter(*this);
		VolumePowerDensity vpdens(*this, &filter);
		vector<vector<vector<double>>> volpdens;
		vararray.resize(3);
		vpdens.GetVolumePowerDensity(vararray, volpdens);
		dimension = 3;
		data.resize(1);
		Copy3d(volpdens, data[0]);
	}
	else if(contains(m_calctype, menu::spdens)){
		data.resize(1);
		GetSurfacePowerDensity(vararray, data[0], 0, m_rank, m_mpiprocesses);
		if(IsFixedPoint()){
			dimension = 0;
		}
		else{
			dimension = 2;
		}
	}
	else if(contains(m_calctype, menu::spatial) 
		|| contains(m_calctype, menu::sprof)){
		vector<vector<vector<double>>> dens;
		if(contains(m_calctype, menu::along)){
			vector<vector<double>> vartmp(2);
			GetSpatialProfile(vartmp, dens, 0, m_rank, m_mpiprocesses, subresults, categories);

			if(m_srctype == BM && m_isfar){
				vartmp[0].resize(0);
			}
			else{
				details.push_back("Along x");
				nvars.push_back((int)vartmp[0].size());
			}
			details.push_back("Along y");
			nvars.push_back((int)vartmp[1].size());

			vararray.resize(1); vararray[0] = vartmp[0];
			vararray[0].insert(vararray[0].end(), vartmp[1].begin(), vartmp[1].end());
			dimension = 1;

			int nitems = (int)dens[0].size(); 
			data.resize(nitems);
			for(int i = 0; i < nitems; i++){
				data[i].resize(vararray[0].size());
			}
			for(int j = 0; j < 2; j++){
				for(int n = 0; n < (int)vartmp[j].size(); n++){
					int nt = n+j*(int)vartmp[0].size();
					for(int i = 0; i < nitems; i++){
						data[i][nt] = dens[j][i][n];
					}
				}
			}
		}
		else{
			vararray.resize(2);
			GetSpatialProfile(vararray, dens, 0, m_rank, m_mpiprocesses, subresults, categories);
			dimension = 2;
			data.resize(dens.size());
			for (int j = 0; j < dens.size(); j++){
				Copy2d(dens[j], data[j]);
			}
		}
	}
	else if(m_isenergy){
		vararray.resize(1);
		if(contains(m_calctype, menu::simpcalc)){
			vector<string> details;
			KValueOperation kv(*this);
			kv.GetSrcPerformance(vararray[0], data, details);
		}
		else{
			GetSpectrum(vararray[0], data, 0, m_rank, m_mpiprocesses, subresults, categories);
			if(m_confv[erange_][0] > m_confv[erange_][1]){
				sort(vararray[0], data, (int)vararray[0].size(), false);
			}
		}
		dimension = 1;
	}
	else if(m_iscoherent){
		Trajectory trajec(*this);
		FilterOperation filter(*this);
		CoherentRadiationCtrl cohctrl(*this, &trajec, &filter);
		if(m_istime){
			cohctrl.GetValues(0, &data, m_rank, m_mpiprocesses);
			vararray.resize(1);
			vararray[0] = m_tarray;
			vararray[0] *= 1.0e+15; // s -> fs
			dimension = 1;
		}
		else{ // fixed point
			dimension = 0;
			vector<vector<double>> values;
			cohctrl.GetValues(0, &values, m_rank, m_mpiprocesses);
			if(contains(m_calctype, menu::fdensa) 
				|| contains(m_calctype, menu::fdenss)
				|| contains(m_calctype, menu::pflux))
			{
				vector<double> fd(4);
				for(int j = 0; j < 4; j++){
					fd[j] = values[j][0];
				}
				stokes(fd);
				for(int j = 0; j < 4; j++){
					values[j][0] = fd[j];
				}
			}
			for (int j = 0; j < values.size(); j++){
				data.push_back(vector<double> {values[j]});
			}
		}
		cohctrl.GetFELData(subresults, categories);
	}
	else if(contains(m_calctype, menu::Kvalue)){
		dimension = 1;
		KValueOperation kv(*this);
		vararray.resize(1);
		if(m_ispower){
			kv.GetPower(vararray[0], data);
		}
		else if(contains(m_calctype, menu::fluxfix)){
			kv.GetFixedFlux(vararray[0], data);
		}
		else{
			kv.GetSrcPerformance(vararray[0], data, details);
			if(details.size() > 0){
				int nvar = (int)(vararray[0].size()/details.size());
				nvars.resize(details.size(), nvar);
			}
		}
	}
	else if(contains(m_calctype, menu::wigner)){
		data.resize(1);
		if(!contains(m_calctype, menu::Wrel) && m_confb[CMD_]){
			m_calcstatus->SetTargetPoint(0, 0.5);
		}

		GetWignerFunction(vararray, data[0], 0, m_rank, m_mpiprocesses);

		double separability = 0, cohdeg[3];
		if(contains(m_calctype, menu::XXpYYp) || contains(m_calctype, menu::Wrel)){
			GetDegreeOfCoherence4D(vararray, data[0], &separability, cohdeg);
			f_SetSuppleData(m_calctype, separability, cohdeg);
		}
		if(contains(m_calctype, menu::XXpprj) || contains(m_calctype, menu::YYpprj)){
			GetDegreeOfCoherence2D(vararray, data[0], &cohdeg[0]);
			f_SetSuppleData(m_calctype, separability, cohdeg);
		}

		if(contains(m_calctype, menu::Wrel)){
			dimension = 0;
			data.resize(4);
			for(int j = 0; j < 4; j++){
				data[j].resize(1);
			}
			data[0][0] = separability;
			for(int j = 0; j < 3; j++){
				data[j+1][0] = cohdeg[j];
			}
		}
		else{
			dimension = (int)vararray.size();
			iscmd = m_confb[CMD_];
			m_calcstatus->SetCurrentOrigin(0);
			m_calcstatus->ResetCurrentStep(0);
			m_calcstatus->SetTargetPoint(0, 1.0);
		}
	}
	else if(IsFixedPoint()){
		vector<double> values;
		dimension = 0;
		GetFixedPoint(values, 0, m_rank, m_mpiprocesses);
		for(int j = 0; j < values.size(); j++){
			data.push_back(vector<double> {values[j]});
		}
	}

	if(iscmd){
		HGModalDecompCtrl cmdctrl(*this);
		if(data.size() > 0){
			cmdctrl.Solve(subresults, categories, &vararray, &data[0]);
		}
		else{
			cmdctrl.Solve(subresults, categories);
		}
	}
	if(isprop){
		WignerPropagator wigprop(*this);
		wigprop.Propagate(subresults, categories);
	}
}

void SpectraSolver::GetSuppleData(vector<string> &titles, vector<double> &data)
{
	titles = m_suppltitle;
	data = m_suppldata;
}

void SpectraSolver::MeasureTime(int index)
{
	if(index < 0){
		m_rtime[0] = chrono::system_clock::now();
	}
	else{
		if(index == 0){
			m_nrep++;
		}
		m_rtime[1] = chrono::system_clock::now();
		m_cputime[index] += static_cast<double>(chrono::duration_cast<chrono::microseconds>(m_rtime[1]-m_rtime[0]).count())*1e-6;
	}
}

void SpectraSolver::GetMeasuredTime(vector<string> &label, vector<double> &rtime, bool appendn)
{
	label = m_rlabel;
	rtime = m_cputime;
	if(appendn){
		label.push_back("Number of Invocation");
		rtime.push_back(m_nrep);
	}
}

//---------- private functions ----------
void SpectraSolver::f_SetAutoRange()
{
	if(m_srctype == FIELDMAP3D || m_srctype == CUSTOM){
		return;
	}
	if(m_confb[autoe_]){
		double range = 4.0;
		double erange[2];
		if(m_isund){
			if(contains(m_calctype, menu::allharm)){
				double Krange[2];
				f_GetKrange(Krange);
				m_Bmax = Krange[1]/m_lu/COEF_K_VALUE;
				m_K2 = Krange[1]*Krange[1]/2;
				m_confv[erange_][0] = GetE1st();
				m_confv[erange_][1] = round(GetCriticalEnergy()*2, false, 1);
				m_conf[emesh_] = 100;
				return;
			}
			double e1st = GetE1st(m_gtcenter);
			double dE = range*e1st/(m_N*m_M);
			if(contains(m_calctype, menu::wigner)){
				erange[0] = m_conf[hfix_]*GetE1st(m_gttypical);
				erange[1] = m_conf[hfix_]*e1st;
			}
			else{
				if(m_confv[hrange_][0] > m_confv[hrange_][1]){
					swap(m_confv[hrange_][0], m_confv[hrange_][1]);
				}
				erange[0] = m_confv[hrange_][0]*GetE1st(m_gtmax);
				erange[1] = m_confv[hrange_][1]*e1st;
				dE *= 4;
			}
			erange[0] = max(e1st/10, erange[0]/(1+2*range*m_acc[espread_])-dE);
			erange[1] = erange[1]*(1+2*range*m_acc[espread_])+dE;
			for(int j = 0; j < 2; j++){
				m_confv[erange_][j] = round(erange[j], 1, j == 0);
			}
			m_conf[de_] = sqrt(hypotsq(2*m_acc[espread_], 0.5/(m_N*m_M)))*e1st;
			if(contains(m_calctype, menu::wigner)){
				m_conf[de_] *= 0.2;
			}
			else{
				m_conf[de_] *= 0.1;
			}
			m_conf[de_] = round(m_conf[de_], 0, true);
		}
		else{
			double ec = round(GetCriticalEnergy(), 0, false);
			m_confv[erange_][0] = ec*0.001;
			m_confv[erange_][1] = ec*10.0;
			m_conf[emesh_] = 100;
		}
	}
	if(m_confb[autot_]){
		double qpk = 0, range;
		double divxy[2], sizexy[2], Divxy[2], Sizexy[2];
		if(contains(m_calctype, menu::pdensa) || contains(m_calctype, menu::pdenss)){
			double rdiv = 10;
			for(int j = 0; j < 2; j++){
				if(m_isbm){
					Divxy[j] = 1/m_gamma;
				}
				else{
					Divxy[j] = m_GT[j]/m_gamma;
				}
				Sizexy[j] = sqrt(hypotsq(m_Esize[j], Divxy[j]*m_conf[slit_dist_]));
				Divxy[j] = Sizexy[j]/m_conf[slit_dist_];
				sizexy[j] = Sizexy[j]/rdiv;
				divxy[j] = Divxy[j]/rdiv;
			}
			range = 2;
		}
		else{
			double ep = m_conf[efix_];
			double detune = 0;
			if(m_isund){
				double e1st = GetE1st();
				if(contains(m_calctype, menu::srcpoint)){
					detune = m_conf[detune_];
					ep = m_conf[hfix_]*e1st*(1.0+m_conf[detune_]);
				}
				else{
					if(m_confb[normenergy_]){
						detune = m_conf[nefix_]-floor(0.5+m_conf[nefix_]);
					}
					else{
						double dnh = floor(0.5+m_conf[efix_]/e1st);
						detune = m_conf[efix_]/e1st-dnh;
					}
				}
				if(detune < 0){
					qpk = sqrt((1+m_K2)*(-detune)/(1+detune))/m_gamma;
				}
			}
			GetSrcDivSize(ep, divxy, sizexy, Divxy, Sizexy, nullptr, nullptr, detune);
			double rdiv = 3;
			double sizeorg[2];
			range = 4;
			for(int j = 0; j < 2; j++){
				sizeorg[j] = sizexy[j];
				sizexy[j] = Sizexy[j]/rdiv;
				divxy[j] = Divxy[j]/rdiv;
			}
			if(contains(m_calctype, menu::srcpoint) && m_isund && detune < 0){
				double dumdiv[2], dumsize[2], dumDiv[2];
				GetSrcDivSize(ep, dumdiv, dumsize, dumDiv, Sizexy, nullptr, nullptr, detune, true);
			}
			if(contains(m_calctype, menu::srcpoint) && m_isund){
				for(int j = 0; j < 2; j++){ // expand the size to cover rapid oscillation
					Sizexy[j] = sqrt(hypotsq(Sizexy[j], 2*sizeorg[j]));
				}
			}
		}
		for(int j = 0; j < 2; j++){
			Sizexy[j] *= range;
			Divxy[j] *= range;
			Divxy[j] += qpk;
		}
		vector<int> rangeidx;
		if(contains(m_calctype, menu::srcpoint)){
			if(m_iswiggler || m_isbm){
				double Dxp = m_conf[horizacc_]*1e-3/2;
				Divxy[0] = min(Divxy[0], Dxp+m_div[0]*range);
			}
			rangeidx = vector<int> {Xrange_, Xprange_, Yrange_, Yprange_};
		}
		else{
			rangeidx = vector<int> {xrange_, qxrange_, yrange_, qyrange_};
			for(int j = 0; j < 2; j++){
				Sizexy[j] = sqrt(hypotsq(Sizexy[j], Divxy[j]*m_conf[slit_dist_]));
				sizexy[j] = sqrt(hypotsq(sizexy[j], divxy[j]*m_conf[slit_dist_]));
				Divxy[j] = Sizexy[j]/m_conf[slit_dist_];
			}
		}
		vector<double> ranges {Sizexy[0], Divxy[0], Sizexy[1], Divxy[1]};
		for(int j = 0; j < 4; j++){
			m_confv[rangeidx[j]][1] = round(ranges[j]*1e3, 1, false);
			m_confv[rangeidx[j]][0] = -m_confv[rangeidx[j]][1];
		}
		if(contains(m_calctype, menu::srcpoint)){
			vector<int> pointsidx {Xmesh_, Xpmesh_, Ymesh_, Ypmesh_};
			vector<double> deltas{sizexy[0], divxy[0], sizexy[1], divxy[1]};
			for(int j = 0; j < 4; j++){
				m_conf[pointsidx[j]] = max(41, 2*(int)round(ranges[j]/deltas[j], 1, false)+1);
			}
		}
		else{
			vector<int> pointsidx {xmesh_, ymesh_};
			for(int j = 0; j < 2; j++){
				m_conf[pointsidx[j]] = 2*round(Sizexy[j]/sizexy[j], 1, false)+1;
			}
			m_confv[rrange_][0] = m_confv[qrange_][1] = 0;
			m_confv[rrange_][1] = round(sqrt(hypotsq(Sizexy[0], Sizexy[1]))*1e3, 1, false);
			m_confv[qrange_][1] = round(sqrt(hypotsq(Divxy[0], Divxy[1]))*1e3, 1, false);
			m_conf[qphimesh_] = round(max(Sizexy[0]/sizexy[0], Sizexy[1]/sizexy[1]), 1, false);
			m_confv[phirange_][0] = 0;
			m_confv[phirange_][1] = 360;
			m_conf[phimesh_] = 41;
		}
	}
}

void SpectraSolver::f_SetSuppleData(string calctype, double separability, double cohdeg[])
{
	if(contains(calctype, menu::XXpYYp) || contains(calctype, menu::Wrel)){
		m_suppltitle.push_back(TitleLablesDetailed[Correlation_]);
		m_suppltitle.push_back(TitleLablesDetailed[DegCohX_]);
		m_suppltitle.push_back(TitleLablesDetailed[DegCohY_]);
		m_suppltitle.push_back(TitleLablesDetailed[DegCoh_]);
		m_suppldata.push_back(separability);
		for(int j = 0; j < 3; j++){
			m_suppldata.push_back(cohdeg[j]);
		}
	}
	if(contains(calctype, menu::XXpprj) || contains(calctype, menu::YYpprj)){
		stringstream ss;
		int idx = contains(calctype, menu::XXpprj) ? DegCohX_ : DegCohY_;
		m_suppltitle.push_back(TitleLablesDetailed[idx]);
		m_suppldata.push_back(cohdeg[0]);
	}
}

double SpectraSolver::f_GetE1stBase(double Kgt2)
{
    return COEF_E1ST*m_acc[eGeV_]*m_acc[eGeV_]/m_lu/(1.0+Kgt2);
}

void SpectraSolver::f_GetTitles(vector<string> &titles, vector<string> &units)
{
	if(contains(m_calctype, menu::CMD)){
		titles.clear();
		units.clear();
		return;
	}
	vector<int> itemindices;
	GetOutputItemsIndices(itemindices);
	titles.resize(itemindices.size());
	units.resize(itemindices.size());
	for(int i = 0; i < itemindices.size(); i++){
		titles[i] = TitleLablesDetailed[itemindices[i]];
		units[i] = UnitLablesDetailed[itemindices[i]];
	}
}

void SpectraSolver::f_GatherMPI(
	int nitems, vector<vector<double>> &items, int rank, int mpiprocesses)
{
	MPI_Status mpistatus;
	double *valuesend = new double[nitems];
	for(int n = 0; n < items[0].size(); n++){
		int sendrank = n%mpiprocesses;
		if(sendrank > 0){
			for(int j = 0; j < nitems; j++){
				valuesend[j] = items[j][n];
			}
			if(m_thread != nullptr){
				m_thread->SendRecv(valuesend, nitems, MPI_DOUBLE, sendrank, 0, rank);
				for(int j = 0; j < nitems && rank == 0; j++){
					items[j][n] = valuesend[j];
				}
			}
			else{
				if(rank == sendrank){
					MPI_Send(valuesend, nitems, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
				}
				else if(rank == 0){
					MPI_Recv(valuesend, nitems, MPI_DOUBLE, sendrank, 0, MPI_COMM_WORLD, &mpistatus);
					for(int j = 0; j < nitems; j++){
						items[j][n] = valuesend[j];
					}
				}
			}
		}
	}
	delete[] valuesend;
}


void SpectraSolver::f_GetKrange(double Krange[])
{
	int kridx = krange_;
	if(m_srctype == ELLIPTIC_UND || m_isf8){
		kridx = ckrange_;
	}
	for(int j = 0; j < 2; j++){
		Krange[j] = m_confv[kridx][j];
	}
	if(Krange[0] > Krange[1]){
		swap(Krange[0], Krange[1]);
	}
}

double SpectraSolver::f_LoadParticleData(const string filename)
{
	int nparticle = 0;
	vector<vector<double>> part(6);

	if(m_rank == 0){
		ifstream ifs(filename);
		if(!ifs){
			throw runtime_error("Cannot open the data file \""+filename+"\".");
		}
		string input((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
		ifs.close();

		vector<string> lines, items;
		int nlines = separate_items(input, lines, "\n");
		for(int j = 0; j < 6; j++){
			part[j].resize(nlines, 0.0);
		}
		char *endptr;
		for(int n = 0; n < nlines; n++){
			if(separate_items(lines[n], items) < 6){
				continue;
			}
			for(int j = 0; j < 6; j++){
				part[j][nparticle] = strtod(items[j].c_str(), &endptr);
				if(*endptr != '\0'){
					break;
				}
			}
			if(*endptr != '\0'){
				continue;
			}
			nparticle++;
		}
	}
	MPI_Barrier(MPI_COMM_WORLD);
	if(m_thread != nullptr){
		m_thread->Bcast(&nparticle, 1, MPI_INT, 0, m_rank);
	}
	else{
		MPI_Bcast(&nparticle, 1, MPI_INT, 0, MPI_COMM_WORLD);
	}

	if(nparticle < 2){
		throw runtime_error("Too few particles found.");
	}

	if(m_mpiprocesses > 1){
		double *ws = new double[6*nparticle];
		if(m_rank == 0){
			for(int j = 0; j < 6; j++){
				for(int n = 0; n < nparticle; n++){
					ws[j*nparticle+n] = part[j][n];
				}
			}
		}
		if(m_thread != nullptr){
			m_thread->Bcast(ws, 6*nparticle, MPI_DOUBLE, 0, m_rank);
		}
		else{
			MPI_Bcast(ws, 6*nparticle, MPI_DOUBLE, 0, MPI_COMM_WORLD);
		}
		if(m_rank > 0){
			for(int j = 0; j < 6; j++){
				part[j].resize(nparticle, 0.0);
				for(int n = 0; n < nparticle; n++){
					part[j][n] = ws[j*nparticle+n];
				}
			}
		}
		delete[] ws;
	}
	MPI_Barrier(MPI_COMM_WORLD);

	for(int j = 0; j < 6; j++){
		m_partbuf[j] = new vector<double>;
		m_partbuf[j]->resize(nparticle);
	}

	vector<double> tpart[2];

	for(int j = 0; j < 2; j++){
		tpart[j].resize(nparticle);
	}

	int index[6];
	double coef[6] = {1, 1, 1, 1, 1, 1};
	index[0] = m_parform[colx_]-1;
	index[1] = m_parform[colxp_]-1;
	index[2] = m_parform[coly_]-1;
	index[3] = m_parform[colyp_]-1;
	index[4] = m_parform[colt_]-1;
	index[5] = m_parform[colE_]-1;

	if(m_parformsel[unitxy_] == UnitMiliMeter){
		coef[0] = coef[2] = 1e-3;
	}

	if(m_parformsel[unitxyp_] == UnitMiliRad){
		coef[1] = coef[3] = 1e-3;
	}

	if(m_parformsel[unitt_] == UnitpSec){
		coef[4] = 1e-12;
	}
	if(m_parformsel[unitt_] == UnitfSec){
		coef[4] = 1e-15;
	}
	if(m_parformsel[unitt_] == UnitMeter){
		coef[4] = 1.0/CC;
	}
	if(m_parformsel[unitt_] == UnitMiliMeter){
		coef[4] = 1e-3/CC;
	}

	if(m_parformsel[unitE_] == UnitMeV){
		coef[5] = 1e-3;
	}
	if(m_parformsel[unitE_] == UnitGamma){
		coef[5] = 1e-3*MC2MeV;
	}

	double sq[6], avg[6], corr[2] = {0, 0};
	for(int j = 0; j < 6; j++){
		sq[j] = avg[j]  = 0;
		for(int n = 0; n < nparticle; n++){
			(*m_partbuf[j])[n] = coef[j]*part[index[j]][n];
			sq[j] += (*m_partbuf[j])[n]*(*m_partbuf[j])[n];
			avg[j] += (*m_partbuf[j])[n];
			if(j == 1 || j == 3){
				corr[(j-1)/2] += (*m_partbuf[j-1])[n]*(*m_partbuf[j])[n];
			}
		}
		sq[j] /= nparticle;
		avg[j] /= nparticle;
	}
	corr[0] /= nparticle;
	corr[1] /= nparticle;

	double emitt[2], beta[2], alpha[2];
	for(int j = 0; j < 2; j++){
		double size = sq[2*j]-avg[2*j]*avg[2*j];
		double div = sq[2*j+1]-avg[2*j+1]*avg[2*j+1];
		double rcorr = corr[j]-avg[2*j]*avg[2*j+1];
		emitt[j] = size*div-rcorr*rcorr;
		if(emitt[j] > 0){
			emitt[j] = sqrt(emitt[j]);
			beta[j] = size/emitt[j];
			alpha[j] = -rcorr/emitt[j];
		}
		else{
			emitt[j] = INFINITESIMAL;
			beta[j] = 1;
			alpha[j] = 0;
		}
	}

	for(int j = 0; j < 6; j++){
		for(int n = 0; n < nparticle && j > 3; n++){
			if(j == 4){ // time
				(*m_partbuf[j])[n] -= avg[j];
			}
			else{ // j == 5; energy
				if(avg[j] == 0){
					throw runtime_error("Particle data invalid: average energy is zero.");
				}
				(*m_partbuf[j])[n] = (*m_partbuf[j])[n]/avg[j]-1;
			}
		}
	}
	m_acc[eGeV_] = avg[5]; // GeV

	get_stats((*m_partbuf[4]), nparticle, &avg[4], &m_acc[bunchlength_]);
	get_stats((*m_partbuf[5]), nparticle, &avg[5], &m_acc[espread_]);

	m_acc[bunchlength_] *= CC*1000; // sec -> mm
	m_acc[emitt_] = emitt[0]+emitt[1];
	m_acc[coupl_] = emitt[1]/emitt[0];
	for(int j = 0; j < 2; j++){
		m_accv[beta_][j] = beta[j];
		m_accv[alpha_][j] = alpha[j];
		m_accv[eta_][j] = m_accv[etap_][j] = 0;
	}
	Initialize();
	m_nparticle = nparticle;

	return m_parform_f[pcharge_]*nparticle;
}


