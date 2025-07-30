#ifndef spectra_config_h
#define spectra_config_h

#include "picojson.h"
#include "spectra_input.h"
#include "data_container.h"
#include "numerical_common_definitions.h"
#include "orbit_components_operation.h"
#include "id_field_profile.h"

using namespace std;

class PathHander
{
public:
	PathHander() {}
	PathHander(std::string pathname);
	void Create(std::string pathname);
	std::string string();
	void replace_extension(std::string ext);
	void replace_filename(std::string name);
	void append(std::string name);
	PathHander filename();
	PathHander& operator = (const std::string& pathname);

private:
	std::string m_directory;
	std::string m_name;
	std::string m_extension;
	std::string m_separator;
};

class SpectraConfig 
{
public:
	SpectraConfig(int serno = -1);
	void LoadJSON(string &input, picojson::object &inobj);
	bool CheckScanProcess(picojson::object &obj);
	bool Initialize();
	void SetMaximumB();
	void SetSymmetry();
	void SetIDSections();
	void SetKvalues(double *kxyext = nullptr);
	void GetIdealOrbit(double z, OrbitComponents* orbit, bool issec = false);
	double GetPrm(string categ, int index);
	double GetVector(string categ, int index, int jxy);
	bool GetBoolean(string categ, int index);
	int GetFluxItms(){return m_fluxitems;}
	int GetPerios(){return m_N;}
	bool IsFixedPoint();
	int GetAccuracy(int index){ return m_accuracy[index]; }

	int GetScanCounts(vector<vector<double>> &scanvalues, 
		string scanprms[], string scanunits[], int scaniniser[]);
	void SetScanCondition(int index, int jxy[]);
	void GetScanValues(int index, vector<double> &scanvalues);
	void KillAutoRange();
	bool IsScan(){return m_isscan;}
	bool IsAutoRange();
	bool Is4D();
	bool Is2DLink(){return m_2dlink;}
	bool IsScanGapE1st(vector<double> &e1values, vector<double> &gvalues);
	void GetRangeParameter(vector<double> &conf, vector<vector<double>> &confv);
	void AssignRangeParameter(vector<double> &conf, vector<vector<double>> &confv, bool force);
	bool CanBundle();
	bool IsPreprocess(){return m_ispreproc;}
	string GetPrePropOrdinate();
	void ExpandResults(bool isexpand, vector<int> &nvars,
		vector<vector<double>> &var2D, vector<vector<vector<double>>> &item2D,
		vector<double> &var1D, vector<vector<double>> &item1D);
	bool IsJSON(){return m_isJSON;}
	bool IsASCII(){return m_isASCII;}
	bool IsJSONFld();
	bool IsBinaryFld();
	void ConfigurePartialPower(double ratio);
	void SetMPI(int rank, int mpiprocesses);
	string GetDataPath();
	void SetDataName(const string dataname){m_dataname = dataname;}
	string GetDataName(){return m_dataname;}
	void SetCalcType(string calctype){m_calctype = calctype;}
	bool IsSkipOutput();
	string GetOrgType(){ return m_orgtype; }

private:
	void f_LoadSingle(picojson::object &obj, string categ,
			const map<string, tuple<int, string>> *maplabeld,
			const map<string, tuple<int, string>> *maplabels,
			string *stype, vector<double> *prm, vector<vector<double>> *prmv, 
			vector<bool> *prmb, vector<string> *prmsel, vector<string> *prmstr,
			vector<vector<string>> *datalabels, 
			vector<string> *invalids = nullptr, string *parent = nullptr,
			string *prmname = nullptr, int *scanidx = nullptr, 
			vector<vector<double>> *scanprms = nullptr);
	void f_CreateFilterMaterials(picojson::object &obj);
	void f_SetFilter(picojson::array &fdata, bool isfilter);
	void f_SetMultiHarmonic(picojson::array &hdata);
	void f_ThrowException(int index, string categ);

protected:
	// input parameters
	vector<double> m_acc;
	vector<double> m_src;
	vector<double> m_conf;

	vector<vector<double>> m_accv;
	vector<vector<double>> m_srcv;
	vector<vector<double>> m_confv;

	vector<bool> m_accb;
	vector<bool> m_srcb;
	vector<bool> m_confb;

	vector<string> m_accsel;
	vector<string> m_srcsel;
	vector<string> m_confsel;

	vector<string> m_accs;
	vector<string> m_srcs;
	vector<string> m_confs;

	vector<int> m_accuracy;
	vector<double> m_accuracy_f;
	vector<bool> m_accuracy_b;

	vector<int> m_parform;
	vector<double> m_parform_f;
	vector<string> m_parformsel;

	vector<double> m_outf;
	vector<string> m_outfs;
	vector<string> m_outfsel;

	vector<double> m_ppconf;
	vector<string> m_ppconfsel;

