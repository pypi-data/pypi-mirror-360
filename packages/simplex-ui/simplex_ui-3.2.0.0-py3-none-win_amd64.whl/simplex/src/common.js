"use strict";

// class for queue
class Queue 
{
    constructor() {
        this.items = [];
    }
  
    Put(element) {
        this.items.push(element);
    }
  
    Get() {
        if (this.items.length == 0){
            return "";
        }
        return this.items.shift();
    }

    Clear() {
        this.items = [];
    }

    Count() {
        return this.items.length;
    }
}

// check overlap of MenuLabels keys
function CheckMenuLabels()
{
    let menus = {};
    Object.keys(GUILabels).forEach(type => {
        Object.keys(GUILabels[type]).forEach(key => {
            if(menus.hasOwnProperty(key)){
                if(menus[key] != GUILabels[type][key]){
                    return false;
                }
            }
            else{
                menus[key] = GUILabels[type][key];
            }
        });      
    });
    return true;
}

// create a scan process
function CreateScan()
{
    let scanconfig = Settings.scanconfig;
    let jxy = ScanTarget.jxy;
    let is2d = jxy >= 0;
    let isint = ScanTarget.isinteger;
    let item = ScanTarget.item;

    scanconfig[item] = CopyJSON(GUIConf.scanconfigold);
    let obj = GetSimulationObject();
    let scanobj;
    if(is2d){
        let type = scanconfig[item][ScanConfigLabel.scan2dtype[0]];
        if(type == Scan2D1DLabel){
            let tmpconf = scanconfig[item];
            if(isint){
                tmpconf[ScanConfigLabel.initiali2[0]][jxy] = tmpconf[ScanConfigLabel.initiali[0]];
                tmpconf[ScanConfigLabel.finali2[0]][jxy] = tmpconf[ScanConfigLabel.finali[0]];
                tmpconf[ScanConfigLabel.interval2[0]][jxy] = tmpconf[ScanConfigLabel.interval[0]];
            }
            else{
                tmpconf[ScanConfigLabel.initial2[0]][jxy] = tmpconf[ScanConfigLabel.initial[0]];
                tmpconf[ScanConfigLabel.final2[0]][jxy] = tmpconf[ScanConfigLabel.final[0]];
                tmpconf[ScanConfigLabel.scanpoints2[0]][jxy] = tmpconf[ScanConfigLabel.scanpoints[0]];
            }
            tmpconf[ScanConfigLabel.iniserno2[0]][jxy] = tmpconf[ScanConfigLabel.iniserno[0]];
        }
        let keys = isint ? ["initiali2", "finali2", "interval2", "iniserno2"] : 
            ["initial2", "final2", "scanpoints2", "iniserno2"];
        scanobj = [];
        for(let j = 0; j < keys.length; j++){
            scanobj.push(
                Array.from(
                    scanconfig[item][
                        ScanConfigLabel[keys[j]][0]
                    ]
                )
            );
        }
        let curr = GUIConf.GUIpanels[ScanTarget.category].JSONObj[item][1-jxy];
        if(type == Scan2D1DLabel){
            scanobj[0][1-ScanTarget.jxy] = curr;
            scanobj[1][1-ScanTarget.jxy] = curr;
            scanobj[2][1-ScanTarget.jxy] = 0;
            scanobj[3][1-ScanTarget.jxy] = 0;
        }
        else if(type == Scan2DLinkLabel){
            if(isint){
                scanobj[0] = [scanconfig[item][ScanConfigLabel.initiali[0]], scanconfig[item][ScanConfigLabel.initiali[0]]];
                scanobj[1] = [scanconfig[item][ScanConfigLabel.finali[0]], scanconfig[item][ScanConfigLabel.finali[0]]];
                scanobj[2] = [scanconfig[item][ScanConfigLabel.interval[0]], -1];
            }
            else{
                scanobj[2] = [scanconfig[item][ScanConfigLabel.scanpoints[0]], -1];
            }
            scanobj[3] = [scanconfig[item][ScanConfigLabel.iniserno[0]], -1];
        }
    }
    else{
        scanobj = isint ? 
        [
            scanconfig[item][ScanConfigLabel.initiali[0]],
            scanconfig[item][ScanConfigLabel.finali[0]],
            scanconfig[item][ScanConfigLabel.interval[0]],
            scanconfig[item][ScanConfigLabel.iniserno[0]]
        ] :
        [
            scanconfig[item][ScanConfigLabel.initial[0]],
            scanconfig[item][ScanConfigLabel.final[0]],
            scanconfig[item][ScanConfigLabel.scanpoints[0]],
            scanconfig[item][ScanConfigLabel.iniserno[0]]
        ];    
    }
    if(ScanTarget.isinteger){
        scanobj.push(IntegerLabel);
    }
    let categ = ScanTarget.category;
    if(Array.isArray(categ)){
        obj[ScanLabel] = {
            [categ[0]]: {
                [categ[1]] : {
                    [item]: scanobj
                }
            }
        }       
    }
    else{
        obj[ScanLabel] = {
            [categ]: {
                [item]: scanobj
            }
        }       
    }
//    obj[ScanLabel][ScanConfigLabel.bundle[0]] = scanconfig[item][ScanConfigLabel.bundle[0]];
    CreateProcess([MenuLabels.run, MenuLabels.process].join(IDSeparator), obj);
}

// create a calculation process
function CreateProcess(id, obj)
{
    let dataname = GetDataPath(GUIConf.GUIpanels[OutFileLabel].JSONObj);
    document.getElementById("calcproc-card").classList.remove("d-none");
    let skip = false;
    if(id.includes(MenuLabels.process) && GUIConf.simproc.length > 0 
            && Last(GUIConf.simproc).Status() == 0){
        Last(GUIConf.simproc).AppendProcess(obj, dataname);
    }
    else if(GUIConf.simproc.length == 0 || Last(GUIConf.simproc).Status() != 0){
        let simprocid = "calcproc-div";
        GUIConf.simproc.push(new SimulationProcess(id.includes(MenuLabels.start), 
            obj, dataname, GUIConf.simproc.length, simprocid, GUIConf.postprocessor));
        document.getElementById(simprocid).appendChild(Last(GUIConf.simproc).GetList());
    }
    else{
        skip = true;
    }
    if(skip == false){
        let outobj = GUIConf.GUIpanels[OutFileLabel].JSONObj;
        if(outobj[OutputOptionsLabel.serial[0]] >= 0){
            outobj[OutputOptionsLabel.serial[0]]++;
            GUIConf.GUIpanels[OutFileLabel].SetPanel();
        }    
    }
}

// set window title
function SetWindowTitle(filename = "", fileid = "")
{
    let title = AppName+" "+Version;
    if(filename != ""){
        GUIConf.filename = filename;
        title += " - "+filename;
    }
    if(fileid.includes(MenuLabels.loadf)){
        let items = fileid.split(IDSeparator);
        title += " / "+Last(items);
    }
    if(Framework == TauriLabel){
        TWindow.appWindow.setTitle(title);
    }
    else{
        document.title = title;
    }
}

// get calculation object and export
async function ExportCommand()
{
    let obj = GetSimulationObject();
    if(GUIConf.simproc.length > 0 && Last(GUIConf.simproc).Status() != -1){
        obj = Last(GUIConf.simproc).ExportProcesses();
    }
    if(Framework == TauriLabel){
        let id = [MenuLabels.run, MenuLabels.export].join(IDSeparator)
        let path = await GetPathDialog(
            "Open a data file to export the data.", id, false, true, false, false);
        if(path == null){
            return;
        }
        let data = FormatArray(JSON.stringify(obj, null, JSONIndent));
        window.__TAURI__.tauri.invoke("write_file", {path: path, data: data});
    }
    else{
        ExportObjects(obj, GUIConf.filename);
    }
}

// arrange process
function RunCommand(id)
{
    let obj = GetSimulationObject();
    CreateProcess(id, obj);
    if(id.includes(MenuLabels.start)){
        Last(GUIConf.simproc).Start();
    }
}

// utilities for plots -->
// arrange and create a plot object
function GetPlotObj(size, plotwindows, ispostp)
{
    let data = [];
    for(let n = 0; n < plotwindows.length; n++){
        data.push(plotwindows[n].GetData());
    }
    let plcols = 1;
    let subcols = 1;
    if(ispostp){
        plcols = GUIConf.postprocessor.GetPlotCols();
        subcols = GUIConf.postprocessor.GetSubPlotCols();    
    }
    let plobj = {data: data, cols: plcols, subcols: subcols, size:size};
    return plobj;
}

// create a new plot
function CreateNewplot(object)
{
    let size = object.size;
    if(Framework == TauriLabel){       
        let newplot = new TWindow.WebviewWindow("subwindow"+GUIConf.subwindows.toString(), {
            url:"newplot.html",
            width: size[0],
            height: size[1],
        });
        newplot.listen("ready", e => {
            newplot.emit("message", object);
        });
        GUIConf.subwindows++;
    }
    else{
        let newwin = window.open("newplot.html", "", 
        "innerWidth="+size[0]+",innerHeight="+size[1]);
        PlotObjects.windows.Put(newwin);
        PlotObjects.objects.Put(object);
    }
}

