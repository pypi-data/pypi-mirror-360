#ifndef quadrature_h
#define quadrature_h

#include <vector>
#include "numerical_common_definitions.h"
#include "print_calculation_status.h"
#include "mpi_by_thread.h"

using namespace std;

class QSimpson
{
public:
	QSimpson();
	void ArrangeMPIConfig(
		int rank, int mpiprocesses, int mpipayer, MPIbyThread *thread = nullptr);
	void AllocateMemorySimpson(int nitems, int nborder, int layers);
	virtual ~QSimpson();
	virtual void QSimpsonIntegrand(int layer, double xy, vector<double> *density) = 0;
	void QSimpsonIntegrandSt(int layer, double xy, vector<double> *density);
	void IntegrateSimpson(int *layers, double a, double b, double eps,
		int jrepmin, vector<vector<double>> *finit, vector<double> *answer,
		string debug = "", bool isappend = false, bool issave = false, int jrepmax = -1);
	void SetCalcStatusPrint(PrintCalculationStatus *status);
	int GetEvaluatedValue(int layer, vector<double> *arg, 
			vector<vector<double>> *values, string debug = "");
private:
	void f_ExpandStorage(int layer, int ndata);
	void f_QTrapezoid(int *layers, double a, double b, int nrep,
		double *fmax, vector<double> &yold, vector<double> &ynew, string debug, bool isappend);
	vector<vector<double>> m_wsFunc; // Work space for integrand function
	vector<vector<double>> m_sumTrap;  // Work space for summation in QTrapezoid
	vector<vector<vector<double>>> m_yRombO; // Old Romberg integrals
	vector<vector<vector<double>>> m_yRombC; // Current Romberg integrals
	vector<vector<vector<double>>> m_fintval; // integrand values storage
	vector<vector<double>> m_fintarg; // integrand arguments storage
	vector<int> m_ndata; // number of function evaluation
	vector<bool> m_issave; // switch to save data
	PrintCalculationStatus *m_statusqsimp;
	int m_mpiprocesses;
	int m_rank;
	int m_mpilayer;
	MPIbyThread *m_qthread;

protected:
	int m_maxorder;
	int m_nitems;
	int m_nborder;
	int m_layers;
	bool m_cancelqsimp;
	vector<double> m_currmaxref;
	double *m_ws4mpi_sum[2];
	double *m_ws4mpi_max[2];
};

class QGauss
{
public:
	void InitializeQGauss(int maxorder, int nitems);
	void Resize(int maxorder);
	virtual void IntegrandGauss(double x, vector<double> *y) = 0;
	void IntegrateGauss(int npoints, double a, double
		b, vector<double> *ans, string debug = "", bool isappend = false);
private:
	void f_AllocatePoints(int n);
	void f_ExpandMaxOrder(int maxorder);
	vector<vector<double>> m_x;
	vector<vector<double>> m_w;
	vector<bool> m_isalloc;
	vector<double> m_ytmp;
	int m_maxorder;

protected:
	int m_nitems;
};

#endif

