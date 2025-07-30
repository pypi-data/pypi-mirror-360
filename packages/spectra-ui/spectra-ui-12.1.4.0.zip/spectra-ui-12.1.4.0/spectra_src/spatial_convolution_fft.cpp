#include <algorithm>
#include "spatial_convolution_fft.h"
#include "numerical_common_definitions.h"
#include "common.h"
#include "density_fixed_point.h"

//---------------------------
//SpatialConvolutionFFT
string SpFFTConf1stConv;
string SpFFTConf1stConvFFT;
string SpFFTConf1stAft;
string SpFFTConf1stAlloc;
string SpFFTConf2ndConv;
string SpFFTConf2ndConvFFT;
string SpFFTConf2ndConvAft;
string SpFFTConf2ndAlloc;

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

#define FACTOR_OF_MEMORY_EXPANSION 4

SpatialConvolutionFFTBase::~SpatialConvolutionFFTBase()
{
    int j;
    for(j = 0; j < m_nitems; j++){
        free(m_wsdata[j]);
        free(m_wsfftold[j]);
        free(m_wsfftnext[j]);
    }
    delete m_fft;
}

void SpatialConvolutionFFTBase::SetCalcStatusPrintFFT(int targetlayer, PrintCalculationStatus *status)
{
    m_layer = targetlayer;
    m_statusfftbase = status;
}

void SpatialConvolutionFFTBase::ArrangeVariables(bool isspline, int nitems,
    int nborder, double eps, int level, double sigma, double sigmalimit,
    double xymin, double dxy, int nxy, double dxyspl, bool posonly,  
	int rank, int mpiprocesses, MPIbyThread *thread)
{
    int ndata, j, n;

    m_posonly = posonly;
    m_cancelspfft = false;
    m_itemrefer = 0;

    m_usespline = isspline && nxy > 1;
	m_rank = rank;
	m_mpiprocesses = mpiprocesses;
    m_cvthread = thread;

    m_nitems = nitems;
    m_nborder = nborder;
    m_sigma = sigma;
    m_eps = eps;
    m_epspline = 0.1/(double)(1<<level);
    if(nxy == 1 || dxy == 0.0){
        dxy = m_sigma/(double)(1<<level);
    }
    m_dxyini = dxy;
    m_nxy = nxy;
    if(dxy < INFINITESIMAL || m_sigma < INFINITESIMAL){
        m_offset = 0;
    }
    else{
        m_offset = (int)floor(fabs(m_sigma*sigmalimit/dxy))+1;
    }
    m_xymin = xymin-(double)m_offset*dxy;
    m_xymax = xymin+(double)(nxy-1)*dxy+(double)(m_offset+1)*dxy;
    m_vtmp.resize(m_nitems);
    if(m_usespline){
        m_ninitspline = max((int)ceil((m_xymax-m_xymin)/dxyspl), 8<<level);
    }

    ndata = max(8, 2*m_offset+nxy); // to avoid contamination by FFT convolution
    m_nfftini = 1;
    while(m_nfftini < ndata) m_nfftini <<= 1;
    if(m_dxyini < INFINITESIMAL){
        m_dkxy = 0.0;
    }
    else{
        m_dkxy = PI2/(m_dxyini*(double)m_nfftini);
    }

    m_wsdata.resize(m_nitems);
    m_wsfftold.resize(m_nitems);
    m_wsfftnext.resize(m_nitems);
    m_vconvold.resize(m_nitems);
    m_allocsize = FACTOR_OF_MEMORY_EXPANSION*m_nfftini;
    for(j = 0; j < m_nitems; j++){
		m_wsdata[j] = (double *)calloc(m_allocsize*2, sizeof(double));
        m_wsfftold[j] = (double *)calloc(m_allocsize*4, sizeof(double));
        m_wsfftnext[j] = (double *)calloc(m_allocsize*4, sizeof(double));
        m_vconvold[j].resize(nxy+1);
    }
    m_fft = new FastFourierTransform(1, m_nfftini);
    AllocateMemoryFuncDigitizer(m_nitems);
    m_denspline.resize(m_nitems);
	m_denspoint.resize(m_nitems);

    m_xyarray.resize(nxy);
    double xyorg = fabs(xymin);
    m_orgidx = 0;
    for(n = 0; n < nxy; n++){
        m_xyarray[n] = xymin+n*dxy;
        if(fabs(m_xyarray[n]) < dxy*DXY_LOWER_LIMIT){
            m_xyarray[n] = 0.0;
        }
        if(fabs(m_xyarray[n]) < xyorg){
            xyorg = fabs(m_xyarray[n]);
            m_orgidx = n;
        }
    }
}

