"use strict";

//-------------------------
// generate help file
//-------------------------

var header_tags = ["h1", "h2", "h3", "h4", "h5", "h6"];
var espcape_chars = ["&lambda;","&gamma","&epsilon;","&eta;","&beta;","&sigma;","&Sigma;"];

const SimplexUILabel = GetSoftName("simplex-ui");

// utility functions
function FormatHTML(htmlstr)
{
    let formathtml = htmlstr
        .replace(/<tbody>/g, "<tbody>\n\n")
        .replace(/<tr>/g, "<tr>\n")
        .replace(/<\/tr>/g, "</tr>\n")
        .replace(/<\/td>/g, "</td>\n")
        .replace(/<\/h1>/g, "</h1>\n")
        .replace(/<\/h2>/g, "</h2>\n")
        .replace(/<\/h3>/g, "</h3>\n")
        .replace(/<\/h4>/g, "</h4>\n")
        .replace(/<\/h5>/g, "</h5>\n")
        .replace(/<\/h6>/g, "</h6>\n")
        .replace(/<p>/g, "\n<p>")
        .replace(/<\/p>/g, "</p>\n")
        .replace(/<\/table>/g, "</table>\n\n");
    return formathtml;
}

function SetRemarks(categ, captions)
{
    let data ="";
    for(let j = 0; j < captions.length; j++){
        let capp = document.createElement("p");
        capp.innerHTML = captions[j];
        capp.id  = categ+(j+1).toString();
        data += capp.outerHTML;
    }
    return data;
}

function GetQString(str)
{
    return "\""+str+"\"";
}

function GetBoldString(str)
{
    return "<b>"+str+"</b>";
}

function GetLink(href, caption, isel)
{
    let link = document.createElement("a");
    link.href = "#"+href;
    link.innerHTML = caption;
    if(isel){
        return link;
    }
    return link.outerHTML;
}

function RetrieveEscapeChars(label)
{
    let fchars = [];
    let iini, ifin = 0;
    do{
        iini = label.indexOf("&", ifin);
        if(iini >= 0){
            ifin = label.indexOf(";", iini);
            let fchar = label.substring(iini , ifin+1);
            if(fchars.indexOf(fchar) < 0){
                fchars.push(fchar);
            }
        }    
    } while(iini >= 0);
    return fchars;
}

function RetrieveAllEscapeChars(prmlabels)
{
    let escchars = [];
    for(let j = 0; j < prmlabels.length; j++){
        let labels = Object.values(prmlabels[j]);
        for(let i = 0; i < labels.length; i++){
            let fchars = RetrieveEscapeChars(labels[i]);
            for(let k = 0; k < fchars.length; k++){
                if(escchars.indexOf(fchars[k]) < 0){
                    escchars.push(fchars[k]);
                }    
            }
        }
    }
    return escchars;
}

function ReplaceSpecialCharacters(espchars, org)
{
    let ret = org;
    let div = document.createElement("div");
    for(let j = 0; j < espchars.length; j++){
        div.innerHTML = espchars[j];
        let spchar = div.innerHTML;
        while(ret.indexOf(spchar) >= 0){
            ret = ret.replace(spchar, espchars[j]);
        }    
    }
    return ret;
}

function WriteParagraph(phrases)
{
    let data = "";
    for(let j = 1; j < phrases.length; j++){
        let p = document.createElement("p");
        p.innerHTML = phrases[j];
        data += p.outerHTML;
    }
    return data;
}

function WriteListedItem(items, isnumber)
{
    let data;
    let ol = document.createElement(isnumber?"ol":"ul");
    for(let j = 1; j < items.length; j++){
        let li = document.createElement("li");
        li.innerHTML = items[j];
        ol.appendChild(li);
    }
    data = ol.outerHTML;
    return data;
}

function WriteFigure(src, figcaption, width = null)
{
    let fig = document.createElement("figure");
    fig.id = src;
    let img = document.createElement("img");
    img.src = src;
    if(width == null){
        if(ImageWidths.hasOwnProperty(src)){
            let width = 3*ImageWidths[src]/4;
            if(src == "BMsetup.png"){
                width = ImageWidths[src]/2;
            }
            img.style.width = Math.floor(width).toString()+"px";
        }
    }
    else{
        img.style.width = Math.floor(width).toString()+"px";
    }
    let caption = document.createElement("figcaption");
    caption.innerHTML = figcaption;
    fig.appendChild(img);
    fig.appendChild(caption);
    return fig.outerHTML;
}

function GetSoftName(name)
{
    let ndiv = document.createElement("span");
    ndiv.innerHTML = name;
    ndiv.classList = "software";
    return ndiv.outerHTML;
}

function WriteObject(layer, obj)
{
    let value;
    let data = "";
    if(Array.isArray(obj) == true){
        value = CopyJSON(obj);
    }
    else{
        let key = Object.keys(obj)[0];
        value = Object.values(obj)[0];
    
        layer = Math.min(layer, header_tags.length-1);
        let hdr = document.createElement(header_tags[layer]);
        hdr.innerHTML = key;
        hdr.id = key;
        data += hdr.outerHTML;
    
        if(typeof value == "string" && value.indexOf("@") >= 0){
            data += value;
            return data;
        }
        else if(Array.isArray(value) == false){
            data += "Error";
            alert("Error"+value);
            return data;
        }   
    }

    if(value[0] == "Paragraph"){
        data += WriteParagraph(value);
        return data;
    }
    else if(value[0] == "NumberedItem"){
        data += WriteListedItem(value, true);
        return data;
    }
    else if(value[0] == "ListedItem"){
        data += WriteListedItem(value, false);
        return data;
    }

    for(let j = 0; j < value.length; j++){
        if(typeof value[j] != "string"){
            data += WriteObject(layer+1, value[j]);
        }
        else if(value[j].indexOf("<img") >= 0){
            data += value[j];
        }
        else{
            let p = document.createElement("p");
            p.innerHTML = value[j];
            data += p.outerHTML;
        }
    }
    return data;
}

function AppendCell(row, item, classname = "")
{
    if(item == null){
        return null;
    }
    let cell = row.insertCell(-1);
    if((typeof item) == "string"){
        cell.innerHTML = item;
    }
    else if(Array.isArray(item)){
        cell.innerHTML = WriteObject(0, item);
//        cell.innerHTML = item.join(",");
    }
    else{
        let cols = 1;
        let rows = 1;
        if(item.hasOwnProperty("cols")){
            cols = item.cols;
        }
        if(item.hasOwnProperty("rows")){
            rows = item.rows;
        }
        if(cols > 1 || rows > 1){
            cell.innerHTML = item.label;
            if(cols > 1){
                cell.setAttribute("colspan", cols);
            }
            if(rows > 1){
                cell.setAttribute("rowspan", rows);
            }
        }
        else{
            cell.innerHTML = WriteObject(0, item);
        }
    }
    if(classname != ""){
        cell.className = classname;
    }
    return cell;
}

function GetTable(captext, titles, data, subtitles = null)
{
    let cell, rows = [];
    let table = document.createElement("table");

    if(captext != ""){
        let caption = document.createElement("caption");
        caption.innerHTML = captext;
        table.caption = caption;    
    }

    rows.push(table.insertRow(-1)); 
    for(let j = 0; j < titles.length; j++){
        AppendCell(rows[rows.length-1], titles[j], "title");
    }
    if(subtitles != null){
        rows.push(table.insertRow(-1)); 
        for(let j = 0; j < subtitles.length; j++){
            AppendCell(rows[rows.length-1], subtitles[j], "title");
        }    
    }

    for(let j = 0; j < data.length; j++){
        rows.push(table.insertRow(-1));
        for(let i = 0; i < titles.length; i++){
            cell = AppendCell(rows[rows.length-1], data[j][i]);            
        }
        if(data[j].length > titles.length && cell != null){
            // set the id of this cell
            cell.id = data[j][titles.length]
        }
    }
    let retstr = table.outerHTML;
    return retstr;    
}


function GetMenuCommand(menus)
{
    let qmenus = [];
    for(let j = 0; j < menus.length; j++){
        qmenus.push("["+menus[j]+"]");
    }
    return qmenus.join("-");
}

function GetDirectPara(str)
{
    let div = document.createElement("div");
    div.innerHTML = "<pre><code>"+str+"</code></pre>";
    div.className = "direct";
    return div.outerHTML;
}

function GetTableBody(tblstr, ishead, isfoot)
{
    let tblinner = tblstr;
    if(!ishead){
        tblinner = tblinner
            .replace("<table>", "")
            .replace("<tbody>", "");
    }
    if(!isfoot){
        tblinner = tblinner
            .replace("</table>", "")
            .replace("</tbody>", "");
    }
    return tblinner;
}

// main body
var chapters = {
    copyright: "Copyright Notice",
    intro: "Introduction",
    gui: "Operation of the GUI",
    prmlist: "Parameter List",
    calcsetup: "Simulation Setup",
    prep: "Pre-Processing",
    postp: "Post-Processing",
    format: "File Format",
    standalone: "Standalone Mode",
    python: "Python User Interface",
    ref: "References",
    ack: "Acknowledgements"
}

var sections = {
    overview: "Overview",
    simmode: "Simulation Modes",
    funcs: "Functions Available",
    start: "Getting Started",
    check: "Rough Estimation",
    visualize: "Graphical Plot",
    dataimp: "Import Custom Data",
    pdata: PPPartAnaLabel,
    lasemod: PPMicroBunchLabel,
    udata: PPUdataLabel,
    optbeta: "Optimize Lattice Function",
    plotlyedit: "Edit the Plot",
    json: "JSON Format",
    compplot: "Comparative Plot",
    multiplot: "Multiple Plot",
    mdplot: "Plotting 3/4-Dimensional Data",
    scan: "Scanning a Parameter",
    ascii: "Export as ASCII",
    input: "Input Format",
    output: "Output Format",
    binary: "Binary File Format"
}

var menus = {
    file: "File",
    run: "Run",
    help: "Help" 
}

var refidx = {};
var referencelist = GetReference(refidx);

