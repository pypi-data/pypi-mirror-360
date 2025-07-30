#include "wigner_function_disc.h"
#include "common.h"
#include "interpolation.h"

string WigDiscRawData;
string WigDiscSplData;
string WigDiscSplBefFFT;
string WigDiscSplAftFFT;
string WigDiscSplBefFFT2D;
string WigDiscSplAftFFT2D;
string WigDiscResult1D;

WignerFunctionDiscrete::WignerFunctionDiscrete()
{
#ifdef _DEBUG
	WigDiscRawData = "..\\debug\\wigner_raw.dat";
	WigDiscSplData = "..\\debug\\wigner_raw_spl.dat";
	WigDiscSplBefFFT = "..\\debug\\wigner_bef.dat";
	WigDiscSplAftFFT = "..\\debug\\wigner_aft.dat";
	WigDiscSplBefFFT2D = "..\\debug\\wigner_bef2d.dat";
	WigDiscSplAftFFT2D = "..\\debug\\wigner_aft2d.dat";
	WigDiscResult1D = "..\\debug\\wigner_result1d.dat";
#endif
	m_fft = nullptr;
	m_ws = nullptr;
	m_ws2d = nullptr;
}

WignerFunctionDiscrete::~WignerFunctionDiscrete()
{
	if(m_fft != nullptr){
		delete m_fft;
	}
	if(m_ws != nullptr){
		delete[] m_ws;
	}
	if(m_ws2d != nullptr){
		for(int n = 0; n < m_nfft2d[1]; n++){
			delete[] m_ws2d[n];
		}
		delete[] m_ws2d;
	}
}

double WignerFunctionDiscrete::Initialize(int ncol, int nrow, 
	double dcol, double drow, int fftlevel, int divlevel, int extracols)
{
	m_ncol = ncol;
	m_nrow = nrow;
	m_dcol = dcol;
	m_drow = drow;
	m_divlevel = divlevel;
	m_ndiv = 1;
	if(m_divlevel > 0){
		m_ndiv = 1<<m_divlevel;
		m_ncol <<= m_divlevel;
		m_dcol /= m_ndiv;
	}

	if(m_nrow == 1){
		m_drow = 1.0;
	}

	m_nfft = fft_number(m_ncol+extracols, fftlevel);
	m_nfft >>= 1; // for interval of Wigner function scheme

	return (double)m_nfft*m_dcol*2.0;
}

void WignerFunctionDiscrete::Initialize2D(int ncol, int nrow, 
	double dcol, double drow, double Dxy[], int level)
{
	m_ncol = ncol;
	m_nrow = nrow;
	m_dcol = dcol;
	m_drow = drow;
	m_divlevel = 0;

	m_nfft2d[0] = fft_number(m_ncol, level);
	m_nfft2d[0] >>= 1; // for interval of Wigner function scheme
	m_nfft2d[1] = fft_number(m_nrow, level);
	m_nfft2d[1] >>= 1; // for interval of Wigner function scheme

	Dxy[0] = m_nfft2d[0]*m_dcol*2.0;
	Dxy[1] = m_nfft2d[1]*m_drow*2.0;
}

void WignerFunctionDiscrete::AssignData(double **data, int fftdir)
{
	m_fftdir = fftdir;
	m_data.resize(m_ncol);
	for(int nc = 0; nc < m_ncol; nc++){
		m_data[nc].resize(m_nrow*2);
	}
	m_fft = new FastFourierTransform(2, m_nfft2d[0], m_nfft2d[1]);

	for(int nc = 0; nc < m_ncol; nc++){
		for(int nr = 0; nr < m_nrow; nr++){
			m_data[nc][2*nr] = data[nc][2*nr];
			m_data[nc][2*nr+1] = data[nc][2*nr+1];
		}
	}
}

