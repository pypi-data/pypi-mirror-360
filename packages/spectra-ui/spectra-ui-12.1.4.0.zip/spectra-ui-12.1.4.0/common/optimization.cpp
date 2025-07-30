#include <algorithm>
#include <stdlib.h>
#include <time.h>
#include "optimization.h"
#include "common.h"
#include "numerical_common_definitions.h"
#include "randomutil.h"

//------------------------------------------------------------------------------

#define INITIAL_OEPRATIONS_FOR_TINI 100

SimulatedAnnealing::SimulatedAnnealing(long *seed)
{
    if(seed == NULL){
        m_seed = -(long)time(NULL);
    }
    else{
        m_seed = -abs((int)(*seed));
    }
    m_canceled = false;
}

void SimulatedAnnealing::DoAnnealing(double Tratio, int repeats)
{
    int Nrep, Nrej, Nacc, Nfix, Nfixmax, i;
    double cost_curr, cost_ini, cost;
    double Tini, T, dE;

    m_currfrac = 1.0;
    m_repeats = 0;

    Initialize();
    m_costmin = cost_ini = CostFunc();
    Tini = 0.0;
    for(i = 1; i <= INITIAL_OEPRATIONS_FOR_TINI; i++){
        Operation();
        Tini += fabs(cost_ini-CostFunc());
        Undo();
    }

    Tini /= INITIAL_OEPRATIONS_FOR_TINI;

    T = Tini;
    Nrep = 0;
    Nrej = 0;
    Nacc = 0;
    Nfix = 0;
    Nfixmax = 5;
    cost_curr = cost_ini;

    do {
        m_currfrac = T/Tini;
        Operation();
        cost = CostFunc();
        m_repeats = max(Nacc, Nrej);
        dE = cost-cost_curr;
        if(f_Judge(dE, T)){
            cost_curr = cost;
            m_costmin = min(m_costmin, cost);
            Nacc++;
            if(Nacc >= repeats){
                Nrep++;
                T = Tini*exp(-((double)Nrep)/10.0);
                Nrej = 0;
                Nacc = 0;
            }
        }
        else{
            Undo();
            Nrej++;
            if(Nrej >= repeats){
                Nrep++;
                T = Tini*exp(-((double)Nrep)/10.0);
                if(Nacc == 0){
                    Nfix++;
                }
                else{
                    Nfix=0;
                }
                Nrej=0;
                Nacc=0;
            }
        }
    }while(!m_canceled && (Nfix <= Nfixmax) && (T/Tini > Tratio));
}

bool SimulatedAnnealing::f_Judge(double dE, double T)
{
    double random, exval;

    if(dE < 0.0){
        return true;
    }
    else {
        exval = exp(-dE/T);
        random = ran1(&m_seed);
        if(exval > random){
            return true;
        }
    }
    return false;
}

#undef INITIAL_OEPRATIONS_FOR_TINI

//------------------------------------------------------------------------------
DownhillSimplex::DownhillSimplex(int ndim)
{
    AssignDimension(ndim);
}

void DownhillSimplex::AssignDimension(int ndim)
{
    m_ndim = ndim;
    m_psum.resize(m_ndim+1);
    m_ptry.resize(m_ndim+1);
    m_nstatusmax = 0;
}

