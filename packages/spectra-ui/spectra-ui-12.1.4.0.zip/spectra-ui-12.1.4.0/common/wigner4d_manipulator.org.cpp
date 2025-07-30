#include "wigner4d_manipulator.h"
#include "numerical_common_definitions.h"
#include "spectra_input.h"
#include "output_utility.h"
#include "fast_fourier_transform.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

//---------------------------
// files for debugging
string WigManipTrans;
string WigManipSpatial;
string WigManipAngular;
string WigManipXXprj;
string WigManipYYprj;
string WigManipCSDx;
string WigManipCSDy;

Wigner4DManipulator::Wigner4DManipulator()
{
#ifdef _DEBUG
	WigManipTrans = "..\\debug\\Transfer";
	WigManipSpatial = "..\\debug\\Spatial2D.dat";
//	WigManipAngular = "..\\debug\\Angular2D.dat";
//	WigManipXXprj = "..\\debug\\XXprj.dat";
//	WigManipYYprj = "..\\debug\\YYprj.dat";
	WigManipCSDx = "..\\debug\\CSDx.dat";
	WigManipCSDy = "..\\debug\\CSDy.dat";
#endif

	m_posxy_spl[1] = m_posxy_spl[2] = -1;
	m_maxval = 0;
	for(int j = 0; j < NumberWignerUVPrm; j++){
		m_mesh[j] = 1;
	}
	for(int j = 0; j < NumberWignerUVPrm; j++){
		m_delta[j] = 0;
	}
	m_variables.resize(NumberWignerUVPrm);

	for(int j = 0; j < NumberWignerUVPrm; j++){
		m_meshZ[j] = -1;
	}
}

void Wigner4DManipulator::SetWavelength(double wavelength)
{
	m_lambda = wavelength;
}

bool Wigner4DManipulator::LoadData(string calctype,
	vector<vector<double>> *vararray, vector<double> *data)
{
	if(contains(calctype, menu::XXpYYp)){
		m_type = WignerType4D;
	}
	else if(contains(calctype, menu::XXpprj)){
		m_type = WignerType2DX;
	}
	else if(contains(calctype, menu::YYpprj)){
		m_type = WignerType2DY;
	}
	else{
		return false;
	}

	int uvidx = 0;
	for(int j = 0; j < vararray->size(); j++){
		if(m_type == WignerType4D){
			uvidx = j;
		}
		else if(m_type == WignerType2DX){
			uvidx = 2*j;
		}
		else if(m_type == WignerType2DY){
			uvidx = 2*j+1;
		}
		m_variables[uvidx] = (*vararray)[j];
		m_mesh[uvidx] = (int)m_variables[uvidx].size();
		m_delta[uvidx] = m_variables[uvidx][1]-m_variables[uvidx][0];
	}
	f_SetSteps(m_steps, m_mesh);

	if(data->size() != m_steps[NumberWignerUVPrm]){
		return false;
	}
	m_data = *data;

	return true;
}

bool Wigner4DManipulator::LoadData(picojson::object &obj)
{
	int dimension = (int)floor(0.5+obj[DataDimLabel].get<double>());
	picojson::array &ptitles = obj[DataTitlesLabel].get<picojson::array>();
	vector<string> titles;
	int index[NumberWignerUVPrm];
	bool isprj, isbrill, isx, isy, isqx, isqy;
	isprj = isbrill = isx = isy = isqx = isqy = false;
	for(int j = 0; j < ptitles.size(); j++){
		titles.push_back(ptitles[j].get<string>());
		if(titles.back() == TitleLablesDetailed[Brill1D_]){
			isprj = true;
		}
		if(titles.back() == TitleLablesDetailed[WBrill_]){
			isbrill = true;
		}
		if(titles.back() == TitleLablesDetailed[SrcX_]){
			index[WignerUVPrmU] = j;
			isx = true;
		}
		if(titles.back() == TitleLablesDetailed[SrcQX_]){
			index[WignerUVPrmu] = j;
			isqx = true;
		}
		if(titles.back() == TitleLablesDetailed[SrcY_]){
			index[WignerUVPrmV] = j;
			isy = true;
		}
		if(titles.back() == TitleLablesDetailed[SrcQY_]){
			index[WignerUVPrmv] = j;
			isqy = true;
		}
	}
	if(isbrill){
		if(!(isx&&isy&&isqx&&isqy)){
			return false;
		}
		m_type = WignerType4D;
	}
	else if(isprj){
		if(isx && isqx){
			m_type = WignerType2DX;
		}
		else if(isy && isqy){
			m_type = WignerType2DY;
		}
		else{
			return false;
		}
	}
	else{
		return false;
	}

	picojson::array &punits = obj[UnitsLabel].get<picojson::array>();
	vector<string> units;
	for(int j = 0; j < punits.size(); j++){
		units.push_back(punits[j].get<string>());
	}
	picojson::array &pdata = obj[DataLabel].get<picojson::array>();

	vector<int> varidx;
	GetVarIndices(varidx);

	for(int j = 0; j < varidx.size(); j++){
		int uvidx = varidx[j];
		picojson::array &vardata = pdata[index[uvidx]].get<picojson::array>();
		m_mesh[uvidx] = (int)vardata.size();
		m_variables[uvidx].resize(m_mesh[uvidx]);
		for(int n = 0; n < m_mesh[uvidx]; n++){
			m_variables[uvidx][n] = vardata[n].get<double>();
		}
		m_delta[uvidx] = m_variables[uvidx][1]-m_variables[uvidx][0];
	}
	f_SetSteps(m_steps, m_mesh);

	picojson::array &pwigner = pdata[dimension].get<picojson::array>();
	int ndata = (int)pwigner.size();
	if(ndata != m_steps[NumberWignerUVPrm]){
		return false;
	}

	m_data.resize(ndata);
	for(int n = 0; n < ndata; n++){
		m_data[n] = pwigner[n].get<double>();
	}

	return true;
}

void Wigner4DManipulator::GetVarIndices(vector<int> &varidx)
{
	if(m_type == WignerType4D || m_type == WignerType2DX){
		varidx.push_back(WignerUVPrmU);
		varidx.push_back(WignerUVPrmu);
	}
	if(m_type == WignerType4D || m_type == WignerType2DY){
		varidx.push_back(WignerUVPrmV);
		varidx.push_back(WignerUVPrmv);
	}
}

