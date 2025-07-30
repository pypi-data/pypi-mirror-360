#include "spectra_config.h"
#include "common.h"
#include "json_writer.h"
#include <math.h>
#include <sstream>
#include <algorithm>
#include <set>
#include <iomanip>

#ifdef _EMSCRIPTEN
#ifdef _MAIN
void set_output(const char *pdataname, const char *poutput){}
#else
#include <emscripten/bind.h>
#include <emscripten.h>
EM_JS(void, set_output, (const char *pdataname, const char *poutput), {
	let output = UTF8ToString(poutput);
	let dataname = UTF8ToString(pdataname);
	SetOutput(dataname, output);
});
#endif
#endif

// constructor
SpectraConfig::SpectraConfig(int serno)
{
	// set default values
	m_acc = DefAccPrm;
	m_accv = DefAccVec;
	m_accb = DefAccBool;
	m_accsel = DefAccSel;
	m_accs = DefAccStr;

	m_src = DefSrcPrm;
	m_srcv = DefSrcVec;
	m_srcb = DefSrcBool;
	m_srcsel = DefSrcSel;
	m_srcs = DefSrcStr;

	m_conf = DefConfPrm;
	m_confv = DefConfVec;
	m_confb = DefConfBool;
	m_confsel = DefConfSel;

	m_outf = DefOutfilePrm;
	m_outfs = DefOutfileStr;
	m_outfsel = DefOutfileSel;

	m_ppconf = DefPreprocPrm;
	m_ppconfsel = DefPreprocSel;

	m_accuracy.resize(NumAccuracyPrm);
	m_accuracy_f = DefAccuracyPrm;
	for(int i = 0; i < NumAccuracyPrm; i++){
		m_accuracy[i] = (int)floor(0.5+DefAccuracyPrm[i]);
	}
	m_accuracy_b = DefAccuracyBool;

	m_parform.resize(NumPartFormatPrm);
	m_parform_f = DefPartFormatPrm;
	m_parformsel = DefPartFormatSel;
	for(int i = 0; i < NumPartFormatPrm; i++){
		m_parform[i] = (int)floor(0.5+DefPartFormatPrm[i]);
	}

	//m_confs = DefConfStr;
	// no configurations available 

	m_iscmdcheck = false;
	m_ispp4apt = false;
	m_2dlink = false;
	m_mpiprocesses = 1;
	m_rank = 0;
	m_scanprmitems = atoi(ScanPrmItems.c_str());
	m_serno = serno;
}

// public functions
void SpectraConfig::LoadJSON(string &input, picojson::object &inobj)
{
	if(inobj.count(FELBunchFactor) > 0){
		m_felbfactor = inobj[FELBunchFactor].get<picojson::object>();
		inobj.erase(FELBunchFactor);
	}
	if(inobj.count(InputLabel) > 0){
		picojson::object iobj = inobj[InputLabel].get<picojson::object>();
		picojson::object confobj = iobj[ConfigLabel].get<picojson::object>();
		string calcid = confobj[TypeLabel].get<string>();
		if(contains(calcid, menu::CMDPP)){
			m_cmd = inobj[CMDResultLabel].get<picojson::object>();
		}
		else if(contains(calcid, menu::CMD2d) || contains(calcid, menu::propagate)){
			m_pjoutput = inobj[OutputLabel].get<picojson::object>();
		}
		inobj = iobj;
	}

	picojson::value val(inobj);
	input = val.serialize(true);
	size_t last = input.find_last_of("\n");
	if(last != string::npos){
		input = input.substr(0, last);
	}

	vector<vector<string>> datalabels;
	vector<string> invalids;

	m_ispreproc = false;
	m_pptype = "";
	m_calctype = "";
	f_LoadSingle(inobj, AccLabel, &Acc, &AccSimple,
		&m_acctype, &m_acc, &m_accv, &m_accb, &m_accsel, &m_accs, &datalabels, &invalids);
	f_LoadSingle(inobj, SrcLabel, &Src, &SrcSimple,
		&m_srctype, &m_src, &m_srcv, &m_srcb, &m_srcsel, &m_srcs, &datalabels, &invalids);
	f_LoadSingle(inobj, ConfigLabel, &Conf, &ConfSimple,
		&m_calctype, &m_conf, &m_confv, &m_confb, &m_confsel, &m_confs, &datalabels, &invalids);

	string dumstr;
	vector<bool> dumb;
	vector<string> dumstrs, dumsel;
	vector<vector<double>> dumvec;
	f_LoadSingle(inobj, OutFileLabel, &Outfile, &OutfileSimple,
		&dumstr, &m_outf, &dumvec, &dumb, &m_outfsel, &m_outfs, &datalabels, &invalids);
	if(inobj.count(PrePLabel) > 0){
		f_LoadSingle(inobj, PrePLabel, &Preproc, &PreprocSimple,
			&dumstr, &m_ppconf, &dumvec, &dumb, &m_ppconfsel, &dumstrs, &datalabels, &invalids);
	}

	if(m_conf[acclevel_] > 0){// version 11.0 
		int acclevel = (int)floor(m_conf[acclevel_]+0.5);
		if(acclevel > 1){
			m_confsel[accuracy_] = CustomLabel;
			fill(m_accuracy.begin(), m_accuracy.end(), acclevel);
		}
		else{
			m_confsel[accuracy_] = DefaultLabel;
		}
	}
	else{
		if(m_confsel[accuracy_] == CustomLabel){
			picojson::object confobj = inobj[ConfigLabel].get<picojson::object>();
			if(confobj.count(AccuracyLabel) > 0){
				vector<double> accuracy = DefAccuracyPrm;
				f_LoadSingle(confobj, AccuracyLabel, &Accuracy, &AccuracySimple,
					&dumstr, &accuracy, &dumvec, &m_accuracy_b, &dumsel, &dumstrs, &datalabels, &invalids);
				for(int i = 0; i < NumAccuracyPrm; i++){
					if(accuracy[i] > 0){
						m_accuracy[i] = (int)floor(0.5+accuracy[i]);
					}
					else{
						m_accuracy[i] = 1;
					}
					m_accuracy_f[i] = accuracy[i];
				}
			}
		}
	}
	if(m_accsel[bunchtype_] == CustomParticle){
		if(inobj.count(PartConfLabel) > 0){
			vector<double> partform = DefPartFormatPrm;
			f_LoadSingle(inobj, PartConfLabel, &PartFormat, &PartFormatSimple,
				&dumstr, &partform, &dumvec, &dumb, &m_parformsel, &dumstrs, &datalabels, &invalids);
			for(int i = 0; i < NumPartFormatPrm; i++){
				if(partform[i] > 0){
					m_parform[i] = (int)floor(0.5+partform[i]);
				}
				else{
					m_parform[i] = 1;
				}
				m_parform_f[i] = partform[i];
			}
		}
	}

	if(invalids.size() > 0){
		string msg = "\""+invalids[0]+"\"";
		for(int j = 0; j < invalids.size(); j++){
			msg += ", \""+invalids[j]+"\"";
		}
#ifdef _EMSCRIPTEN
		stringstream ss;
		ss << WarningLabel << "Invalid parameters found. " << msg;
		set_output("", ss.str().c_str());
#else
		cout << WarningLabel << "Invalid parameters found. " << msg << endl;
#endif
	}

	if(contains(m_calctype, menu::CMDcheck)){
		m_iscmdcheck = true;
		picojson::object &cobj = inobj[ConfigLabel].get<picojson::object>();
		m_calctype = cobj[OrgTypeLabel].get<string>();
	}

	m_materials = FilterMaterials;	// built-in materials
	if(inobj.count(FMaterialLabel) > 0){
		picojson::object fobj = inobj[FMaterialLabel].get<picojson::object>();
		f_CreateFilterMaterials(fobj);
	}

	m_isJSON = true;
	m_isASCII = false;
	if(inobj.count(OutFileLabel) > 0){
		picojson::object fobj = inobj[OutFileLabel].get<picojson::object>();
		if(fobj.count(OutFormat) > 0){
			string fmt = fobj[OutFormat].get<string>();
			if(fmt == JSONOnly){
				// default
			}
			else if(fmt == ASCIIOnly){
				m_isJSON = false;
				m_isASCII = true;
			}
			else{
				m_isASCII = true;
			}
		}
	}

	if(inobj.count("runid") > 0){
		m_ispreproc = true;
		m_pptype = inobj["runid"].get<string>();
	}

	m_isscan = CheckScanProcess(inobj);

	DataContainer *dcont;

	for(int i = 0; i < datalabels.size(); i++){
		string categ = datalabels[i][1];
		string prmlabel = datalabels[i][0];

		picojson::object pobj = inobj[categ].get<picojson::object>();
		if(datalabels[i].size() == 3){
			picojson::object oobj = pobj[datalabels[i][2]].get<picojson::object>();
			pobj = oobj;
		}

		bool iset = false;
		if(prmlabel == "Current Profile"){
			dcont = &m_currprof;
			iset = true;
		}
		else if(prmlabel == "E-t Profile"){
			dcont = &m_Etprof;
			iset = true;
		}
		else if(prmlabel == "Depth-Position Data"){
			dcont = &m_depth;
		}
		else if(prmlabel == "Field Profile"){
			dcont = &m_fvsz;
		}
		else if(prmlabel == "Field Profile (1 Period)"){
			dcont = &m_fvsz1per;
		}
		else if(prmlabel == "Gap vs. Field"){
			dcont = &m_gaptbl;
		}
		else if(prmlabel == "Custom Filter"){
			dcont = &m_customfilter;
		}
		else if(prmlabel == "Harmonic Component"){
			picojson::array hdata = pobj[prmlabel].get<picojson::array>();
			f_SetMultiHarmonic(hdata);
			continue;
		}
		else if(prmlabel == "Filters" 
			|| prmlabel == "Absorbers"){
			picojson::array fdata = pobj[prmlabel].get<picojson::array>();
			f_SetFilter(fdata, prmlabel == "Filters");
			continue;
		}
		else if(prmlabel == "Seed Spectrum"){
			dcont = &m_seedspec;
		}
		else{
			continue;
		}
		tuple<int, vector<string>> format = DataFormat.at(prmlabel);
		int dimension = get<0>(format);
		if(dimension == 0){
			dimension = 1;
			// dimension:0 -> dimension:1 without items
		}
		vector<string> titles = get<1>(format);

		picojson::object dataobj = pobj[prmlabel].get<picojson::object>();
		dcont->Set(dataobj, dimension, titles);

		if(prmlabel == "Field Profile"){
			if(dataobj.count(FELSecIdxLabel) > 0){
				picojson::array idxarr = dataobj[FELSecIdxLabel].get<picojson::array>();
				m_sections.clear();
				int sx, sxo = 0;
				for(int s = 0; s < idxarr.size(); s++){
					sx = (int)floor(idxarr[s].get<double>()+0.5);
					if(s == 0 || sx != sxo){
						m_sections.push_back(s);
						sxo = sx;
					}
				}
			}
		}

		if(iset){// fs -> s
			dcont->ConvertUnit(0, 1.0e-15, true);
		}
	}
	return;
}

