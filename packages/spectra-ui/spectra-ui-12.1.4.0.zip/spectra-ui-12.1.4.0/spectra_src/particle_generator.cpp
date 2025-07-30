#include "particle_generator.h"
#include "trajectory.h"

//----------
Particle::Particle()
{
	Clear();
}

void Particle::Clear()
{
	for(int j = 0; j < 2; j++){
		_xy[j] = _qxy[j] = _tE[j] = _obs[j] = 0;
	}
}

ParticleGenerator::ParticleGenerator(SpectraSolver &spsolver, Trajectory *trajec)
	: SpectraSolver(spsolver)
{
	if(m_isparticle){
		f_LoadData();
		trajec->TransferTwissParamaters(nullptr, nullptr, nullptr, nullptr, m_CS);
	}
	else{
		// get Twiss parameters at the entrance
		double beta0[2], alpha0[2], betaw, espread;
		trajec->TransferTwissParamaters(alpha0, beta0, nullptr);			
		espread = EnergySpreadSigma();
		for (int j = 0; j < 2; j++){
			betaw = beta0[j]/(1.0+alpha0[j]*alpha0[j]);
			m_llxy[j] = betaw*alpha0[j];
			double eta = espread*m_accv[eta_][j];
			double etad = espread*m_accv[etap_][j];
			m_sizew[j] = sqrt(betaw*m_emitt[j]+eta*eta);
			m_divw[j] = sqrt(m_emitt[j]/betaw+etad*etad);
		}
	}
}

void ParticleGenerator::Init()
{
    m_rand.Init(1);
	if(m_isparticle){
		m_curridx = 0;
		for(int n = 0; n < m_nparticle/2; n++){
			int n0 = (int)floor(m_rand.Uniform(0, 1)*m_nparticle);
			int n1 = (int)floor(m_rand.Uniform(0, 1)*m_nparticle);
			swap(m_indices[n0], m_indices[n1]);
		}
	}
}

int ParticleGenerator::Generate(vector<Particle> &particles, int Nmhalf, 
	bool isenergy, bool isobs, bool istime, bool isrand)
{
	if(particles.size() < 2*Nmhalf){
		particles.resize(2*Nmhalf);
	}
	if(m_isparticle){
		for(int n = 0; n < 2*Nmhalf; n++){
			if(m_curridx >= m_nparticle && !isobs){
				return n;
			}
			particles[n] = m_particle[m_curridx];
			double dummy;
			for(int j = 0; j < 2; j++){ // transfer to the entrace (4d, time variable not needed -> tau += tdelay @ Z = 0)
				particles[n]._xy[j] = (dummy=particles[n]._xy[j])*m_CS[j][0]+particles[n]._qxy[j]*m_CS[j][1];
				particles[n]._qxy[j] = dummy*m_CS[j][2]+particles[n]._qxy[j]*m_CS[j][3];
			}
			if(isobs){
				f_AssignObservation(particles[n]);
			}
			m_curridx++;
		}
		return 2*Nmhalf;
	}

	double rex;
    for(int n = 0; n < Nmhalf; n++){
		for(int j = 0; j < 2; j++){
			rex = errfinv(
					isrand ? m_rand.Uniform(-1, 1) : 2.0*m_rand.Hammv(j+1)-1.0
				);
			particles[n]._xy[j] = m_sizew[j]*SQRT2*rex;
			particles[n+Nmhalf]._xy[j] = -particles[n]._xy[j];

			rex = errfinv(
					isrand ? m_rand.Uniform(-1, 1) : 2.0*m_rand.Hammv(j+3)-1.0
				);
			particles[n]._qxy[j] = m_divw[j]*SQRT2*rex;
			particles[n+Nmhalf]._qxy[j] = -particles[n]._qxy[j];
		}
		if(isenergy){
			rex = errfinv(
					isrand ? m_rand.Uniform(-1, 1) : 2.0*m_rand.Hammv(5)-1.0
				);
			particles[n]._tE[1] = EnergySpreadSigma()*SQRT2*rex;
			particles[n+Nmhalf]._tE[1] = -particles[n]._tE[1];
		}
		else{
			particles[n]._tE[1] = 0;
		}
		if(istime){
			rex = errfinv(
					isrand ? m_rand.Uniform(-1, 1) : 2.0*m_rand.Hammv(6)-1.0
				);
			particles[n]._tE[0] = m_acc[bunchlength_]*1e-3/CC*SQRT2*rex;
			particles[n+Nmhalf]._tE[0] = -particles[n]._tE[0];
		}
		else{
			particles[n]._tE[0] = 0;
		}
	}

    for(int n = 0; n < 2*Nmhalf; n++){
		for(int j = 0; j < 2; j++){
			particles[n]._xy[j] -= particles[n]._qxy[j]*m_llxy[j];
		}
		if(isobs){
			f_AssignObservation(particles[n]);
		}
	}
	return 2*Nmhalf;
}

void ParticleGenerator::f_AssignObservation(Particle &particle)
{
	double dran[2];
	for(int j = 0; j < 2; j++){
		dran[j] = m_rand.Hammv(j+7);
		if(m_rectslit){
			particle._obs[j] = m_slitapt[j]*(dran[j]-0.5)+m_center[j];
		}
	}
	if(m_circslit){
		dran[0] = m_slitr[0]+(m_slitr[1]-m_slitr[0])*dran[0];
		dran[1] *= PI2;
		particle._obs[0] = dran[0]*cos(dran[1])+m_center[0];
		particle._obs[1] = dran[0]*sin(dran[1])+m_center[1];
	}
}

void ParticleGenerator::f_LoadData()
{
	m_particle.resize(m_nparticle);
	m_indices.resize(m_nparticle);
	for(int n = 0; n < m_nparticle; n++){
		m_indices[n] = n;
		for(int j = 0; j < 2; j++){
			m_particle[n]._xy[j] = (*m_partbuf[2*j])[n]; // 0: x, 2: y
			m_particle[n]._qxy[j] = (*m_partbuf[2*j+1])[n]; // 1: x', 3: y'
			m_particle[n]._tE[j] = (*m_partbuf[j+4])[n]; // 4: t, 5: E
		}
	}
}
