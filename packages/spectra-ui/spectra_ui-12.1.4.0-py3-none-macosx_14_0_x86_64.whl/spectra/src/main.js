"use strict";

// globals
var Framework;
var RunOS;
var GUIConf = {currnewwin: null, procid: -1, disabled: [], mainid: ""};
var PlotObjects = {windows: new Queue(), objects: new Queue()};
var PyQue = new Queue();
var ScanTarget = {};
var Settings = {plotconfigs:{}, defpaths:{}, scanconfig:{}, sorting: 1};
var Observer = {};
var TWindow = {}; // tauri windows object
var BufferObject = null;

// generate calclulation objects and create processes
function GetSimulationObject(ppitem = null)
{
    let obj = {};
    let exports = Array.from(GUIConf.exports);
    if(GUIConf.mainid.includes(MenuLabels.loadf)){
        if(GUIConf.mainid.includes(MenuLabels.CMDr)){
            obj[CMDResultLabel] = GUIConf.loadedobjs[CMDResultLabel];
        }
        else if(GUIConf.mainid.includes(MenuLabels.bunch)){
            obj[FELBunchFactor] = GUIConf.loadedobjs[FELBunchFactor];
        }
        else{
            obj[OutputLabel] = GUIConf.loadedobjs[OutputLabel];
        }
        obj[InputLabel] = {};
        for(let j = 0; j < exports.length; j++){
            obj[InputLabel][exports[j]] = GUIConf.GUIpanels[exports[j]].ExportCurrent();
        }
        obj[InputLabel][ConfigLabel][TypeLabel] = GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel];
        obj[InputLabel][ConfigLabel][OrgTypeLabel] = GUIConf.GUIpanels[ConfigLabel].JSONObj[OrgTypeLabel];
        if(GUIConf.mainid.includes(MenuLabels.CMDr) || GUIConf.mainid.includes(MenuLabels.wignerCMD))
        {
            let prms = [];            
            if(obj[InputLabel][ConfigLabel][OrgTypeLabel].includes(MenuLabels.XXpprj)){
                prms = [ConfigPrmsLabel.Xrange[0], ConfigPrmsLabel.Xmesh[0]];
            }
            else if(obj[InputLabel][ConfigLabel][OrgTypeLabel].includes(MenuLabels.YYpprj)){
                prms = [ConfigPrmsLabel.Yrange[0], ConfigPrmsLabel.Ymesh[0]];
            }
            else{
                prms = [
                    ConfigPrmsLabel.Xrange[0], ConfigPrmsLabel.Xmesh[0],
                    ConfigPrmsLabel.Yrange[0], ConfigPrmsLabel.Ymesh[0]
                ];
            }
            for(const prm of prms){
                obj[InputLabel][ConfigLabel][prm] = GUIConf.loadedobjs[InputLabel][ConfigLabel][prm];
            }
        }
        Settings[ConfigLabel] = CopyJSON(obj[InputLabel][ConfigLabel]);
        return obj;
    }
    if(ppitem != null){
        exports.push(PrePLabel);
        if(GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel] == ""){
            let confidx = exports.indexOf(ConfigLabel);
            exports.splice(confidx, 1);
        }
    }
    for(let j = 0; j < exports.length; j++){
        obj[exports[j]] = GUIConf.GUIpanels[exports[j]].ExportCurrent();
    }
    if(!obj.hasOwnProperty(ConfigLabel)){
        obj[ConfigLabel] = {};
    }
    obj[ConfigLabel][TypeLabel] = GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel];

    if(obj[ConfigLabel].hasOwnProperty(ConfigOptionsLabel.fmateri[0]) || 
            obj[ConfigLabel].hasOwnProperty(ConfigOptionsLabel.amateri[0])){
        if(GUIConf.spectraobjs.hasOwnProperty(FMaterialLabel)){
            obj[FMaterialLabel] = CopyJSON(GUIConf.spectraobjs[FMaterialLabel]);
        }
    }

    if(obj[AccLabel][AccPrmsLabel.bunchtype[0]] == CustomParticle){
        obj[PartConfLabel] = GUIConf.GUIpanels[PartConfLabel].ExportCurrent();
    }
    if(obj[ConfigLabel][ConfigPrmsLabel.accuracy[0]] == CustomLabel){
        GUIConf.GUIpanels[AccuracyLabel].SetPanel();
        obj[ConfigLabel][AccuracyLabel] = GUIConf.GUIpanels[AccuracyLabel].ExportCurrent();
    }
    return obj;
}

// create main GUI
function MainGUI()
{
    let tabs = ["main", "preproc", "postproc"];
    tabs.forEach(tab => {
        let id = tab+"-tab";
        document.getElementById(id).innerHTML = MenuLabels[tab];
    })

    let menubar = document.getElementById("menubar");
    Menubar.forEach(menu => {
        let rootname = Object.keys(menu)[0];
        let menudiv = document.createElement("div");
        menudiv.id = rootname;
        menudiv.className = "dropdown";
        menubar.appendChild(menudiv);

        let menutitle = document.createElement("div");
        menutitle.setAttribute("data-bs-toggle", "dropdown");
        menutitle.className = "menu";
        menutitle.innerHTML = rootname;
        menudiv.appendChild(menutitle);

        let menucont = document.createElement("ul");
        menucont.className = "dropdown-menu";
        menucont.id = rootname+"-item";

        menudiv.appendChild(menucont);

        let menulist = SetMenuItems(menu[rootname], rootname);
        let runids = [];
        let menus = CreateMenuList(menulist, menucont, null, runids);
        if(rootname == MenuLabels.calc){
            GUIConf.allmenus = menus;
            GUIConf.runids = Array.from(runids);
        }
    });

    GUIConf.ascii = {};
    Object.keys(AsciiFormats).forEach(el => {
        GUIConf.ascii[el] = new AsciiData(AsciiFormats[el].dim, 
            AsciiFormats[el].items, AsciiFormats[el].titles, AsciiFormats[el].ordinate);
    });

    GUIConf.GUIpanels = {
        [AccLabel]: new AccPrmOptions(),
        [SrcLabel]: new SrcPrmOptions(),
        [ConfigLabel]: new ConfigPrmOptions(Object.keys(FilterMaterial)),
        [OutFileLabel]: new OutFileOptions(),
        [PartConfLabel]: new PartFormatOptions(),
        [PartPlotConfLabel]: new PDPlotOptions(),
        [PrePLabel]: new PreProcessOptions(),
        [DataUnitLabel]: new DataUnitsOptions(),
        [AccuracyLabel]: new AccuracyOptions(),
        [MPILabel]: new MPIOptions()
    };

    GUIConf.GUIpanels[AccLabel].SetObjects(
        GUIConf.GUIpanels[SrcLabel], GUIConf.GUIpanels[ConfigLabel]);
    GUIConf.GUIpanels[SrcLabel].SetObjects(
        GUIConf.GUIpanels[AccLabel], GUIConf.GUIpanels[ConfigLabel]);
    GUIConf.GUIpanels[ConfigLabel].SetObjects(
        GUIConf.GUIpanels[AccLabel], GUIConf.GUIpanels[SrcLabel]);
    GUIConf.GUIpanels[OutFileLabel].SetObjects(GUIConf.GUIpanels[ConfigLabel]);
    GUIConf.GUIpanels[AccuracyLabel].SetObjects(
        GUIConf.GUIpanels[AccLabel], GUIConf.GUIpanels[SrcLabel], GUIConf.GUIpanels[ConfigLabel]);
        
    GUIConf.GapFieldTable = new GapFieldTable(GUIConf.GUIpanels[SrcLabel]);
    GUIConf.Updater = new Updater(
        GUIConf.GUIpanels[AccLabel], GUIConf.GUIpanels[SrcLabel], 
        GUIConf.GUIpanels[ConfigLabel], GUIConf.GUIpanels[OutFileLabel], GUIConf.GapFieldTable);

    GUIConf.guids = {
        [AccLabel]: "acc-div",
        [SrcLabel]: "src-div",
        [ConfigLabel]: "config-div",
        [OutFileLabel]: "outfile-div",
        [PartConfLabel]: "preproc-part",
        [PartPlotConfLabel]: "preproc-part-plotconf",
        [PrePLabel]: "preproc-config"
    }
    GUIConf.exports = [
        AccLabel,
        SrcLabel,
        ConfigLabel,
        OutFileLabel
    ];

    GUIConf.plotly = null;
    GUIConf.simproc = [];
    GUIConf.subwindows = 0;
    
    let datatypes = Object.values(GUILabels.datatype);
    GUIConf.postprocessor = new PostProcessor("", 
        "postp-plot", datatypes, OutputLabel, "resultdata");
    GUIConf.postprocessor.EnableSubPanel(true);
    document.getElementById("postp-view-cont").appendChild(GUIConf.postprocessor.GetPanel());    

    // assign labels and ids to buttons for preprocessing
    let labels = ["units", "import", "load", "ascii", "duplicate"];
    labels.forEach(label => {
        let element = document.getElementById("preproc-"+label);
        element.innerHTML = MenuLabels[label];
        element.id = [MenuLabels.preproc, MenuLabels[label]].join(IDSeparator);
    });

    GUIConf.default = {};
    Object.keys(GUIConf.guids).forEach((el) => {
        if(GUIConf.guids[el] == "preproc-part"){
            document.getElementById("preproc-part-anadiv").prepend(GUIConf.GUIpanels[el].GetTable());
        }
        else{
            document.getElementById(GUIConf.guids[el]).prepend(GUIConf.GUIpanels[el].GetTable());
        }
    })

    // assign default settings
    Object.keys(MainPrmLabels).forEach(el => {
        if(InputPanels.includes(el)){
            GUIConf.default[el] = CopyJSON(GUIConf.GUIpanels[el].JSONObj);
        }
        if(SettingPanels.includes(el)){
            Settings[el] = GUIConf.GUIpanels[el].JSONObj;
        }
    })
    GUIConf.default[SrcLabel][TypeLabel] = LIN_UND_Label;
    GUIConf.default[VersionNumberLabel] = Version;

    GUIConf.spectraobjs = GetSPECTRAObjects(CopyJSON(GUIConf.default), DefaultObjName);
    GUIConf.filename = "";

    GUIConf.fmaterial = new EditFilterMaterial("modalDialogCont", FilterMaterial);
    GUIConf.editprms = new EditListTable(Settings);
    GUIConf.panelid = "main-tab";

    let plotoption = new PlotOptions();
    GUIConf.def_plot_configs = plotoption.JSONObj;

    GUIConf.plot_aspect = {
        ["preproc-plot"]: 0.75,
        ["postp-plot"]: 0.75
    };
}

