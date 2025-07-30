"use strict";

// program information
const Version = "12.1.4";
const AppName = "SPECTRA"
const ConfigFileName = "spectra_config.json";
const DefaultWindow = {width:880, height: 700, x:100, y: 100};
const VersionNumberLabel = "Version";

// frameworks
const PythonGUILabel = "python-gui";
const PythonScriptLabel = "python-script";
const BrowserLabel = "browser";
const ServerLabel = "server";
const TauriLabel = "tauri"

// constants
const MC2MeV = 0.510999;
const COEF_BPEAK = 1.80063;
const CC = 2.9979246e+8;
const COEF_BM_RADIUS = 3.33564;
const COEF_EC = 665.025;
const ONE_ANGSTROM_eV = 12398.4247;
const COEF_LINPWD = 4.2208e-3;
const COEF_K_VALUE = 93.3729;
const COEF_E1ST = 9.49634;
const COEF_TOTAL_POWER_ID = 3.6284427e-5;
const COEF_FLUX_UND = 1.7443e+14;
const LOGOFFSET = 1.1;
const MinimumParticles = 1000;
const MaxItems2Plot4PP = 5;

// type identifier and labels for PrmOptionList class 
const TypeLabel = "Type";
const OrgTypeLabel = "Original Type";
const SeparatorLabel = "SEPARATOR";
const SimpleLabel = "LABEL";
const BoolLabel = "boolean";
const StringLabel = "string";
const IntegerLabel = "integer";
const ArrayIntegerLabel = "integerarray";
const NumberLabel = "number";
const ArrayLabel = "array";
const IncrementalLabel = "incremental";
const ArrayIncrementalLabel = "incrarray";
const SelectionLabel = "selection";
const FileLabel = "file";
const FolderLabel = "folder";
const PlotObjLabel = "plottable";
const GridLabel = "grid";
const ColorLabel = "COLOR";

// settings saved in a configuration file
const PlotWindowsRowLabel = "Plot Windows/Row";
const SubPlotsRowLabel = "Subplots/Row";

// update level
const UpdateAll = "all";
const UpdateBeam = "beamspec";
const UpdateCurr = "beamcurrent";

// labels for Grid class
const GridColLabel = "ColLabel";
const GridTypeLabel = "ColType";
const AdditionalRows = 2;

// solver related
const CalcStatusLabel = "Calculation Status: ";
const ErrorLabel = "Error: ";
const WarningLabel = "Warning: ";
const Fin1ScanLabel = "Scan Process: ";
const ScanOutLabel = "Output File: ";
const CancellAllLabel = "Cancel All";
const CancelLabel = "Cancel";
const RemoveLabel = "Remove";
const ImportLabel = "Import";

// keys of output file
const InputLabel = "Input";
const OutputLabel = "Output";
const RelateDataLabel = "Related Data";
const ElapsedTimeLabel = "Elapsed Time (sec)";
const DataLabel = "data";
const DataDimLabel = "dimension";
const DataTitlesLabel = "titles";
const UnitsLabel = "units";
const VariablesLabel = "variables";
const DetailsLabel = "details";
const FELSecIdxLabel = "Section";
const Link2DLabel = "link2d";

// categories
const CurrentLabel = "Current";
const AccLabel = "Accelerator";
const SrcLabel = "Light Source";
const ConfigLabel =  "Configurations";
const BLLabel = "Beamline";
const OutFileLabel = "Output File";
const FMaterialLabel = "Filter Materials"
const PrePLabel = "Pre-Processing";
const CoordinateLabel = "Raw Data Export";
const MPILabel = "Parallel Computing";
const AccuracyLabel = "Numerical Accuracy";
const DataUnitLabel = "Units for Data Import";
const ScanLabel = "Scan Parameter";
const PartConfLabel = "Particle Data Format";
const PartPlotConfLabel = "Particle Data Plot";
const POLabel = "Plot Options";

const SettingPanels = [
  OutFileLabel, PartConfLabel, PartPlotConfLabel, PrePLabel, DataUnitLabel, AccuracyLabel, MPILabel
];
const InputPanels = [
  AccLabel, SrcLabel, ConfigLabel, OutFileLabel, AccuracyLabel, PartConfLabel, PrePLabel
];

const MainCategories = [AccLabel, SrcLabel, ConfigLabel];

// post-post processing labels
const PostPLabel = "Post-Processing";
const PostPResultLabel = "Processed";

// prefix for SimulationProcess instance
const CalculationIDLabel = "Calculation";

// accelerator options
const RINGLabel = "Storage Ring";
const LINACLabel = "Linear Accelerator";
const GaussianLabel = "Gaussian";
const CustomLabel = "Custom";
const EntranceLabel = "Align at Entrance";
const CenterLabel = "Align at Center";
const ExitLabel = "Align at Exit";

// light source types
const LIN_UND_Label = "Linear Undulator";
const VERTICAL_UND_Label = "Vertical Undulator";
const HELICAL_UND_Label = "Helical Undulator";
const ELLIPTIC_UND_Label = "Elliptic Undulator";
const FIGURE8_UND_Label = "Figure-8 Undulator";
const VFIGURE8_UND_Label = "Vertical Figure-8 Undulator";
const MULTI_HARM_UND_Label = "Multi-Harmonic Undulator";
const BM_Label = "Bending Magnet";
const WIGGLER_Label = "Wiggler";
const EMPW_Label = "EMPW";
const WLEN_SHIFTER_Label = "Wavelength Shifter";
const FIELDMAP3D_Label = "Field Mapping";
const CUSTOM_PERIODIC_Label = "Periodic: User Defined";
const CUSTOM_Label = "User Defined";
const SrcTypels = 
[
  LIN_UND_Label, VERTICAL_UND_Label, HELICAL_UND_Label, ELLIPTIC_UND_Label,
  FIGURE8_UND_Label, VFIGURE8_UND_Label, MULTI_HARM_UND_Label,
  BM_Label, WIGGLER_Label, EMPW_Label, WLEN_SHIFTER_Label,
  FIELDMAP3D_Label, CUSTOM_PERIODIC_Label, CUSTOM_Label
];

// light source options
const BxOnlyLabel = "Bx";
const ByOnlyLabel = "By";
const BothLabel = "Both";
const IdenticalLabel = "Identical";
const ImpGapTableLabel = "Import Table"
const SwapBxyLabel = "2nd: Swap Bx,y";
const FlipBxLabel = "2nd: Flip Bx";
const FlipByLabel = "2nd: Flip By";
const AntiSymmLabel = "Antisymmetric";
const SymmLabel = "Symmetric";

// configuration options
const FixedSlitLabel = "Fixed";
const NormSlitLabel = "Normalized";
const GenFilterLabel = "Generic Filter";
const BPFGaussianLabel = "BPF: Gaussian";
const BPFBoxCarLabel = "BPF: Boxcar";
const ArbPositionsLabel = "Export at Arbitrary Positions";
const ObsPointDist = "Position";
const ObsPointAngle = "Angle";
const CMDParameterLabel = "CMD Parameters";
const PropParameterLabel = "Wavefront Propagation Parameters"
const FELConfigLabel = "FEL Configurations"
const FELPrebunchedLabel = "Prebunched FEL";
const FELSeedLabel = "Seeded FEL";
const FELSeedCustomLabel = "Seeded width Custom Pulse";
const FELCPSeedLabel = "Seeded with Chirped Pulse";
const FELDblSeedLabel = "Seeded with Double Pulse";
const FELReuseLabel = "Reuse Bunch Factor";
const PhaseErrZPole = "Pole Number";
const PhaseErrZPos = "z (m)";
const SingleLabel = "Single Slit";
const DoubleLabel = "Double Slit";
const ThinLensLabel = "Ideal Thin Lens";

// available keys for Settings
const SettingKeys = [
  "scanconfig", "sorting", "defpaths", "lastloaded", "lastid", 
  "animinterv", "window", "plotconfigs", 
  FMaterialLabel, AccuracyLabel, DataUnitLabel, MPILabel, OutFileLabel, 
  PrePLabel, PlotWindowsRowLabel, SubPlotsRowLabel, ConfigLabel, 
  PartConfLabel, PartPlotConfLabel
];

// scan options
const Scan2D1DLabel = "1D: Single";
const Scan2DLinkLabel = "1D: Link 1st/2nd";
const Scan2D2DLabel = "2D Mesh"
const BundleScanlabel = "Bundle the output data";

// parallel computing
const ParaMPILabel = "MPI";
const MultiThreadLabel = "Multithread";

// general options
const OutFormat = "Format";
const JSONOnly = "JSON";
const ASCIIOnly = "ASCII";
const BinaryOnly = "BINARY";
const BothFormat = "Both";
const XOnly = "X";
const YOnly = "Y";
const LinearLabel = "Linear";
const LogLabel = "Logarithmic";
const LineLabel = "Line";
const LineSymbolLabel = "Line & Symbol";
const SymbolLabel = "Symbol";
const SurfaceLabel = "Surface (Color Map)";
const SurfaceShadeLabel = "Surface (Shaded)";
const PlotScatterLabel = "scatter";
const ContourLabel = "Contour";
const DefaultLabel = "Default";
const RainbowLabel = "Rainbow";
const BlackBodyLabel = "Blackbody";
const EarthLabel = "Earth";
const GreysLabel = "Greys";
const ByMaxLabel = "By Maximum";
const ForEachLabel = "For Each";
const AutomaticLabel = "Automatic";
const NoneLabel = "None";

// variables for data import
const TimeLabel = "time (fs)"
const DepthLabel = "Depth (mm)"
const NormCurrLabel = "j (A/100%.E.S)";
const BeamCurrLabel = "I (A)";
const EdevLabel = "DE/E";
const ZLabel = "z (m)";
const BxLabel = "Bx (T)";
const ByLabel = "By (T)";
const GapLabel = "Gap (mm)";
const EnergyLabel = "Energy (eV)";
const TransmLabel = "Transmission";

const EspLabel = "Energy Spread";
const EdevspLabel = "Energy Deviation & Spread"
const InstCurrentLabel = "I (A)";
const CurrentProfileTitle = "Current Profile";
const EmittxLabel = "&epsilon;<sub>x</sub> (mm.mrad)";
const EmittyLabel = "&epsilon;<sub>y</sub> (mm.mrad)";
const EmittxyLabel = "&epsilon;<sub>x,y</sub> (mm.mrad)";
const EmittTitle = "Normalized Emittance";
const BetaxLabel = "&beta;<sub>x</sub> (m)";
const BetayLabel = "&beta;<sub>y</sub> (m)";
const BetaTitleLabel = "Twiss (&beta;)";
const BetaxyAvLabel = "&beta;<sub>x,y</sub> (m)";
const AlphaxLabel = "&alpha;<sub>x</sub>";
const AlphayLabel = "&alpha;<sub>y</sub>";
const AlphaTitleLabel = "Twiss (&alpha;)";
const AlphaxyLabel = "&alpha;<sub>x,y</sub>";
const XavLabel = "&lt;x&gt; (m)";
const YavLabel = "&lt;y&gt; (m)";
const XYavLabel = "&lt;x,y&gt; (m)";
const XYTitleLabel = "Offset Position";
const XpavLabel = "&lt;x'&gt; (rad)";
const YpavLabel = "&lt;y'&gt; (rad)";
const XYpavLabel = "&lt;x',y'&gt; (rad)";
const XYpTitleLabel = "Offset Angle";