string SpectraConfig::GetPrePropOrdinate()
{
	string ordinate;
	if(m_pptype == PPBetaLabel){
		ordinate = "betatron Function (m)";
	}
	else if(m_pptype == PPFDlabel){
		ordinate = "Magnetic Field (T)";
	}
	else if(m_pptype == PP1stIntLabel){
		ordinate = "Electron Angle (rad)";
	}
	else if(m_pptype == PP2ndIntLabel){
		ordinate = "Electron Position (m)";
	}
    else if(m_pptype == PPTransLabel){
		ordinate = "Transmission Rate";
    }
    else if(m_pptype == PPAbsLabel){
		ordinate = "Absorption Rate";
    }
	else if(m_pptype == PPPhaseErrLabel){
		ordinate = "Phase Error (degree)";
	}
	else{
		ordinate = "Normalized Intensity";
	}
	return ordinate;
}

bool SpectraConfig::CheckScanProcess(picojson::object &obj)
{
	string type;
	vector<double> values;
	vector<vector<double>> dvectors;
	vector<bool> bools;
	vector<string> selects, strs;
	vector<vector<string>> dconts;
	int iscan;
	vector<vector<double>> scanprms;
	string prmname;

	m_bundle = false;

	picojson::object scanobj;
	if(obj.count(ScanLabel) > 0){
		scanobj = obj[ScanLabel].get<picojson::object>();

		if(contains(m_calctype, menu::fixed)){
			m_bundle = true;
		}
		else if(scanobj.count(BundleScanlabel) > 0){
			m_bundle = scanobj[BundleScanlabel].get<bool>();
		}
	}
	else{
		return false;
	}

	vector<string> invalids;
	if(scanobj.count(AccLabel) > 0){
		f_LoadSingle(scanobj, AccLabel, &Acc, &AccSimple,
			&type, &values, &dvectors, &bools, &selects, 
			&strs, &dconts, &invalids, nullptr, &prmname, &iscan, &scanprms);
		m_scancateg = AccLabel;
	}
	else if(scanobj.count(SrcLabel) > 0){
		f_LoadSingle(scanobj, SrcLabel, &Src, &SrcSimple,
			&type, &values, &dvectors, &bools, &selects, 
			&strs, &dconts, &invalids, nullptr, &prmname, &iscan, &scanprms);
		m_scancateg = SrcLabel;
	}
	else if(scanobj.count(ConfigLabel) > 0){
		f_LoadSingle(scanobj, ConfigLabel, &Conf, &ConfSimple,
			&type, &values, &dvectors, &bools, &selects, 
			&strs, &dconts, &invalids, nullptr, &prmname, &iscan, &scanprms);
		m_scancateg = ConfigLabel;
	}
	else{
		return false;
	}
	m_scanitem = abs(iscan);
	m_scan2d = scanprms.size() > 1;

	if(m_scan2d){
		m_2dlink = scanprms[1][2] < 0;
	}

	size_t nf = prmname.find("(");
	string unit, value;
	if(nf == string::npos){
		unit = "";
		value = prmname;
	}
	else{
		unit = prmname.substr(nf+1);
		int nr = (int)unit.find(")");
		if(nr >= 0){
			unit = unit.substr(0, nr);
		}
		value = prmname.substr(0, nf);
	}

	if(m_scan2d == false){
		m_scanprms[0] = value;
		m_scanunits[0] = unit;
	}
	else{
		for(int j = 0; j < 2; j++){
			m_scanunits[j] = unit;
		}

		nf = value.find(",");
		string suf[2] = {"_1", "_2"};
		if(nf == string::npos){
			for(int j = 0; j < 2; j++){
				m_scanprms[j] = prmname+suf[j];
			}
		}
		else{
			string parts[2], item[2], xy[2], del[2] = {">", "<"};
			parts[0] = value.substr(0, nf);
			parts[1] = value.substr(nf+1);
			size_t na, nb;
			for(int j = 0; j < 2; j++){
				if(j == 0){
					na = parts[j].find_last_of(" ");
					nb = parts[j].find_last_of(del[j]);
					if (na == string::npos){
						na = 0;
					}
					if (nb == string::npos){
						nb = 0;
					}
					nf = max(0, (int)max(na, nb));
				}
				else{
					na = parts[j].find(" ");
					nb = parts[j].find(del[j]);
					nf = min(na, nb);
				}
				if(nf == 0){// delimeter not found
					xy[j] = parts[0];
					item[j] = "";
				}
				else{
					if(j == 0){
						item[j] = parts[0].substr(0, nf+1);
						xy[j] = parts[0].substr(nf+1);
					}
					else{
						xy[j] = parts[1].substr(0, nf);
						item[j] = parts[1].substr(nf);
					}
					trim(item[j]);
					trim(xy[j]);
				}
			}
			if(item[0].find(">") == string::npos){
				item[0] += " ";
			}
			for(int j = 0; j < 2; j++){
				m_scanprms[j] = item[0]+xy[j]+item[1];
			}
		}
		if(m_2dlink){
			scanprms[1][2] = scanprms[0][2];
			scanprms[1][3] = scanprms[0][3];
		}
	}

	for(int j = 0; j < (m_scan2d?2:1); j++){
		if(scanprms[j][2] == 0){
			continue;
		}
		double vini = min(scanprms[j][0], scanprms[j][1]);
		double vfin = max(scanprms[j][0], scanprms[j][1]);
		if(iscan < 0){ // integer parameter
			m_scanvalues[j].push_back(vini);
			double v = vini;
			do{
				v += fabs(scanprms[j][2]);
				m_scanvalues[j].push_back(v);
			} while(m_scanvalues[j].back() < vfin);
		}
		else{
			int nc = max(1, (int)floor(0.5+fabs(scanprms[j][2])));
			double dval = (vfin-vini)/max(1, nc-1);
			m_scanvalues[j].resize(nc);
			for(int n = 0; n < nc; n++){
				m_scanvalues[j][n] = vini+dval*n;
				if(fabs(m_scanvalues[j][n]) < dval*1.0e-10){
					m_scanvalues[j][n] = 0.0;
				}
			}
		}
		m_scaniniser[j] = (int)floor(0.5+scanprms[j][3]);
	}

	return true;
}

