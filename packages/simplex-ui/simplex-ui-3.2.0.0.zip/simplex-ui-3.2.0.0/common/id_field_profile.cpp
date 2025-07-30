#include <algorithm>
#include "common.h"
#include "id_field_profile.h"

//---------------------------
// IDFieldProfile
string CalculateIntegData;
string UndSpecsData;

//------------------------------------------------------------------------------
IDFieldProfile::IDFieldProfile(int rank)
{
    if(rank == 0){
#ifdef _DEBUG
        //CalculateIntegData = "..\\debug\\field_integral.dat";
        //UndSpecsData = "..\\debug\\und_specs.dat";
#endif
    }

    m_ispkallocated[0] = m_ispkallocated[1] = m_isallocated = false;
	m_bpkmin = 0;
	m_bthresho = 0.1;
	m_isphaseavg = true;
}

// allocate field integral, field data
void IDFieldProfile::AllocateIntegral(DataContainer *data, bool isnormalize, int *columns, bool isxavg)
{
    int zcol = 0, bxcol = 1, bycol = 2;
    vector<vector<double>> acc(2);

    if(columns != nullptr){
        zcol = columns[0];
        bxcol = columns[1];
        bycol = columns[2];
    }

    data->GetArray1D(zcol, &m_z);
    data->GetArray1D(bxcol, &acc[1]);
    data->GetArray1D(bycol, &acc[0]);

    m_ndata = (int)m_z.size();
    heap_sort(m_z, acc, m_ndata, true);
    ReAllocateIntegral(nullptr, &acc, isnormalize, 0.0, isxavg);
}

// actually calculate the field integral
void IDFieldProfile::CalculateIntegral(bool isnormalize, bool isxyavg)
{
    vector<double> beta[2], xy[2], xyint[2], rz, rzxy[2];
    double average;

    for(int j = 0; j < 2; j++){
        beta[j].resize(m_ndata);
        xy[j].resize(m_ndata);
        rzxy[j].resize(m_ndata);
        xyint[j].resize(m_ndata);

        m_acc[j].Integrate(&beta[j]);
        if(isnormalize){ // 1st integral -> gamma*beta, positive charge
            beta[j] *= (j==0?-1.0:1.0)*PI2*COEF_K_VALUE;
		}

        m_beta[j].SetSpline(m_ndata, &m_z, &beta[j]);
        average = m_beta[j].Average();
        beta[j] -= average;
        m_beta[j].SetSpline(m_ndata, &m_z, &beta[j]);
        m_beta[j].Integrate(&xy[j]);

        m_xy[j].SetSpline(m_ndata, &m_z, &xy[j]);
        if(isxyavg){
            average = m_xy[j].Average();
            xy[j] -= average;
        }
        m_xy[j].SetSpline(m_ndata, &m_z, &xy[j]);
        m_xy[j].Integrate(&xyint[j]);

        m_xyint[j].SetSpline(m_ndata, &m_z, &xyint[j]);

        for(int n = 0; n < m_ndata; n++){
            rzxy[j][n] = beta[j][n]*beta[j][n];
        }
        m_rzxy[j].SetSpline(m_ndata, &m_z, &rzxy[j]);
        m_rzxy[j].Integrate(&rzxy[j]);
        m_rzxy[j].SetSpline(m_ndata, &m_z, &rzxy[j]);
    }

    m_isallocated = true;

#ifdef _DEBUG
	if(!CalculateIntegData.empty()){
        f_ExportData(CalculateIntegData);
	}
#endif
}

// get initial conditions (slope and position)
void IDFieldProfile::GetAdjustConditions(DataContainer *data,
    vector<double> *bx, vector<double> *by, double *I1offset, double *I2offset)
{
    AllocateIntegral(data, false);

    vector<double> dummy;
    m_acc[0].GetArrays(&dummy, by);
    m_acc[1].GetArrays(&dummy, bx);

    for(int j = 0; j < 2; j++){
        I1offset[j] = m_beta[1-j].GetXYItem(0, false);
        I2offset[j] = m_xy[1-j].GetXYItem(0, false);
    }
}

