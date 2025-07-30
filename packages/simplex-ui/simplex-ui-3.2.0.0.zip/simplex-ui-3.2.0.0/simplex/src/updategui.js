"use strict";

function Update(id = null)
{
    let panels = [];
    let item = null;
    if(id == null){
        UpdateEBeam();
        panels = Array.from(InputPanels);
        for(const option of SettingPanels){
            let index = panels.indexOf(option);
            if(index >= 0){
                panels.splice(index, 1);
            }
        }
    }
    else{
        item = GetItemFromID(id);
        if(item.categ == EBLabel){
            UpdateEBeam();
            panels.push(EBLabel);
            panels.push(SeedLabel);
            panels.push(UndLabel);
            panels.push(FELLabel);
            panels.push(LatticeLabel);
            panels.push(SimCondLabel);
            panels.push(DataDumpLabel);
            if(item.item == EBeamPrmsLabel.bmprofile[0]){
                panels.push(SPXOutLabel);
            }
        }
        else if(item.categ == UndLabel || item.categ == FELLabel){
            if(item.categ == FELLabel){
                let EGeV = GUIConf.input[EBLabel][EBeamPrmsLabel.eenergy[0]]
                let und = GUIConf.input[UndLabel];
                let lu = und[UndPrmsLabel.lu[0]]*0.001;
                if(EGeV == null || lu == null){
                    return;
                }
                let e1sttgt;
                if(item.item == FELPrmsLabel.l1st[0]){
                    e1sttgt = ONE_ANGSTROM_eV/(GUIConf.input[FELLabel][FELPrmsLabel.l1st[0]]*10);
                }
                else{
                    e1sttgt = GUIConf.input[FELLabel][FELPrmsLabel.e1st[0]];
                }
                let K2 = 2*((COEF_E1ST*EGeV**2)/(lu*e1sttgt)-1);
                if(K2 > 0){
                    if(und[UndPrmsLabel.utype[0]] == LinearUndLabel){
                        und[UndPrmsLabel.K[0]] = Math.sqrt(K2);
                    }
                    else{
                        und[UndPrmsLabel.Kperp[0]] = Math.sqrt(K2);
                    }           
                }
                if(item.item == FELPrmsLabel.avgbetasel[0] && 
                    GUIConf.input[FELLabel][FELPrmsLabel.avgbetasel[0]] == AvgBetaCurr)
                {
                    DrawPPPlot(PPBetaLabel);
                }
            }
            UpdateUndulatorSimCtrl();
            panels.push(SeedLabel);
            panels.push(UndLabel);
            panels.push(FELLabel);
            panels.push(LatticeLabel);
            panels.push(SimCondLabel);
            panels.push(DataDumpLabel);
        }
        else if(item.categ == LatticeLabel){
            panels.push(PrePLabel);
        }
        else if(item.categ == SeedLabel){
            UpdateSeedPrms(item.item);
            panels.push(SeedLabel);
            if(item.item == SeedPrmsLabel.seedprofile[0]){
                panels.push(SimCondLabel);
                panels.push(SPXOutLabel);
            }
        }
        else if(item.categ == SPXOutLabel){
            panels.push(SPXOutLabel);
            if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == SimplexOutput){
                panels.push(EBLabel);
            }
            if(item.item == ImportSPXOutLabel.spxfile[0]){
                UpdateOutputData();
                panels.push(DataDumpLabel);
            }
        }
        else if(item.categ == SimCondLabel && (
                item.item == SimCtrlsPrmsLabel.autostep[0] || item.item == SimCtrlsPrmsLabel.simmode[0] ||
                item.item == SimCtrlsPrmsLabel.simoption[0] || item.item == SimCtrlsPrmsLabel.autostep[0] ||
                item.item == SimCtrlsPrmsLabel.step[0] || item.item == SimCtrlsPrmsLabel.beamlets[0] ||
                item.item == SimCtrlsPrmsLabel.maxharmonic[0] || item.item == SimCtrlsPrmsLabel.simrange[0] ||
                item.item == SimCtrlsPrmsLabel.spatwin[0] || item.item == SimCtrlsPrmsLabel.gpointsl[0] || 
                item.item == SimCtrlsPrmsLabel.simpos[0] || item.item == SimCtrlsPrmsLabel.skipwave[0]
                ))
        {
            if(item.item == SimCtrlsPrmsLabel.simoption[0]){
                UpdateEBeam();
                panels.push(EBLabel);
                panels.push(ChicaneLabel);
            }
            else if(item.item == SimCtrlsPrmsLabel.skipwave[0]){
                panels.push(ChicaneLabel);
            }
            else{
                UpdateUndulatorSimCtrl();
            }
            panels.push(UndLabel);
            panels.push(SimCondLabel);
            
            panels.push(DataDumpLabel);
        }
        else if(item.categ == DataDumpLabel){
            UpdateOutputData();
            panels.push(DataDumpLabel);
        }
        else if(item.categ == WakeLabel){
            panels.push(UndLabel);
        }
        else if(item.categ == ChicaneLabel){
            UpdateChicanePrms(item.item);
            panels.push(ChicaneLabel);
            if(item.item == ChicanePrmsLabel.chicaneon[0]){
                UpdateUndulatorSimCtrl();
                panels.push(SimCondLabel);
                panels.push(DataDumpLabel);
            }
        }
    }

    for(let j = 0; j < panels.length; j++){
        GUIConf.GUIpanels[panels[j]].SetPanel();
    }
}

function UpdateEBBaseSpecs()
{
    let ebobj = GUIConf.input[EBLabel];
    let type = ebobj[EBeamPrmsLabel.bmprofile[0]];
    let orgobj;
    if(type == GaussianBunch || type == BoxcarBunch){
        orgobj = ebobj[EBeamPrmsLabel.basespec[0]];
    }
    else if(type == SimplexOutput){
        if(GUIConf.hasOwnProperty("spxobj")){
            ebobj[EBeamPrmsLabel.eenergy[0]] = GUIConf.spxobj[AvgEnergyLabel];
            ebobj[EBeamPrmsLabel.emitt[0]] = Array.from(GUIConf.spxobj[SliceEmittanceLabel]);
            ebobj[EBeamPrmsLabel.espread[0]] = GUIConf.spxobj[SliceEspreadLabel];
            ebobj[EBeamPrmsLabel.pkcurr[0]] = GUIConf.spxobj[PeakCurrLabel];    
        }
        return;
    }
    else if(type == CustomSlice){
        if(!ebobj[EBeamPrmsLabel.slicefile[0]].hasOwnProperty(SpecsLabel)){
            orgobj = {};
        }
        else{
            orgobj = ebobj[EBeamPrmsLabel.slicefile[0]][SpecsLabel];
        }
    }
    else if(type == CustomParticle){
        orgobj = ebobj[EBeamPrmsLabel.partspec[0]];
    }
    else{
        let label = type == CustomCurrent ? EBeamPrmsLabel.currfile[0] : EBeamPrmsLabel.etfile[0] ;
        if(!ebobj[label].hasOwnProperty(SpecsLabel)){
            orgobj = {};
        }
        else{
            orgobj = ebobj[label][SpecsLabel];
        }
        let prms = [EBeamPrmsLabel.eenergy[0], EBeamPrmsLabel.emitt[0]];
        if(type == CustomCurrent){
            prms.push(EBeamPrmsLabel.espread[0]);
        }
        for(let j = 0; j < prms.length; j++){
            orgobj[prms[j]] = ebobj[prms[j]] == null ? ebobj[EBeamPrmsLabel.basespec[0]][prms[j]] : ebobj[prms[j]];
        }
    }
    UpdateEBBaseNormal(ebobj, orgobj);
}