bool DownhillSimplex::Amoeba(bool isshowstatus,
    vector<vector<double>> *p, vector<double> *y,
    int nmax, int contype, double ftol, vector<double> *eps, int *nfunk)
{
    int i, ihi, ilo, inhi, j, nstatus;
    double rtol, rtol0 = -1.0, ysave, ytry;
    vector<double> ptmp(m_ndim+1);
    bool result, isconv;

    *nfunk = 0;

    f_GetPsum(p);
    for(;;){
        ilo = 1;
        ihi = (*y)[1] > (*y)[2] ? (inhi = 2, 1) : (inhi = 1, 2);
        for(i = 1; i <= m_ndim+1; i++){
            if((*y)[i] <= (*y)[ilo]) ilo = i;
            if((*y)[i] > (*y)[ihi]){
                inhi = ihi;
                ihi = i;
            }
            else if((*y)[i] > (*y)[inhi] && i != ihi)
            inhi = i;
        }
        if(contype == AmoebaSerachMinimum){
            rtol = 2.0*fabs((*y)[ihi]-(*y)[ilo])/(fabs((*y)[ihi])+fabs((*y)[ilo]+1e-3));
        }
        else{
            rtol = fabs((*y)[ihi]); // search a solution of equation;
        }
        if(rtol0 < 0){
            rtol0 = rtol;
        }
        if(rtol < ftol){
            isconv = true;
            if(eps != NULL){
                for(i = 1; i <= m_ndim; i++){
                    for(j = 1; j <= m_ndim+1; j++){
                        ptmp[j-1] = (*p)[j][i];
                    }
                    ptmp -= vectorsum(ptmp, -1)/(double)(m_ndim+1);
                    if(max(fabs(minmax(ptmp, true)), fabs(minmax(ptmp, false))) > (*eps)[i]){
                        isconv = false;
                        break;
                    }
                }
            }
            if(isconv){
                swap((*y)[1], (*y)[ilo]);
                for(i = 1; i <= m_ndim; i++){
                    swap((*p)[1][i], (*p)[ilo][i]);
                }
                result = true;
                break;
            }
        }
        if(*nfunk >= nmax){
            result = false;
            break;
        }
        *nfunk += 2;
        ytry = f_Try(p, y, ihi, -1.0);

        if(ytry <= (*y)[ilo]){
            ytry = f_Try(p, y, ihi, 2.0);
        }
        else if(ytry >= (*y)[inhi]){
            ysave = (*y)[ihi];
            ytry = f_Try(p, y, ihi, 0.5);
            if(ytry >= ysave){
                for(i = 1; i <= m_ndim+1; i++){
                    if(i != ilo){
                        for(j = 1; j <= m_ndim; j++){
                            (*p)[i][j] = m_psum[j] = 0.5*((*p)[i][j]+(*p)[ilo][j]);
                        }
                        (*y)[i] = CostFunc(&m_psum);
                    }
                }
                *nfunk += m_ndim;
                f_GetPsum(p);
            }
        }

        if(isshowstatus){
            nstatus = (int)floor(100*(1.0-log(ftol/rtol)/log(ftol/rtol0)));
			nstatus = max(nstatus, 100*(*nfunk)/nmax);
            if(nstatus < 0) nstatus = 0;
            if(nstatus > 100) nstatus = 100;
            if(nstatus > m_nstatusmax){
                m_nstatusmax = nstatus;
            }

            if(!ShowStatusGetCont(m_nstatusmax)){
                result = false;
                break;
            }
        }
        else --(*nfunk);
    }

    if(isshowstatus){
        ShowStatusGetCont(100);
    }
    return result;
}

double DownhillSimplex::f_Try(vector<vector<double>> *p, vector<double> *y,
    int ihi, double fac)
{
    int j;
    double fac1, fac2, ytry;

    fac1 = (1.0-fac)/m_ndim;
    fac2 = fac1-fac;
    for(j = 1; j <= m_ndim; j++){
        m_ptry[j] = m_psum[j]*fac1-(*p)[ihi][j]*fac2;
    }
    ytry = CostFunc(&m_ptry);
    if(ytry <(*y)[ihi]){
        (*y)[ihi] = ytry;
        for(j = 1; j <= m_ndim; j++){
            m_psum[j] += m_ptry[j]-(*p)[ihi][j];
            (*p)[ihi][j] = m_ptry[j];
        }
    }
    return ytry;
}


void DownhillSimplex::f_GetPsum(vector<vector<double>> *p)
{
    double sum;
    int j, i;

    for(j = 1; j <= m_ndim; j++){
        for (sum = 0.0, i = 1; i <= m_ndim+1; i++){
            sum += (*p)[i][j];
        }
        m_psum[j] = sum;
    }
}

