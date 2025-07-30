"use strict";

// program information
const Version = "3.2.0";
const ConfigFileName = "simplex_config.json";
const AppName = "SIMPLEX";
const DefaultWindow = {width:880, height: 700, x:100, y: 100};

// frameworks
const PythonGUILabel = "python-gui";
const PythonScriptLabel = "python-script";
const BrowserLabel = "browser";
const ServerLabel = "server";
const TauriLabel = "tauri"

// physical constants
const CC = 2.9979246e+8;
const MC2MeV = 0.510999;
const ONE_ANGSTROM_eV = 12398.4247;
const COEF_K_VALUE = 93.3729;
const COEF_E1ST = 9.49634;
const DEGREE2RADIAN = Math.PI/180;
const QE = 1.60217733e-19;
const Sigma2FWHM = 2.354820045;
const MAXIMUM_EXPONENT = 100;
const ALFVEN_CURR = 1.7037e+4 /* Alfven current in A */
const PLANCK = 4.1356692e-15 /* Planck constant eV/sec^(-1): not divided by 2pi */
const COEF_ACC_FAR_BT = 586.679 // B(Tesla) to gamma*d(beta)/dz
const ERadius = 2.817938e-15 /* classical electron radius */

// type identifier and labels for PrmOptionList class 
const SeparatorLabel = "SEPARATOR";
const SimpleLabel = "LABEL";
const BoolLabel = "BOOLEAN";
const StringLabel = "STRING";
const IntegerLabel = "INTEGER";
const ArrayIntegerLabel = "INTEGERARRAY";
const NumberLabel = "NUMBER";
const ArrayLabel = "NUMBERARRAY";
const IncrementalLabel = "INCREMENTAL";
const ArrayIncrementalLabel = "INCRARRAY";
const SelectionLabel = "SELECTION";
const FileLabel = "FILE";
const FolderLabel = "FOLDER";
const PlotObjLabel = "PLOT";
const GridLabel = "GRID";
const ColorLabel = "COLOR";

// settings saved in a configuration file
const SubPlotsRowLabel = "Subplots/Row";
const PlotWindowsRowLabel = "Plot Windows/Row";

// labels for Grid class
const GridColLabel = "ColLabel";
const GridTypeLabel = "ColType";
const AdditionalRows = 2;

// solver related
const CalcStatusLabel = "Simulation Status: "
const ErrorLabel = "Error: "
const WarningLabel = "Warning: ";
const Fin1ScanLabel = "Scan Process: "
const ScanOutLabel = "Output File: ";
const CancellAllLabel = "Cancel All";
const CancelLabel = "Cancel";
const RemoveLabel = "Remove";
const ImportLabel = "Import";
const InitStatusLabel = "Initializing: "

// keys and variables of output file
const InputLabel = "Input";
const GainCurveLabel = "Gain Curve";
const RadCharactLabel = "Characteristics";
const TempProfileLabel = "Temporal Profile";
const SpecProfileLabel = "Spectral Profile";
const SpatProfileLabel = "Spatial Profile";
const AnglProfileLabel = "Angular Profile";
const KValueTrendLabel = "K Value Trend";
const CoordinateLabel = "Raw Data Export";
const DataLabel = "data";
const DataDimLabel = "dimension";
const DataTitlesLabel = "titles";
const UnitsLabel = "units";
const VariablesLabel = "variables";
const DetailsLabel = "details";
const RetInfLabel = "returns";
const Link2DLabel = "link2d";
const PlotScatterLabel = "scatter";
const StepCoordLabel = "Steps (m)";
const SliceCoordLabel = "Slices (m)";
const StepIndexLabel = "Step Index";
const XYCoordLabel = "Grid Intervals (m,rad)";
const XYPointsLabel = "Grid Points";
const BeamletsLabel = "Beamlets";
const ParticlesLabel = "Particles/Beamlet";
const AvgEnergyLabel = "Average Electron Energy (GeV)";
const SliceEmittanceLabel = "Normalized Slice Emittance (mm.mrad)";
const SliceEspreadLabel = "Slice Energy Spread";
const PeakCurrLabel = "Peak Current (A)";
const SimulatedChargeLabel = "Total Charge Simulated (C)";
const TotalStepsLabel = "Total Steps Simulated";
const CentralEnergyLabel = "Central Photon Energy (eV)";
const DataNameLabel = "Data File";

// categories
const EBLabel = "Electron Beam";
const SeedLabel = "Seed Light";
const SPXOutLabel = "SIMPLEX Output"
const UndLabel = "Undulator";
const LatticeLabel = "Lattice";
const AlignmentLabel = "Alignment";
const WakeLabel = "Wakefield";
const ChicaneLabel = "Chicane";
const DispersionLabel = "Dispersion";
const SimCondLabel = "Simulation Conditions";
const DataDumpLabel = "Data Dump Configurations";
const OutFileLabel = "Output File";
const FELLabel = "FEL Performance";
const POLabel = "Plot Options";
const ScanLabel = "Scan Parameter";
const PrePLabel = "Pre-Processing";
const DataUnitLabel = "Units for Data Import";
const PartConfLabel = "Particle Data Format";
const PartPlotConfLabel = "Particle Data Plot";
const MBunchEvalLabel = "Microbunch Evaluation";

// post-post processing labels
const PostPLabel = "Post-Processing";
const PostPResultLabel = "Processed";
const RawDataProcLabel = "Raw Data Processing";

// input panel labels
const InputPanels = [
  EBLabel, SeedLabel, SPXOutLabel, UndLabel, LatticeLabel, AlignmentLabel,  WakeLabel, 
  ChicaneLabel, DispersionLabel, SimCondLabel, DataDumpLabel, OutFileLabel, FELLabel
];

// setting panel labels
const SettingPanels = [
  PrePLabel, PartConfLabel, PartPlotConfLabel, MBunchEvalLabel, PostPLabel, DataUnitLabel
];

// prefix for SimulationProcess instance
const SimulationIDLabel = "Simulation";

// available keys for Settings
const SettingKeys = [
  "scanconfig", "sorting", "defpaths", "lastloaded", "lastid", 
  "animinterv", "window", "plotconfigs", 
  OutFileLabel, PlotWindowsRowLabel, SubPlotsRowLabel, ...SettingPanels
];

// scan options
const Scan2D1DLabel = "1D: Single";
const Scan2DLinkLabel = "1D: Link 1st/2nd";
const Scan2D2DLabel = "2D Mesh"

// parallel computing
const ParaMPILabel = "MPI";
const MultiThreadLabel = "Multithread";

// general options
const LinearLabel = "Linear";
const LogLabel = "Logarithmic";
const LineLabel = "Line";
const LineSymbolLabel = "Line & Symbol";
const SymbolLabel = "Symbol";
const SurfaceLabel = "Surface (Color Scale)";
const SurfaceShadeLabel = "Surface (Shading)";
const ContourLabel = "Contour";
const DefaultLabel = "Default";
const RainbowLabel = "Rainbow";
const BlackBodyLabel = "Blackbody";
const EarthLabel = "Earth";
const GreysLabel = "Greys";
const ByMaxLabel = "By Maximum";
const ForEachLabel = "For Each";
const NotAvaliable = "N.A.";

