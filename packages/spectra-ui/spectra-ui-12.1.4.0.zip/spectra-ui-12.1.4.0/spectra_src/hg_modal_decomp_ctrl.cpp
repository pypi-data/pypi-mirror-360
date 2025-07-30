#include "spectra_input.h"
#include "hg_modal_decomp_ctrl.h"
#include "hermite_gauss_decomp.h"
#include "output_utility.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

void WriteModalFlux(SpectraConfig &spconf, 
	vector<string> &titles, vector<string> &units, 
	vector<vector<vector<double>>> &data, string &result)
{
	vector<string> details;
	vector<vector<double>> scanvalues, xyvar;
	vector<vector<vector<double>>> vararrayd;
	vector<vector<vector<vector<double>>>> datad;
	vector<vector<string>> suppletitles;
	vector<vector<double>> suppledata;

	int modes = (int)data[0][0].size();
	titles.push_back(TitleLablesDetailed[ModeNumber_]); 
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

HGModalDecompCtrl::HGModalDecompCtrl(SpectraSolver &spsolver)
	: SpectraSolver(spsolver)
{
}

void HGModalDecompCtrl::Solve(
	vector<string> &subresults, vector<string> &categories,
	vector<vector<double>> *vararray, vector<double> *data)
{
	m_wig4d.SetWavelength(wave_length(m_fixep));

	if(contains(m_calctype, menu::CMDPP)){
		if(contains(m_orgtype, menu::XXpYYp)){
			m_type = WignerType4D;
		}
		else if(contains(m_orgtype, menu::XXpprj)){
			m_type = WignerType2DX;
		}
		else if(contains(m_orgtype, menu::YYpprj)){
			m_type = WignerType2DY;
		}
		else{
			throw runtime_error("Invalid settings.");
			return;
		}
	}
	else{
		if(contains(m_calctype, menu::CMD2d)){
			if(!m_wig4d.LoadData(m_pjoutput)){
				throw runtime_error("Wigner Data Import Failed.");
				return;
			}
		}
		else{
			if(!m_wig4d.LoadData(m_calctype, vararray, data)){
				throw runtime_error("Wigner Data Format Invalid.");
				return;
			}
		}
		m_type = m_wig4d.GetType();
	}

	if(m_type == WignerType4D){
		Solve4D(subresults, categories);
	}
	else{
		Solve2D(subresults, categories);
	}
}

void HGModalDecompCtrl::Solve4D(
	vector<string> &subresults, vector<string> &categories)
{
	int maxmodes[2], cmdmode;
	double dxy[2], xyrange[2], error;
	CMDContainer cmddef;

	for(int j = 0; j < 2; j++){
		maxmodes[j] = (int)floor(0.5+m_confv[HGorderxy_][j]);
		dxy[j] = m_confv[fieldgridxy_][j]*1.0e-3; // mm -> m
		xyrange[j] = m_confv[fieldrangexy_][j]*1.0e-3; // mm -> m
	}

	if(contains(m_calctype, menu::CMDPP)){
		picojson::array pjmaxorder = m_cmd[MaxOrderLabel].get<picojson::array>();
		for(int j = 0; j < 2; j++){
			maxmodes[j] = (int)floor(0.5+pjmaxorder[j].get<double>());
		}
	}

	cmdmode = (int)floor(0.5+m_conf[maxmode_]);

	HGModalDecomp2D hg2d(m_calcstatus, m_accuracy[accinobs_], maxmodes, cmdmode, m_conf[cutoff_], m_conf[fcutoff_], &m_wig4d);

	int csteps = 0;
	if(m_confsel[CMDfld_] != NoneLabel){
		csteps++;
	}
	if(m_confb[CMDint_]){
		csteps++;
	}
	if(m_confb[CMDcmpint_]){
		csteps++;
	}
	if(m_confb[CMDcmp_]){
		csteps += 3;
	}

	if(contains(m_calctype, menu::CMDPP)){
		int maxorder[2];
		double srcsize[2], fnorm;
		vector<int> order;
		vector<double> anmre, anmim;
		RetrieveResult4D(&error, maxorder, srcsize, &fnorm, order, anmre, anmim);
		hg2d.LoadResults(maxorder, srcsize, fnorm, order, anmre, anmim);
		m_calcstatus->SetSubstepNumber(0, 1+csteps);
		if(m_confb[CMDcmp_]){
			hg2d.SetLGContainer(m_rank, m_mpiprocesses, m_thread);
		}
	}
	else{
		hg2d.LoadData();
		if(m_confsel[GSModelXY_] == NoneLabel){
			m_calcstatus->SetSubstepNumber(0, 2);
			m_calcstatus->SetTargetPoint(0, 0.02);
			hg2d.ComputePrjBeamParameters();
			m_calcstatus->SetCurrentOrigin(0);
			m_calcstatus->ResetCurrentStep(0);
			m_calcstatus->SetTargetPoint(0, 1.0);
			m_calcstatus->SetSubstepNumber(0, 4+csteps);
			hg2d.SetLGContainer(m_rank, m_mpiprocesses, m_thread);
			hg2d.GetAnmAll(0, m_rank, m_mpiprocesses, m_thread);
			error = hg2d.GetExpansionError();
		}
		else{
			bool isGS[2] = {false, false};
			if(m_confsel[GSModelXY_] == XOnly || m_confsel[GSModelXY_] == BothFormat){
				isGS[0] = true;
			}
			if(m_confsel[GSModelXY_] == YOnly || m_confsel[GSModelXY_] == BothFormat){
				isGS[1] = true;
			}
			m_calcstatus->SetSubstepNumber(0, 1+csteps);
			hg2d.SetGSModel(isGS, m_rank, m_mpiprocesses, m_thread, &error);
			m_calcstatus->AdvanceStep(0);
		}
	}
	int cmdridx = (int)subresults.size();
	subresults.push_back("");
	categories.push_back(CMDResultLabel);

	double CMDerr[3] = {error, -1, -1};

	vector<string> titles, units, details;
	vector<vector<double>> scanvalues, xyvar;
	vector<vector<vector<double>>> data, vararrayd;
	vector<vector<vector<vector<double>>>> datad;
	vector<vector<string>> suppletitles;
	vector<vector<double>> suppledata;

	subresults.push_back("");
	categories.push_back(CMDModalFluxLabel);
	data.resize(1); data[0].resize(2);
	hg2d.GetFluxConsistency(cmdmode, m_conf[cutoff_], data[0][0], data[0][1]);
	CMDerr[1] = data[0][1].back();
	data[0][1] *= 100.0; // (-) -> %
	data[0][0] *= 100.0; // (-) -> %
	WriteModalFlux(*this, titles, units, data, subresults.back());

	vector<vector<double>> xyarr(2);
	for(int j = 0; j < 2; j++){
		int mesh = (int)floor(0.5+xyrange[j]/dxy[j]);
		xyarr[j].resize(2*mesh+1);
		for(int n = -mesh; n <= mesh; n++){
			xyarr[j][n+mesh] = dxy[j]*n;
		}
	}

	if(m_confsel[CMDfld_] != NoneLabel){
		data.clear();
		string filebin = m_dataname+".bin";
		vector<vector<double>> datari[2];
		hg2d.DumpFieldProfile(IsBinaryFld()?filebin.c_str():nullptr, 
			m_conf[cutoff_], cmdmode, IsJSONFld(), xyarr, datari[0], datari[1], 
			m_rank, m_mpiprocesses, m_thread);
		int modes = (int)datari[0].size();
		if(IsJSONFld()){
			subresults.push_back("");
			categories.push_back(CMDFieldLabel);

			vector<int> index;
			index.push_back(SrcX_); index.push_back(SrcY_); index.push_back(ModeOrder_);
			index.push_back(ModalAmpRe_); index.push_back(ModalAmpIm_);
			titles.resize(index.size());
			units.resize(index.size());
			for(int j = 0; j < index.size(); j++){
				titles[j] = TitleLablesDetailed[index[j]];
				units[j] = UnitLablesDetailed[index[j]];
			}

			vector<double> modeidx(modes);
			for(int p = 0; p < modes; p++){
				modeidx[p] = p;
			}
			xyvar = xyarr;
			for(int j = 0; j < 2; j++){
				xyvar[j] *= 1.0e+3; // m -> mm
			}
			xyvar.push_back(modeidx);
			data.resize(modes);
			for(int p = 0; p < modes; p++){
				data[p].push_back(datari[0][p]);
				data[p].push_back(datari[1][p]);
			}
			WriteResults(*this, nullptr, modes, scanvalues, 3, 2, titles, units, 
				details, xyvar, data, vararrayd, datad, suppletitles, suppledata, subresults.back());
		}
		m_calcstatus->AdvanceStep(0);
	}

	if(m_confb[CMDint_]){
		data.clear();
		hg2d.DumpIntensityProfile(m_conf[cutoff_], cmdmode, xyarr, data, m_rank, m_mpiprocesses, m_thread);
		subresults.push_back("");
		categories.push_back(CMDIntensityLabel);

		vector<int> index;
		index.push_back(SrcX_); index.push_back(SrcY_);
		index.push_back(ModeOrder_); index.push_back(NearFldens_);
		titles.resize(index.size());
		units.resize(index.size());
		for(int j = 0; j < index.size(); j++){
			titles[j] = TitleLablesDetailed[index[j]];
			units[j] = UnitLablesDetailed[index[j]];
		}

		int modes = (int)data.size();
		vector<double> modeidx(modes);
		for(int p = 0; p < modes; p++){
			modeidx[p] = p;
		}
		xyvar = xyarr;
		for(int j = 0; j < 2; j++){
			xyvar[j] *= 1.0e+3; // m -> mm
		}
		xyvar.push_back(modeidx);
		WriteResults(*this, nullptr, modes, scanvalues, 3, 2, titles, units,
			details, xyvar, data, vararrayd, datad, suppletitles, suppledata, subresults.back());
		m_calcstatus->AdvanceStep(0);
	}

	if(m_confb[CMDcmpint_]){
		data.resize(1); xyvar.resize(2);
		hg2d.DumpTotalIntensityProfile(
			m_conf[cutoff_], cmdmode, xyvar, data[0], m_rank, m_mpiprocesses, m_thread);
		subresults.push_back("");
		categories.push_back(CMDCompareIntLabel);

		vector<int> index;
		index.push_back(SrcX_); index.push_back(SrcY_); 
		index.push_back(NearFldens_); index.push_back(ReNearFldens_);
		titles.resize(index.size());
		units.resize(index.size());
		for(int j = 0; j < index.size(); j++){
			titles[j] = TitleLablesDetailed[index[j]];
			units[j] = UnitLablesDetailed[index[j]];
		}
		WriteResults(*this, nullptr, 1, scanvalues, 2, 2, titles, units,
			details, xyvar, data, vararrayd, datad, suppletitles, suppledata, subresults.back());
		m_calcstatus->AdvanceStep(0);
	}

	vector<vector<vector<double>>> wigdata;
	if(m_confb[CMDcmp_]){
		data.clear();
		hg2d.ReconstructExport(
			cmdmode, m_conf[cutoff_], &CMDerr[2], wigdata, m_rank, m_mpiprocesses, m_thread);
		int srcindex[] = {SrcX_, SrcY_};
		int divindex[] = {SrcQX_, SrcQY_};
		string labels[] = {CMDCompareXLabel, CMDCompareYLabel};
		vector<double> xyarr, qarr;
		xyvar.resize(2);
		data.resize(1);
		for(int j = 0; j < 2; j++){
			subresults.push_back("");
			categories.push_back(labels[j]);
			vector<int> index;
			index.push_back(srcindex[j]); index.push_back(divindex[j]);
			index.push_back(WBrill_); index.push_back(ReWBrill_);
			titles.resize(index.size());
			units.resize(index.size());
			for(int j = 0; j < index.size(); j++){
				titles[j] = TitleLablesDetailed[index[j]];
				units[j] = UnitLablesDetailed[index[j]];
			}
			m_wig4d.GetXYQArray(j, xyvar[0], xyvar[1]);
			data[0] = wigdata[j];
			WriteResults(*this, nullptr, 1, scanvalues, 2, 2, titles, units, 
				details, xyvar, data, vararrayd, datad, suppletitles, suppledata, subresults.back());
		}
	}

	hg2d.WriteResults(subresults[cmdridx], CMDerr);

	subresults.push_back("");
	categories.push_back("CPU Time");
	hg2d.WriteCPUTime(subresults.back());
}

void HGModalDecompCtrl::Solve2D(
	vector<string> &subresults, vector<string> &categories)
{
	int imxy, isrcxy, isrcqxy;
	double dxy, xyrange;
	string complabel;
	CMDContainer cmddef;

	if(m_type == WignerType2DX){
		imxy = HGorderx_;
		dxy = m_conf[fieldgridx_]*1.0e-3; // mm -> m
		xyrange = m_conf[fieldrangex_]*1.0e-3;
		isrcxy = SrcX_;
		isrcqxy = SrcQX_;
		complabel = CMDCompareXLabel;
	}
	else{
		imxy = HGordery_;
		dxy = m_conf[fieldgridy_]*1.0e-3; // mm -> m
		xyrange = m_conf[fieldrangey_]*1.0e-3;
		isrcxy = SrcY_;
		isrcqxy = SrcQY_;
		complabel = CMDCompareYLabel;
	}

	int csteps = 0;
	if(m_confsel[CMDfld_] != NoneLabel){
		csteps++;
	}
	if(m_confb[CMDint_]){
		csteps++;
	}
	if(m_confb[CMDcmpint_]){
		csteps++;
	}
	if(m_confb[CMDcmp_]){
		csteps += 3;
	}

	double error = 0;
	int cmdmode = (int)floor(0.5+m_conf[maxmode_]);
	int maxmode = (int)floor(0.5+m_conf[imxy]);

	double srcsize, fnorm;
	vector<double> anmre, anmim;
	if(contains(m_calctype, menu::CMDPP)){
		RetrieveResult2D(&error, &maxmode, &srcsize, &fnorm, anmre, anmim);
	}

	HGModalDecomp hg1d(1, m_calcstatus, m_accuracy[accinobs_], maxmode, m_conf[cutoff_], m_conf[fcutoff_], &m_wig4d);
	if(contains(m_calctype, menu::CMDPP)){
		hg1d.LoadResults(maxmode, srcsize, fnorm, anmre, anmim);
	}
	else{
		hg1d.LoadData();
		if(m_confb[GSModel_]){
			m_calcstatus->SetSubstepNumber(0, 1+csteps);
			hg1d.SetGSModel();
		}
		else{
			m_calcstatus->SetSubstepNumber(0, 1);
			m_calcstatus->SetTargetPoint(0, 0.1);
			hg1d.OptimizeSrcSize();
			m_calcstatus->AdvanceStep(0);
			m_calcstatus->SetCurrentOrigin(0);
			m_calcstatus->ResetCurrentStep(0);
			m_calcstatus->SetTargetPoint(0, 1.0);
			m_calcstatus->SetSubstepNumber(0, 2+csteps);
			hg1d.FourierExpansion();
			hg1d.GetAnm(nullptr, m_rank, m_mpiprocesses, m_thread);
			m_calcstatus->AdvanceStep(0);
			error = hg1d.CholeskyDecomp();
		}
		m_calcstatus->AdvanceStep(0);
	}
	int cmdridx = (int)subresults.size();
	subresults.push_back("");
	categories.push_back(CMDResultLabel);

	double CMDerr[3] = {error, -1, -1};

	vector<string> titles, units, details;
	vector<vector<double>> scanvalues, xyvar;
	vector<vector<vector<double>>> data, vararrayd;
	vector<vector<vector<vector<double>>>> datad;
	vector<vector<string>> suppletitles;
	vector<vector<double>> suppledata;
	vector<int> index;
		
	subresults.push_back("");
	categories.push_back(CMDModalFluxLabel);

	data.resize(1);  data[0].resize(2);
	hg1d.GetFluxConsistency(cmdmode, m_conf[cutoff_], data[0][0], data[0][1]);
	CMDerr[1] = data[0][1].back();
	data[0][1] *= 100.0; // (-) -> %
	data[0][0] *= 100.0; // (-) -> %
	WriteModalFlux(*this, titles, units, data, subresults.back());

	if(m_confsel[CMDfld_] != NoneLabel && m_rank == 0){
		data.clear();
		string filebin = m_dataname+".bin";
		vector<double> xyarr;
		vector<vector<double>> datari[2];
		hg1d.DumpFieldProfile(
			IsBinaryFld()?filebin.c_str():nullptr, 
			m_conf[cutoff_], cmdmode, xyrange, dxy, IsJSONFld(), xyarr, datari[0], datari[1]);
		int modes = (int)datari[0].size();
		if(IsJSONFld()){
			subresults.push_back("");
			categories.push_back(CMDFieldLabel);

			index.push_back(isrcxy); index.push_back(ModeOrder_);
			index.push_back(ModalAmpRe_); index.push_back(ModalAmpIm_);
			titles.resize(index.size());
			units.resize(index.size());
			for(int j = 0; j < index.size(); j++){
				titles[j] = TitleLablesDetailed[index[j]];
				units[j] = UnitLablesDetailed[index[j]];
			}

			vector<double> modeidx(modes);
			for(int p = 0; p < modes; p++){
				modeidx[p] = p;
			}
			xyarr *= 1.0e+3; // m -> mm
			xyvar.push_back(xyarr);
			xyvar.push_back(modeidx);
			data.resize(modes);
			for(int d = 0; d < modes; d++){
				data[d].push_back(datari[0][d]);
				data[d].push_back(datari[1][d]);
			}
			WriteResults(*this, nullptr, modes, scanvalues, 2, 1, titles, units, 
				details, xyvar, data, vararrayd, datad, suppletitles, suppledata, subresults.back());
		}
		m_calcstatus->AdvanceStep(0);
	}

	if(m_confb[CMDint_] && m_rank == 0){
		data.clear();
		vector<double> xyarr;
		hg1d.DumpIntensityProfile(m_conf[cutoff_], cmdmode, xyrange, dxy, xyarr, data);
		subresults.push_back("");
		categories.push_back(CMDIntensityLabel);

		vector<int> index;
		index.push_back(isrcxy); index.push_back(ModeOrder_); index.push_back(NearLinFldens_);
		titles.resize(index.size());
		units.resize(index.size());
		for(int j = 0; j < index.size(); j++){
			titles[j] = TitleLablesDetailed[index[j]];
			units[j] = UnitLablesDetailed[index[j]];
		}

		int modes = (int)data.size();
		vector<double> modeidx(modes);
		for(int p = 0; p < modes; p++){
			modeidx[p] = p;
		}
		xyarr *= 1.0e+3; // m -> mm
		xyvar.clear();
		xyvar.push_back(xyarr);
		xyvar.push_back(modeidx);
		WriteResults(*this, nullptr, modes, scanvalues, 2, 1, titles, units,
			details, xyvar, data, vararrayd, datad, suppletitles, suppledata, subresults.back());
		m_calcstatus->AdvanceStep(0);
	}

	if(m_confb[CMDcmpint_] && m_rank == 0){
		data.clear();
		data.resize(1);
		xyvar.resize(1);
		hg1d.DumpTotalIntensityProfile(m_conf[cutoff_], cmdmode, xyvar[0], data[0]);
		subresults.push_back("");
		categories.push_back(CMDCompareIntLabel);

		index.clear();
		index.push_back(isrcxy); index.push_back(NearLinFldens_); index.push_back(ReNearLinFldens_);
		titles.resize(index.size());
		units.resize(index.size());
		for(int j = 0; j < index.size(); j++){
			titles[j] = TitleLablesDetailed[index[j]];
			units[j] = UnitLablesDetailed[index[j]];
		}
		WriteResults(*this, nullptr, 1, scanvalues, 1, 1, titles, units,
			details, xyvar, data, vararrayd, datad, suppletitles, suppledata, subresults.back());
		m_calcstatus->AdvanceStep(0);
	}

	if(m_confb[CMDcmp_]){
		data.clear();
		data.resize(1);
		data[0].resize(2);
		hg1d.ReconstructExport(cmdmode, 
			m_conf[cutoff_], &CMDerr[2], data[0][1], m_rank, m_mpiprocesses, m_thread);
		subresults.push_back("");
		categories.push_back(complabel);

		index.clear(); xyvar.clear();
		index.push_back(isrcxy); index.push_back(isrcqxy);
		index.push_back(Brill1D_); index.push_back(ReBrill1D_);
		titles.resize(index.size()); units.resize(index.size()); 
		for(int j = 0; j < index.size(); j++){
			titles[j] = TitleLablesDetailed[index[j]];
			units[j] = UnitLablesDetailed[index[j]];
		}
		m_wig4d.RetrieveData(xyvar, data[0][0]);

		WriteResults(*this, nullptr, 1, scanvalues, 2, 2, titles, units, 
			details, xyvar, data, vararrayd, datad, suppletitles, suppledata, subresults.back());
		m_calcstatus->AdvanceStep(0);
	}

	hg1d.WriteResults(subresults[cmdridx], CMDerr);
}

bool HGModalDecompCtrl::RetrieveResult2D(double *err, int *maxorder, 
	double *srcsize, double *fnorm, vector<double> &anmre, vector<double> &anmim)
{
	picojson::object errobj =m_cmd[CMDErrorLabel].get<picojson::object>();
	*err = atof(errobj[MatrixErrLabel].get<string>().c_str())*0.01;
	*maxorder = (int)floor(0.5+m_cmd[MaxOrderLabel].get<double>());
	*srcsize = m_cmd[SrcSizeLabel].get<double>();
	*fnorm = m_cmd[NormFactorLabel].get<double>();
	int nmodes = (*maxorder)+1;
	nmodes *= nmodes;
	return Retrieve_anm(nmodes, anmre, anmim);
}

bool HGModalDecompCtrl::RetrieveResult4D(double *err, int maxorder[], 
	double srcsize[], double *fnorm, vector<int> &order, vector<double> &anmre, vector<double> &anmim)
{
	picojson::object errobj = m_cmd[CMDErrorLabel].get<picojson::object>();
	*err = atof(errobj[MatrixErrLabel].get<string>().c_str())*0.01;
	picojson::array pjmode = m_cmd[MaxOrderLabel].get<picojson::array>();
	picojson::array pjsrc = m_cmd[SrcSizeLabel].get<picojson::array>();
	for(int j = 0; j < 2; j++){
		maxorder[j] = (int)floor(0.5+pjmode[j].get<double>());
		srcsize[j] = pjsrc[j].get<double>();
	}
	*fnorm = m_cmd[NormFactorLabel].get<double>();

	int nmodes = (maxorder[0]+1)*(maxorder[1]+1);
	picojson::array pjorder = m_cmd[OrderLabel].get<picojson::array>();
	if(pjorder.size() != nmodes){
		return false;
	}
	order.resize(pjorder.size());
	for(int n = 0; n < pjorder.size(); n++){
		order[n] = (int)floor(0.5+pjorder[n].get<double>());
	}

	nmodes *= nmodes;
	if(!Retrieve_anm(nmodes, anmre, anmim)){
		return false;
	}
	return true;
}

bool HGModalDecompCtrl::Retrieve_anm(int nmodes, vector<double> &anmre, vector<double> &anmim)
{
	anmre.resize(nmodes, 0.0);
	anmim.resize(nmodes, 0.0);
	if(m_cmd.count(AmplitudeReLabel) > 0){
		// version 11.1 or earlier
		picojson::array pjanmre = m_cmd[AmplitudeReLabel].get<picojson::array>();
		if(pjanmre.size() != nmodes){
			return false;
		}
		picojson::array pjanmim = m_cmd[AmplitudeImLabel].get<picojson::array>();
		if(pjanmim.size() != nmodes){
			return false;
		}
		for(int n = 0; n < nmodes; n++){
			anmre[n] = pjanmre[n].get<double>();
			anmim[n] = pjanmim[n].get<double>();
		}
		return true;
	}
	string labels[2] = {AmplitudeVReLabel, AmplitudeVImLabel};
	string indices[2] = {AmplitudeIndexReLabel, AmplitudeIndexImLabel};
	for(int j = 0; j < 2; j++){
		picojson::array pjval = m_cmd[labels[j]].get<picojson::array>();
		picojson::array pjidx = m_cmd[indices[j]].get<picojson::array>();
		if(pjval.size() != pjidx.size()){
			return false;
		}
		vector<double> &anm = j == 0 ? anmre : anmim;
		for(int n = 0; n < pjidx.size(); n++){
			int index = (int)floor(pjidx[n].get<double>()+0.5);
			if(index >= nmodes){
				return false;
			}
			anm[index] = pjval[n].get<double>();
		}
	}
	return true;
}
