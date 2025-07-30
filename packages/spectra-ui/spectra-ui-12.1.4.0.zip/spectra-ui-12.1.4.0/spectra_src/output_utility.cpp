#include "output_utility.h"
#include "spectra_solver.h"
#include "common.h"

string TitleLables[NumberTitles] = {
    "Gap", "Energy", "Energy", "P.Energy",
    "Angle", "theta_x", "theta_y", "Position", "x", "y", "r", "theta","phi",
    "Ky", "Kx", "K_Value",
    "F.Density", "LF.Density", "Reconst.", "Reconst.", "P.Density", "Filtering",
    "F.Density", "LF.Density", "P.Density", "Filtering", "Harm.x", "Harm.y",
    "GA.Brill.", "Brilliance", "Prj.Brill.", "Flux.eV", "Flux", "I_Power", "I_Flux",
    "Av.Density", "Av.Brill", "PL", "PC", "PL45", "1-|PL|",
    "Horiz.Dens", "Vert.Dens", "Power", "Filtering", "Tot.Power",
    "Nat.Size", "Nat.Div.", "Size.x", "Size.y",
    "Div.x", "Div.y", "Coh.Flux", "Coh.Power",
    "z", "Bx", "By", "Bz", "x'", "y'", "x", "y",
    "E.Field.x", "E.Field.y", "ObserverTime",
    "ReField.x", "ImField.x",
    "ReField.y", "ImField.y",
    "CohFrac.x", "CohFrac.y",
    WigXLabel, WigYLabel, WigXpLabel, WigYpLabel, "Separability", "Ov.Deg.Coh.", "Ov.Deg.Coh.x", "Ov.Deg.Coh.y",
	"DX", "DY", "z", 
	"E.Field.x", "E.Field.y", "Depth", "Vol.P.Density",
	"Harm.No.", 
    "PoleNo.", "PhaseErr.", "Trans.",
    "beta_x", "beta_y", "Abs.",
    "Filtered",
    "Modal.Amp.Re", "Modal.Amp.Im", "Mode", "Reconst.", "Reconst.", "Mode Number", "Modal Flux", "Integrated Modal Flux",
    "Phase.Err", "Gen.Phase.Err",
    "z", "Time", "DE/E", "Curr.", "j", "B.Factor.Re", "B.Factor.Im", "P.Energy.Rad", "P.Energy.e", "P.EnergyDens.",
    "x^", "y^", "x.mid", "y.mid", "dx", "dy", 
    "x^.mid", "y^.mid", "dx^", "dy^", "|CSD|", "Arg.CSD", "Coh.Deg.",
    "Size.x", "Size.y"
};

string TitleLablesDetailed[NumberTitles] = {
    "Gap", "Harmonic Energy", "Energy", "Peak Energy",
    "Angle", "x'", "y'", "Position", "x", "y",  "r", "theta", "phi",
    "Ky", "Kx", "K Value",
    "Flux Density", "Linear Flux Density", "Reconstructed", "Reconstructed", "Power Density", "Filtered Power",
    "Flux Density", "Linear Flux Density", "Power Density", "Filtered Power", "Harmonic Power (x)", "Harmonic Power (y)",
    "GA. Brilliance", "Brilliance", "Prj. Brilliance", "Flux(/eV)", "Flux", "Integrated Power", "Integrated Flux",
    "Average Density", "Average Brill", "PL(s1/s0)", "PC(s3/s0)", "PL45(s2/s0)", "1-|PL|",
    "Horizontal Density", "Vertical Density", "Partial Power", "Filtered Power", "Total Power",
    "Natural Size", "Natural Divergence", "Horizontal Size", "Vertical Size",
    "Horizontal Divergence", "Vertical Divergence",
    "Coherent Flux", "Coherent Power",
    "z", "Bx", "By", "Bz", "x'",  "y'", "x", "y",
    "Horizontal Electric Field", "Vertical Electric Field", "Observer Time",
    "Horizontal Real Field", "Horizontal Imaginary Field",
    "Vertical Real Field", "Vertical Imaginary Field",
    "Horizontal Coherent Fraction", "Vertical Coherent Fraction",
    WigXLabel, WigYLabel, WigXpLabel, WigYpLabel,
	"Separability", "Overall Deg. Coherence (Total)", "Overall Deg. Coherence (X)","Overall Deg. Coherence (Y)",
	"Aperture X", "Aperture Y", "z",
	"Horiozntal Electric Field", "Vertical Electric Field", "Depth", "Volume Power Density",
	"Harmonic Number", 
    "Pole Number", "Phase Error", "Transmission Rate",
    "Horizontal beta function", "Vertical beta function", "Aborption Rate",
    "Filtered",
    "Modal Amplitude Real", "Modal Amplitude Imaginary", "Mode", "Reconstructed", "Reconstructed", "Mode Number", "Modal Flux", "Integrated Modal Flux",
    "Single Electron", "with Recovery Factors",
    "z", "Time", "DE/E", "Current", "Current Density", "Bunch Factor Real", "Bunch Factor Imaginary", "Radiation Pulse Energy", "e- Bunch Energy Loss", "Pulse Energy Density",
    "x^", "y^", "Middle (x)", "Middle (y)", "Distance (x)", "Distance (y)",
    "Middle (x^)", "Middle (y^)", "Distance (x^)", "Distance (y^)", "|CSD|", "CSD Argument", "Degree of Coherence",
    "Beam Size (x)", "Beam Size (y)"
};

