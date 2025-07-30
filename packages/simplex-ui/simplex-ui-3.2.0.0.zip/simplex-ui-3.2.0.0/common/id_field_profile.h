#ifndef id_field_profile_h
#define id_field_profile_h

#include "interpolation.h"
#include "data_container.h"

enum{
    UndFDataZIdx = 0,
    UndFDataByIdx,
    UndFDataBxIdx,
    UndFDataBetaXIdx,
    UndFDataBetaYIdx,
    UndFDataXIdx,
    UndFDataYIdx,
    UndFDataRzxIdx,
    UndFDataRzyIdx,
    NumberUndFData,

	UErrorXerrorIdx = 0, // do not change order
	UErrorYerrorIdx,
	UErrorPhaseIdx,
    UErrorBdevIdx,
    UErrorPeakPosIdx,
	NumberUError
};


class IDFieldProfile
{
public:
    IDFieldProfile(int rank);
    void AllocateIntegral(DataContainer *data, bool isnormalize, int *columns = nullptr, bool isxavg = true);
    void CalculateIntegral(bool isnormalize = true, bool isxyavg = true);

    void SearchPeak(double eps, int ixy = 1);

    void GetAdjustConditions(DataContainer *data,
        vector<double> *bx, vector<double> *by, double *I1offset, double *I2offset);
    void AdjustKValue(double Kcomp);

    void GetFieldIntegralArray(vector<double> &z, vector<vector<double>> &item);
    void GetFieldIntegral(double z,
        double *acc, double *betaxy, double *xy, double *xyint, double *rzxy);
	void SetFieldIntegralArray(int ndata, vector<vector<double>> *item);

    void GetKValuesData(double *kxy);
    void GetUndulatorParametersPeriodic(vector<double> &Kxy, double *lu);
    double GetFieldSqIntegral(DataContainer *data, int jxy = 0);

    void GetErrorContents(
        int endpoles[], double *sigma, vector<vector<double>> *items = nullptr, int *ixyp = nullptr, bool isslpcorr = true);
    void ReAllocateIntegral(vector<double> *z,
        vector<vector<double>> *acc, bool isnormalize, double zbxy, bool isxyavg = true);

    bool IsAllocated();

	void SetBThreshold(double thresho){m_bthresho = thresho;}
	double GetBThreshold(){return m_bthresho;}
	double GetKadjFrac(){return m_kradj;}
	double GetUndulatorPeriod(){return m_undperiod;}
	double GetUndulatorK2(){return m_KxySq*0.5;}
    double GetEntrance(){return m_z[0]; }

	vector<double> GetBPeak(int jxy){return m_bpeak[jxy];}
    double GetZorigin(){return m_zorigin[m_mainixy];}

protected:
    void f_GetErrorContents(
		int ixy, int *prange, double ksq, double *sigma, bool slopecorr = true);
    double f_GetUndulatorPeriod(int *prange, int ixy);
    void f_ExportData(string dataname);

    vector<double> m_z;
    Spline m_acc[2];
    Spline m_accsq;
    Spline m_beta[2];
    Spline m_xy[2];
    Spline m_xyint[2];
    Spline m_rzxy[2];

    vector<double> m_zpeak[2];
    vector<double> m_bpeak[2];
	vector<double> m_zpeaktrj[2];
	
    vector<double> m_betaxypole[2];
    vector<double> m_xypole[2];
    vector<double> m_rzpole;
	vector<double> m_wspnum;

    double m_zorigin[2];
	double m_kradj;

    int m_ndata;
    int m_prange[2];

    bool m_isallocated;
    bool m_ispkallocated[2];
	double m_bpkmin;
	bool m_isphaseavg;
    int m_mainixy;

	double m_bthresho;
	double m_undperiod;
	double m_KxySq;
};

enum {
    PeakTypeAny = 0,
    PeakTypePositive,
    PeakTypeNegative
};

#endif

