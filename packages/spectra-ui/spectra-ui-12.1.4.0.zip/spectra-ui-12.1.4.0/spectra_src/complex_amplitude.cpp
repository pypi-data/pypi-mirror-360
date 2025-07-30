#include "flux_density.h"
#include "complex_amplitude.h"
#include "undulator_fxy_far.h"
#include "trajectory.h"
#include "filter_operation.h"
#include "common.h"

#ifdef __NOMPI__
#include "mpi_dummy.h"
#else
#include "mpi.h"
#endif

// files for debugging
string CampAlongTheta;
string CampCheckXY;
string CampCheckXYPart;
string UfieldCheckXY;
string UfieldCheckSn;
string WfieldCheckXY;
string BfieldCheckXY;
string AllocAlongTheta;

#define MAXARGK1312 10.0
#define MAXARGSINC 30.0
#define ANGLEINTERVAL 0.05

ComplexAmplitude::ComplexAmplitude(SpectraSolver &spsolver)
		: SpectraSolver(spsolver)
{
#ifdef _DEBUG
//CampAlongTheta  = "..\\debug\\camp_along_theta.dat";
//CampCheckXY  = "..\\debug\\camp_check_xy.dat";
//CampCheckXYPart  = "..\\debug\\camp_check_xy_part.dat";
//UfieldCheckXY  = "..\\debug\\ufield_check_xy.dat";
//UfieldCheckSn  = "..\\debug\\ufield_check_sn.dat";
//WfieldCheckXY  = "..\\debug\\wfield_check_xy.dat";
//BfieldCheckXY  = "..\\debug\\bfield_check_xy.dat";
// AllocAlongTheta = "..\\debug\\alloc_along_theta.dat";
#endif

	double epmin, epsilon = 1.0;
	if(m_isund){
		m_isidealund = 
			!m_srcb[fielderr_]  && 
			!m_srcb[phaseerr_] && 
			m_srcsel[segment_type_] == NoneLabel && 
			m_srcsel[natfocus_] == NoneLabel;
	    if(m_isf8){
		    m_nh = (int)floor(2.0*m_conf[hfix_]+0.5);
	    }
		else{
	        m_nh = (int)floor(m_conf[hfix_]+0.5);
		}
		double e1st = GetE1st();
		m_eptarget = e1st*(1.0+m_conf[detune_])*m_nh;
		if(m_isenergy){
			epmin = min(m_confv[erange_][0], m_confv[erange_][1]);
		}
		else{
			epmin = m_eptarget;
		}
		epsilon = (epmin/(double)m_nh/e1st-1.0)*(double)(m_N*m_nh);
	}
	else{
		m_isidealund = false;
	}
	if(m_isbm){
		m_isidealbm = !m_srcb[bmtandem_];
	}
	else{
		m_isidealbm = false;
	}

	m_dUmin = 0;
	for(int j = 0; j < 2; j++){
		m_poffsetXY[j] = m_poffsetUV[j] = 
			m_XYsrcpoint[j] = m_UVsrcpoint[j] = 0;
	}
	m_noidealsrc = false;
	m_ismontecarlo = IsMonteCarlo();
	m_netarget = 0;
	if(m_isidealund){
		m_epnorm = m_nh*GetE1st();
		double divxy[2], sizexy[2];
		GetNaturalSrcDivSize(m_epnorm, divxy, sizexy);
		m_dqduv = 2.0*divxy[0];
		m_dXYdUV = sizexy[0];
		m_coefExy = (double)m_N/wave_length(m_epnorm)/m_gamma2;
		f_AssignEFieldUnd(epsilon, !m_isenergy);
	}
	else if(m_isidealbm || m_iswiggler){
		m_ecritical = GetCriticalEnergy();
		Prepare(m_fixep);
	}
	else{
		m_noidealsrc = true;
		m_dqduv = 1.0/m_gamma;
		m_coefExy = 1.0/m_gamma;

		double thetamax;
		if(m_isund){
			double gt2uv, hDelta;
			thetamax = f_GTmaxU(epsilon, &gt2uv, &hDelta);
			double lim1_5th = sqrt((1.0+m_K2)*0.5);
			thetamax = min(thetamax, lim1_5th); 
			// limit the acceptance within 1.5 x E1st (avoid contamination by 2nd)
		}
		else{
			thetamax = max(m_confv[gtacc_][0], m_confv[gtacc_][1]);
		}
		thetamax /= m_gamma;

		Trajectory trajectory(spsolver);
		FilterOperation filter(spsolver);
		FluxDensity fluxdens(spsolver, &trajectory, &filter);

		if(m_accsel[injectionebm_] != AutomaticLabel){
			trajectory.GetOriginXY(m_XYsrcpoint);
		}

		if(IsMonteCarlo()){
			m_calcstatus->SetTargetPoint(0, 0.02);
			// 2% is completed by this process
		}
		else{
			m_calcstatus->SetTargetPoint(0, 0.05);
			// 5% is completed by this process
		}
		vector<vector<int>> secidx;
		try {
			if (trajectory.GetZsection(secidx) > 0){
				f_CreateDataSet(thetamax, m_accuracy[accinobs_], &fluxdens, &secidx, m_calcstatus, 0);
			}
			else{
				f_CreateDataSet(thetamax, m_accuracy[accinobs_], &fluxdens, nullptr, m_calcstatus, 0);
			}
		}
		catch (const exception&){
			throw runtime_error("Not enough memoery");
		}
		m_calcstatus->SetCurrentOrigin(0);
		m_calcstatus->ResetCurrentStep(0);
		m_calcstatus->SetTargetPoint(0, 1.0);
		Prepare(m_fixep);
	}
}

