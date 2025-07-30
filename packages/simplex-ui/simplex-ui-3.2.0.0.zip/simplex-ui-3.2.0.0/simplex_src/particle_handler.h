#ifndef particle_handler_h
#define particle_handler_h

#include "simplex_solver.h"
#include "randomutil.h"

class LatticeOperation;
class RadiationHandler;

class ParticleHandler : public SimplexSolver
{
public:
	ParticleHandler(SimplexSolver &sxsolver, LatticeOperation *lattice, PrintCalculationStatus *status);
	ParticleHandler(SimplexSolver &sxsolver);
	~ParticleHandler();
	void SetCustomParticles(vector<vector<double>> &particles);
	void SetIndex(int n);
	void GetBunchFactor(vector<vector<double **>> &B);
	void GetSliceBunchFactor(int n,
		vector<vector<double *>> &BG, vector<double> bfg[], double bmsize[]);
	void GetRadFieldAt(int np, int nh, int mp, double *Eri);

	void AdvanceParticle(int n,
		vector<vector<vector<vector<double>>>> F[],
		vector<vector<vector<double **>>> E[],
		RadiationHandler *radfld);
	void AdvanceChicane(int n);
	double GetTotalBunchFactor(int nh);
	void GetParameters(double *q2E, double *ptotal);
	void GetEnergyStats(vector<double> &Eloss, vector<double> &Espread);
	size_t GetBeamlets(){return m_ntotal;}
	int GetParticles(){return m_ntE;}
	double GetCharge(){return m_charge;}
	
	void GetParticlesEt(vector<vector<double>> &tE);
	void DoPostProcess(PrintCalculationStatus *status,
		vector<string> &titles, vector<string> &units, int *variables,
		vector<vector<double>> &vararray, vector<vector<vector<double>>> &data);

	void ExportKValueTrend(vector<string> &categs, vector<string> &results);

private:
	int f_GetSliceOffset(int n);
	void f_ArrangeMemory(bool alloc);
	void f_XYEtSimplex();
	void f_XYEtCustom(bool qonly = false);
	void f_SetEt(bool qonly = false);
	void f_SetEtCommon();
	void f_SetSrange();
	void f_SetXYGaussian();
	void f_AddShotnoize();
	void f_WriteXY();
	void f_ExportData(int n);
	void f_ReadXY(fstream *iofile);
	void f_ReadEt(fstream *iofile, int expstep);
	void f_ArrangeEt();
	void f_ExportXY(string dataname);
	void f_ExportEt(string dataname);
	void f_AdjustTaper(int n);

	LatticeOperation *m_lattice;
	RandomUtility m_rand;

	size_t m_ntotal;
	size_t m_nproc;
	int m_ntE;
	double m_betaxyw[2];
	double m_llxy[2];
	double m_charge;
	double m_e2loss;

	double **m_xy;
	double **m_tE;
	vector<vector<double>> m_custom;
	vector<int> m_index[3];
	vector<double> m_ws[2];
	vector<double> m_dsq;
	vector<double> m_Eloss;
	vector<double> m_Esq;
	double m_Einit;

	vector<double> m_wakefield;
	vector<double> m_Ktaper;
	vector<double> m_detune;

	int m_tgtslice;
	bool m_taperopt;

	fstream m_iofile;
	float *m_wsproc;
	float *m_wsexport;
	bool m_openfile;

	// for Gaussian mode
	vector<double> m_frac[2];
	vector<double> m_xyat[2];

	// for simplified calculation
	vector<double> m_esmpl[2];
	vector<double> m_ssmpl;
	Spline m_espl[2];
	vector<vector<double>> m_Efp[2];
};

#endif
