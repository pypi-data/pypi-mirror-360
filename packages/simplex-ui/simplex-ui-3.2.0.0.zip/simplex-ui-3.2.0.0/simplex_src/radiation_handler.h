#ifndef radiation_handler_h
#define radiation_handler_h

#include "simplex_solver.h"
#include "fast_fourier_transform.h"
#include "wigner_function_disc.h"
#include "randomutil.h"

class ParticleHandler;

class RadiationHandler : public SimplexSolver
{
public:
	RadiationHandler(SimplexSolver &sxsolver, PrintCalculationStatus *status);
	~RadiationHandler();
	void AdvanceField(int n, double q2E, double ptotal, vector<vector<vector<vector<double>>>> F[]);
	void SaveResults(int n, ParticleHandler *particle, vector<vector<vector<vector<double>>>> F[]);
	void SetNearField(int n, int j = 2);
	void SetSeedField(int n);
	void SetBunchFactor(int n, ParticleHandler *particle);
	void AdvanceParticle(int n, ParticleHandler *particle, vector<vector<vector<vector<double>>>> F[]);
	void AdvanceChicane(int nstep, ParticleHandler *particle, PrintCalculationStatus *status);
	void GetGainCurves(vector<vector<double>> &pulseE,
		vector<vector<double>> &Pdn, vector<vector<double>> &Pdf, vector<vector<double>> &bf);
	void GetZProfiles(vector<double> &zprof);
	void GetTemporal(vector<vector<vector<double>>> &Pinst);
	void GetSpectrum(vector<double> &ep, vector<vector<vector<double>>> &Flux);
	void GetSpatialProfile(int jnf, vector<vector<double>> &xy, vector<vector<vector<double>>> &Pd);
	void GetCurvature(vector<vector<double>> &curvature);
	void GetBFSize(vector<vector<double>> &kappa){kappa = m_gkappa;}
	void SetFieldAt(int mp, 
		int n, int nh, int ns, int nx, int ny, vector<vector<double>> *Efp);
	double GetMaxNearField();

	void DoPostProcess(PrintCalculationStatus *status,
		vector<string> &titles, vector<string> &units, int *variables,
		vector<vector<double>> &vararray, vector<vector<vector<double>>> &data);

private:
	int f_GetSliceOffset(int n);
	void f_CyclicShift(int n);
	void f_LoadSimplexOutput(int nhtgt, PrintCalculationStatus *status);
	void f_SetChirpPulse(int iseed);
	void f_PrepareExternalSeed();
	void f_PrepareExternalSeedSpl();
	void f_AdvanceDrift(double L);
	void f_SetPhase(double L, vector<vector<vector<double>>> *phase);
	void f_SetSeedField(int n);
	void f_WriteData(int n);
	void f_ReadData(int expstep);
	void f_BcastField(int nh, int j);
	void f_GetSR(int n, int nh, vector<vector<vector<vector<double>>>> F[]);
	void f_GetTemporal(int n, int nh, int curridx);
	void f_GetSpectrum(int n, int nh, int j, int curridx);
	double f_GetPeakDens(double kL, int n, int nh, int *srange, string dfilename = "");
	double f_GetFocalIntensity(int n, int nh, int *srange = nullptr);
	void f_GetSeedProf(int n, double seedp[]);
	void f_GetWignerSpatial(int n, int nh, 
		PrintCalculationStatus *status, int *nrange = nullptr, int *srange = nullptr);
	void f_GetWignerTemporal(int jnf, int n, int nh, 
		PrintCalculationStatus *status, int *nrange = nullptr, int *sranger = nullptr, int avgslices = 0, int *erange = nullptr);
	void f_GetSpatialProfile(int n, int nh, int jnf, int curridx, int *nrange = nullptr, int *srange = nullptr);
	void f_ExportField(bool isbunch, bool isnear, int type, int ns, int nh, string dataname);
	void f_ExportFieldTemp(int n, bool isbunch, int type, int nh, string dataname);
	void f_ExportGxyGrid(int nh, vector<int> secrange[], string dataname);
	void f_ExportGxyFldGrowth(int n, int nh, vector<int> secrange[], string dataname);
	void f_GetNearFieldGauss(int np, int nh, int ns, int ixy, double *Eri);
	void f_SetSecRange(int n, int nh, vector<int> secrange[]);

