function WriteFigure(src, figcaption, pct)
{
    return "";
}

function GetLink(href, caption, isel, isURL)
{
    return "";
}

function GetDirectPara(txt)
{
    return txt;
}

function GetVersion2Digit()
{
    let vers = Version.split(".").slice(0, 2).join(".");
    return vers;
}

const Version2Digit = GetVersion2Digit();
const RemoteRepository = "https://spectrax.org/simplex/app/"+Version2Digit+"/index.html"
const HelpURL = "https://spectrax.org/simplex/app/"+Version2Digit+"/help/reference.html"
const PySampleURL = "https://spectrax.org/simplex/app/"+Version2Digit+"/python/samples.zip"

function GetBrowserIssue()
{
    let caption = "Web browsers supported in *simplex-ui* and known issues.";
    let titles = ["Browser", "Remarks/Issues"];
    let brdata = [
        ["Chrome", "Fully tested and most recommended."],
        ["Edge", "Recommended as well as Chrome."],
        ["Firefox", "Loading source files from the local repository may fail. In such a case, the user is requested to move them to another location."],
        ["Safari", "GUI cannot be operated, or it is not editable because frozen by the OS; it just shows the parameters and configurations, and plots the pre- and post-processed results."]
    ];
    return {caption:caption, titles:titles, data:brdata};
}

function GetPythonOption()
{
    let caption = "";
    let titles = ["Option", "Alternative", "Contents"];
    let brdata = [
        ["--chrome", "-c", "Specify Chrome (default) as the browser for GUI."],
        ["--edge", "-e", "Specify Edge as the browser for GUI."],
        ["--firefox", "-f", "Specify Firefox  as the browser for GUI."],
        ["--remote", "-r", "Use `remote repository <"+RemoteRepository+">`_ for the source file."],
        ["--local", "-l", "Use local repository (/path-to-python/site-packages/simplex/src/indx.html) for the source file."],
    ];
    return {caption:caption, titles:titles, data:brdata};
}

function GetUnitKey()
{
    let caption = "Arguments available in PreProcess.SetUnit()"
    let titles = ["Menu Items", "Arguments", "Options"];
    let data = [];
    for(const key of DataUnitsOrder){
        let label = DataUnitsLabel[key][0];
        let sel = DataUnitsLabel[key][1].join(", ");
        data.push([label, key, sel]);
    }
    return {caption:caption, titles:titles, data:data};
}

function GetDataProcess()
{
    let caption = "Arguments available in PostProcess.SetDataProcessing()"
    let titles = ["Menu Items", "Arguments", "Options"];
    let data = [];
    for(const key of DataUnitsOrder){
        let label = DataUnitsLabel[key][0];
        let sel = DataUnitsLabel[key][1].join(", ");
        data.push([label, key, sel]);
    }
    return {caption:caption, titles:titles, data:data};
}

function GetMenuCateg()
{
    let caption = "Arguments available in the function  "+GetQString("Set")+" to set a parameter."
    let titles = ["Arguments", "Remarks"];
    let data = [
        ["ebeam", "Parameters to specify the electron beam shown in "+EBLabel+" panel."],
        ["seed", "Parameters to specify the seed light shown in "+SeedLabel+" panel."],
        ["spxout", "Configurations to import the former simulation result shown in "+SPXOutLabel+" panel."],
        ["undulator", "Parameters to specify the undulator shown in "+UndLabel+" panel."],
        ["lattice", "Parameters to specify the lattice arrangement shown in "+LatticeLabel+" panel."],
        ["alignment", "Parameters to specify the alignment error in "+AlignmentLabel+" panel."],
        ["wake", "Parameters to specify the wake field shown in "+WakeLabel+" panel."],
        ["chicane", "Parameters to specify the chicane shown in "+ChicaneLabel+" panel."],
        ["dispersion", "Parameters to specify the dispersion function shown in "+DispersionLabel+" panel."],
        ["condition", "Parameters to specify the simulation conditions in "+SimCondLabel+" panel."],
        ["datadump", "Parameters to specify how to dump the simulation results shown in "+DataDumpLabel+" panel."],
        ["felprm", "Target photon energy or wavelength of radiation shown in "+FELLabel+" panel."],
        ["outfile", "Parameters to specify the output file shown in "+OutFileLabel+" panel."]
    ];
    return {caption:caption, titles:titles, data:data};
}

