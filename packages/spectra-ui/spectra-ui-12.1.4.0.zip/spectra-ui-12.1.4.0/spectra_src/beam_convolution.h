#ifndef beam_convolution_h
#define beam_convolution_h

#include <vector>

#include "quadrature.h"
#include "function_digitizer.h"
#include "interpolation.h"

class BeamConvolution
    : public QSimpson, public FunctionDigitizer
{
public:
    BeamConvolution();
    void SetCondition(double *esigma, bool zeroemitt, 
        double *center, double *radius, double *apt, int level);
    double GetEBeamCovolutedProfile(double xyvar[], bool isskipx);
    void AllocateConvolutedValue();
    double GetConvolutedValue(bool isskipx, double *xy = nullptr);
    virtual void QSimpsonIntegrand(int layer, double y, vector<double> *circcv);
    virtual double Function4Digitizer(double xy, vector<double> *circcv);
    bool IsInit(){return m_isinit;}
    void Disable(){m_isinit = false;}

private:
    void f_GetYIntegRange(int icirc, double yrange[]);
    double m_rcurr;
    double m_esigma[2];
    double m_bmtail[2];
    double m_xyref[2];

    double m_radius[2];
    double m_center[2];
    double m_aptst[2];
    double m_aptfin[2];

    bool m_iscirc;
    bool m_isrect;

    bool m_zeroemitt;
    int m_ialongxy;
    int m_level;
    int m_xarrsize;
    bool m_isallocated;
    bool m_isallocskipx;
    bool m_skipxproc;
    bool m_isinit;
    vector<double> m_xarr;
    vector<Spline> m_slitcvspline;
    Spline m_slipxspline;
};

#endif
