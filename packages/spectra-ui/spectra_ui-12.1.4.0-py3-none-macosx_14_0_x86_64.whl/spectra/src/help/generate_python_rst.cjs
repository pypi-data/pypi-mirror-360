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
const RemoteRepository = "https://spectrax.org/spectra/app/"+Version2Digit+"/index.html"
const HelpURL = "https://spectrax.org/spectra/app/"+Version2Digit+"/help/reference.html"
const PySampleURL = "https://spectrax.org/spectra/app/"+Version2Digit+"/python/samples.zip"

function GetBrowserIssue()
{
    let caption = "Web browsers supported in *spectra-ui* and known issues.";
    let titles = ["Browser", "Remarks/Issues"];
    let brdata = [
        ["Chrome", "Fully tested and most recommended."],
        ["Edge", "Recommended as well as Chrome."],
        ["Firefox", "Loading source files from the local repository may fail. In such a case, the user is requested to move them to another location."],
        ["Safari", "Not recommended for use, because GUI cannot be operated, or it is not editable because frozen by the OS. It just shows the parameters and configurations, and plots the pre- and post-processed results."]
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
        ["--local", "-l", "Use local repository (/path-to-python/site-packages/spectra/src/indx.html) for the source file."],
    ];
    return {caption:caption, titles:titles, data:brdata};
}

function GetMenuKey()
{
    let caption = "Arguments available in the function  "+GetQString("SelectCalculation")+" to specify the calculation type."
    let titles = ["Category", "Menu Items", "Arguments"];
    let data = [];
    let category = [CalcIDSCheme, CalcIDMethod, CalcIDMainTarget, CalcIDCondition, CalcIDSubCondition];
    for(const categ of category){
        let keys = Object.keys(CalcLabels[categ]);
        data.push([categ, CalcLabels[categ][keys[0]], keys[0]]);
        for(let j = 1; j < keys.length; j++){
            let subel = [null, CalcLabels[categ][keys[j]], keys[j]];
            data.push(subel);
        }
    }
    return {caption:caption, titles:titles, data:data};
}

function GetAccKey()
{
    let caption = "Arguments available in SetAccuracy()."
    let titles = ["Category", "Menu Items", "Arguments"];
    let data = [];
    for(let j = 0; j < AccuracyOptionsOrder.length; j++){
        let key = AccuracyOptionsOrder[j];
        if(key == SeparatorLabel){
            continue;
        }
        else if(AccuracyOptionsLabel[key][1] == SimpleLabel && j < AccuracyOptionsOrder.length-1){
            let categ = AccuracyOptionsLabel[key][0];
            let nkey = AccuracyOptionsOrder[j+1]
            data.push([categ, AccuracyOptionsLabel[nkey][0], nkey]);
            j++;
        }
        else{
            data.push([null, AccuracyOptionsLabel[key][0], key]);
        }
    }
    let nd = 0;
    for(let j = data.length-1; j >= 0; j--){
        nd++;
        if(data[j][0] != null){
            data[j][0].rows = nd;
            nd = 0;
        }
    }
    return {caption:caption, titles:titles, data:data};
}

function GetUnitKey()
{
    let caption = "Arguments available in PreProcess.SetUnit()"
    let titles = ["Menu Items", "Arguments", "Options"];
    let data = [];
    for(const key of DataUnitOptionsOrder){
        let label = DataUnitOptionsLabel[key][0];
        let sel = DataUnitOptionsLabel[key][1].join(", ");
        data.push([label, key, sel]);
    }
    return {caption:caption, titles:titles, data:data};
}

function GetMenuCateg()
{
    let caption = "Arguments available in the function  "+GetQString("Set")+" to set a parameter."
    let titles = ["Arguments", "Remarks"];
    let data = [
        ["acc", "Parameters to specify the accelerator as shown in "+AccLabel+" subpanel."],
        ["src", "Parameters to specify the light source as shown in "+SrcLabel+" subpanel."],
        ["config", "Configurations to specify the numerical conditions as shown in "+ConfigLabel+" subpanel."],
        ["outfile", "Configurations to specify the output file as shown in "+OutFileLabel+" subpanel."],
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
    let category = [AccLabel, SrcLabel, ConfigLabel, OutFileLabel];
    let prmlabels = {};
    prmlabels[AccLabel] = [AccPrmsLabel, AccLabelOrder];
    prmlabels[SrcLabel] = [SrcPrmsLabel, SrcLabelOrder];
    prmlabels[ConfigLabel] = [ConfigPrmsLabel, ConfigLabelOrder];
    prmlabels[OutFileLabel] = [OutputOptionsLabel, OutputOptionsOrder];

    let categarg = {};
    categarg[AccLabel] = "acc";
    categarg[SrcLabel] = "src";
    categarg[ConfigLabel] = "config";
    categarg[OutFileLabel] = "outfile";

    let details = {};
    details[AccLabel] = GetAccPrmList(true);
    details[SrcLabel] = GetSrcPrmList(true);
    details[ConfigLabel] = GetConfigPrmList(true);
    details[OutFileLabel] = GetOutputPrmList(true);

    let format = {};
    format[AccLabel] = GetFormat(AccPrmsLabel);
    format[SrcLabel] = GetFormat(SrcPrmsLabel);
    format[ConfigLabel] = GetFormat(ConfigPrmsLabel);
    format[OutFileLabel] = GetFormat(OutputOptionsLabel);

    let objects = {};

    for(const categ of category){
        let caption = "Keywords available in the 2nd argument (arg2) of Set(\""+categarg[categ]+
            "\", arg2, arg3) to change the parameters and options of "+categ+"."
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
            if(keys[j] == "bunchdata" || keys[j] == "fmap"){ // skip file parameter
                continue;
            }
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

function GetQString(str)
{
    return str;
}

module.exports = {
    GetBrowserIssue:GetBrowserIssue,
    GetPythonOption:GetPythonOption,
    GetMenuKey:GetMenuKey,
    GetAccKey:GetAccKey,
    GetUnitKey:GetUnitKey,
    GetMenuCateg:GetMenuCateg,
    GetParameterKey:GetParameterKey,
    GetAccPrmList:GetAccPrmList,
    GetSrcPrmList:GetSrcPrmList,
    GetConfigPrmList:GetConfigPrmList,
    GetOutputPrmList:GetOutputPrmList,
    GetOutDataInf:GetOutDataInf,
    HelpURL:HelpURL,
    PySampleURL:PySampleURL,
    Version2Digit:Version2Digit,
    AccLabel:AccLabel,
    SrcLabel:SrcLabel,
    ConfigLabel:ConfigLabel,
    OutFileLabel:OutFileLabel
}
