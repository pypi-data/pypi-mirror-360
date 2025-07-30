"use strict";

function GetPreprocID(label)
{
    return [MenuLabels.preproc, MenuLabels[label]].join(IDSeparator);
}

function UpdateSliceParameters(sranges)
{
    let ndata = GUIConf.part_obj.data[0].length;
    let slicelen = sranges[2]/GUIConf.input[PartConfLabel][ParticleConfigLabel.bins[0]];
    let nsrange = [Math.floor(sranges[0]/slicelen+0.5), Math.floor(sranges[1]/slicelen+0.5)];
    let slices = nsrange[1]-nsrange[0]+1;

    let slice_avg, slice_sq, slice_corr, slice_particles;
    slice_avg = new Array(6);
    slice_sq = new Array(6);
    slice_corr = new Array(2);
    for(let j = 0; j < 6; j++){
        slice_avg[j] = new Array(slices); slice_avg[j].fill(0);
        slice_sq[j] = new Array(slices); slice_sq[j].fill(0);
        if(j < 2){
            slice_corr[j] = new Array(slices); slice_corr[j].fill(0);
        }
    }
    slice_particles = new Array(slices); slice_particles.fill(0);

    let Eav = 0;
    for(let n = 0; n < ndata; n++){
        let ns = Math.floor(GUIConf.part_obj.data[4][n]/slicelen+0.5)-nsrange[0];
        if(ns < 0 || ns >= slices){
            continue;
        }
        for(let j = 0; j < 6; j++){
            slice_avg[j][ns] += GUIConf.part_obj.data[j][n];
            slice_sq[j][ns] += GUIConf.part_obj.data[j][n]**2;
            if(j < 2){
                slice_corr[j][ns] += GUIConf.part_obj.data[2*j][n]*GUIConf.part_obj.data[2*j+1][n];
            }
        }
        Eav += GUIConf.part_obj.data[5][n];
        slice_particles[ns]++;
    }
    Eav /= ndata;

    for(let j = 0; j < SliceTitles.length; j++){
        GUIConf.slice_prms[j] = new Array(slices);
        GUIConf.slice_prms[j].fill(0);
    }

    let charge = GUIConf.GUIpanels[PartConfLabel].JSONObj[ParticleConfigLabel.pcharge[0]]
    for(let ns = 0; ns < slices; ns++){
        GUIConf.slice_prms[0][ns] = (nsrange[0]+ns)*slicelen;
        GUIConf.slice_prms[1][ns] = slice_particles[ns]*charge/(slicelen/CC); // current
        if(slice_particles[ns] == 0){
            continue;
        }
        for(let j = 0; j < 6; j++){
            slice_avg[j][ns] /= slice_particles[ns];
            slice_sq[j][ns] /= slice_particles[ns];
            if(j < 2){
                slice_corr[j][ns] /= slice_particles[ns];
            }
        }
        GUIConf.slice_prms[2][ns] = slice_avg[5][ns]; // energy
        GUIConf.slice_prms[3][ns] = Math.sqrt((slice_sq[5][ns]-slice_avg[5][ns]**2))/slice_avg[5][ns]; // energy spread
        for(let j = 0; j < 2; j++){
            let size = slice_sq[2*j][ns]-slice_avg[2*j][ns]**2;
            let div = slice_sq[2*j+1][ns]-slice_avg[2*j+1][ns]**2;
            let corr = slice_corr[j][ns]-slice_avg[2*j][ns]*slice_avg[2*j+1][ns];
            let emitt = size*div-corr**2;
            if(emitt > 0 && slice_particles[ns] > 5){
                emitt = Math.sqrt(emitt);
                GUIConf.slice_prms[4+j][ns] = emitt*(Eav*1e3/MC2MeV)*1e6; // normalized emittance, mm.mrad
                GUIConf.slice_prms[6+j][ns] = size/emitt; // beta
                GUIConf.slice_prms[8+j][ns] = -corr/emitt; // alpha
            }
            GUIConf.slice_prms[10+j][ns] = slice_avg[2*j][ns];
            GUIConf.slice_prms[12+j][ns] = slice_avg[2*j+1][ns];
        }
    }
    let specs = GetEBeamSpecSlice(GUIConf.slice_prms);
    specs[EBeamPrmsLabel.bunchcharge[0]] = charge*ndata*1e+9; // C -> nC
    specs[EBeamPrmsLabel.bunchleng[0]] = sranges[2];
    GUIConf.input[EBLabel][EBeamPrmsLabel.partspec[0]] = specs;
}

function ArrangePPPanel()
{
    let ppitem = GetPPItem();
    let pids = {[PPPartAnaLabel]:"preproc-part", [PPMicroBunchLabel]:"preproc-seed", [PPUdataLabel]:"preproc-udata"};
    if(ppitem != null && pids.hasOwnProperty(ppitem)){
        document.getElementById(pids[ppitem]).classList.replace("d-none", "d-flex");
        delete pids[ppitem];
    }
    Object.keys(pids).forEach((el) => {
        document.getElementById(pids[el]).classList.replace("d-flex", "d-none");
    });

    if(ppitem == PPMicroBunchLabel){
        document.getElementById(GetPreprocID("seedrun")).classList.replace("d-none", "d-flex");
    }
    else{
        document.getElementById(GetPreprocID("seedrun")).classList.replace("d-flex", "d-none");
    }

    if(ppitem == null){
        document.getElementById("preproc-conf-div").classList.add("d-none");
        document.getElementById("preproc-plot").innerHTML = "";
        document.getElementById("expbtn").classList.add("d-none");
        GUIConf.plotly = null;        
        return;
    }

    let select = document.getElementById("preproc-select");
    if(ppitem == PPPartAnaLabel){
        let partfile = "Not Selected";
        if(GUIConf.input[EBLabel].hasOwnProperty(EBeamPrmsLabel.partfile[0])){
            partfile = GUIConf.input[EBLabel][EBeamPrmsLabel.partfile[0]];
            if(partfile == ""){
                partfile = "Not Selected";
            }
        }
        document.getElementById(GetPreprocID("optimize")).classList.add("d-none");
        document.getElementById("partdataname").innerHTML = partfile;
    }
    if(ppitem == PPPartAnaLabel || ppitem == PPMicroBunchLabel || ppitem == PPUdataLabel){
        select.setAttribute("size", "1");
        document.getElementById(GUIConf.guids[PrePLabel]).classList.add("d-none");
    }
    else{
        ExpandSelectMenu(select);    
    }
    
    if(ppitem == PPUdataLabel){
        UpdateUDPlot();
    }
    else if(ppitem == PPMicroBunchLabel){
        ["import", "units", "optimize"].forEach((label) => {
            document.getElementById(GetPreprocID(label)).classList.add("d-none");        
        });
        if(Object.keys(GUIConf.mbobjs).length > 0){
            PlotMbunchEvaluation();
        }
        else{
            document.getElementById("expbtn").classList.add("d-none");
        }
    }
    else if(ppitem == PPPartAnaLabel){
        document.getElementById("expbtn").classList.add("d-none");
        UpdateParticlePlot();
    }
    else{
        UpdatePPPlot();
    }

    if(Object.keys(pids).length == 3 && GUIConf.GUIpanels[PrePLabel].Hidden()){
        document.getElementById("preproc-conf-div").classList.add("d-none");
    }
    else{
        document.getElementById("preproc-conf-div").classList.remove("d-none");
    }
}

