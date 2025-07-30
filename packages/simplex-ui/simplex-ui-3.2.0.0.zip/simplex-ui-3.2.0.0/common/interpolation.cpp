#include <algorithm>
#include "interpolation.h"

//------------------------------------------------------------------------------
int SplineBase::GetIndexXcoord(double x)
{
	int index;
	index = SearchIndex(m_size, m_isreg, m_x, x);
	return index;
}

double SplineBase::GetXYItem(int index, bool isx)
{
	index = max(0, min(index, m_size-1));
	return isx ? m_x[index] : m_y[index];
}

double SplineBase::GetIniXY(bool isx)
{
	return GetXYItem(0, isx);
}

double SplineBase::GetFinXY(bool isx)
{
	return GetXYItem(m_size-1, isx);
}
//------------------------------------------------------------------------------
void Spline::SetSpline(
	int nstep, vector<double> *x, vector<double> *y,
	bool isreg, bool islog, bool issort, double *y2ini, double *y2fin)
{
	int i, k;
	double xdifr, ydifr, yn, yp1, y0, ym1;

	Initialize(nstep, x, y, isreg, islog, issort);

	if(m_ws.size() < m_size){
		m_ws.resize(m_size);
	}
	if(islog || y2ini == nullptr){
		m_y2[0] = m_ws[0] = 0.0;
	}
	else{
		m_y2[0] = -0.5;
		m_ws[0] = (3.0/(m_x[1]-m_x[0]))*((m_y[1]-m_y[0])/(m_x[1]-m_x[0])-(*y2ini));
	}
	if(islog){
		if(m_y[0] < INFINITESIMAL){
			ym1 = log(INFINITESIMAL);
		}
		else{
			ym1 = log(m_y[0]);
		}
		if(m_y[1] < INFINITESIMAL){
			y0 = log(INFINITESIMAL);
		}
		else{
			y0 = log(m_y[1]);
		}
	}
	else{
		y0 = m_y[1]; ym1 = m_y[0];
	}
	for(i = 1; i < m_size-1; i++){
		if(islog){
			if(m_y[i+1] < INFINITESIMAL){
				yp1 = log(INFINITESIMAL);
			}
			else{
				yp1 = log(m_y[i+1]);
			}
			if(m_y[i] < INFINITESIMAL){
				m_y2[i] = 0.0;
				m_ws[i] = 0.0;
				ym1 = y0;
				y0 = yp1;
				continue;
			}
		}
		else{
			yp1 = m_y[i+1];
		}
		xdifr = (m_x[i]-m_x[i-1])/(m_x[i+1]-m_x[i-1]);
		ydifr = xdifr*m_y2[i-1]+2.0;
		m_y2[i] = (xdifr-1.0)/ydifr;
		m_ws[i] = (yp1-y0)/(m_x[i+1]-m_x[i])-(y0-ym1)/(m_x[i]-m_x[i-1]);
		m_ws[i] = (6.0*m_ws[i]/(m_x[i+1]-m_x[i-1])-xdifr*m_ws[i-1])/ydifr;
		ym1 = y0;
		y0 = yp1;
	}
	if(islog || y2fin == nullptr){
		m_y2[m_size-1] = 0.0;
	}
	else{
		yn = (3.0/(m_x[m_size-1]-m_x[m_size-2]))
			*((*y2fin)-(m_y[m_size-1]-m_y[m_size-2])/(m_x[m_size-1]-m_x[m_size-2]));
		m_y2[m_size-1] = (yn-0.5*m_ws[m_size-2])/(0.5*m_y2[m_size-2]+1.0);
	}
	for(k = m_size-2; k >= 0; k--){
		m_y2[k] = m_y2[k]*m_y2[k+1]+m_ws[k];
		if(fabs(m_y2[k]) < INFINITESIMAL){
			m_y2[k] = 0;
		}
	}
	m_isderivalloc = false;
	m_spl_on = true;
}

void Spline::Initialize(int nstep,
	vector<double> *x, vector<double> *y, bool isreg, bool islog, bool issort)
{
	if(m_y2.size() < nstep){
		m_y2.resize(nstep, 0.0);
	}
	m_x = *x;
	m_y = *y;

	if(issort){
		sort(m_x, m_y, nstep, true);
	}

	m_size = nstep;
	m_isreg = isreg;
	m_islog = islog;
	m_spl_on = false;
}

