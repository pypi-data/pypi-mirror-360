#include <sstream>
#include <iomanip>
#include "spectra_solver.h"
#include "common.h"
#include "kvalue_operation.h"
#include "undulator_flux_far.h"
#include "energy_convolution.h"
#include "density_fixed_point.h"
#include "spatial_convolution.h"
#include "filter_operation.h"
#include "output_utility.h"
#include "bm_wiggler_radiation.h"
#include "wigner_function.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

KValueOperation::KValueOperation(SpectraSolver &spsolver)
	: SpectraSolver(spsolver)
{
	m_istbl = m_srcsel[gaplink_] == ImpGapTableLabel;
	if(m_istbl){
		m_istbl = m_gaptbl.GetDimension() >= 0;
		if(!m_istbl){
			m_isauto = true;
		}
	}
	else{
		m_isauto = m_srcsel[gaplink_] == AutomaticLabel;
	}
	if(IsFixedPoint()){
		if(m_isund){
			m_gapvar.resize(1);
			m_harmonics.resize(1);
			if (m_isf8){
				m_harmonics[0] = (int)floor(2.0*m_conf[hfix_]+0.5);
			}
			else{
				m_harmonics[0] = (int)floor(m_conf[hfix_]+0.5);
			}
		}
		else{
			m_eparray.resize(1);
			m_eparray[0] = m_fixep;
		}
	}
	else if(m_isund){
		f_SetVariables();
		m_srcb[apple_] = false;
		// K values set, so kill apple option
	}
}

void KValueOperation::GetSrcPerformance(
	vector<double> &energy, vector<vector<double>> &items, vector<string> &details)
{
	vector<vector<double>> energynh;
	vector<vector<vector<double>>> itemsnh;
	vector<int> itemindices;

	details.resize(0);

	if(m_isbm || m_iswiggler){
		GetSrcPerformanceBMWiggler(itemindices, items);
		energy = m_eparray;
		return;
	}
	else if(contains(m_calctype, menu::simpcalc)){
		GetSrcPerformanceTarget(itemindices, energynh, itemsnh);
	}
	else if(contains(m_calctype, menu::wigner)){
		GetWignerBrillianceCurve(itemindices, energynh, itemsnh);
	}
	else{
		GetPeakFluxTarget(itemindices, energynh, itemsnh);
	}

	if(contains(m_calctype, menu::allharm) == false){
		f_ExpandHarmonic(energynh, itemsnh, energy, items, details);
		return;
	}

	SetEnergyPoints(false, true);
	vector<double> energyraw;
	GetEnergyPoints(energyraw);

	energy.resize(0);
	double emin = minmax(energynh[0], false);
	for(int n = 0; n < energyraw.size(); n++){
		if(energyraw[n] < emin){
			continue;
		}
		energy.push_back(energyraw[n]);
	}

	int tgtitem, tgtindex = 1, hidx = 1;
	if(contains(m_calctype, menu::wigner)){
		tgtitem = WBrill_;
	}
	else{
		vector<int>::iterator itrgab = 
			find(itemindices.begin(), itemindices.end(), GABrill_);
		if (itrgab != itemindices.end()){
			tgtitem = GABrill_;
		}
		else{
			tgtitem = Flux_;
		}
	}

	for(int j = 0; j < itemindices.size(); j++){
		if(tgtitem == itemindices[j]){
			tgtindex = j;
		}
		if(Harmonic_ == itemindices[j]){
			hidx = j;
		}
	}
	
	vector<double> itemr;
	items.resize(itemindices.size());
	for(int j = 0; j < itemindices.size(); j++){
		items[j].resize(energy.size());
	}
	for(int n = 0; n < energy.size(); n++){
		f_RetriveHarmonic(energy[n], tgtindex, hidx, energynh, itemsnh, itemr);
		for (int j = 0; j < itemindices.size(); j++){
			items[j][n] = itemr[j];
		}
	}
}

void KValueOperation::GetSrcPerformanceBMWiggler(
	vector<int> &itemindices, vector<vector<double>> &items)
{
	double divxy[2], sizexy[2], Sizexy[2], Divxy[2], SizeSlice[2], fd[3];
	double srcarea, wavel;
	double values[NumberTitles];

	GetOutputItemsIndices(itemindices);
	vector<int>::iterator itr = find(itemindices.begin(), itemindices.end(), Energy_);
	if(itr != itemindices.end()){
		itemindices.erase(itr);
	}

	items.resize(itemindices.size());
	for(int j = 0; j < itemindices.size(); j++){
		items[j].resize(m_eparray.size());
	}

	vector<vector<double>> flux;
	DensityFixedPoint densfix(*this, nullptr, nullptr);
	SpatialConvolution spconv(*this, &densfix, 0, m_rank, m_mpiprocesses);
	spconv.GetValue(&flux);

	BMWigglerRadiation bmrad(*this, nullptr);

	double tfcoef = GetFluxCoef(true);

	// do not apply parallel computing
	for(int n = 0; n < m_eparray.size(); n++){
		GetSrcDivSize(m_eparray[n], divxy, sizexy, Divxy, Sizexy, nullptr, SizeSlice);
		srcarea = SizeSlice[0]*SizeSlice[1]*PI2*1.0e+6; // m^2 -> mm^2
		values[Sizex_] = Sizexy[0];
		values[Sizey_] = Sizexy[1];
		values[Divx_] = Divxy[0];
		values[Divy_] = Divxy[1];

		bmrad.TotalFlux(m_eparray[n], fd);
		values[Flux_] = fd[2]*tfcoef;
		values[Fldens_] = flux[0][n]+flux[1][n];
		values[GABrill_] = values[Fldens_]/srcarea;
		wavel = wave_length(m_eparray[n]);
		values[Cflux_] = values[GABrill_]*pow(wavel/2.0*1.0e+6, 2.0);
		values[Cpower_] = values[Cflux_]*m_eparray[n]*QE*(wavel*1.0e+6)*1.0e+3;

		double emnat = wavel/PI2/2.0;
		values[CohFractionX_] = emnat/PI2/values[Sizex_]/values[Divx_];
		values[CohFractionY_] = emnat/PI2/values[Sizey_]/values[Divy_];

		for (int j = 0; j < itemindices.size(); j++){
			items[j][n] = values[itemindices[j]];
		}
	}
}

