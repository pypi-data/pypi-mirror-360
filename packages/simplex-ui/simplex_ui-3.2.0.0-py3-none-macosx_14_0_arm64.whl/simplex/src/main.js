"use strict";

// globals
var Framework;
var RunOS;
var GUIConf = {currnewwin: null, procid: -1, disabled: [], mainid: ""};
var PlotObjects = {windows: new Queue(), objects: new Queue()};
var PyQue = new Queue();
var ScanTarget = {};
var Settings = {plotconfigs:{}, defpaths:{}, scanconfig:{}};
var Observer = {};
var TWindow = {}; // tauri windows object
var BufferObject = null;

// generate simulation objects and create processes
function GetSimulationObject(ppitem = null)
{
    let obj = {};
    let exports = Array.from(GUIConf.exports);
    if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] != CustomParticle){
        let index = exports.indexOf(PartConfLabel);
        exports.splice(index, 1);
    }
    if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] != SimplexOutput && 
        GUIConf.input[SeedLabel][SeedPrmsLabel.seedprofile[0]] != SimplexOutput){
        let index = exports.indexOf(SPXOutLabel);
        exports.splice(index, 1);
    }
    if(ppitem != null){
        if(ppitem == PPMicroBunchLabel){
            exports.push(MBunchEvalLabel);
        }
        else{
            exports.push(PrePLabel);
        }
    }
    for(let j = 0; j < exports.length; j++){
        obj[exports[j]] = GUIConf.GUIpanels[exports[j]].ExportCurrent();
    }
    if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == SimplexOutput){
        for(let j = 0; j < EBSpecPrmLabels.length; j++){
            if(Array.isArray(GUIConf.input[EBLabel][EBSpecPrmLabels[j]])){
                obj[EBLabel][EBSpecPrmLabels[j]] = Array.from(GUIConf.input[EBLabel][EBSpecPrmLabels[j]]);
            }
            else{
                obj[EBLabel][EBSpecPrmLabels[j]] = GUIConf.input[EBLabel][EBSpecPrmLabels[j]];
            }
        }
    }

    if(GUIConf.input[UndLabel][UndPrmsLabel.umodel[0]] == ImportDataLabel){
        let inuse = [];
        for(let n = 0; n < GUIConf.input[UndLabel][UndPrmsLabel.udata[0]].length; n++){
            inuse.push(GUIConf.input[UndLabel][UndPrmsLabel.udata[0]][n][1]);
        }
        let udata = CopyJSON(GUIConf.input[UndDataLabel]);
        if(udata.hasOwnProperty("names") && udata.hasOwnProperty("data")){
            for(let n = udata.names.length-1; n >= 0; n--){
                if(inuse.indexOf(udata.names[n]) < 0){
                    udata.names.splice(n, 1);
                    udata.data.splice(n, 1);
                }                    
            }
            if(udata.names.length > 0){
                obj[UndDataLabel] = udata;
            }
        }
    }
    return obj;
}

