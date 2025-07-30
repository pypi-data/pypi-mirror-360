#include <algorithm>
#include "spatial_convolution.h"
#include "density_fixed_point.h"
#include "beam_convolution.h"

// files for debugging
string STConvAlongY;
string STConvAlongX;
string STConvResult;
string STConvResultEconv;

SpatialConvolution::SpatialConvolution(
    SpectraSolver &spsolver, DensityFixedPoint *densfix, int layer, int rank, int mpiprocesses)
    : SpectraSolver(spsolver)
{
#ifdef _DEBUG
//STConvAlongY = "..\\debug\\sp_conv_alongy.dat";
STConvAlongX = "..\\debug\\sp_conv_alongx.dat";
//STConvResult = "..\\debug\\sp_conv.dat";
//STConvResultEconv = "..\\debug\\sp_conv_econv.dat";
#endif

    m_xylimit = nullptr;
	m_layer = layer;
    
    m_maxvalues.resize(NumberSpatialIntegOrder);
    for(int j = 0; j < NumberSpatialIntegOrder; j++){
        m_maxvalues[j].resize(2);
    }
    ResetMaxValues();
    if(m_calcstatus != nullptr){
        SetCalcStatusPrint(m_calcstatus);
    }

    m_isskipx = m_isfar && m_isbm;
    m_densfix = densfix;
	m_rank = rank;
	m_mpiprocesses = mpiprocesses;

    double xydiv[2];
	m_densfix->GetTypicalDivergence(xydiv);
    for(int j = 0; j < 2; j++){
        m_typwidth[j] = xydiv[j]*m_conf[slit_dist_];
    }
}

void SpatialConvolution::ResetMaxValues()
{
    for(int j = 0; j < NumberSpatialIntegOrder; j++){
        m_maxvalues[j][0] = m_maxvalues[j][1] = 0.0;
    }
}

void SpatialConvolution::SetRadiationXYLimit(double *xylimit)
{
    m_xylimit = xylimit;
}

void SpatialConvolution::GetConvolutedValue(vector<double> *vconv)
{
    double yrange[2];
	int inilevel, layers[2] = {SpatialIntegOrderAlongY, SpatialIntegOrderAlongY+m_layer};

	if(m_isskipx){
		m_calcstatus->SkipLayer(SpatialIntegOrderAlongX+m_layer);
	}
    if(m_circslit || m_rectslit){
        m_isconvolute = true;
    }
    else{
        m_isconvolute = m_accb[zeroemitt_] == false;
    }

    if(!m_isconvolute){
        QSimpsonIntegrand(SpatialIntegOrderAlongY, m_center[1], vconv);
    }
    else{
        GetSpatialConvolutionRange(1, yrange);
        inilevel = m_accuracy[accinobs_]+min(10, max(4,
            (int)ceil(log10((yrange[1]-yrange[0])/(m_typwidth[1]+INFINITESIMAL))/LOG2)));
        IntegrateSimpson(layers, yrange[0], yrange[1], m_tol_spint,
            inilevel, &m_maxvalues, vconv, STConvAlongY);
    }
}

void SpatialConvolution::AllocateMemorySpatialConvolution(int nitems, int rank, int mpiprocesses)
{
    m_nitems = nitems;
    if(m_circslit){
        m_dtmp.resize(m_nitems);
    }
	if(mpiprocesses > 1){
		ArrangeMPIConfig(rank, mpiprocesses, SpatialIntegOrderAlongY, m_thread);
    }
    try {
        AllocateMemorySimpson(nitems, nitems, NumberSpatialIntegOrder);
    }
    catch (const exception&){
        throw runtime_error("Not enough memory.");
    }
}

void SpatialConvolution::GetSpatialConvolutionRange(int jxy, double *xyrange)
{
    xyrange[0] = xyrange[1] = m_center[jxy];
	if(m_isconvolute){
        if(m_circslit || m_rectslit){
            xyrange[0] -= m_slitapt[jxy]*0.5;
            xyrange[1] += m_slitapt[jxy]*0.5;
        }
        xyrange[0] -= m_Esize[jxy]*m_nlimit[acclimobs_];
        xyrange[1] += m_Esize[jxy]*m_nlimit[acclimobs_];
    }
}

void SpatialConvolution::SingleDensity(double *xy, vector<double> *density)
{
    m_densfix->GetDensity(xy[0], xy[1], density);
}

