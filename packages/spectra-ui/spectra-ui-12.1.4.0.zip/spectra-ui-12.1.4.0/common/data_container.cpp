#include "data_container.h"
#include "spectra_input.h"
#include "function_statistics.h"
#include "common.h"
#include "numerical_common_definitions.h"
#include "fast_fourier_transform.h"
#include "interpolation.h"

//---------------------------
// files for debugging
string DataContProf;
string DataContFFT;
string DataInterp;
string DataApplDisp;

DataContainer::DataContainer()
{
	m_dimension = -1;
#ifdef _DEBUG
//DataContProf  = "..\\debug\\data_conf_prof.dat";
//DataContFFT  = "..\\debug\\data_conf_fft.dat";
//DataInterp = "..\\debug\\data_interp.dat";
//DataApplDisp = "..\\debug\\data_disp.dat";
#endif
}

void DataContainer::Set1D(
	vector<string> &titles, vector<vector<double>> &values)
{
	m_titles = titles;
	m_dimension = 1;
	m_datasets = (int)min(titles.size(), values.size())-m_dimension;
	if(m_datasets <= 0){
		m_datasets = 0;
		return;
	}
	m_var.resize(m_dimension);
	m_items1d.resize(m_datasets);
	m_var[0] = values[0];
	for(int j = 0; j < m_datasets; j++){
		m_items1d[j] = values[j+1];
	}
	m_spl.resize(m_datasets);
}

void DataContainer::Set2D(vector<string> &titles, 
	vector<vector<double>> &variables, vector<vector<vector<double>>> values)
{
	m_titles = titles;
	m_dimension = 2;
	m_datasets = (int)values.size();
	if(m_datasets <= 0){
		m_datasets = 0;
		return;
	}
	m_var.resize(m_dimension);
	m_items2d.resize(m_datasets);
	for(int j = 0; j < 2; j++){
		m_var[j] = variables[j];
	}
	for(int j = 0; j < m_datasets; j++){
		m_items2d[j] = values[j];
	}
	m_spl.resize(m_datasets);
	m_statidx = -1;
}

bool DataContainer::Set(
	picojson::object &obj, int dimension, vector<string> &titles)
{
	m_dimension = dimension;
	if(m_dimension < 1 || m_dimension > 2){
		throw runtime_error("Dimension should be 1 or 2.");
		return false;
	}

	m_titles = titles;
	m_datasets = (int)titles.size()-m_dimension;
	if(m_datasets < 0){
		throw runtime_error("Number of titles not enough.");
		return false;
	}
	m_spl.resize(m_datasets);

	m_var.resize(m_dimension);
	if(m_dimension == 1){
		m_items1d.resize(m_datasets);
	}
	else{
		m_items2d.resize(m_datasets);
		m_statidx = -1;
	}

	size_t nsize = 0, nsize2d[2] = {0, 0};
	vector<picojson::array> buffer;
	try {
		picojson::array jtitles = obj[DataTitlesLabel].get<picojson::array>();
		if(jtitles.size() < titles.size()){
			throw runtime_error("Number of titles in the object not enough.");
		}

		map<string, int> titlemap;
		for(int i = 0; i < jtitles.size(); i++){
			titlemap.insert(make_pair(jtitles[i].get<string>(), i));
		}

		picojson::array dataarray = obj[DataLabel].get<picojson::array>();
		int index;
		vector<double> data;
		for(int i = 0; i < titles.size(); i++){
			index = titlemap[titles[i]];
			picojson::array darray = dataarray.at(index).get<picojson::array>();
			if(dimension == 2){
				if(i < 2){
					nsize2d[i] = darray.size();
				}
				else{
					if(darray.size() != nsize2d[1]){
						throw runtime_error("Data size not consistent.");
					}
					picojson::array darrtmp 
						= darray.at(0).get<picojson::array>();
					if(darrtmp.size() != nsize2d[0]){
						throw runtime_error("Data size not consistent.");
					}
				}
			}
			else{
				if(i == 0){
					nsize = darray.size();
				}
				else{
					if(darray.size() != nsize){
						throw runtime_error("Data size not consistent.");
					}
				}
			}
			buffer.push_back(darray);
		}
	}
	catch (const out_of_range &e){
		cerr << "Data object invalid format: " << e.what() << endl;
		return false;
	}
	catch (const exception &e){
		cerr << e.what() << endl;
		return false;
	}
	catch (...) {
		return false;
	}

	if(m_dimension == 1){
		m_var.resize(1);
		m_items1d.resize(m_datasets);
		ConvertArray1D(buffer[0], nsize, &m_var[0]);
		for(int i = 0; i < m_datasets; i++){
			ConvertArray1D(buffer[i+1], nsize, &m_items1d[i]);
		}
	}
	else{
		m_var.resize(2);
		m_items2d.resize(m_datasets);
		ConvertArray1D(buffer[0], nsize2d[0], &m_var[0]);
		ConvertArray1D(buffer[1], nsize2d[1], &m_var[1]);
		for(int i = 0; i < m_datasets; i++){
			ConvertArray2D(buffer[i+2], nsize2d, &m_items2d[i]);
		}
	}

	return true;
}