function GetFormat(prmlabel)
{
    let keys = Object.keys(prmlabel);
    let formats = {};
    for(const key of keys){
        if(Array.isArray(prmlabel[key][1])){
            if(prmlabel[key].length > 2 && prmlabel[key][2] == SelectionLabel){
                let selections = [];
                prmlabel[key][1].forEach((item) => {
                    if(typeof item == "object"){
                        selections = selections.concat(...Object.values(item));
                    }
                    else{
                        selections.push(item)
                    }
                })
                formats[key] = "string - one of below:<br>'"+selections.join("'<br>'")+"'";
            }
            else{
                formats[key] = "list";
            }
        }
        else if(prmlabel[key].length > 2 && prmlabel[key][2] == IntegerLabel){
            formats[key] = "int";
        }
        else if(prmlabel[key][1] == PlotObjLabel){
            formats[key] = "dictionary";
        }
        else if(prmlabel[key][1] == FileLabel){
            formats[key] = "str: path to the data file";
        }
        else if(prmlabel[key][1] == FolderLabel){
            formats[key] = "str: path to the directory";
        }
        else if(prmlabel[key][1] == GridLabel){
            formats[key] = "dictionary";
        }
        else if(prmlabel[key][1] == SimpleLabel){
            // do nothing
        }
        else if(typeof prmlabel[key][1] == "number"){
            formats[key] = "float";
        }
        else if(typeof prmlabel[key][1] == "boolean"){
            formats[key] = "bool";
        }
        else if(typeof prmlabel[key][1] == "string"){
            formats[key] = "str";
        }
    }
    return formats;
}

function GetParameterKey()
{
    let category = [EBLabel, SeedLabel, SPXOutLabel, UndLabel, LatticeLabel, AlignmentLabel, 
        WakeLabel, ChicaneLabel, DispersionLabel, SimCondLabel, DataDumpLabel, FELLabel, OutFileLabel,
        PostPLabel];
    let prmlabels = {};
    prmlabels[EBLabel] = [EBeamPrmsLabel, EBeamPrmsOrder];
    prmlabels[SeedLabel] = [SeedPrmsLabel, SeedPrmsOrder];
    prmlabels[SPXOutLabel] = [ImportSPXOutLabel, ImportSPXOutOrder];
    prmlabels[UndLabel] = [UndPrmsLabel, UndPrmsOrder];
    prmlabels[LatticeLabel] = [LatticePrmsLabel, LatticePrmsOrder];
    prmlabels[AlignmentLabel] = [AlignErrorUPrmsLabel, AlignErrorPrmsOrder];
    prmlabels[WakeLabel] = [WakePrmsLabel, WakePrmsOrder];
    prmlabels[ChicaneLabel] = [ChicanePrmsLabel, ChicanePrmsOrder];
    prmlabels[DispersionLabel] = [DispersionPrmsLabel, DispersionPrmsOrder];
    prmlabels[SimCondLabel] = [SimCtrlsPrmsLabel, SimCtrlsPrmsOrder];
    prmlabels[DataDumpLabel] = [DataOutPrmsLabel, DataOutPrmsOrder];
    prmlabels[FELLabel] = [FELPrmsLabel, FELPrmsOrder];
    prmlabels[OutFileLabel] = [OutputOptionsLabel, OutputOptionsOrder];
    prmlabels[PostPLabel] = [PostProcessPrmLabel, PostProcessPrmOrder];

    let categarg = {};
    categarg[EBLabel] = "ebeam";
    categarg[SeedLabel] = "seed";
    categarg[SPXOutLabel] = "spxout";
    categarg[UndLabel] = "undulator";
    categarg[LatticeLabel] = "lattice";
    categarg[AlignmentLabel] = "alignment";
    categarg[WakeLabel] = "wake";
    categarg[ChicaneLabel] = "chicane";
    categarg[DispersionLabel] = "dispersion";
    categarg[SimCondLabel] = "condition";
    categarg[DataDumpLabel] = "datadump";
    categarg[FELLabel] = "felprm";
    categarg[OutFileLabel] = "outfile";
    categarg[PostPLabel] = "dataprocess";

    let details = {};
    details[EBLabel] = GetEBeamPrmList(true);
    details[SeedLabel] = GetSeedPrmList(true);
    details[SPXOutLabel] = GetSPXPrmList(true);
    details[UndLabel] = GetUndPrmList(true);
    details[LatticeLabel] = GetLatticePrmList(true);
    details[AlignmentLabel] = GetAlignPrmList(true);
    details[WakeLabel] = GetWakePrmList(true);
    details[ChicaneLabel] = GetChicanePrmList(true);
    details[DispersionLabel] = GetDispersionPrmList(true);
    details[SimCondLabel] = GetSimCtrlPrmList(true);
    details[DataDumpLabel] = GetDataDumpPrmList(true);
    details[FELLabel] = GetFELPrmList(true);
    details[OutFileLabel] = GetOutFilePrmList(true);
    details[PostPLabel] = GetPPrawOptPrmList(true);

    let format = {};
    Object.keys(prmlabels).forEach((key) => {
        format[key] = GetFormat(prmlabels[key][0]);
    })

    let objects = {};

    for(const categ of category){
        let caption = "Keywords available in the 2nd argument (arg2) of Set(\""+categarg[categ]+
            "\", arg2, arg3) to change the parameters and options of "+categ+"."
        if(categ == PostPLabel){
            caption = "Keywords available in the 1st argument of PostProcess.SetDataProcessing()"
        }
        let titles = ["Notation in GUI", "Argument", "Detail", "Format"];
        let labels = {};
        for(const key of prmlabels[categ][1]){
            if(key == SeparatorLabel){
                continue;
            }
            if(prmlabels[categ][0][key][1] == SimpleLabel){
                continue;
            }
            let prm = prmlabels[categ][0][key][0];
            if(NoInput[categ].includes(prm)){
                continue;
            }
            labels[key] = prm;
        }

        let detobjs = {};
        for(let n = 0; n < details[categ].length; n++){
            for(i = 0; i < details[categ][n][0].length; i++){
                let desc = details[categ][n][1];
                if(Array.isArray(desc)){
                    desc = details[categ][n][1][0];
                }
                detobjs[details[categ][n][0][i]] = desc.replaceAll('"', '');
            }
        }
        
        let data = [];
        let keys = Object.keys(labels);
        for(let j = 0; j < keys.length; j++){
            let detail = "";
            if(detobjs.hasOwnProperty(keys[j])){
                detail = detobjs[keys[j]];
            }
            let fmt = "";
            if(format[categ].hasOwnProperty(keys[j])){
                fmt = format[categ][keys[j]];
            }
            let subel = [labels[keys[j]], keys[j], detail, fmt];
            data.push(subel);
        }
        objects[categ] = {caption:caption, titles:titles, data:data};
    }
    return objects;
}

