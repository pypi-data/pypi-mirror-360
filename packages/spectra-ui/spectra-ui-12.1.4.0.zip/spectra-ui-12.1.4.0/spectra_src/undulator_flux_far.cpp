#include <algorithm>
#include <set>
#include <math.h>
#include "undulator_flux_far.h"
#include "energy_convolution.h"
#include "interpolation.h"
#include "fast_fourier_transform.h"
#include "numerical_common_definitions.h"
#include "common.h"
#include "beam_convolution.h"


//UndulatorFluxFarField
string UFarBefFFT;
string UFarAftFFT;
string UFarInfPerSpec;
string FuncIntAlongPhi;
string FuncIntAlongGT;
string FuncIntAlongGTEconv;
string IntegUFarSN;

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

#define STEPS_INF_SPECTRUM_SEGMENTED 20
#define STEPS_INF_SPECTRUM_FINAL 95

//------------------------------------------------------------------------------
UndulatorFluxInfPeriods::UndulatorFluxInfPeriods(SpectraSolver &spsolver)
	: UndulatorFxyFarfield(spsolver)
{
#ifdef _DEBUG
//UFarBefFFT = "..\\debug\\und_far_bef_fft.dat";
//UFarAftFFT = "..\\debug\\und_far_aft_fft.dat";
//UFarInfPerSpec = "..\\debug\\und_far_inf_spec.dat";
//FuncIntAlongPhi = "..\\debug\\func_along_phi.dat";
//FuncIntAlongGT = "..\\debug\\func_along_gt.dat";
//FuncIntAlongGTEconv = "..\\debug\\func_along_gt_econv.dat";
//IntegUFarSN = "..\\debug\\flux_sn_integ.dat";
#endif

    m_ninit_alongphi = (10<<(m_accuracy[accinobs_]-1))+1;
    AllocateMemoryFuncDigitizer(m_fluxitems);

    m_fdarray.resize(m_fluxitems);

    if(hypotsq(m_center[0], m_center[1]) == 0){
        m_phiref[0] = 0;
    }
    else{
        m_phiref[0] = atan2(m_center[1], m_center[0]);
    }

    if(m_Nsymmetry == 4){
        m_phiref[1] = 0.0; m_phiref[2] = PId2;
        if(m_phiref[0]){
            m_phiref[0] = atan2(fabs(sin(m_phiref[0])), fabs(cos(m_phiref[0])));
        }
    }
    else if(m_Nsymmetry == 2 && m_symmetry[0]){
        m_phiref[1] = -PId2; m_phiref[2] = PId2;
        if(m_phiref[0]){
            m_phiref[0] = atan2(sin(m_phiref[0]), fabs(cos(m_phiref[0])));
        }
    }
    else if(m_Nsymmetry == 2 && m_symmetry[1]){
        m_phiref[1] = 0.0; m_phiref[2] = PI;
        if(m_phiref[0]){
            m_phiref[0] = atan2(fabs(sin(m_phiref[0])), cos(m_phiref[0]));
        }
    }
    else{
        m_phiref[1] = 0.0; m_phiref[2] = PI2;
    }
    m_eps_along_phi = 0.1/m_nfrac[accinobs_];
}

double UndulatorFluxInfPeriods::Function4Digitizer(double phi0, vector<double> *fd)
{
    int n, j;
    double xyint[2], phi, s45, conf = 1.0;
    vector<double> fxy(12);

    for(j = 0; j < m_fluxitems; j++){
        (*fd)[j] = 0.0;
    }
    for(n = 0; n < m_Nsymmetry; n++){
        if(n == 0){
            phi = phi0; s45 = 1.0;
        }
        else if(n == 1){
            s45 = -1.0;
            if(m_symmetry[0]){ // integration from 0 or -PI/2 to PI/2, the 2nd point symmetric to y axis
                phi = PI-phi0;
            }
            else{ // integration from 0 to PI, the 2nd point symmetric to x axis
                phi = PI2-phi0;
            }
        }
        else if(n == 2){
            phi = PI+phi0; s45 = 1.0;
        }
        else{
            phi = -phi0; s45 = -1.0;
        }
        xyint[0] = m_rint*cos(phi);
        xyint[1] = m_rint*sin(phi);
        if(m_bmconv->IsInit()){
            conf = m_bmconv->GetEBeamCovolutedProfile(xyint, false);
        }
        if(n == 0){
            if(m_isebconv){ // for BeamConvolution estimation
                for(j = 0; j < m_fluxitems; j++){
                    fxy[j] = 1.0;
                }
            }
            else{
                GetFxy(phi, &fxy);
            }
        }
        for(j = 0; j < m_fluxitems; j++){
            (*fd)[j] += conf*(j == 3 ? s45 : 1.0)*fxy[j];
        }
    }
    return (*fd)[0]+(*fd)[1];
}