void ComplexAmplitude::GetEbeam4Wigner(
	double sigmauv[], double sigmaUV[], double alpha[], bool negdiv)
{
	double betaw, sxy2, spxy2, eta2, etad2;
	for(int j = 0; j < 2; j++){
		if(negdiv){
			betaw = m_accv[beta_][j];
		}
		else{
			betaw = m_accv[beta_][j]/(1.0+m_accv[alpha_][j]*m_accv[alpha_][j]);
		}
		eta2 = EnergySpreadSigma()*m_accv[eta_][j]; eta2 *= eta2;
		etad2 = EnergySpreadSigma()*m_accv[etap_][j]; etad2 *= etad2;
		if(m_accb[zeroemitt_]){
			sxy2 = spxy2 = 0;
		}
		else{
			sxy2 = m_emitt[j]*betaw+eta2;
			spxy2 = m_emitt[j]/betaw+etad2;
		}
		if(negdiv){
			sigmauv[j] = 0.0;
		}
		else{
			sigmauv[j] = sqrt(spxy2)/m_dqduv;
		}
		sigmaUV[j] = sqrt(sxy2)/m_dXYdUV;
		if(m_accb[zeroemitt_] || negdiv){
			alpha[j] = 0;
		}
		else{
			alpha[j] = m_accv[alpha_][j]*m_emitt[j]/spxy2*m_dqduv/m_dXYdUV;
		}
	}
	if(negdiv){
		sigmaUV[0] = max(sigmaUV[0], m_dUmin);

	}
	else if(contains(m_calctype, menu::wigner) && (m_isbm || m_iswiggler)){
		int smlevel = (int)floor(0.5+m_conf[xsmooth_]);
		sigmaUV[0] = max(sigmaUV[0], m_dUmin*(double)(1<<(smlevel-1)));
	}
}

void ComplexAmplitude::Prepare(double ep)
{
	double epsilon;
	if(m_isidealund){
		m_eptarget = ep;
		// m_dqduv & m_dXYdUV specific to harmonic and periodic numbers
		double e1st = GetE1st();
		epsilon = (ep/(double)m_nh/e1st-1.0)*(double)(m_N*m_nh);
		double gt2uv, hDelta;
		f_GTmaxU(epsilon, &gt2uv, &hDelta);
		f_AssignSn(hDelta, epsilon);
	}
	else if(m_isidealbm || m_iswiggler){
		m_eptarget = m_epnorm = ep;
		epsilon = GetEpsilonBMWiggler(ep);
		double deltau = m_conf[horizacc_]*1.0e-3*m_gamma*epsilon;
		m_dqduv = 1.0/(epsilon*m_gamma);
		m_coefExy = 2.0/sqrt(3.0)/PI*epsilon;
		if(m_iswiggler){
			m_eKwiggler = epsilon*m_Kxy[1][1];
			double ke = m_Kxy[1][1];
			deltau = min(deltau, 2.0*ke*epsilon);
			double amp = ke*m_lu/PI2/m_gamma;
			ke *= epsilon;
			ke *= ke;
			m_dXYdUV = amp/ke/2.0;
			f_AssignEFieldWiggler(epsilon, deltau, true);
			m_dUmin = ke/4.0;
			m_UVsrcpoint[0] = -2.0*m_eKwiggler*m_eKwiggler;
			m_XYsrcpoint[0] = m_UVsrcpoint[0]*m_dXYdUV;
		}
		else{
			double bendr = GetOrbitRadius();
			m_dXYdUV = bendr*0.5*m_dqduv*m_dqduv;
			f_AssignEFieldBM(epsilon, deltau);
			m_dUmin = 1.0;
		}
	}
	else{
		m_ecurrtarget = m_eptarget = m_epnorm = ep;
		m_dXYdUV = wave_length(ep)*m_gamma/PI2;
		for(int j = 0; j < 2; j++){
			m_UVsrcpoint[j] = m_XYsrcpoint[j]/m_dXYdUV;
		}
	}
}

double ComplexAmplitude::GetWDFCoef()
{
	double coefWDF = m_gamma/wave_length(m_epnorm);
	coefWDF *= coefWDF;
	coefWDF *= COEF_ALPHA/1.0E+15*m_AvCurr/QE; 
		// /m^2/rad^2/100%BW -> /mm^2/mrad^2/0.1%BW
	return coefWDF;
}

void ComplexAmplitude::GetEnergyArray(vector<double> &eparray)
{
	eparray = m_eparray;
}

double ComplexAmplitude::Function4Digitizer(double theta, vector<double> *exy)
{
	if(theta == 0){
		*exy = m_ExyAxis;
	}
	else{
		double qobs[2] = { theta*m_csn[0], theta*m_csn[1] };
		m_fluxdens->GetFluxItemsAt(qobs, exy, true, nullptr, m_XYsrcpoint);
		*exy *= m_coefExy;
	}
	return (*exy)[m_necenter+m_tgtitem*m_ndata];
}

void ComplexAmplitude::GetSnPrms(int *N, int *nh, double *Ueps)
{
	*N = m_N;
	*nh = m_nh;
	*Ueps = m_Uepsilon;
}

void ComplexAmplitude::GetUVSrcPoints(double srcpoints[])
{
	for(int j = 0; j < 2; j++){
		srcpoints[j] = m_UVsrcpoint[j]+m_poffsetUV[j];
	}
}