// search magnetic field peak
void IDFieldProfile::SearchPeak(double eps, int ixy)
    // eps: accuracy for field range specification
{
    int npk, nini, nfin;
    double zpeak, bpeak, z1, z2, bsqsum = m_accsq.GetFinXY(false), blim;
    vector<double> acc, accs, dummy, trj;
	double accmax;

    m_acc[ixy].GetArrays(&dummy, &acc);
    m_acc[1-ixy].GetArrays(&dummy, &accs);
	m_xy[ixy].GetArrays(&dummy, &trj);

	accmax = max(
        max(fabs(minmax(acc, true)), fabs(minmax(acc, false))),
        max(fabs(minmax(accs, true)), fabs(minmax(accs, false)))
    );
	m_bpkmin = accmax*m_bthresho;

    blim = bsqsum*eps; nini = 0;
    while(m_accsq.GetXYItem(++nini, false) < blim && nini < m_ndata-1);

    blim = bsqsum*(1.0-eps); nfin = m_ndata-1;
    while(m_accsq.GetXYItem(--nfin, false) > blim && nfin > 0);

    z1 = m_accsq.GetXYItem(nini);
    z2 = m_accsq.GetXYItem(nfin);
	m_zorigin[ixy] = (z1+z2)*0.5;

    npk = nini+1;

    m_zpeak[ixy].clear(); m_bpeak[ixy].clear();
    while(1){
        npk = get_parabolic_peak(m_z, acc, &zpeak, &bpeak, npk, 3);
        if(zpeak > z2 || npk < 0){
            break;
        }
		if(fabs(bpeak) < m_bpkmin){
			continue;
		}
        m_zpeak[ixy].push_back(zpeak);
        m_bpeak[ixy].push_back(bpeak);
    }

	int npeaks = (int)m_zpeak[ixy].size();
	if(npeaks >= 1){
	    if(m_zpeak[ixy].size()%2 == 0){
	        m_zorigin[ixy] = 0.5*(m_zpeak[ixy][npeaks/2-1]+m_zpeak[ixy][npeaks/2]);
		}
	    else{
	        m_zorigin[ixy] = m_zpeak[ixy][(npeaks-1)/2];
		}
	}
    m_ispkallocated[ixy] = true;
}

// adjust the k value(s)
void IDFieldProfile::AdjustKValue(double Kcomp)
    // GetErrorContents should be called before to define m_prange
{
    vector<double> acc[2], vtmp;
    double kxy[2], K, kxyo = 0;

    GetKValuesData(kxy);
	K = sqrt(hypotsq(kxy[0], kxy[1]));
	m_kradj = 1.0;
	while(fabs(K/Kcomp-1.0) > 1.0e-4 && fabs(kxyo-K) > 1.0e-4){
		m_kradj *= Kcomp/K;
		for(int j = 0; j < 2; j++){
			m_acc[j].GetArrays(&m_z, &acc[j]);
	        acc[j] *= m_kradj;
		    m_acc[j].SetSpline(m_ndata, &m_z, &acc[j]);
		}
		CalculateIntegral();
		kxyo = K;
	    GetKValuesData(kxy);
        K = sqrt(hypotsq(kxy[0], kxy[1]));
	};
}

// get the field integral arrays
void IDFieldProfile::GetFieldIntegralArray(vector<double> &z, vector<vector<double>> &item)
{
    z = m_z;
    item.resize(6);
    for(int j = 0; j < 2; j++){
        m_acc[j].GetArrays(nullptr, &item[1-j]); // flip acc_x <-> acc_y
        m_beta[j].GetArrays(nullptr, &item[j+2]);
        m_xy[j].GetArrays(nullptr, &item[j+4]);
    }
}

void IDFieldProfile::GetFieldIntegral(double z,
    double *acc, double *betaxy, double *xy, double *xyint, double *rzxy)
{
    int j;

    for(j = 0; j < 2; j++){
        if(acc != nullptr){
            acc[j] = m_acc[j].GetValue(z);
        }
        if(betaxy != nullptr){
            betaxy[j] = m_beta[j].GetValue(z);
        }
        if(xy != nullptr){
            xy[j] = m_xy[j].GetValue(z);
        }
        if(xyint != nullptr){
            xyint[j] = m_xyint[j].GetValue(z);
        }
        if(rzxy != nullptr){
            rzxy[j] = m_rzxy[j].GetValue(z);
        }
    }
}

