#ifndef print_calculation_status_h
#define print_calculation_status_h

#include <string>
#include <vector>

#define INITLABEL "Initializing: "
#define INITIAL_EPS 1.0

using namespace std;

class ShowCalcStatusBase
{
public:
	virtual void PrintStep(int stepwhole) = 0;
};

class PrintCalculationStatus
{
public:
	PrintCalculationStatus(bool lfeedonly, int rank = 0, int serno = -1);
	bool CheckLayer(int layer);
	void InitializeStatus(int layers);
	void ResetTotal(){m_progold = 0;}
	void ResetCurrentStep(int layer);
	void SetCurrentOrigin(int layer);
	void SkipLayer(int layer);
	void SetTargetAccuracy(int layer, double eps);
	void SetCurrentAccuracy(int layer, double eps);
	void SetSubstepNumber(int layer, int steps);
	void SetTargetPoint(int layer, double ratio);
	void SetSubstepWidth(int layer, double frac = -1);
	void FinishLayer(int layer);
	void PutSteps(int layer, int step);
	void AdvanceStep(int layer, int steps = 1);
	double GetTotalRatio();
	void PrintInitStatus(double pct);
	void SetWPLevel(int layer, int level){m_wplevel[layer] = level;}
	int GetSubStepsNumber(int layer){return m_substeps[layer]; }
	int GetSubStep(int layer){return m_currstep[layer]; }

private:
	bool m_lfeedonly;
	vector<double> m_currentorg;
	vector<double> m_currentval;
	vector<double> m_currenteps;
	vector<double> m_targeteps;
	vector<double> m_subwidth;
	vector<double> m_tgtpointr;
	vector<int> m_substeps;
	vector<int> m_currstep;
	vector<int> m_wplevel;
	int m_layers;
	double m_progold;
	int m_rank;
	int m_serno;

protected:
	void f_PrintStep();
};

#endif