string UnitLables[NumberTitles] = {
    "-", "eV", "eV", "eV",
    "mrad", "mrad", "mrad", "mm", "mm", "mm", "mm", "mrad", "deg",
    "-", "-", "-",
    "ph/s/mm^2/0.1%", "ph/s/mm/0.1%", "ph/s/mm^2/0.1%", "ph/s/mm/0.1%", "kW/mm^2", "kW/mm^2",
    "ph/s/mr^2/0.1%", "ph/s/mr/0.1%", "kW/mrad^2", "kW/mrad^2", "kW/mrad^2", "kW/mrad^2",
    "F.Dens/mm^2", "Flux/mm^2/mrad^2", "Flux/mm/mrad", "ph/s/eV", "ph/s/0.1%", "kW", "ph/s",
    "ph/s/mr^2/0.1%", "F.Dens/mm^2", "-", "-", "-", "-",
    "ph/s/mr^2/0.1%", "ph/s/mr^2/0.1%", "kW", "kW", "kW",
    "m", "rad", "m", "m",
    "rad", "rad", "ph/s/0.1%", "W",
    "m", "T", "T", "T", "rad", "rad", "m", "m",
    "V/m", "V/m", "fsec",
    "V.sec/m", "V.sec/m", "V.sec/m", "V.sec/m",
	"-", "-", 
	"mm", "mm", "mrad", "mrad", "-", "-", "-", "-",
	"mm", "mm", "m",
	"V", "V", "mm", "W/mm^3",
	"-", 
    "-", "deg.", "-",
    "m", "m", "-",
    "-",
    "-", "-", "-", "Flux/mm^2/mrad^2", "Flux/mm/mrad", "-", "%", "%",
    "", "",
    "m", "fs", "-", "A", "A/100%", "-", "-", "mJ", "mJ", "mJ/mm^2",
    "/Sigma", "/Sigma", "mm", "mm", "mm", "mm",
    "/Sigma", "/Sigma", "/Sigma", "/Sigma", "ph/s/mm^2/0.1%", "rad.", "-",
    "mm", "mm"
};