void KValueOperation::GetWignerBrillianceCurve(vector<int> &itemindices,
	vector<vector<double>> &energy, vector<vector<vector<double>>> &items)
{
	vector<vector<double>> xyvar;
	vector<double> W;
	double values[NumberTitles];

	GetOutputItemsIndices(itemindices);
	vector<int>::iterator itr = find(itemindices.begin(), itemindices.end(), HEnergy_);
	if(itr != itemindices.end()){
		itemindices.erase(itr);
	}

	items.resize(m_harmonics.size());
	energy.resize(m_harmonics.size());
	for(int hidx = 0; hidx < m_harmonics.size(); hidx++){
		items[hidx].resize(itemindices.size());
		for(int j = 0; j < itemindices.size(); j++){
			items[hidx][j].resize(m_gapvar.size());
		}
		energy[hidx].resize(m_gapvar.size());
	}

	m_calcstatus->SetSubstepNumber(0,
		(int)(m_gapvar.size()*m_harmonics.size()/m_mpiprocesses));

	for(int n = 0; n < m_gapvar.size(); n++){
		if(!IsFixedPoint()){
			f_SetKvalues(n, values);
		}
		if(m_rank != n%m_mpiprocesses){
			continue;
		}
		for (int hidx = 0; hidx < m_harmonics.size(); hidx++){
			energy[hidx][n] = GetE1st()*m_harmonics[hidx];
			m_conf[hfix_] = m_harmonics[hidx];
			if (m_isf8){
				m_conf[hfix_] /= 2;
			}
			WignerFunctionCtrl wigctrl(*this, 1);
			wigctrl.GetPhaseSpaceProfile(xyvar, W);
			values[WBrill_] = W[0];
			values[Harmonic_] = m_harmonics[hidx];
			if(m_isf8){
				values[Harmonic_] *= 0.5;
			}
			for(int j = 0; j < itemindices.size(); j++){
				items[hidx][j][n] = values[itemindices[j]];
			}
			if(m_rank == 0){
				m_calcstatus->AdvanceStep(0);
			}
		}
	}

	if(m_mpiprocesses > 1){
		f_GatherMPIHarmonics((int)itemindices.size()+1, energy, items);
	}
}

void KValueOperation::GetSrcPerformanceTarget(vector<int> &itemindices,
	vector<vector<double>> &energy, vector<vector<vector<double>>> &items)
{
	double peaksn, divr, divxy[2], sizexy[2], Sizexy[2], Divxy[2];
	double srcangle, srcarea, wavel;
	vector<double> fd(4);
	double values[NumberTitles];

	GetOutputItemsIndices(itemindices);
	vector<int>::iterator itr = find(itemindices.begin(), itemindices.end(), HEnergy_);
	if(itr != itemindices.end()){
		itemindices.erase(itr);
	}

	items.resize(m_harmonics.size());
	energy.resize(m_harmonics.size());
	for(int hidx = 0; hidx < m_harmonics.size(); hidx++){
		items[hidx].resize(itemindices.size());
		for(int j = 0; j < itemindices.size(); j++){
			items[hidx][j].resize(m_gapvar.size());
		}
		energy[hidx].resize(m_gapvar.size());
	}

	m_calcstatus->SetSubstepNumber(0, (int)(m_gapvar.size()*m_harmonics.size()));

	// do not apply parallel computing
	for(int n = 0; n < m_gapvar.size(); n++){
		if(!IsFixedPoint()){
			f_SetKvalues(n, values);
		}
		UndulatorFxyFarfield undfxy(*this);
		SincFuncEspreadProfile snesprd(*this);
		double e1st = GetE1st();
		for (int hidx = 0; hidx < m_harmonics.size(); hidx++){
			values[Harmonic_] = m_harmonics[hidx];
			if(m_isf8){
				values[Harmonic_] *= 0.5;
			}
			undfxy.SetCondition(m_harmonics[hidx], 0);
			snesprd.GetPeakValueStdDeviation(m_harmonics[hidx], &peaksn, &divr);
			divr /= m_gamma;

			energy[hidx][n] = e1st*m_harmonics[hidx];
			GetSrcDivSize(energy[hidx][n], divxy, sizexy, Divxy, Sizexy, &divr);
			values[Cohsize_] = sizexy[0];
			values[Cohdiv_] = divxy[0];
            srcangle = Divxy[0]*Divxy[1]*PI2*1.0e+6; // rad^2->mrad^2
            srcarea = Sizexy[0]*Sizexy[1]*PI2*1.0e+6; // m^2 -> mm^2
			values[Sizex_] = Sizexy[0];
			values[Sizey_] = Sizexy[1];
			values[Divx_] = Divxy[0];
			values[Divy_] = Divxy[1];

            undfxy.GetFxy(0.0, &fd);
            values[Flux_] = (fd[0]+fd[1])*peaksn*PI2*divr*divr*1.0e+6*GetFluxCoef();
            values[Fldens_] = values[Flux_]/srcangle;
            values[GABrill_] = values[Fldens_]/srcarea;
			wavel = wave_length(energy[hidx][n]);
            values[Cflux_] = values[GABrill_]*pow(wavel/2.0*1.0e+6, 2.0);
            values[Cpower_] = values[Cflux_]*m_harmonics[hidx]*e1st*QE*(wavel*1.0e+6)*1.0e+3;
            values[Tpower_] = GetTotalPowerID();

			double emnat = wavel/PI2/2.0;
			values[CohFractionX_] = emnat/values[Sizex_]/values[Divx_];
			values[CohFractionY_] = emnat/values[Sizey_]/values[Divy_];

			for (int j = 0; j < itemindices.size(); j++){
				items[hidx][j][n] = values[itemindices[j]];
			}
			if(m_rank == 0){
				m_calcstatus->AdvanceStep(0);
			}
		}
	}
}

