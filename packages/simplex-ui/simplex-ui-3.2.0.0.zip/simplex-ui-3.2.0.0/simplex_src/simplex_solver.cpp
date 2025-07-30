#include <sstream>
#include "simplex_solver.h"
#include "lattice_operations.h"
#include "particle_handler.h"
#include "radiation_handler.h"
#include "undulator_data_manipulation.h"
#include "wakefield.h"
#include  "rocking_curve.h"
#include "bessel.h"
#include "json_writer.h"
#include "function_statistics.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif
#include <iomanip>

void ExportData(stringstream &ssresult, int indlevel,
    int dimension, int nitems, int nscans, int delmesh, bool isnewl,
    vector<vector<double>> &vararray, vector<vector<vector<double>>> &data, int fdim = 1);

// solver main class
string SolverSlicePrmParticle = "";
string SolverCouplingXY = "";
string SolverCouplingCyl = "";
string SolverCouplingZ = "";
string SolverMBEt = "";

// step number to export debug data;
vector<int> ExportSteps {39};

SimplexSolver::SimplexSolver(SimplexConfig &spconf, int thid, MPIbyThread *thread)
	: SimplexConfig(spconf)
{
#ifdef _DEBUG
    SolverSlicePrmParticle = "..\\debug\\solver_slice_particle.dat";
    SolverCouplingXY = "..\\debug\\solver_coupling_xy.dat";
    SolverCouplingCyl = "..\\debug\\solver_coupling_cyl.dat";
    SolverCouplingZ = "..\\debug\\solver_coupling_z.dat";
    SolverMBEt = "..\\debug\\solver_mbet.dat";
#endif

    m_thread = thread;
    if(m_thread != nullptr){
        m_rank = thid;
        m_procs = thread->GetThreads();
    }

    m_exslices = 2;
    m_BGmodes = 4;

    m_isGauss = m_select[SimCtrl_][simoption_] == SmoothingGauss;
    m_skipwave = m_isGaussDebug = false;
    if(m_isGauss){
        //m_isGaussDebug = true;
        m_skipwave = m_bool[SimCtrl_][skipwave_];
        if(m_skipwave){
            m_bool[DataDump_][radiation_] = false;
        }
    }

    m_lu = m_prm[Und_][lu_]*0.001; // mm -> m
    m_N = (int)floor(m_prm[Und_][length_]/m_lu+1e-6); // 1e-6 to avoid truncation due to numerical error
    m_M = (int)floor(m_prm[Und_][segments_]+0.5);
    if(m_select[Und_][utype_] == LinearUndLabel){
        m_K = m_prm[Und_][K_];
        m_Kphi = 0;
    }
    else if(m_select[Und_][utype_] == HelicalUndLabel){
        m_K = m_prm[Und_][Kperp_];
        m_Kphi = 45;
    }
    else{
        m_K = m_prm[Und_][Kperp_];
        m_Kphi = m_prm[Und_][epukratio_];
    }

    if(m_select[EBeam_][bmprofile_] == SimplexOutput || 
            m_select[Seed_][seedprofile_] == SimplexOutput){
        f_InitSimplexOutput();
    }
    if(m_select[EBeam_][bmprofile_] == GaussianBunch){
        f_InitGaussian();
    }
    else if(m_select[EBeam_][bmprofile_] == BoxcarBunch){
        f_InitBoxcar();
    }
    else if(m_select[EBeam_][bmprofile_] == CustomSlice){
        f_InitCustomSlice();
    }
    else if(m_select[EBeam_][bmprofile_] == CustomCurrent){
        f_InitCustomCurr();
    }
    else if(m_select[EBeam_][bmprofile_] == CustomEt){
        f_InitCustomEt();
    }
    else if(m_select[EBeam_][bmprofile_] == CustomParticle){
        f_InitCustomParticle();
    }
    m_lambda_s = m_lambda1;
    if(m_steadystate){
        m_lambda_s *= 1+m_prm[Seed_][relwavelen_];
    }

    if(m_bool[SimCtrl_][autostep_]){
        int n1 = max(1, (int)floor(m_Lg3d*GainPerStep/m_lu));
        int n2 = max(1, (int)ceil(m_Lg3d*GainPerStep/m_lu));
        if(n1 != n2 && n1*floor(m_N/n1) < n2*floor(m_N/n2)){
            n1 = n2;
        }
        m_intstep = n1;
    }
    else{
        m_intstep = (int)floor(0.5+m_prm[SimCtrl_][step_]);
    }
    m_N -= m_N%m_intstep;
    m_segsteps = m_N/m_intstep;
    m_zstep = m_intstep*m_lu;

    double driftlen = m_prm[Und_][interval_]-m_N*m_lu;
    m_driftsteps = (int)ceil(driftlen/(m_intstep*m_lu*(1+m_K*m_K/2)));

    if(m_driftsteps > 0){
        m_zstep_drift = driftlen/m_driftsteps;
    }
    else{
        m_zstep_drift = 0;
    }

    m_totalsteps = m_M*m_segsteps+(m_M-1)*m_driftsteps;

    // set longitudinal coordinate
    for(int j = 0; j < 2; j++){
        m_steprange[j].resize(m_M);
    }
    m_z.resize(m_totalsteps);
    m_detune_err.resize(m_totalsteps, 0.0);
    m_inund.resize(m_totalsteps);
    m_chicane.resize(m_totalsteps); fill(m_chicane.begin(), m_chicane.end(), -1);
    m_zexport.resize(m_totalsteps);
    fill(m_zexport.begin(), m_zexport.end(), false);
    m_segend.resize(m_totalsteps);
    fill(m_segend.begin(), m_segend.end(), -1);

    vector<bool> segext(m_M, false);
    if(m_bool[DataDump_][particle_] || m_bool[DataDump_][radiation_]){
        segext.back() = true;
        if(m_select[DataDump_][expstep_] == DumpSegExitLabel){
            fill(segext.begin(), segext.end(), true);
        }
        else if(m_select[DataDump_][expstep_] == DumpSpecifyLabel){
            int segstep = (int)floor(0.5+m_prm[DataDump_][segint_]);
            int segini = max(0, (int)floor(0.5+m_prm[DataDump_][iniseg_])-1);
            for(int m = segini; m < m_M; m += segstep){
                segext[m] = true;
            }
        }
    }
    int mchic = -1;
    if(m_bool[Chicane_][chicaneon_]){
        mchic = (int)floor(0.5+m_prm[Chicane_][chpos_])-1;
    }

    vector<double> udetune(m_M, 0), ddetune(m_M, 0);
    m_Koffset.resize(m_M, 0.0);
    if(m_select[Alignment_][ualign_] == TargetErrorLabel){
        RandomUtility rand;
        int seed = (int)floor(0.5+m_prm[Alignment_][alrandseed_]);
        rand_init(m_bool[Alignment_][alautoseed_], seed, m_procs, m_rank, &rand, m_thread);
        for(int m = 0; m < m_M; m++){
            m_Koffset[m] = m_prm[Alignment_][Ktol_]*rand.Uniform(-1, 1);
            double Kerr = m_K+m_Koffset[m];
            udetune[m] = 1-(1+Kerr*Kerr/2)/(1+m_K*m_K/2);
            ddetune[m] = -m_prm[Alignment_][sliptol_]*rand.Uniform(-1, 1)/360.0;
        }
    }
    else if(m_select[Alignment_][ualign_] == TargetOffsetLabel){
        for(int n = 0; n < m_ualignment.size(); n++){
            int m = (int)floor(m_ualignment[n][0]+0.5)-1;
            if(m < 0 || m > m_M){
                continue;
            }
            m_Koffset[m] = m_ualignment[n][1];
            double Kerr = m_K+m_Koffset[m];
            udetune[m] = 1-(1+Kerr*Kerr/2)/(1+m_K*m_K/2);
            ddetune[m] = -m_ualignment[n][2]/360.0;
        }
    }

    for(int m = 0; m < m_M; m++){
        int index;
        for(int n = 0; n < m_segsteps; n++){
            index = m*(m_segsteps+m_driftsteps)+n;
            m_z[index] = m*m_prm[Und_][interval_]+(n+1)*m_zstep;
            m_inund[index] = true;
            if(m == mchic && !m_lasermod){
                m_inund[index] = false;
                m_chicane[index] = n == m_segsteps-1 ? 1 : 0;
            }
            else{
                m_detune_err[index] = udetune[m];
            }
            if(n == 0){
                m_steprange[0][m] = index;
            }
            else if(n == m_segsteps-1){
                m_steprange[1][m] = index;
                m_zexport[index] = segext[m];
                m_segend[index] = m;
            }
        }
        if(m == m_M-1){
            break;
        }
        if(m_driftsteps < 1){
            m_detune_err[index] += ddetune[m];
        }
        for(int n = 1; n <= m_driftsteps; n++){
            m_z[index+n] = m_z[index]+n*m_zstep_drift;
            m_inund[index+n] = false;
            m_detune_err[index+n] = ddetune[m]/m_driftsteps;
        }
        m_z[index+m_driftsteps] = (m+1)*m_prm[Und_][interval_];
    }
    if(m_select[DataDump_][expstep_] == RegularIntSteps){
        int interv = max(1, (int)floor(0.5+m_prm[DataDump_][stepinterv_]));
        fill(m_zexport.begin(), m_zexport.end(), false);
        for(int n = m_totalsteps-1; n >= 0; n -= interv){
            m_zexport[n] = true;
        }
    }

    for(int n = 0; n < m_z.size(); n++){
        if(m_zexport[n]){
            m_exportz.push_back(m_z[n]);
            m_exporsteps.push_back(n);
        }
    }

    for(int n = (int)m_exporsteps.size()-1; n >= 0; n--){
        if(m_chicane[m_exporsteps[n]] == 0){
            m_exporsteps.erase(m_exporsteps.begin()+n);
            m_exportz.erase(m_exportz.begin()+n);
        }
    }

    // set slice coordinate
    if(m_array[SimCtrl_][simrange_][0] > m_array[SimCtrl_][simrange_][1]){
        swap(m_array[SimCtrl_][simrange_][0], m_array[SimCtrl_][simrange_][1]);
    }
    m_lslice = m_lambda_s*m_intstep;
    m_dTslice = m_lslice/CC;
    int nspos[2];
    for(int j = 0; j < 2; j++){
        if(m_steadystate){
            nspos[j] = (int)floor(0.5+m_prm[SimCtrl_][simpos_]/m_lslice);
        }
        else{
            nspos[j] = (int)floor(0.5+m_array[SimCtrl_][simrange_][j]/m_lslice);
        }
    }
    m_slices = nspos[1]-nspos[0]+1;
    m_s.resize(m_slices);
    for(int ns = nspos[0]; ns <= nspos[1]; ns++){
        m_s[ns-nspos[0]] = m_lslice*ns;
    }

    if(m_select[EBeam_][bmprofile_] == SimplexOutput ||
        m_select[Seed_][seedprofile_] == SimplexOutput)
    {
        m_slippage = m_prm[SPXOut_][matching_]/m_gamma/m_gamma/2;
        m_slippage = ceil(m_slippage/m_lslice)*m_lslice;
    }

    if(m_steadystate){
        m_slices_total = m_slices;
    }
    else{
        m_slices_total = m_slices+m_totalsteps;
    }

    m_sranges = new int[2];
    m_onslices = new int[m_slices_total];
    m_srangep = &m_sranges;
    m_onslicep = &m_onslices;

    m_nhmax = (int)floor(0.5+m_prm[SimCtrl_][maxharmonic_]);

    for(int m = 0; m < m_M; m++){
        m_segideal.push_back(m);
    }
    if(m_select[Und_][umodel_] == SpecifyErrLabel){
        if(m_bool[Und_][allsegment_]){
            m_segerr = m_segideal;
            m_segideal.clear();
        }
        else{
            int errseg = (int)floor(m_prm[Und_][tgtsegment_]+0.5)-1; // 1 ~ m_M -> 0 ~ m_M-1
            if(errseg >= 0 && errseg < m_M){
                m_segideal.erase(m_segideal.begin()+errseg);
                m_segerr.push_back(errseg);
            }
        }
    }
    else if(m_select[Und_][umodel_] == ImportDataLabel){
        for(int n = 0; n < m_udcont.size(); n++){
            int dseg = stoi(m_udcont[n][0])-1;  // 1 ~ m_M -> 0 ~ m_M-1
            if(dseg >= 0 && dseg < m_M){
                auto result = find(m_unames.begin(), m_unames.end(), m_udcont[n][1]);
                if(result != m_unames.end()){
                    int index = (int)(result-m_unames.begin());
                    m_udata.insert(make_pair(dseg, &m_uconts[index]));
                    m_segideal.erase(remove(m_segideal.begin(), m_segideal.end(), dseg), m_segideal.end());
                    m_segdata.push_back(dseg);
                }
            }
        }
    }

    double csn[] = {sin(DEGREE2RADIAN*m_Kphi), cos(DEGREE2RADIAN*m_Kphi)};
    if(m_select[Und_][utype_] == MultiHarmUndLabel){
        if(m_harmcont.size() == 0){
            m_harmcont.push_back(vector<double> {1, 90, 1, 0});
            // default: elliptic undulator
        }
        int nhmax = (int)m_harmcont.size();
        for(int j = 0; j < 2; j++){
            m_Kxy[j].resize(nhmax+1, 0.0);
            // m_Kxy[x,y][harmonic starting with 1]
            m_deltaxy[j].resize(nhmax+1, 0.0);
        }
        double kxysum[2] = {0, 0};
        for(int h = 1; h <= nhmax; h++){
            for(int j = 0; j < 2; j++){
                kxysum[j] += m_harmcont[h-1][2*j]*m_harmcont[h-1][2*j];
            }
        }
        for(int j = 0; j < 2; j++){
            kxysum[j] = sqrt(kxysum[j]);
        }
        for(int h = 1; h <= nhmax; h++){
            for(int j = 0; j < 2; j++){
                m_Kxy[j][h] = m_K*csn[j]*m_harmcont[h-1][2*j]/kxysum[j];
                m_deltaxy[j][h] = DEGREE2RADIAN*m_harmcont[h-1][2*j+1];
            }
        }
    }
    else{
        for(int j = 0; j < 2; j++){
            m_Kxy[j] = vector<double>{0, m_K*csn[j]};
            m_deltaxy[j] = vector<double>{0, (j-1)*PId2};
            // negative value (j=0) for backward compatibility
        }
    }

    m_exseed = m_select[Seed_][seedprofile_] != NotAvaliable &&
        m_select[Seed_][seedprofile_] != SimplexOutput;

    if(m_exseed){
        m_sigmar = m_prm[Seed_][spotsize_]*1e-3/Sigma2FWHM; // FWFM (mm) -> sigma (m)
    }
}

