#include <algorithm>
#include <iomanip>
#include "wigner_function.h"
#include "bessel.h"
#include "particle_generator.h"
#include "function_statistics.h"
#include "bm_wiggler_radiation.h"
#include "trajectory.h"
#include "flux_density.h"
#include "complex_amplitude.h"

// files for debugging
string WignerIntegCUVU;
string WignerIntegAlong_u;
string WignerIntegAlong_v;
string WignerFuncDigitizer;
string WignerFuncAlongUV;
string WignerFuncEConv;

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

// class WignerFunction
WignerFunction::WignerFunction(ComplexAmplitude *camp, int acclevel, int nwiggler, 
	bool isoddpolewig, PrintCalculationStatus *status, int wlayer)
{
#ifdef _DEBUG
//WignerIntegCUVU  = "..\\debug\\wigner_integ_cuvu.dat";
//WignerIntegAlong_u  = "..\\debug\\wigner_integ_along_u.dat";
//WignerIntegAlong_v  = "..\\debug\\wigner_integ_along_v.dat";
//WignerFuncDigitizer  = "..\\debug\\wigner_func_digit.dat";
//WignerFuncAlongUV  = "..\\debug\\wigner_func_alongUV.dat";
//WignerFuncEConv  = "..\\debug\\wigner_func_econv.dat";
#endif

	m_camp = camp;
	m_polarity = 1.0;
	m_Nwiggler = nwiggler;
	m_ncomps = max(1, nwiggler);
	m_acclevel = acclevel;
	m_isund = m_camp->IsIdealUnd();
	m_idealsrc = m_camp->IsIdealSrc();
	if(!m_idealsrc){
		m_camp->GetEnergyArray(m_eparray);
		m_espredrange = m_camp->GetEspreadRange();
	}
	m_calcstatus = status;
	m_process_layer = wlayer;
	m_oddpolewig = isoddpolewig;
	m_gaussian_limit = GAUSSIAN_MAX_REGION+acclevel-1;
	AllocateMemorySimpson(2*m_ncomps, 2*m_ncomps, 3);
    if(m_calcstatus != nullptr){
        SetCalcStatusPrint(m_calcstatus);
    }
}

void WignerFunction::GetWignerPhaseSpace(int type, bool is4size,
		double UVfix[], double uvfix[], vector<double> vararray[],
		vector<vector<double>> *W, int rank, int mpiprocesses, MPIbyThread *thread)
{
	m_type = type;
	switch(type){
		case WignerFuncType4DX:
		case WignerFuncType2DX:
		case WignerFuncTypeXY:
			m_uvcvidx =  1;
			m_uvscidx = 0;
			break;
		default:
			m_uvcvidx =  0;
			m_uvscidx = 1;
			break;
	}

	m_camp->GetRangePrms(m_halfrange, m_dinterv);
	m_camp->GetEbeam4Wigner(m_sigmauv, m_sigmaUV, m_alpha, is4size);
	m_camp->GetUVSrcPoints(m_srcpoint);
	if(!m_idealsrc){
		m_eptarget = m_camp->GetTargetEnergy();
	}

	int mesh[2];
	for(int j = 0; j < 2; j++){
		mesh[j] = (int)vararray[j].size();
		m_uvfix[j] = uvfix[j];
	}

	if(W->size() < mesh[0]){
		W->resize(mesh[0]);
	}
	for(int i = 0; i < mesh[0]; i++){
		if((*W)[i].size() < mesh[1]){
			(*W)[i].resize(mesh[1]);
		}
	}

	int iscan;
	if(type == WignerFuncTypeXY){
		m_nUVpoints = mesh[1];
		m_UVpoints.resize(m_nUVpoints);
		for(int i = 0; i < mesh[1]; i++){
			m_UVpoints[i] = vararray[1][i];
		}
		iscan = 1;
	}
	else{
		m_nUVpoints = 1;
		m_UVpoints.resize(1, UVfix[m_uvcvidx]);
		iscan = mesh[1];
	}
	AllocateMemoryFuncDigitizer(2*m_ncomps*m_nUVpoints);
	m_wsorg.resize(2*m_ncomps);
	if(!m_idealsrc){
		m_wsni.resize(2*m_ncomps);
	}

	m_calcstatus->SetSubstepNumber(m_process_layer, iscan*(m_Nwiggler>0?2:1));

	vector<vector<double>> Wsglp, Wsglm;

	for(int iuv = 0; iuv < iscan; iuv++){
		double uv = type == WignerFuncTypeXY ? m_uvfix[0] : vararray[1][iuv];
		f_GetWignerAlongUV(uv, &(vararray[0]), &Wsglp, rank, mpiprocesses, thread);
		m_calcstatus->AdvanceStep(m_process_layer);
		
		if(m_Nwiggler > 0){
			m_polarity = -1.0;
			f_GetWignerAlongUV(uv, &(vararray[0]), &Wsglm, rank, mpiprocesses, thread);
			m_calcstatus->AdvanceStep(m_process_layer);
			m_polarity = 1.0;
		}

		if(type == WignerFuncTypeXY){
			for(int iUV = 0; iUV < mesh[0]; iUV++){
				(*W)[iUV] = Wsglp[iUV];
				if(m_Nwiggler > 0){
					(*W)[iUV] += Wsglm[iUV];
				}
			}
			continue;
		}
		for(int iUV = 0; iUV < mesh[0]; iUV++){
			(*W)[iUV][iuv] = Wsglp[iUV][0];
			if(m_Nwiggler > 0){
				(*W)[iUV][iuv] += Wsglm[iUV][0];
			}
			if(type == WignerFuncType2DX || type == WignerFuncType2DY){
				(*W)[iUV][iuv] *=  PI2;
			}
		}
	}
}

