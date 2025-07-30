#include <algorithm>
#include <random>
#include <sstream>
#include "trajectory.h"
#include "common.h"
#include "fast_fourier_transform.h"
#include "bm_wiggler_radiation.h"
#include "bessel.h"
#include "undulator_data_manipulation.h"
#include "randomutil.h"
#include "particle_generator.h"

//---------------------------
// files for debugging
string TrajectoryData;
string CustomPeriodicData;
string CustomArrangeFoc;
string CustomArrangeFocA;
string CustomArrangeFocXY;
string CustomArrangeFocZ;
string CustomArrangeFocXYZ;
string TwissPrmData;
string PhaseCorrRz;
string PhaseCorrDrz;
string PhaseCorrAdd;
string PhaseErrProfile;
string XYPrjData;
string WiggApproxSum;

#define ADJ_INJ_MAXTRIALS 10

//------------------------------------------------------------------------------
Trajectory::Trajectory(SpectraSolver &spsolver, bool isforce)
    : SpectraSolver(spsolver)
{  
#ifdef _DEBUG
TrajectoryData = "..\\debug\\trajectory.dat";
//PhaseCorrAdd = "..\\debug\\delta_phase_alongz.dat";
//CustomPeriodicData = "..\\debug\\custom_periodic.dat";
//CustomArrangeFoc = "..\\debug\\custom_arr_focus.dat";
//CustomArrangeFocA = "..\\debug\\custom_arr_focus_aft.dat";
//CustomArrangeFocXY = "..\\debug\\custom_arr_focus_xy.dat";
//CustomArrangeFocZ = "..\\debug\\custom_arr_focus_z.dat";
//CustomArrangeFocXYZ = "..\\debug\\custom_arr_focus_data.dat";
//TwissPrmData = "..\\debug\\twiss_prms.dat";
//PhaseCorrRz = "..\\debug\\rz_alongz.dat";
//PhaseCorrDrz = "..\\debug\\delta_rz_segment.dat";
PhaseErrProfile = "..\\debug\\phase_error.dat";
//XYPrjData = "..\\debug\\xy_projection.dat";
//WiggApproxSum = "..\\debug\\wig_approx.dat";
#endif

    m_eps_wig = 1e-4/(1<<(m_accuracy[acclimtra_]-1));

    if(isforce){
        m_isfar = false;
    }
    if(m_isfar){
        m_status = FieldMapStatusDataArranged;
        return;
    }

	if(m_iscoherent){
        m_zorg_BM = m_src[csrorg_];
	}
    else{
		m_zorg_BM = 0;
    }
    if(m_srcb[phaseerr_] && m_isdefault){
        f_AssignErrorField();
    }
	f_ArrangeFieldComponent();
	if(m_status < 0){
        string err = "Failed to arrange the light source: "+GetErroCode();
        throw runtime_error(err.c_str());
        return;
    }

    double L = m_zorbit[m_ntotorbit-1]-m_zorbit[0];
    if(m_isfel){
        m_secindex.resize(2);
        if(m_seczpos.size() > 0){
            m_secindex[0].push_back(0);
            for(int n = 1; n < m_seczpos.size(); n++){
                int index = get_index4lagrange(m_zorbit[0]+m_seczpos[n], m_zorbit, m_ntotorbit);
                for(int j = 0; j < 2; j++){
                    m_secindex[j].push_back(index);
                }
            }
            m_secindex[1].push_back(m_ntotorbit-1);
        }
        else{
            m_secindex[0].push_back(0);
            double ztgt;
            if(m_confv[svstep_][0] > m_zorbit[0]){
                ztgt = m_confv[svstep_][0]-m_confv[svstep_][1];
            }
            else{
                ztgt = m_zorbit[0];

            }
            double lregmin = 1e-3; // lower limit for the section length
            int index = 0;
            while(1){
                ztgt += m_confv[svstep_][1];
                if(ztgt >= m_zorbit.back()-lregmin){
                    break;
                }
                index = get_index4lagrange(ztgt, m_zorbit, m_ntotorbit);
                for(int j = 0; j < 2; j++){
                    m_secindex[j].push_back(index);
                }
            }
            m_secindex[1].push_back(m_ntotorbit-1);
            int nsec = (int)m_secindex[1].size();
            if(nsec > 2){
                double Lfin = m_zorbit[m_secindex[1][nsec-1]]-m_zorbit[m_secindex[1][nsec-2]];
                if(Lfin < m_confv[svstep_][1]/4){
                    // combine the last two steps
                    m_secindex[0].erase(m_secindex[0].end()-1);
                    m_secindex[1].erase(m_secindex[1].end()-2);
                }
            }
        }
    }
    else if(m_is3dsrc){
        int nsections, index;
        if(m_srcsel[natfocus_] != NoneLabel || m_srctype == FIELDMAP3D){
            double betaphase[2]; 
            double nr = 0;
            GetBetaPhaseAdvance(betaphase);
            for (int j = 0; j < 2; j++){
                double stdphase = 2.0*atan(L/2.0/m_accv[beta_][j]);
                nr = max(nr, betaphase[j]/stdphase);
            }
            nsections = max(1, (int)floor(nr+0.5)*(1<<m_accuracy[accdisctra_])-1);
        }
        else{
            nsections = 1;
        }
        m_secindex.resize(2);
        if(m_issegu){
            nsections = (int)ceil((nsections-1)/m_M)+1;
            double segrange[2];
            for(int m = 0; m < m_LatticeZ.size()-1; m++){
                segrange[0] = max(m_zorbit[0], m_LatticeZ[m]+m_Ldrift*0.5);
                segrange[1] = min(m_zorbit[m_ntotorbit-1], m_LatticeZ[m+1]-m_Ldrift*0.5);
                double dL = (segrange[1]-segrange[0])/nsections;
                index = SearchIndex(m_ntotorbit, true, m_zorbit, segrange[0]);
                m_secindex[0].push_back(index);
                for (int n = 1; n < nsections; n++){
                    index = SearchIndex(m_ntotorbit, true, m_zorbit, segrange[0]+n*dL);
                    m_secindex[0].push_back(index);
                    m_secindex[1].push_back(index);
                }
                index = SearchIndex(m_ntotorbit, true, m_zorbit, segrange[1]);
                m_secindex[1].push_back(index);
            }
        }
        else{
            m_secindex[0].push_back(0);
            double dL = L/nsections;
            for(int n = 1; n < nsections; n++){
                double zs = m_zorbit[0]+n*dL;
                index = SearchIndex(m_ntotorbit, true, m_zorbit, zs);
                m_secindex[0].push_back(index);
                m_secindex[1].push_back(index);
            }
            m_secindex[1].push_back(m_ntotorbit-1);
        }
    }
    else{
        m_secindex.resize(0);
    }

	AdjustBeamInitialCondition();
    
    m_killtaper = true; // kill tapering for phase shifter tuning
    f_AllocatePhaseCorrection();
    m_killtaper = false;

#ifdef _DEBUG
	if(!PhaseCorrAdd.empty()){
		ofstream debug_out(PhaseCorrAdd);
		if(debug_out){
			PrintDebugPair(debug_out, m_zz, m_Bps, m_nxyz[2]);
		}
	}
#endif

    AllocateTrajectory(true, false, true);
}

void Trajectory::AdjustBeamInitialCondition()
{
    vector<double> xy(m_ntotorbit);
    vector<double> xyint(m_ntotorbit);
    Spline xyspline;
    long n;
    double zrange[2], dz, xymax[4], xyfix[4] = {0,0,0,0};
    int j, irep = 0;
    bool isfinish;
    double xyeps = 1.0e-6;
    double betaeps = 1.0e-6;

	if(m_accsel[injectionebm_] ==  EntranceLabel){
        m_offset.Clear();
        return;
    }
	else if(m_accsel[injectionebm_] == CustomLabel){
        for(int j = 0; j < 2; j++){
            m_offset._xy[j] = m_accv[xy_][j]*0.001; // mm -> m
            m_offset._beta[j] = m_accv[xyp_][j]*0.001; // mrad -> rad
        }
        return;
    }

	if(m_accsel[injectionebm_] == CenterLabel || 
        (m_accsel[injectionebm_] == AutomaticLabel && m_srctype == BM)){
        zrange[0] = zrange[1] = 0.0;
    }
    else if(m_accsel[injectionebm_] == ExitLabel){
        zrange[0] = zrange[1] = m_zorbit[m_ntotorbit-1];
    }
    else{
        zrange[0] = m_zorbit[0];
        zrange[1] = m_zorbit[m_ntotorbit-1];
    }
    dz = zrange[1]-zrange[0];

    do{
        isfinish = true;
        AllocateTrajectory(false, false, false, &m_offset);
        for(j = 0; j < 4; j++){
            if(j == 2){
                m_offset._beta[0] -= xyfix[0];
                m_offset._beta[1] -= xyfix[1];
                AllocateTrajectory(false, false, false, &m_offset);
            }
			xymax[j] = 0;
            for(n = 0; n < m_ntotorbit; n++){
                if(j < 2){
                    xy[n] = m_orbit[n]._beta[j];
                }
                else{
                    xy[n] = m_orbit[n]._xy[j-2];
                }
				xymax[j] = max(xymax[j], fabs(xy[n]));
            }
            xyspline.SetSpline(m_ntotorbit, &m_zorbit, &xy);
            if(dz < 1.0e-6){
                xyfix[j] = xyspline.GetValue((zrange[1]+zrange[0])*0.5);
            }
            else{
                xyspline.Integrate(&xyint);
                xyspline.SetSpline(m_ntotorbit, &m_zorbit, &xyint);
                xyfix[j] = (xyspline.GetValue(zrange[1])-xyspline.GetValue(zrange[0]))/dz;
            }
            if(j < 2){
                isfinish = isfinish && (fabs(xyfix[j]) < betaeps);
            }
            else{
                isfinish = isfinish && (fabs(xyfix[j]) < xyeps);
            }
        }
        m_offset._xy[0] -= xyfix[2];
        m_offset._xy[1] -= xyfix[3];
    } while(++irep < ADJ_INJ_MAXTRIALS && !isfinish);
}