void SpatialConvolutionFFTBase::RunFFTConvolution(vector<vector<double>> *vconv, 
    string debug, string debugfft, string debugaft, string debugspl)
{
    int n, j, nc, nr, irep = 0;
    double vcmax[3], feps;

	m_nskip = 1;

    if(m_sigma < INFINITESIMAL){ // convolution is not necessary
        m_dxy = m_dxyini;
        m_nfft = m_nfftini;
    }
    else{
        m_dxy = m_dxyini*2.0;
        m_nfft = m_nfftini/2;
    }

	if(m_statusfftbase != nullptr && !m_usespline){
		m_statusfftbase->SetTargetAccuracy(m_layer, m_eps);
		m_statusfftbase->SetCurrentAccuracy(m_layer, m_sigma < INFINITESIMAL ? m_eps : INITIAL_EPS);
	}

    if(m_usespline){
        f_AssignSplineData(debugspl);
    }

    f_AllocateData4Convolution(m_dxy, 0.0, m_nfft, debug, false, debugfft);
	if(m_statusfftbase != nullptr && !m_usespline){
		m_statusfftbase->SetCurrentOrigin(m_layer);
	}
    if(m_cancelspfft){
        return;
    }
    if(m_sigma < INFINITESIMAL){ // convolution is not necessary
        for(nc = 0; nc < m_nxy; nc++){
            for(j = 0; j < m_nitems; j++){
                (*vconv)[j][nc] = m_wsdata[j][nc];
            }
        }
        return;
    }
    for(j = 0; j < m_nitems; j++){
        for(n = 0; n < m_nfft; n++){
            m_wsfftold[j][2*n] = m_wsdata[j][2*n];
            m_wsfftold[j][2*n+1] = m_wsdata[j][2*n+1];
        }
		for(nc = 0; nc < m_nxy; nc++){
            m_vconvold[j][nc] = 0.0;
        }
    }

    while(1){
        irep++;
        f_AllocateData4Convolution(m_dxy, m_dxy*0.5, m_nfft, debug, true, debugfft);
		if(m_cancelspfft){
            return;
        }
        f_RunConvolutionSingle(m_nfft, false, debugfft, debugaft);

		vcmax[1] = vcmax[2] = INFINITESIMAL;
        for(nc = 0; nc < m_nxy; nc++){
            nr = m_nskip*(m_offset+nc);
            for(j = 0; j < m_nitems; j++){
                (*vconv)[j][nc] = m_wsfftnext[j][nr];
                if(j > m_nborder){
                    vcmax[2] = max(vcmax[2], fabs((*vconv)[j][nc]));
                }
                else{
                    vcmax[1] = max(vcmax[1], fabs((*vconv)[j][nc]));
                }
            }
        }
        feps = INFINITESIMAL;
        for(nc = 0; nc < m_nxy; nc++){
            for(j = 0; j < m_nitems; j++){
                vcmax[0] = j > m_nborder ? vcmax[2] : vcmax[1];
                feps = max(feps, fabs((*vconv)[j][nc]-m_vconvold[j][nc])/(vcmax[0]+INFINITESIMAL));
                m_vconvold[j][nc] = (*vconv)[j][nc];
            }
        }
		if(m_statusfftbase != nullptr){
			m_statusfftbase->SetCurrentOrigin(m_layer);
			m_statusfftbase->SetCurrentAccuracy(m_layer, feps);
		}
		if(feps > m_eps || irep < m_minrepeatfft){
	        m_dxy *= 0.5; m_nfft <<= 1; m_nskip <<= 1;
		}
		else{
			break;
		}
    }
}

