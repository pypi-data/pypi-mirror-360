#ifndef particle_generator_h
#define particle_generator_h

#include "spectra_solver.h"
#include "randomutil.h"

#define PARTICLES_PER_STEP 1000
#define PARTICLES_PER_STEP_CSR 200

class Particle
{
public:
	Particle();
	void Clear();
	double _xy[2];
	double _qxy[2];
	double _tE[2];
	double _obs[2];
};

class Trajectory;

class ParticleGenerator
	: public SpectraSolver
{
public:
	ParticleGenerator(SpectraSolver &spsolver, Trajectory *trajec);
	virtual ~ParticleGenerator(){}
	void Init();
	int Generate(vector<Particle> &particles, int Nmquat, 
		bool isenergy = false, bool isobs = false, bool istime = false, bool isrand = false);
	double GetBunchLength(){return m_tEspr[0];}

private:
	void f_LoadData();
	void f_AssignObservation(Particle &particle);
	RandomUtility m_rand;
	vector<Particle> m_particle;
	vector<int> m_indices;
	vector<double> m_CS[2];
	int m_curridx;
	double m_llxy[2];
	double m_sizew[2];
	double m_divw[2];
	double m_tEspr[2];
};


#endif
