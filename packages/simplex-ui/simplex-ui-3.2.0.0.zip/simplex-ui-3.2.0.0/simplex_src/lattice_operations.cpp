#include <algorithm>
#include "lattice_operations.h"
#include "randomutil.h"

constexpr auto SectionLengthLimit = 1e-6; // minimum length to define a section (1 um)
constexpr auto ComponentLegnthLimit = 1e-3; // minimum length to define a component (1 mm)

vector<vector<double>> UnitMatrix{
    {1, 0, 0}, {0, 1, 0}, {0, 0, 1}
};

vector<vector<double>> ZeroMatrix{
    {0, 0, 0}, {0, 0, 0}, {0, 0, 0}
};

// matrix operation for lattice functions
void twiss_cossindisp_func(double s, double kfoc, double rhoinv,
    double *cs, double *ss, double *csd, double *ssd, double *ds, double *dsd)
{
    double sqrtk;
    if(kfoc > 0.0){
        sqrtk = sqrt(kfoc);
        *cs = *ssd = cos(sqrtk*s);
        *ss = sin(sqrtk*s);
        *csd = -(*ss)*sqrtk;
        *ss /= sqrtk;
        *ds = (1.0-cos(sqrtk*s))*rhoinv/kfoc;
        *dsd = *ss*rhoinv;
    }
    else if(kfoc == 0.0){
        *cs = *ssd = 1.0;
        *ss = s;
        *csd = 0.0;
        *ds = s*s/2.0*rhoinv;
        *dsd = s*rhoinv;
    }
    else{
        sqrtk = sqrt(fabs(kfoc));
        *cs = *ssd = cosh(sqrtk*s);
        *ss = sinh(sqrtk*s);
        *csd = (*ss)*sqrtk;
        *ss /= sqrtk;
        *ds = (cosh(sqrtk*s)-1.0)*rhoinv/(-kfoc);
        *dsd = *ss*rhoinv;
    }
}

void csd_matrix(double cs, double csd, double ss, double ssd, double ds, double dsd,
    vector<vector<double>> &M)
{
    M[0][0] = cs;
    M[0][1] = ss;
    M[0][2] = ds;
    M[1][0] = csd;
    M[1][1] = ssd;
    M[1][2] = dsd;
    M[2][0] = 0.0;
    M[2][1] = 0.0;
    M[2][2] = 1.0;
}

void twiss_matrix(double s, double kfoc, vector<vector<double>> &M)
{
    double cs, ss, csd, ssd, ds, dsd;

    twiss_cossindisp_func(s, kfoc, 1.0, &cs, &ss, &csd, &ssd, &ds, &dsd);
    M[0][0] = cs*cs;
    M[0][1] = -2.0*ss*cs;
    M[0][2] = ss*ss;
    M[1][0] = -cs*csd;
    M[1][1] = ssd*cs+csd*ss;
    M[1][2] = -ss*ssd;
    M[2][0] = csd*csd;
    M[2][1] = -2.0*ssd*csd;
    M[2][2] = ssd*ssd;
}

vector<vector<double>> matrix_product(vector<vector<double>> &M1, vector<vector<double>> &M2)
{
    vector<vector<double>> M = ZeroMatrix;
    for(int i = 0; i < 3; i++){
        for(int j = 0; j < 3; j++){
            for(int k = 0; k < 3; k++){
                M[i][j] += M1[i][k]*M2[k][j];
            }
        }
    }
    return M;
}

vector<double> vector_product(vector<vector<double>> &M, vector<double> &E)
{
    vector<double> F{0, 0, 0};
    for(int i = 0; i < 3; i++){
        for(int k = 0; k < 3; k++){
            F[i] += M[i][k]*E[k];
        }
    }
    return F;
}

vector<vector<double>> inverse_matrix(vector<vector<double>> M)
{
    double D;
    D = M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])
        +M[0][1]*(M[1][2]*M[2][0]-M[1][0]*M[2][2])
        +M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]);

    vector<vector<double>> MI = ZeroMatrix;

    MI[0][0] = (M[1][1]*M[2][2]-M[1][2]*M[2][1])/D;
    MI[0][1] = (M[0][2]*M[2][1]-M[0][1]*M[2][2])/D;
    MI[0][2] = (M[0][1]*M[1][2]-M[0][2]*M[1][1])/D;
    MI[1][0] = (M[1][2]*M[2][0]-M[1][0]*M[2][2])/D;
    MI[1][1] = (M[0][0]*M[2][2]-M[0][2]*M[2][0])/D;
    MI[1][2] = (M[0][2]*M[1][0]-M[0][0]*M[1][2])/D;
    MI[2][0] = (M[1][0]*M[2][1]-M[1][1]*M[2][0])/D;
    MI[2][1] = (M[0][1]*M[2][0]-M[0][0]*M[2][1])/D;
    MI[2][2] = (M[0][0]*M[1][1]-M[0][1]*M[1][0])/D;

    return MI;
}