// reset GUI components
function OnNewFile()
{
    let outfileobj = GUIConf.GUIpanels[OutFileLabel].JSONObj;
    if(outfileobj[OutputOptionsLabel.folder[0]] == "" && Framework == TauriLabel){
        outfileobj[OutputOptionsLabel.folder[0]] = GUIConf.wdname;
    }

    document.getElementById("preproc-part-anadiv").classList.add("d-none");
    document.getElementById("preproc-part-cont").innerHTML = "";
    document.getElementById("preproc-part-plotconf-div").classList.add("d-none");

    if(GUIConf.panelid != null){
        if(GUIConf.panelid == "preproc-tab"){
            SetPreprocessPlot();
        }
    }

    let ids = {
        [BLLabel]: [MenuLabels.prmset, MenuLabels.bl].join(IDSeparator),
        [AccLabel]: [MenuLabels.prmset, MenuLabels.acc].join(IDSeparator),
        [SrcLabel]: [MenuLabels.prmset, MenuLabels.src].join(IDSeparator),
        [ConfigLabel]: [MenuLabels.prmset, MenuLabels.config].join(IDSeparator),
    };
    Object.keys(ids).forEach(categ => {
        let names = Object.keys(GUIConf.spectraobjs[categ]);
        if(Settings.sorting == 1){
            names.sort((a, b) => a > b ? 1 : -1);
        }
        else if(Settings.sorting == 2){
            names.sort((a, b) => a > b ? -1 : 1);
        }
        let prmset = [];
        names.forEach(name => {
            prmset.push({label:name});
        })
        let prmlist = SetMenuItems(prmset, MenuLabels.prmset+IDSeparator+categ);
        let prmmenu  = document.getElementById(ids[categ]);
        prmmenu.innerHTML = "";
        let currprm;
        if(categ == BLLabel){
            currprm = GUIConf.spectraobjs[CurrentLabel];
        }
        else{
            currprm = GUIConf.spectraobjs[BLLabel][GUIConf.spectraobjs[CurrentLabel]][categ]
        }
        prmmenu.classList.add("prmmenu");
        CreateMenuList(prmlist, prmmenu, currprm);
    });
    SetSelectionPrmSet();
}

