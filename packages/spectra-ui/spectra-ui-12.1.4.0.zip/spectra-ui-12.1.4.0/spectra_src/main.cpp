#include <fstream>
#include <iomanip>
#include <set>
#include <thread>
#include "common.h"
#include "spectra_solver.h"
#include "formats.h"
#include "json_writer.h"
#include "output_utility.h"
#include "montecarlo.h"
#include "kvalue_operation.h"
#include "json_writer.h"

//#define _DEBUG

#ifdef _DEBUG
#include "particle_generator.h"
#include "trajectory.h"
#endif

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

#ifdef _EMSCRIPTEN
#ifndef _MAIN
#include <emscripten/bind.h>
#include <emscripten.h>
#endif
#endif

using namespace std;

#ifdef _EMSCRIPTEN
EM_JS(void, set_message, (const char *poutput), {
	let output = UTF8ToString(poutput);
	SetOutput("", output);
});
#endif

void SetMessage(const char *msg)
{
#ifdef _EMSCRIPTEN
	set_message(msg);
#else
	cout << msg << endl;
#endif
}

void Run(int rank, int nthreads, SpectraConfig &spconf, int *scanindex, 
		vector<string> &categs, vector<string> &results)

{
	int dimension, jxy[2];
	vector<string> titles, units, details;
	vector<vector<double>> vararray, scanvalues;
	vector<vector<vector<double>>> data;
	// data[scan][item][variable]

	vector<vector<string>> suppltitles;
	vector<vector<double>> suppldata;

	vector<vector<vector<double>>> vararrayd;
	vector<vector<vector<vector<double>>>> datad;
	vector<int> nvars;

	string scanprms[2], scanunits[2];

	int nscans, iniser[2];
	if(scanindex == nullptr){
		nscans = spconf.GetScanCounts(scanvalues, scanprms, scanunits, iniser);
	}
	else{
		nscans = 1;
	}
	data.resize(nscans);
	suppltitles.resize(nscans);
	suppldata.resize(nscans);

	vector<double> e1values, gvalues;
	vector<vector<double>> Kxy;
	bool isegscan = spconf.IsScanGapE1st(e1values, gvalues);
	if(isegscan){
		spconf.Initialize();
		bool isgapscan = gvalues.size() > 0;
		SpectraSolver spsolver(spconf);
		vector<double> Kperp(nscans), gap(nscans);
		if(isgapscan){
			gap = gvalues;
			if(scanindex != nullptr){
				gap[0] = gap[scanindex[0]];
			}		
		}
		else{
			if(scanindex == nullptr){
				for(int n = 0; n < e1values.size(); n++){
					Kperp[n] = spsolver.GetKperp(e1values[n]);
				}
			}
			else{
				Kperp[0] = spsolver.GetKperp(e1values[scanindex[0]]);
			}
		}
		KValueOperation kvalue(spsolver);
		kvalue.GetKxyValues(Kperp, gap, Kxy, !isgapscan);
	}

#ifdef _CPUTIME
	chrono::system_clock::time_point rtime[2];
	rtime[0] = chrono::system_clock::now();
#endif

	vector<vector<string>> rlabels(nscans);
	vector<vector<double>> rtimes(nscans);
	for(int n = 0; n < nscans; n++){
		details.clear(); nvars.clear();
		if (scanindex == nullptr){
			spconf.SetScanCondition(n, jxy);
		}
		if(!spconf.Initialize()){
			return;
		}
		if(isegscan){
			double kxyext[] = {Kxy[0][n], Kxy[1][n]};
			spconf.SetKvalues(kxyext);
			spconf.SetMaximumB();
		}

		auto runthread = [&](int thid, MPIbyThread *thread, vector<string> &rlabel, vector<double> &rtime){
			int idummy;
			vector<int> vidummy;
			vector<string> vsdummy[6];
			vector<vector<double>> vddummy[2];

			SpectraSolver spsolver(spconf, thid, thread);
			if(spsolver.IsMonteCarlo() && spconf.GetBoolean(AccLabel, zeroemitt_) == false){
				MonteCarlo montecarlo(spsolver);
				if(thid == 0){
					montecarlo.RunSingle(dimension, titles,
						units, vararray, data[n], details, nvars, results, categs);
				}
				else{
					montecarlo.RunSingle(idummy, vsdummy[0],
						vsdummy[1], vddummy[0], vddummy[1], vsdummy[2], vidummy, vsdummy[4], vsdummy[5]);
				}
			}
			else{
				if(thid == 0){
					spsolver.RunSingle(dimension, titles,
						units, vararray, data[n], details, nvars, results, categs);
					spsolver.GetMeasuredTime(rlabel, rtime, false);
				}
				else{
					spsolver.RunSingle(idummy, vsdummy[0],
						vsdummy[1], vddummy[0], vddummy[1], vsdummy[2], vidummy, vsdummy[4], vsdummy[5]);
				}
			}
			spsolver.DeleteInstances();
			if(thid == 0){
				spsolver.GetSuppleData(suppltitles[n], suppldata[n]);
			}
		};

		if(nthreads > 1){
			MPIbyThread mpithread(nthreads);
			vector<thread> solvers;
			for(int thid = 0; thid < nthreads-1; thid++){// std::ref() needed to avoid compile error
				solvers.emplace_back(runthread, thid+1, &mpithread, ref(rlabels[n]), ref(rtimes[n]));
			}
			runthread(0, &mpithread, rlabels[n], rtimes[n]);
			for(int thid = 0; thid < nthreads-1; thid++){
				solvers[thid].join();
			}
		}
		else{
			runthread(0, nullptr, rlabels[n], rtimes[n]);
		}

		if (data[n].size()+dimension != titles.size()){
			throw runtime_error("Numbers of items and titles do not match.");
			return;
		}
		if(rank == 0){
			stringstream ss;
			bool ismsg = false;
			if(scanindex != nullptr){
				if(scanindex[1] > 1){
					ismsg = true;
					ss << Fin1ScanLabel << scanindex[0]+1 << "/" << scanindex[1] << " Finished";
				}
			}
			else{
				if(nscans > 1){
					ismsg = true;
					ss << Fin1ScanLabel << n+1 << "/" << nscans << " Finished";
				}
			}
			if(ismsg){
				SetMessage(ss.str().c_str());
			}
		}

		if(details.size() > 0){
			if(n == 0){
				vararrayd.resize(details.size());
				datad.resize(details.size());
				for (int d = 0; d < details.size(); d++){
					vararrayd[d].resize(dimension);
					datad[d].resize(nscans);
				}
			}
			vector<vector<double>> var2D;
			vector<vector<vector<double>>> item2D;

			// vararray[0][detail * variable]: dimension = 1
			// data[scan][item][detail * variable]
			// var2D[detail][variable]
			// item2D[detail][item][variable]
			spconf.ExpandResults(false, nvars, var2D, item2D, vararray[0], data[n]);

			// vararrayd[detail][0][variable] : dimension = 1
			// datad[detail][scan][item][variable]
			for(int d = 0; d < details.size(); d++){
				if(n == 0){
					vararrayd[d][0] = var2D[d];
				}
				datad[d][n] = item2D[d];
			}
		}
	}

#ifdef _CPUTIME
	rtime[1] = chrono::system_clock::now();
	double elapsed = static_cast<double>(chrono::duration_cast<chrono::microseconds>(rtime[1]-rtime[0]).count())/1e6;
	if(rank == 0){
		cout << endl << ElapsedTimeLabel << elapsed << endl;
	}
	if(spconf.IsSkipOutput()){
		categs.push_back(ElapsedTimeLabel);
		results.push_back(to_string(elapsed));
	}
	else{
		suppltitles[0].push_back(ElapsedTimeLabel);
		suppldata[0].push_back(elapsed);
		for(int j = 0; j < rlabels[0].size(); j++){
			suppltitles[0].push_back(rlabels[0][j]);
			suppldata[0].push_back(rtimes[0][j]);
		}
	}
#endif

	if(spconf.IsSkipOutput()){
		return;
	}

	int vardimension = dimension;
	if(spconf.IsScan() && scanindex == nullptr){
		for(int j = 0; j < scanvalues.size(); j++){
			vararray.push_back(scanvalues[j]);
		}
		for(int j = 0; j < scanvalues.size(); j++){
			titles.insert(titles.begin()+j+dimension, scanprms[j]);
			units.insert(units.begin()+j+dimension, scanunits[j]);
		}
		dimension += (int)scanvalues.size();
		if(details.size() > 0){
			for(int d = 0; d < details.size(); d++){
				for (int j = 0; j < scanvalues.size(); j++){
					vararrayd[d].push_back(scanvalues[j]);
				}
			}
		}
	}
	if(!spconf.IsFixedPoint() && spconf.IsASCII() 
		&& !spconf.IsPreprocess() && rank == 0){
		vector<string> stitles, sunits;
		vector<int> widths, precs;

		GetIndicesFromTitles(titles, units, stitles, sunits, widths, precs);
		string dataname = spconf.GetDataName();
		if(details.size() == 0){
			dataname += ".txt";
			ExportAscii(dataname, stitles, sunits, widths, precs, vararray, data);
		}
		else{
			string ofile;
			for(int d = 0; d < details.size(); d++){
				stringstream ss;
				ss << d;
				ofile = dataname+"-"+ss.str()+".txt";
				ExportAscii(ofile, stitles, sunits, widths, precs, vararrayd[d], datad[d]);
			}
		}
	}

	WriteResults(spconf, scanindex, nscans, scanvalues, dimension, vardimension,
		titles, units, details, vararray, data, vararrayd, datad, suppltitles, suppldata, results[0]);
}

