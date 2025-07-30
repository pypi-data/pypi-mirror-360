#ifndef rocking_curve_h
#define rocking_curve_h

#include <complex>
#include <vector>
#include <vector>

using namespace std;

class RockingCurve
{
public:
	RockingCurve(vector<double> &prm);
	void GetBandWidth(double *fullwidth, double *oscper);
	bool GetComplexAmplitude(double W, double *Ew, bool isreflect);
	bool GetAmplitudeAsRelLambda(double dl_lambda, double *W, double *Ew, bool isreflect);
	bool GetAmplitudeAsTheta(double theta, double *W, double *Ew, bool isreflect);
	double GetCoefRealTime2Tau();
private:
	complex<double> f_GetRow(double W);
	double m_thetab;
	double m_lambda;
	double m_Lambda;
	double m_eta;
	double m_chig;
};

#endif