void SpatialConvolutionFFTBase::GetXYArray(vector<double> *xy, double fcorr)
{
    int n;

    xy->resize(m_xyarray.size());
    for(n = 0; n < m_xyarray.size(); n++){
        (*xy)[n] = m_xyarray[n]*fcorr;
    }
}

double SpatialConvolutionFFTBase::Function4Digitizer(double xy, vector<double> *density)
{
    SingleDensity1D(xy, density);
    return (*density)[m_itemrefer];
}

void SpatialConvolutionFFTBase::GetFFTedProfileAt(double kxy, double *ftre, double *ftim)
{
	double tex = m_sigma*kxy;
	tex *= tex*0.5;
	tex = tex < MAXIMUM_EXPONENT ? exp(-tex) : 0.0;
	*ftre = tex;
	*ftim = 0.0;
}

//----- private functions -----
void SpatialConvolutionFFTBase::f_GetSpline(double xy, vector<double> *density)
{
    for(int j = 0; j < m_nitems; j++){
		if(m_splassign){
	        (*density)[j] = m_denspline[j].GetOptValue(xy);
		}
		else{
		    (*density)[j] = m_denspoint[j];
		}
    }
}

void SpatialConvolutionFFTBase::f_AssignSplineData(string debug)
{
    vector<double> xy;
    vector<vector<double>> dens;
    int narray, j;
	double xrange[NumberFStepXrange] = 
		{0.0, m_xymin, m_xymax, 0.0, (m_xymax-m_xymin)*1e-3};
	double eps[2] = {m_eps, 0};

	narray = RunDigitizer(FUNC_DIGIT_BASE, &xy, &dens, 
		xrange, m_ninitspline, eps, m_statusfftbase, m_layer, debug, 
        nullptr, false, m_rank, m_mpiprocesses, m_cvthread);

	m_splassign = narray > 2;
	for(j = 0; j < m_nitems; j++){
		if(m_splassign){
			m_denspline[j].SetSpline(narray, &xy, &dens[j]);		
		}
		else{
			m_denspoint[j] = dens[j][0];
		}
    }
}