void DataContainer::ConvertUnit(int j, double coef, bool isvar)
{
	if(isvar){
		m_var[j] *= coef;
	}
	else if(m_dimension == 1){
		m_items1d[j] *= coef;
	}
	else{
		for(int n = 0; n < m_var[0].size(); n++){
			m_items2d[j][n] *= coef;
		}
	}
}

void DataContainer::ConvertArray1D(picojson::array &arr, size_t nsize, vector<double> *data)
{
	data->resize(nsize);
	for(int n = 0; n < nsize; n++){
		(*data)[n] = arr.at(n).get<double>();
	}
}

void DataContainer::ConvertArray2D(picojson::array &arr, size_t nsize[], vector<vector<double>> *data)
{
	data->resize(nsize[0]);
	for(int n = 0; n < nsize[0]; n++){
		(*data)[n].resize(nsize[1]);
	}
	for(int m = 0; m < nsize[1]; m++){
		picojson::array darrtmp = 
				arr.at(m).get<picojson::array>();
		for(int n = 0; n < nsize[0]; n++){
			(*data)[n][m] = darrtmp.at(n).get<double>();
		}
	}
}

void DataContainer::ApplyDispersion(double alpha)
{
	vector<double> data(m_var[0].size());
	Spline spl;
	for(int i = 0; i < m_datasets; i++){
		for(int j = 0; j < m_var[1].size(); j++){
			for(int n = 0; n < m_var[0].size(); n++){
				data[n] = m_items2d[i][n][j];
			}
			spl.SetSpline((int)m_var[0].size(), &m_var[0], &data, true);
			for(int n = 0; n < m_var[0].size(); n++){
				m_items2d[i][n][j] = spl.GetValue(m_var[0][n]-alpha*m_var[1][j], true);
			}
		}
	}

#ifdef _DEBUG
	if(!DataApplDisp.empty()){
		ofstream debug_out(DataApplDisp);
		PrintDebugItems(debug_out, m_titles);
		vector<double> items(m_datasets+2);
		for(int n = 0; n < m_var[0].size(); n++){
			items[0] = m_var[0][n];
			for(int j = 0; j < m_var[1].size(); j++){
				items[1] = m_var[1][j];
				for(int i = 0; i < m_datasets; i++){
					items[2+i] = m_items2d[i][n][j];
				}
				PrintDebugItems(debug_out, items);
			}
		}
		debug_out.close();
	}
#endif
}


void DataContainer::GetArray1D(int j, vector<double> *arr)
{
	if(j < 0 || j >= m_datasets+1){
		return;
	}
	*arr = j == 0 ? m_var[0] : m_items1d[j-1];
}

void DataContainer::GetVariable(int j, vector<double> *arr)
{
	*arr = m_var[j];
}

double DataContainer::GetElement2D(int j, int index[])
{
	return m_items2d[j][index[0]][index[1]];
}

bool DataContainer::MakeStatistics(int index)
{
	int mesh[2];
	double sn = 0, dxy[2], xymean[2], zxy = 0;

	for(int j = 0; j < 2; j++){
		mesh[j] = (int)m_var[j].size();
	}
	vector<double> zprj[2];
	for(int j = 0; j < 2; j++){
		zprj[j].resize(mesh[j], 0);
		for(int nx = 0; nx < mesh[0]; nx++){
			for(int ny = 0; ny < mesh[1]; ny++){
				zprj[j][j==0?nx:ny] += m_items2d[index][nx][ny];
				if(j == 0){
					sn += m_items2d[index][nx][ny];
				}
			}
		}
		dxy[j] = (m_var[j][mesh[j]-1]-m_var[j][0])/(double)((mesh[j]-1));
	}
	sn *= dxy[0]*dxy[1];
	m_volume = sn;
	if(sn < 0.0){
		return false;
	}
	vector<vector<double>> znorm;
	znorm.resize(mesh[0]);
	for(int nx = 0; nx < mesh[0]; nx++){
		znorm[nx].resize(mesh[1]);
		for(int ny = 0; ny < mesh[1]; ny++){
			znorm[nx][ny] = m_items2d[index][nx][ny]/sn;
		}
	}

	double area, peak, stdpk;
	for(int j = 0; j < 2; j++){
		FunctionStatistics stats(mesh[j], &m_var[j], &zprj[j]);
		stats.GetStatistics(&area, &xymean[j], &peak, &m_stdsize[j], &stdpk, 0);
	}

	for(int nx = 0; nx < mesh[0]; nx++){
		for(int ny = 0; ny < mesh[1]; ny++){
			zxy += znorm[nx][ny]*(m_var[0][nx]-xymean[0])*(m_var[1][ny]-xymean[1]);
		}
	}
	zxy *= dxy[0]*dxy[1];

	m_stdemitt = m_stdsize[0]*m_stdsize[1];
	m_stdemitt *= m_stdemitt;
	m_stdemitt -= zxy*zxy;
	if(m_stdemitt < 0){
		return false;
	}
	m_stdemitt = sqrt(m_stdemitt);
	m_alpha = -zxy/m_stdemitt;

	m_statidx = index;
	return true;
}

