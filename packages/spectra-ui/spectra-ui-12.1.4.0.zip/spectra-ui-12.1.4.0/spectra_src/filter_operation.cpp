#include <algorithm>
#include <set>
#include "filter_operation.h"
#include "mucal.h"
#include "energy_absorption_ratio.h"
#include "bm_wiggler_radiation.h"


// files for debugging
string FilterPowerInteg;
string IntegFilterEConv;
string FuncFilterEConv;

#define MAX_POINTS_FILTER_CONV_GAUSSQ 1000

GenericFilterTransmission::GenericFilterTransmission()
{
    m_tbl_energies = tbl_energies;
    m_tbl_ratios = tbl_ratios;
}

void GenericFilterTransmission::SetMaterials(
    vector<tuple<string, double>> &filters, map<string, tuple<double, vector<double>>> &materials)
{
    double thickness, density;
    string filtername;
    tuple<double, vector<double>> mcont;
    vector<double> zratio;

    m_Znumber.clear(); m_density.clear(); m_thickness.clear();
    m_elements = 0;
    for(int m = 0; m < filters.size(); m++){
        filtername = get<0>(filters[m]);
        thickness = get<1>(filters[m]);
        try{
            mcont = materials.at(filtername);
        }
		catch (const out_of_range &e) {
			cerr << "\"" << filtername << "\" is not available: " << e.what() << endl;
			continue;
		}
        density = get<0>(mcont);
        zratio = get<1>(mcont);
        for(int i = 0; i < zratio.size()/2; i++){
            m_elements++;
            int Z = (int)floor(0.5+zratio[2*i]);
            double mr = zratio[2*i+1];
            m_Znumber.push_back(Z);
            m_density.push_back(density*mr);
            m_thickness.push_back(thickness);
        }
    }
}

double GenericFilterTransmission::GetTransmission(
    double ep, double *linabscoef, double *linheatcoef)
{
    int i, err_return;
    double rate, exparg;
    char error[256];
    double energy[9], xsec[11], fl_yield[4], aratio;

    if(ep < INFINITESIMAL){
        return 0.0;
    }
    rate = 1.0;
    if(ep == 1000.0){
        ep += 0.01; // to avoid the bug in mucal.c
    }

	if(linabscoef != nullptr){
		*linabscoef = 0;
	}
	if(linheatcoef != nullptr){
		*linheatcoef = 0;
	}
	
	for(i = 0; i < m_elements; i++){
        err_return = mucal("", 
            m_Znumber[i], ep*1.0e-3, 'c', 0, energy, xsec, fl_yield, error);
		if(err_return == m_edge_warn){
			rate = 0.0;
			break;
		}
		else if(err_return !=  no_error && err_return != within_edge){
            continue;
        }
        else{
            exparg = xsec[3]*m_density[i]*(m_thickness[i]*0.1); // mm -> cm
        }
		if(linabscoef != nullptr){
			*linabscoef += xsec[3]*m_density[i]*0.1; // /cm -> /mm
		}
        if (linheatcoef != nullptr){
            aratio = GetEnergyAbsRatio(m_Znumber[i], ep);
			*linheatcoef += aratio*xsec[3]*m_density[i]*0.1; // /cm -> /mm
        }
        if(exparg > MAXIMUM_EXPONENT){
            rate = 0.0;
            break;
        }
        else{
            rate *= exp(-exparg);
        }
    }
    return rate;
}

double GenericFilterTransmission::GetEnergyAbsRatio(int Z, double ep)
{
    if(Z >= tbl_energies.size()){
        return 1.0;
    }
    if(ep < tbl_energies[Z].front() || ep > tbl_energies[Z].back()){
        return 1.0;
    }

    int eidx = SearchIndex((int)tbl_energies[Z].size(), false, m_tbl_energies[Z], ep);
    eidx = min(eidx, (int)tbl_energies[Z].size()-1);

    return lininterp(ep, m_tbl_energies[Z][eidx], m_tbl_energies[Z][eidx+1], 
        m_tbl_ratios[Z][eidx], m_tbl_ratios[Z][eidx+1]);
}

int GenericFilterTransmission::GetElements()
{
    return m_elements;
}