void Wigner4DManipulator::RetrieveData(
	vector<vector<double>> &vararray, vector<double> &data)
{
	if(m_type == WignerType4D){
		vararray = m_variables;
	}
	else{
		vararray.resize(2);
		if(m_type == WignerType2DX){
			vararray[0] = m_variables[WignerUVPrmU];
			vararray[1] = m_variables[WignerUVPrmu];
		}
		else{
			vararray[0] = m_variables[WignerUVPrmV];
			vararray[1] = m_variables[WignerUVPrmv];
		}
	}
	data = m_data;
}

void Wigner4DManipulator::f_SetSteps(int *steps, int *mesh)
{
	steps[WignerUVPrmU] = 1;
	steps[WignerUVPrmV] = mesh[WignerUVPrmU]; 
	steps[WignerUVPrmu] = mesh[WignerUVPrmV]*steps[WignerUVPrmV];
	steps[WignerUVPrmv] = mesh[WignerUVPrmu]*steps[WignerUVPrmu];
	steps[NumberWignerUVPrm] = mesh[WignerUVPrmv]*steps[WignerUVPrmv];
}

void Wigner4DManipulator::GetXYQArray(int jxy, vector<double> &xy, vector<double> &q)
{
	int ix, iq;

	if(jxy == 0){
		ix = WignerUVPrmU;
		iq = WignerUVPrmu;
	}
	else{
		ix = WignerUVPrmV;
		iq = WignerUVPrmv;
	}
	xy = m_variables[ix];
	q = m_variables[iq];
}

int Wigner4DManipulator::GetTotalIndex(int indices[], int *steps)
{
	int iindex = 0;
	for(int j = 0; j < NumberWignerUVPrm; j++){
		if(steps == nullptr){
			iindex += indices[j]*m_steps[j];
		}
		else{
			iindex += indices[j]*steps[j];
		}
	}
	return iindex;
}

double Wigner4DManipulator::GetValue(int indices[])
{
	int iindex = GetTotalIndex(indices);
	return m_data[iindex];
}

void Wigner4DManipulator::GetSliceValues(int jxy, int *posidx, vector<vector<double>> &data)
{
	int mesh[2], mini[2], mfin[2], m[2], indices[NumberWignerUVPrm];
	double dxdq;

	if(jxy == 0){
		mesh[0] = m_mesh[WignerUVPrmU];
		mesh[1] = m_mesh[WignerUVPrmu];
		dxdq = m_delta[WignerUVPrmV]*m_delta[WignerUVPrmv]*1.0e-6; // mm.mrad -> m.rad
	}
	else{
		mesh[0] = m_mesh[WignerUVPrmV];
		mesh[1] = m_mesh[WignerUVPrmv];
		dxdq = m_delta[WignerUVPrmU]*m_delta[WignerUVPrmu]*1.0e-6; // mm.mrad -> m.rad
	}
	dxdq /= m_lambda; // convert integration from (x,theta_x) to (x^, theta_x^)

	if(posidx == nullptr){
		mini[0] = 0; mini[1] = 0;
		if(jxy == 0){
			mfin[0] = m_mesh[WignerUVPrmV]-1;
			mfin[1] = m_mesh[WignerUVPrmv]-1;
		}
		else{
			mfin[0] = m_mesh[WignerUVPrmU]-1;
			mfin[1] = m_mesh[WignerUVPrmu]-1;
		}
	}
	else{
		mini[0] = mfin[0] = posidx[0];
		mini[1] = mfin[1] = posidx[1];
	}

	if(data.size() < mesh[0]){
		data.resize(mesh[0]);
	}

	for(int nx = 0; nx < mesh[0]; nx++){
		if(data[nx].size() < mesh[0]){
			data[nx].resize(mesh[1]);
		}
		for(int nq = 0; nq < mesh[1]; nq++){
			data[nx][nq] = 0;
			for(m[0] = mini[0]; m[0] <= mfin[0]; m[0]++){
				for(m[1] = mini[1]; m[1] <= mfin[1]; m[1]++){
					if(jxy == 0){
						indices[WignerUVPrmU] = nx;
						indices[WignerUVPrmV] = m[0];
						indices[WignerUVPrmu] = nq;
						indices[WignerUVPrmv] = m[1];
					}
					else{
						indices[WignerUVPrmU] = m[0];
						indices[WignerUVPrmV] = nx;
						indices[WignerUVPrmu] = m[1];
						indices[WignerUVPrmv] = nq;
					}
					data[nx][nq] += GetValue(indices);
					if(posidx == nullptr){
						m_maxval = max(m_maxval, (double)fabs(GetValue(indices)));
					}
				}
			}
			if(posidx == nullptr){
				data[nx][nq] *= dxdq;
			}
		}
	}
}

void Wigner4DManipulator::PrepareSpline(int xyposidx[])
{
	int nmesh[2];
	nmesh[0] = m_mesh[WignerUVPrmu];
	nmesh[1] = m_mesh[WignerUVPrmv];

	if(m_z.size() < nmesh[0]){
		m_z.resize(nmesh[0]);
		for(int n = 0; n < nmesh[0]; n++){
			m_z[n].resize(nmesh[1]);
		}
	}
	int indices[NumberWignerUVPrm];

	indices[WignerUVPrmU] = xyposidx[0]; 
	indices[WignerUVPrmV] = xyposidx[1];
	for(int n = 0; n < nmesh[0]; n++){
		indices[WignerUVPrmu] = n; 
		for(int m = 0; m < nmesh[1]; m++){
			indices[WignerUVPrmv] = m; 
			m_z[n][m] = GetValue(indices);
		}
	}
	m_xypspl2d.SetSpline2D(nmesh, &m_variables[WignerUVPrmu], &m_variables[WignerUVPrmv], &m_z);
	m_posxy_spl[0] = xyposidx[0];
	m_posxy_spl[1] = xyposidx[1];
}

double Wigner4DManipulator::GetInterpolatedValue(int xyposidx[], double xyp[], bool islinear)
{
	double value;
	if(xyposidx[0] != m_posxy_spl[0] 
			|| xyposidx[1] != m_posxy_spl[1]){
		PrepareSpline(xyposidx);
	}

	if(islinear){
		value = m_xypspl2d.GetLinear(xyp);
	}
	else{
		value = m_xypspl2d.GetValue(xyp);
	}
	return value;
}