string UnitLablesDetailed[NumberTitles] = {
    "", "eV", "eV", "eV",
    "mrad", "mrad", "mrad", "mm", "mm", "mm", "mm", "mrad", "degree",
    "", "", "",
    "ph/s/mm^2/0.1%B.W.", "ph/s/mm/0.1%B.W.", "ph/s/mm^2/0.1%B.W.", "ph/s/mm/0.1%B.W.", "kW/mm^2", "kW/mm^2",
    "ph/s/mr^2/0.1%B.W.", "ph/s/mr/0.1%B.W.", "kW/mrad^2", "kW/mrad^2", "kW/mrad^2", "kW/mrad^2",
    "ph/s/mm^2/mr^2/0.1%B.W.", "ph/s/mm^2/mr^2/0.1%B.W.", "ph/s/mm/mr/0.1%B.W.", "ph/s/eV","ph/s/0.1%B.W.", "kW", "ph/s",
    "ph/s/mr^2/0.1%B.W.", "ph/s/mr^2/0.1%B.W./mm^2", "", "", "", "",
    "ph/s/mr^2/0.1%B.W.", "ph/s/mr^2/0.1%B.W.", "kW", "kW", "kW",
    "m", "rad", "m", "m",
    "rad", "rad", "ph/s/0.1%B.W.", "W",
    "m", "T", "T", "T", "rad", "rad", "m", "m",
    "V/m", "V/m", "fsec",
    "V.sec/m", "V.sec/m", "V.sec/m", "V.sec/m", "", "",
	"mm", "mm", "mrad", "mrad", "", "", "", "",
	"mm", "mm", "m",
	"V", "V", "mm", "W/mm^3",
	"", 
    "", "degree", "-",
    "m", "m", "-",
    "-",
    "-", "-", "-", "ph/s/mm^2/mr^2/0.1%B.W.", "ph/s/mm/mr/0.1%B.W.", "-", "%", "%",
    "", "",
    "m", "fs", "-", "A", "A/100%", "-", "-", "mJ", "mJ", "mJ/mm^2",
    "/Sigma", "/Sigma", "mm", "mm", "mm", "mm",
    "/Sigma", "/Sigma", "/Sigma", "/Sigma", "ph/s/mm^2/0.1%", "rad.", "-",
    "mm", "mm"
};

int FormatStringPrecisions[NumberTitles] = {
    3, 5, 5, 5,
    5, 5, 5, 5, 5, 5, 5, 5, 5,
    3, 3, 3,
    4, 4, 4, 4, 4, 4,
    3, 3, 3, 3, 3, 3,
    3, 3, 3, 3, 3, 3, 3,
    3, 3, 6, 6, 6, 6,
    3, 3, 3, 3, 3,
    3, 3, 3, 3,
    3, 3, 3, 3,
    6, 3, 3, 3, 3, 3, 3, 3,
    3, 3, 8,
    3, 3, 3, 3, 4, 4,
	5, 5, 5, 5, 3, 3, 3, 3,
	3, 3, 3,
	3, 3, 5, 3,
	2,
    2, 2, 2,
    2, 2, 2,
    3,
    3, 3, 0, 3, 3, 3, 3, 3,
    3, 3,
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
    3, 3, 3, 3, 3, 3,
    3, 3, 3, 3, 3, 3, 3,
    3, 3
};

int FormatStringWidths[NumberTitles] = {
    10, 11, 11, 11,
    12, 12, 12, 12, 12, 12, 12, 12, 12,
    15, 10, 10,
    13, 13, 13, 13, 13, 13,
    15, 10, 10, 10, 10, 10,
    12, 16, 12, 10, 10, 10, 10,
    15, 12, 13, 13, 13, 13,
    15, 15, 10, 10, 10,
    9, 9, 9, 9,
    9, 9, 10, 10,
    13, 10, 10, 10, 10, 10, 10, 10,
    10, 10, 15,
    10, 10, 10, 10, 11, 11,
	12, 12, 12, 12, 10, 10, 10, 10,
	10, 10, 10,
	10, 10, 12, 13,
	9,
    9, 9, 9,
    9, 9, 9,
    10,
    10, 10, 3, 15, 15, 10, 10, 10,
    10, 10,
    10, 10, 10, 10, 10, 10, 10, 10, 10, 10,
    10, 10, 10, 10, 10, 10,
    10, 10, 10, 10, 10, 10, 10,
    10, 10
};

#define DEFAULTWIDTH 12
#define DEFAULTPREC 4

#ifndef _COMPARATOR