bool ComplexAmplitude::GetExyAmplitude(double uv[], double Exy[])
{
	if(m_noidealsrc){
		if(m_avgorbits.size() > 0){ 
			// Monte Carlo, particle energy should be considered
			if(m_eparray.size() == 1){
				f_GetAmplitudeNIParticle(0, uv, m_avgorbits, Exy);
				return true;
			}
			double Etmp[2][4];
			double epred = m_ecurrtarget/m_eparticle/m_eparticle;
			if(epred < m_eparray[0] || epred > m_eparray[m_ndata-1]){
				return false;
			}
			int netarget = SearchIndex(m_ndata, true, m_eparray, epred);
			for(int i = 0; i < 2; i++){
				f_GetAmplitudeNIParticle(netarget+i, uv, m_avgorbits, Etmp[i]);
			}
			for(int j = 0; j < 4; j++){
				Exy[j] = lininterp(epred, 
					m_eparray[netarget], m_eparray[netarget+1], Etmp[0][j], Etmp[1][j]);
			}
			return true;
		}
		return f_GetAmplitudeNI(m_netarget, uv, Exy);
	}

	int index[2];
	double dresxy[4];

	if(!get_2d_matrix_indices(uv, m_valrange, nullptr, m_delta, m_mesh, index, dresxy)){
		for (int j = 0; j < 4; j++){
			Exy[j] = 0;
		}
		return false;
	}

	for(int j = 0; j < 4; j++){
		Exy[j] = 
		  m_Exy[j][index[0]  ][index[1]  ]*dresxy[0]
		+ m_Exy[j][index[0]+1][index[1]  ]*dresxy[1]
		+ m_Exy[j][index[0]  ][index[1]+1]*dresxy[2]
		+ m_Exy[j][index[0]+1][index[1]+1]*dresxy[3];
	}
	return true;
}

double ComplexAmplitude::GetOmegaWiggler(double index, double polarity)
{
	double dix = (-(double)(m_N-1)*0.5+index)*polarity+0.25;
	if(m_isoddpole){
		dix += polarity*0.25;
	}

	return -dix*PI2*2.0*m_eKwiggler;
}

double ComplexAmplitude::GetAprofPrms(int amesh[], double adelta[])
{
	for(int j = 0; j < 2; j++){
		amesh[j] = m_amesh[j];
		adelta[j] = m_adelta[j];
	}
	return m_aflux;
}

void ComplexAmplitude::GetRangePrms(double hrange[], double dinterv[])
{
	for(int j = 0; j < 2; j++){
		hrange[j] = m_halfrange[j];
		dinterv[j] = m_dinterv[j];
	}
}

double ComplexAmplitude::GetSn(double u[], double v[])
{
	int index[2];
	double dresxy[4], w[2], res;

	for(int j = 0; j < 2; j++){
		w[j] = hypotsq(u[j], v[j])*(1.0+m_Uepsilon/(double)(m_N*m_nh))+m_Uepsilon;
	}
	w[1] -= w[0];

	if(!get_2d_matrix_indices(w, m_valrangesn, nullptr, m_deltasn, m_snmesh, index, dresxy)){
		return 0.0;
	}
	res = m_Sn[index[0]  ][index[1]  ]*dresxy[0]
		+ m_Sn[index[0]+1][index[1]  ]*dresxy[1]
		+ m_Sn[index[0]  ][index[1]+1]*dresxy[2]
		+ m_Sn[index[0]+1][index[1]+1]*dresxy[3];

	return res;
}

void ComplexAmplitude::UpdateParticle(Trajectory *trajec, double edev)
{
	trajec->GetAvgOrbits(m_avgorbits);
	m_eparticle = 1.0+edev;
	int norb = (int)m_avgorbits.size();
	for(int j = 0; j < 2; j++){
		m_poffsetXY[j] = 0;
		for(int n = 0; n < norb; n++){
			m_poffsetXY[j] += m_avgorbits[n]._xy[j];
		}
		m_poffsetXY[j] /= norb;
		m_poffsetUV[j] = m_poffsetXY[j]/m_dXYdUV;
	}
}

double ComplexAmplitude::GetSrcPointCoef()
{
	double dqduv = m_dqduv;
	dqduv *= dqduv;
	return GetWDFCoef()*1.0e+6*dqduv*dqduv;
	// /mm^2/mrad^2/100%BW -> /mm^2/rad^2/0.1%BW
}