double Spline::GetValue(double x, bool istrunc, int *ix, double *truncval)
{
	int index;
	double h, B, A, C, yA, yB;

	if(istrunc){
		if(x > m_x[m_size-1]){
			if(truncval != nullptr){
				return *truncval;
			}
			return m_y[m_size-1];
		}
		else if(x < m_x[0]){
			if(truncval != nullptr){
				return *truncval;
			}
			return m_y[0];
		}
	}

	index = GetIndexXcoord(x);
	if(ix != nullptr){
		*ix = index;
	}
	h = m_x[index+1]-m_x[index];
	A = (m_x[index+1]-x)/h;
	B = (x-m_x[index])/h;
	if(m_islog){
		if(m_y[index] < INFINITESIMAL){
			yA = log(INFINITESIMAL);
		}
		else{
			yA = log(m_y[index]);
		}
		if(m_y[index+1] < INFINITESIMAL){
			yB = log(INFINITESIMAL);
		}
		else{
			yB = log(m_y[index+1]);
		}
	}
	else{
		yA = m_y[index];
		yB = m_y[index+1];
	}
	C = A*yA+B*yB;
	if(m_spl_on){
		C += ((A*A*A-A)*m_y2[index]+(B*B*B-B)*m_y2[index+1])*(h*h)/6.0;
	}
	if(m_islog){
		C = exp(C);
	}
	return C;
}

double Spline::GetLinear(double x, int index)
{
	if(index < 0){
		index = GetIndexXcoord(x);
	}
	double h = m_x[index+1]-m_x[index];
	double A = (m_x[index+1]-x)/h;
	double B = (x-m_x[index])/h;
	double yA = m_y[index];
	double yB = m_y[index+1];
	double C = A*yA+B*yB;
	return C;
}

double Spline::GetOptValue(double x, bool istrunc)
{
	if(istrunc){
		return GetValue(x, istrunc);
	}
	int ix;
	double vspl = GetValue(x, istrunc, &ix);
	if(m_y[ix]*m_y[ix+1] > INFINITESIMAL && m_y[ix]*vspl < INFINITESIMAL){
		return GetLinear(x);
	}
	return vspl;
}

double Spline::Integrate(vector<double> *yint, double Iini)
{
	int nn;
	double dx, sum = Iini;

	if(yint != nullptr){
		(*yint)[0] = Iini;
	}
	for(nn = 0; nn < m_size-1; nn++){
		dx = m_x[nn+1]-m_x[nn];
		sum += 0.5*(m_y[nn]+m_y[nn+1])*dx;
		if(m_spl_on){
			sum += -(m_y2[nn]+m_y2[nn+1])*dx*dx*dx/24.0;
		}
		if(yint != nullptr){
			(*yint)[nn+1] = sum;
		}
	}
	return sum;
}

double Spline::Integrate(double xranger[])
{
	int irange[3];
	double sum = 0.0, h, h3, A, B, A2, B2, xrange[3];

	xrange[1] = max(m_x[0], xranger[0]);
	xrange[2] = min(m_x[m_size-1], xranger[1]);

	irange[1] = SearchIndex(m_size, m_isreg, m_x, xrange[1]);
	irange[2] = min(m_size-1, SearchIndex(m_size, m_isreg, m_x, xrange[2]));

	for(int i = irange[1]; i <= irange[2]; i++){
		if(i == m_size-1){
			break;
		}
		h3 = h = m_x[i+1]-m_x[i];
		h3 *= h*h;
		sum += 0.5*(m_y[i]+m_y[i+1])*h;
		if(m_spl_on){
			sum += -(m_y2[i]+m_y2[i+1])*h3/24.0;
		}
		if(i == irange[1]){
			A = (m_x[i+1]-xrange[1])/h; A2 = A*A;
			B = (xrange[1]-m_x[i])/h; B2 = B*B;
			sum -= 0.5*((1.0-A2)*m_y[i]+B2*m_y[i+1])*h;
			if(m_spl_on){
				sum -= (-(A2*A2-2.0*A2+1.0)*m_y2[i]+(B2*B2-2.0*B2)*m_y2[i+1])*h3/24.0;
			}
		}
		if(i == irange[2]){
			A = (m_x[i+1]-xrange[2])/h; A2 = A*A;
			B = (xrange[2]-m_x[i])/h; B2 = B*B;
			sum -= 0.5*(A2*m_y[i]+(1.0-B2)*m_y[i+1])*h;
			if(m_spl_on){
				sum -= ((A2*A2-2.0*A2)*m_y2[i]-(B2*B2-2.0*B2+1.0)*m_y2[i+1])*h3/24.0;
			}
		}
	}
	return sum;
}

