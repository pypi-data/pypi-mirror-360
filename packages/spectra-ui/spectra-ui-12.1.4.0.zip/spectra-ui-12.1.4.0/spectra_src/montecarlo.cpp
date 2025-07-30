#include "montecarlo.h"
#include "trajectory.h"
#include "complex_amplitude.h"
#include "flux_density.h"
#include "orbit_components_operation.h"
#include "common.h"
#include "json_writer.h"
#include "undulator_flux_far.h"
#include "density_fixed_point.h"
#include "wigner_function.h"
#include "source_profile.h"
#include "filter_operation.h"
#include "particle_generator.h"
#include "json_writer.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

#define MC_SMOOTH_GAUSS 0.333 
// smoothing factor: number of grid for 1 sigma

string MC_Particles;
string MC_CurrentResult;
string MC_SmCurrentResult;
string MC_ParticleResult;
string MC_IndivParticleResult;

MonteCarlo::MonteCarlo(SpectraSolver &spsolver)
	: SpectraSolver(spsolver)
{
#ifdef _DEBUG
//MC_Particles  = "..\\debug\\mc_particles.dat";
//MC_IndivParticleResult  = "..\\debug\\mc_particles_result.dat";
MC_CurrentResult = "..\\debug\\mc_current_result.dat";
//MC_ParticleResult = "..\\debug\\mc_particle_result.dat";
//MC_SmCurrentResult = "..\\debug\\mc_current_result_smooth.dat";
#endif

	m_accb[zeroemitt_] =  true;
	m_eps = m_accuracy_f[accconvMC_];

	m_camp = nullptr;
	m_filter = nullptr;
	m_densfix = nullptr;
	m_wigctrl = nullptr;
	m_srcprofile = nullptr;
	m_nitems = GetNumberOfItems();
	m_smnfft[0] = m_smnfft[1] = 0;
	m_smws1d = nullptr;
	m_smws2d = nullptr;
	m_smfft = nullptr;
	m_iseconvb = false;

	m_isfixpoint = IsFixedPoint();
	m_issurfacepd = contains(m_calctype, menu::spdens);

	m_trajec = new Trajectory(*this);
	if(m_isfilter){
		m_filter = new FilterOperation(*this);
	}

	if(m_issrcpoint){
		m_camp = new ComplexAmplitude(*this);
		m_dXYdUV = m_camp->GetConvUV();
		if(contains(m_calctype, menu::wigner)){
			m_wigctrl = new WignerFunctionCtrl(*this, m_isenergy?2:1, m_camp);
		}
		else{
			m_srcprofile = new SourceProfile(m_camp, m_accuracy[accinobs_],
				m_iswiggler?m_N:0, m_isoddpole, m_calcstatus, 1);
		}
	}
	else{
		if (!m_isgaussbeam){
			// energy spread convolution is done also with MonteCarlo 
			m_iszspread = m_accb[zerosprd_] = true;
		}
		m_densfix = new DensityFixedPoint(*this, m_trajec, m_filter);
	}
	m_particle = new ParticleGenerator(spsolver, m_trajec);
}

MonteCarlo::~MonteCarlo()
{
	if(m_camp != nullptr){
		delete m_camp;
	}
	if(m_filter != nullptr){
		delete m_filter;
	}
	if(m_trajec != nullptr){
		delete m_trajec;
	}
	if(m_densfix != nullptr){
		delete m_densfix;
	}
	if(m_wigctrl != nullptr){
		delete m_wigctrl;
	}
	if(m_srcprofile != nullptr){
		delete m_srcprofile;
	}
	if(m_smfft != nullptr){
		delete m_smfft;
	}
	if(m_smws1d != nullptr){
		delete[] m_smws1d;
	}
	if(m_smws2d != nullptr){
		for(int n = 0; n < m_smnfft[0]; n++){
			delete[] m_smws2d[n];
		}
		delete[] m_smws2d;
	}
}

