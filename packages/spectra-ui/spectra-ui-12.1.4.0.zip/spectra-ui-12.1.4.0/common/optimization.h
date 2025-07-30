#ifndef optimization_h
#define optimization_h

#include <vector>

using namespace std;

class SimulatedAnnealing
{
public:
    SimulatedAnnealing(long *seed = NULL);
    void DoAnnealing(double Tratio, int repeats);
    virtual double CostFunc() = 0;
    virtual void Operation() = 0;
    virtual void Undo() = 0;
    virtual void Initialize() = 0;
	int GetSeed(){return m_seed;}
protected:
    bool f_Judge(double dE, double T);
    int m_seed;
    double m_currfrac;
    double m_costmin;
    int m_repeats;
    bool m_canceled;
};

class DownhillSimplex
{
public:
    DownhillSimplex(int ndim);
    void AssignDimension(int ndim);
    virtual double CostFunc(vector<double> *p) = 0;
    bool Amoeba(bool isshowstatus,
        vector<vector<double>> *p, vector<double> *y,
        int nmax, int contype, double ftol, vector<double> *eps, int *nfunk);
    virtual bool ShowStatusGetCont(int step) = 0;
private:
    double f_Try(vector<vector<double>> *p, vector<double> *y, int ihi, double fac);
    void f_GetPsum(vector<vector<double>> *p);
    int m_ndim;
    int m_nstatusmax;
    vector<double> m_psum;
    vector<double> m_ptry;
};

class SearchMinimum
{
public:
    SearchMinimum();
    void BrentMethod(double ax, double bx, double cx,
        double tol, bool ischeckrel, double tolval, double *xmin, vector<double> *ymin);
    double GetSolutionRtbis(double ytgt, double x1, double x2,
        double *xacc, double *yacc);
    virtual double CostFunc(double x, vector<double> *y) = 0;
};

class MakeTrendMap
{
public:
    MakeTrendMap();
    void SetData(vector<double> *data, int offset, int ndata = 0);
    void GetTrend(int iavg, double eps, int type,
        vector<int> *xpos, vector<double> *ypos);
    void GetTrend(int iavg, vector<int> *ipos, vector<double> *ypos);
    double GetCurrentTrend(int ipos);
    double GetAverage(int iavg, int ipos);
public:
    double f_GetDeviation(int iavg, int type, int *iposmax);
    void f_SetFixedPoint(int iavg, int ipos1, int ipos2);
    vector<double> m_data;
    int m_ndata;
    int m_ifix[3];
    double m_vfix[3];
};

enum {
    AmoebaSerachMinimum = 0,
    AmoebaSerachSolution,

    MakeTrendMapMaxDeviation = 0,
    MakeTrendMapAverage,
};

#endif

