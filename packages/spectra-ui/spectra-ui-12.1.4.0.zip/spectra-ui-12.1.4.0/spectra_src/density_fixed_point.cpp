#include <algorithm>
#include "density_fixed_point.h"
#include "power_density.h"
#include "flux_density.h"
#include "undulator_fxy_far.h"
#include "energy_convolution.h"
#include "bm_wiggler_radiation.h"
#include "filter_operation.h"
#include "complex_amplitude.h"
#include "source_profile.h"

//---------------------------
// files for debugging
string UnfFarHarmSum;

DensityFixedPoint::DensityFixedPoint(SpectraSolver &spsolver, 
    Trajectory *trajectory, FilterOperation *filter)
    : SpectraSolver(spsolver)
{
#ifdef _DEBUG
//UnfFarHarmSum  = "..\\debug\\und_far_nh_sum.dat";
#endif

    m_filter = filter;
    m_powerdens = nullptr;
    m_fluxnear = nullptr;
    m_fluxund = nullptr;
    m_sneconv = nullptr;
    m_sneconvarray = nullptr;
    m_espreadconv = nullptr;
    m_bmwigglerflux = nullptr;
    m_srcprof = nullptr;
    m_camp = nullptr;

    m_harmonic_eps = 1.0e-2/(1<<(m_accuracy[accconvharm_]-1));
    m_convergence_limit = 2+m_accuracy[accconvharm_]*2;
    m_energymesh = 0;
    m_snconv1st = true;

    if(m_isf8){
        m_nhtarget = (int)floor(2.0*m_conf[hfix_]+0.5);
    }
    else{
        m_nhtarget = (int)floor(m_conf[hfix_]+0.5);
    }
    m_nitemspoint = m_isfluxs0 ? 1 : 4;

    if(m_issrcpoint){
        m_camp = new ComplexAmplitude(spsolver);
        int nwiggler = m_iswiggler ? m_N : 0;
        m_calcstatus->SetSubstepNumber(0, 2);
        m_srcprof = new SourceProfile(
            m_camp, m_accuracy[accinobs_], nwiggler, m_isoddpole, m_calcstatus, 1);
        m_calcstatus->SetCurrentOrigin(0);

        m_srcprof->AllocateSpatialProfile(m_rank, m_mpiprocesses);
        m_calcstatus->SetCurrentOrigin(0);
        m_dXYdUV = m_camp->GetConvUV();
        m_coefsrcp =  m_camp->GetSrcPointCoef();
    }
	else if(m_ispower && !m_isvpdens){
        m_powerdens = new PowerDensity(spsolver, trajectory);
		if(m_isfilter && !m_is3dsrc){
            if(m_isfar){
                if(m_iswiggler || m_isbm){
                    m_bmwigglerflux = new BMWigglerRadiation(spsolver, m_filter);
                }
                else{
                    m_fluxund = new UndulatorFxyFarfield(spsolver);
                    m_sneconvarray =
                        new ArraySincFuncEnergyConvolution(spsolver, m_filter);
                }
            }
            else{
                m_fluxnear = new FluxDensity(spsolver, trajectory, filter);
            }
        }
        else if(m_isrespow){
            m_fluxund = new UndulatorFxyFarfield(spsolver);
        }
        m_convf2p = GetPConvFactor();
    }
    else if(m_isfar && m_isund && !m_confb[wiggapprox_]){
        m_fluxund = new UndulatorFxyFarfield(spsolver);
        if(m_isenergy){
            m_sneconv = new SincFuncEnergyConvolution(spsolver);
        }
        else{
            m_sneconvarray = new ArraySincFuncEnergyConvolution(spsolver, m_filter);
        }
    }
    else if(m_isfar && (m_iswiggler || m_isbm || m_confb[wiggapprox_])){
        m_bmwigglerflux = new BMWigglerRadiation(spsolver, m_filter);
    }
    else{
        m_fluxnear = new FluxDensity(spsolver, trajectory, filter);
        m_espreadconv = new EnergySpreadConvolution(&spsolver, 4);
    }

    if(m_fluxnear != nullptr){
        m_fluxnear->GetEnergyArray(m_earray);
        m_energymesh = (int)m_earray.size();
    }
    else if(m_bmwigglerflux != nullptr){
        m_bmwigglerflux->GetEnergyArray(m_earray);
        m_energymesh =  (int)m_earray.size();
    }
    if(m_energymesh > 0){
        m_ws4flux.resize(4*m_energymesh);
        m_farray.resize(4);
        for(int j = 0; j < 4; j++){
            m_farray[j].resize(m_energymesh);
        }
    }
}