function UpdateEBeam()
{
    let ebm = GUIConf.input[EBLabel];
    if(ebm[EBeamPrmsLabel.bmprofile[0]] == BoxcarBunch){
        ebm[EBeamPrmsLabel.pkcurr[0]] = 
            ebm[EBeamPrmsLabel.bunchcharge[0]]*1e-9/(ebm[EBeamPrmsLabel.bunchlenr[0]]/CC);
    }
    else if(ebm[EBeamPrmsLabel.bmprofile[0]] == GaussianBunch){
        ebm[EBeamPrmsLabel.pkcurr[0]] = 
            ebm[EBeamPrmsLabel.bunchcharge[0]]*1e-9/(ebm[EBeamPrmsLabel.bunchleng[0]]*Math.sqrt(2*Math.PI)/CC);
    }

    for(let j = 0; j < 2; j++){
        ebm[EBeamPrmsLabel.ebmsize[0]][j] = null;
        ebm[EBeamPrmsLabel.ediv[0]][j] = null;
    }
    let chkprms = [
        ebm[EBeamPrmsLabel.eenergy[0]],
        ebm[EBeamPrmsLabel.espread[0]],
        ebm[EBeamPrmsLabel.eta[0]],
        ebm[EBeamPrmsLabel.emitt[0]],
    ];
    if(!chkprms.includes(null)){
        let etap = 0;
        let lattice = GUIConf.input[LatticeLabel];
        let espread = ebm[EBeamPrmsLabel.espread[0]];
        let gamma = ebm[EBeamPrmsLabel.eenergy[0]]*1e3/MC2MeV;
        for(let j = 0; j < 2; j++){
            let alpha = lattice[LatticePrmsLabel.alphaxy0[0]][j];
            let beta = lattice[LatticePrmsLabel.betaxy0[0]][j];
            let eta = ebm[EBeamPrmsLabel.eta[0]][j];
            let nemitt = ebm[EBeamPrmsLabel.emitt[0]][j]/gamma*1e-6;
            ebm[EBeamPrmsLabel.ebmsize[0]][j]
            = Math.sqrt(beta*nemitt+(espread*eta)**2)*1000.0;
            ebm[EBeamPrmsLabel.ediv[0]][j]
            = Math.sqrt((1.0+alpha**2)*nemitt/beta+(espread*etap)**2)*1000.0;
        }    
    }
    UpdateUndulatorSimCtrl();
}

function UpdateEBBase()
{
    if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == CustomSlice){
        UpdateEBBaseSlice();
    }
    else if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == CustomEt){
        UpdateEBBaseEt();
    }
    else if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == CustomCurrent){
        UpdateEBBaseCurrProf();
    }
    else if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == CustomParticle){
        if(GUIConf.input[EBLabel].hasOwnProperty(EBeamPrmsLabel.partspec[0])){
            let partspec = GUIConf.input[EBLabel][EBeamPrmsLabel.partspec[0]];
            if(partspec.hasOwnProperty(CurrentProfLabel)){
                GUIConf.qprofile = [
                    Array.from(partspec[CurrentProfLabel][0]),
                    Array.from(partspec[CurrentProfLabel][0])    
                ];
            }
            UpdateEBBaseNormal(GUIConf.input[EBLabel], partspec);
        }
    }
    else{
        UpdateEBBaseNormal(GUIConf.input[EBLabel][EBeamPrmsLabel.basespec[0]], GUIConf.input[EBLabel]);
    }
    let id = GetIDFromItem(EBLabel, EBeamPrmsLabel.bmprofile[0], -1);
    UpdateOptions(id);
}

function UpdateEBBaseNormal(target, original)
{
    EBBasePrmLabels.forEach((el) => {
        if(!original.hasOwnProperty(el)){
            target[el] = null;
        }
        else if(Array.isArray(original[el])){
            target[el] = Array.from(original[el]);
        }
        else{
            target[el] = original[el];
        }
    });
}

function UpdateEBBaseSlice()
{
    let specs = GetEBeamSpecSlice(GUIConf.input[EBLabel][EBeamPrmsLabel.slicefile[0]].data);
    GUIConf.input[EBLabel][EBeamPrmsLabel.slicefile[0]][SpecsLabel] = specs;

    let data = GUIConf.input[EBLabel][EBeamPrmsLabel.slicefile[0]].data;
    SetChargeProfile(data[0], data[1]);

}

function UpdateEBBaseEt()
{
    let data = GUIConf.input[EBLabel][EBeamPrmsLabel.etfile[0]].data;
    let ns = data[0].length;
    let ne = data[1].length;
    let I = new Array(ns);
    let nmax = 0, Imax = 0;
    for(let n = 0; n < ns; n++){
        I[n] = 0;
        for(let m = 0; m < ne; m++){
            I[n] += data[2][m][n];
        }
        I[n] *= (data[1][ne-1]-data[1][0])/(ne-1);
        if(Imax < I[n]){
            nmax = n;
            Imax = I[n]
        }
    }
    SetChargeProfile(data[0], I);
    let stats = GetStats(data[0], I);

    let eImax = new Array(ne);
    for(let m = 0; m < ne; m++){
        eImax[m] = data[2][m][nmax];
    }
    let esp = GetStats(data[1], eImax).rms;

    GUIConf.input[EBLabel][EBeamPrmsLabel.etfile[0]][SpecsLabel] = 
    {
        [EBeamPrmsLabel.bunchcharge[0]]: stats.area*1e+9/CC, // C -> nC
        [EBeamPrmsLabel.bunchleng[0]]: stats.rms,
        [EBeamPrmsLabel.pkcurr[0]]: Imax,
        [EBeamPrmsLabel.espread[0]]: esp,
    };     
}

function UpdateEBBaseCurrProf()
{
    let data = GUIConf.input[EBLabel][EBeamPrmsLabel.currfile[0]].data;
    SetChargeProfile(data[0], data[1]);
    let stats = GetStats(data[0], data[1]);
    let Imax = Math.max(...data[1]);

    GUIConf.input[EBLabel][EBeamPrmsLabel.currfile[0]][SpecsLabel] = 
    {
        [EBeamPrmsLabel.bunchcharge[0]]: stats.area*1e+9/CC, // C -> nC
        [EBeamPrmsLabel.bunchleng[0]]: stats.rms,
        [EBeamPrmsLabel.pkcurr[0]]: Imax
    };     
}

function GetNetMagnetLength(maglen, z, trunc)
{
    if(z <= 0.0){
        return 0.0;
    }
    let segint = GUIConf.input[UndLabel][UndPrmsLabel.interval[0]];
    let totalseg = GUIConf.input[UndLabel][UndPrmsLabel.segments[0]]; 
    let segment = Math.min(totalseg, Math.ceil(z/segint));
    let position = trunc ? 0 : Math.min(z-(segment-1)*segint, maglen);
    return (segment-1)*maglen+position;
}

