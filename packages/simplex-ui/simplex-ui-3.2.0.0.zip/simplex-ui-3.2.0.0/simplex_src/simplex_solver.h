#ifndef simplex_solver_h
#define simplex_solver_h

#include <chrono>
#include "simplex_config.h"
#include "print_calculation_status.h"
#include "quadrature.h"
#include "mpi_by_thread.h"

class RandomUtility;
class LatticeOperation;
class UndulatorFieldData;
class RadiationHandler;
class ParticleHandler;

extern vector<int> ExportSteps;

class SimplexSolver : public SimplexConfig
{
public:
	SimplexSolver(SimplexConfig &spconf, int thid = 0, MPIbyThread *thread = nullptr);
	void DeletePointers();
	void SetUndulatorData(UndulatorFieldData *ufdata, int nseg, int *type);
	void MeausreTime(chrono::system_clock::time_point current[], double time[], int n);
	void RunPreProcessor(vector<string> &categs, vector<string> &results);
	void RunPreProcessorMB(vector<string> &categs, vector<string> &results);
	void RunSingle(vector<string> &categs, vector<string> &results);
	void PostProcess(vector<string> &categs, vector<string> &results);

protected:
	double f_GetSaturationPower(double beta, double emitt, double *Lg3d = nullptr);
	void f_OptimizeBeta();
	void f_InitGaussian();
	void f_InitBoxcar();
	void f_InitCustomCurr();
	void f_InitCustomEt();
	void f_InitCommon();
	void f_InitCustomSlice();
	void f_InitCustomParticle();
	void f_InitSimplexOutput();
	double f_GetWakefield(vector<double> *wakefield = nullptr);
	void f_ArrangePostProcessing(
		vector<double> &zarr, vector<double> &sarr, vector<vector<double>> &xyarr,
		int steprange[], int slicerange[], int nrange[]);
	void f_InitGrid();
	void f_SetCouplingFactor(PrintCalculationStatus *status, LatticeOperation *lattice);
	double f_GetNetMagnetLength(double z, bool trunc);
	void f_GetK4Eta(double eta, double *Kbase, double *detune);
	void f_GetKVaried(double z, double *detune, double *K, double wf = 0);
	void f_ArrangeDetuning(vector<double> &detune);
	void f_ExportSingle(int dimension, vector<string> &titles, vector<string> &units,
		vector<vector<double>> &vararray, vector<vector<vector<double>>> &data, vector<string> &results, string options = "");
	bool f_IsExportDebug(int n, int rank = 0);

	double m_pkcurr;
	double m_eGeV;
	double m_gamma;
	double m_emitt[2];
	double m_betaav[2];
	double m_betaopt;
	double m_espread;
	double m_Lg3d;
	double m_uA[2];
	double m_uB[2];
	vector<vector<double>> m_ptmp;

	double m_lu;
	double m_K;
	double m_Kphi;
	double m_lambda1;
	double m_lambda_s;
	double m_lslice;
	double m_dTslice;
	int m_N; // number of periods
	int m_M; // number of segments
	vector<double> m_Kxy[2];
	vector<double> m_deltaxy[2];

	int m_nhmax;
	int m_slices;
	int m_slices_total;
	int m_intstep;
	int m_driftsteps;
	int m_totalsteps;
	int m_segsteps;
	double m_zstep;
	double m_zstep_drift;

	bool m_isGauss;
	bool m_isGaussDebug;
	bool m_skipwave;
	vector<double> m_sizexy[2];

	// SIMPLEX Output objects
	vector<int> m_simexpsteps;
	int m_simbeamlets;
	int m_simparticles;
	int m_simnfft[2];
	double m_simdxy[2];
	double m_simcharge;
	double m_simlambda1;
	double m_slippage;
	vector<double> m_simspos;
	SimplexConfig m_sxconf;

	vector<double> m_z;
	vector<bool> m_inund;
	vector<double> m_detune_err;
	vector<int> m_chicane;
	vector<bool> m_zexport;
	vector<int> m_segend;
	vector<double> m_s;
	vector<int> m_steprange[2];
	vector<int> m_segideal;
	vector<int> m_segerr;
	vector<int> m_segdata;
	vector<vector<double>> m_bf;
	map<int, DataContainer *> m_udata;

