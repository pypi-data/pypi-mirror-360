"use strict";

var ConvertKeys = {
    [BLLabel]:{}, [AccLabel]:{}, [SrcLabel]:{}, [ConfigLabel]:{}};
var TemporaryData = "Temporary Data";
var AbsorberSetting = "Absorber";
var FilterSetting = "Filter";
var MultiHarmContents = "Multiharmonic"

let LabelSourceType =
{
    LIN_UND: LIN_UND_Label,
    VERTICAL_UND: VERTICAL_UND_Label,
    HELICAL_UND: HELICAL_UND_Label,
    ELLIPTIC_UND: ELLIPTIC_UND_Label,
    FIGURE8_UND:  FIGURE8_UND_Label,
    VFIGURE8_UND:  VFIGURE8_UND_Label,
    MULTI_HARM_UND: MULTI_HARM_UND_Label,
    WIGGLER: WIGGLER_Label,
    EMPW: EMPW_Label,
    WLEN_SHIFTER: WLEN_SHIFTER_Label,
    BM: BM_Label,
    MULTIPOLE_DEVICE: LIN_UND_Label,
    FIELDMAP3D: FIELDMAP3D_Label,
    CUSTOM_PERIODIC: CUSTOM_PERIODIC_Label,
    CUSTOM: CUSTOM_Label
};

let CategoryMap = {
    "[BLDATA]": BLLabel,
    "[ACCELERATOR]": AccLabel,
    "[SOURCE]": SrcLabel,
    "[CALCULATION]": ConfigLabel,
    "[ETPROFILE]": CustomEt,
    "[BUNCHPROFILE]": CustomCurrent,
    "[EPROFILE]": null,
    "[XPROFILE]": null,
    "[YPROFILE]": null,
    "[XYPROFILE]": null,
    "[FMOD_TABLE]": null,
    "[GAP_TABLE]": ImportGapField,
    "[ZVSBini]": null,
    "[ZVSBfin]": null,
    "[ZVSB]": CustomField,
    "[FILTERMATERIAL]": FMaterialLabel,
    "[Filterini]": null,
    "[Filterfin]": null,
    "[FILTERDATA]": CustomFilter,
    "[CUSTOMABSORBERDATA]": null,
    "[ABSORBERDATA]": AbsorberSetting,
    "[GENERICFILTER]": FilterSetting,
    "[MULTIPOLE]": null,
    "[SEGMENTERROR]": null,
    "[CUSTOMSEGMENT]": null,
    "[CUSTOMBXY]": MultiHarmContents,
    "[SavedIndices]": null,
    "[SavedIndex]": CurrentLabel,
    "[OUTPUTDATA]": null,
    "[ProcessN]": null,
    "[GAPFactor]": null
};

function ParseInt(strval)
{
    let num = parseInt(strval);
    if(isNaN(num)){
        num = 0;
    }
    return num;
}

function GetSrcType(type) {
    return LabelSourceType[type];
}

function GetPeriod(lu)
{
    return lu*10;
}

function GetSegmentScheme(scheme) {
    return "";
}

function GetTimeRange(trange)
{
    return [-trange/2, trange/2];
}