function GetRelativeResonance(z = null)
{
    let undobj = GUIConf.input[UndLabel];
	let dztaper, ztini;
    let {K, phi} = GetKValue(undobj);
    let ktaper = K;
    let maglen = undobj[UndPrmsLabel.periods[0]]*undobj[UndPrmsLabel.lu[0]]*1e-3; // mm -> m
	let iniseg = undobj[UndPrmsLabel.initial[0]];
	let seginterv = undobj[UndPrmsLabel.incrseg[0]];
    let segint = undobj[UndPrmsLabel.interval[0]];
    let totalseg = undobj[UndPrmsLabel.segments[0]]; 
    let segment;
    if(z == null){
        z = (totalseg-1)*segint+maglen;
        segment = totalseg;
    }
    else{
        segment = Math.min(totalseg, Math.ceil(z/segint));   
    }
    let type = undobj[UndPrmsLabel.taper[0]];

    if(type != NotAvaliable && type != TaperCustom){
        let rate = undobj[UndPrmsLabel.base[0]];
        while(iniseg <= segment){
			ztini = (iniseg-1)*segint; 
			if(type == TaperStair){
				ztini -= segint;
			}
            dztaper = GetNetMagnetLength(maglen, z-ztini, type == TaperStair);
            ktaper += rate*dztaper;
            iniseg += Math.max(1, seginterv);
            rate = undobj[UndPrmsLabel.incrtaper[0]];
		};
    }

    let phase = (1+ktaper**2/2)/(1+K**2/2)-1;
    return {phase:phase, Ktaper:ktaper};
}

function UpdateTimeDelay(uitem)
{
    let sdelay;
    let obj = GUIConf.input[ChicaneLabel];
    let gamma = GUIConf.input[EBLabel][EBeamPrmsLabel.eenergy[0]]*1e3/MC2MeV;
    let drift = GUIConf.input[UndLabel][UndPrmsLabel.interval[0]]-
        GUIConf.input[UndLabel][UndPrmsLabel.periods[0]]*GUIConf.input[UndLabel][UndPrmsLabel.lu[0]]*1e-3;
    let Lchicane = GUIConf.input[UndLabel][UndPrmsLabel.interval[0]]+drift;
    let LintD = obj[ChicanePrmsLabel.dipoled[0]];
    let LD = obj[ChicanePrmsLabel.dipolel[0]];
    let BD = obj[ChicanePrmsLabel.dipoleb[0]];
    let kicksq;
    if(uitem == ChicanePrmsLabel.delay[0]){
        sdelay = obj[ChicanePrmsLabel.delay[0]]*1e-15*CC; // fs -> s -> m
		sdelay = sdelay*2.0*gamma*gamma-Lchicane;
	    kicksq = sdelay/2.0/(LintD-LD/3.0);
		if(kicksq >= 0.0){
			BD = Math.sqrt(kicksq)/COEF_ACC_FAR_BT/LD;
		}
		else{            
			BD = 0.0;
			sdelay = Lchicane/2.0/gamma/gamma;
            obj[ChicanePrmsLabel.delay[0]] = sdelay/CC*1e15; // m -> fs
		}
        obj[ChicanePrmsLabel.dipoleb[0]] = BD;
    }
    else {
		kicksq = (COEF_ACC_FAR_BT*BD*LD)**2;
		sdelay = kicksq*2.0*(LintD-LD/3.0);
		sdelay = (Lchicane+sdelay)/2.0/gamma/gamma;
        obj[ChicanePrmsLabel.delay[0]] = sdelay/CC*1e15; // m -> fs
    }
    obj[ChicanePrmsLabel.offset[0]] = COEF_ACC_FAR_BT*BD*LD/gamma*obj[ChicanePrmsLabel.dipoled[0]]*1e3;
}

function UpodateXtalType()
{
    let obj = GUIConf.input[ChicaneLabel];

    let wavelnm = ONE_ANGSTROM_eV/obj[ChicanePrmsLabel.monoenergy[0]]*0.1; // nm
	obj[ChicanePrmsLabel.bragg[0]] = Math.abs(wavelnm/2.0/(obj[ChicanePrmsLabel.latticespace[0]]));
	if(obj[ChicanePrmsLabel.bragg[0]] <= 1.0){
		obj[ChicanePrmsLabel.bragg[0]] = Math.asin(obj[ChicanePrmsLabel.bragg[0]])/DEGREE2RADIAN;
	}
    else{
        wavelnm = 2*obj[ChicanePrmsLabel.latticespace[0]];
        obj[ChicanePrmsLabel.monoenergy[0]] = ONE_ANGSTROM_eV/(wavelnm*10); // nm -> A -> eV
        obj[ChicanePrmsLabel.bragg[0]] = 90;
    }
    let thetab = obj[ChicanePrmsLabel.bragg[0]]/90*Math.PI/2;

	let chig= obj[ChicanePrmsLabel.formfactor[0]]/Math.PI*(ERadius*1.0e+9)*wavelnm*wavelnm/obj[ChicanePrmsLabel.unitvol[0]];
	obj[ChicanePrmsLabel.bandwidth[0]] = Math.abs(chig)/2.0/Math.sin(thetab)/Math.sin(thetab);
}

function UpdateChicanePrms(item)
{
    let xtalprms = [
        ChicanePrmsLabel.monotype[0], 
        ChicanePrmsLabel.xtaltype[0], 
        ChicanePrmsLabel.monoenergy[0],
        ChicanePrmsLabel.bragg[0],
        ChicanePrmsLabel.formfactor[0],
        ChicanePrmsLabel.latticespace[0],
        ChicanePrmsLabel.unitvol[0]
    ];
    if(xtalprms.indexOf(item) >= 0){
        UpodateXtalType();
    }
    else{
        UpdateTimeDelay(item);
    }
}