void KValueOperation::GetPeakFluxTarget(vector<int> &itemindices,
	vector<vector<double>> &energy, vector<vector<vector<double>>> &items)
{
	GetOutputItemsIndices(itemindices);
	vector<int>::iterator itr = find(itemindices.begin(), itemindices.end(), HEnergy_);
	if(itr != itemindices.end()){
		itemindices.erase(itr);
	}
	vector<int>::iterator itrgab = find(itemindices.begin(), itemindices.end(), GABrill_);
	bool isbrill = itrgab != itemindices.end();
	double values[NumberTitles];

	items.resize(m_harmonics.size());
	energy.resize(m_harmonics.size());
	for(int hidx = 0; hidx < m_harmonics.size(); hidx++){
		items[hidx].resize(itemindices.size());
		for(int j = 0; j < itemindices.size(); j++){
			items[hidx][j].resize(m_gapvar.size());
		}
		energy[hidx].resize(m_gapvar.size());
	}

	m_calcstatus->SetSubstepNumber(0, (int)ceil((double)m_gapvar.size()/m_mpiprocesses));

	for(int n = 0; n < m_gapvar.size(); n++){
		if(m_rank != n%m_mpiprocesses){
			continue;
		}
		bool skip = !f_SetKvalues(n, values);
		double e1st = GetE1st();
		if(skip){
			for (int hidx = 0; hidx < m_harmonics.size(); hidx++){
				energy[hidx][n] = values[Energycv_] = e1st*m_harmonics[hidx];
				values[Fldens_] = values[GABrill_] = values[Flux_]
					= values[Pl_] = values[Pc_] = values[Pl45_] = 0;
				values[Harmonic_] = m_harmonics[hidx];
				if (m_isf8){
					values[Harmonic_] *= 0.5;
				}
				if (m_rectslit && m_confsel[aperture_] == NormSlitLabel){
					values[AptDX_] = m_confv[slitapt_][0];
					values[AptDY_] = m_confv[slitapt_][1];
				}
				for (int j = 0; j < itemindices.size(); j++){
					items[hidx][j][n] = values[itemindices[j]];
				}
			}
			if (m_rank == 0){
				m_calcstatus->AdvanceStep(0);
			}
			continue;
		}

		SpectraSolver spsolver(*this);
		double emin, emax;
		if(contains(m_calctype, menu::allharm)){
			emin = min(m_confv[erange_][0], m_confv[erange_][1]);
			emax = max(m_confv[erange_][0], m_confv[erange_][1]);
			emin = max(0.0, emin-e1st);
			emax = emax+e1st;
		}
		else{
			emin = 0;
			emax = e1st*(1+m_harmonics.back());
		}
		spsolver.ResetEnergyPrms(emin, emax);
		UndulatorFluxFarField uflux(spsolver, 1);

		vector<double> energyr;
		vector<vector<double>> flux;
		uflux.GetUSpectrum(&energyr, &flux, 1);
		vector<double> fmax(m_harmonics.size(), 0.0);
		vector<int> eidx(m_harmonics.size(), -1);
		for(int m = 0; m < energyr.size(); m++){
			int ntgt = (int)floor(energyr[m]/e1st+0.5);
			if(ntgt >= m_harmonicmap.size()){
				continue;
			}
			int hidx = m_harmonicmap[ntgt];
			if(hidx < 0){
				continue;
			}
			double fd = flux[0][m]+flux[1][m];
			if(fmax[hidx] < fd){
				fmax[hidx] = fd;
				eidx[hidx]= m;
			}
		}
		vector<double> fd(4);
		double epeak, fc[3], divxy[2], sizexy[2], Sizexy[2], Divxy[2], srcarea;
		for(int hidx = 0; hidx < m_harmonics.size(); hidx++){
			int ei = eidx[hidx];
			if(ei < 0){
				epeak = e1st*m_harmonics[hidx];
				for(int j = 0; j < 4; j++){
					fd[j] = 0;
				}
			}
			else if(ei == 0 || ei == energyr.size()-1){
				epeak = energyr[ei];
				for(int j = 0; j < 4; j++){
					fd[j] = flux[j][ei];
				}
			}
			else{
				for(int k = 0; k < 3; k++){
					fc[k] = flux[0][ei-1+k]+flux[1][ei-1+k];
				}
				parabloic_peak(&epeak, energyr[ei-1], energyr[ei], energyr[ei+1], fc[0], fc[1], fc[2]);
				epeak = max(epeak, min(energyr[ei-1], energyr[ei+1]));
				epeak = min(epeak, max(energyr[ei-1], energyr[ei+1]));
				for(int j = 0; j < 4; j++){
					fd[j] = lagrange(epeak, energyr[ei-1], energyr[ei], energyr[ei+1], 
						flux[j][ei-1], flux[j][ei], flux[j][ei+1]);
				}
			}
			stokes(fd);
			energy[hidx][n] = e1st*m_harmonics[hidx];
			values[Energycv_] = epeak;
			values[Fldens_] = values[Flux_] = fd[0];
			if(isbrill){
				GetSrcDivSize(energy[hidx][n], divxy, sizexy, Divxy, Sizexy, nullptr);
				srcarea = Sizexy[0]*Sizexy[1]*PI2*1.0e+6; // m^2 -> mm^2
				values[GABrill_] = fd[0]/srcarea;
			}
			values[Pl_] = fd[1];
			values[Pc_] = fd[2];
			values[Pl45_] = fd[3];
			values[Harmonic_] = m_harmonics[hidx];
			if(m_isf8){
				values[Harmonic_] *= 0.5;
			}
			if(m_rectslit && m_confsel[aperture_] == NormSlitLabel){
				values[AptDX_] = m_confv[slitapt_][0];
				values[AptDY_] = m_confv[slitapt_][1];
			}
			for (int j = 0; j < itemindices.size(); j++){
				items[hidx][j][n] = values[itemindices[j]];
			}
		}
		if(m_rank == 0){
			m_calcstatus->AdvanceStep(0);
		}
	}

	if(m_mpiprocesses > 1){
		MPI_Barrier(MPI_COMM_WORLD);
		f_GatherMPIHarmonics((int)itemindices.size()+1, energy, items);
	}
}