// private functions
void ComplexAmplitude::f_CreateDataSet(
	double thetamax, int acclevel, FluxDensity *fluxdens, vector<vector<int>> *secidx,
	PrintCalculationStatus *status, int targetlayer)
{
	m_fluxdens = fluxdens;
	m_ndivphi = 12+4*acclevel;
	m_fluxdens->GetEnergyArray(m_eparray);
	m_ndata = (int)m_eparray.size();
	m_netarget = 0;

	m_necenter = (m_ndata-1)/2;
	if(!m_isenergy){
		m_ecurrtarget = m_fixep;
	}
	else{
		m_ecurrtarget = m_eparray[m_necenter];
	}
	AllocateMemoryFuncDigitizer(4*m_ndata);

	m_theta.resize(m_ndivphi);
	m_ExyR.resize(m_ndivphi);
	m_nqpoints.resize(m_ndivphi);

	double phi;
	double xrange[NumberFStepXrange] = {0.0, 0.0, thetamax, 0.0, thetamax*1.0e-4};
	int ninit = 50*acclevel+1;
	if(m_M > 1){
		ninit = (int)ceil(ninit*sqrt((double)m_M));		
	}
	double epsval[2] = {0.1/acclevel, 0};

	double axis[2] = {0, 0};
	m_ExyAxis.resize(4*m_ndata);
	m_fluxdens->GetFluxItemsAt(axis, &m_ExyAxis, true, nullptr, m_XYsrcpoint);
	m_ExyAxis *= m_coefExy;

	m_tgtitem = 0;
	double emax = fabs(m_ExyAxis[m_necenter]);
	double rmax;
	for(int j = 1; j < 4; j++){
		rmax = fabs(m_ExyAxis[m_necenter+j*m_ndata]);
		if(rmax > emax){
			m_tgtitem = j;
			emax = rmax;
		}
	}

	m_dphi = PI2/m_ndivphi;
	int nsection = 1;
	if(secidx == nullptr){
		status->SetSubstepNumber(targetlayer, m_ndivphi/m_mpiprocesses);
	}
	else{
		nsection = (int)(*secidx)[0].size();
		status->SetSubstepNumber(targetlayer, m_ndivphi*(nsection+1)/m_mpiprocesses);
	}

	vector<int> mpisteps, mpiinistep, mpifinstep;
	mpi_steps(m_ndivphi, 1, m_mpiprocesses, &mpisteps, &mpiinistep, &mpifinstep);

	for(int n = 0; n < m_ndivphi; n++){
		if(n < mpiinistep[m_rank] || n > mpifinstep[m_rank]){
			continue;
		}
		phi = m_dphi*n;
		m_csn[0] = cos(phi);
		m_csn[1] = sin(phi);

		m_nqpoints[n] = 
			RunDigitizer(FUNC_DIGIT_BASE, &m_theta[n], &m_ExyR[n], xrange, ninit, epsval,
				status, targetlayer+1, AllocAlongTheta, nullptr, false);

#ifdef _DEBUG
		if (!CampAlongTheta.empty()){
			ofstream debug_out(CampAlongTheta);
			vector<vector<double>> ws(4);
			for(int j = 0; j < 4; j++){
				ws[j].resize(m_nqpoints[n]);
				for(int m = 0; m < m_nqpoints[n]; m++){
					ws[j][m] = m_ExyR[n][m_necenter+j*m_ndata][m];
				}
			}
			PrintDebugRows(debug_out, m_theta[n], ws, m_nqpoints[n]);
			debug_out.close();
		}
#endif
		status->AdvanceStep(targetlayer);
	}

	if(m_mpiprocesses > 1){
		f_MPI_Bcast_Exy(true, mpiinistep, mpifinstep, m_ExyR);
	}

	int meshmax = minmax(m_nqpoints, true);
	double delmin = thetamax/m_dqduv/meshmax;
	meshmax = 2*meshmax+1;

	int mesh[2] = {meshmax, meshmax};
	double delta[2] = {delmin, delmin};
	f_AssignGridConditions(mesh, delta, nullptr, nullptr);

#ifdef _DEBUG
	int hpoints = m_nqpoints[0];
	if (m_rank == 0 && !CampCheckXY.empty()){
		double dtheta = thetamax/hpoints*0.5;
		double thetac[2], Exyc[4], uv[2];
		vector<double> wsd(5);
		ofstream debug_out(CampCheckXY);
		for(int n = -hpoints; n <= hpoints; n++){
			thetac[0] = n*dtheta;
			uv[0] = thetac[0]/m_dqduv;
			for (int m = -hpoints; m <= hpoints; m++){
				thetac[1] = m*dtheta;
				uv[1] = thetac[1]/m_dqduv;
				f_GetAmplitudeNI(0, uv, Exyc);
				wsd[0] = thetac[1];
				for(int j = 0; j < 4; j++){
					wsd[j+1] = Exyc[j];
				}
				PrintDebugItems(debug_out, thetac[0], wsd);
			}
		}
	}
#endif
	if(secidx == nullptr){
		return;
	}
	m_GxyAxis.resize(nsection);
	m_GxyR.resize(nsection);

	int zrange[2];
	double qobs[2];
	int nfd = m_fluxdens->GetEnergyMesh();
	vector<double> ws(4*nfd);

	for(int ns = 0; ns < nsection; ns++){
		for(int j = 0; j < 2; j++){
			zrange[j] = (*secidx)[j][ns];
		}
		m_GxyAxis[ns].resize(4*m_ndata);
		m_fluxdens->GetFluxItemsAt(axis, &m_GxyAxis[ns], true, zrange, m_XYsrcpoint);
		m_GxyAxis[ns] *= m_coefExy;
		m_GxyR[ns].resize(m_ndivphi);
		for (int n = 0; n < m_ndivphi; n++){
			m_GxyR[ns][n].resize(4*nfd);
			for(int k = 0; k < 4*nfd; k++){
				m_GxyR[ns][n][k].resize(m_nqpoints[n], 0.0);
			}
			if (n < mpiinistep[m_rank] || n > mpifinstep[m_rank]){
				continue;
			}
			phi = m_dphi*n;
			m_csn[0] = cos(phi);
			m_csn[1] = sin(phi);
			for(int m = 0; m < m_nqpoints[n]; m++){
				if(m_theta[n][m] == 0){
					for (int k = 0; k < 4*nfd; k++){
						m_GxyR[ns][n][k][m] = m_GxyAxis[ns][k];
					}
					continue;
				}
				for(int j = 0; j < 2; j++){
					qobs[j] = m_theta[n][m]*m_csn[j];
				}
				m_fluxdens->GetFluxItemsAt(qobs, &ws, true, zrange, m_XYsrcpoint);
				for (int k = 0; k < 4*nfd; k++){
					m_GxyR[ns][n][k][m] = m_coefExy*ws[k];
				}
			}
			status->AdvanceStep(targetlayer);
		}
		if (m_mpiprocesses > 1){
			f_MPI_Bcast_Exy(false, mpiinistep, mpifinstep, m_GxyR[ns]);
		}
	}

#ifdef _DEBUG
	if (m_rank == 0 && !CampCheckXYPart.empty()){
		double dtheta = thetamax/hpoints*0.5;
		double thetac[2], Exyc[4], uv[2];
		vector<double> wsd(5);
		vector<OrbitComponents> orbits(nsection);
		ofstream debug_out(CampCheckXYPart);
		for(int n = -hpoints; n <= hpoints; n++){
			thetac[0] = n*dtheta;
			uv[0] = thetac[0]/m_dqduv;
			for (int m = -hpoints; m <= hpoints; m++){
				thetac[1] = m*dtheta;
				uv[1] = thetac[1]/m_dqduv;
				f_GetAmplitudeNIParticle(0, uv, orbits, Exyc);
				wsd[0] = thetac[1];
				for(int j = 0; j < 4; j++){
					wsd[j+1] = Exyc[j];
				}
				PrintDebugItems(debug_out, thetac[0], wsd);
			}
		}
	}
#endif
}