void SimplexSolver::DeletePointers()
{
    if(*m_srangep != nullptr){
        delete[] m_sranges;
        *m_srangep = nullptr;
    }
    if(*m_onslicep != nullptr){
        delete[] m_onslices;
        *m_onslicep = nullptr;
    }
}

void SimplexSolver::SetUndulatorData(UndulatorFieldData *ufdata, int nseg, int *type)
{
    double K2 = m_K*m_K/2;
    *type = 0; // ideal
    if(find(m_segerr.begin(), m_segerr.end(), nseg) != m_segerr.end()){
        double sigma[NumberUError], sigalloc[NumberUError];
        sigma[UErrorBdevIdx] = m_prm[Und_][berr_]*0.01; // % -> normal
        sigma[UErrorPhaseIdx] = m_prm[Und_][phaseerr_];
        sigma[UErrorXerrorIdx] = m_array[Und_][xyerr_][0]*1.0e-3*m_gamma; // mm -> normalized
        sigma[UErrorYerrorIdx] = m_array[Und_][xyerr_][1]*1.0e-3*m_gamma;

        RandomUtility rand;
        int seed = (int)floor(0.5+m_prm[Und_][umrandseed_]);
        rand_init(m_bool[Und_][umautoseed_], seed, m_procs, m_rank, &rand, m_thread);
        seed = rand.GetSeed();
        ufdata->AllocateUData(m_np, nullptr, m_N, m_lu, K2, m_Kxy, m_deltaxy); // allocate ideal parameters before setting random seed
        ufdata->SetRandomSeed(nseg, &rand, seed, sigma);
        ufdata->AllocateUData(m_np, &rand, m_N, m_lu, K2, m_Kxy, m_deltaxy, sigma, sigalloc);
        *type = 1; // built-in, err
        return;
    }
    else if(find(m_segdata.begin(), m_segdata.end(), nseg) != m_segdata.end()){
        if(m_udata.count(nseg) > 0){
            ufdata->AllocateUData(m_np, m_udata.at(nseg), m_N, m_lu, K2);
            *type = 2; // field data
            return;
        }
    }
    ufdata->AllocateUData(m_np, nullptr, m_N, m_lu, K2, m_Kxy, m_deltaxy);
}

void SimplexSolver::MeausreTime(chrono::system_clock::time_point current[], double time[], int n)
{
    current[1] = chrono::system_clock::now();
    double elapsed = static_cast<double>(chrono::duration_cast<chrono::microseconds>(current[1]-current[0]).count());
    time[n] += elapsed*1e-6;
    current[0] = chrono::system_clock::now();
}

void SimplexSolver::RunPreProcessor(vector<string> &categs, vector<string> &results)
{
    int dimension = 1;
    vector<vector<double>> vararray(1);
    vector<vector<vector<double>>> data(1);
    vector<string> titles, units;

    // lattice optimization results
    double beta0[2], alpha0[2], qgradient[2];
    bool isok = true;

    categs.clear();
    categs.push_back(m_pptype);

    if(m_pptype == PPFDlabel
        || m_pptype == PP1stIntLabel
        || m_pptype == PP2ndIntLabel
        || m_pptype == PPPhaseErrLabel)
    {
        int m, type;
        m = min(max(0, (int)floor(0.5+m_prm[PreP_][targetuseg_])-1), m_M-1);

        UndulatorFieldData ufdata(0);
        SetUndulatorData(&ufdata, m, &type);
        vector<vector<double>> item;

        if(m_pptype == PPPhaseErrLabel){
            data[0].resize(1);
            ufdata.GetPhaseError(vararray[0], data[0][0]);
            titles = vector<string> {ZLabel, PerrLabel};
            units= vector<string>{ZUnit, PerrUnit};
        }
        else{
            data[0].resize(2);
            ufdata.GetFieldIntegralArray(vararray[0], item);
            int jini;
            double coef = 1;
            if(m_pptype == PPFDlabel){
                jini = 0;
                titles = vector<string>{ZLabel, BxLabel, ByLabel};
                units = vector<string>{ZUnit, BUnit, BUnit};
            }
            else if(m_pptype == PP1stIntLabel){
                jini = 2;
                titles = vector<string>{ZLabel, XpLabel, YpLabel};
                units = vector<string>{ZUnit, XYpUnit, XYpUnit};
                coef = 1e3/m_gamma; // rad -> mrad
            }
            else{
                jini = 4;
                titles = vector<string>{ZLabel, XLabel, YLabel};
                units = vector<string>{ZUnit, XYUnit, XYUnit};
                coef = 1e3/m_gamma; // m -> mm
            }
            for(int j = 0; j < 2; j++){
                data[0][j] = item[j+jini];
                data[0][j] *= coef;
            }
        }
        if(!ufdata.IsIdeal()){
            double zorg = ufdata.GetZorigin();
            vararray[0] -= zorg;
        }
    }
    else if(m_pptype == PPKValue || m_pptype == PPDetune)
    {
        double detune, Kr;
        double wakec = f_GetWakefield();

        if(m_pptype == PPKValue){
            titles = vector<string>{ZLabel, KLabel};
        }
        else{
            titles = vector<string>{ZLabel, DetuneLabel};
        }
        units = vector<string>{ZUnit, NoUnit};
        vararray[0].clear();
        data[0].resize(1, vector<double> {});
        for(int n = 0; n < m_totalsteps; n++){
            if(m_pptype == PPKValue && !m_inund[n]){
                continue;
            }
            f_GetKVaried(m_z[n], &detune, &Kr, wakec);
            vararray[0].push_back(m_z[n]);
            if(m_pptype == PPKValue){
                int m = n/(m_segsteps+m_driftsteps);
                data[0][0].push_back(Kr+m_Koffset[m]);
            }
            else{
                data[0][0].push_back(detune);
            }
        }
        if(m_pptype == PPDetune){
            f_ArrangeDetuning(data[0][0]);
        }
    }
    else if(m_pptype == PPWakeBunch || m_pptype == PPWakeEvar)
    {
        ParticleHandler particle(*this);
        WakefieldUtility wake(particle);
        if(m_pptype == PPWakeBunch){
            wake.GetWakeFieldProfiles(titles, vararray[0], data[0]);
            titles.insert(titles.begin(), ZLabel);
            units = vector<string> {ZUnit};
            for(int j = 0; j < data[0].size(); j++){
                units.push_back(WakeUnit);
            }
        }
        else{
            data[0].resize(1);
            titles = vector<string> {EtaLabel, FracLabel};
            units = vector<string>{NoUnit, NoUnit};
            wake.GetEVariation(vararray[0], data[0][0]);
        }
    }
    else if(m_pptype == PPBetaLabel || m_pptype == PPOptBetaLabel)
    {
        titles = vector<string>{ZLabel, BetaxLabel, BetayLabel};
        units = vector<string>{ZUnit, BetaUnit, BetaUnit};
        vector<vector<double>> betaarr(3);
        LatticeOperation lattice(*this);
        if(m_pptype == PPOptBetaLabel){
            if(m_select[PreP_][betamethod_] == PPBetaOptInitial){
                isok = lattice.AdjustInitialCondition(beta0, alpha0);
            }
            else{
                double betatgt[2];
                for(int j = 0; j < 2; j++){
                    betatgt[j] = m_array[PreP_][avbetaxy_][j];
                }
                isok = lattice.OptimizeGradient(betatgt, qgradient, beta0, alpha0);
            }
        }
        if(!isok){
            LatticeOperation latticeini(*this);
            latticeini.TwissParametersAlongz(nullptr, m_betaav, true);
            latticeini.TwissParametersAlongz(&betaarr, nullptr);
        }
        else{
            lattice.TwissParametersAlongz(nullptr, m_betaav, true);
            lattice.TwissParametersAlongz(&betaarr, nullptr);
        }
        vararray[0] = betaarr[0];
        data[0].resize(2);
        for(int j = 0; j < 2; j++){
            data[0][j] = betaarr[j+1];
        }
    }
    else if(m_pptype == PPFocusStrength)
    {
        titles = vector<string>{ZLabel, "k<sub>x</sub>", "k<sub>y</sub>"};
        units = vector<string>{ZUnit, "m<sup>-2</sup>", "m<sup>-2</sup>"};
        data[0].resize(2);
        LatticeOperation lattice(*this);
        lattice.GetFocusingSystem(vararray[0], data[0]);
    }
    else if(m_pptype == PPDispersion)
    {
        titles = vector<string>{ZLabel, "x", "y"};
        units = vector<string>{ZUnit, "mm", "mm"};
        data[0].resize(2);
        LatticeOperation lattice(*this);
        vararray[0] = m_z;
        lattice.GetDispersionArray(data[0]);
        for(int j = 0; j < 2; j++){
            data[0][j] *= 1e3; // m -> mm
        }
    }
    else if(m_pptype == PPMonoSpectrum)
    {
        titles = vector<string>{RelEnergyLabel, RealLabel, ImagLabel, IntensityLabel};
        units = vector<string>{RelEnergyLabel, NoUnit, NoUnit, NoUnit};
        data[0].resize(3);
        double dummy, bw;
        RockingCurve rocking(m_prm[Chicane_]);
        rocking.GetBandWidth(&bw, &dummy);
        double de = 10.0*bw*m_prm[Chicane_][monoenergy_];
        int mesh = max(21, (int)floor(0.5+m_prm[PreP_][plotpoints_]));
        de /= mesh;
        vararray[0].resize(mesh);
        for(int j = 0; j < 3; j++){
            data[0][j].resize(mesh);
        }
        double W, Ew[2];
        for(int n = 0; n < mesh; n++){
            vararray[0][n] = (-(mesh-1)*0.5+n)*de;
            double dlam = -vararray[0][n]/(m_prm[Chicane_][monoenergy_]+vararray[0][n]);
            rocking.GetAmplitudeAsRelLambda(dlam, &W, Ew, m_select[Chicane_][monotype_] == XtalReflecLabel);
            for(int j = 0; j < 2; j++){
                data[0][j][n] = Ew[j];
            }
            data[0][2][n] = hypotsq(Ew[0], Ew[1]);
        }
    }

    string option = "";
    if(m_pptype == PPBetaLabel || (m_pptype == PPOptBetaLabel && isok)){
        string labelav, labelbeta, labelalpha, labelqf, labelqd;
        for(auto iter = PreP.begin(); iter != PreP.end(); iter++){
            int type = get<0>(iter->second);
            string datatype = get<1>(iter->second);
            if(type == avbetaxy_ && datatype == ArrayLabel){
                labelav = iter->first;
            }
            if(type == cbetaxy0_ && datatype == ArrayLabel){
                labelbeta = iter->first;
            }
            if(type == calphaxy0_ && datatype == ArrayLabel){
                labelalpha = iter->first;
            }
            if(type == cqfg_ && datatype == NumberLabel){
                labelqf = iter->first;
            }
            if(type == cqdg_ && datatype == NumberLabel){
                labelqd = iter->first;
            }
        }
        vector<double> betaav {m_betaav[0], m_betaav[1]};
        stringstream ssoption;
        ssoption << "," << endl;
        PrependIndent(JSONIndent, ssoption);
        ssoption << "\"" << RetInfLabel << "\": {" << endl;
        if(m_pptype == PPOptBetaLabel){
            vector<double> vbeta0 {beta0[0], beta0[1]};
            vector<double> valpha0 {alpha0[0], alpha0[1]};
            WriteJSONArray(ssoption, 2*JSONIndent, vbeta0, labelbeta.c_str(), false, true);
            WriteJSONArray(ssoption, 2*JSONIndent, valpha0, labelalpha.c_str(), false, true);
            if(m_select[PreP_][betamethod_] == PPBetaOptQgrad){
                WriteJSONValue(ssoption, 2*JSONIndent, qgradient[0], labelqf.c_str(), false, true);
                if(m_select[Lattice_][ltype_] != FUFULabel){
                    WriteJSONValue(ssoption, 2*JSONIndent, qgradient[1], labelqd.c_str(), false, true);
                }
            }
        }
        WriteJSONArray(ssoption, 2*JSONIndent, betaav, labelav.c_str(), false, false);
        ssoption << endl;
        PrependIndent(JSONIndent, ssoption);
        ssoption << "}";
        option = ssoption.str();
    }

    f_ExportSingle(dimension, titles, units, vararray, data, results, option);
}

