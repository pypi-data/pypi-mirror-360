#ifndef spatial_convolution_h
#define spatial_convolution_h
#include <vector>
#include "spectra_solver.h"
#include "quadrature.h"
#include "orbit_components_operation.h"

using namespace std;

class DensityFixedPoint;

class SpatialConvolution
    : public SpectraSolver, public QSimpson
{
public:
    SpatialConvolution(SpectraSolver &spsolver, DensityFixedPoint *densfix, 
        int layer, int rank = 0, int mpiprocesses = 1);
    void AllocateMemorySpatialConvolution(int nitems, int rank, int mpiprocesses);
    void SingleDensity(double *xy, vector<double> *density);
    void GetConvolutedValue(vector<double> *vconv);
    void SetRadiationXYLimit(double *xylimit);
    void GetSpatialConvolutionRange(int jxy, double *xrange);
    virtual void QSimpsonIntegrand(int layer, double xy, vector<double> *density);
    void GetValue(vector<vector<double>> *value);
    void ResetMaxValues();

protected:
    DensityFixedPoint *m_densfix;
	double m_typwidth[2];
	int m_layer;
    int m_nitems;
	int m_rank;
	int m_mpiprocesses;

    void f_Integrand4AlongX(double x, vector<double> *density);
    void f_Integrand4AlongY(double y, vector<double> *density);

    double m_x;
    double m_y;
    double *m_xylimit;
    vector<vector<double> > m_maxvalues;
    vector<double> m_dtmp;

    bool m_isskipx;
    bool m_isconvolute;
};

enum {
    SpatialIntegOrderAlongY = 0,
    SpatialIntegOrderAlongX,
    NumberSpatialIntegOrder
};

#define STLAYERS_SP_CONV NumberSpatialIntegOrder

#endif