// callback for a menu command
async function MenuCommand(id)
{
    let options  = {
        title: "",
        filters: [{
            name: "JSON",
            extensions: ["json"]
          }]
    };
    if(Settings.defpaths.hasOwnProperty(id)){
        options.defaultPath = Settings.defpaths[id];
    }

    if(id.includes(MenuLabels.file)){
        SetMainID(id);
        if(id.includes(MenuLabels.new)){
            SetWindowTitle();
            GUIConf.spectraobjs = GetSPECTRAObjects(CopyJSON(GUIConf.default), DefaultObjName);
            GUIConf.filename = "";
            ParameterFileOpened();
            delete Settings.lastloaded;
            delete Settings.lastid;
            return;
        }
        if(id.includes(MenuLabels.postproc)){
            document.getElementById("postproc-tab").click();
            GUIConf.postprocessor.Import();
        }
        else if(id.includes(MenuLabels.open) || id.includes(MenuLabels.outpostp) 
                || id.includes(MenuLabels.loadf) || id.includes(MenuLabels.append)){
            GUIConf.fileid = id;
            if(Framework == TauriLabel){
                let title = "Open a SPECTRA parameter file.";
                if(id.includes(MenuLabels.outpostp)){
                    title = "Open post-processed data file."
                }
                else if(id.includes(MenuLabels.loadf)){
                    title = "Open SPECTRA output file."
                }
                let path = await GetPathDialog(title, id, true, true, true, false);
                if(path == null){
                    return;
                }
                if(!id.includes(MenuLabels.outpostp) && !id.includes(MenuLabels.append)){
                    Settings.lastloaded = path;
                    Settings.defpaths[[MenuLabels.file, MenuLabels.saveas].join(IDSeparator)] = path;
                    Settings.lastid = id;
                }
                SwitchSpinner(true);
                window.__TAURI__.tauri.invoke("read_file", {path: path})
                .then((data) => {
                    HandleFile(data, path);
                    SwitchSpinner(false);
                });
            }
            else if(Framework == BrowserLabel || Framework == ServerLabel){
                document.getElementById("file-main").setAttribute("accept", "application/json");
                document.getElementById("file-main").click();
                document.getElementById("file-main").removeAttribute("accept");
            }                
            else if(Framework == PythonGUILabel){
                PyQue.Put(id);
            }
        }
        else if(id.includes(MenuLabels.exit)){
            if(Framework == TauriLabel){
                BeforeExit().then((e) => {
                    window.__TAURI__.process.exit(0);
                });
            }
            else if(Framework == BrowserLabel || Framework == ServerLabel){
                window.open("","_self").close();
            }        
            else if(Framework == PythonGUILabel){
                PyQue.Put(id);
            }
        }
        else if(id.includes(MenuLabels.save) 
                || id.includes(MenuLabels.saveas) || id.includes(MenuLabels.saveas11)){
            let issaveas = id.includes(MenuLabels.saveas) || id.includes(MenuLabels.saveas11);
            let obj = GetObjectToSave(id);
            if(Framework == TauriLabel){
                let data = FormatArray(JSON.stringify(obj, null, JSONIndent));
                if(issaveas){
                    let path = await GetPathDialog(
                        "Input a data name to save the parameters.", id, false, true, true, false);
                    if(path == null){
                        return;
                    }
                    Settings.lastloaded = path;
                    Settings.lastid = [MenuLabels.file, MenuLabels.open].join(IDSeparator);
                    window.__TAURI__.tauri.invoke("write_file", { path: path, data: data});
                    SetWindowTitle(path);
                    ArrangeMenus();
                }
                else if(id.includes(MenuLabels.save) && GUIConf.filename != ""){
                    window.__TAURI__.tauri.invoke("write_file", { path: GUIConf.filename, data: data});
                }
            }
            else if(Framework == BrowserLabel || Framework == ServerLabel){
                ExportObjects(obj, GUIConf.filename)
            }
            else if(Framework == PythonGUILabel){
                PyQue.Put(id);
            }
        }
    }
    else if(id.includes(MenuLabels.calc)){ // select calculation type
        GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel] = 
            id.split(IDSeparator).slice(1).join(IDSeparator);
        EnableAllRunMenus(true); // reset all run menus
        OpenConfigPanel();
    }
    else if(id.includes(MenuLabels.run))
    {
        if(id.includes(MenuLabels.process) || 
                (id.includes(MenuLabels.start) && Framework != BrowserLabel)){
            RunCommand(id);
        }
        else if(Framework != PythonGUILabel){
            ExportCommand();
        }
        else{
            PyQue.Put(id);
        }
    }
    else if(id.includes(MenuLabels.prmset)){ // select parameter set
        if(id.includes(MenuLabels.editprm)){
            document.getElementById("showPrmset").click();
            GUIConf.editprms.Show(GUIConf.spectraobjs);    
        }
        else{
            let items = id.split(IDSeparator);
            if(items.length < 3){
                return;
            }            
            let calcid = GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel];
            AssignParameterSet({category: items[1], name: items[2]});
            if(GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel] == ""){
                if(!GUIConf.disabled.includes(calcid)){
                    GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel] = calcid;
                }    
            }
            SetSelectionPrmSet();
            OpenConfigPanel();
            if(GUIConf.panelid == "preproc-tab"){
                SetPreprocessPlot();
            }    
        }
    }
    else if(id.includes(MenuLabels.help)){
        if(id.includes(MenuLabels.about)){
            let contdiv = document.createElement("div");
            contdiv.innerHTML = "";
            contdiv.className = "d-flex flex-column align-items-stretch";
            let maintxt = document.createElement("p");
            maintxt.className = "dialogmsg m-0";
            maintxt.innerHTML = 
            "SPECTRA is a computer software to numerically evaluate the characteristics of synchrotron radiation. "
            +"SPECTRA is free for use, however, the author retains the copyright to SPECTRA."
            +"If you are submitting articles to scientific journals with the results obtained by using SPECTRA, "
            +"cite the reference below.";
            let papertxt = document.createElement("p");
            papertxt.className = "text-center dialogmsg m-0";
            papertxt.innerHTML = "J. Synchrotron Radiation 28, 1267 (2021)";
            let urltxt = document.createElement("p");
            urltxt.innerHTML = "https://spectrax.org/spectra/index.html<br>admin@spectrax.org";
            urltxt.className = "text-center dialogmsg m-0";
            contdiv.appendChild(maintxt);
            contdiv.appendChild(papertxt);
            contdiv.appendChild(document.createElement("hr"));
            contdiv.appendChild(urltxt);
            ShowDialog("About SPECTRA ("+Version+")", false, true, "", contdiv);
        }
        else if(id.includes(MenuLabels.reference)){
            if(Framework ==  TauriLabel){
                try {
                    let refpath;
                    if(RunOS == "Linux"){
                        refpath = "/usr/share/spectra/help/reference.html";
                        if(await window.__TAURI__.invoke("exists", {path: refpath}) == false){
                            refpath = "help"+window.__TAURI__.path.sep+"reference.html";
                        }
                    }
                    else{
                        refpath = "help"+window.__TAURI__.path.sep+"reference.html";
                    }
                    window.__TAURI__.shell.open(refpath);
                } catch (e) {
                    Alert(e);
                }        
            }
            else{
                window.open("help/reference.html");
            }
        }    
    }
    else if(id.includes(MenuLabels.edit)){
        if(id.includes(MenuLabels.material)){
            document.getElementById("modalMaterialCont").innerHTML = "";
            document.getElementById("modalMaterialCont").appendChild(
                    GUIConf.fmaterial.GetTable(CopyJSON(GUIConf.spectraobjs[FMaterialLabel])));
            document.getElementById("showMaterial").click();
        }
        else if(id.includes(MenuLabels.unit)){
            EditUnits();
        }
        else{
            let eid = id.split(IDSeparator);
            if(eid.length == 2){
                EditDialog(eid[1]);
            }
        }
    }
    else if(id == "scan-prm-item"){
        if(GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel] == ""){
            Alert("Select the calculation type first.")
            return;
        }
        let scanconfig = Settings.scanconfig;
        let jxy = ScanTarget.jxy;
        let is2d = jxy >= 0;
        let isint = ScanTarget.isinteger;
        let scanoption = new ScanOptions(ScanTarget.isinteger, is2d, GUIConf.GUIpanels[ConfigLabel]);
        if(!scanconfig.hasOwnProperty(ScanTarget.item)){
            let curra = GUIConf.GUIpanels[ScanTarget.category].JSONObj[ScanTarget.item];
            let curr;
            if(is2d){
                curr = curra[jxy];
            }
            else{
                curr = curra;
            }
            if(isint){
                scanconfig[ScanTarget.item] = {
                    [ScanConfigLabel.initiali[0]]: curr,
                    [ScanConfigLabel.finali[0]]: curr+1,
                    [ScanConfigLabel.interval[0]]: 1,
                    [ScanConfigLabel.iniserno[0]]: 1,
                }    
                if(is2d){
                    let tmpconf = scanconfig[ScanTarget.item];
                    tmpconf[ScanConfigLabel.scan2dtype[0]] = Scan2D1DLabel;
                    tmpconf[ScanConfigLabel.initiali2[0]] = curra;
                    tmpconf[ScanConfigLabel.finali2[0]] = [curra[0]+1,curra[1]+1];
                    tmpconf[ScanConfigLabel.interval2[0]] = [1,1];
                    tmpconf[ScanConfigLabel.iniserno2[0]] = [1,1];
                }
            }
            else{
                scanconfig[ScanTarget.item] = {
                    [ScanConfigLabel.initial[0]]: curr*0.8,
                    [ScanConfigLabel.final[0]]: curr*1.2,
                    [ScanConfigLabel.scanpoints[0]]: 11,
                    [ScanConfigLabel.iniserno[0]]: 1
                }    
                if(is2d){
                    let tmpconf = scanconfig[ScanTarget.item];
                    tmpconf[ScanConfigLabel.scan2dtype[0]] = Scan2D1DLabel;
                    tmpconf[ScanConfigLabel.initial2[0]] = [curra[0]*0.8,curra[1]*0.8];
                    tmpconf[ScanConfigLabel.final2[0]] = [curra[0]*1.2,curra[1]*1.2];
                    tmpconf[ScanConfigLabel.scanpoints2[0]] = [11,11];
                    tmpconf[ScanConfigLabel.iniserno2[0]] = [1,1];                    
                }
            }
        }
        else if(is2d){
            let tmpconf = scanconfig[ScanTarget.item];
            if(isint){
                tmpconf[ScanConfigLabel.initiali[0]] = tmpconf[ScanConfigLabel.initiali2[0]][jxy];
                tmpconf[ScanConfigLabel.finali[0]] = tmpconf[ScanConfigLabel.finali2[0]][jxy];
                tmpconf[ScanConfigLabel.interval[0]] = tmpconf[ScanConfigLabel.interval2[0]][jxy];
            }
            else{
                tmpconf[ScanConfigLabel.initial[0]] = tmpconf[ScanConfigLabel.initial2[0]][jxy];
                tmpconf[ScanConfigLabel.final[0]] = tmpconf[ScanConfigLabel.final2[0]][jxy];
                tmpconf[ScanConfigLabel.scanpoints[0]] = tmpconf[ScanConfigLabel.scanpoints2[0]][jxy];
            }
        }
        GUIConf.scanconfigold =  CopyJSON(scanconfig[ScanTarget.item]);
        scanoption.JSONObj = GUIConf.scanconfigold;
        let title = "Scan \""+ScanTarget.item+"\"";
        ShowDialog(title, true, false, "",  scanoption.GetTable(), CreateScan)
        scanoption.SetPanel();
    }
}

// set id for MainGUI
function SetMainID(id)
{
    let menus = [
        MenuLabels.new, MenuLabels.open, MenuLabels.wignerCMD, 
        MenuLabels.wignerProp, MenuLabels.CMDr, MenuLabels.bunch
    ];
    for(const menu of menus){
        if(id.includes(menu)){
            GUIConf.mainid = id;
        }
    }
}

// get parameter object to save
function GetObjectToSave(id)
{
    let obj = CopyJSON(GUIConf.spectraobjs);
    if(id.includes(MenuLabels.saveas11)){
        let converter = new ObjConverter();
        converter.Downconvert(obj);
    }
    return obj;
}

// open configuration panel
function OpenConfigPanel()
{
    let id = GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel];
    if(id == ""){
        document.getElementById("config-card").classList.add("d-none");
    }
    else{
        document.getElementById("config-card").classList.remove("d-none");
    }
    document.getElementById("calcid").innerHTML = "Calculation Type: "+id;
    GUIConf.Updater.Create();
    ArrangeRunMenu();

    if(GUIConf.mainid.includes(MenuLabels.wignerCMD)
        || GUIConf.mainid.includes(MenuLabels.wignerProp)
        || GUIConf.mainid.includes(MenuLabels.CMDr)
        || GUIConf.mainid.includes(MenuLabels.bunch))
    {
        GUIConf.GUIpanels[AccLabel].FreezePanel();
        GUIConf.GUIpanels[SrcLabel].FreezePanel();
    }
}

// enable/disable menu commands
function ArrangeMenus()
{
    let canrun = Framework != PythonScriptLabel
    let cansaveas = canrun && !GUIConf.mainid.includes(MenuLabels.loadf);
    let cansave = GUIConf.filename != "" && cansaveas;

    let items = [
        ["file", "save", cansave], 
        ["file", "saveas", cansaveas], 
        ["file", "saveas11", cansaveas], 
        ["file", "exit", canrun], 
        ["preproc", "ascii", canrun], 
        ["postproc", "ascii", canrun], 
        ["postproc", "save", canrun], 
        ["run", "export", canrun]
    ];

    items.forEach(item => {
        let id = [MenuLabels[item[0]], MenuLabels[item[1]]].join(IDSeparator);
        if(item[2]){
            document.getElementById(id).removeAttribute("disabled");
        }
        else{
            document.getElementById(id).setAttribute("disabled", true);
        }
    })
}