void Wigner4DManipulator::GetCoherenceDeviation(
	double *degcoh, double *devsigma, vector<double> &data)
{
	double sq, sqc, sum, wigr, dsig;

	sq = sqc = sum = dsig = 0;
	for(int n = 0; n < m_steps[NumberWignerUVPrm]; n++){
		wigr = m_data[n];
		sq += wigr*wigr;
		sqc += wigr*(double)data[n];
		dsig += (wigr-(double)data[n])*(wigr-(double)data[n]);
		sum += wigr;
	}
	devsigma[WigErrorCorrelation] = 1.0-sqc/sq;
	devsigma[WigErrorDeviation] = sqrt(dsig/sq);

	double dOmega = GetPhaseVolume();
	double coef;
	sum *= dOmega; // Total Flux
	if(m_type == WignerType4D){
		coef = dOmega*1.0e+12; // /mm^2/mrad^2 -> /m^2/rad^2
		coef *= m_lambda*m_lambda;
	}
	else{
		coef = dOmega*1.0e+6;  // /mm/mrad -> /m/rad
		coef *= m_lambda;
	}
	sq *= coef;
	dsig *= coef;
	*degcoh = sq/sum/sum;
	devsigma[WigErrorCoherent] = sqrt(dsig/sum/sum);
}

double Wigner4DManipulator::GetPhaseVolume()
{
	double dOmega = 1.0;
	if(m_type != WignerType2DX){
		dOmega *= m_delta[WignerUVPrmV]*m_delta[WignerUVPrmv];
	}
	if(m_type != WignerType2DY){
		dOmega *= m_delta[WignerUVPrmU]*m_delta[WignerUVPrmu];
	}
	return dOmega;
}

void Wigner4DManipulator::GetProjection(vector<double> &fdens)
{
	double dq;
	if(m_type == WignerType4D){
		dq = m_delta[WignerUVPrmu]*m_delta[WignerUVPrmv];
	}
	else{
		dq = m_type == WignerType2DX ? m_delta[WignerUVPrmu] : m_delta[WignerUVPrmv];
	}

	fdens.resize(m_mesh[WignerUVPrmU]*m_mesh[WignerUVPrmV]);

	int n[4];
	for(n[0] = 0; n[0] < m_mesh[WignerUVPrmU]; n[0]++){
		for(n[1] = 0; n[1] < m_mesh[WignerUVPrmV]; n[1]++){
			for(n[2] = 0; n[2] < m_mesh[WignerUVPrmu]; n[2]++){
				for(n[3] = 0; n[3] < m_mesh[WignerUVPrmv]; n[3]++){
					fdens[n[0]+n[1]*m_mesh[WignerUVPrmU]] += dq*GetValue(n);
				}
			}
		}
	}
}