DensityFixedPoint::~DensityFixedPoint()
{
    if(m_powerdens != nullptr){
        delete m_powerdens;
    }
    if(m_fluxnear != nullptr){
        delete m_fluxnear;
    }
    if(m_fluxund != nullptr){
        delete m_fluxund;
    }
    if(m_bmwigglerflux != nullptr){
        delete m_bmwigglerflux;
    }
    if(m_sneconv != nullptr){
        delete m_sneconv;
    }
    if(m_sneconvarray != nullptr){
        delete m_sneconvarray;
    }
    if(m_espreadconv != nullptr){
        delete m_espreadconv;
    }
    if(m_camp  != nullptr){
        delete m_camp;
    }
    if(m_srcprof != nullptr){
        delete m_srcprof;
    }
}

void DensityFixedPoint::GetDensity(double x, double y, vector<double> *density)
{
    if(m_issrcpoint){
        double UV[2];
        UV[0] = x/m_dXYdUV; UV[1] = y/m_dXYdUV;
        (*density)[0] = m_srcprof->GetFluxAt(UV);        
    }
	else if(m_ispower && !m_isvpdens){
		f_GetPowerDensity(x, y, density);
		if(m_isrespow){
			f_GetHarmonicPowerUndFar(x, y, density);
			(*density)[1] *= m_convf2p;
			(*density)[2] *= m_convf2p;
		}
		else if(m_isfilter){
			f_GetFilteredPowerDensity(x, y, density); 
            // answer is assigned in density[1]
		}
    }
    else if(m_isfar && !m_confb[wiggapprox_] && m_isund){
        f_GetDensityUndFar(x, y, density);
    }
    else if(m_isfar && (m_confb[wiggapprox_] || m_iswiggler || m_srctype == BM)){
        f_GetFluxDensityWiggler(x, y, density);
    }
    else{
        f_GetFluxDensityNear(x, y, density);
    }
}

void DensityFixedPoint::AllocateOrbitComponents(Trajectory *trajectory)
{
    if(m_powerdens != nullptr){
        m_powerdens->AllocateOrbitComponents(trajectory);
    }
    if(m_fluxnear != nullptr){
        m_fluxnear->AllocateOrbitComponents();
    }
}

int DensityFixedPoint::GetEnergyArray(vector<double> &energy)
{
    if(m_fluxnear != nullptr){
        m_fluxnear->GetEnergyArray(energy);
    }
    else{
        m_bmwigglerflux->GetEnergyArray(energy);
    }
    return (int)energy.size();
}

void DensityFixedPoint::SetObserverPositionAngle(vector<double> &XYZ, vector<double> &exyz)
{
	m_powerdens->SetObserverPositionAngle(XYZ, exyz);
}

void DensityFixedPoint::GetMeasuredTime(vector<string> &label, vector<double> &rtime)
{
    label.clear();
    rtime.clear();
    vector<vector<string>> rlabel;
    vector<vector<double>> cputime;
    if(m_powerdens != nullptr){
        rlabel.push_back({}); cputime.push_back({});
        m_powerdens->GetMeasuredTime(rlabel.back(), cputime.back());
    }
    if(m_fluxnear != nullptr){
        rlabel.push_back({}); cputime.push_back({});
        m_fluxnear->GetMeasuredTime(rlabel.back(), cputime.back());
    }
    if(m_fluxund != nullptr){
        rlabel.push_back({}); cputime.push_back({});
        m_fluxund->GetMeasuredTime(rlabel.back(), cputime.back());
    }
    if(m_camp  != nullptr){
        rlabel.push_back({}); cputime.push_back({});
        m_camp->GetMeasuredTime(rlabel.back(), cputime.back());
    }

    for(int j = 0; j < rlabel.size(); j++){
        label.insert(label.end(), rlabel[j].begin(), rlabel[j].end());
        rtime.insert(rtime.end(), cputime[j].begin(), cputime[j].end());
    }
}

//---------- private functions ----------
void DensityFixedPoint::f_GetPowerDensity(
    double x, double y, vector<double> *density)
{
    m_powerdens->GetPowerDensity(x, y, density);
}

