"use strict";

var ConvertKeys = {};
var UModelKeys = {};

// EBLabel
ConvertKeys["E_GeV"] = "eenergy";
ConvertKeys["BunchL_m"] = "bunchleng";
ConvertKeys["BunchQ_nC"] = "bunchcharge";
ConvertKeys["Emittancex_pi_mm_mrad"] = ["emitt", 0];
ConvertKeys["Emittancey_pi_mm_mrad"] = ["emitt", 1];
ConvertKeys["E_spread"] = "espread";
ConvertKeys["echirp"] = "echirp";
ConvertKeys["disprsionx"] = ["eta", 0];
ConvertKeys["bunchtype"] = "bmprofile";
ConvertKeys["istwissatpeak"] = "twissbunch";
ConvertKeys["r56l1"] = "r56";
ConvertKeys["DistributionFile"] = "partfile";
ConvertKeys["BunchProfileName"] = "slicefile";

// UndLabel
ConvertKeys["Ky"] = "K";
ConvertKeys["kxyphi"] = "epukratio";
ConvertKeys["lambda_u_cm"] = "lu";
ConvertKeys["L1seg"] = "length";
ConvertKeys["segments"] = "segments";
ConvertKeys["Lintseg"] = "interval";
ConvertKeys["tapertype"] = "taper";
ConvertKeys["magmodeltype"] = "umodel";
ConvertKeys["undtype"] = "utype";
ConvertKeys["UndMultiHarm"] = "multiharm";

// UndLabel/Taper
ConvertKeys["taperstartseg"] = "initial";
ConvertKeys["kinkinterv"] = "incrseg";
ConvertKeys["lintaper"] = "base";
ConvertKeys["taperincr"] = "incrtaper";

// UndLabel/UModel
ConvertKeys["modelseed"] = "umrandseed";
ConvertKeys["locperr"] = "berr";
ConvertKeys["erramp"] = "phaseerr";
ConvertKeys["errorbitx"] = ["xyerr", 0];
ConvertKeys["errorbity"] = ["xyerr", 1];
UModelKeys["tgtsegerrran"] = "segment";

// ChicaneLabel
ConvertKeys["ssdipoleB"] = "dipoleb";
ConvertKeys["ssdipoleL"] = "dipolel";
ConvertKeys["ssdipoleD1"] = "dipoled";
ConvertKeys["sspos"] = "chpos";
ConvertKeys["ssmonoThick"] = "xtalthickness";
ConvertKeys["ssmonotiming"] = "reltiming";
ConvertKeys["chicaneon"] = "chicaneon";
ConvertKeys["monotype"] = "monotype";
ConvertKeys["xtalin"] = "monotype";
ConvertKeys["xtaltype"] = "xtaltype";
ConvertKeys["ssrearrchicane"] = "rearrange";
ConvertKeys["SelfSeedFilterName"] = "monodata";

// WakeLabel
ConvertKeys["aperture"] = "aperture";
ConvertKeys["resistivity"] = "resistivity";
ConvertKeys["relaxtime"] = "relaxtime";
ConvertKeys["rough_height"] = "height";
ConvertKeys["rough_length"] = "corrlen";
ConvertKeys["synchro_diel"] = "permit";
ConvertKeys["synchro_thickness"] = "thickness";
ConvertKeys["enable_wake"] = "wakeon";
ConvertKeys["enable_resist"] = "resistive";
ConvertKeys["enable_roughness"] = "roughness";
ConvertKeys["enable_synchro"] = "dielec";
ConvertKeys["enable_addition"] = "wakecustom";
ConvertKeys["enable_spc"] = "spcharge";
ConvertKeys["is_paraplate"] = "paralell";
ConvertKeys["WakeFieldName"] = "wakecustomdata";

// SeedLabel
ConvertKeys["power"] = "pkpower";
ConvertKeys["lambda"] = "relwavelen";
ConvertKeys["seedbmsize"] = "spotsize";
ConvertKeys["waist_pos"] = "waistpos";
ConvertKeys["sigma_t"] = "pulselen";
ConvertKeys["pulseenergy"] = "pulseenergy";
ConvertKeys["offset_t"] = "timing";
ConvertKeys["gdd"] = "gdd";
ConvertKeys["isshotpower"] = "seedprofile";