// arrange run-start command
function ArrangeRunMenu()
{
    let canstart = GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel] != ""
        && Framework != PythonScriptLabel;
    let id = [MenuLabels["run"], MenuLabels["start"]].join(IDSeparator);
    if(canstart){
        document.getElementById(id).removeAttribute("disabled");
    }
    else{
        document.getElementById(id).setAttribute("disabled", true);
    }
}

// enable/disable all run menus
function EnableAllRunMenus(enable)
{
    let ids = [
        [MenuLabels["run"], MenuLabels["process"]].join(IDSeparator),
        [MenuLabels["run"], MenuLabels["export"]].join(IDSeparator),
        [MenuLabels["run"], MenuLabels["start"]].join(IDSeparator),
    ];
    for(const id of ids){
        if(enable){
            document.getElementById(id).removeAttribute("disabled");
        }
        else{
            document.getElementById(id).setAttribute("disabled", true);
        }    
    }
}

// reload the parameter set after revision
function LoadRevisedPrmSet(isset)
{
    if(isset){
        GUIConf.spectraobjs = GUIConf.editprms.GetObject();
    }
    AssignParameterSet(null);
    OnNewFile();
    GUIConf.Updater.Create();
}

// enable/disable MPI menu
function EnableMPI(enable)
{
    let mpiid = [MenuLabels.edit, MenuLabels.MPI].join(IDSeparator);
    if(enable){
        document.getElementById(mpiid).removeAttribute("disabled");
    }
    else{
        document.getElementById(mpiid).setAttribute("disabled", true);
    }
}

// refresh main GUI palels and menus
function RefreshGUI(enableedit)
{
    if(enableedit){
        document.getElementById(MenuLabels.prmset).classList.remove("d-none");
        document.getElementById([MenuLabels.edit, MenuLabels.material].join(IDSeparator)).removeAttribute("disabled");
        document.getElementById([MenuLabels.edit, MenuLabels.unit].join(IDSeparator)).removeAttribute("disabled");
    }
    else{
        document.getElementById(MenuLabels.prmset).classList.add("d-none");
        document.getElementById([MenuLabels.edit, MenuLabels.material].join(IDSeparator)).setAttribute("disabled", true);
        document.getElementById([MenuLabels.edit, MenuLabels.unit].join(IDSeparator)).setAttribute("disabled", true);
    }
    GUIConf.GUIpanels[ConfigLabel].SetDisabledItems(GUIConf.mainid);

    OnNewFile();
    OpenConfigPanel();
    ArrangeMenus();
}


// arrange objects for SPECTRA GUI
function GetSPECTRAObjects(objs, objname)
{
    let spectraobjs = {};
    spectraobjs[BLLabel] = {[objname]:{}};
    MainCategories.forEach(categ => {
        spectraobjs[categ] = {[objname]: objs[categ]};
        spectraobjs[BLLabel][objname][categ] = objname;
    });
    let otherconfs = [OutFileLabel, VersionNumberLabel];
    otherconfs.forEach(conf => {
        if(objs.hasOwnProperty(conf)){
            spectraobjs[conf] = objs[conf];
        }
    });
    spectraobjs[CurrentLabel] = objname;
    spectraobjs[FMaterialLabel] = {};
    return spectraobjs;
}

// handle load file
function ParameterFileOpened(forcedisable = false)
{
    AssignParameterSet(null, forcedisable);
    RefreshGUI(true);
}

// handle the imported object as a parameter one
function HandleParameterObject(objs, filename)
{
    let forcedisable = false;
    if(objs.hasOwnProperty(InputLabel)){
        objs = CopyJSON(objs[InputLabel]);
        let disableids = [MenuLabels.CMD2d, MenuLabels.CMDPP, MenuLabels.propagate];
        let ctype = "";
        if(objs.hasOwnProperty(ConfigLabel)){
            if(objs[ConfigLabel].hasOwnProperty(TypeLabel)){
                ctype = objs[ConfigLabel][TypeLabel];
            }
        }
        for(const did of disableids){
            if(ctype.includes(did)){
                forcedisable = true;
                break;
            }    
        }
    }
    SetWindowTitle(filename, GUIConf.fileid);

    if(!objs.hasOwnProperty(VersionNumberLabel)){
        ObjConverter.Upconvert(objs);
        objs[VersionNumberLabel] = Version;
    }
    if(!objs.hasOwnProperty(BLLabel)){
        MainCategories.forEach(categ => {
            let obj = CopyJSON(GUIConf.default[categ]);
            objs[categ] = Object.assign(obj, objs[categ]);
        });        
        let objname = GetDataname(filename);
        GUIConf.spectraobjs = GetSPECTRAObjects(objs, objname);
    }
    else{
        GUIConf.spectraobjs = objs;
    }
    if(!GUIConf.spectraobjs.hasOwnProperty(FMaterialLabel)){
        GUIConf.spectraobjs[FMaterialLabel] = {};
    }
    ParameterFileOpened(forcedisable);
    EnableAllRunMenus(!forcedisable);
}