int RunProcess(
	picojson::object &inobj, string dataname, int rank, int mpiprocesses, int nthreads, int serno = -1)
{
	string input;
	SpectraConfig spconf(serno);
	spconf.SetMPI(rank, mpiprocesses);

	try{
		spconf.LoadJSON(input, inobj);
	}
	catch (const exception &e){
		if(rank == 0){
			stringstream ss;
			ss << ErrorLabel << e.what();
			SetMessage(ss.str().c_str());
		}
		return -1;
	}

	MPI_Barrier(MPI_COMM_WORLD);

#ifndef _DEBUG
	input = FormatArray(input);
	AddIndent(JSONIndent, input);
#endif

	vector<string> results, categs;
	if(spconf.IsPreprocess()){
		try{
			Run(rank, 1, spconf, nullptr, categs, results);
		}
		catch(const exception &e){
			stringstream ss;
			ss << ErrorLabel << e.what();
			SetMessage(ss.str().c_str());
			return 0;
		}
		if(rank == 0){
			ExportOutput(dataname, input, categs, results);
		}
		return 0;
	}

	dataname = spconf.GetDataPath();
	string namelower = dataname;
	transform(namelower.begin(), namelower.end(), namelower.begin(), ::tolower);
	size_t isjson = namelower.find(".json");
	if(isjson != string::npos){
		dataname = dataname.substr(0, isjson);
	}
	spconf.SetDataName(dataname);

	int iniser[2], nscans;
	if(spconf.IsScan()){
		vector<vector<double>> scanvalues;
		string scanprms[2], scanunits[2];
		nscans = spconf.GetScanCounts(scanvalues, scanprms, scanunits, iniser);
		if(spconf.IsAutoRange() && !spconf.Is4D()){
			vector<double> conf;
			vector<vector<double>> confv;
			int jxy[2];
			for(int n = 0; n < nscans; n++){
				spconf.SetScanCondition(n, jxy);
				spconf.Initialize();
				SpectraSolver spsolver(spconf);
				spsolver.GetRangeParameter(conf, confv);
				spconf.AssignRangeParameter(conf, confv, n == 0);
			}
			spconf.KillAutoRange();
		}
	}

	if(!spconf.CanBundle()){
		int scanidx[2] = {0, nscans}, jxy[2];
		for(int n = 0; n < nscans; n++){
			scanidx[0] = n;
			spconf.SetScanCondition(n, jxy);
			stringstream ss;
			if(iniser[1] < 0){
				ss << dataname << "_" << n+iniser[0];
			}
			else{
				ss << dataname << "_" << jxy[0]+iniser[0] << "_" << jxy[1]+iniser[1];
			}
			spconf.SetDataName(ss.str());
			try{
				Run(rank, nthreads, spconf, scanidx, categs, results);
			}
			catch (const exception &e) {
				if (rank == 0){
					stringstream ss;
					ss << ErrorLabel << e.what();
					SetMessage(ss.str().c_str());
				}
				return -1;
			}
			if (spconf.IsJSON()){
				if (rank == 0){
					string jsonfile = ss.str()+".json";
					ExportOutput(jsonfile, input, categs, results);
#ifdef _EMSCRIPTEN
					// do nothing
#else
					cout << ScanOutLabel << jsonfile << endl;
#endif
				}
			}
		}
		return 0;
	}

	try{
		Run(rank, nthreads, spconf, nullptr, categs, results);
	}
	catch (const exception &e) {
		if(rank == 0){
			stringstream ss;
			ss << ErrorLabel << e.what();
			SetMessage(ss.str().c_str());
		}
		return -1;
	} 

	if(spconf.IsJSON() || spconf.IsFixedPoint()){
		if (rank == 0){
			ExportOutput(dataname+".json", input, categs, results);
		}
	}
	return 0;
}