const XLabel = "x (m)";
const XpLabel = "x' (rad)";
const YLabel = "y (m)";
const YpLabel = "y' (rad)";
const EGeVLabel = "Energy (GeV)";
const SeedWavelLabel = "Wavelength (nm)";
const SeedFluxLabel = "Intensity";
const SeedPhaseLabel = "Phase (deg.)";
const ParticleTitles = [XLabel, XpLabel, YLabel, YpLabel, TimeLabel, EGeVLabel];
const SliceTitles = [TimeLabel, 
  InstCurrentLabel, EnergyLabel, EspLabel, EmittxLabel, EmittyLabel, 
  BetaxLabel, BetayLabel, AlphaxLabel, AlphayLabel, XavLabel, YavLabel, XpavLabel, YpavLabel];

// other configurations
const JSONIndent = 2;
const IDSeparator = "::";
const PSNameLabel = "Parameter Set";
const SimplifiedLabel = "Simplified";
const FixedPointLabel = "Fixed Point Calculation";
const DefaultObjName = "sample";

// preprocessing menus
// accelerator
const PPBetaLabel = "betatron Functions";
const PPPartAnaLabel = "Analyze Particle Data";
const CustomSlice = "Slice Parameters";
const CustomCurrent = "Current Profile";
const CustomEt = "E-t Profile";
const CustomParticle = "Particle Distribution";
const SeedSpectrum = "Seed Spectrum";

// light source
const PPFDlabel = "Field Distribution";
const PP1stIntLabel = "1st Integral";
const PP2ndIntLabel = "2nd Integral";
const PPPhaseErrLabel = "Phase Error";
const PPRedFlux = "Harmonic Intensity";
const CustomField = "Field Profile";
const CustomPeriod = "Field Profile (1 Period)";
const ImportGapField = "Gap vs. Field";

// configuration
const PPFilters = "Filter/Absorber";
const PPTransLabel = "Transmission Rate";
const PPAbsLabel = "Absorption Rate";
const PPDataImpLabel = "Imported Data";
const CustomFilter = "Custom Filter";
const CustomDepth = "Depth-Position Data";

// object for selection
var PreProcessLabel = [
  {[AccLabel]: [PPBetaLabel]},
  {[SrcLabel]: [PPFDlabel, PP1stIntLabel, PP2ndIntLabel, PPPhaseErrLabel, PPRedFlux]},
  {[PPFilters]: [PPTransLabel, PPAbsLabel]}
];

// definition of ascii-file formats
const AsciiFormats = {};
AsciiFormats[CustomCurrent] = {dim: 1, items: 1, titles: [TimeLabel, BeamCurrLabel], ordinate: "Current (A)"};
AsciiFormats[CustomParticle] = {dim: 1, items: 5, titles: ParticleTitles, ordinate: ""};
AsciiFormats[CustomEt] = {dim: 2, items: 1, titles: [TimeLabel, EdevLabel, NormCurrLabel], ordinate: ""};
AsciiFormats[CustomField] = {dim: 1, items: 2, titles: [ZLabel, BxLabel, ByLabel], ordinate: "Magnetic Field (T)"};
AsciiFormats[CustomPeriod] = {dim: 1, items: 2, titles: [ZLabel, BxLabel, ByLabel], ordinate: "Magnetic Field (T)"};
AsciiFormats[ImportGapField] = {dim: 1, items: 2, titles: [GapLabel, BxLabel, ByLabel], ordinate: "Magnetic Field (T)"};
AsciiFormats[CustomFilter] = {dim: 1, items: 1, titles: [EnergyLabel, TransmLabel], ordinate: "Transmission Rate"};
AsciiFormats[CustomDepth] = {dim: 0, items: 1, titles: [DepthLabel], ordinate: DepthLabel};
AsciiFormats[SeedSpectrum] = {dim: 1, items: 2, titles: [SeedWavelLabel, SeedFluxLabel, SeedPhaseLabel], ordinate: "Intensity/Phase(deg.)"};

// titles for pre-processed plot
var AxisTitles = {};
AxisTitles[PPBetaLabel] = "Betatron Function (m)";
AxisTitles[PPFDlabel] = "Magnetic Field (T)";
AxisTitles[PP1stIntLabel] = "Electron Angle (rad)";
AxisTitles[PP2ndIntLabel] = "Electron Position (m)";
AxisTitles[PPPhaseErrLabel] = "Phase Error (degree)";
AxisTitles[PPRedFlux] = "Normalized Flux";
AxisTitles[PPTransLabel] = "Transmission Rate";
AxisTitles[PPAbsLabel] = "Absorption Rate";

// preprocessing options
const PErrThreshLabel = "Field Threshold (%)";
const PErrZcoorLabel = "Long. Coordinate";
const FiltPlotTypeLabel = "Plot Configuration";
const FiltPlotEmin = "Minimum Energy (eV)";
const FiltPlotEmax = "Maximum Energy (eV)";
const FiltPlotPoints = "Energy Points";
const FiltPlotEscale = "Energy Step";

// units for data import
const UnitMeter = "m";
const UnitCentiMeter = "cm";
const UnitMiliMeter = "mm";
const UnitRad = "rad";
const UnitMiliRad = "mrad";
const UnitSec = "s";
const UnitpSec = "ps";
const UnitfSec = "fs";
const UnitGeV = "GeV";
const UnitMeV = "MeV";
const UnitGamma = "gamma";
const UnitTesla = "Tesla";
const UnitGauss = "Gauss"
const LengthUnitLabel = [UnitMiliMeter, UnitMeter, UnitCentiMeter];
const MagFieldUnitLabel = [UnitTesla, UnitGauss];
const DepthUnitLabel = [UnitMiliMeter, UnitCentiMeter, UnitMeter];
const TimeUnitLabel = [UnitMiliMeter, UnitMeter, UnitfSec, UnitpSec, UnitSec];

// analyze particle distribution 
const XYUnits = [UnitMeter, UnitMiliMeter];
const XYpUnits = [UnitRad, UnitMiliRad];
const SUnits  = [UnitSec, UnitpSec, UnitfSec, UnitMeter, UnitMiliMeter];
const EUnits = [UnitGeV, UnitMeV, UnitGamma];

// Categories in output file
// CMD Result
const CMDResultLabel = "CMD Result";
const CMDModalFluxLabel = "Modal Flux";
const CMDFieldLabel = "Modal Profile";
const CMDIntensityLabel = "Modal Intensity";
const CMDCompareIntLabel = "Flux Density Profile";
const CMDCompareXLabel = "Wigner Func. (X,X')";
const CMDCompareYLabel = "Wigner Func. (Y,Y')";
const CMDErrorLabel = "numerical validity";
// FEL Process
const FELCurrProfile = "Current Profile";
const FELEtProfile = "E-t Profile";
const FELCurrProfileR56 = "Current Profile with Dispersion";
const FELEtProfileR56 = "E-t Profile with Dispersion";
const FELBunchFactor = "Bunch Factor";
const FELPulseEnergy = "Pulse Energy";
const FELEfield = "On-Axis Field";
const FELInstPower = "Inst. Power";
const FELSpectrum = "Spectrum";
// Wigner propagation
const SProfLabel = "Spatial Profile";
const AProfLabel = "Angular Profile (Source)";
const WignerLabel = "Wigner Function";
const OptAProfLabel = "Angular Profile (Optical Element)";
const OptWignerLabel = "Wigner Function (Optical Element)";
const CSDLabel = "Cross Spectral Density";
const DegCohLabel = "Degree of Coherence";
const CSDLabelx = "Cross Spectral Density (x)";
const DegCohLabelx = "Degree of Coherence (x)";
const WignerLabelx = "Wigner Function (x)";
const CSDLabely = "Cross Spectral Density (y)";
const DegCohLabely = "Degree of Coherence (y)";
const WignerLabely = "Wigner Function (y)";
const WigXLabel = "X";
const WigXpLabel = "X'";
const WigYLabel = "Y";
const WigYpLabel = "Y'";
const BeamSizeLabel = "Beam Size";

// CMD information for futher processing
const MaxOrderLabel = "maxorder";
const WavelengthLabel = "wavelength";
const SrcSizeLabel = "size";
const OrderLabel = "order";

// CMD labels for futher processing
const AmplitudeReLabel = "anm.re";
const AmplitudeImLabel = "anm.im";
const AmplitudeVReLabel = "anmv.re";
const AmplitudeVImLabel = "anmv.im";
const AmplitudeIndexReLabel = "anmidx.re";
const AmplitudeIndexImLabel = "anmidx.im";
const NormFactorLabel = "coefficient";
const FluxCMDLabel = "photon flux";
const MatrixErrLabel = "Matrix Error";
const FluxErrLabel = "Flux Consistency";
const WignerErrLabel = "Wigner Function Consistency";

// short variable names for Post-Processing
const ShortTitles = {
  "GA. Brilliance": "Brilliance",
  "Harmonic Energy": "Energy"
}