void Spline::GetAveraged(double xrange[], int mesh, vector<double> *yav)
{
	double dx = (xrange[1]-xrange[0])/(double)mesh;
	double dxr[2];

	dxr[0] = xrange[0];
	for(int n = 0; n < mesh; n++){
		dxr[1] = dxr[0]+dx;
		(*yav)[n] = Integrate(dxr)/dx;
		dxr[0] = dxr[1];
	}
}

double Spline::Average()
{
	return Integrate()/(m_x[m_size-1]-m_x[0]);
}

void Spline::AllocateGderiv()
{
	double dx2;

	if(m_dx.size() < m_size){
		m_dx.resize(m_size);
		m_gderiv.resize(m_size);
		for(int n = 0; n < m_size; n++){
			m_gderiv[n].resize(4);
		}
		m_xborder.resize(m_size+1);
	}
	for(int n = 0; n < m_size-1; n++){
		m_dx[n] = m_x[n+1]-m_x[n];
		if(n == 0){
			m_xborder[n] = m_x[n]-m_dx[0]*0.5;
		}
		else{
			m_xborder[n] = (m_x[n]+m_x[n-1])*0.5;
		}
		dx2 = m_dx[n]*m_dx[n];
		m_gderiv[n][0] = m_y[n];
		if(m_spl_on){
			m_gderiv[n][1] = m_y[n+1]-m_y[n]-dx2*(3.0*m_y2[n]+m_y2[n+1])/6.0;
			m_gderiv[n][2] = dx2*m_y2[n];
			m_gderiv[n][3] = dx2*(m_y2[n+1]-m_y2[n]);
		}
		else{
			m_gderiv[n][1] = m_y[n+1]-m_y[n];
			m_gderiv[n][2] = m_gderiv[n][3] = 0;
		}
	}
	m_xborder[m_size] = m_x[m_size-1]+m_dx[m_size-1]*0.5;
	m_isderivalloc = true;
}

int Spline::IntegrateGtEiwtStep(int nini, double x[], double w, double *Gr, double *Gi)
{
	*Gr = *Gi = 0.0;
	if(x[0] > m_xborder[m_size]){
		return nini;
	}

	while(nini < m_size-1 && x[0] > m_xborder[nini+1]){
		nini++;
	}

	int nfin = nini;
	while(nfin < m_size-1 && x[1]> m_xborder[nfin+1]){
		nfin++;
	}

	double xr[2];
	for(int n = nini; n <= nfin; n++){
		xr[0] = max(x[0], m_xborder[n]);
		xr[1] = min(x[1], m_xborder[n+1]);
		if(w > 0){
			*Gr += (sin(w*xr[1])-sin(w*xr[0]))*m_y[n];
			*Gi += -(cos(w*xr[1])-cos(w*xr[0]))*m_y[n];
		}
		else{
			*Gr += (xr[1]-xr[0])*m_y[n];
		}
	}
	if(w > 0){
		*Gr /= w;
		*Gi /= w;
	}

	return nfin;
}

int Spline::IntegrateGtEiwt(int nini, double x[], double w, double *Gr, double *Gi, const char *debug)
{
	double dx, xr[2], Grs, Gis;
	vector<double> gderiv(4);

#ifdef _DEBUG
	ofstream debug_out;
	vector<double> values(6);
	if(debug != nullptr){
		debug_out.open(debug);
	}
#endif

	*Gr = *Gi = 0.0;
	if(x[0] > m_x[m_size-1]){
		return nini;
	}

	int nfin = nini;
	while(nfin < m_size-2 && m_x[nfin+1] < x[1]){
		nfin++;
	}

	for(int n = nini; n <= nfin; n++){
		xr[0] = max(x[0], m_x[n]);
		xr[1] = min(x[1], m_x[n+1]);
		dx = xr[1]-xr[0];
		if(fabs(dx) < INFINITESIMAL){
			continue;
		}
		if(n == nini){
			double dxr = 1.0;
			for(int j = 0; j < 4; j++){
				gderiv[j] = m_gderiv[n][j]/dxr;
				dxr *= m_dx[n];
			}
			double gd2 = gderiv[2];
			double gd1 = gderiv[1];
			double dxi = xr[0]-m_x[n];
			gderiv[2] += gderiv[3]*dxi;
			gderiv[1] += (gderiv[2]+gd2)*dxi/2.0;
			gderiv[0] += dxi*dxi*(gderiv[2]+gd2*2.0)/6.0+gd1*dxi;

			double gd[4];
			gd[0] = GetValue(xr[0]);
			gd[1] = GetDerivativeAt(xr[0]);
			gd[3] = (m_y2[n+1]-m_y2[n])/m_dx[n];
			gd[2] = m_y2[n]+gd[3]*(xr[0]-m_x[n]);

			dxr = 1.0;
			for(int j = 0; j < 4; j++){
				gderiv[j] *= dxr;
				dxr *= dx;
			}
		}
		else{
			double dxr = 1.0;
			for(int j = 0; j < 4; j++){
				gderiv[j] = m_gderiv[n][j]*dxr;
				dxr *= dx/m_dx[n];
			}
		}
		IntegrateGtEiwtSingle(w, xr[0], dx, gderiv, &Grs, &Gis);
		*Gr += Grs;
		*Gi += Gis;
#ifdef _DEBUG
		if(debug != nullptr){
			values[0] = *Gr; values[1] = *Gi;
			for(int i = 0; i < 4; i++){
				values[i+2] = m_gderiv[n][i];
			}
			PrintDebugItems(debug_out, xr[1], values);
		}
#endif
	}
	return nfin;
}

