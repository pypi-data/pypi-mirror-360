#include <vector>
#include <string>
#include <thread>
#include "simplex_solver.h"
#include "json_writer.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

#ifdef _EMSCRIPTEN
#ifndef _MAIN
#include <emscripten/bind.h>
#include <emscripten.h>
#include <sstream>
#endif
#endif

using namespace std;

#ifdef _EMSCRIPTEN
#include <emscripten/bind.h>
#include <emscripten.h>

EM_JS(void, set_output, (const char *pdataname, const char *poutput), {
	let output = UTF8ToString(poutput);
	let dataname = UTF8ToString(pdataname);
	SetOutput(dataname, output);
});

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

void ExportOutput(string dataname, string &input, vector<string> &categs, vector<string> &results)
{
	string outfile = dataname+".json";
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
	vector<vector<double>> &vararray, vector<vector<vector<double>>> &data, int fdim)
{
	int nscon = isnewl ? indlevel+2 : indlevel+1;
	for(int i = 0; i < dimension; i++){
		WriteJSONData(ssresult, (indlevel+1)*JSONIndent, vararray[i], 0, true, true);
	}
	for(int i = 0; i < nitems; i++){
		PrependIndent((indlevel+1)*JSONIndent, ssresult);
		ssresult << "[";
		for(int ns = 0; ns < nscans; ns++){
			if((isnewl || fdim > 1) && ns == 0){
				ssresult << endl;
			}
			if(nscans > 1){
				PrependIndent(nscon*JSONIndent, ssresult);
			}
			if(fdim > 1){
				int ndfm = (int)data[ns][i].size()/fdim;
				vector<double> dcopy(ndfm);
				PrependIndent(JSONIndent, ssresult);
				ssresult << "[" << endl;
				for(int f = 0; f < fdim; f++){
					copy(data[ns][i].begin()+f*ndfm, data[ns][i].begin()+(f+1)*ndfm, dcopy.begin());
					WriteJSONData(ssresult, (nscon+2)*JSONIndent, dcopy, delmesh, f < fdim-1, true);
				}
				ssresult << endl;
				PrependIndent((nscon+1)*JSONIndent, ssresult);
				ssresult << (ns == nscans-1 ? "]" : "],");
				if(ns < nscans-1){
					ssresult << endl;
				}
			}
			else{
				WriteJSONData(ssresult, nscon*JSONIndent, data[ns][i], delmesh, ns < nscans-1, false);
			}
		}
		if(isnewl || fdim > 1){
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

int RunProcess(picojson::object &inobj, string dataname,
	int rank, int mpiprocesses, int nthreads, double memlim, int serno = -1)
{
	vector<string> results, categs;
	string input;
	SimplexConfig spconf;
	spconf.SetMPI(rank, mpiprocesses);

	RemoveSuffix(dataname, ".json");
	spconf.SetDataPath(dataname);

	try{
		spconf.LoadJSON(input, inobj);
	}
	catch(const exception &e){
		if(rank == 0){
			stringstream ss;
			ss << ErrorLabel << e.what() << endl;
			SetMessage(ss.str().c_str());
		}
		return -1;
	}
	MPI_Barrier(MPI_COMM_WORLD);

	if(memlim > 0){
		spconf.SetMaxMemory(memlim);
	}

	if(spconf.IsModulation()){
		try{
			SimplexSolver spsolver(spconf);
			spsolver.RunSingle(categs, results);
			spsolver.RunPreProcessorMB(categs, results);
			spsolver.DeletePointers();
			ExportOutput(dataname, input, categs, results);
		}
		catch(const exception &e) {
			if(rank == 0){
				stringstream ss;
				ss << ErrorLabel << e.what() << endl;
				SetMessage(ss.str().c_str());
			}
			return -1;
		}
		return 0;
	}

	if(spconf.IsPreprocess()){
		try{
			SimplexSolver spsolver(spconf);
			spsolver.RunPreProcessor(categs, results);
			spsolver.DeletePointers();
			ExportOutput(dataname, input, categs, results);
		}
		catch(const exception &e){
			stringstream ss;
			ss << ErrorLabel << e.what() << endl;
			SetMessage(ss.str().c_str());
			return -1;
		}
		return 0;
	}

	if(spconf.IsPostprocess()){
		try{
			SimplexSolver spsolver(spconf);
			spsolver.PostProcess(categs, results);
			spsolver.DeletePointers();
			ExportOutput(dataname, input, categs, results);
		}
		catch(const exception &e){
			stringstream ss;
			ss << ErrorLabel << e.what() << endl;
			SetMessage(ss.str().c_str());
			return -1;
		}
		return 0;
	}

#ifndef _DEBUG
	// format the input objects for output file
	input = FormatArray(input);
	AddIndent(JSONIndent, input);
#endif

	vector<vector<double>> scanvalues;
	string scanprms[2], scanunits[2];
	int iniser[2], jxy[2];
	int nscans = spconf.GetScanCounts(scanvalues, scanprms, scanunits, iniser);
	dataname = spconf.GetDataPath();
	for(int n = 0; n < nscans; n++){
		spconf.SetScanCondition(n, jxy, input);
		stringstream ss;
		if(nscans == 1){
			ss << dataname;
		}
		else if(iniser[1] < 0){
			ss << dataname << "_" << n+iniser[0];
		}
		else{
			ss << dataname << "_" << jxy[0]+iniser[0] << "_" << jxy[1]+iniser[1];
		}
		spconf.SetDataPath(ss.str());
		auto runthread = [&](int thid, MPIbyThread *thread){
			SimplexSolver spsolver(spconf, thid, thread);
			spsolver.RunSingle(categs, results);
			spsolver.DeletePointers();
			};
		try{
			if(nthreads > 1){
				MPIbyThread mpithread(nthreads);
				vector<thread> solvers;
				for(int thid = 0; thid < nthreads-1; thid++){
					solvers.emplace_back(runthread, thid+1, &mpithread);
				}
				runthread(0, &mpithread);
				for(int thid = 0; thid < nthreads-1; thid++){
					solvers[thid].join();
				}
			}
			else{
				runthread(0, nullptr);
			}
		}
		catch(const exception &e) {
			if(rank == 0){
				stringstream ss;
				ss << ErrorLabel << e.what() << endl;
				SetMessage(ss.str().c_str());
			}
			return -1;
		}
		if(rank == 0){
			ExportOutput(ss.str(), input, categs, results);
#ifdef _EMSCRIPTEN
			// do nothing
#else
			if(nscans > 1){
				cout << Fin1ScanLabel << n+1 << "/" << nscans << " Finished" << endl;
				string jsonfile = ss.str()+".json";
				cout << ScanOutLabel << jsonfile << endl;
			}
#endif
		}
		categs.clear();
		results.clear();
	}
	return 0;
}


#ifdef _EMSCRIPTEN

int simplex_solver(int serno, int nthreads, string input)
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
		return -1;
	}
	string input = string((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
	simplex_solver(argv[2], 1, input);
}
#else
EMSCRIPTEN_BINDINGS(simplexModule) {
	emscripten::function("simplex_solver", &simplex_solver);
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
			cout << "(1) simplex_solver(_nompi) [-f] [inputfile]" << endl;
			cout << "(2) simplex_solver(_nompi) [json object]" << endl;
		}
		return -1;
	}

	string input;
	bool isclear = false;
	double memlim = -1;

	for(int j = 1; j < argc; j++){
		string argstr = string(argv[j]);
		if(argstr == "-clear"){
			isclear = true;
		}
	}

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
		LoadFile(rank, mpiprocesses, argv[2], input, nullptr);
		if(rank == 0 && isclear){
			remove(argv[2]);
		}
	}
	int nthreads = 1;
	if(argc >= 5 && string(argv[3]) == "-t"){
		nthreads = atoi(argv[4]);
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
			for(const auto &p : obj){
				inobjs.push_back(p.second.get<picojson::object>());
				datanames.push_back(p.first);
			}
		}
	}
	else{
		inobjs.push_back(v.get<picojson::object>());
		datanames.push_back(argv[2]);
	}

	for(int n = 0; n < inobjs.size(); n++){
		if(RunProcess(inobjs[n], datanames[n], rank, mpiprocesses, nthreads, memlim) < 0){
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