void DataContainer::GetStatistics(double stdsize[], double *stdarea, double *alpha, int index)
{
	if(m_dimension == 1){
		double dummy;
		FunctionStatistics fstats((int)m_var[0].size(), &m_var[0], &m_items1d[index]);
		fstats.GetStatistics(stdarea, &dummy, &dummy, &stdsize[0], &dummy, 0);
		return;
	}
	if(m_statidx != index){
		MakeStatistics(index);
	}
	for(int j = 0; j < 2; j++){
		stdsize[j] = m_stdsize[j];
	}
	*stdarea = m_stdemitt;
	*alpha = m_alpha;
}

void DataContainer::GetSliceStatistics(int jvar, int index, vector<double> &area, vector<double> &size)
{
	double dummy;
	if(m_dimension == 1){
		area.resize(1);
		size.resize(1);
		FunctionStatistics fstats((int)m_var[0].size(), &m_var[0], &m_items1d[index]);
		fstats.GetStatistics(&area[0], &dummy, &dummy, &size[0], &dummy, 0);
		return;
	}

	int ndata = (int)m_var[1-jvar].size();
	int mdata = (int)m_var[jvar].size();
	int idx[2];
	area.resize(ndata);
	size.resize(ndata);
	vector<double> item(mdata);
	for(int n = 0; n < ndata; n++){
		idx[1-jvar] = n;
		for(int m = 0; m < mdata; m++){
			idx[jvar] = m;
			item[m] =  m_items2d[index][idx[0]][idx[1]];
		}
		FunctionStatistics fstats(mdata, &m_var[jvar], &item);
		fstats.GetStatistics(&area[n], &dummy, &dummy, &size[n], &dummy, 0, false);
	}
}

double DataContainer::GetVolume(int item)
{
	if(m_dimension == 2){
		if(m_statidx != item){
			MakeStatistics(item);
		}
		return m_volume;
	}
	Spline spl;
	spl.SetSpline((int)m_var[0].size(), &m_var[0], &m_items1d[item]);
	return spl.Integrate();
}

void DataContainer::GetProjection(int j, int item, vector<double> *arr)
{
	int idx[2];
	arr->resize(m_var[j].size(), 0.0);
	for(int n = 0; n < m_var[j].size(); n++){
		idx[j] = n;
		for(int m = 0; m < m_var[1-j].size(); m++){
			idx[1-j] = m;
			(*arr)[n] += m_items2d[item][idx[0]][idx[1]];
		}
	}
	*arr *= m_var[1-j][1]-m_var[1-j][0];
}