function GetHelpBody(){
    return [
        {
            [chapters.copyright]: [
                "Paragraph",
                "<em>Copyright 2004-2024 Takashi Tanaka</em>",
                "This software is free for use, however, the author retains the copyright to this software. It may be distributed in its entirety only and may not be included in any other product or be distributed as part of any commercial software.", 
                "This software is distributed with <em>NO WARRANTY OF ANY KIND</em>. Use at your own risk. The author is not responsible for any damage done by using this software and no compensation is made for it.",
                "This software has been developed, improved and maintained as voluntary work of the author. Even if problems and bugs are found, the author is not responsible for improvement of them or version up of the software.",
                "<em>If you are submitting articles to scientific journals with the results obtained by using this software, please cite the relevant references.</em> For details, refer to "+GetLink(chapters.intro, chapters.intro, false)+"."
            ]
        },
        {
            [chapters.intro]: [
                "This document describes the instruction to use the free software SIMPLEX, a free electron laser simulation (FEL) code, and is located in \"[SIMPLEX Home]/help\", where \"[SIMPLEX Home]\" is the directory where SIMPLEX has been installed. Brief explanations on the software and numerical implementation of FEL equations are given here, together with a simple instruction of how to get started. Note that <a href=\"https://www.mathjax.org/\">"+GetQString("MathJax")+"</a> javascript library is needed to correctly display the mathematical formulas, which is available online. If you need to read this document offline, "+GetQString("MathJax")+" should be installed in \"[SIMPLEX Home]/help\" directory.",
                {
                    [sections.overview]: [
                        "Paragraph",
                        "SIMPLEX, which stands for SIMulator & Postprocessor for free electron Laser EXperiments, is a computer program to simulate the amplification process of free electron lasers (FELs) and evaluate the light source performances, such as the radiation power growth, electron motion in the phase space, evolution of angular and spatial profiles of radiation field, etc. In order to perform the FEL simulations, a lot of parameters are required to specify the electron beam, lattice function, undulator, and numerical & boundary conditions. SIMPLEX is equipped with a graphical user interface (GUI), which helps the user to input these parameters. Possible errors in the undulator such as the magnetic field and trajectory errors can also be handled in the GUI.",
                        "Besides the above standard functions, the GUI automatically computes and shows relevant parameters related to the FEL system, such as the Pierce parameter, 1D & 3D gain lengths, and saturation power, so that the user can quickly check if their parameters are realistic in advance of actually starting the simulation. Light source characteristics, such as the lasing wavelength, bandwidth, source size and brilliance, are also estimated based on an assumption that the FEL radiation is spatially coherent.",
                        "In addition to pre-processing mentioned above, SIMPLEX offers a GUI-based postprocessor to facilitate retrieving desired information from the simulation results. For example, light source characteristics of FEL radiation can be retrieved from the radiation field profile, and the electron motion can be retrieved from the numerical data on macroparticles modeling the electron beam.",
                        "The numerical part of SIMPLEX (\"solver\") is written in C++11 with the standard template library (STL), which solves the equations describing the FEL process in the 3-dimensional (3-D) form. As explained in the next section, the simulations can be classified into two types according to how to deal with the slippage between electrons and radiation emitted by them. For details of numerical implementation, refer to "+GetLink("simplexjsr", refidx.simplexjsr, false)+".",
                        "In ver. 3.0, the solver has been widely revised to be consistent with the C++11 standard and to facilitate the maintenance and bug fix. In addition, numerical implementation of FEL equations has been improved to be more CPU-efficient and to reduce the simulation time. In addition to the above revisions, two important upgrades have been made. First, the format of the input parameter file has been changed from the original (and thus not readable in other applications) one to JSON (JavaScript Object Notation) format. Because the output data is also given by a JSON file, it is now easy to communicate with other 3rd-party applications."
                    ]
                },
                {
                    [sections.simmode]: [
                        "Paragraph",
                        "In order to investigate the FEL amplification process, it is necessary to solve three equations: (1) equation of motion to describe the motion of each electron in the phase 6-D (x,x',y,y',t,&gamma;) space, (2) energy equation to describe the energy exchange between electrons and radiation, and (3) wave equation to describe the evolution of radiation field. Let us call these equations \"FEL equations\" hereinafter. The main function of an FEL simulator is to numerically solve the FEL equations.",
                        "The wave equation describes evolution of the electric field of radiation and is given by \\[\\left[\\nabla^2+2i\\frac{\\omega}{c}\\left(\\frac{\\partial}{\\partial z}+\\frac{1}{c}\\frac{\\partial}{\\partial t}\\right)\\right]\\mathbf{E}\\mbox{e}^{-i\\omega(z/c-t)}+\\mbox{c.c.}=\\mu_0\\frac{\\partial\\mathbf{j}}{\\partial t}+\\frac{\\nabla\\rho}{\\varepsilon_0},\\] where E is the complex amplitude of radiation field, &omega; is the frequency of radiation, j and &rho; are the current and charge densities of the electron beam.",
                        "Assuming that the electron beam is infinitely long with constant beam parameters such as the emittance, energy, current, and offset (angular and positional), and also the radiation is completely monochromatic, the partial differentiation with respect to time can be dropped from the wave equation. In such a case, the simulation algorithm is considerably simplified and the simulation is referred to as \"steady-state\".",
                        "If the above assumption cannot be applied, the wave equation should be solved with the time dependence taken into account, namely, the slippage between the electron beam and radiation should be considered. To be specific, the radiation emitted by the electrons slips out of them by the so-called slippage length, which equals the fundamental wavelength of undulator radiation. The FEL simulation that takes into account the slippage effect is referred to as \"time-dependent\", which requires a lot of computation time because the algorithm to solve the FEL equations should be applied over the whole electron bunch.",
                        "In order to roughly estimate the FEL performance such as the saturation power, saturation length, radiation spatial profile and motion of the electrons in the 6-D phase space, the steady-state simulation suffices. On the other hand, the time-dependent simulation should be performed for various purposes, e.g., the start-to-end simulations for SASE (self-amplified spontaneous emis-sion) FELs, and investigations of the effects due to the wakefield induced in the undulator line."
                    ]
                },
                {
                    [sections.funcs]: [
                        "Besides the normal FEL simulation procedures described in the preceding section, SIMPLEX offers various functions to investigate the performance of FEL.",
                        {
                            ["Rough Estimation of FEL Performances"]: [
                                "A number of FEL parameters and light source characteristics can be roughly estimated by an-alytical formulae instead of rigorous simulations. SIMPLEX preprocessor automatically computes these values with the given conditions, in order to help the users not only to check if their pa-rameters are valid but also to understand the meanings of parameters.",
                            ]
                        },
                        {
                            ["Electron Beam Data Manipulation"]:[
                                "In order to perform the so-called start-to-end simulation, initial conditions of the electron beam injected to the undulator should be specified. SIMPLEX accepts the user input by importing a file that stores the numerical data of the sliced beam parameters along the bunch. Another way is to load the macroparticle distribution in the 6-D phase space, which is probably generated by an external program. In addition, the preprocessor offers a function to analyze the macroparticle distribution to obtain the sliced beam parameters such as the current, emittance, energy spread, and so on."
                            ]
                        },
                        {
                            ["Modeling the Undulator Field Error"]: [
                                "In normal FEL simulations, the undulator magnetic field is assumed to be completely sinusoidal, which is not the case for the real undulator. SIMPLEX can import the magnetic field distribution data actually measured with a field measurement apparatus such as Hall-effect sensors. Other possible errors of the magnetic field, such as the geomagnetic field and demagnetization due to radiation damage, can be investigated by importing the field-distribution data including these effects. In addition to the above function to specify the undulator error, SIMPLEX offers an option to automatically generate the field errors which reproduce the phase error and trajectory wander in respective undulator segments."
                            ]
                        },
                        {
                            ["Modeling the Alignment Error"]: [
                                "Besides the magnetic field error, there is another error source in the undulator line: alignment errors such as the discrepancy in the gap value between undulator segments, tilt and offset in the vertical position of each undulator, the trajectory error due to misalignment of beam position monitors, and so on. SIMPLEX can perform FEL simulations with all these misalignment effects taken into account."
                            ]
                        },
                        {
                            ["Wakefield Effects"]: [
                                "The wakefield is induced by interaction between the electron and surrounding environment such as the beam pipe, and induces correlated energy variation in the electron bunch. In order to investigate the wakefield effects on the FEL amplification process, it is required to specify the profile of the wakefield along the electron bunch. In SIMPLEX, the wakefield can be computed internally using analytical expressions derived in several research papers. It is also possible to specify the wakefield distribution by importing the wakefield data."
                            ]
                        },
                        {
                            ["Configuration of Lattice Functions"]: [
                                "In general, there exists an optimum betatron function for a given set of electron-beam and undulator parameters and thus the layout and strength of focusing magnets in the undulator line should be designed so that the average betatron function is optimized. SIMPLEX offers a couple of focusing magnet layouts that are periodically arranged with the undulator segments, which are supposed to be regularly spaced. SIMPLEX preprocessor offers an option to compute the optimum initial Twiss parameters for such a periodic lattice."
                            ]
                        },
                        {
                            ["Post-Processing"]: [
                                "The raw data of simulation results of SIMPLEX, i.e., the complex amplitude of radiation field and macro-particle distribution at each slice are saved in binary files. In order to process them and visualize the results (post-processing), such as the spectrum, instantaneous radiation power, and bunch factor, a GUI-based post-processor is available."
                            ]
                        }
                    ]
                },
                {
                    [sections.start]: [
                        "NumberedItem",
                        "Open a parameter file by running "+GetMenuCommand([menus.file, FileOpen])+" command.",
                        "Edit or input parameters in the GUI window. All the parameters and configurations are categorized into several categories, and are shown in a box titled with each category name. To change the category shown in the GUI, select a relevant tab window.",
                        "Run "+GetMenuCommand([menus.run, StartCalcLabel])+" command to start a simulation with current parameters.",
                        "A \"Progressbar\" appears to inform the simulation status.",
                        "The simulation results are saved in files specified by the user with different suffices. For example, the radiation power and bunch factor averaged over the whole bunch are saved in a file with a suffix \"json\" in the JSON format, together with the input parameters used in the simulation",
                        "To verify the simulation results, click "+GetQString(TabPostProp)+" tab, select the name of the output JSON file, and item(s) to check for visualization. Refer to "+GetLink(TabPostProp, TabPostProp, false)+" for details."
                    ]
                }
            ]
        },
        {
            [chapters.gui]: [
                {"Tab Panels": [
                        "SIMPLEX GUI is composed of 6 tab panels entitled as "+GetBoldString(TabEBSeed)+", "+GetBoldString(TabUnd)+", "+GetBoldString(TabOption)+", "+GetBoldString(TabSimCtrl)+", "+GetBoldString(TabPreProp)+", and "+GetBoldString(TabPostProp)+". Note that "+GetLink(DivFELPrms, DivFELPrms, false)+" and "+GetLink(OutFileLabel, OutFileLabel, false)+" subpanels are shown when one of "+GetQString(TabEBSeed)+", "+GetQString(TabUnd)+", "+GetQString(TabOption)+" and "+GetQString(TabSimCtrl)+" tab panels is selected.",
                        WriteFigure("gui.png", "Example of tab panels in the SIMPLEX GUI."),
                        "@tabpanel",
                    ]
                },
                {"Menu Commands": [
                    "Menu commands available in SIMPLEX are described below.",
                    {[menus.file]:["@filemenu"]},
                    {[menus.run]:["@runmenu"]},
                    {[menus.help]:["Open the reference manual or show the information about SIMPLEX."]}
                ]},
                {[sections.plotlyedit]: [
                    "Besides standard Plotly.js configurations, a number of options to edit the graphical plot in the post- and pre-processors are available. To do so, click the small icon located in the top-right side of the plot. Then a dialog box pops up to let the user edit the plot in the following configurations.",
                    "@plotlyedit"
                ]}    
            ]
        },
        {
            [chapters.calcsetup]: [
                "Details of how to setup and start the simulations are presented here.",
                {
                    ["General Method"]: [
                        {
                            [FileOpen]: [
                                "Upon being started, SIMPLEX tries to load parameters from the parameter file that was opened last time. If successful, the parameters are shown in the GUI. If SIMPLEX is run for the first time after installation, default parameters will be shown. To open a new SIMPLEX parameter file, run "+GetMenuCommand([menus.file, FileOpen])+" command. In the initial setting, the parameter files are found in the directory \"[SIMPLEX Home]/prm\" with a default suffix \"json\", where \"[SIMPLEX Home]\" is the directory in which SIMPLEX has been installed."
                            ]
                        },
                        {
                            [sections.check]: [
                                "Before starting a simulation, the user is recommended to  roughly estimate the expected performances of the FEL system, such as the gain length, saturation power, lasing wavelength, brilliance, etc., to make sure that the input parameters are not far from reasonable ones. In SIMPLEX, these values to represent the FEL performance are automatically evaluated using analytical and empirical expressions on FEL physics "+GetLink("rhooc", refidx.rhooc, false)+"-"+GetLink("scaling", refidx.scaling, false)+" and shown in the "+GetLink(DivFELPrms, DivFELPrms, false)+" subpanel. Note that these values are approximate ones and are given just for reference."
                            ]
                        },
                        {
                            [ArrangeDataLabel]: [
                                "Arrange the output JSON file to save the simulation results in the "+GetLink(OutFileLabel, OutFileLabel, false)+" subpanel. SIMPLEX generates at most 3 files (or more, dependenig on the maximum harmonic number) to save the simulation result with the names of *.json, *.par, *.fld, where * stands for the data name specified by the user. Refer to "+GetLink(OutFileLabel, OutFileLabel, false)+" about how the data name is given.",
                                "The gain curve (growth of the pulse energy etc. along the undulator line) is saved in the \"*.json\" file (hereafter, \"output JSON file\") together with the input parameters and configurations. In addition, temporal, spectral, spatial and angular profiles of radiation are optionally saved if specified. For details, refer to "+GetLink(DataDumpLabel, DataDumpLabel, false)+". Note that the data is saved in the "+GetLink(sections.json, sections.json, false)+". The output JSON file can be loaded for visualization of the gain curve and radiation profiles, or for "+GetLink(RawDataProcLabel, RawDataProcLabel, false)+". Besides such post-processing operations, it can be  loaded as a parameter file for another simulation.",
                                "The radiation and particle data (raw data) are saved in the \"*.fld\" and \"*.par\" files, respectively, in a binary format. The raw data in these files will be used in another simulation, or post-processed later with the assistance of the output JSON file as mentioned above."
                            ]
                        },
                        {
                            [StartCalcLabel]:[
                                "Run "+GetMenuCommand([menus.run, StartCalcLabel])+" command to start a single simulation. Then "+GetQString(CalcProcessLabel)+" subpanel is displayed to indicate the progress of simulation. To cancel the simulation, click "+GetQString(CancelLabel)+" button.",
                                WriteFigure("simstatus.png", "Progress bar to indicate the simulation status."),
                                "Note that the serial number is automatically incremented once the simulation is started, unless it is not negative (-1). This is to avoid the overlap of data names in performing successive simulations. When the simulation is completed, the "+GetQString(CalcProcessLabel)+" subpanel vanishes and the result is imported in the "+GetQString(chapters.postp)+" panel for visualization."
                            ]
                        },
                        {
                            ["Verify the Result"]: [
                                "Upon completion of a simulation, the output JSON file is automatically loaded and the gain curve (pulse energy vs. longitudinal position) is plotted in the "+GetQString(chapters.postp)+" subpanel to quickly view the results. Refer to "+GetLink(chapters.postp, chapters.postp, false)+" for details about how to operate the "+chapters.postp+"."
                            ]
                        }
                    ]
                },
                {
                    [CalcProcessLabel]: [
                        "To configure a number of simulations with different conditions, run "+GetMenuCommand([menus.run, "Create Process"])+" command every time you finish specifying all the parameters. Then the "+GetQString(CalcProcessLabel)+" subpanel appears to show the simulation list currently saved in a temporary memory. Repeat the above porcess until all the simulations are specified. Click "+GetQString(RemoveLabel)+" button to delete the selected process, or "+GetQString(CancellAllLabel)+" to clear out all the processes. Run "+GetMenuCommand([menus.run, StartCalcLabel])+" command to start the simulation processes, then a progressbar is displayed to show the status of each process as shown below.",
                        WriteFigure("simprocs.png", "List of simulation processes.")
                    ]
                },
                {
                    [sections.scan]: [
                        "Besides the method described above, it is possible to configure a lot of processes at once by scanning a specific parameter. To do so, right click the target parameter in one of the subpanels, and click "+GetMenuCommand(["Scan This Parameter"])+" in the context menu. Then specify the configurations for scanning in the dialog box as shown below. Note that the context menu does not pop up for parameters that cannot be used for scanning.",
                        WriteFigure("scan.png", "Configuration for scanning a parameter; the normalized emittance is to be scanned in this example."),
                        "Input the initial & final values, and number of points for scanning. For several parameters to be specified by an integer, scanning interval instead of the number of points should be given. If the target parameter forms a pair, such as &epsilon;<sub>x, y</sub> (horizontal and vertical normalized emittances), the user is requested to select "+GetQString("Scan Type")+". "+GetQString(Scan2D1DLabel)+" means that only the target parameter (&epsilon;<sub>x</sub> or &epsilon;<sub>y</sub> in this example) is varied from the inital to the final values. "+GetQString(Scan2DLinkLabel)+" means that both of the pair are simultaneously varied. In contrast to these 1D scan types, "+GetQString(Scan2D2DLabel)+" varies the both parameters in a 2D manner, and thus N<sub>1</sub>N<sub>2</sub> processes are created, where N<sub>1,2</sub> stands for "+GetQString(ScanConfigLabel.scanpoints2[0])+" parameters.",
                        "After configuration, click "+GetQString("OK")+" button. Then the specified parameters are saved in a temporary memory and the scanning process is saved in the simulation list. Run "+GetMenuCommand([menus.run, StartCalcLabel])+" command to start the simulation. Note that a serial number starting from "+GetQString(ScanConfigLabel.iniserno[0])+" is attached to the data name to avoid overlap. If "+GetQString(Scan2D2DLabel)+" is chosen, the serial number is given like "+GetQString("_m_n")+", where m and n mean the serial numbers corresponding to the 1st and 2nd parameters of the pair."
                    ]
                }
            ]
        },
        {
            [chapters.prmlist]: [
                "All the parameters and configurations needed to perform an FEL simulation are classified into several categories in SIMPLEX, and can be edited in the subpanels tiltled with the category name. Details of them are explained in the followings for each category.",
                {
                    [EBLabel]: [
                        "The parameters and configurations in the "+GetQString(EBLabel)+" subpanel are related to the specifications of the electron beam. Details are summarized below.",
                        "@ebprm",
                        {
                            [EBeamPrmsLabel.bmprofile[0]]: [
                                "The distribution functions of the electron beam assumed in the FEL simulation, or the profiles in the 6D phase space available in SIMPLEX,  are summarized below. Note that the custom data needed for several types can be imported in the "+GetLink(sections.dataimp, sections.dataimp, false)+" tab panel.",
                                "@ebtype"
                            ]
                        }
                    ]
                },
                {
                    [SeedLabel]: [
                        "The parameters and configurations in the "+GetQString(SeedLabel)+" subpanel are related to the specifications of the electron beam. Details are summarized below.",
                        "@seedprm",
                        {
                            [SeedTypeLabel]: [
                                "Types of the Seed light available in SIMPLEX are summarized below.",
                                "@seedtype"
                            ]
                        }
                    ]
                },
                {
                    [SPXOutLabel]: [
                        "The results of the former simulation, namely, the distribution of the macripartiles and radiation profiles can be reused in another simulation. To enable this option, related raw data should be exported in the former simulation ("+GetLink(DataDumpLabel, DataDumpLabel, false)+").",
                        "@spxprm",
                        {
                            [R56DriftLabel]: [
                                "To use the former simulation result as ",
                                WriteFigure("ulinestr.png", "Meanings of parameters for using the former simulation result.")
                            ]
                        },                        
                    
                    ]
                },
                {
                    [UndLabel]: [
                        "The parameters and configurations in the "+GetQString(UndLabel)+" subpanel are related to the specifications of the undulator. Details are summarized below.",
                        "@undprm",
                        {
                            [UndulatorType]: [
                                "Undulator types available in SIMPLEX are summarized below.",
                                "@undtype"
                            ]
                        },
                        {
                            [UndulatorLine]: [
                                "The undulator line is supposed to be composed of a number of undulator segments and drift sections in between, where quadrupole magnets are installed (FODO etc. are selected for the "+GetLink(LatticeStrType, LatticeStrType, false)+").",
                                WriteFigure("undulatorline.png", "Parameters to specify the components in the undulator line")
                            ]
                        },
                        {
                            [MultiHarmUndLabel]: [
                                "This is an undulator scheme generating a magnetic field composed of multiple harmonic components, whose configuration is specified in the spreadsheed titled "+GetLink(UndPrmsLabel.multiharm[0], UndPrmsLabel.multiharm[0], false)+".  K<sub>x</sub> Ratio ($=R_n$) and Phase ($=P_n$, in degrees) refer to the fraction and phase of the horizontal field of the n-th harmonic component, where n is the number indicated in the 1st column.",
                                "The K value corresponding to the n-th harmonic is defined as \\[K_{xn}=K_x\\frac{R_n}{\\sqrt{R_1^2+R_2^2+\\cdots+R_N^2}},\\] where $K_x$ is the (total) K value and $N$ is the maximum harmonic number.",
                                "The field distribution is defined as \\[B_{x}(z)=\\sum_{n=1}^{N}B_{xn}\\sin\\left[2\\pi\\left(\\frac{nz}{\\lambda_u}+\\frac{P_n}{360}\\right)\\right],\\] where $B_{xn}$ is the peak field corresponding to the K value of the n-th harmonic.",
                                "Similar definitions of $K_{yn}$ and $B_{y}(z)$ for the horizontal field componeents."
                            ]
                        },
                        {
                            [TaperTypeLabel]: [
                                "Tapering options available in SIMPLEX are summarized below.",
                                "@utapertype"
                            ]
                        },
                        {
                            [TaperCustomLabel]: [
                                "Customize the K value and its gradient along the longitudinal axis for each undualtor segment, as defined below.",
                                "\\[K=K_0+\\Delta K+\\frac{dK}{dz}(z-z_{mid})\\]",
                                "where $K_0$ is the nominal K value, $\\Delta K$ is the offset, $dK/dz$ is the gradient, and $z_{mid}$ is the longitudinal coordinate of the target segment."
                            ]
                        },
                        {
                            [UModelTypeLabel]: [
                                "Undulator models available in SIMPLEX are summarized below.",
                                "@umodeltype"
                            ]
                        },
                        {
                            [HowToTaper]: [
                                WriteFigure("tapering.png", "Example of how to specify the undulator taper with the four parameters."),
                                "In order to specify the undulator taper, four parameters should be specified: \"Initial Segment\", \"Increment Segment Interval\", \"Base Linear Taper\" (&alpha;<sub>1</sub>), and \"Taper Increment\" (&alpha;<sub>2</sub>). The meanings of these parameters are schematically illustrated in the above figure, in which the K value along the undulator axis is plotted when both \"Initial Segment\" and \"Increment Segment Interval\" are assumed to be 3. In this  example, the taper starts at the 3rd segment with the taper rate (dK/dz) of &alpha;<sub>1</sub>, which continues up to the 5th segment. Then the taper rate changes to &alpha;<sub>1</sub>+&alpha;<sub>2</sub> at the 6th segment and continues up to the 8th segment, and again changes to &alpha;<sub>1</sub>+2&alpha;<sub>2</sub> at the 9th segment. This kind of periodic increment continues up to the final undulator segment. The above taper configuration is to model the quadratic taper, and in fact is more convenient for the taper optimization than directly looking for the optimum coefficients of the 2nd order polynomial specifying the taper profile."
                            ]
                        },
                        {
                            [TaperOptType]: [
                                "SIMPLEX offers a scheme to automatically adjust the taper rate to enhance the FEL output by a number of means as summarized below.",
                                "@taperopttype"
                            ]
                        }
                    ]
                },
                {
                    [LatticeLabel]: [
                        "The parameters and configurations in the "+GetQString(LatticeLabel)+" subpanel are related to the arrangement and specifications of the quadrupole magnets and initial Twiss parameters of the electron beam. Details are summarized below.",
                        "@latticeprm",
                        {
                            [LatticeStrType]: [
                                "SIMPLEX offers 5 types of focusing magnet arrangements as shown below. Except for the "+GetQString(CombinedLabel)+" type, the focusing magnets are placed at the drift sections between undulator segments.",
                                WriteFigure("latticetype.png", "Focusing-magnet arrangements in each lattice type available in SIMPLEX")
                            ]
                        }
                    ]
                },
                {
                    [AlignmentLabel]: [
                        "The parameters and configurations in the "+GetQString(AlignmentLabel)+" subpanel are related to the alignment tolerance of the components in the undulator line; this is to evaluate the effects of the misalignment on the FEL amplification process. Details are summarized below.",
                        "@alignprm",
                        {
                            [AlignmentType]: [
                                "Options to specify the alignment errors are summarized below.",
                                "@aligntype"
                            ]
                        }
                    ]
                },
                {
                    [WakeLabel]: [
                        "The parameters and configurations in the "+GetQString(WakeLabel)+" subpanel are related to the parameters and configurations related to the wakefield, which usually degrades the FEL gain.",
                        {
                            [WakeImplementScheme]: [
                                "Wakefield is an electromagnetic wave induced by interaction between electrons and surrounding environment, and induces an energy modulation in the electron bunch, which eventually degrades the FEL gain. In SIMPLEX, several wakefield types can be taken into account to investitage their effects. Note that the wakefield is evaluated only once, before starting a simulation using the current profile at the undulator entrance, and is not modified during the simulation process. This means that the density modulation of the electron beam induced by the FEL interaction is not taken into accout for evaluating the wakefield.", 
                                [
                                    "ListedItem",
                                    "Resistive Wake; the resistive wakefield is evaluated using the expression derived in "+GetLink("resistive", refidx.resistive, false)+".",
                                    "Surface Roughness; the wakefield induced by the surface roughness can be in principle computed using the expressions derived in "+GetLink("rough1", refidx.rough1, false)+" and "+GetLink("rough2", refidx.rough2, false)+" with the knowledge of the surface profile. Instead of them, SIMPLEX uses modified expressions that denote the wakefield induced by the surface whose profile consists of randomly distributed bumps with a Gaussian spectrum.",
                                    "Dielectric Layer: if the surrounding conductor is covered with a thin dielectric layer due to, e.g., oxidation, wakefield is induced as discussed in "+GetLink("synchro", refidx.synchro, false)+".",
                                    "Space Charge: the space charge, or the \"self-induced wakefield without any surrounding structure\", is evaluated using the expressions derived in "+GetLink("spcharge", refidx.spcharge, false)+"."
                                ]
                            ]
                        },
                        "Details of the parameters and configurations are summarized below.",
                        "@wakeprm"    
                    ]
                },
                {
                    [ChicaneLabel]: [
                        "The parameters and configurations in the "+GetQString(ChicaneLabel)+" subpanel are related to the chicane to be inserted in the undulator line. The details are summarized below.",
                        "@chicaneprm"
                    ]
                },
                {
                    [DispersionLabel]: [
                        "The parameters and configurations in the "+GetQString(DispersionLabel)+" subpanel are related to the injection errors and single kick; this is to evaluate the effects of the trajectory error and loss of overlap between the electron beam and seed light.",
                        "@dispprm"
                    ]
                },
                {
                    [SimCondLabel]: [
                        "The parameters and configurations in the "+GetQString(SimCondLabel)+" subpanel are related to the conditions to perform the FEL simulation. Detals are summarized below.",
                        "@simctrlprm",
                        {
                            [SimCtrlsPrmsLabel.simmode[0]]: [
                                "Specifies the simulation mode. Details are summarized below. Also refer to "+GetLink(sections.simmode, sections.simmode, false),
                                "@simtype"
                            ]
                        },
                        {
                            [SimCtrlsPrmsLabel.simoption[0]]: [
                                "Enables an option to be used in the simulation.",
                                "@simoption"
                            ]
                        },
                        {
                            [IntegStepLabel]: [
                                WriteFigure("ulinesteps.png", "Longitudinal step to solve the FEL equatio. In this example, "+GetQString(SimCtrlsPrmsLabel.step[0])+" is 3, which means that the length of a single step is 3&lambda;<sub>u</sub>, where &lambda;<sub>u</sub> is the undulator period, and there are N steps in a single segment.")
                            ]
                        },
                        {
                            [BeamletStrLabel]: [
                                "In general, the number of macroparticles to be used in an FEL simulation is much less than the real number of electrons in the electron beam. This brings a problem of artificial (false) microbunching if the macroparticles are distributed randomly in the phase space. In order to solve the problem without increasing the number of macroparticles, Fawley's algorithm "+GetLink("shotnoise", refidx.shotnoise, false)+" of initial beam loading is implemented, in which all the macroparticles are divided into \"beamlets\" with the longitudinal length equal to the lasing wavelength; the macroparticles in the same beamlet have the identical initial position (x,y), angle (x',y') and energy (&gamma;), and distributes almost evenly along the longitudinal axis with some perturbation to represent the shot noise.",
                                WriteFigure("beamlet.png", "Structure of the beamlet composed of a number of macroparticles"),
                                "The motion of a specific macroparticle traveling along the undulator line is given by solving the equation of motion. The longitudinal position s and energy &gamma; of each macroparticle are given by solving a pair of equations describing the interaction with radiation and undulator field.",
                                "In contrast, the transverse coordinate (x,y,x',y') of each macroparticle is determined by a linear transfer matrix along the undulator line. For example, the horizontal coordinate at the n-th step is given by",
                                "\\[ \\left(\\begin{array}{c}x_n \\\\ x'_n \\\\ 1 \\\\ \\end{array} \\right)=\\left(\\begin{array}{ccc}C_n & S_n & D_n  \\\\ C'_n & S'_n & D'_n \\\\ 0 & 0 & 1 \\\\ \\end{array} \\right)\\left(\\begin{array}{c}x_0 \\\\ x'_0 \\\\ 1 \\\\ \\end{array} \\right), \\]",
                                "where C, S, and D are linear matrix elements defined by the arrangement of the focusing magnets in the undulator line, and subscript 0 means the value at the undulator entrance. Note that effects due to the vaiation of &gamma; along the undulator line, which comes from the interaction with radiation, are supposed to be negligibly small compared to other factors (emittance etc.). As a result, the macroparticles in the same beamlet always have identical transverse coordinate (x,y,x',y'). As a reslt, we need (4+2N<sub>p</sub>)N<sub>b</sub> variables to describe the motion of whole macroparticls in the 6-dimensional phase space; here N<sub>p</sub> is the number of macroparticls in a single beamlet specified by "+GetQString(SimCtrlsPrmsLabel.particles[0])+", while N<sub>b</sub> is the number of beamlets to be used in the simulation specified by "+GetQString(SimCtrlsPrmsLabel.beamlets[0])+"."
                            ]
                        }
                    ]
                },
                {
                    [DataDumpLabel]: [
                        "The parameters and configurations in the "+GetQString(DataDumpLabel)+" subpanel are related to the conditions to export the simulation results. Detals are summarized below.",
                        "@datadumpprm",
                        {
                            [RawDataDumpType]: [
                                "Options to specify the steps to export the raw data are summarized below.",
                                "@rawexptype"
                            ]
                        }
                    ]
                },
                {
                    [OutFileLabel]: [
                        "The parameters and configurations in the "+GetQString(OutFileLabel)+" subpanel are related to the name of the output JSON file and binary files to store the raw data. Detals are summarized below.",
                        "@outfpprm"
                    ]
                },
                {
                    [DivFELPrms]: [
                        "The performances of the FEL system evaluated using analytical and empirical expressions are shown in the "+GetQString(DivFELPrms)+" subpanel. Detals are summarized below.",
                        "@felprm"
                    ]
                }
            ]
        },
        {
            [chapters.prep]: [
                "The "+GetQString(chapters.prep)+" tab panel assists the pre-processing, i.e., visualization and configuration of the simulation conditions, which are not displayed in the subpanels explained above. Six pre-processing operations are available: "+GetQString(sections.visualize)+", "+GetQString(sections.dataimp)+", "+GetQString(sections.pdata)+", "+GetQString(sections.lasemod)+", "+GetQString(sections.udata)+" and "+GetQString(sections.optbeta)+". Detail of each operation is explained below.",
                {
                    [sections.visualize]: [
                        "A number of items can be visualized to verify if the parameters and configurations specified in the subpanels are correct.",
                        WriteFigure("visualize.png", "Example of the "+GetQString(chapters.prep)+" tab panel. The betatron functions along the undulator line are plotted in this example."),
                        "Items that can be visualized are listed in the left; just click one of them for visualization. Note that several of them are available only under specific conditions, which are summarized below. Note that \"Export as ASCII\" exports the current data set and saves as an ASCII file (select a file name in the dialog box), while \"Duplicate Plot\" creates a new window to duplicate the plot.",
                        "@preproc"
                    ]
                },
                {
                    [sections.dataimp]: [
                        "Under a specific simulation condition, the user should prepare custom data and import it. For example, a data file containing the current profile should be imported, if "+GetQString(CustomCurrent)+" is chosen for "+GetQString(EBeamPrmsLabel.bmprofile[0])+" option.",
                        WriteFigure("dataimport.png", "Example of the "+GetQString(chapters.prep)+" tab panel for importing a data set."),
                        "Details of importing the data set are summarized below. The data file to be imported should be an ASCII file, where \"Values\" are given as a function of \"Independent Variable\". \"Condition\" defines the condition in which the relevant \"Data Type\" should be imported. To import the data file, select \"Item to Visualize\" in the list, click "+ImportLabel+" button, and select the data file, or drag-and-drop the file in the area for visualization (grey-painted region in the above example).",
                        "@importpp",
                        "Meanings of \"Values\" and \"Independent Variable\" are as follows with the units to be used in the data file. Note that the units of \"s\" and \"Energy\" should be chosen before importing the data file, in a dialog box to popup by clicking "+GetQString(EditUnitsLabel)+" button.",
                        [
                            "ListedItem",
                            "s: longitudinal position along the electron bunch",
                            "Energy: slice electron energy",
                            "Energy Spread: RMS slice energy spread (dimensionless)",
                            "I: beam current (A)",
                            "&epsilon;<sub>x,y</sub>: normalized emittance (mm.mrad)",
                            "&beta;<sub>x,y</sub>: &beta; Twiss parameter (m)",
                            "&alpha;<sub>x,y</sub>: &alpha; Twiss parameter (dimensionless)",
                            "&lt;x,y&gt;: Offsset position (m)",
                            "&lt;x',y'&gt;: Offset angle (rad)",
                            "&Delta;&gamma;/&gamma;: normalized energy deviation (dimensionless)",
                            "j: beam current density (A/100%)",
                        ],
                        "The unit of j may need to be explained; it is given as the current per unit energy band; in a mathematical form, \\[I(t)=\\int j\\left(t, \\frac{\\Delta\\gamma}{\\gamma}\\right) d\\frac{\\Delta\\gamma}{\\gamma},\\] and thus is given in the unit of Ampere in 100% energy band.",
                        "The data file should be an ASCII file with the format as follows. For the 1-dimensional (1D) data (current profile as an example),",
                        GetDirectPara("s        Current\n-4.00000e-2	1.61861e+2\n-3.99973e-2	1.61904e+2\n-3.99947e-2	1.61947e+2\n-3.99920e-2	1.61990e+2\n          (omitted)\n3.99919e-2	1.61992e+2\n3.99946e-2	1.61949e+2\n3.99972e-2	1.61905e+2\n3.99999e-2	1.61862e+2\n"),
                        "where the 1st line (title) is optional. In the above format, the interval of the independent variable (s) does not have to be necessarily constant, which is not the case for the 2D data; the format should as follows",
                        GetDirectPara("time\tDE/E\tj\n-1.0e-3\t-0.01\t0.001\n-0.9e-3\t-0.01\t0.002\n-0.8e-3\t-0.01\t0.003\n    (omitted)\n0.8e-3\t-0.01\t0.003\n0.9e-3\t-0.01\t0.002\n1.0e-3\t-0.01\t0.001\n-1.0e-3\t-0.008\t0.001\n-0.9e-3\t-0.008\t0.002\n-0.8e-3\t-0.008\t0.003\n    (omitted)\n0.8e-3\t-0.008\t0.003\n0.9e-3\t-0.008\t0.002\n1.0e-3\t-0.008\t0.001\n    (omitted)\n-1.0e-3\t0.01\t0.001\n-0.9e-3\t0.01\t0.002\n-0.8e-3\t0.01\t0.003\n    (omitted)\n0.8e-3\t0.01\t0.003\n0.9e-3\t0.01\t0.002\n1.0e-3\t0.01\t0.001\n"),
                        "For reference, such a data format is created in the C/C++ language as follows.",
                        GetDirectPara("for(n = 0; n < N; n++){\n  for(m = 0; m < M; m++){\n    cout << t[m] << \" \" << de[n] << \" \" <<  j[m][n] << endl;\n  }\n}"),
                        "Note that the order of the \"for loop\" is arbitrary; the 1st and 2nd lines can be swapped in the above example.",
                        "After preparing the ASCII file, click "+GetQString(ImportLabel)+" button and specify the file name in the dialog box to import it. The unit of each item should be chosen before importing, in the "+GetLink(EditUnitsLabel, EditUnitsLabel, false)+" dialog box that pops up by running "+" command. Note that the unit of the imported data cannot be changed, so you need to import the data again with the correct unit in case a wrong unit has been chosen."
                    ]
                }, 
                {
                    [sections.pdata]: [
                        GetQString(sections.pdata)+" pre-processing operation is available when "+GetQString(CustomParticle)+" is selected as "+GetQString(EBeamPrmsLabel.bmprofile[0])+", as shown below. Note that the user needs to specify in advance the data file containing the macroparticle positions in the 6D phase space, which is usually generated by another simulation code. Refer to "+GetLink(EBeamPrmsLabel.partfile[0], EBeamPrmsLabel.partfile[0], false)+" for details.",                        
                        WriteFigure("ppparticle.png", "Example of the "+chapters.prep+" tab panel, under the process of "+GetQString(sections.pdata)),
                        "Once "+GetQString(EBeamPrmsLabel.partfile[0])+" is specified, SIMPLEX automatically loads the file to analyze the particle data. For convenience, part of the data file is shown in "+GetQString("File Contents")+" Select the unit and column index for each coordinate variable of the 6D (x,x',y,y',t,E) phase space and input relevant parameters. In the above example, each macroparticle has the charge of 3.5fC with \"x\" coordinate (horizontal position) located in the 1st column and the unit of m. Note that"+GetQString("Slices in 1&sigma;<sub>s</sub>")+" specifies the number of bins in the  RMS bunch length, to be used for data analysis. Then, additional configurations appear in the GUI to specify how to visualize the results of analysis. In the above example, the current profile is plotted. Upon revision of the configurations above, SIMPLEX automatically analyzes the data with the new configuration and visualizes the result.",
                        "Besides the slice parameters shown in the above example, macroparticle distributions can be directly plotted. For example, distribution in the (E-t) phase space is plotted in the figure below.",
                        WriteFigure("ppparticle2.png", "Example of "+GetQString(sections.pdata)+" pre-processing operation: particle distribution in the (E-t) phase space is plotted."),
                        "The result of analysis can be exported and saved as an ASCII file; "+GetQString("Export Selected")+" exports the data currently plotted, while "+GetQString("Export Slice Data")+" exports the whole slice data (slice paramters vs. s). The exported data file  can be used later as the custom data file for slice parameters or current profile."
                    ]
                },
                {
                    [sections.lasemod]: [
                        GetQString(sections.lasemod)+" pre-processing operation is available for seeded FEL simulations, namely, when options other than "+GetQString(NotAvaliable)+" is chosen as "+GetQString(SeedPrmsLabel.seedprofile[0])+". This is to roughly evaluate the energy modulation in the electron beam through interaction with the seed light. Unlike the rigorous FEL simulation, it neglects the amplification of radiation and other 3D effects coming from the finite emittance of the electron beam, and thus is much faster. Although the result may be less reliable, it can be used to roughly estimate the microbunching in the seeded FELs.",
                        WriteFigure("mbunch.png", "Example of the "+chapters.prep+" tab panel, under the process of "+GetQString(sections.lasemod)),
                        "To start evaluating the microbunching, edit the parameters and configurations listed in the left side, and click "+GetQString("Run")+" button.",
                        "@mbunchprm",
                        "The results of evaluation can be plotted in three different ways (depending on the configurations): distribution of the reference particle in the (E-t) space, current profile, or E-t profile. Select one of the available plots." 
                    ]
                },
                {
                    [sections.udata]: [
                        GetQString(sections.udata)+" pre-processing operation is available when "+GetQString(ImportDataLabel)+" is selected as "+GetQString(UndPrmsLabel.umodel[0])+". Example of the tab panel is shown below.",
                        WriteFigure("impund.png", "Example of the "+chapters.prep+" tab panel, under the process of "+GetQString(sections.udata)),
                        "Click "+GetQString(ImportLabel)+" button and select the undulator data file or drag-and-drop the file in the area for visualization (grey-painted region in the above example). Be sure that the correct units are selected for the longitidunal position and magnetic field strength.",
                        "The imported data name can be changed by clicking "+GetQString("Rename")+" button and input a desired name in the modal dialog box. If a certain data set is not necessary any more, click "+GetQString("Delete")+" button to delete it. "+GetQString("Clear")+" button deletes all the imported data sets."
                    ]
                },
                {
                    [sections.optbeta]: [
                        GetQString(sections.optbeta)+" pre-processing operation tries to optimize the betatron function through the undulator line.",
                        WriteFigure("optbeta.png", "Example of the "+chapters.prep+" tab panel, under the process of "+GetQString(sections.optbeta)),
                        "We have two points to take care in optimization: betatron matching  and average over the whole undulator line. The former is related to the initial Twiss parameters, while the latter is determined by the strength of the quadrupole magnets. Click "+GetQString("Optimize")+" button to start the optimization process. After its completion, the betatron functions through the undulator line are plotted. Parameters needed for optimization are summarized below.",
                        "@boptprm",
                        "Note that the achieved values ("+PreProcessPrmLabel.avbetaxy[0]+") can be far from the target ones, in which case the structure of the undulator line (segment interval, lattice type, etc.) may not be consistent with the electron energy. Another issue is that no solutions are found for the initial Twiss parameters to satisfy the betatron matching condition, in which case the betatron functions (and thus the electron beam size) can diverge. Although the former issue may be probably acceptable, the latter one should be solved before starting a simulation."
                    ]
                }
            ]
        },
        {
            [chapters.postp]: [
                "The "+GetQString(chapters.prep)+" tab panel assists the post-processing, i.e., visualization of the simulation results. Upon completion of a simulation, the output JSON file is automatically loaded, or alternatively, the existing output JSON files can be imported by clicking "+GetQString(ImportLabel)+" button and specify its path.",
                "Two post-processing operations are available: "+GetQString(RawDataProcLabel)+" and "+GetQString(TabPPView)+". The former post-processes the raw data saved in the binary files to evaluate certain items and save the results in a file to be used for visualization, while the latter configures the graphical plot to visualize the simulation results, including those obtained by "+GetLink(RawDataProcLabel, RawDataProcLabel, false)+".",
                {
                    [TabPPView]: [
                        "To visualize the simulation results such as the gain curve and radiation profiles saved in the output JSON file, and the post-processed data generated by "+GetLink(RawDataProcLabel, RawDataProcLabel, false)+", select "+GetQString("Data Type")+" and "+GetQString("Items to Plot")+ " from the list. For 1D plot, also select "+GetQString("x axis")+" to specify the item for the x axis of the plot. The details of "+PPAvailType+" are summarized below.",
                        "@ppavailtype",
                        WriteFigure("postproc.png", "Example of the "+chapters.postp+" tab panel, where the gain curve is plotted."),
                        "The functions of the three buttons in the bottom right are as follows.\"Export as ASCII\" exports the current data set and saves as an ASCII file (select a file name in the dialog box), \"Save\" saves all the configurations of the plot as well as the data in a JSON file, which can be imported later by "+GetLink(FileImportPP, FileImportPP, false)+", and \"Duplicate Plot\" creates a new window to duplicate the plot.",
                        "The dimension of the plot depends on the selected data type and item. In a 1D plot, a desired area can be zoomed in by dragging. Other options are available to operate the plot, by clicking one of the small icons located in the right top of the plot. For details, refer to the documents about "+GetQString("Plotly")+" library to be found online. Besides the above options, the plot can be configured by clicking the "+GetQString("pencil")+" icon and edit the parameters in the modal dialog box to pop up. The details of the parameters are summarized below.",
                        "@ploptprm",
                        {
                            [sections.compplot]: [
                                "If more than one output JSON file is loaded, and/or "+GetLink(RawDataProcLabel, RawDataProcLabel, false)+" has been performed before, "+GetQString(sections.compplot)+" will be available depending on the simulation conditions. Select data names from the list to compare the results."
                            ]
                        },
                        {
                            [sections.multiplot]: [
                                GetQString(sections.multiplot)+" creates more than one plot to view several results simultaneously. The difference from "+GetLink(sections.compplot, sections.compplot, false)+" is that this allows for selection of different items and variables, and the dimension of the plot can be different. Note, however, that the number of steps should be the same for an animation plot."
                            ]
                        },
                        {
                            [sections.mdplot]: [
                                "Depending on the configurations and target items, "+GetLink(RawDataProcLabel, RawDataProcLabel, false)+" pontentially generates 3D or 4D data, which cannot be plotted in a straightforward manner. In SIMPLEX, the 3D/4D data are \"sliced\" into a number of data sets and plotted as a 1D or 2D graph. Let f(z,s,x,y) be a function defined by 4 argument variables, z, s, x, and y. SIMPLEX offers several combinations for plotting and slicing variables. If a pair (x,y) is chosen as the plotting variable, then the data is sliced at each (z,s) position, and a 2D plot is created. Note that the coordinates of the slicing variables can be arbitrary chosen within the possible range, by dragging the sliders indicating their positions."
                            ]
                        }
                    ]
                },
                {
                    [RawDataProcLabel] : [
                        {
                            ["General Instructions"] : [
                                "To perform "+GetQString(RawDataProcLabel)+", radiation/particle data should be saved, by enabling "+GetQString(DataOutPrmsLabel.radiation[0])+"/"+GetQString(DataOutPrmsLabel.particle[0])+" option before starting a simualtion. Then, as explained in "+GetLink(ArrangeDataLabel, ArrangeDataLabel, false)+", two types of binary files \"*.fld\" and \"*.par\" are generated when a simulation is completed. In the former file, complex amplitudes of radiation are saved at specified steps, which are then retrieved to evaluate three different items: "+GetQString(PostPPowerLabel)+", "+GetQString(PostPFluxLabel)+" and "+GetQString(PostPCampLabel)+". In the latter file, coordinate variables of all the macroparticles in the 6D phase space are saved, which are then retrieved to evaluate "+GetQString(PostPBunchFLabel)+" and "+GetQString(PostPEnergyLabel)+" , as well as "+GetQString(PostPPartDistLabel)+".",
                            ],
                        },
                        {
                            ["Parameters and configurations"]: [
                                "@pprawprm"
                            ],
                        },
                        {
                            ["Perform Post-Processing"]: [
                                "Once the configurations have been set, click "+GetQString(BtnRunPP)+" to start post-processing. A progress bar appears to inform its progress. When completed, a new file is created to save the post-processed data, with the name \"*-pp(s/n).json\", wherer * is the data name and s/n is the serial number if specified (>0). This file is automatically loaded and the data is visualized. For details of how to visualize the data, refer to "+GetLink(TabPPView, TabPPView, false)+"."
                            ]
                        }
                    ]
                }
            ]
        },
        {
            [chapters.format]: [
                "Besides the operation based on the GUI, SIMPLEX (more precisely, the solver) can be utilized to communicate with external codes for the so-called start-to-end simulations. This actually requires the knowledge of the format of the input and output files, which is explained in the followings.",
                {
                    [sections.json]: [
                        "To deal with the many parameters and options, SIMPLEX utilizes the JSON (JavaScript Object Notation) format, which is described by a number of \"objects\". The object contains a number of \"pairs\" formed by a \"key\" and \"value\", separated by a colon \":\", and should be enclosed by a curly bracket {}. The value can be one of the followings: number, array, string and (another) object. An example of the SIMPLEX input file is as follows.",
                        GetDirectPara("{\n  \"Electron Beam\": {\n    \"Bunch Profile\": \"Gaussian\",\n    \"Electron Energy (GeV)\": 1,\n    ....\n  },\n  \"Seed Light\": {\n    \"Seed Light\": \"Gaussian Beam\",\n    \"Peak Power (W)\": 1000000,\n    ....\n  },\n  \"Undulator\": {\n    \"Undulator Type\": \"Linear\",\n    \"K Value\": 2.03161,\n    ....\n  },\n  \"Lattice\": {\n    \"Lattice Type\": \"FUDU (QF-U-QD-U)\",\n    \"QF Gradient (T/m)\": 5.89896,\n    ....\n  },\n  ....\n}"),
                        "In this example, four JSON objects are found, whose keys are "+GetQString(EBLabel)+", "+GetQString(SeedLabel)+", "+GetQString(UndLabel)+", and "+GetQString(LatticeLabel)+". The value of each object is also an object, which actually specifies the parameters and options, such as \"Energy (GeV)\": 1, denoting the energy of the electron beam to be 1 GeV.",
                        "For details of the JSON format, please refer to any document available online or found in a text book."
                    ]
                },
                {
                    [sections.input]: [
                        "The input file to be loaded by the solver should have 4 JSON objects: "+GetQString(EBLabel)+", "+GetQString(SeedLabel)+", "+GetQString(UndLabel)+", and"+GetQString(SimCondLabel)+". Details of each object are summarized below, where \"GUI Notation\" is the parameter name displayed in the GUI panel, \"Key\" is the name of the key to be used in the input file, \"Format\" is the format of the value, and \"Default\" is the default value. Note that the key name can be either of the \"Full\" or \"Simplified\" expression.",
                        {
                            [EBLabel+" Object"]: [
                                "@ebjson"
                            ]    
                        },
                        {
                            [SeedLabel+" Object"]: [
                                "@seedjson"
                            ]    
                        },
                        {
                            [SPXOutLabel+" Object"]: [
                                "@spxjson"
                            ]    
                        },
                        {
                            [UndLabel+" Object"]: [
                                "@undjson"
                            ]    
                        },
                        {
                            [LatticeLabel+" Object"]: [
                                "@latticejson"
                            ]    
                        },
                        {
                            [WakeLabel+" Object"]: [
                                "@wakejson"
                            ]    
                        },
                        {
                            [AlignmentLabel+" Object"]: [
                                "@alignjson"
                            ]    
                        },
                        {
                            [ChicaneLabel+" Object"]: [
                                "@chicanejson"
                            ]    
                        },
                        {
                            [DispersionLabel+" Object"]: [
                                "@dispjson"
                            ]    
                        },
                        {
                            [SimCondLabel+" Object"]: [
                                "@simctrljson"
                            ]    
                        },
                        {
                            [DataDumpLabel+" Object"]: [
                                "@dumpjson"
                            ]    
                        }
                    ]
                },    
                {
                    [sections.output]: [
                        "To facilitate further processing of the simulation result with other external codes, the structure of the output JSON file is explained below. Note that the order index (for example of an array, column, etc.) in the followings is defined as starting from \"0\", but not from \"1\".",
                        {
                            [GetQString("Input")+" Object"]: ["All the parameters and options are stored in this object with the same format as the "+GetLink(sections.input, sections.input, false)+". If the output JSON file is opened in the GUI (as an input parameter file), these parameters are displayed and can be used again."]
                        },
                        {
                            ["Objects to Save the Simulation Results"]: [
                                "The simulation results are saved in a number of objects with the keys of "+GetQString(GainCurveLabel)+", "+GetQString(TempProfileLabel)+", "+GetQString(SpecProfileLabel)+", "+GetQString(SpatProfileLabel)+" and "+GetQString(AnglProfileLabel)+" (last 4 are optional), and can be visualized by "+GetLink(TabPPView, TabPPView, false)+" as mentioned in "+GetLink(chapters.postp, chapters.postp, false)+".",
                                "@outfmt",
                                "The format of the \"data\" object (2D array) is as follows.",
                                [
                                    "ListedItem",
                                    "0th ~ (n-1)-th array: independent variables, where n is the dimension",
                                    "n-th ~ (n+m-1)-th array: simulation results, where m is the number of items. The length of each array corresponds to the product of the lengths of the independent variable arrays."
                                ],
                                "As an example, let us consider the \"Gain Curve\" object as follows",
                                GetDirectPara("  \"Gain Curve\": {\n    \"dimension\": 1,\n    \"titles\": [\"z\",\"Pulse Energy\",\"Spatial Energy Density\",\"Angular Energy Density\",\"Bunch Factor\",\"Energy Loss\"],\n    \"units\": [\"m\",\"J\",\"J/mm<sup>2</sup>\",\"J/mrad<sup>2</sup>\",\"-\",\"J\"],\n    \"data\": [\n      [0.18,0.36,...,72.33,72.51],\n      [3.78429e-09,7.57999e-09,...,0.000767857,0.000768138],\n      [2.75008e-06,5.28602e-06,...,0.23161,0.230191,0.229851],\n      [2.20925e-06,4.46296e-06,...,126.883,126.987,127.091],\n      [0.00195631,0.00195761,...,0.0183189,0.0178893],\n      [-5.80174e-09,-5.30405e-09,...,-0.000779005,-0.000777961]\n    ]\n  },"),
                                "The data is composed of 1 independent variable (z) and 5 items (Pulse Energy etc.). The 0th array ([0.18,...]) corresponds to the longitudinal coordinate, and the 1st ([3.78429e-09,...]) to the pulse energy, etc.",
                                "In case the dimension is larger than 1 and thus more than one independent variables exist, the order index j of the item array is given as \\[j=j_0+j_1N_0+j_2N_0N_1+\\cdots,\\] where $j_i$ and $N_i$ refer to the order index and number of data points of the $i$-th variable."
                            ]
                        }
                    ]
                },
                {
                    [sections.binary]:[
                        "Besides the output JSON file described above to summarize the simulation results, SIMPLEX optionally exports \"raw data\", namely, the distribution of macroparticles and complex amplitude of radiation. Because these data can be potentially large, they are saved in a binary format to save the required memory size. Besides being used as input data for another simulation with SIMPLEX, they can be retrieved as numerical data for other applications. For this purpose, the format of these binary files are described below. Note that all of the raw data are saved as float (4-byte) numbers instead of double (8-byte) ones to reduce the file size.",
                        {
                            ["Configurations"]: [
                                "To retrieve the binary data, its configurations are needed. In SIMPLEX, they are saved separately in the output file (*.json) as an object defined by \"Raw Data Export\" as follows.",
                                GetDirectPara('{\n  "Raw Data Export": {\n    ...,\n    "Steps (m)": [4.86,11.01,17.16,23.31,29.46,35.61],\n    "Slices (m)": [-9.99382e-07,-9.97437e-07,...,9.99382e-07],\n    "Grid Intervals (m,rad)": [2.13045e-06,1.23744e-06,4.75329e-07,8.18358e-07],\n    "Grid Points": [128,128],\n    "Beamlets": 500000,\n    "Particles/Beamlet": 4,\n    ....\n  },\n  ....\n}'),
                                "In this example, the raw data are exported at 6 ($=K$) longitudinal positions defined as $z$ = 4.86, 11.01,... . The number of beamlets (=$N_b$) and particles per beamlet ($=N_p$) are 500000 and 4, respectively. The electron bunch is divided into 1209 slices ($=L$) with the slice positions of $s$ = -9.99382e-07,-9.97437e-07,..., and the radiation field is evaluated at 128 ($=M$) x 128 ($=N$) transverse grid points, with the intervals of $(\\Delta x,\\Delta y,\\Delta x',\\Delta y')=$(2.13045e-06,1.23744e-06,4.75329e-07,8.18358e-07)."
                            ]
                        },
                        {
                            ["Radiation Profiles"]: [
                                "The complex amplitude of radiation $E(z,s,\\mathbf{r})$ is saved in file(s) named as \"*-h.fld\", with h being the harmonic number. For computational efficiency, the angular representation $\\mathscr{E}$ is saved instead of $E$, which is defined by the spatial Fourier transform, \\[\\mathscr{E}(z,s,\\mathbf{r}')=\\int E(z,s,\\mathbf{r})\\exp(-i\\kappa\\mathbf{r}'\\cdot\\mathbf{r})d\\mathbf{r},\\] where $\\kappa=2\\pi/\\lambda$ is the wavenumber of radiation, and $\\mathbf{r}'=(x',y')$ is the angular coordinate defined as the Fourier conjugate of the transverse coordinate $\\mathbf{r}$. The discrete data set of $A_{klmn}=\\mathscr{E}(z_k,s_l,\\mathbf{r}'_{m,n}=x'_m,y'_n)$ is saved in the format as follows.",
                                "\\[  \\begin{array}{ccccccc} \
                                A_{0000,re} & A_{0000,im} & A_{0001,re} & A_{0001,im} & \\ldots & A_{000N',re} & A_{000N',im} \\\\ \
                                A_{0010,re} & A_{0010,im} & A_{0011,re} & A_{0011,im} & \\ldots & A_{00M'N',re} & A_{00M'N',im} \\\\ \
                                \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots \\\\ \
                                A_{0100,re} & A_{0100,im} & A_{0101,re} & A_{0101,im} & \\ldots & A_{010N',re} & A_{010N',im} \\\\ \
                                \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots \\\\ \
                                A_{1000,re} & A_{1000,im} & A_{1001,re} & A_{1001,im} & \\ldots & A_{100N',re} & A_{100N',im} \\\\ \
                                \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots \\\\ \
                                A_{K'L'M'0,re} & A_{K'L'M'0,im} & A_{K'L'M'1,re} & A_{K'L'M'1,im} & \\ldots & A_{K'L'M'N',re} & A_{K'L'M'N',im} \\\\ \
                                \\end{array} \\]",
                                "where subscripts re and im mean the real and imaginary parts and $K'=K-1$ being the maximum index for $z_k$, etc. Then, we have $2KLMN$ float numbers in total in this file.",
                                "The relation between indices $(k,l,m,n)$ and real coordinates $(z,s,x',y')$ are given in the output file (*.json) in the former section. Note that the transverse grid points $x,y,x',y'$ are indexed by a common FFT algorithm, and are not as straightforward as $z$ and $s$. Namely, \\[x_m=\\left\\{ \\begin{array}{ll} m\\Delta x&;\\: m\\leq M/2 \\\\ (m-M)\\Delta x&;\\: m> M/2 \\end{array} \\right.\\] and a similar expression for $y,x',y'$.",
                                "The spatial profile of the complex amplitude, $E(\\mathbf{r})$, can be restored by Fourier transforming $\\mathscr{E}(\\mathbf{r}')$, with which $E(\\mathbf{r})$ is discretely given at transverse grid points $x_m$ and $y_m$. Note that we have a well-known relation \\[\\Delta x' = \\frac{\\lambda}{M\\Delta x},\\] and thus $\\Delta x',\\Delta y'$ should be divided by the harmonic number h for higher harmonics.",
                                "If a special (neither linear nor helical) undulator is selected, the radiation field cannot be given by a scalar, and the file format is slghtly different. To be specific, the horizontal ($E_x$) and vertical ($E_y$) components are alternately saved at each longitudinal step, and the format looks as follows.",
                                "\\begin{eqnarray}\
                                \\left. \
                                \\begin{array}{ccccccc} \
                                A_{x,0000,re} & A_{x,0000,im} & A_{x,0001,re} & A_{x,0001,im} & \\ldots & A_{x,000N',re} & A_{x,000N',im} \\\\ \
                                \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots \\\\ \
                                A_{x,0L'M'0,re} & A_{x,0L'M'0,im} & A_{x,0L'M'1,re} & A_{x,0L'M'1,im} & \\ldots & A_{x,0L'M'N',re} & A_{x,0L'M'N',im} \\\\ \
                                \\end{array}\
                                \\right\\} &\\Rightarrow& \\mbox{(0)} \\\\ \
                                \\left. \
                                \\begin{array}{ccccccc} \
                                A_{y,0000,re} & A_{y,0000,im} & A_{y,0001,re} & A_{y,0001,im} & \\ldots & A_{y,000N',re} & A_{y,000N',im} \\\\ \
                                \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots \\\\ \
                                A_{y,0L'M'0,re} & A_{y,0L'M'0,im} & A_{y,0L'M'1,re} & A_{y,0L'M'1,im} & \\ldots & A_{y,0L'M'N',re} & A_{y,0L'M'N',im} \\\\ \
                                \\end{array}\
                                \\right\\} &\\Rightarrow& \\mbox{(1)} \\\\ \
                                \\left. \
                                \\begin{array}{ccccccc} \
                                A_{x,1000,re} & A_{x,1000,im} & A_{x,1001,re} & A_{x,1001,im} & \\ldots & A_{x,100N',re} & A_{x,100N',im} \\\\ \
                                \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots \\\\ \
                                \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots \\\\ \
                                \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots & \\vdots \\\\ \
                                A_{y,K'L'M'0,re} & A_{y,K'L'M'0,im} & A_{y,K'L'M'1,re} & A_{y,K'L'M'1,im} & \\ldots & A_{y,K'L'M'N',re} & A_{y,K'L'M'N',im} \\\\ \
                                \\end{array}\
                                \\right\\} &\\Rightarrow& \\mbox{(2-K')} \\\\ \
                                \\end{eqnarray}",
                                "The section (0) indicted by a curly brace contains $2LMN$ float numbers, representing the horizontal components ($E_x$) over the whole slices and transverse grid points at the 0th step, and the section (1) represents the vertical components at the same step. This arrangement continues until the end of the longitudinal step ($K'$-th step)."
                            ]
                        },
                        {
                            ["Partile Distribution"]: [
                                "The distribution of macroparticles is saved in a file named as \"*.par\". As explained in "+GetLink(BeamletStrLabel, BeamletStrLabel, false)+", the electron beam in SIMPLEX is composed of $N_b$ beamlets, each of which is defined by $4+2N_p$ coordinate variables. The first 4 define the transverse position ($x,y$) and angle ($x',y'$) of each beamlet, while the latter $2N_p$ define the energy ($\\Delta\\gamma/\\gamma$) and longitudinal position ($s$) of each macroparticle. In SIMPLEX, the tansverse coordinate of each beamlet is simply evaluated by the transfer matrix formalism, and can be easily evaluated at any longitudinal steps once the initial values are given. For example, we have \\[\
                                \\left[\
                                \\begin{array}{c}\
                                x(z) \\\\ x'(z) \\\\ \\eta \
                                \\end{array}\
                                 \\right] = \
                                \\left[\
                                \\begin{array}{ccc}\
                                C_x(z) & S_x(z) & D_x(z) \\\\ C'_x(z) & S'_x(z) & D'_x(z) \\\\ 0 & 0 & 1 \
                                \\end{array}\
                                 \\right]\
                                \\left[\
                                \\begin{array}{c}\
                                x(0) \\\\ x'(0) \\\\ \\eta \
                                \\end{array}\
                                 \\right]\
                                \\] with $\\eta\\equiv\\Delta\\gamma/\\gamma$ being relative energy, and a similar expression for $y$ and $y'$. In contrast, the energy and longitudinal position of each macroparticle are numerically evaluated by solving the relevant equations and are saved at each step. As a result, the particle data file has a data format as follows.",
                                "\\[\\begin{eqnarray}\
                                \\begin{array}{ccccccccccc} \
                                x_0 & y_0 & x'_0 & y'_0 & x_1 & \\ldots & x'_{N_b'-1} & y'_{N_b'-1} & x_{N_b'} & y_{N_b'} & x'_{N_b'} & y'_{N_b'} \\\\ \
                                \\end{array} \\:\\:\\:\\:\\:\\: &\\Rightarrow& (0) \\\\ \
                                \\left. \\begin{array}{ccccccccccc} \
                                C_{x,0} & S_{x,0} & D_{x,0} & C'_{x,0} & S'_{x,0} & D'_{x,0} & C_{y,0} & S_{y,0} & D_{y,0} & C'_{y,0} & S'_{y,0} & D'_{y,0} \\\\ \
                                & & & & & \\vdots & \\vdots & & & & & \\\\ \
                                C_{x,K'} & S_{x,K'} & D_{x,K'} & C'_{x,K'} & S'_{x,K'} & D'_{x,K'} & C_{y,K'} & S_{y,K'} & D_{y,K'} & C'_{y,K'} & S'_{y,K'} & D'_{y,K'} \\\\ \
                                \\end{array} \\right\\} &\\Rightarrow& (1) \\\\ \
                                \\left. \\begin{array}{ccccccccccc} \
                                s_{000} & \\eta_{000} & s_{001} & \\eta_{001} & \\ldots & s_{00N_p'} & \\eta_{00N_p'} & s_{010} & \\eta_{010} & \\ldots & s_{0N_b'N_p'} & \\eta_{0N_b'N_p'} \\\\ \
                                s_{100} & \\eta_{100} & s_{101} & \\eta_{101} & \\ldots & s_{10N_p'} & \\eta_{10N_p'} & s_{110} & \\eta_{110} & \\ldots & s_{1N_b'N_p'} & \\eta_{1N_b'N_p'} \\\\ \
                                & & & & & \\vdots & \\vdots & & & & & \\\\ \
                                s_{K'00} & \\eta_{K'00} & s_{K'01} & \\eta_{K'01} & \\ldots & s_{K'0N_p'} & \\eta_{K'0N_p'} & s_{K'10} & \\eta_{K'10} & \\ldots & s_{K'N_b'N_p'} & \\eta_{K'N_b'N_p'} \\\\ \
                                \\end{array} \\right\\} &\\Rightarrow& (2) \
                                \\end{eqnarray}\
                                \\]",
                                "where $x_j, y_j, x_j', y_j'$ denote the transverse coordinate of the $j$-th beamlet, $C_{x,k}, S_{x,k}, ...$ denote the transfer matrix elements at the $k$-th step, and $s_{kji}$ and $\\eta_{kji}$ denotes the longitudinal position and relative energy of the $i$-th particle in the $j$-th beamlet at the $k$-th step. As shown above, the data is composed of 3 sections. The section (0) contains $4N_b$ numbers defining the initial transverse coodrinate of the beamlets, section (1) contains $12K$ numbers to specify the transfer matrix, and section (2) contains $KN_bN_p$ numbers to describe the motion of macroparticles in the energy-time phase space while the electron bunch travels along the undulator." 
                            ]
                        }
                    ]
                }
            ]
        },
        {
            [chapters.standalone]: [
                "Besides the desktop application as described above, the solver of SIMPLEX can be run in a standalone mode. Note that in the followings, [simplex_home] refers to the directory where SIMPLEX has been installed.",
                "When "+GetMenuCommand([menus.run, StartCalcLabel])+" command is executed, the SIMPLEX GUI creates an input parameter file (\"*.json\") and invokes the solver (\"simplex_solver\" or \"simplex_solver_nompi\" depending on whether the parallel computing option is enabled or not) located in the same directory as the main GUI program, with the input file as an argument. This means that SIMPLEX (solver) can be run without the GUI, if the input file is prepared by an alternative method, and a batch process will be possible. To do so, prepare the input file according to the descriptions in "+GetLink(sections.input, sections.input, false)+" and run the solver as follows",
                GetDirectPara("[simplex_home]/simplex_solver_nompi -f [input file]"),
                "to start a simulation without parallel computing, or",
                GetDirectPara("mpiexec -n 4 [simplex_home]/simplex_solver_nompi -f [input file]"),
                "with parallel computing (with 4 MPI processes in this case).",
                "It should be noted that the names of the parameters and options (\"key\" of the object) should be totally correct, including the units and inserted space characters. In addition, the number of parameters and options actually needed for a specific simulation depend on its condition. To avoid possible errors and complexity in preparing the input file, it is recommended to create a \"master input file\" specific to the desired simulation condition, by running "+GetMenuCommand([menus.run, ExportConfigLabel])+". Then, just modify the values of desired parameters to prepare the input file.",
                "Note that this usage has not been officially supported before ver. 2.1, simply because the input file format was original and difficult to read." 
            ]
        },
        {
            [chapters.python]: [
                "To support the expanding users of python language, SIMPLEX has started official support for python, since ver. 3.1. To make use of this function, python version 3.8 or later is needed, and the user is requested to install a python package "+SimplexUILabel+" (SIMPLEX User Interface). Refer to <a href=\"https://spectrax.org/simplex/app/"+Version2Digit+"/python/docs/\">the instructions</a> for details of "+SimplexUILabel+"."
            ]
        },
            {
            [chapters.ref]: [
                "@reference"
            ]
        },
        {
            [chapters.ack]: [
                "This software includes the work that is distributed in the Apache License 2.0, and relies on a number of libraries as summarized below, which are gratefully appreciated.",
                [
                    "ListedItem",
                    "Node.js: Javascript runtime environment to run Javascript code without a web browser (https://nodejs.org/en/).",
                    "Tauri: toolkit to build a desktop application with Javascript, HTML and CSS (https://www.electronjs.org/)",
                    "Plotly.js: Javascript graphing library to facilitate data visualization (https://nodejs.org/en/)",
                    "mathjax: Javascript library to display mathematical formulas in HTML documents (https://www.mathjax.org/)",
                    "picojson: JSON parser for C++ language (https://github.com/kazuho/picojson)",
                    "General Purpose FFT Package (https://www.kurims.kyoto-u.ac.jp/~ooura/fft.html)"
                ]
            ]
        }
    ];   
}

