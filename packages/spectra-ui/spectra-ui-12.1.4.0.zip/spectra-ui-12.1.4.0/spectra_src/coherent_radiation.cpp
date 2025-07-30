#include <algorithm>
#include <iomanip>
#include <time.h>
#include "coherent_radiation.h"
#include "fel_amplifier.h"
#include "particle_generator.h"
#include "trajectory.h"
#include "output_utility.h"
#include "common.h"

// files for debugging
 string CSR_Integ_X;
 string CSR_Integ_Y;
 string CSR_Particles;
 string CSR_Efield_Temporal;
 string CSR_Efield_EtconvTemp;
 string CSR_Efield_Etconv;
 string CSR_Efield_Temporal_Edev;
 string EtBunchFactor;
 string CSR_ZRZ;
 string CSR_Conv_Spec;

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

#define EPS_CSR_SCHEME 0.5

CoherentRadiationBase::CoherentRadiationBase(
	SpectraSolver &spsolver, Trajectory *trajectory, FilterOperation *filter)
	: FluxDensity(spsolver)
{
	m_filter = filter;
	m_trajectory = trajectory;
}

 void CoherentRadiationBase::GetInstPowerDensity(double *xyobs, vector<double> *pd)
 {
	 int tmesh = (int)floor(m_conf[tmesh_]+0.5);
	 if(pd->size() < tmesh){
		 pd->resize(tmesh);
	 }
	 if(m_ws.size() < 2*tmesh){
		 m_ws.resize(2*tmesh);
	 }
	 GetValues(xyobs, &m_ws);
	 for(int n = 0; n < tmesh; n++){
		 (*pd)[n] = hypotsq(m_ws[n], m_ws[n+tmesh]);
	 }
 }

 void CoherentRadiationBase::GetInstEfield(double *xyobs, vector<double> *exy)
 {
	 int tmesh = GetNumberofPoints();
	 if(exy->size() < tmesh){
		 exy->resize(2*tmesh);
	 }
	 GetValues(xyobs, exy);
 }

 void CoherentRadiationBase::GetFluxDensity(double *xyobs, vector<double> *fd)
 {
	 if(m_isenergy){
		 GetValues(xyobs, fd);
		 return;
	 }
	 if(fd->size() < 4){
		 fd->resize(4);
	 }
	 if(m_fws.size() < 4*m_nfdbase){
		 m_fws.resize(4*m_nfdbase);
	 }
	 GetValues(xyobs, &m_fws);
	 if(m_nfdbase < 2){
		 *fd = m_fws;
		 return;
	 }
	 int nefix = max(1, min(m_nfdbase-2, SearchIndex(m_nfdbase, true, m_epbase, m_fixep)));
	 for(int j = 0; j < 4; j++){
		 (*fd)[j] = lagrange(m_fixep, m_epbase[nefix-1], m_epbase[nefix], m_epbase[nefix+1],
			 m_fws[j*m_nfdbase+nefix-1], m_fws[j*m_nfdbase+nefix], m_fws[j*m_nfdbase+nefix+1]);
	 }
 }

 void CoherentRadiationBase::GetPowerDensity(
	double *xyobs, vector<double> *pd, FilterOperation *filter)
 {
 	 int nitems = m_isfilter ? 2 : 1;
	 if(pd->size() < nitems){
		 pd->resize(nitems, 0.0);
	 }
	 GetValues(xyobs, &m_ws);

	 double de = m_epbase[1]-m_epbase[0];
	 (*pd)[0] = simple_integration(m_nfdbase, de, m_ws);
	 if(m_isfilter){
		 (*pd)[1] = m_filter->GetFilteredPower(m_nfdbase, &m_epbase, &m_ws);
	 }
 }

  void CoherentRadiationBase::GetDensity(int csrlayer,
	double *xyobs, vector<double> *density, int rank, int mpiprocesses)
 {
	 m_csrlayer = csrlayer;
	 m_crank = rank;
	 m_cmpiprocesses = mpiprocesses;
	 if(m_istime){
		 if(m_ispower){
			 GetInstPowerDensity(xyobs, density);
		 }
		 else{
			 GetInstEfield(xyobs, density);
		 }
	 }
	 else if(m_ispower){
		 GetPowerDensity(xyobs, density, m_filter);
	 }
	 else{
		 GetFluxDensity(xyobs, density);
	 }
 }

int CoherentRadiationBase::GetNumberofPoints()
{
	int npoints = 1;
	if(m_istime){
		npoints = (int)m_tarray.size();
	}
	else if(m_isenergy){
		npoints = m_nfdbase;
	}
	else{
		npoints = 1;
	}
	return npoints;
}

void CoherentRadiationBase::GetEnergyArray(vector<double> &energy)
{
	energy = m_epbase;
}

//----------
CoherentRadiation::CoherentRadiation(SpectraSolver &spsolver, 
	Trajectory *trajectory, FilterOperation *filter)
	: CoherentRadiationBase(spsolver, trajectory, filter)
{
#ifdef _DEBUG
//CSR_Integ_X  = "..\\debug\\csr_integ_x.dat";
//CSR_Integ_Y  = "..\\debug\\csr_integ_y.dat";
//CSR_Particles  = "..\\debug\\csr_particles.dat";
//CSR_Efield_Temporal  = "..\\debug\\csr_efield_etconv_temp.dat";
//CSR_Efield_Etconv  = "..\\debug\\csr_spec_etconv.dat";
//CSR_Conv_Spec = "..\\debug\\csr_efield_emconv_spec.dat";
//CSR_Efield_EtconvTemp = "..\\debug\\csr_efield_emconv_temp.dat";
//CSR_Efield_Temporal_Edev = "..\\debug\\csr_efield_etconv_temp_edev.dat";
//CSR_ZRZ = "..\\debug\\csr_zrz.dat";
//EtBunchFactor  = "..\\debug\\et_bunch_factor.dat";
#endif

	m_crank = 0;
	m_cmpiprocesses = 1;
	m_particle = new ParticleGenerator(spsolver, trajectory);
	InitFluxDensity(trajectory, filter);
	m_ntaupointsws = 0;
	m_Etws.resize(2);
	m_isflux = !m_istime && !m_ispower;
	m_epbase = m_ep;
	m_nfdbase = m_nfd;
}

