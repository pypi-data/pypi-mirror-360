"use strict";

// functions for updating paramters -->
function IsDataReady(srcobj)
{
    let srctype = srcobj[TypeLabel];
    if(srctype == CUSTOM_Label
        ||  srctype == CUSTOM_PERIODIC_Label)
    {
        let prmlabel;
        if(srctype == CUSTOM_Label){
            prmlabel = SrcPrmsLabel.fvsz[0];
        }
        else{
            prmlabel = SrcPrmsLabel.fvsz1per[0];
        }
        if(!srcobj.hasOwnProperty(prmlabel)){
            return false;
        }
        if(!srcobj[prmlabel].hasOwnProperty("data")){
            return false;
        }
        let data = srcobj[prmlabel].data;
        if(!Array.isArray(data)){
            return false;
        }
        if(data.length < 3){
            return false;
        }
        for(let j = 0; j < 3; j++){
            if(data[j].length < 2){
                return false;
            }
        }
        return true;
    }
    else{
        return true;
    }
}

function GetUprmArb(srcobj)
{
    let POINTSPERPER = 32;

    let srctype = srcobj[TypeLabel];
    let z, Bxy, npoints, lu, ku;
    let isf8 = 
        srctype == FIGURE8_UND_Label ||
        srctype == VFIGURE8_UND_Label;

    if(isf8 || srctype == MULTI_HARM_UND_Label){
        let grid = [];
        if(srctype == FIGURE8_UND_Label){
            grid = [
                ["1", "0", "0", "0"],
                ["0", "0", "1", "0"]
            ];
        }
        else if(srctype == VFIGURE8_UND_Label){
            grid = [
                ["0", "0", "1", "0"],
                ["1", "0", "0", "0"]
            ];
        }
        else{
            if(Array.isArray(srcobj[SrcPrmsLabel.multiharm[0]])){
                grid = srcobj[SrcPrmsLabel.multiharm[0]];
            }
            if(grid.length == 0){
                grid = [["1", "90", "1", "0"]];
                // elliptic undulator 
            }
        }
        let kxy = [], phase = [], isnon0 = [true, true];
        for(let nh = 0; nh < grid.length; nh++){
            if(nh == 0){
                kxy.push([1, 1]);
            }
            else{
                kxy.push([0, 0]);
            }
            phase.push([0, 0]);
            for(let j = 0; j < 2; j++){
                if(grid[nh][2*j] != ""){
                    let val = parseFloat(grid[nh][2*j]);
                    if(!val.isNan){
                        kxy[nh][j] = Math.abs(val);
                    }
                }
                if(grid[nh][2*j+1] != ""){
                    let val = parseFloat(grid[nh][2*j+1]);
                    if(!val.isNan){
                        phase[nh][j] = val/180.0*Math.PI;
                    }
                }
                if(kxy[nh][j] > 0){
                    isnon0[j] = false;
                }
            }
        }
        for(let j = 0; j < 2; j++){
            if(isnon0[j]){
                kxy[0][j] = 1;
            }
        }
        let maxnh = 0;
        let ksum = [0, 0];
        for(let nh = 0; nh < grid.length; nh++){
            if(Math.hypot(kxy[nh][0], kxy[nh][1]) > 0){
                maxnh = nh;
            }
            for(let j = 0; j < 2; j++){
                ksum[j] += kxy[nh][j]*kxy[nh][j];
            }
        }
        for(let j = 0; j < 2; j++){
            ksum[j] = Math.sqrt(ksum[j]);
        }
        lu = srcobj[SrcPrmsLabel.lu[0]]*0.001; // mm -> m
        if(isf8){
            lu *= 2.0;
        }
        ku = 2*Math.PI/lu;
        let Kxy = srcobj[SrcPrmsLabel.Kxy[0]];
        let bcoef = 1/lu/COEF_K_VALUE;
        let Bpk = [];
        for(let nh = 0; nh < grid.length; nh++){
            for(let j = 0; j < 2; j++){
                kxy[nh][j] /= ksum[j];
                kxy[nh][j] *= Kxy[j];
            }
            Bpk.push([kxy[nh][0]*bcoef*(nh+1), kxy[nh][1]*bcoef*(nh+1)]);
        }
        npoints = (maxnh+1)*POINTSPERPER+1;
        let dlu = lu/(npoints-1);
        z = new Array(npoints);
        Bxy = [new Array(npoints), new Array(npoints)];
        for(let n = 0; n < npoints; n++){
            z[n] = dlu*n-lu*0.5;
            Bxy[0][n] = Bxy[1][n] = 0;
            for(let nh = 0; nh <= maxnh; nh++){
                let kunh = ku*(nh+1);
                for(let j = 0; j < 2; j++){
                    Bxy[j][n] += Bpk[nh][j]*Math.sin(kunh*z[n]+phase[nh][j]);
                }
            }
        }
    }
    else{
        let data;
        if(srctype == CUSTOM_Label){
            data = srcobj[SrcPrmsLabel.fvsz[0]].data;
        }
        else{
            data = srcobj[SrcPrmsLabel.fvsz1per[0]].data;
        }
        if(!Array.isArray(data)){
            return {power:0, flux:0, K:[0,0]};
        }
        if(data.length == 0){
            return {power:0, flux:0, K:[0,0]};
        }
        z = CopyJSON(data[0]);
        Bxy = [CopyJSON(data[1]), CopyJSON(data[2])];
        npoints = z.length;
        lu = z[npoints-1]-z[0];
        ku = 2*Math.PI/lu;
        if(npoints == 0 || npoints == 1){
            return {power:0, flux:0, K:[0,0]};
        }
        else if(npoints == 2){
            z.insert((z[0]+z[1])*0.5, 1);
            for(let j = 0; j < 2; j++){
                Bxy[j].insert((Bxy[j][0]+Bxy[j][1])*0.5, 1);
            }
            npoints++;
        }
    }

    let Tm2gt = COEF_K_VALUE*Math.PI*2.0;
    let Ixy = Integrate(z, Bxy, Tm2gt, true);
    let Isq = [new Array(npoints),new Array(npoints)];
    let Bsq = new Array(npoints);
    for(let n = 0; n < npoints; n++){
        for(let j = 0; j < 2; j++){
            Isq[j][n] = Ixy[j][n]**2;
        }
        Bsq[n] = Math.hypot(Bxy[0][n], Bxy[1][n])**2;
    }
    let Bsqa = Integrate(z, [Bsq], 1, false)[0];
    if(srctype == CUSTOM_Label){
        return {power:Bsqa[npoints-1], flux:0, Kxy:0};
    }

    let rz = Integrate(z, Isq, 1, false);
    let FxyR = [new Array(npoints), new Array(npoints)];
    let FxyI = [new Array(npoints), new Array(npoints)];

    let Kxy = [0, 0], K2 = 0;
    for(let j = 0; j < 2; j++){
        Kxy[j] = rz[j][npoints-1]/(z[npoints-1]-z[0]);
        K2 += Kxy[j];
        Kxy[j] = Math.sqrt(2*Kxy[j]);
    }
    for(let n = 0; n < npoints; n++){
        let psi = (z[n]+rz[0][n]+rz[1][n])/(1.0+K2)*ku;
        if(isf8){
            psi *= 2;
            // 2nd harmonic
        }
        for(let j = 0; j < 2; j++){
            FxyR[j][n] = Ixy[j][n]*Math.cos(psi);
            FxyI[j][n] = Ixy[j][n]*Math.sin(psi);
        }
    }
    let fxycoef = 2.0/lu/(1+K2);
    if(isf8){
        fxycoef *= 2;
        // 2nd harmonic
    }
    let FxyRa = Integrate(z, FxyR, fxycoef, false);
    let FxyIa = Integrate(z, FxyI, fxycoef, false);
    let flux = Math.hypot(
                FxyRa[0][npoints-1],
                FxyRa[1][npoints-1],
                FxyIa[0][npoints-1],
                FxyIa[1][npoints-1]
                )**2;
    
    // dump orbit for debugging
    /*
    let debugstr = "z\tbx\tby\tIx\tIy\trzx\trzy\n"
    for(let n = 0; n < npoints; n++){
        let debugline = z[n].toString();
        debugline += "\t"+Bxy[0][n].toString();
        debugline += "\t"+Bxy[1][n].toString();
        debugline += "\t"+Ixy[0][n].toString();
        debugline += "\t"+Ixy[1][n].toString();
        debugline += "\t"+rz[0][n].toString();
        debugline += "\t"+rz[1][n].toString();
        debugstr += debugline+"\n";
    }
    window.__TAURI__.tauri.invoke("write_file", { path: "debug.dat", data: debugstr});
    */

    return {power:Bsqa[npoints-1], flux:flux, Kxy:Kxy};
}

function AssignParameterSet(items, forcedisable = false)
{
    if(items != null){
        if(items.category == BLLabel){
            GUIConf.spectraobjs[CurrentLabel] = items.name;
        }
        else{
            GUIConf.spectraobjs[BLLabel][GUIConf.spectraobjs[CurrentLabel]][items.category] = items.name;
        }    
    }
    MainCategories.forEach(categ => {
        let target = GUIConf.spectraobjs[BLLabel][GUIConf.spectraobjs[CurrentLabel]][categ];
        if(!GUIConf.spectraobjs[categ].hasOwnProperty(target)){
            target = Object.keys(GUIConf.spectraobjs[categ])[0];
            GUIConf.spectraobjs[BLLabel][GUIConf.spectraobjs[CurrentLabel]][categ] = target;
        }
        GUIConf.GUIpanels[categ].JSONObj = GUIConf.spectraobjs[categ][target];
    });

    let accobj = GUIConf.GUIpanels[AccLabel].JSONObj;
    if(accobj[PartConfLabel] != null){
        GUIConf.GUIpanels[PartConfLabel].JSONObj = accobj[PartConfLabel];
        GUIConf.GUIpanels[PartConfLabel].SetPanel();
    }
    GUIConf.part_data = null;
    GUIConf.slice_prms = new Array(SliceTitles.length);
    if(accobj[AccPrmsLabel.bunchtype[0]] == CustomParticle){
        ImportParticle();
    }
    SetDisableCalcIDs(forcedisable);
}

function SetSelectionPrmSet()
{
    let categall = Array.from(MainCategories);
    categall.push(BLLabel);
    categall.forEach(categ => {
        Object.keys(GUIConf.spectraobjs[categ]).forEach(prm => {
            let id = [MenuLabels.prmset, categ, prm].join(IDSeparator);
            document.getElementById(id).classList.remove("fw-bold");
        });
    });

    let currbl = GUIConf.spectraobjs[CurrentLabel];
    let ids = [[MenuLabels.prmset, BLLabel, currbl].join(IDSeparator)];
    MainCategories.forEach(categ => {
        ids.push([MenuLabels.prmset, categ, GUIConf.spectraobjs[BLLabel][currbl][categ]].join(IDSeparator));
    });
    ids.forEach(id => {
        document.getElementById(id).classList.add("fw-bold");
    });
}