//------ create each component
function GetPreprocDetailTable()
{
    let cell, rows = [];
    let table = document.createElement("table");
    let caption = document.createElement("caption");
    caption.innerHTML = "List of items available for visualization";
    table.caption = caption;

    rows.push(table.insertRow(-1)); 
    let titles = ["Name in "+chapters.prep+" Subpanel", "Details", "Available Condition"];
    for(let j = 0; j < titles.length; j++){
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = titles[j];    
        cell.className = " title";
        if(j == 0){
            cell.setAttribute("colspan", "2");
        }
    }

    let details ={};
    details[UndLabel] = {
        [PPFDlabel]: "Magnetic field distribution along the longitudinal axis in a specific segment.",
        [PP1stIntLabel]: "1st integrals of a specific segment, corresponding to the transverse velocity of an electron moving in the undulator",
        [PP2ndIntLabel]: "2nd integrals of a specific segment, corresponding to the electron trajectory",
        [PPPhaseErrLabel]: "Phase error "+GetLink("refperr", refidx.refperr, false)+" evaluated as a function the magnet pole number. Note that the number of end poles (used for the orbit adjustment and should be eliminated for the phase error evaluation) is automatically determined; to be specific, those with the peak field less than 95% of the average are ignored.",
        [PPKValue]: "Variation of the K value along the undulator line",
        [PPDetune]: "Variation of the detuning ($\\omega/\\omega_1-1$) along the undulator line"
    };
    details[LatticeLabel] = {
        [PPBetaLabel]: "betatron functions along the undulator line",
        [PPOptBetaLabel]: "Optimization of the focusing strength and initial Twiss parameters",
        [PPFocusStrength]: "Focusing strength along the undulator line",
    };
    details[WakeLabel] = {
        [PPWakeBunch]: "Wakefield along the electron bunch",
        [PPWakeEvar]: "Variation of the energy distribution of the electron beam"
    };
    details["Others"] = {
        [PPDispersion]: "Dispersion functions induced by injection and kick errors",
        [PPMonoSpectrum]: "Complex reflectance of the monochromator"
    };
    let remarks ={};
    remarks[UndLabel] = {
        [PPFDlabel]: "",
        [PP1stIntLabel]: "",
        [PP2ndIntLabel]: "",
        [PPPhaseErrLabel]: GetQString(UndPrmsLabel.umodel[0])+" is not "+IdealLabel,
        [PPKValue]: GetQString(UndPrmsLabel.taper[0])+" is not "+NotAvaliable,
        [PPDetune]: GetQString(UndPrmsLabel.taper[0])+" is not "+NotAvaliable
    };
    remarks[LatticeLabel] = {
        [PPBetaLabel]: "",
        [PPOptBetaLabel]: "",
        [PPFocusStrength]: "",
    };
    remarks[WakeLabel] = {
        [PPWakeBunch]: GetQString(WakePrmsLabel.wakeon[0])+" is true",
        [PPWakeEvar]: GetQString(WakePrmsLabel.wakeon[0])+" is true"
    };
    remarks["Others"] = {
        [PPDispersion]: GetQString(AlignErrorUPrmsLabel.BPMalign[0])+" is not "+IdealLabel+", "+GetQString(DispersionPrmsLabel.einjec[0])+" is true, or "+GetQString(DispersionPrmsLabel.kick[0])+" is true",
        [PPMonoSpectrum]: GetQString(ChicanePrmsLabel.monotype[0])+" is not "+NotAvaliable
    };

    let preprocobj = [];
    preprocobj.push({[UndLabel]:[PPFDlabel, PP1stIntLabel, PP2ndIntLabel, PPPhaseErrLabel, PPKValue]});
    preprocobj.push({[LatticeLabel]:[PPBetaLabel, PPOptBetaLabel, PPFocusStrength]});
    preprocobj.push({[WakeLabel]:[PPWakeBunch, PPWakeEvar]});
    preprocobj.push({["Others"]:[PPDispersion, PPMonoSpectrum]});   
    
    for(let i = 0; i < preprocobj.length; i++){
        let categ = Object.keys(preprocobj[i])[0];
        let values = Object.values(preprocobj[i])[0];
        for(let j = 0; j < values.length; j++){
            rows.push(table.insertRow(-1));
            if(j == 0){
                cell = rows[rows.length-1].insertCell(-1);
                cell.innerHTML = categ;
                if(values.length > 1){
                    cell.setAttribute("rowspan", values.length.toString());
                }
            }

            cell = rows[rows.length-1].insertCell(-1);
            cell.innerHTML = values[j];
    
            cell = rows[rows.length-1].insertCell(-1);
            cell.innerHTML = details[categ][values[j]];

            if(remarks[categ].hasOwnProperty(values[j])){
                cell = rows[rows.length-1].insertCell(-1);
                if(Array.isArray(remarks[categ][values[j]])){
                    cell.innerHTML = remarks[categ][values[j]][0];
                    cell.setAttribute("rowspan", remarks[categ][values[j]][1]);
                }
                else{
                    cell.innerHTML = remarks[categ][values[j]];    
                }
            }
        }
    }
    let retstr = table.outerHTML;

    return retstr;
}