CoherentRadiation::~CoherentRadiation()
{
	delete m_particle;
}

void CoherentRadiation::GetValues(double *xyobsin, vector<double> *values)
{
	vector<vector<double>> particles;
	Particle ref;
	vector<double> reftau;
	vector<vector<double>> exy(2);
	vector<int> mpisteps, mpiinistep, mpifinstep;
	double xyobs[2];

	for(int j = 0; j < 2; j++){
		if (xyobsin != nullptr){
			xyobs[j] = xyobsin[j];
		}
		else{
			if(m_confb[fouriep_]){
				xyobs[j] = m_confv[qxyfix_][j]*0.001;
			}
			else{
				xyobs[j] = m_center[j];
			}
		}
	}

	if(m_accb[singlee_]){
		f_SetXYPosition(xyobs);
		f_AllocateElectricField(false, true);
		if(m_istime){
			m_taurange[0] = m_tau[0];
			m_taurange[1] = m_tau[m_ntaupoints-1];
			f_GetEtData(values);
		}
		else{ // complex amplitude
			f_GetFT();
			f_GetFluxItems(values);
		}
		return;
	}

	Particle refpart; // reference particle
	f_GetSingleEField(refpart, xyobs[0], xyobs[1], true, true);
	f_SetRz();
	if(!f_SetupFTConfig()){
		throw runtime_error("Not enough memory available for FFT.");
		return;
	}

	if(m_accb[zeroemitt_]){
		f_GetSingleEField(refpart, xyobs[0], xyobs[1], true, false);
		m_tauws = m_tau;
		for(int j = 0; j < 2; j++){
			m_Etws[j] = m_Et[j];
		}
		m_nNt = 1;
		f_ConvluteEt();
	}
	else{
		f_ComputeMacroParticle(xyobs[0], xyobs[1]);
	}

	if(m_istime){
		f_GetTemporalProfile(values);
		return;
	}
	else{
		m_Fxy = m_Fbuf;
	}

	int nflux = m_isfluxs0?1:4;
	if(values->size() < m_nfd*nflux){
		values->resize(m_nfd*nflux);
	}
	f_GetFluxItems(values);
}

void CoherentRadiation::GetBunchFactorAt(int ne, double ep, double *bdft)
{
	if(m_isEtprof){
		if (ep > m_EtBFspl[ne][0].GetFinXY()){
			bdft[0] = bdft[1] = 0.0;
		}
		else{
			for(int j = 0; j < 2; j++){
				bdft[j] = m_EtBFspl[ne][j].GetValue(ep);
			}
		}
		return;
	}

	if(m_isgaussbeam){
		if(ep < INFINITESIMAL){
			bdft[0] = 1.0;
		}
		else{
			double lfrac = m_acc[bunchlength_]*0.001/wave_length(ep);
			bdft[0] = exp(-PI2*PI*lfrac*lfrac);
		}
        bdft[1] = 0.0;
	}
	else{
		for(int j = 0; j < 2; j++){
			bdft[j] = m_EtBFspl[0][j].GetValue(ep);
		}
	}

	double frac = 1.0;
	double eta = m_eearray[ne];
	if(!m_iszspread){
		double tex = eta/m_acc[espread_];
		tex *= 0.5*tex;
		if(tex > MAXIMUM_EXPONENT){
			frac = 0;
		}
		else{
			frac = exp(-tex)/SQRTPI2/m_acc[espread_];
		}
	}
	for(int j = 0; j < 2; j++){
		bdft[j] *= frac;
	}
}