function UpdateUndulatorSimCtrl()
{
    UpdateFELPrms();
    UpdateSeedPrms();

    let und = GUIConf.input[UndLabel];
    let simctrl = GUIConf.input[SimCondLabel];
    let felprm = GUIConf.input[FELLabel];
    let lu_m = und[UndPrmsLabel.lu[0]]*1e-3;
    let {K, phi} = GetKValue(und);
    let luk2 = lu_m*(1+K**2/2);
    und[UndPrmsLabel.peakb[0]] = K/COEF_K_VALUE/lu_m;
    und[UndPrmsLabel.periods[0]] = Math.floor(und[UndPrmsLabel.length[0]]/lu_m);

    let periods = und[UndPrmsLabel.periods[0]];
    if(simctrl[SimCtrlsPrmsLabel.autostep[0]] && felprm[FELPrmsLabel.Lg[0]] != null){
        let steps = felprm[FELPrmsLabel.Lg[0]][1]*GainPerStep/lu_m;
		let n1 = Math.max(1, Math.floor(steps));
		let n2 = Math.max(1, Math.ceil(steps));
		if(n1 == n2){
			simctrl[SimCtrlsPrmsLabel.step[0]] = n1;
		}
		else{
			if(n1*Math.floor(periods/n1) >= n2*Math.floor(periods/n2)){
                simctrl[SimCtrlsPrmsLabel.step[0]] = n1;
			}
			else{
                simctrl[SimCtrlsPrmsLabel.step[0]] = n2;
			}
		}
    }

    und[UndPrmsLabel.periods[0]] -= und[UndPrmsLabel.periods[0]]%simctrl[SimCtrlsPrmsLabel.step[0]];
    let Lu = und[UndPrmsLabel.periods[0]]*lu_m;
    und[UndPrmsLabel.slippage[0]] = Math.floor((und[UndPrmsLabel.interval[0]]-Lu)/luk2);

    if(und[UndPrmsLabel.taper[0]] == TaperContinuous 
            || und[UndPrmsLabel.taper[0]] == TaperCustom 
            || und[UndPrmsLabel.taper[0]] == TaperStair)
    {
        let {phase, Ktaper} = GetRelativeResonance();
        und[UndPrmsLabel.Kexit[0]] = Ktaper;
        und[UndPrmsLabel.detune[0]] = phase;
    }

    let pkcurr = GUIConf.input[EBLabel][EBeamPrmsLabel.pkcurr[0]];
    let slicelen = felprm[FELPrmsLabel.l1st[0]]*1e-9;
    if(pkcurr != null && slicelen != null){
        slicelen *= simctrl[SimCtrlsPrmsLabel.step[0]];
        let simrange = Array.from(simctrl[SimCtrlsPrmsLabel.simrange[0]]);
        if(simctrl[SimCtrlsPrmsLabel.simmode[0]] == SSLabel){
            simrange.fill(simctrl[SimCtrlsPrmsLabel.simpos[0]]);
        }
        simrange[0] -= slicelen*0.5; simrange[1] += slicelen*0.5;
        let charge = GetCharge(simrange);
        if(charge != null){
            let pkratio = pkcurr*(slicelen/CC)/charge;
            if(simctrl[SimCtrlsPrmsLabel.simoption[0]] == RealElectronNumber){
                simctrl[SimCtrlsPrmsLabel.electrons[0]] = charge/QE;
                simctrl[SimCtrlsPrmsLabel.sliceels[0]] = Math.floor(0.5+pkratio*simctrl[SimCtrlsPrmsLabel.electrons[0]]);
                simctrl[SimCtrlsPrmsLabel.sliceelsss[0]] = simctrl[SimCtrlsPrmsLabel.electrons[0]];
            }
            else if(simctrl[SimCtrlsPrmsLabel.slicebmlets[0]] < 0){
                simctrl[SimCtrlsPrmsLabel.slicebmlets[0]] = Math.abs(simctrl[SimCtrlsPrmsLabel.slicebmlets[0]]);
                simctrl[SimCtrlsPrmsLabel.beamlets[0]] = Math.floor(simctrl[SimCtrlsPrmsLabel.slicebmlets[0]]/pkratio+0.5);
            }
            else{
                simctrl[SimCtrlsPrmsLabel.slicebmlets[0]] = Math.floor(0.5+pkratio*simctrl[SimCtrlsPrmsLabel.beamlets[0]]);
            }
        }
    }

    simctrl[SimCtrlsPrmsLabel.slices[0]] = 
        Math.ceil(
            Math.abs(simctrl[SimCtrlsPrmsLabel.simrange[0]][1]-simctrl[SimCtrlsPrmsLabel.simrange[0]][0])
            /(felprm[FELPrmsLabel.l1st[0]]*1e-9*simctrl[SimCtrlsPrmsLabel.step[0]])    
        );

    let nspos = [0, 0];
    for(let j = 0; j < 2 && slicelen != null; j++){
        nspos[j] = Math.floor(0.5+simctrl[SimCtrlsPrmsLabel.simrange[0]][j]/slicelen);
    }
    simctrl[SimCtrlsPrmsLabel.slices[0]] = nspos[1]-nspos[0]+1;  

    simctrl[SimCtrlsPrmsLabel.stepsseg[0]] = und[UndPrmsLabel.periods[0]]/simctrl[SimCtrlsPrmsLabel.step[0]];
    simctrl[SimCtrlsPrmsLabel.driftsteps[0]] = Math.ceil(und[UndPrmsLabel.slippage[0]]/simctrl[SimCtrlsPrmsLabel.step[0]]);
    simctrl[SimCtrlsPrmsLabel.particles[0]] = Math.max(simctrl[SimCtrlsPrmsLabel.particles[0]], 2+2*simctrl[SimCtrlsPrmsLabel.maxharmonic[0]]);
    simctrl[SimCtrlsPrmsLabel.gpoints[0]] = 2**(simctrl[SimCtrlsPrmsLabel.gpointsl[0]]+4);
    UpdateOutputData();
}

function UpdateSeedPrms(item = "")
{
    if(GUIConf.input[SeedLabel][SeedPrmsLabel.seedprofile[0]] == NotAvaliable || 
        GUIConf.input[SeedLabel][SeedPrmsLabel.seedprofile[0]] == SimplexOutput){
        return;
    }
    let sigt = GUIConf.input[SeedLabel][SeedPrmsLabel.pulselen[0]]*1e-15/Sigma2FWHM;
    GUIConf.input[SeedLabel][SeedPrmsLabel.wavelen[0]]
        = GUIConf.input[FELLabel][FELPrmsLabel.l1st[0]]*(1+GUIConf.input[SeedLabel][SeedPrmsLabel.relwavelen[0]]);
    let wavelen = GUIConf.input[SeedLabel][SeedPrmsLabel.wavelen[0]]*1e-9; // nm -> m
    if(GUIConf.input[SeedLabel][SeedPrmsLabel.seedprofile[0]] == ChirpedPulse){
        let GDD = GUIConf.input[SeedLabel][SeedPrmsLabel.gdd[0]]*1e-30; // fs^2 -> s^2
        let sigfl = sigt;
        let pstretch = Math.hypot(1.0, GDD/2.0/sigfl/sigfl);
        GUIConf.input[SeedLabel][SeedPrmsLabel.stplen[0]] = 
            pstretch*GUIConf.input[SeedLabel][SeedPrmsLabel.pulselen[0]];
        sigt = sigfl*pstretch;
        GUIConf.input[SeedLabel][SeedPrmsLabel.chirprate[0]]
            = GDD/8/sigfl**2/sigt/(2*Math.PI*CC/wavelen)*Sigma2FWHM;
    }

    if(item == SeedPrmsLabel.pulseenergy[0]){
        GUIConf.input[SeedLabel][SeedPrmsLabel.pkpower[0]] = 
        GUIConf.input[SeedLabel][SeedPrmsLabel.pulseenergy[0]]/(Math.sqrt(2*Math.PI)*sigt);
    }
    else if(item == SeedPrmsLabel.pkpower[0] 
            || item == SeedPrmsLabel.seedprofile[0]
            || item == SeedPrmsLabel.pulselen[0]){
        GUIConf.input[SeedLabel][SeedPrmsLabel.pulseenergy[0]] = 
        GUIConf.input[SeedLabel][SeedPrmsLabel.pkpower[0]]*Math.sqrt(2*Math.PI)*sigt;
    }
    let waist = GUIConf.input[SeedLabel][SeedPrmsLabel.spotsize[0]]*2*1e-3/Sigma2FWHM;
    GUIConf.input[SeedLabel][SeedPrmsLabel.raylen[0]] = waist*waist/wavelen*Math.PI;
}

