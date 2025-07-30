#include <algorithm>
#include <set>
#include "energy_convolution.h"
#include "filter_operation.h"

// files for debugging
string FuncConvSNArray;
string IntegSNFilter;
string IntegUFarSNEconv;
string IntegEconv;
string IntegSinFuncEsp;

#define MAX_POINTS_ENERGY_CONV_GAUSSQ 1000
#define DIRECT_SN_CONVOLUTION_STEP 10

//------------------------------------------------------------------------------
EnergyConvolution::EnergyConvolution(int nitems)
{
    if(nitems > 0){
        AllocateMemoryEnergyConvolution(nitems);
    }
}

void EnergyConvolution::AllocateMemoryEnergyConvolution(int nitems)
{
    InitializeQGauss(MAX_POINTS_ENERGY_CONV_GAUSSQ, nitems);
    m_splfitem.resize(nitems);
}

void EnergyConvolution::AllocateInterpolant(
    int energymesh, vector<double> *energy, vector<vector<double>> *fluxin, bool isreg)
{
    m_energymesh = energymesh;
    for(int j = 0; j < m_nitems; j++){
        m_splfitem[j].Initialize(energy, &((*fluxin)[j]), isreg, energymesh);
    }
}

//------------------------------------------------------------------------------
EnergySpreadConvolution::EnergySpreadConvolution(SpectraSolver *spsolver, int nitems)
    : EnergyConvolution(nitems)
{
#ifdef _DEBUG
//IntegEconv = "..\\debug\\energy_conv_integ.dat";
#endif
    m_spsolver = spsolver;
    m_glimit = m_spsolver->GetAccuracy(acclimpE_)+GAUSSIAN_MAX_REGION-1;
    m_glevel = m_spsolver->GetAccuracy(accinpE_);
    m_pointsgauss = 64<<(m_glevel-1);
}

void EnergySpreadConvolution::IntegrandGauss(double ep, vector<double> *flux)
{
	GetValues(ep, flux);
    double eprof = m_spsolver->EnergyProfile(m_epref, ep);
    for(int j = 0; j < m_nitems; j++){
		(*flux)[j] *= eprof;
	}
}

void EnergySpreadConvolution::RunEnergyConvolution(
    double ep, vector<double> *fluxout, bool isdirect)
{
    int index, ip, im;
    int npointsg, jgrep = m_glevel+4;
    double epp, epm, eprof, eprof0, esigma;

    esigma = m_spsolver->EnergySpreadSigma(ep);
    if(isdirect || esigma < INFINITESIMAL || ep < INFINITESIMAL){
		GetValues(ep, fluxout);
        return;
    }
    m_epref = ep;

    npointsg = m_pointsgauss;
    if(ep > m_splfitem[0].GetFinXY()){
        epp = m_splfitem[0].GetFinXY();
        epm = max(m_splfitem[0].GetIniXY(), epp-esigma*m_glimit);
    }
    else if(ep < m_splfitem[0].GetIniXY()){
        epm = m_splfitem[0].GetIniXY();
        epp = min(m_splfitem[0].GetFinXY(), epm+esigma*m_glimit);
    }
    else{
        eprof0 = m_spsolver->EnergyProfile(ep, ep);

        index = m_splfitem[0].GetIndexXcoord(ep);
        epp = m_splfitem[0].GetXYItem(min(m_energymesh-1, index+1));
        epm = m_splfitem[0].GetXYItem(max(0, index-1));

        eprof = m_spsolver->EnergyProfile(ep, epp)/eprof0;
        ip = index;
        while(ip < m_energymesh-1 && eprof > 1.0e-3){
            epp = m_splfitem[0].GetXYItem(++ip);
            eprof = m_spsolver->EnergyProfile(ep, epp)/eprof0;
        }
        epp = min(epp, ep+esigma*m_glimit);

        eprof = m_spsolver->EnergyProfile(ep, epm)/eprof0;
        im = index;
        while(im > 0 && eprof > 1.0e-3){
            epm = m_splfitem[0].GetXYItem(--im);
            eprof = m_spsolver->EnergyProfile(ep, epm)/eprof0;
        }
        epm = max(epm, ep-esigma*m_glimit);

        jgrep += (int)floor(fabs(epp-epm)/eprof0);
        npointsg = m_pointsgauss*(((ip-im)/m_pointsgauss)+1)+1;
    }
    IntegrateGauss(npointsg, epm, epp, fluxout, IntegEconv);
}

