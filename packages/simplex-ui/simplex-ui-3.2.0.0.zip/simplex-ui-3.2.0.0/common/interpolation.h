#ifndef interpolation_h
#define interpolation_h

#include <vector>
#include "common.h"
#include "numerical_common_definitions.h"

using namespace std;

class SplineBase {
public:
	int GetIndexXcoord(double x);
	double GetXYItem(int index, bool isx = true);
	double GetIniXY(bool isx = true);
	double GetFinXY(bool isx = true);

protected:
	vector<double> m_x;
	vector<double> m_y;
	int m_size;
	bool m_isreg;
};

// Spline interpolation
class Spline 
	: public SplineBase
{
public:
	void SetSpline(
		int nstep, vector<double> *x, vector<double> *y,
		bool isreg = false, bool islog = false, bool issort = false,
		double *y2ini = nullptr, double *y2fin = nullptr);
	void Initialize(int nstep, vector<double> *x, vector<double> *y, 
		bool isreg = false, bool islog = false, bool issort = false);

	double GetValue(double x, bool istrunc = false, int *ix = nullptr, double *truncval = nullptr);
	double GetLinear(double x, int index = -1);
	double GetOptValue(double x, bool istrunc = false);
	double Integrate(vector<double> *yint = nullptr, double Iini = 0.0);
	double Average();
	void AllocateGderiv();
	void IntegrateGtEiwt(double w,
		double *Gr, double *Gi, const char *debug = nullptr);
	int IntegrateGtEiwtStep(int nini, double x[], double w,
		double *Gr, double *Gi);
	int IntegrateGtEiwt(int nini, double x[], double w,
		double *Gr, double *Gi, const char *debug = nullptr);
	void IntegrateGtEiwtSingle(
		double w, double xini, double dx, vector<double> &gderiv, double *Gr, double *Gi);
	double GetDerivative(int index);
	double GetDerivativeAt(double x);
	bool GetPeakValue(int index, double *xp, double *yp, bool ismaxonly = false);
	int GetPointsInRegion(double xini, double xfin);
	void GetArrays(vector<double> *x, vector<double> *y);
	void GetAveraged(double xrange[], int mesh, vector<double> *yav);
	double Integrate(double xranger[]);

private:
	bool m_islog;
	bool m_isderivalloc;
	bool m_spl_on;
	vector<double> m_y2;
	vector<double> m_ws;

	vector<double> m_dx;
	vector<double> m_xborder;
	vector<vector<double>> m_gderiv;
};

class MonotoneSpline
	: public SplineBase
{
public:
	bool Initialize(vector<double> *x, vector<double> *y, bool isreg, int ndata = -1);
	double GetValue(double x);

private:
	vector<double> m_yp;
	vector<double> m_a;
	vector<double> m_b;
};

class Spline2D {
public:
	void SetSpline2D(int *nstep,
		vector<double> *x, vector<double> *y, vector<vector<double>> *z, 
		bool islog = false);
	double GetValue(double *xy, bool istrunc = false);
	double GetLinear(double *xy);
	double Integrate(const char *debug = nullptr);
private:
	vector<Spline> m_splines;
	Spline m_spltmp;
	vector<double> m_ztmp;
	vector<double> m_x;
	int m_xmesh;
	bool m_islog;
};


#endif

