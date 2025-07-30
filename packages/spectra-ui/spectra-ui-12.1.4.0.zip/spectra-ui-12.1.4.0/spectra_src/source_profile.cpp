#include "source_profile.h"
#include "complex_amplitude.h"
#include "common.h"
#include "bessel.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

string AllocSrcP1DEnd;
string AllocSrcP2DEnd;
string AllocSrcFD;
string AllocSrcUnd;
string AllocSrcEconv;
string AllocSrcBMFunc;

SourceProfile::SourceProfile(ComplexAmplitude *camp, 
	int acclevel, int nwiggler, bool isoddpole, PrintCalculationStatus *status, int layer)
{

#ifdef _DEBUG
//AllocSrcP1DEnd  = "..\\debug\\alloc_src_1d.dat";
//AllocSrcP2DEnd = "..\\debug\\alloc_src_2d.dat";
//AllocSrcFD  = "..\\debug\\alloc_src_FD.dat";
//AllocSrcUnd  = "..\\debug\\alloc_src_U.dat";
//AllocSrcEconv  = "..\\debug\\alloc_src_econv.dat";
//AllocSrcBMFunc  = "..\\debug\\alloc_src_bm_func.dat";
#endif

	m_camp = camp;
	m_thread = m_camp->GetThread();
	m_oddpolewig = isoddpole;
	m_polarity = 1.0;
	m_Nwiggler = nwiggler;
	m_acclevel = acclevel;
	m_ncomps = max(1, nwiggler);
	m_isund = m_camp->IsIdealUnd();
	m_isbm = m_camp->IsIdealBM();
	m_nfftxydata = 0;
	if(m_isbm){
		m_splon = false;
		AllocateMemoryFuncDigitizer(4);
	}
	if(!m_camp->IsIdealSrc()){
		m_camp->GetEnergyArray(m_eparray);
		m_espredrange = m_camp->GetEspreadRange();
	}
	m_status = status;
	m_layer = layer;
	m_nfftcurr[0] = m_nfftcurr[1] = -1;
	m_camp->GetEBeamSize(m_sigmaUV);
	double dXYdUV = m_camp->GetConvUV();
	for(int j = 0; j < 2; j++){
		m_sigmaUV[j] /= dXYdUV;
	}
}

SourceProfile::~SourceProfile()
{
	f_ClearPointers();
}

void SourceProfile::AllocateSpatialProfile(int rank, int mpiprocesses)
{
	for(int j = 0; j < 2; j++){
		m_fft[j] = nullptr;
		m_wsdatax[j] = nullptr;
		m_wsdatay[j] = nullptr;
	}

	m_F.resize(m_ncomps);
	if(m_oddpolewig){
		m_G.resize(m_ncomps);
	}
	for(int j = 0; j < 4; j++){
		m_deltasp[j].resize(m_ncomps+1);
		m_spmesh[j].resize(m_ncomps+1);
		m_halfmeshsp[j].resize(m_ncomps+1);
	}

	if(m_isund){
		f_AllocateProfileUndulator();
	}
	else if(m_Nwiggler > 0){
		m_status->SetSubstepNumber(m_layer, m_ncomps*(m_oddpolewig?2:1)+1);
		f_AllocateProfileWiggler(rank, mpiprocesses);
	}
	else if(m_isbm){
		f_SpatialProfileSingle(0, &m_F[0]);
	}
	else{
		m_status->SetSubstepNumber(m_layer, m_eparray.size());
		AllocateProfileEconv();
	}
}

double SourceProfile::Function4Digitizer(double v, vector<double> *Exy)
{
	double coef = 4.0*PI*m_epsilon;
	double evv = hypotsq(v, m_epsilon);
	(*Exy)[0] = coef*Bessel::AiP(evv)*Bessel::Ai(evv+m_UVtgt[0]);
	(*Exy)[1] = coef*Bessel::Ai(evv)*Bessel::Ai(evv+m_UVtgt[0])*v/sqrt(evv);
	return (*Exy)[0];
}