function ShowImportButtons(isshow)
{
    ["import", "units"].forEach((label) => {
        if(isshow){
            document.getElementById(GetPreprocID(label)).classList.remove("d-none");
        }
        else{
            document.getElementById(GetPreprocID(label)).classList.add("d-none");
        }
    });
}

function GetPPObject(ppitem)
{
    if(ppitem == null){
        ppitem = GetPPItem();
        if(ppitem == null){
            return null;
        }
    }

    let obj = {};
    obj = GetSimulationObject(ppitem);
    obj.runid = ppitem;
    obj[PrePLabel] = GUIConf.GUIpanels[PrePLabel].ExportCurrent();    

    return obj;
}

function UpdatePlot(categ, ascii = null, label = null, items = null)
{
    let obj, titles, axtitles, dimension;
    if(categ == UndDataLabel){
        let selection = GetSelections(document.getElementById("preproc-udata-select"));
        obj = GUIConf.input[UndDataLabel].data[selection.index[0]];
        titles = GUIConf.input[UndDataLabel].data[selection.index[0]][DataTitlesLabel];
        axtitles = [AsciiFormats[UndDataLabel].titles[0], AsciiFormats[UndDataLabel].ordinate];
        dimension = 1;
    }
    else if(ascii == CustomSlice){
        dimension = 1;
        titles = Array.from(items);
        obj = {titles: items, data: new Array(items.length)};

        let ispsat = items.indexOf(SatPowerLabel) >= 0;
        let isgain = items.indexOf(GainLengthLabel) >= 0;
        let psat = [], lgain = [];
        if(ispsat || isgain){
            let lu = GUIConf.input[UndLabel][UndPrmsLabel.lu[0]]*0.001;
            let {K, phi} = GetKValue(GUIConf.input[UndLabel]);          
            let titles = [CurrentLabel, EnergyLabel, EspLabel, EmittxLabel, EmittyLabel];
                // retrive data to evaluate the gain length etc.
            let data = [];
            for(let j = 0; j < titles.length; j++){
                let index = GUIConf.input[categ][label].titles.indexOf(titles[j]);
                data.push(GUIConf.input[categ][label].data[index]);
            }
            let ndata = data[0].length;
            psat = new Array(ndata);
            lgain = new Array(ndata);
            let embspecs = new Array(3);
            for(let n = 0; n < data[0].length; n++){
                let nemitt = [data[3][n], data[4][n]];
                let specs = FEL_specs(data[0][n], nemitt, data[1][n], data[2][n], lu, K, phi, embspecs);
                if(specs == null){
                    psat[n] = lgain[n] = 0;
                }
                else{
                    psat[n] = specs[FELPrmsLabel.psat[0]];
                    lgain[n] = specs[FELPrmsLabel.Lg[0]][1];
                }
            }
        }

        for(let j = 0; j < items.length; j++){
            if(items[j] == SatPowerLabel){
                obj.data[j] = psat;
                continue;
            }
            if(items[j] == GainLengthLabel){
                obj.data[j] = lgain;
                continue;
            }
            let tgtidx = GUIConf.input[categ][label].titles.indexOf(
                    items[j] == EdevLabel ? EnergyLabel : items[j]);
            obj.data[j] = Array.from(GUIConf.input[categ][label].data[tgtidx]);
            if(items[j] == EdevLabel){
                for(let n = 0; n < obj.data[j].length; n++){
                    obj.data[j][n] = obj.data[j][n]/GUIConf.input[EBLabel][EBeamPrmsLabel.eenergy[0]]-1;
                }
            }
        }
        axtitles = Array.from(items);
        if(items.indexOf(EdevLabel) >= 0){
            axtitles[1] = EdevspLabel;
        }
        else if(items.indexOf(EmittxLabel) >= 0){
            axtitles[1] = EmittxyLabel;
        }
        else if(items.indexOf(BetaxLabel) >= 0){
            axtitles[1] = BetaxyAvLabel;
        }
        else if(items.indexOf(AlphaxLabel) >= 0){
            axtitles[1] = AlphaxyLabel;
        }
        else if(items.indexOf(XavLabel) >= 0){
            axtitles[1] = XYavLabel;
        }
        else if(items.indexOf(XpavLabel) >= 0){
            axtitles[1] = XYpavLabel;
        }
    }
    else{
        obj = GUIConf.input[categ][label];
        dimension = GUIConf.ascii[ascii].GetDimension();
        titles = items;
        if(dimension == 2){
            axtitles = Array.from(items);
        }
        else{
            axtitles = [items[0], GUIConf.ascii[ascii].GetOrdinate()];
        }
    }
    let plot_configs = CopyJSON(GUIConf.def_plot_configs);
    if(Settings.plotconfigs.hasOwnProperty(axtitles[dimension])){
        plot_configs = Settings.plotconfigs[axtitles[dimension]];
    }
    else{
        Settings.plotconfigs[axtitles[dimension]] = plot_configs;
    }

    let parent = document.getElementById("preproc-plot");
    parent.innerHTML = "";
    let plobj = {
        data: [obj],
        dimension: dimension,
        titles: titles,
        axtitles: axtitles,
        legprefix: "",
        isdata2d: true
    }
    GUIConf.plotly = new PlotWindow(
        parent, "plot", plobj, plot_configs, GUIConf.filename, null, []);
    document.getElementById("expbtn").classList.remove("d-none");
}