void Trajectory::AllocateTrajectory(
    bool isps, bool killfocus, bool isinjcorr, OrbitComponents *orbit)
{
    int j, n, nz;
    double xy[5], B[3], acc[5], cE, betaxy[2], rxy[2], rz, rzorg = 0;
    OrbitComponents init;

    if(m_isfar) return;

    if(orbit != nullptr){
        cE = CC/m_acc[eGeV_]/(orbit->_tsqrt)/1.0e+9;
    }
    else{
        cE = CC/m_acc[eGeV_]/1.0e+9;
    }

	if(orbit != nullptr){
        init.SetComponents(orbit);
    }
	if(isinjcorr){
        for (int j = 0; j < 2; j++){
            init._beta[j] += m_offset._beta[j];
            init._xy[j] += m_offset._xy[j];
        }
	}

    for(int j = 0; j < 2; j++){
        betaxy[j] = xy[j] = init._beta[j];
        rxy[j] = xy[j+2] = init._xy[j];
    }

    rz = xy[4] = 0.0;
    nz = -1;
    for(n = 0; n < m_nxyz[2]; n += 2){
        nz++;
        if(!killfocus && (m_issegu && m_srcb[perlattice_])){
            xy[0] += xy[2]*m_finvmatch[0][nz];
            xy[1] += xy[3]*m_finvmatch[1][nz];
        }
        if(n == 0){
            GetField(n, isps, killfocus, xy, B);
            get_EMF_variables(cE, xy, B, acc);
        }
        else{
            f_AdvanceOrbit(n-2, isps, killfocus, cE, 1, xy, acc, B, xy);
        }
        for(j = 0; j < 2; j++){
            betaxy[j] = xy[j]; rxy[j] = xy[j+2];
        }
        rz = xy[4];
		if(nz == m_nzorgorbit){
			rzorg = rz;
		}

        m_orbit[nz].SetComponents(acc, betaxy, rxy, rz);
        m_B[0][nz] = B[0]; m_B[1][nz] = B[1]; m_B[2][nz] = B[2];
        if(nz == m_ntotorbit-1){
            break;
        }
    }

    for(nz = 0; nz < m_ntotorbit; nz++){
		m_orbit[nz]._rz -= rzorg;
        if (orbit != nullptr){
            m_orbit[nz]._tsqrt = orbit->_tsqrt;
        }
	}

#ifdef _DEBUG
	if(!TrajectoryData.empty()){
		ofstream debug_out(TrajectoryData);
        vector<string> titles {"z", "acc.x", "acc.y", "beta.x", "beta.y", "x", "y", "rz"};
        PrintDebugItems(debug_out, titles);
        if(debug_out){
			vector<double> tmp(7);
            for (nz = 0; nz < m_ntotorbit; nz++){
                for(int j = 0; j < 2; j++){
                    tmp[j] = m_orbit[nz]._acc[j];
                    tmp[j+2] = m_orbit[nz]._beta[j];
                    tmp[j+4] = m_orbit[nz]._xy[j];
                }
                tmp[6] = m_orbit[nz]._rz;
				PrintDebugItems(debug_out, m_zorbit[nz], tmp);
			}
		}
        debug_out.close();
	}
#endif
}

void Trajectory::GetField(int index, bool isps, bool killfocus, double xy[], double rBxyz[])
{
    int j, m;
    double frac, xyz[3];
    double bxyz1[3], bxyz2[] = {0.0, 0.0, 0.0};

    if(killfocus){
        xyz[0] = xyz[1] = 0.0;
    }
    else{
        xyz[0] = xy[2]; xyz[1] = xy[3];
    }
    xyz[2] = m_zz[index];

    for(j = 0; j < 3; j++){
        rBxyz[j] = 0.0;
    }
    if(isps){
        rBxyz[1] = m_Bps[index];
    }
    if(m_isdefault){
        for(m = 1; m <= m_M; m++){
            Get2dField(m, false, xyz, bxyz1);
            if(m_issrc2){
                Get2dField(m, true, xyz, bxyz2);
            }
            for(j = 0; j < 3; j++){
                rBxyz[j] += bxyz1[j]+bxyz2[j];
            }
        }
    }
    else if(m_ismapaxis){
        for(j = 0; j < 2; j++){
            if(m_nxyz[j] < 2){
                rBxyz[j] = m_Bxy[j][index][0];
                rBxyz[2] += m_Bz[j][index][0];
            }
            else{
                rBxyz[j] = m_SplineBxy[j][index].GetValue(xyz[j]);
                rBxyz[2] += m_SplineBz[j][index].GetValue(xyz[j]);
            }
        }
    }
    else if(m_ismap3d){
		int xyidx[2];
		double dresxy[4];
		bool isinrange = get_2d_matrix_indices(xyz, m_valrange, nullptr, m_dxyz, m_nxyz, xyidx, dresxy);
        for(j = 0; j < 3; j++){
			if(isinrange){
	            rBxyz[j] = m_Bxyz[j][xyidx[0]  ][xyidx[1]  ][index]*dresxy[0]
						 + m_Bxyz[j][xyidx[0]+1][xyidx[1]  ][index]*dresxy[1]
						 + m_Bxyz[j][xyidx[0]  ][xyidx[1]+1][index]*dresxy[2]
						 + m_Bxyz[j][xyidx[0]+1][xyidx[1]+1][index]*dresxy[3];
			}
			else{
				rBxyz[j] = 0;
			}
        }
    }
    else if(m_iswshifter){
        rBxyz[1] = f_GetBfield(m_zz[index], m_zorg_BM, m_src[mplength_], m_src[bmain_], m_isbm);
        rBxyz[1] += f_GetBfield(m_zz[index],
            m_zorg_BM-(m_src[mplength_]+m_src[subpolel_])*0.5, m_src[subpolel_], -m_src[subpoleb_], false);
        rBxyz[1] += f_GetBfield(m_zz[index],
            m_zorg_BM+(m_src[mplength_]+m_src[subpolel_])*0.5, m_src[subpolel_], -m_src[subpoleb_], false);
    }
    else if(m_isbm){
		if(m_srcb[bmtandem_]){
			rBxyz[1] = f_GetBfield(m_zz[index], m_zorg_BM-m_src[bminterv_]*0.5, m_src[bendlength_], m_Bmax, true);
			rBxyz[1] += f_GetBfield(m_zz[index], m_zorg_BM+m_src[bminterv_]*0.5, m_src[bendlength_], m_Bmax, true);
		}
		else{
			rBxyz[1] = f_GetBfield(m_zz[index], m_zorg_BM, m_src[bendlength_], m_Bmax, m_isbm);
		}
    }

    if(m_srcb[fielderr_] && !m_isdefault){
        // m_isdefault = true: field error already included in Get2dField()
        for (j = 0; j < 2; j++){
            frac = 1.0+m_zz[index]*m_srcv[ltaper_][j]+m_zz[index]*m_zz[index]*m_srcv[qtaper_][j];
            rBxyz[j] = rBxyz[j]*frac+m_srcv[boffset_][j];
        }
    }
}

void Trajectory::Get2dField(int iseg, bool issec, double *xyz, double *Bxyz)
{
    double ftapers[2] = {1.0, 1.0}, bdev[2] = {0.0, 0.0};
    double zorg = issec ? m_zorgS[iseg] : m_zorg[iseg];
    vector<double> *deltaxy = issec ? m_deltaxyS : m_deltaxy;
    vector<double> *Kxy = issec ? m_KxyS : m_Kxy;
    Bxyz[0] = Bxyz[1] = Bxyz[2] = 0.0;

    int N = m_N+2*ENDPERIODS; // half + end magnets, amplitude adjusted by m_isendcorr
    double dz = xyz[2]-zorg;

    if(m_M > 1){
        int sidx = iseg;
        int M = m_M;
        if(m_issrc2){
            M *= 2;
            sidx = 2*iseg-1;
            if(issec){
                sidx = 2*iseg;
            }
        }
        double segorg = (M+1)*0.5;
        dz += (sidx-segorg)*m_N*m_lu;
    }

    for (int j = 0; j < 2; j++){
        if(m_srcb[fielderr_] && !m_killtaper){
            ftapers[j] += m_srcv[ltaper_][j]*dz+m_srcv[qtaper_][j]*dz*dz;
        }
        if(!m_issegu && m_srcb[phaseerr_]){
            int polen = UndulatorFieldData::GetPoleNumber(xyz[2], m_z0thpole[j], m_lu);
            if (polen >= 0 && polen < m_I1err[j].size()){
                ftapers[j] += m_I1err[j][polen];
                bdev[j] = m_bkick[j][polen];
            }
        }
    }
    get_id_field_general(zorg, N, m_lu, Kxy, deltaxy, ftapers, bdev,
        m_isnatfoc, m_issymmetric, m_srcb[endmag_], xyz, Bxyz);

    if(m_srcb[fielderr_]){
        for (int j = 0; j < 2; j++){
            Bxyz[j] += m_srcv[boffset_][j];
        }
    }
}

bool Trajectory::TransferTwissParamaters(double *alpha, double *beta, 
    vector<vector<double>> *betaarr, vector<vector<double>> *alphaarr,
    vector<double> *CS)
{
    OrbitComponents offset;
    double gamma0, betar, alphac, betac, alphar;
    vector<vector<double>> xyarr(4), xyorg(4);
    vector<double> C[2], Cd[2], S[2], Sd[2];
    vector<vector<double>> CStmp(3), CSinv(3), CSn(3);
    bool isinionly = betaarr == nullptr;

    for(int j = 0; j < 3; j++){
        CStmp[j].resize(3, 0.0);
        CSinv[j].resize(3, 0.0);
        CSn[j].resize(3, 0.0);
    }
    CStmp[2][2] = 1.0;

    for(int j = 0; j < 4; j++){
        xyarr[j].resize(m_ntotorbit);
        xyorg[j].resize(m_ntotorbit);
    }
    for(int j = 0; j < 2; j++){
        C[j].resize(m_ntotorbit);
        Cd[j].resize(m_ntotorbit);
        S[j].resize(m_ntotorbit);
        Sd[j].resize(m_ntotorbit);
        if(!isinionly){
            if((*betaarr)[j].size() < m_ntotorbit){
                (*betaarr)[j].resize(m_ntotorbit);
            }
        }
        if(alphaarr != nullptr){
            if((*alphaarr)[j].size() < m_ntotorbit){
                (*alphaarr)[j].resize(m_ntotorbit);
            }
        }
    }

    int nfin = isinionly ? 0 : m_ntotorbit-1;
    double unit;
    for(int j = -1; j < 4; j++){
        offset.Clear();
        if(j == -1){
            // do nothing
        }
        else if(j < 2){
            unit = offset._beta[j] = m_div[j];
        }
        else{
            unit = offset._xy[j-2] = m_size[j-2];
        }
        AllocateTrajectory(false, false, true, &offset);
        if(j == -1){
            f_CopyOrbitComponents(&xyorg);
            continue;
        }
        else{
            f_CopyOrbitComponents(&xyarr);
        }

        for(int n = 0; n < m_ntotorbit; n++){
            for(int i = 0; i < 4; i++){
                xyarr[i][n] -= xyorg[i][n];
            }
            if(j < 2){
                S[j][n] = xyarr[j+2][n]/unit; Sd[j][n] = xyarr[j][n]/unit;
            }
            else {
                C[j-2][n] = xyarr[j][n]/unit; Cd[j-2][n] = xyarr[j-2][n]/unit;
            }
        }
    }
    // restore reference orbit (default setting for phase, focus, injection)
    AllocateTrajectory(true, false, true);

    for(int j = 0; j < 2; j++){
        int n = m_nzorgorbit;
        csd_matrix(C[j][n], Cd[j][n], S[j][n], Sd[j][n], 0.0, 0.0, CStmp);
        if(!inverse_matrix(CStmp, CSinv)){
            return false;
        }
        if(CS != nullptr){
            CS[j].resize(4);
            for(int i = 0; i < 2; i++){
                CS[j][2*i] = CSinv[i][0];
                CS[j][2*i+1] = CSinv[i][1];
            }
        }
        for(n = 0; n <= nfin; n++){
            csd_matrix(C[j][n], Cd[j][n], S[j][n], Sd[j][n], 0.0, 0.0, CStmp);
            multiply_matrices(CStmp, CSinv, CSn);
            C[j][n] = CSn[0][0];
            S[j][n] = CSn[0][1];
            Cd[j][n] = CSn[1][0];
            Sd[j][n] = CSn[1][1];
        }
        if(m_srcb[perlattice_]){
            alphac = m_alphaorg[j];
            betac = m_betaorg[j];
        }
        else{
            alphac = m_accv[alpha_][j];
            betac = m_accv[beta_][j];
        }
        gamma0 = (1.0+alphac*alphac)/betac;
        for(n = 0; n <= nfin; n++){
            betar = C[j][n]*C[j][n]*betac
                    -2.0*S[j][n]*C[j][n]*alphac
                    +S[j][n]*S[j][n]*gamma0;
            alphar = -C[j][n]*Cd[j][n]*betac
                            +(Sd[j][n]*C[j][n]+S[j][n]*Cd[j][n])*alphac
                            -S[j][n]*Sd[j][n]*gamma0;
            if(n == 0 && alpha != nullptr){
                alpha[j] = alphar;
            }
            if(n == 0 && beta != nullptr){
                beta[j] = betar;
            }
            if(betaarr != nullptr){
                (*betaarr)[j][n] = betar;
            }
            if(alphaarr != nullptr){
                (*alphaarr)[j][n] = alphar;
            }
        }
    }
    return true;
}