function GetImportDetailTable()
{
    let cell, rows = [];
    let table = document.createElement("table");
    let caption = document.createElement("caption");
    caption.innerHTML = "Data types that can be imported in the "+chapters.prep+" tab panel";
    table.caption = caption;

    rows.push(table.insertRow(-1)); 
    let titles = ["Data Type", "Independent Variable", "Values", "Condition", "Item to Visualize"];
    for(let j = 0; j < titles.length; j++){
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = titles[j];    
        cell.className = " title";
    }

    let imports = {};
    imports[CustomSlice] = {
        categ: EBLabel, id: EBeamPrmsLabel.bmprofile[0],
        item: [PPCurrentLabel, PPSliceEmittLabel, "..."],
        condition: CustomSlice,
        detail: "Slice parameters (current, electron energy, emittance, etc.)"
    };
    imports[CustomCurrent] = {
        categ: EBLabel, id: EBeamPrmsLabel.bmprofile[0],
        item: [PPCurrentLabel],
        condition: CustomCurrent,
        detail: "Current profile"
    };
    imports[CustomEt] = {
        categ: EBLabel, id: EBeamPrmsLabel.bmprofile[0],
        item: [PPEtLabel],
        condition: CustomEt,
        detail: "Electron density in the (E-t) phase space"
    };
    imports[WakeDataLabel] = {
        categ: WakeLabel, id: WakePrmsLabel.wakecustom[0],
        item: [PPCustomWake],
        condition: true,
        detail: "Wakefield function by a point unit charge"
    };
    imports[MonoDataLabel] = {
        categ: ChicaneLabel, id: ChicanePrmsLabel.monotype[0],
        item: [PPCustomMono],
        condition: CustomLabel,
        detail: "Complex reflectance of the monochromator"
    };
    
    Object.keys(imports).forEach((el) => {
        rows.push(table.insertRow(-1));

        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = imports[el].detail;

        let dim = GUIConf.ascii[el].GetDimension();
        if(el == CustomParticle){
            dim = 0;
        }

        let titles = GUIConf.ascii[el].GetTitles();
        let tdef = [];
        for(let j = 0; j < dim; j++){
            let idx = titles[j].indexOf("(");
            if(idx < 0){
                tdef.push(titles[j]);
            }
            else{
                tdef.push(titles[j].substring(0, idx));
            }
        }
        cell = rows[rows.length-1].insertCell(-1);
        if(tdef.length > 0){
            cell.innerHTML = tdef.join(", ");
        }

        tdef = [];
        for(let j = dim; j < titles.length; j++){
            let idx = titles[j].indexOf("(");
            if(idx < 0){
                tdef.push(titles[j]);
            }
            else{
                tdef.push(titles[j].substring(0, idx));
            }
        }
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = tdef.join(", ");

        cell = rows[rows.length-1].insertCell(-1);
        let label = "\""+imports[el].id+"\" = \""+imports[el].condition+"\"";
        cell.innerHTML = label;

        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = imports[el].item.join("<br>");
    });
    let retstr = table.outerHTML;
    return retstr;
}