function UpdateOutputData()
{
    let ebeam = GUIConf.input[EBLabel];
    let output = GUIConf.input[DataDumpLabel];
    let simctrl = GUIConf.input[SimCondLabel];
    let segments = GUIConf.input[UndLabel][UndPrmsLabel.segments[0]];
    let totalsteps = segments*simctrl[SimCtrlsPrmsLabel.stepsseg[0]]
        +(segments-1)*simctrl[SimCtrlsPrmsLabel.driftsteps[0]];

    let steps;
    if(output[DataOutPrmsLabel.expstep[0]] == DumpSegExitLabel){
        steps = segments;
    }
    else if(output[DataOutPrmsLabel.expstep[0]] == DumpSpecifyLabel){
        steps = Math.ceil((segments-output[DataOutPrmsLabel.iniseg[0]]+1)/output[DataOutPrmsLabel.segint[0]]);
    }
    else if(output[DataOutPrmsLabel.expstep[0]] == RegularIntSteps){
        let nmod = totalsteps%output[DataOutPrmsLabel.stepinterv[0]];
        steps = (totalsteps-nmod)/output[DataOutPrmsLabel.stepinterv[0]];
        if(nmod > 0){
            steps++;
        }
    }
    else  if(output[DataOutPrmsLabel.expstep[0]] == DumpUndExitLabel){
        steps = 1;
    }
    let slices = simctrl[SimCtrlsPrmsLabel.slices[0]];
    if(simctrl[SimCtrlsPrmsLabel.simmode[0]] == SSLabel){
        slices = 1;
    }

    let xydim = 4; // (x, x', y, y')
    let datasize = 4; // byte, size of float
    let etdim = 2 // (t, E)
    let partdatasize = 0;

    if(output[DataOutPrmsLabel.particle[0]]){
        let bmlets, particles;
        if(simctrl[SimCtrlsPrmsLabel.simoption[0]] == RealElectronNumber){
            bmlets = simctrl[SimCtrlsPrmsLabel.electrons[0]];
            if(simctrl[SimCtrlsPrmsLabel.simmode[0]] == SSLabel){
                bmlets = simctrl[SimCtrlsPrmsLabel.sliceelsss[0]];
            }    
        }
        else{
            bmlets = simctrl[SimCtrlsPrmsLabel.beamlets[0]];
            if(simctrl[SimCtrlsPrmsLabel.simmode[0]] == SSLabel){
                bmlets = simctrl[SimCtrlsPrmsLabel.slicebmletsss[0]];
            }    
        }
        particles = simctrl[SimCtrlsPrmsLabel.particles[0]];
        if(simctrl[SimCtrlsPrmsLabel.simoption[0]] == KillQuiteLoad 
                || simctrl[SimCtrlsPrmsLabel.simoption[0]] == RealElectronNumber){
            particles = 1;
        }    
        if(ebeam[EBeamPrmsLabel.bmprofile[0]] == SimplexOutput){
            if(!GUIConf.input.hasOwnProperty(SPXOutLabel)){
                bmlets = null;
                particles = null;
            }
            else{
                let outobj = GUIConf.input[SPXOutLabel];
                bmlets = outobj[ImportSPXOutLabel.bmletsout[0]];
                particles = outobj[ImportSPXOutLabel.paticlesout[0]];    
            }
        }
        if(bmlets == null){
            partdatasize = null;
        }
        else{
            partdatasize = bmlets*xydim*datasize; // initial distribution of 4D phase space
            partdatasize += bmlets*particles*etdim*datasize*steps; // all data for distrition of E-t phase space    
            partdatasize /= 1e6; // byte -> MB
        }
    }
    output[DataOutPrmsLabel.pfilesize[0]] = partdatasize; 

    let raddata = 0;
    if(output[DataOutPrmsLabel.radiation[0]]){
        let grnfft = simctrl[SimCtrlsPrmsLabel.gpoints[0]];
        raddata = steps*slices*grnfft**2*2*datasize;
        if(GUIConf.input[UndLabel][UndPrmsLabel.utype[0]] != LinearUndLabel 
                && GUIConf.input[UndLabel][UndPrmsLabel.utype[0]] != HelicalUndLabel){
            raddata *= 2; // Ex and Ey
        }   
    }
    output[DataOutPrmsLabel.rfilesize[0]] = raddata/1e6; // byte -> MB
}

function UpdateFELPrms()
{
    let ebm = GUIConf.input[EBLabel];
    let IA = ebm[EBeamPrmsLabel.pkcurr[0]];
    let nemitt = ebm[EBeamPrmsLabel.emitt[0]];
    let EGeV = ebm[EBeamPrmsLabel.eenergy[0]];
    let espread = ebm[EBeamPrmsLabel.espread[0]];
    let und = GUIConf.input[UndLabel];
    let lu = und[UndPrmsLabel.lu[0]]*0.001;
    let {K, phi} = GetKValue(und);
    let ebmspecs = new Array(3);
    let felprm = GUIConf.input[FELLabel];

    let betasel = felprm[FELPrmsLabel.avgbetasel[0]];
    let betaval;
    if(betasel == AvgBetaOpt){
        betaval = null
    }
    else if(betasel == AvgBetaCurr){
        betaval = felprm[FELPrmsLabel.avgbetavalue[0]];
        if(betaval == null){
            betaval = -1;
        }
    }
    else{
        betaval = felprm[FELPrmsLabel.inputbeta[0]];
    }

    let felspecs = FEL_specs(IA, nemitt, EGeV, espread, lu, K, phi, ebmspecs, betaval);

    if(felspecs == null){
        Object.keys(FELPrmsLabel).forEach((el) => {
            felprm[FELPrmsLabel[el][0]] =  null;
        });
        return;
    }

    GUIConf.input[LatticeLabel][LatticePrmsLabel.optbeta[0]] = ebmspecs[2];
    felprm[FELPrmsLabel.optbeta[0]] = ebmspecs[2];

    Object.keys(felspecs).forEach((el) => {
        felprm[el] = felspecs[el];
    });

    if(betasel == AvgBetaCurr && betaval <= 0){
        felprm[FELPrmsLabel.avgbetavalue[0]] = null;
        felprm[FELPrmsLabel.Sigxyp[0]] = [null, null];
        felprm[FELPrmsLabel.Sigxy[0]] = [null, null];
        felprm[FELPrmsLabel.pkflux[0]] = null;
        felprm[FELPrmsLabel.pkbrill[0]] = null;
        felprm[FELPrmsLabel.pulseE[0]] = null;
        return;
    }

    let Lsrc = felprm[FELPrmsLabel.Lg[0]][1]*Math.log(10.0);
    let sigmadn = Math.sqrt(felprm[FELPrmsLabel.l1st[0]]/2.0/Lsrc);

    let l1st = felprm[FELPrmsLabel.l1st[0]]*1e-9; // nm -> m
    felprm[FELPrmsLabel.Sigxyp[0]] = new Array(2);
    felprm[FELPrmsLabel.Sigxy[0]] = new Array(2);
    for(let j = 0; j < 2; j++){
        let ebsig = ebmspecs[j]/Math.sqrt(2);
        let phsig = l1st/4.0/Math.PI/ebsig;
        felprm[FELPrmsLabel.Sigxyp[0]][j] = 1.0/Math.hypot(1.0/phsig, 1.0/sigmadn);
        felprm[FELPrmsLabel.Sigxy[0]][j] = l1st/4.0/Math.PI/felprm[FELPrmsLabel.Sigxyp[0]][j];
        felprm[FELPrmsLabel.Sigxyp[0]][j] *= 1e3; // rad -> mrad
        felprm[FELPrmsLabel.Sigxy[0]][j] *= 1e3; // m -> mm
    }

    let flux = 2*Math.sqrt(Math.log(2.0)/Math.PI)*(felprm[FELPrmsLabel.psat[0]]*1.0e+9)
        /(1.0e+3*QE*felprm[FELPrmsLabel.e1st[0]])/felprm[FELPrmsLabel.bandwidth[0]];
    felprm[FELPrmsLabel.pkflux[0]] = flux;
    felprm[FELPrmsLabel.pkbrill[0]] = flux/(l1st*0.5)/(l1st*0.5)*1.0e-12; //  1/m^2rad^2 -> 1/mm^2mrad^2

    let sigmas = ebm[EBeamPrmsLabel.bmprofile[0]] == BoxcarBunch ? 
        ebm[EBeamPrmsLabel.bunchlenr[0]] : ebm[EBeamPrmsLabel.bunchleng[0]]*Math.sqrt(2*Math.PI);
    felprm[FELPrmsLabel.pulseE[0]] = felprm[FELPrmsLabel.psat[0]]*1.0e+9*sigmas/CC;
}