void ComplexAmplitude::f_MPI_Bcast_Exy(bool istheta,
	vector<int> &mpiinistep, vector<int> &mpifinstep, vector<vector<vector<double>>> &exy)
{
	MPI_Barrier(MPI_COMM_WORLD);
	int qpmax = 0;
	for(int m = 0; m < m_mpiprocesses; m++){
		for(int n = mpiinistep[m]; n <= mpifinstep[m]; n++){
			if(istheta){
				if(m_thread != nullptr){
					m_thread->Bcast(&m_nqpoints[n], 1, MPI_INT, m, m_rank);
				}
				else{
					MPI_Bcast(&m_nqpoints[n], 1, MPI_INT, m, MPI_COMM_WORLD);
				}
			}
			qpmax = max(qpmax, m_nqpoints[n]);
		}
	}
	double *qws = new double[qpmax*4*m_ndata];
	double *theta = nullptr;
	if(istheta){
		theta = new double[qpmax];
	}
	for(int m = 0; m < m_mpiprocesses; m++){
		for(int n = mpiinistep[m]; n <= mpifinstep[m]; n++){
			if(m == m_rank){
				for(int k = 0; k < 4*m_ndata; k++){
					for (int i = 0; i < m_nqpoints[n]; i++){
						qws[k*m_nqpoints[n]+i] = exy[n][k][i];
					}
				}
				if(istheta){
					for (int i = 0; i < m_nqpoints[n]; i++){
						theta[i] = m_theta[n][i];
					}
				}
			}
			if(m_thread != nullptr){
				m_thread->Bcast(qws, m_nqpoints[n]*4*m_ndata, MPI_DOUBLE, m, m_rank);
				if(istheta){
					m_thread->Bcast(theta, m_nqpoints[n], MPI_DOUBLE, m, m_rank);
				}
			}
			else{
				MPI_Bcast(qws, m_nqpoints[n]*4*m_ndata, MPI_DOUBLE, m, MPI_COMM_WORLD);
				if(istheta){
					MPI_Bcast(theta, m_nqpoints[n], MPI_DOUBLE, m, MPI_COMM_WORLD);
				}
			}
			if(m != m_rank){
				exy[n].resize(4*m_ndata);
				for(int k = 0; k < 4*m_ndata; k++){
					exy[n][k].resize(m_nqpoints[n]);
					for (int i = 0; i < m_nqpoints[n]; i++){
						exy[n][k][i] = qws[k*m_nqpoints[n]+i];
					}
				}
				if(istheta){
					m_theta[n].resize(m_nqpoints[n]);
					for (int i = 0; i < m_nqpoints[n]; i++){
						m_theta[n][i] = theta[i];
					}
				}
			}
		}
	}
	delete[] qws;
	if(istheta){
		delete[] theta;
	}
}


bool ComplexAmplitude::f_GetAmplitudeNIParticle(int ne, double uv[], 
	vector<OrbitComponents> &orbits, double Exy[])
{
	double Exytmp[4], Exypr[2], uvtmp[2], csn[2], phs;
	bool isval = false;

	double knumber = PI2/wave_length(m_eparray[ne]);
	for(int j = 0; j < 4; j++){
		Exy[j] = 0;
	}
	for(int nsec = 0; nsec < orbits.size(); nsec++){
		for (int j = 0; j < 2; j++){
			uvtmp[j] = uv[j]-orbits[nsec]._beta[j]/m_dqduv;
		}
		if(!f_GetAmplitudeNI(ne, uvtmp, Exytmp, nsec)){
			continue;
		}
		for (int j = 0; j < 2; j++){
			phs = -knumber*uv[j]*m_dqduv*
				(orbits[nsec]._xy[j]-m_poffsetXY[j]);
			csn[0] = cos(phs);
			csn[1] = sin(phs);
			complex_product(Exytmp+2*j, csn, Exypr);
			Exy[2*j] += Exypr[0];
			Exy[2*j+1] += Exypr[1];
		}
		isval = true;
	}
	return isval;
}

bool ComplexAmplitude::f_GetAmplitudeNI(int ne, double uv[], double Exy[], int nsec)
{
	double thetar = sqrt(hypotsq(uv[0], uv[1]))*m_dqduv;
	if(thetar == 0){
		for(int j = 0; j < 4; j++){
			if(nsec < 0){
				Exy[j] = m_ExyAxis[ne+j*m_ndata];
			}
			else{
				Exy[j] = m_GxyAxis[nsec][ne+j*m_ndata];
			}
		}
		return true;
	}
	double phir = atan2(uv[1], uv[0]), phi[2];
	if(phir < 0){
		phir += PI2;
	}
	int nphi = (int)floor(phir/m_dphi), np[2], nt[2];

	for(int n = 0; n < 2; n++){
		np[n] = nphi+n;
		phi[n] = m_dphi*np[n];
		if(np[n] >= m_ndivphi){
			np[n] = 0;
		}
		if(thetar > m_theta[np[n]][m_nqpoints[np[n]]-1]){
			for (int j = 0; j < 4; j++){
				Exy[j] = 0.0;
			}
			return false;
		}
		nt[n] = SearchIndex(m_nqpoints[np[n]], false, m_theta[np[n]], thetar);
	}

	double ews[2], ewr[2];
	for(int j = 0; j < 4; j++){
		for (int n = 0; n < 2; n++){
			for (int m = 0; m < 2; m++){
				if (nsec < 0){
					ewr[m] = m_ExyR[np[n]][ne+j*m_ndata][nt[n]+m];
				}
				else{
					ewr[m] = m_GxyR[nsec][np[n]][ne+j*m_ndata][nt[n]+m];
				}
			}
			ews[n] = lininterp(thetar, 
				m_theta[np[n]][nt[n]], m_theta[np[n]][nt[n]+1], ewr[0], ewr[1]);
		}
		Exy[j] = lininterp(phir, phi[0], phi[1], ews[0], ews[1]);
	}
	return true;
}

