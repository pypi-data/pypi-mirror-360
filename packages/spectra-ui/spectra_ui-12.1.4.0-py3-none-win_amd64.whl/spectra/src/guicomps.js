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
                return "number";
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

// classes specific to SPECTRA to handle parameters
class AccPrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(AccLabelOrder, AccPrmsLabel, optionlabel);
        super(AccLabel, optionlabel);
        this.m_config = null;
        this.m_src = null;
        this.m_scans = AccPrmsScans;
        this.SetPanel();
    }

    SetObjects(src, config)
    {
        this.m_src = src;
        this.m_config = config;
    }    

    GetShowList(isall = false)
    {
        let validlist = this.GetValidList();
        // always-hidden paramters
        validlist[AccPrmsLabel.minsize[0]] = -1;
        validlist[AccPrmsLabel.partform[0]] = -1;
        validlist[AccPrmsLabel.buf_eGeV[0]] = -1;
        validlist[AccPrmsLabel.buf_bunchlength[0]] = -1;
        validlist[AccPrmsLabel.buf_bunchcharge[0]] = -1;
        validlist[AccPrmsLabel.buf_espread[0]] = -1;

        validlist[AccPrmsLabel.bunchdata[0]] = -1;

        let bunchtype = this.m_jsonobj[AccPrmsLabel.bunchtype[0]];
        if(isall){
            validlist[AccPrmsLabel.bunchtype[0]] = 1;
            validlist[AccPrmsLabel.imA[0]] = 1;
            validlist[AccPrmsLabel.bunches[0]] = 1;
            validlist[AccPrmsLabel.bunchdata[0]] = 1;
        }
        else if(bunchtype == CustomParticle){
            validlist = this.GetValidList(-1);
            this.m_jsonobj[AccPrmsLabel.type[0]] = LINACLabel;
            validlist[AccPrmsLabel.eGeV[0]] = 0;
            validlist[AccPrmsLabel.aimA[0]] = 0;
            validlist[AccPrmsLabel.pulsepps[0]] = 1;
            validlist[AccPrmsLabel.bunchlength[0]] = 0;
            validlist[AccPrmsLabel.bunchcharge[0]] = 0;
            validlist[AccPrmsLabel.emitt[0]] = 0;
            validlist[AccPrmsLabel.coupl[0]] = 0;
            validlist[AccPrmsLabel.espread[0]] = 0;
            validlist[AccPrmsLabel.beta[0]] = 0;
            validlist[AccPrmsLabel.alpha[0]] = 0;
            validlist[AccPrmsLabel.peakcurr[0]] = 0;
            validlist[AccPrmsLabel.sigma[0]] = 0;
            validlist[AccPrmsLabel.sigmap[0]] = 0;
            validlist[AccPrmsLabel.gaminv[0]] = 0;
            validlist[AccPrmsLabel.bunchdata[0]] = 1;
            validlist[AccPrmsLabel.bunchtype[0]] = 1;
            return validlist;
        }
        validlist[AccPrmsLabel.cirm[0]] = 1;
        validlist[AccPrmsLabel.bunches[0]] = 1;
        validlist[AccPrmsLabel.peakcurr[0]] = 0;
        validlist[AccPrmsLabel.epsilon[0]] = 0;
        validlist[AccPrmsLabel.sigma[0]] = 0;
        validlist[AccPrmsLabel.sigmap[0]] = 0;
        validlist[AccPrmsLabel.gaminv[0]] = 0;
        if(isall){
            return validlist;
        }

        if(this.m_jsonobj[AccPrmsLabel.type[0]] == RINGLabel){
            validlist[AccPrmsLabel.aimA[0]] = -1;
            validlist[AccPrmsLabel.pulsepps[0]] = -1;
            validlist[AccPrmsLabel.bunchcharge[0]] = -1;
        }
        else{
            validlist[AccPrmsLabel.aimA[0]] = 0;
            validlist[AccPrmsLabel.imA[0]] = -1;
            validlist[AccPrmsLabel.cirm[0]] = -1;
            validlist[AccPrmsLabel.bunches[0]] = -1;
        }
    
        if(bunchtype == CustomCurrent || bunchtype == CustomEt){
            validlist[AccPrmsLabel.aimA[0]] = -1;
            validlist[AccPrmsLabel.cirm[0]] = -1;
            validlist[AccPrmsLabel.bunches[0]] = -1;
            validlist[AccPrmsLabel.bunchlength[0]] = -1;
            validlist[AccPrmsLabel.bunchcharge[0]] = -1;
            validlist[AccPrmsLabel.peakcurr[0]] = -1;
        }
        if(bunchtype == CustomEt){
            validlist[AccPrmsLabel.espread[0]] = -1;
        }
        else{
            validlist[AccPrmsLabel.R56add[0]] = -1;
        }       
        validlist[AccPrmsLabel.currdata[0]] = bunchtype == CustomCurrent ? 1 : -1;
        validlist[AccPrmsLabel.Etdata[0]] = bunchtype == CustomEt ? 1 : -1;

        let calcid = "";
        if(this.m_config != null){
            if(this.m_config.JSONObj.hasOwnProperty(TypeLabel)){
                calcid = this.m_config.GetCalcID();
            }
        }
        if(calcid.includes(MenuLabels.far)){
            validlist[AccPrmsLabel.injectionebm[0]] = -1;
            validlist[AccPrmsLabel.xy[0]] = -1;
            validlist[AccPrmsLabel.xyp[0]] = -1;
        }
        else{
            if(this.m_jsonobj[AccPrmsLabel.injectionebm[0]] != CustomLabel){
                validlist[AccPrmsLabel.xy[0]] = -1;
                validlist[AccPrmsLabel.xyp[0]] = -1;    
            }
        }

        let srctype = LIN_UND_Label;
        let srccont = {isund: 1};
        if(this.m_src != null){
            srctype = this.m_src.JSONObj[TypeLabel];
            srccont = GetSrcContents(this.m_src);
        }
        let iscoh = calcid.includes(MenuLabels.cohrad);
        let isfel = iscoh && bunchtype != CustomParticle &&
            (srccont.isund >= 0 || srctype == CUSTOM_Label) &&
            this.m_config.JSONObj[ConfigPrmsLabel.fel[0]] != NoneLabel;
    
        if(calcid == "" || isfel || validlist[AccPrmsLabel.bunchdata[0]] == 1){
            validlist[AccPrmsLabel.zeroemitt[0]]  = -1;
            validlist[AccPrmsLabel.singlee[0]] = -1;
            validlist[AccPrmsLabel.zerosprd[0]] = -1;
        }
        else{
            if(iscoh && (calcid.includes(MenuLabels.efield) || calcid.includes(MenuLabels.camp)))
            {
                validlist[AccPrmsLabel.singlee[0]] = 1;
            }
            else{
                validlist[AccPrmsLabel.singlee[0]] = -1;
            }
            if(calcid.includes(MenuLabels.pdensa) ||
                calcid.includes(MenuLabels.pdenss) ||
                calcid.includes(MenuLabels.ppower)
            ){
                validlist[AccPrmsLabel.zerosprd[0]] = -1;
            }
            if(calcid.includes(MenuLabels.far) || calcid.includes(MenuLabels.Kvalue)){
                validlist[AccPrmsLabel.bunchtype[0]] = -1;
                validlist[AccPrmsLabel.currdata[0]] = -1;        
            }
            validlist[AccPrmsLabel.zeroemitt[0]] = calcid.includes(MenuLabels.tflux) ? -1 : 1;
            
            if(this.m_jsonobj[AccPrmsLabel.bunchtype[0]] == CustomEt ||
                this.m_jsonobj[AccPrmsLabel.bunchtype[0]] == CustomParticle)
            {
                validlist[AccPrmsLabel.zerosprd[0]] = -1;
            }
            else{
                let isshow;
                if(srctype == CUSTOM_Label){
                    isshow = 
                        this.m_config.JSONObj[ConfigPrmsLabel.wiggapprox[0]] == false && 
                        this.m_config.JSONObj[ConfigPrmsLabel.esmooth[0]] == false;
                }
                else{
                    isshow = 
                    iscoh || (srctype != BM_Label && srctype != WIGGLER_Label 
                            && srctype != EMPW_Label && srctype != WLEN_SHIFTER_Label) ? 1 : -1;
                }
                validlist[AccPrmsLabel.zerosprd[0]] = isshow ? 1 : -1;
            }
            if(validlist[AccPrmsLabel.singlee[0]] > 0
                    && this.m_jsonobj[AccPrmsLabel.singlee[0]] > 0){
                validlist[AccPrmsLabel.zeroemitt[0]]  = -1;
                validlist[AccPrmsLabel.zerosprd[0]] = -1;
            }
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
        if(Framework == ServerLabel){
            this.DisableSelection(AccPrmsLabel.bunchtype[0], CustomParticle, true);
        }
    }
}

class SrcPrmOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(SrcLabelOrder, SrcPrmsLabel, optionlabel);

        let ugridlists = {};
        ugridlists[SrcPrmsLabel.multiharm[0]] = {
            coltypes:[
                {[GridColLabel]:"K<sub>x</sub> Ratio", [GridTypeLabel]:"number"},
                {[GridColLabel]:"K<sub>x</sub> Phase", [GridTypeLabel]:"number"},
                {[GridColLabel]:"K<sub>y</sub> Ratio", [GridTypeLabel]:"number"},
                {[GridColLabel]:"K<sub>y</sub> Phase", [GridTypeLabel]:"number"}
            ],
            withnum:1
        };
        super(SrcLabel, optionlabel, null, ugridlists);
        this.m_acc = null;
        this.m_config = null;
        this.m_scans = SrcPrmsScans;
        this.SetPanel();
    }

    GetShowList(ismagconf = false)
    {
        let validlist = this.GetValidList();

        if(ismagconf){
            validlist = this.GetValidList(-1);
            validlist[SrcPrmsLabel.br[0]] = -1;
            validlist[SrcPrmsLabel.geofactor[0]] = -1;
            this.SetPanelBase(validlist);
            return validlist;
        }
        else{
            validlist[SrcPrmsLabel.br[0]] = -1;
            validlist[SrcPrmsLabel.geofactor[0]] = -1;    
        }

        let srccont = GetSrcContents(this.m_jsonobj);
        let srctype = this.m_jsonobj[TypeLabel];

        let iAitem = 0;
        let emittitem = 0;
        if(this.m_acc != null){
            let accobj = this.m_acc.JSONObj;
            let bunchtype = accobj[AccPrmsLabel.bunchtype[0]];
            if(bunchtype == CustomParticle){
                emittitem = -1;
            }
            if(accobj[TypeLabel] == LINACLabel && bunchtype != GaussianLabel){
                iAitem = -1;
            }
        }

        validlist[SrcPrmsLabel.fmap[0]] = -1;
        validlist[SrcPrmsLabel.fvsz[0]] = -1;
        validlist[SrcPrmsLabel.bminterv[0]] = -1;
        validlist[SrcPrmsLabel.bmtandem[0]] = -1; 

        let calcid = "";
        if(this.m_config != null){
            calcid = this.m_config.GetCalcID();
        }
        
        if(srctype == BM_Label 
                || srctype == WLEN_SHIFTER_Label
                || srctype == CUSTOM_Label
                || srctype == FIELDMAP3D_Label)
        {
            validlist = this.GetValidList(-1);
            validlist[SrcPrmsLabel.type[0]] = 1;
            if(srctype == CUSTOM_Label){
                validlist[SrcPrmsLabel.fvsz[0]] = 1;
                validlist[SrcPrmsLabel.tpower[0]] = iAitem;
                return validlist;
            }
            else if(srctype == FIELDMAP3D_Label){
                validlist[SrcPrmsLabel.fmap[0]] = 1;
                return validlist;
            }
            validlist[SrcPrmsLabel.ec[0]] = 0;
            validlist[SrcPrmsLabel.lc[0]] = 0;
            if(srctype == BM_Label){
                validlist[SrcPrmsLabel.tpowerrev[0]] = iAitem;
                validlist[SrcPrmsLabel.linpower[0]] = iAitem;
                validlist[SrcPrmsLabel.b[0]] = 1;
                validlist[SrcPrmsLabel.radius[0]] = 1;
                validlist[SrcPrmsLabel.bendlength[0]] = 1;
                validlist[SrcPrmsLabel.fringelen[0]] = 1;
                if(!calcid.includes(MenuLabels.far)){
                    validlist[SrcPrmsLabel.bmtandem[0]] = 1;
                    validlist[SrcPrmsLabel.bminterv[0]] 
                        = this.m_jsonobj[SrcPrmsLabel.bmtandem[0]]?1:-1;
                }
            }
            else{
                validlist[SrcPrmsLabel.tpower[0]] = iAitem;
                validlist[SrcPrmsLabel.bmain[0]] = 1;
                validlist[SrcPrmsLabel.mplength[0]] = 1;
                validlist[SrcPrmsLabel.subpolel[0]] = 1;
                validlist[SrcPrmsLabel.subpoleb[0]] = 1;
            }
            return validlist;
        }
    
        let ismulth = srctype == MULTI_HARM_UND_Label;
    
        validlist[SrcPrmsLabel.gap[0]] = srccont.isgap;
        validlist[SrcPrmsLabel.bxy[0]] = srccont.isbxy;
        validlist[SrcPrmsLabel.b[0]] = srccont.isb;
        validlist[SrcPrmsLabel.bmain[0]] =-1;
        validlist[SrcPrmsLabel.lu[0]] = srccont.islu;
        validlist[SrcPrmsLabel.devlength[0]] = 1;
        validlist[SrcPrmsLabel.reglength[0]] =0;
        validlist[SrcPrmsLabel.periods[0]] = srccont.isper;
        validlist[SrcPrmsLabel.Kxy0[0]] = srccont.isapple;
        validlist[SrcPrmsLabel.phase[0]] = srccont.isapple;
        validlist[SrcPrmsLabel.Kxy[0]] = srccont.isKxy;
        validlist[SrcPrmsLabel.K[0]] = srccont.isK;
        validlist[SrcPrmsLabel.Kperp[0]] = srccont.isKxy >= 0 ? 0 : -1;
        validlist[SrcPrmsLabel.e1st[0]] = srccont.ise1st;
        validlist[SrcPrmsLabel.lambda1[0]] = srccont.ise1st;
        validlist[SrcPrmsLabel.radius[0]] = -1;
        validlist[SrcPrmsLabel.bendlength[0]] = -1;
        validlist[SrcPrmsLabel.mplength[0]] = -1;
        validlist[SrcPrmsLabel.fringelen[0]] = -1;
        validlist[SrcPrmsLabel.subpolel[0]] = -1;
        validlist[SrcPrmsLabel.subpoleb[0]] = -1;
        validlist[SrcPrmsLabel.csrorg[0]] = -1;
        validlist[SrcPrmsLabel.fvsz1per[0]] =
            srctype == CUSTOM_PERIODIC_Label ? 1 : -1;
        validlist[SrcPrmsLabel.multiharm[0]] = ismulth ? 1 : -1;
    
        validlist[SrcPrmsLabel.sigmar[0]] = srccont.isund;
        validlist[SrcPrmsLabel.sigmarx[0]] = srccont.iswiggler;
        validlist[SrcPrmsLabel.sigmary[0]]  = srccont.iswiggler;
        validlist[SrcPrmsLabel.Sigmax[0]] = emittitem;
        validlist[SrcPrmsLabel.Sigmay[0]] = emittitem;
        validlist[SrcPrmsLabel.fd[0]] = -1; // always hidden
        validlist[SrcPrmsLabel.flux[0]] = iAitem < 0 ? -1 : srccont.isund;
        validlist[SrcPrmsLabel.brill[0]] 
            = iAitem < 0 || emittitem < 0 ? -1 : srccont.isund;
        validlist[SrcPrmsLabel.pkbrill[0]] 
            = iAitem < 0 || emittitem < 0 ? -1 : srccont.isund;
        validlist[SrcPrmsLabel.degener[0]] 
            = iAitem < 0 || emittitem < 0 ? -1 : srccont.isund;
        validlist[SrcPrmsLabel.ec[0]] = srccont.iswiggler;
        validlist[SrcPrmsLabel.lc[0]] = srccont.iswiggler;
        validlist[SrcPrmsLabel.tpower[0]] = iAitem;
        validlist[SrcPrmsLabel.tpowerrev[0]] = -1;
        validlist[SrcPrmsLabel.linpower[0]] = -1;

        validlist[SrcPrmsLabel.br[0]] = 
            srccont.isgap >= 0 && this.m_jsonobj[SrcPrmsLabel.gaplink[0]] == AutomaticLabel ? 1 : -1;
        validlist[SrcPrmsLabel.geofactor[0]] = validlist[SrcPrmsLabel.br[0]];
        
        let isubuitin = srccont.ise1st > 0
        let isund = srccont.isund >= 0;
        let gaplabel = SrcPrmsLabel.gaplink[0];
        let isseg = this.m_jsonobj[SrcPrmsLabel.segment_type[0]] != NoneLabel;
        let isperr = this.m_jsonobj[SrcPrmsLabel.phaseerr[0]];

        validlist[gaplabel[0]] = srccont.isgaplink >= 0 ? 1 : -1;
        validlist[SrcPrmsLabel.gaptbl[0]]
            = srccont.isgap >= 0 && this.m_jsonobj[gaplabel] == ImpGapTableLabel ? 1 : -1;
    
        validlist[SrcPrmsLabel.apple[0]]
            = srctype == ELLIPTIC_UND_Label ? 1 : -1;
    
        validlist[SrcPrmsLabel.field_str[0]] 
            = validlist[SrcPrmsLabel.lu[0]] >= 0 
            && srctype != CUSTOM_PERIODIC_Label ? 1 : -1;
        validlist[SrcPrmsLabel.endmag[0]] = validlist[SrcPrmsLabel.lu[0]] >= 0  ? 1 : -1;
    
        let ferrpmr = 1, perrprm = 1;

        if(calcid.includes(MenuLabels.far) || calcid.includes(MenuLabels.Kvalue)){
            validlist[SrcPrmsLabel.field_str[0]] = -1;
            validlist[SrcPrmsLabel.natfocus[0]] = -1;
            validlist[SrcPrmsLabel.fielderr[0]] = -1;
            ferrpmr = -1; 
            validlist[SrcPrmsLabel.phaseerr[0]] = -1;
            perrprm = -1;
            validlist[SrcPrmsLabel.bmtandem[0]] = -1;
            validlist[SrcPrmsLabel.perlattice[0]] = -1;
        }
        else{
            if(calcid.includes(MenuLabels.vpdens)){
                validlist[SrcPrmsLabel.natfocus[0]] = -1;
                validlist[SrcPrmsLabel.perlattice[0]] = -1;    
            }
            else{
                validlist[SrcPrmsLabel.natfocus[0]] = isund ? 1 : -1;
            }
            validlist[SrcPrmsLabel.fielderr[0]] = isund ? 1 : -1;
            ferrpmr = isund && this.m_jsonobj[SrcPrmsLabel.fielderr[0]] ? 1 : -1;
            validlist[SrcPrmsLabel.phaseerr[0]] = isund && !isseg ? 1 : -1;
            perrprm = isund && !isseg && this.m_jsonobj[SrcPrmsLabel.phaseerr[0]] ? 1 : -1;
        }

        validlist[SrcPrmsLabel.boffset[0]] = ferrpmr;
        validlist[SrcPrmsLabel.ltaper[0]] = ferrpmr;
        validlist[SrcPrmsLabel.qtaper[0]] = ferrpmr;

        validlist[SrcPrmsLabel.seed[0]] = perrprm;
        validlist[SrcPrmsLabel.fsigma[0]] = perrprm;
        validlist[SrcPrmsLabel.psigma[0]] = perrprm;
        validlist[SrcPrmsLabel.xysigma[0]] = perrprm;
        
        if(calcid.includes(MenuLabels.simpcalc)){
            validlist[SrcPrmsLabel.segment_type[0]] = -1;
        }
        else{
            validlist[SrcPrmsLabel.segment_type[0]] = isubuitin && !isperr ? 1 : -1;
            validlist[SrcPrmsLabel.perlattice[0]] = 
            validlist[SrcPrmsLabel.perlattice[0]] == 1 && isubuitin && !isperr 
                && this.m_jsonobj[SrcPrmsLabel.segment_type[0]] != NoneLabel ? 1 : -1;
        }

        let segprm = validlist[SrcPrmsLabel.segment_type[0]] == 1
            && this.m_jsonobj[SrcPrmsLabel.segment_type[0]] != NoneLabel
            && !calcid.includes(MenuLabels.pdensr);

        validlist[SrcPrmsLabel.segments[0]] = -1;
        validlist[SrcPrmsLabel.hsegments[0]] = -1;
        validlist[SrcPrmsLabel.interval[0]] = -1;
        validlist[SrcPrmsLabel.pslip[0]] = -1;
        validlist[SrcPrmsLabel.phi0[0]] = -1;
        validlist[SrcPrmsLabel.phi12[0]] = -1;
        validlist[SrcPrmsLabel.mdist[0]] = -1;            
        if(segprm){
            validlist[SrcPrmsLabel.pslip[0]] = 0;
            validlist[SrcPrmsLabel.interval[0]] = 1;
            let segtype = this.m_jsonobj[SrcPrmsLabel.segment_type[0]];
            if(segtype == IdenticalLabel){
                validlist[SrcPrmsLabel.segments[0]] = 1;
                validlist[SrcPrmsLabel.phi0[0]] = 1;
            }
            else{
                validlist[SrcPrmsLabel.hsegments[0]] = 1;
                validlist[SrcPrmsLabel.phi12[0]] = 1;
            }
            if(validlist[SrcPrmsLabel.perlattice[0]] == 1 && 
                    this.m_jsonobj[SrcPrmsLabel.perlattice[0]]){
                validlist[SrcPrmsLabel.mdist[0]] = 1;
            }
        }    
        return validlist;
    }

    SetPanel(ismagconf = false)
    {
        let validlist = this.GetShowList(ismagconf);
        this.SetPanelBase(validlist);
        if(Framework == ServerLabel){
            this.DisableSelection(SrcPrmsLabel.type[0], FIELDMAP3D_Label, true);
        }
    }

    SetObjects(acc, config)
    {
        this.m_acc = acc;
        this.m_config = config;
    }    
}

class ConfigPrmOptions extends PrmOptionList {
    constructor(materials){
        let optionlabel = [];
        GetObjectsOptionList(ConfigLabelOrder, ConfigPrmsLabel, optionlabel);

        let indents = [
            ConfigPrmsLabel.wigner[0],
            ConfigPrmsLabel.aprofile[0],
            ConfigPrmsLabel.csd[0],
            ConfigPrmsLabel.degcoh[0],
        ];
        super(ConfigLabel, optionlabel, {}, {}, indents);

        this.m_harmindex = [0, 0 ,0];
        for(let n = 0; n < optionlabel.length; n++){
            if(optionlabel[n][0] == ConfigPrmsLabel.hrange[0]){
                this.m_harmindex[0] = n;
            }
            else if(optionlabel[n][0] == ConfigPrmsLabel.hfix[0]){
                this.m_harmindex[1] = n;                
            }
            else if(optionlabel[n][0] == ConfigPrmsLabel.hmax[0]){
                this.m_harmindex[2] = n;                
            }
        }
        this.m_acc = null;
        this.m_src = null;
        this.m_validlist = {};
        this.m_disables = [];
        this.m_scans = ConfigPrmsScans;
        this.SetMaterialName(materials);
    }

    SetObjects(acc, src)
    {
        this.m_acc = acc;
        this.m_src = src;
    }

    GetMaterialConf(materials)
    {
        let fmaterials = {};
        fmaterials[ConfigPrmsLabel.fmateri[0]] = {
            coltypes:[
                {[GridColLabel]:"Material", [GridTypeLabel]:materials},
                {[GridColLabel]:"Thickness (mm)", [GridTypeLabel]:"number"}
            ],
            withnum:-1
        };
        fmaterials[ConfigPrmsLabel.amateri[0]] = {
            coltypes:[
                {[GridColLabel]:"Material", [GridTypeLabel]:materials},
                {[GridColLabel]:"Thickness (mm)", [GridTypeLabel]:"number"}
            ],
            withnum:-1
        };
        return fmaterials;
    }

    SetMaterialName(materials)
    {
        this.m_gridconfs = this.GetMaterialConf(materials);
        this.SetPanel();
    }