void Wigner4DManipulator::GetCSD(double Z,
	vector<vector<double>> &vararray, vector<vector<vector<vector<double>>>> *CSD,
	double *xymax, int *xypoints, bool normalized)
{
	Transfer(Z, xymax, xypoints, normalized);

	int nfft[NumberWignerUVPrm] = {1, 1, 1, 1};
	int meshfft[NumberWignerUVPrm] = {1, 1, 1, 1};
	int hmeshfft[NumberWignerUVPrm] = {0, 0, 0, 0};
	double deltaZ[NumberWignerUVPrm] = {0, 0, 0, 0};
	double slim;
	//------>>>>>>
	int level = 2;
	//------>>>>>>
	for(int j = 0; j < NumberWignerUVPrm; j++){
		if(j == WignerUVPrmu || j == WignerUVPrmv){
			if(m_hmeshZ[j] > 0){
				nfft[j] = fft_number(m_meshZ[j], 0);
				while(nfft[j]*m_deltaZ[j] < m_delta[j]*m_mesh[j]*level){
					nfft[j] <<= 1;
				}
				deltaZ[j] = m_lambda/(1e-3*m_deltaZ[j]*nfft[j])*1e3; // mm -> m -> mm
				double div = j == WignerUVPrmu ? m_sdiv[0] : m_sdiv[1];
				slim = 1e3*GAUSSIAN_MAX_REGION*m_lambda/PI2/(div*1e-3);
				hmeshfft[j] = (int)floor(0.5+slim/deltaZ[j]);
				meshfft[j] = 2*hmeshfft[j]+1;
				if(meshfft[j] > nfft[j]-1){
					meshfft[j] = nfft[j]-1;
					hmeshfft[j] = (meshfft[j]-1)/2;
				}
			}
		}
		else{
			deltaZ[j] = m_deltaZ[j];
			meshfft[j] = m_meshZ[j];
			hmeshfft[j] = m_hmeshZ[j];
		}
	}
	f_SetSteps(m_stepsZ, meshfft);

	int ndim = m_hmeshZ[WignerUVPrmu] > 0 && m_hmeshZ[WignerUVPrmv] > 0 ? 2 : 1;
	double *ws, **ws2;
	vector<int> varidx;
	FastFourierTransform *fft;
	if(ndim == 2){
		fft = new FastFourierTransform(2, nfft[WignerUVPrmu], nfft[WignerUVPrmv]);
		ws2 = new double* [nfft[WignerUVPrmu]];
		for(int n = 0; n < nfft[WignerUVPrmu]; n++){
			ws2[n] = new double [2*nfft[WignerUVPrmv]];
		}
		varidx = vector<int> {WignerUVPrmU, WignerUVPrmV, WignerUVPrmu, WignerUVPrmv};
	}
	else if(m_hmeshZ[WignerUVPrmu] > 0){
		fft = new FastFourierTransform(1, nfft[WignerUVPrmu]);
		ws = new double[2*nfft[WignerUVPrmu]];
		varidx = vector<int> {WignerUVPrmU, WignerUVPrmu};
	}
	else{
		fft = new FastFourierTransform(1, nfft[WignerUVPrmv]);
		ws = new double[2*nfft[WignerUVPrmv]];
		varidx = vector<int>{WignerUVPrmV, WignerUVPrmv};
	}

	for(int j = 0; j < varidx.size(); j++){
		int idx = varidx[j];
		vector<double> vtmp(meshfft[idx]);
		int hmesh = (meshfft[idx]-1)/2;
		for(int n = -hmesh; n <= hmesh; n++){
			vtmp[n+hmesh] = n*deltaZ[idx];
		}
		vararray.push_back(vtmp);
	}
	for(int n = 0; n < 2; n++){
		CSD[n].resize(m_meshZ[WignerUVPrmU]);
		for(int i = 0; i < meshfft[WignerUVPrmU]; i++){
			CSD[n][i].resize(meshfft[WignerUVPrmV]);
			for(int j = 0; j < meshfft[WignerUVPrmV]; j++){
				CSD[n][i][j].resize(meshfft[WignerUVPrmu]);
				for(int k = 0; k < meshfft[WignerUVPrmu]; k++){
					CSD[n][i][j][k].resize(meshfft[WignerUVPrmv]);
				}
			}
		}
	}

	double UV[2];
	for(int i = -m_hmeshZ[WignerUVPrmU]; i <= m_hmeshZ[WignerUVPrmU]; i++){
		int ii = i+m_hmeshZ[WignerUVPrmU];
		UV[0] = i*m_deltaZ[WignerUVPrmU];
		for(int j = -m_hmeshZ[WignerUVPrmV]; j <= m_hmeshZ[WignerUVPrmV]; j++){
			int jj = j+m_hmeshZ[WignerUVPrmV];
			UV[1] = j*m_deltaZ[WignerUVPrmV];
			for(int k = 0; k < nfft[WignerUVPrmu]; k++){
				int kk = k;
				if(nfft[WignerUVPrmu] > 1){
					kk = fft_index(k, nfft[WignerUVPrmu], 1)+m_hmeshZ[WignerUVPrmu];
				}
				for(int l = 0; l < nfft[WignerUVPrmv]; l++){
					int ll = l;
					if(nfft[WignerUVPrmv] > 1){
						ll = fft_index(l, nfft[WignerUVPrmv], 1)+m_hmeshZ[WignerUVPrmv];
					}
					if(ndim == 2){
						ws2[k][2*l] = ws2[k][2*l+1] = 0;
						if(kk >= 0 && kk <= m_meshZ[WignerUVPrmu] 
							&& ll >= 0 && ll <= m_meshZ[WignerUVPrmu])
						{
							ws2[k][2*l] = m_dataZ[ii][jj][kk][ll]*m_deltaZ[WignerUVPrmu]*m_deltaZ[WignerUVPrmv];
						}
					}
					else if(m_hmeshZ[WignerUVPrmu] > 0){
						ws[2*k] = ws[2*k+1] = 0;
						if(kk >= 0 && kk < m_meshZ[WignerUVPrmu]){
							ws[2*k] = m_dataZ[ii][jj][kk][ll]*m_deltaZ[WignerUVPrmu];
						}
					}
					else{
						ws[2*l] = ws[2*l+1] = 0;
						if(ll >= 0 && ll < m_meshZ[WignerUVPrmv]){
							ws[2*l] = m_dataZ[ii][jj][kk][ll]*m_deltaZ[WignerUVPrmv];
						}
					}
				}
			}
			if(ndim == 2){
				fft->DoFFT(ws2, -1);
			}
			else{
				fft->DoFFT(ws, -1);
			}

			double phase[2] = {0, 0}, phs = 0, csn[2];
			for(int k = 0; k < nfft[WignerUVPrmu]; k++){
				int kk = k;
				if(nfft[WignerUVPrmu] > 1){
					kk = fft_index(k, nfft[WignerUVPrmu], 1)+hmeshfft[WignerUVPrmu];
				}
				if(kk < 0 || kk >= meshfft[WignerUVPrmu]){
					continue;
				}
				if(m_farzone[0]){
					phase[0] = fft_index(k, nfft[WignerUVPrmu], 1)*deltaZ[WignerUVPrmu]*UV[0]*1e-6;
					// mm^2 -> m^2
				}
				for(int l = 0; l < nfft[WignerUVPrmv]; l++){
					int ll = l;
					if(nfft[WignerUVPrmv] > 1){
						ll = fft_index(l, nfft[WignerUVPrmv], 1)+hmeshfft[WignerUVPrmv];
					}
					if(ll < 0 || ll >= meshfft[WignerUVPrmv]){
						continue;
					}
					if(m_farzone[1]){
						phase[1] = fft_index(l, nfft[WignerUVPrmv], 1)*deltaZ[WignerUVPrmv]*UV[1]*1e-6;
						// mm^2 -> m^2
					}
					if(fabs(Z) > 0){
						phs = -(phase[0]+phase[1])*PI2/m_lambda/Z;
					}
					csn[0] = cos(phs);
					csn[1] = sin(phs);
					if(ndim == 2){
						multiply_complex(ws2[k]+2*l, csn);
						CSD[0][ii][jj][kk][ll] = ws2[k][2*l];
						CSD[1][ii][jj][kk][ll] = ws2[k][2*l+1];
					}
					else if(m_hmeshZ[WignerUVPrmu] > 0){
						multiply_complex(ws+2*k, csn);
						CSD[0][ii][jj][kk][ll] = ws[2*k];
						CSD[1][ii][jj][kk][ll] = ws[2*k+1];
					}
					else{
						multiply_complex(ws+2*l, csn);
						CSD[0][ii][jj][kk][ll] = ws[2*l];
						CSD[1][ii][jj][kk][ll] = ws[2*l+1];
					}
				}
			}
		}
	}

	delete fft;
	if(ndim == 2){
		for(int n = 0; n < nfft[WignerUVPrmu]; n++){
			delete[] ws2[n];
		}
		delete ws2;
	}
	else{
		delete ws;
	}

#ifdef _DEBUG
	if(!WigManipCSDx.empty() && nfft[WignerUVPrmu] > 1){
		vector<string> titles {"X", "DX", "F", "Real", "Imag"};
		vector<double> items(titles.size());
		ofstream debug_out(WigManipCSDx);
		PrintDebugItems(debug_out, titles);
		for(int i = 0; i < meshfft[WignerUVPrmU]; i++){
			items[0] = vararray[0][i];
			for(int k = 0; k < meshfft[WignerUVPrmu]; k++){
				items[1] = vararray[1][k];
				items[3] = items[4] = 0;
				for(int j = 0; j < meshfft[WignerUVPrmV]; j++){
					for(int l = 0; l < meshfft[WignerUVPrmv]; l++){
						items[3] += CSD[0][i][j][k][l];
						items[4] += CSD[1][i][j][k][l];
					}
				}
				items[2] = sqrt(hypotsq(items[3], items[4]));
				PrintDebugItems(debug_out, items);
			}
		}
	}
	if(!WigManipCSDy.empty() && nfft[WignerUVPrmv] > 1){
		vector<string> titles{"Y", "DY", "F", "Real", "Imag"};
		vector<double> items(titles.size());
		ofstream debug_out(WigManipCSDy);
		PrintDebugItems(debug_out, titles);
		for(int j = 0; j < meshfft[WignerUVPrmV]; j++){
			items[0] = vararray[0][j];
			for(int l = 0; l < meshfft[WignerUVPrmv]; l++){
				items[1] = vararray[1][l];
				items[3] = items[4] = 0;
				for(int i = 0; i < meshfft[WignerUVPrmU]; i++){
					for(int k = 0; k < meshfft[WignerUVPrmu]; k++){
						items[3] += CSD[0][i][j][k][l];
						items[4] += CSD[1][i][j][k][l];
					}
				}
				items[2] = sqrt(hypotsq(items[3], items[4]));
				PrintDebugItems(debug_out, items);
			}
		}
	}
#endif

}