function ConvertPrm(data)
{
    let linesr = data.split(/\n|\r/);
    let categ = null;
    let objects = {};

    objects[BLLabel] = [];
    objects[AccLabel] = [];
    objects[SrcLabel] = [];
    objects[ConfigLabel] = [];
    objects[FMaterialLabel] = [];
    objects[CurrentLabel] = [];

    objects[CustomCurrent] = [];
    objects[CustomEt] = [];    
    objects[ImportGapField] = [];
    objects[CustomField] = [];
    objects[CustomFilter] = [];

    objects[AbsorberSetting] = [];
    objects[FilterSetting] = [];
    objects[MultiHarmContents] = [];

    for(let n = 0; n < linesr.length; n++){
        let line = linesr[n].trim();
        if(line == ""){
            continue;
        }
        if(CategoryMap.hasOwnProperty(line)){
            categ = CategoryMap[line];
            if(categ != null){
                objects[categ].push([]);
            }
            continue;
        }
        if(categ == null){
            continue;
        }
        Last(objects[categ]).push(line);
    }
    let categs = [BLLabel, AccLabel, SrcLabel, ConfigLabel];
    for(const categ of categs){
        if(objects[categ].length == 0){
            return null;
        }
    }

    let curridx = 0;
    objects[CurrentLabel].forEach(obj => {
        obj.forEach(line => {
            curridx = ParseInt(line);
        })
    });
    curridx = Math.max(0, Math.min(curridx, objects[BLLabel].length-1));

    let prmlabels  = {
        [BLLabel]: null, 
        [AccLabel]: AccPrmsLabel, 
        [SrcLabel]: SrcPrmsLabel, 
        [ConfigLabel]: ConfigPrmsLabel
    };

    let spobjs = {};
    let spsupple = {};
    categs.forEach(categ => {        
        spobjs[categ] = {};
        spsupple[categ] = {};
        objects[categ].forEach(lines => {
            let obj = {};
            if(categ != BLLabel){
                obj = CopyJSON(GUIConf.default[categ]);
            }
            let supple = {};
            let name = "untitled";
            lines.forEach(line => {
                let items = line.split("\t");
                if(items.length >= 2){
                    if(items[0] == "Name"){
                        name = items[1];
                    }
                    else{
                        InsertNewObject(obj, supple, categ, prmlabels[categ], items);
                    }
                }                
            });
            spobjs[categ][name] = obj;
            if(categ == BLLabel){
                if(curridx == Object.keys(spobjs[categ]).length-1){
                    spobjs[CurrentLabel] = name;
                };
            }
            if(Object.keys(supple).length > 0){
                spsupple[categ][name] = supple;
            }
        })
    });

    let dataobjs = {};
    let datacategs = [CustomCurrent, CustomEt, ImportGapField, CustomField, CustomFilter];
    for(let j = 0; j < datacategs.length; j++){
        let categ = datacategs[j];
        dataobjs[categ] = {};
        if(objects[categ].length == 0){
            continue;
        }
        objects[categ].forEach(obj => {
            let items = obj[0].split("\t");
            let name = "untitled";
            if(items.length >= 2 && items[0] == "Name"){
                name = items[1];
            }
            obj.splice(0, 1);
            dataobjs[categ][name] = obj.join("\n");    
        })
    };

    let gridobjs = {};
    let gridcategs = [AbsorberSetting, FilterSetting, MultiHarmContents];
    for(let j = 0; j < gridcategs.length; j++){
        let categ = gridcategs[j];
        gridobjs[categ] = {};
        if(objects[categ].length == 0){
            continue;
        }
        let grids = [];
        objects[categ].forEach(obj => {
            let items = obj[0].split("\t");
            let name = "untitled";
            if(items.length >= 2 && items[0] == "Name"){
                name = items[1];
            }
            obj.splice(0, 1);
            obj.forEach(line => {
                items = line.split("\t");
                if(categ == MultiHarmContents){
                    if(items.length >= 4){
                        let isok = true;
                        for(let k = 0; k < 4; k++){
                            if(isNaN(parseFloat(items[k]))){
                                isok = false;
                                break;
                            }
                        }
                        if(isok){
                            grids.push(items);
                        }
                    }
                }
                else{
                    if(items.length >= 3){
                        let thickness = parseFloat(items[0]);
                        if(!isNaN(thickness)){
                            grids.push([items[2], thickness]);
                        }
                    }
                }    
            })      
            gridobjs[categ][name] = grids;
        });
    };

    spobjs[FMaterialLabel] = {};
    objects[FMaterialLabel].forEach(lines => {
        let obj = {dens: 1, comp:[]};
        let name = "untitled";
        lines.forEach(line => {
            let items = line.split("\t");
            if(items.length >= 2){
                if(items[0] == "Name"){
                    name = items[1];
                }
                else if(items[0] == "Density"){
                    obj.dens = parseFloat(items[1]);
                }
                else{
                    let Z = parseFloat(items[0]);
                    let M = parseFloat(items[1]);                    
                    if(!isNaN(Z) && !isNaN(M)){
                        obj.comp.push([Z, M]);
                    }                    
                }
            }                
        });
        spobjs[FMaterialLabel][name] = obj;
    });

    Object.keys(spsupple[AccLabel]).forEach(accname => {
        let units = [1, 1, 1];
        if(spsupple[AccLabel][accname].hasOwnProperty("bunchunit")){
            let bunit = ParseInt(spsupple[AccLabel][accname]["bunchunit"]);
            switch(bunit){
                case 0:
                    units[0] = 1e-3/CC;
                    break;
                case 1:
                    units[0] = 1.0e-2/CC;
                    break;
                case 2:
                    units[0] = 1.0/CC;
                    break;
                case 3:
                    units[0] = 1.0;
                    break;
                case 4:
                    units[0] = 1.0e-12;
                    break;
                case 5:
                    units[0] = 1.0e-15;
                    break;
            }
            units[0] *= 1e15; // s -> fs
        }

        spobjs[AccLabel][accname][AccPrmsLabel.bunchtype[0]] = GaussianLabel;
        let iscbeam = false;
        if(spsupple[AccLabel][accname].hasOwnProperty("bunchtype")){
            let btype = ParseInt(spsupple[AccLabel][accname]["bunchtype"]);
            iscbeam = !isNaN(btype) && btype > 0;
        }

        if(spsupple[AccLabel][accname].hasOwnProperty("BunchProfileName")){
            let dataname = spsupple[AccLabel][accname]["BunchProfileName"];
            if(dataobjs[CustomCurrent].hasOwnProperty(dataname)){
                GUIConf.ascii[CustomCurrent].SetData(dataobjs[CustomCurrent][dataname], units);
                spobjs[AccLabel][accname][CustomCurrent] = GUIConf.ascii[CustomCurrent].GetObj();    
                if(iscbeam){
                    spobjs[AccLabel][accname][AccPrmsLabel.bunchtype[0]] = CustomCurrent;
                }
            }
        }
        if(spsupple[AccLabel][accname].hasOwnProperty("ETProfileName")){
            let dataname = spsupple[AccLabel][accname]["ETProfileName"];
            if(dataobjs[CustomEt].hasOwnProperty(dataname)){
                GUIConf.ascii[CustomEt].SetData(dataobjs[CustomEt][dataname], units);
                spobjs[AccLabel][accname][CustomEt] = GUIConf.ascii[CustomEt].GetObj();
                if(iscbeam){
                    spobjs[AccLabel][accname][AccPrmsLabel.bunchtype[0]] = CustomEt;
                }
            }
        }
    });

    Object.keys(spsupple[SrcLabel]).forEach(srcname => {
        let dunit = 0;
        if(spsupple[SrcLabel][srcname].hasOwnProperty("dunit")){
            dunit = ParseInt(spsupple[SrcLabel][srcname]["dunit"]);
        }
        let funitgap = 0;
        if(spsupple[SrcLabel][srcname].hasOwnProperty("funitgap")){
            funitgap = ParseInt(spsupple[SrcLabel][srcname]["funitgap"]);
        }
        let funit = 0;
        if(spsupple[SrcLabel][srcname].hasOwnProperty("funit")){
            funit = ParseInt(spsupple[SrcLabel][srcname]["funit"]);
        }
        let units = [1, 1, 1];
        if(dunit == 0){
            units[0] = 1e-3;
        }
        else if(dunit == 1){
            units[0] = 1e-2;
        }
        if(funit == 1){
            units[1] = units[2] = 1e-4;
        }

        if(spsupple[SrcLabel][srcname].hasOwnProperty("FieldDataName")){
            let dataname = spsupple[SrcLabel][srcname]["FieldDataName"];
            let ascii = null;
            if(spobjs[SrcLabel][srcname][TypeLabel] == CUSTOM_Label){
                ascii = CustomField;
            }
            else if(spobjs[SrcLabel][srcname][TypeLabel] == CUSTOM_PERIODIC_Label){
                ascii = CustomPeriod;                
            }
            if(ascii != null && dataobjs[CustomField].hasOwnProperty(dataname)){
                GUIConf.ascii[ascii].SetData(dataobjs[CustomField][dataname], units);
                spobjs[SrcLabel][srcname][ascii] = GUIConf.ascii[ascii].GetObj();    
            }
        }

        if(spsupple[SrcLabel][srcname].hasOwnProperty("GapDataName")){
            let srccont = GetSrcContents(spobjs[SrcLabel][srcname]);
            if(srccont.isgap > 0){
                let dataname = spsupple[SrcLabel][srcname]["GapDataName"];
                units[0] = 1;
                units[1] = units[2] = funitgap == 0 ? 1 : 1e-4;
                if(dataobjs[ImportGapField].hasOwnProperty(dataname)){
                    GUIConf.ascii[ImportGapField].SetData(dataobjs[ImportGapField][dataname], units);
                    spobjs[SrcLabel][srcname][ImportGapField] = GUIConf.ascii[ImportGapField].GetObj();    
                }    
            }
        }

        let natfoc = 0;
        if(spsupple[SrcLabel][srcname].hasOwnProperty("natfocusx")){
            if(ParseInt(spsupple[SrcLabel][srcname].natfocusx) > 0){
                natfoc = 1;
            }
        }
        if(spsupple[SrcLabel][srcname].hasOwnProperty("natfocusy")){
            if(ParseInt(spsupple[SrcLabel][srcname].natfocusy) > 0){
                natfoc += 2;
            }
        }
        spobjs[SrcLabel][srcname][SrcPrmsLabel.natfocus[0]] =
            [NoneLabel, BxOnlyLabel, ByOnlyLabel, BothLabel][natfoc];

        spobjs[SrcLabel][srcname][SrcPrmsLabel.b[0]] = spobjs[SrcLabel][srcname][SrcPrmsLabel.bxy[0]][1];
        spobjs[SrcLabel][srcname][SrcPrmsLabel.K[0]] = spobjs[SrcLabel][srcname][SrcPrmsLabel.Kxy[0]][1];

        if(spsupple[SrcLabel][srcname].hasOwnProperty("CustomBxyData")){
            let dataname = spsupple[SrcLabel][srcname]["CustomBxyData"];
            if(gridobjs[MultiHarmContents].hasOwnProperty(dataname)){
                spobjs[SrcLabel][srcname][SrcPrmsLabel.multiharm[0]] = gridobjs[MultiHarmContents][dataname];
            }
        }

        let segtypes = [IdenticalLabel, SwapBxyLabel, FlipBxLabel, FlipByLabel];
        spobjs[SrcLabel][srcname][SrcPrmsLabel.segment_type[0]] = NoneLabel;
        if(spsupple[SrcLabel][srcname].hasOwnProperty("segment_scheme")){
            if(ParseInt(spsupple[SrcLabel][srcname].segment_scheme) > 0){
                if(spsupple[SrcLabel][srcname].hasOwnProperty("segment_type")){
                    let type = ParseInt(spsupple[SrcLabel][srcname].segment_type);
                    type = Math.max(0, Math.min(type, segtypes.length-1));
                    spobjs[SrcLabel][srcname][SrcPrmsLabel.segment_type[0]] = segtypes[type];
                }        
            }
        }

        if(spobjs[SrcLabel][srcname][SrcPrmsLabel.type[0]] == CUSTOM_PERIODIC_Label){
            let Nper = Math.max(1, spobjs[SrcLabel][srcname][SrcPrmsLabel.periods[0]])+1;
            if(spobjs[SrcLabel][srcname][SrcPrmsLabel.endmag[0]]){
                Nper += 1;
            }
            spobjs[SrcLabel][srcname][SrcPrmsLabel.devlength[0]] = 
                spobjs[SrcLabel][srcname][SrcPrmsLabel.lu[0]]*Nper*1e-3

        }
        
    })

    Object.keys(spsupple[ConfigLabel]).forEach(confname => {
        let units = [1, 1];
        if(spsupple[ConfigLabel][confname].hasOwnProperty("FilterDataName")){
            let dataname = spsupple[ConfigLabel][confname]["FilterDataName"];
            if(dataobjs[CustomFilter].hasOwnProperty(dataname)){
                GUIConf.ascii[CustomFilter].SetData(dataobjs[CustomFilter][dataname], units);
                spobjs[ConfigLabel][confname][CustomFilter] = GUIConf.ascii[CustomFilter].GetObj();    
            }
        }

        if(spsupple[ConfigLabel][confname].hasOwnProperty("filter")){
            let filtertype = ParseInt(spsupple[ConfigLabel][confname]["filter"]);
            if(filtertype == 0){
                spobjs[ConfigLabel][confname][ConfigPrmsLabel.filter[0]] = NoneLabel;
            }
        }
        
        spobjs[ConfigLabel][confname][ConfigPrmsLabel.dstep[0]] = LinearLabel;
        if(spsupple[ConfigLabel][confname].hasOwnProperty("voldenslog")){
            if(ParseInt(spsupple[ConfigLabel][confname]["voldenslog"]) > 0){
                spobjs[ConfigLabel][confname][ConfigPrmsLabel.dstep[0]] = LogLabel;
            }
        }
        if(spsupple[ConfigLabel][confname].hasOwnProperty("voldensarb")){
            if(ParseInt(spsupple[ConfigLabel][confname]["voldensarb"]) > 0){
                spobjs[ConfigLabel][confname][ConfigPrmsLabel.dstep[0]] = ArbPositionsLabel;                
            }
        }

        if(spsupple[ConfigLabel][confname].hasOwnProperty("GenericFilterDataName")){
            let dataname = spsupple[ConfigLabel][confname]["GenericFilterDataName"];
            if(gridobjs[FilterSetting].hasOwnProperty(dataname)){
                spobjs[ConfigLabel][confname][ConfigPrmsLabel.fmateri[0]] = gridobjs[FilterSetting][dataname];
            }
        }
        if(spsupple[ConfigLabel][confname].hasOwnProperty("GenAbsDataName")){
            let dataname = spsupple[ConfigLabel][confname]["GenAbsDataName"];
            if(gridobjs[AbsorberSetting].hasOwnProperty(dataname)){
                spobjs[ConfigLabel][confname][ConfigPrmsLabel.amateri[0]] = gridobjs[AbsorberSetting][dataname];
            }
        }
    });

    spobjs[VersionNumberLabel] = Version;
    return spobjs;
}

