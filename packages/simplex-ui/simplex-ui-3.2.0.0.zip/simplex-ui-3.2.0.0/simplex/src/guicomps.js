"use strict";

// Abstract class to handle parameters and configurations
class PrmOptionList {
    constructor(categ, labels, tbllist = {}, gridconf = {}, indents = [], columns = [], scans = []){
        this.m_table = document.createElement("div");
        this.m_table.className = "d-flex flex-column align-items-stretch w-100";
        this.m_labels = labels;
        this.m_categ = categ;
        this.m_grids = {};
        this.m_jsonobj =  {};
        this.m_tbllist = tbllist;
        this.m_gridconfs = gridconf;
        this.m_indents = indents;
        this.m_columns = columns;
        this.m_precs = [6, 4];
        this.m_scans = scans;
        this.m_parentobj = null;
        this.m_fixedrows = {};

        this.m_objlabels = [PlotObjLabel, FileLabel, FolderLabel, GridLabel];
        this.SetDefault();

        this.m_types = {};
        for(let n = 0; n < this.m_labels.length; n++){
            if(this.m_labels[n] == SeparatorLabel){
                continue;
            }
            this.m_types[this.m_labels[n][0]] = this.GetPrmType(n);
        }
    };

    get JSONObj(){
        return this.m_jsonobj;
    };

    set JSONObj(jsonobj){
        this.m_jsonobj = jsonobj;
        this.SetDefault();
    };

    GetFormat(label){
        if(!this.m_types.hasOwnProperty(label)){
            return null;
        }
        return this.m_types[label];
    }

    GetSelectable(label){
        let id = GetIDFromItem(this.m_categ, label, -1);
        let el = document.getElementById(id);
        if(el == undefined){
            return;
        }
        let options = [];
        for(let i = 0; i < el.options.length; i++){
            options.push(el.options[i].value);
        }
        return options;
    }

    GetReferenceList(simplified, noinputs, skiptitle = false, subtitle = "")
    {
        let tbl = document.createElement("table");

        /*
        let caption = document.createElement("caption");
        caption.innerHTML = "Parameters in \""+this.m_categ+"."+OptionLabel+"\" object.";
        tbl.caption = caption;
        */

        let rows = [];
        let cell;

        if(!skiptitle){
            ArrangeObjectTblTitle(tbl, rows);
        }
        if(subtitle != ""){
            rows.push(tbl.insertRow(-1)); 
            cell = rows[rows.length-1].insertCell(-1);
            cell.innerHTML = subtitle;
            cell.className += " subtitle";
            cell.setAttribute("colspan", "5");
        }                

        for(let i = 0; i < this.m_labels.length; i++){
            if(this.m_labels[i] == SeparatorLabel){
                continue;
            }
            let tgtlabel = this.m_labels[i][0];
            if(noinputs.includes(tgtlabel)){
                continue;
            }

            rows.push(tbl.insertRow(-1)); 

            cell = rows[rows.length-1].insertCell(-1);
            cell.innerHTML = tgtlabel;

            cell = rows[rows.length-1].insertCell(-1);           
            let label = tgtlabel
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;").replace(/>/g, "&gt;");
            cell.innerHTML = label;
            cell.className += " prm";

            cell = rows[rows.length-1].insertCell(-1);
            cell.innerHTML = simplified[i];
            cell.className += " prm";

            let type = this.m_types[tgtlabel];
            let fmt;
            if(IsArrayParameter(type) || type == GridLabel){
                fmt = "array";
            }
            else if(type == "boolean"){
                fmt = "boolean";
            }
            else if(type == SelectionLabel){
                let selections = this.m_labels[i][1];
                if(Array.isArray(selections) && selections.length > 0){
                    if(typeof selections[0] == "object"){
                        selections = [];
                        for(const selgrp of this.m_labels[i][1]){
                            let key = Object.keys(selgrp)[0];
                            selections = selections.concat(selgrp[key]);
                        }
                    }
                    for(let n = 0; n < selections.length; n++){
                        selections[n] = "\""+selections[n]+"\""
                    }
                    fmt = "Select from:<br>"+selections.join("<br>");
                }
                else{
                    Alert("Invalid format in "+this.m_labels[i][0]);
                }
            }
            else if(type == FileLabel){
                fmt = "file name";
            }
            else if(type == FolderLabel){
                fmt = "directory name";
            }
            else if(type == "string"){
                fmt = "string";
            }
            else if(type == IntegerLabel || type == IncrementalLabel){
                fmt = "integer";
            }
            else if(type == NumberLabel){
                fmt = "number";
            }
            else if(type == PlotObjLabel){
                fmt = "object";
            }

            cell = rows[rows.length-1].insertCell(-1);
            cell.innerHTML = fmt;          

            let val = this.m_jsonobj[tgtlabel];
            if(Array.isArray(val)){
                val = "["+val.join(", ")+"]";
            }
            else if(val == undefined || typeof(val) == "object"){
                val = "";
            }
            cell = rows[rows.length-1].insertCell(-1);
            cell.innerHTML = val;
        }
        let retstr = tbl.outerHTML;   
        return retstr;
    }

    SetPrecision(precs)
    {
        this.m_precs = precs;
    }

    GetLabels(){
        return this.m_labels;
    }

    GetTable(){
        return this.m_table;
    };

    DisableInput(prmlabel, isdisable, forcevalue = null)
    {
        let type = this.m_types[prmlabel];
        let jxy = [-1];
        if(IsArrayParameter(type)){
            jxy = [0, 1];
        }
        jxy.forEach(j => {
            let inputid = GetIDFromItem(this.m_categ, prmlabel, j);
            let el = document.getElementById(inputid);
            if(el == null){
                return;
            }
            if(isdisable){
                el.setAttribute("disabled", true);
            }  
            else{
                el.removeAttribute("disabled");                        
            }
            if(forcevalue != null){
                if(typeof forcevalue == "boolean"){
                    el.checked = forcevalue;
                }
                else{
                    el.checked = forcevalue;
                }
            }
        });
    }

    DisableOptions(disable)
    {
        for(let i = 0; i < this.m_labels.length; i++){
            if(this.m_labels[i] == SeparatorLabel){
                continue;
            }
            if(this.m_validlist[this.m_labels[i][0]] == false){
                continue;
            }
            if(this.m_labels[i][1] == GridLabel){
                this.m_grids[this.m_labels[i][0]].DisableGrid(disable);
            }
            else if(this.m_labels[i][1] == FileLabel 
                || this.m_labels[i][1] == FolderLabel){
                let btnid = this.m_labels[i][0]+SuffixButton;
                this.DisableInput(btnid, disable);
                this.DisableInput(this.m_labels[i][0], disable);
            }
            else{
                this.DisableInput(this.m_labels[i][0], disable)
            }
        }
    }

    DisableSelection(label, item, isdisable)
    {
        let id = GetIDFromItem(this.m_categ, label, -1);
        let el = document.getElementById(id);
        if(el == undefined){
            return;
        }
        let children = el.options;
        let reset = false;
        for(let i = 0; i < children.length; i++){
            if(children[i].value == item){
                if(isdisable){
                    children[i].setAttribute("disabled", true);
                    if(children[i].selected){
                        children[i].selected = false;
                        reset = true;
                    }
                }
                else{
                    children[i].removeAttribute("disabled");
                }
                break;
            }
        }

        if(reset){
            let e = new Event("change")
            el.dispatchEvent(e);    
        }
    }

    ReplaceSelection(label, selections)
    {
        for(let i = 0; i < this.m_labels.length; i++){
            if(label == this.m_labels[i][0]){
                this.m_labels[i][1] = Array.from(selections);
            }
        }
    }

    IsShown(label)
    {
        return this.m_validlist[label];
    }

    GetValidList(type = 1)
    {
        let validlist = {};
        this.m_labels.forEach((el) => {
            if(el != SeparatorLabel){
                validlist[el[0]] = type;
            }
        });
        return validlist;
    }

    GetShowList()
    {
        return this.GetValidList();
    }

    GetPrmType(i)
    {
        let type;
        if(this.m_objlabels.includes(this.m_labels[i][1])){
            type = this.m_labels[i][1];
        }
        else{
            if(this.m_labels[i][1] == null){
                return NumberLabel;
            }
            type = typeof this.m_labels[i][1];
            if(type == "object" || type == "number"){
                // array: vector or selection
                // number: integer or float
                if(this.m_labels[i].length > 2){
                    type = this.m_labels[i][2];
                }
                else{
                    type = type == "number" ? NumberLabel : ArrayLabel;
                }
            }
            else if(this.m_labels[i].length > 2){
                type = this.m_labels[i][2];
            }
        }
        return type;
    }

    SetDefault()
    {
        for(let i = 0; i < this.m_labels.length; i++){
            if(this.m_labels[i] == SeparatorLabel || this.m_labels[i][1] == SimpleLabel){
                continue;
            }
            if(this.m_jsonobj.hasOwnProperty(this.m_labels[i][0])){
                continue;
            }
            let type = this.GetPrmType(i);
            if(type == PlotObjLabel){
                this.m_jsonobj[this.m_labels[i][0]] = {};
            }
            else if(type == FileLabel || type == FolderLabel){
                this.m_jsonobj[this.m_labels[i][0]] = "";
            }
            else if(type == GridLabel){
                this.m_jsonobj[this.m_labels[i][0]] = [];
            }
            else if(this.m_labels[i].length > 2 && this.m_labels[i][2] == SelectionLabel){
                if(typeof this.m_labels[i][1][0] == "object"){
                    let key = Object.keys(this.m_labels[i][1][0])[0];
                    this.m_jsonobj[this.m_labels[i][0]] = this.m_labels[i][1][0][key][0];
                }
                else{
                    this.m_jsonobj[this.m_labels[i][0]] = this.m_labels[i][1][0];
                }
            }
            else{
                this.m_jsonobj[this.m_labels[i][0]] = this.m_labels[i][1];
            }
        }
    }

    RefreshItem(label){
        if(Array.isArray(label)){
            if(IsArrayParameter(this.m_types[label[0]]) && this.m_validlist[label[0]] >= 1){
                let items = [this.GetItem(label[0], 0), this.GetItem(label[0], 1)];
                this.UpdateItem(items, label[0], label[1]);
            }
            else{
                this.UpdateItem(this.GetItem(label[0]), label[0], label[1]);
            }
        }
        else{
            if(IsArrayParameter(this.m_types[label]) && this.m_validlist[label] >= 1){
                let items = [this.GetItem(label, 0), this.GetItem(label, 1)];
                this.UpdateItem(items, label);
            }
            else{
                this.UpdateItem(this.GetItem(label), label);
            }
        }
    }

    FreezePanel()
    {
        let elements = document.querySelectorAll(`[id^="${this.m_categ}"]`);
        elements.forEach(element => {
            element.setAttribute("disabled", true);
        });
    }

    SetPanelBase(validlist, disabled = [])
    {
        this.m_validlist = validlist;
        this.m_table.innerHTML = "";
        this.m_fdialog = {};
        this.m_fdlist = {};
        this.m_skipupdate = false;
        let isitem = false;
        this.m_incrlabels = [];
        this.m_runbuttons = {};

        for(let i = 0; i < this.m_labels.length; i++){
            if(this.m_labels[i] == SeparatorLabel){
                if(isitem){
                    let isshow = false;
                    for(let j = i+1; j < this.m_labels.length; j++){
                        if(this.m_labels[j] == SeparatorLabel){
                            continue;
                        }
                        if(this.m_validlist[this.m_labels[j][0]] >= 0){
                            isshow = true;
                            break;
                        }
                    }
                    if(isshow){
                        let cell = document.createElement("hr");
                        cell.className = "mt-1 mb-1";
                        this.m_table.appendChild(cell);
                        isitem = false;
                    }
                }
                continue;
            }
            if(this.m_validlist[this.m_labels[i][0]] < 0){
                continue;
            }

            if(this.m_labels[i][1] == SimpleLabel){
                let label = document.createElement("div");
                label.className = "fw-bold";
                label.innerHTML = this.m_labels[i][0];
                this.m_table.appendChild(label);
                continue;
            }

            let type = this.GetPrmType(i);
            if(type == ArrayIncrementalLabel || type == IncrementalLabel){
                this.m_incrlabels.push(this.m_labels[i][0]);
            }
            let changable = !this.m_objlabels.includes(this.m_labels[i][1]);

            let val = this.m_jsonobj[this.m_labels[i][0]];
            isitem = true;
            let cell = document.createElement("div");
            cell.className = "d-flex justify-content-between";
            if(this.m_columns.includes(this.m_labels[i][0])){
                cell.className = "d-flex flex-column align-items-stretch";
            }
            if(this.m_indents.includes(this.m_labels[i][0])){
                cell.classList.add("ms-2");
            }
            this.m_table.appendChild(cell);

            let inputid = 
                GetIDFromItem(this.m_categ, this.m_labels[i][0], -1);

            if(changable && type != "boolean"){
                let celltitle = document.createElement("div");
                celltitle.innerHTML = this.m_labels[i][0];
                celltitle.className = "me-1";
                cell.appendChild(celltitle);
            }
    
            let item = null, body = null;
            if((type == IntegerLabel || type == NumberLabel || type == ArrayLabel) 
                    && this.m_validlist[this.m_labels[i][0]] == 0){
                body = item = document.createElement("div");
            }
            else if(type == "boolean"){
                let chk = CreateCheckBox(this.m_labels[i][0], val, inputid);
                item = chk.chkbox;
                body = chk.div;
                body.classList.add("ms-1");
            }
            else if(IsArrayParameter(type)){
                item = this.SetArrayNumber(this.m_labels[i], cell, type);
            }
            else if(type == SelectionLabel){
                body = item = document.createElement("select");
                SetSelectMenus(item, this.m_labels[i][1], [], val);
            }
            else if(type == GridLabel){
                cell.className = "d-flex flex-column align-items-stretch";
                body = item = document.createElement("div");
                item.className = "prmgrid d-flex flex-column align-items-stretch";
                let fixedrows = -1;
                if(this.m_fixedrows.hasOwnProperty(this.m_labels[i][0])){
                    fixedrows = this.m_fixedrows[this.m_labels[i][0]];
                }
                this.SetGrid(this.m_labels[i][0], null, item, fixedrows);
                if(this.m_labels[i].length > 2){
                    let cellheader = document.createElement("div");
                    cellheader.className = "d-flex align-items-end justify-content-between";
                    let celltitle = document.createElement("div");
                    celltitle.innerHTML = this.m_labels[i][0];
                    cellheader.appendChild(celltitle);
                    let runbtn = document.createElement("button");
                    runbtn.className = "btn btn-primary btn-sm";
                    runbtn.innerHTML = this.m_labels[i][2];
                    cellheader.appendChild(celltitle);    
                    cellheader.appendChild(runbtn);    
                    cell.appendChild(cellheader);
                    this.m_runbuttons[this.m_labels[i][2]] = runbtn;
                }
                else{
                    let celltitle = document.createElement("div");
                    celltitle.innerHTML = this.m_labels[i][0];
                    cell.appendChild(celltitle);
                }
            }
            else if(type == FileLabel || type == FolderLabel){
                cell.className = "d-flex flex-column";
                let titdiv = document.createElement("div");
                titdiv.className = "d-flex justify-content-between align-items-end";
                let labdiv = document.createElement("div");
                labdiv.innerHTML = this.m_labels[i][0];
                let btn = document.createElement("button");
                titdiv.appendChild(labdiv);
                titdiv.appendChild(btn);
                cell.appendChild(titdiv);

                btn.innerHTML = "Browse";
                btn.className = "btn btn-outline-primary btn-sm"
                btn.addEventListener("click",
                    async (e) => {
                        if(Framework == PythonGUILabel){
                            let command = [type, inputid];
                            PyQue.Put(command);        
                        }
                        if(Framework == BrowserLabel || Framework == ServerLabel){
                            Alert("This command is not available under the current environment.");
                        }
                        if(Framework != TauriLabel){
                            return;
                        }
                        let isfile = this.m_labels[i][1] == FileLabel;
                        let title = "Select a directory to save the output file."
                        if(isfile){
                            title = "Select a data file."
                        }
                        let path = await GetPathDialog(title, inputid, true, isfile, false, false);
                        if(path == null){
                            return;
                        }
                        this.m_jsonobj[this.m_labels[i][0]] = path;
                        this.UpdateItem(document.getElementById(inputid), this.m_labels[i][0]);
                        UpdateOptions(inputid);
                    });

                if(Framework == PythonScriptLabel){
                    btn.className = "d-none";
                }
                body = item = document.createElement("textarea");
                item.setAttribute("rows", "1");
            }
            else if(type == PlotObjLabel){
                cell.className = "d-flex justify-content-end";
                body = item = document.createElement("button");
                item.className = "btn btn-outline-primary btn-sm"
                item.innerHTML = "Import/View Data";
                item.addEventListener("click", (e)=>
                {
                    ShowDataImport(e.currentTarget.id);
                    let items = GetItemFromID(e.currentTarget.id)
                    if(this.m_jsonobj.hasOwnProperty(items.item)){
                        if(CheckDataObj(this.m_jsonobj[items.item])){
                            return;
                        }
                    }
                });
            }
            else if(type == "string"){
                body = item = document.createElement("textarea");
                item.setAttribute("rows", "1");
                item.className = "comment";
            }
            else if(type == IntegerLabel || type == IncrementalLabel){
                body = item = document.createElement("input");
                item.setAttribute("type", "number");
                this.SetMinMax(item, this.m_labels[i]);
            }
            else if(type == ColorLabel){
                body = item = document.createElement("input");
                item.setAttribute("type", "color");                
            }
            else{ // number
                body = item = document.createElement("input");
                item.setAttribute("type", "text");
            }
            if(!Array.isArray(item)){
                item.id = inputid;
                if(this.m_validlist[this.m_labels[i][0]] > 0){
                    item.addEventListener("change", (e) => {this.Change(e);} );
                }    
            }
            if(body != null){
                cell.appendChild(body);
            }
            this.UpdateItem(item, this.m_labels[i][0]);
        }

        disabled.forEach(item => {
            this.DisableInput(item, true);
        });
    }