// LatticeLabel
ConvertKeys["focusg"] = "qfg";
ConvertKeys["defocusg"] = "qdg";
ConvertKeys["length"] = "qfl";
ConvertKeys["length2"] = "qdl";
ConvertKeys["interval"] = "dist";
ConvertKeys["periods"] = "lperiods";
ConvertKeys["betaxini"] = ["betaxy0", 0];
ConvertKeys["betayini"] = ["betaxy0", 1];
ConvertKeys["alphaxini"] = ["alphaxy0", 0];
ConvertKeys["alphayini"] = ["alphaxy0", 1];
ConvertKeys["type"] = "ltype";

// SimCondLabel
ConvertKeys["seed"] = "randseed";
ConvertKeys["step"] = "step";
ConvertKeys["maxharmonic"] = "maxharmonic";
ConvertKeys["electrons"] = "slicebmlets";
ConvertKeys["divisions"] = "particles";
ConvertKeys["xyrange"] = "spatwin";
ConvertKeys["xymesh"] = "gpointsl";
ConvertKeys["bunchtail"] = ["simrange", 0];
ConvertKeys["bunchhead"] = ["simrange", 1];
ConvertKeys["timedep"] = "simmode";
ConvertKeys["autostep"] = "autostep";
ConvertKeys["sketype"] = "kick";

// DispersionLabel
ConvertKeys["ebdxini"] = ["exy", 0];
ConvertKeys["ebdyini"] = ["exy", 1];
ConvertKeys["ebdxdini"] = ["exyp", 0];
ConvertKeys["ebdydini"] = ["exyp", 1];
ConvertKeys["pbdxini"] = ["sxy", 0];
ConvertKeys["pbdyini"] = ["sxy", 1];
ConvertKeys["pbdxdini"] = ["sxyp", 0];
ConvertKeys["pbdydini"] = ["sxyp", 1];
ConvertKeys["z"] = "kickpos";
ConvertKeys["L"] = "";
ConvertKeys["Bx"] = ["kickangle", 0];
ConvertKeys["By"] = ["kickangle", 1];

// DataOutPrmsLabel
ConvertKeys["bendonly"] = "expstep";

const SkipCategories = [
    "[CUSTOMBEAM]", "[INPUTBEAM]", "[TWISSDATA]", "[MAGDATA]", "[USEGCONFIG]", 
    "[SEEDFILTERING]", "[FOCUSINGDATA]", "[STEERINGDATA]", "[TRAJECTORY]", 
    "@ProcessNo", "@ScanProcessNo",
    "[ZPOSCONFIGS]", "[SLICECONFIGS]", "[ORIGINALCURR]", "[VERSION]", "[CURR4S2E]",
	"[CRYSTALS]", "</EDIT>"
];

var ConvertObjs = {};
ConvertObjs["[ACCELERATOR]"] = [EBLabel, EBeamPrmsLabel];
ConvertObjs["[INPUTFIELD]"] = [SeedLabel, SeedPrmsLabel];
ConvertObjs["[SOURCE]"] = [UndLabel, UndPrmsLabel];
ConvertObjs["[WAKE]"] = [WakeLabel, WakePrmsLabel];
ConvertObjs["[FOCUSING]"] = [LatticeLabel, LatticePrmsLabel];
ConvertObjs["[SELFSEED]"] = [ChicaneLabel, ChicanePrmsLabel];
ConvertObjs["[BPMALIGN]"] = [AlignmentLabel, AlignErrorUPrmsLabel];
ConvertObjs["[TRAJECTORYSPEC]"] = [DispersionLabel, DispersionPrmsLabel];
ConvertObjs["[CALCULATION]"] = [SimCondLabel, SimCtrlsPrmsLabel];
ConvertObjs["[OUTPUTDATA]"] = [DataDumpLabel, DataOutPrmsLabel];
ConvertObjs["[INPUTSPX]"] = [SPXOutLabel, ImportSPXOutLabel];