function InsertNewObject(obj, supple, categ, prmlabel, items)
{    
    if(!ConvertKeys[categ].hasOwnProperty(items[0])){
        return;
    }
    let key = ConvertKeys[categ][items[0]];
    if(key == TemporaryData){
        supple[items[0]] = items[1];
    }
    else if(typeof key == "string"){
        if(prmlabel == null){
            obj[key] = items[1];
        }
        else{
            let keyd = prmlabel[key][0];
            if(typeof prmlabel[key][1] == "number"){
                obj[keyd] = parseFloat(items[1]);
            }
            else{
                obj[keyd] = items[1];
            }
        }
    }
    else{
        let keyd = prmlabel[key[0]][0];
        if(typeof key[1] == "number"){
            let j = ParseInt(key[1]);
            if(j == 0 || j == 1){
                if(!obj.hasOwnProperty(keyd) || !Array.isArray(obj[keyd])){
                    obj[keyd] = [1, 1];    
                }
                obj[keyd][j] = parseFloat(items[1]);
            }
        }
        else if(Array.isArray(key[1])){
            let j = ParseInt(items[1]);
            if(key[0] == "accuracy"){
                j--;
            }
            j = Math.max(0, Math.min(j, key[1].length-1));
            obj[keyd] = key[1][j];
        }
        else if(typeof key[1] == "function"){
            obj[keyd] = key[1](items[1]);
        }
    }
}

