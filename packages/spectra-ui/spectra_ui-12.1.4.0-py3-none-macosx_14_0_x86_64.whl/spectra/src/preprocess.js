"use strict";

function GetPreprocID(label)
{
    return [MenuLabels.preproc, MenuLabels[label]].join(IDSeparator);
}

function UpdateSliceParameters(trangesfs)
{
    let ndata = GUIConf.part_obj.data[0].length;
    let slicelen = trangesfs[2]/GUIConf.GUIpanels[PartConfLabel].JSONObj[ParticleConfigLabel.bins[0]];
    let nsrange = [Math.floor(trangesfs[0]/slicelen+0.5), Math.floor(trangesfs[1]/slicelen+0.5)];
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
        GUIConf.slice_prms[1][ns] = slice_particles[ns]*charge/(slicelen*1e-15); // current
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
//
//
//
//    
}

function ArrangePPPanel()
{
    let ppitem = GetPPItem();
    let pids = {[PPPartAnaLabel]:"preproc-part"};
    if(ppitem != null && pids.hasOwnProperty(ppitem)){
        document.getElementById(pids[ppitem]).classList.replace("d-none", "d-flex");
        delete pids[ppitem];
    }
    Object.keys(pids).forEach((el) => {
        document.getElementById(pids[el]).classList.replace("d-flex", "d-none");
    });

/*




*/

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
        let accobj = GUIConf.GUIpanels[AccLabel].JSONObj;
        if(accobj.hasOwnProperty(AccPrmsLabel.bunchdata[0])){
            partfile = accobj[AccPrmsLabel.bunchdata[0]];
            if(partfile == ""){
                partfile = "Not Selected";
            }
        }
//        
        document.getElementById("partdataname").innerHTML = partfile;
    }
    if(ppitem == PPPartAnaLabel){
        select.setAttribute("size", "1");
        document.getElementById(GUIConf.guids[PrePLabel]).classList.add("d-none");
        document.getElementById("expbtn").classList.add("d-none");
        UpdateParticlePlot();
    }
    else{
        ExpandSelectMenu(select);    
        UpdatePPPlot();
    }

    if(Object.keys(pids).length == 1 && GUIConf.GUIpanels[PrePLabel].Hidden()){
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
    obj = CopyJSON(GUIConf.GUIpanels[categ].JSONObj[label]);
    dimension = GUIConf.ascii[ascii].GetDimension();
    titles = items;
    if(dimension == 2){
        axtitles = Array.from(items);
    }
    else{
        axtitles = [items[0], GUIConf.ascii[ascii].GetOrdinate()];
        if(dimension == 0){
            let ndata = obj.data[0].length;
            axtitles[0] = "Index";
            titles.unshift(axtitles[0]);
            obj.titles.unshift(axtitles[0]);
            obj.data.unshift(new Array(ndata));
            for(let n = 0; n < ndata; n++){
                obj.data[0][n] = n;
            }
            dimension = 1;
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

    let ppitem = GetPPItem(), items;
    if(ppitem == null){
        GUIConf.GUIpanels[PrePLabel].SetPanel();
        GUIConf.plotly = null;
        document.getElementById("expbtn").classList.add("d-none");        
        document.getElementById("preproc-plot").innerHTML = "";
        return;
    }

    let categ = "", label, ascii;
    document.getElementById(GUIConf.guids[PrePLabel]).classList.remove("d-none");
    if(ppitem == CustomCurrent){
        categ = AccLabel;
        label = AccPrmsLabel.currdata[0];
        ascii = CustomCurrent;
        items = [TimeLabel, BeamCurrLabel];
    }
    else if(ppitem == CustomEt){
        categ = AccLabel;
        label = AccPrmsLabel.Etdata[0];
        ascii = CustomEt;
        items = [TimeLabel, EdevLabel, NormCurrLabel];
    }
    else if(ppitem == CustomField){
        categ = SrcLabel;
        label = SrcPrmsLabel.fvsz[0];
        ascii = CustomField;
        items = [ZLabel, BxLabel, ByLabel];
    }
    else if(ppitem == CustomPeriod){
        categ = SrcLabel;
        label = SrcPrmsLabel.fvsz1per[0];
        ascii = CustomPeriod;
        items = [ZLabel, BxLabel, ByLabel];
    }
    else if(ppitem == ImportGapField){
        categ = SrcLabel;
        label = SrcPrmsLabel.gaptbl[0];
        ascii = ImportGapField;
        items = [GapLabel, BxLabel, ByLabel];
    }
    else if(ppitem == CustomFilter){
        categ = ConfigLabel;
        label = ConfigPrmsLabel.fcustom[0];
        ascii = CustomFilter;
        items = [EnergyLabel, TransmLabel];
    }
    else if(ppitem == CustomDepth){
        categ = ConfigLabel;
        label = ConfigPrmsLabel.depthdata[0];
        ascii = CustomDepth;
        items = [DepthLabel];
    }
    if(categ != ""){ // import data
        GUIConf.import = {category:categ, prmlabel:label, ascii:ascii};
        ShowImportButtons(true);
        GUIConf.GUIpanels[PrePLabel].SetPanel();
        if(IsEmptyObj(categ, label)){
            CreateUploadArea(GetPreprocID("import"));
            return;
        }
        UpdatePlot(categ, ascii, label, items);
    }
    else{ // do preprocess and plot
        if(ppitem == ""){
            return;
        }
        GUIConf.GUIpanels[PrePLabel].SetPanel(ppitem);
        DrawPPPlot(ppitem);
    }
}

function SetPreprocessPlot()
{
    let ppplotlabel = [];
    let ppobjs = {};
    ppobjs[AccLabel] = [PPBetaLabel];
 
    let bunch = GUIConf.GUIpanels[AccLabel].JSONObj[AccPrmsLabel.bunchtype[0]];
    if(bunch == CustomCurrent){
        ppobjs[AccLabel].push(CustomCurrent);
    }
    else if(bunch == CustomEt){
        ppobjs[AccLabel].push(CustomEt);
    }
    else if(bunch == CustomParticle){
        ppobjs[AccLabel].push(PPPartAnaLabel);
    }
    if(ppobjs.hasOwnProperty(AccLabel)){
        ppplotlabel.push(ppobjs);
    }

    ppobjs = {};
    let srclist = GUIConf.GUIpanels[SrcLabel].GetShowList();
    if(GUIConf.GUIpanels[SrcLabel].JSONObj[TypeLabel] == CUSTOM_Label){
        ppobjs[SrcLabel] = [CustomField, PP1stIntLabel, PP2ndIntLabel];
    }
    else if(GUIConf.GUIpanels[SrcLabel].JSONObj[TypeLabel] == CUSTOM_PERIODIC_Label){
        ppobjs[SrcLabel] = [CustomPeriod, PPFDlabel, PP1stIntLabel, PP2ndIntLabel];
    }
    else{
        ppobjs[SrcLabel] = [PPFDlabel, PP1stIntLabel, PP2ndIntLabel]
    }

    if(GUIConf.GUIpanels[SrcLabel].JSONObj[TypeLabel] == CUSTOM_Label ||
        GUIConf.GUIpanels[SrcLabel].JSONObj[SrcPrmsLabel.phaseerr[0]] ||
        GUIConf.GUIpanels[SrcLabel].JSONObj[SrcPrmsLabel.fielderr[0]])
    {
        ppobjs[SrcLabel].push(PPPhaseErrLabel);
        ppobjs[SrcLabel].push(PPRedFlux);
    }
    if(srclist[SrcPrmsLabel.gaplink[0]] == 1 &&
        GUIConf.GUIpanels[SrcLabel].JSONObj[SrcPrmsLabel.gaplink[0]] == ImpGapTableLabel)
    {
        ppobjs[SrcLabel].push(ImportGapField);
    }
    ppplotlabel.push(ppobjs);

    let confobj = GUIConf.GUIpanels[ConfigLabel].JSONObj;
    if(confobj[TypeLabel] != ""){
        let validlist = GUIConf.GUIpanels[ConfigLabel].GetShowList();

        ppobjs = {[PPFilters]: []};
        if(validlist[ConfigPrmsLabel.filter[0]] >= 0 
            && confobj[ConfigPrmsLabel.filter[0]] != NoneLabel)
        {
            if(confobj[ConfigPrmsLabel.filter[0]] == CustomLabel){
                ppobjs[PPFilters].push(CustomFilter);
            }
            else{
                ppobjs[PPFilters].push(PPTransLabel);
            }
        }
        if(confobj[TypeLabel].includes(MenuLabels.vpdens)){
            ppobjs[PPFilters].push(PPAbsLabel);
            if(validlist[ConfigPrmsLabel.depthdata[0]] >= 0){
                ppobjs[PPFilters].push(CustomDepth);
            }
        }
        if(ppobjs[PPFilters].length > 0){
            ppplotlabel.push(ppobjs);
        }
    }

    let former = GetPPItem();
    let select = document.getElementById("preproc-select");
    select.innerHTML = "";
    SetSelectMenus(select, ppplotlabel, [], former, true);
    ArrangePPPanel();
    EnableCutomFieldItems();
}

// pre-processing via solver
async function DrawPPPlot(ppitem = null)
{
    let obj = GetPPObject(ppitem);
    if(obj == null){
        return;
    }

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
            if(!result.hasOwnProperty(ppitem)){
                Alert("No pre-processing results found.");
                return;    
            }
            DrawPreprocObj(ppitem, result[ppitem]);
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

// plot the pre-processed data
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

    //----->>>>>
    if(obj.hasOwnProperty(RelateDataLabel)){
        let items = Object.keys(obj[RelateDataLabel]);
        let text = [];
        for(const item of items){
            if(item != ElapsedTimeLabel){
                text.push(item+": "+obj[RelateDataLabel][item]);
            }
        }
        let textopr = {
            xref: 'paper',
            yref: 'paper',
            x: 0.95,
            xanchor: 'right',
            y: 0.95,
            yanchor: 'top',
            text: text.join("<br>"),
            showarrow: false        
        };
        GUIConf.plotly.RefreshPlotObject([], {text: textopr});
    }
    document.getElementById("expbtn").classList.remove("d-none");
}

function EnableCutomFieldItems()
{
    let fidx, labels;
    if(GUIConf.GUIpanels[SrcLabel].JSONObj[TypeLabel] == CUSTOM_Label){
        fidx = SrcPrmsLabel.fvsz[0];
        labels = [PP1stIntLabel, PP2ndIntLabel, PPPhaseErrLabel, PPRedFlux];
    }
    else if(GUIConf.GUIpanels[SrcLabel].JSONObj[TypeLabel] == CUSTOM_PERIODIC_Label){
        fidx = SrcPrmsLabel.fvsz1per[0];
        labels = [PPFDlabel, PP1stIntLabel, PP2ndIntLabel, PPPhaseErrLabel, PPRedFlux];
    }
    else{
        return;
    }
    let select = document.getElementById("preproc-select");
    EnableSelection(select, labels, !IsEmptyObj(SrcLabel, fidx));
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

        let idxs = SliceTitles.indexOf(TimeLabel);
        let idxI = SliceTitles.indexOf(InstCurrentLabel);
        let idxemitt = [SliceTitles.indexOf(EmittxLabel), SliceTitles.indexOf(EmittyLabel)];
        let idxbeta = [SliceTitles.indexOf(BetaxLabel), SliceTitles.indexOf(BetayLabel)];
        let idxalpha = [SliceTitles.indexOf(AlphaxLabel), SliceTitles.indexOf(AlphayLabel)];
        let idxp = [SliceTitles.indexOf(XavLabel), SliceTitles.indexOf(YavLabel)];
        let idxa = [SliceTitles.indexOf(XpavLabel), SliceTitles.indexOf(YpavLabel)];
        let idxE = SliceTitles.indexOf(EnergyLabel);
        let idxEsp = SliceTitles.indexOf(EspLabel);
        let item = GUIConf.GUIpanels[PartPlotConfLabel].JSONObj[PDPLotConfigLabel.item[0]];

        titles = [TimeLabel];
        axtitles = [TimeLabel, item];
        let data = [GUIConf.slice_prms[idxs]];
        if(item == CurrentProfileTitle){
            titles.push(InstCurrentLabel);
            axtitles[1] = InstCurrentLabel;
            data.push(GUIConf.slice_prms[idxI]);
        }
        else if(item == EdevspLabel){
            titles.push(EdevLabel);
            titles.push(EspLabel);
            let edev = Array.from(GUIConf.slice_prms[idxE]);
            for(let n = 0; n < edev.length; n++){
                if(GUIConf.slice_prms[idxI][n] > 0){
                    edev[n] = edev[n]/GUIConf.GUIpanels[AccLabel].JSONObj[AccPrmsLabel.eGeV[0]]-1;
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
        obj = {titles: titles, data: data};
    }
    else{
        let partconf = GUIConf.GUIpanels[PartPlotConfLabel].JSONObj;
        let xaxis = partconf[PDPLotConfigLabel.xaxis[0]];
        let yaxis = partconf[PDPLotConfigLabel.yaxis[0]];
        let plots = partconf[PDPLotConfigLabel.plotparts[0]];
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
        return;
    }

    let partconf = GUIConf.GUIpanels[PartConfLabel].JSONObj;
    let cols = [
        partconf[ParticleConfigLabel.colx[0]],
        partconf[ParticleConfigLabel.colxp[0]],
        partconf[ParticleConfigLabel.coly[0]],
        partconf[ParticleConfigLabel.colyp[0]],
        partconf[ParticleConfigLabel.colt[0]],
        partconf[ParticleConfigLabel.colE[0]]
    ];
    let xyunit =  partconf[ParticleConfigLabel.unitxy[0]] == UnitMeter ? 1 : 1e-3;
    let xypunit =  partconf[ParticleConfigLabel.unitxyp[0]] == UnitRad ? 1 : 1e-3;
    let tunit = 1, eunit = 1;
    switch(partconf[ParticleConfigLabel.unitt[0]]){
        case UnitpSec:
            tunit = 1000;
            break;
        case UnitSec:
            tunit = 1e15;
            break;
        case UnitMeter:
            tunit = 1e15/CC;
            break;
        case UnitMiliMeter:
            tunit = 1e12/CC;
            break;
    }
    if(partconf[ParticleConfigLabel.unitE[0]] == UnitMeV){
        eunit = 1e-3;
    }
    else if(partconf[ParticleConfigLabel.unitE[0]] == UnitGamma){
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
        return;
    }

    let slice_avg = new Array(6); slice_avg.fill(0);
    let slice_sq = new Array(6); slice_sq.fill(0);
    let slice_corr = new Array(2); slice_corr.fill(0);

    let tmin, tmax;
    for(let n = 0; n < ndata; n++){
        for(let j = 0; j < 6; j++){
            slice_avg[j] += GUIConf.part_obj.data[j][n];
            slice_sq[j] += GUIConf.part_obj.data[j][n]**2;
            if(j < 2){
                slice_corr[j] += GUIConf.part_obj.data[2*j][n]*GUIConf.part_obj.data[2*j+1][n];
            }
        }
        if(n == 0){
            tmin = GUIConf.part_obj.data[4][n];
            tmax = GUIConf.part_obj.data[4][n];
        }
        else{
            tmin = Math.min(tmin, GUIConf.part_obj.data[4][n]);
            tmax = Math.max(tmax, GUIConf.part_obj.data[4][n]);
        }
    }
    for(let j = 0; j < 6; j++){
        slice_avg[j] /= ndata;
        slice_sq[j] /= ndata;
        if(j < 2){
            slice_corr[j] /= ndata;
        }
    }
    let Eav = slice_avg[5]; // energy
    let Espr = Math.sqrt((slice_sq[5]-slice_avg[5]**2))/slice_avg[5]; // energy spread
    let tsigma = 1e-15*Math.sqrt((slice_sq[4]-slice_avg[4]**2)); // bunch length

    let trangesfs = [tmin, tmax, tsigma*1e15];
    UpdateSliceParameters(trangesfs);

    let emittxy = [null, null], sizexy = [null, null], divxy = [null, null];
    let betaxy = [null, null], alphaxy = [null, null];
    for(let j = 0; j < 2; j++){
        let size = slice_sq[2*j]-slice_avg[2*j]**2;
        let div = slice_sq[2*j+1]-slice_avg[2*j+1]**2;
        let corr = slice_corr[j]-slice_avg[2*j]*slice_avg[2*j+1];
        let emitt = size*div-corr**2;

        if(size > 0){
            sizexy[j] = Math.sqrt(size)*1000;
        }
        if(div > 0){
            divxy[j] = Math.sqrt(div)*1000;
        }
        if(emitt > 0){
            emittxy[j] = Math.sqrt(emitt);
            betaxy[j] = size/emittxy[j];
            alphaxy[j] = -corr/emittxy[j];
        }
        else{
            emittxy[j] = 0;
            betaxy[j] = 1;
            alphaxy[j] = 0;
        }
    }
    let accobj = GUIConf.GUIpanels[AccLabel].JSONObj;
    let charge = ndata*GUIConf.GUIpanels[PartConfLabel].JSONObj[ParticleConfigLabel.pcharge[0]];
    accobj[AccPrmsLabel.buf_eGeV[0]][1] = Eav;
    accobj[AccPrmsLabel.buf_espread[0]][1] = Espr;
    accobj[AccPrmsLabel.buf_bunchcharge[0]][1] = charge*1e9;
    accobj[AccPrmsLabel.buf_bunchlength[0]][1] = tsigma*CC*1000;
    accobj[AccPrmsLabel.emitt[0]] = emittxy[0]+emittxy[1];
    accobj[AccPrmsLabel.coupl[0]] = emittxy[1]/emittxy[0];
    accobj[AccPrmsLabel.beta[0]] = betaxy;
    accobj[AccPrmsLabel.alpha[0]] = alphaxy;
    accobj[AccPrmsLabel.eta[0]] = [0, 0];
    accobj[AccPrmsLabel.etap[0]] = [0, 0];
    accobj[AccPrmsLabel.peakcurr[0]] = charge/Math.sqrt(2.0*Math.PI)/tsigma;

    GUIConf.Updater.Update();
    UpdateParticlePlot();
    document.getElementById("preproc-part-plotconf-div").classList.remove("d-none");
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
            HandleFile(data, path);
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
    let accobj = GUIConf.GUIpanels[AccLabel].JSONObj;
    if(accobj.hasOwnProperty(AccPrmsLabel.bunchdata[0])){
        dataname = accobj[AccPrmsLabel.bunchdata[0]];
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
            let msg = "No path is specified for \""+AccPrmsLabel.bunchdata[0]+"\"";
            Alert(msg);
        }
        else{
            window.__TAURI__.tauri.invoke("read_file", {path: path})
            .then((data) => {
                HandleFile(data, path);
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

function IsEmptyObj(categ, label)
{
    let obj = GUIConf.GUIpanels[categ].JSONObj;
    if(!obj.hasOwnProperty(label)){
        return true;
    }
    else if(typeof obj[label] != "object"){
        return true;
    }
    else if(Object.keys(obj[label]).length == 0){
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