// handle the imported object as an output one
function HandleOutputObject(objs, filename)
{
    GUIConf.loadedobjs = objs;
    if(!GUIConf.loadedobjs.hasOwnProperty(InputLabel)){
        GUIConf.loadedobjs = null;
        return "Invalid format: no input data found";
    }
    let calcid = GUIConf.loadedobjs[InputLabel][ConfigLabel][TypeLabel];
    let targetid = calcid;
    if(GUIConf.fileid.includes(MenuLabels.wignerCMD)){
        if(!calcid.includes(MenuLabels.phasespace)){
            GUIConf.loadedobjs = null;
            return "Invalid format: no Wigner function data found";
        }
        targetid = [MenuLabels.CMD, MenuLabels.CMD2d].join(IDSeparator);
    }
    if(GUIConf.fileid.includes(MenuLabels.wignerProp)){
        if(!calcid.includes(MenuLabels.phasespace)){
            GUIConf.loadedobjs = null;
            return "Invalid format: no Wigner function data found";
        }
        targetid = MenuLabels.propagate;
    }
    if(GUIConf.fileid.includes(MenuLabels.CMDr)){
        if(!GUIConf.loadedobjs.hasOwnProperty(CMDResultLabel)){
            GUIConf.loadedobjs = null;
            return "Invalid format: no CMD results found";
        }
        targetid = [MenuLabels.CMD, MenuLabels.CMDPP].join(IDSeparator);
    }
    if(GUIConf.fileid.includes(MenuLabels.bunch)){
        if(!GUIConf.loadedobjs.hasOwnProperty(FELBunchFactor)){
            GUIConf.loadedobjs = null;
            return "Invalid format: no bunch factor data found";
        }
        GUIConf.loadedobjs[InputLabel][ConfigLabel][ConfigPrmsLabel.fel[0]] = FELReuseLabel;
    }
    SetWindowTitle(filename, GUIConf.fileid);

    let currtype = GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel];
    if(Settings.hasOwnProperty(ConfigLabel)){
        let keys = [];
        if(GUIConf.fileid.includes(MenuLabels.wignerCMD) && !currtype.includes(MenuLabels.wignerCMD)){
            keys = ["GSModel", "GSModelXY", "CMDfld", "CMDint", 
                "HGorderxy", "HGorderx", "HGordery", "maxmode", 
                "fcutoff", "cutoff", "CMDcmp", "CMDcmpint"];
        }
        else if(GUIConf.fileid.includes(MenuLabels.CMDr) && !currtype.includes(MenuLabels.CMDr)){
            keys = ["CMDfld", "CMDint",  "HGorderxy", "HGorderx", "HGordery", 
                "maxmode", "fcutoff", "cutoff"];
        }
        else if(GUIConf.fileid.includes(MenuLabels.wignerProp) && !currtype.includes(MenuLabels.wignerProp)){
            keys = [
                // transverse range option
                "autot", 
                "gridspec", 
                "grlevel", 

                // transverse range values
                "xrange", 
                "xmesh", 
                "yrange", 
                "ymesh", 
                "zrange", 
                "zmesh",
                "wnxrange", 
                "wnyrange", 
                "wdxrange", 
                "wdyrange", 
                "wndxrange", 
                "wndyrange", 
                "wdxmesh", 
                "wdymesh",

                // other options
                "optics",
                "optpos",
                "aptx", 
                "aptdistx",
                "apty", 
                "aptdisty",
                "softedge",
                "diflim",
                "anglelevel",
                "foclenx",
                "focleny",
                "aprofile",
                "wigner",
                "csd",
                "degcoh",                
            ];
        }
        let config = GUIConf.loadedobjs[InputLabel][ConfigLabel];
        for(const key of keys){
            let label = ConfigPrmsLabel[key][0];
            if(!config.hasOwnProperty(label)){
                if(Settings[ConfigLabel].hasOwnProperty(label)){
                    config[label] = Settings[ConfigLabel][label];
                }
            }
        }
    }

    let defconf = CopyJSON(GUIConf.default);
    MainCategories.forEach(categ => {
        Object.assign(defconf[categ], GUIConf.loadedobjs[InputLabel][categ]);
    });
    GUIConf.loadedobjs[InputLabel] = CopyJSON(defconf);

    let objname = GetDataname(filename);
    GUIConf.spectraobjs = GetSPECTRAObjects(GUIConf.loadedobjs[InputLabel], objname);

    if(!GUIConf.loadedobjs[InputLabel][ConfigLabel].hasOwnProperty(OrgTypeLabel)){
        GUIConf.loadedobjs[InputLabel][ConfigLabel][OrgTypeLabel] = 
            GUIConf.loadedobjs[InputLabel][ConfigLabel][TypeLabel];
    }
    GUIConf.loadedobjs[InputLabel][ConfigLabel][TypeLabel] = targetid;
    let config = CopyJSON(GUIConf.loadedobjs[InputLabel][ConfigLabel]);
    if(GUIConf.fileid.includes(MenuLabels.wignerCMD) || GUIConf.fileid.includes(MenuLabels.CMDr)){
        let tmpconfig = GUIConf.loadedobjs[InputLabel][ConfigLabel];
        let ranges = [
            tmpconfig[ConfigPrmsLabel.Xrange[0]],
            tmpconfig[ConfigPrmsLabel.Yrange[0]]
        ]
        let mesh = [
            tmpconfig[ConfigPrmsLabel.Xmesh[0]],
            tmpconfig[ConfigPrmsLabel.Ymesh[0]]
        ]
        let delta = [0, 0];
        for(let j = 0; j < 2; j++){
            delta[j] = (ranges[j][1]-ranges[j][0])/Math.max(1, mesh[j]-1);
            delta[j] = ToPrmString(delta[j], 3);
            ranges[j] = Math.max(Math.abs(ranges[j][0]), Math.abs(ranges[j][1]));
        }
        config[ConfigPrmsLabel.fieldrangex[0]] = ranges[0];
        config[ConfigPrmsLabel.fieldrangey[0]] = ranges[1];
        config[ConfigPrmsLabel.fieldrangexy[0]] = [ranges[0], ranges[1]];
        config[ConfigPrmsLabel.fieldgridx[0]] = delta[0];
        config[ConfigPrmsLabel.fieldgridy[0]] = delta[1];
        config[ConfigPrmsLabel.fieldgridxy[0]] = [delta[0], delta[1]];
        if(GUIConf.fileid.includes(MenuLabels.CMDr)){
            if(config[OrgTypeLabel].includes(MenuLabels.XXpYYp)){
                config[ConfigPrmsLabel.maxHGorderxy[0]] = GUIConf.loadedobjs[CMDResultLabel][MaxOrderLabel];
            }
            else if(config[OrgTypeLabel].includes(MenuLabels.XXpprj)){
                config[ConfigPrmsLabel.maxHGorderx[0]] = GUIConf.loadedobjs[CMDResultLabel][MaxOrderLabel]
            }
            else if(config[OrgTypeLabel].includes(MenuLabels.YYpprj)){
                config[ConfigPrmsLabel.maxHGordery[0]] = GUIConf.loadedobjs[CMDResultLabel][MaxOrderLabel]
            }    
        }
    }
    else if(GUIConf.fileid.includes(MenuLabels.wignerProp)){
        let isx = false;
        let isy = false;
        if(config[OrgTypeLabel].includes(MenuLabels.XXpYYp)){
            isx = isy = true;
        }
        else if(config[OrgTypeLabel].includes(MenuLabels.XXpprj)){
            isx = true;
        }
        else if(config[OrgTypeLabel].includes(MenuLabels.YYpprj)){
            isy = true;
        }
        else{
            return "This data is not available for wavefront propagation.";
        }
        if(!GUIConf.loadedobjs.hasOwnProperty(OutputLabel)){
            return "No output data found.";
        }
        let dataobj = GUIConf.loadedobjs[OutputLabel];
        let isok = true;
        if(!dataobj.hasOwnProperty(DataDimLabel)){
            isok = false;
        }
        else if(!dataobj.hasOwnProperty(DataTitlesLabel)){
            isok = false;            
        }
        else if(!dataobj.hasOwnProperty(UnitsLabel)){
            isok = false;            
        }
        else if(!dataobj.hasOwnProperty(DataLabel)){
            isok = false;            
        }
        if(!isok){
            return "Output data format invalid.";
        }
        let dim = dataobj[DataDimLabel];
        if(dim != 2 && dim != 4){
            return "Output data format invalid.";
        }
        let vararray = [[0], [0], [0], [0]];
        let xyidx = [WigXLabel, WigYLabel, WigXpLabel, WigYpLabel];
        for(let j = 0; j < dim; j++){
            let darray = dataobj[DataLabel][j];
            let dlen = darray.length;
            let title = dataobj[DataTitlesLabel][j]+": "
            if(dlen%2 == 0){
                return title+"Length of the variables should be an odd number.";
            }
            else if(darray[(dlen-1)/2] != 0){
                return title+"Invalid position of the origin.";
            }
            let jk = xyidx.indexOf(dataobj[DataTitlesLabel][j]);
            if(jk < 0){
                return title+"Invalid variable included.";
            }
            vararray[jk] = darray;
        }
        let labels = [
            [ConfigPrmsLabel.Xmesh[0], ConfigPrmsLabel.Xrange[0]],
            [ConfigPrmsLabel.Ymesh[0], ConfigPrmsLabel.Yrange[0]],
            [ConfigPrmsLabel.Xpmesh[0], ConfigPrmsLabel.Xprange[0]],
            [ConfigPrmsLabel.Ypmesh[0], ConfigPrmsLabel.Yprange[0]]
        ]
        for(let j = 0; j < labels.length; j++){
            config[labels[j][0]] = vararray[j].length;
            config[labels[j][1]] = [vararray[j][0], vararray[j][vararray[j].length-1]];    
        }

        let wigdata = dataobj[DataLabel][dim];
        let size = [0, 0, 0, 0];
        let v = [0, 0, 0, 0];
        let sum = 0;
        let ntot = 0;
        for(let i = 0;  i < vararray[3].length; i++){
            v[3] = vararray[3][i];
            for(let j = 0;  j < vararray[2].length; j++){
                v[2] = vararray[2][j];
                for(let k = 0;  k < vararray[1].length; k++){
                    v[1] = vararray[1][k];
                    for(let l = 0;  l < vararray[0].length; l++){
                        v[0] = vararray[0][l];
                        for(let n = 0; n < 4; n++){
                            size[n] += v[n]*v[n]*wigdata[ntot];
                        }
                        sum += wigdata[ntot];
                        ntot++;
                    }                    
                }                    
            }    
        }
        for(let n = 0; n < 4; n++){
            if(sum <= 0){
                size[n] = 0;
            }
            else{
                size[n] = Math.sqrt(Math.max(0, size[n]/sum));
            }
        }
        config[ConfigPrmsLabel.wigsizex[0]] = [size[0], size[2]];
        config[ConfigPrmsLabel.wigsizey[0]] = [size[1], size[3]];
    }
    GUIConf.GUIpanels[ConfigLabel].JSONObj = config;

    [AccLabel, SrcLabel].forEach(categ => {
        GUIConf.GUIpanels[categ].JSONObj = GUIConf.loadedobjs[InputLabel][categ];
    });
    RefreshGUI(false);
    SetDisableCalcIDs();

    return "";
}

