#include <algorithm>
#include "beam_convolution.h"
#include "fast_fourier_transform.h"

// files for debugging
string IntegBMCond;
string FuncBMCond;
string ConvBeamAlloc;

//------------------------------------------------------------------------------
// class BeamConvolution
BeamConvolution::BeamConvolution()
{
	m_isinit = false;
}

void BeamConvolution::SetCondition(double *esigma, bool zeroemitt, 
	double *center, double *radius, double *apt, int level)
{
#ifdef _DEBUG
//IntegBMCond = "..\\debug\\beam_cond_integ.dat";
//FuncBMCond = "..\\debug\\beam_cond_func.dat";
//ConvBeamAlloc = "..\\debug\\beam_conf_alloc.dat";
#endif

	m_isinit = true;
	m_level = level;
	m_zeroemitt = zeroemitt;
	m_iscirc = radius != nullptr;
	if(m_iscirc){
		m_radius[0] = min(radius[0], radius[1]); 
		m_radius[1] = max(radius[0], radius[1]);
	}
	m_isrect = apt != nullptr;
	if(m_isrect){
		for(int j = 0; j < 2; j++){
			m_aptst[j] = center[j]-0.5*fabs(apt[j]);
			m_aptfin[j] = center[j]+0.5*fabs(apt[j]);
		}
	}
	for(int j = 0; j < 2; j++){
		m_center[j] = center[j];
		m_esigma[j] = esigma[j];
		m_bmtail[j] = esigma[j]*(GAUSSIAN_MAX_REGION+m_level);
	}
	AllocateMemorySimpson(1, 1, 1);
	AllocateMemoryFuncDigitizer(1);
	m_isallocated = m_isallocskipx = m_skipxproc = false;
}

double BeamConvolution::GetEBeamCovolutedProfile(double xyvar[], bool isskipx)
	// xyvar: integration variable for the upper level
{
	double xyr[2], ans = 1.0;

	if(m_iscirc){ // circular slit
		xyr[0] = m_center[0]-xyvar[0]; xyr[1] = m_center[1]-xyvar[1]; 
		if(m_zeroemitt){
			double r = sqrt(hypotsq(xyr[0], xyr[1]));
			ans = r >= m_radius[0] && r <= m_radius[1] ? 1.0 : 0.0;
		}
		else{
			ans = GetConvolutedValue(isskipx, xyr);
		}
	}
	else if(m_isrect){ // rectangular slit
		for(int j = 0; j < 2; j++){
			if(j == 0 && isskipx){
				ans *= m_aptfin[0]-m_aptst[0];
			}
			else if(m_esigma[j] > INFINITESIMAL && !m_zeroemitt){
				ans *= (errf((m_aptfin[j]-xyvar[j])/m_esigma[j]/SQRT2)
					-errf((m_aptst[j]-xyvar[j])/m_esigma[j]/SQRT2))*0.5;
			}
			else{
				ans *= (m_aptfin[j]-xyvar[j])*(m_aptst[j]-xyvar[j]) <= 0.0 ? 1.0 : 0.0;
			}
		}
	}
	else{ // density calculation
		double tex;
		for(int j = 1; j >= (isskipx?1:0); j--){
			tex = (m_center[j]-xyvar[j])/m_esigma[j];
			tex *= tex*0.5;
			if (tex > MAXIMUM_EXPONENT){
				return 0.0;
			}
			ans *= exp(-tex)/SQRTPI2/m_esigma[j];
		}
	}
	return ans;
}

void BeamConvolution::AllocateConvolutedValue()
{
	int meshy, meshymax, n;
	vector<double> yarr;
	vector<vector<double>> circcv;
	double xrange[NumberFStepXrange] = 
		{0.0, 0.0, m_radius[1]+m_bmtail[0], 0.0, m_esigma[0]*1.0e-6};
	double eps[2] = {0.1/(double)m_level, 0.0};

	m_ialongxy = 0;
	m_xyref[1] = 0.0;
	m_xarrsize = RunDigitizer(FUNC_DIGIT_BASE, 
		&m_xarr, &circcv, xrange, 10, eps, nullptr, 0, FuncBMCond);

	m_slitcvspline.resize(m_xarrsize);
	m_ialongxy = 1; meshymax = 0;
	xrange[FstepXfin] = m_radius[1]+m_bmtail[1];
	xrange[FstepXlim] = m_esigma[1]*1.0e-6;
	for(n = 0; n < m_xarrsize; n++){
		m_xyref[0] = m_xarr[n];
		meshy = RunDigitizer(FUNC_DIGIT_BASE, 
			&yarr, &circcv, xrange, 10, eps, nullptr, 0, FuncBMCond);
		m_slitcvspline[n].SetSpline(meshy, &yarr, &circcv[0]);
		meshymax = max(meshymax, meshy);
	}
	m_isallocated = true;

	m_skipxproc = true;
	meshy = RunDigitizer(FUNC_DIGIT_BASE, 
		&yarr, &circcv, xrange, 10, eps, nullptr, 0, FuncBMCond);
	m_slipxspline.SetSpline(meshy, &yarr, &circcv[0]);
	m_skipxproc = false;
	m_isallocskipx = true;

#ifdef _DEBUG
	if(!ConvBeamAlloc.empty()){
		ofstream debug_out(ConvBeamAlloc);
		int nx, ny;
		int mesh[2] = {m_xarrsize, meshymax};
		double dxy[2], xyr[2];
		for(int j = 0; j < 2; j++){
			dxy[j] = (m_radius[1]+m_bmtail[j])/(double)(2*mesh[j]-1);
		}
		vector<double> cont(2);
		for(ny = 0; ny < 2*mesh[1]; ny++){
			cont[0] = xyr[1] = (double)ny*dxy[1];
			for(nx = 0; nx < 2*mesh[0]; nx++){
				xyr[0] = (double)nx*dxy[0];
				cont[1] = GetConvolutedValue(false, xyr);
				PrintDebugItems(debug_out, xyr[0], cont);
			}
		}
	}
#endif
}