function GetPrmListTable(labels, conts, subtitles)
{
    let table = document.createElement("table");
    let rows = [], cell;
    let titles = ["Parameter/Option", "Detail"];

    rows.push(table.insertRow(-1));
    for(let j = 0; j < titles.length; j++){
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = titles[j];
        cell.className += " title";
    }

    for(let j = 0; j < conts.length; j++){
        let cont = conts[j];
        let label = labels[j];

        if(subtitles[j] != ""){
            rows.push(table.insertRow(-1));
            cell = rows[rows.length-1].insertCell(-1);
            cell.setAttribute("colspan", "2");
            if(Array.isArray(subtitles[j])){
                cell.innerHTML = subtitles[j][0];
                cell.id = subtitles[j][1];
            }
            else{
                cell.innerHTML = subtitles[j];
            }
            cell.className += " subtitle";    
        }

        for(let i = 0; i < cont.length; i++){
            for(let k = 0; k < cont[i][0].length; k++){
                rows.push(table.insertRow(-1));
                cell = rows[rows.length-1].insertCell(-1);
                let labelr = label == null ? cont[i][0][k] : label[cont[i][0][k]];
                let id;
                if(Array.isArray(labelr)){
                    cell.innerHTML = labelr[0];
                    id = labelr[0];
                }
                else{
                    cell.innerHTML = labelr;
                    id = labelr;
                }
                if(cont[i].length > 2){
                    cell.id = id;
                }
                if(k == 0){
                    cell = rows[rows.length-1].insertCell(-1);
                    if(Array.isArray(cont[i][1])){
                        cell.className += " cont";
                        let p = document.createElement("p")
                        p.innerHTML = cont[i][1][0];
                        let ul = document.createElement("ul");
                        for(let l = 1; l < cont[i][1].length; l++){
                            let li = document.createElement("li");
                            li.innerHTML = cont[i][1][l];
                            ul.appendChild(li);
                        }
                        cell.appendChild(p);
                        cell.appendChild(ul);
                    }
                    else{
                        cell.innerHTML = cont[i][1];
                    }
                    if(cont[i][0].length > 1){
                        cell.setAttribute("rowspan", cont[i][0].length.toString());
                    }
                }
            }
        }
    }
    return table.outerHTML;
}

