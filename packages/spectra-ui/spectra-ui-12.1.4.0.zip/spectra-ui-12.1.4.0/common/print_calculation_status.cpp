#include <math.h>
#include <algorithm>
#include <iostream>
#include <sstream>
#include <iomanip>
#include "print_calculation_status.h"
#include "spectra_input.h"

#ifdef _EMSCRIPTEN
#include <emscripten/bind.h>
#include <emscripten.h>
EM_JS(void, set_satatus, (const char *poutput), {
	let data = UTF8ToString(poutput);
	SetOutput("", data);
});
#endif

PrintCalculationStatus::PrintCalculationStatus(bool lfeedonly, int rank, int serno)
{
	m_lfeedonly = lfeedonly;
	m_rank = rank;
	m_serno = serno;
}

void PrintCalculationStatus::InitializeStatus(int layers)
{
	m_layers = layers;
	m_currentorg.resize(m_layers, 0.0);
	m_currentval.resize(m_layers, 0.0);
	m_currenteps.resize(m_layers, 1.0);
	m_targeteps.resize(m_layers, 1.0);
	m_subwidth.resize(m_layers);
	m_substeps.resize(m_layers);
	m_currstep.resize(m_layers);
	m_tgtpointr.resize(m_layers, 1.0);
	m_wplevel.resize(m_layers, 2);
	m_progold = 0.0;
}

bool PrintCalculationStatus::CheckLayer(int layer)
{
	if(layer >= m_layers){
		throw runtime_error("Invalid layer number for calculation process monitor.");
		return false;
	}
	return true;
}

void PrintCalculationStatus::ResetCurrentStep(int layer)
{
#ifdef _DEBUG
	if(!CheckLayer(layer)) return;
#endif
	m_currstep[layer] = 0;
	m_currentval[layer] = m_currentorg[layer];
}

void PrintCalculationStatus::SetCurrentOrigin(int layer)
{
#ifdef _DEBUG
	if(!CheckLayer(layer)) return;
#endif
	m_currentorg[layer] = m_currentval[layer]*m_tgtpointr[layer];
}

void PrintCalculationStatus::SkipLayer(int layer)
{
#ifdef _DEBUG
	if(!CheckLayer(layer)) return;
#endif
	m_subwidth[layer] = 1.0;
	m_currentval[layer] = 0.0;
}

void PrintCalculationStatus::SetTargetAccuracy(int layer, double eps)
{
#ifdef _DEBUG
	if(!CheckLayer(layer)) return;
#endif
	m_targeteps[layer] = eps;
	SetSubstepWidth(layer);
}

void PrintCalculationStatus::SetCurrentAccuracy(int layer, double eps)
{
#ifdef _DEBUG
	if(!CheckLayer(layer)) return;
#endif
	m_currenteps[layer] = eps;
	SetSubstepWidth(layer);
}

void PrintCalculationStatus::SetSubstepNumber(int layer, int steps)
{
#ifdef _DEBUG
	if(!CheckLayer(layer)) return;
#endif
	m_substeps[layer] = steps;
	SetSubstepWidth(layer);
}

void PrintCalculationStatus::SetTargetPoint(int layer, double ratio)
{
#ifdef _DEBUG
	if(!CheckLayer(layer)) return;
#endif
	m_tgtpointr[layer] = ratio;
}

void PrintCalculationStatus::SetSubstepWidth(int layer, double frac)
{
#ifdef _DEBUG
	if(!CheckLayer(layer)) return;
#endif
	double eps;
	if(frac > 0){
		eps = frac;
	}
	else{
		eps = min(1.0, (1.0-log10(m_currenteps[layer]))/(1.0-log10(m_targeteps[layer])));
	}
	m_subwidth[layer] = 1.0-m_currentorg[layer];

	for(int n = 1; n <= m_wplevel[layer]; n++){
		m_subwidth[layer] *= eps;
	}

	if(m_substeps[layer] > 0){
		m_subwidth[layer] /= (double)m_substeps[layer];
	}
}

void PrintCalculationStatus::FinishLayer(int layer)
{
	m_subwidth[layer] = 0.0;
	m_tgtpointr[layer] = m_currentval[layer] = 1.0;
}

void PrintCalculationStatus::PutSteps(int layer, int step)
{
#ifdef _DEBUG
	if(!CheckLayer(layer)) return;
#endif
	for(int j = layer+1; j < m_layers; j++){
		m_currstep[j] = 0;
		m_currentorg[j] = 0;
		m_currentval[j] = 0;
		m_currenteps[j] = INITIAL_EPS;
	}
	m_currstep[layer] = step;
	m_currentval[layer] = m_currentorg[layer]+m_subwidth[layer]*(double)step;
	double prog = GetTotalRatio();
	if(prog-m_progold >= 9.9e-4){
		m_progold = prog;
		f_PrintStep();
	}
}

void PrintCalculationStatus::AdvanceStep(int layer, int steps)
{
#ifdef _DEBUG
	if(!CheckLayer(layer)) return;
#endif
	if(layer < m_layers-1){
		ResetCurrentStep(layer+1);
	}
	PutSteps(layer, m_currstep[layer]+steps);
}

double PrintCalculationStatus::GetTotalRatio()
{
	double ratio = 0.0;
	for(int nl = m_layers-1; nl >= 0; nl--){
		ratio = (m_subwidth[nl]*ratio+m_currentval[nl])*m_tgtpointr[nl];
	}
	return ratio;
}

void PrintCalculationStatus::PrintInitStatus(double pct)
{
	if(m_rank > 0) return;

	string delim;
	if(m_lfeedonly){
		delim = "\r";
	}
	else{
		delim = "\n";
	}
	if(m_rank == 0){
#ifdef _EMSCRIPTEN
		// do nothing
#else
		cout << INITLABEL << fixed << setprecision(1) << pct << "%      " << delim;
		flush(cout);
#endif
	}
}

// private functions 
void PrintCalculationStatus::f_PrintStep()
{
	if(m_rank > 0) return;

	string delim;
	if(m_lfeedonly){
		delim = "\r";
	}
	else{
		delim = "\n";
	}
	if(m_rank == 0){
#ifdef _EMSCRIPTEN
		stringstream ss;
		ss << CalcStatusLabel << fixed << setprecision(2) << m_progold*100.0 << "%";
		set_satatus(ss.str().c_str());
#else
		fflush(stdout);
		cout << CalcStatusLabel << fixed << setprecision(2) << m_progold*100.0 << "%      " << delim;
		flush(cout);
#endif
	}
}
