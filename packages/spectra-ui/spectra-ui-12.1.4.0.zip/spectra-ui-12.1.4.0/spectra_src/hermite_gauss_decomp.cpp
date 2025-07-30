#include <cmath>
#include <boost/math/special_functions/laguerre.hpp>
#include <boost/math/special_functions/hermite.hpp>
#include <Eigen/Dense>
#include <Eigen/Eigenvalues> 

#include "spectra_input.h"
#include "numerical_common_definitions.h"
#include "optimization.h"
#include "interpolation.h"
#include "quadrature.h"
#include "hermite_gauss_decomp.h"
#include "output_utility.h"
#include "json_writer.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

#define _HGTIME

using namespace boost::math;
using namespace std;
using namespace Eigen;

//---------------------------
// files for debugging
string IntegCMDAlongCF;
string IntegCMDAlongR;
string CMDAmn1D;
string CMDCholeskyBef;
string CMDCholeskyAft;
string CMDFourierTheta;
string CMDFourierPhiBef;
string CMDFourierPhiAft;
string CMD_Anm_Func_1st;
string CMD_Anm_Func_2nd;
string CMD_Chk_1d;
string CMD_Chk_FFT;
string CMD_Chk_2d;
string CMD_Chk_2d_FFT;
string CMD_Chk_Comp;
string CMD_Chk_anm_bef;
string CMD_Chk_anm_aft;
string LGMode_profile;
string LGMode_verify;