// handle the imported data from a file
function HandleFile(data, filename)
{
    if(GUIConf.fileid.includes(MenuLabels.loadf)){
        let objs;
        try {
            objs = JSON.parse(data);
        }
        catch(e) {
            let msg = '"'+filename+'"'+" is not a SPECTRA output file.: "+e.message;
            Alert(msg);
            GUIConf.loading = false;
            return;
        }
        let msg = HandleOutputObject(objs, filename);
        if(msg != ""){
            Alert(msg);
        }
    }
    else if(GUIConf.fileid.includes(MenuLabels.file) 
            && (GUIConf.fileid.includes(MenuLabels.open) 
            || GUIConf.fileid.includes(MenuLabels.append)))
    {        
        let objs;
        try {
            objs = JSON.parse(data);
        }
        catch(e) {
            objs = ConvertPrm(data);
            let msg;
            if(objs == null){
                msg = '"'+filename+'" is not a SPECTRA output file.';
                Alert(msg);
                GUIConf.loading = false;
                return;
            }
            msg = 'Updated the old parameter file "'+filename+'" to the latest version.';
            Alert(msg);
            GUIConf.loading = false;
            return;
        }
        if(GUIConf.fileid.includes(MenuLabels.append)){
            let blobjs = {};
            if(objs.hasOwnProperty(BLLabel)){
                blobjs = objs[BLLabel];
            }
            MainCategories.forEach(categ => {               
                if(GUIConf.spectraobjs.hasOwnProperty(categ) && objs.hasOwnProperty(categ)){
                    let keys = Object.keys(objs[categ]);
                    keys.forEach(key => {
                        let oldkey = key;
                        let incr = 0;
                        while(GUIConf.spectraobjs[categ].hasOwnProperty(key)){
                            incr++;
                            key = oldkey+"-"+incr.toString();
                        }
                        if(key != oldkey){
                            Object.keys(blobjs).forEach(bl => {
                                if(blobjs[bl][categ] == oldkey){
                                    blobjs[bl][categ] = key;
                                }
                            })
                        }
                        GUIConf.spectraobjs[categ][key] = objs[categ][oldkey]
                    });
                }
            })
            if(GUIConf.spectraobjs.hasOwnProperty(BLLabel) == false){
                GUIConf.spectraobjs[BLLabel] = {};
            }
            Object.keys(blobjs).forEach(bl => {
                let blnew = bl;
                let incr = 0;
                while(GUIConf.spectraobjs[BLLabel].hasOwnProperty(blnew)){
                    incr++;
                    blnew = bl+"-"+incr.toString();
                }
                GUIConf.spectraobjs[BLLabel][blnew] = blobjs[bl]
            })
            HandleParameterObject(GUIConf.spectraobjs, GUIConf.filename);
        }
        else{
            HandleParameterObject(objs, filename);
        }
    }
    else if(GUIConf.fileid.includes(MenuLabels.outpostp)){
        try {
            let obj = JSON.parse(data);
            CreateNewplot(obj);    
        } catch (e) {
            Alert(e);
        }
    }
    else if(GUIConf.fileid.includes(MenuLabels.preproc) 
            && GUIConf.fileid.includes(MenuLabels.load)){
        let str;
        if(data.length > 1000){
            str = data.substring(0, 1000);
            str += "....."
        }
        else{
            str = data;
        }
        const regexp = /[\r\n]/g;        
        let cols = str.match(regexp).length+2;
        cols = Math.min(Math.max(3, cols), 5);
        let cont = document.getElementById("preproc-part-cont");
        cont.innerHTML = str;
        cont.setAttribute("rows", cols.toString());
        GUIConf.part_data = data;
        document.getElementById("preproc-part-anadiv").classList.remove("d-none");
        document.getElementById("preproc-part-plotconf-div").classList.add("d-none");
        AnalyzeParticle();
    }
    else if(GUIConf.fileid.includes(MenuLabels.preproc) 
            && GUIConf.fileid.includes(MenuLabels.import)){
        let units = null;
        let setunit = GUIConf.GUIpanels[DataUnitLabel].JSONObj;
        if(GUIConf.import.ascii == ImportGapField)
        {
            units = [1, 1, 1];
            if(setunit[DataUnitOptionsLabel.gap[0]] == UnitMeter)
            {
                units[0] = 1000;
            }
            else if(setunit[DataUnitOptionsLabel.gap[0]] == UnitCentiMeter)
            {
                units[0] = 10;
            }
            if(setunit[DataUnitOptionsLabel.magf[0]] == UnitGauss){
                units[1] = units[2] = 1e-4;
            }
        }
        else if(GUIConf.import.ascii == CustomField || GUIConf.import.ascii == CustomPeriod)
        {
            units = [1, 1, 1];
            if(setunit[DataUnitOptionsLabel.zpos[0]] == UnitMiliMeter)
            {
                units[0] = 1e-3;
            }
            else if(setunit[DataUnitOptionsLabel.zpos[0]] == UnitCentiMeter)
            {
                units[0] = 1e-2;
            }
            if(setunit[DataUnitOptionsLabel.magf[0]] == UnitGauss){
                units[1] = units[2] = 1e-4;
            }
        }
        else if(GUIConf.import.ascii == CustomDepth){
            units = [1];
            if(setunit[DataUnitOptionsLabel.depth[0]] == UnitMeter){
                units[0] = 1000;
            }
            else if(setunit[DataUnitOptionsLabel.depth[0]] == UnitCentiMeter){
                units[0] = 10;
            }
        }
        else{
            if(GUIConf.import.ascii == CustomCurrent)
            {
                units = [1, 1];
            }
            else if(GUIConf.import.ascii == CustomEt)
            {
                units = [1, 1, 1];
            }
            if(units != null){
                if(setunit[DataUnitOptionsLabel.time[0]] == UnitMeter){
                    units[0] = 1e15/CC;
                }
                else if(setunit[DataUnitOptionsLabel.time[0]] == UnitMiliMeter){
                    units[0] = 1e12/CC;
                }
                else if(setunit[DataUnitOptionsLabel.time[0]] == UnitSec){
                    units[0] = 1e15;
                }
                else if(setunit[DataUnitOptionsLabel.time[0]] == UnitpSec){
                    units[0] = 1e3;
                }
            }
        }
        GUIConf.ascii[GUIConf.import.ascii].SetData(data, units);
        GUIConf.GUIpanels[GUIConf.import.category].JSONObj[GUIConf.import.prmlabel]
            = GUIConf.ascii[GUIConf.import.ascii].GetObj();
        if(GUIConf.import.ascii == ImportGapField){
            GUIConf.GapFieldTable.SetSrcObj();
        }
        GUIConf.Updater.Update();
        UpdatePPPlot();
        EnableCutomFieldItems();
    }
    else if(GUIConf.fileid == "compatibility"){
        try {
            GUIConf.compobj.push(JSON.parse(data));
        }
        catch (e) {
            Alert(filename+" is not a JSON file.");
            GUIConf.compobj = [];
        }
        if(GUIConf.compobj.length == 2){
            let result = ObjConverter.Compare(GUIConf.compobj);
            if(result.length > 0){
                Alert(result.join("\n"));
            }
        }
    }
    GUIConf.loading = false;
}

// procedures for initial loading/launcher of the program
// load configuration
async function GetConfiguration()
{
    try {
        SwitchSpinner(true);
        let conffile = await window.__TAURI__.path.join(GUIConf.wdname, ConfigFileName);
        let data = await window.__TAURI__.tauri.invoke("read_file", { path: conffile});
        SwitchSpinner(false);
        if(data != ""){
            Object.assign(Settings, JSON.parse(data));
            let keys = Object.keys(Settings);
            for(const key of keys){
                if(!SettingKeys.includes(key)){
                    delete Settings[key];
                }
            }

            // convert old MPI settings
            let oldmpi = "MPI Settings";
            if(Settings.hasOwnProperty[oldmpi]){
                Settings[MPILabel] = Settings[oldmpi];
                delete Settings[oldmpi];
            }
            if(Settings.hasOwnProperty(MPILabel)){
                let oldpara = "Enable Parallel Computing";
                if(Settings[MPILabel].hasOwnProperty(oldpara)){
                    if(Settings[MPILabel][oldpara]){
                        Settings[MPILabel][MPIOptionsLabel.parascheme[0]] = ParaMPILabel;
                    }
                    delete Settings[MPILabel][oldpara];
                }
            }

            let categs = [AccuracyLabel, DataUnitLabel, MPILabel, OutFileLabel];
            let labels = [AccuracyOptionsLabel, DataUnitOptionsLabel, MPIOptionsLabel, OutputOptionsLabel];
            for(let j = 0; j < categs.length; j++){
                if(Settings.hasOwnProperty(categs[j])){
                    CleanObject(Settings[categs[j]], labels[j]);
                }
            }
            for(const option of SettingPanels){
                if(Settings.hasOwnProperty(option)){
                    GUIConf.GUIpanels[option].JSONObj = Settings[option];
                    GUIConf.GUIpanels[option].SetPanel();
                }
            }
            
            if(Settings.hasOwnProperty("animinterv")){
                AnimationInterval = Settings.animinterv;
            };
            if(Settings.hasOwnProperty(OutFileLabel)){
                GUIConf.GUIpanels[OutFileLabel].JSONObj[OutputOptionsLabel.fixpdata[0]] = [["-", "-", "-"]];
            }
        }
    } catch(e) {
        Alert(e);
    }
}

// check version compatibility
function CompareVersions()
{
    GUIConf.compobj = [];
    GUIConf.fileid = "compatibility"
    document.getElementById("file-main").setAttribute("accept", "application/json");
    document.getElementById("file-main").setAttribute("multiple", true);
    document.getElementById("file-main").click();
    document.getElementById("file-main").removeAttribute("accept");
    document.getElementById("file-main").removeAttribute("multiple");
}

var init_process = Initialize();

