#ifndef trajectory_h
#define trajectory_h

#include "interpolation.h"
#include "orbit_components_operation.h"
#include "spectra_solver.h"

#define ALLOC_ERROR_CANNOT_OPEN_FILE -0x001L
#define ALLOC_ERROR_MESH_INVALID -0x003L
#define ALLOC_ERROR_DATA_NOT_FOUND -0x007L
#define TOO_FEW_DATA_POINTS -0x004L
#define ALLOC_ERROR_NO_FIELD_TABLE -0x005L
#define PERIOD_LATTICE_MATCHING -0x006L

enum {
	FieldMapStatusDataAllocated = 1,
	FieldMapStatusDataArranged,
	FieldMapStatusCenterAdjusted,

	FieldMapSinusoidal = 0,
	FieldMapOnAxis,
	FieldMap3Axes,
	FieldMapRectMag,
    FieldMapFail = -1
};

class DataContainer;
class Particle;

class Trajectory
    : public SpectraSolver
{
public:
    Trajectory(SpectraSolver &spsolver, bool isforce = false);
    virtual ~Trajectory(){}
    void AdjustBeamInitialCondition();
    void AllocateTrajectory(
        bool isps, bool killfocus, bool isinjcorr, OrbitComponents *orbit = nullptr);
    void GetField(int index, bool isps, bool killfocus, double xy[], double rBxyz[]);
    void Get2dField(int iseg, bool issec, double *xyz, double *Bxyz);
    bool TransferTwissParamaters(double *alpha, double *beta, 
        vector<vector<double>> *betaarr, vector<vector<double>> *alphaarr = nullptr, 
        vector<double> *CS = nullptr);
    void GetXYtildeBetasxyAt(int n, Particle *particle, double *XYtilde, 
        double *betasxy, int type = 0);
    double GetPhaseError(vector<double> &zpeak, 
        vector<double> &phase, double beps, vector<vector<double>> &rho);
    void GetBetaPhaseAdvance(double phase[]);

    void AllocateProjectedXPosision();
    void GetTrajectory(vector<OrbitComponents> *orbit);
    void GetTrajectory(vector<double> &z, vector<vector<double>> *B, 
        vector<vector<double>> *beta, vector<vector<double>> *xy, vector<double> *rz = nullptr);
    void GetOrbitComponentIndex(int index, OrbitComponents *orbit);
    int GetOrbitPoints();
    void GetZCoordinate(vector<double> *zorbit);
    int GetDataArrangementStatus();

    bool f_GetLocalWigglerRad(int nfd, vector<double> &ep, 
        int nzp[], double XYZo[], vector<vector<double>> &fd, double *zemission);
    void GetStokesWigglerApprox2D(double *XYZ, int nfd, 
        vector<double> &ep, vector<vector<double>> &fd);
    vector<double> m_xyprj[2];
    vector<double> m_csn[2];

    string GetErroCode();
	int GetOriginIndex(){return m_nzorgorbit;}
    void GetOriginXY(double xy[]);
    int GetZsection(vector<vector<int>> &secidx);
    void GetAvgOrbits(vector<OrbitComponents> &orb);
    void SetReference(){m_reforbit = m_orbit;}
    void AdvancePhaseSpace(int iniindex, vector<double> &tarr,
        vector<vector<double>> *Exy, Particle &particle, double *Fz, double Ej[]);

private:
	void f_AssignErrorField();
    void f_ArrangeFieldComponent();
    double f_GetPhaseAdvances(vector<vector<double>> &Drz, bool settgt);
    void f_AllocatePhaseCorrection();
    int f_AllocateData(DataContainer *zvsbxy);
    void f_FinerStep();
    int f_AllocateData(string input3dfile);
    void f_AdvanceOrbit(int iniindex, bool isps, bool killfocus, double cE, int step, double xyzin[],
        double acc[], double Bexit[], double xyzout[]);
    double f_AdditionalPhase(double zz, vector<vector<double>> &Drz);
    double f_PhaseShifterField(double zz, vector<vector<double>> &Bpkps);
    bool f_GetMatchingF(int jxy, int m, double z1, double z2, double *finv,
        double *beta0 = nullptr, double *alpha0 = nullptr);
    double f_GetSegmentOrigin(int m);
    void f_CopyOrbitComponents(vector<vector<double>> *xyarr);
	double f_GetBfield(double z, double zorgbm, double bmlength, double B, bool rect);
    void f_GetRecovFactor(double lu, int N, int nh, double *sigw, double *sigxy);

    double m_zorg_BM;
    double m_Lmatch;
    vector<vector<double>> m_I1err;
    vector<vector<double>> m_bkick;

    int m_status;
    int m_nxyz[3];

    int m_nzorg;
    int m_nzorgorbit;
    vector<double> m_zz;
    vector<double> m_xyarray[3];
    vector<double> m_B[3];

	double m_z0thpole[3];
	double m_betaorg[2];
    double m_alphaorg[2];

    vector<vector<double>> m_Bxy[2];
    vector<vector<double>> m_Bz[2];
    vector<vector<vector<double>>> m_Bxyz[3];
	double m_valrange[3];

    vector<Spline> m_SplineBxy[2];
    vector<Spline> m_SplineBz[2];

    vector<double> m_Bps;
    vector<double> m_Drz[2];
    vector<double> m_Trz[2];
    vector<double> m_Bpkps[2];
    vector<double> m_zmid[2];

    // periodic lattice parameters
    vector<double> m_finvmatch[2];

    vector<double> m_C[2];
    vector<double> m_S[2];
    vector<double> m_Cd[2];
    vector<double> m_Sd[2];

    vector<double> m_CU[2];
    vector<double> m_SU[2];
    vector<double> m_CUd[2];
    vector<double> m_SUd[2];

    vector<double> m_CD[2];
    vector<double> m_SD[2];
    vector<double> m_CDd[2];
    vector<double> m_SDd[2];

    // radiation field section index
    vector<vector<int>> m_secindex;
    vector<vector<int>> m_bfsects;
    vector<double> m_seczpos;

    vector<int> m_custsegtype;
    vector<double> m_custsegphi;
    vector<int> m_custsegNdif;

    bool m_killtaper;

protected:
	OrbitComponents m_offset;
    int m_ntotorbit;
    double m_injangle[2];
    double m_dxyz[3];
    double m_eps_wig;
    vector<double> m_zorbit;
    vector<double> m_prjd;
    vector<double> m_prjlen;
    vector<OrbitComponents> m_orbit;
    vector<OrbitComponents> m_reforbit;
};

#endif