function ExportTable(object, widths = null)
{
	let lines = [];
	lines.push(".. csv-table:: "+object.caption);
	lines.push("   :header: \""+object.titles.join("\", \"")+"\"");
	if(widths != null){
		lines.push("   :widths: "+widths);
	}
	lines.push("   ");

    if(object.data.length > 1){
        let nitem = object.data[0].length;
        for(let n = 0; n < nitem; n++){
            if(object.titles[n] == "Format"){
                continue;
            }
            let citem = object.data[0][n];
            for(let j = 1; j < object.data.length; j++){
                if(object.data[j][n] == citem && citem !=  ""){
                    object.data[j][n] = "&uarr;"
                }
                else{
                    citem = object.data[j][n];
                }
            }
        }
    }

	for(let j = 0; j < object.data.length; j++){
		let items = object.data[j];
		for(let n = 0; n < items.length; n++){
			if(items[n] == null){
				items[n] = "";
			}
			else{
				items[n] = items[n].
					replaceAll("\\varepsilon", "\\\\varepsilon").
					replaceAll("\\perp", "\\\\perp").
					replaceAll("\\sqrt", "\\\\sqrt").
					replaceAll("\\pi", "\\\\pi").
					replaceAll("\\Delta", "\\\\Delta").
					replaceAll("\\lambda", "\\\\lambda").
					replaceAll("\\[", "\\\\[").
					replaceAll("\\]", "\\\\]");
			}
		}
		lines.push("   \""+items.join("\", \"")+"\"");
	}
	return lines;
}

function GetHelpLink(helpurl, category)
{
	let categurl = category.replaceAll(" ", "%20");
	let url = "`"+category+" <"+helpurl+"#"+categurl+">`_";
	return url;
}

function GetParagraph(label, detail, prmwidths)
{
	let lines = [];
	let sepline = "";
	sepline = sepline.padStart(label.length+2, "^");

	lines.push("*"+label+"*");
	lines.push(sepline);
	lines.push("");
	lines.push("Keywords to specify the parameters "+detail+" are summarized below. Refer to "+GetHelpLink(HelpURL, label)+" for more details about each parameter.")
	lines.push("");
	lines.push(...ExportTable(GetParameterKey()[label], prmwidths));
    return lines;
}

function GetQString(str)
{
    return str;
}

module.exports = {
    GetBrowserIssue:GetBrowserIssue,
    GetPythonOption:GetPythonOption,
    GetUnitKey:GetUnitKey,
    GetMenuCateg:GetMenuCateg,
    GetParagraph:GetParagraph,
    GetEBeamPrmList:GetEBeamPrmList,
    GetSeedPrmList:GetSeedPrmList,
    GetSPXPrmList:GetSPXPrmList,
    GetUndPrmList:GetUndPrmList,
    GetLatticePrmList:GetLatticePrmList,
    GetWakePrmList:GetWakePrmList,
    GetAlignPrmList:GetAlignPrmList,
    GetChicanePrmList:GetChicanePrmList,
    GetDispersionPrmList:GetDispersionPrmList,
    GetSimCtrlPrmList:GetSimCtrlPrmList,
    GetDataDumpPrmList:GetDataDumpPrmList,
    GetOutFilePrmList:GetOutFilePrmList,
    GetPPrawOptPrmList:GetPPrawOptPrmList,
    GetFELPrmList:GetFELPrmList,
    ExportTable:ExportTable,
    GetParameterKey:GetParameterKey,
    PySampleURL:PySampleURL,
    Version2Digit:Version2Digit,
    EBLabel:EBLabel,
    SeedLabel:SeedLabel,
    SPXOutLabel:SPXOutLabel,
    UndLabel:UndLabel,
    LatticeLabel:LatticeLabel,
    AlignmentLabel:AlignmentLabel,
    WakeLabel:WakeLabel,
    ChicaneLabel:ChicaneLabel,
    DispersionLabel:DispersionLabel,
    SimCondLabel:SimCondLabel,
    DataDumpLabel:DataDumpLabel,
    OutFileLabel:OutFileLabel,
    FELLabel:FELLabel,
    PostPLabel:PostPLabel,
    GetOutDataInf:GetOutDataInf
}