// arrange the plot size
function SetPlotSize(plotdivs = null)
{
    if(plotdivs == null){
        plotdivs = Object.keys(GUIConf.plot_aspect);
    }
    let isplotshow  = false;
    for(let j = 0; j < plotdivs.length; j++){
        if(!document.getElementById(plotdivs[j]).classList.contains("d-none")){
            isplotshow = true;
            break;
        }
    }
    if(!isplotshow){
        return;
    }
    let pwidth;
    if(document.getElementById("preproc").classList.contains("active")){
        pwidth = document.getElementById("preproc-item-div").clientWidth+10;
    }
    if(document.getElementById("postproc").classList.contains("active")){
        pwidth = document.getElementById("postproc-conf-div").clientWidth+10;
    }
    let width = document.getElementById("gui-panel").clientWidth-pwidth;

    for(let j = 0; j < plotdivs.length; j++){
        let height = Math.floor(0.5+width*GUIConf.plot_aspect[plotdivs[j]]);
        Observer[plotdivs[j]].disconnect(); // stop aspect-ratio calculation
        document.getElementById(plotdivs[j]).style.width = width.toString()+"px";
        document.getElementById(plotdivs[j]).style.height = height.toString()+"px";    
        const options = {
            attriblutes: true,
            attributeFilter: ["style"]
        };
        Observer[plotdivs[j]].observe(document.getElementById(plotdivs[j]), options); // resume 
    }
}
// <<-- utilities for plots

// initialize/terminate -->
// operation just before exit
function GatherSettings()
{    
    Settings.animinterv = AnimationInterval;
    for(const option of SettingPanels){
        if(Settings.hasOwnProperty(option)){
            Settings[option] = GUIConf.GUIpanels[option].JSONObj;
        }
    }
    Settings[SubPlotsRowLabel] = GUIConf.postprocessor.GetSubPlotCols();
    Settings[PlotWindowsRowLabel] = GUIConf.postprocessor.GetPlotCols();
}

async function BeforeExit()
{
    GatherSettings();
    const factor = await TWindow.appWindow.scaleFactor();
    let pos = await TWindow.appWindow.outerPosition();
    let size = await TWindow.appWindow.innerSize();
    pos = pos.toLogical(factor);
    size = size.toLogical(factor);
    Settings.window = {...pos, ...size};
    let data = FormatArray(JSON.stringify(Settings, null, JSONIndent));
    let conffile = await window.__TAURI__.path.join(GUIConf.wdname, ConfigFileName);
    await window.__TAURI__.tauri.invoke("write_file", { path: conffile, data: data});
    return Promise.resolve(0);
}

// load/write from local storage
function LocalStorage(issave)
{    
    if(issave){
        GatherSettings();
        let settingstr = JSON.stringify(Settings);
        localStorage["Settings"] = settingstr;
    }
    else{        
        let settingstr = localStorage["Settings"];
        if(settingstr != ""){
            try {
                let obj = JSON.parse(settingstr);    
                Settings = obj;
            }
            catch (e) {
                return;
            }
        }
    }
}

// initialize
async function Initialize()
{
    if(window.hasOwnProperty("__TAURI__")){
        Framework = TauriLabel;
        RunOS = await window.__TAURI__.os.type();
        TWindow = window.__TAURI__.window;
        if(RunOS == "Linux"){
            PlotlyScatterType = "scatter";
        }
        TWindow.appWindow.listen('tauri://close-requested', (ev) => {
            BeforeExit().then((e) => {
                window.__TAURI__.process.exit(0);
            });
        });

        window.__TAURI__.tauri.invoke("get_exepath").then(async function(exepath){
            let exedir = await window.__TAURI__.path.dirname(exepath);
            if(RunOS == "Darwin"){
                exedir = exedir.substring(0, exedir.lastIndexOf("simplex"));
            }
            if(await window.__TAURI__.tauri.invoke("change_directory", { path: exedir})){
            }
            else{
                Alert("Failed to move to the application directory.");
            }    
        });

        try {
            GUIConf.wdname = await window.__TAURI__.path.documentDir();
        } 
        catch (e) {
            GUIConf.wdname = await window.__TAURI__.path.homeDir();
        }

        await GetConfiguration();
        let winconf = CopyJSON(DefaultWindow);
        const monitor = await TWindow.currentMonitor();
        if(Settings.hasOwnProperty("window")){
            winconf = Settings.window;
            if(!winconf.hasOwnProperty("width")){
                winconf.width = DefaultWindow.width;
            } 
            if(!winconf.hasOwnProperty("height")){
                winconf.height = DefaultWindow.height;
            } 
            if(!winconf.hasOwnProperty("x")){
                winconf.x = DefaultWindow.x;
            } 
            if(!winconf.hasOwnProperty("y")){
                winconf.y = DefaultWindow.x;
            } 
            let dwidth = monitor.size.width/monitor.scaleFactor;
            let dheight = monitor.size.height/monitor.scaleFactor;
            winconf.width = Math.min(winconf.width, dwidth);
            if(winconf.x+winconf.width > dwidth){
                winconf.x = dwidth-winconf.width;
            }
            winconf.height = Math.min(winconf.height, dheight);
            if(winconf.y+winconf.height > dheight){
                winconf.y = dheight-winconf.height;
            }
        }
        try {
            await TWindow.appWindow.setSize(new TWindow.LogicalSize(winconf.width, winconf.height));
            await TWindow.appWindow.setPosition(new TWindow.LogicalPosition(winconf.x, winconf.y));
        } catch(e) {
            Alert(e);
        }
    }
    else{
        let hostname = "";
        try {
            hostname = window.location.hostname
        }
        catch (e) {
            alert("Cannot specify the hostname");
        }
        if(hostname == ""){
            Framework = BrowserLabel;
        }
        else{
            Framework = ServerLabel;
        }
    }
    SetWindowTitle();
}

// output file configuration
function SetSettingsGUI()
{
    SettingPanels.forEach(key => {
        if(!Settings.hasOwnProperty(key)){
            Settings[key] = CopyJSON(GUIConf.GUIpanels[key].JSONObj);
        }
        GUIConf.GUIpanels[key].JSONObj = Settings[key];
        GUIConf.GUIpanels[key].SetPanel();    
    })
}
// <<-- initialize/terminate

// cleanup the object
function CleanObject(obj, labels)
{
    let keys = Object.keys(labels);
    let validkeys = Array.from(keys);
    for(const key of keys){
        validkeys.push(labels[key][0]);
    }
    let exkeys = Object.keys(obj);
    for(const exkey of exkeys){
        if(!validkeys.includes(exkey)){
            delete  obj[exkey];
        }
    }
}

// Max, Min
function GetMax(data)
{
    return GetMinMax(data, true);
}

function GetMin(data)
{
    return GetMinMax(data, false);
}

function GetMinMax(data, ismax)
{
    if(data.length == 0){
        return null;
    }
    let val = data[0];
    for(let j = 1; j < data.length && ismax; j++){        
        val = val > data[j] ? val : data[j];
    }    
    for(let j = 1; j < data.length && !ismax; j++){        
        val = val < data[j] ? val : data[j];
    }    
    return val;
}

// Open File Dialog
async function GetPathDialog(
    title, id, isopen = true, isfile = true, isjson = true, ismultiple = false)
{
    let options  = {
        title: title,
        directory: !isfile,
        filters: [],
        multiple: ismultiple
    };
    if(id == [MenuLabels.file, MenuLabels.saveas].join(IDSeparator)){
        id = [MenuLabels.file, MenuLabels.open].join(IDSeparator);
    }
    if(Settings.defpaths.hasOwnProperty(id)){
        options.defaultPath = Settings.defpaths[id];
    }
    if(isjson){
        options.filters.unshift({name: "JSON Files", extensions: ["json"]})
    }
    let path;
    if(isopen){
        path = await window.__TAURI__.dialog.open(options);
    }
    else{
        path = await window.__TAURI__.dialog.save(options);
    }
    if(path != null){
        if(ismultiple){
            Settings.defpaths[id] = path[0];
        }
        else{
            Settings.defpaths[id] = path;
        }
    }
    return path;
}

// operate spinners
function SwitchSpinner(enable)
{
    let spinner = document.getElementById("spinner");
    if(!spinner){
        return;
    }
    if(enable){
        spinner.classList.remove("d-none");
    }
    else{
        spinner.classList.add("d-none");
    }
}

// boolean to judge array
function IsArrayParameter(type)
{
    return type == ArrayLabel || type == ArrayIntegerLabel || type == ArrayIncrementalLabel;
}

// create context menu
function OnRightClickData(e, id)
{
    ScanTarget = {
        category:e.category,
        item:e.item,
        jxy:e.jxy,
        isinteger:e.isinteger
    }
    let trect = e.currentTarget.getBoundingClientRect();
    let mdiv = document.getElementById(id);
    let guiwidth = document.getElementById("gui-panel").clientWidth;
    let mwidth = mdiv.clientWidth;
    let pointx = trect.x;
    let pointy = trect.y-11;
    if(pointx+mwidth > guiwidth){
        pointx = guiwidth-mwidth;
    }

    mdiv.style.top = pointy.toString()+"px";
    mdiv.style.left = pointx.toString()+"px";
    mdiv.click();
}