    GetShowList()
    {
        let validlist = this.GetValidList(-1);
        let calcid = this.m_jsonobj[TypeLabel];
        if(typeof calcid == "undefined"){
            calcid = "";
        }
        if(calcid == "" || this.m_src == null){
            return null;
        }
       
        let srcobj = this.m_src.JSONObj;
        let srccont = GetSrcContents(srcobj);
        let isCMD = calcid.includes(MenuLabels.CMD2d);
        let isCMDPP = calcid.includes(MenuLabels.CMDPP);
        let iswigner = calcid.includes(MenuLabels.wigner) && !isCMD;
        let isprop = calcid.includes(MenuLabels.propagate);
        let istf = calcid.includes(MenuLabels.tflux);
        let isspd = calcid.includes(MenuLabels.spdens);
        let iscoh = calcid.includes(MenuLabels.cohrad);
        let istime = calcid.includes(MenuLabels.temporal);
        let isFourier = iscoh && istime && 
            this.m_jsonobj[ConfigPrmsLabel.fouriep[0]];
        let issrcpoint = calcid.includes(MenuLabels.sprof);
        let isedep = calcid.includes(MenuLabels.energy);
        let isvoldens = calcid.includes(MenuLabels.vpdens);
        let isfixedp = calcid.includes(MenuLabels.fixed);
        let isbmlike = false;
        let issimple = calcid.includes(MenuLabels.simpcalc);
        let isKdep = calcid.includes(MenuLabels.Kvalue);
        let isallharm = calcid.includes(MenuLabels.allharm);
        let issdep = calcid.includes(MenuLabels.along) 
            || calcid.includes(MenuLabels.meshxy)
            || calcid.includes(MenuLabels.meshrphi);

        if(calcid.includes(MenuLabels.propagate)){
            validlist[ConfigPrmsLabel.efix[0]] = 1;
            validlist[ConfigPrmsLabel.zrange[0]] = 1;
            validlist[ConfigPrmsLabel.zmesh[0]] = 1;
            validlist[ConfigPrmsLabel.gridspec[0]] = 1;
            validlist[ConfigPrmsLabel.wigexplabel[0]] = 1;
            validlist[ConfigPrmsLabel.csd[0]] = 1;
            validlist[ConfigPrmsLabel.degcoh[0]] = 1;
            validlist[ConfigPrmsLabel.grlevel[0]] = 1;

            validlist[ConfigPrmsLabel.optics[0]] = 1;

            let isxy = [false, false];
            if(this.m_jsonobj[OrgTypeLabel].includes(MenuLabels.XXpYYp)){
                isxy[0] = isxy[1] = true;
            }
            else if(this.m_jsonobj[OrgTypeLabel].includes(MenuLabels.XXpprj)){
                isxy[0] = true;
            }
            else if(this.m_jsonobj[OrgTypeLabel].includes(MenuLabels.YYpprj)){
                isxy[1] = true;
            }
            if(isxy[0]){
                validlist[ConfigPrmsLabel.wigsizex[0]] = 0;
                validlist[ConfigPrmsLabel.bmsizex[0]] = 0;
                if(this.m_jsonobj[ConfigPrmsLabel.wigsizex[0]][0] == null){
                    validlist[ConfigPrmsLabel.wigsizex[0]] = -1;
                    validlist[ConfigPrmsLabel.bmsizex[0]] = -1;    
                }
            }
            if(isxy[1]){
                validlist[ConfigPrmsLabel.wigsizey[0]] = 0;
                validlist[ConfigPrmsLabel.bmsizey[0]] = 0;
                if(this.m_jsonobj[ConfigPrmsLabel.wigsizey[0]][0] == null){
                    validlist[ConfigPrmsLabel.wigsizey[0]] = -1;
                    validlist[ConfigPrmsLabel.bmsizey[0]] = -1;
                }
            }
            if(srccont.isund >= 0){
                validlist[ConfigPrmsLabel.hfix[0]] = 1;
                validlist[ConfigPrmsLabel.detune[0]] = 1;    
            }

            if(this.m_jsonobj[ConfigPrmsLabel.optics[0]] != NoneLabel){
                validlist[ConfigPrmsLabel.optpos[0]] = 1;
                validlist[ConfigPrmsLabel.aprofile[0]] = 1;
                validlist[ConfigPrmsLabel.wigner[0]] = 1;
                    if(this.m_jsonobj[ConfigPrmsLabel.optics[0]] == ThinLensLabel){
                    if(isxy[0]){
                        validlist[ConfigPrmsLabel.foclenx[0]] = 1;
                    }
                    if(isxy[1]){
                        validlist[ConfigPrmsLabel.focleny[0]] = 1;
                    }
                }
                else{
                    if(isxy[0]){
                        if(this.m_jsonobj[ConfigPrmsLabel.optics[0]] == DoubleLabel){
                            validlist[ConfigPrmsLabel.aptdistx[0]] = 1;
                        }
                        validlist[ConfigPrmsLabel.aptx[0]] = 1;
                    }
                    if(isxy[1]){
                        if(this.m_jsonobj[ConfigPrmsLabel.optics[0]] == DoubleLabel){
                            validlist[ConfigPrmsLabel.aptdisty[0]] = 1;
                        }
                        validlist[ConfigPrmsLabel.apty[0]] = 1;
                    }
                    validlist[ConfigPrmsLabel.softedge[0]] = 1;
                    validlist[ConfigPrmsLabel.diflim[0]] = 1;
                    validlist[ConfigPrmsLabel.anglelevel[0]] = 1;
                    validlist[ConfigPrmsLabel.memsize[0]] = 0;
                }
            }

            if(this.m_jsonobj[ConfigPrmsLabel.gridspec[0]] == AutomaticLabel){
                return validlist;
            }
            let xylabel = [
                [
                    ConfigPrmsLabel.xrange[0], ConfigPrmsLabel.xmesh[0], ConfigPrmsLabel.wnxrange[0]
                ],
                [
                    ConfigPrmsLabel.yrange[0], ConfigPrmsLabel.ymesh[0], ConfigPrmsLabel.wnyrange[0]
                ]
            ];
            let dxylabel = [
                [
                    ConfigPrmsLabel.wdxrange[0], ConfigPrmsLabel.wdxmesh[0], ConfigPrmsLabel.wndxrange[0]
                ],
                [
                    ConfigPrmsLabel.wdyrange[0], ConfigPrmsLabel.wdymesh[0], ConfigPrmsLabel.wndyrange[0]
                ]
            ];
            let idxdxy = this.m_jsonobj[ConfigPrmsLabel.csd[0]] 
                || this.m_jsonobj[ConfigPrmsLabel.degcoh[0]] ? 1 : -1
            for(let j = 0; j < 2; j++){
                if(isxy[j]){
                    if(this.m_jsonobj[ConfigPrmsLabel.gridspec[0]] == FixedSlitLabel){
                        validlist[xylabel[j][0]] = 1;
                        validlist[dxylabel[j][0]] = idxdxy;
                    }
                    else{
                        validlist[xylabel[j][2]] = 1;
                        validlist[dxylabel[j][2]] = idxdxy;
                    }
                    validlist[xylabel[j][1]] = 1;
                    validlist[dxylabel[j][1]] = idxdxy;
                }    
            }
            return validlist;
        }

        // if figure-8 undulator, switch harmonic numbers
        let dh = srcobj[TypeLabel] == FIGURE8_UND_Label ||
                srcobj[TypeLabel] == VFIGURE8_UND_Label ? 0.5 : 1;
        for(let j = 0; j < this.m_harmindex.length; j++){
            this.m_labels[this.m_harmindex[j]][3] = dh;
            this.m_labels[this.m_harmindex[j]][4] = dh;
        }
    
        // boolean for show info.
        let isshow = {};
       
        let iscustomsrc = false;
        let isbm = false;
        switch(srcobj[TypeLabel]){
            case BM_Label:
                isbm = true;
            case WIGGLER_Label:
            case EMPW_Label:
            case WLEN_SHIFTER_Label:
                isbmlike = true;
                break;
            case CUSTOM_Label:
                iscustomsrc = true;
                isbmlike = 
                    this.m_jsonobj[ConfigPrmsLabel.wiggapprox[0]] ||
                    this.m_jsonobj[ConfigPrmsLabel.esmooth[0]];
                break;
        } 
        let iswiggler = isbmlike && 
            srcobj[TypeLabel] != WLEN_SHIFTER_Label;
        let iswigapprox = calcid.includes(MenuLabels.far) 
            && srccont.isund >= 0 && this.m_jsonobj[ConfigPrmsLabel.wiggapprox[0]];
    
        //--- parameters ---
        // z positions
        validlist[ConfigPrmsLabel.slit_dist[0]] = 1;
        if(iswigner || isCMD || isCMDPP || istf || (isspd && !isfixedp) || isFourier || issrcpoint || issimple){
            validlist[ConfigPrmsLabel.slit_dist[0]] = -1;
        }
        if(isspd && !isfixedp){
            validlist[ConfigPrmsLabel.zrange[0]] = 1;
            validlist[ConfigPrmsLabel.zmesh[0]] = 1;
        }

        // auto range configuration
        let erangeidx = 1, trangeidx = 1;
        if(srcobj[TypeLabel] != CUSTOM_Label && srcobj[TypeLabel] != FIELDMAP3D_Label){
            if(isedep || isallharm){
                validlist[ConfigPrmsLabel.autoe[0]] = 1;
                if(this.m_jsonobj[ConfigPrmsLabel.autoe[0]]){
                    erangeidx = -1;
                }
            }
            if(issdep || isCMD || calcid.includes(MenuLabels.phasespace) 
                    || calcid.includes(MenuLabels.sprof) 
                    || calcid.includes(MenuLabels.Wrel))
            {
                validlist[ConfigPrmsLabel.autot[0]] = 1;
                if(this.m_jsonobj[ConfigPrmsLabel.autot[0]]){
                    trangeidx = -1;
                }
            }    
        }

        // energy 
        if(isedep){
            validlist[ConfigPrmsLabel.erange[0]] = erangeidx;
            if(isbmlike || iswigapprox){
                validlist[ConfigPrmsLabel.emesh[0]] = erangeidx;
            }
            else{
                validlist[ConfigPrmsLabel.de[0]] = erangeidx;
            }
            if(srccont.isund >= 0 && erangeidx == -1 && !iswigner){
                validlist[ConfigPrmsLabel.hrange[0]] = 1;
            }
        }
        if(isallharm){
            validlist[ConfigPrmsLabel.erange[0]] = erangeidx;
            validlist[ConfigPrmsLabel.emesh[0]] = erangeidx;
        }
    
        if(isvoldens && srcobj[TypeLabel] == CUSTOM_Label && isbmlike){
            validlist[ConfigPrmsLabel.epitch[0]] = 1;
        }
    
        let isefix, isdetune = false;
        if(calcid.includes(MenuLabels.spatial)){
            isefix = calcid.includes(MenuLabels.fdensa) 
                || calcid.includes(MenuLabels.camp)
                || calcid.includes(MenuLabels.fdenss);
        }
        else if(isfixedp){
            isefix = iswigner
                || calcid.includes(MenuLabels.fdensa) 
                || calcid.includes(MenuLabels.fdenss)
                || calcid.includes(MenuLabels.pflux)
                || istf
                || (srccont.isund < 0 && issimple);
        }
        else if(isCMD || isCMDPP){
            isefix = true;
        }        
        else{
            isefix = calcid.includes(MenuLabels.fluxfix)
                || calcid.includes(MenuLabels.phasespace);
        }
        if(srccont.isund >= 0 && (iswigner || isCMD || isCMDPP || isprop)){
            isdetune = !isedep;
        }
        let normenergy = srccont.isund >= 0 && 
            isefix && !isKdep && !iswigner && !isCMD && !isCMDPP && !issrcpoint;  
    
        if(isefix){
            validlist[ConfigPrmsLabel.efix[0]] = 1;
            if(srccont.isund >= 0 && normenergy
                    && this.m_jsonobj[ConfigPrmsLabel.normenergy[0]])
            {
                validlist[ConfigPrmsLabel.efix[0]] = 0;
                validlist[ConfigPrmsLabel.nefix[0]] = 1;
            }
        }
        if(isdetune){
            if(isefix){
                validlist[ConfigPrmsLabel.efix[0]] = 0;
            }
            validlist[ConfigPrmsLabel.nefix[0]] = -1;
            validlist[ConfigPrmsLabel.detune[0]] = 1;
        }
        if(issrcpoint){
            if(srccont.isund >= 0){
                validlist[ConfigPrmsLabel.efix[0]] = 0;
                validlist[ConfigPrmsLabel.detune[0]] = 1;
            }
            else{
                validlist[ConfigPrmsLabel.efix[0]] = 1;
            }
        }
    
        // obs. points
        let isangle = isFourier || 
            this.m_jsonobj[ConfigPrmsLabel.defobs[0]] == ObsPointAngle;
        if(isedep || istime || isfixedp){
            let isdens = calcid.includes(MenuLabels.fdensa)
                || calcid.includes(MenuLabels.fdenss)
                || calcid.includes(MenuLabels.pdensa)
                || calcid.includes(MenuLabels.pdenss)
                || calcid.includes(MenuLabels.efield);
            if(isdens){
                if(isangle){
                    validlist[ConfigPrmsLabel.qxyfix[0]] = 1;
                }
                else{
                    validlist[ConfigPrmsLabel.xyfix[0]] = 1;
                }
            }
            if(isspd){
                validlist[ConfigPrmsLabel.xyfix[0]] = 1;
                validlist[ConfigPrmsLabel.Qnorm[0]] = 1;
                validlist[ConfigPrmsLabel.Phinorm[0]] = 1;
            }
        }
        else if(isspd){
            if(calcid.includes(MenuLabels.xzplane)){
                validlist[ConfigPrmsLabel.spdyfix[0]] = 1;
            }
            else if(calcid.includes(MenuLabels.yzplane)){
                validlist[ConfigPrmsLabel.spdxfix[0]] = 1;
            }
            else if(calcid.includes(MenuLabels.pipe)){
                validlist[ConfigPrmsLabel.spdrfix[0]] = 1;
            }
        }
      
        // slit
        isshow.size = false;
        isshow.div = false;
        let isrect = calcid.includes(MenuLabels.slitrect);
        let aptopt = false;
        let isnorm = false;
        if(isedep || istime || isfixedp || (isKdep && !issimple)){
            let iscirc = calcid.includes(MenuLabels.slitcirc);
            if(isrect || iscirc){
                if(isangle){
                    validlist[ConfigPrmsLabel.qslitpos[0]] = 
                        !calcid.includes(MenuLabels.fluxpeak) ? 1 : -1;
                    isshow.div = true;
                }
                else{
                    validlist[ConfigPrmsLabel.slitpos[0]] = 
                        !calcid.includes(MenuLabels.fluxpeak) ? 1 : -1;
                    isshow.size = true;
                }
            }
            if(iscirc){
                if(isangle){
                    validlist[ConfigPrmsLabel.slitq[0]] = 1;
                }
                else{
                    validlist[ConfigPrmsLabel.slitr[0]] = 1;
                }
            }
            else if(isrect){
                if((isedep && srccont.isund >= 0) 
                        || (isKdep && !calcid.includes(MenuLabels.fluxfix))){
                    aptopt = true;
                    isnorm = 
                        this.m_jsonobj[ConfigPrmsLabel.aperture[0]] == NormSlitLabel;
                }
                if(isnorm){
                    if(isangle){
                        validlist[ConfigPrmsLabel.qslitapt[0]] = 0;
                    }
                    else{
                        validlist[ConfigPrmsLabel.slitapt[0]] = 0;
                    }
                    validlist[ConfigPrmsLabel.nslitapt[0]] = 1;
                    if(isKdep && !calcid.includes(MenuLabels.ppower)){
                        validlist[ConfigPrmsLabel.pplimit[0]] = 
                            this.m_jsonobj[ConfigPrmsLabel.powlimit[0]] ? 1 : -1;
                    }
                }
                else{
                    if(isangle){
                        validlist[ConfigPrmsLabel.qslitapt[0]] = 1;
                    }
                    else{
                        validlist[ConfigPrmsLabel.slitapt[0]] = 1;
                    }
                }
            }
        }  
      
        // obs. range
        if(calcid.includes(MenuLabels.along) 
                || calcid.includes(MenuLabels.meshxy))
        {
            if(isangle){
                validlist[ConfigPrmsLabel.qxrange[0]] = trangeidx;
                validlist[ConfigPrmsLabel.qyrange[0]] = trangeidx;
                isshow.div = true;
            }
            else{
                validlist[ConfigPrmsLabel.xrange[0]] = trangeidx;
                validlist[ConfigPrmsLabel.yrange[0]] = trangeidx;
                isshow.size = true;
            }
            validlist[ConfigPrmsLabel.xmesh[0]] = trangeidx;
            validlist[ConfigPrmsLabel.ymesh[0]] = trangeidx;
        } 
        if(calcid.includes(MenuLabels.meshrphi)){
            if(isangle){
                validlist[ConfigPrmsLabel.qrange[0]] = trangeidx;
                validlist[ConfigPrmsLabel.qphimesh[0]] = trangeidx;
                isshow.div = true;
            }
            else{
                validlist[ConfigPrmsLabel.rrange[0]] = trangeidx;
                validlist[ConfigPrmsLabel.rphimesh[0]] = trangeidx;
                isshow.size = true;
            }
            validlist[ConfigPrmsLabel.phirange[0]] = trangeidx;
            validlist[ConfigPrmsLabel.phimesh[0]] = trangeidx;
        }
        if(isspd){
            if(calcid.includes(MenuLabels.xzplane)){
                if(isangle){
                    validlist[ConfigPrmsLabel.qxrange[0]] = 1;
                }
                else{
                    validlist[ConfigPrmsLabel.xrange[0]] = 1;
                }
                validlist[ConfigPrmsLabel.xmesh[0]] = 1;
            }
            else if(calcid.includes(MenuLabels.yzplane)){
                if(isangle){
                    validlist[ConfigPrmsLabel.qyrange[0]] = 1;
                }
                else{
                    validlist[ConfigPrmsLabel.yrange[0]] = 1;
                }
                validlist[ConfigPrmsLabel.ymesh[0]] = 1;
            }
            else if(calcid.includes(MenuLabels.pipe)){
                validlist[ConfigPrmsLabel.phirange[0]] = 1;
                validlist[ConfigPrmsLabel.phimesh[0]] = 1;
            }
        }
        if(isvoldens)
        {
            validlist[ConfigPrmsLabel.xrange[0]] = 1;
            validlist[ConfigPrmsLabel.xmesh[0]] = 1;
            validlist[ConfigPrmsLabel.yrange[0]] = 1;
            validlist[ConfigPrmsLabel.ymesh[0]] = 1;
            if(this.m_jsonobj[ConfigPrmsLabel.dstep[0]] 
                    != ArbPositionsLabel){
                validlist[ConfigPrmsLabel.drange[0]] = 1;
                validlist[ConfigPrmsLabel.dmesh[0]] = 1;   
            }
            validlist[ConfigPrmsLabel.Qgl[0]] = 1;
            validlist[ConfigPrmsLabel.Phiinc[0]] = 1;
            validlist[ConfigPrmsLabel.qslitapt[0]] = 1;
            validlist[ConfigPrmsLabel.illumarea[0]] = 0;
        }
    
        // K, harmonic
        if(isKdep){
            if(srccont.isbxy >= 0){
                validlist[ConfigPrmsLabel.krange[0]] = -1;
                validlist[ConfigPrmsLabel.ckrange[0]] = 1;
            }
            else{
                validlist[ConfigPrmsLabel.krange[0]] = 1;
                validlist[ConfigPrmsLabel.ckrange[0]] = -1;
            }
            validlist[ConfigPrmsLabel.e1strange[0]] = 0;
            if(!isallharm){
                validlist[ConfigPrmsLabel.kmesh[0]] = 1;
            }
            if(calcid.includes(MenuLabels.tgtharm)){
                validlist[ConfigPrmsLabel.hrange[0]] = 1;
            }
        }
        if(iswigner && isallharm){
            if(srccont.isbxy >= 0){
                validlist[ConfigPrmsLabel.krange[0]] = -1;
                validlist[ConfigPrmsLabel.ckrange[0]] = 1;
            }
            else{
                validlist[ConfigPrmsLabel.krange[0]] = 1;
                validlist[ConfigPrmsLabel.ckrange[0]] = -1;
            }
        }
        let isharmfix = srccont.isund >= 0 
            && (calcid.includes(MenuLabels.pdensr) 
            || (isfixedp && issimple)
            || issrcpoint 
            || ((iswigner || isCMD || isCMDPP) && !calcid.includes(MenuLabels.Kvalue)));
        if(isharmfix){
            validlist[ConfigPrmsLabel.hfix[0]] = 1;
        }
        if(isallharm){
            validlist[ConfigPrmsLabel.hmax[0]] = 1;
        }
    
        // temporal
        if(istime){
            validlist[ConfigPrmsLabel.trange[0]] = 1;
            validlist[ConfigPrmsLabel.tmesh[0]] = 1;
        }
    
        // Wigner
        if(iswigner || isCMD){
            let index = 1;
            let calcidw = calcid;
            if(isCMD){
                index = 0;
                calcidw = this.m_jsonobj[OrgTypeLabel];
            }
            if(calcidw.includes(MenuLabels.XXpslice)){
                validlist[ConfigPrmsLabel.Yfix[0]] = index;
                validlist[ConfigPrmsLabel.Ypfix[0]] = index;
            }
            else if(calcidw.includes(MenuLabels.YYpslice)){
                validlist[ConfigPrmsLabel.Xfix[0]] = index;
                validlist[ConfigPrmsLabel.Xpfix[0]] = index;
            }
            if(calcidw.includes(MenuLabels.XXpslice) 
                    || calcidw.includes(MenuLabels.XXpprj)){
                validlist[ConfigPrmsLabel.Xrange[0]] = index;
                validlist[ConfigPrmsLabel.Xprange[0]] = index;
                validlist[ConfigPrmsLabel.Xmesh[0]] = index;
                validlist[ConfigPrmsLabel.Xpmesh[0]] = index;
            }
            else if(calcidw.includes(MenuLabels.YYpslice) 
                    || calcidw.includes(MenuLabels.YYpprj)){
                validlist[ConfigPrmsLabel.Yrange[0]] = index;
                validlist[ConfigPrmsLabel.Yprange[0]] = index;
                validlist[ConfigPrmsLabel.Ymesh[0]] = index;
                validlist[ConfigPrmsLabel.Ypmesh[0]] = index;
            }
            else if(calcidw.includes(MenuLabels.XXpYYp) || 
                    calcidw.includes(MenuLabels.Wrel)){
                validlist[ConfigPrmsLabel.Xrange[0]] = index;
                validlist[ConfigPrmsLabel.Xmesh[0]] = index;
                validlist[ConfigPrmsLabel.Xprange[0]] = index;
                validlist[ConfigPrmsLabel.Xpmesh[0]] = index;
                validlist[ConfigPrmsLabel.Yrange[0]] = index;
                validlist[ConfigPrmsLabel.Ymesh[0]] = index;
                validlist[ConfigPrmsLabel.Yprange[0]] = index;
                validlist[ConfigPrmsLabel.Ypmesh[0]] = index;
            }
            else if(calcidw.includes(MenuLabels.Wslice)
                     || isedep || isKdep){
                validlist[ConfigPrmsLabel.Xfix[0]] = index;
                validlist[ConfigPrmsLabel.Xpfix[0]] = index;
                validlist[ConfigPrmsLabel.Yfix[0]] = index;
                validlist[ConfigPrmsLabel.Ypfix[0]] = index;
            }
            else if(calcidw.includes(MenuLabels.WprjX)){
                validlist[ConfigPrmsLabel.Xfix[0]] = index;
                validlist[ConfigPrmsLabel.Xpfix[0]] = index;
            }
            else if(calcidw.includes(MenuLabels.WprjY)){
                validlist[ConfigPrmsLabel.Yfix[0]] = index;
                validlist[ConfigPrmsLabel.Ypfix[0]] = index;
            }
        }
        if(issrcpoint){
            validlist[ConfigPrmsLabel.Xrange[0]] = 1;
            validlist[ConfigPrmsLabel.Xmesh[0]] = 1;
            validlist[ConfigPrmsLabel.Yrange[0]] = 1;
            validlist[ConfigPrmsLabel.Ymesh[0]] = 1;
        }
        if(trangeidx == -1){
            validlist[ConfigPrmsLabel.Xrange[0]] = -1;
            validlist[ConfigPrmsLabel.Xmesh[0]] = -1;
            validlist[ConfigPrmsLabel.Xprange[0]] = -1;
            validlist[ConfigPrmsLabel.Xpmesh[0]] = -1;
            validlist[ConfigPrmsLabel.Yrange[0]] = -1;
            validlist[ConfigPrmsLabel.Ymesh[0]] = -1;
            validlist[ConfigPrmsLabel.Yprange[0]] = -1;
            validlist[ConfigPrmsLabel.Ypmesh[0]] = -1;
            validlist[ConfigPrmsLabel.Xrange[0]] = -1;
            validlist[ConfigPrmsLabel.Xmesh[0]] = -1;
            validlist[ConfigPrmsLabel.Yrange[0]] = -1;
            validlist[ConfigPrmsLabel.Ymesh[0]] = -1;
        }
    
        // aperture limit for comp. amp.
        if(iswigner || issrcpoint){
            if(iscustomsrc || srcobj[TypeLabel] == FIELDMAP3D_Label){
                validlist[ConfigPrmsLabel.gtacc[0]] = 1;
            }
            if(isbm || iswiggler){
                validlist[ConfigPrmsLabel.horizacc[0]] = 1;
            }    
        }
    
        // horizontal aperture for GABrill & total flux (BM)
        if(isbm && 
            (calcid.includes(MenuLabels.fdensa) ||
            istf || issimple))
        {
            validlist[ConfigPrmsLabel.horizacc[0]] = 1;
        }
    
        // size, divergence
        let ispower = calcid.includes(MenuLabels.pdensa) 
                    || calcid.includes(MenuLabels.pdenss)
                    || calcid.includes(MenuLabels.ppower);
        if(isshow.size){
            validlist[ConfigPrmsLabel.psize[0]] = ispower ? 0 : -1;
            validlist[ConfigPrmsLabel.fsize[0]] = ispower ? -1 : 0;
        }
        if(isshow.div){
            validlist[ConfigPrmsLabel.pdiv[0]] = ispower ? 0 : -1;
            validlist[ConfigPrmsLabel.fdiv[0]] = ispower ? -1 : 0;
        }
        if(srccont.isund < 0 && srccont.iswiggler < 0){
            validlist[ConfigPrmsLabel.psize[0]] = -1;
            validlist[ConfigPrmsLabel.fsize[0]] = -1;
            validlist[ConfigPrmsLabel.pdiv[0]] = -1;
            validlist[ConfigPrmsLabel.fdiv[0]] = -1;
        }
    
        //--- options ---
        // filtering    
        if(iswigner || isCMD || isCMDPP || issimple || iscoh){
            validlist[ConfigPrmsLabel.filter[0]] = -1;
        }
        else if(isedep || isvoldens){
            validlist[ConfigPrmsLabel.filter[0]] = 1;
        }
        else if(calcid.includes(MenuLabels.pdensr)){
            validlist[ConfigPrmsLabel.filter[0]] = -1;
        }
        else if(calcid.includes(MenuLabels.pdensa)
            || calcid.includes(MenuLabels.pdenss)
            || calcid.includes(MenuLabels.ppower))
        {
            if(srcobj[TypeLabel] == FIELDMAP3D_Label){
                validlist[ConfigPrmsLabel.filter[0]] = -1;
            }
            else if(srccont.isund >= 0 && 
                srcobj[SrcPrmsLabel.segment_type[1]] != NoneLabel &&
                srcobj[SrcPrmsLabel.perlattice[1]])
            {
                validlist[ConfigPrmsLabel.filter[0]] = -1;
            }
            else if(srcobj[TypeLabel] == WIGGLER_Label 
                || srcobj[TypeLabel] == EMPW_Label)
            {
                validlist[ConfigPrmsLabel.filter[0]] 
                    = calcid.includes(MenuLabels.far) ? 1 : -1;
            }
            else{
                validlist[ConfigPrmsLabel.filter[0]] = 1;
            }     
        }
        if(validlist[ConfigPrmsLabel.filter[0]] == 1){
            let ftype = this.m_jsonobj[ConfigPrmsLabel.filter[0]];
            if(ftype == GenFilterLabel){            
                validlist[ConfigPrmsLabel.fmateri[0]] = 1;
            }
            else if(ftype == BPFGaussianLabel || ftype == BPFBoxCarLabel){
                validlist[ConfigPrmsLabel.bpfcenter[0]] = 1;
                validlist[ConfigPrmsLabel.bpfwidth[0]] = 
                    this.m_jsonobj[ConfigPrmsLabel.filter[0]] == BPFBoxCarLabel ? 1 : -1;
                validlist[ConfigPrmsLabel.bpfsigma[0]] = 
                    this.m_jsonobj[ConfigPrmsLabel.filter[0]] == BPFGaussianLabel ? 1 : -1;        
            }
            else if(ftype == CustomLabel){
                validlist[ConfigPrmsLabel.fcustom[0]] = 1;        
            }
        }
        if(isvoldens){
            validlist[ConfigPrmsLabel.amateri[0]] = 1;
        }
        let isfilter = validlist[ConfigPrmsLabel.filter[0]] == 1
            && this.m_jsonobj[ConfigPrmsLabel.filter[0]] != NoneLabel;
    
        // energy step
        if(isallharm || (isedep && (iswigapprox || isbmlike))){
            validlist[ConfigPrmsLabel.estep[0]] = 1;
        }
    
        // aperture, powerlimit
        if(aptopt){
            validlist[ConfigPrmsLabel.aperture[0]] = 1;
            validlist[ConfigPrmsLabel.powlimit[0]] = 
                isnorm && calcid.includes(MenuLabels.fluxpeak) ? 1 : -1;
        }
    
        // depth step
        validlist[ConfigPrmsLabel.dstep[0]] 
            = calcid.includes(MenuLabels.vpdens) ? 1 : -1;
    
        // depth step data
        validlist[ConfigPrmsLabel.depthdata[0]] 
            = calcid.includes(MenuLabels.vpdens) && 
            this.m_jsonobj[ConfigPrmsLabel.dstep[0]] == ArbPositionsLabel ? 1 : -1;
    
        // energy representation
        validlist[ConfigPrmsLabel.normenergy[0]] = normenergy ? 1 : -1;
    
        // defobs
        if(calcid.includes(MenuLabels.temporal)){
            validlist[ConfigPrmsLabel.defobs[0]] 
                = this.m_jsonobj[ConfigPrmsLabel.fouriep[0]] == -1 ? 1 : -1;
        }
        else if(calcid.includes(MenuLabels.srcpoint)
            || calcid.includes(MenuLabels.wigner)
            || calcid.includes(MenuLabels.spdens)
            || calcid.includes(MenuLabels.vpdens)
            || isCMDPP
        )
        {
            validlist[ConfigPrmsLabel.defobs[0]] = -1;
        }
        else if(isKdep){
            validlist[ConfigPrmsLabel.defobs[0]] 
                = calcid.includes(MenuLabels.pflux) 
                    || calcid.includes(MenuLabels.ppower) ? 1 : -1;
        }
        else if(istf || issimple)
        {
            validlist[ConfigPrmsLabel.defobs[0]] 
                = srcobj[TypeLabel] == BM_Label ? 1 : -1;
        }
        else{
            validlist[ConfigPrmsLabel.defobs[0]] = 1;
        }
    
        // optDx, xsmooth
        if(iswigner && isbmlike){
            let snglbm = isbm && !srcobj[SrcPrmsLabel.bmtandem[0]];
            validlist[ConfigPrmsLabel.optDx[0]] = snglbm ? 1 : -1;
            validlist[ConfigPrmsLabel.xsmooth[0]] = !isbm || snglbm ? 1 : -1;
        }
    
        // Fourier plane
        validlist[ConfigPrmsLabel.fouriep[0]] 
            = calcid.includes(MenuLabels.temporal) ? 1 : -1;
    
        let ispowsimple = !isvoldens && !isfilter && (
                calcid.includes(MenuLabels.ppower) ||
                calcid.includes(MenuLabels.pdenss) ||
                calcid.includes(MenuLabels.spdens)
            );
    
        // Wiggler approximation
        validlist[ConfigPrmsLabel.wiggapprox[0]] = 
            (isedep && srccont.isund >= 0 
                && calcid.includes(MenuLabels.far)) ||
            (srcobj[TypeLabel] == CUSTOM_Label && !ispowsimple
                && calcid.includes(MenuLabels.near)) ? 1 : -1;
        
        // Energy smoothing
        validlist[ConfigPrmsLabel.esmooth[0]] = 
            !calcid.includes(MenuLabels.far) &&
            validlist[ConfigPrmsLabel.wiggapprox[0]] == 1 ? 1 : -1;
        if(validlist[ConfigPrmsLabel.wiggapprox[0]] == 1){
            if(this.m_jsonobj[ConfigPrmsLabel.esmooth[0]]){
                validlist[ConfigPrmsLabel.wiggapprox[0]] = -1;
                validlist[ConfigPrmsLabel.esmooth[0]] = 1;
            }
            if(this.m_jsonobj[ConfigPrmsLabel.wiggapprox[0]] == 1){
                validlist[ConfigPrmsLabel.wiggapprox[0]] = 1;
                validlist[ConfigPrmsLabel.esmooth[0]] = -1;
            }
        }
        validlist[ConfigPrmsLabel.smoothwin[0]] = 
            validlist[ConfigPrmsLabel.esmooth[0]] &&
            this.m_jsonobj[ConfigPrmsLabel.esmooth[0]] ? 1 : -1;
    
        // accuracy
        validlist[ConfigPrmsLabel.acclevel[0]] = -1;
        validlist[ConfigPrmsLabel.accuracy[0]] = !isCMDPP ? 1 : -1;
    
        // CMD
        let cmdenable = 
            calcid.includes(MenuLabels.XXpprj) ||
            calcid.includes(MenuLabels.YYpprj) ||
            calcid.includes(MenuLabels.XXpYYp);
        let cmdon = this.m_jsonobj[ConfigPrmsLabel.CMD[0]];
    
        let showgs = false;
        if(!isCMD && !isCMDPP){
            showgs = cmdenable && cmdon;
            let cmdeidx = showgs ? 1 : -1;
            validlist[ConfigPrmsLabel.CMD[0]] = cmdenable ? 1 : -1;
            validlist[ConfigPrmsLabel.CMDfld[0]] = cmdeidx;
            validlist[ConfigPrmsLabel.CMDint[0]] = cmdeidx;
            validlist[ConfigPrmsLabel.CMDcmp[0]] = cmdeidx;
            validlist[ConfigPrmsLabel.CMDcmpint[0]] = cmdeidx;
        }
        else{
            validlist[ConfigPrmsLabel.CMD[0]] = -1;
            validlist[ConfigPrmsLabel.CMDfld[0]] = 1;
            validlist[ConfigPrmsLabel.CMDint[0]] = 1;
            validlist[ConfigPrmsLabel.CMDcmp[0]] = isCMDPP?-1:1;
            validlist[ConfigPrmsLabel.CMDcmpint[0]] = isCMDPP?-1:1;
            showgs = !isCMDPP;
        }
        if(validlist[ConfigPrmsLabel.CMDfld[0]] == 1){
            validlist[ConfigPrmsLabel.maxmode[0]] = 1;
            validlist[ConfigPrmsLabel.fcutoff[0]] = 1;
            validlist[ConfigPrmsLabel.cutoff[0]] = 1;
            let isexport = this.m_jsonobj[ConfigPrmsLabel.CMDfld[0]] != NoneLabel ||
                    this.m_jsonobj[ConfigPrmsLabel.CMDint[0]] ? 1 : -1;
            let idorg;
            if(isCMD || isCMDPP){
                idorg = this.m_jsonobj[OrgTypeLabel];
            }
            else{
                idorg = calcid;
            }
            if(idorg.includes(MenuLabels.XXpprj)){
                validlist[ConfigPrmsLabel.HGorderx[0]] = isCMDPP?-1:1;
                validlist[ConfigPrmsLabel.maxHGorderx[0]] = isCMDPP?0:-1;
                validlist[ConfigPrmsLabel.fieldgridx[0]] = isexport;
                validlist[ConfigPrmsLabel.fieldrangex[0]] = isexport;
            }
            else if(idorg.includes(MenuLabels.YYpprj)){
                validlist[ConfigPrmsLabel.HGordery[0]] = isCMDPP?-1:1;
                validlist[ConfigPrmsLabel.maxHGordery[0]] = isCMDPP?0:-1;
                validlist[ConfigPrmsLabel.fieldgridy[0]] = isexport;
                validlist[ConfigPrmsLabel.fieldrangey[0]] = isexport;
            }
            else if(idorg.includes(MenuLabels.XXpYYp)){
                validlist[ConfigPrmsLabel.HGorderxy[0]] = isCMDPP?-1:1;
                validlist[ConfigPrmsLabel.maxHGorderxy[0]] = isCMDPP?0:-1;
                validlist[ConfigPrmsLabel.fieldgridxy[0]] = isexport;
                validlist[ConfigPrmsLabel.fieldrangexy[0]] = isexport;
            }        
    
            if(showgs){
                if(idorg.includes(MenuLabels.XXpYYp)){
                    validlist[ConfigPrmsLabel.GSModelXY[0]] = 1;
                }
                else{
                    validlist[ConfigPrmsLabel.GSModel[0]] = 1;
                }    
            }
        }
        
        // FEL
        let accobj = this.m_acc.JSONObj;
        let felopt = this.m_jsonobj[ConfigPrmsLabel.fel[0]];

        validlist[ConfigPrmsLabel.fel[0]] 
            = iscoh && (srccont.isund >= 0 || iscustomsrc) && 
            accobj[AccPrmsLabel.bunchtype[0]] != CustomParticle ? 1 : -1;
        
        validlist[ConfigPrmsLabel.seedspec[0]] = 
            validlist[ConfigPrmsLabel.fel[0]] == 1 && 
            felopt == FELSeedCustomLabel ? 1 : -1;
        validlist[ConfigPrmsLabel.exportInt[0]] = 
            validlist[ConfigPrmsLabel.fel[0]] == 1 && 
            felopt != NoneLabel && felopt != FELReuseLabel ? 1 : -1;
        validlist[ConfigPrmsLabel.R56Bunch[0]] = validlist[ConfigPrmsLabel.exportInt[0]];
        validlist[ConfigPrmsLabel.exportEt[0]] = 
            (this.m_jsonobj[ConfigPrmsLabel.R56Bunch[0]] || this.m_jsonobj[ConfigPrmsLabel.exportInt[0]]) &&
            validlist[ConfigPrmsLabel.exportInt[0]] == 1 ? 1 : -1;

        if(validlist[ConfigPrmsLabel.fel[0]] == 1 && felopt != NoneLabel)
        {
            let isfelsec = false;
            if(srcobj[TypeLabel] == CUSTOM_Label){
                if(srcobj.hasOwnProperty(SrcPrmsLabel.fvsz[0])){
                    if(srcobj[SrcPrmsLabel.fvsz[0]].hasOwnProperty(FELSecIdxLabel)){
                        if(Array.isArray(srcobj[SrcPrmsLabel.fvsz[0]][FELSecIdxLabel])){
                            isfelsec = srcobj[SrcPrmsLabel.fvsz[0]][FELSecIdxLabel].length > 0;
                        }
                    }
                }        
            }
        
            if(felopt == FELSeedLabel || felopt == FELCPSeedLabel || felopt == FELSeedCustomLabel){
                validlist[ConfigPrmsLabel.pulseE[0]] = 1;
                if(felopt != FELSeedCustomLabel){
                    validlist[ConfigPrmsLabel.wavelen[0]] = 1;
                    if(felopt == FELSeedLabel){
                        validlist[ConfigPrmsLabel.pulselen[0]] = 1;
                    }
                    else{
                        validlist[ConfigPrmsLabel.tlpulselen[0]] = 1;
                    }    
                }
                validlist[ConfigPrmsLabel.srcsize[0]] = 1;
                validlist[ConfigPrmsLabel.waistpos[0]] = 1;
                validlist[ConfigPrmsLabel.timing[0]] = 1;
                if(felopt == FELCPSeedLabel || felopt == FELSeedCustomLabel){
                    validlist[ConfigPrmsLabel.gdd[0]] = 1;
                    validlist[ConfigPrmsLabel.tod[0]] = 1;
                }
            }
            else if(felopt == FELDblSeedLabel){
                validlist[ConfigPrmsLabel.pulseE_d[0]] = 1;
                validlist[ConfigPrmsLabel.wavelen_d[0]] = 1;
                validlist[ConfigPrmsLabel.tlpulselen_d[0]] = 1;
                validlist[ConfigPrmsLabel.srcsize_d[0]] = 1;
                validlist[ConfigPrmsLabel.waistpos_d[0]] = 1;
                validlist[ConfigPrmsLabel.timing_d[0]] = 1;
                validlist[ConfigPrmsLabel.gdd_d[0]] = 1;
                validlist[ConfigPrmsLabel.tod_d[0]] = 1;
            }
            if(felopt != FELReuseLabel){
                validlist[ConfigPrmsLabel.particles[0]] = 1;
                validlist[ConfigPrmsLabel.edevstep[0]] =
                    (this.m_jsonobj[ConfigPrmsLabel.exportEt[0]] && (
                        this.m_jsonobj[ConfigPrmsLabel.R56Bunch[0]] || 
                        this.m_jsonobj[ConfigPrmsLabel.exportInt[0]] )
                    ) ? 1 : -1;
                validlist[ConfigPrmsLabel.R56[0]] =
                    this.m_jsonobj[ConfigPrmsLabel.R56Bunch[0]] ? 1 : -1;    
            }
            validlist[ConfigPrmsLabel.eproi[0]] = 1;
            validlist[ConfigPrmsLabel.svstep[0]] = isfelsec ? -1 : 1;
            validlist[ConfigPrmsLabel.radstep[0]] = 1;
        }
        return validlist;
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        if(validlist != null){
            this.SetPanelBase(validlist, this.m_disables);
        }
    }

