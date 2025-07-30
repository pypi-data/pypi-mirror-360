#include <iostream>
#include <fstream>
#include <sstream>
#include <iomanip>
#include "formats.h"

void ExportAscii(const string filename, vector<string> &titles, 
	vector<int> &widths, vector<int> &precs, vector<vector<double>> &data, bool col1st)
{
	stringstream ss;
	int nrows = (int)titles.size();

	for(int j = 0; j < nrows; j++){
		ss << setw(widths[j]) << titles[j];
	}
	ss << endl;

	ss << scientific;
	int ncols = (int)(col1st ? data.size() : data[0].size());
	for(int n = 0; n < ncols; n++){
		for (int j = 0; j < nrows; j++){
			ss << setw(widths[j]) << setprecision(precs[j]);
			if(col1st){
				ss << data[n][j];
			}
			else{
				ss << data[j][n];
			}
		}
		ss << endl;
	}

	ofstream ofs(filename);
	if(ofs){
		ofs << ss.str() << endl;
	}
}

void ExportAscii2D(const string filename, vector<string> &titles, 
	vector<int> &widths, vector<int> &precs, 
	vector<double> &x, vector<double> &y, vector<vector<vector<double>>> &data)
{
	stringstream ss;
	int nrows = (int)titles.size();

	for(int j = 0; j < nrows; j++){
		ss << setw(widths[j]) << titles[j];
	}
	ss << endl;

	ss << scientific;
	for (int m = 0; m < y.size(); m++){
		for (int n = 0; n < x.size(); n++){
			ss << setw(widths[0]) << setprecision(precs[0]) << x[n];
			ss << setw(widths[1]) << setprecision(precs[1]) << y[m];
			for (int j = 2; j < nrows; j++){
				ss << setw(widths[j]) << setprecision(precs[j]) << data[j-2][n][m];
			}
			ss << endl;
		}
	}

	ofstream ofs(filename);
	if(ofs){
		ofs << ss.str() << endl;
	}
}

void ExportAscii(const string filename, vector<string> &titles, 
	vector<int> &widths, vector<int> &precs, 
	vector<vector<double>> &var, vector<vector<double>> &data)
{
	stringstream ss;
	int nrows = (int)titles.size();
	int ndim = (int)var.size();
	vector<int> ndata(ndim+1), indices(ndim);
	ndata[0] = 1;
	for(int j = 1; j <= ndim; j++){
		ndata[j] = ndata[j-1]*(int)var[j-1].size();
	}

	for(int j = 0; j < nrows; j++){
		ss << setw(widths[j]) << titles[j];
	}
	ss << endl;

	ss << scientific;
	for(int n = 0; n < ndata[ndim]; n++){
		int nres = n;
		for(int j = ndim-1; j > 0; j--){
			indices[j] = nres/ndata[j];
			nres = nres%ndata[j];
 		}
		indices[0] = nres;
		for(int j = 0; j < ndim; j++){
			ss << setw(widths[j]) << setprecision(precs[j]) << var[j][indices[j]];
		}
		for (int j = ndim; j < nrows; j++){
			ss << setw(widths[j]) << setprecision(precs[j]) << data[j-ndim][n];
		}
		ss << endl;
	}

	ofstream ofs(filename);
	if(ofs){
		ofs << ss.str() << endl;
	}
}

