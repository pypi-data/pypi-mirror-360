#ifndef undulator_data_manipulation_h
#define undulator_data_manipulation_h

#include "quadrature.h"
#include "id_field_profile.h"

#define ENDPERIODS 1

class RandomUtility;

class UndulatorFieldData
    : public IDFieldProfile
{
public:
	UndulatorFieldData();
	bool AllocateUData(
		RandomUtility *rand, int N, double lu, double K2, vector<double> Kxy[],vector<double> deltaxy[],
		double *sigma, double *sigalloc, bool isfsym, bool isendcorr);
	bool AllocateIntegral(RandomUtility *rand, bool isnormalize, double *sigma, double *sigalloc);
	void GetErrorArray(
		vector<vector<double>> *I1err, vector<vector<double>> *bkick);
	void GetEnt4Err(double zent[]);
	static int GetPoleNumber(double z, double z0th, double lu);

private:
	void f_AllocateFieldError(vector<vector<double>> &i1err, 
		vector<vector<double>> &berr, vector<vector<double>> &acc);
	void f_SetCommonPrm(double lu, vector<double> Kxy[], vector<double> deltaxy[]);
	void f_ApplyErrors();
	void f_AdjustPhase();

	vector<double> m_Kxy[2];
	vector<double> m_deltaxy[2];
	double m_B;  
	double m_z0thpole[3];
	double m_K2;

	int m_N;
	int m_endpoles[2];
	double m_lu;
	double m_dz;
	bool m_isnormalize;
	bool m_isfsymm;
	bool m_isendcorr;

	double m_frac[NumberUError];

	vector<vector<double>> m_items;
	vector<vector<double>> m_i1drv;
	vector<vector<double>> m_bdrv;
	vector<vector<double>> m_bkick;
	vector<vector<double>> m_i1err;
	vector<vector<double>> m_wsacc;
	vector<double> m_bcorr[2];
	vector<double> m_eta;

	string m_errmsg;
};

enum {
//	Undulator Type
	UTypeLinear = 0,
	UTypeHelical,
	UTypeElliptic,
	UTypeMultiHarmonic,
	UTypeVert,
	NumberUType
};


#endif

