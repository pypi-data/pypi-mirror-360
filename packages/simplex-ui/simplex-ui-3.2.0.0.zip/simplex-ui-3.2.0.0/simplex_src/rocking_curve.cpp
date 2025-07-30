#include  "rocking_curve.h"
#include "fast_fourier_transform.h"
#include "numerical_common_definitions.h"
#include "common.h"
#include "simplex_input.h"

RockingCurve::RockingCurve(vector<double> &prm)
//double lambda, double bragangledeg, double thickness, double cellvolume_nm3, double Fg)
{
	m_lambda = wave_length(prm[monoenergy_]);
	double lambdanm = m_lambda*1.0e+9;
	double eradnm = ERadius*1.0e+9;

	m_thetab = asin(fabs(lambdanm/2.0/prm[latticespace_]));
	m_chig= -prm[formfactor_]/PI*eradnm*lambdanm*lambdanm/prm[unitvol_];
	m_Lambda = m_lambda*cos(m_thetab)/fabs(m_chig);
	m_eta = PI*(prm[xtalthickness_]*1e-3)/m_Lambda/tan(m_thetab); // mm -> m
}

void RockingCurve::GetBandWidth(double *fullwidth, double *oscper)
{
	*fullwidth = fabs(m_chig)/2.0/sin(m_thetab)/sin(m_thetab);
	*oscper = (*fullwidth)/(m_eta/PI2);
}

bool RockingCurve::GetAmplitudeAsRelLambda(double dl_lambda, double *W, double *Ew, bool isreflect)
{
	*W = -2.0*sin(m_thetab)*sin(m_thetab)*dl_lambda/fabs(m_chig);
	return GetComplexAmplitude(*W, Ew, isreflect);
}

bool RockingCurve::GetAmplitudeAsTheta(double theta, double *W, double *Ew, bool isreflect)
{
	*W = sin(2.0*m_thetab)*theta/fabs(m_chig);
	return GetComplexAmplitude(*W, Ew, isreflect);
}

bool RockingCurve::GetComplexAmplitude(double W, double *Ew, bool isreflect)
{
	if(isreflect){
		Ew[1] = 0;
		if(W < -1.0){
			Ew[0] = -W-sqrt(W*W-1.0);
		}
		else if(W > 1.0){
			Ew[0] = -W+sqrt(W*W-1.0);
		}
		else{
			Ew[0] = -W;
			Ew[1] = sqrt(1.0-W*W);
		}
		return true;
	}

	complex<double> Enum, Eden, Eamp, arg;
	complex<double> rho, w(W, 0.0), i(0.0, 1.0);

	rho = f_GetRow(W);

	Enum = exp(-i*m_eta*w)*(rho-1.0);
	arg = i*m_eta*sqrt(w*w-1.0);
	Eden = rho*exp(arg)-exp(-arg);

	if(abs(Eden) == 0.0){
		return false;
	}
	Eamp = Enum/Eden;

	Ew[0] = Eamp.real();
	Ew[1] = Eamp.imag();

	return true;
}

double RockingCurve::GetCoefRealTime2Tau()
{
	double coef = PI*fabs(m_chig)*CC/(sin(m_thetab)*sin(m_thetab)*m_lambda);
	return coef;
}

// private functions
complex<double> RockingCurve::f_GetRow(double W)
{
	complex<double> rho, w(W, 0.0);
	rho = w-sqrt(w*w-1.0);
	rho *= rho;
	return rho;
}