void SimplexSolver::RunPreProcessorMB(vector<string> &categs, vector<string> &results)
{
    int particles = (int)m_tE.size();
    vector<double> s(particles), eta(particles);
    bool isng = false;

#ifdef _DEBUG
    ofstream debug_out;
    if(!SolverMBEt.empty()){
        debug_out.open(SolverMBEt);
    }
    vector<string> titles {"s", "E"};
    vector<double> items(titles.size());
    PrintDebugItems(debug_out, titles);
#endif

    for(int n = 0; n < particles; n++){
        s[n] = m_tE[n][0];
        eta[n] = m_tE[n][1];
        if(n > 0){
            if(s[n] < s[n-1]){
                isng = true;
            }
        }
#ifdef _DEBUG
        if(!SolverMBEt.empty()){
            items[0] = s[n];
            items[1] = eta[n];
            PrintDebugItems(debug_out, items);
        }
#endif
    }

#ifdef _DEBUG
    if(!SolverMBEt.empty()){
        debug_out.close();
    }
#endif

    double r56 = m_prm[Mbunch_][mbr56_];
    bool splneed = m_bool[Mbunch_][isoptR56_] || m_bool[Mbunch_][iscurrent_] || m_bool[Mbunch_][isoptR56_];
    if(isng && splneed){
        string msg = "Too large energy modulation.";
        throw runtime_error(msg.c_str());
    }

    EtIntegrator etinteg;
    if(!isng){
        double bunchlen = 0;
        if(m_select[EBeam_][bmprofile_] == GaussianBunch){
            bunchlen = m_prm[EBeam_][bunchleng_];
        }
        etinteg.Set(m_lambda1, m_prm[Mbunch_][mbr56_], m_espread, m_pkcurr, bunchlen, s, eta);
    }

    if(m_bool[Mbunch_][isoptR56_]){
        r56 = etinteg.GetOptimumR56(m_prm[Mbunch_][nr56_]);
    }
    for(int n = 0; n < particles; n++){
        s[n] += m_tE[n][1]*r56;
    }

    vector<double> stmp(particles), etmp(particles);
    int ndump = 0;
    if(m_array[Mbunch_][mbtrange_][1] < m_array[Mbunch_][mbtrange_][0]){
        swap(m_array[Mbunch_][mbtrange_][0], m_array[Mbunch_][mbtrange_][1]);
    }
    for(int n = 0; n < particles; n++){
        if(s[n] >= m_array[Mbunch_][mbtrange_][0] && s[n] <= m_array[Mbunch_][mbtrange_][1]){
            stmp[ndump] = s[n];
            etmp[ndump] = m_tE[n][1];
            ndump++;
        }
    }
    stmp.resize(ndump);
    etmp.resize(ndump);
    f_ExportRefEt(categs, results, stmp, etmp, m_bool[Mbunch_][isoptR56_] ? &r56 : nullptr);

    if(!m_bool[Mbunch_][iscurrent_] && !m_bool[Mbunch_][isEt_]){
        return;
    }

    int partslice = max(2, (int)floor(0.5+m_prm[Mbunch_][tpoints_]));
    double ds = m_lambda1/partslice;
    int ns = (int)floor((m_array[Mbunch_][mbtrange_][1]-m_array[Mbunch_][mbtrange_][0])/ds+0.5)+1;
    s.resize(ns);
    for(int n = 0; n < ns; n++){
        s[n] = m_array[Mbunch_][mbtrange_][0]+n*ds;
    }

    if(m_bool[Mbunch_][iscurrent_]){
        vector<double> I;
        etinteg.GetCurrent(s, I, (int)floor(0.5+m_prm[Mbunch_][mbaccinteg_]));
        f_ExportI(s, I, categs, results);
    }

    if(m_bool[Mbunch_][isEt_]){
        vector<double> eta, j;
        int ne = max(2, (int)floor(0.5+m_prm[Mbunch_][epoints_]));
        eta.resize(ne);
        double de = (m_array[Mbunch_][erange_][1]-m_array[Mbunch_][erange_][0])/(ne-1);
        for(int n = 0; n < ne; n++){
            eta[n] = m_array[Mbunch_][erange_][0]+de*n;
        }
        etinteg.GetParticalCurrent(s, eta, j);
        f_ExportEt(s, eta, j, categs, results);
    }
}

void SimplexSolver::RunSingle(vector<string> &categs, vector<string> &results)
{  
    PrintCalculationStatus status(true, m_rank);
    status.InitializeStatus(3);
    status.SetSubstepNumber(0, 3); // radiation, partice, coupling
    
    vector<vector<double>> beta(3);
    LatticeOperation lattice(*this);
    lattice.TwissParametersAlongz(&beta, m_betaav);
#ifdef _DEBUG 
    // to export dump information
    lattice.TwissParametersAlongz(&beta, nullptr);
#endif
    f_InitGrid(); // should be done after getting m_betaav[]
    if(m_isGauss){
        for(int j = 0; j < 2; j++){
            m_sizexy[j].resize(m_totalsteps);
            for(int n = 0; n < m_totalsteps; n++){
                m_sizexy[j][n] = sqrt(m_emitt[j]*beta[j+1][n]);
            }
        }
    }
    f_SetCouplingFactor(&status, &lattice); // should be done after f_InitGrid()

    ParticleHandler particle(*this, &lattice, &status); // should be done after f_InitGrid()
    if(m_select[EBeam_][bmprofile_] == CustomParticle){
        particle.SetCustomParticles(m_ptmp);
        m_ptmp.clear(); m_ptmp.shrink_to_fit();
    }
    double q2E, ptotal;
    particle.GetParameters(&q2E, &ptotal);

    RadiationHandler radiation(*this, &status);

    status.StartMain();
    status.InitializeStatus(1);

    int psteps = 3*m_totalsteps;
    if(m_bool[Chicane_][chicaneon_]){
        if(m_select[Chicane_][monotype_] == NotAvaliable){
            psteps = 3*(m_totalsteps-m_segsteps+1);
        }
    }
    status.SetSubstepNumber(0, psteps);

    if(m_lasermod){
        for(int n = 0; n < m_totalsteps; n++){
            particle.SetIndex(n);
            radiation.SetSeedField(n);
            radiation.AdvanceParticle(n, &particle, m_F);
        }
        particle.GetParticlesEt(m_tE);
        return;
    }

#ifdef _CPUTIME
    chrono::system_clock::time_point current[2];
    double time[5] = {0, 0, 0, 0, 0};
#endif

    for(int n = 0; n < m_totalsteps; n++){
        if(m_chicane[n] == 0){
            continue;
        }
        else if(m_chicane[n] == 1){
            particle.AdvanceChicane(n); status.AdvanceStep(0);
            radiation.AdvanceChicane(n, &particle, &status);
            radiation.SaveResults(n, &particle, m_F); status.AdvanceStep(0);
            continue;
        }

#ifdef _CPUTIME
        current[0] = chrono::system_clock::now();
#endif

        particle.SetIndex(n);
#ifdef _CPUTIME
        MeausreTime(current, time, 0);
#endif

        radiation.SetBunchFactor(n, &particle); status.AdvanceStep(0);
#ifdef _CPUTIME
        MeausreTime(current, time, 1);
#endif
        radiation.AdvanceField(n, q2E, ptotal, m_F); status.AdvanceStep(0);
#ifdef _CPUTIME
        MeausreTime(current, time, 2);
#endif

        radiation.AdvanceParticle(n, &particle, m_F); status.AdvanceStep(0);
#ifdef _CPUTIME
        MeausreTime(current, time, 3);
#endif

        radiation.SaveResults(n, &particle, m_F);
#ifdef _CPUTIME
        MeausreTime(current, time, 4);
#endif
    }

    vector<vector<double>> pulseE, pdn, pdf, bf;
    radiation.GetGainCurves(pulseE, pdn, pdf, bf);
    vector<double> Eloss, Espread;
    particle.GetEnergyStats(Eloss, Espread);

    m_nhl = vector<string> {"", "-2nd", "-3rd"};
    vector<vector<vector<double>>> data(1);
    vector<string> titles {ZLabel};
    vector<string> units {ZUnit};

    for(int nh = 0; nh < m_nhmax; nh++){
        data[0].push_back(pulseE[nh]);
        if(m_steadystate){
            titles.push_back(RadPowerLabel);
            units.push_back(RadPowerUnit);
        }
        else{
            titles.push_back(PulseEnergyLabel);
            units.push_back(PulseEnergyUnit);
        }
        if(m_nhmax > 1){
            if(nh >= m_nhl.size()){
                m_nhl.push_back("-"+to_string(nh+1)+"th");
            }
            titles.back() += m_nhl[nh];
        }
    }
    for(int nh = 0; nh < m_nhmax; nh++){
        data[0].push_back(pdn[nh]);
        if(m_steadystate){
            titles.push_back(SpatPowerDensLabel);
            units.push_back(SpatPowerDensUnit);
        }
        else{
            titles.push_back(SpatEnergyDensLabel);
            units.push_back(SpatEnergyDensUnit);
        }
        if(m_nhmax > 1){
            titles.back() += m_nhl[nh];
        }
    }
    for(int nh = 0; nh < m_nhmax; nh++){
        data[0].push_back(pdf[nh]);
        if(m_steadystate){
            titles.push_back(AngPowerDensLabel);
            units.push_back(AngPowerDensUnit);
        }
        else{
            titles.push_back(AngEnergyDensLabel);
            units.push_back(AngEnergyDensUnit);
        }
        if(m_nhmax > 1){
            titles.back() += m_nhl[nh];
        }
    }
    for(int nh = 0; nh < m_nhmax; nh++){
        data[0].push_back(bf[nh]);
        titles.push_back(BunchFactorLabel);
        units.push_back(BunchFactorUnit);
        if(m_nhmax > 1){
            titles.back() += m_nhl[nh];
        }
    }
    data[0].push_back(Eloss);
    if(m_steadystate){
        titles.push_back(PLossLabel);
        units.push_back(PLossUnit);
    }
    else{
        titles.push_back(ELossLabel);
        units.push_back(ELossUnit);
    }
    data[0].push_back(Espread);
    titles.push_back(EspreadLabel);
    units.push_back(EspreadUnit);

    if(m_rank > 0){
        return;
    }

#ifdef _CPUTIME
    stringstream ssresult;
    ssresult << "{" << endl;
    WriteJSONValue(ssresult, JSONIndent, time[0], "SetIndex", false, true);
    WriteJSONValue(ssresult, JSONIndent, time[1], "SetBunchFactor", false, true);
    WriteJSONValue(ssresult, JSONIndent, time[2], "AdvanceField", false, true);
    WriteJSONValue(ssresult, JSONIndent, time[3], "AdvanceParticle", false, true);
    WriteJSONValue(ssresult, JSONIndent, time[4], "SaveResults", false, true);
    for(int j = 1; j < 5; j++){
        time[0] += time[j];
    }
    WriteJSONValue(ssresult, JSONIndent, time[0], "Total", false, false);
    ssresult << endl << "}";
    results.push_back(ssresult.str());
    categs.push_back(ElapsedTimeLabel);
    ssresult.str("");
    ssresult.clear(stringstream::goodbit);

    if(m_isGauss){
        vector<vector<double>> kappa;
        radiation.GetBFSize(kappa);
        for(int nh = 0; nh < m_nhmax; nh++){
            data[0].push_back(kappa[nh]);
            titles.push_back("&kappa;");
            units.push_back("-");
            if(m_nhmax > 1){
                titles.back() += m_nhl[nh];
            }
        }
    }
#endif

    vector<vector<double>> vararray{m_z};
    if(m_bool[Chicane_][chicaneon_]){
        f_RemoveInChicane(vararray, data, 1);
    }

    f_ExportCurve(titles, units, vararray, data, results);
    categs.push_back(GainCurveLabel);

    f_ExportCharacteristics(&radiation, categs, results);

    if(m_select[Und_][taper_] != NotAvaliable){
        particle.ExportKValueTrend(categs, results);
    }
    if(m_bool[DataDump_][radiation_] || m_bool[DataDump_][particle_]){
        f_ExportCoordinate(&particle, categs, results);
    }
}

void SimplexSolver::PostProcess(vector<string> &categs, vector<string> &results)
{
    PrintCalculationStatus status(true, m_rank);
    status.InitializeStatus(2);
    status.SetSubstepNumber(0, 3); // radiation, partice, coupling

    vector<vector<double>> beta(3);
    LatticeOperation lattice(*this);
    lattice.TwissParametersAlongz(&beta, m_betaav);
    f_InitGrid();

    vector<string> titles, units;
    vector<vector<double>> vararray;
    vector<vector<vector<double>>> data;
    int variables;

    m_nhpp = (int)floor(0.5+m_prm[PostP_][harmonic_])-1;

    m_oixy = m_select[PostP_][zone_] == PostPFarLabel ? overxyf_ : overxy_;
    m_rixy = m_select[PostP_][zone_] == PostPFarLabel ? anglrange_ : spatrange_;
    if(m_select[PostP_][item_] == PostPBunchFLabel || m_select[PostP_][item_] == PostPEnergyLabel){
        m_oixy = overxy_;
        m_rixy = spatrange_;
        if(m_select[PostP_][item_] == PostPEnergyLabel){
            m_select[PostP_][m_rixy] = PostPIntegFullLabel;
            m_bool[PostP_][m_oixy] = true;
        }
    }
    m_isppalongs = m_bool[PostP_][alongs_];
    m_isppoxy = m_bool[PostP_][m_oixy];
    if(m_select[PostP_][item_] == PostPCampLabel 
            || m_select[PostP_][item_] == PostPPartDistLabel)
    {
        m_isppoxy = false;
    }
    else if(m_select[PostP_][item_] == PostPWignerLabel 
        && m_select[PostP_][domain_] == PostPTimeDomainLabel)
    {
        m_isppoxy = true;
    }

    status.StartMain();
    if(m_select[PostP_][item_] == PostPPartDistLabel 
            || m_select[PostP_][item_] == PostPBunchFLabel
            || m_select[PostP_][item_] == PostPEnergyLabel){
        ParticleHandler particle(*this, &lattice, &status);
        particle.DoPostProcess(&status, titles, units, &variables, vararray, data);
    }
    else{
        RadiationHandler radiation(*this, &status);
        radiation.DoPostProcess(&status, titles, units, &variables, vararray, data);
    }

    int dimension = (int)vararray.size();
    for(int n = dimension-1; n >= 0; n--){
        if(vararray[n].size() < 2){
            titles.erase(titles.begin()+n);
            units.erase(units.begin()+n);
            vararray.erase(vararray.begin()+n);
            dimension--;
            if(n < variables){
                variables--;
            }
        }
    }

    stringstream ssresult;
    ssresult << "{" << endl;

    string scatter;
    int fdim = 1;
    if(m_select[PostP_][item_] == PostPPartDistLabel){
        scatter = "true";
        dimension = (int)titles.size()-variables-1;
        if(variables > 0){
            fdim = dimension+1;
        }
        else{
            int ndata = (int)data[0][0].size()/(dimension+1);
            vararray.resize(dimension);
            for(int j = 0; j < dimension; j++){
                vararray[j].resize(ndata);
                copy(data[0][0].begin()+j*ndata, data[0][0].begin()+(j+1)*ndata, vararray[j].begin());
            }
            vector<double> dcopy(ndata);
            copy(data[0][0].begin()+dimension*ndata, data[0][0].begin()+(dimension+1)*ndata, dcopy.begin());
            data[0][0] = dcopy;
        }
    }
    else{
        variables = max(1, variables);
        scatter = "false";
    }

    WriteJSONValue(ssresult, JSONIndent, dimension, DataDimLabel.c_str(), false, true);
    if(variables > 0){
        WriteJSONValue(ssresult, JSONIndent, variables, VariablesLabel.c_str(), false, true);
    }
    WriteJSONArray(ssresult, JSONIndent, titles, DataTitlesLabel.c_str(), true, true);
    WriteJSONArray(ssresult, JSONIndent, units, UnitsLabel.c_str(), true, true);
    WriteJSONValue(ssresult, JSONIndent, scatter, PlotScatterLabel.c_str(), false, true);

    PrependIndent(JSONIndent, ssresult);
    ssresult << "\"" << DataLabel << "\": [" << endl;

    int delmesh = -1;
    if(dimension == 2){
        delmesh = (int)vararray[0].size();
    }
    else if(dimension >= 3){
        delmesh = (int)(vararray[0].size()*vararray[1].size());
    }
    ExportData(ssresult, 1, dimension, (int)data[0].size(), (int)data.size(), delmesh, delmesh > 0, vararray, data, fdim);

    PrependIndent(JSONIndent, ssresult);
    ssresult << "]";

    ssresult << endl << "}";

    results.push_back(ssresult.str());
    categs.push_back(PostPResultLabel);
}

