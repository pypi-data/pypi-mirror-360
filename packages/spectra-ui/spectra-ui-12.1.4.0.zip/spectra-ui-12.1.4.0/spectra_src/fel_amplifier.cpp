#include <boost/math/special_functions/bessel.hpp>
#include "fel_amplifier.h"
#include "trajectory.h"
#include "flux_density.h"
#include "common.h"
#include "particle_generator.h"
#include "output_utility.h"
#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

using namespace boost::math;

// files for debugging
string FELTempProfile;
string FELTempProfileFar;
string FELSprofileFar;
string FELTempWhole;
string FELSpecSingle;
string FELSpecProfile;
string FELSpecProfileFar;
string FELCurrProfileDebug;
string FELBunchFactorDebug;
string FELEtProfileDebug;
string FELStepTdelay;
string FELStepIndex;
string ParticleDist6D;
string InputCSRTrack;
string FELTrajectory;
string FELAdvSprofBef;
string FELAdvSprofAft;
string FELSprofGrid;
string SeedCustomIntSpec;

int TargetParticle = 0;
int TargetRank = 0;

//#define _DEBUG
//#define _ONLYAXIS

#undef PART_RANDOM

FELAmplifier::FELAmplifier(
    SpectraSolver& spsolver, Trajectory *trajectory, FilterOperation *filter, int fellayer)
    : CoherentRadiationBase(spsolver, trajectory, filter)
{

#ifdef _DEBUG
//    FELTempProfile = "..\\debug\\fel_temporal.dat";
//    FELTempProfileFar = "..\\debug\\fel_temporal_far.dat";
//    FELSprofileFar = "..\\debug\\fel_spatial_far.dat";
//    FELTempWhole = "..\\debug\\fel_temporal_whole.dat";
//    FELSpecProfile = "..\\debug\\fel_spectrum.dat";
//    FELSpecProfileFar = "..\\debug\\fel_spectrum_far.dat";
//    FELSpecSingle = "..\\debug\\fel_spectrum_single.dat";
//    FELCurrProfileDebug = "..\\debug\\fel_current.dat";
//    FELEtProfileDebug = "..\\debug\\fel_Et.dat";
//    FELStepTdelay = "..\\debug\\fel_step_tdelay.dat";
//    FELStepIndex = "..\\debug\\fel_step_index.dat";
//    FELBunchFactorDebug = "..\\debug\\fel_bfactor.dat";
//    ParticleDist6D = "..\\debug\\particles6d-";
//    ParticleDist6D = "..\\debug\\particles6d.dat";
//    InputCSRTrack = "..\\debug\\in_particles_csr.fmt1";
//    FELTrajectory = "..\\debug\\fel_trajectory_append.dat";
//    FELTrajectory = "..\\debug\\fel_trajectory.dat";
//    FELAdvSprofBef = "..\\debug\\fel_efield_adv_bef.dat";
//    FELAdvSprofAft = "..\\debug\\fel_efield_adv_aft.dat";
//    FELSprofGrid = "..\\debug\\fel_efield_grid.dat";
//    SeedCustomIntSpec = "..\\debug\\seed_integ.dat";
#endif

    m_fellayer = fellayer;
    m_epmax_fel = max(m_confv[eproi_][0], m_confv[eproi_][1]);
    m_epmin_fel = min(m_confv[eproi_][0], m_confv[eproi_][1]);
    m_grank = m_rank;
    m_dim = 3;
    m_gprocesses = m_mpiprocesses;
    m_isrealft = true;
    m_bunchE = m_bunchelectrons*QE*m_acc[eGeV_]*1e9;
    m_advsteps = (int)floor(m_conf[radstep_]+0.5);
    m_bfreuse = m_confsel[fel_] == FELReuseLabel;

    vector<vector<double>> betaarr(2);
    vector<double> rz;
    m_trajectory->GetTrajectory(m_zorbit, nullptr, &m_qxyref, &m_xyref, &rz);
    m_trajectory->TransferTwissParamaters(nullptr, nullptr, &betaarr);
    m_trajectory->GetZsection(m_secidx);
    m_nsections = (int)m_secidx[1].size();

    m_xyfar[0] = m_xyfar[1] = 0;
    InitFluxDensity(m_trajectory, filter);

    // save the parameters to compute coherent radiation by microbunch
    m_epbf = m_ep;
    m_deFTbf = m_deFT;
    m_nfftbf = m_nfftbase;
    m_dtaubf = m_dtau;
    m_nfdbase = m_nfdbf = m_nfd;
    m_epbase = m_ep;

    f_SetTauRange();
    if(!f_SetupFTBase(true)){
        throw runtime_error("Not enough memory available for FFT.");
        return;
    }

    if(m_nfftbf < (int)m_nfftbase){
        // redefine the the parameters for radiation by microbunch
        m_epbf = m_ep;
        m_deFTbf = m_deFT;
        m_nfftbf = m_nfftbase;
        m_dtaubf = m_dtau;
        m_nfdbase = m_nfdbf = m_nfd;
        m_epbase = m_ep;
    }
    for(int j = 0; j < 3; j++){
        m_EwFFTbf[j] = new double[m_nfftbf];
    }
    m_fftbf = new FastFourierTransform(1, m_nfftbf);

    for(int nsec = 0; nsec < m_nsections; nsec++){
        m_Zmid.push_back((m_zorbit[m_secidx[0][nsec]]+m_zorbit[m_secidx[1][nsec]])*0.5);
        m_Zex.push_back(m_zorbit[m_secidx[1][nsec]]);
    }

#ifdef _DEBUG
    if(!FELStepIndex.empty() && m_grank == 0){
        ofstream debug_out(FELStepIndex);
        vector<string> titles {"Section", "Zindex", "Zpos"};
        vector<double> items(3);
        PrintDebugItems(debug_out, titles);
        for(int nsec = 0; nsec < m_nsections; nsec++){
            items[0] = nsec;
            items[1] = m_secidx[1][nsec];
            items[2] = m_Zex[nsec];
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif

    Spline betaspl[2], xyspl[2], rzspl;
    m_tstep.resize(m_nsections+1);
    m_tmid.resize(m_nsections);
    m_bmsize.resize(2);
    for(int j = 0; j < 2; j++){
        m_bmsize[j].resize(m_nsections);
        betaspl[j].SetSpline((int)m_zorbit.size(), &m_zorbit, &betaarr[j]);
        xyspl[j].SetSpline((int)m_zorbit.size(), &m_zorbit, &m_xyref[j]);
    }
    rzspl.SetSpline((int)m_zorbit.size(), &m_zorbit, &rz);
    m_t0 = -(m_zorbit[0]+m_gamma2*rz[0])/m_time2tau; // time delay at the entrance
    
    m_bmavg[0] = m_bmavg[1] = 0;
    for(int nsec = 0; nsec < m_nsections; nsec++){
        m_tstep[nsec] = -(m_Zex[nsec]+m_gamma2*rz[m_secidx[1][nsec]])/m_time2tau;
        m_tmid[nsec] = -(m_Zmid[nsec]+m_gamma2*rzspl.GetValue(m_Zmid[nsec]))/m_time2tau;
        // time delay at the end of each section
        for(int j = 0; j < 2; j++){
            m_bmsize[j][nsec] = sqrt(betaspl[j].GetValue(m_Zmid[nsec])*m_emitt[j]);
            // beam size at the middle of each section
            if(nsec == 0){
                m_bmmax[j] = m_bmmin[j] = m_bmsize[j][nsec];
            }
            else{
                m_bmmax[j] = min(m_bmmax[j], m_bmsize[j][nsec]);
                m_bmmin[j] = min(m_bmmin[j], m_bmsize[j][nsec]);
            }
            m_bmavg[j] += m_bmsize[j][nsec]/m_nsections;
        }
    }
    m_tstep[m_nsections] = 0;

    m_tzorb.resize((int)m_zorbit.size());
    for(int n = 0; n < (int)m_zorbit.size(); n++){
        m_tzorb[n] = -(m_zorbit[n]+m_gamma2*rz[n])/m_time2tau;
    }

#ifdef _DEBUG
    if(!FELStepTdelay.empty() && m_grank == 0){
        vector<string> titles {"Section", "Delay(fs)"};
        vector<double> items(2);
        ofstream debug_out(FELStepTdelay);
        for(int n = 0; n < m_nsections; n++){
            items[0] = n;
            items[1] = m_tstep[n]*1e15;
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif

    if(m_confsel[fel_] == FELPrebunchedLabel || m_bfreuse){
        m_seed.clear(); // no seeding
    }
    else if(m_confsel[fel_] == FELDblSeedLabel){
        m_seed.resize(2);
        for(int j = 0; j < 2; j++){
            double pulseE = m_confv[pulseE_d_][j]*1e-3;
            double plen = m_confv[tlpulselen_d_][j]*1e-15;
            double epcenter = photon_energy(m_confv[wavelen_d_][j]*1e-9);
            double srcsize = m_confv[srcsize_d_][j]*1e-3;
            double zwaist = m_confv[waistpos_d_][j];
            double torg = m_confv[timing_d_][j]*1e-15;
            m_seed[j] = new SeedLight(pulseE, epcenter, plen, 
                srcsize, zwaist, torg, m_confv[gdd_d_][j], m_confv[tod_d_][j]);
        }
    }
    else{
        m_seed.resize(1);
        double pulseE = m_conf[pulseE_]*1e-3;
        double plen = (m_confsel[fel_] == FELSeedLabel
            ? m_conf[pulselen_] : m_conf[tlpulselen_])*1e-15;
        double epcenter = photon_energy(m_conf[wavelen_]*1e-9);
        double srcsize = m_conf[srcsize_]*1e-3;
        double zwaist = m_conf[waistpos_];
        double torg = m_conf[timing_]*1e-15;
        if(m_confsel[fel_] == FELSeedCustomLabel){
            m_seed[0] = new SeedLight(m_seedspec, pulseE, srcsize, zwaist, torg);
        }
        else{
            m_seed[0] = new SeedLight(pulseE, epcenter, plen,
                srcsize, zwaist, torg, m_conf[gdd_], m_conf[tod_]);
        }

    }

    f_SetAngularGrid(m_bmavg);

    m_bunchf.resize(m_nsections+1);
    m_spectra.resize(m_nsections);
    for(int nsec = 0; nsec <= m_nsections; nsec++){
        m_bunchf[nsec].resize(2);
        for(int j = 0; j < 2; j++){
            m_bunchf[nsec][j].resize(m_nfdbf, 0);
        }
        if(nsec < m_nsections){
            m_spectra[nsec].resize(m_nfdbf, 0);
        }
    }

    // define the FFT-related parameters
    f_SetupFTConfig();
    m_dt = m_dtaubf/m_time2tau;

    if(!f_SetParticles((int)m_conf[particles_])){
        throw runtime_error("Too few macroparticles.");
    }
    if(!m_bfreuse){
        // arrange particles
        m_reference.Clear();

        // setup grid points
        double Dxy[2];
        m_xygrid.resize(2);
        for(int j = 0; j < 2; j++){
            m_dxy[j] = m_bmavg[j]/m_accuracy[accinobs_]; // step: sigma for default
            Dxy[j] = 2*(m_accuracy[acclimobs_]+2.5)*m_bmavg[j]; // xyrange: -3.5sigma~3.5sigma for default
        }
        f_SetGridPoints(true, m_accuracy[accinobs_], Dxy);
    }

#ifdef _DEBUG
    vector<double> eptgt{0.001, 0.002, 0.003, 0.004};
    for(int ne = 0; ne < eptgt.size(); ne++){
        int idx = (int)floor(0.5+(eptgt[ne]-m_ep[0])/(m_ep[1]-m_ep[0]));
        if(idx > m_ep.size()){
            continue;
        }
        if(m_ep[idx] > 0){
            if(m_netgt.size() == 0 || idx > m_netgt.back()){
                m_netgt.push_back(idx);
            }
        }

        idx = (int)floor(0.5+(eptgt[ne]-m_epbf[0])/(m_epbf[1]-m_epbf[0]));
        if(idx > m_epbf.size()){
            continue;
        }
        if(m_epbf[idx] > 0){
            if(m_netgtbf.size() == 0 || idx > m_netgtbf.back()){
                m_netgtbf.push_back(idx);
            }
        }
    }
#endif

    if(m_bfreuse){
        picojson::array dataarr = m_felbfactor[DataLabel].get<picojson::array>();
        if(dataarr.size() != 4){
            throw runtime_error("Bunch-facotor format is invalid.");
        }
        if(dataarr[1].get<picojson::array>().size() != m_nsections+1){
            throw runtime_error("Bunch-facotor format is invalid.");
        }
        int nfdbf = (int)dataarr[0].get<picojson::array>().size();
        vector<double> epbf(nfdbf), bfws(nfdbf);
        picojson::array data = dataarr[0].get<picojson::array>();
        for(int ne = 0; ne < nfdbf; ne++){
            epbf[ne] = data[ne].get<double>();
        }
        Spline bfspl;
        for(int j = 0; j < 2; j++){
            picojson::array data = dataarr[j+2].get<picojson::array>();
            for(int n = 0; n <= m_nsections; n++){
                for(int ne = 0; ne < nfdbf; ne++){
                    bfws[ne] = data[n*nfdbf+ne].get<double>();
                }
                bfspl.SetSpline(nfdbf, &epbf, &bfws);
                for(int ne = 0; ne < m_nfdbf; ne++){
                    m_bunchf[n][j][ne] = bfspl.GetValue(m_epbf[ne]);
                }
            }
        }
        return;
    }

    int steps = f_GetTotalSteps();
    m_calcstatus->SetSubstepNumber(m_fellayer, steps);

    // compute the bunch factor at the entrance
    f_GetBunchFactor(0);
}

FELAmplifier::~FELAmplifier()
{
    for(int j = 0; j < 3; j++){
        delete[] m_EwFFTbf[j];
    }
    for(int i = 0; i < m_seed.size(); i++){
        delete m_seed[i];
    }
    delete m_fftbf;

    if(!m_bfreuse){
        delete m_fftsp;
        for(int n = 0; n < m_nfftsp[0]; n++){
            delete[] m_fftspws[n];
        }
        delete[] m_fftspws;
        delete[] m_wssp;
    }
}


string FELAmplifier::f_GetParticleDataName(int tgtsec)
{
    if(ParticleDist6D.find("-") != string::npos){
        return ParticleDist6D+(tgtsec < 0 ? "init" : to_string(tgtsec))+".dat";
    }
    return ParticleDist6D;
}

void FELAmplifier::AdvanceSection(int tgtsec)
{
    // advance particles, updating the radiation waveform
    f_AdvanceParticlesSection(tgtsec);

    // evaluate the pulse energy
    f_GetPulseEnergy(tgtsec);

    // adjust the e- energy to be consistent with radiation
    double deta = 0;
    if(m_seed.size() == 0){
        deta = (m_pulseE[0][tgtsec]-m_pulseE[1][tgtsec])*0.001/m_bunchE;
    }

    for(int m = 0; m < m_Nparticles && m_accuracy_b[accEcorr_]; m++){
        // adjust energy change to be self-consistent
        m_particles[m]._tE[1] -= deta;
    }

    // compute the bunch profile & factor at the exit for the next step
    f_GetBunchFactor(tgtsec+1);

    if(tgtsec == m_nsections-1 && m_confb[R56Bunch_]){
        // comupte the bunch profile with R56
        f_GetBunchFactor(m_nsections+1);
    }

#ifdef _DEBUG
    vector<int> steps, inistep, finstep;
    vector<int> ranks(m_Nparticles);
    mpi_steps(1, m_Nparticles, m_gprocesses, &steps, &inistep, &finstep);

    string dataname = f_GetParticleDataName(tgtsec);
    if(!dataname.empty()){
        MPI_Barrier(MPI_COMM_WORLD);
        string filename;

        ofstream debug_out;
        vector<double> items(9);
        if(m_grank == 0){
            debug_out.open(dataname);
            vector<string> titles{"t(fs)", "DE/E", "No.", "x(m)", "y(m)", "x'(rad)", "y'(rad)", "Weight", "DEW"};
            PrintDebugItems(debug_out, titles);
        }

        for(int rank = 0; rank < m_gprocesses; rank++){
            for(int m = inistep[rank]; m <= finstep[rank]; m++){
                ranks[m] = rank;
            }
        }

        for(int m = 0; m < m_Nparticles; m++){
            if(m_charge[m] < 0.01){
                continue;
            }
            if(m_grank == ranks[m]){
                items[2] = m;
                for(int j = 0; j < 2; j++){
                    items[j+3] = m_particles[m]._xy[j];
                    items[j+5] = m_particles[m]._qxy[j];
                    items[j] = m_particles[m]._tE[j];
                }
                items[0] *= 1e15;
                items[7] = m_charge[m];
                items[8] = items[1]*items[7];
            }
            for(int j = 0; j < 9; j++){
                if(m_thread != nullptr){
                    m_thread->Bcast(&items[j], 1, MPI_DOUBLE, ranks[m], m_grank);
                }
                else{
                    MPI_Bcast(&items[j], 1, MPI_DOUBLE, ranks[m], MPI_COMM_WORLD);
                }
            }
            if(m_grank == 0){
                PrintDebugItems(debug_out, items);
            }
            MPI_Barrier(MPI_COMM_WORLD);
        }
        if(m_grank == 0){
            debug_out.close();
        }
    }
#endif
}

void FELAmplifier::GetValues(double *xyobsin, vector<double> *values)
{
    double xyobs[2], Zpos;
    for(int j = 0; j < 2; j++){
        if(xyobsin != nullptr){
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
    Zpos = m_confb[fouriep_] ? 0 : m_conf[slit_dist_];

    int mesh = m_istime ? (int)m_tarray.size() : m_nfdbf;

    f_GetRadWaveformPoint(Zpos, xyobs, 0);

    if(m_istime){
        double coef = GetTempCoef(true);
        for(int j = 0; j < 2; j++){
            m_EtSpline[j].SetSpline(2*m_hntgrid+1, &m_tgrid, &m_EtGrid[0][0][j]);
            for(int n = 0; n < mesh; n++){
                (*values)[n+j*mesh] = m_EtSpline[j].GetValue(m_tarray[n], true)/coef;
            }
        }
        return;
    }

    int nflux = m_isfluxs0?1:4;
    if(values->size() < m_nfdbf*nflux){
        values->resize(m_nfdbf*nflux);
    }

    double fx[2], fy[2];
    vector<double> fxy(4);
    for(int n = 0; n < mesh; n++){
        if(m_isfluxamp){
            for(int j = 0; j < 2; j++){
                (*values)[n+j*m_nfdbf] = m_EwFFTbf[0][2*n+j];
                (*values)[n+(2+j)*m_nfdbf] = m_EwFFTbf[1][2*n+j];
            }
        }
        else if(m_isfluxs0){
            (*values)[n] =
                hypotsq(m_EwFFTbf[0][2*n], m_EwFFTbf[0][2*n+1])
                +hypotsq(m_EwFFTbf[1][2*n], m_EwFFTbf[1][2*n+1]);
        }
        else{
            for(int j = 0; j < 2; j++){
                fx[j] = m_EwFFTbf[0][2*n+j];
                fy[j] = m_EwFFTbf[1][2*n+j];
            }
            stokes(fx, fy, &fxy);
            for(int j = 0; j < 4; j++){
                (*values)[n+j*m_nfdbf] = fxy[j];
            }
        }
    }
}

void FELAmplifier::PrepareFinal()
{
    double Dxy[2];
    for(int j = 0; j < 2; j++){
        Dxy[j] = 2*(m_accuracy[acclimobs_]+1.5)*m_bmavg[j]; // xyrange: -2.5sigma~2.5sigma for default
    }
    m_dim = 2;
    f_SetGridPoints(true, 0, Dxy);
}

void FELAmplifier::GetBunchFactor(vector<double> &energy, 
    vector<double> &zstepI, vector<vector<vector<double>>> &bunchf)
{
    zstepI = m_Zex; zstepI.insert(zstepI.begin(), m_zorbit[0]);
    bunchf = m_bunchf;
    energy = m_epbf;
}

void FELAmplifier::GetBunchInf(
    vector<double> &currt,
    vector<double> &tgrid,
    vector<double> &eta,
    vector<double> &energy,
    vector<double> &zstepI,
    vector<double> &zstep,
    vector<vector<double>> &currI,
    vector<vector<double>> &jEt,
    vector<vector<double>> &tprof,
    vector<vector<vector<double>>> &eprof,
    vector<vector<vector<double>>> &bunchf,
    vector<vector<double>> &spectra,
    vector<vector<double>> &pulseE,
    vector<double> &currIR56,
    vector<double> &jEtR56
    )
{
    currt = m_currt;
    currt *= 1e15; // s -> fs

    tgrid = m_tgrid;
    tgrid *= 1e15; // s -> fs

    zstep = m_Zex;
    GetBunchFactor(energy, zstepI, bunchf);
    currI = m_currI; currI.erase(currI.end()-1);
    spectra = m_spectra;
    eprof = m_eprof;
    tprof = m_tprof;
    pulseE = m_pulseE;

    int tmesh = (int)m_currt.size();
    if(m_confb[exportEt_] && 
            (m_confb[exportInt_] || m_confb[R56Bunch_])){
        int neta = (int)m_curr_j[m_nsections][0].size();
        eta.resize(neta);
        int heta = (neta-1)/2;
        for(int i = -heta; i <= heta; i++){
            eta[i+heta] = i*m_d_eta;
        }
        if(m_confb[exportInt_]){
            jEt.resize(m_nsections+1);
        }
        int nini = m_confb[exportInt_] ? 0 : m_nsections+1;
        int nfin = m_confb[R56Bunch_] ? m_nsections+1 : m_nsections;

        for(int n = nini; n <= nfin; n++){
            vector<double> &jetr = n == m_nsections+1 ? jEtR56 : jEt[n];
            jetr.resize(tmesh*neta);
            int netan = (int)m_curr_j[n][0].size();
            int hetan = (netan-1)/2;
            for(int t = 0; t < tmesh; t++){
                for(int ne = -heta; ne <= heta; ne++){
                    int idx = t+(ne+heta)*tmesh;
                    if(abs(ne) <= hetan){
                        jetr[idx] = m_curr_j[n][t][ne+hetan];
                    }
                    else{
                        jetr[idx] = 0;
                    }
                }
            }
        }
    }

    if(m_confb[R56Bunch_]){
        currIR56 = m_currI.back();
    }
}

// private functions
int FELAmplifier::f_GetTotalSteps()
{
    int steps = m_advsteps*(
            m_nsections*(m_nsections+1) // f_GetComplexAmpGrid, f_GetComplexAmpAdv, f_ConvoluteEbeamSize
            +m_nsections // f_GetTemporalBF
        );

    // f_GetPulseEnergy
    steps += m_nsections*m_nsq[0]*2;

    //  AdvancePhaseSpace
    steps += (int)m_zorbit.size();

    return steps;
}

void FELAmplifier::f_SetTauRange()
{
    double etmax = 0, etmaxr, eps = 0.01/(1<<(m_accuracy[acclimobs_]-1));
    double theta[2];
    for(int j = 0; j < 2; j++){
        theta[j] = 0;
        do{
            theta[j] += 0.5/m_gamma;
            m_qxqy[j] = theta[j];
            m_qxqy[1-j] = 0;
            f_AllocateElectricField(true, true, true);
            etmaxr = theta[j]*max(
                max(fabs(minmax(m_Et[0], true)), fabs(minmax(m_Et[0], false))),
                max(fabs(minmax(m_Et[1], true)), fabs(minmax(m_Et[1], false)))
            );
            etmax = max(etmax, etmaxr);
        } while(etmaxr > etmax*eps);
    }
    for(int j = 0; j < 2; j++){
        m_qxqy[j] = theta[j];
    }
    f_AllocateElectricField(true, true, true);

    double dtaumax = 0;
    for(int nsec = 0; nsec < m_nsections; nsec++){
        dtaumax = max(dtaumax, m_tau[m_secidx[1][nsec]]-m_tau[m_secidx[0][nsec]]);
    }
    m_taurange[0] = 0;
    m_taurange[1] = m_taurange[2] = dtaumax;
}

bool FELAmplifier::f_SetParticles(int Nmax)
{
    double glime = 3, threshold = 0.01;
    double sigtE[2], dtE[2];
    int ntE[2], htE[2], m[2];

    dtE[0] = m_dt;

    vector<double> tvar, evar;
    if(m_iscurrprof || m_isEtprof){
        if(m_iscurrprof){
            m_currprof.GetVariable(0, &tvar);
        }
        else if(m_isEtprof){
            m_Etprof.GetVariable(0, &tvar);
            m_Etprof.GetVariable(1, &evar);
        }
        double tmax = max(fabs(tvar.front()), fabs(tvar.back()));
        htE[0] = (int)floor(tmax/dtE[0]);
    }
    else{
        double glimt = m_nlimit[acclimeE_]-1; // +- 3 sigma for default
        sigtE[0] = m_acc[bunchlength_]*0.001/CC;
        htE[0] = max(25, (int)floor((glimt*sigtE[0])/dtE[0]));
    }
    ntE[0] = 2*htE[0]+1;
    m_hncurrt = htE[0];
    m_currt.resize(ntE[0]);
    for(m[0] = -htE[0]; m[0] <= htE[0]; m[0]++){
        m_currt[m[0]+htE[0]] = m_dt*m[0];
    }

    double tslip = m_t0-m_tstep[m_nsections-1];
    m_hntgrid = (int)ceil((m_currt.back()+tslip)/m_dt);

    int ntrad = 2*m_hntgrid+1;
    m_tgrid.resize(ntrad);
    for(int n = -m_hntgrid; n <= m_hntgrid; n++){
        m_tgrid[n+m_hntgrid] = m_dt*n;
    }
    if(m_bfreuse){
        return true;
    }

    m_currI.resize(m_nsections+2);
    m_curr_j.resize(m_nsections+2);
    m_eprof.resize(m_nsections);
    m_tprof.resize(m_nsections);
    m_pulseE.resize(2);
    for(int j = 0; j < 2; j++){
        m_pulseE[j].resize(m_nsections);
    }
    for(int nsec = 0; nsec <= m_nsections+1; nsec++){
        m_currI[nsec].resize(ntE[0]);
        m_curr_j[nsec].resize(ntE[0]);
        if(nsec >= m_nsections){
            continue;
        }
        m_tprof[nsec].resize(ntrad);
        m_eprof[nsec].resize(2);
        for(int j = 0; j < 2; j++){
            m_eprof[nsec][j].resize(ntrad);
        }
    }

    htE[1] = Nmax/(htE[0]*2)/2;
    if(m_isEtprof){
        if(htE[1] < evar.size()/4){
            return false;
        }
        double emax = max(fabs(evar.front()), fabs(evar.back()));
        dtE[1] = emax/htE[1];
    }
    else{
        sigtE[1] = EnergySpreadSigma();
        if(sigtE[1] > 0){ // finite energy spread
            if(htE[1] < 5){
                return false;
            }
            dtE[1] = glime*sigtE[1]/htE[1];
        }
        else{
            dtE[1] = 0;
        }
    }
    ntE[1] = 2*htE[1]+1;

    m_Nparticles = ntE[0]*ntE[1]-1;
    if(TargetParticle >= m_Nparticles){
        TargetParticle = m_Nparticles/2;
    }

    ParticleGenerator partgen(*this, m_trajectory);
    partgen.Init();
#ifdef PART_RANDOM
    partgen.Generate(m_particles, m_Nparticles/2, false, false, true, true);
#else
    partgen.Generate(m_particles, m_Nparticles/2, false, false, false, true);
#endif
    m_charge.resize(m_Nparticles);

    RandomUtility rand;
    rand.Init(1);

    double shotnoize;
    int np = 0;
    bool isnew;

    for(m[0] = -htE[0]; m[0] <= htE[0]; m[0]++){
        for(m[1] = -htE[1]; m[1] <= htE[1]; m[1]++){
            for(int j = 0; j < 2; j++){
#ifndef PART_RANDOM
                m_particles[np]._tE[j] = m[j]*dtE[j];
#endif
                m_particles[np]._xy[j] += m_xyref[j][0];
                m_particles[np]._qxy[j] += m_qxyref[j][0];
            }
            isnew = m[1] == -htE[1];
            if(isnew){
                double electrons = f_ElectronNumber(m_particles[np]._tE[0]);
                if(electrons > 0){
                    shotnoize = rand.Gauss(true)/sqrt(electrons);
                }
                // kill shot noise: 2021/06/30
                shotnoize = 0;
            }
            m_charge[np] = f_GetCharge(m_particles[np], dtE, isnew);
            m_charge[np] *= m_Nparticles*(1+shotnoize);
            if(dtE[1] == 0){
                m_charge[np] /= ntE[1];
            }
#ifdef PART_RANDOM
            m_charge[np] = 1.0;
#endif
            if(m_charge[np] < threshold){
                continue;
            }
            np++;
            if(np == m_Nparticles){
                break;
            }
        }
        if(np == m_Nparticles){
            break;
        }
    }
    m_Nparticles = np;

#ifdef _DEBUG
    vector<int> steps, inistep, finstep;
    mpi_steps(1, m_Nparticles, m_gprocesses, &steps, &inistep, &finstep);
    for(int rank = 0; rank < m_gprocesses; rank++){
        if(inistep[rank] <= TargetParticle && finstep[rank] >= TargetParticle){
            TargetRank = rank;
            break;
        }
    }
#endif

    double tcharge = vectorsum(m_charge, m_Nparticles);
    m_charge *= m_Nparticles/tcharge;

#ifdef _DEBUG
    if((!f_GetParticleDataName(-1).empty() || !InputCSRTrack.empty()) && m_grank == 0){
        ofstream debug_out;
        ofstream debug_out2;
        vector<double> items(9);
        vector<double> items2(7);
        string dataname = f_GetParticleDataName(-1);

        if(!dataname.empty()){
            debug_out.open(dataname);
            vector<string> titles{"t(fs)", "DE/E", "No.", "x(m)", "y(m)", "x'(rad)", "y'(rad)", "Weight", "DEW"};
            PrintDebugItems(debug_out, titles);
        }
        if(!InputCSRTrack.empty()){
            debug_out2.open(InputCSRTrack);
            items2[0] = -0.005;
            for(int j = 1; j < 7; j++){
                items2[j] = 0;
            }
            PrintDebugItems(debug_out2, items2, " ");
            items2[3] = m_acc[eGeV_]*1e9;
            PrintDebugItems(debug_out2, items2, " ");
        }


        for(int m = 0; m < m_Nparticles; m++){
            if(m_charge[m] == 0){
                continue;
            }
            items[2] = m;
            for(int j = 0; j < 2; j++){
                items[j+3] = m_particles[m]._xy[j];
                items[j+5] = m_particles[m]._qxy[j];
                items[j] = m_particles[m]._tE[j];
            }
            items[0] *= 1e15;
            items[7] = m_charge[m];
            items[8] = items[1]*items[7];
            if(!dataname.empty()){
                PrintDebugItems(debug_out, items);
            }
            if(!InputCSRTrack.empty()){
                // "t(fs)", "DE/E", "No.", "x(m)", "y(m)", "x'(rad)", "y'(rad)", "Weight"
                items2[0] = -items[0]/1e15*CC; // t <- t
                items2[1] = items[3]; // y <- x
                items2[2] = items[4]; // z <- y
                items2[3] = items[1]*m_acc[eGeV_]*1e9; // dxp <- DE/E
                items2[4] = items[5]*m_acc[eGeV_]*1e9; // dyp <- x'
                items2[5] = items[6]*m_acc[eGeV_]*1e9; // dzp <- y'
                items2[6] = m_bunchelectrons*items[7]/m_Nparticles*QE; // q <- Weight
                PrintDebugItems(debug_out2, items2, " ");
            }
        }
        if(!InputCSRTrack.empty()){
            debug_out.close();
        }
        if(!InputCSRTrack.empty()){
            debug_out2.close();
        }
    }
#endif

    for(int m = 0; m < m_Nparticles; m++){
        m_particles[m]._tE[0] += m_t0*2.0*m_particles[m]._tE[1];
    }

#ifdef _DEBUG
    if(!FELTrajectory.empty() && m_grank == TargetRank){
        vector<double> items(17);
        ofstream debug_out(FELTrajectory);
        vector<string> titles{"z", "xref", "x", "yref", "y",
            "x'ref", "x'", "y'ref", "y'", "tref", "t", "DEref", "DE/E", "Exref", "Ex", "Ezref", "Ez"};
        PrintDebugItems(debug_out, titles);

        items[0] = m_zorbit[0];
        for(int j = 0; j < 2; j++){
            items[2*j+1] = m_reference._xy[j];
            items[2*j+2] = m_particles[TargetParticle]._xy[j];
            items[2*j+5] = m_reference._qxy[j];
            items[2*j+6] = m_particles[TargetParticle]._qxy[j];
            items[2*j+9] = m_reference._tE[j];
            items[2*j+10] = m_particles[TargetParticle]._tE[j];
        }
        items[9] *= 1e15;
        items[10] *= 1e15;
        PrintDebugItems(debug_out, items);
        debug_out.close();
    }
#endif

    return true;
}

void FELAmplifier::f_SetGridPoints(bool init, int spincr, double Deltaxy[])
{
    if(!init && !m_bfreuse){
        delete m_fftsp;
        for(int n = 0; n < m_nfftsp[0]; n++){
            delete[] m_fftspws[n];
        }
        delete[] m_fftspws;
        delete[] m_wssp;
        for(int j = 0; j < 6; j++){
            m_FxyCart[j].clear(); m_FxyCart[j].shrink_to_fit();
            m_FxyGrid[j].clear(); m_FxyGrid[j].shrink_to_fit();
            m_FbufSec[j].clear(); m_FbufSec[j].shrink_to_fit();
        }
        m_EtGrid.clear(); m_EtGrid.shrink_to_fit();
    }
    for(int j = 0; j < 2 && !m_bfreuse; j++){
        m_nshalf[j] = (int)floor(Deltaxy[j]/m_dxy[j]+0.5);
        m_xygrid[j].resize(2*m_nshalf[j]+1);
        for(int n = -m_nshalf[j]; n <= m_nshalf[j]; n++){
            m_xygrid[j][n+m_nshalf[j]] = n*m_dxy[j];
        }
    }

    m_nspincr = 1<<spincr;
    for(int j = 0; j < 2 && !m_bfreuse; j++){
        m_nfftsp[j] = 1;
        while(m_nfftsp[j] < 3*m_nshalf[j]+1){
            m_nfftsp[j] <<= 1;
        }
        m_nfftsp[j] *= m_nspincr;
        m_nshalfm[j] = m_nshalf[j]*m_nspincr;
        m_dxyN[j] = m_dxy[j]/m_nspincr;
    }

    if(!m_bfreuse){
        m_fftsp = new FastFourierTransform(2, m_nfftsp[0], m_nfftsp[1]);
        m_fftspws = new double *[m_nfftsp[0]];
        for(int n = 0; n < m_nfftsp[0]; n++){
            m_fftspws[n] = new double[2*m_nfftsp[1]];
        }
        for(int j = 0; j < 2*m_dim; j++){
            m_FxyCart[j].resize(m_nfd);
            for(int n = 0; n < m_nfd; n++){
                m_FxyCart[j][n].resize((2*m_nshalfm[0]+1)*(2*m_nshalfm[1]+1));
            }
        }
        m_wssp = new double[(2*m_nshalfm[0]+1)*(2*m_nshalfm[1]+1)];
    }

    int mesh[2] = {2*m_nshalf[0]+1, 2*m_nshalf[1]+1};
    if(m_bfreuse){
        mesh[0] = mesh[1] = 1;
    }
    int nstot = mesh[0]*mesh[1];
    m_EtGrid.resize(mesh[0]);
    for(int nx = 0; nx < mesh[0]; nx++){
        m_EtGrid[nx].resize(mesh[1]);
        for(int ny = 0; ny < mesh[1]; ny++){
            m_EtGrid[nx][ny].resize(m_dim);
            for(int j = 0; j < m_dim; j++){
                m_EtGrid[nx][ny][j].resize(2*m_hntgrid+1, 0.0);
            }
        }
    }
    for(int j = 0; j < 2*m_dim; j++){
        m_FxyGrid[j].resize(m_nfd);
        m_FbufSec[j].resize(m_nsections);
        for(int nsec = 0; nsec < m_nsections; nsec++){
            m_FbufSec[j][nsec].resize(nstot);
            for(int n = 0; n < nstot; n++){
                m_FbufSec[j][nsec][n].resize(m_nfd);
            }
        }
    }
    m_hnxymax[0] = m_hnxymax[1] = 0;
}

void FELAmplifier::f_SetAngularGrid(double bmsize[])
{
    double eps = 0.05/(1<<(m_accuracy[acclimobs_]-1));

    m_nsq[0] = 8<<m_accuracy[accinobs_];
    m_dq[0] = PI2/m_nsq[0];

    // delta_theta defined by the divergence at max. energy
    m_dq[1] = wave_length(m_epmax_fel)/PI2/max(bmsize[0], bmsize[1])/2.0;
    m_dq[1] /= 1<<(m_accuracy[accinobs_]-1);

    // minimum angular acceptance
    double thetaCSR = wave_length(m_confv[eproi_][0])/min(m_size[0], m_size[1])/4/PI;
    thetaCSR *= (1+m_accuracy[acclimobs_]); // default 2*sigma

    m_qxqy[0] = m_qxqy[1] = 0;
    f_AllocateElectricField(true, false, true);
    double pmax = m_Etmax*m_Etmax, pr;
    double thetamax = 0;
    do{
        thetamax += 0.5/m_gamma;
        pr = 0;
        for(int j = 0; j < 2; j++){
            m_qxqy[j] = thetamax;
            m_qxqy[1-j] = 0;
            f_AllocateElectricField(true, false, true);
            pr = max(pr, m_Etmax);
        }
        pr *= pr;
        pmax = max(pmax, pr);
    } while(pr > pmax*eps || thetamax < thetaCSR);

    m_nsq[1] = (int)ceil(thetamax/m_dq[1]);

    for(int j = 0; j < 2; j++){
        m_qgrid[j].resize(m_nsq[j]);
        for(int n = 0; n < m_nsq[j]; n++){
            m_qgrid[j][n] = n*m_dq[j];
        }
    }

    m_Zorg = m_torg = 0;
    double Lmax = max(fabs(m_Zmid[m_nsections-1]-m_Zorg), fabs(m_Zmid[0]-m_Zorg));
    double eproi, qlimmax;
    double explim = 3; // 3sigma
    double seeddiv = m_qgrid[1].back();
    for(int i = 0; i < m_seed.size(); i++){
        seeddiv = max(seeddiv, m_seed[i]->GetDivergence());
    }

    m_qstore.resize(m_nsq[0]);
    for(int np = 0; np < m_nsq[0]; np++){
        for(int nq = 1; nq < m_nsq[1]; nq++){
            double thetaavg = (m_qgrid[1][nq-1]+m_qgrid[1][nq])/2;
            for(int ne = m_nfdbf-1; ne > 0; ne--){
                qlimmax = f_ThetaLimit(explim, np, m_epbf[ne]);
                if(qlimmax >= thetaavg){
                    eproi = m_epbf[ne];
                    break;
                }
            }
            double dtheta = wave_length(eproi)/8/Lmax/thetaavg;
            int ndiv = max(1, (int)floor(0.5+(m_qgrid[1][nq]-m_qgrid[1][nq-1])/dtheta));
            dtheta = (m_qgrid[1][nq]-m_qgrid[1][nq-1])/ndiv;
            if(m_qgrid[1][nq] < seeddiv*explim){
                while(dtheta > seeddiv*0.5){
                    dtheta *= 0.5;
                    ndiv *= 2;
                }
            }
            for(int nv = 1; nv <= ndiv; nv++){
                m_qstore[np].push_back(m_qgrid[1][nq-1]+nv*dtheta);
            }
        }
    }
    m_nqlimbf.resize(m_nsq[0]);
    for(int np = 0; np < m_nsq[0]; np++){
        m_nqlimbf[np].resize(m_nfdbf, (int)m_qstore[np].size()-1);
        for(int ne = 0; ne < m_nfdbf; ne++){
            qlimmax = f_ThetaLimit(explim, np, m_epbf[ne]);
            for(int nq = 0; nq < m_qstore[np].size(); nq++){
                if(m_qstore[np][nq] > qlimmax){
                    m_nqlimbf[np][ne] = max(0, nq-1);
                    break;
                }
            }
        }
    }

    m_nqlim.resize(m_nsq[0]);
    for(int np = 0; np < m_nsq[0]; np++){
        m_nqlim[np].resize(m_nfd);
        for(int ne = 0; ne < m_nfd; ne++){
            qlimmax = f_ThetaLimit(explim, np, m_ep[max(0, ne-1)]);
            m_nqlim[np][ne] = min(m_nsq[1]-1, (int)ceil(qlimmax/m_dq[1]));
        }
    }

    for(int j = 0; j < 4; j++){
        m_FwGrid[j].resize(m_nsq[0]);
        for(int np = 0; np < m_nsq[0]; np++){
            m_FwGrid[j][np].resize(m_nfd);
            for(int ne = 0; ne < m_nfd; ne++){
                m_FwGrid[j][np][ne].resize(m_nqlim[np][ne]+2, 0.0);
            }
        }
        m_FwGridbf[j].resize(m_nsq[0]);
        for(int np = 0; np < m_nsq[0]; np++){
            m_FwGridbf[j][np].resize(m_nfdbf);
            for(int ne = 0; ne < m_nfdbf; ne++){
                m_FwGridbf[j][np][ne].resize(m_nqlimbf[np][ne]+2, 0.0);
            }
        }
    }
}

double FELAmplifier::f_GetCharge(Particle &particle, double dtE[], bool isnew)
{
    int jini;
    double q;
    if(m_isEtprof){
        q = m_Etprof.GetLocalVolume2D(isnew?0:-1, dtE, particle._tE, true);
        return q;
    }
    else if(m_iscurrprof){
        q = m_currprof.GetLocalVolume1D(0, dtE[0], particle._tE[0], true);
        jini = 1;
    }
    else{
        q = 1;
        jini = 0;
    }

    double sigtE[2];
    sigtE[0] = m_acc[bunchlength_]*0.001/CC;
    sigtE[1] = EnergySpreadSigma();

    for(int j = jini; j < 2; j++){
        if(sigtE[j] == 0){
            continue;
        }
        double tex = particle._tE[j]/sigtE[j];
        tex *= tex*0.5;
        if(tex > MAXIMUM_EXPONENT){
            return 0;
        }
        q *= exp(-tex)/SQRTPI2/sigtE[j]*dtE[j];
    }
    return q;
}

double FELAmplifier::f_ElectronNumber(double t)
{
    double electrons;
    if(m_iscurrprof){
        electrons = m_currprof.GetLocalVolume1D(0, m_dt, t, false)/QE;
    }
    else if(m_isEtprof){
        electrons = m_Etprof.GetLocalVolume1D(0, m_dt, t, false)/QE;
    }
    else{
        double sigt = m_acc[bunchlength_]*0.001/CC;
        double tex = t/sigt;
        tex *= 0.5*tex;
        if(tex > MAXIMUM_EXPONENT){
            return 0;
        }
        electrons = m_bunchelectrons*m_dt/SQRTPI2/sigt*exp(-tex);
    }
    return electrons;
}

double FELAmplifier::f_ThetaLimit(double explim, int np, double ep)
{
    double thlim = explim/(ep/PLANKCC)/
        sqrt(hypotsq(
            cos(m_qgrid[0][np])*m_bmmin[0],
            sin(m_qgrid[0][np])*m_bmmin[1])
            );

    return min(m_qgrid[1].back(), thlim);
}

// functions to solve FEL equations
void FELAmplifier::f_AdvanceParticlesSection(int nsec)
{
#ifdef _DEBUG
    vector<vector<double>> items;
    vector<double> item(17);
    double Eref[3];
#endif
    vector<vector<double>> *Exy;
    double Ej[3];
    int nidx[2];

    vector<int> steps, inistep, finstep;
    mpi_steps(1, m_Nparticles, m_gprocesses, &steps, &inistep, &finstep);

    for(int nx = 0; nx <= 2*m_nshalf[0]; nx++){
        for(int ny = 0; ny <= 2*m_nshalf[1]; ny++){
            for(int j = 0; j < 3; j++){
                fill(m_EtGrid[nx][ny][j].begin(), m_EtGrid[nx][ny][j].end(), 0.0);
            }
        }
    }
    double dnstep = max(2.0, (double)(m_secidx[1][nsec]-m_secidx[0][nsec])/(double)m_advsteps);
    double xyo[2];
    int irep = 0;
    double torg = nsec == 0 ? m_t0 : m_tstep[nsec-1];
    double tslip = torg-m_tstep[nsec];
    double Fz, Fzsum = 0;

    for(int nz = 2*m_secidx[0][nsec]+2; nz <= 2*m_secidx[1][nsec]; nz += 2){
        int dnz = nz/2-m_secidx[0][nsec];
        if(nz/2 < m_secidx[1][nsec] && (irep == 0 || dnz == (int)floor(0.5+dnstep*irep))){
            irep++;
            // target (= mid) point in this range
            int inz = min(m_secidx[1][nsec], nz/2+(int)floor(0.5*dnstep));

            for(int j = 0; j < 2; j++){
                xyo[j] = m_xyref[j][inz];
            }

            // generate the field inside this section
            int zrangelim[2] = {m_secidx[0][nsec], inz};
            f_GetRadWaveform(nsec, xyo, m_zorbit[inz], torg, zrangelim);

            //----->>>>>>
            if(m_rank == 0){
                cout << setprecision(4) << endl << "section: " << nsec << "/" 
                    << m_nsections-1 << ", z ->" << m_zorbit[inz] << endl;
            }
        }

        for(int j = 0; j < 2; j++){
            xyo[j] = m_xyref[j][nz/2];
        }

        for(int m = 0; m < m_Nparticles; m++){
            if(m < inistep[m_grank] || m > finstep[m_grank] || m_charge[m] == 0){
                continue;
            }
            for(int j = 0; j < 2; j++){
                nidx[j] = (int)floor(((m_particles[m]._xy[j]-xyo[j])-m_xygrid[j][0])/m_dxy[j]+0.5);
            }
            if(nidx[0] >= 0 && nidx[0] < m_xygrid[0].size()
                && nidx[1] >= 0 && nidx[1] < m_xygrid[1].size()){
                Exy = &m_EtGrid[nidx[0]][nidx[1]];
            }
            else{
                Exy = nullptr;
            }

#ifdef _ONLYAXIS
            Exy = &m_EtGrid[m_nshalf[0]][m_nshalf[1]];
#endif

            m_trajectory->AdvancePhaseSpace(nz-2, m_tgrid, Exy, m_particles[m], &Fz, Ej);
            Fzsum += Fz*m_charge[m];
#ifdef _DEBUG
            if(!FELTrajectory.empty() && m == TargetParticle && m_grank == TargetRank){
                m_trajectory->AdvancePhaseSpace(nz-2, m_tgrid,
                    &m_EtGrid[m_nshalf[0]][m_nshalf[1]], m_reference, &Fz, Eref);
                // m_reference: reference particle for debugging
                item[0] = m_zorbit[nz/2];
                for(int j = 0; j < 2; j++){
                    item[2*j+1] = m_reference._xy[j];
                    item[2*j+2] = m_particles[TargetParticle]._xy[j];
                    item[2*j+5] = m_reference._qxy[j];
                    item[2*j+6] = m_particles[TargetParticle]._qxy[j];
                    item[2*j+9] = m_reference._tE[j];
                    item[2*j+10] = m_particles[TargetParticle]._tE[j];
                }
                item[9] *= 1e15;
                item[10] *= 1e15;
                item[13] = Eref[0];
                item[14] = Ej[0];
                item[15] = Eref[2];
                item[16] = Ej[2];
                items.push_back(item);
            }
#endif
            if(nz == 2*m_secidx[1][nsec]){
                // reached the final position, adjust time
                m_particles[m]._tE[0] -= tslip;
#ifdef _DEBUG
                if(!FELTrajectory.empty() && m == TargetParticle && m_grank == TargetRank){
                    m_reference._tE[0] -= tslip;
                }
#endif
            }
        }
        MPI_Barrier(MPI_COMM_WORLD);
        m_calcstatus->AdvanceStep(m_fellayer);
    }

#ifdef _DEBUG
    if(!FELTrajectory.empty() && m_grank == TargetRank){
        ofstream debug_out;
        if(FELTrajectory.find("append") != string::npos){
            debug_out.open(FELTrajectory, ios_base::app);
        }
        else{
            debug_out.open(FELTrajectory);
            vector<string> titles{"z", "xref", "x", "yref", "y",
                "x'ref", "x'", "y'ref", "y'", "tref", "t", "DEref", "DE/E", "Exref", "Ex", "Ezref", "Ez"};
            PrintDebugItems(debug_out, titles);
        }
        for(int n = 0; n < items.size(); n++){
            PrintDebugItems(debug_out, items[n]);
        }
        debug_out.close();
    }
#endif
}

void FELAmplifier::f_GetBunchFactor(int tgtsection)
    // compute the current bunch factor and save in m_bunchf[tgtsection]
{
    vector<int> steps, inistep, finstep;
    mpi_steps(1, m_Nparticles, m_gprocesses, &steps, &inistep, &finstep);

    int hetamax = 0;
    for(int n = 0; n < m_Nparticles; n++){
        if(n < inistep[m_grank] || n > finstep[m_grank]){
            continue;
        }
        hetamax = max(hetamax,
            (int)floor(0.5+fabs(m_particles[n]._tE[1])/m_d_eta)+1);
    }
    if(m_gprocesses > 1){
        for(int rank = 0; rank < m_gprocesses; rank++){
            int temp = hetamax;
            if(m_thread != nullptr){
                m_thread->Bcast(&temp, 1, MPI_INT, rank, m_grank);
            }
            else{
                MPI_Bcast(&temp, 1, MPI_INT, rank, MPI_COMM_WORLD);
            }
            hetamax = max(temp, hetamax);
        }
    }
    int neta = 2*hetamax+1;

    f_ClearEwFFTbf(0);

    for(int n = 0; n < (int)m_currt.size() && m_confb[exportEt_]; n++){
        m_curr_j[tgtsection][n].resize(neta, 0.0);
    }

    int nr[2], ns[2];
    double r56t = tgtsection == m_nsections+1 ? -m_conf[R56_]/CC : 0;
    for(int n = 0; n < m_Nparticles; n++){
        if(n < inistep[m_grank] || n > finstep[m_grank]){
            continue;
        }
        if(m_charge[n] == 0){
            continue;
        }
        double dnt = (m_particles[n]._tE[0]+r56t*m_particles[n]._tE[1])/m_dt;
        double dneta = m_particles[n]._tE[1]/m_d_eta;
        nr[0] = (int)floor(dnt); nr[1] = nr[0]+1;
        ns[0] = (int)floor(dneta); ns[1] = ns[0]+1;
        for(int i = 0; i < 2; i++){
            int idx = fft_index(nr[i], m_nfftbf, -1);
            if(idx >= 0 && idx < m_nfftbf){
                m_EwFFTbf[0][idx] +=
                    fabs(nr[1-i]-dnt)*m_charge[n]/m_Nparticles;
            }
            if(!m_confb[exportEt_] || abs(nr[i]) > m_hncurrt){
                continue;
            }
            for(int k = 0; k < 2; k++){
                if(abs(ns[k]) > hetamax){
                    continue;
                }
                m_curr_j[tgtsection][nr[i]+m_hncurrt][ns[k]+hetamax] +=
                    fabs(nr[1-i]-dnt)*fabs(ns[1-k]-dneta)*m_charge[n]/m_Nparticles;

            }
        }
    }
    if(m_gprocesses > 1){
        int ntmax = m_nfftbf;
        int mtmax = (int)m_currt.size()*neta;
        if(m_confb[exportEt_]){
            ntmax = max(ntmax, mtmax);
        }
        if(m_ws[0].size() < ntmax){
            m_ws[0].resize(ntmax);
        }

        for(int n = 0; n < m_nfftbf; n++){
            m_ws[0][n] = m_EwFFTbf[0][n];
        }
        if(m_thread != nullptr){
            m_thread->Allreduce(m_ws[0].data(), m_EwFFTbf[0], m_nfftbf, MPI_DOUBLE, MPI_SUM, m_grank);
        }
        else{
            MPI_Allreduce(m_ws[0].data(), m_EwFFTbf[0], m_nfftbf, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
        }
        if(m_confb[exportEt_]){
            if(m_ws[1].size() < mtmax){
                m_ws[1].resize(mtmax);
            }
            for(int n = 0; n < (int)m_currt.size(); n++){
                for(int m = 0; m < neta; m++){
                    m_ws[0][n*neta+m] = m_curr_j[tgtsection][n][m];
                }
            }
            if(m_thread != nullptr){
                m_thread->Allreduce(m_ws[0].data(), m_ws[1].data(), mtmax, MPI_DOUBLE, MPI_SUM, m_grank);
            }
            else{
                MPI_Allreduce(m_ws[0].data(), m_ws[1].data(), mtmax, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
            }
            for(int n = 0; n < (int)m_currt.size(); n++){
                for(int m = 0; m < neta; m++){
                    m_curr_j[tgtsection][n][m] = m_ws[1][n*neta+m];
                }
            }
        }
    }

    for(int n = -m_hncurrt; n <= m_hncurrt; n++){
        int idx = fft_index(n, m_nfftbf, -1);
        m_currI[tgtsection][n+m_hncurrt] = m_EwFFTbf[0][idx]*m_bunchelectrons*QE/m_dt;
        for(int i = 0; i < neta && m_confb[exportEt_]; i++){
            m_curr_j[tgtsection][n+m_hncurrt][i] *= m_bunchelectrons*QE/m_d_eta/m_dt;
        }
    }

#ifdef _DEBUG
    if(!FELCurrProfileDebug.empty() && m_grank == 0){
        ofstream debug_out(FELCurrProfileDebug);
        vector<string> titles{"time(fs)", "I(A)"};
        vector<double> items(2);
        PrintDebugItems(debug_out, titles);
        for(int n = 0; n < m_currt.size(); n++){
            items[0] = m_currt[n]*1e15;
            items[1] = m_currI[tgtsection][n];
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
    if(!FELEtProfileDebug.empty() && m_grank == 0 && m_confb[exportEt_]){
        ofstream debug_out(FELEtProfileDebug);
        vector<string> titles{"time(fs)", "DE/E", "j(A/100%)"};
        vector<double> items(3);
        PrintDebugItems(debug_out, titles);
        for(int n = 0; n < m_currt.size(); n++){
            items[0] = m_currt[n]*1e15;
            for(int i = -hetamax; i <= hetamax; i++){
                items[1] = i*m_d_eta;
                items[2] = m_curr_j[tgtsection][n][i+hetamax];
                PrintDebugItems(debug_out, items);
            }
        }
        debug_out.close();
    }
#endif
    if(tgtsection > m_nsections){
        // bunch factor not needed
        return;
    }

    m_fftbf->DoRealFFT(m_EwFFTbf[0]);
    for(int ne = 0; ne < m_nfdbf; ne++){
        if(ne == 0){
            m_bunchf[tgtsection][0][ne] = m_EwFFTbf[0][0];
            m_bunchf[tgtsection][1][ne] = 0;
        }
        for(int j = 0; j < 2; j++){
            m_bunchf[tgtsection][j][ne] = m_EwFFTbf[0][2*ne+j];
        }
    }

#ifdef _DEBUG
    if(!FELBunchFactorDebug.empty() && m_grank == 0){
        ofstream debug_out(FELBunchFactorDebug);
        vector<string> titles{"ep(eV)", "Bre", "Bim"};
        vector<double> items(3);
        PrintDebugItems(debug_out, titles);
        for(int ne = 0; ne < m_nfdbf; ne++){
            items[0] = m_epbf[ne];
            for(int j = 0; j < 2; j++){
                items[j+1] = m_bunchf[tgtsection][j][ne];
            }
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif
}

void FELAmplifier::f_GetRadWaveformPoint(double Zpos, double xyobs[], double torg)
{
    double xy[2], qxy[2], dxy[2], *qxyp = nullptr;
    double sigdiv = m_accuracy[accinobs_]+0.5;
    double grange = 1.5+m_accuracy[acclimobs_];
    int hmesh = (int)floor(0.5+sigdiv*grange);

    vector<double> tex(hmesh+1);
    for(int n = 0; n <= hmesh; n++){
        tex[n] = n/sigdiv;
        tex[n] *= tex[n]*0.5;
        tex[n] = exp(-tex[n])/SQRTPI2/sigdiv;
    }

    vector<int> steps, inistep, finstep;
    mpi_steps(2*hmesh+1, 2*hmesh+1, m_gprocesses, &steps, &inistep, &finstep);

    m_calcstatus->SetSubstepNumber(m_csrlayer, m_nsections);
    if(m_confb[fouriep_]){
        qxyp = qxy;
        for(int j = 0; j < 2; j++){
            qxy[j] = xyobs[j];
        }
    }

    for(int nsec = 0; nsec < m_nsections; nsec++){
        for(int j = 0; j < 2; j++){
            dxy[j] = m_bmsize[j][nsec]/sigdiv;
        }
        for(int n = 0; n < m_nfd; n++){
            for(int j = 0; j < 2*m_dim; j++){
                m_FbufSec[j][nsec][0][n] = 0;
            }
        }
        for(int nx = -hmesh; nx <= hmesh; nx++){
            for(int ny = -hmesh; ny <= hmesh; ny++){
                if(m_confb[fouriep_]){
                    xy[0] = dxy[0]*nx;
                    xy[1] = dxy[1]*ny;
                }
                else{
                    xy[0] = xyobs[0]-dxy[0]*nx;
                    xy[1] = xyobs[1]-dxy[1]*ny;
                }
                int nxy = (hmesh+ny)+(hmesh+nx)*(2*hmesh+1);
                if(nxy < inistep[m_grank] || nxy > finstep[m_grank]){
                    continue;
                }
                f_GetComplexAmpAt(nsec, xy, Zpos, m_tmid[nsec], nullptr, nullptr, qxyp);
                for(int n = 0; n < m_nfd; n++){
                    for(int j = 0; j < 2*m_dim; j++){
                        m_FbufSec[j][nsec][0][n] += 
                            m_Fxy[j][n]*tex[abs(nx)]*tex[abs(ny)];
                    }
                }
            }
        }
        if(m_gprocesses > 1){
            for(int j = 0; j < m_dim; j++){
                for(int n = 0; n < m_nfd; n++){
                    m_EwFFT[0][2*n] = m_FbufSec[2*j][nsec][0][n];
                    m_EwFFT[0][2*n+1] = m_FbufSec[2*j+1][nsec][0][n];
                }
                if(m_thread != nullptr){
                    m_thread->Allreduce(m_EwFFT[0], m_EwFFT[1], 2*m_nfd, MPI_DOUBLE, MPI_SUM, m_grank);
                }
                else{
                    MPI_Allreduce(m_EwFFT[0], m_EwFFT[1], 2*m_nfd, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
                }
                for(int n = 0; n < m_nfd; n++){
                    m_FbufSec[2*j][nsec][0][n] = m_EwFFT[1][2*n];
                    m_FbufSec[2*j+1][nsec][0][n] = m_EwFFT[1][2*n+1];
                }
            }
        }
        m_calcstatus->AdvanceStep(m_csrlayer);
    }

    f_GetTemporalBF(0, m_istime, m_nsections, xy, Zpos, torg, true);

    if(m_istime){
        double coef = GetTempCoef(true);
        for(int n = -m_hntgrid; n <= m_hntgrid; n++){
            int idx = fft_index(n, m_nfftbf, -1);
            for(int j = 0; j < m_dim; j++){
                m_EtGrid[0][0][j][n+m_hntgrid] = m_EwFFTbf[j][idx]*coef;
            }
        }
        if(!FELTempProfile.empty() && m_grank == 0){
            f_PrintTemp(FELTempProfile, xy, true, 0);
        }
    }
    MPI_Barrier(MPI_COMM_WORLD);
}

void FELAmplifier::f_GetRadWaveform(
    int tgtsection, double *xyoffset, double Zobs, double torg, int *zrangelim)
{
    int secend = min(tgtsection, m_nsections-1);
    double xyo[2] = {0, 0}, xyseed[2];

    if(xyoffset != nullptr){
        for(int j = 0; j < 2; j++){
            xyo[j] = xyoffset[j];
        }
    }

    for(int nsec = 0; nsec <= secend; nsec++){
        if(zrangelim != nullptr && nsec == tgtsection){
            f_GetComplexAmpAdv(tgtsection, xyo, Zobs, m_tmid[nsec], zrangelim, nsec == secend);
            // space charge assinged in [secend] variables
        }
        else{
            f_GetComplexAmpGrid(nsec, xyo, Zobs, m_tmid[nsec]);
        }
        m_calcstatus->AdvanceStep(m_fellayer);
        f_ConvoluteEbeamSize(nsec, xyo);
        // space charge assinged in 0-th section variables
        for(int nx = 0; nx <= 2*m_nshalf[0]; nx++){
            for(int ny = 0; ny <= 2*m_nshalf[1]; ny++){
                int nxycont = nx+ny*(2*m_nshalf[0]+1);
                int nxy = nx*m_nspincr+ny*m_nspincr*(2*m_nshalfm[0]+1);
                for(int n = 0; n < m_nfd; n++){
                    for(int j = 0; j < 2*m_dim; j++){
                        m_FbufSec[j][nsec][nxycont][n] = m_FxyCart[j][n][nxy];
                    }
                }
            }
        }
        m_calcstatus->AdvanceStep(m_fellayer);
    }

    double coef = GetTempCoef(true);
    vector<int> steps, inistep, finstep;
    mpi_steps(2*m_nshalf[0]+1, 2*m_nshalf[1]+1, m_gprocesses, &steps, &inistep, &finstep);
    m_calcstatus->SetSubstepNumber(m_fellayer+1, 2*m_nshalf[0]+1);

    for(int nx = -m_nshalf[0]; nx <= m_nshalf[0]; nx++){
        xyseed[0] = nx*m_dxy[0]+xyo[0];
        for(int ny = -m_nshalf[1]; ny <= m_nshalf[1]; ny++){
            xyseed[1] = ny*m_dxy[1]+xyo[1];
            int nxy  = (nx+m_nshalf[0])+(ny+m_nshalf[1])*(2*m_nshalf[0]+1);
            if(nxy >= inistep[m_grank] && nxy <= finstep[m_grank]){
                bool debex = (nx == 0 && ny == 0);
                f_GetTemporalBF(nxy, true, tgtsection, xyseed, Zobs, torg, debex);
                for(int n = -m_hntgrid; n <= m_hntgrid; n++){
                    int idx = fft_index(n, m_nfftbf, -1);
                    for(int j = 0; j < m_dim; j++){
                        m_EtGrid[nx+m_nshalf[0]][ny+m_nshalf[1]][j][n+m_hntgrid]
                            = m_EwFFTbf[j][idx]*coef;
                    }
                }
            }
        }
        m_calcstatus->AdvanceStep(m_fellayer+1);
    }
    m_calcstatus->AdvanceStep(m_fellayer);
    MPI_Barrier(MPI_COMM_WORLD);

    if(m_gprocesses > 1){
        for(int nx = -m_nshalf[0]; nx <= m_nshalf[0]; nx++){
            for(int ny = -m_nshalf[1]; ny <= m_nshalf[1]; ny++){
                int nxycont = (nx+m_nshalf[0])+(ny+m_nshalf[1])*(2*m_nshalf[0]+1);
                int currrank = get_mpi_rank(nxycont, m_gprocesses, inistep, finstep);
                for(int j = 0; j < m_dim; j++){
                    if(currrank == m_grank){
                        for(int n = 0; n <= 2*m_hntgrid; n++){
                            m_EwFFTbf[j][n] = m_EtGrid[nx+m_nshalf[0]][ny+m_nshalf[1]][j][n];
                        }
                    }
                    if(m_thread != nullptr){
                        m_thread->Bcast(m_EwFFTbf[j], 2*m_hntgrid+1, MPI_DOUBLE, currrank, m_grank);
                    }
                    else{
                        MPI_Bcast(m_EwFFTbf[j], 2*m_hntgrid+1, MPI_DOUBLE, currrank, MPI_COMM_WORLD);
                    }
                    if(currrank != m_grank){
                        for(int n = 0; n <= 2*m_hntgrid; n++){
                            m_EtGrid[nx+m_nshalf[0]][ny+m_nshalf[1]][j][n] = m_EwFFTbf[j][n];
                        }
                    }
                }
            }
        }
        MPI_Barrier(MPI_COMM_WORLD);
    }

    if(!FELTempProfile.empty() && m_grank == 0){
        double tslip = 0;
        if(zrangelim != nullptr){
           // tslip = torg-m_tzorb[zrangelim[1]];
        }
        f_PrintTemp(FELTempProfile, xyoffset, true, tslip);

    }
    MPI_Barrier(MPI_COMM_WORLD);
}

void FELAmplifier::f_GetComplexAmpGrid(
    int tgtsection, double *xyoffset, double Zobs, double torg)
{
    if(Zobs-m_Zex[tgtsection] < m_Zex[tgtsection]-m_Zmid[tgtsection]){
        // near field
        int zrangelim[2] = {m_secidx[0][tgtsection], m_secidx[1][tgtsection]};
        f_GetComplexAmpAdv(tgtsection, xyoffset, Zobs, torg, zrangelim);
        return;
    }

    double Sigmamn[2], dhxy[2], xy[2], dixy[2];
    double wavel = wave_length(m_epmax_fel);
    double L = Zobs-m_Zmid[tgtsection];
    int hnxy[2], nmax[2];

    for(int j = 0; j < 2; j++){
        double Dxy = 1.5*m_xygrid[j].back();
        Sigmamn[j] = sqrt(hypotsq(m_bmsize[j][tgtsection],
            wavel/PI2/m_bmsize[j][tgtsection]*L))/SQRT2;
        hnxy[j] = max(1, (int)floor(0.5+Dxy/Sigmamn[j]));
        dhxy[j] = Dxy/hnxy[j];
        nmax[j] = 2*hnxy[j];
        if(m_xygridrad[j].size() < 2*hnxy[j]+1){
            m_xygridrad[j].resize(2*hnxy[j]+1);
        }
        for(int n = -hnxy[j]; n <= hnxy[j]; n++){
            m_xygridrad[j][n+hnxy[j]] = dhxy[j]*n+xyoffset[j];
        }
    }

    if(m_hnxymax[0] < hnxy[0] || m_hnxymax[1] < hnxy[1]){
        for(int j = 0; j < 2; j++){
            m_hnxymax[j] = max(m_hnxymax[j], hnxy[j]);
        }
        for(int j = 0; j < 2*m_dim; j++){
            for(int n = 0; n < m_nfd; n++){
                m_FxyGrid[j][n].resize(2*m_hnxymax[0]+1);
                for(int nx = -m_hnxymax[0]; nx <= m_hnxymax[0]; nx++){
                    m_FxyGrid[j][n][nx+m_hnxymax[0]].resize(2*m_hnxymax[1]+1);
                }
            }
        }
    }

    m_calcstatus->SetSubstepNumber(m_fellayer+1, (2*hnxy[0]+1)*(2*hnxy[1]+1));

    vector<int> steps, inistep, finstep;
    mpi_steps(2*hnxy[0]+1, 2*hnxy[1]+1, m_gprocesses, &steps, &inistep, &finstep);

    for(int nx = -hnxy[0]; nx <= hnxy[0]; nx++){
        xy[0] = m_xygridrad[0][nx+hnxy[0]];
        for(int ny = -hnxy[1]; ny <= hnxy[1]; ny++){
            xy[1] = m_xygridrad[1][ny+hnxy[1]];
            int nxy = (nx+hnxy[0])+(ny+hnxy[1])*(2*hnxy[0]+1);
            if(nxy >= inistep[m_grank] && nxy <= finstep[m_grank]){
                f_GetComplexAmpAt(tgtsection, xy, Zobs, torg);
                for(int j = 0; j < 2*m_dim; j++){
                    for(int n = 0; n < m_nfd; n++){
                        m_FxyGrid[j][n][nx+hnxy[0]][ny+hnxy[1]] = m_Fxy[j][n];
                    }
                }
            }
            m_calcstatus->AdvanceStep(m_fellayer+1);
        }
    }
    MPI_Barrier(MPI_COMM_WORLD);

    if(m_gprocesses > 1){
        for(int nx = -hnxy[0]; nx <= hnxy[0]; nx++){
            for(int ny = -hnxy[1]; ny <= hnxy[1]; ny++){
                int nxy = (nx+hnxy[0])+(ny+hnxy[1])*(2*hnxy[0]+1);
                int currrank = get_mpi_rank(nxy, m_gprocesses, inistep, finstep);
                if(m_grank == currrank){
                    for(int j = 0; j < m_dim; j++){
                        for(int n = 0; n < m_nfd; n++){
                            m_EwFFT[j][2*n] = m_FxyGrid[2*j][n][nx+hnxy[0]][ny+hnxy[1]];
                            m_EwFFT[j][2*n+1] = m_FxyGrid[2*j+1][n][nx+hnxy[0]][ny+hnxy[1]];
                        }
                    }
                }
                for(int j = 0; j < m_dim; j++){
                    if(m_thread != nullptr){
                        m_thread->Bcast(m_EwFFT[j], 2*m_nfd, MPI_DOUBLE, currrank, m_grank);
                    }
                    else{
                        MPI_Bcast(m_EwFFT[j], 2*m_nfd, MPI_DOUBLE, currrank, MPI_COMM_WORLD);
                    }
                }
                if(m_grank != currrank){
                    for(int j = 0; j < m_dim; j++){
                        for(int n = 0; n < m_nfd; n++){
                            m_FxyGrid[2*j][n][nx+hnxy[0]][ny+hnxy[1]] = m_EwFFT[j][2*n];
                            m_FxyGrid[2*j+1][n][nx+hnxy[0]][ny+hnxy[1]] = m_EwFFT[j][2*n+1];
                        }
                    }
                }
            }
        }
        MPI_Barrier(MPI_COMM_WORLD);
    }

#ifdef _DEBUG
    if(!FELSprofGrid.empty() && m_grank == 0){
        ofstream debug_out(FELSprofGrid);
        vector<string> titles(2+2*m_dim*m_netgt.size());
        vector<double> items(2+2*m_dim*m_netgt.size());
        titles[0] = "x(mm)";
        titles[1] = "y(mm)";
        for(int n = 0; n < m_netgt.size(); n++){
            titles[2*m_dim*n+2] = "Ex.re"+to_string(m_ep[m_netgt[n]]);
            titles[2*m_dim*n+3] = "Ex.im"+to_string(m_ep[m_netgt[n]]);
            titles[2*m_dim*n+4] = "Ey.re"+to_string(m_ep[m_netgt[n]]);
            titles[2*m_dim*n+5] = "Ey.im"+to_string(m_ep[m_netgt[n]]);
            if(m_dim == 3){
                titles[2*m_dim*n+6] = "Ez.re"+to_string(m_ep[m_netgt[n]]);
                titles[2*m_dim*n+7] = "Ez.im"+to_string(m_ep[m_netgt[n]]);
            }
        }
        PrintDebugItems(debug_out, titles);
        for(int nx = -hnxy[0]; nx <= hnxy[0]; nx++){
            items[0] = m_xygridrad[0][nx+hnxy[0]]*1000;
            for(int ny = -hnxy[1]; ny <= hnxy[1]; ny++){
            //for(int ny = 0; ny <= 0; ny++){
                items[1] = m_xygridrad[1][ny+hnxy[1]]*1000;
                for(int n = 0; n < m_netgt.size(); n++){
                    for(int j = 0; j < 2*m_dim; j++){
                        items[2+4*n+j] = m_FxyGrid[j][m_netgt[n]][nx+hnxy[0]][ny+hnxy[1]];
                    }
                }
                PrintDebugItems(debug_out, items);
            }
        }
        debug_out.close();
    }
#endif

    mpi_steps(m_nfd, 1, m_gprocesses, &steps, &inistep, &finstep);

    for(int j = 0; j < 2*m_dim; j++){
        for(int n = 0; n < m_nfd; n++){
            if(n < inistep[m_grank] || n > finstep[m_grank]){
                continue;
            }
            for(int nx = -m_nshalfm[0]; nx <= m_nshalfm[0]; nx++){
                xy[0] = nx*m_dxyN[0]+xyoffset[0];
                dixy[0] = (xy[0]-m_xygridrad[0][0])/dhxy[0];
                for(int ny = -m_nshalfm[1]; ny <= m_nshalfm[1]; ny++){
                    int nxy = (nx+m_nshalfm[0])+(ny+m_nshalfm[1])*(2*m_nshalfm[0]+1);
                    xy[1] = ny*m_dxyN[1]+xyoffset[1];
                    dixy[1] = (xy[1]-m_xygridrad[1][0])/dhxy[1];
                    m_FxyCart[j][n][nxy] = lagrange2d(m_FxyGrid[j][n], dixy, nmax);
                }
            }
        }
    }

    if(m_gprocesses > 1){
        f_BcastFxyCart(inistep, finstep);
    }

#ifdef _DEBUG
    if(!FELAdvSprofBef.empty() && m_grank == 0){
        f_PrintAmpAdv(FELAdvSprofBef, xyoffset);
    }
#endif
}

void FELAmplifier::f_GetComplexAmpAdv(
    int tgtsection, double *xyoffset, double Zobs, double torg, int *zrangelim, bool spcharge)
{
    double xy[2], xyspc[3], *xyspcp = nullptr;
    vector<int> steps, inistep, finstep;
    mpi_steps(2*m_nshalfm[0]+1, 2*m_nshalfm[1]+1, m_gprocesses, &steps, &inistep, &finstep);

    int ncdiv = m_accuracy[accinobs_];
    double ddxy[2] = {m_dxyN[0]/2/ncdiv, m_dxyN[1]/2/ncdiv};
    for(int j = 0; j < 2*m_dim; j++){
        for(int n = 0; n < m_nfd; n++){
            fill(m_FxyCart[j][n].begin(), m_FxyCart[j][n].end(), 0.0);
        }
    }

    if(spcharge){
        xyspcp = xyspc;
        xyspc[2] = torg-m_tzorb[zrangelim[1]];
        // slip the space-charge field to follow the e-beam timing
    }
    m_calcstatus->SetSubstepNumber(m_fellayer+1, (2*m_nshalfm[0]+1)*(2*m_nshalfm[1]+1));
    for(int nx = -m_nshalfm[0]; nx <= m_nshalfm[0]; nx++){
        for(int ny = -m_nshalfm[0]; ny <= m_nshalfm[1]; ny++){
            int nxy = (nx+m_nshalfm[0])+(ny+m_nshalfm[1])*(2*m_nshalfm[0]+1);
            if(nxy >= inistep[m_grank] && nxy <= finstep[m_grank]){
#ifdef _ONLYAXIS
                if(nx != m_nshalf[0] || ny != m_nshalf[1]){
                    //if(ny != m_nshalf[1]){
                    continue;
                }
#endif
                if(nx == 0 && ny == 0){
                    for(int ix = 0; ix < 2*ncdiv; ix++){
                        xyspc[0] = (ix+0.5)*ddxy[0]-m_dxyN[0]*0.5;
                        xy[0] = xyspc[0]+xyoffset[0];
                        for(int iy = 0; iy < 2*ncdiv; iy++){
                            xyspc[1] = (iy+0.5)*ddxy[1]-m_dxyN[1]*0.5;
                            xy[1] = xyspc[1]+xyoffset[1];
                            f_GetComplexAmpAt(tgtsection, xy, Zobs, torg, zrangelim, xyspcp);
                            for(int j = 0; j < 2*m_dim; j++){
                                for(int n = 0; n < m_nfd; n++){
                                    m_FxyCart[j][n][nxy] += m_Fxy[j][n]/(4*ncdiv*ncdiv);
                                }
                            }
                        }
                    }
                }
                else{
                    xyspc[0] = nx*m_dxyN[0];
                    xyspc[1] = ny*m_dxyN[1];
                    xy[0] = xyspc[0]+xyoffset[0];
                    xy[1] = xyspc[1]+xyoffset[1];
                    f_GetComplexAmpAt(tgtsection, xy, Zobs, torg, zrangelim, xyspcp);
                    for(int j = 0; j < 2*m_dim; j++){
                        for(int n = 0; n < m_nfd; n++){
                            m_FxyCart[j][n][nxy] = m_Fxy[j][n];
                        }
                    }
                }
            }
            m_calcstatus->AdvanceStep(m_fellayer+1);
        }
    }
    MPI_Barrier(MPI_COMM_WORLD);

    if(m_gprocesses > 1){
        for(int nx = -m_nshalfm[0]; nx <= m_nshalfm[0]; nx++){
            for(int ny = -m_nshalfm[0]; ny <= m_nshalfm[1]; ny++){
                int nxy = (nx+m_nshalfm[0])+(ny+m_nshalfm[1])*(2*m_nshalfm[0]+1);
                int currrank = get_mpi_rank(nxy, m_gprocesses, inistep, finstep);
                if(m_grank == currrank){
                    for(int j = 0; j < m_dim; j++){
                        for(int n = 0; n < m_nfd; n++){
                            m_EwFFT[j][2*n] = m_FxyCart[2*j][n][nxy];
                            m_EwFFT[j][2*n+1] = m_FxyCart[2*j+1][n][nxy];
                        }
                    }
                }
                for(int j = 0; j < m_dim; j++){
                    if(m_thread != nullptr){
                        m_thread->Bcast(m_EwFFT[j], 2*m_nfd, MPI_DOUBLE, currrank, m_grank);
                    }
                    else{
                        MPI_Bcast(m_EwFFT[j], 2*m_nfd, MPI_DOUBLE, currrank, MPI_COMM_WORLD);
                    }
                }
                if(m_grank != currrank){
                    for(int j = 0; j < m_dim; j++){
                        for(int n = 0; n < m_nfd; n++){
                            m_FxyCart[2*j][n][nxy] = m_EwFFT[j][2*n];
                            m_FxyCart[2*j+1][n][nxy] = m_EwFFT[j][2*n+1];
                        }
                    }
                }
            }
        }
        MPI_Barrier(MPI_COMM_WORLD);
    }

#ifdef _DEBUG
    if(!FELAdvSprofBef.empty() && m_grank == 0){
        f_PrintAmpAdv(FELAdvSprofBef, xyoffset);
    }
#endif
}

void FELAmplifier::f_ConvoluteEbeamSize(int section, double *xyoffset)
{
    vector<int> steps, inistep, finstep;
    mpi_steps(m_nfd, 1, m_gprocesses, &steps, &inistep, &finstep);

    double cutoff[2];
    for(int j = 0; j < 2; j++){
        cutoff[j] = m_dxyN[j]/m_bmsize[j][section];
    }

    m_calcstatus->SetSubstepNumber(m_fellayer+1, m_nfd/m_gprocesses+1);
    for(int n = 0; n < m_nfd; n++){
        if(n < inistep[m_grank] || n > finstep[m_grank]){
            continue;
        }
        for(int j = 0; j < m_dim; j++){
            for(int nx = 0; nx < m_nfftsp[0]; nx++){
                for(int ny = 0; ny < m_nfftsp[1]; ny++){
                    if(nx > 2*m_nshalfm[0] || ny > 2*m_nshalfm[1]){
                        m_fftspws[nx][2*ny] = 0;
                        m_fftspws[nx][2*ny+1] = 0;
                        continue;
                    }
                    int nxy = nx+ny*(2*m_nshalfm[0]+1);
                    m_fftspws[nx][2*ny] = m_FxyCart[2*j][n][nxy];
                    m_fftspws[nx][2*ny+1] = m_FxyCart[2*j+1][n][nxy];
                }
            }
            m_fftsp->DoFFTFilter2D(m_fftspws, cutoff, true);
            for(int nx = 0; nx <= 2*m_nshalfm[0]; nx++){
                for(int ny = 0; ny <= 2*m_nshalfm[1]; ny++){
                    int nxy = nx+ny*(2*m_nshalfm[0]+1);
                    m_FxyCart[2*j][n][nxy] = m_fftspws[nx][2*ny];
                    m_FxyCart[2*j+1][n][nxy] = m_fftspws[nx][2*ny+1];
                }
            }
        }
        m_calcstatus->AdvanceStep(m_fellayer+1);
    }

    if(m_gprocesses > 1){
        f_BcastFxyCart(inistep, finstep);
    }

#ifdef _DEBUG
    if(!FELAdvSprofAft.empty() && m_grank == 0){
        f_PrintAmpAdv(FELAdvSprofAft, xyoffset);
    }
#endif
}

void FELAmplifier::f_GetComplexAmpAt(int tgtsection, double xy[],
    double Zobs, double torg, int *zrangelim, double *xytspc, double *qxy)
{
    if(zrangelim != nullptr){
        m_ntaupoints = zrangelim[1]+1;
    }
    else{
        m_ntaupoints = m_secidx[1][tgtsection]+1;
    }

    if(m_ntaupoints < 2 || m_ntaupoints > (int)m_tau.size()){
        for(int n = 0; n < m_nfd; n++){
            for(int j = 0; j < m_dim; j++){
                m_Fxy[2*j][n] = m_Fxy[2*j+1][n] = 0;
            }
        }
        return;
    }

    bool isfar = qxy != nullptr;
    if(isfar){
        f_SetXYAngle(qxy);
    }
    else{
        f_SetXYPosition(xy);
    }

    int zrange[2];
    for(int j = 0; j < 2; j++){
        if(zrangelim != nullptr){
            zrange[j] = zrangelim[j];
        }
        else{
            zrange[j] = m_secidx[j][tgtsection];
        }
    }
    m_XYZ[2] = Zobs;

    f_AllocateElectricField(false, true, isfar, &Zobs, &torg);
    f_AllocateComplexField(false, false, false, zrange, isfar, &Zobs, &torg);

    if(isfar){
        double xyq = qxy[0]*xy[0]+qxy[1]*xy[1];
        double dummy;
        for(int n = 0; n < m_nfd; n++){
            double phase = -m_ep[n]/PLANKCC*xyq;
                // sign(-) -> spatial Fourier: int F(x)exp(-ikx*x) dx
            double cs = cos(phase);
            double sn = sin(phase);
            for(int j = 0; j < 2; j++){
                m_Fxy[2*j][n] = (dummy=m_Fxy[2*j][n])*cs-m_Fxy[2*j+1][n]*sn;
                m_Fxy[2*j+1][n] = dummy*sn+m_Fxy[2*j+1][n]*cs;
            }
        }
    }

    if(xytspc == nullptr){
        return;
    }

    // add space charge field
    double spf, phase, W, r = sqrt(hypotsq(xytspc[0], xytspc[1]));
    for(int n = 1; n < m_nfd && r > 0; n++){
        W = PI2*r/wave_length(m_ep[n])/m_gamma;
        phase = xytspc[2]*m_ep[n]/(PLANCK/PI2);
        // time delay to follow the e-beam timing
        spf = -W*boost::math::cyl_bessel_k(0, W)/m_gamma/PI/r;
        m_Fxy[4][n] += spf*cos(phase);
        m_Fxy[5][n] += spf*sin(phase);
    }
}

void FELAmplifier::f_GetTemporalBF(int nxyindex, bool istime, int tgtsection,
    double xy[], double Zobs, double torg, bool debex)
{
    double ef[2], bf[2], ExyS[4], ExySn[4];
    double coef = GetTempCoef(true);
    double scoef = m_gamma2/PI*m_time2tau/coef;
    // m_gamma2/PI : Dw = Fw * gamma^2/Pi *(-i)
    // m_time2tau : dtau = 2*gamma^2*c dt

    int nsections[2];
    // sum up sections up to tgtsection (< m_nsecctions)
    nsections[0] = 0;
    nsections[1] = min(m_nsections-1, tgtsection);

    f_ClearEwFFTbf(2);

    if(m_seed.size() > 0){
        for(int n = 1; n < m_nfdbf; n++){
            for(int j = 0; j < 4; j++){
                ExyS[j] = 0;
            }
            for(int i = 0; i < m_seed.size(); i++){
                m_seed[i]->GetAmplitudeS(m_epbf[n], m_deFTbf, torg, Zobs, xy, ExySn);
                for(int j = 0; j < 4; j++){
                    ExyS[j] += ExySn[j];
                }
            }

            // *(-i); swap real/imaginary & negate imaginary
            std::swap(ExyS[0], ExyS[1]); ExyS[1] *= -1;
            std::swap(ExyS[2], ExyS[3]); ExyS[3] *= -1;
            for(int j = 0; j < 2; j++){
                // convert seed field to "Dw"
                m_EwFFTbf[j][2*n] = ExyS[2*j]*scoef;
                m_EwFFTbf[j][2*n+1] = ExyS[2*j+1]*scoef;
            }
            m_EwFFTbf[2][2*n] = m_EwFFTbf[2][2*n+1] = 0;
        }
    }

#ifdef _DEBUG
    if(!FELSpecSingle.empty() && debex){
        ofstream debug_out(FELSpecSingle);
        vector<string> titles(1+2*m_dim);
        vector<double> items(1+2*m_dim);
        titles[0] = "energy(eV)";
        titles[1] = "Ex.re";
        titles[2] = "Ex.im";
        titles[3] = "Ey.re";
        titles[4] = "Ey.im";
        if(m_dim == 3){
            titles[5] = "Ez.re";
            titles[6] = "Ez.im";
        }
        PrintDebugItems(debug_out, titles);
        for(int n = 0; n < m_nfd; n++){
            items[0] = m_ep[n];
            for(int j = 0; j < 2*m_dim; j++){
                items[j+1] = m_FbufSec[j][0][nxyindex][n];
            }
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif

    for(int j = 0; j < m_dim; j++){
        for(int nsec = nsections[0]; nsec <= nsections[1]; nsec++){
            for(int i = 0; i < 2; i++){
                m_FbufSpl[i].SetSpline(m_nfd, &m_ep, &m_FbufSec[2*j+i][nsec][nxyindex]);
            }
            for(int n = 0; n < m_nfdbf; n++){
                double phase = (torg-m_tmid[nsec])*m_epbf[n]/(PLANCK/PI2);
                double cs = cos(phase);
                double sn = sin(phase);
                bf[0] = m_bunchf[nsec][0][n]*cs-m_bunchf[nsec][1][n]*sn;
                bf[1] = m_bunchf[nsec][1][n]*cs+m_bunchf[nsec][0][n]*sn;

                ef[0] = m_FbufSpl[0].GetValue(m_epbf[n]);
                ef[1] = m_FbufSpl[1].GetValue(m_epbf[n]);
                m_EwFFTbf[j][2*n]   += ef[0]*bf[0]-ef[1]*bf[1];
                m_EwFFTbf[j][2*n+1] += ef[1]*bf[0]+ef[0]*bf[1];
            }
        }
    }

#ifdef _DEBUG
    if(!FELSpecProfile.empty() && m_grank == 0 && debex){
        f_PrintSpectrum(FELSpecProfile, m_dim);
    }
#endif

    if(!istime){
        return;
    }

    f_InverseFFT(FELTempWhole, m_dim, debex);
}

void FELAmplifier::f_InverseFFT(string dfile, int dim, bool debex, double tshift)
{
    double phase, cs, sn, dummy;
    double dnu = 2.0/(m_dtaubf*m_nfftbf); // 2.0: inverse real fft
    dnu *= PI/m_gamma2;

    for(int j = 0; j < dim; j++){
        for(int n = 0; n < m_nfdbf; n++){
            // Fw = Dw * (i Pi/gamma^2)
            swap(m_EwFFTbf[j][2*n], m_EwFFTbf[j][2*n+1]);
            m_EwFFTbf[j][2*n] *= -dnu;
            m_EwFFTbf[j][2*n+1] *= dnu;
            if(tshift != 0){
                phase = tshift*m_epbf[n]/(PLANCK/PI2);
                cs = cos(phase);
                sn = sin(phase);
                m_EwFFTbf[j][2*n] = (dummy=m_EwFFTbf[j][2*n])*cs-m_EwFFTbf[j][2*n+1]*sn;
                m_EwFFTbf[j][2*n+1] = dummy*sn+m_EwFFTbf[j][2*n+1]*cs;
            }
        }
        m_fftbf->DoRealFFT(m_EwFFTbf[j], -1);
    }

#ifdef _DEBUG
    if(!dfile.empty() && m_grank == 0 && debex){
        double tcoef = GetTempCoef(true);
        ofstream debug_out(dfile);
        vector<string> titles(3);
        titles[0] = "time";
        titles[1] = "Ex";
        titles[2] = "Ey";
        if(dim == 3){
            titles.push_back("Ez");
        }
        vector<double> items(titles.size());
        PrintDebugItems(debug_out, titles);
        for(int n = -m_hntgrid; n <= m_hntgrid; n++){
            items[0] = m_tgrid[n+m_hntgrid]*1e15;
            int idx = fft_index(n, m_nfftbf, -1);
            for(int j = 0; j < dim; j++){
                items[j+1] = m_EwFFTbf[j][idx]*tcoef;
            }
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif
}

void FELAmplifier::f_SetAmplitudeAng(int tgtsection)
{
    m_ntaupoints = m_secidx[1][tgtsection]+1;
    int zrange[2];
    for(int j = 0; j < 2; j++){
        zrange[j] = m_secidx[j][tgtsection];
    }

    vector<int> steps, inistep, finstep;
    mpi_steps(m_nsq[0], m_nsq[1], m_gprocesses, &steps, &inistep, &finstep);
    int npq;
    for(int np = 0; np < m_nsq[0]; np++){
        for(int nq = 0; nq < m_nsq[1]; nq++){
            if(nq == 0 && np > 0){
                for(int j = 0; j < 4; j++){
                    for(int ne = 0; ne < m_nfd; ne++){
                        m_FwGrid[j][np][ne][nq] = m_FwGrid[j][0][ne][0];
                    }
                }
                continue;
            }
            npq = nq+np*m_nsq[1];
            if(npq < inistep[m_grank] || npq > finstep[m_grank]){
                continue;
            }
            m_qxqy[0] = m_qgrid[1][nq]*cos(m_qgrid[0][np]);
            m_qxqy[1] = m_qgrid[1][nq]*sin(m_qgrid[0][np]);
            f_AllocateElectricField(false, true, true, &m_Zmid[tgtsection], &m_tmid[tgtsection]);
            f_AllocateComplexField(false, false, false, zrange, true, &m_Zmid[tgtsection], &m_tmid[tgtsection]);
            for(int ne = 0; ne < m_nfd; ne++){
                if(m_nqlim[np][ne] < nq){
                    continue;
                }
                for(int j = 0; j < 4; j++){
                    m_FwGrid[j][np][ne][nq] = m_Fxy[j][ne];
                }
            }
        }
        m_calcstatus->AdvanceStep(m_fellayer);
    }

    if(m_gprocesses > 1){
        for(int np = 0; np < m_nsq[0]; np++){
            for(int nq = 0; nq < m_nsq[1]; nq++){
                npq = nq+np*m_nsq[1];
                int currrank = get_mpi_rank(npq, m_gprocesses, inistep, finstep);
                if(m_grank == currrank){
                    for(int j = 0; j < 2; j++){
                        for(int ne = 0; ne < m_nfd; ne++){
                            if(m_nqlim[np][ne] < nq){
                                continue;
                            }
                            m_EwFFT[j][2*ne] = m_FwGrid[2*j][np][ne][nq];
                            m_EwFFT[j][2*ne+1] = m_FwGrid[2*j+1][np][ne][nq];
                        }
                    }
                }
                for(int j = 0; j < 2; j++){
                    if(m_thread != nullptr){
                        m_thread->Bcast(m_EwFFT[j], 2*m_nfd, MPI_DOUBLE, currrank, m_grank);
                    }
                    else{
                        MPI_Bcast(m_EwFFT[j], 2*m_nfd, MPI_DOUBLE, currrank, MPI_COMM_WORLD);
                    }
                }
                if(m_grank != currrank){
                    for(int j = 0; j < 2; j++){
                        for(int ne = 0; ne < m_nfd; ne++){
                            if(m_nqlim[np][ne] < nq){
                                continue;
                            }
                            m_FwGrid[2*j][np][ne][nq] = m_EwFFT[j][2*ne];
                            m_FwGrid[2*j+1][np][ne][nq] = m_EwFFT[j][2*ne+1];
                        }
                    }
                }
                MPI_Barrier(MPI_COMM_WORLD);
            }
        }
    }
}

void FELAmplifier::f_AddCA(int nsec, int np, int ne, int nq)
{
    if(nsec == 0 && m_seed.size() > 0 && ne > 0){
        double coef = GetTempCoef(true);
        double wavelen = wave_length(m_epbf[ne]);
        double scoef = -m_gamma2/PI*m_time2tau/coef/wavelen;
        double Exy[4], Exyn[4], kxy[2];
        kxy[0] = m_epbf[ne]/PLANKCC*m_qstore[np][nq];
        kxy[1] = kxy[0]*sin(m_qgrid[0][np]);
        kxy[0] *= cos(m_qgrid[0][np]);
        for(int j = 0; j < 4; j++){
            Exy[j] = 0;
        }
        for(int i = 0; i < m_seed.size(); i++){
            m_seed[i]->GetAmplitudeA(m_epbf[ne], m_deFTbf, 0, 0, kxy, Exyn);
            for(int j = 0; j < 4; j++){
                Exy[j] += Exyn[j];
            }
        }
        for(int j = 0; j < 4; j++){
            m_FwGridbf[j][np][ne][nq] = (float)(Exy[j]*scoef);
        }
    }
    if(m_epbf[ne] < m_epmin_fel){
        return;
    }

    double fwsum[2], tex, phase, dindex[2], cs, sn, bf[2], fw[2];
    dindex[0] = m_epbf[ne]/m_deFT;
    dindex[1] = m_qstore[np][nq]/m_dq[1];

    for(int j = 0; j < 2; j++){
        fwsum[0] = fwsum[1] = 0;
        tex = m_epbf[ne]/PLANKCC*m_qstore[np][nq];
        tex *= tex*0.5;
        tex *= hypotsq(
            cos(m_qgrid[0][np])*m_bmsize[0][nsec],
            sin(m_qgrid[0][np])*m_bmsize[1][nsec]);
        tex = exp(-tex);
        phase = -m_epbf[ne]/PLANKCC*(m_Zorg-m_Zmid[nsec])*m_qstore[np][nq]*m_qstore[np][nq]/2;
        phase += (m_torg-m_tmid[nsec])*m_epbf[ne]/(PLANCK/PI2);
        cs = cos(phase);
        sn = sin(phase);
        bf[0] = m_bunchf[nsec][0][ne]*cs-m_bunchf[nsec][1][ne]*sn;
        bf[1] = m_bunchf[nsec][1][ne]*cs+m_bunchf[nsec][0][ne]*sn;
        for(int i = 0; i < 2; i++){
            fw[i] = lininterp2d(m_FwGrid[2*j+i][np], dindex);
        }
        m_FwGridbf[2*j][np][ne][nq] += (float)((fw[0]*bf[0]-fw[1]*bf[1])*tex);
        m_FwGridbf[2*j+1][np][ne][nq] += (float)((fw[1]*bf[0]+fw[0]*bf[1])*tex);
    }
}

double FELAmplifier::f_GetPulseEnergyDens(int tgtsection, int np, bool debug)
{
    double Fsum = 0;
    double efcoef = GetTempCoef(true);

    vector<double> Fw[2], Ft[2];
    for(int i = 0; i < 2; i++){
        Fw[i].resize(m_nfdbf);
        Ft[i].resize(m_tgrid.size());
    }

    for(int ne = 0; ne < m_nfdbf; ne++){
        for(int nq = 0; nq <= m_nqlimbf[np][ne]; nq++){
            f_AddCA(tgtsection, np, ne, nq);
        }
    }

    if(np == 0){
        f_ClearEwFFTbf(1);
        for(int j = 0; j < 2; j++){
            for(int n = 0; n < m_nfdbf; n++){
                m_EwFFTbf[j][2*n] = m_FwGridbf[2*j][np][n][0];
                m_EwFFTbf[j][2*n+1] = m_FwGridbf[2*j+1][np][n][0];
            }
        }
#ifdef _DEBUG
        f_PrintSpectrum(FELSpecProfileFar, 2);
#endif
        f_InverseFFT(FELTempProfileFar, 2, true, m_tstep[tgtsection]-m_torg);
        for(int n = -m_hntgrid; n <= m_hntgrid; n++){
            int idx = fft_index(n, m_nfftbf, -1);
            for(int j = 0; j < 2; j++){
                m_eprof[tgtsection][j][n+m_hntgrid] = m_EwFFTbf[j][idx]*efcoef;
            }
        }
    }

    fill(Fw[0].begin(), Fw[0].end(), 0.0);
    fill(Ft[0].begin(), Ft[0].end(), 0.0);
    for(int nq = 1; nq < m_qstore[np].size(); nq++){
        double dtheta = m_qstore[np][nq]-m_qstore[np][nq-1];

        f_ClearEwFFTbf(1);
        for(int ne = 0; ne < m_nfdbf; ne++){
            for(int j = 0; j < 2; j++){
                if(nq <= m_nqlimbf[np][ne]){
                    m_EwFFTbf[j][2*ne] = m_FwGridbf[2*j][np][ne][nq];
                    m_EwFFTbf[j][2*ne+1] = m_FwGridbf[2*j+1][np][ne][nq];
                }
            }
            Fw[1][ne] =
                hypotsq(m_EwFFTbf[0][2*ne], m_EwFFTbf[0][2*ne+1])*m_qstore[np][nq]+
                hypotsq(m_EwFFTbf[1][2*ne], m_EwFFTbf[1][2*ne+1])*m_qstore[np][nq];
            double Fr = (Fw[0][ne]+Fw[1][ne])*dtheta*0.5;
            Fsum += Fr;
            m_spectra[tgtsection][ne] += Fr;
        }
        Fw[0] = Fw[1];
        f_InverseFFT(FELTempProfileFar, 2, false, m_tstep[tgtsection]-m_torg);
        for(int n = -m_hntgrid; n <= m_hntgrid; n++){
            int idx = fft_index(n, m_nfftbf, -1);
            Ft[1][n+m_hntgrid] =
                hypotsq(m_EwFFTbf[0][idx]*efcoef, m_EwFFTbf[1][idx]*efcoef)*m_qstore[np][nq];
            m_tprof[tgtsection][n+m_hntgrid] +=
                (Ft[0][n+m_hntgrid]+Ft[1][n+m_hntgrid])*dtheta*0.5;
        }
        Ft[0] = Ft[1];
    }

#ifdef _DEBUG
    if(!FELSprofileFar.empty() && m_grank == 0 && debug){
        vector<double> item(1+4*m_netgtbf.size());
        ofstream debug_out(FELSprofileFar);
        vector<string> titles(1+4*m_netgtbf.size());
        titles[0] = "theta(rad)";
        for(int n = 0; n < m_netgtbf.size(); n++){
            titles[4*n+1] = "Ex.re"+to_string(m_epbf[m_netgtbf[n]]);
            titles[4*n+2] = "Ex.im"+to_string(m_epbf[m_netgtbf[n]]);
            titles[4*n+3] = "Ey.re"+to_string(m_epbf[m_netgtbf[n]]);
            titles[4*n+4] = "Ey.im"+to_string(m_epbf[m_netgtbf[n]]);
        }
        PrintDebugItems(debug_out, titles);
        for(int nq = 0; nq < m_qstore[np].size(); nq++){
            item[0] = m_qstore[np][nq];
            for(int n = 0; n < m_netgtbf.size(); n++){
                for(int j = 0; j < 4; j++){
                    if(nq <= m_nqlimbf[np][m_netgtbf[n]]){
                        item[4*n+j+1] = m_FwGridbf[j][np][m_netgtbf[n]][nq];
                    }
                    else{
                        item[4*n+j+1] = 0;
                    }
                }
            }
            PrintDebugItems(debug_out, item);
        }
        debug_out.close();
    }
#endif

    return Fsum;
}

void FELAmplifier::f_GetPulseEnergy(int tgtsection)
{
    f_SetAmplitudeAng(tgtsection);

    fill(m_spectra[tgtsection].begin(), m_spectra[tgtsection].end(), 0);
    fill(m_tprof[tgtsection].begin(), m_tprof[tgtsection].end(), 0);

    double Fsum = 0;
    vector<int> steps, inistep, finstep;
    mpi_steps(m_nsq[0], 1, m_gprocesses, &steps, &inistep, &finstep);

    for(int np = 0; np < m_nsq[0]; np++){
        m_calcstatus->AdvanceStep(m_fellayer);
        if(np < inistep[m_grank] || np > finstep[m_grank]){
            continue;
        }
        Fsum += f_GetPulseEnergyDens(tgtsection, np, np == 0);
    }

    if(m_gprocesses > 1){
        MPI_Barrier(MPI_COMM_WORLD);
        double ftmp = Fsum;
        if(m_thread != nullptr){
            m_thread->Allreduce(&ftmp, &Fsum, 1, MPI_DOUBLE, MPI_SUM, m_grank);
        }
        else{
            MPI_Allreduce(&ftmp, &Fsum, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
        }
        for(int n = 0; n < m_nfdbf; n++){
            ftmp = m_spectra[tgtsection][n];
            if(m_thread != nullptr){
                m_thread->Allreduce(&ftmp, &m_spectra[tgtsection][n], 1, MPI_DOUBLE, MPI_SUM, m_grank);
            }
            else{
                MPI_Allreduce(&ftmp, &m_spectra[tgtsection][n], 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
            }
        }
        for(int n = -m_hntgrid; n <= m_hntgrid; n++){
            ftmp = m_tprof[tgtsection][n+m_hntgrid];
            if(m_thread != nullptr){
                m_thread->Allreduce(&ftmp, &m_tprof[tgtsection][n+m_hntgrid], 1, MPI_DOUBLE, MPI_SUM, m_grank);
            }
            else{
                MPI_Allreduce(&ftmp, &m_tprof[tgtsection][n+m_hntgrid], 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
            }
        }
    }

    double comc = m_dq[0]*COEF_ALPHA*m_bunchelectrons*m_bunchelectrons;
    Fsum *= m_deFTbf*comc*QE;
    m_pulseE[0][tgtsection] = Fsum*1000.0; // J -> mJ
    m_spectra[tgtsection] *= comc*0.001; // /100% -> /0.1%
    m_tprof[tgtsection] *= m_dq[0]/Z0VAC*0.001; // W -> kW

#ifdef _DEBUG
    if(!FELSpecProfile.empty() && m_grank == 0){
        ofstream debug_out(FELSpecProfile);
        vector<string> titles(2);
        vector<double> items(2);
        titles[0] = "energy(eV)";
        titles[1] = "Flux";
        PrintDebugItems(debug_out, titles);
        for(int n = 0; n < m_nfdbf; n++){
            items[0] = m_epbf[n];
            items[1] = m_spectra[tgtsection][n];
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif

    mpi_steps(1, m_Nparticles, m_gprocesses, &steps, &inistep, &finstep);
    double echange = 0;
    for(int n = 0; n < m_Nparticles; n++){
        if(n < inistep[m_grank] || n > finstep[m_grank]){
            continue;
        }
        if(m_charge[n] == 0){
            continue;
        }
        echange += m_charge[n]*m_particles[n]._tE[1];
    }
    if(m_gprocesses > 1){
        double etmp = echange;
        MPI_Barrier(MPI_COMM_WORLD);
        if(m_thread != nullptr){
            m_thread->Allreduce(&etmp, &echange, 1, MPI_DOUBLE, MPI_SUM, m_grank);
        }
        else{
            MPI_Allreduce(&etmp, &echange, 1, MPI_DOUBLE, MPI_SUM, MPI_COMM_WORLD);
        }
    }
    m_pulseE[1][tgtsection] = -echange/m_Nparticles*m_bunchE;
    m_pulseE[1][tgtsection] *= 1000; // J -> mJ
}

// functions to export data for debugging
void FELAmplifier::f_PrintAmpAdv(string filename, double *xyoffset)
{
    double xyr[2] = {0, 0};
    if(xyoffset != nullptr){
        xyr[0] = xyoffset[0];
        xyr[1] = xyoffset[1];
    }
    ofstream debug_out(filename);
    vector<string> titles(2+2*m_dim*m_netgt.size());
    vector<double> items(2+2*m_dim*m_netgt.size());
    titles[0] = "x(mm)";
    titles[1] = "y(mm)";
    for(int n = 0; n < m_netgt.size(); n++){
        titles[2*m_dim*n+2] = "Ex.re"+to_string(m_ep[m_netgt[n]]);
        titles[2*m_dim*n+3] = "Ex.im"+to_string(m_ep[m_netgt[n]]);
        titles[2*m_dim*n+4] = "Ey.re"+to_string(m_ep[m_netgt[n]]);
        titles[2*m_dim*n+5] = "Ey.im"+to_string(m_ep[m_netgt[n]]);
        if(m_dim == 3){
            titles[2*m_dim*n+6] = "Ez.re"+to_string(m_ep[m_netgt[n]]);
            titles[2*m_dim*n+7] = "Ez.im"+to_string(m_ep[m_netgt[n]]);
        }
    }
    PrintDebugItems(debug_out, titles);
    for(int nx = -m_nshalfm[0]; nx <= m_nshalfm[0]; nx++){
        items[0] = (xyr[0]+nx*m_dxyN[0])*1000;
//        for(int ny = 0; ny <= 0; ny++){
        for(int ny = -m_nshalfm[1]; ny <= m_nshalfm[1]; ny++){
            items[1] = (xyr[1]+ny*m_dxyN[1])*1000;
            int nxy = (nx+m_nshalfm[0])+(ny+m_nshalfm[1])*(2*m_nshalfm[0]+1);
            for(int n = 0; n < m_netgt.size(); n++){
                for(int j = 0; j < 2*m_dim; j++){
                    items[2+2*m_dim*n+j] = m_FxyCart[j][m_netgt[n]][nxy];
                }
            }
            PrintDebugItems(debug_out, items);
        }
    }
    debug_out.close();
}

void FELAmplifier::f_BcastFxyCart(vector<int> &inistep, vector<int> &finstep)
{
    int ntot = (2*m_nshalfm[0]+1)*(2*m_nshalfm[1]+1);
    for(int n = 0; n < m_nfd; n++){
        int currrank = get_mpi_rank(n, m_gprocesses, inistep, finstep);
        for(int j = 0; j < 2*m_dim; j++){
            for(int nxy = 0; nxy < ntot && m_grank == currrank; nxy++){
                m_wssp[nxy] = m_FxyCart[j][n][nxy];
            }
            if(m_thread != nullptr){
                m_thread->Bcast(m_wssp, ntot, MPI_DOUBLE, currrank, m_grank);
            }
            else{
                MPI_Bcast(m_wssp, ntot, MPI_DOUBLE, currrank, MPI_COMM_WORLD);
            }
            for(int nxy = 0; nxy < ntot; nxy++){
                m_FxyCart[j][n][nxy] = m_wssp[nxy];
            }
        }
        MPI_Barrier(MPI_COMM_WORLD);
    }
}

void FELAmplifier::f_ClearEwFFTbf(int jmax)
{
    for(int j = 0; j <= jmax; j++){
        for(int n = 0; n < m_nfftbf; n++){
            m_EwFFTbf[j][n] = 0;
        }
    }
}

void FELAmplifier::f_PrintTemp(
        string filename, double *xyoffset, bool iscenter, double tslip)
{
    ofstream debug_out(filename);
    vector<string> titles(m_dim+2);
    vector<double> items(m_dim+2);
    titles[0] = "time(fs)";
    titles[1] = "x(mm)";
    titles[2] = "Ex";
    titles[3] = "Ey";
    if(m_dim == 3){
        titles[4] = "Ez";
    }
    PrintDebugItems(debug_out, titles);
    int ny = m_nshalf[1], nxini, nxfin;

    if(m_bfreuse){
        ny = nxini = nxfin = 0;        
    }
    else if(iscenter){
        nxini = nxfin = m_nshalf[0];
    }
    else{
        nxini = 0;
        nxfin = 2*m_nshalf[0];
    }

    for(int nx = nxini; nx <= nxfin; nx++){
        if(m_bfreuse){
            items[1] = 0;
        }
        else{
            items[1] = 1000*m_xygrid[0][nx];
        }
        int ix = nx;
        if(xyoffset != nullptr){
            items[1] += xyoffset[0]*1000;
        }
        for(int n = -m_hntgrid; n <= m_hntgrid; n++){
            items[0] = m_tgrid[n+m_hntgrid]*1e15;
            items[0] -= tslip*1e+15;
            for(int j = 0; j < m_dim; j++){
                items[j+2] = m_EtGrid[ix][ny][j][n+m_hntgrid];
            }
            PrintDebugItems(debug_out, items);
        }
    }
    debug_out.close();
}

void FELAmplifier::f_PrintSpectrum(string filename, int dim)
{
    if(!filename.empty() && m_grank == 0){
        ofstream debug_out(filename);
        vector<string> titles(5);
        titles[0] = "energy(eV)";
        titles[1] = "Ex.re";
        titles[2] = "Ex.im";
        titles[3] = "Ey.re";
        titles[4] = "Ey.im";
        if(dim == 3){
            titles.push_back("Ez.re");
            titles.push_back("Ez.im");
        }
        vector<double> items(titles.size());
        PrintDebugItems(debug_out, titles);
        for(int n = 0; n < m_nfdbf; n++){
            items[0] = m_epbf[n];
            for(int j = 0; j < dim; j++){
                items[2*j+1] = m_EwFFTbf[j][2*n];
                items[2*j+2] = m_EwFFTbf[j][2*n+1];
            }
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
}

// class SeedLight
SeedLight::SeedLight(double pulseE,
    double epcenter, double pulselenFWHM, double srcsizeFWHM,
    double zwaist, double torg, double gdd, double tod)
{
    m_epcenter = epcenter;
    m_sigmat = pulselenFWHM/Sigma2FWHM;
    m_sigmath = m_sigmat/(PLANCK/PI2); // sigma_t/hbar
    m_sigmaxy = srcsizeFWHM/Sigma2FWHM;
    m_E0 = sqrt(2*pulseE*Z0VAC/m_sigmat)/pow(PI2, 0.75)/m_sigmaxy;

    m_Epk = m_E0*m_sigmat*m_sigmaxy*m_sigmaxy*4*pow(PI, 1.5);
    m_torg = torg;
    m_zwaist = zwaist;

    double planckfs = PLANCK*1e15/PI2;

    m_d2nd = gdd/planckfs/planckfs/2;
    m_d3rd = tod/planckfs/planckfs/planckfs/6;

    double kwave = wave_number(epcenter);
    m_zrayl = m_sigmaxy*2.0;
    m_zrayl *= m_zrayl*kwave/2.0;
    m_iscustom = false;
}

SeedLight::SeedLight(DataContainer &datacon, double pulseE, double srcsizeFWHM, double zwaist, double torg)
{
    m_sigmaxy = srcsizeFWHM/Sigma2FWHM;
    m_torg = torg;
    m_zwaist = zwaist;

    vector<double> ep, Eamp;
    vector<vector<double>> flux(2);
    datacon.GetVariable(0, &ep);
    for(int j = 0; j < 2; j++){
        datacon.GetArray1D(j+1, &flux[j]);
    }
    int ndata = datacon.GetSize();
    for(int n = 0; n < ndata; n++){
        ep[n] = photon_energy(ep[n]*1e-9);
    }

    if(ep[0] > ep[1]){
        sort(ep, flux, ndata, true);
    }
    m_seedrange[0] = ep[0];
    m_seedrange[1] = ep[ndata-1];

    m_seedspec[0].SetSpline(ndata, &ep, &flux[0]);
    double total = m_seedspec[0].Integrate()/(PLANCK/PI2);
    m_E0custom = 0;
    if(total > 0){
        m_E0custom = sqrt(Z0VAC*pulseE/2/total)/m_sigmaxy;
    }
    Eamp.resize(ndata, 0.0);
    for(int j = 0; j < 2; j++){
        for(int n = 0; n < ndata; n++){
            if(flux[0][n] > 0){
                double phi = flux[1][n]*DEGREE2RADIAN;
                Eamp[n] = sqrt(flux[0][n])*cos(phi-PId2*j);
            }
            else{
                Eamp[n] = 0;
            }
        }
        m_seedspec[j].SetSpline(ndata, &ep, &Eamp);
        m_seedspec[j].Integrate(&Eamp);
        m_seedspec[j].SetSpline(ndata, &ep, &Eamp);
    }
    m_iscustom = true;

#ifdef _DEBUG
    if(!SeedCustomIntSpec.empty()){
        for(int j = 0; j < 2; j++){
            m_seedspec[j].GetArrays(&ep, &flux[j]);
        }
        ofstream debug_out(SeedCustomIntSpec);
        vector<string> titles {"Energy", "Re", "Im"};
        PrintDebugItems(debug_out, titles);
        vector<double> items(titles.size());
        for(int n = 0; n < ndata; n++){
            items[0] = ep[n];
            items[1] = flux[0][n];
            items[2] = flux[1][n];
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif

}

void SeedLight::GetAmplitudeS(
    double ep, double de, double tshift, double zpos, double xy[], double Exy[])
{
    for(int j = 0; j < 4; j++){
        Exy[j] = 0;
    }
    if(ep <= 0){
        return;
    }
    double kwave = wave_number(ep);
    double zrayl = m_sigmaxy*2.0;
    zrayl *= zrayl*kwave/2.0;
    double r2 = hypotsq(xy[0], xy[1]);
    zpos -= m_zwaist;
    double src2 = hypotsq(1, zpos/zrayl);
    double phase = -atan2(zpos, zrayl)+(tshift+m_torg)*CC*kwave;
    if(fabs(zpos) > 0){
        phase += r2*kwave/zpos/hypotsq(1, zrayl/zpos)/2;
    }

    double tex = r2/(2*m_sigmaxy)/(2*m_sigmaxy)/src2, zero = 0;
    if(tex > MAXIMUM_EXPONENT){
        return;
    }
    phase += f_GetPhase(ep); // add chirp
    if(m_iscustom){
        if(ep < m_seedrange[0] || ep > m_seedrange[1]){
            Exy[0] = Exy[1] = 0;
        }
        else{
            double csn[2], exy[2];
            for(int j = 0; j < 2; j++){
                csn[j] = cos(phase-PId2*j)*exp(-tex)/sqrt(src2);
                exy[j] = m_E0custom*(
                    m_seedspec[j].GetValue(ep+de/2, true, nullptr, &zero)-
                    m_seedspec[j].GetValue(ep-de/2, true, nullptr, &zero)
                    )/de;
            }
            Exy[0] = exy[0]*csn[0]-exy[1]*csn[1];
            Exy[1] = exy[0]*csn[1]+exy[1]*csn[0];
        }
    }
    else{
        double eamp = m_E0*SQRTPI*m_sigmat/sqrt(src2)*f_GetAmp(ep, de, tex);
        Exy[0] = eamp*cos(phase);
        Exy[1] = eamp*sin(phase);
    }
}

void SeedLight::GetAmplitudeA(double ep, double de,
    double tshift, double zpos, double kxy[], double Exy[])
{
    Exy[2] = Exy[3] = 0; 
    if(ep <= 0){
        Exy[0] = Exy[1] = 0;
        return;
    }
    double kwave = wave_number(ep);
    double tex = hypotsq(kxy[0]*m_sigmaxy, kxy[1]*m_sigmaxy);
    Exy[1] = 0; // imaginary = 0; waist position
    if(tex > MAXIMUM_EXPONENT){
        Exy[0] = 0;
        return;
    }

    double phase = (tshift+m_torg)*CC*kwave, zero = 0.0;
    phase -= (zpos-m_zwaist)/kwave*hypotsq(kxy[0], kxy[1])/2.0;
    phase += f_GetPhase(ep); // add chirp
    if(m_iscustom){
        if(ep < m_seedrange[0] || ep > m_seedrange[1]){
            Exy[0] = Exy[1] = 0;
        }
        else{
            double csn[2], exy[2];
            for(int j = 0; j < 2; j++){
                csn[j] = cos(phase-PId2*j)*exp(-tex);
                exy[j] = 2*PI2*m_sigmaxy*m_sigmaxy*m_E0custom*(
                    m_seedspec[j].GetValue(ep+de/2, true, nullptr, &zero)-
                    m_seedspec[j].GetValue(ep-de/2, true, nullptr, &zero)
                    )/de;
            }
            Exy[0] = exy[0]*csn[0]-exy[1]*csn[1];
            Exy[1] = exy[0]*csn[1]+exy[1]*csn[0];
        }
    }
    else{
        double eamp = f_GetAmp(ep, de, tex);
        Exy[0] = m_Epk*eamp*cos(phase);
        Exy[1] = m_Epk*eamp*sin(phase);
    }
}

double SeedLight::GetDivergence()
{
    return wave_length(m_epcenter)/2/PI2/m_sigmaxy;
}

double SeedLight::f_GetPhase(double ep)
{
    double de = ep-m_epcenter;
    return de*de*(m_d2nd+de*m_d3rd);
}

double SeedLight::f_GetAmp(double ep, double de, double tex)
{
    double dOmega = de*m_sigmath;
    double Omega;
    double eamp = 0;
    for(int i = -1; i <= 1; i += 2){
        Omega = (ep+i*m_epcenter)*m_sigmath;
        eamp += erf(Omega+dOmega/2)-erf(Omega-dOmega/2);
    }
    return SQRTPI/2/dOmega*eamp*exp(-tex);
}