double BeamConvolution::GetConvolutedValue(bool isskipx, double *xy)
{
	vector<double> value1(1), value2(1, 0.0);
	double eps = 1.0e-3/(double)m_level;
	double cv1, cv2, yrange[2];
	int indexx, layers[2] = {0, -1};

	if(xy != nullptr){
		m_xyref[0] = fabs(xy[0]);
		m_xyref[1] = fabs(xy[1]);
	}
	if(isskipx){
		if(m_isallocskipx){
			return m_slipxspline.GetValue(m_xyref[1]);
		}
		else{
			f_GetYIntegRange(1, yrange);
			m_rcurr = m_radius[1];
			if(m_esigma[1] < INFINITESIMAL){
				QSimpsonIntegrand(0, m_xyref[1], &value1);
			}
			else{
				IntegrateSimpson(layers, yrange[0], yrange[1], eps, 4+m_level, nullptr, &value1, IntegBMCond);
			}
			if(m_radius[0] > INFINITESIMAL){
				f_GetYIntegRange(0, yrange);
				m_rcurr = m_radius[0];
				if(m_esigma[1] < INFINITESIMAL){
					QSimpsonIntegrand(0, m_xyref[1], &value2);
				}
				else{
					IntegrateSimpson(layers, yrange[0], yrange[1], eps, 4+m_level, nullptr, &value2, IntegBMCond);
				}
			}
			return value1[0]-value2[0];
		}
	}
	if(m_isallocated){
		if(fabs(m_xyref[0]) > m_radius[1]+m_bmtail[0] || fabs(m_xyref[1]) > m_radius[1]+m_bmtail[1]){
			return 0.0;
		}
		indexx = SearchIndex(m_xarrsize, false, m_xarr, m_xyref[0]);
		if(indexx >= m_xarrsize-1){
			return 0.0;
		}
		cv1 = m_slitcvspline[indexx].GetValue(m_xyref[1]);
		cv2 = m_slitcvspline[indexx+1].GetValue(m_xyref[1]);
		return max(0.0,
			(cv2-cv1)/(m_xarr[indexx+1]-m_xarr[indexx])*(m_xyref[0]-m_xarr[indexx])+cv1);
	}

	f_GetYIntegRange(1, yrange);
	m_rcurr = m_radius[1];
	if(m_esigma[1] < INFINITESIMAL){
		QSimpsonIntegrand(0, m_xyref[1], &value1);
	}
	else{
		IntegrateSimpson(layers, yrange[0], yrange[1], eps, 4+m_level, nullptr, &value1, IntegBMCond);
	}
	if(m_radius[0] > INFINITESIMAL){
		f_GetYIntegRange(0, yrange);
		m_rcurr = m_radius[0];
		if(m_esigma[1] < INFINITESIMAL){
			QSimpsonIntegrand(0, m_xyref[1], &value2);
		}
		else{
			IntegrateSimpson(layers, yrange[0], yrange[1], eps, 4+m_level, nullptr, &value2, IntegBMCond);
		}
	}
	return value1[0]-value2[0];
}

double BeamConvolution::Function4Digitizer(double xy, vector<double> *circcv)
{
	m_xyref[m_ialongxy] = xy;
	(*circcv)[0] = GetConvolutedValue(m_skipxproc);
	return (*circcv)[0];
}

void BeamConvolution::QSimpsonIntegrand(int layer, double y, vector<double> *circcv)
{
	double xr, tex;

	if(m_esigma[1] < INFINITESIMAL){
		(*circcv)[0] = 1.0;
	}
	else{
		tex = (y-m_xyref[1])/m_esigma[1];
		tex *= 0.5*tex;
		if (tex > MAXIMUM_EXPONENT){
			(*circcv)[0] = 0.0;
			return;
		}
		(*circcv)[0] = exp(-tex)/SQRTPI2/m_esigma[1];
	}

	xr = m_rcurr*m_rcurr-y*y;
	if(xr < INFINITESIMAL){
		(*circcv)[0] = 0.0;
		return;
	}
	if(m_skipxproc){
		(*circcv)[0] *= 2.0*sqrt(xr);
	}
	else{
		if(m_esigma[0] < INFINITESIMAL){
			if(fabs(m_xyref[0]) > xr){
				(*circcv)[0] = 0.0;
				return;
			}
			else{
				(*circcv)[0] *= 1.0;
			}
		}
		else{
			xr = sqrt(xr);
			(*circcv)[0] *= 0.5*(errf((xr-m_xyref[0])/SQRT2/m_esigma[0])-errf((-xr-m_xyref[0])/SQRT2/m_esigma[0]));
		}
	}
 }

// private functions
void BeamConvolution::f_GetYIntegRange(int icirc, double yrange[])
{
	if(m_xyref[1] >= -m_radius[icirc] && m_xyref[1] <= m_radius[icirc]){
		yrange[0] = max(-m_radius[icirc], m_xyref[1]-m_bmtail[1]*2.0);
		yrange[1] = min(m_radius[icirc], m_xyref[1]+m_bmtail[1]*2.0);
	}
	else if(m_xyref[1] < -m_radius[icirc]){
		yrange[0] = -m_radius[icirc];
		yrange[1] = min(m_radius[icirc], -m_radius[icirc]+m_bmtail[1]*2.0);
	}
	else{
		yrange[1] = m_radius[icirc];
		yrange[0] = max(-m_radius[icirc], m_radius[icirc]-m_bmtail[1]*2.0);
	}
}