// BLLabel
ConvertKeys[BLLabel]["EBname"] = AccLabel;
ConvertKeys[BLLabel]["SRCname"] = SrcLabel;
ConvertKeys[BLLabel]["OUTname"] = ConfigLabel;

// AccLabel
ConvertKeys[AccLabel]["accelerator"] = ["type", [RINGLabel, LINACLabel]];
ConvertKeys[AccLabel]["eGeV"] = "eGeV";
ConvertKeys[AccLabel]["imA"] = "imA";
ConvertKeys[AccLabel]["aimA"] = "aimA";
ConvertKeys[AccLabel]["cirm"] = "cirm";
ConvertKeys[AccLabel]["bunches"] = "bunches";
ConvertKeys[AccLabel]["pulsepps"] = "pulsepps";
ConvertKeys[AccLabel]["bunchlength"] = "bunchlength";
ConvertKeys[AccLabel]["bunchcharge"] = "bunchcharge";
ConvertKeys[AccLabel]["emitt"] = "emitt";
ConvertKeys[AccLabel]["coupl"] = "coupl";
ConvertKeys[AccLabel]["espread"] = "espread";
ConvertKeys[AccLabel]["betax"] = ["beta", 0];
ConvertKeys[AccLabel]["betay"] = ["beta", 1];
ConvertKeys[AccLabel]["alphax"] = ["alpha", 0];
ConvertKeys[AccLabel]["alphay"] = ["alpha", 1];
ConvertKeys[AccLabel]["eta"] = ["eta", 0];
ConvertKeys[AccLabel]["etay"] = ["eta", 1];
ConvertKeys[AccLabel]["deta"] = ["etap", 0];
ConvertKeys[AccLabel]["detay"] = ["etap", 1];
ConvertKeys[AccLabel]["xinj"] = ["xy", 0];
ConvertKeys[AccLabel]["yinj"] = ["xy", 1];
ConvertKeys[AccLabel]["xdinj"] = ["xyp", 0];
ConvertKeys[AccLabel]["ydinj"] = ["xyp", 1];
ConvertKeys[AccLabel]["injectionebm"] = ["injectionebm", 
    [AutomaticLabel, EntranceLabel, CenterLabel, ExitLabel, CustomLabel]];