function SetMaterial()
{
    GUIConf.spectraobjs[FMaterialLabel] = CopyJSON(GUIConf.fmaterial.Custom);
    GUIConf.GUIpanels[ConfigLabel].SetMaterialName(GUIConf.fmaterial.GetMaterialNames());
}

// enable menu command
function SwithCalcIDs(calcids, enable)
{
    GUIConf.disabled = [];
    GUIConf.allmenus.forEach(item => {
        let id = item.split(IDSeparator).slice(1).join(IDSeparator);

        let found = false;
        for(const calcid of calcids){
            if(id == calcid){
                found = true;
            }
        }
        let disable = (!enable && found) || (enable && !found);
        
        if(document.getElementById(item).classList.contains("dropdown-item")){            
            if(disable){
                GUIConf.disabled.push(id);
                document.getElementById(item).setAttribute("disabled", true);
            }
            else{
                document.getElementById(item).removeAttribute("disabled");
            }
        }
        else{
            if(disable){
                GUIConf.disabled.push(id);
                document.getElementById(item).classList.add("d-none");
                document.getElementById(item).parentElement.classList.add("disabled");
            }
            else{
                document.getElementById(item).classList.remove("d-none");
                document.getElementById(item).parentElement.classList.remove("disabled");
            }    
        }
    });
}

// disable menu command
function SetDisableCalcIDs(forcedisable = false)
{
    let isenable = false;
    let disabled = [];
    if(GUIConf.mainid.includes(MenuLabels.wignerCMD)){
        disabled.push(MenuLabels.CMD);
        disabled.push([MenuLabels.CMD, MenuLabels.CMD2d].join(IDSeparator));
        isenable = true;
    }
    if(GUIConf.mainid.includes(MenuLabels.wignerProp)){
        disabled.push(MenuLabels.propagate);
        isenable = true;
    }
    if(GUIConf.fileid.includes(MenuLabels.CMDr)){
        disabled.push(MenuLabels.CMD);
        disabled.push([MenuLabels.CMD, MenuLabels.CMDPP].join(IDSeparator));
        isenable = true;
    }
    if(GUIConf.fileid.includes(MenuLabels.bunch)){
        disabled.push(MenuLabels.far);
        disabled.push(MenuLabels.near);
        disabled.push(MenuLabels.srcpoint);
        disabled.push(MenuLabels.CMD);
        disabled.push([MenuLabels.fixed, MenuLabels.far].join(IDSeparator));
        disabled.push([MenuLabels.fixed, MenuLabels.near].join(IDSeparator));
        disabled.push([MenuLabels.fixed, MenuLabels.wigner].join(IDSeparator));
    }
    if(disabled.length > 0){
        SwithCalcIDs(disabled, isenable);
        return;
    }

    let near_sp = GetIDFromItem(MenuLabels.near, MenuLabels.spatial, -1);
    let far_simp = GetIDFromItem(MenuLabels.far, 
            GetIDFromItem(MenuLabels.energy, MenuLabels.simpcalc, -1), -1);
    let far_sp = GetIDFromItem(MenuLabels.far, MenuLabels.spatial, -1);
    let src_wig = GetIDFromItem(MenuLabels.srcpoint, MenuLabels.wigner, -1);
    let src_wigK =  GetIDFromItem(src_wig, MenuLabels.Kvalue, -1);
    let far_K = GetIDFromItem(MenuLabels.far, MenuLabels.Kvalue, -1);
    
    let bunchtype = GUIConf.GUIpanels[AccLabel].JSONObj[AccPrmsLabel.bunchtype[0]];

    let srcobj = GUIConf.GUIpanels[SrcLabel].JSONObj;
    if(Is3DField(srcobj) || bunchtype == CustomParticle){
        disabled.push(MenuLabels.far);
        disabled.push(GetIDFromItem(near_sp, MenuLabels.vpdens, -1));
        disabled.push(GetIDFromItem(MenuLabels.fixed, MenuLabels.far, -1));
        let wigner = GetIDFromItem(MenuLabels.srcpoint, MenuLabels.wigner, -1);
        disabled.push(GetIDFromItem(wigner, MenuLabels.Kvalue, -1));    
    }
    let isseg = srcobj[SrcOptionsLabel.segment_type[0]] != NoneLabel;
    if(isseg){
        disabled.push(GetIDFromItem(far_sp, MenuLabels.pdensr, -1));
    }

    let srctype = srcobj[TypeLabel];
    if(srctype == CUSTOM_Label){
        disabled.push(MenuLabels.far);
        disabled.push(GetIDFromItem(MenuLabels.fixed, MenuLabels.far, -1));
        disabled.push(src_wigK);
    }
    else if(srctype == WLEN_SHIFTER_Label)
    {
        disabled.push(MenuLabels.far);
        disabled.push(MenuLabels.srcpoint);
        disabled.push(MenuLabels.cohrad);

        if(srctype == FIELDMAP3D_Label){
            disabled.push(GetIDFromItem(near_sp, MenuLabels.spdens, -1));
            disabled.push(GetIDFromItem(near_sp, MenuLabels.vpdens, -1));
        }

        disabled.push(GetIDFromItem(MenuLabels.fixed, MenuLabels.far, -1));
        disabled.push(GetIDFromItem(MenuLabels.fixed, MenuLabels.cohrad, -1));
        disabled.push(GetIDFromItem(MenuLabels.fixed, MenuLabels.wigner, -1));
        let fixed_near = GetIDFromItem(MenuLabels.fixed, MenuLabels.near, -1);
        if(srctype == FIELDMAP3D_Label){
            disabled.push(GetIDFromItem(fixed_near, MenuLabels.spdens, -1));
        }
    }
    else if(srctype == BM_Label){
        disabled.push(src_wigK);
        disabled.push(GetIDFromItem(far_sp, MenuLabels.pdensr, -1));
        let far_sp_flux = GetIDFromItem(far_sp, MenuLabels.fdensa, -1);
        let far_sp_power = GetIDFromItem(far_sp, MenuLabels.pdensa, -1);
        disabled.push(far_K);
        disabled.push(GetIDFromItem(far_sp_flux, MenuLabels.meshxy, -1));
        disabled.push(GetIDFromItem(far_sp_flux, MenuLabels.meshrphi, -1));
        disabled.push(GetIDFromItem(far_sp_power, MenuLabels.meshxy, -1));
        disabled.push(GetIDFromItem(far_sp_power, MenuLabels.meshrphi, -1));
        if(srcobj[SrcOptionsLabel.bmtandem[0]]){
            disabled.push(MenuLabels.far);
        }
    }
    else if(srctype == WIGGLER_Label || srctype == EMPW_Label){
        disabled.push(src_wigK);
        disabled.push(GetIDFromItem(far_sp, MenuLabels.pdensr, -1));
        disabled.push(far_K);
        disabled.push(GetIDFromItem(MenuLabels.near, MenuLabels.energy, -1));
        disabled.push(GetIDFromItem(near_sp, MenuLabels.fdenss, -1));
        disabled.push(GetIDFromItem(near_sp, MenuLabels.vpdens, -1));
        disabled.push(MenuLabels.cohrad);
        let fixnear = GetIDFromItem(MenuLabels.fixed, MenuLabels.near, -1);
        disabled.push(GetIDFromItem(fixnear, MenuLabels.fdenss, -1));
        disabled.push(GetIDFromItem(fixnear, MenuLabels.pflux, -1));
        disabled.push(GetIDFromItem(MenuLabels.fixed, MenuLabels.cohrad, -1));
        disabled.push(GetIDFromItem(MenuLabels.fixed, MenuLabels.wigner, -1));
    }
    else if(srctype == CUSTOM_PERIODIC_Label){
        disabled.push(far_simp);
        disabled.push(far_K);
        disabled.push(src_wigK);
    }
    else{
        disabled.push(far_simp);
        if(isseg){
            disabled.push(GetIDFromItem(far_K, MenuLabels.simpcalc, -1));
            disabled.push(src_wigK);
        }
        if(srcobj[SrcOptionsLabel.fielderr[0]] || srcobj[SrcOptionsLabel.phaseerr[0]])
        {
            disabled.push(MenuLabels.far);
            disabled.push(src_wigK);
        }
    }

    disabled.push(GetIDFromItem(MenuLabels.CMD, MenuLabels.CMD2d, -1))
    disabled.push(GetIDFromItem(MenuLabels.CMD, MenuLabels.CMDPP, -1))
    disabled.push(MenuLabels.CMD)
    disabled.push(MenuLabels.propagate)

    SwithCalcIDs(disabled, false);
    disabled.forEach(disableid => {
        if(GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel].includes(disableid)){
            if(forcedisable){
                // skip
            }
            else{
                GUIConf.GUIpanels[ConfigLabel].JSONObj[TypeLabel] = "";
            }
        }
    });   
}

// class to handle Gap/Field table
class GapFieldTable {
    constructor(src){
        this.m_src = src;        
        this.SetSourceOption();
        this.SetSrcObj();
    }

    IsApple(){
        return this.m_isapple;
    }
    
    SetSourceOption(){
        let srcobj = this.m_src.JSONObj;
        if(srcobj.hasOwnProperty(SrcPrmsLabel.phase[0]) == false){
            srcobj[SrcPrmsLabel.phase[0]] = 0;
        }
        if(srcobj.hasOwnProperty(SrcPrmsLabel.Kxy0[0]) == false){
            srcobj[SrcPrmsLabel.Kxy0[0]] = [0.7, 1.0];
        }        
        if(srcobj.hasOwnProperty(SrcPrmsLabel.apple[0]) == false){
            srcobj[SrcPrmsLabel.apple[0]] = false;
        }        
        let srccont = GetSrcContents(srcobj);
        this.m_isbxy = srccont.isbxy >= 0;
        this.m_isapple = srcobj[TypeLabel] == ELLIPTIC_UND_Label
                        && srcobj[SrcPrmsLabel.apple[0]];

        this.m_mainjxy = 1;
        if(srcobj[TypeLabel] == VERTICAL_UND_Label ||
                srcobj[TypeLabel] == VFIGURE8_UND_Label){
            this.m_mainjxy = 0;
        }
        else if(srcobj[TypeLabel] == FIGURE8_UND_Label){
            this.m_mainjxy = 1;
        }
        else if(this.m_isbxy){
            this.m_mainjxy = 
                srcobj[SrcPrmsLabel.Kxy[0]][0] > srcobj[SrcPrmsLabel.Kxy[0]][1] ? 0 : 1;
        }
        if(this.m_isapple){
            let csn = this.GetPhaseFactor();
            this.m_mainjxy = Math.abs(csn[0]) > Math.abs(csn[1]) ? 0 : 1;
        }
    }