bool SpectraConfig::Initialize()
{
	m_gamma = m_acc[eGeV_]*1000.0/MC2MeV;

	m_emitt[0] = m_acc[emitt_]/(1.0+m_acc[coupl_]);
	m_emitt[1] = m_emitt[0]*m_acc[coupl_];

	double Z = m_conf[slit_dist_];
	m_conv2gt = m_gamma/max(INFINITESIMAL, Z);

	double dsize = 0, ddiv = 0;
	for(int j = 0; j < 2; j++){
		if(!m_accb[zerosprd_]){
			dsize = m_acc[espread_]*m_accv[eta_][j];
			ddiv = m_acc[espread_]*m_accv[etap_][j];
		}
		double alpha0 = m_accv[alpha_][j];
		double beta0 = m_accv[beta_][j];
		if(beta0 == 0){
			throw runtime_error("betatron function shoud be > 0");
			return false;
		}
		double gamma0 = (1.0+alpha0*alpha0)/beta0; // Twiss parameter gamma
		m_size[j] = sqrt(beta0*m_emitt[j]+dsize*dsize);
		m_div[j] = sqrt(gamma0*m_emitt[j]+ddiv*ddiv);

		double betaz = beta0-2.0*alpha0*Z+gamma0*Z*Z;
		double etazsq = hypotsq(dsize, ddiv*Z);
		m_Esize[j] = max(sqrt(betaz*m_emitt[j]+etazsq), m_acc[minsize_]);
		m_Ealpha[j] = m_emitt[j]*(alpha0-gamma0*Z);
		double SigmaSq = m_Esize[j]*m_Esize[j]*m_div[j]*m_div[j]
			-m_Ealpha[j]*m_Ealpha[j];
		m_Ediv[j] = sqrt(SigmaSq)/m_Esize[j];
	}

	m_isund = 
		m_srctype != WIGGLER &&
		m_srctype != EMPW &&
		m_srctype != WLEN_SHIFTER &&
		m_srctype != BM &&
		m_srctype != FIELDMAP3D &&
		m_srctype != CUSTOM;

	m_isf8 = m_srctype == FIGURE8_UND || m_srctype == VFIGURE8_UND;

	m_iswiggler = 
		m_srctype == WIGGLER ||
		m_srctype == EMPW;

    m_ismap3d = m_srctype == FIELDMAP3D;
    m_isbm = m_srctype == BM;
    m_iswshifter = m_srctype == WLEN_SHIFTER;

	m_issegu = m_issrc2 = m_isoddpole = false;
	if(m_isund || m_iswiggler){
		if(m_srctype == CUSTOM_PERIODIC){
			m_idfield.AllocateIntegral(&m_fvsz1per, true);
			m_idfield.GetUndulatorParametersPeriodic(m_srcv[Kxy_], &m_lu);
		}
		else{
			m_lu = m_src[lu_];
			m_lu /= 1000.0; // mm -> m
		}
		m_magharm = 1.0;
		if(m_isf8){
			m_magharm = 0.5;
		}
		m_lu /= m_magharm;
		if(m_lu <= 0){
			throw runtime_error("undulator period shoud be > 0");
			return false;
		}

		//!! definition of N should be consistent with GUI
		if(m_iswiggler){
			int poles = (int)floor(m_src[devlength_]/(m_lu/2.0)+1.0e-6);
			if(poles%2 > 0){
				m_isoddpole = true;
				poles++;
			}
			m_N = poles/2;
		}
		else{
			m_N = (int)floor(m_src[devlength_]/m_lu+1.0e-6);
		}
		if(m_srcb[endmag_]){
			m_N -= 2;
		}
		else{
			m_N -= 1;
		}
		if(m_N <= 0){
			throw runtime_error("device length too short");
			return false;
		}
		m_M = 1;
		if(m_isund){
			if(m_srcsel[segment_type_] == NoneLabel){
			}
			else if(m_srcsel[segment_type_] == IdenticalLabel){
				m_M = (int)floor(m_src[segments_]+0.5);
				m_issegu = true;
			}
			else{
				m_M = (int)floor(m_src[hsegments_]+0.5);
				m_issegu = true;
				m_issrc2 = true;
			}
			SetSymmetry();
		}
		SetKvalues();
		SetIDSections();
	}
	else{
		m_GT[0] = m_GT[1] = 1.0;
		m_N = m_M = 1;
	}

	if(m_srctype == FIELDMAP3D){
		m_is3dsrc = true;
	}
	else{
		m_is3dsrc = (m_issegu&&m_srcb[perlattice_]) 
			|| m_srcsel[natfocus_] != NoneLabel;
	}

	m_fluxitems = m_issrc2?12:4;

	SetMaximumB();

	if(contains(m_calctype, menu::vpdens)){
		if(m_conf[Qgl_] <= 0){
			throw runtime_error("angle of incidence should be > 0");
			return false;
		}
	}

	for(int j = 0; j < NumAccuracyPrm; j++){
		m_nlimit[j] = m_accuracy[j]+GAUSSIAN_MAX_REGION-1;
		m_nfrac[j] = 1 << ((int)floor(0.5+m_accuracy[j])-1);
	}

	return true;
}