// export JSON objects -->
function ExportObjects(obj, dataname, format = true)
{
    if(Framework.includes("python")){
        if(obj != null){
            BufferObject = obj;
            return;    
        }
        if(BufferObject == null){
            Alert("Fatal error: cannot export object.")
            return;
        }
        obj = BufferObject;
    }

    let data = JSON.stringify(obj, null, JSONIndent);
    if(format){
        data = FormatArray(data);
    }
    let blob = new Blob([data], {type:"application/text"});
    let link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    if(Framework.includes("python")){
        link.download = "tmp.txt";
    }
    else{
        link.download = dataname;
    }
    link.click();
    link.remove();            

    if(Framework.includes("python")){
        BufferObject = null;
    }
    return dataname;
}

async function ExportAsciiData(data, id, path = "", isjson = false)
{
    // base function to export ascii data (pre-processor, post-processor)
    if(Framework == TauriLabel){
        if(path == ""){
            path = await GetPathDialog(
                "Select the file name to export the data.", id, false, true, false, false);
        }
        if(path == null){
            return;
        }
        await window.__TAURI__.tauri.invoke("write_file", {path: path, data: data});
    }
    else if(Framework == BrowserLabel || Framework == ServerLabel){
        let typestr = "application/text";
        if(isjson){
            typestr = "application/json"
        }
        let blob = new Blob([data], {type:typestr});
        let link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
        let dname = path;
        if(dname != ""){
            let sufidx = dname.lastIndexOf(".");
            if(sufidx > 0){
                dname = dname.substring(0, sufidx);
            }    
        }
        link.download = dname;
        link.click();
        link.remove();    
    }
}

async function ExportPlotWindows(id, plotwindows)
{
    let nplots = plotwindows.length;
    let path = "", ext = "";
    if(Framework == TauriLabel){
        path = await GetPathDialog("", "exportplots", false, true, false, false);
        if(path == null){
            return;
        }
        let sufidx = path.lastIndexOf(".");
        if(sufidx > 0){
            ext = path.substring(sufidx);
            path = path.substring(0, sufidx);
        }    
    }
    for(let n = 0; n < nplots; n++){
        let pathn = "";
        if(Framework == TauriLabel){
            pathn = path+ext;
            if(nplots > 1){
                pathn = path+"-"+(n+1).toString()+ext;
            }    
        }
        if(Framework == BrowserLabel || Framework == ServerLabel){
            pathn = "untitled";
            if(nplots > 1){
                pathn += "-"+(n+1).toString();
            }
        }
        plotwindows[n].ExportPlotWindow(id, pathn);
    }
}

async function SavePlotObj(plobj, dataname = "untitled")
{
    if(Framework == TauriLabel){
        let path = await GetPathDialog("Input a file name to save the plot.", 
            "saveplot", false, true, true, false);
        if(path == null){
            return;
        }
        let data = FormatArray(JSON.stringify(plobj, null, JSONIndent));
        window.__TAURI__.tauri.invoke("write_file", {path: path, data: data});
    }
    else if(Framework == BrowserLabel || Framework == ServerLabel){
        ExportObjects(plobj, dataname);
    }
}
// <-- export JSON objects

// handle path names -->
function SplitPath(pathname){
    let delim;
    if(pathname.indexOf("\\") >= 0){
        delim = "\\";
    }
    else if(pathname.indexOf("/") >= 0){
        delim = "/";
    }
    else{
        return {dir:"", name:pathname};
    }
    let items = pathname.split(delim);
    let name = items.pop();
    let dir = items.join(delim);

    return {dir:dir, name:name};
}

function GetDataPath(outfileobj)
{
    let folder = outfileobj[OutputOptionsLabel.folder[0]];
    if(folder != ""){
        let ua = window.navigator.userAgent.toLowerCase();
        if(ua.indexOf("windows") >= 0){
            folder += "\\";
        }
        else{
            folder += "/";
        }
    }
    let fname = outfileobj[OutputOptionsLabel.prefix[0]];
    if(outfileobj[OutputOptionsLabel.serial[0]] >= 0){
        fname += "-";
        fname += outfileobj[OutputOptionsLabel.serial[0]].toString();
    }
    fname += ".json";
    return folder+fname;
}

function GetDataname(datapath)
{
    let dataname = SplitPath(datapath).name;
    let sufidx = dataname.indexOf(".json");
    if(sufidx >= 0){
        dataname = dataname.substring(0, sufidx);
    }
    return dataname;
}

function GetShortPath(pathname, bef, aft){
    let orglen = pathname.length; 
    if(orglen < bef+aft){
        return pathname;
    }
    let shname = pathname.substring(0, bef)+"..."+pathname.substring(orglen-aft);
    return shname;
}

// <-- handle path names

// extract last element from array
function Last(rarray)
{
    return rarray.slice(-1)[0];
}

// dialogs -->
function Alert(msg)
{
    if(Framework == BrowserLabel || Framework == ServerLabel){
        alert(msg);
    }
    else{
        ShowDialog("Warning", true, true, msg);
    }
}

function ShowDialog(title, issmall, killcancel, msg = "", cont = null, ok = null, cancel = null)
{
    if(issmall){
        document.getElementById("modaldlg").classList.remove("modal-default");
        document.getElementById("modaldlg").classList.add("modal-sm");
    }
    else{
        document.getElementById("modaldlg").classList.remove("modal-sm");        
        document.getElementById("modaldlg").classList.add("modal-default");
    }
    if(killcancel){
        document.getElementById("modalCancel").classList.add("d-none");
    }
    else{
        document.getElementById("modalCancel").classList.remove("d-none");
    }

    document.getElementById("modalDialogLabel").innerHTML = title;
    if(msg != ""){
        if(msg.length > 40 && msg.search(/\s/) < 0){
            document.getElementById("modalDialogCont").style.overflowWrap = "anywhere";
        }
        else{
            document.getElementById("modalDialogCont").style.overflowWrap = "break-word";
        }
        document.getElementById("modalDialogCont").innerHTML = msg;
    }
    else{
        document.getElementById("modalDialogCont").innerHTML = "";
        if(cont != null){
            document.getElementById("modalDialogCont").appendChild(cont);
        }
    }
    document.getElementById("modalCancel").onclick = cancel;
    document.getElementById("modalOKsimple").onclick = ok;
    document.getElementById("showModal").click();
}

function EditDialog(id)
{
    if(id != DataUnitLabel){
        return;
    }
    let oldsettings = CopyJSON(GUIConf.GUIpanels[id].JSONObj);
    GUIConf.GUIpanels[id].SetPanel();
    ShowDialog(id, false, false, "", GUIConf.GUIpanels[id].GetTable(), null, 
    () => {
        GUIConf.GUIpanels[id].JSONObj = oldsettings;
    });
}
// <-- dialogs

// create GUI components -->
function CreateFileDialogElement(title, btnlabel, ismulti, isjson)
{
    let cont = document.createElement("div");
    cont.className = "d-flex align-items-end justify-content-between";

    if(title.length > 0){
        let tlabel = document.createElement("div");
        tlabel.innerHTML = title;
        cont.appendChild(tlabel);    
    }

    let div = document.createElement("div");
    div.className = "d-flex";

    let fileel =  document.createElement("input");
    fileel.setAttribute("type", "file");
    if(ismulti){
        fileel.setAttribute("multiple", "multiple");
    }
    if(isjson){
        fileel.setAttribute("accept", "application/json");
    }
    fileel.className = "d-none";

    let btn = document.createElement("button");
    btn.innerHTML = btnlabel;
    btn.className = "btn btn-outline-primary btn-sm";

    div.appendChild(fileel);
    div.appendChild(btn);
    cont.appendChild(div);

    return {file:fileel, button:btn, body:cont};
}

function CreateSelectBox(title, lines, ismulti, iscolumn)
{
    let div = document.createElement("div");
    if(iscolumn){
        div.className = "d-flex flex-column";
    }
    else{
        div.className = "d-flex align-items-center";
    }

    let label = document.createElement("div");        
    label.innerHTML = title;
    if(!iscolumn){
        label.className = "seltitle";
    }

    let select = document.createElement("select");
    
    select.setAttribute("size", lines.toString());
    select.multiple = ismulti;

    div.appendChild(label);
    div.appendChild(select);

    return {select:select, body:div};
}

function CreateCheckBox(title, val, id)
{
    let chkdiv = document.createElement("div");
    chkdiv.className = "form-check";
    let chkbox = document.createElement("input");
    chkbox.setAttribute("type", "checkbox");
    if(val == true){
        chkbox.setAttribute("checked", true);
    }
    chkbox.id = id;
    chkbox.className = "form-check-input";

    let label = document.createElement("label");
    label.setAttribute("for", id);
    label.innerHTML = title;
    label.className = "form-check-label";
    
    chkdiv.appendChild(chkbox);
    chkdiv.appendChild(label);

    return {div: chkdiv, chkbox: chkbox, label: label};
}