void SourceProfile::AllocateProfileEconv(bool isalloc)
{
	if (m_camp->IsEsingle() || m_eparray.size() == 1){
		f_SpatialProfileSingle(0, &m_F[0], 0, isalloc);
		return;
	}

	vector<vector<double>> ws;
	double deavg = m_eparray[1]-m_eparray[0], eprof;

#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(2);
	if(!AllocSrcEconv.empty()){
		debug_out.open(AllocSrcEconv);
	}
	int nc[2];
#endif

	double eptarget = m_camp->GetTargetEnergy();
	for(int ne = 0; ne < m_eparray.size(); ne++){
		m_camp->SetTargetEnergyIndex(ne);
		if(ne == 0){
			f_SpatialProfileSingle(0, &m_F[0], isalloc);
		}
		else{
			f_SpatialProfileSingle(0, &ws, 0, false);
		}
		eprof = m_camp->EnergyProfile(eptarget, m_eparray[ne], deavg)*deavg;
#ifdef _DEBUG
		if (!AllocSrcEconv.empty()){
			if(ne == 0){
				nc[0] = (m_spmesh[0][0]-1)/2;
				nc[1] = (m_spmesh[1][0]-1)/2;
				items[0] = m_F[0][nc[0]][nc[1]];
			}
			else{
				items[0] = ws[nc[0]][nc[1]];
			}
			items[1] = eprof;
			PrintDebugItems(debug_out, m_eparray[ne], items);
		}
#endif
		for(int nx = 0; nx < m_spmesh[0][0]; nx++){
			if(ne == 0){
				m_F[0][nx] *= eprof;
			}
			else{
				ws[nx] *= eprof;
				m_F[0][nx] += ws[nx];
			}
		}
		m_status->AdvanceStep(m_layer);
	}

#ifdef _DEBUG
	if(!AllocSrcEconv.empty()){
		debug_out.close();
	}
#endif
}

double SourceProfile::GetFluxAt(double UV[])
{
	double res = 0;
	int nflip = m_Nwiggler > 0 ? 1 : 0;
	double UVr[2], dindex[2], srcpoints[2];

	m_camp->GetUVSrcPoints(srcpoints);
	for(int nc = 0; nc < m_ncomps; nc++){
		for(int n = -nflip; n <= nflip; n += 2){
			if(m_oddpolewig && nc == m_ncomps-1 && n > 0){
				continue;
			}
			int jo = (m_oddpolewig && n < 0) ? 2 : 0;
			for(int j = 0; j < 2; j++){
				if(m_oddpolewig){
					UVr[j] = UV[j]-(n < 0 ? -1.0 : 1.0)*srcpoints[j];
				}
				else{
					UVr[j] = (n < 0 ? -1.0 : 1.0)*UV[j]-srcpoints[j];
				}
				dindex[j] = UVr[j]/m_deltasp[j+jo][nc]+m_halfmeshsp[j+jo][nc];
			}
			if(m_oddpolewig && n < 0){
				res += lagrange2d(m_G[nc], dindex, nullptr);
			}
			else{
				res += lagrange2d(m_F[nc], dindex, nullptr);
			}
		}
	}

	return res;
}