// maing GUI
function MainGUI()
{
    let menubar = document.getElementById("menubar");
    Menubar.forEach(menu => {
        let rootname = Object.keys(menu)[0];
        let menudiv = document.createElement("div");
        menudiv.id = rootname;
        menudiv.className = "dropdown";
        menubar.appendChild(menudiv);

        let menutitle = document.createElement("div");
        menutitle.setAttribute("data-bs-toggle", "dropdown");
        menutitle.className = "menu";
        menutitle.innerHTML = rootname;
        menudiv.appendChild(menutitle);

        let menucont = document.createElement("ul");
        menucont.className = "dropdown-menu";
        menucont.id = rootname+"-item";

        menudiv.appendChild(menucont);

        let menulist = SetMenuItems(menu[rootname], rootname);
        let runids = [];
        let menus = CreateMenuList(menulist, menucont, null, runids);
    });

    GUIConf.ascii = {};
    Object.keys(AsciiFormats).forEach(el => {
        GUIConf.ascii[el] = new AsciiData(AsciiFormats[el].dim, 
            AsciiFormats[el].items, AsciiFormats[el].titles, AsciiFormats[el].ordinate);
    });

    GUIConf.GUIpanels = {
        [EBLabel]: new EBPrmOptions(),
        [SeedLabel]: new SeedPrmOptions(),
        [SPXOutLabel]: new SPXOutPrmOptions(),
        [UndLabel]: new UndPrmOptions(),
        [LatticeLabel]: new LatticePrmOptions(),
        [AlignmentLabel]: new AlignUPrmOptions(),
        [WakeLabel]: new WakePrmOptions(),
        [ChicaneLabel]: new ChicanePrmOptions(),
        [DispersionLabel]: new DispersionPrmOptions(),
        [SimCondLabel]: new SimCtrlPrmOptions(),
        [DataDumpLabel]: new OutDataPrmOptions(),
        [OutFileLabel]: new OutFileOptions(),
        [FELLabel]: new FELPrmOptions(),
        [PrePLabel]:new PreProcessOptions(),
        [PartConfLabel]: new PartFormatOptions(),
        [PartPlotConfLabel]: new PDPlotOptions(),
        [MBunchEvalLabel]:new MBunchPrmOptions(),
        [PostPLabel]:new PostProcessOptions(),
        [DataUnitLabel]: new DataUnitsOptions()
    };    
    GUIConf.GUIpanels[EBLabel].SetObjects(GUIConf.GUIpanels[SimCondLabel]);
    GUIConf.GUIpanels[ChicaneLabel].SetObjects(GUIConf.GUIpanels[SimCondLabel]);
    GUIConf.GUIpanels[SimCondLabel].SetObjects(GUIConf.GUIpanels[EBLabel], GUIConf.GUIpanels[SeedLabel], GUIConf.GUIpanels[ChicaneLabel]);
    GUIConf.GUIpanels[DataDumpLabel].SetObjects(GUIConf.GUIpanels[SimCondLabel]);

    GUIConf.guids = {
        [EBLabel]: "ebeam-div",
        [SeedLabel]: "seed-div",
        [SPXOutLabel]: "spxout-div",
        [UndLabel]: "und-div",
        [LatticeLabel]: "lattice-div",
        [AlignmentLabel]: "ualign-div",
        [WakeLabel]: "wake-div",
        [ChicaneLabel]: "chicane-div",
        [DispersionLabel]: "dispersion-div",
        [SimCondLabel]: "simctrl-div",
        [DataDumpLabel]: "dump-div",
        [OutFileLabel]: "outfile-div",
        [FELLabel]: "felprms-div",
        [PrePLabel]: "preproc-subconf-div",
        [PartConfLabel]: "preproc-part",
        [PartPlotConfLabel]: "preproc-part-plotconf",
        [MBunchEvalLabel]: "preproc-seed",
        [PostPLabel]: "postp-conf-cont"
    }
    GUIConf.exports = [
        EBLabel,
        SeedLabel,
        SPXOutLabel,
        UndLabel,
        LatticeLabel,
        AlignmentLabel,
        WakeLabel,
        ChicaneLabel,
        DispersionLabel,
        SimCondLabel,
        DataDumpLabel,
        OutFileLabel,
        PartConfLabel
    ];
   
    GUIConf.plotly = null;
    GUIConf.simproc = [];
    GUIConf.mbobjs = {};
    GUIConf.subwindows = 0;

    GUIConf.filename = null;
    GUIConf.input = {};

    let outcategs = Object.values(GUILabels.datatype);
    GUIConf.postprocessor = new PostProcessor("", "postp-plot", 
        outcategs, GainCurveLabel, "resultdata", GUIConf.guids[PostPLabel]);
    GUIConf.postprocessor.EnableSubPanel(true);
    document.getElementById("postp-view-cont").appendChild(GUIConf.postprocessor.GetPanel());

    // assign labels and ids to buttons for preprocessing
    let labels = Object.keys(GUILabels.preproc);
    labels.forEach(label => {
        let element = document.getElementById("preproc-"+label);
        element.innerHTML = MenuLabels[label];
        element.id = GetPreprocID(label);
    });

    Object.keys(GUIConf.guids).forEach((el) => {
        if(GUIConf.guids[el] == "preproc-part"){
            document.getElementById("preproc-part-anadiv").prepend(GUIConf.GUIpanels[el].GetTable());
        }
        else{
            document.getElementById(GUIConf.guids[el]).prepend(GUIConf.GUIpanels[el].GetTable());
        }
    })

    // assign default settings
    Object.keys(MainPrmLabels).forEach(el => {
        if(InputPanels.includes(el)){
            GUIConf.input[el] = GUIConf.GUIpanels[el].JSONObj;
        }
        if(SettingPanels.includes(el)){
            Settings[el] = GUIConf.GUIpanels[el].JSONObj;
        }
    })
    GUIConf.input[UndDataLabel] = {names:[], data:[]};
    GUIConf.default = CopyJSON(GUIConf.input);
    GUIConf.defref = CopyJSON(GUIConf.input);
    Object.assign(GUIConf.defref, Settings);
    GUIConf.filename = "";

    GUIConf.panelid = "ebeam-seed-tab";

    let plotoption = new PlotOptions();
    GUIConf.def_plot_configs = CopyJSON(plotoption.JSONObj);

    GUIConf.plot_aspect = {
        ["preproc-plot"]: 0.75,
        ["postp-plot"]: 0.75
    };
}