// Menu Items
const GUILabels = {
  // tab titles
  Tab: {
    main: "Main Parameters",
    preproc: "Pre-Processing",
    postproc: "Post-Processing"
  },

  // menu titles
  Menu: {
    file: "File",
    calc: "Select Calculation",
    run: "Run",
    prmset: "Parameter Set",
    edit: "Edit",
    help: "Help"
  },

    // category
  Category: {
    bl: BLLabel,
    acc: AccLabel,
    src: SrcLabel,
    config: ConfigLabel,
    outfile: OutFileLabel,
    accuracy: AccuracyLabel,
    unit: UnitsLabel,
    MPI: MPILabel,
    partconf: PartConfLabel,
    partplot: PartPlotConfLabel
  },
  
  // file
  file: {
    new: "Create a New Parameter File",
    open: "Open a Parameter File",
    append: "Append Parameter Sets",
    loadf: "Load Output File",
    outpostp: "Open Post-Processed Result",
    wignerCMD: "Wigner Function for CMD",
    wignerProp: "Wigner Function for Wavefront Propagation",
    CMDr: "CMD Result for Modal Profile",
    bunch: "Bunch Factor for Coherent Radiation",
    save: "Save",
    saveas: "Save As",
    saveas11: "Save As (ver.11)",
    exit: "Exit"
  },

  // run
  run: {
    process: "Create a New Process",
    export: "Export Calculation Settings",
    start: "Start Calculation",
    cancel: CancelLabel,
    python: "Python Script",
    scanout: ScanOutLabel  
  },

  // prmset
  prmset: {
    bl: BLLabel,
    acc: AccLabel,
    src: SrcLabel,
    config: ConfigLabel,
    editprm: "Edit Parameter Set",  
  },
 
  // edit
  edit: {
    material: "Filter/Absorber Material",
    unit: DataUnitLabel,
    accuracy: AccuracyLabel,
    MPI: MPILabel,  
  },

  // help
  help: {
    reference: "Open Reference Manual",
    about: "About SPECTRA",  
  },

  // post-processor buttons
  postproc: {
    import: ImportLabel,
    ascii: "Export as ASCII",
    duplicate: "Duplicate Plot",
    clear: "Clear",
    remove: "Remove",  
    dload: "Download",
    dataname: "Data Name",
    datatype: "Data Type",
    xaxis: "x axis",
    xyaxis: "x-y axis",
    item: "Items to Plot",
    comparative: "Comparative Plot",
    multiplot: "Multiple Plot",
  },

  // data types
  datatype: {
    output:OutputLabel,
    cmdflux:CMDModalFluxLabel, 
    cmdfld:CMDFieldLabel, 
    cmdint:CMDIntensityLabel, 
    cmdcompint:CMDCompareIntLabel, 
    cmdcompx:CMDCompareXLabel, 
    cmdcompy:CMDCompareYLabel, 
    currprof:FELCurrProfile, 
    felEtprof:FELEtProfile, 
    felcurrR56:FELCurrProfileR56, 
    felEtprofR56:FELEtProfileR56, 
    felbunchF:FELBunchFactor, 
    felpulseE:FELPulseEnergy, 
    felefld:FELEfield, 
    felinstP:FELInstPower, 
    felspectrum:FELSpectrum,
    felsprof:SProfLabel, 
    bmsize:BeamSizeLabel, 
    aprof:AProfLabel, 
    oaprof:OptAProfLabel, 
    wigner4d:WignerLabel,
    owigner:OptWignerLabel,
    wignerx:WignerLabelx,
    wignery:WignerLabely, 
    csd4d:CSDLabel,
    csdx:CSDLabelx, 
    csdy:CSDLabely, 
    degcoh2d:DegCohLabel, 
    degcohx:DegCohLabelx, 
    degcohy:DegCohLabely
  },

  // pre-processor buttons
  preproc: {
    import: ImportLabel,
    load: "Load",
    units: "Edit Units"  
  }
};

// labels to classify the calculation menu
const CalcIDSCheme = "Numerical Scheme";
const CalcIDMethod = "Method";
const CalcIDMainTarget  = "Main Target Item";
const CalcIDCondition = "Condition";
const CalcIDSubCondition = "Sub-Condition";

// Calculation Items
const CalcLabels = {
  [CalcIDSCheme]: {
    far: "Far Field & Ideal Condition",
    near: "Near Field",
    cohrad: "Coherent Radiation",
    srcpoint: "Characterization at the Source Point",
    CMD: "Coherent Mode Decomposition",
    propagate: "Wavefront Propagation",
    fixed: FixedPointLabel
  },

  [CalcIDMethod]: {
    energy: "Energy Dependence",
    spatial: "Spatial Dependence",
    Kvalue: "K Dependence",
    temporal: "Time Dependence",
    wigner: "Wigner Function"
  },

  [CalcIDMainTarget]: {
    fdensa: "Angular Flux Density",
    pflux: "Partial Flux",
    tflux: "Total Flux",  
    pdensa: "Angular Power Density",
    ppower: "Partial Power",  
    pdensr: "Resolved Power Density",
    fdenss: "Spatial Flux Density",
    pdenss: "Spatial Power Density",
    spdens: "Surface Power Density",
    vpdens: "Volume Power Density",
    CMD2d: "CMD with the Wigner Function",
    CMDPP: "Modal Profile",
    CMDcheck: "Check Validity",
    efield: "Electric Field",
    camp: "Complex Amplitude",
    phasespace: "Phase-Space Distribution",
    sprof: SProfLabel
  },

  [CalcIDCondition]: {
    slitrect: "Rectangular Slit",
    slitcirc: "Circular Slit",
    along: "Along Axis",
    meshxy: "Mesh: x-y",
    meshrphi: "Mesh: r-&phi;",    
    simpcalc: "Simplified Calculation",
    fluxfix: "Flux at a Fixed Energy",
    fluxpeak: "Peak Flux Curve",
    powercv: "Power",
    xzplane: "Planar Surface: x-z",
    yzplane: "Planar Surface: y-z",
    pipe: "Cylindrical Surface",
    XXpslice: "X-X' (Sliced)",
    XXpprj: "X-X' (Projected)",
    YYpslice: "Y-Y' (Sliced)",
    YYpprj: "Y-Y' (Projected)",
    XXpYYp: "X-X'-Y-Y'"
  },

  [CalcIDSubCondition]: {
    tgtharm: "Target Harmonics",
    allharm: "All Harmonics",
    Wslice: "Sliced",
    WprjX: "Projected on X-X'",
    WprjY: "Projected on Y-Y'",
    Wrel: "Related Characteristics"
  }
}

// bundle GUI label items
var MenuLabels = {};
Object.keys(GUILabels).forEach(type => {
  Object.assign(MenuLabels, GUILabels[type])
});
Object.keys(CalcLabels).forEach(type => {
  Object.assign(MenuLabels, CalcLabels[type]);
});

// Menus in the main menu bar
const FileMenus = 
[
  {
    label:MenuLabels.new
  },
  {
    label:MenuLabels.open
  },
  {
    label:MenuLabels.append
  },
  {
    type:"separator"
  },
  {
    label:MenuLabels.loadf,
    submenu: [
      {
        label:MenuLabels.postproc
      },
      {
        type:"separator"
      },
      {
        label:MenuLabels.wignerCMD
      },
      {
        label:MenuLabels.wignerProp
      },
      {
        label:MenuLabels.CMDr
      },
      {
        label:MenuLabels.bunch
      },            
    ]
  },
  {
    label:MenuLabels.outpostp
  },
  {
    type:"separator"
  },
  {
    label:MenuLabels.save
  },
  {
    label:MenuLabels.saveas
  },
  {
    label:MenuLabels.saveas11
  },
  {
    type:"separator"
  },
  {
    label:MenuLabels.exit
  }
];

