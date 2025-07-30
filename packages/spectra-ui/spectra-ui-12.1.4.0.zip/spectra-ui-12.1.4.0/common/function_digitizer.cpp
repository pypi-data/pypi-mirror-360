#include <algorithm>
#include "function_digitizer.h"
#include "numerical_common_definitions.h"
#include "common.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

FunctionDigitizer::FunctionDigitizer()
{
	m_allocsize = 0;
	m_nitems = -1;
	m_allocsize = 0;
	m_isinitialized = m_cancelfstepper = false;
}

FunctionDigitizer::FunctionDigitizer(int nitems)
{
	m_allocsize = 0;
	m_nitems = -1;
	AllocateMemoryFuncDigitizer(nitems);
	m_isinitialized = m_cancelfstepper = false;
}

void FunctionDigitizer::AllocateMemoryFuncDigitizer(int nitems)
{
	m_size = 0;
	if(m_isinitialized == true && m_nitems == nitems){
		return;
	}
	Free();
	m_nitems = nitems;
	m_ytmp.resize(m_nitems);
	m_yvecarray.resize(m_nitems);
	m_wsyvec.resize(m_nitems);

	m_wsy = nullptr;
	for(int ni = 0; ni < m_nitems; ni++){
		m_yvecarray[ni] = m_wsyvec[ni] = nullptr;
	}
	m_allocsize = 0;
	m_isinitialized = true;
}

void FunctionDigitizer::Free()
{
	if(m_allocsize > 0){
		free(m_wsy);
		for(int ni = 0; ni < m_nitems; ni++){
			free(m_yvecarray[ni]);
			free(m_wsyvec[ni]);
		}
	}
}

FunctionDigitizer::~FunctionDigitizer()
{
	Free();
}

void FunctionDigitizer::f_Resize(int arraysize)
{
	if(m_allocsize <= arraysize){
		m_allocsize = arraysize+NUMBER_OF_MEMORY_EXPANSION;
		m_index.resize(m_allocsize);
		m_indices.resize(m_allocsize);
		m_xarray.resize(m_allocsize);
		m_yarray.resize(m_allocsize);
		m_y1st.resize(m_allocsize);
		m_wsx.resize(m_allocsize);
		int lsize = (m_allocsize)*sizeof(double);
		m_wsy = (double *)realloc_chk(m_wsy, lsize);
		for(int ni = 0; ni < m_nitems; ni++){
			m_yvecarray[ni] = (double *)realloc_chk(m_yvecarray[ni], lsize);
			m_wsyvec[ni] = (double *)realloc_chk(m_wsyvec[ni], lsize);
		}
	}
}

void FunctionDigitizer::f_InsertItem(int index, double x, double *y, vector<double> *yvec)
{
	int ni, n;

	m_size++; f_Resize(m_size);
	for(n = m_size-1; n > index; n--){
		m_index[n] = m_index[n-1];
	}
	m_index[index] = m_size-1;

	m_xarray[m_size-1] =  x;
	if(y == nullptr){
		m_yarray[m_size-1] = Function4Digitizer(x, &m_ytmp);
	}
	else{
		m_yarray[m_size-1] = *y;
	}

	m_y1st[m_size-1] = f_yd(index)/f_xd(index);
	if(index > 0){ // modify the (index+1)-th derivative
		m_y1st[m_index[index+1]] = f_yd(index+1)/f_xd(index+1);
	}
	for(ni = 0; ni < m_nitems; ni++){
		if(y == nullptr){
			m_yvecarray[ni][m_size-1] = m_ytmp[ni];
		}
		else{
			m_yvecarray[ni][m_size-1] = (*yvec)[ni];
		}
	}
}

double FunctionDigitizer::f_xd(int index)
{
	return m_xarray[m_index[index]]-m_xarray[m_index[index-1]];
}

double FunctionDigitizer::f_yd(int index)
{
	return m_yarray[m_index[index]]-m_yarray[m_index[index-1]];
}