void SpatialConvolution::GetValue(vector<vector<double>> *value)
{
    vector<double> earray;
    int number, ndata, nepoints;
    Spline spl4pw;
    string errmsg;

    if(m_isenergy || m_isvpdens){
        nepoints = m_densfix->GetEnergyArray(earray);
        ndata = 4*nepoints;
    }
    else{
        nepoints = 1;
        ndata = GetNumberOfItems();
    }

    vector<double> vconf(ndata);
    ResetMaxValues();
    AllocateMemorySpatialConvolution(ndata, m_rank, m_mpiprocesses);
    GetConvolutedValue(&vconf);

	if(m_isenergy || m_isvpdens){
        number = (int)m_eparray.size();
        vector<vector<double>> vtmp(4);
        if(value->size() < 4){
            value->resize(4);
            for (int j = 0; j < 4; j++){
                (*value)[j].resize(number);
            }
        }
        for(int j = 0; j < 4; j++){
            vtmp[j].resize(nepoints);
        }
        for(int n = 0; n < nepoints; n++){
            for(int j = 0; j < 4; j++){
                vtmp[j][n] = vconf[n+j*nepoints];
            }
        }

        double coef = GetFluxCoef();

#ifdef _DEBUG
        if(!STConvResult.empty()){
            ofstream debug_out(STConvResult);
            vector<string> titles{"energy", "flux"};
            vector<double> items(titles.size());
            for(int n = 0; n < number; n++){
                items[0] = m_eparray[n];
                items[1] = (vtmp[0][n]+vtmp[1][n]);
                PrintDebugItems(debug_out, items);
            }
            debug_out.close();
        }
#endif
        EnergySpreadConvolution esampler(this, 4);
        esampler.AllocateInterpolant(nepoints, &earray, &vtmp, false);
        vector<double> fd(4);
        bool isdirect = m_isbm || m_iswiggler 
        || m_iswshifter || m_confb[wiggapprox_];
        for(int n = 0; n < number; n++){
            esampler.RunEnergyConvolution(m_eparray[n], &fd, isdirect);
            for(int j = 0; j < 4; j++){
                (*value)[j][n] = fd[j]*coef;
            }
        }

#ifdef _DEBUG
        if(!STConvResultEconv.empty()){
            ofstream debug_out(STConvResultEconv);
            vector<string> titles {"energy", "flux"};
            vector<double> items(titles.size());
            for(int n = 0; n < number; n++){
                items[0] = m_eparray[n];
                items[1] = (*value)[0][n]+(*value)[1][n];
                PrintDebugItems(debug_out, items);
            }
            debug_out.close();
        }
#endif
    }
    else{
        if(value->size() < vconf.size()){
            value->resize(vconf.size());
            for(int j = 0; j < vconf.size(); j++){
                (*value)[j].resize(1, 0.0);
            }
        }
        double coef = m_ispower ? GetPowerCoef() : GetFluxCoef();
        for(int j = 0; j < vconf.size(); j++){
            (*value)[j][0] = vconf[j]*coef;
        }
    }
}


void SpatialConvolution::QSimpsonIntegrand(int layer, double xy, vector<double> *density)
{
    if(layer == SpatialIntegOrderAlongX){
        f_Integrand4AlongX(xy, density);
    }
    else if(layer == SpatialIntegOrderAlongY){
        f_Integrand4AlongY(xy, density);
    }
}

// private functions
void SpatialConvolution::f_Integrand4AlongY(double y, vector<double> *density)
{
    double xrange[2];
	int inilevel, layers[2] = {SpatialIntegOrderAlongX, SpatialIntegOrderAlongX+m_layer};

    m_y = y;
    if(!m_isconvolute){
        QSimpsonIntegrand(SpatialIntegOrderAlongX, m_center[0], density);
    }
    else{
        if(m_isskipx){
            QSimpsonIntegrand(SpatialIntegOrderAlongX, 0.0, density);
        }
        else{
            GetSpatialConvolutionRange(0, xrange);
            inilevel = m_accuracy[accinobs_]+min(10, max(4,
                (int)ceil(log10((xrange[1]-xrange[0])/(m_typwidth[0]+INFINITESIMAL))/LOG2)));
            IntegrateSimpson(layers, xrange[0], xrange[1], m_tol_spint,
                inilevel, &m_maxvalues, density, STConvAlongX);
        }
    }
}

void SpatialConvolution::f_Integrand4AlongX(double x, vector<double> *density)
{
    double xy[2], ebconv;

    m_x = x;
    xy[0] = m_isskipx ? 0.0 : m_x; xy[1] = m_y;

    SingleDensity(xy, density);

    if(m_isconvolute && m_bmconv->IsInit()){
        ebconv = m_bmconv->GetEBeamCovolutedProfile(xy, m_isskipx);
    }
    else{
        ebconv = 1.0;
    }

    for(int n = 0; n < m_nitems;n++){
        (*density)[n] *= ebconv;
    }
}
