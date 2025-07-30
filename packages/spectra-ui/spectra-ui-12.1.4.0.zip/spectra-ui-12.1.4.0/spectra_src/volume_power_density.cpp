#include "volume_power_density.h"
#include "filter_operation.h"
#include "trajectory.h"

// files for debugging
string VolDensInteg;

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

VolumePowerDensity::VolumePowerDensity(
	SpectraSolver &spsolver, FilterOperation *filter)
	: SpectraSolver(spsolver)
{
#ifdef _DEBUG
//VolDensInteg = "..\\debug\\vol_dens_integ.dat";
#endif

	m_confsel[defobs_] = ObsPointDist;
	m_confv[erange_][0] = 0;

	Trajectory trajec(spsolver); // to assing m_Bmax, before spectrum calculations
	m_confv[erange_][1] = m_ecritical = trajec.GetCriticalEnergy()*(5+5*m_accuracy[acclimpE_]);

	if(m_isund){
		m_conf[de_] = GetE1st()/(m_N*m_M*(4+m_accuracy[accinpE_]));
	}
	else if(m_confb[wiggapprox_] ||
		m_iswiggler || m_srctype == BM || m_srctype == WLEN_SHIFTER){
		m_conf[emesh_] = 200*m_accuracy[accinpE_];
		m_confsel[estep_] = LinearLabel;
	}
	else{
		m_conf[de_] = m_conf[epitch_];
	}
	SetEnergyPoints();

	if(m_confsel[dstep_] == ArbPositionsLabel){
		m_depth.GetVariable(0, &m_darray);
	}
	else{
		double ddepth;
		bool islin = m_confsel[dstep_] == LinearLabel;
		int ndepth = (int)floor(m_conf[dmesh_]+0.5);
		m_darray.resize(ndepth);
		if(islin){
			ddepth = m_confv[drange_][1]-m_confv[drange_][0];
		}
		else{
			if(m_confv[drange_][0] <= 0){
				m_confv[drange_][0] = 0.001;
			}
			if(m_confv[drange_][1] <= 0){
				m_confv[drange_][1] = 10.0;
			}
			ddepth = log(m_confv[drange_][1]/m_confv[drange_][0]);
		}
		if(ndepth > 2){
			ddepth /= ndepth-1;
		}
		for(int n = 0; n < ndepth; n++){
			if(islin){
				m_darray[n] = m_confv[drange_][0]+n*ddepth;
			}
			else{
				m_darray[n] = m_confv[drange_][0]*exp(n*ddepth);
			}
		}
	}
	for(int j = 0; j < 2; j++){
		m_xyaccgl[j] = fabs(m_confv[qslitapt_][j]*m_conf[slit_dist_])*0.5;
		m_xyaccst[j] = -m_xyaccgl[j];
		// given in mm
	}
	m_absorber = new GenericAbsorber(m_absorbers, m_materials);
	m_filter = filter;
}

VolumePowerDensity::~VolumePowerDensity()
{
	delete m_absorber;
}

void VolumePowerDensity::AllocVolumePowerDensity(double leff,
	vector<vector<double>> &xyd,
	vector<vector<vector<double>>> &volpdens)
{
	int mesh[2] = {(int)xyd[0].size(), (int)xyd[1].size()};
	int nr[2], nrep;
	int totalmesh = mesh[0]*mesh[1];
    vector<vector<double>> flux;
	vector<double> ws, energy;
	double *pdensws, *pdensr;
	vector<string> dummy[2];

	double coef = QE*1000.0;
	if(m_isfar){
		coef /= m_conf[slit_dist_]*m_conf[slit_dist_];
	}
	pdensws = new double[m_darray.size()];
	pdensr = new double[m_darray.size()];
	m_calcstatus->SetSubstepNumber(0, (int)ceil((double)totalmesh/m_mpiprocesses));

	for(int nc = 0; nc < totalmesh; nc += m_mpiprocesses){
		bool isout = false;
		nrep = nc+m_rank;
		if(nrep >= totalmesh){
			isout = true;
		}
		else{
			nr[0] = nrep%mesh[0];
			nr[1] = nrep/mesh[0];
			for (int j = 0; j < 2; j++){
				m_confv[xyfix_][j] = xyd[j][nr[j]];
				double db = m_confv[xyfix_][j]/(1.0+EXP2AVOID_ROUNDING_ERROR);
				if (db > m_xyaccgl[j] || db < m_xyaccst[j]){
					isout = true;
					break;
				}
			}
		}
		if(isout){
			for (int n = 0; n < m_darray.size(); n++){
				pdensws[n] = 0.0;
			}
		}
		else{
			SetObservation();
			//f_SetEnergyRange();

			GetSpectrum(energy, flux, 1, 0, 1, dummy[0], dummy[1]);
			ws.resize(flux[0].size());
			if(m_isfilter){
				for(int n = 0; n < energy.size(); n++){
					flux[0][n] *= m_filter->GetTransmissionRateF(energy[n]);
				}
			}
			for (int n = 0; n < m_darray.size(); n++){
				pdensws[n] = coef*f_GetVolumePDSingle(
					m_darray[n], leff, energy, flux[0], ws);
			}
		}

		for(int nt = nc; nt < min(nc+m_mpiprocesses, totalmesh); nt++){
			int sendrank = nt%m_mpiprocesses;
			if(m_rank == sendrank){
				for (int n = 0; n < m_darray.size(); n++){
					pdensr[n] = pdensws[n];
				}
			}
			if(m_thread != nullptr){
				m_thread->Bcast(pdensr, (int)m_darray.size(), MPI_DOUBLE, sendrank, m_rank);
			}
			else{
				MPI_Bcast(pdensr, (int)m_darray.size(), MPI_DOUBLE, sendrank, MPI_COMM_WORLD);
				MPI_Barrier(MPI_COMM_WORLD);
			}
			nr[0] = nt%mesh[0];
			nr[1] = nt/mesh[0];
			for(int n = 0; n < (int)m_darray.size(); n++){
				volpdens[nr[0]][nr[1]][n] = pdensr[n];
			}
		}

		if(m_rank == 0){
			m_calcstatus->AdvanceStep(0);
		}
	}
	delete[] pdensws;
	delete[] pdensr;
}

