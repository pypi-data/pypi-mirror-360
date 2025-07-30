#ifndef function_statistics_h
#define function_statistics_h

#include <vector>
using namespace std;

class FunctionStatistics
{
public:
	FunctionStatistics(){}
    FunctionStatistics(int ndata, vector<double> *x, vector<double> *y);
    void AssignFunction(int ndata, vector<double> *x, vector<double> *y);
    void GetStatistics(double *area, double *mean, double *peak, 
        double *std, double *stdpk, double cutpk, bool splon = true);
private:
    vector<double> m_x;
    vector<double> m_y;
    double m_xpeak;
    double m_ypeak;
    int m_size;
};

#endif