window.onload = async function()
{
    MainGUI();
    document.getElementById("file-main").addEventListener(
        "change", (e) => {
            LoadFiles(e, HandleFile);
            document.getElementById("file-main").value = "";
        });

    let tabs = document.querySelectorAll(`[id$="tab"]`);
    let ids = [];
    tabs.forEach(el => {
        el.addEventListener("click", ev => {
            if(ev.currentTarget.id == GUIConf.panelid){
                return;
            }
            document.getElementById(GUIConf.panelid).classList.remove("fw-bold");
            document.getElementById(ev.currentTarget.id).classList.add("fw-bold");
        
            GUIConf.panelid = ev.currentTarget.id;
        
            let id = GetPanelID(GUIConf.panelid);
            if(id == "postproc" || id == "preproc"){
                if(id == "postproc"){
                    SetPlotSize(["postp-plot"]);    
                    GUIConf.postprocessor.Refresh();    
                }
                else{
                    SetPreprocessPlot();
                    SetPlotSize(["preproc-plot"]);
                    if(GUIConf.plotly != null){
                        GUIConf.plotly.RefreshPlotObject();
                    }    
                }
            }
        });
    });

    let scanmenu = document.getElementById("scan-prm-item");
    scanmenu.addEventListener("click", ev => {
        MenuCommand(ev.currentTarget.id);
    });

    let plotdivs = Object.keys(GUIConf.plot_aspect);    
    for(let j = 0; j < plotdivs.length; j++){
        Observer[plotdivs[j]] = new MutationObserver((mutation) => {
            if(plotdivs[j] == "preproc-plot"){
                if(GUIConf.plotly != null){
                    GUIConf.plotly.RefreshPlotObject();
                }
            }
            else if(plotdivs[j] == "postp-plot"){
                GUIConf.postprocessor.Refresh();
            }
            let target = document.getElementById(plotdivs[j]);
            if(!target.classList.contains("d-none")){
                GUIConf.plot_aspect[plotdivs[j]] = target.clientHeight/target.clientWidth;
            }    
        });
        const options = {
            attriblutes: true,
            attributeFilter: ["style"]
        };
        Observer[plotdivs[j]].observe(document.getElementById(plotdivs[j]), options);
    }

    init_process.then(async function () {
        if(Settings.hasOwnProperty(PlotWindowsRowLabel)){
            GUIConf.postprocessor.SetPlotCols(Settings[PlotWindowsRowLabel]);
        }
        if(Settings.hasOwnProperty(SubPlotsRowLabel)){
            GUIConf.postprocessor.SetSubPlotCols(Settings[SubPlotsRowLabel]);
        }

        for(const option of SettingPanels){
            if(Settings.hasOwnProperty(option)){
                GUIConf.GUIpanels[option].JSONObj = Settings[option];
                GUIConf.GUIpanels[option].SetPanel();
            }
        }

        GUIConf.fileid = [MenuLabels.file, MenuLabels.open].join(IDSeparator);

        if(!CheckMenuLabels()){
            Alert("Key overlap found in MenuLabels constant");
        }
        if(Framework != BrowserLabel && Framework != ServerLabel){
            document.getElementById(GetPreprocID("load")).classList.add("d-none");
        }
        if(Framework == ServerLabel){
            LocalStorage(false);
        }
        SetSettingsGUI();
        if(Framework == ServerLabel && (iniFile != "" || iniPP != "" || iniLPP != "")){
            if(iniDir != ""){
                iniDir += "/"
            }
            if(iniFile != ""){
                let xhr = new XMLHttpRequest();
                xhr.open("GET", "get_file.php?filename=prm/"+iniDir+iniFile, true); 
                xhr.responseType = "text";
                xhr.addEventListener("load", function(event){
                    if(xhr.response != null){
                        HandleFile(xhr.response, iniFile);
                    }
                    else{
                        LoadRevisedPrmSet(false);
                    }
                    ArrangeMenus();
                    if(iniBL != ""){
                        if(GUIConf.spectraobjs[BLLabel].hasOwnProperty(iniBL)){
                            GUIConf.spectraobjs[CurrentLabel] = iniBL;
                            let id = [MenuLabels.prmset, BLLabel, iniBL].join(IDSeparator);
                            MenuCommand(id);
                        }
                    }
                });
                xhr.send(null);
            }
            if(iniPP != "" || iniLPP != ""){
                let iniPPs = [iniPP, iniLPP];
                for(let j = 0; j < 2; j++){
                    let PPfile = iniPPs[j];
                    if(PPfile == ""){
                        continue;
                    }
                    if(j == 1){
                        GUIConf.fileid = [MenuLabels.file, MenuLabels.outpostp].join(IDSeparator);
                    }
                    let ppfiles;
                    if(PPfile.includes(",")){
                        ppfiles = PPfile.split(",");
                    }
                    else{
                        ppfiles = [PPfile];
                    }
                    for(const ppfile of ppfiles){
                        let xhr = new XMLHttpRequest();
                        xhr.open("GET", "get_file.php?filename=data/"+iniDir+ppfile, true); 
                        xhr.responseType = "text";
                        xhr.addEventListener("load", async (e) => {
                            if(xhr.response != null){
                                if(j == 0){
                                    document.getElementById("postproc-tab").click();
                                    GUIConf.postprocessor.LoadOutputFile(xhr.response, ppfile, true);    
                                }
                                else{
                                    HandleFile(xhr.response, ppfiles, true);
                                }
                            }
                        });
                        xhr.send(null);    
                    }    
                }
                LoadRevisedPrmSet(false);
                ArrangeMenus();
            }
            return;
        }
        else if(Framework == TauriLabel && Settings.hasOwnProperty("lastloaded"))
        {
            if(Settings.hasOwnProperty("lastid")){
                GUIConf.mainid = GUIConf.fileid = Settings.lastid;
            }
            SwitchSpinner(true);
            let data = await window.__TAURI__.tauri.invoke("read_file", { path: Settings.lastloaded });
            SwitchSpinner(false);
            if(data != ""){
                HandleFile(data, Settings.lastloaded);
            }
        }
        else{
            LoadRevisedPrmSet(false);
        }
        ArrangeMenus();
    });
}

window.addEventListener("beforeunload", () => {
    if(Framework == TauriLabel){
        BeforeExit().then((e) => {
            window.__TAURI__.process.exit(0);
        });
    }
    else if(Framework == ServerLabel){
        LocalStorage(true);
    }
});

window.addEventListener("message", (e) => {
    if(e.data == "ready"){
        let object = PlotObjects.objects.Get();
        object.Framework = Framework;
        PlotObjects.windows.Get().postMessage(object, "*");
        return;
    }
    if(Framework != PythonGUILabel){
        return;
    }
    let obj;
    try {
        obj = JSON.parse(e.data);
    }
    catch (e) {
        Alert(e);
        return;
    }

    let id = [MenuLabels.duplicate]
    if(obj.type == "save"){
        id.push(MenuLabels.save);
    }
    else{
        id.push(MenuLabels.ascii);        
    }
    id = id.join(IDSeparator);
    BufferObject = obj.data;
    PyQue.Put(id);
});

window.onresize = function()
{
    SetPlotSize();
}

// key binding for supplmental functions (generating C++ source code etc.)
window.addEventListener("keydown", (ev) => {
    try {
        if(ev.key == "e" && ev.ctrlKey && Framework == BrowserLabel){
            GenerateHeaderFile();
        }
        else if(ev.key == "q" && ev.ctrlKey && Framework == BrowserLabel){
            ExportHelpFile();
        }
        else if(ev.key == "c" && ev.ctrlKey && Framework == BrowserLabel){
            CompareVersions();
        }
        else{
            let prmname = SplitPath(GUIConf.filename).name;
            if(!ReferenceInputFiles.includes(prmname)){
                return;
            }
            if(ev.ctrlKey && (ev.key == "a" || ev.key == "h")){
                if(ev.altKey){ // only current parameter set
                    let outfobj = GUIConf.GUIpanels[OutFileLabel].JSONObj;
                    outfobj[OutputOptionsLabel.prefix[0]] = GUIConf.spectraobjs[CurrentLabel];
                    CreateAllCalcProcesses(ev.key == "h")
                }
                else{ // all parameter sets
                    CreateAllProcesses(ev.key == "h", false);
                }
            }
            if(ev.ctrlKey && ev.key == "s"){
                CreateAllProcesses(false, true);
            }
            return;
        }
    }
    catch (e) {
        Alert(e);
    }
}, false);

//-------------------------
// create processes to check the compatibility with former versions
//-------------------------

var ReferenceInputFiles = ["std.json", "misc.json", "csr.json"];

function CreateAllProcesses(iscoh, issingle)
{
    let blnames = Object.keys(GUIConf.spectraobjs[BLLabel]);
    let outfobj = GUIConf.GUIpanels[OutFileLabel].JSONObj;

    blnames.forEach(function(el) {
        GUIConf.spectraobjs[CurrentLabel] = el;
        let prmsetid = [MenuLabels.prmset, BLLabel, el].join(IDSeparator);
        MenuCommand(prmsetid);
        outfobj[OutputOptionsLabel.prefix[0]] = el;
        if(issingle){
            outfobj[OutputOptionsLabel.serial[0]] = -1;
            RunCommand([MenuLabels.run, MenuLabels.process].join(IDSeparator));
        }
        else{
            outfobj[OutputOptionsLabel.serial[0]] = 0;
            CreateAllCalcProcesses(iscoh)
        }
    });
}