void Trajectory::GetXYtildeBetasxyAt(
    int n, Particle *particle, double *XYtilde, double *betasxy, int type)
{
	if(!m_srcb[perlattice_] || !m_issegu){
        for(int j = 0; j < 2; j++){
            XYtilde[j] = particle->_xy[j];
            betasxy[j] = particle->_qxy[j];
        }
		return;
	}

    for(int j = 0; j < 2; j++){
		if(type == 1){
			XYtilde[j] = particle->_xy[j]*m_CU[j][n]+particle->_qxy[j]*m_SU[j][n];
			betasxy[j] = particle->_xy[j]*m_CUd[j][n]+particle->_qxy[j]*m_SUd[j][n];
		}
		else if(type == 2){
	        XYtilde[j] = particle->_xy[j]*m_CD[j][n]+particle->_qxy[j]*m_SD[j][n];
		    betasxy[j] = particle->_xy[j]*m_CDd[j][n]+particle->_qxy[j]*m_SDd[j][n];
		}
		else{
	        XYtilde[j] = particle->_xy[j]*m_C[j][n]+particle->_qxy[j]*m_S[j][n];
		    betasxy[j] = particle->_xy[j]*m_Cd[j][n]+particle->_qxy[j]*m_Sd[j][n];
		}
    }
}

double Trajectory::GetPhaseError(vector<double> &zpeak,
    vector<double> &phase, double beps, vector<vector<double>> &rho)
{
	IDFieldProfile idprof;

    for(int j = 0; j < 2; j++){
        m_injangle[j] = m_offset._beta[j]*m_gamma;
    }
    idprof.SetInjectionAngle(m_injangle);

    double zoffset = 0;
    if(m_srctype == CUSTOM){
        idprof.AllocateIntegral(&m_fvsz, true);
        zoffset = m_zorbit[0]-idprof.GetEntrance();
    }
    else{
        DataContainer bxy;
        vector<string> titles { "z", "Bx", "By" };
        vector<vector<double>> values(3);
        double xyz[3] = { 0, 0, 0 }, Bxyz[3];
        values[0] = m_zorbit;
        values[1].resize(m_ntotorbit);
        values[2].resize(m_ntotorbit);
        for (int n = 0; n < m_ntotorbit; n++){
            xyz[2] = m_zorbit[n];
            Get2dField(1, false, xyz, Bxyz);
            values[1][n] = Bxyz[0];
            values[2][n] = Bxyz[1];
        }
        bxy.Set1D(titles, values);
        idprof.AllocateIntegral(&bxy, true);
    }
    double sigma[NumberUError];
    vector<vector<double>> items;
    int jxyp;
    int endpoles[2] = {0, 0};
    idprof.GetErrorContents(endpoles, sigma, &items, &jxyp);
    vector<double> bpeak = idprof.GetBPeak(jxyp);
    double bmax = 
        max(fabs(minmax(bpeak, true)),
            fabs(minmax(bpeak, false)));
    while(fabs(bpeak[endpoles[0]]) < bmax*beps){
        endpoles[0]++;
    }
    while(fabs(bpeak[bpeak.size()-1-endpoles[1]]) < bmax*beps){
        endpoles[1]++;
    }
    items.clear();
    idprof.GetErrorContents(endpoles, sigma, &items);
    phase = items[UErrorPhaseIdx];
    zpeak = items[UErrorPeakPosIdx];
    zpeak += zoffset;

    if(m_srctype == CUSTOM){
        m_K2 = idprof.GetUndulatorK2();
        m_lu = idprof.GetUndulatorPeriod();
        m_GT[0] = 1.0+m_K2;
        m_GT[1] = 1.0;
    }

    // flux reduction factor
    int npoles = (int)phase.size();
    int N = npoles/2;
    double lu = idprof.GetUndulatorPeriod();
    vector<double> phaseDelta(npoles), varphi(npoles);
    double sigDelta, meandummy, sigphi, sigvarphi;
    phaseDelta[0] = 0;
    varphi[0] = phase[0];
    for(int n = 1; n < npoles; n++){
        // phase error oscillation coming from trajector error
        phaseDelta[n] = (phase[n]-phase[n-1])*0.5;
        if(n%2 == 0){
            varphi[n] = phase[n];
        }
        else{
            if(n == npoles-1){
                varphi[n] = phase[n-1];
            }
            else{
                varphi[n] = (phase[n-1]+phase[n+1])*0.5;
            }
        }
    }
    get_stats(phaseDelta, npoles, &meandummy, &sigDelta);
    get_stats(varphi, npoles, &meandummy, &sigvarphi);

#ifdef _DEBUG
    vector<double> poles(npoles);
    vector<string> navgws;
    for(int n = 0; n < npoles; n++){
        poles[n] = n;
    }
    vector<vector<double>> phaseprof;
    phaseprof.push_back(phase);
    phaseprof.push_back(varphi);
    navgws.push_back("Pole");
    navgws.push_back("Phi");
    navgws.push_back("VarPhi");
#endif

    double sigw, sigxy;
    vector<double> gphase(phase.size());
    rho.resize(2);
    int nh = 0, navgh;
    int nhmax = (int)floor(m_ppconf[maxharm_]+0.5);
    do{
        nh++;
        double rnh = nh*sigma[UErrorPhaseIdx]*DEGREE2RADIAN;
        if(rnh < MAXIMUM_EXPONENT){
            rho[0].push_back(exp(-rnh*rnh));
        }
        else{
            rho[0].push_back(0.0);
        }
        
        f_GetRecovFactor(lu, N, nh, &sigw, &sigxy);
        navgh = (int)floor(0.5+npoles/2.0/sqrt(1.0+PI2*N*N*hypotsq(sigw, 2.0*nh*EnergySpreadSigma())));
        for(int n = 0; n < npoles; n++){
            gphase[n] = 0;
            for(int m = n-navgh; m <= n+navgh; m++){
                int mr = max(0, min(m, npoles-1));
                gphase[n] += varphi[mr];
            }
            gphase[n] /= (double)(2*navgh+1);
        }
        get_stats(gphase, npoles, &meandummy, &sigphi);
        rnh = sqrt(max(0.0, hypotsq(sigvarphi, sigxy*sigDelta)-sigphi*sigphi));
        rnh *= nh*DEGREE2RADIAN;
        rho[1].push_back(exp(-rnh*rnh));

#ifdef _DEBUG
        phaseprof.push_back(gphase);
        stringstream ss;
        ss << "N_" << navgh;
        navgws.push_back(ss.str());
#endif

    } while(nh < nhmax);

#ifdef _DEBUG
    ofstream debug_out(PhaseErrProfile);
    PrintDebugItems(debug_out, navgws);
    PrintDebugRows(debug_out, poles, phaseprof, npoles);
    debug_out.close();
#endif

    return sigma[UErrorPhaseIdx];
}

void Trajectory::AllocateProjectedXPosision()
{
    for(int j = 0; j < 2; j++){
        m_xyprj[j].resize(m_ntotorbit);
        m_csn[j].resize(m_ntotorbit);
    }
    m_prjlen.resize(m_ntotorbit);
    m_prjd.resize(m_ntotorbit);

    for(int n = 0; n < m_ntotorbit; n++){
        for(int j = 0; j < 2; j++){
            m_xyprj[j][n] = m_orbit[n]._xy[j]+(m_conf[slit_dist_]-m_zorbit[n])*m_orbit[n]._beta[j];
        }
        if(n > 0){
            m_prjlen[n] = sqrt(hypotsq(m_xyprj[0][n]-m_xyprj[0][n-1], m_xyprj[1][n]-m_xyprj[1][n-1]));
        }
        double theta = 0;
        if(hypotsq(m_orbit[n]._acc[1], m_orbit[n]._acc[0]) > 0){
            theta = -atan2(-m_orbit[n]._acc[1], -m_orbit[n]._acc[0]);
        }
        m_csn[0][n] = cos(theta);
        m_csn[1][n] = sin(theta);
    }
    m_prjlen[0] = m_prjlen[1];
#ifdef _DEBUG
    if(!XYPrjData.empty()){
        ofstream debug_out(XYPrjData);
        vector<string> titles {"z", "Xprj", "Yprj", "theta"};
        vector<double> items(4);
        PrintDebugItems(debug_out, titles);
        for(int n = 0; n < m_ntotorbit; n++){
            items[0] = m_zorbit[n];
            items[1] = m_xyprj[0][n];
            items[2] = m_xyprj[1][n];
            items[3] = atan2(m_csn[1][n], m_csn[0][n])/DEGREE2RADIAN;
            PrintDebugItems(debug_out, items);
        }
        debug_out.close();
    }
#endif
}

void Trajectory::GetBetaPhaseAdvance(double phase[])
{
    vector<vector<double>> betaarr(2);
    vector<double> divr(m_ntotorbit);
    TransferTwissParamaters(nullptr, nullptr, &betaarr);
    for(int j = 0; j < 2; j++){
        Spline binv;
        for (int n = 0; n < m_ntotorbit; n++){
            divr[n] = 1.0/betaarr[j][n];
        }
        binv.SetSpline(m_ntotorbit, &m_zorbit, &divr);
        phase[j] = binv.Integrate();
    }
}


void Trajectory::GetTrajectory(vector<OrbitComponents> *orbit)
{
    if(orbit->size() < m_ntotorbit){
        orbit->resize(m_ntotorbit);
    }
    for(int n = 0; n < m_ntotorbit; n++){
        (*orbit)[n].SetComponents(&m_orbit[n]);
    }
}


void Trajectory::GetTrajectory(vector<double> &z, vector<vector<double>> *B, 
    vector<vector<double>> *beta, vector<vector<double>> *xy, vector<double> *rz)
{
    z = m_zorbit;
    if(B != nullptr){
        B->resize(3);
        for(int j = 0; j < 3; j++){
            (*B)[j] = m_B[j];
        }
    }
    if(beta != nullptr){
        beta->resize(2);
        for(int j = 0; j < 2; j++){
            (*beta)[j].resize(m_ntotorbit);
        }
    }
    if(xy != nullptr){
        xy->resize(2);
        for(int j = 0; j < 2; j++){
            (*xy)[j].resize(m_ntotorbit);
        }
    }
    if(rz != nullptr){
        rz->resize(m_ntotorbit);
    }
    if(beta == nullptr && xy == nullptr){
        return;
    }
    for(int n = 0; n < m_ntotorbit; n++){
        if(beta != nullptr){
            for(int j = 0; j < 2; j++){
                (*beta)[j][n] = m_orbit[n]._beta[j];
            }
        }
        if(xy != nullptr){
            for(int j = 0; j < 2; j++){
                (*xy)[j][n] = m_orbit[n]._xy[j];
            }
        }
        if(rz != nullptr){
            (*rz)[n] = m_orbit[n]._rz;
        }
    }
}

void Trajectory::GetOrbitComponentIndex(int index, OrbitComponents *orbit)
{
    orbit->SetComponents(&m_orbit[index]);
}

int Trajectory::GetOrbitPoints()
{
    if(m_isfel){
        return m_ntotorbit;
    }
    int norbit = m_ntotorbit;
    double zobsnear = m_conf[slit_dist_];
    if(contains(m_calctype, menu::spdens) && !IsFixedPoint()){
        zobsnear = min(m_confv[zrange_][0], m_confv[zrange_][1]);
    }

    while(zobsnear <= m_zorbit[norbit-1]){
        norbit--;
        if(norbit < 1){
            break;
        }
    }
    return norbit;
}