const LabelDataName = [
    "[BUNCHDATA]", "[WAKEDATA]", "[MONOCUSTOM]", "[MULTIHARM]"
];

function ConvertFile(data)
{
    var DataCont = [{}, {}, {}, {}];
    let objs = CopyJSON(GUIConf.default);
    let linesr = data.split(/\n|\r/);
    let category = null;
    let categlabel = null;
    let dataname = null;
    let xtalin, edump, fdump, bpmtype, uend, stepint;
    let categnames = Object.keys(ConvertObjs);
    let convkeys = Object.keys(ConvertKeys);
    let umkeys = Object.keys(UModelKeys);

    let lines = []
    for(let n = 0; n < linesr.length; n++){
        if(linesr[n].trim().length > 0){
            lines.push(linesr[n]);
        }
    }

    let kickon = false;
    let kickL;
    for(let n = 0; n < lines.length; n++){
        let skipidx = SkipCategories.indexOf(lines[n]);
        if(skipidx >= 0){
            category = null;
            continue;
        }
        let idx = categnames.indexOf(lines[n]);
        let didx = LabelDataName.indexOf(lines[n]);
        if(idx >= 0){
            category = ConvertObjs[lines[n]][0];
            categlabel = ConvertObjs[lines[n]][1];
            objs[category] = {};
            continue;
        }
        else if(didx >= 0){
            category = didx;
            dataname = "none";
            if(n < lines.length-1){
                let dhdrs = lines[n+1].split("\t");
                if(dhdrs.length > 1){
                    dataname = dhdrs[1];
                }
            }
            DataCont[category][dataname] = [];
            n++;
            continue;
        }
        else if(category != null){
            if(typeof category == "number"){
                if(lines[n].length > 1){
                    DataCont[category][dataname].push(lines[n]);
                }
                continue;
            }
            let items = lines[n].split("\t");
            if(items.length < 2){
                continue;
            }
            if(category == SPXOutLabel){
                continue;
            }
            if(items[0] == "edump"){
                edump = parseInt(items[1]) > 0;
                continue;
            }
            if(items[0] == "fdump"){
                fdump = parseInt(items[1]) > 0;
                continue;
            }
            if(items[0] == "trajecerrtype"){
                bpmtype = parseInt(items[1]);
                continue;
            }
            if(items[0] == "L"){
                kickL = parseFloat(items[1]);
                continue;
            }
            if(items[0] == "bendonly"){
                uend = parseInt(items[1]) > 0;
                continue;
            }
            if(items[0] == "interval" && category == SimCondLabel){
                stepint = parseInt(items[1]);
                continue;
            }

            let itemidx = convkeys.indexOf(items[0]);
            let prmkey, jxy = -1, tgtkeys, tgtlabel;
            let inobj = objs[category];
            if(itemidx >= 0){
                tgtkeys = ConvertKeys[convkeys[itemidx]];
                tgtlabel = categlabel;
            }
            else{
                continue;
            }
            if(Array.isArray(tgtkeys)){
                prmkey = tgtkeys[0];               
                jxy = tgtkeys[1];
            }
            else{
                prmkey = tgtkeys;
            }

            if(!tgtlabel.hasOwnProperty(prmkey)){
                continue;
            }

            if(Array.isArray(tgtlabel[prmkey][1])){
                if(tgtlabel[prmkey].length > 2 && tgtlabel[prmkey][2] == SelectionLabel){
                    let selidx = parseInt(items[1]);
                    if(items[0] == "bunchtype"){
                        inobj[tgtlabel[prmkey][0]] = BunchType(selidx);
                    }
                    else if(items[0] == "isshotpower"){
                        inobj[tgtlabel[prmkey][0]] = SeedType(selidx);
                    }
                    else if(items[0] == "timedep"){
                        inobj[tgtlabel[prmkey][0]] = SimulationType(selidx);
                    }
                    else if(items[0] == "type"){
                        inobj[tgtlabel[prmkey][0]] = LatticeType(selidx);
                    }
                    else if(items[0] == "tapertype"){
                        inobj[tgtlabel[prmkey][0]] = TaperType(selidx);
                    }
                    else if(items[0] == "magmodeltype"){
                        inobj[tgtlabel[prmkey][0]] = UModelType(selidx);
                        inobj[UndPrmsLabel.allsegment[0]] = selidx == 2;
                    }
                    else if(items[0] == "monotype"){
                        inobj[tgtlabel[prmkey][0]] = MonochromatorType(selidx);
                    }
                    else if(items[0] == "xtalin"){
                        xtalin = selidx;
                        continue;
                    }
                    else{
                        if(selidx < 0 || selidx >= tgtlabel[prmkey][1].length){
                            selidx = 0;
                        }
                        inobj[tgtlabel[prmkey][0]] = tgtlabel[prmkey][1][selidx];
                    }
                }
                else if(jxy >= 0){
                    if(!inobj.hasOwnProperty(tgtlabel[prmkey][0])){
                        inobj[tgtlabel[prmkey][0]] = [0, 0];
                    }
                    inobj[tgtlabel[prmkey][0]][jxy] = parseFloat(items[1]);
                    if(items[0] == "Bx" || items[0] == "By"){
                        kickon = true;
                    }
                    else if(items[0] == "errorbitx" || items[0] == "errorbity"){
                        inobj[tgtlabel[prmkey][0]][jxy] *= 0.001;
                    }
                }
            }
            else if(tgtlabel[prmkey][1] == PlotObjLabel 
                    || tgtlabel[prmkey][1] == GridLabel || tgtlabel[prmkey][1] == FileLabel){
                inobj[tgtlabel[prmkey][0]] = items[1];
            }
            else if(typeof tgtlabel[prmkey][1] == "boolean"){
                inobj[tgtlabel[prmkey][0]] = items[1] > 0;
            }
            else{
                inobj[tgtlabel[prmkey][0]] = parseFloat(items[1]);
                if(items[0] == "lambda_u_cm"){
                    inobj[tgtlabel[prmkey][0]] *= 10;
                }
                else if(items[0] == "sigma_t"){
                    inobj[tgtlabel[prmkey][0]] *= 1e15/CC*Sigma2FWHM;
                }
                else if(items[0] == "seedbmsize"){
                    inobj[tgtlabel[prmkey][0]] *= Sigma2FWHM;
                }
                else if(items[0] == "offset_t"){
                    inobj[tgtlabel[prmkey][0]] *= 1e15/CC;
                }
                else if(items[0] == "electrons"){
                    inobj[tgtlabel[prmkey][0]] *= -1;
                }
                else if(items[0] == "Ky"){
                    inobj[UndPrmsLabel.Kperp[0]] = inobj[tgtlabel[prmkey][0]];
                }
                else if(items[0] == "xymesh"){
                    let nd = inobj[tgtlabel[prmkey][0]];
                    inobj[tgtlabel[prmkey][0]] = 1;
                    let nfft = 32;
                    while(nfft < nd){
                        nfft <<= 1;
                        inobj[tgtlabel[prmkey][0]]++;
                    }

                }
            }
        }
    }
    objs[EBLabel][EBeamPrmsLabel.bunchlenr[0]] = objs[EBLabel][EBeamPrmsLabel.bunchleng[0]];
    if(xtalin == false){
        objs[ChicaneLabel][ChicanePrmsLabel.monotype[0]] = NotAvaliable;    
    }
    for(let j = 0; j < 2; j++){
        if(objs[DispersionLabel][DispersionPrmsLabel.exy[0]][j] != 0 || 
                objs[DispersionLabel][DispersionPrmsLabel.exyp[0]][j] != 0){
            objs[DispersionLabel][DispersionPrmsLabel.einjec[0]] = true;
        }
        if(objs[DispersionLabel][DispersionPrmsLabel.sxy[0]][j] != 0 || 
                objs[DispersionLabel][DispersionPrmsLabel.sxyp[0]][j] != 0){
            objs[DispersionLabel][DispersionPrmsLabel.sinjec[0]] = true;
        }
        objs[DataDumpLabel] = CopyJSON(GUIConf.default[DataDumpLabel]);
        objs[DataDumpLabel][DataOutPrmsLabel.particle[0]] = edump;    
        objs[DataDumpLabel][DataOutPrmsLabel.radiation[0]] = fdump;
    }
    objs[DataDumpLabel][DataOutPrmsLabel.expstep[0]] = uend ? DumpUndExitLabel : RegularIntSteps;
    objs[DataDumpLabel][DataOutPrmsLabel.stepinterv[0]] = stepint;
    if(objs[EBLabel][EBeamPrmsLabel.slicefile[0]] != ""){
        if(Object.keys(DataCont[0]).indexOf(objs[EBLabel][EBeamPrmsLabel.slicefile[0]]) >= 0){
            let datalines = DataCont[0][objs[EBLabel][EBeamPrmsLabel.slicefile[0]]];
            let bdata = [];
            let beta = Array.from(objs[LatticeLabel][LatticePrmsLabel.betaxy0[0]]);
            let alpha = Array.from(objs[LatticeLabel][LatticePrmsLabel.alphaxy0[0]]);
            for(let j = 0; j < 2; j++){
                beta[j] = beta[j].toString();
                alpha[j] = alpha[j].toString();
            }
            for(let n = 0; n < datalines.length; n++){
                let items = datalines[n].split("\t");
                if(items.length != 10){
                    continue;
                }
                if(isNaN(parseFloat(items[0]))){
                    continue;
                }
                let espread = items[5];
                items.splice(5, 1);
                items.splice(3, 0, espread);                
                items.splice(6, 0, beta[0], beta[1], alpha[0], alpha[1]);
                bdata.push(items.join("\t"));
            }
            bdata = bdata.join("\n");
            let units = new Array(SliceTitles.length);
            GUIConf.ascii[CustomSlice].SetData(bdata);
            objs[EBLabel][EBeamPrmsLabel.slicefile[0]] = GUIConf.ascii[CustomSlice].GetObj();
        }
    }
    let labels = ["", WakeLabel, ChicaneLabel, UndLabel];
    let prmkeys = ["", WakePrmsLabel.wakecustomdata[0], ChicanePrmsLabel.monodata[0], UndPrmsLabel.multiharm[0]];
    let ascname = ["", WakeDataLabel, MonoDataLabel]
    for(let j = 1; j < DataCont.length; j++){
        if(objs[labels[j]][prmkeys[j]] != ""){
            if(Object.keys(DataCont[j]).indexOf(objs[labels[j]][prmkeys[j]]) >= 0){
                let datalines = DataCont[j][objs[labels[j]][prmkeys[j]]];
                if(j == DataCont.length-1){
                    let mcont = [];
                    for(let m = 0; m < datalines.length; m++){
                        let items = datalines[m].split("\t");
                        if(items.length != 5){
                            continue;
                        }
                        let nh = parseInt(items[0]);
                        if(isNaN(nh) || nh < 1){
                            continue;
                        }
                        while(mcont.length < parseInt(nh)){
                            mcont.push([0, 0, 0, 0]);
                        }
                        mcont[nh-1] = [];
                        for(let j = 1; j <= 4; j++){
                            mcont[nh-1].push(parseFloat(items[j]));
                        }
                    }            
                    objs[labels[j]][prmkeys[j]] = mcont;
                }
                else{
                    GUIConf.ascii[ascname[j]].SetData(datalines.join("\n"));
                    objs[labels[j]][prmkeys[j]] = GUIConf.ascii[ascname[j]].GetObj();
                }
            }
        }    
    }
    if(kickon && objs[DispersionLabel][DispersionPrmsLabel.kick[0]]){
        let pcoef = CC/(objs[EBLabel][EBeamPrmsLabel.eenergy[0]]*1e9)*kickL*1000; // rad -> mrad
        for(let j = 0; j < 2; j++){
            objs[DispersionLabel][DispersionPrmsLabel.kickangle[0]][j] *= pcoef;
        }
    }

    let und = objs[UndLabel];
    let lu_m = und[UndPrmsLabel.lu[0]]*1e-3;
    let {K, phi} = GetKValue(und);
    let luk2 = lu_m*(1+K**2/2);
    let gam = objs[EBLabel][EBeamPrmsLabel.eenergy[0]]*1000/MC2MeV;
    let l1 = luk2/2/gam**2;
    objs[EBLabel][EBeamPrmsLabel.r56[0]] *= l1;
    
    objs[AlignmentLabel] = CopyJSON(GUIConf.default[AlignmentLabel]);
    objs[AlignmentLabel][AlignErrorUPrmsLabel.BPMalign[0]] = BPMType(bpmtype);

    let injkeys  = ["exy", "exyp", "sxy", "sxyp"];
    injkeys.forEach((el) => {
        for(let j = 0; j < 2; j++){
            objs[DispersionLabel][DispersionPrmsLabel[el][0]][j] *= 1000; // m,rad -> mm,mrad
        }
    })

    return objs;
}