void Spline::IntegrateGtEiwt(double w, double *Gr, double *Gi, const char *debug)
{
	double Grs, Gis;

#ifdef _DEBUG
	ofstream debug_out;
	vector<double> values(6);
	if(debug != nullptr){
		debug_out.open(debug);
	}
#endif

	*Gr = *Gi = 0.0;
	for(int n = 0; n < m_size-1; n++){
		IntegrateGtEiwtSingle(w, m_x[n], m_dx[n], m_gderiv[n], &Grs, &Gis);
		*Gr += Grs;
		*Gi += Gis;
#ifdef _DEBUG
		if(debug != nullptr){
			values[0] = *Gr; values[1] = *Gi;
			for(int i = 0; i < 4; i++){
				values[i+2] = m_gderiv[n][i];
			}
			PrintDebugItems(debug_out, m_x[n+1], values);
		}
#endif
	}
}

void Spline::IntegrateGtEiwtSingle(
	double w, double xini, double dx, vector<double> &gderiv, double *Gr, double *Gi)
{
	double Omega, Omega2, wt, F[4][3], grre, grim, facto, cs, sn;

	Omega = w*dx;
	if(fabs(Omega) < 0.1){
		Omega2 = Omega*Omega;
		F[0][1] = 1.0-Omega2/6.0;
		F[0][2] = Omega/2.0;
		F[1][1] = 0.5-Omega2/8.0;
		F[1][2] = Omega/3.0;
		F[2][1] = 1.0/6.0-Omega2/20.0;
		F[2][2] = Omega/8.0;
		F[3][1] = 1.0/24.0-Omega2/72.0;
		F[3][2] = Omega/30.0;
	}
	else{
		F[0][1] = sin(Omega)/Omega;
		F[0][2] = (1.0-cos(Omega))/Omega;
		facto = 1.0;
		for(int j = 1; j <= 3; j++){
			facto *= (double)j;
			F[j][1] = (-F[j-1][2]+sin(Omega)/facto)/Omega;
			F[j][2] = (F[j-1][1]-cos(Omega)/facto)/Omega;
		}
	}
	grre = grim = 0.0;
	for(int j = 0; j <= 3; j++){
		grre += gderiv[j]*F[j][1];
		grim += gderiv[j]*F[j][2];
	}
	grre *= dx;
	grim *= dx;
	wt = w*xini;
	cs = cos(wt);
	sn = sin(wt);
	*Gr = cs*grre-sn*grim;
	*Gi = sn*grre+cs*grim;	
}

double Spline::GetDerivative(int index)
{
	if(!m_isderivalloc){
		AllocateGderiv();
	}
	return m_gderiv[index][1]/m_dx[index];
}

double Spline::GetDerivativeAt(double x)
{
	int index;
	double h, B, A, yA, yB;

	index = GetIndexXcoord(x);
	h = m_x[index+1]-m_x[index];
	A = (m_x[index+1]-x)/h;
	B = (x-m_x[index])/h;

	yA = m_y[index];
	yB = m_y[index+1];

	return (yB-yA)/h+(
		-(3.0*A*A-1.0)*m_y2[index]+(3.0*B*B-1.0)*m_y2[index+1]
	)*h/6.0;
}

bool Spline::GetPeakValue(int index, double *xp, double *yp, bool ismaxonly)
{
	if(index == 0 || index == m_size-1){
		return false;
	}
	if((m_y[index-1]-m_y[index])*(m_y[index]-m_y[index+1]) > 0.0){
		return false;
	}
	if(ismaxonly && m_y[index] < m_y[index-1]){
		return false;
	}
	*yp = parabloic_peak(xp, m_x[index-1], m_x[index], m_x[index+1], 
				m_y[index-1], m_y[index], m_y[index+1]);
	return true;
}