void VolumePowerDensity::GetVolumePowerDensity(
	vector<vector<double>> &xyd, // given in mm
	vector<vector<vector<double>>> &volpdens)
{
	xyd.resize(3);
	xyd[2] = m_darray;

	double xyini, dxy[2], dummy;
	int mesh[2];
	for(int j = 0; j < 2; j++){
		GetGridContents(j, true, &xyini, &dxy[j], &dummy, &mesh[j]);
		xyd[j].resize(mesh[j]);
		for(int n = 0; n < mesh[j]; n++){
			xyd[j][n] = (xyini+dxy[j]*n)*1000.0; // m -> mm
			if (fabs(xyd[j][n]) < fabs(dxy[j])*DXY_LOWER_LIMIT){
				xyd[j][n] = 0.0;
			}
		}
	}
	volpdens.resize(mesh[0]);
	for(int n = 0; n < mesh[0]; n++){
		volpdens[n].resize(mesh[1]);
		for (int m = 0; m < mesh[1]; m++){
			volpdens[n][m].resize(m_darray.size());
		}
	}

	m_Theta = m_conf[Qgl_]*DEGREE2RADIAN;
	m_Phi = m_conf[Phiinc_]*DEGREE2RADIAN;
	if(fabs(cos(m_Theta)) < 0.001){// normal incidence
		AllocVolumePowerDensity(1.0, xyd, volpdens);
		return;
	}

	vector<vector<double>> xyde(3);
	vector<vector<vector<double>>> volpde;
	double xybm[2], xytgt[2];

	double ltan = 1.0/tan(m_Theta);
	double prjxy[2], xytini[2], xytfin[2], xyinibm[2], xyfinbm[2];
	prjxy[0] = m_darray.back()*ltan*cos(m_Phi);
	prjxy[1] = m_darray.back()*ltan*sin(m_Phi);
	for(int j = 0; j < 2; j++){ 
		// area to cover the whole area exposed to radiation
		xytini[j] = min(xyd[j].front(), xyd[j].back());
		xytfin[j] = max(xyd[j].front(), xyd[j].back());
		if(prjxy[j] < 0){
			xytini[j] += prjxy[j];
		}
		else{
			xytfin[j] += prjxy[j];
		}
	}
	f_GetBeamCorrdinate(xytini, xyinibm);
	f_GetBeamCorrdinate(xytfin, xyfinbm);
	for(int j = 0; j < 2; j++){
		m_xyaccst[j] = max(xyinibm[j], m_xyaccst[j]);
		m_xyaccgl[j] = min(xyfinbm[j], m_xyaccgl[j]);
	}

	f_GetBeamCorrdinate(dxy, m_dxybm);
	for(int j = 0; j < 2; j++){
		double accst = m_xyaccgl[j]-m_xyaccst[j];
		double pdiv = m_GT[j]/m_gamma*m_conf[slit_dist_]/(3+m_accuracy[accinobs_]);
		m_dxybm[j] = min(pdiv, m_dxybm[j]);
		m_dxybm[j] *= 1000.0; // m -> mm
 		m_meshbm[j] = max(5, (int)ceil(accst/m_dxybm[j]));
		m_dxybm[j] = accst/(m_meshbm[j]-1);
		xyde[j].resize(m_meshbm[j]);
		for(int n = 0; n < m_meshbm[j]; n++){
			xyde[j][n] = (m_xyaccst[j]+n*m_dxybm[j]); // given in mm
		}
	}
	xyde[2] = m_darray;
	volpde.resize(m_meshbm[0]);
	for(int n = 0; n < m_meshbm[0]; n++){
		volpde[n].resize(m_meshbm[1]);
		for (int m = 0; m < m_meshbm[1]; m++){
			volpde[n][m].resize(m_darray.size());
		}
	}
	double leff = 1.0/sin(m_Theta);
	AllocVolumePowerDensity(leff, xyde, volpde);

	for(int d = 0; d < m_darray.size(); d++){
		for (int n = 0; n < mesh[0]; n++){
			xytgt[0] = xyd[0][n]+m_darray[d]*leff*cos(m_Theta)*cos(m_Phi);
			for (int m = 0; m < mesh[1]; m++){
				xytgt[1] = xyd[1][m]+m_darray[d]*leff*cos(m_Theta)*sin(m_Phi);
				f_GetBeamCorrdinate(xytgt, xybm);
				// xybm given in mm
				volpdens[n][m][d] = f_Interpolate(d, xybm, xyde, volpde);
			}
		}
	}
}