    SetDisabledItems(mainid){
        if(mainid.includes(MenuLabels.bunch)){
            this.m_disables = [
                ConfigPrmsLabel.eproi[0], 
                ConfigPrmsLabel.svstep[0], 
                ConfigPrmsLabel.radstep[0], 
                ConfigPrmsLabel.fel[0]
            ];
        }
        else if(mainid.includes(MenuLabels.wignerCMD) || mainid.includes(MenuLabels.CMDr)){
            this.m_disables = [
                ConfigPrmsLabel.autot[0],
                ConfigPrmsLabel.detune[0],
                ConfigPrmsLabel.efix[0],
                ConfigPrmsLabel.hfix[0]
            ];
        }
        else if(mainid.includes(MenuLabels.propagate)){
            this.m_disables = [
                ConfigPrmsLabel.detune[0],
                ConfigPrmsLabel.efix[0],
                ConfigPrmsLabel.hfix[0]
            ];
        }
        else{
            this.m_disables = [];
        }
    }

    GetCalcID(){
        if(this.m_jsonobj.hasOwnProperty(TypeLabel)){
            return this.m_jsonobj[TypeLabel];
        }
        return "";
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
    GetShowList()
    {
        return this.GetValidList();
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

class OutFileOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(OutputOptionsOrder, OutputOptionsLabel, optionlabel);

        let ugridlists = {};
        ugridlists[OutputOptionsLabel.fixpdata[0]] = {
            coltypes:[
                {[GridColLabel]:"Item", [GridTypeLabel]:"text"},
                {[GridColLabel]:"Value", [GridTypeLabel]:"text"},
                {[GridColLabel]:"Unit", [GridTypeLabel]:"text"}
            ],
            withnum:-1,
            readonly: true
        };

        super(OutFileLabel, optionlabel, null, ugridlists);
        this.m_config = null;
        this.SetPanel();
    }

    SetPanel()
    {
        let validlist = this.GetShowList();
        this.SetPanelBase(validlist);
        if(this.m_runbuttons.hasOwnProperty(OutputOptionsLabel.fixpdata[2])){
            this.m_runbuttons[OutputOptionsLabel.fixpdata[2]].addEventListener("click", (e) => {
                let id = [MenuLabels.run, MenuLabels.start].join(IDSeparator)
                MenuCommand(id)
            });
        }
    }

    SetObjects(config)
    {
        this.m_config = config;
    }    

    GetShowList()
    {
        let isfixed = false;
        if(this.m_config != null && this.m_config.JSONObj.hasOwnProperty(TypeLabel)){
            isfixed = this.m_config.JSONObj[TypeLabel].includes(FixedPointLabel);
        }
        let validlist = this.GetValidList();
        validlist[OutputOptionsLabel.fixpdata[0]] = isfixed ? 0 : -1;
        if(Framework == ServerLabel){
            validlist[OutputOptionsLabel.format[0]] = -1;
            validlist[OutputOptionsLabel.folder[0]] = -1;
        }
        return validlist;
    }

    ShowFixedPointResult(data)
    {
        let obj;
        try{
            obj = JSON.parse(data);
            let dataobj = obj[OutputLabel];
            let result = [
                dataobj[DataTitlesLabel],
                dataobj[DataLabel],
                dataobj[UnitsLabel]
            ];
            this.m_jsonobj[OutputOptionsLabel.fixpdata[0]] = result[0].map((col, i) => result.map(row => row[i]));
            this.SetPanel();
        }
        catch (e){
            Alert("Error: invalid format.\n"+e.message);
        }                    
    }
}

class MPIOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(MPIOptionsOrder, MPIOptionsLabel, optionlabel);
        super(MPILabel, optionlabel);
        this.SetPanel();
    }

    SetPanel()
    {
        let validlist = this.GetValidList(-1);
        validlist[MPIOptionsLabel.parascheme[0]] = 1;

        if(this.m_jsonobj[MPIOptionsLabel.parascheme[0]] == ParaMPILabel){
            validlist[MPIOptionsLabel.processes[0]] = 1;
        }
        else if(this.m_jsonobj[MPIOptionsLabel.parascheme[0]] == MultiThreadLabel){
            validlist[MPIOptionsLabel.threads[0]] = 1;
        }
        this.SetPanelBase(validlist);
    }
}

class DataUnitsOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(DataUnitOptionsOrder, DataUnitOptionsLabel, optionlabel);
        super(DataUnitLabel, optionlabel);
        this.SetPanel();
    }

    SetPanel()
    {
        let validlist = this.GetValidList();
        this.SetPanelBase(validlist);
    }
}

class AccuracyOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(AccuracyOptionsOrder, AccuracyOptionsLabel, optionlabel);

        let indents = [];
        let noindent = ["integlabel", "rangelabel", "otherslabel", SeparatorLabel];
        AccuracyOptionsOrder.forEach(key => {
            if(!noindent.includes(key)){
                indents.push(AccuracyOptionsLabel[key][0])
            }
        })
        super(AccuracyLabel, optionlabel, {}, {}, indents);
        this.m_acc = null;
        this.m_src = null;
        this.m_conf = null;
        this.SetPanel();
    }

    SetObjects(acc, src, conf){
        this.m_acc = acc;
        this.m_src = src;
        this.m_conf = conf;
    }

    SetPanel()
    {
        let validlist = this.GetValidList();
        if(this.m_acc == null || this.m_src == null || this.m_conf == null){
            this.SetPanelBase(validlist);
            return;            
        }
        let accobj = this.m_acc.JSONObj;
        let srcobj = this.m_src.JSONObj;
        let confobj = this.m_conf.JSONObj;
        let confvalid = this.m_conf.GetShowList();
        if(confvalid == null){
            confvalid = {}; 
            confvalid[ConfigPrmsLabel.fel[0]] = false;
            confvalid[ConfigPrmsLabel.wiggapprox[0]] = false;
        }

        let loadebm = accobj[AccPrmsLabel.bunchtype[0]] == CustomParticle;
        let is3dsrc = Is3DField(srcobj);
        let srccont = GetSrcContents(srcobj);
        let isfel = confvalid[ConfigPrmsLabel.fel[0]] >= 0
            && confobj[ConfigPrmsLabel.fel[0]] != NoneLabel;
        let calcid = confobj[TypeLabel];
        let iscoh = calcid.indexOf(MenuLabels.cohrad) >= 0;
        let isfar = calcid.indexOf(MenuLabels.far) >= 0;
        let srctype = srcobj[TypeLabel];
        let iswigapprox = confvalid[ConfigPrmsLabel.wiggapprox[0]] && 
            confobj[ConfigPrmsLabel.wiggapprox[0]];
       
        validlist[AccuracyOptionsLabel.accdisctra[0]] = 
            !isfar || srctype != CUSTOM_PERIODIC_Label || iswigapprox;
        validlist[AccuracyOptionsLabel.acclimtra[0]] = !isfar;
    
        validlist[AccuracyOptionsLabel.accineE[0]] = iscoh;
        validlist[AccuracyOptionsLabel.acclimeE[0]] = iscoh;

        validlist[AccuracyOptionsLabel.accconvMCcoh[0]] = iscoh && !isfel;
        validlist[AccuracyOptionsLabel.accconvMC[0]] = 
            (is3dsrc || loadebm) && !validlist[AccuracyOptionsLabel.accconvMCcoh[0]];
        validlist[AccuracyOptionsLabel.acclimMCpart[0]] = is3dsrc || loadebm || (iscoh && !isfel);
        validlist[AccuracyOptionsLabel.accMCpart[0]] = 
            validlist[AccuracyOptionsLabel.acclimMCpart[0]]
            && this.m_jsonobj[AccuracyOptionsLabel.acclimMCpart[0]];
        validlist[AccuracyOptionsLabel.accconvharm[0]] = isfar && srccont.ise1st >= 0;   
        validlist[AccuracyOptionsLabel.accEcorr[0]] = isfel;

        Object.keys(validlist).forEach(key => {
            if(typeof validlist[key] == "boolean"){
                validlist[key] = validlist[key] ? 1 : -1;
            }
        })            
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
                validlist[PlotOptionsLabel.xauto[0]] = -1;
                validlist[PlotOptionsLabel.yauto[0]] = -1;    
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
    constructor(isinteger, is2d, config){
        let optionlabel = [];
        GetObjectsOptionList(ScanConfigOrder, ScanConfigLabel, optionlabel);
        super(ScanLabel, optionlabel);
        this.m_isinteger = isinteger;
        this.m_is2d = is2d;
        this.m_config = config;
        this.SetPanel();
    }

    SetPanel()
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
        this.SetPanelBase(validlist);

        let config = this.m_config.JSONObj;
        let calcid = config[TypeLabel];
        let conflist = this.m_config.GetShowList();

        if(calcid.includes(FixedPointLabel)){
            this.m_jsonobj[ScanConfigLabel.bundle[0]] = true;
            this.DisableInput(ScanConfigLabel.bundle[0], true, true)
        }
        else{
            let killbundle = calcid.includes(MenuLabels.XXpYYp) 
            || calcid.includes(MenuLabels.CMD)
            || (conflist[ConfigPrmsLabel.CMD[0]] >= 0 && config[ConfigPrmsLabel.CMD[0]])
            || (conflist[ConfigPrmsLabel.fel[0]] >= 0 && config[ConfigPrmsLabel.fel[0]] != NoneLabel)
            if(killbundle){
                this.m_jsonobj[ScanConfigLabel.bundle[0]] = false;
                this.DisableInput(ScanConfigLabel.bundle[0], true, false)
            }
        }
    }
}

