#include <algorithm>
#include <complex>
#include "undulator_data_manipulation.h"
#include "randomutil.h"
#include "fast_fourier_transform.h"
#include "optimization.h"

// files for debugging
string UFdataPhaseTrend;
string UFdataRadField;
string UFdataCoupling;
string UFdataAllocated;
string UFDataPhaseErr;

constexpr auto PHASESMOOTHR = 0.5;
constexpr auto MESHPERPERIOD = 64;
constexpr auto EPUTHRESHOLD = 1e-3;

UndulatorFieldData::UndulatorFieldData(int rank)
	: IDFieldProfile(rank)
	
{
	if(rank != 0){
		return;
	}
#ifdef _DEBUG
//	UFdataPhaseTrend = "..\\debug\\ufdata_phase_trend.dat";
//	UFdataRadField = "..\\debug\\ufdata_rad_field.dat";
//	UFdataCoupling = "..\\debug\\ufdata_coupling.dat";
//	UFdataAllocated = "..\\debug\\ufdata_allocated.dat";
//	UFDataPhaseErr = "..\\debug\\ufdata_allocated_phase.dat";
#endif
}

void UndulatorFieldData::AllocateUData(int np, DataContainer *data, int N, double lu, double K2)
{
	m_isideal = false;
	m_np = np;
	m_N = N;
	m_lu = lu;
	m_K2 = K2;

	IDFieldProfile::AllocateIntegral(data, true);

	double sigma[NumberUError];
	double lut[2] = {-1, -1};
	for(int j = 0; j < 2; j++){
		SearchPeak(1e-6, j);
		if(m_zpeak[j].size() > 1){
			lut[j] = (m_zpeak[j].back()-m_zpeak[j].front())/(m_zpeak[j].size()-1);
		}
	}
	int ixy = fabs(m_lu-lut[0]) < fabs(m_lu-lut[1]) ? 0 : 1;
	m_endpoles[0] = m_endpoles[1] = ((int)m_zpeak[ixy].size()-m_N*2)/2;
	if(m_endpoles[0] < 0){
		throw runtime_error("Too few magnetic periods contained in the imported data.");
	}

	GetErrorContents(m_endpoles, sigma, &m_items);
	AdjustKValue(sqrt(2.0*m_K2));

	m_zpeak0 = m_zpeak[ixy][m_endpoles[0]+1];
}

bool UndulatorFieldData::AllocateUData(int np,
	RandomUtility *rand, int N, double lu, double K2, vector<double> Kxy[], vector<double> deltaxy[],
	double *sigma, double *sigalloc)
{
	m_np = np;
	m_isideal = rand == nullptr;

	m_isfsymm = true;
	m_isendcorr = true;

	m_K2 = K2;
	m_N = N+1; // regular section starts and ends at the peak field, so (N+1) periods needed
	m_endpoles[0] = m_endpoles[1] = 2*ENDPERIODS; // # end poles at each end
	bool isepu = max(minmax(Kxy[0], true), fabs(minmax(Kxy[0], false))) > EPUTHRESHOLD;
	if(isepu){// this is an EPU, so add an extra period
		m_N++;
	}
	f_SetCommonPrm(lu, Kxy, deltaxy);

	if(m_isfsymm){
		m_z0thpole[0] += m_lu*0.25;
		m_z0thpole[1] += m_lu*0.25;
	}
	m_zpeak0 = m_z0thpole[1]+m_endpoles[0]*m_lu/2; 
		// defined by the 1st peak position of By,

	if(!AllocateIntegral(rand, true, sigma, sigalloc)){
		throw runtime_error(m_errmsg);
	}

	if(m_isideal){
		m_idealrange[0] = SearchIndex(m_ndata, true, m_z, m_zpeak0-m_lu*0.5);
		m_idealrange[1] = SearchIndex(m_ndata, true, m_z, m_zpeak0+m_lu*1.5);
	}
	return true;
}