void DataContainer::GetFT(int item, vector<double> &varinv,
    vector<vector<double>> &FT, double dtmin, double *typlen, 
	int rowindex) 
	// rowindex-> 1D: ignored, 
	//			  2D: -1 for projected, >= 0 for m_var[1]
{
    double dtime, dtimeav, dtinv, pos;
    int index, nfft;
    double *currentdata;

	double Imax = 0, Iavg = 0;
	int imax = 0, iini, ifin, ndata = (int)m_var[0].size();
	vector<double> Iarr;
	double vol = GetVolume(item);
	if(m_dimension == 1){
		Iarr = m_items1d[item];
	}
	else{
		double dvar1 = m_var[1].size() > 1?m_var[1][1]-m_var[1][0]:1.0;
		Iarr.resize(ndata);
		for(int n = 0; n < ndata; n++){
			if (rowindex < 0){
				Iarr[n] = vectorsum(m_items2d[item][n], -1)*dvar1;
			}
			else{
				Iarr[n] = m_items2d[item][n][rowindex];
			}
		}
	}
	Iarr /= vol;

    for(int n = 0; n < ndata; n++){
		Iavg += Iarr[n];
		if(Iarr[n] > Imax){
			imax = n;
			Imax = Iarr[n];
		}
	}
	Iavg /= ndata;

	iini = ifin = imax;
	do{
		if(iini == 0){
			break;
		}
		iini--;
	}while(Iarr[iini]-Iavg >= (Imax-Iavg)*0.5);

	do{
		if(ifin >= ndata-1){
			break;
		}
		ifin++;
	}while(Iarr[ifin]-Iavg >= (Imax-Iavg)*0.5);
	*typlen = 0.5*(m_var[0][ifin]-m_var[0][iini]);

    dtime = m_var[0][1]-m_var[0][0];
    for(int n = 2; n < ndata; n++){
        dtime = min(dtime, m_var[0][n]-m_var[0][n-1]);
    }
    dtimeav = (m_var[0][ndata-1]-m_var[0][0])/(double)(ndata-1);
    dtime = max(dtimeav*0.1, dtime);
    if(dtmin > INFINITESIMAL){
        dtime = min(dtmin, dtime);
    }

    int ntime = (int)ceil(fabs(m_var[0][ndata-1]-m_var[0][0])/dtime);
    nfft = 1;
    while(nfft < ntime){
        nfft <<= 1;
    }
    nfft <<= 4;

    FastFourierTransform currentfft(1, nfft);

    currentdata = (double *)malloc(sizeof(double)*nfft);

	Spline profile;
	double dzero = 0.0;
	profile.Initialize(ndata, &m_var[0], &Iarr); 
    for(int n = 0; n < nfft; n++){
		index = fft_index(n, nfft, 1);
		pos = (double)index*dtime;
		currentdata[n] = profile.GetValue(pos, true, nullptr, &dzero)*dtime;
	}

#ifdef _DEBUG
	if (!DataContProf.empty()){
		vector<double> posa(nfft), curra(nfft);
		for (int n = 0; n < nfft; n++){
			posa[n] = (double)fft_index(n, nfft, 1)*dtime;
			curra[n] = currentdata[n];
		}
		ofstream debug_out(DataContProf);
		PrintDebugPair(debug_out, posa, curra, nfft);
		debug_out.close();
	}
#endif

	currentfft.DoRealFFT(currentdata, 1);

	if(FT.size() < 2){
		FT.resize(2);
	}
	for(int j = 0; j < 2; j++){
		if(FT[j].size() < nfft/2){
			FT[j].resize(nfft/2);
		}
	}
	if(varinv.size() < nfft/2){
		varinv.resize(nfft/2);
	}

    dtinv = 1.0/(dtime*nfft);
    for(int n = 0; n < nfft/2; n++){
        varinv[n] = (double)n*dtinv;
        FT[0][n] = currentdata[2*n];
		FT[1][n] = currentdata[2*n+1];
    }
    free(currentdata);

#ifdef _DEBUG
	if (!DataContFFT.empty()){
		ofstream debug_out(DataContFFT);
		PrintDebugRows(debug_out, varinv, FT, nfft/2);
		debug_out.close();
	}
#endif
}

int DataContainer::GetSize()
{
	if(m_var.size() == 0){
		return 0;
	}
	return (int)m_var[0].size();
}

double DataContainer::GetLocalVolume1D(
	int index, double delta, double x, bool isnormalize)
{
	if(m_dimension == 2){
		double del2[2] = {delta, m_var[1].back()-m_var[1].front()};
		double xy[2] = {x, (m_var[1].back()+m_var[1].front())/2};
		return GetLocalVolume2D(index, del2, xy, isnormalize);
	}
	if(m_spl[index].size() == 0){
		m_spl[index].resize(1);
		f_AllocSpline(index, 0);
	}
	double var[2];
	var[0] = max(m_var[0][0], x-delta/2);
	var[1] = min(m_var[0].back(), x+delta/2);
	double vol = m_spl[index][0].GetOptValue(var[1])-m_spl[index][0].GetOptValue(var[0]);
	if(isnormalize){
		vol /= m_spl[index][0].GetValue(m_var[0].back());
	}
	return vol;
}