double WignerFunction::Function4Digitizer(double uv, vector<double> *W)
{
	double uvrange[2], w, wn;
	int layers[2] = {WignerIntegOrderUVcv, -1};
	vector<double> uvrangew;
	vector<double> Wsgl(3);
    vector<vector<double>> Wsum(WignerIntegOrderUVcv+1);

	double tex = uv*m_sigmaUV[m_uvscidx];
	tex *= tex*0.5;
	if(tex > MAXIMUM_EXPONENT){
		f_PutZeroValues(W, m_nUVpoints);
		return 0.0;
	}
	tex = exp(-tex);

	m_uvcv[m_uvscidx] = uv;
	if(m_type == WignerFuncType2DX || m_type == WignerFuncType2DY){
		QSimpsonIntegrand(WignerIntegOrderUVcv, 0.0, W);
	}
	else{
		f_GetFTRange(m_uvcvidx, uvrange);
		if(m_sigmaUV[m_uvcvidx] > INFINITESIMAL){
			uvrange[0] = max(uvrange[0], -m_gaussian_limit/m_sigmaUV[m_uvcvidx]);
			uvrange[1] = min(uvrange[1], m_gaussian_limit/m_sigmaUV[m_uvcvidx]);
		}

		if(uvrange[1] <= uvrange[0]){
			f_PutZeroValues(W, m_nUVpoints);
			return 0.0;
		}

		int qlevel[2];
		f_GetIntegralLevel(uvrange, m_uvcvidx, qlevel);

		IntegrateSimpson(layers, uvrange[0], uvrange[1], 0.2/(double)m_acclevel, 
			qlevel[0], nullptr, &m_wsorg, WignerIntegCUVU, false, true, qlevel[1]);
		int N = GetEvaluatedValue(WignerIntegOrderUVcv, 
				&m_wsarg[WignerIntegOrderUVcv], &m_wsval[WignerIntegOrderUVcv], WignerIntegCUVU);
		for(int np = 0; np < m_nUVpoints; np++){
			w = m_UVpoints[np]*m_polarity-m_srcpoint[m_uvcvidx];
			if(m_Nwiggler > 0 || fabs(w*(uvrange[1]-uvrange[0])) >= MAX_ARG_SN_APPROX){
				for(int nc = 0; nc < m_ncomps; nc++){
					if(m_Nwiggler > 0){
						wn = w-m_camp->GetOmegaWiggler(nc, m_polarity)*m_uvfix[m_uvcvidx];
					}
					else{
						wn = w;
					}
					f_ReIntegrateEwit(nc, np, -wn, N,  &m_wsarg[WignerIntegOrderUVcv], &m_wsval[WignerIntegOrderUVcv], W);
				}	
			}
			else{
				for(int nc = 0; nc < 2*m_ncomps; nc++){
					(*W)[np*2*m_ncomps+nc] = m_wsorg[nc];
				}
			}
		}
	}

	for(int nc = 0; nc < 2*m_ncomps*m_nUVpoints; nc++){
		(*W)[nc] *= tex;
	}

	double wref = 0;
	for(int nc = 0; nc < m_ncomps*m_nUVpoints; nc++){
		wref += sqrt(hypotsq((*W)[2*nc], (*W)[2*nc+1]));
	}
	return wref;
}