ConvertKeys[AccLabel]["bunchdata"] = CustomParticle;

// SrcLabel
ConvertKeys[SrcLabel]["type"] = ["type", GetSrcType];
ConvertKeys[SrcLabel]["gap"] = "gap";
ConvertKeys[SrcLabel]["periods"] = "periods";
ConvertKeys[SrcLabel]["bx"] = ["bxy", 0];
ConvertKeys[SrcLabel]["by"] = ["bxy", 1];
ConvertKeys[SrcLabel]["lu"] = ["lu", GetPeriod];
ConvertKeys[SrcLabel]["devlength"] = "devlength";
ConvertKeys[SrcLabel]["kperp"] = "Kperp";
ConvertKeys[SrcLabel]["kx"] = ["Kxy", 0];
ConvertKeys[SrcLabel]["ky"] = ["Kxy", 1];
ConvertKeys[SrcLabel]["radius"] = "radius";
ConvertKeys[SrcLabel]["bendlength"] = "bendlength";
ConvertKeys[SrcLabel]["fringelen"] = "fringelen";
ConvertKeys[SrcLabel]["sidepolel"] = "subpolel";
ConvertKeys[SrcLabel]["bminterv"] = "bminterv";
ConvertKeys[SrcLabel]["csrorg"] = "csrorg";