//private functions
void CoherentRadiation::f_AllocateEtBF()
{
    vector<double> tinv;
	vector<vector<double>> Ift;
    double typblen, de, ehalf, dtmin = 0.0;

	if(m_isgaussbeam || m_iscurrprof){
		if(m_iszspread){
			m_eearray.resize(1, 0.0);
		}
		else{
			int nepoints = (8<<m_accuracy[accineE_])+1;
			ehalf = m_acc[espread_]*m_nlimit[acclimeE_];
			de = 2.0*ehalf/(double)(nepoints-1);
			m_eearray.resize(nepoints);
			for (int ne = 0; ne < nepoints; ne++){
				m_eearray[ne] = -ehalf+(double)ne*de;
			}
		}
		if(m_isgaussbeam){
			return;
		}
		m_EtBFspl.resize(1);
		m_EtBFspl[0].resize(2);
	}
	else if(m_isEtprof){
		m_Etprof.GetVariable(1, &m_eearray);
		m_EtBFspl.resize(m_eearray.size());
		for(int n = 0; n  < m_eearray.size(); n++){
			m_EtBFspl[n].resize(2);
		}
	}

	if(m_erange[1] > INFINITESIMAL){
        dtmin = 0.3*PLANCK/m_erange[1];
    }

	int nend = m_iscurrprof ? 1 : (int)m_eearray.size();

#ifdef _DEBUG
	vector<vector<double>> items;
	vector<vector<double>> sum;
#endif

	for(int ne = 0; ne < nend; ne++){
		if(m_iscurrprof){
			m_currprof.GetFT(0, tinv, Ift, dtmin, &typblen);
		}
		else{
			m_Etprof.GetFT(0, tinv, Ift, dtmin, &typblen, ne);
		}
	    tinv *= PLANCK;
		for(int j = 0; j < 2; j++){
			m_EtBFspl[ne][j].SetSpline((int)tinv.size(), &tinv, &Ift[j]);
#ifdef _DEBUG
			if(!EtBunchFactor.empty()){
				items.push_back(Ift[j]);
				if(ne == 0){
					sum.push_back(Ift[j]);
				}
				else{
					sum[j] += Ift[j];
				}
			}
#endif
		}
	}

#ifdef _DEBUG
	if(!EtBunchFactor.empty()){
		ofstream debug_out(EtBunchFactor);
		vector<string> titles;
		titles.push_back("tinv");
		stringstream ss;
		for(int ne = 0; ne < nend; ne++){
			ss << m_eearray[ne];
			titles.push_back("E"+ss.str()+"re");
			titles.push_back("E"+ss.str()+"im");
			ss.str("");
			ss.clear(stringstream::goodbit);
		}
		string sumt[] = {"Sre", "Sim"};
		for(int j = 0; j < 2 && nend > 1; j++){
			titles.push_back(sumt[j]);
			sum[j] *= m_eearray[1]-m_eearray[0];
			items.push_back(sum[j]);
		}
		PrintDebugItems(debug_out, titles);
		PrintDebugRows(debug_out, tinv, items, (int)tinv.size());
	}
#endif
}

