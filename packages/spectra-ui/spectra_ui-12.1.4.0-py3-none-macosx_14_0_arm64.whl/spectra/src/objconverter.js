"use strict";

const OptionLabel =  "Options";
const PrmTableLabel = "PRMTABLE";
const ImportPaticleLabel = "Import Particles";
const CurrProfLabel = "Import Current Profile";
const EtProfLabel = "Import E-t Profile";

// accelerator injection conditions
const InjectionPrmsLabel = {
    xy:"x,y (mm)",
    xyp:"x',y' (mrad)"
};

const AccOptionsLabel = {
    bunchtype:["Bunch Profile",
        [GaussianLabel, CurrProfLabel, EtProfLabel, ImportPaticleLabel]],
    bunchdata:["Particle Data", FileLabel],
    currdata:["Current Profile", PlotObjLabel],    
    Etdata:["E-t Profile", PlotObjLabel],    
    injectionebm:["Injection Condition",
        [AutomaticLabel, EntranceLabel, CenterLabel, ExitLabel, CustomLabel]],
    injecprm:["InjecPrm", PrmTableLabel],
    zeroemitt:["Zero Emittance", false],
    zerosprd:["Zero Energy Spread", false],
    singlee:["Single Electron", false]
};

// light source field error parameters
const FerrPrmsLabel = {
    boffset:"Offset x,y (T)",
    ltaper:"Lin. Taper x,y (/m)",
    qtaper:"Quad. Taper x,y (/m<sup>2</sup>)"
};

// light source field error parameters
const PerrPrmsLabel = {
    seed:"Random Number Seed",
    fsigma:"&sigma;<sub>B</sub> (%)",
    psigma:"&sigma;<sub>&phi;</sub> (deg.)",
    xysigma:"&sigma;<sub>x,y</sub> (mm);"
};

// light source segment parameters
const SegPrmsLabel = {
    segments:"Number of Segments",
    hsegments:"Half Number of Segments",
    interval:"Segment Interval (m)",
    pslip:"Number of Phase Slip@&lambda;<sub>1</sub>",
    phi0:"&Delta;&phi; (&pi;)",
    phi12:"&Delta;&phi;<sub>1,2</sub> (&pi;)",
    mdist:"Matching Distance (m)"
};

// light source magnet conditions
const MagnetPrmsLabel = {
    br:"B<sub>r</sub> (T)",
    geofactor:"Geometrical Factor (x,y)",
};

const SrcOptionsLabel = {
    gaplink:["Gap-Field Relation",
        [NoneLabel, AutomaticLabel, ImpGapTableLabel]],
    gaptbl:["Gap vs. Field", PlotObjLabel],

    apple:["APPLE Configuration", false],

    field_str:["Field Structure", [AntiSymmLabel, SymmLabel]],
    endmag:["End Correction Magnet", true],

    natfocus:["Natural Focusing",
        [NoneLabel, BxOnlyLabel, ByOnlyLabel, BothLabel]],
    fielderr:["Field Offset & Taper", false],
    ferrprm:["FerrPrms", PrmTableLabel],

    phaseerr:["Add Phase Error", false],
    perrprm:["PerrPrms", PrmTableLabel],

    bmtandem:["Tandem Arrangement", false],

    segment_type:["Segmentation",
        [NoneLabel, IdenticalLabel, SwapBxyLabel, FlipBxLabel, FlipByLabel]],
    segprm:["SegPrms", PrmTableLabel],
    perlattice:["Periodic &beta; Function", false],
    magconf:["Magnet Configurations", PrmTableLabel]
};

// configuration of BPF conditions
const BPFPrmsLabel = {
    bpfcenter:"Central Energy (eV)",
    bpfwidth:"Width (eV)",
    bpfsigma:"Width (&sigma;, eV)",
    bpfmaxeff:"Max. Trans. Rate"
};