void SpatialConvolutionFFTBase::f_AllocateData4Convolution(
    double dxy, double offset, int nfft, string debug, bool isappend, string debufft)
{
    int n, j;
    double xy;
#ifdef _DEBUG
	ofstream debug_out;
    vector<double> wstmp(m_nitems);
	if(!debug.empty()){
		debug_out.open(debug,  isappend?(ios::app):(ios::trunc));
	}
#endif

	MPI_Status status;

    if(nfft > m_allocsize){
        m_allocsize = FACTOR_OF_MEMORY_EXPANSION*m_nfft;
        for(j = 0; j < m_nitems; j++){
            m_wsdata[j] = (double *)realloc_chk(m_wsdata[j], sizeof(double)*m_allocsize*2);
            m_wsfftold[j] = (double *)realloc_chk(m_wsfftold[j], sizeof(double)*m_allocsize*4);
            m_wsfftnext[j] = (double *)realloc_chk(m_wsfftnext[j], sizeof(double)*m_allocsize*4);
        }
    }

	if(m_sigma < INFINITESIMAL){ // convolution is not necessary
        nfft = m_nxy;
    }

	if(m_statusfftbase != nullptr && !m_usespline){
		m_statusfftbase->SetSubstepNumber(m_layer, nfft);
	}

	if((!m_usespline) && m_mpiprocesses > 1){
		mpi_steps(nfft, 1, m_mpiprocesses, &m_mpisteps, &m_mpiinistep, &m_mpifinstep);

		for(n = 0; n < nfft; n++){
			xy = dxy*(double)n+offset+m_xymin;
	        if((n >= m_mpiinistep[m_rank] && n <= m_mpifinstep[m_rank] && m_xymax-xy > -INFINITESIMAL) 
					|| n == 0){
	            SingleDensity1D(xy, &m_vtmp);

				if(m_cancelspfft){
	                break;
		        }
			    for(j = 0; j < m_nitems; j++){
				    m_wsdata[j][n] = m_vtmp[j];
	            }
		    }
			else{
				for(j = 0; j < m_nitems; j++){
	                m_wsdata[j][n] = 0.0;
		        }
			}
		    if(m_statusfftbase != nullptr && !m_usespline){
				m_statusfftbase->PutSteps(m_layer, n+1);
			}
	    }

		MPI_Barrier(MPI_COMM_WORLD);
		for(j = 0; j < m_nitems; j++){
			for(int k = 1; k < m_mpiprocesses; k++){
                if(m_cvthread != nullptr){
                    m_cvthread->SendRecv(m_wsdata[j]+m_mpiinistep[k], m_mpisteps[k], MPI_DOUBLE, k, 0, m_rank);
                }
                else{
                    if(m_rank == 0){
                        MPI_Recv(m_wsdata[j]+m_mpiinistep[k], m_mpisteps[k], MPI_DOUBLE, k, 0, MPI_COMM_WORLD, &status);
                    }
                    else if(m_rank == k){
                        MPI_Send(m_wsdata[j]+m_mpiinistep[k], m_mpisteps[k], MPI_DOUBLE, 0, 0, MPI_COMM_WORLD);
                    }
                    MPI_Barrier(MPI_COMM_WORLD);
                }
			}
            if(m_cvthread != nullptr){
                m_cvthread->Bcast(m_wsdata[j], nfft, MPI_DOUBLE, 0, m_rank);
            }
            else{
                MPI_Bcast(m_wsdata[j], nfft, MPI_DOUBLE, 0, MPI_COMM_WORLD);
            }
		}
	}
	else{
		for(n = 0; n < nfft; n++){
			xy = dxy*(double)n+offset+m_xymin;
	        if(n == 0 || m_xymax-xy > -INFINITESIMAL){
		        if(m_usespline){
			        f_GetSpline(xy, &m_vtmp);
				}
	            else{
		            SingleDensity1D(xy, &m_vtmp);
			    }
				if(m_cancelspfft){
	                break;
		        }
			    for(j = 0; j < m_nitems; j++){
				    m_wsdata[j][n] = m_vtmp[j];
	            }
		    }
			else{
				for(j = 0; j < m_nitems; j++){
	                m_wsdata[j][n] = 0.0;
		        }
			}
#ifdef _DEBUG
            if(!debug.empty()){
		        if(xy < m_xymax){
                    for (int j = 0; j < m_nitems; j++){
                        wstmp[j] = m_wsdata[j][n];
                    }
                    PrintDebugItems(debug_out, xy, wstmp);
                }
            }
#endif
		    if(m_statusfftbase != nullptr && !m_usespline){
				m_statusfftbase->PutSteps(m_layer, n+1);
			}
	    }
#ifdef _DEBUG
        if(!debug.empty()){
            debug_out.close();
        }
#endif
	}

    if(m_sigma < INFINITESIMAL){ // convolution is not necessary
        return;
    }
    if(m_cancelspfft){
        return;
    }

	m_fft->SetFFTWorkSpace(1, nfft);
    for(j = 0; j < m_nitems; j++){
        m_fft->DoRealFFT(m_wsdata[j]);
    }

#ifdef _DEBUG
	if(!debufft.empty()){
		ofstream debug_outa(debufft);
        vector<double> wstmpa(2*m_nitems);
        for(n = 0; n <= nfft/2; n++){
            double kxy = (double)n*m_dkxy;
            for (int j = 0; j < m_nitems; j++){
                if(n == nfft/2){
                    wstmpa[2*j] = m_wsdata[j][1];
                    wstmpa[2*j+1] = 0;
                }
                else if(n == 0){
                    wstmpa[2*j] = m_wsdata[j][0];
                    wstmpa[2*j+1] = 0;
                }
                else{
                    wstmpa[2*j] = m_wsdata[j][2*n];
                    wstmpa[2*j+1] = m_wsdata[j][2*n+1];
                }
            }
            PrintDebugItems(debug_outa, kxy, wstmpa);
        }
	}
#endif

}