function BPMType(orgidx)
{
    let sel = IdealLabel;
    if(orgidx == 0){
        sel = IdealLabel;
    }
    else if(orgidx == 1 || orgidx == 2){
        sel = TargetErrorLabel;
    }
    return sel;
}

function BunchType(orgidx)
{
    let sel = GaussianBunch;
    if(orgidx == 0){
        sel = BoxcarBunch;
    }
    else if(orgidx == 1){
        sel = GaussianBunch;
    }
    else if(orgidx == 2){
        sel = CustomSlice;
    }
    else if(orgidx == 3){
        sel = CustomParticle;
    }
    else if(orgidx == 4){
        sel = SimplexOutput;
    }
    else if(orgidx == 5 || orgidx == 6){
        sel = CustomEt;
    }
    return sel;
}

function SeedType(orgidx)
{
    let sel = GaussianPulse;
    if(orgidx == 0 || orgidx == 1){
        sel = GaussianPulse;
    }
    else if(orgidx == 2){
        sel = SimplexOutput;
    }
    else if(orgidx == 3){
        sel = NotAvaliable;
    }
    else if(orgidx == 4){
        sel = ChirpedPulse;
    }
    return sel;
}

function SimulationType(orgidx)
{
    let sel = TimeDepLabel;
    if(orgidx == 0){
        sel = SSLabel;
    }
    else if(orgidx == 1){
        sel = TimeDepLabel;
    }
    else if(orgidx == 2){
        sel = CyclicLabel;
    }
    return sel;
}