    SetMinMax(item, label)
    {
        let confs = label.length;
        if(confs > 3){
            if(label[3] != null){
                item.setAttribute("min", 
                    label[3].toString());
            }
            if(confs > 4){
                if(label[4] != null){
                    item.setAttribute("step", 
                        label[4].toString());
                }    
            }
            if(confs > 5){
                if(label[5] != null){
                    item.setAttribute("max", 
                        label[5].toString());
                }    
            }
        }
        else{
            if(label[1] == 0){
                item.setAttribute("min", "0");
            }
            else if(label[1] > 0){
                item.setAttribute("min", "1");
            }
            else{
                item.setAttribute("min", "-1");
            }    
        }
    }

    GetItem(label, j = -1)
    {
        if(this.m_validlist.hasOwnProperty(label) == false){
            return null;
        }
        let inputid = GetIDFromItem(this.m_categ, label, j);
        let item = document.getElementById(inputid);
        return item;
    }

    UpdateItem(item, label, option = null)
    {
        if(item == null){
            return;
        }
        let type = this.m_types[label];
        let val = this.m_jsonobj[label];
        let scanitems = [];
        if((type == IntegerLabel || type == NumberLabel || type == ArrayLabel || type == ArrayIntegerLabel) 
                && this.m_validlist[label] == 0){
            if(type == NumberLabel){
                item.innerHTML = ToPrmString(val, this.m_precs[0]);
            }
            else if(type == IntegerLabel){
                item.innerHTML = Math.floor(0.5+val).toString();
            }
            else{
                if(val == null){
                    item.innerHTML = "-"+this.GetDelimiter(label)+"-";
                }
                else{
                    item.innerHTML = ToPrmString(val[0], this.m_precs[1])+this.GetDelimiter(label)+ToPrmString(val[1], this.m_precs[1]);
                }
            }
        }
        else if(IsArrayParameter(type)){
            for(let j = 0; j < 2; j++){
                let valstr;
                try {
                    if(type == ArrayLabel){
                        valstr = ToPrmString(val[j], this.m_precs[1]);
                    }
                    else{
                        valstr = val[j].toString();
                    }
                } catch(e) {
                    valstr = "";
                }
                item[j].value = valstr;
                if(this.m_scans.includes(label)){
                    scanitems.push(item[j]);
                }
            }
        }
        else if(type == "boolean"){
            if(val == true){
                item.setAttribute("checked", "checked");
            }
            else{
                item.removeAttribute("checked");
            }
        }
        else if(type == SelectionLabel){
            SetSelectedItem(item, val);
        }
        else if(type == FileLabel || type == FolderLabel){
            item.value = GetShortPath(val, 10, 25);
        }
        else if(type == "string"){
            item.value = val;
        }
        else if(type == IntegerLabel || type == IncrementalLabel){
            item.value = val;
            if(this.m_scans.includes(label)){
                scanitems.push(item);
            }
        }
        else if(type == ColorLabel){
            item.value = val;
        }
        else if(type == NumberLabel){
            item.value = ToPrmString(val, this.m_precs[0]);
            if(option != null){
                item.style.color = option.color;
            }    
            if(this.m_scans.includes(label)){
                scanitems.push(item);
            }
        }
        for(let j = 0; j < scanitems.length; j++){
            scanitems[j].addEventListener("contextmenu", (e) => {
                if(this.m_parentobj == null){
                    e.category = this.m_categ;
                }
                else{
                    e.category = [this.m_parentobj.parent, this.m_parentobj.label];
                }
                e.item = label;
                e.jxy = scanitems.length == 1 ? -1 : j;
                e.isinteger = type == IntegerLabel || type == IncrementalLabel || type == ArrayIntegerLabel;
                OnRightClickData(e, "scan-prm");
            });
        }
    }

    SetGrid(label, gridconfs = null, item = null, fixedrows = -1){
        if(this.m_validlist[label] < 0){
            return;
        }
        if(gridconfs != null){
            this.m_gridconfs[label] = CopyJSON(gridconfs);
        }
        let inputid = GetIDFromItem(this.m_categ, label, -1);
        let grid = new Grid(inputid, this.m_gridconfs[label], null, fixedrows);
        this.m_grids[label] = grid;
        if(Array.isArray(this.m_jsonobj[label]) == false){
            this.m_jsonobj[label] = [];
        }
        grid.SetData(this.m_jsonobj[label]);
        grid.GetTable().addEventListener("gridchange", (e) => {
            this.Change(e);
        });
        if(item != null){
            item.appendChild(grid.GetTable());
        }
        else{
            document.getElementById(inputid).innerHTML = "";
            document.getElementById(inputid).appendChild(grid.GetTable());
        }
    }

    GetDelimiter(label){
        return label.includes(",") ? "," : "~";
    }

    SetArrayNumber(label, cell, type){
        let item = [];
        let cellvalue = document.createElement("div");
        cellvalue.className = "d-flex";
        for(let j = 0; j < 2; j++){
            if(j > 0){
                let spdiv = document.createElement("span");
                spdiv.innerHTML = this.GetDelimiter(label[0]);
                cellvalue.appendChild(spdiv);
            }
            let inputid = GetIDFromItem(this.m_categ, label[0], j);            
            let input = document.createElement("input");
            item.push(input);
            input.style = "width: 60px";
            input.setAttribute("type", type == ArrayLabel ? "text" : "number");
            input.id = inputid;
            input.addEventListener("change", (e) => {this.Change(e);} );
            cellvalue.appendChild(input);
            if(type != ArrayLabel){
                this.SetMinMax(input, label);
            }
        }
        cell.appendChild(cellvalue);
        return item;
    }

    Change(event){
        if(event.type == "gridchange"){
            let id = event.detail.id;
            if(!this.m_skipupdate){
                UpdateOptions(id);
            }
            return;
        }
        let tgt = event.currentTarget; 
        let idc = GetItemFromID(tgt.id);
        if(idc.categ != this.m_categ){
            return;
        }
        if(tgt.type == "text"){
            if(idc.jxy < 0){
                this.m_jsonobj[idc.item] = parseFloat(tgt.value);
            }
            else{
                this.m_jsonobj[idc.item][idc.jxy] = parseFloat(tgt.value);
            }
        }
        else if(tgt.type == "textarea" || tgt.type == "select-one" || tgt.type == "color"){
            this.m_jsonobj[idc.item] = tgt.value;
        }
        else if(tgt.type == "checkbox"){
            this.m_jsonobj[idc.item] = tgt.checked;
        }
        else if(tgt.type == "number"){
            let value;
            if(this.m_incrlabels.includes(idc.item)){
                value = parseFloat(tgt.value)
            }
            else{
                value = parseInt(tgt.value)
            }
            if(idc.jxy < 0){
                this.m_jsonobj[idc.item] = value;
            }
            else{
                this.m_jsonobj[idc.item][idc.jxy] = value;
            }
        }
        if(tgt.type == "checkbox" || tgt.type == "select-one"){
            this.SetPanel();
        }
        UpdateOptions(tgt.id);
    };

    ExportCurrent(){
        let obj = {};
        for(let i = 0; i < this.m_labels.length; i++){
            if(this.m_labels[i] == SeparatorLabel){
                continue;
            }
            if(this.m_validlist[this.m_labels[i][0]] <= 0){
                continue;
            }
            if(this.m_labels[i][1] == SimpleLabel){
                continue;
            }
            else{
                obj[this.m_labels[i][0]] = 
                    CopyJSON(this.m_jsonobj[this.m_labels[i][0]]);
            }
        }
        return obj;
    }

    Hidden(){
        let isshown = false;
        Object.keys(this.m_validlist).forEach((el) => {
            if(this.m_validlist[el] >= 0){
                isshown = true;
            }            
        });
        return isshown == false;
    }
}

// Grid Controls (spread sheed)
class Grid {
    constructor(id, gridconf, subtitles = null, fixedrows = -1){
        this.m_id = id;
        this.m_coltypes = gridconf.coltypes;
        this.m_table = document.createElement("table");
        this.m_table.className = "grid h-auto";
        this.m_withnum = gridconf.withnum;
        this.m_readonly = false;
        if(gridconf.hasOwnProperty("readonly")){
            this.m_readonly = gridconf.readonly;
        }
        this.m_subtitles = subtitles;
        this.m_sortlogic = null;
        if(gridconf.hasOwnProperty("sortlogic")){
            this.m_sortlogic = gridconf.sortlogic;
        }
        this.m_nrowfix = fixedrows;
        this.m_addrows = AdditionalRows;
        if(fixedrows >= 0){
            this.m_addrows = 0;
        }
    }

    DisableGrid(isdisable){
        let iini = this.m_subtitles == null ? 1 : 2;
        for(let i = iini; i < this.m_table.rows.length; i++){
            for(let j = 0; j < this.m_coltypes.length; j++){
                let id = GetIdFromCell(this.m_id, i-1, j);
                let el = document.getElementById(id);
                if(el == null){
                    continue;
                }            
                if(isdisable){
                    el.setAttribute("disabled", true);
                }
                else{
                    el.removeAttribute("disabled");
                }
            }
        }
    }

    Clear()
    {
        this.m_table.innerHTML = "";
    }

    ClearData()
    {
        let nrows = this.m_subtitles == null ? 1 : 2;
        while(this.m_table.rows.length > nrows){
            this.m_table.deleteRow(-1);
        }
    }

    SetSorting(cell, coltitle, j)
    {
        cell.innerHTML = "";
        let tddiv = document.createElement("div");
        tddiv.className = "d-flex justify-content-between";

        let tddtitle = document.createElement("div");
        tddtitle.innerHTML = coltitle;
        tddiv.appendChild(tddtitle);

        let databtn = document.createElement("div");
        databtn.innerHTML = "&#8691;";
        databtn.className = "btndiv";
        tddiv.appendChild(databtn);
        cell.appendChild(tddiv);

        databtn.addEventListener("click", (e) => {
            if(this.m_data.length < 2){
                return;
            }
            let ilogic = 1;
            if(this.m_sortlogic != null){
                if(this.m_sortlogic.hasOwnProperty(coltitle)){
                    ilogic = this.m_sortlogic[coltitle];
                }
                else{
                    this.m_sortlogic[coltitle] = 1;
                }
            }
            this.m_data.sort((a, b) => {return ilogic*(a[j] > b[j] ? 1 : -1)});
            this.ClearData();
            this.ApplyData();
            if(this.m_sortlogic != null){
                this.m_sortlogic[coltitle] *= -1;
            }
        });
    }

    SetData(data, grpcols = null, width = "100px", sortcols = null)
    {
        this.m_data = data;
        this.m_table.innerHTML = "";

        if(grpcols != null){
            let colgrp = document.createElement("colgroup");
            for(let j = 0; j < grpcols[0]; j++){
                colgrp.appendChild(document.createElement("col"));
            }
            let col = document.createElement("col");
            let cols = grpcols[1]-grpcols[0]+1
            col.setAttribute("span", cols.toString());
            col.style.width = width;
            colgrp.appendChild(col);
            for(let j = grpcols[1]+1; j < this.m_coltypes.length; j++){
                colgrp.appendChild(document.createElement("col"));
            }
            this.m_table.appendChild(colgrp);
        }

        this.m_titlerow = this.m_table.insertRow(-1);
        let cell;

        if(this.m_withnum >= 0){
            cell = this.m_titlerow.insertCell(-1);
            cell.innerHTML = "";    
        }
        for(let j = 0; j < this.m_coltypes.length; j++){
            cell = this.m_titlerow.insertCell(-1);
            cell.innerHTML = this.m_coltypes[j][GridColLabel];
            cell.className = "title";
            if(sortcols == null){
                continue;
            }
            if(this.m_subtitles == null && sortcols.includes(j)){
                this.SetSorting(cell, this.m_coltypes[j][GridColLabel], j);
            }
        }
        if(this.m_subtitles != null){
            // do not change order
            this.InsertSubTitle(this.m_subtitles.subtitles, sortcols);
            this.CombineTitle(this.m_subtitles.index, this.m_subtitles.coltitles);
        }

        this.ApplyData();
    }

    ApplyData()
    {
        let rowdata;
        let nrows = this.m_data.length;
        if(this.m_nrowfix >= 0){
            nrows = this.m_nrowfix;
        }
        if(!this.m_readonly){
            nrows += this.m_addrows;
        } 
        for(let i = 0; i < nrows; i++){
            rowdata = i >= this.m_data.length ? "" : this.m_data[i];
            this.AppendRow(rowdata);
        }
    }

    SetAlert(col, row, color = "red")
    {
        let id = GetIdFromCell(this.m_id, row, col);
        document.getElementById(id).style.color = color;
    }

    InsertSubTitle(titles, sortcols)
    {
        let titlerow = this.m_table.insertRow(-1);
        let cell;
        let childs = this.m_titlerow.childNodes;
        let offset = 0;
        if(this.m_withnum >= 0){            
            childs[0].rowSpan = 2;
            offset = 1;
        }
        for(let j = 0; j < titles.length; j++){
            if(titles[j] == ""){
                childs[j+offset].rowSpan = 2;
            }
            else{
                cell = titlerow.insertCell(-1);
                cell.innerHTML = titles[j];
                cell.className = "title";    
                if(sortcols != null && sortcols.includes(j)){
                    this.SetSorting(cell, titles[j], j);
                }    
            }
        }
    }

    CombineTitle(index, coltitles)
    {
        let offset = this.m_withnum >= 0 ? 1 : 0;
        let childs = this.m_titlerow.childNodes;
        sort(index, coltitles, index.length, false);
        for(let j = 0; j < index.length; j++){            
            childs[index[j]+offset].colSpan = coltitles[j][0];
            childs[index[j]+offset].innerHTML = coltitles[j][1];
            for(let i = index[j]+coltitles[j][0]-1; i > index[j]; i--){
                this.m_titlerow.removeChild(childs[i+offset]);
            }
        }
    }

    GetData()
    {
        return this.m_data;
    }