double DataContainer::GetLocalVolume2D(
	int index, double delta[], double xy[], bool isnormalize)
{
	double var[2];
	if(index >= 0){ // refresh the monotone spline
		int rows = (int)m_var[1].size();
		if(m_spl[index].size() == 0){
			// allocate spline along x for all  y positions
			m_spl[index].resize(rows);
			for(int m = 0; m < rows; m++){
				f_AllocSpline(index, m);
			}
		}
		var[0] = max(m_var[0][0], xy[0]-delta[0]/2);
		var[1] = min(m_var[0].back(), xy[0]+delta[0]/2);
		m_ws.resize(rows);
		for(int m = 0; m < rows; m++){
			// allocate spline along y for the target x
			m_ws[m] = m_spl[index][m].GetOptValue(var[1])-m_spl[index][m].GetOptValue(var[0]);
		}
		f_AllocSpline(-1, 0);

		if(m_statidx != index){
			MakeStatistics(index);
		}
	}
	var[0] = max(m_var[1][0], xy[1]-delta[1]/2);
	var[1] = min(m_var[1].back(), xy[1]+delta[1]/2);
	double vol = m_mpl.GetOptValue(var[1])-m_mpl.GetOptValue(var[0]);
	if(isnormalize){
		vol /= m_volume;
	}
	return vol;
}

double DataContainer::GetFracThreshold(int index, double thresh)
{
	if(m_statidx != index){
		MakeStatistics(index);
	}

	double threv = thresh*m_volume;
	for(int j = 0; j < 2; j++){
		threv /= m_var[j].back()-m_var[j].front();
	}
	int nsum = 0;
	for(int nx = 0; nx < m_var[0].size(); nx++){
		for(int ny = 0; ny < m_var[1].size(); ny++){
			if(m_items2d[index][nx][ny] > threv){
				nsum++;
			}
		}
	}
	return (double)nsum/m_var[0].size()/m_var[1].size();
}

void DataContainer::f_AllocSpline(int index, int m)
{
	int nr = index < 0 ? 1 : 0;
	int ndata = (int)m_var[nr].size();
/*
	vector<double> var(ndata+1), values(ndata+1);
	double dval[2], dvar;

	for(int n = 0; n <= ndata; n++){
		if(n == 0){
			dval[0] = 0;
			dval[1] = index < 0 ? m_ws[n] :
				(m_dimension == 2 ? m_items2d[index][n][m] : m_items1d[index][n]);
			dvar = m_var[nr][1]-m_var[nr][0];
			var[n] = m_var[nr][0]-dvar/2;
			values[n] = dvar*(dval[0]+dval[1])/2;
		}
		else if(n == ndata){
			dval[0] = index < 0 ? m_ws[n-1] :
				(m_dimension == 2 ? m_items2d[index][n-1][m] : m_items1d[index][n-1]);
			dval[1] = 0;
			dvar = m_var[nr][ndata-1]-m_var[nr][ndata-2];
			var[n] = m_var[nr][ndata-1]+dvar/2;
			values[n] = values[n-1]+dvar*(dval[0]+dval[1])/2;
		}
		else{
			dval[0] = index < 0 ? m_ws[n-1] :
				(m_dimension == 2 ? m_items2d[index][n-1][m] : m_items1d[index][n-1]);
			dval[1] = index < 0 ? m_ws[n] :
				(m_dimension == 2 ? m_items2d[index][n][m] : m_items1d[index][n]);
			dvar = m_var[nr][n]-m_var[nr][n-1];
			var[n] = m_var[nr][n]-dvar/2;
			values[n] = values[n-1]+dvar*(dval[0]+dval[1])/2;
		}
	}
*/
	vector<double> values(ndata), var;
	double dval[2], dvar;

	for(int n = 0; n < ndata; n++){
		if(n == 0){
			dval[0] = 0;
			dval[1] = index < 0 ? m_ws[n] :
				(m_dimension == 2 ? m_items2d[index][n][m] : m_items1d[index][n]);
			dvar = m_var[nr][1]-m_var[nr][0];
			values[n] = dvar*(dval[0]+dval[1])/2;
		}
		else{
			dval[0] = index < 0 ? m_ws[n-1] :
				(m_dimension == 2 ? m_items2d[index][n-1][m] : m_items1d[index][n-1]);
			dval[1] = index < 0 ? m_ws[n] :
				(m_dimension == 2 ? m_items2d[index][n][m] : m_items1d[index][n]);
			dvar = m_var[nr][n]-m_var[nr][n-1];
			values[n] = values[n-1]+dvar*(dval[0]+dval[1])/2;
		}
	}
	var = m_var[nr];

	if(index < 0){
		m_mpl.SetSpline((int)var.size(), &var, &values, false);
	}
	else{
		m_spl[index][m].SetSpline((int)var.size(), &var, &values, false);
	}

#ifdef _DEBUG
	if(!DataInterp.empty()){
		ofstream debug_out(DataInterp);
		PrintDebugPair(debug_out, var, values, (int)var.size());
		debug_out.close();
	}
#endif
}