void WignerFunction::QSimpsonIntegrand(int layer, double uv, vector<double> *W)
{
	switch(layer){
		case WignerIntegOrderU:
			if(!m_idealsrc && !m_camp->IsMonteCarlo()){
				f_Integrand_u_econv(uv, W);
			}
			else{
				f_Integrand_u(uv, W);
			}
			break;
		case WignerIntegOrderV:
			f_Integrand_v(uv, W);
			break;
		case WignerIntegOrderUVcv:
			f_Convolute_uv(m_uvcvidx, uv, W);
			break;
	}
}

//---------- private functions
bool WignerFunction::f_IsEvaluateGtEiwt(bool isx, double range[], double w)
{
	if(isx){
		if(m_type == WignerFuncType2DY){
			return false;
		}
	}
	else{
		if(m_type == WignerFuncType2DX){
			return false;
		}
	}
	if(m_Nwiggler == 0){
		return fabs(w*(range[1]-range[0])) >= MAX_ARG_SN_APPROX;
	}
	return true;
}

void WignerFunction::f_ReIntegrateEwit(int nc, int np, double w, int N, 
	vector<double> *arg, vector<vector<double>> *values, vector<double> *W)
{
	if(N < 2){
		return;
	}

	double dtau = ((*arg)[1]-(*arg)[0])/(double)(N-1); // 0 = initial, 1 =  final
	double wdtau = w*dtau;
	double wdtauh = wdtau*0.5;
	double sincw = sincsq(wdtauh);
	double sum[2] = {0.0, 0.0}, cval[2], ctex[2], stex[2], buf[2];

	for(int n = 0; n < N; n++){
		for(int j = 0; j < 2; j++){
			cval[j] = (*values)[n][2*nc+j];
		}
		ctex[0] = cos(w*(*arg)[n]);
		ctex[1] = sin(w*(*arg)[n]);
		complex_product(ctex, cval, buf);
		if(n > 1){
			for(int j = 0; j < 2; j++){
				sum[j] += buf[j]*sincw;
			}
		}
		else{
			if(fabs(wdtau) < MAX_ARG_SN_APPROX){
				stex[0] = 0.5;
				stex[1] = 0.0;
			}
			else if(n == 0){
				stex[0] = 1.0;
				stex[1] = wdtau-sin(wdtau);
			}
			else{
				stex[0] = 1.0;
				stex[1] = -wdtau+sin(wdtau);
			}
			complex_product(buf, stex, cval);
			for(int j = 0; j < 2; j++){
				sum[j] += cval[j];
			}
		}
	}
	for(int j = 0; j < 2; j++){
		sum[j] *= dtau;
		(*W)[2*nc+j+np*2*m_ncomps] = sum[j];
	}
}