void EnergySpreadConvolution::GetValues(double ep, vector<double> *fluxout)
{
	int j;
	if(ep > m_splfitem[0].GetFinXY() || ep < m_splfitem[0].GetIniXY()){
		for(j = 0; j < m_nitems; j++){
			(*fluxout)[j] = 0.0;
		}
	}
	else{
		for(j = 0; j < m_nitems; j++){
			(*fluxout)[j] = m_splfitem[j].GetValue(ep);
		}
	}
}

//------------------------------------------------------------------------------
SincFuncEnergyConvolution::SincFuncEnergyConvolution(SpectraSolver &spsolver)
    : EnergySpreadConvolution(&spsolver), SpectraSolver(spsolver)
{
#ifdef _DEBUG
//IntegUFarSNEconv = "..\\debug\\flux_snesp_conv.dat";
#endif

    m_snitems = 1;
    if(m_issegu && m_issrc2){
        m_snitems = 3;
    }
    AllocateMemoryEnergyConvolution(m_snitems);
}

void SincFuncEnergyConvolution::SetHarmonic(int nh)
{
    m_nh = nh;
}

void SincFuncEnergyConvolution::SetObservationAngle(double gtx, double gty)
{
    SetRadialAngle(sqrt(hypotsq(gtx, gty)));
}

void SincFuncEnergyConvolution::SetRadialAngle(double gt)
{
    m_e1st4sn = GetE1st(gt);
}

void SincFuncEnergyConvolution::SetCurrentE1st(double e1st)
{
    m_e1st4sn = e1st;
}

void SincFuncEnergyConvolution::IntegrandGauss(double ep, vector<double> *snc)
{
    double eprof;
    int j;

    GetSincFunctions(m_nh, ep/m_e1st4sn, snc);
    eprof = EnergyProfile(m_epref, ep);
    for(j = 0; j < m_snitems; j++){
        (*snc)[j] *= eprof;
    }
}

void SincFuncEnergyConvolution::GetSincFunctionCV(double ep, vector<double> *sn)
{
    double esigma, epm, epp;

    esigma = EnergySpreadSigma(ep);
    if(esigma < INFINITESIMAL){
        GetSincFunctions(m_nh, ep/m_e1st4sn, sn);
        return;
    }

    m_epref = ep;
    epm = ep-esigma*m_nlimit[acclimpE_];
    epp = ep+esigma*m_nlimit[acclimpE_];
    int npointsg = (int)ceil((epp-epm)/(m_e1st4sn/(double)(m_N*m_M)))*4*m_accuracy[accinpE_];
        // 4 points per sigma

    npointsg = 16*((npointsg/16)+1)+1;
    IntegrateGauss(npointsg, epm, epp, sn, IntegUFarSNEconv);
}

double SincFuncEnergyConvolution::GetCurrentE1st()
{
    return m_e1st4sn;
}

int SincFuncEnergyConvolution::GetNumberOfSnItems()
{
    return m_snitems;
}

//------------------------------------------------------------------------------
SincFuncEspreadProfile::SincFuncEspreadProfile(SpectraSolver &spsolver)
    : SincFuncEnergyConvolution(spsolver)
{
#ifdef _DEBUG
//IntegSinFuncEsp = "..\\debug\\energy_conv_sinc_func.dat";
#endif
    m_eps = 1.0e-5/m_nfrac[accinpE_];
    AllocateMemorySimpson(1, 1, 1);
}

void SincFuncEspreadProfile::QSimpsonIntegrand(int layer, double gt, vector<double> *density)
{
    vector<double> sn(3);

    SetCurrentE1st(GetE1st(gt));
    GetSincFunctionCV((double)m_nh*m_e1staxis, &sn);
    (*density)[0] = sn[0]*gt*PI2;
}