void GetIndicesFromTitles(vector<string> &dtitles, vector<string> &dunits, 
    vector<string> &stitles, vector<string> &sunits, vector<int> &widths, vector<int> &precs)
{
    int index;
    stitles.resize(dtitles.size());
    sunits.resize(dtitles.size());
    widths.resize(dtitles.size());
    precs.resize(dtitles.size());
    for(int j = 0; j < dtitles.size(); j++){
        index = -1;
        for(int i = 0; i < NumberTitles; i++){
            if(dtitles[j] == TitleLablesDetailed[i] 
                && dunits[j] == UnitLablesDetailed[i]){
                index = i;
                break;
            }
        }
        if(index < 0){
            size_t ist = dtitles[j].find("(");
            if(ist != string::npos){
                size_t ied = dtitles[j].find(")");
                stitles[j] = dtitles[j].substr(0, ist);
                if(ied != string::npos){
                    sunits[j] = dtitles[j].substr(ist+1, ied-ist-1);
                }
                else{
                    sunits[j] = dtitles[j].substr(ist+1);
                }
            }
            else{
                stitles[j] = dtitles[j];
                sunits[j] = "-";
            }
            vector<string> items;
            int nitems = separate_items(stitles[j], items);
            if(nitems > 1){
                stitles[j] = items[0];
                for (int i = 1; i < nitems; i++){
                    stitles[j] += items[i];
                }
            }
            widths[j] = max(DEFAULTWIDTH, 
                (int)max(stitles[j].length(), sunits[j].length())+1);
            precs[j] = DEFAULTPREC;
        }
        else{
            stitles[j] = TitleLables[index];
            sunits[j] = UnitLables[index];
            widths[j] = FormatStringWidths[index]+(j>0?1:0);
            precs[j] = FormatStringPrecisions[index];
        }
    }
}