// gui setup
function OnNewFile()
{
    if(GUIConf.input[OutFileLabel][OutputOptionsLabel.folder[0]] == "" 
        && Framework == TauriLabel){
        GUIConf.input[OutFileLabel][OutputOptionsLabel.folder[0]] = GUIConf.wdname;
    }

    SetPreprocessUData();
    document.getElementById("preproc-part-anadiv").classList.add("d-none");
    document.getElementById("preproc-part-cont").innerHTML = "";
    document.getElementById("preproc-part-plotconf-div").classList.add("d-none");

    GUIConf.part_data = null;
    delete GUIConf.qprofile;
    delete GUIConf.spxobj;
    GUIConf.slice_prms = new Array(SliceTitles.length);
    UpdateEBBase();
    Update();
    SetUndulatorDataList();
    GUIConf.mbobjs = {};

    if(GUIConf.panelid != null){
        if(GUIConf.panelid == "preproc-tab"){
            SetPreprocessPlot();
            ArrangePPPanel();
        }
    }
}

async function MenuCommand(id)
{
    let options  = {
        title: "",
        filters: [{
            name: "JSON",
            extensions: ["json"]
          }]
    };
    if(Settings.defpaths.hasOwnProperty(id)){
        options.defaultPath = Settings.defpaths[id];
    }

    if(id.includes(MenuLabels.new)){
        SetWindowTitle();
        GUIConf.input = CopyJSON(GUIConf.default);
        GUIConf.filename = "";
        for(const item of InputPanels){
            GUIConf.GUIpanels[item].JSONObj = GUIConf.input[item];
        }
        OnNewFile();
        ArrangeMenus();
        delete Settings.lastloaded;
    }
    else if(id.includes(MenuLabels.open) || id.includes(MenuLabels.outpostp)){
        GUIConf.fileid = id;
        if(Framework == TauriLabel){
            let title = "Open a SIMPLEX parameter file.";
            if(id.includes(MenuLabels.outpostp)){
                title = "Open a file for the post-processed data."
            }
            let path = await GetPathDialog(title, id, true, true, true, false);
            if(path == null){
                return;
            }
            if(!id.includes(MenuLabels.outpostp)){
                Settings.lastloaded = path;
            }
            window.__TAURI__.tauri.invoke("read_file", {path: path})
            .then((data) => {
                HandleFile(data, path, true);
            });
        }
        else if(Framework == BrowserLabel || Framework == ServerLabel){
            document.getElementById("file-main").setAttribute("accept", "application/json");
            document.getElementById("file-main").click();
            document.getElementById("file-main").removeAttribute("accept");
        }
        else if(Framework == PythonGUILabel){
            PyQue.Put(id);
        }
    }
    else if(id.includes(MenuLabels.loadf)){
        document.getElementById("postproc-tab").click();
        GUIConf.postprocessor.Import();
    }
    else if(id.includes(MenuLabels.exit)){
        if(Framework == TauriLabel){
            BeforeExit().then((e) => {
                window.__TAURI__.process.exit(0);
            });
        }
        else if(Framework == BrowserLabel || Framework == ServerLabel){
            window.open("","_self").close();
        }        
        else if(Framework == PythonGUILabel){
            PyQue.Put(id);
        }
    }
    else if(id.includes(MenuLabels.save) || id.includes(MenuLabels.saveas)){
        if(Framework == TauriLabel){
            let data = FormatArray(JSON.stringify(GUIConf.input, null, JSONIndent));
            if(id == [MenuLabels.file, MenuLabels.saveas].join(IDSeparator)){
                let path = await GetPathDialog(
                    "Input a data name to save the parameters.", id, false, true, true, false);
                if(path == null){
                    return;
                }
                Settings.lastloaded = path;
                window.__TAURI__.tauri.invoke("write_file", { path: path, data: data});
                SetWindowTitle(path);
                ArrangeMenus();
            }
            else{
                window.__TAURI__.tauri.invoke("write_file", { path: GUIConf.filename, data: data});
            }
        }
        else if(Framework == BrowserLabel || Framework == ServerLabel){
            ExportObjects(GUIConf.input, GUIConf.filename)
        }
        else if(Framework == PythonGUILabel){
            PyQue.Put(id);
        }
    }
    else if(id.includes(MenuLabels.run)){
        if(id.includes(MenuLabels.process) || 
                (id.includes(MenuLabels.start) && Framework != BrowserLabel)){
            RunCommand(id);
        }
        else if(Framework != PythonGUILabel){
            ExportCommand();
        }
        else{
            PyQue.Put(id);
        }
    }
    else if(id == "scan-prm-item"){
        let scanconfig = Settings.scanconfig;
        let jxy = ScanTarget.jxy;
        let is2d = jxy >= 0;
        let isint = ScanTarget.isinteger;
        let scanoption = new ScanOptions(ScanTarget.isinteger, is2d);
        if(!scanconfig.hasOwnProperty(ScanTarget.item)){
            let curra = GUIConf.GUIpanels[ScanTarget.category].JSONObj[ScanTarget.item];
            let curr;
            if(is2d){
                curr = curra[jxy];
            }
            else{
                curr = curra;
            }
            if(isint){
                scanconfig[ScanTarget.item] = {
                    [ScanConfigLabel.initiali[0]]: curr,
                    [ScanConfigLabel.finali[0]]: curr+1,
                    [ScanConfigLabel.interval[0]]: 1,
                    [ScanConfigLabel.iniserno[0]]: 1,
                }    
                if(is2d){
                    let tmpconf = scanconfig[ScanTarget.item];
                    tmpconf[ScanConfigLabel.scan2dtype[0]] = Scan2D1DLabel;
                    tmpconf[ScanConfigLabel.initiali2[0]] = curra;
                    tmpconf[ScanConfigLabel.finali2[0]] = [curra[0]+1,curra[1]+1];
                    tmpconf[ScanConfigLabel.interval2[0]] = [1,1];
                    tmpconf[ScanConfigLabel.iniserno2[0]] = [1,1];
                }
            }
            else{
                scanconfig[ScanTarget.item] = {
                    [ScanConfigLabel.initial[0]]: curr*0.8,
                    [ScanConfigLabel.final[0]]: curr*1.2,
                    [ScanConfigLabel.scanpoints[0]]: 11,
                    [ScanConfigLabel.iniserno[0]]: 1
                }    
                if(is2d){
                    let tmpconf = scanconfig[ScanTarget.item];
                    tmpconf[ScanConfigLabel.scan2dtype[0]] = Scan2D1DLabel;
                    tmpconf[ScanConfigLabel.initial2[0]] = [curra[0]*0.8,curra[1]*0.8];
                    tmpconf[ScanConfigLabel.final2[0]] = [curra[0]*1.2,curra[1]*1.2];
                    tmpconf[ScanConfigLabel.scanpoints2[0]] = [11,11];
                    tmpconf[ScanConfigLabel.iniserno2[0]] = [1,1];                    
                }
            }
        }
        else if(is2d){
            let tmpconf = scanconfig[ScanTarget.item];
            if(isint){
                tmpconf[ScanConfigLabel.initiali[0]] = tmpconf[ScanConfigLabel.initiali2[0]][jxy];
                tmpconf[ScanConfigLabel.finali[0]] = tmpconf[ScanConfigLabel.finali2[0]][jxy];
                tmpconf[ScanConfigLabel.interval[0]] = tmpconf[ScanConfigLabel.interval2[0]][jxy];
            }
            else{
                tmpconf[ScanConfigLabel.initial[0]] = tmpconf[ScanConfigLabel.initial2[0]][jxy];
                tmpconf[ScanConfigLabel.final[0]] = tmpconf[ScanConfigLabel.final2[0]][jxy];
                tmpconf[ScanConfigLabel.scanpoints[0]] = tmpconf[ScanConfigLabel.scanpoints2[0]][jxy];
            }
        }
        GUIConf.scanconfigold =  CopyJSON(scanconfig[ScanTarget.item]);
        scanoption.JSONObj = GUIConf.scanconfigold;
        let title = "Scan \""+ScanTarget.item+"\"";
        ShowDialog(title, true, false, "",  scanoption.GetTable(), CreateScan)
        scanoption.SetPanel();
    }
    else if(id.includes(MenuLabels.about)){
        let contdiv = document.createElement("div");
        contdiv.innerHTML = "";
        contdiv.className = "d-flex flex-column align-items-stretch";
        let maintxt = document.createElement("p");
        maintxt.className = "dialogmsg m-0";
        maintxt.innerHTML = 
        "SIMPLEX is a computer software package to simulate the lasing process in free electron lasers. "+
        "If you are submitting articles to scientific journals with the results obtained by using "+
        "SIMPLEX, cite the reference below.";
        let papertxt = document.createElement("p");
        papertxt.className = "text-center dialogmsg m-0";
        papertxt.innerHTML = "J. Synchrotron Rad. 22 (2015) 1319";
        let urltxt = document.createElement("p");
        urltxt.innerHTML = "https://spectrax.org/simplex/index.html<br>admin@spectrax.org";
        urltxt.className = "text-center dialogmsg m-0";
        contdiv.appendChild(maintxt);
        contdiv.appendChild(papertxt);
        contdiv.appendChild(document.createElement("hr"));
        contdiv.appendChild(urltxt);
        ShowDialog("About SIMPLEX ("+Version+")", false, true, "", contdiv);
    }
    else if(id.includes(MenuLabels.help)){
        if(Framework == TauriLabel){
            try {
                let refpath;
                if(RunOS == "Linux"){
                    refpath = "/usr/share/simplex/help/reference.html";
                    if(await window.__TAURI__.invoke("exists", {path: refpath}) == false){
                        refpath = "help"+window.__TAURI__.path.sep+"reference.html";
                    }
                }
                else{
                    refpath = "help"+window.__TAURI__.path.sep+"reference.html";
                }
                await window.__TAURI__.shell.open(refpath);
            } catch (e) {
                Alert(e);
            }        
        }
        else{
            window.open("help/reference.html");
        }
    }
}