vector<int> GenericFilterTransmission::GetZnumbers()
{
    return m_Znumber;
}

//------------------------------------------------------------------------------
GenericAbsorber::GenericAbsorber(
    vector<tuple<string, double>> &filters,
    map<string, tuple<double, vector<double>>> &materials)
{
	m_nabss = (int)filters.size();
	m_generic.resize(m_nabss, nullptr);
	m_dborders.resize(m_nabss, 0.0);

    vector<tuple<string, double>> ftmp(1);
	for(int n = 0; n < m_nabss; n++){
		m_generic[n] = new GenericFilterTransmission();
        ftmp[0] = filters[n];
		m_generic[n]->SetMaterials(ftmp, materials);
		m_dborders[n] = get<1>(filters[n]);
		if(n > 0){
			m_dborders[n] += m_dborders[n-1];
		}
	}
}

GenericAbsorber::~GenericAbsorber()
{
	for(int n = 0; n < m_nabss; n++){
		if(m_generic[n] != nullptr){
			delete m_generic[n];
		}
	}
}

int GenericAbsorber::GetTargetLayer(double depth, double *reldepth)
{
	*reldepth = 0;
	if(depth < 0){
		return -1;
	}
	int nlayer = -1;
	for(int n = 0; n < m_nabss; n++){
		if(m_dborders[n] > depth){
			*reldepth = depth;
			if(n > 0){
				*reldepth -= m_dborders[n-1];
			}
			nlayer = n;
			break;
		}
	}
	if(nlayer < 0){
		nlayer = m_nabss;
	}
	return nlayer;
}

double GenericAbsorber::GetAbsorption(
    int tgtlayer, double reldepth, double ep, double *leff)
{
	if(tgtlayer < 0 || tgtlayer >= m_nabss || ep < INFINITESIMAL){
		return 0;
	}

	double linabscoef, linheatcoef, cudepth, tex = 0;
	for(int n = 0; n <= tgtlayer; n++){
		m_generic[n]->GetTransmission(ep, &linabscoef, &linheatcoef);
		if(n == tgtlayer){
			cudepth = reldepth;
		}
		else{
			cudepth = n == 0 ? m_dborders[n] : m_dborders[n]-m_dborders[n-1];
		}
        if(leff != nullptr){
            cudepth *= *leff;
        }
		tex += cudepth*linabscoef;
	}
	if(tex > MAXIMUM_EXPONENT){
		return 0;
	}
	return exp(-tex)*linheatcoef;
}

double GenericAbsorber::GetTotalAbsorption(double ep)
{
	if(ep < INFINITESIMAL){
		return 1.0;
	}
    double linabscoef, linheatcoef, cudepth, tex = 0;
	for(int n = 0; n < m_nabss; n++){
		m_generic[n]->GetTransmission(ep, &linabscoef, &linheatcoef);
		cudepth = n == 0 ? m_dborders[n] : m_dborders[n]-m_dborders[n-1];
		tex += cudepth*linheatcoef;
	}
    if(tex == 0){
        return 1.0;
    }
    return 1.0-exp(-tex);
}


GenericFilterTransmission *GenericAbsorber::GenFilter(int layer)
{
	return m_generic[layer];
}

//------------------------------------------------------------------------------
FilterOperation::FilterOperation(SpectraSolver &spsolver, bool isabs)
    : FunctionDigitizer(1), SpectraSolver(spsolver)
{
#ifdef _DEBUG
//FilterPowerInteg = "..\\debug\\filtered_power_integ.dat";
//IntegFilterEConv = "..\\debug\\filter_econv.dat";
//FuncFilterEConv = "..\\debug\\func_econv.dat";
#endif

    m_isBPFGauss = m_confsel[filter_] == BPFGaussianLabel;
    m_isBPFBox = m_confsel[filter_] == BPFBoxCarLabel;
    m_isgeneric = m_confsel[filter_] == GenFilterLabel;
    m_isCustom = m_confsel[filter_] == CustomLabel;
    m_ispowabs = false;
    if(isabs && m_absorbers.size() > 0){
        m_isgeneric = true;
        m_isBPFGauss = m_isBPFBox = m_isCustom = false;
        m_filters = m_absorbers;
    }

    if(m_isgeneric){
		GetTransmissionRate = &FilterOperation::f_GetGeneric;
        f_AllocateGeneric();
    }
    else if(m_isBPFGauss || m_isBPFBox){
		GetTransmissionRate = &FilterOperation::f_GetBPF;
        f_AllocateBPF();
    }
    else if(m_isCustom){
		GetTransmissionRate = &FilterOperation::f_GetCustom;
        f_AllocateCustom();
    }
    else{
        return;
    }

    m_maxdatapoints = 100; // initial memory allocation
    m_energy.resize(m_maxdatapoints);
    m_flux.resize(m_maxdatapoints);
    m_pointsgauss = 64<<(m_accuracy[accinpE_]-1);
    InitializeQGauss(MAX_POINTS_FILTER_CONV_GAUSSQ, 1);

    if(m_ispower){
        f_AllocateEConvolutedRate();
    }
}