// configuration of CMD conditions
const CMDPrmsLabel = {
    HGorderxy:"HG Order Limit (X,Y)",
    HGorderx:"HG Order Limit (X)",
    HGordery:"HG Order Limit (Y)",
    maxHGorderxy:"Max. HG Order (X,Y)",
    maxHGorderx:"Max. HG Order (X)",
    maxHGordery:"Max. HG Order (Y)",
    maxmode:"Maximum CMD Order",
    fcutoff:"Flux Cutoff",
    cutoff:"Amplitude Cutoff",
    fieldgridxy:"Export Step: X,Y (mm)",
    fieldgridx:"Export Step: X (mm)",
    fieldgridy:"Export Step: Y (mm)"
};

// configuration of FEL-related parameters
const FELPrmsLabel = {
  pulseE:"Pulse Energy (mJ)",
  wavelen:"Wavelength (nm)",
  pulselen:"Pulse Length (FWHM, fs)",
  tlpulselen:"TL. Pulse Length (FWHM, fs)",
  srcsize:"Source Size (FWHM, mm)",
  waistpos:"Waist Position (m)",
  timing: "Timing (fs)",
  gdd: "GDD (fs<sup>2</sup>)",
  tod: "TOD (fs<sup>3</sup>)",

  pulseE_d:"Pulse Energy: 1,2 (mJ)",
  wavelen_d:"Wavelength: 1,2 (nm)",
  tlpulselen_d:"TL. Pulse Length: 1,2 (FWHM, fs)",
  srcsize_d:"Source Size: 1,2 (FWHM, mm)",
  waistpos_d:"Waist Position: 1,2 (m)",
  timing_d: "Timing: 1,2 (fs)",
  gdd_d: "GDD: 1,2 (fs<sup>2</sup>)",
  tod_d: "TOD: 1,2 (fs<sup>3</sup>)",

  svstep: "Step: Initial, Interval (m)",
  radstep: "Substeps for Radiation",
  eproi: "Photon Energy ROI (eV)",
  particles: "Number of Particles",
  edevstep: "e- Energy Interval",
  R56: "R<sub>56</sub> (m)"
};

const ConfigOptionsLabel = {
    filter:["Filtering",
        [NoneLabel, GenFilterLabel, BPFGaussianLabel, BPFBoxCarLabel, CustomLabel]],
    fmateri:["Filters", GridLabel],
    amateri:["Absorbers", GridLabel],
    fcustom:["Custom Filter", PlotObjLabel],
    bpfprms:["BPF Parameter", PrmTableLabel],
    estep:["Energy Step", [LinearLabel, LogLabel]],
    aperture:["Slit Aperture Size", [FixedSlitLabel, NormSlitLabel]],
    dstep:["Depth Step", 
        [LinearLabel, LogLabel, ArbPositionsLabel]],
    depthdata:["Depth-Position Data", PlotObjLabel],
	  defobs:["Define Obs. Point in", [ObsPointDist, ObsPointAngle]],
	  normenergy:["Normalize Photon Energy", false],
    powlimit:["Set Upper Limit on Power", false],
    optDx:["Optimize &Delta;X' for Computation", true],
    xsmooth:["Level of Smoothing Along X", 1],
    fouriep:["Observation in the Fourier Plane", false],
    wiggapprox:["Wiggler Approximation", false],
    esmooth:["Spectral Smoothing", false],
    smoothwin:["Smoothing Window (%)", 1, 0, 0.1],
    acclevel:["Accuracy Level", 1],
    accuracy:["Accuracy", [DefaultLabel, CustomLabel]],
    CMD:["Perform CMD?", false],
    GSModel:["Apply GS Model", false],
    GSModelXY:["GS Model X/Y", [NoneLabel, XOnly, YOnly, BothFormat]],
    CMDfld:["Export Field Profile", [NoneLabel, JSONOnly, BinaryOnly, BothFormat]],
    CMDint:["Export Intensity Profile", false],
    CMDcmp:["Compare Wigner Function", false],
    CMDcmpint:["Compare Intensity Profile", false],
    CMDprms:[CMDParameterLabel, PrmTableLabel],
    fel:["FEL Mode", [NoneLabel, FELPrebunchedLabel, FELSeedLabel, 
      FELCPSeedLabel, FELDblSeedLabel, FELSeedCustomLabel, FELReuseLabel]],
    seedspec:["Seed Spectrum", PlotObjLabel],
    FELprms:[FELConfigLabel, PrmTableLabel],
    exportInt:["Export Intermediate Data", true], 
    R56Bunch:["Bunch with Dispersion", false],
    exportEt:["E-t Data", false]
};