void UndulatorFluxInfPeriods::IntegrateAlongPhi(
    int nh, double gt, vector<double> *fd, bool isebconv)
{
    int j;
    double philim = PI2*1.0e-4;

    m_isebconv = isebconv;
    m_gt = gt;
    m_rint = gt/m_conv2gt;
    SetCondition(nh, gt);

	double xrange[NumberFStepXrange] = 
		{0.0, m_phiref[1], m_phiref[2], m_phiref[0], philim};
	double eps[2] = {m_eps_along_phi, 0};

    vector<double> fint(m_fluxitems);
	RunDigitizer(FUNC_DIGIT_BASE, &m_phi, &m_fdarray,
        xrange, m_ninit_alongphi, eps, nullptr, 0, FuncIntAlongPhi, &fint);

    double cvgtsq = m_conv2gt*m_conv2gt;
    for(j = 0; j < m_fluxitems; j++){
        (*fd)[j] = fint[j]/cvgtsq;
    }
}

//------------------------------------------------------------------------------
UndulatorSpectrumInfPeriods::UndulatorSpectrumInfPeriods(
    SpectraSolver &spsolver, int rank, int mpiprocesses) : SpectraSolver(spsolver)
{
	m_skipintphi = m_accb[zeroemitt_] && !m_circslit && !m_rectslit;
	m_FluxInf = new UndulatorFluxInfPeriods(spsolver);
    m_EspreadConv = new EnergySpreadConvolution(this, m_fluxitems);
    AllocateMemoryFuncDigitizer(m_fluxitems);
    m_fdtmp.resize(m_fluxitems);
    m_ep1onaxis = GetE1st();
    m_e1stobs = GetE1st(m_gtcenter);

    m_eps_harmonic = 1.0e-2/(1<<(m_accuracy[accconvharm_]-1));
    m_eps_stepper = 0.1/((1<<m_accuracy[accinpE_])-1);

    m_epmax = max(m_confv[erange_][0], m_confv[erange_][1]);
    m_epallocmax = (m_epmax+m_nlimit[acclimpE_]*m_ep1onaxis*20.0/(double)m_N)
            *(1.0+2.0*GetEspreadRange());
    if(m_issegu){
        double gttf = max(m_GT[0], m_GT[1])+m_accuracy[acclimobs_];
        double e1stlow = GetE1st(gttf);
        m_nhmax = (int)ceil(m_epallocmax/e1stlow)+1;
    }
    else if(m_skipintphi){
        m_nhmax = (int)ceil(m_epallocmax/m_e1stobs)+1;
    }
    else{
        m_nhmax = (int)ceil(m_epallocmax/m_ep1onaxis)+1;
    }

	m_rank = rank;
	m_mpiprocesses = mpiprocesses;
}

UndulatorSpectrumInfPeriods::~UndulatorSpectrumInfPeriods()
{
    if(m_FluxInf != nullptr){
        delete m_FluxInf;
        m_FluxInf = nullptr;
    }
    if(m_EspreadConv != nullptr){
        delete m_EspreadConv;
        m_EspreadConv = nullptr;
    }
}