double FilterOperation::GetFilteredPower(
    int energymesh, vector<double> *energy, vector<double> *flux)
{
    int m, n, nn, npointsfilter, npointsflux, nini, nfin;
    double eini, efin, rflux, rate;

#ifdef _DEBUG
	ofstream debug_out;
	if(!FilterPowerInteg.empty()){
		debug_out.open(FilterPowerInteg);
	}
    vector<double> tmp(2);
#endif

    double rpower = 0.0;

    m_efluxspline.SetSpline(energymesh, energy, flux);
    if(m_isgeneric){
        f_AllocateMaximumEnergy4GenericFilter((*energy)[energymesh-1]);
    }

    for(m = 0; m < m_regions; m++){
        if(m_efluxspline.GetIniXY() >= m_filtercvspline[m].GetFinXY()){
            continue;
        }
        else if(m_efluxspline.GetFinXY() <= m_filtercvspline[m].GetIniXY()){
            continue;
        }
        eini = max(m_filtercvspline[m].GetIniXY(), m_efluxspline.GetIniXY());
        efin = min(m_filtercvspline[m].GetFinXY(), m_efluxspline.GetFinXY());
        npointsfilter = m_filtercvspline[m].GetPointsInRegion(eini, efin)+2;
        npointsflux = m_efluxspline.GetPointsInRegion(eini, efin)+2;

        if(max(npointsfilter, npointsflux) > m_maxdatapoints){
            m_maxdatapoints = max(npointsfilter, npointsflux);
            m_energy.resize(m_maxdatapoints);
            m_flux.resize(m_maxdatapoints);
        }

        if(npointsfilter > npointsflux){ // the input spectrum has too few data points
            nini = m_filtercvspline[m].GetIndexXcoord(eini)+1;
            nfin = m_filtercvspline[m].GetIndexXcoord(efin);
            nn = -1;
            if(eini < m_filtercvspline[m].GetXYItem(nini)){
                m_energy[++nn] = eini;
                rflux = m_efluxspline.GetValue(m_energy[nn]);
                rate = GetTransmissionRateCV(m_energy[nn], true, m);
                m_flux[nn] = rflux*rate;
#ifdef _DEBUG
                tmp[0] = m_flux[nn]; tmp[1] = rate;
                PrintDebugItems(debug_out, m_energy[nn], tmp);
#endif
            }
            for(n = nini; n <= nfin; n++){
                m_energy[++nn] = m_filtercvspline[m].GetXYItem(n);
                rflux = m_efluxspline.GetValue(m_energy[nn]);
                rate = GetTransmissionRateCV(m_energy[nn], true, m, n);
                m_flux[nn] = rflux*rate;
#ifdef _DEBUG
                tmp[0] = m_flux[nn]; tmp[1] = rate;
                PrintDebugItems(debug_out, m_energy[nn], tmp);
#endif
            }
            if(efin > m_filtercvspline[m].GetXYItem(nfin)){
                m_energy[++nn] = efin;
                rflux = m_efluxspline.GetValue(m_energy[nn]);
                rate = GetTransmissionRateCV(m_energy[nn], true, m);
                m_flux[nn] = rflux*rate;
#ifdef _DEBUG
                tmp[0] = m_flux[nn]; tmp[1] = rate;
                PrintDebugItems(debug_out, m_energy[nn], tmp);
#endif
            }
        }
        else{ // the input spectrum has a lot of data points
            nini = m_efluxspline.GetIndexXcoord(eini)+1;
            nfin = m_efluxspline.GetIndexXcoord(efin);
            nn = -1;
            if(eini < m_efluxspline.GetXYItem(nini)){
                m_energy[++nn] = eini;
                rflux = m_efluxspline.GetValue(m_energy[nn]);
                rate = GetTransmissionRateCV(m_energy[nn], true, m);
                m_flux[nn] = rflux*rate;
#ifdef _DEBUG
                tmp[0] = m_flux[nn]; tmp[1] = rate;
                PrintDebugItems(debug_out, m_energy[nn], tmp);
#endif
            }
            for(n = nini; n <= nfin; n++){
                m_energy[++nn] = m_efluxspline.GetXYItem(n);
                rflux = m_efluxspline.GetXYItem(n, false);
                rate = GetTransmissionRateCV(m_energy[nn], true, m);
                m_flux[nn] = rflux*rate;
#ifdef _DEBUG
                tmp[0] = m_flux[nn]; tmp[1] = rate;
                PrintDebugItems(debug_out, m_energy[nn], tmp);
#endif
            }
            if(efin > m_efluxspline.GetXYItem(nfin)){
                m_energy[++nn] = efin;
                rflux = m_efluxspline.GetValue(m_energy[nn]);
                rate = GetTransmissionRateCV(m_energy[nn], true, m);
                m_flux[nn] = rflux*rate;
#ifdef _DEBUG
                tmp[0] = m_flux[nn]; tmp[1] = rate;
                PrintDebugItems(debug_out, m_energy[nn], tmp);
#endif
            }
        }
        m_fluxfilterspline.SetSpline(nn, &m_energy, &m_flux);
        rpower += m_fluxfilterspline.Integrate();
    }
    return rpower;
}