double FunctionDigitizer::f_y1std(int index)
{
	if(index >= m_size){
		index = m_size-1;
	}
	return m_y1st[m_index[index+1]]-m_y1st[m_index[index]];
}

int FunctionDigitizer::RunDigitizer(
	int level, vector<double> *x, vector<vector<double>> *y,
	double *xrange, int ninit, double *epsval,
	PrintCalculationStatus *status, int targetlayer,
	string debug, vector<double> *integ, bool istruncate, 
	int rank, int mpiprocesses, MPIbyThread *thread)
{
	int ni, nn, ndiv, nstep, nr, nini, nfin;
	double xini, xfin, xref, dx0, xminlim, eps, epsneg, epslog;
	double dx, dx1, dx2, dsq, dymax, finestep, ymax, ymin, ystemp;

	xini = xrange[FstepXini];
	xfin = xrange[FstepXfin];

	if(fabs(xini-xfin) < INFINITESIMAL){
		if(x->size() < 2){
			x->resize(2);
		}
		if(y->size() < m_nitems){
			y->resize(m_nitems);
		}
		for(ni = 0; ni < m_nitems; ni++){
			if((*y)[ni].size() < 2){
				(*y)[ni].resize(2);
			}
		}
		Function4Digitizer(xini, &m_ytmp);
		(*x)[0] = (*x)[1] = xini;
		for(ni = 0; ni < m_nitems; ni++){
			(*y)[ni][0] = (*y)[ni][1] = m_ytmp[ni];
		}
		return 1;
	}

	xref = xrange[FstepXref];
	dx0 = xrange[FstepDx];
	xminlim = xrange[FstepXlim];
	eps = epsval[0];
	epsneg = epsval[1]; 
		// epsneg = 0 means no limit for the logarithmic reference
	epslog = 2.0+eps*10.0;

	if(level&FUNC_DIGIT_DX_ALLOCATED){
		dx = (xfin > xini ? 1.0 : -1.0)*fabs(dx0);
		ninit = (int)floor(fabs((xfin-xini)/dx0)+0.5)+1;
	}
	f_Resize(ninit); m_size = ninit;

	if(level&FUNC_DIGIT_XINI_ALLOC){
		for(nn = 0; nn < ninit; nn++){
			m_xarray[nn] = (*x)[nn];
		}
	}
	else{
		if(!(level&FUNC_DIGIT_DX_ALLOCATED)){
			dx = (xfin-xini)/(double)(ninit-1);
		}
		if((xref-xini)*(xref-xfin) > -fabs(dx)*LIMIT_RATIO_XREF_IGNORE){
			xref = xini;
			ndiv = 1;
			dx1 = dx2 = dx;
		}
		else{
			if(fabs(xref-xini) < fabs(xfin-xref)){
				ndiv = (int)ceil(fabs((xref-xini)/dx))+1;
			}
			else{
				ndiv = ninit-(int)ceil(fabs((xref-xfin)/dx))-1;
			}
			if(ndiv == 1){
				dx1 = 0.0;
			}
			else{
				dx1 = (xref-xini)/(double)(ndiv-1);
			}
			if(ninit == ndiv){
				dx2 = 0.0;
			}
			else{
				dx2 = (xfin-xref)/(double)(ninit-ndiv);
			}
		}
		for(nn = 0; nn < ndiv; nn++){
			m_xarray[nn] = xini+(double)nn*dx1;
		}
		for(nn = ndiv; nn < ninit; nn++){
			m_xarray[nn] = xref+(double)(nn+1-ndiv)*dx2;
		}
	}

	int ndsd = 1;
	if(status != nullptr){
		if(level&FUNC_DIGIT_BASE){
			ndsd++;
		}
		if(level&FUNC_DIGIT_ENABLE_LOG){
			ndsd++;
		}
		status->SetSubstepNumber(targetlayer, ndsd*ninit);
	}

	if(mpiprocesses > 1 && !(level&FUNC_DIGIT_YINI_ALLOC)){
		f_ComputeFuncMPI(ninit, ninit, m_xarray, 
			rank, mpiprocesses, thread, status, targetlayer, 0);
		for(nn = 0; nn < ninit; nn++){
			m_yarray[nn] = m_wsy[nn];
			for(ni = 0; ni < m_nitems; ni++){
				m_yvecarray[ni][nn] = m_wsyvec[ni][nn];
			}
		}
	}
	if(mpiprocesses > 1){
		MPI_Barrier(MPI_COMM_WORLD);
	}

	for(nn = 0; nn < ninit; nn++){
		m_index[nn] = nn;
		if(level&FUNC_DIGIT_YINI_ALLOC){
			m_yarray[nn] = (*y)[0][nn];
			for(ni = 0; ni < m_nitems; ni++){
				m_yvecarray[ni][nn] = (*y)[ni][nn];
			}
		}
		else if(mpiprocesses <= 1){
			m_yarray[nn] = Function4Digitizer(m_xarray[nn], &m_ytmp);
			for(ni = 0; ni < m_nitems; ni++){
				m_yvecarray[ni][nn] = m_ytmp[ni];
			}
		}
		if(m_cancelfstepper){
			ninit = nn;
			break;
		}
		if(nn == 0){
			ymax = ymin = m_yarray[nn];
			m_y1st[1] = 0.0;
		}
		else{
			ymax = max(ymax, m_yarray[nn]);
			ymin = min(ymin, m_yarray[nn]);
		}
		if(nn > 0){
			m_y1st[nn] = f_yd(nn)/f_xd(nn);
		}
		if(status != nullptr){
			status->PutSteps(targetlayer, nn);
		}
	}
	nstep = ninit;
	dymax = ymax-ymin;

	int nins;
	bool linng = false, logng = false, stepng = false;
	do{
		nins = 0;
		for(nn = 1; nn < nstep && dymax > INFINITESIMAL && 
				((level&FUNC_DIGIT_BASE) > 0 || (level&FUNC_DIGIT_ENABLE_LOG) > 0); nn++){

			if((level&FUNC_DIGIT_BASE) > 0){
				dsq = fabs(f_yd(nn)/dymax);
				if((level&FUNC_DIGIT_SIMPLE) == 0){
					dsq = sqrt(hypotsq(f_xd(nn)/(xfin-xini), dsq));
				}
				linng = dsq > eps;
			}
			else{
				linng = false;
			}
			if((level&FUNC_DIGIT_ENABLE_LOG) > 0){
				if(fabs(m_yarray[m_index[nn]]) < dymax*epsneg ||
						fabs(m_yarray[m_index[nn-1]]) < dymax*epsneg){
					logng = false;
				}
				else{
					dsq = fabs(m_yarray[m_index[nn]]/m_yarray[m_index[nn-1]]);
					if(dsq < 1.0){
						dsq = 1.0/dsq;
					}
					logng = dsq > epslog;
				}
			}
			else{
				logng = false;
			}

			if(linng == false && logng == false){
				if(nn > 1 && f_xd(nn) > (2.0+eps)*f_xd(nn-1)){
					stepng = true;
				}
				else if(nn < nstep-1 && f_xd(nn) > (2.0+eps)*f_xd(nn+1)){
					stepng = true;
				}
				else{
					stepng = false;
				}
			}

			if(linng || logng || stepng){
				finestep = f_xd(nn)*0.5;
				if(finestep > xminlim){
					m_indices[nins] = nn;
					m_wsx[nins] = m_xarray[m_index[nn]]-finestep;
					nins++;
				}
			}
		}
		nstep += nins;
		if(nins > 0 && status != nullptr){
			status->SetCurrentOrigin(targetlayer);
			status->SetSubstepNumber(targetlayer, nins*2);
		}
		if(mpiprocesses > 1 && nins > 0){
			f_ComputeFuncMPI(ninit, nins, m_wsx, 
				rank, mpiprocesses, thread, status, targetlayer, ninit);
		}
		for(nn = nins-1; nn >= 0; nn--){
			if(mpiprocesses > 1){
				for(ni = 0; ni < m_nitems; ni++){
					m_ytmp[ni] = m_wsyvec[ni][nn];
				}
				ystemp = m_wsy[nn];
				f_InsertItem(m_indices[nn], m_wsx[nn], &ystemp, &m_ytmp);
			}
			else{
				f_InsertItem(m_indices[nn], m_wsx[nn]);
				if(status != nullptr){
					status->PutSteps(targetlayer, nins-nn);
				}
			}
			ymax = max(ymax, m_yarray[m_index[m_indices[nn]]]);
			ymin = min(ymin, m_yarray[m_index[m_indices[nn]]]);
			dymax = ymax-ymin;
		}
	}while(nins > 0);

	if(y->size() < m_nitems){
		y->resize(m_nitems);
	}
	for(ni = 0; ni < m_nitems; ni++){
		if((*y)[ni].size() < nstep){
			(*y)[ni].resize(nstep);
		}
	}
	if(x->size() < nstep){
		x->resize(nstep);
	}
	nini = 0;
	nfin = nstep-1;
	if(istruncate){
		while(nini < nstep-FUNC_DIGIT_MIN_POINTS && fabs(m_yarray[m_index[nini]]) < (ymax-ymin)*epsneg){
			nini++;
		}
		while(nfin > nini+FUNC_DIGIT_MIN_POINTS && fabs(m_yarray[m_index[nfin]]) < (ymax-ymin)*epsneg){
			nfin--;
		}
		nstep = nfin-nini+1;
	}
	for(nn = nini; nn <= nfin; nn++){
		nr = nn-nini;
		(*x)[nr] = m_xarray[m_index[nn]];
		for(ni = 0; ni < m_nitems; ni++){
			(*y)[ni][nr] = m_yvecarray[ni][m_index[nn]];
		}
	}
	if(integ != nullptr){
		if(integ->size() < m_nitems){
			integ->resize(m_nitems, 0.0);
		}
		else{
			fill(integ->begin(), integ->end(), 0.0);
		}
		for(nn = 0; nn < nstep; nn++){
			if(nn == 0){
				dx = 0.5*((*x)[1]-(*x)[0]);
			}
			else if(nn == nstep-1){
				dx = 0.5*((*x)[nstep-1]-(*x)[nstep-2]);
			}
			else{
				dx = 0.5*((*x)[nn+1]-(*x)[nn-1]);
			}
			for(ni = 0; ni < m_nitems; ni++){
				(*integ)[ni] += (*y)[ni][nn]*dx;
			}
		}
	}

#ifdef _DEBUG
	if(!debug.empty()){
		ofstream debug_out(debug);
		if(debug_out){
			vector<double> tmp(m_nitems+1);
			for(nn = nini; nn <= nfin; nn++){
				tmp[0] = m_yarray[m_index[nn]];
				for(ni = 0; ni < m_nitems; ni++){
					tmp[ni+1] = m_yvecarray[ni][m_index[nn]];
				}
				PrintDebugItems(debug_out, m_xarray[m_index[nn]], tmp);
			}
		}
	}
#endif

	return nfin-nini+1;
}

