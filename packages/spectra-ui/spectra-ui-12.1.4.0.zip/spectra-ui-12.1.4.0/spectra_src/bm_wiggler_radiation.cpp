#include <algorithm>
#include "bessel.h"
#include "bm_wiggler_radiation.h"
#include "undulator_fxy_far.h"
#include "filter_operation.h"

// files for debugging
string IntegBMIFlux;
string IntegEMPWTFlux;
string SpectrumWiggApprox;

BMWigglerRadiation::BMWigglerRadiation(SpectraSolver &spsolver, FilterOperation *filter)
    : SpectraSolver(spsolver)
{
#ifdef _DEBUG
//IntegBMIFlux = "..\\debug\\bm_iflux_integ.dat";
//IntegEMPWTFlux = "..\\debug\\empw_tflux_integ.dat";
//SpectrumWiggApprox = "..\\debug\\wigg_approx_spectrum.dat";
#endif
    double eps_erange = 1.0e-2/(1<<(m_accuracy[acclimpE_]-1)), erange[2];

    m_isbm = m_srctype == BM;
    m_ecritical = GetCriticalEnergy();
    if(m_isenergy || m_isvpdens){
        SetEnergyPoints();
    }
    else if(m_ispower && m_isfilter){
        m_conf[emesh_] = 100<<(m_accuracy[accinpE_]-1);
        m_confsel[estep_] = LogLabel;
        if(m_confsel[filter_] == GenFilterLabel){
            filter->GetEnergyRange4Power(m_ecritical, eps_erange, erange);
            for(int j = 0; j < 2; j++){
                m_confv[erange_][j] = erange[j];
            }
        }
        else{
            filter->GetEnergyRange(&m_confv[erange_][0], &m_confv[erange_][1]);
            m_confv[erange_][0] = max(m_confv[erange_][0], 
                m_ecritical*1.0e-5/(1<<(m_accuracy[acclimpE_]-1)));
        }
        SetEnergyPoints();
    }
    else{
        SetEnergyPoints(true);
    }
    m_undfxy = nullptr;
    if(m_confb[wiggapprox_]){
        m_undfxy = new UndulatorFxyFarfield(spsolver);
    }
    AllocateMemorySimpson(2, 2, 2);
}

BMWigglerRadiation::~BMWigglerRadiation()
{
    if(m_undfxy != nullptr){
        delete m_undfxy;
    }
}

void BMWigglerRadiation::GetEnergyArray(vector<double> &energy)
{
    energy = m_eparray;
}

void BMWigglerRadiation::GetBMStokes(double u, double v, vector<double> *fhvc)
{
    if(u <= 0){
        for(int j = 0; j < 4; j++){
            (*fhvc)[j] = 0.0;
        }
        return;
    }
	double eta, vv, fx, fy;
	vv = 1.0+v*v;
	eta = u*pow(vv, (1.5))/2.0;
	fx = 2.0/sqrt(vv)*Bessel::K23_u(eta);
	fy = 2.0/vv*v*Bessel::K13_u(eta);

    (*fhvc)[0] = fx*fx;
    (*fhvc)[1] = fy*fy;
    (*fhvc)[2] = 2.0*fy*fx;
    (*fhvc)[3] = 0.0;
}

void BMWigglerRadiation::BMPowerDensity(double gpsi, vector<double> *pd)
{
    (*pd)[0] = pow((1.0+pow(gpsi, 2.0)), -2.5)+
            5.0*pow(gpsi, 2.0)/7.0*pow((1.0+pow(gpsi, 2.0)), -3.5);
}

double BMWigglerRadiation::GetDivergence(double u)
{
	double IK53, K23;
	IK53 = Bessel::IK53_u(u);
	K23 = Bessel::K23_u(u/2.0);
	return sqrt(PI2/3.0)/4.0*IK53/K23/K23;
}

void BMWigglerRadiation::GetFluxWigglerBM(
    double ep, double gtx, double gty, vector<double> *fhvc)
{
    double fu, rfu, u, gtyk, ukx, uky;
    vector<double> fhvc1(5), fhvc2(5);
    int i;

    if(m_isbm){
        GetBMStokes(ep/m_ecritical, gty, fhvc);
        return;
    }

    ukx = m_Kxy[0][1];
    uky = m_Kxy[1][1];
    fu = 1.0-pow(gtx/uky, 2.0);
    if(fu > 0.0){
        rfu = sqrt(fu);
        u = ep/m_ecritical/rfu ;
        if (ukx < KX_EXIST){
            GetBMStokes(u, gty, fhvc);
            (*fhvc)[2] = 0.0;
        }
        else{
            gtyk = -gty+ukx*rfu;
            GetBMStokes(u, gtyk, &fhvc1);
            gtyk = gty+ukx*rfu;
            GetBMStokes(u, gtyk, &fhvc2);
            for(i = 0; i < 3; i++){
                (*fhvc)[i] = (fhvc1[i]+fhvc2[i])/2.0;
            }
        }
        (*fhvc)[3] = 0.0;
    }
    else{
        for(i = 0; i < 4; i++){
            (*fhvc)[i] = 0;
        }
    }
}

