#include <time.h>
#include <math.h>
#include <stdlib.h>
#include "randomutil.h"

double ran1(int *seed)
{
    int j;
    long k;
    static long iy = 0;
    static long iv[NTAB];
    double temp;

    if(*seed <= 0 || !iy){
        if(-(*seed) < 1) *seed = 1;
        else *seed = -(*seed);
        for(j = NTAB+7; j >= 0; j--){
            k = (*seed)/IQ;
            *seed = IA*(*seed-k*IQ)-IR*k;
            if(*seed < 0) *seed += IM;
            if(j < NTAB) iv[j] = *seed;
        }
        iy = iv[0];
    }
    k = (*seed)/IQ;
    *seed = IA*(*seed-k*IQ)-IR*k;
    if(*seed < 0) *seed += IM;
    j = iy/NDIV;
    iy = iv[j];
    iv[j] = *seed;
    if((temp = AM*iy) > RNMX) return RNMX;
    else return temp;
}

double ran2(int *seed)
{
    return 2.0*ran1(seed)-1.0;
}

double gasdev(int *seed, bool isseedrand)
{
    static int iset = 0;
    static double gset;
    double fac, rsq, v1, v2;

    if(*seed < 0){
        iset = 0;
    }

    if(iset == 0){
        do{
            if(isseedrand){
                v1 = 2.0*ran1(seed)-1.0;
                v2 = 2.0*ran1(seed)-1.0;
            }
            else{
                v1 = 2.0*hammv(*seed)-1.0;
                v2 = 2.0*hammv(*seed)-1.0;
            }
            rsq = v1*v1+v2*v2;
        } while(rsq >= 1.0 || rsq == 0.0);
        fac = sqrt(-2.0*log(rsq)/rsq);
        gset = v1*fac;
        iset = 1;
        return v2*fac;
    }
    else {
        iset = 0;
        return gset;
    }
}

double expdev(int *seed)
{
    double dum;

    do{
        dum = ran1(seed);
    } while(dum == 0.0);
    return -log(dum);
}

double hammv(int j)
{
/* uniform hammersley sequence
   reinitializable */

    double xs[27], xsi[27];
    int i1[27], i2[27], jd;
    static int nbase[27] = {0,2,3,5,7,11,13,17,19,23,29,31,37,41,43,
        47,53,59,61,67,71,73,79,83,89,97,101};
    static int i[27] = {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
    static int icall = 0;

    if((icall == 0)  || (j < 0)){
        for(jd = 1; jd <= 26; jd++){
    	    i[jd] = 0;
        }
        icall = 1;
        j = abs(j);
    }

    xs[j] = 0.0;
    xsi[j] = 1.0;
    i[j]++;
    i2[j] = i[j];
    do{
        xsi[j] /= (float)nbase[j];
        i1[j] = i2[j]/nbase[j];
        xs[j] += (i2[j]-nbase[j]*i1[j])*xsi[j];
        i2[j] = i1[j];
    }while(i2[j] > 0);
    return xs[j];
}


int Ham_Base[HAMMBBASEMAX+1] =
    {0,2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101};

long RandomUtility::Init()
{
    long seed = (long)time(NULL);
    Init(seed);
	return seed;
}

void RandomUtility::Init(int seed)
{
    int j, k;
    m_idum = abs(seed);
    for(j = NTAB+7; j >= 0; j--){
        k = m_idum/IQ;
        m_idum = IA*(m_idum-k*IQ)-IR*k;
        if(m_idum < 0){
            m_idum += IM;
        }
        if(j < NTAB){
            m_iv[j] = m_idum;
        }
    }
    m_iy = m_iv[0];
    m_iset = 0;

    for(j = 1; j <= HAMMBBASEMAX; j++){
        m_i[j] = 0;
    }
}

double RandomUtility::Uniform(double ini, double fin)
{
    return (fin-ini)*f_Uniform01()+ini;
}

double RandomUtility::Gauss(bool isrand, int index)
{
    double fac, rsq, v1, v2;

    if(m_iset == 0){
        do{
            if(isrand || index == 0){
                v1 = 2.0*f_Uniform01()-1.0;
                v2 = 2.0*f_Uniform01()-1.0;
            }
            else{
                v1 = 2.0*Hammv(index)-1.0;
                v2 = 2.0*Hammv(index)-1.0;
            }
            rsq = v1*v1+v2*v2;
        } while(rsq >= 1.0 || rsq == 0.0);
        fac = sqrt(-2.0*log(rsq)/rsq);
        m_gset = v1*fac;
        m_iset = 1;
        return v2*fac;
    }
    else{
        m_iset = 0;
    }
    return m_gset;
}

double RandomUtility::Expon()
{
    double dum;

    do{
        dum = f_Uniform01();
    } while(dum == 0.0);
    return -log(dum);
}

void RandomUtility::AdvanceSeedNumber(int repnumbers[])
{
	for(long n = 0; n < repnumbers[0]; n++){
		f_Uniform01();
	}

    for(int j = 1; j <= HAMMBBASEMAX; j++){
		for(long n = 0; n < repnumbers[j]; n++){
			Hammv(j);
		}
	}
}

double RandomUtility::Hammv(int index)
{
    double xs[HAMMBBASEMAX+1], xsi[HAMMBBASEMAX+1];
    int i1[HAMMBBASEMAX+1], i2[HAMMBBASEMAX+1], j;

    j = abs(index);

	//m_repnumbers[j]++;

	xs[j] = 0.0;
    xsi[j] = 1.0;
    m_i[j]++;
    i2[j] = m_i[j];
    do{
        xsi[j] /= (float)Ham_Base[j];
        i1[j] = i2[j]/Ham_Base[j];
        xs[j] += (i2[j]-Ham_Base[j]*i1[j])*xsi[j];
        i2[j] = i1[j];
    }while(i2[j] > 0);
    return xs[j];
}

double RandomUtility::f_Uniform01()
{
    int j, k;
    double temp;

	//m_repnumbers[0]++;

    k = m_idum/IQ;
    m_idum = IA*(m_idum-k*IQ)-IR*k;
    if(m_idum < 0) m_idum += IM;
    j = m_iy/NDIV;
    m_iy = m_iv[j];
    m_iv[j] = m_idum;
    if((temp = AM*(double)m_iy) > RNMX){
        return RNMX;
    }
    return temp;
}