void UndulatorSpectrumInfPeriods::AllocateInfPeriodSpectrum(int layer)
{
    int nhmax, nh, ninit, nenergymeshorg, nenergymesh, n, j;
    double eplowlim1, eplowlim, dnh, epfin, epsneg;
    double deplim, deplimini;
    vector<double> etmp, etmporg;
    vector<vector<double>> fluxtmporg, fluxtmp;

    nhmax = m_nhmax;   
    epsneg = (double)(m_N*m_M);
    epsneg = 1.0e-3/epsneg/epsneg;

    m_eparray.resize(nhmax+1);
    m_fdmatrix.resize(nhmax+1);
    m_epmesh.resize(nhmax+1);

    fluxtmp.resize(m_fluxitems);
    fluxtmporg.resize(m_fluxitems);

    ninit = 30<<(m_accuracy[accinpE_]-1);
    deplim = m_ep1onaxis/(double)(m_N*m_M)*0.1;
    deplimini = GetE1st()-GetE1st(min(m_Esize[0], m_Esize[1])*m_conv2gt);
	deplimini /= 1<<(m_accuracy[acclimpE_]-1);
    deplimini = max(deplim*1.0e-10, deplimini);

    eplowlim1 = min(GetE1st(m_gtmax), 
        min(m_confv[erange_][0], m_confv[erange_][1])/(1.0+2.0*GetEspreadRange()));

    // check the profile of the infinite-period spectrum
    m_currnh = 1; m_checkebconv = true; m_espreadconv = false;
    for(nh = 1; nh <= nhmax; nh++){
        m_fdmatrix[nh].resize(m_fluxitems);
	}

	double xrange[NumberFStepXrange] = {0.0, eplowlim1, m_ep1onaxis, m_e1stobs, deplimini};
	double eps1[2] = {m_eps_stepper, epsneg};

    // allocate the infinite-period spectrum for each harmonic
	m_checkebconv = false;
    for(nh = 1+m_rank; nh <= nhmax; nh += m_mpiprocesses){
        dnh = (double)nh;
        eplowlim = eplowlim1*dnh;
        m_currnh = nh;
        if(!m_issegu){
            eplowlim = max(eplowlim, m_ep1onaxis*(double)(nh-1));
        }
        epfin = m_ep1onaxis*dnh;

		xrange[FstepXini] = eplowlim;
		xrange[FstepXfin] = epfin;
		xrange[FstepXref] = m_e1stobs*dnh;

		nenergymeshorg = 
			RunDigitizer(FUNC_DIGIT_BASE|FUNC_DIGIT_ENABLE_LOG, &etmporg, &fluxtmporg,
			xrange, ninit, eps1, m_calcstatus, layer+1, FuncIntAlongGT, nullptr, true);

		double maxfd = 0;
        for(n = 0; n < nenergymeshorg; n++){
			maxfd = max(maxfd, fluxtmporg[0][n]+fluxtmporg[1][n]);
		}

        for(j = 0; j < m_fluxitems; j++){
            fluxtmp[j].resize(nenergymeshorg);
        }
        etmp.resize(nenergymeshorg);
        nenergymesh = 0;
        for(n = 0; n < nenergymeshorg; n++){
            if((fluxtmporg[0][n]+fluxtmporg[1][n]+INFINITESIMAL)/(maxfd+INFINITESIMAL) > INFINITESIMAL){
                etmp[nenergymesh] = etmporg[n];
                for(j = 0; j < m_fluxitems; j++){
                    fluxtmp[j][nenergymesh] = fluxtmporg[j][n];
                }
                nenergymesh++;
            }
        }

        if(!m_iszspread){
            m_EspreadConv->AllocateInterpolant(nenergymesh, &etmp, &fluxtmp, false);
			xrange[FstepXini] = etmporg[0]/(1.0+2.0*GetEspreadRange());
			xrange[FstepXfin] = etmporg[nenergymeshorg-1]*(1.0+2.0*GetEspreadRange());
			xrange[FstepXref] = m_e1stobs*dnh;
            m_espreadconv = true;
			m_epmesh[nh] =
				RunDigitizer(FUNC_DIGIT_BASE|FUNC_DIGIT_ENABLE_LOG, &m_eparray[nh], &m_fdmatrix[nh],
				xrange, ninit, eps1, nullptr, 0, FuncIntAlongGTEconv);
			m_espreadconv = false;
        }
        else{
            m_epmesh[nh] = nenergymesh;
            m_eparray[nh].resize(m_epmesh[nh]);
            for(j = 0; j < m_fluxitems; j++){
                m_fdmatrix[nh][j].resize(m_epmesh[nh]);
            }
            for(n = 0; n < m_epmesh[nh]; n++){
                m_eparray[nh][n] = etmp[n];
                for(j = 0; j < m_fluxitems; j++){
                    m_fdmatrix[nh][j][n] = fluxtmp[j][n];
                }
            }
        }
		if(m_calcstatus != nullptr){
			m_calcstatus->AdvanceStep(layer);
		}
	}
	if(m_mpiprocesses > 1){
		MPI_Barrier(MPI_COMM_WORLD);
	}

    for(nh = 1; nh <= nhmax && m_mpiprocesses > 1; nh++){
        int trank = (nh-1)%m_mpiprocesses;
        if(m_thread != nullptr){
            m_thread->Bcast(&m_epmesh[nh], 1, MPI_INT, trank, m_rank);
        }
        else{
            MPI_Bcast(&m_epmesh[nh], 1, MPI_INT, trank, MPI_COMM_WORLD);
        }
        if(m_rank != trank){
            m_eparray[nh].resize(m_epmesh[nh]);
            for(j = 0; j < m_fluxitems; j++){
                m_fdmatrix[nh][j].resize(m_epmesh[nh]);
            }
        }
        if(m_thread != nullptr){
            m_thread->Bcast(m_eparray[nh].data(), m_epmesh[nh], MPI_DOUBLE, trank, m_rank);
            for(j = 0; j < m_fluxitems; j++){
                m_thread->Bcast(m_fdmatrix[nh][j].data(), m_epmesh[nh], MPI_DOUBLE, trank, m_rank);
            }
        }
        else{
            MPI_Bcast(m_eparray[nh].data(), m_epmesh[nh], MPI_DOUBLE, trank, MPI_COMM_WORLD);
            for(j = 0; j < m_fluxitems; j++){
                MPI_Bcast(m_fdmatrix[nh][j].data(), m_epmesh[nh], MPI_DOUBLE, trank, MPI_COMM_WORLD);
            }
        }
    }
}

double UndulatorSpectrumInfPeriods::Function4Digitizer(double ep, vector<double> *fd)
{

    if(m_espreadconv){
        m_EspreadConv->RunEnergyConvolution(ep, fd);
        return (*fd)[0]+(*fd)[1];
    }
    else if(m_checkebconv){ // get the profile of the projected beam integrated along azimuth
        return f_GetFxyFixedEnergyHarmonic(m_currnh, ep, fd, nullptr, true);
    }
    else if(m_issegu){
        return f_GetFxyFixedEnergyHarmonic(m_currnh, ep, fd, nullptr, false);
    }
    else{
        return f_GetFxyFixedEnergy(ep, fd);
    }
}

void UndulatorSpectrumInfPeriods::QSimpsonIntegrand(int layer, double ep, vector<double> *fd)
{
    f_GetFxyFixedEnergy(ep, fd);
}