function SetChargeProfile(s, I)
{
    let ns = s.length;
    GUIConf.qprofile = [s, new Array(ns)];
    GUIConf.qprofile[1][0] = 0;
    for(let n = 1; n < ns; n++){
        GUIConf.qprofile[1][n] = GUIConf.qprofile[1][n-1]
            +(I[n-1]+I[n])*(s[n]-s[n-1])/2/CC;
    }
}

function SetExportZ()
{
    let zsteps = GUIConf.input[SPXOutLabel][ImportSPXOutLabel.spxstepzarr[0]];
    if(zsteps.length == 0){
        return;
    }
    let step = zsteps.length-1+GUIConf.input[SPXOutLabel][ImportSPXOutLabel.spxstep[0]];
    GUIConf.input[SPXOutLabel][ImportSPXOutLabel.spxstepz[0]] = zsteps[step];    
}

function IsSPXOut()
{
    let isspx = GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == SimplexOutput
        || GUIConf.input[SeedLabel][SeedPrmsLabel.seedprofile[0]] == SimplexOutput;
    return isspx;
}

function SetSPXOut()
{
    let isspx = IsSPXOut();
    if(isspx){
        document.getElementById("spx-output-card").classList.remove("d-none");
        SetExportZ();
    }
    else{
        document.getElementById("spx-output-card").classList.add("d-none");
    }
}

function ArrangeSPXOutput(tgtid)
{
    SetSPXOut();
    if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == SimplexOutput){
        UpdateEBBaseSpecs();
    }
    Update(tgtid);
}

async function LoadSPXOutput()
{
    if(!GUIConf.input.hasOwnProperty(SPXOutLabel)){
        return Promise.reject(new Error("Current object does not have "+SPXOutLabel+" object."));
    }
    let outobj = GUIConf.input[SPXOutLabel];
    if(!outobj.hasOwnProperty(ImportSPXOutLabel.spxfile[0]) || outobj[ImportSPXOutLabel.spxfile[0]] == ""){
        return Promise.reject(new Error("Current object does not have the SIMPLEX output file name."));
    }
    try {
        let obj = {};
        if(Framework == TauriLabel){
            delete GUIConf.spxobj;
            let data = await window.__TAURI__.tauri.invoke("read_file", { path: outobj[ImportSPXOutLabel.spxfile[0]]});
            obj = JSON.parse(data);    
        }
        else if(Framework.includes("python")){
            obj = GUIConf.spxobj;
        }
        if(!obj.hasOwnProperty(CoordinateLabel)){
            return Promise.reject(new Error("The file format is invalid."));
        }
        GUIConf.spxobj = obj[CoordinateLabel];
        let steps = GUIConf.spxobj[StepCoordLabel].length;
        ImportSPXOutLabel.spxstep[3] = -(steps.toString()-1);
        outobj[ImportSPXOutLabel.bmletsout[0]] = GUIConf.spxobj[BeamletsLabel];
        outobj[ImportSPXOutLabel.paticlesout[0]] = GUIConf.spxobj[ParticlesLabel];
        outobj[ImportSPXOutLabel.spxstepzarr[0]] = GUIConf.spxobj[StepCoordLabel];
        outobj[ImportSPXOutLabel.spxenergy[0]] = GUIConf.spxobj[CentralEnergyLabel];
    }
    catch (e){
        return Promise.reject(new Error(e.message));
    }
    return Promise.resolve();
}