void ComplexAmplitude::f_AssignGridConditions(
	int mesh[], double delta[], double *dinterv, double *hrange)
{
	for(int j = 0; j < 2; j++){
		m_halfmesh[j] = (mesh[j]-1)/2;
		m_delta[j] = delta[j];
		m_mesh[j] = mesh[j];
		m_valrange[j] = (double)(m_halfmesh[j]+1.0e-3)*m_delta[j];

		if(dinterv == nullptr){
			// for undulator, calc. interval should be shorter than grid size (m_delta)
			m_dinterv[j] = m_delta[j];
			m_halfrange[j] = m_halfmesh[j]*m_dinterv[j];
		}
		else{
			m_dinterv[j] = dinterv[j];
			m_halfrange[j] = hrange[j];
		}
	}
}

double ComplexAmplitude::f_GTmaxU(double epsilon, double *gt2uv, double *hDelta)
{
	*hDelta = MAXARGSINC+max(0.0, -epsilon/(1.0+epsilon/(double)(m_nh*m_N)));
	*hDelta = sqrt(*hDelta);
	*gt2uv = sqrt((double)(m_nh*m_N)/(1.0+m_K2));
	return (*hDelta)/(*gt2uv);
}

void ComplexAmplitude::f_AssignEFieldUnd(double epsilon, bool issn)
{
	double hDelta, u, v, pk, gtxymax, gt2uv, gt, phi, coef;
	double delta[2], dinterv[2], hrange[2];
	int hmesh, mesh[2];
	vector<double> fxy(4);

	gtxymax = f_GTmaxU(epsilon, &gt2uv, &hDelta);
	delta[0] = delta[1] = 1.0/16.0/(double)m_nh/m_accuracy[accinobs_];

	hmesh = (int)ceil(gtxymax/delta[0]);
	for(int j = 0; j < 2; j++){
		delta[j] = (gtxymax/(double)hmesh)*gt2uv;
		mesh[j] = 2*hmesh+1;
	}

	pk = max(1.0, -epsilon);
	dinterv[0] = dinterv[1] = sqrt(1.0/32.0/pk/m_accuracy[accinobs_]);
	hrange[0] = hrange[1] = hDelta;


#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(5);
	if(!UfieldCheckXY.empty()){
		debug_out.open(UfieldCheckXY);
	}
#endif

	UndulatorFxyFarfield *uxyfar = new UndulatorFxyFarfield(*this);
	for(int j = 0; j < 4; j++){
		m_Exy[j].resize(2*hmesh+1);
	}
	for(int nx = -hmesh; nx <= hmesh; nx++){
		u = (double)nx*delta[0];
		for (int j = 0; j < 4; j++){
			m_Exy[j][nx+hmesh].resize(2*hmesh+1);
		}
		for(int ny = -hmesh; ny <= hmesh; ny++){
			v = (double)ny*delta[1];
			gt = sqrt(hypotsq(u, v))/gt2uv;
			if(gt > INFINITESIMAL){
				phi = atan2(v, u);
			}
			else{
				phi = 0.0;
			}
			uxyfar->SetCondition(m_nh, gt);
			uxyfar->GetFxy(phi, &fxy, true);
			coef = uxyfar->GetCoefFxy();
			for(int j = 0; j < 4; j++){
				m_Exy[j][nx+hmesh][ny+hmesh] = fxy[j]*(m_coefExy/coef);
				// to be consistent with the definition of Fx,y
			}
#ifdef _DEBUG
			items[0] = v;
			for(int j = 0; j < 4; j++){
				items[j+1] = m_Exy[j][nx+hmesh][ny+hmesh];
			}
			PrintDebugItems(debug_out, u, items);
#endif
		}
	}
	delete uxyfar;

#ifdef _DEBUG
	if(!UfieldCheckXY.empty()){
		debug_out.close();
	}
#endif

	f_AssignGridConditions(mesh, delta, dinterv, hrange);
	if(issn){
		f_AssignSn(hDelta, epsilon);
	}
}