void SpectraConfig::SetMaximumB()
{
	if(m_isund || m_iswiggler){
		double B;
		m_Bmax = 0.0;
		for(int j = 0; j < 2; j++){
			for(int h = 1; h < m_Kxy[j].size(); h++){
				B = fabs((double)h*m_Kxy[j][h]/(m_lu*COEF_K_VALUE));
				m_Bmax = max(m_Bmax, B);
			}
		}
	}
	else if(m_iswshifter){
		m_Bmax = m_src[bmain_];
	}
	else{
		m_Bmax = m_src[b_];
	}
}

void SpectraConfig::SetSymmetry()
{
	m_Nsymmetry = 1;
	m_symmetry[0] = m_symmetry[1] = false;
	if(!m_issrc2){
		if(m_srctype == FIGURE8_UND){
			m_Nsymmetry = 2;
			m_symmetry[1] = true;
		}
		else if(m_srctype == VFIGURE8_UND){
			m_Nsymmetry = 2;
			m_symmetry[0] = true;
		}
		else if(m_srctype != CUSTOM_PERIODIC 
			&& m_srctype != MULTI_HARM_UND){
			m_Nsymmetry = 4;
			m_symmetry[0] = m_symmetry[1] = true;
		}
	}
}

void SpectraConfig::SetIDSections()
{
	m_zorg.resize(m_M+1);
	m_zorgS.resize(m_M+1);
	double lint = m_src[interval_];
	if(m_issrc2){
		lint *= 2.0;
	}
	for(int m = 1; m <= m_M; m++){
		m_zorg[m] = m_zorgS[m] = (-m_M+2*m-1)*lint*0.5;
		if(m_issrc2){
			m_zorg[m] -= m_src[interval_]*0.5;
			m_zorgS[m] += m_src[interval_]*0.5;
		}
	}

	if(m_srcb[perlattice_] && m_issegu){
		int Mtot = (m_issrc2?2:1)*m_M;
		m_LatticeZ.resize(Mtot+1);
		for(int j = 0; j < 2; j++){
			m_betac[j].resize(Mtot+1, 0.0);
			m_alphac[j].resize(Mtot+1, 0.0);
		}
		for(int m = 0; m <= Mtot; m++){
			m_LatticeZ[m] = (-(double)Mtot*0.5+(double)m)*m_src[interval_];
		}
	}

}

void SpectraConfig::SetKvalues(double *kxyext)
{
	double Kxy[2];

	if(m_srctype == LIN_UND || m_srctype == WIGGLER){
		Kxy[0] = 0;
		Kxy[1] = m_src[K_];
	}
	else if(m_srctype == VERTICAL_UND){
		Kxy[1] = 0;
		Kxy[0] = m_src[K_];
	}
	else if(m_srctype == HELICAL_UND){
		Kxy[0] = Kxy[1] = m_src[K_];
	}
	else if(m_srctype == ELLIPTIC_UND && m_srcb[apple_]){
		double phase = PI2*m_src[phase_]/m_src[lu_];
		Kxy[0] = m_srcv[Kxy0_][0]*sin(phase);
		Kxy[1] = m_srcv[Kxy0_][1]*cos(phase);
	}
	else{
		Kxy[0] = m_srcv[Kxy_][0];
		Kxy[1] = m_srcv[Kxy_][1];
	}

	if(kxyext != nullptr){
		for (int j = 0; j < 2; j++){
			Kxy[j] = kxyext[j];
		}
	}

	m_extraN = 0;
	for(int j = 0; j < 2; j++){		
		m_Kxy[j].resize(3, 0.0); 
			// m_Kxy[x,y][harmonic starting with 1]
		m_deltaxy[j].resize(3, 0.0);
	}
	if(m_srctype == HELICAL_UND || m_srctype == ELLIPTIC_UND || m_srctype == EMPW){
		m_deltaxy[1][1] = PId2;
		m_extraN = 1;
	}
	if(m_srctype == FIGURE8_UND){
		m_Kxy[0][1] = Kxy[0];
		m_Kxy[1][2] = Kxy[1];
		m_extraN = 1;
	}
	else if(m_srctype == VFIGURE8_UND){
		m_Kxy[1][1] = -Kxy[1];
		m_Kxy[0][2] = Kxy[0];
		m_extraN = 1;
	}
	else if(m_srctype == MULTI_HARM_UND){
		m_extraN = 1;
		if(m_harmcont.size() == 0){
			m_harmcont.push_back(vector<double> {1, 90, 1, 0});
			// default: elliptic undulator
		}
		int nhmax = (int)m_harmcont.size();
		for (int j = 0; j < 2; j++){
			m_Kxy[j].resize(nhmax+1, 0.0);
			// m_Kxy[x,y][harmonic starting with 1]
			m_deltaxy[j].resize(nhmax+1, 0.0);
		}
		double kxysum[2] = {0, 0};
		for(int h = 1; h <= nhmax; h++){
			for(int j = 0; j < 2; j++){
				kxysum[j] += m_harmcont[h-1][2*j]*m_harmcont[h-1][2*j];
			}
		}
		for(int j = 0; j < 2; j++){
			kxysum[j] = sqrt(kxysum[j]);
		}
		for(int h = 1; h <= nhmax; h++){
			for(int j = 0; j < 2; j++){
				if(Kxy[j] > 0 && kxysum[j] == 0){
					throw runtime_error("At least one harmonic component should have non-zero ratio.");
				}
				if(Kxy[j] == 0){
					m_Kxy[j][h] = 0;
				}
				else{
					m_Kxy[j][h] = Kxy[j]*m_harmcont[h-1][2*j]/kxysum[j];
				}
				m_deltaxy[j][h] = DEGREE2RADIAN*m_harmcont[h-1][2*j+1];
			}
		}
	}
	else{
		m_Kxy[0][1] = Kxy[0];
		m_Kxy[1][1] = Kxy[1];
	}

	if(m_srcsel[segment_type_] == NoneLabel || 
			m_srcsel[segment_type_] == IdenticalLabel){
		// do nothing
	}
	else if(m_srcsel[segment_type_] == SwapBxyLabel){
		for(int j = 0; j < 2; j++){
			m_KxyS[j] = m_Kxy[1-j];
			m_deltaxyS[j] = m_deltaxy[1-j];
		}
	}
	else{
		for(int j = 0; j < 2; j++){
			m_KxyS[j] = m_Kxy[j];
			m_deltaxyS[j] = m_deltaxy[j];
		}
		int jxy = m_srcsel[segment_type_] == FlipBxLabel ? 0 : 1;
		for(int h = 1; h < m_KxyS[jxy].size(); h++){
			m_KxyS[jxy][h] = -m_KxyS[jxy][h];
		}
	}

	m_K2 = 0.0;
	for(int j = 0; j < 2; j++){
		m_GT[j] = 0.0;
		for(int h = 1; h < m_Kxy[j].size(); h++){
			m_GT[j] += m_Kxy[j][h]*m_Kxy[j][h];
		}
		m_K2 += m_GT[j]/2.0;
		m_GT[j] = sqrt(1.0+m_GT[j]/2.0);
	}
	swap(m_GT[0], m_GT[1]); // Ky -> x divergence
}