function LatticeType(orgidx)
{
    let sel = FUDULabel;
    if(orgidx == 0){
        sel = FUFULabel;
    }
    else if(orgidx == 1){
        sel = FUDULabel;
    }
    else if(orgidx == 2){
        sel = DoubletLabel;
    }
    else if(orgidx == 3){
        sel = TripletLabel;
    }
    else if(orgidx == 4){
        sel = CombinedLabel;
    }
    return sel;
}

function TaperType(orgidx)
{
    let sel = NotAvaliable;
    if(orgidx == 0){
        sel = NotAvaliable;
    }
    else if(orgidx == 2){
        sel = TaperStair;
    }
    else if(orgidx == 1){
        sel = TaperContinuous;
    }
    return sel;
}

function UModelType(orgidx)
{
    let sel = IdealLabel;
    if(orgidx == 0){
        sel = IdealLabel;
    }
    else if(orgidx == 1 || orgidx == 2){
        sel = SpecifyErrLabel;
    }
    else if(orgidx == 3 || orgidx == 4){
        sel = ImportDataLabel;
    }
    return sel;
}

function MonochromatorType(orgidx)
{
    let sel = NotAvaliable;
    if(orgidx == 0){
        sel = XtalTransLabel;
    }
    else if(orgidx == 1){
        sel = XtalReflecLabel;
    }
    return sel;
}

