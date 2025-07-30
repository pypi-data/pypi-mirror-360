#ifndef simplex_config_h
#define simplex_config_h

#include "picojson.h"
#include "simplex_input.h"
#include "data_container.h"
#include "numerical_common_definitions.h"

using namespace std;

class PathHander
{
public:
	PathHander(){}
	PathHander(std::string pathname);
	void Create(std::string pathname);
	std::string string();
	void replace_extension(std::string ext);
	void replace_filename(std::string name);
	void append(std::string name);
	PathHander filename();
	PathHander &operator = (const std::string &pathname);

private:
	std::string m_directory;
	std::string m_name;
	std::string m_extension;
	std::string m_separator;
};

class SimplexConfig 
{
public:
	SimplexConfig(int serno = -1);
	void LoadJSON(string &input, picojson::object &inobj);
	bool CheckScanProcess(picojson::object &obj);
	bool Initialize();

	double GetPrm(string categ, int index);
	double GetVector(string categ, int index, int jxy);
	bool GetBoolean(string categ, int index);
	string GetSelection(string categ, int index);

	int GetScanCounts(vector<vector<double>> &scanvalues, 
		string scanprms[], string scanunits[], int scaniniser[]);
	void SetScanCondition(int index, int jxy[], string &input);
	void GetScanValues(int index, vector<double> &scanvalues);
	bool IsScan(){return m_isscan;}
	bool IsPreprocess(){return m_ispreproc;}
	bool IsPostprocess(){return m_ispostproc;}
	bool IsModulation(){return m_lasermod;}

	void SetMaxMemory(double memgb){ m_maxmem = memgb; }

	void SetMPI(int rank, int mpiprocesses);
	void SetDataPath(const string datapath);
	string GetDataPath();

private:
	void f_LoadSingle(picojson::object &obj, string categ,
		const map<string, tuple<int, string>> &maplabeld,
		const map<string, tuple<int, string>> &maplabels,
		vector<double> &prm, vector<vector<double>> &prmv,
		vector<bool> &prmb, vector<string> &prmsel, 
		vector<string> &prmstr, vector<vector<string>> &datalabels, 
		string *parent = nullptr, string *prmname = nullptr, 
		int *scanidx = nullptr, vector<vector<double>> *scanprms = nullptr, bool *isint = nullptr);

	void f_SetMultiHarmonic(picojson::array &hdata);
	void f_SetCustomTaper(picojson::array &tdata);
	void f_SetUndulatorData(picojson::array &udata);
	void f_SetUAlignOffset(picojson::array &adata);

	void f_ThrowException(int index, string categ);

protected:
	// input parameters
	vector<double> m_prm[Categories];
	vector<vector<double>> m_array[Categories];
	vector<bool> m_bool[Categories];
	vector<string> m_select[Categories];
	vector<string> m_string[Categories];
	double m_gamma;

	// category name <-> index
	map<string, int> m_categidx;

	DataContainer m_slice;
	DataContainer m_currprof;
	DataContainer m_Etprf;
	DataContainer m_wakeprf;
	DataContainer m_monoprf;
	vector<vector<double>> m_harmcont;
	vector<vector<double>> m_tapercont;
	vector<vector<double>> m_ualignment;
	vector<vector<string>> m_udcont;
	vector<string> m_unames;
	vector<DataContainer> m_uconts;

	// scan configuration
	int m_scanprmitems;
	bool m_isscan;
	int m_scancateg;
	int m_scanitem;
	bool m_scan2d;
	vector<double> m_scanvalues[2];
	int m_scaniniser[2];
	string m_scanprms[2];
	string m_scanunits[2];
	string m_scanprmlabel;

	// steady state mode or cyclic mode
	bool m_steadystate;
	bool m_cyclic;

	// preprocessing;
	string m_pptype;
	bool m_ispreproc;
	bool m_lasermod;

	double m_maxmem;
	bool m_ispostproc;

	// MPI configurations
	int m_procs;
	int m_rank;

	// output dataname
	PathHander m_datapath;

	// raw data object
	picojson::object m_tobj;

	// serial number (for progressbar in emscripten)
	int m_serno;
};

#endif