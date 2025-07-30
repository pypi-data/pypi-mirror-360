#ifndef wakefield_h
#define wakefield_h

#include "simplex_solver.h"
#include "quadrature.h"
#include "interpolation.h"
#include "fast_fourier_transform.h"

#define ROUGH_WAKE_DATA_NUMBER 201

class WakefieldUtility : public SimplexSolver, public QSimpson
{
public:
    WakefieldUtility(SimplexSolver &sxsolver);
    ~WakefieldUtility();
    void QSimpsonIntegrand(int layer, double xy, vector<double> *density);
    void GetWakeFieldProfiles(vector<string> &types, 
        vector<double> &s, vector<vector<double>> &wakes);
    void GetWakeFieldProfile(int waketype, vector<double> &wakef);
    void GetEVariation(vector<double> &earr, vector<double> &rate);

private:
    void f_AdjustSrange(double dkmax, double dsmax, double *ds, int *nfft);
    void f_GetSpaceChargeImpedance(double k, double *re, double *im);
    void f_GetACResistiveImpedance(double k, double *re, double *im);
    void f_GetACResistiveImpedanceBase(
        bool iscircular, double q, double kappa, double Tau, double *re, double *im);
    void f_GetACResistiveImpedanceParallelPlate(
        double kappa, double Tau, double *re, double *im);
    double f_SurfaceRoughnessWakePotentialUnitCharge(double s);
    void f_GetSynchroImpedance(double L, double k, double *re, double *im);
    double f_CustomWakeUnitCharge(double s);
    void f_DensityAtEnergy(double s, vector<double> *density);

    FastFourierTransform *m_fft;
    Spline m_customwake;
    Spline m_wakefspl;
    Spline m_Ispl;
    Spline m_resisspl;
    vector<double> m_earr;
    vector<int> m_types;
    vector<string> m_typenames;
    double *m_Iw;

    double m_zcoef[NumWakeBool];
    double m_kappa;
    double m_tau;
    double m_sigmaebm;
    double m_s0;
    double m_Tau;
    double m_ksynchro;
    double m_gammaz;
    double m_kmax_resis;

    int m_nfft;
    double m_ds;

    bool m_enable[NumWakeBool];
    bool m_iscircular;
    bool m_evaldist;
};

#endif