function CreateNumberInput(title, vals, id)
{
    let numdiv = document.createElement("div");
    numdiv.className = "d-flex";

    let numinput = document.createElement("input");
    numinput.setAttribute("type", "number");
    if(vals.length > 1){
        numinput.setAttribute("min", vals[1]);
    }
    if(vals.length > 2){
        numinput.setAttribute("max", vals[2]);
    }
    numinput.value = vals[0].toString();
    numinput.id = id;

    let label = document.createElement("label");
    label.setAttribute("for", id);
    label.innerHTML = title;
    label.className = "me-2";
    
    numdiv.appendChild(label);
    numdiv.appendChild(numinput);

    return {div: numdiv, input: numinput};
}
// <-- create GUI components

// operate selection box -->
function SetSelection(select, label, isvalue)
{
    let curridx = -1;
    for(let i = 0; i < select.length; i++){
        if(select.options[i].selected){
            curridx = i;
        }
        select.options[i].selected = false; 
    }
    select.selectedIndex = -1;
    for(let i = 0; i < select.length; i++){
        let item = (isvalue ? 
            select.options[i].value : select.options[i].text);
        if(Array.isArray(label) && label.includes(item)){
            select.options[i].selected = true;
        }
        else if(label == item){
            select.options[i].selected = true;
            select.selectedIndex = i;
            break;
        }
    }
    if(select.selectedIndex < 0 && curridx >= 0){
        select.options[curridx].selected = true;
        select.selectedIndex = curridx;
    }
}

function GetSelections(select)
{
    let indices = [];
    let texts = [];
    let values = [];
    for(let i = 0; i < select.length; i++){
        if(select.options[i].selected){
            indices.push(i);
            values.push(select.options[i].value);
            texts.push(select.options[i].text);
        }
    }
    return {index:indices, text:texts, value:values};
}

function AddSelection(select, value, isselect, expand = false)
{
    let option = document.createElement("option");
    option.innerHTML = value;
    option.value = value;
    if(isselect){
        option.selected = true;
    }
    select.appendChild(option);
    if(expand){
        let counts = select.length;
        for(let n = 0; n < select.children.length; n++){
            if(select.children[n].tagName == "OPTGROUP"){
                counts++;
            }
        }
        select.setAttribute("size", counts.toString());
    }
}

function DeleteSelection(select, value)
{
    let childnames = Array.from(select.childNodes).map((v) => v.value);
    let index = childnames.indexOf(value);
    if(index >= 0){
        select.removeChild(select.childNodes[index]);
    }
}

function SetSelectedItem(select, label)
{
    let curridx = -1;
    for(let i = 0; i < select.length; i++){
        if(select.options[i].selected){
            curridx = i;
        }
        select.options[i].selected = false; 
    }
    select.selectedIndex = -1;
    for(let i = 0; i < select.length; i++){
        if(label == select.options[i].value){
            select.options[i].selected = true;
            select.selectedIndex = i;
            break;
        }
    }
    if(select.selectedIndex < 0 && curridx >= 0){
        select.options[curridx].selected = true;
        select.selectedIndex = curridx;
    }
}

function EnableSelection(select, label, enable)
{
    let labels;
    if(!Array.isArray(label)){
        labels = [label];
    }
    else{
        labels = label;
    }
    for(let i = 0; i < select.length; i++){
        if(labels.includes(select.options[i].value)){
            select.options[i].disabled = !enable;
        }
    }
}

function SetSelectMenus(select, menuobj, disables, 
        selection = null, expand = false, valueobj = null, maxsize = 0)
{
    let ncounts = 0, totalsize = 0, isfound = false;
    select.selectedIndex = -1;
    select.innerHTML = "";
    for(let j = 0; j < menuobj.length; j++){
        totalsize++;
        if(typeof menuobj[j] != "object"){
            let option = document.createElement("option");
            option.innerHTML = menuobj[j];
            if(valueobj == null){
                option.value = menuobj[j];
            }
            else{
                option.value = valueobj[j];
            }
            if(menuobj[j] == selection){
                option.selected = true;
                isfound = true;
            }
            select.appendChild(option);
            if(disables.indexOf(menuobj[j]) >= 0){
                option.setAttribute("disabled", true);
            }
            continue;
        }
        let optgroup = document.createElement("optgroup");
        let grpname = Object.keys(menuobj[j]);
        optgroup.label = grpname[0];
        for(let i = 0; i < menuobj[j][grpname[0]].length; i++){
            totalsize++;
            let option = document.createElement("option");
            option.innerHTML = menuobj[j][grpname[0]][i];
            if(valueobj == null){
                option.value = menuobj[j][grpname[0]][i];
            }
            else{
                option.value = valueobj[j][grpname[0]][i];
            }
            if(menuobj[j][grpname[0]][i] == selection){
                option.selected = true;
                isfound = true;
            }
            optgroup.appendChild(option);
            ncounts++;
            if(disables.indexOf(menuobj[j][grpname[0]][i]) >= 0){
                option.setAttribute("disabled", true);
            }
        }
        select.appendChild(optgroup);
    }
    if(!isfound){
        select.selectedIndex = -1;
    }
    if(expand){
        let size = totalsize;
        if(maxsize > 0){
            size = Math.min(size, maxsize);
        }
        select.setAttribute("size", size.toString());
    }
    return ncounts;
}

function ExpandSelectMenu(select)
{
    let childs = select.childNodes;
    let size = 0;
    for(let j = 0; j < childs.length; j++){
        size += 1+childs[j].childElementCount;
    }
    select.setAttribute("size", size.toString()); 
}
// <-- operate selection box

// format strings -->
function ToPrmString(numvalr, prec) {
    if(numvalr == null){
        return "-";
    }
    if((typeof numvalr) == "undefined"){
        return "";
    }
    if(numvalr == 0){
        return numvalr;
    }

    let numexp = numvalr.toExponential().toLowerCase();
    let numchar = numexp.split('e');
//    let signif = Math.floor(numchar[0]*1.0e+5+0.5)/1.0e+5;
    let numval = parseFloat(parseFloat(numchar[0]).toPrecision(prec)+'e'+numchar[1]);
    let absval = Math.abs(numval);

    let dec = Math.floor(Math.log10(absval));
    numexp = (numvalr < 0 ? -absval : absval).toExponential().toLowerCase();
    if(numexp.length < prec+6){
        if(Math.abs(dec) > 3){
            return numexp;
        }
        return numval;
    }

    let lval;
    if(dec <= -3 || dec >= 3){
        lval = numval.toExponential(Math.max(prec, 3));
    }
    else{        
        lval = numval.toFixed(Math.max(prec, 3)-dec);
    }
    return lval;
}

function CopyJSON(obj){
    if(typeof obj == "undefined"){
        return "";
    }
    return JSON.parse(JSON.stringify(obj));
}

function FormatArray(strobj){
//return strobj;

    let idel, ist, bef, mid, newmid, aft, ichk = [0, 0, 0];
    let iend = 0;
    while((ist = strobj.indexOf("[", iend)) >= 0)
    {
        iend = strobj.indexOf("]", ist+1);
        ichk[0] = strobj.indexOf("{", ist);
        ichk[1] = strobj.indexOf("}", ist);
        ichk[2] = strobj.indexOf(":", ist);
        for(let j = 0; j < 3; j++){
            if(ichk[j] < 0){
                ichk[j] = strobj.length-1;
            }
        }
        idel = Math.min(ichk[0], ichk[1], ichk[2]);

        if(idel < iend){
            iend = ist+1;
            continue;
        }
        let itmp = iend;
        while(itmp >= 0 && itmp < idel){
            iend = itmp;
            itmp = strobj.indexOf("]", itmp+1);
        }
        bef = strobj.slice(0, ist+1);
        mid = strobj.slice(ist+1, iend);
        aft = strobj.slice(iend);
        newmid = mid.replace(/\n\s*/g, "");
        iend -= mid.length-newmid.length;
        strobj = bef+newmid+aft;
    };
    return strobj;
}
// <-- format strings 

// convert/get from/to item -->
function GetIDFromItem(categ, item, jxy)
{
    let id;
    if(jxy >= 0){
        id = [categ, item, jxy].join(IDSeparator);
    }
    else{
        id = [categ, item].join(IDSeparator);
    }
    return id;
}

function GetItemFromID(id)
{
    let categ = "", item = "", subitem = "", jxy = -1;
    if((typeof id) == "string"){
        let labels = id.split(IDSeparator);
        if(labels.length > 2){
            let xy = parseInt(labels[labels.length-1]);
            if(isNaN(xy)== false){
                jxy = xy;
            }
        }
        if(labels.length >= 2){           
            categ = labels[0];
            item = labels[1];
            if(labels.length > 3 || 
                (labels.length == 3 && jxy < 0)){
                subitem = labels[2];
            }
        }
    }
    return {categ:categ, item:item, subitem:subitem, jxy:jxy};
}

function GetIdFromCell(parent, i, j)
{
    return parent+"/"+i+"/"+j;
}

function GetCellFromId(parent, id)
{
    let cell = id.split("/");
    return [parseInt(cell[1]), parseInt(cell[2])];
}

function GetPanelID(id)
{
    let index = id.indexOf("-tab");
    return id.slice(0, index);
}
// <-- convert/get from/to item