void DensityFixedPoint::f_GetDensityUndFar(
    double x, double y, vector<double> *density, bool ispower)
{
    int nh, nhcenter, j, k, cnumber = 0, irep;
    double gt, phi, ep1xy, fdnh, fdsum;
    vector<double> fd0(5), sn(4), fxy(13);

#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(3);
	if(!UnfFarHarmSum.empty()){
		debug_out.open(UnfFarHarmSum);
	}
#endif

    gt = m_conv2gt*sqrt(hypotsq(x, y));
    if(gt > 0){
        phi = atan2(y, x);
    }
    else{
        phi = 0.0;
    }
    ep1xy = GetE1st(gt);
    if(m_sneconv != nullptr){
        m_sneconv->SetCurrentE1st(ep1xy);
    }

    if(ispower){
        nhcenter = 1;
        (*density)[1] = 0.0;
    }
    else{
        nhcenter = (int)floor(m_fixep/ep1xy)+1;
        for(j = 0; j < 4; j++){
            (*density)[j] = 0.0;
        }
    }

    fdsum = 0.0;

    nh = nhcenter;
    irep = 0;
    for(k = -1; k <= 1; k += 2){
        do{
            if(m_sneconvarray != nullptr){
                m_sneconvarray->GetSincFunctionFromArray(nh, ep1xy, &sn);
            }
            else{
                m_sneconv->SetHarmonic(nh);
                m_sneconv->GetSincFunctionCV(m_fixep, &sn);
            }
            irep++;
            m_fluxund->SetCondition(nh, gt);
            m_fluxund->GetFxy(phi, &fxy);
            MultiplySincFunctions(&fxy, &sn, &fd0);
            fdnh = 0.0;
            if(ispower){
                (*density)[1] += fd0[0]+fd0[1];
                fdnh += fabs(fd0[0]+fd0[1]);
            }
            else{
                for(j = 0; j < 4; j++){
                    (*density)[j] += fd0[j];
                    fdnh += fabs(fd0[j]);
                }
            }
            fdsum += fdnh;
#ifdef _DEBUG
            if(!UnfFarHarmSum.empty()){
                items[0] = ep1xy*nh;
                items[1] = sn[0];
                items[2] = fdsum;
                PrintDebugItems(debug_out, (double)nh, items);
            }
#endif
            if(fdnh < m_harmonic_eps*fdsum){
                cnumber++;
            }
            else{
                cnumber = 0;
            }
            nh += k;
            if(nh > 2*nhcenter && fdsum <= INFINITESIMAL){
                break;
            }
        }while(nh > 0 && (fdsum <= INFINITESIMAL || cnumber < m_convergence_limit));
        nh = nhcenter+1;
    }
    m_snconv1st = false;
}

void DensityFixedPoint::f_GetHarmonicPowerUndFar(
    double x, double y, vector<double> *density)
{
    double gt, phi, E1stN;
    vector<double> fxy(12);

    gt = m_conv2gt*sqrt(hypotsq(x, y));
    if(gt){
        phi = atan2(y, x);
    }
    else{
        phi = 0.0;
    }
    m_fluxund->SetCondition(m_nhtarget, gt);
    m_fluxund->GetFxy(phi, &fxy);
    E1stN = GetE1st(gt)*m_M/(double)(m_N);
	(*density)[1] = fxy[0]*E1stN;
    (*density)[2] = fxy[1]*E1stN;
}

void DensityFixedPoint::f_AllocateFluxDensityNearZspread(double *xy)
{
    m_fluxnear->GetFluxItemsAt(xy, &m_ws4flux);
    for(int n = 0; n < m_energymesh; n++){
        for(int j = 0; j < m_nitemspoint; j++){
            m_farray[j][n] = m_ws4flux[n+j*m_energymesh];
        }
    }
}

void DensityFixedPoint::f_GetFluxDensityNear(double x, double y, vector<double> *density)
{
    int j;
    double xy[2];

    xy[0] = x; xy[1] = y;
    if(m_isenergy || m_isvpdens){
        m_fluxnear->GetFluxItemsAt(xy, density);
    }
    else{
        f_AllocateFluxDensityNearZspread(xy);
        if(m_energymesh == 1){
            for(j = 0; j < m_nitemspoint; j++){
                (*density)[j] = m_farray[j][0];
            }
        }
        else{
            m_espreadconv->AllocateInterpolant(m_energymesh, &m_earray, &m_farray, false);
            m_espreadconv->RunEnergyConvolution(m_fixep, density);
        }
    }
}

void DensityFixedPoint::f_GetFluxDensityWiggler(double x, double y, vector<double> *density)
{
    x *= m_conv2gt;
    y *= m_conv2gt;
    if(m_isenergy || m_isvpdens){
        m_bmwigglerflux->GetFluxArrayWigglerBM(x, y, density);
    }
    else{
        m_bmwigglerflux->GetFluxWigglerBM(m_fixep, x, y, density);
    }
}

void DensityFixedPoint::f_GetFilteredPowerDensity(double x, double y, vector<double> *density)
{
    double xy[2];

    if(m_isfar){
        if(m_isbm || m_iswiggler){
            x *= m_conv2gt;
            y *= m_conv2gt;
            m_bmwigglerflux->GetFluxArrayWigglerBM(x, y, &m_farray[0], true);
            (*density)[1] = m_filter->GetFilteredPower(m_energymesh, &m_earray, &m_farray[0]);
        }
        else{
            f_GetDensityUndFar(x, y, density, true);
        }
    }
    else{
        xy[0] = x; xy[1] = y;
        f_AllocateFluxDensityNearZspread(xy);
        (*density)[1] = m_filter->GetFilteredPower(m_energymesh, &m_earray, &m_farray[0]);
    }
    (*density)[1] *= m_convf2p;

    if(m_filter->IsPowerAbs()){
        (*density)[1] = max(0.0, (*density)[0]-(*density)[1]);
    }
}
