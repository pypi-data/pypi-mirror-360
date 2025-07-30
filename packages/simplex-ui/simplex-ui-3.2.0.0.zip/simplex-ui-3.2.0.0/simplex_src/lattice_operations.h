#ifndef lattice_operations_h
#define lattice_operations_h

#include "simplex_solver.h"
#include "optimization.h"

class LatticeOperation : public SimplexSolver, public SearchMinimum
{
public:
    LatticeOperation(SimplexSolver &sxsolver);
    void Initialize();
    void PreOperation(double lmatch, double *betap, double *alphap, double *betac, double *alphac,
        double *CS, double *SS, double *CSd, double *SSd, double *DS, double *DSd);

    void SetBPMError();
    void AllocateComponentNumbers(double s1, double s2, int *comps, int *stcomp);

    void CSD_Functions(int iseg, double s,
        double CS[], double CSd[], double SS[], double SSd[], double DS[], double DSd[]);
    void TwissTransferMatrix(double s1, double s2, vector<vector<vector<double>>> &Mxy);
    void MultiplyComponent(int iseg, double ds, vector<vector<vector<double>>> &Mxy);
    void MultiplyComponentCSD(int iseg, double ds, vector<vector<vector<double>>> &Mxy);
    void ComputeCSSS_Direct(double s1, double s2,
        double *CS, double *SS, double *CSd, double *SSd, double *DS, double *DSd);
    void GetTwissParametersAt(int n, double *beta, double *alpha);
    void TwissParametersAlongz(vector<vector<double>> *betaarr, double *avbetaxy, bool periodic = false);
    void GetFocusingSystem(vector<double> &zarr, vector<vector<double>> &kxy);
    void TwissParametersFrom(
        double s0, vector<vector<double>> &twiss0, double s, vector<vector<double>> &twiss);
    bool AdjustInitialCondition(double beta0[], double alpha0[]);
    bool OptimizeGradient(double betatgt[], double qgradient[], double beta0[], double alpha0[]);
    virtual double CostFunc(double x, vector<double> *y);
    void Move(int n, double xy0[], int icd, double xy[]);
    void GetCSDElements(vector<int> &steps, float *CSD);
    void GetDispersionArray(vector<vector<double>> &xy, int icd = 0);

private:
    void f_SetQStrength(double gradient[]);

    double m_betaini[2];
    double m_alphaini[2];
    double m_qgradient[2];

    int m_ncomp;
    int m_ntcomp;
    vector<double> m_length;
    vector<double> m_position;
    double m_qtypical;

    vector<double> m_stBxy[2];
    vector<double> m_stlength;
    vector<double> m_stposition;
    double m_stT2rad;

    int m_nseg;
    vector<double> m_zc;
    vector<double> m_kfoc[2];
    vector<double> m_rhoinv[2];

    vector<vector<double>> m_Bpeak[2]; // undulator peak field for each lattice segment
    vector<vector<int>> m_nq; // Q magnet order for each lattice segment

    vector<vector<vector<vector<double>>>> m_CSD;
    double m_xyinj[2];
    double m_xydinj[2];

    bool m_optratio;
    double m_qopt[2];
    double m_opttarget[2];
    double m_orgcost[2];
};

#endif