// plot-related functions -->
function GetPlotPanelSize(id)
{
    let ppdiv = document.getElementById(id);
    let size = [ppdiv.style.width, ppdiv.style.height];
    for(let j = 0; j < 2; j++){
        let idx = size[j].indexOf("px");
        size[j] = size[j].substring(0, idx);
        size[j] = parseInt(size[j])+7
        // 7 = 14 (font sie) * 0.5 (m-2)
    }
    return size;
}

function ConvertGreek(input, tocode)
{
    let chars = [
        "&Alpha;","&Beta;","&Gamma;","&Delta;","&Epsilon;","&Zeta;","&Eta;","&Theta;","&Iota;","&Kappa;","&Lambda;","&Mu;","&Nu;","&Xi;","&Omicron;","&Pi;","&Rho;","&Sigma;","&Tau;","&Upsilon;","&Phi;","&Chi;","&Psi;","&Omega;","&alpha;","&beta;","&gamma;","&delta;","&epsilon;","&zeta;","&eta;","&theta;","&iota;","&kappa;","&lambda;","&mu;","&nu;","&xi;","&omicron;","&pi;","&rho;","&sigmaf;","&sigma;","&tau;","&upsilon;","&phi;","&chi;","&psi;","&omega;","&thetasym;","&upsih;","&piv;"
    ];
    let codes = [
        "&#913;","&#914;","&#915;","&#916;","&#917;","&#918;","&#919;","&#920;","&#921;","&#922;","&#923;","&#924;","&#925;","&#926;","&#927;","&#928;","&#929;","&#931;","&#932;","&#933;","&#934;","&#935;","&#936;","&#937;","&#945;","&#946;","&#947;","&#948;","&#949;","&#950;","&#951;","&#952;","&#953;","&#954;","&#955;","&#956;","&#957;","&#958;","&#959;","&#960;","&#961;","&#962;","&#963;","&#964;","&#965;","&#966;","&#967;","&#968;","&#969;","&#977;","&#978;","&#982;"
    ];

    let org, dest;
    if(tocode){
        org = chars;
        dest = codes;
    }
    else{
        org = codes;
        dest = chars;
    }

    let ret = input;
    for(let n = 0; n < org.length; n++){
        if(ret.indexOf(org[n]) >= 0){
            ret = ret.replaceAll(org[n], dest[n]);
        }
    }
    return ret;
}

function GetSceneName(i)
{
    return (i == 0 ? "scene" : "scene"+(i+1).toString());
}

function GetAsciiData1D(plobj)
{
    let objs = plobj.data;
    let nplots = objs.length;
    let xarrays = [];
    let legends = [];
    for(let n = 0; n < nplots; n++){
        xarrays.push(objs[n].x);
        if(objs[n].hasOwnProperty("name")){
            legends.push("\""+objs[n].name+"\"");
        }
        else{
            legends.push("-");
        }
    }
    let xidx = [0];
    let xarrr = [xarrays[0]];
    for(let n = 1; n < nplots; n++){
        let xastrn = JSON.stringify(xarrays[n]);
        let mf = -1;
        for(let m = 0; m < n; m++){
            let xastrm = JSON.stringify(xarrays[m]);
            if(xastrn == xastrm){
                mf = m;
                break;
            }
        }
        if(mf >= 0){
            xidx.push(xidx[mf]);
        }
        else{
            xidx.push(xarrr.length);
            xarrr.push(xarrays[n]);
        }
    }
    let xtitle = plobj.layout.xaxis.title.text;
    let ytitle = plobj.layout.yaxis.title.text;

    let yindices = [];
    for(let n = 0; n < xarrr.length; n++){
        yindices.push([]);
    }
    for(let n = 0; n < nplots; n++){
        yindices[xidx[n]].push(n);
    }
    let titles = [];
    let ndata = 0;
    for(let j = 0; j < xarrr.length; j++){
        if(xarrr[j].length > ndata){
            ndata = xarrr[j].length;
        }
        titles.push("\""+xtitle+"\"");
        if(nplots == 1){
            titles.push("\""+ytitle+"\"");
        }
        else{
            for(let i = 0; i < yindices[j].length; i++){
                titles.push(legends[yindices[j][i]]);
            }       
        }
    }

    let lineval = [], values = [ConvertGreek(titles.join("\t"), false)];
    lineval.length = titles.length;
    for(let n = 0; n < ndata; n++){
        let jt = -1;
        for(let j = 0; j < xarrr.length; j++){
            jt++;
            if(xarrr[j].length <= n){
                lineval[jt] = "-";
            }
            else{
                lineval[jt] = xarrr[j][n].toExponential(5);
            }
            for(let i = 0; i < yindices[j].length; i++){
                jt++;
                if(xarrr[j].length <= n){
                    lineval[jt] = "-";
                }
                else{
                    lineval[jt] = objs[yindices[j][i]].y[n].toExponential(5);
                }
            }       
        }
        values.push(lineval.join("\t"));
    }
    let data = values.join("\n");
    return data;
}

function GetAsciiData2D(plobj)
{
    let objs = plobj.data;
    let nplots = objs.length;

    let xarrays = [], yarrays = [], zarrays = [];
    let xtitles = [], ytitles = [], ztitles = [];

    for(let n = 0; n < nplots; n++){
        if(objs[n].type == "scatter3d"){
            continue;
        }
        else if(objs[n].type == "mesh3d"){
            let xg = [], yg = [], zg = [];
            Convert2DFormat(objs[n].x, objs[n].y, objs[n].z, xg, yg, zg, true);
            xarrays.push(xg);
            yarrays.push(yg);
            zarrays.push(zg);
        }
        else{
            xarrays.push(objs[n].x);
            yarrays.push(objs[n].y);
            zarrays.push(objs[n].z);    
        }
        if(objs[n].type == "heatmap"){
            xtitles.push(plobj.layout.xaxis.title.text);
            ytitles.push(plobj.layout.yaxis.title.text);    
        }
        else{
            xtitles.push(plobj.layout.scene.xaxis.title.text);
            ytitles.push(plobj.layout.scene.yaxis.title.text);
        }
    }
    if(nplots == 1){
        if(objs[0].type == "heatmap"){
            ztitles.push(objs[0].colorbar.title.text);
        }
        else{
            ztitles.push(plobj.layout.scene.zaxis.title.text);
        }
    }
    else{
        for(let n = 0; n < nplots; n++){
            if(objs[n].type == "scatter3d"){
                continue;
            }
            if(plobj.layout.hasOwnProperty("annotations")){
                ztitles.push(plobj.layout.annotations[ztitles.length].text);
            }
            else{
                let scn = GetSceneName(n);
                ztitles.push(plobj.layout[scn].zaxis.title.text);
            }
        }
    }

    let nexport = xarrays.length;
    let isxy = new Array(nexport);
    isxy[0] = true;
    let xstr = JSON.stringify(xarrays[0]);
    let ystr = JSON.stringify(yarrays[0]);
    for(let n = 1; n < nexport; n++){
        let xstrn = JSON.stringify(xarrays[n]);
        let ystrn = JSON.stringify(yarrays[n]);
        isxy[n] = xstrn != xstr || ystrn != ystr;
        xstr = xstrn; ystr = ystrn;
    }

    let titles = ["\""+xtitles[0]+"\"", "\""+ytitles[0]+"\"", "\""+ztitles[0]+"\""];
    let nlinesmax = xarrays[0].length*yarrays[0].length;
    for(let n = 1; n < nexport; n++){
        if(isxy[n]){
            titles.push("\""+xtitles[n]+"\"");
            titles.push("\""+ytitles[n]+"\"");
        }
        titles.push("\""+ztitles[n]+"\"");
        nlinesmax = Math.max(nlinesmax, xarrays[n].length*yarrays[n].length);
    }
    let values = [ConvertGreek(titles.join("\t"), false)];

    for(let m = 0; m < nlinesmax; m++){
        let lineval = [];
        for(let n = 0; n < nexport; n++){
            let nx = m%xarrays[n].length;
            let ny = Math.floor(m/xarrays[n].length);
            if(isxy[n]){
                if(m >= xarrays[n].length*yarrays[n].length){
                    lineval.push("-");
                    lineval.push("-");
                }
                else{
                    lineval.push(xarrays[n][nx].toExponential(5));
                    lineval.push(yarrays[n][ny].toExponential(5));
                }
            }           
            if(m >= xarrays[n].length*yarrays[n].length){
                lineval.push("-");
            }
            else{
                lineval.push(zarrays[n][ny][nx].toExponential(5));
            }
        }
        values.push(lineval.join("\t"));
    }

    let data = values.join("\n");
    return data;
}
 
function GetAsciiData(dim, plobj)
{
    let data;
    if(dim == 2){
        data = GetAsciiData2D(plobj);
    }
    else{
        data = GetAsciiData1D(plobj);
    }
    return data;
}