void SpectraConfig::GetIdealOrbit(double z, OrbitComponents *orbit, bool issec)
{
    double ku, ak, k2, al;

    if(m_srctype == CUSTOM_PERIODIC){
		if(!m_idfield.IsAllocated()){
			m_idfield.AllocateIntegral(&m_fvsz1per, true);
		}
		double rz[2];
		m_idfield.GetFieldIntegral(z, orbit->_acc, orbit->_beta, orbit->_xy, nullptr, rz);
		orbit->_rz = rz[0]+rz[1];
		orbit->_acc[0] *= -COEF_ACC_FAR_BT;
		orbit->_acc[1] *= COEF_ACC_FAR_BT;
    }
    else{
		orbit->Clear();
        ku = PI2/m_lu;

		vector<double> *kxy = m_Kxy, *delta = m_deltaxy;
		if(issec){
			kxy = m_KxyS;
			delta = m_deltaxyS;
		}

		for(int j = 0; j < 2; j++){
			double sign = j == 0 ? 1.0 : -1.0;
			for (int k = 1; k < kxy[1-j].size(); k++){
				if (fabs(kxy[1-j][k]) < INFINITESIMAL) {
					continue;
				}
				ak = ku*z*(double)k+delta[1-j][k];
				orbit->_beta[j] += sign*kxy[1-j][k]*cos(ak);
				orbit->_xy[j] += sign*kxy[1-j][k]*sin(ak)/ku/(double)k;
				k2 = kxy[1-j][k]*kxy[1-j][k];
				orbit->_rz += k2/2.0*z+k2/4.0/(double)k/ku*sin(2.0*ak);
				orbit->_acc[j] += kxy[1-j][k]*(double)k*sin(ak);
				for (int l = k+1; l < kxy[1-j].size(); l++) {
					al = ku*z*(double)l+delta[1-j][l];
					if(fabs(kxy[1-j][l]) < INFINITESIMAL) {
						continue;
					}
					orbit->_rz += kxy[1-j][k]*kxy[1-j][l]/ku*
						(sin(ak-al)/(double)(k-l)+sin(ak+al)/(double)(k+l));
				}
			}
		}

        orbit->_acc[0] *= -COEF_ACC_FAR_BT/(COEF_K_VALUE*m_lu);
        orbit->_acc[1] *= COEF_ACC_FAR_BT/(COEF_K_VALUE*m_lu);
    }
}

double SpectraConfig::GetPrm(string categ, int index)
{
	if(categ == AccLabel){
		return m_acc[index];
	}
	else if(categ == AccLabel){
		return m_src[index];
	}
	else if(categ ==SrcLabel){
		return m_conf[index];
	}
	f_ThrowException(index, categ);
	return 0;
}

double SpectraConfig::GetVector(string categ, int index, int jxy)
{
	if(categ == AccLabel){
		return m_accv[index][jxy];
	}
	else if(categ == SrcLabel){
		return m_srcv[index][jxy];
	}
	else if(categ == ConfigLabel){
		return m_confv[index][jxy];
	}
	f_ThrowException(index, categ);
	return 0;
}

bool SpectraConfig::GetBoolean(string categ, int index)
{
	if(categ == AccLabel){
		return m_accb[index];
	}
	else if(categ == AccLabel){
		return m_srcb[index];
	}
	else if(categ ==SrcLabel){
		return m_confb[index];
	}
	f_ThrowException(index, categ);
	return false;
}

bool SpectraConfig::IsFixedPoint()
{
	return contains(m_calctype, menu::fixed);
}

int SpectraConfig::GetScanCounts(
	vector<vector<double>> &scanvalues, string scanprms[], string scanunits[], int scaniniser[])
{
	int nscans;
	scaniniser[1] = -1;
	if(!m_isscan){
		nscans = 1;
	}
	else if(m_scan2d){
		if(m_scanvalues[0].size() == 0){
			nscans = (int)m_scanvalues[1].size();
			scanvalues.resize(1);
			scanvalues[0] = m_scanvalues[1];
			scanprms[0] = m_scanprms[1];
			scanunits[0] = m_scanunits[1];
			scaniniser[0] = m_scaniniser[1];
		}
		else if(m_scanvalues[1].size() == 0){
			nscans = (int)m_scanvalues[0].size();
			scanvalues.resize(1);
			scanvalues[0] = m_scanvalues[0];
			scanprms[0] = m_scanprms[0];
			scanunits[0] = m_scanunits[0];
			scaniniser[0] = m_scaniniser[0];
		}
		else{
			if(m_2dlink){
				nscans = (int)m_scanvalues[0].size();
			}
			else{
				nscans =
					(int)(m_scanvalues[0].size()*m_scanvalues[1].size());
			}
			scanvalues.resize(2);
			for(int j = 0; j < 2; j++){
				scanvalues[j] = m_scanvalues[j];
				scanprms[j] = m_scanprms[j];
				scanunits[j] = m_scanunits[j];
				scaniniser[j] = m_scaniniser[j];
			}
		}
	}
	else{
		scanvalues.resize(1);
		scanvalues[0] = m_scanvalues[0];
		scanprms[0] = m_scanprms[0];
		scanunits[0] = m_scanunits[0];
		scaniniser[0] = m_scaniniser[0];
		scaniniser[0] = m_scaniniser[0];
		nscans = (int)m_scanvalues[0].size();
	}
	return nscans;
}

void SpectraConfig::SetScanCondition(int index, int jxy[])
{
	if(!m_isscan){
		return;
	}
	if(m_scan2d){
		if(m_2dlink){
			jxy[0] =  jxy[1] = index;
		}
		else{
			int ncol = (int)m_scanvalues[0].size();
			if(ncol == 0){
				jxy[0] = 0;
				jxy[1] = index;
			}
			else{
				jxy[0] = index%ncol;
				jxy[1] = index/ncol;
				// [0] -> varies first
			}
		}

		for(int j = 0; j < 2; j++){
			if(m_scanvalues[j].size() == 0){
				continue;
			}
			if (m_scancateg == AccLabel){
				m_accv[m_scanitem][j] = m_scanvalues[j][jxy[j]];
			}
			else if (m_scancateg == SrcLabel){
				m_srcv[m_scanitem][j] = m_scanvalues[j][jxy[j]];
			}
			else{
				m_confv[m_scanitem][j] = m_scanvalues[j][jxy[j]];
			}
		}
	}
	else{
		if(m_scancateg == AccLabel){
			m_acc[m_scanitem] = m_scanvalues[0][index];
		}
		else if(m_scancateg == SrcLabel){
			if(m_scanitem == e1st_){
				// do nothing, set K vlues later (after initializaton)
			}
			else{
				m_src[m_scanitem] = m_scanvalues[0][index];
			}
		}
		else{
			m_conf[m_scanitem] = m_scanvalues[0][index];
		}
	}
}

void SpectraConfig::GetScanValues(int index, vector<double> &scanvalues)
{
	if(m_scan2d){
		scanvalues.resize(2);
		for(int j = 0; j < 2; j++){
			if (m_scancateg == AccLabel){
				scanvalues[j] = m_accv[m_scanitem][j];
			}
			else if (m_scancateg == SrcLabel){
				scanvalues[j] = m_srcv[m_scanitem][j];
			}
			else{
				scanvalues[j] = m_confv[m_scanitem][j];
			}
		}
	}
	else{
		scanvalues.resize(1);
		scanvalues[0] = m_scanvalues[0][index];
	}
}

void SpectraConfig::KillAutoRange()
{
	m_confb[autoe_] = false;
	m_confb[autot_] = false;
}

bool SpectraConfig::IsAutoRange()
{
	return m_confb[autoe_] || m_confb[autot_];
}