bool Wigner4DManipulator::Transfer(double Z, double *xymax, int *xypoints, bool normalized)
{
	f_GetSigma(0, m_sigmaorg);
	for(int j = 0; j < 2; j++){
		int iUV = j == 0 ? WignerUVPrmU : WignerUVPrmV;
		int iuv = j == 0 ? WignerUVPrmu : WignerUVPrmv;
		m_sizeZ[j] = sqrt(hypotsq(m_sigmaorg[iUV], m_sigmaorg[iuv]*Z));
		if(m_sigmaorg[iUV] > 0){
			m_sdiv[j] = m_sigmaorg[iuv]*m_sigmaorg[iUV]/m_sizeZ[j];
		}
		else{
			m_sdiv[j] = 0;
		}

	}

	for(int j = 0; j < NumberWignerUVPrm; j++){
		if(m_mesh[j]%2 == 0){
			return false;
		}
		m_hmesh[j] = (m_mesh[j]-1)/2;
	}

	vector<int> varidx;
	GetVarIndices(varidx);

	double Border[2] = {1, 2};
	double DeltaUV[2] = {
		m_delta[WignerUVPrmU]*(m_mesh[WignerUVPrmU]-1), 
		m_delta[WignerUVPrmV]*(m_mesh[WignerUVPrmV]-1)
	};
	double Deltauv[2] = {
		m_delta[WignerUVPrmu]*(m_mesh[WignerUVPrmu]-1), 
		m_delta[WignerUVPrmv]*(m_mesh[WignerUVPrmv]-1)
	};

	double Znear[2] = {0, 0}, Zfar[2] = {0, 0};
	for(int j = 0; j < varidx.size(); j++){
		int uvidx = varidx[j];
		int i = -1;
		if(uvidx == WignerUVPrmU){
			i = 0;
		}
		else if(uvidx == WignerUVPrmV){
			i = 1;
		}
		if(i >= 0){
			Znear[i] = Border[0]*DeltaUV[i]/Deltauv[i];
			Zfar[i] = Border[1]*DeltaUV[i]/Deltauv[i];
		}
	}

	int ifin[2] = {1, 1};
	int vidx[2] = {WignerUVPrmU, WignerUVPrmV};
	m_farzone[0] = m_farzone[1] = true;
	for(int j = 0; j < 2; j++){
		int uv = j == 0 ? WignerUVPrmu : WignerUVPrmv;
		int UV = j == 0 ? WignerUVPrmU : WignerUVPrmV;
		m_meshZ[uv] = m_meshZ[UV] = 1;
		m_hmeshZ[uv] = m_hmeshZ[UV] = 0;
		m_deltaZ[uv] = m_deltaZ[UV] = 0;
		if(Zfar[j] > 0){
			ifin[j] = 2; // interpolation rank, linear: 2, quadratic: 3
			DeltaUV[j] += Deltauv[j]*Z;
			m_farzone[j] = Z > Zfar[j];

			double deltan = m_delta[UV];
			double deltaf = m_delta[uv]*Z;

			if(m_farzone[j]){ // far zone
				m_deltaZ[uv] = m_delta[UV]/Z;
				m_deltaZ[UV] = deltaf;
				m_meshZ[uv] = m_mesh[UV];
				vidx[j] = j==0?WignerUVPrmu:WignerUVPrmv;
			}
			else{
				m_deltaZ[uv] = m_delta[uv];
				m_meshZ[uv] = m_mesh[uv];
				if(Z > Znear[j]){ // intermediate
					m_deltaZ[UV] = deltan+(deltaf-deltan)/(Zfar[j]-Znear[j])*(Z-Znear[j]);
				}
				else{ // near zone
					m_deltaZ[UV] = deltan;
				}
			}
			m_hmeshZ[UV] = (int)floor(0.5+DeltaUV[j]/2/m_deltaZ[UV]);
			m_meshZ[UV] = 2*m_hmeshZ[UV]+1;
			m_hmeshZ[uv] = (m_meshZ[uv]-1)/2;
		}
	}
	if(xymax != nullptr){
		for(int j = 0; j < 2; j++){
			int UV = j == 0 ? WignerUVPrmU : WignerUVPrmV;
			m_hmeshZ[UV] = (xypoints[j]-1)/2;
			m_meshZ[UV] = 2*m_hmeshZ[UV]+1;
			m_deltaZ[UV] = fabs(xymax[j])/m_hmeshZ[UV];
			if(normalized){
				m_deltaZ[UV] *= m_sizeZ[j];
			}
		}
	}

	vector<double> a[2];
	for(int j = 0; j < 2; j++){
		a[j].resize(ifin[j], 1.0);
	}

	m_dataZ.clear();
	m_dataZ.resize(m_meshZ[WignerUVPrmU]);
	for(int i = 0; i < m_meshZ[WignerUVPrmU]; i++){
		m_dataZ[i].resize(m_meshZ[WignerUVPrmV]);
		for(int j = 0; j < m_meshZ[WignerUVPrmV]; j++){
			m_dataZ[i][j].resize(m_meshZ[WignerUVPrmu]);
			for(int k = 0; k < m_meshZ[WignerUVPrmu]; k++){
				m_dataZ[i][j][k].resize(m_meshZ[WignerUVPrmv]);
			}
		}
	}

	double UV[2]; // coordinate in the target Z
	double delta[2];
	int index[NumberWignerUVPrm] = {0, 0, 0, 0};
	int gindex[NumberWignerUVPrm];

	for(int i = -m_hmeshZ[WignerUVPrmU]; i <= m_hmeshZ[WignerUVPrmU]; i++){
		int ii = i+m_hmeshZ[WignerUVPrmU];
		UV[0] = i*m_deltaZ[WignerUVPrmU];
		for(int j = -m_hmeshZ[WignerUVPrmV]; j <= m_hmeshZ[WignerUVPrmV]; j++){
			int jj = j+m_hmeshZ[WignerUVPrmV];
			UV[1] = j*m_deltaZ[WignerUVPrmV];
			for(int k = -m_hmeshZ[WignerUVPrmu]; k <= m_hmeshZ[WignerUVPrmu]; k++){
				int kk = k+m_hmeshZ[WignerUVPrmu];
				if(Zfar[0] > 0){
					f_SetWindex(0, Z, ifin, m_farzone, k, index, UV, &delta[0]);
					if(index[WignerUVPrmu] < 0 || index[WignerUVPrmU] < 0){
						continue;
					}
				}
				for(int l = -m_hmeshZ[WignerUVPrmv]; l <= m_hmeshZ[WignerUVPrmv]; l++){
					int ll = l+m_hmeshZ[WignerUVPrmv];
					if(Zfar[1] > 0){
						f_SetWindex(1, Z, ifin, m_farzone, l, index, UV, &delta[1]);
						if(index[WignerUVPrmv] < 0 || index[WignerUVPrmV] < 0){
							continue;
						}
					}

					for(int j = 0; j < 2; j++){
						if(ifin[j] == 2){
							a[j][0] = 1-delta[j];
							a[j][1] = delta[j];
						}
						else if(ifin[j] == 3){
							double del2 = delta[j]*delta[j];
							a[j][0] = (del2-delta[j])/2;
							a[j][1] = 1-del2;
							a[j][2] = (del2+delta[j])/2;
						}
					}

					m_dataZ[ii][jj][kk][ll] = 0;
					for(int i = 0; i < NumberWignerUVPrm; i++){
						gindex[i] = index[i];
					}
					for(int ix = 0; ix < ifin[0]; ix++){
						gindex[vidx[0]] = index[vidx[0]]+ix;
						for(int iy = 0; iy < ifin[1]; iy++){
							gindex[vidx[1]] = index[vidx[1]]+iy;
							m_dataZ[ii][jj][kk][ll] += GetValue(gindex)*a[0][ix]*a[1][iy];
						}
					}
				}
			}
		}
	}

#ifdef _DEBUG
	if(Zfar[0] > 0 && Zfar[1] > 0){
		f_ExportProfile2D();
	}
	else{
		int jxy = Zfar[0] > 0 ? 0 : 1;
		f_ExportWTrans(Z, m_farzone[jxy], jxy, false);
	}
#endif

	return true;
}

