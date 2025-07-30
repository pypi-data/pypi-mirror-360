#include <algorithm>
#include <math.h>
#include "wakefield.h"
#include <stdio.h>
#include "fast_fourier_transform.h"
#include "print_calculation_status.h"
#include "lattice_operations.h"


#if defined(_macox) || defined(_EMSCRIPTEN)
#include <boost/math/special_functions/expint.hpp>
using namespace boost::math;
#endif

string WakeBeforeFFT;
string WakeUnitCharge;
string WakeResitiveSpl;

WakefieldUtility::WakefieldUtility(SimplexSolver &sxsolver)
    : SimplexSolver(sxsolver)
{
    if(SimplexConfig::m_rank == 0){
#ifdef _DEBUG
        WakeBeforeFFT = "..\\debug\\wake_before_fft.dat";
        WakeUnitCharge = "..\\debug\\wake_unit_charge.dat";
        WakeResitiveSpl = "..\\debug\\wake_resistive.dat";
#endif
    }

    if(m_prm[Wake_][aperture_] < INFINITESIMAL || m_prm[Wake_][corrlen_] < INFINITESIMAL
        || m_prm[Wake_][thickness_] < INFINITESIMAL || m_prm[Wake_][permit_]-1.0 < INFINITESIMAL){
        throw runtime_error("Invalid parameters for the wakefield option.");
    }

    m_types.clear(); m_typenames.clear();
    if(m_bool[Wake_][resistive_]){
        m_types.push_back(resistive_);
    }
    if(m_bool[Wake_][roughness_]){
        m_types.push_back(roughness_);
    }
    if(m_bool[Wake_][dielec_]){
        m_types.push_back(dielec_);
    }
    if(m_bool[Wake_][spcharge_]){
        m_types.push_back(spcharge_);
    }
    if(m_bool[Wake_][wakecustom_]){
        m_types.push_back(wakecustom_);
    }
    for(int j = 0; j < (int)m_types.size(); j++){
        string name = "";
        for(auto iter = Wake.begin(); iter != Wake.end(); iter++){
            int type = get<0>(iter->second);
            string datatype = get<1>(iter->second);
            if(type == m_types[j] && datatype == BoolLabel){
                name = iter->first;
            }
        }
        m_typenames.push_back(name);
    }

    m_evaldist = false;

    LatticeOperation lattice(*this);
    vector<vector<double>> betaarr(3);
    lattice.TwissParametersAlongz(&betaarr, m_betaav);
    m_sigmaebm = (sqrt(m_betaav[0]*m_emitt[0])+sqrt(m_betaav[1]*m_emitt[1]))/2;
    m_gammaz = m_gamma/sqrt(1+m_K*m_K/2);

    // initilize configurations
    m_iscircular = m_bool[Wake_][paralell_] == false;

    m_zcoef[spcharge_] = -CC*Z0VAC/PI/m_gammaz/m_sigmaebm/4;

    double a2 = 0.5*m_prm[Wake_][aperture_];
    a2 *= a2;
    m_s0 = pow(2.0*a2/Z0VAC*m_prm[Wake_][resistivity_], 1.0/3.0);
    m_Tau = m_prm[Wake_][relaxtime_]*CC/m_s0;
    m_zcoef[resistive_] = CC*m_s0*Z0VAC/4.0/PI/a2;

    m_zcoef[roughness_] =
        CC*Z0VAC*m_prm[Wake_][height_]*m_prm[Wake_][height_]
        /8.0/pow(PI, 2.5)/(m_prm[Wake_][aperture_]/2.0)/pow(m_prm[Wake_][corrlen_], 2.0);

    m_zcoef[dielec_] = Z0VAC*CC/PI/a2;
    m_ksynchro =
        sqrt(2.0/(m_prm[Wake_][aperture_]/2.0)/m_prm[Wake_][thickness_]
            /(1.0-1.0/m_prm[Wake_][permit_]));

    if(m_bool[Wake_][wakecustom_]){
        vector<double> s, W;
        if(m_wakeprf.GetDimension() < 0){
            m_prm[Wake_][wakecustom_] = false;
        }
        else{
            m_wakeprf.GetVariable(0, &s);
            m_wakeprf.GetArray1D(1, &W);
            m_customwake.SetSpline((int)s.size(), &s, &W);
        }
    }

    double dkmax = -1, dsmax = -1;
    if(m_bool[Wake_][resistive_]){
        dkmax = 1.0/m_s0/max(m_Tau, pow(m_Tau, 0.25))/8.0;
        m_kmax_resis = dkmax;
    }
    if(m_bool[Wake_][roughness_]){
        dsmax = m_prm[Wake_][corrlen_]*0.01;
    }
    double ds, s;
    m_nfft = 256;
    // compute current profile
    if(m_select[EBeam_][bmprofile_] == GaussianBunch){
        double sigmas = m_prm[EBeam_][bunchleng_], tex;
        ds = 4*sigmas*GAUSSIAN_MAX_REGION/m_nfft;
        f_AdjustSrange(dkmax, dsmax, &ds, &m_nfft);
        m_Iw = new double[2*m_nfft];
        for(int n = 0; n < m_nfft; n++){
            m_Iw[2*n] = m_Iw[2*n+1] = 0;
            s = fft_index(n, m_nfft, 1)*ds;
            tex = s/sigmas;
            tex *= tex/2;
            if(tex < MAXIMUM_EXPONENT){
                m_Iw[2*n] = m_pkcurr*exp(-tex);
            }
        }
    }
    else if(m_select[EBeam_][bmprofile_] == BoxcarBunch){
        double Ds = m_prm[EBeam_][bunchlenr_];
        ds = 2*Ds/m_nfft;
        f_AdjustSrange(dkmax, dsmax, &ds, &m_nfft);
        m_Iw = new double[2*m_nfft];
        for(int n = 0; n < m_nfft; n++){
            m_Iw[2*n] = m_Iw[2*n+1] = 0;
            s = fft_index(n, m_nfft, 1)*ds;
            if(fabs(s)+ds/2 <= Ds/2){
                m_Iw[2*n] = m_pkcurr;
            }
            else if(fabs(s)-ds/2 <= Ds/2){
                m_Iw[2*n] = m_pkcurr*(Ds/2-(fabs(s)-ds/2))/ds;
            }
        }
    }
    else{
        vector<double> sprf, Iprf;
        if(m_select[EBeam_][bmprofile_] == CustomSlice 
                || m_select[EBeam_][bmprofile_] == CustomParticle){
            m_slice.GetArray1D(0, &sprf);
            vector<string> items = get<1>(DataFormat.at(CustomSlice));
            for(int j = 0; j < items.size(); j++){
                if(items[j] == CurrentLabel){
                    m_slice.GetArray1D(j, &Iprf);
                }
            }
        }
        else if(m_select[EBeam_][bmprofile_] == CustomCurrent 
                || m_select[EBeam_][bmprofile_] == SimplexOutput){
            m_currprof.GetArray1D(0, &sprf);
            m_currprof.GetArray1D(1, &Iprf);
        }
        else if(m_select[EBeam_][bmprofile_] == CustomEt){
            m_Etprf.GetProjection(0, 0, &Iprf);
            m_Etprf.GetVariable(0, &sprf);
        }
        while(m_nfft < (int)sprf.size()*2){
            m_nfft <<= 1;
        }

        Spline spl;
        spl.SetSpline((int)sprf.size(), &sprf, &Iprf);
        ds = 2*(sprf.back()-sprf.front())/m_nfft;
        f_AdjustSrange(dkmax, dsmax, &ds, &m_nfft);
        m_Iw = new double[2*m_nfft];
        for(int n = 0; n < m_nfft; n++){
            m_Iw[2*n] = m_Iw[2*n+1] = 0;
            s = fft_index(n, m_nfft, 1)*ds;
            if(s >= sprf.front() && s <= sprf.back()){
                m_Iw[2*n] = spl.GetValue(s);
            }
        }
    }
    m_ds = ds;

    vector<double> Icurr(m_nfft+1), scurr(m_nfft+1);
    for(int n = -m_nfft/2; n <= m_nfft/2; n++){
        scurr[n+m_nfft/2] = ds*n;
        int index = fft_index(n, m_nfft, -1);
        Icurr[n+m_nfft/2] = m_Iw[2*index];
    }
    m_Ispl.SetSpline(m_nfft+1, &scurr, &Icurr);

    m_fft = new FastFourierTransform (1, m_nfft);
    m_fft->DoFFT(m_Iw);
    for(int n = 0; n < m_nfft; n++){ // convert the unit
        m_Iw[2*n] *= ds;
        m_Iw[2*n+1] *= ds;
    }
}