	vector<double> m_Ktaper;
	vector<double> m_Koffset;
	vector<double> m_deta4K;
	vector<int> m_exporsteps;
	vector<double> m_exportz;
	int m_nhpp;

	bool m_exseed;
	int m_np; // 1: linear or circular, 2 elliptical
	int m_nfft[2];
	double m_dxy[2];
	double m_Dxy[2];
	double m_qxy[2];
	double m_dkxy[2];
	double m_sigmar; // seed source size

	int *m_sranges;
	int *m_onslices;
	int **m_srangep;
	int **m_onslicep;
	int m_exslices;

	// post-processing
	bool m_isppalongs;
	bool m_isppoxy;
	int m_oixy;
	int m_rixy;

	// modulation
	vector<vector<double>> m_tE;

	int m_BGmodes;

	MPIbyThread *m_thread;

private:
	void f_RemoveInChicane(vector<vector<double>> &vararray, vector<vector<vector<double>>> &data, int dim);
	void f_SkipStep(vector<vector<double>> &vararray, vector<vector<vector<double>>> &data, int dim);
	void f_ExportCurve(vector<string> &titles, vector<string> &units, 
		vector<vector<double>> &vararray, vector<vector<vector<double>>> &data, vector<string> &results);
	void f_ExportCharacteristics(RadiationHandler *radiation, vector<string> &categs, vector<string> &results);
	void f_ExportTemporal(RadiationHandler *radiation, vector<string> &categs, vector<string> &results, vector<vector<double>> &plen);
	void f_ExportSpectrum(RadiationHandler *radiation, vector<string> &categs, vector<string> &results, vector<vector<double>> &bw);
	void f_ExportSpatial(RadiationHandler *radiation, int jnf, vector<string> &categs, vector<string> &results, vector<vector<double>> &sxy);
	void f_ExportCoordinate(ParticleHandler *particle, vector<string> &categs, vector<string> &results);
	void f_ExportRefEt(vector<string> &categs, vector<string> &results, vector<double> &s, vector<double> &eta, double *r56 = nullptr);
	void f_ExportI(vector<double> &s, vector<double> &I, vector<string> &categs, vector<string> &results);
	void f_ExportEt(vector<double> &s, vector<double> &eta, vector<double> &j, vector<string> &categs, vector<string> &results);

	vector<vector<vector<vector<double>>>> m_F[4]; // coupling: Exreal, Eximag, ...
	vector<string> m_nhl;
};

class EtIntegrator: public QSimpson
{
public:
	void Set(double wavel, double r56, double espread, double pkcurr, double bunchlen, vector<double> &s, vector<double> &eta);
	double GetOptimumR56(double efactor);
	void GetCurrent(vector<double> &s, vector<double> &I, int acc);
	void GetParticalCurrent(vector<double> &s, vector<double> &eta, vector<double> &j);
	virtual void QSimpsonIntegrand(int layer, double eta, vector<double> *j);

private:
	Spline m_etaspl;
	double m_r56;
	double m_s;
	double m_espread;
	double m_sigmas;
	double m_pkcurr;
	double m_wavelength;
	double m_etarange[2];
	int m_particles;
};

double rho_fel_param_1D(double ipeak, double lambda_u_m, double K, double phi,
	double beta, double emitt, double gamma);
double scaling_fel3d_eta(double lambda, double L1D,
	double beta, double emitt, double lambda_u, double espread);
void rand_init(bool autoseed, int seed, int procs, int rank, RandomUtility *rand, MPIbyThread *mpithread);
void LoadFile(int rank, int mpiprocesses, const string filename, string &input, MPIbyThread *mpithread);