    SetSrcObj(){
        let srcobj = this.m_src.JSONObj;
        this.SetSourceOption();
        this.m_gap = [];
        this.m_bxy = [[], []];
        let gaptbl = srcobj[SrcPrmsLabel.gaptbl[0]];

        if(typeof gaptbl == "undefined"){
            return;
        }
        if(Array.isArray(gaptbl.data) && gaptbl.data.length > 1){
            this.m_gap = [].concat(gaptbl.data[0]);
            this.m_bxy[0] = [].concat(gaptbl.data[1]);
            this.m_bxy[1] = [].concat(gaptbl.data[2]);
            this.SetBSquared();
        }
        if(this.m_gap.length > 0){
            this.m_mingap = this.m_gap.reduce((red,curr)=>curr<red?curr:red);
            this.m_maxgap = this.m_gap.reduce((red,curr)=>curr>red?curr:red);
        }
    }

    GetPhaseFactor(){
        let srcobj = this.m_src.JSONObj;
        let phi = Math.PI*2.0*srcobj[SrcPrmsLabel.phase[0]]
            /srcobj[SrcPrmsLabel.lu[0]];
        let csn = [0,0];
        csn[0] = Math.sin(phi);
        csn[1] = Math.cos(phi);
        for(let j = 0; j < 2; j++){
            if(Math.abs(csn[j]) < 1.0e-10){
                csn[j] = 0;
            }    
        }
        return csn;
    }

    SetBSquared(){
        let csn = [1, 1];
        if(this.m_isapple){
            csn = this.GetPhaseFactor();
        }
        let srcobj = this.m_src.JSONObj;
        if(srcobj[TypeLabel] == FIGURE8_UND_Label){
            csn[0] = 2;
        }
        else if(srcobj[TypeLabel] == VFIGURE8_UND_Label){
            csn[1] = 2;
        }
        else if(srcobj[TypeLabel] == LIN_UND_Label){
            csn[0] = 0;
        }
        else if(srcobj[TypeLabel] == VERTICAL_UND_Label){
            csn[1] = 0;
        }

        let bxy, bsq;
        this.m_bsq = [];
        bsq = this.m_bsq;
        bxy = this.m_bxy;
        for(let n = 0; n < bxy[0].length; n++){
            if(srcobj[TypeLabel] == HELICAL_UND_Label){
                bsq.push(bxy[1][n]*Math.sqrt(2));
            }
            else{
                bsq.push(Math.hypot(bxy[0][n]*csn[0], bxy[1][n]*csn[1]));
            }
        }
    }

    GetKCoef(){
        let srcobj = this.m_src.JSONObj;
        let kcoef = srcobj[SrcPrmsLabel.lu[0]]/1000.0*COEF_K_VALUE;
        let kcoefa = [kcoef, kcoef];
        if(srcobj[TypeLabel] == FIGURE8_UND_Label){
            kcoefa[0] *= 2.0;
        }
        if(srcobj[TypeLabel] == VFIGURE8_UND_Label){
            kcoefa[1] *= 2.0;
        }
        return kcoefa;
    }

    GetBpeak(){
        let srcobj = this.m_src.JSONObj;
        let Br = parseFloat(srcobj[SrcPrmsLabel.br[0]]);
        if(isNaN(Br) || Br <= 0){
            Br = 1.2;
        }

        let bpeak = [];
        for(let j = 0; j < 2; j++){
            let geo = parseFloat(srcobj[SrcPrmsLabel.geofactor[0]][j]);
            bpeak.push(COEF_BPEAK*Br*geo);
        }
        return bpeak;
    }

    GetGapKxy(item, jxy, tgtvalue)
    {
        let srcobj = this.m_src.JSONObj;
        let lu_mm = [srcobj[SrcPrmsLabel.lu[0]], srcobj[SrcPrmsLabel.lu[0]]];
        let if8 = -1;
        if(srcobj[TypeLabel] == FIGURE8_UND_Label){
            lu_mm[0] *= 2;
            if8 = 0;
        }
        else if(srcobj[TypeLabel] == VFIGURE8_UND_Label){
            lu_mm[1] *= 2;
            if8 = 1;
        }
        let Kpeak = [];
        let kcoef = this.GetKCoef();
        let bpeak = this.GetBpeak();
        for(let j = 0; j < 2; j++){
            Kpeak.push(bpeak[j]*kcoef[j]);
        }
        if(srcobj[TypeLabel] == LIN_UND_Label || 
                srcobj[TypeLabel] == WIGGLER_Label){
            Kpeak[0] = 0;
        }
        else if(srcobj[TypeLabel] == HELICAL_UND_Label){
            Kpeak[0] = Kpeak[1];
        }
        else if(srcobj[TypeLabel] == VERTICAL_UND_Label){
            Kpeak[1] = 0;
        }

        let csn;
        if(this.m_isapple){
            csn = this.GetPhaseFactor();
        }

        if(item == SrcPrmsLabel.gap[0]){
            for(let j = 0; j < 2; j++){
                if(this.m_isapple){
                    srcobj[SrcPrmsLabel.Kxy0[0]][j] 
                        = Kpeak[j]*Math.exp(-Math.PI*tgtvalue/lu_mm[j]);
                    srcobj[SrcPrmsLabel.Kxy[0]][j] 
                        = srcobj[SrcPrmsLabel.Kxy0[0]][j]*csn[j];
                }
                else{
                    srcobj[SrcPrmsLabel.Kxy[0]][j] 
                        = Kpeak[j]*Math.exp(-Math.PI*tgtvalue/lu_mm[j]);
                }
            }
            return;
        }
        else{
            if(tgtvalue == 0){
                srcobj[SrcPrmsLabel.gap[0]] = Infinity;
                if(this.m_isapple){
                    srcobj[SrcPrmsLabel.Kxy0[0]][1-jxy] = 0; 
                }
                else{
                    srcobj[SrcPrmsLabel.Kxy[0]][1-jxy] = 0; 
                }
                return;
            }
            else if(item == SrcPrmsLabel.e1st[0] || 
                    item == SrcPrmsLabel.lambda1[0]){
                let Kpeak0;
                if(this.m_isapple){
                    Kpeak0 = Math.hypot(Kpeak[0]*csn[0], Kpeak[1]*csn[1]);
                }
                else{
                    Kpeak0 = Math.hypot(Kpeak[0], Kpeak[1]);
                }
                if(if8 >= 0){
                    let K0 = Kpeak[if8];
                    let K1 = Kpeak[1-if8];
                    let frac = (-K0*K0+Math.sqrt(K0**4+4*(K1*tgtvalue)**2))/2/K1/K1;
                    srcobj[SrcPrmsLabel.gap[0]] = -Math.log(frac)*lu_mm[1-if8]/Math.PI;
                }
                else{
                    srcobj[SrcPrmsLabel.gap[0]] = -Math.log(tgtvalue/Kpeak0)*lu_mm[0]/Math.PI;
                }
                if(this.m_isapple){
                    srcobj[SrcPrmsLabel.Kxy0[0]][jxy] 
                        = Kpeak[jxy]*Math.exp(-Math.PI*srcobj[SrcPrmsLabel.gap[0]]/lu_mm[jxy]);
                }
                else{
                    srcobj[SrcPrmsLabel.Kxy[0]][jxy] 
                        = Kpeak[jxy]*Math.exp(-Math.PI*srcobj[SrcPrmsLabel.gap[0]]/lu_mm[jxy]);
                }
            }
            else{
                srcobj[SrcPrmsLabel.gap[0]] = -Math.log(tgtvalue/Kpeak[jxy])*lu_mm[jxy]/Math.PI;            
            }    
        }

        if(this.m_isapple){
            srcobj[SrcPrmsLabel.Kxy0[0]][1-jxy] 
                = Kpeak[1-jxy]*Math.exp(-Math.PI*srcobj[SrcPrmsLabel.gap[0]]/lu_mm[1-jxy]);
            for(let j = 0; j < 2; j++){
                srcobj[SrcPrmsLabel.Kxy[0]][j] 
                    = srcobj[SrcPrmsLabel.Kxy0[0]][j]*csn[j];
            }
        }
        else{
            srcobj[SrcPrmsLabel.Kxy[0]][1-jxy] 
                = Kpeak[1-jxy]*Math.exp(-Math.PI*srcobj[SrcPrmsLabel.gap[0]]/lu_mm[1-jxy]);
        }
    }

    GetGapKxyFromTable(item, jxy, tgtvalue)
    {
        let srcobj = this.m_src.JSONObj;
        let bsqarr, gaparr, bxyarr;
        bsqarr = this.m_bsq;
        gaparr = this.m_gap;
        bxyarr = this.m_bxy;

        let Kxy = [0, 0], gap;
        let kcoef = this.GetKCoef();
        if(item == SrcPrmsLabel.gap[0] || item == SrcPrmsLabel.type[0]){
            gap = tgtvalue;
        }
        else if(item == SrcPrmsLabel.e1st[0] 
                || item == SrcPrmsLabel.lambda1[0]){ // tgtvalue = sqrt(Kx^2+Ky^2)
            gap = SolveParabolic(gaparr, bsqarr, tgtvalue/kcoef[this.m_mainjxy]);
            srcobj[SrcPrmsLabel.gap[0]] = gap;
        }
        if(item == SrcPrmsLabel.gap[0] 
                || item == SrcPrmsLabel.e1st[0]
                || item == SrcPrmsLabel.lambda1[0]){
            for(let j = 0; j < 2; j++){
                Kxy[j] = GetParabolic(gaparr, bxyarr[j], gap)*kcoef[j];
            }
        }
        else{ // tgtvalue = Kx,y
            gap = SolveParabolic(gaparr, bxyarr[jxy], tgtvalue/kcoef[jxy]);
            if(isNaN(gap)){
                tgtvalue = NaN;            
            }
            srcobj[SrcPrmsLabel.gap[0]] = gap;
            Kxy[jxy] = tgtvalue;
            if(this.m_isbxy){
                Kxy[1-jxy] = GetParabolic(gaparr, bxyarr[1-jxy], gap)*kcoef[1-jxy];
            }
        }

        let dround = 1.0+1e-6;
        let isok = gap >= this.m_mingap/dround && gap <= this.m_maxgap*dround;
        if(this.m_isapple){
            let csn = this.GetPhaseFactor();
            for(let j = 0; j < 2; j++){
                srcobj[SrcPrmsLabel.Kxy0[0]][j] = Kxy[j];
                srcobj[SrcPrmsLabel.Kxy[0]][j] = Kxy[j]*csn[j];
            }
        }
        else{
            for(let j = 0; j < 2; j++){
                srcobj[SrcPrmsLabel.Kxy[0]][j] = Kxy[j];
            }
        }
        return isok;
    }