void WignerFunction::f_GetWignerAlongUV(
	double uvfix, vector<double> *UVarr, vector<vector<double>> *W,
	int rank, int mpiprocesses, MPIbyThread *thread)
{
	if(W->size() < UVarr->size()){
		W->resize(UVarr->size());
	}
	for(int n = 0; n < UVarr->size(); n++){
		if((*W)[n].size() < m_nUVpoints){
			(*W)[n].resize(m_nUVpoints);
		}
	}

	m_uvfix[m_uvscidx] = uvfix;

	double uvrange[NumberFStepXrange], rtmp[2];
	f_GetFTRange(m_uvscidx, rtmp);

	if(m_sigmaUV[m_uvscidx] > INFINITESIMAL){
		uvrange[FstepXini] = max(rtmp[0], -m_gaussian_limit/m_sigmaUV[m_uvscidx]);
		uvrange[FstepXfin] = min(rtmp[1], m_gaussian_limit/m_sigmaUV[m_uvscidx]);
	}
	else{
		uvrange[FstepXini] = rtmp[0];
		uvrange[FstepXfin] = rtmp[1];
	}

	if(uvrange[FstepXfin]-uvrange[FstepXini] <= INFINITESIMAL){
		for(int n = 0; n < UVarr->size(); n++){
			fill((*W)[n].begin(), (*W)[n].end(), 0.0);
		}
		return;
	}

	uvrange[FstepDx] = 0;
	uvrange[FstepXref] = uvrange[FstepXini];
	uvrange[FstepXlim] = m_dinterv[m_uvscidx]*1.0e-6;

	vector<double> uv;
	vector<vector<double>> Warr;
	double eps[2] = {0.1/(double)m_acclevel, 0.1/(double)m_acclevel};
	int ninit, steps;
	ninit = (int)ceil(m_gaussian_limit*3)*2+1;
	steps = RunDigitizer(FUNC_DIGIT_BASE|FUNC_DIGIT_ENABLE_LOG, &uv, &Warr, 
					uvrange, ninit, eps, m_calcstatus, m_process_layer+1, 
					WignerFuncDigitizer, nullptr, false, rank, mpiprocesses, thread); 

	vector<Spline> wspline(2*m_ncomps*m_nUVpoints);
	for(int np = 0; np < m_nUVpoints; np++){
		for(int nc = 0; nc < 2*m_ncomps; nc++){
			wspline[nc+np*2*m_ncomps].SetSpline(steps, &uv, &Warr[nc+np*2*m_ncomps]);
			wspline[nc+np*2*m_ncomps].AllocateGderiv();
		}
	}

#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(3);
	if(!WignerFuncAlongUV.empty()){
		debug_out.open(WignerFuncAlongUV);
	}
	double gi = 0.0;
#endif

	vector<double> G[2];
	for(int j = 0; j < 2; j++){
		G[j].resize(2*m_ncomps);
	}

	double Gr, Gi, wn, w;
	for(int n = rank; n < UVarr->size(); n += mpiprocesses){
		w = (*UVarr)[n]*m_polarity-m_srcpoint[m_uvscidx];
		for(int np = 0; np < m_nUVpoints; np++){
#ifdef _DEBUG
			if(!WignerFuncAlongUV.empty()){
				gi = 0;
			}
#endif
			for(int nc = 0; nc < m_ncomps; nc++){
				if(m_Nwiggler > 0){
					wn = w-m_camp->GetOmegaWiggler(nc, m_polarity)*m_uvfix[m_uvscidx];
				}
				else{
					wn = w;
				}
				for(int j = 0; j < 2; j++){
					wspline[2*nc+j+np*2*m_ncomps].IntegrateGtEiwt(-wn, &Gr, &Gi);
					G[0][2*nc+j] = Gr;
					G[1][2*nc+j] = Gi;
				}
			}
			int ncps = m_ncomps;
			if(m_oddpolewig && m_polarity > 0){ // odd pole number, skip final period for negative pole
				ncps--;
			}
			(*W)[n][np] = 0;
			if(ncps > 0){
				for(int nc = 0; nc < ncps; nc++){
					(*W)[n][np] += G[0][2*nc]-G[1][2*nc+1];
#ifdef _DEBUG
					if(!WignerFuncAlongUV.empty()){
						gi += G[0][2*nc+1]+G[1][2*nc];
					}
#endif
				}
			}
#ifdef _DEBUG
			if(!WignerFuncAlongUV.empty()){
				items[0] = m_UVpoints[np];
				items[1] = (*W)[n][np];
				items[2] = gi;
				PrintDebugItems(debug_out, (*UVarr)[n], items);
			}
#endif
		}
	}

	if(mpiprocesses > 1){
		for(int n = 0; n < UVarr->size(); n++){
			int target = n%mpiprocesses;
			if(thread != nullptr){
				thread->Bcast((*W)[n].data(), m_nUVpoints, MPI_DOUBLE, target, rank);
			}
			else{
				MPI_Bcast((*W)[n].data(), m_nUVpoints, MPI_DOUBLE, target, MPI_COMM_WORLD);
			}
		}
	}

#ifdef _DEBUG
	if(!WignerFuncAlongUV.empty()){
		debug_out.close();
	}
#endif
}

/*
	m_uvfix	: u  , v
	m_uvvar	: u' , v'
	m_uvcv	: u" , v"
*/

