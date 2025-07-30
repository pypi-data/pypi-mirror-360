"use strict";

// get data in memory buffer
function GetBufferData(limit, direct = false)
{
    let data;
    if(direct){
        data = BufferObject;
    }
    else{
        data = FormatArray(JSON.stringify(BufferObject, null, JSONIndent));
    }
    if(data.length > limit){
        return null;
    }
    return data;
}

// check scan availability
function GetScanAvailability(categ, label)
{
    let scanobj = {dimension: 0};
    if(!MainPrmLabels.hasOwnProperty(categ)){
        return scanobj;
    }
    let type = GUIConf.GUIpanels[categ].GetFormat(label);
    if(type == null){
        return scanobj;
    }
    scanobj.dimension = 1;
    if(type == ArrayLabel || type == ArrayIntegerLabel){
        scanobj.dimension = 2;
    }
    scanobj.integer = type == ArrayIntegerLabel || type == IntegerLabel;
    return scanobj;
}

// prepare scan
function CreateScanDirect(category, item, jxy, scanobj)
{
    let dimension = scanobj["dimension"];
    let isint = scanobj["integer"];
    let method2d = scanobj["method"];
    let bundle = scanobj["bundle"];
    let scanoption = new ScanOptions(isint, dimension == 2);

    let obj = scanoption.JSONObj;

    let values = scanobj["range"]
    let keys = new Array(4);
    let is2d = new Array(4);
    is2d.fill(false);

    if(isint){
        if(dimension == 1 || method2d == Scan2D1DLabel){
            keys[0] = ScanConfigLabel.initiali[0];
            keys[1] = ScanConfigLabel.finali[0];
            keys[2] = ScanConfigLabel.interval[0];
            keys[3] = ScanConfigLabel.iniserno[0];
        }
        else{
            keys[0] = ScanConfigLabel.initiali2[0];
            keys[1] = ScanConfigLabel.finali2[0];
            is2d[0] = is2d[1] = true;
            is2d[2] = is2d[3] = method2d != Scan2DLinkLabel;
            if(method2d == Scan2DLinkLabel){
                keys[2] = ScanConfigLabel.interval[0];
                keys[3] = ScanConfigLabel.iniserno[0];    
            }
            else{
                keys[2] = ScanConfigLabel.interval2[0];
                keys[3] = ScanConfigLabel.iniserno2[0];    
            }
        }
    }
    else{
        if(dimension == 1 || method2d == Scan2D1DLabel){
            keys[0] = ScanConfigLabel.initial[0];
            keys[1] = ScanConfigLabel.final[0];
            keys[2] = ScanConfigLabel.scanpoints[0];
            keys[3] = ScanConfigLabel.iniserno[0];
        }
        else{
            keys[0] = ScanConfigLabel.initial2[0];
            keys[1] = ScanConfigLabel.final2[0];
            is2d[0] = is2d[1] = true;
            is2d[2] = is2d[3] = method2d != Scan2DLinkLabel;
            if(method2d == Scan2DLinkLabel){
                keys[2] = ScanConfigLabel.scanpoints[0];
                keys[3] = ScanConfigLabel.iniserno[0];
                }
            else{
                keys[2] = ScanConfigLabel.scanpoints2[0];
                keys[3] = ScanConfigLabel.iniserno2[0];    
            }
        }
    }
    if(dimension == 2){
        obj[ScanConfigLabel.scan2dtype[0]] = method2d;
    }
//    let valids = scanoption.ExportCurrent();
//    if(valids.hasOwnProperty(ScanConfigLabel.bundle[0])){
//       obj[ScanConfigLabel.bundle[0]] = bundle;
//    }

    for(let j = 0; j < 4; j++){
        if(is2d[j] && !Array.isArray(values[j])){
            values[j] = [values[j], values[j]];
        }
        else if(!is2d[j] && Array.isArray(values[j])){
            values[j] = values[j][0];
        }
        obj[keys[j]] = values[j];
    }
    GUIConf.scanconfigold = obj;

    ScanTarget = {
        category:category,
        item:item,
        jxy:jxy,
        isinteger:isint
    }
    CreateScan();
}