function GetKValue(uprm)
{
    let K, phi = 0;
    if(uprm[UndPrmsLabel.utype[0]] == LinearUndLabel){
        K = uprm[UndPrmsLabel.K[0]];
    }
    else if(uprm[UndPrmsLabel.utype[0]] == HelicalUndLabel){
        K = uprm[UndPrmsLabel.Kperp[0]];
        phi = 45;
    }
    else{
        K = uprm[UndPrmsLabel.Kperp[0]];
        phi = uprm[UndPrmsLabel.epukratio[0]];
    }
    return {K:K, phi:phi};
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

//  errf(x) = 2/sqrt(pi) int_0^x exp(-t^2)dt
function errf(x)
{
    let t, z, ans, ret, arg;

    z = Math.abs(x);
    t = 1.0/(1.0+0.5*z);
    arg = -z*z-1.26551223+t*(1.00002368+t*(0.37409196+t*(0.09678418+
          t*(-0.18628806+t*(0.27886807+t*(-1.13520398+t*(1.48851587+
          t*(-0.82215223+t*0.17087277))))))));
    if(arg < -MAXIMUM_EXPONENT){
        ans = 0.0;
    }
    else{
        ans = t*Math.exp(arg);
    }
    ret = x >= 0.0 ? ans : 2.0-ans;
    return 1.0-ret;
}

function scaling_fel3d_eta(lambda, L1D, beta, emitt, lambda_u, espread)
{
    let eta, Lr, d, e, g;
    let a = [0.0, 0.45, 0.57, 0.55, 1.6, 3.0, 2.0, 0.35, 2.9, 2.4, 51.0,
        0.95, 3.0, 5.4, 0.7, 1.9, 1140.0, 2.2, 2.9, 3.2];

    Lr = 4.0*Math.PI*beta*emitt/lambda;
    d = L1D/Lr;
    e = L1D/beta*(4.0*Math.PI*emitt/lambda);
    g = 4.0*Math.PI*L1D/lambda_u*espread;

    eta = a[1]*Math.pow(d, a[2])+a[3]*Math.pow(e, a[4])+a[5]*Math.pow(g, a[6])
        + a[7]*Math.pow(e, a[8])*Math.pow(g, a[9])+a[10]*Math.pow(d, a[11])*Math.pow(g, a[12])
        +a[13]*Math.pow(d, a[14])*Math.pow(e, a[15])+a[16]*Math.pow(d, a[17])*Math.pow(e, a[18])*Math.pow(g, a[19]);
    return eta;
}

function rho_fel_param_1D(ipeak, lambda_u_m, K, phi, betaav, emittav, gamma)
{
    let ir, kr, gr, rho, Ajj, Bjj, Q;
	phi *= DEGREE2RADIAN;

    Q = K*K*Math.cos(2.0*phi)/(4.0+2.0*K*K);
    Ajj = BesselJ0(Q)-BesselJ1(Q);
    Bjj = BesselJ0(Q)+BesselJ1(Q);
	Ajj = Math.hypot(Ajj*Math.cos(phi), Bjj*Math.sin(phi));

    ir = ipeak/ALFVEN_CURR;
    kr = lambda_u_m*K*Ajj/Math.PI/2;
    kr *= kr/2.0/(betaav*emittav);
    gr = 0.5/gamma;
    gr *= gr*gr;
    rho = ir*kr*gr;
    return Math.pow(rho, 1.0/3.0);
}

function fel_parameters(IA, emittav, betaav, EGeV, espread, lu, K, phi)
{
    let gamma = EGeV*1e3/MC2MeV;
    let e1st = COEF_E1ST*EGeV**2/lu/(1+K**2/2);
    let l1st = ONE_ANGSTROM_eV/e1st*1e-10;
    let rho, Lg1d, eta;
    if(betaav <= 0){
        rho = Lg1d = eta = null;
    }
    else{
        rho = rho_fel_param_1D(IA, lu, K, phi, betaav, emittav, gamma);
        Lg1d = lu/Math.PI/4.0/Math.sqrt(3.0)/rho;
        eta = scaling_fel3d_eta(l1st, Lg1d, betaav, emittav, lu, espread);    
    }
    return {e1st:e1st, l1st:l1st, rho:rho, Lg1d:Lg1d, eta:eta, npsat:rho/(1+eta)**2};
}

function optimize_beta(IA, emittav, EGeV, espread, lu, K, phi)
{
    let incrf = Math.sqrt(2);
    let betaorg = 10;
    let betaavr = [];
    let psatr = [];

    let betatest = betaorg;
    betaavr.push(betatest);
    psatr.push(fel_parameters(IA, emittav, betatest, EGeV, espread, lu, K, phi).npsat);

    do {
        betatest *= incrf;
        betaavr.push(betatest);
        psatr.push(fel_parameters(IA, emittav, betatest, EGeV, espread, lu, K, phi).npsat);    
    } while(psatr[psatr.length-1] >= psatr[psatr.length-2]);

    let center;
    if(psatr.length >= 3){
        center = psatr.length-2;
    }
    else{
        betatest = betaorg;
        do {
            betatest /= incrf;
            betaavr.unshift(betatest);
            psatr.unshift(fel_parameters(IA, emittav, betatest, EGeV, espread, lu, K, phi).npsat);    
        } while(psatr[0] >= psatr[1]);    
        center = 1;
    }
    return ParabolicPeak(betaavr[center-1], betaavr[center], betaavr[center+1], 
            psatr[center-1], psatr[center], psatr[center+1]).x;
}

function Lagrange(t, t0, t1, t2, e0, e1, e2)
{
    let ft;
    ft = e0*(t-t1)*(t-t2)/(t0-t1)/(t0-t2)
         +e1*(t-t0)*(t-t2)/(t1-t0)/(t1-t2)
         +e2*(t-t0)*(t-t1)/(t2-t0)/(t2-t1);
    return ft;
}

function LinearInterp(t, t0, t1, e0, e1)
{
    return e0+(e1-e0)/(t1-t0)*(t-t0);
}

function ParabolicPeak(x0, x1, x2, f0, f1, f2)
{
	let a, b, peak, xpeak;
	a = f0/(x0-x1)/(x0-x2)+f1/(x1-x0)/(x1-x2)+f2/(x2-x1)/(x2-x0);
	b = -(x1+x2)*f0/(x0-x1)/(x0-x2)-(x0+x2)*f1/(x1-x0)/(x1-x2)-(x1+x0)*f2/(x2-x1)/(x2-x0);
	if(a == 0){
		xpeak = x1;
		peak = f1;
	}
	else{
		xpeak = -b/2.0/a;
		peak = Lagrange(xpeak, x0, x1, x2, f0, f1, f2);
	}
	return {x:xpeak, y:peak};
}

function SearchIndex(nsize, isreg, xarr, x)
{
	let km, kp, k, n = nsize;
	if(isreg){
		let dx = (xarr[nsize-1]-xarr[0])/(nsize-1);
		km = (int)((x-xarr[0])/dx);
		if(km >= n-1){
			km = n-2;
		}
		if(km < 0){
			km = 0;
		}
		kp = km+1;
	}
	else{
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
	}
	return xarr[0] < xarr[1] ? km : kp;
}

function FEL_specs(IA, nemitt, EGeV, espread, lu, K, phi, ebmspecs, betaval = null)
{
    if(IA == null || nemitt == null || EGeV == null || espread == null){
        return null;
    }
    if(IA <= 0 || nemitt[0] <= 0 || nemitt[1] <= 0 || EGeV <= 0){
        return null;
    }

    let gamma = EGeV*1e3/MC2MeV;
    let emitt = [0, 0];
    for(let j = 0; j < 2; j++){
        emitt[j] = nemitt[j]*1e-6/gamma;
    }
    let emittav = Math.sqrt(emitt[0]*emitt[1]);

    let betaav = optimize_beta(IA, emittav, EGeV, espread, lu, K, phi);
    ebmspecs[2] = betaav;
    for(let j = 0; j < 2; j++){
        ebmspecs[j] = Math.sqrt(emitt[j]*betaav);
    }

    if(betaval == null){
        betaval = betaav;
    }
    let {e1st, l1st, rho, Lg1d, eta, npsat} = 
        fel_parameters(IA, emittav, betaval, EGeV, espread, lu, K, phi);
    let Lg3d, pshot, psatGW, Lsat, bandwidth;
    if(betaval <= 0){
        Lg3d = pshot = psatGW = Lsat = bandwidth = null;
    }
    else{
        Lg3d = Lg1d*(1.0+eta);
        let bmpowGW = EGeV*IA;
        psatGW = 1.6*npsat*bmpowGW;
        pshot = rho*rho*CC*EGeV*1.0e+9/l1st*QE;
    
        let gain = psatGW*1.0e+9*9.0/pshot;
        Lsat = Lg3d*Math.log(gain);
        gain = 10.0*Math.log10(gain);
        bandwidth = gain > 0.0 ? 2.0*rho*10.4/Math.sqrt(gain+9.5) : 1.0;    
    }

    return {
        [FELPrmsLabel.shotnoize[0]] : pshot,
        [FELPrmsLabel.rho[0]] : rho,
        [FELPrmsLabel.Lg[0]] : [Lg1d,Lg3d],
        [FELPrmsLabel.psat[0]] : psatGW,
        [FELPrmsLabel.Lsat[0]] : Lsat,
        [FELPrmsLabel.e1st[0]] : e1st,
        [FELPrmsLabel.l1st[0]] : l1st*1e9, // m -> nm
        [FELPrmsLabel.bandwidth[0]] : bandwidth
    };
}

function GetStats(x, y)
{
    let ndata = x.length;
    let chn = new Array(ndata);
    let area = 0, avgx = 0;
    chn.fill(0);
    for(let n = 1; n < ndata; n++){
        chn[n] = (y[n]+y[n-1])*(x[n]-x[n-1])/2;
        area += chn[n];
        avgx += (x[n]+x[n-1])/2*chn[n];
    }
    avgx /= area;
    let rms = 0;
    for(let n = 1; n < ndata; n++){
        rms += ((x[n]+x[n-1])/2-avgx)**2*chn[n];
    }
    rms = Math.sqrt(rms/area);

    return {area: area, avpos: avgx, rms: rms};
}

function GetEBeamSpecSlice(sliceprms)
{
    let lu = GUIConf.input[UndLabel][UndPrmsLabel.lu[0]]*0.001;
    let {K, phi} = GetKValue(GUIConf.input[UndLabel]);
    let ndata = sliceprms[0].length;
    let idxs = SliceTitles.indexOf(SliceLabel);
    let idxI = SliceTitles.indexOf(CurrentLabel);
    let idxemitt = [SliceTitles.indexOf(EmittxLabel), SliceTitles.indexOf(EmittyLabel)];
    let idxE = SliceTitles.indexOf(EnergyLabel);
    let idxEsp = SliceTitles.indexOf(EspLabel);
    let idxbeta = [SliceTitles.indexOf(BetaxLabel), SliceTitles.indexOf(BetayLabel)];
    let idxalpha = [SliceTitles.indexOf(AlphaxLabel), SliceTitles.indexOf(AlphayLabel)];
    let ebmspecs = new Array(3);

    let felprms, emitt, pkpow = 0, npeak = 0;
    let betaavg = [0, 0];
    let alphaavg = [0, 0];
    for(let n = 0; n < ndata; n++){
        if(sliceprms[idxI][n] <= 0 || sliceprms[idxemitt[0]][n] <= 0 || sliceprms[idxemitt[1]][n] <= 0){
            continue;
        }
        if(n > 0){
            let chn = (sliceprms[idxI][n]+sliceprms[idxI][n-1])*(sliceprms[idxs][n]-sliceprms[idxs][n-1])/2;
            for(let j = 0; j < 2; j++){
                betaavg[j] += (sliceprms[idxbeta[j]][n]+sliceprms[idxbeta[j]][n-1])/2*chn;
                alphaavg[j] += (sliceprms[idxalpha[j]][n]+sliceprms[idxalpha[j]][n-1])/2*chn;
            }
        }
        felprms = FEL_specs(
                    sliceprms[idxI][n], [sliceprms[idxemitt[0]][n], sliceprms[idxemitt[1]][n]], 
                    sliceprms[idxE][n], sliceprms[idxEsp][n], lu, K, phi, ebmspecs);
        if(felprms != null && felprms[FELPrmsLabel.psat[0]] > pkpow){
            pkpow = felprms[FELPrmsLabel.psat[0]];
            npeak = n;
        }
    }
    let stats = GetStats(sliceprms[idxs], sliceprms[idxI]);
    let charge = stats.area;
    let bunchlen = stats.rms;
    for(let j = 0; j < 2; j++){
        betaavg[j] /= charge;
        alphaavg[j] /= charge;
    }

    charge *= 1e+9/CC; // C -> nC
    emitt = [sliceprms[idxemitt[0]][npeak], sliceprms[idxemitt[1]][npeak]];

    let betabunch = betaavg;
    let alphabunch = alphaavg 
    let speak = 0;
    if(GUIConf.input[EBLabel][EBeamPrmsLabel.twissbunch[0]] == SlicedPrmCustom){
        speak = GUIConf.input[EBLabel][EBeamPrmsLabel.twisspos[0]];
        let ns = Math.min(ndata-2, SearchIndex(sliceprms[idxs].length, false, sliceprms[idxs], speak));
        let ds = (speak-sliceprms[idxs][ns])/(sliceprms[idxs][ns+1]-sliceprms[idxs][ns]);
        for(let j = 0; j < 2; j++){
            betabunch[j] = sliceprms[idxbeta[j]][ns]*(1-ds)+sliceprms[idxbeta[j]][ns+1]*ds;
            alphabunch[j] = sliceprms[idxalpha[j]][ns]*(1-ds)+sliceprms[idxalpha[j]][ns+1]*ds;
        }    
    }
    else if(GUIConf.input[EBLabel][EBeamPrmsLabel.twissbunch[0]] == SlicedPrmOptimize){
        speak = sliceprms[idxs][npeak];
        for(let j = 0; j < 2; j++){
            betabunch[j] = sliceprms[idxbeta[j]][npeak];
            alphabunch[j] = sliceprms[idxalpha[j]][npeak];
        }    
    }
    SetChargeProfile(sliceprms[idxs], sliceprms[idxI]);

    let specs = BundleEBeamSpecs(sliceprms[idxE][npeak], charge, bunchlen, sliceprms[idxI][npeak], sliceprms[idxEsp][npeak], emitt, speak, betabunch, alphabunch);
    GUIConf.input[EBLabel][EBeamPrmsLabel.bunchbeta[0]] = betabunch;
    GUIConf.input[EBLabel][EBeamPrmsLabel.bunchalpha[0]] = alphabunch;
    GUIConf.input[EBLabel][EBeamPrmsLabel.twisspos[0]] = speak;
    if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == CustomParticle){
        specs[CurrentProfLabel] = GUIConf.qprofile;
    }
    return specs;
}