void Trajectory::GetZCoordinate(vector<double> *zorbit)
{
    if(zorbit == nullptr) return;
    *zorbit = m_zorbit;
}

int Trajectory::GetDataArrangementStatus()
{
    return m_status;
}

bool Trajectory::f_GetLocalWigglerRad(int nfd, vector<double> &ep, 
    int nzp[], double XYZo[], vector<vector<double>> &fd, double *zemission)
{
    double theta, XY[3], xyprj[2], cs, sn;
    double acc[2], beta[2], xy[2], B;
    int nz = nzp[1];
    vector<double> fhvc(4);

    double prjd;
    if((m_prjd[nz-1] > m_prjd[nz] && m_prjd[nz] < m_prjd[nz+1]) 
            || m_prjd[nz-1] == m_prjd[nz] || (nz == m_ntotorbit-2 && m_prjd[nz] == m_prjd[nz+1])){
        prjd = parabloic_peak(zemission, m_zorbit[nz-1], m_zorbit[nz], m_zorbit[nz+1],
            m_prjd[nz-1], m_prjd[nz], m_prjd[nz+1]);
    }
    else{
        return false;
    }

    for(int j = 0; j < 2; j++){
        acc[j] = lagrange(*zemission, m_zorbit[nz-1], m_zorbit[nz], m_zorbit[nz+1], 
                m_orbit[nz-1]._acc[j], m_orbit[nz]._acc[j], m_orbit[nz+1]._acc[j]);
    }
    double cE = CC/m_acc[eGeV_]/1.0e+9;
    B = sqrt(hypotsq(acc[0], acc[1]))/cE;

    if(B < m_Bmax*m_eps_wig){
        return false;
    }
    theta = -atan2(acc[1], acc[0]);
    cs = cos(theta); sn = sin(theta);
    for(int j = 0; j < 2; j++){
        beta[j] = lagrange(*zemission, m_zorbit[nz-1], m_zorbit[nz], m_zorbit[nz+1],
            m_orbit[nz-1]._beta[j], m_orbit[nz]._beta[j], m_orbit[nz+1]._beta[j]);
        xy[j] = lagrange(*zemission, m_zorbit[nz-1], m_zorbit[nz], m_zorbit[nz+1],
            m_orbit[nz-1]._xy[j], m_orbit[nz]._xy[j], m_orbit[nz+1]._xy[j]);
        xyprj[j] = xy[j]+(XYZo[2]-(*zemission))*beta[j];
    }
    xyprj[1] = xyprj[0]*sn+xyprj[1]*cs;
    XY[1] = XYZo[0]*sn+XYZo[1]*cs;

    double epsd = fabs(XY[1]-xyprj[1])-prjd;
    double epsc = max(m_prjlen[nz], m_prjlen[nz+1]);
    if(fabs(epsd) > epsc){
        return false;
    }

    double ec = GetCriticalEnergy(&B);
    double gty = m_gamma*(XY[1]-xyprj[1])/(XYZo[2]-(*zemission));
    gty *= -1; // flip sign, to be consistent with the definition of helicity
    for(int n = 0; n < nfd; n++){
        BMWigglerRadiation::GetBMStokes(ep[n]/ec, gty, &fhvc);
        fd[0][n] += fhvc[0]*cs*cs+fhvc[1]*sn*sn;
        fd[1][n] += fhvc[0]*sn*sn+fhvc[1]*cs*cs;
        fd[2][n] += fhvc[2];
        fd[3][n] += (fhvc[0]-fhvc[1])*2*sn*cs;
    }

    nzp[0] = nzp[1];

    return true;
}

void Trajectory::GetStokesWigglerApprox2D(double *XYZ, 
    int nfd, vector<double> &ep, vector<vector<double>> &fd)
{
    double zemission;
    vector<double> fhvc(4);

    for(int j = 0; j < 4; j++){
        fill(fd[j].begin(), fd[j].end(), 0.0);
    }

#ifdef _DEBUG
    double eptgt = 700;
    int netgt;
    for(netgt = 0; netgt < ep.size()-1; netgt++){
        if(eptgt < ep[netgt]){
            break;
        }
    }
    ofstream debug_out;
    if(!WiggApproxSum.empty()){
        debug_out.open(WiggApproxSum);
        vector<string> titles {"z", "nz", "fx", "fy", "fc", "f45"};
        PrintDebugItems(debug_out, titles);
    }
#endif

    double prjr[2];
    for(int n = 0; n < m_ntotorbit; n++){       
        m_prjd[n] = sqrt(hypotsq(XYZ[0]-m_xyprj[0][n], XYZ[1]-m_xyprj[1][n]));
    }
    prjr[0] = minmax(m_prjd, false);
    prjr[1] = minmax(m_prjd, true);
    if(prjr[1]-prjr[0] < prjr[1]*m_eps_wig){
        // helical undulator on axis, skip
        return;
    }

    bool issrc;
    int nz[2] = {-1, 0};
    for(int n = 1; n < m_ntotorbit-1; n++){
        nz[1] = n;
        issrc = f_GetLocalWigglerRad(nfd, ep, nz, XYZ, fd, &zemission);
#ifdef _DEBUG
        if(!WiggApproxSum.empty() && issrc){
            vector<double> items(6);
            items[0] = zemission;
            items[1] = n;
            for(int j = 0; j < 4; j++){
                items[j+2] = fd[j][netgt];
            }
            PrintDebugItems(debug_out, items);
        }
#endif
    }

#ifdef _DEBUG
    if(!WiggApproxSum.empty()){
        debug_out.close();
    }
#endif
}

string Trajectory::GetErroCode()
{
    string errmsg;
    switch(m_status){
        case ALLOC_ERROR_CANNOT_OPEN_FILE:
            errmsg = "Cannot open the specified file for the field mapping data.";
            break;
        case ALLOC_ERROR_MESH_INVALID:
            errmsg = "Number of data points is not valid.";
            break;
        case TOO_FEW_DATA_POINTS:
            errmsg = "Number of data points is too few. More than 3 points are required.";
            break;
        case ALLOC_ERROR_NO_FIELD_TABLE:
            errmsg = "No magnetic data set is selected.";
            break;
		case PERIOD_LATTICE_MATCHING:
            errmsg = "No lattice functions exist to satisfy the input condition.";
            break;
        default:
            errmsg = "Default Error";
            break;
    }
    return errmsg;
}

void Trajectory::GetOriginXY(double xy[])
{
    for(int j = 0; j < 2; j++){
        xy[j] = m_orbit[m_nzorgorbit]._xy[j];
    }
}


int Trajectory::GetZsection(vector<vector<int>> &secidx)
{
    if(m_secindex.size() == 0){
        return 0;
    }
    secidx = m_secindex;
    return (int)m_secindex[0].size();
}

void Trajectory::GetAvgOrbits(vector<OrbitComponents> &orb)
{
    int nsection = (int)m_secindex[0].size();
    if(orb.size() < nsection){
        orb.resize(nsection);
    }
    double Dxy[2], Dz;
    for(int n = 0; n < nsection; n++){
        Dz = m_zorbit[m_secindex[1][n]]-m_zorbit[m_secindex[0][n]];
        for(int j = 0; j < 2; j++){
            for(int i = 0; i < 2; i++){
                Dxy[i] = m_orbit[m_secindex[i][n]]._xy[j]
                    -m_reforbit[m_secindex[i][n]]._xy[j];
            }
            orb[n]._beta[j] = (Dxy[1]-Dxy[0])/Dz;
            orb[n]._xy[j] = Dxy[1]-m_zorbit[m_secindex[1][n]]*orb[n]._beta[j];
        }
    }
}

void Trajectory::AdvancePhaseSpace(int iniindex,  vector<double> &tarr, 
    vector<vector<double>> *Exy, Particle &particle, double *Fz, double Ej[])
{
    int zstp[] = {0, 1, 1, 2};
    double dzn[] = {1, 2, 2, 1};
    double cE0 = CC/m_acc[eGeV_]/1.0e+9, cE;
    double xytmp[2], qtmp[2], tgtmp[2], Btmp[3], ktmp[5], Etmp[3], values[3], rFz[4];

    Particle dp[4];

    for(int j = 0; j < 2; j++){
        xytmp[j] = particle._xy[j];
        qtmp[j] = particle._qxy[j];
        tgtmp[j] = particle._tE[j];
    }
    dp[0].Clear();
    for(int n = 0; n < 4; n++){
        double dz = m_dxyz[2]*zstp[n];
        for(int j = 0; j < 2 && n > 0; j++){
            xytmp[j] = particle._xy[j]+dp[n-1]._xy[j]*dz;
            qtmp[j] = particle._qxy[j]+dp[n-1]._qxy[j]*dz;
            tgtmp[j] = particle._tE[j]+dp[n-1]._tE[j]*dz;
        }
        cE = cE0/(1+tgtmp[1]);
        tgtmp[1] = (1+tgtmp[1])*m_gamma; // DE/E -> gamma
        GetField(iniindex+zstp[n], true, false, xytmp, Btmp);
        get_EMF_variables(cE, qtmp, Btmp, ktmp);
        if(tgtmp[0] < tarr.front() || tgtmp[0] > tarr.back() || Exy == nullptr)
        {
            Etmp[0] = Etmp[1] = Etmp[2] = 0;
        }
        else{
            double tef = tgtmp[0];
            int idx = get_index4lagrange(tef, tarr, (int)tarr.size());
            for(int j = 0; j < 3; j++){
                for(int k = 0; k < 3; k++){
                    if(Exy != nullptr){
                        values[k] = (*Exy)[j][idx-1+k];
                    }
                }
                Etmp[j] = lagrange(tef,
                    tarr[idx-1], tarr[idx], tarr[idx+1], values[0], values[1], values[2]);
            }
        }
        for(int j = 0; j < 2; j++){
            Ej[j] = Etmp[j];
            dp[n]._qxy[j] = ktmp[j];
            dp[n]._xy[j] = ktmp[j+2];
        }
        Ej[2] = Etmp[2];
        dp[n]._tE[0] = (1/tgtmp[1]/tgtmp[1]+ktmp[4])/2/CC;
        dp[n]._tE[1] = (Etmp[0]*qtmp[0]+Etmp[1]*qtmp[1]+Etmp[2])/(m_acc[eGeV_]*1.0e+9);
        rFz[n] = dp[n]._tE[1];

        if(iniindex > m_nxyz[2]-2){ // additional step: Euler method
            for(int j = 0; j < 2; j++){
                particle._qxy[j] += 2*m_dxyz[2]*dp[n]._qxy[j];
                particle._xy[j] += 2*m_dxyz[2]*dp[n]._xy[j];
            }
            particle._tE[0] += 2*m_dxyz[2]*dp[n]._tE[0];
            particle._tE[1] += 2*m_dxyz[2]*dp[n]._tE[1];
            return;
        }
    }

    *Fz = 0;
    for(int n = 0; n < 4; n++){
        double dz = m_dxyz[2]*dzn[n]/3.0;
        for(int j = 0; j < 2; j++){
            particle._qxy[j] += dp[n]._qxy[j]*dz;
            particle._xy[j] += dp[n]._xy[j]*dz;
            particle._tE[j] += dp[n]._tE[j]*dz;
        }
        *Fz += rFz[n]*dz;
    }
}

