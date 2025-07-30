#include "wigner4d_manipulator.h"
#include "numerical_common_definitions.h"
#include "spectra_input.h"
#include "output_utility.h"

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
string WigManipAfterOptics;
string WigManipCSDAfterOptics;
string WigManipCompare;
string WigManipCSDOptics;
string WigPropSpatialInt;
string WigPropSpatialOrg;
string WigPropGamma;

using namespace std;

int GetUV(int j)
{
	return j == 0 ? WignerUVPrmU : WignerUVPrmV;
}

int Getuv(int j)
{
	return j == 0 ? WignerUVPrmu : WignerUVPrmv;
}

Wigner4DManipulator::Wigner4DManipulator()
{
#ifdef _DEBUG
//	WigManipTrans = "..\\debug\\Transfer";
//	WigManipCompare = "..\\debug\\Compare.dat";
//	WigManipSpatial = "..\\debug\\Spatial2D.dat";
//	WigManipAngular = "..\\debug\\Angular2D.dat";
//	WigManipXXprj = "..\\debug\\XXprj.dat";
//	WigManipYYprj = "..\\debug\\YYprj.dat";
//	WigManipCSDx = "..\\debug\\CSDx.dat";
//	WigManipCSDy = "..\\debug\\CSDy.dat";
	WigManipCSDOptics = "..\\debug\\OpticsCSD.dat";
	WigManipAfterOptics = "..\\debug\\WignerAtOptics.dat";
	WigManipCSDAfterOptics = "..\\debug\\CSDAtOptics.dat";
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
	m_csdlevel = 2;
	for(int j = 0; j < 2; j++){
		m_Zwaist[j] = 0;
	}
	m_dfringe[0] = m_dfringe[1] = 1e-3;
	m_apteps = 0.01;
	m_aptpoints = 4;
	m_acclevel = 1;
	m_nproc = 1;
	m_rank = 0;
	m_thread = nullptr;
}

void Wigner4DManipulator::SetAccLevel(
		int xlevel, int xplevel, double eps, double dfringe)
{
	m_apteps = eps;
	m_aptpoints = 2<<xplevel;
	m_csdlevel = xplevel+1;
	m_acclevel = xlevel;
	for(int j = 0; j < 2; j++){
		m_dfringe[j] = dfringe;
	}
}

void Wigner4DManipulator::SetWavelength(double wavelength)
{
	m_lambda = wavelength;
}