// set status
function SetProcStatus(procid, data, cancel = false)
{    
    if(GUIConf.simproc[procid].Status() != 1){
        return false;
    }
    if(cancel){
        GUIConf.simproc[procid].FinishSingle(data);
    }
    else{
        GUIConf.simproc[procid].HandleStatus(data);
    }
    return true;
}

// Get MPI setting
function GetMPISetting()
{
    let obj = {};
    obj.enable = GUIConf.input[SimCondLabel][SimCtrlsPrmsLabel.parascheme[0]] == ParaMPILabel;
    obj.processes = GUIConf.input[SimCondLabel][SimCtrlsPrmsLabel.mpiprocs[0]];
    return obj;
}

// Get Multithread setting
function GetMultithreadSetting()
{
    let obj = {};
    obj.enable = GUIConf.input[SimCondLabel][SimCtrlsPrmsLabel.parascheme[0]] == MultiThreadLabel;
    obj.processes = GUIConf.input[SimCondLabel][SimCtrlsPrmsLabel.threads[0]];
    return obj;
}

// add menu for python version
function AddMenuPython()
{
    let parent = document.getElementById(MenuLabels.run+"-item");
    let menulist = [
        {type: "separator"},
        {
            id: [MenuLabels.run, MenuLabels.python].join(IDSeparator),
            label: MenuLabels.python,
            type: "item"
        }    
    ];
    CreateMenuList(menulist, parent);    
}

// set variables from the python script
function SetFromPython(target, object)
{
    if(target == "Framework"){
        Framework = object;
        GUIConf.postprocessor.HideDLButton();
        document.getElementById(GetPreprocID("load")).classList.add("d-none");
    }
    else if(target == "Settings"){
        Settings = object;
//
//
//
        for(const option of SettingPanels){
            GUIConf.GUIpanels[option].JSONObj = Settings[option];
            GUIConf.GUIpanels[option].SetPanel();
        }
        if(object.hasOwnProperty("categ")){
            if(SettingPanels.includes(object.categ)){
                GUIConf.GUIpanels[object.categ].JSONObj = Settings[object.categ];
            }
            delete Settings.categ;
        }
    }
    else if(target == "fileid"){
        GUIConf.fileid = object;
//        
    }
    else if(target == "filename"){
        GUIConf.filename = object;
    }
    else if(target == "guipanel"){
        GUIConf.GUIpanels[object[0]].JSONObj[object[1]] = object[2];
        GUIConf.GUIpanels[object[0]].SetPanel();
    }
    else if(target == "element"){
        document.getElementById(object[0]).value = object[1];
    }
    else if(target == "spxout"){
        GUIConf.spxobj = object;
    }
    else if(target == "pformat"){
        let rkeys = Object.keys(ParticleConfigLabel);
        Object.keys(object).forEach((key) => {
            let skey = key;
            if(rkeys.includes(key)){
                key = ParticleConfigLabel[key][0];
            }
            GUIConf.GUIpanels[PartConfLabel].JSONObj[key] = object[skey];
        });
        GUIConf.GUIpanels[PartConfLabel].SetPanel();
        AnalyzeParticle();
    }
    else if(target == "loading"){
        GUIConf.loading = object;
    }
}

// command menu for script
function CommandScript(id)
{
    let msg = "";
    let element = document.getElementById(id);
    if(element == null){
        msg = "Command \""+id+"\" is invalid."
    }
    else if(element.disabled){
        msg = "Command \""+id+"\" is currently disabled."         
    }
    else{
        if(GUIConf.hasOwnProperty("disabled")){
            GUIConf.disabled.forEach(disabled => {
                if(id.includes(disabled)){
                    msg = "Command \""+id+"\" is currently disabled."         
                }
            })    
        }
        if(msg == ""){
            element.click();
        }
    }
    return msg;
}

// get GUI elements currently visible
function GetGUIShown(category, label)
{
    if(!MainPrmLabels.hasOwnProperty(category)){
        return null;
    }
    if(!MainPrmLabels[category].hasOwnProperty(label)){
        return null;
    }
    if(MainPrmLabels[category].hasOwnProperty(label)){
        label = MainPrmLabels[category][label][0];
    }
    let obj = GUIConf.GUIpanels[category].JSONObj;
    if(!obj.hasOwnProperty(label)){
        return null;
    }
    return obj[label];
}