/*
double FilterOperation::GetMaxEnergyAndAllocateMethod4Power(double ec, double eps, bool isapplymethod)
{
    double rate, ifluxtrns, ifluxabs, fluxabs, fluxtrns, epr = 1.0;
    vector<double> fhvc(4);
	bool isabs, istrns;

	ifluxtrns = ifluxabs = INFINITESIMAL;
    while(1){
        BMWigglerRadiation::GetBMStokes(epr, 0.0, &fhvc);
        rate = 0.5*(f_GetGeneric(epr*ec)+f_GetGeneric(epr*ec-5.0)); // to avoid edge absorbtion
        fluxabs = fhvc[0]*(1.0-rate);
        fluxtrns = fhvc[0]*rate;
        ifluxabs += fluxabs;
        ifluxtrns += fluxtrns;
		istrns = (INFINITESIMAL+fluxtrns)/ifluxtrns < eps;
		isabs = (INFINITESIMAL+fluxabs)/ifluxabs < eps;
		if(isapplymethod && (isabs || istrns)){
			break;
		}
		else if(m_ispowmeth_abs && isabs){
			break;
		}
		else if(!m_ispowmeth_abs && istrns){
			break;
		}
        epr *= 1.2;
    }
    f_AllocateMaximumEnergy4GenericFilter(ec*epr);
    if(isapplymethod){
        m_ispowmeth_abs = isabs;
    }
    return ec*epr;
}
*/

void FilterOperation::GetEnergyRange4Power(double ec, double eps, double erange[])
{
    double rate[2], iflux[2], flux[2], epr;
    vector<double> fhvc(4);
	bool isconv[2];
    int iat = 0;

	iflux[0] = iflux[1] = INFINITESIMAL;
    double incrate[2] = {0.3, 1.2};
    for(int i = 1; i >= 0; i--){
        epr = i == 1 ? 1.0 : incrate[0];
        while (1){
            BMWigglerRadiation::GetBMStokes(epr, 0.0, &fhvc);
            rate[0] = 0.5*(f_GetGeneric(epr*ec)+f_GetGeneric(epr*ec-5.0)); // to avoid edge absorbtion
            rate[1] = 1.0-rate[0];
            for(int j = 0; j < 2; j++){
                flux[j] = fhvc[0]*rate[j];
                iflux[j] += flux[j];
                isconv[j] = (INFINITESIMAL+flux[j])/iflux[j] < eps;
            }
            if(i == 0){
                if(isconv[iat]){
                    break;
                }
            }
            else{
                for(int j = 0; j < 2; j++){
                    // determines the method: absorbed or transmitted
                    // target item should be lower than another
                    isconv[j] = isconv[j] && iflux[j] < iflux[1-j];
                }
                if(isconv[0] || isconv[1]){
                    break;
                }
            }
            epr *= incrate[i];
        }
        if(i == 1){
            iat = isconv[0] ? 0 : 1;
        }
        erange[i] = ec*epr;
    }
    m_ispowabs = iat == 1;
    f_AllocateMaximumEnergy4GenericFilter(erange[1]);
}