void Wigner4DManipulator::f_GetSigma(double Z, double *sigma)
{
	for(int n = 0; n < NumberWignerUVPrm; n++){
		sigma[n] = 0;
	}
	double var[NumberWignerUVPrm], data;
	double sum = 0;
	int hmesh[NumberWignerUVPrm];
	double delta[NumberWignerUVPrm];

	bool isorg = false;
	if(fabs(Z) > 0){
		for(int j = 0; j < NumberWignerUVPrm; j++){
			hmesh[j] = m_hmeshZ[j];
			delta[j] = m_deltaZ[j];
		}
	}
	else{
		isorg = true;
		for(int j = 0; j < NumberWignerUVPrm; j++){
			hmesh[j] = m_hmesh[j];
			delta[j] = m_delta[j];
		}
	}

	int indices[4];
	for(int i = -hmesh[WignerUVPrmU]; i <= hmesh[WignerUVPrmU]; i++){
		indices[0] = i+hmesh[WignerUVPrmU];
		var[WignerUVPrmU] = i*delta[WignerUVPrmU];
		for(int j = -hmesh[WignerUVPrmV]; j <= hmesh[WignerUVPrmV]; j++){
			indices[1] = j+hmesh[WignerUVPrmV];
			var[WignerUVPrmV] = j*delta[WignerUVPrmV];
			for(int k = -hmesh[WignerUVPrmu]; k <= hmesh[WignerUVPrmu]; k++){
				indices[2] = k+hmesh[WignerUVPrmu];
				var[WignerUVPrmu] = k*delta[WignerUVPrmu];
				if(m_farzone[0] && !isorg){
					var[WignerUVPrmu] += var[WignerUVPrmU]/Z;
				}
				for(int l = -hmesh[WignerUVPrmv]; l <= hmesh[WignerUVPrmv]; l++){
					indices[3] = l+hmesh[WignerUVPrmv];
					var[WignerUVPrmv] = l*delta[WignerUVPrmv];
					if(m_farzone[1] && !isorg){
						var[WignerUVPrmv] += var[WignerUVPrmV]/Z;
					}
					if(isorg){
						data = GetValue(indices);
					}
					else{
						data = m_dataZ[indices[0]][indices[1]][indices[2]][indices[3]];
					}
					sum += data;
					for(int n = 0; n < NumberWignerUVPrm; n++){
						sigma[n] += data*var[n]*var[n];
					}
				}
			}
		}
	}
	for(int n = 0; n < NumberWignerUVPrm; n++){
		sigma[n] = sqrt(max(0.0, sigma[n]/sum));
	}
}

void Wigner4DManipulator::f_GetSliceDivergence(double *sigma)
{
	double var[2], sum = 0;
	int ii = m_hmeshZ[WignerUVPrmU];
	int jj = m_hmeshZ[WignerUVPrmV];
	sigma[0] = sigma[1] = 0;
	for(int k = -m_hmeshZ[WignerUVPrmu]; k <= m_hmeshZ[WignerUVPrmu]; k++){
		int kk = k+m_hmeshZ[WignerUVPrmu];
		var[0] = k*m_deltaZ[WignerUVPrmu];
		for(int l = -m_hmeshZ[WignerUVPrmv]; l <= m_hmeshZ[WignerUVPrmv]; l++){
			int ll = l+m_hmeshZ[WignerUVPrmv];
			var[1] = l*m_deltaZ[WignerUVPrmv];
			sum += m_dataZ[ii][jj][kk][ll];
			for(int j = 0; j < 2; j++){
				sigma[j] += m_dataZ[ii][jj][kk][ll]*var[j]*var[j];
			}
		}
	}
	if(sum > 0){
		for(int j = 0; j < 2; j++){
			sigma[j] = sqrt(max(0.0, sigma[j]/sum));
		}
	}
	else{
		sigma[0] = sigma[1] = 0;
	}

}