function GetTabPanelTable()
{
    let caption = "Summary of tab panels in the SIMPLEX GUI";
    let titles = ["Title", "Operation", "Related Subpanels"];
    let details = [
        [TabEBSeed, "Display and edit the parameters and configurations related to the electron beam, seed light, and importing the former simulation result.", GetLink(EBLabel, EBLabel, false)+", "+GetLink(SeedLabel, SeedLabel, false)+" and " +GetLink(SPXOutLabel, SPXOutLabel, false)],
        [TabUnd, "Display and edit the parameters and configurations related to the undulator and lattice functions.", GetLink(UndLabel, UndLabel, false)+" and " +GetLink(LatticeLabel, LatticeLabel, false)],
        [TabOption, "Display and edit the parameters and configurations related to the alitmnent tolerance, wakefield in the undulator, chicane to be inserted in the undulator line, and trajectory error and sources to spoil the overlap between the electron beam and seed light.", GetLink(AlignmentLabel, AlignmentLabel, false)+", "+GetLink(WakeLabel, WakeLabel, false)+", "+GetLink(ChicaneLabel, ChicaneLabel, false)+" and " +GetLink(DispersionLabel, DispersionLabel, false)],
        [TabSimCtrl, "Display and edit the parameters and configurations related to the simulation conditions and data save.", GetLink(SimCondLabel, SimCondLabel, false)+" and " +GetLink(DataDumpLabel, DataDumpLabel, false)],
        [TabPreProp, "Assist the pre-processing, i.e., visualization and configuration of the simulation conditions, which are not displayed in the subpanels explained above.", GetLink(chapters.prep, chapters.prep, false)],
        [TabPostProp, "Assist the post-processing, i.e., visualization of the simulation results.", GetLink(chapters.postp, chapters.postp, false)]
    ];
    return GetTable(caption, titles, details);
}

function GetPlotlyDialog()
{
    let xyscales = XYScaleOptions.join(", ");
    let plottypes = PlotTypeOptions.join(", ");
    let clmap = ColorMapOptions.join(", ");
    let caption = "Options for the graphical plot";
    let titles = ["Item", "Details", "Available Options"];
    let dlgconts = [
        [{rows: 2, label:PlotOptionsLabel.normalize[0]}, {rows: 2, label: "Select how to normalize the animation plot"}, 
                    ForEachLabel+": y-/z-axis scale is normalized by the maximum value for each slide"],
        [null, null, ByMaxLabel+": y-/z-axis scale is normalized by the maximum value over the whole slides"],
        [PlotOptionsLabel.xscale[0], "Select the scale for x axis", xyscales],
        [PlotOptionsLabel.yscale[0], "Select the scale for y axis", xyscales],
        [PlotOptionsLabel.type[0], "Select the type of the 1D plot", plottypes],
        [PlotOptionsLabel.size[0], "Size of the symbol", "Input a number"],
        [PlotOptionsLabel.width[0], "Width of the line", "Input a number"],
        [{rows:3, label:PlotOptionsLabel.type2d[0]}, {rows:3, label:"Select the type of the 2D plot"}, ContourLabel+": contour plot with a specific color map"],
        [null, null, SurfaceLabel+": surface plot painted with a specific color map"],
        [null, null, SurfaceShadeLabel+": shaded surface plot illuminated by a specific light source"],
        [PlotOptionsLabel.shadecolor[0], "Select the color of the light source to create a shaded surface plot", "Select from the color picker dialog."],
        [PlotOptionsLabel.colorscale[0], "Select the color map. Several built-in options are available but cannot be customized", clmap],
        [PlotOptionsLabel.wireframe[0], "If checked, grid lines are shown on the surface plot", ""]
    ];
    return GetTable(caption, titles, dlgconts);
}

//----- python -----
function GetEBeamPrmList(rst = false)
{
    let prmconts = [
        [["bmprofile"], "Bunch profile of the electron beam in the 6D phase space."+(rst?"":(" For details, refer to "+GetLink(EBeamPrmsLabel.bmprofile[0], EBeamPrmsLabel.bmprofile[0], false)+"."))],
        [["partfile"], 
        "Path to a local file containing the particle data"+(rst?"":(". Input the absolute path in the text box, or click "+GetQString(BrowseLabel)+" and specify the file in the dialog box. Note that the data file should be an ASCII file, and each line is composed of 6 values specifying the position of a single macroparticle in the 6D phase space. After specifying the data, the user is strongly recommended to perform "+GetQString(sections.pdata)+" for configuration of the particle data such as the units and column indices for respective coordinates.")), true],
        [["eenergy"], "Slice (representative) energy of the electron beam."],
        [["bunchleng"], "RMS bunch length of the electron beam."],
        [["bunchlenr"], "Full bunch length of the electron beam. Available if "+GetQString(BoxcarBunch)+" is chosen for the electron bunch profile."],
        [["bunchcharge"], "Bunch charge of the electron beam."],
        [["emitt"], "Normalized emittance of the electron beam."],
        [["espread", "echirp"], "Energy spread and chirp of the electron beam."],
        [["eta"], "Dispersion functions of the electron beam."],
        [["pkcurr"], "Peak current of the electron beam evaluated from relevant parameters."],
        [["ebmsize","ediv"], "Beam size and angular divergence at the undulator entrance."],
        [["r56"], "Strength of the virtual dispersive section located in front of the undulator. Available if "+GetQString(SimplexOutput)+" is chosen for the electron bunch profile, and may be needed to simulate the HGHG/EEHG FELs"+(rst?"":(". Refer to "+GetLink(R56DriftLabel, R56DriftLabel, false)+" for details."))]
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [EBeamPrmsLabel], 
        [prmconts], 
        [""]);
}

function GetEBTypesTable(rst = false)
{
    let caption = "";
    let titles = ["Type", "Detail"];
    let details = [
        [GaussianBunch, "Distribution function in the 6D phase space is given by a 6D Gaussian function."],
        [BoxcarBunch, "Same as \""+GaussianBunch+"\", but the current profile is given by a boxcar function."],
        [SimplexOutput, "Macroparticles are loaded from the former simulation result."+(rst?"":(" To specify the former simulation, refer to "+GetLink(SPXOutLabel, SPXOutLabel, false)+"."))],
        [CustomCurrent, "Same as \""+GaussianBunch+"\", but the current profile is given by custom data."],
        [CustomSlice, "Same as \""+CustomCurrent+"\", but the slice parameters are given by custom data."],
        [CustomEt, "Same as \""+GaussianBunch+"\", but the profile in the (E-t) phase space is given by custom data."],
        [CustomParticle, "Beamlets are loaded from a data file that contains the particle distribution in the 6D phase space. The user should specify the path of the data in "+GetQString(EBeamPrmsLabel.partfile[0])+" and specify its format. Refer to "+GetLink(sections.pdata, sections.pdata, false)+" for details of how to specify the data format and how to verify its validity."]
    ];
    return GetTable(caption, titles, details);
}

function GetSeedTypesTable(rst = false)
{
    let caption = "";
    let titles = ["Type", "Detail"];
    let details = [
        [NotAvaliable, "No seed light is supposed."],
        [GaussianPulse, "Transform-limited Gaussian beam is supposed."],
        [ChirpedPulse, "Chirped Gaussian beam is supposed."],
        [SimplexOutput, "Radiation profiles are loaded from the former simulation result."]
    ];
    return GetTable(caption, titles, details);
}

function GetSeedPrmList(rst = false)
{
    let prmconts = [
        [["seedprofile"], "Type of the seed light"+(rst?"":(". For details, refer to "+GetLink(SeedTypeLabel, SeedTypeLabel, false)+"."))],
        [["pkpower"], "Peak power of the seed light."],
        [["relwavelen"], "Wavelength of the seed light relative to the undulator fundamental wavelength."],
        [["wavelen"], "Wavelength of the seed light."],
        [["pulseenergy", "pulselen"], "Pulse energy and pulse length of the seed light."],
        [["spotsize","raylen"], "Source size and Rayleigh length of the seed light."],
        [["waistpos"], "Longitudinal position where the seed light forms a beam waist"],
        [["CEP","gdd", "tod"], "Carrier envelope phase, group delay dispersion and third order dispersion of the seed light."]
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [SeedPrmsLabel], 
        [prmconts], 
        [""]);
}

function GetSPXPrmList(rst = false)
{
    let prmconts = [
        [["spxfile"], "Path to the output data file"],
        [["spxstep"], "Step index to retrieve the raw data of the former simulation, counted from the final step. For example, \"-1\" means that the raw data at the (N-1)-th step are used."],
        [["spxstepz"], "Longitudinal position corresponding to the above index."],
        [["driftrad"], "Length of the drift section between the exit of the former simulation and the entrance of the current one."],
        [["spxenergy"], "Fundamental energy used in the former simulation"],
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [ImportSPXOutLabel], 
        [prmconts], 
        [""]);
}

function GetUndPrmList(rst = false)
{
    let prmconts = [
        [["utype"], "Undulator type. "+(rst?"":(" For details, refer to "+GetLink(UndulatorType, UndulatorType, false)+"."))],
        [["K", "Kperp"], "Deflection parameter (K value) of the undulator. Note that "+UndPrmsLabel.Kperp[0]+" is defined as \\[K_{\\perp}=\\sqrt{K_x^2+K_y^2}\\]"],
        [["epukratio"], "Specifies the ratio of the horizontal and vertical K values."],
        [["multiharm"], "Arrange the harmonic components of "+GetQString(MultiHarmUndLabel)+"."+(rst?"":(" For details, refer to "+GetLink(MultiHarmUndLabel, MultiHarmUndLabel, false)+".")), true],
        [["lu"], "Magnetic Period Length of the undulator"],
        [["length", "segments", "interval"], "Parameters to specify the undulator line, which is supposed to be composed of several segments and drift sections in between."+(rst?"":(" For details, refer to "+GetLink(UndulatorLine, UndulatorLine, false)+"."))],
        [["peakb"], "Peak field of the undulator evaluate from the K value"],
        [["periods"], "Number of undulator periods/segment"],
        [["slippage"], "Number of slippage in the drift section"],
        [["exslippage"], "Extra slippage in the drift section"],
        [["taper"], "Type of undulator taper."+(rst?"":(" For details, refer to "+GetLink(TaperTypeLabel, TaperTypeLabel, false)+"."))],
        [["umodel"], "Type of undulator model."+(rst?"":(" For details, refer to "+GetLink(UModelTypeLabel, UModelTypeLabel, false)+"."))]
    ];

    let taperconts = [
        [["opttype"], "Specifies how to optimize the taper rate."+(rst?"":(" For details, refer to "+GetLink(TaperOptType, TaperOptType, false)+"."))],
        [["slicepos"], "Target slice position for taper optimization"],
        [["initial","incrseg","base","incrtaper"], "Four parameters to specify the undulator taper. For details, refer to "+(rst?"":(GetLink(HowToTaper, HowToTaper, false)+"."))],
        [["Kexit"], "K value at the exit of the undulator"],
        [["detune"], "Detuning at the exit of the undulator"],
    ];

    let umodelconts = [
        [["umautoseed"], "If enabled, seed number for the random number generator is automatically determined"],
        [["umrandseed"], "Seed number for the random number generator to model the undulator error"],
        [["phaseerr"], "RMS phase error"],
        [["berr"], "RMS field deviation"],
        [["xyerr"], "RMS trajectory error"],
        [["allsegment"], "Apply the error to all the segments"],
        [["segment"], "Target segment number to apply the error"]
    ];

    if(rst){
        return [...prmconts,  ...taperconts, ...umodelconts];
    }

    return GetPrmListTable( 
        [UndPrmsLabel, UndPrmsLabel, UndPrmsLabel], 
        [prmconts, taperconts, umodelconts], 
        ["Main Parameters", "Undulator Taper Parameters", "Undulator Model Configurations"]);
}

function GetLatticePrmList(rst = false)
{
    let prmconts = [
        [["ltype"], "Type of the lattice."+(rst?"":(" Refer to "+GetLink(LatticeStrType, LatticeStrType, false)+" for details."))],
        [["qfg", "qdg"], "Field gradient of the quadrupole magnets."],
        [["qfl", "qdl"], "Length of the quadrupole magnets."],
        [["dist"], "Distance between the focusing and defocusing mangets."],
        [["lperiods",], "Number of FODO periods in a single undulator segment."],
        [["betaxy0", "alphaxy0"], "Initial Twiss parameters at the undulator entrance."],
        [["optbeta"], "Optimmum betatron function evaluate to maximize the saturation power."]
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [LatticePrmsLabel], 
        [prmconts], 
        [""]);
}

function GetWakePrmList(rst = false)
{
    let prmconts = [
        [["wakeon"], "Enables the wakefield"],
        [["aperture"], "Aperture of the surrounding beam duct"],
        [["resistive"], "Enables the resistive wall wakefield"],
        [["resistivity", "relaxtime"], "Resistivity and relaxation time of the wall material"],
        [["paralell",], "If enabled, a parallel-plate configuration is used for the resistive-wall wakefield"],
        [["roughness"], "Enables the wakefield induced by surface roughness"],
        [["height", "corrlen"], "Height and correlation length to specify the profile of the rough surface"],
        [["dielec"], "Enables the wakefield induced by a dielectric layer"],
        [["permit", "thickness"], "Permitivity and thickness of the dielectric layer"],
        [["dielec"], "Enables the space charge effect"],
        [["wakecustom"], "Enables the additional wakefield defined by custom data"],
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [WakePrmsLabel], 
        [prmconts], 
        [""]);
}

function GetAlignPrmList(rst = false)
{
    let prmconts = [
        [["ualign"], "Type of the undulator alignment error."+(rst?"":(" For details, refer to "+GetLink(AlignmentType, AlignmentType, false)+"."))],
        [["Ktol"], "RMS deviation of the K value"],
        [["sliptol"], "RMS deviation of the phase slip"],
        [["sigsegment"], "Specifies the offset of the K values and slippage for each segment"],
        [["BPMalign",], "Type of the BPM alignment error."+(rst?"":(" For details, refer to "+GetLink(AlignmentType, AlignmentType, false)+"."))],
        [["xytol"], "Tolerance of the BPM alignment"],
        [["alautoseed"], "If enabled, seed number for the random number generator is automatically determined"],
        [["alrandseed"], "Seed number for the random number generator to model the alignment errors"]
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [AlignErrorUPrmsLabel], 
        [prmconts], 
        [""]);
}

function GetChicanePrmList(rst = false)
{
    let prmconts = [
        [["chicaneon"], "Replaces a single undulator segment by a magnetic chiane composed of 4 identical bending magnets."],
        [["dipoleb", "dipolel", "dipoled"], "Field strength, length, and distance of the bending magnets"],
        [["offset","delay"], "Trajectory offset and time delay given by the chicane."],
        [["chpos"], "Undulator segment number to be replace by the chicane."],
        [["rearrange"], "If enabled, the macroparticles are rearranged so that the microbunches induced before the chicane are smeared out."],
        [["monotype"], "Type of the monochromator to be inserted in the chicane for the self-seeding scheme"+(rst?".":(" "+GetLink("selfseed", refidx.selfseed, false)+GetLink("sstrans", refidx.sstrans, false)+"."))],
        [["xtaltype"], "Type of the crystal for the monochromator"],
        [["monoenergy"], "Photon energy of the monochromator"],
        [["bragg"], "Bragg angle for the monochromator energy"],
        [["formfactor", "latticespace", "unitvol"], "Form factor, lattice constant, and unit cell volume of the crystal"],
        [["bandwidth"], "Bandwidth of the crystal monochromator"],
        [["xtalthickness"], "Thickness of the crystal"],
        [["reltiming"], "Arrival time of radiation with respect to the electron beam after the chicane"],
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [ChicanePrmsLabel], 
        [prmconts], 
        [""]);
}

function GetDispersionPrmList(rst = false)
{
    let prmconts = [
        [["einjec"], "Enables the injection error of the electron beam."],
        [["exy", "exyp"], "Positional and anglular offset of the electron beam at the undulator entrance."],
        [["kick"], "Adds a single kick at a certain position in the undulator line."],
        [["kickpos","kickangle"], "Longitudinal position and angle of the single kick."],
        [["sinjec"], "Enables the injection error of the seed light."],
        [["sxy", "sxyp"], "Positional and anglular offsets of the seed light at the undulator entrance."]
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [DispersionPrmsLabel], 
        [prmconts], 
        [""]);
}

function GetSimCtrlPrmList(rst = false)
{
    let prmconts = [
        [["simmode"], "Selects the simulation mode."+(rst?"":(" Refer to "+GetLink(SimCtrlsPrmsLabel.simmode[0], SimCtrlsPrmsLabel.simmode[0], false)+"."))],
        [["simoption"], "Enables a special numerical algorithm to reduce the number of macropaticles needed to obtain a resliable simulation result."],
        [["autostep"], "The longitudinal step to solver the FEL equation is automatically determined based on the approximate gain length."],
        [["autoseed"], "If enabled, seed number for the random number generator is automatically determined"],
        [["randseed"], "Seed number for the random number generator to generate the macroparticles"],
        [["step"], "Longitudinal step normalized by the undulator period to solve the FEL equation."+(rst?"":(" Also refer to "+GetLink(IntegStepLabel, IntegStepLabel, false)+"."))],
        [["stepsseg"], "Steps in a single undulator segment"],
        [["driftsteps"], "Steps in a single drift section"],
        [["beamlets","particles"], "Total number of beamlets and number of macroparticles in a single beamlet."+(rst?"":(" For details, refer to "+GetLink(BeamletStrLabel, BeamletStrLabel, false)+"."))],
        [["slicebmlets", "slicebmletsss"], "Maximum number of beamlets in a single slice"],
        [["maxharmonic"], "Maximum harmonic number to be considered"],
        [["spatwin"], "Specifies the spatial range to evaluate the radiation field"],
        [["gpointsl","gpoints"], "Specifies the number of spatial grid points"],
        [["simrange"], "Temporal window of the electron bunch"],
        [["simpos"], "Slice position in the electron bunch"],
        [["slices"], "Total number of slices"],
        [["enablempi"], "Enables the parallel computing by MPI. Note that MPI environment should be installed (Open MPI for LINUX and macOS, MS-MPI for MS-Windows) and path to mpiexec should be set."],
        [["mpiprocs"], "Number of MPI processes"]
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [SimCtrlsPrmsLabel], 
        [prmconts], 
        [""]);
}

function GetSimTypeTable(rst = false)
{
    let caption = "";
    let titles = ["Type", "Detail"];
    let details = [
        [SSLabel, "The simulation is performed in a steady-state mode."],
        [TimeDepLabel, "The simulation is performed in a time-dependent mode."],
        [CyclicLabel, "As the above, but the radiation field slipped out of the head of the temporal window of the electron bunch is reused, namely shifted to the tail. This is convenient when doing a simulation in a limited temporal window of a long electron bunch."]
    ];
    return GetTable(caption, titles, details);
}