function UpdatePPPlot()
{
    ShowImportButtons(false);
    document.getElementById(GetPreprocID("optimize")).classList.add("d-none");        

    let ppitem = GetPPItem(), items;
    if(ppitem == null){
        GUIConf.GUIpanels[PrePLabel].Clear();
        GUIConf.GUIpanels[PrePLabel].SetPanel();
        GUIConf.plotly = null;
        document.getElementById("expbtn").classList.add("d-none");        
        document.getElementById("preproc-plot").innerHTML = "";
        return;
    }

    let categ = "", label, ascii;
    document.getElementById(GUIConf.guids[PrePLabel]).classList.remove("d-none");
    if(ppitem == PPCurrentLabel){
        if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == CustomSlice){
            label = EBeamPrmsLabel.slicefile[0];
            ascii = CustomSlice;
        }
        else{
            label = EBeamPrmsLabel.currfile[0];
            ascii = CustomCurrent;
        }
        categ = EBLabel;
        items = [SliceLabel, CurrentLabel];
    }
    else if(ppitem == PPEtLabel){
        categ = EBLabel;
        label = EBeamPrmsLabel.etfile[0];
        ascii = CustomEt;
        items = [SliceLabel, EdevLabel, CurrjLabel];
    }
    else if(
        ppitem == PPSliceEmittLabel || 
        ppitem == PPSliceELabel || 
        ppitem == PPSliceBetaLabel || 
        ppitem == PPSliceAlphaLabel || 
        ppitem == XYTitleLabel || 
        ppitem == XYpTitleLabel || 
        ppitem == PPGainLengthLabel || 
        ppitem == PPSatPowerLabel)
    {
        categ = EBLabel;
        label = EBeamPrmsLabel.slicefile[0];
        ascii = CustomSlice;
        if(ppitem == PPSliceEmittLabel){
            items = [SliceLabel, EmittxLabel, EmittyLabel];
        }
        else if(ppitem == PPSliceELabel){
            items = [SliceLabel, EdevLabel, EspLabel];
        }
        else if(ppitem == PPSliceBetaLabel){
            items = [SliceLabel, BetaxLabel, BetayLabel];
        }
        else if(ppitem == PPSliceAlphaLabel){
            items = [SliceLabel, AlphaxLabel, AlphayLabel];
        }
        else if(ppitem == XYTitleLabel){
            items = [SliceLabel, XavLabel, YavLabel];
        }
        else if(ppitem == XYpTitleLabel){
            items = [SliceLabel, XpavLabel, YpavLabel];
        }
        else if(ppitem == PPGainLengthLabel){
            items = [SliceLabel, GainLengthLabel];
        }
        else if(ppitem == PPSatPowerLabel){
            items = [SliceLabel, SatPowerLabel];
        }
    }
    else if(ppitem == PPCustomWake){
        categ = WakeLabel;
        label = WakePrmsLabel.wakecustomdata[0];
        ascii = WakeDataLabel;
        items = [SliceLabel, WakeSingleLabel];
    }
    else if(ppitem == PPCustomMono){
        categ = ChicaneLabel;
        label = ChicanePrmsLabel.monodata[0];
        ascii = MonoDataLabel;
        items = [PhotonEnergyLabel, TransmittanceReal, TransmittanceImag];
    }
    if(categ != ""){
        GUIConf.import = {category:categ, prmlabel:label, ascii:ascii};
        ShowImportButtons(true);
        GUIConf.GUIpanels[PrePLabel].Clear();
        GUIConf.GUIpanels[PrePLabel].SetPanel();
        let isempty = IsEmptyObj(GUIConf.input, categ, label);
        if(isempty){
            CreateUploadArea("pp-import");
            return;
        }
        UpdatePlot(categ, ascii, label, items);
    }
    else{
        if(ppitem == ""){
            return;
        }

        if(ppitem == PPBetaLabel || ppitem == PPOptBetaLabel){
            GUIConf.GUIpanels[PrePLabel].SetPanel(ppitem, GUIConf.input[LatticeLabel]);
        }
        else if(ppitem == PPWakeEvar){
            GUIConf.GUIpanels[PrePLabel].SetPanel(ppitem, GUIConf.input[WakeLabel]);
        }
        else if(ppitem == PPFDlabel ||
            ppitem == PP1stIntLabel ||
            ppitem == PP2ndIntLabel ||
            ppitem == PPPhaseErrLabel)
        {
            GUIConf.GUIpanels[PrePLabel].SetPanel(ppitem, GUIConf.input[UndLabel]);
        }
        else if(ppitem == PPMonoSpectrum){
            GUIConf.GUIpanels[PrePLabel].SetPanel(ppitem, GUIConf.input[ChicaneLabel]);
        }
        else{
            GUIConf.GUIpanels[PrePLabel].Clear();
            GUIConf.GUIpanels[PrePLabel].SetPanel();
        }
        if(ppitem == PPOptBetaLabel){
            document.getElementById(GetPreprocID("optimize")).classList.remove("d-none");
        }
        else{
            DrawPPPlot(ppitem);
        }
    }
}