bool SpectraConfig::Is4D()
{
	return contains(m_calctype, menu::XXpYYp);
}

bool SpectraConfig::IsScanGapE1st(vector<double> &e1values, vector<double> &gvalues)
{
	if(m_scancateg != SrcLabel || (m_scanitem != e1st_ && m_scanitem != gap_)){
		return false;
	}
	if(m_scanitem == e1st_){
		e1values = m_scanvalues[0];
		gvalues.resize(0);
	}
	else{
		gvalues = m_scanvalues[0];
		e1values.resize(0);
	}
	return true;
}

void SpectraConfig::GetRangeParameter(
		vector<double> &conf, vector<vector<double>> &confv)
{
	conf = m_conf;
	confv = m_confv;
}

void SpectraConfig::AssignRangeParameter(
	vector<double> &conf, vector<vector<double>> &confv, bool force)
{
	if(force){
		m_conf = conf;
		m_confv = confv;
		return;
	}
	if(m_confb[autoe_]){
		m_confv[erange_][0] = min(m_confv[erange_][0], confv[erange_][0]);
		m_confv[erange_][1] = max(m_confv[erange_][1], confv[erange_][1]);
		m_conf[de_] = min(m_conf[de_], conf[de_]);
	}
	if(m_confb[autot_]){
		vector<int> rangeidx;
		if(contains(m_calctype, menu::srcpoint)){
			rangeidx = vector<int>{Xrange_, Xprange_, Yrange_, Yprange_};
		}
		else{
			rangeidx = vector<int>{xrange_, qxrange_, yrange_, qyrange_};
		}
		for(int j = 0; j < 4; j++){
			m_confv[rangeidx[j]][1] = max(m_confv[rangeidx[j]][1], confv[rangeidx[j]][1]);
			m_confv[rangeidx[j]][0] = min(m_confv[rangeidx[j]][0], confv[rangeidx[j]][0]);
		}
		m_confv[rrange_][1] = max(m_confv[rrange_][1], confv[rrange_][1]);
		m_confv[qrange_][1] = max(m_confv[qrange_][1], confv[qrange_][1]);
		m_conf[qphimesh_] = max(m_conf[qphimesh_], conf[qphimesh_]);
	}
}

bool SpectraConfig::CanBundle()
{
	if(m_isscan){
		if(!m_bundle){
			return false;
		}
		if(contains(m_calctype, menu::XXpYYp)){
			return false;
		}
		if(contains(m_calctype, menu::XXpprj) || contains(m_calctype, menu::YYpprj)){
			return m_confb[CMD_] == false;
		}
		else if(contains(m_calctype, menu::vpdens) && m_scan2d){
			return m_scanvalues[0].size() == 0 
				|| m_scanvalues[1].size() == 0;
		}
	}
	return true;
}

void SpectraConfig::ExpandResults(
	bool isexpand, vector<int> &nvars,
	vector<vector<double>> &var2D, vector<vector<vector<double>>> &item2D,
	vector<double> &var1D, vector<vector<double>> &item1D)
{
	int nitems, details = (int)nvars.size();
	if(isexpand){ // 2D -> 1D
		nitems = (int)item2D[0].size();
		int nvartotal = vectorsum(nvars, -1);
		var1D.resize(nvartotal);
		item1D.resize(nitems);
		for(int j = 0; j < nitems; j++){
			item1D[j].resize(nvartotal);
		}
	}
	else{
		nitems = (int)item1D.size();
		var2D.resize(details);
		item2D.resize(details);
		for(int d = 0; d < details; d++){
			var2D[d].resize(nvars[d]);
			item2D[d].resize(nitems);
			for (int j = 0; j < nitems; j++){
				item2D[d][j].resize(nvars[d]);
			}
		}
	}
	for(int d = 0; d < details; d++){
		for (int n = 0; n < nvars[d]; n++){
			int nd = 0;
			for(int jd = 0; jd < d; jd++){
				nd += nvars[jd];
			}
			nd += n;
			if(isexpand){
				var1D[nd] = var2D[d][n];
			}
			else{
				var2D[d][n] = var1D[nd];
			}
			for (int j = 0; j < nitems; j++){
				if (isexpand){
					item1D[j][nd] = item2D[d][j][n];
				}
				else{
					item2D[d][j][n] = item1D[j][nd];
				}
			}
		}
	}
}

bool SpectraConfig::IsJSONFld()
{
	return m_confsel[CMDfld_] == BothFormat || m_confsel[CMDfld_] == JSONOnly;
}

bool SpectraConfig::IsBinaryFld()
{
	return m_confsel[CMDfld_] == BothFormat || m_confsel[CMDfld_] == BinaryOnly;
}

void SpectraConfig::ConfigurePartialPower(double ratio)
{
	m_calctype = menu::fixed+"::"+menu::far+"::"+menu::ppower+"::"+menu::slitrect;
	m_confsel[aperture_] = FixedSlitLabel;
	m_confsel[defobs_] = ObsPointDist;
	for(int j = 0; j < 2; j++){
		m_confv[slitapt_][j] *= ratio;
	}
	Initialize();
}

void SpectraConfig::SetMPI(int rank, int mpiprocesses)
{
	m_rank = rank;
	m_mpiprocesses = mpiprocesses;
}

string SpectraConfig::GetDataPath()
{
	int serno = (int)floor(0.5+m_outf[serial_]);
	string dataname = m_outfs[prefix_];
	if(serno >= 0) {
		stringstream ss;
		ss << serno;
		dataname += "-" + ss.str();
	}
	PathHander datapath(m_outfs[folder_]);
	datapath.append(dataname);
	return datapath.string();
}

bool SpectraConfig::IsSkipOutput()
{
	if(contains(m_calctype, menu::CMD2d) 
		|| contains(m_calctype, menu::CMDPP)
		|| contains(m_calctype, menu::propagate))
	{
		return true;
	}
	return false;
}