function GetPlotConfig0D(obj, ytitles, mode = "lines")
{
    let yindices = [];
    for(let i = 0; i < ytitles.length; i++){
        let yindex = obj.titles.indexOf(ytitles[i]);
        if(yindex < 0){
            return null;
        }
        yindices.push(yindex);
    }
    let xdata = [];
    for(let i = 0; i < obj.data[yindices[0]].length; i++){
        xdata.push(i+1);
    }
    let data = [];
    for(let i = 0; i < ytitles.length; i++){
        data.push(
            {
                x: xdata,
                y: obj.data[yindices[i]],
                type: PlotlyScatterType,
                name: ConvertGreek(ytitles[i], true),
                mode: mode
            }
        )
    }
    return data;
}

function GetPlotConfig1D(obj, xtitle, ytitles, legends, mode = "lines")
{
    let xindex = obj.titles.indexOf(xtitle);
    if(xindex < 0){
        return null;
    }
    let yindices = [];
    for(let i = 0; i < ytitles.length; i++){
        let yindex = obj.titles.indexOf(ytitles[i]);
        if(yindex < 0){
            return null;
        }
        yindices.push(yindex);
    }
    let data = [];
    for(let i = 0; i < ytitles.length; i++){
        data.push(
            {
                x: obj.data[xindex],
                y: obj.data[yindices[i]],
                type: PlotlyScatterType,
                name: ConvertGreek(i >= legends.length ? ytitles[i] : legends[i], true),
                mode: mode
            }
        )
    }
    return data;
}

function GetLayout1D(axtitles, ranges, logranges, xyscale)
{
    let defaxis = {
            ticks:"inside", zeroline:false, type:"linear",
            showline:true, mirror:true, exponentformat:"power"};
    let xaxis = CopyJSON(defaxis);
    let yaxis = CopyJSON(defaxis);
    xaxis.title = {text:ConvertGreek(axtitles[0], true)};
    yaxis.title = {text:ConvertGreek(axtitles[1], true)};

    if(xyscale != null){
        xaxis.type = xyscale[0];
        yaxis.type = xyscale[1];
    }
    if(xaxis.type == "log"){
        xaxis.range = logranges[0];
    }
    else{
        if(ranges != null){
            xaxis.range = ranges[0];
        }    
    }
    if(yaxis.type == "log"){
        yaxis.range = logranges[1];
    }
    else{
        if(ranges != null){
            yaxis.range = ranges[1];
        }    
    }

    let legend, margin;
    legend = {x:0.02, y:0.98};
    margin = CopyJSON(PlotlyPrms.margin1d);
    let layout = {
        showlegend:true, 
        autosize:true,
        legend:legend,
        margin:margin,
        xaxis:xaxis,
        yaxis:yaxis,
        hovermode:"closest"
    };
    layout.font = PlotlyFont;
    return layout;
}

function AddAnnotations(layout, issurface, nplots, titles)
{
    layout.annotations = []
    let frac, colrows = [0, 0], dg = [0, 0], xy = [0, 0], Dxy = [0, 0], xyini = [0, 0];
    if(issurface){
        frac = [0.5, 0.95];
    }
    else{
        colrows[0] = layout.grid.columns;
        colrows[1] = layout.grid.rows;
        dg[0] = layout.grid.xgap;
        dg[1] = layout.grid.ygap;
        for(let j = 0; j < 2; j++){
            Dxy[j] = 1/(colrows[j]+dg[j]*(colrows[j]-1))*(-1)**j*(1+dg[j]);
        }
        xyini[0] = 0.01;
        xyini[1] = 0.99;
    }
   
    let xanchor = issurface ? "center" : "left";
    let color = issurface ? "rgb(0,0,0)" : "rgb(255,255,255)";
    for(let n = 0; n < Math.min(nplots, titles.length); n++){
        if(issurface){
            let xyr = [layout[GetSceneName(n)].domain.x, layout[GetSceneName(n)].domain.y];
            for(let j = 0; j < 2; j++){
                xy[j] = xyr[j][0]*(1-frac[j])+xyr[j][1]*frac[j];
            }                        
        }
        else{
            let nxy = [n%colrows[0], Math.floor(n/colrows[0])];
            for(let j = 0; j < 2; j++){
                xy[j] = xyini[j]+nxy[j]*Dxy[j];
            }
        }
        layout.annotations.push({
            x:xy[0], 
            y:xy[1],
            xref:"paper",
            yref:"paper",
            xanchor: xanchor,
            yanchor: "top",
            text: titles[n], 
            showarrow: false, 
            font:{size:16, color:color}
        });
    }
}

function GetLayout2D(nplots, iscontour, xytitles, ztitles, xyranges, zrange, cols = null)
{
    let rows;
    if(cols == null){
        if(nplots == 1){
            rows = cols = 1;
        }
        else if(nplots == 2){
            rows = 1;
            cols = 2;
        }
        else if(nplots == 3){
            rows = 1;
            cols = 3;
        }
        else{
            rows = Math.ceil(Math.sqrt(nplots));
            cols = rows-1;
            while(rows*cols < nplots){
                cols++;
            }
        }    
    }
    else{
        rows = 1;
        while(rows*cols < nplots){
            rows++;
        }
    }

    let layout;
    if(iscontour){
        let dx = 0.01;
        let dy = 0.01;

        layout = 
            {
                grid:
                {
                    rows:rows, 
                    columns:cols, 
                    pattern:"independent",
                    xgap:dx,
                    ygap:dy
                },
                xaxis:{title:{text:ConvertGreek(xytitles[0], true)}},
                yaxis:{title:{text:ConvertGreek(xytitles[1], true)}}
            };

        for(let i = 1; i < nplots; i++){
            let xlabel = "xaxis"+(i+1).toString();
            let ylabel = "yaxis"+(i+1).toString();
            layout[xlabel] = {title:{text:ConvertGreek(xytitles[0], true)}};
            layout[ylabel] = {title:{text:ConvertGreek(xytitles[1], true)}};
        }
        for(let i = 0; i < nplots; i++){
            let xlabel = "xaxis";
            let ylabel = "yaxis";
            if(i > 0){
                xlabel += (i+1).toString();
                ylabel += (i+1).toString();
            }
            let nx = i%cols;
            let ny = Math.floor(i/cols);
            if(nx != 0){
                delete layout[ylabel].title;
                layout[ylabel].showticklabels = false;
            }
            if(ny != rows-1){
                delete layout[xlabel].title;
                layout[xlabel].showticklabels = false;
            }
            if(xyranges != null){
                layout[xlabel].range = Array.from(xyranges[0]);
                layout[ylabel].range = Array.from(xyranges[1]);
            }    
        }

        layout.margin = CopyJSON(PlotlyPrms.margin1d);    
    }
    else{
        let scenes = [];
        let domains = [];
        let serno = 0;
        for(let m = 0; m < rows; m++){
            let ypos = [1.0-(m+1.0)/rows, 1.0-m/rows];
            if(rows > 1){
                ypos[0] += 1/rows*0.01;
                ypos[1] -= 1/rows*0.01;
            }
            for(let n = 0; n < cols; n++){
                let xpos = [n/cols, (n+1.0)/cols];
                if(cols > 1){
                    xpos[0] += 1/cols*0.01;
                    xpos[1] -= 1/cols*0.01;
                }
                    scenes.push(GetSceneName(serno++));
                let scnobj = {domain:{x:xpos, y:ypos}};         
                scnobj.xaxis = {title:{text:ConvertGreek(xytitles[0], true)}};
                scnobj.yaxis = {title:{text:ConvertGreek(xytitles[1], true)}};
                scnobj.zaxis = {tickformat: ".2g", title:{text:ConvertGreek(ztitles[serno-1], true)}};
                if(zrange != null){
                    scnobj.zaxis.range = Array.from(zrange);
                }
                scnobj.aspectratio = {x:1, y:1, z:1};
                scnobj.camera = CopyJSON(PlotlyPrms.camera);
                // default: 1.25, slightly going away

                domains.push(scnobj);
                if(scenes.length == nplots){
                    break;
                }
            }
            if(scenes.length == nplots){
                break;
            }
        }
        layout = {};
        for(let i = 0; i < nplots; i++){
            layout[scenes[i]] = domains[i];
        }
        layout.margin = CopyJSON(PlotlyPrms.margin2d);    
    }
    if(zrange != null){
        layout.zaxis = {range: Array.from(zrange)};
    }

    layout.font = PlotlyFont;
    return layout;
}

function GetPlotConfig2D(obj, titles, axtitles, config, isdata2d)
{
    let xindex = obj[0].titles.indexOf(titles[0]);
    if(xindex < 0){
        return null;
    }
    let yindex = obj[0].titles.indexOf(titles[1]);
    if(yindex < 0){
        return null;
    }
    let nobjs = obj.length;
    let nplots = (titles.length-2)*nobjs;
    let zindices = [];
    for(let i = 0; i < nplots; i++){
        let objidx = i%nobjs;
        let tidx = Math.floor(i/nobjs);
        let zindex = obj[objidx].titles.indexOf(titles[tidx+2]);
        if(zindex < 0){
            return null;
        }
        zindices.push(zindex);
    }
    
    let layout = {
        "surface": GetLayout2D(nplots, false, axtitles, axtitles.slice(2), null, null),
        "heatmap": GetLayout2D(nplots, true, axtitles, axtitles.slice(2), null, null)
    };

    let data = [];
    for(let i = 0; i < nplots; i++){
        let objidx = i%nobjs;

        let zdata = [];
        if(isdata2d){
            zdata = obj[objidx].data[zindices[i]];
        }
        else{
            let mesh = [obj[objidx].data[xindex].length, obj[objidx].data[yindex].length];
            for(let ny = 0; ny < mesh[1]; ny++){
                let mvdidx = GetIndexMDV(mesh, [0, ny], 2);
                zdata.push(obj[objidx].data[zindices[i]].slice(mvdidx, mvdidx+mesh[0]));
            }
        }
        Set2DPlotObjects(obj[objidx].data[xindex], obj[objidx].data[yindex], zdata, null, config, i, nplots, data, axtitles[i+2]);
    }
    return {data:data, layout:layout, nplots:nplots};
}

