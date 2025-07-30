#include "simplex_config.h"
#include "common.h"
#include <math.h>
#include <sstream>
#include <algorithm>

// constructor
SimplexConfig::SimplexConfig(int serno)
{
	for(int n = 0; n < Categories; n++){
		m_prm[n] = DefaultPrm[n];
		m_array[n] = DefaultVec[n];
		m_bool[n] = DefaultBool[n];
		m_select[n] = DefaultSel[n];
		m_string[n] = DefaultStr[n];
		m_categidx.insert(make_pair(CategoryNames[n], n));
	}

	// set default values
	m_procs = 1;
	m_rank = 0;
	m_scanprmitems = atoi(ScanPrmItems.c_str());
	m_serno = serno;
}

// public functions

void SimplexConfig::LoadJSON(string &input, picojson::object &inobj)
{
	picojson::object postpobj;
	bool ispostp = inobj.count(PostPLabel) > 0;
	string dataname;
	if(ispostp){
		postpobj = inobj[PostPLabel].get<picojson::object>();
		if(inobj.count(DataNameLabel) == 0){
			throw runtime_error("No data name is given for post-processing.");
		}
		dataname= inobj[DataNameLabel].get<string>();
	}

	if(inobj.count(InputLabel) > 0){
		picojson::object iobj = inobj[InputLabel].get<picojson::object>();
		inobj = iobj;
	}
	if(ispostp){
		inobj.insert(make_pair(PostPLabel, picojson::value(postpobj)));
		inobj.insert(make_pair(DataNameLabel, picojson::value(dataname)));
	}
	m_ispostproc = inobj.count(PostPLabel);

	picojson::value val(inobj);
	picojson::object& obj = val.get<picojson::object>();
	obj.erase(ScanLabel);
	input = val.serialize(true);

	vector<vector<string>> datalabels;

	for(int n = 0; n < Categories; n++){
		if(inobj.count(CategoryNames[n]) == 0){
			continue;
		}
		f_LoadSingle(inobj, CategoryNames[n], ParameterFullNames[n], ParameterSimples[n],
			m_prm[n], m_array[n], m_bool[n], m_select[n], m_string[n], datalabels);
	}
	if(m_ispostproc){
		string dataname = inobj[DataNameLabel].get<string>();
		RemoveSuffix(dataname, ".json");
		m_datapath = dataname;
	}

	m_lasermod = false;
	m_ispreproc = false;
	if(inobj.count("runid") > 0){
		m_ispreproc = true;
		m_pptype = inobj["runid"].get<string>();
		m_lasermod = m_pptype == PPMicroBunchLabel;
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

		if(prmlabel == CustomSlice){
			dcont = &m_slice;
		}
		else if(prmlabel == CustomCurrent){
			dcont = &m_currprof;
		}
		else if(prmlabel == CustomEt){
			dcont = &m_Etprf;
		}
		else if(prmlabel == WakeDataLabel){
			dcont = &m_wakeprf;
		}
		else if(prmlabel == MonoDataLabel){
			dcont = &m_monoprf;
		}
		else if(prmlabel == MultiHarmContLabel){
			picojson::array hdata = pobj[prmlabel].get<picojson::array>();
			f_SetMultiHarmonic(hdata);
			continue;
		}
		else if(prmlabel == TaperCustomLabel){
			picojson::array tdata = pobj[prmlabel].get<picojson::array>();
			f_SetCustomTaper(tdata);
			continue;
		}
		else if(prmlabel == DataAllocLabel){
			picojson::array udata = pobj[prmlabel].get<picojson::array>();
			f_SetUndulatorData(udata);
			continue;
		}
		else if(prmlabel == OffsetEachLabel){
			picojson::array adata = pobj[prmlabel].get<picojson::array>();
			f_SetUAlignOffset(adata);
			continue;
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
		if(dataobj.size() == 0){
			throw runtime_error("\""+prmlabel+"\" data not imported or found");
		}
		dcont->Set(dataobj, dimension, titles);
	}

	if(inobj.count(UndDataLabel) > 0){
		tuple<int, vector<string>> uformat = DataFormat.at(UndDataLabel);
		vector<string> titles = get<1>(uformat);

		picojson::object pobj = inobj[UndDataLabel].get<picojson::object>();
		picojson::array datanames = pobj["names"].get<picojson::array>();
		picojson::array dataconts = pobj["data"].get<picojson::array>();
		int ndata = (int)min(datanames.size(), dataconts.size());
		for(int n = 0; n < ndata; n++){
			string dataname = datanames[n].get<string>();
			m_unames.push_back(dataname);
			DataContainer udata;
			m_uconts.push_back(udata);
			picojson::object dataobj = dataconts[n].get<picojson::object>();
			m_uconts.back().Set(dataobj, 1, titles);
		}
	}

	if(BuiltinXtals.count(m_select[Chicane_][xtaltype_]) > 0){
		m_prm[Chicane_][formfactor_] = BuiltinXtals.at(m_select[Chicane_][xtaltype_])[0];
		m_prm[Chicane_][latticespace_] = BuiltinXtals.at(m_select[Chicane_][xtaltype_])[1];
		m_prm[Chicane_][unitvol_] = BuiltinXtals.at(m_select[Chicane_][xtaltype_])[2];
	}

	m_steadystate = !m_lasermod && m_select[SimCtrl_][simmode_] == SSLabel;
	m_cyclic = !m_lasermod && m_select[SimCtrl_][simmode_] == CyclicLabel;

	if(m_lasermod){
		m_select[Und_][umodel_] = IdealLabel;
		m_prm[Und_][segments_] = m_prm[Mbunch_][mbsegments_];
		m_select[Und_][opttype_] = NotAvaliable;
		m_select[Alignment_][ualign_] = IdealLabel;
		m_select[Alignment_][BPMalign_] = IdealLabel;
		m_bool[Dispersion_][einjec_] = false;
		m_bool[Dispersion_][kick_] = false;
		m_bool[DataDump_][temporal_] = false;
		m_bool[DataDump_][spectral_] = false;
		m_bool[DataDump_][spatial_] = false;
		m_bool[DataDump_][angular_] = false;
		m_bool[DataDump_][particle_] = false;
		m_bool[DataDump_][radiation_] = false;
		m_bool[Wake_][wakeon_] = false;
		m_bool[SimCtrl_][autostep_] = false;
		m_prm[SimCtrl_][step_] = 1;

		for(int j = 0; j < 2; j++){
			m_array[SimCtrl_][simrange_][j] =  m_array[Mbunch_][mbtrange_][j];
		}
	}
	if(m_steadystate){
		m_bool[DataDump_][temporal_] = false;
		m_bool[DataDump_][spectral_] = false;
	}
}

bool SimplexConfig::CheckScanProcess(picojson::object &obj)
{
	string type;
	vector<double> values;
	vector<vector<double>> dvectors;
	vector<bool> bools;
	vector<string> selects, strs;
	vector<vector<string>> dconts;
	int iscan;
	bool isint;
	vector<vector<double>> scanprms;

	picojson::object scanobj;
	if(obj.count(ScanLabel) > 0){
		scanobj = obj[ScanLabel].get<picojson::object>();
	}
	else{
		return false;
	}

	m_scancateg = -1;
	for(int n = 0; n < Categories; n++){
		if(scanobj.count(CategoryNames[n]) > 0){
			f_LoadSingle(scanobj, CategoryNames[n], ParameterFullNames[n], ParameterSimples[n],
				values, dvectors, bools, selects, strs, dconts, nullptr, &m_scanprmlabel, &iscan, &scanprms, &isint);
			m_scancateg = n;
			break;
		}
	}
	if(m_scancateg < 0){
		return false;
	}

	m_scanitem = iscan;
	m_scan2d = scanprms.size() > 1;

	if(m_scan2d == false){
		m_scanprms[0] = m_scanprmlabel;
	}
	else{
		size_t nf = m_scanprmlabel.find("(");
		string unit, value;
		if(nf == string::npos){
			unit = "";
			value = m_scanprmlabel;
		}
		else{
			unit = m_scanprmlabel.substr(nf+1);
			int nr = (int)unit.find(")");
			if(nr >= 0){
				unit = unit.substr(0, nr);
			}
			value = m_scanprmlabel.substr(0, nf);
		}
		for(int j = 0; j < 2; j++){
			m_scanunits[j] = unit;
		}

		nf = value.find(",");
		string suf[2] = {"_1", "_2"};
		if(nf == string::npos){
			for(int j = 0; j < 2; j++){
				m_scanprms[j] = m_scanprmlabel+suf[j];
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
	}

	for(int j = 0; j < (m_scan2d?2:1); j++){
		if(scanprms[j][2] == 0){
			continue;
		}
		else if(scanprms[j][2] < 0){
			scanprms[j][2] = scanprms[0][2];
		}
		double vini = scanprms[j][0];
		double vfin = scanprms[j][1];
		if(isint){ // integer parameter
			m_scanvalues[j].push_back(vini);
			do{
				vini += fabs(scanprms[j][2]);
				m_scanvalues[j].push_back(vini);
			}while(m_scanvalues[j].back() < vfin);
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

bool SimplexConfig::Initialize()
{
//	m_gamma = m_eb[eenergy_]*1000.0/MC2MeV;
	return true;
}

double SimplexConfig::GetPrm(string categ, int index)
{
	return m_prm[m_categidx[categ]][index];
}

double SimplexConfig::GetVector(string categ, int index, int jxy)
{
	return m_array[m_categidx[categ]][index][jxy];
}

bool SimplexConfig::GetBoolean(string categ, int index)
{
	return m_bool[m_categidx[categ]][index];
}

string SimplexConfig::GetSelection(string categ, int index)
{
	return m_select[m_categidx[categ]][index];
}


int SimplexConfig::GetScanCounts(
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
			if(m_scaniniser[1] < 0){
				nscans = (int)m_scanvalues[0].size();
			}
			else{
				nscans = (int)(m_scanvalues[0].size()*m_scanvalues[1].size());
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

void SimplexConfig::SetScanCondition(int index, int jxy[], string &input)
{
	if(!m_isscan){
		return;
	}
	stringstream ss;
	string delim[] = {":", ","};
	if(m_scan2d){
		int ncol = (int)m_scanvalues[0].size();
		if(m_scaniniser[1] < 0){ // 2d link
			jxy[0] = jxy[1] = index;
		}
		else if(ncol == 0){
			jxy[0] = 0;
			jxy[1] = index;
		}
		else{
			jxy[0] = index%ncol;
			jxy[1] = index/ncol;
			// [0] -> varies first
		}

		for(int j = 0; j < 2; j++){
			if(m_scanvalues[j].size() == 0){
				continue;
			}
			m_array[m_scancateg][m_scanitem][j] = m_scanvalues[j][jxy[j]];
		}
		delim[0] = "[";
		delim[1] = "]";
		ss << m_array[m_scancateg][m_scanitem][0] << "," << m_array[m_scancateg][m_scanitem][1];
	}
	else{
		m_prm[m_scancateg][m_scanitem] = m_scanvalues[0][index];
		ss << " " << m_prm[m_scancateg][m_scanitem];
	}
	int npos[2];
	npos[0] = (int)input.find(delim[0], input.find(m_scanprmlabel));
	npos[1] = (int)input.find(delim[1], npos[0]);

	if(!m_scan2d){
		int ncurl = (int)input.find("}", npos[0]);
		int ncr = (int)input.find("\n", npos[0]);
		npos[1] = min(npos[1], min(ncurl, ncr));
	}

	input.replace(npos[0]+1, npos[1]-npos[0]-1, ss.str());
}

void SimplexConfig::GetScanValues(int index, vector<double> &scanvalues)
{
	if(m_scan2d){
		scanvalues.resize(2);
		for(int j = 0; j < 2; j++){
			scanvalues[j] = m_array[m_scancateg][m_scanitem][j];
		}
	}
	else{
		scanvalues.resize(1);
		scanvalues[0] = m_scanvalues[0][index];
	}
}

void SimplexConfig::SetMPI(int rank, int mpiprocesses)
{
	m_rank = rank;
	m_procs = mpiprocesses;
}

void SimplexConfig::SetDataPath(const string datapath)
{
	m_datapath = datapath;
}

string SimplexConfig::GetDataPath()
{
	int serno = (int)floor(0.5+m_prm[Outfile_][serial_]);
	string dataname = m_string[Outfile_][prefix_];
	if(serno >= 0){
		stringstream ss;
		ss << serno;
		dataname += "-"+ss.str();
	}
	PathHander datapath(m_string[Outfile_][folder_]);
	datapath.append(dataname);
	return datapath.string();
}

// private functions
void SimplexConfig::f_LoadSingle(picojson::object &obj, string categ,
		const map<string, tuple<int, string>> &maplabeld,
		const map<string, tuple<int, string>> &maplabels,
		vector<double> &prm, vector<vector<double>> &prmv, 
		vector<bool> &prmb, vector<string> &prmsel, 
		vector<string> &prmstr, vector<vector<string>> &datalabels, 
		string *parent, string *prmname, 
		int *scanidx, vector<vector<double>> *scanprms, bool *isint)
{
	picojson::object sglobj = obj[categ].get<picojson::object>();
	string type;
	int index;

	if(isint != nullptr){
		*isint = false;
	}

	for(const auto& p : sglobj){
		try {
			type = get<1>(maplabeld.at(p.first));
			index = get<0>(maplabeld.at(p.first));
		}
		catch (const out_of_range) {
			try {
				type = get<1>(maplabels.at(p.first));
				index = get<0>(maplabels.at(p.first));
			}
			catch (const out_of_range){
				string msg = "Parameter \""+p.first+"\" is not available. Ignored.";
				continue;
			}
		}

		if(type == NumberLabel){
			if(prmname != nullptr){
				picojson::array &vec = sglobj[p.first].get<picojson::array>();
				if (vec.size() < m_scanprmitems){
					string msg = "invalid scan format for \""+p.first+"\"";
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
					if(vec[m_scanprmitems].get<string>() == IntegerLabel && isint != nullptr){
						*isint = true;
					}
				}
				continue;
			}
			prm[index] = p.second.get<double>();
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
					if(vec[m_scanprmitems].get<string>() == IntegerLabel && isint != nullptr){
						*isint = true;
					}
				}
				continue;
			}
			if(vec.size() != 2){
				string msg = "invalid format for \""+p.first+"\"";
				throw runtime_error(msg.c_str());
			}
			try {
				prmv[index][0] = vec[0].get<double>();
				prmv[index][1] = vec[1].get<double>();
			}
			catch (const exception&) {
				string msg = "invalid format for \""+p.first+"\"";
				throw runtime_error(msg.c_str());
			}
		}
		else if(type == BoolLabel){
			prmb[index] = p.second.get<bool>();
		}
		else if(type == SelectionLabel){
			prmsel[index] = p.second.get<string>();
		}
		else if(type == StringLabel){
			prmstr[index] = p.second.get<string>();
		}
		else if(type == DataLabel || type == GridLabel){
			if(parent != nullptr){
				datalabels.push_back(vector<string> {p.first, *parent, categ});
			}
			else{
				datalabels.push_back(vector<string> {p.first, categ});
			}
		}
	}
}

void SimplexConfig::f_ThrowException(int index, string categ)
{
	stringstream msg;
	msg << "No parameters available for index " << index << " in category" << categ;
	throw out_of_range(msg.str());
}

void SimplexConfig::f_SetMultiHarmonic(picojson::array &hdata)
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

void SimplexConfig::f_SetCustomTaper(picojson::array &tdata)
{
	vector<double> tvalues(2, 0.0);
	for(int n = 0; n < tdata.size(); n++){
		picojson::array item = tdata[n].get<picojson::array>();
		if(item.size() < 2){
			continue;
		}
		for(int j = 0; j < 2; j++){
			string hs = item[j].get<string>();
			tvalues[j] = atof(hs.c_str());
		}
		m_tapercont.push_back(tvalues);
	}
}

void SimplexConfig::f_SetUndulatorData(picojson::array &udata)
{
	for(int n = 0; n < udata.size(); n++){
		picojson::array item = udata[n].get<picojson::array>();
		if(item.size() < 2){
			continue;
		}
		vector<string> segcont {item[0].get<string>(), item[1].get<string>()};
		m_udcont.push_back(segcont);
	}
}

void SimplexConfig::f_SetUAlignOffset(picojson::array &adata)
{
	vector<double> mvalues(3, 0.0);
	for(int n = 0; n < adata.size(); n++){
		picojson::array item = adata[n].get<picojson::array>();
		if(item.size() < 3){
			continue;
		}
		for(int j = 0; j < 3; j++){
			string hs = item[j].get<string>();
			mvalues[j] = atof(hs.c_str());
		}
		m_ualignment.push_back(mvalues);
	}
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
	if(idir != std::string::npos){
		m_directory = pathname.substr(0, idir+1);
		if(idir < pathname.size()-1){
			name = pathname.substr(idir+1);
		}
	}
	else{
		name = pathname;
	}
	replace_filename(name);
}

std::string PathHander::string()
{
	return m_directory+m_name+m_extension;
}

void PathHander::replace_extension(std::string ext)
{
	m_extension = ext;
}

void PathHander::replace_filename(std::string name)
{
	m_name = m_extension = "";
	size_t edir = name.find_last_of(".");
	if(edir != std::string::npos){
		m_name = name.substr(0, edir);
		m_extension = name.substr(edir);
	}
	else{
		m_name = name;
	}
}

void PathHander::append(std::string name)
{
	if(m_directory != ""){
		m_directory += m_name+m_extension+m_separator;
	}
	replace_filename(name);
}

PathHander PathHander::filename()
{
	PathHander path(m_name+m_extension);
	return path;
}

PathHander &PathHander::operator = (const std::string &pathname)
{
	Create(pathname);
	return *this;
}