void KValueOperation::GetFixedFlux(
	vector<double> &Kvalue, vector<vector<double>> &items)
{
	vector<int> itemindices;
	GetOutputItemsIndices(itemindices);
	vector<int>::iterator itr;
	int skipidx[] = {Kx_, Kvalue_};
	int kidx = 0;
	for(int j = 0; j < 2; j++){
		itr = find(itemindices.begin(), itemindices.end(), skipidx[j]);
		if(itr != itemindices.end()){
			kidx = skipidx[j];
			itemindices.erase(itr);
		}
	}
	double values[NumberTitles];

	items.resize(itemindices.size());
	for(int j = 0; j < itemindices.size(); j++){
		items[j].resize(m_gapvar.size());
	}
	Kvalue.resize(m_gapvar.size());

	vector<vector<double>> pvalue;
	vector<double> fd(4);

	m_calcstatus->SetSubstepNumber(0, (int)ceil((double)m_gapvar.size()/m_mpiprocesses));

	for(int n = 0; n < m_gapvar.size(); n++){
		if(m_rank != n%m_mpiprocesses){
			continue;
		}

		if(!f_SetKvalues(n, values)){
			Kvalue[n] = 0;
			for (int j = 0; j < itemindices.size(); j++){
				items[j][n] = 0;
			}
			continue;
		}
		SpectraSolver spsolver(*this);
		double e1st = spsolver.GetE1st();
		double emin = max(0.0, m_fixep-e1st*0.5);
		double emax = m_fixep+e1st*0.5;
		spsolver.ResetEnergyPrms(emin, emax);
		UndulatorFluxFarField uflux(spsolver, 1);
		vector<double> energyr;
		vector<vector<double>> flux;
		uflux.GetUSpectrum(&energyr, &flux, 1);

		int eidx = get_index4lagrange(m_fixep, energyr, (int)energyr.size());
		for(int j = 0; j < 4; j++){
			fd[j] = lagrange(m_fixep, 
				energyr[eidx-1], energyr[eidx], energyr[eidx+1],
				flux[j][eidx-1], flux[j][eidx], flux[j][eidx+1]);
		}
		stokes(fd);
		values[Fldens_] = values[Flux_] = fd[0];
		values[Pl_] = fd[1];
		values[Pc_] = fd[2];
		values[Pl45_] = fd[3];
		for (int j = 0; j < itemindices.size(); j++){
			items[j][n] = values[itemindices[j]];
		}
		Kvalue[n] = values[kidx];

		if(m_rank == 0){
			m_calcstatus->AdvanceStep(0);
		}
	}

	if(m_mpiprocesses > 1){
		f_GatherMPI((int)itemindices.size()+1, Kvalue, items);
	}
}