bool Wigner4DManipulator::LoadData(string calctype,
	vector<vector<double>> *vararray, vector<double> *data)
{
	bool direct = calctype.empty();
	if(direct){
		// do not change type
	}
	else if(contains(calctype, menu::XXpYYp)){
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
		if(direct || m_type == WignerType4D){
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
		if(m_mesh[uvidx] > 1){
			m_delta[uvidx] = m_variables[uvidx][1]-m_variables[uvidx][0];
		}
		else{
			m_delta[uvidx] = 0;
		}
	}
	f_SetSteps(m_steps, m_mesh);

	if(data->size() != m_steps[NumberWignerUVPrm]){
		return false;
	}
	m_data = *data;

	GetVarIndices(m_varidx);

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

	GetVarIndices(m_varidx);

	for(int j = 0; j < m_varidx.size(); j++){
		int uvidx = m_varidx[j];
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

bool Wigner4DManipulator::Initialize()
{
	bool isok = true;
	for(int j = 0; j < NumberWignerUVPrm; j++){
		if(m_mesh[j]%2 == 0){
			isok = false;
		}
		m_hmesh[j] = (m_mesh[j]-1)/2;
	}
	f_GetSigma(nullptr, m_sigmaorg);

	m_active[0] = m_type == WignerType4D || m_type == WignerType2DX;
	m_active[1] = m_type == WignerType4D || m_type == WignerType2DY;

	m_DeltaUV[0] = m_delta[WignerUVPrmU]*(m_mesh[WignerUVPrmU]-1);
	m_DeltaUV[1] = m_delta[WignerUVPrmV]*(m_mesh[WignerUVPrmV]-1);
	m_Deltauv[0] = m_delta[WignerUVPrmu]*(m_mesh[WignerUVPrmu]-1);
	m_Deltauv[1] = m_delta[WignerUVPrmv]*(m_mesh[WignerUVPrmv]-1);

	double Border[2] = {1, 2};
	for(int j = 0; j < 2; j++){
		m_Zborder[j].clear();
		if(m_active[j]){
			m_Zborder[j].push_back(Border[0]*m_DeltaUV[j]/m_Deltauv[j]);
			m_Zborder[j].push_back(Border[1]*m_DeltaUV[j]/m_Deltauv[j]);
		}
	}

	return isok;
}

void Wigner4DManipulator::GetVarIndices(vector<int> &varidx)
{
	varidx.clear();
	if(m_type == WignerType4D){
		varidx.push_back(WignerUVPrmU);
		varidx.push_back(WignerUVPrmV);
		varidx.push_back(WignerUVPrmu);
		varidx.push_back(WignerUVPrmv);
	}
	else if(m_type == WignerType2DX){
		varidx.push_back(WignerUVPrmU);
		varidx.push_back(WignerUVPrmu);
	}
	else{
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
	fill(fdens.begin(), fdens.end(), 0.0);

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

void Wigner4DManipulator::GetAngularProfile(vector<double> &fdensa)
{
	double dq;
	if(m_type == WignerType4D){
		dq = m_delta[WignerUVPrmU]*m_delta[WignerUVPrmV];
	}
	else{
		dq = m_type == WignerType2DX ? m_delta[WignerUVPrmU] : m_delta[WignerUVPrmV];
	}

	fdensa.resize(m_mesh[WignerUVPrmu]*m_mesh[WignerUVPrmv]);
	fill(fdensa.begin(), fdensa.end(), 0.0);

	int n[4];
	for(n[0] = 0; n[0] < m_mesh[WignerUVPrmU]; n[0]++){
		for(n[1] = 0; n[1] < m_mesh[WignerUVPrmV]; n[1]++){
			for(n[2] = 0; n[2] < m_mesh[WignerUVPrmu]; n[2]++){
				for(n[3] = 0; n[3] < m_mesh[WignerUVPrmv]; n[3]++){
					fdensa[n[2]+n[3]*m_mesh[WignerUVPrmu]] += dq*GetValue(n);
				}
			}
		}
	}
}

void Wigner4DManipulator::GetBeamSizeAt(double Z, double *size)
{
	for(int j = 0; j < 2; j++){
		double Zt = Z-m_Zwaist[j];
		int iUV = GetUV(j);
		int iuv = Getuv(j);
		size[j] = sqrt(hypotsq(m_sigmaorg[iUV], m_sigmaorg[iuv]*Zt));
	}
}

void Wigner4DManipulator::Transfer(double Z, double *dxytgt,
	PrintCalculationStatus *calcstats, double *aptmin, double *aptmax, double *dfringe)
{
	for(int j = 0; j < 2; j++){
		m_Zt[j] = Z-m_Zwaist[j];
		int iUV = GetUV(j);
		int iuv = Getuv(j);
		double sizeZ = sqrt(hypotsq(m_sigmaorg[iUV], m_sigmaorg[iuv]*m_Zt[j]));
		if(m_sigmaorg[iUV] > 0){
			m_sdiv[j] = m_sigmaorg[iuv]*m_sigmaorg[iUV]/sizeZ;
		}
		else{
			m_sdiv[j] = 0;
		}
	}
	f_SetGridUV(dxytgt, aptmin, aptmax, dfringe);

	int ifin[2] = {1, 1};
	int intpolidx[2] = {WignerUVPrmU, WignerUVPrmV};

	vector<double> a[2];
	for(int j = 0; j < 2; j++){
		if(m_active[j]){
			ifin[j] = 3; // interpolation rank, linear: 2, quadratic: 3
		}
		if(m_isfar[j]){
			intpolidx[j] = Getuv(j);
		}
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
				fill(m_dataZ[i][j][k].begin(), m_dataZ[i][j][k].end(), 0.0);
			}
		}
	}

	double UV[2]; // coordinate in the target Z
	double delta[2];
	int index[NumberWignerUVPrm] = {0, 0, 0, 0};
	int gindex[NumberWignerUVPrm];

	if(calcstats != nullptr){
		calcstats->SetSubstepNumber(1, m_meshZ[WignerUVPrmU]*m_meshZ[WignerUVPrmV]/m_nproc);
	}

	vector<int> steps, inistep, finstep;
	mpi_steps(m_meshZ[WignerUVPrmU], m_meshZ[WignerUVPrmV], m_nproc, &steps, &inistep, &finstep);

	double sum = 0;
	m_sigmaZ[0] = m_sigmaZ[1] = 0;
	for(int i = -m_hmeshZ[WignerUVPrmU]; i <= m_hmeshZ[WignerUVPrmU]; i++){
		int ii = i+m_hmeshZ[WignerUVPrmU];
		UV[0] = i*m_deltaZ[WignerUVPrmU];
		for(int j = -m_hmeshZ[WignerUVPrmV]; j <= m_hmeshZ[WignerUVPrmV]; j++){
			int jj = j+m_hmeshZ[WignerUVPrmV];
			UV[1] = j*m_deltaZ[WignerUVPrmV];
			int nstep = ii*m_meshZ[WignerUVPrmV]+jj;
			if(nstep < inistep[m_rank] || nstep > finstep[m_rank]){
				continue;
			}
			double sumr  = 0;
			for(int k = -m_hmeshZ[WignerUVPrmu]; k <= m_hmeshZ[WignerUVPrmu]; k++){
				int kk = k+m_hmeshZ[WignerUVPrmu];
				if(m_active[0]){
					f_SetWindex(0, m_Zt[0], ifin, k, index, UV, &delta[0]);
					if(index[WignerUVPrmu] < 0 || index[WignerUVPrmU] < 0){
						continue;
					}
				}
				for(int l = -m_hmeshZ[WignerUVPrmv]; l <= m_hmeshZ[WignerUVPrmv]; l++){
					int ll = l+m_hmeshZ[WignerUVPrmv];
					if(m_active[1]){
						f_SetWindex(1, m_Zt[1], ifin, l, index, UV, &delta[1]);
						if(index[WignerUVPrmv] < 0 || index[WignerUVPrmV] < 0){
							continue;
						}
					}
					for(int j = 0; j < 2; j++){
						setinterpolant(ifin[j], delta[j], a[j]);
					}
					m_dataZ[ii][jj][kk][ll] = 0;
					for(int i = 0; i < NumberWignerUVPrm; i++){
						gindex[i] = index[i];
					}
					for(int ix = 0; ix < ifin[0]; ix++){
						gindex[intpolidx[0]] = index[intpolidx[0]]+ix;
						for(int iy = 0; iy < ifin[1]; iy++){
							gindex[intpolidx[1]] = index[intpolidx[1]]+iy;
							m_dataZ[ii][jj][kk][ll] += GetValue(gindex)*a[0][ix]*a[1][iy];
						}
					}
					sumr += m_dataZ[ii][jj][kk][ll];
				}
			}
			for(int jxy = 0; jxy < 2; jxy++){
				m_sigmaZ[jxy] += UV[jxy]*UV[jxy]*sumr;
			}
			sum += sumr;

			if(calcstats != nullptr){
				calcstats->AdvanceStep(1);
			}
		}
	}

	if(m_nproc > 1){
		double tmp = sum;
		double tmpsig[2] = {m_sigmaZ[0], m_sigmaZ[1]};
		if(m_thread != nullptr){
			m_thread->Allreduce(&tmp, &sum, 1, MPI_DOUBLE, MPI_SUM, m_rank);
			m_thread->Allreduce(tmpsig, m_sigmaZ, 2, MPI_DOUBLE, MPI_SUM, m_rank);
		}
		else{
			MPI_Allreduce(&tmp, &sum, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
			MPI_Allreduce(tmpsig, m_sigmaZ, 2, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
		}
		int nws = m_meshZ[WignerUVPrmu]*m_meshZ[WignerUVPrmv];
		double *wsmpi = new double[nws];
		for(int i = 0; i < m_meshZ[WignerUVPrmU]; i++){
			for(int j = 0; j < m_meshZ[WignerUVPrmV]; j++){
				int nstep = i*m_meshZ[WignerUVPrmV]+j;
				int currrank = get_mpi_rank(nstep, m_nproc, inistep, finstep);
				if(m_rank == currrank){
					for(int k = 0; k < m_meshZ[WignerUVPrmu]; k++){
						for(int l = 0; l < m_meshZ[WignerUVPrmv]; l++){
							wsmpi[k*m_meshZ[WignerUVPrmv]+l] = m_dataZ[i][j][k][l];
						}
					}
				}
				if(m_thread != nullptr){
					m_thread->Bcast(wsmpi, nws, MPI_DOUBLE, currrank, m_rank);
				}
				else{
					MPI_Bcast(wsmpi, nws, MPI_DOUBLE, currrank, MPI_COMM_WORLD);
				}
				if(m_rank != currrank){
					for(int k = 0; k < m_meshZ[WignerUVPrmu]; k++){
						for(int l = 0; l < m_meshZ[WignerUVPrmv]; l++){
							m_dataZ[i][j][k][l] = wsmpi[k*m_meshZ[WignerUVPrmv]+l];
						}
					}
				}
			}
		}
		delete[] wsmpi;
	}

	if(sum > 0){
		for(int jxy = 0; jxy < 2; jxy++){
			m_sigmaZ[jxy] = sqrt(max(0.0, m_sigmaZ[jxy]/sum));
		}
	}

#ifdef _DEBUG
	f_Export(false);
#endif


	if(calcstats != nullptr){
		calcstats->AdvanceStep(0);
	}
}

void Wigner4DManipulator::GetCSD(double sigma[], vector<vector<double>> &vararray, 
	vector<vector<double>> &F, vector<vector<vector<vector<double>>>> *CSD,
	PrintCalculationStatus *calcstats)
{
	for(int j = 0; j < 2; j++){
		sigma[j] = m_sigmaZ[j];
	}

	int nfft[NumberWignerUVPrm] = {1, 1, 1, 1};
	int hmeshfft[NumberWignerUVPrm] = {0, 0, 0, 0};
	double deltaZ[NumberWignerUVPrm] = {0, 0, 0, 0};
	double slim;
	for(int j = 0; j < NumberWignerUVPrm; j++){
		m_meshfft[j] = 1;
		if(j == WignerUVPrmu || j == WignerUVPrmv){
			if(m_hmeshZ[j] > 0){
				f_GetFFTCSD(j, nfft, deltaZ);
				double div = j == WignerUVPrmu ? m_sdiv[0] : m_sdiv[1];
				slim = 1e3*GAUSSIAN_MAX_REGION*m_lambda/PI2/(div*1e-3);
				hmeshfft[j] = (int)floor(0.5+slim/deltaZ[j]);
				m_meshfft[j] = 2*hmeshfft[j]+1;
				if(m_meshfft[j] > nfft[j]-1){
					m_meshfft[j] = nfft[j]-1;
					hmeshfft[j] = (m_meshfft[j]-1)/2;
				}
			}
		}
		else{
			deltaZ[j] = m_deltaZ[j];
			m_meshfft[j] = m_meshZ[j];
		}
	}

	FastFourierTransform *fft;
	double *ws = nullptr, **ws2 = nullptr;
	int ndim = f_AllocFFTWS(&fft, nfft, &ws, &ws2);

	vararray.clear();
	vararray.resize(NumberWignerUVPrm);
	for(int j = 0; j < NumberWignerUVPrm; j++){
		vararray[j].resize(m_meshfft[j]);
		if(j == WignerUVPrmu || j == WignerUVPrmv){
			for(int n = -hmeshfft[j]; n <= hmeshfft[j]; n++){
				vararray[j][n+hmeshfft[j]] = n*deltaZ[j];
			}
		}
		else{
			for(int n = -m_hmeshZ[j]; n <= m_hmeshZ[j]; n++){
				vararray[j][n+m_hmeshZ[j]] = n*deltaZ[j];
			}
		}
	}

	for(int n = 0; n < 2 && CSD != nullptr; n++){
		CSD[n].resize(m_meshZ[WignerUVPrmU]);
		for(int i = 0; i < m_meshfft[WignerUVPrmU]; i++){
			CSD[n][i].resize(m_meshfft[WignerUVPrmV]);
			for(int j = 0; j < m_meshfft[WignerUVPrmV]; j++){
				CSD[n][i][j].resize(m_meshfft[WignerUVPrmu]);
				for(int k = 0; k < m_meshfft[WignerUVPrmu]; k++){
					CSD[n][i][j][k].resize(m_meshfft[WignerUVPrmv], 0.0);
				}
			}
		}
	}
	F.resize(m_meshZ[WignerUVPrmU]);
	for(int i = 0; i < m_meshfft[WignerUVPrmU]; i++){
		F[i].resize(m_meshfft[WignerUVPrmV]);
	}

	if(calcstats != nullptr){
		calcstats->SetSubstepNumber(1, m_meshZ[WignerUVPrmU]*m_meshZ[WignerUVPrmV]);
	}

	vector<int> steps, inistep, finstep;
	mpi_steps(m_meshZ[WignerUVPrmU], m_meshZ[WignerUVPrmV], m_nproc, &steps, &inistep, &finstep);

	double UV[2];
	for(int i = -m_hmeshZ[WignerUVPrmU]; i <= m_hmeshZ[WignerUVPrmU]; i++){
		int ii = i+m_hmeshZ[WignerUVPrmU];
		UV[0] = i*m_deltaZ[WignerUVPrmU];
		for(int j = -m_hmeshZ[WignerUVPrmV]; j <= m_hmeshZ[WignerUVPrmV]; j++){
			int jj = j+m_hmeshZ[WignerUVPrmV];
			UV[1] = j*m_deltaZ[WignerUVPrmV];
			F[ii][jj] = f_LoadWS(ii, jj, nfft, ndim, ws, ws2, m_deltaZ);

			int nstep = ii*m_meshZ[WignerUVPrmV]+jj;
			if(nstep < inistep[m_rank] || nstep > finstep[m_rank]){
				continue;
			}

			if(CSD == nullptr){
				if(calcstats != nullptr){
					calcstats->AdvanceStep(1);
				}
				continue;
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
				if(kk < 0 || kk >= m_meshfft[WignerUVPrmu]){
					continue;
				}
				if(m_isfar[0] && fabs(m_Zt[0]) > 0){
					phase[0] = fft_index(k, nfft[WignerUVPrmu], 1)*deltaZ[WignerUVPrmu]*UV[0]*1e-6/m_Zt[0];
					// mm^2 -> m^2
				}
				for(int l = 0; l < nfft[WignerUVPrmv]; l++){
					int ll = l;
					if(nfft[WignerUVPrmv] > 1){
						ll = fft_index(l, nfft[WignerUVPrmv], 1)+hmeshfft[WignerUVPrmv];
					}
					if(ll < 0 || ll >= m_meshfft[WignerUVPrmv]){
						continue;
					}
					if(m_isfar[1] && fabs(m_Zt[0]) > 0){
						phase[1] = fft_index(l, nfft[WignerUVPrmv], 1)*deltaZ[WignerUVPrmv]*UV[1]*1e-6/m_Zt[1];
						// mm^2 -> m^2
					}
					phs = -(phase[0]+phase[1])*PI2/m_lambda;
					csn[0] = cos(phs);
					csn[1] = sin(phs);
					if(ndim == 2){
						CSD[0][ii][jj][kk][ll] = sqrt(hypotsq(ws2[k][2*l], ws2[k][2*l+1]));
						CSD[1][ii][jj][kk][ll] = 0;
						if(CSD[0][ii][jj][kk][ll] > 0){
							CSD[1][ii][jj][kk][ll] = atan2(ws2[k][2*l+1], ws2[k][2*l])+phs;
						}
					}
					else{
						CSD[0][ii][jj][kk][ll] = sqrt(hypotsq(ws[2*(k+l)], ws[2*(k+l)+1]));
						CSD[1][ii][jj][kk][ll] = 0;
						if(CSD[0][ii][jj][kk][ll] > 0){
							CSD[1][ii][jj][kk][ll] = atan2(ws[2*(k+l)+1], ws[2*(k+l)])+phs;
						}
					}
				}
			}

			if(calcstats != nullptr){
				calcstats->AdvanceStep(1);
			}
		}
	}

	delete fft;
	if(ndim == 2){
		for(int n = 0; n < nfft[WignerUVPrmu]; n++){
			delete[] ws2[n];
		}
		delete[] ws2;
	}
	else{
		delete[] ws;
	}

	if(m_nproc > 1 && CSD != nullptr){
		int nws = m_meshfft[WignerUVPrmu]*m_meshfft[WignerUVPrmv];
		double *wsmpi = new double[2*nws];
		for(int i = 0; i < m_meshZ[WignerUVPrmU]; i++){
			for(int j = 0; j < m_meshZ[WignerUVPrmV]; j++){
				int nstep = i*m_meshZ[WignerUVPrmV]+j;
				int currrank = get_mpi_rank(nstep, m_nproc, inistep, finstep);
				if(m_rank == currrank){
					for(int k = 0; k < m_meshfft[WignerUVPrmu]; k++){
						for(int l = 0; l < m_meshfft[WignerUVPrmv]; l++){
							for(int reim = 0; reim < 2; reim++){
								wsmpi[2*(k*m_meshfft[WignerUVPrmv]+l)+reim] = CSD[reim][i][j][k][l];
							}
						}
					}
				}
				if(m_thread != nullptr){
					m_thread->Bcast(wsmpi, 2*nws, MPI_DOUBLE, currrank, m_rank);
				}
				else{
					MPI_Bcast(wsmpi, 2*nws, MPI_DOUBLE, currrank, MPI_COMM_WORLD);
				}
				if(m_rank != currrank){
					for(int k = 0; k < m_meshfft[WignerUVPrmu]; k++){
						for(int l = 0; l < m_meshfft[WignerUVPrmv]; l++){
							for(int reim = 0; reim < 2; reim++){
								CSD[reim][i][j][k][l] = wsmpi[2*(k*m_meshfft[WignerUVPrmv]+l)+reim];
							}
						}
					}
				}
			}
		}
		delete[] wsmpi;
	}

#ifdef _DEBUG
	if(m_rank == 0){
		if(!WigManipCSDx.empty() && nfft[WignerUVPrmu] > 1 && CSD != nullptr){
			vector<string> titles{"X", "DX", "F", "Real", "Imag"};
			vector<double> items(titles.size());
			ofstream debug_out(WigManipCSDx);
			PrintDebugItems(debug_out, titles);
			for(int i = 0; i < m_meshfft[WignerUVPrmU]; i++){
				items[0] = vararray[WignerUVPrmU][i];
				for(int k = 0; k < m_meshfft[WignerUVPrmu]; k++){
					items[1] = vararray[WignerUVPrmu][k];
					items[3] = items[4] = 0;
					for(int j = 0; j < m_meshfft[WignerUVPrmV]; j++){
						for(int l = 0; l < m_meshfft[WignerUVPrmv]; l++){
							items[3] += CSD[0][i][j][k][l];
							items[4] += CSD[1][i][j][k][l];
						}
					}
					items[2] = sqrt(hypotsq(items[3], items[4]));
					PrintDebugItems(debug_out, items);
				}
			}
		}
		if(!WigManipCSDy.empty() && nfft[WignerUVPrmv] > 1 && CSD != nullptr){
			vector<string> titles{"Y", "DY", "F", "Real", "Imag"};
			vector<double> items(titles.size());
			ofstream debug_out(WigManipCSDy);
			PrintDebugItems(debug_out, titles);
			for(int j = 0; j < m_meshfft[WignerUVPrmV]; j++){
				items[0] = vararray[WignerUVPrmV][j];
				for(int l = 0; l < m_meshfft[WignerUVPrmv]; l++){
					items[1] = vararray[WignerUVPrmv][l];
					items[3] = items[4] = 0;
					for(int i = 0; i < m_meshfft[WignerUVPrmU]; i++){
						for(int k = 0; k < m_meshfft[WignerUVPrmu]; k++){
							items[3] += CSD[0][i][j][k][l];
							items[4] += CSD[1][i][j][k][l];
						}
					}
					items[2] = sqrt(hypotsq(items[3], items[4]));
					PrintDebugItems(debug_out, items);
				}
			}
		}
	}
	MPI_Barrier(MPI_COMM_WORLD);
#endif

	if(calcstats != nullptr){
		calcstats->AdvanceStep(0);
	}
}

void Wigner4DManipulator::GetMeshPoints(vector<int> &hmesh)
{
	for(int j = 0; j < NumberWignerUVPrm; j++){
		hmesh[j] = m_meshfft[j];
	}
}

void Wigner4DManipulator::GetDeltaZ(double deltaZ[])
{
	for(int j = 0; j < NumberWignerUVPrm; j++){
		deltaZ[j] = m_deltaZ[j];
	}
}

void Wigner4DManipulator::OpticalElement(double Z, double *flen, double fringe,
	vector<vector<double>> &position, vector<vector<double>> &aperture,
	PrintCalculationStatus *calcstats)
{
	double finv[2] = {0, 0};
	if(flen != nullptr){
		Transfer(Z, nullptr, calcstats);
		for(int j = 0; j < 2; j++){
			finv[j] = 1/flen[j];
		}
		if(calcstats != nullptr){
			calcstats->AdvanceStep(0);
		}
	}
	else{
		f_SetSlit(fringe, position, aperture);
		Transfer(Z, nullptr, calcstats, m_aptmin, m_aptmax, m_dfringe);
		f_InsertSlit(calcstats);
	}

	vector<vector<double>> vararray;
	vector<double> data;

	GetWignerAtWaist(Z, finv, vararray, data, calcstats);
	m_dataZ.clear(); m_dataZ.shrink_to_fit();
	LoadData("", &vararray, &data);
	Initialize();
}

void Wigner4DManipulator::GetWaistPosition(double rho[], double Zwaist[])
{
	double UV[2], uv[2];
	double	divsum[2] = {0, 0};
	Zwaist[0] = Zwaist[1] = 0;
	for(int i = -m_hmeshZ[WignerUVPrmU]; i <= m_hmeshZ[WignerUVPrmU]; i++){
		int ii = i+m_hmeshZ[WignerUVPrmU];
		UV[0] = i*m_deltaZ[WignerUVPrmU];
		for(int j = -m_hmeshZ[WignerUVPrmV]; j <= m_hmeshZ[WignerUVPrmV]; j++){
			int jj = j+m_hmeshZ[WignerUVPrmV];
			UV[1] = j*m_deltaZ[WignerUVPrmV];
			for(int k = -m_hmeshZ[WignerUVPrmu]; k <= m_hmeshZ[WignerUVPrmu]; k++){
				int kk = k+m_hmeshZ[WignerUVPrmu];
				uv[0] = k*m_deltaZ[WignerUVPrmu];
				if(m_isfar[0]){
					uv[0] += UV[0]*rho[0];
				}
				for(int l = -m_hmeshZ[WignerUVPrmv]; l <= m_hmeshZ[WignerUVPrmv]; l++){
					uv[1] = l*m_deltaZ[WignerUVPrmv];
					if(m_isfar[1]){
						uv[1] += UV[1]*rho[1];
					}
					int ll = l+m_hmeshZ[WignerUVPrmv];
					for(int jxy = 0; jxy < 2; jxy++){
						divsum[jxy] += uv[jxy]*uv[jxy]*m_dataZ[ii][jj][kk][ll];
						Zwaist[jxy] += uv[jxy]*UV[jxy]*m_dataZ[ii][jj][kk][ll];
					}
				}
			}
		}
	}
	for(int jxy = 0; jxy < 2; jxy++){
		if(divsum[jxy] > 0){
			Zwaist[jxy] /= divsum[jxy];
		}
	}
}

void Wigner4DManipulator::GetWignerAtWaist(double Z, double finv[],
	vector<vector<double>> &vararray, vector<double> &data,
	PrintCalculationStatus *calcstats)
{
	double rho[2];
	for(int j = 0; j < 2; j++){
		if(m_isfar[j]){
			rho[j] = 1/m_Zt[j]-finv[j];
		}
		else{
			rho[j] = -finv[j];
		}
	}

	int hmesh[NumberWignerUVPrm], mesh[NumberWignerUVPrm];
	double hDelta[NumberWignerUVPrm], delta[NumberWignerUVPrm];
	for(int j = 0; j < NumberWignerUVPrm; j++){
		hDelta[j] = m_hmeshZ[j]*m_deltaZ[j];
		hmesh[j] = 0;
		delta[j] = 0;
	}

	bool direct[2] = {true, true};
	for(int j = 0; j < 2; j++){
		if(!m_active[j]){
			continue;
		}
		int UV = GetUV(j);
		int uv = Getuv(j);
		direct[j] = rho[j]*rho[j] < hDelta[uv]*m_deltaZ[uv]/(hDelta[UV]*m_deltaZ[UV]);

		if(direct[j]){
			m_Zwaist[j] = Z;
			delta[uv] = m_deltaZ[uv];
			delta[UV] = m_deltaZ[UV];
			hmesh[UV] = m_hmeshZ[UV];
			hDelta[uv] += fabs(rho[j])*hDelta[UV];
			hmesh[uv] = (int)floor(0.5+hDelta[uv]/delta[uv]);
		}
		else{
			delta[uv] = m_deltaZ[UV]*fabs(rho[j]);
			delta[UV] = m_deltaZ[uv]/fabs(rho[j]);
			hmesh[UV] = m_hmeshZ[uv];
			hDelta[UV] += hDelta[uv]/fabs(rho[j]);
			hmesh[uv] = (int)floor(0.5+hDelta[UV]/m_deltaZ[UV]);
			m_Zwaist[j] = Z-1/rho[j];
		}
	}

	for(int j = 0; j < NumberWignerUVPrm; j++){
		mesh[j] = 2*hmesh[j]+1;
	}

	for(int j = 0; j < NumberWignerUVPrm; j++){
		m_ifin[j] = 1;
		m_a[j].resize(1, 1.0);
	}
	for(int j = 0; j < 2; j++){
		if(m_active[j]){
			int uvidx[2] = {GetUV(j), Getuv(j)};
			for(int i = 0; i < 2; i++){
				int UV = uvidx[i];
				m_ifin[UV] = 2;
				m_a[UV].resize(m_ifin[UV]);
			}
		}
	}

	int stepsZ[NumberWignerUVPrm+1], index[NumberWignerUVPrm];
	f_SetSteps(stepsZ, mesh);
	data.resize(stepsZ[NumberWignerUVPrm]);

	if(calcstats != nullptr){
		calcstats->SetSubstepNumber(1, mesh[WignerUVPrmv]*mesh[WignerUVPrmu]);
	}

	vector<bool> nonzero[NumberWignerUVPrm];
	for(int n = 0; n < NumberWignerUVPrm; n++){
		nonzero[n].resize(hmesh[n]+1, true);
	}

	double var[NumberWignerUVPrm];
	for(int l = -hmesh[WignerUVPrmv]; l <= hmesh[WignerUVPrmv]; l++){
		int ll = index[3] = l+hmesh[WignerUVPrmv];
		var[3] = l*delta[WignerUVPrmv];
		for(int k = -hmesh[WignerUVPrmu]; k <= hmesh[WignerUVPrmu]; k++){
			int kk = index[2] = k+hmesh[WignerUVPrmu];
			var[2] = k*delta[WignerUVPrmu];
			for(int j = -hmesh[WignerUVPrmV]; j <= hmesh[WignerUVPrmV]; j++){
				int jj = index[1] = j+hmesh[WignerUVPrmV];
				var[1] = j*delta[WignerUVPrmV];
				if(!direct[1]){
					var[1] += var[3]/rho[1];
				}
				for(int i = -hmesh[WignerUVPrmU]; i <= hmesh[WignerUVPrmU]; i++){
					int ii = index[0] = i+hmesh[WignerUVPrmU];
					var[0] = i*delta[WignerUVPrmU];
					if(!direct[0]){
						var[0] += var[2]/rho[0];
					}
					int total = GetTotalIndex(index, stepsZ);
					data[total] = f_GetWignerAtZ(rho, var);
					if(data[total] != 0){
						nonzero[0][abs(i)] = false;
						nonzero[1][abs(j)] = false;
						nonzero[2][abs(k)] = false;
						nonzero[3][abs(l)] = false;
					}
				}
			}
			if(calcstats != nullptr){
				calcstats->AdvanceStep(1);
			}
		}
	}
	if(calcstats != nullptr){
		calcstats->AdvanceStep(0);
	}

	int shmesh[NumberWignerUVPrm];
	for(int n = 0; n < NumberWignerUVPrm; n++){
		for(int j = hmesh[n]; j >= 0; j--){
			if(!nonzero[n][j]){
				shmesh[n] = j;
				break;
			}
		}
		mesh[n] = 2*shmesh[n]+1;
	}
	int sstepsZ[NumberWignerUVPrm+1];
	f_SetSteps(sstepsZ, mesh);

	int sindex[NumberWignerUVPrm];
	for(int l = -shmesh[WignerUVPrmv]; l <= shmesh[WignerUVPrmv]; l++){
		index[3] = l+hmesh[WignerUVPrmv];
		sindex[3] = l+shmesh[WignerUVPrmv];
		for(int k = -shmesh[WignerUVPrmu]; k <= shmesh[WignerUVPrmu]; k++){
			index[2] = k+hmesh[WignerUVPrmu];
			sindex[2] = k+shmesh[WignerUVPrmu];
			for(int j = -shmesh[WignerUVPrmV]; j <= shmesh[WignerUVPrmV]; j++){
				index[1] = j+hmesh[WignerUVPrmV];
				sindex[1] = j+shmesh[WignerUVPrmV];
				for(int i = -shmesh[WignerUVPrmU]; i <= shmesh[WignerUVPrmU]; i++){
					index[0] = i+hmesh[WignerUVPrmU];
					sindex[0] = i+shmesh[WignerUVPrmU];
					int stotal = GetTotalIndex(sindex, sstepsZ);
					int total = GetTotalIndex(index, stepsZ);
					data[stotal] = data[total];
				}
			}
		}
	}

	vararray.resize(NumberWignerUVPrm);
	for(int j = 0; j < NumberWignerUVPrm; j++){
		vararray[j].resize(mesh[j]);
		for(int n = -shmesh[j]; n <= shmesh[j]; n++){
			vararray[j][n+shmesh[j]] = n*delta[j];
		}
	}
	data.resize(sstepsZ[NumberWignerUVPrm]);
}

void Wigner4DManipulator::GetWignerAtWaistTest(double Z)
{
	double rho[2] = {1/Z, 1/Z};

	for(int j = 0; j < NumberWignerUVPrm; j++){
		m_ifin[j] = 1;
		m_a[j].resize(1, 1.0);
	}
	for(int j = 0; j < 2; j++){
		if(m_active[j]){
			int uvidx[2] = {GetUV(j), Getuv(j)};
			for(int i = 0; i < 2; i++){
				int UV = uvidx[i];
				m_ifin[UV] = 2;
				m_a[UV].resize(m_ifin[UV]);
			}
		}
	}

#ifdef _DEBUG
	vector<string> titles{"X", "Y", "X'", "Y'", "W", "W2", "Diff"};
	ofstream debug_out;
	vector<double> items(titles.size());
	if(!WigManipCompare.empty()){
		debug_out.open(WigManipCompare);
		PrintDebugItems(debug_out, titles);
	}
	double fmax = m_dataZ[m_hmeshZ[WignerUVPrmU]][m_hmeshZ[WignerUVPrmV]][m_hmeshZ[WignerUVPrmu]][m_hmeshZ[WignerUVPrmv]];
#endif

	double var[NumberWignerUVPrm], W;
	int m[NumberWignerUVPrm];
	for(int l = -m_hmesh[WignerUVPrmv]; l <= m_hmesh[WignerUVPrmv]; l++){
		int ll = m[3] = l+m_hmesh[WignerUVPrmv];
		var[3] = l*m_delta[WignerUVPrmv];
		for(int k = -m_hmesh[WignerUVPrmu]; k <= m_hmesh[WignerUVPrmu]; k++){
			int kk = m[2] = k+m_hmesh[WignerUVPrmu];
			var[2] = k*m_delta[WignerUVPrmu];
			for(int j = -m_hmesh[WignerUVPrmV]; j <= m_hmesh[WignerUVPrmV]; j++){
				int jj = m[1] = j+m_hmesh[WignerUVPrmV];
				var[1] = j*m_delta[WignerUVPrmV]+var[3]/rho[1];
				for(int i = -m_hmesh[WignerUVPrmU]; i <= m_hmesh[WignerUVPrmU]; i++){
					int ii = m[0] = i+m_hmesh[WignerUVPrmU];
					var[0] = i*m_delta[WignerUVPrmU]+var[2]/rho[0];
					W = f_GetWignerAtZ(rho, var);
#ifdef _DEBUG
					if(!WigManipCompare.empty()){
						bool isdump = abs(i)%2 == 0 && abs(k)%2 == 0 && abs(j)%2 == 0 && abs(l)%2 == 0;
						if(isdump){
							items[0] = i*m_delta[WignerUVPrmU];
							items[1] = j*m_delta[WignerUVPrmV];
							for(int n = 2; n < 4; n++){
								items[n] = var[n];
							}
							items[4] = GetValue(m);
							items[5] = W;
							items[6] = fabs(items[5]-items[4])/fmax;
							PrintDebugItems(debug_out, items);
						}
					}
#endif
				}
			}
		}
	}

#ifdef _DEBUG
	if(!WigManipCompare.empty()){
		debug_out.close();
	}
#endif

}

void Wigner4DManipulator::SetMPI(int procs, int rank, MPIbyThread *thread)
{
	m_nproc = procs;
	m_rank = rank;
	m_thread = thread;
}

void Wigner4DManipulator::SetRay(bool spherical)
{
	int n[4];
	for(n[0] = 0; n[0] < m_mesh[WignerUVPrmU]; n[0]++){
		for(n[1] = 0; n[1] < m_mesh[WignerUVPrmV]; n[1]++){
			for(n[2] = 0; n[2] < m_mesh[WignerUVPrmu]; n[2]++){
				for(n[3] = 0; n[3] < m_mesh[WignerUVPrmv]; n[3]++){
					int index = GetTotalIndex(n);
					if(!spherical && n[2] == m_hmesh[WignerUVPrmu] && n[3] == m_hmesh[WignerUVPrmv]){
						m_data[index] = 1;
					}
					if(spherical && n[0] == m_hmesh[WignerUVPrmU] && n[1] == m_hmesh[WignerUVPrmV]){
						m_data[index] = 1;
					}
					else{
						m_data[index] = 0;
					}
				}
			}
		}
	}
}

void Wigner4DManipulator::SetSourceWigner(vector<double> &Zwaist, vector<double> &sigma,
		vector<vector<double>> &vararray, vector<double> &wigner, bool isget)
{
	if(isget){
		vararray = m_variables;
		wigner = m_data;
		for(int j = 0; j < 2; j++){
			Zwaist[j] = m_Zwaist[j];
		}
		for(int j = 0; j < NumberWignerUVPrm; j++){
			if(vararray[j].size() == 0){
				vararray[j].resize(1, 0.0);
			}
			sigma[j] = m_sigmaorg[j];
		}
	}
	else{
		for(int j = 0; j < 2; j++){
			m_Zwaist[j] = Zwaist[j];
		}
		m_dataZ.clear(); m_dataZ.shrink_to_fit();
		LoadData("", &vararray, &wigner);
		Initialize();
	}
}

double Wigner4DManipulator::f_GetWignerAtZ(double rho[], double var[])
{
	int index[NumberWignerUVPrm] = {0, 0, 0, 0};
	double delta[NumberWignerUVPrm], rvar[NumberWignerUVPrm];
	for(int j = 0; j < NumberWignerUVPrm; j++){
		rvar[j] = var[j];
	}

	for(int j = 0; j < 2; j++){
		if(m_active[j]){
			int uvidx[2] = {GetUV(j), Getuv(j)};
			rvar[uvidx[1]] -= rvar[uvidx[0]]*rho[j];
			for(int i = 0; i < 2; i++){
				int UV = uvidx[i];
				interpolant2d(m_ifin[UV], rvar[UV], m_deltaZ[UV], m_hmeshZ[UV], &delta[UV], &index[UV]);
				if(index[UV] < 0){
					return 0;
				}
				setinterpolant(m_ifin[UV], delta[UV], m_a[UV]);
			}
		}
	}

	double W = 0, ar[4];
	int m[NumberWignerUVPrm];
	for(int i = 0; i < m_ifin[0]; i++){
		m[0] = index[0]+i;
		ar[0] = m_a[0][i];
		for(int j = 0; j < m_ifin[1]; j++){
			ar[1] = ar[0]*m_a[1][j];
			m[1] = index[1]+j;
			for(int k = 0; k < m_ifin[2]; k++){
				m[2] = index[2]+k;
				ar[2] = ar[1]*m_a[2][k];
				for(int l = 0; l < m_ifin[3]; l++){
					ar[3] = ar[2]*m_a[3][l];
					m[3] = index[3]+l;
					W += m_dataZ[m[0]][m[1]][m[2]][m[3]]*ar[3];
				}
			}
		}
	}
	return W;
}

void Wigner4DManipulator::f_GetFFTCSD(int j, int *nfft, 
	double *deltaZ, double *aptmin, double *aptmax, double fringe, int *anfft)
{
	double Dr = 0;

	int level = m_csdlevel;
	double softedge = 1;
	if(aptmin != nullptr){
		if(aptmin[j] > 0){
			if(fringe > 0){
				softedge = min(1.0, sqrt(aptmin[j]*m_apteps/fringe));
			}
			Dr = m_lambda/(PI2*aptmin[j]*1e-3)*1e3/m_apteps*softedge;
			level = 0;
		}
	}
	nfft[j] = fft_number(m_meshZ[j], level);
	while(nfft[j]*m_deltaZ[j] < Dr){
		nfft[j] <<= 1;
	}
	deltaZ[j] = m_lambda/(1e-3*m_deltaZ[j]*nfft[j])*1e3; // mm -> m -> mm
	if(anfft != nullptr){
		anfft[j] = nfft[j];
		double dns = m_aptpoints/m_apteps/PI*aptmax[j]/aptmin[j]*softedge;
		while(anfft[j]/2 > dns){ // shrink until the aperture size ~ FFT range
			anfft[j] >>= 1;
		}
	}
}

int Wigner4DManipulator::f_AllocFFTWS(
	FastFourierTransform **fft, int nfft[], double **ws, double ***ws2)
{
	int ndim = m_hmeshZ[WignerUVPrmu] > 0 && m_hmeshZ[WignerUVPrmv] > 0 ? 2 : 1;
	if(ndim == 2){
		*fft = new FastFourierTransform(2, nfft[WignerUVPrmu], nfft[WignerUVPrmv]);
		if(ws2 != nullptr){
			*ws2 = new double *[nfft[WignerUVPrmu]];
			for(int n = 0; n < nfft[WignerUVPrmu]; n++){
				(*ws2)[n] = new double[2*nfft[WignerUVPrmv]];
			}
		}
	}
	else if(m_hmeshZ[WignerUVPrmu] > 0){
		*fft = new FastFourierTransform(1, nfft[WignerUVPrmu]);
		if(ws != nullptr){
			*ws = new double[2*nfft[WignerUVPrmu]];
		}
	}
	else{
		*fft = new FastFourierTransform(1, nfft[WignerUVPrmv]);
		if(ws != nullptr){
			*ws = new double[2*nfft[WignerUVPrmv]];
		}
	}
	return ndim;
}

double Wigner4DManipulator::f_LoadWS(int ii, int jj,
	int nfft[], int ndim, double *ws, double **ws2, double *deltaZ)
{
	double F = 0;
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
				if(kk >= 0 && kk < m_meshZ[WignerUVPrmu]
					&& ll >= 0 && ll < m_meshZ[WignerUVPrmv])
				{
					ws2[k][2*l] = m_dataZ[ii][jj][kk][ll];
					if(deltaZ != nullptr){
						ws2[k][2*l] *= deltaZ[WignerUVPrmu]*deltaZ[WignerUVPrmv];
					}
					F += ws2[k][2*l];
				}
			}
			else if(m_hmeshZ[WignerUVPrmu] > 0){
				ws[2*k] = ws[2*k+1] = 0;
				if(kk >= 0 && kk < m_meshZ[WignerUVPrmu]){
					ws[2*k] = m_dataZ[ii][jj][kk][ll];
					if(deltaZ != nullptr){
						ws[2*k] *= deltaZ[WignerUVPrmu];
					}
					F += ws[2*k];
				}
			}
			else{
				ws[2*l] = ws[2*l+1] = 0;
				if(ll >= 0 && ll < m_meshZ[WignerUVPrmv]){
					ws[2*l] = m_dataZ[ii][jj][kk][ll];
					if(deltaZ != nullptr){
						ws[2*l] *= deltaZ[WignerUVPrmv];
					}
					F += ws[2*l];
				}
			}
		}
	}
	return F;
}

void Wigner4DManipulator::f_SetSlit(double fringe,
	vector<vector<double>> &position, vector<vector<double>> &aperture)
{
	m_napt = (int)position.size();
	m_border.resize(m_napt);
	for(int napt = 0; napt < m_napt; napt++){
		m_border[napt].resize(2);
		for(int j = 0; j < 2; j++){
			double wh = aperture[napt][j];
			double org = position[napt][j];
			if(wh <= 0){
				wh = m_DeltaUV[j]*2;
				org = 0;
			}
			m_border[napt][j].resize(4);
			m_border[napt][j][0] = m_border[napt][j][1] = org-wh/2;
			m_border[napt][j][2] = m_border[napt][j][3] = org+wh/2;
			int UV = GetUV(j);
			if(napt == 0){
				m_aptmin[UV] = wh;
				m_aptmax[UV] = wh+2*(fringe+fabs(org));
			}
			else{
				m_aptmin[UV] = min(m_aptmin[UV], wh);
				m_aptmax[UV] = max(m_aptmax[UV], wh+2*(fringe+fabs(org)));
			}
		}
	}
}

void Wigner4DManipulator::f_InsertSlit(PrintCalculationStatus *calcstats)
{
	if(m_napt == 0){
		return;
	}

	int nfft[NumberWignerUVPrm] = {1, 1, 1, 1};
	int anfft[NumberWignerUVPrm] = {1, 1, 1, 1};
	double deltaZ[NumberWignerUVPrm] = {0, 0, 0, 0};
	double aptmin[NumberWignerUVPrm], aptmax[NumberWignerUVPrm];
	bool shrink = false;
	for(int j = 0; j < 2; j++){ // get FFT settings
		if(!m_active[j]){
			continue;
		}
		int uv = Getuv(j);
		aptmin[uv] = m_aptmin[GetUV(j)];
		aptmax[uv] = m_aptmax[GetUV(j)];
		f_GetFFTCSD(uv, nfft, deltaZ, aptmin, aptmax, m_dfringe[j], anfft);
		if(nfft[uv] != anfft[uv]){
			shrink = true;
		}
	}

	for(int napt = 0; napt < m_napt; napt++){ // set the fringe
		for(int j = 0; j < 2; j++){
			double df = max(m_dfringe[j], deltaZ[Getuv(j)]);
			m_border[napt][j][0] -= df/2;
			m_border[napt][j][1] += df/2;
			m_border[napt][j][2] -= df/2;
			m_border[napt][j][3] += df/2;
		}
	}

	FastFourierTransform *fft, *afft = nullptr;
	double *ws = nullptr;
	double **ws2 = nullptr;
	int ndim = f_AllocFFTWS(&fft, nfft, &ws, &ws2);
	if(shrink){
		f_AllocFFTWS(&afft, anfft);
	}
	double UV[2];
	vector<double> wscsd[2], *pwscsd = nullptr;
	vector<vector<double>> wscsd2[2], *pwscsd2 = nullptr;

	if(ndim == 2){
		for(int j = 0; j < 2; j++){
			wscsd2[j].resize(nfft[Getuv(0)]+1);
			for(int k = 0; k <= nfft[Getuv(0)]; k++){
				wscsd2[j][k].resize(2*(nfft[Getuv(1)]+1));
			}
		}
		pwscsd2 = wscsd2;
	}
	else{
		for(int j = 0; j < 2; j++){
			if(m_active[0]){
				wscsd[j].resize(2*(nfft[Getuv(0)]+1));
			}
			else{
				wscsd[j].resize(2*(nfft[Getuv(1)]+1));
			}
		}
		pwscsd = wscsd;
	}

	int nmesh[NumberWignerUVPrm] = {1, 1, 1, 1};
	int hnmesh[NumberWignerUVPrm] = {0, 0, 0, 0};
	for(int j = 0; j < 2; j++){
		if(m_active[j]){
			int uv = Getuv(j);
			hnmesh[uv] = anfft[uv]/2;
			nmesh[uv] = 2*hnmesh[uv]+1;
		}
	}

	if(calcstats != nullptr){
		calcstats->SetSubstepNumber(1, m_meshZ[WignerUVPrmU]*m_meshZ[WignerUVPrmV]/m_nproc);
	}

	vector<int> steps, inistep, finstep;
	mpi_steps(m_meshZ[WignerUVPrmU], m_meshZ[WignerUVPrmV], m_nproc, &steps, &inistep, &finstep);

	int nm = nfft[Getuv(0)]*nfft[Getuv(1)];
	for(int i = -m_hmeshZ[WignerUVPrmU]; i <= m_hmeshZ[WignerUVPrmU]; i++){
		int ii = i+m_hmeshZ[WignerUVPrmU];
		UV[0] = i*m_deltaZ[WignerUVPrmU];
		for(int j = -m_hmeshZ[WignerUVPrmV]; j <= m_hmeshZ[WignerUVPrmV]; j++){
			int jj = j+m_hmeshZ[WignerUVPrmV];
			UV[1] = j*m_deltaZ[WignerUVPrmV];
			
			int nstep = ii*m_meshZ[WignerUVPrmV]+jj;
			if(nstep < inistep[m_rank] || nstep > finstep[m_rank]){
				continue;
			}

#ifdef _DEBUG
			f_CSDOptics(UV, deltaZ, nfft, pwscsd, pwscsd2, abs(i)<5);
#else
			f_CSDOptics(UV, deltaZ, nfft, pwscsd, pwscsd2);
#endif
			f_LoadWS(ii, jj, nfft, ndim, ws, ws2, nullptr);
			if(ndim == 2){
				fft->DoFFT(ws2, -1);
			}
			else{
				fft->DoFFT(ws, -1);
			}

			for(int k = 0; k < nfft[WignerUVPrmu]; k++){
				for(int l = 0; l < nfft[WignerUVPrmv]; l++){
					if(ndim == 2){
						ws2[k][2*l] *= wscsd2[1][k][2*l]/nm;
						ws2[k][2*l+1] *= wscsd2[1][k][2*l]/nm;
					}
					else{
						ws[2*(k+l)] *= wscsd[1][2*(k+l)]/nm;
						ws[2*(k+l)+1] *= wscsd[1][2*(k+l)]/nm;
					}
				}
			}

#ifdef _DEBUG
			if(!WigManipCSDAfterOptics.empty()){
				vector<string> titles{"dX", "dY", "CSD"};
				vector<double> items(titles.size());
				ofstream debug_out(WigManipCSDAfterOptics);
				PrintDebugItems(debug_out, titles);
				int kk = 0, ll = 0;
				for(int k = -nfft[WignerUVPrmu]/2; k <= nfft[WignerUVPrmu]/2; k++){
					if(m_active[0]){
						kk = fft_index(k, nfft[WignerUVPrmu], -1);
					}
					items[0] = k*deltaZ[WignerUVPrmu];
					for(int l = -nfft[WignerUVPrmv]/2; l <= nfft[WignerUVPrmv]/2; l++){
						if(m_active[1]){
							ll = fft_index(l, nfft[WignerUVPrmv], -1);
						}
						items[1] = l*deltaZ[WignerUVPrmv];
						if(ndim == 2){
							items[2] = ws2[kk][2*ll];
						}
						else{
							items[2] = ws[2*(kk+ll)];
						}
						PrintDebugItems(debug_out, items);
					}
				}
				debug_out.close();
			}
#endif
			if(shrink){
				for(int k = 0; k < nfft[WignerUVPrmu]; k++){
					int kk = nfft[WignerUVPrmu] == 0 ? 0 : -1;
					if(k < anfft[WignerUVPrmu]){
						kk = fft_index(fft_index(k, anfft[WignerUVPrmu], 1), nfft[WignerUVPrmu], -1);
					}
					for(int l = 0; l < nfft[WignerUVPrmv]; l++){
						int ll = nfft[WignerUVPrmv] == 0 ? 0 : -1;
						if(l < anfft[WignerUVPrmv]){
							ll = fft_index(fft_index(l, anfft[WignerUVPrmv], 1), nfft[WignerUVPrmv], -1);
						}
						if(ndim == 2){
							if(kk < 0 || ll < 0){
								ws2[k][2*l] = ws2[k][2*l+1] = 0;
							}
							else{
								ws2[k][2*l] = ws2[kk][2*ll];
								ws2[k][2*l+1] = ws2[kk][2*ll+1];
							}
						}
						else{
							if(kk+ll < 0){
								ws[2*(k+l)] = ws[2*(k+l)+1] = 0;
							}
							else{
								ws[2*(k+l)] = ws[2*(kk+ll)];
								ws[2*(k+l)+1] = ws[2*(kk+ll)+1];
							}
						}
					}
				}
				if(ndim == 2){
					afft->DoFFT(ws2, 1);
				}
				else{
					afft->DoFFT(ws, 1);
				}
			}
			else{
				if(ndim == 2){
					fft->DoFFT(ws2, 1);
				}
				else{
					fft->DoFFT(ws, 1);
				}
			}

			int kfft = -1, lfft = -1;
			m_dataZ[ii][jj].resize(nmesh[WignerUVPrmu]);
			for(int k = 0; k < nmesh[WignerUVPrmu]; k++){
				if(hnmesh[WignerUVPrmu] > 0){
					kfft = fft_index(k-hnmesh[WignerUVPrmu], anfft[WignerUVPrmu], -1);
				}
				m_dataZ[ii][jj][k].resize(nmesh[WignerUVPrmv]);
				for(int l = 0; l < nmesh[WignerUVPrmv]; l++){
					if(hnmesh[WignerUVPrmv] > 0){
						lfft = fft_index(l-hnmesh[WignerUVPrmv], anfft[WignerUVPrmv], -1);
					}
					if(ndim == 2){
						m_dataZ[ii][jj][k][l] = ws2[kfft][2*lfft];
					}
					else if(m_hmeshZ[WignerUVPrmu] > 0){
						m_dataZ[ii][jj][k][l] = ws[2*kfft];
					}
					else{
						m_dataZ[ii][jj][k][l] = ws[2*lfft];
					}
					if(kfft == hnmesh[WignerUVPrmu]){ // halve the value at the FFT edge
						m_dataZ[ii][jj][k][l] /= 2;
					}
					if(lfft == hnmesh[WignerUVPrmv]){
						m_dataZ[ii][jj][k][l] /= 2;
					}
				}
			}

#ifdef _DEBUG
			if(!WigManipAfterOptics.empty()){
				vector<string> titles{"X'", "Y'", "W"};
				vector<double> items(titles.size());
				ofstream debug_out(WigManipAfterOptics);
				PrintDebugItems(debug_out, titles);
				int kk = 0, ll = 0;
				for(int k = -anfft[WignerUVPrmu]/2; k <= anfft[WignerUVPrmu]/2; k++){
					if(m_active[0]){
						kk = fft_index(k, anfft[WignerUVPrmu], -1);
					}
					items[0] = k*m_deltaZ[WignerUVPrmu];
					if(shrink && nfft[WignerUVPrmu] > 0){
						items[0] *= nfft[WignerUVPrmu]/anfft[WignerUVPrmu];
					}
					for(int l = -anfft[WignerUVPrmv]/2; l <= anfft[WignerUVPrmv]/2; l++){
						if(m_active[1]){
							ll = fft_index(l, anfft[WignerUVPrmv], -1);
						}
						items[1] = l*m_deltaZ[WignerUVPrmv];
						if(shrink && nfft[WignerUVPrmv] > 0){
							items[1] *= nfft[WignerUVPrmv]/anfft[WignerUVPrmv];
						}
						if(ndim == 2){
							items[2] = ws2[kk][2*ll];
						}
						else{
							items[2] = ws[2*(kk+ll)];
						}
						PrintDebugItems(debug_out, items);
					}
				}
				debug_out.close();
			}
#endif

			if(calcstats != nullptr){
				calcstats->AdvanceStep(1);
			}

		}
	}

	if(m_nproc > 1){
		int nws = nmesh[WignerUVPrmu]*nmesh[WignerUVPrmv];
		double *wsmpi = new double[nws];
		for(int i = 0; i < m_meshZ[WignerUVPrmU]; i++){
			for(int j = 0; j < m_meshZ[WignerUVPrmV]; j++){
				int nstep = i*m_meshZ[WignerUVPrmV]+j;
				int currrank = get_mpi_rank(nstep, m_nproc, inistep, finstep);
				if(m_rank == currrank){
					for(int k = 0; k < nmesh[WignerUVPrmu]; k++){
						for(int l = 0; l < nmesh[WignerUVPrmv]; l++){
							wsmpi[k*nmesh[WignerUVPrmv]+l] = m_dataZ[i][j][k][l];
						}
					}
				}
				else{
					m_dataZ[i][j].resize(nmesh[WignerUVPrmu]);
					for(int k = 0; k < nmesh[WignerUVPrmu]; k++){
						m_dataZ[i][j][k].resize(nmesh[WignerUVPrmv]);
					}
				}
				if(m_thread != nullptr){
					m_thread->Bcast(wsmpi, nws, MPI_DOUBLE, currrank, m_rank);
				}
				else{
					MPI_Bcast(wsmpi, nws, MPI_DOUBLE, currrank, MPI_COMM_WORLD);
				}
				if(m_rank != currrank){
					for(int k = 0; k < nmesh[WignerUVPrmu]; k++){
						for(int l = 0; l < nmesh[WignerUVPrmv]; l++){
							m_dataZ[i][j][k][l] = wsmpi[k*nmesh[WignerUVPrmv]+l];
						}
					}
				}
			}
		}
		delete[] wsmpi;
	}

	for(int j = 0; j < 2; j++){
		if(m_active[j]){
			int uv = Getuv(j);
			m_hmeshZ[uv] = hnmesh[uv];
			m_meshZ[uv] = 2*m_hmeshZ[uv]+1;
			if(shrink){
				m_deltaZ[uv] *= nfft[uv]/anfft[uv];
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
	if(shrink){
		delete afft;
	}

	if(calcstats != nullptr){
		calcstats->AdvanceStep(0);
	}

#ifdef _DEBUG
	f_Export(true);
#endif
}

void Wigner4DManipulator::f_CSDOptics(double center[], double deltaZ[], int nfft[], 
	vector<double> *wscsd, vector<vector<double>> *wscsd2, bool debug)
{
	int Var[2] = {WignerUVPrmU, WignerUVPrmV}; // for spatial filtering;
	int var[2] = {WignerUVPrmu, WignerUVPrmv}; // for spatial filtering;
	int mesh[2] = {nfft[var[0]], nfft[var[1]]};
	double deldiff[2] = {deltaZ[var[0]], deltaZ[var[1]]};

	double aptfringe[2];
	for(int j = 0; j < 2; j++){
		aptfringe[j] = m_border[0][j][1]-m_border[0][j][0];
	}

	double xy[2], t;
	for(int k = -mesh[0]/2; k <= mesh[0]/2; k++){
		int kk = k+mesh[0]/2;
		xy[0] = k*deldiff[0]/2+center[Var[0]];
		for(int l = -mesh[1]/2; l <= mesh[1]/2; l++){
			int ll = l+mesh[1]/2;
			xy[1] = l*deldiff[1]/2+center[Var[1]];
			t = 0;
			for(int na = 0; na < m_napt; na++){
				t = max(t, f_GetRectSlit(aptfringe, m_border[na], xy));
			}
			if(wscsd2 != nullptr){
				wscsd2[0][kk][2*ll] = t;
				wscsd2[0][kk][2*ll+1] = 0;
			}
			else{
				wscsd[0][2*(kk+ll)] = t;
				wscsd[0][2*(kk+ll)+1] = 0;
			}
		}
	}

	int kp = 0, km = 0, lp = 0, lm = 0;
	for(int k = 0; k < mesh[0]; k++){
		int kk = fft_index(k, mesh[0], 1);
		if(m_active[0]){
			kp = mesh[0]/2-kk;
			km = mesh[0]/2+kk;
		}
		for(int l = 0; l < mesh[1]; l++){
			int ll = fft_index(l, mesh[1], 1);
			if(m_active[1]){
				lp = mesh[1]/2-ll;
				lm = mesh[1]/2+ll;
			}
			if(wscsd2 != nullptr){
				wscsd2[1][k][2*l] = wscsd2[0][kp][2*lp]*wscsd2[0][km][2*lm];
				wscsd2[1][k][2*l+1] = 0;
			}
			else{
				wscsd[1][2*(k+l)] = wscsd[0][2*(kp+lp)]*wscsd[0][2*(km+lm)];
				wscsd[1][2*(k+l)+1] = 0;
			}
		}
	}

#ifdef _DEBUG
	if(!WigManipCSDOptics.empty() && debug){
		vector<string> titles{"X", "Y", "t", "dx", "dy", "CSD"};
		vector<double> items(titles.size());
		ofstream debug_out(WigManipCSDOptics);
		PrintDebugItems(debug_out, titles);
		for(int k = -mesh[0]/2; k <= mesh[0]/2; k++){
			int ki = k+mesh[0]/2;
			int kk = fft_index(k, mesh[0], -1);
			items[0] = k*deldiff[0]/2+center[Var[0]];
			items[3] = k*deldiff[0];
			for(int l = -mesh[1]/2; l <= mesh[1]/2; l++){
				int li = l+mesh[1]/2;
				int ll = fft_index(l, mesh[1], -1);
				items[1] = l*deldiff[1]/2+center[Var[1]];
				items[4] = l*deldiff[1];
				if(wscsd2 != nullptr){
					items[2] = wscsd2[0][ki][2*li];
					items[5] = wscsd2[1][kk][2*ll];
				}
				else{
					items[2] = wscsd[0][2*(ki+li)];
					items[5] = wscsd[1][2*(kk+ll)];
				}
				PrintDebugItems(debug_out, items);
			}
		}
		debug_out.close();
	}
#endif
}

double Wigner4DManipulator::f_GetRectSlit(double fringe[], vector<vector<double>> &border, double xy[])
{
	double t[2] = {1, 1};
	for(int j = 0; j < 2; j++){
		if(m_active[j]){
			t[j] = 0;
			if(xy[j] > border[j][0] && xy[j] < border[j][1]){
				t[j] = (xy[j]-border[j][0])/fringe[j];
			}
			else if(xy[j] >= border[j][1] && xy[j] <= border[j][2]){
				t[j] = 1;
			}
			else if(xy[j] > border[j][2] && xy[j] < border[j][3]){
				t[j] = (border[j][3]-xy[j])/fringe[j];
			}
			if(t[j] == 0){
				return 0;
			}
		}
	}
	return sqrt(t[0]*t[1]);
}

void Wigner4DManipulator::f_SetGridUV(
	double *dxytgt, double *aptmin, double *aptmax, double *dfringe)
{
	for(int j = 0; j < 2; j++){
		double Z = fabs(m_Zt[j]);
		int uv = Getuv(j);
		int UV = GetUV(j);
		m_meshZ[uv] = m_meshZ[UV] = 1;
		m_hmeshZ[uv] = m_hmeshZ[UV] = 0;
		m_deltaZ[uv] = m_deltaZ[UV] = 0;
		m_isfar[j] = false;
		if(m_active[j]){
			double deltaf = m_delta[uv]*Z;
			m_isfar[j] = Z >= m_Zborder[j][1];
			if(m_isfar[j]){
				m_deltaZ[UV] = deltaf;
				m_deltaZ[uv] = m_delta[UV]/Z;
				m_meshZ[uv] = m_mesh[UV];
			}
			else{
				if(Z < m_Zborder[j][0]){ //  near zone
					m_deltaZ[UV] = m_delta[UV];
				}
				else{ //  near->far zone 
					m_deltaZ[UV] = m_delta[UV]+(deltaf-m_delta[UV])/(m_Zborder[j][1]-m_Zborder[j][0])*(Z-m_Zborder[j][0]);
				}
				m_deltaZ[uv] = m_delta[uv];
				m_meshZ[uv] = m_mesh[uv];
			}
			int level = m_acclevel;
			if(dxytgt != nullptr){
				while(m_deltaZ[UV]/level > 2*dxytgt[j]){
					level++;
				}
			}
			m_deltaZ[UV] /= level;

			double DeltaUV = m_DeltaUV[j]+m_Deltauv[j]*Z;
			m_hmeshZ[UV] = (int)floor(0.5+DeltaUV/2/m_deltaZ[UV]);
			m_meshZ[UV] = 2*m_hmeshZ[UV]+1;
			m_hmeshZ[uv] = (m_meshZ[uv]-1)/2;

			if(aptmin != nullptr){
				if(aptmin[UV] > 0){
					double softedge = 1;
					if(dfringe[j] > 0){
						softedge = min(1.0, sqrt(aptmin[UV]*m_apteps/dfringe[j]));
					}
					int mpoints = (int)floor(0.5+(1<<m_acclevel)/PI/m_apteps*softedge);
					double aptdelta = aptmin[UV]/mpoints;
					m_deltaZ[UV] = min(aptdelta, m_deltaZ[UV]);
					m_hmeshZ[UV] = (int)ceil(min(DeltaUV, aptmax[UV])/2/m_deltaZ[UV]);
					m_meshZ[UV] = 2*m_hmeshZ[UV]+1;
				}
				if(aptmin[uv] > 0 && !m_isfar[j]){
					//--- to be written
				}
			}
		}
	}
}

void Wigner4DManipulator::f_GetSigma(double *Zt, double *sigma)
{
	for(int n = 0; n < NumberWignerUVPrm; n++){
		sigma[n] = 0;
	}
	double var[NumberWignerUVPrm], data;
	double sum = 0;
	int hmesh[NumberWignerUVPrm];
	double delta[NumberWignerUVPrm];

	bool isorg = false;
	if(Zt != nullptr){
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
				if(m_isfar[0] && !isorg){
					var[WignerUVPrmu] += var[WignerUVPrmU]/Zt[0];
				}
				for(int l = -hmesh[WignerUVPrmv]; l <= hmesh[WignerUVPrmv]; l++){
					indices[3] = l+hmesh[WignerUVPrmv];
					var[WignerUVPrmv] = l*delta[WignerUVPrmv];
					if(m_isfar[1] && !isorg){
						var[WignerUVPrmv] += var[WignerUVPrmV]/Zt[1];
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

void Wigner4DManipulator::f_SetSteps(int *steps, int *mesh)
{
	steps[WignerUVPrmU] = 1;
	steps[WignerUVPrmV] = mesh[WignerUVPrmU];
	steps[WignerUVPrmu] = mesh[WignerUVPrmV]*steps[WignerUVPrmV];
	steps[WignerUVPrmv] = mesh[WignerUVPrmu]*steps[WignerUVPrmu];
	steps[NumberWignerUVPrm] = mesh[WignerUVPrmv]*steps[WignerUVPrmv];
}

void Wigner4DManipulator::f_SetWindex(int j, double Z,
	int ifin[], int k, int index[], double UV[], double *delta)
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
	if(m_isfar[j]){
		idsc = UVidx;
		ipol = uvidx;
		if(Z < 0){
			k = -k;
		}
		Wp = (UV[j]+k*m_delta[idsc])/Z;
		index[idsc] = -k+m_hmesh[idsc];
	}
	else{
		idsc = uvidx;
		ipol = UVidx;
		Wp = UV[j]-k*m_delta[idsc]*Z;
		index[idsc] = k+m_hmesh[idsc];
	}

	if(index[idsc] < 0 || index[idsc] >= m_mesh[idsc]){
		index[ipol] = -1;
		return;
	}
	interpolant2d(ifin[j], Wp, m_delta[ipol], m_hmesh[ipol], delta, &index[ipol]);
}

void Wigner4DManipulator::f_Export(bool killoffset)
{
	if(m_rank == 0){
		if(m_type == WignerType4D){
			for(int j = 0; j < 2; j++){
				f_ExportWTrans(j, killoffset);
			}
			f_ExportProfile2D();
		}
		else{
			int jxy = m_active[0] ? 0 : 1;
			f_ExportWTrans(jxy, killoffset);
		}
	}
	MPI_Barrier(MPI_COMM_WORLD);
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
		{"X", "X'", "Flux"},
		{"Y", "Y'", "Flux"}
	};
	double delta[4] = {
		m_deltaZ[WignerUVPrmu]*m_deltaZ[WignerUVPrmv],
		m_deltaZ[WignerUVPrmU]*m_deltaZ[WignerUVPrmV],
		m_deltaZ[WignerUVPrmV]*m_deltaZ[WignerUVPrmv],
		m_deltaZ[WignerUVPrmU]*m_deltaZ[WignerUVPrmu]
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
							items[2] += m_dataZ[q[0]][q[1]][q[2]][q[3]]*delta[n];
						}
					}
					PrintDebugItems(debug_out, items);
				}
			}
			debug_out.close();
		}
	}
}

void Wigner4DManipulator::f_ExportWTrans(int jxy, bool killoffset)
{
	if(WigManipTrans.empty()){
		return;
	}

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
	int prjmesh[2], hmesh[2], prjh[2];
	for(int j = 0; j < 2; j++){
		prjmesh[j] = m_meshZ[prjidx[j]];
		hmesh[j] = m_hmeshZ[exidx[j]];
		prjh[j] = m_hmeshZ[prjidx[j]];
	}

	int kini = 0;
	int kfin = prjmesh[0]-1;
	int lini = 0;
	int lfin = prjmesh[1]-1;
//	kini = kfin = prjh[0];
//	lini = lfin = prjh[1];

	vector<vector<double>> data(2*hmesh[0]+1);
	for(int j = 0; j <= 2*hmesh[0]; j++){
		data[j].resize(2*hmesh[1]+1, 0.0);
	}
	vector<int> index(NumberWignerUVPrm);
	for(int i = -hmesh[0]; i <= hmesh[0]; i++){
		index[exidx[0]] = i+hmesh[0];
		for(int j = -hmesh[1]; j <= hmesh[1]; j++){
			index[exidx[1]] = j+hmesh[1];
			for(int k = kini; k <= kfin; k++){
				index[prjidx[0]] = k;
				for(int l = lini; l <= lfin; l++){
					index[prjidx[1]] = l;
					data[i+hmesh[0]][j+hmesh[1]] +=
						m_dataZ[index[0]][index[1]][index[2]][index[3]];
				}
			}
		}
	}

	vector<string> xytitles{"X", "Y", "X'", "Y'"};
	ofstream debug_out[3];
	vector<string> titles[3];
	vector<double> items[3];

	titles[0] = vector<string>{xytitles[exidx[0]], xytitles[exidx[1]], "W"};
	titles[1] = vector<string>{xytitles[exidx[0]], "F"};
	titles[2] = vector<string>{xytitles[exidx[0]], "aF"};

	string pathname = WigManipTrans+(jxy==0?"X":"Y");
	debug_out[0].open(pathname+"Wigner.dat");
	debug_out[1].open(pathname+"Sprof.dat");
	debug_out[2].open(pathname+"Aprof.dat");

	for(int j = 0; j < 3; j++){
		if(debug_out[j].is_open()){
			PrintDebugItems(debug_out[j], titles[j]);
		}
		items[j].resize(titles[j].size());
	}

	vector<double> y(2*hmesh[1]+1);
	double zero = 0;
	Spline spl;
	int exhmesh = m_hmeshZ[exidx[1]];

	bool far = m_isfar[jxy];
	if(far){
		if(killoffset){
			exhmesh = hmesh[1];
		}
		else{
			exhmesh = (int)floor(0.5+m_Deltauv[jxy]/2/m_deltaZ[exidx[1]]);
		}
	}
	vector<double> aflux(2*exhmesh+1, 0.0);
	for(int i = -hmesh[0]; i <= hmesh[0]; i++){
		items[0][0] = items[1][0] = i*m_deltaZ[exidx[0]];
		if(far && !killoffset){
			for(int j = -hmesh[1]; j <= hmesh[1]; j++){
				y[j+hmesh[1]] = j*m_deltaZ[exidx[1]]+items[0][0]/m_Zt[jxy];
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
		items[1][1] = flux*m_deltaZ[exidx[1]];
		if(debug_out[1].is_open()){
			PrintDebugItems(debug_out[1], items[1]);
		}
	}

	for(int j = -exhmesh; j <= exhmesh && debug_out[2].is_open(); j++){
		items[2][0] = j*m_deltaZ[exidx[1]];
		items[2][1] = aflux[j+exhmesh]*m_deltaZ[exidx[0]];
		PrintDebugItems(debug_out[2], items[2]);
	}

	for(int j = 0; j < 3; j++){
		if(debug_out[j].is_open()){
			debug_out[j].close();
		}
	}
}

//  class WignerPropagator
WignerPropagator::WignerPropagator(SpectraSolver &spsolver)
	: SpectraSolver(spsolver)
{
#ifdef _DEBUG
//	WigPropSpatialInt = "..\\debug\\Spatial2D_int.dat";
//	WigPropSpatialOrg = "..\\debug\\Spatial2D_org.dat";
//	WigPropGamma = "..\\debug\\Gamma.dat";
#endif

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

	int xlevel = (int)floor(0.5+m_conf[grlevel_])+1;
	int xplevel = (int)floor(0.5+m_conf[anglelevel_])+1;
	m_wigmanip.SetAccLevel(xlevel, xplevel, m_conf[diflim_], m_conf[softedge_]);
	m_wigmanip.SetWavelength(wave_length(m_fixep));
	m_wigmanip.SetMPI(m_mpiprocesses, m_rank, m_thread);
	if(!m_wigmanip.LoadData(m_pjoutput)){
		throw runtime_error("Loading the Wigner function data failed.");
	}
	if(!m_wigmanip.Initialize()){
		throw runtime_error("Invalid Wigner function data format.");
	}
}

void WignerPropagator::Propagate(
	vector<string> &subresults, vector<string> &categories)
{
	int zpoints = (int)floor(0.5+m_conf[zmesh_]);
	if(m_confv[zrange_][1] < m_confv[zrange_][0]){
		swap(m_confv[zrange_][0], m_confv[zrange_][1]);
	}
	double dz = (m_confv[zrange_][1]-m_confv[zrange_][0])/max(1, zpoints-1);
	vector<vector<vector<vector<double>>>> CSD[2], *pCSD = nullptr;
	vector<vector<double>> vararray(NumberWignerUVPrm);
	vector<vector<double>> CSDslice[2], F;
	vector<double> zarray;
	for(int j = 0; j < 2; j++){ // x,y
		CSDslice[j].resize(3); // absolute, argument, Gamma
		m_SigmaZ[j].resize(zpoints);
	}

	m_vararray.resize(zpoints);
	if(m_confb[degcoh_] || m_confb[csd_]){
		m_CSD.resize(2);
	}
	else{
		m_CSD.resize(1);
	}
	for(int n = 0; n < m_CSD.size(); n++){
		m_CSD[n].resize(zpoints);
	}
	m_hmesh.resize(zpoints);
	m_mesh.resize(zpoints);
	zarray.resize(zpoints);

	int mopt = -1;
	double *pflen = nullptr;
	double flen[2] = {0, 0};
	vector<vector<double>> apt, pos;
	if(m_confsel[optics_] != NoneLabel){
		if(m_conf[optpos_] <= m_confv[zrange_][0]){
			mopt = 0;
		}
		else if(dz > 0){
			mopt = (int)ceil((m_conf[optpos_]-m_confv[zrange_][0])/dz);
		}
		if(m_confsel[optics_] == ThinLensLabel){
			pflen = flen;
			if(m_conf[foclenx_] != 0){
				flen[0] = m_conf[foclenx_];
			}
			if(m_conf[focleny_] != 0){
				flen[1] = m_conf[focleny_];
			}
		}
		else{
			apt.push_back(vector<double> {m_conf[aptx_], m_conf[apty_]});
			if(m_confsel[optics_] == SingleLabel){
				pos.push_back(vector<double> {0, 0});
			}
			else if(m_confsel[optics_] == DoubleLabel){
				pos.push_back(vector<double> {-m_conf[aptdistx_]/2, -m_conf[aptdisty_]/2});
				apt.push_back(vector<double> {m_conf[aptx_], m_conf[apty_]});
				pos.push_back(vector<double> {m_conf[aptdistx_]/2, m_conf[aptdisty_]/2});
			}
		}
	}

	if(m_confb[degcoh_] || m_confb[csd_]){
		pCSD = CSD;
	}

	int nopt = mopt >= 0 ? 1 : 0;
	vector<vector<double>> Zwaist(nopt+1);
	vector<vector<double>> sigmao(nopt+1);

	int csteps = 2*((zpoints-1)/m_mpiprocesses+1);
	if(mopt >= 0){
		csteps += 3*nopt;
	}
	if(m_confsel[gridspec_] == AutomaticLabel){
		csteps += 2;
	}
	m_calcstatus->SetSubstepNumber(0, csteps);

	for(int n = 0; n <= nopt; n++){
		Zwaist[n].resize(2);
		sigmao[n].resize(NumberWignerUVPrm);
	}
	
	vector<vector<vector<vector<double>>>> AProfiles(nopt+1);

	m_xyWig.resize(nopt+1);
	m_Wig.resize(nopt+1);
	// get the original Wigner function
	m_wigmanip.SetSourceWigner(Zwaist[0], sigmao[0], m_xyWig[0], m_Wig[0], true);
	if(m_confb[aprofile_]){
		AProfiles[0].resize(1); AProfiles[0][0].resize(1);
		m_wigmanip.GetAngularProfile(AProfiles[0][0][0]);
	}
	for(int n = 0; n < nopt; n++){
		m_wigmanip.OpticalElement(
			m_conf[optpos_], pflen, m_conf[softedge_], pos, apt, m_calcstatus);
		m_wigmanip.SetSourceWigner(Zwaist[n+1], sigmao[n+1], m_xyWig[n+1], m_Wig[n+1], true);
		if(m_confb[aprofile_]){
			AProfiles[n+1].resize(1); AProfiles[n+1][0].resize(1);
			m_wigmanip.GetAngularProfile(AProfiles[n+1][0][0]);
		}
	}

	if(m_confsel[gridspec_] == AutomaticLabel){
		m_wigmanip.Transfer(m_confv[zrange_][1], nullptr, m_calcstatus);
	}
	if(nopt > 0){
		m_wigmanip.SetSourceWigner(Zwaist[0], sigmao[0], m_xyWig[0], m_Wig[0], false);
	}

	double sigma[2], tgtdxy[2], tgtdxyorg[2], *ptgtdxy = nullptr;
	if(m_confsel[gridspec_] != AutomaticLabel){
		// set the x,x',y,y' coordinates in advance to set tgtdxy
		f_SetGrid(vararray);
		ptgtdxy = tgtdxy;
		for(int j = 0; j < 2; j++){
			int iUV = GetUV(j);
			if(vararray[iUV].size() < 2){
				tgtdxy[j] = tgtdxyorg[j] = 0;
			}
			else{
				tgtdxy[j] = tgtdxyorg[j] = vararray[iUV][1]-vararray[iUV][0];
			}
		}
	}

	m_wigmanip.SetMPI(1, 0, nullptr);
	bool beforeopt = mopt >= 0;

	for(int m = 0; m < zpoints; m++){
		double ztarget = m_confv[zrange_][0]+dz*m;
		zarray[m] = ztarget;
		if(m_rank != m%m_mpiprocesses){
			continue;
		}
		if(m >= mopt && beforeopt){
			m_wigmanip.SetSourceWigner(Zwaist[1], sigmao[1], m_xyWig[1], m_Wig[1], false);
			beforeopt = false;
		}
		if(m_confsel[gridspec_] == NormSlitLabel){
			double sigma[2];
			m_wigmanip.GetBeamSizeAt(ztarget, sigma);
			for(int j = 0; j < 2; j++){
				tgtdxy[j] = sigma[j]*tgtdxyorg[j];
			}
		}

		m_wigmanip.Transfer(ztarget, ptgtdxy, m_calcstatus);
		m_wigmanip.GetCSD(sigma, m_vararray[m], F, pCSD, m_calcstatus);
		for(int j = 0; j < 2; j++){
			m_SigmaZ[j][m] = sigma[j];
		}
		f_SliceCSD(m, F, pCSD);
	}

	if(m_mpiprocesses > 1){
		for(int m = 0; m < zpoints; m++){
			f_ScatterCSD(m, pCSD == nullptr);
		}
	}

	vector<vector<vector<double>>> Profiles(zpoints);
	vector<vector<vector<double>>> CSDxy[2];
	vector<vector<vector<double>>> Gammaxy[2];

	if(m_confb[csd_]){
		for(int j = 0; j < 2; j++){
			CSDxy[j].resize(zpoints);
			for(int m = 0; m < zpoints; m++){
				CSDxy[j][m].resize(2);
			}
		}
	}
	if(m_confb[degcoh_]){
		for(int j = 0; j < 2; j++){
			Gammaxy[j].resize(zpoints);
			for(int m = 0; m < zpoints; m++){
				Gammaxy[j][m].resize(1);
			}
		}
	}

	if(m_confsel[gridspec_] == AutomaticLabel){
		// set the x,x',y,y' coordinates after m_vararray is arranged
		f_SetGrid(vararray);
	}

	for(int m = 0; m < zpoints; m++){
		Profiles[m].resize(1);
		f_GetProfile(m, vararray, Profiles[m][0]);
		if(m_confb[csd_] || m_confb[degcoh_]){
			f_GetCSD(m, vararray, CSDslice);
			if(m_confb[csd_]){
				for(int j = 0; j < 2; j++){
					for(int n = 0; n < 2; n++){
						CSDxy[j][m][n] = CSDslice[j][n];
					}
				}
			}
			if(m_confb[degcoh_]){
				for(int j = 0; j < 2; j++){
					Gammaxy[j][m][0] = CSDslice[j][2];
				}
			}
		}
	}

	vector<string> titles, units, details;
	vector<vector<double>> scanvalues, xyvar;
	vector<vector<vector<double>>> data, vararrayd;
	vector<vector<vector<vector<double>>>> datad;
	vector<vector<string>> suppletitles;
	vector<vector<double>> suppledata;

	string csd[2], degcoh[2];
	int spdim = 1;
	vector<int> spidx, apidx, wpidx, sizeidx;
	vector<vector<vector<double>>> bmsize(1);

	sizeidx.push_back(LongPos_);
	if(m_type == WignerType4D){
		csd[0] = CSDLabelx;
		csd[1] = CSDLabely;
		degcoh[0] = DegCohLabelx;
		degcoh[1] = DegCohLabely;
		spdim = 2;
		if(m_confsel[gridspec_] == NormSlitLabel){
			spidx.push_back(Xn_);
			spidx.push_back(Yn_);
		}
		else{
			spidx.push_back(DistX_);
			spidx.push_back(DistY_);
		}
		apidx.push_back(ThetaX_);
		apidx.push_back(ThetaY_);
		wpidx.push_back(SrcX_);
		wpidx.push_back(SrcY_);
		wpidx.push_back(SrcQX_);
		wpidx.push_back(SrcQY_);
		sizeidx.push_back(BeamSizeX_);			
		sizeidx.push_back(BeamSizeY_);
		bmsize[0].push_back(m_SigmaZ[0]);
		bmsize[0].push_back(m_SigmaZ[1]);
	}
	else{
		csd[0] = CSDLabel;
		csd[1] = CSDLabel;
		degcoh[0] = DegCohLabel;
		degcoh[1] = DegCohLabel;
		if(m_confsel[gridspec_] == NormSlitLabel){
			if(m_type == WignerType2DX){
				spidx.push_back(Xn_);
			}
			else{
				spidx.push_back(Yn_);
			}
		}
		else{
			if(m_type == WignerType2DX){
				spidx.push_back(DistX_);
			}
			else{
				spidx.push_back(DistY_);
			}
		}
		if(m_type == WignerType2DX){
			apidx.push_back(ThetaX_);
			wpidx.push_back(SrcX_);
			wpidx.push_back(SrcQX_);
			sizeidx.push_back(BeamSizeX_);
			bmsize[0].push_back(m_SigmaZ[0]);
		}
		else{
			apidx.push_back(ThetaY_);
			wpidx.push_back(SrcY_);
			wpidx.push_back(SrcQY_);
			sizeidx.push_back(BeamSizeY_);
			bmsize[0].push_back(m_SigmaZ[1]);
		}
	}
	spidx.push_back(LongPos_);
	if(m_type == WignerType4D){
		spidx.push_back(NearFldens_);
		apidx.push_back(Fldens_);
		wpidx.push_back(WBrill_);
	}
	else{
		spidx.push_back(NearLinFldens_);
		apidx.push_back(LinFldens_);
		wpidx.push_back(Brill1D_);
	}

	// export spatial profiles
	subresults.push_back("");
	categories.push_back(SProfLabel);
	titles.clear(); units.clear(); xyvar.clear();
	for(int j = 0; j < spidx.size(); j++){
		titles.push_back(TitleLablesDetailed[spidx[j]]);
		units.push_back(UnitLablesDetailed[spidx[j]]);
	}
	for(int j = 0; j < 2; j++){
		if(!m_wigmanip.IsActive(j)){
			continue;
		}
		int iUV = GetUV(j);
		xyvar.push_back(vararray[iUV]);
	}
	xyvar.push_back(zarray);
	WriteResults(*this, nullptr, zpoints, scanvalues, spdim+1, spdim, titles, units,
		details, xyvar, Profiles, vararrayd, datad, suppletitles, suppledata, subresults.back());

	// export beam size variation
	subresults.push_back("");
	categories.push_back(BeamSizeLabel);
	titles.clear(); units.clear(); xyvar.clear();
	for(int j = 0; j < sizeidx.size(); j++){
		titles.push_back(TitleLablesDetailed[sizeidx[j]]);
		units.push_back(UnitLablesDetailed[sizeidx[j]]);
	}
	xyvar.push_back(zarray);
	WriteResults(*this, nullptr, 1, scanvalues, 1, 1, titles, units,
		details, xyvar, bmsize, vararrayd, datad, suppletitles, suppledata, subresults.back());

	// export optional data
	int uvidx[NumberWignerUVPrm] = {Xavg_, Yavg_, Xdiff_, Ydiff_};
	int uvnidx[NumberWignerUVPrm] = {Xnavg_, Ynavg_, Xndiff_, Yndiff_};
	int *puvidx = m_confsel[gridspec_] == NormSlitLabel ? uvnidx : uvidx;
	if(m_confb[csd_] || m_confb[degcoh_]){
		for(int k = 0; k < 2; k++){
			if(k == 0 && !m_confb[csd_]){
				continue;
			}
			if(k == 1 && !m_confb[degcoh_]){
				continue;
			}
			for(int j = 0; j < 2; j++){
				if(!m_wigmanip.IsActive(j)){
					continue;
				}
				if(k == 0){
					categories.push_back(csd[j]);
				}
				else{
					categories.push_back(degcoh[j]);
				}
				subresults.push_back("");
				titles.clear(); units.clear(); xyvar.clear(); spidx.clear();
				int iUV = GetUV(j); int iuv = Getuv(j);
				xyvar.push_back(vararray[iUV]);
				xyvar.push_back(vararray[iuv]);
				xyvar.push_back(zarray);
				spidx.push_back(puvidx[iUV]);
				spidx.push_back(puvidx[iuv]);
				spidx.push_back(LongPos_);
				if(k == 0){
					spidx.push_back(CSD_);
					spidx.push_back(CSDphase_);
				}
				else{					
					spidx.push_back(DegCohR_);
				}
				for(int j = 0; j < spidx.size(); j++){
					titles.push_back(TitleLablesDetailed[spidx[j]]);
					units.push_back(UnitLablesDetailed[spidx[j]]);
				}
				if(k == 0){
					WriteResults(*this, nullptr, zpoints, scanvalues, 3, 2, titles, units,
						details, xyvar, CSDxy[j], vararrayd, datad, suppletitles, suppledata, subresults.back());
				}
				else{
					WriteResults(*this, nullptr, zpoints, scanvalues, 3, 2, titles, units,
						details, xyvar, Gammaxy[j], vararrayd, datad, suppletitles, suppledata, subresults.back());
				}
			}
		}
	}

	if(m_confb[aprofile_]){
		string labels[2] = {AProfLabel, OptAProfLabel};
		titles.clear(); units.clear();
		for(int j = 0; j < apidx.size(); j++){
			titles.push_back(TitleLablesDetailed[apidx[j]]);
			units.push_back(UnitLablesDetailed[apidx[j]]);
		}

		for(int n = 0; n <= nopt; n++){
			xyvar.clear();
			for(int j = 0; j < 2; j++){
				if(!m_wigmanip.IsActive(j)){
					continue;
				}
				xyvar.push_back(m_xyWig[n][Getuv(j)]);
			}
			subresults.push_back("");
			categories.push_back(labels[n]);
			WriteResults(*this, nullptr, 1, scanvalues, spdim, spdim, titles, units,
				details, xyvar, AProfiles[n], vararrayd, datad, suppletitles, suppledata, subresults.back());
		}
	}
	if(m_confb[wigner_]){
		string labels[2] = {WignerLabel, OptWignerLabel};
		titles.clear(); units.clear();
		for(int j = 0; j < wpidx.size(); j++){
			titles.push_back(TitleLablesDetailed[wpidx[j]]);
			units.push_back(UnitLablesDetailed[wpidx[j]]);
		}

		vector<vector<vector<double>>> WProfiles(1);
		WProfiles[0].resize(1);
		for(int n = 1; n <= nopt; n++){
			xyvar.clear();
			if(m_wigmanip.IsActive(0)){
				xyvar.push_back(m_xyWig[n][WignerUVPrmU]);
			}
			if(m_wigmanip.IsActive(1)){
				xyvar.push_back(m_xyWig[n][WignerUVPrmV]);
			}
			if(m_wigmanip.IsActive(0)){
				xyvar.push_back(m_xyWig[n][WignerUVPrmu]);
			}
			if(m_wigmanip.IsActive(1)){
				xyvar.push_back(m_xyWig[n][WignerUVPrmv]);
			}
			WProfiles[0][0] = m_Wig[n];
			subresults.push_back("");
			categories.push_back(labels[n]);
			WriteResults(*this, nullptr, 1, scanvalues, 2*spdim, 2*spdim, titles, units,
				details, xyvar, WProfiles, vararrayd, datad, suppletitles, suppledata, subresults.back());
		}
	}
}

void WignerPropagator::f_SetGrid(vector<vector<double>> &vararray)
{
	if(m_confsel[gridspec_] == AutomaticLabel){
		vararray = m_vararray.back();
		int zpoints = (int)m_vararray.size();
		for(int j = 0; j < 2; j++){
			if(!m_wigmanip.IsActive(j)){
				continue;
			}
			int iUV = GetUV(j);
			double delta = vararray[iUV][1]-vararray[iUV][0];
			int hmesh = (int)floor(m_SigmaZ[j][zpoints-1]*GAUSSIAN_MAX_REGION/delta+0.5);
			vararray[iUV].resize(2*hmesh+1);
			for(int n = -hmesh; n <= hmesh; n++){
				vararray[iUV][n+hmesh] = n*delta;
			}
		}
	}
	else{
		int pidx[NumberWignerUVPrm] = {xmesh_, ymesh_, wdxmesh_, wdxmesh_};
		int ridx[NumberWignerUVPrm] = {xrange_, yrange_, wdxrange_, wdyrange_};
		int nridx[NumberWignerUVPrm] = {wnxrange_, wnyrange_, wndxrange_, wndyrange_};
		double delta = 0, xyini;
		for(int j = 0; j < NumberWignerUVPrm; j++){
			vararray[j].resize(1, 0.0);
			if((j == WignerUVPrmU || j == WignerUVPrmu) && !m_wigmanip.IsActive(0)){
				continue;
			}
			if((j == WignerUVPrmV || j == WignerUVPrmv) && !m_wigmanip.IsActive(1)){
				continue;
			}
			int points = (int)floor(0.5+m_conf[pidx[j]]);
			vararray[j].resize(points);
			if(m_confsel[gridspec_] == NormSlitLabel){
				delta = m_confv[nridx[j]][1]-m_confv[nridx[j]][0];
				xyini = m_confv[nridx[j]][0];
			}
			else if(m_confsel[gridspec_] == FixedSlitLabel){
				delta = m_confv[ridx[j]][1]-m_confv[ridx[j]][0];
				xyini = m_confv[ridx[j]][0];
			}
			delta /= max(1, points-1);
			for(int n = 0; n < points; n++){
				vararray[j][n] = xyini+n*delta;
			}
		}
	}
}

void WignerPropagator::f_SliceCSD(int zstep, vector<vector<double>> &F, 
	vector<vector<vector<vector<double>>>> *CSD)
{
	m_mesh[zstep].resize(NumberWignerUVPrm);
	m_hmesh[zstep].resize(NumberWignerUVPrm);

	m_wigmanip.GetMeshPoints(m_mesh[zstep]);
	for(int j = 0; j < NumberWignerUVPrm; j++){
		m_hmesh[zstep][j] = (m_mesh[zstep][j]-1)/2;
	}

	for(int n = 0; n < m_CSD.size(); n++){
		m_CSD[n][zstep].resize(m_mesh[zstep][WignerUVPrmU]);
		for(int i = 0; i < m_mesh[zstep][WignerUVPrmU]; i++){
			m_CSD[n][zstep][i].resize(m_mesh[zstep][WignerUVPrmV]);
			for(int j = 0; j < m_mesh[zstep][WignerUVPrmV]; j++){
				if(CSD == nullptr){
					m_CSD[n][zstep][i][j].resize(1, vector<double> {0});
					m_CSD[n][zstep][i][j][0][0] = F[i][j];
					continue;
				}
				m_CSD[n][zstep][i][j].resize(2);
				m_CSD[n][zstep][i][j][0].resize(m_mesh[zstep][WignerUVPrmu]);
				for(int k = 0; k < m_mesh[zstep][WignerUVPrmu]; k++){
					m_CSD[n][zstep][i][j][0][k] = CSD[n][i][j][k][m_hmesh[zstep][WignerUVPrmv]];
				}
				m_CSD[n][zstep][i][j][1].resize(m_mesh[zstep][WignerUVPrmv]);
				for(int l = 0; l < m_mesh[zstep][WignerUVPrmv]; l++){
					m_CSD[n][zstep][i][j][1][l] = CSD[n][i][j][m_hmesh[zstep][WignerUVPrmu]][l];
				}
			}
		}
	}
}

void WignerPropagator::f_ScatterCSD(int zstep, bool single)
{
	int target = zstep%m_mpiprocesses;
	if(m_rank != target){
		m_mesh[zstep].resize(NumberWignerUVPrm);
		m_hmesh[zstep].resize(NumberWignerUVPrm);
	}
	if(m_thread != nullptr){
		m_thread->Bcast(m_mesh[zstep].data(), NumberWignerUVPrm, MPI_INT, target, m_rank);
		m_thread->Bcast(m_hmesh[zstep].data(), NumberWignerUVPrm, MPI_INT, target, m_rank);
		for(int j = 0; j < 2; j++){
			m_thread->Bcast(&m_SigmaZ[j][zstep], 1, MPI_DOUBLE, target, m_rank);
		}
	}
	else{
		MPI_Bcast(m_mesh[zstep].data(), NumberWignerUVPrm, MPI_INT, target, MPI_COMM_WORLD);
		MPI_Bcast(m_hmesh[zstep].data(), NumberWignerUVPrm, MPI_INT, target, MPI_COMM_WORLD);
		for(int j = 0; j < 2; j++){
			MPI_Bcast(&m_SigmaZ[j][zstep], 1, MPI_DOUBLE, target, MPI_COMM_WORLD);
		}
	}
	if(m_rank != target){
		m_vararray[zstep].resize(NumberWignerUVPrm);
		for(int i = 0; i < NumberWignerUVPrm; i++){
			m_vararray[zstep][i].resize(m_mesh[zstep][i]);
		}
	}

	if(m_rank != target){
		for(int n = 0; n < m_CSD.size(); n++){
			m_CSD[n][zstep].resize(m_mesh[zstep][WignerUVPrmU]);
			for(int i = 0; i < m_mesh[zstep][WignerUVPrmU]; i++){
				m_CSD[n][zstep][i].resize(m_mesh[zstep][WignerUVPrmV]);
				for(int j = 0; j < m_mesh[zstep][WignerUVPrmV]; j++){
					if(single){
						m_CSD[n][zstep][i][j].resize(1, vector<double> {0});
					}
					else{
						m_CSD[n][zstep][i][j].resize(2);
						m_CSD[n][zstep][i][j][0].resize(m_mesh[zstep][WignerUVPrmu]);
						m_CSD[n][zstep][i][j][1].resize(m_mesh[zstep][WignerUVPrmv]);
					}
				}
			}
		}
	}

	int ntotal = m_mesh[zstep][WignerUVPrmU]*m_mesh[zstep][WignerUVPrmV];
	int nuv = m_mesh[zstep][WignerUVPrmu]+m_mesh[zstep][WignerUVPrmv];
	if(!single){
		ntotal *= nuv;
	}
	vector<double> ws(ntotal);
	for(int n = 0; n < m_CSD.size(); n++){
		if(m_rank == target){
			for(int i = 0; i < m_mesh[zstep][WignerUVPrmU]; i++){
				for(int j = 0; j < m_mesh[zstep][WignerUVPrmV]; j++){
					int ij = i*m_mesh[zstep][WignerUVPrmV]+j;
					if(single){
						ws[ij] = m_CSD[n][zstep][i][j][0][0];
					}
					else{						
						for(int k = 0; k < m_mesh[zstep][WignerUVPrmu]; k++){
							ws[ij*nuv+k] = m_CSD[n][zstep][i][j][0][k];
						}
						for(int l = 0; l < m_mesh[zstep][WignerUVPrmv]; l++){
							ws[ij*nuv+m_mesh[zstep][WignerUVPrmu]+l] = m_CSD[n][zstep][i][j][1][l];
						}
					}
				}
			}
		}
		if(m_thread != nullptr){
			m_thread->Bcast(ws.data(), ntotal, MPI_DOUBLE, target, m_rank);
		}
		else{
			MPI_Bcast(ws.data(), ntotal, MPI_DOUBLE, target, MPI_COMM_WORLD);
		}
		if(m_rank != target){
			for(int i = 0; i < m_mesh[zstep][WignerUVPrmU]; i++){
				for(int j = 0; j < m_mesh[zstep][WignerUVPrmV]; j++){
					int ij = i*m_mesh[zstep][WignerUVPrmV]+j;
					if(single){
						m_CSD[n][zstep][i][j][0][0] = ws[ij];
					}
					else{
						for(int k = 0; k < m_mesh[zstep][WignerUVPrmu]; k++){
							m_CSD[n][zstep][i][j][0][k] = ws[ij*nuv+k];
						}
						for(int l = 0; l < m_mesh[zstep][WignerUVPrmv]; l++){
							m_CSD[n][zstep][i][j][1][l] = ws[ij*nuv+m_mesh[zstep][WignerUVPrmu]+l];
						}
					}
				}
			}
		}
	}

	if(m_thread != nullptr){
		for(int i = 0; i < NumberWignerUVPrm; i++){
			m_thread->Bcast(m_vararray[zstep][i].data(), m_mesh[zstep][i], MPI_DOUBLE, target, m_rank);
		}
	}
	else{
		for(int i = 0; i < NumberWignerUVPrm; i++){
			MPI_Bcast(m_vararray[zstep][i].data(), m_mesh[zstep][i], MPI_DOUBLE, target, MPI_COMM_WORLD);
		}
	}

}

void WignerPropagator::f_GetProfile(int zstep,
	vector<vector<double>> &vararray, vector<double> &Profile)
{
	f_GetValues(zstep, -1, 0, vararray, Profile);
}

void WignerPropagator::f_GetCSD(int zstep,
	vector<vector<double>> &vararray, vector<vector<double>> *CSD)
{
	for(int n = 0; n < 2; n++){
		for(int jxy = 0; jxy < 2; jxy++){
			if(m_wigmanip.IsActive(jxy)){
				f_GetValues(zstep, jxy, n, vararray, CSD[jxy][n]);
			}
		}
	}
	if(m_confb[degcoh_]){
		for(int jxy = 0; jxy < 2; jxy++){
			if(!m_wigmanip.IsActive(jxy)){
				continue;
			}
			CSD[jxy][2] = CSD[jxy][0];
			int iUV = GetUV(jxy);
			int iuv = Getuv(jxy);
			f_GetGamma(zstep, jxy, vararray[iUV], vararray[iuv], CSD[jxy]);
		}
	}
}

void WignerPropagator::f_GetGamma(int zstep, int jxy,
	vector<double> &UV, vector<double> &uv, vector<vector<double>> &CSD)
{
	int oUV, ouv, iUV, iuv;
	int mesh[2] = {(int)UV.size(), (int)uv.size()};

	if(jxy == 0){
		iUV = WignerUVPrmU;
		iuv = WignerUVPrmu;
		oUV = m_hmesh[zstep][WignerUVPrmV]; // center for y
	}
	else{
		iUV = WignerUVPrmV;
		iuv = WignerUVPrmv;
		oUV = m_hmesh[zstep][WignerUVPrmU]; // center for x
	}
	ouv = m_hmesh[zstep][iuv]; // center for deleta x/y
	double dgrid = m_vararray[zstep][iUV][1]-m_vararray[zstep][iUV][0];

	double delta, f12[2], UV12[2];
	int ifin, index;
	ifin = 2; // interpolation rank, linear: 2, quadratic: 3
	vector<double> a(ifin);

	CSD[2].resize(mesh[0]*mesh[1], 0.0);
	for(int j = 0; j < mesh[1]; j++){
		for(int i = 0; i < mesh[0]; i++){
			if(CSD[2][i+j*mesh[0]] == 0){
				continue;
			}
			UV12[0] = UV[i]-uv[j]/2;
			UV12[1] = UV[i]+uv[j]/2;
			if(m_confsel[gridspec_] == NormSlitLabel){
				UV12[0] *= m_SigmaZ[jxy][zstep];
				UV12[1] *= m_SigmaZ[jxy][zstep];
			}

			f12[0] = f12[1] = 0;
			for(int k = 0; k < 2; k++){
				interpolant2d(ifin, UV12[k], dgrid, m_hmesh[zstep][iUV], &delta, &index);
				if(index < 0){
					continue;
				}
				setinterpolant(ifin, delta, a);
				f12[k] = 0;
				for(int ixy = 0; ixy < ifin; ixy++){
					if(jxy == 0){
						f12[k] += m_CSD[0][zstep][index+ixy][oUV][jxy][ouv]*a[ixy];
					}
					else{
						f12[k] += m_CSD[0][zstep][oUV][index+ixy][jxy][ouv]*a[ixy];
					}
				}
			}
			if(f12[0]*f12[1] <= 0){
				CSD[2][i+j*mesh[0]] = 0;
			}
			else{
				CSD[2][i+j*mesh[0]] /= sqrt(f12[0]*f12[1]);
				CSD[2][i+j*mesh[0]] = min(1.0, CSD[2][i+j*mesh[0]]);
			}
		}
	}

#ifdef _DEBUG
	string xytitles[NumberWignerUVPrm] = {"x", "y", "dx", "dy"};
	vector<string> titles{xytitles[iUV], xytitles[iuv], "Gamma"};
	if(!WigPropGamma.empty()){
		ofstream debug_out(WigPropGamma);
		PrintDebugItems(debug_out, titles);
		vector<double> items(titles.size());

		for(int i = 0; i < mesh[0]; i++){
			items[0] = UV[i];
			for(int j = 0; j < mesh[1]; j++){
				items[1] = uv[j];
				items[2] = CSD[2][i+j*mesh[0]];
				PrintDebugItems(debug_out, items);
			}
		}
		debug_out.close();
	}
#endif
}

void WignerPropagator::f_GetValues(int zstep, int jxy, int reim,
	vector<vector<double>> &vararray, vector<double> &CSD)
{
	int index[2], xymesh[2], iUV[2];

	if(jxy < 0){
		iUV[0] = WignerUVPrmU;
		iUV[1] = WignerUVPrmV;
	}
	else if(jxy == 0){
		iUV[0] = WignerUVPrmU;
		iUV[1] = WignerUVPrmu;
	}
	else{
		iUV[0] = WignerUVPrmV;
		iUV[1] = WignerUVPrmv;
	}

	int ifin[2] = {1, 1};
	vector<double> a[2];
	double dgrid[2];
	for(int j = 0; j < 2; j++){
		a[j].resize(1, 1.0);
		xymesh[j] = (int)vararray[iUV[j]].size();
		if(jxy >= 0 || m_wigmanip.IsActive(j)){
			ifin[j] = 3; // interpolation rank, linear: 2, quadratic: 3
			dgrid[j] = m_vararray[zstep][iUV[j]][1]-m_vararray[zstep][iUV[j]][0];
			a[j].resize(ifin[j], 1.0);
		}
	}
	CSD.resize(xymesh[0]*xymesh[1]);
	fill(CSD.begin(), CSD.end(), 0.0);

	int iu0;
	if(jxy < 0){
		if(m_CSD.size() == 1){
			iu0 = 0;
		}
		else{
			iu0 = m_hmesh[zstep][WignerUVPrmu];
		}
	}
	else if(jxy == 0){
		iu0 = m_hmesh[zstep][WignerUVPrmV];
	}
	else{
		iu0 = m_hmesh[zstep][WignerUVPrmU];
	}
	double delta, UV[2];
	bool isnorm = m_confsel[gridspec_] == NormSlitLabel;
	for(int j = 0; j < xymesh[1]; j++){
		UV[1] = vararray[iUV[1]][j];
		if(isnorm){
			if(jxy < 0){
				UV[1] *= m_SigmaZ[1][zstep];
			}
			else{
				UV[1] *= m_SigmaZ[jxy][zstep];
			}
		}
		interpolant2d(ifin[1], UV[1], dgrid[1], m_hmesh[zstep][iUV[1]], &delta, &index[1]);
		if(index[1] < 0){
			continue;
		}
		setinterpolant(ifin[1], delta, a[1]);
		for(int i = 0; i < xymesh[0]; i++){
			UV[0] = vararray[iUV[0]][i];
			if(isnorm){
				if(jxy < 0){
					UV[0] *= m_SigmaZ[0][zstep];
				}
				else{
					UV[0] *= m_SigmaZ[jxy][zstep];
				}
			}
			interpolant2d(ifin[0], UV[0], dgrid[0], m_hmesh[zstep][iUV[0]], &delta, &index[0]);
			if(index[0] < 0){
				continue;
			}
			setinterpolant(ifin[0], delta, a[0]);
			double prof = 0;
			for(int ix = 0; ix < ifin[0]; ix++){
				for(int iy = 0; iy < ifin[1]; iy++){
					if(jxy < 0){
						prof += m_CSD[reim][zstep][index[0]+ix][index[1]+iy][0][iu0]*a[0][ix]*a[1][iy];
					}
					else if(jxy == 0){
						prof += m_CSD[reim][zstep][index[0]+ix][iu0][0][index[1]+iy]*a[0][ix]*a[1][iy];
					}
					else{
						prof += m_CSD[reim][zstep][iu0][index[0]+ix][1][index[1]+iy]*a[0][ix]*a[1][iy];
					}
				}
			}
			CSD[j*xymesh[0]+i] = prof;
		}
	}

#ifdef _DEBUG
	string xytitles[NumberWignerUVPrm] = {"x", "y", "dx", "dy"};
	vector<string> titles{xytitles[iUV[0]], xytitles[iUV[1]], "Flux"};
	if(!WigPropSpatialOrg.empty()){
		ofstream debug_out(WigPropSpatialOrg);
		PrintDebugItems(debug_out, titles);
		vector<double> items(titles.size());

		for(int i = -m_hmesh[zstep][iUV[0]]; i <= m_hmesh[zstep][iUV[0]]; i++){
			items[0] = i*dgrid[0];
			int ii = i+m_hmesh[zstep][iUV[0]];
			for(int j = -m_hmesh[zstep][iUV[1]]; j <= m_hmesh[zstep][iUV[1]]; j++){
				int jj = j+m_hmesh[zstep][iUV[1]];
				items[1] = j*dgrid[1];
				if(jxy < 0){
					items[2] = m_CSD[reim][zstep][ii][jj][0][iu0];
				}
				else if(jxy == 0){
					items[2] = m_CSD[reim][zstep][ii][iu0][0][jj];
				}
				else{
					items[2] = m_CSD[reim][zstep][iu0][ii][1][jj];
				}
				PrintDebugItems(debug_out, items);
			}
		}
		debug_out.close();
	}

	if(!WigPropSpatialInt.empty()){
		ofstream debug_out(WigPropSpatialInt);
		PrintDebugItems(debug_out, titles);
		vector<double> items((int)titles.size());
		int xymesh[2] = {(int)vararray[iUV[0]].size(), (int)vararray[iUV[1]].size()};
		for(int i = 0; i < xymesh[0]; i++){
			items[0] = vararray[iUV[0]][i];
			for(int j = 0; j < xymesh[1]; j++){
				items[1] = vararray[iUV[1]][j];
				items[2] = CSD[j*xymesh[0]+i];
				PrintDebugItems(debug_out, items);
			}
		}
		debug_out.close();
	}
#endif
}