    AppendRow(rowdata){
        let cell, item, val;
        let row = this.m_table.insertRow(-1);

        if(this.m_withnum >= 0){
            cell = row.insertCell(-1);
            cell.innerHTML = this.GetEndIndex()+this.m_withnum;
        }
        for(let j = 0; j < this.m_coltypes.length; j++){
            cell = row.insertCell(-1);
            val = rowdata == "" ? "" : rowdata[j];
            if((typeof this.m_coltypes[j][GridTypeLabel]) == "object"){
                item = document.createElement("select");
                let isselect = false;

                for(let k = 0; k < this.m_coltypes[j][GridTypeLabel].length; k++){
                    let option = document.createElement("option");
                    option.value = this.m_coltypes[j][GridTypeLabel][k];
                    option.innerHTML = this.m_coltypes[j][GridTypeLabel][k];
                    if(val == this.m_coltypes[j][GridTypeLabel][k]){
                        option.selected = true;
                        isselect = true;
                    }
                    item.appendChild(option);
                }
                if(!isselect){
                    item.selectedIndex = -1;
                }
                item.addEventListener("keydown", (e) => {
                    if(e.key == "Delete"){
                        e.currentTarget.selectedIndex = -1;
                        let cell = GetCellFromId(this.m_id, e.currentTarget.id);
                        this.m_data[cell[0]][cell[1]] = "";
                    }
                });
            }
            else if(this.m_readonly || this.m_coltypes[j][GridTypeLabel] == "text"){
                item = document.createElement("div");
                if(typeof val == "number"){
                    item.innerHTML = ToPrmString(val, 4);
                }
                else{
                    item.innerHTML = val;
                }
            }
            else{
                item = document.createElement("input");
                if(this.m_coltypes[j][GridTypeLabel] == "boolean"){
                    item.setAttribute("type", "checkbox");
                    if(val == true){
                        item.setAttribute("checked", true);
                    }    
                }
                else{
                    item.setAttribute("type", "text");
                    if(typeof val == "number"){
                        item.value  = ToPrmString(val, 4);
                    }
                    else{
                        item.value = val;
                    }
                }
                if(this.m_readonly){
                    item.setAttribute("readonly", "readonly");
                }
            }
            item.addEventListener("change", (e) => {this.Change(e);} );
            item.id = GetIdFromCell(this.m_id, this.GetEndIndex(), j);
            cell.appendChild(item);
        }        
    }

    GetTable(){
        return this.m_table;
    }

    GetEndIndex(){
        let rows = this.m_table.rows.length-2;
        if(this.m_subtitles != null){
            rows--;
        }
        return rows;
    }

    Change(event){
        let cell = GetCellFromId(this.m_id, event.currentTarget.id);
        let nadd = cell[0]+this.m_addrows-this.GetEndIndex();
        for(let n = 0; n < nadd; n++){
            this.AppendRow("");
        }
        nadd = cell[0]-(this.m_data.length-1);
        for(let n = 0; n < nadd; n++){
            this.m_data.push([]);
            for(let j = 0; j < this.m_coltypes.length; j++){
                this.m_data[this.m_data.length-1].push("");
            }
        }
        this.m_data[cell[0]][cell[1]] = event.currentTarget.value;
        let eventup = new CustomEvent("gridchange", { detail: {id: this.m_id} });
        this.m_table.dispatchEvent(eventup);
    }

    ExportGridAsASCII(skipcols){
        let values = [], lines = [];
        for(let j = 0; j < this.m_coltypes.length; j++){
            if(skipcols.includes(j)){
                continue;
            }
            values.push(this.m_coltypes[j][GridColLabel]);
        }
        lines.push(values.join("\t"));

        for(let n = 0; n < this.m_data.length; n++){
            values.length = 0;
            for(let j = 0; j < this.m_coltypes.length; j++){
                if(skipcols.includes(j)){
                    continue;
                }
                if(typeof this.m_data[n][j] == "number"){
                    values.push(ToPrmString(this.m_data[n][j], 4));
                }
                else{
                    values.push(this.m_data[n][j]);
                }
            }                
            lines.push(values.join("\t"));
        }
        let data = lines.join("\n");
        let id = [GridLabel, MenuLabels.ascii].join(IDSeparator);
        if(Framework == PythonGUILabel){
            PyQue.Put(id);
            BufferObject = data;
            return;
        }
        ExportAsciiData(data, id);
    }

}

// Class to hold the ascii data (for pre-processing)
class AsciiData {
    constructor(dim, ntargets, titles, ordinate, extitle = ""){
        this.m_dim = dim; 
            // dimension of argument 1 (2D) or 2 (3D)
        this.m_ntargets = ntargets; 
            // number of target items as a function of x (and y) 
        this.m_nitems = this.m_ntargets+this.m_dim;
            // number of items to load
        this.m_labels = new Array(this.m_nitems);
        this.m_values = new Array(this.m_nitems);
        this.m_ordinate = ordinate;
        this.m_titles = [];
        for(let m = 0; m < this.m_nitems; m++){
            this.m_values[m] = [];
            if(m < titles.length){
                this.m_titles.push(titles[m]);
            }
            else{
                this.m_titles.push("col"+m);
            }
        }
        this.m_extitle = extitle;
        this.m_exdata = [];
    }

    GetXYMeshNumber(x, y)
    {
        let dx, dy, isx1st;
        let ndata = Math.min(x.length, y.length);

        if(ndata < 2){
            return {meshx:1, meshy:1, isx1st:true};
        }

        dy = Math.abs(y[ndata-1]-y[0])/(ndata-1)*1.0e-8;
        dx = Math.abs(x[ndata-1]-x[0])/(ndata-1)*1.0e-8;

        let n;
        for(n = 1; n < ndata; n++){
            if(n == 1){
                isx1st = Math.abs(x[n]-x[n-1]) > dx;
            }
            if(Math.abs(y[n]-y[n-1]) > dy 
                    && Math.abs(x[n]-x[n-1]) > dx){
                break;
            }
        }

        let meshx, meshy;
        if(isx1st){
            meshx = n;
            meshy = ndata/meshx;
        }
        else{
            meshy = n;
            meshx = ndata/meshy;
        }
        return {meshx:meshx, meshy:meshy, isx1st:isx1st};
    }

    SetData(data, defunits = null, cols = null){
        let lines;
        if(this.m_dim == 0){
            lines = data.split(/\n|,/);
        }
        else{
            lines = data.split(/\n|\r/);
        }
        let items, n;
        let tmp = new Array(this.m_nitems);

        let units = [];
        for(let m = 0; m < this.m_nitems; m++){
            this.m_values[m].length = 0;
            if(Array.isArray(defunits)){
                if(m < defunits.length){
                    units.push(defunits[m]);
                }
                else{
                    units.push(1.0);    
                }    
            }
            else{
                units.push(1.0);
            }
        }

        if(cols == null){
            cols = new Array(this.m_nitems);
            for(let j = 0; j < this.m_nitems; j++){
                cols[j] = j+1;
            }
        }

        this.m_exdata = [];
        let nrmax = 0;
        for(let j = 0; j < cols.length; j++){
            nrmax = Math.max(nrmax, parseInt(cols[j])-1);
        }
        for(n = 0; n < lines.length; n++){
            items = lines[n].trim().split(/\s*,\s*|\s+/);
            if(items.length < nrmax){
                continue;
            }
            let isheader = false;
            for(let m = 0; m < this.m_nitems; m++){
                tmp[m] = parseFloat(items[cols[m]-1]);
                if(isNaN(tmp[m])){
                    isheader = true;
                    break;
                }
            }
            if(isheader){
                for(let m = 0; m < this.m_nitems; m++){
                    this.m_labels[m] = items[cols[m]-1];
                }
            }
            else{
                for(let m = 0; m < this.m_nitems; m++){
                    this.m_values[m].push(tmp[m]*units[m]);
                }
            }
        }

        if(this.m_dim < 2){
            return;
        }

        this.m_z = new Array(this.m_ntargets);

        let index;
        let xyspec = this.GetXYMeshNumber(this.m_values[0], this.m_values[1]);
        this.m_x = new Array(xyspec.meshx);
        this.m_y = new Array(xyspec.meshy);
        for(let i = 0; i < this.m_ntargets; i++){
            this.m_z[i] = new Array(xyspec.meshy);            
        }
        for(let m = 0; m < xyspec.meshy; m++){
            for(let i = 0; i < this.m_ntargets; i++){
                this.m_z[i][m] = new Array(xyspec.meshx);
            }
            index = xyspec.isx1st?(m*xyspec.meshx):m;
            this.m_y[m] = this.m_values[1][index];
        }
        for(let n = 0; n < xyspec.meshx; n++){
            index = xyspec.isx1st?n:(n*xyspec.meshy);
            this.m_x[n] = this.m_values[0][index];
        }
        for(let m = 0; m < xyspec.meshy; m++){
            for(let n = 0; n < xyspec.meshx; n++){
                if(xyspec.isx1st){
                    index = m*xyspec.meshx+n;
                }
                else{
                    index = n*xyspec.meshy+m;
                }
                for(let i = 0; i < this.m_ntargets; i++){
                    this.m_z[i][m][n] = this.m_values[i+2][index];                    
                }
            }
        }
    }

    GetTitle(j){
        return this.m_titles[j];
    }

    GetTitles(){
        return this.m_titles;
    }

    GetOrdinate(){
        return this.m_ordinate;
    }

    GetDimension(){
        return this.m_dim;
    }

    GetItems(){
        return this.m_nitems;
    }

    GetObj(){
        let titles = [];
        let data = [];
        if(this.m_dim < 2){
            for(let m = 0; m < this.m_nitems; m++){
                titles.push(this.m_titles[m]);
                data.push(Array.from(this.m_values[m]));
            }
        }
        else{
            titles.push(this.m_titles[0]);
            titles.push(this.m_titles[1]);
            data.push(Array.from(this.m_x));
            data.push(Array.from(this.m_y));
            for(let m = 0; m < this.m_ntargets; m++){
                titles.push(this.m_titles[m+2]);
                data.push(new Array(this.m_z[m].length));
                for(let j = 0; j < this.m_z[m].length; j++){
                    data[m+2][j] = Array.from(this.m_z[m][j])
                }
            }
        }
        let obj = {};
        obj[DataTitlesLabel] = titles;
        obj[DataLabel] = data;
        if(this.m_extitle != "" && this.m_exdata.length > 0){
            obj[this.m_extitle] = this.m_exdata;
        }
        return obj;
    }

    AddData(obj){
        if(this.m_dim < 2){
            if(obj.data.length != this.m_nitems){
                return false;
            }
            let ndata = this.m_values[0].length;
            if(obj.data[0] === this.m_values[0]){
                for(let m = 1; m < this.m_nitems; m++){
                    for(let n = 0; n < ndata; n++){
                        this.m_values[m][n] += obj.data[m][n];
                    }
                }    
            }
            else{
                let spl = new Spline();
                for(let m = 1; m < this.m_nitems; m++){
                    spl.SetSpline(obj.data[0].length, obj.data[0], obj.data[m]);
                    for(let n = 0; n < ndata; n++){
                        this.m_values[m][n] += spl.GetValue(this.m_values[0][n], true, null, 0);
                    }
                }    
            }
        }
        else{
            //--- caution: this function is not tested ---
            if(obj.data.length != this.m_ntargets+2){
                return false;
            }
            if(obj.data[0] !== this.m_x){
                return false;
            }
            if(obj.data[1] !== this.m_y){
                return false;
            }
            for(let m = 0; m < this.m_y.length; m++){
                for(let n = 0; n < this.m_x.length; n++){
                    for(let i = 0; i < this.m_ntargets; i++){
                        this.m_z[i][m][n] += obj.data[i+2][m][n];
                    }
                }
            }
        }
        return true;
    }
}

// arrange the order of parameters and configurations
function GetObjectsOptionList(order, label, optionlabel)
{
    for(let i = 0; i < order.length; i++){
        if(order[i] == SeparatorLabel){
            optionlabel.push(SeparatorLabel);
        }
        else{
            optionlabel.push(label[order[i]]);
        }
    }
}

// arrange the title to export reference
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

// check if the object is valid
function CheckDataObj(obj)
{
    if(obj.hasOwnProperty(DataTitlesLabel) == false){
        return false;
    }
    if(Array.isArray(obj[DataTitlesLabel]) == false){
        return false;
    }
    if(obj.hasOwnProperty(DataLabel) == false){
        return false;
    }
    if(Array.isArray(obj[DataLabel]) == false){
        return false;
    }
    return true;
}

// classes specific to SIMPLEX to handle parameters
class EBPrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(EBeamPrmsOrder, EBeamPrmsLabel, optionlabel);
        super(EBLabel, optionlabel);
        this.m_scans = EBeamPrmsScans;
        UpdateEBBaseNormal(this.m_jsonobj[EBeamPrmsLabel.basespec[0]], this.m_jsonobj);
        this.m_simcond = null;
        this.SetPanel();
    }

    SetObjects(simcond)
    {
        this.m_simcond = simcond;
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        validlist[EBeamPrmsLabel.pkcurr[0]] = 0;
        validlist[EBeamPrmsLabel.ebmsize[0]] = 0;
        validlist[EBeamPrmsLabel.ediv[0]] = 0;
        validlist[EBeamPrmsLabel.partspec[0]] = -1;
        validlist[EBeamPrmsLabel.basespec[0]] = -1;

        validlist[EBeamPrmsLabel.twissbunch[0]] = -1;
        validlist[EBeamPrmsLabel.twisspos[0]] = -1;
        validlist[EBeamPrmsLabel.bunchbeta[0]] = -1;
        validlist[EBeamPrmsLabel.bunchalpha[0]] = -1;

        validlist[EBeamPrmsLabel.echirp[0]] = -1;

        let bmprof = this.m_jsonobj[EBeamPrmsLabel.bmprofile[0]];
        if(bmprof == GaussianBunch || bmprof == BoxcarBunch || bmprof == CustomCurrent){
            validlist[EBeamPrmsLabel.echirp[0]] = 1;
        }

        if(bmprof == BoxcarBunch){
            validlist[EBeamPrmsLabel.bunchleng[0]] = -1;
        }
        else{
            validlist[EBeamPrmsLabel.bunchlenr[0]] = -1;
            if(bmprof != GaussianBunch){
                validlist[EBeamPrmsLabel.bunchleng[0]] = 0;
            }
        }
        if(bmprof != CustomSlice){
            validlist[EBeamPrmsLabel.slicefile[0]] = -1;
        }
        if(bmprof != CustomCurrent){
            validlist[EBeamPrmsLabel.currfile[0]] = -1;
        }
        if(bmprof != CustomEt){
            validlist[EBeamPrmsLabel.etfile[0]] = -1;
        }
        if(bmprof != CustomParticle){
            validlist[EBeamPrmsLabel.partfile[0]] = -1;
        }
        if(bmprof != SimplexOutput){
            validlist[EBeamPrmsLabel.r56[0]] = -1;
        }
        if(bmprof == CustomSlice || bmprof == CustomParticle)
        {
            validlist[EBeamPrmsLabel.eenergy[0]] = 0;
            validlist[EBeamPrmsLabel.bunchcharge[0]] = 0;
            validlist[EBeamPrmsLabel.emitt[0]] = 0;
            validlist[EBeamPrmsLabel.espread[0]] = 0;
            validlist[EBeamPrmsLabel.eta[0]] = -1;
        }
        else if(bmprof == SimplexOutput)
        {
            validlist[EBeamPrmsLabel.eenergy[0]] = 0;
            validlist[EBeamPrmsLabel.bunchcharge[0]] = -1;
            validlist[EBeamPrmsLabel.bunchleng[0]] = -1;
            validlist[EBeamPrmsLabel.emitt[0]] = 0;
            validlist[EBeamPrmsLabel.espread[0]] = 0;
            validlist[EBeamPrmsLabel.eta[0]] = -1;
        }
        else if(bmprof == CustomCurrent){
            validlist[EBeamPrmsLabel.bunchcharge[0]] = 0;
        }
        else if(bmprof == CustomEt){
            validlist[EBeamPrmsLabel.bunchcharge[0]] = 0;
            validlist[EBeamPrmsLabel.espread[0]] = 0;
        }

        if(bmprof == CustomSlice ||
            bmprof == CustomParticle)
        {
            validlist[EBeamPrmsLabel.twissbunch[0]] = 1;
            validlist[EBeamPrmsLabel.bunchbeta[0]] = 0;
            validlist[EBeamPrmsLabel.bunchalpha[0]] = 0;
            if(this.m_jsonobj[EBeamPrmsLabel.twissbunch[0]] == SlicedPrmCustom){
                validlist[EBeamPrmsLabel.twisspos[0]] = 1;
            }
            else if(this.m_jsonobj[EBeamPrmsLabel.twissbunch[0]] == SlicedPrmOptimize){
                validlist[EBeamPrmsLabel.twisspos[0]] = 0;
            }
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
        if(this.m_simcond != null){
            let isspxnone =  
                this.m_simcond.JSONObj[SimCtrlsPrmsLabel.simoption[0]] == KillQuiteLoad || 
                this.m_simcond.JSONObj[SimCtrlsPrmsLabel.simoption[0]] == RealElectronNumber;
            this.DisableSelection(EBeamPrmsLabel.bmprofile[0], SimplexOutput, isspxnone);
        }
        if(Framework == ServerLabel){
            this.DisableSelection(EBeamPrmsLabel.bmprofile[0], SimplexOutput, true);
            this.DisableSelection(EBeamPrmsLabel.bmprofile[0], CustomParticle, true);
        }
    }
}

class PartFormatOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(ParticleConfigOrder, ParticleConfigLabel, optionlabel);
        let indents = [
            ParticleConfigLabel.unitxy[0],
            ParticleConfigLabel.unitxyp[0],
            ParticleConfigLabel.unitt[0],
            ParticleConfigLabel.unitE[0],
            ParticleConfigLabel.colx[0],
            ParticleConfigLabel.colxp[0],
            ParticleConfigLabel.coly[0],
            ParticleConfigLabel.colyp[0],
            ParticleConfigLabel.colt[0],
            ParticleConfigLabel.colE[0]
        ];
        super(PartConfLabel, optionlabel, {}, {}, indents);
        this.SetPanel();
    }

    SetPanel()
    {
        let validlist = this.GetValidList();
        this.SetPanelBase(validlist);
    }
}

class PDPlotOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        let columns = [PDPLotConfigLabel.item[0]];
        GetObjectsOptionList(PDPLotConfigOrder, PDPLotConfigLabel, optionlabel);
        super(PartPlotConfLabel, optionlabel, {}, {}, [], columns);
        this.m_jsonobj[PDPLotConfigLabel.yaxis[0]] = XpLabel;
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        if(this.m_jsonobj[PDPLotConfigLabel.type[0]] == CustomSlice){
            validlist[PDPLotConfigLabel.xaxis[0]] = -1;
            validlist[PDPLotConfigLabel.yaxis[0]] = -1;
            validlist[PDPLotConfigLabel.plotparts[0]] = -1;
        }
        else{
            validlist[PDPLotConfigLabel.item[0]] = -1;
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class SeedPrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(SeedPrmsOrder, SeedPrmsLabel, optionlabel);
        super(SeedLabel, optionlabel);
        this.m_scans = SeedPrmsScans;
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        if(this.m_jsonobj[SeedPrmsLabel.seedprofile[0]] == NotAvaliable 
                || this.m_jsonobj[SeedPrmsLabel.seedprofile[0]] == SimplexOutput){
            validlist = this.GetValidList(-1);
            validlist[SeedPrmsLabel.seedprofile[0]] = 1;
            if(this.m_jsonobj[SeedPrmsLabel.seedprofile[0]] == SimplexOutput){
                validlist[SeedPrmsLabel.phase[0]] = 1;
                validlist[SeedPrmsLabel.timing[0]] = 1;
            }
        }
        else{
            validlist[SeedPrmsLabel.wavelen[0]] = 0;
            validlist[SeedPrmsLabel.raylen[0]] = 0;    
            if(this.m_jsonobj[SeedPrmsLabel.seedprofile[0]] == ChirpedPulse){
                validlist[SeedPrmsLabel.gdd[0]] = 1;
                validlist[SeedPrmsLabel.tod[0]] = 1;
                validlist[SeedPrmsLabel.stplen[0]] = 0;    
                validlist[SeedPrmsLabel.chirprate[0]] = 0;    
            }
            else{
                validlist[SeedPrmsLabel.gdd[0]] = -1;
                validlist[SeedPrmsLabel.tod[0]] = -1;
                validlist[SeedPrmsLabel.stplen[0]] = -1;    
                validlist[SeedPrmsLabel.chirprate[0]] = -1;
            }
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
        if(Framework == ServerLabel){
            this.DisableSelection(SeedPrmsLabel.seedprofile[0], SimplexOutput, true);
        }
    }

}

class MBunchPrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(EvalMBunchOrder, EvalMBunchLabel, optionlabel);

        let indents = [
            EvalMBunchLabel.relwavelen2[0],
            EvalMBunchLabel.CEP2[0],
            EvalMBunchLabel.gdd2[0],
            EvalMBunchLabel.tod2[0],
            EvalMBunchLabel.timing2[0]
        ];
        super(MBunchEvalLabel, optionlabel, {}, {}, indents);
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        if(!this.m_jsonobj[EvalMBunchLabel.iscurrent[0]]){
            validlist[EvalMBunchLabel.mbaccinteg[0]] = -1;
        }
        if(!this.m_jsonobj[EvalMBunchLabel.iscurrent[0]] && !this.m_jsonobj[EvalMBunchLabel.isEt[0]]){
            validlist[EvalMBunchLabel.tpoints[0]] = -1;
        }
        if(!this.m_jsonobj[EvalMBunchLabel.isEt[0]]){
            validlist[EvalMBunchLabel.erange[0]] = -1;
            validlist[EvalMBunchLabel.epoints[0]] = -1;
        }
        if(this.m_jsonobj[EvalMBunchLabel.isoptR56[0]]){
            validlist[EvalMBunchLabel.mbr56[0]] = 0;
        }
        else{
            validlist[EvalMBunchLabel.nr56[0]] = -1;
        }
        if(this.m_jsonobj[EvalMBunchLabel.wpulse[0]] == false){
            validlist[EvalMBunchLabel.conf2nd[0]] = -1;
            validlist[EvalMBunchLabel.relwavelen2[0]] = -1;
            validlist[EvalMBunchLabel.CEP2[0]] = -1;
            validlist[EvalMBunchLabel.gdd2[0]] = -1;
            validlist[EvalMBunchLabel.tod2[0]] = -1;
            validlist[EvalMBunchLabel.timing2[0]] = -1;
        }
        return validlist
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class SPXOutPrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(ImportSPXOutOrder, ImportSPXOutLabel, optionlabel);
        super(SPXOutLabel, optionlabel);
        this.m_scans = ImportSPXPrmsScans;
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        validlist[ImportSPXOutLabel.spxstepz[0]] = 0;
        validlist[ImportSPXOutLabel.spxstepzarr[0]] = -1;
        validlist[ImportSPXOutLabel.spxenergy[0]] = 0;
        validlist[ImportSPXOutLabel.bmletsout[0]] = 0;
        validlist[ImportSPXOutLabel.paticlesout[0]] = 0;
        validlist[ImportSPXOutLabel.paticlesout[0]] = 0;
        return validlist;
    }
    
    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class UndPrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(UndPrmsOrder, UndPrmsLabel, optionlabel);
        let ugridlists = {};
        ugridlists[UndPrmsLabel.udata[0]] = {
            coltypes:[
                {[GridColLabel]:"Segment No.", [GridTypeLabel]:[]},
                {[GridColLabel]:"Data Name", [GridTypeLabel]:[NotAvaliable]}
            ],
            withnum:-1
        };
        ugridlists[UndPrmsLabel.multiharm[0]] = {
            coltypes:[
                {[GridColLabel]:"K<sub>x</sub> Ratio", [GridTypeLabel]:"number"},
                {[GridColLabel]:"K<sub>x</sub> Phase", [GridTypeLabel]:"number"},
                {[GridColLabel]:"K<sub>y</sub> Ratio", [GridTypeLabel]:"number"},
                {[GridColLabel]:"K<sub>y</sub> Phase", [GridTypeLabel]:"number"}
            ],
            withnum:1
        };  
        ugridlists[UndPrmsLabel.tapercustom[0]] = {
            coltypes:[
                {[GridColLabel]:"K Offset", [GridTypeLabel]:"number"},
                {[GridColLabel]:"dK/dz", [GridTypeLabel]:"number"}
            ],
            withnum:1
        };  
        super(UndLabel, optionlabel, {}, ugridlists);
        this.m_scans = UndPrmsScans;
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        validlist[UndPrmsLabel.Kperp[0]] = -1;
        validlist[UndPrmsLabel.epukratio[0]] = -1;
        validlist[UndPrmsLabel.multiharm[0]] = -1;
        validlist[UndPrmsLabel.peakb[0]] = 0;
        validlist[UndPrmsLabel.periods[0]] = 0;
        validlist[UndPrmsLabel.slippage[0]] = 0;

        if(this.m_jsonobj[UndPrmsLabel.utype[0]] == EllipticUndLabel){
            validlist[UndPrmsLabel.Kperp[0]] = 1;
            validlist[UndPrmsLabel.epukratio[0]] = 1;
            validlist[UndPrmsLabel.K[0]] = -1;
        }
        else if(this.m_jsonobj[UndPrmsLabel.utype[0]] == MultiHarmUndLabel){
            validlist[UndPrmsLabel.Kperp[0]] = 1;
            validlist[UndPrmsLabel.epukratio[0]] = 1;
            validlist[UndPrmsLabel.K[0]] = -1;
            validlist[UndPrmsLabel.multiharm[0]] = 1;
        }
        else if(this.m_jsonobj[UndPrmsLabel.utype[0]] == HelicalUndLabel){
            validlist[UndPrmsLabel.Kperp[0]] = 1;
            validlist[UndPrmsLabel.K[0]] = -1;
        }

        validlist[UndPrmsLabel.opttype[0]] = -1;
        validlist[UndPrmsLabel.slicepos[0]] = -1;
        validlist[UndPrmsLabel.initial[0]] = -1;
        validlist[UndPrmsLabel.incrseg[0]] = -1;
        validlist[UndPrmsLabel.base[0]] = -1;
        validlist[UndPrmsLabel.incrtaper[0]] = -1;
        validlist[UndPrmsLabel.Kexit[0]] = -1;
        validlist[UndPrmsLabel.detune[0]] = -1;
        validlist[UndPrmsLabel.tapercustom[0]] = -1;
        let type = this.m_jsonobj[UndPrmsLabel.taper[0]];
        if(type == TaperCustom){
            validlist[UndPrmsLabel.tapercustom[0]] = 1;
            let nsegment = this.m_jsonobj[UndPrmsLabel.segments[0]];
            let gdata = this.m_jsonobj[UndPrmsLabel.tapercustom[0]];
            while(gdata.length < nsegment){
                gdata.push(["0", "0"]);
            }
        }
        else if(type != NotAvaliable){
            let opttype = this.m_jsonobj[UndPrmsLabel.opttype[0]];
            validlist[UndPrmsLabel.opttype[0]] = 1;
            if(opttype == TaperOptSlice || opttype == TaperOptWake){
                validlist[UndPrmsLabel.slicepos[0]] = 1;
            }
            if(opttype == TaperOptWake || opttype == NotAvaliable){
                validlist[UndPrmsLabel.initial[0]] = 1;
                validlist[UndPrmsLabel.incrseg[0]] = 1;
                validlist[UndPrmsLabel.base[0]] = 1;
                validlist[UndPrmsLabel.incrtaper[0]] = 1;
                if(opttype == NotAvaliable){
                    validlist[UndPrmsLabel.Kexit[0]] = 0;
                    validlist[UndPrmsLabel.detune[0]] = 0;
                }
            }
        }

        validlist[UndPrmsLabel.umautoseed[0]] = -1;
        validlist[UndPrmsLabel.umrandseed[0]] = -1;
        validlist[UndPrmsLabel.phaseerr[0]] = -1;
        validlist[UndPrmsLabel.berr[0]] = -1;
        validlist[UndPrmsLabel.xyerr[0]] = -1;
        validlist[UndPrmsLabel.allsegment[0]] = -1;
        validlist[UndPrmsLabel.tgtsegment[0]] = -1;
        validlist[UndPrmsLabel.udata[0]] = -1;
        if(this.m_jsonobj[UndPrmsLabel.umodel[0]] == ImportDataLabel){
            validlist[UndPrmsLabel.udata[0]] = 1;
        }
        else if(this.m_jsonobj[UndPrmsLabel.umodel[0]] == SpecifyErrLabel){
            validlist[UndPrmsLabel.umautoseed[0]] = 1;
            validlist[UndPrmsLabel.umrandseed[0]] = 1;
            validlist[UndPrmsLabel.phaseerr[0]] = 1;
            validlist[UndPrmsLabel.berr[0]] = 1;
            validlist[UndPrmsLabel.xyerr[0]] = 1;
            validlist[UndPrmsLabel.allsegment[0]] = 1;
            validlist[UndPrmsLabel.tgtsegment[0]] = 1;
            if(this.m_jsonobj[UndPrmsLabel.umautoseed[0]]){
                validlist[UndPrmsLabel.umrandseed[0]] = -1;
            }
            if(this.m_jsonobj[UndPrmsLabel.allsegment[0]]){
                validlist[UndPrmsLabel.tgtsegment[0]] = -1;
            }    
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.m_fixedrows[UndPrmsLabel.tapercustom[0]] = this.m_jsonobj[UndPrmsLabel.segments[0]];
        this.SetPanelBase(validlist);
    }

    SetUdataGrid(udlist){
        let udatalist = [NotAvaliable, ...udlist];
        let segments = this.m_jsonobj[UndPrmsLabel.segments[0]];
        let seglist = new Array(segments);
        for(let n = 0; n < segments; n++){
            seglist[n] = (n+1);//.toString();
        }
        let gridconf = {
            coltypes:[
                {[GridColLabel]:"Segment No.", [GridTypeLabel]:seglist},
                {[GridColLabel]:"Data Name", [GridTypeLabel]:udatalist}
            ],
            withnum:-1
        };
        this.SetGrid(UndPrmsLabel.udata[0], gridconf);    
    }
}

class WakePrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(WakePrmsOrder, WakePrmsLabel, optionlabel);
        super(WakeLabel, optionlabel);
        this.m_scans = WakePrmsScans;
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList(-1);
        validlist[WakePrmsLabel.wakeon[0]] = 1;

        if(this.m_jsonobj[WakePrmsLabel.wakeon[0]]){
            validlist[WakePrmsLabel.resistive[0]] = 1;
            validlist[WakePrmsLabel.roughness[0]] = 1;
            validlist[WakePrmsLabel.dielec[0]] = 1;
            validlist[WakePrmsLabel.wakecustom[0]] = 1;
            validlist[WakePrmsLabel.spcharge[0]] = 1;
            let isapt = false;
            if(this.m_jsonobj[WakePrmsLabel.resistive[0]]){
                validlist[WakePrmsLabel.resistivity[0]] = 1;
                validlist[WakePrmsLabel.relaxtime[0]] = 1;
                validlist[WakePrmsLabel.paralell[0]] = 1;
                isapt = true;
            }
            if(this.m_jsonobj[WakePrmsLabel.roughness[0]]){
                validlist[WakePrmsLabel.height[0]] = 1;
                validlist[WakePrmsLabel.corrlen[0]] = 1;
                isapt = true;
            }
            if(this.m_jsonobj[WakePrmsLabel.dielec[0]]){
                validlist[WakePrmsLabel.permit[0]] = 1;
                validlist[WakePrmsLabel.thickness[0]] = 1;
                isapt = true;
            }
            if(this.m_jsonobj[WakePrmsLabel.wakecustom[0]]){
                validlist[WakePrmsLabel.wakecustomdata[0]] = 1;
            }   
            validlist[WakePrmsLabel.aperture[0]] = isapt?1:-1;
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class LatticePrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(LatticePrmsOrder, LatticePrmsLabel, optionlabel);
        super(LatticeLabel, optionlabel);
        this.m_scans = LatticePrmsScans;
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        if(this.m_jsonobj[LatticePrmsLabel.ltype[0]] == FUFULabel){
            validlist[LatticePrmsLabel.qdg[0]] = -1;
            validlist[LatticePrmsLabel.qdl[0]] = -1;
        }
        if(this.m_jsonobj[LatticePrmsLabel.ltype[0]] == FUFULabel || 
            this.m_jsonobj[LatticePrmsLabel.ltype[0]] == FUDULabel ||
            this.m_jsonobj[LatticePrmsLabel.ltype[0]] == DUFULabel)
        {
            validlist[LatticePrmsLabel.dist[0]] = -1;
        }
        if(this.m_jsonobj[LatticePrmsLabel.ltype[0]] != CombinedLabel){
            validlist[LatticePrmsLabel.lperiods[0]] = -1;
        }
        validlist[LatticePrmsLabel.optbeta[0]] = 0;
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class ChicanePrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(ChicanePrmsOrder, ChicanePrmsLabel, optionlabel);
        super(ChicaneLabel, optionlabel);
        this.m_scans = ChicanePrmsScans;
        this.m_simcond = null;
        this.SetPanel();
    }

    SetObjects(simcond)
    {
        this.m_simcond = simcond;
    }

    GetShowList()
    {
        let validlist = this.GetValidList(-1);
        validlist[ChicanePrmsLabel.chicaneon[0]] = 1;

        if(this.m_simcond != null){
            if(this.m_simcond.JSONObj[SimCtrlsPrmsLabel.simoption[0]] == SmoothingGauss && 
                this.m_simcond.JSONObj[SimCtrlsPrmsLabel.skipwave[0]])
            {
                return validlist;
            }
        }
        if(!this.m_jsonobj[ChicanePrmsLabel.chicaneon[0]]){
            return validlist;
        }

        validlist[ChicanePrmsLabel.dipoleb[0]] = 0;
        validlist[ChicanePrmsLabel.dipolel[0]] = 1;
        validlist[ChicanePrmsLabel.dipoled[0]] = 1;
        validlist[ChicanePrmsLabel.offset[0]] = 0;
        validlist[ChicanePrmsLabel.delay[0]] = 1;
        validlist[ChicanePrmsLabel.rearrange[0]] = 1;        
        validlist[ChicanePrmsLabel.chpos[0]] = 1;
        validlist[ChicanePrmsLabel.monotype[0]] = 1;
        if(this.m_jsonobj[ChicanePrmsLabel.monotype[0]] == NotAvaliable){
            return validlist;
        }
        validlist[ChicanePrmsLabel.monoenergy[0]] = 1;
        if(this.m_jsonobj[ChicanePrmsLabel.monotype[0]] == XtalTransLabel){
            validlist[ChicanePrmsLabel.xtalthickness[0]] = 1;
        }
        else{
            validlist[ChicanePrmsLabel.reltiming[0]] = 1;
        }
        if(this.m_jsonobj[ChicanePrmsLabel.monotype[0]] == CustomLabel){
            validlist[ChicanePrmsLabel.monodata[0]] = 1;
            return validlist;
        }
        if(this.m_jsonobj[ChicanePrmsLabel.xtaltype[0]] == CustomLabel){
            validlist[ChicanePrmsLabel.formfactor[0]] = 1;
            validlist[ChicanePrmsLabel.latticespace[0]] = 1;
            validlist[ChicanePrmsLabel.unitvol[0]] = 1;            
        }
        else{
            validlist[ChicanePrmsLabel.formfactor[0]] = 0;
            validlist[ChicanePrmsLabel.latticespace[0]] = 0;
            validlist[ChicanePrmsLabel.unitvol[0]] = 0;    
        }
        validlist[ChicanePrmsLabel.xtaltype[0]] = 1;
        validlist[ChicanePrmsLabel.bragg[0]] = 0;
        validlist[ChicanePrmsLabel.bandwidth[0]] = 0;

        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        if(this.m_simcond != null){
            if(this.m_simcond.JSONObj[SimCtrlsPrmsLabel.simoption[0]] == SmoothingGauss && 
                this.m_simcond.JSONObj[SimCtrlsPrmsLabel.skipwave[0]])
            {
                this.m_jsonobj[ChicanePrmsLabel.chicaneon[0]] = false;
                this.SetPanelBase(validlist);
                this.DisableInput(ChicanePrmsLabel.chicaneon[0], true);
                return;
            }
        }
        this.SetPanelBase(validlist);
    }
}

class AlignUPrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(AlignErrorPrmsOrder, AlignErrorUPrmsLabel, optionlabel);
        let gridconf = {
            coltypes:[
                {[GridColLabel]:"Segment", [GridTypeLabel]:"number"},
                {[GridColLabel]:"&Delta;K", [GridTypeLabel]:"number"},
                {[GridColLabel]:"Slippage (&deg;)", [GridTypeLabel]:"number"}
            ],
            withnum:-1
        };
        let ugridlists = {};
        ugridlists[AlignErrorUPrmsLabel.sigsegment[0]] = gridconf;
    
        super(AlignmentLabel, optionlabel, {}, ugridlists);
        this.m_scans = AlignErrorUPrmsScans;
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList(-1);
        let isrand = false;
        validlist[AlignErrorUPrmsLabel.ualign[0]] = 1;
        if(this.m_jsonobj[AlignErrorUPrmsLabel.ualign[0]] == TargetErrorLabel){
            validlist[AlignErrorUPrmsLabel.Ktol[0]] = 1;
            validlist[AlignErrorUPrmsLabel.sliptol[0]] = 1;
            isrand = true;
        }
        else if(this.m_jsonobj[AlignErrorUPrmsLabel.ualign[0]] == TargetOffsetLabel){
            validlist[AlignErrorUPrmsLabel.sigsegment[0]] = 1;
        }

        validlist[AlignErrorUPrmsLabel.BPMalign[0]] = 1;
        if(this.m_jsonobj[AlignErrorUPrmsLabel.BPMalign[0]] == TargetErrorLabel){
            validlist[AlignErrorUPrmsLabel.xytol[0]] = 1;
            isrand = true;
        }
        if(isrand){
            validlist[AlignErrorUPrmsLabel.alautoseed[0]] = 1;
            if(!this.m_jsonobj[AlignErrorUPrmsLabel.alautoseed[0]]){
                validlist[AlignErrorUPrmsLabel.alrandseed[0]] = 1;
            }    
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class DispersionPrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(DispersionPrmsOrder, DispersionPrmsLabel, optionlabel);
        super(DispersionLabel, optionlabel);
        this.m_scans = DispersionPrmsScans;
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        if(!this.m_jsonobj[DispersionPrmsLabel.einjec[0]]){
            validlist[DispersionPrmsLabel.exy[0]] = -1;
            validlist[DispersionPrmsLabel.exyp[0]] = -1;
        }
        if(!this.m_jsonobj[DispersionPrmsLabel.kick[0]]){
            validlist[DispersionPrmsLabel.kickpos[0]] = -1;
            validlist[DispersionPrmsLabel.kickangle[0]] = -1;
        }
        if(!this.m_jsonobj[DispersionPrmsLabel.sinjec[0]]){
            validlist[DispersionPrmsLabel.sxy[0]] = -1;
            validlist[DispersionPrmsLabel.sxyp[0]] = -1;
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class SimCtrlPrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(SimCtrlsPrmsOrder, SimCtrlsPrmsLabel, optionlabel);
        super(SimCondLabel, optionlabel);
        this.m_scans = SimCtrlsPrmScans;
        this.m_ebeam = null;
        this.m_seed = null;
        this.m_chicane = null;
        this.SetPanel();
    }

    SetObjects(ebeam, seed, chicane)
    {
        this.m_ebeam = ebeam;
        this.m_seed = seed;
        this.m_chicane = chicane;
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        validlist[SimCtrlsPrmsLabel.stepsseg[0]] = 0;
        validlist[SimCtrlsPrmsLabel.driftsteps[0]] = 0;
        validlist[SimCtrlsPrmsLabel.slices[0]] = 0;
        validlist[SimCtrlsPrmsLabel.gpoints[0]] = 0;        

        validlist[SimCtrlsPrmsLabel.mpiprocs[0]] = -1;
        validlist[SimCtrlsPrmsLabel.threads[0]] = -1;
        if(this.m_jsonobj[SimCtrlsPrmsLabel.simmode[0]] == SSLabel){
            validlist[SimCtrlsPrmsLabel.parascheme[0]] = -1;
        }
        else{
            if(this.m_jsonobj[SimCtrlsPrmsLabel.parascheme[0]] == ParaMPILabel){
                validlist[SimCtrlsPrmsLabel.mpiprocs[0]] = 1;
            }
            else if(this.m_jsonobj[SimCtrlsPrmsLabel.parascheme[0]] == MultiThreadLabel){
                validlist[SimCtrlsPrmsLabel.threads[0]] = 1;
            }    
        }

        if(this.m_jsonobj[SimCtrlsPrmsLabel.autoseed[0]]){
            validlist[SimCtrlsPrmsLabel.randseed[0]] = -1;
        }
        if(this.m_jsonobj[SimCtrlsPrmsLabel.autostep[0]]){
            validlist[SimCtrlsPrmsLabel.step[0]] = 0;
        }
        let isss, bmspx = false, gaussng = false;
        if(this.m_ebeam != null){
            if(this.m_ebeam.JSONObj[EBeamPrmsLabel.bmprofile[0]] == SimplexOutput){
                validlist[SimCtrlsPrmsLabel.randseed[0]] = -1;
                validlist[SimCtrlsPrmsLabel.autoseed[0]] = -1;
                validlist[SimCtrlsPrmsLabel.simoption[0]] = -1;        
                bmspx = true;
            }
            isss = this.m_ebeam.JSONObj[EBeamPrmsLabel.bmprofile[0]] == GaussianBunch 
                || this.m_ebeam.JSONObj[EBeamPrmsLabel.bmprofile[0]] == BoxcarBunch;
        }
        else{
            isss = false;
        }
        if(this.m_seed != null){
            if(this.m_seed.JSONObj[SeedPrmsLabel.seedprofile[0]] == SimplexOutput){
                validlist[SimCtrlsPrmsLabel.spatwin[0]] = -1;
                validlist[SimCtrlsPrmsLabel.gpointsl[0]] = -1;
                validlist[SimCtrlsPrmsLabel.gpoints[0]] = -1;
            }
            isss = isss && this.m_seed.JSONObj[SeedPrmsLabel.seedprofile[0]] == GaussianPulse;
        }
        else{
            isss = false;
        }
        if(this.m_chicane != null){
            gaussng = this.m_chicane.JSONObj[ChicanePrmsLabel.chicaneon[0]];
        }

        validlist[SimCtrlsPrmsLabel.beamlets[0]] = -1;
        validlist[SimCtrlsPrmsLabel.slicebmlets[0]] = -1;
        validlist[SimCtrlsPrmsLabel.slicebmletsss[0]] = -1;
        validlist[SimCtrlsPrmsLabel.electrons[0]] = -1;
        validlist[SimCtrlsPrmsLabel.sliceels[0]] = -1;
        validlist[SimCtrlsPrmsLabel.sliceelsss[0]] = -1;

        if(isss && this.m_jsonobj[SimCtrlsPrmsLabel.simmode[0]] == SSLabel){
            validlist[SimCtrlsPrmsLabel.simrange[0]] = -1;
            if(this.m_ebeam.JSONObj[EBeamPrmsLabel.bmprofile[0]] == BoxcarBunch){
                validlist[SimCtrlsPrmsLabel.simpos[0]] = -1;
            }
            else{
                validlist[SimCtrlsPrmsLabel.simpos[0]] = 1;
            }
            validlist[SimCtrlsPrmsLabel.slices[0]] = -1;
            validlist[SimCtrlsPrmsLabel.parascheme[0]] = -1;
            validlist[SimCtrlsPrmsLabel.mpiprocs[0]] = -1;

            if(this.m_jsonobj[SimCtrlsPrmsLabel.simoption[0]] == RealElectronNumber){
                validlist[SimCtrlsPrmsLabel.sliceelsss[0]] = 0;
            }
            else{
                validlist[SimCtrlsPrmsLabel.slicebmletsss[0]] = 1;
            }
        }
        else{
            validlist[SimCtrlsPrmsLabel.simpos[0]] = -1;
            if(this.m_jsonobj[SimCtrlsPrmsLabel.simoption[0]] == RealElectronNumber){
                validlist[SimCtrlsPrmsLabel.electrons[0]] = 0;
                validlist[SimCtrlsPrmsLabel.sliceels[0]] = 0;        
            }
            else if(!bmspx){
                validlist[SimCtrlsPrmsLabel.beamlets[0]] = 1;
                validlist[SimCtrlsPrmsLabel.slicebmlets[0]] = 0;        
            }
        }

        if(bmspx || 
                this.m_jsonobj[SimCtrlsPrmsLabel.simoption[0]] == KillQuiteLoad ||
                this.m_jsonobj[SimCtrlsPrmsLabel.simoption[0]] == RealElectronNumber){
            validlist[SimCtrlsPrmsLabel.particles[0]] = -1;
        }

        if(gaussng || this.m_jsonobj[SimCtrlsPrmsLabel.simoption[0]] != SmoothingGauss){
            validlist[SimCtrlsPrmsLabel.skipwave[0]] = -1;
        }
        validlist.isss = isss;
        validlist.bmspx = bmspx;
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);

        this.DisableSelection(SimCtrlsPrmsLabel.simmode[0], SSLabel, !validlist.isss);
        this.DisableSelection(SimCtrlsPrmsLabel.simoption[0], KillQuiteLoad, validlist.bmspx);
        this.DisableSelection(SimCtrlsPrmsLabel.simoption[0], RealElectronNumber, validlist.bmspx);
        if(Framework == ServerLabel){
            this.DisableSelection(SimCtrlsPrmsLabel.parascheme[0], ParaMPILabel, true);
        }    
    }
}

class OutDataPrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(DataOutPrmsOrder, DataOutPrmsLabel, optionlabel);
        super(DataDumpLabel, optionlabel);
        this.SetPrecision([2, 2]);
        this.SetPanel();
        this.m_simcond = null;
    }

    SetObjects(simcond)
    {
        this.m_simcond = simcond;
    }

    GetShowList()
    {
        let isss = false;
        if(this.m_simcond != null){
            isss = this.m_simcond.JSONObj[SimCtrlsPrmsLabel.simmode[0]] == SSLabel;
        }

        let validlist = this.GetValidList();
        if(this.m_simcond != null){
            if(this.m_simcond.JSONObj[SimCtrlsPrmsLabel.simoption[0]] == SmoothingGauss &&
                    this.m_simcond.JSONObj[SimCtrlsPrmsLabel.skipwave[0]])
            {
                validlist[DataOutPrmsLabel.spatial[0]] = -1;
                validlist[DataOutPrmsLabel.spectral[0]] = -1;
                validlist[DataOutPrmsLabel.angular[0]] = -1;
                validlist[DataOutPrmsLabel.radiation[0]] = -1;
                this.m_jsonobj[DataOutPrmsLabel.radiation[0]] = false;
            }
        }

        validlist[DataOutPrmsLabel.pfilesize[0]] = 0;
        validlist[DataOutPrmsLabel.rfilesize[0]] = 0;

        if(!this.m_jsonobj[DataOutPrmsLabel.particle[0]]){
            validlist[DataOutPrmsLabel.pfilesize[0]] = -1;
        }
        if(!this.m_jsonobj[DataOutPrmsLabel.radiation[0]]){
            validlist[DataOutPrmsLabel.rfilesize[0]] = -1;
        }
        if(Framework == ServerLabel){
            validlist[DataOutPrmsLabel.rawdata[0]] = -1;
            validlist[DataOutPrmsLabel.particle[0]] = -1;
            validlist[DataOutPrmsLabel.radiation[0]] = -1;
            validlist[DataOutPrmsLabel.pfilesize[0]] = -1;
            validlist[DataOutPrmsLabel.rfilesize[0]] = -1;
        }
        if(Framework == ServerLabel || 
            (!this.m_jsonobj[DataOutPrmsLabel.particle[0]] 
                && !this.m_jsonobj[DataOutPrmsLabel.radiation[0]])){
            validlist[DataOutPrmsLabel.expstep[0]] = -1;
            validlist[DataOutPrmsLabel.iniseg[0]] = -1;
            validlist[DataOutPrmsLabel.segint[0]] = -1;
            validlist[DataOutPrmsLabel.stepinterv[0]] = -1;
        }
        else{
            if(this.m_jsonobj[DataOutPrmsLabel.expstep[0]] != DumpSpecifyLabel){
                validlist[DataOutPrmsLabel.iniseg[0]] = -1;
                validlist[DataOutPrmsLabel.segint[0]] = -1;
            }
            if(this.m_jsonobj[DataOutPrmsLabel.expstep[0]] != RegularIntSteps){
                validlist[DataOutPrmsLabel.stepinterv[0]] = -1;
            }
        }
        if(isss){
            validlist[DataOutPrmsLabel.temporal[0]] = -1;
            validlist[DataOutPrmsLabel.spectral[0]] = -1;
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class FELPrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(FELPrmsOrder, FELPrmsLabel, optionlabel);
        super(FELLabel, optionlabel);
        this.m_scans = FELPrmsScans;
        this.SetPrecision([5, 3]);
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList(0);
        validlist[FELPrmsLabel.avgbetasel[0]] = 1;
        validlist[FELPrmsLabel.e1st[0]] = 1;
        validlist[FELPrmsLabel.l1st[0]] = 1;
        validlist[FELPrmsLabel.optbeta[0]] = -1;
        validlist[FELPrmsLabel.avgbetavalue[0]] = -1;
        validlist[FELPrmsLabel.inputbeta[0]] = -1;
        if(this.m_jsonobj[FELPrmsLabel.avgbetasel[0]] == AvgBetaOpt){
            validlist[FELPrmsLabel.optbeta[0]] = 0;
        }
        else if(this.m_jsonobj[FELPrmsLabel.avgbetasel[0]] == AvgBetaCurr){
            validlist[FELPrmsLabel.avgbetavalue[0]] = 0;
        }
        else{
            validlist[FELPrmsLabel.inputbeta[0]] = 1;
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class OutFileOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(OutputOptionsOrder, OutputOptionsLabel, optionlabel);
        super(OutFileLabel, optionlabel);
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        validlist[OutputOptionsLabel.comment[0]] = -1; // kill comment parameter
        if(Framework == ServerLabel){
            validlist[OutputOptionsLabel.folder[0]] = -1;
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class DataUnitsOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(DataUnitsOrder, DataUnitsLabel, optionlabel);
        super(DataUnitLabel, optionlabel);
        this.SetPanel();
    }

    SetPanel()
    {
        let validlist = this.GetValidList();
        this.SetPanelBase(validlist);
    }
}

class PlotOptions extends PrmOptionList {
    constructor(dimension = 1, animation = false, nplots = 1){
        let optionlabel = [];
        GetObjectsOptionList(PlotOptionsOrder, PlotOptionsLabel, optionlabel);
        super(POLabel, optionlabel);
        this.m_dimension = dimension;
        this.m_animation = animation;
        this.m_nplots = nplots;
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        if(this.m_dimension == 2){
            validlist[PlotOptionsLabel.xscale[0]] = -1;
            validlist[PlotOptionsLabel.yscale[0]] = -1;
            validlist[PlotOptionsLabel.type[0]] = -1;
            validlist[PlotOptionsLabel.size[0]] = -1;
            validlist[PlotOptionsLabel.width[0]] = -1;
            validlist[PlotOptionsLabel.wireframe[0]] = 
                this.m_jsonobj[PlotOptionsLabel.type2d[0]] != ContourLabel ? 1 : -1;
            validlist[PlotOptionsLabel.shadecolor[0]] = 
                this.m_jsonobj[PlotOptionsLabel.type2d[0]] == SurfaceShadeLabel ? 1 : -1;
            validlist[PlotOptionsLabel.colorscale[0]] = 
                this.m_jsonobj[PlotOptionsLabel.type2d[0]] == SurfaceShadeLabel ? -1 : 1;
            if(this.m_nplots > 1){
                validlist[PlotOptionsLabel.showscale[0]] = -1;
            }
            if(this.m_jsonobj[PlotOptionsLabel.type2d[0]] != ContourLabel){
                validlist[PlotOptionsLabel.xrange[0]] = -1;
                validlist[PlotOptionsLabel.yrange[0]] = -1;    
            }
        }
        else{
            validlist[PlotOptionsLabel.type2d[0]] = -1;
            validlist[PlotOptionsLabel.wireframe[0]] = -1;
            validlist[PlotOptionsLabel.shadecolor[0]] = -1;
            validlist[PlotOptionsLabel.colorscale[0]] = -1;  
            validlist[PlotOptionsLabel.showscale[0]] = -1;    
        }
        if(!this.m_animation || (this.m_dimension == 1 && !this.m_jsonobj[PlotOptionsLabel.yauto[0]])){
            validlist[PlotOptionsLabel.normalize[0]] = -1;
        }
        if(this.m_jsonobj[PlotOptionsLabel.xauto[0]]){
            validlist[PlotOptionsLabel.xrange[0]] = -1;
        }
        if(this.m_jsonobj[PlotOptionsLabel.yauto[0]]){
            validlist[PlotOptionsLabel.yrange[0]] = -1;
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class ScanOptions extends PrmOptionList {
    constructor(isinteger, is2d){
        let optionlabel = [];
        GetObjectsOptionList(ScanConfigOrder, ScanConfigLabel, optionlabel);
        super(ScanLabel, optionlabel);
        this.m_isinteger = isinteger;
        this.m_is2d = is2d;
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        let is2d, islink;

        if(!this.m_is2d){
            validlist[ScanConfigLabel.scan2dtype[0]] = -1;
            is2d = false;
            islink = false;
        }
        else{
            is2d = this.m_jsonobj[ScanConfigLabel.scan2dtype[0]] == Scan2D2DLabel;
            islink = this.m_jsonobj[ScanConfigLabel.scan2dtype[0]] == Scan2DLinkLabel;
        }

        if(is2d || islink){
            validlist[ScanConfigLabel.initial[0]] = -1;
            validlist[ScanConfigLabel.final[0]] = -1;
            validlist[ScanConfigLabel.initiali[0]] = -1;
            validlist[ScanConfigLabel.finali[0]] = -1;
            if(is2d){
                validlist[ScanConfigLabel.scanpoints[0]] = -1;
                validlist[ScanConfigLabel.interval[0]] = -1;
                validlist[ScanConfigLabel.iniserno[0]] = -1;
            }
            else{
                validlist[ScanConfigLabel.scanpoints2[0]] = -1;
                validlist[ScanConfigLabel.interval2[0]] = -1;
                validlist[ScanConfigLabel.iniserno2[0]] = -1;
            }
            if(this.m_isinteger){
                validlist[ScanConfigLabel.initial2[0]] = -1;
                validlist[ScanConfigLabel.final2[0]] = -1;
                validlist[ScanConfigLabel.scanpoints2[0]] = -1;
                validlist[ScanConfigLabel.scanpoints[0]] = -1;
            }
            else{
                validlist[ScanConfigLabel.initiali2[0]] = -1;
                validlist[ScanConfigLabel.finali2[0]] = -1;
                validlist[ScanConfigLabel.interval2[0]] = -1;
                validlist[ScanConfigLabel.interval[0]] = -1;
            }    
        }
        else{
            validlist[ScanConfigLabel.initial2[0]] = -1;
            validlist[ScanConfigLabel.final2[0]] = -1;
            validlist[ScanConfigLabel.initiali2[0]] = -1;
            validlist[ScanConfigLabel.finali2[0]] = -1;
            validlist[ScanConfigLabel.scanpoints2[0]] = -1;
            validlist[ScanConfigLabel.interval2[0]] = -1;
            validlist[ScanConfigLabel.iniserno2[0]] = -1;
            if(this.m_isinteger){
                validlist[ScanConfigLabel.initial[0]] = -1;
                validlist[ScanConfigLabel.final[0]] = -1;
                validlist[ScanConfigLabel.scanpoints[0]] = -1;
            }
            else{
                validlist[ScanConfigLabel.initiali[0]] = -1;
                validlist[ScanConfigLabel.finali[0]] = -1;
                validlist[ScanConfigLabel.interval[0]] = -1;
            }    
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class PreProcessOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(PreProcessPrmOrder, PreProcessPrmLabel, optionlabel);
        super(PrePLabel, optionlabel);
        this.m_currtarget = null;
        this.m_currobj = null;
        this.SetPanel(null, null);
    }

    Clear()
    {
        this.m_currtarget = null;
        this.m_currobj = null;
    }

    GetShowList()
    {
        let validlist = this.GetValidList(-1);
        let isund = 
            this.m_currtarget == PPFDlabel || 
            this.m_currtarget == PP1stIntLabel ||
            this.m_currtarget == PP2ndIntLabel ||
            this.m_currtarget == PPPhaseErrLabel;
        if(isund){
            validlist[PreProcessPrmLabel.targetuseg[0]] = 1;
            if(this.m_currobj != null){
                PreProcessPrmLabel.targetuseg[5] = this.m_currobj[UndPrmsLabel.segments[0]];
            }
        }
        else if(this.m_currtarget == PPWakeEvar ||
                this.m_currtarget == PPMonoSpectrum){
            validlist[PreProcessPrmLabel.plotpoints[0]] = 1;
        }
        else if(this.m_currtarget == PPBetaLabel){
            validlist[PreProcessPrmLabel.avbetaxy[0]] = 0;
        }
        else if(this.m_currtarget == PPOptBetaLabel){
            validlist[PreProcessPrmLabel.betamethod[0]] = 1;
            validlist[PreProcessPrmLabel.cqfg[0]] = 0;
            validlist[PreProcessPrmLabel.avbetaxy[0]] = 
                this.m_jsonobj[PreProcessPrmLabel.betamethod[0]] == PPBetaOptQgrad ? 1 : 0;
            validlist[PreProcessPrmLabel.tolbeta[0]] = 1;
            if(this.m_currobj[LatticePrmsLabel.ltype[0]] != FUFULabel){
                validlist[PreProcessPrmLabel.cqdg[0]] = 0;
            }
            validlist[PreProcessPrmLabel.cbetaxy0[0]] = 0;
            validlist[PreProcessPrmLabel.calphaxy0[0]] = 0;
        }
        return validlist;
    }

    SetPanel(target = null, obj = null)
    {
        if(target != null){
            this.m_currtarget = target;
        }
        if(obj != null){
            this.m_currobj = obj;
        }
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
    }
}

class PostProcessOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(PostProcessPrmOrder, PostProcessPrmLabel, optionlabel);

        let indents = [
            PostProcessPrmLabel.s1[0],
            PostProcessPrmLabel.s2[0],
            PostProcessPrmLabel.s3[0]
        ];

        super(PostPLabel, optionlabel,  {}, {}, indents);
        this.m_input = null;
        this.m_range = {};        
        this.SetPanel();
    }

    SetInput(input, exprms)
    {
        this.m_input = input;
        this.m_exprms = exprms;
        this.ArrangeInput();

        let prms = [
            PostProcessPrmLabel.zwindow[0], 
            PostProcessPrmLabel.timewindow[0], 
            PostProcessPrmLabel.energywindow[0],
            PostProcessPrmLabel.spatwindow[0],
            PostProcessPrmLabel.anglindow[0]];
        
        for(let j = 0; j < 2; j++){
            for(let i = 0; i < prms.length; i++){
                let id = GetIDFromItem(PostPLabel, prms[i], j);
                UpdateOptions(id);
            }
        }

        this.SetPanel();
    }

    GetExprms(){
        return this.m_exprms;
    }

    SetCoordinateValue(label, jtgt)
    {
        if(label == PostProcessPrmLabel.zrange[0]){
            label = PostProcessPrmLabel.zwindow[0];
        }
        if(label == PostProcessPrmLabel.timerange[0]){
            label = PostProcessPrmLabel.timewindow[0];
        }
        if(label == PostProcessPrmLabel.energyrange[0]){
            label = PostProcessPrmLabel.energywindow[0];
        }
        if(label == PostProcessPrmLabel.spatrange[0]){
            label = PostProcessPrmLabel.spatwindow[0];
        }
        if(label == PostProcessPrmLabel.anglrange[0]){
            label = PostProcessPrmLabel.anglindow[0];
        }

        let jini, jfin;
        if(jtgt < 0){
            jini = 0; jfin = 1;
        }
        else{
            jini = jfin = jtgt;
        }

        let valitems = [];
        for(let j = jini; j <= jfin; j++){
            let valitem;
            let validmin = this.m_range[label][j][0];
            let validmax = this.m_range[label][j][1];
            this.m_jsonobj[label][j] = Math.max(Math.min(this.m_jsonobj[label][j], validmax), validmin);
            let valindex = this.m_jsonobj[label][j];
            if(label == PostProcessPrmLabel.zwindow[0]){
                valitem = PostProcessPrmLabel.zvalue[0];
                if(this.m_jsonobj[PostProcessPrmLabel.zrange[0]] == PostPIntegFullLabel){
                    valindex = j == 0 ? validmin : validmax;
                }
                this.m_jsonobj[valitem][j] = this.m_exprms[StepCoordLabel][valindex-1];
            }
            else if(label == PostProcessPrmLabel.timewindow[0]){
                valitem = PostProcessPrmLabel.timevalue[0];
                if(this.m_jsonobj[PostProcessPrmLabel.timerange[0]] == PostPIntegFullLabel){
                    valindex = j == 0 ? validmin : validmax;
                }
                this.m_jsonobj[valitem][j] = this.m_exprms[SliceCoordLabel][valindex-validmin];
            }
            else if(label == PostProcessPrmLabel.energywindow[0]){
                valitem = PostProcessPrmLabel.energyvalue[0];
                let EGeV = this.m_exprms[AvgEnergyLabel];
                let lu = this.m_input[UndLabel][UndPrmsLabel.lu[0]]*0.001;
                let {K, phi} = GetKValue(this.m_input[UndLabel]);
                let e1st = COEF_E1ST*EGeV**2/lu/(1+K**2/2);
                if(this.m_jsonobj[PostProcessPrmLabel.energyrange[0]] == PostPIntegFullLabel){
                    valindex = j == 0 ? validmin : validmax;
                }
                this.m_jsonobj[valitem][j] = valindex*PLANCK/(this.m_swhole/CC)+e1st;
            }
            else if(label == PostProcessPrmLabel.spatwindow[0]){
                valitem = PostProcessPrmLabel.spatvalue[0];
                if(this.m_jsonobj[PostProcessPrmLabel.spatrange[0]] == PostPIntegFullLabel){
                    valindex = validmax;
                }
                this.m_jsonobj[valitem][j] = this.m_exprms[XYCoordLabel][j]*(2*valindex+1);
            }
            else if(label == PostProcessPrmLabel.anglindow[0]){
                valitem = PostProcessPrmLabel.anglvalue[0];
                if(this.m_jsonobj[PostProcessPrmLabel.anglrange[0]] == PostPIntegFullLabel){
                    valindex = validmax;
                }
                this.m_jsonobj[valitem][j] = this.m_exprms[XYCoordLabel][j+2]*(2*valindex+1);
            }
            else if(label == PostProcessPrmLabel.smoothing[0]){
                valitem = PostProcessPrmLabel.smvalues[0];
                if(j == 0){
                    let ds = this.m_exprms[SliceCoordLabel][1]-this.m_exprms[SliceCoordLabel][0];
                    this.m_jsonobj[valitem][j] = valindex*ds;
                }
                else{
                    this.m_jsonobj[valitem][j] = valindex*PLANCK/(this.m_swhole/CC);
                }
            }
            valitems.push(valitem);
        }

        return valitems;
    }

    ArrangeInput()
    {
        if(this.m_input == null || this.m_exprms == null){
            return;
        }
        let raditems = [PostPPowerLabel, PostPCampLabel, PostPFluxLabel, PostPWignerLabel];
        let partitems = [PostPBunchFLabel, PostPPartDistLabel, PostPEnergyLabel];
        let radobj = {Radiation: raditems};
        let partobj = {Particle: partitems};
        let obj = [];
        if(this.m_input[DataDumpLabel][DataOutPrmsLabel.radiation[0]]){
            obj.push(radobj);
        }
        if(this.m_input[DataDumpLabel][DataOutPrmsLabel.particle[0]]){
            obj.push(partobj);            
        }
        if(obj.length == 0){
            obj.push(NotAvaliable);
            this.m_jsonobj[PostProcessPrmLabel.item[0]] = NotAvaliable;
        }
        else{
            if(this.m_jsonobj[PostProcessPrmLabel.item[0]] == NotAvaliable){
                this.m_jsonobj[PostProcessPrmLabel.item[0]] = PostPPowerLabel;
            }
            if(!this.m_input[DataDumpLabel][DataOutPrmsLabel.radiation[0]] 
                && raditems.includes(this.m_jsonobj[PostProcessPrmLabel.item[0]]))
            {
                this.m_jsonobj[PostProcessPrmLabel.item[0]] = PostPBunchFLabel;
            }
            if(!this.m_input[DataDumpLabel][DataOutPrmsLabel.particle[0]] 
                && partitems.includes(this.m_jsonobj[PostProcessPrmLabel.item[0]]))
            {
                this.m_jsonobj[PostProcessPrmLabel.item[0]] = PostPPowerLabel;
            }
        }
        let tgtitem = this.GetItem(PostProcessPrmLabel.item[0]);
        SetSelectMenus(tgtitem, obj, []);
        this.UpdateItem(tgtitem, PostProcessPrmLabel.item[0]);

        let nsteps = this.m_exprms[StepCoordLabel].length;
        let nslices = this.m_exprms[SliceCoordLabel].length;
        let nfft = 1;
        while(nfft < nslices+this.m_exprms[TotalStepsLabel]){ 
            // should be "slices+steps" to be consistent with the solver
            nfft <<= 1;
        }

        let slicerange = [0, nslices-1];
        let spos = this.m_exprms[SliceCoordLabel];
        let nsorg = 0;
        if(nslices > 1){
            let lslice = (spos[nslices-1]-spos[0])/(nslices-1);
            nsorg = Math.floor(spos[0]/lslice+0.5);    
        }

        for(let j = 0; j < 2; j++){
            slicerange[j] += nsorg;
        }

        this.m_swhole = nfft*(this.m_exprms[SliceCoordLabel][1]-this.m_exprms[SliceCoordLabel][0]);
        let ndata = nfft/2;
        this.m_range[PostProcessPrmLabel.zwindow[0]] = [[1, nsteps], [1, nsteps]];
        this.m_range[PostProcessPrmLabel.timewindow[0]] = [[slicerange[0], slicerange[1]], [slicerange[0], slicerange[1]]];
        this.m_range[PostProcessPrmLabel.energywindow[0]] = [[-ndata, ndata], [-ndata, ndata]];
        this.m_range[PostProcessPrmLabel.spatwindow[0]] = new Array(2);
        this.m_range[PostProcessPrmLabel.anglindow[0]] = new Array(2);
        this.m_range[PostProcessPrmLabel.smoothing[0]] = [[0, nslices], [0, ndata]];
        for(let j = 0; j < 2; j++){
            nfft = this.m_exprms[XYPointsLabel][j];
            ndata = nfft/2;
            this.m_range[PostProcessPrmLabel.spatwindow[0]][j] = [0, ndata];
            this.m_range[PostProcessPrmLabel.anglindow[0]][j] = [0, ndata];
        }
        Object.keys(this.m_range).forEach(el => {
            let item;
            for(let j = 0; j < 2; j++){
                item = this.GetItem(el, j);
                if(item != null){
                    item.setAttribute("min", this.m_range[el][j][0]);
                    item.setAttribute("max", this.m_range[el][j][1]);
                }    
            }
        });
        let item = this.GetItem(PostProcessPrmLabel.harmonic[0], -1);
        if(item != null){
            item.setAttribute("max", this.m_input[SimCondLabel][SimCtrlsPrmsLabel.maxharmonic[0]]);
        }
    }

    GetShowList()
    {
        let validlist = this.GetValidList();
        let ispdist = this.m_jsonobj[PostProcessPrmLabel.item[0]] == PostPPartDistLabel;
        let isbf = this.m_jsonobj[PostProcessPrmLabel.item[0]] == PostPBunchFLabel;
        let isedist = this.m_jsonobj[PostProcessPrmLabel.item[0]] == PostPEnergyLabel;
        let isflux = this.m_jsonobj[PostProcessPrmLabel.item[0]] == PostPFluxLabel;
        let ispower = this.m_jsonobj[PostProcessPrmLabel.item[0]] == PostPPowerLabel;
        let iscamp = this.m_jsonobj[PostProcessPrmLabel.item[0]] == PostPCampLabel;
        let iszful = this.m_jsonobj[PostProcessPrmLabel.zrange[0]] == PostPIntegFullLabel;
        let isxyfull = this.m_jsonobj[PostProcessPrmLabel.spatrange[0]] == PostPIntegFullLabel;
        let isxypfull = this.m_jsonobj[PostProcessPrmLabel.anglrange[0]] == PostPIntegFullLabel;
        let issfull = this.m_jsonobj[PostProcessPrmLabel.timerange[0]] == PostPIntegFullLabel;
        let isefull = this.m_jsonobj[PostProcessPrmLabel.energyrange[0]] == PostPIntegFullLabel;
        let iswigner = this.m_jsonobj[PostProcessPrmLabel.item[0]] == PostPWignerLabel;
        let istimewigner, isspwigner;
        if(iswigner){
            istimewigner = this.m_jsonobj[PostProcessPrmLabel.domain[0]] == PostPTimeDomainLabel;
            isspwigner = this.m_jsonobj[PostProcessPrmLabel.domain[0]] == PostPSpatDomainLabel;    
        }
        else{
            validlist[PostProcessPrmLabel.domain[0]] = -1;
            istimewigner = isspwigner = false;
        }
        if(isspwigner == false){
            validlist[PostProcessPrmLabel.axis[0]] = -1;
        }

        validlist[PostProcessPrmLabel.zvalue[0]] = 0;
        validlist[PostProcessPrmLabel.timevalue[0]] = 0;
        validlist[PostProcessPrmLabel.energyvalue[0]] = 0;
        validlist[PostProcessPrmLabel.spatvalue[0]] = 0;
        validlist[PostProcessPrmLabel.anglvalue[0]] = 0;
        validlist[PostProcessPrmLabel.bmletspp[0]] = -1;
        validlist[PostProcessPrmLabel.particlespp[0]] = -1;

        if(iszful){
            validlist[PostProcessPrmLabel.zwindow[0]] = -1;
        }
        if(issfull){
            validlist[PostProcessPrmLabel.timewindow[0]] = -1;
        }
        if(isefull){
            validlist[PostProcessPrmLabel.energywindow[0]] = -1;
        }
        if(isxyfull){
            validlist[PostProcessPrmLabel.spatwindow[0]] = -1;
            validlist[PostProcessPrmLabel.spatvalue[0]] = -1;    
        }
        if(isxypfull){
            validlist[PostProcessPrmLabel.anglindow[0]] = -1;
            validlist[PostProcessPrmLabel.anglvalue[0]] = -1;    
        }

        if(ispdist){
            validlist[PostProcessPrmLabel.harmonic[0]] = -1;
            validlist[PostProcessPrmLabel.spatrange[0]] = -1;
            validlist[PostProcessPrmLabel.spatwindow[0]] = -1;
            validlist[PostProcessPrmLabel.spatvalue[0]] = -1;
        }
        else{
            validlist[PostProcessPrmLabel.coord[0]] = -1;
        }
        validlist[PostProcessPrmLabel.r56pp[0]] = ispdist || isbf ? 1 : -1;
        validlist[PostProcessPrmLabel.smoothing[0]] = istimewigner ? 1 : -1;
        validlist[PostProcessPrmLabel.smvalues[0]] = istimewigner ? 0 : -1;
        if(ispdist || iscamp){
            validlist[PostProcessPrmLabel.alongs[0]] = -1;
            validlist[PostProcessPrmLabel.overxyf[0]] = -1;
            validlist[PostProcessPrmLabel.overxy[0]] = -1;
        }
        if(ispdist || isbf || isedist){
            validlist[PostProcessPrmLabel.zone[0]] = -1;
            validlist[PostProcessPrmLabel.anglrange[0]] = -1;
            validlist[PostProcessPrmLabel.anglindow[0]] = -1;
            validlist[PostProcessPrmLabel.anglvalue[0]] = -1;
        }
        else if(isspwigner){
            validlist[PostProcessPrmLabel.zone[0]] = -1;
        }
        else if(istimewigner){
            validlist[PostProcessPrmLabel.alongs[0]] = -1;
        }
        
        if(!isbf && !iscamp){
            validlist[PostProcessPrmLabel.realimag[0]] = -1;
        }
        if(isedist){
            validlist[PostProcessPrmLabel.alongs[0]] = -1;
        }
        if(isflux){
            validlist[PostProcessPrmLabel.alongs[0]] = -1;
            validlist[PostProcessPrmLabel.timerange[0]] = -1;
            validlist[PostProcessPrmLabel.timewindow[0]] = -1;
            validlist[PostProcessPrmLabel.timevalue[0]] = -1;
        }
        else if(!istimewigner){
            validlist[PostProcessPrmLabel.energyrange[0]] = -1;
            validlist[PostProcessPrmLabel.energywindow[0]] = -1;
            validlist[PostProcessPrmLabel.energyvalue[0]] = -1;
        }
        if(isspwigner){
            validlist[PostProcessPrmLabel.overxy[0]] = -1;
            validlist[PostProcessPrmLabel.overxyf[0]] = -1;
        }
        else if(validlist[PostProcessPrmLabel.zone[0]] >= 0 &&
                this.m_jsonobj[PostProcessPrmLabel.zone[0]] == PostPFarLabel){
            validlist[PostProcessPrmLabel.spatrange[0]] = -1;
            validlist[PostProcessPrmLabel.spatwindow[0]] = -1;
            validlist[PostProcessPrmLabel.spatvalue[0]] = -1;
            validlist[PostProcessPrmLabel.overxy[0]] = -1;
        }
        else{
            validlist[PostProcessPrmLabel.anglrange[0]] = -1;
            validlist[PostProcessPrmLabel.anglindow[0]] = -1;
            validlist[PostProcessPrmLabel.anglvalue[0]] = -1;
            validlist[PostProcessPrmLabel.overxyf[0]] = -1;
        }
        if(isedist){
            validlist[PostProcessPrmLabel.spatrange[0]] = -1;
            validlist[PostProcessPrmLabel.spatwindow[0]] = -1;
            validlist[PostProcessPrmLabel.spatvalue[0]] = -1;
            validlist[PostProcessPrmLabel.overxy[0]] = -1;
        }

        let noepu = true;
        if(this.m_input != null){
            noepu = this.m_input[UndLabel][UndPrmsLabel.utype[0]] == LinearUndLabel 
                || this.m_input[UndLabel][UndPrmsLabel.utype[0]] == HelicalUndLabel;
        }
        if(!iscamp || noepu){
            validlist[PostProcessPrmLabel.Exy[0]] = -1;
        }
        if(!(isflux||ispower) || noepu){            
            validlist[PostProcessPrmLabel.slabel[0]] = -1;
            validlist[PostProcessPrmLabel.s1[0]] = -1;
            validlist[PostProcessPrmLabel.s2[0]] = -1;
            validlist[PostProcessPrmLabel.s3[0]] = -1;
        }

        validlist.istimewigner = istimewigner;
        return validlist;
    }
    
    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
        this.ArrangeInput();
        if(validlist.istimewigner){
            if(this.m_jsonobj[PostProcessPrmLabel.zone[0]] == PostPFarLabel){
                this.DisableInput(PostProcessPrmLabel.overxyf[0], true, true);
            }
            else{
                this.DisableInput(PostProcessPrmLabel.overxy[0], true, true);
            }
        }
    }

    ExportPostPrms(){
        let obj = {};
        obj[PostPLabel] = this.ExportCurrent();
        let trlabel = PostProcessPrmLabel.timewindow[0];
        if(obj[PostPLabel].hasOwnProperty(trlabel)){
            for(let j = 0; j < 2; j++){
                obj[PostPLabel][trlabel][j] -= this.m_range[trlabel][0][0]-1;
            }    
        }
        obj[PostPLabel][BeamletsLabel] = this.m_exprms[BeamletsLabel];
        obj[PostPLabel][ParticlesLabel] = this.m_exprms[ParticlesLabel];
        obj[InputLabel] = CopyJSON(this.m_input);
        delete obj[InputLabel][PostPLabel]; // "Post-Processing" object should not be included in "Input"
        obj[DataNameLabel] = GetDataPath(this.m_input[OutFileLabel]);
        return obj;
    }
}

class SimulationProcess {
    constructor(issingle, spobj, dataname, serno, parentid, postproc, ispostp = false){
        this.m_id = GetIDFromItem(SimulationIDLabel, serno);
        this.m_serno = serno;
        this.m_postproc = postproc;
        this.m_ispostp = ispostp;
        this.m_parentid = parentid;
        this.m_running = false;
        this.m_issingle = issingle;
        this.m_spobj = [];
        this.m_spobj.push(spobj);
        this.m_datanames = [];
        this.m_datanames.push(dataname);
        this.m_div = document.createElement("div");
        this.m_div.className = "d-flex flex-column align-items-stretch flex-grow-1";
        this.m_div.id = this.m_id;
        this.m_status = 0; // waiting to start

        this.m_dots = "...";
        this.m_charlimit = 100;

        let progcnt = document.createElement("div");
        progcnt.className = "d-flex justify-content-between align-items-center";
        this.m_div.appendChild(progcnt);

        this.m_progress = document.createElement("progress");
        this.m_progress.setAttribute("max", "100");
        this.m_progress.setAttribute("value", "0");
        this.m_progress.className = "flex-grow-1"
        this.m_progress.id = GetIDFromItem(this.m_id, "progress", -1);
        progcnt.appendChild(this.m_progress);
        this.m_progress.style.visibility = "hidden";

        let btncnt = document.createElement("div");
        let dispname = issingle?GetShortPath(dataname, 5, 20):GetShortPath(dataname, 10, 25);
        btncnt.className = "d-flex align-items-center";
        if(issingle){
            let title = document.createElement("div");
            title.style.whiteSpace = "normal";
            title.style.wordBreak = "break-all";

            if(dataname.length > this.m_charlimit){
                dataname = dataname.substring(dataname.length-this.m_charlimit+this.m_dots.length);
                dataname = this.m_dots+dataname;                
            }
            btncnt.classList.add("justify-content-between");
            title.innerHTML = dispname;
            btncnt.appendChild(title);
        }
        else{
            let btn = document.createElement("button");
            btn.innerHTML = CancellAllLabel;
            btn.className = "btn btn-outline-primary btn-sm";
            btn.addEventListener("click", (e) => {
                this.CancelAll();
            });
            btncnt.appendChild(btn);

            this.m_list = document.createElement("select");
            this.m_list.setAttribute("size", "5");
            this.m_list.style.minWidth = "100%";
            this.m_list.style.fieldSizing = "fixed";
            let item = document.createElement("option");
            item.innerHTML = dispname;
            this.m_list.appendChild(item);

            let divlist = document.createElement("div");
            divlist.style.maxWidth = "280px";
            divlist.style.overflow = "auto";
            divlist.appendChild(this.m_list);
            this.m_div.appendChild(divlist);
        }

        this.m_cancelbtn = document.createElement("button");
        this.m_cancelbtn.className = "btn btn-outline-primary btn-sm";
        this.m_cancelbtn.innerHTML = RemoveLabel;
        this.m_cancelbtn.addEventListener("click", (e) => {
            this.Cancel();
        });
        btncnt.appendChild(this.m_cancelbtn);
        if(issingle){
            this.m_div.appendChild(btncnt);
        }
        else{
            progcnt.appendChild(btncnt);
        }
    }

    AppendProcess(spobj, dataname){
        this.m_spobj.push(spobj);
        this.m_datanames.push(dataname);
        let item = document.createElement("option");
        item.innerHTML = GetShortPath(dataname, 5, 20);
        this.m_list.appendChild(item);
        if(this.m_datanames.length > 5 && this.m_datanames.length <= 10){
            this.m_list.setAttribute("size", this.m_datanames.length.toString());
        }
    }

    GetList(){
        return this.m_div;
    }

    Start(nompi = false){
        this.m_status = 1; // started
        this.m_currindex = 0;
        this.m_running = true;
        this.m_cancelbtn.innerHTML = CancelLabel;
        this.m_progress.style.visibility = "visible";
        this.StartSingle(nompi);
    }

    Status()
    {
        return this.m_status;
    }

    GeneratePrmObject()
    {
        let index = this.m_currindex-1;
        ExportObjects(this.m_spobj[index], this.m_datanames[index]);
        let spobj = this.m_spobj[index];
        if(spobj.hasOwnProperty(InputLabel)){
            spobj = spobj[InputLabel];
        }
        return {dataname: this.m_datanames[index], isfixed: false};
    }

    async StartSingle(nompi){
        let dataname = this.m_datanames[this.m_currindex];
        let currspobj = this.m_spobj[this.m_currindex];

        let comtype = "solver_nompi";
        let args = ["-f", dataname];

        if(!this.m_issingle){
            this.m_list.childNodes[this.m_currindex].innerHTML 
            = GetShortPath(this.m_datanames[this.m_currindex], 10, 25)+": in progress";
        }

        if(Framework.includes("python")){
            if(Framework == PythonGUILabel){
                let command = [MenuLabels.start, this.m_serno];
                if(this.m_ispostp){
                    command[0] = MenuLabels.runpostp;                    
                }
                PyQue.Put(command);        
            }
            this.m_currindex++;
            return;
        }

        // <EMSCRIPTEN>
        if(Framework == ServerLabel){
            let prms = JSON.stringify(currspobj, null, JSONIndent);
            this.m_worker = new Worker("launch_solver.js");
            this.m_worker.addEventListener("message", (msgobj) => {
                if(msgobj.data == "ready"){
                    let threads = 1;
                    if(currspobj[SimCondLabel][SimCtrlsPrmsLabel.parascheme[0]] == MultiThreadLabel){
                        threads = currspobj[SimCondLabel][SimCtrlsPrmsLabel.threads[0]];
                    }    
                    this.m_worker.postMessage({data: prms, nthread: threads, serno: this.m_serno});    
                }
                else if(msgobj.data.data == null){
                    this.FinishSingle("");
                }
                else if(msgobj.data.dataname != ""){
                    GUIConf.postprocessor.LoadOutputFile(msgobj.data.data, msgobj.data.dataname, true)
                }
                else{
                    this.HandleStatus(msgobj.data.data);
                }
            });
            this.m_currindex++;
            return;
        }
        // </EMSCRIPTEN>        

        if(!nompi && currspobj[SimCondLabel][SimCtrlsPrmsLabel.simmode[0]] != SSLabel){
            if(currspobj[SimCondLabel][SimCtrlsPrmsLabel.parascheme[0]] == ParaMPILabel){
                comtype = "solver";
                args.unshift("./simplex_solver");
                args.unshift(currspobj[SimCondLabel][SimCtrlsPrmsLabel.mpiprocs[0]].toString());
                args.unshift("-n");
            }
            if(currspobj[SimCondLabel][SimCtrlsPrmsLabel.parascheme[0]] == MultiThreadLabel){
                args.push("-t");
                args.push(currspobj[SimCondLabel][SimCtrlsPrmsLabel.threads[0]].toString());
            }    
        }

        let prms = FormatArray(JSON.stringify(currspobj, null, JSONIndent));
        let result = await window.__TAURI__.tauri.invoke("write_file", { path: dataname, data: prms});
        if(result != ""){
            Alert(result);
            this.m_currindex++;
            this.FinishSingle();
            return;
        }

        const command = new window.__TAURI__.shell.Command(comtype, args);
        command.on("close", (data) => {
            let msg = "Done";
            if(this.m_errmsgs.length > 0){
                Alert(this.m_errmsgs.join(" "));
                msg = "Terminated incorrectly.";
            }
            else if(this.m_process == null){
                msg = "Canceled";
            }
            else if(data.code != 0){
                msg = "Terminated incorrectly; exit code "+data.code.toString();
            }
            else{
                if(this.m_datanames[this.m_currindex-1] != ""){
                    document.getElementById("postp-view-btn").click();
                    window.__TAURI__.tauri.invoke("read_file", { path: this.m_datanames[this.m_currindex-1]})
                    .then((data) => {
                        this.m_postproc.LoadOutputFile(data, this.m_datanames[this.m_currindex-1], true);    
                    });
                }
            }
            this.FinishSingle(msg);
        });
        command.stdout.on("data", (data) => {
            this.HandleStatus(data);
        });
        command.stderr.on("data", (data) => {
            this.m_errmsgs.push(data);
            this.m_process = null;
        });

        this.m_errmsgs = [];
        try{
            this.m_process = await command.spawn();
        } catch(e) {
            Alert("Cannot launch the solver: "+e+".");
            this.m_currindex++;
            this.FinishSingle();
            return;
        }

        this.m_currindex++;
    }

    HandleStatus(status)
    {
        if(status.includes(CalcStatusLabel)){
            let pct = parseInt(status.replace(CalcStatusLabel, ""));
            if(typeof pct == "number" && pct <= 100){
                this.m_progress.value = pct;
            }
        }
        else if(status.includes(Fin1ScanLabel)){
            // finished 1 scan process
            let lines = status.split("\n");
            if(lines.length < 1){
                return;
            }
            let procs = lines[0].replace(Fin1ScanLabel, "").split("/");
            if(procs.length >= 2){
                let total = parseInt(procs[1]);
                let curr = Math.min(total, parseInt(procs[0])+1);
                if(typeof curr == "number" && typeof total == "number"){
                    this.m_list.childNodes[this.m_currindex-1].innerHTML 
                    = GetShortPath(this.m_datanames[this.m_currindex-1], 5, 20)
                    +": "+curr.toString()+"/"+total.toString()+" in Progress";
                }    
            }
            if(lines.length < 2){
                return;
            }
            this.LoadScanSingle(lines[1]);
        }
        else if(status.includes(ScanOutLabel)){
            this.LoadScanSingle(status);
        }
        else if(status.includes(ErrorLabel)){
            Alert(status);
        }
        else if(status.includes(WarningLabel)){
            Alert(status);
        }
    }

    LoadScanSingle(line)
    {
        let outname = line.replace(ScanOutLabel, "").trim();
        window.__TAURI__.tauri.invoke("read_file", { path: outname})
        .then((data) => {
            this.m_postproc.LoadOutputFile(data, outname, true);    
        });
    }

    ReleaseProcess(id)
    {
        this.m_status = -1; // completed
        let cprocdiv = document.getElementById(this.m_parentid);
        let item = document.getElementById(id);
        cprocdiv.removeChild(item);
        if(cprocdiv.childElementCount == 0){
            cprocdiv.parentElement.classList.add("d-none");
        }
    }
    
    FinishSingle(msg = "Done"){
        if(this.m_currindex < this.m_spobj.length){
            this.m_list.childNodes[this.m_currindex-1].disabled = true;
            this.m_list.childNodes[this.m_currindex-1].innerHTML 
                = GetShortPath(this.m_datanames[this.m_currindex-1], 5, 20)+": "+msg;
            this.StartSingle();
        }
        else{
            this.m_div.innerHTML = "";
            this.m_div.style.display = "d-none";
            this.ReleaseProcess(this.m_id);
        }
    }

    async CancelAll(){
        if(this.m_running){
            await this.KillCurrent();
        }
        this.m_spobj.length = 0;
        this.m_div.innerHTML = "";
        this.m_div.style.display = "d-none";
        this.ReleaseProcess(this.m_id);
    }

    Cancel(){
        if(this.m_issingle){
            this.KillCurrent();
            this.FinishSingle();
            return;
        }
        let index = this.m_list.selectedIndex;
        if(this.m_running){
            if(index >= this.m_currindex){
                this.RemoveProcess(index);
            }
            else{
                this.KillCurrent();
            }
        }
        else{
            if(index < 0){
                return;
            }
            this.RemoveProcess(index);
        }
    }

    RemoveProcess(index){
        let item = this.m_list.childNodes[index];
        this.m_list.removeChild(item);
        this.m_spobj.splice(index, 1);
        this.m_datanames.splice(index, 1)
    }

    async KillCurrent(){
        if(Framework == ServerLabel){
            this.m_worker.terminate();
        }
        else if(Framework != TauriLabel){
            PyQue.Put([CancelLabel, this.m_serno])
        }
        else{
            await this.m_process.kill();
            this.m_process = null;    
        }
    }

    ExportProcesses(){
        let prms;
        if(this.m_spobj.length == 1){            
            return this.m_spobj[0];
        }
        let calcobjs = [];
        for(let n = 0; n < this.m_datanames.length; n++){
            let calcobj = {};
            calcobj[this.m_datanames[n]] = this.m_spobj[n];
            calcobjs.push(calcobj);
        }
        return calcobjs;
    }
}

function UpdateOptions(tgtid)
{
    let item = GetItemFromID(tgtid);
    if(item.categ == PartPlotConfLabel){
        UpdateParticlePlot();
    }
    if(item.categ == PartConfLabel){
        AnalyzeParticle();
    }
    else if(item.categ == PostPLabel){
        if(
            item.item == PostProcessPrmLabel.zrange[0] || 
            item.item == PostProcessPrmLabel.timerange[0] ||
            item.item == PostProcessPrmLabel.energyrange[0] ||
            item.item == PostProcessPrmLabel.spatrange[0] ||
            item.item == PostProcessPrmLabel.anglrange[0] ||
            item.item == PostProcessPrmLabel.zwindow[0] || 
            item.item == PostProcessPrmLabel.timewindow[0] ||
            item.item == PostProcessPrmLabel.energywindow[0] ||
            item.item == PostProcessPrmLabel.spatwindow[0] ||
            item.item == PostProcessPrmLabel.anglindow[0] ||
            item.item == PostProcessPrmLabel.smoothing[0]
        )
        {
            let tgtitems = [null, null];
            for(let j = 0; j < 2; j++){
                tgtitems[j] = GUIConf.GUIpanels[PostPLabel].GetItem(item.item, j);
            }
            if(tgtitems[0] != null && tgtitems[1] != null){ // tgtitems should be an array
                GUIConf.GUIpanels[PostPLabel].UpdateItem(tgtitems, item.item);
            }
            let valitems = GUIConf.GUIpanels[PostPLabel].SetCoordinateValue(item.item, item.jxy);
            for(let i = 0; i < valitems.length; i++){
                let tgtitem = GUIConf.GUIpanels[PostPLabel].GetItem(valitems[i]);
                if(tgtitem != null){ // tgtitem is a single item
                    GUIConf.GUIpanels[PostPLabel].UpdateItem(tgtitem, valitems[i]);
                }    
            }
        }
        return;
    }
    else if(item.categ == PrePLabel){
        if(document.getElementById(GetPreprocID("optimize")).classList.contains("d-none")){
            DrawPPPlot();    
        }
    }
    else if(item.categ != POLabel){
        if(item.categ == EBLabel){
            if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == CustomParticle 
                    && GUIConf.part_data == null && GetParticleDatapath() != ""){
                ImportParticle();
                return;
            }
            if(EBBasePrmLabels.includes(item.item)){
                if(item.jxy >= 0){
                    GUIConf.input[EBLabel][EBeamPrmsLabel.basespec[0]][item.item][item.jxy]
                        = GUIConf.input[EBLabel][item.item][item.jxy];
                }
                else{
                    GUIConf.input[EBLabel][EBeamPrmsLabel.basespec[0]][item.item] 
                        = GUIConf.input[EBLabel][item.item]
                }
            }
            else if(item.item == EBeamPrmsLabel.bmprofile[0]){
                SetSPXOut();
                UpdateEBBaseSpecs();
            }
            else if(item.item == EBeamPrmsLabel.twissbunch[0] || item.item == EBeamPrmsLabel.twisspos[0]){
                let specs = null;
                if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == CustomSlice && 
                        GUIConf.input[EBLabel][EBeamPrmsLabel.slicefile[0]].hasOwnProperty("data")){
                    specs = GetEBeamSpecSlice(GUIConf.input[EBLabel][EBeamPrmsLabel.slicefile[0]].data);
                }
                else if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == CustomParticle && GUIConf.slice_prms[0].length > 0){
                    specs = GetEBeamSpecSlice(GUIConf.slice_prms);
                }
            }
        }
        if(item.categ == SeedLabel){
            if(item.item == SeedPrmsLabel.seedprofile[0]){
                SetSPXOut();
            }
        }
        if(item.categ == SPXOutLabel){
            if(item.item == ImportSPXOutLabel.spxfile[0]){
                LoadSPXOutput().then((e) => {
                    ArrangeSPXOutput();
                })
                .catch((e) => {
                    Alert(e);
                    let outobj = GUIConf.input[SPXOutLabel];
                    outobj[ImportSPXOutLabel.spxfile[0]] = "";
                    outobj[ImportSPXOutLabel.spxstep[0]] = 0;
                    outobj[ImportSPXOutLabel.spxstepzarr[0]] = [];
                    outobj[ImportSPXOutLabel.spxstepz[0]] = null;
                    outobj[ImportSPXOutLabel.bmletsout[0]] = null;
                    outobj[ImportSPXOutLabel.paticlesout[0]] = null;
                    outobj[ImportSPXOutLabel.spxenergy[0]] = null;
                    ArrangeSPXOutput();
                });
                return;
            }
            if(item.item == ImportSPXOutLabel.spxstep[0]){
                SetExportZ();
            }
            else{
                SetSPXOut();
            }
            if(GUIConf.input[EBLabel][EBeamPrmsLabel.bmprofile[0]] == SimplexOutput){
                UpdateEBBaseSpecs();
            }
        }
        if(item.categ == UndLabel && 
                (item.item == UndPrmsLabel.segments[0] || item.item == UndPrmsLabel.umodel[0])){
            SetUndulatorDataList();
        }
        if(item.categ == LatticeLabel){
            GUIConf.input[PrePLabel] = GUIConf.GUIpanels[PrePLabel].JSONObj; // to save in the parameter file
            if(item.item == LatticePrmsLabel.qfg[0]){
                GUIConf.input[PrePLabel][PreProcessPrmLabel.cqfg[0]] 
                = GUIConf.input[LatticeLabel][LatticePrmsLabel.qfg[0]];
            }
            else if(item.item == LatticePrmsLabel.qdg[0]){
                GUIConf.input[PrePLabel][PreProcessPrmLabel.cqdg[0]]
                = GUIConf.input[LatticeLabel][LatticePrmsLabel.qdg[0]];
            }            
        }
        if(item.categ == ChicaneLabel){
            if(item.item == ChicanePrmsLabel.xtaltype[0]){
                let type = GUIConf.input[ChicaneLabel][ChicanePrmsLabel.xtaltype[0]];
                if(type != CustomLabel){
                    GUIConf.input[ChicaneLabel][ChicanePrmsLabel.formfactor[0]] = BuiltinXtals[type][0];
                    GUIConf.input[ChicaneLabel][ChicanePrmsLabel.latticespace[0]] = BuiltinXtals[type][1];
                    GUIConf.input[ChicaneLabel][ChicanePrmsLabel.unitvol[0]] = BuiltinXtals[type][2];    
                }
            }
        }
        Update(tgtid);
    }
}