function SetPreprocessPlot()
{
    let ppplotlabel = [];
    let ppobjs = {};

    let bunch = GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]];
    if(bunch == CustomSlice)
    {
        ppobjs[EBLabel] = [PPCurrentLabel, PPSliceEmittLabel, PPSliceELabel, PPSliceBetaLabel, PPSliceAlphaLabel, 
            XYTitleLabel, XYpTitleLabel, PPGainLengthLabel, PPSatPowerLabel];
    }
    else if(bunch == CustomCurrent){
        ppobjs[EBLabel] = [PPCurrentLabel];
    }
    else if(bunch == CustomEt){
        ppobjs[EBLabel] = [PPEtLabel];
    }
    else if(bunch == CustomParticle){
        ppobjs[EBLabel] = [PPPartAnaLabel];
    }
    if(ppobjs.hasOwnProperty(EBLabel)){
        ppplotlabel.push(ppobjs);
    }

    let bmprof = GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]];
    let seedprf = GUIConf.input[SeedLabel][SeedPrmsLabel.seedprofile[0]];
    if((bmprof == GaussianBunch || bmprof == BoxcarBunch) 
        && seedprf != NotAvaliable && seedprf != SimplexOutput){
        ppobjs = {};
        ppobjs[SeedLabel] = [];
        ppobjs[SeedLabel].push(PPMicroBunchLabel);
        ppplotlabel.push(ppobjs);
    }

    ppobjs = {};
    ppobjs[UndLabel] = [PPFDlabel, PP1stIntLabel, PP2ndIntLabel]
    let uobj = GUIConf.input[UndLabel];
    let opttype = uobj[UndPrmsLabel.opttype[0]];
    if(GUIConf.input[AlignmentLabel][AlignErrorUPrmsLabel.ualign[0]] != IdealLabel ||
        (uobj[UndPrmsLabel.taper[0]] != NotAvaliable && 
            opttype != TaperOptWhole && opttype != TaperOptSlice))
    {
        ppobjs[UndLabel].push(PPKValue);
        ppobjs[UndLabel].push(PPDetune);
    }
    if(uobj[UndPrmsLabel.umodel[0]] == ImportDataLabel){
        ppobjs[UndLabel].push(PPPhaseErrLabel);
        ppobjs[UndLabel].push(PPUdataLabel);
    }
    if(uobj[UndPrmsLabel.umodel[0]] == SpecifyErrLabel){
        ppobjs[UndLabel].push(PPPhaseErrLabel);
    }
    ppplotlabel.push(ppobjs);

    if(GUIConf.input[WakeLabel][WakePrmsLabel.wakeon[0]] && (
            GUIConf.input[WakeLabel][WakePrmsLabel.resistive[0]] ||
            GUIConf.input[WakeLabel][WakePrmsLabel.roughness[0]] ||
            GUIConf.input[WakeLabel][WakePrmsLabel.dielec[0]] ||
            GUIConf.input[WakeLabel][WakePrmsLabel.spcharge[0]] ||
            GUIConf.input[WakeLabel][WakePrmsLabel.wakecustom[0]]
        )
    ){
        ppobjs = {};
        ppobjs[WakeLabel] = [PPWakeBunch, PPWakeEvar];
        if(GUIConf.input[WakeLabel][WakePrmsLabel.wakecustom[0]]){
            ppobjs[WakeLabel].push(PPCustomWake);
        }
        ppplotlabel.push(ppobjs);    
    }

    ppobjs = {};
    ppobjs[LatticeLabel] = [PPBetaLabel, PPOptBetaLabel, PPFocusStrength];
    ppplotlabel.push(ppobjs);

    let others = [];
    if(GUIConf.input[AlignmentLabel][AlignErrorUPrmsLabel.BPMalign[0]] != IdealLabel
            || GUIConf.input[DispersionLabel][DispersionPrmsLabel.einjec[0]] 
            || GUIConf.input[DispersionLabel][DispersionPrmsLabel.kick[0]]
            || GUIConf.input[DispersionLabel][AlignErrorUPrmsLabel.BPMalign[0]])
    {
        others.push(PPDispersion);
    }
    if(GUIConf.input[ChicaneLabel][ChicanePrmsLabel.chicaneon[0]] 
            && GUIConf.input[ChicaneLabel][ChicanePrmsLabel.monotype[0]] != NotAvaliable)
    {
        if(GUIConf.input[ChicaneLabel][ChicanePrmsLabel.monotype[0]] == CustomLabel){
            others.push(PPCustomMono);
        }
        else{
            others.push(PPMonoSpectrum);
        }
    }
    if(others.length > 0){
        ppobjs = {};
        ppobjs[OthersLabel] = others;
        ppplotlabel.push(ppobjs);
    }

    let former = GetPPItem();
    let select = document.getElementById("preproc-select");
    select.innerHTML = "";
    SetSelectMenus(select, ppplotlabel, [], former, true);
}

// pre-processing via solver
async function DrawPPPlot(ppitem = null)
{
    let obj = GetPPObject(ppitem);
    if(obj == null){
        return;
    }
    ppitem = obj.runid;

    // <EMSCRIPTEN>
    if(Framework == ServerLabel){
        let prms = JSON.stringify(obj, null, JSONIndent);
        let worker = new Worker("launch_solver.js");
        let isok = true;
        worker.addEventListener("message", (msgobj) => {
            if(msgobj.data == "ready"){
                worker.postMessage({data: prms, nthread: 1, serno: 0});    
            }
            else if(msgobj.data.dataname != ""){
                if(isok){
                    let result = JSON.parse(msgobj.data.data);
                    if(ppitem == PPMicroBunchLabel){
                        ApplyMicroBunch(result);
                        return;
                    }
                    if(!result.hasOwnProperty(ppitem)){
                        Alert("No pre-processing results found.");
                        return;    
                    }
                    DrawPreprocObj(ppitem, result[ppitem]);        
                }
            }
            else if(msgobj.data.data != null){
                if(msgobj.data.data.indexOf(ErrorLabel) >= 0){
                    Alert(msgobj.data.data);
                }
            }
        });
        return;
    }
    // </EMSCRIPTEN>
    
    if(Framework != TauriLabel){
        if(Framework.includes("python")){
            PyQue.Put([PrePLabel, obj]);
        }
        else if(Framework == BrowserLabel){
            ExportObjects(obj, GUIConf.filename);
        }
        return;
    }

    let dataname = await window.__TAURI__.path.join(GUIConf.wdname, ".preproc.json");
    let prms = FormatArray(JSON.stringify(obj, null, JSONIndent));

    try {
        await window.__TAURI__.tauri.invoke("write_file", { path: dataname, data: prms});
    }
    catch (e) {
        Alert(e.message);
        return;
    }

    let isNG = false;
    const command = new window.__TAURI__.shell.Command("solver_nompi", ["-f", dataname]);
    command.on("close", (data) => {
        if(data.code != 0 || isNG){
            return;
        }
        window.__TAURI__.tauri.invoke("read_file", { path: dataname})
        .then((result) => {
            window.__TAURI__.tauri.invoke("remove_file", { path: dataname})
            result = JSON.parse(result);
            if(ppitem == PPMicroBunchLabel){
                ApplyMicroBunch(result);
                return;
            }
            if(!result.hasOwnProperty(ppitem)){
                Alert("No pre-processing results found.");
                return;    
            }
    
            let obj = result[ppitem];
            DrawPreprocObj(ppitem, obj);
        })
        .catch((e) => {
            Alert("Pre-processing failed: "+e.message+".");
        });
    });
    command.stdout.on("data", (data) => {
        if(data.indexOf(ErrorLabel) >= 0){
            Alert(data);
            isNG = true;
        }
    });   
    command.spawn();
}