class PreProcessOptions extends PrmOptionList {
    constructor(){
        let optionlabel = [];
        GetObjectsOptionList(PreProcessPrmOrder, PreProcessPrmLabel, optionlabel);
        super(PrePLabel, optionlabel);
        this.SetPanel();
    }

    SetPanel(target)
    {
        let validlist = this.GetValidList(-1);
        if(target == PPPhaseErrLabel){
            validlist[PreProcessPrmLabel.thresh[0]] = 1;
            validlist[PreProcessPrmLabel.zcoord[0]] = 1;
        }
        else if(target == PPRedFlux){
            validlist[PreProcessPrmLabel.thresh[0]] = 1;
            validlist[PreProcessPrmLabel.maxharm[0]] = 1;
        }
        else if(target == PPTransLabel || target == PPAbsLabel){
            validlist[PreProcessPrmLabel.filtauto[0]] = 1;
            if(this.m_jsonobj[PreProcessPrmLabel.filtauto[0]] == CustomLabel){
                validlist[PreProcessPrmLabel.filtemin[0]] = 1;
                validlist[PreProcessPrmLabel.filtemax[0]] = 1;
                validlist[PreProcessPrmLabel.filtpoints[0]] = 1;
                validlist[PreProcessPrmLabel.filtscale[0]] = 1;    
            }            
        }
        this.SetPanelBase(validlist);
    }
}

