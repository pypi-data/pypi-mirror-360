#include <iomanip>
#include "particle_handler.h"
#include "lattice_operations.h"
#include "radiation_handler.h"
#include "wakefield.h"
#include "common.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

constexpr auto NONZEROCURRENT = 1e-6;
constexpr auto CUSTOMPARTMIXTURE = 1e-2;

string ParticleSPXIcurr;
string ParticleEtInitial;
string ParticleXYInitial;
string ParticleEt;
string ParticleXY;
string ParticleRadFld;
string ParticlBfactor;
string ParticleBeamSize;
int MaxParticleExports = 20000;

ParticleHandler::ParticleHandler(
	SimplexSolver &sxsolver, LatticeOperation *lattice, PrintCalculationStatus *status)
	: SimplexSolver(sxsolver)
{
	m_lattice = lattice;
	status->SetSubstepNumber(1, 3); // memory allocation, XY, Et
	status->ResetCurrentStep(1);

#ifdef _DEBUG
	ParticleSPXIcurr = "..\\debug\\particle_spx_curr.dat";
	ParticleEtInitial = "..\\debug\\particle_Et_init.dat";
	ParticleXYInitial = "..\\debug\\particle_XY_init.dat";
	ParticleEt = "..\\debug\\particle_Et.dat";
	ParticleXY = "..\\debug\\particle_XY.dat";
//	ParticleRadFld = "..\\debug\\particle_rad_fld.dat";
//	ParticlBfactor = "..\\debug\\particle_bfactor.dat";
	ParticleBeamSize = "..\\debug\\particle_beamsize.dat";
#endif

	if(m_ispostproc){
		m_ntotal = (int)floor(0.5+m_prm[PostP_][bmletspp_]);
		m_ntE = (int)floor(0.5+m_prm[PostP_][particlespp_]);
	}
	else{
		if(m_select[EBeam_][bmprofile_] == SimplexOutput){
			m_ntotal = m_simbeamlets;
			m_ntE = m_simparticles;
		}
		else if(!m_lasermod && m_select[SimCtrl_][simoption_] == RealElectronNumber){
			if(m_select[EBeam_][bmprofile_] == CustomParticle){
				f_XYEtCustom(true);
			}
			else{
				f_SetEt(true);
			}
			m_ntotal = (size_t)floor(0.5+m_charge/QE);
			m_ntotal -= m_ntotal%m_procs;
			m_ntE = 1;
		}
		else{
			m_ntotal = (int)floor(0.5+m_prm[SimCtrl_][beamlets_]);
			if(m_steadystate){
				m_ntotal = (int)floor(0.5+m_prm[SimCtrl_][slicebmletsss_]);
			}
			m_ntotal -= m_ntotal%m_procs;

			if(m_select[SimCtrl_][simoption_] == KillQuiteLoad){
				m_ntE = 1;
			}
			else{
				m_ntE = (int)floor(0.5+m_prm[SimCtrl_][particles_]);
			}
		}
	}

	for(int j = 0; j < 2; j++){
		m_ws[j].resize(m_nhmax);
	}

	if(m_array[SimCtrl_][simrange_][0] > m_array[SimCtrl_][simrange_][1]){
		swap(m_array[SimCtrl_][simrange_][0], m_array[SimCtrl_][simrange_][1]);
	}

	double ds, mbsrange[2];
	if(m_lasermod){
		int partslice = (int)floor(0.5+m_prm[Mbunch_][mbparticles_]);
		ds = m_lambda1/partslice;
		if(m_array[Mbunch_][mbtrange_][0] > m_array[Mbunch_][mbtrange_][1]){
			swap(m_array[Mbunch_][mbtrange_][0], m_array[Mbunch_][mbtrange_][1]);
		}
		for(int j = 0; j < 2; j++){
			mbsrange[j] = m_array[Mbunch_][mbtrange_][j]+m_lambda1*(2*j-1);
		}
		m_ntotal = (int)floor((mbsrange[1]-mbsrange[0])/ds+0.5)+1;
		m_ntE = 1;
	}

	m_nproc = m_ntotal/m_procs;
	f_ArrangeMemory(true);

	for(int j = 0; j < 3; j++){
		m_index[j].resize(m_nproc);
	}
	m_dsq.resize(m_nproc);
	m_Eloss.resize(m_totalsteps);
	m_Esq.resize(m_totalsteps);

	m_openfile = m_ispostproc || m_bool[DataDump_][particle_] ||
		m_select[EBeam_][bmprofile_] == SimplexOutput ||
		!ParticleEtInitial.empty() || 
		!ParticleXYInitial.empty() || 
		!ParticleEt.empty();
	if(m_openfile){
		if(m_rank == 0 && (m_ispostproc || m_bool[DataDump_][particle_])){
			m_datapath.replace_extension(".par");
			string partdata = m_datapath.string();
			if(m_ispostproc){
				m_iofile.open(partdata, ios::binary|ios::in);
			}
			else{
				m_iofile.open(partdata, ios::binary|ios::out);
			}
			if(!m_iofile){
				throw runtime_error("Failed to open the particle data file.");
			}
		}
		size_t ndata = max(12*m_exporsteps.size(), max(4*m_nproc, 2*m_ntE*m_nproc));
		// 12: CSD matrix elements (3:C,S,D * 2: C/C' * 2: x/y)
		// 4 : x,x',y,y'
		// 2 : t, E
		m_wsproc = new float[ndata];
		m_wsexport = new float[ndata*m_procs];
	}

	if(!m_ispostproc && !m_lasermod){
		status->AdvanceStep(1);
	}

	int seed = (int)floor(0.5+m_prm[SimCtrl_][randseed_]);
	rand_init(m_bool[SimCtrl_][autoseed_], seed, m_procs, m_rank, &m_rand, m_thread);

	double beta0[2], alpha0[2];
	for(int j = 0; j < 2; j++){
		beta0[j] = m_array[Lattice_][betaxy0_][j];
		alpha0[j] = m_array[Lattice_][alphaxy0_][j];
	}
	bool isgauss = 
		m_select[EBeam_][bmprofile_] != SimplexOutput &&
		m_select[EBeam_][bmprofile_] != CustomParticle;
	if(isgauss){
		for(int j = 0; j < 2; j++){
			m_betaxyw[j] = beta0[j]/(1.0+alpha0[j]*alpha0[j]);
			m_llxy[j] = m_betaxyw[j]*alpha0[j];
		}
	}

	if(m_ispostproc){
		m_sranges[0] = 0;
		m_sranges[1] = m_slices_total-1;
		for(int j = 0; j < 2; j++){
			m_xyat[j].resize(m_nproc);
		}
		return;
	}

	m_tgtslice = -1;
	bool taperon = m_select[Und_][taper_] != NotAvaliable;
	m_taperopt = taperon &&
		(m_select[Und_][opttype_] == TaperOptWhole || m_select[Und_][opttype_] == TaperOptSlice);
	if(m_select[Und_][opttype_] == TaperOptSlice){
		m_tgtslice = (int)floor((m_prm[Und_][slicepos_]-m_s[0])/m_lslice+0.5);
		if(m_tgtslice >= m_slices){
			m_tgtslice = -1;
			m_taperopt = false;
		}
	}

	if(m_lasermod){
		for(int ns = 0; ns < m_ntotal; ns++){
			m_tE[ns][0] = mbsrange[0]+ds*ns;
			m_tE[ns][1] = 0;
		}
		m_sranges[0] = 0;
		m_sranges[1] = m_slices_total-1;
		for(int j = 0; j < 2; j++){
			m_esmpl[j].resize(m_slices_total);
		}
		m_ssmpl.resize(m_slices_total);
		for(int n = 0; n < m_slices_total; n++){
			m_ssmpl[n] = m_s[0]+(n-m_totalsteps)*m_lslice;
		}
	}
	else if(m_select[EBeam_][bmprofile_] == CustomParticle){
		f_XYEtCustom();
		status->AdvanceStep(1, 2);
	}
	else if(m_select[EBeam_][bmprofile_] == SimplexOutput){
		f_XYEtSimplex();
		status->AdvanceStep(1, 2);
	}
	else{
		f_SetEt();
		status->AdvanceStep(1);
		f_SetXYGaussian();
		status->AdvanceStep(1);
	}

	if(m_bool[Dispersion_][einjec_]){
		double xy0[4];
		for(int j = 0; j < 2; j++){
			xy0[2*j] = m_array[Dispersion_][exy_][j]*1e-3; // mm -> m
			xy0[2*j+1] = m_array[Dispersion_][exyp_][j]*1e-3; // mm -> m
		}
		for(size_t n = 0; n < m_nproc; n++){
			for(int j = 0; j < 2; j++){
				m_xy[n][2*j] += xy0[2*j];
				m_xy[n][2*j+1] += xy0[2*j+1];
			}
		}
	}
	f_WriteXY();

	m_wakefield.resize(m_slices, 0.0);
	double wakec = f_GetWakefield(&m_wakefield);

	if(!m_lasermod){
		status->AdvanceStep(0);
	}

	m_detune.resize(m_totalsteps, 0.0);
	m_Ktaper.resize(m_totalsteps, m_K);
	m_deta4K.resize(m_M, 0.0);

	for(int n = 0; n < m_totalsteps; n++){
		if(!m_inund[n]){
			m_Ktaper[n] = 0;
		}
	}

	for(int n = 0; n < m_totalsteps && taperon && m_taperopt == false; n++){
		if(m_inund[n]){
			f_GetKVaried(m_z[n], &m_detune[n], &m_Ktaper[n], wakec);
		}
	}
	f_ArrangeDetuning(m_detune);

	for(int j = 0; j < 2; j++){
		m_frac[j].resize(m_nhmax);
		m_xyat[j].resize(m_nproc);
	}
}

ParticleHandler::ParticleHandler(SimplexSolver &sxsolver)
	: SimplexSolver(sxsolver)
	// constructor to be a parent instance for WakefieldUtility
{
#ifdef _DEBUG
	ParticleSPXIcurr = "..\\debug\\particle_spx_curr.dat";
#endif

	if(m_select[EBeam_][bmprofile_] != SimplexOutput){
		return;
	}
	m_nproc = m_ntotal = m_simbeamlets;
	m_ntE = m_simparticles;

	f_ArrangeMemory(true);

	size_t ndata = max(4*m_nproc, 2*m_ntE*m_nproc);
	m_wsproc = new float[ndata];
	m_wsexport = new float[ndata];
	f_XYEtSimplex();
	delete[] m_wsproc;
	delete[] m_wsexport;
}

ParticleHandler::~ParticleHandler()
{
	if(m_openfile){
		if(m_rank == 0){
			m_iofile.close();
		}
		delete[] m_wsproc;
		delete[] m_wsexport;
	}
	f_ArrangeMemory(false);
}

void ParticleHandler::SetCustomParticles(vector<vector<double>> &particles)
{
	m_custom = particles;
}