void IDFieldProfile::SetFieldIntegralArray(int ndata, vector<vector<double>> *item)
{
	m_ndata = ndata;
	m_z = (*item)[0];

	for(int j = 0; j < 2; j++){
        m_acc[j].SetSpline(ndata, &m_z, &(*item)[j+1]);
        m_beta[j].SetSpline(ndata, &m_z, &(*item)[j+3]);
        m_xy[j].SetSpline(ndata, &m_z, &(*item)[j+5]);
        m_rzxy[j].SetSpline(ndata, &m_z, &(*item)[j+7]);
    }

	vector<double> accsq;
    accsq.resize(m_ndata);
    for(int n = 0; n < m_ndata; n++){
        accsq[n] = hypotsq((*item)[1][n], (*item)[2][n]);
    }
    m_accsq.SetSpline(m_ndata, &m_z, &accsq);
    m_accsq.Integrate(&accsq);
    m_accsq.SetSpline(m_ndata, &m_z, &accsq);
}

// get the K values
void IDFieldProfile::GetKValuesData(double *kxy)
{
	for(int j = 0; j < 2; j++){
	    if(!m_ispkallocated[j]){
		    SearchPeak(1.0e-6, j);
		}
	}

    double zent = m_zpeak[m_mainixy][m_prange[0]];
    double zexit = m_zpeak[m_mainixy][m_prange[1]];

    for(int j = 0; j < 2; j++){
        kxy[j] = (m_rzxy[j].GetValue(zexit)-m_rzxy[j].GetValue(zent))/(zexit-zent);
        if(kxy[j] < INFINITESIMAL){
            kxy[j] = 0.0;
        }
        else{
            kxy[j] = sqrt(kxy[j]*2.0);
        }
    }
}

// get the period and K values
void IDFieldProfile::GetUndulatorParametersPeriodic(vector<double> &Kxy, double *lu)
{
    *lu = m_z[m_ndata-1]-m_z[0];
    for(int j = 0; j < 2; j++){
        int ji = 1-j;
        Kxy[ji] = (m_rzxy[j].GetFinXY(false)-m_rzxy[j].GetIniXY(false))/(*lu);
        if(Kxy[ji] < INFINITESIMAL){
            Kxy[ji] = 0.0;
        }
        else{
            Kxy[ji] = sqrt(Kxy[ji]*2.0);
        }
    }
}

// get integral of B^2
double IDFieldProfile::GetFieldSqIntegral(DataContainer *data, int jxy)
{
    vector<double> z, bb, acc[2];
    Spline BBspl;

    if(data == nullptr){
        return 0.0;
    }

    data->GetArray1D(0, &z);
    data->GetArray1D(1, &acc[1]);
    data->GetArray1D(2, &acc[0]);
    int nsize = (int)z.size();
    bb.resize(nsize);
    for(int n = 0; n < nsize; n++){
        if(jxy == 2){
            bb[n] = hypotsq(acc[0][n], acc[1][n]);
        }
        else{
            bb[n] = acc[jxy][n]*acc[jxy][n];
        }
    }
    BBspl.SetSpline(nsize, &z, &bb);
    return BBspl.Integrate(&bb);
}