// enable/disable menu commands
function ArrangeMenus()
{
    let canrun = Framework != PythonScriptLabel
    let cansaveas = canrun;
    let cansave = GUIConf.filename != "" && cansaveas;

    let items = [
        ["file", "save", cansave], 
        ["file", "saveas", cansaveas], 
        ["file", "exit", canrun], 
        ["preproc", "ascii", canrun], 
        ["postproc", "ascii", canrun], 
        ["postproc", "save", canrun], 
        ["run", "export", canrun]
    ];

    items.forEach(item => {
        let id = [MenuLabels[item[0]], MenuLabels[item[1]]].join(IDSeparator);
        if(item[2]){
            document.getElementById(id).removeAttribute("disabled");
        }
        else{
            document.getElementById(id).setAttribute("disabled", true);
        }
    })
}

function HandleFile(data, filename, isfinal)
{
    if(GUIConf.fileid == [MenuLabels.file, MenuLabels.open].join(IDSeparator)){
        SetWindowTitle(filename);
        try {
            GUIConf.input = JSON.parse(data);
        }
        catch(e) {
            let sidx = GUIConf.filename.lastIndexOf(".");
            if(sidx >= 0){
                GUIConf.filename = GUIConf.filename.substring(0, sidx)+".json";
                Settings.lastloaded = GUIConf.filename;
            }
            GUIConf.input = ConvertFile(data);
        }       
        if(GUIConf.input.hasOwnProperty(InputLabel)){
            GUIConf.input = CopyJSON(GUIConf.input[InputLabel]);
        }
        if(GUIConf.input.hasOwnProperty(UndLabel)){
            ["TaperPrm", "UModelPrm"].forEach((key) => {
                if(GUIConf.input[UndLabel].hasOwnProperty(key)){
                    Object.keys(GUIConf.input[UndLabel][key]).forEach((obs) => {
                        GUIConf.input[UndLabel][obs] = GUIConf.input[UndLabel][key][obs];
                    });
                    delete GUIConf.input[UndLabel][key];
                }
            });
        }

        let oldpara = "Enable Parallel Computing";
        if(GUIConf.input[SimCondLabel].hasOwnProperty(oldpara)){
            if(GUIConf.input[SimCondLabel][oldpara]){
                GUIConf.input[SimCondLabel][SimCtrlsPrmsLabel.parascheme[0]] = ParaMPILabel;
            }
            delete GUIConf.input[SimCondLabel][oldpara];
        }

        for(const item of InputPanels){
            let def = CopyJSON(GUIConf.default[item]);
            if(SettingPanels.includes(item)){
                def = CopyJSON(Settings[item]);
            }
            if(GUIConf.input.hasOwnProperty(item)){
                GUIConf.input[item] = Object.assign(def, GUIConf.input[item]);
            }
            else{
                GUIConf.input[item] = def;
            }
            GUIConf.GUIpanels[item].JSONObj = GUIConf.input[item];
        }
        for(const item of InputPanels){
            GUIConf.GUIpanels[item].SetPanel();
        }

        if(GUIConf.input[EBLabel].hasOwnProperty(EBeamPrmsLabel.basespec[0])){            
            let keys = Object.keys(GUIConf.input[EBLabel][EBeamPrmsLabel.basespec[0]]);
            for(let j = 0; j < keys.length; j++){
                if(EBBasePrmLabels.indexOf(keys[j]) < 0){
                    delete GUIConf.input[EBLabel][EBeamPrmsLabel.basespec[0]][keys[j]];
                }
            }
        }
        if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == CustomParticle){
            ImportParticle();
        }

        if(!GUIConf.input.hasOwnProperty(UndDataLabel)){
            GUIConf.input[UndDataLabel] = {names:[], data:[]};
        }
        OnNewFile();
    }
    else if(GUIConf.fileid == "preproc-udata"){
        let units = [1, 1, 1];        
        if(GUIConf.GUIpanels[DataUnitLabel].JSONObj[DataUnitsLabel.zpos[0]] == UnitMiliMeter){
            units[0] = 1e-3;
        }
        if(GUIConf.GUIpanels[DataUnitLabel].JSONObj[DataUnitsLabel.bxy[0]] == UnitGauss){
            units[1] = units[2] = 1e-4;
        }
        GUIConf.ascii[UndDataLabel].SetData(data, units, [1, 2, 3]);
        let dindex = GUIConf.input[UndDataLabel].names.indexOf(filename);
        if(dindex >= 0){
            if(!confirm("Data \""+filename+"\" already imported. Replace?")){
                GUIConf.loading = false;
                return;
            }
            GUIConf.input[UndDataLabel].data[dindex] = GUIConf.ascii[UndDataLabel].GetObj();
        }
        else{
            GUIConf.input[UndDataLabel].names.push(filename);
            GUIConf.input[UndDataLabel].data.push(GUIConf.ascii[UndDataLabel].GetObj());
            let select = document.getElementById("preproc-udata-select");
            AddSelection(select, filename, true, true)
        }        
        if(isfinal){
            UpdatePlot(UndDataLabel);
            SetUndulatorDataList();
        }
    }
    else if(GUIConf.fileid == [MenuLabels.preproc, MenuLabels.load].join(IDSeparator)){
        let str;
        if(data.length > 1000){
            str = data.substring(0, 1000);
            str += "....."
        }
        else{
            str = data;
        }
        const regexp = /[\r\n]/g;        
        let cols = str.match(regexp).length+2;
        cols = Math.min(Math.max(3, cols), 5);
        let cont = document.getElementById("preproc-part-cont");
        cont.innerHTML = str;
        cont.setAttribute("rows", cols.toString());
        GUIConf.part_data = data;
        document.getElementById("preproc-part-anadiv").classList.remove("d-none");
        document.getElementById("preproc-part-plotconf-div").classList.add("d-none");
        GUIConf.input[EBLabel][EBeamPrmsLabel.partspec[0]] = BundleEBeamSpecs();
        AnalyzeParticle();
    }
    else if(GUIConf.fileid == [MenuLabels.preproc, MenuLabels.import].join(IDSeparator)){
        let units = null;
        if(GUIConf.import.ascii == CustomSlice)
        {
            units = new Array(SliceTitles.length);
            units.fill(1);
            if(GUIConf.GUIpanels[DataUnitLabel].JSONObj[DataUnitsLabel.energy[0]] == UnitMeV){
                units[SliceTitles.indexOf(EnergyLabel)] = 1e-3;
            }
            if(GUIConf.GUIpanels[DataUnitLabel].JSONObj[DataUnitsLabel.energy[0]] == UnitGamma){
                units[SliceTitles.indexOf(EnergyLabel)] = 1e-3*MC2MeV;
            }
        }
        else if(GUIConf.import.ascii == CustomCurrent)
        {
            units = [1, 1];
        }
        else if(GUIConf.import.ascii == CustomEt)
        {
            units = [1, 1, 1];
        }
        if(units != null){
            if(GUIConf.GUIpanels[DataUnitLabel].JSONObj[DataUnitsLabel.bpos[0]] == UnitMiliMeter){
                units[0] = 1e-3;
            }
            else if(GUIConf.GUIpanels[DataUnitLabel].JSONObj[DataUnitsLabel.bpos[0]] == UnitSec){
                units[0] = CC;
            }
            else if(GUIConf.GUIpanels[DataUnitLabel].JSONObj[DataUnitsLabel.bpos[0]] == UnitpSec){
                units[0] = 1e-12*CC;
            }
            else if(GUIConf.GUIpanels[DataUnitLabel].JSONObj[DataUnitsLabel.bpos[0]] == UnitfSec){
                units[0] = 1e-15*CC;
            }
        }
        GUIConf.ascii[GUIConf.import.ascii].SetData(data, units);
        GUIConf.input[GUIConf.import.category][GUIConf.import.prmlabel]
            = GUIConf.ascii[GUIConf.import.ascii].GetObj();
        UpdateEBBase();
        Update();
        UpdatePPPlot();
    }
    else if(GUIConf.fileid == [MenuLabels.file, MenuLabels.outpostp].join(IDSeparator)){
        try {
            let obj = JSON.parse(data);
            CreateNewplot(obj);    
        } catch (e) {
            Alert(e);
        }
    }
    GUIConf.loading = false;
}