// private functions for export data
void SimplexSolver::f_RemoveInChicane(vector<vector<double>> &vararray, vector<vector<vector<double>>> &data, int dim)
{
    for(int n = m_totalsteps-1; n >= 0; n--){
        if(m_chicane[n] == 0){
            vararray.back().erase(vararray.back().begin()+n);
            if(dim == 1){
                for(int i = 0; i < data[0].size(); i++){
                    data[0][i].erase(data[0][i].begin()+n);
                }
            }
            else{
                data.erase(data.begin()+n);
            }
        }
    }
}

void SimplexSolver::f_SkipStep(vector<vector<double>> &vararray, vector<vector<vector<double>>> &data, int dim)
{
    int dn = (int)floor(0.5+m_prm[DataDump_][profstep_])-1;
    if(dn < 1){
        return;
    }
    int n = (int)vararray.back().size()-1;
    do{
        int ni = max(0, n-dn);
        vararray.back().erase(vararray.back().begin()+ni, vararray.back().begin()+n);
        if(dim == 1){
            for(int i = 0; i < data[0].size(); i++){
                data[0][i].erase(data[0][i].begin()+ni, data[0][i].begin()+n);
            }
        }
        else{
            data.erase(data.begin()+ni, data.begin()+n);
        }
        n -= dn+1;
    } while(n > 0);
}

void SimplexSolver::f_ExportCurve(vector<string> &titles, vector<string> &units, 
    vector<vector<double>> &vararray, vector<vector<vector<double>>> &data, vector<string> &results)
{
    stringstream ssresult;

    ssresult << "{" << endl;

    int dim = 1;
    WriteJSONValue(ssresult, JSONIndent, dim, DataDimLabel.c_str(), false, true);
    WriteJSONArray(ssresult, JSONIndent, titles, DataTitlesLabel.c_str(), true, true);
    WriteJSONArray(ssresult, JSONIndent, units, UnitsLabel.c_str(), true, true);

    PrependIndent(JSONIndent, ssresult);
    ssresult << "\"" << DataLabel << "\": [" << endl;

    ExportData(ssresult, 1, 1, (int)data[0].size(), 1, -1, false, vararray, data);

    PrependIndent(JSONIndent, ssresult);
    ssresult << "]";

    ssresult << endl << "}";

    results.push_back(ssresult.str());
}

void SimplexSolver::f_ExportCharacteristics(RadiationHandler *radiation, vector<string> &categs, vector<string> &results)
{
    vector<vector<double>> vararray(1);
    vector<vector<vector<double>>> data(1);
    vector<string> titles{ZLabel};
    vector<string> units{ZUnit};

    radiation->GetZProfiles(vararray[0]);
    if(vararray[0].size() < 1){
        return;
    }

    vector<vector<double>> ws(m_nhmax*2);
    for(int nh = 0; nh < m_nhmax*2; nh++){
        ws[nh].resize(vararray[0].size());
    }
    int dimension = 1;
    if(m_bool[DataDump_][temporal_]){
        f_ExportTemporal(radiation, categs, results, ws);
        for(int nh = 0; nh < m_nhmax && m_steadystate == false; nh++){
            titles.push_back(PulselengthLabel);
            units.push_back(PulselengthUnit);
            if(m_nhmax > 1){
                titles.back() += m_nhl[nh];
            }
            data[0].push_back(ws[nh]);
        }
    }
    if(m_bool[DataDump_][spectral_]){
        f_ExportSpectrum(radiation, categs, results, ws);
        for(int nh = 0; nh < m_nhmax && m_steadystate == false; nh++){
            titles.push_back(BandwidthLabel);
            units.push_back(BandwidthUnit);
            if(m_nhmax > 1){
                titles.back() += m_nhl[nh];
            }
            data[0].push_back(ws[nh]);
        }
    }

    vector<vector<double>> size(2*m_nhmax);
    if(m_bool[DataDump_][spatial_]){
        f_ExportSpatial(radiation, 1, categs, results, ws);
        for(int nh = 0; nh < m_nhmax && m_steadystate == false; nh++){
            titles.push_back(BeamSizeX);
            units.push_back(BeamSizeUnit);
            if(m_nhmax > 1){
                titles.back() += m_nhl[nh];
            }
            titles.push_back(BeamSizeY);
            units.push_back(BeamSizeUnit);
            if(m_nhmax > 1){
                titles.back() += m_nhl[nh];
            }
            data[0].push_back(ws[2*nh]);
            data[0].push_back(ws[2*nh+1]);
            if(m_bool[DataDump_][angular_]){
                size[2*nh] = ws[2*nh];
                size[2*nh+1] = ws[2*nh+1];
            }
        }
    }
    if(m_bool[DataDump_][angular_]){
        f_ExportSpatial(radiation, 0, categs, results, ws);
        vector<vector<double>> curvature;
        radiation->GetCurvature(curvature);

        for(int nh = 0; nh < m_nhmax && m_steadystate == false; nh++){
            titles.push_back(DivergenceX);
            units.push_back(DivergenceUnit);
            if(m_nhmax > 1){
                titles.back() += m_nhl[nh];
            }
            titles.push_back(DivergenceY);
            units.push_back(DivergenceUnit);
            if(m_nhmax > 1){
                titles.back() += m_nhl[nh];
            }
            data[0].push_back(ws[2*nh]);
            data[0].push_back(ws[2*nh+1]);
            if(m_bool[DataDump_][spatial_]){
                titles.push_back(CurvatureLabel);
                units.push_back(CurvatureUnit);
                if(m_nhmax > 1){
                    titles.back() += m_nhl[nh];
                }
                vector<double> curv(vararray[0].size());
                for(int n = 0; n < vararray[0].size(); n++){
                    double X = ws[2*nh  ][n]/size[2*nh  ][n]; X *= X;
                    double Y = ws[2*nh+1][n]/size[2*nh+1][n]; Y *= Y;
                    double XpY = X+Y;
                    double XY = X*Y;
                    double eta2 = 1/(curvature[nh][n]*curvature[nh][n]);
                    curv[n] = (XpY-sqrt(XpY*XpY-4*(1-eta2)*XY))/2/XY;
                    curv[n] = sqrt(max(0.0, curv[n]));
                }
                data[0].push_back(curv);
            }            
        }
    }
    if(titles.size() > 1){
        f_ExportCurve(titles, units, vararray, data, results);
        categs.push_back(RadCharactLabel);
    }
}

void SimplexSolver::f_ExportTemporal(RadiationHandler *radiation, vector<string> &categs, vector<string> &results, vector<vector<double>> &plen)
{
    vector<vector<vector<double>>> Pinst;
    radiation->GetTemporal(Pinst);
    vector<double> zprof;
    radiation->GetZProfiles(zprof);

    double area, mean, peak, stdpk;
    for(int nh = 0; nh < m_nhmax; nh++){
        for(int n = 0; n < zprof.size(); n++){
            FunctionStatistics fstats(m_slices, &m_s, &Pinst[n][nh]);
            fstats.GetStatistics(&area, &mean, &peak, &plen[nh][n], &stdpk, 0, false);
        }
    }

    // temporal profile
    vector<double> s_mm = m_s;
    s_mm *= 1000.0;  // m -> mm

    vector<string> titles{SLabel, ZLabel};
    vector<string> units{SUnit, ZUnit};
    for(int nh = 0; nh < m_nhmax; nh++){
        titles.push_back(RadPowerLabel);
        units.push_back(RadPowerUnit);
        if(m_nhmax > 1){
            titles.back() += m_nhl[nh];
        }
    }

    vector<vector<double>> vararray {s_mm, zprof};
    stringstream ssresult;

    ssresult << "{" << endl;

    int variables = 1;
    int dimension = 2;
    WriteJSONValue(ssresult, JSONIndent, dimension, DataDimLabel.c_str(), false, true);
    WriteJSONValue(ssresult, JSONIndent, variables, VariablesLabel.c_str(), false, true);
    WriteJSONArray(ssresult, JSONIndent, titles, DataTitlesLabel.c_str(), true, true);
    WriteJSONArray(ssresult, JSONIndent, units, UnitsLabel.c_str(), true, true);

    PrependIndent(JSONIndent, ssresult);
    ssresult << "\"" << DataLabel << "\": [" << endl;

    ExportData(ssresult, 1, dimension, m_nhmax, (int)vararray.back().size(), m_slices, true, vararray, Pinst);

    PrependIndent(JSONIndent, ssresult);
    ssresult << "]";

    ssresult << endl << "}";

    results.push_back(ssresult.str());
    categs.push_back(TempProfileLabel);
}

void SimplexSolver::f_ExportSpectrum(
    RadiationHandler *radiation, vector<string> &categs, vector<string> &results, vector<vector<double>> &bw)
{
    vector<double> ep;
    vector<vector<vector<double>>> Flux;

    radiation->GetSpectrum(ep, Flux);
    vector<double> zprof;
    radiation->GetZProfiles(zprof);

    int nep = (int)ep.size();
    double area, mean, peak, stdpk;
    double e1st = wave_length(m_lambda1);
    for(int nh = 0; nh < m_nhmax; nh++){
        for(int n = 0; n < zprof.size(); n++){
            FunctionStatistics fstats(nep, &ep, &Flux[n][nh]);
            fstats.GetStatistics(&area, &mean, &peak, &bw[nh][n], &stdpk, 0, false);
            bw[nh][n] /= e1st*(nh+1);
        }
    }

    vector<string> titles{PhotonELabel, ZLabel};
    if(m_nhmax > 1){
        titles[0] = RelEnergyLabel;
    }
    vector<string> units{PhotonEUnit, ZUnit};
    for(int nh = 0; nh < m_nhmax; nh++){
        titles.push_back(RadFluxLabel);
        units.push_back(RadFluxUnit);
        if(m_nhmax > 1){
            titles.back() += m_nhl[nh];
        }
    }

    vector<vector<double>> vararray{ep, zprof};
    stringstream ssresult;

    ssresult << "{" << endl;

    int variables = 1;
    int dimension = 2;
    WriteJSONValue(ssresult, JSONIndent, dimension, DataDimLabel.c_str(), false, true);
    WriteJSONValue(ssresult, JSONIndent, variables, VariablesLabel.c_str(), false, true);
    WriteJSONArray(ssresult, JSONIndent, titles, DataTitlesLabel.c_str(), true, true);
    WriteJSONArray(ssresult, JSONIndent, units, UnitsLabel.c_str(), true, true);

    PrependIndent(JSONIndent, ssresult);
    ssresult << "\"" << DataLabel << "\": [" << endl;

    ExportData(ssresult, 1, dimension, m_nhmax, (int)vararray.back().size(), m_slices, true, vararray, Flux);

    PrependIndent(JSONIndent, ssresult);
    ssresult << "]";

    ssresult << endl << "}";
    results.push_back(ssresult.str());
    categs.push_back(SpecProfileLabel);
}

void SimplexSolver::f_ExportSpatial(
    RadiationHandler *radiation, int jnf, vector<string> &categs, vector<string> &results, vector<vector<double>> &sxy)
{
    vector<vector<double>> vararray(2);
    vector<vector<vector<double>>> Pd;
    radiation->GetSpatialProfile(jnf, vararray, Pd);
    vector<double> zprof;
    radiation->GetZProfiles(zprof);

    int kl[2], nsize[2];
    vector<double> values[2];
    double area, mean, peak,  stdpk;
    for(int j = 0; j < 2; j++){
        nsize[j] = (int)vararray[j].size();
        values[j].resize(vararray[j].size());
    }
    for(int n = 0; n < zprof.size(); n++){
        for(int nh = 0; nh < m_nhmax; nh++){
            for(int j = 0; j < 2; j++){
                for(kl[j] = 0; kl[j] < nsize[j]; kl[j]++){
                    values[j][kl[j]] = 0;
                    for(kl[1-j] = 0; kl[1-j] < nsize[1-j]; kl[1-j]++){
                        int index = kl[1]*nsize[0]+kl[0];
                        values[j][kl[j]] += Pd[n][nh][index];
                    }
                }
                FunctionStatistics fstats(nsize[j], &vararray[j], &values[j]);
                fstats.GetStatistics(&area, &mean, &peak, &sxy[2*nh+j][n], &stdpk, 0, false);
                sxy[2*nh+j][n] /= nh+1;
            }
        }
    }

    vector<string> titles{XLabel, YLabel, ZLabel};
    vector<string> units{XYUnit, XYUnit, ZUnit};
    if(jnf == 0){
        titles[0] = hQxLabel;
        titles[1] = hQyLabel;
        units[0] = XYpUnit;
        units[1] = XYpUnit;
    }
    for(int nh = 0; nh < m_nhmax; nh++){
        if(jnf == 0){
            titles.push_back(AngEnergyDensLabel);
            units.push_back(AngEnergyDensUnit);
        }
        else{
            titles.push_back(SpatEnergyDensLabel);
            units.push_back(SpatEnergyDensUnit);
        }
        if(m_nhmax > 1){
            titles.back() += m_nhl[nh];
        }
    }
    vararray.push_back(zprof);

    stringstream ssresult;
    ssresult << "{" << endl;

    int variables = 2;
    int dimension = 3;
    WriteJSONValue(ssresult, JSONIndent, dimension, DataDimLabel.c_str(), false, true);
    WriteJSONValue(ssresult, JSONIndent, variables, VariablesLabel.c_str(), false, true);
    WriteJSONArray(ssresult, JSONIndent, titles, DataTitlesLabel.c_str(), true, true);
    WriteJSONArray(ssresult, JSONIndent, units, UnitsLabel.c_str(), true, true);

    PrependIndent(JSONIndent, ssresult);
    ssresult << "\"" << DataLabel << "\": [" << endl;

    ExportData(ssresult, 1, dimension, m_nhmax, (int)vararray.back().size(), (m_nfft[0]+1)*(m_nfft[1]+1), true, vararray, Pd);

    PrependIndent(JSONIndent, ssresult);
    ssresult << "]";

    ssresult << endl << "}";
    results.push_back(ssresult.str());
    if(jnf == 0){
        categs.push_back(AnglProfileLabel);
    }
    else{
        categs.push_back(SpatProfileLabel);
    }
}