void KValueOperation::GetPower(
	vector<double> &e1st, vector<vector<double>> &items)
{
	vector<int> itemindices;
	GetOutputItemsIndices(itemindices);
	vector<int>::iterator itr = find(itemindices.begin(), itemindices.end(), HEnergy_);
	itemindices.erase(itr);
	double values[NumberTitles];

	items.resize(itemindices.size());
	for(int j = 0; j < itemindices.size(); j++){
		items[j].resize(m_gapvar.size());
	}
	e1st.resize(m_gapvar.size());

	vector<vector<double>> pvalue;
	bool isskip;

	m_calcstatus->SetSubstepNumber(0, (int)ceil((double)m_gapvar.size()/m_mpiprocesses));

	for(int n = 0; n < m_gapvar.size(); n++){
		if(m_rank != n%m_mpiprocesses){
			continue;
		}

		isskip = f_SetKvalues(n, values) == false;
		SpectraSolver spsolver(*this);
		e1st[n] = spsolver.GetE1st();
		if(m_isf8){
			e1st[n] *= 2.0;
		}
		if(isskip){
			for (int j = 0; j < itemindices.size(); j++){
				items[j][n] = 0;
			}
			continue;
		}
		FilterOperation filter(spsolver);
		DensityFixedPoint density(spsolver, nullptr, &filter);
		SpatialConvolution spconv(spsolver, &density, 1);
		spconv.GetValue(&pvalue);
		values[Pwdens_] = values[Power_] =  pvalue[0][0];
		if(m_confsel[filter_] != NoneLabel){
			values[Fpwdens_] = values[FPower_] = pvalue[1][0];
		}
		values[Tpower_] = spsolver.GetTotalPowerID();
		if(m_rectslit && m_confsel[aperture_] == NormSlitLabel){
			values[AptDX_] = m_confv[slitapt_][0];
			values[AptDY_] = m_confv[slitapt_][1];
		}

		for (int j = 0; j < itemindices.size(); j++){
			items[j][n] = values[itemindices[j]];
		}

		if(m_rank == 0){
			m_calcstatus->AdvanceStep(0);
		}
	}

	if(m_mpiprocesses > 1){
		f_GatherMPI((int)itemindices.size()+1, e1st, items);
	}
}

void KValueOperation::GetKxyValues(
	vector<double> &Kperp, vector<double> &gap, vector<vector<double>> &Kxy, bool setgap)
{
	m_gapvar.resize(Kperp.size());
	for(int j = 0; j < 2; j++){
		m_kxyvar[j].resize(Kperp.size());
	}
	for(int n = 0; n < Kperp.size(); n++){
		f_ArrangeGapK(&Kperp[n], &gap[n], n, setgap);
	}
	Kxy.resize(2);
	for(int j = 0; j < 2; j++){
		Kxy[j] = m_kxyvar[j];
	}
}

void KValueOperation::SetPowerLimit()
{
	SpectraConfig spconftmp(*this);
	vector<vector<double>> pp;
	double ratio = 1.0, eps = 0.02/m_nfrac[accinobs_];
	int nrep = 0;
	while(true){
		spconftmp.ConfigurePartialPower(ratio);
		SpectraSolver spsoltmp(spconftmp);
		DensityFixedPoint densfix(spsoltmp, nullptr, nullptr);
		SpatialConvolution spconv(spsoltmp, &densfix, 2);
		spconv.GetValue(&pp);
		if(nrep == 0 && pp[0][0] <= m_conf[pplimit_]){
			break;
		}
		else if(fabs(pp[0][0]-m_conf[pplimit_]) < m_conf[pplimit_]*eps){
			break;
		}
		nrep++;
		ratio = sqrt(m_conf[pplimit_]/pp[0][0]);
	}
	for (int j = 0; j < 2; j++){
		m_confv[slitapt_][j] = spconftmp.GetVector(ConfigLabel, slitapt_, j);
	}
}

// private functions
void KValueOperation::f_GatherMPIHarmonics(int nei, 
	vector<vector<double>> &variable, vector<vector<vector<double>>> &items)
{
	int nsize = nei*(int)m_harmonics.size();
	double *valuesend = new double[nsize];
	for(int n = 0; n < m_gapvar.size(); n++){
		int sendrank = n%m_mpiprocesses;
		if(m_rank == sendrank){
			for(int hidx = 0; hidx < m_harmonics.size(); hidx++){
				for(int j = 0; j < nei; j++){
					valuesend[j+hidx*nei] = j == nei-1 ? 
						variable[hidx][n] : items[hidx][j][n];
				}
			}
		}
		if(m_thread != nullptr){
			m_thread->Bcast(valuesend, nsize, MPI_DOUBLE, sendrank, m_rank);
		}
		else{
			MPI_Bcast(valuesend, nsize, MPI_DOUBLE, sendrank, MPI_COMM_WORLD);
		}
		if(m_rank != sendrank){
			for(int hidx = 0; hidx < m_harmonics.size(); hidx++){
				for(int j = 0; j < nei; j++){
					if(j == nei-1){
						variable[hidx][n] = valuesend[j+hidx*nei];
					}
					else{
						items[hidx][j][n] = valuesend[j+hidx*nei];
					}
				}
			}
		}
	}
	delete[] valuesend;
}