const CalcMenus = 
[
  {
    label:MenuLabels.far,
    submenu:[
      {
        label:MenuLabels.energy,
        submenu:[
          {
            label:MenuLabels.fdensa
          },
          {
            label:MenuLabels.pflux,
            submenu:[
              {
                label:MenuLabels.slitrect
              },
              {
                label:MenuLabels.slitcirc
              },
            ]          
          },
          {
            label:MenuLabels.tflux
          },
          {
            type:"separator"
          },
          {
            label:MenuLabels.simpcalc,
          }
        ]
      },      
      {
        label:MenuLabels.spatial,
        submenu:[
          {
            label:MenuLabels.fdensa,
            submenu:[
              {
                label:MenuLabels.along,
              },
              {
                label:MenuLabels.meshxy,
              },
              {
                label:MenuLabels.meshrphi,
              }
            ]
          },
          {
            label:MenuLabels.pdensa,
            submenu:[
              {
                label:MenuLabels.along,
              },
              {
                label:MenuLabels.meshxy,
              },
              {
                label:MenuLabels.meshrphi,
              }
            ]
          },
          {
            label:MenuLabels.pdensr,
            submenu:[
              {
                label:MenuLabels.along,
              },
              {
                label:MenuLabels.meshxy,
              },
              {
                label:MenuLabels.meshrphi,
              }
            ]
          },
          {
            type:"separator"
          },
          {
            label:MenuLabels.vpdens,
          }
        ]
      },
      {
        label:MenuLabels.Kvalue,
        submenu:[
          {
            label:MenuLabels.simpcalc,
            submenu:[
              {
                label:MenuLabels.tgtharm,
              },
              {
                label:MenuLabels.allharm,
              }
            ]
          },
          {
            label:MenuLabels.fluxfix,
            submenu:[
              {
                label:MenuLabels.fdensa
              },
              {
                label:MenuLabels.pflux,
                submenu:[
                  {
                    label:MenuLabels.slitrect
                  },
                  {
                    label:MenuLabels.slitcirc
                  },
                ]          
              }
            ]
          },
          {
            label:MenuLabels.fluxpeak,
            submenu:[
              {
                label:MenuLabels.fdensa,
                submenu:[
                  {
                    label:MenuLabels.tgtharm,
                  },
                  {
                    label:MenuLabels.allharm,
                  }
                ]
              },
              {
                label:MenuLabels.pflux,
                submenu:[
                  {
                    label:MenuLabels.slitrect,
                    submenu:[
                      {
                        label:MenuLabels.tgtharm,
                      },
                      {
                        label:MenuLabels.allharm,
                      }
                    ]
                  },
                  {
                    label:MenuLabels.slitcirc,
                    submenu:[
                      {
                        label:MenuLabels.tgtharm,
                      },
                      {
                        label:MenuLabels.allharm,
                      }
                    ]
                  },
                ]          
              }
            ]
          },
          {
            label:MenuLabels.powercv,
            submenu:[
              {
                label:MenuLabels.pdensa
              },
              {
                label:MenuLabels.ppower,
                submenu:[
                  {
                    label:MenuLabels.slitrect
                  },
                  {
                    label:MenuLabels.slitcirc
                  },
                ]          
              }
            ]
          }
        ]
      },
    ]
  },
  {
    type:"separator"
  },
  {
    label:MenuLabels.near,
    submenu:[
      {
        label:MenuLabels.energy,
        submenu:[
          {
            label:MenuLabels.fdenss
          },
          {
            label:MenuLabels.pflux,
            submenu:[
              {
                label:MenuLabels.slitrect
              },
              {
                label:MenuLabels.slitcirc
              },
            ]          
          }
        ]
      },
      {
        label:MenuLabels.spatial,
        submenu:[
          {
            label:MenuLabels.fdenss,
            submenu:[
              {
                label:MenuLabels.along,
              },
              {
                label:MenuLabels.meshxy,
              },
              {
                label:MenuLabels.meshrphi,
              }
            ]
          },
          {
            label:MenuLabels.pdenss,
            submenu:[
              {
                label:MenuLabels.along,
              },
              {
                label:MenuLabels.meshxy,
              },
              {
                label:MenuLabels.meshrphi,
              }
            ]
          },
          {
            label:MenuLabels.spdens,
            submenu:[
              {
                label:MenuLabels.xzplane,
              },
              {
                label:MenuLabels.yzplane,
              },
              {
                label:MenuLabels.pipe,
              }
            ]
          },
          {
            type:"separator"
          },
          {
            label:MenuLabels.vpdens,
          }
        ]
      },
    ]
  },
  {
    label:MenuLabels.cohrad,
    submenu:[
      {
        label:MenuLabels.energy,
        submenu:[
          {
            label:MenuLabels.fdenss
          },
          {
            label:MenuLabels.pflux,
            submenu:[
              {
                label:MenuLabels.slitrect
              },
              {
                label:MenuLabels.slitcirc
              },
            ]          
          }
        ]
      },
      {
        label:MenuLabels.spatial,
        submenu:[
          {
            label:MenuLabels.camp,
            submenu:[
              {
                label:MenuLabels.along,
              },
              {
                label:MenuLabels.meshxy,
              },
              {
                label:MenuLabels.meshrphi,
              }
            ]
          },
          {
            label:MenuLabels.fdenss,
            submenu:[
              {
                label:MenuLabels.along,
              },
              {
                label:MenuLabels.meshxy,
              },
              {
                label:MenuLabels.meshrphi,
              }
            ]
          },
          {
            label:MenuLabels.pdenss,
            submenu:[
              {
                label:MenuLabels.along,
              },
              {
                label:MenuLabels.meshxy,
              },
              {
                label:MenuLabels.meshrphi,
              }
            ]
          }
        ]
      },
      {
        label:MenuLabels.temporal,
        submenu:[
          {
            label:MenuLabels.efield
          },
          {
            label:MenuLabels.pdenss
          },
          {
            label:MenuLabels.ppower,
            submenu:[
              {
                label:MenuLabels.slitrect
              },
              {
                label:MenuLabels.slitcirc
              },
            ]
          },
        ]
      }
    ]
  },
  {
    label:MenuLabels.srcpoint,
    submenu:[
      {
        label:MenuLabels.wigner,
        submenu:[
          {
            label:MenuLabels.energy
          },
          {
            label:MenuLabels.Kvalue,
            submenu:[
              {
                label:MenuLabels.tgtharm,
              },
              {
                label:MenuLabels.allharm,
              }
            ]
          },
          {
            type:"separator"
          },
          {
            label:MenuLabels.phasespace,
            submenu:[
              {
                label:MenuLabels.XXpslice
              },
              {
                label:MenuLabels.XXpprj
              },
              {
                label:MenuLabels.YYpslice
              },
              {
                label:MenuLabels.YYpprj
              },
              {
                label:MenuLabels.XXpYYp
              },
            ]
          },
        ]
      },
      {
        type:"separator"
      },
      {
        label:MenuLabels.sprof
      }
    ]
  },
  {
    type:"separator"
  },
  {
    label:MenuLabels.fixed,
    submenu:[
      {
        label:MenuLabels.far,
        submenu:[
          {
            label:MenuLabels.fdensa
          },
          {
            label:MenuLabels.pflux,
            submenu:[
              {
                label:MenuLabels.slitrect
              },
              {
                label:MenuLabels.slitcirc
              },
            ]          
          },
          {
            label:MenuLabels.tflux
          },
          {
            type:"separator"
          },
          {
            label:MenuLabels.pdensa
          },
          {
            label:MenuLabels.ppower,
            submenu:[
              {
                label:MenuLabels.slitrect
              },
              {
                label:MenuLabels.slitcirc
              },
            ]          
          },
          {
            type:"separator"
          },
          {
            label:MenuLabels.simpcalc
          }
        ]
      },
      {
        type:"separator"
      },
      {
        label:MenuLabels.near,
        submenu:[
          {
            label:MenuLabels.fdenss
          },
          {
            label:MenuLabels.pflux,
            submenu:[
              {
                label:MenuLabels.slitrect
              },
              {
                label:MenuLabels.slitcirc
              },
            ]          
          },
          {
            type:"separator"
          },
          {
            label:MenuLabels.pdenss
          },
          {
            label:MenuLabels.ppower,
            submenu:[
              {
                label:MenuLabels.slitrect
              },
              {
                label:MenuLabels.slitcirc
              },
            ]          
          },
          {
            label:MenuLabels.spdens
          }
        ]
      },
      {
        label:MenuLabels.cohrad,
        submenu:[
          {
            label:MenuLabels.fdenss
          },
          {
            label:MenuLabels.pflux,
            submenu:[
              {
                label:MenuLabels.slitrect
              },
              {
                label:MenuLabels.slitcirc
              },
            ]          
          },
          {
            type:"separator"
          },
          {
            label:MenuLabels.pdenss
          },
          {
            label:MenuLabels.ppower,
            submenu:[
              {
                label:MenuLabels.slitrect
              },
              {
                label:MenuLabels.slitcirc
              },
            ]          
          }
        ]
      },
      {
        label:MenuLabels.wigner,
        submenu:[
          {
            label:MenuLabels.Wslice
          },
          {
            label:MenuLabels.WprjX
          },
          {
            label:MenuLabels.WprjY
          },
          {
            label:MenuLabels.Wrel
          }
        ]
      }        
    ]
  },
  {
    type:"separator"
  },
  {
    label:MenuLabels.CMD,
    submenu:[
      {
        label:MenuLabels.CMD2d
      },
      {
        label:MenuLabels.CMDPP
      }
      /*,{
        label:MenuLabels.CMDcheck
      }*/
    ]
  },
  {
    label:MenuLabels.propagate
  }
];

const RunMenus = [
  {
    label:MenuLabels.process
  },
  {
    label:MenuLabels.export
  },
  {
    label:MenuLabels.start
  }
];

const PrmsetMenus = [
  {
    label:MenuLabels.bl,
    submenu: [
    ]
  },  
  {
    label:MenuLabels.acc,
    submenu: [
    ]
  },  
  {
    label:MenuLabels.src,
    submenu: [
    ]
  },  
  {
    label:MenuLabels.config,
    submenu: [
    ]
  },  
  {
    type:"separator"
  },
  {
    label:MenuLabels.editprm
  },
];

const EditMenus = [
  {
    label:MenuLabels.material
  },  
  {
    label:MenuLabels.unit
  },  
  {
    label:MenuLabels.accuracy
  },  
  {
    label:MenuLabels.MPI
  }
];

const HelpMenus = [
  {
    label:MenuLabels.reference
  },  
  {
    label:MenuLabels.about
  }
];

const Menubar = [
  {[MenuLabels.file]: FileMenus},
  {[MenuLabels.calc]: CalcMenus},
  {[MenuLabels.run]: RunMenus},
  {[MenuLabels.prmset]: PrmsetMenus},
  {[MenuLabels.edit]: EditMenus},
  {[MenuLabels.help]: HelpMenus}
];

//---------- Parameter List ----------
// accelerator parameters
const BunchProfiles = 
[
  GaussianLabel,
  {[CustomLabel]: [CustomCurrent, CustomEt, CustomParticle]}
];

const AccPrmsLabel = {
    type:[TypeLabel, [RINGLabel, LINACLabel], SelectionLabel], 
    eGeV:["Energy (GeV)", 8],
    imA:["Current (mA)", 100],
    aimA:["Avg. Current (mA)", 100],
    cirm:["Circumference (m)", 1435.95],
    bunches:["Bunches", 203, IntegerLabel, 1],
    pulsepps:["Pulses/sec", 60, IntegerLabel, 1],
    bunchlength:["&sigma;<sub>z</sub> (mm)", 3.9],
    bunchcharge:["Bunch Charge (nC)", 0.1],
    emitt:["Nat. Emittance (m.rad)", 2.4e-9],
    coupl:["Coupling Constant", 0.002],
    espread:["Energy Spread", 0.0011],
    beta:["&beta;<sub>x,y</sub> (m)", [31.2, 5]],
    alpha:["&alpha;<sub>x,y</sub>", [0, 0]],
    eta:["&eta;<sub>x,y</sub> (m)", [0.146, 0]],
    etap:["&eta;'<sub>x,y</sub>", [0, 0]],
    peakcurr:["Peak Current (A)", null],
    epsilon:["&epsilon;<sub>x,y</sub> (m.rad)", [null, null]],
    sigma:["&sigma;<sub>x,y</sub> (mm)", [null, null]],
    sigmap:["&sigma;'<sub>x,y</sub> (mrad)", [null, null]],
    gaminv:["&gamma;<sup>-1</sup> (mrad)", null],

    buf_eGeV:["Buffer: Energy", null],
    buf_bunchlength:["Buffer: &sigma;<sub>z</sub>", null],
    buf_bunchcharge:["Buffer: Bunch Charge", null],
    buf_espread:["Bffer: Energy Spread", null],

    bunchtype:["Bunch Profile", BunchProfiles, SelectionLabel],
    bunchdata:[CustomParticle, FileLabel],
    currdata:[CustomCurrent, PlotObjLabel],    
    Etdata:[CustomEt, PlotObjLabel],

    injectionebm:["Injection Condition",
        [AutomaticLabel, EntranceLabel, CenterLabel, ExitLabel, CustomLabel], SelectionLabel],
    xy:["x,y (mm)", [0, 0]],
    xyp:["x',y' (mrad)", [0, 0]],
    
    zeroemitt:["Zero Emittance", false],
    zerosprd:["Zero Energy Spread", false],
    singlee:["Single Electron", false],

    R56add:["Additional R<sub>56</sub> (m)", 0],

    minsize:["Beam Size Lower Limit (m)", 1.0e-12],
    partform:[PartConfLabel, null]
};

const AccPrmsScans = [
  AccPrmsLabel.eGeV[0],
  AccPrmsLabel.imA[0],
  AccPrmsLabel.bunchcharge[0],
  AccPrmsLabel.bunchlength[0],
  AccPrmsLabel.emitt[0],
  AccPrmsLabel.coupl[0],
  AccPrmsLabel.espread[0],
  AccPrmsLabel.beta[0],
  AccPrmsLabel.alpha[0],
  AccPrmsLabel.eta[0],
  AccPrmsLabel.etap[0],
  AccPrmsLabel.xy[0],
  AccPrmsLabel.xyp[0]
];

const AccLabelOrder = [
    "type",
    "eGeV",
    "imA",
    "aimA",
    "cirm",
    "bunches",
    "pulsepps",
    "bunchlength",
    "bunchcharge",
    "emitt",
    "coupl",
    "espread",
    "beta",  
    "alpha",
    "eta",
    "etap",
    "peakcurr",
    "epsilon",
    "sigma",
    "sigmap",
    "gaminv",

    "buf_eGeV",
    "buf_bunchlength",
    "buf_bunchcharge",
    "buf_espread",

    SeparatorLabel,
    "bunchtype",
    "bunchdata",
    "currdata",
    "Etdata",
    SeparatorLabel,
    "injectionebm",
    "xy",
    "xyp",
    SeparatorLabel,
    "zeroemitt",
    "zerosprd",
    "singlee",
    SeparatorLabel,
    "R56add",
    SeparatorLabel,
    "minsize",
    "partform"
];

// light source parameters
const SrcTypes = [
  {"Undulators": [LIN_UND_Label, VERTICAL_UND_Label, HELICAL_UND_Label,
    ELLIPTIC_UND_Label, FIGURE8_UND_Label, VFIGURE8_UND_Label, MULTI_HARM_UND_Label]},
  {"BMs and Wigglers":[BM_Label, WIGGLER_Label, EMPW_Label, WLEN_SHIFTER_Label]},
  {"Custom": [FIELDMAP3D_Label, CUSTOM_PERIODIC_Label, CUSTOM_Label]}
];