void SimplexSolver::f_ExportCoordinate(ParticleHandler *particle, vector<string> &categs, vector<string> &results)
{
    stringstream ssresult;
    ssresult << "{" << endl;

    vector<double> xy(4), emitt(2);
    vector<int> nfft(2);
    for(int j = 0; j < 2; j++){
        xy[j] = m_dxy[j];
        xy[j+2] = m_qxy[j];
        nfft[j] = m_nfft[j];
        emitt[j] = m_emitt[j]*m_gamma*1e6;
    }
    size_t beamlets = particle->GetBeamlets();
    int particles = particle->GetParticles();
    double charge = particle->GetCharge();
    double e1st = photon_energy(m_lambda1);

    WriteJSONArray(ssresult, JSONIndent, m_exporsteps, StepIndexLabel.c_str(), false, true);
    WriteJSONArray(ssresult, JSONIndent, m_exportz, StepCoordLabel.c_str(), false, true);
    WriteJSONArray(ssresult, JSONIndent, m_s, SliceCoordLabel.c_str(), false, true);
    WriteJSONArray(ssresult, JSONIndent, xy, XYCoordLabel.c_str(), false, true);
    WriteJSONArray(ssresult, JSONIndent, nfft, XYPointsLabel.c_str(), false, true);
    WriteJSONValue(ssresult, JSONIndent, beamlets, BeamletsLabel.c_str(), false, true);
    WriteJSONValue(ssresult, JSONIndent, particles, ParticlesLabel.c_str(), false, true);

    WriteJSONValue(ssresult, JSONIndent, m_eGeV, AvgEnergyLabel.c_str(), false, true);
    WriteJSONValue(ssresult, JSONIndent, m_espread, SliceEspreadLabel.c_str(), false, true);
    WriteJSONValue(ssresult, JSONIndent, m_pkcurr, PeakCurrLabel.c_str(), false, true);
    WriteJSONArray(ssresult, JSONIndent, emitt, SliceEmittanceLabel.c_str(), false, true);
    WriteJSONValue(ssresult, JSONIndent, charge, SimulatedChargeLabel.c_str(), false, true);
    WriteJSONValue(ssresult, JSONIndent, m_totalsteps, TotalStepsLabel.c_str(), false, true);
    WriteJSONValue(ssresult, JSONIndent, e1st, CentralEnergyLabel.c_str(), false, false);

    ssresult << endl << "}";
    results.push_back(ssresult.str());
    categs.push_back(CoordinateLabel);
}

void SimplexSolver::f_ExportSingle(int dimension, vector<string> &titles, vector<string> &units,
    vector<vector<double>> &vararray, vector<vector<vector<double>>> &data, vector<string> &results, string options)
{
    stringstream ssresult;
    ssresult << "{" << endl;

    WriteJSONValue(ssresult, JSONIndent, dimension, DataDimLabel.c_str(), false, true);
    WriteJSONArray(ssresult, JSONIndent, titles, DataTitlesLabel.c_str(), true, true);
    WriteJSONArray(ssresult, JSONIndent, units, UnitsLabel.c_str(), true, true);

    PrependIndent(JSONIndent, ssresult);
    ssresult << "\"" << DataLabel << "\": [" << endl;

    int delmesh = -1;
    if(dimension > 1){
        delmesh = (int)vararray[0].size();
    }

    ExportData(ssresult, 1, dimension, (int)data[0].size(), 1, delmesh, false, vararray, data);

    PrependIndent(JSONIndent, ssresult);
    ssresult << "]";

    if(!options.empty()){
        ssresult << options;
    }

    ssresult << endl << "}";

    results.push_back(ssresult.str());
}

bool SimplexSolver::f_IsExportDebug(int n, int rank)
{
    for(int i = 0; i < ExportSteps.size(); i++){
        if(n == ExportSteps[i]){
            return true;
        }
    }
    return m_steadystate || (n < 0 && rank == 0);
}

void SimplexSolver::f_ExportRefEt(vector<string> &categs, vector<string> &results, 
    vector<double> &s, vector<double> &eta, double *r56)
{
    vector<string> titles {SLabel, EtaLabel};
    vector<string> units {SUnit, NoUnit};
    vector<vector<double>> vararray(1);
    vector<vector<vector<double>>> data(1);

    vararray[0] = s;
    vararray[0] *= 1e3; // m -> mm
    data[0].push_back(eta);

    string option = "";
    if(r56 != nullptr){
        stringstream ssoption;
        ssoption << "," << endl;
        PrependIndent(JSONIndent, ssoption);
        ssoption << "\"" << RetInfLabel << "\": {" << endl;

        string labelr56;
        for(auto iter = Mbunch.begin(); iter != Mbunch.end(); iter++){
            int type = get<0>(iter->second);
            string datatype = get<1>(iter->second);
            if(type == mbr56_ && datatype == NumberLabel){
                labelr56 = iter->first;
            }
        }
        WriteJSONValue(ssoption, 2*JSONIndent, *r56, labelr56.c_str(), false, false);
        ssoption << endl;
        PrependIndent(JSONIndent, ssoption);
        ssoption << "}";
        option = ssoption.str();
    }

    f_ExportSingle(1, titles, units, vararray, data, results, option);
    categs.push_back(EtDistLabel);
}

void SimplexSolver::f_ExportI(vector<double> &s, 
    vector<double> &I, vector<string> &categs, vector<string> &results)
{
    vector<string> titles{SLabel, CurrLabel};
    vector<string> units{SUnit, CurrUnit};
    vector<vector<double>> vararray(1);
    vector<vector<vector<double>>> data(1);
    stringstream ssresult;

    vararray[0] = s;
    vararray[0] *= 1e3; // m -> mm
    data[0].resize(1);
    data[0][0] = I;

    f_ExportSingle(1, titles, units, vararray, data, results);
    categs.push_back(CurrentProfLabel);
}

void SimplexSolver::f_ExportEt(vector<double> &s, vector<double> &eta, 
    vector<double> &j, vector<string> &categs, vector<string> &results)
{
    vector<string> titles{SLabel, EtaLabel, PartialCurrLabel};
    vector<string> units{SUnit, NoUnit, PartialCurrUnit};
    vector<vector<double>> vararray(2);
    vector<vector<vector<double>>> data(1);
    stringstream ssresult;

    vararray[0] = s;
    vararray[0] *= 1e3; // m -> mm
    vararray[1] = eta;
    data[0].resize(1);
    data[0][0] = j;
    f_ExportSingle(2, titles, units, vararray, data, results);
    categs.push_back(EtProfLabel);
}

// private functions
double SimplexSolver::f_GetSaturationPower(double beta, double emitt, double *Lg3d)
{
    double rho = rho_fel_param_1D(m_pkcurr, m_lu, m_K, m_Kphi, beta, emitt, m_gamma);
    double Lg1d = m_lu/PI/4.0/sqrt(3.0)/rho;
    double eta = scaling_fel3d_eta(m_lambda1, Lg1d, beta, emitt, m_lu, m_espread);
    if(Lg3d != nullptr){
        *Lg3d = Lg1d*(1.0+eta);
    }
    return 1.6*m_pkcurr*m_eGeV*rho/(1.0+eta)/(1.0+eta);
}

void SimplexSolver::f_OptimizeBeta()
{
    double incrf = SQRT2;
    double emitt = sqrt(m_emitt[0]*m_emitt[1]);

    double betaorg = 10;
    vector<double> betaavr, psatr;

    double betatest = betaorg;
    betaavr.push_back(betatest);
    psatr.push_back(f_GetSaturationPower(betatest, emitt));

    do {
        betatest *= incrf;
        betaavr.push_back(betatest);
        psatr.push_back(f_GetSaturationPower(betatest, emitt));
    } while(psatr[psatr.size()-1] >= psatr[psatr.size()-2]);

    int center;
    if(psatr.size() >= 3){
        center = (int)psatr.size()-2;
    }
    else{
        betatest = betaorg;
        do {
            betatest /= incrf;
            betaavr.insert(betaavr.begin(), betatest);
            psatr.insert(psatr.begin(), f_GetSaturationPower(betatest, emitt));
        } while(psatr[0] >= psatr[1]);
        center = 1;
    }
    parabloic_peak(&m_betaopt, 
        betaavr[center-1], betaavr[center], betaavr[center+1], 
        psatr[center-1], psatr[center], psatr[center+1]);
}


void SimplexSolver::f_InitGaussian()
{
    m_pkcurr = m_prm[EBeam_][bunchcharge_]*1e-9/(m_prm[EBeam_][bunchleng_]*SQRTPI2/CC);
    m_espread = m_prm[EBeam_][espread_];
    f_InitCommon();
}

void SimplexSolver::f_InitBoxcar()
{
    m_pkcurr = m_prm[EBeam_][bunchcharge_]*1e-9/(m_prm[EBeam_][bunchlenr_]/CC);
    m_espread = m_prm[EBeam_][espread_];
    f_InitCommon();
}

void SimplexSolver::f_InitCustomCurr()
{
    vector<double> Iprf;
    m_currprof.GetArray1D(1, &Iprf);
    m_pkcurr = minmax(Iprf, true);
    m_espread = m_prm[EBeam_][espread_];
    f_InitCommon();
}

void SimplexSolver::f_InitCustomEt()
{
    vector<double> Iprf, etaprf, jprf;
    m_Etprf.GetProjection(0, 0, &Iprf);
    double Imax = 0;
    int nmax = 0;
    for(int n = 0; n < Iprf.size(); n++){
        if(Imax < Iprf[n]){
            nmax = n;
        }
    }
    m_Etprf.GetVariable(1, &etaprf);
    m_Etprf.Slice2D(0, nmax, &jprf);
    m_pkcurr = vectorsum(jprf, (int)jprf.size())*(etaprf[1]-etaprf[0]);

    f_InitCommon();
}

void SimplexSolver::f_InitCommon()
{
    m_eGeV = m_prm[EBeam_][eenergy_];
    m_gamma = m_eGeV*1e3/MC2MeV;
    for(int j = 0; j < 2; j++){
        m_emitt[j] = m_array[EBeam_][emitt_][j]*1e-6/m_gamma;
    }
    m_lambda1 = m_lu*(1+m_K*m_K/2)/2/m_gamma/m_gamma;

    double emitt = sqrt(m_emitt[0]*m_emitt[1]);
    f_OptimizeBeta();
    f_GetSaturationPower(m_betaopt, emitt, &m_Lg3d);
}

void SimplexSolver::f_InitCustomSlice()
{
    int nslices = m_slice.GetSize();
    vector<double> pos, curr, energy, espread, emitt[2], beta[2], alpha[2], chn(nslices, 0);

    m_slice.GetArray1D(SliceIndex.at(SliceLabel), &pos);
    m_slice.GetArray1D(SliceIndex.at(CurrentLabel), &curr);
    m_slice.GetArray1D(SliceIndex.at(EnergyLabel), &energy);
    m_slice.GetArray1D(SliceIndex.at(EspLabel), &espread);
    m_slice.GetArray1D(SliceIndex.at(EmittxLabel), &emitt[0]);
    m_slice.GetArray1D(SliceIndex.at(EmittyLabel), &emitt[1]);
    m_slice.GetArray1D(SliceIndex.at(BetaxLabel), &beta[0]);
    m_slice.GetArray1D(SliceIndex.at(BetayLabel), &beta[1]);
    m_slice.GetArray1D(SliceIndex.at(AlphaxLabel), &alpha[0]);
    m_slice.GetArray1D(SliceIndex.at(AlphayLabel), &alpha[1]);

    int npeak = 0;
    double pmax = 0, Lg3d, charge = 0, betasim[] = {0, 0}, alphasim[] = {0, 0};
    for(int ns = 0; ns < nslices; ns++){
        if(curr[ns] <= 0 || emitt[0][ns] <= 0 || emitt[1][ns] <= 0){
            continue;
        }
        if(ns > 0){
            double chn = (curr[ns]+curr[ns-1])*(pos[ns]-pos[ns-1])/2;
            charge += chn;
            for(int j = 0; j < 2; j++){
                betasim[j] += (beta[j][ns]+beta[j][ns-1])/2*chn;
                alphasim[j] += (alpha[j][ns]+alpha[j][ns-1])/2*chn;
            }
        }
        m_pkcurr = curr[ns];
        m_espread = espread[ns];
        m_eGeV = energy[ns];
        m_gamma = m_eGeV*1e3/MC2MeV;
        for(int j = 0; j < 2; j++){
            m_emitt[j] = emitt[j][ns]*1e-6/m_gamma;
        }
        m_lambda1 = m_lu*(1+m_K*m_K/2)/2/m_gamma/m_gamma;
        f_OptimizeBeta();
        double psat = f_GetSaturationPower(m_betaopt, sqrt(m_emitt[0]*m_emitt[1]), &Lg3d);
        if(psat > pmax){
            pmax = psat;
            npeak = ns;
        }
    }
    for(int j = 0; j < 2; j++){
        betasim[j] /= charge;
        alphasim[j] /= charge;
    }

    m_pkcurr = curr[npeak];
    m_espread = espread[npeak];

    m_eGeV = energy[npeak];
    m_gamma = m_eGeV*1e3/MC2MeV;
    for(int j = 0; j < 2; j++){
        m_emitt[j] = emitt[j][npeak]*1e-6/m_gamma;
    }
    m_lambda1 = m_lu*(1+m_K*m_K/2)/2/m_gamma/m_gamma;

    f_OptimizeBeta();
    f_GetSaturationPower(m_betaopt, sqrt(m_emitt[0]*m_emitt[1]), &m_Lg3d);

    if(m_select[EBeam_][twissbunch_] == SlicedPrmOptimize){
        for(int j = 0; j < 2; j++){
            betasim[j] = beta[j][npeak];
            alphasim[j] = alpha[j][npeak];
        }
    }
    else if(m_select[EBeam_][twissbunch_] == SlicedPrmCustom){
        int ns = min((int)pos.size()-2, SearchIndex((int)pos.size(), false, pos, m_prm[EBeam_][twisspos_]));
        double ds = (m_prm[EBeam_][twisspos_]-pos[ns])/(pos[ns+1]-pos[ns]);
        for(int j = 0; j < 2; j++){
            betasim[j] = beta[j][ns]*(1-ds)+beta[j][ns+1]*ds;
            alphasim[j] = alpha[j][ns]*(1-ds)+alpha[j][ns+1]*ds;
        }
    }

    for(int j = 0; j < 2; j++){
        m_uB[j] = sqrt(m_array[Lattice_][betaxy0_][j]/betasim[j]);
        m_uA[j] = (alphasim[j]-m_array[Lattice_][alphaxy0_][j])/sqrt(betasim[j]*m_array[Lattice_][betaxy0_][j]);
    }
}