void UndulatorFieldData::SetRandomSeed(int mseg, RandomUtility *rand, int seed, double *sigma)
{
	rand->Init(seed);
	for(int m = 0; m < mseg; m++){
		if(sigma[UErrorBdevIdx] < 0){
			rand->Uniform(0, 1.0);
		}
		for(int n = 0; n < 4*(m_N+m_endpoles[0]); n++){
			// call rand 2*2*(m_N+m_endpoles[0]) times
			rand->Gauss(true);
		}
	}
}


bool UndulatorFieldData::AllocateIntegral(
	RandomUtility *rand, bool isnormalize, double *sigma, double *sigalloc)
{
	vector<vector<double>> acc(2);

	m_z.resize(m_ndata);
	m_isnormalize = isnormalize;

	m_i1err.resize(2); m_i1drv.resize(2); 
	m_bdrv.resize(2); m_bkick.resize(2); m_wsacc.resize(2);
	for(int j = 0; j < 2; j++){
		m_i1err[j].resize(2*(m_N+m_endpoles[0])); fill(m_i1err[j].begin(), m_i1err[j].end(), 0);
		m_i1drv[j].resize(2*(m_N+m_endpoles[0])); fill(m_i1drv[j].begin(), m_i1drv[j].end(), 0);
		m_bkick[j].resize(2*(m_N+m_endpoles[0])); fill(m_bkick[j].begin(), m_bkick[j].end(), 0);
		m_bcorr[j].resize(2*(m_N+m_endpoles[0])); fill(m_bcorr[j].begin(), m_bcorr[j].end(), 0);
		m_bdrv[j].resize(2*(m_N+m_endpoles[0]));  fill(m_bdrv[j].begin(), m_bdrv[j].end(), 0);
	}
	m_eta.resize(2*(m_N+m_endpoles[0])); fill(m_eta.begin(), m_eta.end(), 0);

	// orbit error arrangement
	double fdev;
	if(rand != nullptr){
		fdev = sigma[UErrorBdevIdx];
		if(fdev < 0){
			fdev = fabs(fdev)*rand->Uniform(0, 1.0);
		}
		for(int n = 0; n < m_N+m_endpoles[0]; n++){
			for(int j = 0; j < 2; j++){
				m_bdrv[j][2*n+1] = m_B*fdev*rand->Gauss(true);
				m_bdrv[j][2*n] = -m_bdrv[j][2*n+1];
			}
		}
	}

	// evaluate the field quality without correction
	for(int j = 0; j < 3; j++){
		m_frac[j] = 1.0;
	}
	f_ApplyErrors();

	if(rand == nullptr){
#ifdef _DEBUG
		if(!UFdataAllocated.empty()){
			f_ExportData(UFdataAllocated);
		}
#endif
		return true;
	}

	double sigstd[NumberUError];
	GetErrorContents(m_endpoles, sigstd, &m_items);
	// adjust the orbit error component
	m_frac[0] = sigma[UErrorYerrorIdx]/sigstd[UErrorYerrorIdx];
	m_frac[1] = sigma[UErrorXerrorIdx]/sigstd[UErrorXerrorIdx];

	double pdev = max(m_frac[0], m_frac[1]);
	if(pdev > 1.0){
		// the field deviation too small for the orbit error
		m_errmsg = "The field deviation is too small to generate the specified trajectory error.";
		return false;
	}
	pdev = sqrt(1.0-pdev)*fdev;
	for(int n = 0; n < m_N+m_endpoles[0]; n++){
		// compensate the field error to satisfy the given condition
		for(int j = 0; j < 2; j++){
			double bdev = m_B*pdev*rand->Gauss(true);
			m_bdrv[j][2*n+1] = m_bdrv[j][2*n+1]*m_frac[j]+bdev;
			m_bdrv[j][2*n] = m_bdrv[j][2*n]*m_frac[j]+bdev;
		}
	}
	m_frac[0] = m_frac[1] = 1;
	f_ApplyErrors();
	GetErrorContents(m_endpoles, sigstd, &m_items);
	double sigsq = sigstd[UErrorPhaseIdx]*sigstd[UErrorPhaseIdx];

	m_frac[2] = 0;
	f_AdjustPhase();
	f_ApplyErrors();
	GetErrorContents(m_endpoles, sigstd, &m_items, nullptr, true);
	double sig0sq = sigstd[UErrorPhaseIdx];
	if(sig0sq > sigma[UErrorPhaseIdx]){
		m_errmsg = "The trajectory error is too large compared to the phase error.";
		return false;
	}
	sig0sq *= sig0sq;

	double eps = 0.05, err, tgteta;
	double sigtsq = sigma[UErrorPhaseIdx]*sigma[UErrorPhaseIdx];
	m_frac[2] = 1.0;
	do{
		tgteta = sigsq-sig0sq;
		if(tgteta <= 0){
			m_errmsg = "Cannot find a solution to generate the specified undulator error model.";
			return false;
		}
		tgteta = sqrt((sigtsq-sig0sq)/tgteta);
		m_frac[2] *= tgteta;
		f_ApplyErrors();
		GetErrorContents(m_endpoles, sigalloc, &m_items);
		sigsq = sigalloc[UErrorPhaseIdx]*sigalloc[UErrorPhaseIdx];
		err = fabs(sigalloc[UErrorPhaseIdx]-sigma[UErrorPhaseIdx]);
	} while(fabs(tgteta-1.0) > 0.01 && err > eps);

    AdjustKValue(sqrt(2.0*m_K2));

#ifdef _DEBUG
	if(!UFdataAllocated.empty()){
		f_ExportData(UFdataAllocated);
	}
	if(!UFDataPhaseErr.empty()){
		ofstream debug_out(UFDataPhaseErr);
		vector<string> titles{"z", "phase"};
		vector<double> items(titles.size());
		PrintDebugItems(debug_out, titles);
		int npoles = (int)m_items[0].size();
		for(int n = 0; n < npoles; n++){
			items[0] = m_items[UErrorPeakPosIdx][n];
			items[1] = m_items[UErrorPhaseIdx][n];
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif

	return err <= eps;
}

void UndulatorFieldData::GetErrorArray(
	vector<vector<double>> *I1err, vector<vector<double>> *bkick)
{
	*I1err = m_i1err;
	*bkick = m_bkick;
}

void UndulatorFieldData::GetPhaseError(vector<double> &zpeak, vector<double> &phase)
{
	double sigstd[NumberUError];
	GetErrorContents(m_endpoles, sigstd, &m_items, nullptr, true);
	zpeak = m_items[UErrorPeakPosIdx];
	phase = m_items[UErrorPhaseIdx];
	if(m_isideal){
		fill(phase.begin(), phase.end(), 0);
	}
}

void UndulatorFieldData::GetEnt4Err(double zent[])
{
	zent[0] = m_z0thpole[0];
	zent[1] = m_z0thpole[1];
}

int UndulatorFieldData::GetPoleNumber(double z, double z0th, double lu)
{
	return (int)floor((z-z0th)/(lu*0.5)+0.5);
}

void UndulatorFieldData::GetCoupling(
	int nhmax,	double gtxy[], vector<int> &steps, int intstep, vector<double> &z, int ngt, int nphi,
	vector<vector<vector<vector<vector<double>>>>> &Fre, vector<vector<vector<vector<vector<double>>>>> &Fim)
{
	double gt2 = hypotsq(gtxy[0], gtxy[1]), Theta[3];
	vector<double> Phi, Exy[2];
	Spline PhiSpl, ExySpl[2];

	int nrange[2] = {0, m_ndata-1};
	int *nranger = m_isideal ? m_idealrange : nrange;
	int ndata = nranger[1]-nranger[0]+1;

	Phi.resize(ndata);
	for(int j = 0; j < 2; j++){
		Exy[j].resize(ndata);
	}

	for(int n = nranger[0]; n <= nranger[1]; n++){
		Phi[n-nranger[0]] = (1+gt2)*(m_z[n]-m_zpeak0);
		for(int j = 0; j < 2; j++){
			Phi[n-nranger[0]] += m_rzxy[j].GetXYItem(n, false)-2*gtxy[j]*m_xy[j].GetXYItem(n, false);
			Theta[j] = m_beta[j].GetXYItem(n, false)-gtxy[j];
		}
		Theta[2] = hypotsq(Theta[0], Theta[1]);
		for(int j = 0; j < m_np; j++){
			for(int nh = 0; nh < nhmax; nh++){
				Exy[j][n-nranger[0]] = Theta[j]/(1+Theta[2]);
			}
		}
	}
	for(int j = 0; j < m_np; j++){
		ExySpl[j].SetSpline(ndata, &Phi, &Exy[j]);
		ExySpl[j].AllocateGderiv();
	}

#ifdef _DEBUG
	if(!UFdataRadField.empty()){
		ofstream debug_out(UFdataRadField);
		vector<string> titles{"Phi", "z", "Ex"};
		if(m_np > 1){
			titles.push_back("Ey");
		}
		vector<double> items(titles.size());
		PrintDebugItems(debug_out, titles);
		for(int n = 0; n < ndata; n++){
			items[0] = Phi[n];
			items[1] = m_z[n+nranger[0]]-m_zpeak0;
			for(int j = 0; j < m_np; j++){
				items[j+2] = Exy[j][n];
			}
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif

	double zrange[2], Phirange[2], sn[2], phin, W, Gr, Gi;
	for(int nh = 0; nh < nhmax; nh++){
		W = (nh+1)*PI2/m_lu/(1+m_K2);
		phin = -PI2*gt2/(1.0+m_K2)*intstep;
		sn[0] = cos(phin);
		sn[1] = sin(phin);
		for(int np = 0; np < m_np; np++){
			int nini = -1;
			for(int k = 0; k < steps.size(); k++){
				int n = steps[k];
				if(m_isideal){
					if(k > 0){
						break;
					}
					zrange[0] = 0;
					zrange[1] = m_lu;
				}
				else{
					if(n == 0){
						zrange[0] = 0;
						zrange[1] = z[0];
					}
					else{
						double zorg = steps[0] > 0 ? z[steps[0]-1] : 0;
						zrange[0] = z[n-1]-zorg;
						zrange[1] = z[n]-zorg;
					}
					phin = -PI2*gt2/(1.0+m_K2)*(zrange[1]/m_lu);
					sn[0] = cos(phin);
					sn[1] = sin(phin);
				}
				for(int i = 0; i < 2; i++){
					Phirange[i] = (1+gt2)*zrange[i];
					for(int j = 0; j < 2; j++){
						Phirange[i] += m_rzxy[j].GetValue(zrange[i]+m_zpeak0)
							-2*gtxy[j]*m_xy[j].GetValue(zrange[i]+m_zpeak0);
					}
				}
				if(nini < 0){
					nini = ExySpl[0].GetIndexXcoord(Phirange[0]);
				}
				nini = ExySpl[np].IntegrateGtEiwt(nini, Phirange, W, &Gr, &Gi);
				multiply_complex(&Gr, &Gi, sn);

				Fre[np][nh][n][ngt][nphi] = Gr;
				Fim[np][nh][n][ngt][nphi] = Gi;

				if(m_isideal && intstep > 1){
					double phin2 = PI2*(nh+1)*gt2/(1.0+m_K2);
					double sn0[2];
					if(phin2 < 1e-6){
						sn0[0] = intstep;
						sn0[1] = 0;
					}
					else{
						complex<double> p(0.0, phin2);
						complex<double> pN(0.0, intstep*phin2);
						complex<double> snc = (1.0-exp(pN))/(1.0-exp(p));
						sn0[0] = snc.real();
						sn0[1] = snc.imag();
					}
					multiply_complex(&Fre[np][nh][n][ngt][nphi], &Fim[np][nh][n][ngt][nphi], sn0);
				}
				if(nphi == 0){
					// input for phi = 2*PI
					Fre[np][nh][n][ngt].back() = Fre[np][nh][n][ngt][0];
					Fim[np][nh][n][ngt].back() = Fim[np][nh][n][ngt][0];
				}			
			}
			if(m_isideal){
				for(int k = 1; k < steps.size(); k++){
					int n = steps[k];
					Fre[np][nh][n][ngt][nphi] = Fre[np][nh][steps[0]][ngt][nphi];
					Fim[np][nh][n][ngt][nphi] = Fim[np][nh][steps[0]][ngt][nphi];
					if(nphi == 0){
						Fre[np][nh][n][ngt].back() = Fre[np][nh][steps[0]][ngt][0];
						Fim[np][nh][n][ngt].back() = Fim[np][nh][steps[0]][ngt][0];
					}
				}
			}
		}
	}

#ifdef _DEBUG
	if(!UFdataCoupling.empty()){
		ofstream debug_out(UFdataCoupling);
		vector<string> titles{"z"};
		for(int nh = 0; nh < nhmax; nh++){
			titles.push_back("FxRe"+to_string(nh+1));
			titles.push_back("FxIm"+to_string(nh+1));
			if(m_np > 1){
				titles.push_back("FyRe"+to_string(nh+1));
				titles.push_back("FyIm"+to_string(nh+1));
			}
		}
		vector<double> items(titles.size());
		PrintDebugItems(debug_out, titles);
		for(int k = 0; k < steps.size(); k++){
			items[0] = z[steps[k]];
			int ni = 0;
			for(int nh = 0; nh < nhmax; nh++){
				for(int j = 0; j < m_np; j++){
					items[++ni] = Fre[j][nh][steps[k]][ngt][nphi];
					items[++ni] = Fim[j][nh][steps[k]][ngt][nphi];
				}
			}
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif
}


//----- private functions -----
void UndulatorFieldData::f_AdjustPhase()
{
	int npoles = (int)m_items[UErrorPhaseIdx].size();
	int nfft = 1, n;
	while(nfft < npoles*1.5){
		nfft <<= 1;
	}
	vector<double> zpole(npoles), zphase(npoles);
	double *data = new double[nfft];

	for(int n = 0; n < npoles; n++){
		zpole[n] = (double)n*m_lu*0.5;
		data[n] = m_items[UErrorPhaseIdx][n];
	}
	for(n = npoles; n < nfft; n++){
		if(n < (npoles+nfft)/2){
			data[n] = 0.5*(m_items[UErrorPhaseIdx][npoles-1]+m_items[UErrorPhaseIdx][npoles-2]);
		}
		else{
			data[n] = 0.5*(m_items[UErrorPhaseIdx][0]+m_items[UErrorPhaseIdx][1]);
		}
	}
	FastFourierTransform fft(1, nfft);
	fft.DoFFTFilter(data, PHASESMOOTHR, false, true);

	for(n = 0; n < npoles; n++){
		zphase[n] = data[n];
	}
	delete[] data;

	Spline zphasespl;
	zphasespl.SetSpline(npoles, &zpole, &zphase, true);

	double pcoef = m_lu*(1.0+m_K2)/(2.0*m_K2)/360.0;
	for(n = 0; n < npoles; n++){
		m_eta[n+m_prange[0]] = zphasespl.GetDerivativeAt(zpole[n]+m_lu*0.25)*pcoef;
	}

#ifdef _DEBUG
	if(!UFdataPhaseTrend.empty()){
		ofstream debug_out(UFdataPhaseTrend);
		if(debug_out){
			vector<double> tmp(2);
			for(int n = 0; n < npoles; n++){
				tmp[0] = zphase[n];
				tmp[1] = m_eta[m_prange[0]+n];
				PrintDebugItems(debug_out, zpole[n], tmp);
			}
		}
	}
#endif
}

void UndulatorFieldData::f_ApplyErrors()
{
	for(int j = 0; j < 2; j++){
		for(int n = 0; n < 2*(m_N+m_endpoles[0]); n++){
			m_i1err[j][n] = m_eta[n]*(m_frac[2]-1.0);
			m_bkick[j][n] = m_bdrv[j][n]*m_frac[j];
		}
	}
	f_AllocateFieldError(m_i1err, m_bkick, m_wsacc);
    for(int j = 0; j < 2; j++){
        m_acc[j].SetSpline(m_ndata, &m_z, &m_wsacc[j]);
    }
    CalculateIntegral(m_isnormalize);
}

void UndulatorFieldData::f_AllocateFieldError(
	vector<vector<double>> &i1err, vector<vector<double>> &berr, vector<vector<double>> &acc)
{
	double xyz[3] = {0, 0, 0};
	double Bxyz[3], bdev[2], ratio[2];
	double zent = -(double)(m_N+m_endpoles[0]+1)*m_lu*0.5;
	int polen[2];
	vector<double> accsq;

	for(int j = 0; j < 2; j++){
		acc[j].resize(m_ndata);
	}
    accsq.resize(m_ndata);
    for(int n = 0; n < m_ndata; n++){
        xyz[2] = m_z[n] = zent+(double)(n-1)*m_dz;
		for(int j = 0; j < 2; j++){
			polen[j] = max(0, min(2*(m_N+2)-1, GetPoleNumber(m_z[n], m_z0thpole[j], m_lu)));
			ratio[j] = 1.0+i1err[j][polen[j]];
			bdev[j] = berr[j][polen[j]];
		}
		get_id_field_general(0.0, m_N+m_endpoles[0], m_lu, m_Kxy, m_deltaxy, 
			ratio, bdev, nullptr, m_isfsymm, m_isendcorr, xyz, Bxyz);
		for (int j = 0; j < 2; j++){
			acc[j][n] = Bxyz[1-j];
		}
		accsq[n] = hypotsq(Bxyz[0], Bxyz[1]);
    }
    m_accsq.SetSpline(m_ndata, &m_z, &accsq);
    m_accsq.Integrate(&accsq);
    m_accsq.SetSpline(m_ndata, &m_z, &accsq);
}

void UndulatorFieldData::f_SetCommonPrm(double lu, vector<double> Kxy[], vector<double> deltaxy[])
{
	m_lu = lu;
	m_B = sqrt(2.0*m_K2)/(COEF_K_VALUE*m_lu);
	double Bmax[2] = {0, 0};
	int kmax[2] = {1, 1};
	for(int j = 0; j < 2; j++){
		m_Kxy[j] = Kxy[j];
		m_deltaxy[j] = deltaxy[j];
		for(int k = 1; k < m_Kxy[j].size(); k++){
			double Br = m_Kxy[j][k]/(COEF_K_VALUE*m_lu/k);
			if(Br > Bmax[j]){
				Bmax[j] = Br;
				kmax[j] = k;
			}
		}
	}

	m_z0thpole[0] = m_z0thpole[1] = -(double)(m_N+m_endpoles[0])*m_lu*0.5+m_lu*0.25;
	for(int j = 0; j < 2; j++){
		m_z0thpole[j] += -(m_lu/kmax[j])*m_deltaxy[j][kmax[j]]/PI2;
	}

	int nhmax = max(kmax[0], kmax[1]);
    m_ndata = (m_N+m_endpoles[0]+1)*(MESHPERPERIOD*nhmax)+1;
    m_dz = m_lu/(double)(MESHPERPERIOD*nhmax);
}