function GetSimOptionTable(rst = false)
{
    let caption = "";
    let titles = ["Type", "Detail"];
    let details = [
        [NotAvaliable, "No option is used."],
        [SmoothingGauss, "Apply a method to accelerate the numerical convergence in FEL simulations"+(rst?".":(" "+GetLink("tmethod", refidx.tmethod, false)+"."))],
        [KillQuiteLoad, "Turn off the quiet loading scheme to model the shot noize "+(rst?"":GetLink("shotnoise", refidx.shotnoise, false))+"."],
        [KillShotNoize, "Artifically disable the shot noize effect; the macroparticles are longitudinally arranged with a regular interval and thus no radiation (including spontaneous one) is initially generated."],
        [RealElectronNumber, "Use the real number of electrons, which are randomly distributed in the longitudinal direction."]
    ];
    if(rst){
        return prmconts;
    }
    return GetTable(caption, titles, details);
}

function GetDataDumpPrmList(rst = false)
{
    let prmconts = [
        [["temporal","spectral","spatial","angular"], "Specifies if the related radiation profiles are saved in the output JSON file."],
        [["profstep"], "Step interval to evaluate the above profiles. Note the results at the final step are always exported. For example, data export is done at the steps of the 1st, 4th, ... 97th and 100th, if the total number of steps is 100 and this parameter is set at 3.", true],
        [["particle"], "Saves the macroparticle raw data in a binary file (*.par)."],
        [["radiation"], "Saves the radiation raw data in a binary file (*.fld)."],
        [["expstep"], "Specifies the steps to save the raw data."+(rst?"":(" For details, refer to "+GetLink(RawDataDumpType, RawDataDumpType, false)+"."))],
        [["iniseg","segint"], "Initial segment and segment interval to save the raw data."],
        [["stepinterv"], "Step interval to save the raw data, if "+GetQString(RegularIntSteps, RegularIntSteps, false)+" is chosen for "+GetQString(DataOutPrmsLabel.expstep[0], DataOutPrmsLabel.expstep[0], false)+(rst?".":(". Note the results at the final step are always exported as explained "+GetLink(DataOutPrmsLabel.profstep[0], DataOutPrmsLabel.profstep[0], false)+". In practice, too fine step interval is not recommended, because the file size to store the raw data can be huge."))],
        [["pfilesize", "rfilesize"], "Approximate file size of the birary file to save the raw data."]
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [DataOutPrmsLabel], 
        [prmconts], 
        [""]);
}

function GetOutFilePrmList(rst = false)
{
    let prmconts = [
        [["folder", "prefix", "serial"], "Input the path to the output JSON file in [Folder], a prefix text in [Prefix], and a serial number in [Serial Number]. The data name is given as [Folder]/[Prefix]-[Serial Number], like \"/Users/data/test-1\", where \"/Users/data\", \"test\", and 1 refer to [Folder], [Prefix] and [Serial Number]. Note that the serial number can be -1 (negative), in which case it is not attached to the data name."]
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [OutputOptionsLabel], 
        [prmconts], 
        [""]);
}

function GetFELPrmList(rst = false)
{
    let prmconts = [
        [["shotnoize"], "Power of the shot noise to launch the SASE amplification process"],
        [["rho"], "Pierce parameter"+(rst?".":("; refer to "+GetLink("rhooc", refidx.rhooc, false)+" for details"))],
        [["Lg"], "Gain length evaluated with an analytical formula under 1D approximation (1D), and with a more rigorous expression to consider adverse effects (3D)"+(rst?".":(GetLink("scaling", refidx.scaling, false)+" for details"))],
        [["psat","Lsat"], "Satulation power and undulator length to reach saturation"],
        [["pulseE"], "Pulse energy at the saturation"],
        [["e1st","l1st"], "Fundamental photon energy and wavelength"],
        [["bandwidth"], "Bandwidth of the FEL radiation"+(rst?".":("; refer to "+GetLink("felbook", refidx.felbook, false)+" for details."))],
        [["Sigxy","Sigxyp"], "RMS source size and angular divergence of the FEL radiation"]
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [FELPrmsLabel], 
        [prmconts], 
        [""]);
}

function GetMbunchPrmList(rst = false)
{
    let prmconts = [
        [["mbparticles"], "Number of macroparticles per fundamental wavelength"],
        [["mbaccinteg"], "Accuracy of integration to evaluate the current profile. Given by a positive integer; the larger the more accurate."],
        [["iscurrent"], "Evaluate the current profile"],
        [["isEt"], "Evaluate the density in the (E,t) phase space"],
        [["mbtrange"], "Temporal range to evaluate the current and E-t profiles"],
        [["tpoints"], "Number of points per fundamental wavelength to evaluate the current and E-t profiles"],
        [["erange"], "Energy range to evaluate the E-t profile"],
        [["epoints"], "Number of energy points to evaluate the E-t profile"],
        [["mbr56"], "Longitudinal dispersion of a virtual chicane to be positioned after the undulator"],
        [["isoptR56","nr56"], "If enabled, the longitudinal dispersion is given by R<sub>56</sub>=r&times;r<sub>56</sub> where r<sub>56</sub> is the dispersion to maximize the density modulation (peak current) to be automatically determined, while r is the normalized value that can be adjusted by the user."],
        [["mbsegments"], "Number of undulator segments to be used for the numerical evaluation"],
        [["wpulse"], "If enabled, another seed pulse with similar properties is supposed"],
        [["relwavelen2"], "Relative wavelength of the 2nd seed pulse"],
        [["CEP2"], "Carrier envelope phase of the 2nd seed pulse"],
        [["gdd2"], "Groupd delay dispersion of the 2nd seed pulse"],
        [["tod2"], "Third order dispersion of the 2nd seed pulse"],
        [["timing2"], "Relative timing of the the 2nd seed pulse"],
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [EvalMBunchLabel], 
        [prmconts], 
        [""]);
}

function GetOptBetaPrmList(rst = false)
{
    let prmconts = [
        [["betamethod"], "Target of optimization. "+GetQString(PPBetaOptQgrad)+" optimizes both of the quadrupole strength and initial Twiss parameters, while "+GetQString(PPBetaOptInitial)+" does the Twiss parameters alone, without changing the qudrupole strength from the current value."],
        [["avbetaxy"], "Target average betatron functions. After the optimization process, they are updated by the actual values given by the quadrupole strengths and initial Twiss parameters determined by the optimization, and thus are not necessarily the same as the input values."],
        [["tolbeta"], "Optimization tolerance of the average betatron function"],
        [["cqfg","cqdg","cbetaxy0","calphaxy0"], "Quadrupole strengths and initial Twiss parameters determined by the optimization process. Note that these values, which are shown upon completion of the optimization process"+(rst?".":(", are automatically copied to the same parameters in "+GetLink(LatticeLabel, LatticeLabel, false)+" parameter list."))]
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [PreProcessPrmLabel], 
        [prmconts], 
        [""]);
}

function GetPlotOptPrmList(rst = false)
{
    let prmconts = [
        [["normalize"], "Select the normalization scheme for animation plots. "+GetQString(ForEachLabel)+" means that the y(z) axis is normalized for each slide, while "+GetQString(ByMaxLabel)+" means that it is normalized by a maximum value through the whole slides."],
        [["xscale", "yscale"], "Select the linear/log scale for x and y axes."],
        [["type"], "Select the plot type for the 1D plot."],
        [["size"], "Select the symbol size for the 1D plot."],
        [["width"], "Select the line width for the 1D plot."],
        [["type2d"], "Select the plot type for the 2D plot."],
        [["shadecolor"], "Select the color of the surface plot."],
        [["colorscale"], "Select the color scale pattern of the surface plot."],
        [["showscale"], "Enable the color scale."],
        [["wireframe"], "Add a wire frame on the surface plot."]
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [PlotOptionsLabel], 
        [prmconts], 
        [""]);
}

function GetPPrawOptPrmList(rst = false)
{
    let prmconts = [
        [["item"], "Target item to be evaluate by "+RawDataProcLabel],
        [["realimag"], "Select real/imaginary component for an item given by a complex number"],
        [["Exy"], "Select horizontal/vertical component for the radiation field"],
        [["s1","s2","s3"], "If enabled, relevant Stoke parameters are evaluated"],
        [["harmonic"], "Target harmonic number"],
        [["zone"], "Select the observation zone (near or far field)"],
        [["coord"], "Select the coordinates to retrieve the macroparticle data"],
        [["zrange","timerange","energyrange","spatrange","anglrange"], "Select how to specify the range of interest (ROI) for respective variables. "+GetQString(PostPIntegFullLabel)+" means that the whole range used in the simulation is assumed, while "+GetQString(PostPIntegPartialLabel)+" put a window on the ROI."],
        [["zwindow","zvalue"], "Range of the step and corresponding range of the longitudinal coordinate (z)"],
        [["timewindow","timevalue"], "Range of the slice and corresponding range of the bunch position (s)"],
        [["energywindow","energyvalue"], "Range of the photon energy"],
        [["spatwindow","spatvalue"], "Half range of the transverse position"],
        [["anglrange","anglvalue"], "Half range of the observation angle"],
        [["alongs","overxy","overxyf"], "Enable integration over the ROI"],
        [["r56pp"], "Virtual longitudinal dispersion to be added after each step. This is convenient to evaluate the reasonable R</sub>56</sub> to enhance the microbunching."],
        [["serialpp"], "Serial number to be attached to the data file to save the post-processed data."],
    ];

    if(rst){
        return prmconts;
    }
    return GetPrmListTable( 
        [PostProcessPrmLabel], 
        [prmconts], 
        [""]);
}

function GetOutDataInf(rst = false)
{
    let caption = "Format of an object to save the simulation result";
    let titles = ["Key", "Details", "Format"];
    let outdata = [
        [DataDimLabel, "Dimension of the data, or the number of independent variables.", "number"],
        [DataTitlesLabel, "Titles of individual arrays included in the "+GetQString(DataLabel)+" object.", "array (1D)"],
        [UnitsLabel, "Units of individual arrays included in the "+GetQString(DataLabel)+" object.", "array (1D)"],
        [DetailsLabel, "Additional information of the 3D-array data, which is generated in several calculation types. For example, those with "+GetQString(MenuLabels.tgtharm)+" (flux specific to a specific harmonic) result in a number of data, each of which is 2D and corresponds to the harmonic number.", "array (1D)"],
        [DataLabel, "Main body of the calculation result data.", "array (2D or 3D)"]
    ];
    if(rst){
        return {caption:caption, titles:titles, data:outdata};
    }
    return GetTable(caption, titles, outdata);
}

var NoInput = {
    [EBLabel]: [
        EBeamPrmsLabel.partspec[0],
        EBeamPrmsLabel.basespec[0],
        EBeamPrmsLabel.bunchbeta[0],
        EBeamPrmsLabel.bunchalpha[0]    
    ],
    [SeedLabel]: [
        SeedPrmsLabel.wavelen[0],
        SeedPrmsLabel.pulseenergy[0],
        SeedPrmsLabel.raylen[0],
        SeedPrmsLabel.stplen[0],
        SeedPrmsLabel.chirprate[0]
    ],
    [SPXOutLabel]: [
        ImportSPXOutLabel.spxstepz[0]
    ],
    [UndLabel]: [
        UndPrmsLabel.peakb[0],
        UndPrmsLabel.periods[0],
        UndPrmsLabel.slippage[0],
        UndPrmsLabel.udata[0]  
    ],
    [WakeLabel]: [        
    ],
    [LatticeLabel]: [
        LatticePrmsLabel.optbeta[0]
    ],
    [AlignmentLabel]: [        
    ],
    [ChicaneLabel]: [
        ChicanePrmsLabel.dipoleb[0],
        ChicanePrmsLabel.dipolel[0],
        ChicanePrmsLabel.dipoled[0],
        ChicanePrmsLabel.offset[0],
        ChicanePrmsLabel.bragg[0],
        ChicanePrmsLabel.bandwidth[0]
    ],
    [DispersionLabel]: [
    ],
    [SimCondLabel]: [
        SimCtrlsPrmsLabel.stepsseg[0],
        SimCtrlsPrmsLabel.driftsteps[0],
        SimCtrlsPrmsLabel.slicebmlets[0],
        SimCtrlsPrmsLabel.slicebmletsss[0],
        SimCtrlsPrmsLabel.gpointsl[0],
        SimCtrlsPrmsLabel.gpoints[0],
        SimCtrlsPrmsLabel.slices[0]
    ],
    [DataDumpLabel]: [
        DataOutPrmsLabel.pfilesize[0],
        DataOutPrmsLabel.rfilesize[0]            
    ],
    [OutFileLabel]: [OutputOptionsLabel.comment[0]],
    [PostPLabel]: []
}

NoInput[FELLabel] = [];
Object.keys(FELPrmsLabel).forEach(key => {
    if(key != "e1st" && key != "l1st"){
        NoInput[FELLabel].push(FELPrmsLabel[key][0]);
    }
});

function GetEBPrmTable()
{
    let tbl = new EBPrmOptions();
    let data = tbl.GetReferenceList(EBeamPrmsOrder, NoInput[EBLabel]);
    return data;
}

function GetSeedPrmTable()
{
    let tbl = new SeedPrmOptions();
    let data = tbl.GetReferenceList(SeedPrmsOrder, NoInput[SeedLabel]);
    return data;
}

function GetSPXPrmTable()
{
    let tbl = new SPXOutPrmOptions();
    let data = tbl.GetReferenceList(ImportSPXOutOrder, NoInput[SPXOutLabel]);
    return data;
}

function GetUndPrmTable()
{
    let tbl = new UndPrmOptions();
    let data = tbl.GetReferenceList(UndPrmsOrder, NoInput[UndLabel]);
    return data;
}

function GetLatticePrmTable()
{
    let tbl = new LatticePrmOptions();
    let data = tbl.GetReferenceList(LatticePrmsOrder, NoInput[LatticeLabel]);
    return data;
}

function GetWakePrmTable()
{
    let tbl = new WakePrmOptions();
    let data = tbl.GetReferenceList(WakePrmsOrder, NoInput[WakeLabel]);
    return data;
}

function GetAlignPrmTable()
{
    let tbl = new AlignUPrmOptions();
    let data = tbl.GetReferenceList(AlignErrorPrmsOrder, NoInput[AlignmentLabel]);
    return data;
}

function GetChicanePrmTable()
{
    let tbl = new ChicanePrmOptions();
    let data = tbl.GetReferenceList(ChicanePrmsOrder, NoInput[ChicaneLabel]);
    return data;
}

function GetDispersionPrmTable()
{
    let tbl = new DispersionPrmOptions();
    let data = tbl.GetReferenceList(DispersionPrmsOrder, NoInput[DispersionLabel]);
    return data;
}

function GetSimCtrlPrmTable()
{
    let tbl = new SimCtrlPrmOptions();
    let data = tbl.GetReferenceList(SimCtrlsPrmsOrder, NoInput[SimCondLabel]);
    return data;
}

function GetDataDumpPrmTable()
{
    let tbl = new OutDataPrmOptions();
    let data = tbl.GetReferenceList(DataOutPrmsOrder, NoInput[DataDumpLabel]);
    return data;
}
//----- python -----

function GetMenu(baseobj)
{
    let data = "";
    for(let j = 0; j < baseobj.length; j++){
        let subsections = Object.values(baseobj[j])[0];
        let isobj = false;
        for(let i = 0; i < subsections.length; i++){
            if(typeof subsections[i] != "string" 
                    && Array.isArray(subsections[i]) == false){
                isobj = true;
                continue;
            }
        }
        if(!isobj){
            let div = document.createElement("div");
            div.appendChild(GetLink(Object.keys(baseobj[j])[0], Object.keys(baseobj[j])[0], true));
            data += div.outerHTML;
            continue;
        }
        let details = document.createElement("details");
        let summary = document.createElement("summary");
        summary.innerHTML = Object.keys(baseobj[j])[0];
        details.appendChild(summary);
        let list = document.createElement("ul");
        for(let i = 0; i < subsections.length; i++){
            let item = document.createElement("li");
            if(typeof subsections[i] == "string"){
                continue;
            }
            let link = GetLink(Object.keys(subsections[i])[0], Object.keys(subsections[i])[0], true);
            item.appendChild(link);
            list.appendChild(item);
        }
        details.appendChild(list);
        data += details.outerHTML;
    }  
    return data;
}

function GetFileMenu()
{
    let caption = "Contents of \"File\" main menu.";
    let titles = ["Menu", "Details"];
    let filemenus = [
        [FileOpen, "Open a SIMPLEX parameter file. Although those for older (&lE; 2.1) versions are automatically converted to the new format, the user is strongly recommended to check if the conversion is OK."],
        [FileSave, "Save all the parameters and options in the current file."],
        [FileSaveAs, "Save all the parameters and options in a new file."],
        [FileImportOut, "Import the former simulation results for visualization."],
        [FileImportPP, "Import the former post-processred results for visualization", FileImportPP],
        [FileExit, "Quit SIMPLEX and Exit"]
    ];
    return GetTable(caption, titles, filemenus);
}

function GetRunMenu()
{
    let caption = "Contents of \"Run\" main menu";
    let titles = ["Menu", "Details"];
    let filemenus = [
        [CalcProcessLabel, "Create a simulation process with the current parameters and options."],
        [ExportConfigLabel, "Export the current parameters and options to a file, or download it (web-application mode), which can be used as an input file to directly call the solver."],
        [StartCalcLabel, "Start a new simulation, or launch the simulation process."]
    ];
    return GetTable(caption, titles, filemenus);
}