void SpectraSolver::GetOutputItemsIndices(vector<int> &itemindices)
{
    itemindices.clear();

    if(m_pptype == PPBetaLabel){
		itemindices.push_back(Z_);
		itemindices.push_back(twiss_betax_);
		itemindices.push_back(twiss_betay_);
        return;
    }
    else if(m_pptype == PPFDlabel){
		itemindices.push_back(Z_);
		itemindices.push_back(Bx_);
		itemindices.push_back(By_);
		itemindices.push_back(Bz_);
        return;
    }
    else if(m_pptype == PP1stIntLabel){
		itemindices.push_back(Z_);
		itemindices.push_back(Betax_);
		itemindices.push_back(Betay_);
        return;
    }
    else if(m_pptype == PP2ndIntLabel){
		itemindices.push_back(Z_);
		itemindices.push_back(X_);
		itemindices.push_back(Y_);
        return;
    }
    else if(m_pptype == PPPhaseErrLabel){
        if(m_ppconfsel[zcoord_] == PhaseErrZPole){
            itemindices.push_back(PoleNo_);
        }
        else{
            itemindices.push_back(Z_);
        }
		itemindices.push_back(PhaseErr_);
        return;
    }
    else if(m_pptype == PPRedFlux){
		itemindices.push_back(Harmonic_);
		itemindices.push_back(NormIntPhase_);
		itemindices.push_back(NormIntGPhase_);
        return;
    }
    else if(m_pptype == PPTransLabel){
		itemindices.push_back(Energy_);
		itemindices.push_back(Transmission_);
        return;
    }
    else if(m_pptype == PPAbsLabel){
		itemindices.push_back(Energy_);
		itemindices.push_back(Absorption_);
        return;
    }

	if(m_isvpdens){
		itemindices.push_back(DistX_);
		itemindices.push_back(DistY_);
		itemindices.push_back(DistDepth_);
		itemindices.push_back(VolPowerDens_);
		return;
	}

    bool isbxund = m_srctype == ELLIPTIC_UND 
        || m_srctype == FIGURE8_UND
        || m_srctype == VFIGURE8_UND;

	if(m_issrcpoint){
        if(contains(m_calctype, menu::sprof)){
	        itemindices.push_back(SrcX_);
	        itemindices.push_back(SrcY_);
	        itemindices.push_back(NearFldens_);
            return;
        }
		else if(m_isenergy){
	        itemindices.push_back(Energy_);
		}
		else if(contains(m_calctype, menu::Kvalue)){
	        itemindices.push_back(HEnergy_);
            if(!contains(m_calctype, menu::allharm)){
                if(isbxund){
                    itemindices.push_back(Kx_);
                    itemindices.push_back(Ky_);
                }
                else{
                    itemindices.push_back(Kvalue_);
                }
                if (m_srcsel[gaplink_] == ImpGapTableLabel){
                    itemindices.push_back(Gap_);
                }
            }
		}
		else{
			if(contains(m_calctype, menu::XXpslice) ||
                contains(m_calctype, menu::XXpprj))
            {
		        itemindices.push_back(SrcX_);
		        itemindices.push_back(SrcQX_);
			}
			if(contains(m_calctype, menu::YYpslice) ||
                contains(m_calctype, menu::YYpprj))
            {
		        itemindices.push_back(SrcY_);
		        itemindices.push_back(SrcQY_);
			}
            if(contains(m_calctype, menu::XXpYYp)){
		        itemindices.push_back(SrcX_);
		        itemindices.push_back(SrcY_);
		        itemindices.push_back(SrcQX_);
		        itemindices.push_back(SrcQY_);
            }
		}
		if(contains(m_calctype, menu::Wrel)){
			itemindices.push_back(Correlation_);
			itemindices.push_back(DegCohX_);
			itemindices.push_back(DegCohY_);
			itemindices.push_back(DegCoh_);
		}
        else if (contains(m_calctype, menu::XXpprj)
            || contains(m_calctype, menu::YYpprj)
            || contains(m_calctype, menu::WprjX)
            || contains(m_calctype, menu::WprjY))
        {
            itemindices.push_back(Brill1D_);
        }
        else{
            itemindices.push_back(WBrill_);
        }
        if (contains(m_calctype, menu::allharm)){
            itemindices.push_back(Harmonic_);
        }
		return;
	}

    if((m_isenergy || IsFixedPoint())
        && contains(m_calctype, menu::simpcalc))
    {
        if(m_isenergy){
            itemindices.push_back(Energy_);
        }
        itemindices.push_back(Fldens_);
        itemindices.push_back(GABrill_);
        itemindices.push_back(Flux_);
        itemindices.push_back(Sizex_);
        itemindices.push_back(Sizey_);
        itemindices.push_back(Divx_);
        itemindices.push_back(Divy_);
		itemindices.push_back(Cflux_);
		itemindices.push_back(Cpower_);
		itemindices.push_back(CohFractionX_);
		itemindices.push_back(CohFractionY_);
        return;
    }

    if(m_istime){
        itemindices.push_back(Obstime_);
        if(contains(m_calctype, menu::efield)){
            if(m_confb[fouriep_]){
                itemindices.push_back(FarEfieldx_);
                itemindices.push_back(FarEfieldy_);
            }
            else{
                itemindices.push_back(Efieldx_);
                itemindices.push_back(Efieldy_);
            }
        }
        else if(contains(m_calctype, menu::pdenss)){
            if(m_confb[fouriep_]){
                itemindices.push_back(Pwdens_);
            }
            else{
                itemindices.push_back(NearPwdens_);
            }
        }
        else{
            itemindices.push_back(Power_);
        }
        return;
    }

	if(m_isenergy){
        itemindices.push_back(Energy_);
    }
    bool isangle = m_confsel[defobs_] == ObsPointAngle;
    if(contains(m_calctype, menu::along)){
        if(isangle){
            itemindices.push_back(ThetaXY_);
        }
        else{
            itemindices.push_back(DistXY_);
        }
    }
    if(contains(m_calctype, menu::meshxy)){
        if(isangle){
            itemindices.push_back(ThetaX_);
            itemindices.push_back(ThetaY_);
        }
        else{
            itemindices.push_back(DistX_);
            itemindices.push_back(DistY_);
        }
    }
    if(contains(m_calctype, menu::meshrphi)){
        if(isangle){
            itemindices.push_back(Theta_);
        }
        else{
            itemindices.push_back(R_);
        }
        itemindices.push_back(Phi_);
    }
    if(contains(m_calctype, menu::xzplane)){
        itemindices.push_back(DistX_);
        itemindices.push_back(LongPos_);
    }
    if(contains(m_calctype, menu::yzplane)){
        itemindices.push_back(DistY_);
        itemindices.push_back(LongPos_);
    }
    if(contains(m_calctype, menu::pipe)){
        itemindices.push_back(Phi_);
        itemindices.push_back(LongPos_);
    }
    if(contains(m_calctype, menu::Kvalue)){
        if(contains(m_calctype, menu::fluxpeak)){        
            itemindices.push_back(HEnergy_);
            itemindices.push_back(Energycv_);
        }
        else if(!contains(m_calctype, menu::fluxfix)){
            itemindices.push_back(HEnergy_);
        }
        if(!contains(m_calctype, menu::allharm)){
            if(isbxund){
                itemindices.push_back(Kx_);
                itemindices.push_back(Ky_);
            }
            else{
                itemindices.push_back(Kvalue_);
            }
            if(m_srcsel[gaplink_] == ImpGapTableLabel){
                itemindices.push_back(Gap_);
            }
        }

        if(contains(m_calctype, menu::simpcalc)){
            itemindices.push_back(Fldens_);
            itemindices.push_back(GABrill_);
            itemindices.push_back(Flux_);
            if(contains(m_calctype, menu::tgtharm)){
                itemindices.push_back(Tpower_);
            }
            itemindices.push_back(Cohsize_);
            itemindices.push_back(Cohdiv_);
            itemindices.push_back(Sizex_);
            itemindices.push_back(Sizey_);
            itemindices.push_back(Divx_);
            itemindices.push_back(Divy_);
            itemindices.push_back(Cflux_);
            itemindices.push_back(Cpower_);
            itemindices.push_back(CohFractionX_);
            itemindices.push_back(CohFractionY_);
            if(contains(m_calctype, menu::allharm)){
                itemindices.push_back(Harmonic_);
            }
            return;
        }
    }

    bool isflux = false;
    if(contains(m_calctype, menu::fdensa)){
        itemindices.push_back(Fldens_);
        if(m_isenergy || IsFixedPoint() || contains(m_calctype, menu::fluxpeak)){
            itemindices.push_back(GABrill_);
        }
        isflux = true;
    }
    else if(contains(m_calctype, menu::fdenss)){
        itemindices.push_back(NearFldens_);
        isflux = true;
    }
    else if(contains(m_calctype, menu::pflux) 
        || contains(m_calctype, menu::tflux))
    {
        itemindices.push_back(Flux_);
        isflux = true;
    }
    if(isflux){
        itemindices.push_back(Pl_);
        itemindices.push_back(Pc_);
        itemindices.push_back(Pl45_);
    }

    if(contains(m_calctype, menu::spdens)){
        itemindices.push_back(NearPwdens_);
    }
    else if(contains(m_calctype, menu::pdensa)){
        itemindices.push_back(Pwdens_);
        if(m_isfilter){
            itemindices.push_back(Fpwdens_);
        }
        if(contains(m_calctype, menu::Kvalue)){
            itemindices.push_back(Tpower_);
        }
    }
    else if(contains(m_calctype, menu::pdenss)){
		itemindices.push_back(NearPwdens_);
        if(m_isfilter){
            itemindices.push_back(NearFpwdens_);
        }
    }
    else if(contains(m_calctype, menu::pdensr)){
        itemindices.push_back(Pwdens_);
        itemindices.push_back(ResPwdensX_);
        itemindices.push_back(ResPwdensY_);
    }
    else if(m_ispower){
        itemindices.push_back(Power_);
        if(m_isfilter){
            itemindices.push_back(FPower_);
        }
        if(contains(m_calctype, menu::Kvalue)){
            itemindices.push_back(Tpower_);
        }
    }

    if(m_isenergy && m_isfilter){
        itemindices.push_back(Filtered_);
    }
	if(m_rectslit && m_confsel[aperture_] == NormSlitLabel
        && (contains(m_calctype, menu::fluxpeak) || contains(m_calctype, menu::ppower)))
    {
		itemindices.push_back(AptDX_);
		itemindices.push_back(AptDY_);
	}
	if(contains(m_calctype, menu::camp)){
        itemindices.push_back(FieldRex_);
        itemindices.push_back(FieldImx_);
        itemindices.push_back(FieldRey_);
        itemindices.push_back(FieldImy_);
	}
	if(contains(m_calctype, menu::allharm)){
        itemindices.push_back(Harmonic_);
	}
}

#endif