	FastFourierTransform *m_fft;

	// members for Gaussian mode
	void f_InitGaussianMode();
	vector<vector<int>> m_assigned;
	vector<vector<vector<double>>> m_GnAvg;
	vector<double> m_Gxy[2];
	vector<double> m_bfg[2];
	vector<double> m_pcoef[2];
	vector<double> m_pampl[2];
	vector<double> m_paeven[4];
	double m_pampl_seed[2];
	double m_sigh2seed;
	vector<vector<double>> m_gkappa;
	vector<vector<double>> m_bfsize[2];
	vector<double> m_gn[2];
	vector<vector<double *>> m_eorg[2];
	vector<vector<double *>> m_etgt[2];
	double *m_ewsbuf;
	vector<vector<double>> m_Gf[3];
	vector<int> m_mini;
	vector<int> m_Esec;
	vector<vector<double>> m_Eaxis[2];
	vector<vector<double>> **m_Efp;

	vector<vector<double *>> m_ws[2];
	vector<vector<vector<double **>>> m_E[2];
	vector<vector<double>> m_Eseed;
	vector<double> m_E0s[2];
	vector<double> m_e0s[2];
	vector<vector<vector<double>>> m_uphase;
	vector<vector<vector<double>>> m_dphase;
	vector<double *> m_wsbf; // work space for bunch factor
	vector<vector<double **>> m_B;

	vector<vector<double *>> m_BG; 
	// bunch factors for Gaussian: 0=shotnoise, 1=total, 2=LG0th, 3=LG1st
	double *m_wsbg; // work space for m_BG

	vector<double> m_bfphase; // initial phase of the bunch factor for shotnoise

	// spontaneous radiation
	vector<vector<double>> m_Psr[2]; // temporal profile, 0 = total, 1 = current step
	vector<vector<double>> m_psr[2]; // angular & spatial profiles
	vector<vector<vector<double>>> m_fsr[2]; // spectral complex amplitude
	vector<vector<double>> m_Fsr; // spectral flux
	double m_electrons;

	double m_z0; // Rayleigh length
	double m_Zw; // Waist position

	double m_f2n;
	vector<double> m_E2pd[2];
	vector<double> m_E2P[2];
	vector<double> m_E2f[2];

	vector<vector<vector<double>>> m_Pinst;
	vector<vector<double>> m_Pax[2];
	int m_nsorg;

	vector<double> m_zprof;
	vector<double> m_ep;
	vector<vector<double>> m_curvature;
	vector<vector<vector<double>>> m_Pexprt;
	vector<vector<vector<double>>> m_Flux;
	vector<vector<vector<double>>> m_Pd[2];
	double *m_wspd[2];

	vector<fstream> m_iofs;
	float *m_wsexport;
	int m_ndata;
	int m_ngrids;
	size_t m_nexport;
	int *m_wsonslices;

	vector<vector<double>> m_Epp[4];
	bool m_ispppower;
	bool m_isppflux;
	bool m_isppamp;
	bool m_iswignerX;
	bool m_iswignerY;
	bool m_iswignerT;
	bool m_iswigner;
	WignerFunctionDiscrete m_wigner;
	vector<vector<double>> m_W;
	vector<double> m_Wtmp[2];
	double *m_wsW;
	double m_deltaW;

	FastFourierTransform *m_tfft;
	double *m_wssp[2]; // work space for spectral calculation
	int m_nfftsp;

	// rank administrating the field data for each slice
	vector<int> m_rank_admin;

	vector<double> m_schirp;
	Spline m_echirp[2];

};

extern int ExportSlice;

#endif