const SrcPrmsLabel = {
    type:[TypeLabel, SrcTypes, SelectionLabel], 
    gap:[GapLabel, 8],
    bxy:["B<sub>x,y</sub> (T)", [0.5, 0.5]],
    b:["B (T)", 0.679498],
    bmain:["Main Field (T)", 1],
    subpoleb:["Sub Field (T)", 1],
    lu:["&lambda;<sub>u</sub> (mm)", 32],
    devlength:["Device Length (m)", 4.564],
    reglength:["Reg. Magnet Length (m)", null],
    periods:["# of Reg. Periods", 10],
    Kxy0:["K<sub>0x,0y</sub>", [0.6,1.0]],
    phase:["Phase Shift (mm)", 0],
    Kxy:["K<sub>x,y</sub>", [1.0, 1.0]],
    K:["K value", 1],
    Kperp:["K<sub>&perp;</sub>", null],
    e1st:["&epsilon;<sub>1st</sub> (eV)", 12000],
    lambda1:["&lambda;<sub>1st</sub> (nm)", 1],
    radius:["&rho; (m)", 39.2718],
    bendlength:["BM Length (m)", 2.8],
    fringelen:["BM Fringe Length (m)", 0.05],
    mplength:["Main Length (m)", 0.1],
    subpolel:["Sub Length (m)", 0.05],
    bminterv:["BM Interval (m)", 5],
    csrorg:["Origin for CSR (m)", 0],
    fvsz:[CustomField, PlotObjLabel],
    fvsz1per:[CustomPeriod, PlotObjLabel],
    fmap:["Field Mapping Data", FileLabel],
    multiharm:["Harmonic Component", GridLabel],

    sigmar:["&sigma;<sub>r,r'</sub> (mm,mrad)", [null, null]],
    sigmarx:["&sigma;<sub>rx,rx'</sub> (mm,mrad)", [null, null]],
    sigmary:["&sigma;<sub>ry,ry'</sub> (mm,mrad)", [null, null]],
    Sigmax:["&Sigma;<sub>x,x'</sub> (mm,mrad)", [null, null]],
    Sigmay:["&Sigma;<sub>y,y'</sub> (mm,mrad)", [null, null]],
    fd:["Flux Density", null],
    flux:["Flux<sub>1st</sub>", null],
    brill:["Brilliance<sub>1st</sub>", null],
    pkbrill:["Peak Brilliance", null],
    degener:["Bose Degeneracy", null],
    ec:["&epsilon;<sub>c</sub> (eV)", null],
    lc:["&lambda;<sub>c</sub> (nm)", null],
    tpower:["Total Power (kW)", null],
	  tpowerrev:["Total Power/Rev. (kW)", null],
    linpower:["Lin. Pow. Density (kW/mrad)", null],

    gaplink:["Gap-Field Relation",
        [NoneLabel, AutomaticLabel, ImpGapTableLabel], SelectionLabel],
    br:["B<sub>r</sub> (T)", 1.2],
    geofactor:["Geometrical Factor (x,y)", [0.6, 0.9]],
    gaptbl:[ImportGapField, PlotObjLabel],
    apple:["APPLE Configuration", false],
    field_str:["Field Structure", [AntiSymmLabel, SymmLabel], SelectionLabel],
    endmag:["End Correction Magnet", true],
    natfocus:["Natural Focusing",
        [NoneLabel, BxOnlyLabel, ByOnlyLabel, BothLabel], SelectionLabel],
    fielderr:["Field Offset & Taper", false],
    boffset:["Offset x,y (T)", [0,0]],
    ltaper:["Lin. Taper x,y (/m)", [0,0]],
    qtaper:["Quad. Taper x,y (/m<sup>2</sup>)", [0,0]],   
    phaseerr:["Add Phase Error", false],
    seed:["Random Number Seed", 1, IntegerLabel, 1],
    fsigma:["&sigma;<sub>B</sub> (%)", 0.5],
    psigma:["&sigma;<sub>&phi;</sub> (deg.)", 5],
    xysigma:["&sigma;<sub>x,y</sub> (mm);", [1e-3,1e-3]],
    bmtandem:["Tandem Arrangement", false],
    segment_type:["Segmentation",
        [NoneLabel, IdenticalLabel, SwapBxyLabel, FlipBxLabel, FlipByLabel], SelectionLabel],
    segments:["Number of Segments", 2, IntegerLabel, 2],
    hsegments:["Half Number of Segments", 1, IntegerLabel, 1],
    interval:["Segment Interval (m)", 5],
    pslip:["Number of Phase Slip@&lambda;<sub>1</sub>", null],
    phi0:["&Delta;&phi; (&pi;)", 1],
    phi12:["&Delta;&phi;<sub>1,2</sub> (&pi;)", [0.5,1.5]],
    mdist:["Matching Distance (m)", 5],
    perlattice:["Periodic &beta; Function", false]
};

const SrcPrmsScans = [
  SrcPrmsLabel.gap[0],
  SrcPrmsLabel.bxy[0],
  SrcPrmsLabel.b[0],
  SrcPrmsLabel.bmain[0],
  SrcPrmsLabel.subpoleb[0],
  SrcPrmsLabel.lu[0],
  SrcPrmsLabel.devlength[0],
  SrcPrmsLabel.Kxy0[0],
  SrcPrmsLabel.phase[0],
  SrcPrmsLabel.Kxy[0],
  SrcPrmsLabel.K[0],
  SrcPrmsLabel.e1st[0],
  SrcPrmsLabel.e1st[0],
  SrcPrmsLabel.boffset[0],
  SrcPrmsLabel.ltaper[0],
  SrcPrmsLabel.qtaper[0],
  SrcPrmsLabel.phaseerr[0],
  SrcPrmsLabel.seed[0],
  SrcPrmsLabel.fsigma[0],
  SrcPrmsLabel.psigma[0],
  SrcPrmsLabel.xysigma[0],
  SrcPrmsLabel.segments[0],
  SrcPrmsLabel.hsegments[0],
  SrcPrmsLabel.interval[0],
  SrcPrmsLabel.phi0[0],
  SrcPrmsLabel.phi12[0],
  SrcPrmsLabel.mdist[0]
];

const SrcLabelOrder = [
    "type",
    "fvsz",
    "fvsz1per",
    "gap",
    "bxy",
    "b",
    "bmain",
    "subpoleb",
    "lu",
    "devlength",
    "reglength",
    "periods",
    "Kxy0",
    "phase",
    "Kxy",
    "K",
    "Kperp",
    "e1st",
    "lambda1",
    "multiharm",
    "radius",
    "bendlength",
    "fringelen",
    "mplength",
    "subpolel",
    "bminterv",
    "csrorg",
    "fmap",

    // do not change order (used in generating a reference) ==>>
    "sigmar",
    "sigmarx",
    "sigmary",
    "Sigmax",
    "Sigmay",
    "fd",
    "flux",
    "brill",
    "pkbrill",
    "degener",
    "ec",
    "lc",
    "tpower",
    "tpowerrev",
    "linpower",
    // <==

    SeparatorLabel,
    "gaplink",
    "br",
    "geofactor",
    "gaptbl",
    "apple",
    "field_str",
    "endmag",
    SeparatorLabel,
    "natfocus",
    "fielderr",
    "boffset",
    "ltaper",
    "qtaper",
    SeparatorLabel,
    "phaseerr",
    "seed",
    "fsigma",
    "psigma",
    "xysigma",
    SeparatorLabel,
    "bmtandem",
    "segment_type",
    "segments",
    "hsegments",
    "interval",
    "pslip",
    "phi0",
    "phi12",
    "mdist",
    SeparatorLabel,
    "perlattice"
];

