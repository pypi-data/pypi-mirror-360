#include "radiation_handler.h"
#include "particle_handler.h"
#include  "rocking_curve.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif
#include <iomanip>

string RadiationSpatial = "";
string RadiationTemporal = "";
string RadiationBunchFactorFar = "";
string RadiationBunchFactorNear = "";
string RadiationBunchFactorTemp = "";
string RadiationSPXRestore = "";
string RadiationSPXRestoreTemp = "";
string RadiationSSTemp = "";
string RadiationSSSpec = "";
string RadiationCurvatureS = "";
string RadiatioGaussGrid = "";
string RadiatioGaussGrowth = "";
string RadiatioPinst = "";
string RadiationSeedTemp = "";
string RadiationSeedTempSpl = "";
string RadiationChirpPulse = "";
string RadiationChirpPulseF = "";

int ExportSlice = 0;

RadiationHandler::RadiationHandler(SimplexSolver &sxsolver, PrintCalculationStatus *status)
	: SimplexSolver(sxsolver)
{
#ifdef _DEBUG
//	RadiationSpatial = "..\\debug\\radiation_sprofile";
//	RadiationTemporal = "..\\debug\\radiation_temprofile";
//	RadiationBunchFactorFar = "..\\debug\\radiation_bunchf_far.dat";
//	RadiationBunchFactorNear = "..\\debug\\radiation_bunchf_near.dat";
//	RadiationBunchFactorTemp = "..\\debug\\radiation_bunchf_temp";
//	RadiationSPXRestore = "..\\debug\\radiation_spx_restore.dat";
//	RadiationSPXRestoreTemp = "..\\debug\\radiation_spx_restore_temp.dat";
//	RadiationSSTemp = "..\\debug\\radiation_ss_temprofile";
//	RadiationSSSpec = "..\\debug\\radiation_ss_spec.dat";
//	RadiationCurvatureS = "..\\debug\\radiation_curv_scan.dat";
//	RadiatioGaussGrid = "..\\debug\\radiation_gauss_grid_";
//	RadiatioGaussGrowth = "..\\debug\\radiation_gauss_grow_";
//	RadiatioPinst = "..\\debug\\radiation_pinst.dat";
//	RadiationSeedTemp = "..\\debug\\seed_rad_temp.dat";
//	RadiationSeedTempSpl = "..\\debug\\seed_rad_temp_spl.dat";
//	RadiationChirpPulse = "..\\debug\\chirp_pulse.dat";;
//	RadiationChirpPulseF = "..\\debug\\chirp_pulse_freq.dat";;
#endif

	m_ngrids = m_nfft[0]*m_nfft[1]*2;
	m_ndata = m_slices_total*m_ngrids;
	m_nexport = m_slices*m_ngrids;
	m_nfftsp = fft_number(m_slices_total, 1);

	if(m_ispostproc){
		m_isppflux = m_select[PostP_][item_] == PostPFluxLabel;
		m_isppamp = m_select[PostP_][item_] == PostPCampLabel;
		m_ispppower = m_select[PostP_][item_] == PostPPowerLabel;
		m_iswignerX = m_select[PostP_][item_] == PostPWignerLabel
				&& m_select[PostP_][domain_] == PostPSpatDomainLabel
				&&m_select[PostP_][axis_] == PostPXAxisLabel;
		m_iswignerY = m_select[PostP_][item_] == PostPWignerLabel
				&& m_select[PostP_][domain_] == PostPSpatDomainLabel
				&&m_select[PostP_][axis_] == PostPYAxisLabel;
		m_iswignerT = m_select[PostP_][item_] == PostPWignerLabel
			&& m_select[PostP_][domain_] == PostPTimeDomainLabel;
		m_iswigner = m_iswignerX || m_iswignerY || m_iswignerT;
		int ngrids = (m_nfft[0]+1)*(m_nfft[1]+1);
		if(m_iswignerX){
			m_deltaW = m_wigner.Initialize(m_nfft[0], m_nfft[1]+1, m_qxy[0], m_qxy[1], 0, 1);
			m_wsW = new double[ngrids*2];
		}
		else if(m_iswignerY){
			m_deltaW = m_wigner.Initialize(m_nfft[1], m_nfft[0]+1, m_qxy[1], m_qxy[0], 0, 1);
			m_wsW = new double[ngrids*2];
		}
		else if(m_iswignerT){
			m_deltaW = m_wigner.Initialize(m_slices, 1, m_lslice/CC, 0, 0, 1, m_totalsteps);
				// total slices (= m_slices+m_totalsteps) defines the FFT number
			m_wsW = new double[m_slices*2];
		}
	}
	else{
		m_isppflux = m_isppamp = m_ispppower = m_iswignerX = m_iswignerY = m_iswignerT = m_iswigner = false;
	}

	if(m_ispostproc || (m_bool[DataDump_][radiation_] && m_rank == 0)){
		m_iofs.resize(m_nhmax);
		if(m_ispostproc){
			for(int j = 0; j < 4; j++){
				m_Epp[j].resize(m_nfftsp); // slice position of radiation (not e-bunch)
			}
		}
		string dataname = m_datapath.filename().string();
		for(int nh = 0; nh < m_nhmax; nh++){
			if(m_ispostproc && nh != m_nhpp){
				continue;
			}
			m_datapath.replace_filename(dataname+"-"+to_string(nh+1));
			m_datapath.replace_extension(".fld");
			string flddata = m_datapath.string();
			if(m_ispostproc){
				m_iofs[nh].open(flddata, ios::binary|ios::in);
			}
			else{
				m_iofs[nh].open(flddata, ios::binary|ios::out);
			}
			if(!m_iofs[nh]){
				throw runtime_error("Failed to open the radiation data file.");
			}
		}
		m_wsexport = new float[m_nexport];
	}
	m_wsonslices = new int[m_slices_total];

	bool putstep = !m_ispostproc && !m_lasermod;
	if(putstep){
		int substeps = 3;
		if(m_select[Seed_][seedprofile_] == SimplexOutput){
			substeps = 4+m_nhmax;
		}
		else if(m_exseed){
			substeps = 5;
		}
		status->SetSubstepNumber(1, substeps); // memory allocation, phase, others
		status->ResetCurrentStep(1);
	}

	m_fft = new FastFourierTransform(2, m_nfft[0], m_nfft[1]);

	if(!m_skipwave || m_isGaussDebug){
		for(int np = 0; np < m_np; np++){
			m_ws[np].resize(m_nhmax);
			m_E[np].resize(m_nhmax);
			for(int nh = 0; nh < m_nhmax; nh++){
				m_ws[np][nh].resize(3); // 0: far field, 1: near field, 2: near bunch factor & storage
				m_E[np][nh].resize(3);
				for(int j = 0; j < 3; j++){
					m_ws[np][nh][j] = new double[m_ndata];
					for(size_t n = 0; n < m_ndata; n++){
						m_ws[np][nh][j][n] = 0; // initialize: fill with 0
					}
					m_E[np][nh][j].resize(m_slices_total);
					for(int ns = 0; ns < m_slices_total; ns++){
						m_E[np][nh][j][ns] = new double *[m_nfft[0]];
						for(int nx = 0; nx < m_nfft[0]; nx++){
							m_E[np][nh][j][ns][nx] = m_ws[np][nh][j]+ns*m_ngrids+nx*m_nfft[1]*2;
						}
					}
				}
			}
		}
	}
	if(putstep){
		status->AdvanceStep(1);
	}

	if(m_isGauss){
		m_BG.resize(m_BGmodes);
		for(int g = 0; g < m_BGmodes; g++){
			int nri = g > 0 ? 2 : 1;
			m_BG[g].resize(m_nhmax);
			for(int nh = 0; nh < m_nhmax; nh++){
				m_BG[g][nh] = new double[m_slices_total*nri];
			}
		}
		m_wsbg = new double[m_slices_total*2];

		for(int j = 0; j < 2; j++){
			m_Psr[j].resize(m_nhmax);
			m_psr[j].resize(m_nhmax);
		}
		for(int nh = 0; nh < m_nhmax; nh++){
			for(int j = 0; j < 2; j++){
				m_Psr[j][nh].resize(m_slices_total, 0.0);
				m_psr[j][nh].resize(m_nfft[0]*m_nfft[1], 0.0);
			}
		}
		if(m_bool[DataDump_][spectral_]){
			for(int j = 0; j < m_np; j++){
				m_fsr[j].resize(m_nhmax);
				for(int nh = 0; nh < m_nhmax; nh++){
					m_fsr[j][nh].resize(m_nfft[0]*m_nfft[1]);
					for(int nxy = 0; nxy < m_nfft[0]*m_nfft[1]; nxy++){
						if(m_rank == nxy%m_procs){
							m_fsr[j][nh][nxy].resize(2*(m_nfftsp+1), 0.0);
						}
					}
				}
			}
			m_Fsr.resize(m_nhmax);
			for(int nh = 0; nh < m_nhmax; nh++){
				m_Fsr[nh].resize(m_nfftsp+1, 0.0);
			}
		}
	}
	if(!m_skipwave || m_isGaussDebug){
		m_wsbf.resize(m_nhmax);
		m_B.resize(m_nhmax);
		for(int nh = 0; nh < m_nhmax; nh++){
			m_wsbf[nh] = new double[m_ndata];
			m_B[nh].resize(m_slices_total);
			for(int ns = 0; ns < m_slices_total; ns++){
				m_B[nh][ns] = new double *[m_nfft[0]];
				for(int nx = 0; nx < m_nfft[0]; nx++){
					m_B[nh][ns][nx] = m_wsbf[nh]+ns*m_ngrids+nx*m_nfft[1]*2;
				}
			}
		}
	}

	m_Pinst.resize(m_nhmax);
	m_bf.resize(m_nhmax);
	for(int nh = 0; nh < m_nhmax; nh++){
		m_Pinst[nh].resize(m_totalsteps);
		m_bf[nh].resize(m_totalsteps);
		for(int n = 0; n < m_totalsteps; n++){
			m_Pinst[nh][n].resize(m_slices_total);
		}
	}
	for(int i = 0; i < 2; i++){
		m_Pax[i].resize(m_nhmax);
		for(int nh = 0; nh < m_nhmax; nh++){
			m_Pax[i][nh].resize(m_totalsteps);
		}
	}

	if(m_bool[DataDump_][temporal_]){
		m_Pexprt.resize(m_totalsteps);
		for(int n = 0; n < m_totalsteps; n++){
			m_Pexprt[n].resize(m_nhmax);
			for(int nh = 0; nh < m_nhmax; nh++){
				m_Pexprt[n][nh].resize(m_slices);
			}
		}
	}

	if(m_bool[DataDump_][spectral_] || m_isppflux){
		for(int j = 0; j < 2; j++){
			m_wssp[j] = new double[2*m_nfftsp];
		}
		m_tfft = new FastFourierTransform(1, m_nfftsp);
		double de = PLANCK/(m_nfftsp*m_dTslice);
		m_Flux.resize(m_totalsteps);
		for(int n = 0; n < m_totalsteps; n++){
			m_Flux[n].resize(m_nhmax);
			for(int nh = 0; nh < m_nhmax; nh++){
				m_Flux[n][nh].resize(m_nfftsp+1);
			}
		}
		m_ep.resize(m_nfftsp+1);
		for(int ne = -m_nfftsp/2; ne <= m_nfftsp/2; ne++){
			m_ep[ne+m_nfftsp/2] = ne*de;
			if(m_nhmax == 1){
				m_ep[ne+m_nfftsp/2] += photon_energy(m_lambda1);
			}
		}
	}
	m_curvature.resize(m_nhmax);
	for(int nh = 0; nh < m_nhmax; nh++){
		m_curvature[nh].resize(m_totalsteps);
	}
	for(int j = 0; j < 2; j++){
		m_Pd[j].resize(m_totalsteps);
		for(int n = 0; n < m_totalsteps; n++){
			m_Pd[j][n].resize(m_nhmax);
			for(int nh = 0; nh < m_nhmax; nh++){
				m_Pd[j][n][nh].resize((m_nfft[0]+1)*(m_nfft[1]+1));
			}
		}
	}
	if(m_bool[DataDump_][angular_] || m_bool[DataDump_][spatial_]){
		for(int j = 0; j < 2; j++){
			m_wspd[j] = new double[2*(m_nfft[0]+1)*(m_nfft[1]+1)];
		}
	}

	if(putstep){
		status->AdvanceStep(1);
	}

	if(m_isGauss){
		f_InitGaussianMode();
	}
	f_SetPhase(m_zstep, &m_uphase);
	f_SetPhase(m_zstep_drift, &m_dphase);

	m_f2n = m_dkxy[0]*m_dkxy[1]/PI2/PI2; // far field to near field

	for(int j = 0; j < 2; j++){
		m_E2pd[j].resize(m_nhmax);
		m_E2P[j].resize(m_nhmax);
		m_E2f[j].resize(m_nhmax);
	}

	for(int nh = 0; nh < m_nhmax; nh++){
		double fnh = nh+1;
		m_E2pd[1][nh] = 2/Z0VAC*1e-6; // spatial power density (W/mm^2)
		if(m_select[Und_][utype_] == HelicalUndLabel){
			m_E2pd[1][nh] *= 2;
		}
		m_E2pd[0][nh] = m_E2pd[1][nh]*fnh*fnh/m_lambda_s/m_lambda_s; // angular power density (W/mrad^2)

		m_E2P[1][nh] = m_E2pd[1][nh]*1e6*m_dxy[0]*m_dxy[1]; // P = int |~E|^2*2/Z0VAC dxdy
		m_E2P[0][nh] = m_E2pd[0][nh]*1e6*(m_qxy[0]/fnh)*(m_qxy[1]/fnh); // P = 1/lambda^2 int |~e|^2*2/Z0VAC dqxdqy

		for(int j = 0; j < 2; j++){
			m_E2f[j][nh] = m_E2pd[j][nh]*m_dTslice*m_dTslice/QE/PLANCK*1e-3; // field amplitude to flux density (photons/mm^2,mrad^2/0.1%)
		}
	}

	if(m_ispostproc){
		m_rank_admin.resize(m_slices_total, 0);
		m_sranges[0] = 0;
		m_sranges[1] = m_slices_total-1;
		if(m_exseed){
			f_PrepareExternalSeed();
		}
		return;
	}
	else{
		m_rank_admin.resize(m_slices_total, -1);
		int sranges[2];
		for(int rank = 0; rank < m_procs; rank++){
			for(int j = 0; j < 2; j++){
				sranges[j] = m_sranges[j];
			}
			if(rank == 0){ // expand the tail side
				sranges[0] -= m_exslices;
			}
			if(rank == m_procs-1){ // expand the head side
				sranges[1] += m_exslices;
			}
			if(m_thread != nullptr){
				m_thread->Bcast(sranges, 2, MPI_INT, rank, m_rank);
			}
			else{
				MPI_Bcast(sranges, 2, MPI_INT, rank, MPI_COMM_WORLD);
			}
			for(int s = sranges[0]; s <= sranges[1]; s++){
				if(s < 0 || s >= m_slices_total){
					continue;
				}
				m_rank_admin[s] = rank;
			}
		}
		if(!m_steadystate){
			// expand the slice range to be automatically covered
			m_sranges[0] -= m_exslices;
			m_sranges[1] += m_exslices;
		}
	}

	if(putstep){
		status->AdvanceStep(1);
	}
	if(m_select[Seed_][seedprofile_] == SimplexOutput){
		for(int nh = 0; nh < m_nhmax; nh++){
			f_LoadSimplexOutput(nh, status);
			status->AdvanceStep(1);
		}
		m_nsorg = m_totalsteps+m_slices/2;
	}
	else if(m_select[Seed_][seedprofile_] == NotAvaliable){
		m_nsorg = m_totalsteps+m_slices/2;
		status->AdvanceStep(0);
		return;
	}
	else if(m_exseed){
		// modified in 3.1 to use FT of frequency domain
		//f_PrepareExternalSeed();
		f_PrepareExternalSeedSpl();

		status->AdvanceStep(1);
	}

	if(m_lasermod){
		SetSeedField(-1);
	}
	SetNearField(-1, 1); // assign seed field at the entrance to E[1]; skip copy from E[2] to E[1]

	if(putstep){
		status->AdvanceStep(1);
		status->AdvanceStep(0);
	}
}

RadiationHandler::~RadiationHandler()
{
	if(!m_skipwave || m_isGaussDebug){
		for(int np = 0; np < m_np; np++){
			for(int nh = 0; nh < m_nhmax; nh++){
				for(int j = 0; j < 3; j++){
					if(np > 0 && j == 3){ // do not use
						continue;
					}
					else{
						delete[] m_ws[np][nh][j];
					}
					for(int ns = 0; ns < m_slices_total; ns++){
						delete[] m_E[np][nh][j][ns];
					}
				}
			}
		}
	}
	delete m_fft;
	if(m_bool[DataDump_][spectral_] || m_isppflux){
		delete m_tfft;
		for(int j = 0; j < 2; j++){
			delete[] m_wssp[j];
		}
	}

	if(m_isGauss){
		for(int nh = 0; nh < m_nhmax; nh++){
			for(int g = 0; g < m_BGmodes; g++){
				delete[] m_BG[g][nh];
			}
		}
		delete[] m_wsbg;
		for(int np = 0; np < m_np; np++){
			for(int nh = 0; nh < m_nhmax; nh++){
				for(int n = 0; n < m_totalsteps; n++){
					delete[] m_eorg[np][nh][n];
					delete[] m_etgt[np][nh][n];
				}
			}
		}
		delete[] m_ewsbuf;
	}
	if(!m_skipwave || m_isGaussDebug){
		for(int nh = 0; nh < m_nhmax; nh++){
			delete[] m_wsbf[nh];
			for(int ns = 0; ns < m_slices_total; ns++){
				delete[] m_B[nh][ns];
			}
		}
	}

	if((m_ispostproc || m_bool[DataDump_][radiation_]) && m_rank == 0){
		for(int nh = 0; nh < m_nhmax; nh++){
			m_iofs[nh].close();
		}
		delete[] m_wsexport;
	}
	delete[] m_wsonslices;

	if(m_bool[DataDump_][angular_] || m_bool[DataDump_][spatial_]){
		for(int j = 0; j < 2; j++){
			delete[] m_wspd[j];
		}
	}

	if(m_iswigner){
		delete[] m_wsW;
	}
}