//---------- private functions ----------
void Trajectory::f_AssignErrorField()
{
	UndulatorFieldData udata;
	double sigma[NumberUError], sigalloc[NumberUError];
	RandomUtility rand;

	int seed = (int)floor(0.5+m_src[seed_]);
	rand.Init(seed);

    sigma[UErrorBdevIdx] = m_src[fsigma_]*0.01; // % -> normal
    sigma[UErrorPhaseIdx] = m_src[psigma_];
    sigma[UErrorXerrorIdx] = m_srcv[xysigma_][0]*1.0e-3*m_gamma; // mm -> normalized
    sigma[UErrorYerrorIdx] = m_srcv[xysigma_][1]*1.0e-3*m_gamma;

	for(int j = UErrorXerrorIdx; j <= UErrorBdevIdx; j++){
		if(sigma[j] < 0){
			sigma[j] = fabs(sigma[j])*rand.Uniform(0.0, 1.0);
		}
	}
	udata.AllocateUData(&rand, m_N, m_lu, m_K2, m_Kxy, m_deltaxy, sigma, sigalloc, m_issymmetric, m_srcb[endmag_]);
	udata.GetErrorArray(&m_I1err, &m_bkick);
	udata.GetEnt4Err(m_z0thpole);
}

void Trajectory::f_ArrangeFieldComponent()
{
    double XYhalf, zmax, radius;
    int Nadd, Ndrift, n, j, nx, m, mk, indexdata;
    int nppp = 16;

    m_seczpos.clear();
    if(m_ismapaxis){
        m_status = f_AllocateData(m_srctype == CUSTOM ? &m_fvsz : &m_fvsz1per);
        if(m_status < 0) return;
    }
    else if(m_ismap3d){
		m_status = f_AllocateData(m_srcs[fmap_]);
        if(m_status < 0) return;
    }
    else if(m_isdefault){
        nppp *= 2; // Runge-Kutta method
        if(m_isf8){
            nppp <<= 1; // half-period field is contained
        }
        else if(m_srctype == MULTI_HARM_UND){
            nppp *= (int)m_harmcont.size();
        }
		if(m_iscoherent){
			nppp *= (int)floor(sqrt(1.0+m_K2));
		}
        nppp <<= m_accuracy[accdisctra_];
        Nadd = 2*m_extraN;
		Nadd += 2*ENDPERIODS;

        m_dxyz[2] = m_lu/(double)nppp;
		radius = GetOrbitRadius();
		double dzmax = radius/m_gamma/(double)(1<<m_accuracy[accdisctra_]);
		while(m_dxyz[2] > dzmax){
			m_dxyz[2] *= 0.5;
			nppp <<= 1;
		}
        m_nxyz[2] = (m_N+Nadd+1)*nppp+1;

		if(m_issegu){
            Ndrift = (int)floor(m_Ldrift/m_dxyz[2])+1;
        }
        else{
            Ndrift = 0;
        }
        m = m_issrc2 ? 2*m_M : m_M;
        m_nxyz[2] = m*m_nxyz[2]+(m-1)*Ndrift;
    }

    if(m_isbm || m_iswshifter){
        radius = GetOrbitRadius();
        if(m_iswshifter){
            zmax = m_src[mplength_]*0.5+m_src[subpolel_];
            m_dxyz[2] = radius/m_gamma/(double)m_accuracy[accdisctra_];
            m_dxyz[2] = zmax/ceil(zmax/m_dxyz[2]+INFINITESIMAL);
            zmax += m_dxyz[2]*2.0;
		}
        else{
            zmax = (m_src[bendlength_]+m_src[fringelen_]*m_nlimit[acclimtra_]*10.0)*0.5;
            if (m_srcb[bmtandem_]){
                zmax += m_src[bminterv_];
            }
            double divfactor = 20.0;
            m_dxyz[2] = radius/m_gamma/divfactor/(double)m_accuracy[accdisctra_];
        }
        m_nxyz[2] = 2*(int)ceil(zmax/m_dxyz[2])+1;
        m_nzorg = (m_nxyz[2]-1)/2+(int)(m_zorg_BM/m_dxyz[2]); // index point@z=0
    }
    else{
        m_nzorg = (m_nxyz[2]-1)/2; // index point@z=0
    }

    m_zz.resize(m_nxyz[2]);
    for(n = 0; n < m_nxyz[2]; n++){
        m_zz[n] = (double)(n-m_nzorg)*m_dxyz[2];
    }
    m_Bps.resize(m_nxyz[2], 0.0);

    indexdata = m_nxyz[2]%2+2*(abs(m_nzorg)%2);
    switch(indexdata){
        case 0: // origin: even, data points: even
            m_nzorgorbit = m_nzorg/2;
            m_ntotorbit = m_nxyz[2]/2;
            break;
        case 1: // origin: even, data points: odd
            m_nzorgorbit = m_nzorg/2;
            m_ntotorbit = (m_nxyz[2]+1)/2;
            break;
        case 2: // origin: odd, data points: even
            m_nzorgorbit = (m_nzorg+1)/2;
            m_ntotorbit = m_nxyz[2]/2;
            break;
        case 3: // origin: odd, data points: odd
            m_nzorgorbit = (m_nzorg+1)/2;
            m_ntotorbit = (m_nxyz[2]+1)/2;
            break;
    }
    m_zorbit.resize(m_ntotorbit);
    m_orbit.resize(m_ntotorbit);
    for(j = 0; j < 3; j++){
        m_B[j].resize(m_ntotorbit);
    }
    for(n = 0; n < m_ntotorbit; n++){
        m_zorbit[n] = (double)(n-m_nzorgorbit)*m_dxyz[2]*2.0;
    }

    if(m_issegu && m_srcb[perlattice_]){
        double finv[2];
		vector<double> finv1[2], finv2[2];
        int Mtot = (m_issrc2?2:1)*m_M;
        for(m = 1; m <= Mtot; m++){
            for(int j = 0; j < 2; j++){
                m_betac[j][m] = m_accv[beta_][j];
                m_alphac[j][m] = m_accv[alpha_][j]*(m%2?1.0:-1.0);
            }
        }
        if(Mtot%2){ // save the Twiss parametes at the center
            for(int j = 0; j < 2; j++){
                m_betaorg[j] = m_betac[j][(Mtot+1)/2];
                m_alphaorg[j] = m_alphac[j][(Mtot+1)/2];
            }
        }

        vector<double> FC[2], FS[2], FCd[2], FSd[2], Z[2];
        int nzMatch = max(1, (int)floor(m_src[mdist_]/(2.0*m_dxyz[2])));
        m_Lmatch = (double)nzMatch*(2.0*m_dxyz[2]);
        for(j = 0; j < 2; j++){
            m_finvmatch[j].resize(m_ntotorbit, 0.0);
            m_C[j].resize(Mtot+1);
            m_S[j].resize(Mtot+1);
            m_Cd[j].resize(Mtot+1);
            m_Sd[j].resize(Mtot+1);
            FC[j].resize(Mtot+1);
            FS[j].resize(Mtot+1);
            FCd[j].resize(Mtot+1);
            FSd[j].resize(Mtot+1);
            Z[j].resize(Mtot+1);

            m_CU[j].resize(Mtot+1);
            m_SU[j].resize(Mtot+1);
            m_CUd[j].resize(Mtot+1);
            m_SUd[j].resize(Mtot+1);
            m_CD[j].resize(Mtot+1);
            m_SD[j].resize(Mtot+1);
            m_CDd[j].resize(Mtot+1);
            m_SDd[j].resize(Mtot+1);

			finv1[j].resize(Mtot+1);
			finv2[j].resize(Mtot+1);
		}

		vector<vector<double>> M1(3), M2(3), M3(3), Mmid(3);
        for(j = 0; j < 3; j++){
            M1[j].resize(3, 0.0); 
            M2[j].resize(3, 0.0);
            M3[j].resize(3, 0.0); 
			Mmid[j].resize(3, 0.0); 
        }
		M1[2][2] = 1.0;
		M2[2][2] = 1.0;
		M3[2][2] = 1.0;
		Mmid[2][2] = 1.0;

        Z[1][0] = m_zorbit[0];
        Z[0][Mtot] = m_conf[slit_dist_];
        for(m = 1; m < Mtot; m++){
            int jm = (int)floor(0.5+(m_LatticeZ[m]-m_Lmatch*0.5-m_zorbit[0])/(2.0*m_dxyz[2]));
            for(int j = 0; j < 2; j++){
                if(Mtot%2 == 0 && m == Mtot/2){ // beta and alpha @ z origin
                    if(!f_GetMatchingF(j, m, m_zorbit[jm], m_zorbit[jm+nzMatch], finv, m_betaorg, m_alphaorg)){
						m_status = PERIOD_LATTICE_MATCHING;
						return;
					}
                }
                else{
                    if(!f_GetMatchingF(j, m, m_zorbit[jm], m_zorbit[jm+nzMatch], finv)){
						m_status = PERIOD_LATTICE_MATCHING;
						return;
					}
                }
                finv1[j][m] = m_finvmatch[j][jm] = finv[0];
                finv2[j][m] = m_finvmatch[j][jm+nzMatch] = finv[1];
                if(j == 0){
                    Z[0][m] = m_zorbit[jm];
                    Z[1][m] = m_zorbit[jm+nzMatch];
                }
                unit_matrix(2, M1); M1[1][0] = finv[1];
                unit_matrix(2, M2); M2[0][1] = Z[1][m]-Z[0][m];
                multiply_matrices(M1, M2, M3);
                unit_matrix(2, M1); M1[1][0] = finv[0];
                multiply_matrices(M3, M1, M2);
                unit_matrix(2, M2); M3[0][1] = Z[0][m]-Z[1][m-1];
                multiply_matrices(M2, M3, M1);
                FC[j][m] = M1[0][0];
                FS[j][m] = M1[0][1];
                FCd[j][m] = M1[1][0];
                FSd[j][m] = M1[1][1];
            }
        }

		vector<vector<vector<double>>> Mstru(Mtot), Mstrd(Mtot);
        for(m = 1; m < Mtot; m++){
			Mstru[m].resize(3);
			Mstrd[m].resize(3);
	        for(j = 0; j < 3; j++){
				Mstru[m][j].resize(3, 0.0);
				Mstrd[m][j].resize(3, 0.0);
			}
		}
		double lmag = m_src[interval_]-m_Lmatch;
        for(int j = 0; j < 2; j++){
            unit_matrix(2, M2);
            for(m = 1; m < Mtot; m++){
				finv[0] = finv1[j][m]; finv[1] = finv2[j][m];

				// matrix for Um->Dm
                M3[0][0] = 1.0; M3[0][1] = lmag*0.5; M3[1][0] = finv[0]; M3[1][1] = finv[0]*M3[0][1]+1;
				multiply_matrices(M3, M2, M1);
				M2 = M1;
				M3[0][0] = M3[1][1] = 1.0; M3[0][1] = m_Lmatch*0.5; M3[1][0] = 0.0;
				multiply_matrices(M3, M2, M1);
                M2 = M1;
                Mstrd[m] = M1;
				if(Mtot%2 == 0 && m == Mtot/2){
                    Mmid = M1;
				}

				// matrix for Dm->Um+1
                M3[0][0] = 1.0; M3[0][1] = m_Lmatch*0.5; M3[1][0] = finv[1]; M3[1][1] = finv[1]*M3[0][1]+1;
				multiply_matrices(M3, M2, M1);
                M2 = M1;
				M3[0][0] = M3[1][1] = 1.0; M3[0][1] = lmag*0.5; M3[1][0] = 0.0;
				multiply_matrices(M3, M2, M1);
                M2 = M1;
                Mstru[m] = M1;

				if(Mtot%2 > 0 && m == (Mtot-1)/2){
                    Mmid = M1;
				}
			}
			inverse_matrix(Mmid, M1);
			m_CU[j][0] = M1[0][0]; m_SU[j][0] = M1[0][1];
			m_CUd[j][0] = M1[1][0]; m_SUd[j][0] = M1[1][1];
            for(m = 1; m < Mtot; m++){
				multiply_matrices(Mstrd[m], M1, M2);
                m_CD[j][m] = M2[0][0];
                m_SD[j][m] = M2[0][1];
                m_CDd[j][m] = M2[1][0];
                m_SDd[j][m] = M2[1][1];
				multiply_matrices(Mstru[m], M1, M2);
                m_CU[j][m+1] = M2[0][0];
                m_SU[j][m+1] = M2[0][1];
                m_CUd[j][m+1] = M2[1][0];
                m_SUd[j][m+1] = M2[1][1];
			}
		}

		for(int j = 0; j < 2; j++){
            for(m = 1; m <= Mtot; m++){
                unit_matrix(2, M1); M1[0][1] = Z[0][Mtot]-Z[1][Mtot-1];
                for(mk = Mtot-1; mk >= m; mk--){
                    unit_matrix(2, M2); M2[0][1] = Z[1][mk]-Z[1][mk-1];
                    multiply_matrices(M1, M2, M3);
                    M1 = M3;
                }
                for(mk = m-1; mk >= 1; mk--){
                    M2[0][0] = FC[j][mk];
                    M2[0][1] = FS[j][mk];
                    M2[1][0] = FCd[j][mk];
                    M2[1][1] = FSd[j][mk];
                    multiply_matrices(M1, M2, M3);
                    M1 = M3;
                }
                m_C[j][m] = M1[0][0];
                m_S[j][m] = M1[0][1];
                m_Cd[j][m] = M1[1][0];
                m_Sd[j][m] = M1[1][1];
            }
        }
    }

#ifdef _DEBUG
	if(!TwissPrmData.empty()){
		ofstream debug_out(TwissPrmData);
		if(debug_out && m_issegu && m_srcb[perlattice_]){
			vector<double> tmp(8);
            int Mtot = (m_issrc2?2:1)*m_M;
            for (m = 1; m <= Mtot; m++){
                for(int j = 0; j < 2; j++){
                    tmp[4*j] = m_C[j][m];
                    tmp[4*j+1] = m_S[j][m];
                    tmp[4*j+2] = m_Cd[j][m];
                    tmp[4*j+3] = m_Sd[j][m];
                }
				PrintDebugItems(debug_out, (double)m, tmp);
			}
		}
	}
#endif

	if(m_isbm || m_iswshifter || m_isdefault){
        m_status = FieldMapStatusDataArranged;
        return;
    }

    for(j = 0; j < 2; j++){
        XYhalf = (double)(m_nxyz[j]-1)*m_dxyz[j]*0.5;
        m_xyarray[j].resize(m_nxyz[j]);
        for(nx = 0; nx < m_nxyz[j]; nx++){
            m_xyarray[j][nx] = nx*m_dxyz[j]-XYhalf;
        }
    }
    if(m_ismapaxis){
        for(j = 0; j < 2; j++){
            m_SplineBxy[j].resize(m_nxyz[2]);
            m_SplineBz[j].resize(m_nxyz[2]);
            for(n = 0; n < m_nxyz[2]; n++){
                if(m_nxyz[j] < 2){
                    continue;
                }
                m_SplineBxy[j][n].SetSpline(m_nxyz[j], &m_xyarray[j], &m_Bxy[j][n], true);
                m_SplineBz[j][n].SetSpline(m_nxyz[j], &m_xyarray[j], &m_Bz[j][n], true);
            }
        }
    }
    m_status = FieldMapStatusDataArranged;
}