// configurations
const ConfigPrmsLabel = {
    // calculation type
    type:[TypeLabel, "Far Field & Ideal Condition::Energy Dependence::Angular Flux Density"],

    // observation point
    slit_dist:["Distance from the Source (m)", 30],

    // auto range
    autoe: ["Auto Config. for Energy Range", false],
    autot: ["Auto Config. for Transverse Range", false],

    // harmonic
    hrange:["Harmonic Range", [1,5], ArrayIntegerLabel, 1, 1],
    hfix:["Target Harmonic", 1, IntegerLabel, 1 ,1],
    hmax:["Maximum Harmonic", 5, IntegerLabel, 1, 1],

    // energy 
    detune:["Detuning", 0],
    erange:["Energy Range (eV)", [5000,50000]],
    de:["Energy Pitch (eV)", 2],
    epitch:["Energy Pitch for Integration (eV)", 2],
    emesh:["Points (Energy)", 101, IntegerLabel, 1],
    nefix:["Normalized Energy", 1],
    efix:["Target Energy (eV)", 12661],

    // Wigner propagation options
    gridspec:["Transverse Grid", [AutomaticLabel, NormSlitLabel, FixedSlitLabel], SelectionLabel],
    grlevel: ["Finer Spatial Grid", 0, IntegerLabel, 0],
    optics: ["Optical Element", [NoneLabel, SingleLabel, DoubleLabel, ThinLensLabel], SelectionLabel],
    optpos: ["Position (m)", 25],
    aptx: ["Aperture x (mm)", 0.2], 
    aptdistx: ["Slit Distance x  (mm)", 0.4],
    apty: ["Aperture y (mm)", 0.1], 
    aptdisty: ["Slit Distance y  (mm)", 0.2],
    softedge: ["Soft Edge Fringe Size (mm)", 1e-3],
    diflim: ["Limit of Diffraction Effect", 0.02],
    memsize: ["Required Memory (MB) ~", 1000],
    foclenx: ["Focal Length x (m)", 10],
    focleny: ["Focal Length y (m)", 10],
    anglelevel: ["Larger Angular Range", 0, IntegerLabel, 0],
    wigexplabel:["Other Data to Export", SimpleLabel],
    wigner: ["Wigner Function", false],
    aprofile: ["Angular Profile", false],
    csd: [CSDLabel, false],
    degcoh: [DegCohLabel, false],

    // transverse size, divergence
    wigsizex:["&Sigma;<sub>x,x'</sub>@Source (mm,mrad)", [null, null]],
    wigsizey:["&Sigma;<sub>y,y'</sub>@Source (mm,mrad)", [null, null]],
    bmsizex:["&Sigma;<sub>x</sub>@End (mm)", null],
    bmsizey:["&Sigma;<sub>y</sub>@End (mm)", null],

    // transverse grid for CSD
    wnxrange:["x Range/&Sigma;", [-4, 4]],
    wnyrange:["y Range/&Sigma;", [-4, 4]],
    wdxrange:["&delta;x Range (mm)", [-0.1, 0.1]],
    wdyrange:["&delta;y Range (mm)", [-0.1, 0.1]],
    wndxrange:["&delta;x Range/&Sigma;", [-0.1, 0.1]],
    wndyrange:["&delta;y Range/&Sigma;", [-0.1, 0.1]],
    wdxmesh:["Points (&delta;x)", 51],
    wdymesh:["Points (&delta;y)", 51],
    
    // obs. points
    xyfix:["Position x,y (mm)", [0,0]],
    qxyfix:["Angle &theta;<sub>x,y</sub> (mrad)", [0,0]],
    spdxfix:["Surface Pos. x (mm)", 10],
    spdyfix:["Surface Pos. y (mm)", 3],
    spdrfix:["Surface Radius (mm)", 3],
    Qnorm:["&Theta; (deg.)", 90],
    Phinorm:["&Phi; (deg.)", 90],
    Qgl:["Glancing Angle (deg.)",90 ],
    Phiinc:["Azimuth of Incidence (deg.)", 90],

    // slit
    slitpos:["Slit Pos.: x,y (mm)", [0,0]],
    qslitpos:["Slit Pos.: &theta;<sub>x,y</sub> (mrad)", [0,0]],
    nslitapt:["&Delta;/&Sigma;<sub>s</sub>: x,y", [4,4]],
    slitapt:["&Delta;x,&Delta;y (mm)", [2,1]],
    qslitapt:["&Delta;&theta;<sub>x,y</sub> (mrad)", [0.06,0.03]],
    slitr:["Slit r<sub>1,2</sub> (mm)", [0,1]],
    slitq:["Slit &theta;<sub>1,2</sub> (mrad)", [0,0.03]],
    pplimit:["Power Upper Limit (kW)", 0.3],
    illumarea:["Illuminated x,y (mm)", [null, null]],

    // obs. range 
    xrange:["x Range (mm)", [-1,1]],
    qxrange:["&theta;<sub>x</sub> Range (mrad)", [-0.03,0.03]],
    xmesh:["Points (x)", 41, IntegerLabel, 1],
    yrange:["y Range (mm)", [-0.5,0.5]],
    qyrange:["&theta;<sub>y</sub> Range (mrad)", [-0.02,0.02]],
    ymesh:["Points (y)", 41, IntegerLabel, 1],
    rrange:["r Range (mm)", [0,1]],
    qrange:["&theta; Range (mrad)", [0,0.03]],
    rphimesh:["Points (r)", 41, IntegerLabel, 1],
    qphimesh:["Points (&theta;)", 41, IntegerLabel, 1],
    phirange:["&phi; Range (deg.)", [0,90]],
    phimesh:["Points (&phi;)", 41, IntegerLabel, 1],
    drange:["Depth Range (mm)", [0,1]],
    dmesh:["Points (Depth)", 41, IntegerLabel, 1],

    // z range
    zrange:["z range (m)", [5, 6]],
    zmesh:["Points (z)", 21, IntegerLabel, 1],

    // beam size (flux, power)
    fsize:["&Sigma;<sub>x,y</sub>@&epsilon;<sub>1st</sub> (mm)", [null, null]],
    psize:["&Sigma;<sub>px,py</sub> (mm)", [null, null]],
    fdiv:["&Sigma;<sub>x',y'</sub>@&epsilon;<sub>1st</sub> (mrad)", [null, null]],
    pdiv:["&Sigma;<sub>px',py'</sub> (mrad)", [null, null]],

    // K
    krange:["K Range", [0,2.3]],
    ckrange:["K<sub>&perp;</sub> Range", [0,5.0]],
    kmesh:["Points (K)", 51, IntegerLabel, 1],
    e1strange:["&epsilon;<sub>1st</sub> Range (eV)", [null, null]],

    // temporal
    trange:["Temporal Range (fs)", [-0.05,0.05]],
    tmesh:["Points (Temporal)", 10001, IntegerLabel, 1],

    // source point
    gtacc:["&gamma;&Delta;&theta;<sub>x,y</sub>", [1,1]],
    horizacc:["X' Acceptance (mrad)", 0.1],
    Xfix:["Slice X (mm)", 0],
    Yfix:["Slice Y (mm)", 0],
    Xpfix:["Slice X' (mrad)", 0],
    Ypfix:["Slice Y' (mrad)", 0],
    Xrange:["X Range (mm)", [-1,1]],
    Xmesh:["Points (X)", 51, IntegerLabel, 1],
    Xprange:["X' Range (mrad)", [-0.05,0.05]],
    Xpmesh:["Points (X')", 41, IntegerLabel, 1],
    Yrange:["Y Range (mm)", [-0.04,0.04]],
    Ymesh:["Points (Y)", 51, IntegerLabel, 1],
    Yprange:["Y' Range (mrad)", [-0.02,0.02]],
    Ypmesh:["Points (Y')", 41, IntegerLabel, 1],

    // filtering options
    filter:["Filtering",
        [NoneLabel, GenFilterLabel, BPFGaussianLabel, BPFBoxCarLabel, CustomLabel], SelectionLabel],
    fmateri:["Filters", GridLabel],
    fcustom:[CustomFilter, PlotObjLabel],
    // BPF
    bpfcenter:["Central Energy (eV)", 10000],
    bpfwidth:["Width (eV)", 100],
    bpfsigma:["Width (&sigma;, eV)", 100],
    bpfmaxeff:["Max. Trans. Rate", 1],

    // volume density options
    amateri:["Absorbers", GridLabel],
    dstep:["Depth Step", 
        [LinearLabel, LogLabel, ArbPositionsLabel], SelectionLabel],
    depthdata:[CustomDepth, PlotObjLabel],

    // general options
	  defobs:["Define Obs. Point in", [ObsPointDist, ObsPointAngle], SelectionLabel],
	  normenergy:["Normalize Photon Energy", false],
    estep:["Energy Step", [LinearLabel, LogLabel], SelectionLabel],
    aperture:["Slit Aperture Size", [FixedSlitLabel, NormSlitLabel], SelectionLabel],
    powlimit:["Set Upper Limit on Power", false],
    optDx:["Optimize &Delta;X' for Computation", true],
    xsmooth:["Level of Smoothing Along X", 1],
    fouriep:["Observation in the Fourier Plane", false],
    wiggapprox:["Wiggler Approximation", false],
    esmooth:["Spectral Smoothing", false],
    smoothwin:["Smoothing Window (%)", 1.0, IncrementalLabel, 0.1, 0.1, 100],
    acclevel:["Accuracy Level", 0],
    accuracy:["Accuracy", [DefaultLabel, CustomLabel], SelectionLabel],

    // CMD options
    CMD:["Perform CMD?", false],
    GSModel:["Apply GS Model", false],
    GSModelXY:["GS Model X/Y", [NoneLabel, XOnly, YOnly, BothFormat], SelectionLabel],
    CMDfld:["Export Field Profile", [NoneLabel, JSONOnly, BinaryOnly, BothFormat], SelectionLabel],
    CMDint:["Export Intensity Profile", false],
    // configuration of CMD conditions
    HGorderxy:["HG Order Limit (X,Y)", [50,50]],
    HGorderx:["HG Order Limit (X)", 50],
    HGordery:["HG Order Limit (Y)", 50],
    maxHGorderxy:["Max. HG Order (X,Y)", [50,50]],
    maxHGorderx:["Max. HG Order (X)", 50],
    maxHGordery:["Max. HG Order (Y)", 50],
    maxmode:["Maximum CMD Order", 100],
    fcutoff:["Flux Cutoff", 1e-3],
    cutoff:["Amplitude Cutoff", 1e-4],
    fieldrangexy:["Range: X,Y (mm)", [1,0.2]],
    fieldrangex:["Range: X (mm)", 1],
    fieldrangey:["Range: Y (mm)", 0.2],
    fieldgridxy:["Step: X,Y (mm)", [0.005,0.002]],
    fieldgridx:["Step: X (mm)", 0.005],
    fieldgridy:["Step: Y (mm)", 0.002],
    CMDcmp:["Compare Wigner Function", false],
    CMDcmpint:["Compare Intensity Profile", false],

    // FEL options
    fel:["FEL Mode", [NoneLabel, FELPrebunchedLabel, FELSeedLabel, 
      FELCPSeedLabel, FELDblSeedLabel, FELSeedCustomLabel, FELReuseLabel], SelectionLabel],
    seedspec:[SeedSpectrum, PlotObjLabel],
    // configuration of FEL-related parameters   
    pulseE:["Pulse Energy (mJ)", 0.1],
    wavelen:["Wavelength (nm)", 267],
    pulselen:["Pulse Length (FWHM, fs)", 40],
    tlpulselen:["TL. Pulse Length (FWHM, fs)", 40],
    srcsize:["Source Size (FWHM, mm)", 1],
    waistpos:["Waist Position (m)", 0],
    timing:["Timing (fs)", 0],
    gdd:["GDD (fs<sup>2</sup>)", 0],
    tod:["TOD (fs<sup>3</sup>)", 0],
    pulseE_d:["Pulse Energy: 1,2 (mJ)", [0.1, 0.1]],
    wavelen_d:["Wavelength: 1,2 (nm)", [267, 280]],
    tlpulselen_d:["TL. Pulse Length: 1,2 (FWHM, fs)", [40, 40]],
    srcsize_d:["Source Size: 1,2 (FWHM, mm)", [1, 1]],
    waistpos_d:["Waist Position: 1,2 (m)", [0, 0]],
    timing_d:["Timing: 1,2 (fs)", [0, 0]],
    gdd_d:["GDD: 1,2 (fs<sup>2</sup>)", [0, 0]],
    tod_d:["TOD: 1,2 (fs<sup>3</sup>)", [0, 0]],
    svstep:["Step: Initial, Interval (m)", [-1,0.1]],
    radstep:["Substeps for Radiation", 5],
    eproi:["Photon Energy ROI (eV)", [1,120]],
    particles:["Number of Particles", 1000000],
    edevstep:["e- Energy Interval", 1e-4],
    R56:["R<sub>56</sub> (m)", 0],
    exportInt:["Export Intermediate Data", true], 
    R56Bunch:["Bunch with Dispersion", false],
    exportEt:["E-t Data", false]
};