void SincFuncEspreadProfile::GetPeakValueStdDeviation(int nh, double *peak, double *gtsigma)
{
    vector<double> sn(3);
    double gt = 0.0;
	int layers[2] = {0, -1};

    if(m_iszspread){
        *peak = 1.0;
        *gtsigma = sqrt((1.0+m_K2)/(double)(nh*m_N))*0.5;
		return;
    }

    m_e1staxis = GetE1st(0.0);

    m_nh = nh;
    SetHarmonic(nh);

    SetCurrentE1st(m_e1staxis);
    GetSincFunctionCV((double)nh*m_e1staxis, &sn);
    *peak = sn[0];
    do {
        gt += SINC_INTEG_DIVISION*sqrt(1.0/(double)m_N);
        SetCurrentE1st(GetE1st(gt));
        GetSincFunctionCV((double)nh*m_e1staxis, &sn);
    } while(sn[0] > (*peak)*m_eps);

    IntegrateSimpson(layers, 0.0, gt, m_eps, 6, NULL, &sn, IntegSinFuncEsp);
    *gtsigma = sn[0]/PI2/(*peak);
    if(*gtsigma < INFINITESIMAL){
        *gtsigma = 0.0;
    }
    else{
        *gtsigma = sqrt(*gtsigma);
    }
}

//------------------------------------------------------------------------------
SincFuncFilteredIntegration::SincFuncFilteredIntegration(
    SpectraSolver &spsolver, FilterOperation *filter)
    : SincFuncEnergyConvolution(spsolver)
{
#ifdef _DEBUG
    IntegSNFilter = "..\\debug\\filterp_sn_integ.dat";
#endif
    AllocateMemorySimpson(m_snitems, m_snitems, 1);
    m_eps = 0.01/m_nfrac[accinpE_];
    m_filter = filter;
}

void SincFuncFilteredIntegration::QSimpsonIntegrand(int layer, double ep, vector<double> *snc)
{
    GetSincFunctions(m_nh, ep/m_e1st4sn, snc);
    double rate = m_filter->GetTransmissionRateCV(ep, true);
    for(int j = 0; j < m_snitems; j++){
        (*snc)[j] *= rate;
    }
}

void SincFuncFilteredIntegration::GetSincFunctionFilteredPower(vector<double> *sn)
{
	int j, m, regions, layers[2] = {0, -1};
    double epm, epp, demn;
    vector<double> sntmp(4);
    vector<vector<double>> snv(1);
    set<double> eregion;
    set<double>::iterator itr;

    snv[0].resize(2);
    regions = m_filter->GetNumberOfRegions()+1;
    for(m = 0; m < regions; m++){
        eregion.insert(m_filter->GetRegionBorder(m));
    }

    demn = (double)(1<<SINC_MAX_DIVISION_POW2)*m_e1st4sn/(double)(m_N*m_M);
    epp = m_filter->GetRegionBorder(0)+demn;
    while(epp < m_filter->GetRegionBorder(regions-1)){
        eregion.insert(epp);
        epp += demn;
    };
    for(j = 0; j < m_snitems; j++){
        (*sn)[j] = 0.0;
    }
    itr = eregion.begin();
    epm = *itr;
    int nrep = 0;
    while(++itr != eregion.end()){
        epp = *itr;
        IntegrateSimpson(layers, epm, epp, m_eps, SINC_MAX_DIVISION_POW2+4,
            &snv, &sntmp, IntegSNFilter, nrep > 0);
        for(j = 0; j < m_snitems; j++){
            (*sn)[j] += sntmp[j];
        }
        snv[0][0] = (*sn)[0];
        epm = epp;
        nrep++;
    }
}

//------------------------------------------------------------------------------
ArraySincFuncEnergyConvolution::ArraySincFuncEnergyConvolution(
    SpectraSolver &spsolver, FilterOperation *filter)
    : SpectraSolver(spsolver)
{
#ifdef _DEBUG
//FuncConvSNArray = "..\\debug\\func_conv_sn_array.dat";
#endif

    int j, nhmaxini;
    double erange[2], ec;
    double eps_erange = 1.0e-2/(1<<(m_accuracy[acclimpE_]-1));

    m_eps_func_stepper = 0.1/m_nfrac[accinpE_];
    m_sincfunc = nullptr;
    m_sincfilter = nullptr;
    m_ep1max4array = GetE1st();
    m_ep1min4array = GetE1st(m_gtmax);
    m_demin4array = m_ep1min4array/(double)(m_N*m_M)*0.1;
    if(m_ispower){
        if(m_confsel[filter_] == GenFilterLabel){
            ec = max(m_ep1max4array, GetCriticalEnergy());
            filter->GetEnergyRange4Power(ec, eps_erange, erange);
        }
        m_sincfilter = new SincFuncFilteredIntegration(spsolver, filter);
        m_snitems = m_sincfilter->GetNumberOfSnItems();
    }
    else{
        m_sincfunc = new SincFuncEnergyConvolution(spsolver);
        m_snitems = m_sincfunc->GetNumberOfSnItems();
    }
    nhmaxini = (int)ceil(m_fixep/m_ep1min4array)+10;
            // 10: margin to avoid push_back, if possible

    AllocateMemoryFuncDigitizer(m_snitems);

    m_allocspline.resize(nhmaxini+1);
    for(j = 0; j < m_snitems; j++){
        m_sincfuncspline[j].resize(nhmaxini+1);
    }
    m_sntmp.resize(m_snitems+1);
}