WakefieldUtility::~WakefieldUtility()
{
    delete m_fft;
    delete[] m_Iw;
}

void WakefieldUtility::QSimpsonIntegrand(int layer, double xy, vector<double> *density)
{
    if(m_evaldist){
        f_DensityAtEnergy(xy, density);
    }
    else{
        f_GetACResistiveImpedanceBase(false, xy, m_kappa, m_tau, &(*density)[0], &(*density)[1]);
    }
}

void WakefieldUtility::GetWakeFieldProfiles(vector<string> &types, 
    vector<double> &s, vector<vector<double>> &wakes)
{
    s.resize(m_nfft/2+1);
    for(int n = -m_nfft/4; n <= m_nfft/4; n++){
        s[n+m_nfft/4]  = n*m_ds;
    }
    types = m_typenames;
    wakes.resize(m_types.size());
    for(int j = 0; j < m_types.size(); j++){
        GetWakeFieldProfile(m_types[j], wakes[j]);
    }
    if(m_types.size() > 1){
        vector<double> waketotal = wakes[0];
        for(int j = 1; j < m_types.size(); j++){
            waketotal += wakes[j];
        }
        wakes.insert(wakes.begin(), waketotal);
        types.insert(types.begin(), "Total");
    }
}

void WakefieldUtility::GetWakeFieldProfile(int waketype, vector<double> &wakef)
{
    int n, index;
    vector<double> sr, curr;
    double kk, tmp, ss, fre, fim;

    AllocateMemorySimpson(2, 1, 1);
    wakef.resize(m_nfft/2+1);

    if(waketype == roughness_ && m_select[EBeam_][bmprofile_] == BoxcarBunch){
        double Ds = m_prm[EBeam_][bunchlenr_];
        for(n = -m_nfft/4; n <= m_nfft/4; n++){
            double s = m_ds*n;
            wakef[n+m_nfft/4] = 0.0;
            if(s < -Ds/2){
                wakef[n] += -f_SurfaceRoughnessWakePotentialUnitCharge(-Ds/2-s);
            }
            if(s < Ds/2){
                wakef[n] -= -f_SurfaceRoughnessWakePotentialUnitCharge(Ds/2-s);
            }
            wakef[n] *= m_pkcurr/CC;
        }
        return;
    }

    double dk = PI2/m_ds/m_nfft;

    double *wsI, *wsW, *wsWfft;
    wsI = new double[2*m_nfft];
    wsW = new double[2*m_nfft];
    wsWfft = new double[2*m_nfft];

    for(n = 0; n < m_nfft; n++){
        wsI[2*n] = m_Iw[2*n];
        wsI[2*n+1] = m_Iw[2*n+1];
        if(waketype == roughness_){
            index = fft_index(n, m_nfft, 1);
            kk = dk*(double)index;
            tmp = wsI[2*n];
            wsI[2*n] = wsI[2*n+1]*kk;
            wsI[2*n+1] = -tmp*kk; // multiply i*k to get derivative
        }
    }

    if(waketype == roughness_ || waketype == wakecustom_)
    {
        for(n = -m_nfft/2; n <= m_nfft/2; n++){
            index = fft_index(n, m_nfft, -1);
            ss = m_ds*(double)n;
            wsWfft[2*index+1] = 0.0;
            if(waketype == roughness_){
                wsWfft[2*index] = f_SurfaceRoughnessWakePotentialUnitCharge(ss);
            }
            else{
                if(n == 0){// correction for step function at s=0
                    wsWfft[2*index] = 0.5*f_CustomWakeUnitCharge(ss);                    
                }
                else{
                    wsWfft[2*index] = f_CustomWakeUnitCharge(ss);
                }
            }
        }

#ifdef _DEBUG
        if(!WakeUnitCharge.empty()){
            vector<string> titles{"s", "Wake"};
            vector<double> items(titles.size());
            ofstream debug_out(WakeUnitCharge);
            PrintDebugItems(debug_out, titles);
            for(n = 0; n < m_nfft; n++){
                items[0] = m_ds*fft_index(n, m_nfft, 1);
                items[1] = wsWfft[2*n];
                PrintDebugItems(debug_out, items);
            }
            debug_out.close();
        }
#endif

        m_fft->DoFFT(wsWfft, 1);
        for(n = 0; n < m_nfft; n++){
            wsW[2*n] = m_ds*wsWfft[2*n];
            wsW[2*n+1] = m_ds*wsWfft[2*n+1];
        }
    }
    else{
        Spline resplre, resplim;
        if(waketype == resistive_){
            int nres = 0;
            double kk = 0, dkres = dk;
            vector<double> karr(m_nfft), frearr(m_nfft), fimarr(m_nfft);
            for(n = 0; n < m_nfft; n++){
                karr[n] = kk;
                f_GetACResistiveImpedance(karr[n], &frearr[n], &fimarr[n]);
                if(kk > 2/m_s0){
                    dkres *= 1.1;
                }
                kk += dkres;
                nres++;
                if(karr[n] > dk*m_nfft/2){
                    break;
                }
            }

#ifdef _DEBUG
            if(!WakeResitiveSpl.empty()){
                vector<string> titles{"k", "re", "im"};
                vector<double> items(titles.size());
                ofstream debug_out(WakeResitiveSpl);
                PrintDebugItems(debug_out, titles);
                for(int n = 0; n < nres; n++){
                    items[0] = karr[n];
                    items[1] = frearr[n];
                    items[2] = fimarr[n];
                    PrintDebugItems(debug_out, items);
                }
                debug_out.close();
            }
#endif
            resplre.SetSpline(nres, &karr, &frearr);
            resplim.SetSpline(nres, &karr, &fimarr);
        }

        double wmaxres = 0;
        bool kinrange = true;
        for(n = 0; n < m_nfft; n++){
            index = fft_index(n, m_nfft, 1);
            kk = dk*(double)index;
            if(waketype == resistive_){
                if(kinrange == false){
                    wsW[2*n] = wsW[2*n+1] = 0;
                    continue;
                }
                fre = resplre.GetValue(fabs(kk));
                fim = resplim.GetValue(fabs(kk));
                if(index < 0){
                    fim *= -1;
                }

                if(kk > m_kmax_resis){
                    double w = sqrt(hypotsq(fre, fim));
                    if(w > wmaxres){
                        wmaxres = w;
                    }
                    if(w < wmaxres*1e-6){
                        kinrange = false;
                    }
                }
            }
            else if(waketype == dielec_){
                f_GetSynchroImpedance(0.5*m_ds*(double)m_nfft, kk, &fre, &fim);
            }
            else if(waketype == spcharge_){
                if(n == 0){
                    fre = fim = 0;
                }
                else{
                    f_GetSpaceChargeImpedance(kk, &fre, &fim);
                }
            }
            wsW[2*n] = fre;
            wsW[2*n+1] = fim;
        }
    }

    for(n = 0; n < m_nfft; n++){
        wsW[2*n] = -wsW[2*n]; // reverse the time scale and consider the negative charge
        wsI[2*n] = (tmp = wsI[2*n])*wsW[2*n]-wsI[2*n+1]*wsW[2*n+1];
        wsI[2*n+1] = tmp*wsW[2*n+1]+wsI[2*n+1]*wsW[2*n];
    }

#ifdef _DEBUG
    if(!WakeBeforeFFT.empty()){
        vector<string> titles {"k", "re", "im", "reW", "imW"};
        vector<double> items(titles.size());
        ofstream debug_out(WakeBeforeFFT);
        PrintDebugItems(debug_out, titles);
        for(int n = 0; n < m_nfft; n++){
            items[0] = fft_index(n, m_nfft, 1)*dk;
            items[1] = wsW[2*n];
            items[2] = wsW[2*n+1];
            items[3] = wsI[2*n];
            items[4] = wsI[2*n+1];
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif
  
    m_fft->DoFFT(wsI, -1);

    for(n = -m_nfft/4; n <= m_nfft/4; n++){
        int index = fft_index(n, m_nfft, -1);
        wakef[n+m_nfft/4] = wsI[2*index]*dk/PI2/CC;
    }


    delete[] wsI;
    delete[] wsW;
    delete[] wsWfft;
}

//----- private functions -----
void WakefieldUtility::f_AdjustSrange(double dkmax, double dsmax, double *ds, int *nfft)
{
    if(dsmax > 0){
        while(*ds > dsmax) {
            *ds *= 0.5;
            *nfft <<= 1;
        };
    }
    if(dkmax <= 0){
        return;
    }
    double dk = PI2/(*ds)/(*nfft);
    while(dk > dkmax) {
        dk *= 0.5;
        *nfft <<= 1;
    };
}

void WakefieldUtility::f_GetSpaceChargeImpedance(double k, double *re, double *im)
{
    double xisig = k*m_sigmaebm/m_gammaz;
    double xisig2 = xisig*xisig/2;
    *re = 0;
    if(xisig2 > 50){
        *im = m_zcoef[spcharge_]*xisig*(1/xisig2/xisig2-1/xisig2);
    }
    else{
        *im = m_zcoef[spcharge_]*xisig*exp(xisig2)*expint(-xisig2);
    }
}

void WakefieldUtility::f_GetACResistiveImpedance(double k, double *re, double *im)
{
    if(m_iscircular){
        f_GetACResistiveImpedanceBase(true, 0, k*m_s0, m_Tau, re, im);
    }
    else{
        f_GetACResistiveImpedanceParallelPlate(k*m_s0, m_Tau, re, im);
    }
    *re *= m_zcoef[resistive_];
    *im *= m_zcoef[resistive_];
}

void WakefieldUtility::f_GetACResistiveImpedanceBase(
    bool iscircular, double q, double kappa, double Tau, double *re, double *im)
{
    double Theta, kc, tlam, ktau2, Qktau, tanhq, coshq;

    if(kappa == 0.0){
        *re = *im = 0.0;
        return;
    }

    ktau2 = kappa*Tau;
    ktau2 *= ktau2;
    tlam = fabs(kappa)*Tau/sqrt(1.0+ktau2);
    Qktau = pow(1.0+ktau2, 0.25);

    if(iscircular){ // circular pipe
        coshq = tanhq = 1.0;
    }
    else if(fabs(q) < INFINITESIMAL){ // integrand for parallel plate
        coshq = 1.0; tanhq = 2.0;
    }
    else{
        coshq = coshyper(q); coshq *= coshq;
        tanhq = 2.0*tanhyper(q)/q;
    }

    Theta = 2.0*sqrt(1.0+tlam)-pow(fabs(kappa), 1.5)*Qktau*tanhq;

    kc = 4.0*sqrt(fabs(kappa))*Qktau/(4.0*(1.0-tlam)+Theta*Theta)/coshq;

    *re = 2.0*kc*sqrt(1.0-tlam);
    *im = -(kappa > 0.0 ? 1.0 : -1.0)*Theta*kc;
}

void WakefieldUtility::f_GetACResistiveImpedanceParallelPlate(
    double kappa, double Tau, double *re, double *im)
{
    double qfin = 0.0, zmax = INFINITESIMAL, zz;
    vector<double> zans(2);
	int layers[2] = {0, -1};

    m_kappa = kappa;
    m_tau = Tau;

    while(1){
        f_GetACResistiveImpedanceBase(false, qfin, kappa, Tau, re, im);
        zz = sqrt(hypotsq(*re, *im));
        zmax = max(zmax, zz);
        if(zz/zmax < 1.0e-6){
            break;
        }
        qfin += 1.0;
    };

    IntegrateSimpson(layers, 0.0, qfin, 1.0e-3, 5, nullptr, &zans);
    *re = zans[0]; *im = zans[1];
}

double WakefieldUtility::f_SurfaceRoughnessWakePotentialUnitCharge(double s)
{
    if(s <= 0.0) return 0.0;
    double sn = s/m_prm[Wake_][corrlen_];
    return -m_zcoef[roughness_]
            *(3.56525*exp(-pow(fabs(sn-0.58167), 1.89626)*0.11347)
            *cos(pow(fabs(sn-0.58168), 0.7944)*0.96661))/sqrt(sn);
}

void WakefieldUtility::f_GetSynchroImpedance(double L, double k, double *re, double *im)
{
    double kpm[2], cspm[2], snpm[2];
    int j;

    kpm[0] = (k+m_ksynchro)*L;
    kpm[1] = (k-m_ksynchro)*L;

    for(j = 0; j < 2; j++){
        cspm[j] = cos_sinc(kpm[j]);
        snpm[j] = sin_sinc(kpm[j]);
    }
    *re = m_zcoef[dielec_]*L*(snpm[0]+snpm[1])/2.0;
    *im = m_zcoef[dielec_]*L*(cspm[0]+cspm[1])/2.0;
}

double WakefieldUtility::f_CustomWakeUnitCharge(double s)
{
    return m_customwake.GetValue(s);
}

void WakefieldUtility::GetEVariation(vector<double> &earr, vector<double> &rate)
{
    double ulen = m_N*m_M*m_lu/(m_eGeV*1e9);

    vector<double> sarr;
    vector<string> types;
    vector<vector<double>> wakes;
    GetWakeFieldProfiles(types, sarr, wakes);
    wakes[0] *= ulen;

    double dw = m_prm[EBeam_][espread_]*GAUSSIAN_MAX_REGION;
    double wmax = minmax(wakes[0], true)+dw;
    double wmin = minmax(wakes[0], false)-dw;

    m_wakefspl.SetSpline((int)sarr.size(), &sarr, &wakes[0]);

    int mesh = max(2, (int)floor(0.5+m_prm[PreP_][plotpoints_]));

	m_earr.resize(mesh);
	rate.resize(mesh, 0.0);
	double dr = (wmax-wmin)/(mesh-1);
	for(int n = 0; n < mesh; n++){
		m_earr[n] = wmin+n*dr;
	}
    earr = m_earr;

    AllocateMemorySimpson(mesh, 1, 1);
    m_evaldist = true;
	int layers[2] = {0, -1};
    IntegrateSimpson(layers, sarr.front(), sarr.back(), 0.01, 5, nullptr, &rate);

    double rmax = minmax(rate, true);
    if(rmax > 0){
        rate /= rmax;
    }
}

void WakefieldUtility::f_DensityAtEnergy(double s, vector<double> *density)
{
	double di = m_Ispl.GetValue(s);
	if(di < INFINITESIMAL){
		return;
	}
    double tex, wakev = m_wakefspl.GetValue(s);

	for(int n = 0; n < m_nitems; n++){
		tex = m_earr[n]-wakev;
		if(fabs(tex) > m_prm[EBeam_][espread_]*GAUSSIAN_MAX_REGION){
			(*density)[n] = 0.0;
			continue;
		}
		tex = tex/m_prm[EBeam_][espread_];
		tex *= tex*0.5;
		(*density)[n] = exp(-tex)*di;
	}
}
