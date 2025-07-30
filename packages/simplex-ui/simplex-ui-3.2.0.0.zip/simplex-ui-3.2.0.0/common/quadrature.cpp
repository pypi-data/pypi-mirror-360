#include <algorithm>
#include <iostream>
#include <fstream>
#include <math.h>
#include <stdlib.h>

#include "common.h"
#include "quadrature.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

#define SIMPSON_MAX_ITERATION 16
// maximum number to evaluate the integrand function: 2^16 = 65536
#define INITIAL_EPS_SIMPSON 2.0

//------------------------------------------------------------------------------
// Simpson quadruature
QSimpson::QSimpson()
{
	m_nitems = 0;
	m_statusqsimp = NULL;
	m_cancelqsimp = false;
	m_mpiprocesses = 1;
	m_rank = 0;
	m_mpilayer = -1;
}

void QSimpson::ArrangeMPIConfig(
	int rank, int mpiprocesses, int mpipayer, MPIbyThread *thread)
	// should be called before AllocateMemorySimpson()
{
	m_mpiprocesses = mpiprocesses;
	m_rank = rank;
	m_mpilayer = mpipayer;
	m_qthread = thread;
}

void QSimpson::AllocateMemorySimpson(int nitems, int nborder, int layers)
{
	m_maxorder = 4;

	m_nitems = nitems;
	m_nborder = nborder;
	m_layers = layers;
	m_wsFunc.resize(m_layers);
	m_sumTrap.resize(m_layers);
	m_yRombO.resize(m_layers);
	m_yRombC.resize(m_layers);
	m_fintval.resize(m_layers);
	m_fintarg.resize(m_layers);
	m_ndata.resize(m_layers);
	m_issave.resize(m_layers, false);
	m_currmaxref.resize(m_layers, 0.0);

	for(int j = 0; j < m_layers; j++){
		m_wsFunc[j].resize(m_nitems);
		m_yRombO[j].resize(m_maxorder);
		m_yRombC[j].resize(m_maxorder);
	}

	if(m_mpiprocesses > 1){
		for(int j = 0; j < 2; j++){
			m_ws4mpi_sum[j] = new double[m_nitems];
			m_ws4mpi_max[j] = new double[m_nitems];
		}
	}

	for(int j = 0; j < m_layers; j++){
		m_sumTrap[j].resize(m_nitems, 0.0);
		for(int m = 0; m < m_maxorder; m++){
			m_yRombO[j][m].resize(m_nitems, 0.0);
			m_yRombC[j][m].resize(m_nitems, 0.0);
		}
	}
}

QSimpson::~QSimpson()
{
	if(m_mpiprocesses > 1){
		for(int j = 0; j < 2; j++){
			delete[] m_ws4mpi_sum[j];
			delete[] m_ws4mpi_max[j];
		}
	}
}