// private functions
bool SourceProfile::f_SpatialProfileSingleFD(
	int nc, vector<vector<double>> *we, vector<vector<double>> *wf)
	// spatial profile given by Fraunhofer diffraction
{
	double adxy[2]; // interval for angular-spatial profile
	double hdxy[2]; // interval for source profile
	double uv[2];
	double dUVduv; // conversion from u,v to U,V (normalized distance from the wiggler center)
	double dl[2];
	double coef;
	double ewxy[4];

	double adelta[2];
	int amesh[2];
	double aflux = m_camp->GetAprofPrms(amesh, adelta);

	dUVduv = fabs(m_camp->GetOmegaWiggler(nc, m_polarity));
	for(int j = 0; j < 2; j++){
		adxy[j] = adelta[j]*dUVduv;
		hdxy[j] = m_deltasp[j][m_ncomps];
	}
	dl[0] = fabs(m_camp->GetOmegaWiggler(nc+0.25, m_polarity))+INFINITESIMAL;
	dl[1] = fabs(m_camp->GetOmegaWiggler(nc-0.25, m_polarity))+INFINITESIMAL;
	dl[0] = max(dl[0]/dl[1], dl[1]/dl[0]);
	if(adxy[0] < hdxy[0]*3.0 || adxy[1] < hdxy[1]*3.0 || dl[0] > SQRT2){
		return false;
	}

	for(int j = 0; j < 2; j++){
		m_spmesh[j][nc] = amesh[j];
		m_deltasp[j][nc] = adxy[j];
		m_halfmeshsp[j][nc] = (m_spmesh[j][nc]-1)/2;
		if (wf != nullptr){
			m_spmesh[j+2][nc] = amesh[j];
			m_deltasp[j+2][nc] = adxy[j];
			m_halfmeshsp[j+2][nc] = (m_spmesh[j+2][nc]-1)/2;
		}
	}

	coef = m_sflux/aflux/dUVduv/dUVduv;
	if(we->size() < m_spmesh[0][nc]){
		we->resize(m_spmesh[0][nc]);
	}
	if(wf != nullptr){
		if(wf->size() < m_spmesh[0][nc]){
			wf->resize(m_spmesh[0][nc]);
		}
	}
#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(2);
	if(!AllocSrcFD.empty()){
		debug_out.open(AllocSrcFD);
	}
#endif
	for(int nx = 0; nx < m_spmesh[0][nc]; nx++){
		if((*we)[nx].size() < m_spmesh[1][nc]){
			(*we)[nx].resize(m_spmesh[1][nc]);
		}
		if(wf != nullptr){
			if((*wf)[nx].size() < m_spmesh[1][nc]){
				(*wf)[nx].resize(m_spmesh[1][nc]);
			}
		}
		uv[0] = (double)(nx-m_halfmeshsp[0][nc])*m_deltasp[0][nc]/dUVduv;
		for(int ny = 0; ny < m_spmesh[1][nc]; ny++){
			uv[1] = (double)(ny-m_halfmeshsp[1][nc])*m_deltasp[1][nc]/dUVduv;
			if(m_camp->GetExyAmplitude(uv, ewxy)){
				(*we)[nx][ny] = hypotsq(ewxy, 4)*coef;
			}
			else{
				(*we)[nx][ny] = 0.0;
			}
			if(wf != nullptr){
				(*wf)[nx][ny] = (*we)[nx][ny];
			}
#ifdef _DEBUG
			if(!AllocSrcFD.empty()){
				items[0] = uv[1]*dUVduv;
				items[1] = (*we)[nx][ny];
				PrintDebugItems(debug_out, uv[0]*dUVduv, items);
			}
#endif
		}
	}
#ifdef _DEBUG
	if(!AllocSrcFD.empty()){
		debug_out.close();
	}
#endif
	return true;
}