double FilterOperation::GetTransmissionRateF(double ep)
{
    return (this->*GetTransmissionRate)(ep);
}

double FilterOperation::GetTransmissionRateCV(double ep, bool isopt, int region, int index)
{
    double rate;

    if(ep < m_ecvboundary[0] || ep > m_ecvboundary[1]){
        rate = (this->*GetTransmissionRate)(ep);
        return m_ispowabs ? 1.0-rate : rate;
    }
    if(!m_isgeneric){
        region = 0;
    }
    if(region < 0){
        region = SearchIndex(m_regions+1, false, m_eregborder, ep);
    }
    if(index > 0){
        rate = m_filtercvspline[region].GetXYItem(index, false);
    }
    else{
        rate = m_filtercvspline[region].GetOptValue(ep);
    }
    return m_ispowabs ? 1.0-rate : rate;
}

void FilterOperation::IntegrandGauss(double ep, vector<double> *rate)
{
    double eprof;
    eprof = EnergyProfile(m_epref, ep);
    ep = f_GetEpInRange(ep);
    (*rate)[0] = eprof*(this->*GetTransmissionRate)(ep);
}

double FilterOperation::Function4Digitizer(double ep, vector<double> *rate)
{
    int m, npointsg;
    double elimini, elimfin, eintini, eintfin, desigma;
    vector<double> ratecv(1);

    desigma = EnergySpreadSigma(ep);

    if(desigma < INFINITESIMAL || ep < INFINITESIMAL){
        ep = f_GetEpInRange(ep);
        (*rate)[0] = (this->*GetTransmissionRate)(ep);
        return (*rate)[0];
    }

    m_epref = ep;
    elimini = ep-desigma*m_nlimit[acclimpE_];
    elimfin = ep+desigma*m_nlimit[acclimpE_];

    (*rate)[0] = 0.0;
    for(m = 0; m < m_regions; m++){
        m_currregion = m;
        if(m_eregborder[m] > elimfin || m_eregborder[m+1] < elimini){
            continue;
        }
        eintini = max(elimini, m_eregborder[m]);
        eintfin = min(elimfin, m_eregborder[m+1]);
        npointsg = m_pointsgauss*((int)floor((eintfin-eintini)/desigma)+1)+1;
        IntegrateGauss(npointsg, eintini, eintfin, &ratecv, IntegFilterEConv);
        (*rate)[0] += ratecv[0];
    }
    return (*rate)[0];
}

void FilterOperation::GetEnergyRange(double *epmin, double *epmax)
{
    *epmin = m_eregborder[0];
    *epmax = m_eregborder[m_regions];
}

double FilterOperation::GetRegionBorder(int region)
{
    return m_eregborder[region];
}

int FilterOperation::GetNumberOfRegions()
{
    return m_regions;
}