void SpatialConvolutionFFTBase::f_RunConvolutionSingle(int nfft, bool isrestore,
    string debugfft, string debugaft)
{
    int n, nn, j;
    double cs, sn, kxy, farg, dsign, ftre, ftim, dummy;

    for(n = 0; n < nfft; n++){
		if(isrestore){
	        for(j = 0; j < m_nitems; j++){
		        m_wsfftnext[j][2*n] = m_wsfftold[j][2*n];
			    m_wsfftnext[j][2*n+1] = m_wsfftold[j][2*n+1];
			}
			continue;
		}
        farg = PI2*(double)n/(double)(nfft*2);
        cs = cos(farg); sn = sin(farg);
        if(n == 0){
            for(j = 0; j < m_nitems; j++){
                m_wsfftnext[j][0] = m_wsfftold[j][0]+m_wsdata[j][0];
                m_wsfftnext[j][1] = m_wsfftold[j][0]-m_wsdata[j][0];
                    // Real(F_(N/2)) = Real(F_(0))-Real(F_(Delta))
            }
        }
        else  if(n == nfft/2){
            for(j = 0; j < m_nitems; j++){
                m_wsfftnext[j][2*n] = m_wsfftold[j][1]+cs*m_wsdata[j][1];
                m_wsfftnext[j][2*n+1] = sn*m_wsdata[j][1];
            }
        }
        else{
            if(n < nfft/2){
                nn = n;
                dsign = 1.0;
            }
            else{
                nn = nfft-n;
                dsign = -1.0;
            }
            for(j = 0; j < m_nitems; j++){
                m_wsfftnext[j][2*n]
                = m_wsfftold[j][2*nn]+cs*m_wsdata[j][2*nn]-dsign*sn*m_wsdata[j][2*nn+1];
                m_wsfftnext[j][2*n+1]
                = dsign*(m_wsfftold[j][2*nn+1]+cs*m_wsdata[j][2*nn+1])+sn*m_wsdata[j][2*nn];
            }
        }
    }

    for(n = 0; n < nfft && !isrestore; n++){
        for(j = 0; j < m_nitems; j++){
            m_wsfftold[j][2*n] = m_wsfftnext[j][2*n];
            m_wsfftold[j][2*n+1] = m_wsfftnext[j][2*n+1];
        }
    }

#ifdef _DEBUG
	if(!debugfft.empty()){
		ofstream debug_outa(debugfft);
        vector<double> wstmpa(2*m_nitems+2);
        for(n = 0; n <= nfft; n++){
            double kxy = (double)n*m_dkxy;
            GetFFTedProfileAt(kxy, &ftre, &ftim);
            wstmpa[0] = ftre;
            wstmpa[1] = ftim;
            for (int j = 0; j < m_nitems; j++){
                if(n == nfft/2){
                    wstmpa[2*j+2] = m_wsfftnext[j][1];
                    wstmpa[2*j+3] = 0;
                }
                else if(n == 0){
                    wstmpa[2*j+2] = m_wsfftnext[j][0];
                    wstmpa[2*j+3] = 0;
                }
                else{
                    wstmpa[2*j+2] = m_wsfftnext[j][2*n];
                    wstmpa[2*j+3] = m_wsfftnext[j][2*n+1];
                }
            }
            PrintDebugItems(debug_outa, kxy, wstmpa);
        }
        debug_outa.close();
	}
#endif

    for(n = 0; n <= nfft; n++){
        kxy = (double)n*m_dkxy;
		GetFFTedProfileAt(kxy, &ftre, &ftim);
        for(j = 0; j < m_nitems; j++){
            if(n == nfft){
                m_wsfftnext[j][1] *= ftre;
            }
            else if(n == 0){
                m_wsfftnext[j][0] *= ftre;
            }
            else{
                m_wsfftnext[j][2*n] = ftre*(dummy=m_wsfftnext[j][2*n])-ftim*m_wsfftnext[j][2*n+1];
                m_wsfftnext[j][2*n+1] = dummy*ftim+m_wsfftnext[j][2*n+1]*ftre;
			}
        }
    }

    m_fft->SetFFTWorkSpace(1, 2*nfft);
    for(j = 0; j < m_nitems; j++){
        m_fft->DoRealFFT(m_wsfftnext[j], -1);
        for(n = 0; n < 2*nfft; n++){
            m_wsfftnext[j][n] /= (double)nfft;
        }
    }

#ifdef _DEBUG
	if(!debugaft.empty()){
		ofstream debug_outb(debugaft);
        vector<double> wstmpb(m_nitems);
        for(n = 0; n < 2*nfft; n++){
            double xy = (double)n*m_dxy*0.5+m_xymin;
            if(xy > m_xymax) continue;
            for(int j = 0; j < m_nitems; j++){
                wstmpb[j] = m_wsfftnext[j][n];
            }
            PrintDebugItems(debug_outb, xy, wstmpb);
        }
        debug_outb.close();
	}
#endif
}