	string m_acctype;
	string m_srctype;
	string m_calctype;
	string m_orgtype;
	string m_pptype;

	DataContainer m_gaptbl;
	DataContainer m_fvsz;
	DataContainer m_fvsz1per;
	DataContainer m_customfilter;
	DataContainer m_currprof;
	DataContainer m_Etprof;
	DataContainer m_depth;
	DataContainer m_seedspec;

	picojson::object m_pjoutput;
	picojson::object m_cmd;
	picojson::object m_felbfactor;
	bool m_iscmdcheck;

	// scan configuration
	int m_scanprmitems;
	bool m_isscan;
	string m_scancateg;
	int m_scanitem;
	bool m_scan2d;
	bool m_bundle;
	bool m_2dlink;
	vector<double> m_scanvalues[2];
	int m_scaniniser[2];
	string m_scanprms[2];
	string m_scanunits[2];

	// preprocessing;
	bool m_ispreproc;

	// partial power for slit size
	bool m_ispp4apt;

	// ----- accelerator variables -----
	double m_gamma;
	double m_emitt[2]; // emittance with dispersion
	double m_size[2]; // beam size with dispersion
	double m_div[2]; // divergence with dispersion
	double m_Esize[2]; // effective size (at obs. point)
	double m_Ediv[2]; // effective div (emittance/ eff.size)
	double m_Ealpha[2]; // effective alpha for surface PD

	// ----- light source variables -----
	bool m_isund;
	bool m_iswiggler;
    bool m_isbm;
	bool m_isf8;
    bool m_iswshifter;
    bool m_ismapaxis;
    bool m_ismap3d;
	bool m_issegu; // segmented U scheme
	bool m_issrc2; // 2nd source exisits in seg. U
	bool m_is3dsrc; // 3-d field structure
	double m_lu; // period length in m
	int m_N; // number of regular periods
	int m_M; // number of segments (pairs)
	bool m_isoddpole; // odd magn. pole in wigglers 
	int m_extraN; // number of extra periods to describe full device
	double m_magharm; 
		// relative number of magn. fundamental 
		// w.r.t undulator fundamenttal

	int m_Nsymmetry; // number of symmetric quadrant
	bool m_symmetry[2]; // symmetric axis
	int m_fluxitems; // number of items to compute und. flux

	vector<double> m_zorg; // origins of seg. U
	vector<double> m_zorgS;	// origins (secandary)
	vector<double> m_betac[2]; // periodic beta at m_zorg
	vector<double> m_alphac[2]; // periodic alpha at m_zorg

	vector<double> m_Kxy[2]; // Kx,y (main)
	vector<double> m_KxyS[2]; // Kx,y (secondary)
	vector<double> m_deltaxy[2]; // Bx phase
	vector<double> m_deltaxyS[2]; // By phase
	double m_K2; // (Kx^2+K^y2)/2
	double m_GT[2]; // typ. div. of SR power
	double m_Bmax; // mag. field for critical energy

	vector<double> m_LatticeZ; // z range of seg. U

	vector<int> m_sections; // sections for FELamplifier class

	// multi-harmonic undulator
	vector<vector<double>> m_harmcont;

	// custom periodic field
	IDFieldProfile m_idfield;

	// export configuratins
	bool m_isJSON;
	bool m_isASCII;

	// filtering related
	map<string, tuple<double, vector<double>>> m_materials;
	vector<tuple<string, double>> m_filters;
	vector<tuple<string, double>> m_absorbers;

	// others
	double m_conv2gt; // gamma*theta <-> r

	// accuracy
	double m_nlimit[NumAccuracyPrm];
	double m_nfrac[NumAccuracyPrm];

	// MPI configurations
	int m_mpiprocesses;
	int m_rank;

	// output dataname
	string m_dataname;

	// serial number (for progressbar in emscripten)
	int m_serno;
};

class CMDContainer
{
public:
	void Set(string caption, int dim, vector<string> &titles, vector<string> &units, 
		vector<vector<double>> &vararray, vector<vector<double>> &data);
	string _caption;
	int _dimension;
	vector<string> _titles;
	vector<string> _units;
	vector<vector<double>> _vararray;
	vector<vector<double>> _data;
};

void ExportOutput(string outfile,
	string &input, vector<string> &categs, vector<string> &results);
void ExportData(stringstream &ssresult, int indlevel,
	int dimension, int nitems, int nscans, int delmesh, bool isnewl,
	vector<vector<double>> &vararray, vector<vector<vector<double>>> &data);
void ExportAscii(string filename,
	vector<string> &stitles, vector<string> &sunits, vector<int> &widths, vector<int> &precs,
	vector<vector<double>> &vararray, vector<vector<vector<double>>> &data);
void WriteSupplementalData(stringstream &ss,
	vector<vector<string>> &suppletitles, vector<vector<double>> &suppledata);
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

#endif