// get phase and orbit errors
void IDFieldProfile::GetErrorContents(
    int endpoles[], double *sigma, vector<vector<double>> *items, int *ixyp, bool isslpcorr)
{
	for(int j = 0; j < 2; j++){
	    if(!m_ispkallocated[j]){
		    SearchPeak(1.0e-6, j);
		}
        if(m_zpeak[0].size() >= m_zpeak[1].size()){
            m_mainixy = m_zpeak[1].size() >= 3 ? 1 : 0;
        }
        else{
            m_mainixy = m_zpeak[0].size() >= 3 ? 0 : 1;
        }
    }

    for(int i = 0; i < NumberUError; i++){
        sigma[i] = 0.0;
    }

	if(ixyp != nullptr){
		*ixyp = m_mainixy;
	}

	if(m_zpeak[m_mainixy].size() < 2){
		if(items != nullptr){
			if(items->size() < NumberUError){
				items->resize(NumberUError, vector<double> {0.0});
			}
		}
		return;
	}

    m_prange[0] = endpoles[0];
    m_prange[1] =  (int)m_zpeak[m_mainixy].size()-1-endpoles[1];
    
    m_undperiod = f_GetUndulatorPeriod(m_prange, m_mainixy);
    double Lmag = 0.5*m_undperiod*(m_prange[1]-m_prange[0]+1);

    double kxy[2];
    GetKValuesData(kxy);
	m_KxySq = hypotsq(kxy[0], kxy[1]);
    f_GetErrorContents(m_mainixy, m_prange, m_KxySq, sigma, isslpcorr);
    if(items == nullptr){
        return;
    }
	if(items->size() < NumberUError){
		items->resize(NumberUError);
		for(int j = 0; j < NumberUError; j++){
		    (*items)[j].resize(m_prange[1]-m_prange[0]+1);
		}
	}
    for(int n = 0; n <= m_prange[1]-m_prange[0]; n++){
        (*items)[UErrorPhaseIdx][n] = m_rzpole[n];
        (*items)[UErrorXerrorIdx][n] = m_xypole[0][n];
        (*items)[UErrorYerrorIdx][n] = m_xypole[1][n];
        (*items)[UErrorPeakPosIdx][n] = m_zpeak[m_mainixy][n+m_prange[0]];
    }

#ifdef _DEBUG
	if(!UndSpecsData.empty()){
        vector<double> titems(3);
		ofstream debug_out(UndSpecsData);
        for(int n = 0; n <= m_prange[1]-m_prange[0]; n++){
            titems[0] = m_rzpole[n];
            titems[1] = m_xypole[0][n];
            titems[2] = m_xypole[1][n];
            PrintDebugItems(debug_out, (double)n, titems);
        }
	}
#endif
}

void IDFieldProfile::ReAllocateIntegral(vector<double> *z,
    vector<vector<double>> *acc, bool isnormalize, double zbxy, bool isxyavg)
{
    int j, n;
    vector<double> accsq;

    if(z != nullptr){
        *z = m_z;
    }

    for(j = 0; j < 2; j++){
        m_acc[j].SetSpline(m_ndata, &m_z, &((*acc)[j]));
    }
    if(fabs(zbxy) > INFINITESIMAL){
        for(n = 0; n < m_ndata; n++){
            double zbx = min(m_z[m_ndata-1], max(m_z[n]-zbxy, m_z[0]));
            (*acc)[1][n] = m_acc[1].GetValue(zbx);
        }
        m_acc[1].SetSpline(m_ndata, &m_z, &((*acc)[1]));
    }

    accsq.resize(m_ndata);
    for(int n = 0; n < m_ndata; n++){
        accsq[n] = hypotsq((*acc)[0][n], (*acc)[1][n]);
    }
    m_accsq.SetSpline(m_ndata, &m_z, &accsq);
    m_accsq.Integrate(&accsq);
    m_accsq.SetSpline(m_ndata, &m_z, &accsq);

    CalculateIntegral(isnormalize, isxyavg);
}

// check if the field integral is calculated
bool IDFieldProfile::IsAllocated()
{
   return m_isallocated;
}