int Spline::GetPointsInRegion(double xini, double xfin)
{
	return abs(GetIndexXcoord(xfin)-GetIndexXcoord(xini))+1;
}

void Spline::GetArrays(vector<double> *x, vector<double> *y)
{
	if(x != nullptr){
		*x = m_x;
	}
	if(y != nullptr){
		*y = m_y;
	}
}

//------------------------------------------------------------------------------
bool MonotoneSpline::Initialize(vector<double> *x, vector<double> *y, bool isreg, int ndata)
{
	if(ndata < 0){
		if(x->size() != y->size()){
			return false;
		}
		m_size = (int)x->size();
	}
	else{
		if(x->size() < ndata || y->size() < ndata){
			return false;
		}
		m_size = ndata;
	}
	m_isreg = isreg;
	m_x = *x;
	m_y = *y;
	m_yp.resize(m_size, 0.0);
	m_a.resize(m_size, 0.0);
	m_b.resize(m_size, 0.0);

	for(int n = 1; n < m_size; n++){
		if(m_x[n] == m_x[n-1]){
			return false;
		}
	}

	double h0, h1, s0, s1, p;
	h0 = m_x[1]-m_x[0];
	s0 = (m_y[1]-m_y[0])/h0;
	m_yp[0] = s0;
	for(int n = 1; n < m_size-1; n++){
		h1 = m_x[n+1]-m_x[n];
		s1 = (m_y[n+1]-m_y[n])/h1;
		p = (s0*h1+s1*h0)/(h0+h1);
		if(s0*s1 <= 0.0){
			m_yp[n] = 0.0;
		}
		else if(fabs(p) > 2.0*fabs(s0) || fabs(p) > 2.0*fabs(s1)){
			m_yp[n] = 2.0*min(fabs(s0), fabs(s1))*(s0 > 0.0 ? 1.0 : -1.0);
		}
		else{
			m_yp[n] = p;
		}
		m_a[n-1] = (m_yp[n-1]+m_yp[n]-2.0*s0)/h0/h0;
		m_b[n-1] = (3.0*s0-2.0*m_yp[n-1]-m_yp[n])/h0;
		h0 = h1;
		s0 = s1;
	}
	m_yp[m_size-1] = s0;
	m_a[m_size-2] = (m_yp[m_size-2]+m_yp[m_size-1]-2.0*s0)/h0/h0;
	m_b[m_size-2] = (3.0*s0-2.0*m_yp[m_size-2]-m_yp[m_size-1])/h0;
	return true;
}

double MonotoneSpline::GetValue(double x)
{
	int index = SearchIndex(m_size, m_isreg, m_x, x);
	double dx = x-m_x[index];

	return ((m_a[index]*dx+m_b[index])*dx+m_yp[index])*dx+m_y[index];
}

//------------------------------------------------------------------------------
void Spline2D::SetSpline2D(int *nstep,
		vector<double> *x, vector<double> *y, vector<vector<double>> *z, bool islog)
	// (*z)[ix][iy]
{
	if(m_x.size() < nstep[0]){
		m_ztmp.resize(nstep[0]);
		m_splines.resize(nstep[0]);
	}
	m_xmesh = nstep[0];
	m_x = *x;
	m_islog = islog;

	m_splines.resize(m_xmesh);
	for(int n = 0; n < m_xmesh; n++){
		m_splines[n].SetSpline(nstep[1], y, &((*z)[n]), true, islog);
	}
}

double Spline2D::GetValue(double *xy, bool istrunc)
{
	for(int n = 0; n < m_xmesh; n++){
		m_ztmp[n] = m_splines[n].GetValue(xy[1], istrunc);
	}

	m_spltmp.SetSpline(m_xmesh, &m_x, &m_ztmp, true, m_islog);
	return m_spltmp.GetValue(xy[0], istrunc);
}

double Spline2D::GetLinear(double *xy)
{
	for(int n = 0; n < m_xmesh; n++){
		m_ztmp[n] = m_splines[n].GetLinear(xy[1]);
	}

	m_spltmp.Initialize(m_xmesh, &m_x, &m_ztmp, true, m_islog);
	return m_spltmp.GetLinear(xy[0]);
}

double Spline2D::Integrate(const char *debug)
{
	vector<double> yint(m_xmesh);

	for(int n = 0; n < m_xmesh; n++){
		yint[n] = m_splines[n].Integrate();
	}

#ifdef _DEBUG
	if(debug != nullptr){
		ofstream debug_out(debug);
		PrintDebugPair(debug_out, m_x, yint, m_xmesh);
	}
#endif
	return simple_integration(m_xmesh, m_x[2]-m_x[1], yint);
}