double UndulatorSpectrumInfPeriods::f_GetFxyFixedEnergy(double ep, vector<double> *fd)
{
    double fsum = INFINITESIMAL, fxynh, fxynhold, eps, gt;
    int nh, j;

    fxynhold = fsum;
    nh = m_currnh;
    for(j = 0; j < m_fluxitems; j++){
        (*fd)[j] = 0.0;
    }

    do{
		f_GetFxyFixedEnergyHarmonic(nh, ep, &m_fdtmp, &gt, false);
        for(j = 0; j < m_fluxitems; j++){
            (*fd)[j] += m_fdtmp[j]*(ep/(double)nh/m_ep1onaxis);
        }
        fxynh = (m_fdtmp[0]+m_fdtmp[1])/(double)nh;
        fsum += fxynh;
        eps = (fxynh+fxynhold)/fsum;
        fxynhold = fxynh;
        nh++;
    }while((eps > m_eps_harmonic || gt < m_gttypical)
        || (double)(nh-1)*m_e1stobs < (double)m_currnh*m_ep1onaxis);

    return fsum;
}

double UndulatorSpectrumInfPeriods::f_GetFxyFixedEnergyHarmonic(
    int nh, double ep, vector<double> *fd, double *gt, bool ischeckebconv)
{
    double epdiv, uw;
    int j;

    if(ep == 0.0){
        uw = -1.0;
    }
    else{
        epdiv = ep/(double)nh;
        uw = COEF_E1ST*m_acc[eGeV_]*m_acc[eGeV_]/epdiv/m_lu-m_K2-1.0;
    }
    if(uw < -1.0e-6){
        for(j = 0; j < m_fluxitems; j++){
            (*fd)[j] = INFINITESIMAL;
        }
        if(gt != nullptr){ // finish this energy
            *gt = m_gttypical*2.0;
        }
        return ischeckebconv?INFINITESIMAL:INFINITESIMAL/(double)nh;
    }
    else{
        uw = max(0.0, uw);
    }
    uw = sqrt(uw);
    m_FluxInf->IntegrateAlongPhi(nh, uw, fd, ischeckebconv);
    for(j = 0; j < m_fluxitems; j++){
        (*fd)[j] *= (double)nh/ep/ep;
    }
    if(gt != nullptr){
        *gt = uw;
    }

    return ischeckebconv?(*fd)[0]:((*fd)[0]+(*fd)[1])/(double)nh;
}

//------------------------------------------------------------------------------
FluxSincFuncConvolution::FluxSincFuncConvolution(SpectraSolver *spsolver,
        int nh, int rank, int mpiprocesses)
{
    m_spsolver = spsolver;
    int level = m_spsolver->GetAccuracy(accinpE_);
    m_eps_simpson = 0.01/(1<<(level-1));
    m_eps_sum = 5.0e-2/(1<<(level-1));
    m_nh = nh;
	if(mpiprocesses > 1){
		ArrangeMPIConfig(rank, mpiprocesses, 1, spsolver->GetThread());
	}
    AllocateMemorySimpson(4, 4, 1);
}

void FluxSincFuncConvolution::QSimpsonIntegrand(int layer, double ep, vector<double> *flux)
{
    int j;
    double epr;
    vector<double> sn(3), fxy(12);

    for(j = 0; j < m_spsolver->GetFluxItms(); j++){
		fxy[j] = m_splfitem[j].GetOptValue(ep);
    }

    epr = m_epref/(ep/(double)m_nh);
    m_spsolver->GetSincFunctions(m_nh, epr, &sn);
    m_spsolver->MultiplySincFunctions(&fxy, &sn, flux);
}

void FluxSincFuncConvolution::AllocateInterpolant(long energymesh,
    vector<double> *energy, vector<vector<double>> *fluxin, bool isreg)
{
    int j;

    m_splfitem.resize(m_spsolver->GetFluxItms());
    for(j = 0; j < m_spsolver->GetFluxItms(); j++){
        m_splfitem[j].SetSpline(energymesh, energy, &((*fluxin)[j]), isreg);
    }
    m_epmax = (*energy)[energymesh-1];
    m_epmin = (*energy)[0];
}

void FluxSincFuncConvolution::RunSincFuncConvolution(double ep, double *fluxout)
{
    double erange[2], fluxr, eini, efin;
    vector<double> flux(4);
    vector<vector<double>> fluxtot(1);
	int j, npoints, nindex, ncurr, nrep = 0, layers[2] = {0, -1};

    m_epref = ep;
    for(j = 0; j < 4; j++){
        fluxout[j] = 0.0;
    }
    fluxtot[0].resize(2, 0.0);

    nindex = f_GetIndexMaximumEnergy(ep);

    if(nindex >= 0){
        ncurr = 0; // first integrate at ncurr = 0: integration around ep
    }
    else{
        ncurr = nindex;
    }

    do{
        f_GetIntegrationRange(ep, ncurr--, erange);
        eini = max(m_epmin, erange[0]);
        efin = min(m_epmax, erange[1]);
        npoints = abs(m_splfitem[0].GetIndexXcoord(efin)
                    -m_splfitem[0].GetIndexXcoord(eini))+1;
        npoints = max((int)(log((double)npoints)/log(2.0)), 4);
        if(erange[0] <= ep && erange[1] >= ep){
            npoints++;
        }
        if(eini >= efin){
            for(j = 0; j < 4; j++){
                flux[j] = 0.0;
            }
        }
        else{
            IntegrateSimpson(layers, eini, efin,
                m_eps_simpson, npoints+1, &fluxtot, &flux, IntegUFarSN, true);
        }
        for(j = 0; j < 4; j++){
            fluxout[j] += flux[j];
        }
        fluxr = fabs(flux[0]+flux[1])+INFINITESIMAL;
        fluxtot[0][0] = fabs(fluxout[0]+fluxout[1]);
        if(erange[1] <= m_epmin && nrep > 0) break;
        if(ncurr == 0){// skip ncurr = 0: <= already done
            ncurr = -1;
        }
        if(nindex > 0 && nrep == 0){// start integration in other region
            ncurr = nindex;
        }
        nrep++;
    } while(fluxr > fluxtot[0][0]*m_eps_sum || erange[1] > m_epmax);
}             