void ComplexAmplitude::f_AssignSn(double uvmax, double epsilon)
{
	int hmesh[2], meshsn[2];
	double deltasn[2];
	double wmax = max(2.0*uvmax*uvmax, MAXARGSINC);
	deltasn[0] = deltasn[1] = 1.0/8.0/m_accuracy[accinpE_];
	hmesh[0] = (int)ceil(wmax/deltasn[0]);
	hmesh[1] = (int)ceil(MAXARGSINC/deltasn[1]);

	for(int j = 0; j < 2; j++){
		meshsn[j] = 2*hmesh[j]+1;
	}
	m_Sn.resize(2*hmesh[0]+1);
	for(int nx = -hmesh[0]; nx <= hmesh[0]; nx++){
		m_Sn[nx+hmesh[0]].resize(2*hmesh[1]+1);
	}
	double esigma = 2.0*EnergySpreadSigma()*m_nh*m_N; 
	// to convert from e-energy deviation to wavelength deviation

#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(2);
	if(!UfieldCheckXY.empty()){
		debug_out.open(UfieldCheckSn);
	}
#endif

	int nfft = 1;
	while(nfft < meshsn[0]) nfft <<= 1;
	
	FastFourierTransform fft(1, nfft);
	double *data, w, dw, sarg[2], dz = PI2/((double)nfft*deltasn[0]), tex;
	data = (double *)calloc(nfft, sizeof(double));
	for(int ny = -hmesh[1]; ny <= hmesh[1]; ny++){
		dw = deltasn[1]*(double)ny;
		for(int n = 0; n < nfft; n++){
			data[n] = 0.0;
		}
		for(int nx = -hmesh[0]; nx <= hmesh[0]; nx++){
			w = deltasn[0]*(double)nx;
			sarg[0] = PI*w;
			sarg[1] = PI*(w+dw);
			data[nx+nfft/2] = sinc(sarg[0])*sinc(sarg[1]);
		}
		fft.DoRealFFT(data);
	    for(int n = 0; n <= nfft/2; n++){
			tex = (double)n*dz;
			tex *= esigma;
			tex *= tex*0.5;
			if(tex > MAXIMUM_EXPONENT){
				tex = 0.0;
			}
			else{
				tex = exp(-tex);
			}
            if(n == nfft/2){
                data[1] *= tex;
            }
            else if(n == 0){
                data[0] *= tex;
            }
            else{
                data[2*n] *= tex;
                data[2*n+1] *= tex;
            }

		}
		fft.DoRealFFT(data, -1);
		for(int nx = -hmesh[0]; nx <= hmesh[0]; nx++){
			w = deltasn[0]*(double)nx;
			m_Sn[nx+hmesh[0]][ny+hmesh[1]] = data[nx+nfft/2]*2.0/(double)nfft;
#ifdef _DEBUG
			items[0] = w;
			items[1] = m_Sn[nx+hmesh[0]][ny+hmesh[1]];
			PrintDebugItems(debug_out, dw, items);
#endif

		}
	}

#ifdef _DEBUG
	if(!UfieldCheckXY.empty()){
		debug_out.close();
	}
#endif

	f_AssignSnGrid(meshsn, deltasn, epsilon);
	free(data);
}

void ComplexAmplitude::f_AssignSnGrid(
	int mesh[], double delta[], double epsilon)
{
	m_Uepsilon = epsilon;
	for(int j = 0; j < 2; j++){
		m_halfmeshsn[j] = (mesh[j]-1)/2;
		m_deltasn[j] = delta[j];
		m_snmesh[j] = mesh[j];
		m_valrangesn[j] = (double)(m_halfmeshsn[j]+1.0e-3)*m_deltasn[j];
	}
}

void ComplexAmplitude::f_AssignAngularGrid(double aflux, int mesh[], double delta[])
{
	m_aflux = aflux;
	for(int j = 0; j < 2; j++){
		m_adelta[j] = delta[j];
		m_amesh[j] = mesh[j];
	}
}

void ComplexAmplitude::f_AssignEFieldWiggler(double epsilon, double deltau, bool isbma)
{
	double ex[2] = {0, 0}, ey[2] = {0,0}, csn[2], buffx[2], buffy[2];
	double ev2, eubcub, exparg, eta0, cv, eKx, eKy, aflux;
	double hDelta[2], u, v, vs, delta[2], adelta[2];
	int hmesh[2], mesh[2], ahmesh[2], amesh[2];
	vector<vector<double>> ws(4);
	vector<double> zws;

	delta[0] = PI2/4.0/deltau/deltau/m_accuracy[accinobs_];
	delta[1] = min(0.1, PI2/4.0/deltau/sqrt(MAXARGK1312))/m_accuracy[accinobs_];
	hDelta[0] = deltau*0.5;
	hDelta[1] = sqrt(MAXARGK1312);
	adelta[0] = adelta[1] = ANGLEINTERVAL;

	for(int j = 0; j < 2; j++){
		hmesh[j] = max(4, (int)ceil(hDelta[j]/delta[j]));
		delta[j] = hDelta[j]/(double)hmesh[j];
		mesh[j] = 2*hmesh[j]+1;
		ahmesh[j] = max(4, (int)ceil(hDelta[j]/adelta[j]));
		amesh[j] = 2*ahmesh[j]+1;
	}

	eKy = epsilon*m_Kxy[1][1];
	eKx = epsilon*m_Kxy[0][1];

#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(5);
	if(!WfieldCheckXY.empty()){
		debug_out.open(WfieldCheckXY);
	}
#endif

	for(int j = 0; j < 4; j++){
		m_Exy[j].resize(2*hmesh[0]+1);
	}
	aflux = 0.0;
	for(int nx = -hmesh[0]; nx <= hmesh[0]; nx++){
		u = (double)nx*delta[0];
		for (int j = 0; j < 4; j++){
			m_Exy[j][nx+hmesh[0]].resize(2*hmesh[1]+1);
		}
		for(int ny = -hmesh[1]; ny <= hmesh[1]; ny++){
			v = (double)ny*delta[1];
			eta0 = u/eKy;
			if(fabs(eta0) >= 1.0){
				for (int j = 0; j < 4; j++){
					m_Exy[j][nx+hmesh[0]][ny+hmesh[1]] = 0;
				}
			}
			else{
				cv = 1.0-eta0*eta0;
				cv = sqrt(cv);
				vs = v-eKx*cv;
				ev2 = epsilon*epsilon+vs*vs;
				eubcub = 2.0/3.0*pow(ev2, 1.5)/cv;
				ex[1] = -1.5/sqrt(ev2)*Bessel::K23_u(eubcub); // imaginary of Ex
				ey[0] = vs*1.5/ev2*Bessel::K13_u(eubcub); // real of Ey
				eta0 = asin(eta0);
				exparg = eKy*(
							eta0*(epsilon*epsilon+hypotsq(u, v)+hypotsq(eKx, eKy)*0.5)
							+(eKx*eKx-eKy*eKy)*sin(2.0*eta0)/4.0
							-2.0*eKx*v*sin(eta0)+2.0*eKy*u*(cos(eta0)-1.0)
						);
				csn[0] = cos(exparg);
				csn[1] = sin(exparg);

				complex_product(ex, csn, buffx);
				complex_product(ey, csn, buffy);
				for(int j = 0; j < 2; j++){
					m_Exy[j  ][nx+hmesh[0]][ny+hmesh[1]] = buffx[j];
					m_Exy[j+2][nx+hmesh[0]][ny+hmesh[1]] = buffy[j];
				}

			}
			for (int j = 0; j < 4; j++){
				m_Exy[j][nx+hmesh[0]][ny+hmesh[1]] *= m_coefExy;
				aflux += m_Exy[j][nx+hmesh[0]][ny+hmesh[1]]*m_Exy[j][nx+hmesh[0]][ny+hmesh[1]];
			}
#ifdef _DEBUG
			items[0] = v;
			for(int j = 0; j < 4; j++){
				items[j+1] = m_Exy[j][nx+hmesh[0]][ny+hmesh[1]];
			}
			PrintDebugItems(debug_out, u, items);
#endif
		}
	}
#ifdef _DEBUG
	if(!WfieldCheckXY.empty()){
		debug_out.close();
	}
#endif
	aflux *= delta[0]*delta[1];

	f_AssignGridConditions(mesh, delta, nullptr, nullptr);
	f_AssignAngularGrid(aflux, amesh, adelta);
}

