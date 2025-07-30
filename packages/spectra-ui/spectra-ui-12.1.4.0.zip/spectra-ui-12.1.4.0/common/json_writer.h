#ifndef json_writer_h
#define json_writer_h

#include <sstream>
#include <string>
#include <vector>

using namespace std;

template <class T>
void PrependIndent(int indent, T &ss)
{
	for(int j = 0; j < indent; j++){
		ss << " ";
	}
}

template <class T>
void WriteJSONArray(stringstream &ss, int indent, vector<T> &vec, const char *title, bool isquote, bool isnext)
{
	PrependIndent(indent, ss);
	if(title != nullptr){
		ss << "\"" << title << "\": ";
	}
	ss << "[";
	for(int n = 0; n < vec.size(); n++){
		if(n > 0){
			ss << ",";
		}
		if(isquote){
			ss << "\"" << vec[n] << "\"";
		}
		else{
			ss << vec[n];
		}
	}
	ss << "]";
	if(isnext){
		ss << "," << endl;
	}
}

template <class T>
void WriteJSONValue(stringstream &ss, 
	int indent, T &value, const char *title, bool isquote, bool isnext, bool skipnl = false)
{
	PrependIndent(indent, ss);
	ss << "\"" << title << "\": ";
	if(isquote){
		ss << "\"" << value << "\"";
	}
	else{
		ss << value;
	}
	if(isnext){
		if(skipnl){
			ss << ", ";
		}
		else{
			ss << "," << endl;
		}
	}
}

template <class T>
void WriteJSONData(stringstream &ss,
	int indent, vector<T> &values, int delmesh, bool isnext, bool isbrace)
{
	if(isbrace){
		PrependIndent(indent, ss);
		ss << "[";
	}
	for(int n = 0; n < values.size(); n++){
		if(n > 0){
			ss << ",";
		}
		if(n > 0 && delmesh > 0){
			if(n%delmesh == 0){
				ss << endl;
				PrependIndent(indent, ss);
			}
		}
		ss << values[n];
	}
	if(isbrace){
		if(delmesh > 0){
			ss << endl;
			PrependIndent(indent, ss);
		}
		ss << "]";
	}
	if(isnext){
		ss << "," << endl;
	}
}

int GetIndexMDV(int mesh[], int n[], int dim);
void GetIndicesMDV(int index, vector<int> &mesh, vector<int> &n, int dim);

void Copy2d(vector<vector<double>> &org, vector<double> &data);
void Copy3d(vector<vector<vector<double>>> &org, vector<double> &data);
void Copy4d(vector<vector<vector<vector<double>>>> &org, vector<double> &data);

void WriteJSONMatrix(stringstream &ss, 
	int indent, vector<vector<double>> &values, bool isnext);
string FormatArray(string jsonstr);
void AddIndent(int indent, string &jstr);

#endif