function DrawPreprocObj(ppitem, obj)
{
    let plot_configs = CopyJSON(GUIConf.def_plot_configs);
    if(Settings.plotconfigs.hasOwnProperty(ppitem)){
        plot_configs = Settings.plotconfigs[ppitem];
    }
    else{
        Settings.plotconfigs[ppitem] = plot_configs;
    }

    let parent = document.getElementById("preproc-plot");
    parent.innerHTML = "";
    let axtitles = new Array(obj.dimension+1);
    for(let j = 0; j < obj.dimension; j++){
        axtitles[j] = obj.titles[j];
        if(obj.units[j] != "-"  && obj.units[j] != ""){
            axtitles[j] += " ("+obj.units[j]+")";
        }
    }
    axtitles[obj.dimension] = AxisTitles[ppitem];
    let plobj = {
        data: [obj],
        dimension: obj.dimension,
        titles: obj.titles,
        axtitles: axtitles,
        legprefix: "",
        isdata2d: true
    }
    GUIConf.plotly = new PlotWindow(
        parent, "plot", plobj, plot_configs, GUIConf.filename, null, []);
    document.getElementById("expbtn").classList.remove("d-none");
    ApplyPPResult(ppitem, obj);
}

function UpdateParticlePlot()
{
    ShowImportButtons(false);

    if(GUIConf.part_data == null){
        GUIConf.plotly = null;
        document.getElementById("preproc-plot").innerHTML = "";
        return;
    }

    let obj, titles, axtitles;
    let plot_configs = CopyJSON(GUIConf.def_plot_configs);

    if(GUIConf.GUIpanels[PartPlotConfLabel].JSONObj[PDPLotConfigLabel.type[0]] == CustomSlice)
    {
        let idxs = SliceTitles.indexOf(SliceLabel);
        let idxI = SliceTitles.indexOf(CurrentLabel);
        let idxemitt = [SliceTitles.indexOf(EmittxLabel), SliceTitles.indexOf(EmittyLabel)];
        let idxbeta = [SliceTitles.indexOf(BetaxLabel), SliceTitles.indexOf(BetayLabel)];
        let idxalpha = [SliceTitles.indexOf(AlphaxLabel), SliceTitles.indexOf(AlphayLabel)];
        let idxp = [SliceTitles.indexOf(XavLabel), SliceTitles.indexOf(YavLabel)];
        let idxa = [SliceTitles.indexOf(XpavLabel), SliceTitles.indexOf(YpavLabel)];
        let idxE = SliceTitles.indexOf(EnergyLabel);
        let idxEsp = SliceTitles.indexOf(EspLabel);
        let item = GUIConf.GUIpanels[PartPlotConfLabel].JSONObj[PDPLotConfigLabel.item[0]];

        titles = [SliceLabel];
        axtitles = [SliceLabel, item];
        let data = [GUIConf.slice_prms[idxs]];
        if(item == CurrentTitle){
            titles.push(CurrentLabel);
            axtitles[1] = CurrentLabel;
            data.push(GUIConf.slice_prms[idxI]);
        }
        else if(item == EdevspLabel){
            titles.push(EdevLabel);
            titles.push(EspLabel);
            let edev = Array.from(GUIConf.slice_prms[idxE]);
            for(let n = 0; n < edev.length; n++){
                if(GUIConf.slice_prms[idxI][n] > 0){
                    edev[n] = edev[n]/GUIConf.input[EBLabel][EBeamPrmsLabel.eenergy[0]]-1;
                }
            }
            data.push(edev);
            data.push(GUIConf.slice_prms[idxEsp]);
        }
        else if(item == EmittTitle){
            titles.push(EmittxLabel);
            titles.push(EmittyLabel);
            data.push(GUIConf.slice_prms[idxemitt[0]]);
            data.push(GUIConf.slice_prms[idxemitt[1]]);
            axtitles[1] = EmittxyLabel;
        }
        else if(item == BetaTitleLabel){
            titles.push(BetaxLabel);
            titles.push(BetayLabel);
            data.push(GUIConf.slice_prms[idxbeta[0]]);
            data.push(GUIConf.slice_prms[idxbeta[1]]);
            axtitles[1] = BetaxyAvLabel;
        }
        else if(item == AlphaTitleLabel){
            titles.push(AlphaxLabel);
            titles.push(AlphayLabel);
            data.push(GUIConf.slice_prms[idxalpha[0]]);
            data.push(GUIConf.slice_prms[idxalpha[1]]);
            axtitles[1] = AlphaxyLabel;
        }
        else if(item == XYTitleLabel){
            titles.push(XavLabel);
            titles.push(YavLabel);
            data.push(GUIConf.slice_prms[idxp[0]]);
            data.push(GUIConf.slice_prms[idxp[1]]);
            axtitles[1] = XYavLabel;
        }
        else if(item == XYpTitleLabel){
            titles.push(XpavLabel);
            titles.push(YpavLabel);
            data.push(GUIConf.slice_prms[idxa[0]]);
            data.push(GUIConf.slice_prms[idxa[1]]);
            axtitles[1] = XYpavLabel;
        }
        else if(item == PPGainLengthLabel || item == PPSatPowerLabel){
            if(item == PPGainLengthLabel){
                titles.push(GainLengthLabel);
                axtitles[1] = GainLengthLabel;
            }
            else{
                titles.push(SatPowerLabel);
                axtitles[1] = SatPowerLabel;
            }
            let lu = GUIConf.input[UndLabel][UndPrmsLabel.lu[0]]*0.001;
            let {K, phi} = GetKValue(GUIConf.input[UndLabel]);
            let IA = GUIConf.slice_prms[idxI];
            let EGeV = GUIConf.slice_prms[idxE];
            let espread = GUIConf.slice_prms[idxEsp];
            let emitxy = [GUIConf.slice_prms[idxemitt[0]], GUIConf.slice_prms[idxemitt[1]]];
            let ebmspecs = new Array(3);
            data.push(new Array(data[0].length));
            for(let n = 0; n < data[0].length; n++){
                let nemitt = [emitxy[0][n], emitxy[1][n]];
                let specs = FEL_specs(IA[n], nemitt, EGeV[n], espread[n], lu, K, phi, ebmspecs);
                if(specs == null){
                    data[1][n] = 0;
                }
                else{
                    data[1][n] = item == PPGainLengthLabel ? specs[FELPrmsLabel.Lg[0]][1] : specs[FELPrmsLabel.psat[0]];
                }
            }
        }
        obj = {titles: titles, data: data};
    }
    else{
        let xaxis = GUIConf.GUIpanels[PartPlotConfLabel].JSONObj[PDPLotConfigLabel.xaxis[0]];
        let yaxis = GUIConf.GUIpanels[PartPlotConfLabel].JSONObj[PDPLotConfigLabel.yaxis[0]];
        let plots = GUIConf.GUIpanels[PartPlotConfLabel].JSONObj[PDPLotConfigLabel.plotparts[0]];
        let ndata = GUIConf.part_obj.data[0].length;
        titles = [xaxis, yaxis];
        axtitles = [xaxis, yaxis];

        if(plots < ndata){
            let jindices = [ParticleTitles.indexOf(xaxis), ParticleTitles.indexOf(yaxis)];
            obj = {titles: [xaxis, yaxis], data: [new Array(plots), new Array(plots)]};
            let dn = (ndata-1)/(plots-1);
            for(let n = 0; n < plots; n++){
                let nindex = Math.floor(n*dn+0.5);
                for(let j = 0; j < 2; j++){
                    obj.data[j][n] = GUIConf.part_obj.data[jindices[j]][nindex];
                }
            }
        }
        else{
            obj = GUIConf.part_obj;
        }
        plot_configs[PlotOptionsLabel.type[0]] = SymbolLabel;
        plot_configs[PlotOptionsLabel.size[0]] = 1;
    }

    if(Settings.plotconfigs.hasOwnProperty(axtitles[1])){
        plot_configs = Settings.plotconfigs[axtitles[1]];
    }
    else{
        Settings.plotconfigs[axtitles[1]] = plot_configs;
    }

    let parent = document.getElementById("preproc-plot");
    parent.innerHTML = "";
    let plobj = {
        data: [obj],
        dimension: 1,
        titles: titles,
        axtitles: axtitles,
        legprefix: "",
        isdata2d: false
    }
    GUIConf.plotly = new PlotWindow(
        parent, "plot", plobj, plot_configs, GUIConf.filename, null, []);
    document.getElementById("expbtn").classList.remove("d-none");
}