void WignerFunctionDiscrete::AssignData(double *data, int ndata, int fftdir, bool istranspose)
{
	Spline re, im;
	vector<double> colarr, rearr, imarr;
	double zero = 0;

	m_fftdir = fftdir;
	m_data.resize(m_nrow);
	for(int nr = 0; nr < m_nrow; nr++){
		m_data[nr].resize(m_ncol*2);
	}
	m_fft = new FastFourierTransform(1, m_nfft);

	if(m_divlevel > 0){
		colarr.resize(ndata);
		rearr.resize(ndata);
		imarr.resize(ndata);
		for(int nc = 0; nc < ndata; nc++){
			colarr[nc] = nc*m_ndiv;
		}
	}

	for(int nr = 0; nr < m_nrow; nr++){
		for(int nc = 0; nc < ndata; nc++){
			if(istranspose){
				m_data[nr][2*nc] = data[nc*m_nrow*2+2*nr];
				m_data[nr][2*nc+1] = data[nc*m_nrow*2+2*nr+1];
			}
			else{
				m_data[nr][2*nc] = data[nr*ndata*2+2*nc];
				m_data[nr][2*nc+1] = data[nr*ndata*2+2*nc+1];
			}

			if(m_divlevel > 0){
				rearr[nc] = m_data[nr][2*nc];
				imarr[nc] = m_data[nr][2*nc+1];
			}
		}
		if(m_divlevel > 0){
#ifdef _DEBUG
			if(!WigDiscRawData.empty()){
				ofstream debug_out(WigDiscRawData);
				vector<string> titles {"x", "real", "imag"};
				vector<double> items(titles.size());
				PrintDebugItems(debug_out, titles);
				for(int nc = 0; nc < ndata; nc++){
					items[0] = nc*m_ndiv;
					items[1] = m_data[nr][2*nc];
					items[2] = m_data[nr][2*nc+1];
					PrintDebugItems(debug_out, items);
				}
				debug_out.close();
			}
#endif
			re.SetSpline(ndata, &colarr, &rearr, true);
			im.SetSpline(ndata, &colarr, &imarr, true);
			for(int nc = 0; nc < m_ncol; nc++){
				m_data[nr][2*nc] = re.GetValue(nc, true, nullptr, &zero);
				m_data[nr][2*nc+1] = im.GetValue(nc, true, nullptr, &zero);
			}
#ifdef _DEBUG
			if(!WigDiscSplData.empty()){
				ofstream debug_out(WigDiscSplData);
				vector<string> titles{"x", "real", "imag"};
				vector<double> items(titles.size());
				PrintDebugItems(debug_out, titles);
				for(int nc = 0; nc < m_ncol; nc++){
					items[0] = nc;
					items[1] = m_data[nr][2*nc];
					items[2] = m_data[nr][2*nc+1];
					PrintDebugItems(debug_out, items);
				}
				debug_out.close();
			}
#endif
		}
	}
}

void WignerFunctionDiscrete::GetWigner(
	int colrange[], int arange[], vector<double> *w, bool istranspose, int asmooth, bool debug)
{
	// arange: range to specify energy or angle, can be negative (0 = center)
	int ncs = colrange[1]-colrange[0]+1;
	int nws = arange[1]-arange[0]+1;
	if(w->size() < ncs*nws){
		w->resize(ncs*nws);
	}

	for(int nc = colrange[0]; nc <= colrange[1]; nc++){
		bool isob = nc < 0 || nc >= m_ncol;
		if(!isob){
			int ncr = nc<<m_divlevel;
			f_WignerSingle(ncr, asmooth, debug);
		}
		for(int nw = arange[0]; nw <= arange[1]; nw++){
			int index = istranspose ? 
				(nw-arange[0])+(nc-colrange[0])*nws : 
				(nc-colrange[0])+(nw-arange[0])*ncs;
			if(abs(nw) > m_nfft/2 || isob){
				(*w)[index] = 0.0;
				continue;
			}
			int windex = fft_index(nw, m_nfft, -1);
			(*w)[index] = m_ws[2*windex];
		}
	}

#ifdef _DEBUG
	if(!WigDiscResult1D.empty() && debug){
		ofstream debug_out(WigDiscResult1D);
		vector<string> titles{"x", "x'", "W"};
		vector<double> items(titles.size());
		PrintDebugItems(debug_out, titles);
		int nws = arange[1]-arange[0]+1;
		for(int nc = colrange[0]; nc <= colrange[1]; nc++){
			items[0] = nc;
			for(int nw = arange[0]; nw <= arange[1]; nw++){
				items[1] = nw;
				items[2] = (*w)[(nw-arange[0])+(nc-colrange[0])*nws];
				PrintDebugItems(debug_out, items);
			}
		}
		debug_out.close();
	}
#endif
}