//------------------------------------------------------------------------------
#define JMAXINTPOL 40
#define ITMAX 20
#define JMAX 40
#define CGOLD 0.381966
#define ZEPS 1.0e-10
#define SHFT(a,b,c,d) (a)=(b);(b)=(c);(c)=(d);

SearchMinimum::SearchMinimum()
{
}

#define SIGN(a,b) ((b) >= 0.0 ? fabs(a) : -fabs(a))

void SearchMinimum::BrentMethod(double ax, double bx, double cx,
    double tol, bool ischeckrel, double tolval, double *xmin, vector<double> *ymin)
{
    int iter;
    double a, b, etemp, fu, fv, fw, fx, p, q, r, tol1, tol2, u, v, w, x, xm;
    double e = 0.0, d = 0.0;

    a = (ax < cx ? ax : cx);
    b = (ax > cx ? ax : cx);
    x = w = v = bx;
    fw = fv = fx = CostFunc(x, ymin);
    for(iter = 1; iter <= ITMAX; iter++){
        xm = 0.5*(a+b);
        tol2 = 2.0*(tol1 = tol*fabs(x)+ZEPS);
        if(fabs(x-xm) <= (tol2-0.5*(b-a)) && iter > 2 &&
                !(ischeckrel && max(fabs(fx-fw), fabs(fx-fv)) > max(fabs(fx), fabs(fw))*tolval)){
            *xmin = x;
            CostFunc(x, ymin);
            return;
        }
        if(fabs(e) <= tol1 || iter < 3){
            d = CGOLD*(e = (x >= xm ? a-x : b-x));
        }
        else{
            r = (x-w)*(fx-fv);
            q = (x-v)*(fx-fw);
            p = (x-v)*q-(x-w)*r;
            q = 2.0*(q-r);
            if(q > 0.0){
                p = -p;
            }
            q = fabs(q);
            etemp = e;
            e = d;
            if(fabs(p) >= fabs(0.5*q*etemp) || p <= q*(a-x) || p >= q*(b-x)){
                d = CGOLD*(e = (x >= xm ? a-x : b-x));
            }
            else{
                d = p/q;
                u = x+d;
                if(!ischeckrel){
                    if(u-a < tol2 || b-u < tol2){
                        d = SIGN(tol1, xm-x);
                    }
                }
            }
        }
        if(ischeckrel){
            u = x+d;
        }
        else{
            u = (fabs(d) >= tol1 ? x+d : x+SIGN(tol1, d));
        }
        fu = CostFunc(u, ymin);
        if(fu <= fx){
            if(u >= x){
                a = x;
            }
            else{
                b = x;
            }
            SHFT(v, w, x, u);
            SHFT(fv, fw, fx, fu);
        }
        else{
            if(u < x){
                a = u;
            }
            else{
                b = u;
            }
            if(fu <= fw || w == x){
                v = w;
                w = u;
                fv = fw;
                fw = fu;
            }
            else if(fu <= fv || v == x || v == w){
                v = u;
                fv = fu;
            }
        }
    }
    *xmin = x;
}

double SearchMinimum::GetSolutionRtbis(double ytgt, double x1, double x2,
    double *xacc, double *yacc)
{
    int j;
    double dx, f, fmid, xmid, rtb;
    bool isconv;

    f = CostFunc(x1, NULL)-ytgt;
    if(f == 0.0){
        return x1;
    }
    fmid = CostFunc(x2, NULL)-ytgt;
    if(fmid == 0.0){
        return x2;
    }
    if(f*fmid > 0.0){
        return 0.5*(x1+x2);
    }
    rtb = f < 0.0 ? (dx = x2-x1, x1) : (dx = x1-x2, x2);
    for(j = 1; j <= JMAXINTPOL; j++){
        fmid = CostFunc(xmid = rtb + (dx *= 0.5), NULL)-ytgt;
        if(fabs(fmid) < INFINITESIMAL){
            break;
        }
        if(fmid <= 0.0) rtb = xmid;
        isconv = xacc != NULL ? fabs(dx) < (*xacc) : true;
        isconv = isconv && (yacc != NULL ? fabs(fmid) < (*yacc) : true);
        if(isconv){
            break;
        }
    }
    return xmid;
}