void SourceProfile::f_SpatialProfileSingle(int nc, vector<vector<double>> *ws,	
	double de_e1st, bool isalloc, int rank, int mpiprocesses, bool issec)
{
	double duv[2], omega = 0, dUV[2], uv[2], phi, ewxy[4], csn[2], ewmaxr, Ueps;
	double dinterv[2], halfrange[2];
	int Nnh = 1, N, nh;

	m_camp->GetRangePrms(halfrange, dinterv);

	if(m_Nwiggler > 0){
		if(nc < 0){
			omega = 0;
			nc = m_ncomps;
		}
		else{
			omega = m_camp->GetOmegaWiggler(nc, m_polarity);
		}
	}

	for(int j = 0; j < 2; j++){
		if(m_Nwiggler > 0){
			duv[j] = min(dinterv[j], PId2/(INFINITESIMAL+fabs(omega))/halfrange[j]);
		}
		else{
			duv[j] = dinterv[j];
		}
		if(!isalloc){
			dUV[j] = PI2/(duv[j]*(double)m_nfft[j]);
		}
	}

	int jo = issec ? 2 : 0;
	double exrange = 0.5*(1.0+(double)m_acclevel);
	for(int j = 0; j < 2 && isalloc; j++){
		m_nfft[j] = 1;
		while(duv[j]*(double)m_nfft[j] < 2.0*halfrange[j]*exrange){
			m_nfft[j] <<= 1;
		}
		dUV[j] = PI2/(duv[j]*(double)m_nfft[j]);
		if(m_nfft[j] != m_nfftcurr[j]){
			if (m_fft[j] != nullptr){
				delete m_fft[j];
			}
			m_fft[j] = new FastFourierTransform(1, m_nfft[j]);
			if (m_wsdatax[j] != nullptr){
				delete[] m_wsdatax[j];
			}
			if (m_wsdatay[j] != nullptr){
				delete[] m_wsdatay[j];
			}
			m_wsdatax[j] = new double[m_nfft[j]*2];
			m_wsdatay[j] = new double[m_nfft[j]*2];
			m_nfftcurr[j] = m_nfft[j];
		}

		if(m_Nwiggler > 0){
			uv[1-j] = 0;
			double ewmax = 0;
			bool isex = false;
			for(int n = 0; n < m_nfft[j]; n++){
				int ixy = fft_index(n, m_nfft[j], 1);
				uv[j] = (double)ixy*duv[j];
				if(!m_camp->GetExyAmplitude(uv, ewxy)){
					for(int i = 0; i < 2; i++){
						m_wsdatax[j][2*n+i] = m_wsdatay[j][2*n+i] = 0.0;
					}
					continue;
				}
				phi = -omega*uv[j]*uv[j]*0.5;
				csn[0] = cos(phi);
				csn[1] = sin(phi);

				complex_product(ewxy, csn, m_wsdatax[j]+2*n);
				ewmaxr = hypotsq(ewxy[0], ewxy[1]);
				if(ewmax < ewmaxr){
					ewmax = ewmaxr;
					isex = true;
				}
				complex_product(ewxy+2, csn, m_wsdatay[j]+2*n);
				ewmaxr = hypotsq(ewxy[2], ewxy[3]);
				if(ewmax < ewmaxr){
					ewmax = ewmaxr;
					isex = false;
				}
			}
			if(isex){
				m_fft[j]->DoFFT(m_wsdatax[j]);
				m_nskip[j] = f_GetSkipNumber(m_wsdatax[j], m_nfft[j]);
			}
			else{
				m_fft[j]->DoFFT(m_wsdatay[j]);
				m_nskip[j] = f_GetSkipNumber(m_wsdatay[j], m_nfft[j]);
			}
		}
		else{
			m_nskip[j] = 1;
		}
		m_deltasp[j+jo][nc] = dUV[j]*m_nskip[j];
		m_halfmeshsp[j+jo][nc] = m_nfft[j]/2/m_nskip[j];
		m_spmesh[j+jo][nc] = 2*m_halfmeshsp[j+jo][nc]+1;
	}

	if(m_xdata.size() < m_spmesh[jo][nc]){
		m_xdata.resize(m_spmesh[jo][nc], nullptr);
		m_ydata.resize(m_spmesh[jo][nc], nullptr);
	}
	for (int nx = 0; nx < m_spmesh[jo][nc]; nx++){
		if(m_xdata[nx] != nullptr){
			delete[] m_xdata[nx];
		}
		if(m_ydata[nx] != nullptr){
			delete[] m_ydata[nx];
		}
		m_xdata[nx] = new double[m_nfft[1]*2];
		m_ydata[nx] = new double[m_nfft[1]*2];
	}

	m_status->SetSubstepNumber(m_layer+1, (m_nfft[1]+m_spmesh[jo][nc])/mpiprocesses);
	m_status->PutSteps(m_layer+1, 0);

	bool nonzero = false;

	if(m_isund){
		m_camp->GetSnPrms(&N, &nh, &Ueps);
		Nnh = N*nh;
	}

	for(int ny = 0; ny < m_nfft[1]; ny++){
		int iy = fft_index(ny, m_nfft[1], 1);
		uv[1] = (double)iy*duv[1];
		int currrank = ny%mpiprocesses;
		if(currrank != rank){
			continue;
		}
		for(int nx = 0; nx < m_nfft[0]; nx++){
			int ix = fft_index(nx, m_nfft[0], 1);
			uv[0] = (double)ix*duv[0];
			if(!m_camp->GetExyAmplitude(uv, ewxy)){
				for(int j = 0; j < 2; j++){
					m_wsdatax[0][2*nx+j] = m_wsdatay[0][2*nx+j] = 0.0;
				}
				continue;
			}
			if(m_Nwiggler > 0){
				phi = -omega*uv[0]*uv[0]*0.5;
				csn[0] = cos(phi);
				csn[1] = sin(phi);
				complex_product(ewxy  , csn, m_wsdatax[0]+2*nx);
				complex_product(ewxy+2, csn, m_wsdatay[0]+2*nx);
			}
			else{
				double snc = 1.0;
				if (m_isund){
					double uv2 = hypotsq(uv[0], uv[1]);
					double snarg = uv2+(Ueps+de_e1st)*(1.0+uv2/(double)Nnh);
					snc = sinc(PI*snarg);
				}
				for(int j = 0; j < 2; j++){
					m_wsdatax[0][2*nx+j] = ewxy[j]*snc;
					m_wsdatay[0][2*nx+j] = ewxy[j+2]*snc;
				}
			}
			nonzero = true;
		}
		if(nonzero){
			m_fft[0]->DoFFT(m_wsdatax[0]);
			m_fft[0]->DoFFT(m_wsdatay[0]);
		}
		for(int nxc = -m_halfmeshsp[jo][nc]; nxc <= m_halfmeshsp[jo][nc]; nxc++){
			int ix = fft_index(nxc*m_nskip[0], m_nfft[0], -1);
			int idx = nxc+m_halfmeshsp[jo][nc];
			for(int i = 0; i < 2; i++){
				m_xdata[idx][2*ny+i] = m_wsdatax[0][2*ix+i]*duv[0];
				m_ydata[idx][2*ny+i] = m_wsdatay[0][2*ix+i]*duv[0];
			}
		}
		m_status->AdvanceStep(m_layer+1);
	}

	double *wsx = nullptr, *wsy = nullptr;
	if(mpiprocesses > 1){
		int ndata = max(m_spmesh[jo][nc], m_spmesh[1+jo][nc]);
		wsx = new double[ndata*2];
		wsy = new double[ndata*2];
		for(int i = 0; i < 2; i++){
			for (int ny = 0; ny < m_nfft[1]; ny++){
				int currrank = ny%mpiprocesses;
				if (currrank == rank){
					for (int nxc = -m_halfmeshsp[jo][nc]; nxc <= m_halfmeshsp[jo][nc]; nxc++){
						int idx = nxc+m_halfmeshsp[jo][nc];
						wsx[idx] = m_xdata[idx][2*ny+i];
						wsy[idx] = m_ydata[idx][2*ny+i];
					}
				}
				if(m_thread != nullptr){
					m_thread->Bcast(wsx, m_spmesh[jo][nc], MPI_DOUBLE, currrank, rank);
					m_thread->Bcast(wsy, m_spmesh[jo][nc], MPI_DOUBLE, currrank, rank);
				}
				else{
					MPI_Bcast(wsx, m_spmesh[jo][nc], MPI_DOUBLE, currrank, MPI_COMM_WORLD);
					MPI_Bcast(wsy, m_spmesh[jo][nc], MPI_DOUBLE, currrank, MPI_COMM_WORLD);
				}
				if (currrank != rank){
					for (int nxc = -m_halfmeshsp[jo][nc]; nxc <= m_halfmeshsp[jo][nc]; nxc++){
						int idx = nxc+m_halfmeshsp[jo][nc];
						m_xdata[idx][2*ny+i] = wsx[idx];
						m_ydata[idx][2*ny+i] = wsy[idx];
					}
				}
			}
		}
	}

#ifdef _DEBUG
	if(!AllocSrcP1DEnd.empty() && rank == 0){
		ofstream debug_out(AllocSrcP1DEnd);
		vector<double> items(7);
		double dUV = 1.0/(m_nfft[0]*duv[0]);
		for (int ny = -m_nfft[1]/2; ny <= m_nfft[1]/2; ny += m_nskip[1]){
//		for (int ny = 0; ny <= 0; ny += m_nskip[1]){
			int iy = fft_index(ny, m_nfft[1], -1);
			uv[1] = (double)ny*duv[1];
//			for (int nxc = -m_halfmeshsp[jo][nc]; nxc <= m_halfmeshsp[jo][nc]; nxc+=4){
			for (int nxc = 0; nxc <= 0; nxc++){
				int idx = nxc+m_halfmeshsp[jo][nc];
				items[0] = uv[1];
				items[3] = items[6] = 0;
 				for(int j = 0; j < 2; j++){
					items[j+1] = m_xdata[idx][2*iy+j];
					items[j+4] = m_ydata[idx][2*iy+j];
					items[3] += items[j+1]*items[j+1];
					items[6] += items[j+4]*items[j+4];
				}
				PrintDebugItems(debug_out, (double)nxc*dUV, items);
			}
		}
	}
#endif

	if(ws->size() < m_spmesh[jo][nc]){
		ws->resize(m_spmesh[jo][nc]);
	}
	int mesh2 = m_spmesh[1+jo][nc];
	for(int nx = 0; nx < m_spmesh[jo][nc]; nx++){
		if((*ws)[nx].size() < mesh2){
			(*ws)[nx].resize(mesh2);
		}
	}

	if(nc == m_ncomps){
		m_sflux = 0.0;
	}
	for(int nxc = -m_halfmeshsp[jo][nc]; nxc <= m_halfmeshsp[jo][nc]; nxc++){
		int idx = nxc+m_halfmeshsp[jo][nc];
		int currrank = idx%mpiprocesses;
		if(currrank != rank){
			continue;
		}
		for(int ny = 0; ny < m_nfft[1]; ny++){
			int iy = fft_index(ny, m_nfft[1], 1);
			if(m_Nwiggler > 0){
				uv[1] = (double)iy*duv[1];
				phi = -omega*uv[1]*uv[1]*0.5;
				csn[0] = cos(phi);
				csn[1] = sin(phi);
				complex_product(m_xdata[idx]+2*ny, csn, m_wsdatax[1]+2*ny);
				complex_product(m_ydata[idx]+2*ny, csn, m_wsdatay[1]+2*ny);
			}
			else{
				for(int j = 0; j < 2; j++){
					m_wsdatax[1][2*ny+j] = m_xdata[idx][2*ny+j];
					m_wsdatay[1][2*ny+j] = m_ydata[idx][2*ny+j];
				}
			}
		}
		m_fft[1]->DoFFT(m_wsdatax[1]);
		m_fft[1]->DoFFT(m_wsdatay[1]);
		for(int nyc = -m_halfmeshsp[1+jo][nc]; nyc <= m_halfmeshsp[1+jo][nc]; nyc++){
			int iy = fft_index(nyc*m_nskip[1], m_nfft[1], -1);
			int idy = nyc+m_halfmeshsp[1+jo][nc];
			(*ws)[idx][idy] = 
				hypotsq(m_wsdatax[1][2*iy]*duv[1], m_wsdatax[1][2*iy+1]*duv[1])+
				hypotsq(m_wsdatay[1][2*iy]*duv[1], m_wsdatay[1][2*iy+1]*duv[1]);
			if(nc == m_ncomps){
				m_sflux += (*ws)[idx][idy];
			}	
		}
		m_status->AdvanceStep(m_layer+1);
	}

	if(nc == m_ncomps){
		m_sflux *= m_deltasp[0][m_ncomps]*m_deltasp[1][m_ncomps];
	}

	if(mpiprocesses > 1){
		for(int nxc = -m_halfmeshsp[jo][nc]; nxc <= m_halfmeshsp[jo][nc]; nxc++){
			int idx = nxc+m_halfmeshsp[jo][nc];
			int currrank = idx%mpiprocesses;
			if (currrank == rank){
				for (int nyc = -m_halfmeshsp[1+jo][nc]; nyc <= m_halfmeshsp[1+jo][nc]; nyc++){
					int idy = nyc+m_halfmeshsp[1+jo][nc];
					wsx[idy] = (*ws)[idx][idy];
				}
			}
			if(m_thread != nullptr){
				m_thread->Bcast(wsx, m_spmesh[1+jo][nc], MPI_DOUBLE, currrank, rank);
			}
			else{
				MPI_Bcast(wsx, m_spmesh[1+jo][nc], MPI_DOUBLE, currrank, MPI_COMM_WORLD);
			}
			if(currrank != rank){
				for (int nyc = -m_halfmeshsp[1+jo][nc]; nyc <= m_halfmeshsp[1+jo][nc]; nyc++){
					int idy = nyc+m_halfmeshsp[1+jo][nc];
					(*ws)[idx][idy] = wsx[idy];
				}
			}
		}
		if (nc == m_ncomps){
			double sum;
			if(m_thread != nullptr){
				m_thread->Allreduce(&m_sflux, &sum, 1, MPI_DOUBLE, MPI_SUM, rank);
			}
			else{
				MPI_Allreduce(&m_sflux, &sum, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
			}
			m_sflux = sum;
		}
		delete[] wsx;
		delete[] wsy;
	}

	if(m_Nwiggler > 0 
		&&nc != m_ncomps && fabs(omega) < 1e-6
		&& m_sigmaUV[0] > INFINITESIMAL
		&& m_sigmaUV[1] > INFINITESIMAL){ // central pole, apply smoothing
		int nsmfft[2];
		double cutoff[2];
		for(int j = 0; j < 2; j++){
			nsmfft[j] = fft_number(m_spmesh[j+jo][nc], 1);
			cutoff[j] = max(PI2*2.0/m_spmesh[j+jo][nc], m_deltasp[j+jo][nc]/(m_sigmaUV[j]*0.1));
		}
		double **datasm = new double*[nsmfft[0]];
		for(int n = 0; n < nsmfft[0]; n++){
			datasm[n] = new double[nsmfft[1]*2];
			for(int m = 0; m < nsmfft[1]; m++){
				if(n < m_spmesh[jo][nc] && m < m_spmesh[1+jo][nc]){
					datasm[n][2*m] = (*ws)[n][m];
				}
				else{
					datasm[n][2*m] = 0;
				}
				datasm[n][2*m+1] = 0;
			}
		}
		FastFourierTransform smfft(2, nsmfft[0], nsmfft[1]);
		smfft.DoFFTFilter2D(datasm, cutoff, true);
		for(int n = 0; n < m_spmesh[jo][nc]; n++){
			for(int m = 0; m < m_spmesh[1+jo][nc]; m++){
				(*ws)[n][m] = datasm[n][2*m];
			}
			delete[] datasm[n];
		}
		delete[] datasm;
	}

#ifdef _DEBUG
	if(!AllocSrcP2DEnd.empty() && rank == 0){
		ofstream debug_out(AllocSrcP2DEnd);
		vector<double> items(2);
		for (int nx = -m_halfmeshsp[jo][nc]; nx <= m_halfmeshsp[jo][nc]; nx++){
			for (int ny = 0; ny <= 0; ny++){
//			for (int ny = -m_halfmeshsp[1+jo][nc]; ny <= m_halfmeshsp[1+jo][nc]; ny++){
				int ixx = nx+m_halfmeshsp[jo][nc];
				int iyy = ny+m_halfmeshsp[1+jo][nc];
				items[0] = ny*m_deltasp[1+jo][nc];
				items[1] = (*ws)[ixx][iyy];
				PrintDebugItems(debug_out, nx*m_deltasp[jo][nc], items);
			}
		}
		debug_out.close();
	}
#endif
}

void SourceProfile::f_AllocateProfileUndulator()
{
	int N, nh;
	double Ueps;
	m_camp->GetSnPrms(&N, &nh, &Ueps);
	double erange = m_camp->GetEspreadRange();
	if(erange == 0){
		f_SpatialProfileSingle(0, &m_F[0]);
		return;
	}

	vector<vector<double>> ws;
	double eptarget = m_camp->GetTargetEnergy();
	double eprange = eptarget*2.0*erange;
	double dep = 1.0/4.0/(double)(1+m_acclevel)/(N*nh)*eptarget;
	double eprof, de_e1st, evar, e1st = m_camp->GetE1st();
	int nmesh = (int)ceil(2.0*eprange/dep);

#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(2);
	if(!AllocSrcEconv.empty()){
		debug_out.open(AllocSrcEconv);
	}
	int nc[2];
#endif

	m_status->SetSubstepNumber(m_layer, 2*nmesh+1);
	for(int ne = 0; ne < 2*nmesh; ne++){
		evar = eptarget+dep*(ne-nmesh);
		de_e1st = dep*(ne-nmesh)/e1st*N;
		if(ne == 0){
			f_SpatialProfileSingle(0, &m_F[0], de_e1st);
		}
		else{
			f_SpatialProfileSingle(0, &ws, de_e1st, false);
		}
		eprof = m_camp->EnergyProfile(eptarget, evar, dep)*dep;
#ifdef _DEBUG
		if (!AllocSrcEconv.empty()){
			if(ne == 0){
				nc[0] = (m_spmesh[0][0]-1)/2;
				nc[1] = (m_spmesh[1][0]-1)/2;
				items[0] = m_F[0][nc[0]][nc[1]];
			}
			else{
				items[0] = ws[nc[0]][nc[1]];
			}
			items[1] = eprof;
			PrintDebugItems(debug_out, evar, items);
		}
#endif
		for(int nx = 0; nx < m_spmesh[0][0]; nx++){
			if(ne == 0){
				m_F[0][nx] *= eprof;
			}
			else{
				ws[nx] *= eprof;
				m_F[0][nx] += ws[nx];
			}
		}
		m_status->AdvanceStep(m_layer);
	}

#ifdef _DEBUG
	if(!AllocSrcEconv.empty()){
		debug_out.close();
	}
	if(!AllocSrcUnd.empty()){
		ofstream debug_out(AllocSrcUnd);
		vector<double> items(2);
		for(int nx = -m_halfmeshsp[0][0]; nx <= m_halfmeshsp[0][0]; nx++){
			for(int ny = -m_halfmeshsp[1][0]; ny <= m_halfmeshsp[1][0]; ny++){
				items[0] = ny*m_deltasp[1][0];
				items[1] = m_F[0][nx+m_halfmeshsp[0][0]][ny+m_halfmeshsp[1][0]];
				PrintDebugItems(debug_out, nx*m_deltasp[0][0], items);
			}
		}
		debug_out.close();
	}
#endif

}

void SourceProfile::f_AllocateProfileWiggler(int rank, int mpiprocesses)
{
	vector<vector<double>> dummy;
	f_SpatialProfileSingle(-1, &dummy, 0, true, rank, mpiprocesses);
	m_status->AdvanceStep(m_layer);

	vector<int> dirper;
	for(int nc = 0; nc < m_ncomps; nc++){
		if(f_SpatialProfileSingleFD(nc, &m_F[nc], m_oddpolewig?&m_G[nc]:nullptr)){
			m_status->AdvanceStep(m_layer);
			if (m_oddpolewig){
				m_status->AdvanceStep(m_layer);
			}
			continue;
		}
		dirper.push_back(nc);
	}

	for(int ppr = 0; ppr < dirper.size(); ppr++){
		int nc = dirper[ppr];
		f_SpatialProfileSingle(nc, &m_F[nc], 0, true, rank, mpiprocesses);
		m_status->AdvanceStep(m_layer);
		if(m_oddpolewig){
			m_polarity = -1.0;
			f_SpatialProfileSingle(nc, &m_G[nc], 0, true, rank, mpiprocesses, true);
			m_status->AdvanceStep(m_layer);
			m_polarity = 1.0;
		}
	}
}

int SourceProfile::f_GetSkipNumber(double *data, int nfft)
{
	int nskip = 0;
	double eps = 0, smax = 0, dsmax, ssa = 0, ssb, tgtacc;

	for(int n = -nfft/2; n <= nfft/2; n++){
		int ix = fft_index(n, nfft, -1);
		smax = max(smax, hypotsq(data[2*ix], data[2*ix+1]));
	}

	tgtacc = 0.04/(double)max(1, m_acclevel/4);

	while(eps < tgtacc){
		if(nskip == 0){
			nskip = 1;
		}
		else{
			nskip <<= 1;
		}
		dsmax = 0.0;
		for(int n = -nfft/2; n <= nfft/2; n+= nskip){
			int ix = fft_index(n, nfft, -1);
			if(n == -nfft/2){
				ssa = hypotsq(data[2*ix], data[2*ix+1]);
			}
			else{
				ssb = hypotsq(data[2*ix], data[2*ix+1]);
				dsmax = max(dsmax, fabs(ssa-ssb));
				ssa = ssb;
			}
		}
		eps = dsmax/smax;
	}
	return nskip;
}

void SourceProfile::f_ClearPointers()
{
	for(int j = 0; j < 2; j++){
		if(m_fft[j] != nullptr){
			delete m_fft[j];
			m_fft[j] = nullptr;
		}
		if(m_wsdatax[j] != nullptr){
			delete[] m_wsdatax[j];
			m_wsdatax[j] = nullptr;
		}
		if(m_wsdatay[j] != nullptr){
			delete[] m_wsdatay[j];
			m_wsdatay[j] = nullptr;
		}
	}
	for(int nx = 0; nx < m_xdata.size(); nx++){
		delete[] m_xdata[nx];
		delete[] m_ydata[nx];
	}

}