void WignerFunction::f_Integrand_u_econv(double u, vector<double> *W)
{
	if(m_camp->IsEsingle() || m_eparray.size() == 1){
		f_Integrand_u(u, W);
		return;
	}

	double deavg = m_eparray[1]-m_eparray[0];
	for(int nc = 0; nc < m_ncomps; nc++){
		fill(W->begin(), W->end(), 0.0);
	}

	if(m_camp->EnergySpreadSigma() == 0){
		int index = SearchIndex((int)m_eparray.size(), true, m_eparray, m_eptarget);
		double dres[2];
		dres[0] = (m_eparray[index+1]-m_eptarget)/deavg;
		dres[1] =(m_eptarget-m_eparray[index])/deavg;
		for(int j = 0; j < 2; j++){
			m_camp->SetTargetEnergyIndex(index+j);
			f_Integrand_u(u, &m_wsni);
			m_wsni *= dres[j];
			*W += m_wsni;
		}
		return;
	}

	double edivi = 1.0+2.0*m_espredrange;
	double epmin = m_eptarget/edivi;
	double epmax = m_eptarget*edivi;
	double eprof;

#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(3);
	if(!WignerFuncEConv.empty()){
		debug_out.open(WignerFuncEConv);
	}
#endif

	for(int ne = 0; ne < m_eparray.size(); ne++){
		if(m_eparray[ne] < epmin || m_eparray[ne] > epmax){
			continue;
		}
		m_camp->SetTargetEnergyIndex(ne);
		f_Integrand_u(u, &m_wsni);
		eprof = m_camp->EnergyProfile(m_eptarget, m_eparray[ne], deavg)*deavg;
#ifdef _DEBUG
		if(!WignerFuncEConv.empty()){
			items[0] = m_wsni[0];
			items[1] = m_wsni[1];
			items[2] = eprof;
			PrintDebugItems(debug_out, m_eparray[ne], items);
		}
#endif
		m_wsni *= eprof;
		*W += m_wsni;
	}

#ifdef _DEBUG
	if(!WignerFuncEConv.empty()){
		debug_out.close();
	}
#endif
}

void WignerFunction::f_Integrand_u(double u, vector<double> *W)
{
	double tex[2], uvp[2], uvm[2], sn, Wcpx[2];
	double ew[2], ewx[2], ewy[2], emxy[4], epxy[4];

	m_uvvar[0] = u;

	for(int j = 0; j < 2 ; j++){
		uvp[j] = m_uvfix[j]-m_uvvar[j]+m_uvcv[j]*0.5;
		uvm[j] = m_uvfix[j]-m_uvvar[j]-m_uvcv[j]*0.5;
		if(m_sigmauv[j] < INFINITESIMAL){
			tex[j] = 1.0;
		}
		else{
			tex[j] = m_uvvar[j]/m_sigmauv[j];
			tex[j] *= tex[j]*0.5;
			if(tex[j] > MAXIMUM_EXPONENT){
				tex[j] = 0.0;
			}
			else{
				tex[j] = exp(-tex[j])/(SQRTPI2*m_sigmauv[j]);
			}
		}
	}
	if(m_type == WignerFuncType2DX){
		uvp[1] = uvm[1] = m_uvvar[1];
		tex[1] = 1.0;
	}
	else if(m_type == WignerFuncType2DY){
		uvp[0] = uvm[0] = m_uvvar[0];
		tex[0] = 1.0;
	}

	Wcpx[0] = tex[0]*tex[1];
	if(fabs(Wcpx[0]) > INFINITESIMAL){
		if(m_isund){
			double uu[2] = {uvm[0], uvp[0]};
			double vv[2] = {uvm[1], uvp[1]};
#ifdef DEFINE_UR_GAUSSIAN
			sn = exp(-hypotsq(uvm[0], uvm[1]))*exp(-hypotsq(uvp[0], uvp[1]));
#else
			sn = m_camp->GetSn(uu, vv);
#endif
		}
		else{
			sn = 1.0;
		}
		if(m_camp->GetExyAmplitude(uvp, epxy) 
			&& m_camp->GetExyAmplitude(uvm, emxy))
		{
			epxy[1] *= -1; epxy[3] *= -1; // complex conjugate
			complex_product(epxy, emxy, ewx);
			complex_product(epxy+2, emxy+2, ewy);
			for (int j = 0; j < 2; j++){
				ew[j] = (ewx[j]+ewy[j])*sn;
			}
			Wcpx[1] = Wcpx[0]*ew[1];
			Wcpx[0] *= ew[0];
		}
		else{
			Wcpx[0] = Wcpx[1] = 0;
		}
	}
	else{
		Wcpx[0] = Wcpx[1] = 0;
	}

	for(int nc = 0; nc < m_ncomps; nc++){
		for(int j = 0; j < 2; j++){
			(*W)[2*nc+j] = Wcpx[j];
		}
	}
}