void LGFunctionContainer::Create(int maxmode, double eps, 
	int rank, int mpiprocesses, MPIbyThread *thread, PrintCalculationStatus *status)
{
#ifdef _DEBUG
	LGMode_profile = "..\\debug\\LGmode_profile";
	LGMode_verify = "..\\debug\\LGmode_verify.dat";
#endif

	m_maxmode = maxmode;
	for(int j = 0; j < 2; j++){
		m_rr[j].resize(maxmode+1);
	}
	m_dr.resize(maxmode+1);
	m_points.resize(maxmode+1);
	m_LG.resize(maxmode+1);

	status->SetSubstepNumber(1, m_maxmode+1);

	int nmesh = 0;
	for(int n = 0; n <= m_maxmode; n++){
		for(int j = 0; j < 2; j++){
			m_rr[j][n].resize(m_maxmode+1);
		}
		m_dr[n].resize(m_maxmode+1);
		m_points[n].resize(m_maxmode+1);
		m_LG[n].resize(m_maxmode+1);
		if(n%mpiprocesses != rank){
			continue;
		}
		nmesh = max(nmesh, f_Assign(n, eps));
		status->AdvanceStep(1);
	}

#ifdef _DEBUG
	if(mpiprocesses == 1 && rank == 0 && !LGMode_verify.empty()){
		ofstream debug_out(LGMode_verify);
		int dn = 20, dm = 20;

		int mesh = m_maxmode*10+1;
		double rmax = m_rr[1][m_maxmode][m_maxmode];
		double dr = rmax/(mesh-1);

		vector<string> titles{"r"};
		for(int n = 0; n < m_maxmode; n += dn){
			for(int m = 0; m < m_maxmode; m += dm){
				titles.push_back("m"+to_string(m)+"n"+to_string(n)+"r");
				titles.push_back("m"+to_string(m)+"n"+to_string(n)+"c");
			}
		}
		PrintDebugItems(debug_out, titles);

		vector<double> items(titles.size());
		for(int i = 0; i < mesh; i++){
			double rr = i*dr;
			items[0] = rr;
			int j = 0;
			for(int n = 0; n < m_maxmode; n += dn){
				for(int m = 0; m < m_maxmode; m += dm){
					items[++j] = LGFunction(n, m, rr);
					items[++j] = Get(n, m, rr);
				}
			}
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif

	if(mpiprocesses == 1){
		return;
	}

	int ntmesh = nmesh;
	if(thread != nullptr){
		thread->Allreduce(&ntmesh, &nmesh, 1, MPI_INT, MPI_MAX, rank);
	}
	else{
		MPI_Allreduce(&ntmesh, &nmesh, 1, MPI_INT, MPI_MAX, MPI_COMM_WORLD);
	}

	double *ws = new double[nmesh*(m_maxmode+1)];
	for(int n = 0; n <= m_maxmode; n++){
		int trank = n%mpiprocesses;
		if(trank == rank){
			for(int m = n; m <= m_maxmode; m++){
				for(int i = 0; i < m_points[n][m]; i++){
					ws[m*nmesh+i] = m_LG[n][m][i];
				}
			}
		}
		if(thread != nullptr){
			thread->Bcast(ws, nmesh*(m_maxmode+1), MPI_DOUBLE, trank, rank);
			for(int m = n; m <= m_maxmode; m++){
				for(int j = 0; j < 2; j++){
					thread->Bcast(&m_rr[j][n][m], 1, MPI_DOUBLE, trank, rank);
				}
				thread->Bcast(&m_dr[n][m], 1, MPI_DOUBLE, trank, rank);
				thread->Bcast(&m_points[n][m], 1, MPI_INT, trank, rank);
			}
		}
		else{
			MPI_Bcast(ws, nmesh*(m_maxmode+1), MPI_DOUBLE, trank, MPI_COMM_WORLD);
			for(int m = n; m <= m_maxmode; m++){
				for(int j = 0; j < 2; j++){
					MPI_Bcast(&m_rr[j][n][m], 1, MPI_DOUBLE, trank, MPI_COMM_WORLD);
				}
				MPI_Bcast(&m_dr[n][m], 1, MPI_DOUBLE, trank, MPI_COMM_WORLD);
				MPI_Bcast(&m_points[n][m], 1, MPI_INT, trank, MPI_COMM_WORLD);
			}
		}
		if(trank != rank){
			for(int m = n; m <= m_maxmode; m++){
				m_LG[n][m].resize(m_points[n][m]);
				for(int i = 0; i < m_points[n][m]; i++){
					m_LG[n][m][i] = ws[m*nmesh+i];
				}
			}
		}
	}
	delete[] ws;
}

double LGFunctionContainer::Get(int n, int m, double r)
{
	if(n > m){
		swap(n, m);
	}
	if(r < m_rr[0][n][m] || r > m_rr[1][n][m]){
		return 0;
	}
	int rindex = (int)floor(0.5+(r-m_rr[0][n][m])/m_dr[n][m])-1;
	rindex = min(m_points[n][m]-3, max(0, rindex));
	double rl[3], LG[3];
	for(int j = 0; j < 3; j++){
		rl[j] = m_rr[0][n][m]+(rindex+j)*m_dr[n][m];
		LG[j] = m_LG[n][m][rindex+j];
	}
	return lagrange(r, rl[0], rl[1], rl[2], LG[0], LG[1], LG[2]);
}

int LGFunctionContainer::f_Assign(int n, double eps)
{
#ifdef _DEBUG
	int mdebug = 50;
	int ndebug = 50;
	bool isdebug;
	ofstream debug_out;
	vector<string> titles{"r", "LG"};
	vector<double> items(titles.size());
#endif

	int minimum_mode = 5;
	int minimum_pointspp = 10;
	int maxmesh = max(minimum_mode, m_maxmode)*minimum_pointspp+1;
	vector<double> r(maxmesh), lg(maxmesh);
	double rrange[2] = {0, 0}, dr, lgnext;
	int points = 0;
	for(int m = n; m <= m_maxmode; m++){
		int nmesh = max(minimum_mode, min(m, n))*minimum_pointspp+1;
		rrange[1] = sqrt((double)(m+n)/6+2);
		dr = (rrange[1]-rrange[0])/(nmesh-1);

		for(int j = 0; j < 2; j++){
			m_rr[j][n][m] = rrange[j];
		}
		m_dr[n][m] = dr;
		m_points[n][m] = nmesh;
		m_LG[n][m].resize(nmesh);
		points = max(points, m_points[n][m]);

#ifdef _DEBUG
		isdebug = (n%ndebug == 0 && m%mdebug == 0 && !LGMode_profile.empty());
		if(isdebug){
			debug_out.open(LGMode_profile+"m"+to_string(m)+"n"+to_string(n)+".dat");
			PrintDebugItems(debug_out, titles);
		}
#endif
		for(int i = 0; i < nmesh; i++){
			r[i] = rrange[0]+dr*i;
			m_LG[n][m][i] = LGFunction(n, m, r[i]);
#ifdef _DEBUG
			if(isdebug){
				items[0] = r[i];
				items[1] = m_LG[n][m][i];
				PrintDebugItems(debug_out, items);
			}
#endif
		}
#ifdef _DEBUG
		if(isdebug){
			debug_out.close();
		}
#endif
		int nini = 0;
		do{
			nini++;
			lgnext = LGFunction(n, m+1, r[nini]);
		} while(fabs(lgnext) < eps);
		rrange[0] = r[nini-1];
	}
	return points;
}

HGModalDecomp::HGModalDecomp(int layer,	PrintCalculationStatus *calcstatus, 
	int acclevel, int kmax, double cutoff, double fluxcut, Wigner4DManipulator *wig4d)
{
#ifdef _DEBUG
//IntegCMDAlongCF = "..\\debug\\CMD_integ_along_cf.dat";
//IntegCMDAlongR = "..\\debug\\CMD_integ_along_r.dat";
//CMDAmn1D = "..\\debug\\CMD_Amn_1d.dat";
//CMDCholeskyBef = "..\\debug\\CMD_Cholesky_bef.dat";
//CMDCholeskyAft = "..\\debug\\CMD_Cholesky_aft.dat";
//CMDFourierTheta = "..\\debug\\CMD_FFT_theta.dat";
//CMDFourierPhiBef = "..\\debug\\CMD_FFT_phi_bef.dat";
//CMDFourierPhiAft = "..\\debug\\CMD_FFT_phi_aft.dat";
//CMD_Anm_Func_1st= "..\\debug\\CMD_Anm_1st.dat";
CMD_Anm_Func_2nd= "..\\debug\\CMD_Anm_2nd.dat";
//CMD_Chk_1d = "..\\debug\\CMD_chk_1d.dat";
//CMD_Chk_FFT = "..\\debug\\CMD_chk_1d_fft.dat";
//CMD_Chk_2d = "..\\debug\\CMD_chk_2d.dat";
//CMD_Chk_2d_FFT = "..\\debug\\CMD_chk_2d_fft.dat";
//CMD_Chk_Comp = "..\\debug\\CMD_chk_comp.dat";
CMD_Chk_anm_bef = "..\\debug\\CMD_chk_anm_bef.dat";
CMD_Chk_anm_aft = "..\\debug\\CMD_chk_anm_aft.dat";
#endif

	m_calcstatus = calcstatus;
	m_acclevel = acclevel;
	m_layer = layer;
	m_lambda = wig4d->GetWavelength();
	m_fft = nullptr;
	m_nfftcurr = m_nfftmax = 0;
	m_ws = nullptr;
	m_hgmode = nullptr;
	m_maxmodenumber = kmax;
	m_lhgws.resize(m_maxmodenumber+1);
	m_cutoff = cutoff;
	m_fluxcut = fluxcut;
	m_undersrcopt = false;
	m_wig4d = wig4d;
	m_lgcont = nullptr;
	AllocateMemorySimpson(2, 2, 1);
}

HGModalDecomp::~HGModalDecomp()
{
	if(m_fft != nullptr){
		delete m_fft;
	}
	if(m_ws != nullptr){
		free(m_ws);
	}
	if(m_hgmode != nullptr){
		delete m_hgmode;
	}
}

void HGModalDecomp::MeasureTime(string cpucont)
{
	m_cpuclock.push_back(chrono::system_clock::now());
	int nmeas = (int)m_cpuclock.size()-1;
	if(nmeas > 0){
		double elapsed = static_cast<double>(chrono::duration_cast<chrono::microseconds>(m_cpuclock[nmeas]-m_cpuclock[nmeas-1]).count());
		m_elapsed.push_back(elapsed*1e-6);
		m_cpucont.push_back(cpucont);
	}
}

void HGModalDecomp::GetCPUTime(vector<double> *elapsed, vector<string> *cpucont)
{
	*elapsed = m_elapsed;
	*cpucont = m_cpucont;
}

void HGModalDecomp::LoadData()
{
	int type = m_wig4d->GetType();
	int jxy, idr[2], indices[NumberWignerUVPrm];
	if(type == WignerType2DX){
		jxy = 0;
		idr[0] = WignerUVPrmU;
		idr[1] = WignerUVPrmu;
		indices[WignerUVPrmV] = indices[WignerUVPrmv] = 0;
	}
	else{
		jxy = 1;
		idr[0] = WignerUVPrmV;
		idr[1] = WignerUVPrmv;
		indices[WignerUVPrmU] = indices[WignerUVPrmu] = 0;
	}
	m_xqarr.resize(2);
	m_wig4d->GetXYQArray(jxy, m_xqarr[0], m_xqarr[1]);

	for(int j = 0; j < 2; j++){
		m_xqarr[j] *= 1.0e-3; // mm -> m, mrad -> rad
		m_XQarr.push_back(m_xqarr[j]);
		m_mesh[j] = (int)m_xqarr[j].size();
		m_dxdq[j] = m_xqarr[j][1]-m_xqarr[j][0];
	}

	m_data.resize(m_mesh[0]);
	for(int n = 0; n < m_mesh[0]; n++){
		m_data[n].resize(m_mesh[1]);
		indices[idr[0]] = n;
		for(int m = 0; m < m_mesh[1]; m++){
			indices[idr[1]] = m;
			m_data[n][m] = m_wig4d->GetValue(indices);
		}
	}

	SetBeamParameters();
}

bool HGModalDecomp::AssingData(vector<vector<double>> *xyqarr, 
	vector<vector<double>> &data, bool isstat)
{
	m_data = data;
	if(xyqarr != nullptr){
		m_xqarr = *xyqarr;
		for(int j = 0; j < 2; j++){
			m_xqarr[j] *= 1.0e-3; // mm,mrad -> m,rad
			m_mesh[j] = (int)m_xqarr[j].size();
			m_dxdq[j] = m_xqarr[j][1]-m_xqarr[j][0];
		}
	}
	if(isstat){
		SetBeamParameters();
	}
	else{
		m_fluxspl.SetSpline2D(m_mesh, &m_xqarr[0], &m_xqarr[1], &m_data, false);
	}
	return true;
}

void HGModalDecomp::SetBeamParameters()
{
	double sigma[2], alpha, beta, emitt;
	vector<string> titles(3);
	titles[0] = TitleLablesDetailed[SrcX_];
	titles[1] = TitleLablesDetailed[SrcQX_];
	titles[2] = TitleLablesDetailed[Brill1D_];
	DataContainer datacont;
	vector<vector<vector<double>>> values(1);
	values[0] = m_data;
	datacont.Set2D(titles, m_xqarr, values);
	datacont.GetStatistics(sigma, &emitt, &alpha, 0);
	beta = sigma[0]*sigma[0]/emitt;
	m_zwaist = beta*alpha/hypotsq(alpha, 1.0);
	m_srcsize = sigma[0]/sqrt(hypotsq(alpha, 1.0));
	m_srcdiv = sigma[1];
}

void HGModalDecomp::SetAnm(vector<vector<complex<double>>> *Anm)
{
	m_Anm.resize(m_maxmodenumber+1);
	for(int n = 0; n <= m_maxmodenumber; n++){
		m_Anm[n].resize(m_maxmodenumber+1);
		for(int m = 0; m <= m_maxmodenumber; m++){
			m_Anm[n][m] = (*Anm)[n][m];
		}
	}
}

void HGModalDecomp::CreateHGMode(double *norm)
{
	if(norm != nullptr){
		m_hgmode = new HermiteGaussianMode(m_srcsize*(*norm), m_lambda, m_maxmodenumber, m_lgcont);
	}
	else{
		m_hgmode = new HermiteGaussianMode(m_srcsize, m_lambda, m_maxmodenumber, m_lgcont);
	}
}

int HGModalDecomp::GetIntegrateRange(vector<vector<double>> &rrange, bool forcedebug)
{
	int l = min(m_ncoef, m_mcoef);

	// envelope width of Gauss-Laguerre function
	double width = GetHLGWidth(l);
	double bwidth = 0.01*width;

	if(m_lgrange[0][m_ncoef][m_mcoef] < 0){
		double eps = 1.0e-6; // cut off of LGFunc
		double dr = 0.1; // increment to search the start position of integration
		double rini = 0;
		double lgg;
		lgg = fabs(GetLGFunction(m_lgcont, m_ncoef, m_mcoef, rini+dr));
		while(lgg < eps && rini < m_rmax) {
			rini += dr;
			lgg = fabs(GetLGFunction(m_lgcont, m_ncoef, m_mcoef, rini+dr));
		}
		if(rini < bwidth){ // 0~rini is not so wide compared to the envelope width
			m_lgrange[0][m_ncoef][m_mcoef] = 0;
		}
		else{
			m_lgrange[0][m_ncoef][m_mcoef] = rini;
		}
		if(rini > m_rmax){
			m_lgrange[0][m_ncoef][m_mcoef] = 0;
			m_lgrange[1][m_ncoef][m_mcoef] = rini;
		}
		else{
			double rfin = rini+width;
			if(m_rmax-rfin < bwidth){// rfin~m_rmax is not so wide, or rfin > m_rmax
				m_lgrange[1][m_ncoef][m_mcoef] = m_rmax;
			}
			else{
				m_lgrange[1][m_ncoef][m_mcoef] = rfin;
			}
		}
	}

	int k = abs(m_ncoef-m_mcoef);
	double flborder = m_flborder[k]; // 0~flborder: large flux range
	double dw = width/(1.0+l)*4.0; // width for 4 peaks
	int nbins[2] = {0, 0}, nsec = 1;
	double border[3], wbins[2];

	border[0] = m_lgrange[0][m_ncoef][m_mcoef];
	if(flborder > m_lgrange[0][m_ncoef][m_mcoef]+bwidth 
		&& flborder < m_lgrange[1][m_ncoef][m_mcoef]-bwidth){
		nsec = 2;
		border[1] = flborder;
	}
	border[nsec] = m_lgrange[1][m_ncoef][m_mcoef];

	int ndiv = 0;
	for(int j = 0; j < nsec; j++){
		wbins[j] = border[j+1]-border[j];
		nbins[j] = max(1, (int)floor(0.5+wbins[j]/dw));
		wbins[j] /= nbins[j];
		ndiv += nbins[j];
	}

	if(rrange.size() < 2){
		rrange.resize(2);
	}
	if(rrange[0].size() < ndiv+2){
		for(int j = 0; j < 2; j++){
			rrange[j].resize(ndiv+2);
		}
	}

	int ndivtot = ndiv, ntr = 0;
	for(int j = 0; j < nsec; j++){
		for (int n = 0; n < nbins[j]; n++){
			rrange[0][ntr] = border[j]+n*wbins[j];
			rrange[1][ntr] = rrange[0][ntr]+wbins[j];
			ntr++;
		}
	}

	if(m_lgrange[1][m_ncoef][m_mcoef] < m_rmax){
		ndivtot++;
		rrange[0][ndiv] = rrange[1][ndiv-1];
		rrange[1][ndiv] = m_rmax;
	}
	if(m_lgrange[0][m_ncoef][m_mcoef] > 0){
		ndivtot++;
		rrange[0][ndivtot-1] = 0;
		rrange[1][ndivtot-1] = rrange[0][0];
	}
	return ndivtot;
}

void HGModalDecomp::GetAnm(vector<vector<complex<double>>> *Anm, 
	int rank, int mpiprocesses, MPIbyThread *thread, bool forcedebug)
{
	int layers[2] = {0, -1};
	vector<double> result(2), rsum(2);
	vector<vector<double>> finit(1);
	finit[0].resize(2, 0.0);

	if(m_hgmode != nullptr){
		delete m_hgmode;
	}
	CreateHGMode();
	m_Anm.resize(m_maxmodenumber+1);

	m_calcstatus->SetSubstepNumber(m_layer, (m_maxmodenumber+1)/mpiprocesses);

	vector<vector<double>> rrange;
	int repmin[] = {6+m_acclevel, 4+m_acclevel}, idrep;

	for(int n = 0; n <= m_maxmodenumber; n++){
		m_ncoef = n;
		m_Anm[n].resize(m_maxmodenumber+1);
		if(rank != (n%mpiprocesses)){
			continue;
		}
		for(int m = 0; m <= n; m++){
			finit[0][0] = finit[0][1] = 0;
			m_mcoef = m;
			string fdebug = n == m ? IntegCMDAlongR : "";
			int ndiv = GetIntegrateRange(rrange, forcedebug);
			IntegrateSimpson(layers, rrange[0][0], rrange[1][0], 0.01/m_acclevel, repmin[0], &finit, &rsum, fdebug);
			for(int nrr = 1; nrr < ndiv; nrr++){
				idrep = nrr < ndiv-2 ? 0 : 1;
				IntegrateSimpson(layers, rrange[0][nrr], rrange[1][nrr], 0.01/m_acclevel, repmin[idrep], &finit, &result, fdebug, true);
				rsum += result;
			}
			m_Anm[n][m] = complex<double>(rsum[0], rsum[1]);
		}
		m_calcstatus->AdvanceStep(m_layer);
	}

	if(mpiprocesses > 1){
		double *ws = new double[2*(m_maxmodenumber+1)];
		for (int n = 0; n <= m_maxmodenumber; n++){
			int currrank = n%mpiprocesses;
			if(rank == currrank){
				for (int m = 0; m <= n; m++){
					ws[2*m] = m_Anm[n][m].real();
					ws[2*m+1] = m_Anm[n][m].imag();
				}
			}
			if(thread != nullptr){
				thread->Bcast(ws, 2*(n+1), MPI_DOUBLE, currrank, rank);
			}
			else{
				MPI_Bcast(ws, 2*(n+1), MPI_DOUBLE, currrank, MPI_COMM_WORLD);
			}
			if(rank != currrank){
				for (int m = 0; m <= n; m++){
					m_Anm[n][m] = complex<double>(ws[2*m], ws[2*m+1]);
				}
			}
		}
		delete[] ws;
	}

	for(int n = 0; n <= m_maxmodenumber; n++){
		for(int m = 0; m < n; m++){
			m_Anm[m][n] = conj(m_Anm[n][m]);
		}
	}

	if(Anm != nullptr){
		if(Anm->size() < m_maxmodenumber+1){
			Anm->resize(m_maxmodenumber+1);
		}
		for(int n = 0; n <= m_maxmodenumber; n++){
			if((*Anm)[n].size() < m_maxmodenumber+1){
				(*Anm)[n].resize(m_maxmodenumber+1);
			}
			for(int m = 0; m <= m_maxmodenumber; m++){
				(*Anm)[n][m] = m_Anm[n][m];
			}
		}
	}

#ifdef _DEBUG
	if(!CMDAmn1D.empty()){
		ofstream debug_out(CMDAmn1D);
		vector<string> titles {"n", "m", "re", "im"};
		PrintDebugItems(debug_out, titles);
		vector<double> values(titles.size());
		for (int n = 0; n <= m_maxmodenumber; n++){
			values[0] = n;
			for (int m = 0; m <= m_maxmodenumber; m++){
				values[1] = m;
				values[2] = m_Anm[m][n].real();
				values[3] = m_Anm[m][n].imag();
				PrintDebugItems(debug_out, values);
			}
		}
		debug_out.close();
	}
#endif
}

double HGModalDecomp::CostFunc(double x, vector<double> *y)
{
	int layers[2] = {0, -1};
	double xqrange[2];
	for(int j = 0; j < 2; j++){
		xqrange[j] = minmax(m_xqarr[j], true);
	}
	double rlim = max(xqrange[0]/x, xqrange[1]*x);
	double dhr = min(m_dxdq[0]/x, m_dxdq[1]*x);
	int rmesh = (int)floor(sqrt(hypotsq(xqrange[0]/x, xqrange[1]*x))/dhr);

	vector<double> rarr(rmesh+1), farr(rmesh+1);
	for(int nr = 0; nr <= rmesh; nr++){
		rarr[nr] = dhr*(double)nr;
		int nphi = max(16, (int)ceil(PI2*rarr[nr]/dhr));
		double dphi = PI2/nphi, phi, xq[3], flux;
		farr[nr] = 0;
		for(int n = 0; n < nphi; n++){
			phi = (n+0.5)*dphi;
			xq[0] = rarr[nr]*cos(phi)*x;
			if(fabs(xq[0]) > xqrange[0]){
				continue;
			}
			xq[1] = rarr[nr]*sin(phi)/x;
			if(fabs(xq[1]) > xqrange[1]){
				continue;
			}
			flux = m_fluxspl.GetValue(xq, true);
			farr[nr] += flux*dphi;
		}
	}
	m_F0spl.SetSpline(rmesh+1, &rarr, &farr, true);

	double fmax = minmax(farr, true);
	m_flborder[0] = rarr[rmesh];
	for(int nr = rmesh; nr >= 0; nr--){
		if(farr[nr] >= 0.1*fmax){
			m_flborder[0] = rarr[nr];
			break;
		}
	}

	m_rmax = rlim;

	vector<double> result(2, 0.0), rsum(2, 0.0);
	vector<vector<double>> finit(1);
	finit[0].resize(2);

	if(m_hgmode != nullptr){
		delete m_hgmode;
	}
	CreateHGMode(&x);

	double Asum = 0;
	int repmin[] = {6+m_acclevel, 4+m_acclevel}, idrep;
	vector<vector<double>> rrange;

	m_maxmodecurr = m_maxmodenumber;
	int nconv = 0;
	for(int mn = 0; mn <= m_maxmodenumber; mn++){
		finit[0][0] = finit[0][1] = 0;
		m_mcoef = m_ncoef = mn;
		int ndiv = GetIntegrateRange(rrange, false);
		IntegrateSimpson(layers, rrange[0][0], rrange[1][0], 0.01/m_acclevel, repmin[0], &finit, &rsum, IntegCMDAlongCF);
		for(int nrr = 1; nrr < ndiv; nrr++){
			idrep = nrr < ndiv-2 ? 0 : 1;
			IntegrateSimpson(layers, rrange[0][nrr], rrange[1][nrr], 0.01/m_acclevel, repmin[idrep], &finit, &result, IntegCMDAlongCF, true);
			rsum += result;
		}
		Asum += rsum[0];
		if(fabs(rsum[0])/Asum < m_fluxcut){
			nconv++;
			if(nconv > 1){
				m_maxmodecurr = mn;
				break;
			}
		}
		else{
			nconv = 0;
		}
	}

	for(int mn = 0; mn <= m_maxmodenumber; mn++){
		// reset m_lgrange (Gauss-Laguerre range) because m_rmax changes
		for(int j = 0; j < 2; j++){
			m_lgrange[j][mn][mn] = -1;
		}
	}
	return 1.0-Asum;
}

void HGModalDecomp::QSimpsonIntegrand(int layer, double rh, vector<double> *density)
{
	if(rh == 0){
		(*density)[0] = (*density)[1] = 0;
		return;
	}
	double WLG = GetLGFunction(m_lgcont, m_ncoef, m_mcoef, rh)/m_norm_factor;

	if(m_undersrcopt){
		(*density)[0] = rh*WLG*m_F0spl.GetValue(rh);
		(*density)[1] = 0;
	}
	else{
		int kmn = abs(m_ncoef-m_mcoef);
		(*density)[0] = rh*WLG*m_fspl[0][kmn].GetValue(rh, true);
		(*density)[1] = rh*WLG*m_fspl[1][kmn].GetValue(rh, true);
	}
}

complex<double> HGModalDecomp::GetComplexAmpSingle(int mode, double eps, double xh)
{
	complex<double> Es(0.0, 0.0);
	HGFunctions(m_maxmodenumber, xh, m_lhgws);
	for(int m = 0; m <= m_maxmodenumber; m++){		
		if(abs(m_anm[m][mode]) > eps){
			Es += m_lhgws[m]*m_anm[m][mode];
		}
	}
	return Es;
}

void HGModalDecomp::GetComplexAmp(vector<double> &xyarr, 
	vector<vector<complex<double>>> *Ea, double eps, int pmax, bool issimple, bool skipstep)
{
	double sigpi = 2.0*SQRTPI*m_srcsize;
	int mesh = (int)xyarr.size();

	pmax = GetMaxOrder(pmax);
	if(Ea->size() < pmax+1){
		Ea->resize(pmax+1);
	}

	m_calcstatus->SetSubstepNumber(m_layer, mesh);
	for(int mode = 0; mode <= pmax; mode++){
		if((*Ea)[mode].size() < mesh){
			(*Ea)[mode].resize(mesh);
		}
	}
	for(int nx = 0; nx < mesh; nx++){
		if(issimple){
			HGFunctions(pmax, xyarr[nx]/sigpi, m_lhgws);
		}
		for(int mode = 0; mode <= pmax; mode++){
			if(issimple){
				(*Ea)[mode][nx] = m_lhgws[mode];
			}
			else{
				(*Ea)[mode][nx] = GetComplexAmpSingle(mode, eps, xyarr[nx]/sigpi);
			}
		}
		if(!skipstep){
			m_calcstatus->AdvanceStep(m_layer);
		}
	}
}

void HGModalDecomp::GetApproximatedAnm(int pmax, double eps, 
		vector<complex<double>> *aAnm, vector<int> *nindex, vector<int> *mindex)
{
	pmax = GetMaxOrder(pmax);
	aAnm->clear(); nindex->clear(); mindex->clear();
	complex<double> Anm;

	m_calcstatus->SetSubstepNumber(m_layer, 1+m_maxmodenumber);

	for(int n = 0; n <= m_maxmodenumber; n++){
		for(int m = 0; m <= m_maxmodenumber; m++){
			Anm = complex<double>(0.0, 0.0);
			for(int p = 0; p <= pmax; p++){
				if(abs(m_anm[n][p]) > eps && abs(m_anm[m][p]) > eps){
					Anm = Anm+m_anm[n][p]*conj(m_anm[m][p]);
				}
			}
			if(abs(Anm) > eps*eps){
				aAnm->push_back(Anm);
				nindex->push_back(n);
				mindex->push_back(m);
			}
		}
		m_calcstatus->AdvanceStep(m_layer);
	}
}


void HGModalDecomp::GetFluxConsistency(
	int pmax, double eps, vector<double> &fr, vector<double> &fa)
{
	pmax = GetMaxOrder(pmax);

	fa.resize(1+pmax, 0.0);
	fr.resize(1+pmax, 0.0);

	double sum = 0;
	for(int p = 0; p <= m_maxmodenumber; p++){
		for(int n = 0; n <= m_maxmodenumber; n++){
			double ff = abs(m_anm[n][p]);
			sum += ff*ff;
		}
	}
	if(sum > 1){
		double mag = sqrt(sum);
		for(int p = 0; p <= m_maxmodenumber; p++){
			for(int n = 0; n <= m_maxmodenumber; n++){
				m_anm[n][p] /= mag;
			}
		}
	}

	for(int p = 0; p <= pmax; p++){
		if(p == 0){
			fa[p] = 0;
		}
		else{
			fa[p] = fa[p-1];
		}
		fr[p] = 0;
		for(int n = 0; n <= m_maxmodenumber; n++){
			double ff = abs(m_anm[n][p]);
			if (ff > eps){
				fa[p] += ff*ff;
				fr[p] += ff*ff;
			}
		}
	}
}

void HGModalDecomp::ReconstructExport(int pmax, double epsanm, double *CMDerr, 
	vector<double> &data, int rank, int mpiprocesses, MPIbyThread *thread)
{
	vector<double> stderror[NumberWigError];
	double errors[NumberWigError];
	vector<complex<double>> aAnm;
	vector<int> mindex, nindex;
	vector<vector<complex<double>>> ws;
	int indices[NumberWignerUVPrm], iq, ixy, mesh[2];
	double fnorm;

	pmax = GetMaxOrder(pmax);
	fnorm = m_norm_factor/(2.0*SQRTPI*m_srcsize);

	for(int j = 0; j < 2; j++){
		mesh[j] = (int)m_XQarr[j].size();
	}
	data.resize(mesh[0]*mesh[1]);

	f_AssignWignerArray(&ws, &m_XQarr[0], &m_XQarr[1]);

	if(m_wig4d->GetType() == WignerType2DX){
		indices[WignerUVPrmV] = 0;
		indices[WignerUVPrmv] = 0;
		ixy = WignerUVPrmU;
		iq = WignerUVPrmu;
	}
	else{
		indices[WignerUVPrmU] = 0;
		indices[WignerUVPrmu] = 0;
		ixy = WignerUVPrmV;
		iq = WignerUVPrmv;
	}

	double degcoh;
	GetApproximatedAnm(pmax, epsanm, &aAnm, &nindex, &mindex);
	f_ComputeWholeWigner(fnorm, indices, ixy, iq, &aAnm, &nindex, 
		&mindex, &ws, data, rank, mpiprocesses, thread);
	m_wig4d->GetCoherenceDeviation(&degcoh, errors, data);
	*CMDerr = errors[WigErrorDeviation];

#ifdef _DEBUG
	if(!CMD_Chk_Comp.empty()){

		m_calcstatus->SetSubstepNumber(m_layer, mesh[0]);
		m_calcstatus->ResetCurrentStep(m_layer);
		m_calcstatus->ResetTotal();

		int hqmesh = (mesh[1]-1)/2;
		vector<double> datar(mesh[0]*mesh[1]);
		vector<double> W;
		double dq = m_XQarr[1][1]-m_XQarr[1][0];
		for (int n = 0; n < mesh[0]; n++){
			GetWignerAt(pmax, epsanm, m_XQarr[0][n], dq, hqmesh, W);
			for (int m = 0; m < mesh[1]; m++){
				datar[m*mesh[0]+n] = fnorm*W[m];
			}
			m_calcstatus->AdvanceStep(m_layer);
		}
		double wmax = minmax(data, true);
		vector<double> items(5);
		ofstream debug_out(CMD_Chk_Comp);
		for (int n = 0; n < mesh[0]; n++){
			items[0] = m_XQarr[0][n];
			for (int m = 0; m < mesh[1]; m++){
				items[1] = m_XQarr[1][m];
				items[2] = data[m*mesh[0]+n];
				items[3] = datar[m*mesh[0]+n];
				items[4] = (items[3]-items[2])/wmax;
				PrintDebugItems(debug_out, items);
			}
		}
		debug_out.close();
	}
#endif

}

void HGModalDecomp::GetWignerAt(int pmax, double eps,
	double xy, double dq, int hqmesh, vector<double> &W)
{
	int nfft = fft_number(2*hqmesh+1, 1), nskip = 1;
	double xyh, xyr, sigpi = 2.0*SQRTPI*m_srcsize;
	double dxy = 1.0/(nfft*dq/m_lambda);
	while(dxy > m_srcsize/max(2, pmax/4)){
		dxy *= 0.5;
		nfft <<= 1;
	}
	double hgwidth = 2.0*sigpi*GetHLGWidth(pmax);
	while(nfft*dxy < hgwidth){
		nfft <<= 1;
		nskip <<= 1;
	}

	double *ws = new double[2*nfft];
	complex<double> exycomp[2], exy;

	if(W.size() < 2*hqmesh+1){
		W.resize(2*hqmesh+1);
	}
	fill(W.begin(), W.end(), 0.0);

	FastFourierTransform fft(1, nfft);

	for(int p = 0; p <= pmax; p++){
		for(int n = 0; n < nfft; n++){
			xyr = dxy*fft_index(n, nfft, 1);
			for(int j = 0; j < 2; j++){
				xyh = j == 0 ? (xy+xyr*0.5)/sigpi : (xy-xyr*0.5)/sigpi;
				exycomp[j] = GetComplexAmpSingle(p, eps, xyh);
			}

			exy = exycomp[0]*conj(exycomp[1]);
			ws[2*n] = exy.real();
			ws[2*n+1] = exy.imag();
		}

#ifdef _DEBUG
		if (!CMD_Chk_FFT.empty()){
			ofstream debug_out(CMD_Chk_FFT);
			PrintDebugFFT(debug_out, dxy, ws, nfft, nfft, false);
		}
#endif

		fft.DoFFT(ws);
		for(int n = -hqmesh; n <= hqmesh; n++){
			int index = fft_index(n*nskip, nfft, -1);
			W[n+hqmesh] += ws[2*index]*dxy;
		}
#ifdef _DEBUG
		if (!CMD_Chk_1d.empty()){
			ofstream debug_out(CMD_Chk_1d);
			vector<double> items(2);
			for(int n = -hqmesh; n <= hqmesh; n++){
				items[0] = dq*n;
				items[1] = W[n+hqmesh];
				PrintDebugItems(debug_out, items);
			}
		}
#endif
	}

	delete[] ws;
}

void HGModalDecomp::SetLGContainer(LGFunctionContainer *lgcont)
{
	m_lgcont = lgcont;
	m_hgmode->SetLGContainer(lgcont);
}

void HGModalDecomp::SetGSModel()
{
	double ehat = m_srcdiv*m_srcsize/(m_lambda/4/PI);
	double an0 = sqrt(2/(1+ehat)), earg = (ehat-1)/(ehat+1);

	vector<double> an(m_maxmodenumber+1);
	double Asum = 0;
	int maxorder;
	m_calcstatus->SetSubstepNumber(m_layer, 1+m_maxmodenumber);
	for(int n = 0; n <= m_maxmodenumber; n++){
		maxorder = n;
		double arglim = pow(INFINITESIMAL, 2.0/n);
		if(earg < arglim){
			break;
		}
		an[n] = an0*pow(earg, n/2.0);
		Asum += an[n]*an[n];
		if(an[n]*an[n]/Asum < m_fluxcut){
			break;
		}
		m_calcstatus->AdvanceStep(m_layer);
	}
	m_maxmodenumber = maxorder;

	m_anm.resize(m_maxmodenumber+1);
	m_Anm.resize(m_maxmodenumber+1);

	for(int n = 0; n <= m_maxmodenumber; n++){
		m_anm[n].resize(m_maxmodenumber+1, complex<double> {0.0, 0.0});
		m_Anm[n].resize(m_maxmodenumber+1, complex<double> {0.0, 0.0});
		m_anm[n][n] = complex<double> {an[n], 0.0};
		m_Anm[n][n] = complex<double>{an[n]*an[n], 0.0};
	}

	m_srcsize /= sqrt(ehat);
	f_SetupDataGrid();
	CreateHGMode();
}

int HGModalDecomp::GetMaxOrder(int pmax)
{
	if(pmax < 0){
		pmax = m_maxmodenumber;
	}
	else{
		pmax = min(m_maxmodenumber, pmax);
	}
	return pmax;
}

double HGModalDecomp::CholeskyDecomp(vector<vector<complex<double>>> *anm, vector<int> *order)
{
	m_calcstatus->SetSubstepNumber(m_layer, 8);

#ifdef _HGTIME
	MeasureTime("");
#endif

	vector<double> AA(m_maxmodenumber+1);
	vector<int> index(m_maxmodenumber+1);
	for(int n = 0; n <= m_maxmodenumber; n++){
		AA[n] = m_Anm[n][n].real();
		index[n] = n;
	}
	sort(AA, index, m_maxmodenumber+1, false);

	m_calcstatus->AdvanceStep(m_layer);

	if(order != nullptr){
		order->resize(m_maxmodenumber+1);
		for(int n = 0; n <= m_maxmodenumber; n++){
			(*order)[n] = index[n];
		}
	}

	MatrixXcd A(m_maxmodenumber+1, m_maxmodenumber+1);

	m_calcstatus->AdvanceStep(m_layer);

	double Asum = 0;
	for(int n = 0; n <= m_maxmodenumber; n++){
		for(int m = 0; m <= m_maxmodenumber; m++){
			A(n, m) = m_Anm[index[n]][index[m]];
		}
		Asum += A(n, n).real();
	}

	SelfAdjointEigenSolver<MatrixXcd> ES(A);

#ifdef _HGTIME
	MeasureTime("Get Eigen Values");
#endif

	m_calcstatus->AdvanceStep(m_layer);

	vector<double> eig(m_maxmodenumber+1);
	bool ispos = true;
	for(int i = 0; i <= m_maxmodenumber; i++){
		eig[i] = ES.eigenvalues()(i);
		if(eig[i] < 0){
			ispos = false;
			break;
		}
	}

	if(!ispos){
		MatrixXcd V = ES.eigenvectors();
		MatrixXcd Vinv = V.inverse();
		m_calcstatus->AdvanceStep(m_layer);

#ifdef _HGTIME
		MeasureTime("Get Inverse Matrix");
#endif

		MatrixXcd D(m_maxmodenumber+1, m_maxmodenumber+1);
		for(int j = 0; j <= m_maxmodenumber; j++){
			for(int i = 0; i <= m_maxmodenumber; i++){
				if(i == j){
					D(i, i) = max(0.0, ES.eigenvalues()(i));
				}
				else{
					D(j, i) = 0.0;
				}
			}
		}

#ifdef _DEBUG
		if (!CMDCholeskyBef.empty()){
			ofstream debug_out(CMDCholeskyBef);
			vector<double> values(m_maxmodenumber+2);
			for(int n = 0; n <= m_maxmodenumber; n++){
				values[0] = eig[n];
				for(int m = 0; m <= m_maxmodenumber; m++){
					values[m+1] = A(n, m).real();
				}
				PrintDebugItems(debug_out, values);
			}
		}
#endif

		A = V*D*Vinv;

#ifdef _HGTIME
		MeasureTime("Reconstruct Anm");
#endif

#ifdef _DEBUG
		if (!CMDCholeskyBef.empty()){
			ofstream debug_out(CMDCholeskyBef);
			vector<double> values(m_maxmodenumber+2);
			for(int n = 0; n <= m_maxmodenumber; n++){
				values[0] = D(n, n).real();
				for(int m = 0; m <= m_maxmodenumber; m++){
					values[m+1] = A(n, m).real();
				}
				PrintDebugItems(debug_out, values);
			}
		}
#endif
	}
	else{
		m_calcstatus->AdvanceStep(m_layer);
	}

	m_calcstatus->AdvanceStep(m_layer);

	LLT<MatrixXcd> ldlt(A);
	MatrixXcd L = ldlt.matrixL();

#ifdef _HGTIME
	MeasureTime("Get LLT");
#endif

	vector<vector<complex<double>>> anmtmp;
	anmtmp.resize(m_maxmodenumber+1);
	for(int n = 0; n <= m_maxmodenumber; n++){
		anmtmp[n].resize(m_maxmodenumber+1);
	}
	complex<double> anmsc;
	double anmre, anmim;
	for(int n = 0; n <= m_maxmodenumber; n++){
		for(int m = 0; m <= m_maxmodenumber; m++){
			anmsc = L(n, m);
			anmre = anmsc.real();
			anmim = anmsc.imag();
			if(fabs(anmre) < m_cutoff){
				anmre = 0;
			}
			if(fabs(anmim) < m_cutoff){
				anmim = 0;
			}
			if(order != nullptr){
				anmtmp[n][m] = complex<double>(anmre, anmim);
			}
			else{
				anmtmp[index[n]][index[m]] = complex<double>(anmre, anmim);
			}
		}
	}

	m_calcstatus->AdvanceStep(m_layer);

	for(int p = 0; p <= m_maxmodenumber; p++){
		AA[p] = 0;
		for(int n = 0; n <= m_maxmodenumber; n++){
			AA[p] += abs(anmtmp[n][p])*abs(anmtmp[n][p]);
		}
		index[p] = p;
	}
	sort(AA, index, m_maxmodenumber+1, false);

	m_anm.resize(m_maxmodenumber+1);
	for(int n = 0; n <= m_maxmodenumber; n++){
		m_anm[n].resize(m_maxmodenumber+1);
	}
	for(int p = 0; p <= m_maxmodenumber; p++){
		for(int n = 0; n <= m_maxmodenumber; n++){
			m_anm[n][p] = anmtmp[n][index[p]];
		}
	}

	m_calcstatus->AdvanceStep(m_layer);

	if(anm != nullptr){
		anm->resize(m_maxmodenumber+1);
		for(int n = 0; n <= m_maxmodenumber; n++){
			(*anm)[n].resize(m_maxmodenumber+1);
			for(int p = 0; p <= m_maxmodenumber; p++){
				(*anm)[n][p] = m_anm[n][p];
			}
		}
	}

	MatrixXcd Lt = L.adjoint();
	MatrixXcd M =L*Lt-A;
	m_experr = 0;
	for(int n = 0; n <= m_maxmodenumber; n++){
		for(int m = 0; m <= m_maxmodenumber; m++){
			m_experr = max(m_experr, abs(M(n, m)));
		}
	}
	m_experr = sqrt(m_experr);

	m_calcstatus->AdvanceStep(m_layer);

#ifdef _HGTIME
	MeasureTime("Get Error");
#endif

	return m_experr;
}

void HGModalDecomp::Get_anm(vector<vector<complex<double>>> &anm)
{
	anm = m_anm;
}

void HGModalDecomp::Set_anm(vector<vector<complex<double>>> &anm)
{
	m_anm = anm;
}

void HGModalDecomp::OptimizeSrcSize(double *defsrcsize, int *layer)
{
	vector<double> y(1);
	double srcsize[3];
	bool isok = true;
	int nlayer = layer != nullptr ? *layer : m_layer;

	for(int j = 0; j < 2; j++){
		m_lgrange[j].resize(m_maxmodenumber+1);
		for (int n = 0; n <= m_maxmodenumber; n++){
			m_lgrange[j][n].resize(m_maxmodenumber+1, -1);
		}
	}
	if(m_flborder.size() < m_maxmodenumber+1){
		m_flborder.resize(m_maxmodenumber+1);
	}

	if(defsrcsize == nullptr){
		m_undersrcopt = true;
		f_SetupDataGrid();
		m_calcstatus->SetSubstepNumber(nlayer, 4);

		double Wref = CostFunc(1.0, &y), Wr;
		m_calcstatus->AdvanceStep(nlayer);

		srcsize[1] = 1.0;
		while(1){
			srcsize[0] = srcsize[1]*0.5;
			Wr = CostFunc(srcsize[0], &y);
			if(Wr > Wref){
				break;
			}
			srcsize[1] = srcsize[0];
			Wref = Wr;
			if(srcsize[1] < 0.01){
				isok = false;
				break;
			}
		};
		m_calcstatus->AdvanceStep(nlayer);

		while(isok){
			srcsize[2] = srcsize[1]*2.0;
			Wr = CostFunc(srcsize[2], &y);
			if(Wr > Wref){
				break;
			}
			srcsize[1] = srcsize[2];
			Wref = Wr;
			if(srcsize[1] > 100.0){
				isok = false;
				break;
			}
		};
		m_calcstatus->AdvanceStep(nlayer);

		double optsize = 1;
		if(isok){
			BrentMethod(srcsize[0], srcsize[1], srcsize[2], 1e-3, false, 1.0, &optsize, &y);
		}
		m_calcstatus->AdvanceStep(nlayer);
		m_srcsize *= optsize;
		f_SetupDataGrid(&optsize);
		m_maxmodenumber = m_maxmodecurr;
		m_undersrcopt = false;
	}
	else{
		m_srcsize = *defsrcsize;
		f_SetupDataGrid();
	}
}

void HGModalDecomp::FourierExpansion()
{
	vector<double> fr, fi;
	vector<vector<double>> frarr, fiarr, fmarr;
	double dhr = min(m_dxdq[0], m_dxdq[1]);
	double xymax[2];
	for(int j = 0; j < 2; j++){
		xymax[j] = minmax(m_xqarr[j], true);
	}
	int rmesh = (int)floor(sqrt(hypotsq(xymax[0], xymax[1]))/dhr);
	vector<double> rarr;

	for(int j = 0; j < 2; j++){
		m_fspl[j].resize(m_maxmodenumber+1);
	}
	frarr.resize(m_maxmodenumber+1);
	fiarr.resize(m_maxmodenumber+1);
	fmarr.resize(m_maxmodenumber+1);

	for(int k = 0; k <= m_maxmodenumber; k++){
		frarr[k].resize(rmesh+1);
		fiarr[k].resize(rmesh+1);
		fmarr[k].resize(rmesh+1);
	}
	rarr.resize(rmesh+1);

	for(int nr = 0; nr <= rmesh; nr++){
		rarr[nr] = dhr*(double)nr;
		FourierExpansionSingle(rarr[nr], m_maxmodenumber, &fr, &fi);
		for(int k = 0; k <= m_maxmodenumber; k++){
			frarr[k][nr] = fr[k];
			fiarr[k][nr] = fi[k];
			fmarr[k][nr] = sqrt(hypotsq(fr[k], fi[k]));
		}
	}

	for(int k = 0; k <= m_maxmodenumber; k++){
		m_fspl[0][k].SetSpline(rmesh+1, &rarr, &frarr[k], true);
		m_fspl[1][k].SetSpline(rmesh+1, &rarr, &fiarr[k], true);
		double fmax = minmax(fmarr[k], true);
		m_flborder[k] = rarr[rmesh];
		for(int nr = rmesh; nr >= 0; nr--){
			if(fmarr[k][nr] > 0.1*fmax){
				// pick up a "border" to separate the range by flux
				m_flborder[k] = rarr[nr];
				break;
			}
		}
	}
	m_rmax = m_r2max = rarr[rmesh];
	m_r2max *= m_r2max;

#ifdef _DEBUG
	if(!CMDFourierTheta.empty()){
		ofstream debug_out(CMDFourierTheta);
		vector<double> values(2*(m_maxmodenumber+1)+1);
		for (int nr = 0; nr <= rmesh; nr++){
			values[0] = rarr[nr];
			for (int k = 0; k <= m_maxmodenumber; k++){
				values[2*k+1] = frarr[k][nr];
				values[2*k+2] = fiarr[k][nr];
			}
			PrintDebugItems(debug_out, values);
		}
	}
#endif
}

void HGModalDecomp::FourierExpansionSingle(
	double rh, int kmax, vector<double> *fr, vector<double> *fi)
{
	int ndata = max(kmax, (int)ceil(rh/min(m_dxdq[0], m_dxdq[1])));
	int nfft = 1;
	while(nfft < ndata*8){
		nfft <<= 1;
	}

	if(nfft > m_nfftmax){
		m_ws = (double *)realloc(m_ws, sizeof(double)*nfft);
		m_nfftmax = nfft;
	}
	if(nfft != m_nfftcurr){
		if(m_fft != nullptr){
			delete m_fft;
		}
		m_fft = new FastFourierTransform(1, nfft);
		m_nfftcurr = nfft;
	}

	double dphi = PI2/(double)nfft, phi, xqh[2];

	for(int n = 0; n < nfft; n++){
		phi = dphi*(double)n;
		xqh[0] = rh*cos(phi);
		xqh[1] = rh*sin(phi);
		xqh[0] -= xqh[1]*m_zwaist;

		if(m_xqarr[0].front() > xqh[0] || m_xqarr[0].back() < xqh[0]
			|| m_xqarr[1].front() > xqh[1] || m_xqarr[1].back() < xqh[1])
		{
			m_ws[n] = 0.0;
		}
		else{
			m_ws[n] = m_fluxspl.GetValue(xqh);
		}
	}

#ifdef _DEBUG
	if(!CMDFourierPhiBef.empty()){
		ofstream debug_out(CMDFourierPhiBef);
		vector<double> wsl(2);
		for (int n = 0; n < nfft; n++){
			wsl[0] = dphi*(double)n;
			wsl[1] = m_ws[n];
			PrintDebugItems(debug_out, wsl);
		}
	}
#endif

	if(fr->size() <= kmax){
		fr->resize(kmax+1);
	}
	if(fi->size() <= kmax){
		fi->resize(kmax+1);
	}

	m_fft->DoRealFFT(m_ws);
	for(int k = 0; k <= kmax; k++){
		(*fr)[k] = m_ws[2*k]*dphi;
		if(k == 0){
			(*fi)[k] = 0;
		}
		else{
			(*fi)[k] = -m_ws[2*k+1]*dphi;
			// take the complex conjugate
		}
	}

#ifdef _DEBUG
	if(!CMDFourierPhiAft.empty()){
		ofstream debug_out(CMDFourierPhiAft);
		vector<double> wsl(3);
		for (int k = 0; k <= kmax; k++){
			wsl[0] = k;
			wsl[1] = (*fr)[k];
			wsl[2] = (*fi)[k];
			PrintDebugItems(debug_out, wsl);
		}
	}
#endif
}

void HGModalDecomp::DumpIntensityProfile(double eps, int pmax, double xyrange, double dxy, 
	vector<double> &xyarr, vector<vector<vector<double>>> &data)
{
	vector<vector<complex<double>>> Ea;

	pmax = GetMaxOrder(pmax);

	int mesh = (int)floor(0.5+xyrange/dxy);
	xyarr.resize(2*mesh+1);
	for(int n = -mesh; n <= mesh; n++){
		xyarr[n+mesh] = dxy*n;
	}

	mesh = 2*mesh+1;
	GetComplexAmp(xyarr, &Ea, eps, pmax, false);

	data.resize(pmax+1);
	for(int p = 0; p <= pmax; p++){
		data[p].resize(1);
		data[p][0].resize(mesh, 0.0);
	}
	double coef = m_norm_factor*1e3*m_lambda/(2*SQRTPI*m_srcsize);
		// /mm.mrad -> /mm
	for(int p = 0; p <= pmax; p++){
		for(int n = 0; n < mesh; n++){
			data[p][0][n] = coef*hypotsq(Ea[p][n].real(), Ea[p][n].imag());
		}
	}
}

void HGModalDecomp::DumpTotalIntensityProfile(
	double eps, int pmax, vector<double> &xyarr, vector<vector<double>> &data)
{
	vector<vector<complex<double>>> Ea;
	vector<double> dummy;

	int jxy = m_wig4d->GetType() == WignerType2DX ? 0 : 1;
	m_wig4d->GetXYQArray(jxy, xyarr, dummy);

	pmax = GetMaxOrder(pmax);
	vector<double> xyarrm(xyarr);
	xyarrm *= 1e-3; // mm -> m
	GetComplexAmp(xyarrm, &Ea, eps, pmax, false);

	int mesh = (int)xyarr.size();
	data.resize(2);
	for(int j = 0; j < 2; j++){
		data[j].resize(mesh, 0.0);
	}

	double coef = m_norm_factor*1e3*m_lambda/(2*SQRTPI*m_srcsize);
	// /mm.mrad -> /mm
	for(int p = 0; p <= pmax; p++){
		for(int n = 0; n < mesh; n++){
			data[1][n] += coef*hypotsq(Ea[p][n].real(), Ea[p][n].imag());
		}
	}
	m_wig4d->GetProjection(data[0]);
}

void HGModalDecomp::DumpFieldProfile(const char *bufbin, 
	double eps, int pmax, double xyrange, double dxy, bool iswrite,
	vector<double> &xyarr, vector<vector<double>> &datar, vector<vector<double>> &datai)
{
	vector<vector<complex<double>>> Ea;

	pmax = GetMaxOrder(pmax);

	int mesh = (int)floor(0.5+xyrange/dxy);
	xyarr.resize(2*mesh+1);
	for(int n = -mesh; n <= mesh; n++){
		xyarr[n+mesh] = dxy*n;
	}
	mesh = 2*mesh+1;
	GetComplexAmp(xyarr, &Ea, eps, pmax, false);
	if(bufbin != nullptr){
		f_ExportFieldBinary(bufbin, &xyarr, &Ea);
	}

	if(iswrite){
		datar.resize(pmax+1);
		datai.resize(pmax+1);
		for(int p = 0; p <= pmax; p++){
			datar[p].resize(mesh);
			datai[p].resize(mesh);
			for(int n = 0; n < mesh; n++){
				datar[p][n] = Ea[p][n].real();
				datai[p][n] = Ea[p][n].imag();
			}
		}
	}
}

void HGModalDecomp::WriteResults(string &result, double cmderr[])
{
	int nmodes = m_maxmodenumber+1;
	vector<double> anm[2];
	vector<int> anmidx[2];
	GetSparseMatrix(nmodes, m_anm, anm, anmidx);

	double tflux = m_norm_factor*m_lambda*1.0e+6; // /mm.mrad -> /m.rad
	stringstream ssresult;
	ssresult << "{" << endl;

	WriteJSONValue(ssresult, JSONIndent, m_maxmodenumber, MaxOrderLabel.c_str(), false, true);
	WriteJSONValue(ssresult, JSONIndent, m_lambda, WavelengthLabel.c_str(), false, true);
	WriteJSONValue(ssresult, JSONIndent, tflux, FluxCMDLabel.c_str(), false, true);
	WriteJSONValue(ssresult, JSONIndent, m_srcsize, SrcSizeLabel.c_str(), false, true);
	WriteCommonJSON(ssresult, cmderr, m_norm_factor, anm, anmidx);

	result = ssresult.str();
}

void HGModalDecomp::LoadResults(int maxorder, 
	double srcsize, double fnorm, vector<double> &anmre, vector<double> &anmim)
{
	m_maxmodenumber = maxorder;
	m_srcsize = srcsize;
	m_norm_factor = fnorm;
	int nmodes = m_maxmodenumber+1;
	m_anm.resize(nmodes);
	for(int n = 0; n < nmodes; n++){
		m_anm[n].resize(nmodes);
		for(int m = 0; m < nmodes; m++){
			int nm = n*nmodes+m;
			m_anm[n][m] = complex<double>(anmre[nm], anmim[nm]);
		}
	}
	CreateHGMode();
}

//----- private functions -----
void HGModalDecomp::f_SetupDataGrid(double *ladj)
{
	if(ladj != nullptr){
		m_xqarr[0] /= *ladj;
		m_dxdq[0] /= *ladj;
		m_xqarr[1] *= *ladj;
		m_dxdq[1] *=  *ladj;
		m_zwaist /= (*ladj)*(*ladj);
	}
	else{
		double sigpi = 2.0*SQRTPI*m_srcsize;
		m_xqarr[0] /= sigpi;
		m_dxdq[0] /= sigpi;
		m_xqarr[1] *= sigpi/m_lambda;
		m_dxdq[1] *=  sigpi/m_lambda;
		m_zwaist *= m_lambda/sigpi/sigpi;
	}

	m_fluxspl.SetSpline2D(m_mesh, &m_xqarr[0], &m_xqarr[1], &m_data, false);
	m_norm_factor = m_fluxspl.Integrate();
}

void HGModalDecomp::f_ComputeWholeWigner(double fnorm, int indices[], int ixy, int iq, 
		vector<complex<double>> *aAnm, vector<int> *nindex, vector<int> *mindex, 
		vector<vector<complex<double>>> *ws, vector<double> &data,
		int rank, int mpiprocesses, MPIbyThread *thread)
{
	int mesh[2], nxy, nq, n, m;
	complex<double> Wrrc;

	for(int j = 0; j < 2; j++){
		mesh[j] = (int)m_xqarr[j].size();
	}

	vector<int> steps, inistep, finstep;
	mpi_steps(mesh[0], mesh[1], mpiprocesses, &steps, &inistep, &finstep);

	m_calcstatus->SetSubstepNumber(m_layer, steps[0]);

	for(nxy = 0; nxy < mesh[0]; nxy++){
		indices[ixy] = nxy;
		for(nq = 0; nq < mesh[1]; nq++){
			indices[iq] = nq;

			int nm = nxy*mesh[1]+nq;
			if (nm < inistep[rank] || nm > finstep[rank]){
				continue;
			}

			int iindex = m_wig4d->GetTotalIndex(indices);
			double dbldr = 0;
			data[iindex] = 0.0;
			for(nm = 0; nm < aAnm->size(); nm++){
				n = (*nindex)[nm];
				m = (*mindex)[nm];
				Wrrc = (*ws)[n*(m_maxmodenumber+1)+m][nxy*mesh[1]+nq]*(*aAnm)[nm];
				dbldr += Wrrc.real();
			}
			data[iindex] = (double)(fnorm*dbldr);
			m_calcstatus->AdvanceStep(m_layer);
		}
	}

	if(mpiprocesses > 1){
		for(nxy = 0; nxy < mesh[0]; nxy++){
			indices[ixy] = nxy;
			for(nq = 0; nq < mesh[1]; nq++){
				indices[iq] = nq;
				int iindex = m_wig4d->GetTotalIndex(indices);
				int nm = nxy*mesh[1]+nq;
				int currrank;
				for(currrank = 0; currrank < mpiprocesses; currrank++){
					if(nm >= inistep[currrank] && nm <= finstep[currrank]){
						break;
					}
				}
				if(thread != nullptr){
					thread->Bcast(&data[iindex], 1, MPI_DOUBLE, currrank, rank);
				}
				else{
					MPI_Bcast(&data[iindex], 1, MPI_DOUBLE, currrank, MPI_COMM_WORLD);
				}
			}
		}
	}
}

void HGModalDecomp::f_ExportFieldBinary(const char *buffer, 
			vector<double> *xyarr, vector<vector<complex<double>>> *Ea)
{
	int nmesh[2];
	double dxy, *datar, *datai;

	nmesh[0] = (int)Ea->size();
	nmesh[1] = (int)xyarr->size();
	dxy = (xyarr->back()-xyarr->front())/(double)(nmesh[1]-1);

	FILE *fp = fopen(buffer, "wb");

	fwrite(nmesh, sizeof(int), 2, fp);
	fwrite(&dxy, sizeof(double), 1, fp);

	datar = new double[nmesh[1]];
	datai = new double[nmesh[1]];

	for(int p = 0; p < nmesh[0]; p++){
		for(int nx = 0; nx < nmesh[1]; nx++){
			datar[nx] = (*Ea)[p][nx].real();
			datai[nx] = (*Ea)[p][nx].imag();
		}
		fwrite(datar, sizeof(double), nmesh[1], fp);
		fwrite(datai, sizeof(double), nmesh[1], fp);
	}
	fclose(fp);

	delete[] datar;
	delete[] datai;
}

void HGModalDecomp::f_AssignWignerArray(
	vector<vector<complex<double>>> *ws, vector<double> *xyarr, vector<double> *qarr)
{
	int mesh[2], n, m, nxy, nq;

	mesh[0] = (int)xyarr->size();
	mesh[1] = (int)qarr->size();

	int nmodes = (m_maxmodenumber+1)*(m_maxmodenumber+1);
	ws->resize(nmodes);
	for(int n = 0; n < nmodes; n++){
		(*ws)[n].resize(mesh[0]*mesh[1]);
	}

	m_calcstatus->SetSubstepNumber(m_layer, mesh[0]);
	vector<double> W(2*(m_maxmodenumber+1)*(m_maxmodenumber+1));
	for(nxy = 0; nxy < mesh[0]; nxy++){
		for(nq = 0; nq < mesh[1]; nq++){
			m_hgmode->GetWignerFunctions(m_maxmodenumber, (*xyarr)[nxy], (*qarr)[nq], W);
			for(n = 0; n <= m_maxmodenumber; n++){
				for(m = 0; m <= m_maxmodenumber; m++){
					int nm = n*(m_maxmodenumber+1)+m;
					(*ws)[n*(m_maxmodenumber+1)+m][nxy*mesh[1]+nq] = complex<double>(W[2*nm], W[2*nm+1]);
				}
			}
		}
		m_calcstatus->AdvanceStep(m_layer);
	}
}

//-----------
HGModalDecomp2D::HGModalDecomp2D(PrintCalculationStatus *calcstatus, 
	int acclevel, int maxmodes[], int cmdmode, double cutoff, double fluxcut, Wigner4DManipulator *wig4d)
{
	m_calcstatus = calcstatus;
	m_acclevel = acclevel;
	for(int j = 0; j < 2; j++){
		m_hgmode[j] = nullptr;
		m_maxmode[j] = maxmodes[j];
	}
	m_hgmode[2] = nullptr;
	m_max_cmdmode = cmdmode;
	m_wig4d = wig4d;
	m_lambda = m_wig4d->GetWavelength();
	m_cutoff = cutoff;
	m_fluxcut = fluxcut;

	for(int j = 0; j < 2; j++){
		m_hgmode[j] = new HGModalDecomp(2, m_calcstatus, m_acclevel, m_maxmode[j], cutoff, fluxcut, wig4d);
	}
}

HGModalDecomp2D::~HGModalDecomp2D()
{
	for(int j = 0; j < 3; j++){
		if(m_hgmode[j] != nullptr){
			delete m_hgmode[j];
		}
	}
}

void HGModalDecomp2D::LoadData()
{
	for(int j = 0; j < 2; j++){
		m_wig4d->GetXYQArray(j, m_xyarr[j], m_qarr[j]);
		m_xyarr[j] *= 1.0e-3; // mm -> m
		m_qarr[j] *= 1.0e-3; // mrad -> rad
		m_nmesh[j] = (int)m_xyarr[j].size();
		m_anmesh[j] = (int)m_qarr[j].size();
	}
}

void HGModalDecomp2D::ComputePrjBeamParameters(double *sigma)
{
	vector<vector<double>> dprj;
	vector<vector<double>> xyq(2);
	double *sigmain = nullptr;
	int sublayer = 1;

	for(int j = 0; j < 2; j++){
		m_wig4d->GetSliceValues(j, nullptr, dprj);
		m_wig4d->GetXYQArray(j, xyq[0], xyq[1]);
		m_hgmode[j]->AssingData(&xyq, dprj, true);
		if(sigma != nullptr){
			sigmain = &sigma[j];
		}
		m_hgmode[j]->OptimizeSrcSize(sigmain, &sublayer);
		m_srcsize[j] = m_hgmode[j]->GetSigma();
		m_maxmode[j] = m_hgmode[j]->GetMaxOrder(m_maxmode[j]);
		dprj.clear();
		if(sigma == nullptr){
			m_calcstatus->AdvanceStep(0);
		}
	}
}

void HGModalDecomp2D::SetLGContainer(int rank, int mpiprocesses, MPIbyThread *thread)
{
	double lgeps = 1e-6;
	int maxmode = max(m_maxmode[0], m_maxmode[1]);
	m_lgcont.Create(maxmode, lgeps, rank, mpiprocesses, thread, m_calcstatus);
	for(int j = 0; j < 2; j++){
		m_hgmode[j]->SetLGContainer(&m_lgcont);
	}
	m_calcstatus->AdvanceStep(0);
}

void HGModalDecomp2D::GetAnmAt(int jxy, int posidx[], vector<vector<complex<double>>> *Anm)
{
	vector<vector<double>> dprj;

	m_wig4d->GetSliceValues(jxy, posidx, dprj);
	m_hgmode[jxy]->AssingData(nullptr, dprj, false);
	m_hgmode[jxy]->FourierExpansion();
	m_hgmode[jxy]->GetAnm(Anm);
}

void HGModalDecomp2D::GetAnmAll(int jxy, int rank, int mpiprocesses, MPIbyThread *thread)
{
	MPI_Status mpistatus;

	int posidx[2];
	int kxy = 1-jxy;

	vector<vector<complex<double>>> Anm;
	vector<vector<vector<double>>> mnRe, mnIm;

	int nmodes[2], totalmodes;
	nmodes[0] = m_maxmode[jxy]+1; 
	nmodes[1] = m_maxmode[kxy]+1; 
	totalmodes = nmodes[0]*nmodes[0];
	mnRe.resize(totalmodes);
	mnIm.resize(totalmodes);
	for(int n = 0; n < totalmodes; n++){
		mnRe[n].resize(m_nmesh[kxy]);
		mnIm[n].resize(m_nmesh[kxy]);
		for(posidx[0] = 0; posidx[0] < m_nmesh[kxy]; posidx[0]++){
			mnRe[n][posidx[0]].resize(m_anmesh[kxy]);
			mnIm[n][posidx[0]].resize(m_anmesh[kxy]);
		}
	}

	m_normfactor = m_hgmode[jxy]->GetNormalization();

	double *anmtmp = nullptr;
	if(mpiprocesses > 1){
		anmtmp = new double[m_nmesh[kxy]*m_anmesh[kxy]*totalmodes*2];
	}

	vector<int> steps, inistep, finstep;
	mpi_steps(m_nmesh[kxy], m_anmesh[kxy], mpiprocesses, &steps, &inistep, &finstep);

	m_calcstatus->SetSubstepNumber(1, steps[0]);

#ifdef _HGTIME
	m_hgmode[0]->MeasureTime("");
#endif

	for(posidx[0] = 0; posidx[0] < m_nmesh[kxy]; posidx[0]++){
		for(posidx[1] = 0; posidx[1] < m_anmesh[kxy]; posidx[1]++){
			int totpos = posidx[0]*m_anmesh[kxy]+posidx[1];
			if(totpos < inistep[rank] || totpos > finstep[rank]){
				continue;
			}
			GetAnmAt(jxy, posidx, &Anm);
			for(int n = 0; n < nmodes[0]; n++){
				for(int m = 0; m < nmodes[0]; m++){
					mnRe[n*nmodes[0]+m][posidx[0]][posidx[1]] = Anm[n][m].real();
					mnIm[n*nmodes[0]+m][posidx[0]][posidx[1]] = Anm[n][m].imag();
					if(mpiprocesses > 1){
						int ntlt = (posidx[0]*m_anmesh[kxy]+posidx[1])*totalmodes;
						ntlt += n*nmodes[0]+m;
						anmtmp[ntlt*2] = Anm[n][m].real();
						anmtmp[ntlt*2+1] = Anm[n][m].imag();
					}
				}
			}
			m_calcstatus->AdvanceStep(1);
		}
	}

	if(mpiprocesses > 1){
		for(int k = 1; k < mpiprocesses; k++){
			if(thread != nullptr){
				thread->SendRecv(anmtmp+inistep[k]*totalmodes*2, steps[k]*totalmodes*2, MPI_DOUBLE, k, 0, rank);
			}
			else{
				if(rank == 0){
					MPI_Recv(anmtmp+inistep[k]*totalmodes*2, steps[k]*totalmodes*2, MPI_DOUBLE, k, 0, MPI_COMM_WORLD, &mpistatus);
				}
				else if(rank == k){
					MPI_Send(anmtmp+inistep[k]*totalmodes*2, steps[k]*totalmodes*2, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
				}
				MPI_Barrier(MPI_COMM_WORLD);
			}
		}
		if(thread != nullptr){
			thread->Bcast(anmtmp, m_nmesh[kxy]*m_anmesh[kxy]*totalmodes*2, MPI_DOUBLE, 0, rank);
		}
		else{
			MPI_Bcast(anmtmp, m_nmesh[kxy]*m_anmesh[kxy]*totalmodes*2, MPI_DOUBLE, 0, MPI_COMM_WORLD);
		}
		for(posidx[0] = 0; posidx[0] < m_nmesh[kxy]; posidx[0]++){
			for(posidx[1] = 0; posidx[1] < m_anmesh[kxy]; posidx[1]++){
				for(int n = 0; n < nmodes[0]; n++){
					for(int m = 0; m < nmodes[0]; m++){
						int ntlt = (posidx[0]*m_anmesh[kxy]+posidx[1])*totalmodes;
						ntlt += n*nmodes[0]+m;
						mnRe[n*nmodes[0]+m][posidx[0]][posidx[1]] = anmtmp[ntlt*2];
						mnIm[n*nmodes[0]+m][posidx[0]][posidx[1]] = anmtmp[ntlt*2+1];
					}
				}
			}
		}
		delete[] anmtmp;
	}

#ifdef _HGTIME
	m_hgmode[0]->MeasureTime("GetAnmAll::Anm(y,y')");
#endif

	m_calcstatus->AdvanceStep(0);

	totalmodes = nmodes[1]*nmodes[1];
	if(mpiprocesses > 1){
		anmtmp = new double[nmodes[0]*nmodes[0]*totalmodes*2];
	}

#ifdef _DEBUG
	if(rank == 0 && !CMD_Anm_Func_1st.empty()){
		vector<int> modecheck {0, 5, 10};
		ofstream debug_out(CMD_Anm_Func_1st);
		vector<string> items(2);
		items[0] = "xy";
		items[1] = "q";
		for (int n = 0; n < modecheck.size(); n++){
			for (int m = 0; m < modecheck.size(); m++){
				if (modecheck[n] > m_maxmode[0] || modecheck[m] > m_maxmode[1]){
					continue;
				}
				stringstream ss;
				ss << "N" <<modecheck[n] << modecheck[m];
				items.push_back(ss.str());
			}
		}
		PrintDebugItems(debug_out, items);

		vector<double> xy, q, values(items.size());
		m_wig4d->GetXYQArray(kxy, xy, q);
		for (posidx[0] = 0; posidx[0] < m_nmesh[kxy]; posidx[0]++){
			for (posidx[1] = 0; posidx[1] < m_anmesh[kxy]; posidx[1]++){
				values[0] = xy[posidx[0]];
				values[1] = q[posidx[1]];
				int nm = 1;
				for (int n = 0; n < modecheck.size(); n++){
					for (int m = 0; m < modecheck.size(); m++){
						if (modecheck[n] > m_maxmode[0] || modecheck[m] > m_maxmode[1]){
							continue;
						}
						values[++nm] = mnRe[modecheck[n]*nmodes[0]+modecheck[m]][posidx[0]][posidx[1]];
					}
				}
				PrintDebugItems(debug_out, values);
			}
		}
		debug_out.close();
	}
#endif

	m_Anm.resize(nmodes[0]*nmodes[1]);
	for(int nm = 0; nm < nmodes[0]*nmodes[1]; nm++){
		m_Anm[nm].resize(nmodes[0]*nmodes[1]);
	}

	vector<vector<complex<double>>> AnmRe, AnmIm;
	int nnk, mmk;

	mpi_steps(nmodes[0], nmodes[0], mpiprocesses, &steps, &inistep, &finstep);

	m_calcstatus->SetSubstepNumber(1, steps[0]);

	double Asum = 0;
	m_hgmode[kxy]->SetNormalization(1.0);
	for(int n = 0; n < nmodes[0]; n++){
		for(int m = 0; m < nmodes[0]; m++){
			int nm = n*nmodes[0]+m;
			if(nm < inistep[rank] || nm > finstep[rank]){
				continue;
			}

			m_hgmode[kxy]->AssingData(nullptr, mnRe[n*nmodes[0]+m], false);
			m_hgmode[kxy]->FourierExpansion();
			m_hgmode[kxy]->GetAnm(&AnmRe);

			m_hgmode[kxy]->AssingData(nullptr, mnIm[n*nmodes[0]+m], false);
			m_hgmode[kxy]->FourierExpansion();
			m_hgmode[kxy]->GetAnm(&AnmIm);

			for(int nk = 0; nk < nmodes[1]; nk++){
				for(int mk = 0; mk < nmodes[1]; mk++){
					if(jxy == 0){
						nnk = n*nmodes[1]+nk;
						mmk = m*nmodes[1]+mk;
					}
					else{
						nnk = nk*nmodes[0]+n;
						mmk = mk*nmodes[0]+m;
					}
					m_Anm[nnk][mmk] = (AnmRe[nk][mk]+complex<double>(0.0, 1.0)*AnmIm[nk][mk]);
					if(mpiprocesses > 1){
						int ntlt = (n*nmodes[0]+m)*totalmodes;
						ntlt += nk*nmodes[1]+mk;
						anmtmp[ntlt*2] = m_Anm[nnk][mmk].real();
						anmtmp[ntlt*2+1] = m_Anm[nnk][mmk].imag();
					}
					if(nnk == mmk){
						Asum += m_Anm[nnk][mmk].real();
					}
				}
			}
			m_calcstatus->AdvanceStep(1);
		}
	}

	if(mpiprocesses > 1){
		if(thread != nullptr){
			for(int k = 1; k < mpiprocesses; k++){
				thread->SendRecv(anmtmp+inistep[k]*totalmodes*2, steps[k]*totalmodes*2, MPI_DOUBLE, k, 0, rank);
			}
		}
		else{
			for(int k = 1; k < mpiprocesses; k++){
				if(rank == 0){
					MPI_Recv(anmtmp+inistep[k]*totalmodes*2, steps[k]*totalmodes*2, MPI_DOUBLE, k, 0, MPI_COMM_WORLD, &mpistatus);
				}
				else if(rank == k){
					MPI_Send(anmtmp+inistep[k]*totalmodes*2, steps[k]*totalmodes*2, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
				}
				MPI_Barrier(MPI_COMM_WORLD);
			}
		}
		if(thread != nullptr){
			thread->Bcast(anmtmp, nmodes[0]*nmodes[0]*totalmodes*2, MPI_DOUBLE, 0, rank);
		}
		else{
			MPI_Bcast(anmtmp, nmodes[0]*nmodes[0]*totalmodes*2, MPI_DOUBLE, 0, MPI_COMM_WORLD);
		}
		for(int n = 0; n < nmodes[0]; n++){
			for(int m = 0; m < nmodes[0]; m++){
				for(int nk = 0; nk < nmodes[1]; nk++){
					for(int mk = 0; mk < nmodes[1]; mk++){
						if(jxy == 0){
							nnk = n*nmodes[1]+nk;
							mmk = m*nmodes[1]+mk;
						}
						else{
							nnk = nk*nmodes[0]+n;
							mmk = mk*nmodes[0]+m;
						}
						int ntlt = (n*nmodes[0]+m)*totalmodes;
						ntlt += nk*nmodes[1]+mk;
						m_Anm[nnk][mmk] = complex<double>(anmtmp[ntlt*2], anmtmp[ntlt*2+1]);
					}	
				}
			}
		}
		delete[] anmtmp;
	}

#ifdef _HGTIME
	m_hgmode[0]->MeasureTime("GetAnmAll::MatrixAnm");
#endif

	m_calcstatus->AdvanceStep(0);

#ifdef _DEBUG
	if(rank == 0 && !CMD_Anm_Func_2nd.empty()){
		ofstream debug_out(CMD_Anm_Func_2nd);
		vector<double> values(4);

		vector<string> items(4);
		items[0] = "n";
		items[1] = "m";
		items[2] = "Real";
		items[3] = "Imag";
		PrintDebugItems(debug_out, items);

		for (int n = 0; n < nmodes[0]*nmodes[1]; n++){
			for (int m = 0; m < nmodes[0]*nmodes[1]; m++){
				values[0] = n;
				values[1] = m;
				values[2] = m_Anm[n][m].real();
				values[3] = m_Anm[n][m].imag();
				PrintDebugItems(debug_out, values);
			}
		}
	}
#endif

	m_hgmode[2] = new HGModalDecomp(1, m_calcstatus, m_acclevel, nmodes[0]*nmodes[1]-1, m_cutoff, m_fluxcut, m_wig4d);
	m_hgmode[2]->SetAnm(&m_Anm);

	if(rank == 0){
		m_experr = m_hgmode[2]->CholeskyDecomp(&m_anm, &m_ordered_mode);
	}	
	if(mpiprocesses > 1){
		if(thread != nullptr){
			thread->Bcast(&m_experr, 1, MPI_DOUBLE, 0, rank);
		}
		else{
			MPI_Bcast(&m_experr, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);
		}
		int modes = nmodes[0]*nmodes[1];
		int *idx = new int[modes];
		double *ws = new double[modes*modes*2];
		if(rank == 0){
			for(int n = 0; n < modes; n++){
				idx[n] = m_ordered_mode[n];
				for(int m = 0; m < modes; m++){
					ws[2*(n*modes+m)] = m_anm[n][m].real();
					ws[2*(n*modes+m)+1] = m_anm[n][m].imag();
				}
			}
		}
		if(thread != nullptr){
			thread->Bcast(idx, modes, MPI_INT, 0, rank);
			thread->Bcast(ws, modes *modes*2, MPI_DOUBLE, 0, rank);
		}
		else{
			MPI_Bcast(idx, modes, MPI_INT, 0, MPI_COMM_WORLD);
			MPI_Bcast(ws, modes *modes*2, MPI_DOUBLE, 0, MPI_COMM_WORLD);
		}
		if(rank > 0){
			m_ordered_mode.resize(modes);
			m_anm.resize(modes);
			for(int n = 0; n < modes; n++){
				m_anm[n].resize(modes);
				m_ordered_mode[n] = idx[n];
				for(int m = 0; m < modes; m++){
					m_anm[n][m] = complex<double> {ws[2*(n*modes+m)], ws[2*(n*modes+m)+1]};
				}
			}
		}
		delete[] idx;
		delete[] ws;
	}
	if(rank > 0){
		m_hgmode[2]->Set_anm(m_anm);
	}

#ifdef _HGTIME
	m_hgmode[0]->MeasureTime("GetAnmAll::Cholesky");
#endif

	m_calcstatus->AdvanceStep(0);
}

void HGModalDecomp2D::GetComplexAmp2D(vector<vector<double>> &xyarr,
		vector<vector<vector<complex<double>>>> *Ea, double eps, int pmax,
		int rank, int mpiprocesses, MPIbyThread *thread, bool skipstep)
{
	int nxy[2], mode[2], nmodes[2], mesh[2], totalmodes;
	vector<vector<complex<double>>> Exyarr[2];
	complex<double> Exy[2];

	for(int j = 0; j < 2; j++){
		mesh[j] = (int)xyarr[j].size();
	}
	for(int j = 0; j < 2; j++){
		m_hgmode[j]->GetComplexAmp(xyarr[j], &Exyarr[j], 0.0, -1, true, true);
		nmodes[j] = m_maxmode[j]+1;
	}
	totalmodes = nmodes[0]*nmodes[1];

	pmax = m_hgmode[2]->GetMaxOrder(pmax);
	if(pmax < 0){
		pmax = totalmodes-1;
	}
	else{
		pmax = min(totalmodes-1, pmax);
	}

	Ea->resize(pmax+1);
	for(int p = 0; p <= pmax; p++){
		(*Ea)[p].resize(mesh[0]);
		for(nxy[0] = 0; nxy[0] < mesh[0]; nxy[0]++){
			(*Ea)[p][nxy[0]].resize(mesh[1]);
		}
	}

	vector<int> steps, inistep, finstep;
	mpi_steps(mesh[0], mesh[1], mpiprocesses, &steps, &inistep, &finstep);
	if(!skipstep){
		m_calcstatus->SetSubstepNumber(1, steps[0]);
	}

	int q;
	for(nxy[0] = 0; nxy[0] < mesh[0]; nxy[0]++){
		for(nxy[1] = 0; nxy[1] < mesh[1]; nxy[1]++){
			int nm = nxy[1]*mesh[0]+nxy[0];
			if(nm < inistep[rank] || nm > finstep[rank]){
				continue;
			}
			for(int p = 0; p <= pmax; p++){
				(*Ea)[p][nxy[0]][nxy[1]] = complex<double>(0.0, 0.0);
				for(int qr = 0; qr < totalmodes; qr++){
					q = GetOrderedModeNumber(qr);
					mode[0] = q/nmodes[1];
					mode[1] = q%nmodes[1];
					for(int j = 0; j < 2; j++){
						Exy[j] = Exyarr[j][mode[j]][nxy[j]];
					}
					if(abs(m_anm[qr][p]) > eps){
						(*Ea)[p][nxy[0]][nxy[1]] += m_anm[qr][p]*Exy[0]*Exy[1];
					}
				}
			}
			if (!skipstep){
				m_calcstatus->AdvanceStep(1);
			}
		}
	}

	if(mpiprocesses > 1){
		double *ws = new double[2*(pmax+1)];
		for (nxy[0] = 0; nxy[0] < mesh[0]; nxy[0]++){
			for (nxy[1] = 0; nxy[1] < mesh[1]; nxy[1]++){
				int nm = nxy[1]*mesh[0]+nxy[0];
				int currrank;
				for(currrank = 0; currrank < mpiprocesses; currrank++){
					if(nm >= inistep[currrank] && nm <= finstep[currrank]){
						break;
					}
				}
				if(currrank == rank){
					for (int p = 0; p <= pmax; p++){
						ws[2*p] = (*Ea)[p][nxy[0]][nxy[1]].real();
						ws[2*p+1] = (*Ea)[p][nxy[0]][nxy[1]].imag();
					}
				}
				if(thread != nullptr){
					thread->Bcast(ws, 2*(pmax+1), MPI_DOUBLE, currrank, rank);
				}
				else{
					MPI_Bcast(ws, 2*(pmax+1), MPI_DOUBLE, currrank, MPI_COMM_WORLD);
				}
				if(currrank != rank){
					for (int p = 0; p <= pmax; p++){
						(*Ea)[p][nxy[0]][nxy[1]] = complex<double>(ws[2*p], ws[2*p+1]);
					}
				}
			}
		}
		delete[] ws;
	}
}

void HGModalDecomp2D::DumpTotalIntensityProfile(double eps, int pmax, 
	vector<vector<double>> &xyarr, vector<vector<double>> &data, 
	int rank, int mpiprocess, MPIbyThread *thread)
{
	vector<vector<vector<complex<double>>>> Ea;
	vector<double> dummy;
	int mesh[2];

	xyarr.resize(2);
	for(int j = 0; j < 2; j++){
		m_wig4d->GetXYQArray(j, xyarr[j], dummy);
		mesh[j] = (int)xyarr[j].size();
	}
	vector<vector<double>> xyarrm(xyarr);
	for(int j = 0; j < 2; j++){
		xyarrm[j] *= 1e-3; // mm -> m
	}

	pmax = m_hgmode[2]->GetMaxOrder(pmax);
	GetComplexAmp2D(xyarrm, &Ea, eps, pmax, rank, mpiprocess, thread);

	double coef = GetNormalizeFactor()*1e6*m_lambda*m_lambda;
	data.resize(2);
	for(int j = 0; j < 2; j++){
		data[j].resize(mesh[0]*mesh[1], 0.0);
	}
	for(int p = 0; p <= pmax; p++){
		for(int n = 0; n < mesh[0]; n++){
			for(int m = 0; m < mesh[1]; m++){
				int nm = m*mesh[0]+n;
				data[1][nm] += coef*hypotsq(Ea[p][n][m].real(), Ea[p][n][m].imag());
			}
		}
	}
	m_wig4d->GetProjection(data[0]);
}

void HGModalDecomp2D::DumpIntensityProfile(double eps, int pmax,
	vector<vector<double>> &xyarr, vector<vector<vector<double>>> &data,
	int rank, int mpiprocess, MPIbyThread *thread)
{
	vector<vector<vector<complex<double>>>> Ea;

	int mesh[2];
	for(int j = 0; j < 2; j++){
		mesh[j] = (int)xyarr[j].size();
	}

	double coef = GetNormalizeFactor()*1e6*m_lambda*m_lambda;
	pmax = m_hgmode[2]->GetMaxOrder(pmax);
	GetComplexAmp2D(xyarr, &Ea, eps, pmax, rank, mpiprocess, thread);
	data.resize(pmax+1);
	for(int p = 0; p <= pmax; p++){
		data[p].resize(1);
		data[p][0].resize(mesh[0]*mesh[1], 0.0);
	}
	for(int p = 0; p <= pmax; p++){
		for(int n = 0; n < mesh[0]; n++){
			for(int m = 0; m < mesh[1]; m++){
				int nm = m*mesh[0]+n;
				data[p][0][nm] = coef*hypotsq(Ea[p][n][m].real(), Ea[p][n][m].imag());
			}
		}
	}
#ifdef _HGTIME
	m_hgmode[0]->MeasureTime("Intensity Profile");
#endif
}

void HGModalDecomp2D::DumpFieldProfile(const char *bufbin, double eps, int pmax, bool iswrite,
	vector<vector<double>> &xyarr, vector<vector<double>> &datar, vector<vector<double>> &datai,
	int rank, int mpiprocess, MPIbyThread *thread)
{
	vector<vector<vector<complex<double>>>> Ea;

	int mesh[2];
	for(int j = 0; j < 2; j++){
		mesh[j] = (int)xyarr[j].size();
	}

	pmax = m_hgmode[2]->GetMaxOrder(pmax);
	GetComplexAmp2D(xyarr, &Ea, eps, pmax, rank, mpiprocess, thread);
	if(bufbin != nullptr){
		f_ExportFieldBinary(bufbin, &xyarr, &Ea);
	}

	if(iswrite){
		datar.resize(pmax+1);
		datai.resize(pmax+1);
		for(int p = 0; p <= pmax; p++){
			datar[p].resize(mesh[0]*mesh[1]);
			datai[p].resize(mesh[0]*mesh[1]);
			for(int n = 0; n < mesh[0]; n++){
				for (int m = 0; m < mesh[1]; m++){
					int nm = m*mesh[0]+n;
					datar[p][nm] = Ea[p][n][m].real();
					datai[p][nm] = Ea[p][n][m].imag();
				}
			}
		}
	}

#ifdef _HGTIME
	m_hgmode[0]->MeasureTime("Field Profile");
#endif
}

double HGModalDecomp2D::GetNormalizeFactor()
{
	return m_normfactor/(m_srcsize[0]*m_srcsize[1]*PI*4.0);
}

void HGModalDecomp2D::GetFluxConsistency(int pmax, double eps, vector<double> &fr, vector<double> &fa)
{
	m_hgmode[2]->GetFluxConsistency(pmax, eps, fr, fa);
}

void HGModalDecomp2D::ReconstructExport(int pmax, double epsanm, 
		double *CMDerr, vector<vector<vector<double>>> &data, 
		int rank, int mpiprocesses, MPIbyThread *thread)
{
	vector<double> stderror[NumberWigError];
	double errors[NumberWigError];
	int nxy[2], nq[2];
	double xy[2], q[2], degcoh;
	double fnorm = GetNormalizeFactor();

	int n, m;

	for(int j = 0; j < 2; j++){
		int nrmodes = (m_maxmode[j]+1)*(m_maxmode[j]+1);
		m_ws[j].resize(nrmodes);
		for(int n = 0; n < nrmodes; n++){
			m_ws[j][n].resize(m_nmesh[j]*m_anmesh[j]);
		}
	}

	m_calcstatus->SetSubstepNumber(1, m_nmesh[0]+m_nmesh[1]);
	int maxmode = max(m_maxmode[0], m_maxmode[1]);
	vector<double> W(2*(maxmode+1)*(maxmode+1));
	for(int j = 0; j < 2; j++){
		for(nxy[j] = 0; nxy[j] < m_nmesh[j]; nxy[j]++){
			xy[j] = m_xyarr[j][nxy[j]];
			for(nq[j] = 0; nq[j] < m_anmesh[j]; nq[j]++){
				q[j] = m_qarr[j][nq[j]];
				m_hgmode[j]->GetHGMode()->GetWignerFunctions(m_maxmode[j], xy[j], q[j], W);
				for(n = 0; n <= m_maxmode[j]; n++){
					for(m = 0; m <= m_maxmode[j]; m++){
						int nm = n*(m_maxmode[j]+1)+m;
						m_ws[j][m+n*(m_maxmode[j]+1)][nxy[j]*m_anmesh[j]+nq[j]]
							= complex<double>(W[2*nm], W[2*nm+1]);
					}
				}
			}
			m_calcstatus->AdvanceStep(1);
		}
	}
	m_calcstatus->AdvanceStep(0);

	m_hgmode[2]->GetApproximatedAnm(pmax, epsanm, &m_Anm_approx, &m_nindex, &m_mindex);
	m_calcstatus->AdvanceStep(0);

	int tmesh = m_nmesh[0]*m_nmesh[1]*m_anmesh[0]*m_anmesh[1];
	vector<double> wigdata(tmesh);
	f_ComputeWholeWigner(fnorm, wigdata, rank, mpiprocesses, thread);

#ifdef _DEBUG
	if(!CMD_Chk_Comp.empty()){

		vector<int> steps, inistep, finstep;
		mpi_steps(m_nmesh[0], m_nmesh[1], mpiprocesses, &steps, &inistep, &finstep);
		m_calcstatus->SetSubstepNumber(0, steps[0]);
		m_calcstatus->ResetCurrentStep(0);
		m_calcstatus->ResetTotal();

		int hqmesh[2];
		double dq[2];
		for(int j = 0; j < 2; j++){
			hqmesh[j] = (m_anmesh[j]-1)/2;
			dq[j] = m_qarr[j][1]-m_qarr[j][0];
		}
		vector<double> wigdatar(tmesh, 0.0);
		vector<double> W;
		int indices[NumberWignerUVPrm];

		for(nxy[1] = 0; nxy[1] < m_nmesh[1]; nxy[1]++){
			indices[WignerUVPrmV] = nxy[1];
			xy[1] = m_xyarr[1][nxy[1]];
			for(nxy[0] = 0; nxy[0] < m_nmesh[0]; nxy[0]++){
				int nm = nxy[1]*m_nmesh[0]+nxy[0];
				if (nm < inistep[rank] || nm > finstep[rank]){
					continue;
				}
				indices[WignerUVPrmU] = nxy[0];
				xy[0] = m_xyarr[0][nxy[0]];
				GetWignerAt(pmax, epsanm, xy, dq, hqmesh, W);
				for(nq[1] = 0; nq[1] < m_anmesh[1]; nq[1]++){
					indices[WignerUVPrmv] = nq[1];
					for (nq[0] = 0; nq[0] < m_anmesh[0]; nq[0]++){
						indices[WignerUVPrmu] = nq[0];
						int iindex = m_wig4d->GetTotalIndex(indices);
						int idq = nq[1]*m_anmesh[0]+nq[0];
						wigdatar[iindex] = fnorm*W[idq];
					}
				}
				m_calcstatus->AdvanceStep(0);
			}
		}

		if(mpiprocesses > 1){
			double *ws = new double[m_anmesh[0]*m_anmesh[1]];
			for (nxy[1] = 0; nxy[1] < m_nmesh[1]; nxy[1]++){
				indices[WignerUVPrmV] = nxy[1];
				for (nxy[0] = 0; nxy[0] < m_nmesh[0]; nxy[0]++){
					indices[WignerUVPrmU] = nxy[0];
					int nm = nxy[1]*m_nmesh[0]+nxy[0];
					int currrank;
					for (currrank = 0; currrank < mpiprocesses; currrank++){
						if (nm >= inistep[currrank] && nm <= finstep[currrank]){
							break;
						}
					}
					if (currrank == rank){
						for (nq[1] = 0; nq[1] < m_anmesh[1]; nq[1]++){
							indices[WignerUVPrmv] = nq[1];
							for (nq[0] = 0; nq[0] < m_anmesh[0]; nq[0]++){
								indices[WignerUVPrmu] = nq[0];
								int iindex = m_wig4d->GetTotalIndex(indices);
								ws[nq[1]*m_anmesh[0]+nq[0]] = wigdatar[iindex];
							}
						}
					}
					if(thread != nullptr){
						thread->Bcast(ws, m_anmesh[0]*m_anmesh[1], MPI_DOUBLE, currrank, rank);
					}
					else{
						MPI_Bcast(ws, m_anmesh[0]*m_anmesh[1], MPI_DOUBLE, currrank, MPI_COMM_WORLD);
					}
					if (currrank != rank){
						for (nq[1] = 0; nq[1] < m_anmesh[1]; nq[1]++){
							indices[WignerUVPrmv] = nq[1];
							for (nq[0] = 0; nq[0] < m_anmesh[0]; nq[0]++){
								indices[WignerUVPrmu] = nq[0];
								int iindex = m_wig4d->GetTotalIndex(indices);
								wigdatar[iindex] = ws[nq[1]*m_anmesh[0]+nq[0]];
							}
						}
					}
				}
			}
			delete[] ws;
		}

		if(rank == 0){
			vector<double> items(7);
			ofstream debug_out(CMD_Chk_Comp);
			double wmax = minmax(wigdata, true);

			int nqx = (m_anmesh[0]-1)/2;
			int nx = (m_nmesh[0]-1)/2;

			for (nq[1] = 0; nq[1] < m_anmesh[1]; nq[1]++){
				indices[WignerUVPrmv] = nq[1];
				items[3] = m_qarr[1][nq[1]];
				for (nq[0] = 0; nq[0] < m_anmesh[0]; nq[0]++){
					indices[WignerUVPrmu] = nq[0];
					items[2] = m_qarr[0][nq[0]];
					for (nxy[1] = 0; nxy[1] < m_nmesh[1]; nxy[1]++){
						items[1] = m_xyarr[1][nxy[1]];
						indices[WignerUVPrmV] = nxy[1];
						for (nxy[0] = 0; nxy[0] < m_nmesh[0]; nxy[0]++){
							items[0] = m_xyarr[0][nxy[0]];
							indices[WignerUVPrmU] = nxy[0];
							int iindex = m_wig4d->GetTotalIndex(indices);
							items[4] = wigdata[iindex];
							items[5] = wigdatar[iindex];
							items[6] = (items[5]-items[4])/wmax;
							PrintDebugItems(debug_out, items);
						}
					}
				}
			}
			debug_out.close();
		}

	}
#endif

	data.resize(2);
	Wigner4DManipulator wigmanip;
	vector<vector<double>> varxy {m_xyarr[0], m_xyarr[1], m_qarr[0], m_qarr[1]};
	for(int j = 0; j < 4; j++){
		varxy[j] *= 1.0e+3; // m,rad -> mm,mrad
	}
	wigmanip.SetWavelength(m_lambda);
	wigmanip.LoadData(menu::XXpYYp, &varxy, &wigdata);
	
	vector<vector<double>> data2d[2];
	for(int j = 0; j < 2; j++){
		data[j].resize(2);
		for(int i = 0; i < 2; i++){
			data2d[i].clear();
		}
		m_wig4d->GetSliceValues(j, nullptr, data2d[0]);
		wigmanip.GetSliceValues(j, nullptr, data2d[1]);
		for(int i = 0; i < 2; i++){
			data[j][i].resize(m_nmesh[j]*m_anmesh[j]);
			for(int n = 0; n < m_nmesh[j]; n++){
				for (int m = 0; m < m_anmesh[j]; m++){
					data[j][i][m*m_nmesh[j]+n] = data2d[i][n][m];
				}
			}
		}
	}

	m_wig4d->GetCoherenceDeviation(&degcoh, errors, wigdata);
	*CMDerr = errors[WigErrorDeviation];

	m_calcstatus->AdvanceStep(0);	

#ifdef _HGTIME
	m_hgmode[0]->MeasureTime("Reconstruct Wigner");
#endif
}

double HGModalDecomp2D::GetWignerAt(int posxy[], int posxyq[], int nmesh[], int anmesh[])
{
	int n, m, h, k, j, l, nm;
	complex<double> Wr(0.0, 0.0), Wrrc;

	Wr = complex<double>(0.0, 0.0);

	for(nm = 0; nm < m_Anm_approx.size(); nm++){
		n = GetOrderedModeNumber(m_nindex[nm]);
		m = GetOrderedModeNumber(m_mindex[nm]);
		h = n/(m_maxmode[1]+1);
		j = n%(m_maxmode[1]+1);
		k = m/(m_maxmode[1]+1);
		l = m%(m_maxmode[1]+1);
		Wrrc = m_ws[0][h*(m_maxmode[0]+1)+k][posxy[0]*anmesh[0]+posxyq[0]]
			  *m_ws[1][j*(m_maxmode[1]+1)+l][posxy[1]*anmesh[1]+posxyq[1]]
			  *m_Anm_approx[nm];
		Wr = Wr+Wrrc;
	}
	return Wr.real();
}

void HGModalDecomp2D::GetWignerAt(int pmax, double eps,
		double xy[], double dq[], int hqmesh[], vector<double> &W)
{
	int nfft[2], nskip[2], n[2], m[2], index[2], qi[2];
	double dxy[2], sigpi[2], xyr;
	double **ws;
	complex<double> exy;
	vector<vector<double>> xyarr[2];
	vector<vector<vector<complex<double>>>> Ea[2];

	for(int j = 0; j < 2; j++){
		nfft[j] = fft_number(2*hqmesh[j]+1, 1);
		nskip[j] = 1;
		sigpi[j] = 2.0*SQRTPI*m_srcsize[j];
		dxy[j] = 1.0/(nfft[j]*dq[j]/m_lambda);
		while(dxy[j] > m_srcsize[j]/max(2, m_maxmode[j]/4)){
			dxy[j] *= 0.5;
			nfft[j] <<= 1;
		}
		double hgwidth = 2.0*sigpi[j]*GetHLGWidth(m_maxmode[j]);
		while(nfft[j]*dxy[j] < hgwidth){
			nfft[j] <<= 1;
			nskip[j] <<= 1;
		}
	}

	pmax = m_hgmode[2]->GetMaxOrder(pmax);
	for (int i = 0; i < 2; i++){
		xyarr[i].resize(2);
		for (int j = 0; j < 2; j++){
			xyarr[i][j].resize(nfft[j]);
			for(int n = 0; n < nfft[j]; n++){
				xyr = dxy[j]*fft_index(n, nfft[j], 1);
				xyarr[i][j][n] = i == 0 ? xy[j]+xyr*0.5 : xy[j]-xyr*0.5;
			}
		}
		GetComplexAmp2D(xyarr[i], &Ea[i], eps, pmax, 0, 1, nullptr, true);
	}

	ws = new double*[nfft[0]];
	for(n[0] = 0; n[0] < nfft[0]; n[0]++){
		ws[n[0]] = new double[nfft[1]*2];		
	}

	if(W.size() < (2*hqmesh[0]+1)*(2*hqmesh[1]+1)){
		W.resize((2*hqmesh[0]+1)*(2*hqmesh[1]+1));
	}
	fill(W.begin(), W.end(), 0.0);

	FastFourierTransform fft(2, nfft[0], nfft[1]);

	for(int p = 0; p <= pmax; p++){
		for(n[0] = 0; n[0] < nfft[0]; n[0]++){
			for (n[1] = 0; n[1] < nfft[1]; n[1]++){
				exy = Ea[0][p][n[0]][n[1]]*conj(Ea[1][p][n[0]][n[1]]);
				ws[n[0]][2*n[1]] = exy.real();
				ws[n[0]][2*n[1]+1] = exy.imag();
			}
		}

#ifdef _DEBUG
		if (!CMD_Chk_2d_FFT.empty()){
			ofstream debug_out(CMD_Chk_2d_FFT);
			vector<double> items(4);
			for (n[0] = 0; n[0] < nfft[0]; n[0]++){
				items[0] = dxy[0]*n[0];
				for (n[1] = 0; n[1] < nfft[1]; n[1]++){
					items[1] = dxy[1]*n[1];
					items[2] = ws[n[0]][2*n[1]];
					items[3] = ws[n[0]][2*n[1]+1];
					PrintDebugItems(debug_out, items);					
				}
			}
			debug_out.close();
		}
#endif

		fft.DoFFT(ws);
		for(m[1] = -hqmesh[1]; m[1] <= hqmesh[1]; m[1]++){
			index[1] = fft_index(m[1]*nskip[1], nfft[1], -1);
			qi[1] = m[1]+hqmesh[1];
			for (m[0] = -hqmesh[0]; m[0] <= hqmesh[0]; m[0]++){
				index[0] = fft_index(m[0]*nskip[0], nfft[0], -1);
				qi[0] = m[0]+hqmesh[0];
				W[qi[1]*(2*hqmesh[0]+1)+qi[0]] += ws[index[0]][2*index[1]]*dxy[0]*dxy[1];
			}
		}

#ifdef _DEBUG
		if (!CMD_Chk_2d.empty()){
			ofstream debug_out(CMD_Chk_2d);
			vector<double> items(4);
			for (m[1] = -hqmesh[1]; m[1] <= hqmesh[1]; m[1]++){
				items[1] = m[1]*dq[1];
				index[1] = fft_index(m[1], nfft[1], -1);
				for (m[0] = -hqmesh[0]; m[0] <= hqmesh[0]; m[0]++){
					items[0] = m[0]*dq[0];
					index[0] = fft_index(m[0], nfft[0], -1);
					items[2] = ws[index[0]][2*index[1]]*dxy[0]*dxy[1];
					items[3] = ws[index[0]][2*index[1]+1]*dxy[0]*dxy[1];
					PrintDebugItems(debug_out, items);					
				}
			}
			debug_out.close();
		}
#endif
	}

	for(n[0] = 0; n[0] < nfft[0]; n[0]++){
		delete[] ws[n[0]];	
	}
	delete[] ws;
}

int HGModalDecomp2D::GetOrderedModeNumber(int seqno)
{
	if(m_ordered_mode.size() == 0){
		return seqno;
	}
	return m_ordered_mode[seqno];
}

void HGModalDecomp2D::WriteResults(string &result, double cmderr[])
{
	int nmodes = (m_maxmode[0]+1)*(m_maxmode[1]+1);
	vector<double> anm[2];
	vector<int> anmidx[2];
	GetSparseMatrix(nmodes, m_anm, anm, anmidx);

	stringstream ssresult;
	vector<double> srcsize(2);
	vector<int> maxorder(2);
	for(int j = 0; j < 2; j++){
		srcsize[j] = m_srcsize[j];
		maxorder[j] = m_maxmode[j];
	}

	double tflux = m_lambda*1.0e+6; // /mm.mrad -> /m.rad
	tflux *= tflux;
	tflux *= m_normfactor;
	
	ssresult << "{" << endl;

	WriteJSONArray(ssresult, JSONIndent, maxorder, MaxOrderLabel.c_str(), false, true);
	WriteJSONValue(ssresult, JSONIndent, m_lambda, WavelengthLabel.c_str(), false, true);
	WriteJSONValue(ssresult, JSONIndent, tflux, FluxCMDLabel.c_str(), false, true);
	WriteJSONArray(ssresult, JSONIndent, srcsize, SrcSizeLabel.c_str(), false, true);
	WriteJSONArray(ssresult, JSONIndent, m_ordered_mode, OrderLabel.c_str(), false, true);
	WriteCommonJSON(ssresult, cmderr, m_normfactor, anm, anmidx);

	result = ssresult.str();
}

void HGModalDecomp2D::WriteCPUTime(string &result)
{
	stringstream ssresult;
	vector<double> elapsed[2];
	vector<string> cpucont[2];
	for(int j = 0; j < 2; j++){
		m_hgmode[2*j]->GetCPUTime(&elapsed[j], &cpucont[j]);
	}
	int ifin = elapsed[1].size() > 0 ? 2 : 1;
	ssresult << "{" << endl;
	for(int i = 0; i < ifin; i++){
		for(int j = 0; j < elapsed[i].size(); j++){
			bool isend = i == ifin-1 && j == elapsed[i].size()-1;
			WriteJSONValue(ssresult, JSONIndent, elapsed[i][j], cpucont[i][j].c_str(), false, !isend);
		}
	}
	ssresult << endl << "}";
	result = ssresult.str();
}

void HGModalDecomp2D::LoadResults(int maxorder[], double srcsize[], 
	double fnorm, vector<int> &order, vector<double> &anmre, vector<double> &anmim)
{
	for(int j = 0; j < 2; j++){
		m_srcsize[j] = srcsize[j];
		m_maxmode[j] = maxorder[j];
	}
	m_ordered_mode = order;
	int nmodes = (m_maxmode[0]+1)*(m_maxmode[1]+1);
	m_anm.resize(nmodes);
	for(int n = 0; n < nmodes; n++){
		m_anm[n].resize(nmodes);
		for(int m = 0; m < nmodes; m++){
			int nm = n*nmodes+m;
			m_anm[n][m] = complex<double>(anmre[nm], anmim[nm]);
		}
	}
	m_normfactor = fnorm;
	for(int j = 0; j < 2; j++){
		m_hgmode[j]->SetSigma(srcsize[j]);
		m_hgmode[j]->SetMaximumModeNumber(m_maxmode[j]);
		m_hgmode[j]->CreateHGMode();
	}
	m_hgmode[2] = new HGModalDecomp(1, m_calcstatus, m_acclevel, nmodes-1, m_cutoff, m_fluxcut, m_wig4d);
	m_hgmode[2]->Set_anm(m_anm);

#ifdef _HGTIME
	m_hgmode[0]->MeasureTime("");
#endif
}

void HGModalDecomp2D::SetGSModel(
	bool isGS[], int rank, int processes, MPIbyThread *thread, double *err)
{
	vector<vector<double>> dprj;
	vector<vector<double>> xyq(2);
	vector<vector<complex<double>>> anm[2];
	double *sigmain = nullptr, error[2] = {0, 0};

	int steps = 5;
	for(int j = 0; j < 2; j++){
		if(!isGS[j]){
			steps += 2;
		}
	}

	m_calcstatus->SetSubstepNumber(1, steps);
	for(int j = 0; j < 2; j++){
		m_wig4d->GetSliceValues(j, nullptr, dprj);
		m_wig4d->GetXYQArray(j, xyq[0], xyq[1]);
		m_hgmode[j]->AssingData(&xyq, dprj, true);

		if(isGS[j]){
			m_hgmode[j]->SetGSModel();
		}
		else{
			m_hgmode[j]->OptimizeSrcSize(sigmain);
			m_calcstatus->AdvanceStep(1);
			m_hgmode[j]->FourierExpansion();
			m_hgmode[j]->GetAnm(nullptr, rank, processes, thread);
			m_calcstatus->AdvanceStep(1);
			error[j] = m_hgmode[j]->CholeskyDecomp();
		}
		m_hgmode[j]->Get_anm(anm[j]);
		m_srcsize[j] = m_hgmode[j]->GetSigma();
		m_maxmode[j] = m_hgmode[j]->GetMaxOrder(m_maxmode[j]);
		dprj.clear();
		m_calcstatus->AdvanceStep(1);
	}
	*err = sqrt(hypotsq(error[0], error[1]));
	m_normfactor = m_hgmode[0]->GetNormalization();

	int nmodes = (m_maxmode[0]+1)*(m_maxmode[1]+1);
	m_anm.resize(nmodes);
	vector<double> AA(nmodes);
	m_ordered_mode.resize(nmodes);
	int h, k, m, n;
	for(int q = 0; q < nmodes; q++){
		m_ordered_mode[q] = q;
		m_anm[q].resize(nmodes);
		h = q/(m_maxmode[1]+1);
		k = q%(m_maxmode[1]+1);
		AA[q] = 0;
		for(int p = 0; p < nmodes; p++){
			m = p/(m_maxmode[1]+1);
			n = p%(m_maxmode[1]+1);
			m_anm[q][p] = anm[0][h][m]*anm[1][k][n];
			AA[q] += hypotsq(m_anm[q][p].real(), m_anm[q][p].imag());
		}
	}
	sort(AA, m_ordered_mode, nmodes, false);

	vector<int> index(nmodes);
	for(int p = 0; p < nmodes; p++){
		index[p] = p;
		AA[p] = 0;
		for(int q = 0; q < nmodes; q++){
			complex<double> anms = m_anm[m_ordered_mode[q]][m_ordered_mode[p]];
			AA[p] += hypotsq(anms.real(), anms.imag());
		}
	}
	sort(AA, index, nmodes, false);

	for(int q = 0; q < nmodes; q++){
		vector<complex<double>> anmt(m_anm[q]);
		for(int p = 0; p < nmodes; p++){
			m_anm[q][p] = anmt[m_ordered_mode[index[p]]];
		}
	}
	RecursiveSwap(m_anm, m_ordered_mode);

	m_hgmode[2] = new HGModalDecomp(1, m_calcstatus, m_acclevel, nmodes-1, m_cutoff, m_fluxcut, m_wig4d);
	m_hgmode[2]->Set_anm(m_anm);
	m_calcstatus->AdvanceStep(1);
}

//---------- private functions
void HGModalDecomp2D::f_ExportFieldBinary(const char *buffer, 
		vector<vector<double>> *xyarr, vector<vector<vector<complex<double>>>> *Ea)
{
	int nmesh[3];
	double dxy[2], *datar, *datai;

	nmesh[0] = (int)Ea->size();
	for(int j = 0; j < 2; j++){
		nmesh[j+1] = (int)(*xyarr)[j].size();
		dxy[j] = ((*xyarr)[j].back()-(*xyarr)[j].front())/(double)(nmesh[j+1]-1);
	}

	FILE *fp = fopen(buffer, "wb");
	fwrite(nmesh, sizeof(int), 3, fp);
	fwrite(dxy, sizeof(double), 2, fp);

	datar = new double[nmesh[1]*nmesh[2]];
	datai = new double[nmesh[1]*nmesh[2]];

	for(int p = 0; p < nmesh[0]; p++){
		for(int ny = 0; ny < nmesh[2]; ny++){
			for (int nx = 0; nx < nmesh[1]; nx++){
				datar[nx+ny*nmesh[1]] = (*Ea)[p][nx][ny].real();
				datai[nx+ny*nmesh[1]] = (*Ea)[p][nx][ny].imag();
			}
		}
		fwrite(datar, sizeof(double), nmesh[1]*nmesh[2], fp);
		fwrite(datai, sizeof(double), nmesh[1]*nmesh[2], fp);
	}
	fclose(fp);

	delete[] datar;
	delete[] datai;
}

void HGModalDecomp2D::f_ComputeWholeWigner(
	double fnorm, vector<double> &data, 
	int rank, int mpiprocesses, MPIbyThread *thread)
{
	MPI_Status mpistatus;
	int nxy[2], nq[2], indices[NumberWignerUVPrm], npoints;
	vector<int> steps, inistep, finstep;
	mpi_steps(m_anmesh[0], m_anmesh[1], mpiprocesses, &steps, &inistep, &finstep);
	npoints = m_nmesh[0]*m_nmesh[1];

	m_calcstatus->SetSubstepNumber(1, steps[0]);

	for(nq[1] = 0; nq[1] < m_anmesh[1]; nq[1]++){
		indices[WignerUVPrmv] = nq[1];
		for(nq[0] = 0; nq[0] < m_anmesh[0]; nq[0]++){
			indices[WignerUVPrmu] = nq[0];
			int nm = m_anmesh[0]*nq[1]+nq[0];
			if(nm < inistep[rank] || nm > finstep[rank]){
				continue;
			}
			for(nxy[1] = 0; nxy[1] < m_nmesh[1]; nxy[1]++){
				indices[WignerUVPrmV] = nxy[1];
				for(nxy[0] = 0; nxy[0] < m_nmesh[0]; nxy[0]++){
					indices[WignerUVPrmU] = nxy[0];
					int iindex = m_wig4d->GetTotalIndex(indices);
					data[iindex] = fnorm*GetWignerAt(nxy, nq, m_nmesh, m_anmesh);
				}
			}
			m_calcstatus->AdvanceStep(1);
		}
	}

	if(mpiprocesses > 1){
		double *wsmpi = new double[data.size()];
		for(int n = 0; n < (int)data.size(); n++){
			wsmpi[n] = data[n];
		}
		if(thread != nullptr){
			for(int k = 1; k < mpiprocesses; k++){
				thread->SendRecv(wsmpi+inistep[k]*npoints, steps[k]*npoints, MPI_DOUBLE, k, 0, rank);
			}
		}
		else{
			for(int k = 1; k < mpiprocesses; k++){
				if(rank == 0){
					MPI_Recv(wsmpi+inistep[k]*npoints, steps[k]*npoints, MPI_DOUBLE, k, 0, MPI_COMM_WORLD, &mpistatus);
				}
				else if(rank == k){
					MPI_Send(wsmpi+inistep[k]*npoints, steps[k]*npoints, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
				}
				MPI_Barrier(MPI_COMM_WORLD);
			}
		}
		if(thread != nullptr){
			thread->Bcast(wsmpi, m_anmesh[0]*m_anmesh[1]*npoints, MPI_DOUBLE, 0, rank);
		}
		else{
			MPI_Bcast(wsmpi, m_anmesh[0]*m_anmesh[1]*npoints, MPI_DOUBLE, 0, MPI_COMM_WORLD);
		}
		for(int n = 0; n < (int)data.size(); n++){
			data[n] = wsmpi[n];
		}
		delete[] wsmpi;
	}
}

//-----------
HermiteGaussianMode::HermiteGaussianMode(
	double sigma, double lambda, int maxorder, LGFunctionContainer *lgcont)
{
	m_sigma = sigma;
	m_lambda = lambda;
	m_maxorder = maxorder;
	m_lgcont = lgcont;
	m_hgcoef.resize(maxorder+1, 0.0);
}

void HermiteGaussianMode::GetWignerFunctions(int nmax, double x, double theta, vector<double> &W)
{
	double sigpi = 2.0*SQRTPI*m_sigma;
	double xh = x/sigpi;
	double qh = theta/m_lambda*sigpi;
	double r = sqrt(hypotsq(xh, qh));

	for(int n = 0; n <= nmax; n++){
		for(int m = 0; m <= nmax; m++){
			double phi = 0;
			if(r > 0){
				phi = (double)(m-n)*atan2(qh, xh);
			}
			double LG = GetLGFunction(m_lgcont, n, m, r);
			int nm = n*(nmax+1)+m;
			W[2*nm] = LG*sigpi*cos(phi);
			W[2*nm+1] = LG*sigpi*sin(phi);
		}
	}
}

double HermiteGaussianMode::HGFunc(int mode, double xh)
{
	if(mode > m_maxorder){
		return 0.0;
	}
	double xmax = sqrt((double)mode/3+12); 
		// empirical estimation of maximum x to give non-negligible values
	if(fabs(xh) > xmax){
		return 0.0;
	}

	if(m_hgcoef[mode] < INFINITESIMAL){
		m_hgcoef[mode] = 1.0/SQRT2;
		for(int m = 1; m <= mode; m++){
			m_hgcoef[mode] *= (double)(2*m);
		}
		m_hgcoef[mode] = 1.0/sqrt(m_hgcoef[mode]);
	}

	double tex = xh*xh*PI;
	if(tex > MAXIMUM_EXPONENT){
		return 0.0;
	}
	return m_hgcoef[mode]*exp(-tex)*boost::math::hermite(mode, SQRTPI2*xh);
}

void HermiteGaussianMode::SetLGContainer(LGFunctionContainer *lgcont)
{ 
	m_lgcont = lgcont;
}

void HGFunctions(int maxmode, double xh, vector<double> &HG)
{
	double xarg = xh*SQRTPI2;
	double fexp = exp(-xarg*xarg/2)*sqrt(SQRT2);

	HG[0] = fexp;
	if(maxmode == 0){
		return;
	}
	HG[1] = SQRT2*xarg*fexp;
	for(int n = 1; n < maxmode; n++){
		double dn = n;
		HG[n+1] = sqrt(2/(dn+1))*xarg*HG[n]-sqrt(dn/(dn+1))*HG[n-1];
	}
}

double LGFunction(int n, int m, double r)
{
	double rmax = sqrt((double)(m+n)/6+2);
	// empirical estimation of maximum r to give non-negligible values
	if(r > rmax){
		return 0.0;
	}

	int mode = min(n, m);
	int k = abs(n-m);

	double xarg = 2*PI2*r*r;
	double fexp;
	if(k == 0){
		fexp = exp(-xarg/2);
	}
	else{
		fexp = exp(-xarg/2/k)*2*SQRTPI*r;
	}

	double kfact[2] = {2*fexp, 0};
	for(int i = 2; i <= k; i++){
		kfact[0] *= fexp/sqrt(i);
	}
	kfact[1] = -kfact[0]/sqrt(k+1)*(1+k-xarg);

	if(mode == 0){
		return kfact[0];
	}
	else if(mode == 1){
		return kfact[1];
	}
	double H[3] = {kfact[0], kfact[1], 0};

	for(int l = 1; l < mode; l++){
		double denom = sqrt((l+k+1)*(l+1));
		H[2] = ((xarg-2*l-k-1)*H[1]-sqrt(l*(l+k))*H[0])/denom;
		H[0] = H[1];
		H[1] = H[2];
	}
	return H[2];
}

double GetLGFunction(LGFunctionContainer *lgcont, int n, int m, double r)
{
	if(lgcont != nullptr){
		return lgcont->Get(n, m, r);
	}
	return LGFunction(n, m, r);
}

void LGFunctions(int nmmax, double r, vector<vector<double>> &LG)
{
	double xarg = 2*PI2*r*r;
	vector<double> H(nmmax+1);

	for(int k = 0; k <= nmmax; k++){
		int mode = nmmax-k;
		double fexp = exp(-xarg/2)*pow(2*SQRTPI*r, k);
		double kfact[2] = {2, 0};
		for(int i = 2; i <= k; i++){
			kfact[0] /= sqrt(i);
		}
		kfact[1] = -kfact[0]/sqrt(k+1);

		if(mode == 0){
			LG[0][nmmax] = LG[nmmax][0] = fexp*kfact[0];
			continue;
		}
		H[0] = fexp*kfact[0];
		H[1] = fexp*kfact[1]*(1+k-xarg);
		for(int l = 1; l < mode; l++){
			double denom = sqrt((l+k+1)*(l+1));
			H[l+1] = ((xarg-2*l-k-1)*H[l]-sqrt(l*(l+k))*H[l-1])/denom;
		}
		for(int m = k; m <= nmmax; m++){
			int n = m-k;
			LG[m][n] = LG[n][m] = H[n];
		}
	}
}

void GetSparseMatrix(int nmodes, 
	vector<vector<complex<double>>> &anmfull, vector<double> anm[], vector<int> anmidx[])
{
	double reim[2];
	for(int j = 0; j < 2; j++){
		anm[j].clear();
		anmidx[j].clear();
	}
	for(int n = 0; n < nmodes; n++){
		for(int m = 0; m < nmodes; m++){
			int nm = n*nmodes+m;
			reim[0] = anmfull[n][m].real();
			reim[1] = anmfull[n][m].imag();
			for(int j = 0; j < 2; j++){
				if(fabs(reim[j]) > 0){
					anm[j].push_back(reim[j]);
					anmidx[j].push_back(nm);
				}
			}
		}
	}
}

void WriteCommonJSON(stringstream &ssresult, 
	double cmderr[], int nmodes, double fnorm, vector<double> &anmre, vector<double> &anmim)
{
	PrependIndent(JSONIndent, ssresult);
	ssresult << fixed << setprecision(1);
	ssresult << "\"" << CMDErrorLabel << "\"" << 
		": {\"" << MatrixErrLabel << "\": \"" << cmderr[0]*100 << "%\"" 
		<< ", \"" << FluxErrLabel << "\": \"" << cmderr[1]*100 << "%\"";
	if(cmderr[2] >= 0){
		ssresult << ", \"" << WignerErrLabel << "\": \"" << (1.0-cmderr[2])*100 << "%\"";
	}
	ssresult << "}," << endl;
	ssresult << defaultfloat << setprecision(6);

	WriteJSONValue(ssresult, JSONIndent, fnorm, NormFactorLabel.c_str(), false, true);


	PrependIndent(JSONIndent, ssresult);
	ssresult << "\"" << AmplitudeReLabel << "\"" << ": [" << endl;
	PrependIndent(2*JSONIndent, ssresult);
	WriteJSONData(ssresult, 2*JSONIndent, anmre, nmodes, false, false);
	ssresult << endl;
	PrependIndent(JSONIndent, ssresult);
	ssresult << "]," << endl;

	PrependIndent(JSONIndent, ssresult);
	ssresult << "\"" << AmplitudeImLabel << "\"" << ": [" << endl;
	PrependIndent(2*JSONIndent, ssresult);
	WriteJSONData(ssresult, 2*JSONIndent, anmim, nmodes, false, false);
	ssresult << endl;
	PrependIndent(JSONIndent, ssresult);
	ssresult << "]" << endl << "}";
}

void WriteCommonJSON(stringstream &ssresult,
	double cmderr[], double fnorm, vector<double> anm[], vector<int> anmidx[])
{
	PrependIndent(JSONIndent, ssresult);
	ssresult << fixed << setprecision(1);
	ssresult << "\"" << CMDErrorLabel << "\"" <<
		": {\"" << MatrixErrLabel << "\": \"" << cmderr[0]*100 << "%\""
		<< ", \"" << FluxErrLabel << "\": \"" << cmderr[1]*100 << "%\"";
	if(cmderr[2] >= 0){
		ssresult << ", \"" << WignerErrLabel << "\": \"" << (1.0-cmderr[2])*100 << "%\"";
	}
	ssresult << "}," << endl;
	ssresult << defaultfloat << setprecision(6);

	WriteJSONValue(ssresult, JSONIndent, fnorm, NormFactorLabel.c_str(), false, true);

	int maxcols = 100;
	string amplabel[2] = {AmplitudeVReLabel, AmplitudeVImLabel};
	string idxlabel[2] = {AmplitudeIndexReLabel, AmplitudeIndexImLabel};
	for(int j = 0; j < 2; j++){
		PrependIndent(JSONIndent, ssresult);
		ssresult << "\"" << idxlabel[j] << "\"" << ": [" << endl;
		PrependIndent(2*JSONIndent, ssresult);
		WriteJSONData(ssresult, 2*JSONIndent, anmidx[j], maxcols, false, false);
		ssresult << endl;
		PrependIndent(JSONIndent, ssresult);
		ssresult << "]," << endl;

		PrependIndent(JSONIndent, ssresult);
		ssresult << "\"" << amplabel[j] << "\"" << ": [" << endl;
		PrependIndent(2*JSONIndent, ssresult);
		WriteJSONData(ssresult, 2*JSONIndent, anm[j], maxcols, false, false);
		ssresult << endl;
		PrependIndent(JSONIndent, ssresult);
		if(j == 1){
			ssresult << "]" << endl << "}";
		}
		else{
			ssresult << "]," << endl;
		}
	}
}


double GetHLGWidth(int n)
// evaluate the width of Hermite- or Laguerre-Gaussian Functions
{
	// fitting parameters
	double coef = 0.23; 
	double exponent = 0.65;
	double offset = 1.9;
	// envelope width of Gauss-Laguerre function
	double width = coef*pow(n, exponent)+offset;
	return width;
}