ArraySincFuncEnergyConvolution::~ArraySincFuncEnergyConvolution()
{
    int j, nh;

    if(m_sincfunc != nullptr){
        delete m_sincfunc;
        m_sincfunc = nullptr;
    }
    if(m_sincfilter != nullptr){
        delete m_sincfilter;
        m_sincfilter = nullptr;
    }
    for(nh = 1; nh < (int)m_allocspline.size()-1; nh++){
        if(!m_allocspline[nh]) continue;
        for(j = 0; j < m_snitems; j++){
            if(m_sincfuncspline[j][nh] != nullptr){
                delete m_sincfuncspline[j][nh];
                m_sincfuncspline[j][nh] = nullptr;
            }
        }
    }
}

double ArraySincFuncEnergyConvolution::Function4Digitizer(double ep1, vector<double> *sn)
{
    double ref;

    if(m_ispower){
        m_sincfilter->SetCurrentE1st(ep1);
        m_sincfilter->GetSincFunctionFilteredPower(sn);
        ref = (*sn)[0];
    }
    else{
        m_sincfunc->SetCurrentE1st(ep1);
        m_sincfunc->GetSincFunctionCV(m_fixep, sn);
        ref = (*sn)[0]+INFINITESIMAL;
    }
    return ref;
}

void ArraySincFuncEnergyConvolution::GetSincFunctionFromArray(
        int nh, double ep1, vector<double> *sn)
{
    if(m_accb[zeroemitt_] && m_ispower){
        m_sincfilter->SetHarmonic(nh);
        Function4Digitizer(ep1, sn);
        return;
    }

    if(nh > (int)m_allocspline.size()-1){
        f_AllocateSpline(nh, true);
    }
    else if(!m_allocspline[nh]){
        f_AllocateSpline(nh, false);
    }
    for(int j = 0; j < m_snitems; j++){
        (*sn)[j] = m_sincfuncspline[j][nh]->GetOptValue(ep1);
    }
}

void ArraySincFuncEnergyConvolution::f_AllocateSpline(int nh, bool isappend)
{
    int nstep, npointsini, level;
    double refenergy;
    Spline *splinetmp[4];
    vector<double> ep1array;

    if(m_ispower){
		npointsini = 20<<(m_accuracy[accinpE_]-1);
        m_sincfilter->SetHarmonic(nh);
        refenergy = m_ep1max4array;
        level = FUNC_DIGIT_BASE;
    }
    else{
		npointsini = (m_N*m_M*nh)<<(m_accuracy[accinpE_]-1);
        m_sincfunc->SetHarmonic(nh);
        refenergy = m_fixep/(double)nh;
        level = FUNC_DIGIT_ALLOC_XREF|FUNC_DIGIT_BASE;
    }

	double xrange[NumberFStepXrange] = 
		{0.0, m_ep1min4array, m_ep1max4array, refenergy, m_demin4array};
	double eps[2] = {m_eps_func_stepper, 0.0};

	nstep = RunDigitizer(level, &ep1array, &m_sntmp, 
			xrange, npointsini, eps, nullptr, 0, FuncConvSNArray);

    for(int j = 0; j < m_snitems; j++){
        splinetmp[j] =  new Spline();
        splinetmp[j]->SetSpline(nstep, &ep1array, &m_sntmp[j]);
    }
    if(isappend){
        m_allocspline.push_back(true);
        for(int j = 0; j < m_snitems; j++){
            m_sincfuncspline[j].push_back(splinetmp[j]);
        }
    }
    else{
        m_allocspline[nh] = true;
        for(int j = 0; j < m_snitems; j++){
            m_sincfuncspline[j][nh] = splinetmp[j];
        }
    }
}