class SimulationProcess {
    constructor(issingle, spobj, dataname, serno, parentid, postproc){
        this.m_id = GetIDFromItem(CalculationIDLabel, serno);
        this.m_serno = serno;
        this.m_postproc = postproc;
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
            item.value = dataname;
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
        let isfixed = 
            spobj[ConfigLabel][TypeLabel].includes(FixedPointLabel) 
        && !spobj.hasOwnProperty(ScanLabel);
        return {dataname: this.m_datanames[index], isfixed: isfixed};
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
                PyQue.Put(command);        
            }
            this.m_currindex++;
            return;
        }

        if(!nompi){
            if(GUIConf.GUIpanels[MPILabel].JSONObj[MPIOptionsLabel.parascheme[0]] == ParaMPILabel){
                comtype = "solver";
                args.unshift("./spectra_solver");
                args.unshift(GUIConf.GUIpanels[MPILabel].JSONObj[MPIOptionsLabel.processes[0]].toString());
                args.unshift("-n");
            }    
            if(GUIConf.GUIpanels[MPILabel].JSONObj[MPIOptionsLabel.parascheme[0]] == MultiThreadLabel){
                args.push("-t");
                args.push(GUIConf.GUIpanels[MPILabel].JSONObj[MPIOptionsLabel.threads[0]].toString());
            }    
        }

        let isfixed;
        if(currspobj.hasOwnProperty(InputLabel)){
            isfixed = currspobj[InputLabel][ConfigLabel][TypeLabel].includes(FixedPointLabel) 
                && !currspobj[InputLabel].hasOwnProperty(ScanLabel);
        }
        else{
            isfixed = currspobj[ConfigLabel][TypeLabel].includes(FixedPointLabel) 
                && !currspobj.hasOwnProperty(ScanLabel);
        }

        // <EMSCRIPTEN>
        if(Framework == ServerLabel){
            let prms = JSON.stringify(currspobj, null, JSONIndent);
            this.m_worker = new Worker("launch_solver.js");
            this.m_worker.addEventListener("message", (msgobj) => {
                if(msgobj.data == "ready"){
                    let threads = 1;
                    if(GUIConf.GUIpanels[MPILabel].JSONObj[MPIOptionsLabel.parascheme[0]] == MultiThreadLabel){
                        threads = GUIConf.GUIpanels[MPILabel].JSONObj[MPIOptionsLabel.threads[0]];
                    }    
                    this.m_worker.postMessage({data: prms, nthread: threads, serno: this.m_serno});    
                }
                else if(msgobj.data.data == null){
                    this.FinishSingle("");
                    if(msgobj.data.dataname != ""){
                        Alert(msgobj.data.dataname);
                    }
                }
                else if(msgobj.data.dataname != ""){
                    if(isfixed){
                        GUIConf.GUIpanels[OutFileLabel].ShowFixedPointResult(msgobj.data.data);
                    }
                    else{
                        this.m_postproc.LoadOutputFile(msgobj.data.data, msgobj.data.dataname, true)
                    }
                }
                else{
                    this.HandleStatus(msgobj.data.data);
                }
            });
            this.m_currindex++;
            return;
        }
        // </EMSCRIPTEN>

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
                    window.__TAURI__.tauri.invoke("read_file", {path: this.m_datanames[this.m_currindex-1]})
                    .then((data) => {
                        if(isfixed){
                            GUIConf.GUIpanels[OutFileLabel].ShowFixedPointResult(data);
                        }
                        else{
                            this.m_postproc.LoadOutputFile(data, this.m_datanames[this.m_currindex-1], true);
                        }
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

    async Cancel(){
        if(this.m_issingle){
            await this.KillCurrent();
            this.FinishSingle();
            return;
        }
        let index = this.m_list.selectedIndex;
        if(this.m_running){
            if(index >= this.m_currindex){
                this.RemoveProcess(index);
            }
            else{
                await this.KillCurrent();
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

// GUI to edit filter material
class EditFilterMaterial {
    constructor(id, builtin){      
        this.m_id = id;
        this.m_table = document.createElement("table");
        this.m_table.className = "grid";
        this.m_builtinobjs = builtin;
        this.m_materials = [];
    }

    get Custom(){
        return this.m_materials;
    };

    GetTable(custom)
    {
        this.m_table.innerHTML = "";
        this.m_materials = custom;

        this.m_elements = 0;
        for(let el in this.m_builtinobjs){
            this.m_elements = Math.max(this.m_elements, this.m_builtinobjs[el].comp.length);
        }
        for(let el in this.m_materials){
            this.m_elements = Math.max(this.m_elements, this.m_materials[el].comp.length);
        }

        let cell;
        for(let k = 0; k < 2; k++){
            let titlerow = this.m_table.insertRow(-1);
            if(k == 0){
                cell = titlerow.insertCell(-1);
                cell.setAttribute("rowspan","2");
                cell.innerHTML = "Name";
                cell.className = "title";
                cell = titlerow.insertCell(-1);
                cell.setAttribute("rowspan","2");
                cell.innerHTML = "Density (g/cm<sup>3</sup>)";
                cell.className = "title";    
            }
            for(let i = 0; i < this.m_elements; i++){
                cell = titlerow.insertCell(-1);
                cell.className = "title";
                if(k == 0){
                    cell.setAttribute("colspan","2");
                    cell.innerHTML = "Element"+(i+1).toString();
                }
                else{
                    cell.innerHTML = "Z";
                    cell = titlerow.insertCell(-1);
                    cell.innerHTML = "Ratio";
                    cell.className = "title";
                }
            }    
        }

        let filters = [this.m_builtinobjs, this.m_materials];
        for(let k = 0; k < filters.length; k++){
            let keys = Object.keys(filters[k]);
            if(k == 0){
                this.m_builtins = keys.length;
            }
            for(let n = 0; n < keys.length; n++){
                this.AddMaterial(keys[n], filters[k][keys[n]], k == 0);
            }
        }
        for(let n = 0; n < AdditionalRows; n++){
            this.AddMaterial("", "", false);
        }
        this.AddElement();        
        return this.m_table;
    }

    AddMaterial(matname, matobj, isreadonly){
        let cell, item, val;
        let row = this.m_table.insertRow(-1);
        for(let j = -2; j < this.m_elements*2; j++){
            cell = row.insertCell(-1);
            if(matname == "" || j >= matobj.comp.length*2){
                val = "";
            }
            else if(j == -2){
                val = matname;
            }
            else if(j == -1){
                val = matobj.dens;
            }
            else if(j%2 ==0){
                val = matobj.comp[j/2][0];
            }
            else{
                val = matobj.comp[(j-1)/2][1];
            }
            if(isreadonly){
                cell.innerHTML = val;
                cell.className = "rdonly";    
            }
            else{
                item = document.createElement("input");
                item.setAttribute("type", "text");
                item.setAttribute("value", val);
                item.addEventListener("change", (e) => {this.Modify(e);} );
                item.id = GetIdFromCell(this.m_id, this.m_table.rows.length-3, j);
                cell.appendChild(item);    
            }
        }        

    }

    AddElement(){
        this.m_elements++;
        let rows = this.m_table.rows;
        let cell, item;

        cell = rows[0].insertCell(-1);
        cell.setAttribute("colspan","2");
        cell.innerHTML = "Element"+this.m_elements.toString(); cell.className = "title";

        cell = rows[1].insertCell(-1);
        cell.innerHTML = "Z"; cell.className = "title";
        cell = rows[1].insertCell(-1);
        cell.innerHTML = "Ratio"; cell.className = "title";

        for(let n = 2; n < rows.length; n++){
            for(let j = 0; j < 2; j++){
                cell = rows[n].insertCell(-1);
                if(n < this.m_builtins+2){
                    cell.innerHTML = "";
                    cell.className = "rdonly";        
                }
                else{
                    item = document.createElement("input");
                    item.setAttribute("type", "text");
                    item.setAttribute("value", "");
                    item.addEventListener("change", (e) => {this.Modify(e);} );
                    let cellidx = 2*(this.m_elements-1)+j;
                    item.id = GetIdFromCell(this.m_id, n-2, cellidx);
                    cell.appendChild(item);    
                }
            }
        }
    }

    Modify(event){
        let cell = GetCellFromId(this.m_id, event.currentTarget.id);
        let naddrow = cell[0]+AdditionalRows-(this.m_table.rows.length-3);
        for(let n = 0; n < naddrow; n++){
            this.AddMaterial("", "");
        }
        if(cell[1] >= 2*(this.m_elements-1)){
            this.AddElement();
        }
        let name = document.getElementById(GetIdFromCell(this.m_id, cell[0], -2));
        let dens = document.getElementById(GetIdFromCell(this.m_id, cell[0], -1));
        let conts = [];
        for(let n = 0; n < this.m_elements; n++){
            let znum = parseInt(document.getElementById(GetIdFromCell(this.m_id, cell[0], 2*n)).value);
            let ratio = parseFloat(document.getElementById(GetIdFromCell(this.m_id, cell[0], 2*n+1)).value);
            if(!isNaN(znum) && !isNaN(ratio)){
                conts.push([znum, ratio]);
            }
        }
        if(cell[1] == -2){
            let oldname = event.currentTarget.defaultValue;
            if(this.m_materials.hasOwnProperty(oldname)){
                delete this.m_materials[oldname];
            }
            name.setAttribute("value", name.value);
        }
        let ndens = parseFloat(dens.value);
        if(!isNaN(ndens) && conts.length > 0){
            this.m_materials[name.value] = {dens:ndens, comp:conts};
        }
    }

    GetMaterialNames(){
        let bnames = Object.keys(this.m_builtinobjs);
        let mnames = Object.keys(this.m_materials);
        return bnames.concat(mnames);
    }
}

class EditListTable {
    constructor(settings){
        let oprbtn = document.querySelectorAll(`[id$="prmedit"]`);
        oprbtn.forEach(btn => {
            btn.addEventListener("click", e => {
                this.Operate(e.currentTarget.id);
            })
        })

        let sortdiv = document.getElementById("sortarea");
        let sortsel = document.createElement("select");
        sortsel.className = "mt-1 mb-1";

        let sortitle = document.createElement("div");
        sortitle.innerHTML =  "Sorting"
        sortsel.className = "m-1";

        let sortschema = ["None", "A &rarr; Z", "Z &rarr; A"];
        this.m_settings = settings;
        if(!this.m_settings.hasOwnProperty("sorting")){
            this.m_settings.sorting = 0;
        }
        this.m_settings.sorting = Math.max(0, Math.min(this.m_settings.sorting, sortschema.length-1));
        SetSelectMenus(sortsel, sortschema, [], sortschema[this.m_settings.sorting]);
        sortsel.addEventListener("change", (e) => {
            this.m_settings.sorting = sortschema.indexOf(e.currentTarget.value);
            this.SetAll();
        })

        sortdiv.appendChild(sortitle);
        sortdiv.appendChild(sortsel);
    }

    Show(spectraobjs){
        this.m_currcateg = null;
        this.m_list = {};
        this.m_object = CopyJSON(spectraobjs);
        this.m_maxsize = 12;

        let blid = "editbl";
        let parent = document.getElementById(blid);
        let blcurr = this.m_object[CurrentLabel];
        
        this.CreateList(BLLabel, parent, blcurr, this.m_object[BLLabel], 1);
        
        let categids  = ["editacc", "editsrc", "editconf"];
        for(let j = 0; j < MainCategories.length; j++){
            let categ = MainCategories[j];
            parent = document.getElementById(categids[j]);
            this.CreateList(categ, parent, 
                this.m_object[BLLabel][blcurr][categ], this.m_object[categ], this.m_maxsize);
        }
        document.getElementById(GetIDFromItem("edit", BLLabel)).click();
    }

    GetObject()
    {
        return this.m_object;
    }

    WriteStatus(label){
        document.getElementById("prmstatus").innerHTML = label;
    }

    CreateList(categ, parent, curr, objects, maxitems){
        parent.innerHTML = "";
        this.m_list[categ] = document.createElement("select");
        this.m_list[categ].id = GetIDFromItem("edit", categ);
        this.m_list[categ].className = "w-100";
        this.m_list[categ].setAttribute("multiple", "multiple");
        let prmsets = Object.keys(objects)
        SetSelectMenus(this.m_list[categ], prmsets, [], curr, true, null, maxitems);
        parent.appendChild(this.m_list[categ]);
        ["click", "change"].forEach(evtype => {
            this.m_list[categ].addEventListener(evtype, e => {
                let categ = GetItemFromID(e.currentTarget.id).item;
                let items = GetSelections(this.m_list[categ]);
                this.m_currcateg = categ;
                this.EnableSingle(items.index.length == 1);
                if(items.index.length > 1){
                    document.getElementById("editname").value = "";
                }
                else{
                    document.getElementById("editname").value = e.currentTarget.value;
                    if(categ == BLLabel){
                        this.ShowBL();
                    }
                    else{
                        this.m_object[BLLabel][this.m_object[CurrentLabel]][categ] = e.currentTarget.value
                    }
                }
                this.WriteStatus(this.m_currcateg+" Selected: "+items.value.join(","));
            });    
        })
    }

    EnableSingle(enable){
        let ids = ["ren-prmedit", "dupl-prmedit"];
        ids.forEach(id => {
            if(enable){
                document.getElementById(id).removeAttribute("disabled");
            }
            else{
                document.getElementById(id).setAttribute("disabled", "disabled");
            }
        })
    }

    ShowBL()
    {
        let items = GetSelections(this.m_list[BLLabel]);
        if(items.index.length > 1){
            return;
        }
        this.m_object[CurrentLabel] = items.value[0];
        this.SetAll();
    }

    SetAll()
    {
        let blcurr = this.GetValidItemName(BLLabel, this.m_object[CurrentLabel]);
        this.m_object[CurrentLabel] = blcurr;

        let prmsets = Object.keys(this.m_object[BLLabel]);
        if(this.m_settings.sorting == 1){
            prmsets.sort((a, b) => a > b ? 1 : -1);
        }
        else if(this.m_settings.sorting == 2){
            prmsets.sort((a, b) => a > b ? -1 : 1);
        }
        SetSelectMenus(this.m_list[BLLabel], prmsets, [], blcurr, true, null, this.m_maxsize);

        MainCategories.forEach(categ => {
            let curr = this.GetValidItemName(categ, this.m_object[BLLabel][blcurr][categ]);
            this.m_object[BLLabel][blcurr][categ] = curr;
            prmsets = Object.keys(this.m_object[categ]);
            if(this.m_settings.sorting == 1){
                prmsets.sort((a, b) => a > b ? 1 : -1);
            }
            else if(this.m_settings.sorting == 2){
                prmsets.sort((a, b) => a > b ? -1 : 1);
            }
            SetSelectMenus(this.m_list[categ], prmsets, [], curr, true, null, this.m_maxsize);
        });
    }

    GetValidItemName(categ, name){
        if(this.m_object[categ].hasOwnProperty(name)){
            return name;
        }
        return Object.keys(this.m_object[categ])[0];
    }

    Operate(id){
        if(this.m_currcateg == null){
            return;
        }
        let obj = this.m_object[this.m_currcateg];
        if(id.includes("del")){
            let items = GetSelections(this.m_list[this.m_currcateg]).value;
            if(items.length == Object.keys(obj).length){
                this.WriteStatus("At least one item should be left.");
                return;
            }
            items.forEach(item => {
                if(obj.hasOwnProperty(item)){
                    delete obj[item];
                }
            });
            this.m_currcateg = null; // to stop multiple deleting operations
        }
        else{
            let currname = this.GetSelectedName(this.m_currcateg);
            let blname = this.GetSelectedName(BLLabel);
            if(currname == null || blname == null){                
                return;
            }
            let newname = document.getElementById("editname").value;
            if(Object.keys(obj).includes(newname)){
                this.WriteStatus("\""+newname+"\" already exisits. Input another name.");
                return;
            }
            if(id.includes("ren")){
                let buff = obj[currname];
                delete obj[currname];
                obj[newname] = buff;
            }
            else if(id.includes("dupl")){
                obj[newname] = CopyJSON(obj[currname]);
            }
            if(this.m_currcateg == BLLabel){
                this.m_object[CurrentLabel] = newname;
            }
            else{
                this.m_object[BLLabel][blname][this.m_currcateg] = newname;
            }
        }
        this.SetAll();
    }

    GetSelectedName(categ){
        let items = GetSelections(this.m_list[categ]).value;
        if(items.length == 0){
            return null;
        }
        return items[0];
    }
}

// funnctions specific to SPECTRA
// operation after parameter change
function UpdateOptions(tgtid)
{
    let item = GetItemFromID(tgtid);
    if(item.categ == PartPlotConfLabel){
        UpdateParticlePlot();
    }
    else if(item.categ == PartConfLabel){
        AnalyzeParticle();
    }
    else if(item.categ == PrePLabel){
        GUIConf.GUIpanels[PrePLabel].SetPanel(GetPPItem());
        UpdatePPPlot();
    }
    else if(item.categ != POLabel){
        GUIConf.Updater.Update(tgtid);
        SetDisableCalcIDs();
        if(GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel] == ""){
            OpenConfigPanel();
        }
    }
}

function Is3DField(srcobj)
{
    let srctype = srcobj[TypeLabel];
    switch(srctype){
        case WLEN_SHIFTER_Label:
        case BM_Label:
        case WIGGLER_Label:
        case EMPW_Label:
            return false;
        case FIELDMAP3D_Label:
            return true;
        case CUSTOM_Label:
            return srcobj[SrcPrmsLabel.natfocus[0]] != NoneLabel;
    }
    if(srcobj[SrcPrmsLabel.segment_type[0]] != NoneLabel){
        if(srcobj[SrcPrmsLabel.perlattice[0]]){
            return true;
        }
    }
    if(srcobj[SrcPrmsLabel.natfocus[0]] != NoneLabel){
        return true;
    }
    return false;
}

function GetSrcContents(srcobj)
{
    let srctype = srcobj[TypeLabel];
    let isgap, isgaplink, isbxy, isb, islu, isper, isapple, isKxy, isK;
    let ise1st, isund, iswiggler;

    isgap = ise1st = 3; // scan possible, but not an input parameter
    islu = isb = isK = 1;
    isund = isper = 0;
    isbxy = isapple = isKxy = iswiggler = -1;
    switch(srctype){
        case BM_Label:
        case WLEN_SHIFTER_Label:
        case CUSTOM_Label:
        case FIELDMAP3D_Label:
            isgap = islu = isK = ise1st = isund = isper = -1;
            break;
        case LIN_UND_Label:
        case VERTICAL_UND_Label:
        case HELICAL_UND_Label:
            isb  = 2;
            break;
        case ELLIPTIC_UND_Label:
        case FIGURE8_UND_Label:
        case VFIGURE8_UND_Label:
            isbxy = 2;
            isKxy = 1;
            isb = isK = -1;
            break;
        case MULTI_HARM_UND_Label:
            isgap = isb = isK = -1;
            isKxy = 1;
            break;
        case EMPW_Label:
            isb = isK = ise1st = isund = -1;
            isbxy = isKxy = 1;
            iswiggler = 0;
            break;
        case WIGGLER_Label:
            ise1st = isund = -1;
            iswiggler = 0;
            break;
        case CUSTOM_PERIODIC_Label:
            isgap = isb = isK = -1;
            islu = isKxy = ise1st = 0;
            break;
    }
    if(srcobj[SrcPrmsLabel.apple[0]] 
            && srctype == ELLIPTIC_UND_Label)
    {
        isbxy = isKxy = 0;
        isapple = 1;
    }
    isgaplink = isgap;
    if(srcobj[SrcPrmsLabel.gaplink[0]] == NoneLabel){
        isgap = -1;
    }

    let srccont = {
        isgap:isgap, isgaplink:isgaplink, isbxy:isbxy, isb:isb, islu:islu, isper:isper, 
        isapple:isapple, isKxy:isKxy, isK:isK, ise1st:ise1st, isund:isund, iswiggler:iswiggler
    };
    return srccont;
}