function AnalyzeParticle()
{
    if(GUIConf.part_data == null){
        GUIConf.input[EBLabel][EBeamPrmsLabel.partspec[0]] = BundleEBeamSpecs();
        return;
    }

    if(!GUIConf.input.hasOwnProperty(PartConfLabel)){ // to save in the parameter file
        GUIConf.input[PartConfLabel] = GUIConf.GUIpanels[PartConfLabel].JSONObj;
    }

    let cols = [
        GUIConf.input[PartConfLabel][ParticleConfigLabel.colx[0]],
        GUIConf.input[PartConfLabel][ParticleConfigLabel.colxp[0]],
        GUIConf.input[PartConfLabel][ParticleConfigLabel.coly[0]],
        GUIConf.input[PartConfLabel][ParticleConfigLabel.colyp[0]],
        GUIConf.input[PartConfLabel][ParticleConfigLabel.colt[0]],
        GUIConf.input[PartConfLabel][ParticleConfigLabel.colE[0]]
    ];
    let xyunit =  GUIConf.input[PartConfLabel][ParticleConfigLabel.unitxy[0]] == UnitMeter ? 1 : 1e-3;
    let xypunit =  GUIConf.input[PartConfLabel][ParticleConfigLabel.unitxyp[0]] == UnitRad ? 1 : 1e-3;
    let tunit = 1, eunit = 1;
    switch(GUIConf.input[PartConfLabel][ParticleConfigLabel.unitt[0]]){
        case UnitpSec:
            tunit = -1e-12*CC;
            break;
        case UnitfSec:
            tunit = -1e-15*CC;
            break;
        case UnitSec:
            tunit = -CC;
            break;
        case UnitMiliMeter:
            tunit = 1e-3;
            break;
    }
    if(GUIConf.input[PartConfLabel][ParticleConfigLabel.unitE[0]] == UnitMeV){
        eunit = 1e-3;
    }
    else if(GUIConf.input[PartConfLabel][ParticleConfigLabel.unitE[0]] == UnitGamma){
        eunit = 1e-3*MC2MeV;
    }
    let units = [
        xyunit, xypunit, xyunit, xypunit, tunit, eunit
    ];

    GUIConf.ascii[CustomParticle].SetData(GUIConf.part_data, units, cols);
    GUIConf.part_obj = GUIConf.ascii[CustomParticle].GetObj();
    let ndata = GUIConf.part_obj.data[0].length;
    if(ndata < MinimumParticles){
        Alert("More than "+MinimumParticles+" particles needed.");
        GUIConf.input[EBLabel][EBeamPrmsLabel.partspec[0]] = BundleEBeamSpecs();
        return;
    }
    let sav = 0, smin, smax, ssigma;
    for(let n = 0; n < ndata; n++){
        sav += GUIConf.part_obj.data[4][n];
        if(n == 0){
            smin = GUIConf.part_obj.data[4][n];
            smax = GUIConf.part_obj.data[4][n];
        }
        else{
            smin = Math.min(smin, GUIConf.part_obj.data[4][n]);
            smax = Math.max(smax, GUIConf.part_obj.data[4][n]);
        }
    }
    sav /= ndata;
    ssigma = 0;
    for(let n = 0; n < ndata; n++){
        GUIConf.part_obj.data[4][n] -= sav;
        ssigma += GUIConf.part_obj.data[4][n]**2;
    }
    ssigma = Math.sqrt(ssigma/ndata);
    smin -= sav;
    smax -= sav;
    let sranges = [smin, smax, ssigma];
    UpdateSliceParameters(sranges);
    GUIConf.input[EBLabel][EBeamPrmsLabel.eenergy[0]] = 
        GUIConf.input[EBLabel][EBeamPrmsLabel.partspec[0]][EBeamPrmsLabel.eenergy[0]];
    UpdateParticlePlot();
    document.getElementById("preproc-part-plotconf-div").classList.remove("d-none");

    let id = GetIDFromItem(EBLabel, EBeamPrmsLabel.bmprofile[0], -1);
    SetSPXOut();
    UpdateEBBaseSpecs();
    Update(id);
}