function Get1DLength(xdata)
{
    let nx = 1;
    while(nx < xdata.length && xdata[nx] != xdata[0]){
        nx++;
    }
    return nx;
}

function Convert2DFormat(xdata, ydata, zdata, xg, yg, zg, tosurface)
{
    let nx, ny;
    if(tosurface){
        nx = Get1DLength(xdata);
        ny = xdata.length/nx;

        xg.length = nx;
        for(let n = 0; n < nx; n++){
            xg[n] = xdata[n];
        }
        yg.length = ny;
        for(let n = 0; n < ny; n++){
            yg[n] = ydata[n*nx];
        }
        zg.length = ny;
        for(let n = 0; n < ny; n++){
            zg[n] = new Array(nx);
            for(let m = 0; m < nx; m++){
                zg[n][m] = zdata[n*nx+m];
            }                
        }
    }
    else{
        nx = xdata.length;
        ny = ydata.length;
        xg.length = nx*ny;
        yg.length = nx*ny;
        zg.length = nx*ny;
        for(let n = 0; n < nx*ny; n++){
            let ix = n%nx;
            let iy = Math.floor(n/nx);
            xg[n] = xdata[ix];
            yg[n] = ydata[iy];
            zg[n] = zdata[iy][ix];
        }
    }
    return [nx, ny];
}

function Set2DPlotObjects(xdata, ydata, zdata, zranges, config, index, nplots, data, ztitle, dataorg = null)
{
    let sglobj, xg = [], yg = [], zg = [], isdefault = true;
    let nxy = [0, 0];
    if(dataorg != null){
        isdefault = dataorg.type == "surface" || dataorg.type == "heatmap";
    }
    if(isdefault){
        if(config.typepl == "surface" || config.typepl == "heatmap"){
            xg = xdata;
            yg = ydata;
            zg = zdata;
            nxy = [xdata.length, ydata.length];
        }
        else{
            nxy = Convert2DFormat(xdata, ydata, zdata, xg, yg, zg, false);
        }    
    }
    else{
        if(config.typepl == "mesh3d"){
            nxy[0] = Get1DLength(xdata);
            nxy[1] = xdata.length/nxy[0];
            xg = xdata;
            yg = ydata;
            zg = zdata;
        }
        else{
            nxy = Convert2DFormat(xdata, ydata, zdata, xg, yg, zg, true);
        }    
    }
    let clbar = CopyJSON(PlotlyPrms.colorbar);
    if(dataorg != null && dataorg.hasOwnProperty("colorbar")){
        clbar = CopyJSON(dataorg.colorbar);
    }
    else{
        clbar.title = {text: ztitle};
    }
    sglobj = 
    {
        x: xg,
        y: yg,
        z: zg,
        type: config.typepl,
        zsmooth: "best",
        scene:GetSceneName(index),
        showscale: nplots==1?config.showscale:false,
        colorbar: clbar,
        colorscale: config.colorscale,
        color: config.color
    };
    if(zranges != null){
        sglobj.zmin = zranges[0];
        sglobj.zmax = zranges[1];
    }
    if(index > 0){
        sglobj.xaxis = "x"+(index+1).toString();
        sglobj.yaxis = "y"+(index+1).toString();
    }

    let ig = [], jg = [], kg = [];
    if(config.typepl == "mesh3d"){
        for(let n = 0; n < nxy[1]-1; n++){
            for(let m = 0; m < nxy[0]-1; m++){
                ig.push(n*nxy[0]+m);
                jg.push(n*nxy[0]+m+1)
                kg.push((n+1)*nxy[0]+m+1);   
                ig.push(n*nxy[0]+m);
                jg.push((n+1)*nxy[0]+m+1);            
                kg.push((n+1)*nxy[0]+m)
            }    
        }
        sglobj.i = ig;
        sglobj.j = jg;
        sglobj.k = kg;
    }
    
    data.push(sglobj);

    if(!config.wireframe || config.typepl == "heatmap"){
        return;
    }

    if(!isdefault && config.typepl == "mesh3d"){
        xg = []; yg = []; zg = [];
        nxy = Convert2DFormat(xdata, ydata, zdata, xg, yg, zg, true);
    }
    else{
        xg = xdata;
        yg = ydata;
        zg = zdata;
    }

    for(let j = 0; j < 2; j++){
        let xv = [], yv = [], zv = [], ixy = [0, 0];
        while(ixy[j] < nxy[j]) {
            for(let n = 0; n < nxy[1-j]; n++){
                ixy[1-j] = ixy[j]%2 > 0 ? nxy[1-j]-1-n : n;
                xv.push(xg[ixy[0]]);
                yv.push(yg[ixy[1]]);
                zv.push(zg[ixy[1]][ixy[0]]);
            }
            ixy[j]++
        };    
        sglobj = 
        {
            x: xv,
            y: yv,
            z: zv,
            type: "scatter3d",
            mode: "lines",
            scene:GetSceneName(index),
            line: {
                width: 1.5,
                color: "rgb(0,0,0)"
            },
            showlegend: false
        };
        if(index > 0){
            sglobj.xaxis = "x"+(index+1).toString();
            sglobj.yaxis = "y"+(index+1).toString();
        }
        data.push(sglobj);
    }
}

function GetIndexMDV(mesh, n, dim)
{
	let index = n[dim-1];
	for(let nd = dim-2; nd >= 0; nd--){
		index = index*mesh[nd]+n[nd];
	}
	return index;
}

function ConvertPow2Super(unit)
{
    let cunit = unit.replace(/\^2/g, "<sup>2</sup>");
    return cunit.replace(/\^3/g, "<sup>3</sup>");
}

function GetLogRange(vmin, vmax, coef){
    if(vmax < 0){
        return[-1, 1];
    }
    let rmax = Math.log10(vmax*coef), rmin;
    if(vmin < 0){
        rmin = Math.log10(vmax*1.0e-6);
    }
    else{
        rmin = Math.max(Math.log10(vmin/coef), rmax-10);
    }
    return [rmin, rmax];
}
// <-- plot-related functions

// functions for loading files -->
async function LoadFiles(e, func)
{
    SwitchSpinner(true);
    let nfiles = e.currentTarget.files.length;
    let files = e.currentTarget.files;
    let promise = [];
    for(let n = 0; n < nfiles; n++){
        promise.push(LoadSingleFile(files[n]));
    }
    let objs = await Promise.all(promise);
    for(let n = 0; n < nfiles; n++){
        await func(objs[n].data, objs[n].name, n == nfiles-1);
    }
    SwitchSpinner(false);
}

function LoadSingleFile(file)
{
    return new Promise(function(resolve) 
    {
        var fileReader = new FileReader();   
        fileReader.onload = () =>
        {   
           resolve({data: fileReader.result, name:file.name});
        }
        fileReader.readAsText(file);     
    });
}
// <-- functions for loading files

// numerical functions -->
function GetParabolicSingle(xarr, yarr, x)
{
    let sum;
	sum  = (x-xarr[1])/(xarr[0]-xarr[1])*(x-xarr[2])/(xarr[0]-xarr[2])*yarr[0];
	sum += (x-xarr[2])/(xarr[1]-xarr[2])*(x-xarr[0])/(xarr[1]-xarr[0])*yarr[1];
	sum += (x-xarr[0])/(xarr[2]-xarr[0])*(x-xarr[1])/(xarr[2]-xarr[1])*yarr[2];
    return sum;
}

function GetParabolic(xv, yv, x)
{
	let xarr = [], yarr = [];
	let index = Math.min(xv.length-3, SearchIndex(xv, x));	

	for(let n = 0; n < 3; n++){
		xarr.push(xv[n+index]);
		yarr.push(yv[n+index]);
	}
    return GetParabolicSingle(xarr, yarr, x);
}

function ParabloicPeak(x0, x1, x2, f0, f1, f2)
{
    let a, b, peak = {};

    a = f0/(x0-x1)/(x0-x2)+f1/(x1-x0)/(x1-x2)+f2/(x2-x1)/(x2-x0);
    b = -(x1+x2)*f0/(x0-x1)/(x0-x2)-(x0+x2)*f1/(x1-x0)/(x1-x2)-(x1+x0)*f2/(x2-x1)/(x2-x0);
    if(a == 0.0){
        peak.x = x1;
        peak.y = f1;
    }
    else{
        peak.x = -b/2.0/a;
        peak.y = GetParabolicSingle([x0, x1, x2], [f0, f1, f2], peak.x);
    }
    return peak;
}