void CoherentRadiation::f_ComputeMacroParticle(double xobs, double yobs)
{
	vector<Particle> particles;
	double eps = m_accuracy_f[accconvMCcoh_];
	vector<int> mpisteps, mpiinistep, mpifinstep;
	vector<double> exydif[4], exyold[4];
	int Nm = PARTICLES_PER_STEP_CSR;
	m_nNt = 0;
	double err = 2.0;
	if(m_isparticle){
		eps *= 0.1;
	}

#ifdef _DEBUG
	vector<double> pardump(6);
	ofstream debug_outp;
	if(!CSR_Particles.empty()){
		debug_outp.open(CSR_Particles);
		vector<string> titles {"No", "x", "y", "x'", "y'", "t", "DE/E"};
		PrintDebugItems(debug_outp, titles);
	}
#endif

	m_calcstatus->SetTargetAccuracy(m_csrlayer, eps);	
	m_calcstatus->SetWPLevel(m_csrlayer, 4);

	for(int j = 0; j < 4; j++){
		exyold[j].resize(m_nfd, 0.0);
	}
	f_SetEt(m_EwBuf);
	m_particle->Init();

	do{
		int Np = m_particle->Generate(particles, Nm/2);
		if(m_accuracy_b[acclimMCpart_]){
			Np = min((int)floor(m_accuracy_f[accMCpart_]-m_nNt+0.5), Np);
		}

		mpi_steps(Np, 1, m_cmpiprocesses, &mpisteps, &mpiinistep, &mpifinstep);

		m_calcstatus->SetSubstepNumber(m_csrlayer, mpisteps[0]);
		m_calcstatus->SetCurrentAccuracy(m_csrlayer, err);

		for(int p = 0; p < Np; p++){
			if(p < mpiinistep[m_crank] || p > mpifinstep[m_crank]){
				continue;
			}
			f_GetSingleEField(particles[p], xobs, yobs, m_is3dsrc||m_isparticle, false);
			f_AllocateComplexField(false, true, true);

			f_SetEt(m_EwBuf, m_EwFFT, true);
#ifdef _DEBUG
			if(!CSR_Particles.empty()){
				for (int j = 0; j < 2; j++){
					pardump[j] = particles[p]._xy[j];
					pardump[j+2] = particles[p]._qxy[j];
					pardump[j+4] = particles[p]._tE[j];
				}
				PrintDebugItems(debug_outp, (double)p, pardump);
			}
#endif
			m_calcstatus->PutSteps(m_csrlayer, p);
		}
		m_calcstatus->SetCurrentOrigin(m_csrlayer);

		if(m_cmpiprocesses > 1){
			for (int j = 0; j < 2; j++){
				if(m_thread != nullptr){
					m_thread->Allreduce(m_EwBuf[j], m_EwFFT[j], 2*m_nfft, MPI_DOUBLE, MPI_SUM, m_crank);
				}
				else{
					MPI_Allreduce(m_EwBuf[j], m_EwFFT[j], 2*m_nfft, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
				}
			}
		}
		else{
			f_SetEt(m_EwFFT, m_EwBuf);
		}
		m_nNt += (double)Np;

		if(m_isparticle){// skip E-t convolution
#ifdef _DEBUG
			if(!CSR_Efield_EtconvTemp.empty() && m_crank == 0){
				int ntau = (int)floor((m_taurange[1]-m_taurange[0])/m_dtau)+1;
				vector<vector<double>> items(2);
				vector<double> tauloc(ntau);
				for(int j = 0; j < 2; j++){
					items[j].resize(ntau);
				}
				for(int n = 0; n < ntau; n++){
					tauloc[n] = m_taurange[0]+m_dtau*n;
					for (int j = 0; j < 2; j++){
						items[j][n] = m_EwFFT[j][2*n]/m_nNt;
					}
				}
				ofstream debug_out(CSR_Efield_EtconvTemp);
				PrintDebugRows(debug_out, tauloc, items, ntau);
				debug_out.close();
			}
#endif
			f_AllocTemporal(true);
			for (int j = 0; j < 2; j++){
				m_EtSpline[j].Initialize(m_ntaupointsws, &m_tauws, &m_Etws[j]);
				m_EtSpline[j].AllocateGderiv();
			}
			f_AllocateComplexField();
			for (int j = 0; j < 4; j++){
				m_Fbuf[j] = m_Fxy[j];
			}
		}
		else{
			f_ConvluteEt();
		}
		for (int j = 0; j < 4; j++){
			m_Fbuf[j] /= m_nNt;
		}

		double fmax = 0;
		for (int n = 0; n < m_nfd; n++){
			fmax = max(fmax, hypotsq(m_Fbuf[0][n], m_Fbuf[1][n])
				+hypotsq(m_Fbuf[2][n], m_Fbuf[3][n]));
		}
		fmax = sqrt(fmax);

#ifdef _DEBUG
		if (!CSR_Efield_Etconv.empty()){
			ofstream debug_out(CSR_Efield_Etconv);
			PrintDebugRows(debug_out, m_ep, m_Fbuf, m_nfd);
			debug_out.close();
		}
#endif
		err = 0.0;
		for(int j = 0; j < 4; j++){
			exydif[j] = m_Fbuf[j];
			exydif[j] -= exyold[j];
			exydif[j] /= fmax;
			err = max(err, fabs(minmax(exydif[j], true)));
			err = max(err, fabs(minmax(exydif[j], false)));
		}

		if(Np != Nm){
			break;
		}
		Nm <<= 1;

		for(int j = 0; j < 4; j++){
			exyold[j] = m_Fbuf[j];
		}
    } while(err > eps);

#ifdef _DEBUG
	if(!CSR_Particles.empty()){
		debug_outp.close();
	}
#endif
}

void CoherentRadiation::f_ConvluteEt()
{
	int ntaupoints;
	if(m_EtBFspl.size() == 0){
		f_AllocateEtBF();
	}
	if(m_accb[zeroemitt_]){
		ntaupoints = m_ntaupoints;
	}
	else{
		f_AllocTemporal(true);
		ntaupoints = m_ntaupointsws;
	}

	double dedev = 1.0;
	if(m_eearray.size() > 1){
		dedev = m_eearray[1]-m_eearray[0];
	}

	for (int j = 0; j < 2; j++){
		fill(m_Fbuf[2*j].begin(), m_Fbuf[2*j].end(), 0.0);
		fill(m_Fbuf[2*j+1].begin(), m_Fbuf[2*j+1].end(), 0.0);
	}

#ifdef _DEBUG
	if(!CSR_Efield_EtconvTemp.empty()){
		ofstream debug_out(CSR_Efield_EtconvTemp);
		vector<vector<double>> Etmp;
		Etmp = m_Etws;
		for(int j = 0; j < 2; j++){
			Etmp[j] /= m_nNt;
		}
		PrintDebugRows(debug_out, m_tauws, Etmp, ntaupoints);
		debug_out.close();
	}
#endif

	double eesq, bdft[2], desq;
	vector<double> tautmp(ntaupoints), rza(ntaupoints);

 	for (int ne = 0; ne < m_eearray.size(); ne++){
		eesq = 1.0+m_eearray[ne];
		eesq *= eesq;
		desq = dedev*eesq*eesq;		
		for (int n = 0; n < ntaupoints; n++){
			tautmp[n]  = f_GetTauEdev(m_tauws[n], m_eearray[ne]);
		}
#ifdef _DEBUG
		if (!CSR_ZRZ.empty()){
			vector<vector<double>> item {tautmp};
			ofstream debug_out(CSR_ZRZ);
			PrintDebugRows(debug_out, m_tauws, item, ntaupoints);
			debug_out.close();
		}
		if(!CSR_Efield_Temporal_Edev.empty()){
			ofstream debug_out(CSR_Efield_Temporal_Edev);
			vector<vector<double>> Etmp;
			Etmp = m_Etws;
			for(int j = 0; j < 2; j++){
				Etmp[j] /= m_nNt;
			}
			PrintDebugRows(debug_out, tautmp, Etmp, ntaupoints);
			debug_out.close();
		}
#endif
		for (int j = 0; j < 2; j++){
			m_EtSpline[j].Initialize(ntaupoints, &tautmp, &m_Etws[j]);
			m_EtSpline[j].AllocateGderiv();
		}

		f_AllocateComplexField(m_accb[zeroemitt_] == false);
		for (int j = 0; j < 2; j++){
			for (int n = 0; n < m_nfd; n++){
				GetBunchFactorAt(ne, m_ep[n], bdft);
				m_Fbuf[2*j][n] += (m_Fxy[2*j][n]*bdft[0]-m_Fxy[2*j+1][n]*bdft[1])*desq;
				m_Fbuf[2*j+1][n] += (m_Fxy[2*j][n]*bdft[1]+m_Fxy[2*j+1][n]*bdft[0])*desq;
			}
		}
	}

#ifdef _DEBUG
	if(!CSR_Conv_Spec.empty()){
		ofstream debug_out(CSR_Conv_Spec);
		vector<string> titles {"Energy", "Ex.re", "Ex.im", "Ey.re", "Ey.im"};
		vector<double> items(5);
		for(int n = 0; n < m_nfd; n++){
			items[0] = m_ep[n];
			for(int j = 0; j < 4; j++){
				items[j+1] = m_Fbuf[j][n]/m_nNt;
			}
			PrintDebugItems(debug_out, items);
		}
		debug_out.close();
	}
#endif
}

void CoherentRadiation::f_AllocTemporal(bool isdirect)
{
	int nrange[2];
	double stau = m_dtau;
	if(isdirect){
		m_ntaupointsws = (int)ceil(m_taurange[2]/stau);
		nrange[0] = 0;
		nrange[1] = m_ntaupointsws-1;
	}
	else{
		if(m_fft_nskip > 1){
			// if > 1, shrink the time interval, because the energy interval 
			// is expanded to compute the temporal profile, 
			stau /= m_fft_nskip;
		}
		nrange[0] = (int)floor(m_taurange[0]/stau);
		nrange[1] = (int)ceil(m_taurange[1]/stau);
		m_ntaupointsws = nrange[1]-nrange[0]+1;
	}
	if(m_tauws.size() < m_ntaupointsws){
		m_tauws.resize(m_ntaupointsws);
		for (int j = 0; j < 2; j++){
			m_Etws[j].resize(m_ntaupointsws);
		}
	}

	int index, nr;
	for(int n = nrange[0]; n <= nrange[1]; n++){
		nr = n-nrange[0];
		if (isdirect){
			m_tauws[nr] = m_taurange[0]+stau*(double)nr;
			index = 2*nr;
		}
		else{
			m_tauws[nr] = stau*(double)n;
			if(n <= -(int)(m_nfft/2) || n > (int)(m_nfft/2)){
				m_Etws[0][nr] = m_Etws[1][nr] = 0;
				continue;
			}
			index = fft_index(n, m_nfft, -1);
		}
		for(int j = 0; j < 2; j++){
			m_Etws[j][nr] = m_EwFFT[j][index];
		}
	}
}

void CoherentRadiation::f_GetTemporalProfile(vector<double> *values)
{
	f_GetTemporal();
	f_AllocTemporal(false);

#ifdef _DEBUG
	ofstream debug_outb;
	if(!CSR_Efield_Temporal.empty()){
		debug_outb.open(CSR_Efield_Temporal);
		vector<vector<double>> Etmp;
		Etmp = m_Etws;
		for(int j = 0; j < 2; j++){
			Etmp[j] /= m_nNt;
		}
		PrintDebugRows(debug_outb, m_tauws, Etmp, m_ntaupointsws);
	}
#endif

	if(values == nullptr){
		return;
	}

	for(int j = 0; j < 2; j++){
		m_EtSpline[j].SetSpline(m_ntaupointsws, &m_tauws, &m_Etws[j]);
	}
	f_GetEtData(values);
}

void CoherentRadiation::f_GetEtData(vector<double> *values)
{
	int tmesh = GetNumberofPoints();
	for(int n = 0; n < tmesh; n++){
		double tau = m_tarray[n]*m_time2tau;
		for(int j = 0; j < 2; j++){
			if(tau < m_taurange[0] || tau > m_taurange[1]){
				(*values)[n+j*tmesh] = 0;
			}
			else{
				(*values)[n+j*tmesh] = m_EtSpline[j].GetValue(tau);
			}
		}
	}
}

void CoherentRadiation::f_GetSingleEField(Particle &particle, 
	double xobs, double yobs, bool recalcorb, bool allocref)
{
	double xy[2];
	OrbitComponents orb, corbit;

	xy[0] = xobs; xy[1] = yobs;
	if(m_confb[fouriep_]){
		f_SetXYAngle(xy);
	}
	else{
		f_SetXYPosition(xy);
	}

	if(recalcorb){
		orb.SetComponents(&particle);
		m_trajectory->AllocateTrajectory(true, false, true, &orb);
		AllocateOrbitComponents();
		if (allocref){
			m_reforb = m_orbit;
			f_AllocateElectricField(false, false, m_confb[fouriep_]);
			return;
		}
	}
	else{
		for(int n = 0; n < m_ntaupoints; n++){
			m_orbit[n]._rz = m_reforb[n]._rz;
			for(int j = 0; j < 2; j++){
				m_orbit[n]._xy[j] = m_reforb[n]._xy[j]+particle._xy[j]
					+(m_zorbit[n]-m_zorbit[0])*particle._qxy[j];
				m_orbit[n]._beta[j] = m_reforb[n]._beta[j]+particle._qxy[j];
				m_orbit[n]._rz +=
					m_zorbit[n]*particle._qxy[j]*particle._qxy[j]
					+2.0*m_reforb[n]._xy[j]*particle._qxy[j];
			}
		}
	}

	if(m_isparticle){
		double tdelay = particle._tE[0];
		f_AllocateElectricField(false, true, m_confb[fouriep_], nullptr, &tdelay);
	}
	else{
		f_AllocateElectricField(false, true, m_confb[fouriep_]);
	}
}

void CoherentRadiation::f_SetEt(double **etfft, double **etbuf, bool isadd)
{
    for(unsigned n = 0; n < m_nfft; n++){
		for(int j = 0; j < 2; j++){
			if(etbuf == nullptr){
				etfft[j][2*n] = etfft[j][2*n+1] = 0.0;
			}
			else if(isadd){
				etfft[j][2*n] += etbuf[j][2*n];
				etfft[j][2*n+1] += etbuf[j][2*n+1];
			}
			else{
				etfft[j][2*n] = etbuf[j][2*n];
				etfft[j][2*n+1] = etbuf[j][2*n+1];
			}
		}
	}
}

void CoherentRadiation::f_SetRz()
{
	vector<double> rz(m_ntaupoints);
	for(int n = 0; n < m_ntaupoints; n++){
		rz[n] = m_zorbit[n]+m_orbit[n]._rz*m_gamma2;
	}
	m_zvsrz.SetSpline(m_ntaupoints, &m_zorbit, &rz);
	m_tauvsz.SetSpline(m_ntaupoints, &m_tau, &m_zorbit);
}

double CoherentRadiation::f_GetTauEdev(double tau, double edev)
{
	double z, rz, esq = 1.0+edev;
	double taulim[2];
	taulim[0] = m_tauvsz.GetIniXY();
	taulim[1] = m_tauvsz.GetFinXY();
	esq *= esq;
	if(tau < taulim[0]){
		rz = m_zvsrz.GetIniXY(false)+tau-taulim[0];
	}
	else if(tau > taulim[1]){
		rz = m_zvsrz.GetFinXY(false)+tau-taulim[1];
	}
	else{
		z = m_tauvsz.GetValue(tau);
		rz = m_zvsrz.GetValue(z);
	}
	tau = tau-rz+rz/esq;
	return tau;
}

//---------------------------------------------------------------------------
CoherentRadiationCtrl::CoherentRadiationCtrl(
	SpectraSolver &spsolver, Trajectory *trajectory, FilterOperation *filter)
	: SpectraSolver(spsolver)
{
	if(m_isfel){
		if(m_isparticle){
			string msg = "\""+CustomParticle+"\" option is not available in FEL-mode calculations.";
			throw runtime_error(msg);
		}
		double goal = 1.0;
		if(contains(m_calctype, menu::spatial) || m_circslit || m_rectslit){
			goal = 0.9;
		}
		m_calcstatus->SetTargetPoint(0, goal);
		m_fel = new FELAmplifier(spsolver, trajectory, filter, 0);
		m_cohbase = m_fel;
		for(int nsec = 0; nsec < m_fel->GetSections() && m_confsel[fel_] != FELReuseLabel; nsec++){
			m_fel->AdvanceSection(nsec);
		}
		m_fel->PrepareFinal();
		m_calcstatus->SetCurrentOrigin(0);
		m_calcstatus->ResetCurrentStep(0);
		m_calcstatus->SetTargetPoint(0, 1.0);
	}
	else{
		m_cohrad = new CoherentRadiation(spsolver, trajectory, filter);
		m_cohbase = m_cohrad;
	}
	m_tol_spint = 0.2/(1.0+m_accuracy[accinobs_]);
	m_jrepmin = 3+m_accuracy[accinobs_];
	m_nitems = GetNumberOfItems();
	m_npoints = m_cohbase->GetNumberofPoints();

	if(m_isfldamp){
		m_coef = GetFldAmpCoef();
	}
	else if(m_istime){
		m_coef = GetTempCoef();
	}
	else{
		m_coef = GetFluxCoef();
		if(m_ispower){
			m_coef *= QE;
		}
	}

	if(m_circslit || m_rectslit){
		for(int j = 0; j < 2; j++){
			m_slitorigin[j] = m_confb[fouriep_] ? m_confv[qslitpos_][j]*0.001 : m_center[j];
		}
		if(m_circslit){
			if(m_confb[fouriep_]){
				m_slitbdini[0] = m_confv[slitq_][0]*0.001;
				m_slitbdfin[0] = m_confv[slitq_][1]*0.001;
			}
			else{
				m_slitbdini[0] = m_slitr[0];
				m_slitbdfin[0] = m_slitr[1];
			}
			m_slitbdini[1] = 0.0;
			m_slitbdfin[1] = PI2;
		}
		else{
			if(m_confb[fouriep_]){
				for(int j = 0; j < 2; j++){
					m_slitbdini[j] = m_slitorigin[j]-0.5*m_confv[qslitapt_][j]*0.001;
					m_slitbdfin[j] = m_slitorigin[j]+0.5*m_confv[qslitapt_][j]*0.001;
				}
			}
			else{
				for(int j = 0; j < 2; j++){
					m_slitbdini[j] = m_slitorigin[j]-0.5*m_slitapt[j];
					m_slitbdfin[j] = m_slitorigin[j]+0.5*m_slitapt[j];
				}
			}
		}
	}

	if(m_calcstatus != nullptr){
		SetCalcStatusPrint(m_calcstatus);
	}
}

CoherentRadiationCtrl::~CoherentRadiationCtrl()
{
	if(m_isfel){
		delete m_fel;
	}
	else{
		delete m_cohrad;
	}
}

void CoherentRadiationCtrl::GetCohSpatialProfile(int layer,
	vector<vector<double>> *xy, vector<vector<double>> *density, 
	int rank, int mpiprocesses)
{
	double xyp[2];
	int npoints = (int)(*xy)[0].size();
	vector<int> mpisteps, mpiinistep, mpifinstep;
	bool issingle = mpiprocesses == 1 || m_isfel;

	density->resize(npoints);
	if(issingle){
		m_calcstatus->SetSubstepNumber(layer, npoints);
	}
	else{
		m_calcstatus->SetSubstepNumber(layer, npoints/mpiprocesses+1);
	}
	for(int n = 0; n < npoints; n++){
		if(!issingle){
			// enable MPI processes and compute in parallel
			mpi_steps(npoints, 1, mpiprocesses, &mpisteps, &mpiinistep, &mpifinstep);
			if(n < mpiinistep[rank] || n > mpifinstep[rank]){
				continue;
			}
		}
		for(int j = 0; j < 2; j++){
			xyp[j] = (*xy)[j][n];
		}
		if(issingle){
			// compute at each observation point with all processes
			m_cohbase->GetDensity(layer+1, xyp, &(*density)[n], rank, mpiprocesses);
		}
		else{
			// compute at each observation point for each process
			m_cohbase->GetDensity(layer+1, xyp, &(*density)[n]);
		}
		(*density)[n] *= m_coef;
		if(rank == 0){
			m_calcstatus->AdvanceStep(layer);
		}
	}

	if(issingle || mpiprocesses == 1){
		return;
	}

	int ndata;
	if(rank == 0){
		ndata = (int)(*density)[0].size();
	}
	if(m_thread != nullptr){
		m_thread->Bcast(&ndata, 1, MPI_INT, 0, rank);
	}
	else{
		MPI_Bcast(&ndata, 1, MPI_INT, 0, MPI_COMM_WORLD);
	}

	int r;
	for(int n = 0; n < npoints; n++){
		for(r = 0; r < mpiprocesses; r++){
			if(n >= mpiinistep[r] && n <= mpifinstep[r]){
				break;
			}
		}
		if(r != rank){
			(*density)[n].resize(ndata);
		}
		if(m_thread != nullptr){
			m_thread->Bcast((*density)[n].data(), ndata, MPI_DOUBLE, r, rank);
		}
		else{
			MPI_Bcast((*density)[n].data(), ndata, MPI_DOUBLE, r, MPI_COMM_WORLD);
		}
	}
}

void CoherentRadiationCtrl::GetValues(int layer,
	vector<vector<double>> *values, int rank, int mpiprocesses)
{
	vector<double> items;

	if(m_circslit || m_rectslit){
		int layers[2] = {0, -1};
		if(m_calcstatus != nullptr){
			layers[1] = layer;
		}
		m_csrlayer = layer+2;
		items.resize(m_nitems*m_npoints);
		if(m_isfel){
			ArrangeMPIConfig(0, 1, 1);
		}
		else{
			ArrangeMPIConfig(rank, mpiprocesses, 1, m_thread);
		}
		int ndata = m_nitems*m_npoints;
		AllocateMemorySimpson(ndata, ndata, 2);
		IntegrateSimpson(layers, m_slitbdini[0], m_slitbdfin[0], 
			m_tol_spint, m_jrepmin, nullptr, &items, CSR_Integ_X);
	}
	else{
		m_cohbase->GetDensity(layer, nullptr, &items, rank, mpiprocesses);
	}
	values->resize(m_nitems);
	if(m_isenergy){
		vector<double> energy, fd;
		m_cohbase->GetEnergyArray(energy);
		fd.resize(m_npoints);
		for(int j = 0; j < 4; j++){
			for(int n = 0; n < m_npoints; n++){
				fd[n] = items[n+j*m_npoints];
			}
			m_fdspl[j].SetSpline(m_npoints, &energy, &fd, false);
			(*values)[j].resize(m_eparray.size());
		}
		for(int n = 0; n < m_eparray.size(); n++){
			for(int j = 0; j < 4; j++){
				(*values)[j][n] = m_coef*m_fdspl[j].GetOptValue(m_eparray[n]);
			}
		}
	}
	else{
		for(int j = 0; j < m_nitems; j++){
			(*values)[j].resize(m_npoints);
			for(int n = 0; n < m_npoints; n++){
				(*values)[j][n] = m_coef*items[n+j*m_npoints];
			}
		}
	}
}

void CoherentRadiationCtrl::QSimpsonIntegrand(int layer, double xyrq, vector<double> *density)
{
	double xy[3];

	m_varint[layer] = xyrq;
	if(layer == 0){
		int layers[2] = {1, -1};
		if(m_calcstatus != nullptr){
			layers[1] = m_csrlayer-1;
		}
		if(m_circslit && fabs(xyrq) < INFINITESIMAL){
			for(int n = 0; n < m_nitems*m_npoints; n++){
				(*density)[n] = 0; // dx dy = rdr dq
			}
			return;
		}
		IntegrateSimpson(layers, m_slitbdini[1], m_slitbdfin[1], 
			m_tol_spint, m_jrepmin, nullptr, density, CSR_Integ_Y);
		if(m_circslit){
			for(int n = 0; n < m_nitems*m_npoints; n++){
				(*density)[n] *= m_varint[0]; // dx dy = rdr dq
			}
		}
	}
	else{
		if(m_circslit){	
			xy[0] = m_varint[0]*cos(m_varint[1])+m_slitorigin[0];
			xy[1] = m_varint[0]*sin(m_varint[1])+m_slitorigin[1];
		}
		else{
			xy[0] = m_varint[0];
			xy[1] = m_varint[1];
		}
		m_cohbase->GetDensity(m_csrlayer, xy, density);
	}
}

void CoherentRadiationCtrl::GetFELData(
	vector<string> &felresults, vector<string> &feltitles)
{
	if(m_isfel == false){
		return;
	}
	if(!m_confb[exportInt_] && !m_confb[R56Bunch_]){
		return;
	}

	vector<string> titles;
	vector<double> energy, currt, tgrid, eta, zstep, zstepI, currIR56, jEtR56;
	vector<vector<vector<double>>> bunchf, eprof;
	vector<vector<double>> currI, spectra, tprof, jEt, pulseE;

	if(m_confsel[fel_] == FELReuseLabel){
		m_fel->GetBunchFactor(energy, zstepI, bunchf);
		titles.push_back(FELBunchFactor);
	}
	else{
		m_fel->GetBunchInf(currt, tgrid, eta, energy, zstepI, zstep,
			currI, jEt, tprof, eprof, bunchf, spectra, pulseE, currIR56, jEtR56);
		if(m_confb[R56Bunch_]){
			titles.push_back(FELCurrProfileR56);
			if(m_confb[exportEt_]){
				titles.push_back(FELEtProfileR56);
			}
		}
		if(m_confb[exportInt_]){
			titles.push_back(FELCurrProfile);
			if(m_confb[exportEt_]){
				titles.push_back(FELEtProfile);
			}
			titles.push_back(FELBunchFactor);
			titles.push_back(FELPulseEnergy);
			titles.push_back(FELEfield);
			titles.push_back(FELInstPower);
			titles.push_back(FELSpectrum);
		}
	}

	int vardim;
	vector<vector<double>> xyvar;
	vector<int> index;
	vector<vector<vector<double>>> data;
	for(int i = 0; i < titles.size(); i++){
		xyvar.clear(); index.clear(); data.clear();
		bool isvarz = titles[i] != FELCurrProfileR56 && titles[i] != FELEtProfileR56;
		bool isvarzI = titles[i] == FELCurrProfile || titles[i] == FELEtProfile || titles[i] == FELBunchFactor;
		if(titles[i] == FELPulseEnergy){
			if(m_accuracy_b[accEcorr_]){
				pulseE.erase(pulseE.begin()+1);
			}
			data.push_back(vector<vector<double>> {pulseE});
		}
		else{
			if(titles[i] == FELBunchFactor || titles[i] == FELSpectrum){
				index.push_back(Energy_);
				xyvar.push_back(energy);
			}
			else if(titles[i] == FELEfield || titles[i] == FELInstPower){
				index.push_back(FELTime_);
				xyvar.push_back(tgrid);
			}
			else{
				index.push_back(FELTime_);
				xyvar.push_back(currt);
				if(titles[i] == FELEtProfile || titles[i] == FELEtProfileR56){
					index.push_back(FELEta_);
					xyvar.push_back(eta);
				}
			}
			int nsections;
			if(!isvarz){
				nsections = 1;
			}
			else if(titles[i] == FELCurrProfile){
				nsections = (int)currI.size();
			}
			else if(titles[i] == FELEtProfile){
				nsections = (int)jEt.size();
			}
			else if(titles[i] == FELBunchFactor){
				nsections = (int)bunchf.size();
			}
			else{
				nsections = (int)eprof.size();
			}
			data.resize(nsections);
			for(int n = 0; n < nsections; n++){
				if(titles[i] == FELCurrProfile){
					data[n].push_back(currI[n]);
				}
				else if(titles[i] == FELCurrProfileR56){
					data[n].push_back(currIR56);
				}
				else if(titles[i] == FELEtProfile){
					data[n].push_back(jEt[n]);
				}
				else if(titles[i] == FELEtProfileR56){
					data[n].push_back(jEtR56);
				}
				else if(titles[i] == FELBunchFactor){
					for(int j = 0; j < 2; j++){
						data[n].push_back(bunchf[n][j]);
					}
				}
				else if(titles[i] == FELEfield){
					for(int j = 0; j < 2; j++){
						data[n].push_back(eprof[n][j]);
					}
				}
				else if(titles[i] == FELInstPower){
					data[n].push_back(tprof[n]);
				}
				else if(titles[i] == FELSpectrum){
					data[n].push_back(spectra[n]);
				}
			}
		}
		if(isvarz || isvarzI){
			index.push_back(FELZStep_);
			if(isvarzI){
				xyvar.push_back(zstepI);
			}
			else{
				xyvar.push_back(zstep);
			}
		}
		vardim = 1;
		if(titles[i] ==  FELCurrProfile || titles[i] ==  FELCurrProfileR56){
			index.push_back(FELCurrent_);
		}
		else if(titles[i] ==  FELEtProfile || titles[i] ==  FELEtProfileR56){
			index.push_back(FELEtProf_);
			vardim = 2;
		}
		else if(titles[i] ==  FELBunchFactor){
			index.push_back(FELBFactorRe_);
			index.push_back(FELBFactorIm_);
		}
		else if(titles[i] ==  FELPulseEnergy){
			index.push_back(FELPulseEnergyRad_);
			if(!m_accuracy_b[accEcorr_]){
				index.push_back(FELPulseEnergyBeam_);
			}
		}
		else if(titles[i] ==  FELEfield){
			index.push_back(FarEfieldx_);
			index.push_back(FarEfieldy_);
		}
		else if(titles[i] ==  FELInstPower){
			index.push_back(Power_);
		}
		else if(titles[i] ==  FELSpectrum){
			index.push_back(Flux_);
		}
		f_WriteFELResult(titles[i], felresults, feltitles, index, vardim, xyvar, data);
	}
}

// private functions
void CoherentRadiationCtrl::f_WriteFELResult(string title,
	vector<string> &felresults, vector<string> &feltitles,
	vector<int> &index, int vardim, vector<vector<double>> &xyvar, vector<vector<vector<double>>> &data)
{
	vector<string> titles, units, details;
	vector<vector<double>> scanvalues;
	vector<vector<vector<double>>> vararrayd;
	vector<vector<vector<vector<double>>>> datad;
	vector<vector<string>> suppletitles;
	vector<vector<double>> suppledata;

	felresults.push_back("");
	feltitles.push_back(title);

	titles.resize(index.size());
	units.resize(index.size());
	for(int j = 0; j < index.size(); j++){
		titles[j] = TitleLablesDetailed[index[j]];
		units[j] = UnitLablesDetailed[index[j]];
	}
	WriteResults(*this, nullptr, (int)data.size(), scanvalues, (int)xyvar.size(), vardim, titles, units,
		details, xyvar, data, vararrayd, datad, suppletitles, suppledata, felresults.back());
}