    UpdateGapField(item, jxy)
    {   
        let srcobj = this.m_src.JSONObj;
        let tgtvalue;
        let kcoef = this.GetKCoef();
        let srctype = srcobj[TypeLabel];

        jxy = jxy < 0 ? this.m_mainjxy : jxy;   
    
        let isauto = this.m_gap.length == 0 || 
            srcobj[SrcPrmsLabel.gaplink[0]] == AutomaticLabel;

        switch(item){
            case SrcPrmsLabel.apple[0]:
            case SrcPrmsLabel.type[0]:
                item = SrcPrmsLabel.gap[0];
            case SrcPrmsLabel.gap[0]:
                tgtvalue = srcobj[SrcPrmsLabel.gap[0]];
                break;
            case SrcPrmsLabel.b[0]:
                tgtvalue = srcobj[SrcPrmsLabel.b[0]]*kcoef[this.m_mainjxy];
                srcobj[SrcPrmsLabel.Kxy[0]][jxy] = tgtvalue;
                break;
            case SrcPrmsLabel.bxy[0]:
                tgtvalue = srcobj[SrcPrmsLabel.bxy[0]][jxy]*kcoef[jxy];
                srcobj[SrcPrmsLabel.Kxy[0]][jxy] = tgtvalue;
                break;
            case SrcPrmsLabel.Kxy[0]:
                tgtvalue = srcobj[SrcPrmsLabel.Kxy[0]][jxy];
                break;
            case SrcPrmsLabel.Kxy0[0]:
                tgtvalue = srcobj[SrcPrmsLabel.Kxy0[0]][jxy];
                break;
            case SrcPrmsLabel.e1st[0]:
            case SrcPrmsLabel.lambda1[0]:
                tgtvalue = srcobj[SrcPrmsLabel.Kperp[0]];
                break;
        }

        let isok = true;
        if(item == SrcPrmsLabel.phase[0]){
            let csn = this.GetPhaseFactor();
            for(let j = 0; j < 2; j++){
                srcobj[SrcPrmsLabel.Kxy[0]][j] = srcobj[SrcPrmsLabel.Kxy0[0]][j]*csn[j];
            }
        }
        else if(srcobj[SrcPrmsLabel.gaplink[0]] == NoneLabel){
            if(item == SrcPrmsLabel.b[0]){
                srcobj[SrcPrmsLabel.Kxy[0]][this.m_mainjxy] 
                    = srcobj[SrcPrmsLabel.b[0]]*kcoef[this.m_mainjxy];
                return;
            }
            else if(item == SrcPrmsLabel.bxy[0]){
                srcobj[SrcPrmsLabel.Kxy[0]][jxy] 
                    = srcobj[SrcPrmsLabel.bxy[0]][jxy]*kcoef[jxy];
                return;
            }
            else if(item == SrcPrmsLabel.Kxy[0]){
                srcobj[SrcPrmsLabel.bxy[0]][jxy] 
                    = srcobj[SrcPrmsLabel.Kxy[0]][jxy]/kcoef[jxy];
            }
            else if(item == SrcPrmsLabel.Kxy0[0]){
                let csn = this.GetPhaseFactor();
                srcobj[SrcPrmsLabel.Kxy[0]][jxy] 
                    = srcobj[SrcPrmsLabel.Kxy0[0]][jxy]*csn[jxy];
            }
            else if(item == SrcPrmsLabel.e1st[0] || 
                    item == SrcPrmsLabel.lambda1[0]){
                let kxyr;
                if(srctype == LIN_UND_Label){
                    kxyr = [0, 1];
                }
                else if(srctype == VERTICAL_UND_Label){
                    kxyr = [1, 0];
                }
                else if(srctype == HELICAL_UND_Label){
                    kxyr = [1/Math.sqrt(2), 1/Math.sqrt(2)];
                }
                else{
                    let phi = Math.atan2(srcobj[SrcPrmsLabel.Kxy[0]][1], 
                        srcobj[SrcPrmsLabel.Kxy[0]][0]);
                    kxyr = [Math.cos(phi), Math.sin(phi)];
                }       

                let Kperp = srcobj[SrcPrmsLabel.Kperp[0]];
                srcobj[SrcPrmsLabel.b[0]] = Kperp/kcoef[this.m_mainjxy];
                for(let j = 0; j < 2; j++){
                    srcobj[SrcPrmsLabel.Kxy[0]][j] = Kperp*kxyr[j];
                }
                if(this.m_isapple){
                    let csn = this.GetPhaseFactor();
                    let islin = false;
                    for(let j = 0; j < 2; j++){
                        if(Math.abs(csn[j]) < 1.0e-10){
                            srcobj[SrcPrmsLabel.Kxy[0]][j] = 
                            srcobj[SrcPrmsLabel.Kxy0[0]][j] = Kperp;
                            islin = true;
                        }    
                    }
                    if(islin == false){
                        srcobj[SrcPrmsLabel.Kxy0[0]][0] = 
                            srcobj[SrcPrmsLabel.Kxy[0]][0]/csn[0];
                        srcobj[SrcPrmsLabel.Kxy0[0]][1] = 
                            srcobj[SrcPrmsLabel.Kxy[0]][0]/csn[1];
                    }
                }
            }
        }
        else if(isauto){
            this.GetGapKxy(item, jxy, tgtvalue);
        }
        else{
            isok = this.GetGapKxyFromTable(item, jxy, tgtvalue);
        }

        if(srctype == LIN_UND_Label){
            srcobj[SrcPrmsLabel.Kxy[0]][0] = 0;
        }
        else if(srctype == VERTICAL_UND_Label){
            srcobj[SrcPrmsLabel.Kxy[0]][1] = 0;
        }
        else if(srctype == HELICAL_UND_Label){
            srcobj[SrcPrmsLabel.Kxy[0]][0] = srcobj[SrcPrmsLabel.Kxy[0]][1];
        }
    
        srcobj[SrcPrmsLabel.b[0]] = 
            srcobj[SrcPrmsLabel.Kxy[0]][this.m_mainjxy]/kcoef[this.m_mainjxy];
        for(let j = 0; j < 2; j++){
            srcobj[SrcPrmsLabel.bxy[0]][j] = srcobj[SrcPrmsLabel.Kxy[0]][j]/kcoef[j];
        }
        return isok;
    }
}

// class to update GUI panels
class Updater {
    constructor(acc, src, config, outfile, gaptbl){
        this.m_acc = acc;
        this.m_src = src;
        this.m_config = config;
        this.m_outfile = outfile;
        this.m_gaptbl = gaptbl;
        this.m_deflu = this.m_src.JSONObj[SrcPrmsLabel.lu[0]];
    }

    Create(){
        this.m_gaptbl.SetSrcObj();
        this.Update();
        this.m_acc.SetPanel();
        this.m_src.SetPanel();
        this.m_config.SetPanel();
        this.m_outfile.SetPanel();
    }

    Update(id = null)
    {
        if(id == null){
            this.UpdateAcc(GetIDFromItem(AccLabel, UpdateAll, -1));
        }
        else{
            let item = GetItemFromID(id);
            if(item.categ == AccLabel){
                this.UpdateAcc(id);
            }
            else if(item.categ == SrcLabel){
                this.UpdateLightSrc(id);
            }
            else if(item.categ == ConfigLabel){
                this.UpdateConfig()
            }
        }
    }    