void SimplexSolver::f_InitCustomParticle()
{
    string input;
    LoadFile(m_rank, m_procs, m_string[EBeam_][partfile_], input, m_thread);

    vector<string> lines, items;
    int nlines = separate_items(input, lines, "\n\r");

    double partline[6];

    int index[] = {
        (int)floor(0.5+m_prm[PartFmt_][colx_]),
        (int)floor(0.5+m_prm[PartFmt_][colxp_]),
        (int)floor(0.5+m_prm[PartFmt_][coly_]),
        (int)floor(0.5+m_prm[PartFmt_][colyp_]),
        (int)floor(0.5+m_prm[PartFmt_][colt_]),
        (int)floor(0.5+m_prm[PartFmt_][colE_])
    };
    double units[] = {1, 1, 1, 1, 1, 1};
    if(m_select[PartFmt_][unitxy_] == UnitMiliMeter){
        units[0] = units[2] = 1e-3;
    }
    if(m_select[PartFmt_][unitxyp_] == UnitMiliRad){
        units[1] = units[3] = 1e-3;
    }
    if(m_select[PartFmt_][unitt_] == UnitSec){
        units[4] = -CC;
    }
    else if(m_select[PartFmt_][unitt_] == UnitpSec){
        units[4] = -1e-12*CC;
    }
    else if(m_select[PartFmt_][unitt_] == UnitfSec){
        units[4] = -1e-15*CC;
    }
    else if(m_select[PartFmt_][unitt_] == UnitMiliMeter){
        units[4] = 1e-3;
    }
    if(m_select[PartFmt_][unitE_] == UnitMeV){
        units[5] = 1e-3;
    }
    else if(m_select[PartFmt_][unitE_] == UnitGamma){
        units[5] = 1e-3*MC2MeV;
    }

    m_ptmp.resize(6);
    for(int j = 0; j < 6; j++){
        m_ptmp[j].resize(nlines, 0.0);
    }
    int particles = 0;
    char *endptr;
    for(int n = 0; n < nlines; n++){
        if(separate_items(lines[n], items) < 6){
            continue;
        }
        for(int j = 0; j < 6; j++){
            partline[j] = strtod(items[j].c_str(), &endptr);
            if(*endptr != '\0'){
                break;
            }
        }
        if(*endptr != '\0'){
            continue;
        }
        for(int j = 0; j < 6; j++){
            m_ptmp[j][particles] = units[j]*partline[index[j]-1];
        }
        particles++;
    }
    if(particles < MinimumParticles){
        string msg = "Too few particles (more than "+to_string(MinimumParticles)+" particles needed).";
        throw runtime_error(msg.c_str());
    }

    for(int j = 0; j < 6; j++){
        m_ptmp[j].resize(particles);
    }

    double sav = 0, smin, smax;
    for(int n = 0; n < particles; n++){
        sav += m_ptmp[4][n];
        if(n == 0){
            smin = m_ptmp[4][n];
            smax = m_ptmp[4][n];
        }
        else{
            smin = min(smin, m_ptmp[4][n]);
            smax = max(smax, m_ptmp[4][n]);
        }
    }
    sav /= particles;
    double ssigma = 0;
    for(int n = 0; n < particles; n++){
        m_ptmp[4][n] -= sav; // eliminate time offset for all particles
        ssigma += m_ptmp[4][n]*m_ptmp[4][n];
    }
    ssigma = sqrt(ssigma/particles);
    smin -= sav;
    smax -= sav;

    double slicelen = ssigma/m_prm[PartFmt_][bins_];
    int nsrange[] = {(int)floor(smin/slicelen+0.5), (int)floor(smax/slicelen+0.5)};
    int slices = nsrange[1]-nsrange[0]+1;

    vector<double> slice_avg[6], slice_sq[6], slice_corr[2];
    vector<int> slice_particles;
    for(int j = 0; j < 6; j++){
        slice_avg[j].resize(slices, 0);
        slice_sq[j].resize(slices, 0);
        if(j < 2){
            slice_corr[j].resize(slices, 0);
        }
    }
    slice_particles.resize(slices, 0);

    double Eav = 0;
    for(int n = 0; n < particles; n++){
        int ns = (int)floor(m_ptmp[4][n]/slicelen+0.5)-nsrange[0];
        if(ns < 0 || ns >= slices){
            continue;
        }
        for(int j = 0; j < 6; j++){
            slice_avg[j][ns] += m_ptmp[j][n];
            slice_sq[j][ns] += m_ptmp[j][n]*m_ptmp[j][n];
            if(j < 2){
                slice_corr[j][ns] += m_ptmp[2*j][n]*m_ptmp[2*j+1][n];
            }
        }
        Eav += m_ptmp[5][n];
        slice_particles[ns]++;
    }
    Eav /= particles;

    vector<double> pos(slices), curr(slices), energy(slices), espread(slices);
    vector<double> emitt[2], beta[2], alpha[2];
    for(int j = 0; j < 2; j++){
        emitt[j].resize(slices);
        beta[j].resize(slices);
        alpha[j].resize(slices);
    }

    for(int ns = 0; ns < slices; ns++){
        pos[ns] = (nsrange[0]+ns)*slicelen;
        curr[ns] = slice_particles[ns]*m_prm[PartFmt_][pcharge_]/(slicelen/CC); // current
        if(slice_particles[ns] == 0){
            continue;
        }
        for(int j = 0; j < 6; j++){
            slice_avg[j][ns] /= slice_particles[ns];
            slice_sq[j][ns] /= slice_particles[ns];
            if(j < 2){
                slice_corr[j][ns] /= slice_particles[ns];
            }
        }
        energy[ns] = slice_avg[5][ns]; // energy
        espread[ns] = sqrt((slice_sq[5][ns]-slice_avg[5][ns]*slice_avg[5][ns]))/slice_avg[5][ns]; // energy spread
        for(int j = 0; j < 2; j++){
            double size = slice_sq[2*j][ns]-slice_avg[2*j][ns]*slice_avg[2*j][ns];
            double div = slice_sq[2*j+1][ns]-slice_avg[2*j+1][ns]*slice_avg[2*j+1][ns];
            double corr = slice_corr[j][ns]-slice_avg[2*j][ns]*slice_avg[2*j+1][ns];
            double emittr = size*div-corr*corr;
            if(emittr > 0 && slice_particles[ns] > 5){
                emittr = sqrt(emittr);
                emitt[j][ns] = emittr*(Eav*1e3/MC2MeV)*1e6; // normalized emittance, mm.mrad
                beta[j][ns] = size/emittr; // beta
                alpha[j][ns] = -corr/emittr; // alpha
            }
        }
    }

    vector<string> titles = get<1>(DataFormat.at(CustomSlice));
    vector<vector<double>> values(titles.size());
    for(int j = 0; j < titles.size(); j++){
        if(titles[j] == SliceLabel){
            values[j] = pos;
        }
        else if(titles[j] == CurrentLabel){
            values[j] = curr;
        }
        else if(titles[j] == EnergyLabel){
            values[j] = energy;
        }
        else if(titles[j] == EspLabel){
            values[j] = espread;
        }
        else if(titles[j] == EmittxLabel){
            values[j] = emitt[0];
        }
        else if(titles[j] == EmittyLabel){
            values[j] = emitt[1];
        }
        else if(titles[j] == BetaxLabel){
            values[j] = beta[0];
        }
        else if(titles[j] == BetayLabel){
            values[j] = beta[1];
        }
        else if(titles[j] == AlphaxLabel){
            values[j] = alpha[0];
        }
        else if(titles[j] == AlphayLabel){
            values[j] = alpha[1];
        }
        else{
            values[j].resize(slices, 0);
        }
    }

#ifdef _DEBUG
    if(!SolverSlicePrmParticle.empty() && m_rank == 0){
        ofstream debug_out(SolverSlicePrmParticle);
        vector<double> items(titles.size());
        PrintDebugItems(debug_out, titles);
        for(int ns = 0; ns < slices; ns++){
            for(int j = 0; j < titles.size(); j++){
                items[j] = values[j][ns];
            }
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
    MPI_Barrier(MPI_COMM_WORLD);
#endif

    m_slice.Set1D(titles, values);
    f_InitCustomSlice();
}

void SimplexSolver::f_InitSimplexOutput()
{
    string input, spxfile;
    bool isbeam = m_select[EBeam_][bmprofile_] == SimplexOutput;
    bool isseed = m_select[Seed_][seedprofile_] == SimplexOutput;
    
    if(m_ispostproc){ // post processing, load from the -current- simulation result
        PathHander orgpath(m_datapath);
        orgpath.replace_extension(".json");
        spxfile = orgpath.string();
    }
    else{ // simulation, load from the -input- simulation result
        spxfile = m_string[SPXOut_][spxfile_];
        if(spxfile == m_datapath.string()+".json"){
            throw runtime_error("Output data name should be different from that of the input SIMPLEX data.");
        }
    }
    LoadFile(m_rank, m_procs, spxfile, input, m_thread);

    picojson::value v;
    picojson::parse(v, input);
    picojson::object obj = v.get<picojson::object>();

    if(obj.count(CoordinateLabel) == 0){
        throw runtime_error("Format of the SIMPLEX output file is invalid.");
    }
    picojson::object tobj = obj[CoordinateLabel].get<picojson::object>();
    picojson::array tsteps = tobj[StepIndexLabel].get<picojson::array>();
    m_simexpsteps.resize(tsteps.size());
    for(int n = 0; n < tsteps.size(); n++){
        m_simexpsteps[n] = (int)floor(0.5+tsteps[n].get<double>());
    }
    m_simlambda1 = wave_length(tobj[CentralEnergyLabel].get<double>());

    if(isbeam){
        m_prm[EBeam_][eenergy_] = tobj[AvgEnergyLabel].get<double>();
        picojson::array emitt = tobj[SliceEmittanceLabel].get<picojson::array>();
        for(int j = 0; j < 2; j++){
            m_array[EBeam_][emitt_][j] = emitt[j].get<double>();
        }
        m_pkcurr = tobj[PeakCurrLabel].get<double>();
        f_InitCommon();
    }
    if(isseed){
        picojson::array grids = tobj[XYCoordLabel].get<picojson::array>();
        for(int j = 0; j < 2; j++){
            m_simdxy[j] = grids[j].get<double>();
        }

        picojson::array slices = tobj[SliceCoordLabel].get<picojson::array>();
        m_simspos.resize(slices.size());
        for(int n = 0; n < slices.size(); n++){
            m_simspos[n] = slices[n].get<double>();
        }

        picojson::array nffts = tobj[XYPointsLabel].get<picojson::array>();
        for(int j = 0; j < 2; j++){
            m_simnfft[j] = (int)floor(0.5+nffts[j].get<double>());
        }
    }

    if(m_ispostproc || 
            (m_ispreproc && m_pptype != PPWakeBunch && m_pptype != PPWakeEvar)){
        return;
    }

    m_simcharge = tobj[SimulatedChargeLabel].get<double>();
    m_simbeamlets = (int)floor(0.5+tobj[BeamletsLabel].get<double>());
    m_simparticles = (int)floor(0.5+tobj[ParticlesLabel].get<double>());

    string dummy;
    if(obj.count(InputLabel) == 0){
        throw runtime_error("Format of the SIMPLEX output file is invalid.");
    }
    picojson::object inobj = obj[InputLabel].get<picojson::object>();
    m_sxconf.LoadJSON(dummy, inobj);
    RemoveSuffix(spxfile, ".json");
    m_sxconf.SetDataPath(spxfile);
}

double SimplexSolver::f_GetWakefield(vector<double> *wakefield)
{
    double wakec = 0;
    if(m_bool[Wake_][wakeon_]){
        vector<string> types;
        WakefieldUtility wake(*this);
        vector<double> sw;
        vector<vector<double>> wakes;
        wake.GetWakeFieldProfiles(types, sw, wakes);
        if(types.size() > 0){
            Spline spl;
            spl.SetSpline((int)sw.size(), &sw, &wakes[0]);
            if(wakefield != nullptr){
                for(int n = 0; n < m_slices; n++){
                    (*wakefield)[n] = spl.GetValue(m_s[n], true)*m_lu*m_intstep/(m_eGeV*1e9);
                }
            }
            double zero = 0;
            if(m_select[Und_][opttype_] == TaperOptWake && m_select[Und_][taper_] != NotAvaliable){
                wakec = spl.GetValue(m_prm[Und_][slicepos_], true, nullptr, &zero)/(m_eGeV*1e9);
            }
        }
    }
    return wakec;
}

void SimplexSolver::f_ArrangePostProcessing(
    vector<double> &zarr, vector<double> &sarr, vector<vector<double>> &xyarr,
    int steprange[], int slicerange[], int nrange[])
{
    int winixy = m_select[PostP_][zone_] == PostPFarLabel ? anglindow_ : spatwindow_;
    for(int j = 0; j < 2; j++){
        steprange[j] = (int)floor(0.5+m_array[PostP_][zwindow_][j])-1;
        slicerange[j] = (int)floor(0.5+m_array[PostP_][timewindow_][j])-1;
        nrange[j] = min(m_nfft[j]/2, max(0, (int)floor(0.5+m_array[PostP_][winixy][j])));
    }
    if(m_select[PostP_][timerange_] == PostPIntegFullLabel){
        slicerange[0] = 0;
        slicerange[1] = m_slices-1;
    }
    if(m_select[PostP_][m_rixy] == PostPIntegFullLabel){
        for(int j = 0; j < 2; j++){
            nrange[j] = m_nfft[j]/2;
        }
    }
    if(m_select[PostP_][zrange_] == PostPIntegFullLabel){
        steprange[0]= 0;
        steprange[1] = m_totalsteps-1;
    }

    if(steprange[0] > steprange[1]){
        swap(steprange[0], steprange[1]);
    }
    if(slicerange[0] > slicerange[1]){
        swap(slicerange[0], slicerange[1]);
    }
    steprange[0] = max(0, steprange[0]);
    steprange[1] = min((int)m_exporsteps.size()-1, steprange[1]);

    for(int j = 0; j < 2; j++){
        xyarr[j].resize(2*nrange[j]+1);
        double dxy = m_select[PostP_][zone_] == PostPFarLabel ? m_qxy[j]/(m_nhpp+1) : m_dxy[j];
        for(int n = -nrange[j]; n <= nrange[j]; n++){
            xyarr[j][n+nrange[j]] = dxy*n*1e3; // m -> mm
        }
    }
    zarr.resize(steprange[1]-steprange[0]+1);
    for(int n = steprange[0]; n <= steprange[1]; n++){
        zarr[n-steprange[0]] = m_exportz[n];
    }
    sarr.resize(slicerange[1]-slicerange[0]+1);
    for(int n = slicerange[0]; n <= slicerange[1]; n++){
        sarr[n-slicerange[0]] = m_s[n]*1e3; // m -> mm
    }
}

void SimplexSolver::f_InitGrid()
// m_betaav should be assigned before calling this function
{
    if(m_select[Seed_][seedprofile_] == SimplexOutput){
        for(int j = 0; j < 2; j++){
            m_nfft[j] = m_simnfft[j];
            m_dxy[j] = m_simdxy[j];
        }
    }
    else{
        int grlevel = (int)floor(0.5+m_prm[SimCtrl_][gpointsl_])+4;
        for(int j = 0; j < 2; j++){
            m_nfft[j] = 1<<grlevel;
            m_dxy[j] = sqrt(m_emitt[j]*m_betaav[j])*2*m_prm[SimCtrl_][spatwin_]/m_nfft[j];
        }
    }

    for(int j = 0; j < 2; j++){
        m_dkxy[j] = PI2/m_dxy[j]/m_nfft[j];
        m_qxy[j] = m_lambda_s/m_nfft[j]/m_dxy[j];
        m_Dxy[j] = m_dxy[j]*m_nfft[j]/2;
    }

    if(m_select[Und_][utype_] == LinearUndLabel || m_select[Und_][utype_] == HelicalUndLabel){
        m_np = 1;
    }
    else{
        m_np = 2;
    }
}

void SimplexSolver::f_SetCouplingFactor(PrintCalculationStatus *status, LatticeOperation *lattice)
{
    for(int np = 0; np < m_np; np++){
        m_F[np].resize(m_nhmax);
        for(int nh = 0; nh < m_nhmax; nh++){
            m_F[np][nh].resize(m_totalsteps+1);
            for(int n = 0; n <= m_totalsteps; n++){
                // m_F[np][nh].back(): values for ideal case
                m_F[np][nh][n].resize(m_nfft[0]);
                for(int nx = 0; nx < m_nfft[0]; nx++){
                    m_F[np][nh][n][nx].resize(2*m_nfft[1]);
                }
            }
        }
    }

#ifdef _DEBUG
    vector<int> cplsteps, cplsegs;
#endif

    UndulatorFieldData ufdata(m_rank);
    vector<int> steps;
    int nxy[2], type;
    double gt[2], K2 = m_K*m_K/2;
    bool doneideal = false;

    vector<double> zstep = m_z;
    zstep.insert(zstep.begin(), 0.0); // prepend the initial position (=0)

    int nonideals = m_M-(int)m_segideal.size();

    status->SetSubstepNumber(1, nonideals+1); // memory allocation, XY, Et
    status->ResetCurrentStep(1);

    vector<vector<double>> xyp(2);
    for(int j = 0; j < 2; j++){
        xyp[j].resize(m_totalsteps, 0);
    }
    double xypmax[2] = {0, 0}, gtmax, dgt, dphi, gtphi[2];
    if(m_select[Alignment_][BPMalign_] != IdealLabel || m_bool[Dispersion_][einjec_] || m_bool[Dispersion_][kick_]){
        lattice->GetDispersionArray(xyp, 1);
        for(int j = 0; j < 2; j++){
            xypmax[j] = max(minmax(xyp[j], false), minmax(xyp[j], true));
        }
    }
    gtmax = m_gamma*sqrt(hypotsq(m_qxy[0]*m_nfft[0]/2+xypmax[0], m_qxy[1]*m_nfft[1]/2+xypmax[1]));
    dgt = m_gamma*sqrt(m_lambda1/m_nhmax/(m_lu*m_intstep*SPATIALMESH)); // define delta g*theta to be k theta^2 L <= 2PI / SPMESH
    int gtmesh = max(16, (int)floor(gtmax/dgt+0.5))+1, phimesh = SPATIALMESH+1;
    dgt = gtmax/(gtmesh-1);
    dphi = PI2/(phimesh-1);
    vector<vector<vector<vector<vector<double>>>> >Fre(m_np), Fim(m_np);
    for(int np = 0; np < m_np; np++){
        Fre[np].resize(m_nhmax);
        Fim[np].resize(m_nhmax);
        for(int nh = 0; nh < m_nhmax; nh++){
            Fre[np][nh].resize(m_totalsteps);
            Fim[np][nh].resize(m_totalsteps);
            for(int n = 0; n < m_totalsteps; n++){
                Fre[np][nh][n].resize(gtmesh);
                Fim[np][nh][n].resize(gtmesh);
                for(int ngt = 0; ngt < gtmesh; ngt++){
                    Fre[np][nh][n][ngt].resize(phimesh);
                    Fim[np][nh][n][ngt].resize(phimesh);
                }
            }
        }
    }

    vector<double> phiarr(phimesh), gtarr(gtmesh);
    int ngtphi[2] = {gtmesh, phimesh};
    for(int nphi = 0; nphi < phimesh; nphi++){
        phiarr[nphi] = nphi*dphi;
    }
    for(int ngt = 0; ngt < gtmesh; ngt++){
        gtarr[ngt] = ngt*dgt;
    }
    double *ws = nullptr;
    if(m_procs > 1){
        ws = new double[2*phimesh];
    }
    Spline2D spl2dre, spl2dim;

    for(int m = 0; m < m_M; m++){
        SetUndulatorData(&ufdata, m, &type);
        steps.clear();
        if(type == 1 || type == 2){ // error or data
            for(int n = m_steprange[0][m]; n <= m_steprange[1][m]; n++){
                steps.push_back(n);
            }
        }
        else if(doneideal){ // ideal: already done
#ifdef _DEBUG
            int nini = m_steprange[0][m];
            if(fabs(xyp[0][nini]) >= m_qxy[0]*KICKTHRESHOLD || fabs(xyp[1][nini]) >= m_qxy[1]*KICKTHRESHOLD){
                cplsteps.push_back(nini);
                cplsegs.push_back(m);
            }
#endif
            continue;
        }
        else{ // ideal: to be done
            for(int i = 0; i < m_segideal.size(); i++){
                for(int n = m_steprange[0][m_segideal[i]]; n <= m_steprange[1][m_segideal[i]]; n++){
                    steps.push_back(n);
                }
            }
            doneideal = true;
        }
#ifdef _DEBUG
        cplsteps.push_back(steps.back());
        cplsegs.push_back(m);
#endif

        if(m_lasermod){
            gt[0] = gt[1] = 0;
            ufdata.GetCoupling(m_nhmax, gt, steps, m_intstep, m_z, 0, 0, Fre, Fim);
            for(int k = 0; k < steps.size(); k++){
                int n = steps[k];
                m_F[0][0][n][0][0] = Fre[0][0][n][0][0];
                m_F[0][0][n][0][1] = Fim[0][0][n][0][0];
            }
            continue;
        }

        for(int ngt = 0; ngt < gtmesh; ngt++){
            if(ngt%m_procs != m_rank){
                continue;
            }
            for(int nphi = 0; nphi < phimesh-1; nphi++){
                gt[0] = gtarr[ngt]*cos(phiarr[nphi]);
                gt[1] = gtarr[ngt]*sin(phiarr[nphi]);
                ufdata.GetCoupling(m_nhmax, gt, steps, m_intstep, m_z, ngt, nphi, Fre, Fim);
            }
        }
        if(m_procs > 1){
            for(int np = 0; np < m_np; np++){
                for(int nh = 0; nh < m_nhmax; nh++){
                    for(int k = 0; k < steps.size(); k++){
                        int n = steps[k];
                        for(int ngt = 0; ngt < gtmesh; ngt++){
                            int rank = ngt%m_procs;
                            if(rank == m_rank){
                                for(int nphi = 0; nphi < phimesh; nphi++){
                                    ws[nphi] = Fre[np][nh][n][ngt][nphi];
                                    ws[nphi+phimesh] = Fim[np][nh][n][ngt][nphi];
                                }
                            }
                            if(m_thread != nullptr){
                                m_thread->Bcast(ws, 2*phimesh, MPI_DOUBLE, rank, m_rank);
                            }
                            else{
                                MPI_Bcast(ws, 2*phimesh, MPI_DOUBLE, rank, MPI_COMM_WORLD);
                            }
                            if(rank != m_rank){
                                for(int nphi = 0; nphi < phimesh; nphi++){
                                    Fre[np][nh][n][ngt][nphi] = ws[nphi];
                                    Fim[np][nh][n][ngt][nphi] = ws[nphi+phimesh];
                                }
                            }
                        }
                    }
                }
            }
        }

        for(int np = 0; np < m_np; np++){
            for(int nh = 0; nh < m_nhmax; nh++){
                double re = 0, im = 0;
                for(int k = 0; k < steps.size(); k++){
                    int n = steps[k];
                    re += Fre[np][nh][n][0][0];
                    im += Fim[np][nh][n][0][0];
                }
                if(hypotsq(re, im) == 0){
                    continue;
                }
                double phi = -atan2(im, re);
                double csn[2] = {cos(phi), sin(phi)};
                for(int ngt = 0; ngt < gtmesh; ngt++){
                    for(int nphi = 0; nphi < phimesh; nphi++){
                        for(int k = 0; k < steps.size(); k++){
                            int n = steps[k];
                            multiply_complex(&Fre[np][nh][n][ngt][nphi], &Fim[np][nh][n][ngt][nphi], csn);
                        }
                    }
                }
            }
        }

        if(!SolverCouplingCyl.empty() && m_rank == 0){
            ofstream debug_out(SolverCouplingCyl);
            vector<string> titles{"theta", "phi"};
            titles.push_back("FxRe"+to_string(m+1));
            titles.push_back("FxIm"+to_string(m+1));
            if(m_np > 1){
                titles.push_back("FyRe"+to_string(m+1));
                titles.push_back("FyIm"+to_string(m+1));
            }

            PrintDebugItems(debug_out, titles);
            vector<double> items(titles.size());
            int nhtgt = 4;
            nhtgt = min(m_nhmax-1, nhtgt);
            for(int ngt = 0; ngt < gtmesh; ngt++){
                items[0] = gtarr[ngt];
                for(int nphi = 0; nphi < phimesh-1; nphi++){
                    items[1] = phiarr[nphi];
                    int ni = 1;
                    for(int np = 0; np < m_np; np++){
                        items[++ni] = Fre[np][nhtgt][steps[0]][ngt][nphi];
                        items[++ni] = Fim[np][nhtgt][steps[0]][ngt][nphi];
                    }
                    PrintDebugItems(debug_out, items);
                }
            }
            debug_out.close();
        }

        if(ufdata.IsIdeal()){
            for(int np = 0; np < m_np; np++){
                for(int nh = 0; nh < m_nhmax; nh++){
                    double knh = PI2*(nh+1)/m_lambda_s;
                    spl2dre.SetSpline2D(ngtphi, &gtarr, &phiarr, &Fre[np][nh][steps[0]]);
                    spl2dim.SetSpline2D(ngtphi, &gtarr, &phiarr, &Fim[np][nh][steps[0]]);
                    for(nxy[0] = 0; nxy[0] < m_nfft[0]; nxy[0]++){
                        gt[0] = m_gamma*m_dkxy[0]*fft_index(nxy[0], m_nfft[0], 1)/knh;
                        for(nxy[1] = 0; nxy[1] < m_nfft[1]; nxy[1]++){
                            gt[1] = m_gamma*m_dkxy[1]*fft_index(nxy[1], m_nfft[1], 1)/knh;
                            gtphi[0] = sqrt(hypotsq(gt[0], gt[1]));
                            if(gtphi[0] > 0){
                                gtphi[1] = atan2(gt[1], gt[0])+PI;
                            }
                            else{
                                gtphi[1] = 0;
                            }
                            m_F[np][nh][m_totalsteps][nxy[0]][2*nxy[1]] = spl2dre.GetValue(gtphi, true);
                            m_F[np][nh][m_totalsteps][nxy[0]][2*nxy[1]+1] = spl2dim.GetValue(gtphi, true);
                        }
                    }
                }
            }
        }

        for(int np = 0; np < m_np; np++){
            for(int nh = 0; nh < m_nhmax; nh++){
                double knh = PI2*(nh+1)/m_lambda_s;
                for(int k = 0; k < steps.size(); k++){
                    int n = steps[k];
                    bool nokick = fabs(xyp[0][n]) < m_qxy[0]*KICKTHRESHOLD && fabs(xyp[1][n]) < m_qxy[1]*KICKTHRESHOLD;
                    // ignore dispersion if kick angle is lower than grid*KICKTHRESHOLD
                    if(ufdata.IsIdeal() && nokick){
                        m_F[np][nh][n] = m_F[np][nh][m_totalsteps];
                        continue;
                    }
                    if(k > 0 && ufdata.IsIdeal()){
                        nokick = fabs(xyp[0][n]-xyp[0][steps[k-1]]) < m_qxy[0]*KICKTHRESHOLD 
                            && fabs(xyp[1][n]-xyp[1][steps[k-1]]) < m_qxy[1]*KICKTHRESHOLD;
                        if(nokick){
                            m_F[np][nh][n] = m_F[np][nh][steps[k-1]];
                            continue;
                        }
                    }
                    spl2dre.SetSpline2D(ngtphi, &gtarr, &phiarr, &Fre[np][nh][n]);
                    spl2dim.SetSpline2D(ngtphi, &gtarr, &phiarr, &Fim[np][nh][n]);
                    for(nxy[0] = 0; nxy[0] < m_nfft[0]; nxy[0]++){
                        gt[0] = m_gamma*(m_dkxy[0]*fft_index(nxy[0], m_nfft[0], 1)/knh-xyp[0][n]);
                        for(nxy[1] = 0; nxy[1] < m_nfft[1]; nxy[1]++){
                            gt[1] = m_gamma*(m_dkxy[1]*fft_index(nxy[1], m_nfft[1], 1)/knh-xyp[1][n]);
                            gtphi[0] = sqrt(hypotsq(gt[0], gt[1]));
                            if(gtphi[0] > 0){
                                gtphi[1] = atan2(gt[1], gt[0])+PI;
                            }
                            else{
                                gtphi[1] = 0;
                            }
                            m_F[np][nh][n][nxy[0]][2*nxy[1]] = spl2dre.GetValue(gtphi, true);
                            m_F[np][nh][n][nxy[0]][2*nxy[1]+1] = spl2dim.GetValue(gtphi, true);
                        }
                    }
                }
            }
        }
        status->AdvanceStep(1);
    }

    if(m_procs > 1){
        delete[] ws;
    }
    
    if(!m_lasermod){
        status->AdvanceStep(0);
    }

#ifdef _DEBUG
    if(!SolverCouplingXY.empty() && m_rank == 0){
        ofstream debug_out(SolverCouplingXY);
        vector<string> titles {"x'", "y'"};
        for(int m = 0; m < cplsegs.size(); m++){
            titles.push_back("FxRe"+to_string(cplsegs[m]+1));
            titles.push_back("FxIm"+to_string(cplsegs[m]+1));
            if(m_np > 1){
                titles.push_back("FyRe"+to_string(cplsegs[m]+1));
                titles.push_back("FyIm"+to_string(cplsegs[m]+1));
            }
        }
        PrintDebugItems(debug_out, titles);
        vector<double> items(titles.size());
        int index[2], nhtgt = 2;
        nhtgt = min(m_nhmax-1, nhtgt);
        double fnh = nhtgt+1;
        for(nxy[0] = -m_nfft[0]/2+1; nxy[0] <= m_nfft[0]/2-1; nxy[0]++){
            items[0] = m_qxy[0]*nxy[0]/fnh;
            index[0] = fft_index(nxy[0], m_nfft[0], -1);
            for(nxy[1] = -m_nfft[1]/2+1; nxy[1] <= m_nfft[1]/2-1; nxy[1]++){
                items[1] = m_qxy[1]*nxy[1]/fnh;
                index[1] = fft_index(nxy[1], m_nfft[1], -1);
                int ni = 1;
                for(int m = 0; m < cplsteps.size(); m++){
                    for(int np = 0; np < m_np; np++){
                        items[++ni] = m_F[np][nhtgt][cplsteps[m]][index[0]][2*index[1]];
                        items[++ni] = m_F[np][nhtgt][cplsteps[m]][index[0]][2*index[1]+1];
                    }
                }
                PrintDebugItems(debug_out, items);
            }
        }
        debug_out.close();
    }
    if(!SolverCouplingZ.empty() && m_rank == 0){
        ofstream debug_out(SolverCouplingZ);
        vector<string> titles{ZLabel};
        for(int nh = 1; nh <= m_nhmax; nh++){
            titles.push_back("FxRe"+to_string(nh));
            titles.push_back("FxIm"+to_string(nh));
            if(m_np > 1){
                titles.push_back("FyRe"+to_string(nh));
                titles.push_back("FyIm"+to_string(nh));
            }
        }

        PrintDebugItems(debug_out, titles);
        vector<double> items(titles.size());
        for(int n = 0; n < m_totalsteps; n++){
            items[0] = m_z[n];
            int ni = 0;
            for(int nh = 0; nh < m_nhmax; nh++){
                for(int np = 0; np < m_np; np++){
                    items[++ni] = m_F[np][nh][n][0][0];
                    items[++ni] = m_F[np][nh][n][0][1];
                }
            }
            PrintDebugItems(debug_out, items);
        }

        debug_out.close();
    }
    MPI_Barrier(MPI_COMM_WORLD);
#endif
}

double SimplexSolver::f_GetNetMagnetLength(double z, bool trunc)
{
    if(z <= 0.0){
        return 0.0;
    }
    int segment = min(m_M, (int)ceil(z/m_prm[Und_][interval_]));
    double position = trunc ? 0 : min(z-(segment-1)*m_prm[Und_][interval_], m_N*m_lu);
    return (segment-1)*(m_N*m_lu)+position;
}

void SimplexSolver::f_GetK4Eta(double eta, double *Kbase, double *detune)
{
    double Kadd = 1+eta;
    Kadd = sqrt(2*Kadd*Kadd*(1+m_K*m_K/2)-2)-m_K;

    *Kbase += Kadd;
    *detune = 1-(1+(*Kbase)*(*Kbase)/2)/(1+m_K*m_K/2);
}

void SimplexSolver::f_GetKVaried(double z, double *detune, double *K, double wf)
{
    double ktaper = m_K;
    if(m_select[Und_][taper_] == TaperContinuous 
            || m_select[Und_][taper_] == TaperStair){
        double dztaper, ztini;
        int iniseg = (int)floor(0.5+m_prm[Und_][initial_]);
        int incrseg = (int)floor(0.5+m_prm[Und_][incrseg_]);
        int segment = min(m_M, (int)ceil(z/m_prm[Und_][interval_]));
        double rate = m_prm[Und_][base_];
        while(iniseg <= segment){
            ztini = (iniseg-1)*m_prm[Und_][interval_];
            if(m_select[Und_][taper_] == TaperStair){
                ztini -= m_prm[Und_][interval_];
            }
            dztaper = f_GetNetMagnetLength(z-ztini, m_select[Und_][taper_] == TaperStair);
            ktaper += rate*dztaper;
            iniseg += max(1, incrseg);
            rate = m_prm[Und_][incrtaper_];
        };
    }
    else if(m_select[Und_][taper_] == TaperCustom){
        int segment = min(m_M, max(1, (int)ceil(z/m_prm[Und_][interval_])));
        if(segment <= m_tapercont.size()){
            double z0 = (segment-1)*m_prm[Und_][interval_]+m_N*m_lu/2;
            double dz = z-z0;
            ktaper += m_tapercont[segment-1][0]+m_tapercont[segment-1][1]*dz;
        }
    }
    double dzwake = f_GetNetMagnetLength(z, m_select[Und_][taper_] == TaperStair)+m_lu*m_N/2;

    f_GetK4Eta(wf*dzwake, &ktaper, detune);
    *K = ktaper;
}

void SimplexSolver::f_ArrangeDetuning(vector<double> &detune)
{
    int ulsteps = m_segsteps+m_driftsteps;
    for(int m = 1; m < m_M; m++){
        if(m_driftsteps > 0){
            double detdrift = (detune[m*ulsteps-m_driftsteps-1]+detune[m*ulsteps])/2;
            for(int n = 0; n < m_driftsteps; n++){
                detune[m*ulsteps-m_driftsteps+n] = detdrift;
            }
        }
        detune[m*ulsteps-1] += m_prm[Und_][exslippage_]/360;
    }

    for(int n = 0; n < m_totalsteps; n++){
        detune[n] += m_detune_err[n];
    }
}

// Integration over E-t space
string EtIntegrate = "";

void EtIntegrator::Set(double wavel, double r56, double espread, double pkcurr, double bunchlen,
    vector<double> &s, vector<double> &eta)
{
#ifdef _DEBUG
    //EtIntegrate = "..\\debug\\Et_integrate.dat";
#endif

    m_wavelength = wavel;
    m_r56 = r56;
    m_espread = espread;
    m_sigmas = bunchlen;
    m_pkcurr = pkcurr;

    m_etarange[0] = minmax(eta, false)-m_espread*GAUSSIAN_MAX_REGION;
    m_etarange[1] = minmax(eta, true)+m_espread*GAUSSIAN_MAX_REGION;
    m_etaspl.SetSpline((int)s.size(), &s, &eta);
    m_particles = (int)s.size();

    AllocateMemorySimpson(1, 1, 1);
}

double EtIntegrator::GetOptimumR56(double efactor)
{
    double gmax = INFINITESIMAL;
    for(int n = 0; n < m_particles; n++){
        double grad = -m_etaspl.GetDerivative(n);
        if(grad > gmax){
            gmax = grad;
        }
    }
    m_r56 = 1.0/gmax*efactor;
    return m_r56;
}

void EtIntegrator::GetCurrent(vector<double> &s, vector<double> &I, int acc)
{
    vector<double> jret(1);
    double eps = 1e-3;
    int layers[2] = {0, -1};
    double deta = m_wavelength/m_r56;
    int ndiv = max(1, (int)ceil((m_etarange[1]-m_etarange[0])/deta));
    ndiv *= max(1, acc);
    deta = (m_etarange[1]-m_etarange[0])/ndiv;
    double etar[2];

    int slices = (int)s.size();
    I.resize(slices);
    for(int n = 0; n < slices; n++){
        m_s = s[n];
        I[n] = 0;
        for(int m = 0; m < ndiv; m++){
            etar[0] = m_etarange[0]+m*deta;
            etar[1] = etar[0]+deta;
            IntegrateSimpson(layers, etar[0], etar[1], eps, 5, nullptr, &jret, EtIntegrate, m > 0);
            I[n] += jret[0];
        }
    }
}

void EtIntegrator::GetParticalCurrent(vector<double> &s, vector<double> &eta, vector<double> &j)
{
    int slices = (int)s.size();
    int ne = (int)eta.size();
    j.resize(slices*ne);
    vector<double> jr(1);
    for(int m = 0; m < ne; m++){
        for(int n = 0; n < slices; n++){
            m_s = s[n];
            QSimpsonIntegrand(0, eta[m], &jr);
            j[m*slices+n] = jr[0];
        }
    }
}

void EtIntegrator::QSimpsonIntegrand(int layer, double eta, vector<double> *j)
{
    double s0 = m_s-m_r56*eta;
    double eta0 = eta-m_etaspl.GetValue(s0);
    double tex = eta0/m_espread;
    tex *= tex*0.5;
    if(m_sigmas > 0){
        double texs = s0/m_sigmas;
        tex += texs*texs*0.5;
    }
    if(tex > MAXIMUM_EXPONENT){
        (*j)[0] = 0;
        return;
    }
    (*j)[0] = m_pkcurr/SQRTPI2/m_espread*exp(-tex);
}


double rho_fel_param_1D(double ipeak, double lambda_u_m, double K, double phi,
    double beta, double emitt, double gamma)
{
    double ir, kr, gr, rho, Ajj, Bjj, Q;
    phi *= DEGREE2RADIAN;

    Q = K*K*cos(2.0*phi)/(4.0+2.0*K*K);
    Ajj = Bessel::J0(Q)-Bessel::J1(Q);
    Bjj = Bessel::J0(Q)+Bessel::J1(Q);
    Ajj = sqrt(hypotsq(Ajj*cos(phi), Bjj*sin(phi)));

    ir = ipeak/ALFVEN_CURR;
    kr = lambda_u_m*K*Ajj/PI2;
    kr *= kr/2.0/(beta*emitt);

    gr = 0.5/gamma;
    gr *= gr*gr;
    rho = ir*kr*gr;
    return pow(rho, 1.0/3.0);
}

double scaling_fel3d_eta(double lambda, double L1D,
    double beta, double emitt, double lambda_u, double espread)
{
    double eta, Lr, d, e, g;
    double a[] = {0.0, 0.45, 0.57, 0.55, 1.6, 3.0, 2.0, 0.35, 2.9, 2.4, 51.0,
        0.95, 3.0, 5.4, 0.7, 1.9, 1140.0, 2.2, 2.9, 3.2};

    Lr = 4.0*PI*beta*emitt/lambda;
    d = L1D/Lr;
    e = L1D/beta*(4.0*PI*emitt/lambda);
    g = 4.0*PI*L1D/lambda_u*espread;

    eta = a[1]*pow(d, a[2])+a[3]*pow(e, a[4])+a[5]*pow(g, a[6])
        + a[7]*pow(e, a[8])*pow(g, a[9])+a[10]*pow(d, a[11])*pow(g, a[12])
        +a[13]*pow(d, a[14])*pow(e, a[15])+a[16]*pow(d, a[17])*pow(e, a[18])*pow(g, a[19]);
    return eta;
}

void rand_init(bool autoseed, int seed, int procs, int rank, RandomUtility *rand, MPIbyThread *mpithread)
{
    if(autoseed){
        int seed = rand->Init();
        if(procs > 0){
            if(mpithread != nullptr){
                mpithread->Bcast(&seed, 1, MPI_INT, 0, rank);
            }
            else{
                MPI_Bcast(&seed, 1, MPI_INT, 0, MPI_COMM_WORLD);
            }
            if(rank > 0){
                rand->Init(seed);
            }
        }
    }
    else{
        rand->Init(seed);
    }
}

void LoadFile(int rank, int mpiprocesses, const string filename, string &input, MPIbyThread *mpithread)
{
    if(rank == 0){
        ifstream ifs(filename);
        if(!ifs){
            string msg = "Load the data file \""+filename+"\" failed.";
            throw runtime_error(msg.c_str());
        }
        input = string((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
        ifs.close();
    }
    if(mpiprocesses > 1){
        int inputsize;
        if(rank == 0){
            inputsize = (int)input.length();
        }
        if(mpithread != nullptr){
            mpithread->Bcast(&inputsize, 1, MPI_INT, 0, rank);
        }
        else{
            MPI_Bcast(&inputsize, 1, MPI_INT, 0, MPI_COMM_WORLD);
        }

        char *buffer = new char[inputsize+1];
        if(rank == 0){
#ifdef WIN32
            strcpy_s(buffer, inputsize+1, input.c_str());
#else
            strcpy(buffer, input.c_str());
#endif
        }
        if(mpithread != nullptr){
            mpithread->Bcast(buffer, inputsize+1, MPI_CHAR, 0, rank);
        }
        else{
            MPI_Bcast(buffer, inputsize+1, MPI_CHAR, 0, MPI_COMM_WORLD);
        }
        if(rank > 0){
            input = string(buffer);
        }
        delete[] buffer;
    }
}