void WignerFunction::f_Integrand_v(double v, vector<double> *W)
{
	double urange[2];
	int layers[2] = {WignerIntegOrderU, -1};
	m_uvvar[1] = v;

	if(m_type == WignerFuncType2DY){
		urange[0] = -m_halfrange[0];
		urange[1] = m_halfrange[0];
	}
	else if(m_sigmauv[0] < INFINITESIMAL){
		QSimpsonIntegrand(WignerIntegOrderU, 0.0, W);
		return;
	}
	else{
		f_GetIntegRangeCV(0, urange);
		urange[0] = max(urange[0], -m_gaussian_limit*m_sigmauv[0]);
		urange[1] = min(urange[1], m_gaussian_limit*m_sigmauv[0]);
		if(urange[1]-urange[0] < INFINITESIMAL){
			f_PutZeroValues(W);
			return;
		}
	}

	int qlevel[2];
	f_GetIntegralLevel(urange, 0, qlevel);
	
	IntegrateSimpson(layers, urange[0], urange[1], 0.1/(double)m_acclevel, 
		qlevel[0], nullptr, W, WignerIntegAlong_u, false, true, qlevel[1]);

	double w = m_alpha[0]*m_uvcv[0], wn;
	if(f_IsEvaluateGtEiwt(true, urange, w)){
		int N = GetEvaluatedValue(WignerIntegOrderU, 
			&m_wsarg[WignerIntegOrderU], &m_wsval[WignerIntegOrderU], WignerIntegAlong_u);
		for(int nc = 0; nc < m_ncomps; nc++){
			if(m_Nwiggler > 0){
				wn = w+m_camp->GetOmegaWiggler(nc, m_polarity)*m_uvcv[0];
			}
			else{
				wn = w;
			}
			f_ReIntegrateEwit(nc, 0, -wn, N, &m_wsarg[WignerIntegOrderU], &m_wsval[WignerIntegOrderU], W);
		}
	}

	for(int nc = 0; nc < 2*m_ncomps; nc++){
		if(fabs((*W)[nc]) > m_currmaxref[WignerIntegOrderV]){
			m_currmaxref[WignerIntegOrderV] = fabs((*W)[nc]);
		}
	}
}

void WignerFunction::f_Convolute_uv(int uvidx, double uv, vector<double> *W)
{
	double vrange[2], tex;
	int layers[2] = {WignerIntegOrderV, -1};
	m_uvcv[uvidx] = uv;

	if(m_type == WignerFuncType4DX || m_type == WignerFuncType4DY || m_type == WignerFuncTypeXY){
		tex = uv*m_sigmaUV[uvidx];
		tex *= tex*0.5;
		if(tex > MAXIMUM_EXPONENT){
			f_PutZeroValues(W);
			return;
		}
		tex = exp(-tex);
	}
	else{
		tex = 1.0;
	}

	if(m_type != WignerFuncType2DX && m_sigmauv[1] < INFINITESIMAL){
		QSimpsonIntegrand(WignerIntegOrderV, 0.0, W);
	}
	else{
		if(m_type == WignerFuncType2DX){
			vrange[0] = -m_halfrange[1];
			vrange[1] = m_halfrange[1];
		}
		else{
			f_GetIntegRangeCV(1, vrange);
			vrange[0] = max(vrange[0], -m_gaussian_limit*m_sigmauv[1]);
			vrange[1] = min(vrange[1], m_gaussian_limit*m_sigmauv[1]);
			if(vrange[1]-vrange[0] < INFINITESIMAL){
				f_PutZeroValues(W);
				return;
			}
		}

		int qlevel[2];
		f_GetIntegralLevel(vrange, 1, qlevel);
		layers[1] = m_process_layer+2;

		IntegrateSimpson(layers, vrange[0], vrange[1], 0.2/(double)m_acclevel, 
			qlevel[0], nullptr, W, WignerIntegAlong_v, false, true, qlevel[1]);

		double w = m_alpha[1]*m_uvcv[1], wn;
		if(f_IsEvaluateGtEiwt(false, vrange, w)){
			int N = GetEvaluatedValue(WignerIntegOrderV, 
				&m_wsarg[WignerIntegOrderV], &m_wsval[WignerIntegOrderV], WignerIntegAlong_v);
			for(int nc = 0; nc < m_ncomps; nc++){
				if(m_Nwiggler > 0){
					wn = w+m_camp->GetOmegaWiggler(nc, m_polarity)*m_uvcv[1];
				}
				else{
					wn = w;
				}
				f_ReIntegrateEwit(nc, 0, -wn, N, &m_wsarg[WignerIntegOrderV], &m_wsval[WignerIntegOrderV], W);
			}
		}
	}

	for(int nc = 0; nc < m_ncomps; nc++){
		(*W)[2*nc] *= tex;
		(*W)[2*nc+1] *= tex;
	}
}

void WignerFunction::f_GetIntegRangeCV(int uvidx, double uvrange[])
{
	double range = m_halfrange[uvidx];

	if(m_uvcv[uvidx] < 0){
		uvrange[0] = m_uvfix[uvidx]-m_uvcv[uvidx]*0.5-range;
		uvrange[1] = m_uvfix[uvidx]+m_uvcv[uvidx]*0.5+range;
	}
	else{
		uvrange[0] = m_uvfix[uvidx]+m_uvcv[uvidx]*0.5-range;
		uvrange[1] = m_uvfix[uvidx]-m_uvcv[uvidx]*0.5+range;
	}
}