void KValueOperation::f_GatherMPI(int nsize,
	vector<double> &variable, vector<vector<double>> &items)
{
	double *valuesend = new double[nsize];
	for(int n = 0; n < m_gapvar.size(); n++){
		int sendrank = n%m_mpiprocesses;
		if(m_rank == sendrank){
			for (int j = 0; j < nsize; j++){
				valuesend[j] = j == nsize-1 ? variable[n] : items[j][n];
			}
		}
		if(m_thread != nullptr){
			m_thread->Bcast(valuesend, nsize, MPI_DOUBLE, sendrank, m_rank);
		}
		else{
			MPI_Bcast(valuesend, nsize, MPI_DOUBLE, sendrank, MPI_COMM_WORLD);
		}
		if(m_rank != sendrank){
			for (int j = 0; j < nsize-1; j++){
				items[j][n] = valuesend[j];
			}
			variable[n] = valuesend[nsize-1];
		}
	}
	delete[] valuesend;
}

void KValueOperation::f_ExpandHarmonic(
	vector<vector<double>> energynh, vector<vector<vector<double>>> itemsnh,
	vector<double> &energy, vector<vector<double>> &items, vector<string> &details)
{
	vector<int> epoints;
	epoints.resize(m_harmonics.size(), (int)m_gapvar.size());
	ExpandResults(true, epoints, energynh, itemsnh, energy, items);
	details.resize(m_harmonics.size());
	stringstream ss, sshod;
	if(m_isf8){
		sshod << fixed;
		sshod << setprecision(1);
	}
	for(int hidx = 0; hidx < m_harmonics.size(); hidx++){
		if(m_isf8){
			if(hidx%2 > 0){
				sshod << "Harmonic: " << m_harmonics[hidx]*0.5;
				details[hidx] = sshod.str();
				sshod.str("");
				sshod.clear(stringstream::goodbit);
				continue;
			}
			else{
				ss << "Harmonic: " << m_harmonics[hidx]*0.5;
			}
		}
		else{
			ss << "Harmonic: " << m_harmonics[hidx];
		}
		details[hidx] = ss.str();
		ss.str("");
		ss.clear(stringstream::goodbit);
	}
}

void KValueOperation::f_RetriveHarmonic(double energy, int tgtindex, int hidx,
	vector<vector<double>> &energynh, vector<vector<vector<double>>> &itemsnh,
	vector<double> &items)
{
	int hidxmax = -1;
	double vmax = 0, value;
	for(int hidx = 0; hidx < energynh.size(); hidx++){
		vector<double> &earr = energynh[hidx];
		vector<double> &item = itemsnh[hidx][tgtindex];
		if((earr.front()-energy)*(earr.back()-energy) > 0){
			continue;
		}

		int eidx = get_index4lagrange(energy, earr, (int)earr.size());
		value = lagrange(energy, earr[eidx-1], earr[eidx], earr[eidx+1], 
			item[eidx-1], item[eidx], item[eidx+1]);
		if(value > vmax){
			vmax = value;
			hidxmax = hidx;
		}
	}
	if(items.size() < itemsnh[0].size()){
		items.resize(itemsnh[0].size());
	}

	if(hidxmax < 0){
		fill(items.begin(), items.end(), 0);
		return;
	}

	vector<double> &earr = energynh[hidxmax];
	int eidx = get_index4lagrange(energy, earr, (int)earr.size());
	for(int j = 0; j < itemsnh[0].size(); j++){
		if(j == hidx){
			items[j] = itemsnh[hidxmax][j][eidx];
		}
		else{
			vector<double> &item = itemsnh[hidxmax][j];
			items[j] = lagrange(energy, earr[eidx-1], earr[eidx], earr[eidx+1],
				item[eidx-1], item[eidx], item[eidx+1]);
		}
	}
}