// preprocessing menus
// items for pre-processing
const PPCurrentLabel = "Current Profile";
const PPEtLabel = "E-t Distribution";
const PPSliceEmittLabel = "Slice Emittance";
const PPSliceELabel = "Slice Energy & Spread";
const PPSliceBetaLabel = "Slice &beta; Functions";
const PPSliceAlphaLabel = "Slice &alpha; Functions";
const PPSatPowerLabel = "Saturation Power";
const PPGainLengthLabel = "Gain Length";
const PPCustomWake = "Custom Wakefield";
const PPCustomMono = "Custom Monochromator";
const PPBetaOptQgrad = "Average";
const PPBetaOptInitial = "Matching";
const PPPartAnaLabel = "Analyze Particle Data";
const PPMicroBunchLabel = "Simplified Microbunch Evaluation";
const PPFDlabel = "Field Distribution";
const PP1stIntLabel = "1st Integral";
const PP2ndIntLabel = "2nd Integral";
const PPPhaseErrLabel = "Phase Error";
const PPKValue = "K Value Trend";
const PPDetune = "Detuning Trend";
const PPUdataLabel = "Arrange Undulator Data";
const PPWakeBunch = "Wakefield Temporal Profile";
const PPWakeEvar = "Energy Distribution";
const PPBetaLabel = "betatron Functions";
const PPOptBetaLabel = "Optimization";
const PPFocusStrength = "Focusing Strength";
const PPDispersion = "Dispersion";
const PPMonoSpectrum = "Mono. Spectrum";
const OthersLabel = "Others";

// items available with "Simplified Microbunch Evaluation"
const EtDistLabel = "Ref. Particles in (t,E)";
const CurrentProfLabel = "Current Profile";
const EtProfLabel = "E-t Profile";

// post-processor labels
const SpecsLabel = "Specifications";

// gain curve items
const PulseEnergyLabel = "Pulse Energy";
const RadPowerLabel = "Radiation Power";
const SpatEnergyDensLabel = "Spatial Energy Density";
const AngEnergyDensLabel = "Angular Energy Density";
const SpatPowerDensLabel = "Spatial Power Density";
const AngPowerDensLabel = "Angular Power Density";
const BunchFactorLabel = "Bunch Factor";
const ELossLabel = "Energy Loss";
const PLossLabel = "Power Loss";
const EspreadLabel = "Energy Spread";

// characteristics items
const PulselengthLabel = "RMS Pulse Length";
const BandwidthLabel = "RMS Bandwidth";
const DivergenceX = "RMS Divergence (x)";
const DivergenceY = "RMS Divergence (y)";
const BeamSizeX = "RMS Beam Size (x)";
const BeamSizeY = "RMS Beam Size (y)";
const CurvatureLabel = "Wavefront Curvature";
const ElapsedTimeLabel = "Elapsed Time (sec)";

// other configurations
const JSONIndent = 2;
const IDSeparator = "::";
const GainPerStep = 0.2;
const LOGOFFSET = 1.1;
const MinimumParticles = 1000;
const MaxItems2Plot4PP = 5;

// import data format
const CustomSlice = "Slice Parameters";
const CustomCurrent = "Current Profile";
const CustomEt = "E-t Profile";
const CustomParticle = "Particle Distribution";
const UndDataLabel = "Undulator Data";
const WakeDataLabel = "Wakefield Data";
const MonoDataLabel = "Monochromator Data";

// variables for data import
const XLabel = "x (m)";
const XpLabel = "x' (rad)";
const YLabel = "y (m)";
const YpLabel = "y' (rad)";
const EnergyLabel = "Energy (GeV)";
const EdevLabel = "&Delta;&gamma;/&gamma;";
const EspLabel = "Energy Spread";
const EdevspLabel = "Energy Deviation & Spread"
const SliceLabel = "s (m)";
const CurrentLabel = "I (A)";
const CurrentTitle = "Current Profile";
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
const SatPowerLabel = "Saturation Power (GW)";
const GainLengthLabel = "Gain Length (m)";
const CurrjLabel = "j (A/100%)";
const WakeSingleLabel = "Point-Charge Wake (V/m/C)";
const PhotonEnergyLabel = "Photon Energy (eV)";
const TransmittanceReal = "Transmission Real";
const TransmittanceImag = "Transmission Imaginary";

const ParticleTitles = [XLabel, XpLabel, YLabel, YpLabel, SliceLabel, EnergyLabel];
const SliceTitles = [SliceLabel, 
  CurrentLabel, EnergyLabel, EspLabel, EmittxLabel, EmittyLabel, 
  BetaxLabel, BetayLabel, AlphaxLabel, AlphayLabel, XavLabel, YavLabel, XpavLabel, YpavLabel];

  // definition of ascii-file formats
const AsciiFormats = {};
AsciiFormats[CustomSlice] = {dim: 1, items: SliceTitles.length-1, titles: SliceTitles, ordinate: CustomSlice};
AsciiFormats[CustomCurrent] = {dim: 1, items: 1, titles: [SliceLabel, CurrentLabel], ordinate: "Current (A)"};
AsciiFormats[CustomParticle] = {dim: 1, items: 5, titles: ParticleTitles, ordinate: ""};
AsciiFormats[CustomEt] = {dim: 2, items: 1, titles: [SliceLabel, EdevLabel, CurrjLabel], ordinate: ""};
AsciiFormats[UndDataLabel] = {dim: 1, items: 2, titles: ["z (m)", "B<sub>x</sub> (T)", "B<sub>y</sub> (T)"], ordinate: "Magnetic Field (T)"};
AsciiFormats[WakeDataLabel] = {dim: 1, items: 1, titles: [SliceLabel, WakeSingleLabel], ordinate: "Point-Charge Wavefield (V/m/C)"};
AsciiFormats[MonoDataLabel] = {dim: 1, items: 2, titles: [PhotonEnergyLabel, TransmittanceReal, TransmittanceImag], ordinate: "Transmittance"};

// titles for pre-processed plot
var AxisTitles = {};
AxisTitles[PPFDlabel] = "Magnetic Field (T)";
AxisTitles[PP1stIntLabel] = "Electron Angle (mrad)";
AxisTitles[PP2ndIntLabel] = "Electron Position (mm)";
AxisTitles[PPPhaseErrLabel] = "Phase Error (degree)";
AxisTitles[PPKValue] = "K Value";
AxisTitles[PPDetune] = "Detuning";
AxisTitles[PPWakeBunch] = "Wake Field (V/m)";
AxisTitles[PPWakeEvar] = "Normalized Intensity";
AxisTitles[PPBetaLabel] = "Betatron Function (m)";
AxisTitles[PPOptBetaLabel] = "Betatron Function (m)";
AxisTitles[PPFocusStrength] = "k<sub>x,y</sub> (m<sup>-2</sup>)";
AxisTitles[PPDispersion] = "Dispersion Function (mm)";
AxisTitles[PPMonoSpectrum] = "Complex Reflectance";
AxisTitles[EtDistLabel] = "&Delta;&gamma;/&gamma;";
AxisTitles[CurrentProfLabel] = "Current (A)";
AxisTitles[EtProfLabel] = "Partical Current (A/100%)";

// short variable names for Post-Processing
const ShortTitles = {}