int FluxSincFuncConvolution::f_GetIndexMaximumEnergy(double epref)
{
    double erange[2];
    int index = 0;

    f_GetIntegrationRange(epref, index, erange);
    while(erange[1] < m_epmax || erange[0] >= m_epmax){
        index += epref < m_epmax ? 1 : -1;
        f_GetIntegrationRange(epref, index, erange);
    }
    return index;
}

void FluxSincFuncConvolution::f_GetIntegrationRange(
    double epref, int nindex, double *erange)
{
    double frac;
    double dnh = double(m_spsolver->GetPerios()*m_nh);

    for(int j = 0; j <= 1; j++){
        frac = 1.0-(double)(2*nindex-(1-2*j))*SINC_INTEG_DIVISION/dnh;
        if(frac < INFINITESIMAL){
            erange[j] = m_epmax*2.0;
        }
        else{
            erange[j] = epref/frac;
        }
    }
}

//------------------------------------------------------------------------------
UndulatorFluxFarField::UndulatorFluxFarField(
        SpectraSolver &spsolver, int layer, int rank, int mpiprocesses)
    : UndulatorSpectrumInfPeriods(spsolver, rank, mpiprocesses)
{
    int nh, psteps;

    if(m_issegu && m_calcstatus != nullptr){
        layer++;
        m_calcstatus->SetSubstepNumber(layer-1, 2);
    }

	psteps = m_nhmax;

	if(mpiprocesses > 1){
		psteps = m_nhmax/mpiprocesses+((m_nhmax%mpiprocesses) > 0 ? 1 : 0);
	}

	if(!m_issegu || m_skipintphi){
		psteps += m_fluxitems*2; // for fft
	}
	psteps++; // to get the final array
	if(m_calcstatus != nullptr){
		m_calcstatus->SetSubstepNumber(layer, psteps);
		m_calcstatus->PutSteps(layer, 0);
	}

    if (!m_skipintphi){
        AllocateInfPeriodSpectrum(layer);
    }
    if((!m_issegu) || m_skipintphi){
        f_GetSpectrumFT(layer);
    }
    else{
        m_FluxSincConv.resize(m_nhmax+1);
        for (nh = 1; nh <= m_nhmax; nh++){
            m_FluxSincConv[nh] = new FluxSincFuncConvolution(&spsolver, nh);
            m_FluxSincConv[nh]->AllocateInterpolant(
                m_epmesh[nh], &m_eparray[nh], &m_fdmatrix[nh], false);
        }
    }

    m_coef = GetFluxCoef();
    if(!m_skipintphi){
        m_coef *= 0.5*f_GetE1stBase();
    }

    if(m_issegu && m_calcstatus != nullptr){
        m_calcstatus->AdvanceStep(layer-1);
    }
}

UndulatorFluxFarField::~UndulatorFluxFarField()
{
    if(m_issegu){
        for(int nh = 1; nh < m_FluxSincConv.size(); nh++){
            if(m_FluxSincConv[nh] != nullptr){
                delete m_FluxSincConv[nh];
                m_FluxSincConv[nh] = nullptr;
            }
        }
    }
    else{
        if(m_fxy.size()){
            for(int j = 0; j < m_fluxitems; j++){
                if(m_fxy[j] != nullptr){
                    delete[] m_fxy[j];
                    m_fxy[j] = nullptr;
                }
            }
        }
    }
}

double UndulatorFluxFarField::GetFlux(double ep, vector<double> *flux)
{
    int nh, nhcenter, j, k;
    double fluxnh[5], fdnh, fdsum, fdnhold;

    if(!m_issegu || m_skipintphi){
        f_GetFluxFromSpline(ep, flux);
        return (*flux)[0]+(*flux)[1];
    }

    nhcenter = (int)floor(ep/m_ep1onaxis)+1;

    for(j = 0; j < 4; j++){
        (*flux)[j] = 0.0;
    }
    fdsum = 0.0;

    if(nhcenter > 1){
        m_FluxSincConv[1]->RunSincFuncConvolution(ep, fluxnh);
        for (j = 0; j < 4; j++){
            (*flux)[j] = fluxnh[j];
        }
        fdsum += fluxnh[0]+fluxnh[1];
    }

    double eps = 0.01/(1<<(m_accuracy[accconvharm_]-1));

    nh = nhcenter;
    for(k = -1; k <= 1; k += 2){
        fdnh = 0.0;
        do{
            fdnhold = fdnh;
            m_FluxSincConv[nh]->RunSincFuncConvolution(ep, fluxnh);
            for(j = 0; j < 4; j++){
                (*flux)[j] += fluxnh[j];
            }
            fdnh = fluxnh[0]+fluxnh[1];
            fdsum += fdnh;
            nh += k;
        } while(nh > 1 && nh <= m_nhmax && (fdsum <= INFINITESIMAL || fdnh+fdnhold > eps*fdsum));
        nh = nhcenter+1;
    }
    return (*flux)[0]+(*flux)[1];
}