    UpdateAcc(id)
    {
        let issrc = false, isconf = false;
        let idc = GetItemFromID(id);
        let prmlabel = idc.item;        
        switch(prmlabel){
            case AccPrmsLabel.eGeV[0]:
            case AccPrmsLabel.emitt[0]:
            case AccPrmsLabel.coupl[0]:
            case AccPrmsLabel.espread[0]:
            case AccPrmsLabel.beta[0]:
            case AccPrmsLabel.alpha[0]:
            case AccPrmsLabel.eta[0]:
            case AccPrmsLabel.etap[0]:
            case AccPrmsLabel.bunchtype[0]:
            case UpdateAll:
                isconf = true;
            case AccPrmsLabel.type[0]:
            case AccPrmsLabel.imA[0]:
            case AccPrmsLabel.cirm[0]:
            case AccPrmsLabel.bunches[0]:
            case AccPrmsLabel.pulsepps[0]:
            case AccPrmsLabel.bunchlength[0]:
            case AccPrmsLabel.bunchcharge[0]:
                issrc = true;
                break;
        }
        
        let indices = [];
        let accobj = this.m_acc.JSONObj;
        let bufmap = {
            [AccPrmsLabel.eGeV[0]]: AccPrmsLabel.buf_eGeV[0],
            [AccPrmsLabel.bunchlength[0]]: AccPrmsLabel.buf_bunchlength[0],
            [AccPrmsLabel.bunchcharge[0]]: AccPrmsLabel.buf_bunchcharge[0],
            [AccPrmsLabel.espread[0]]: AccPrmsLabel.buf_espread[0],
        };
        if(accobj[AccPrmsLabel.bunchtype[0]] != GaussianLabel){
            if(accobj[AccPrmsLabel.buf_eGeV[0]] == null){
                Object.keys(bufmap).forEach(key => {
                    accobj[bufmap[key]] = [accobj[key], accobj[key]];
                })
            }
        }
        if(accobj[AccPrmsLabel.bunchtype[0]] == CustomParticle 
                && GUIConf.part_data == null && GetParticleDatapath() != ""){
            ImportParticle();
            return;
        }

        if(prmlabel == AccPrmsLabel.bunchtype[0]){
            let jxy = accobj[AccPrmsLabel.bunchtype[0]] == CustomParticle ? 1 : 0;
            Object.keys(bufmap).forEach(key => {
                accobj[key] = accobj[bufmap[key]][jxy];
            })
            indices.push(AccPrmsLabel.eGeV[0]);
            indices.push(AccPrmsLabel.bunchlength[0]);
            indices.push(AccPrmsLabel.bunchcharge[0]);
            indices.push(AccPrmsLabel.espread[0]);
        }
        if(prmlabel == AccPrmsLabel.eGeV[0] || prmlabel == UpdateAll 
                || prmlabel == AccPrmsLabel.bunchtype[0])
        {
            accobj[AccPrmsLabel.gaminv[0]] = 
                1.0/(accobj[AccPrmsLabel.eGeV[0]]/MC2MeV);
            indices.push(AccPrmsLabel.gaminv[0]);
        }

        let charge;
        if(accobj[AccPrmsLabel.bunchtype[0]] == CustomParticle){
            Object.keys(bufmap).forEach(key => {
                accobj[key] = accobj[bufmap[key]][1];
            })
            if(accobj[PartConfLabel] == null){
                accobj[PartConfLabel] = GUIConf.GUIpanels[PartConfLabel].JSONObj;
            }
            charge = accobj[AccPrmsLabel.bunchcharge[0]]*1.0e-9;
            accobj[AccPrmsLabel.aimA[0]] = charge*accobj[AccPrmsLabel.pulsepps[0]]*1000.0;
            indices.push(AccPrmsLabel.aimA[0]);
            indices.push(AccPrmsLabel.eGeV[0]);
            if(accobj[TypeLabel] == LINACLabel){
                indices.push(AccPrmsLabel.aimA[0]);
            }
            indices.push(AccPrmsLabel.bunchlength[0]);
            indices.push(AccPrmsLabel.bunchcharge[0]);
            indices.push(AccPrmsLabel.espread[0]);
            indices.push(AccPrmsLabel.peakcurr[0]);
            indices.push(AccPrmsLabel.emitt[0]);
            indices.push(AccPrmsLabel.coupl[0]);
            indices.push(AccPrmsLabel.beta[0]);
            indices.push(AccPrmsLabel.alpha[0]);
        }
        switch(prmlabel){
            case AccPrmsLabel.emitt[0]:
            case AccPrmsLabel.coupl[0]:
            case AccPrmsLabel.espread[0]:
            case AccPrmsLabel.beta[0]:
            case AccPrmsLabel.alpha[0]:
            case AccPrmsLabel.eta[0]:
            case AccPrmsLabel.etap[0]:
            case AccPrmsLabel.bunchtype[0]:
            case UpdateAll:
                accobj[AccPrmsLabel.epsilon[0]][0] 
                    = accobj[AccPrmsLabel.emitt[0]]/(1.0+accobj[AccPrmsLabel.coupl[0]]);
                accobj[AccPrmsLabel.epsilon[0]][1] 
                    = accobj[AccPrmsLabel.epsilon[0]][0]*accobj[AccPrmsLabel.coupl[0]];
                let espread = accobj[AccPrmsLabel.espread[0]];
                for(let j = 0; j < 2; j++){
                    let nemitt = accobj[AccPrmsLabel.epsilon[0]][j];
                    let alpha = accobj[AccPrmsLabel.alpha[0]][j];
                    let beta = accobj[AccPrmsLabel.beta[0]][j];
                    let eta =  accobj[AccPrmsLabel.eta[0]][j];
                    let etap = accobj[AccPrmsLabel.etap[0]][j];
                    accobj[AccPrmsLabel.sigma[0]][j]
                        = Math.sqrt(beta*nemitt+(espread*eta)**2)*1000.0;
                    accobj[AccPrmsLabel.sigmap[0]][j] 
                        = Math.sqrt((1.0+alpha**2)*nemitt/beta+(espread*etap)**2)*1000.0;
                }
                indices.push(AccPrmsLabel.epsilon[0]);
                indices.push(AccPrmsLabel.sigma[0]);
                indices.push(AccPrmsLabel.sigmap[0]);
                break;
        }
        if(accobj[AccPrmsLabel.bunchtype[0]] != CustomParticle){
            if(accobj[TypeLabel] == RINGLabel){
                switch(prmlabel){
                    case AccPrmsLabel.imA[0]:
                    case AccPrmsLabel.cirm[0]:
                    case AccPrmsLabel.bunches[0]:
                    case AccPrmsLabel.bunchlength[0]:
                    case UpdateAll:
                        let pulserate = 
                                CC/accobj[AccPrmsLabel.cirm[0]]*accobj[AccPrmsLabel.bunches[0]];
                        charge = accobj[AccPrmsLabel.imA[0]]*1.0e-3/pulserate;
                        indices.push(AccPrmsLabel.peakcurr[0]);
                        break;
                }        
            }
            else{
                switch(prmlabel){
                    case AccPrmsLabel.type[0]:
                    case AccPrmsLabel.pulsepps[0]:
                    case AccPrmsLabel.bunchcharge[0]:
                    case AccPrmsLabel.bunchlength[0]:
                    case UpdateAll:
                        charge = accobj[AccPrmsLabel.bunchcharge[0]]*1.0e-9;
                        accobj[AccPrmsLabel.aimA[0]] = charge*accobj[AccPrmsLabel.pulsepps[0]]*1000.0;
                        indices.push(AccPrmsLabel.peakcurr[0]);
                        indices.push(AccPrmsLabel.aimA[0]);
                        break;
                }    
            }    
            if(indices.includes(AccPrmsLabel.peakcurr[0])){
                accobj[AccPrmsLabel.peakcurr[0]] = 
                    charge/Math.sqrt(2.0*Math.PI)/
                    (accobj[AccPrmsLabel.bunchlength[0]]*1.0e-3/CC);
            }    
        }

        for(let j = 0; j < indices.length; j++){
            this.m_acc.RefreshItem(indices[j]);
        }
    
        if(issrc){
            let idsrc;
            if(prmlabel == UpdateAll|| prmlabel == AccPrmsLabel.bunchtype[0]){
                idsrc = GetIDFromItem(SrcLabel, UpdateAll, -1);
            }
            else if(isconf){
                idsrc = GetIDFromItem(SrcLabel, UpdateBeam, -1);
            }
            else{
                idsrc = GetIDFromItem(SrcLabel, UpdateCurr, -1);
            }
            this.UpdateLightSrc(idsrc);
        }
        else if(isconf && prmlabel != UpdateAll){
            this.UpdateConfig();
        }
    }