//------------------------------------------------------------------------------
SpatialConvolutionFFT1Axis::SpatialConvolutionFFT1Axis(
    int type, bool ismesh, SpectraSolver &spsolver)
{
    int nitems, judgeitems, mesh;
    double xyini, dxy, sigma, dxyspl, size[2];

    m_minrepeatfft = spsolver.GetAccuracy(accinobs_);
    m_type = type;
    spsolver.GetGridContents(type, ismesh, &xyini, &dxy, &dxyspl, &mesh);
    judgeitems = nitems = spsolver.GetNumberOfItems();
    spsolver.GetEBeamSize(size);
    sigma = size[type];

    double tol, nglim;
    int level;
    spsolver.GetAccuracySpFFT(&tol, &level, &nglim);
    ArrangeVariables(spsolver.IsSmoothSprofile(), 
        nitems, judgeitems, tol, level, sigma, nglim, xyini, dxy, mesh, dxyspl, spsolver.IsPower());
}

void SpatialConvolutionFFT1Axis::SingleDensity1D(double xy, vector<double> *density)
{
    m_xyfix[m_type] = xy;
    SingleDensity2D(m_xyfix, density);
}

void SpatialConvolutionFFT1Axis::SetXYFixPoint(double xy)
{
    int antype;
    if(m_type == SPATIAL_CONVOLUTION_ALONGX){
        antype = 1;
    }
    else{
        antype = 0;
    }
    m_xyfix[antype] = xy;
}

//------------------------------------------------------------------------------
SpatialConvolutionAlongXYAxis::SpatialConvolutionAlongXYAxis(
        int type, bool ismesh, SpectraSolver &spsolver, DensityFixedPoint *densfix) :
        SpatialConvolutionFFT1Axis(type, ismesh, spsolver)
{
    m_densfix = densfix;
	m_fftrespl = nullptr;
	m_fftimspl = nullptr;
}

void SpatialConvolutionAlongXYAxis::SingleDensity2D(double *xy, vector<double> *density)
{
    m_densfix->GetDensity(xy[0], xy[1], density);
}

void SpatialConvolutionAlongXYAxis::GetFFTedProfileAt(double kxy, double *ftre, double *ftim)
{
	if(m_fftrespl == nullptr || m_fftimspl == nullptr){
		SpatialConvolutionFFTBase::GetFFTedProfileAt(kxy, ftre, ftim);
	}
	else{
		*ftre = m_fftrespl->GetValue(kxy, true);
		*ftim = m_fftimspl->GetValue(kxy, true);
	}
}

void SpatialConvolutionAlongXYAxis::SetFFTSpline(Spline *re, Spline *im)
{
	m_fftrespl = re;
	m_fftimspl = im;
}