void UndulatorFluxFarField::GetPeakFluxHarmonic(vector<int> *harmonicnumber,
    vector<double> *ep, vector<vector<double>> *flux)
{
    int nh, n, nini, nfin, npeak, i;
	double epeak, fpeak, epnh, epnhm1, fd;
	double ded = m_ep1onaxis;

    for(i = 1; i < harmonicnumber->size(); i++){
        nh = (*harmonicnumber)[i];
		ded = m_ep1onaxis*min(0.5, sqrt(hypotsq(1.0/(double)m_N, (double)nh*EnergySpreadSigma())));
		if(m_issegu){
            GetPeakFluxHarmonicSegmented(nh, &(*ep)[i], &(*flux)[i]);
        }
        else{
            epnh = (double)nh*m_ep1onaxis+ded;
            epnhm1 = (double)(nh-1)*m_ep1onaxis+ded;
            nini = m_FxySpline[1][1].GetIndexXcoord(epnhm1)+1;
            nfin = m_FxySpline[1][1].GetIndexXcoord(epnh)+1;
            fpeak = 0.0; npeak = nini;
            for(n = nini; n <= nfin; n++){
                fd = m_FxySpline[1][1].GetXYItem(n, false);
                if(fd > fpeak){
                    fpeak = fd;
                    npeak = n;
                }
            }
            if(npeak == nini){
                epeak = (double)nh*m_ep1onaxis;
            }
            else{
				m_FxySpline[1][1].GetPeakValue(npeak, &epeak, &fpeak, true);
            }
            if(epeak < epnhm1+ded){
                (*ep)[i] = -1.0;
            }
            else{
                (*ep)[i] = epeak;
                f_GetFluxFromSpline(epeak, &(*flux)[i]);
            }
        }
    }
}

void UndulatorFluxFarField::GetPeakFluxHarmonicSegmented(int nh, double *ek, vector<double> *flux)
{
    double ep, epmin, DE, de, fmax, epeak, fcurr, demin;
    double ep1, ep2, fcurr1, fcurr2;
    bool isupdated;
    vector<double> fluxtmp1(5), fluxtmp2(5);

    double deex = 1<<(m_accuracy[acclimpE_]-1);
    DE = m_ep1onaxis/(double)m_N*deex*3.0;
    de = m_ep1onaxis/(double)m_N/m_nfrac[accinpE_]/3.0;
    demin = m_ep1onaxis/(double)(m_N*m_M)/deex*1.0e-2;

    ep = m_ep1onaxis*(double)nh+DE;
    epmin = m_ep1onaxis*(double)nh-DE;

    fmax = GetFlux(ep, &fluxtmp1);
    epeak = ep;
    do{
        ep -= de;
        fcurr = GetFlux(ep, &fluxtmp1);
        isupdated = fcurr > fmax;
        if(isupdated){
            epeak = ep;
            fmax = fcurr;
            *flux = fluxtmp1;
        }
    }while(ep > epmin || isupdated);

    ep = epeak; fcurr = fmax;
    do {
        de *= 0.5;
        ep1 = ep-de; fcurr1 = GetFlux(ep1, &fluxtmp1);
        ep2 = ep+de; fcurr2 = GetFlux(ep2, &fluxtmp2);
        if(fcurr1 > fcurr){
            fcurr = fcurr1; ep = ep1;
            *flux = fluxtmp1;
        }
        if(fcurr2 > fcurr){
            fcurr = fcurr2; ep = ep2;
            *flux = fluxtmp2;
        }
    } while(de > demin);

    *ek = ep;
}

void UndulatorFluxFarField::GetUSpectrum(
    vector<double> *energy, vector<vector<double>> *flux, int layer, int rank, int mpiprocesses)
{
    *energy = SpectraSolver::m_eparray;
    flux->resize(4);
    for(int j = 0; j < 4; j++){
        (*flux)[j].resize(energy->size());
    }

    int nmesh = (int)energy->size();
    if(m_issegu && m_calcstatus != nullptr){
        layer++;
		m_calcstatus->SetSubstepNumber(layer, nmesh/mpiprocesses);
    }

    vector<double> ftmp(4);
    for(int n = 0; n < nmesh; n++){
        if(m_issegu && rank != (n%mpiprocesses)){
            continue;
        }
        GetFlux((*energy)[n], &ftmp);
        for(int j = 0; j < 4; j++){
            (*flux)[j][n] = ftmp[j]*m_coef;
        }
        if(m_issegu && m_calcstatus != nullptr){
            m_calcstatus->AdvanceStep(layer);
        }
    }

    if(m_issegu && mpiprocesses > 1){
        double ws[4];
        for (int n = 0; n < nmesh; n++){
            int currrank = n%mpiprocesses;
            if(rank == currrank){
                for (int j = 0; j < 4; j++){
                    ws[j] = (*flux)[j][n];
                }
            }
            if(m_thread != nullptr){
                m_thread->Bcast(ws, 4, MPI_DOUBLE, currrank, rank);
            }
            else{
                MPI_Bcast(ws, 4, MPI_DOUBLE, currrank, MPI_COMM_WORLD);
            }
            if(rank != currrank){
                for (int j = 0; j < 4; j++){
                    (*flux)[j][n] = ws[j];
                }
            }
        }
    }
}