async function GetConfiguration()
{
    try {
        SwitchSpinner(true);
        let conffile = await window.__TAURI__.path.join(GUIConf.wdname, ConfigFileName);
        let data = await window.__TAURI__.tauri.invoke("read_file", { path: conffile});
        SwitchSpinner(false);
        if(data != ""){
            Object.assign(Settings, JSON.parse(data));
            let keys = Object.keys(Settings);
            for(const key of keys){
                if(!SettingKeys.includes(key)){
                    delete Settings[key];
                }
            }
            if(Settings.hasOwnProperty("animinterv")){
                AnimationInterval = Settings.animinterv;
            };
        }
    } catch(e) {
        Alert(e);
    }
}

var init_process = Initialize();

window.onload = async function()
{
    Object.keys(GUILabels.Category).forEach((el) => {
        if(el != "dataprocess" && el != "partconf" && el != "partplot"){
            document.getElementById(el).innerHTML = GUILabels.Category[el];
        }
    });
    document.getElementById("postp-rproc-btn").innerHTML = RawDataProcLabel;

    MainGUI();

    document.getElementById("file-main").addEventListener(
        "change", (e) => {
            LoadFiles(e, HandleFile);
            document.getElementById("file-main").value = "";
        });

    let tabs = document.querySelectorAll(`[id$="tab"]`);
    let ids = [];
    tabs.forEach(el => {
        let pid = GetPanelID(el.id);
        if(ids.indexOf(pid) < 0){
            ids.push(pid);
        }
        el.addEventListener("click", ev => {
            if(ev.currentTarget.id == GUIConf.panelid){
                return;
            }
            document.getElementById(GUIConf.panelid).classList.remove("fw-bold");
            document.getElementById(ev.currentTarget.id).classList.add("fw-bold");
        
            GUIConf.panelid = ev.currentTarget.id;
        
            let id = GetPanelID(GUIConf.panelid);
            if(id == "postproc" || id == "preproc"){
                document.getElementById("fel-panel").classList.replace("d-flex", "d-none");
                if(id == "postproc"){
                    SetPlotSize(["postp-plot"]);    
                    GUIConf.postprocessor.Refresh();    
                }
                else{
                    SetPreprocessPlot();
                    ArrangePPPanel();
                    SetPlotSize(["preproc-plot"]);
                    if(GUIConf.plotly != null){
                        GUIConf.plotly.RefreshPlotObject();
                    }    
                }
            }
            else{
                document.getElementById("fel-panel").classList.replace("d-none", "d-flex");
            }
        });
    });

    let scanmenu = document.getElementById("scan-prm-item");
    scanmenu.addEventListener("click", ev => {
        MenuCommand(ev.currentTarget.id);
    });

    let plotdivs = Object.keys(GUIConf.plot_aspect);    
    for(let j = 0; j < plotdivs.length; j++){
        Observer[plotdivs[j]] = new MutationObserver((mutation) => {
            if(plotdivs[j] == "preproc-plot"){
                if(GUIConf.plotly != null){
                    GUIConf.plotly.RefreshPlotObject();
                }
            }
            else if(plotdivs[j] == "postp-plot"){
                GUIConf.postprocessor.Refresh();
            }
            let target = document.getElementById(plotdivs[j]);
            if(!target.classList.contains("d-none")){
                GUIConf.plot_aspect[plotdivs[j]] = target.clientHeight/target.clientWidth;
            }    
        });
        const options = {
            attriblutes: true,
            attributeFilter: ["style"]
        };
        Observer[plotdivs[j]].observe(document.getElementById(plotdivs[j]), options);
    }

    init_process.then(async function () {
        if(Settings.hasOwnProperty(PlotWindowsRowLabel)){
            GUIConf.postprocessor.SetPlotCols(Settings[PlotWindowsRowLabel]);
        }
        if(Settings.hasOwnProperty(SubPlotsRowLabel)){
            GUIConf.postprocessor.SetSubPlotCols(Settings[SubPlotsRowLabel]);
        }

        for(const option of SettingPanels){
            if(Settings.hasOwnProperty(option)){
                let defprms = CopyJSON(GUIConf.GUIpanels[option].JSONObj);
                Object.keys(defprms).forEach(key => {
                    if(!Settings[option].hasOwnProperty(key)){
                        Settings[option][key] = defprms[key];
                    }
                });
                GUIConf.GUIpanels[option].JSONObj = Settings[option];
                GUIConf.GUIpanels[option].SetPanel();
            }
        }

        GUIConf.fileid = [MenuLabels.file, MenuLabels.open].join(IDSeparator);

        OnNewFile();
        if(!CheckMenuLabels()){
            Alert("Key overlap found in MenuLabels constant");
        }
        if(Framework != BrowserLabel && Framework != ServerLabel){
            document.getElementById(GetPreprocID("load")).classList.add("d-none");
        }
        if(Framework == ServerLabel){
            LocalStorage(false);
        }
        SetSettingsGUI();
        if(Framework == ServerLabel && (iniFile != "" || iniPP != "" || iniLPP != "")){
            if(iniDir != ""){
                iniDir += "/"
            }
            if(iniFile != ""){
                let xhr = new XMLHttpRequest();
                xhr.open("GET", "get_file.php?filename=prm/"+iniDir+iniFile, true); 
                xhr.responseType = "text";
                xhr.addEventListener("load", async (e) => {
                    if(xhr.response != null){
                        HandleFile(xhr.response, iniFile, true);
                    }
                    ArrangeMenus();
                });
                xhr.send(null);    
            }
            if(iniPP != "" || iniLPP != ""){
                let iniPPs = [iniPP, iniLPP];
                for(let j = 0; j < 2; j++){
                    let PPfile = iniPPs[j];
                    if(PPfile == ""){
                        continue;
                    }
                    if(j == 1){
                        GUIConf.fileid = [MenuLabels.file, MenuLabels.outpostp].join(IDSeparator);
                    }
                    let ppfiles;
                    if(PPfile.includes(",")){
                        ppfiles = PPfile.split(",");
                    }
                    else{
                        ppfiles = [PPfile];
                    }
                    for(const ppfile of ppfiles){
                        let xhr = new XMLHttpRequest();
                        xhr.open("GET", "get_file.php?filename=data/"+iniDir+ppfile, true); 
                        xhr.responseType = "text";
                        xhr.addEventListener("load", async (e) => {
                            if(xhr.response != null){
                                if(j == 0){
                                    document.getElementById("postproc-tab").click();
                                    GUIConf.postprocessor.LoadOutputFile(xhr.response, ppfile, true);    
                                }
                                else{
                                    HandleFile(xhr.response, ppfiles, true);
                                }
                            }
                        });
                        xhr.send(null);    
                    }    
                }
            }
            return;
        }
        if(Framework == TauriLabel && Settings.hasOwnProperty("lastloaded"))
        {
            GUIConf.fileid = [MenuLabels.file, MenuLabels.open].join(IDSeparator);
            let data = await window.__TAURI__.tauri.invoke("read_file", { path: Settings.lastloaded });
            if(data != ""){
                HandleFile(data, Settings.lastloaded, true);
            }
        }
        ArrangeMenus();
    });
};