void ComplexAmplitude::f_AssignEFieldBM(double epsilon, double deltau)
{
	double hDelta[2], uv[2], delta[2], umax, exy[4];
	double Mg = 2*m_accuracy[accinobs_];
	int hmesh[2], mesh[2];

	if(!m_issrcpoint && m_confb[optDx_]){
		double dqduv = 1.0/(epsilon*m_gamma);
		double A = PI2*Mg*3.0/pow(epsilon, 3.0);
		// oscillating term: double E ~ exp(iA)
		double B = pow((A+sqrt(A*A+4.0))/2.0, 1.0/3.0);
		if(contains(m_calctype, menu::XXpslice)
			|| contains(m_calctype, menu::YYpslice)
			|| contains(m_calctype, menu::XXpYYp))
		{
			umax = max(fabs(m_confv[Xprange_][0]), fabs(m_confv[Xprange_][1]))/dqduv;
		}
		else{
			umax = fabs(m_conf[Xpfix_])/dqduv;
		}
		umax = max(umax, (B-1.0/B)*epsilon);
		deltau = min(2.0*umax, deltau);
	}

	delta[0] = PI2/4.0/deltau/deltau/m_accuracy[accinobs_];
	delta[1] = min(0.1, PI2/4.0/deltau/sqrt(MAXARGK1312))/m_accuracy[accinobs_];
	hDelta[0] = deltau*0.5;
	hDelta[1] = sqrt(MAXARGK1312);

	for(int j = 0; j < 2; j++){
		hmesh[j] = max(4, (int)ceil(hDelta[j]/delta[j]));
		delta[j] = hDelta[j]/(double)hmesh[j];
		mesh[j] = 2*hmesh[j]+1;
	}

#ifdef _DEBUG
	ofstream debug_out;
	vector<double> items(5);
	if(!BfieldCheckXY.empty()){
		debug_out.open(BfieldCheckXY);
	}
#endif

	for(int j = 0; j < 4; j++){
		m_Exy[j].resize(2*hmesh[0]+1);
	}
	for(int nx = -hmesh[0]; nx <= hmesh[0]; nx++){
		uv[0] = (double)nx*delta[0];
		for (int j = 0; j < 4; j++){
			m_Exy[j][nx+hmesh[0]].resize(2*hmesh[1]+1, 0.0);
		}
		for(int ny = -hmesh[1]; ny <= hmesh[1]; ny++){
			uv[1] = (double)ny*delta[1];
			f_GetBMExyAmpDirect(epsilon, uv, exy);
			for(int j  = 0; j < 4; j++){
				m_Exy[j][nx+hmesh[0]][ny+hmesh[1]] = exy[j];
			}
#ifdef _DEBUG
			if(!BfieldCheckXY.empty()){
				items[0] = uv[1];
				for (int j = 0; j < 4; j++){
					items[j+1] = m_Exy[j][nx+hmesh[0]][ny+hmesh[1]];
				}
				PrintDebugItems(debug_out, uv[0], items);
			}
#endif
		}
	}
#ifdef _DEBUG
	if(!BfieldCheckXY.empty()){
		debug_out.close();
	}
#endif
	f_AssignGridConditions(mesh, delta, nullptr, nullptr);
}

void ComplexAmplitude::f_GetBMExyAmpDirect(double epsilon, double uv[], double Exy[])
{
	double ev2 = epsilon*epsilon+uv[1]*uv[1];
	double u = 2.0/3.0*pow(ev2, 1.5);
	double ex[2] = {0, 0}, ey[2] = {0, 0};
	double csn[2];

	double phi = uv[0]*(ev2+uv[0]*uv[0]/3.0);
	csn[0] = cos(phi);
	csn[1] = sin(phi);
	ex[1] = -1.5/sqrt(ev2)*Bessel::K23_u(u)*m_coefExy;
	ey[0] = uv[1]*1.5/ev2*Bessel::K13_u(u)*m_coefExy;

	complex_product(ex, csn, Exy);
	complex_product(ey, csn, Exy+2);
}