function GetParabolicPeak(x, y, peak, init, ihist)
{
    let i = init, j;
    let flag = false;

    while(i+2 < x.length){
        if((y[i]-y[i+1])*(y[i+1]-y[i+2]) < 0.0 ||
                (y[i] == y[i+1] && y[i+1] != y[i+2])){
            flag =  true;
            for(j = i+1; j >= i-ihist && j > 2; j--){
                if((y[j]-y[j-1])*(y[j-1]-y[j-2]) < 0.0){
                    flag = false;
                    break;
                }
            }
            for(j = i+1; flag && j <= i+ihist && j+2 < x.length; j++){
                if((y[j]-y[j+1])*(y[j+1]-y[j+2]) < 0.0){
                    flag = false;
                    break;
                }
            }
            if(flag){
                break;
            }
        }
        i++;
    }
    if(!flag) return -1;
    let pkobj = ParabloicPeak(x[i], x[i+1], x[i+2], y[i], y[i+1], y[i+2]);
    peak.x = pkobj.x;
    peak.y = pkobj.y;
    return i+1;
}

function SolveParabolic(xv, yv, y)
{
	let xarr = [], yarr = [], a = 0, b = 0, c;
	let index = Math.min(xv.length-3, SearchIndex(yv, y));

	for(let n = 0; n < 3; n++){
		xarr.push(xv[n+index]);
		yarr.push(yv[n+index]);
    }
    
    let ia = [1,2,0], ib = [2,0,1], dx = [];
    for(let i = 0; i < 3; i++){
        dx.push(xarr[ia[i]]-xarr[ib[i]]);
    }
    c = dx[0]*dx[1]*dx[2]*y;
    for(let i = 0; i < 3; i++){
        a += dx[i]*yarr[i];
        b -= (xarr[ia[i]]**2-xarr[ib[i]]**2)*yarr[i];
        c += xarr[ia[i]]*xarr[ib[i]]*(xarr[ia[i]]-xarr[ib[i]])*yarr[i];
    }

    let D = b**2-4*a*c;
    if(D < 0 || a == 0){
        return NaN;
    }
    let Dsqrt = Math.sqrt(D);

    let x1 = (-b+Dsqrt)/2/a;
    let x2 = (-b-Dsqrt)/2/a;
    if(Math.abs(x1-xarr[1]) < Math.abs(x2-xarr[1])){
        return x1;
    }
    return x2;
}

function Integrate(z, Bxy, coef, iscorr)
{
    let npoints = z.length;
    let items = Bxy.length;
    let zmid, bmid, nt;
    let zarr = new Array(3);
    let barr = [];
    let Ixy = [];

    for(let j = 0; j < items; j++){
        barr.push(new Array(3));
        Ixy.push(new Array(npoints));
        Ixy[j][0] = 0;
    }
    for(let n = 1; n < npoints; n++){
        zmid = (z[n-1]+z[n])*0.5;
        if(n == npoints-1){
            nt = n-2;
        }
        else{
            nt = n-1;
        }
        for(let na = 0; na < 3; na++){
            zarr[na] = z[nt+na];
            for(let j = 0; j < items; j++){
                barr[j][na] = Bxy[j][nt+na];
            }
        }
        for(let j = 0; j < items; j++){
            bmid = GetParabolicSingle(zarr, barr[j], zmid);
            Ixy[j][n] = Ixy[j][n-1]+
                coef*(Bxy[j][n-1]+bmid*4.0+Bxy[j][n])/6.0*(z[n]-z[n-1]);
        }
    }
    if(iscorr){
        let zrange = z[npoints-1]-z[0];
        let Islope = [0, 0], Ioffset = [0, 0];
        for(let j = 0; j < 2; j++){
            Islope[j] = Ixy[j][npoints-1]/zrange;
        }
        for(let n = 1; n < npoints; n++){
            for(let j = 0; j < 2; j++){
                Ixy[j][n] -= Islope[j]*(z[n]-z[0]);
                Ioffset[j] += Ixy[j][n];
            }    
        }
        for(let j = 0; j < 2; j++){
            Ioffset[j] /= npoints-1;
            for(let n = 0; n < npoints; n++){
                Ixy[j][n] -= Ioffset[j];
            }
        }
    }
    return Ixy;
}

function SearchIndex(xarr, x)
{
    let km, kp, k, n = xarr.length;

    km = 0;
    kp = n-1;
    while (kp-km > 1){
        k = (kp+km) >> 1;
        if((xarr[0] < xarr[1] && xarr[k] > x)
            || (xarr[0] > xarr[1] && xarr[k] < x)){
            kp = k;
        }
        else{
            km = k;
        }
    }
    return km;
}

function BesselJ1(x)
{
    let ax, z, xx, y, ans, ans1, ans2;

    if((ax = Math.abs(x)) < 8.0){
        y = x*x;
        ans1=x*(72362614232.0+y*(-7895059235.0+y*(242396853.1
                +y*(-2972611.439+y*(15704.48260+y*(-30.16036606))))));
        ans2=144725228442.0+y*(2300535178.0+y*(18583304.74
                +y*(99447.43394+y*(376.9991397+y*1.0))));
        ans=ans1/ans2;
    }
    else {
        z = 8.0/ax;
        y = z*z;
        xx = ax-2.356194491;
        ans1 = 1.0+y*(0.183105e-2+y*(-0.3516396496e-4
                +y*(0.2457520174e-5+y*(-0.240337019e-6))));
        ans2 = 0.04687499995+y*(-0.2002690873e-3
                +y*(0.8449199096e-5+y*(-0.88228987e-6
                +y*0.105787412e-6)));
        ans = Math.sqrt(0.636619772/ax)*(Math.cos(xx)*ans1-z*Math.sin(xx)*ans2);
        if (x < 0.0) ans = -ans;
    }
    return ans;
}

function BesselJ0(x)
{
    let ax, z, xx, y, ans, ans1, ans2;

    if((ax = Math.abs(x)) < 8.0){
        y = x*x;
        ans1 = 57568490574.0+y*(-13362590354.0+y*(651619640.7
            +y*(-11214424.18+y*(77392.33017+y*(-184.9052456)))));
        ans2 = 57568490411.0+y*(1029532985.0+y*(9494680.718
            +y*(59272.64853+y*(267.8532712+y*1.0))));
        ans = ans1/ans2;
    }
    else{
        z = 8.0/ax;
        y = z*z;
        xx = ax-0.785398164;
        ans1 = 1.0+y*(-0.1098628627e-2+y*(0.2734510407e-4
                +y*(-0.2073370639e-5+y*0.2093887211e-6)));
        ans2 = -0.1562499995e-1+y*(0.1430488765e-3
                +y*(-0.6911147651e-5+y*(0.7621095161e-6
                -y*0.934935152e-7)));
        ans = Math.sqrt(0.636619772/ax)*(Math.cos(xx)*ans1-z*Math.sin(xx)*ans2);
    }
    return ans;
}
// <-- numerical functions

// create menu commands -->
function SetMenuItems(list, id)
{
    let tmp = CopyJSON(list);
    tmp.forEach(element => {
        if(id.length > 0){
            element.id = GetIDFromItem(id, element.label, -1);
        }
        else{
            element.id = element.label;
        }
        if(element.hasOwnProperty("submenu")){
            element.submenu = SetMenuItems(element.submenu, element.id);
        }
        if(!element.hasOwnProperty("type")){
            element.type = "item";
        }
    });
    return tmp;
}

function CreateMenuList(list, parent, insel = null, runids = [])
{
    if(list.length < 1){
        return [];
    }
    let ids = [];
    let menutype = [];
    list.forEach(element => {
        let menuitem =  document.createElement("li");
        let skip = false;
        if(element.type == "separator"){
            if(menutype.length > 0){
                if(menutype[menutype.length-1] == "separator"){
                    skip = true;
                }
            }            
            menuitem.className = "dropdown-divider";
        }
        else if(element.hasOwnProperty("submenu")){
            menuitem.className = "dropend";
            ids.push(element.id);
            let label = document.createElement("div");
            label.className = "dropdown-toggle";
            label.setAttribute("data-bs-toggle", "dropdown");
            label.innerHTML = element.label;
            menuitem.appendChild(label);
            let ulp = document.createElement("ul");
            ulp.className = "dropdown-menu";
            ulp.id = element.id;
            menuitem.appendChild(ulp);
            let subids = CreateMenuList(element.submenu, ulp, insel, runids);
            ids = ids.concat(subids);
        }
        else if(element.hasOwnProperty("label")){
            let menubtn = document.createElement("button");
            menubtn.className = "dropdown-item";
            menubtn.innerHTML = element.label;
            if(element.label == insel){
                menubtn.classList.add("fw-bold");
            }
            menubtn.id = element.id;
            menubtn.addEventListener("click", (ev) => {MenuCommand(ev.currentTarget.id);});
            menuitem.appendChild(menubtn);
            ids.push(element.id);
            runids.push(element.id);
        }
        if(!skip){
            parent.appendChild(menuitem);
            menutype.push(element.type);    
        }
    });
    return ids;
}
// <-- create menu commands