void RadiationHandler::AdvanceField(int n, double q2E, double ptotal, vector<vector<vector<vector<double>>>> F[])
{
	double bf[2], dFdq[4];
	vector<int> secrange[2];

	for(int nh = 0; nh < m_nhmax; nh++){
		bool nheven = nh%2 > 0;
		if(nheven){ // even harmonics, get gradient x/y
			for(int np = 0; np < m_np; np++){
				double dq = m_qxy[np]/(nh+1);
				if(np == 0){ // dF/dqx
					dFdq[0] = (F[np][nh][n][1][0]-F[np][nh][n][0][0])/dq;
					dFdq[1] = (F[np][nh][n][1][1]-F[np][nh][n][0][1])/dq;
				}
				else{ // dF/dqy
					dFdq[2] = (F[np][nh][n][0][2]-F[np][nh][n][0][0])/dq;
					dFdq[3] = (F[np][nh][n][0][3]-F[np][nh][n][0][1])/dq;
				}
			}
		}

		if(m_procs > 1){ // reduce bunch factors
			if(m_isGauss){
				for(int g = 0; g < m_BGmodes; g++){
					int ndata = m_slices_total;
					if(g > 0){
						ndata *= 2;
					}
					for(int nd = 0; nd < ndata; nd++){
						m_wsbg[nd] = m_BG[g][nh][nd];
					}
					if(m_thread != nullptr){
						m_thread->Allreduce(m_wsbg, m_BG[g][nh], ndata, MPI_DOUBLE, MPI_SUM, m_rank);
					}
					else{
						MPI_Allreduce(m_wsbg, m_BG[g][nh], ndata, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
					}
				}
			}
			if(!m_skipwave || m_isGaussDebug){
				if(m_thread != nullptr){
					m_thread->Allreduce(m_onslices, m_wsonslices, m_slices_total, MPI_INT, MPI_SUM, m_rank);
				}
				else{
					MPI_Allreduce(m_onslices, m_wsonslices, m_slices_total, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
				}
				for(int ns = 0; ns < m_slices_total; ns++){
					if(m_wsonslices[ns] > 1){
						for(int n = 0; n < m_ngrids; n++){
							m_ws[0][nh][2][n] = m_wsbf[nh][ns*m_ngrids+n];
						}
						if(m_thread != nullptr){
							m_thread->Allreduce(m_ws[0][nh][2], m_wsbf[nh]+ns*m_ngrids, m_ngrids, MPI_DOUBLE, MPI_SUM, m_rank);
						}
						else{
							MPI_Allreduce(m_ws[0][nh][2], m_wsbf[nh]+ns*m_ngrids, m_ngrids, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
						}
					}
				}
			}
		}

		double bfGL[] = {0, 0};
		m_bf[nh][n] = 0;
		for(int ns = 0; ns < m_slices_total; ns++){
			if(m_rank != m_rank_admin[ns]){
				continue;
			}
			if(m_isGauss){
				m_bf[nh][n] += sqrt(hypotsq(m_BG[1][nh][2*ns], m_BG[1][nh][2*ns+1]));
				bfGL[0] += hypotsq(m_BG[1][nh][2*ns], m_BG[1][nh][2*ns+1]);
				bfGL[1] += hypotsq(m_BG[2][nh][2*ns], m_BG[2][nh][2*ns+1])
						+hypotsq(m_BG[3][nh][2*ns], m_BG[3][nh][2*ns+1]);
			}
			else{
				bf[0] = bf[1] = 0;
				for(int nx = 0; nx < m_nfft[0]; nx++){
					for(int ny = 0; ny < m_nfft[1]; ny++){
						bf[0] += m_B[nh][ns][nx][2*ny];
						bf[1] += m_B[nh][ns][nx][2*ny+1];
					}
				}
				m_bf[nh][n] += sqrt(hypotsq(bf[0], bf[1]));
			}
		}

		if(m_procs > 1){
			double temp = m_bf[nh][n];
			if(m_thread != nullptr){
				m_thread->Allreduce(&temp, &m_bf[nh][n], 1, MPI_DOUBLE, MPI_SUM, m_rank);
				if(m_isGauss){
					double tempbf[] = {bfGL[0], bfGL[1]};
					m_thread->Allreduce(&tempbf, &bfGL, 2, MPI_DOUBLE, MPI_SUM, m_rank);
				}
			}
			else{
				MPI_Allreduce(&temp, &m_bf[nh][n], 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
				if(m_isGauss){
					double tempbf[] = {bfGL[0], bfGL[1]};
					MPI_Allreduce(&tempbf, &bfGL, 2, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
				}
			}
		}
		m_bf[nh][n] /= ptotal;

		if(m_isGauss){
			double kxy[2], tex, lambdan = m_lambda_s/(nh+1);
			double bfl = sqrt(bfGL[0]/(4*PI*bfGL[1]));
			for(int j = 0; j < 2; j++){
				m_bfg[j][nh] *= bfl;
				m_bfsize[j][nh][n] = m_sizexy[j][n]*m_bfg[j][nh];
			}
			m_gkappa[nh][n] = m_bfg[0][nh];

			if(!m_skipwave || m_isGaussDebug){
				double ksig[2];
				for(int nx = 0; nx < m_nfft[0]; nx++){
					kxy[0] = m_dkxy[0]*fft_index(nx, m_nfft[0], 1);
					ksig[0] = kxy[0]*m_bfsize[0][nh][n];
					ksig[0] *= ksig[0];
					for(int ny = 0; ny < m_nfft[1]; ny++){
						kxy[1] = m_dkxy[1]*fft_index(ny, m_nfft[1], 1);
						ksig[1] = kxy[1]*m_bfsize[1][nh][n];
						ksig[1] *= ksig[1];
						tex = (ksig[0]+ksig[1])/2;
						if(tex < MAXIMUM_EXPONENT){
							m_Gf[0][nx][ny] = exp(-tex);
						}
					}
				}
			}

			if(m_skipwave){
				for(int ns = 0; ns < m_slices_total; ns++){
					fill(m_assigned[ns].begin(), m_assigned[ns].end(), -1);
				}
				f_SetSecRange(n, nh, secrange);
			}

#ifdef _DEBUG
			if(!RadiatioGaussGrid.empty() && nh == 0 && m_rank == 0){
				f_ExportGxyGrid(nh, secrange, RadiatioGaussGrid);
			}
			if(!RadiatioGaussGrowth.empty() && nh == 0 && m_rank == 0){
				f_ExportGxyFldGrowth(n, nh, secrange, RadiatioGaussGrowth);
			}
			MPI_Barrier(MPI_COMM_WORLD);
#endif
		}
		if(!m_skipwave){
#ifdef _DEBUG
			if(!RadiationBunchFactorTemp.empty() && f_IsExportDebug(n) && nh == 0 && m_rank == 0){
				f_ExportFieldTemp(n, true, -1, nh, RadiationBunchFactorTemp);
				MPI_Barrier(MPI_COMM_WORLD);
			}
			MPI_Barrier(MPI_COMM_WORLD);
#endif
		}

		if(m_inund[n]){			
			if(m_skipwave){
				for(int ns = m_sranges[0]; ns <= m_sranges[1]; ns++){
					if(ns < 0 || ns >= m_slices_total){
						continue;
					}
					double g00[2];
					for(int j = 0; j < 2; j++){
						g00[j] = m_BG[1][nh][2*ns+j];
					}

					for(int np = 0; np < m_np; np++){
						if(nheven){
							m_eorg[np][nh][n][2*ns  ] = q2E*(dFdq[2*np]*g00[0]-dFdq[2*np+1]*g00[1]);
							m_eorg[np][nh][n][2*ns+1] = q2E*(dFdq[2*np]*g00[1]+dFdq[2*np+1]*g00[0]);
						}
						else{
							m_eorg[np][nh][n][2*ns  ] = q2E*(F[np][nh][n][0][0]*g00[0]-F[np][nh][n][0][1]*g00[1]);
							m_eorg[np][nh][n][2*ns+1] = q2E*(F[np][nh][n][0][0]*g00[1]+F[np][nh][n][0][1]*g00[0]);
						}
					}
				}
				if(m_procs > 1){
					for(int np = 0; np < m_np; np++){
						for(int ns = 0; ns < m_slices_total; ns++){
							if(m_rank == m_rank_admin[ns]){
								m_ewsbuf[2*ns] = m_eorg[np][nh][n][2*ns];
								m_ewsbuf[2*ns+1] = m_eorg[np][nh][n][2*ns+1];
							}
							else{
								m_ewsbuf[2*ns] = m_ewsbuf[2*ns+1] = 0;
							}
						}
						if(m_thread != nullptr){
							m_thread->Allreduce(m_ewsbuf, m_eorg[np][nh][n], 2*m_slices_total, MPI_DOUBLE, MPI_SUM, m_rank);
						}
						else{
							MPI_Allreduce(m_ewsbuf, m_eorg[np][nh][n], 2*m_slices_total, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
						}
					}
				}
			}
			if(!m_skipwave || m_isGaussDebug){
				if(m_isGauss){
					if(n == 0){
						m_bfphase.resize(m_slices_total);
					}
					for(int ns = m_sranges[0]; ns <= m_sranges[1]; ns++){
						if(ns < 0 || ns >= m_slices_total){
							continue;
						}
						double arg = 0, csn[2], g00[2];
						for(int j = 0; j < 2; j++){
							g00[j] = m_BG[1][nh][2*ns+j];
						}
						if(g00[0] != 0 || g00[1] != 0){
							arg = atan2(g00[0], g00[1]);
						}
						if(n == 0){
							m_bfphase[ns-m_sranges[0]] = arg;
						}
						else{
							arg = m_bfphase[ns-m_sranges[0]];
						}
						csn[0] = cos(arg);
						csn[1] = sin(arg);
						for(int nx = 0; nx < m_nfft[0]; nx++){
							for(int ny = 0; ny < m_nfft[1]; ny++){
								m_B[nh][ns][nx][2*ny] = g00[0]*m_Gf[0][nx][ny];
								m_B[nh][ns][nx][2*ny+1] = g00[1]*m_Gf[0][nx][ny];
							}
						}
					}
				}
				else{
#ifdef _DEBUG
					if(!RadiationBunchFactorNear.empty() && f_IsExportDebug(n) && m_rank == 0){
						f_ExportField(true, true, -1, ExportSlice, 0, RadiationBunchFactorNear);
					}
#endif
					for(int ns = m_sranges[0]; ns <= m_sranges[1]; ns++){
						if(ns < 0 || ns >= m_slices_total){
							continue;
						}
						m_fft->DoFFT(m_B[nh][ns], -1);
					}
				}
#ifdef _DEBUG
				if(!RadiationBunchFactorFar.empty() && f_IsExportDebug(n) && m_rank == 0){
					f_ExportField(true, false, -1, ExportSlice, 0, RadiationBunchFactorFar);
				}
				MPI_Barrier(MPI_COMM_WORLD);
#endif
			}
		}

		if(m_skipwave){
			double atanz, zrayl, zmn, lambdan = m_lambda_s/(nh+1);
			for(int m = 0; m <= n; m++){
				m_gn[0][m] = 1/(PI2*m_bfsize[0][nh][m]*m_bfsize[1][nh][m]);
				atanz = 0;
				for(int j = 0; j < 2; j++){
					zrayl = PI2*m_bfsize[j][nh][m]*m_bfsize[j][nh][m]/lambdan;
					zmn = (m_z[n]-m_z[m])/zrayl;
					atanz -= atan(zmn)/2;
				}
				m_gn[1][m] = m_gn[0][m]*sin(atanz);
				m_gn[0][m] *= cos(atanz);
			}
			for(int np = 0; np < m_np; np++){
				for(int ns = m_sranges[0]; ns <= m_sranges[1]; ns++){
					if(ns < 0 || ns >= m_slices_total){
						continue;
					}
					for(int nsec = 0; nsec < m_Esec[nh]; nsec++){
						m_etgt[np][nh][nsec][2*ns] = m_etgt[np][nh][nsec][2*ns+1] = 0;
						for(int m = secrange[0][nsec]; m <= secrange[1][nsec] && !nheven; m++){
							m_etgt[np][nh][nsec][2*ns] += m_eorg[np][nh][m][2*ns]*m_gn[0][m]-m_eorg[np][nh][m][2*ns+1]*m_gn[1][m];
							m_etgt[np][nh][nsec][2*ns+1] += m_eorg[np][nh][m][2*ns]*m_gn[1][m]+m_eorg[np][nh][m][2*ns+1]*m_gn[0][m];
						}
					}
				}
			}
		}
		if(!m_skipwave || m_isGaussDebug){
			vector<vector<double>> &phase = m_inund[n] ? m_uphase[nh] : m_dphase[nh];
			double ure, uim, temp;
			for(int ns = m_sranges[0]; ns <= m_sranges[1]; ns++){
				if(ns < 0 || ns >= m_slices_total){
					continue;
				}
				for(int np = 0; np < m_np; np++){
					double **E = m_E[np][nh][0][ns];
					for(int nx = 0; nx < m_nfft[0]; nx++){
						for(int ny = 0; ny < m_nfft[1]; ny++){
							E[nx][2*ny] =
								(temp = E[nx][2*ny])*phase[nx][2*ny]-E[nx][2*ny+1]*phase[nx][2*ny+1];
							E[nx][2*ny+1] =
								temp*phase[nx][2*ny+1]+E[nx][2*ny+1]*phase[nx][2*ny];
							if(m_inund[n]){
								ure = F[np][nh][n][nx][2*ny]*q2E;
								uim = F[np][nh][n][nx][2*ny+1]*q2E;
								E[nx][2*ny] += m_B[nh][ns][nx][2*ny]*ure-m_B[nh][ns][nx][2*ny+1]*uim;
								E[nx][2*ny+1] += m_B[nh][ns][nx][2*ny]*uim+m_B[nh][ns][nx][2*ny+1]*ure;
							}
						}
					}
				}
			}
#ifdef _DEBUG
			if(!RadiationTemporal.empty() && f_IsExportDebug(n) && m_rank == 0){
				string dataname = RadiationTemporal+"_far";
				f_ExportFieldTemp(n, false, 0, 0, dataname);
			}
			MPI_Barrier(MPI_COMM_WORLD);
#endif
		}
	}
	MPI_Barrier(MPI_COMM_WORLD);

	if(!m_steadystate){
		// shift the parameters to handle slice positions for each rank
		for(int n = 0; n < m_slices_total-1; n++){
			m_rank_admin[n] = m_rank_admin[n+1];
		}
		m_sranges[0]--; // shift the entrance of slice range
	}

	if(m_procs > 1 && (!m_skipwave || m_isGaussDebug)){ // transfer data for the entrance
		MPI_Status status;
		int ns;
		for(int rank = 1; rank < m_procs; rank++){
			ns = m_sranges[0];
			if(m_thread != nullptr){
				m_thread->Bcast(&ns, 1, MPI_INT, rank, m_rank);
			}
			else{
				MPI_Bcast(&ns, 1, MPI_INT, rank, MPI_COMM_WORLD);
			}
			if(ns < 0 || ns >= m_slices_total){
				continue;
			}
			for(int np = 0; np < m_np; np++){
				for(int nh = 0; nh < m_nhmax; nh++){
					if(m_thread != nullptr){
						m_thread->SendRecv(
							m_ws[np][nh][0]+ns*m_ngrids,
							m_ws[np][nh][0]+m_sranges[0]*m_ngrids,
							m_ngrids, MPI_DOUBLE, rank-1, rank, m_rank);
					}
					else{
						if(m_rank == rank){
							MPI_Recv(m_ws[np][nh][0]+m_sranges[0]*m_ngrids, m_ngrids, MPI_DOUBLE, rank-1, 0, MPI_COMM_WORLD, &status);
						}
						else if(m_rank == rank-1){
							MPI_Send(m_ws[np][nh][0]+ns*m_ngrids, m_ngrids, MPI_DOUBLE, rank, 0, MPI_COMM_WORLD);
						}
					}
				}
			}
			MPI_Barrier(MPI_COMM_WORLD);
		}
	}

	if(m_skipwave && n > 0){
		double eps = 0.0;
		for(int nh = 0; nh < m_nhmax; nh++){
			double bfmax = m_bf[nh][n];
			m_mini[nh] = n-1;
			while(m_bf[nh][m_mini[nh]] > eps*bfmax && m_mini[nh] > 0){
				if(m_bf[nh][m_mini[nh]] > bfmax){
					bfmax = m_bf[nh][m_mini[nh]];
				}
				m_mini[nh]--;
			}
		}
	}

	SetNearField(n); // compute near-field radiation in the slice range
	if(!m_steadystate){
		m_sranges[1]--; // shift the exit of the slice range to save
	}
	if(m_cyclic){
		f_CyclicShift(n);
	}
	if(m_bool[DataDump_][radiation_] && m_zexport[n]){
		f_WriteData(n);
	}
}

void RadiationHandler::f_GetSR(int n, int nh, vector<vector<vector<vector<double>>>> F[])
{
	double e2E = -Z0VAC/2/m_gamma*QE/m_dTslice;
	double f2p = e2E*e2E;
	double f2f = f2p*m_E2f[0][nh]*1e6*(m_qxy[0]/(nh+1))*(m_qxy[1]/(nh+1));
	double f2P = f2p*m_E2P[0][nh];
	f2p *= m_E2pd[0][nh]*m_dTslice;

	fill(m_Psr[1][nh].begin(), m_Psr[1][nh].end(), 0);
	if(m_bool[DataDump_][spectral_]){
		fill(m_Fsr[nh].begin(), m_Fsr[nh].end(), 0);
	}
	for(int np = 0; np < m_np; np++){
		double Epk = 0;
		vector<vector<double>> &phase = m_inund[n] ? m_uphase[nh] : m_dphase[nh];
		for(int nx = 0; nx < m_nfft[0]; nx++){
			for(int ny = 0; ny < m_nfft[1]; ny++){
				double psq = hypotsq(F[np][nh][n][nx][2*ny], F[np][nh][n][nx][2*ny+1]);
				for(int ns = 0; ns < m_slices_total; ns++){
					m_Psr[1][nh][ns] += psq*m_BG[0][nh][ns]*f2P;
				}
				if(m_bool[DataDump_][angular_]){
					m_psr[0][nh][nx*m_nfft[1]+ny] += psq*m_electrons*f2p;
				}
				if(m_bool[DataDump_][spatial_]){
					Epk += psq*m_electrons*f2P*m_dTslice;
				}				
				if(m_bool[DataDump_][spectral_]){
					double arg0 = atan2(phase[nx][2*ny+1], phase[nx][2*ny]);
					int nxy = nx*m_nfft[1]+ny;
					if(m_rank != nxy%m_procs){
						continue;
					}
					double arg, csn[2], dummy;
					vector<double> &fsn = m_fsr[np][nh][nxy];
					for(int nt = -m_nfftsp/2; nt <= m_nfftsp/2; nt++){
						arg = arg0-PI2*nt/m_nfftsp;
						csn[0] = cos(arg);
						csn[1] = sin(arg);
						int ntr = nt+m_nfftsp/2;
						if(n > 0){
							fsn[2*ntr] = (dummy=fsn[2*ntr])*csn[0]-fsn[2*ntr+1]*csn[1];
							fsn[2*ntr+1] = dummy*csn[1]+fsn[2*ntr+1]*csn[0];
						}
						fsn[2*ntr] += F[np][nh][n][nx][2*ny];
						fsn[2*ntr+1] += F[np][nh][n][nx][2*ny+1];
						m_Fsr[nh][ntr] += hypotsq(fsn[2*ntr], fsn[2*ntr+1])*f2f*m_electrons;
					}
				}
			}
		}
		if(m_bool[DataDump_][spatial_]){
			Epk /= PI2*m_sizexy[0][n]*m_sizexy[1][n]*1e6; // W/m^2 -> W/mm^2
			for(int nx = 0; nx < m_nfft[0]; nx++){
				double xr = fft_index(nx, m_nfft[0], 1)*m_dxy[0]/m_sizexy[0][n];
				xr *= xr/2;
				for(int ny = 0; ny < m_nfft[1]; ny++){
					double yr = fft_index(ny, m_nfft[1], 1)*m_dxy[1]/m_sizexy[1][n];
					yr *= yr/2;
					m_psr[1][nh][nx*m_nfft[1]+ny] += Epk*exp(-xr-yr);
				}
			}
		}
	}

	if(m_bool[DataDump_][spectral_] && m_procs > 1){
		double fsr;
		for(int nt = 0; nt <= m_nfftsp+1; nt++){
			fsr = m_Fsr[nh][nt];
			if(m_thread != nullptr){
				m_thread->Allreduce(&fsr, &m_Fsr[nh][nt], 1, MPI_DOUBLE, MPI_SUM, m_rank);
			}
			else{
				MPI_Allreduce(&fsr, &m_Fsr[nh][nt], 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
			}
		}
	}

	m_Psr[0][nh] += m_Psr[1][nh];

	if(m_cyclic && m_isGauss){
		int inslice = f_GetSliceOffset(n);
		int outslice = inslice+m_slices;
		m_Psr[0][nh][inslice] = m_Psr[0][nh][outslice];
	}
}

void RadiationHandler::SaveResults(
	int n, ParticleHandler *particle, vector<vector<vector<vector<double>>>> F[])
{
	if(n == 0){
		m_electrons = particle->GetCharge()/QE;
	}

	double Pinst;
	for(int nh = 0; nh < m_nhmax; nh++){
		double kr, sigsq, atanr[2], sigzh[2], sighxy = 1, sigh[2];
		bool nheven = nh%2 > 0;

		if(m_isGauss){
			f_GetSR(n, nh, F);
		}

		if(m_skipwave){
			kr = (nh+1)*PI2/m_lambda1;
			for(int j = 0; j < 2; j++){
				sigh[j] = kr*m_bfsize[j][nh][n];
				sighxy *= sigh[j];
			}
			for(int m = 0; m < n; m++){
				double zh = (m_z[m]-m_z[n])*kr/2;
				for(int j = 0; j < 2; j++){
					sigsq = hypotsq(m_bfsize[j][nh][n], m_bfsize[j][nh][m])*kr*kr/2;
					atanr[j] = atan2(zh, sigsq)/2;
					sigzh[j] = sqrt(sqrt(hypotsq(zh, sigsq)));
				}
				m_pampl[0][m] = cos(-atanr[0]-atanr[1])/(sigzh[0]*sigzh[1]);
				m_pampl[1][m] = sin(-atanr[0]-atanr[1])/(sigzh[0]*sigzh[1]);
				if(nheven){
					double phase, denom;
					for(int np = 0; np < m_np; np++){
						phase = -atanr[0]-atanr[1]-atanr[np]*2;
						denom = sigzh[0]*sigzh[1]*(sigzh[np]*sigzh[np])*2;
						m_paeven[2*np  ][m] = cos(phase)/denom;
						m_paeven[2*np+1][m] = sin(phase)/denom;
					}
				}
			}
			if(m_exseed && nh == 0){
				double zh = (m_Zw-m_z[n])*kr/2;
				for(int j = 0; j < 2; j++){
					sigsq = hypotsq(m_bfsize[j][nh][n], m_sigmar*SQRT2)*kr*kr/2;
					// RMS of seed radiation field is sigma*sqrt(2)
					atanr[j] = atan2(zh, sigsq)/2;
					sigzh[j] = sqrt(sqrt(hypotsq(zh, sigsq)));
				}
				m_pampl_seed[0] = cos(-atanr[0]-atanr[1])/(sigzh[0]*sigzh[1]);
				m_pampl_seed[1] = sin(-atanr[0]-atanr[1])/(sigzh[0]*sigzh[1]);
			}
		}

#ifdef _DEBUG
		ofstream debug_out;
		vector<string> titles {"s", "P"};
		vector<double> items(titles.size());
		if(!RadiatioPinst.empty() && m_rank == 0){
			debug_out.open(RadiatioPinst);
		}
#endif

		for(int ns = m_sranges[0]; ns <= m_sranges[1]; ns++){
			if(ns < 0 || ns >= m_slices_total){
				continue;
			}
			if(!m_skipwave || m_isGaussDebug){
				Pinst = 0;
				for(int np = 0; np < m_np; np++){
					for(int nx = 0; nx < m_nfft[0]; nx++){
						for(int ny = 0; ny < m_nfft[1]; ny++){
							m_E[np][nh][1][ns][nx][2*ny] = m_E[np][nh][2][ns][nx][2*ny];
							m_E[np][nh][1][ns][nx][2*ny+1] = m_E[np][nh][2][ns][nx][2*ny+1];
							Pinst += hypotsq(m_E[np][nh][2][ns][nx][2*ny], m_E[np][nh][2][ns][nx][2*ny+1]);
						}
					}
				}
				Pinst *= m_E2P[1][nh];
				if(m_isGauss){
					Pinst += m_Psr[0][nh][ns];
				}

#ifdef _DEBUG
				if(!RadiatioPinst.empty() && m_rank == 0){
					items[0] = ns;
					items[1] = Pinst;
					PrintDebugItems(debug_out, items);
				}
#endif

			}
			if(m_skipwave){
				double PinstG = m_Psr[1][nh][ns]/(m_E2pd[0][nh]*1e6);
				if(n > 0){
					PinstG += m_Pinst[nh][n-1][ns]/(m_E2pd[0][nh]*1e6);
				}

				for(int np = 0; np < m_np; np++){
					if(nheven){
						PinstG += PI*hypotsq(m_eorg[np][nh][n][2*ns], m_eorg[np][nh][n][2*ns+1])/(sighxy*sigh[np]*sigh[np]*2);
					}

					else{
						PinstG += PI*hypotsq(m_eorg[np][nh][n][2*ns], m_eorg[np][nh][n][2*ns+1])/sighxy;
					}

					double eri[2] = {0, 0};
					for(int m = m_mini[nh]; m < n; m++){
						if(nheven){
							eri[0] += m_eorg[np][nh][m][2*ns]*m_paeven[2*np  ][m]+m_eorg[np][nh][m][2*ns+1]*m_paeven[2*np+1][m];
							eri[1] += m_eorg[np][nh][m][2*ns]*m_paeven[2*np+1][m]-m_eorg[np][nh][m][2*ns+1]*m_paeven[2*np  ][m];
						}
						else{
							eri[0] += m_eorg[np][nh][m][2*ns]*m_pampl[0][m]+m_eorg[np][nh][m][2*ns+1]*m_pampl[1][m];
							eri[1] += m_eorg[np][nh][m][2*ns]*m_pampl[1][m]-m_eorg[np][nh][m][2*ns+1]*m_pampl[0][m];
						}
					}
					if(m_exseed && nh == 0 && np == 0 && n > 0){
						// add only the cross term between seed and coherent radiation
						// seed power is added later, after the final step
						eri[0] += m_e0s[0][ns]*m_pampl_seed[0]+m_e0s[1][ns]*m_pampl_seed[1];
						eri[1] += m_e0s[0][ns]*m_pampl_seed[1]-m_e0s[1][ns]*m_pampl_seed[0];
					}
					PinstG += PI2*(m_eorg[np][nh][n][2*ns]*eri[0]-m_eorg[np][nh][n][2*ns+1]*eri[1]);
				}
				PinstG *= m_E2pd[0][nh]*1e6; // GW/mrad^2 -> GW/rad^2
				if(m_isGaussDebug){
					if(Pinst > 0){
						double seedP = 0;
						if(m_exseed){
							seedP = PI*hypotsq(m_e0s[0][ns], m_e0s[1][ns])/m_sigh2seed*m_E2pd[0][nh]*1e6;
						}
						// add seed power for comparison
						double err = fabs((PinstG+seedP)/Pinst-1);
#ifdef _DEBUGINF
						if(err > 5e-2){
							cout << scientific << setprecision(3) << ns << ": " << "Rad. Power Error: " << err << endl;
						}
#endif
					}
				}
				Pinst = PinstG;
			}
			if(m_rank == m_rank_admin[ns]){
				m_Pinst[nh][n][ns] = Pinst;
			}
		}
#ifdef _DEBUG
		if(!RadiatioPinst.empty() && m_rank == 0){
			debug_out.close();
		}
#endif
		if(m_procs > 1){
			for(int ns = 0; ns < m_slices_total; ns++){
				if(m_rank_admin[ns] < 0){
					continue;
				}
				Pinst = 0;
				if(m_rank == m_rank_admin[ns]){
					Pinst = m_Pinst[nh][n][ns];
				}
				if(m_thread != nullptr){
					m_thread->Bcast(&Pinst, 1, MPI_DOUBLE, m_rank_admin[ns], m_rank);
				}
				else{
					MPI_Bcast(&Pinst, 1, MPI_DOUBLE, m_rank_admin[ns], MPI_COMM_WORLD);
				}
				if(m_rank != m_rank_admin[ns]){
					m_Pinst[nh][n][ns] = Pinst;
				}
			}
		}
	}

	int nsoffset = f_GetSliceOffset(n);
	if(m_skipwave && m_cyclic){
		for(int nh = 0; nh < m_nhmax; nh++){
			for(int ns = nsoffset; ns >= 0; ns--){
				m_Pinst[nh][n][ns] = m_Pinst[nh][n][ns+m_slices];
				for(int np = 0; np < m_np; np++){
					for(int j = 0; j < 2; j++){
						m_eorg[np][nh][n][2*ns+j] = m_eorg[np][nh][n][2*(ns+m_slices)+j];
					}
				}
			}
		}
	}

	double Eri[2];
	for(int nh = 0; nh < m_nhmax; nh++){
		for(int i = 0; i < 2; i++){
			m_Pax[i][nh][n] = 0;
		}
		for(int np = 0; np < m_np; np++){
			for(int ns = 0; ns < m_slices_total; ns++){
				if(m_rank != m_rank_admin[ns]){
					continue;
				}
				int nq = ns-nsoffset;
				if(nq < 0 || nq >= m_slices){
					continue;
				}
				if(m_skipwave){
					m_Eaxis[np][nh][2*ns] += m_eorg[np][nh][n][2*ns];
					m_Eaxis[np][nh][2*ns+1] += m_eorg[np][nh][n][2*ns+1];
					if(m_exseed && np == 0 && nh == 0){
						m_Eaxis[np][nh][2*ns] += m_e0s[0][ns];
						m_Eaxis[np][nh][2*ns+1] += m_e0s[1][ns];
					}
					m_Pax[0][nh][n] += hypotsq(m_Eaxis[np][nh][2*ns], m_Eaxis[np][nh][2*ns+1]); // far
					if(m_assigned[ns][0] >= 0){
						particle->GetRadFieldAt(np, nh, m_assigned[ns][0], Eri);
					}
					else{
						f_GetNearFieldGauss(np, nh, ns, 0, Eri);
					}
					m_Pax[1][nh][n] += hypotsq(Eri[0], Eri[1]); // near
				}
				else{
					m_Pax[1][nh][n] += hypotsq(m_E[np][nh][2][ns][0][0], m_E[np][nh][2][ns][0][1]); // near
					if(m_exseed && np == 0 && nh == 0){
						m_Pax[0][nh][n] +=
							hypotsq(m_E[np][nh][0][ns][0][0]+m_e0s[0][ns], m_E[np][nh][0][ns][0][1]+m_e0s[1][ns]); // far; add seed field
					}
					else{
						m_Pax[0][nh][n] += hypotsq(m_E[np][nh][0][ns][0][0], m_E[np][nh][0][ns][0][1]); // far
					}
				}
			}
		}
		for(int i = 0; i < 2; i++){
			if(m_steadystate){
				m_Pax[i][nh][n] *= m_E2pd[i][nh]*1e-9; // power density in GW
			}
			else{
				m_Pax[i][nh][n] *= m_E2pd[i][nh]*m_dTslice;
			}
		}
		if(m_procs > 1){
			for(int i = 0; i < 2; i++){
				double temp = m_Pax[i][nh][n];
				if(m_thread != nullptr){
					m_thread->Allreduce(&temp, &m_Pax[i][nh][n], 1, MPI_DOUBLE, MPI_SUM, m_rank);
				}
				else{
					MPI_Allreduce(&temp, &m_Pax[i][nh][n], 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
				}
			}
		}
	}

	int dn = max(1, (int)floor(0.5+m_prm[DataDump_][profstep_]));
	if(n != m_totalsteps-1 && (m_totalsteps-1-n)%dn > 0){
		return;
	}

	m_zprof.push_back(m_z[n]);
	int curridx = (int)m_zprof.size()-1;
	for(int nh = 0; nh < m_nhmax; nh++){
		if(m_bool[DataDump_][temporal_]){
			f_GetTemporal(n, nh, curridx);
		}
		if(m_bool[DataDump_][spectral_]){
			f_GetSpectrum(n, nh, 1, curridx);
		}
		if(m_bool[DataDump_][angular_]){
			m_curvature[nh][curridx] = f_GetFocalIntensity(n, nh);
			f_GetSpatialProfile(n, nh, 0, curridx);
		}
		if(m_bool[DataDump_][spatial_]){
			f_GetSpatialProfile(n, nh, 1, curridx);
		}
	}
}

void RadiationHandler::SetNearField(int n, int j)
{
	f_SetSeedField(n);
	
	if(m_skipwave && !m_isGaussDebug){
		return;
	}

	for(int nh = 0; nh < m_nhmax; nh++){
		for(int ns = m_sranges[0]; ns <= m_sranges[1]; ns++){
			if(ns < 0 || ns >= m_slices_total){
				continue;
			}
			for(int np = 0; np < m_np; np++){
				for(int nx = 0; nx < m_nfft[0]; nx++){
					for(int ny = 0; ny < m_nfft[1]; ny++){
						m_E[np][nh][j][ns][nx][2*ny] = m_f2n*m_E[np][nh][0][ns][nx][2*ny];
						m_E[np][nh][j][ns][nx][2*ny+1] = m_f2n*m_E[np][nh][0][ns][nx][2*ny+1];
					}
				}
				// compute near field by bunching at ns-th slice
				m_fft->DoFFT(m_E[np][nh][j][ns], 1);
			}
			if(m_exseed && nh == 0){ // add seed field
				for(int nx = 0; nx < m_nfft[0]; nx++){
					for(int ny = 0; ny < m_nfft[1]; ny++){
						m_E[0][nh][j][ns][nx][2*ny  ] += m_E0s[0][ns]*m_Eseed[nx][2*ny  ]-m_E0s[1][ns]*m_Eseed[nx][2*ny+1];
						m_E[0][nh][j][ns][nx][2*ny+1] += m_E0s[0][ns]*m_Eseed[nx][2*ny+1]+m_E0s[1][ns]*m_Eseed[nx][2*ny];
					}
				}
			}
		}
	}

	if(m_procs > 1 && n >= 0){ // assign field for slices out of this rank
		for(int ns = m_sranges[0]; ns <= m_sranges[1]; ns++){
			if(ns < 0 || ns >= m_slices_total){
				continue;
			}
			m_onslices[ns] = 0;
		}
		if(m_thread != nullptr){
			m_thread->Allreduce(m_onslices, m_wsonslices, m_slices_total, MPI_INT, MPI_SUM, m_rank);
		}
		else{
			MPI_Allreduce(m_onslices, m_wsonslices, m_slices_total, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
		}
		for(int ns = 0; ns < m_slices_total; ns++){
			if(m_wsonslices[ns] > 0 && m_rank_admin[ns] >= 0){
				for(int np = 0; np < m_np; np++){
					for(int nh = 0; nh < m_nhmax; nh++){
						if(m_thread != nullptr){
							m_thread->Bcast(m_ws[np][nh][j]+ns*m_ngrids, m_ngrids, MPI_DOUBLE, m_rank_admin[ns], m_rank);
						}
						else{
							MPI_Bcast(m_ws[np][nh][j]+ns*m_ngrids, m_ngrids, MPI_DOUBLE, m_rank_admin[ns], MPI_COMM_WORLD);
						}
					}
				}
			}
		}
	}

#ifdef _DEBUG
	if(!RadiationSpatial.empty() && f_IsExportDebug(n) && m_rank == 0){
		string far = RadiationSpatial+"_far.dat";
		string near = RadiationSpatial+"_near.dat";
		f_ExportField(false, false, 0, ExportSlice, 0, far);
		f_ExportField(false, true, j, ExportSlice, 0, near);
//		f_ExportField(false, false, 0, m_nsorg-n, 0, far);
//		f_ExportField(false, true, j, m_nsorg-n, 0, near);
	}
	if(!RadiationTemporal.empty() && f_IsExportDebug(n) && m_rank == 0){
		string dataname = RadiationTemporal+"_near";
		f_ExportFieldTemp(n, true, j, 0, dataname);
	}
	MPI_Barrier(MPI_COMM_WORLD);
#endif
}

void RadiationHandler::SetSeedField(int n)
// for evaluation of laser modulation
{
	f_SetSeedField(n);
	for(int ns = 0; ns < m_slices_total; ns++){
		m_E[0][0][1][ns][0][0] = m_E[0][0][2][ns][0][0];
		m_E[0][0][1][ns][0][1] = m_E[0][0][2][ns][0][1];
		m_E[0][0][2][ns][0][0] = m_E0s[0][ns]*m_Eseed[0][0]-m_E0s[1][ns]*m_Eseed[0][1];
		m_E[0][0][2][ns][0][1] = m_E0s[0][ns]*m_Eseed[0][1]+m_E0s[1][ns]*m_Eseed[0][0];
	}
}

void RadiationHandler::SetBunchFactor(int n, ParticleHandler *particle)
{
	if(m_isGauss){
		double bmsize[] = {m_sizexy[0][n], m_sizexy[1][n]};
		particle->GetSliceBunchFactor(n, m_BG, m_bfg, bmsize);
	}
	else{
		particle->GetBunchFactor(m_B);
	}
}

void RadiationHandler::AdvanceParticle(
	int n, ParticleHandler *particle, vector<vector<vector<vector<double>>>> F[])
{
	particle->AdvanceParticle(n, F, m_E, this);
}

void RadiationHandler::AdvanceChicane(int nstep, ParticleHandler *particle, PrintCalculationStatus *status)
{
	for(int nh = 0; nh < m_nhmax; nh++){
		f_BcastField(nh, 0);
	}

	double sslip;
	if(m_select[Chicane_][monotype_] == XtalTransLabel || m_select[Chicane_][monotype_] == NotAvaliable){
		sslip = m_prm[Chicane_][delay_]*1e-15*CC;
	}
	else{
		sslip = m_prm[Chicane_][reltiming_]*1e-15*CC;
	}
	sslip -= m_N*m_lambda1; // compensate for e- shift
	int nslip = (int)floor(0.5+sslip/m_lslice);

	if(m_select[Chicane_][monotype_] != NotAvaliable){
		int nfftsp = m_nfftsp;
		double e1st = photon_energy(m_lambda1);

		double demax;
		if(m_select[Chicane_][monotype_] == CustomLabel){
			vector<double> egrid;
			m_monoprf.GetArray1D(0, &egrid);
			demax = (egrid.back()-egrid.front())/egrid.size();
		}
		else{
			double dummy;
			RockingCurve rocking(m_prm[Chicane_]);
			rocking.GetBandWidth(&demax, &dummy);
			demax *= e1st/2;
		}
		double de = PLANCK/(nfftsp*m_dTslice);
		while(de > demax){
			nfftsp <<= 1;
			de /= 2;
		}
		if(m_select[Chicane_][monotype_] == XtalTransLabel){
			while(m_lslice*nfftsp < 2*sslip){
				nfftsp <<= 1;
			}
		}
		double *wssp = new double[2*nfftsp];

		FastFourierTransform fft(1, nfftsp);

		vector<double> reflec[2];
		for(int j = 0; j < 2; j++){
			reflec[j].resize(nfftsp);
		}
		if(m_select[Chicane_][monotype_] == CustomLabel){
			vector<double> reftmp[3];
			for(int j = 0; j < 3; j++){
				m_monoprf.GetArray1D(j, &reftmp[j]);
			}
			Spline spl;
			double zero = 0;
			for(int j = 0; j < 2; j++){
				spl.SetSpline((int)reftmp[0].size(), &reftmp[0], &reftmp[j+1]);
				for(int n = 0; n < nfftsp; n++){
					double ep = de*fft_index(n, nfftsp, 1)+e1st-m_prm[Chicane_][monoenergy_];
					reflec[j][n] = spl.GetValue(ep, true, nullptr, &zero);
				}
			}
		}
		else{
			double W, Ew[2];
			RockingCurve rocking(m_prm[Chicane_]);
			for(int n = 0; n < nfftsp; n++){
				double ep = de*fft_index(n, nfftsp, 1)+e1st-m_prm[Chicane_][monoenergy_];
				for(int j = 0; j < 2; j++){
					double dlam = -ep/(m_prm[Chicane_][monoenergy_]+ep);
					rocking.GetAmplitudeAsRelLambda(dlam, &W, Ew, m_select[Chicane_][monotype_] == XtalReflecLabel);
					reflec[j][n] = Ew[j];
				}
			}
		}

		double refat[2];
		double Ds = (double)(3*m_segsteps-2)/m_nfft[0], dstep = 0;
		for(int nh = 0; nh < m_nhmax; nh++){
			for(int nx = 0; nx < m_nfft[0]; nx++){
				for(int ny = 0; ny < m_nfft[1]; ny++){
					for(int np = 0; np < m_np; np++){
						for(int ns = 0; ns < nfftsp; ns++){
							if(ns >= m_slices_total || m_rank_admin[ns] < 0){
								wssp[2*ns] = wssp[2*ns+1] = 0;
							}
							else{
								wssp[2*ns] = m_E[np][nh][0][ns][nx][2*ny];
								wssp[2*ns+1] = m_E[np][nh][0][ns][nx][2*ny+1];
							}
						}
						fft.DoFFT(wssp, -1); // do fft by time, not by s (bunch position)
						for(int ns = 0; ns < nfftsp; ns++){
							for(int j = 0; j < 2; j++){
								refat[j] = reflec[j][ns]/nfftsp;
							}
							multiply_complex(&wssp[2*ns], &wssp[2*ns+1], refat);
						}
#ifdef _DEBUG
						if(!RadiationSSSpec.empty() && nx == 0 && ny == 0 && m_rank == 0){
							ofstream debug_out(RadiationSSSpec);
							vector<string> titles{"Energy", "Re", "Im", "Tre", "Tim"};
							vector<double> items(titles.size());
							PrintDebugItems(debug_out, titles);
							for(int ns = -nfftsp/2; ns <= nfftsp/2; ns++){
								items[0] = ns*de;
								int eidx = fft_index(ns, nfftsp, -1);
								items[1] = wssp[2*eidx];
								items[2] = wssp[2*eidx+1];
								items[3] = reflec[0][eidx];
								items[4] = reflec[1][eidx];
								PrintDebugItems(debug_out, items);
							}
							debug_out.close();
						}
#endif
						fft.DoFFT(wssp, 1);
						for(int ns = 0; ns < m_slices_total; ns++){
							int nst = ns-nslip;
							if(abs(nst) >= nfftsp/2){
								m_E[np][nh][0][ns][nx][2*ny] = m_E[np][nh][0][ns][nx][2*ny+1] = 0;
							}
							else{
								int nsidx = fft_index(nst, nfftsp, -1);
								m_E[np][nh][0][ns][nx][2*ny] = wssp[2*nsidx];
								m_E[np][nh][0][ns][nx][2*ny+1] = wssp[2*nsidx+1];
							}
						}
					}
				}
				dstep += Ds;
				if(dstep > 1){
					int sst = (int)floor(dstep);
					dstep -= sst;
					status->AdvanceStep(0, sst);
				}
			}
		}
		delete[] wssp;
	}
	else if(nslip != 0){
		for(int nh = 0; nh < m_nhmax; nh++){
			for(int nx = 0; nx < m_nfft[0]; nx++){
				for(int ny = 0; ny < m_nfft[1]; ny++){
					for(int np = 0; np < m_np; np++){
						if(nslip > 0){
							for(int ns = m_slices_total-1; ns >= 0; ns--){
								int nst = ns-nslip;
								if(nst < 0){
									m_E[np][nh][0][ns][nx][2*ny] = m_E[np][nh][0][ns][nx][2*ny+1] = 0;
								}
								else{
									m_E[np][nh][0][ns][nx][2*ny] = m_E[np][nh][0][nst][nx][2*ny];
									m_E[np][nh][0][ns][nx][2*ny+1] = m_E[np][nh][0][nst][nx][2*ny+1];
								}
							}
						}
						else{
							for(int ns = 0; ns < m_slices_total; ns++){
								int nst = ns-nslip;
								if(nst >= m_slices_total){
									m_E[np][nh][0][ns][nx][2*ny] = m_E[np][nh][0][ns][nx][2*ny+1] = 0;
								}
								else{
									m_E[np][nh][0][ns][nx][2*ny] = m_E[np][nh][0][nst][nx][2*ny];
									m_E[np][nh][0][ns][nx][2*ny+1] = m_E[np][nh][0][nst][nx][2*ny+1];
								}
							}
						}
					}
				}
			}
		}
	}

	f_AdvanceDrift(m_N*m_lu);
	status->AdvanceStep(0);

#ifdef _DEBUG
	if(!RadiationSSTemp.empty() && m_rank == 0){
		f_ExportFieldTemp(nstep, false, 0, 0, RadiationSSTemp);
	}
	MPI_Barrier(MPI_COMM_WORLD);
#endif

	// shift the parameters to handle slice positions for each rank
	for(int n = 0; n < m_slices_total-m_segsteps; n++){
		m_rank_admin[n] = m_rank_admin[n+m_segsteps];
	}
	if(!m_steadystate){
		m_sranges[0] -= m_segsteps; // shift the entrance of slice range
	}

	SetNearField(nstep); // compute near-field radiation in the slice range
	if(!m_steadystate){
		m_sranges[1] -= m_segsteps; // shift the exit of the slice range to save
	}
	if(m_cyclic){
		f_CyclicShift(nstep);
	}
	if(m_bool[DataDump_][radiation_] && m_zexport[nstep]){
		f_WriteData(nstep);
	}

	for(int nh = 0; nh < m_nhmax; nh++){
		m_bf[nh][nstep] = particle->GetTotalBunchFactor(nh);
	}	
}

void RadiationHandler::GetGainCurves(vector<vector<double>> &pulseE,
	vector<vector<double>> &Pdn, vector<vector<double>> &Pdf, vector<vector<double>> &bf)
{
	if(m_skipwave && m_exseed){
		// add the seed power before evaluating the total radiation power
		for(int ns = 0; ns < m_slices_total; ns++){
			double seedP = PI*hypotsq(m_e0s[0][ns], m_e0s[1][ns])/m_sigh2seed*m_E2pd[0][0]*1e6;
			for(int n = 0; n < m_totalsteps; n++){
				m_Pinst[0][n][ns] += seedP;
			}
		}
	}

	pulseE.resize(m_nhmax);
	for(int nh = 0; nh < m_nhmax; nh++){
		pulseE[nh].resize(m_totalsteps);
		for(int n = 0; n < m_totalsteps; n++){
			int nsoffset = f_GetSliceOffset(n);
			pulseE[nh][n] = 0;
			for(int ns = 0; ns < m_slices; ns++){
				if(m_steadystate){
					pulseE[nh][n] += m_Pinst[nh][n][0]*1e-9; // W -> GW
				}
				else{
					pulseE[nh][n] += m_Pinst[nh][n][ns+nsoffset+1]*m_dTslice;
				}
			}
		}
	}
	Pdn = m_Pax[1];
	Pdf = m_Pax[0];
	bf = m_bf;
}

void RadiationHandler::GetZProfiles(vector<double> &zprof)
{
	zprof = m_zprof;
}

void RadiationHandler::GetTemporal(vector<vector<vector<double>>> &Pinst)
{
	Pinst = m_Pexprt;
}

void RadiationHandler::GetSpectrum(vector<double> &ep, vector<vector<vector<double>>> &Flux)
{
	ep =  m_ep;
	Flux = m_Flux;
}

void RadiationHandler::GetCurvature(vector<vector<double>> &curvature)
{
	curvature = m_curvature;
}

void RadiationHandler::SetFieldAt(int mp, 
	int n, int nh, int ns, int nx, int ny, vector<vector<double>> *Efp)
{
	int ixy = nx*m_nfft[1]+ny;
	int mpfix = m_assigned[ns][ixy];
	if(mpfix >= 0){
		for(int j = 0; j < 2; j++){
			for(int np = 0; np < m_np; np++){
				Efp[np][nh][2*mp+j] = Efp[np][nh][2*mpfix+j];
			}
		}
		return;
	}

	double Eri[2];
	for(int np = 0; np < m_np; np++){
		f_GetNearFieldGauss(np, nh, ns, ixy, Eri);
		Efp[np][nh][2*mp] = Eri[0];
		Efp[np][nh][2*mp+1] = Eri[1];
		if(m_exseed && np == 0){
			Efp[np][nh][2*mp] += m_E0s[0][ns]*m_Eseed[nx][2*ny]-m_E0s[1][ns]*m_Eseed[nx][2*ny+1];
			Efp[np][nh][2*mp+1] += m_E0s[0][ns]*m_Eseed[nx][2*ny+1]+m_E0s[1][ns]*m_Eseed[nx][2*ny];
		}
	}
	m_assigned[ns][ixy] = mp;
}

double RadiationHandler::GetMaxNearField()
{
	double Eri[2], Emax = 0, Er;

	for(int ns = m_sranges[0]; ns <= m_sranges[1]; ns++){
		if(ns < 0 || ns >= m_slices_total){
			continue;
		}
		Er = 0;
		for(int np = 0; np < m_np; np++){
			f_GetNearFieldGauss(np, 0, ns, 0, Eri);
			Er += hypotsq(Eri[0], Eri[1]);
		}
		Emax = max(Emax, sqrt(Er));
	}
	if(m_procs > 1){
		Er = Emax;
		if(m_thread != nullptr){
			m_thread->Allreduce(&Er, &Emax, 1, MPI_DOUBLE, MPI_MAX, m_rank);
		}
		else{
			MPI_Allreduce(&Er, &Emax, 1, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
		}
	}
	return Emax;
}

void RadiationHandler::f_GetNearFieldGauss(int np, int nh, int ns, int ixy, double *Eri)
{
	Eri[0] = Eri[1] = 0;
	for(int nsec = 0; nsec < m_Esec[nh]; nsec++){
		Eri[0] += m_etgt[np][nh][nsec][2*ns]*m_GnAvg[nh][nsec][2*ixy]-m_etgt[np][nh][nsec][2*ns+1]*m_GnAvg[nh][nsec][2*ixy+1];
		Eri[1] += m_etgt[np][nh][nsec][2*ns]*m_GnAvg[nh][nsec][2*ixy+1]+m_etgt[np][nh][nsec][2*ns+1]*m_GnAvg[nh][nsec][2*ixy];
	}
}

void RadiationHandler::f_SetSecRange(int n, int nh, vector<int> secrange[])
{
	double lambdan = m_lambda_s/(nh+1);
	double dcurr[2] = {1, 0};
	double dlimit = 0.05;
	for(int j = 0; j < 2; j++){
		secrange[j].clear();
	}
	secrange[0].push_back(0);
	double xyh, arg, zmn, zmnsqrt, zmnqdrt, zrayl, sigxy, gr[2];
	for(int m = 0; m < n; m++){
		double curr = 1;
		for(int j = 0; j < 2; j++){
			zrayl = PI2*m_bfsize[j][nh][m]*m_bfsize[j][nh][m]/lambdan;
			zmn = (m_z[n]-m_z[m])/zrayl;
			zmnsqrt = sqrt(1+zmn*zmn);
			curr /= sqrt(zmnsqrt);
		}
		if(dcurr[0] > curr){
			dcurr[0] = curr;
		}
		if(dcurr[1] < curr){
			dcurr[1] = curr;
		}
		if(dcurr[1]-dcurr[0] > dlimit){
			secrange[1].push_back(m);
			secrange[0].push_back(m+1);
			dcurr[0] = 1;
			dcurr[1] = 0;
		}
	}
	secrange[1].push_back(n);
	m_Esec[nh] = (int)secrange[0].size();
	for(int nsec = 0; nsec < m_Esec[nh]; nsec++){
		fill(m_GnAvg[nh][nsec].begin(), m_GnAvg[nh][nsec].end(), 0);
		int nsstep = secrange[1][nsec]-secrange[0][nsec]+1;
		for(int m = secrange[0][nsec]; m <= secrange[1][nsec]; m++){
			for(int j = 0; j < 2; j++){
				zrayl = PI2*m_bfsize[j][nh][m]*m_bfsize[j][nh][m]/lambdan;
				zmn = (m_z[n]-m_z[m])/zrayl;
				zmnsqrt = sqrt(1+zmn*zmn);
				zmnqdrt = sqrt(zmnsqrt);
				sigxy = m_bfsize[j][nh][m]*zmnsqrt;
				for(int nxy = 0; nxy < m_nfft[j]; nxy++){
					xyh = m_dxy[j]*fft_index(nxy, m_nfft[j], 1)/sigxy;
					xyh *= 0.5*xyh;
					arg = xyh*zmn;
					m_Gxy[j][2*nxy] = exp(-xyh)/zmnqdrt;
					m_Gxy[j][2*nxy+1] = m_Gxy[j][2*nxy]*sin(arg);
					m_Gxy[j][2*nxy] *= cos(arg);
				}
			}
			for(int nx = 0; nx < m_nfft[0]; nx++){
				for(int ny = 0; ny < m_nfft[1]; ny++){
					int nxy = nx*m_nfft[1]+ny;
					gr[0] = (m_Gxy[0][2*nx]*m_Gxy[1][2*ny]-m_Gxy[0][2*nx+1]*m_Gxy[1][2*ny+1]);
					gr[1] = (m_Gxy[0][2*nx]*m_Gxy[1][2*ny+1]+m_Gxy[0][2*nx+1]*m_Gxy[1][2*ny]);
					m_GnAvg[nh][nsec][2*nxy] += gr[0]/nsstep;
					m_GnAvg[nh][nsec][2*nxy+1] += gr[1]/nsstep;
				}
			}
		}
	}
}

void RadiationHandler::GetSpatialProfile(int jnf, vector<vector<double>> &xy, vector<vector<vector<double>>> &Pd)
{
	double *dxy = jnf == 0 ? m_qxy : m_dxy;
	for(int j = 0; j < 2; j++){
		xy[j].resize(m_nfft[j]+1);
		for(int n = -m_nfft[j]/2; n <= m_nfft[j]/2; n++){
			xy[j][n+m_nfft[j]/2] = dxy[j]*n*1000; // m,rad -> mm, mrad
		}
	}
	Pd = m_Pd[jnf];
}

void RadiationHandler::DoPostProcess(PrintCalculationStatus *status,
	vector<string> &titles, vector<string> &units, int *variables,
	vector<vector<double>> &vararray, vector<vector<vector<double>>> &data)
{
	string exyunit = m_select[PostP_][zone_] == PostPFarLabel ? ExyFarUnit : ExyUnit;
	string xlabel, ylabel, xunit, yunit, edlabel, edunit, pdlabel, pdunit, fdlabel, fdunit;
	vector<double> earr, zarr, sarr;
	vector<vector<double>> xyarr(2);
	int steprange[2], erange[2], nrange[2], slicerange[2];

	int avgslices = (int)ceil(m_array[PostP_][smoothing_][0]*GAUSSIAN_MAX_REGION);
	int jnf = m_select[PostP_][zone_] == PostPFarLabel ? 0 : 1;
	if(m_iswignerX || m_iswignerY){
		jnf = 0;
	}

	f_ArrangePostProcessing(zarr, sarr, xyarr, steprange, slicerange, nrange);

	for(int j = 0; j < 2; j++){
		erange[j] = (int)floor(0.5+m_array[PostP_][energywindow_][j]);
	}
	if(erange[0] > erange[1]){
		swap(erange[0], erange[1]);
	}
	if(m_select[PostP_][energyrange_] == PostPIntegFullLabel){
		erange[0] = -m_nfftsp/2;
		erange[1] = m_nfftsp/2;
	}
	else{
		erange[0] = max(-m_nfftsp/2, erange[0]);
		erange[1] = min(m_nfftsp/2, erange[1]);
	}
	earr.resize(erange[1]-erange[0]+1);
	double de = PLANCK/(m_nfftsp*m_dTslice);
	for(int n = erange[0]; n <= erange[1]; n++){
		int eindex = fft_index(n, m_nfftsp, -1);
		earr[n-erange[0]] = de*n+photon_energy(m_lambda1/(m_nhpp+1));
	}

	for(int j = 0; j < 4; j++){
		for(int ns = 0; ns < m_nfftsp; ns++){
			m_Epp[j][ns].resize((2*nrange[0]+1)*(2*nrange[1]+1));
		}
	}

	if(m_iswignerX || m_iswignerY){
		int jxy = m_iswignerX ? 0 : 1;
		if(m_select[PostP_][spatrange_] == PostPIntegFullLabel){
			nrange[0] = m_nfft[jxy]/2;
		}
		else{
			nrange[0] = min(m_nfft[jxy]/2, max(0, (int)floor(0.5+m_array[PostP_][spatwindow_][jxy])));
		}
		if(m_select[PostP_][anglrange_] == PostPIntegFullLabel){
			nrange[1] = m_nfft[jxy]/2;
		}
		else{
			nrange[1] = min(m_nfft[jxy]/2, max(0, (int)floor(0.5+m_array[PostP_][anglindow_][jxy])));
		}
		for(int j = 0; j < 2; j++){
			xyarr[j].resize(2*nrange[j]+1);
			double dxy = j == 1 ? m_qxy[jxy]/(m_nhpp+1) : m_dxy[jxy];
			for(int n = -nrange[j]; n <= nrange[j]; n++){
				xyarr[j][n+nrange[j]] = dxy*n*1e3; // m -> mm, rad -> mrad
			}
		}
	}
	if(m_iswignerX){
		xlabel = XLabel;
		ylabel = QxLabel;
		xunit = XYUnit;
		yunit = XYpUnit;
	}
	else if(m_iswignerY){
		xlabel = YLabel;
		ylabel = QyLabel;
		xunit = XYUnit;
		yunit = XYpUnit;
	}
	else if(m_select[PostP_][zone_] == PostPFarLabel){
		xlabel = QxLabel;
		ylabel = QyLabel;
		xunit = XYpUnit;
		yunit = XYpUnit;
		edlabel = AngEnergyDensLabel;
		edunit = AngEnergyDensUnit;
		pdlabel = AngPowerDensLabel;
		pdunit = AngPowerDensUnit;
		fdlabel = AngFluxDensLabel;
		fdunit = AngFluxDensUnit;
	}
	else{
		xlabel = XLabel;
		ylabel = YLabel;
		xunit = XYUnit;
		yunit = XYUnit;
		edlabel = SpatEnergyDensLabel;
		edunit = SpatEnergyDensUnit;
		pdlabel = SpatPowerDensLabel;
		pdunit = SpatPowerDensUnit;
		fdlabel = SpatFluxDensLabel;
		fdunit = SpatFluxDensUnit;
	}

	titles.clear(); units.clear();
	int nslides[2] = {1, 1};
	int nsteps = steprange[1]-steprange[0]+1;
	int nenergies = erange[1]-erange[0]+1;
	int nslices = slicerange[1]-slicerange[0]+1;
	int ngrids = (2*nrange[0]+1)*(2*nrange[1]+1);
	double Wcoef;

	int nvariables = ngrids;
	*variables = 2;

	if(m_iswignerX || m_iswignerY){
		double lambda = m_lambda_s/(m_nhpp+1);
		Wcoef = 2/Z0VAC/lambda/lambda/lambda*1e-6*1e-9; // W/m/rad -> GW/mm/mrad
		titles.push_back(xlabel);
		titles.push_back(ylabel);
		nslides[0] = nsteps;
		if(m_isppalongs){
			Wcoef *= m_dTslice*1e9; // GW -> J
		}
		else {
			nslides[1] = nslices;
			titles.push_back(SLabel);
		}
		titles.push_back(ZLabel);
		m_W.resize(nslices);
		for(int ns = 0; ns < nslices; ns++){
			m_W[ns].resize(ngrids);
		}
		m_Wtmp[0].resize(ngrids);
	}
	else if(m_iswignerT){
		Wcoef = m_E2P[jnf][m_nhpp]/QE/PLANCK*1e-3;
		nvariables = nenergies*nslices;
		nslides[0] = nsteps;
		titles.push_back(SLabel);
		titles.push_back(PhotonELabel);
		titles.push_back(ZLabel);
		m_W.resize(1);
		m_W[0].resize(nslices*nenergies);
		for(int j = 0; j < 2; j++){
			m_Wtmp[j].resize((nslices+avgslices*2)*nenergies);
		}
	}
	else if(m_isppflux){
		nslides[0] = nsteps;
		if(m_isppoxy){
			nvariables = nenergies;
			*variables = 1;
		}
		else{
			nslides[1] = nenergies;
			titles.push_back(xlabel);
			titles.push_back(ylabel);
		}
		titles.push_back(PhotonELabel);
		titles.push_back(ZLabel);
	}
	else if(m_select[PostP_][item_] == PostPCampLabel){
		nslides[0] = nsteps;
		nslides[1] = nslices;
		titles.push_back(xlabel);
		titles.push_back(ylabel);
		titles.push_back(SLabel);
		titles.push_back(ZLabel);
	}
	else{
		if(m_isppoxy){
			if(m_isppalongs){
				nvariables = nsteps;
			}
			else{
				nslides[0] = nsteps;
				nvariables = nslices;
				titles.push_back(SLabel);
			}
			*variables = 1;
		}
		else{
			titles.push_back(xlabel);
			titles.push_back(ylabel);

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
		if(titles[n] == xlabel){
			units.push_back(xunit);
			vararray.push_back(xyarr[0]);
		}
		else if(titles[n] == ylabel){
			units.push_back(yunit);
			vararray.push_back(xyarr[1]);
		}
		else if(titles[n] == PhotonELabel){
			units.push_back(PhotonEUnit);
			vararray.push_back(earr);
		}
		else if(titles[n] == SLabel){
			units.push_back(SUnit);
			vararray.push_back(sarr);
		}
		else if(titles[n] == ZLabel){
			units.push_back(ZUnit);
			vararray.push_back(zarr);
		}
	}

	vector<int> jxyindex;
	if(m_select[PostP_][item_] == PostPCampLabel){
		bool isreal = true, isimag = true, isx = true, isy = true;
		if(m_select[PostP_][realimag_] == PostPRealLabel){
			isimag = false;
		}
		else if(m_select[PostP_][realimag_] == PostPImagLabel){
			isreal = false;
		}
		if(m_select[PostP_][Exy_] == PostPExLabel){
			isy = false;
		}
		else if(m_select[PostP_][Exy_] == PostPEyLabel){
			isx = false;
		}
		if(m_np == 1){
			if(isreal){
				titles.push_back(ERealLabel);
				units.push_back(exyunit);
				jxyindex.push_back(0);
			}
			if(isimag){
				titles.push_back(EImagLabel);
				units.push_back(exyunit);
				jxyindex.push_back(1);
			}
		}
		else{
			if(isx){
				if(isreal){
					titles.push_back(ExRealLabel);
					units.push_back(exyunit);
					jxyindex.push_back(0);
				}
				if(isimag){
					titles.push_back(ExImagLabel);
					units.push_back(exyunit);
					jxyindex.push_back(1);
				}
			}
			if(isy){
				if(isreal){
					titles.push_back(EyRealLabel);
					units.push_back(exyunit);
					jxyindex.push_back(2);
				}
				if(isimag){
					titles.push_back(EyImagLabel);
					units.push_back(exyunit);
					jxyindex.push_back(3);
				}
			}
		}
	}
	else{
		if(m_iswignerX || m_iswignerY){
			if(m_isppalongs){
				titles.push_back(WigEnergyDensLabel);
				units.push_back(WigEnergyDensUnit);
			}
			else{
				titles.push_back(WigPowerDensLabel);
				units.push_back(WigPowerDensUnit);
			}
		}
		else if(m_iswignerT){
			titles.push_back(WigFluxLabel);
			units.push_back(WigFluxUnit);
		}
		else if(m_ispppower){
			if(m_isppalongs){
				if(m_isppoxy){
					titles.push_back(PulseEnergyLabel);
					units.push_back(PulseEnergyUnit);
				}
				else{
					titles.push_back(edlabel);
					units.push_back(edunit);
				}
			}
			else{
				if(m_isppoxy){
					titles.push_back(RadPowerLabel);
					units.push_back(RadPowerUnit);
				}
				else{
					titles.push_back(pdlabel);
					units.push_back(pdunit);
				}
			}
		}
		else{
			if(m_isppoxy){
				titles.push_back(RadFluxLabel);
				units.push_back(RadFluxUnit);
			}
			else{
				titles.push_back(fdlabel);
				units.push_back(fdunit);
			}
		}
		jxyindex.push_back(0);
		if(m_np > 1 && m_iswigner == false){
			if(m_bool[PostP_][s1_]){
				titles.push_back(StokesS1Label);
				units.push_back("-");
				jxyindex.push_back(1);
			}
			if(m_bool[PostP_][s2_]){
				titles.push_back(StokesS2Label);
				units.push_back("-");
				jxyindex.push_back(2);
			}
			if(m_bool[PostP_][s3_]){
				titles.push_back(StokesS3Label);
				units.push_back("-");
				jxyindex.push_back(3);
			}
		}
	}

	int nitems = (int)titles.size()-dimensions;
	data.resize(nslides[0]*nslides[1]);
	for(int ns = 0; ns < nslides[0]*nslides[1]; ns++){
		data[ns].resize(nitems);
		for(int i = 0; i < nitems; i++){
			data[ns][i].resize(nvariables);
		}
	}

	if(m_iswignerX || m_iswignerY){
		status->SetSubstepNumber(1, nslices*m_np);
		status->SetSubstepNumber(0, steprange[1]-steprange[0]+1);
	}
	else if(m_iswignerT){
		status->SetSubstepNumber(1, ngrids*m_np);
		status->SetSubstepNumber(0, steprange[1]-steprange[0]+1);
	}
	else{
		status->SetSubstepNumber(0, (2+jnf) *(steprange[1]-steprange[0]+1));
	}

	for(int next = steprange[0]; next <= steprange[1]; next++){
		f_ReadData(next);
		if(!m_iswigner){
			status->AdvanceStep(0);
		}
		if(jnf == 1){
			SetNearField(m_exporsteps[next], 1);
			if(!m_iswigner){
				status->AdvanceStep(0);
			}
		}
		if(m_iswignerX || m_iswignerY){
			f_GetWignerSpatial(m_exporsteps[next], m_nhpp, status, nrange, slicerange);
		}
		else if(m_iswignerT){
			f_GetWignerTemporal(jnf, m_exporsteps[next], m_nhpp, status, nrange, slicerange, avgslices, erange);
		}
		else{
			f_GetSpatialProfile(m_exporsteps[next], m_nhpp, jnf, m_exporsteps[next], nrange, slicerange);
		}
		status->AdvanceStep(0);

		int nsoffset = f_GetSliceOffset(m_exporsteps[next]);
		int m = next-steprange[0], lq;
		int *range = m_isppflux ? erange : slicerange;
		int ranges = (int)(m_isppflux ? earr.size() : sarr.size());

		// m_Epp[0~3:polarization][0~m_slices_total-1: slice(radiation) or 0~m_nfft_sp-1: energy][xyindex]
		// m_W[0 or slices][Wigner 2D Variable]
		if(m_iswignerT){  // (s, e, z)
			data[m][0] = m_W[0];
			data[m][0] *= Wcoef;
			continue;
		}
		else if(dimensions == 4){ // (x, y, s/e, z): power density, flux density or complex amplitude 
			for(int nq = range[0]; nq <= range[1]; nq++){
				int mq = nq-range[0];
				if(m_iswignerX || m_iswignerY){
					data[m*ranges+mq][0] = m_W[mq];
					data[m*ranges+mq][0] *= Wcoef;
					continue;
				}
				if(m_isppflux){
					lq = fft_index(nq, m_nfftsp, -1);
				}
				else{
					lq = nq+nsoffset;
				}
				for(int i = 0; i < nitems; i++){
					data[m*ranges+mq][i] = m_Epp[jxyindex[i]][lq];
				}
			}
		}
		else if(dimensions == 3){ // (x, y, z): energy density
			if(m_iswignerX || m_iswignerY){
				fill(data[m][0].begin(), data[m][0].end(), 0.0);
				for(int nq = range[0]; nq <= range[1]; nq++){
					int mq = nq-range[0];
					for(int ng = 0; ng < ngrids; ng++){
							data[m][0][ng] += m_W[mq][ng]*Wcoef;
					}
				}
				continue;
			}
			for(int i = 0; i < nitems; i++){
				data[m][i] = m_Epp[jxyindex[i]][0];
			}
		}
		else if(dimensions == 2){ // (s/e, z): power or flux
			for(int i = 0; i < nitems; i++){
				for(int nq = range[0]; nq <= range[1]; nq++){
					int mq = nq-range[0];
					if(m_isppflux){
						lq = fft_index(nq, m_nfftsp, -1);
					}
					else{
						lq = nq+nsoffset;
					}
					data[m][i][mq] = m_Epp[jxyindex[i]][lq][0];
				}
			}
		}
		else{ // (z): pulse energy
			for(int i = 0; i < nitems; i++){
				data[0][i][m] = m_Epp[jxyindex[i]][0][0];
			}
		}
	}
}

// private functions
void RadiationHandler::f_InitGaussianMode()
{
	for(int j = 0; j < 2; j++){
		m_bfg[j].resize(m_nhmax, 1);
	}
	for(int n = 0; n < m_totalsteps; n++){
		for(int j = 0; j < 3; j++){
			m_Gf[j].resize(m_nfft[0]);
			for(int nx = 0; nx < m_nfft[0]; nx++){
				m_Gf[j][nx].resize(m_nfft[1], 0.0);
			}
		}
	}
	m_gkappa.resize(m_nhmax);
	for(int nh = 0; nh < m_nhmax; nh++){
		m_gkappa[nh].resize(m_totalsteps);
	}
	for(int j = 0; j < 2; j++){
		m_bfsize[j].resize(m_nhmax);
		m_gn[j].resize(m_totalsteps);
		for(int nh = 0; nh < m_nhmax; nh++){
			m_bfsize[j][nh].resize(m_totalsteps);
		}
	}

	for(int np = 0; np < m_np; np++){
		m_Eaxis[np].resize(m_nhmax);
		m_eorg[np].resize(m_nhmax);
		m_etgt[np].resize(m_nhmax);
		for(int nh = 0; nh < m_nhmax; nh++){
			m_Eaxis[np][nh].resize(2*m_slices_total, 0.0);
			m_eorg[np][nh].resize(m_totalsteps);
			m_etgt[np][nh].resize(m_totalsteps);
			for(int n = 0; n < m_totalsteps; n++){
				m_eorg[np][nh][n] = new double[2*m_slices_total];
				m_etgt[np][nh][n] = new double[2*m_slices_total];
				for(int ns = 0; ns < m_slices_total; ns++){
					m_eorg[np][nh][n][2*ns] = m_eorg[np][nh][n][2*ns+1] = 0;
					m_etgt[np][nh][n][2*ns] = m_etgt[np][nh][n][2*ns+1] = 0;
				}
			}
		}
	}
	m_ewsbuf = new double[2*m_slices_total];

	for(int j = 0; j < 2; j++){
		m_pcoef[j].resize(m_totalsteps);
		m_pampl[j].resize(m_totalsteps);
		m_paeven[2*j].resize(m_totalsteps);
		m_paeven[2*j+1].resize(m_totalsteps);
	}

	m_GnAvg.resize(m_nhmax);
	for(int nh = 0; nh < m_nhmax; nh++){
		m_GnAvg[nh].resize(m_totalsteps);
		for(int n = 0; n < m_totalsteps; n++){
			m_GnAvg[nh][n].resize(2*m_nfft[0]*m_nfft[1]);
		}
	}

	for(int j = 0; j < 2; j++){
		m_Gxy[j].resize(2*m_nfft[j]);
	}
	m_assigned.resize(m_slices_total);
	for(int ns = 0; ns < m_slices_total; ns++){
		m_assigned[ns].resize(m_nfft[0]*m_nfft[1]);
	}
	m_mini.resize(m_nhmax, 0);
	m_Esec.resize(m_nhmax);

	m_sigh2seed = PI2/m_lambda1*m_sigmar*SQRT2;
	// RMS of seed radiation field is sigma*sqrt(2)
	m_sigh2seed *= m_sigh2seed;
}

void RadiationHandler::f_CyclicShift(int n)
{
	if(m_skipwave && !m_isGaussDebug){
		return;
	}

	int outslice, inslice;
	inslice = f_GetSliceOffset(n);
	outslice = inslice+m_slices;
	for(int np = 0; np < m_np; np++){
		for(int nh = 0; nh < m_nhmax; nh++){
			if(m_procs == 1){
				for(int nxy = 0; nxy < m_ngrids; nxy++){
					for(int j = 0; j < 2; j++){
						m_ws[np][nh][j][inslice*m_ngrids+nxy] = m_ws[np][nh][j][outslice*m_ngrids+nxy];
					}
				}
			}
			else{
				if(m_thread != nullptr){
					m_thread->SendRecv(
						m_ws[np][nh][0]+outslice*m_ngrids,
						m_ws[np][nh][0]+inslice*m_ngrids,
						m_ngrids, MPI_DOUBLE, m_procs-1, 0, m_rank);
				}
				else{
					if(m_rank == m_procs-1){
						MPI_Send(m_ws[np][nh][0]+outslice*m_ngrids, m_ngrids, MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
					}
					else if(m_rank == 0){
						MPI_Status status;
						MPI_Recv(m_ws[np][nh][0]+inslice*m_ngrids, m_ngrids, MPI_DOUBLE, m_procs-1, 0, MPI_COMM_WORLD, &status);
					}
					MPI_Barrier(MPI_COMM_WORLD);
				}
			}
		}
	}
}

int RadiationHandler::f_GetSliceOffset(int n)
{
	return m_steadystate ? 0 : m_totalsteps-n-1;
}

void RadiationHandler::f_LoadSimplexOutput(int nhtgt, PrintCalculationStatus *status)
{
	int nhspx = (int)floor(0.5+m_simlambda1/(m_lambda1/nhtgt));
	int nhmax = (int)floor(0.5+m_sxconf.GetPrm(SimCondLabel, maxharmonic_));
	if(nhmax < nhspx){ // no radiation source
		return;
	}

	PathHander datapath(m_sxconf.GetDataPath());
	string dataname = datapath.filename().string();
	datapath.replace_filename(dataname+"-"+to_string(nhspx+1));
	datapath.replace_extension(".fld");
	string flddata = datapath.string();
	fstream iofile;
	int iok = 0;
	if(m_rank == 0){
		iofile.open(flddata, ios::binary|ios::in);
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
		throw runtime_error("Failed to open the radiation data file.");
	}

	int step = (int)m_simexpsteps.size()-1+(int)floor(0.5+m_prm[SPXOut_][spxstep_]);
	int npspx;
	if(m_sxconf.GetSelection(UndLabel, utype_) == LinearUndLabel || m_sxconf.GetSelection(UndLabel, utype_) == HelicalUndLabel){
		npspx = 1;
	}
	else{
		npspx = 2;
	}

	int ndg = m_nfft[0]*m_nfft[1], nexport;
	int slices[2], nfft[2], index, norg[2];
	double ds[2], de[2], ep1[2], De, dk;
	vector<double> earr[2], Ea[2];
	FastFourierTransform *fft[2];

	slices[0] = (int)m_simspos.size();
	slices[1] = m_slices;
	if(slices[0] < 2){
		throw runtime_error("Too few slice data output.");
	}
	nexport = slices[0]*m_ngrids;
	ds[0] = (m_simspos.back()-m_simspos.front())/(slices[0]-1);
	ds[1] = m_lslice;
	ep1[0] = wave_length(m_simlambda1);
	ep1[1] = wave_length(m_lambda1);
	for(int j = 0; j < 2; j++){
		norg[j] = slices[j]/2;
		nfft[j] = fft_number(slices[j], 2);
		fft[j] = new FastFourierTransform(1, nfft[j]);
		de[j] = PLANCK/(ds[j]*nfft[j]/CC);
		earr[j].resize(nfft[j]+1);
		for(int n = -nfft[j]/2; n <= nfft[j]/2; n++){
			earr[j][n+nfft[j]/2] = de[j]*n;
			if(j == 1){
				earr[j][n+nfft[j]/2] += ep1[1]-ep1[0];
			}
		}
		Ea[j].resize(nfft[0]+1);
	}
	De = PLANCK/(ds[0]/CC); // energy range of the simplex output data
	dk = 1.0/(ds[1]*nfft[1]);
	float *ws = new float[nexport];

	vector<vector<double *>> wsvec[2];
	for(int j = 0; j < 2; j++){
		wsvec[j].resize(2);
		for(int np = 0; np < 2; np++){
			wsvec[j][np].resize(ndg);
			for(int ni = 0; ni < ndg; ni++){
				wsvec[j][np][ni] = new double[2*nfft[j]];
				for(int n = 0; n < 2*nfft[j]; n++){
					wsvec[j][np][ni][n] = 0;
				}
			}
		}
	}

	double sdelay, phi, csn[2];
	sdelay = m_simspos[norg[0]]-m_s[norg[1]]+m_prm[Seed_][timing_]*1e-15*CC;
	status->SetSubstepNumber(2, npspx*ndg);

	bool noshift = fabs(sdelay) < m_lambda1/4 && slices[0] == slices[1];

	iofile.seekg(step*nexport*npspx*sizeof(float), ios_base::beg);
	for(int np = 0; np < npspx && m_rank == 0; np++){
		iofile.read((char *)ws, nexport*sizeof(float));
		for(int ni = 0; ni < ndg; ni++){
			if(noshift){
				for(int ns = 0; ns < m_slices; ns++){
					wsvec[1][np][ni][2*ns] = ws[ns*2*ndg+2*ni];
					wsvec[1][np][ni][2*ns+1] = ws[ns*2*ndg+2*ni+1];
				}
				continue;
			}
			for(int ns = 0; ns < nfft[0]; ns++){
				index = fft_index(ns, nfft[0], 1)+norg[0];
				if(index < 0 || index >= slices[0]){
					wsvec[0][np][ni][2*ns] = wsvec[0][np][ni][2*ns+1] = 0;
				}
				else{
					wsvec[0][np][ni][2*ns] = ws[index*2*ndg+2*ni]*ds[0];
					wsvec[0][np][ni][2*ns+1] = ws[index*2*ndg+2*ni+1]*ds[0];
				}
			}
			fft[0]->DoFFT(wsvec[0][np][ni], -1);

			for(int n = -nfft[0]/2; n <= nfft[0]/2; n++){
				index = fft_index(n, nfft[0], -1);
				for(int j = 0; j < 2; j++){
					Ea[j][n+nfft[0]/2] = wsvec[0][np][ni][2*index+j];
				}
			}

			for(int ns = 0; ns < nfft[1] && np < m_np; ns++){
				index = fft_index(ns, nfft[1], 1)+nfft[1]/2;
				if(fabs(earr[1][index]) >= De/2){
					wsvec[1][np][ni][2*ns] = wsvec[1][np][ni][2*ns+1] = 0;
					continue;
				}
				for(int j = 0; j < 2; j++){
					wsvec[1][np][ni][2*ns+j] = dk*lagrange(earr[1][index], earr[0], Ea[j], true);
				}
				phi = -earr[1][index]*sdelay/PLANKCC;
				csn[0] = cos(phi);
				csn[1] = sin(phi);
				multiply_complex(&wsvec[1][np][ni][2*ns], &wsvec[1][np][ni][2*ns+1], csn);
			}

#ifdef _DEBUG
			if(!RadiationSPXRestore.empty() && ni == 0){
				ofstream debug_out(RadiationSPXRestore);
				vector<string> titles {"index", "ep0", "re0", "im0", "ep1", "re1", "im1"};
				vector<double> items(titles.size());
				PrintDebugItems(debug_out, titles);
				int nft = max(nfft[0], nfft[1]), nidx;
				for(int ns = -nft/2+1; ns <= nft/2; ns++){
					items[0] = ns;
					for(int j = 0; j < 2; j++){
						items[3*j+1] = ns*de[j];
						if(abs(ns) > nfft[j]/2){
							items[3*j+2] = items[3*j+3] = 0;
						}
						else{
							nidx = fft_index(ns, nfft[j], -1);
							if(j == 0){
								items[3*j+2] = wsvec[0][np][ni][2*nidx];
								items[3*j+3] = wsvec[0][np][ni][2*nidx+1];
							}
							else{
								items[3*j+1] += ep1[1]-ep1[0];
								items[3*j+2] = wsvec[j][np][ni][2*nidx]/dk;
								items[3*j+3] = wsvec[j][np][ni][2*nidx+1]/dk;
							}
						}
					}
					PrintDebugItems(debug_out, items);
				}
				debug_out.close();
			}
#endif
			fft[1]->DoFFT(wsvec[1][np][ni], 1);
#ifdef _DEBUG
			if(ni == 0 && !RadiationSPXRestoreTemp.empty()){
				ofstream debug_out(RadiationSPXRestoreTemp);
				vector<string> titles{"s0", "re0", "im0", "s1", "re1", "im1"};
				vector<double> items(titles.size());
				PrintDebugItems(debug_out, titles);
				for(int ns = 0; ns < slices[0]; ns++){
					items[0] = m_simspos[ns];
					items[1] = ws[ns*2*ndg+2*ni];
					items[2] = ws[ns*2*ndg+2*ni+1];
				
					items[3] = m_s[min(ns, slices[1]-1)];
					index= fft_index(min(ns, slices[1]-1)-norg[1], nfft[1], -1);
					items[4] = wsvec[1][np][ni][2*index];
					items[5] = wsvec[1][np][ni][2*index+1];
					PrintDebugItems(debug_out, items);
				}
				debug_out.close();
			}
#endif
			status->AdvanceStep(2);
		}
	}

	double phaseoffset = m_prm[Seed_][phase_]*DEGREE2RADIAN;
	csn[0] = cos(phaseoffset);
	csn[1] = sin(phaseoffset);

	int nsoffset = f_GetSliceOffset(-1);
	if(m_select[EBeam_][bmprofile_] == SimplexOutput){
		nsoffset += (int)floor(0.5+m_slippage/m_lslice); // slippage in the drift section
		nsoffset++; // advance one slice (field-data is stored in slices before slippage)
	}
	for(int np = 0; np < m_np; np++){
		for(int ns = 0; ns < m_slices; ns++){
			if(ns+nsoffset >= m_slices_total){
				continue;
			}
			if(noshift){
				index = ns;
			}
			else{
				index = fft_index(ns-norg[1], nfft[1], -1);
			}
			for(int nx = 0; nx < m_nfft[0] && m_rank == 0; nx++){
				for(int ny = 0; ny < m_nfft[1]; ny++){
					m_E[np][nhtgt][0][ns+nsoffset][nx][2*ny] = 
						wsvec[1][np][nx*m_nfft[1]+ny][2*index]*csn[0]-wsvec[1][np][nx*m_nfft[1]+ny][2*index+1]*csn[1];
					m_E[np][nhtgt][0][ns+nsoffset][nx][2*ny+1] =
						wsvec[1][np][nx*m_nfft[1]+ny][2*index]*csn[1]+wsvec[1][np][nx*m_nfft[1]+ny][2*index+1]*csn[0];
				}
			}
			if(m_procs > 1){
				if(m_thread != nullptr){
					m_thread->Bcast(m_ws[np][nhtgt][0]+(ns+nsoffset)*m_ngrids, m_ngrids, MPI_DOUBLE, 0, m_rank);
				}
				else{
					MPI_Bcast(m_ws[np][nhtgt][0]+(ns+nsoffset)*m_ngrids, m_ngrids, MPI_DOUBLE, 0, MPI_COMM_WORLD);
				}
			}
		}
	}

	delete[] ws;
	for(int j = 0; j < 2; j++){
		for(int np = 0; np < 2; np++){
			for(int n = 0; n < ndg; n++){
				delete[] wsvec[j][np][n];
			}
		}
	}
	for(int j = 0; j < 2; j++){
		delete fft[j];
	}
	if(m_rank == 0){
		iofile.close();
	}

	if(m_prm[SPXOut_][matching_] != 0){
		f_AdvanceDrift(m_prm[SPXOut_][matching_]);
	}
}

void RadiationHandler::f_SetChirpPulse(int iseed)
{
	int nfft = fft_number(m_slices_total, 2);
	double *ef = new double[2*nfft];
	double sigmasFL = CC*m_prm[Seed_][pulselen_]*1e-15/Sigma2FWHM; // FWHG (fs) -> sigma (m)
	FastFourierTransform fft(1, nfft);

	for(int n = 0; n < nfft; n++){
		double s = fft_index(n, nfft, 1)*m_lslice;
		double tex = s/sigmasFL;
		ef[2*n] = exp(-tex*tex/4);
		ef[2*n+1] = 0;
	}
	fft.DoFFT(ef);

	int igdd = iseed == 0 ? gdd_ : gdd2_;
	int itod = iseed == 0 ? tod_ : tod2_;
	int categ = iseed == 0 ? Seed_: Mbunch_;
	double gdd = m_prm[categ][igdd]*1e-30; // fs^2 -> s^2
	double tod = m_prm[categ][itod]*1e-45; // fs^3 -> s^3
	double dw = PI2/(nfft*m_lslice/CC);
	double csn[2], dummy;

	for(int n = 0; n < nfft; n++){
		double w = fft_index(n, nfft, 1)*dw;
		double w2 = w*w;
		double phase = -w2*(gdd/2+tod*w/6);
		csn[0] = cos(phase);
		csn[1] = sin(phase);
		ef[2*n] = ((dummy = ef[2*n])*csn[0]-ef[2*n+1]*csn[1])/nfft;
		ef[2*n+1] = (dummy*csn[1]+ef[2*n+1]*csn[0])/nfft;
	}

#ifdef _DEBUG
	if(m_rank == 0 && !RadiationChirpPulseF.empty()){
		ofstream debug_out;
		debug_out.open(RadiationChirpPulseF);
		vector<string> titles{"E", "real", "imag"};
		vector<double> items(titles.size());
		PrintDebugItems(debug_out, titles);
		for(int ns = -nfft/2; ns <= nfft/2; ns++){
			int index = fft_index(ns, nfft, -1);
			items[0] = ns*dw*PLANCK/PI2;
			items[1] = ef[2*index];
			items[2] = ef[2*index+1];
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif
	fft.DoFFT(ef, -1);
#ifdef _DEBUG
	if(m_rank == 0 && !RadiationChirpPulse.empty()){
		ofstream debug_out;
		debug_out.open(RadiationChirpPulse);
		vector<string> titles{"s", "real", "imag"};
		vector<double> items(titles.size());
		PrintDebugItems(debug_out, titles);
		for(int ns = -nfft/2; ns <= nfft/2; ns++){
			int index = fft_index(ns, nfft, -1);
			items[0] = ns*m_lslice;
			items[1] = ef[2*index];
			items[2] = ef[2*index+1];
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif

	vector<double> s, ea[2];
	s.resize(nfft+1);
	for(int j = 0; j < 2; j++){
		ea[j].resize(nfft+1);
	}

	double efamp = sqrt(hypotsq(ef[0], ef[1]));
	double phase = -atan2(ef[1], ef[0]);
	csn[0] = cos(phase)/efamp;
	csn[1] = sin(phase)/efamp;
	for(int n = -nfft/2; n <= nfft/2; n++){
		int idx = fft_index(n, nfft, -1);
		s[n+nfft/2] = n*m_lslice;
		ea[0][n+nfft/2] = ef[2*idx]*csn[0]-ef[2*idx+1]*csn[1];
		ea[1][n+nfft/2] = ef[2*idx]*csn[1]+ef[2*idx+1]*csn[0];
	}
	for(int j = 0; j < 2; j++){
		m_echirp[j].SetSpline(nfft+1, &s, &ea[j]);
	}

	delete[] ef;
}

void RadiationHandler::f_PrepareExternalSeed()
{
	for(int j = 0; j < 2; j++){
		m_E0s[j].resize(m_slices_total, 0.0);
		m_e0s[j].resize(m_slices_total, 0.0);
	}

	double sigmasFL = m_prm[Seed_][pulselen_]*1e-15/Sigma2FWHM; // FWHG (fs) -> sigma (s)
	double smin, tex;
	double Es = sqrt(m_prm[Seed_][pkpower_]*Z0VAC/4/PI)/m_sigmar;
	double Ea = Es*(4*PI*m_sigmar*m_sigmar);
	double phase;

	int kfin = (m_lasermod && m_bool[Mbunch_][wpulse_]) ? 2 : 1;
	for(int k = 0; k < kfin; k++){
		int categ = k == 0 ? Seed_: Mbunch_;
		int igdd = k == 0 ? gdd_ : gdd2_;
		int itiming = k == 0 ? timing_ : timing2_;
		int irelwavelen = k == 0 ? relwavelen_ : relwavelen2_;
		int iCEP = k == 0 ? CEP_ :CEP2_;

		double sigmas = sigmasFL;
		double aG = 0;
		if(m_select[Seed_][seedprofile_] == ChirpedPulse){
			double G = m_prm[categ][igdd]*1e-30; // fs^2 -> s^2
			double pstretch = sqrt(hypotsq(1.0, G/2.0/sigmasFL/sigmasFL));
			sigmas *= pstretch;
			aG = 0.5/pstretch/sigmasFL/sigmasFL/CC;
			aG = G/2.0*aG*aG;
		}
		sigmas *= CC; // s -> m

		double soffset = m_prm[categ][itiming]*1e-15*CC; // fs -> m
		soffset = floor(soffset/m_lambda1+0.5)*m_lambda1; // timing should be discretized (s = n*m_lambda1)
		double dks = -PI2*m_prm[categ][irelwavelen]/(m_lambda1*(1+m_prm[categ][irelwavelen]));
		if(k == 0){
			m_nsorg = -1;
		}
		for(int ns = 0; ns < m_slices_total; ns++){
			if(m_steadystate){
				tex = 0;
				phase = 0;
			}
			else{
				double spos = m_s[0]+(ns-m_totalsteps)*m_lslice-soffset;
				if(k == 0 && (m_nsorg < 0 || smin > fabs(spos))){
					smin = fabs(spos);
					m_nsorg = ns;
				}
				tex = spos/sigmas/2;
				tex *= tex;
				if(tex > MAXIMUM_EXPONENT){
					continue;
				}
				phase = dks*spos+m_prm[categ][iCEP]*DEGREE2RADIAN+aG*spos*spos;
			}

			double E0 = Es*exp(-tex);
			m_E0s[0][ns] += E0*cos(phase);
			m_E0s[1][ns] += E0*sin(phase);

			E0 = Ea*exp(-tex);
			m_e0s[0][ns] += E0*cos(phase);
			m_e0s[1][ns] += E0*sin(phase);
		}
	}

#ifdef _DEBUG
	if(m_rank == 0 && !RadiationSeedTemp.empty()){
		ofstream debug_out;
		debug_out.open(RadiationSeedTemp);
		vector<string> titles{"s", "Real", "Imaginary"};
		vector<double> items(titles.size());
		PrintDebugItems(debug_out, titles);
		for(int ns = 0; ns < m_slices_total; ns++){
			items[0] = m_s[0]+(ns-m_totalsteps)*m_lslice;
			items[1] = m_E0s[0][ns];
			items[2] = m_E0s[1][ns];
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif

	m_Eseed.resize(m_nfft[0]);
	for(int nx = 0; nx < m_nfft[0]; nx++){
		m_Eseed[nx].resize(m_nfft[1]*2);
	}
	m_z0 = 4*PI*m_sigmar*m_sigmar/m_lambda_s;
	m_Zw = m_prm[Seed_][waistpos_];
}

void RadiationHandler::f_PrepareExternalSeedSpl()
{
	for(int j = 0; j < 2; j++){
		m_E0s[j].resize(m_slices_total);
		m_e0s[j].resize(m_slices_total);
		fill(m_E0s[j].begin(), m_E0s[j].end(), 0);
		fill(m_e0s[j].begin(), m_e0s[j].end(), 0);
	}

	double smin;
	double Es = sqrt(m_prm[Seed_][pkpower_]*Z0VAC/4/PI)/m_sigmar;
	double Ea = Es*(4*PI*m_sigmar*m_sigmar);
	double phase;

	int kfin = (m_lasermod && m_bool[Mbunch_][wpulse_]) ? 2 : 1;
	for(int k = 0; k < kfin; k++){
		int categ = k == 0 ? Seed_: Mbunch_;
		int igdd = k == 0 ? gdd_ : gdd2_;
		int itiming = k == 0 ? timing_ : timing2_;
		int irelwavelen = k == 0 ? relwavelen_ : relwavelen2_;
		int iCEP = k == 0 ? CEP_ :CEP2_;

		f_SetChirpPulse(k);

		double soffset = m_prm[categ][itiming]*1e-15*CC; // fs -> m
		double dks = -PI2*m_prm[categ][irelwavelen]/(m_lambda1*(1+m_prm[categ][irelwavelen]));
		double ea[2], csn[2];
		if(k == 0){
			m_nsorg = -1;
		}
		for(int ns = 0; ns < m_slices_total; ns++){
			if(m_steadystate){
				m_E0s[0][ns] += Es;
				m_e0s[0][ns] += Ea;
			}
			else{
				double spos = m_s[0]+(ns-m_totalsteps)*m_lslice-soffset;
				if(k == 0 && (m_nsorg < 0 || smin > fabs(spos))){
					smin = fabs(spos);
					m_nsorg = ns;
				}
				phase = dks*spos+m_prm[categ][iCEP]*DEGREE2RADIAN;
				csn[0] = cos(phase);
				csn[1] = sin(phase);
				for(int j = 0; j < 2; j++){
					ea[j] = m_echirp[j].GetValue(spos);
				}
				multiply_complex(ea, csn);
				for(int j = 0; j < 2; j++){
					m_E0s[j][ns] += Es*ea[j];
					m_e0s[j][ns] += Ea*ea[j];
				}
			}
		}
	}

#ifdef _DEBUG
	if(m_rank == 0 && !RadiationSeedTempSpl.empty()){
		ofstream debug_out;
		debug_out.open(RadiationSeedTempSpl);
		vector<string> titles{"s", "Real", "Imaginary"};
		vector<double> items(titles.size());
		PrintDebugItems(debug_out, titles);
		for(int ns = 0; ns < m_slices_total; ns++){
			items[0] = m_s[0]+(ns-m_totalsteps)*m_lslice;
			items[1] = m_E0s[0][ns];
			items[2] = m_E0s[1][ns];
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif


	m_Eseed.resize(m_nfft[0]);
	for(int nx = 0; nx < m_nfft[0]; nx++){
		m_Eseed[nx].resize(m_nfft[1]*2);
	}
	m_z0 = 4*PI*m_sigmar*m_sigmar/m_lambda_s;
	m_Zw = m_prm[Seed_][waistpos_];
}

void RadiationHandler::f_AdvanceDrift(double L)
{
	vector<vector<vector<double>>> phase;
	f_SetPhase(L, &phase);

	for(int nh = 0; nh < m_nhmax; nh++){
		double temp;
		for(int ns = m_sranges[0]; ns <= m_sranges[1]; ns++){
			if(ns < 0 || ns >= m_slices_total){
				continue;
			}
			for(int np = 0; np < m_np; np++){
				double **E = m_E[np][nh][0][ns];
				for(int nx = 0; nx < m_nfft[0]; nx++){
					for(int ny = 0; ny < m_nfft[1]; ny++){
						E[nx][2*ny] =
							(temp = E[nx][2*ny])*phase[nh][nx][2*ny]-E[nx][2*ny+1]*phase[nh][nx][2*ny+1];
						E[nx][2*ny+1] =
							temp*phase[nh][nx][2*ny+1]+E[nx][2*ny+1]*phase[nh][nx][2*ny];
					}
				}
			}
		}
	}
}

void RadiationHandler::f_SetPhase(double L, vector<vector<vector<double>>> *phase)
{
	double kxy[2], phs;
	phase->resize(m_nhmax);
	for(int nh = 0; nh < m_nhmax; nh++){
		double kac = m_lambda_s*L/(nh+1)/PI2/2;
		(*phase)[nh].resize(m_nfft[0]);
		for(int nx = 0; nx < m_nfft[0]; nx++){
			kxy[0] = m_dkxy[0]*fft_index(nx, m_nfft[0], 1);
			(*phase)[nh][nx].resize(2*m_nfft[1]);
			for(int ny = 0; ny < m_nfft[1]; ny++){
				kxy[1] = m_dkxy[1]*fft_index(ny, m_nfft[1], 1);
				phs = -hypotsq(kxy[0], kxy[1])*kac;
				(*phase)[nh][nx][2*ny] = cos(phs);
				(*phase)[nh][nx][2*ny+1] = sin(phs);
			}
		}
	}
}

void RadiationHandler::f_SetSeedField(int n)
{
	if(!m_exseed){
		return;
	}

	double xy[2], r2, tex, phase;
	double zh = ((n<0?0:m_z[n])-m_Zw)/m_z0;
	double z_1 = 1+zh*zh;
	double phc = PI*zh/m_lambda_s/m_z0/z_1;

	for(int nx = 0; nx < m_nfft[0]; nx++){
		xy[0] = m_dxy[0]*fft_index(nx, m_nfft[0], 1);
		for(int ny = 0; ny < m_nfft[1]; ny++){
			xy[1] = m_dxy[1]*fft_index(ny, m_nfft[1], 1);
			r2 = hypotsq(xy[0], xy[1]);
			tex = r2/4/m_sigmar/m_sigmar/z_1;
			if(tex > MAXIMUM_EXPONENT){
				m_Eseed[nx][2*ny] = m_Eseed[nx][2*ny+1] = 0;
				continue;
			}
			phase = -atan(zh)+phc*r2;
			m_Eseed[nx][2*ny] = exp(-tex)/sqrt(z_1);
			m_Eseed[nx][2*ny+1] = m_Eseed[nx][2*ny]*sin(phase);
			m_Eseed[nx][2*ny] *= cos(phase);
		}
	}
}

void RadiationHandler::f_WriteData(int n)
{
	int nsoffset = f_GetSliceOffset(n);
	int ndg = m_nfft[0]*2*m_nfft[1];
	for(int nh = 0; nh < m_nhmax; nh++){
		if(m_procs > 1){
			for(int np = 0; np < m_np; np++){
				for(int ns = 0; ns < m_slices_total; ns++){
					if(m_rank_admin[ns] < 0){
						continue;
					}
					if(m_thread != nullptr){
						m_thread->Bcast(m_ws[np][nh][0]+ns*m_ngrids, m_ngrids, MPI_DOUBLE, m_rank_admin[ns], m_rank);
					}
					else{
						MPI_Bcast(m_ws[np][nh][0]+ns*m_ngrids, m_ngrids, MPI_DOUBLE, m_rank_admin[ns], MPI_COMM_WORLD);
					}
				}
			}
		}
		for(int np = 0; np < m_np && m_rank == 0; np++){
			for(int nq = 0; nq < m_slices; nq++){
				int ns = nq+nsoffset+1;
				for(int ni = 0; ni < ndg; ni++){
					m_wsexport[nq*ndg+ni] = (float)m_ws[np][nh][0][ns*ndg+ni];
				}
			}
			m_iofs[nh].write((char *)m_wsexport, m_nexport*sizeof(float));
		}
		MPI_Barrier(MPI_COMM_WORLD);
	}
}

void RadiationHandler::f_ReadData(int expstep)
{
	int nsoffset = f_GetSliceOffset(m_exporsteps[expstep]);
	int ndg = m_nfft[0]*2*m_nfft[1];
	
	m_iofs[m_nhpp].seekg(expstep*m_nexport*m_np*sizeof(float), ios_base::beg);
	for(int np = 0; np < m_np && m_rank == 0; np++){
		m_iofs[m_nhpp].read((char *)m_wsexport, m_nexport*sizeof(float));
		for(int ns = 0; ns < m_slices_total; ns++){
			int nq = ns-nsoffset;
			for(int ni = 0; ni < ndg; ni++){
				if(nq >= 0 && nq < m_slices){
					m_ws[np][m_nhpp][0][ns*ndg+ni] = m_wsexport[nq*ndg+ni];
				}
				else{
					m_ws[np][m_nhpp][0][ns*ndg+ni] = 0;
				}
			}
		}
	}
}

void RadiationHandler::f_GetTemporal(int n, int nh, int curridx)
{
	int nsoffset = f_GetSliceOffset(n);
	for(int nq = 0; nq < m_slices; nq++){
		int ns = nq+nsoffset+1;
		m_Pexprt[curridx][nh][nq] = m_Pinst[nh][n][ns];
		// -(n+1): slippage by slice/step
		if(m_skipwave && m_exseed){
			double seedP = PI*hypotsq(m_e0s[0][ns], m_e0s[1][ns])/m_sigh2seed*m_E2pd[0][0]*1e6;
			m_Pexprt[curridx][nh][nq] += seedP;
		}
		m_Pexprt[curridx][nh][nq] /= 1e9; // W -> GW
	}
}

void RadiationHandler::f_BcastField(int nh, int j)
{
	if(m_procs > 1){
		for(int ns = 0; ns < m_slices_total; ns++){
			if(m_rank_admin[ns] < 0){
				continue;
			}
			for(int np = 0; np < m_np; np++){
				if(m_thread != nullptr){
					m_thread->Bcast(m_ws[np][nh][j]+ns*m_ngrids, m_ngrids, MPI_DOUBLE, m_rank_admin[ns], m_rank);
				}
				else{
					MPI_Bcast(m_ws[np][nh][j]+ns*m_ngrids, m_ngrids, MPI_DOUBLE, m_rank_admin[ns], MPI_COMM_WORLD);
				}
			}
		}
	}
}

void RadiationHandler::f_GetSpectrum(int n, int nh, int j, int curridx)
{
	int nsoffset = f_GetSliceOffset(n);
	double Exy[4] = {0, 0, 0, 0};

	fill(m_Flux[curridx][nh].begin(), m_Flux[curridx][nh].end(), 0.0);

	f_BcastField(nh, j);

	for(int nx = 0; nx < m_nfft[0]; nx++){
		if(m_rank != nx%m_procs){
			continue;
		}
		for(int ny = 0; ny < m_nfft[1]; ny++){
			for(int np = 0; np < m_np; np++){
				for(int ns = 0; ns < m_nfftsp; ns++){
					int nq = ns-nsoffset;
					if(nq < 0 || nq >= m_slices || m_rank_admin[ns] < 0){
						m_wssp[np][2*ns] = m_wssp[np][2*ns+1] = 0;
					}
					else{
						m_wssp[np][2*ns] = m_E[np][nh][j][ns][nx][2*ny];
						m_wssp[np][2*ns+1] = m_E[np][nh][j][ns][nx][2*ny+1];
					}
				}
				m_tfft->DoFFT(m_wssp[np], -1); // do fft by time, not by s (bunch position)
			}
			for(int ne = -m_nfftsp/2; ne <= m_nfftsp/2; ne++){
				int index = fft_index(ne, m_nfftsp, -1);
				for(int np = 0; np < m_np; np++){
					Exy[2*np] = m_wssp[np][2*index];
					Exy[2*np+1] = m_wssp[np][2*index+1];
				}
				stokes(Exy, m_np);
				m_Flux[curridx][nh][ne+m_nfftsp/2] += Exy[0];
			}
		}
	}
	if(m_procs > 1){
		for(int ne = 0; ne <= m_nfftsp; ne++){
			m_wssp[0][ne] = m_Flux[curridx][nh][ne];
		}
		if(m_thread != nullptr){
			m_thread->Allreduce(m_wssp[0], m_wssp[1], m_nfftsp+1, MPI_DOUBLE, MPI_SUM, m_rank);
		}
		else{
			MPI_Allreduce(m_wssp[0], m_wssp[1], m_nfftsp+1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
		}
		for(int ne = 0; ne <= m_nfftsp; ne++){
			m_Flux[curridx][nh][ne] = m_wssp[1][ne];
		}
	}
	if(j > 0){ // near field
		m_Flux[curridx][nh] *= m_E2f[j][nh]*1e6*m_dxy[0]*m_dxy[1];
	}
	else{
		double fnh = nh+1;
		m_Flux[curridx][nh] *= m_E2f[j][nh]*1e6*(m_qxy[0]/fnh)*(m_qxy[1]/fnh);
	}
	if(m_bool[DataDump_][spectral_] && m_isGauss){
		m_Flux[curridx][nh] += m_Fsr[nh];
	}
}

double RadiationHandler::f_GetPeakDens(double kL, int n, int nh, int *srange, string dfilename)
{
	int sini = 0, sfin = m_slices-1;
	if(srange != nullptr){
		sini = srange[0];
		sfin = srange[1];
	}
	int nsoffset = f_GetSliceOffset(n);
	double kxy[2], csn[2], phase, Eamp[2], pk = 0, pktot;
	double **Ep;
	for(int ns = 0; ns < m_slices_total; ns++){
		if(m_rank != m_rank_admin[ns]){
			continue;
		}
		int nq = ns-nsoffset;
		if(nq < 0|| nq > sfin){
			continue;
		}
		for(int np = 0; np < m_np; np++){
			Ep = m_E[np][nh][0][ns];
			Eamp[0] = Eamp[1] = 0;
			for(int nx = 0; nx < m_nfft[0]; nx++){
				kxy[0] = fft_index(nx, m_nfft[0], 1)*m_dkxy[0];
				for(int ny = 0; ny < m_nfft[1]; ny++){
					kxy[1] = fft_index(ny, m_nfft[1], 1)*m_dkxy[1];
					phase = kL/2*hypotsq(kxy[0], kxy[1]);
					csn[0] = cos(phase);
					csn[1] = sin(phase);
					Eamp[0] += Ep[nx][2*ny]*csn[0]-Ep[nx][2*ny+1]*csn[1];
					Eamp[1] += Ep[nx][2*ny]*csn[1]+Ep[nx][2*ny+1]*csn[0];
				}
			}
			pk += hypotsq(Eamp[0], Eamp[1]);
		}
	}
	if(m_procs > 1){
		if(m_thread != nullptr){
			m_thread->Allreduce(&pk, &pktot, 1, MPI_DOUBLE, MPI_SUM, m_rank);
		}
		else{
			MPI_Allreduce(&pk, &pktot, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
			MPI_Barrier(MPI_COMM_WORLD);
		}
	}
	else{
		pktot = pk;
	}
	return pktot*pktot;
}

double RadiationHandler::f_GetFocalIntensity(int n, int nh, int *srange)
{
	double pcurr, pmax, eps = 0.5, Lr = 0.5, dL = m_zstep;
	double kwave = PI2/m_lambda1*(nh+1);

#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(2);
	if(!RadiationCurvatureS.empty()){
		vector<double> items(2);
		if(m_rank == 0){
			debug_out.open(RadiationCurvatureS);
			vector<string> titles{"L", "peak"};
			PrintDebugItems(debug_out, titles);
		}
	}
#endif
	
	pmax = f_GetPeakDens(0, n, nh, srange);
	double p0 = pmax;
	for(int j = 1; j >= -1; j -= 2){
		Lr = j*dL;
		do{
			pcurr = f_GetPeakDens(Lr/kwave, n, nh, srange);
#ifdef _DEBUG
			if(!RadiationCurvatureS.empty() && m_rank == 0){
				items[0] = Lr;
				items[1] = pcurr;
				PrintDebugItems(debug_out, items);
			}
#endif
			if(pcurr > pmax){
				pmax = pcurr;
			}
			Lr += j*dL;
		} while(pcurr > pmax*eps);
	}
	
#ifdef _DEBUG
	if(!RadiationCurvatureS.empty() && m_rank == 0){
#ifdef _DEBUGINF
		cout << endl << "foc.int = " << pmax/p0 << endl;
#endif
		debug_out.close();
	}
#endif

	return pmax/p0;
}

void RadiationHandler::f_GetSeedProf(int n, double seedp[])
{
	seedp[0] = PI2*m_sigmar/m_lambda_s;
	seedp[0] *= seedp[0];
	seedp[1] = -PI/m_lambda_s*(m_z[n]-m_Zw);
}

void RadiationHandler::f_GetWignerSpatial(int n, int nh, 
	PrintCalculationStatus *status, int *nrange, int *srange)
{
	bool debug = false;

	bool seedon = nh == 0 && m_exseed;
	double seedp[2], thetasq, tex, phase, csn[2];
	int colrange[2], arange[2];
	if(seedon){
		f_GetSeedProf(n, seedp);
	}

	int jxy = m_iswignerX ? 0 : 1;
	colrange[0] = m_nfft[jxy]/2-nrange[1];
	colrange[1] = m_nfft[jxy]/2+nrange[1];
	arange[0] = -nrange[0];
	arange[1] = nrange[0];

	for(int np = 0; np < m_np; np++){
		for(int nq = srange[0]; nq <= srange[1]; nq++){
			int ns = f_GetSliceOffset(n)+nq;
			for(int nx = -m_nfft[0]/2; nx <= m_nfft[0]/2; nx++){
				int ix = nx+m_nfft[0]/2;
				int jx = fft_index(nx, m_nfft[0], -1);
				for(int ny = -m_nfft[1]/2; ny <= m_nfft[1]/2; ny++){
					int iy = ny+m_nfft[1]/2;
					int jy = fft_index(ny, m_nfft[1], -1);
					int index = ix*(m_nfft[1]+1)+iy;
					m_wsW[2*index  ] = m_E[np][nh][0][ns][jx][2*jy];
					m_wsW[2*index+1] = m_E[np][nh][0][ns][jx][2*jy+1];
					if(seedon && np == 0){
						thetasq = hypotsq(nx*m_qxy[0], ny*m_qxy[1]);
						tex = seedp[0]*thetasq;
						phase = seedp[1]*thetasq;
						if(tex < MAXIMUM_EXPONENT){
							csn[0] = csn[1] = exp(-tex);
							csn[0] *= cos(phase);
							csn[1] *= sin(phase);
						}
						else{
							csn[0] = csn[1] = 0;
						}
						m_wsW[2*index  ] += m_e0s[0][ns]*csn[0]-m_e0s[1][ns]*csn[1];
						m_wsW[2*index+1] += m_e0s[0][ns]*csn[1]+m_e0s[1][ns]*csn[0];
					}
				}
			}
#ifdef _DEBUG
			debug = nq == m_slices/2;
#endif
			m_wigner.AssignData(m_wsW, m_nfft[jxy]+1, -1, m_iswignerY);
			m_wigner.GetWigner(colrange, arange, &m_Wtmp[0], true, 0, debug);
			if(np == 0){
				m_W[nq-srange[0]] = m_Wtmp[0];
			}
			else{
				m_W[nq-srange[0]] += m_Wtmp[0];
			}
			status->AdvanceStep(1);
		}
	}
}

void RadiationHandler::f_GetWignerTemporal(int jnf, int n, int nh, 
	PrintCalculationStatus *status, int *nrange, int *sranger, int avgslices, int *erange)
{
	bool seedon = nh == 0 && m_exseed && jnf == 0;
	double seedp[2], thetasq, tex, phase, csn[2];
	if(seedon){
		f_GetSeedProf(n, seedp);
	}

	int srange[2];
	srange[0] = sranger[0]-avgslices;
	srange[1] = sranger[1]+avgslices;

	int jxy = m_iswignerX ? 0 : 1;

	int avgenergy = (int)floor(m_array[PostP_][smoothing_][1]+0.5);

	fill(m_Wtmp[0].begin(), m_Wtmp[0].end(), 0.0);
	for(int np = 0; np < m_np; np++){
		for(int nx = -nrange[0]; nx <= nrange[0]; nx++){
			int ix = nx+m_nfft[0]/2;
			int jx = fft_index(nx, m_nfft[0], -1);
			for(int ny = -nrange[1]; ny <= nrange[1]; ny++){
				int iy = ny+m_nfft[1]/2;
				int jy = fft_index(ny, m_nfft[1], -1);
				for(int nq = 0; nq < m_slices; nq++){
					int ns = nq+f_GetSliceOffset(n);
					m_wsW[2*nq] = m_E[np][nh][jnf][ns][jx][2*jy];
					m_wsW[2*nq+1] = m_E[np][nh][jnf][ns][jx][2*jy+1];
					if(seedon && np == 0){
						thetasq = hypotsq(nx*m_qxy[0], ny*m_qxy[1]);
						tex = seedp[0]*thetasq;
						phase = seedp[1]*thetasq;
						if(tex < MAXIMUM_EXPONENT){
							csn[0] = csn[1] = exp(-tex);
							csn[0] *= cos(phase);
							csn[1] *= sin(phase);
						}
						else{
							csn[0] = csn[1] = 0;
						}
						m_wsW[2*nq] += m_e0s[0][ns]*csn[0]-m_e0s[1][ns]*csn[1];
						m_wsW[2*nq+1] += m_e0s[0][ns]*csn[1]+m_e0s[1][ns]*csn[0];
					}
				}
				m_wigner.AssignData(m_wsW, m_slices, 1, false);
				m_wigner.GetWigner(srange, erange, &m_Wtmp[1], false, avgenergy, nx == 0 && ny == 0);
				m_Wtmp[0] += m_Wtmp[1];
				status->AdvanceStep(1);
			}
		}
	}
	if(avgslices == 0){
		m_W[0] = m_Wtmp[0];
		return;
	}

	int sranges = srange[1]-srange[0]+1;
	int srangesr = sranger[1]-sranger[0]+1;
	int nfft = fft_number(sranges, 2);
	double *data = new double[nfft];
	double cutoff = 1.0/m_array[PostP_][smoothing_][0];
	FastFourierTransform fft(1, nfft);
	for(int ne = erange[0]; ne <= erange[1]; ne++){
		for(int ns = 0; ns < nfft; ns++){
			if(ns >= sranges){
				data[ns] = 0;
				continue;
			}
			int index = sranges*(ne-erange[0])+ns;
			data[ns] = m_Wtmp[0][index];
		}
		fft.DoFFTFilter(data, cutoff, true);
		for(int nsr = 0; nsr < srangesr; nsr++){
			int indexr = srangesr*(ne-erange[0])+nsr;
			m_W[0][indexr] = data[nsr+avgslices];
		}
	}
}

void RadiationHandler::f_GetSpatialProfile(int n, int nh, int jnf, int curridx, int *nrange, int *srange)
{
	double seedp[2], csn[2], thetasq, tex, phase, Eseed[2] = {0, 0};
	bool seedon = jnf == 0 && nh == 0 && m_exseed;
	if(seedon){
		f_GetSeedProf(n, seedp);
	}
	int ixy[2], nxy[2], index, ins, iindex;
	int nf[2] = {m_nfft[0]/2, m_nfft[1]/2};
	if(nrange != nullptr){
		for(int i = 0; i < 2; i++){
			nf[i] = min(nf[i], nrange[i]);
		}
	}

	double Exy[4] = {0, 0, 0, 0};
	vector<double> s(4);
	if(m_ispostproc){
		for(int i = 0; i < 4; i++){
			for(int ns = 0; ns < m_nfftsp; ns++){
				fill(m_Epp[i][ns].begin(), m_Epp[i][ns].end(), 0.0);
			}
		}
	}
	else{
		fill(m_Pd[jnf][curridx][nh].begin(), m_Pd[jnf][curridx][nh].end(), 0);
	}

	double **Ep[2];
	int nsoffset = f_GetSliceOffset(n);
	int npn = m_np > 1 ? 4 : (m_isppamp ? 2 : 1), nxyfin;
	int sini = 0, sfin = m_slices-1;
	if(srange != nullptr){
		sini = srange[0];
		sfin = srange[1];
	}

	for(int ns = 0; ns < m_slices_total; ns++){
		if(m_rank != m_rank_admin[ns]){
			continue;
		}
		int nq = ns-nsoffset;
		if(nq < sini || nq > sfin){
			continue;
		}
		for(int np = 0; np < m_np; np++){
			Ep[np] = m_E[np][nh][jnf][ns];
		}
		for(int nx = -nf[0]; nx <= nf[0]; nx++){
			nxy[0] = nx+nf[0];
			ixy[0] = fft_index(nx, m_nfft[0], -1);
			for(int ny = -nf[1]; ny <= nf[1]; ny++){
				nxy[1] = ny+nf[1];
				ixy[1] = fft_index(ny, m_nfft[1], -1);
				index = nxy[1]*(2*nf[0]+1)+nxy[0];
				if(seedon){
					thetasq = hypotsq(nx*m_qxy[0], ny*m_qxy[1]);
					tex = seedp[0]*thetasq;
					phase = seedp[1]*thetasq;
					if(tex < MAXIMUM_EXPONENT){
						csn[0] = csn[1] = exp(-tex);
						csn[0] *= cos(phase);
						csn[1] *= sin(phase);
					}
					else{
						csn[0] = csn[1] = 0;
					}
				}
				for(int np = 0; np < m_np; np++){
					if(seedon && np == 0){
						Eseed[0] = m_e0s[0][ns]*csn[0]-m_e0s[1][ns]*csn[1];
						Eseed[1] = m_e0s[0][ns]*csn[1]+m_e0s[1][ns]*csn[0];
					}
					else{
						Eseed[0] = Eseed[1] = 0;
					}
					if(m_ispostproc){
						Exy[2*np] = Ep[np][ixy[0]][2*ixy[1]]+Eseed[0];
						Exy[2*np+1] = Ep[np][ixy[0]][2*ixy[1]+1]+Eseed[1];
					}
					else{
						m_Pd[jnf][curridx][nh][index] +=
							hypotsq(Ep[np][ixy[0]][2*ixy[1]]+Eseed[0],
								Ep[np][ixy[0]][2*ixy[1]+1]+Eseed[1]);
					}
				}
				if(m_ispostproc){
					if(m_ispppower){
						stokes(Exy, m_np);
					}
					if(m_isppflux){
						ins = ns;
						iindex = index;
					}
					else{
						ins = m_isppalongs ? 0 : ns;
						iindex = m_isppoxy ? 0 : index;
					}
					for(int i = 0; i < 4; i++){
						m_Epp[i][ins][iindex] += Exy[i];
					}
				}
			}
		}
	}

	if(m_ispostproc){
		nxyfin = (2*nf[0]+1)*(2*nf[1]+1)-1;
	}

	if(m_isppflux){
		for(int nxy = 0; nxy <= nxyfin; nxy++){
			for(int np = 0; np < m_np; np++){
				for(int ns = 0; ns < m_nfftsp; ns++){
					int nq = ns-nsoffset;
					if(nq < 0 || nq >= m_slices){
						m_wssp[np][2*ns] = m_wssp[np][2*ns+1] = 0;
					}
					else{
						m_wssp[np][2*ns] = m_Epp[2*np][ns][nxy];
						m_wssp[np][2*ns+1] = m_Epp[2*np+1][ns][nxy];
					}
				}
				m_tfft->DoFFT(m_wssp[np], -1); // do fft by time, not by s (bunch position)
			}
			for(int ne = 0; ne < m_nfftsp; ne++){
				for(int np = 0; np < m_np; np++){
					Exy[2*np] = m_wssp[np][2*ne];
					Exy[2*np+1] = m_wssp[np][2*ne+1];
				}
				stokes(Exy, m_np);
				for(int i = 0; i < npn; i++){
					m_Epp[i][ne][nxy] = Exy[i];
				}
			}
		}
	}

	if(m_ispppower){
		int nsfin = m_slices_total-1;
		double coef = m_E2pd[jnf][nh]*1e-9; // W -> GW
		if(m_isppoxy){
			nxyfin = 0;
			coef = m_E2P[jnf][nh]*1e-9; // W -> GW
		}
		if(m_isppalongs){
			nsfin = 0;
			coef *= 1e9*m_dTslice; // GW -> W -> J
		}
		for(int nxy = 0; nxy <= nxyfin; nxy++){
			for(int ns = 0; ns <= nsfin; ns++){
				for(int i = 0; i < npn; i++){
					m_Epp[i][ns][nxy] *= coef;
				}
			}
		}
	}
	else if(m_isppflux){
		double coef = m_E2f[jnf][nh];
		double fnh = nh+1;
		if(m_isppoxy){
			for(int nxy = 1; nxy <= nxyfin; nxy++){
				for(int ns = 0; ns < m_nfftsp; ns++){
					for(int i = 0; i < npn; i++){
						m_Epp[i][ns][0] += m_Epp[i][ns][nxy];
					}
				}
			}
			nxyfin = 0;
			if(jnf == 1){
				coef *= 1e6*m_dxy[0]*m_dxy[1];
			}
			else{
				coef *= 1e6*(m_qxy[0]/fnh)*(m_qxy[1]/fnh);
			}
		}
		for(int nxy = 0; nxy <= nxyfin; nxy++){
			for(int i = 0; i < npn; i++){
				for(int ns = 0; ns < m_nfftsp; ns++){
					m_Epp[i][ns][nxy] *= coef;
				}
			}
		}
	}

	if(m_procs > 1){
		int nfn = (2*nf[0]+1)*(2*nf[1]+1);
		for(int m = 0; m < nfn; m++){
			m_wspd[0][m] = m_Pd[jnf][curridx][nh][m];
		}
		if(m_thread != nullptr){
			m_thread->Allreduce(m_wspd[0], m_wspd[1], nfn, MPI_DOUBLE, MPI_SUM, m_rank);
		}
		else{
			MPI_Allreduce(m_wspd[0], m_wspd[1], nfn, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
		}
		for(int m = 0; m < nfn; m++){
			m_Pd[jnf][curridx][nh][m] = m_wspd[1][m];
		}
	}
	m_Pd[jnf][curridx][nh] *= m_E2pd[jnf][nh]*m_dTslice;

	if(m_isGauss && !m_ispostproc){
		for(int nx = -nf[0]; nx <= nf[0]; nx++){
			nxy[0] = nx+nf[0];
			ixy[0] = fft_index(nx, m_nfft[0], -1);
			for(int ny = -nf[1]; ny <= nf[1]; ny++){
				nxy[1] = ny+nf[1];
				ixy[1] = fft_index(ny, m_nfft[1], -1);
				index = nxy[1]*(2*nf[0]+1)+nxy[0];
				m_Pd[jnf][curridx][nh][index] += m_psr[jnf][nh][ixy[0]*m_nfft[1]+ixy[1]];
			}
		}
	}
}

void RadiationHandler::f_ExportField(
	bool isbunch, bool isnear, int type, int ns, int nh, string dataname)
{
	if(m_steadystate){
		ns = 0;
	}
	ns = min(ns, m_slices_total-1);

	int rank = m_rank_admin[ns];
	if(rank < 0){
		return;
	}
	if(m_rank != rank){
		return;
	}

	ofstream debug_out(dataname);
	vector<string> titles;
	double *dxy;
	if(isnear){
		titles = vector<string>{"x", "y"};
		dxy = m_dxy;
	}
	else{
		titles = vector<string>{"x'", "y'"};
		dxy = m_qxy;
	}
	if(isbunch){ // bunch factor
		titles.push_back("Bre");
		titles.push_back("Bim");
	}
	else{
		titles.push_back("Exre");
		titles.push_back("Exim");
		if(m_np > 1){
			titles.push_back("Eyre");
			titles.push_back("Eyim");
		}
	}
	PrintDebugItems(debug_out, titles);
	vector<double> items(titles.size());

	for(int nx = -m_nfft[0]/2+1; nx < m_nfft[0]/2; nx++){
		int ix = fft_index(nx, m_nfft[0], -1);
		items[0] = dxy[0]*nx;
		for(int ny = -m_nfft[1]/2+1; ny < m_nfft[1]/2; ny++){
			int iy = fft_index(ny, m_nfft[1], -1);
			items[1] = dxy[1]*ny;
			if(type < 0){ // bunch factor workspace
				items[2] = m_B[nh][ns][ix][2*iy];
				items[3] = m_B[nh][ns][ix][2*iy+1];
			}
			else{
				for(int np = 0; np < (isbunch?1:m_np); np++){
					items[2*np+2] = m_E[np][nh][type][ns][ix][2*iy];
					items[2*np+3] = m_E[np][nh][type][ns][ix][2*iy+1];
				}
			}
			PrintDebugItems(debug_out, items);
		}
	}
	debug_out.close();
}

void RadiationHandler::f_ExportFieldTemp(
	int n,  bool isbunch, int type, int nh, string dataname)
{
	dataname = dataname+to_string(m_rank)+".dat";
	ofstream debug_out(dataname);
	int nsoffset = f_GetSliceOffset(n);

	vector<string> titles {"s(mm)"};
	if(isbunch){ // bunch factor
		titles.push_back("Bre");
		titles.push_back("Bim");
	}
	else{
		titles.push_back("Exre");
		titles.push_back("Exim");
		if(m_np > 1){
			titles.push_back("Eyre");
			titles.push_back("Eyim");
		}
	}
	PrintDebugItems(debug_out, titles);

	vector<double> items(titles.size());
	double reim[2];
	for(int ns = 0; ns < m_slices_total; ns++){
		if(ns < m_sranges[0] || ns > m_sranges[1]){
			continue;
		}
		items[0] = (ns-m_nsorg)*m_lslice*1e3; // m -> mm
		if(type < 0){
			reim[0] = reim[1] = 0;
			for(int nx = 0; nx < m_nfft[0]; nx++){
				for(int ny = 0; ny < m_nfft[1]; ny++){
					reim[0] += m_B[nh][ns][nx][2*ny];
					reim[1] += m_B[nh][ns][nx][2*ny+1];
				}
			}
			items[1] = reim[0];
			items[2] = reim[1];
		}
		else{
			for(int np = 0; np < (isbunch?1:m_np); np++){
				items[2*np+1] = m_E[np][nh][type][ns][0][0];
				items[2*np+2] = m_E[np][nh][type][ns][0][1];
			}
		}
		PrintDebugItems(debug_out, items);
	}
	debug_out.close();
}

void RadiationHandler::f_ExportGxyGrid(int nh, vector<int> secrange[], string dataname)
{
	int nxy[2];
	string xystr[2] = {"x", "y"};
	for(int jxy = 0; jxy < 2; jxy++){
		string fname = dataname+xystr[jxy]+".dat";
		ofstream debug_out(fname);
		vector<string> titles(1+2*m_Esec[nh]);
		vector<int> sec(m_Esec[nh]);
		titles[0] = xystr[jxy]+"hat";
		for(int i = 0; i < m_Esec[nh]; i++){
			sec[i] = (secrange[0][i]+secrange[1][i])/2;
			titles[i+1] = "Re"+to_string(secrange[0][i])+"-"+to_string(secrange[1][i]);
			titles[i+1+m_Esec[nh]] = "Im"+to_string(secrange[0][i])+"-"+to_string(secrange[1][i]);
		}
		PrintDebugItems(debug_out, titles);
		vector<double> items(titles.size());
		double avsize[2];
		for(int j = 0; j < 2; j++){
			avsize[j] = sqrt(m_betaav[j]*m_emitt[j]);
		}
		nxy[1-jxy] = 0;
		for(nxy[jxy] = -m_nfft[jxy]/2; nxy[jxy] <= m_nfft[jxy]/2; nxy[jxy]++){
			items[0] = nxy[jxy]*m_dxy[jxy]/avsize[jxy];
			int ixy = fft_index(nxy[0], m_nfft[0], -1)*m_nfft[1]+fft_index(nxy[1], m_nfft[1], -1);
			int im = 1;
			for(int i = 0; i < m_Esec[nh]; i++){
				items[im] = m_GnAvg[nh][i][2*ixy];
				im++;
			}
			for(int i = 0; i < m_Esec[nh]; i++){
				items[im] = m_GnAvg[nh][i][2*ixy+1];
				im++;
			}
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
}

void RadiationHandler::f_ExportGxyFldGrowth(int n, int nh, vector<int> secrange[], string dataname)
{
	double dsigma = 1;
	int nxy[2];
	string xystr[2] = {"x", "y"};
	for(int jxy = 0; jxy < 2; jxy++){
		int dn = (int)floor(sqrt(m_emitt[jxy]*m_betaav[jxy])/dsigma/m_dxy[jxy]+0.5);
		int ngrid = m_nfft[jxy]/2/dn;
		string fname = dataname+xystr[jxy]+".dat";
		ofstream debug_out(fname);
		vector<string> titles(1+ngrid*2);
		titles[0] = "Step";
		for(int ng = 0; ng < ngrid; ng++){
			int dxy = (int)floor(0.5+ng*dsigma);
			titles[2*ng+1] = "Re"+to_string(dxy);
			titles[2*ng+2] = "Im"+to_string(dxy);
		}
		PrintDebugItems(debug_out, titles);
		vector<double> items(titles.size());

		nxy[1-jxy] = 0;
		int nfin = m_Esec[nh]-1;
		int jfin = n == nfin ? 1 : 2;
		for(int m = 0; m <= nfin; m++){
			for(int j = 0; j < jfin; j++){
				items[0] = secrange[j][m];
				for(int ng = 0; ng < ngrid; ng++){
					nxy[jxy] = ng*dn;
					int ixy = fft_index(nxy[0], m_nfft[0], 1)*m_nfft[1]+fft_index(nxy[1], m_nfft[1], 1);
					items[2*ng+1] = m_GnAvg[nh][m][2*ixy];
					items[2*ng+2] = m_GnAvg[nh][m][2*ixy+1];
				}
				PrintDebugItems(debug_out, items);
			}
		}
		debug_out.close();
	}
}