ConvertKeys[SrcLabel]["segments"] = "segments";
ConvertKeys[SrcLabel]["Lint"] = "interval";
ConvertKeys[SrcLabel]["phi1"] = ["phi12", 0];
ConvertKeys[SrcLabel]["phi2"] = ["phi12", 1];
ConvertKeys[SrcLabel]["Dphi"] = "phi0";
ConvertKeys[SrcLabel]["Lmatch"] = "mdist";

ConvertKeys[SrcLabel]["gaplink"] = ["gaplink", [NoneLabel, ImpGapTableLabel]];
ConvertKeys[SrcLabel]["isperlattice"] = ["perlattice", [false, true]];

ConvertKeys[SrcLabel]["special_magnets"] = ["fielderr", [false, true]];
ConvertKeys[SrcLabel]["bxoffset"] = ["boffset", 0];
ConvertKeys[SrcLabel]["byoffset"] = ["boffset", 1];
ConvertKeys[SrcLabel]["taperfx"] = ["ltaper", 0];
ConvertKeys[SrcLabel]["taperfy"] = ["ltaper", 1];
ConvertKeys[SrcLabel]["taperqx"] = ["qtaper", 0];
ConvertKeys[SrcLabel]["taperqy"] = ["qtaper", 1];

ConvertKeys[SrcLabel]["magerron"] = ["phaseerr", [false, true]];
ConvertKeys[SrcLabel]["magerrseed"] = "seed";
ConvertKeys[SrcLabel]["fielderr"] = "fsigma";
ConvertKeys[SrcLabel]["phaseerr"] = "psigma";
ConvertKeys[SrcLabel]["errtrax"] = ["xysigma", 0];
ConvertKeys[SrcLabel]["errtray"] = ["xysigma", 1];

ConvertKeys[SrcLabel]["issymme"] = ["field_str", [AntiSymmLabel, SymmLabel]];
ConvertKeys[SrcLabel]["endcorr"] = ["endmag", [false, true]];
ConvertKeys[SrcLabel]["tandembm"] = ["bmtandem", [false, true]];

ConvertKeys[AccLabel]["bunchtype"] = TemporaryData;
ConvertKeys[AccLabel]["ETProfileName"] = TemporaryData;
ConvertKeys[AccLabel]["BunchProfileName"] = TemporaryData;
ConvertKeys[SrcLabel]["FieldDataName"] = TemporaryData;
ConvertKeys[SrcLabel]["GapDataName"] = TemporaryData;
ConvertKeys[ConfigLabel]["FilterDataName"] = TemporaryData;

