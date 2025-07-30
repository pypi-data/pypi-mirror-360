#ifndef wigner_function_disc_h
#define wigner_function_disc_h

#include <vector>
#include "fast_fourier_transform.h"
using namespace std;

class WignerFunctionDiscrete
{
public:
	WignerFunctionDiscrete();
	~WignerFunctionDiscrete();
	double Initialize(int ncol, int nrow, 
		double dcol, double drow, int fftlevel, int divlevel, int extracols = 0);
	void Initialize2D(int ncol, int nrow, 
		double dcol, double drow, double Dxy[], int fftlevel = 1);

	void AssignData(double **data, int fftdir);
	void AssignData(double *data, int ndata, int fftdir, bool istranspose);
	void GetWigner(int colrange[], int arange[], vector<double> *w, 
		bool istranspose, int asmooth = 0, bool debug = false);
	void GetWigner2D(int crindex[], int aini[], int afin[], vector<vector<double>> *w);

private:
	void f_WignerSingle(int colindex, int asmooth, bool debug = false);
	void f_WignerSingle2D(int colindex, int rowindex);

	FastFourierTransform *m_fft;
	vector<vector<double>> m_data;
	double *m_ws;
	int m_ncol; // number of data points for FFT
	int m_nrow; // number of data points for summation
	int m_nfft;
	double m_dcol; // interval of columns
	double m_drow; // interval of rows
	int m_divlevel; // interpolation number
	int m_ndiv; // point interval
	int m_fftdir; // FFT direction

	double **m_ws2d;
	int m_nfft2d[2]; // number of data points for FFT2D
};


#endif