void KValueOperation::f_SetVariables()
{
	int nhrange[2], hint;
	bool isallharm = contains(m_calctype, menu::allharm);
	if(m_isf8){
		if(isallharm){
			nhrange[0] = 1;
			nhrange[1] = (int)floor(0.5+2*m_conf[hmax_]);
		}
		else{
			for (int j = 0; j < 2; j++){
				nhrange[j] = (int)floor(0.5+2*m_confv[hrange_][j]);
			}
		}
		hint = 1;
	}
	else{
		if(isallharm){
			nhrange[0] = 1;
			nhrange[1] = (int)floor(0.5+m_conf[hmax_]);
		}
		else{
			for (int j = 0; j < 2; j++){
				nhrange[j] = (int)floor(0.5+m_confv[hrange_][j]);
			}
		}
		hint = 2;
	}
	if(nhrange[0] > nhrange[1]){
		swap(nhrange[0], nhrange[1]);
	}

	int nh = 1;
	while(nh < nhrange[0]){
		nh += hint;
	}

	while(nh <= nhrange[1]){
		m_harmonics.push_back(nh);
		nh += hint;
	}

	m_harmonicmap.resize(m_harmonics.back()+1, -1);
	for(int hidx = 0; hidx < m_harmonics.size(); hidx++){
		m_harmonicmap[m_harmonics[hidx]] = hidx;
	}

	double Krange[2];
	f_GetKrange(Krange);

	if(m_srctype == HELICAL_UND){
		for (int j = 0; j < 2; j++){
			Krange[j] *= SQRT2;
		}
	}

	if(m_istbl){
		double coef[2] = {COEF_K_VALUE*m_lu, COEF_K_VALUE*m_lu};
		if(m_srctype == FIGURE8_UND){
			coef[1] *= 0.5;
		}
		else if(m_srctype == VFIGURE8_UND){
			coef[0] *= 0.5;
		}
		if(m_srctype == ELLIPTIC_UND && m_srcb[apple_]){
			double phase = m_src[phase_]*PI2/m_src[lu_];
			coef[0] *= sin(phase);
			coef[1] *= cos(phase);
		}
		m_gaptbl.GetVariable(0, &m_gap);
		m_gpoints = (int)m_gap.size();
		for(int j = 0; j < 2; j++){
			m_gaptbl.GetArray1D(j+1, &m_KxyTbl[j]);
			m_KxyTbl[j] *= coef[j];
		}
		if(m_srctype == LIN_UND){
			m_KxyTbl[0] *= 0.0;
		}
		else if(m_srctype == VERTICAL_UND){
			m_KxyTbl[1] *= 0.0;
		}
		else if(m_srctype == HELICAL_UND){
			m_KxyTbl[0] = m_KxyTbl[1];
		}
		m_KxyTbl[2].resize(m_gpoints);
		for(int n = 0; n < m_gpoints; n++){
			m_KxyTbl[2][n] = sqrt(hypotsq(m_KxyTbl[0][n], m_KxyTbl[1][n]));
		}
		Krange[0] = max(Krange[0], minmax(m_KxyTbl[2], false));
		Krange[1] = min(Krange[1], minmax(m_KxyTbl[2], true));
	}
	
	int kpoints;
	if(isallharm){
		kpoints = min(100, (int)floor(0.5+m_conf[emesh_]));
		kpoints *= m_accuracy[accinpE_];
	}
	else{
		kpoints = max((int)floor(0.5+m_conf[kmesh_]), 2);
	}
	double dK = (Krange[1]-Krange[0])/(kpoints-1), Kperp;

	m_gapvar.resize(kpoints, 0);
	for(int j = 0; j < 2; j++){
		m_kxyvar[j].resize(kpoints);
	}

	double gapdummy;
	for(int nk = 0; nk < kpoints; nk++){
		Kperp = Krange[0]+nk*dK;
		f_ArrangeGapK(&Kperp, &gapdummy, nk);
	}
}

bool KValueOperation::f_SetKvalues(int n, double *values)
{
	for (int j = 0; j < 2; j++){
		m_srcv[Kxy_][j] = m_kxyvar[j][n];
	}
	if(m_srctype == VERTICAL_UND){
		m_src[K_] = m_kxyvar[0][n];
	}
	else{
		m_src[K_] = m_kxyvar[1][n];
	}
	values[Kx_] = m_kxyvar[0][n];
	values[Ky_] = m_kxyvar[1][n];
	if(m_srctype == VERTICAL_UND){
		values[Kvalue_] = m_kxyvar[0][n];
	}
	else{
		values[Kvalue_] = m_kxyvar[1][n];
	}
	if(m_istbl){
		values[gap_] = m_gapvar[n];
	}
	Initialize();
	ApplyConditions(false);
	return hypotsq(m_kxyvar[0][n], m_kxyvar[1][n]) > 0;
}

void KValueOperation::f_ArrangeGapK(double *pKperp, double *pgap, int nk, bool setgap)
{
	double Kxy[2] = {0, 0};

	if(m_istbl){
		if(setgap){
			if(fabs(*pKperp) == 0){
				*pgap = 0;
			}
			else{
				*pgap = f_GetGapTbl(*pKperp);
				if(*pgap > 0){
					f_GetKxyTbl(*pgap, Kxy);
				}
			}
		}
		else{
			f_GetKxyTbl(*pgap, Kxy);
		}
		m_gapvar[nk] = *pgap;
	}
	else if(m_isauto){
		f_GetGapKxyAuto(pKperp, pgap, Kxy, setgap);
		m_gapvar[nk] = *pgap;
	}
	else{
		if (m_srctype == LIN_UND){
			Kxy[1] = *pKperp;
		}
		else if (m_srctype == HELICAL_UND){
			Kxy[1] = *pKperp;
		}
		else if (m_srctype == VERTICAL_UND){
			Kxy[0] = *pKperp;
		}
		else{
			double kxyf[2], phi;
			if(m_srcb[apple_] && m_srctype == ELLIPTIC_UND){
				phi = PI2*m_src[phase_]/m_src[lu_];
				double csn[2] = {sin(phi), cos(phi)};
				for(int j = 0; j < 2; j++){
					kxyf[j] = m_srcv[Kxy0_][j]*csn[j];
				}
			}
			else{
				for(int j = 0; j < 2; j++){
					kxyf[j] = m_srcv[Kxy_][j];
				}
			}
			if(hypotsq(kxyf[0], kxyf[1]) == 0){
				phi = 0;
			}
			else{
				phi = atan2(kxyf[0], kxyf[1]);
			}
			Kxy[0] = (*pKperp)*sin(phi);
			Kxy[1] = (*pKperp)*cos(phi);
		}
	}
	for(int j = 0; j < 2; j++){
		m_kxyvar[j][nk] = Kxy[j];
	}
	if(setgap == false){
		*pKperp = sqrt(hypotsq(Kxy[0], Kxy[1]));
	}
}