void UndulatorFluxFarField::f_GetSpectrumFT(int layer)
{
    int j, nh, n, nepmax;
    double nu, snu, s0;
    vector<double> energy, flux, segfluxin(13), segfluxout(5);
#ifdef _DEBUG
	ofstream debug_out;
    vector<double> dtmp(9);
	if(!UFarBefFFT.empty()){
		debug_out.open(UFarBefFFT);
	}
#endif

    f_ArrangeFFT();

    if(!m_skipintphi){
        m_FxySpline.resize(m_nhmax+1);
        for(nh = 1; nh <= m_nhmax; nh++){
            m_FxySpline[nh].resize(4);
        }
        for(nh = 1; nh <= m_nhmax; nh++){
            for(j = 0; j < 4; j++){
                m_FxySpline[nh][j].SetSpline(
                    m_epmesh[nh], &m_eparray[nh], &m_fdmatrix[nh][j]);
				// to get the averaged flux, integrate the flux array and interpolate
				m_FxySpline[nh][j].Integrate(&m_fdmatrix[nh][j]);
                m_FxySpline[nh][j].SetSpline(
                    m_epmesh[nh], &m_eparray[nh], &m_fdmatrix[nh][j]);
            }
        }
    }

    FastFourierTransform fft(1, m_nfft);

    m_fxy.resize(m_fluxitems);
    for(j = 0; j < m_fluxitems; j++){
        m_fxy[j] = new double[m_nfft]();
    }
	f_AssignInfPeriodSpectrum();
	for(j = 0; j < m_fluxitems; j++){
		fft.DoRealFFT(m_fxy[j], 1);
		if(m_calcstatus != nullptr){
			m_calcstatus->AdvanceStep(layer);
		}
	}

    for(n = 0; n <= m_nfft/2; n++){
        nu = (double)n*m_dnu;
        if(fabs(nu) > m_numax){
            snu = 0.0;
        }
        else{
            snu = m_snumax*(1.0-fabs(nu)/m_numax);
        }
#ifdef _DEBUG
        if(!UFarBefFFT.empty()){
            if(n < m_nfft/2){
                dtmp[0] = snu;
                for (int j = 0; j < 4; j++){
                    dtmp[j] = m_fxy[j][2*n];
                }
                for (int j = 4; j < 8; j++){
                    dtmp[j] = n == 0 ? 0 : m_fxy[j][2*n+1];
                }
                PrintDebugItems(debug_out, nu, dtmp);
            }
        }
#endif
        for(j = 0; j < m_fluxitems; j++){
            if(n == m_nfft/2){
                m_fxy[j][1] *= snu;
            }
            else if(n == 0){
                m_fxy[j][0] *= snu;
            }
            else{
                m_fxy[j][2*n] *= snu;
                m_fxy[j][2*n+1] *= snu;
            }
        }
    }

    for(j = 0; j < m_fluxitems; j++){
        fft.DoRealFFT(m_fxy[j], -1);
		if(m_calcstatus != nullptr){
			m_calcstatus->AdvanceStep(layer);
		}
        for(n = 0; n < m_nfft; n++){
            m_fxy[j][n] *= 2.0/(double)m_nfft;
        }
    }

    nepmax = (int)ceil(m_epallocmax/m_de);
    energy.resize(nepmax+1); // energy[1] = 0
    flux.resize(nepmax+1); // flux[1] = flux(energy=0)
    for(n = 0; n <= nepmax; n++){
        energy[n] = (double)n*m_de;
    }

    if(m_skipintphi && m_issegu){
        vector<double> snc(3);
        for(n = 0; n <= nepmax; n++){
            GetSincFunctions(0, energy[n]/m_e1stobs, &snc);
            for(j = 0; j < m_fluxitems; j++){
                segfluxin[j] = m_fxy[j][n];
            }
            MultiplySincFunctions(&segfluxin, &snc, &segfluxout);
            for(j = 0; j < 4; j++){
                m_fxy[j][n] = segfluxout[j];
            }
        }
    }

#ifdef _DEBUG
    if(!UFarAftFFT.empty()){
        ofstream debug_outb(UFarAftFFT);
        vector<double> ftmp(4);
        for (n = 0; n <= nepmax; n++){
            for (int j = 0; j < 4; j++){
                ftmp[j] = m_fxy[j][n];
            }
            double eptmp = (double)n*m_de;
            PrintDebugItems(debug_outb, eptmp, ftmp);
        }
    }
#endif

    if(m_skipintphi){
        m_FxySpline.resize(1);
    }
    m_FxySpline[0].resize(4);
    for(j = 0; j < 4; j++){
        for(n = 0; n <= nepmax; n++){
            s0 = m_fxy[0][n]+m_fxy[1][n];
            if(j == 0){
                flux[n] = s0;
            }
            else{
                if(fabs(s0) < INFINITESIMAL){
                    flux[n] = n == 0 || n == nepmax ? 0.0 : 2.0;
                }
                else if(j == 1){
                    flux[n] = (m_fxy[0][n]-m_fxy[1][n])/s0;
                }
                else{
                    flux[n] = m_fxy[j][n]/s0;
                }
            }
        }
        for(n = 1; n < nepmax && j > 0; n++){
            if(fabs(flux[n])-1.0 > 1.0e-3){
                flux[n] = (flux[n-1]+flux[n+1])*0.5;
            }
        }
        m_FxySpline[0][j].SetSpline(nepmax+1, &energy, &flux, true);
    }
}