void FunctionDigitizer::f_ComputeFuncMPI(int ninit, int npoints, vector<double> &xarr,
	int rank, int mpiprocesses, MPIbyThread *thread, PrintCalculationStatus *status, int targetlayer, int npininit)
{
	int nn, ni;
	vector<int> mpisteps, mpiinistep, mpifinstep;
	MPI_Status mpistatus;

	mpi_steps(npoints, 1, mpiprocesses, &mpisteps, &mpiinistep, &mpifinstep);

	for(nn = 0; nn < npoints; nn++){
		if(nn < mpiinistep[rank] || nn > mpifinstep[rank]){
			continue;
		}
		m_wsy[nn] = Function4Digitizer(xarr[nn], &m_ytmp);
		for(ni = 0; ni < m_nitems; ni++){
			m_wsyvec[ni][nn] = m_ytmp[ni];
		}
		if(status != nullptr && rank == 0){
			status->PutSteps(targetlayer, npoints*(nn+1)/mpisteps[0]);
		}
	}
	MPI_Barrier(MPI_COMM_WORLD);

	for(int k = 1; k < mpiprocesses; k++){
		if(thread != nullptr){
			thread->SendRecv(m_wsy+mpiinistep[k], mpisteps[k], MPI_DOUBLE, k, 0, rank);
			for(ni = 0; ni < m_nitems; ni++){
				thread->SendRecv(m_wsyvec[ni]+mpiinistep[k], mpisteps[k], MPI_DOUBLE, k, 0, rank);
			}
		}
		else{
			if(rank == 0){
				MPI_Recv(m_wsy+mpiinistep[k], mpisteps[k], MPI_DOUBLE, k, 0, MPI_COMM_WORLD, &mpistatus);
				for(ni = 0; ni < m_nitems; ni++){
					MPI_Recv(m_wsyvec[ni]+mpiinistep[k], mpisteps[k], MPI_DOUBLE, k, 0, MPI_COMM_WORLD, &mpistatus);
				}
			}
			else if(rank == k){
				MPI_Send(m_wsy+mpiinistep[k], mpisteps[k], MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
				for(ni = 0; ni < m_nitems; ni++){
					MPI_Send(m_wsyvec[ni]+mpiinistep[k], mpisteps[k], MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
				}
			}
			MPI_Barrier(MPI_COMM_WORLD);
		}
	}
	if(thread != nullptr){
		thread->Bcast(m_wsy, npoints, MPI_DOUBLE, 0, rank);
	}
	else{
		MPI_Bcast(m_wsy, npoints, MPI_DOUBLE, 0, MPI_COMM_WORLD);
	}
	for(ni = 0; ni < m_nitems; ni++){
		if(thread != nullptr){
			thread->Bcast(m_wsyvec[ni], npoints, MPI_DOUBLE, 0, rank);
		}
		else{
			MPI_Bcast(m_wsyvec[ni], npoints, MPI_DOUBLE, 0, MPI_COMM_WORLD);
		}
	}
}

int FunctionDigitizer::f_IsPeak(double *xarray, double *yarray, int index)
{
	double y0, y1, y2;
	int ispeak;

	y0 = yarray[m_index[index-1]];
	y1 = yarray[m_index[index]];
	y2 = yarray[m_index[index+1]];

	if(y0 == y1 && y1 == y2){
		ispeak = 0;
	}
	else if(y0 == y1){
		ispeak = y1 > y2 ? 1 : -1;
	}
	else if((y2-y1)*(y1-y0) < 0.0){
		ispeak = y1 > y2 ? 1 : -1;
	}
	else{
		ispeak = 0;
	}
	return ispeak;
}

bool FunctionDigitizer::f_IsPeak(double *xarray, double *yarray, int index,
	double *xpeak, double *ypeak)
{
	double a, b, x0, x1, x2, dx0, dx1, dx2, y0, y1, y2;

	y0 = yarray[m_index[index-1]];
	y1 = yarray[m_index[index]];
	y2 = yarray[m_index[index+1]];

	if((y2-y1)*(y1-y0) > 0.0){
		return false;
	}

	x0 = xarray[m_index[index-1]];
	x1 = xarray[m_index[index]];
	x2 = xarray[m_index[index+1]];
	dx0 = x0-x1;
	dx1 = x1-x2;
	dx2 = x2-x0;

	a = -y0/dx0/dx2-y1/dx0/dx1-y2/dx1/dx2;
	b = (x1+x2)*y0/dx0/dx2+(x0+x2)*y1/dx0/dx1+(x1+x0)*y2/dx1/dx2;

	if(a == 0.0){
		*xpeak = x1;
		*ypeak = y1;
	}
	else{
		*xpeak = -b/2.0/a;
		*ypeak = y0*((*xpeak)-x1)*((*xpeak)-x2)/(x0-x1)/(x0-x2)
			 +y1*((*xpeak)-x0)*((*xpeak)-x2)/(x1-x0)/(x1-x2)
			 +y2*((*xpeak)-x0)*((*xpeak)-x1)/(x2-x0)/(x2-x1);
	}

	return true;
}
