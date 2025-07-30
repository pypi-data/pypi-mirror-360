#include <algorithm>
#include <regex>
#include "json_writer.h"

#include <iostream>

int GetIndexMDV(int mesh[], int n[], int dim)
{
	int index = n[dim-1];
	for(int nd = dim-2; nd >= 0; nd--){
		index = index*mesh[nd]+n[nd];
	}
	return index;
}

void GetIndicesMDV(int index, vector<int> &mesh, vector<int> &n, int dim)
{
	for(int nd = 0; nd < dim; nd++){
		n[nd] = index%mesh[nd];
		index = (index-n[nd])/mesh[nd];
	}
}

string FormatArray(string jsonstr)
{
	regex regstr("\n *| +");
    size_t ist, iend;
	string bef, mid, midorg, aft;
    
    iend = 0;
    while(1) {
        ist = jsonstr.find("[", iend);
        iend = jsonstr.find("]", ist);
        if(ist == string::npos || iend == string::npos){
            break;
        }
        bef = jsonstr.substr(0, ist+1);
        midorg = jsonstr.substr(ist+1, iend-ist-1);
        aft = jsonstr.substr(iend);
		if(midorg.find("\"") == string::npos){
			mid = regex_replace(midorg, regstr, "");
		}
		else{// skip the string array
			mid = midorg;
		}
        iend -= midorg.size()-mid.size();
        jsonstr = bef+mid+aft;
    };
    return jsonstr;
}

void WriteJSONMatrix(stringstream &ss, int indent, vector<vector<double>> &values, bool isnext)
{
	PrependIndent(indent, ss);
	ss << "[" << endl;
	for(int m = 0; m < values[0].size(); m++){
		if (m > 0){
			ss << "," << endl;
		}
		PrependIndent(indent, ss);
		ss << "[";
		for (int n = 0; n < values.size(); n++){
			if (n > 0){
				ss << ",";
			}
			ss << values[n][m];
		}
		ss << "]";
	}
	ss << endl;
	PrependIndent(indent, ss);
	ss << "]";
	if(isnext){
		ss << "," << endl;
	}
}

void AddIndent(int indent, string &jstr)
{
	string delim = "\n";
	for(int j = 0; j < indent; j++){
		delim += " ";
	}
	jstr = regex_replace(jstr, regex("\n"), delim);
}

void Copy2d(vector<vector<double>> &org, vector<double> &data)
{
	int mesh[2], n[2], mtotal, index;
	mesh[0] = (int)org.size();
	mesh[1] = (int)org[0].size();
	mtotal = mesh[0];
	for(int j = 1; j < 2; j++){
		mtotal *= mesh[j];
	}

	if(data.size() < mtotal){
		data.resize(mtotal);
	}
	for(n[0] = 0; n[0] < mesh[0]; n[0]++){
		for (n[1] = 0; n[1] < mesh[1]; n[1]++){
			index = GetIndexMDV(mesh, n, 2);
			data[index] = org[n[0]][n[1]];
		}
	}
}

void Copy3d(vector<vector<vector<double>>> &org, vector<double> &data)
{
	int mesh[3], n[3], mtotal, index;
	mesh[0] = (int)org.size();
	mesh[1] = (int)org[0].size();
	mesh[2] = (int)org[0][0].size();

	mtotal = mesh[0];
	for(int j = 1; j < 3; j++){
		mtotal *= mesh[j];
	}
	if(data.size() < mtotal){
		data.resize(mtotal);
	}

	for(n[0] = 0; n[0] < mesh[0]; n[0]++){
		for (n[1] = 0; n[1] < mesh[1]; n[1]++){
			for (n[2] = 0; n[2] < mesh[2]; n[2]++){
				index = GetIndexMDV(mesh, n, 3);
				data[index] = org[n[0]][n[1]][n[2]];
			}
		}
	}
}

void Copy4d(vector<vector<vector<vector<double>>>> &org, vector<double> &data)
{
	int mesh[4], n[4], mtotal, index;
	mesh[0] = (int)org.size();
	mesh[1] = (int)org[0].size();
	mesh[2] = (int)org[0][0].size();
	mesh[3] = (int)org[0][0][0].size();

	mtotal = mesh[0];
	for(int j = 1; j < 4; j++){
		mtotal *= mesh[j];
	}
	if(data.size() < mtotal){
		data.resize(mtotal);
	}

	for(n[0] = 0; n[0] < mesh[0]; n[0]++){
		for (n[1] = 0; n[1] < mesh[1]; n[1]++){
			for (n[2] = 0; n[2] < mesh[2]; n[2]++){
				for (n[3] = 0; n[3] < mesh[3]; n[3]++){
					index = GetIndexMDV(mesh, n, 4);
					data[index] = org[n[0]][n[1]][n[2]][n[3]];
				}
			}
		}
	}
}