ConvertKeys[AccLabel]["bunchunit"] = TemporaryData;
ConvertKeys[SrcLabel]["funitgap"] = TemporaryData;
ConvertKeys[SrcLabel]["funit"] = TemporaryData;
ConvertKeys[SrcLabel]["dunit"] = TemporaryData;
ConvertKeys[SrcLabel]["natfocusx"] = TemporaryData;
ConvertKeys[SrcLabel]["natfocusy"] = TemporaryData;
ConvertKeys[SrcLabel]["segment_scheme"] = TemporaryData;
ConvertKeys[SrcLabel]["segment_type"] = TemporaryData;

ConvertKeys[ConfigLabel]["filter"] = TemporaryData;
ConvertKeys[ConfigLabel]["voldenslog"] = TemporaryData;
ConvertKeys[ConfigLabel]["voldensarb"] = TemporaryData;

ConvertKeys[SrcLabel]["CustomBxyData"] = TemporaryData;
ConvertKeys[ConfigLabel]["GenericFilterDataName"] = TemporaryData;
ConvertKeys[ConfigLabel]["GenAbsDataName"] = TemporaryData;

// ConfigLabel
ConvertKeys[ConfigLabel]["slit_dist"] = "slit_dist";
ConvertKeys[ConfigLabel]["epmin"] = ["erange", 0];
ConvertKeys[ConfigLabel]["epmax"] = ["erange", 1];
ConvertKeys[ConfigLabel]["de"] = "de";
ConvertKeys[ConfigLabel]["normalfixep"] = "nefix";
ConvertKeys[ConfigLabel]["fixep"] = "efix";
ConvertKeys[ConfigLabel]["minthetax"] = ["qxrange", 0];
ConvertKeys[ConfigLabel]["maxthetax"] = ["qxrange", 1];
ConvertKeys[ConfigLabel]["minthetay"] = ["qyrange", 0];
ConvertKeys[ConfigLabel]["maxthetay"] = ["qyrange", 1];
ConvertKeys[ConfigLabel]["min_x"] = ["xrange", 0];
ConvertKeys[ConfigLabel]["max_x"] = ["xrange", 1];
ConvertKeys[ConfigLabel]["min_y"] = ["yrange", 0];
ConvertKeys[ConfigLabel]["max_y"] = ["yrange", 1];
ConvertKeys[ConfigLabel]["meshx"] = "xmesh";
ConvertKeys[ConfigLabel]["meshy"] = "ymesh";
ConvertKeys[ConfigLabel]["mintheta"] = ["qrange", 0];
ConvertKeys[ConfigLabel]["maxtheta"] = ["qrange", 1];
ConvertKeys[ConfigLabel]["min_r"] = ["rrange", 0];
ConvertKeys[ConfigLabel]["max_r"] = ["rrange", 1];
ConvertKeys[ConfigLabel]["minphi"] = ["phirange", 0];
ConvertKeys[ConfigLabel]["maxphi"] = ["phirange", 1];
ConvertKeys[ConfigLabel]["meshr"] = "rphimesh";
ConvertKeys[ConfigLabel]["meshphi"] = "qphimesh";
ConvertKeys[ConfigLabel]["harmmin"] = ["hrange", 0];
ConvertKeys[ConfigLabel]["harmmax"] = ["hrange", 1];
ConvertKeys[ConfigLabel]["tgtharm"] = "hfix";
ConvertKeys[ConfigLabel]["detune"] = "detune";
ConvertKeys[ConfigLabel]["kymin"] = ["krange", 0];
ConvertKeys[ConfigLabel]["kymax"] = ["krange", 1];
ConvertKeys[ConfigLabel]["meshep"] = "kmesh";