window.addEventListener("beforeunload", () => {
    if(Framework == TauriLabel){
        BeforeExit().then((e) => {
            window.__TAURI__.process.exit(0);
        });
    }
    else if(Framework == ServerLabel){
        LocalStorage(true);
    }
});

window.addEventListener("message", (e) => {
    if(e.data == "ready"){
        let object = PlotObjects.objects.Get();
        object.Framework = Framework;
        PlotObjects.windows.Get().postMessage(object, "*");
        return;
    }
    if(Framework != PythonGUILabel){
        return;
    }
    let obj;
    try {
        obj = JSON.parse(e.data);
    }
    catch (e) {
        Alert(e);
        return;
    }

    let id = [MenuLabels.duplicate]
    if(obj.type == "save"){
        id.push("save");
    }
    else{
        id.push(MenuLabels.ascii);        
    }
    id = id.join(IDSeparator);
    BufferObject = obj.data;
    PyQue.Put(id);
});

window.onresize = function()
{
    SetPlotSize();
}

// key binding for supplmental functions (generating C++ source code etc.)
window.addEventListener("keydown", (ev) => {
    try {
        if(ev.key == "e" && ev.ctrlKey && Framework == BrowserLabel){
            GenerateHeaderFile();
        }
        else if(ev.key == "q" && ev.ctrlKey && Framework == BrowserLabel){
            ExportHelpFile();
        }
    }
    catch (e) {
        Alert(e);
    }
}, false);
