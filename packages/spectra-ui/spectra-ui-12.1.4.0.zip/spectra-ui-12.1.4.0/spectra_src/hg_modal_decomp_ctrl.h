#ifndef hg_modal_decomp_ctrl_h
#define hg_modal_decomp_ctrl_h

#include <vector>
#include "wigner4d_manipulator.h"
#include "spectra_solver.h"

using namespace std;

class HGModalDecompCtrl :
	public SpectraSolver
{
public:
	HGModalDecompCtrl(SpectraSolver &spsolver);
	void Solve(
		vector<string> &subresults, vector<string> &categories,
		vector<vector<double>> *vararray = nullptr, vector<double> *data = nullptr);
	void Solve4D(vector<string> &subresults, vector<string> &categories);
	void Solve2D(vector<string> &subresults, vector<string> &categories);
	bool RetrieveResult2D(double *err, int *maxorder,  double *srcsize, 
		double *fnorm, vector<double> &anmre, vector<double> &anmim);
	bool RetrieveResult4D(double *err, int maxorder[], double srcsize[], 
		double *fnorm, vector<int> &order, vector<double> &anmre, vector<double> &anmim);
	bool Retrieve_anm(int nmodes, vector<double> &anmre, vector<double> &anmim);

private:
	Wigner4DManipulator m_wig4d;
	int m_type;
};

#endif