function ExportPreProcess(type, titles = [])
{
    if(GUIConf.plotly != null){
        if(type == 0){
            let id = GetPreprocID("ascii");
            if(Framework == PythonGUILabel){
                PyQue.Put(id);
                return;
            }
            GUIConf.plotly.ExportPlotWindow(id);
        }
        else{
            let size = GetPlotPanelSize("preproc-plot");
            let plotobj = GetPlotObj(size, [GUIConf.plotly], false);
            for(let j = 0; j < plotobj.data.length; j++){
                if(j >= titles.length){
                    plotobj.data[j].title = "";
                }
                else{
                    plotobj.data[j].title = titles[j];
                }
            }
            CreateNewplot(plotobj);
        }
    }
}

function GetPPItem(id = "preproc-select")
{
    let select = document.getElementById(id);
    let ppitem = GetSelections(select).value;
    if(ppitem.length == 0){
        return null;
    }
    return ppitem[0];
}

function EditUnits()
{
    EditDialog(DataUnitLabel);
}

async function ImportData()
{
    GUIConf.fileid = GetPreprocID("import");
    if(Framework == TauriLabel){
        let path = await GetPathDialog(
            "Import a data file for pre-processing.", "preproc", true, true, false, false);
        if(path == null){
            return;
        }
        window.__TAURI__.tauri.invoke("read_file", {path: path})
        .then((data) => {
            HandleFile(data, path, true);
        });
    }
    else if(Framework == PythonGUILabel){
        PyQue.Put(GUIConf.fileid);
    }
    else{
        document.getElementById("file-main").click();
    }
}

function GetParticleDatapath()
{
    let dataname = "";
    if(GUIConf.input[EBLabel].hasOwnProperty(EBeamPrmsLabel.partfile[0])){
        dataname = GUIConf.input[EBLabel][EBeamPrmsLabel.partfile[0]];
    }   
    if(dataname == "Unselected"){
        dataname = "";
    }
    return dataname;
}

function ImportParticle()
{
    if(Framework.includes("python")){  // do nothing; particle data to be loaded in python
        return;
    }
    GUIConf.fileid = GetPreprocID("load");
    let path = GetParticleDatapath();
    if(Framework == TauriLabel){
        if(path == ""){
            let msg = "No path is specified for \""+EBeamPrmsLabel.partfile[0]+"\"";
            Alert(msg);
        }
        else{
            window.__TAURI__.tauri.invoke("read_file", {path: path})
            .then((data) => {
                HandleFile(data, path, true);
            })
            .catch((e) => {
                let msg = 'Loading from "'+path+'" failed: '+e.message;
                Alert(msg);
            })    
        }
    }
    else{
        document.getElementById("file-main").click();
    }
}

function CreateUploadArea(type, ismultiple = false)
{
    GUIConf.plotly = null;
    document.getElementById("preproc-plot").innerHTML = "";
    document.getElementById("expbtn").classList.add("d-none");    
    document.getElementById("preproc-plot").classList.replace("d-none", "d-flex");

    let ddfile = document.createElement("input");
    ddfile.setAttribute("type", "file");
    if(ismultiple){
        ddfile.setAttribute("multiple", true);
    }
    ddfile.addEventListener("change", (e) => {
        GUIConf.fileid = type;
        LoadFiles(e, HandleFile);
        ddfile.value = "";
    });

    let dddiv = document.createElement("div");
    dddiv.className = "uploader";
    dddiv.appendChild(ddfile);
    document.getElementById("preproc-plot").appendChild(dddiv);
}

function IsEmptyObj(obj, categ, label)
{
    if(!obj.hasOwnProperty(categ)){
        return true;
    }
    else if(!obj[categ].hasOwnProperty(label)){
        return true;
    }
    else if(typeof obj[categ][label] != "object"){
        return true;
    }
    else if(Object.keys(GUIConf.input[categ][label]).length == 0){
        return true;
    }
    return false;
}

function ShowDataImport(id)
{
    SetPreprocessPlot();
    let item = GetItemFromID(id);
    document.getElementById("preproc-tab").click();
    let select = document.getElementById("preproc-select");
    SetSelection(select, item.item);
    ArrangePPPanel();
}

// functions specific to simplex
function SetUndulatorDataList()
{
    GUIConf.GUIpanels[UndLabel].SetUdataGrid(GUIConf.input[UndDataLabel].names);
}

function SetPreprocessUData()
{
    let select = document.getElementById("preproc-udata-select");
    select.innerHTML = "";
    SetSelectMenus(select, GUIConf.input[UndDataLabel].names, [], "", true);
}

function ImportUData()
{
    GUIConf.fileid = "preproc-udata";
    document.getElementById("file-main").setAttribute("multiple", true);
    document.getElementById("file-main").click();
    document.getElementById("file-main").removeAttribute("multiple");
}