const PrmTableKeys = [
    AccOptionsLabel.injecprm[0],
    SrcOptionsLabel.ferrprm[0],
    SrcOptionsLabel.perrprm[0],
    SrcOptionsLabel.segprm[0],
    SrcOptionsLabel.magconf[0],
    ConfigOptionsLabel.bpfprms[0],
    ConfigOptionsLabel.CMDprms[0],
    ConfigOptionsLabel.FELprms[0]
];

function GenerateParameterMap(labels, parent, isopt = false)
{
    let keys = Object.keys(labels);
    let obj = {};
    for(let n = 0; n < keys.length; n++){
        if(isopt){
            obj[labels[keys[n]][0]] = parent;
        }
        else{
            obj[labels[keys[n]]] = parent;
        }
    }
    return obj;
}

function ConvertBunch(obj, isup)
{
    let up = {[GaussianLabel]: GaussianLabel, [CurrProfLabel]: CustomCurrent, [EtProfLabel]: CustomEt, [ImportPaticleLabel]: CustomParticle};
    let dw = {[GaussianLabel]: GaussianLabel, [CustomCurrent]: CurrProfLabel, [CustomEt]: EtProfLabel, [CustomParticle]: ImportPaticleLabel};
    if(obj.hasOwnProperty(AccPrmsLabel.bunchtype[0])){
        if(isup){
            obj[AccPrmsLabel.bunchtype[0]] = up[obj[AccPrmsLabel.bunchtype[0]]];
        }
        else{
            obj[AccPrmsLabel.bunchtype[0]] = dw[obj[AccPrmsLabel.bunchtype[0]]];    
        }                
    }
}

class ObjConverter {
    constructor()
    {
        this.m_map = {};
        this.m_map[AccLabel] = this.AssignMap(AccOptionsLabel, [
            {obj: InjectionPrmsLabel, key: AccOptionsLabel.injecprm[0]}
        ]);
        this.m_map[SrcLabel] = this.AssignMap(SrcOptionsLabel, [
            {obj: FerrPrmsLabel, key: SrcOptionsLabel.ferrprm[0]},
            {obj: PerrPrmsLabel, key: SrcOptionsLabel.perrprm[0]},
            {obj: SegPrmsLabel, key: SrcOptionsLabel.segprm[0]},
            {obj: MagnetPrmsLabel, key: SrcOptionsLabel.magconf[0]}
        ]);
        this.m_map[ConfigLabel] = this.AssignMap(ConfigOptionsLabel, [
            {obj: BPFPrmsLabel, key: ConfigOptionsLabel.bpfprms[0]},
            {obj: CMDPrmsLabel, key: ConfigOptionsLabel.CMDprms[0]},
            {obj: FELPrmsLabel, key: ConfigOptionsLabel.FELprms[0]}
        ]);
    };

    AssignMap(optionlabel, prmtbls)
    {
        let obj = GenerateParameterMap(optionlabel, OptionLabel, true);
        for(let j = 0; j < prmtbls.length; j++){
            Object.assign(obj, GenerateParameterMap(prmtbls[j].obj, prmtbls[j].key));
        }
        return obj;
    }

    Downconvert(obj)
    {
        for(let i = 0; i < MainCategories.length; i++){
            if(!obj.hasOwnProperty(MainCategories[i])){
                continue;
            }
            Object.keys(obj[MainCategories[i]]).forEach(name => {
                this.DownconvertSingle(MainCategories[i], obj[MainCategories[i]][name]);
            });
        }
        delete obj[VersionNumberLabel];
    }