void QSimpson::IntegrateSimpson(
	int *layers, // 0: layer for integrand, 1: layer for print status
	double a, double b, double eps, int jrepmin, 
	vector<vector<double>> *finit, vector<double> *answer, 
	string debug, bool isappend, bool issave, int jrepmax)
{
	double ymax[2], fmax[2], dfmax[2], dx = fabs(b-a), feps = INFINITESIMAL, qeps;
	int j, jm, n, m, n4m, mcurr, ndata = 1;
	int layeri = layers[0];
	int layerp = layers[1];
	bool iconv = false;

	if(layeri >= m_layers){
		throw runtime_error("Invalid layer number for integration.");
		return;
	}

	if(jrepmax < 0){
		jrepmax = SIMPSON_MAX_ITERATION;
	}
	jrepmax = min(jrepmax, SIMPSON_MAX_ITERATION);
	
	if(m_statusqsimp && layerp >= 0){
		m_statusqsimp->SetTargetAccuracy(layerp, eps);
		m_statusqsimp->SetCurrentAccuracy(layerp, INITIAL_EPS_SIMPSON);
	}

	if(fabs(a-b) < INFINITESIMAL){
		for(n = 0; n < m_nitems; n++){
			(*answer)[n] = 0.0;
		}
		if(m_statusqsimp && layerp >= 0){
			m_statusqsimp->SetSubstepNumber(layerp, 1);
			m_statusqsimp->PutSteps(layerp, 1);
		}
		return;
	}

	if(finit != NULL){
		fmax[0] = (*finit)[layeri][0];
		fmax[1] = (*finit)[layeri][1];
	}
	else{
		fmax[0] = fmax[1] = INFINITESIMAL;
	}

	jrepmin = max(jrepmin-1, 2);

	if(issave){
		m_issave[layeri] = true;
		ndata = (1<<jrepmin)+1;
		f_ExpandStorage(layeri, ndata);
		m_ndata[layeri] = 0;
	}

	for(j = 0; j <= jrepmax; j++){
		if(issave && j > jrepmin){
			ndata = (ndata-1)*2+1;
			f_ExpandStorage(layeri, ndata);
		}
		dx *= 0.5;
		f_QTrapezoid(layers, a, b, j, 
			dfmax, m_yRombO[layeri][0], m_yRombC[layeri][0], debug, (j>0)||isappend);

		if(m_statusqsimp && layerp >= 0){
			m_statusqsimp->SetCurrentOrigin(layerp);
		}

		if(m_cancelqsimp){
			return;
		}
		fmax[0] = max(fmax[0], dfmax[0]); 
		fmax[1] = max(fmax[1], dfmax[1]);
		mcurr = min(j, m_maxorder-1);
		n4m = 1;
		for(m = 1; m <= mcurr; m++){
			n4m *= 4;
			for(n = 0; n < m_nitems; n++){
				m_yRombC[layeri][m][n] =
				((double)n4m*m_yRombC[layeri][m-1][n]-m_yRombO[layeri][m-1][n])/(double)(n4m-1);
			}
		}
		ymax[0] = ymax[1] = INFINITESIMAL;
		for(n = 0; n < m_nitems; n++){
			jm = n > m_nborder ? 1 : 0;
			ymax[jm] = max(ymax[jm], fabs(m_yRombC[layeri][mcurr][n]));
		}
		if(j > 1){
			feps = INFINITESIMAL;
			if(m_currmaxref[layeri] > INFINITESIMAL){
				qeps = INFINITESIMAL;
			}
			for(n = 0; n < m_nitems; n++){
				jm = n > m_nborder ? 1 : 0;
				double derr = fabs((*answer)[n]-m_yRombC[layeri][mcurr][n]);
				feps = max(feps, derr/(INFINITESIMAL+max(dx*fmax[jm], ymax[jm])));
				if(m_currmaxref[layeri] > INFINITESIMAL){
					qeps = max(qeps, derr/m_currmaxref[layeri]);
				}
			}
			if(m_currmaxref[layeri] > INFINITESIMAL){
				feps = min(feps, qeps);
			}						
			iconv = feps < eps;
			if(m_statusqsimp && layerp >= 0){
				if(j >= jrepmin){
					m_statusqsimp->SetCurrentAccuracy(layerp, feps);
				}
			}
		}
		iconv = (j >= jrepmin) && iconv;
		for(n = 0; n < m_nitems; n++){
			(*answer)[n] = m_yRombC[layeri][mcurr][n];
		}
		if(iconv){
			break;
		}
		for(m = 0; m <= mcurr; m++){
			for(n = 0; n < m_nitems; n++){
				m_yRombO[layeri][m][n] = m_yRombC[layeri][m][n];
			}
		}
	}
	if(finit != NULL){
		(*finit)[layeri][0] = fmax[0];
		(*finit)[layeri][1] = fmax[1];
	}
}