//----- private functions -----
void IDFieldProfile::f_GetErrorContents(
	int ixy, int *prange, double ksq, double *sigma, bool slopecorr)
{
    int n, npole = prange[1]-prange[0]+1;
    double xy[2], rzxy[2], rzorg, mean[NumberUError], beta[2], acc[2];
    double lu = f_GetUndulatorPeriod(prange, ixy);

    GetFieldIntegral(m_zorigin[ixy], nullptr, nullptr, xy, nullptr, rzxy);
    rzorg = rzxy[0]+rzxy[1];
    if(m_xypole[0].size() < npole){
        m_xypole[0].resize(npole); m_xypole[1].resize(npole); 
        m_betaxypole[0].resize(npole); m_betaxypole[1].resize(npole); 
		m_rzpole.resize(npole);
		m_wspnum.resize(npole);
		for(int n = 0 ; n < npole; n++){
			m_wspnum[n] = (double)n;
		}
    }
    for(n = 0; n < npole; n++){
		GetFieldIntegral(m_zpeak[ixy][n+prange[0]], acc, beta, xy, nullptr, rzxy);
        for(int j = 0; j < 2; j++){
            m_xypole[j][n] = xy[j];
            m_betaxypole[j][n] = beta[j];
        }
        m_rzpole[n] = rzxy[0]+rzxy[1]-rzorg;
    }
	if(prange[0] == 0){
		double dz = m_zpeak[ixy][1]-m_zpeak[ixy][0];
        for(int j = 0; j < 2; j++){
            xy[j] = m_xypole[j][0];
            beta[j] = m_betaxypole[j][0];
            xy[j] -= beta[j]*dz;
        }
	}
	else{
		GetFieldIntegral(m_zpeak[ixy][prange[0]-1], acc, beta, xy, nullptr, rzxy);
	}

	for(n = npole-1; n > 0; n--){
        for(int j = 0; j < 2; j++){
            m_xypole[j][n] = 0.5*(m_xypole[j][n-1]+m_xypole[j][n]);
            m_betaxypole[j][n] = 0.5*(m_betaxypole[j][n-1]+m_betaxypole[j][n]);
        }
    }
    for(int j = 0; j < 2; j++){
        m_xypole[j][0] = 0.5*(xy[j]+m_xypole[j][0]);
        m_betaxypole[j][0] = 0.5*(beta[j]+m_betaxypole[j][0]);
    }

	if(m_isphaseavg){
	    for(n = 0; n < npole; n++){
			m_rzpole[n] += m_zpeak[ixy][n+prange[0]]-m_zorigin[ixy];
			m_rzpole[n] -= n*(1.0+ksq*0.5)*lu*0.5;
		}
	}
	else{
	    for(n = 0; n < npole; n++){
			m_rzpole[n] -= (m_zpeak[ixy][n+prange[0]]-m_zorigin[ixy])*ksq*0.5;
		}
	}
	m_rzpole *= 360.0/(1.0+ksq*0.5)/lu; //  -> degree

    get_stats(m_xypole[0], npole, &mean[UErrorXerrorIdx], &sigma[UErrorXerrorIdx]);
    get_stats(m_xypole[1], npole, &mean[UErrorYerrorIdx], &sigma[UErrorYerrorIdx]);
    get_stats(m_rzpole, npole, &mean[UErrorPhaseIdx], &sigma[UErrorPhaseIdx]);
	m_rzpole -= mean[UErrorPhaseIdx];

	if(slopecorr){
        double djsum = 0, djs = 0, dn;
		for(int n = 0; n < npole; n++){
            dn = -0.5*(npole-1)+n;
            djsum += (double)dn*dn;
            djs += dn*m_rzpole[n];
		}
        double slp = djs/djsum;
		for(int n = 0; n < npole; n++){
            m_rzpole[n] -= n*slp;
		}
        get_stats(m_rzpole, npole, &mean[UErrorPhaseIdx], &sigma[UErrorPhaseIdx]);
        m_rzpole -= mean[UErrorPhaseIdx];
	}
}

double IDFieldProfile::f_GetUndulatorPeriod(int *prange, int ixy)
{
	int range[2];
	if(prange == nullptr){
		range[0] = 0;
		range[1] = (int)m_zpeak[ixy].size()-1;
	}
	else{
		range[0] = prange[0];
		range[1] = prange[1];
	}
    double lu = (m_zpeak[ixy][range[1]]-m_zpeak[ixy][range[0]])/(double)(range[1]-range[0])*2.0;
    return lu;
}

void IDFieldProfile::f_ExportData(string dataname)
{
    ofstream debug_out(dataname);
    vector<string> titles{"z", "accx", "accy", "betax", "betay", "x", "y", "rzx", "rzy", "xint", "yint"};
    vector<double> items(titles.size());
    PrintDebugItems(debug_out, titles);
    for(int n = 0; n < m_ndata; n++){
        items[0] = m_z[n];
        for(int j = 0; j < 2; j++){
            items[1+j] = m_acc[j].GetXYItem(n, false);
            items[3+j] = m_beta[j].GetXYItem(n, false);
            items[5+j] = m_xy[j].GetXYItem(n, false);
            items[7+j] = m_rzxy[j].GetXYItem(n, false);
            items[9+j] = m_xyint[j].GetXYItem(n, false);
        }
        PrintDebugItems(debug_out, items);
    }
    debug_out.close();
}