function AddOption(calcid, options, iscoh)
{
    let optobj = {}, option = {}, categ = {};

    optobj[ConfigPrmsLabel.aperture[0]] = [
        "Far Field & Ideal Condition::K Dependence::Peak Flux Curve::Partial Flux::Rectangular Slit::Target Harmonics",
        "Far Field & Ideal Condition::K Dependence::Peak Flux Curve::Partial Flux::Rectangular Slit::All Harmonics",
        "Far Field & Ideal Condition::K Dependence::Power::Partial Power::Rectangular Slit"
    ];
    option[ConfigPrmsLabel.aperture[0]] = NormSlitLabel;
    categ[ConfigPrmsLabel.aperture[0]] = iscoh ? "" : ConfigLabel;

    optobj[AccPrmsLabel.singlee[0]] = [
        "Coherent Radiation::Time Dependence::Electric Field",
        "Coherent Radiation::Spatial Dependence::Complex Amplitude::Mesh: x-y"
    ];
    option[AccPrmsLabel.singlee[0]] = true;
    categ[AccPrmsLabel.singlee[0]] = iscoh ? "" : AccLabel;

    optobj[ConfigPrmsLabel.fouriep[0]] = [
        "Coherent Radiation::Time Dependence::Electric Field",
        "Coherent Radiation::Time Dependence::Spatial Power Density",
        "Coherent Radiation::Time Dependence::Partial Power::Rectangular Slit",
        "Coherent Radiation::Time Dependence::Partial Power::Circular Slit"
    ];
    option[ConfigPrmsLabel.fouriep[0]] = true;
    categ[ConfigPrmsLabel.fouriep[0]] = iscoh ? ConfigLabel : "";

    Object.keys(optobj).forEach(el => {
        let cids = optobj[el];
        for(let n = 0; n < cids.length; n++){
            if(cids[n] == calcid){
                options.push({
                    id: calcid,
                    label: el,
                    categ: categ[el],
                    value: option[el]
                });
            }
        }
    });
}

function CreateAllCalcProcesses(iscoh)
{
    let outfobj = GUIConf.GUIpanels[OutFileLabel].JSONObj;
    let options = [];
    let serorg = outfobj[OutputOptionsLabel.serial[0]];
    for(let n = 0; n < GUIConf.runids.length; n++){
        let runid = GUIConf.runids[n].split(IDSeparator).slice(1).join(IDSeparator);
        outfobj[OutputOptionsLabel.serial[0]] = n;
        AddOption(runid, options, iscoh);
        if(runid.indexOf(MenuLabels.fixed) >= 0){
            continue;
        }
        else if(iscoh && runid.indexOf(MenuLabels.cohrad) < 0){
            continue;
        }
        else if(!iscoh && runid.indexOf(MenuLabels.cohrad) >= 0){
            continue;
        }
        let skip = false;
        for(let j = 0; j < GUIConf.disabled.length; j++){
            if(runid.indexOf(GUIConf.disabled[j]) >= 0){
                skip = true;
                break;
            }
        }
        if(skip){
            continue;
        }
        let erange = null, e1stk = null, efix = null, accu = null;
        let de, acculim, accnp;
        let wige = MenuLabels.srcpoint+"::"+MenuLabels.wigner+"::"+MenuLabels.energy;
        let srcobj = GUIConf.GUIpanels[SrcLabel].JSONObj;
        let srccont = GetSrcContents(srcobj);
        let srctype = srcobj[TypeLabel];
        let confobj = GUIConf.GUIpanels[ConfigLabel].JSONObj;
        if(runid == wige){
            if(srcobj[TypeLabel] == FIELDMAP3D_Label){
                continue;
            }
            if(srccont.isund >= 0){
                erange = confobj[ConfigPrmsLabel.erange[0]];
                de = confobj[ConfigPrmsLabel.de[0]];
                let e1st = srcobj[SrcPrmsLabel.e1st[0]];

                let nemin = 0.9;
                let nemax = 1.05;
                let nepoints = 400;
                if(srcobj[SrcPrmsLabel.segment_type[0]] != NoneLabel 
                        && srcobj[SrcPrmsLabel.perlattice[0]])
                {
                    nemin = 0.975;
                    nemax = 1.015;
                }
                confobj[ConfigPrmsLabel.erange[0]] = [e1st*nemin, e1st*nemax];
                confobj[ConfigPrmsLabel.de[0]] = e1st/nepoints;
                GUIConf.Updater.Update();
                GUIConf.GUIpanels[ConfigLabel].SetPanel();
            }
        }
        if(runid == wige || runid.includes(MenuLabels.XXpYYp) || runid.includes(MenuLabels.YYpslice)){
            if(srccont.isund >= 0 
                && srcobj[SrcPrmsLabel.segment_type[0]] != NoneLabel 
                && srcobj[SrcPrmsLabel.perlattice[0]])
            {
                accu = confobj[ConfigPrmsLabel.accuracy[0]];
                acculim = GUIConf.GUIpanels[AccuracyLabel].JSONObj[AccuracyOptionsLabel.acclimMCpart[0]];
                accnp = GUIConf.GUIpanels[AccuracyLabel].JSONObj[AccuracyOptionsLabel.accMCpart[0]];
                confobj[ConfigPrmsLabel.accuracy[0]] = CustomLabel;
                GUIConf.GUIpanels[AccuracyLabel].JSONObj[AccuracyOptionsLabel.acclimMCpart[0]] = true;
                GUIConf.GUIpanels[AccuracyLabel].JSONObj[AccuracyOptionsLabel.accMCpart[0]] = 10000;
            }
        }
        if(runid.includes(MenuLabels.srcpoint)){
            efix = confobj[ConfigPrmsLabel.efix[0]];
        }
        else if(runid.includes(MenuLabels.vpdens) && 
            (srctype == FIGURE8_UND_Label || 
            srctype == ELLIPTIC_UND_Label ||
            srctype == VFIGURE8_UND_Label ||
            srctype == HELICAL_UND_Label))
        {
            e1stk = srcobj[SrcPrmsLabel.e1st[0]];
            srcobj[SrcPrmsLabel.e1st[0]] = 2000;
            let id = GetIDFromItem(SrcLabel, SrcPrmsLabel.e1st[0], -1);
            GUIConf.Updater.Update(id);
            GUIConf.GUIpanels[ConfigLabel].SetPanel();
        }

        MenuCommand(GUIConf.runids[n]);
        RunCommand([MenuLabels.run, MenuLabels.process].join(IDSeparator));

        if(erange != null){
            confobj[ConfigPrmsLabel.erange[0]] = erange;
            confobj[ConfigPrmsLabel.de[0]] = de;
            erange = null;
        }
        if(accu != null){
            confobj[ConfigPrmsLabel.accuracy[0]] = accu;
            GUIConf.GUIpanels[AccuracyLabel].JSONObj[AccuracyOptionsLabel.acclimMCpart[0]] = acculim;
            GUIConf.GUIpanels[AccuracyLabel].JSONObj[AccuracyOptionsLabel.accMCpart[0]] = accnp;
            accu = null;
        }
        if(e1stk != null){
            srcobj[SrcPrmsLabel.e1st[0]] = e1stk;
            let id = GetIDFromItem(SrcLabel, SrcPrmsLabel.e1st[0], -1);
            GUIConf.Updater.Update(id);
            GUIConf.GUIpanels[SrcLabel].SetPanel();
            e1stk = null;
        }
        if(efix != null){
            confobj[ConfigPrmsLabel.efix[0]] = efix;
            efix = null;
        }
    }
    for(let n = 0; n < options.length; n++){
        // --->> eliminate Wigner Wavefront Propagation to be consistent with 11.2
        outfobj[OutputOptionsLabel.serial[0]] = GUIConf.runids.length+n-1;
        let skip = false;
        for(let j = 0; j < GUIConf.disabled.length; j++){
            if(options[n].id.indexOf(GUIConf.disabled[j]) >= 0){
                skip = true;
                break;
            }
        }
        if(skip){
            continue;
        }
        if(options[n].categ == ""){
            continue;
        }
        let targetobj = GUIConf.GUIpanels[options[n].categ].JSONObj;

        let org = targetobj[options[n].label];
        targetobj[options[n].label] = options[n].value;

        let srcobj = GUIConf.GUIpanels[SrcLabel].JSONObj;
        let confobj = GUIConf.GUIpanels[ConfigLabel].JSONObj;
        let srccont = GetSrcContents(srcobj);
        let efix = null, dxy = null;
        if(options[n].id.includes(MenuLabels.camp) && srccont.isund >= 0){
            efix = confobj[ConfigPrmsLabel.efix[0]];
            confobj[ConfigPrmsLabel.efix[0]] = srcobj[SrcPrmsLabel.e1st[0]];
        }
        if(options[n].label == ConfigPrmsLabel.aperture[0] && srccont.isund >= 0){
            dxy = Array.from(confobj[ConfigPrmsLabel.slitapt[0]]);
        }

        MenuCommand([MenuLabels.calc, options[n].id].join(IDSeparator));
        RunCommand([MenuLabels.run, MenuLabels.process].join(IDSeparator));

        targetobj[options[n].label] = org;

        if(efix != null){
            confobj[ConfigPrmsLabel.efix[0]] = efix;
        }
        if(dxy != null){
            confobj[ConfigPrmsLabel.slitapt[0]] = dxy;
        }

    }
    outfobj[OutputOptionsLabel.serial[0]] = serorg;
}