void Wigner4DManipulator::f_ExportProfile2D()
{
	string paths[4] = {WigManipSpatial, WigManipAngular, WigManipXXprj, WigManipYYprj};
	vector<int> index[4] = {
		{WignerUVPrmU, WignerUVPrmV, WignerUVPrmu, WignerUVPrmv}, 
		{WignerUVPrmu, WignerUVPrmv, WignerUVPrmU, WignerUVPrmV},
		{WignerUVPrmU, WignerUVPrmu, WignerUVPrmV, WignerUVPrmv},
		{WignerUVPrmV, WignerUVPrmv, WignerUVPrmU, WignerUVPrmu}
	};
	vector<string> titles[4] = {
		{"X", "Y", "Flux"},
		{"X'", "Y'", "Flux"},
		{"X'", "X'", "Flux"},
		{"Y", "Y'", "Flux"}
	};
	int s[4], q[4];
	for(int n = 0; n < 4; n++){
		if(!paths[n].empty()){
			for(int m = 0; m < 4; m++){
				s[m] = index[n][m];
			}
			ofstream debug_out(paths[n]);
			PrintDebugItems(debug_out, titles[n]);
			vector<double> items(titles[n].size());

			for(int i = -m_hmeshZ[s[0]]; i <= m_hmeshZ[s[0]]; i++){
				q[index[n][0]] = i+m_hmeshZ[s[0]];
				items[0] = i*m_deltaZ[s[0]];
				for(int j = -m_hmeshZ[s[1]]; j <= m_hmeshZ[s[1]]; j++){
					q[index[n][1]] = j+m_hmeshZ[s[1]];
					items[1] = j*m_deltaZ[s[1]];
					items[2] = 0;
					for(int k = 0; k < m_meshZ[s[2]]; k++){
						q[index[n][2]] = k;
						for(int l = 0; l < m_meshZ[s[3]]; l++){
							q[index[n][3]] = l;
							items[2] += m_dataZ[q[0]][q[1]][q[2]][q[3]];
						}
					}
					PrintDebugItems(debug_out, items);
				}
			}
			debug_out.close();
		}
	}
}

void Wigner4DManipulator::f_ExportWTrans(double Z, bool far, int jxy, bool killoffset)
{
	int prjidx[2], exidx[2];
	if(jxy == 0){
		prjidx[0] = WignerUVPrmV;
		prjidx[1] = WignerUVPrmv;
		exidx[0] = WignerUVPrmU;
		exidx[1] = WignerUVPrmu;
	}
	else{
		prjidx[0] = WignerUVPrmU;
		prjidx[1] = WignerUVPrmu;
		exidx[0] = WignerUVPrmV;
		exidx[1] = WignerUVPrmv;
	}
	int prjmesh[2], hmesh[2];
	for(int j = 0; j < 2; j++){
		prjmesh[j] = m_meshZ[prjidx[j]];
		hmesh[j] = m_hmeshZ[exidx[j]];
	}

	vector<vector<double>> data(2*hmesh[0]+1);
	for(int j = 0; j <= 2*hmesh[0]; j++){
		data[j].resize(2*hmesh[1]+1, 0.0);
	}
	vector<int> index(NumberWignerUVPrm);
	for(int i = -hmesh[0]; i <= hmesh[0]; i++){
		index[exidx[0]] = i+hmesh[0];
		for(int j = -hmesh[1]; j <= hmesh[1]; j++){
			index[exidx[1]] = j+hmesh[1];
			for(int k = 0; k < prjmesh[0]; k++){
				index[prjidx[0]] = k;
				for(int l = 0; l < prjmesh[1]; l++){
					index[prjidx[1]] = l;
					data[i+hmesh[0]][j+hmesh[1]] +=
						m_dataZ[index[0]][index[1]][index[2]][index[3]];
				}
			}
		}
	}

	if(!WigManipTrans.empty())
	{
		vector<string> xytitles{"X", "Y", "X'", "Y'"};
		ofstream debug_out[3];
		vector<string> titles[3];
		vector<double> items[3];

		titles[0] = vector<string> {xytitles[exidx[0]], xytitles[exidx[1]], "W"};
		titles[1] = vector<string> {xytitles[exidx[0]], "F"};
		titles[2] = vector<string>{xytitles[exidx[0]], "aF"};

		debug_out[0].open(WigManipTrans+"Wigner.dat");
		debug_out[1].open(WigManipTrans+"Sprof.dat");
//		debug_out[2].open(WigManipTrans+"Aprof.dat");

		for(int j = 0; j < 3; j++){
			if(debug_out[j].is_open()){
				PrintDebugItems(debug_out[j], titles[j]);
			}
			items[j].resize(titles[j].size());
		}

		vector<double> y(2*hmesh[1]+1);
		double zero = 0;
		Spline spl;
		int exhmesh = m_hmesh[exidx[1]];
		if(far){
			if(killoffset){
				exhmesh = hmesh[1];
			}
			else{
				exhmesh = (int)floor(0.5+m_delta[exidx[1]]*m_hmesh[exidx[1]]/m_deltaZ[exidx[1]]);
			}
		}
		vector<double> aflux(2*exhmesh+1, 0.0);
		for(int i = -hmesh[0]; i <= hmesh[0]; i++){
			items[0][0] = items[1][0] = i*m_deltaZ[exidx[0]];
			if(far && !killoffset){
				for(int j = -hmesh[1]; j <= hmesh[1]; j++){
					y[j+hmesh[1]] = j*m_deltaZ[exidx[1]]+items[0][0]/Z;
				}
				spl.SetSpline(2*hmesh[1]+1, &y, &data[i+hmesh[0]], true);
			}
			double flux = 0;
			for(int j = -exhmesh; j <= exhmesh; j++){
				items[0][1] = j*m_deltaZ[exidx[1]];
				if(far && !killoffset){
					items[0][2] = spl.GetValue(items[0][1], true, nullptr, &zero);
				}
				else{
					items[0][2] = data[i+hmesh[0]][j+exhmesh];
				}
				if(debug_out[0].is_open()){
					PrintDebugItems(debug_out[0], items[0]);
				}
				flux += items[0][2];
				aflux[j+exhmesh] += items[0][2];
			}
			items[1][1] = flux;
			if(debug_out[1].is_open()){
				PrintDebugItems(debug_out[1], items[1]);
			}
		}

		for(int j = -exhmesh; j <= exhmesh && debug_out[2].is_open(); j++){
			items[2][0] = j*m_deltaZ[exidx[1]];
			items[2][1] = aflux[j+exhmesh];
			PrintDebugItems(debug_out[2], items[2]);
		}

		for(int j = 0; j < 3; j++){
			if(debug_out[j].is_open()){
				debug_out[j].close();
			}
		}
	}
}