#undef JMAXINTPOL
#undef ITMAX
#undef JMAX
#undef CGOLD
#undef ZEPS
#undef SHFT
#undef SIGN

//------------------------------------------------------------------------------
MakeTrendMap::MakeTrendMap()
{
}

void MakeTrendMap::SetData(vector<double> *data, int offset, int ndata)
{
    if(ndata <= 0){
        ndata = (int)data->size()-offset;
    }
    m_data.resize(ndata);
    for(int n = 0; n < ndata; n++){
        m_data[n] = (*data)[n+offset];
    }
    m_ndata = ndata;
}

void MakeTrendMap::GetTrend(int iavg, double eps, int type,
    vector<int> *xpos, vector<double> *ypos)
{
    int i1 = iavg, i2 = m_ndata-1-iavg, iposmax;
    double dv;
    vector<int> ipos;

    ipos.push_back(iavg);
    do{
        f_SetFixedPoint(iavg, i1, i2);
        dv = f_GetDeviation(iavg, type, &iposmax);
        if(dv > eps){
            i2 = iposmax;
        }
        else{
            if(i2 < m_ndata-1-iavg){
                ipos.push_back(i2);
            }
            i1 = i2;
            i2 = m_ndata-1-iavg;
        }
    }while(i1 < i2);
    ipos.push_back(m_ndata-1-iavg);

    if(xpos->size() < ipos.size()){
        xpos->resize(ipos.size());
        ypos->resize(ipos.size());
    }
    for(int n = 0; n < (int)ipos.size(); n++){
        (*xpos)[n] = ipos[n];
        (*ypos)[n] = GetAverage(iavg, ipos[n]);
    }
}

void MakeTrendMap::GetTrend(int iavg, vector<int> *ipos, vector<double> *ypos)
{
    if(ypos->size() != ipos->size()){
        ypos->resize(ipos->size());
    }
    for(int n = 0; n < (int)ipos->size(); n++){
        (*ypos)[n] = GetAverage(iavg, (*ipos)[n]);
    }
}

double MakeTrendMap::GetCurrentTrend(int ipos)
{
    return m_vfix[1]+(m_vfix[2]-m_vfix[1])/(double)(m_ifix[2]-m_ifix[1])
        *(double)(ipos-m_ifix[1]);
}

double MakeTrendMap::GetAverage(int iavg, int ipos)
{
    double avg = 0.0;
    int ini, fin;

    ini = max(0, ipos-iavg);
    fin = min(m_ndata-1, ipos+iavg);

    for(int i = ini; i <= fin; i++){
        avg += m_data[i];
    }
    return avg/(double)(fin-ini+1);
}

//----- private functions -----
double MakeTrendMap::f_GetDeviation(int iavg, int type, int *iposmax)
{
    double average = 0.0, devmax = 0.0, diff, data;

    *iposmax = m_ifix[1];
    for(int i = m_ifix[1]; i <= m_ifix[2]; i++){
        data = GetAverage(iavg, i);
        diff = fabs(data-GetCurrentTrend(i));
        average += diff;
        if(diff > devmax){
            devmax = diff;
            *iposmax = i;
        }
    }
    average /= (double)(m_ifix[2]-m_ifix[1]+1);
    return type == MakeTrendMapMaxDeviation ? average : devmax;
}


void MakeTrendMap::f_SetFixedPoint(int iavg, int ipos1, int ipos2)
{
    m_ifix[1] = ipos1; m_ifix[2] = ipos2;
    m_vfix[1] = GetAverage(iavg, ipos1);
    m_vfix[2] = GetAverage(iavg, ipos2);
}