    UpdateLightSrc(id)
    {
        let srcobj = this.m_src.JSONObj;
        let accobj = this.m_acc.JSONObj;
        let srctype = srcobj[TypeLabel];
        let eGeV = accobj[AccPrmsLabel.eGeV[0]];
        let gaminv_mrad = accobj[AccPrmsLabel.gaminv[0]];
        let iA = accobj[TypeLabel] == RINGLabel ? 
                    accobj[AccPrmsLabel.imA[0]] : accobj[AccPrmsLabel.aimA[0]];
        let nharm = (srctype == FIGURE8_UND_Label 
                    || srctype == VFIGURE8_UND_Label) ? 0.5 : 1.0;
        iA /= 1000.0;
    
        let isready = IsDataReady(srcobj);
        let uprms = {power:0, flux:0, Kxy:[0,0]};
    
        let isconf = false;
        let idc = GetItemFromID(id);
        let prmlabel = idc.item;
        let jxy = idc.jxy;
        let indices = [];
        if(prmlabel == UpdateAll){ // add properties with an array
            srcobj[SrcPrmsLabel.sigmar[0]] = [0,0];
            srcobj[SrcPrmsLabel.sigmarx[0]] = [0,0];
            srcobj[SrcPrmsLabel.sigmary[0]] = [0,0];
            srcobj[SrcPrmsLabel.Sigmax[0]] = [0,0];
            srcobj[SrcPrmsLabel.Sigmay[0]] = [0,0];
        }
        if(srctype == CUSTOM_Label){
            if(isready){
                uprms = GetUprmArb(srcobj);
            }
            srcobj[SrcPrmsLabel.tpower[0]] = 
                COEF_TOTAL_POWER_ID*(eGeV**2)*iA
                *(COEF_K_VALUE*COEF_K_VALUE*4.0*uprms.power);
            indices.push(SrcPrmsLabel.tpower[0]);
            this.UpdateSrcIndices(indices);
            return;
        }
        if(srctype == BM_Label){
            if(prmlabel == SrcPrmsLabel.bendlength[0] 
                    || prmlabel == SrcPrmsLabel.fringelen[0]){
                this.UpdateSrcIndices(indices);
                return;
            }
            if(prmlabel == SrcPrmsLabel.b[0] || prmlabel == UpdateAll){
                srcobj[SrcPrmsLabel.radius[0]] 
                    = COEF_BM_RADIUS*eGeV/srcobj[SrcPrmsLabel.b[0]];
                indices.push(SrcPrmsLabel.radius[0]);
            }
            else{
                srcobj[SrcPrmsLabel.b[0]]
                = COEF_BM_RADIUS*eGeV/srcobj[SrcPrmsLabel.radius[0]];
                indices.push(SrcPrmsLabel.b[0]);
            }
            srcobj[SrcPrmsLabel.ec[0]] = COEF_EC*(eGeV**2)*srcobj[SrcPrmsLabel.b[0]];
            srcobj[SrcPrmsLabel.lc[0]] = ONE_ANGSTROM_eV/srcobj[SrcPrmsLabel.ec[0]]*0.1;
            srcobj[SrcPrmsLabel.linpower[0]]
                = COEF_LINPWD*iA*(eGeV**3)*srcobj[SrcPrmsLabel.b[0]];
            srcobj[SrcPrmsLabel.tpowerrev[0]] 
                = srcobj[SrcPrmsLabel.linpower[0]]*Math.PI*2.0*1000.0;
            indices.push(SrcPrmsLabel.ec[0]);
            indices.push(SrcPrmsLabel.lc[0]);
            indices.push(SrcPrmsLabel.tpowerrev[0]);
            indices.push(SrcPrmsLabel.linpower[0]);
            this.UpdateSrcIndices(indices);
            return;
        }
        if(srctype == WLEN_SHIFTER_Label){
            if(prmlabel == SrcPrmsLabel.bmain[0] || 
                    prmlabel == SrcPrmsLabel.mplength[0] ||
                    prmlabel == SrcPrmsLabel.subpolel[0] || prmlabel == UpdateAll)
            {
                srcobj[SrcPrmsLabel.subpoleb[0]] = 
                    srcobj[SrcPrmsLabel.bmain[0]]*srcobj[SrcPrmsLabel.mplength[0]]
                    /(2*srcobj[SrcPrmsLabel.subpolel[0]]);
                indices.push(SrcPrmsLabel.subpoleb[0]);
            }
            else if(prmlabel == SrcPrmsLabel.subpoleb[0]){
                srcobj[SrcPrmsLabel.subpolel[0]] = 
                    srcobj[SrcPrmsLabel.bmain[0]]*srcobj[SrcPrmsLabel.mplength[0]]
                    /(2*srcobj[SrcPrmsLabel.subpoleb[0]]);
                indices.push(SrcPrmsLabel.subpolel[0]);
            }
            srcobj[SrcPrmsLabel.tpower[0]] = (COEF_K_VALUE**2)*4.0*(
                (srcobj[SrcPrmsLabel.bmain[0]]**2)*srcobj[SrcPrmsLabel.mplength[0]]+
                (srcobj[SrcPrmsLabel.subpoleb[0]]**2)*srcobj[SrcPrmsLabel.subpolel[0]]*2.0)
                *COEF_TOTAL_POWER_ID*(eGeV**2)*iA;
            srcobj[SrcPrmsLabel.ec[0]] = COEF_EC*(eGeV**2)*srcobj[SrcPrmsLabel.bmain[0]];
            srcobj[SrcPrmsLabel.lc[0]] = ONE_ANGSTROM_eV/srcobj[SrcPrmsLabel.ec[0]]*0.1;
            indices.push(SrcPrmsLabel.tpower[0]);
            indices.push(SrcPrmsLabel.ec[0]);
            indices.push(SrcPrmsLabel.lc[0]);
    
            this.UpdateSrcIndices(indices);
            return;
        }
    
        let iscustomu = 
            srctype == FIGURE8_UND_Label ||
            srctype == VFIGURE8_UND_Label ||
            srctype == CUSTOM_PERIODIC_Label ||
            srctype == MULTI_HARM_UND_Label;
    
        let srccont = GetSrcContents(srcobj);
    
        if(srctype == CUSTOM_PERIODIC_Label){
            if(isready){
                if(prmlabel == SrcPrmsLabel.fvsz1per[0]){
                    indices.push(SrcPrmsLabel.lu[0]);
                    indices.push(SrcPrmsLabel.Kperp[0]);
                }
                let np = srcobj[SrcPrmsLabel.fvsz1per[0]].data[0].length;
                srcobj[SrcPrmsLabel.lu[0]] = 
                    (srcobj[SrcPrmsLabel.fvsz1per[0]].data[0][np-1]
                    -srcobj[SrcPrmsLabel.fvsz1per[0]].data[0][0])*1000.0; // m -> mm
            }
            else{
                srcobj[SrcPrmsLabel.lu[0]] = this.m_deflu;
            }
        }

        if(prmlabel == SrcPrmsLabel.type[0] || prmlabel == SrcPrmsLabel.apple[0]){
            this.m_gaptbl.SetSrcObj();
        }
    
        let islength = false;
        let lu = srcobj[SrcPrmsLabel.lu[0]]/1000.0;
        if(prmlabel == SrcPrmsLabel.devlength[0] 
                || prmlabel == SrcPrmsLabel.lu[0]
                || prmlabel == SrcPrmsLabel.segments[0]
                || prmlabel == SrcPrmsLabel.hsegments[0]
                || prmlabel == SrcPrmsLabel.fvsz1per[0]
                || prmlabel == SrcPrmsLabel.endmag[0]
                || prmlabel == SrcPrmsLabel.type[0]
                || prmlabel == UpdateAll){
    
            //!! definition of N should be consistent with solver
            if(srccont.iswiggler >= 0){
                let poles = Math.floor(srcobj[SrcPrmsLabel.devlength[0]]/(lu/2.0)+1.0e-6);
                srcobj[SrcPrmsLabel.periods[0]] = poles/2;
            }
            else{
                srcobj[SrcPrmsLabel.periods[0]]
                    = Math.floor(srcobj[SrcPrmsLabel.devlength[0]]/(lu/nharm)+1.0e-6);
                }
            if(srcobj[SrcPrmsLabel.endmag[0]]){
                srcobj[SrcPrmsLabel.periods[0]] -= 2;
            }
            else{
                srcobj[SrcPrmsLabel.periods[0]] -= 1;
            }
            if(srccont.iswiggler < 0){
                srcobj[SrcPrmsLabel.periods[0]] = Math.floor(srcobj[SrcPrmsLabel.periods[0]]/nharm);
            }
            srcobj[SrcPrmsLabel.reglength[0]]
                = srcobj[SrcPrmsLabel.periods[0]]*lu;
            indices.push(SrcPrmsLabel.reglength[0]);
            indices.push(SrcPrmsLabel.periods[0]);
            islength = true;
        }
    
        if(prmlabel == SrcPrmsLabel.br[0] || prmlabel == SrcPrmsLabel.geofactor[0]){
            prmlabel = SrcPrmsLabel.gap[0];
        }
    
        let isfield = false;
        switch(prmlabel){
            case SrcPrmsLabel.type[0]:
            case SrcPrmsLabel.gap[0]:
            case SrcPrmsLabel.bxy[0]:
            case SrcPrmsLabel.b[0]:
            case SrcPrmsLabel.lu[0]:
            case SrcPrmsLabel.Kxy[0]:
            case SrcPrmsLabel.K[0]:
            case SrcPrmsLabel.Kxy0[0]:
            case SrcPrmsLabel.phase[0]:
            case SrcPrmsLabel.e1st[0]:
            case SrcPrmsLabel.lambda1[0]:
            case SrcPrmsLabel.multiharm:
            case SrcPrmsLabel.fvsz1per[0]:
            case SrcPrmsLabel.apple[0]:
            case UpdateAll:
                isfield = true;
                isconf = true;
                break;
        }
    
        if(prmlabel == SrcPrmsLabel.phase[0]){
            this.m_gaptbl.SetBSquared();
        }
        if(prmlabel == SrcPrmsLabel.K[0] || prmlabel == UpdateAll || prmlabel == SrcPrmsLabel.lu[0]){
            if(this.m_gaptbl.IsApple()){
                prmlabel = SrcPrmsLabel.Kxy0[0];
            }
            else{
                prmlabel = SrcPrmsLabel.Kxy[0];
            }
            if(srctype == LIN_UND_Label ||  
                    srctype == WIGGLER_Label){
                srcobj[SrcPrmsLabel.Kxy[0]][0] = 0;
                srcobj[SrcPrmsLabel.Kxy[0]][1] = srcobj[SrcPrmsLabel.K[0]];
            }
            else if(srctype == VERTICAL_UND_Label){
                srcobj[SrcPrmsLabel.Kxy[0]][0] = srcobj[SrcPrmsLabel.K[0]];
                srcobj[SrcPrmsLabel.Kxy[0]][1] = 0;
            }
            else if(srctype == HELICAL_UND_Label){
                srcobj[SrcPrmsLabel.Kxy[0]][0] = srcobj[SrcPrmsLabel.K[0]];
                srcobj[SrcPrmsLabel.Kxy[0]][1] = srcobj[SrcPrmsLabel.K[0]];
            }
        }
        if(prmlabel == SrcPrmsLabel.e1st[0] || prmlabel == SrcPrmsLabel.lambda1[0]){
            if(prmlabel == SrcPrmsLabel.lambda1[0]){
                srcobj[SrcPrmsLabel.e1st[0]] = ONE_ANGSTROM_eV/srcobj[SrcPrmsLabel.lambda1[0]]*0.1;
            }
            let K2 = COEF_E1ST*(eGeV**2)/srcobj[SrcPrmsLabel.e1st[0]]/lu-1.0;
            if(K2 <= 0){
                srcobj[SrcPrmsLabel.Kperp[0]] = 0;
            }
            else{
                srcobj[SrcPrmsLabel.Kperp[0]] = Math.sqrt(2*K2);
            }
            if(srctype == MULTI_HARM_UND_Label){
                let karg;
                if(Math.hypot(srcobj[SrcPrmsLabel.Kxy[0]][1], srcobj[SrcPrmsLabel.Kxy[0]][0]) == 0){
                    karg = 0;
                }
                else{
                    karg = Math.atan2(srcobj[SrcPrmsLabel.Kxy[0]][1], srcobj[SrcPrmsLabel.Kxy[0]][0]);
                }
                srcobj[SrcPrmsLabel.Kxy[0]][0] = srcobj[SrcPrmsLabel.Kperp[0]]*Math.cos(karg);
                srcobj[SrcPrmsLabel.Kxy[0]][1] = srcobj[SrcPrmsLabel.Kperp[0]]*Math.sin(karg);
                indices.push(SrcPrmsLabel.Kxy[0]);
            }
        }
        let Nper = srcobj[SrcPrmsLabel.periods[0]];
        if(srctype == FIGURE8_UND_Label ||
                srctype == VFIGURE8_UND_Label){
            Nper /= 2;
        }
        let segtype = srcobj[SrcPrmsLabel.segment_type[0]];
        let Mseg = 1;
        if(srccont.iswiggler < 0 && segtype != NoneLabel){
            if(segtype == IdenticalLabel){
                Mseg = srcobj[SrcPrmsLabel.segments[0]];
            }
            else{
                Mseg = 2*srcobj[SrcPrmsLabel.hsegments[0]];
            }
            Nper *= Mseg;
        }
    
        if(isfield || islength || prmlabel == UpdateBeam){
            if(iscustomu){
                if(isfield){
                    if(srctype == FIGURE8_UND_Label 
                            || srctype == VFIGURE8_UND_Label){
                        let isok = this.m_gaptbl.UpdateGapField(prmlabel, jxy);
                        indices.push([SrcPrmsLabel.gap[0], {color:isok?"black":"red"}]);
                        indices.push(SrcPrmsLabel.bxy[0]);
                        indices.push(SrcPrmsLabel.Kxy[0]);
                        indices.push(SrcPrmsLabel.Kperp[0]);    
                    }
                    else if(srctype == MULTI_HARM_UND_Label){
                        indices.push(SrcPrmsLabel.Kperp[0]);
                    }
                }
                if(isready){
                    uprms = GetUprmArb(srcobj);
                }
                if(srctype == CUSTOM_PERIODIC_Label){
                    srcobj[SrcPrmsLabel.Kxy[0]] = uprms.Kxy;
                    indices.push(SrcPrmsLabel.Kxy[0]);
                }
                srcobj[SrcPrmsLabel.tpower[0]] = 
                    COEF_TOTAL_POWER_ID*(eGeV**2)*iA
                    *(COEF_K_VALUE*COEF_K_VALUE*4.0*uprms.power*Nper);
                indices.push(SrcPrmsLabel.tpower[0]);
            }
            else if(isfield){
                let isok = this.m_gaptbl.UpdateGapField(prmlabel, jxy);
                indices.push([SrcPrmsLabel.gap[0], {color:isok?"black":"red"}]);
                indices.push(SrcPrmsLabel.bxy[0]);
                indices.push(SrcPrmsLabel.Kxy0[0]);
                indices.push(SrcPrmsLabel.Kxy[0]);
                indices.push(SrcPrmsLabel.b[0]);
                indices.push(SrcPrmsLabel.Kperp[0]);
                indices.push(SrcPrmsLabel.K[0]);    
            }
            if(srctype == LIN_UND_Label ||
                    srctype == HELICAL_UND_Label ||
                    srctype == WIGGLER_Label){
                srcobj[SrcPrmsLabel.K[0]] = srcobj[SrcPrmsLabel.Kxy[0]][1];
            }
            else if(srctype == VERTICAL_UND_Label){
                srcobj[SrcPrmsLabel.K[0]] = srcobj[SrcPrmsLabel.Kxy[0]][0];
            }
            let Kx =  Math.abs(srcobj[SrcPrmsLabel.Kxy[0]][0]);
            let Ky =  Math.abs(srcobj[SrcPrmsLabel.Kxy[0]][1]);
            if(prmlabel != SrcPrmsLabel.e1st[0] && prmlabel != SrcPrmsLabel.lambda1[0]){
                srcobj[SrcPrmsLabel.Kperp[0]] = Math.hypot(Kx, Ky);
            }
            if(srccont.ise1st >= 0){
                srcobj[SrcPrmsLabel.e1st[0]] 
                    = COEF_E1ST*(eGeV**2)/lu/(1+srcobj[SrcPrmsLabel.Kperp[0]]**2/2);
                srcobj[SrcPrmsLabel.lambda1[0]] 
                    = ONE_ANGSTROM_eV/srcobj[SrcPrmsLabel.e1st[0]]*0.1;
    
                let lambda = srcobj[SrcPrmsLabel.lambda1[0]]*1e-9;
                let srcdiv = Math.sqrt(lambda/2/(Mseg*srcobj[SrcPrmsLabel.reglength[0]])); 
                let srcsize = lambda/4/Math.PI/srcdiv;
                srcobj[SrcPrmsLabel.sigmar[0]] = [srcsize, srcdiv];
                srcobj[SrcPrmsLabel.sigmar[0]][0] *= 1000.0;
                srcobj[SrcPrmsLabel.sigmar[0]][1] *= 1000.0;
    
                indices.push(SrcPrmsLabel.e1st[0]);
                indices.push(SrcPrmsLabel.lambda1[0]);
                indices.push(SrcPrmsLabel.sigmar[0]);
                indices.push(SrcPrmsLabel.lambda1[0]);
            }
            let sigrx, sigry;
            if(srccont.iswiggler >= 0){
                if(srctype == WIGGLER_Label){
                    srcobj[SrcPrmsLabel.ec[0]] = COEF_EC*(eGeV**2)*srcobj[SrcPrmsLabel.b[0]];
                }
                else{
                    srcobj[SrcPrmsLabel.ec[0]] = COEF_EC*(eGeV**2)*srcobj[SrcPrmsLabel.bxy[0]][1];
                }
                srcobj[SrcPrmsLabel.lc[0]] = ONE_ANGSTROM_eV/srcobj[SrcPrmsLabel.ec[0]]*0.1;
    
                let tanh1 = Math.tanh(1.0);
                let xid = Ky*gaminv_mrad*(0.0863*Math.pow(Kx, 2.13)+0.633)*tanh1;
                let xi = Ky*gaminv_mrad*(0.0194*Math.pow(Kx, 2.25)+0.283)*tanh1;
                srcobj[SrcPrmsLabel.sigmarx[0]][1] = xid;
                srcobj[SrcPrmsLabel.sigmarx[0]][0] = lu*Math.hypot(xi, Nper*xid/Math.sqrt(12));
                sigrx = [srcobj[SrcPrmsLabel.sigmarx[0]][0], srcobj[SrcPrmsLabel.sigmarx[0]][1]];
    
                let eta = 8.89e-2/Ky*gaminv_mrad;
                let etad = Math.sqrt(0.356+Kx*Kx)*gaminv_mrad;
                srcobj[SrcPrmsLabel.sigmary[0]][1] = etad;
                srcobj[SrcPrmsLabel.sigmary[0]][0] = lu*Math.hypot(eta, Nper*etad/Math.sqrt(12));
                sigry = [srcobj[SrcPrmsLabel.sigmary[0]][0], srcobj[SrcPrmsLabel.sigmary[0]][1]];
    
                indices.push(SrcPrmsLabel.ec[0]);
                indices.push(SrcPrmsLabel.lc[0]);
                indices.push(SrcPrmsLabel.sigmarx[0]);
                indices.push(SrcPrmsLabel.sigmary[0]);
            }
            else{
                sigrx = [srcobj[SrcPrmsLabel.sigmar[0]][0], srcobj[SrcPrmsLabel.sigmar[0]][1]];
                sigry = [srcobj[SrcPrmsLabel.sigmar[0]][0], srcobj[SrcPrmsLabel.sigmar[0]][1]];
            }
            let Sigmax = [accobj[AccPrmsLabel.sigma[0]][0], accobj[AccPrmsLabel.sigmap[0]][0]];
            let Sigmay = [accobj[AccPrmsLabel.sigma[0]][1], accobj[AccPrmsLabel.sigmap[0]][1]];
            for(let j = 0; j < 2; j++){
                srcobj[SrcPrmsLabel.Sigmax[0]][j] = Math.hypot(sigrx[j], Sigmax[j]);
                srcobj[SrcPrmsLabel.Sigmay[0]][j] = Math.hypot(sigry[j], Sigmay[j]);
            }
            indices.push(SrcPrmsLabel.Sigmax[0]);
            indices.push(SrcPrmsLabel.Sigmay[0]);
        }
    
        if(srccont.ise1st >= 0){
            if(isfield){
                if(iscustomu){
                    srcobj[SrcPrmsLabel.fd[0]] = uprms.flux;
                }
                else{
                    let gsi = 1/(1+srcobj[SrcPrmsLabel.Kperp[0]]**2/2);
                    let besarg = gsi/4*
                        (srcobj[SrcPrmsLabel.Kxy[0]][1]**2-srcobj[SrcPrmsLabel.Kxy[0]][0]**2);
                    let fx = srcobj[SrcPrmsLabel.Kxy[0]][1]*gsi*(BesselJ0(besarg)-BesselJ1(besarg));
                    let fy = srcobj[SrcPrmsLabel.Kxy[0]][0]*gsi*(BesselJ0(besarg)+BesselJ1(besarg));
                    srcobj[SrcPrmsLabel.fd[0]] = fx**2+fy**2;
                }
            }     
            if(isfield || islength || prmlabel == UpdateBeam || prmlabel == UpdateCurr){
                let fdcoef = COEF_FLUX_UND*(eGeV**2)*iA*(Nper**2);
                srcobj[SrcPrmsLabel.flux[0]] = fdcoef*srcobj[SrcPrmsLabel.fd[0]]
                    *(Math.PI*2)*(srcobj[SrcPrmsLabel.sigmar[0]][1]**2);
                srcobj[SrcPrmsLabel.brill[0]] = srcobj[SrcPrmsLabel.flux[0]]/4/(Math.PI**2)
                    /(srcobj[SrcPrmsLabel.Sigmax[0]][0]*srcobj[SrcPrmsLabel.Sigmax[0]][1])
                    /(srcobj[SrcPrmsLabel.Sigmay[0]][0]*srcobj[SrcPrmsLabel.Sigmay[0]][1]);
                srcobj[SrcPrmsLabel.pkbrill[0]] = 
                    srcobj[SrcPrmsLabel.brill[0]]/iA*accobj[AccPrmsLabel.peakcurr[0]];
                srcobj[SrcPrmsLabel.degener[0]] = 
                    srcobj[SrcPrmsLabel.pkbrill[0]]*
                    (srcobj[SrcPrmsLabel.lambda1[0]]**3)*1.0e-12/8.0/CC;
                indices.push(SrcPrmsLabel.flux[0]);
                indices.push(SrcPrmsLabel.brill[0]);
                indices.push(SrcPrmsLabel.pkbrill[0]);
                indices.push(SrcPrmsLabel.degener[0]);
            }
    
            if(srcobj[SrcPrmsLabel.segment_type[0]] != NoneLabel){
                let ldrift = srcobj[SrcPrmsLabel.interval[0]]-srcobj[SrcPrmsLabel.periods[0]]*lu;
                let gamma2 = 1.0e+6/(gaminv_mrad*gaminv_mrad);
                let pslip = ldrift/(srcobj[SrcPrmsLabel.lambda1[0]]*1.0e-9*2.0*gamma2);
                srcobj[SrcPrmsLabel.pslip[0]] = Math.max(0, Math.floor(pslip));            
                indices.push(SrcPrmsLabel.pslip[0]);
            }
        }
    
        if(!iscustomu){
            let K2 = srcobj[SrcPrmsLabel.Kperp[0]]**2;
            srcobj[SrcPrmsLabel.tpower[0]] 
                = COEF_TOTAL_POWER_ID*(eGeV**2)*iA*2*K2/lu*Nper;   
            indices.push(SrcPrmsLabel.tpower[0]);
        }
    
        this.UpdateSrcIndices(indices);

        if(isconf){
            this.UpdateConfig();
        }
    }