//------------------------------------------------------------------------------
SpatialConvolutionFFT::SpatialConvolutionFFT(int type, 
    SpectraSolver &spsolver, DensityFixedPoint *densfix, int layer, 
    int rank, int mpiprocesses)
    : SpectraSolver(spsolver)
{
#ifdef _DEBUG
//SpFFTConf1stConv = "..\\debug\\spfft_1st_conv.dat";
//SpFFTConf1stConvFFT = "..\\debug\\spfft_1st_conv_fft.dat";
//SpFFTConf1stAft = "..\\debug\\spfft_1st_conv_aft.dat";
//SpFFTConf1stAlloc = "..\\debug\\spfft_1st_alloc.dat";
//SpFFTConf2ndConv = "..\\debug\\spfft_2nd_conv.dat";
//SpFFTConf2ndConvFFT = "..\\debug\\spfft_2nd_conv_fft.dat";
//SpFFTConf2ndConvAft = "..\\debug\\spfft_2nd_conv_aft.dat";
//SpFFTConf2ndAlloc = "..\\debug\\spfft_2nd_alloc.dat";
#endif
    if(contains(m_calctype, menu::meshrphi)){
        int ist =  (int)m_calctype.find(menu::meshrphi);
        m_calctype = m_calctype.replace(ist, menu::meshrphi.length(), menu::meshxy);
        int xidx, yidx, ridx, pidx;
        if(m_confsel[defobs_] == ObsPointAngle){
            ridx = qrange_;
            xidx = qxrange_;
            yidx = qyrange_;
            pidx = qphimesh_;
        }
        else{
            ridx = rrange_;
            xidx = xrange_;
            yidx = yrange_;
            pidx = rphimesh_;
        }
        double range = max(m_confv[ridx][0], m_confv[ridx][1]);
        range *= 1.01; // avoid extrapolation
        int mesh = (int)floor(0.5+max(m_conf[phimesh_], m_conf[pidx]));
        m_confv[xidx][0] = m_confv[yidx][0] = range;
        m_confv[xidx][1] = m_confv[yidx][1] = -range;
        m_conf[xmesh_] = m_conf[ymesh_] = 2*mesh+1;
    }

    int xyindex, meshx, meshy, j, idum;
    double sigma, xyini, dxy, dxyspl, bmsize[2];

    m_isyonly = m_srctype == BM && m_isfar;
    m_minrepeatfft = m_accuracy[accinobs_];
	m_layer = layer;

    int xmidx = GetIndexXYMesh(0);
    int ymidx = GetIndexXYMesh(1);
    meshx = m_isyonly ? 1 : (int)floor(0.5+m_conf[xmidx]);
    meshy = (int)floor(0.5+m_conf[ymidx]);
    if(type == SPATIAL_CONVOLUTION_ALONGX){
        meshy = 1;
    }
    else if(type == SPATIAL_CONVOLUTION_ALONGY){
        meshx = 1;
    }
    GetEBeamSize(bmsize);

    m_xfirst = bmsize[0] > bmsize[1] && (!m_isyonly);
    if(m_issrcpoint && m_isbm && !m_srcb[bmtandem_]){
        m_xfirst = false;
        m_tol_spint /= 2.0;
        // flux oscillates along x, more stringent accuracy requried
    }

    m_densfix = densfix;

    if(m_xfirst){
		m_mesh1st = meshx;
        m_mesh2nd = meshy;
        xyindex = 1;
        m_spconv = new SpatialConvolutionAlongXYAxis(SPATIAL_CONVOLUTION_ALONGX,
                    meshx > 1, *this, densfix);
    }
    else{
        m_mesh1st = meshy;
        m_mesh2nd = meshx;
        xyindex = 0;
        m_spconv = new SpatialConvolutionAlongXYAxis(SPATIAL_CONVOLUTION_ALONGY,
                    meshy > 1, *this, densfix);
    }

	m_spconv->SetCalcStatusPrintFFT(m_layer+1, m_calcstatus);
	SetCalcStatusPrintFFT(m_layer, m_calcstatus);

    m_nitemspoint = GetNumberOfItems();
    m_nitems1st = m_mesh1st*m_nitemspoint;
    m_vconvtmp.resize(m_nitemspoint);
    for(j = 0; j < m_nitemspoint; j++){
        m_vconvtmp[j].resize(m_mesh1st);
    }
    m_vconv.resize(m_nitems1st);
    for(j = 0; j < m_nitems1st; j++){
        m_vconv[j].resize(m_mesh2nd);
    }

    sigma = (m_isyonly || m_accb[zeroemitt_]) ? 0.0 : bmsize[xyindex];
    GetGridContents(xyindex, 
        !m_isyonly && m_mesh2nd > 1, &xyini, &dxy, &dxyspl, &idum);

    ArrangeVariables(IsSmoothSprofile(), m_nitems1st, m_nitems1st, m_tol_spint,
        m_spfftlevel, sigma, m_nlimit[acclimobs_], xyini, dxy, m_mesh2nd, dxyspl,
	    m_ispower, rank, mpiprocesses, m_thread);

    if(!m_isyonly && m_mesh1st > 1){
        m_itemrefer = m_spconv->GetIndexOrigin();
    }
}