void KValueOperation::f_GetGapKxyAuto(double *pKperp, double *pgap, double Kxy[], bool setgap)
{
	double Kperp = 0, gap;

	if(setgap){
		Kperp = *pKperp;
		if (Kperp <= 0){
			*pgap = 0;
			Kxy[0] = Kxy[1] = 0;
			return;
		}
	}
	else{
		gap = *pgap;
	}

	double lu_mm[] = {m_src[lu_], m_src[lu_]};
	double kcoef[] = {m_lu*COEF_K_VALUE, m_lu*COEF_K_VALUE};
	int if8 = -1;
	if(m_srctype == FIGURE8_UND){
		if8 = 0;
	}
	else if(m_srctype == VFIGURE8_UND){
		if8 = 1;
	}
	if(if8 >= 0){
		kcoef[if8] *= 2.0;
		lu_mm[if8] *= 2.0;
	}

	double Br = m_src[br_], Kpeak[2], csn[2] = {1, 1};
	for(int j = 0; j < 2; j++){
		Kpeak[j] = Br*m_srcv[geofactor_][j]*COEF_BPEAK*kcoef[j];
	}
	if (m_srctype == LIN_UND){
		Kpeak[0] = 0;
	}
	else if(m_srctype == HELICAL_UND){
		Kpeak[0] = Kpeak[1];
	}
	else if(m_srctype == VERTICAL_UND){
		Kpeak[1] = 0;
	}

	bool isapple = m_srcb[apple_] && m_srctype == ELLIPTIC_UND;
	if(isapple){
		double phi = PI2*m_src[phase_]/m_src[lu_];
		csn[0] = sin(phi);
		csn[1] = cos(phi);
	}

	double Kpeak0;
	if(isapple){
		Kpeak0 = sqrt(hypotsq(Kpeak[0]*csn[0], Kpeak[1]*csn[1]));
	}
	else{
		Kpeak0 = sqrt(hypotsq(Kpeak[0], Kpeak[1]));
	}
	if(setgap){
		if (if8 >= 0){
			double K0 = Kpeak[if8];
			double K1 = Kpeak[1-if8];
			double frac = (-K0*K0+sqrt(pow(K0, 4.0)+4*(K1*Kperp)*(K1*Kperp)))/2/K1/K1;
			gap = -log(frac)*lu_mm[1-if8]/PI;
		}
		else{
			gap = -log(Kperp/Kpeak0)*lu_mm[0]/PI;
		}
	}
	for(int j = 0; j < 2; j++){
		Kxy[j] = Kpeak[j]*csn[j]*exp(-PI*gap/lu_mm[j]);
	}

	if(setgap){
		*pgap = gap;
	}
	else{
		*pKperp = Kperp;
	}
}

void KValueOperation::f_GetKxyTbl(double gap, double Kxy[])
{
	int index = get_index4lagrange(gap, m_gap, m_gpoints);
	for(int j = 0; j < 2; j++){
		Kxy[j] = lagrange(gap, 
			m_gap[index-1], m_gap[index], m_gap[index+1], 
			m_KxyTbl[j][index-1], m_KxyTbl[j][index], m_KxyTbl[j][index+1]);
	}
}

double KValueOperation::f_GetGapTbl(double Kperp)
{
	double xarr[3], yarr[3], a = 0, b = 0, c;
	int index = get_index4lagrange(Kperp, m_KxyTbl[2], m_gpoints);

	for(int n = -1; n <= 1; n++){
		xarr[n+1] = m_gap[n+index];
		yarr[n+1] = m_KxyTbl[2][n+index];
    }
    
    int ia[] = {1,2,0}, ib[] = {2,0,1};
	double dx[3];
    for(int i = 0; i < 3; i++){
        dx[i] = xarr[ia[i]]-xarr[ib[i]];
    }
    c = dx[0]*dx[1]*dx[2]*Kperp;
    for(int i = 0; i < 3; i++){
        a += dx[i]*yarr[i];
        b -= (xarr[ia[i]]*xarr[ia[i]]-xarr[ib[i]]*xarr[ib[i]])*yarr[i];
        c += xarr[ia[i]]*xarr[ib[i]]*(xarr[ia[i]]-xarr[ib[i]])*yarr[i];
    }

    double D = b*b-4*a*c;
    if(D < 0 || a == 0){
        return 0;
    }
    double Dsqrt = sqrt(D);

    double x1 = (-b+Dsqrt)/2/a;
    double x2 = (-b-Dsqrt)/2/a;
    if(fabs(x1-xarr[1]) < fabs(x2-xarr[1])){
        return x1;
    }
    return x2;
}