// private functions
void SpectraConfig::f_LoadSingle(picojson::object &obj, string categ,
		const map<string, tuple<int, string>> *maplabeld,
		const map<string, tuple<int, string>> *maplabels,
		string *stype, vector<double> *prm, vector<vector<double>> *prmv, 
		vector<bool> *prmb, vector<string> *prmsel, vector<string> *prmstr,
		vector<vector<string>> *datalabels, 
		vector<string> *invalids, string *parent,
		string *prmname, int *scanidx, vector<vector<double>> *scanprms)
{
	picojson::object sglobj = obj[categ].get<picojson::object>();
	string type;
	int index;

	for(const auto& p : sglobj){
		if(p.first == TypeLabel){
			*stype = p.second.get<string>();
			continue;
		}
		if(count(ObsoleteLabels.begin(), ObsoleteLabels.end(), p.first)){
			f_LoadSingle(sglobj, p.first,
				maplabeld, maplabels, stype, prm, prmv, prmb, prmsel, prmstr,
				datalabels, invalids, &categ, prmname, scanidx, scanprms);
			continue;
		}
		if(p.first == OrgTypeLabel){
			m_orgtype = p.second.get<string>();
			continue;
		}
		if(p.first == AccuracyLabel){
			continue;
		}
		
		try {
			type = get<1>(maplabeld->at(p.first));
			index = get<0>(maplabeld->at(p.first));
		}
		catch (const out_of_range&) {
			try {
				type = get<1>(maplabels->at(p.first));
				index = get<0>(maplabels->at(p.first));
			}
			catch (const out_of_range&){
				if(invalids != nullptr){
					invalids->push_back(p.first);
				}
				continue;
			}
		}
		if(type == NumberLabel){			
			if(prmname != nullptr){
				picojson::array &vec = sglobj[p.first].get<picojson::array>();
				if (vec.size() < m_scanprmitems){
					string msg = "Invalid scan format for \""+p.first+"\"";
					throw runtime_error(msg.c_str());
				}
				*prmname = p.first;
				*scanidx = index;
				scanprms->resize(1);
				(*scanprms)[0].resize(m_scanprmitems);
				for(int j = 0; j < m_scanprmitems; j++){
					(*scanprms)[0][j] = vec[j].get<double>();
				}
				if(vec.size() == m_scanprmitems+1){
					if(vec[m_scanprmitems].get<string>() == IntegerLabel){
						*scanidx *= -1;
					}
				}
				continue;
			}
			(*prm)[index] = p.second.get<double>();
		}
		else if(type == ArrayLabel){
			picojson::array vec;
			try{
				vec = sglobj[p.first].get<picojson::array>();
			}
			catch (const exception&) {
				string msg = "parameter \""+p.first+"\""+" should be a vector";
				throw runtime_error(msg.c_str());
			}
			if(prmname != nullptr){
				if (vec.size() < m_scanprmitems){
					string msg = "invalid scan format for \""+p.first+"\"";
					throw runtime_error(msg.c_str());
				}
				*prmname = p.first;
				*scanidx = index;
				scanprms->resize(2);
				for(int j = 0; j < 2; j++){
					(*scanprms)[j].resize(m_scanprmitems);
				}
				for(int j = 0; j < m_scanprmitems; j++){
					picojson::array &values = vec[j].get<picojson::array>();
					(*scanprms)[0][j] = values[0].get<double>();
					(*scanprms)[1][j] = values[1].get<double>();
				}
				if(vec.size() == m_scanprmitems+1){
					if(vec[m_scanprmitems].get<string>() == IntegerLabel){
						*scanidx *= -1;
					}
				}
				continue;
			}
			if(vec.size() != 2){
				string msg = "invalid format for \""+p.first+"\"";
				throw runtime_error(msg.c_str());
			}
			(*prmv)[index][0] = vec[0].get<double>();
			(*prmv)[index][1] = vec[1].get<double>();
		}
		else if(type == BoolLabel){
			(*prmb)[index] = p.second.get<bool>();
		}
		else if(type == SelectionLabel){
			(*prmsel)[index] = p.second.get<string>();
		}
		else if(type == StringLabel){
			(*prmstr)[index] = p.second.get<string>();
		}		
		else if(type == DataLabel || type == GridLabel){
			if(parent != nullptr){
				datalabels->push_back(vector<string> {p.first, *parent, categ});
			}
			else{
				datalabels->push_back(vector<string> {p.first, categ});
			}
		}
	}
}

void SpectraConfig::f_CreateFilterMaterials(picojson::object &obj)
{
	for (const auto& p : obj) {
		picojson::object item = p.second.get<picojson::object>();
		double density = item["dens"].get<double>();
		picojson::array comps = item["comp"].get<picojson::array>();
		vector<double> dcomp;
		for(int n = 0; n < comps.size(); n++){
			picojson::array acomp = comps.at(n).get<picojson::array>();
			if(acomp.size() < 2){
				string msg = "invalid format for the filter list";
				throw runtime_error(msg.c_str());
			}
			dcomp.push_back(acomp.at(0).get<double>());
			dcomp.push_back(acomp.at(1).get<double>());
		}
		m_materials.insert(make_pair(p.first, make_tuple(density, dcomp)));
	}
}

void SpectraConfig::f_SetFilter(picojson::array &fdata, bool isfilter)
{
	for(int n = 0; n < fdata.size(); n++){
		picojson::array item = fdata[n].get<picojson::array>();
		string fname = item[0].get<string>();
		double thickness = atof(item[1].get<string>().c_str());
		if(isfilter){
			m_filters.push_back(make_tuple(fname, thickness));
		}
		else{
			m_absorbers.push_back(make_tuple(fname, thickness));
		}
	}
}

void SpectraConfig::f_SetMultiHarmonic(picojson::array &hdata)
{
	vector<double> mvalues(4, 0.0);
	for(int n = 0; n < hdata.size(); n++){
		picojson::array item = hdata[n].get<picojson::array>();
		if(item.size() < 4){
			continue;
		}
		for(int j = 0; j < 4; j++){
			string hs = item[j].get<string>();
			mvalues[j] = atof(hs.c_str());
		}
		m_harmcont.push_back(mvalues);
	}
}

void SpectraConfig::f_ThrowException(int index, string categ)
{
	stringstream msg;
	msg << "No parameters available for index " << index << " in category" << categ;
	throw out_of_range(msg.str());
}

//----------
void CMDContainer::Set(string caption, 
	int dim, vector<string> &titles, vector<string> &units,
	vector<vector<double>> &vararray, vector<vector<double>> &data)
{
	_caption = caption;
	_dimension = dim;
	_titles = titles;
	_units = units;
	_vararray = vararray;
	_data = data;
}

// wrapper class for filesystem::path (c++17)
PathHander::PathHander(std::string pathname)
{
	Create(pathname);
}

void PathHander::Create(std::string pathname)
{
#ifdef WIN32
	m_separator = "\\";
#else
	m_separator = "/";
#endif
	size_t idir = pathname.find_last_of(m_separator);

	m_directory = "";
	std::string name = "";
	if (idir != std::string::npos) {
		m_directory = pathname.substr(0, idir + 1);
		if (idir < pathname.size() - 1) {
			name = pathname.substr(idir + 1);
		}
	}
	else {
		name = pathname;
	}
	replace_filename(name);
}

std::string PathHander::string()
{
	return m_directory + m_name + m_extension;
}

void PathHander::replace_extension(std::string ext)
{
	m_extension = ext;
}

void PathHander::replace_filename(std::string name)
{
	m_name = m_extension = "";
	size_t edir = name.find_last_of(".");
	if (edir != std::string::npos) {
		m_name = name.substr(0, edir);
		m_extension = name.substr(edir);
	}
	else {
		m_name = name;
	}
}

void PathHander::append(std::string name)
{
	if (m_directory != "") {
		m_directory += m_name + m_extension + m_separator;
	}
	replace_filename(name);
}

PathHander PathHander::filename()
{
	PathHander path(m_name + m_extension);
	return path;
}

PathHander& PathHander::operator = (const std::string& pathname)
{
	Create(pathname);
	return *this;
}

void ExportOutput(string outfile,
	string &input, vector<string> &categs, vector<string> &results)
{
#ifdef _EMSCRIPTEN
	stringstream outputfile;
#else
	ofstream outputfile(outfile);
#endif

	AddIndent(JSONIndent, results[0]);
	outputfile << "{" << endl;

	if(input != ""){
		PrependIndent(JSONIndent, outputfile);
		outputfile << "\""+InputLabel+"\": " << input << "," << endl;
	}

	PrependIndent(JSONIndent, outputfile);
	outputfile << "\""+categs[0]+"\": " << results[0];

	for(int i = 1; i < categs.size(); i++){
		AddIndent(JSONIndent, results[i]);
		outputfile << "," << endl;
		PrependIndent(JSONIndent, outputfile);
		outputfile << "\""+categs[i]+"\": " << results[i];
	}

	outputfile << endl << "}" << endl;

#ifdef _EMSCRIPTEN
	set_output(outfile.c_str(), outputfile.str().c_str());
#else
	outputfile.close();
#endif
}