void FilterOperation::GetTransmissionData(
    vector<double> &ep, vector<double> &trans)
{
    if(m_isCustom){
        m_filterspline.GetArrays(&ep, &trans);
        return;
    }

    double eprange[2], de, fe;
    bool isauto = true;
    int npoints;

    isauto = m_ppconfsel[filtauto_] == AutomaticLabel;
    if(!isauto){
        eprange[0] = m_ppconf[filtemin_];
        eprange[1] = m_ppconf[filtemax_];
        npoints = max(2, (int)floor(0.5+m_ppconf[filtpoints_]));
        ep.resize(npoints);
        trans.resize(npoints);
        bool islog = m_ppconfsel[filtscale_] == LogLabel;
        double de = islog ? log(eprange[1]/eprange[0])/(npoints-1) : (eprange[1]-eprange[0])/(npoints-1);
        for(int n = 0; n < npoints; n++){
            ep[n] = islog ? eprange[0]*exp(n*de) : eprange[0]+de*n;
            trans[n] = (this->*GetTransmissionRate)(ep[n]);
        }
        return;
    }

    GetEnergyRange(&eprange[0], &eprange[1]);
    npoints = m_accuracy[accinpE_]*100*m_regions+1;
    de  = (eprange[1]-eprange[0])/(npoints-1);

    if(m_isBPFBox || m_isBPFGauss){
        if(m_isBPFBox){
            double DE = eprange[1]-eprange[0];
            eprange[0] -= DE*0.1;
            eprange[1] += DE*0.1;
        }
        ep.resize(npoints);
        trans.resize(npoints);
        for(int n = 0; n < npoints; n++){
            ep[n] = eprange[0]+de*n;
            trans[n] = (this->*GetTransmissionRate)(ep[n]);
        }
        return;
    }

    int n  = 0;
    bool islog = false;
    double eclim = GetCriticalEnergy()*5.0;
    do{
        if(islog){
            ep.push_back(ep[n-1]);
            ep[n] *= fe;
        }
        else{
            ep.push_back(eprange[0]+n*de);
        }
        if(!islog && ep[n] > eprange[1]){
            islog = true;
            fe = 1.0+de/ep.back();
        }
        trans.push_back((this->*GetTransmissionRate)(ep[n]));
        n++;
    }while(ep.back() < eclim && (fabs(1-trans.back()) > 0.05 || n < npoints));
}

//---------- private functions ----------
void FilterOperation::f_AllocateEConvolutedRate()
{
    int m;
    vector<double> etmp;
    vector<vector<double>> rtmp;
    vector<double> srtmp(2);
    double eini, efin, eref;

    m_ndatapoints.resize(m_regions);
    m_filtercvspline.resize(m_regions);
    for(m = 0; m < m_regions; m++){
        eini = m_eregborder[m];
        efin = m_eregborder[m+1];
        if(!m_isgeneric){
            eini -=  EnergySpreadSigma(eini)*m_nlimit[acclimpE_];
            efin +=  EnergySpreadSigma(efin)*m_nlimit[acclimpE_];
        }
        if(m == 0){
            m_ecvboundary[0] = eini;
        }
        if(m == m_regions-1){
            m_ecvboundary[1] = efin;
        }
        eref = (m_isBPFGauss || m_isBPFBox) ? m_conf[bpfcenter_] : efin;
        m_currregion = m;

		double xrange[NumberFStepXrange] = {0.0, eini, efin, eref, fabs(efin-eini)*1.0e-6};
		double eps[2] = {0.1, 0.0};
        m_ndatapoints[m] = RunDigitizer(FUNC_DIGIT_BASE, 
            &etmp, &rtmp, xrange, 31, eps, nullptr, 0, FuncFilterEConv);
        m_filtercvspline[m].SetSpline(m_ndatapoints[m], &etmp, &rtmp[0]);
    }
}

void FilterOperation::f_AllocateBPF()
{
    double maxwidth;

    if(m_confsel[filter_] == BPFGaussianLabel){
        maxwidth = m_conf[bpfsigma_]*m_nlimit[acclimpE_];
    }
    else{
        maxwidth = 0.5*m_conf[bpfwidth_];
    }

    m_regions = 1;
    m_eregborder.resize(2);
    m_eregborder[0] = max(0.0, m_conf[bpfcenter_]-maxwidth);
    m_eregborder[1] = m_conf[bpfcenter_]+maxwidth;
}

void FilterOperation::f_AllocateCustom()
{
    vector<double> ep, trans;
    m_customfilter.GetArray1D(0, &ep);
    m_customfilter.GetArray1D(1, &trans);
    m_filterspline.SetSpline((int)ep.size(), &ep, &trans, false, false, true);
    m_regions = 1;
    m_eregborder.resize(2);
    m_eregborder[0] = m_filterspline.GetIniXY();
    m_eregborder[1] = m_filterspline.GetFinXY();
}

