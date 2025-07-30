#ifndef data_container_h
#define data_container_h

#include <string>
#include "picojson.h"
#include "interpolation.h"

using namespace std;

class DataContainer
{
public:
	DataContainer();
	void Set1D(vector<string> &titles, vector<vector<double>> &values);
	void Set2D(vector<string> &titles, vector<vector<double>> &variables, vector<vector<vector<double>>> values);
	bool Set(picojson::object &obj, int dimension, vector<string> &titles);
	void ConvertUnit(int j, double coef, bool isvar);
	void ConvertArray1D(picojson::array &arr, size_t nsize, vector<double> *data);
	void ConvertArray2D(picojson::array &arr, size_t nsize[], vector<vector<double>> *data);
	void ApplyDispersion(double alpha);
	void GetArray1D(int j, vector<double> *arr);
	void GetVariable(int j, vector<double> *arr);
	double GetElement2D(int j, int index[]);
	bool MakeStatistics(int index);
	void GetStatistics(double stdsize[], double *stdarea, double *alpha, int index);
	void GetSliceStatistics(int jvar, int index, vector<double> &area, vector<double> &size);
	void GetFT(int item, vector<double> &varinv,
		vector<vector<double>> &FT, double dtmin, double *typlen, 
		int rowindex = -1);
	double GetVolume(int item);
	void GetProjection(int j, int item, vector<double> *arr);
	int GetDimension(){return m_dimension;}
	int GetItemNumber(){return m_datasets;}
	int GetSize();
	double GetLocalVolume1D(int index, double delta, double var, bool isnormalize);
	double GetLocalVolume2D(int index, double delta[], double xy[], bool isnormalize);
	double GetFracThreshold(int index, double thresh);

private:
	void f_AllocSpline(int index, int m);

	int m_dimension;
	int m_datasets;
	vector<vector<double>> m_var;
	vector<vector<double>> m_items1d;
	vector<vector<vector<double>>> m_items2d;
	int m_statidx;
	double m_volume;
	double m_stdsize[2];
	double m_stdemitt;
	double m_alpha;
	vector<vector<Spline>> m_spl;
	vector<double> m_ws;
	Spline m_mpl;
	vector<string> m_titles;
};

#endif