void ExportData(stringstream &ssresult, int indlevel,
	int dimension, int nitems, int nscans, int delmesh, bool isnewl,
	vector<vector<double>> &vararray, vector<vector<vector<double>>> &data)
{
	int nscon = isnewl ? indlevel+2 : indlevel+1;
	for(int i = 0; i < dimension; i++){
		WriteJSONData(ssresult, (indlevel+1)*JSONIndent, vararray[i], 0, true, true);
	}
	for(int i = 0; i < nitems; i++){
		PrependIndent((indlevel+1)*JSONIndent, ssresult);
		ssresult << "[";
		for(int ns = 0; ns < nscans; ns++){
			if(isnewl && ns == 0){
				ssresult << endl;
			}
			if(nscans > 1){
				PrependIndent(nscon*JSONIndent, ssresult);
			}
			WriteJSONData(ssresult, nscon*JSONIndent, data[ns][i], delmesh, ns < nscans-1, false);
		}
		if(isnewl){
			ssresult << endl;
			PrependIndent((indlevel+1)*JSONIndent, ssresult);
		}
		ssresult << (i == nitems-1 ? "]" : "],");
		if(i < nitems-1){
			ssresult << endl;
		}
	}
	ssresult << endl;
}

void ExportAscii(string filename,
	vector<string> &stitles, vector<string> &sunits, vector<int> &widths, vector<int> &precs,
	vector<vector<double>> &vararray, vector<vector<vector<double>>> &data)
{
	int nscans = (int)data.size();
	int nitems = (int)data[0].size();
	int ndata = (int)data[0][0].size();
	int nvars = (int)vararray.size();
	vector<int> mesh(nvars), nidx(nvars);

	for(int j = 0; j < nvars; j++){
		mesh[j] = (int)vararray[j].size();
	}

	ofstream ofs(filename);

	for(int j = 0; j < nitems+nvars; j++){
		ofs << setw(widths[j]);
		ofs << stitles[j];
	}
	ofs << endl;

	for(int j = 0; j < nitems+nvars; j++){
		ofs << setw(widths[j]);
		ofs << sunits[j];
	}
	ofs << endl;

	ofs << scientific;
	for(int ns = 0; ns < nscans; ns++){
		for(int n = 0; n < ndata; n++){
			int nt = n+ns*ndata;
			GetIndicesMDV(nt, mesh, nidx, nvars);
			for(int j = 0; j < nvars; j++){
				ofs << setw(widths[j]) << setprecision(precs[j]);
				ofs << vararray[j][nidx[j]];
			}
			for(int j = 0; j < nitems; j++){
				ofs << setw(widths[j+nvars]) << setprecision(precs[j+nvars]);
				ofs << data[ns][j][n];
			}
			ofs << endl;
		}
	}

	ofs.close();
}

void WriteSupplementalData(stringstream &ss,
	vector<vector<string>> &suppletitles,
	vector<vector<double>> &suppledata)
{
	int nsc = (int)suppletitles.size();
	if(nsc == 0){
		return;
	}
	int nitems = (int)suppletitles[0].size();
	if(nitems == 0){
		return;
	}

	for(int nq = 1; nq < nsc; nq++){
		if((int)suppletitles[nq].size() < nitems){
			nsc = nq;
			break;
		}
	}

	ss << "," << endl;
	PrependIndent(JSONIndent, ss);
	ss << "\"" << RelateDataLabel << "\": {";
	if(nsc == 1){
		for(int j = 0; j < nitems; j++){
			bool isnext = j < nitems-1;
			WriteJSONValue(ss, 0, suppledata[0][j], suppletitles[0][j].c_str(), false, isnext, true);
		}
	}
	else{
		ss << endl;
		vector<double> ws(nsc);
		for(int j = 0; j < nitems; j++){
			for(int n = 0; n < nsc; n++){
				ws[n] = suppledata[n][j];
			}
			WriteJSONArray(ss, 2*JSONIndent, ws, suppletitles[0][j].c_str(), false, j < nitems-1);
		}
		ss << endl;
		PrependIndent(JSONIndent, ss);
	}
	ss << "}";
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
	string &result)
{
	int delmesh = -1;
	if(dimension > 1){
		if(details.size() > 0){
			delmesh = (int)vararrayd[0][0].size();
		}
		else{
			delmesh = (int)vararray[0].size();
		}
	}

	stringstream ssresult;
	ssresult << boolalpha; // show "true" or "false" for boolean
	ssresult << "{" << endl;
	if(scanindex != nullptr){
		vector<double> scanvalues;
		spconf.GetScanValues(*scanindex, scanvalues);
		if(scanvalues.size() == 1){
			WriteJSONValue(ssresult, JSONIndent, scanvalues[0], "Set Value", false, true);
		}
		else{
			WriteJSONArray(ssresult, JSONIndent, scanvalues, "Set Value", false, true);
		}
	}

	WriteJSONValue(ssresult, JSONIndent, dimension, DataDimLabel.c_str(), false, true);
	if(spconf.IsPreprocess()){
		string ordinate = spconf.GetPrePropOrdinate();
		WriteJSONValue(ssresult, JSONIndent, ordinate, "ordinate", true, true);
	}
	if(dimension > vardimension){
		WriteJSONValue(ssresult, JSONIndent, vardimension, VariablesLabel.c_str(), false, true);
	}
	WriteJSONArray(ssresult, JSONIndent, titles, DataTitlesLabel.c_str(), true, true);
	WriteJSONArray(ssresult, JSONIndent, units, UnitsLabel.c_str(), true, true);
	if(details.size() > 0){
		WriteJSONArray(ssresult, JSONIndent, details, DetailsLabel.c_str(), true, true);
	}
	if(spconf.Is2DLink()){
		bool istrue = true;
		WriteJSONValue(ssresult, JSONIndent, istrue, Link2DLabel.c_str(), false, true);
	}

	int nitems = (int)data[0].size();
	if(dimension == 0){
		vector<double> sglvalues(nitems);
		for(int i = 0; i < nitems; i++){
			sglvalues[i] = data[0][i][0];
		}
		PrependIndent(JSONIndent, ssresult);
		ssresult << "\"" << DataLabel << "\": [" << endl;
		PrependIndent(2*JSONIndent, ssresult);
		WriteJSONData(ssresult, 0, sglvalues, 0, false, false);
		ssresult << endl;
		PrependIndent(JSONIndent, ssresult);
		ssresult << "]";
	}
	else{
		PrependIndent(JSONIndent, ssresult);
		ssresult << "\"" << DataLabel << "\": [" << endl;
		bool isnewl = dimension > vardimension;

		if(details.size() == 0){
			ExportData(ssresult, 1, dimension, nitems, nscans, delmesh, isnewl, vararray, data);
		}
		else{
			for(int d = 0; d < details.size(); d++){
				PrependIndent(2*JSONIndent, ssresult);
				ssresult << "[" << endl;
				ExportData(ssresult, 2, dimension, nitems, nscans, delmesh, isnewl, vararrayd[d], datad[d]);
				PrependIndent(2*JSONIndent, ssresult);
				if(d == details.size()-1){
					ssresult << "]" << endl;
				}
				else{
					ssresult << "]," << endl;
				}
			}
		}
		PrependIndent(JSONIndent, ssresult);
		ssresult << "]";
	}
	WriteSupplementalData(ssresult, suppletitles, suppledata);
	ssresult << endl << "}";
	result = ssresult.str();
}

