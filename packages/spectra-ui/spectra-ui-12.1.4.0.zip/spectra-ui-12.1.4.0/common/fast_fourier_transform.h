#ifndef fast_fourier_transform_h
#define fast_fourier_transform_h

class FastFourierTransform
{
public:
    FastFourierTransform(int dimension, int n1, int n2 = 0);
    ~FastFourierTransform();
    void SetFFTWorkSpace(int dimension, int n1, int n2 = 0);
    void DoFFT(double *data, int direction = 1);
    void DoRealFFT(double *data, int direction = 1);
	void DoFFTFilter(double *data, double cutoff, bool isgauss = false, bool isauto = false);
    void DoFFTFilter2D(double **data, double cutoff[], bool isgauss);
    void DoCosFT(double *data);
    void DoFFT(double **data, int direction = 1);
	void DoRealFFT(double **data, int direction = 1);
	int GetNfft(int ixy);
private:
    double *m_w;
    double *m_t;
    int *m_ip;
    int m_dimension;
    int m_n1;
    int m_n2;
};

#endif