void WignerFunction::f_GetFTRange(int uvidx, double uvrange[])
{
	double valrange = m_halfrange[uvidx]*2.0;
	uvrange[0] = 2.0*fabs(m_uvfix[uvidx])-valrange-m_gaussian_limit*m_sigmauv[uvidx];
	uvrange[1] = -2.0*fabs(m_uvfix[uvidx])+valrange+m_gaussian_limit*m_sigmauv[uvidx];
}

void WignerFunction::f_PutZeroValues(vector<double> *W, int np)
{
	for(int nc = 0; nc < m_ncomps*np; nc++){
		(*W)[2*nc] = (*W)[2*nc+1] = 0.0;
	}
}

void WignerFunction::f_GetIntegralLevel(double uvrange[], int uvidx, int level[])
{
	double meshnum = fabs(uvrange[1]-uvrange[0])/m_dinterv[uvidx]/2.0;
	int basel = (int)ceil(log10(meshnum+INFINITESIMAL)/LOG2);
	level[0] = m_acclevel+max(4, basel);	
	level[1] = min(15, level[0]+m_acclevel+3);
}

//--------------------
// class WignerFunctionCtrl
WignerFunctionCtrl::WignerFunctionCtrl(SpectraSolver &spsolver, 
	int layer, ComplexAmplitude *camp)
	: SpectraSolver(spsolver)
{
	m_wiglayer = layer;
	if(contains(m_calctype, menu::XXpYYp) 
		|| contains(m_calctype, menu::Wrel)){
		m_wiglayer++;
	}
	m_single = contains(m_calctype, menu::energy) 
		|| contains(m_calctype, menu::Kvalue);

	int Nw = m_iswiggler ? m_N : 0;
	if(camp != nullptr){
		m_camp = camp;
		m_isctrled = true;
	}
	else{
		m_camp = new ComplexAmplitude(spsolver);
		m_isctrled = false;
	}
	m_wigner = new WignerFunction(m_camp, 
		m_accuracy[accinobs_], Nw, m_isoddpole, m_calcstatus, m_wiglayer);
	m_dXYdUV = m_camp->GetConvUV();
	m_dqduv = m_camp->GetConv_uv();
}

WignerFunctionCtrl::~WignerFunctionCtrl()
{
	if (!m_isctrled){
		delete m_camp;
	}
	delete m_wigner;
}