// set object from script
function SetObjectScript(id)
{
    if(id.includes(MenuLabels.run) && id.includes(MenuLabels.export)){
        ExportCommand();
        return;
    }
    let obj, dataname = "";
    if(id.includes(MenuLabels.file) && (id.includes(MenuLabels.save) 
        || id.includes(MenuLabels.saveas)))
    {
        obj = CopyJSON(GUIConf.input);
    }
    else if(id.includes(MenuLabels.postproc) && id.includes(MenuLabels.save)){
        obj = GUIConf.postprocessor.GetWholeObject();
        dataname = GUIConf.postprocessor.GetCurrentDataName();
    }
    ExportObjects(obj, dataname);
}

// get menu items and labels for python
function GetMenuItems()
{
    let obj = CopyJSON(Labels4Python);
    let menus = document.querySelectorAll(".dropdown-item");
    obj.calcid = [];
    let menuid = [];
    menus.forEach(el => {
/*





        empty space






*/
        if(!el.id.includes("scan")){
            menuid.push(el.id);
        }
    });

    let tabs = document.querySelectorAll(".nav-link");
    obj.tabs = {};
    obj.tablabels = {};
    tabs.forEach(el =>{
        let label = el.id.replace("-tab", "");
        obj.tablabels[label] = el.innerHTML;
        label = el.innerHTML;
        obj.tabs[label] = el.id;
    });
    obj.tabs[PartConfLabel] = obj.tabs[PrePLabel];

    obj.modes = {
        "gui": PythonGUILabel,
        "script": PythonScriptLabel
    }

    obj.dialogs = {
        "file": FileLabel,
        "dir": FolderLabel,
        "grid": GridLabel,        
    }

    return obj;
}

// get labels to save in Settings
function GetSettingLabels(categ)
{
    if(categ == AccuracyLabel){
        return AccuracyOptionsLabel;
    }
    else if(categ == DataUnitLabel){
        return DataUnitOptionsLabel
    }
    else if(categ == MPILabel){
        return MPIOptionsLabel;
    }
    return null;
}

// get parameter labels with formats
function GetPrmLabels(categ)
{
    let obj = {label:{}, format:{}};

    if(!MainPrmLabels.hasOwnProperty(categ)){
        return obj;
    }

    let validlist = GUIConf.GUIpanels[categ].GetShowList();
    if(validlist == null){
        return obj;
    }
    let validkeys = [];
    Object.keys(validlist).forEach(key => {
        if(validlist[key] > 0){
            validkeys.push(key);
        }
    })

    Object.keys(MainPrmLabels[categ]).forEach(key => {
        let label = MainPrmLabels[categ][key][0];
        if(validkeys.includes(label)){
            let format = GUIConf.GUIpanels[categ].GetFormat(label);
            if(format == NumberLabel || format == IncrementalLabel){
                format = "float";
            }
            else if(format == IntegerLabel){
                format = "integer";
            }
            else if(format == ArrayLabel || format == ArrayIncrementalLabel){
                format = "list";
            }
            else if(format == ArrayIntegerLabel){
                format = "list";
            }
            else if(format == SelectionLabel){
                format = GUIConf.GUIpanels[categ].GetSelectable(label);
            }
            else if(format == FileLabel){
                format = "filename";
            }
            else if(format == FolderLabel){
                format = "directory";
            }
            else if(format == PlotObjLabel){
                format = "dict";
            }
            else if(format == GridLabel){
                format = "spreadsheet";
            }
            else if(format == "boolean"){
                format = "bool";
            }
            obj.label[key] = label;
            obj.format[label] = format;
        }
    });
    return obj;
}

// get relative window size
function RelativeFitWindowSize()
{
    let winoffset = [15, 10];
    if(!document.getElementById("maingui").classList.contains("active")){
        return [0, 0];
    }
    let main = document.getElementById("maingui").getBoundingClientRect();
    let gui = document.getElementById("gui-panel").getBoundingClientRect();
    return [main.width-window.innerWidth+winoffset[0], gui.height-window.innerHeight+winoffset[1]];
}

// check if former command is still running
function PlotRunning()
{
    return PlotObjects.windows.Count() > 0
}

// select tab
function SelectTab(category)
{
    if(!TabIDs.hasOwnProperty(category)){
        return false;
    }
    let element = document.getElementById(TabIDs[category]);
    element.click();
    return true;
}