const ConfigPrmsScans = [
  ConfigPrmsLabel.slit_dist[0],
  ConfigPrmsLabel.hfix[0],
  ConfigPrmsLabel.hmax[0],
  ConfigPrmsLabel.detune[0],
  ConfigPrmsLabel.epitch[0],
  ConfigPrmsLabel.nefix[0],
  ConfigPrmsLabel.efix[0],
  ConfigPrmsLabel.xyfix[0],
  ConfigPrmsLabel.qxyfix[0],
  ConfigPrmsLabel.spdxfix[0],
  ConfigPrmsLabel.spdyfix[0],
  ConfigPrmsLabel.spdrfix[0],
  ConfigPrmsLabel.Qnorm[0],
  ConfigPrmsLabel.Phinorm[0],
  ConfigPrmsLabel.Qgl[0],
  ConfigPrmsLabel.Phiinc[0],
  ConfigPrmsLabel.slitpos[0],
  ConfigPrmsLabel.qslitpos[0],
  ConfigPrmsLabel.nslitapt[0],
  ConfigPrmsLabel.slitapt[0],
  ConfigPrmsLabel.qslitapt[0],
  ConfigPrmsLabel.slitr[0],
  ConfigPrmsLabel.slitq[0],
  ConfigPrmsLabel.pplimit[0],
  ConfigPrmsLabel.gtacc[0],
  ConfigPrmsLabel.horizacc[0],
  ConfigPrmsLabel.Xfix[0],
  ConfigPrmsLabel.Yfix[0],
  ConfigPrmsLabel.Xpfix[0],
  ConfigPrmsLabel.Ypfix[0],
  ConfigPrmsLabel.bpfcenter[0],
  ConfigPrmsLabel.bpfwidth[0],
  ConfigPrmsLabel.bpfsigma[0],
  ConfigPrmsLabel.bpfmaxeff[0],
  ConfigPrmsLabel.pulseE[0],
  ConfigPrmsLabel.wavelen[0],
  ConfigPrmsLabel.pulselen[0],
  ConfigPrmsLabel.tlpulselen[0],
  ConfigPrmsLabel.srcsize[0],
  ConfigPrmsLabel.waistpos[0],
  ConfigPrmsLabel.timing[0],
  ConfigPrmsLabel.gdd[0],
  ConfigPrmsLabel.tod[0],
  ConfigPrmsLabel.pulseE_d[0],
  ConfigPrmsLabel.wavelen_d[0],
  ConfigPrmsLabel.tlpulselen_d[0],
  ConfigPrmsLabel.srcsize_d[0],
  ConfigPrmsLabel.waistpos_d[0],
  ConfigPrmsLabel.timing_d[0],
  ConfigPrmsLabel.gdd_d[0],
  ConfigPrmsLabel.tod_d[0],
  ConfigPrmsLabel.svstep[0],
  ConfigPrmsLabel.radstep[0],
  ConfigPrmsLabel.eproi[0],
  ConfigPrmsLabel.particles[0],
  ConfigPrmsLabel.R56[0]
];

const ConfigLabelOrder = [
    // calculation type
    "type",

    // observation point
    "slit_dist",

    // auto energy range
    "autoe",

    // harmonic
    "hrange",
    "hfix",
    "hmax",

    // energy 
    "detune",
    "erange",
    "de",
    "epitch",
    "emesh",
    "nefix",
    "efix",
   
    // obs. points
    "xyfix",
    "qxyfix",
    "spdxfix",
    "spdyfix",
    "spdrfix",
    "Qnorm",
    "Phinorm",
    "Qgl",
    "Phiinc",

    // slit
    "slitpos",
    "qslitpos",
    "nslitapt",
    "slitapt",
    "qslitapt",
    "slitr",
    "slitq",
    "pplimit",
    "illumarea",

    // obs. range 
    "zrange",
    "zmesh",

    "autot",
    "gridspec",
    "grlevel",

    "wigsizex",
    "bmsizex",
    "xrange",
    "qxrange",
    "wnxrange",
    "xmesh",
    "wdxrange",
    "wndxrange",
    "wdxmesh",

    "wigsizey",
    "bmsizey",
    "yrange",
    "qyrange",
    "wnyrange",
    "ymesh",
    "wdyrange",
    "wndyrange",
    "wdymesh",

    "rrange",
    "qrange",
    "rphimesh",
    "qphimesh",
    "phirange",
    "phimesh",
    "drange",
    "dmesh",

    // Wigner propagation
    "optics",
    "optpos",
    "aptx", 
    "aptdistx",
    "apty", 
    "aptdisty",
    "softedge",
    "diflim",
    "anglelevel",
    "memsize",
    "foclenx",
    "focleny",
    "wigexplabel",
    "aprofile",
    "wigner",
    "csd",
    "degcoh",

    // beam size (flux, power)
    "fsize",
    "psize",
    "fdiv",
    "pdiv",

    // K
    "krange",
    "ckrange",
    "e1strange",
    "kmesh",

    // temporal
    "trange",
    "tmesh",

    // Wigner
    "gtacc",
    "horizacc",
    "Xfix",
    "Yfix",
    "Xpfix",
    "Ypfix",
    "Xrange",
    "Xmesh",
    "Xprange",
    "Xpmesh",
    "Yrange",
    "Ymesh",
    "Yprange",
    "Ypmesh",

    // filtering options
    SeparatorLabel,
    "filter",
    "fmateri",
    "fcustom",
    // BPF
    "bpfcenter",
    "bpfwidth",
    "bpfsigma",
    "bpfmaxeff",

    SeparatorLabel,
    // volume density options
    "amateri",
    "dstep",
    "depthdata",

    SeparatorLabel,
    // general options
	  "defobs",
    "normenergy",
    "estep",
    "aperture",
    "powlimit",
    "optDx",
	  "xsmooth",
    "fouriep",
    "wiggapprox",
    "esmooth",
    "smoothwin",
    "acclevel",
    "accuracy",

    // CMD options
    SeparatorLabel,
    "CMD",
    "GSModel",
    "GSModelXY",
    "CMDfld",
    "CMDint",
    "fieldrangexy",
    "fieldrangex",
    "fieldrangey",
    "fieldgridxy",
    "fieldgridx",
    "fieldgridy",
    // configuration of CMD conditions
    SeparatorLabel,
    "HGorderxy",
    "HGorderx",
    "HGordery",
    "maxHGorderxy",
    "maxHGorderx",
    "maxHGordery",
    "maxmode",
    "fcutoff",
    "cutoff",
    SeparatorLabel,
    "CMDcmp",
    "CMDcmpint",

    // FEL options
    SeparatorLabel,
    "fel",
    "seedspec",
    // configuration of FEL-related parameters   
    "pulseE",
    "wavelen",
    "pulselen",
    "tlpulselen",
    "srcsize",
    "waistpos",
    "timing",
    "gdd",
    "tod", 
    "pulseE_d",
    "wavelen_d",
    "tlpulselen_d",
    "srcsize_d",
    "waistpos_d",
    "timing_d",
    "gdd_d",
    "tod_d",
    "svstep",
    "radstep",
    "eproi",
    "particles",
    "edevstep",
    "R56",
    "exportInt",
    "R56Bunch",
    "exportEt"
];

// custom accuracy
const AccuracyOptionsLabel = {
  integlabel:["Integration/Discretization Step", SimpleLabel],
  accdisctra:["Longitudinal Step", 1, IntegerLabel, 1],
  accinobs:["Transverse Grid", 1, IntegerLabel, 1],
  accineE:["Electron Energy Step", 1, IntegerLabel, 1],
  accinpE:["Photon Energy Step", 1, IntegerLabel, 1],
  rangelabel:["Integration Range", SimpleLabel],
  acclimtra:["Longitudinal Range", 1, IntegerLabel, 1],
  acclimobs:["Transverse Range", 1, IntegerLabel, 1],
  acclimpE:["Photon Energy Range", 1, IntegerLabel, 1],
  acclimeE:["Electron Energy Range", 1, IntegerLabel, 1],
  otherslabel:["Others", SimpleLabel],
  accconvharm:["Harmonic Convergence", 1, IntegerLabel, 1],
  accEcorr:["Energy Consistency", false],
  accconvMC:["Monte Carlo Integral Tolerance", 0.1],
  accconvMCcoh:["Coherent Radiation Integral Tolerance", 0.3],
  acclimMCpart:["Limit Macroparticles", false],
  accMCpart:["Maximum Macroparticles", 1e6]
};

const AccuracyOptionsOrder = [
  "integlabel",
  "accdisctra",
  "accinobs",
  "accineE",
  "accinpE", 
  SeparatorLabel,
  "rangelabel",
  "acclimtra",
  "acclimobs",
  "acclimpE",
  "acclimeE",
  SeparatorLabel,
  "otherslabel",
  "accconvharm",
  "accEcorr",
  "accconvMC",
  "accconvMCcoh",
  "acclimMCpart",
  "accMCpart"
];

// MPI configurations
const MPIOptionsLabel = {
  parascheme:["Parallel Computing", [NoneLabel, MultiThreadLabel, ParaMPILabel], SelectionLabel],
  processes:["Number of MPI Processes", 4, IntegerLabel],
  threads:["Number of Threads", 4, IntegerLabel]
};

const MPIOptionsOrder = [
  "parascheme",
  "processes",
  "threads"
];

// Output file
const OutputOptionsLabel = {
    fixpdata:["Output Data", GridLabel, "Calculate"],
    comment:["Comment", ""],
    format:[OutFormat, [JSONOnly, ASCIIOnly, BothFormat], SelectionLabel],
    folder:["Folder", FolderLabel],
    prefix:["Prefix", "Untitled"],
    serial:["Serial Number", -1, IntegerLabel]
};

const OutputOptionsOrder = [
    "fixpdata",
    SeparatorLabel,
    "format", 
    "folder", 
    "prefix",
    "comment",
    "serial"
];

// Units for Data Import
const DataUnitOptionsLabel = {
  gap:["Gap", LengthUnitLabel, SelectionLabel], 
  zpos:["Longitudinal Position (z)", LengthUnitLabel, SelectionLabel],
  magf:["Magnetic Field (B<sub>x,y</sub>)", [UnitTesla, UnitGauss], SelectionLabel],
  depth:["Depth for Volume Power Density", LengthUnitLabel, SelectionLabel],
  time:["Time for Bunch Profile", [UnitMiliMeter, UnitMeter, UnitfSec, UnitSec, UnitpSec], SelectionLabel],
};

const DataUnitOptionsOrder = [
  "gap",
  "zpos",
  "magf",
  "depth",
  "time"
];

// preprocessing configuration
const PreProcessPrmLabel = {
  thresh:[PErrThreshLabel, 90],
  zcoord:[PErrZcoorLabel, [PhaseErrZPole, PhaseErrZPos], SelectionLabel],
  maxharm:["Max. Harmonic", 11, IntegerLabel],
  filtauto:[FiltPlotTypeLabel, [AutomaticLabel, CustomLabel], SelectionLabel],
  filtemin:[FiltPlotEmin, 1000],
  filtemax:[FiltPlotEmax, 100000],
  filtpoints:[FiltPlotPoints, 1000, IntegerLabel, 2],
  filtscale:[FiltPlotEscale, [LinearLabel, LogLabel], SelectionLabel]
};

const PreProcessPrmOrder = [
  "thresh",
  "zcoord",
  "maxharm",
  "filtauto",
  "filtemin",
  "filtemax",
  "filtpoints",
  "filtscale"
];