function GetReference(refidx)
{
    let reflists = [
        {
            simplexjsr: "T. Tanaka, \"SIMPLEX: SIMulator and Postprocessor for free electron Laser EXperiments,\" J. Synchrotron Radiation 22, 1319 (2015)"
        },
        {
            rhooc: "R. Bonifacio, C. Pellegrini and L. M. Narducci, \"Collective instabilities and high-gain regime in a free electron laser,\" Optics Communications, 50 (1984) 373"
        },
        {
            felbook: "E. L. Saldin, E. A. Schneidmiller and M. V. Yurkov, The Physics of Free Electron Lasers, Springer, 2000"
        },
        {
            scaling: "M. Xie, \"Exact and variational solutions of 3D eigenmodes in high gain FELs,\" Nucl. Instrum. Meth. A445 (2000) 59"
        },
        {
            resistive: "K. L. F. Bane and G. Stupakov, \"Resistive wall wakefield in the LCLS undulator beam pipe,\" SLAC-PUB-10707 (2004)"
        },
        {
            rough1: "G. V. Stupakov, \"Impedance of small obstacles and rough surfaces,\" Phys. Rev. ST-AB, 1 (1998) 064401"
        },
        {
            rough2: "G. V. Stupakov, \"Surface roughness impedance,\" Proc. ICFA Workshop on Phys. Sci. X-ray FEL, 2000"
        },
        {
            synchro: "G. V. Stupakov, \"Surface impedance and synchronous modes,\" Workshop on Instabilities of High Intensity Hadron Beams in Rings, 1999"
        },
        {
            spcharge: "M. Venturini, \"Models of longitudinal space-charge impedance for microbunching instability,\" Phys. Rev. ST-AB 11, 034401 (2008)"
        },
        {
            selfseed: "J. Feldhaus et al., \"Possible application of X-ray optical elements for reducing the spectral bandwidth of an X-ray SASE FEL,\" Optics Comm., 140 (1997) 341"
        },
        {
            sstrans: "G. Geloni, V. Kocharyan and E. Saldin, \"A novel self-seeding scheme for hard x-ray FELs,\" J. Mod. Optics, 58 (2011) 1391"
        },
        {
            tmethod: "T. Tanaka \"Accelerating the convergence of free electron laser simulations by retrieving a spatially-coherent component of microbunching,\" arXiv:2310.20197"
        },
        {
            shotnoise: "W. M. Fawley, \"Algorithm for loading shot noise microbunching in multidimensional free-electron laser simulation codes,\" Phys. Rev. ST-AB, 5 (2002) 070701"
        },
        {
            refperr: "R. Walker, \"Interference effects in undulator and wiggler radiation sources\", Nucl. Instrum. Methods Phys. Res., Sect. A 335, 328 (1993)"
        }
    ];
    let refol = document.createElement("ol")
    refol.className = "paren";
    for(let j = 0; j < reflists.length; j++){
        let refi = document.createElement("li");
        let keys = Object.keys(reflists[j]);
        refi.innerHTML = reflists[j][keys[0]];
        refi.id = keys[0];
        refol.appendChild(refi);
        refidx[keys[0]] = "["+(j+1).toString()+"]";
    }
    return refol.outerHTML;
}

function GetPPAvailTable()
{
    let titles = ["Name", "Detail", "Plot Type"];
    let details = [
        [GainCurveLabel, "Values integrated over the whole electron bunch, such as the pulse energy of radiation and bunch factor, evaluated as a function of the longitudinal position along the undulator line.", "1D"],
        [TempProfileLabel, "Radiation power integrated over the whole solid angle vs. the bunch,", "1D animation"],
        [SpecProfileLabel, "Spectrum of radiation integrated over the whole solid angle.", "1D animation"],
        [SpatProfileLabel, "Spatial profile of radiation integrated over the whole slice.", "2D animation"],
        [AnglProfileLabel, "Angular profile of radiation integrated over the whole slice. Note that the angular coordinate is normalized by the reciprocal of a harmonic order. Namely, it is given as h&times;&theta, where h is the harmonic order.", "2D animation"],
        ["Processed [s/n]: *", "Result of "+GetLink(RawDataProcLabel, RawDataProcLabel, false)+". \"s/n\" stands for the serial number specified by the user (optional), and * means the target item for post-processing.", "Depends on the configurations of "+RawDataProcLabel]
    ];
    return GetTable("", titles, details);
}

function GetUndulatorType()
{
    let caption = "";
    let titles = ["Type", "Details", "Radiation Field for Simulation"];
    let outdata = [
        [LinearUndLabel, "Conventional linear undualtor with a vertical magnetic filed to generate 100% linearly polarized radiation.", "Scalar: E<sub>x</sub>"],
        [HelicalUndLabel, "Helical undulator to generate 100% circularly polarized radiation.", "Scalar: E<sub>x</sub>+iE<sub>y</sub>"],
        [EllipticUndLabel, "Elliptical undulator to generate elliptically polarized radiation.", "Vector: (E<sub>x</sub>, E<sub>y</sub>)"],
        [MultiHarmUndLabel, "Special undulator generating a magnetic field composed of multiple harmonic components.", "Vector: (E<sub>x</sub>, E<sub>y</sub>)"]
    ];
    return GetTable(caption, titles, outdata);
}

function GetTaperType()
{
    let caption = "";
    let titles = ["Type", "Details"];
    let outdata = [
        [NotAvaliable, "Tapering is not applied."],
        [TaperStair, "Each undulator segment cannot be tapered; the K value is constant within a single segment and jumps at the entrance of the next segment."],
        [TaperContinuous, "Each undulator segment can be tapered; the K value changes gradually from the entrance to the exit in a single segment, and thus the K value varies continuously along the undulator."],
        [TaperCustom, "Customize the K value offset and slope for each segment."]
    ];
    return GetTable(caption, titles, outdata);
}

function GetUMType()
{
    let caption = "";
    let titles = ["Type", "Details"];
    let outdata = [
        [IdealLabel, "Magnetic fields of all the undulator segments are ideal."],
        [SpecifyErrLabel, "Specify the magnetic field errors."],
        [ImportDataLabel, "Use the field distribution given by custom data. To import the custom data, refer to "+GetLink(sections.udata, sections.udata, false)+"."]
    ];
    return GetTable(caption, titles, outdata);
}

function GetTaperOptType()
{
    let caption = "";
    let titles = ["Type", "Details"];
    let outdata = [
        [NotAvaliable, "Optimization is not applied."],
        [TaperOptWake, "Besides what is specified by the user, additional tapering is applied to compensate for the energy loss by the wakefield evaluated at the target slice position."],
        [TaperOptWhole, "The taper rate is automatically determined to compensate for the energy loss in the whole electron bunch."],
        [TaperOptSlice, "The taper rate is automatically determined to compensate for the energy loss at the target slice position."]
    ];
    return GetTable(caption, titles, outdata);
}

function GetAlignmentType()
{
    let caption = "";
    let titles = ["Type", "Details"];
    let outdata = [
        [IdealLabel, "All the components are aligned perfectly."],
        [TargetOffsetLabel, "K values and slippage values of target undulator segments are misaligned."],
        [TargetErrorLabel, "Related components are aligned with a specific tolerance."]
    ];
    return GetTable(caption, titles, outdata);
}

function GetRawExportType()
{
    let caption = "";
    let titles = ["Type", "Details"];
    let outdata = [
        [DumpSegExitLabel, "Export at the exit of every undulator segments."],
        [DumpSpecifyLabel, "Export at the exit of specified undulator segments."],
        [DumpUndExitLabel, "Export once at the exit of the undulator line."],
        [RegularIntSteps, "Export with a regular step interval. Note that data at the final step is always exported.", RegularIntSteps]
    ];
    return GetTable(caption, titles, outdata);
}

function GetOutputFormat()
{
    let caption = "Format of the objects in the output JSON file";
    let titles = ["Key", "Details", "Format"];
    let outdata = [
        [DataDimLabel, "Dimension of the data", "number"],
        [VariablesLabel, "Number of independent variables for each sliced data. If "+GetQString(DataDimLabel)+" is 3 and "+GetQString(VariablesLabel)+" is 2, then the 2D data (for example, spatial profile of radiation) was generated repeatedly at each step. These conditions are used later for visualization", "number"],
        [DataTitlesLabel, "Titles of individual arrays included in the "+GetQString(DataLabel)+" object.", "array (1D)"],
        [UnitsLabel, "Units of individual arrays included in the "+GetQString(DataLabel)+" object.", "array (1D)"],
        [DataLabel, "Main body of the simulation result data.", "array (2D or 3D)"]
    ];
    return GetTable(caption, titles, outdata);
}

function GetFldFormat()
{
    let caption = "Numbers";
    let titles = ["Notation", "Details", "Related Parameter"];
    let outdata = [
        ["L", "Number of longitudinal steps where the binary data are exported.", "\"Output Steps\" in "+GetLink(DataDumpLabel, DataDumpLabel, false)],
        ["M", "Number of slices over the whole electron bunch.", "\"Total Slices\" in "+GetLink(SimCondLabel, SimCondLabel, false)],
        ["N", "Number of transverse grid points. Common to horizontal and vertical directions.", "\"Grid Points\" in "+GetLink(SimCondLabel, SimCondLabel, false)],
        ["B", "Number of beamlets.", "\"Total Beamlets\" in "+GetLink(SimCondLabel, SimCondLabel, false)],
        ["P", "Number of macroparticles per beamlet.", "\"Particles/Beamlet\" in "+GetLink(SimCondLabel, SimCondLabel, false)]
    ];
    return GetTable(caption, titles, outdata);
}


var FileOpen;
var FileSave;
var FileSaveAs;
var FileImportOut;
var FileImportPP;
var FileExit;
var CalcProcessLabel;
var ExportConfigLabel;
var StartCalcLabel;
var TabEBSeed;
var TabUnd;
var TabOption
var TabSimCtrl;
var TabPreProp;
var TabPostProp;
var DivFELPrms;
var TabPPView;
var BtnRunPP;
const BrowseLabel = "Browse"
const EditUnitsLabel = "Edit Units";
const ArrangeDataLabel = "Arrange the Output File";
const PPAvailType = "Available Data Type";
const UndulatorLine = "Undulator Line Parameters";
const UndulatorType = "Undulator Type";
const LatticeStrType = "Lattice Type";
const TaperTypeLabel = "Taper Type";
const UModelTypeLabel = "Undulator Models";
const TaperOptType = "Automatic Taper Optimization";
const HowToTaper = "How to Setup Tapering";
const R56DriftLabel = "Configuration to Use the Former Result";
const BeamletStrLabel = "Structure of a Beamlet";
const IntegStepLabel = "Integration Step";
const WakeImplementScheme = "Wakefield Evaluation";
const SeedTypeLabel = "Seed Type";
const AlignmentType = "How to Specify the Alignment Error";
const RawDataDumpType = "Steps to Export the Raw Data";
var Version2Digit = Version.split(".").slice(0, 2).join(".");

function ExportHelpFile()
{
    FileOpen = document.getElementById([MenuLabels.file, MenuLabels.open].join(IDSeparator)).innerHTML;
    FileSave = document.getElementById([MenuLabels.file, MenuLabels.save].join(IDSeparator)).innerHTML;
    FileSaveAs = document.getElementById([MenuLabels.file, MenuLabels.saveas].join(IDSeparator)).innerHTML;
    FileImportOut = document.getElementById([MenuLabels.file, MenuLabels.loadf].join(IDSeparator)).innerHTML;
    FileImportPP = document.getElementById([MenuLabels.file, MenuLabels.outpostp].join(IDSeparator)).innerHTML;
    FileExit = document.getElementById([MenuLabels.file, MenuLabels.exit].join(IDSeparator)).innerHTML;
    TabEBSeed = document.getElementById("ebeam-seed-tab").innerHTML;
    TabUnd = document.getElementById("undulatorline-tab").innerHTML;
    TabOption = document.getElementById("options-tab").innerHTML;
    TabSimCtrl = document.getElementById("simctrl-dump-tab").innerHTML;
    TabPreProp = document.getElementById("preproc-tab").innerHTML;
    TabPostProp = document.getElementById("postproc-tab").innerHTML;
    DivFELPrms = document.getElementById("felprm").innerHTML;
    CalcProcessLabel = document.getElementById([MenuLabels.run, MenuLabels.process].join(IDSeparator)).innerHTML;
    ExportConfigLabel = document.getElementById([MenuLabels.run, MenuLabels.export].join(IDSeparator)).innerHTML;
    StartCalcLabel = document.getElementById([MenuLabels.run, MenuLabels.start].join(IDSeparator)).innerHTML;  
    TabPPView = document.getElementById("postp-view-btn").innerHTML;
    BtnRunPP = document.getElementById("runpostp").innerHTML;
    
    let prmlabels = [EBeamPrmsLabel, SeedPrmsLabel, ImportSPXOutLabel, UndPrmsLabel, WakePrmsLabel, LatticePrmsLabel, ChicanePrmsLabel, AlignErrorUPrmsLabel, DispersionPrmsLabel, SimCtrlsPrmsLabel, DataOutPrmsLabel, FELPrmsLabel];
    let espchars = RetrieveAllEscapeChars(prmlabels);
    espchars.push("&uarr;");

    let baseobj = CopyJSON(GetHelpBody());
    let data =
    '<!DOCTYPE html>\n<html lang="en">\n<head>\n<title>Reference Manual for SIMPLEX '+Version2Digit+'</title>\n'
    +'<link rel="stylesheet" type="text/css" href="reference.css">\n'
    +"<script>MathJax = {chtml: {matchFontHeight: false}, tex: { inlineMath: [['$', '$']] }};</script>\n"
    +'<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>\n'
    +'</head>\n<body>\n'
    +'<div style="display: flex;">\n'
    +'<div class="sidemenu">\n'

    data += GetMenu(baseobj);

    data += '</div>\n<div class="main">';

    let cont = "";
    for(let j = 0; j < baseobj.length; j++){
        cont += WriteObject(0, baseobj[j]);
    }

    let contrep = cont 
        .replace("<p>@filemenu</p>", GetFileMenu())
        .replace("<p>@runmenu</p>", GetRunMenu())
        .replace("<p>@tabpanel</p>", GetTabPanelTable())
        .replace("<p>@plotlyedit</p>", GetPlotlyDialog())
        .replace("<p>@ebprm</p>", GetEBeamPrmList())
        .replace("<p>@ebtype</p>", GetEBTypesTable())
        .replace("<p>@seedtype</p>", GetSeedTypesTable())
        .replace("<p>@seedprm</p>", GetSeedPrmList())
        .replace("<p>@spxprm</p>", GetSPXPrmList())
        .replace("<p>@undprm</p>", GetUndPrmList())
        .replace("<p>@undtype</p>", GetUndulatorType())
        .replace("<p>@utapertype</p>", GetTaperType())
        .replace("<p>@umodeltype</p>", GetUMType())
        .replace("<p>@taperopttype</p>", GetTaperOptType())
        .replace("<p>@aligntype</p>", GetAlignmentType()) 
        .replace("<p>@rawexptype</p>", GetRawExportType()) 
        .replace("<p>@latticeprm</p>", GetLatticePrmList())
        .replace("<p>@wakeprm</p>", GetWakePrmList())
        .replace("<p>@alignprm</p>", GetAlignPrmList())
        .replace("<p>@chicaneprm</p>", GetChicanePrmList())
        .replace("<p>@dispprm</p>", GetDispersionPrmList())
        .replace("<p>@simctrlprm</p>", GetSimCtrlPrmList())
        .replace("<p>@datadumpprm</p>", GetDataDumpPrmList())
        .replace("<p>@outfpprm</p>", GetOutFilePrmList())
        .replace("<p>@felprm</p>", GetFELPrmList())
        .replace("<p>@mbunchprm</p>", GetMbunchPrmList())
        .replace("<p>@boptprm</p>", GetOptBetaPrmList())
        .replace("<p>@pprawprm</p>", GetPPrawOptPrmList())
        .replace("<p>@ploptprm</p>", GetPlotOptPrmList())
        .replace("<p>@ebjson</p>", GetEBPrmTable())
        .replace("<p>@seedjson</p>", GetSeedPrmTable())
        .replace("<p>@spxjson</p>", GetSPXPrmTable())
        .replace("<p>@undjson</p>", GetUndPrmTable())
        .replace("<p>@latticejson</p>", GetLatticePrmTable())
        .replace("<p>@wakejson</p>", GetWakePrmTable())
        .replace("<p>@alignjson</p>", GetAlignPrmTable())
        .replace("<p>@chicanejson</p>", GetChicanePrmTable())
        .replace("<p>@dispjson</p>", GetDispersionPrmTable())
        .replace("<p>@simctrljson</p>", GetSimCtrlPrmTable())
        .replace("<p>@simtype</p>", GetSimTypeTable())
        .replace("<p>@simoption</p>", GetSimOptionTable())
        .replace("<p>@dumpjson</p>", GetDataDumpPrmTable())
        .replace("<p>@preproc</p>", GetPreprocDetailTable())
        .replace("<p>@importpp</p>", GetImportDetailTable())
        .replace("<p>@ppavailtype</p>", GetPPAvailTable())
        .replace("<p>@outfmt</p>", GetOutputFormat())
        .replace("<p>@reference</p>", referencelist);

    data += FormatHTML(contrep);

    data += "</div>\n</body>\n";

    data = ReplaceSpecialCharacters(espchars, data);

    let blob = new Blob([data], {type:"text/html"});
    let link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = "reference.html";
    link.click();
    link.remove();
}

function ArrangeObjectTblTitle(tbl, rows)
{
    let cell;
    let titles = [["GUI Notation", ""], 
        ["Key", ["Full", "Simplified"]], ["Format", ""], ["Default", ""]];

    rows.push(tbl.insertRow(-1));
    for(let j = 0; j < titles.length; j++){
        cell = rows[rows.length-1].insertCell(-1);
        if(typeof titles[j][0] == "string"){
            cell.innerHTML = titles[j][0];
        }
        cell.className += " title";
        if(titles[j][0] == "Format"){
            cell.setAttribute("width", "200px");
        }
        if(typeof titles[j][1] == "string" && titles[j][1] == ""){
            cell.setAttribute("rowspan", "2");
        }
        else if(Array.isArray(titles[j][1])){
            cell.setAttribute("colspan", titles[j][1].length.toString());
        }
    }
    rows.push(tbl.insertRow(-1));
    for(let j = 0; j < titles.length; j++){
        if(Array.isArray(titles[j][1])){
            for(let i = 0; i < titles[j][1].length; i++){
                cell = rows[rows.length-1].insertCell(-1);
                cell.innerHTML = titles[j][1][i];
                cell.className += " title";
            }
        }
        else if(titles[j][1] != ""){
            cell = rows[rows.length-1].insertCell(-1);
            cell.innerHTML = titles[j][1];
            cell.className += " title";
        }
    }
}
