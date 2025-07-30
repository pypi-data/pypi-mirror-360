#include <math.h>
#include <algorithm>
#include "fast_fourier_transform.h"
#include "common.h"
#include "numerical_common_definitions.h"

using namespace std;

FastFourierTransform::FastFourierTransform(int dimension, int n1, int n2)
{
    m_n1 = m_n2 = -1;
    m_t = m_w = NULL;
    m_ip = NULL;
	m_dimension = dimension;
    SetFFTWorkSpace(dimension, n1, n2);
}

FastFourierTransform::~FastFourierTransform()
{
    if(m_w != NULL){
        free(m_w);
    }
    free(m_ip);
    if(m_dimension == 2){
        if(m_t != NULL){
            free(m_t);
        }
    }
}

void FastFourierTransform::SetFFTWorkSpace(int dimension, int n1, int n2)
{
    int nip, nw;

    if(n1 == m_n1 && n2 == m_n2) return;

    m_n1 = n1;
    m_n2 = n2;

    if(dimension > 1){
        m_dimension = 2;
        m_t = (double *)realloc_chk(m_t, sizeof(double)*(8*n1+1));
    }
    else{
        m_dimension = 1;
        m_t = (double *)realloc_chk(m_t, sizeof(double)*(n1+1));
    }
    nw = max(n1, n2);
    m_w = (double *)realloc_chk(m_w, sizeof(double)*(nw+1));
    nip = (int)(2+sqrt((double)max(n1, n2)));
    m_ip = (int *)realloc_chk(m_ip, sizeof(int)*(nip+1));
    m_ip[0] = 0;
}

void FastFourierTransform::DoFFT(double *data, int direction)
{
    void cdft(int n, int isgn, double *a, int *ip, double *w);
    cdft(2*m_n1, direction, data, m_ip, m_w);
}

void FastFourierTransform::DoRealFFT(double *data, int direction)
{
    void rdft(int n, int isgn, double *a, int *ip, double *w);
    rdft(m_n1, direction, data, m_ip, m_w);
}

void FastFourierTransform::DoFFTFilter(double *data, double cutoff, bool isgauss, bool isauto)
{
	int nc;
	DoRealFFT(data, 1);
	if(isauto){
		double sum = 0;
		for(int n = 1; n < m_n1/2; n++){
			sum += sqrt(hypotsq(data[2*n], data[2*n+1]));
		}
		double sumr = 0 ;
		nc = 0;
		for(int n = 1; n < m_n1/2; n++){
			sumr += sqrt(hypotsq(data[2*n], data[2*n+1]));
			if(sumr > cutoff*sum){
				nc = n;
				break;
			}
		}
	}
	if(isgauss){
		for(int n = 0; n < m_n1/2; n++){
			double tex = (double)n/m_n1/cutoff;
			tex *= 2.0*PI*PI*tex;
			if(tex > MAXIMUM_EXPONENT){
				data[2*n] = 0;
				data[2*n+1] = 0;
			}
			else{
				double coef = 2.0/(double)m_n1*exp(-tex);
				data[2*n] *= coef;
				if(n == 0){
					tex = 0.5/cutoff;
					tex *= 2.0*PI*PI*tex;
					coef = 2.0/(double)m_n1*exp(-tex);
					data[1] *= coef;
				}
				else{
					data[2*n+1] *= coef;
				}				
			}
		}
	}
	else{
		if(isauto == false){
			nc = (int)floor(m_n1/2*cutoff);
		}
		if(nc < m_n1/2){
			data[1] = 0;
		}
		for(int n = 0; n < m_n1/2; n++){
			if(n >= nc){
				data[2*n] = 0;
				data[2*n+1] = 0;
			}
			else{
				data[2*n] *= 2.0/(double)m_n1;
				data[2*n+1] *= 2.0/(double)m_n1;
			}
		}
	}
	DoRealFFT(data, -1);
}


void FastFourierTransform::DoFFTFilter2D(double **data, double cutoff[], bool isgauss)
// data should be data[0~n1][0~2*n2]
{
	int nc[2], ni, mi;
	double texn, texm, tex;
	DoFFT(data, 1);
	if(isgauss){
		for(int n = 0; n < m_n1; n++){
			ni = fft_index(n, m_n1, 1);
			texn = (double)ni/m_n1/cutoff[0];
			for (int m = 0; m < m_n2; m++){
				mi = fft_index(m, m_n2, 1);
				texm = (double)mi/m_n2/cutoff[1];
				tex = 2.0*PI*PI*hypotsq(texn, texm);
				if (tex > MAXIMUM_EXPONENT){
					data[n][2*m] = data[n][2*m+1] = 0;
				}
				else{
					double coef = 1.0/(double)(m_n1*m_n2)*exp(-tex);
					data[n][2*m] *= coef;
					data[n][2*m+1] *= coef;
				}
			}
		}
	}
	else{
		nc[0] = (int)floor(m_n1/2*cutoff[0]);
		nc[1] = (int)floor(m_n2/2*cutoff[1]);
		for(int n = 0; n < m_n1; n++){
			ni = abs(fft_index(n, m_n1, 1));
			for (int m = 0; m < m_n2; m++){
				mi = abs(fft_index(m, m_n2, 1));
				if (ni >= nc[0] || mi >= nc[1]){
					data[n][2*m] = data[n][2*m+1] = 0;
				}
				else{
					double coef = 1.0/(double)(m_n1*m_n2);
					data[n][2*m] *= coef;
					data[n][2*m+1] *= coef;
				}
			}
		}
	}
	DoFFT(data, -1);
}

int FastFourierTransform::GetNfft(int ixy)
{
	return ixy == 1 ? m_n1 : m_n2;
}

void FastFourierTransform::DoCosFT(double *data)
{
    void dfct(int n, double *a, double *t, int *ip, double *w);
    dfct(m_n1, data, m_t, m_ip, m_w);
}

void FastFourierTransform::DoFFT(double **data, int direction)
{
    void cdft2d(int n1, int n2, int isgn, double **a, double *t, int *ip, double *w);
    cdft2d(m_n1, 2*m_n2, direction, data, m_t, m_ip, m_w);
}

void FastFourierTransform::DoRealFFT(double **data, int direction)
{
	void rdft2d(int n1, int n2, int isgn, double **a, double *t, int *ip, double *w);
	rdft2d(m_n1, m_n2, direction, data, m_t, m_ip, m_w);
}
