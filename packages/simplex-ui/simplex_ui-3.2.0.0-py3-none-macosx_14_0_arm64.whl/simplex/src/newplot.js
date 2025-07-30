"use strict";

var GUIConf = {};
var PlotObject = {};
var Framework;
var PlotWindows;
var Settings = {plotconfigs:{}, defpaths:{}, scanconfig:{}};
var TWindow = {}; // tauri windows object

if(window.hasOwnProperty("__TAURI__")){
    Framework = TauriLabel;
    TWindow = window.__TAURI__.window;
    window.__TAURI__.event.listen("message", (e) => {
        ArrangeObjects(e.payload);
    });
}
else{
    Framework = BrowserLabel; // python verions reduce to browser
    window.addEventListener("message", (e) => {
        ArrangeObjects(e.data);
        setTimeout(
            function(){
                for(let np = 0; np < PlotWindows.length; np++){
                    PlotWindows[np].RefreshPlotObject();
                }
            }, 100);
    });
}
SetWindowTitle();

window.onload = function()
{
    if(Framework == TauriLabel){
        window.__TAURI__.event.emit("ready", "");
    }
    else{
        window.opener.postMessage("ready", "*");
    }
}

async function ExportAsciiNew()
{
    if(Framework == PythonGUILabel){
        let data = [];
        PlotWindows.forEach(plotwin => {
            data.push(plotwin.GetASCIIData());
        });
        let obj = {type: "export", data: data};
        window.opener.postMessage(JSON.stringify(obj), "*");
        return;
    }
    ExportPlotWindows("new-ascii", PlotWindows);
}

function SaveObject()
{
    PlotObject.data = [];
    for(let n = 0; n < PlotWindows.length; n++){
        PlotObject.data.push(PlotWindows[n].GetData());
    }
    PlotObject.size = [window.innerWidth, window.innerHeight];
    if(Framework == PythonGUILabel){
        let obj = {type: "save", data: PlotObject};
        window.opener.postMessage(JSON.stringify(obj), "*");
        return;
    }
    SavePlotObj(PlotObject);
}

function ArrangeObjects(data)
{
    let pp_plot = document.getElementById("pp_plot");
    let plobj = data.data;
    PlotObject.cols = data.cols;
    PlotObject.subcols = data.subcols;
    PlotObject.size = data.size;
    if(data.hasOwnProperty("Framework")){
        Framework = data.Framework;
    }
    
    let nplots = plobj.length;
    if(nplots == 1){
        PlotObject.subcols = null;
    }
    let areas = [document.createElement("div"), document.createElement("div")];
    areas[0].className = "flex-grow-1";
    let stylestr = "display: grid; grid-template-columns: 1fr";
    if(nplots > 1){
        for(let j = 1; j < PlotObject.cols; j++){
            stylestr += " 1fr";
        }
    }
    areas[0].style = stylestr;

    pp_plot.appendChild(areas[0]);
    pp_plot.appendChild(areas[1]);
    let plotparents = [];
    for(let n = 0; n < nplots; n++){
        plotparents.push(document.createElement("div"));
        plotparents[n].className = "d-flex flex-grow-1";
        areas[0].appendChild(plotparents[n]);
    }

    window.resizeBy(data.size[0]-window.innerWidth, data.size[1]-window.innerHeight);

    let lists = [];
    for(let np = 0; np < nplots; np++){
        if(lists.includes(plobj[np].plotname) == false){
            lists.push(plobj[np].plotname);
        }
    }
    SetWindowTitle(lists.join("/"));

    PlotWindows = new Array(plobj.length);
    for(let np = 0; np < nplots; np++){
        let frames = 1;
        if(plobj[np].hasOwnProperty("fdata")){
            frames = plobj[np].fdata[0].length*plobj[np].fdata[1].length;
        }
        PlotWindows[np] = new PlotWindow(
            plotparents[np], "newwin"+np.toString(), plobj[np], plobj[np].setting, 
            plobj[np].plotname, PlotObject.subcols, plobj[0].frameindices, plobj[np].tinv, 0, areas[1], 
            np > 0 || frames == 1, plobj[np].layout, plobj[np].link2d);
        if(plobj[np].hasOwnProperty("title")){
            PlotWindows[np].PutTitle(plobj[np].title);
        }
    }

    plotparents[0].addEventListener("slidechange", (e)=>{
        for(let np = 1; np < nplots; np++){
            PlotWindows[np].ShowSlide(false, e.detail.slices);
        }
    });
}