void BMWigglerRadiation::GetFluxArrayWigglerBM(
    double gtx, double gty, vector<double> *farray, bool ispower)
{
    int n, j;
    vector<double> fhvc(4);

    double e1st =1.0;
    if(m_confb[wiggapprox_]){
        double gtxy[2] = {gtx, gty};
        double gt = sqrt(hypotsq(gtx, gty));
        e1st = m_undfxy->GetE1st(gt);
        int umax = (int)ceil(minmax(m_eparray, true)/e1st);
        m_undfxy->SetObservation4Wiggler(umax, gtxy);
    }

    for(n = 0; n < m_eparray.size(); n++){
        if(m_confb[wiggapprox_]){
            m_undfxy->GetFlux4Wiggler(m_eparray[n]/e1st, &fhvc);
        }
        else{
            GetFluxWigglerBM(m_eparray[n], gtx, gty, &fhvc);
        }
        if(ispower){
            (*farray)[n] = fhvc[0]+fhvc[1];
        }
        else{
            for(j = 0; j < 4; j++){
                (*farray)[n+j*m_eparray.size()] = fhvc[j];
            }
        }
    }

#ifdef _DEBUG
    if(!SpectrumWiggApprox.empty()){
        ofstream debug_out(SpectrumWiggApprox);
        vector<double> items(6);
        for (n = 0; n < m_eparray.size(); n++){
            items[0] = m_eparray[n];
            items[1] = m_eparray[n]/e1st;
            for(int j = 0; j < 4; j++){
                items[j+2] = (*farray)[n+j*m_eparray.size()];
            }
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif
}

void BMWigglerRadiation::TotalFlux(double ep, double flux[])
// 0: horizoznta, 1: vertical, 2: total
{
    if(m_isbm){
        f_TotalFluxBM(ep/m_ecritical, flux);
    }
    else{
        f_TotalFluxEMPW(ep, flux);
    }
}

void BMWigglerRadiation::IntegratedFluxPower(double ep, vector<double> *Ifp)
{
    double epfin;
	int layers[2] = {RadQSimpTypeIflux, -1};

    m_eptmp = ep;
    epfin = m_ecritical*MAX_EP_EC_BM;
    IntegrateSimpson(layers,
        ep, epfin, 1.0e-3/m_nfrac[accinpE_], m_accuracy[accinpE_]+4, NULL, Ifp, IntegBMIFlux);
}

void BMWigglerRadiation::QSimpsonIntegrand(int layer, double x, vector<double> *y)
{
    switch(layer){
        case RadQSimpTypeTflux:
            f_QSimpsonTflux(x, y);
            break;
        case RadQSimpTypeIflux:
            f_QSimpsonIflux(x, y);
            break;
    }
}

void BMWigglerRadiation::f_QSimpsonTflux(double z, vector<double> *flux)
{
    double u, b1, b2, tflux[3];
    OrbitComponents orbit;

    GetIdealOrbit(z, &orbit);
    b1 = sqrt(hypotsq(orbit._acc[0], orbit._acc[1]))/COEF_ACC_FAR_BT;
    if(m_issrc2){
        GetIdealOrbit(z, &orbit, true);
        b2 = sqrt(hypotsq(orbit._acc[0], orbit._acc[1]))/COEF_ACC_FAR_BT;
    }

    if(b1 < INFINITESIMAL){
        (*flux)[0] = 0.0;
    }
    else{
        u = m_eptmp/GetCriticalEnergy(&b1);
		f_TotalFluxBM(u, tflux);
        (*flux)[0] = PI2*tflux[0]*b1*COEF_K_VALUE;
        (*flux)[1] = PI2*tflux[1]*b1*COEF_K_VALUE;
    }
    if(m_issrc2){
        if(b2 > INFINITESIMAL){
            u = m_eptmp/GetCriticalEnergy(&b2);
			f_TotalFluxBM(u, tflux);
            (*flux)[0] += PI2*tflux[0]*b2*COEF_K_VALUE;
            (*flux)[1] += PI2*tflux[1]*b2*COEF_K_VALUE;
        }
    }
}

void BMWigglerRadiation::f_QSimpsonIflux(double ep, vector<double> *flux)
{
    double tflux[3];

    TotalFlux(ep, tflux);
    (*flux)[0] = 1.0e+3*tflux[2]/ep;
    (*flux)[1] = tflux[2]; //W -> kW
}

void BMWigglerRadiation::f_TotalFluxEMPW(double ep, double tflux[])
{
    vector<double> tv(3);
	int layers[2] = {RadQSimpTypeTflux, -1};

    m_eptmp = ep;
    IntegrateSimpson(layers,
        0.0, m_lu, 1.0e-2/m_nfrac[accinpE_], m_accuracy[accinpE_]+5, NULL, &tv, IntegEMPWTFlux);
	tflux[0] = tv[0];
	tflux[1] = tv[1];
	tflux[2] = tflux[0]+tflux[1];
}

void BMWigglerRadiation::f_TotalFluxBM(double u, double tflux[])
	// tflux[0] = (tflux[0]+u*K_2/3(u))/2 : horizontal flux
	// tflux[1] = (tflux[0]-u*K_2/3(u))/2 : vertical flux
	// tflux[2] = u*int_u^infty K_5/3(u) : total flux
{
	double af = Bessel::K23_u(u);
	tflux[2] = Bessel::IK53_u(u);
	tflux[0] = (tflux[2]+af)*0.5;
	tflux[1] = (tflux[2]-af)*0.5;
}