// Menu Items
const GUILabels = {
  // tab titles
  Tab: {
    preproc: PrePLabel,
    postproc: PostPLabel
  },

  // menu titles
  Menu: {
    file: "File",
    run: "Run",
    help: "Help"
  },

  // file
  file: {
    new: "Create a New Parameter File",
    open: "Open a Parameter File",
    loadf: "Load Output File",
    outpostp: "Load Post-Processed Result",
    save: "Save",
    saveas: "Save As",
    exit: "Exit"
  },

  // run
  run: {
    process: "Create a New Process",
    export: "Export Simulation Settings",
    start: "Start Simulation",
    cancel: CancelLabel,
    python: "Python Script",
    scanout: ScanOutLabel,
    runpostp: "Run Data-Processing"
  },

  // help
  help: {
    reference: "Open Reference Manual",
    about: "About SIMPLEX",  
  },

  // category
  Category: {
    ebeam: EBLabel,
    seed: SeedLabel,
    spxout: SPXOutLabel,
    undulator: UndLabel,
    lattice: LatticeLabel,
    alignment: AlignmentLabel,
    wake: WakeLabel,
    chicane: ChicaneLabel,
    dispersion: DispersionLabel,
    condition: SimCondLabel,
    datadump: DataDumpLabel,
    outfile: OutFileLabel,
    felprm: FELLabel,
    dataprocess: PostPLabel,
    partconf: PartConfLabel,
    partplot: PartPlotConfLabel
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

  // gain-curve items
  gcitems: {
    pulseE: PulseEnergyLabel,
    radP: RadPowerLabel,
    sdE: SpatEnergyDensLabel,
    adE: AngEnergyDensLabel,
    sdP: SpatPowerDensLabel,
    adP: AngPowerDensLabel,
    bunchF: BunchFactorLabel,
    Eloss: ELossLabel,
    Ploss: PLossLabel,
    Espr: EspreadLabel
  },

  // characteristics items
  radchar: {
    puleL: PulselengthLabel,
    bandW: BandwidthLabel,
    divx: DivergenceX,
    divy: DivergenceY,
    sizex: BeamSizeX,
    sizey: BeamSizeY,
    curvature: CurvatureLabel
  },

  // data types
  datatype: {
    gcurve:GainCurveLabel,
    radchar:RadCharactLabel,
    timeprof:TempProfileLabel,
    specprof:SpecProfileLabel,
    spatprof:SpatProfileLabel,
    angprof:AnglProfileLabel,
    ktrend:KValueTrendLabel
  },

  // pre-processor buttons
  preproc: {
    import: ImportLabel,
    ascii: "Export as ASCII",
    duplicate: "Duplicate Plot",
    units: "Edit Units",
    optimize: "Optimize",
    seedrun: "Run",
    load: "Load",
    slice: "Export Slice Data",
    uimport: "Import",
    uunits: "Edit Units",
    urename: "Rename",
    uclear: "Clear",
    udelete: "Delete",
  }
}

var MenuLabels = {};
Object.keys(GUILabels).forEach(type => {
  Object.assign(MenuLabels, GUILabels[type])
});

const TabIDs = {
  [EBLabel]: "ebeam-seed-tab",
  [SeedLabel]: "ebeam-seed-tab",
  [SPXOutLabel]: "ebeam-seed-tab",
  [UndLabel]: "undulatorline-tab",
  [LatticeLabel]: "undulatorline-tab",
  [AlignmentLabel]: "options-tab",
  [WakeLabel]: "options-tab",
  [ChicaneLabel]: "options-tab",
  [DispersionLabel]: "options-tab",
  [SimCondLabel]: "simctrl-dump-tab",
  [DataDumpLabel]: "simctrl-dump-tab",
  [OutFileLabel]: "simctrl-dump-tab",
  [FELLabel]: "ebeam-seed-tab",
  [PartPlotConfLabel]: "preproc-tab" 
};

const FileMenus = 
[
  {
    label:MenuLabels.new
  },
  {
    label:MenuLabels.open
  },
  {
    type:"separator"
  },
  {
    label:MenuLabels.loadf
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
    type:"separator"
  },
  {
    label:MenuLabels.exit
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
  {[MenuLabels.run]: RunMenus},
  {[MenuLabels.help]: HelpMenus}
];

//---------- Parameter List ----------
// electron beam
const GaussianBunch = "Gaussian";
const BoxcarBunch = "Boxcar";
const SimplexOutput = "SIMPLEX Output";
const BunchProfiles = [
    GaussianBunch, BoxcarBunch, SimplexOutput,
    {Customize: [CustomSlice, CustomCurrent, 
      CustomEt, CustomParticle]}
  ];

const ProjectedPrm = "Projected";
const SlicedPrmOptimize = "Sliced (Optimized)";
const SlicedPrmCustom = "Sliced (Custom)";

const EBeamPrmsLabel = {
  bmprofile:["Bunch Profile", BunchProfiles, SelectionLabel],
  slicefile:[CustomSlice, PlotObjLabel],
  currfile:[CustomCurrent, PlotObjLabel],
  etfile:[CustomEt, PlotObjLabel],
  partfile:[CustomParticle, FileLabel],
  partspec:["Sliced Particle Spec.", PlotObjLabel],
  basespec:["Base Spec.", PlotObjLabel],
  eenergy:["Electron Energy (GeV)", 8],
  bunchleng:["RMS Bunch Length (m)", 5e-6],
  bunchlenr:["Bunch Length (m)", 1e-5],
  bunchcharge:["Bunch Charge (nC)", 0.15],
  emitt:["&epsilon;<sub>x,y</sub> (mm.mrad)", [0.4, 0.4]],
  espread:["RMS Energy Spread", 1e-4],
  echirp:["Energy Chirp (m<sup>-1</sup>)", 0],
  eta:["&eta;<sub>x,y</sub> (m)", [0,0]],
  pkcurr:["Peak Current (A)", 3588],
  ebmsize:["&sigma;<sub>0x,0y</sub> (mm)",[2e-5,2e-5]],
  ediv:["&sigma;<sub>0x',0y'</sub> (mrad)",[1e-6,1e-6]],
  r56:["R<sub>56</sub> (m)", 0],
  twissbunch:["Bunch Twiss Prms.", [ProjectedPrm, SlicedPrmOptimize, SlicedPrmCustom], SelectionLabel],
  twisspos:["Slice Position (m)", 0],
  bunchbeta:["&beta;<sub>x,y</sub> (m)", [20, 20]],
  bunchalpha:["&alpha;<sub>x,y</sub> (m)", [0, 0]]
};

const EBeamPrmsScans = [
  EBeamPrmsLabel.eenergy[0],
  EBeamPrmsLabel.bunchleng[0],
  EBeamPrmsLabel.bunchlenr[0],
  EBeamPrmsLabel.bunchcharge[0],
  EBeamPrmsLabel.emitt[0],
  EBeamPrmsLabel.espread[0],
  EBeamPrmsLabel.echirp[0],
  EBeamPrmsLabel.eta[0],
  EBeamPrmsLabel.r56[0],
  EBeamPrmsLabel.twisspos[0]
];

const EBeamPrmsOrder = [
  "bmprofile",
  "slicefile",
  "currfile",
  "etfile",
  "partfile",
  "partspec",
  "basespec",
  "eenergy",
  "bunchleng",
  "bunchlenr",
  "bunchcharge",
  "emitt",
  "espread",
  "echirp",
  "eta",
  "pkcurr",
  "ebmsize",
  "ediv",
  SeparatorLabel,
  "r56",
  SeparatorLabel,
  "twissbunch",
  "twisspos",
  "bunchbeta",
  "bunchalpha"
];

const EBBasePrmLabels = [
  EBeamPrmsLabel.eenergy[0],
  EBeamPrmsLabel.bunchcharge[0],
  EBeamPrmsLabel.bunchleng[0],
  EBeamPrmsLabel.pkcurr[0],
  EBeamPrmsLabel.espread[0],
  EBeamPrmsLabel.emitt[0],
  EBeamPrmsLabel.bunchbeta[0],
  EBeamPrmsLabel.bunchalpha[0]
];

const EBSpecPrmLabels = [
  EBeamPrmsLabel.eenergy[0],
  EBeamPrmsLabel.pkcurr[0],
  EBeamPrmsLabel.espread[0],
  EBeamPrmsLabel.emitt[0]
];

// analyze particle distribution 
const UnitMeter = "m";
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

const XYUnits = [UnitMeter, UnitMiliMeter];
const XYpUnits = [UnitRad, UnitMiliRad];
const SUnits  = [UnitSec, UnitpSec, UnitfSec, UnitMeter, UnitMiliMeter];
const EUnits = [UnitGeV, UnitMeV, UnitGamma];

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

// plot particle-distribution related
const PDPlotType = [CustomSlice, CustomParticle];
const XYAxisTitles = [XLabel, XpLabel, YLabel, YpLabel, SliceLabel, EnergyLabel];
const BPTitles = [CurrentTitle, EdevspLabel, EmittTitle, BetaTitleLabel, AlphaTitleLabel, 
    XYTitleLabel, XYpTitleLabel, PPGainLengthLabel, PPSatPowerLabel];

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

// seed light
const GaussianPulse = "Gaussian Beam";
const ChirpedPulse = "Chirp Pulse";
const PulseProfiles = [NotAvaliable, GaussianPulse, ChirpedPulse, SimplexOutput];

const SeedPrmsLabel = {
  seedprofile:["Seed Light", PulseProfiles, SelectionLabel],
  pkpower:["Peak Power (W)", 1e9],
  relwavelen:["&Delta;&lambda;/&lambda;<sub>1</sub>", 0],
  wavelen:["Wavelength (nm)", 1],
  pulseenergy:["Pulse Energy (J)", 1e-3],
  pulselen:["FWHM Pulse Length (fs)", 40],
  spotsize:["FWHM Spot Size (mm)", 0.05],
  raylen:["Rayleigh Length (m)", 10],
  waistpos:["Position of Waist (m)", 0],
  timing:["Relative Time (fs)", 0],
  CEP:["Carrier Envelope Phase (&deg;)", 0],
  gdd:["GDD (fs<sup>2</sup>)", 0],
  tod:["TOD (fs<sup>3</sup>)", 0],
  stplen:["Stretched Pulse Length (fs)", 40],
  chirprate:["Chirp Rate (&Delta;&omega;/&omega;)", 0.1],
  phase:["Phase Offset (&deg;)", 0]
};

const SeedPrmsOrder = [
  "seedprofile",
  "pkpower",
  "relwavelen",
  "wavelen",
  "pulseenergy",
  "pulselen",
  "spotsize",
  "raylen",
  "waistpos",
  "timing",
  "CEP",
  "gdd",
  "tod",
  "stplen",
  "chirprate",
  "phase"
];

const SeedPrmsScans = [
  SeedPrmsLabel.pkpower[0],
  SeedPrmsLabel.relwavelen[0],
  SeedPrmsLabel.pulseenergy[0],
  SeedPrmsLabel.pulselen[0],
  SeedPrmsLabel.spotsize[0],
  SeedPrmsLabel.waistpos[0],
  SeedPrmsLabel.timing[0],
  SeedPrmsLabel.CEP[0],
  SeedPrmsLabel.gdd[0],
  SeedPrmsLabel.phase[0]
];

// evaluate microbunching
const DoublePulseLabel = "Double Pulse";
const CascadingLabel = "Cascading";

const EvalMBunchLabel = {
  mbparticles:["Particles/&lambda;", 16, IntegerLabel, 8],
  mbaccinteg:["Accuracy of Integration", 1, IntegerLabel, 1],
  iscurrent:["Current Profile", false],
  isEt:["E-t Profile", false],
  mbtrange:["Temporal Range", [-5e-7, 5e-7]],
  tpoints:["Points/&lambda;", 16],
  erange:["Energy Range", [-0.001, 0.001]],
  epoints:["Energy Points", 21, IntegerLabel, 1, 5],
  mbr56:["R<sub>56</sub> (m)", 1e-6],
  isoptR56:["Optimize R<sub>56</sub>", false],
  nr56:["Normalized R<sub>56</sub>", 1],
  mbsegments:["Number of Undulators", 1, IntegerLabel, 1],
  wpulse:["Double Pulse", false],
  conf2nd:["Configurations of 2nd Pulse", SimpleLabel],
  relwavelen2:["&Delta;&lambda;/&lambda;", 0],
  CEP2:["CEP (&deg;)", 0],
  gdd2:["GDD (fs<sup>2</sup>)", 0],
  tod2:["TOD (fs<sup>2</sup>)", 0],
  timing2:["Time Delay (fs)", 0]
};

const EvalMBunchOrder = [
  "mbparticles",
  "mbaccinteg",
  "iscurrent",
  "isEt",
  "mbtrange",
  "tpoints",
  "erange",
  "epoints",
  "mbr56",
  "isoptR56",
  "nr56",
  "mbsegments",
  "wpulse",
  SeparatorLabel,
  "conf2nd",
  "relwavelen2",
  "CEP2",
  "gdd2",
  "tod2",
  "timing2"
];

// SIMPLEX output
const ImportSPXOutLabel = {
  spxfile:["Data Name", FileLabel],
  spxstep:["Step Index to Retrieve Data", 0, IntegerLabel, -5, 1, 0],
  spxstepzarr:["Exported Positions (m)", GridLabel],
  spxstepz:["z (m)", 100],
  bmletsout:["Total Beamlets", 0],
  paticlesout:["Particles/Beamlet", 0],
  matching:["Drift Length (m)", 1],
  spxenergy:["Photon Energy (eV)", 10]
};

const ImportSPXOutOrder = [
  "spxfile",
  "spxstep",
  "spxstepzarr",
  "spxstepz",
  "bmletsout",
  "paticlesout",
  "matching",
  "spxenergy"
];

const ImportSPXPrmsScans = [
  ImportSPXOutLabel.spxstep[0]
];

// Undulator
const LinearUndLabel = "Linear";
const HelicalUndLabel = "Helical";
const EllipticUndLabel = "Elliptical";
const MultiHarmUndLabel = "Multi-Harmonic"
const UndulatorTypes = [LinearUndLabel, HelicalUndLabel, EllipticUndLabel, MultiHarmUndLabel];
const TaperStair = "Stair-Like";
const TaperContinuous = "Continuous";
const TaperCustom = "Custom";
const TaperOptWhole = "Projection";
const TaperOptSlice = "Slice";
const TaperOptWake  = "Compensate Wake";
const TaperTypes = [NotAvaliable, TaperStair, TaperContinuous, TaperCustom];
const TaperOptTypes = [NotAvaliable, TaperOptWake, TaperOptWhole, TaperOptSlice]
const IdealLabel = "Ideal";
const SpecifyErrLabel = "Specify Error";
const ImportDataLabel = "Import Data";
const UModelTypes = [IdealLabel, SpecifyErrLabel, ImportDataLabel];
const MultiHarmContLabel = "Multi-Harmonic Contents";
const DataAllocLabel = "Data Allocation";
const TaperCustomLabel = "Custom Taper";

const UndPrmsLabel = {
  utype:["Undulator Type", UndulatorTypes, SelectionLabel],
  K:["K Value", 2.18],
  Kperp:["K<sub>&perp;</sub>", 2.18],
  multiharm:[MultiHarmContLabel, GridLabel],
  epukratio:["tan<sup>-1</sup>(K<sub>x</sub>/K<sub>y</sub>) (&deg;)", 30],
  lu:["&lambda;<sub>u</sub> (mm)", 18],
  length:["Length/Segment (m)", 5],
  segments:["Number of Segments", 18, IntegerLabel, 1, 1],
  interval:["Segment Interval", 6.15],
  peakb:["Peak Field (T)", 1.25],
  periods:["Periods/Segment", 273],
  slippage:["Slippage in Drift (2&pi;)", 27],
  exslippage:["Extra Slippage (&deg;)", 0],

  taper:["Tapering", TaperTypes, SelectionLabel],
  opttype:["Optimization", TaperOptTypes, SelectionLabel],
  slicepos:["Target Slice Position (m)", 0],
  initial:["Initial Segment", 10, IntegerLabel],
  incrseg:["Increment Segment Interval", 2, IntegerLabel],
  base:["Base Linear Taper (m<sup>-1</sup>)", 1e-3],
  incrtaper:["Taper Increment (m<sup>-1</sup>)", 1e-3],
  Kexit:["K Value@Exit", 2.024],
  detune:["Resonance Detuning@Exit", 0.08],
  tapercustom:[TaperCustomLabel, GridLabel],

  umodel:["Undulator Model", UModelTypes, SelectionLabel],
  umautoseed:["Random Number Auto Seeding", false],
  umrandseed:["Random Number Seed", 1, IntegerLabel],
  phaseerr:["&sigma;<sub>&phi;</sub> (&deg;)", 5],
  berr:["&sigma;<sub>B</sub>/B (%)", 0.5],
  xyerr:["&sigma;<sub>x,y</sub> (mm)", [1e-3,1e-3]],
  allsegment:["Apply to All Segments", false],
  tgtsegment:["Target Segment", 1, IntegerLabel, 1, 1, 10],
  udata:[DataAllocLabel, GridLabel]

};

const UndPrmsOrder = [
  "utype",
  "K",
  "Kperp",
  "multiharm",
  "epukratio",
  "lu",
  "length",
  "segments",
  "interval",
  "peakb",
  "periods",
  "slippage",
  "exslippage",
  SeparatorLabel,
  "taper",
  "opttype",
  "slicepos",
  "initial",
  "incrseg",
  "base",
  "incrtaper",
  "Kexit",
  "detune", 
  "tapercustom",
  SeparatorLabel,
  "umodel",
  "umautoseed",
  "umrandseed",
  "phaseerr",
  "berr",
  "xyerr",
  "allsegment",
  "tgtsegment",
  "udata"
];

const UndPrmsScans = [
  UndPrmsLabel.K[0],
  UndPrmsLabel.Kperp[0],
  UndPrmsLabel.epukratio[0],
  UndPrmsLabel.lu[0],
  UndPrmsLabel.length[0],
  UndPrmsLabel.segments[0],
  UndPrmsLabel.interval[0],

  UndPrmsLabel.slicepos[0],
  UndPrmsLabel.initial[0],
  UndPrmsLabel.incrseg[0],
  UndPrmsLabel.base[0],
  UndPrmsLabel.incrtaper[0],

  UndPrmsLabel.umrandseed[0],
  UndPrmsLabel.phaseerr[0],
  UndPrmsLabel.berr[0],
  UndPrmsLabel.xyerr[0],
  UndPrmsLabel.tgtsegment[0]
];

// Wakefield
const WakePrmsLabel = {
  wakeon:["Wakefield On", false],
  aperture:["Aperture (m)", 0.0035],
  resistive:["Resistive", false],
  resistivity:["Resistivity (&Omega;m)", 1.68e-8],
  relaxtime:["Relaxation Time (sec)", 8e-15],
  paralell:["Parallel Plate", true],
  roughness:["Surface Roughness", false],
  height:["RMS Height (m)", 2e-6],
  corrlen:["Correlation Length (m)", 4e-5],
  dielec:["Dielectric Layer", false],
  permit:["&epsilon;/&epsilon;<sub>0</sub>", 2],
  thickness:["Thickness (m)", 2e-8],
  spcharge:["Space Charge", false],
  wakecustom:["Additional Custom Wake", false],
  wakecustomdata:[WakeDataLabel, PlotObjLabel]
};

const WakePrmsOrder = [
  "wakeon",
  "aperture",
  SeparatorLabel,
  "resistive",
  "resistivity",
  "relaxtime",
  "paralell",
  SeparatorLabel,
  "roughness",
  "height",
  "corrlen",
  SeparatorLabel,
  "dielec",
  "permit",
  "thickness",
  SeparatorLabel,
  "spcharge",
  "wakecustom",
  "wakecustomdata"
];

const WakePrmsScans = [
  WakePrmsLabel.aperture[0],
  WakePrmsLabel.resistivity[0],
  WakePrmsLabel.relaxtime[0],
  WakePrmsLabel.height[0],
  WakePrmsLabel.corrlen[0],
  WakePrmsLabel.permit[0],
  WakePrmsLabel.thickness[0]
];

// Lattice
const FUDULabel = "FUDU (QF-U-QD-U)";
const DUFULabel = "DUFU (QD-U-QF-U)";
const FUFULabel = "FUFU (QF-U-QF-U)";
const DoubletLabel= "Doublet (QF-QD-U)";
const TripletLabel= "Triplet (QF-QD-QF-U)";
const CombinedLabel= "Undulator Combined";
const LatticeTypes = [FUDULabel, DUFULabel, FUFULabel, DoubletLabel, TripletLabel, CombinedLabel];

const LatticePrmsLabel = {
  ltype:["Lattice Type", LatticeTypes, SelectionLabel],
  qfg:["QF Gradient (T/m)", 18.99],
  qdg:["QD Gradient (T/m)", -17.44],
  qfl:["QF Length (m)", 0.1],
  qdl:["QD Length (m)", 0.1],
  dist:["QF-QD Distance (m)", 0.02],
  lperiods:["# Periods/Segment", 18, IntegerLabel],
  betaxy0:["&beta;<sub>x0,y0</sub> (m)", [29.5483, 20.8583]],
  alphaxy0:["&alpha;<sub>x0,y0</sub> (m)", [1.05297, -0.757107]],
  optbeta:["Optimum &beta; (m)", 10],
};

const LatticePrmsOrder = [
  "ltype",
  "qfg",
  "qdg",
  "qfl",
  "qdl",
  "dist",
  "lperiods",
  SeparatorLabel,
  "betaxy0",
  "alphaxy0",
  "optbeta"
];

const LatticePrmsScans = [
  LatticePrmsLabel.qfg[0],
  LatticePrmsLabel.qdg[0],
  LatticePrmsLabel.qfl[0],
  LatticePrmsLabel.qdl[0],
  LatticePrmsLabel.dist[0],
  LatticePrmsLabel.lperiods[0],
  LatticePrmsLabel.betaxy0[0],
  LatticePrmsLabel.alphaxy0[0]
];

// Chicane
const XtalTransLabel = "Transmission";
const XtalReflecLabel = "Reflection";
const CustomLabel = "Customize";
const MonochroTypes = [NotAvaliable, XtalTransLabel, XtalReflecLabel, CustomLabel];
const C400Label = "Diamond (400)";
const C220Label = "Diamond (220)";
const Si111Label = "Silicon (111)";
const XtalTypes = [C400Label, C220Label, Si111Label, CustomLabel];

// Crystal configurations
const BuiltinXtals = {
	[C400Label]: [12.72, 0.089175, 0.045385],
	[C220Label]: [15.68, 0.1261, 0.045385],
	[Si111Label]: [42.484, 0.31357, 0.16019]
};

const ChicanePrmsLabel = {
  chicaneon:["Chicane On", false],
  dipoleb:["Dipole Field (T)", 0.4],
  dipolel:["Dipole Length", 0.2],
  dipoled:["Dipole Distance", 0.5],
  offset:["Beam Offset (mm)", 1.5],
  delay:["Electron Delay (fs)", 10],
  chpos:["Chicane Position", 10, IntegerLabel, 1],
  rearrange:["Rearrange After Chicane", false] ,
  monotype:["Monochromator Type", MonochroTypes, SelectionLabel],
  monodata:[MonoDataLabel, PlotObjLabel],
  xtaltype:["Crystal Type", XtalTypes, SelectionLabel],
  monoenergy:["&hbar;&omega; (eV)", 10000],
  bragg:["Bragg Angle (&deg;)", 11.4024],
  formfactor:["|F<sub>g</sub>|", BuiltinXtals[C400Label][0]],
  latticespace:["Lattice Spacing (nm)", BuiltinXtals[C400Label][1]],
  unitvol:["Unit Cell Volume (nm<sup>3</sup>)", BuiltinXtals[C400Label][2]],
  bandwidth:["Bandwidth", 4.67811e-5],
  xtalthickness:["Crystal Thickness (mm)", 0.1],
  reltiming:["Relative Timing (fs)", 0]
};

const ChicanePrmsOrder = [
  "chicaneon",
  "dipoleb",
  "dipolel",
  "dipoled",
  "offset",
  "delay",
  "chpos",
  "rearrange",
  SeparatorLabel,
  "monotype",
  "monodata",
  "xtaltype",
  "monoenergy",
  "bragg",
  "formfactor",
  "latticespace",
  "unitvol",
  "bandwidth",
  "xtalthickness",
  "reltiming"
];

const ChicanePrmsScans = [
  ChicanePrmsLabel.dipoleb[0],
  ChicanePrmsLabel.dipolel[0],
  ChicanePrmsLabel.dipoled[0],
  ChicanePrmsLabel.delay[0],
  ChicanePrmsLabel.chpos[0],
  ChicanePrmsLabel.monoenergy[0],
  ChicanePrmsLabel.xtalthickness[0],
  ChicanePrmsLabel.reltiming[0],
];

// Alignment Error
const TargetOffsetLabel = "Specify Offset";
const TargetErrorLabel = "Specify Tolerance";
const AlignUTypes = [IdealLabel, TargetErrorLabel, TargetOffsetLabel];
const AlignBPMTypes = [IdealLabel, TargetErrorLabel];
const OffsetEachLabel = "Offset for Each Segment";

const AlignErrorUPrmsLabel = {
  ualign:["Undulator Alignment", AlignUTypes, SelectionLabel], 
  Ktol:["&Delta;K Tolerance", 0],
  sliptol:["Slippage Tolerance (&deg;)", 0],
  sigsegment:[OffsetEachLabel, GridLabel],
  BPMalign:["BPM Alignment", AlignBPMTypes, SelectionLabel],
  xytol:["x,y Tolerance (mm)", [0.05, 0.05]],
  alautoseed:["Random Number Auto Seeding", false],
  alrandseed:["Random Number Seed", 1, IntegerLabel]
};

const AlignErrorPrmsOrder = [
  "ualign",
  "Ktol",
  "sliptol",
  "sigsegment",
  "BPMalign",
  "xytol",
  SeparatorLabel,
  "alautoseed",
  "alrandseed"
];

const AlignErrorUPrmsScans = [
  AlignErrorUPrmsLabel.Ktol[0],
  AlignErrorUPrmsLabel.sliptol[0],
  AlignErrorUPrmsLabel.xytol[0],
  AlignErrorUPrmsLabel.alrandseed[0]
];

// Dispersion & Injection
const DispersionPrmsLabel = {
  einjec:["e<sup>-</sup> Injection Error", false],
  exy:["&Delta;x,y (mm)", [0, 0]],
  exyp:["&Delta;x',y' (mrad)", [0, 0]],
  kick:["Single Kick", false],
  kickpos:["Kick Position (m)", 0],
  kickangle:["Kick Angle x,y (mrad)", [0, 0]],
  sinjec:["Seed Injection Error", false],
  sxy:["Seed &Delta;x,y (mm)", [0, 0]],
  sxyp:["Seed &Delta;x',y' (mrad)", [0, 0]]
};

const DispersionPrmsOrder = [
  "einjec",
  "exy",
  "exyp",
  "kick",
  "kickpos",
  "kickangle",
  "sinjec",
  "sxy",
  "sxyp"
];

const DispersionPrmsScans = [
  DispersionPrmsLabel.exy[0],
  DispersionPrmsLabel.exyp[0],
  DispersionPrmsLabel.kick[0],
  DispersionPrmsLabel.kickpos[0],
  DispersionPrmsLabel.kickangle[0],
  DispersionPrmsLabel.sxy[0],
  DispersionPrmsLabel.sxyp[0]
];

// Simulation Controls
const TimeDepLabel = "Time Dependent";
const SSLabel = "Steady State";
const CyclicLabel = "Cyclic";
const SimulationModes = [TimeDepLabel, SSLabel, CyclicLabel];
const SmoothingGauss = "Gaussian Mode";
const KillQuiteLoad = "Disable Quiet Loading";
const KillShotNoize = "Kill Shotnoize"
const RealElectronNumber = "Real Electron Number";
const SimulationOptions = [NotAvaliable, SmoothingGauss, KillQuiteLoad, KillShotNoize, RealElectronNumber];

const SimCtrlsPrmsLabel = {
  simmode:["Simulation Mode", SimulationModes, SelectionLabel],
  simoption:["Simulation Option", SimulationOptions, SelectionLabel],
  skipwave:["Skip Wavefront Transfer Process", false],
  autostep:["Auto Integration Step", true],
  autoseed:["Random Number Auto Seeding", false],
  randseed:["Random Number Seed", 1, IntegerLabel],
  step:["Integration Step", 5, IntegerLabel],
  stepsseg:["Steps/Segment", 20],
  driftsteps:["Steps in Drift Section", 2],
  beamlets:["Total Beamlets", 1e7],
  slicebmlets:["Max. Beamlets/Slice", 2000],
  slicebmletsss:["Beamlets/Slice", 2000],
  electrons:["Total Electrons", 1e7],
  sliceels:["Max. Electrons/Slice", 2000],
  sliceelsss:["Electrons/Slice", 2000],
  maxharmonic:["Max. Harmonic", 1, IntegerLabel],
  particles:["Particles/Beamlet", 4, IntegerLabel, 4],
  spatwin:["Spatial Window/&sigma;", 4, IntegerLabel, 2],
  gpointsl:["Grid Points Level", 1, IntegerLabel, 0],
  gpoints:["Grid Points", 1],
  simrange:["Temporal Window (m)", [-6e-6,6e-6]],
  simpos:["Bunch Position (m)", 0],
  slices:["Total Slices", 4000],
  parascheme:["Parallel Computing", [NotAvaliable, MultiThreadLabel, ParaMPILabel], SelectionLabel],
  mpiprocs:["Number of Processes", 4, IntegerLabel],
  threads:["Number of Threads", 4, IntegerLabel]

};

const SimCtrlsPrmsOrder = [
  "simmode",
  "simoption",
  "skipwave",
  "autostep",
  "autoseed",
  "randseed",
  SeparatorLabel,
  "step",
  "stepsseg",
  "driftsteps",
  SeparatorLabel,
  "beamlets",
  "slicebmlets",
  "slicebmletsss",
  "electrons",
  "sliceels",
  "sliceelsss",
  "maxharmonic",
  "particles",
  SeparatorLabel,
  "spatwin",
  "gpointsl",
  "gpoints",
  SeparatorLabel,
  "simrange",
  "simpos",
  "slices",
  SeparatorLabel,
  "parascheme",
  "mpiprocs",
  "threads"
];

const SimCtrlsPrmScans = [
  SimCtrlsPrmsLabel.randseed[0],
  SimCtrlsPrmsLabel.step[0],
  SimCtrlsPrmsLabel.beamlets[0],
  SimCtrlsPrmsLabel.gpointsl[0]
];

// Output Data
const DumpSegExitLabel = "All Segments";
const DumpSpecifyLabel = "Specific Segments";
const DumpUndExitLabel = "Final Step";
const RegularIntSteps = "Regular Interval";
const ExpStepTypes = [DumpSegExitLabel, DumpSpecifyLabel, DumpUndExitLabel, RegularIntSteps];
const WholeSliceLabel = "All Slices";
const SpecificSliceLabel = "Specific Slices";
const ExpSliceTypes = [WholeSliceLabel, SpecificSliceLabel];

const DataOutPrmsLabel = {
  procdata:["Radiation Profile Data", SimpleLabel],
  temporal:[TempProfileLabel, false],
  spectral:[SpecProfileLabel, false],
  spatial:[SpatProfileLabel, false],
  angular:[AnglProfileLabel, false],
  profstep:["Output Interval", 1, IntegerLabel],
  rawdata:["Raw Data", SimpleLabel],
  particle:["Particle Data", false],
  radiation:["Radiation Data", false],
  expstep:["Output Steps", ExpStepTypes, SelectionLabel],
  iniseg:["Initial Segment", 1, IntegerLabel],
  segint:["Segment Step", 1, IntegerLabel],
  stepinterv:["Step Interval", 1, IntegerLabel],
  pfilesize:["Particle Data Size (MB)", 2000],
  rfilesize:["Radiation Data Size (MB)", 2000]
};

const DataOutPrmsOrder = [
  "procdata",
  "temporal",
  "spectral",
  "spatial",
  "angular",
  "profstep",
  SeparatorLabel,
  "rawdata",
  "particle",
  "radiation",
  "expstep",
  "iniseg",
  "segint",
  "stepinterv",
  "pfilesize",
  "rfilesize"
];

// FEL parameters
const AvgBetaOpt = "Optimum";
const AvgBetaCurr = "Average";
const AvgBetaCustom = "Input Value";

const FELPrmsLabel = {
  avgbetasel: ["&beta; Representing Value ", [AvgBetaOpt, AvgBetaCurr, AvgBetaCustom], SelectionLabel],
  avgbetavalue: ["&lt;&beta;&gt; (m)", null],
  inputbeta: ["&beta; (m)", 15],
  optbeta: ["Optimum &lt;&beta;&gt; (m)", 15],
  shotnoize:["Shotnoise Power (W)", 1000],
  rho:["&rho;", 1e-4],
  Lg:["L<sub>g1D,3D</sub> (m)", [2,3]],
  psat:["P<sub>sat</sub> (GW)", 10],
  Lsat:["L<sub>sat</sub> (m)", 50],
  pulseE:["Pulse Energy (J)", 5e-4],
  e1st:["&hbar;&omega;<sub>1st</sub> (eV)", 12000],
  l1st:["&lambda;<sub>1st</sub> (nm)", 0.1],
  bandwidth:["FWHM Bandwidth", 1e-3],
  Sigxy:["&Sigma;<sub>x,y</sub> (mm)", [0.02, 0.02]],
  Sigxyp:["&Sigma;<sub>x',y'</sub> (mrad)", [4e-4, 4e-4]],
  pkflux:["Peak Flux", 8e24],
  pkbrill:["Peak Brilliance", 3e33]
};

const FELPrmsOrder = [
  "avgbetasel",
  "avgbetavalue",
  "inputbeta",
  "optbeta",
  "shotnoize",
  "rho",
  "Lg",
  "psat",
  "Lsat",
  "pulseE",
  SeparatorLabel,
  "e1st",
  "l1st",
  "bandwidth",
  "Sigxy",
  "Sigxyp",
  "pkflux",
  "pkbrill"
];

const FELPrmsScans = [
  FELPrmsLabel.e1st[0],
  FELPrmsLabel.l1st[0]
];


// Output File
const OutputOptionsLabel = {
  folder:["Folder", FolderLabel],
  prefix:["Prefix", "untitled"],
  comment:["Comment", ""],
  serial:["Serial Number", -1, IntegerLabel]
};

const OutputOptionsOrder = [
  "folder", 
  "prefix",
  "comment",
  "serial"
];

// Units for Data Import
const DataUnitsLabel = {
  bpos:["Bunch Position", [UnitMeter, UnitMiliMeter, UnitSec, UnitpSec, UnitfSec], SelectionLabel],
  energy:["Electron Energy", [UnitGeV, UnitMeV, UnitGamma], SelectionLabel],
  zpos:["Longitudinal Position (z)", [UnitMeter, UnitMiliMeter], SelectionLabel],
  bxy:["Magnetic Field (B<sub>x,y</sub>)", [UnitTesla, UnitGauss], SelectionLabel],
};

const DataUnitsOrder = [
  "bpos",
  "energy",
  "zpos",
  "bxy"
];

const PreProcessPrmLabel = {
  targetuseg:["Target Segment", 1, IntegerLabel, 1, 1, 10],
  plotpoints:["Data Points", 100, IntegerLabel],
  betamethod:["Target Item", [PPBetaOptQgrad, PPBetaOptInitial], SelectionLabel],
  avbetaxy:["&lt;&beta;<sub>x,y</sub>&gt;", [null,null]],
  tolbeta:["Tolerance", 0.01],
  cqfg:["QF Gradient (T/m)", 18.99],
  cqdg:["QD Gradient (T/m)", -17.44],
  cbetaxy0:["&beta;<sub>x0,y0</sub> (m)", [29.5483, 20.8583]],
  calphaxy0:["&alpha;<sub>x0,y0</sub> (m)", [1.05297, -0.757107]],
};

const PreProcessPrmOrder = [
  "targetuseg",
  "plotpoints",
  "betamethod",
  "avbetaxy",
  "tolbeta",
  "cqfg",
  "cqdg",
  "cbetaxy0",
  "calphaxy0"
];

const PreProcRespObjs = {
  [PreProcessPrmLabel.cbetaxy0[0]]: [LatticeLabel, LatticePrmsLabel.betaxy0[0]],
  [PreProcessPrmLabel.calphaxy0[0]]: [LatticeLabel, LatticePrmsLabel.alphaxy0[0]],
  [PreProcessPrmLabel.cqdg[0]]: [LatticeLabel, LatticePrmsLabel.qdg[0]],
  [PreProcessPrmLabel.cqfg[0]]: [LatticeLabel, LatticePrmsLabel.qfg[0]]
};

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
  "iniserno2"
];

const UpdateScans = [
  SeedPrmsLabel.pulseenergy[0],
  ChicanePrmsLabel.delay[0],
  FELPrmsLabel.e1st[0],
  FELPrmsLabel.l1st[0]  
];

// post-processing parameters
const PostPPowerLabel = "Radiation Power";
const PostPCampLabel = "Complex Amplitude";
const PostPFluxLabel = "Photon Flux";
const PostPWignerLabel = "Wigner Function";
const PostPBunchFLabel = "Bunch Factor";
const PostPEnergyLabel = "Energy Distribution";
const PostPPartDistLabel = "Particle Motion"
const PostPFarLabel = "Far Field";
const PostPNearLabel = "Near Field";
const PostPtXLabel = "(s, x)";
const PostPtYLabel = "(s, y)";
const PostPtetaLabel = "(s, &Delta;&gamma;/&gamma;)";
const PostPIntegFullLabel = "Whole";
const PostPIntegPartialLabel = "Set Window"

const PostPTimeDomainLabel = "Temporal";
const PostPSpatDomainLabel = "Spatial";
const PostPRealLabel = "Real Part";
const PostPImagLabel = "Imaginary Part";
const PostPExLabel = "x";
const PostPEyLabel = "y";
const PostPBothLabel = "Both";
const PostPXAxisLabel = "x";
const PostPYAxisLabel = "y";

const PostProcessPrmLabel = {
  item:["Target ", [PostPPowerLabel, PostPFluxLabel], SelectionLabel],
  domain:["Domain", [PostPSpatDomainLabel, PostPTimeDomainLabel], SelectionLabel],
  realimag:["Real/Imaginary Part", [PostPRealLabel, PostPImagLabel, PostPBothLabel], SelectionLabel],
  Exy:["E<sub>x,y</sub>", [PostPExLabel, PostPEyLabel, PostPBothLabel], SelectionLabel],
  axis:["Axis", [PostPXAxisLabel, PostPYAxisLabel], SelectionLabel],
  slabel:["Polarized Component", SimpleLabel],
  s1:["S<sub>1</sub> (Horizontal)", false],
  s2:["S<sub>2</sub> (45-deg.)", false],
  s3:["S<sub>3</sub> (Circular)", false],
  harmonic:["Harmonic Number", 1, IntegerLabel],
  zone:["Zone", [PostPNearLabel, PostPFarLabel], SelectionLabel],
  coord:["Coordinate System", [PostPtetaLabel, PostPtXLabel, PostPtYLabel], SelectionLabel],

  range:["Range of Interest", SimpleLabel],
  zrange:["Step", [PostPIntegFullLabel, PostPIntegPartialLabel], SelectionLabel],
  timerange:["Slice", [PostPIntegFullLabel, PostPIntegPartialLabel], SelectionLabel],
  energyrange:["Photon Energy", [PostPIntegFullLabel, PostPIntegPartialLabel], SelectionLabel],
  spatrange:["Space", [PostPIntegFullLabel, PostPIntegPartialLabel], SelectionLabel],
  anglrange:["Angle", [PostPIntegFullLabel, PostPIntegPartialLabel], SelectionLabel],

  window:["Window Index/Values", SimpleLabel],
  zwindow:["Step (z)", [1, 10], ArrayIntegerLabel],
  timewindow:["Slice (s)", [-100, 100], ArrayIntegerLabel],
  energywindow:["Energy (&hbar;&omega;)", [-10, 10], ArrayIntegerLabel],
  spatwindow:["Spatial (x,y)", [16, 16], ArrayIntegerLabel],
  anglindow:["Angular (x',y')", [16, 16], ArrayIntegerLabel],
  zvalue:["z (m)", [0, 10]],
  timevalue:["s (m)", [0, 10]],
  energyvalue:["&hbar;&omega; (eV)", [0, 10]],
  spatvalue:["&Delta;x,y (mm)", [0, 10]],
  anglvalue:["&Delta;x',y' (mrad)", [0, 10]],

  alongs:["Integration (s)", false],
  overxy:["Integration (x,y)", true],
  overxyf:["Integration (x',y')", true],
  smoothing:["Smoothing: (s,&hbar;&omega;)", [0, 0], ArrayIntegerLabel],
  smvalues:["&sigma;<sub>s</sub> (m), &sigma;<sub>&hbar;&omega;</sub> (eV)", [0, 0]],
  r56pp:["R<sub>56</sub> (m)", 0],

  serialpp:["Data Serial Number", -1, IntegerLabel, -1],
  bmletspp:[BeamletsLabel, 1],
  particlespp:[ParticlesLabel, 1]
};

const PostProcessPrmOrder = [
  "item",
  "domain",
  "realimag",
  "Exy",
  "axis",
  "slabel",
  "s1",
  "s2",
  "s3",
  "harmonic",
  "zone",
  "coord",
  SeparatorLabel,
  "range",
  "zrange",
  "timerange",
  "energyrange",
  "spatrange",
  "anglrange",
  SeparatorLabel,
  "window",
  "zwindow",
  "timewindow",
  "energywindow",
  "spatwindow",
  "anglindow",
  "zvalue",
  "timevalue",
  "energyvalue",
  "spatvalue",
  "anglvalue",
  SeparatorLabel,
  "alongs",
  "overxy",
  "overxyf",
  "smoothing",
  "smvalues",
  "r56pp",
  SeparatorLabel,
  "serialpp",
  "bmletspp",
  "particlespp"
];

//----- labels and categories for python
// simplified labels
const Labels4Python = {
  menuitems: MenuLabels,
  outfile: OutFileLabel,
  separator: IDSeparator,
  gaincurve: GainCurveLabel,
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
  mblabel: PPMicroBunchLabel,
  partana: PPPartAnaLabel,
  partdata: CustomParticle,
  partslice: CustomSlice,
  foreach: ForEachLabel,
  bymax: ByMaxLabel
}
Object.keys(GUILabels.Category).forEach((key)=>{
  Labels4Python[key] = GUILabels.Category[key];
})

// identifiers
const MainPrmLabels = {
  [EBLabel]: EBeamPrmsLabel,
  [SeedLabel]: SeedPrmsLabel,
  [SPXOutLabel]: ImportSPXOutLabel,
  [UndLabel]: UndPrmsLabel,
  [LatticeLabel]: LatticePrmsLabel,
  [AlignmentLabel]: AlignErrorUPrmsLabel,
  [WakeLabel]: WakePrmsLabel,
  [ChicaneLabel]: ChicanePrmsLabel,
  [DispersionLabel]: DispersionPrmsLabel,
  [SimCondLabel]: SimCtrlsPrmsLabel,
  [DataDumpLabel]: DataOutPrmsLabel,
  [OutFileLabel]: OutputOptionsLabel,
  [FELLabel]: FELPrmsLabel,

  [PrePLabel]: PreProcessPrmLabel,
  [PartConfLabel]: ParticleConfigLabel,
  [PartPlotConfLabel]: PDPLotConfigLabel,
  [MBunchEvalLabel]: EvalMBunchLabel,
  [PostPLabel]: PostProcessPrmLabel,
  [DataUnitLabel]: DataUnitsLabel
};

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
  normalize:["Scale", [ForEachLabel, ByMaxLabel], SelectionLabel],
  xscale:["X-axis Scale", XYScaleOptions, SelectionLabel],
  yscale:["Y-axis Scale", XYScaleOptions, SelectionLabel],
  type:["Plot Type", PlotTypeOptions, SelectionLabel],
  size:["Symbol Size", 3, IntegerLabel],
  width:["Line Width", 1.5, IncrementalLabel, 0.5, 0.5],
  type2d:["2D Plot Type", Plot2DOptions, SelectionLabel],
  shadecolor:["Color", "#cccccc", ColorLabel],
  colorscale:["Color Map", ColorMapOptions, SelectionLabel],
  showscale:["Show Scale", true],
  wireframe:["Wireframe", false],
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
  "wireframe",
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

var PlotlyScatterType = "scatter";
// ver 2.32, scattergl OK
//var PlotlyScatterType = "scattergl";
var PlotlyFont = {family: "Arial", size: 12};