void WignerFunctionCtrl::GetPhaseSpaceProfile(
	vector<vector<double>> &xyvar, vector<double> &W, int rank, int mpiprocesses)
{
	vector<vector<int>> indices;
	vector<int> wigtypes;
	int wigtype;

	if(m_single){
		wigtype = WignerFuncTypeXY;
		xyvar.resize(NumberSrcVar);
		xyvar[SrcVarX] = vector<double> {m_conf[Xfix_]*0.001}; // mm -> m
		xyvar[SrcVarY] = vector<double> {m_conf[Yfix_]*0.001};
		xyvar[SrcVarXp] = vector<double> {m_conf[Xpfix_]*0.001};
		xyvar[SrcVarYp] = vector<double> {m_conf[Ypfix_]*0.001};
		indices.push_back(vector<int> {SrcVarX, SrcVarY});
	}
	else{
		GetVariables(wigtypes, xyvar, indices);
		wigtype = wigtypes[0];
		if(indices.size() == 0){
			if(wigtype == WignerFuncType4DX ||
				wigtype == WignerFuncType2DX){
				indices.push_back(vector<int> {SrcVarX, SrcVarXp});
			}
			else if(wigtype == WignerFuncType2DY){
				indices.push_back(vector<int> {SrcVarY, SrcVarYp});
			}
		}
	}
	int ndata = (int)xyvar[0].size();
	for(int j = SrcVarY; j < NumberSrcVar; j++){
		ndata *= (int)xyvar[j].size();
	}
	W.resize(ndata);

	double UVfix[2], uvfix[2];
	vector<double> vararray[2], uvvalues[2];
	double conv[NumberSrcVar] = {m_dXYdUV, m_dXYdUV, m_dqduv, m_dqduv};

	for(int j = 0; j < 2; j++){
		UVfix[j] = xyvar[j][0]/m_dXYdUV;
		uvfix[j] = xyvar[j+2][0]/m_dqduv;
		vararray[j] = xyvar[indices[0][j]];
		vararray[j] /= conv[indices[0][j]];
	}

	vector<vector<double>> ws;

	if(indices.size() > 1){
		for (int j = 0; j < 2; j++){
			uvvalues[j] = xyvar[indices[1][j]];
			uvvalues[j] /= conv[indices[1][j]];
		}
		int steps = (int)(uvvalues[1].size()*uvvalues[0].size());
		m_calcstatus->SetSubstepNumber(m_wiglayer-1, (steps-1)/mpiprocesses+1);
		int nrep;
		vector<double> WW;
		if(mpiprocesses > 1){
			WW.resize(ndata, 0.0);
		}
		for(int m = 0; m < uvvalues[1].size(); m++){
			uvfix[1] = uvvalues[1][m];
			for (int n = 0; n < (int)uvvalues[0].size(); n++){
				nrep = m*(int)uvvalues[0].size()+n;
				if(rank != nrep%mpiprocesses){
					continue;
				}
				int offset = m*(int)uvvalues[0].size()+n;
				offset *= (int)(vararray[0].size()*vararray[1].size());
				uvfix[0] = uvvalues[0][n];
				m_wigner->GetWignerPhaseSpace(
					wigtype, false, UVfix, uvfix, vararray, &ws);
				if(mpiprocesses > 1){
					f_CopyWdata(vararray, ws, WW, offset);
				}
				else{
					f_CopyWdata(vararray, ws, W, offset);
				}
				m_calcstatus->AdvanceStep(m_wiglayer-1);
			}
		}
		if(mpiprocesses > 1){
			if(m_thread != nullptr){
				m_thread->Allreduce(WW.data(), W.data(), ndata, MPI_DOUBLE, MPI_SUM, rank);
			}
			else{
				MPI_Allreduce(WW.data(), W.data(), ndata, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
			}
		}
	}
	else{
		m_wigner->GetWignerPhaseSpace(
			wigtype, false, UVfix, uvfix, vararray, &ws, rank, mpiprocesses, m_thread);
		f_CopyWdata(vararray, ws, W);
	}

	double wcoef = m_camp->GetWDFCoef()*m_dqduv*m_dqduv;
	if(wigtype == WignerFuncType2DX || wigtype == WignerFuncType2DY){
		wcoef *= (m_dqduv*1.0e+3)*(m_dXYdUV*1.0e+3);
			// m -> mm, rad -> mrad
	}
	W *= wcoef;
}

void WignerFunctionCtrl::GetVariables(vector<int> &wigtypes,
	vector<vector<double>> &xyvar, vector<vector<int>> &indices)
{
	double varini[NumberSrcVar], dvar[NumberSrcVar], dvarspl[2];
	int mesh[NumberSrcVar] = {0,0,0,0};
	GetWignerType(wigtypes, indices);
	
	for(int k = 0; k < indices.size(); k++){
		for(int j = 0; j < indices[k].size(); j++){
			int varidx = indices[k][j];
			GetGridContents(j, true, 
				&varini[varidx], &dvar[varidx], &dvarspl[j], &mesh[varidx], wigtypes[k]);
		}
	}

	int prmidx[NumberSrcVar] = {Xfix_, Yfix_, Xpfix_, Ypfix_}; 
	xyvar.resize(NumberSrcVar);
	for(int j = SrcVarX; j < NumberSrcVar; j++){
		xyvar[j].resize(max(1, mesh[j]));
		if(mesh[j] == 0){
			xyvar[j][0] = m_conf[prmidx[j]]*0.001;
		}
		else{
			for(int n = 0; n < mesh[j]; n++){
				xyvar[j][n] = varini[j]+dvar[j]*n;
				if (fabs(xyvar[j][n]) < fabs(dvar[j])*DXY_LOWER_LIMIT){
					xyvar[j][n] = 0.0;
				}
			}
		}
	}
}

void WignerFunctionCtrl::SetPhotonEnergy(double ep)
{
	m_camp->Prepare(ep);
	m_dXYdUV = m_camp->GetConvUV();
	m_dqduv = m_camp->GetConv_uv();
}

// private functions
void WignerFunctionCtrl::f_CopyWdata(
	vector<double> vararray[], vector<vector<double>> &ws, vector<double> &W, int offset)
{
	for(int h = 0; h < vararray[1].size(); h++){
		for (int i = 0; i < vararray[0].size(); i++){
			W[vararray[0].size()*h+i+offset] = ws[i][h];
		}
	}
}