void WignerFunctionDiscrete::GetWigner2D(int crindex[], int aini[], int afin[], vector<vector<double>> *w)
{
	// arange: range to specify energy or angle, can be negative (0 = center)
	int ncs = afin[0]-aini[0]+1;
	int nws = afin[1]-aini[1]+1;

	if(w->size() < ncs){
		w->resize(ncs);
		for(int n = 0; n < ncs; n++){
			(*w)[n].resize(nws);
		}
	}

	f_WignerSingle2D(crindex[0], crindex[1]);

	for(int nc = aini[0]; nc <= afin[0]; nc++){
		int cindex = fft_index(nc, m_nfft2d[0], -1);
		for(int nw = aini[1]; nw <= afin[1]; nw++){
			int windex = fft_index(nw, m_nfft2d[1], -1);
			if(abs(nc) > m_nfft2d[0]/2 || abs(nw) > m_nfft2d[1]/2){
				(*w)[nc-aini[0]][nw-aini[1]] = 0.0;
				continue;
			}
			(*w)[nc-aini[0]][nw-aini[1]] = m_ws2d[cindex][2*windex];
		}
	}
}

// private functions
void WignerFunctionDiscrete::f_WignerSingle(int colindex, int asmooth, bool debug)
{
	if(m_ws == nullptr){
		m_ws = new double[2*m_nfft];
	}

	int index, icp, icm;
	double tex, sigma;
	sigma = PI2*(double)abs(asmooth)/m_nfft;
	for(int n = 0; n < m_nfft; n++){
		index = fft_index(n, m_nfft, 1);
		icp = colindex+index;
		icm = colindex-index;

		m_ws[2*n] = m_ws[2*n+1] = 0.0;
		if(icp < 0 || icp >= m_ncol || icm < 0 || icm >= m_ncol){
			continue;
		}
		for(int nr = 0; nr < m_nrow; nr++){
			m_ws[2*n] += m_data[nr][2*icp]*m_data[nr][2*icm]+m_data[nr][2*icp+1]*m_data[nr][2*icm+1]; // real part E^* x E
			m_ws[2*n+1] += -m_data[nr][2*icp+1]*m_data[nr][2*icm]+m_data[nr][2*icp]*m_data[nr][2*icm+1]; // imaginary part E^* x E
		}
		m_ws[2*n] *= m_drow;
		m_ws[2*n+1] *= m_drow;
		if(asmooth > 0){
			tex = sigma*index;
			tex *= tex*0.5;
			if(tex < MAXIMUM_EXPONENT){
				tex = exp(-tex);
				m_ws[2*n] *= tex;
				m_ws[2*n+1] *= tex;
			}
		}
	}

#ifdef _DEBUG
	if(!WigDiscSplBefFFT.empty() && debug){
		ofstream debug_out(WigDiscSplBefFFT);
		vector<string> titles{"x", "real", "imag"};
		vector<double> items(titles.size());
		PrintDebugItems(debug_out, titles);
		for(int n = -m_nfft/2; n <= m_nfft/2; n++){
			index = fft_index(n, m_nfft, -1);
			items[0] = n*m_dcol;
			items[1] = m_ws[2*index];
			items[2] = m_ws[2*index+1];
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif

	m_fft->DoFFT(m_ws, m_fftdir);
	for(int n = 0; n < m_nfft; n++){
		m_ws[2*n] *= 2.0*m_dcol;
		m_ws[2*n+1] *= 2.0*m_dcol;
	}

#ifdef _DEBUG
	if(!WigDiscSplAftFFT.empty() && debug){
		ofstream debug_out(WigDiscSplAftFFT);
		vector<string> titles{"x'", "real", "imag"};
		vector<double> items(titles.size());
		PrintDebugItems(debug_out, titles);
		for(int n = -m_nfft/2; n <= m_nfft/2; n++){
			index = fft_index(n, m_nfft, -1);
			items[0] = n;
			items[1] = m_ws[2*index];
			items[2] = m_ws[2*index+1];
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif
}

void WignerFunctionDiscrete::f_WignerSingle2D(int colindex, int rowindex)
{
	if(m_ws2d == nullptr){
		m_ws2d = new double*[m_nfft2d[0]];
		for(int n = 0; n < m_nfft2d[1]; n++){
			m_ws2d[n] = new double[2*m_nfft2d[1]];
		}
	}

	int index[2], icp[2], icm[2];
	for(int n = 0; n < m_nfft2d[0]; n++){
		index[0] = fft_index(n, m_nfft2d[0], 1);
		icp[0] = colindex+index[0];
		icm[0] = colindex-index[0];
		for(int m = 0; m < m_nfft2d[1]; m++){
			index[1] = fft_index(m, m_nfft2d[1], 1);
			icp[1] = rowindex+index[1];
			icm[1] = rowindex-index[1];
			m_ws2d[n][2*m] = m_ws2d[n][2*m+1] = 0.0;
			if(icp[0] < 0 || icp[0] >= m_ncol || icm[0] < 0 || icm[0] >= m_ncol){
				continue;
			}
			if(icp[1] < 0 || icp[1] >= m_nrow || icm[1] < 0 || icm[1] >= m_nrow){
				continue;
			}
			double rep = m_data[icp[0]][2*icp[1]];
			double imp = m_data[icp[0]][2*icp[1]+1];
			double rem = m_data[icm[0]][2*icm[1]];
			double imm = m_data[icm[0]][2*icm[1]+1];
			m_ws2d[n][2*m] += rep*rem+imp*imm; // real part E^* x E
			m_ws2d[n][2*m+1] += -imp*rem+rep*imm; // imaginary part E^* x E
		}
	}

#ifdef _DEBUG
	if(!WigDiscSplBefFFT2D.empty()){
		ofstream debug_out(WigDiscSplBefFFT2D);
		vector<string> titles{"x", "y", "real", "imag"};
		vector<double> items(titles.size());
		PrintDebugItems(debug_out, titles);
		for(int n = -m_nfft2d[0]/2; n <= m_nfft2d[0]/2; n++){
			items[0] = n*m_dcol;
			index[0] = fft_index(n, m_nfft2d[0], -1);
			for(int m = -m_nfft2d[1]/2; m <= m_nfft2d[1]/2; m++){
				items[0] = m*m_drow;
				index[1] = fft_index(m, m_nfft2d[1], -1);
				items[2] = m_ws2d[index[0]][2*index[1]];
				items[3] = m_ws2d[index[0]][2*index[1]+1];
				PrintDebugItems(debug_out, items);
			}
		}
		debug_out.close();
	}
#endif

	m_fft->DoFFT(m_ws2d, m_fftdir);
	for(int n = 0; n < m_nfft2d[0]; n++){
		for(int m = 0; m < m_nfft2d[1]; m++){
			m_ws2d[n][2*m] *= 4.0*m_dcol*m_drow;
			m_ws2d[n][2*m+1] *= 4.0*m_dcol*m_drow;
		}
	}

#ifdef _DEBUG
	if(!WigDiscSplAftFFT2D.empty()){
		ofstream debug_out(WigDiscSplAftFFT2D);
		vector<string> titles{"x'", "y'", "real", "imag"};
		vector<double> items(titles.size());
		PrintDebugItems(debug_out, titles);
		for(int n = -m_nfft2d[0]/2; n <= m_nfft2d[0]/2; n++){
			items[0] = n;
			index[0] = fft_index(n, m_nfft2d[0], -1);
			for(int m = -m_nfft2d[1]/2; m <= m_nfft2d[1]/2; m++){
				items[0] = m;
				index[1] = fft_index(m, m_nfft2d[1], -1);
				items[2] = m_ws2d[index[0]][2*index[1]];
				items[3] = m_ws2d[index[0]][2*index[1]+1];
				PrintDebugItems(debug_out, items);
			}
		}
		debug_out.close();
	}
#endif
}