double VolumePowerDensity::f_Interpolate(int d, double xybm[], 
	vector<vector<double>> &xyde, vector<vector<vector<double>>> &volpde)
{
	int index[2];
	double dresxy[4];
	bool isin = get_2d_matrix_indices(xybm, nullptr, 
		m_xyaccst, m_dxybm, m_meshbm, index, dresxy);

	if(!isin){
		return 0;
	}
	double dens = 
		  volpde[index[0]  ][index[1]  ][d]*dresxy[0]
		+ volpde[index[0]+1][index[1]  ][d]*dresxy[1]
		+ volpde[index[0]  ][index[1]+1][d]*dresxy[2]
		+ volpde[index[0]+1][index[1]+1][d]*dresxy[3];
	return dens;
}

double VolumePowerDensity::f_GetVolumePDSingle(double depth, double leff,
		vector<double> &energy, vector<double> &flux, vector<double> &ws)
{
	double reldepth, pd, de;
	de = energy[1]-energy[0];

#ifdef _DEBUG
	ofstream debug_out;
	if(!VolDensInteg.empty()){
		debug_out.open(VolDensInteg);
	}
	vector<double> items(2);
#endif

	int tgtlayer;
	tgtlayer = m_absorber->GetTargetLayer(depth, &reldepth);
	for(int n = 0; n < energy.size(); n++){
		ws[n] = m_absorber->GetAbsorption(tgtlayer, reldepth, energy[n], &leff)*flux[n];
#ifdef _DEBUG
		items[0] = flux[n];
		items[1] = ws[n];
		PrintDebugItems(debug_out, energy[n], items);
#endif
	}
	pd = simple_integration((int)energy.size(), de, ws);

#ifdef _DEBUG
	debug_out.close();
#endif

	return pd;
}

void VolumePowerDensity::f_GetBeamCorrdinate(double xytgt[], double xybeam[])
{
	double csn[3] = {cos(m_Phi), sin(m_Phi), 0}, conv[3];
	csn[2] = csn[0]*csn[1];
	for(int j = 0; j < 2; j++){
		csn[j] *= csn[j];
	}
	double sef = sin(m_Theta);
	conv[0] = csn[1]+sef*csn[0];
	conv[1] = csn[2]*(sef-1.0);
	conv[2] = csn[0]+sef*csn[1];
	xybeam[0] = xytgt[0]*conv[0]+xytgt[1]*conv[1];
	xybeam[1] = xytgt[0]*conv[1]+xytgt[1]*conv[2];
}

void VolumePowerDensity::f_SetEnergyRange()
{
	vector<string> dummy[2];
	vector<double> energy;
	vector<vector<double>> flux;
	double eps = 1e-4/(1<<(m_accuracy[acclimpE_]-1));

	bool ebmz[3] = {m_accb[zeroemitt_], m_accb[zerosprd_], m_confb[wiggapprox_]};
	
	m_accb[zeroemitt_] = m_accb[zerosprd_] = m_confb[wiggapprox_] = true;
	m_confv[erange_][1] = m_ecritical;

	GetSpectrum(energy, flux, 1, 0, 1, dummy[0], dummy[1]);

	double fmax = flux[0][0]+flux[1][0], fr;
	for(int n = 1; n < energy.size(); n++){
		fmax = max(flux[0][n]+flux[1][n], fmax);
	}
	int nr = (int)energy.size();
	do{
		nr--;
		fr = flux[0][nr]+flux[1][nr];		
	}while(fr < fmax*eps);

	m_confv[erange_][1] = energy[nr];

	m_accb[zeroemitt_] = ebmz[0]; m_accb[zerosprd_] = ebmz[1]; m_confb[wiggapprox_] = ebmz[2];
}