void FilterOperation::f_AllocateGeneric()
{
    int j, i, m;
    double energy[9], xsec[11], fl_yield[4];
    double delimit;
    char error[256];
    vector<int> znumber;
    set<double> edge_energy, edge_energycv;

    m_genericf.SetMaterials(m_filters, m_materials);
    m_elements = m_genericf.GetElements();
    znumber = m_genericf.GetZnumbers();

    for(i = 0; i < m_elements; i++){
        for(j = 0; j < 9; j++){
            energy[j] = 0.0;
        }
        mucal("", znumber[i], 5.0, 'c', 0, energy, xsec, fl_yield, error);
        for(j = 0; j < 9; j++){
            if(energy[j] > 0.0){
                edge_energy.insert(energy[j]*1.0e+3); // keV->eV
            }
        }
    }
    for(set<double>::iterator itr = edge_energy.begin(); itr != edge_energy.end(); itr++){
        delimit = EnergySpreadSigma(*itr)*m_nlimit[acclimpE_];
        edge_energycv.insert((*itr)-delimit);
        if(delimit > INFINITESIMAL){
            edge_energycv.insert((*itr)+delimit);
        }
    }

    m_regions = (int)edge_energycv.size()+1;
    m_eregborder.resize(m_regions+1);
    m_eregborder[0] = 0.0;
    m = 0;
    for(set<double>::iterator itr = edge_energycv.begin(); itr != edge_energycv.end(); itr++){
        m_eregborder[++m] = *itr;
    }
    m_eregborder[m_regions] = m_eregborder[m_regions-1]+max(
        EnergySpreadSigma(m_eregborder[m_regions])*m_nlimit[acclimpE_],
        1000.0); // initial maximum energy: 1keV higher than the highest edge
}

void FilterOperation::f_AllocateMaximumEnergy4GenericFilter(double epmax)
{
    double eini, efin;
    vector<double> etmp;
    vector<vector<double>> rtmp;
	double eps[2] = {0.1, 0.0};

    if(epmax > m_eregborder[m_regions]){
        eini = m_eregborder[m_regions-1];
        efin = epmax;
        efin += EnergySpreadSigma(efin)*m_nlimit[acclimpE_]*2.0;
        m_eregborder[m_regions] = efin;

		double xrange[NumberFStepXrange] = {0.0, eini, efin, efin, fabs(efin-eini)*1.0e-6};
		m_ndatapoints[m_regions-1] = RunDigitizer(FUNC_DIGIT_BASE, 
            &etmp, &rtmp, xrange, 101, eps, nullptr, 0, FuncFilterEConv);
        m_filtercvspline[m_regions-1].SetSpline(m_ndatapoints[m_regions-1], &etmp, &rtmp[0]);
    }
}

double FilterOperation::f_GetBPF(double ep)
{
    double rate, tex;

    if(m_isBPFGauss){
        tex = (ep-m_conf[bpfcenter_])/m_conf[bpfsigma_];
        tex *= tex*0.5;
        if(tex > MAXIMUM_EXPONENT){
            rate = 0.0;
        }
        else{
            rate = m_conf[bpfmaxeff_]*exp(-tex);
        }
    }
    else{
        rate = 
            (ep < m_eregborder[0] || ep > m_eregborder[1]) ? 0.0 : m_conf[bpfmaxeff_];
    }
    return rate;
}

double FilterOperation::f_GetCustom(double ep)
{
    if((ep-m_filterspline.GetIniXY())*(ep-m_filterspline.GetFinXY()) > 0.0){
        return 0.0;
    }
    return m_filterspline.GetOptValue(ep);
}

double FilterOperation::f_GetGeneric(double ep)
{
    return m_genericf.GetTransmission(ep);
}

double FilterOperation::f_GetEpInRange(double ep)
{
    if(ep <= m_eregborder[m_currregion]){
        ep = m_eregborder[m_currregion]+0.01;
    }
    if(m_currregion < m_regions){
        if(ep >= m_eregborder[m_currregion+1]){
            ep = m_eregborder[m_currregion+1]-0.01;
        }
    }
    return ep;
}