ConvertKeys[ConfigLabel]["thetax"] = ["qxyfix", 0];
ConvertKeys[ConfigLabel]["thetay"] = ["qxyfix", 1];
ConvertKeys[ConfigLabel]["posx"] = ["xyfix", 0];
ConvertKeys[ConfigLabel]["posy"] = ["xyfix", 1];
ConvertKeys[ConfigLabel]["slit_thetax"] = ["qslitpos", 0];
ConvertKeys[ConfigLabel]["slit_thetay"] = ["qslitpos", 1];
ConvertKeys[ConfigLabel]["slit_x"] = ["slitpos", 0];
ConvertKeys[ConfigLabel]["slit_y"] = ["slitpos", 1];
ConvertKeys[ConfigLabel]["slitvarx"] = ["nslitapt", 0];
ConvertKeys[ConfigLabel]["slitvary"] = ["nslitapt", 1];
ConvertKeys[ConfigLabel]["Dthetax"] = ["qslitapt", 0];
ConvertKeys[ConfigLabel]["Dthetay"] = ["qslitapt", 1];
ConvertKeys[ConfigLabel]["Dx"] = ["slitapt", 0];
ConvertKeys[ConfigLabel]["Dy"] = ["slitapt", 1];
ConvertKeys[ConfigLabel]["slit_theta1"] = ["slitq", 0];
ConvertKeys[ConfigLabel]["slit_theta2"] = ["slitq", 1];
ConvertKeys[ConfigLabel]["slit_r1"] = ["slitr", 0];
ConvertKeys[ConfigLabel]["slit_r2"] = ["slitr", 1];
ConvertKeys[ConfigLabel]["timerange"] = ["trange", GetTimeRange];
ConvertKeys[ConfigLabel]["meshtime"] = "tmesh";
ConvertKeys[ConfigLabel]["gthetax"] = ["gtacc", 0];
ConvertKeys[ConfigLabel]["gthetay"] = ["gtacc", 1];
ConvertKeys[ConfigLabel]["hacceptance"] = "horizacc";
ConvertKeys[ConfigLabel]["srcxfix"] = "Xfix";
ConvertKeys[ConfigLabel]["srcyfix"] = "Yfix";
ConvertKeys[ConfigLabel]["srcqxfix"] = "Xpfix";
ConvertKeys[ConfigLabel]["srcqyfix"] = "Ypfix";
ConvertKeys[ConfigLabel]["srcxini"] = ["Xrange", 0];
ConvertKeys[ConfigLabel]["srcxfin"] = ["Xrange", 1];
ConvertKeys[ConfigLabel]["srcxmesh"] = "Xmesh"
ConvertKeys[ConfigLabel]["srcyini"] = ["Yrange", 0];
ConvertKeys[ConfigLabel]["srcyfin"] = ["Yrange", 1];
ConvertKeys[ConfigLabel]["srcymesh"] = "Ymesh";
ConvertKeys[ConfigLabel]["srcqxini"] = ["Xprange", 0];
ConvertKeys[ConfigLabel]["srcqxfin"] = ["Xprange", 1];
ConvertKeys[ConfigLabel]["srcqxmesh"] = "Xpmesh";
ConvertKeys[ConfigLabel]["srcqyini"] = ["Yprange", 0];
ConvertKeys[ConfigLabel]["srcqyfin"] = ["Yprange", 1];
ConvertKeys[ConfigLabel]["srcqymesh"] = "Ypmesh";

ConvertKeys[ConfigLabel]["spdzini"] = ["zrange", 0];
ConvertKeys[ConfigLabel]["spdzfin"] = ["zrange", 1];
ConvertKeys[ConfigLabel]["spdzmesh"] = "zmesh";
ConvertKeys[ConfigLabel]["spdypos"] = "spdyfix";
ConvertKeys[ConfigLabel]["spdxpos"] = "spdxfix";
ConvertKeys[ConfigLabel]["spdrpos"] = "spdrfix";
ConvertKeys[ConfigLabel]["spdnradial"] = "Qnorm";
ConvertKeys[ConfigLabel]["spdnazimuth"] = "Phinorm";

ConvertKeys[ConfigLabel]["voldensdepthini"] = ["drange", 0];
ConvertKeys[ConfigLabel]["voldensdepthfin"] = ["drange", 1];
ConvertKeys[ConfigLabel]["voldensmesh"] = "dmesh"
ConvertKeys[ConfigLabel]["pplimupper"] = "pplimit";

ConvertKeys[ConfigLabel]["accuracy"] = ["accuracy", [DefaultLabel, CustomLabel]];
ConvertKeys[ConfigLabel]["filtertype"] = ["filter", 
    [GenFilterLabel, BPFGaussianLabel, CustomLabel]];
ConvertKeys[ConfigLabel]["elogscale"] = ["estep", [LinearLabel, LogLabel]];
ConvertKeys[ConfigLabel]["efixnorm"] = ["normenergy", [false, true]];
ConvertKeys[ConfigLabel]["trunbbmrad"] = ["optDx", [false, true]];
ConvertKeys[ConfigLabel]["xsmoothing"] = "xsmooth";
ConvertKeys[ConfigLabel]["voldenspath"] = "depthdata";