const string ZLabel = "z";
const string ZUnit = "m";
const string SLabel = "s";
const string SUnit = "mm";
const string XLabel = "x";
const string XYUnit = "mm";
const string YLabel = "y";
const string hQxLabel = "h&theta;<sub>x</sub>";
const string QxLabel = "&theta;<sub>x</sub>";
const string XpLabel = "x'";
const string XYpUnit = "mrad";
const string YpLabel = "y'";
const string hQyLabel = "h&theta;<sub>y</sub>";
const string QyLabel = "&theta;<sub>y</sub>";
const string BxLabel = "B<sub>x</sub>";
const string BUnit = "T";
const string ByLabel = "B<sub>y</sub>";
const string PerrLabel = "Phase Error";
const string PerrUnit = "degree";
const string KLabel = "K Value";
const string DetuneLabel = "Detuning";
const string SlippageLabel = "Slippage";
const string NoUnit = "-";
const string PhotonELabel = "Photon Energy";
const string PhotonEUnit = "eV";
const string EtaLabel = "&Delta;&gamma;/&gamma;";
const string FracLabel = "Fraction";
const string BetaUnit = "m";
const string WakeUnit = "V/m";
const string CurrLabel = "I";
const string CurrUnit = "A";
const string PartialCurrLabel = "j";
const string PartialCurrUnit = "A/100%";
const string RelEnergyLabel = "Relative Photon Energy";
const string RealLabel = "Real";
const string ImagLabel = "Imaginary";
const string IntensityLabel = "Intensity";
const string RelEnergyUnit = "eV";

const string PulseEnergyUnit = "J";
const string RadPowerUnit = "GW";
const string SpatEnergyDensUnit = "J/mm<sup>2</sup>";
const string AngEnergyDensUnit = "J/mrad<sup>2</sup>";
const string SpatPowerDensUnit = "GW/mm<sup>2</sup>";
const string AngPowerDensUnit = "GW/mrad<sup>2</sup>";
const string BunchFactorUnit = "-";
const string ELossUnit = "J";
const string PLossUnit = "GW";
const string EspreadUnit = "-";

const string RadFluxLabel = "Photon Flux";
const string RadFluxUnit = "photons/0.1%b.w.";
const string SpatFluxDensLabel = "Spatial Flux Density";
const string SpatFluxDensUnit = "photons/mm<sup>2</sup>/0.1%b.w.";
const string AngFluxDensLabel = "Angular Flux Density";
const string AngFluxDensUnit = "photons/mrad<sup>2</sup>/0.1%b.w.";

const string WigEnergyDensLabel = "Energy Density";
const string WigEnergyDensUnit = "J/mrad/mm";
const string WigPowerDensLabel = "Power Density";
const string WigPowerDensUnit = "GW/mrad/mm";
const string WigFluxLabel = "Inst. Photon Flux";
const string WigFluxUnit = "photons/s/0.1%b.w.";

const string PulselengthUnit = "mm";
const string BandwidthUnit = "-";
const string DivergenceUnit = "mrad";
const string BeamSizeUnit = "mm";
const string CurvatureUnit = "m";

const string SourceSizeX = "RMS Source Size (x)";
const string SourceSizeY = "RMS Source Size (y)";
const string SourceSizeUnit = "mm";

const string StokesS1Label = "S<sub>1</sub>";
const string StokesS2Label = "S<sub>2</sub>";
const string StokesS3Label = "S<sub>3</sub>";
const string ERealLabel = "Real Part";
const string EImagLabel = "Imaginary Part";
const string ExRealLabel = "E<sub>x</sub> Real Part";
const string ExImagLabel = "E<sub>x</sub> Imaginary Part";
const string EyRealLabel = "E<sub>y</sub> Real Part";
const string EyImagLabel = "E<sub>y</sub> Imaginary Part";
const string ExyUnit = "V/m";
const string ExyFarUnit = "V";

const string BRealLabel = "Bunch Factor Real Part";
const string BImagLabel = "Bunch Factor Imaginary Part";

const string SliceElossLabel = "Normalized Energy";
const string SliceEsprdabel = "Energy Spread";
const string SliceEUnit = "-";

const int SPATIALMESH = 16;
const double KICKTHRESHOLD = 0.1;

//-------->>>>>>
//#define _CPUTIME
#undef _DEBUGINF

#endif