int QSimpson::GetEvaluatedValue(int layer, 
		vector<double> *arg, vector<vector<double>> *values, string debug)
{
	if(arg->size() < m_ndata[layer]){
		arg->resize(m_ndata[layer]);
	}

	if(values->size() < m_ndata[layer]){
		values->resize(m_ndata[layer]);
	}
	for(int n = 0; n < m_ndata[layer]; n++){
		if((*values)[n].size() < m_nitems){
			(*values)[n].resize(m_nitems);
		}
	}

	for(int n = 0; n < m_ndata[layer]; n++){
		(*arg)[n] = m_fintarg[layer][n];
		for(int m = 0; m < m_nitems; m++){
			(*values)[n][m] = m_fintval[layer][n][m];
		}
	}

#ifdef _DEBUG
	if(!debug.empty()){
		ofstream debug_out(debug);
		PrintDebugCols(debug_out, *arg, *values, m_ndata[layer]);
	}
#endif

	return m_ndata[layer];

}

void QSimpson::SetCalcStatusPrint(PrintCalculationStatus *status)
{
	m_statusqsimp = status;
}

void QSimpson::QSimpsonIntegrandSt(int layer, double xy, vector<double> *density)
{
	QSimpsonIntegrand(layer, xy, density);
	if(m_issave[layer]){
		m_fintarg[layer][m_ndata[layer]] = xy;
		for(int n = 0; n < m_nitems; n++){
			m_fintval[layer][m_ndata[layer]][n] = (*density)[n];
		}
		m_ndata[layer]++;
	}
}

//----- private functions
void QSimpson::f_ExpandStorage(int layer, int ndata)
{
	if(m_fintval[layer].size() < ndata){
		m_fintval[layer].resize(ndata);
	}
	for(int n = 0; n < ndata; n++){
		if(m_fintval[layer][n].size() < m_nitems){
			m_fintval[layer][n].resize(m_nitems);
		}
	}
	if(m_fintarg[layer].size() < ndata){
		m_fintarg[layer].resize(ndata);
	}		
}