double Trajectory::f_GetPhaseAdvances(vector<vector<double>> &Drz, bool settgt)
{
    vector<double> rzarray(m_ntotorbit);
    Spline rzspline;

    AllocateTrajectory(true, true, true);
    for(int n = 0; n < m_ntotorbit; n++){
        rzarray[n] = m_orbit[n]._rz;
    }
    rzspline.SetSpline(m_ntotorbit, &m_zorbit, &rzarray);

#ifdef _DEBUG
	if(!PhaseCorrRz.empty()){
		ofstream debug_out(PhaseCorrRz);
		if(debug_out){
            vector<double> rztmp(rzarray);
            rztmp *= m_gamma2;
			PrintDebugPair(debug_out, m_zorbit, rztmp, m_ntotorbit);
		}
	}
#endif

    for(int m = 1; m <= m_M; m++){
        Drz[0][m] = m_gamma2*rzspline.GetValue(m_zorg[m]);
        if(m_issrc2){
            Drz[1][m] = m_gamma2*rzspline.GetValue(m_zorgS[m]);
        }
    }

    double DrzPer = m_lu*(1.0+m_K2);
    double phase[2];
    double phaseerr = 0; 
    int jfin = 0;
    for(int m = 1; m <= (m_issrc2?m_M:(m_M-1)); m++){
        if(m_issrc2){
            for(int j = 0; j < 2; j++){
                phase[j] = m_segphase[j+1]-PI2*m_pslip;
            }
            Drz[0][m] = Drz[1][m]-Drz[0][m]+m_src[interval_];
            if(m < m_M){
                Drz[1][m] = Drz[0][m+1]-Drz[1][m]+m_src[interval_];
                jfin = 1;
            }
            else{
                jfin = 0;
            }
        }
        else{
            phase[0] = m_segphase[0]-PI2*m_pslip;
            Drz[0][m] = Drz[0][m+1]-Drz[0][m]+m_src[interval_];
        }
        for(int j = 0; j <= jfin; j++){
            if(settgt){
                m_Trz[j][m] = (floor(Drz[j][m]/DrzPer)+phase[j]/PI2)*DrzPer;
                while(m_Trz[j][m] < Drz[j][m]){
                    m_Trz[j][m] += DrzPer;
                }
            }
            Drz[j][m] = m_Trz[j][m]-Drz[j][m];
            phaseerr = max(phaseerr, fabs(Drz[j][m]/DrzPer));
        }
    }

#ifdef _DEBUG
	if(!PhaseCorrDrz.empty()){
		ofstream debug_out(PhaseCorrDrz);
		if(debug_out){
            vector<double> mtmp(m_M+1);
            for(int m = 0; m <= m_M; m++){
                mtmp[m] = m;
            }
			PrintDebugRows(debug_out, mtmp, Drz, m_M+1);
		}
	}
#endif

    return phaseerr;
}

void Trajectory::f_AllocatePhaseCorrection()
{
    double rBxzy[3];
    vector<double> rzarray(m_ntotorbit);
    Spline rzspline;

    if(!m_issegu){
        return;
    }

    vector<vector<double>> Drz0(2), Drz1(2), bkps0(2), bkps(2), bkps1(2);
    for(int j = 0; j < 2; j++){
        Drz0[j].resize(m_M+1);
        Drz1[j].resize(m_M+1);
        bkps0[j].resize(m_M+1, 0.0);
        bkps1[j].resize(m_M+1);
        bkps[j].resize(m_M+1);
        m_zmid[j].resize(m_M+1);
        m_Trz[j].resize(m_M+1, 0.0);
        m_Drz[j].resize(m_M+1, 0.0);
    }
    for (int m = 1; m <= (m_issrc2?m_M:(m_M-1)); m++){
        if (m_issrc2){
            m_zmid[0][m] = (m_zorg[m]+m_zorgS[m])*0.5;
            if (m < m_M){
                m_zmid[1][m] = (m_zorgS[m]+m_zorg[m+1])*0.5;
            }
        }
        else{
            m_zmid[0][m] = (m_zorg[m]+m_zorg[m+1])*0.5;
        }
    }
    f_GetPhaseAdvances(Drz0, true); // get initial status

    for(int m = 1; m <= (m_issrc2?m_M:(m_M-1)); m++){// apply initial phase shifter values
        int idx = SearchIndex(m_nxyz[2], true, m_zz, m_zmid[0][m]);
        GetField(idx, false, true, nullptr, rBxzy);
        bkps1[0][m] = (rBxzy[1]<0?-1.0:1.0)*(Drz0[0][m]<0?-1.0:1.0)
            *sqrt(fabs(Drz0[0][m])/(5.0*m_lu/8.0))/m_lu/COEF_K_VALUE;
        if(m_issrc2 && m < m_M){
            int idx = SearchIndex(m_nxyz[2], true, m_zz, m_zmid[0][m]);
            GetField(idx, false, true, nullptr, rBxzy);
            bkps1[1][m] = (rBxzy[1]<0?-1.0:1.0)*(Drz0[0][m]<0?-1.0:1.0)
                *sqrt(fabs(Drz0[1][m])/(5.0*m_lu/8.0))/m_lu/COEF_K_VALUE;
        }
    }
    for(int n = 0; n < m_nxyz[2]; n++){
        m_Bps[n] = f_PhaseShifterField(m_zz[n], bkps1);
    }

    while(f_GetPhaseAdvances(Drz1, false) > 0.01){
        for (int m = 1; m <= (m_issrc2?m_M:(m_M-1)); m++){
            int jfin = (m_issrc2 && m < m_M)?1:0;
            for (int j = 0; j <= jfin; j++){
                bkps[j][m] = bkps0[j][m]+Drz0[j][m]/(Drz0[j][m]-Drz1[j][m])*(bkps1[j][m]-bkps0[j][m]);
                if (fabs(Drz1[j][m]) < fabs(Drz0[j][m])){
                    Drz0[j][m] = Drz1[j][m];
                    bkps0[j][m] = bkps1[j][m];
                }
                bkps1[j][m] = bkps[j][m];
            }
        }
        for (int n = 0; n < m_nxyz[2]; n++){
            m_Bps[n] = f_PhaseShifterField(m_zz[n], bkps1);
        }
    };
}