void UndulatorFluxFarField::f_ArrangeFFT()
{
    double epmaxd;

    if(m_skipintphi){
        m_snumax = m_e1stobs/(double)m_N;
        m_de = m_e1stobs/(double)(m_accuracy[accinpE_]*16*m_N*m_M);
    }
    else{
        m_snumax = m_ep1onaxis/(double)m_N;
        m_de = m_ep1onaxis/(double)(m_accuracy[accinpE_]*16*m_N*m_M);
    }

	m_numax = PI2/m_snumax;
    epmaxd = m_epallocmax*1.5;

    //---------- estimation of # flops for FFT
	m_ndata = (long)floor(epmaxd/m_de)+1;
	m_nfft = 1;
	while(m_nfft < m_ndata){
		m_nfft <<= 1;
	}
	m_dnu = PI2/(m_de*(double)m_nfft);
}

void UndulatorFluxFarField::f_AssignInfPeriodSpectrum()
{
    double ep, epi, epf, gt, phi, esigma, frac, ifluxi, ifluxf;
    int i, nh, n, j, nnh, dnnh, nnini, nnfin;
    vector<double> fxy(12);

    for(i = 0; i < m_nfft; i++){
        for(j = 0; j < m_fluxitems; j++){
            m_fxy[j][i] = 0.0;
        }
    }
    if(m_skipintphi){
        for(nh= 1; nh <= m_nhmax; nh++){
            if((double)nh*m_e1stobs > m_epallocmax){
                continue;
            }
            gt = m_conv2gt*sqrt(hypotsq(m_center[0], m_center[1]));
            if(gt > 0){
                phi = atan2(m_center[1], m_center[0]);
            }
            else{
                phi = 0.0;
            }
            m_FluxInf->SetCondition(nh, gt);
            m_FluxInf->GetFxy(phi, &fxy);
            nnh = (int)floor((double)nh*m_e1stobs/m_de+0.5);
            if(m_iszspread){
                for(j = 0; j < m_fluxitems; j++){
                    m_fxy[j][nnh] = fxy[j]/m_de;
                }
            }
            else{
                esigma = (double)nh*m_e1stobs*m_acc[espread_]*2.0;
                dnnh = (int)floor(m_nlimit[acclimpE_]*esigma/m_de)+1;
                nnini = max(1, nnh-dnnh);
                nnfin = min(m_nfft-1, nnh+dnnh);
                for(n = nnini; n <= nnfin; n++){
                    frac = EnergyProfile((double)n*m_de, (double)nh*m_e1stobs, m_de);
                    for(j = 0; j < m_fluxitems; j++){
                        m_fxy[j][n] += fxy[j]*frac;
                    }
                }
            }
        }
    }
    else{
        i = 0;
        while((ep = (double)i*m_de) <= m_epallocmax){
			epi = ep-0.5*m_de;
			epf = ep+0.5*m_de;
            for(nh= 1; nh <= m_nhmax; nh++){
                if(m_eparray[nh][0] > epf || m_eparray[nh][m_epmesh[nh]-1] < epi){
                    continue;
                }
                for(j = 0; j < 4; j++){
					ifluxi = m_FxySpline[nh][j].GetValue(epi, true);
					ifluxf = m_FxySpline[nh][j].GetValue(epf, true);
					if(j <= 1 && ifluxi > ifluxf){
						continue;
					}
					m_fxy[j][i] += (ifluxf-ifluxi)/m_de;
                }
            }
            i++;
        }
    }
#ifdef _DEBUG
    if(!UFarInfPerSpec.empty()){
        ofstream debug_out(UFarInfPerSpec);
        vector<double> ftmp(4);
        for (i = 0; i < m_nfft; i++){
            for (int j = 0; j < 4; j++){
                ftmp[j] = m_fxy[j][i];
            }
            double eptmp = (double)i*m_de;
            PrintDebugItems(debug_out, eptmp, ftmp);
        }
    }
#endif
}

void UndulatorFluxFarField::f_GetFluxFromSpline(double ep, vector<double> *flux)
{
    int j;
    double stokes[4];

    for(j = 0; j < 4; j++){
        stokes[j] = m_FxySpline[0][j].GetValue(ep);
        if(j == 0){
            stokes[j] = fabs(stokes[j]); // photon flux
        }
        else{
            stokes[j] = max(-1.0, min(1.0, stokes[j])); // degree of polarization
        }
    }
    (*flux)[0] = stokes[0]*(1.0+stokes[1])*0.5;
    (*flux)[1] = stokes[0]*(1.0-stokes[1])*0.5;
    (*flux)[2] = stokes[0]*stokes[2];
    (*flux)[3] = stokes[0]*stokes[3];
}