void QSimpson::f_QTrapezoid(int *layers,  double a, double b, int nrep,
	double *fmax, vector<double> &yold, vector<double> &ynew, string debug, bool isappend)
{
	double xr, di, dx, dab;
	int i, j, n, jm;
	int layer = layers[0];
	int layerp = layers[1];

#ifdef _DEBUG
	ofstream debug_out;
	if(!debug.empty()){
		debug_out.open(debug,  isappend?(ios::app):(ios::trunc));
	}
#endif

	//------->>>>>>>>
	//chrono::system_clock::time_point rtime[2];
	//rtime[0] = chrono::system_clock::now();

	fmax[0] = fmax[1] = INFINITESIMAL;

	dab = b-a;
	if(nrep == 0){
		if(m_statusqsimp && layerp >= 0){
			m_statusqsimp->SetSubstepNumber(layerp, 2);
		}
		QSimpsonIntegrandSt(layer, a, &m_wsFunc[layer]);
		if(m_cancelqsimp){
			return;
		}
		if(m_statusqsimp && layerp >= 0){
			m_statusqsimp->PutSteps(layerp, 1);
		}

		for(n = 0; n < m_nitems; n++){
			jm = n > m_nborder ? 1 : 0;
			fmax[jm] = max(fmax[jm], fabs(m_wsFunc[layer][n]));
			ynew[n] = 0.5*dab*m_wsFunc[layer][n];
		}
#ifdef _DEBUG
		PrintDebugItems(debug_out, a, m_wsFunc[layer]);
#endif
		QSimpsonIntegrandSt(layer, b, &m_wsFunc[layer]);
		if(m_statusqsimp && layerp >= 0){
			m_statusqsimp->PutSteps(layerp, 2);
		}
		for(n = 0; n < m_nitems; n++){
			jm = n > m_nborder ? 1 : 0;
			fmax[jm] = max(fmax[jm], fabs(m_wsFunc[layer][n]));
			ynew[n] += 0.5*dab*m_wsFunc[layer][n];
		}
#ifdef _DEBUG
		PrintDebugItems(debug_out, b, m_wsFunc[layer]);
#endif
	}
	else{
		i = 1;
		if(nrep > 1){
			i <<= nrep-1;
		}
		di = (double)i;
		dx = dab/di;
		for(n = 0; n < m_nitems; n++){
			m_sumTrap[layer][n] = 0.0;
		}

		if(m_mpiprocesses > 1 && i > 1 && layer == m_mpilayer){
			if(m_statusqsimp && layerp >= 0){
				m_statusqsimp->SetSubstepNumber(layerp, (i-1)/m_mpiprocesses+1);
			}
			for(n = 0; n < m_nitems; n++){
				m_ws4mpi_sum[0][n] = m_ws4mpi_max[0][n] = 0.0;
			}

			for(j = 0; j < i; j++){
				if(m_rank != j%m_mpiprocesses){
					continue;
				}
				xr = a+0.5*dx+j*dx;
				QSimpsonIntegrandSt(layer, xr, &m_wsFunc[layer]);
				if(m_cancelqsimp){
					return;
				}
				if(m_statusqsimp && layerp >= 0){
					m_statusqsimp->PutSteps(layerp, j+1);
				}
				for(n = 0; n < m_nitems; n++){
					m_ws4mpi_max[0][n] = max(m_ws4mpi_max[0][n], fabs(m_wsFunc[layer][n]));
					m_ws4mpi_sum[0][n] += m_wsFunc[layer][n];
				}
			}

			MPI_Barrier(MPI_COMM_WORLD);
			if(m_qthread != nullptr){
				m_qthread->Allreduce(m_ws4mpi_sum[0], m_ws4mpi_sum[1], m_nitems, MPI_DOUBLE, MPI_SUM, m_rank);
				m_qthread->Allreduce(m_ws4mpi_max[0], m_ws4mpi_max[1], m_nitems, MPI_DOUBLE, MPI_MAX, m_rank);
			}
			else{
				MPI_Allreduce(m_ws4mpi_sum[0], m_ws4mpi_sum[1], m_nitems, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
				MPI_Allreduce(m_ws4mpi_max[0], m_ws4mpi_max[1], m_nitems, MPI_DOUBLE, MPI_MAX, MPI_COMM_WORLD);
			}

			for(n = 0; n < m_nitems; n++){
				jm = n > m_nborder ? 1 : 0;
				fmax[jm] = max(fmax[jm], m_ws4mpi_max[1][n]);
				m_sumTrap[layer][n] += m_ws4mpi_sum[1][n];
			}
		}
		else{
			if(m_statusqsimp && layerp >= 0){
				m_statusqsimp->SetSubstepNumber(layerp, i);
			}
			for(j = 0; j < i; j++){
				xr = a+0.5*dx+j*dx;
				QSimpsonIntegrandSt(layer, xr, &m_wsFunc[layer]);
				if(m_cancelqsimp){
					return;
				}
				if(m_statusqsimp && layerp >= 0){
					m_statusqsimp->PutSteps(layerp, j+1);
				}
				for(n = 0; n < m_nitems; n++){
					jm = n > m_nborder ? 1 : 0;
					fmax[jm] = max(fmax[jm], fabs(m_wsFunc[layer][n]));
					m_sumTrap[layer][n] += m_wsFunc[layer][n];
				}
#ifdef _DEBUG
				PrintDebugItems(debug_out, xr, m_wsFunc[layer]);
#endif
			}
		}

		for(n = 0; n < m_nitems; n++){
			ynew[n] = 0.5*(yold[n]+dab*m_sumTrap[layer][n]/di);
		}

		//------->>>>>>>>
		/*if(layers[0] == 0){
			rtime[1] = chrono::system_clock::now();
			double elapsed = static_cast<double>(chrono::duration_cast<chrono::microseconds>(rtime[1]-rtime[0]).count())/1e6;
			cout << "rank = " << m_rank << ", ndiv = " << i << ", Time elapsed (sec) = " << elapsed << endl;
		}*/
	}


#ifdef _DEBUG
	if(!debug.empty()){
		debug_out.close();
	}
#endif
}

//------------------------------------------------------------------------------
// Gaussian quadruature
void QGauss::InitializeQGauss(int maxorder, int nitems)
{
	Resize(maxorder);
	m_ytmp.resize(nitems);
	m_nitems = nitems;
	m_maxorder = maxorder;
}

void QGauss::Resize(int maxorder)
{
	int ni;
	m_x.resize(maxorder+1);
	m_w.resize(maxorder+1);
	m_isalloc.resize(maxorder+1);
	for(ni = 1; ni <= maxorder; ni++){
		m_isalloc[ni] = false;
	}
}

#define EPS 3.0e-11

void QGauss::f_AllocatePoints(int n)
{
	int m, j, i;
	double z1, z, pp, p3, p2, p1;

	m_x[n].resize(n+1);
	m_w[n].resize(n+1);
	m = (n+1)/2;
	for (i = 1; i <= m; i++) {
		z = cos(PI*(i-0.25)/(n+0.5));
		do {
			p1= 1.0;
			p2 =0.0;
			for (j = 1;j <= n;j++) {
				p3 = p2;
				p2 = p1;
				p1 = ((2.0*j-1.0)*z*p2-(j-1.0)*p3)/j;
			}
			pp = n*(z*p1-p2)/(z*z-1.0);
			z1 = z;
			z = z1-p1/pp;
		} while (fabs(z-z1) > EPS);
		m_x[n][i] = -z;
		m_x[n][n+1-i] = z;
		m_w[n][i] = 2.0/((1.0-z*z)*pp*pp);
		m_w[n][n+1-i] = m_w[n][i];
	}
	m_isalloc[n] = true;
}

#undef EPS

void QGauss::f_ExpandMaxOrder(int maxorder)
{
	int n, ni;
	vector<vector<double>> xtmp(m_maxorder+1);
	vector<vector<double>> wtmp(m_maxorder+1);
	vector<bool> istmp(m_maxorder+1);

	for(n = 1; n <= m_maxorder; n++){
		istmp[n] = m_isalloc[n];
		if(istmp[n]){
			xtmp[n].resize(n+1);
			wtmp[n].resize(n+1);
			for(ni = 1; ni <= n; ni++){
				xtmp[n][ni] = m_x[n][ni];
				wtmp[n][ni] = m_w[n][ni];
			}
		}
	}

	Resize(maxorder);
	for(n = 1; n <= m_maxorder; n++){
		m_isalloc[n] = istmp[n];
		if(m_isalloc[n]){
			m_x[n].resize(n+1);
			m_w[n].resize(n+1);
			for(ni = 1; ni <= n; ni++){
				m_x[n][ni] = xtmp[n][ni];
				m_w[n][ni] = wtmp[n][ni];
			}
		}
	}
	m_maxorder = maxorder;
}

void QGauss::IntegrateGauss(int npoints, double a, double b, 
		vector<double> *ans, string debug, bool isappend)
{
	int n, ni;
	double x, dx = 0.5*(b-a);

#ifdef _DEBUG
	ofstream debug_out;
	if(!debug.empty()){
		debug_out.open(debug, isappend?(ios::app):(ios::trunc));
	}
#endif

	if(npoints > m_maxorder){
		f_ExpandMaxOrder(npoints);
	}
	if(!m_isalloc[npoints]){
		f_AllocatePoints(npoints);
	}
	for(ni = 0; ni < m_nitems; ni++){
		(*ans)[ni] = 0.0;
	}

	for(n = 1; n <= npoints; n++){
		x = ((a+b)+(a-b)*m_x[npoints][n])*0.5;
		IntegrandGauss(x, &m_ytmp);
		for(ni = 0; ni < m_nitems; ni++){
			(*ans)[ni] += m_w[npoints][n]*m_ytmp[ni];
		}
#ifdef _DEBUG
		PrintDebugItems(debug_out, x, m_ytmp);
#endif
	}

	for(ni = 0; ni < m_nitems; ni++){
		(*ans)[ni] *= dx;
	}
}