// class LatticeOperation
string LatticeArrangement = "";
string LatticeDispersion = "";
string LatticeKickList = "";
string LatticeBeta = "";

LatticeOperation::LatticeOperation(SimplexSolver &sxsolver)
    : SimplexSolver(sxsolver)
{
    if(m_rank == 0){
#ifdef _DEBUG
//        LatticeArrangement = "..\\debug\\lattice_arrangement.dat";
//        LatticeDispersion = "..\\debug\\lattice_dispersion.dat";
//        LatticeKickList = "..\\debug\\lattice_kicklist.dat";
        LatticeBeta = "..\\debug\\lattice_beta.dat";
#endif
    }
    Initialize();
}

void LatticeOperation::Initialize()
{
    for(int j = 0; j < 2; j++){
        m_betaini[j] = m_array[Lattice_][betaxy0_][j];
        m_alphaini[j] = m_array[Lattice_][alphaxy0_][j];
        m_xyinj[j] = m_xydinj[j] = 0;
    }

    int segper;
    double Lu = m_prm[Und_][length_];
    double Uint = max(Lu, m_prm[Und_][interval_]);
	double Ldrift = max(0.0, Uint-Lu);
    double qinterval = m_prm[Lattice_][dist_];
    double segst = 0.0;

    double qlen[2];
    qlen[0] = m_prm[Lattice_][qfl_];
    qlen[1] = m_prm[Lattice_][qdl_];

    m_ncomp = m_M+1;
    if(m_select[Lattice_][ltype_] == DoubletLabel){
        m_ncomp = 2*(m_M+1);
    }
    else if(m_select[Lattice_][ltype_] == TripletLabel){
        m_ncomp = 3*(m_M+1);
    }
    else if(m_select[Lattice_][ltype_] == CombinedLabel){
        segper = (int)floor(m_prm[Lattice_][lperiods_]+0.5);
        m_ncomp = segper*2*m_M;
        segst = (Lu-(double)(segper*2)*qinterval)*0.5+qinterval*0.5;
    }

    m_position.resize(m_ncomp);
    m_length.resize(m_ncomp);

    int mseg;
    for(int n = 0; n < m_ncomp; n++){
        // magnet length
        if(m_select[Lattice_][ltype_] == FUFULabel){
            m_length[n] = qlen[0];
        }
        else if(m_select[Lattice_][ltype_] == TripletLabel){
            if(n%3 == 1){ // central Q
                m_length[n] = qlen[1];
            }
            else{
                m_length[n] = qlen[0];
            }
        }
        else if(m_select[Lattice_][ltype_] == DUFULabel){
            m_length[n] = qlen[(n+1)%2];
        }
        else{
            m_length[n] = qlen[n%2];
        }

        // magnet position
        if(m_select[Lattice_][ltype_] == FUFULabel 
            || m_select[Lattice_][ltype_] == FUDULabel 
            || m_select[Lattice_][ltype_] == DUFULabel)
        {
            m_position[n] = -Ldrift*0.5+n*Uint;
        }
        else if(m_select[Lattice_][ltype_] == DoubletLabel){
            mseg = n/2;
            m_position[n] = -Ldrift*0.5+(double)mseg*Uint+((n%2)-0.5)*qinterval;
        }
        else if(m_select[Lattice_][ltype_] == TripletLabel){
            mseg = n/3;
            m_position[n] = -Ldrift*0.5+(double)mseg*Uint+((n%3)-1.0)*qinterval;
        }
        else if(m_select[Lattice_][ltype_] == CombinedLabel){
            mseg = n/(segper*2);
            m_position[n] = segst+(double)mseg*Uint+(n%(segper*2))*qinterval;
        }
    }

    double lst = m_lu; // steering length = undulator period; just to simplify
    double cE = CC*1.0e-9/m_eGeV;
    m_stT2rad = cE*lst; // Tesla to rad for all steering components
    m_qtypical = 1.0/cE/(Lu*m_length[0]); // field gradient (T/m) for focal length of undulator length
    if(m_select[Alignment_][BPMalign_] == TargetErrorLabel){
        m_stposition.resize(m_M-1);
        m_stlength.resize(m_M-1, lst);
        for(int j = 0; j < 2; j++){
            m_stBxy[j].resize(m_M-1, 0);
        }
        for(int n = 1; n < m_M; n++){
            m_stposition[n-1] = n*m_prm[Und_][interval_]-Ldrift/2;
        }
    }
    if(m_bool[Dispersion_][kick_]){
        m_stposition.push_back(m_prm[Dispersion_][kickpos_]);
        m_stlength.push_back(lst);
        for(int j = 0; j < 2; j++){
            m_stBxy[j].push_back(m_array[Dispersion_][kickangle_][j]*1e-3); // mrad -> rad
            m_stBxy[j].back() /= m_stT2rad; // rad -> T
        }
    }

    int nsegu = m_driftsteps > 0 ? m_M*2 : 2;
    m_ntcomp = m_ncomp+(int)m_stposition.size();

    vector<double> pos(m_ntcomp), len(m_ntcomp), 
        zcq1(m_ntcomp), zcq2(m_ntcomp), zcu1(nsegu/2), zcu2(nsegu/2);

    for(int nq = 0; nq < m_ncomp; nq++){
        pos[nq] = m_position[nq];
        len[nq] = m_length[nq];
    }
    for(int nq = m_ncomp; nq < m_ntcomp; nq++){
        pos[nq] = m_stposition[nq-m_ncomp];
        len[nq] = m_stlength[nq-m_ncomp];
    }

    m_nseg = nsegu+m_ntcomp*2;
    m_zc.resize(m_nseg);

    for(int nq = 0; nq < m_ntcomp; nq++){
        len[nq] = max(ComponentLegnthLimit, len[nq]);
        zcq1[nq] = m_zc[2*nq] = pos[nq]-0.5*len[nq];
        zcq2[nq] = m_zc[2*nq+1] = pos[nq]+0.5*len[nq];
    }
    if(m_driftsteps > 0){
        for(int nu = 0; nu < m_M; nu++){
            zcu1[nu] = m_zc[2*m_ntcomp+2*nu] = nu*Uint;
            zcu2[nu] = m_zc[2*m_ntcomp+2*nu+1] = m_zc[2*m_ntcomp+2*nu]+m_lu*m_N;
        }
    }
    else{
        zcu1[0] = m_zc[2*m_ntcomp] = 0.0;
        zcu2[0] = m_zc[2*m_ntcomp+1] = m_lu*m_N*m_M;
    }
    sort(m_zc.begin(), m_zc.end());

    // check borders
    for(int n = 0; n < m_nseg-1; n++){
        if(m_zc[n] == m_zc[n+1]){
            for(int nr = n+1; nr < m_nseg-1; nr++){
                m_zc[nr] = m_zc[nr+1];
            }
            m_nseg--;
            n--;
            continue;
        }
    }

    for(int j = 0; j < 2; j++){
        m_kfoc[j].resize(m_nseg);
        m_rhoinv[j].resize(m_nseg);
        m_Bpeak[j].resize(m_nseg);
    }
    m_nq.resize(m_nseg);

    // assign segment number and undulator peak field
    double Bpeak = m_K/COEF_K_VALUE/m_lu;
    for(int n = 0; n < m_nseg-1; n++){
        double zmid = 0.5*(m_zc[n]+m_zc[n+1]);
        for(int nq = 0; nq < m_ntcomp; nq++){
            if(zmid > zcq1[nq] && zmid < zcq2[nq]){
                m_nq[n].push_back(nq);
            }
        }
        for(int nu = 0; nu < nsegu/2; nu++){
            if(zmid > zcu1[nu] && zmid < zcu2[nu]){
                double uphi = m_Kphi*DEGREE2RADIAN;
                m_Bpeak[0][n].push_back(Bpeak*sin(uphi));
                m_Bpeak[1][n].push_back(Bpeak*cos(uphi));
            }
        }
    }

    double gradient[2];
    gradient[0] = m_prm[Lattice_][qfg_];
    gradient[1] = m_prm[Lattice_][qdg_];
    f_SetQStrength(gradient);

#ifdef _DEBUG
    if(!LatticeArrangement.empty()){
        ofstream debug_out(LatticeArrangement);
        vector<string> titles {"z", "kx", "ky"};
        vector<double> items(titles.size());
        PrintDebugItems(debug_out, titles);
        for(int n = 0; n < m_nseg-1; n++){
            items[0] = m_zc[n];
            items[1] = m_kfoc[0][n];
            items[2] = m_kfoc[1][n];
            PrintDebugItems(debug_out, items);
            items[0] = m_zc[n+1];
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif
    
    if(m_select[Alignment_][BPMalign_] == TargetErrorLabel){
        SetBPMError();
    }

    for(int n = 0; n < m_nseg-1; n++){
        double zmid = 0.5*(m_zc[n]+m_zc[n+1]);
        for(int nq = m_ncomp; nq < m_ntcomp; nq++){
            if(zmid > zcq1[nq] && zmid < zcq2[nq]){
                for(int j = 0; j < 2; j++){
                    m_rhoinv[j][n] += m_stBxy[j][nq-m_ncomp]*cE;
                }
            }
        }
    }
    m_CSD.resize(m_z.size(), {UnitMatrix, UnitMatrix});

    if(m_select[Alignment_][BPMalign_] == TargetErrorLabel){
        for(int j = 0; j < 2; j++){
            m_CSD[0][j][0][2] = m_xyinj[j];
            m_CSD[0][j][1][2] = m_xydinj[j];
        }
    }

    int comps, stcomp;
    double snew, sold = 0, ds, z[2] = {0, 0};
    for(int n = 0; n < m_z.size(); n++){
        if(n == 0){
            z[1] = m_z[0];
        }
        else{
            z[0] = z[1];
            z[1] = m_z[n];
            m_CSD[n] = m_CSD[n-1];
        }

        AllocateComponentNumbers(z[0], z[1], &comps, &stcomp);
        for(int nc = stcomp; nc < stcomp+comps; nc++){
            if(nc >= m_nseg-1){
                snew = z[1];
            }
            else if(m_zc[nc+1] > z[1]){
                snew = z[1];
            }
            else{
                snew = m_zc[nc+1];
            }
            ds = snew-sold;
            sold = snew;
            MultiplyComponentCSD(nc, ds, m_CSD[n]);
        }
    }

#ifdef _DEBUG
    if(!LatticeDispersion.empty()){
        ofstream debug_out(LatticeDispersion);
        vector<string> titles{"z", "Dx", "Dx'", "Dy", "Dy'"};
        vector<double> items(titles.size());
        PrintDebugItems(debug_out, titles);
        for(int n = 0; n < m_z.size(); n++){
            items[0] = m_z[n];
            for(int j = 0; j < 2; j++){
                items[2*j+1] = m_CSD[n][j][0][2];
                items[2*j+2] = m_CSD[n][j][1][2];
            }
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif
}

void LatticeOperation::PreOperation(
    double lmatch, double *betap, double *alphap, double *betac, double *alphac,
    double *CS, double *SS, double *CSd, double *SSd, double *DS, double *DSd)
{
    ComputeCSSS_Direct(-lmatch, 0, CS, SS, CSd, SSd, DS, DSd);

    vector<vector<double>> twiss{{0, 0, 0}, {0, 0, 0}};
    for(int j = 0; j < 2; j++){
        twiss[j][0] = betap[j];
        twiss[j][1] = alphap[j];
        twiss[j][2] = (1.0+alphap[j]*alphap[j])/betap[j];
    }
    TwissParametersFrom(-lmatch, twiss, 0, twiss);
    for(int j = 0; j < 2; j++){
        betac[j] = twiss[j][0];
        alphac[j] = twiss[j][1];
    }
}

void LatticeOperation::SetBPMError()
{
    double CS[2], SS[2], CSd[2], SSd[2], DS[2], DSd[2];
    double xy[2], xyo[2], xyd[2], xydo[2], theta[2];

    vector<double> zpivot(m_M+1);
    for(int m = 1; m < m_M; m++){
        zpivot[m] = m_stposition[m-1];
    }
    zpivot[0] = m_stposition[0]-m_prm[Und_][interval_];
    zpivot[m_M] = m_stposition[m_M-2]+m_prm[Und_][interval_];

    RandomUtility rand;
    int seed = (int)floor(0.5+m_prm[Alignment_][alrandseed_]);
    rand_init(m_bool[Alignment_][alautoseed_], seed, m_procs, m_rank, &rand, m_thread);

    double xytol[2];
    for(int j = 0; j < 2; j++){
        xytol[j] = m_array[Alignment_][xytol_][j]*1e-3; // mm -> m
        xyo[j] = xytol[j]*rand.Uniform(-1, 1);
        xydo[j] = 0;
    }

#ifdef _DEBUG
    ofstream debug_out;
    vector<string> titles{"z", "x", "y", "x'", "y'", "kickx", "kicky"};
    vector<double> items(titles.size());
    if(!LatticeKickList.empty()){
        debug_out.open(LatticeKickList);
        PrintDebugItems(debug_out, titles);
    }
#endif

    for(int m = 1; m <= m_M; m++){
        for(int j = 0; j < 2; j++){
            xy[j] = xytol[j]*rand.Uniform(-1, 1);
        }
        ComputeCSSS_Direct(zpivot[m-1], zpivot[m], CS, SS, CSd, SSd, DS, DSd);
        for(int j = 0; j < 2; j++){
            theta[j] = (xy[j]-(CS[j]*xyo[j]+SS[j]*xydo[j]+DS[j]))/SS[j];
            xyd[j] = CSd[j]*xyo[j]+SSd[j]*(xydo[j]+theta[j])+DSd[j];
        }

        if(m == 1){ // compute the injection condition (z = 0)
            ComputeCSSS_Direct(zpivot[m], 0, CS, SS, CSd, SSd, DS, DSd);
            for(int j = 0; j < 2; j++){
                m_xyinj[j] = CS[j]*xy[j]+SS[j]*xyd[j]+DS[j];
                m_xydinj[j] = CSd[j]*xy[j]+SSd[j]*xyd[j]+DSd[j];
            }
        }
        else{
            for(int j = 0; j < 2; j++){
                m_stBxy[j][m-2] = theta[j]/m_stT2rad;
            }
        }

#ifdef _DEBUG
        if(!LatticeKickList.empty()){
            items[0] = zpivot[m-1];
            for(int j = 0; j < 2; j++){
                items[j+1] = xyo[j];
                items[j+3] = xydo[j];
                items[j+5] = theta[j];
            }
            PrintDebugItems(debug_out, items);
        }
#endif
        for(int j = 0; j < 2; j++){
            xyo[j] = xy[j];
            xydo[j] = xyd[j];
        }
    }

#ifdef _DEBUG
    if(!LatticeKickList.empty()){
        items[0] = zpivot[m_M];
        for(int j = 0; j < 2; j++){
            items[j+1] = xyo[j];
            items[j+3] = xydo[j];
            items[j+5] = 0;
        }
        PrintDebugItems(debug_out, items);
        debug_out.close();
    }
#endif
}

void LatticeOperation::AllocateComponentNumbers(
    double s1, double s2, int *comps, int *stcomp)
{
    int isega, isegb;
    double sa, sb;

    sa = min(s1, s2);
    sb = max(s1, s2);

    if(sa < m_zc[0]){
        isega = -1;
    }
    else if(sa < m_zc[1]){
        isega = 0;
    }
    else{
        isega = 1;
        while(isega < m_nseg){
            if(sa >= m_zc[isega] && sa < m_zc[isega+1]){
                if(m_zc[isega+1]-sa < SectionLengthLimit){
                    isega = min(m_nseg, isega+1);
                }
                break;
            }
            isega++;
        }
    }

    if(sb < m_zc[1]){
        isegb = 0;
    }
    else{
        isegb = 1;
        while(isegb < m_nseg){
            if(sb > m_zc[isegb] && sb <= m_zc[isegb+1]){
                if(sb-m_zc[isegb] < SectionLengthLimit){
                    isegb = max(1, isegb-1);
                }
                break;
            }
            isegb++;
        }
    }

    *comps = isegb-isega+1;
    *stcomp = isega;
}

void LatticeOperation::CSD_Functions(int iseg, double s,
    double CS[], double CSd[], double SS[], double SSd[], double DS[], double DSd[])
{
    for(int j = 0; j < 2; j++){
        if(iseg < 0){ // drift section before the initial Q. magnet
            twiss_cossindisp_func(s, 0, 0,
                &CS[j], &SS[j], &CSd[j], &SSd[j], &DS[j], &DSd[j]);
        }
        else{
            twiss_cossindisp_func(s, m_kfoc[j][iseg], m_rhoinv[j][iseg],
                &CS[j], &SS[j], &CSd[j], &SSd[j], &DS[j], &DSd[j]);
        }
    }
}

void LatticeOperation::TwissTransferMatrix(
    double s1, double s2, vector<vector<vector<double>>> &Mxy)
{
    double s, ds, sa, sb;
    int isega, isegb, i;
    vector<vector<double>> Mtmp = UnitMatrix;

    sa = min(s1, s2);
    sb = max(s1, s2);

    if(sa < m_zc[0]){
        isega = -1;
    }
    else if(sa < m_zc[1]){
        isega = 0;
    }
    else{
        isega = 1;
        while(isega < m_nseg-1){
            if(sa >= m_zc[isega]
                    && sa < m_zc[isega+1]){
                break;
            }
            isega++;
        }
    }

    if(sb < m_zc[1]){
        isegb = 0;
    }
    else{
        isegb = 1;
        while(isegb < m_nseg-1){
            if(sb >= m_zc[isegb]
                    && sb < m_zc[isegb+1]){
                break;
            }
            isegb++;
        }
    }

    s = sa;
    for(i = isega; i <= isegb; i++){
        if(i >= m_nseg){
            ds = sb-s;
        }
        else if(m_zc[i+1] > sb){
            ds = sb-s;
        }
        else{
            ds = m_zc[i+1]-s;
        }
        MultiplyComponent(i, ds, Mxy);
        if(i >= m_nseg) break;
        s = m_zc[i+1];
    }
    if(s1 > s2){
        for(int j = 0; j < 2; j++){
            Mxy[j] = inverse_matrix(Mxy[j]);
        }
    }
}

void LatticeOperation::MultiplyComponent(
    int iseg, double ds, vector<vector<vector<double>>> &Mxy)
{
    vector<vector<double>> Mtmp = UnitMatrix;
    for(int j = 0; j < 2; j++){
        if(iseg < 0){
            twiss_matrix(ds, 0, Mtmp);
        }
        else{
            twiss_matrix(ds, m_kfoc[j][iseg], Mtmp);
        }
        Mxy[j] = matrix_product(Mtmp, Mxy[j]);
    }
}
                                                                                            
void LatticeOperation::MultiplyComponentCSD(
    int iseg, double ds, vector<vector<vector<double>>> &Mxy)
{
    double CS[2], SS[2], CSd[2], SSd[2], DS[2], DSd[2];
    vector<vector<double>> Mtmp = UnitMatrix;

    CSD_Functions(iseg, ds, CS, CSd, SS, SSd, DS, DSd);

    for(int j = 0; j < 2; j++){
        csd_matrix(CS[j], CSd[j], SS[j], SSd[j], DS[j], DSd[j], Mtmp);
        Mxy[j] = matrix_product(Mtmp, Mxy[j]);
    }
}

void LatticeOperation::ComputeCSSS_Direct(double s1, double s2,
    double *CS, double *SS, double *CSd, double *SSd, double *DS, double *DSd)
{
    double ds, sa, sb, sold, snew;
    int comps, stcomp, nc;

    vector<vector<vector<double>>> Mxy {UnitMatrix, UnitMatrix};

    sa = min(s1, s2);
    sb = max(s1, s2);

    AllocateComponentNumbers(sa, sb, &comps, &stcomp);

    sold = sa;
    for(nc = stcomp; nc < stcomp+comps; nc++){
        if(nc >= m_nseg-1){
            snew = sb;
        }
        else if(m_zc[nc+1] > sb){
            snew = sb;
        }
        else{
            snew = m_zc[nc+1];
        }
        ds = snew-sold;
        sold = snew;
        MultiplyComponentCSD(nc, ds, Mxy);
    }
    if(s1 > s2){
        for(int j = 0; j < 2; j++){
            Mxy[j] = inverse_matrix(Mxy[j]);
        }
    }

    for(int j = 0; j < 2; j++){
        CS[j] = Mxy[j][0][0];
        SS[j] = Mxy[j][0][1];
        DS[j] = Mxy[j][0][2];
        CSd[j] = Mxy[j][1][0];
        SSd[j] = Mxy[j][1][1];
        DSd[j] = Mxy[j][1][2];
    }
}

void LatticeOperation::GetTwissParametersAt(int n, double *beta, double *alpha)
{
    vector<vector<double>> twiss{{0, 0, 0}, {0, 0, 0}};
    vector<vector<double>> betaxy(2);
    vector<double> zarr;

    for(int j = 0; j < 2; j++){
        twiss[j][0] = m_betaini[j];
        twiss[j][1] = m_alphaini[j];
        twiss[j][2] = (1.0+m_alphaini[j]*m_alphaini[j])/m_betaini[j];
    }
    TwissParametersFrom(0, twiss, m_z[n], twiss);
    for(int j = 0; j < 2; j++){
        beta[j] = twiss[j][0];
        alpha[j] = twiss[j][1];
    }
}

void LatticeOperation::TwissParametersAlongz(vector<vector<double>> *betaarr, double *avbetaxy, bool periodic)
{
    vector<vector<double>> twiss {{0, 0, 0}, {0, 0, 0}};
    vector<vector<double>> betaxy(2);
    vector<double> zarr;

    if(periodic){
        zarr.resize(m_segsteps);
        copy(m_z.begin(), m_z.begin()+m_segsteps, zarr.begin());
    }
    else{
        zarr = m_z;
    }

    zarr.insert(zarr.begin(), 0);
    for(int j = 0; j < 2; j++){
        betaxy[j].resize(zarr.size());
        betaxy[j][0] = m_betaini[j];
        twiss[j][0] = m_betaini[j];
        twiss[j][1] = m_alphaini[j];
        twiss[j][2] = (1.0+m_alphaini[j]*m_alphaini[j])/m_betaini[j];
    }

    for(int n = 1; n < zarr.size(); n++){
        TwissParametersFrom(zarr[n-1], twiss, zarr[n], twiss);
        for(int j = 0; j < 2; j++){
            betaxy[j][n] = twiss[j][0];
        }
    }

    if(betaarr != nullptr){
        betaarr->resize(3);
        (*betaarr)[0] = zarr;
        for(int j = 0; j < 2; j++){
            (*betaarr)[j+1] = betaxy[j];
        }
    }

    if(avbetaxy != nullptr){
        for(int j = 0; j < 2; j++){
            avbetaxy[j] = vectorsum(betaxy[j], -1)/zarr.size();
        }
    }

#ifdef _DEBUG
    if(avbetaxy == nullptr && !LatticeBeta.empty()){
        ofstream debug_out(LatticeBeta);
        vector<string> titles{"z", "betax", "betay"};
        vector<double> items(titles.size());
        PrintDebugItems(debug_out, titles);
        for(int n = 0; n < zarr.size(); n++){
            items[0] = zarr[n];
            for(int j = 0; j < 2; j++){
                items[j+1] = betaxy[j][n];
            }
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif
}

void LatticeOperation::GetFocusingSystem(vector<double> &zarr, vector<vector<double>> &kxy)
{
    zarr.resize((m_nseg-1)*2);
    kxy.resize(2);
    for(int j = 0; j < 2; j++){
        kxy[j].resize((m_nseg-1)*2);
    }

    for(int n = 0; n < m_nseg-1; n++){
        zarr[2*n] = m_zc[n];
        zarr[2*n+1] = m_zc[n+1];
        for(int j = 0; j < 2; j++){
            kxy[j][2*n] = kxy[j][2*n+1] = m_kfoc[j][n];
        }
    }
}

void LatticeOperation::TwissParametersFrom(
    double s0, vector<vector<double>> &twiss0, double s, vector<vector<double>> &twiss)
{
    vector<vector<vector<double>>> Mxy{UnitMatrix, UnitMatrix};

    TwissTransferMatrix(s0, s, Mxy);
    for(int j = 0; j < 2; j++){
        twiss[j] = vector_product(Mxy[j], twiss0[j]);
    }
}

bool LatticeOperation::AdjustInitialCondition(double beta0[], double alpha0[])
{
    double CS[2], SS[2], CSd[2], SSd[2], DS[2], DSd[2], den, lper, st = 0.0;

    if(m_select[Lattice_][ltype_] == CombinedLabel && m_M == 1){
        lper = (m_position[1]-m_position[0])*2.0;
        st = m_position[0]-lper*0.25;
    }
    else if(m_M ==1){
        st = 0;
        lper = m_prm[Und_][length_];
    }
    else if(m_select[Lattice_][ltype_] == FUDULabel || m_select[Lattice_][ltype_] == DUFULabel){
        lper = 2.0*m_prm[Und_][interval_];
    }
    else{
        lper = m_prm[Und_][interval_];
    }

    ComputeCSSS_Direct(st, lper+st, CS, SS, CSd, SSd, DS, DSd);

    for(int j = 0; j < 2; j++){
        if(fabs(SS[j]) < INFINITESIMAL){
            beta0[j] = -1.0;
            alpha0[j] = 0.0;
            continue;
        }
        den = (CS[j]+SSd[j])*0.5;
        den = 1.0-den*den;
        if(den < INFINITESIMAL){
            if(m_M == 1){
                beta0[j] = m_prm[Und_][length_];
                alpha0[j] = 1;
            }
            else{
                beta0[j] = -1.0;
                alpha0[j] = 0.0;
            }
        }
        else{
            beta0[j] = fabs(SS[j])/sqrt(den);
            alpha0[j] = (CS[j]-SSd[j])/2.0/SS[j]*beta0[j];
        }
    }

    if(m_select[Lattice_][ltype_] == CombinedLabel && m_M == 1){
        vector<vector<double>> twiss{{0, 0, 0}, {0, 0, 0}};
        for(int j = 0; j < 2; j++){
            twiss[j][0] = beta0[j];
            twiss[j][1] = alpha0[j];
            twiss[j][2] = (1.0+alpha0[j]*alpha0[j])/beta0[j];
        }
        TwissParametersFrom(st, twiss, 0, twiss);
        for(int j = 0; j < 2; j++){
            beta0[j] = twiss[j][0];
            alpha0[j] = twiss[j][1];
        }
    }

    if(beta0[0] < INFINITESIMAL || beta0[1] < INFINITESIMAL){
        return false;
    }

    for(int j = 0; j < 2; j++){
        m_betaini[j] = beta0[j];
        m_alphaini[j] = alpha0[j];
    }
    return true;
}

bool LatticeOperation::OptimizeGradient(double betatgt[], double qgradient[], double beta0[], double alpha0[])
{
    double err[2], xovd[3], cost[3], avbetaxy[2], dif[2];
    double betaold[2] = {0, 0};
    double incr[2] = {2, 1.01};
    double acc[2] = {0.01, 0.1}; // normalized accuracy for (0) q-gradient, and (1) ratio

    m_opttarget[0] = sqrt(betatgt[0]*betatgt[1]);
    m_opttarget[1] = betatgt[0]/betatgt[1];

    double eps = fabs(m_prm[PreP_][tolbeta_])*m_opttarget[0];

    m_qopt[0] = m_qtypical;
    m_qopt[1] = 1;

    for(int j = 0; j < 2; j++){
        m_orgcost[j] = -1;
        m_optratio = j > 0;
        m_orgcost[j] = CostFunc(m_qopt[j], nullptr);
        if(m_orgcost[j] < 0){
            return false;
        }
    }

    do {
        for(int j = 0; j < 2; j++){
            m_optratio = j > 0;
            xovd[0] = m_qopt[j]/incr[j];
            xovd[1] = m_qopt[j];
            xovd[2] = m_qopt[j]*incr[j];
            for(int i = 0; i < 3; i++){
                cost[i] = CostFunc(xovd[i], nullptr);
            }
            if((cost[0]-cost[1])*(cost[1]-cost[2]) > 0){
                double rincr;
                if(cost[0] < cost[1]){
                    rincr = 1/incr[j];
                    swap(cost[0], cost[2]);
                    swap(xovd[0], xovd[2]);
                }
                else{
                    rincr = incr[j];
                }
                do{
                    for(int i = 0; i <= 1; i++){
                        cost[i] = cost[i+1];
                        xovd[i] = xovd[i+1];
                    }
                    xovd[2] = xovd[1]*rincr;
                    cost[2] = CostFunc(xovd[2], nullptr);

                } while(cost[2] < cost[1]);
            }
            BrentMethod(xovd[0], xovd[1], xovd[2], acc[j], true, eps, &m_qopt[j], nullptr);
        }
        TwissParametersAlongz(nullptr, avbetaxy, true);
        for(int j = 0; j < 2; j++){
            dif[j] = fabs(avbetaxy[j]-betaold[j]);
            err[j] = min(dif[j], fabs(avbetaxy[j]-betatgt[j]));
            betaold[j] = avbetaxy[j];
        }
    } while(max(err[0], err[1]) > eps);

    for(int j = 0; j < 2; j++){
        qgradient[j] = m_qgradient[j];
        beta0[j] = m_betaini[j];
        alpha0[j] = m_alphaini[j];
    }
    return true;
}

double LatticeOperation::CostFunc(double x, vector<double> *y)
{
    double gradient[] = {0, 0};
    if(m_select[Lattice_][ltype_] == FUFULabel){
        gradient[0] = x;
    }
    else if(m_optratio){
        gradient[0] = m_qopt[0]*x;
        gradient[1] = -m_qopt[0]/x;
    }
    else{
        gradient[0] = x*m_qopt[1];
        gradient[1] = -x/m_qopt[1];
    }
    for(int j = 0; j < 2; j++){
        m_qgradient[j] = gradient[j];
    }
    f_SetQStrength(gradient);

    double ans;
    double avbetaxy[2] = {0, 0};
    if(!AdjustInitialCondition(m_betaini, m_alphaini)){
        if(m_select[Lattice_][ltype_] == FUFULabel || m_optratio){
            ans = m_orgcost[1]*2;
        }
        else{
            ans = m_orgcost[0]*2;
        }
        return ans;
    }
    TwissParametersAlongz(nullptr, avbetaxy, true);

    if(m_select[Lattice_][ltype_] == FUFULabel || m_optratio){
        ans = m_opttarget[0]*fabs(avbetaxy[0]/avbetaxy[1]-m_opttarget[1]);
    }
    else{
        ans = fabs(sqrt(avbetaxy[1]*avbetaxy[0])-m_opttarget[0]);
    }
    return ans;
}

void LatticeOperation::Move(int n, double xy0[], int icd, double xy[])
// icd = 0/1 : position/momentum
{
    for(int j = 0; j < 2; j++){
        xy[j] = 
            m_CSD[n][j][icd][0]*xy0[2*j  ]+
            m_CSD[n][j][icd][1]*xy0[2*j+1]+
            m_CSD[n][j][icd][2];
    }
}

void LatticeOperation::GetCSDElements(vector<int> &steps, float *CSD)
{
    for(int i = 0; i < steps.size(); i++){
        int k = 0;
        for(int j = 0; j < 2; j++){
            for(int icd = 0; icd < 2; icd++){
                for(int cs = 0; cs < 3; cs++){
                    CSD[12*i+k] = (float)m_CSD[steps[i]][j][icd][cs];
                    k++;
                }
            }
        }
    }
}

void LatticeOperation::GetDispersionArray(vector<vector<double>> &xy, int icd)
{
    double xy0[4];

    xy.resize(2);
    for(int j = 0; j < 2; j++){
        xy[j].resize(m_totalsteps);
        if(m_bool[Dispersion_][einjec_]){
            xy0[2*j] = m_array[Dispersion_][exy_][j]*1e-3; // mm -> m
            xy0[2*j+1] = m_array[Dispersion_][exyp_][j]*1e-3; // mm -> m
        }
        else{
            xy0[2*j] = xy0[2*j+1] = 0;
        }
    }

    double xyr[2];
    for(int n = 0; n < m_totalsteps; n++){
        Move(n, xy0, icd, xyr);
        for(int j = 0; j < 2; j++){
            xy[j][n] = xyr[j];
        }
    }
}

// private functions
void LatticeOperation::f_SetQStrength(double gradient[])
{
    vector<double> dBd(m_ntcomp, 0);
    for(int n = 0; n < m_ncomp; n++){
        // magnet length
        if(m_select[Lattice_][ltype_] == FUFULabel){
            dBd[n] = gradient[0];
        }
        else if(m_select[Lattice_][ltype_] == TripletLabel){
            if(n%3 == 1){ // central Q
                dBd[n] = gradient[1];
            }
            else{
                dBd[n] = gradient[0];
            }
        }
        else if(m_select[Lattice_][ltype_] == DUFULabel){
            dBd[n] = gradient[(n+1)%2];
        }
        else{
            dBd[n] = gradient[n%2];
        }
    }

    for(int j = 0; j < 2; j++){
        fill(m_kfoc[j].begin(), m_kfoc[j].end(), 0);
        fill(m_rhoinv[j].begin(), m_rhoinv[j].end(), 0);
    }

    double cE = CC*1.0e-9/m_eGeV;
    for(int n = 0; n < m_nseg-1; n++){
        double isign[] = {1, -1};
        for(int nq = 0; nq < m_nq[n].size(); nq++){
            for(int j = 0; j < 2; j++){
                m_kfoc[j][n] += isign[j]*cE*dBd[m_nq[n][nq]];
            }
        }
        for(int j = 0; j < 2; j++){
            for(int nu = 0; nu < m_Bpeak[j][n].size(); nu++){
                m_kfoc[j][n] += 0.5*cE*cE*m_Bpeak[j][n][nu]*m_Bpeak[j][n][nu];
            }
        }
    }
}