    UpdateSrcIndices(indices){
        for(let j = 0; j < indices.length; j++){
            this.m_src.RefreshItem(indices[j]);
        }
    }

    UpdateConfig()
    {
        let srcobj = this.m_src.JSONObj;
        let accobj = this.m_acc.JSONObj;
        let confobj = this.m_config.JSONObj
        if(confobj[TypeLabel] == ""){
            return;
        }
        let srccont = GetSrcContents(srcobj);
        let conflist = this.m_config.GetShowList();

        let accdef = confobj[ConfigPrmsLabel.accuracy[0]] == DefaultLabel;
        let accid = [MenuLabels.edit, MenuLabels.accuracy].join(IDSeparator);
        if(accdef){
            document.getElementById(accid).setAttribute("disabled", true);
        }
        else{
            document.getElementById(accid).removeAttribute("disabled");
        }
    
        let indices = [];   
        let posprm = [ConfigPrmsLabel.de[0], ConfigPrmsLabel.epitch[0]];
        for(let i = 0; i < posprm.length; i++){
            if(conflist[posprm[i]] >= 0){
                if(confobj[posprm[i]] <= 0){
                    confobj[posprm[i]] = 1;
                }
                indices.push(posprm[i]);
            }    
        }
        
        if(srccont.ise1st >= 0){
            if(conflist[ConfigPrmsLabel.detune[0]] >= 0){
                confobj[ConfigPrmsLabel.efix[0]] = confobj[ConfigPrmsLabel.hfix[0]]*
                (1+confobj[ConfigPrmsLabel.detune[0]])*srcobj[SrcPrmsLabel.e1st[0]];
                indices.push(ConfigPrmsLabel.efix[0]);
            }
            else if(conflist[ConfigPrmsLabel.normenergy[0]]){
                if(confobj[ConfigPrmsLabel.normenergy[0]]){
                    confobj[ConfigPrmsLabel.efix[0]] = 
                    srcobj[SrcPrmsLabel.e1st[0]]*confobj[ConfigPrmsLabel.nefix[0]];        
                    indices.push(ConfigPrmsLabel.efix[0]);
                }
            }
        }
    
        let ldist = confobj[ConfigPrmsLabel.slit_dist[0]];
        if(conflist[ConfigPrmsLabel.fsize[0]] >= 0
            || conflist[ConfigPrmsLabel.fdiv[0]] >= 0
            || conflist[ConfigPrmsLabel.slitapt[0]] == 0)
        {
            let size = [srcobj[SrcPrmsLabel.Sigmax[0]][0], srcobj[SrcPrmsLabel.Sigmay[0]][0]];
            let div = [srcobj[SrcPrmsLabel.Sigmax[0]][1], srcobj[SrcPrmsLabel.Sigmay[0]][1]];
            if(confobj.hasOwnProperty(ConfigPrmsLabel.fsize[0]) == false){
                confobj[ConfigPrmsLabel.fsize[0]] = [0, 0];
            }
            if(confobj.hasOwnProperty(ConfigPrmsLabel.fdiv[0]) == false){
                confobj[ConfigPrmsLabel.fdiv[0]] = [0, 0];
            }
            for(let j = 0; j < 2; j++){
                confobj[ConfigPrmsLabel.fsize[0]][j] 
                    = Math.hypot(size[j], div[j]*ldist);
                confobj[ConfigPrmsLabel.fdiv[0]][j] = 
                    confobj[ConfigPrmsLabel.fsize[0]][j]/ldist
                indices.push(ConfigPrmsLabel.fsize[0]);
                indices.push(ConfigPrmsLabel.fdiv[0]);
            }
        }
        if(conflist[ConfigPrmsLabel.slitapt[0]] == 0){
            for(let j = 0; j < 2; j++){
                confobj[ConfigPrmsLabel.slitapt[0]][j] 
                = confobj[ConfigPrmsLabel.fsize[0]][j]*confobj[ConfigPrmsLabel.nslitapt[0]][j];
            }
            indices.push(ConfigPrmsLabel.slitapt[0]);
        }
        if(conflist[ConfigPrmsLabel.qslitapt[0]] == 0){
            for(let j = 0; j < 2; j++){
                confobj[ConfigPrmsLabel.qslitapt[0]][j] 
                = confobj[ConfigPrmsLabel.fdiv[0]][j]*confobj[ConfigPrmsLabel.nslitapt[0]][j];
            }
            indices.push(ConfigPrmsLabel.qslitapt[0]);
        }
        if(conflist[ConfigPrmsLabel.psize[0]] >= 0 ||
                conflist[ConfigPrmsLabel.pdiv[0]] >= 0)
        {
            if(confobj.hasOwnProperty(ConfigPrmsLabel.psize[0]) == false){
                confobj[ConfigPrmsLabel.psize[0]] = [0, 0];
            }
            if(confobj.hasOwnProperty(ConfigPrmsLabel.pdiv[0]) == false){
                confobj[ConfigPrmsLabel.pdiv[0]] = [0, 0];
            }
            for(let j = 0; j < 2; j++){
                let k2 = srcobj[SrcPrmsLabel.Kxy[0]][1-j];
                k2 = 1+k2*k2*0.5;
                confobj[ConfigPrmsLabel.pdiv[0]][j]
                    = Math.sqrt(k2)/Math.SQRT2*accobj[AccPrmsLabel.gaminv[0]];
                confobj[ConfigPrmsLabel.psize[0]][j] 
                    = confobj[ConfigPrmsLabel.pdiv[0]][j]*ldist;
            }
            if(conflist[ConfigPrmsLabel.psize[0]] >= 0){
                indices.push(ConfigPrmsLabel.psize[0]);
            }
            if(conflist[ConfigPrmsLabel.pdiv[0]] >= 0){
                indices.push(ConfigPrmsLabel.pdiv[0]);
            }
        }
        if(conflist[ConfigPrmsLabel.illumarea[0]] >= 0){
            let stheta = Math.sin(Math.PI*confobj[ConfigPrmsLabel.Qgl[0]]/180);
            let csphi = [Math.cos(Math.PI*confobj[ConfigPrmsLabel.Phiinc[0]]/180), 
                        Math.sin(Math.PI*confobj[ConfigPrmsLabel.Phiinc[0]]/180)];
            let xyR = [];
            for(let j = 0; j < 2; j++){
                xyR.push(confobj[ConfigPrmsLabel.qslitapt[0]][j]*ldist);
            }
            indices.push(ConfigPrmsLabel.illumarea[0]);
            let MM = [
                [csphi[0]**2/stheta+csphi[1]**2, csphi[0]*csphi[1]*(1/stheta-1)],
                [csphi[0]*csphi[1]*(1/stheta-1), csphi[1]**2/stheta+csphi[0]**2]
            ];
            for(let j = 0; j < 2; j++){
                confobj[ConfigPrmsLabel.illumarea[0]][j] 
                    = xyR[0]*MM[j][0]+xyR[1]*MM[j][1];
            }
        }
        if(conflist[ConfigPrmsLabel.e1strange[0]] >= 0){
            let lu = srcobj[[SrcPrmsLabel.lu[0]]]*0.001; // mm -> m
            let eGeV = accobj[AccPrmsLabel.eGeV[0]]
            let kidx = srccont.isbxy >= 0 ? ConfigPrmsLabel.ckrange : ConfigPrmsLabel.krange;
            let krange = CopyJSON(confobj[kidx[0]]);
            if(srcobj[TypeLabel] == HELICAL_UND_Label){
                for(let j = 0; j < krange.length; j++){
                    krange[j] *= Math.SQRT2;
                }
            }
            confobj[ConfigPrmsLabel.e1strange[0]] = [];
            for(let j = 0; j < krange.length; j++){
                let e1str = COEF_E1ST*(eGeV**2)/lu/(1+krange[j]**2/2);    
                confobj[ConfigPrmsLabel.e1strange[0]].push(e1str); 
            }
            indices.push(ConfigPrmsLabel.e1strange[0]);
        }
        if(conflist[ConfigPrmsLabel.bmsizex[0]] >= 0){
            confobj[ConfigPrmsLabel.bmsizex[0]] = 
                Math.hypot(
                    confobj[ConfigPrmsLabel.wigsizex[0]][0], 
                    confobj[ConfigPrmsLabel.wigsizex[0]][1]*confobj[ConfigPrmsLabel.zrange[0]][1]
                );
            indices.push(ConfigPrmsLabel.bmsizex[0]);
        }
        if(conflist[ConfigPrmsLabel.bmsizey[0]] >= 0){
            confobj[ConfigPrmsLabel.bmsizey[0]] = 
                Math.hypot(
                    confobj[ConfigPrmsLabel.wigsizey[0]][0], 
                    confobj[ConfigPrmsLabel.wigsizey[0]][1]*confobj[ConfigPrmsLabel.zrange[0]][1]
                );
            indices.push(ConfigPrmsLabel.bmsizey[0]);
        }
        if(conflist[ConfigPrmsLabel.memsize[0]] >= 0){
            let apt = [0, 0, 0, 0];
            let idx = [
                ConfigPrmsLabel.aptx[0], ConfigPrmsLabel.aptdistx[0], 
                ConfigPrmsLabel.apty[0], ConfigPrmsLabel.aptdisty[0]
            ];
            for(let j = 0; j < 4; j++){
                if(conflist[idx[j]] >= 0){
                    apt[j] = Math.abs(confobj[idx[j]]);
                    if(j%2 > 0){
                        apt[j] += apt[j-1];
                    }                    
                }
            }

            let wavelength = ONE_ANGSTROM_eV/confobj[ConfigPrmsLabel.efix[0]]*1e-10;
            let fftlevel = confobj[ConfigPrmsLabel.anglelevel[0]]+1;
            let Nxy = [1, 1, 1, 1];
            let dxy = [0, 0, 0, 0];
            let mesh = [1, 1, 1, 1];
            let labels = [
                [ConfigPrmsLabel.Xmesh[0], ConfigPrmsLabel.Xrange[0]],
                [ConfigPrmsLabel.Ymesh[0], ConfigPrmsLabel.Yrange[0]],
                [ConfigPrmsLabel.Xpmesh[0], ConfigPrmsLabel.Xprange[0]],
                [ConfigPrmsLabel.Ypmesh[0], ConfigPrmsLabel.Yprange[0]]
            ]
            for(let j = 0; j < 4; j++){
                mesh[j] = confobj[labels[j][0]];
                dxy[j] = (confobj[labels[j][1]][1]-confobj[labels[j][1]][0])/Math.max(1, (mesh[j]-1));
            }
    
            for(let j = 0; j < 2; j++){
                if(apt[2*j] == 0){
                    continue;
                }
                let Nmesh, dpZ;
                if(dxy[j+2] > dxy[j]/confobj[ConfigPrmsLabel.optpos[0]]){
                    dpZ = dxy[j]/confobj[ConfigPrmsLabel.optpos[0]]*1e-3;
                    Nmesh = mesh[j];
                }
                else{
                    dpZ = dxy[j+2]*1e-3;                    
                    Nmesh = mesh[j+2];
                }

                let eps = confobj[ConfigPrmsLabel.diflim[0]];
                let fringe = confobj[ConfigPrmsLabel.softedge[0]];
                let softedge = 1;
                if(fringe > 0){
                    softedge = Math.min(1, Math.sqrt(eps*apt[2*j]/fringe));
                }
                let pmax = wavelength/eps/2/Math.PI/(apt[2*j]*1e-3)/dpZ*softedge;
                let Nfft = 1;
                while(Nfft < pmax || Nfft < Nmesh){
                    Nfft <<= 1;
                }
                for(let k = 0; k < 2; k++){
                    let dn = k == 0 ? 1 : 4; // base: x&y = 2, x'&y' = 8;
                    dn = (dn<<fftlevel)/Math.PI/eps*softedge;
                    if(apt[2*j+1] > 0){
                        dn *= apt[2*j+1]/apt[2*j];
                    }
                    if(k == 0){
                        Nxy[j] = Math.ceil(dn);
                    }
                    else{
                        while(Nxy[j+2]*2 < dn){
                            Nxy[j+2] <<= 1;
                        }
                    }
                }
                Nxy[j] *= 1+confobj[ConfigPrmsLabel.grlevel[0]];
                Nxy[j] *= 2; // x,y points can be twice
                Nxy[j+2] = Math.min(Nfft, Nxy[j+2]);
            }
            let Nm = 2; // need two vector<double> storages
            for(let j = 0; j < 4; j++){
                Nm *= Nxy[j];
            }
            let MB = ToPrmString(Nm*8/1e6, 2) 
            confobj[ConfigPrmsLabel.memsize[0]] = parseFloat(MB);
            indices.push(ConfigPrmsLabel.memsize[0]);
        }
        for(let j = 0; j < indices.length; j++){
            this.m_config.RefreshItem(indices[j]);
        }
    }
}