function BundleEBeamSpecs(energy = null, charge = null, bunchlen = null, peakcurr = null, esp = null, emitt = null, spos = null, beta = null, alpha = null)
{
    return {
        [EBeamPrmsLabel.eenergy[0]]: energy,
        [EBeamPrmsLabel.bunchcharge[0]]: charge,
        [EBeamPrmsLabel.bunchleng[0]]: bunchlen,
        [EBeamPrmsLabel.pkcurr[0]]: peakcurr,
        [EBeamPrmsLabel.espread[0]]: esp,
        [EBeamPrmsLabel.emitt[0]]: emitt,
        [EBeamPrmsLabel.twisspos[0]]: spos,
        [EBeamPrmsLabel.bunchbeta[0]]: beta,
        [EBeamPrmsLabel.bunchalpha[0]]: alpha,
    };   
}

function GetCharge(rangec)
{
    let range = [Math.min(rangec[0], rangec[1]), Math.max(rangec[0], rangec[1])];
    let ebeam = GUIConf.input[EBLabel];
    let pkcurr = GUIConf.input[EBLabel][EBeamPrmsLabel.pkcurr[0]];
    if(ebeam[EBeamPrmsLabel.bmprofile[0]] == GaussianBunch){
        let sigmas = GUIConf.input[EBLabel][EBeamPrmsLabel.bunchleng[0]];        
		return Math.sqrt(Math.PI/2)*sigmas/CC*pkcurr*(errf(range[1]/Math.SQRT2/sigmas)-errf(range[0]/Math.SQRT2/sigmas));
    }
    else if(ebeam[EBeamPrmsLabel.bmprofile[0]] == BoxcarBunch){
        range[0] = Math.max(range[0], -ebeam[EBeamPrmsLabel.bunchlenr[0]]/2);
        range[1] = Math.min(range[1], ebeam[EBeamPrmsLabel.bunchlenr[0]]/2);
        return (range[1]-range[0])/CC*pkcurr;
    }
    else{
        if(!GUIConf.hasOwnProperty("qprofile")){
            return null;
        }
        let charge = [0, 0];
        for(let j = 0; j < 2; j++){
            let index = SearchIndex(GUIConf.qprofile[0].length, false, GUIConf.qprofile[0], range[j]);
            charge[j] = LinearInterp(range[j], 
                    GUIConf.qprofile[0][index], GUIConf.qprofile[0][index+1], 
                    GUIConf.qprofile[1][index], GUIConf.qprofile[1][index+1]);
        }
        return charge[1]-charge[0];
    }
}
