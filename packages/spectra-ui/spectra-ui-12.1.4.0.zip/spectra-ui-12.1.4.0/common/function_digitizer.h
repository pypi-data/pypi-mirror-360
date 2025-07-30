#ifndef function_digitizer_h
#define function_digitizer_h

#include <iostream>
#include <vector>
#include "print_calculation_status.h"
#include "mpi_by_thread.h"

using namespace std;

#define FUNC_DIGIT_BASE			0x0001
#define FUNC_DIGIT_XINI_ALLOC	0x0002
#define FUNC_DIGIT_YINI_ALLOC	0x0004
#define FUNC_DIGIT_DX_ALLOCATED  0x0008
#define FUNC_DIGIT_ALLOC_XREF	0x0010
#define FUNC_DIGIT_ENABLE_LOG	0x0020
#define FUNC_DIGIT_SIMPLE		0x0040

#define FUNC_DIGIT_MIN_POINTS 10
#define LIMIT_RATIO_XREF_IGNORE 1.0e-5
#define NUMBER_OF_MEMORY_EXPANSION 1000

enum {
	FstepDx = 0,
	FstepXini,
	FstepXfin,
	FstepXref,
	FstepXlim,
	NumberFStepXrange
};

// "Digitizing" a function with less points
class FunctionDigitizer {
public:

	FunctionDigitizer();
	FunctionDigitizer(int nitems);
	virtual ~FunctionDigitizer();
	void Free();
	void AllocateMemoryFuncDigitizer(int nitems);
	virtual double Function4Digitizer(double x, vector<double> *y) = 0;
	int RunDigitizer(
		int level, vector<double> *x, vector<vector<double>> *y,
		double *xrange, int ninit, double *epsval,
		PrintCalculationStatus *status, int targetlayer,
		string debug, vector<double> *integ = nullptr, bool istruncate = false,
		int rank = 0, int mpiprocesses = 1, MPIbyThread *thread = nullptr);

	int GetNumberItems(){return m_nitems;}

private:
	void f_ComputeFuncMPI(int ninit, int npoints, vector<double> &xarr,
			int rank, int mpiprocesses, MPIbyThread *thread, PrintCalculationStatus *status, int targetlayer, int npininit = 0);
	void f_Resize(int arraysize);
	void f_InsertItem(int index, double x, double *y = NULL, vector<double> *yvec = NULL);
	int f_IsPeak(double *xarray, double *yarray, int index);
	bool f_IsPeak(double *xarray, double *yarray, int index,
		double *xpeak, double *ypeak);

	int m_allocsize; // memory size currently allocated
	int m_size; // number of variables currently stored in arrays of the class member
	vector<int> m_index; // array of an integer to specify the order of data

	vector<double> m_ytmp; // stores the return value of Function4Digitizer
	vector<double> m_xarray; // array for x
	vector<double> m_yarray; // stores values to judege convergence
	vector<double> m_y1st; // stores values to judege convergence
	vector<double *> m_yvecarray; // array for y

	vector<int> m_indices; // index for insertion
	vector<double> m_wsx; // x workspace for MPI
	double *m_wsy; // y workspace for MPI
	vector<double *> m_wsyvec; // yvec workspace for MPI

	double f_xd(int index); // returns x[n]-x[n-1]
	double f_yd(int index); // returns y[n]-y[n-1]
	double f_y1std(int index); // returns dy/dx[n+1]-dy/dx[n]

	bool m_isinitialized;

protected:
	int m_nitems; // number of items in the function for stepper
	bool m_cancelfstepper;
};

#endif
