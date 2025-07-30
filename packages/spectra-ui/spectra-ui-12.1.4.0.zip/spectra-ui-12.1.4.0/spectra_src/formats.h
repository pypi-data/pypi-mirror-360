#ifndef formats_h
#define formats_h

#include <vector>
#include <string>

using namespace std;

void ExportAscii(const string filename, vector<string> &titles, 
	vector<int> &widths, vector<int> &precs, vector<vector<double>> &data, bool col1st);
void ExportAscii2D(const string filename, vector<string> &titles, 
	vector<int> &widths, vector<int> &precs, 
	vector<double> &x, vector<double> &y, vector<vector<vector<double>>> &data);
void ExportAscii(const string filename, vector<string> &titles, 
	vector<int> &widths, vector<int> &precs, 
	vector<vector<double>> &var, vector<vector<double>> &data);

#endif

