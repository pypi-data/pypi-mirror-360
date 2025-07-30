#ifndef randomutil_h
#define randomutil_h

#define IA 16807
#define IM 2147483647
#define AM (1.0/IM)
#define IQ 127773
#define IR 2836
#define NTAB 32
#define NDIV (1+(IM-1)/NTAB)
#define EPS 1.2e-7
#define RNMX (1.0-EPS)
#define HAMMBBASEMAX 26

double ran1(int *seed);
double ran2(int *seed);
double gasdev(int *seed, bool isseedrand = true);
double expdev(int *seed);
double hammv(int j);

class RandomUtility
{
public:
    long Init();
    void Init(int seed);
    double Uniform(double ini, double fin);
    double Gauss(bool isrand, int index = 0);
    double Expon();
    double Hammv(int index);
	void AdvanceSeedNumber(int repnumbers[]);
private:
    double f_Uniform01();
    long m_idum;
    long m_iy;
    long m_iv[NTAB];
    int m_iset;
    double m_gset;
    int m_i[HAMMBBASEMAX+1];
};


#endif