// particle data file format
const ParticleConfigLabel = {
  unitlabel:["Units", SimpleLabel],
  unitxy:["x & y", XYUnits, SelectionLabel],
  unitxyp:["x' & y'", XYpUnits, SelectionLabel],
  unitt:["Time", SUnits, SelectionLabel],
  unitE:["Energy", EUnits, SelectionLabel],
  collabel:["Columns", SimpleLabel],
  colx:["x", 1, IntegerLabel, 1, 1, 6],
  colxp:["x'", 2, IntegerLabel, 1, 1, 6],
  coly:["y", 3, IntegerLabel, 1, 1, 6],
  colyp:["y'", 4, IntegerLabel, 1, 1, 6],
  colt:["t", 5, IntegerLabel, 1, 1, 6],
  colE:["E", 6, IntegerLabel, 1, 1, 6],
  pcharge:["Charge/Particle (C)", 1e-15],
  bins:["Slices in 1&sigma;<sub>s</sub>", 100, IntegerLabel, 1]
};

const ParticleConfigOrder = [
  "unitlabel",
  "unitxy",
  "unitxyp",
  "unitt",
  "unitE",
  "collabel",
  "colx",
  "colxp",
  "coly",
  "colyp",
  "colt",
  "colE",
  SeparatorLabel,
  "pcharge",
  "bins"
];

// plot particle-distribution
const PDPlotType = [CustomSlice, CustomParticle];
const XYAxisTitles = [XLabel, XpLabel, YLabel, YpLabel, TimeLabel, EGeVLabel];
const BPTitles = [CurrentProfileTitle, EdevspLabel, EmittTitle, BetaTitleLabel, AlphaTitleLabel, 
  XYTitleLabel, XYpTitleLabel];

const PDPLotConfigLabel = {
  type:["Plot Type", PDPlotType, SelectionLabel],
  xaxis:["x axis", XYAxisTitles, SelectionLabel],
  yaxis:["y axis", XYAxisTitles, SelectionLabel],
  item:["Select Item", BPTitles, SelectionLabel],
  plotparts:["Particles to Plot", 10000, IntegerLabel, 1]
};

const PDPLotConfigOrder = [
  "type",
  "xaxis",
  "yaxis",
  "item",
  "plotparts"
];

//---------- Parameter List ----------

// built-in filters
const FilterMaterial = {
    Air:{
        dens:0.001184,
        comp:[[7,0.755],[8,0.232],[18,0.013]]
    },
    He:{
        dens:0.000179,
        comp:[[2,1]]
    },
    Ar:{
        dens:0.001784,
        comp:[[18,1]]
    },
    Be:{
        dens:1.84,
        comp:[[4,1]]
    },
    C:{
        dens:2.25,
        comp:[[6,1]]
    },
    Diamond:{
        dens:3.52,
        comp:[[6,1]]
    },
    N2:{
        dens:0.00125,
        comp:[[7,1]]
    },
    Al:{
        dens:2.69,
        comp:[[13,1]]
    },
    Si:{
        dens:2.34,
        comp:[[14,1]]
    },
    Ti:{
        dens:4.506,
        comp:[[22,1]]
    },
    Cu:{
        dens:8.93,
        comp:[[29,1]]
    },
    Mo:{
        dens:10.28,
        comp:[[42,1]]
    },
    Rh:{
        dens:12.41,
        comp:[[45,1]]
    },
    Pt:{
        dens:21.45,
        comp:[[78,1]]
    },
    Au:{
        dens:19.32,
        comp:[[79,1]]
    },
    Pb:{
        dens:11.35,
        comp:[[82,1]]
    },
    Kapton:{
        dens:1.42,
        comp:[[1,0.026],[6,0.69],[7,0.073],[8,0.21]]
    }
}

// parameter scan configurations
const ScanConfigLabel = {
  scan2dtype:["Scan Type", [Scan2D1DLabel, Scan2DLinkLabel, Scan2D2DLabel], SelectionLabel],
  initial:["Initial Value", 1],
  final:["Final Value", 10],
  initial2:["Initial Value (1,2)",[1,1]],
  final2:["Final Value (1,2)", [10,10]],
  scanpoints:["Scan Points", 10, IntegerLabel, 2],
  scanpoints2:["Scan Points (1,2)", [10,10], ArrayIntegerLabel, 2],
  initiali:["Initial Number", 1, IntegerLabel, null],
  finali:["Final Number", 10, IntegerLabel, null],
  initiali2:["Initial Number (1,2)", [1,1], ArrayIntegerLabel, null],
  finali2:["Final Number (1,2)", [10,10], ArrayIntegerLabel, null],
  interval:["Interval", 1, IntegerLabel],
  interval2:["Interval (1,2)", [1,1], ArrayIntegerLabel],
  iniserno:["Initial S/N", 1, IntegerLabel, null],
  iniserno2:["Initial S/N (1,2)", [1,1], ArrayIntegerLabel, null],
  bundle:[BundleScanlabel, false]
};

const ScanConfigOrder = [
  "scan2dtype",
  "initial",
  "final",
  "initial2",
  "final2",
  "scanpoints",
  "scanpoints2",
  "initiali",
  "finali",
  "initiali2",
  "finali2",
  "interval",
  "interval2",
  "iniserno",
  "iniserno2",
  "bundle"
];

const UpdateScans = [
  SrcPrmsLabel.e1st[0],
  SrcPrmsLabel.lambda1[0]  
];

//----- labels and categories for python
// simplified labels
const Labels4Python = {
  acc: AccLabel,
  src: SrcLabel,
  config: ConfigLabel,
  outfile: OutFileLabel,
  bl: BLLabel,
  menuitems: MenuLabels,
  separator: IDSeparator,
  output: OutputLabel,
  dimension: DataDimLabel,
  titles: DataTitlesLabel,
  units: UnitsLabel,
  data: DataLabel,
  details: DetailsLabel,
  linear: LinearLabel,
  log: LogLabel,
  line: LineLabel,
  linesymbol: LineSymbolLabel,
  symbol: SymbolLabel,
  contour: ContourLabel,
  surface: SurfaceLabel,
  shade: SurfaceShadeLabel,
  scan2ds: Scan2D1DLabel,
  scan2dl: Scan2DLinkLabel,
  scan2dm: Scan2D2DLabel,
  partana: PPPartAnaLabel,
  partdata: CustomParticle,
  partslice: CustomSlice,
  foreach: ForEachLabel,
  bymax: ByMaxLabel,
  parascheme: MPIOptionsLabel.parascheme[0],
  parampi: ParaMPILabel
}
// identifiers
const MainPrmLabels = {
  [AccLabel]: AccPrmsLabel, 
  [SrcLabel]: SrcPrmsLabel, 
  [ConfigLabel]: ConfigPrmsLabel,
  [OutFileLabel]: OutputOptionsLabel,
  [PartConfLabel]: ParticleConfigLabel,
  [PartPlotConfLabel]: PDPLotConfigLabel,
  [PrePLabel]: PreProcessPrmLabel,
  [DataUnitLabel]: DataUnitOptionsLabel,
  [AccuracyLabel]: AccuracyOptionsLabel,
  [MPILabel]: MPIOptionsLabel,
  [PartConfLabel]: ParticleConfigLabel
}

//----- plotly.js configurations -----
const XYScaleOptions = [LinearLabel, LogLabel];
const PlotTypeOptions = [LineLabel, LineSymbolLabel, SymbolLabel];
const Plot2DOptions = [ContourLabel, SurfaceLabel, SurfaceShadeLabel];
const ColorMapOptions = [DefaultLabel, RainbowLabel, BlackBodyLabel, EarthLabel, GreysLabel];

const PlotOptionsLabel = {
  xauto:["X auto range", true],
  yauto:["Y auto range", true],
  xrange:["X range", [0, 1]],
  yrange:["Y range", [0, 1]],
  normalize:["Normalize", [ForEachLabel, ByMaxLabel], SelectionLabel],
  xscale:["X-axis Scale", XYScaleOptions, SelectionLabel],
  yscale:["Y-axis Scale", XYScaleOptions, SelectionLabel],
  type:["Plot Type", PlotTypeOptions, SelectionLabel],
  size:["Symbol Size", 3, IntegerLabel],
  width:["Line Width", 1.5, IncrementalLabel, 0.5, 0.5],
  type2d:["2D Plot Type", Plot2DOptions, SelectionLabel],
  shadecolor:["Color", "#cccccc", ColorLabel],
  colorscale:["Color Map", ColorMapOptions, SelectionLabel],
  showscale:["Show Scale", true],
  wireframe:["Wireframe", false]
};

const PlotOptionsOrder = [
  "xauto",
  "yauto", 
  "xrange",
  "yrange", 
  "normalize",
  "xscale", 
  "yscale", 
  "type",
  "size",
  "width",
  "type2d",
  "shadecolor",
  "colorscale",
  "showscale",
  "wireframe"
];

var PlotlyPrms = {};
PlotlyPrms.config = {
    displaylogo: false, 
    responsive: true,
    scrollZoom: true,
    editable: true,
    edits: {
        axisTitleText: false,
        titleText: false,
        colorbarTitleText: false
    },
    modeBarButtonsToAdd:[
        {
          name: "Edit",
          click: function(e) {
            let eventup = new CustomEvent("editplotly");
            e.dispatchEvent(eventup);    
          }
        }
      ],
  
    modeBarButtonsToRemove:["toggleSpikelines"]
};
PlotlyPrms.colorbar = {
    thickness: 10,
    thicknessmode: "pixels",
    len: 0.5,
    lenmode: "fraction",
    outlinewidth: 0,
    tickformat: ".1e",
    showexponent: "first",
    orientation: "v", // changed from h, plotly.js default seems to redefined
    titleside: "right"
};
PlotlyPrms.clscale = [
    [0, "rgb(0,0,255)"], 
    [0.5, "rgb(220,220,220)"], 
    [1, "rgb(255,0,0)"]
];
PlotlyPrms.margin1d = {l:70,r:20,t:20,b:40};
PlotlyPrms.margin2d = {l:5,r:5,t:5,b:5};

PlotlyPrms.camera = {
  //center: {x: -0.17, y:0.11, z:-0.06},
  eye: {x:-1.8, y:-1.8, z:1.8},
  up: {x:0.4, y:0.4, z:0.8}
};

var PlotlyColors = [
  [0, 0, 0], // black
  [255, 0, 0], // red
  [0, 0, 255], // blue
  [0, 255, 0], // green
  [0, 255, 255], // cyan
  [255, 255, 0], // yellow
  [255, 0, 255] // purple
]

var PlotlyMarkers = [
  "circle",
  "square",
  "circle-open",
  "square-open",
  "triangle-up",
  "diamond",
  "triangle-down",
  "triangle-up-open",
  "diamond-open",
  "triangle-down-open"
];

PlotlyPrms.config.modeBarButtonsToAdd[0].icon = Plotly.Icons.pencil;

//var PlotlyScatterType = "scatter";
// ver 2.32, scattergl OK
var PlotlyScatterType = "scattergl";
var PlotlyFont = {family: "Arial", size: 12};