double MonteCarlo::AllocAndGetError(double nNt)
{
	m_ws[1] /= (double)nNt;

	double vmax = f_GetMaxWS(1);
	if(vmax == 0){
		return true;
	}
#ifdef _DEBUG
	f_DumpCurrent(MC_CurrentResult);
#endif
	if(m_smdim > 0 && m_smnfft[0] > 1 && !m_iseconvb){
//		f_Smoothing();
	}
#ifdef _DEBUG
	f_DumpCurrent(MC_SmCurrentResult);
#endif

	m_ws[0] -= m_ws[1];
	double difmax = f_GetMaxWS(0);
	m_ws[0] = m_ws[1];
	return difmax/vmax;
}

void MonteCarlo::RunMonteCarlo(int layer)
{
	vector<Particle> particles;
	int Nm = PARTICLES_PER_STEP;

	if(contains(m_calctype, menu::pdenss) 
		|| contains(m_calctype, menu::ppower)
		|| contains(m_calctype, menu::spdens))
	{
		Nm /= 10;
	}

	vector<int> mpisteps, mpiinistep, mpifinstep;
	double err = 5.0, errnew, nGoal;

	m_calcstatus->SetTargetAccuracy(layer, m_eps);
	m_calcstatus->SetCurrentAccuracy(layer, err);
	m_calcstatus->SetSubstepNumber(layer, Nm);

	Particle refparticle;
	for(int j = 0; j < 2; j++){
		refparticle._obs[j] = m_center[j];
	}
	f_RunSingle(refparticle, true);

	m_ndatatotal = (int)m_ws[1].size();

	double nNt = 0;
	fill(m_ws[1].begin(), m_ws[1].end(), 0.0);
	m_sum = m_ws[1];
	m_ws[0] = m_ws[1];

	if(m_mpiprocesses > 1){
		for(int j = 0; j < 2; j++){
			m_wsmpi[j] = new double[m_ndatatotal];
		}
	}

	m_particle->Init();
	int irep = 0;
	do{
		int Np = m_particle->Generate(particles, Nm/2, 
			m_issrcpoint || !m_isgaussbeam, m_rectslit || m_circslit);
		if(m_accuracy_b[acclimMCpart_]){
			int nlim = (int)floor(m_accuracy_f[accMCpart_]-nNt+0.5);
			if(Np > nlim){
				Np = nlim;
				m_calcstatus->SetTargetAccuracy(layer, 1);
				m_calcstatus->SetCurrentAccuracy(layer, 1);
				m_calcstatus->ResetCurrentStep(layer);
				m_calcstatus->SetSubstepNumber(layer, Np);
			}
		}

#ifdef _DEBUG
		if(m_rank == 0 && !MC_Particles.empty()){
			vector<double> pardump(6);
			ofstream debug_outp;
			debug_outp.open(MC_Particles, nNt < 2 ? ios_base::out : ios_base::app);
			for (int p = 0; p < Np; p++){
				for (int j = 0; j < 2; j++){
					pardump[j] = particles[p]._xy[j];
					pardump[j+2] = particles[p]._qxy[j];
					pardump[j+4] = particles[p]._tE[j];
				}
				PrintDebugItems(debug_outp, (double)p, pardump);
			}
			debug_outp.close();
		}
		vector<double> buf(Np);
#endif

		mpi_steps(Np, 1, m_mpiprocesses, &mpisteps, &mpiinistep, &mpifinstep);
		for(int p = 0; p < Np; p++){
			if(p < mpiinistep[m_rank] || p > mpifinstep[m_rank]){
				continue;
			}
			f_RunSingle(particles[p]);

#ifdef _DEBUG
			f_DumpCurrent(MC_ParticleResult, &particles[p]);
#endif

			m_sum += m_ws[1];
			m_calcstatus->AdvanceStep(layer, m_mpiprocesses);

#ifdef _DEBUG
			if(m_rank == 0 && !MC_IndivParticleResult.empty()){
				buf[p] = m_ws[1][0];
			}
#endif
		}
		m_calcstatus->SetCurrentOrigin(layer);
	
#ifdef _DEBUG
		if(m_rank == 0 && !MC_IndivParticleResult.empty()){
			vector<double> pardump(7);
			ofstream debug_outp;
			debug_outp.open(MC_IndivParticleResult, nNt < 2?ios_base::out:ios_base::app);
			for (int p = 0; p < Np; p++){
				for (int j = 0; j < 2; j++){
					pardump[j] = particles[p]._xy[j];
					pardump[j+2] = particles[p]._qxy[j];
					pardump[j+4] = particles[p]._tE[j];
				}
				pardump[6] = buf[p];
				PrintDebugItems(debug_outp, (double)p, pardump);
			}
			debug_outp.close();
		}
#endif

		if(m_mpiprocesses > 1){
			for(int n = 0; n < m_ndatatotal; n++){
				m_wsmpi[0][n] = m_sum[n];
			}
			if(m_thread != nullptr){
				m_thread->Allreduce(m_wsmpi[0], m_wsmpi[1], m_ndatatotal, MPI_DOUBLE, MPI_SUM, m_rank);
			}
			else{
				MPI_Allreduce(m_wsmpi[0], m_wsmpi[1], m_ndatatotal, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
			}
			for(int n = 0; n < m_ndatatotal; n++){
				m_ws[1][n] = m_wsmpi[1][n];
			}
		}
		else{
			m_ws[1] = m_sum;
		}

		if(m_iseconvb && !m_iszspread){
			f_EnergyConvolution();
		}
		nNt += (double)Np;
		errnew = AllocAndGetError(nNt);

		if(Np != Nm){
			// reached the maximum or imported particles
			break;
		}
		if(irep > 0){
			Nm <<= 1;
		}
		irep++;

		m_calcstatus->SetCurrentAccuracy(layer, errnew);
		double errn = min(1.0, err);
		if(errnew >= errn){
			nGoal = Np*8;
		}
		else{
			nGoal = Np*log(m_eps)/log(errnew/errn)/2;
		}
		nGoal = max((double)Nm*2.0, nGoal);

		m_calcstatus->SetSubstepNumber(layer, (int)ceil(nGoal));
		err = errnew;

//------->>>>>>>
		if(m_rank == 0){
			cout << endl;
			cout << scientific << "Particles = " << (int)floor(0.5+nNt) << ", Error = " << errnew << endl;
		}
    } while(err > m_eps);

	if(m_mpiprocesses > 1){
		for(int j = 0; j < 2; j++){
			delete[] m_wsmpi[j];
		}
	}

	if(m_rectslit || m_circslit){
		double area = m_rectslit ? m_slitapt[0]*m_slitapt[1] : 
			PI*(m_slitr[1]*m_slitr[1]-m_slitr[0]*m_slitr[0]);
		for(int n = 0; n < m_ndatatotal; n++){
			m_ws[1][n] *= area;
		}
	}
}

void MonteCarlo::GetSpectrum(
	vector<double> &energy, vector<vector<double>> &flux,
	int layer, int rank, int mpiprocesses,
	vector<string> &subresults, vector<string> &categories)
{
	if(m_densfix != nullptr){
		m_densfix->GetEnergyArray(m_ealloc);
	}
	m_smdim = 1;
	m_isaxis = false;
	m_nbundle = m_nitems;
	if(m_densfix != nullptr){
		m_mesh[0] = (int)m_ealloc.size();
	}
	else{
		m_mesh[0] = (int)m_eparray.size();
	}
	m_mesh[1] = 1;
	m_iseconvb = !m_issrcpoint;

	RunMonteCarlo(0);

	energy = m_eparray;
	flux.resize(m_nitems);
	if(m_wigctrl != nullptr){
		flux[0] = m_ws[1];
		return;
	}

	for(int j = 0; j < m_nitems; j++){
		flux[j].resize(m_eparray.size());
	}

	vector<double> ftmp(4), farr(m_ealloc.size());
	Spline fluxspl[4];
	for(int j = 0; j < 4; j++){
		for(int n = 0; n < m_ealloc.size(); n++){
			farr[n] = m_ws[1][j*m_ealloc.size()+n];
		}
		fluxspl[j].SetSpline((int)m_ealloc.size(), &m_ealloc, &farr);
	}
	for(int n = 0; n < energy.size(); n++){
		for(int j = 0; j < 4; j++){
			ftmp[j] = fluxspl[j].GetOptValue(energy[n]);
		}
		stokes(ftmp);
		for(int j = 0; j < 4; j++){
			flux[j][n] = ftmp[j];
		}
	}
	flux[0] *= GetFluxCoef();

	if(m_isfilter){
		FilterOperation filter(*this);
		vector<double> fflux(energy.size());
		for(int n = 0; n < energy.size(); n++){
			fflux[n] = flux[0][n]*filter.GetTransmissionRateF(energy[n]);
		}
		flux.push_back(fflux);
	}
}

void MonteCarlo::GetSpatialProfile(
	vector<vector<double>> &xy, vector<vector<vector<double>>> &dens,
	int layer, int rank, int mpiprocesses,
	vector<string> &subresults, vector<string> &categories)
{
	ArrangeMeshSettings(m_xyrp, m_xyobs);
	m_obspoints = (int)m_xyobs[0].size();

	m_isaxis = contains(m_calctype, menu::along);
	m_smdim = m_isaxis ? 1 : 2;
	m_nbundle = m_nitems;
	for(int j = 0; j < 2; j++){
		m_mesh[j] = (int)m_xyrp[j].size();
	}
	
	RunMonteCarlo(0);
	xy = m_xyrp;

    double coef;
    if(!m_ispower && !m_isrespow && !m_issrcpoint){
        coef = GetFluxCoef();
    }
    else if(m_issrcpoint){
        coef = m_camp->GetSrcPointCoef();
    }
    else{
        coef = GetPowerCoef();
    }

	if(contains(m_calctype, menu::along)){
		vector<vector<double>> dens1d(m_nitems);
		for(int j = 0; j < 2; j++){
			for(int i = 0; i < m_nitems; i++){
				dens1d[i].resize(m_xyrp[j].size());
				for(int n = 0; n < m_xyrp[j].size(); n++){
					dens1d[i][n] = m_ws[1][i*m_obspoints+j*m_xyrp[0].size()+n]*coef;
				}
			}
			dens.push_back(dens1d);
		}
	}
	else{
		int mesh[2], n[2], index;
		for(int j = 0; j < 2; j++){
			mesh[j] = (int)m_xyrp[j].size();
		}
		dens.resize(m_nitems);
		for(int i = 0; i < m_nitems; i++){
			dens[i].resize(mesh[0]);
			for(n[0] = 0; n[0] < mesh[0]; n[0]++){
				dens[i][n[0]].resize(mesh[1]);
				for(n[1] = 0; n[1] < mesh[1]; n[1]++){
					index = i*m_obspoints+n[1]*mesh[0]+n[0];
					dens[i][n[0]][n[1]] = m_ws[1][index]*coef;
				}
			}
		}
	}
	if(contains(m_calctype, menu::fdensa) || contains(m_calctype, menu::fdenss)){
		f_ToStokes(xy, dens);
	}
}

void MonteCarlo::GetSurfacePowerDensity(
		vector<vector<double>> &obs, vector<double> &dens,
		int layer, int rank, int mpiprocesses)
{
	vector<vector<double>> value;
	GetSPDConditions(obs, m_xyz, m_exyz);
	for(int j = 0; j < 2; j++){
		m_mesh[j] = (int)obs[j].size();
	}
	dens.resize(m_xyz.size());
	RunMonteCarlo(0);
    double coef = GetPowerCoef();
	dens = m_ws[1];
	dens *= coef;
}

void MonteCarlo::GetWignerFunction(
	vector<vector<double>> &XY, vector<double> &W,
	int layer, int rank, int mpiprocesses)
{
	vector<vector<double>> xyvar;
	vector<vector<int>> indices;
	vector<int> wigtypes;
	m_wigctrl->GetVariables(wigtypes, xyvar, indices);
	m_smdim = 2;
	m_isaxis = false;
	for(int j = 0; j < 2; j++){
		if(indices.size() > 0){
			m_mesh[j] = (int)xyvar[indices[0][j]].size();
		}
		else{
			m_mesh[j] = 1;
		}
	}
	if(indices.size() > 1){
		m_nbundle = (int)(xyvar[indices[1][0]].size()
			*xyvar[indices[1][1]].size());
	}
	else{
		m_nbundle = 1;
	}

	RunMonteCarlo(0);
	W = m_ws[1];

	XY.clear();
	for(int j = 0; j < indices.size(); j++){
		for (int k = 0; k < indices[j].size(); k++){
			XY.push_back(m_xyrp[indices[j][k]]);
			XY.back() *= 1000.0; // m, rad -> mm, mrad
		}
	}
}

void MonteCarlo::GetFixedPoint(vector<double> &values, 
	int layer, int rank, int mpiprocesses)
{
    double coef;
    if(m_ispower){
        coef = GetPowerCoef();
    }
    else{
        coef = GetFluxCoef();
    }

	m_smdim = 0;
	RunMonteCarlo(0);
	values.resize(m_nitems);
	for(int j = 0; j < m_nitems; j++){
		values[j] = coef*m_ws[1][j];
	}
	if(!m_ispower){
		stokes(values);
	}
}

// private functions
void MonteCarlo::f_RunSingle(Particle &particle, bool init)
{
	OrbitComponents orb;
	orb.SetComponents(&particle);

	m_trajec->AllocateTrajectory(true, false, true, &orb);
	if(init){
		m_trajec->SetReference();
	}
	if(m_camp != nullptr){
		m_camp->UpdateParticle(m_trajec, particle._tE[1]);
	}
	if(m_densfix != nullptr){
		m_densfix->AllocateOrbitComponents(m_trajec);
	}

	if(m_wigctrl != nullptr){
		if(m_isenergy){
			if(init){
				m_ws[1].resize(m_eparray.size());
				m_calcstatus->SetSubstepNumber(1, (int)m_eparray.size());
			}
			for (int n = 0; n < m_eparray.size(); n++){
				m_wigctrl->SetPhotonEnergy(m_eparray[n]);
				m_wigctrl->GetPhaseSpaceProfile(m_xyrp, m_wstmp);
				m_ws[1][n] = m_wstmp[0];
				m_calcstatus->AdvanceStep(1);
			}
		}
		else{
			m_wigctrl->GetPhaseSpaceProfile(m_xyrp, m_ws[1]);
			// m_ws[1][ W[X0~Xn][Y0~Ym][0][0], W[X0~Xn][Y0~Ym][0][1], ..., W[X0~Xn][Y0~Ym][1][0], ...]
		}
	}
	else if(m_srcprofile != nullptr){
		double UV[2];
		if(init){
			m_ws[1].resize(m_obspoints);
			m_srcprofile->AllocateSpatialProfile(0, 1);
		}
		else{
			m_srcprofile->AllocateProfileEconv(false);
		}

		for(int n = 0; n < m_obspoints; n++){
			for(int j = 0; j < 2; j++){
				UV[j] = m_xyobs[j][n]/m_dXYdUV;
			}
			m_ws[1][n] = m_srcprofile->GetFluxAt(UV);
		}
		// m_ws[1][ s0[x0~xn][y0~ym] ]
	}
	else if(m_issurfacepd){
		if(init){
			m_ws[1].resize(m_xyz.size());
			m_wstmp.resize(1);
		}
		for (int n = 0; n < m_xyz.size(); n++){
			m_densfix->SetObserverPositionAngle(m_xyz[n], m_exyz[n]);
			m_densfix->GetDensity(m_xyz[n][0], m_xyz[n][1], &m_wstmp);
			m_ws[1][n] = m_wstmp[0];
		}
	}
	else if(m_isfixpoint || m_isenergy){
		if(init){
			if(m_isenergy){
				m_ws[1].resize(m_ealloc.size()*4);
			}
			else{
				m_ws[1].resize(m_nitems);
			}
		}
		double xy[2];
		for(int j = 0; j < 2; j++){
			xy[j] = m_rectslit || m_circslit ? particle._obs[j] : m_center[j];
		}
		m_densfix->GetDensity(xy[0], xy[1], &m_ws[1]);
		// m_ws[1][ fx[0-m_nfd], fy[0-mnfd], ...]
	}
	else{
		if(init){
			m_ws[1].resize(m_obspoints*m_nitems);
			m_wstmp.resize(m_nitems);
		}
		for(int n = 0; n < m_obspoints; n++){
			m_densfix->GetDensity(m_xyobs[0][n], m_xyobs[1][n], &m_wstmp);
			for(int j = 0; j < m_nitems; j++){
				m_ws[1][j*m_obspoints+n] = m_wstmp[j];
			}
			// m_ws[1][ fx[x0~xn][y0~ym], fy[x0~xn][y0~ym], ...]
		}
	}
}

void MonteCarlo::f_EnergyConvolution()
{
	vector<vector<double>> farr(4);
	EnergySpreadConvolution esampler(this, 4);
	for(int j = 0; j < 4; j++){
		farr[j].resize(m_ealloc.size());
		for(int n = 0; n < m_ealloc.size(); n++){
			farr[j][n] = m_ws[1][j*m_ealloc.size()+n];
		}
	}
	esampler.AllocateInterpolant((int)m_ealloc.size(), &m_ealloc, &farr, false);
	vector<double> fd(4);
	for(int n = 0; n < m_ealloc.size(); n++){
		esampler.RunEnergyConvolution(m_ealloc[n], &fd);
		for(int j = 0; j < 4; j++){
			m_ws[1][j*m_ealloc.size()+n] = fd[j];
		}
	}
}

void MonteCarlo::f_Smoothing()
{
	if(m_smdim == 0){
		return;
	}
	if(m_smfft == nullptr){
		for (int i = 0; i < m_smdim; i++){
			m_smnfft[i] = fft_number(m_mesh[i]*3/2, 1);
			m_smoffset[i] = (m_smnfft[i]-m_mesh[i])/2;
		}
		if(m_isaxis){
			m_smnfft[0] = max(m_smnfft[0], fft_number(m_mesh[1], 1));
			for(int i = 0;  i < 2; i++){
				m_smoffset[i] = (m_smnfft[0]-m_mesh[i])/2;
			}
		}
		if(m_smdim == 1){
			m_smfft = new FastFourierTransform(1, m_smnfft[0]);
			m_smws1d = new double[m_smnfft[0]];
		}
		else{
			m_smfft = new FastFourierTransform(2, m_smnfft[0], m_smnfft[1]);
			m_smws2d = new double*[m_smnfft[0]];
			for(int n = 0; n < m_smnfft[0]; n++){
				m_smws2d[n] = new double[2*m_smnfft[1]];
			}
		}
	}
	for(int nb = 0; nb < m_nbundle; nb++){
		if(m_smdim == 1 && m_isaxis){
			int tmesh = m_mesh[0]+m_mesh[1];
			for(int ia = 0; ia < 2; ia++){
				for (int n = 0; n < m_smnfft[0]; n++){
					int nr = max(0, min(n-m_smoffset[ia], m_mesh[ia]-1));
					m_smws1d[n] = m_ws[1][nb*tmesh+nr+ia*m_mesh[0]];
				}
				m_smfft->DoFFTFilter(m_smws1d, MC_SMOOTH_GAUSS, true);
				for (int n = 0; n < m_mesh[ia]; n++){
					m_ws[1][nb*tmesh+n+ia*m_mesh[0]] = m_smws1d[n+m_smoffset[ia]];
				}
			}
		}
		else if(m_smdim == 1){
			for (int n = 0; n < m_smnfft[0]; n++){
				int nr = max(0, min(n-m_smoffset[0], m_mesh[0]-1));
				m_smws1d[n] = m_ws[1][nb*m_mesh[0]+nr];
			}
			m_smfft->DoFFTFilter(m_smws1d, MC_SMOOTH_GAUSS, true);
			for (int n = 0; n < m_mesh[0]; n++){
				m_ws[1][nb*m_mesh[0]+n] = m_smws1d[n+m_smoffset[0]];
			}
		}
		else{
			for(int m = 0; m < m_smnfft[1]; m++){
				int mr = max(0, min(m-m_smoffset[1], m_mesh[1]-1));
				for (int n = 0; n < m_smnfft[0]; n++){
					int nr = max(0, min(n-m_smoffset[0], m_mesh[0]-1));
					m_smws2d[n][2*m] = m_ws[1][nb*m_mesh[1]*m_mesh[0]+mr*m_mesh[0]+nr];
					m_smws2d[n][2*m+1] = 0.0;
				}
			}
			double cutoff[2] = {MC_SMOOTH_GAUSS, MC_SMOOTH_GAUSS};
			m_smfft->DoFFTFilter2D(m_smws2d, cutoff, true);
			for(int m = 0; m < m_mesh[1]; m++){
				for (int n = 0; n < m_mesh[0]; n++){
					m_ws[1][nb*m_mesh[1]*m_mesh[0]+m*m_mesh[0]+n] 
						= m_smws2d[n+m_smoffset[0]][2*(m+m_smoffset[1])];
				}
			}
		}
	}
}

double MonteCarlo::f_GetMaxWS(int i)
{
	double vmax = 0;
	for(int n = 0; n < m_ws[i].size(); n++){
		vmax = max(vmax, fabs(m_ws[i][n]));
	}
	return vmax;
}

void MonteCarlo::f_DumpCurrent(string debug, Particle *particle)
{
	if(m_rank != 0 || debug.empty()){
		return;
	}
	ofstream debug_out(debug);

	if(particle != nullptr){
		vector<string> comments 
			{"#", "_x=", "_x'=", "_y=", "_y'=", "_t=", "_DE/E="};
		stringstream ss[7];
		for(int j = 0; j < 2; j++){
			ss[2*j+1] << particle->_xy[j]; comments[2*j+1] += ss[2*j+1].str();
			ss[2*j+2] << particle->_qxy[j]; comments[2*j+2] += ss[2*j+2].str();
			ss[5+j] << particle->_tE[j]; comments[5+j] += ss[5+j].str();
		}
		vector<string> comment(1);
		for(int j = 0; j < 7; j++){
			comment[0] += comments[j];
		}
		PrintDebugItems(debug_out, comment);
	}

	vector<vector<double>> tmp;

	if(m_wigctrl != nullptr){
		if(m_isenergy){
			tmp.push_back(m_ws[0]);
			tmp.push_back(m_ws[1]);
			PrintDebugRows(debug_out, m_eparray, tmp, (int)m_eparray.size());
			debug_out.close();
		}
		else{
			int ntot = (int)m_ws[1].size();
			vector<int> mesh, nvar;
			vector<vector<double>> var;
			for(int j = 0; j < 4; j++){
				if(m_xyrp[j].size() > 1){
					mesh.push_back((int)m_xyrp[j].size());
					var.push_back(m_xyrp[j]);
				}
			}
			int ndim = (int)var.size();
			if(ndim == 0){
				for(int n = 0; n < ntot; n++){
					vector<double> values { m_ws[0][n], m_ws[1][n] };
					PrintDebugItems(debug_out, values);
				}
				debug_out.close();
				return;
			}
			nvar.resize(ndim);
			vector<double> items(ndim+1);
			for(int n = 0; n < ntot; n++){
				GetIndicesMDV(n, mesh, nvar, ndim);
				for(int j = 0; j < ndim-1; j++){
					items[j] = var[j+1][nvar[j+1]];
				}
				if(m_ws[0].size() > 0){
					items[ndim-1] = m_ws[0][n];
				}
				else{
					items[ndim-1] = 0;
				}
				items[ndim] = m_ws[1][n];
				PrintDebugItems(debug_out, var[0][nvar[0]], items);
			}
			debug_out.close();
		}
	}
	else if(m_isfixpoint){
		vector<double> items(2);
		for(int n = 0; n < m_nitems; n++){
			for(int j = 0; j < 2; j++){
				items[j] = m_ws[j][n];
			}
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
	else if(m_issurfacepd){
		vector<double> items(5);
		for(int n = 0; n < m_xyz.size(); n++){
			for(int j = 0; j < 3; j++){
				items[j] = m_xyz[n][j];
			}
			items[3] = m_ws[0][n];
			items[4] = m_ws[1][n];
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
	else if(m_isenergy){
		for(int j = 0; j < 2; j++){
			vector<double> fd(m_ealloc.size());
			for (int n = 0; n < m_ealloc.size(); n++){
				fd[n] = m_ws[j][n]+m_ws[j][n+m_ealloc.size()];
			}
			tmp.push_back(fd);
		}
		PrintDebugRows(debug_out, m_ealloc, tmp, (int)m_ealloc.size());
		debug_out.close();
	}
	else{
		tmp.push_back(m_xyobs[1]);
		vector<double> value(m_obspoints);
		for (int j = 0; j < 2; j++){
			for (int n = 0; n < m_obspoints; n++){
				value[n] = m_ws[j][n];
				if (m_nitems == 4){
					value[n] += m_ws[j][m_obspoints+n];
				}
			}
			tmp.push_back(value);
		}
		PrintDebugRows(debug_out, m_xyobs[0], tmp, m_obspoints);
		debug_out.close();
	}
}