#ifdef _EMSCRIPTEN

int spectra_solver(int serno, int nthreads, string input)
{
	int retcode = 0;

	picojson::value v;
	picojson::parse(v, input);

	vector<picojson::object> inobjs;
	vector<string> datanames;
	if(v.is<picojson::array>()){
		picojson::array &objects = v.get<picojson::array>();
		for(int n = 0; n < objects.size(); n++){
			picojson::object &obj = objects[n].get<picojson::object>();
			for(const auto &p : obj){
				inobjs.push_back(p.second.get<picojson::object>());
				datanames.push_back(p.first);
			}
		}
	}
	else{
		inobjs.push_back(v.get<picojson::object>());
		datanames.push_back("single");
	}

	for(int n = 0; n < inobjs.size(); n++){
		if(RunProcess(inobjs[n], datanames[n], 0, 1, nthreads, serno) < 0){
			retcode = -1;
		}
	}
	return retcode;
}

#ifdef _MAIN
int main(int argc, char **argv)
{

	ifstream ifs(argv[2]);
	if(!ifs){
		return FILE_OPEN_FAILED;
	}
	string input = string((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
	spectra_solver(argv[2], 1, input);
}
#else
EMSCRIPTEN_BINDINGS(spectraModule) {
	emscripten::function("spectra_solver", &spectra_solver);
}
#endif

#else

int main(int argc, char **argv)
{
	MPI_Init(&argc, &argv);

	int mpiprocesses, rank;
	MPI_Bcast(&argc, 1, MPI_INT, 0, MPI_COMM_WORLD);
    MPI_Comm_size(MPI_COMM_WORLD, &mpiprocesses);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);

#ifdef _DEBUG
#ifndef __NOMPI__
	if(rank == 0){
		cout << "MPI Debug Mode: Attach the process and put any key to start." << endl;
		char c = getchar();
	}
	MPI_Barrier(MPI_COMM_WORLD);
#endif
#endif

	if(argc < 2){
		if(rank == 0){
			cout << "Usage:" << endl;
			cout << "(1) spectra_solver(_nompi) [-f] [inputfile]" << endl;
			cout << "(2) spectra_solver(_nompi) [json object]" << endl;
		}
		return -1;
	}

	string input;
	bool isclear = false;

	for(int j = 1; j < argc; j++){
		string argstr = string(argv[j]);
		if(argstr == "-clear"){
			isclear = true;
		}
	}

	int nthread = 1;
	if(argc == 2){
		input = string(argv[1]);
	}
	else if(string(argv[1]) != "-f"){
		if(rank == 0){
			cout << "Invalid input format" << endl;
		}
		return -1;
	}
	else{
		if(rank == 0){
			ifstream ifs(argv[2]);
			if (!ifs){
				return -1;
			}
			input = string((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
			ifs.close();
			if (isclear){
				remove(argv[2]);
			}
		}
		if(mpiprocesses > 1){
			int inputsize;
			if(rank == 0){
				inputsize = (int)input.length();
			}
			MPI_Bcast(&inputsize, 1, MPI_INT, 0, MPI_COMM_WORLD);
		
			char *buffer = new char[inputsize+1];
			if (rank == 0){
#ifdef WIN32
				strcpy_s(buffer, inputsize+1, input.c_str());
#else
				strcpy(buffer, input.c_str());
#endif
			}
			MPI_Bcast(buffer, inputsize+1, MPI_CHAR, 0, MPI_COMM_WORLD);
			if (rank > 0){
				input = string(buffer);
			}
			delete[] buffer;
		}
		else{
			if(argc >= 5 && string(argv[3]) == "-t"){
				nthread = atoi(argv[4]);
			}
		}
	}

	int retcode = 0;

	picojson::value v;
	picojson::parse(v, input);

	vector<picojson::object> inobjs;
	vector<string> datanames;
	if(v.is<picojson::array>()){
		picojson::array &objects = v.get<picojson::array>();
		for(int n = 0; n < objects.size(); n++){
			picojson::object &obj = objects[n].get<picojson::object>();
			for (const auto &p : obj){
				inobjs.push_back(p.second.get<picojson::object>());
				datanames.push_back(p.first);
			}
		}
	}
	else{
		inobjs.push_back(v.get<picojson::object>());
		datanames.push_back(argv[2]);
	}

#ifdef _DEBUG
	if(argc == 4 && string(argv[3]) == "-g"){
		// generate particle data file for debugging
		SpectraConfig spconf;
		spconf.LoadJSON(input, inobjs[0]);
		spconf.Initialize();
		SpectraSolver spsolver(spconf);
		Trajectory trajec(spsolver);
		ParticleGenerator partgen(spsolver, &trajec);
		vector<Particle> p;
		int nmquat = 25000;
		double R56t = 1.565e-5/CC;
		partgen.Init();
		int nm = partgen.Generate(p, nmquat, true);
		ofstream partdata("particles.dat");
		vector<double> items(5);
		for(int n = 0; n < nm; n++){
			items[0] = p[n]._qxy[0];
			items[1] = p[n]._xy[1];
			items[2] = p[n]._qxy[1];
			items[3] = p[n]._tE[0]+p[n]._tE[1]*R56t;
			items[4] = p[n]._tE[1];
			PrintDebugItems(partdata, p[n]._xy[0], items);
		}
		return 0;
	}
	if(argc == 4 && string(argv[3]) == "-c"){
		// to generate possible Output Items for reference.html
		SpectraConfig spconf;
		spconf.LoadJSON(input, inobjs[0]);
		spconf.Initialize();

		string calcfile = "help\\calc_types.txt";
		ifstream ifc(calcfile);
		if (!ifc){
			return -1;
		}
		string cinput = string((std::istreambuf_iterator<char>(ifc)), std::istreambuf_iterator<char>());
		ifc.close();

		vector<string> calcs, calrs;
		vector<int> indices;
		set<int> calcids;
		int icalcs = separate_items(cinput, calcs, "\n");
		for(int j = 0; j < icalcs; j++){
			if(separate_items(calcs[j], calrs, "\t") != 2){
				continue;
			}
			spconf.SetCalcType(calrs[1]);
			SpectraSolver spsolver(spconf);
			spsolver.GetOutputItemsIndices(indices);
			for(int i = 0; i < indices.size(); i++){
				calcids.insert(indices[i]);
			}
		}
		string items;
		for(set<int>::iterator itr = calcids.begin(); itr != calcids.end(); itr++){
			items += "[[\""+TitleLablesDetailed[*itr]+"\"], \" \"],\n";
		}
		calcfile = "help\\calc_details.txt";
		ofstream ifo(calcfile);
		ifo << items;
		return 0;
	}
#endif

	for(int n = 0; n < inobjs.size(); n++){
		if(RunProcess(inobjs[n], datanames[n], rank, mpiprocesses, nthread) < 0){
			retcode = -1;
		}
		if(inobjs.size() > 1 && rank == 0){
			cout << endl << "Process " << n << " Completed." << endl;
		}
	}

	MPI_Barrier(MPI_COMM_WORLD);
	MPI_Finalize();
	return retcode;
}

#endif