void Wigner4DManipulator::f_SetWindex(int j, double Z,
	int ifin[], bool far[], int k, int index[], double UV[], double *delta)
{
	int uvidx, UVidx, idsc, ipol;
	double Wp;
	if(j == 0){
		uvidx = WignerUVPrmu;
		UVidx = WignerUVPrmU;
	}
	else{
		uvidx = WignerUVPrmv;
		UVidx = WignerUVPrmV;
	}
	if(far[j]){
		idsc = UVidx;
		ipol = uvidx;
		Wp = (UV[j]+k*m_delta[idsc])/Z;
	}
	else{
		idsc = uvidx;
		ipol = UVidx;
		k = -k;
		Wp = UV[j]+k*m_delta[idsc]*Z;
	}

	index[idsc] = -k+m_hmesh[idsc];
	if(fabs(Wp) > m_delta[ipol]*m_hmesh[ipol]){
		index[ipol] = -1;
	}
	else{
		if(ifin[j] > 2){
			index[ipol] = (int)floor(Wp/m_delta[ipol]+0.5);
			index[ipol] = max(-m_hmesh[ipol]+1, index[ipol]);
		}
		else{
			index[ipol] = (int)floor(Wp/m_delta[ipol]);
		}
		index[ipol] = min(m_hmesh[ipol]-1, index[ipol]);
		*delta = Wp/m_delta[ipol]-index[ipol];
		index[ipol] += m_hmesh[ipol];
		if(ifin[j] > 2){
			index[ipol]--;
		}
	}
}


void WriteResults(SpectraConfig &spconf,
	int *scanindex, int nscans, vector<vector<double>> &scanvalues,
	int dimension, int vardimension,
	vector<string> &titles, vector<string> &units, vector<string> &details,
	vector<vector<double>> &vararray,
	vector<vector<vector<double>>> &data,
	vector<vector<vector<double>>> &vararrayd,
	vector<vector<vector<vector<double>>>> &datad,
	vector<vector<string>> &suppletitles,
	vector<vector<double>> &suppledata,
	string &result);

//  class WignerPropagator
WignerPropagator::WignerPropagator(SpectraSolver &spsolver)
	: SpectraSolver(spsolver)
{
	m_isxy[0] = m_isxy[1] = false;
	if(contains(m_orgtype, menu::XXpYYp)){
		m_type = WignerType4D;
		m_isxy[0] = m_isxy[1] = true;
	}
	else if(contains(m_orgtype, menu::XXpprj)){
		m_type = WignerType2DX;
		m_isxy[0] = true;
	}
	else if(contains(m_orgtype, menu::YYpprj)){
		m_type = WignerType2DY;
		m_isxy[1] = true;
	}
	else{
		throw runtime_error("Invalid settings.");
		return;
	}

	m_wigmanip.SetWavelength(wave_length(m_fixep));
}

void WignerPropagator::Propagate(
	vector<string> &subresults, vector<string> &categories)
{
	m_wigmanip.LoadData(m_pjoutput);
	vector<vector<double>> vararray;
	vector<vector<vector<vector<double>>>> CSD[2];
	double xymax[2];
	int xypoints[2];
	double *pxymax = nullptr;
	int *pxypoints = nullptr;
	bool normalized = false;

	if(m_confsel[gridspec_] == NormSlitLabel){
		normalized = true;
		if(m_confsel[csditem_] == CSDLabel){
			xymax[0] = m_confv[wnxrange_][0];
			xymax[1] = m_confv[wnyrange_][0];
		}
		else{
			xymax[0] = m_confv[snxrange_][0];
			xymax[1] = m_confv[snyrange_][0];
		}
	}
	else if(m_confsel[gridspec_] == FixedSlitLabel){
		if(m_confsel[csditem_] == CSDLabel){
			xymax[0] = m_confv[wxrange_][0];
			xymax[1] = m_confv[wyrange_][0];
		}
		else{
			xymax[0] = m_confv[sxrange_][0];
			xymax[1] = m_confv[syrange_][0];
		}
	}
	if(m_confsel[gridspec_] != AutomaticLabel){
		if(m_confsel[csditem_] == CSDLabel){
			xypoints[0] = (int)floor(m_conf[wxmesh_]+0.5);
			xypoints[1] = (int)floor(m_conf[wymesh_]+0.5);
		}
		else{
			xypoints[0] = (int)floor(m_conf[xmesh_]+0.5);
			xypoints[1] = (int)floor(m_conf[xmesh_]+0.5);
		}
		pxymax = xymax;
		pxypoints = xypoints;
	}
	m_wigmanip.GetCSD(m_conf[zprop_], vararray, CSD, pxymax, pxypoints, normalized);
	if(m_confsel[gridspec_] == AutomaticLabel){

	}

	subresults.push_back("");

	vector<int> index;
	if(m_confsel[csditem_] == CSDLabel){
		categories.push_back(CSDLabel);
		if(m_type == WignerType4D){
			index.push_back(Xavg_);
			index.push_back(Yavg_);
			index.push_back(Xdiff_);
			index.push_back(Ydiff_);
		}
		else if(m_type == WignerType2DX){
			index.push_back(Xavg_);
			index.push_back(Xdiff_);
		}
		else{
			index.push_back(Yavg_);
			index.push_back(Ydiff_);
		}
	}
	else{
		categories.push_back(SProfLabel);
	}
	

	vector<string> titles, units, details;
	vector<vector<double>> scanvalues, xyvar;
	vector<vector<vector<double>>> data, vararrayd;
	vector<vector<vector<vector<double>>>> datad;
	vector<vector<string>> suppletitles;
	vector<vector<double>> suppledata;

	titles.resize(index.size());
	units.resize(index.size());
	for(int j = 0; j < index.size(); j++){
		titles[j] = TitleLablesDetailed[index[j]];
		units[j] = UnitLablesDetailed[index[j]];
	}


	titles.push_back();
	units.push_back(UnitLablesDetailed[ModeNumber_]);
	titles.push_back(TitleLablesDetailed[ModalFlux_]);
	units.push_back(UnitLablesDetailed[ModalFlux_]);
	titles.push_back(TitleLablesDetailed[ModalIFlux_]);
	units.push_back(UnitLablesDetailed[ModalIFlux_]);
	xyvar.resize(1);
	xyvar[0].resize(modes);
	for(int p = 0; p < modes; p++){
		xyvar[0][p] = p;
	}
	WriteResults(spconf, nullptr, 1, scanvalues, 1, 1, titles, units,
		details, xyvar, data, vararrayd, datad, suppletitles, suppledata, result);
}