function EditUData(type)
{
    if(type <= 0){
        let msg = type == 0 ? "Clear all the imported data sets. OK?" : "Delete the data set currently selected. OK?";
        let result = window.confirm(msg);
        if(result == false){
            return;
        }
    }
    let select = document.getElementById("preproc-udata-select");
    if(select.options.length == 0){
        return;
    }    
    if(type == 0){ // clear
        GUIConf.input[UndDataLabel].names = [];
        GUIConf.input[UndDataLabel].data = [];
        select.innerHTML = "";
        CreateUploadArea("preproc-udata", true);
        SetUndulatorDataList();
        return;
    }
    let currdata = GetSelections(select);
    let curroption = select.options[currdata.index[0]];
    let index = GUIConf.input[UndDataLabel].names.indexOf(currdata.value[0]);
    if(type == 1){ // rename
        let input = document.createElement("input");
        input.setAttribute("type", "text");
        input.className = "w-100";
        input.value = curroption.value;

        ShowDialog("Rename the undulator data", true, false, "Input a new data name", input, () => {
            curroption.innerHTML = curroption.value = input.value;
            GUIConf.input[UndDataLabel].names[index] = input.value;
            SetUndulatorDataList();
        });
    }
    else{ // delete
        select.removeChild(curroption);
        GUIConf.input[UndDataLabel].names.splice(index, 1);
        GUIConf.input[UndDataLabel].data.splice(index, 1);
        if(select.options.length > 0){
            select.selectedIndex = 0;
            select.options[0].setAttribute("selected", true);
            UpdateUDPlot();                
        }
        else{
            CreateUploadArea("preproc-udata", true);
        }
        SetUndulatorDataList();
    }
}

function RunMbunchEvaluation()
{
    DrawPPPlot(PPMicroBunchLabel);
}

function PlotMbunchEvaluation()
{
    let ppitem = GetPPItem("preproc-seed-select");
    if(ppitem == null){
        return;
    }
    let obj = GUIConf.mbobjs[ppitem];
    DrawPreprocObj(ppitem, obj);
}

function UpdateUDPlot()
{
    ["optimize", "import", "units"].forEach((label) => {
        document.getElementById(GetPreprocID(label)).classList.add("d-none");        
    });
   if(GUIConf.input[UndDataLabel].data.length == 0){
        CreateUploadArea("preproc-udata", true);
        return;
    }
    UpdatePlot(UndDataLabel);
}

function ExportBunchProfile()
{
    let items = new Array(SliceTitles.length);
    let slices = GUIConf.slice_prms[0].length;
    let data = new Array(slices+1);
    data[0] = "\""+SliceTitles.join("\"\t\"")+"\"";
    for(let ns = 0; ns < slices; ns++){
        for(let j = 0; j < SliceTitles.length; j++){
            items[j] = GUIConf.slice_prms[j][ns].toExponential(5);
        }
        data[ns+1] = items.join("\t");
    }
    ExportAsciiData(data.join("\n"), "bunchprof");
}

function ApplyPPResult(ppitem, obj)
{
    let keys = Object.keys(PreProcRespObjs);
    if(obj.hasOwnProperty(RetInfLabel)){
        GUIConf.input[PrePLabel] = GUIConf.GUIpanels[PrePLabel].JSONObj; // to save in the parameter file
        Object.keys(obj[RetInfLabel]).forEach((el) => {
            GUIConf.input[PrePLabel][el] = obj[RetInfLabel][el];
            if(keys.indexOf(el) >= 0){
                if(Array.isArray(obj[RetInfLabel][el])){
                    GUIConf.input[PreProcRespObjs[el][0]][PreProcRespObjs[el][1]] = Array.from(obj[RetInfLabel][el]);
                }
                else{
                    GUIConf.input[PreProcRespObjs[el][0]][PreProcRespObjs[el][1]] = obj[RetInfLabel][el];
                }
            }
        });
        GUIConf.GUIpanels[PrePLabel].SetPanel();
        if(obj[RetInfLabel].hasOwnProperty(PreProcessPrmLabel.avbetaxy[0])){
            let avxy = obj[RetInfLabel][PreProcessPrmLabel.avbetaxy[0]];
            GUIConf.input[FELLabel][FELPrmsLabel.avgbetavalue[0]] = Math.sqrt(avxy[0]*avxy[1]);
            UpdateFELPrms();
            GUIConf.GUIpanels[FELLabel].SetPanel();
        }
    }
    else if(ppitem == PPOptBetaLabel){
        Alert("Twiss parameters consistent with the current condition do not exist.");
        return;
    }
    if(ppitem == PPOptBetaLabel){
        GUIConf.GUIpanels[LatticeLabel].SetPanel();
    }
    if(ppitem == PPOptBetaLabel || ppitem == PPBetaLabel){
        UpdateEBeam();
        GUIConf.GUIpanels[EBLabel].SetPanel();
    }
}

function ApplyMicroBunch(obj)
{
    GUIConf.mbobjs = {};
    let items = [EtDistLabel, CurrentProfLabel, EtProfLabel];
    let curr = GetPPItem("preproc-seed-select");
    if(curr == null){
        curr = EtDistLabel;
    }
    for(let j = items.length-1; j >= 0; j--){
        if(obj.hasOwnProperty(items[j])){
            GUIConf.mbobjs[items[j]] = obj[items[j]];
            if(items[j] == EtProfLabel){
                // 1d -> 2d
                let nc = GUIConf.mbobjs[EtProfLabel].data[0].length;
                let nr = GUIConf.mbobjs[EtProfLabel].data[1].length;
                let tmp = Array.from(GUIConf.mbobjs[EtProfLabel].data[2]);
                GUIConf.mbobjs[EtProfLabel].data[2] = new Array(nr);
                for(let n = 0; n < nr; n++){
                    GUIConf.mbobjs[EtProfLabel].data[2][n] = tmp.slice(n*nc, n*nc+nc);
                }
            }
        }
        else{
            items.splice(j, 1);
        }
    }            
    let select = document.getElementById("preproc-seed-select");
    if(items.length == 0){
        select.classList.add("d-none");
        Alert("No pre-processing results found.");
        return;        
    }
    document.getElementById("preproc-seed-select-div").classList.replace("d-none", "d-flex");
    SetSelectMenus(document.getElementById("preproc-seed-select"), items, [], curr);
    if(items.indexOf(EtDistLabel) >= 0){
        GUIConf.input[MBunchEvalLabel] = GUIConf.GUIpanels[MBunchEvalLabel].JSONObj; // to save in the parameter file
        if(GUIConf.mbobjs[EtDistLabel].hasOwnProperty(RetInfLabel)){
            GUIConf.GUIpanels[MBunchEvalLabel].JSONObj[EvalMBunchLabel.mbr56[0]] = 
                GUIConf.mbobjs[EtDistLabel][RetInfLabel][EvalMBunchLabel.mbr56[0]];
            GUIConf.GUIpanels[MBunchEvalLabel].SetPanel();
        }
    }
    PlotMbunchEvaluation();
}