void ParticleHandler::SetIndex(int n)
{
	double xy[2];

#ifdef _DEBUG
	vector<double> xypos[4];
	bool isdump = !ParticleBeamSize.empty() || !ParticleXY.empty();
	if(isdump){
		for(int j = 0; j < 4; j++){
			xypos[j].resize(m_nproc*m_procs);
		}
	}
#endif

	for(size_t m = 0; m < m_nproc; m++){
		if(m_steadystate){
			m_index[2][m] = 0;
		}
		else{
			m_index[2][m] = (int)floor((m_tE[m][0]-m_s[0])/m_lslice+0.5)+f_GetSliceOffset(n);
		}
		if(m_lasermod){
			m_index[0][m] = m_index[1][m] = 0;
			m_dsq[m] = 0;
			continue;
		}
		m_lattice->Move(n, m_xy[m], 0, xy); // get position
		if(fabs(xy[0]) > m_Dxy[0] || fabs(xy[1]) > m_Dxy[1]){
			m_index[0][m] = m_index[1][m] = -1;
		}
#ifdef _DEBUG
		if(isdump){
			for(int j = 0; j < 2; j++){
				xypos[j][m] = xy[j];
			}
		}
#endif
		for(int j = 0; j < 2; j++){
			m_xyat[j][m] = xy[j];
			m_index[j][m] = (int)floor(0.5+xy[j]/m_dxy[j]);
			m_index[j][m] = fft_index(m_index[j][m], m_nfft[j], -1);
		}
		m_lattice->Move(n, m_xy[m], 1, xy); // get momentum
#ifdef _DEBUG
		if(isdump){
			for(int j = 0; j < 2; j++){
				xypos[j+2][m] = xy[j];
			}
		}
#endif
		m_dsq[m] = hypotsq(xy[0], xy[1])/2;
	}

#ifdef _DEBUG
	if(isdump && m_procs > 1){
		MPI_Status status;
		double *ws = new double[m_nproc];
		for(int j = 0; j < 4; j++){
			if(m_rank > 0){
				for(size_t m = 0; m < m_nproc; m++){
					ws[m] = xypos[j][m];
				}
			}
			for(int r = 1; r < m_procs; r++){
				if(m_thread != nullptr){
					m_thread->SendRecv(ws, ws, (int)m_nproc, MPI_DOUBLE, r, 0, m_rank);
					if(m_rank == 0){
						for(size_t m = 0; m < m_nproc; m++){
							xypos[j][m+r*m_nproc] = ws[m];
						}
					}
				}
				else{
					if(m_rank == 0){
						MPI_Recv(ws, (int)m_nproc, MPI_DOUBLE, r, 0, MPI_COMM_WORLD, &status);
						for(size_t m = 0; m < m_nproc; m++){
							xypos[j][m+r*m_nproc] = ws[m];
						}
					}
					else if(m_rank == r){
						MPI_Send(ws, (int)m_nproc, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
					}
					MPI_Barrier(MPI_COMM_WORLD);
				}
			}
		}
		delete[] ws;
	}
	if(!ParticleBeamSize.empty() && m_rank ==0){
		double mean[4];
		vector<double> items(5);
		items[0] = m_z[n];
		for(int j = 0; j < 4; j++){
			get_stats(xypos[j], (int)m_nproc*m_procs, &mean[j], &items[j+1]);
		}
		ofstream debug_out(ParticleBeamSize, n==0?ios::out:ios::app);
		if(n == 0){
			vector<string> titles {"z", "sx", "sy", "sx'", "sy'"};
			PrintDebugItems(debug_out, titles);
		}
		PrintDebugItems(debug_out, items);
		debug_out.close();
	}
	if(!ParticleXY.empty() && m_rank ==0){
		for(size_t m = 0; m < m_nproc*m_procs; m++){
			for(int j = 0; j < 2; j++){
				m_wsexport[4*m+2*j] = (float)xypos[j][m];
				m_wsexport[4*m+2*j+1] = (float)xypos[j+2][m];
			}
		}
		if(f_IsExportDebug(n)){
			f_ExportXY(ParticleXY);
		}
	}
	MPI_Barrier(MPI_COMM_WORLD);
#endif

}

void ParticleHandler::GetBunchFactor(vector<vector<double **>> &B)
{
	for(int ns = 0; ns < m_slices_total; ns++){
		for(int nh = 0; nh < m_nhmax; nh++){
			for(int nx = 0; nx < m_nfft[0]; nx++){
				for(int ny = 0; ny < m_nfft[1]; ny++){
					B[nh][ns][nx][2*ny] = B[nh][ns][nx][2*ny+1] = 0;
				}
			}
		}
		if(ns >= m_sranges[0] && ns <= m_sranges[1]){
			m_onslices[ns] = 1;
		}
		else{
			m_onslices[ns] = 0;
		}
	}
	for(size_t m = 0; m < m_nproc; m++){
		if(m_index[0][m] < 0 || m_index[1][m] < 0 || 
				m_index[2][m] < 0 || m_index[2][m] >= m_slices_total){
			continue;
		}
		for(int j = 0; j < m_ntE; j++){
			double phi = -PI2*(m_tE[m][2*j]-m_dsq[m]*m_zstep/2)/m_lambda_s; // bunch factor defined by exp(-i phi)
			for(int nh = 1; nh <= m_nhmax; nh++){
				B[nh-1][m_index[2][m]][m_index[0][m]][2*m_index[1][m]  ] += cos(phi*nh);
				B[nh-1][m_index[2][m]][m_index[0][m]][2*m_index[1][m]+1] += sin(phi*nh);
			}
		}
		m_onslices[m_index[2][m]] = 1;
	}

#ifdef _DEBUG
	if(!ParticlBfactor.empty()){
		vector<string> titles {"x", "y", "Re", "Im"};
		vector<double> values(titles.size());
		ofstream debug_out(ParticlBfactor);
		int sindex = m_slices/2;
		PrintDebugItems(debug_out, titles);
		for(int nx = 0; nx < m_nfft[0]; nx++){
			values[0] = nx;
			for(int ny = 0; ny < m_nfft[1]; ny++){
				values[1] = ny;
				values[2] = B[0][sindex][nx][2*ny];
				values[3] = B[0][sindex][nx][2*ny+1];
				PrintDebugItems(debug_out, values);
			}
		}
		debug_out.close();
	}
#endif

}

void ParticleHandler::GetSliceBunchFactor(int n,
	vector<vector<double *>> &BG, vector<double> bfg[], double bmsize[])
{
	double mp = m_charge/QE/(m_ntE*m_ntotal);

	for(int ns = 0; ns < m_slices_total; ns++){
		for(int nh = 0; nh < m_nhmax; nh++){
			for(int j = 0; j < 2; j++){
				BG[0][nh][ns] = 0;
				for(int g = 1; g < m_BGmodes; g++){
					BG[g][nh][2*ns+j] = 0;
				}
			}
		}
		if(ns >= m_sranges[0] && ns <= m_sranges[1]){
			m_onslices[ns] = 1;
		}
		else{
			m_onslices[ns] = 0;
		}
	}

	double csn[2], tex[2];
	for(size_t m = 0; m < m_nproc; m++){
		if(m_index[0][m] < 0 || m_index[1][m] < 0 ||
			m_index[2][m] < 0 || m_index[2][m] >= m_slices_total){
			continue;
		}
		for(int nh = 0; nh < m_nhmax; nh++){
			for(int j = 0; j < 2; j++){
				tex[j] = m_xyat[j][m]/(bmsize[j]*bfg[j][nh]);
				tex[j] *= tex[j];
			}
			double rtex = tex[0]+tex[1];
			m_frac[0][nh] = exp(-rtex/2)/SQRTPI;
			m_frac[1][nh] = m_frac[0][nh]*(1-rtex);
		}
		for(int j = 0; j < m_ntE; j++){
			double phi = -PI2*(m_tE[m][2*j]-m_dsq[m]*m_zstep/2)/m_lambda_s; // bunch factor defined by exp(-i phi)
			for(int nh = 1; nh <= m_nhmax; nh++){
				csn[0] = cos(phi*nh);
				csn[1] = sin(phi*nh);

				// particle density (for shot noise)
				BG[0][nh-1][m_index[2][m]] += mp;

				// bunch factors
				for(int j = 0; j < 2; j++){
					BG[1][nh-1][2*m_index[2][m]+j] += csn[j]; // total
					BG[2][nh-1][2*m_index[2][m]+j] += csn[j]*m_frac[0][nh-1]; // LG 0th
					BG[3][nh-1][2*m_index[2][m]+j] += csn[j]*m_frac[1][nh-1]; // LG 1st

				}
			}
		}
		m_onslices[m_index[2][m]] = 1;
	}
}

void ParticleHandler::GetRadFieldAt(int np, int nh, int mp, double *Eri)
{
	for(int j = 0; j < 2; j++){
		Eri[j] = m_Efp[np][nh][2*mp+j];
	}
}

void ParticleHandler::AdvanceParticle(int n, 
	vector<vector<vector<vector<double>>>> F[], vector<vector<vector<double **>>> E[], RadiationHandler *radfld)
{
	double Et[2], Eold[2][2], Eg[2], de[4], dphi[4], eta[2], phi[2], phase, dsphi, dzphi, dzeta, phincr;
	double delta[] = {0, 0.5, 0.5, 1};
	int nt, nn, ns, nx, ny;
	bool isgather;

	dsphi = m_lambda_s/PI2;
	dzphi = PI2*m_intstep;
	dzeta = m_inund[n] ? 2/m_gamma/(m_eGeV*1e9) : 0;
	int nsoffset = f_GetSliceOffset(n);
	double dl = m_steadystate ? m_prm[Seed_][relwavelen_] : 0;

	if(m_lasermod){
		for(int j = 0; j < 2; j++){
			m_esmpl[j][0] = E[0][0][1][0][0][j];
			for(int n = 1; n < m_slices_total; n++){
				m_esmpl[j][n] = (E[0][0][1][n][0][j]+E[0][0][2][n-1][0][j])/2;
			}
			m_espl[j].SetSpline((int)m_ssmpl.size(), &m_ssmpl, &m_esmpl[j]);
		}
#ifdef _DEBUG
		ofstream debug_out(ParticleRadFld);
		vector<string> titles{"s", "Ere", "Eim"};
		PrintDebugItems(debug_out, titles);
		vector<double> items(titles.size());
		for(size_t n = 0; n < m_slices_total; n++){
			items[0] = m_ssmpl[n];
			items[1] = m_esmpl[0][n];
			items[2] = m_esmpl[1][n];
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
#endif
	}

	double Emag = 0;
	if(m_isGaussDebug){
		Emag = radfld->GetMaxNearField()+INFINITESIMAL;
	}

	bool ishelical = m_select[Und_][utype_] == HelicalUndLabel;
	double deta, Deta, etar;
	int seg = m_taperopt ? m_segend[n] : -1;
	int mtgt = 0;
	if(seg >= 0){
		m_deta4K[seg] = 0;
	}
	double zqlen = n == 0 ? m_zstep : m_z[n]-m_z[n-1];

	for(size_t m = 0; m < m_nproc; m++){
		nx = m_index[0][m];
		ny = m_index[1][m];
		nt = m_index[2][m];
		nn = nt-1;
		ns = min(max(0, nt-nsoffset), m_slices-1);
		if(m_steadystate){
			nn = nt = ns = 0;
		}
		if(nn < m_sranges[0]){
#ifdef _DEBUGINF
			cout << endl << "rank:" << m_rank << ", n: " << n << " " << nt << "<" << m_sranges[0] << endl;
#endif
			nn = m_sranges[0];
			if(!m_steadystate){
				nt = nn+1;
			}
		}
		else if(nt > m_sranges[1]){
#ifdef _DEBUGINF
			cout << endl << "rank:" << m_rank << ", n: " << n << " " << nt << ">" << m_sranges[1] << endl;
#endif
			nt = m_sranges[1];
			if(!m_steadystate){
				nn = nt-1;
			}
		}

		for(int nh = 0; nh < m_nhmax; nh++){
			for(int j = 0; j < 2; j++){
				m_ws[j][nh] = 0;
			}
			if(nx < 0 || ny < 0 || nn < 0 || nt >= m_slices_total){
				// skip e-field evaluation
				continue;
			}
			if(m_skipwave){
				for(int np = 0; np < m_np; np++){
					for(int j = 0; j < 2; j++){
						Eold[np][j] = m_Efp[np][nh][2*m+j];
					}
				}
				radfld->SetFieldAt((int)m, n, nh, nn, nx, ny, m_Efp);
			}

			for(int np = 0; np < m_np; np++){
				for(int j = 0; j < 2; j++){
					if(m_lasermod){
						double s = m_tE[m][0]-n*m_lslice;
						Et[j] = m_espl[j].GetValue(s);
					}
					else{
						if(m_skipwave){
							Et[j] = (Eold[np][j]+m_Efp[np][nh][2*m+j])/2;
							if(m_isGaussDebug){
								Eg[j] =  Et[j];
								Et[j] = (E[np][nh][1][nt][nx][2*ny+j]+E[np][nh][2][nn][nx][2*ny+j])/2;
							}
						}
						else{
							Et[j] = (E[np][nh][1][nt][nx][2*ny+j]+E[np][nh][2][nn][nx][2*ny+j])/2;
						}
					}
				}
				if(m_isGaussDebug && n >= 0){
					double *Echk[2] = {Et, Eg};
					double mag[2], arg[2] = {0, 0};
					for(int j = 0; j < 2; j++){
						mag[j] = sqrt(hypotsq(Echk[j][0], Echk[j][1]));
						if(mag[j] > 0){
							arg[j] = acos(Echk[j][0]/mag[j]);
						}
					}
					double dmag = fabs(mag[1]-mag[0])/Emag;
					double darg = fabs(arg[1]-arg[0]);
					if(/*abs(nt-ExportSlice) < 100 &&*/ (dmag > 0.1 || (dmag > 0.03 && darg > 0.1))){
						int nidx[2];
						nidx[0] = fft_index(nx, m_nfft[0], 1);
						nidx[1] = fft_index(ny, m_nfft[1], 1);
//						cout << scientific << setprecision(2) << "n/nx/ny=" << n << "/" << nidx[0] << "/" << nidx[1] << ": " << dmag << ", " << darg << endl;
					}
				}

				for(int j = 0; j < 2; j++){
					if(m_isGaussDebug){
						Et[j] = Eg[j];
					}
					if(ishelical){
						Et[j] *= 2;
					}
				}

				m_ws[0][nh] += Et[0]*F[np][nh][n][0][0]+Et[1]*F[np][nh][n][0][1];
				m_ws[1][nh] += Et[0]*F[np][nh][n][0][1]-Et[1]*F[np][nh][n][0][0];
			}
		}

		isgather = seg >= 0 && (ns == m_tgtslice|| m_tgtslice == -1);
		etar = Deta = 0;
		for(int j = 0; j < m_ntE; j++){
			eta[0] = eta[1] = m_tE[m][2*j+1];
			phi[0] = m_tE[m][2*j]/m_lambda_s;
			phi[0] = PI2*(phi[0]-floor(phi[0]));
			phi[1] = phi[0];
			for(int i = 0; i < 4; i++){
				if(i > 0){
					phi[1] = phi[0]+delta[i]*dphi[i-1];
					eta[1] = eta[0]+delta[i]*de[i-1];
				}
				dphi[i] = (2*eta[1]+dl+m_detune[n])*dzphi;
				de[i] = 0;
				for(int nh = 0; nh < m_nhmax; nh++){
					phase = (nh+1)*phi[1];
					de[i] += m_ws[0][nh]*cos(phase)+m_ws[1][nh]*sin(phase);
				}
				de[i] *= dzeta/(1+eta[1]);
			}
			phincr = (dphi[0]+2*dphi[1]+2*dphi[2]+dphi[3])/6;
			m_tE[m][2*j] += phincr*dsphi;
			deta = (de[0]+2*de[1]+2*de[2]+de[3])/6;
			m_tE[m][2*j+1] += deta;

			// shift due to angle
			m_tE[m][2*j] -= m_dsq[m]*zqlen;

			// energy/slippage variation by wake/tapering
			if(m_inund[n]){
				m_tE[m][2*j+1] += m_wakefield[ns];
				deta += m_wakefield[ns];
			}
			if(isgather && m_tE[m][2*j+1] < 0){ // pick up only low-energy (captured) particles 
				etar += m_tE[m][2*j+1];
				Deta += deta;
				mtgt++;
			}
		}
		if(isgather){
			m_deta4K[seg] += Deta;
		}
	}

	m_Esq[n] = m_Eloss[n] = 0;
	for(size_t m = 0; m < m_nproc; m++){
		for(int j = 0; j < m_ntE; j++){
			m_Eloss[n] += m_tE[m][2*j+1];
			m_Esq[n] += m_tE[m][2*j+1]*m_tE[m][2*j+1];
		}
	}

	if(m_procs > 1){
		double tmp = m_Eloss[n];
		if(m_thread != nullptr){
			m_thread->Allreduce(&tmp, &m_Eloss[n], 1, MPI_DOUBLE, MPI_SUM, m_rank);
			tmp = m_Esq[n];
			m_thread->Allreduce(&tmp, &m_Esq[n], 1, MPI_DOUBLE, MPI_SUM, m_rank);
			if(seg >= 0){
				tmp = m_deta4K[seg];
				m_thread->Allreduce(&tmp, &m_deta4K[seg], 1, MPI_DOUBLE, MPI_SUM, m_rank);
				int itmp = mtgt;
				m_thread->Allreduce(&itmp, &mtgt, 1, MPI_INT, MPI_SUM, m_rank);
			}
		}
		else{
			MPI_Allreduce(&tmp, &m_Eloss[n], 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
			tmp = m_Esq[n];
			MPI_Allreduce(&tmp, &m_Esq[n], 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
			if(seg >= 0){
				tmp = m_deta4K[seg];
				MPI_Allreduce(&tmp, &m_deta4K[seg], 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
				int itmp = mtgt;
				MPI_Allreduce(&itmp, &mtgt, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
			}
		}
	}
	m_Esq[n] -= m_Eloss[n]*m_Eloss[n]/(m_ntotal*m_ntE);
	m_Esq[n] = sqrt(m_Esq[n]/(m_ntotal*m_ntE));
	m_Eloss[n] -= m_Einit;
	if(seg >= 0){
		m_deta4K[seg] /= mtgt;
		f_AdjustTaper(n);
	}
	m_Eloss[n] *= m_e2loss;
	if(m_steadystate){
		m_Eloss[n] *= 1e-9/m_dTslice; // J -> GW
	}
	f_ExportData(n);

}

void ParticleHandler::AdvanceChicane(int nstep)
{
	double xy[2];
	double r56 = m_prm[Chicane_][delay_]*1e-15*CC*2;
	bool rearrange = m_bool[Chicane_][rearrange_];

	for(size_t m = 0; m < m_nproc; m++){
		double dsq = 0;
		for(int n = nstep-m_segsteps+1; n <= nstep; n++){
			m_lattice->Move(n, m_xy[m], 1, xy);
			dsq += hypotsq(xy[0], xy[1])/2;
		}
		for(int j = 0; j < m_ntE; j++){
			m_tE[m][2*j] += r56*m_tE[m][2*j+1]-dsq*m_lu*m_intstep;
		}
		if(rearrange){
			int ntE = m%m_ntE;
			for(int j = 0; j < m_ntE; j++){
				m_tE[m][2*j] = m_tE[m][2*ntE]+m_lambda_s/m_ntE*(j-ntE);
				m_tE[m][2*j+1] = m_tE[m][2*ntE+1];
			}
		}
	}
	if(rearrange){
		f_AddShotnoize();
	}
	f_ExportData(nstep);
}

double ParticleHandler::GetTotalBunchFactor(int nh)
{
	vector<double> bf[2];
	for(int j = 0; j < 2; j++){
		bf[j].resize(m_slices, 0);
	}
	for(size_t m = 0; m < m_nproc; m++){
		int sindex = (int)floor((m_tE[m][0]-m_s[0])/m_lslice+0.5);
		if(sindex < 0 || sindex >= m_slices){
			continue;
		}
		for(int j = 0; j < m_ntE; j++){
			double phi = -PI2*m_tE[m][2*j]/m_lambda_s; // bunch factor defined by exp(-i phi)
			bf[0][sindex] += cos((nh+1)*phi);
			bf[1][sindex] += sin((nh+1)*phi);
		}
	}
	if(m_procs > 1){
		for(int ns = 0; ns < m_slices; ns++){
			for(int j = 0; j < 2; j++){
				double temp = bf[j][ns];
				if(m_thread != nullptr){
					m_thread->Allreduce(&temp, &bf[j][ns], 1, MPI_DOUBLE, MPI_SUM, m_rank);
				}
				else{
					MPI_Allreduce(&temp, &bf[j][ns], 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
				}
			}
		}
	}
	double tbf = 0;
	for(int ns = 0; ns < m_slices; ns++){
		tbf += sqrt(hypotsq(bf[0][ns], bf[1][ns]));
	}
	tbf /= m_ntotal*m_ntE;
	return tbf;
}

void ParticleHandler::GetParameters(double *q2E, double *ptotal)
{
	*q2E = -Z0VAC/2/m_gamma*(m_charge/m_ntotal/m_ntE)/m_dTslice;
	*ptotal = (double)m_ntotal*m_ntE;
}

void ParticleHandler::GetEnergyStats(vector<double> &Eloss, vector<double> &Espread)
{
	Eloss = m_Eloss;
	Espread = m_Esq;
}

void ParticleHandler::GetParticlesEt(vector<vector<double>> &tE)
{
	tE.resize(m_ntotal);
	for(int n = 0; n < m_ntotal; n++){
		tE[n].resize(2*m_ntE);
		for(int j = 0; j < 2*m_ntE; j++){
			tE[n][j] = m_tE[n][j];
		}
	}
}

void ParticleHandler::DoPostProcess(PrintCalculationStatus *status,
	vector<string> &titles, vector<string> &units, int *variables, vector<vector<double>> &vararray, vector<vector<vector<double>>> &data)
{
	int steprange[2], nrange[2], slicerange[2];
	vector<double> zarr, sarr;
	vector<vector<double>> xyarr(2);

	f_ArrangePostProcessing(zarr, sarr, xyarr, steprange, slicerange, nrange);

	int nsteps = steprange[1]-steprange[0]+1;
	int nslices = slicerange[1]-slicerange[0]+1;
	int ngrids = (2*nrange[0]+1)*(2*nrange[1]+1);

	titles.clear(); units.clear();
	int nslides[2] = {1, 1};

	int nvariables = ngrids;
	bool ispart = m_select[PostP_][item_] == PostPPartDistLabel;
	bool isedist = m_select[PostP_][item_] == PostPEnergyLabel;
	*variables = 2;
	if(ispart){
		nslides[0] = nsteps;
		titles.push_back(ZLabel);
		titles.push_back(SLabel);
		if(m_select[PostP_][coord_] == PostPtXLabel){
			titles.push_back(XLabel);
		}
		else if(m_select[PostP_][coord_] ==PostPtYLabel){
			titles.push_back(YLabel);
		}
		else{
			titles.push_back(EtaLabel);
		}
		*variables = 1;
	}
	else{ // bunch factor || energy distribution
		if(m_isppoxy){
			nslides[0] = nsteps;
			nvariables = nslices;
			titles.push_back(SLabel);
			*variables = 1;
		}
		else{
			titles.push_back(XLabel);
			titles.push_back(YLabel);
			nslides[0] = nsteps;
			if(!m_isppalongs){
				nslides[1] = nslices;
				titles.push_back(SLabel);
			}
		}
		titles.push_back(ZLabel);
	}

	int dimensions = (int)titles.size();

	vararray.clear();
	for(int n = 0; n < dimensions; n++){
		if(titles[n] == XLabel){
			units.push_back(XYUnit);
			if(!ispart){
				vararray.push_back(xyarr[0]);
			}
		}
		else if(titles[n] == YLabel){
			units.push_back(XYUnit);
			if(!ispart){
				vararray.push_back(xyarr[1]);
			}
		}
		else if(titles[n] == SLabel){
			units.push_back(SUnit);
			if(!ispart){
				vararray.push_back(sarr);
			}
		}
		else if(titles[n] == ZLabel){
			units.push_back(ZUnit);
			vararray.push_back(zarr);
		}
		else if(titles[n] == EtaLabel){
			units.push_back(NoUnit);
		}
	}
	
	vector<int> jxyindex, counts;
	vector<vector<double>> eta;
	if(isedist){
		titles.push_back(SliceElossLabel);
		units.push_back(SliceEUnit);
		titles.push_back(SliceEsprdabel);
		units.push_back(SliceEUnit);
		counts.resize(m_slices);
		eta.resize(m_slices);
	}
	else if(!ispart){
		bool isreal = true, isimag = true;
		if(m_select[PostP_][realimag_] == PostPRealLabel){
			isimag = false;
		}
		else if(m_select[PostP_][realimag_] == PostPImagLabel){
			isreal = false;
		}
		if(isreal){
			titles.push_back(BRealLabel);
			units.push_back(BunchFactorUnit);
			jxyindex.push_back(0);
		}
		if(isimag){
			titles.push_back(BImagLabel);
			units.push_back(BunchFactorUnit);
			jxyindex.push_back(1);
		}
	}

	int nitems = max(1, (int)titles.size()-dimensions);
	// data[slides][item][variable]
	data.resize(nslides[0]*nslides[1]);
	for(int ns = 0; ns < nslides[0]*nslides[1]; ns++){
		data[ns].resize(nitems);
		for(int i = 0; i < nitems; i++){
			if(!ispart){
				data[ns][i].resize(nvariables);
				fill(data[ns][i].begin(), data[ns][i].end(), 0);
			}
		}
	}

	vector<vector<double **>> B;
	vector<double> partmp[2];
	
	if(ispart){
		for(int j = 0; j < 2; j++){
			partmp[j].resize(m_ntotal*m_ntE);
		}
	}
	else{
		B.resize(m_nhmax);
		for(int nh = 0; nh < m_nhmax; nh++){
			B[nh].resize(m_slices_total);
			for(int ns = 0; ns < m_slices_total; ns++){
				B[nh][ns] = new double *[m_nfft[0]];
				for(int n = 0; n < m_nfft[0]; n++){
					B[nh][ns][n] = new double[2*m_nfft[1]];
				}
			}
		}
	}

	double xy[2];
	double sini = m_s[slicerange[0]]-m_lslice/2;
	double sfin = m_s[slicerange[1]]+m_lslice/2;

	bool isppeta = m_select[PostP_][coord_] == PostPtetaLabel;
	bool isppx = m_select[PostP_][coord_] == PostPtXLabel;
	bool isppy = m_select[PostP_][coord_] == PostPtYLabel;

	int steps = steprange[1]-steprange[0]+1;
	if(ispart){
		steps *= 2;
	}
	else{
		steps *= 4;
	}
	status->SetSubstepNumber(0, steps);

	// get initial position (4D), this should be done first
	f_ReadXY(&m_iofile);

	// get maximum particles in a slice at the intial step
	f_ReadEt(&m_iofile, 0);
	SetIndex(0);
	vector<double> mcounts(m_slices_total, 0);
	for(int m = 0; m < m_ntotal; m++){
		if(m_index[2][m] >= 0 && m_index[2][m] < m_slices_total){
			mcounts[m_index[2][m]]++;
		}
	}
	double maxcounts = minmax(mcounts, true)*m_ntE;
	if(isedist){
		for(int n = 0; n < m_slices; n++){
			eta[n].resize(2*m_ntE*(int)maxcounts);
		}
	}

	for(int next = steprange[0]; next <= steprange[1]; next++){
		f_ReadEt(&m_iofile, next);
		status->AdvanceStep(0);

		int nidx = next-steprange[0], sidx, vidx;

		for(size_t m = 0; m < m_ntotal; m++){
			for(int j = 0; j < m_ntE; j++){
				m_tE[m][2*j] += m_tE[m][2*j+1]*m_prm[PostP_][r56pp_];
			}
		}

		if(ispart){
			size_t ninslice = 0;
			for(size_t m = 0; m < m_ntotal; m++){
				bool isxyalloc = false;
				for(int j = 0; j < m_ntE; j++){
					if(m_steadystate || (sfin-m_tE[m][2*j])*(sini-m_tE[m][2*j]) <= 0){
						partmp[0][ninslice] = m_tE[m][2*j]*1e3; // m -> mm
						if(isppeta){
							partmp[1][ninslice] = m_tE[m][2*j+1];
						}
						else{
							if(!isxyalloc){
								m_lattice->Move(m_exporsteps[next], m_xy[m], 0, xy);
								isxyalloc = true;
							}
							if(isppx){
								partmp[1][ninslice] = xy[0]*1e3; // m -> mm
							}
							else if(isppy){
								partmp[1][ninslice] = xy[1]*1e3; // m -> mm
							}
						}
						ninslice++;
					}
				}
			}
			data[nidx][0].resize(2*ninslice);
			for(size_t n = 0; n < ninslice; n++){
				data[nidx][0][n] = partmp[0][n];
				data[nidx][0][n+ninslice] = partmp[1][n];
			}
			status->AdvanceStep(0);
			continue;
		}

		int nsoffset = f_GetSliceOffset(m_exporsteps[next]);
		SetIndex(m_exporsteps[next]);
		status->AdvanceStep(0);

		if(isedist){
			fill(counts.begin(), counts.end(), 0);
			for(int n = 0; n < m_slices; n++){
				fill(eta[n].begin(), eta[n].end(), 0.0);
			}
			for(size_t m = 0; m < m_ntotal; m++){
				int ns = m_index[2][m]-nsoffset;
				if(ns < 0 || ns >= m_slices){
					continue;
				}
				for(int j = 0; j < m_ntE; j++){
					eta[ns][counts[ns]++] = m_tE[m][2*j+1];
					if(counts[ns] > eta[ns].size()){
						eta[ns].resize(counts[ns]+(int)maxcounts);
					}
				}
			}
			status->AdvanceStep(0);

			for(int nq = slicerange[0]; nq <= slicerange[1]; nq++){
				if(counts[nq] == 0){
					data[nidx][0][nq-slicerange[0]] = data[nidx][1][nq-slicerange[0]] = 0;
				}
				else{
					get_stats(eta[nq], counts[nq], &data[nidx][0][nq-slicerange[0]], &data[nidx][1][nq-slicerange[0]]);
				}
			}

			status->AdvanceStep(0);

			continue;
		}

		GetBunchFactor(B);
		status->AdvanceStep(0);

		for(int ny = -nrange[1]; ny <= nrange[1]; ny++){
			int iy = fft_index(ny, m_nfft[1], -1);
			for(int nx = -nrange[0]; nx <= nrange[0]; nx++){
				int ix = fft_index(nx, m_nfft[0], -1);
				if(!m_isppoxy){
					vidx = (ny+nrange[1])*(2*nrange[0]+1)+nx+nrange[0];
				}
				for(int nq = slicerange[0]; nq <= slicerange[1]; nq++){
					if(m_isppoxy){
						if(m_isppalongs){
							vidx = nidx;
							sidx = 0;
						}
						else{
							vidx = nq-slicerange[0];
							sidx = nidx;
						}
					}
					else{
						if(m_isppalongs){
							sidx = nidx;
						}
						else{
							sidx = nidx*(slicerange[1]-slicerange[0]+1)+(nq-slicerange[0]);
						}
					}
					int lq = nq+nsoffset;
					for(int i = 0; i < nitems; i++){
						data[sidx][i][vidx] += B[m_nhpp][lq][ix][2*iy+jxyindex[i]]/m_ntotal/m_ntE;
					}
				}
			}
		}
		status->AdvanceStep(0);
	}

	if(!ispart){
		for(int nh = 0; nh < m_nhmax; nh++){
			for(int ns = 0; ns < m_slices_total; ns++){
				for(int n = 0; n < m_nfft[0]; n++){
					delete[] B[nh][ns][n];
				}
				delete[] B[nh][ns];
			}
		}
	}
}

void ParticleHandler::ExportKValueTrend(vector<string> &categs, vector<string> &results)
{
	vector<string> titles{ZLabel, KLabel};
	vector<string> units{ZUnit, NoUnit};
	vector<vector<double>> vararray(1);
	vector<vector<vector<double>>> data(1);

	vector<double> z(m_z), K(m_Ktaper);
	for(int n = m_totalsteps-1; n >= 0; n--){
		if(!m_inund[n]){
			z.erase(z.begin()+n);
			K.erase(K.begin()+n);
		}
	}

	vararray[0] = z;
	data[0].resize(1);
	data[0][0] = K;

	f_ExportSingle(1, titles, units, vararray, data, results);
	categs.push_back(KValueTrendLabel);
}

// private functions
int ParticleHandler::f_GetSliceOffset(int n)
{ 
	return m_steadystate ? 0 : m_totalsteps-n;
}

void ParticleHandler::f_ArrangeMemory(bool alloc)
{
	if(alloc){
		m_xy = new double *[m_nproc];
		m_tE = new double *[m_nproc];
		for(size_t n = 0; n < m_nproc; n++){
			m_xy[n] = new double[4];
			m_tE[n] = new double[2*m_ntE];
			for(int j = 0; j < 4; j++){
				m_xy[n][j] = 0;
			}
			for(int j = 0; j < 2*m_ntE; j++){
				m_tE[n][j] = 0;
			}
		}
		if(m_skipwave){
			for(int np = 0; np < m_np; np++){
				m_Efp[np].resize(m_nhmax);
				for(int nh = 0; nh < m_nhmax; nh++){
					m_Efp[np][nh].resize(2*m_nproc, 0.0);
				}
			}
		}
	}
	else{
		for(size_t n = 0; n < m_nproc; n++){
			delete[] m_xy[n];
			delete[] m_tE[n];
		}
		delete[] m_xy;
		delete[] m_tE;
	}
}

void ParticleHandler::f_XYEtSimplex()
{
	int step = (int)m_simexpsteps.size()-1+(int)floor(0.5+m_prm[SPXOut_][spxstep_]);
	int mxytotal = 4*(int)m_ntotal;
	int mxyproc = 4*(int)m_nproc;
	int mtEtotal = 2*(int)(m_ntotal*m_ntE);
	int mtEproc = 2*(int)(m_nproc*m_ntE);

	m_charge = m_simcharge;

	PathHander datapath(m_sxconf.GetDataPath());
	datapath.replace_extension(".par");
	string partdata = datapath.string();
	fstream iofile;
	int iok = 0;
	if(m_rank == 0){
		iofile.open(partdata, ios::binary|ios::in);
		if(!iofile){
			iok = -1;
		}
	}
	if(m_thread != nullptr){
		m_thread->Bcast(&iok, 1, MPI_INT, 0, m_rank);
	}
	else{
		MPI_Bcast(&iok, 1, MPI_INT, 0, MPI_COMM_WORLD);
	}
	if(iok < 0){
		throw runtime_error("Failed to open the particle data file.");
	}

	int exsteps = (int)m_simexpsteps.size();
	if(m_rank == 0){
		iofile.seekg(0, ios_base::beg);
		iofile.read((char *)m_wsexport, mxytotal*sizeof(float));
		int lcounts = (int)(iofile.gcount()/sizeof(float));
		if(mxytotal != lcounts){
			iofile.close();
			throw runtime_error("Raw data file format is not consistent with the setup file.");
		}

#ifdef _DEBUG
		float *data = new float[12*exsteps];
		iofile.read((char *)data, 12*exsteps*sizeof(float));
		cout << setprecision(4);
		for(int i = 0; i < exsteps; i++){
			int k = 0;
			for(int j = 0; j < 2; j++){
				cout << endl;
				for(int icd = 0; icd < 2; icd++){
					for(int cs = 0; cs < 3; cs++){
						cout << "\t" << data[12*i+k];
						k++;
					}
					cout << endl;
				}
				cout << endl;
			}
		}
		delete[] data;
#endif
	}

	if(m_thread != nullptr){
		m_thread->Scatter(m_wsexport, mxyproc, MPI_FLOAT, m_wsproc, mxyproc, MPI_FLOAT, 0, m_rank);
	}
	else{
		MPI_Scatter(m_wsexport, mxyproc, MPI_FLOAT, m_wsproc, mxyproc, MPI_FLOAT, 0, MPI_COMM_WORLD);
	}
	for(size_t n = 0; n < m_nproc; n++){
		for(int j = 0; j < 4; j++){
			m_xy[n][j] = m_wsproc[4*n+j];
		}
	}

	if(m_rank == 0){
		iofile.seekg((mxytotal+12*exsteps+step*mtEtotal)*sizeof(float), ios_base::beg);
		iofile.read((char *)m_wsexport, mtEtotal*sizeof(float));
		int lcounts = (int)(iofile.gcount()/sizeof(float));
		if(mtEtotal != lcounts){
			throw runtime_error("Raw data file format is not consistent with the setup file.");
		}
		iofile.close();
	}
	if(m_thread != nullptr){
		m_thread->Scatter(m_wsexport, mtEproc, MPI_FLOAT, m_wsproc, mtEproc, MPI_FLOAT, 0, m_rank);
	}
	else{
		MPI_Scatter(m_wsexport, mtEproc, MPI_FLOAT, m_wsproc, mtEproc, MPI_FLOAT, 0, MPI_COMM_WORLD);
	}

	for(size_t n = 0; n < m_nproc; n++){
		for(int j = 0; j < 2*m_ntE; j++){
			m_tE[n][j] = m_wsproc[2*m_ntE*n+j];
		}
	}
	m_ntotal = m_nproc*m_procs;

	double *icurr = new double[m_slices];
	double *irecv = new double[m_slices];
	double iunit = m_charge/(m_ntE*m_ntotal)/m_dTslice;
	for(int n = 0; n < m_slices; n++){
		icurr[n] = irecv[n] = 0;
	}

	double prvbeta[2], prvalpha[2];
	SimplexSolver prvsolver(m_sxconf);
	LatticeOperation prvlattice(prvsolver);
	int nextep = m_simexpsteps[step];
	prvlattice.GetTwissParametersAt(nextep, prvbeta, prvalpha);

	double CS[2], SS[2], CSd[2], SSd[2], DS[2], DSd[2];
	double betar[2], alphar[2];
	m_lattice->PreOperation(m_prm[SPXOut_][matching_], prvbeta, prvalpha, betar, alphar, CS, SS, CSd, SSd, DS, DSd);

	for(int j = 0; j < 2; j++){
		m_uB[j] = sqrt(m_array[Lattice_][betaxy0_][j]/betar[j]);
		m_uA[j] = (alphar[j]-m_array[Lattice_][alphaxy0_][j])/sqrt(betar[j]*m_array[Lattice_][betaxy0_][j]);
	}

	m_Einit = 0;
	double r56 = max(2*m_slippage, m_prm[EBeam_][r56_]);
		// r56 should be at least longer than that for the drift length
	double dsq, xy[2], xyd[2];
	for(size_t n = 0; n < m_nproc; n++){
		prvlattice.Move(nextep, m_xy[n], 0, xy);
		prvlattice.Move(nextep, m_xy[n], 1, xyd);
		for(int j = 0; j < 2; j++){

			// move to the entrance through the matching section
			m_xy[n][2*j] = xy[j]*CS[j]+xyd[j]*SS[j]+DS[j];
			m_xy[n][2*j+1] = xy[j]*CSd[j]+xyd[j]*SSd[j]+DSd[j];

			// adjust Twiss parameters
			m_xy[n][2*j+1] = m_uA[j]*m_xy[n][2*j]+m_xy[n][2*j+1]/m_uB[j];
			m_xy[n][2*j] *= m_uB[j];

		}
		dsq = (hypotsq(m_xy[n][1], m_xy[n][3])+hypotsq(xyd[0], xyd[1]))/2;
		dsq *= m_prm[SPXOut_][matching_]/2;
		for(int j = 0; j < m_ntE; j++){
			m_tE[n][2*j] += r56*m_tE[n][2*j+1];
			m_tE[n][2*j] -= dsq;
			m_Einit += m_tE[n][2*j+1];

			int index = (int)floor((m_tE[n][2*j]-m_s[0])/m_lslice+0.5);
			if(index >= 0 && index < m_slices){
				icurr[index] += iunit;
			}
		}
	}
	if(m_thread != nullptr){
		m_thread->Allreduce(icurr, irecv, m_slices, MPI_DOUBLE, MPI_SUM, m_rank);
	}
	else{
		MPI_Allreduce(icurr, irecv, m_slices, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
	}

#ifdef _DEBUG
	double sqavg[4] = {0, 0, 0, 0}, corr[2] = {0, 0}, avg[4] = {0, 0, 0, 0};
	for(size_t n = 0; n < m_nproc; n++){
		for(int j = 0; j < 4; j++){
			avg[j] += m_xy[n][j]/m_nproc;
			sqavg[j] += m_xy[n][j]*m_xy[n][j]/m_nproc;
		}
		for(int j = 0; j < 2; j++){
			corr[j] += m_xy[n][2*j]*m_xy[n][2*j+1]/m_nproc;
		}
	}

	double betac[2], alphac[2];
	for(int j = 0; j < 2; j++){
		double sizeq = sqavg[2*j]-avg[2*j]*avg[2*j];
		double divq = sqavg[2*j+1]-avg[2*j+1]*avg[2*j+1];
		double corrq = corr[j]-avg[2*j]*avg[2*j+1];
		double emitt = sizeq*divq-corrq*corrq;
		if(emitt < 0){
			throw runtime_error("Invalid emittance");
		}
		emitt = sqrt(emitt);
		betac[j] = sizeq/emitt;
		alphac[j] = -corrq/emitt;
	}

#endif

	vector<double> Icurr(m_slices);
	for(int n = 0; n < m_slices; n++){
		Icurr[n] = irecv[n];
	}
	delete[] icurr;
	delete[] irecv;

	vector<string> titles{SliceLabel, CurrentLabel};
	vector<vector<double>> items{m_s, Icurr};
	m_currprof.Set1D(titles, items);

#ifdef _DEBUG
	if(!ParticleSPXIcurr.empty() && m_rank == 0){
		ofstream debug_out(ParticleSPXIcurr);
		vector<double> items(2);
		PrintDebugItems(debug_out, titles);
		for(int n = 0; n < m_slices; n++){
			items[0] = m_s[n];
			items[1] = Icurr[n];
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif
	if(m_procs > 1){
		double *wsloc, *wstot = nullptr;
		int nxyt = 4+2*m_ntE;
		int nitems = (int)m_nproc*nxyt;
		wsloc = new double[nitems];
		if(m_rank == 0){
			wstot = new double[nitems*m_procs];
		}
		for(int n = 0; n < m_nproc; n++){
			for(int j = 0; j < nxyt; j++){
				wsloc[nxyt*n+j] = j < 4 ? m_xy[n][j] : m_tE[n][j-4];
			}
		}
		if(m_thread != nullptr){
			m_thread->Gather(wsloc, nitems, MPI_DOUBLE, wstot, nitems, MPI_DOUBLE, 0, m_rank);
		}
		else{
			MPI_Gather(wsloc, nitems, MPI_DOUBLE, wstot, nitems, MPI_DOUBLE, 0, MPI_COMM_WORLD);
		}

		if(m_rank == 0){
			vector<double> t(m_nproc*m_procs);
			vector<vector<double>> xyt(nxyt);
			for(int j = 0; j < nxyt; j++){
				xyt[j].resize(m_nproc*m_procs);
			}
			for(int n = 0; n < m_nproc*m_procs; n++){
				t[n] = 0;
				for(int j = 0; j < m_ntE; j++){
					t[n] += wstot[nxyt*n+4+2*j];
				}
				t[n] /= m_ntE;
				for(int j = 0; j < nxyt; j++){
					xyt[j][n] = wstot[nxyt*n+j];
				}
			}
			heap_sort(t, xyt, (int)m_nproc*m_procs, true);
			for(int n = 0; n < m_nproc*m_procs; n++){
				for(int j = 0; j < nxyt; j++){
					wstot[nxyt*n+j] = xyt[j][n];
				}
			}
		}

		if(m_thread != nullptr){
			m_thread->Scatter(wstot, nitems, MPI_DOUBLE, wsloc, nitems, MPI_DOUBLE, 0, m_rank);
		}
		else{
			MPI_Scatter(wstot, nitems, MPI_DOUBLE, wsloc, nitems, MPI_DOUBLE, 0, MPI_COMM_WORLD);
		}
		for(int n = 0; n < m_nproc; n++){
			for(int j = 0; j < nxyt; j++){
				if(j < 4){
					m_xy[n][j] = wsloc[nxyt*n+j];
				}
				else{
					m_tE[n][j-4] = wsloc[nxyt*n+j];
				}
			}
		}

		delete[] wsloc;
		if (m_rank == 0){
			delete[] wstot;
		}
	}

	f_SetSrange();
	f_SetEtCommon();
}

void ParticleHandler::f_XYEtCustom(bool qonly)
{
	vector<double> sprf, Iprf;
	m_slice.GetArray1D(SliceIndex.at(SliceLabel), &sprf);
	m_slice.GetArray1D(SliceIndex.at(CurrentLabel), &Iprf);
	Spline Qspl;
	Qspl.Initialize((int)sprf.size(), &sprf, &Iprf);

	double srange[2];
	for(int j = 0; j < 2; j++){
		srange[j] = m_array[SimCtrl_][simrange_][j]+(j-0.5)*m_lslice;
	}
	m_charge = Qspl.Integrate(srange)/CC;
	if(qonly){
		return;
	}

	size_t pick[2], particles = m_ptmp[0].size();

	vector<double> s(particles);
	for(int n = 0; n < particles; n++){
		s[n] = m_ptmp[4][n];
	}

	heap_sort(s, m_ptmp, (int)particles, true);

	int irange[2] = {0, (int)particles-1};
	while(s[irange[0]] < m_array[SimCtrl_][simrange_][0] && irange[0] < particles-1){
		irange[0]++;
	}
	irange[0]--;
	while(s[irange[1]] > m_array[SimCtrl_][simrange_][1] && irange[1] > 0){
		irange[1]--;
	}
	irange[1]++;
	irange[0] = max(0, irange[0]);
	irange[1] = min(irange[1], (int)particles-1);
	particles = irange[1]-irange[0]+1;
	if(particles < MinimumParticles){
		string msg = "Too few particles in the specified temporal window (more than "+to_string(MinimumParticles)+" particles needed).";
		throw runtime_error(msg.c_str());
	}

	double cs = cos(CUSTOMPARTMIXTURE);
	double sn = sin(CUSTOMPARTMIXTURE);
	// mix coordinate of two pick-up particles, with the ratio of tan(CUSTOMPARTMIXTURE)
	// this gives negligible change in profile, and has no effect on the RMS size in each direction
	
	size_t nrand = m_nproc*2;
	// forward the random seed to the initial point of this rankd
	if(m_procs > 1){
		for(size_t n = 0; n < nrand*m_rank; n++){
			m_rand.Uniform(0, 1);
		}
	}

	m_Einit = 0;
	vector<vector<double>> ptmp(6);
	for(int j = 0; j < 6; j++){
		ptmp[j].resize(m_nproc);
	}

	m_ptmp[5] -= m_eGeV;
	for(size_t n = 0; n < m_nproc; n++){
		for(int j = 0; j < 2; j++){
			pick[j] = (size_t)floor(m_rand.Uniform(0, 1)*particles)+irange[0];
		}
		for(int j = 0; j < 6; j++){
			ptmp[j][n] = m_ptmp[j][pick[0]]*cs+m_ptmp[j][pick[1]]*sn;
		}
	}

	vector<double> wsvec;
	if(m_procs > 1){
		vector<vector<int>> index(1);
		index.resize(m_nproc*m_procs);
		wsvec.resize(m_nproc*m_procs);

		double *wsrecv = nullptr;
		double *wssend = new double[m_nproc];
		vector<vector<double>> proot(6);
		if(m_rank == 0){
			wsrecv = new double[m_nproc*m_procs];
			for(int j = 0; j < 6; j++){
				proot[j].resize(m_nproc*m_procs);
			}
		}
		for(int j = 0; j < 6; j++){
			for(size_t n = 0; n < m_nproc; n++){
				wssend[n] = ptmp[j][n];
			}
			if(m_thread != nullptr){
				m_thread->Gather(wssend, (int)m_nproc, MPI_DOUBLE, wsrecv, (int)m_nproc, MPI_DOUBLE, 0, m_rank);
			}
			else{
				MPI_Gather(wssend, (int)m_nproc, MPI_DOUBLE, wsrecv, (int)m_nproc, MPI_DOUBLE, 0, MPI_COMM_WORLD);
			}
			if(m_rank == 0){
				for(size_t n = 0; n < m_nproc*m_procs; n++){
					proot[j][n] = wsrecv[n];
				}
			}
		}
		if(m_rank == 0){
			vector<double> wsvec = proot[4];
			heap_sort(wsvec, proot, (int)m_nproc*m_procs, true);
		}
		for(int j = 0; j < 6; j++){
			if(m_rank == 0){
				for(size_t n = 0; n < m_nproc*m_procs; n++){
					wsrecv[n] = proot[j][n];
				}
			}
			if(m_thread != nullptr){
				m_thread->Scatter(wsrecv, (int)m_nproc, MPI_DOUBLE, wssend, (int)m_nproc, MPI_DOUBLE, 0, m_rank);
			}
			else{
				MPI_Scatter(wsrecv, (int)m_nproc, MPI_DOUBLE, wssend, (int)m_nproc, MPI_DOUBLE, 0, MPI_COMM_WORLD);
			}
			if(j < 4){
				for(size_t n = 0; n < m_nproc; n++){
					m_xy[n][j] = wssend[n];
				}
			}
			else{
				for(size_t n = 0; n < m_nproc; n++){
					m_tE[n][j-4] = wssend[n];
				}
			}
		}
		delete[] wssend;
		if(m_rank == 0){
			delete[] wsrecv;
		}
	}
	else{
		wsvec = ptmp[4];
		heap_sort(wsvec, ptmp, (int)m_nproc*m_procs, true);
		for(size_t n = 0; n < m_nproc; n++){
			for(int j = 0; j < 4; j++){
				m_xy[n][j] = ptmp[j][n];
			}
			for(int j = 0; j < 2; j++){
				m_tE[n][j] = ptmp[j+4][n];
			}
		}
	}

	m_Einit = 0;
	for(size_t n = 0; n < m_nproc; n++){
		for(int j = 0; j < 2; j++){
			m_xy[n][2*j+1] = m_uA[j]*m_xy[n][2*j]+m_xy[n][2*j+1]/m_uB[j];
			m_xy[n][2*j] *= m_uB[j];
		}
		for(int j = 1; j < m_ntE; j++){
			m_tE[n][2*j] = m_tE[n][0]+m_lambda_s/m_ntE*j;
			m_tE[n][2*j+1] = m_tE[n][1];
		}
		m_Einit += m_tE[n][1]*m_ntE;
	}

	f_SetSrange();
	f_SetEtCommon();
}

void ParticleHandler::f_SetEt(bool qonly)
{
	int npoints = 101;
	vector<double> s(npoints), p(npoints);

	double srange[2];
	if(m_steadystate){
		if(m_select[EBeam_][bmprofile_] == BoxcarBunch){
			srange[0] = -m_lslice/2;
			srange[1] = m_lslice/2;
		}
		else{
			srange[0] = m_prm[SimCtrl_][simpos_]-m_lslice/2;
			srange[1] = m_prm[SimCtrl_][simpos_]+m_lslice/2;
		}
	}
	else{
		for(int j = 0; j < 2; j++){
			srange[j] = m_array[SimCtrl_][simrange_][j]+(j-0.5)*m_lslice;
		}
		srange[0] = m_s[0]-0.5*m_lslice;
		srange[1] = m_s.back()+0.5*m_lslice;
	}

	vector<double> sprf, Iprf, eta, espread;
	if(m_select[EBeam_][bmprofile_] == GaussianBunch){
		double sigmas = m_prm[EBeam_][bunchleng_];
		if(!m_steadystate){
			srange[0] = max(-GAUSSIAN_MAX_REGION*sigmas, srange[0]);
			srange[1] = min(GAUSSIAN_MAX_REGION*sigmas, srange[1]);
		}
		double ds = (srange[1]-srange[0])/(npoints-1);
		for(int n = 0; n < npoints; n++){
			s[n] = srange[0]+ds*n;
			p[n] = errf(s[n]/sigmas/SQRT2);
		}
		m_charge = SQRTPI/SQRT2*sigmas/CC*m_pkcurr*(errf(srange[1]/SQRT2/sigmas)-errf(srange[0]/SQRT2/sigmas));
	}
	else if(m_select[EBeam_][bmprofile_] == BoxcarBunch){
		double Ds = m_prm[EBeam_][bunchlenr_];
		srange[0] = max(-Ds/2, srange[0]);
		srange[1] = min(Ds/2, srange[1]);
		double ds = (srange[1]-srange[0])/(npoints-1);
		for(int n = 0; n < npoints; n++){
			s[n] = srange[0]+ds*n;
			p[n] = n;
		}
		m_charge = m_pkcurr*(srange[1]-srange[0])/CC;
	}
	else{
		if(m_select[EBeam_][bmprofile_] == CustomSlice){
			m_slice.GetArray1D(0, &sprf);
			vector<string> items = get<1>(DataFormat.at(CustomSlice));
			for(int j = 0; j < items.size(); j++){
				if(items[j] == CurrentLabel){
					m_slice.GetArray1D(j, &Iprf);
				}
				else if(items[j] == EnergyLabel){
					m_slice.GetArray1D(j, &eta);
				}
				else if(items[j] == EspLabel){
					m_slice.GetArray1D(j, &espread);
				}
			}
			eta /= m_eGeV;
			eta -= 1.0;
		}
		else if(m_select[EBeam_][bmprofile_] == CustomCurrent){
			m_currprof.GetArray1D(0, &sprf);
			m_currprof.GetArray1D(1, &Iprf);
		}
		else if(m_select[EBeam_][bmprofile_] == CustomEt){
			m_Etprf.GetProjection(0, 0, &Iprf);
			m_Etprf.GetVariable(0, &sprf);
		}

		double Iav = vectorsum(Iprf, (int)Iprf.size())/Iprf.size();
		for(int n = 0; n < Iprf.size(); n++){
			Iprf[n] = max(Iprf[n], Iav*NONZEROCURRENT);
		}

		Spline Qspl;
		Qspl.Initialize((int)sprf.size(), &sprf, &Iprf);
		m_charge = Qspl.Integrate(srange)/CC;
		Qspl.Integrate(&Iprf);

		npoints = max(npoints, (int)sprf.size());
		srange[0] = max(sprf.front(), srange[0]);
		srange[1] = min(sprf.back(), srange[1]);
		s.resize(npoints);
		p.resize(npoints);
		double ds = (srange[1]-srange[0])/(npoints-1);
		MonotoneSpline Ispl;
		Ispl.Initialize(&sprf, &Iprf, false);
		for(int n = 0; n < npoints; n++){
			s[n] = srange[0]+ds*n;
			p[n] = Ispl.GetValue(s[n]);
		}
	}
	if(qonly){
		return;
	}

	double pmin = p[0], pmax = p[npoints-1]-p[0];
	p -= pmin;
	p /= pmax;
	Spline tprofinv;
	tprofinv.Initialize(npoints, &p, &s);

	vector<Spline> jsplinv;
	if(m_select[EBeam_][bmprofile_] == CustomEt){
		// arrange probability along eta for each s value
		jsplinv.resize(sprf.size());
		vector<double> eta, jprf;
		m_Etprf.GetVariable(1, &eta);
		for(int n = 0; n < sprf.size(); n++){
			m_Etprf.Slice2D(0, n, &jprf);
			double jav = vectorsum(jprf, (int)jprf.size())/jprf.size();
			if(jav <= 0){
				for(int n = 0; n < jprf.size(); n++){
					jprf[n] = (n+0.5)/jprf.size();
				}
			}
			else{
				for(int n = 0; n < jprf.size(); n++){
					jprf[n] = max(jprf[n], jav*NONZEROCURRENT);
				}
				jsplinv[n].Initialize((int)jprf.size(), &eta, &jprf);
				jsplinv[n].Integrate(&jprf);
				jprf /= jprf[jprf.size()-1];
			}
			jsplinv[n].Initialize((int)jprf.size(), &jprf, &eta);
		}
	}

	size_t nrand = m_nproc;
	// forward the random seed to the initial point of this rank (1)
	if(m_procs > 1){
		for(size_t n = 0; n < nrand*m_rank; n++){
			m_rand.Uniform(0, 1);
		}
	}

	for(size_t n = 0; n < m_nproc; n++){
		m_tE[n][0] = tprofinv.GetValue(m_rand.Uniform(0, 1));
	}

	vector<double> wsvec(m_nproc*m_procs);
	if(m_procs > 1){
		double *wssend = new double[m_nproc];
		double *wsrecv = new double[m_nproc*m_procs];
		for(size_t n = 0; n < m_nproc; n++){
			wssend[n] = m_tE[n][0];
		}
		if(m_thread != nullptr){
			m_thread->Allgather(wssend, (int)m_nproc, MPI_DOUBLE, wsrecv, (int)m_nproc, MPI_DOUBLE, m_rank);
		}
		else{
			MPI_Allgather(wssend, (int)m_nproc, MPI_DOUBLE, wsrecv, (int)m_nproc, MPI_DOUBLE, MPI_COMM_WORLD);
		}
		for(size_t n = 0; n < m_nproc*m_procs; n++){
			wsvec[n] = wsrecv[n];
		}
		delete[] wssend;
		delete[] wsrecv;
	}
	else{
		for(size_t n = 0; n < m_nproc*m_procs; n++){
			wsvec[n] = m_tE[n][0];
		}
	}

	sort(wsvec.begin(), wsvec.end());
	for(size_t n = 0; n < m_nproc; n++){
		m_tE[n][0] = wsvec[m_rank*m_nproc+n];
	}

	f_SetSrange();

	// forward the random seed to the initial point of this rank (2)
	if(m_procs > 1){
		for(size_t n = 0; n < nrand*(m_procs-1); n++){
			m_rand.Uniform(0, 1);
		}
	}

	m_Einit = 0;
	for(size_t n = 0; n < m_nproc; n++){
		if(m_select[EBeam_][bmprofile_] == CustomEt || m_select[EBeam_][bmprofile_] == CustomSlice){
			int sidx = SearchIndex((int)sprf.size(), true, sprf, m_tE[n][0]);
			if(m_select[EBeam_][bmprofile_] == CustomEt){
				m_tE[n][1] = jsplinv[sidx].GetValue(m_rand.Uniform(0, 1));
			}
			else{
				m_tE[n][1] = SQRT2*espread[sidx]*errfinv(m_rand.Uniform(-1, 1))+eta[sidx];
			}
		}
		else{
			m_tE[n][1] = SQRT2*m_prm[EBeam_][espread_]*errfinv(m_rand.Uniform(-1, 1))
				+m_tE[n][0]*m_prm[EBeam_][echirp_];
		}
		for(int j = 1; j < m_ntE; j++){
			m_tE[n][2*j] = m_tE[n][0]+m_lambda_s/m_ntE*j;
			m_tE[n][2*j+1] = m_tE[n][1];
		}
		m_Einit += m_tE[n][1]*m_ntE;
	}

	if(m_procs > 1){
		for(size_t n = nrand*(m_rank+1); n < nrand*m_procs; n++){
			m_rand.Uniform(0, 1);
		}
	}

	f_SetEtCommon();
}

void ParticleHandler::f_SetSrange()
{
	if(m_steadystate){
		m_sranges[0] = m_sranges[1] = 0;
		return;
	}
	// initial slice range of this rank
	m_sranges[0] = (int)floor((m_tE[0][0]-m_s[0])/m_lslice+0.5)+f_GetSliceOffset(-1);
	m_sranges[1] = (int)floor((m_tE[m_nproc-1][0]-m_s[0])/m_lslice+0.5)+f_GetSliceOffset(-1);

	if(m_rank == m_procs-1){
		m_sranges[1] = max(m_sranges[1], m_slices_total-1);
	}

	if(m_nproc > 1){
		for(int mr = 1; mr < m_procs; mr++){
			if(m_thread != nullptr){
				int send;
				m_thread->SendRecv(&m_sranges[0], &send, 1, MPI_INT, mr, mr-1, m_rank);
				if(m_rank == mr-1){
					m_sranges[1] = max(m_sranges[1], send-1);
				}
			}
			else{
				if(m_rank == mr-1){
					int send;
					MPI_Status status;
					MPI_Recv(&send, 1, MPI_INT, mr, 0, MPI_COMM_WORLD, &status);
					m_sranges[1] = max(m_sranges[1], send-1);
				}
				else if(m_rank == mr){
					MPI_Send(&m_sranges[0], 1, MPI_INT, mr-1, 0, MPI_COMM_WORLD);
				}
				MPI_Barrier(MPI_COMM_WORLD);
			}
		}
	}
}

void ParticleHandler::f_SetEtCommon()
{
	m_e2loss = m_charge/m_ntotal/m_ntE*m_eGeV*1e9; // energy loss/particle (J)

	size_t nrand = m_nproc;
	if(m_procs > 1){
		double temp = m_Einit;
		if(m_thread != nullptr){
			m_thread->Allreduce(&temp, &m_Einit, 1, MPI_DOUBLE, MPI_SUM, m_rank);
		}
		else{
			MPI_Allreduce(&temp, &m_Einit, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
		}
	}

	if(m_ntE > 1 && m_select[EBeam_][bmprofile_] != SimplexOutput){
		f_AddShotnoize();
	}

#ifdef _DEBUG
	if(!ParticleEtInitial.empty()){
		f_ArrangeEt();
		if(m_rank == 0){
			f_ExportEt(ParticleEtInitial);
		}
		MPI_Barrier(MPI_COMM_WORLD);
	}
#endif
}

void ParticleHandler::f_SetXYGaussian()
{
	vector<double> sprf, sigxyprf[4], llxyprf[2], xyprf[2], xydprf[2];
	vector<double> emittprf[2], betaprf[2], alphaprf[2];
	if(m_select[EBeam_][bmprofile_] == CustomSlice){
		m_slice.GetArray1D(0, &sprf);
		vector<string> items = get<1>(DataFormat.at(CustomSlice));
		for(int j = 0; j < items.size(); j++){
			if(items[j] == EmittxLabel){
				m_slice.GetArray1D(j, &emittprf[0]);
				emittprf[0] *= 1e-6/m_gamma;
			}
			else if(items[j] == EmittyLabel){
				m_slice.GetArray1D(j, &emittprf[1]);
				emittprf[1] *= 1e-6/m_gamma;
			}
			else if(items[j] == BetaxLabel){
				m_slice.GetArray1D(j, &betaprf[0]);
			}
			else if(items[j] == BetayLabel){
				m_slice.GetArray1D(j, &betaprf[1]);
			}
			else if(items[j] == AlphaxLabel){
				m_slice.GetArray1D(j, &alphaprf[0]);
			}
			else if(items[j] == AlphayLabel){
				m_slice.GetArray1D(j, &alphaprf[1]);
			}
			else if(items[j] == XavLabel){
				m_slice.GetArray1D(j, &xyprf[0]);
			}
			else if(items[j] == YavLabel){
				m_slice.GetArray1D(j, &xyprf[1]);
			}
			else if(items[j] == XpavLabel){
				m_slice.GetArray1D(j, &xydprf[0]);
			}
			else if(items[j] == YpavLabel){
				m_slice.GetArray1D(j, &xydprf[1]);
			}
		}
		for(int ns = 0; ns < sprf.size(); ns++){
			for(int j = 0; j < 2; j++){
				alphaprf[j][ns] -= m_uA[j]*m_uB[j]*betaprf[j][ns];
				betaprf[j][ns] *= m_uB[j]*m_uB[j];
			}
		}
		double betaw;
		for(int j = 0; j < 2; j++){
			sigxyprf[2*j].resize(sprf.size());
			sigxyprf[2*j+1].resize(sprf.size());
			llxyprf[j].resize(sprf.size());
			for(int n = 0; n < sprf.size(); n++){
				betaw = betaprf[j][n]/(1.0+alphaprf[j][n]*alphaprf[j][n]);
				sigxyprf[2*j][n] = sqrt(betaw*emittprf[j][n])*SQRT2;
				sigxyprf[2*j+1][n] = sqrt(emittprf[j][n]/betaw)*SQRT2;
				llxyprf[j][n] = betaw*alphaprf[j][n];
			}
		}
	}

	double sigmaxy[4], llxy[2];
	if(m_select[EBeam_][bmprofile_] != CustomSlice){
		for(int j = 0; j < 2; j++){
			sigmaxy[2*j] = sqrt(m_betaxyw[j]*m_emitt[j])*SQRT2;
			sigmaxy[2*j+1] = sqrt(m_emitt[j]/m_betaxyw[j])*SQRT2;
			llxy[j] = m_llxy[j];
		}
	}

	size_t nrand = m_nproc*4;
	// forward the random seed to the initial point of this rank (3)
	if(m_procs > 1){
		for(size_t n = 0; n < nrand*m_rank; n++){
			m_rand.Uniform(-1, 1);
		}
	}

	int sidx;
	for(size_t n = 0; n < m_nproc; n++){
		if(m_select[EBeam_][bmprofile_] == CustomSlice){
			sidx = SearchIndex((int)sprf.size(), true, sprf, m_tE[n][0]);
			for(int j = 0; j < 2; j++){
				sigmaxy[2*j] = sigxyprf[2*j][sidx];
				sigmaxy[2*j+1] = sigxyprf[2*j+1][sidx];
				llxy[j] = llxyprf[j][sidx];
			}
		}
		for(int j = 0; j < 2; j++){
			m_xy[n][2*j+1] = sigmaxy[2*j+1]*errfinv(m_rand.Uniform(-1, 1));
			m_xy[n][2*j] = sigmaxy[2*j]*errfinv(m_rand.Uniform(-1, 1))-m_xy[n][2*j+1]*llxy[j];
		}
		if(m_select[EBeam_][bmprofile_] == CustomSlice){
			for(int j = 0; j < 2; j++){
				m_xy[n][2*j] += xyprf[j][sidx];
				m_xy[n][2*j+1] += xydprf[j][sidx];
			}
		}
	}

	if(m_procs > 1){
		for(size_t n = nrand*(m_rank+1); n < nrand*m_procs; n++){
			m_rand.Uniform(-1, 1);
		}
	}
}

void ParticleHandler::f_AddShotnoize()
{
	if(m_steadystate || m_select[SimCtrl_][simoption_] == KillShotNoize){// do nothing
		return;
	}

	double sigma = sqrt(2/(m_charge/m_ntotal/QE)), phi0, phi, delta;
	vector<double> a(m_ntE/2+1), b(m_ntE/2+1);

	size_t nrand = m_nproc*2*(m_ntE/2);
	if(m_procs > 1){
		for(size_t n = 0; n < nrand*m_rank; n++){
			m_rand.Gauss(true);
		}
	}

	for(size_t n = 0; n < m_nproc; n++){
		for(int m = 1; m <= m_ntE/2; m++){
			a[m] = m_rand.Gauss(true)*sigma/m;
			b[m] = m_rand.Gauss(true)*sigma/m;
		}
		phi0 = m_tE[n][0]/m_lambda_s;
		phi0 = (phi0-floor(phi0))*PI2;
		for(int j = 0; j < m_ntE; j++){
			phi = phi0+j*PI2/m_ntE;
			delta = 0;
			for(int m = 1; m <= m_ntE/2; m++){
				delta += a[m]*cos(m*phi)+b[m]*sin(m*phi);
			}
			m_tE[n][2*j] += delta/PI2*m_lambda_s;
		}
	}

	if(m_procs > 1){
		for(size_t n = nrand*(m_rank+1); n < nrand*m_procs; n++){
			m_rand.Gauss(true);
		}
	}
}

void ParticleHandler::f_WriteXY()
{
	int nproc = (int)m_nproc*4;
	if(m_bool[DataDump_][particle_] || !ParticleXYInitial.empty()){
		for(size_t n = 0; n < m_nproc; n++){
			for(int j = 0; j < 4; j++){
				m_wsproc[4*n+j] = (float)m_xy[n][j];
			}
		}
		if(m_thread != nullptr){
			m_thread->Gather(m_wsproc, nproc, MPI_FLOAT, m_wsexport, nproc, MPI_FLOAT, 0, m_rank);
		}
		else{
			MPI_Gather(m_wsproc, nproc, MPI_FLOAT, m_wsexport, nproc, MPI_FLOAT, 0, MPI_COMM_WORLD);
		}
	}

#ifdef _DEBUG
	if(!ParticleXYInitial.empty() && m_rank == 0){
		f_ExportXY(ParticleXYInitial);
	}
#endif

	if(m_bool[DataDump_][particle_] && m_rank == 0){
		m_iofile.write((char *)m_wsexport, m_procs*nproc*sizeof(float)); // [x,x',y,y']*beamlets: float
		m_lattice->GetCSDElements(m_exporsteps, m_wsexport);
		m_iofile.write((char *)m_wsexport, 12*(int)m_exporsteps.size()*sizeof(float)); // [CSD elements]*steps: float
	}

	MPI_Barrier(MPI_COMM_WORLD);
}

void ParticleHandler::f_ExportData(int n)
{
	if(m_bool[DataDump_][particle_] && m_zexport[n]){
		f_ArrangeEt();
		if(m_rank == 0){
			m_iofile.write((char *)m_wsexport, m_procs*m_nproc*2*m_ntE*sizeof(float));
		}
		MPI_Barrier(MPI_COMM_WORLD);
	}

#ifdef _DEBUG
	if(!ParticleEt.empty()){
		if(!m_bool[DataDump_][particle_] || !m_zexport[n]){
			f_ArrangeEt();
		}
		if(f_IsExportDebug(n, m_rank)){
			f_ExportEt(ParticleEt);
		}
		MPI_Barrier(MPI_COMM_WORLD);
	}
#endif
}

void ParticleHandler::f_ReadXY(fstream *iofile)
{
	iofile->seekg(0, ios_base::beg);
	iofile->read((char *)m_wsexport, 4*m_ntotal*sizeof(float));
	for(size_t n = 0; n < m_ntotal; n++){
		for(int j = 0; j < 4; j++){
			m_xy[n][j] = m_wsexport[4*n+j];
		}
	}
}

void ParticleHandler::f_ReadEt(fstream *iofile, int expstep)
{
	size_t offset = 4*m_ntotal; // x,y,x',y'
	offset += 12*m_exporsteps.size(); // CSD * steps
	size_t particles = 2*m_ntotal*m_ntE;
	iofile->seekg((offset+expstep*particles)*sizeof(float), ios_base::beg);
	iofile->read((char *)m_wsexport, particles*sizeof(float));

	int lcounts = (int)(iofile->gcount()/sizeof(float));
	if(lcounts != particles){
		throw runtime_error("Raw data file format is not consistent with the setup file.");
	}

	for(size_t n = 0; n < m_ntotal; n++){
		for(int j = 0; j < 2*m_ntE; j++){
			m_tE[n][j] = m_wsexport[2*m_ntE*n+j];
		}
	}
}

void ParticleHandler::f_ArrangeEt()
{
	int nproc = (int)m_nproc*2*m_ntE;
	for(size_t n = 0; n < m_nproc; n++){
		for(int j = 0; j < 2*m_ntE; j++){
			m_wsproc[2*m_ntE*n+j] = (float)m_tE[n][j];
		}
	}
	if(m_thread != nullptr){
		m_thread->Gather(m_wsproc, nproc, MPI_FLOAT, m_wsexport, nproc, MPI_FLOAT, 0, m_rank);
	}
	else{
		MPI_Gather(m_wsproc, nproc, MPI_FLOAT, m_wsexport, nproc, MPI_FLOAT, 0, MPI_COMM_WORLD);
	}
}

void ParticleHandler::f_ExportXY(string dataname)
{
	int step = max(1, (int)(m_procs*m_nproc/MaxParticleExports));
	ofstream debug_out(dataname);
	vector<string> titles{"n", "x", "x'", "y", "y'"};
	PrintDebugItems(debug_out, titles);
	vector<double> items(titles.size());
	for(size_t n = 0; n < m_procs*m_nproc; n++){
		if(n%step > 0){
			continue;
		}
		items[0] = (double)n;
		for(int j = 0; j < 4; j++){
			items[j+1] = m_wsexport[4*n+j];
		}
		for(int j = 0; j < m_ntE; j++){
			PrintDebugItems(debug_out, items);
		}
	}
	debug_out.close();
}

void ParticleHandler::f_ExportEt(string dataname)
{
	int step = max(1, (int)(m_procs*m_nproc/MaxParticleExports));
	ofstream debug_out(dataname);
	vector<string> titles{"s", "eta", "n", "m", "phi"};
	PrintDebugItems(debug_out, titles);
	vector<double> items(titles.size());
	for(size_t n = 0; n < m_procs*m_nproc; n++){
		if(n%step > 0){
			continue;
		}
		items[2] = (double)n;
		double s0 = 0;
		for(int j = 0; j < m_ntE; j++){
			s0 += m_wsexport[2*m_ntE*n+2*j];
		}
		s0 /= m_ntE;

		for(int j = 0; j < m_ntE; j++){
			double s = m_wsexport[2*m_ntE*n+2*j];
			double e = m_wsexport[2*m_ntE*n+2*j+1];
			items[0] = s;
			items[1] = e;
			items[3] = j;
			items[4] = (s/m_lambda_s-floor(s0/m_lambda_s)-(double)j/m_ntE)*360;
			PrintDebugItems(debug_out, items);
		}
	}
	debug_out.close();
}

void ParticleHandler::f_AdjustTaper(int n)
{
	int seg = m_segend[n];
	if(seg < 0 || seg == m_M-1){
		return;
	}

	double Kini = m_Ktaper[m_steprange[1][seg]];

	if(seg > 0){
		m_deta4K[seg] = min(m_deta4K[seg], m_deta4K[seg-1]);
	}

	double dK = (2+m_K*m_K)/m_K*m_deta4K[seg];
	for(int n = m_steprange[0][seg+1]; n <= m_steprange[1][seg+1]; n++){
		if(m_select[Und_][taper_] == TaperContinuous){
			m_Ktaper[n] = Kini+(n-m_steprange[0][seg+1]+1)*dK;
		}
		else{
			m_Ktaper[n] = Kini+dK*m_segsteps/2;
		}
		f_GetK4Eta(0, &m_Ktaper[n], &m_detune[n]);
		m_detune[n] += m_detune_err[n];
	}
}