int Trajectory::f_AllocateData(DataContainer *zvsbxy)
{
    int n, nn, m, ndnew, nfft0, nfft, nbkmax = 0, nbkhigh, ndata, nz, ndatanew;
    double bkmax, lushort, bk;
    double xy, dk, kxy, chyper, shyper, deltaz;
    double bz1, dbdz1, bz2, dbdz2, DLdump2, tex1, tex2, Dz1, Dz2;
    double dz, dzav, zr, zexit, fsign;
    double *bfft, *bffttmpz, *bffttmp;
    double I1offset[2], I2offset[2], kuz;
    double B1up[2], B2up[2], B1dw[2], B2dw[2];
    int j, i;
    IDFieldProfile finteg;

    vector<double> z, bxytmp[2], ztmp;
    vector<vector<double>> bxy(2);
    Spline splineb;

    if(zvsbxy == nullptr){
        return ALLOC_ERROR_NO_FIELD_TABLE;
    }

    if(m_srctype == CUSTOM_PERIODIC){
        zvsbxy->GetArray1D(0, &ztmp);
        ndata = (int)ztmp.size();
        finteg.GetAdjustConditions(zvsbxy, &bxytmp[0], &bxytmp[1], I1offset, I2offset);
        for(j = 0; j < 2; j++){
            B1up[j] = I1offset[j]/2.0/m_lu*PI;
            B2up[j] = I2offset[j]*PI2/m_lu/m_lu-2.0*B1up[j];
            B1dw[j] = -B1up[j];
            B2dw[j] = -(I2offset[j]+I1offset[j]*m_lu)*PI2/m_lu/m_lu-2.0*B1dw[j];
			if(!m_srcb[endmag_]){
				B2up[j] = B2dw[j] = 0;
			}
        }

        int N = m_N+2*ENDPERIODS;
        ndatanew = (ndata-1)*N+1;
        bxy[0].resize(ndatanew);
        bxy[1].resize(ndatanew);
        z.resize(ndatanew);
        for(m = 1; m <= N+1; m++){
            for(n = 0; n < ndata-1; n++){
                nn = (m-1)*(ndata-1)+n;
                z[nn] = (double)(m-1)*m_lu+ztmp[n];
                if(m == 1){
                    kuz = PI2*(ztmp[n]-ztmp[1])/m_lu;
                    for(int j = 0; j < 2; j++){
                        bxy[j][nn] = B1up[j]*sin(kuz/2.0)+B2up[j]*sin(kuz);
                    }
                }
                else if(m >= N){
                    kuz = PI2*(ztmp[n]-ztmp[1])/m_lu;
                    for(int j = 0; j < 2; j++){
                        bxy[j][nn] = B1dw[j]*sin(kuz/2.0)+B2dw[j]*sin(kuz);
                    }
                    if(m == N && n == 0){
                        for(int j = 0; j < 2; j++){
                            bxy[j][nn] += 0.5*bxytmp[j][n];
                        }
                    }
                }
                else{
                    for (int j = 0; j < 2; j++){
                        bxy[j][nn] = bxytmp[j][n];
                    }
                    if(m == 2 && n == 0){
                        bxy[0][nn] *= 0.5; bxy[1][nn] *= 0.5;
                    }
                }
                if(m > N){
                    break;
                }
            }
        }
        ndata = ndatanew;

#ifdef _DEBUG
	if(!CustomPeriodicData.empty()){
		ofstream debug_out(CustomPeriodicData);
		if(debug_out){
            PrintDebugRows(debug_out, z, bxy, ndata);
		}
	}
#endif
    }
    else{
        zvsbxy->GetArray1D(0, &z);
        zvsbxy->GetArray1D(1, &bxy[0]);
        zvsbxy->GetArray1D(2, &bxy[1]);
        ndata = (int)z.size();
        if(m_isfel){
            if(m_sections.size() > 0){
                m_seczpos.resize(m_sections.size());
                for(int n = 0; n < m_sections.size(); n++){
                    m_seczpos[n] = z[m_sections[n]]-z[0];
                }
            }
        }
    }

    m_Bmax = 0.0;
    for(n = 0; n < ndata; n++){
        m_Bmax = max(m_Bmax, sqrt(hypotsq(bxy[0][n], bxy[1][n])));
    }

    if(ndata < 3){
        return TOO_FEW_DATA_POINTS;
    }

    dzav = (z[ndata-1]-z[0])/(ndata-1);
    dz = z[1]-z[0];
    for(n = 1; n < ndata-1; n++){
        if(dz > z[n+1]-z[n] && z[n+1] > z[n]+dzav*0.01){
            dz = z[n+1]-z[n];
        }
    }
    dz /= (double)(1<<m_accuracy[accdisctra_]);
    nfft0 = ndnew = (int)floor((z[ndata-1]-z[0])/dz)+1;
    nfft0 = nfft0*3/2;  // to avoid contamination during convolution

    nfft = 1;
    while(nfft < nfft0) nfft <<= 1;

    m_dxyz[2] = dz;
    m_nxyz[2] = ndnew;
    for(j = 0; j < 2; j++){
        m_Bxy[j].resize(m_nxyz[2]);
        m_Bz[j].resize(m_nxyz[2]);
    }

    FastFourierTransform fft(1, nfft);

    bfft =(double *)calloc(2*nfft, sizeof(double));
    bffttmp = (double *)calloc(2*nfft, sizeof(double));
    bffttmpz = (double *)calloc(2*nfft, sizeof(double));

    zexit = z[0]+dz*(double)(nfft-1);
    DLdump2 = (zexit-z[ndata-1])*0.1;
    DLdump2 *= 2.0*DLdump2;

    for(j = 0; j < 2; j++){
        // spline interpolaton needed; otherwise the K value becomes lower
        splineb.SetSpline(ndata, &z, &bxy[j]);
        if(!m_isnatfoc[j]){
            m_dxyz[j] = 0.0;
            m_nxyz[j] = 1;
            for(nz = 0; nz < m_nxyz[2]; nz++){
                m_Bxy[j][nz].resize(1);
                m_Bz[j][nz].resize(1);
                m_Bxy[j][nz][0] = splineb.GetValue(z[0]+dz*(double)nz);
                m_Bz[j][nz][0] = 0.0;
            }
            continue;
        }
        bz1 = bxy[j][ndata-1]; bz2 = bxy[j][0];

        nn = ndata-2;
        while(z[ndata-1]-z[nn] < dzav*0.01){
            nn--;
        }
        dbdz1 = (bxy[j][ndata-1]-bxy[j][nn])/(z[ndata-1]-z[nn]);

        nn = 1;
        while(z[nn]-z[0] < dzav*0.01){
            nn++;
        }
        dbdz2 = (bxy[j][nn]-bxy[j][0])/(z[nn]-z[0]);

        for(n = 0; n < nfft; n++){
            deltaz = (double)n*dz;
            zr = z[0]+deltaz;
            if(zr > z[ndata-1]){
                Dz1 = zr-z[ndata-1];
                if(bz1){
                    tex1 = Dz1*dbdz1/bz1;
                    tex1 *= 1.0-tex1;
                    tex1 += -Dz1*Dz1/DLdump2;
                }
                else{
                    tex1 = 0.0;
                }

                Dz2 = zr-zexit;
                if(bz2){
                    tex2 = Dz2*dbdz2/bz2;
                    tex2 *= 1.0-tex2;
                    tex2 += -Dz2*Dz2/DLdump2;
                }
                else{
                    tex2 = 0.0;
                }

                if(fabs(tex1) < MAXIMUM_EXPONENT){
                    bfft[2*n] = bz1*exp(tex1);
                }
                else{
                    bfft[2*n] = 0.0;
                }
                if(fabs(tex2) < MAXIMUM_EXPONENT){
                    bfft[2*n] += bz2*exp(tex2);
                }
            }
            else{
                bfft[2*n] = splineb.GetValue(zr);
            }
            bfft[2*n+1] = 0.0;
        }

#ifdef _DEBUG
	if(!CustomArrangeFoc.empty()){
		ofstream debug_out(CustomArrangeFoc);
		if(debug_out){
            PrintDebugFFT(debug_out, dz, bfft, nfft, nfft, false);
		}
	}
#endif
        fft.DoFFT(bfft, 1);
        bkmax = 0.0;
        for(n = 0; n < nfft/2; n++){
            bk = sqrt(hypotsq(bfft[2*n], bfft[2*n+1]));
            if(bkmax < bk){
                bkmax = bk;
                nbkmax = n;
            }
        }
        for(n = nbkmax; n < nfft/2; n++){
            if(bkmax > 10.0*sqrt(hypotsq(bfft[2*n], bfft[2*n+1]))){
                break;
            }
        }
        nbkhigh = n;
        lushort = (double)nfft/(double)nbkhigh*dz;
        m_dxyz[j] = min(1.0e-3, lushort*LN2DIV2PI/5.0);

        m_nxyz[j] = 2*(int)floor(LN2DIV2PI*lushort/m_dxyz[j])+1;
        dk = PI2/(dz*nfft);

        for(nz = 0; nz < m_nxyz[2]; nz++){
            m_Bxy[j][nz].resize(m_nxyz[j]);
            m_Bz[j][nz].resize(m_nxyz[j]);
        }

#ifdef _DEBUG
	if(!CustomArrangeFocA.empty()){
		ofstream debug_out(CustomArrangeFocA);
		if(debug_out){
            PrintDebugFFT(debug_out, dk, bfft, nfft, nfft, true);
		}
	}
#endif
        for(i = 0; i < m_nxyz[j]; i++){
            xy = (double)(i-(m_nxyz[j]-1)/2)*m_dxyz[j];
            fsign = xy < 0.0 ? -1.0 : 1.0;
            for(n = 0; n < nfft; n++){
                kxy = fsign*min(dk*(double)fft_index(n, nfft, 1)*fabs(xy), LOG1E6);
                chyper = coshyper(kxy);
                shyper = sinhyper(kxy);
                bffttmp[2*n] = bfft[2*n]*chyper;
                bffttmp[2*n+1] = bfft[2*n+1]*chyper;
                bffttmpz[2*n] = bfft[2*n]*shyper;
                bffttmpz[2*n+1] = bfft[2*n+1]*shyper;
            }

#ifdef _DEBUG
            if(!CustomArrangeFocXY.empty()){
                ofstream debug_out(CustomArrangeFocXY);
                if (debug_out){
                    PrintDebugFFT(debug_out, dk, bffttmp, nfft, nfft, true);
                }
            }
            if(!CustomArrangeFocZ.empty()){
                ofstream debug_out(CustomArrangeFocZ);
                if (debug_out){
                    PrintDebugFFT(debug_out, dk, bffttmpz, nfft, nfft, true);
                }
            }
#endif

            fft.DoFFT(bffttmp, -1);
            fft.DoFFT(bffttmpz, -1);
            for(n = 0; n < m_nxyz[2]; n++){
                nn = n;
                if(n >= nfft){
                    nn = 0;
                }
                m_Bxy[j][n][i] = bffttmp[2*nn]/(double)nfft;
                m_Bz[j][n][i] = bffttmpz[2*nn+1]/(double)nfft;
            }

        }
    }

#ifdef _DEBUG
    if(!CustomArrangeFocXYZ.empty()){
        ofstream debug_out(CustomArrangeFocXYZ);
        if(debug_out){
            vector<double> griddata(6);
            for(int j = 0; j < 3; j++){
                griddata[2*j] = m_dxyz[j];
                griddata[2*j] = m_nxyz[j];
            }
            PrintDebugItems(debug_out, griddata);
            griddata.resize(3);
            for (int nx = 0; nx < m_nxyz[0]; nx++){
                for (int ny = 0; ny < m_nxyz[1]; ny++){
                    for (int nz = 0; nz < m_nxyz[2]; nz++){
                        for (int j = 0; j < 3; j++){
                            griddata[j] = m_Bxyz[j][nx][ny][nz];
                        }
                        PrintDebugItems(debug_out, griddata);
                    }
                }
            }
        }
    }
#endif

    free(bfft);
    free(bffttmp);
    free(bffttmpz);

    return FieldMapStatusDataAllocated;
}

void Trajectory::f_FinerStep()
{
    int nstep = (m_nxyz[2]-1)*m_accuracy[accdisctra_]+1;
    double dz = m_dxyz[2]/m_accuracy[accdisctra_];

    vector<double> z(m_nxyz[2]);
    for(int n = 0; n < m_nxyz[2]; n++){
        z[n] = n*m_accuracy[accdisctra_];
    }

    int nx, ny, nz;
    Spline bspl;
    for(int j = 0; j < 3; j++){
        for(nx = 0; nx < m_nxyz[0]; nx++){
            for(ny = 0; ny < m_nxyz[1]; ny++){
                bspl.SetSpline(m_nxyz[2], &z, &m_Bxyz[j][nx][ny], true);
                m_Bxyz[j][nx][ny].resize(nstep);
                for(nz = 0; nz < nstep; nz++){
                    m_Bxyz[j][nx][ny][nz] = bspl.GetValue(nz);
                }
            }
        }
    }
    m_nxyz[2] = nstep;
    m_dxyz[2] = dz;
}