    DownconvertSingle(categ, obj)
    {
        let options = {};
        Object.keys(obj).forEach(key => {
            if(this.m_map[categ].hasOwnProperty(key)){
                let oldkey = this.m_map[categ][key];
                if(oldkey == OptionLabel){
                    options[key] = obj[key];
                }
                else{
                    if(!options.hasOwnProperty(oldkey)){
                        options[oldkey] = {};
                    }
                    options[oldkey][key] = obj[key];
                }
                delete obj[key];
            }
        });
        if(categ == AccLabel){
            ConvertBunch(options, false);
        }
        obj[OptionLabel] = options;
    }

   static SkipKeys = {
    [AccLabel]: [],
    [SrcLabel]: ["phi1", "phi2", "Number of Phase Slip@&epsilon;<sub>1</sub>"],
    [ConfigLabel]: [
        "zeroemitt", "zerosprd", "zeroespread", "faalog", "repang", "withpd", "binary", 
        "Widgh (&sigma;, eV)","Max. Photon Energy (eV)", "Energy Smoothing", 
        "Zero Emittance", "Solver Interval (m)", "Algorithm for Field Amplitude",
        "Input Normalized Energy", "Angular Representation", "On-Axis Power Density",
        "Export in Binary"
    ]
   };

    static Upconvert(obj)
    {
        for(let i = 0; i < MainCategories.length; i++){
            if(!obj.hasOwnProperty(MainCategories[i])){
                continue;
            }
            Object.keys(obj[MainCategories[i]]).forEach(name => {
                this.UpconvertSingle(MainCategories[i], obj[MainCategories[i]][name]);
            });
        }
    }

    static UpconvertSingle(categ, obj)
    {
        if(!obj.hasOwnProperty(OptionLabel)){
            return;
        }
        let option = obj[OptionLabel];
        delete obj[OptionLabel];
        Object.keys(option).forEach(key => {
            if(PrmTableKeys.includes(key)){
                let obj = option[key];
                delete option[key];
                Object.assign(option, obj);
            }
            ObjConverter.SkipKeys[categ].forEach(skipkey => {
                delete option[skipkey];
            });
        });
        Object.assign(obj, option);
        if(categ == AccLabel){
            ConvertBunch(obj, true);
        }
    }

    static Compare(objs, parentkey = "")
    {
        let results = [];
        let keys = [];
        let exists = Object.keys(objs[1]);
        let currkeys = Object.keys(objs[0]);
        currkeys.forEach((key) => {
            if(!objs[1].hasOwnProperty(key)){
                keys.push([key, 1]);
            }
            else{
                exists.splice(exists.indexOf(key), 1);
            }
        })
        exists.forEach(key => {
            keys.push([key, 0]);
        })
        let keylabel = parentkey;
        if(keylabel != ""){
            keylabel += IDSeparator;
        }

        let categ = parentkey.split(IDSeparator);
        if(categ.length > 1){
            categ = categ[0];
            keys.forEach(key => {
                if(!ObjConverter.SkipKeys[categ].includes(key[0])){
                    results.push(keylabel+"Key "+key[0]+" not found in "+key[1].toString());
                }
                let index = currkeys.indexOf(key[0]);
                if(index >= 0){
                    currkeys.splice(index, 1);
                }    
            });
        }

        currkeys.forEach((key) => {
            if(objs[0][key] == null){
                if(objs[1][key] != null){
                    results.push(keylabel+"Inconsistent type "+key);
                }
            }
            else if(objs[1][key] == null){
                if(objs[0][key] != null){
                    results.push(keylabel+"Inconsistent type "+key);
                }
            }
            else if(typeof objs[0][key] == "object" && !Array.isArray(objs[0][key])){
                if(typeof objs[1][key] != "object" || Array.isArray(objs[1][key])){
                    results.push(keylabel+"Inconsistent type "+key);
                }
                else{
                    let subresults = this.Compare([objs[0][key], objs[1][key]], keylabel+key);
                    results = results.concat(subresults);
                }
            }
            else if(Array.isArray(objs[0][key])){
                if(JSON.stringify(objs[0][key]) != JSON.stringify(objs[1][key])){
                    results.push(keylabel+"Inconsistent value "+key);
                }
            }
            else if(objs[0][key] != objs[1][key]){
                results.push(keylabel+"Inconsistent value "+key);
            }
        });
        return results;
    }
}