SpatialConvolutionFFT::~SpatialConvolutionFFT()
{
    delete m_spconv;
}

void SpatialConvolutionFFT::SingleDensity1D(double xy, vector<double> *density)
{
    m_spconv->SetXYFixPoint(xy);
    m_spconv->RunFFTConvolution(&m_vconvtmp, SpFFTConf1stConv, SpFFTConf1stConvFFT, SpFFTConf1stAft, SpFFTConf1stAlloc);
    for(int j = 0; j < m_nitemspoint; j++){
        for(int i = 0; i < m_mesh1st; i++){
            (*density)[i+j*m_mesh1st] = m_vconvtmp[j][i];
        }
    }
}

void SpatialConvolutionFFT::Run2DConvolution()
{
    RunFFTConvolution(&m_vconv, SpFFTConf2ndConv, SpFFTConf2ndConvFFT, SpFFTConf2ndConvAft, SpFFTConf2ndAlloc);
}

void SpatialConvolutionFFT::GetXYArrays(vector<double> *xarray, vector<double> *yarray)
{
    if(m_xfirst){
        GetXYArray(yarray, m_fcoef_obspoint);
        m_spconv->GetXYArray(xarray, m_fcoef_obspoint);
    }
    else{
        GetXYArray(xarray, m_fcoef_obspoint);
        m_spconv->GetXYArray(yarray, m_fcoef_obspoint);
    }
}

void SpatialConvolutionFFT::GetValues(vector<vector<vector<double>>> *zmatrix)
{
    int meshx, meshy, nx, ny, j, nitems, index1st, index2nd;
    if(m_xfirst){
        meshx = m_mesh1st;
        meshy = m_mesh2nd;
    }
    else{
        meshy = m_mesh1st;
        meshx = m_mesh2nd;
    }

    nitems = GetNumberOfItems();
    zmatrix->resize(nitems);

    for(j = 0; j < nitems; j++){
        (*zmatrix)[j].resize(meshx);
        for(nx = 0; nx < meshx; nx++){
            (*zmatrix)[j][nx].resize(meshy);
        }
    }
    double coef;
    if(!m_ispower && !m_isrespow && !m_issrcpoint){
        coef = GetFluxCoef();
    }
    else if(m_issrcpoint){
        coef = m_densfix->GetSrcPointCoef();
    }
    else{
        coef = GetPowerCoef();
    }

    for(nx = 0; nx < meshx; nx++){
        for(ny = 0; ny < meshy; ny++){
            if(m_xfirst){
                index1st = nx; index2nd = ny;
            }
            else{
                index1st = ny; index2nd = nx;
            }
            for(j = 0; j < nitems; j++){
                (*zmatrix)[j][nx][ny] = coef*m_vconv[index1st+j*m_mesh1st][index2nd];
            }
        }
    }
}