int Trajectory::f_AllocateData(string input3dfile)
{
    int nx, ny, nz;

	ifstream ifs(input3dfile);
	if(!ifs){
		return ALLOC_ERROR_CANNOT_OPEN_FILE;
	}
	string input((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
    vector<string> items;
    int nitems = separate_items(input, items);

    if(nitems < 7){
        return ALLOC_ERROR_DATA_NOT_FOUND;
    }
    for(int j = 0; j < 3; j++){
        m_dxyz[j] = atof(items[j].c_str());
        m_dxyz[j] *= 0.001; // mm -> m
        m_nxyz[j] = (int)atol(items[j+3].c_str());
		m_valrange[j] = m_nxyz[j]*m_dxyz[j]/2.0;
    }

    if(nitems < 3*m_nxyz[0]*m_nxyz[1]*m_nxyz[2]+6){
        return ALLOC_ERROR_MESH_INVALID;
    }

    for(int j = 0; j < 3; j++){
        m_Bxyz[j].resize(m_nxyz[0]);
        for(nx = 0; nx < m_nxyz[0]; nx++){
            m_Bxyz[j][nx].resize(m_nxyz[1]);
            for(ny = 0; ny < m_nxyz[1]; ny++){
                m_Bxyz[j][nx][ny].resize(m_nxyz[2], 0.0);
            }
        }
    }

    size_t nrep = 6;
    m_Bmax = 0.0;
    for(nx = 0; nx < m_nxyz[0]; nx++){
        for(ny = 0; ny < m_nxyz[1]; ny++){
            for(nz = 0; nz < m_nxyz[2]; nz++){
                for(int j = 0; j < 3; j++){
                    m_Bxyz[j][nx][ny][nz] = atof(items[nrep++].c_str());
                }
                m_Bmax = max(m_Bmax, sqrt(hypotsq(m_Bxyz[0][nx][ny][nz], m_Bxyz[1][nx][ny][nz])));
            }
        }
    }

    if(m_accuracy[accdisctra_] > 1){
        f_FinerStep();
    }

    m_status = FieldMapStatusDataAllocated;
	return 0;
}

void Trajectory::f_AdvanceOrbit(int iniindex, bool isps, bool killfocus, double cE, int step,
    double xyzin[] /* 0:x' 1:y' 2:x 3:y 4:rz */, double acc[], double Bexit[],
    double xyzout[])
{
    int i;
    double k1[5], k2[5], k3[5], k4[5], Btmp[3], xyztmp[5], dz;

    dz = (double)step*2.0*m_dxyz[2];

    // get the derivative at origin
    GetField(iniindex, isps, killfocus, xyzin, Btmp);
    get_EMF_variables(cE, xyzin, Btmp, k1);

    if((step > 0 && iniindex > m_nxyz[2]-2) ||
        (step < 0 && iniindex < 3)){ // final step: Euler method
        for(i = 0; i < 5; i++){
            xyzout[i] = xyzin[i]+dz*k1[i];
        }
        return;
    }

    // get the derivative at intermediate 1
    for(i = 0; i < 5; i++){
        xyztmp[i] = xyzin[i]+dz*k1[i]*0.5;
    }
    GetField(iniindex+step, isps, killfocus, xyztmp, Btmp);
    get_EMF_variables(cE, xyztmp, Btmp, k2);

    // get the derivative at intermediate 2
    for(i = 0; i < 5; i++){
        xyztmp[i] = xyzin[i]+dz*k2[i]*0.5;
    }
    GetField(iniindex+step, isps, killfocus, xyztmp, Btmp);
    get_EMF_variables(cE, xyztmp, Btmp, k3);

    // get the derivative at destination
    for(i = 0; i < 5; i++){
        xyztmp[i] = xyzin[i]+dz*k3[i];
    }
    GetField(iniindex+2*step, isps, killfocus, xyztmp, Bexit);
    get_EMF_variables(cE, xyztmp, Bexit, k4);
    acc[0] = k4[0]; acc[1] = k4[1];

    // get the orbit at destination
    for(i = 0; i < 5; i++){
        xyzout[i] = xyzin[i]+(k1[i]+2.0*k2[i]+2.0*k3[i]+k4[i])*dz/6.0;
    }
}

double Trajectory::f_AdditionalPhase(double zz, vector<vector<double>> &Drz)
{
    int jfin;
    double zb1[2], zb2[2], rzsum = 0.0, L1segH;

	L1segH = m_lu*m_N*0.5;

    for(int m = 1; m <= (m_issrc2?m_M:(m_M-1)); m++){
        if(m_issrc2){
            zb1[0] = m_zorg[m]+L1segH;
            zb2[0] = m_zorgS[m]-L1segH;
            if(m == m_M){
                jfin = 0;
            }
            else{
                jfin = 1;
                zb1[1] = m_zorgS[m]+L1segH;
                zb2[1] = m_zorg[m+1]-L1segH;
            }
        }
        else{
            zb1[0] = m_zorg[m]+L1segH;
            zb2[0] = m_zorg[m+1]-L1segH;
            jfin = 0;
        }
		for(int j = 0; j <= jfin; j++){
			if(zz > zb1[j] && zz < zb2[j]){
				if(zb2[j] <= zb1[j]){
					rzsum += Drz[j][m];
				}
				else{
					rzsum += Drz[j][m]/(zb2[j]-zb1[j])*(zz-zb1[j]);
				}
            }
            else if(zz >= zb2[j]){
                rzsum += Drz[j][m];
            }
        }
    }
    return rzsum;
}


double Trajectory::f_PhaseShifterField(double zz, vector<vector<double>> &Bpkps)
{
    int jfin;
    double bsum = 0.0, dz;

    for(int m = 1; m <= (m_issrc2?m_M:(m_M-1)); m++){
        jfin = (m_issrc2 && m < m_M) ? 1 : 0;
		for(int j = 0; j <= jfin; j++){
            dz = zz-m_zmid[j][m];
            if(fabs(dz) <= m_lu*0.25){
                bsum += Bpkps[j][m]*cos(dz*PI2/m_lu);
            }
			else if(fabs(dz) <= m_lu*0.75){
                bsum += Bpkps[j][m]*0.5*cos(dz*PI2/m_lu);
            }
        }
    }
    return bsum;
}

bool Trajectory::f_GetMatchingF(int jxy,
    int m, double z1, double z2, double *finv, double *beta0, double *alpha0)
{
    double betab[2], alphab[2], s[2], zorg[2], betaw, D;
    double beff, kurt, C, S, Cd, Sd, Lund, sa, sb, cs, sn;

    zorg[0] = f_GetSegmentOrigin(m);
    zorg[1] = f_GetSegmentOrigin(m+1);
    s[0] = z1-zorg[0]; s[1] = z2-zorg[1];

    for(int j = 0; j < 2; j++){
        if(m_isnatfoc[jxy]){
            beff = GetAverageFieldSquared(1-jxy, m_issrc2&&((m+j)%2==0));
                    // Bx,y works as y,x focusing
            kurt = 1.0e-9*CC*sqrt(beff)/m_acc[eGeV_];
            Lund = (double)m_N*m_lu;
        }
        betaw = m_betac[jxy][m+j]/(1.0+m_alphac[jxy][m+j]*m_alphac[jxy][m+j]);
        if(m_isnatfoc[jxy]){
            sa = Lund*0.5*(j==0?1.0:-1.0);
            sb = s[j]-sa;
            cs = cos(kurt*sa);
            sn = sin(kurt*sa);
            C = cs-sb*kurt*sn;
            S = sa*sinc(kurt*sa)+sb*cs;
            Cd = -kurt*sn;
            Sd = cs;
            betab[j] = C*C*m_betac[jxy][m+j]-2.0*S*C*m_alphac[jxy][m+j]+S*S/betaw;
            alphab[j] = -C*Cd*m_betac[jxy][m+j]+(Sd*C+S*Cd)*m_alphac[jxy][m+j]-S*Sd/betaw;
        }
        else{
            betab[j] = s[j]-m_alphac[jxy][m+j]*betaw;
            betab[j] = betaw+betab[j]*betab[j]/betaw;
            alphab[j] = m_alphac[jxy][m+j]-s[j]/betaw;
        }
    }
    D = betab[0]*betab[1]-m_Lmatch*m_Lmatch;
    if(D < 0){
        return false;
    }
    for(int j = 0; j < 2; j++){
        finv[j] = (sqrt(D)-betab[j]+(j==0?1.0:-1.0)*alphab[j]*m_Lmatch)/betab[j]/m_Lmatch;
    }

    if(beta0 != nullptr){
        s[0] = m_zorbit[m_nzorgorbit]-z1;
        alphab[0] = (betab[0]-sqrt(D))/m_Lmatch;
        betaw = betab[0]/(1.0+alphab[0]*alphab[0]);
        beta0[jxy] = (s[0]-alphab[0]*betaw);
        beta0[jxy] = beta0[jxy]*beta0[jxy]/betaw+betaw;
        alpha0[jxy] = alphab[0]-s[0]/betaw;
    }
	return true;
}

double Trajectory::f_GetSegmentOrigin(int m)
{
    double zorg;

    if(m_issrc2){
        if(m%2){
            zorg = m_zorg[(m+1)/2];
        }
        else{
            zorg = m_zorgS[m/2];
        }
    }
    else{
        zorg = m_zorg[m];
    }
    return zorg;
}

void Trajectory::f_CopyOrbitComponents(vector<vector<double>> *xyarr)
{
    if(xyarr->size() < 4){
        xyarr->resize(4);
    }
    for(int j = 0; j < 4; j++){
        if((*xyarr)[j].size() < m_ntotorbit){
            (*xyarr)[j].resize(m_ntotorbit);
        }
    }
    for(int n = 0; n < m_ntotorbit; n++){
        for(int j = 0; j < 2; j++){
            (*xyarr)[j][n] = m_orbit[n]._beta[j];
            (*xyarr)[j+2][n] = m_orbit[n]._xy[j];
        }
    }
}

double Trajectory::f_GetBfield(
	double z, double zorgbm, double bmlength, double B, bool rect)
{
	double by;
	z -= zorgbm;
	if(fabs(z) < bmlength*0.5){
		if(rect){
			by = B;
		}
		else{
			by = B*cos(PI*z/bmlength);
		}
	}
	else if(rect){
		if(m_src[fringelen_] < INFINITESIMAL){
			by = 0.0;
		}
		else{
			double tex = (fabs(z)-bmlength*0.5)/m_src[fringelen_];
			tex *= tex*0.5;
			if(tex > MAXIMUM_EXPONENT){
				by = 0.0;
			}
			else{
				by = B*exp(-tex);
			}
		}
	}
	else{
		by = 0.0;
	}
	return by;
}

void Trajectory::f_GetRecovFactor(double lu, int N, int nh, double *sigw, double *sigxy)
{
    double effdiv[2], divnat, signat;
    *sigxy = 0;
    for(int j = 0; j < 2; j++){
        double ediv = m_accb[zeroemitt_] ? 0 : 
            (m_calctype == "" ? m_div[j] : m_Esize[j]/m_conf[slit_dist_]);
        double eapt = m_slitapt[j]/m_conf[slit_dist_]/PI;
        effdiv[j] = sqrt(hypotsq(ediv, eapt));
        double Ktyp = sqrt(max(0.0, (m_GT[j]*m_GT[j]-1.0)*2.0));
        double sigtmp = 2.0*nh*Ktyp*m_gamma*effdiv[j]/(1+m_K2);
        *sigxy += 2.0*sigtmp*sigtmp;
    }
    if(*sigxy > MAXIMUM_EXPONENT){
        *sigxy = 0;
    }
    else{
        *sigxy = sqrt(2.0/(1.0+exp(*sigxy)));
    }
    natural_usrc(lu*N, wave_length(GetE1st()), &divnat, &signat);
    *sigw = nh*effdiv[0]*effdiv[1]/2.0/SQRTPI2/N/divnat/divnat;
}


