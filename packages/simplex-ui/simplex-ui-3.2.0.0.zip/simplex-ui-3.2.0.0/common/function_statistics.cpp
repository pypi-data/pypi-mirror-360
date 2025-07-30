#include "function_statistics.h"
#include "interpolation.h"

FunctionStatistics::FunctionStatistics(int ndata, vector<double> *x, vector<double> *y)
{
    AssignFunction(ndata, x, y);
}

void FunctionStatistics::AssignFunction(int ndata, vector<double> *x, vector<double> *y)
{
    m_size = ndata;
    m_x.resize(m_size);
    m_y.resize(m_size);

    m_ypeak = 0;

    for(int n = 0; n < m_size; n++){
        m_x[n] = (*x)[n];
        m_y[n] = (*y)[n];
        if(fabs(m_y[n]) > m_ypeak){
            m_ypeak = fabs(m_y[n]);
            m_xpeak = m_x[n];
        }
    }
}

void FunctionStatistics::GetStatistics(
    double *area, double *mean, double *peak, double *std, double *stdpk, double cutpk, bool splon)
{
    Spline spl;
    vector<double> y1(m_size);

    for(int n = 0; n < m_size; n++){
        y1[n] = m_x[n]*m_y[n];
    }
    *peak = m_xpeak;

    if(splon){
        spl.SetSpline(m_size, &m_x, &m_y, false, false, true);
    }
    else{
        spl.Initialize(m_size, &m_x, &m_y, false, false, true);
    }
    *area = spl.Integrate();
    if(*area == 0){
        *mean = *std = *stdpk = 0;
        return;
    }

    if(splon){
        spl.SetSpline(m_size, &m_x, &y1, false, false, true);
    }
    else{
        spl.Initialize(m_size, &m_x, &y1, false, false, true);
    }
    *mean = spl.Integrate()/(*area);

    for(int n = 0; n < m_size; n++){
        if(fabs(m_y[n]) > m_ypeak*cutpk){
            y1[n] = (m_x[n]-*mean)*(m_x[n]-*mean)*fabs(m_y[n]);
        }
        else{
            y1[n] = 0;
        }
    }
    if(splon){
        spl.SetSpline(m_size, &m_x, &y1, false, false, true);
    }
    else{
        spl.Initialize(m_size, &m_x, &y1, false, false, true);
    }
    *std = sqrt(spl.Integrate()/(*area));

    for(int n = 0; n < m_size; n++){
        if(fabs(m_y[n]) > m_ypeak*cutpk){
            y1[n] = (m_x[n]-*peak)*(m_x[n]-*peak)*fabs(m_y[n]);
        }
        else{
            y1[n] = 0;
        }
    }
    if(splon){
        spl.SetSpline(m_size, &m_x, &y1, false, false, true);
    }
    else{
        spl.Initialize(m_size, &m_x, &y1, false, false, true);
    }

    *stdpk = sqrt(spl.Integrate()/(*area));
}




