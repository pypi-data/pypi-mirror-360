"use strict";

var header_tags = ["h1", "h2", "h3", "h4", "h5", "h6"];
var espcape_chars = ["&lambda;","&gamma","&epsilon;","&eta;","&beta;","&sigma;","&Sigma;"];

const CalcTypeLabel = "Calculation Type";
const AccTypeCaption = "Accelerator Type";
const SrcTypeCaption = "Light Source Type";
const CalcProcessLabel ="Calculation Status/Processes";

const SpectraUILabel = GetSoftName("spectra-ui");

function FormatHTML(htmlstr)
{
    let formathtml = htmlstr
        .replace(/<tbody>/g, "<tbody>\n\n")
        .replace(/<tr>/g, "<tr>\n")
        .replace(/<\/tr>/g, "</tr>\n")
        .replace(/<\/td>/g, "</td>\n")
        .replace(/<\/h1>/g, "</h1>\n")
        .replace(/<\/h2>/g, "</h2>\n")
        .replace(/<\/h3>/g, "</h3>\n")
        .replace(/<\/h4>/g, "</h4>\n")
        .replace(/<\/h5>/g, "</h5>\n")
        .replace(/<\/h6>/g, "</h6>\n")
        .replace(/<p>/g, "\n<p>")
        .replace(/<\/p>/g, "</p>\n")
        .replace(/<\/table>/g, "</table>\n\n");
    return formathtml;
}

function SetRemarks(categ, captions)
{
    let data ="";
    for(let j = 0; j < captions.length; j++){
        let capp = document.createElement("p");
        capp.innerHTML = captions[j];
        capp.id  = categ+(j+1).toString();
        data += capp.outerHTML;
    }
    return data;
}

function GetQString(str)
{
    return "\""+str+"\"";
}

function GetLink(href, caption, isel, isURL = false)
{
    let link = document.createElement("a");
    if(isURL){
        link.href = href;
    }
    else{
        link.href = "#"+href;
    }
    link.innerHTML = caption;
    if(isel){
        return link;
    }
    return link.outerHTML;
}

function RetrieveEscapeChars(label)
{
    let fchars = [];
    let iini, ifin = 0;
    do{
        iini = label.indexOf("&", ifin);
        if(iini >= 0){
            ifin = label.indexOf(";", iini);
            if(ifin < 0){
                ifin = iini+1;
                continue;
            }
            let fchar = label.substring(iini , ifin+1);
            if(fchars.indexOf(fchar) < 0){
                fchars.push(fchar);
            }
        }    
    } while(iini >= 0);
    return fchars;
}

function RetrieveAllEscapeChars(prmlabels)
{
    let escchars = [];
    for(let j = 0; j < prmlabels.length; j++){
        let labels = Object.values(prmlabels[j]);
        for(let i = 0; i < labels.length; i++){
            let fchars = RetrieveEscapeChars(labels[i][0]);
            for(let k = 0; k < fchars.length; k++){
                if(escchars.indexOf(fchars[k]) < 0){
                    escchars.push(fchars[k]);
                }    
            }
        }
    }
    return escchars;
}

function ReplaceSpecialCharacters(espchars, org)
{
    let ret = org;
    let div = document.createElement("div");
    for(let j = 0; j < espchars.length; j++){
        div.innerHTML = espchars[j];
        let spchar = div.innerHTML;
        while(ret.indexOf(spchar) >= 0){
            ret = ret.replace(spchar, espchars[j]);
        }    
    }
    return ret;
}

function WriteParagraph(phrases)
{
    let data = "";
    for(let j = 1; j < phrases.length; j++){
        let p = document.createElement("p");
        p.innerHTML = phrases[j];
        data += p.outerHTML;
    }
    return data;
}

function WriteListedItem(items, isnumber)
{
    let data;
    let ol = document.createElement(isnumber?"ol":"ul");
    for(let j = 1; j < items.length; j++){
        let li = document.createElement("li");
        li.innerHTML = items[j];
        ol.appendChild(li);
    }
    data = ol.outerHTML;
    return data;
}

function WriteFigure(src, figcaption, width = null)
{
    let fig = document.createElement("figure");
    fig.id = src;
    let img = document.createElement("img");
    img.src = src;
    if(width == null){
        if(ImageWidths.hasOwnProperty(src)){
            let width = 2*ImageWidths[src]/3;
            if(src == "segscheme.png" 
                || src == "spatialgrid.png" 
                || src == "slittype.png" 
                || src == "surfacepd.png" 
                || src == "surfacepd_point.png"
                || src == "fourieplane.png"
                || src == "volpdens.png"
            ){
                width = ImageWidths[src]/3;
            }
            else if(src == "felsteps.png"){
                width = ImageWidths[src]/4;
            }
            else if(src == "BMsetup.png"){
                width = ImageWidths[src]/2;
            }
            img.style.width = Math.floor(width).toString()+"px";
        }
    }
    else{
        img.style.width = Math.floor(width).toString()+"px";
    }
    let caption = document.createElement("figcaption");
    caption.innerHTML = figcaption;
    fig.appendChild(img);
    fig.appendChild(caption);
    return fig.outerHTML;
}

function GetSoftName(name)
{
    let ndiv = document.createElement("span");
    ndiv.innerHTML = name;
    ndiv.classList = "software";
    return ndiv.outerHTML;
}

function WriteObject(layer, obj)
{
    let value;
    let data = "";
    if(Array.isArray(obj) == true){
        value = CopyJSON(obj);
    }
    else{
        let key = Object.keys(obj)[0];
        value = Object.values(obj)[0];
    
        layer = Math.min(layer, header_tags.length-1);
        let hdr = document.createElement(header_tags[layer]);
        hdr.innerHTML = key;
        hdr.id = key;
        data += hdr.outerHTML;
    
        if(typeof value == "string" && value.indexOf("@") >= 0){
            data += value;
            return data;
        }
        else if(Array.isArray(value) == false){
            data += "Error";
            alert("Error"+value);
            return data;
        }   
    }

    if(value[0] == "Paragraph"){
        data += WriteParagraph(value);
        return data;
    }
    else if(value[0] == "NumberedItem"){
        data += WriteListedItem(value, true);
        return data;
    }
    else if(value[0] == "ListedItem"){
        data += WriteListedItem(value, false);
        return data;
    }

    for(let j = 0; j < value.length; j++){
        if(typeof value[j] != "string"){
            data += WriteObject(layer+1, value[j]);
        }
        else if(value[j].indexOf("<img") >= 0){
            data += value[j];
        }
        else{
            let p = document.createElement("p");
            p.innerHTML = value[j];
            data += p.outerHTML;
        }
    }
    return data;
}

function AppendCell(row, item, classname = "")
{
    if(item == null){
        return null;
    }
    let cell = row.insertCell(-1);
    if((typeof item) == "string"){
        cell.innerHTML = item;
    }
    else if(Array.isArray(item)){
        cell.innerHTML = WriteObject(0, item);
//        cell.innerHTML = item.join(",");
    }
    else{
        let cols = 1;
        let rows = 1;
        if(item.hasOwnProperty("cols")){
            cols = item.cols;
        }
        if(item.hasOwnProperty("rows")){
            rows = item.rows;
        }
        if(cols > 1 || rows > 1){
            cell.innerHTML = item.label;
            if(cols > 1){
                cell.setAttribute("colspan", cols);
            }
            if(rows > 1){
                cell.setAttribute("rowspan", rows);
            }
        }
        else{
            cell.innerHTML = WriteObject(0, item);
        }
    }
    if(classname != ""){
        cell.className = classname;
    }
    return cell;
}

function GetTable(captext, titles, data, subtitles = null)
{
    let cell, rows = [];
    let table = document.createElement("table");

    if(captext != ""){
        let caption = document.createElement("caption");
        caption.innerHTML = captext;
        table.caption = caption;    
    }

    rows.push(table.insertRow(-1)); 
    for(let j = 0; j < titles.length; j++){
        AppendCell(rows[rows.length-1], titles[j], "title");
    }
    if(subtitles != null){
        rows.push(table.insertRow(-1)); 
        for(let j = 0; j < subtitles.length; j++){
            AppendCell(rows[rows.length-1], subtitles[j], "title");
        }    
    }

    for(let j = 0; j < data.length; j++){
        rows.push(table.insertRow(-1));
        for(let i = 0; i < titles.length; i++){
            cell = AppendCell(rows[rows.length-1], data[j][i]);            
        }
        if(data[j].length > titles.length && cell != null){
            // set the id of this cell
            cell.id = data[j][titles.length]
        }
    }
    let retstr = table.outerHTML;
    return retstr;    
}

function GetMenuCommand(menus)
{
    let qmenus = [];
    for(let j = 0; j < menus.length; j++){
        qmenus.push("["+menus[j]+"]");
    }
    return qmenus.join("-");
}

function GetDirectPara(str)
{
    let div = document.createElement("div");
    div.innerHTML = "<pre><code>"+str+"</code></pre>";
    div.className = "direct";
    return div.outerHTML;
}

function GetTableBody(tblstr, ishead, isfoot)
{
    let tblinner = tblstr;
    if(!ishead){
        tblinner = tblinner
            .replace("<table>", "")
            .replace("<tbody>", "");
    }
    if(!isfoot){
        tblinner = tblinner
            .replace("</table>", "")
            .replace("</tbody>", "");
    }
    return tblinner;
}

// main body
var chapters = {
    copyright: "Copyright Notice",
    intro: "Introduction",
    gui: "Operation of the GUI",
    prmlist: "Parameter List",
    calcsetup: "Calculation Setup",
    spcalc: "Advanced Functions",
    format: "File Format",
    standalone: "Standalone Mode",
    python: "Python User Interface",
    ref: "References",
    ack: "Acknowledgements"
}

var sections = {
    overview: "Overview",
    start: "Getting Started",
    main: "Main Parameters",
    postproc: "Post-Processing",
    preproc: "Pre-Processing",
    dataimp: "Data Import",
    plotlyedit: "Edit the Plot",
    json: "JSON Format",
    compplot: "Comparative Plot",
    multiplot: "Multiple Plot",
    mdplot: "Plotting 3/4-Dimensional Data",
    scan: "Scanning a Parameter",
    ascii: "Export as ASCII",
    save: "Save",
    prmset : PSNameLabel,
    setupdlg: "Setup Dialogs",
    outitems: "Output Items",
    ppcomp: "Parallel Computing Support",
    input: "Input Format",
    accobj: AccLabel+" Object",
    srcobj: SrcLabel+" Object",
    confobj: ConfigLabel+" Object",
    outfobj: OutFileLabel+" Object",
    output: "Output Format",
    pdata: PPPartAnaLabel,
    flddata: "Magnetic data format for custom sources",
    binary: "Binary Format for the Modal Profile",
    separa: "Separability",
    degcoh: "Degree of Spatial Coherence",
    phaseerr: "Analytical Method to Evaluate the Harmonic Intensity",
    kxyscan: "Notes on Scanning &epsilon;<sub>1st</sub>",
    howtocmd: "How to Do?"
}

var refidx = {};
var referencelist = GetReference(refidx);
var Version2Digit = Version.split(".").slice(0, 2).join(".");

var help_body = 
[
    {
        [chapters.copyright]: [
            "Paragraph",
            "<em>Copyright 1998-2024 Takashi Tanaka</em>",
            "This software is free for use, however, the author retains the copyright to this software. It may be distributed in its entirety only and may not be included in any other product or be distributed as part of any commercial software.", 
            "This software is distributed with <em>NO WARRANTY OF ANY KIND</em>. Use at your own risk. The author is not responsible for any damage done by using this software and no compensation is made for it.",
            "This software has been developed, improved and maintained as voluntary work of the author. Even if problems and bugs are found, the author is not responsible for improvement of them or version up of the software.",
            "<em>If you are submitting articles to scientific journals with the results obtained by using this software, please cite the relevant references.</em> For details, refer to "+GetLink(chapters.intro, chapters.intro, false)+"."
        ]
    },
    {
        [chapters.intro]: [
            "This document describes the instruction to use the free software SPECTRA, a synchrotron radiation (SR) calculation code, and is located in \"[SPECTRA Home]/help\", where \"[SPECTRA Home]\" is the directory where SPECTRA has been installed. Brief explanations on the software and numerical implementation of SR calculation are given here, together with a simple instruction of how to get started. Note that <a href=\"https://www.mathjax.org/\">"+GetQString("MathJax")+"</a> javascript library is needed to correctly display the mathematical formulas, which is available online. If you need to read this document offline, "+GetQString("MathJax")+" should be installed in \"[SPECTRA Home]/help\" directory.",
            {
                [sections.overview]: [
                    "Paragraph",
                    "SPECTRA is a computer program to numerically evaluate the characteristics of radiation emitted from various synchrotron radiation (SR) sources, such as bending magnets and insertion devices (IDs, i.e., wigglers and undulators). In addition, SR sources with arbitrary magnetic fields are available by importing the magnetic field data prepared by the user. This makes it possible to estimate the real performance of the SR source by using the magnetic field distribution actually measured by field measurement instruments such as Hall probes.",
                    "To compute the characteristics of radiation and evaluate the performances of SR sources, a large number of parameters are required to specify the electron beam, light source, observation conditions, and options for numerical operations. SPECTRA is equipped with a fully graphical user interface (GUI) which facilitates configurations of them. In addition, a post-processor is included to verify the computation results graphically. Since version 11.0, the GUI is written based on the web technologies, i.e., HTML, CSS and Javascript, with the assistance of \"node.js\" and \"tauri\" to build a standalone application. For visualization of calculation results and imported data, \"Plotly\" library is used. Thanks to portability of these libraries, SPECTRA will run on most of the platforms such as Microsoft Windows, Macintosh OS X and Linux. SPECTRA does not require any other commercial software or libraries.",
                    "The numerical part of SPECTRA (\"solver\") is written in C++11 with the standard template library (STL). For bending magnets, wigglers and undulators, numerical implementation is based on the well-known expressions on SR, and the so-called far-field approximation is available for fast computation. For more accurate evaluation, expressions on SR in the near-field region are used for numerical computation. In this case, characteristics of SR emitted from both the ideal- and arbitrary-field devices can be calculated. For details of numerical implementation, refer to "+GetLink("spectrajsr", refidx.spectrajsr, false)+" and "+GetLink("spectrasri", refidx.spectrasri, false)+". The users who are publishing their results obtained with SPECTRA are kindly requested to cite "+GetLink("spectra11jsr", refidx.spectra11jsr, false)+".",
                    "Before ver. 7.2, the magnetic field was assumed to be constant in the transverse (x-y) plane. In other words, only the dipole components were taken into account. This considerably simplifies the numerical algorithm not only in the trajectory calculation but also in the spatial integration to take into account the finite electron beam emittance. In ver. 8.0, an arbitrary magnetic field has been supported to enable the evaluation of the effects due to quadrupole magnets between undulator segments and the undulator natural focusing, which would be significant for low-energy electrons. In ver. 9.0, an arbitrary electron bunch profile has been supported. The user can specify the longitudinal bunch profile, or import the macroparticle coordinates in the 6D phase space, which is usually created by the start-to-end simulation for accelerators.",
                    "In ver. 10.0, a new function to compute the photon flux density in the 4D phase space (x,x',y,y') has been implemented"+GetLink("refwigner", refidx.refwigner, false)+", which enables the rigorous estimation of the brilliance (brightness) of typical SR sources and the photon distribution at the source point to be utilized in other computer codes for ray-tracing simulations. Based on the phase-space density computed with this function, a numerical scheme to decompose the partially-coherent radiation into a number of coherent modes (coherent mode decomposition: CMD)"+GetLink("refcmd", refidx.refcmd, false)+" has been later implemented in version 10.1, which is explained in more detail "+GetLink(MenuLabels.CMD, "here", false)+". The users who are publishing their results obtained using these numerical schemes are kindly requested to cite the relevant references. Also implemented in ver. 10.1 is a function to compute the surface power density, which is convenient to compute the heat load on the inner wall of a vacuum chamber located near the SR source and exposed to SR with a shallow incident angle.",
                    "In ver. 11.0, the solver has been widely revised to be consistent with the C++11 standard and to facilitate the maintenance and bug fix. A new function has been also implemented to compute the volume power density; this is to evaluate the heat load of SR incident on an object, which gradually decays while it transmits the object. The output data will probably be used later for heat analysis of high heat-load components in the SR beamline based on the finite element method. In addition to the above revisions, two important upgrades have been made in ver. 11. First, the format of the input parameter file has been changed from the original one (and thus not readable in other applications) to JSON (JavaScript Object Notation) format. Because the output data is also given by a JSON file, it is now easy to communicate with other 3rd-party applications. Second, the framework (GUI library) has been switched to those based on web technologies (HTML, CSS, and JavaScript). This enhances the portability between different platforms (operating systems).",
                    "In ver. 12.0, the python support, which was experimentally implemented in ver 11.0, has been extensively enhanced. Python package as a user interface to communicate with the SPECTRA GUI has been developed and is available from the Python Package Index repository (by a normal pip command). Note that this function is based on \"Selenium\" framework that is usually used to automatically operate the web browser. For details about how it works, refer to "+GetLink(chapters.python, chapters.python, false),
                    "Following the enhancement of the python support deseribed abvove, an imporant decision has been made in ver. 12.0 regarding the support for Linux platforms; because of the too diverse versions of relevant (not only GUI but also core) libraries, it is almost impossible to prepare the conventional desktop application to support all the potential distributions. Thus, only one package compiled on Ubuntu 20.04, which can be installed through dpkg/apt, is prepared as of May 2024. The users of other Linux distributions are kindly recommended to try the python version."
                ]
            },
            {
                [sections.start]: [
                    "NumberedItem",
                    "Open a parameter file by running "+GetMenuCommand([MenuLabels.file, MenuLabels.open])+" command, or run "+GetMenuCommand([MenuLabels.file, MenuLabels.new])+" command to start with a new parameter set.",
                    "Select the calculation type from submenus in "+GetMenuCommand([MenuLabels.calc])+".",
                    "Edit the parameters if necessary and specify the directory and data name to save the calculation results.",
                    "Run "+GetMenuCommand([MenuLabels.run, MenuLabels.start])+" command to start a calculation with current parameters.",
                    "A \"Progressbar\" appears to inform the calculation status.",
                    "To verify the calculation results after completion of the calculation, click "+GetQString(sections.postproc)+" tab, select the name of the output file and item(s) to check for visualization. Refer to "+GetLink(sections.postproc, sections.postproc, false)+" for details."
                ]
            }
        ]
    },
    {
        [chapters.gui]: [
            "SPECTRA GUI is composed of three tabbed panels entitled as "+GetQString(sections.main)+", "+GetQString(sections.preproc)+", and "+GetQString(sections.postproc)+", which are explained in what follows.",
            {
                [sections.main]: [
                    "The "+GetQString(sections.main)+" tabbed panel is composed of a number of subpanels entitled as "+GetQString(AccLabel)+", "+GetQString(SrcLabel)+", "+GetQString(ConfigLabel)+", "+GetQString(OutFileLabel)+", and "+GetQString(CalcProcessLabel)+". Note that the "+GetQString(AccLabel)+", "+GetQString(SrcLabel)+GetQString(OutFileLabel)+" subpanels are always displayed, while the others are shown when necessary.",
                    WriteFigure("main.png", "Example of the "+GetQString(sections.main)+" tabbed panel."),
                    {
                        [AccLabel+" Subpanel"]: [
                            "Display and edit the parameters and numerical conditions related to the electron beam. For details, refer to "+GetLink(AccLabel, AccLabel+" "+chapters.prmlist, false)+"."
                        ]
                    },
                    {
                        [SrcLabel+" Subpanel"]: [
                            "Display and edit the parameters and numerical conditions related to the light source. For details, refer to "+GetLink(SrcLabel, SrcLabel+" "+chapters.prmlist, false)+"."
                        ]
                    },
                    {
                        [ConfigLabel+" Subpanel"]: [
                            "Display and edit the parameters and numerical conditions related to the observation of radiation. For details, refer to "+GetLink(ConfigLabel, ConfigLabel+" "+chapters.prmlist, false)+"."
                        ]
                    },
                    {
                        [OutFileLabel+" Subpanel"]: [
                            "Specify the path, name and format of the output file.",
                            "@outfile",
                            "Note that a spread sheet "+GetQString(OutputOptionsLabel.fixpdata[0])+" is shown in this subpanel, if "+GetQString(FixedPointLabel)+" is selected as the calculation type. Click "+GetQString(MenuLabels.start)+" to start a calculation using current parameters and options, then the results are displayed when it is completed."
                        ]
                    },
                    {
                        [CalcProcessLabel+" Subpanel"]: [
                            "Display the status of a calculation in progress, or the list of "+GetLink(CalcProcessLabel, CalcProcessLabel, false)+". Click "+GetQString(CancelLabel)+" to stop the calculation currently running, "+GetQString(CancellAllLabel)+" to terminate all the calculations, and "+GetQString(RemoveLabel)+" to remove the selected process."
                        ]
                    }
                ]
            },
            {
                [sections.preproc]: [
                    "The "+GetQString(sections.preproc)+" tabbed panel assists the pre-processing, or the arrangement of numerical conditions not displayed in the "+GetQString(sections.main)+" panel.",
                    {
                        [sections.dataimp]: [
                            "Import a data set prepared by the user, which is necessary for several types of calculations. The types of data sets available in SPECTRA are summarized below.",
                            "@import",
                            "Meanings of the items and variables are as follows.",
                            [
                                "ListedItem",
                                "time: arrival time, or longitudinal position along the electron bunch",
                                "DE/E: normalized energy deviation (dimensionless)",
                                "I: beam current (A)",
                                "j: beam current density (A/100%)",
                                "z: longitudinal coordinate along the beam axis",
                                "Bx,By: horizontal and vertical magnetic fields",
                                "Gap: gap of the ID",
                                "Depth: depth positions where the Volume Power Density is calculated"
                            ],
                            "The unit of j may need to be explained; it is given as the current per unit energy band; in a mathematical form, \\[I(t)=\\int j\\left(t, \\frac{DE}{E}\\right) d\\frac{DE}{E}\\]",
                            "The format of the ASCII file for the 1D data is as follows (magnetic field distribution as an example)",
                            GetDirectPara("z\tBx\tBy\n-8.959978e-01\t5.174e-05\t7.035e-06\n-8.949972e-01\t5.423e-05\t7.062e-06\n-8.939967e-01\t5.646e-05\t7.244e-06\n\t\t(omitted)\n 8.979989e-01\t4.801e-05\t6.639e-06\n 8.989994e-01\t4.582e-05\t6.327e-06\n 9.000000e-01\t4.409e-05\t6.456e-06\n"),
                            "The 1st line (title) is optional. In the above format, the interval of the independent variable (z) does not have to be necessarily constant, which is not the case for the 2D data; the format should as follows",
                            GetDirectPara("time\tDE/E\tj\n-1.0e-3\t-0.01\t0.001\n-0.9e-3\t-0.01\t0.002\n-0.8e-3\t-0.01\t0.003\n    (omitted)\n0.8e-3\t-0.01\t0.003\n0.9e-3\t-0.01\t0.002\n1.0e-3\t-0.01\t0.001\n-1.0e-3\t-0.008\t0.001\n-0.9e-3\t-0.008\t0.002\n-0.8e-3\t-0.008\t0.003\n    (omitted)\n0.8e-3\t-0.008\t0.003\n0.9e-3\t-0.008\t0.002\n1.0e-3\t-0.008\t0.001\n    (omitted)\n-1.0e-3\t0.01\t0.001\n-0.9e-3\t0.01\t0.002\n-0.8e-3\t0.01\t0.003\n    (omitted)\n0.8e-3\t0.01\t0.003\n0.9e-3\t0.01\t0.002\n1.0e-3\t0.01\t0.001\n"),
                            "For reference, such a data format is created in the C/C++ language as follows.",
                            GetDirectPara("for(n = 0; n < N; n++){\n  for(m = 0; m < M; m++){\n    cout << t[m] << \" \" << de[n] << \" \" <<  j[m][n] << endl;\n  }\n}"),
                            "Note that the order of the \"for loop\" is arbitrary; the 1st and 2nd lines can be swapped in the above example.",
                            "After preparing the ASCII file, click "+GetQString(MenuLabels.import)+" button and specify the file name in the dialog box to import it. The unit of each item should be chosen before importing, in the "+GetLink(MenuLabels.unit, MenuLabels.unit, false)+" dialog box that pops up by running "+GetMenuCommand([MenuLabels.edit, MenuLabels.unit])+" command or clicking "+ GetQString("Edit Units")+" button. Note that the unit of the imported data cannot be changed, so you need to import the data again with the correct unit in case a wrong unit has been chosen. Also note that the units of several items (I, j, DE/E) are fixed, and cannot be selected when importing."
                        ]
                    },
                    {
                        "Visualization": [
                            "After importing, the data sets can be visualized to verify if the configurations (unit and format of the data file) are correct. An example is shown below.",
                            WriteFigure("preproc.png", "Example of the "+GetQString(sections.preproc)+" tabbed panel. The relation between the gap and magnetic field amplitude of an undulator is plotted in this example."),
                            "Besides the imported data sets as described above, there exist a number of items that can be visualized, which are listed in the top left of this subpanel. Just click one of them for visualization. Note that several of them are available only under specific conditions, which are summarized below.",
                            "@preproc",
                            {
                                [sections.phaseerr] : [
                                    "It is well known that the effects due to magnetic errors in undulators can be evaluated using an analytical formula \\[I_r/I_0=\\exp(-k^2\\sigma_{\\phi}^2),\\] where $I_0$ means the photon intensity available with an ideal condition, $I_r$ means that in a real condition with magnetic errors, $k$ is the harmonic number, and $\\sigma_{\\phi}$ is the RMS phase error.", 
                                    "Although the above formula is valid for radiation emitted by a single electron observed on axis (with an infinitely narrow angular acceptance), it overestimates the effects due to magnetic errors in a more realistic condition that the electron beam emittance and energy spread are finite, and/or the the angular acceptance in the beamline is not narrow; these factors effectively work to recover the normalized intensity $I_r/I_0$. To estimate $I_r/I_0$ with these recovery factors, an alternative method "+GetLink("refunivperr", refidx.refunivperr, false)+" can be used, whose results are shown together with those using the conventional method."
                                ]
                            }
                        ]
                    }, 
                    {
                        [sections.pdata]: [
                            GetQString(sections.pdata)+" pre-processing operation is available when "+GetQString(CustomParticle)+" is selected as "+GetQString(AccPrmsLabel.bunchtype[0])+", as shown below. Note that the user needs to specify in advance the data file containing the macroparticle positions in the 6D phase space, which is usually generated by another simulation code. Refer to "+GetLink(AccPrmsLabel.bunchdata[0], AccPrmsLabel.bunchdata[0], false)+" for details.",                        
                            WriteFigure("ppparticle.png", "Example of the "+chapters.prep+" tab panel, under the process of "+GetQString(sections.pdata)),
                            "Once "+GetQString(AccPrmsLabel.bunchtype[0])+" is specified, SPECTRA automatically loads the file to analyze the particle data. For convenience, part of the data file is shown in "+GetQString("File Contents")+" Select the unit and column index for each coordinate variable of the 6D (x,x',y,y',t,E) phase space and input relevant parameters. In the above example, each macroparticle has the charge of 3.5fC with \"x\" coordinate (horizontal position) located in the 1st column and the unit of m. Note that"+GetQString("Slices in 1&sigma;<sub>s</sub>")+" specifies the number of bins in the  RMS bunch length, to be used for data analysis. Then, additional configurations appear in the GUI to specify how to visualize the results of analysis. In the above example, the current profile is plotted. Upon revision of the configurations above, SIMPLEX automatically analyzes the data with the new configuration and visualizes the result.",
                            "Besides the slice parameters shown in the above example, macroparticle distributions can be directly plotted. For example, distribution in the (E-t) phase space is plotted in the figure below.",
                            WriteFigure("ppparticle2.png", "Example of "+GetQString(sections.pdata)+" pre-processing operation: particle distribution in the (E-t) phase space is plotted."),
                            "The result of analysis can be exported and saved as an ASCII file; "+GetQString("Export Selected")+" exports the data currently plotted, while "+GetQString("Export Slice Data")+" exports the whole slice data (slice paramters vs. s). The exported data file  can be used later as the custom data file for slice parameters or current profile."
                        ]
                    },                    
                ]
            },
            {
                [sections.postproc]: [
                    "The "+GetQString(sections.postproc)+" tabbed panel assists the user to visualize the calculation results. The output file is automatically loaded upon completion of a calculation, or alternatively, the existing output files can be imported. To do so, click "+GetQString("Import")+" button and specify the path of the output file.",
                    WriteFigure("postproc.png", "Example of the "+sections.postproc+" tabbed panel, showing the energy spectrum of the flux density."),
                    "For visualization, select more than one item from "+GetQString("Items to Plot")+". The dimension of the plot depends on the calculation type of the loaded file. In a 1D plot, a desired area can be zoomed in by dragging. Other options are available to operate the plot, by clicking one of the small icons located in the right top of the plot. For details, refer to the documents about "+GetQString("Plotly")+" library to be found online.",
                    "Besides the above options, the plot can be configured in a dialog panel that appears by clicking a small icon (pencil) located in the top right of the plot. Options available are as follows; switch the scale (linear or log), change the 2D plot type (contour, color-scale surface or shaded surface), or change the method of scaling in each frame for multidimensional plot (see below).",
                    {
                        [sections.compplot]: [
                            "If more than one output file with the same calculation type is loaded, "+GetQString(sections.compplot)+" is available, and possible data names are shown. Click the desired ones to compare the results. Note that 1D data sets are shown in the same plot, however, 2D data sets are plotted separatory and thus more than one plots are shown. How to arrange the plots can be specified by "+GetQString(PlotWindowsRowLabel)+" parameter. If there are 6 plots in total and this parameter is set to 3, they are arranged in 3 columns times 2 rows."
                        ]
                    },
                    {
                        [sections.multiplot]: [
                            "This option is available for more than two data sets having different calculation types and thus "+GetQString(sections.compplot)+" is not available. It tries to create a number of plots and display in the plot area. How to arrange the plots can be specified by "+GetQString(SubPlotsRowLabel)+" parameter. If there are 6 plots in total and this parameter is set to 3, they are arranged in 3 columns times 2 rows."
                        ]
                    },
                    {
                        [sections.mdplot]: [
                            "There exist a number of calculation types to generate 3D or 4D output data in SPECTRA (including the "+GetLink(sections.scan, sections.scan, false)+" option), which cannot be plotted in a straightforward manner. In SPECTRA, the 3D/4D data are \"sliced\" into a number of data sets and plotted as a 1D or 2D graph. As an example, let us consider the visualization of a Wigner function calculated in the 4D phase space (X,X',Y,Y'). SPECTRA offers several combinations for plotting and slicing variables. If a pair (X,X') is chosen as the plotting variable, then the data is sliced at each (Y,Y') position, and 2D plot (Brilliance vs X,X') is created. Note that the coordinates of the slicing variables can be arbitrary chosen within the possible range, by dragging the sliders indicating their positions."
                        ]
                    },
                    "The post-processed output data can be saved as another JSON file in two methods explained below.",
                    {
                        [sections.ascii]: [
                            "The visualization result, or the data set(s) currently plotted, are exported as an ASCII file."
                        ]
                    },
                    {
                        [sections.save]: [
                            "The plot configurations together with the output data are saved in a JSON file. The file can be later imported by the post-processor to reproduce the plot."
                        ]
                    }
                ]
            },
            {
                [sections.prmset]: [
                    "In SPECTRA, parameters and numerical conditions displayed in the "+GetQString(AccLabel)+", "+GetQString(SrcLabel)+" and "+GetQString(ConfigLabel)+" subpanels are separately saved in JSON objects, each of which is referred to as a "+sections.prmset+". For example, "+GetQString(AccLabel+" "+sections.prmset)+" means a JSON object that stores the parameters displayed in the "+GetQString(AccLabel)+" subpanel. In addition, "+GetQString(BLLabel+" "+sections.prmset)+" is available to bundle the three "+sections.prmset+"s, which represent a \"beamline\" in a specific SR facility. Each "+sections.prmset+" can be switched from one to another by selecting from the submenus in "+GetQString(sections.prmset)+" main menu. To configure (rename, duplicate, or delete) the parameter sets, run Edit menu command. Then a modal dialog box pops up to show the current contents of all the parameter set as shown below.",
                    WriteFigure("editprmset.png", "Example of the dialog to edit the parameter sets."),
                    "Select the target item for configuration; in the above example, "+GetQString(BLLabel+" bl03")+" is the target parameter set. Click one of the buttons for operation; for example, to rename or duplicate the parameter set currently in selection, enter a new name in the text entry box in the left bottom and click [Rename] or [Duplicate] button. To delete the parameter set, click [Delete] button; note that at least one parameter set should be left."
                ]
            },
            {"Menu Commands": [
                {[MenuLabels.file]:["@filemenu"]},
                {[MenuLabels.calc]:["Select the type of calculation. Refer to "+GetLink(CalcTypeLabel, CalcTypeLabel, false)+" for details."]},
                {[MenuLabels.run]:["@runmenu"]},
                {[sections.prmset]:["Select and edit the "+GetQString(sections.prmset)+", Refer to "+GetLink(sections.prmset, sections.prmset, false)+" for details."]},
                {[MenuLabels.edit]:["Open one of the "+GetLink(sections.setupdlg, sections.setupdlg, false)+" to set up various configurations, not included in the "+sections.prmset+"s."]},
                {[MenuLabels.help]:["Open the reference manual or show the information about SPECTRA."]}
            ]},
            {"Setup Dialogs": [
                "Open a dialog to edit miscellaneous parameters besides those displayed in the main panel. Details of each dialog are explained below.",
                "@setupdlg"
            ]},
            {[sections.plotlyedit]: [
                "Besides standard Plotly.js configurations, a number of options to edit the graphical plot in the post- and pre-processors are available. To do so, click the small icon located in the top-right side of the plot. Then a dialog box pops up to let the user edit the plot in the following configurations.",
                "@plotlyedit"
            ]}
        ]
    },
    {
        [chapters.prmlist]: [
            "All the parameters available in the subpanels of the "+GetQString(sections.main)+" panel are summarized below, for each subpanel.",
            {
                [AccLabel]: [
                    "@accprm"
                ]
            },
            {
                [SrcLabel]: [
                    "@srcprm",
                    {
                        [SrcTypeCaption]: [
                            "Details of the type of the light sources available in SPECTRA are summarized below.",
                            "@srctype"
                        ]
                    },
                    {
                        [sections.flddata]: [
                            "When one of the custom light sources ("+GetQString(CUSTOM_Label)+", "+GetQString(CUSTOM_PERIODIC_Label)+", and "+GetQString(FIELDMAP3D_Label)+") is chosen, the user should prepare a data file to import the magnetic data. The format of the data file depends on the ligt source and is summarized below.",
                            "@flddata"
                        ]
                    }
                ]
            },
            {
                [ConfigLabel]: [
                    "@confprm",
                    {
                        [sections.binary]: [
                            "The binary format to export the modal profile is defined below.",
                            [
                                "ListedItem",
                                "Integer (4 byte) $\\times\\:3$: $N_m$, $N_X$, $N_Y$",
                                "Double (8 byte) $\\times\\:2$: $\\Delta X$, $\\Delta Y$",
                                "Double (8 byte) $\\times\\:N_XN_Y$: 0-th Mode Profile Real Part",
                                "Double (8 byte) $\\times\\:N_XN_Y$: 0-th Mode Profile Imaginary Part",
                                "...",
                                "Double (8 byte)$\\times N_XN_Y$: ($N_m$-1)-th Mode Profile Imaginary Part",
                            ],
                            "where $N_m$ is the number of coherent modes, $\\Delta X$ and $N_{X}$ are the interval and number of positions along the horizontal (X) axis, and similar expressions for the vertical (Y) axis. The order index j in each array representing the real/imaginary part of the complex amplitude is given as \\[j=j_x+j_yN_X\\] where $j_x$ and $j_y$ refer to the order indices corresponding to the X and Y positions. To be specific, the X index changes first.",
                        ]
                    }
                ]
            }
        ]
    },
    {
        [chapters.calcsetup]: [
            "Details of how to setup and start the calculations are presented here, together with explanations of the type of calculations and output items available in SPECTRA.",
            {
                ["General Method"]: [
                    {
                        ["Open a Parameter File"]: [
                            "Upon being started, SPECTRA tries to load parameters from the parameter file that was opened last time. If successful, the parameters are shown in the "+GetQString(sections.main)+" panel. If SPECTRA is run for the first time after installation, default parameters will be shown. To open a new SPECTRA parameter file, run "+GetMenuCommand([MenuLabels.file, MenuLabels.open])+" command. In the initial setting, the parameter files are found in the directory \"[SPECTRA Home]/prm\" with a default suffix \"json\", where \"[SPECTRA Home]\" is the directory in which SPECTRA has been installed."
                        ]
                    },
                    {
                        ["Select a "+CalcTypeLabel]: [
                            "Before starting any calculation, "+GetQString(CalcTypeLabel)+" should be selected by running one of the submenus in "+GetMenuCommand([MenuLabels.calc])+". Refer to "+GetLink(CalcTypeLabel, CalcTypeLabel, false)+" for details of each calculation type."
                        ]
                    },
                    {
                        ["Arrange the Output File"]: [
                            "Arrange the output file to save the calculation results in the "+GetLink(OutFileLabel+" Subpanel", OutFileLabel, false)+" subpanel."
                        ]
                    },
                    {
                        [MenuLabels.start]:[
                            "Run "+GetMenuCommand([MenuLabels.run, MenuLabels.start])+" command to start a single calculation. Then "+GetQString(CalcProcessLabel)+" subpanel is displayed in the "+GetQString(sections.main)+" panel to indicate the progress of calculation. To cancel the calculation, click "+GetQString(CancelLabel)+" button. Note that the serial number is automatically incremented once the calculation is started, unless it is not negative (-1). This is to avoid the overlap of the output file name in performing successive calculations. When the calculation is completed, the "+GetQString(CalcProcessLabel)+" subpanel vanishes and the result is imported in the "+GetQString(sections.postproc)+" panel for visualization."
                        ]
                    },
                    {
                        ["Verify the Result"]: [
                            "Upon completion of a calculation, the output file is automatically loaded and one of the items is plotted in the "+GetQString(sections.postproc)+" subpanel to quickly view the results. Refer to "+GetLink(sections.postproc, sections.postproc, false)+" for details about how to operate the post-processor."
                        ]
                    }
                ]
            },
            {
                [CalcTypeLabel]: [
                    "To start any calculation in SPECTRA, the "+GetQString(CalcTypeLabel)+" should be specified first. This is shown as the submenus of "+GetMenuCommand([MenuLabels.calc])+" main menu in the GUI. The meanings and details of the submenus are summarized in the table below. After selection, the calculation type is shown in the top of the "+GetQString(ConfigLabel)+" subpanel, which is represented by a string given by concatenating a number of submenu items. Note that a \"double colon (::)\" is inserted between items for clarity.",
                    "@calctype",
                ]
            },
            {
                [sections.outitems]: [
                    "The output items specific to respective calculation types are summarized below.",
                    "@outitems"
                ]
            },
            {
                [CalcProcessLabel]: [
                    "To configure a number of calculations with different conditions, run "+GetMenuCommand([MenuLabels.run, "Create Process"])+" command every time you finish specifying all the parameters. Then the "+GetQString(CalcProcessLabel)+" subpanel appears in the "+GetQString(sections.main)+" panel to show the calculation list currently saved in a temporary memory. Repeat it until all the calculations are specified. Click "+GetQString(RemoveLabel)+" button to delete the selected process, or "+GetQString(CancellAllLabel)+" to clear out all the processes. Run "+GetMenuCommand([MenuLabels.run, MenuLabels.start])+" command to start the calculation processes, then a progressbar is displayed to show the status of each process."
                ]
            },
            {
                [sections.scan]: [
                    "Besides the method described above, it is possible to configure a lot of "+CalcProcessLabel+" at once by scanning a specific parameter. To do so, right click the target parameter in one of the subpanels after selecting the "+CalcTypeLabel+", and click "+GetMenuCommand(["Scan This Parameter"])+" in the context menu. Then specify the configurations for scanning in the dialog box as shown below. Note that the context menu does not pop up for parameters that cannot be used for scanning.",
                    WriteFigure("scanconfig.png", "Configuration for scanning a parameter."),
                    "Input the initial & final values, and number of points for scanning. For several parameters to be specified by an integer, scanning interval instead of the number of points should be given. Note that the "+GetQString("Bundle the output data")+" option is to bundle all the output data into a single output file, which can be retrieved later in the "+GetQString(sections.postproc)+" panel. The availability of this option depend on the selected "+CalcTypeLabel+".",
                    "If the target parameter forms a pair, such as &beta;<sub>x, y</sub> (horizontal and  betatron functions), the user is requested to select the dimension for scanning: "+GetMenuCommand(["Scan Parameter 1D/2D"])+". For the 2D scanning, configurations for the both parameters are needed.",
                    "After configuration, click "+GetQString("OK")+" button to create a "+GetQString(CalcProcessLabel)+". Then the specified parameters are saved in a temporary memory and the scanning process is saved in the calculation list. Run "+GetMenuCommand([MenuLabels.run, MenuLabels.start])+" command to start the calculation.",
                    {
                        [sections.kxyscan]: [
                            "When scanning the fundamental energy of undulators having both (horizontal and vertical) K values (K<sub>x</sub> and K<sub>y</sub>), such as elliptic undulators, the ratio of the two (K<sub>x</sub>/K<sub>y</sub>) depends on "+GetQString(SrcPrmsLabel.gaplink[0])+" option as summarized below.",
                            "@e1scan"
                        ]
                    }
                ]
            },
            {[sections.ppcomp]: [
                "SPECTRA supports parallel computing in two different methods: MPI (Message Passing Interface) and Multithread. To enable this option, refer to "+GetLink(MenuLabels.MPI, MenuLabels.MPI, false)+" setup dialog. Note that MPI is not available in the web-application version."
                ]
            }
        ]
    },
    {
        [chapters.spcalc]: [
            "Besides the fundamental properties of SR such as the flux and radiation power, which can be calculated in a rather straightforward manner, SPECTRA offers a method to evaluate a number of special characteristics of SR: "+MenuLabels.spdens+", "+MenuLabels.vpdens+", "+MenuLabels.srcpoint+", "+MenuLabels.CMD+". In what follows, details of them are explained.",
            {
                [MenuLabels.spdens]: [
                    "The surface power density is defined as the radiation power per unit surface area of the target object, which should be distinguished from the (normal) power density defined as the power per unit area of the transverse (x,y) plane. If the normal vector of the surface of the target object is parallel to z, there is no difference between the two. This is not the case when the normal vector is perpendicular to z; the surface power density in this configuration is much lower than the normal power density as easily understood.",
                    "Computation of the surface power density is usually much more complicated than that of the normal power density. This comes from the fact that the incident angle of SR largely depends on the longitudinal position where it is emitted, if the surface of the target object has a small glancing angle. This is not the case for computing the normal power density, where the incident angle is always nearly 90 degrees."
                ]
            },
            {
                [MenuLabels.vpdens]: [
                    "The volume power density is defined as the radiation power absorbed per unit volume in an object illuminated by radiation. In a mathematical form it is given by \\[\\frac{d^3P(x,y,D)}{dxdydD}=C\\int \\frac{d^2F(x,y,\\omega)}{dxdy}[1-\\mbox{e}^{-\\mu(\\omega)D}]\\mu_{en}(\\omega)d\\omega,\\] where $\\mu$ & $\\mu_{en}$ are the linear attenuation & energy absorption coefficients at the photon energy $\\hbar\\omega$, $D$ is the distance from the surface of the object (\"Depth\"), and $C$ is a unit conversion factor. Note that glancing-incidence conditions can be specified as explained in the <a href=\"#volpdens.png\">relevant parameters</a>."
                ]
            },
            {
                [MenuLabels.srcpoint]: [
                    "In contrast to other calculations in which the observation point is assumed to be located downstream of the light source, characteristics exactly at the source point (center of the light source, z=0) are evaluated in this calculation. This is possible by propagating the emitted radiation backward to the source point using wave optics. Two options are available as follows.",
                    {
                        [MenuLabels.wigner]:[
                            "The photon flux density in the phase space spanned by the spatial $(x,y)=\\boldsymbol{r}$ and angular $(x',y')=\\boldsymbol{r}'$ coordinates, which is referred to as the phase-space density and denoted by $d(x,y,x',y')$, is an important physical quantity to characterize SR as a light source. Its maximum value, which is known as brilliance or brightness, gives the information of how many coherent photons are available. Its distribution in the phase space is necessary to carry out the ray-trace simulation based on the geometrical optics.", 
                            "It is worth noting that the angular profile of SR in the far-field region is obtained by integrating $d(x,y,x',y')$ over $(x,y)$, while the spatial profile in the near-field region is obtained by integrating over $(x',y')$. Also note that these spatial and angular profiles can be computed directly from an analytical formulas based on classical electrodynamics. It should be noted, however, that there is no analytical method to calculate $d(x,y,x',y')$ directly from the first principle. The Wigner function $W(x,y,x',y')$ is introduced in SR formulation to solve this problem and makes it possible to compute $d(x,y,x',y')$ from the complex amplitude of radiation.",
                            "SPECTRA is equipped with several functions to compute the phase-space density not only for the single electron, but also for more practical conditions, i.e., the electron beam with finite emittance and energy spread. The resultant phase-space density can be computed as a function of various variables: photon energy, K value, and phase-space coordinates. For details of numerical implementation of the Wigner function, refer to "+GetLink("refwigner", refidx.refwigner, false)+".",
                            {
                                [MenuLabels.energy]: [
                                    "The phase-space density is calculated as a function of the photon energy with other conditions being fixed. In the case of undulator radiation, the target harmonic number should be specified as well."
                                ]
                            },
                            {
                                [MenuLabels.Kvalue]: [
                                    "The phase-space density of undulator radiation at a specific harmonic is calculated as a function of the undulator K value. Note that the photon energy should be given as a detuning parameter with respect to the exact harmonic energy. If the calculation is done on-axis (x=y=x'=y'=0), the resultant data are comparable to the brilliance roughly estimated by a Gaussian approximation, but are based on a more rigorous method using the Wigner function."
                                ]
                            },
                            {
                                [MenuLabels.phasespace]: [
                                    "The distribution of the phase-space density is calculated as a function of the phase-space coordinate variables: x, y, x', and y'. Five types of calculation conditions are available as follows.",
                                    [
                                        "NumberedItem",
                                        "X-X' (Sliced): $W(x,y_{fix},x',y_{fix}')$",
                                        "X-X' (Projected): $W_x(x,x')$",
                                        "Y-Y' (Sliced): $W(x_{fix},y,x_{fix}',y')$",
                                        "Y-Y' (Projected): $W_y(y,y')$",
                                        "X-X-Y-Y' : $W(x,y,x',y')$"
                                    ],
                                    "where $W_x$ is defined as \\[W_x=\\int\\!\\!\\!\\!\\int W(x,x',y,y')dydy',\\] and a similar expression for $W_y$."
                                ]
                            },
                            {
                                [MenuLabels.Wrel]: [
                                    "When the 4D phase-space density is calculated, two important properties related to the Wigner function method are available: separability and total degree of spatial coherence. The details of them are explained as follows.",
                                    "@wigrel",
                                    "Note that the above properties, $\\kappa$, $\\zeta$, $\\zeta_x$, and $\\zeta_y$ are evaluated by a simple summation of quadratic forms of Wigner functions given at a number of grid points specified by the user, and the accuracy of integration is not checked. The user is required to input the range and number of mesh that are sufficiently wide and large to obtain a reliable result. One solution is to first check the profile of the projected Wigner functions in the 2D phase space, then input these parameters."
                                ]
                            }
                        ]
                    },
                    {
                        [MenuLabels.sprof]:[
                            "Spatial profile of the photon density, i.e., the spatial flux density is computed at the source point. This may be useful when discussing the profile of the photon beam after focusing optical components in the SR beamline. To be more specific, the spatial profile computed with this scheme reproduces the photon beam profile at the focal point of the unit magnification optical system."
                        ]
                    }            
                ]
            },
            {
                [MenuLabels.CMD]: [
                    MenuLabels.CMD+" is a mathematical method to decompose the partially coherent radiation into a number of coherent modes. Because the propagation of each mode can be described by wave optics, designing the optical elements can be much more reliable than that with the conventional ray-tracing that is based on geometrical optics.",
                    {
                        ["Mathematical Form"]: [
                            "In the numerical CMD implemented in SPECTRA, the Wigner function $W$ is supposed to be approximated by $W'$ composed of several coherent modes, namely, \\[W'=f\\sum_{p=0}^{M}\\mathscr{W}(\\Psi_p,\\Psi_p),\\] with $\\mathscr{W}$ meaning an operator to calculate the Wigner function of the $p$-th order coherent mode, whose complex amplitude is represented by a function $\\Psi_p$, and $M$ is the maximum order of the coherent modes. The function $\\Psi_p$ is assumed top have a form \\[\\Psi_p=\\sum_{q=0}^{N_p}a_{h,j}\\phi_h(\\hat{x})\\phi_j(\\hat{y}),\\] with \\[\\phi_m(\\zeta)=\\frac{2^{1/4}}{\\sqrt{2^m m!}}\\mbox{e}^{-\\pi\\zeta^2}H_m(\\sqrt{2\\pi}\\zeta),\\] denoting the m-th order Hermite-Gaussian (HG) function, where $\\hat{\\boldsymbol{r}=(\\hat{x},\\hat{y})=(x/\\sqrt{\\pi}w_x,y/\\sqrt{\\pi}w_y)}$ is the normalized transverse coordinate, $a_{h,j}$ is the amplitude of the HG function of $\\phi_h(\\hat{x})\\phi_j(\\hat{y})$, $H_m$ is the Hermite polynomial of the order $m$, and $N_p$ denotes the maximum order of the HG modes in the p-th coherent mode. Note that the indices $h$ and $j$ are given as a function of the integer $q$ and order $p$. The coefficient $f$ and the dimension of $a_{h,j}$ are chosen arbitrarily as long as the above formulas are satisfied. In SPECTRA, they are determined so that $a_{h,j}$ is dimensionless, and \\[\\sum_{p=0}^{\\infty}\\int|\\Psi_p|^2d\\hat{\\boldsymbol{r}}=1\\] is satisfied. The purpose of the numerical CMD is to compute the coefficient $a_{h,j}$ so that the resultant Wigner function $W'$ well reproduces the original function $W$. For details of the CMD method in SPECTRA, refer to "+GetLink("refcmd", refidx.refcmd, false)+"."
                        ]
                    },
                    {
                        [sections.howtocmd]: [
                            "To perform the CMD in SPECTRA, follow the steps explained below.",
                            [
                                "ListedItem",
                                "Preparation of the Wigner Function: Before starting the CMD, the user should compute the Wigner function in the phase space. In addition to the 4D Wigner function $W(x,y,x',y')$, the projected ones ($W_x$ and $W_y$), are also available, in which case 1D modal functions are given in the target direction (horizontal or vertical). The range and number of points to calculate the Wigner function should be reasonably wide and large. Note that the JSON format should be chosen as the format of the "+GetLink(OutFileLabel+" Subpanel", "output file", false)+".",
                                "Load the Wigner Function: Open the JSON output file for the Winger function data generated in the above step, by running [File]-[Load Output File]-[Wigner Function for CMD] command. If the Wigner function data is successfully loaded, [CMD with the Wigner Function] menu is enabled under the [Select Calculation]-[Coherent Mode Decomposition] menu. Run it to show configurations for the CMD.",
                                "Arrange the Parameters: In the "+ConfigLabel+" subpanel, edit the parameters and options related to the CMD; refer to "+GetLink(CMDParameterLabel, CMDParameterLabel, false)+" for details. After configuration, run [Run]-[Start Calculation] command to start the CMD process.",
                                "Verify the Result: The results of the CMD, such as the modal amplitude $a_{h,j}$, maximum orders of the HG functions, and numerical errors in the CMD process, are save in the output file, which can be directly verified by opening the output file in any text editor.",
                                "Visualization: other data sets specified in the options before starting the CMD, such as the modal profiles and reconstructed Wigner functions, are saved as well, which can be visualized in the "+GetQString(sections.postproc)+" panel."
                            ]
                        ]
                    }
                ]
            },
            {
                [MenuLabels.propagate]: [
                    MenuLabels.propagate+" is a function to describe the propagation of synchrotron radiation using the Wigner function. In contrast to the conventional wavefront propagation based on the multi-electron or CMD scheme, it has a potential to complete the computation with a much shorter time. The basic concept has been proposed in 1980's and is found in "+GetLink("refwigprop", refidx.refwigprop, false)+". Besides simple porpagation in the drift space, two typical optical elements are available: single/double slit and ideal lens. Although the availability is currently limited, efforts are under way to extend the capability of this scheme to a wider variety of components.",
                    {
                        ["How to Do?"]: [
                            "To perform the wavefront propagation, follow the steps explained below.",
                            [
                                "ListedItem",
                                "Prepare and Load the Wigner Function: before starting, the Wigner function data should be generated and loaded. Refer to "+GetLink(sections.howtocmd, sections.howtocmd, true)+" for details.",
                                "Arrange the Parameters: In the "+ConfigLabel+" subpanel, edit the parameters and options related to the wavefront propagation; refer to "+GetLink(PropParameterLabel, PropParameterLabel, false)+" for details. After configuration, run [Run]-[Start Calculation] command to start the wavefront propagation process.",
                                "Verify the Result: The results of the CMD, such as the modal amplitude $a_{h,j}$, maximum orders of the HG functions, and numerical errors in the CMD process, are save in the output file, which can be directly verified by opening the output file in any text editor.",
                                "Visualization: other data sets specified in the options before starting the CMD, such as the modal profiles and reconstructed Wigner functions, are save as well, which can be visualized in the "+GetQString(sections.postproc)+" panel."
                            ]
                        ]
                    }        
                ]
            }
        ]
    },
    {
        [chapters.format]: [
            "Besides the operation based on the GUI, SPECTRA (more precisely, the solver) can be utilized to communicate with external codes for the so-called start-to-end simulations. This actually requires the knowledge of the format of the input and output files, which is explained in the followings.",
            {
                [sections.json]: [
                    "To deal with the many parameters and options, SPECTRA utilizes the JSON (JavaScript Object Notation) format, which is described by a number of \"objects\". The object contains a number of \"pairs\" formed by a \"key\" and \"value\", separated by a colon \":\", and should be enclosed by a curly bracket {}. The value can be one of the followings: number, array, string and (another) object. An example of the SPECTRA input file is as follows.",
                    GetDirectPara("{\n  \"Accelerator\": {\n    \"Energy (GeV)\": 8,\n    \"Current (mA)\": 100,\n    ....\n    \"Options\": {\n      \"Zero Emittance\": false,\n      \"Zero Energy Spread\": false\n    }\n  },\n  \"Light Source\": {\n    \"B (T)\": 0.33467954834861074,\n    \"&lambda;<sub>u</sub> (mm)\": 32,\n    ....\n  },\n  \"Configurations\": {\n    \"Distance from the Source (m)\": 30,\n    ....\n  },\n  \"Output File\": {\n    \"Comment\": \"\",\n    ....\n  }\n}"),
                    "In this example, four JSON objects are found, whose keys are "+GetQString(AccLabel)+", "+GetQString(SrcLabel)+", "+GetQString(ConfigLabel)+", and "+GetQString(OutFileLabel)+". The value of each object is also an object, which actually specifies the parameters and options, such as \"Energy (GeV)\": 8, denoting the energy of the electron beam to be 8 GeV.",
                    "For details of the JSON format, please refer to any document available online or found in the text."
                ]
            },
            {
                [sections.input]: [
                    "The input file to be loaded by the solver should have 4 JSON objects: "+GetQString(AccLabel)+", "+GetQString(SrcLabel)+", "+GetQString(ConfigLabel)+", and"+GetQString(OutFileLabel)+". Details of each object are summarized below, where \"GUI Notation\" is the parameter name displayed in the "+GetQString(MenuLabels.main)+" GUI panel, \"Key\" is the name of the key to be used in the input file, \"Format\" is the format of the value, and \"Default\" is the default value. Note that the key name can be either of the \"Full\" or \"Simplified\" expression.",
                    {
                        [sections.accobj]: [
                            "@accjson"
                        ]    
                    },
                    {
                        [sections.srcobj]: [
                            "@srcjson"
                        ]    
                    },
                    {
                        [sections.confobj]: [
                            "@confjson"
                        ]    
                    },
                    {
                        [sections.outfobj]: [
                            "@outjson"
                        ]    
                    }
                ]
            },

            {
                [sections.output]: [
                    "If \"JSON\" or \"Both\" is chosen as the \"Format\" option in the "+GetLink(OutFileLabel+" Subpanel", OutFileLabel)+" subpanel, a JSON format output file is generated after the calculation completes. Besides the visualization in the "+GetQString(sections.postproc)+" panel, it can be used for further processing with other external codes. To facilitate it, the structure of the output file is explained below. Note that the order index (for example of an array, column, etc.) in the followings is defined as starting from \"0\", but not from \"1\".",
                    {
                        [GetQString("Input")+" Object"]: ["All the parameters and options are stored in this object with the same format as the "+GetLink(sections.input, sections.input, false)+". If the output file is opened in the GUI (as an input parameter file), these parameters are displayed and can be used again."]
                    },
                    {
                        [GetQString("Output")+" Object"]: [
                            "The calculation results are stored in this object.",
                            "@outdata",
                            "The format of the \"data\" object (2D array) is as follows.",
                            [
                                "ListedItem",
                                "0th ~ (n-1)-th array: independent variables, where n is the dimension. The length of each array corresponds to the number of calculation points. For example, it is defined by \"Points (Energy)\" parameter for \"Energy Dependence\" calculations.",
                                "n-th ~ (n+m-1)-th array: calculated items, where m is the number of items. The length of each array corresponds to the product of the lengths of the independent variable arrays."
                            ],
                            "As an example, let us consider an \"Output\" object as follows",
                            GetDirectPara("\"Output\": {\n    \"dimension\": 1,\n    \"titles\": [\"Energy\",\"Flux Density\",\"GA. Brilliance\",\"PL(s1/s0)\",\"PC(s3/s0)\",\"PL45(s2/s0)\"],\n    \"units\": [\"eV\",\"ph/s/mr^2/0.1%B.W.\",\"ph/s/mm^2/mr^2/0.1%B.W.\",\"\",\"\",\"\"],\n    \"data\": [\n      [5000,5005,...,49995,50000],\n      [4.02638e+14,3.98914e+14,...,6.66718e+16,6.81642e+16],\n      [3.2776e+16,3.24789e+16,...,6.64598e+18,6.79476e+18],\n      [0.999949,0.999947,...,0.999703,0.999713],\n      [0,0,...,0,0],\n      [-8.67036e-18,-8.97758e-18,...,-1.72714e-17,-1.6893e-17]\n    ]\n  }"),
                            "The data is composed of 1 independent variable (Energy) and 5 items (Flux Density etc.). The 0th array ([5000,...]) corresponds to the photon energy, and the 1st ([4.02638e+14,...]) to the flux density, etc.",
                            "In case the dimension is larger than 1 and thus more than one independent variables exist, the order index j of the item array is given as \\[j=j_0+j_1N_0+j_2N_0N_1+\\cdots,\\] where $j_i$ and $N_i$ refer to the order index and number of data points of the $i$-th variable.",
                            "In some case, 3D data array composed of a number of 2D arrays with the same format as above is stored; each of 2D array is characterized by the \"details\" object. An example is shown below.",
                            GetDirectPara("  \"Output\": {\n    \"dimension\": 1,\n    \"titles\": [\"Harmonic Energy\",\"Peak Energy\",\"K Value\",\"Gap\",\"Flux Density\",...],\n    \"units\": [\"eV\",\"eV\",\"\",\"\",\"ph/s/mr^2/0.1%B.W.\",...],\n    \"details\": [\"Harmonic: 1\",\"Harmonic: 3\",\"Harmonic: 5\"],\n    \"data\": [\n      [\n        [18977.5,18707.1,...,4702.57,4336.24],\n        [18927.2,18657.6,...,4692.37,4326.97],\n        [0.040015,0.174748,...,2.46527,2.6],\n        [50,35.2675,...,8.58047,8.01609],\n        [7.24659e+15,1.3423e+17,...,1.90452e+18,1.82972e+18],\n        [6.91663e+17,1.27995e+19,...,1.5325e+20,1.44896e+20],\n        [0.999995,0.999995,...,0.999998,0.999998],\n        [0,0,...,0,0],\n        [-6.23832e-19,-6.15261e-19,...,-8.10339e-19,-7.90166e-19]\n      ],\n      [\n        [56932.5,56121.2,54374,...,14107.7,13008.7],\n        [47488.9,56019.4,54276.1,...,15312,14087.7,12990.4],\n        [0.040015,0.174748,...,2.46527,2.6],\n        [50,35.2675,...,8.58047,8.01609],\n        [3.235e+10,5.91631e+13,...,1.21888e+18,1.20334e+18],\n        .....\n      ],\n      [\n        [94887.4,93535.3,...,23512.9,21681.2],\n        [85444.8,84227.3,...,23487.4,21658],\n        [0.040015,0.174748,...,2.46527,2.6],\n        [50,35.2675,...,8.58047,8.01609],\n        [7.1207e+11,1.37382e+13,...,7.22944e+19,7.31154e+19],\n        .....\n      ]\n    ]\n  }"),
                            "The \"details\" object in this example specify the harmonic number, i.e., 1st, 3rd and 5th harmonics, and the maximum flux density near the harmonic energy, and other related characteristics are calculated as a function of the K value, for the three different harmonic numbers. The \"data\" object is then composed of three 2D arrays and thus forms a 3D array."
                        ]
                    },
                    {
                        ["Objects Related to CMD"]: [
                            "The results of "+GetLink(MenuLabels.CMD, MenuLabels.CMD, false)+", such as the modal amplitude and profiles, are saved separately from the \"data\" object described above. The details of them are explained below.",
                            {
                                [GetQString(MenuLabels.CMD)+" Object"]: [
                                    "@cmdresult",
                                    {
                                        ["How to retrieve the flux and Wigner function from the modal amplitue?"]: [
                                            "The flux density ($I_n$) and Wigner function ($W_n$) of the $n$-th mode can be retrieved form the complex amplitude $a_n$ determined by the CMD according to the following formulas, using the symbols summarized in the above table.",
                                            "For 1D case (CMD with 2D Wigner function):\\[I_n(x)=|a_n(x)|^2\\frac{F}{2\\sqrt{\\pi}\\sigma}\\times 10^{-3},\\] \\[W_n(x,\\theta_x')=\\frac{W_0}{2\\sqrt{\\pi}\\sigma}\\int a_n\\left(x-\\frac{x'}{2}\\right)a_n^*\\left(x+\\frac{x'}{2}\\right)\\mbox{e}^{ik\\theta_x x'}dx',\\]",
                                            "For 2D case (CMD with 4D Wigner function):\\[I_n(\\boldsymbol{r})=|a_n(\\boldsymbol{r})|^2\\frac{F}{4\\pi\\sigma_x\\sigma_y}\\times 10^{-6},\\] \\[W_n(\\boldsymbol{r},\\boldsymbol{\\theta})=\\frac{W_0}{4\\pi\\sigma_x\\sigma_y}\\int a_n\\left(\\boldsymbol{r}-\\frac{\\boldsymbol{r}'}{2}\\right)a_n^*\\left(\\boldsymbol{r}+\\frac{\\boldsymbol{r}'}{2}\\right)\\mbox{e}^{ik\\boldsymbol{\\theta}\\boldsymbol{r}'}d\\boldsymbol{r}',\\]",
                                            "where $k=2\\pi/\\lambda$ is the wavenumber of radiation." 
                                        ]
                                    }
                                ]
                            },
                            {
                                ["Other Objects"]: [
                                    "A number of data sets evaluated by post-processing the CMD results described above are saved as follows. Note that the format of each object is the same as that of the \"data\" object.",
                                    "@cmdpp"
                                ]
                            }
                        ]
                    },
                    {
                        ["Objects Related to FEL Mode"]: [
                            "When "+GetLink(ConfigPrmsLabel.fel[0], ConfigPrmsLabel.fel[0], false)+" and "+GetLink(ConfigPrmsLabel.exportInt[0], ConfigPrmsLabel.exportInt[0], false)+" options are enabled, numerical data generated while solving the FEL equation, such as variation of the electron beam temporal profile and growth of the FEL radiation pulse, are recorded as summarized below.",
                            "@felvar"
                        ]
                    }
                ]
            }
        ]
    },
    {
        [chapters.standalone]: [
            "Besides the desktop application as described above, the solver of SPECTRA can be run in a standalone mode. Note that in the followings, [spectra_home] refers to the directory where SPECTRA has been installed.",
            "When "+GetMenuCommand([MenuLabels.run, MenuLabels.start])+" command is executed, the SPECTRA GUI creates an input parameter file (\"*.json\") and invokes the solver (\"spectra_solver\" or \"spectra_solver_nompi\" depending on whether the parallel computing option is enabled or not) located in the same directory as the main GUI program, with the input file as an argument. This means that SPECTRA (solver) can be run without the GUI, if the input file is prepared by an alternative method, and a batch process will be possible. To do so, prepare the input file according to the descriptions in "+GetLink(sections.input, sections.input, false)+" and run the solver as follows",
            GetDirectPara("[spectra_home]/spectra_solver_nompi -f [input file]"),
            "without parallel computing, or",
            GetDirectPara("mpiexec -n 4 [spectra_home]/spectra_solver_nompi -f [input file]"),
            "with parallel computing (4 processes in this example).",
            "It should be noted that the names of the parameters and options (\"key\" of the object) should be totally correct, including the units and inserted space characters. In addition, the number of parameters and options actually needed for a specific calculation depend on its condition. To avoid potential errors and complexity in preparing the input file, it is recommended to create a \"master input file\" specific to the desired calculation type, by running "+GetMenuCommand([MenuLabels.run, MenuLabels.ascii])+" command. Then, just modify the values of desired parameters to prepare the input file.",
            "Note that this usage has not been officially supported before ver. 11.0, simply because the input file format was original and difficult to read." 
        ]
    },
    {
        [chapters.python]: [
            "To support the expanding users of python language, SPECTRA has started official support for python, since ver. 12.0. To make use of this function, python version 3.8 or later is needed, and the user is requested to install a python package "+SpectraUILabel+" (SPECTRA User Interface). Refer to <a href=\"https://spectrax.org/spectra/app/"+Version2Digit+"/python/docs/\">the instructions</a> for details of "+SpectraUILabel+"."
        ]
    },
    {
        [chapters.ref]: [
            "@reference"
        ]
    },
    {
        [chapters.ack]: [
            "This software includes the work that is distributed in the Apache License 2.0, and relies on a number of libraries & database as summarized below, which are gratefully appreciated.",
            [
                "ListedItem",
                "Node.js: Javascript runtime environment to run Javascript code without a web browser (https://nodejs.org/en/).",
                "tauri: application toolkit to build software for all major desktop operating systems using web technologies. (https://tauri.app/)",
                "Plotly.js: Javascript graphing library to facilitate data visualization (https://nodejs.org/en/)",
                "Boost C++: Set of libraries for the C++ language (https://www.boost.org/)",
                "EIGEN: C++ template library for linear algebra (https://eigen.tuxfamily.org/index.php?title=Main_Page)",
                "mathjax: Javascript library to display mathematical formulas in HTML documents (https://www.mathjax.org/)",
                "picojson: JSON parser for C++ language (https://github.com/kazuho/picojson)",
                "mucal.c: Source code to calculate the x-ray absorption coefficients (http://www.csrri.iit.edu/mucal.html)",
                "NIST database: Database for the mass energy-absorption coefficients (https://www.nist.gov/pml/x-ray-mass-attenuation-coefficients)",
                "General Purpose FFT Package (https://www.kurims.kyoto-u.ac.jp/~ooura/fft.html)"
            ]
        ]
    }
];

//------ create each component
function GetPreprocDetailTable(rst = false)
{
    let cell, rows = [];
    let table = document.createElement("table");
    let caption = document.createElement("caption");
    caption.innerHTML = "List of items available for visualization";
    table.caption = caption;

    rows.push(table.insertRow(-1)); 
    let titles = ["Name in "+sections.preproc+" Subpanel", "Details", "Availability"];
    for(let j = 0; j < titles.length; j++){
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = titles[j];    
        cell.className = " title";
        if(j == 0){
            cell.setAttribute("colspan", "2");
        }
    }

    let details ={};
    details[AccLabel] = {
        [PPBetaLabel]: "betatron functions within the light source"
    };
    details[SrcLabel] = {
        [PPFDlabel]: "Magnetic field distribution along the longitudinal axis",
        [PP1stIntLabel]: "1st integrals, corresponding to the velocity of an electron",
        [PP2ndIntLabel]: "2nd integrals, corresponding to the electron trajectory",
        [PPPhaseErrLabel]: "Phase error"+(rst?"":(" "+GetLink("refperr", refidx.refperr, false)+" evaluated as a function the magnet pole number. Note that the number of end poles (used for the orbit adjustment and should be eliminated for the phase error evaluation) is automatically determined; to be specific, those with the peak field less than 95% of the average are ignored.")),
        [PPRedFlux]: "Reduction of photon intensity at each harmonic due to magnetic errors evaluated by analytical methods. Refer to "+GetLink(sections.phaseerr, "below", false)+" for details."
    };
    details[PPFilters] = {
        [PPTransLabel]: "Transmission rate of the filter",
        [PPAbsLabel]: "Absorption rate of the absorber"
    };
    let remarks ={};
    remarks[AccLabel] = {
        [PPBetaLabel]: ""
    };
    remarks[SrcLabel] = {
        [PPFDlabel]: "",
        [PP1stIntLabel]: "",
        [PP2ndIntLabel]: "",
        [PPPhaseErrLabel]: ["\""+CUSTOM_Label+"\" sources and/or \""+SrcPrmsLabel.phaseerr[0]+"\" option", "2"]
    };
    remarks[PPFilters] = {
        [PPTransLabel]: "\""+ConfigPrmsLabel.filter[0]+"\" options excluding \""+NoneLabel+"\"",
        [PPAbsLabel]: "\""+MenuLabels.vpdens+"\" calculations"
    };
    
    for(let i = 0; i < PreProcessLabel.length; i++){
        let categ = Object.keys(PreProcessLabel[i])[0];
        let values = Object.values(PreProcessLabel[i])[0];
        for(let j = 0; j < values.length; j++){
            rows.push(table.insertRow(-1));
            if(j == 0){
                cell = rows[rows.length-1].insertCell(-1);
                cell.innerHTML = categ;
                if(values.length > 1){
                    cell.setAttribute("rowspan", values.length.toString());
                }
            }

            cell = rows[rows.length-1].insertCell(-1);
            cell.innerHTML = values[j];
    
            cell = rows[rows.length-1].insertCell(-1);
            cell.innerHTML = details[categ][values[j]];

            if(remarks[categ].hasOwnProperty(values[j])){
                cell = rows[rows.length-1].insertCell(-1);
                if(Array.isArray(remarks[categ][values[j]])){
                    cell.innerHTML = remarks[categ][values[j]][0];
                    cell.setAttribute("rowspan", remarks[categ][values[j]][1]);
                }
                else{
                    cell.innerHTML = remarks[categ][values[j]];    
                }
            }
        }
    }
    let retstr = table.outerHTML;

    return retstr;
}

function GetImportDetailTable()
{
    let cell, rows = [];
    let table = document.createElement("table");
    let caption = document.createElement("caption");
    caption.innerHTML = "Data types that can be imported in the "+sections.preproc+" subpanel";
    table.caption = caption;

    rows.push(table.insertRow(-1)); 
    let titles = ["Name in "+sections.preproc+" Subpanel", "Details", "Dimension", "Independent Variable(s)", "Items"];
    for(let j = 0; j < titles.length; j++){
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = titles[j];    
        cell.className = " title";
    }

    let details = {};
    details[CustomCurrent] = "Current profile of the electron bunch to be used for coherent radiation calculation";
    details[CustomEt] = "Electron density in the (E-t) phase space";
    details[CustomField] = "Magnetic field distribution for "+CUSTOM_Label+" light source";

    details[CustomPeriod] = "Magnetic field distribution within a single period for "+CUSTOM_PERIODIC_Label+" light source";
    details[ImportGapField] = "Relation between the gap and peak field of the ID";

    details[CustomFilter] = "Transmission rate of a filter given as a function of the photon energy";
    details[CustomDepth] = "Depth positions to compute the "+MenuLabels.vpdens;
    details[SeedSpectrum] = "Spectrum of the seed pulse";       
    
    let labels = Object.keys(details);
    for(let i = 0; i < labels.length; i++){
        rows.push(table.insertRow(-1));
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = labels[i];

        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = details[i];

        let dim = AsciiFormats[labels[i]].dim;
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = dim.toString();

        let titles = AsciiFormats[labels[i]].titles;
        let tdef = [];
        for(let j = 0; j < dim; j++){
            let idx = titles[j].indexOf("(");
            if(idx < 0){
                tdef.push(titles[j]);
            }
            else{
                tdef.push(titles[j].substring(0, idx));
            }
        }
        cell = rows[rows.length-1].insertCell(-1);
        if(tdef.length > 0){
            cell.innerHTML = tdef.join(", ");
        }

        tdef = [];
        for(let j = dim; j < titles.length; j++){
            let idx = titles[j].indexOf("(");
            if(idx < 0){
                tdef.push(titles[j]);
            }
            else{
                tdef.push(titles[j].substring(0, idx));
            }
        }
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = tdef.join(", ");
    }
    let retstr = table.outerHTML;
    return retstr;
}

function GetSPECTRAMenuTable(ispython)
{
    let schemes = [
        {far: "Assumes that $|\\boldsymbol{R}|$ is much larger than $|\\boldsymbol{r}|$, where $\\boldsymbol{R}$ and $\\boldsymbol{r}$ represent the vectors directing from the origin to the observer and moving electron, respectively. This implies that the observation angle, i.e., an angle formed by $\\boldsymbol{R}$ and $\\boldsymbol{r}$, is kept constant while the electron passes through the SR source. In addition, the field distribution of the SR source is assumed to be ideal: perfectly periodic in undulators and wigglers, and constant in bending magnets. This significantly simplifies the expressions on SR and thus enables a fast computation. For most applications, such as evaluation of the photon flux passing through a slit and heat load on optical elements, this method is recommended and is in fact reliable enough."},
        {near: "No approximation is made in this method besides an assumption that the electron is relativistic. In other words, the observation angle is a function of the electron position, i.e., it varies while the electron travels along the SR source axis. If the distance between the SR source and observer is shorter and or comparable to the length of the SR source itself, the near-field effect would not be negligible. Especially, the off-axis spectrum will be considerably different from that observed at the point infinitely far from the SR source. In addition, this method should be chosen if the SR source is not ideal. One important case is to compute the characteristics expected in a real device based on a magnetic field distribution actually measured."},
        {cohrad: "Same as \""+MenuLabels.near+"\", except that the radiation is temporally coherent. In other words, radiation emitted by each electron in the electron beam is summed up coherently. This is in contrast to the two methods described above, where radiation is summed up incoherently. The intensity of coherent radiation is significantly enhanced if the bunch length of the electron beam is shorter than the wavelength of radiation, or it has a local density modulation with the typical length shorter than the wavelength."},
        {srcpoint: "Evaluates the photon distribution exactly at the source point, or the center of the SR source. This means that the distance from the source to the observer is zero, i.e., $\\boldsymbol{R}=\\boldsymbol{0}$. Computing the SR properties under such a condition is not possible in a straightforward manner, but requires another numerical operation to propagate the radiation from the observation point back to the source point. SPECTRA is equipped with a number of numerical methods to enable this function."},
        {fixed: "Calculation is performed for a single fixed condition (photon energy, observation point, etc.) and the results are displayed in the GUI."},
        {CMD: "Using the photon distribution at the source point (Wigner functions), partially-coherent radiation can be decomposed into a number of coherent modes, which is useful to describe the propagation of SR in the framework of wave optics."}
    ];
    let methods = [
        {energy: "Target items are calculated as a function of the photon energy."},
        {spatial: "Target items are calculated as a function of the observation point."},
        {Kvalue: "Target items are calculated as a function of the undulator K value (deflection parameter)."},
        {temporal: "Target items are calculated as a function of time."},
        {wigner: "Photon density in the 2D/4D phase space is evaluated by means of the Wigner function method."}
    ];
    let targets = [
        {fdensa: "Photon flux per unit solid angle."},
        {fdenss: "Photon flux per unit area."}, 
        {pflux: "Photon flux of radiation passing through a finite aperture."}, 
        {tflux: "Photon flux of radiation integrated over the whole solid angle."}, 
        SimpleLabel,
        {pdensa: "Radiation power per unit solid angle."}, 
        {pdenss: "Radiation power per unit area."}, 
        {ppower: "Radiation Power passing through a finite aperture"},
        {pdensr: "Radiation power decomposed into polarization and harmonic components"}, 
        {spdens: "Radiation power density under a glancing-incidence condition"}, 
        {vpdens: "Radiation power per unit volume absorbed by a target object (absorber)"}, 
        SimpleLabel,
        {efield: "Temporal profile of electric field of radiation."}, 
        {camp: "Spatial profile of complex amplitude of radiation."}, 
        SimpleLabel,
        {sprof: "Transverse profile of the spatial flux density calculated at the source point."}, 
        {phasespace: "Distribution of the photon density in the in the 2D/4D phase space."}, 
        SimpleLabel,
        {CMD2d: "Perform CMD using the existing Wigner function data"}, 
        {CMDPP: "Perform post-processing using the CMD results"}
    ];
    let conds = [
        {slitrect: "Radiation passes through a rectangular aperture."},
        {slitcirc: "Radiation passes through a circular aperture."},
        SimpleLabel,
        {along: "Moves the observation point along the x- and y-axes."},
        {meshxy: "Moves the observation point over the rectangular grid."},
        {meshrphi: "Moves the observation point over the grid in the 2D polar coordinate."},
        {simpcalc: "Assumes that the radiation is a Gaussian beam, and roughly estimates its characteristics, such as the brilliance, on-axis flux density, source size and angular divergence without actually doing the convolution."},
        SimpleLabel,
        {fluxfix: "Calculates the characteristics of UR at a fixed photon energy. To be specific, the monochromator is unchanged, while the K value is tuned."},
        {fluxpeak: "Calculates the characteristics of UR at peak harmonic energies. To be specific, the monochromator is scanned synchronously with the K value."},
        {powercv: "Calculate the radiation power as a function of the K value."}, 
        SimpleLabel,
        {xzplane: "Calculation is done on the x-z surface located vertically off the beam axis."},
        {yzplane: "Calculation is done on the y-z surface located horizontally off the beam axis."},
        {pipe: "Calculation is done on the inner surface of a pipe coaxially located with the beam axis."},
        SimpleLabel,
        {XXpslice: "4D Wigner function calculated on (X,X') phase space at given (Y,Y')."},
        {XXpprj: "2D (projected) Wigner function calculated on (X,X') phase space."},
        {YYpslice: "4D Wigner function calculated on (Y,Y') phase space at given (X,X')."},
        {YYpprj: "2D (projected) Wigner function calculated on (Y,Y') phase space."},
        {XXpYYp: "4D Wigner function calculated on (X,X',Y,Y')."}
    ];
    let subconds = [
        {tgtharm: "Calculation is performed for individual harmonics."},
        {allharm: "Optimizes the harmonic number to maximize the target item (brilliance or flux)."},
        {Wslice: "4D (X,X',Y,Y') Wigner function at a single point."},
        {WprjX: "2D Wigner function projected on (X,X')."},
        {WprjY: "2D Wigner function projected on (Y,Y')."},
        {Wrel: "Degree of Coherence and X-Y Separability evaluated from Wigner function."}
    ];

    let categories = [
        [CalcIDSCheme, schemes],
        [CalcIDMethod, methods],
        [CalcIDMainTarget, targets],
        [CalcIDCondition, conds],
        [CalcIDSubCondition, subconds],
    ];
    let calclabels = [];
    for(let i = 0; i < categories.length; i++){
        let category = categories[i];
        let valids = category[1].filter(item => item != SimpleLabel);
        for(let j = 0; j < category[1].length; j++){
            let label = category[1][j];
            if(label == SimpleLabel){
                continue;
            }
            let key = Object.keys(label)[0];
            let lists = [
                j == 0 ? [category[0], valids.length] : null,
                CalcLabels[category[0]][key]
            ];
            if(ispython){
                lists.push(key)
            }
            else{
                lists.push(label[key])
            }
            calclabels.push(lists);
        }
    }

    let cell, rows = [];
    let table = document.createElement("table");
    let caption = document.createElement("caption");
    caption.innerHTML = "Classification and Description of Menu Items";
    table.caption = caption;

    rows.push(table.insertRow(-1)); 
    let titles = ["Category", "GUI Menu Items"];
    let widths = ["150px", "150px", ""];
    if(ispython){
        titles.push("Simplified");
        widths = ["", "", ""];
    }
    else{
        titles.push("Details");
    }
    for(let j = 0; j < titles.length; j++){
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = titles[j];    
        cell.className = " title";
        if(widths[j] != ""){
            cell.setAttribute("width", widths[j]);
        }
    }

    let links = {
        [MenuLabels.spdens]: "surfacepd.png",
        [MenuLabels.ppower]: "slittype.png",
        [MenuLabels.pflux]: "slittype.png",
        [MenuLabels.spatial]: "spatialgrid.png",
    }
    let likids = Object.keys(links);

    for(let i = 0; i < calclabels.length; i++){
        let menu = calclabels[i];
        rows.push(table.insertRow(-1));
        for(let j = 0; j < menu.length; j++){
            if(menu[j] == null){
                continue;
            }
            cell = rows[rows.length-1].insertCell(-1);
            if(Array.isArray(menu[j])){
                cell.setAttribute("rowspan", menu[j][1]);
                cell.innerHTML = menu[j][0];
            }
            else{
                if(ispython && j == 2){
                    cell.classList.add("prm");
                }
                cell.innerHTML = menu[j];
            }
        }
    }

    let retstr = table.outerHTML;
    return retstr;
}

function GetPrmListTable(labels, conts, subtitles)
{
    let table = document.createElement("table");
    let rows = [], cell;
    let titles = ["Parameter/Option", "Detail"];

    rows.push(table.insertRow(-1));
    for(let j = 0; j < titles.length; j++){
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = titles[j];
        cell.className += " title";
    }

    for(let j = 0; j < conts.length; j++){
        let cont = conts[j];
        let label = labels[j];

        if(subtitles[j] != ""){
            rows.push(table.insertRow(-1));
            cell = rows[rows.length-1].insertCell(-1);
            cell.setAttribute("colspan", "2");
            if(Array.isArray(subtitles[j])){
                cell.innerHTML = subtitles[j][0];
                cell.id = subtitles[j][1];
            }
            else{
                cell.innerHTML = subtitles[j];
            }
            cell.className += " subtitle";    
        }

        for(let i = 0; i < cont.length; i++){
            for(let k = 0; k < cont[i][0].length; k++){
                rows.push(table.insertRow(-1));
                cell = rows[rows.length-1].insertCell(-1);
                let labelr = label == null ? cont[i][0][k] : label[cont[i][0][k]];
                let id;
                if(Array.isArray(labelr)){
                    cell.innerHTML = labelr[0];
                    id = labelr[0];
                }
                else{
                    cell.innerHTML = labelr;
                    id = labelr;
                }
                if(cont[i].length > 2){
                    cell.id = id;
                }
                if(k == 0){
                    cell = rows[rows.length-1].insertCell(-1);
                    if(Array.isArray(cont[i][1])){
                        cell.className += " cont";
                        let p = document.createElement("p")
                        p.innerHTML = cont[i][1][0];
                        let ul = document.createElement("ul");
                        for(let l = 1; l < cont[i][1].length; l++){
                            let li = document.createElement("li");
                            li.innerHTML = cont[i][1][l];
                            ul.appendChild(li);
                        }
                        cell.appendChild(p);
                        cell.appendChild(ul);
                    }
                    else{
                        cell.innerHTML = cont[i][1];
                    }
                    if(cont[i][0].length > 1){
                        cell.setAttribute("rowspan", cont[i][0].length.toString());
                    }
                }
            }
        }
    }
    return table.outerHTML;
}

function GetSrcTypesTable()
{
    let cell, rows = [];
    let table = document.createElement("table");
    let caption = document.createElement("caption");
    caption.innerHTML = "List of light sources available in SPECTRA";
    table.caption = caption;

    rows.push(table.insertRow(-1)); 
    let titles = ["Name", "Details", "Field Profile"];
    for(let j = 0; j < titles.length; j++){
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = titles[j];    
        cell.className = " title";
    }

    let sinfu = [
        LIN_UND_Label,
        VERTICAL_UND_Label,
        HELICAL_UND_Label,
        ELLIPTIC_UND_Label,
        FIGURE8_UND_Label,
        VFIGURE8_UND_Label
    ];
    let sinfw = [
        WIGGLER_Label,
        EMPW_Label
    ];
    let customsrc = [
        FIELDMAP3D_Label,
        CUSTOM_PERIODIC_Label,
        CUSTOM_Label
    ];

    let details = {};
    details[LIN_UND_Label] = "Conventional linear undulator for horizontal polarization";
    details[VERTICAL_UND_Label] = "Undulator for vertical polarization to generate a horizontal field";
    details[HELICAL_UND_Label] = "Undulator for circular polarization to generate a (completely) helical field";
    details[ELLIPTIC_UND_Label] = "General form of an undulator to generate a helical-like field (horizontal and vertical field amplitudes may be different)";
    details[FIGURE8_UND_Label] = "Undulator having figure-8 shaped electron orbit, for horizontal polarization and low on-axis heat load";
    details[VFIGURE8_UND_Label] = "Same as the figure-8 undulator, but for vertical polarization";
    details[MULTI_HARM_UND_Label] = "\"Semi-Customized\" undulator, in which the magnetic field distribution is composed of a number of harmonic components. The strength and phase of each harmonic should be defined by the user.";
    details[WIGGLER_Label] = "Conventional multi-pole wiggler";
    details[EMPW_Label] = "Elliptic multi-pole wiggler for elliptic polarization in the high energy region";
    details[WLEN_SHIFTER_Label] = "Wavelength shifter composed of 3 magnet poles; the main (central) pole has the strongest field, while the other two have lower fields so that the field integrals are zero. Note that the magnetic field is not uniform along the longitudinal (z) axis but changes in a sinusoidal manner";
    details[BM_Label] = "Conventional bending magnet";
    details[FIELDMAP3D_Label] = "Specify the 3-D magnetic vector in the (x,y,z) space to calculate the electron orbit. Refer to "+GetLink(sections.flddata, sections.flddata, false)+" for details.";
    details[CUSTOM_PERIODIC_Label] = "Similar to \""+FIELDMAP3D_Label+"\", but specify the 2D magnetic vector along z. Refer to "+GetLink(sections.flddata, sections.flddata, false)+" for details.";
    details[CUSTOM_Label] = "";

    for(const src of SrcTypels){
        rows.push(table.insertRow(-1)); 
        
        cell = rows[rows.length-1].insertCell(-1);
        cell.innerHTML = src;

        if(src != CUSTOM_Label){
            cell = rows[rows.length-1].insertCell(-1);
            if(Array.isArray(details[src])){
                cell.innerHTML = WriteObject(0, details[src]);
            }
            else{
                cell.innerHTML = details[src];
            }
            if(src == CUSTOM_PERIODIC_Label){
                cell.setAttribute("rowspan", "2");
            }
        }

        if(sinfu.indexOf(src) > 0 || sinfw.indexOf(src) > 0 || customsrc.indexOf(src) > 0)
        {
            continue;
        }
        cell = rows[rows.length-1].insertCell(-1);
        if(src == sinfu[0] || src == sinfw[0]){
            cell.innerHTML = "Sinusoidal";
            if(src == sinfu[0]){
                cell.setAttribute("rowspan", sinfu.length.toString());
            }
            else{
                cell.setAttribute("rowspan", sinfw.length.toString());
            }
        }
        else if(src == customsrc[0]){
            cell.innerHTML = "Custom";
            cell.setAttribute("rowspan", customsrc.length.toString());
        }
        else if(src == BM_Label){
            cell.innerHTML = "Uniform";
        }
        else if(src == WLEN_SHIFTER_Label){
            cell.innerHTML = "Semi Sinusoidal";
        }
        else{
            cell.innerHTML = "Custom";
        }
    }
    return table.outerHTML;
}

function GetFldDataFormatTable()
{
    let caption = "Format of a data file to import the magnetic field distribution.";
    let titles = ["Source Type", "Format"];
    let fmt = GetDirectPara("z\tBx\tBy\n-8.959978e-01\t5.174e-05\t7.035e-06\n-8.949972e-01\t5.423e-05\t7.062e-06\n-8.939967e-01\t5.646e-05\t7.244e-06\n\t\t(omitted)\n 8.979989e-01\t4.801e-05\t6.639e-06\n 8.989994e-01\t4.582e-05\t6.327e-06\n 9.000000e-01\t4.409e-05\t6.456e-06\n")+" The 1st line (title) is optional and the interval of the z coordinate does not have to be constant. For "+GetQString(CUSTOM_PERIODIC_Label)+" sources, the magnetic field is defined as a periodic function with the periodicity defined by the imported data. Note that the data should be imported and embedded in the parameter file. Refer to "+GetLink(sections.preproc, sections.preproc, false)+" for details.";
    let flddata = [
        [CUSTOM_Label, {rows:2, label:fmt}],
        [CUSTOM_PERIODIC_Label, null],
        [FIELDMAP3D_Label, GetDirectPara("0.2	0.3	0.5	11	13	421\n1.23456e-1	2.3456e-1	3.4557e-1\n2.23456e-1	3.3456e-1	6.4557e-1\n	...\n4.23456e-1	5.3456e-1	8.4557e-1\n2.23456e-1	3.3456e-1	6.4557e-1")+"The 6 numbers in the first line indicate the grid interval in mm and number of grid points along the x, y, and z axes. In the above case, the magnetic field components are given at 11x13x421 grid points with the x, y, and z intervals of 0.2 mm, 0.3 mm, and 0.5 mm, respectively. From the 2nd line, the magnetic field components ($B_x$, $B_y$, $B_z$) at each grid point are given. The grid point should be moved first along the z direction, next y direction, and finally x direction. Note that the user should specify the file name instead of directly importing the data, unlike other two sources of "+GetQString(CUSTOM_Label)+" and "+GetQString(CUSTOM_PERIODIC_Label)+"."]
    ];
    return GetTable(caption, titles, flddata);
}

//----- python -----
function GetAccPrmList(rst = false)
{
    let prmconts = [
        [["type"], "Type of the accelerator. In SPECTRA, the accelerators are categorized into two types: "+GetQString("Storage Ring")+" and "+GetQString("Linear Accelerator")+(rst?".":". The difference between them is how to specify the average beam current. In the former, it is directly specified by the user. In the latter, the pulse repetition rate and bunch charge should be given to evaluate the average current.")],
        [["eGeV"], "Total energy of the electron beam."],
        [["imA", "aimA"], "Average beam current of the accelerator. The former is determined by the user, while the latter is evaluated from \"Pulses/sec\" and \"Bunch Charge\"."],
        [["cirm"], "Circumference of the storage ring."],
        [["bunches"], "Number of electron bunches stored in the storage ring."],
        [["pulsepps"], "Number of electron bunches/second in the linear accelerator."],
        [["bunchlength", "bunchcharge"], "Bunch length and charge of the electron beam."],
        [["emitt"], "Natural emittance of the electron beam."],
        [["coupl", "espread"], "Coupling constant and energy spread of the electron beam."],
        [["beta", "alpha"], "Twiss parameters at the center of the light source"],
        [["eta", "etap"], "Dispersion functions and their derivatives."],
        [["peakcurr"], "Peak current of the electron beam evaluated from relevant parameters."],
        [["epsilon"], "Horizontal and vertical emittances evaluated from &epsilon; and Coupling Constant."],
        [["sigma", "sigmap"], "Beam size and angular divergence at at the center of the light source."],
        [["gaminv"], "Inverse of the Lorentz factor."]
    ];
    let injconts = [
        [["injectionebm"], 
            ["Specify the injection condition, or the position and angle of the electron beam at the entrance of the light source.",
            GetQString(AutomaticLabel)+": an appropriate condition for the current light source is selected. This is usually recommended in most cases.",
            GetQString(EntranceLabel)+", "+GetQString(CenterLabel)+", "+GetQString(ExitLabel)+": the electron beam axis is adjusted to coincide with that of the light source. The longitudinal position for adjustment can be selected from the entrance, center, and exit of the light source.",
            GetQString(CustomLabel)+": directly input the injection condition."]
        ],
        [["xy", "xyp"], "Horizontal/vertical positions/angles at the entrance. Available when "+GetQString(AccPrmsLabel.injectionebm[0])+" is "+CustomLabel]
    ];
    let othterconts = [
        [["bunchtype"], 
            ["Specify the distribution functions of the electron beam in the spatial and temporal domains.",
            GetQString(GaussianLabel)+": Gaussian functions in the both domains.",
            GetQString(CustomCurrent)+": import the current profile.",
            GetQString(CustomEt)+": import the electron density in the (E-t) phase space.",
            GetQString(CustomParticle)+": load the particle coordinates in the 6D phase space."]
        ],
        [["currdata"], "Dictionary data to represent the current profile of the electron bunch."],
        [["Etdata"], "Dictionary data to represent the electron distribution in the E-t phase space."],
        [["bunchdata"], "File name to specify the particle coordinates in the 6D phase space (x,x',y,y',t,DE/E) used for "+GetQString(CustomParticle)+" option. An example of the data format is shown below."+GetDirectPara("       x        x'      y        y'        t     DE/E\n 6.20E-4 -6.08E-5 4.83E-4 -7.72E-5 -7.68E-15 -0.00133\n-2.88E-4 -1.83E-5 7.21E-4 -4.09E-5 -5.49E-15 -9.08E-4\n                ...\n 9.22E-4 -1.09E-5 0.00160 -1.47E-4  5.33E-16  3.48E-4")+"In this example, the 1st column defines the horizontal position (x) of the particle, and so on. The column index and unit of each coordinate should be specified by the user."+(rst?"":(" For details, refer to "+GetLink(sections.pdata, sections.pdata, false)+"."))],
        [["zeroemitt", "zerosprd"], "Calculation is done without the effects due to the finite emittance and/or energy spread of the electron beam."],
        [["singlee"], "SR emitted by a single electron is supposed."],
        [["R56add"], "Strength of the virtual dispersive section located in front of the light source. Effective for computation of coherent radiation, if "+GetQString(CustomEt)+" is chosen for the electron bunch profile."]
    ];

    if(rst){
        return [...prmconts, ...injconts, ...othterconts];
    }
    return GetPrmListTable( 
        [AccPrmsLabel, AccPrmsLabel, AccPrmsLabel], 
        [prmconts, injconts, othterconts], 
        ["Main Parameters and Conditions", "Injection Condition", "Others"]);
}

function GetSrcPrmList(rst = false)
{
    let bmsche = WriteFigure("BMsetup.png", "Schematic drawing of the bending magnet configuration.");
    let prmconts = [
        [["gap"], "Gap of the ID."],
        [["bxy", "b"], "Field amplitude (IDs) or uniform field (BMs)."],
        [["bmain", "subpoleb"], "Peak fields of the main and sub poles of Wavelength Shifters."],
        [["lu"], "Magnetic Period Length of the ID"],
        [["devlength"], "Total length of the ID"],
        [["reglength"], "Length of the ID for the regular period."],
        [["periods"], "Number of regular periods."],
        [["Kxy0"], "Available for APPLE undulators. Maximum K values (deflection parameters) when the phase is adjusted to generate horizontal and vertical polarizations."],
        [["phase"], "Longitudinal shift of each magnetic array for the APPLE undulators, defined as the displacement from the position for the horizontally-polarized mode. To be specific, K values are given as $K_x=K_{x0}\\sin(2\\pi\\Delta z/\\lambda_u)$ and $K_y=K_{y0}\\cos(2\\pi\\Delta z/\\lambda_u)$, where $\\Delta z$ is the phase shift. In other words, it is defined as half the relative distance between two diagonal pairs of magnetic arrays."],
        [["Kxy", "K"], "K values of the ID."],
        [["Kperp"], "Composite K value defined as $\\sqrt{K_x^2+K_y^2}$."],
        [["e1st","lambda1"], "Fundamental photon energy and wavelength of undulator radiation."],
        [["multiharm"], [
                "Arrange the harmonic components for "+MULTI_HARM_UND_Label+"s.",
                "K<sub>x</sub> Ratio ($=R_n$) and Phase ($=P_n$, in degrees) refer to the fraction and phase of the horizontal field of the n-th harmonic component, where n is the number indicated in the 1st row.",
                "The K value corresponding to the n-th harmonic is defined as \\[K_{xn}=K_x\\frac{R_n}{\\sqrt{R_1^2+R_2^2+\\cdots+R_N^2}},\\] where $K_x$ is the (total) K value and $N$ is the maximum harmonic number.",
                "The field distribution is defined as \\[B_{x}(z)=\\sum_{n=1}^{N}B_{xn}\\sin\\left[2\\pi\\left(\\frac{nz}{\\lambda_u}+\\frac{P_n}{360}\\right)\\right],\\] where $B_{xn}$ is the peak field corresponding to the K value of the n-th harmonic.",
                "Similar definitions of $K_{yn}$ and $B_{y}(z)$."
            ]
        ],
        [["radius"], "Radius of the BM."],
        [["bendlength", "fringelen", "csrorg"], "Specify the geometric configuration of BMs. \"Origin for CSR\" defines the longitudinal coordinate where the electron bunch length or the temporal profile is defined to calculate coherent radiation."+bmsche],
        [["mplength", "subpolel"], "Lengths of the main and sub poles of the Wavelength Shifter."],
        [["bminterv"], "Distance between two BMs."],
        [["fmap"], "File name containing the 3D magnetic field data."+(rst?"":(" Refer to "+GetLink(sections.flddata, sections.flddata, false)+" for details."))],
        [["sigmar", "sigmarx", "sigmary"], "Natural source size and angular divergence of radiation."],
        [["Sigmax", "Sigmay"], "Effective source size and angular divergence of the photon beam, convoluted with those of the electron beam."],
        [["fd", "flux", "brill"], "Approximate values of the on-axis flux density, available flux, and brilliance at &epsilon;<sub>1st</sub>."],
        [["pkbrill"], "Peak brilliance at &epsilon;<sub>1st</sub> evaluated with the peak current of the electron beam."],
        [["degener"], "Bose degeneracy evaluated for the Peak Brilliance."],
        [["ec", "lc"], "Critical photon energy and wavelength."],
        [["tpower"], "Total radiation power."],
        [["tpowerrev", "linpower"], "Total power/revolution and linear power density of the BM."]
    ];
    if(rst){
        prmconts.push([["type"], "Type of the light source"]);
        prmconts.push([["fvsz"], "Dictionary data to represent the whole magnetic field distribution of the light source."]);
        prmconts.push([["fvsz1per"], "Dictionary data to represent the magnetic field distribution of the light source over a single period."]);
    }

    let slitsche = WriteFigure("segscheme.png", "Schematic drawing of the segmented undulator configurations: (a) all segments are identical, and (b) even-number segments are of different type.");
    let optconnts = [
        [["gaplink"], 
            ["Specify the relation between the gap and peak field of the ID.",
            GetQString(NoneLabel)+": no relation is given. The Gap parameter is not available.",
            GetQString(AutomaticLabel)+": evaluate according to an analytical formula of Halbach array defined as \\[B(g)=1.8G B_r\\mbox{exp}(-\\pi g/\\lambda_u),\\] where $B_r$ is the remanent field of the magnet and $G$ is a geometrical (reduction) factor coming from the physical boundary conditions such as the finite dimension of magnet blocks.",
            GetQString(ImpGapTableLabel)+": evaluate by interpolating the imported data."],
            true // <- enable id
        ],
        [["apple"], "Enable/disable the APPLE configuration for "+ELLIPTIC_UND_Label+"s."],
        [["field_str"], 
            ["Specify the field-distribution symmetry of the ID. ",
            GetQString(AntiSymmLabel)+": anti-symmetric with respect to the center (sine-like).",
            GetQString(SymmLabel)+": symmetric with respect to the center (cosine-like)."]
        ],
        [["br"], "Remanent field of the permanent magnet."],
        [["geofactor"], "Geometrical factor to reduce the peak magnetic field (x,y)."],
        [["endmag"], "Put additional magnets at the both ends, for orbit compensation."],
        [["natfocus"], 
            ["Apply the natural focusing of IDs.",
            GetQString(NoneLabel)+": no focusing considered.",
            GetQString(BxOnlyLabel)+": horizontal field (and focusing).",
            GetQString(ByOnlyLabel)+": vertical field (and focusing).",
            GetQString(BothLabel)+": focus in the both directions.",
            ]
        ],
        [["bmtandem"], "Calculate radiation from two BMs located at the both ends of the straight section."]
    ];

    let ferrprms = [
        [["fielderr"], "Specify if the magnetic field contains an error component."],
        [["boffset"], "Magnetic field offset, such as that coming from the ambient field."],
        [["ltaper", "qtaper"], "Linear (a<sub>1</sub>) and quadratic (a<sub>2</sub>) taper coefficients. The magnetic field amplitude is given as \\[B(z)=B_0(1+a_1z+a_2z^2),\\] where $B_0$ is the field amplitude corresponding to the K value."]
    ];

    let perrprms = [
        [["phaseerr"], "If ticked, the RMS phase error and relevant parameters can be specified."],
        [["seed"], "Seed for the random number generator to model the field error."],
        [["fsigma"], "RMS of the peak field variation."],
        [["psigma"], "RMS of the phase error"+(rst?".":(" "+GetLink("refperr", refidx.refperr, false)+"."))],
        [["xysigma"], "RMS of the trajectory error."]
    ];

    let segprms = [
        [["segment_type"], 
            ["Arrange the segmented undulator configuration."+(rst?"":(" For details of how these segmentation schemes work to improve the characteristics of radiation, refer to "+GetLink("refsegment", refidx.refsegment, false)+" and "+GetLink("refsegx", refidx.refsegx, false)+"."+slitsche+
            "To adjust the optical phase ($\\Delta\\phi$) in each drift section, SPECTRA assumes that a phase shifter, or a 1.5-period undulator with the same periodic length, is installed at the center of the drift section, whose amplitude is tuned to generate the specified phase. Five options are available as explained below.")),
            GetQString(NoneLabel)+": no segmentation.",
            GetQString(IdenticalLabel)+": all segments have the same specification (a).",
            GetQString(SwapBxyLabel)+": horizontal and vertical fields are swapped in even segments (b).",
            GetQString(FlipBxLabel)+": polarity of the horizontal field is swapped in even segments (b).",
            GetQString(FlipByLabel)+": polarity of the vertical field is swapped in even segments (b).",
            ],
            true // <- enable id
        ],
        [["segments", "hsegments"], "Number of undulator segments (M) if "
            +GetQString(IdenticalLabel)+" is selected for "+GetQString(SrcPrmsLabel.segment_type[0])
            +", or number of segment pair (M') for other options."],
        [["interval"], "Distance between the center positions of adjacent undulator segments."],
        [["pslip"], "Slippage in the drift section given in the unit of &lambda;<sub>1st</sub>."],
        [["phi0"], "Additional phase in the unit of &pi;."],
        [["phi12"], "Additional phase in the unit of &pi;: subscripts 1 and 2 refer to the odd and even drift sections"],
        [["mdist"], "Distance between virtual focusing magnets in the matching section to arrange the periodic lattice function."],
        [["perlattice"], "The betatron function is periodic with the period of segment interval."]
    ];

    if(rst){
        return [...prmconts, ...optconnts, ...ferrprms, ...perrprms, ...segprms];
    }
    return GetPrmListTable( 
        [SrcPrmsLabel, SrcPrmsLabel, SrcPrmsLabel, SrcPrmsLabel, SrcPrmsLabel], 
        [prmconts, optconnts, ferrprms, perrprms, segprms], 
        ["Main Parameters", "Options", 
            "Parameters for the Field-Error Condition",
            "Parameters to Specify the Phase Error",
            "Parameters for the Segmented Undulator Option"
        ]);
}

function GetConfigPrmList(rst = false)
{
    let slitsche = WriteFigure("slittype.png", "Schematic drawing of the slit conditions.");
    let spdmesh = WriteFigure("spatialgrid.png", "Meanings of the observation position for "+GetQString(MenuLabels.spatial)+": (a) [Planar Surface: x-z/y-z] and (b) [Cylindrical Surface].");
    let spdgrid = WriteFigure("surfacepd.png", "Observation conditions of the surface power density.");
    let spdpoint = WriteFigure("surfacepd_point.png", "Observation conditions of the surface power density available in "+FixedPointLabel+" calculation.");
    let fpsche = WriteFigure("fourieplane.png", "Virtual observation in the Fourier plane.");
    let vpdsche = WriteFigure("volpdens.png", "Definitions of parameters to define the condition of the target object and coordinate to define the calculation positions in "+MenuLabels.vpdens+" calculations");
    let felsche = WriteFigure("felsteps.png", "Definitions of parameters to define the longitudinal steps to solve the FEL equation.");
    let prmconts = [
        [[
            "xyfix",
            "qxyfix"       
        ], "Transverse position/angle at the observation point."],
        [[
            "erange",
            "de"        
        ], "Energy range and pitch for "+MenuLabels.energy+" calculations."],
        [["epitch"], "Energy pitch for integration in "+MenuLabels.vpdens+" calculations. Needs to be defined by the user for "+CUSTOM_Label+" light sources."],
        [["emesh"], "Number of energy points for "+MenuLabels.energy+" calculations."],
        [["detune"], "Photon energy defined as a detuned value, i.e., $\\varepsilon/(n\\varepsilon_1)-1$, where $n$ is the target harmonic number."],
        [["efix"], "Photon energy to be fixed."],
        [["nefix"], "Same as the above, but normalized by &epsilon;<sub>1st</sub>."],
        [["autoe"], "Enable automatic configuration to define the energy range and pitch."],
        [["autot"], "Enable automatic configuration to define the spatial/angular range and grid intervals."],
        [[
            "xrange",
            "qxrange", 
            "yrange",
            "qyrange",
            "rrange",
            "qrange",
            "phirange"
        ], "Range of the Observation positions/angles for \"Spatial Dependence\" calculations: (a) [Along Axis] and [Mesh: x-y] and (b) [Mesh: r-&phi;]."+spdmesh],
        [[
            "xmesh", 
            "ymesh",
            "rphimesh",
            "qphimesh",
            "phimesh"
        ], "Number of observation point in the relevant range."],
        [["slit_dist"], "Distance from the center of the light source to the observation point."],
        [[
            "slitpos",
            "qslitpos",
            "nslitapt",
            "slitapt",
            "slitr",
            "slitq"
        ], "Specify the configuration of the slit positions and aperture."+slitsche],
        [[
            "drange",
            "dmesh"        
        ], "Depth range and number of points for "+MenuLabels.vpdens+" calculations."],
        [[
            "qslitapt",
            "illumarea"    ,
            "Qgl",
            "Phiinc"    
        ], "Angular acceptance to confine the photon beam and resultant illuminated area of the object, and angles to define the condition of glancing incidence for "+MenuLabels.vpdens+" calculations."+vpdsche+"Azimuth of Incidence define the direction along which the object is inclined: if it is vertically tilted as in the case of a crystal monochromator, this parameter should be 90 degree, as shown in the above figure."],
        [[
            "xrange",
            "yrange",
            "zrange",
            "spdxfix",
            "spdyfix",
            "spdrfix"
        ], "Position of the object and range of observation for "+MenuLabels.pdenss+" calculations."+(rst?"":" Note that SPECTRA distinguishes the inner and outer sides of the surface. To be specific, the above figure shows the case when the inner size indicated by a red line is facing the beam axis, and thus receives the radiation power. If, in contrast, the object with the same normal vector is located at a negative position of x, the inner surface is facing outsize and it does not receive any radiation"+spdgrid)],
        [[
            "xmesh", 
            "ymesh",
            "zmesh",
        ], "Number of observation points in the relevant range"],
        [[
            "Qnorm",
            "Phinorm"    
        ], "Normal vectors to specify the inner surface of the object irradiated by SR."+(rst?"":(" In "+GetQString(FixedPointLabel)+" calculations, the normal vector to the object surface is specified more flexibly by two angles as schematically illustrated below. For example, &Theta; = &Phi; = 0 means that the surface of the object is parallel to the y-z plane, with its inner side facing the beam axis. Angles of the normal vector to define the inner surface illuminated by radiation for "+MenuLabels.pdenss+" calculations."+spdpoint))],
        [[
            "fsize",
            "fdiv"        
        ], "Photon beam size and divergence at the observation position, defined at &epsilon;<sub>1st</sub>."+(rst?"":" Note this is a rough estimation and does not take into account the energy spread of the electron beam.")],
        [[
            "psize",
            "pdiv"        
        ], "Spatial spread and divergence of the radiation power at the observation position"],
        [[
            "krange",
            "ckrange",
            "kmesh"    
        ], "Range of the K values and number of points."],
        [["e1strange"], "Range of the fundamental energy determined by the above K-value range."],
        [["pplimit"], "Upper limit of the partial power to define the width and height of the rectangular slit for "+MenuLabels.Kvalue+" calculations."],
        [[
            "hrange",
            "hfix"
        ], "Harmonic range or target harmonic number for K-value dependence calculations."],
        [[
            "trange",
            "tmesh"        
        ], "Temporal range and number of points for "+MenuLabels.temporal+" calculations."],
        [["hmax"], "Maximum harmonic number to be considered."],
        [[
            "Xfix",
            "Yfix",
            "Xpfix",
            "Ypfix"        
        ], "Transverse positions and angles at the source point where the Wigner function is calculated."+(rst?"":" These parameters should be distinguished from those indicated by lower letters, which mean the transverse positions at a certain longitudinal position downstream of the light source.")],
        [[
            "Xrange",
            "Xmesh",
            "Xprange",
            "Xpmesh",
            "Yrange",
            "Ymesh",
            "Yprange",
            "Ypmesh"
        ], "Calculation range/number of points of the transverse positions/angles at the source point."+(rst?"":" Should be distinguished from those indicated by lower letters (see above).")],
        [[
            "gtacc",
            "horizacc"        
        ], "Angular acceptance normalized by &gamma;<sup>-1</sup> to calculate the Wigner function."],
        [["optics"], "Optical element to be inserted."],
        [["optpos"], "Position of the optical element."],
        [["aptx", "apty"], "Aperture size of the slit."],
        [["aptdistx", "aptdisty"], "Distance of the double slit."],
        [["softedge"], "Length of the soft-edge region."],
        [["diflim"], "Target tolerance to define the threashold of the angular range when a slit is inserted."],
        [["anglelevel"], "An integer to define the angular range to evaluate the CSD."],
        [["anglelevel"], "An integer to define the angular range to evaluate the CSD."],
        [["anglelevel"], "An integer to define the angular range to evaluate the CSD."],
        [["foclenx", "focleny"], "Focal length of the thin lens."],
        [["aprofile"], "Export the angular profile"],
        [["wigner"], "Export the Wigner function after the optical element."],
        [["csd"], "Export the CSD."],
        [["degcoh"], "Export the spatial degree of coherence."],
    ];

    if(rst){
        prmconts.push([["fmateri"], "Dictionaly data to represent the filter materials."]);
        prmconts.push([["fcustom"], "Dictionaly data to represent the filter transmission rate."]);
        prmconts.push([["depthdata"], "Dictionaly data to represent the depth positions."]);
    }

    let optconnts = [
        [["filter"], 
            ["Specify the type of filtering.",
            GetQString(NoneLabel)+": no filter is assumed.",
            GetQString(GenFilterLabel)+": slab or layer that attenuates the photon beam, made of any material.",
            GetQString(BPFGaussianLabel)+": Gaussian bandpath filter.",
            GetQString(BPFBoxCarLabel)+": boxcar-type bandpath filter.",
            GetQString(CustomLabel)+": evaluate the transmission rate by interpolating the imported data.",
            ]
        ],
        [["estep", "dstep"],
            ["Specify how to change the energy/depth position in the calculation range.",
                GetQString(LinearLabel)+": linear variation (constant interval).",
                GetQString(LogLabel)+": logarithmic variation (constant ratio)."
            ]
        ],
        [["aperture"],
            ["Specify how to represent the width and height of the rectangular slit.",
                GetQString(FixedSlitLabel)+": fixed aperture",
                GetQString(NormSlitLabel)+": normalized by "+ConfigPrmsLabel.fsize+" and is varied for "+MenuLabels.Kvalue+" calculations"
            ]
        ],
        [["defobs"],
            [
                "Specify how to represent the transverse observation points.",
                GetQString(ObsPointDist)+": in position.",
                GetQString(ObsPointAngle)+": in angle."
            ]
        ],
        [["normenergy"], "Specify the photon energy as a normalized value."],
        [["powlimit"], "Put an upper limit on the allowable partial power."],
        [["optDx"], "Horizontal angular acceptance is virtually closed to reduce the computation time, without changing the calculation results."],
        [["xsmooth"], "Apply smoothing for the Wigner function of BMs and wigglers; larger values results in more smooth profiles."],
        [["fouriep"], "Calculation is done at the \"Fourier Plane\" as schematically illustrated below, to evaluate the angular profile at the source point (center of the light source)"+fpsche],
        [["wiggapprox"], "Apply the wiggler approximation, in which radiation incoherently summed up (as photons)."],
        [["esmooth"], "Apply the spectral smoothing; this is useful to reduce the computation time by smoothing the spectral fine structure potentially found in undulator radiation."],
        [["smoothwin"], "Smoothing window in %; this means that the photon flux at 1000 eV is given as the average from 995 to 1005 eV."],
        [["accuracy"], "Specify the numerical accuracy. In most cases, "+GetQString(DefaultLabel)+" is recommended, in which case SPECTRA automatically arranges all the relevant parameters."+(rst?"":(" If "+GetQString(CustomLabel)+" is selected, the user should configure each parameter. Refer to "+GetLink(MenuLabels.accuracy, MenuLabels.accuracy, false)+" for details.")), true]
    ];

    let bpfprms = [
        [["bpfcenter"], "Central photon energy of the bandpath filter (BPF)."],
        [["bpfwidth"], "Full width of the boxcar-type BPF."],
        [["bpfsigma"], "1&sigma; of the Gaussian BPF."],
        [["bpfmaxeff"], "Maximum transmission rate of the BPF."]
    ];

    let cmdprms = [
        [["CMD"], "Perform "+GetQString("Coherent Mode Decomposition")+" after calculating the Wigner function."],
        [["CMDfld"], 
            [
                "Calculate and export the modal profiles based on the CMD results",
                GetQString(NoneLabel)+": do not export.",
                GetQString(JSONOnly)+": export in the JSON format.",
                GetQString(BinaryOnly)+": export in the "+(rst?"binary format":(GetLink(sections.binary, "binary format", false)+".")),
                GetQString(BothFormat)+": export in the both formats."
            ]
        ],
        [["CMDint"], "Calculate and export the modal intensity profiles based on the CMD results"],
        [["CMDcmp"], "Reconstruct the Wigner function using the CMD result to check its validity."],
        [["CMDcmpint"], "Reconstruct the flux density profile using the CMD result to check its validity."],
        [["GSModel"], "Use Gaussian-Schell (GS) model to simplify the CMD and reduce computation time."],
        [["GSModelXY"], 
            [
                "Use Gaussian-Schell (GS) model for CMD. Select the axis to apply.",
                GetQString(NoneLabel)+": do not use GS model.",
                GetQString(XOnly)+": GS model for horizontal axis.",
                GetQString(YOnly)+": GS model for vertical axis.",
                GetQString(BothFormat)+": GS model for both axes."
            ]
        ],
        [["HGorderxy", "HGorderx", "HGordery"], "Upper limit of the order of the Hermite-Gaussian functions to be used in the CMD."],
        [["maxHGorderxy", "maxHGorderx", "maxHGordery"], "Maximum orders of the coherent mode."],
        [["maxmode"], "Maximum number of the coherent modes for post-processing (exporting the modal profile, reconstructing the Wigner functions)."],
        [["fcutoff"], "Cutoff flux (normalized) to be used to determine the maximum HG order of of each coherent mode."],
        [["cutoff"], "Cutoff amplitude (normalized) of individual modes, below which Hermite-Gaussian functions are neglected."],
        [["fieldrangexy", "fieldrangex", "fieldrangey"], "Range of the spatial grid to export the modal profile."],
        [["fieldgridxy", "fieldgridx", "fieldgridy"], "Intervals of the spatial grid points to export the modal profile."]
    ];

    let felprms = [
        [["fel"], 
            ["Coherent radiation in an FEL (free electron laser) mode is calculated. If this option is enabled, interaction (energy exchange) between electrons and radiation is taken into account in solving the equation of electron motion in the 6D phase space."+(rst?"":(" This is exactly what the general FEL simulation code does (solving the FEL equation), and thus the amplification process in FELs can be evaluated. There are several types of FEL modes available in SPECTRA, depending on how to prepare the initial condition. Note that the self-amplified spontaneous emission (SASE) FELs cannot be evaluated; this comes from the difficulty in dealing with the shot-noize, which is the source of amplification in SASE FELs.",
                GetQString(FELPrebunchedLabel)+": the electron beam is pre-bunched and no seed light is supposed.",
                GetQString(FELSeedLabel)+": a simple seed pulse is supposed.",
                GetQString(FELCPSeedLabel)+": same as the above, but the seed pulse is chirped.",
                GetQString(FELDblSeedLabel)+": same as the above, but a couple of pulses are supposed.",
                GetQString(FELReuseLabel)+": reuse the bunch factor evaluated in the former calculations. This option is available by opening a former calculation result of coherent radiation,  with the FEL mode option enabled."))
            ], true
        ],
        [["pulseE"], "Seed pulse energy."],
        [["wavelen"], "Seed wavelength."],
        [["pulselen"], "Seed pulse length."],
        [["tlpulselen"], "Transform-limited pulse length of the chirped seed pulse."],
        [["srcsize"], "Seed source size."],
        [["waistpos"], "Longitudinal position where the seed pulse forms a beam waist."],
        [["timing"], "Relative time of the seed pulse with respect to the electron beam."],
        [["gdd", "tod"], "Group delay dispersion and third order dispersion of the chirped seed pulse."],
        [["pulseE_d"], "Pulse energies of the 1st and 2nd seed pulses. Available when "+GetQString(FELDblSeedLabel)+" is chosen. Note that there are a number of parameters having the same suffix (1,2), which denotes that they are for the 1st and 2nd seed pulses."],
        [["svstep","radstep"], "Define the longitudinal step to solve the FEL equation."+(rst?"":(" Refer to the schematic drawing for details."+felsche+"The light source is divided into a number of steps (indicated by yellow arrows), and each step is further divided into a number of substeps (blue arrows). The bunch factor of the electron beam is assumed to be constant within a step and is updated at the end, which is then used to calculate the coherent radiation in the next step. The radiation waveform is assumed to be constant within a substep besides the slippage effect and is updated at the end, which is then used to evaluate the interaction with electrons in the next substep. A number of data sets used in each step is saved in the output file, if "+(rst?ConfigPrmsLabel.exportInt[0]:(GetLink(ConfigPrmsLabel.exportInt[0], ConfigPrmsLabel.exportInt[0], false)+" option is enabled."))))],
        [["eproi"], "Photon energy range of interest to solve the FEL equation."],
        [["particles"], "Number of macro-particles to represent the electron beam."],
        [["edevstep"], "Interval of the electron energy deviation to export the electron density in the (E-t) phase space."],
        [["R56"], "Strength of the virtual dispersive section. Need to be specified if "+GetLink(ConfigPrmsLabel.R56Bunch[0], ConfigPrmsLabel.R56Bunch[0], false)+" option is enabled."],
        [["exportInt"], "Export the intermediate data evaluated during the process of solving the FEL equation.", true],
        [["R56Bunch"], "Export the bunch profile after the electron beam passes through a virtual dispersive section located downstream of the source, as in the high-gain harmonic generation (HGHG) FELs.", true],
        [["exportEt"], "Export the electron density in the (E-t) phase space."],
    ];

    let wpropprms = [
        [["gridspec"], 
            [
                "Specify the transverse grid at each longitudinal step.",
                GetQString(AutomaticLabel)+": automatically determined.",
                GetQString(NormSlitLabel)+": specify the grid intervals normalized by the RMS beam size at each longitudinal step.",
                GetQString(FixedSlitLabel)+":  specify the grid intervals directly."
            ]
        ],
        [["grlevel"], "Specify a finer grid interval if "+GetQString(AutomaticLabel)+"is selected for "+GetQString(ConfigPrmsLabel.gridspec[0])+". Default is 0 and a larger number means a finer interval."],
        [["optics"], 
            [
                "Specify an optical element inserted in the beamline.",
                GetQString(NoneLabel)+": no optical elements.",
                GetQString(SingleLabel)+": insert a single slit.",
                GetQString(DoubleLabel)+": insert a double slit.",
                GetQString(ThinLensLabel)+": insert an ideal thin lens."
            ]
        ],
        [["optpos"], "Longitudinal position to insert an optical element."],
        [["aptx"], "Horizontal aperture size."],
        [["aptdistx"], "Distance between the double slit in the horizontal direction."],
        [["apty"], "Vertical aperture size."],
        [["aptdisty"], "Distance between the double slit in the vertical direction."],
        [["softedge"], "Range of the "+GetQString("Soft Edge")+"of the slit. At the edge of the slit, the photon intensity is supposed to gradually drop, as opposed to a hard-edged condition. Longer soft-edge ranges reduce the diffraction effects. In addition, the memory requirement is relaxed as well."],
        [["diflim"], "Specify the threshold to cut off the diffraction effects and determine the angular range to compute the Wigner function after passing through a slit."],
        [["memsize"], "Approximate memory size needed during the computation. The parameters should be arranged so that this value is not too large."],
        [["foclenx"], "Focal length of an ideal lens in the horizontal direction."],
        [["focleny"], "Focal length of an ideal lens in the vertical direction."],
        [["anglelevel"], "Specify the angular range to evaluate the Wigner function after an optical element. If set to 0, the angular range is determined to be consistent with the relevant parameters; a larger number means a large angular range."],
        [["wigner"], "Export the Wigner function after an optical element."],
        [["aprofile"], "Export the angular profile after an optical element."],
        [["csd"], "Export the cross spectral density."],
        [["degcoh"], "Export the degree of spatial coherence."],
    ];

    if(rst){
        return [...prmconts, ...optconnts, ...bpfprms, ...cmdprms, ...felprms, ...wpropprms];
    }
    return GetPrmListTable( 
        [ConfigPrmsLabel, ConfigPrmsLabel, ConfigPrmsLabel, ConfigPrmsLabel, ConfigPrmsLabel, ConfigPrmsLabel], 
        [prmconts, optconnts, bpfprms, cmdprms, felprms, wpropprms], 
        ["Main Parameters", "Options", "Parameters to Specify the BPF", ["Parameters for the CMD (coherent mode decomposition)", CMDParameterLabel], "Parameters for the FEL mode", ["Parameters for the wavefront propagation", PropParameterLabel]]);
}

function GetOutputPrmList(rst = false)
{
    let outprms = [
        [["format"], "Select the format of the output file from three options"+(rst?".":(": \"JSON\" for the JSON format, \"ASCII\" for the ASCII (simple text with the suffix \".txt\") format, and \"Both\" for the both options. Note that the ASCII format is identical to that in the older (&lE 10.2) versions, however, it cannot be used later for "+(rst?"post-processing":(GetLink(sections.postproc, sections.postproc, false)+" (visualization of the data)."))))],
        [["folder", "prefix", "serial"], "Input the path of the output file in [Folder], a prefix text in [Prefix], and a serial number in [Serial Number]. Then the output file name is given as [Folder]/[Prefix]-[Serial Number].[Format]"+(rst?"":(", like \"/Users/data/test-1.json\", where \"/Users/data\", \"test\", 1, and \"json\" refer to [Folder], [Prefix], [Serial Number] and [Format]. Note that the serial number can be -1 (negative), in which case it is not attached to the data name."))],
        [["comment"], "Input any comment in [Comment] if necessary, which is saved in the output file and can be referred later on."]
    ];

    if(rst){
        return outprms;
    }
    return GetPrmListTable([OutputOptionsLabel], [outprms], [""]);
}

function GetOutputItems(rst = false)
{
    let outitems = [
        [["Flux Density"], "Spatial (far field conditions) or angular (others) flux density"],
        [["Flux"], "Partial photon flux passing through a finite angular acceptance, or total flux integrated over the whole solid angle"],
        [["GA. Brilliance", "Brilliance"], "Photon density in the 4D phase space (or its maximum). \"GA.\" stands for \"Gaussian Approximation\", meaning that it is evaluated by assuming that the photon beam is a Gaussian one."],
        [["Prj. Brilliance"], "Brilliance projected on the (X,X') or (Y,Y') phase space."],
        [["PL(s1/s0)", "PC(s3/s0)", "PL45(s2/s0)"], "Stokes parameters: PL, PC, PL45 correspond to the horizontal, left-hand and 45-deg.-inclined linear polarizations."],
        [["Harmonic Energy", "Peak Energy"], "Photon energy of a target harmonic. \"Harmonic\" is defined as n&epsilon;<sub>1st</sub>, where n is the harmonic number, while \"Peak\" specifies the photon energy at which the photon intensity (flux density of flux) becomes the maximum; in general this is slightly lower than the former one."],
        [["Power Density"], "Spatial (far field conditions) or angular (others) power density"],
        [["Partial Power", "Total Power"], "Partial power passing through a finite angular acceptance, or total power integrated over the whole solid angle"],
        [["Harmonic Power (x)", "Harmonic Power (y)"], "Angular power density corresponding to a specific harmonic and polarization state"],
        [["Volume Power Density"], "Refer to "+GetLink(MenuLabels.vpdens, MenuLabels.vpdens, false)],
        [["Natural Size", "Natural Divergence"], "Source size and angular divergence of radiation emitted by a single electron"],
        [["Horizontal Size", "Vertical Size"], "Source size of a photon beam emitted by an electron beam with finite emittance and energy spread"],
        [["Horizontal Divergence", "Vertical Divergence"], "Angular divergence of a photon beam"],
        [["Coherent Flux"], "Photon flux contained in a coherent volume of radiation that is fully coherent in space"],
        [["Coherent Power"], "Power contained in a bandwidth corresponding to 1 &mu;m coherence length"],
        [["Horizontal Coherent Fraction", "Vertical Coherent Fraction"], "Quality of a photon beam in terms of coherence, defined as $\\Sigma_x\\Sigma_{x'}/(\\lambda/4\\pi)$ for the horizontal direction and a similar expression for the vertical direction, where $\\Sigma_{x}$ and $\\Sigma_{x'}$ are the source size and angular divergence of the photon beam."],
        [["Harmonic Number"], "Harmonic number to generate the maximum photon intensity at a given photon energy"],
        [["Observer Time"], "Time in the laboratory frame (for observer)"],
        [["Horizontal Electric Field", "Vertical Electric Field"], "Electric field of radiation"],
        [["Horizontal Real Field", "Horizontal Imaginary Field", "Vertical Real Field", "Vertical Imaginary Field"], "Complex amplitude of radiation evaluated at a given photon energy"],
        [["Separability"], rst?"":("Refer to "+GetLink(sections.separa, sections.separa, false))],
        [["Deg. Coherence (X)", "Deg. Coherence (Y)", "Deg. Coherence (Total)"], rst?"":("Refer to "+GetLink(sections.degcoh, sections.degcoh, false))],
    ];
    if(rst){
        return outitems;
    }
    return GetPrmListTable([null], [outitems], [""]);
}

function GetOutDataInf(rst = false)
{
    let caption = "Format of the "+GetQString(OutputLabel)+" object";
    let titles = ["Key", "Details", "Format"];
    let outdata = [
        [DataDimLabel, "Dimension of the calculation data, or the number of independent variables.", "number"],
        [DataTitlesLabel, "Titles of individual arrays included in the "+GetQString(DataLabel)+" object.", "array (1D)"],
        [UnitsLabel, "Units of individual arrays included in the "+GetQString(DataLabel)+" object.", "array (1D)"],
        [DetailsLabel, "Additional information of the 3D-array data, which is generated in several calculation types. For example, those with "+GetQString(MenuLabels.tgtharm)+" (flux specific to a specific harmonic) result in a number of data, each of which is 2D and corresponds to the harmonic number.", "array (1D)"],
        [DataLabel, "Main body of the calculation result data.", "array (2D or 3D)"]
    ];
    if(rst){
        return {caption:caption, titles:titles, data:outdata};
    }
    return GetTable(caption, titles, outdata);
}

var NoInput = {
    [AccLabel]: [
        AccPrmsLabel.aimA[0],
        AccPrmsLabel.cirm[0],
        AccPrmsLabel.peakcurr[0],
        AccPrmsLabel.epsilon[0],
        AccPrmsLabel.sigma[0],
        AccPrmsLabel.sigmap[0],
        AccPrmsLabel.gaminv[0],
        AccPrmsLabel.minsize[0],
        AccPrmsLabel.partform[0],
        AccPrmsLabel.buf_eGeV[0],
        AccPrmsLabel.buf_bunchlength[0],
        AccPrmsLabel.buf_bunchcharge[0],
        AccPrmsLabel.buf_espread[0]
    ],
    [SrcLabel]: [
        SrcPrmsLabel.reglength[0],
        SrcPrmsLabel.Kperp[0],
        SrcPrmsLabel.pslip[0]
    ],
    [ConfigLabel]: [
        ConfigPrmsLabel.illumarea[0],
        ConfigPrmsLabel.e1strange[0],
        ConfigPrmsLabel.fsize[0],
        ConfigPrmsLabel.psize[0],
        ConfigPrmsLabel.fdiv[0],
        ConfigPrmsLabel.pdiv[0],
        ConfigPrmsLabel.e1strange[0],
        ConfigPrmsLabel.memsize[0],
        ConfigPrmsLabel.wigsizex[0],
        ConfigPrmsLabel.wigsizey[0],
        ConfigPrmsLabel.bmsizex[0],
        ConfigPrmsLabel.bmsizey[0],
        ConfigPrmsLabel.wigexplabel[0]
    ],
    [OutFileLabel]: [OutputOptionsLabel.fixpdata[0]],
    [AccuracyLabel]: [
        AccuracyOptionsLabel.integlabel[0],
        AccuracyOptionsLabel.rangelabel[0],
        AccuracyOptionsLabel.otherslabel[0]
    ]
}
for(let j = SrcLabelOrder.indexOf("sigmar"); j <= SrcLabelOrder.indexOf("linpower"); j++){
    NoInput[SrcLabel].push(SrcPrmsLabel[SrcLabelOrder[j]][0]);
}
//----- python -----

function GetAccPrmTable()
{
    let data = (new AccPrmOptions()).GetReferenceList(AccLabelOrder, NoInput[AccLabel]);
    return data;
}

function GetSrcPrmTable()
{
    let data = (new SrcPrmOptions()).GetReferenceList(SrcLabelOrder, NoInput[SrcLabel]);
    return data;
}

function GetConfigPrmTable()
{
    let data = (new ConfigPrmOptions()).GetReferenceList(ConfigLabelOrder, NoInput[ConfigLabel]);
    return data;
}

function GetOutFilePrmTable()
{
    let noinput = [OutputOptionsLabel.fixpdata[0]];
    let data = (new OutFileOptions()).GetReferenceList(OutputOptionsOrder, noinput);
    return data;
}

function GetMenu(baseobj)
{
    let data = "";
    for(let j = 0; j < baseobj.length; j++){
        let subsections = Object.values(baseobj[j])[0];
        let isobj = false;
        for(let i = 0; i < subsections.length; i++){
            if(typeof subsections[i] != "string" 
                    && Array.isArray(subsections[i]) == false){
                isobj = true;
                continue;
            }
        }
        if(!isobj){
            let div = document.createElement("div");
            div.appendChild(GetLink(Object.keys(baseobj[j])[0], Object.keys(baseobj[j])[0], true));
            data += div.outerHTML;
            continue;
        }
        let details = document.createElement("details");
        let summary = document.createElement("summary");
        summary.innerHTML = Object.keys(baseobj[j])[0];
        details.appendChild(summary);
        let list = document.createElement("ul");
        for(let i = 0; i < subsections.length; i++){
            let item = document.createElement("li");
            if(typeof subsections[i] == "string"){
                continue;
            }
            let link = GetLink(Object.keys(subsections[i])[0], Object.keys(subsections[i])[0], true);
            item.appendChild(link);
            list.appendChild(item);
        }
        details.appendChild(list);
        data += details.outerHTML;
    }  
    return data;
}

function GetFileMenu()
{
    let caption = "Contents of \"File\" main menu. Note that some of them are disabled in the python interactive mode.";
    let titles = [{cols: 2, label: "Menu"}, null, "Details",];
    let filemenus = [
        [{cols:2, label:MenuLabels.new}, null, "Start SPECTRA with a default parameter set."],
        [{cols:2, label:MenuLabels.open}, null, "Open a SPECTRA parameter file. Even though a parameter file for older (&lE; 10.2) versions is accepted as well, it cannot be saved in the older format."],
        [{cols:2, label:MenuLabels.append}, null, "Append the parameter sets in another parameter file to the current ones."],
        [{cols:2, label:MenuLabels.loadf}, null, "Load the output file of a former calculation."],
        [{rows:4, label:""}, MenuLabels.outpostp, "For post-processing (visualization)"],
        [null, MenuLabels.wignerCMD, "To perform CMD with the Wigner function"],
        [null, MenuLabels.wignerProp, "To perform Wavefront Propagation with the Wigner function"],
        [null, MenuLabels.CMDr, "For modal analysis with the CMD result"],
        [null, MenuLabels.bunch, "Reuse the bunch factors for other coherent radiation calculations"],
        [{cols:2, label:MenuLabels.save}, null, "Save all the parameters and options in the current file."],
        [{cols:2, label:MenuLabels.saveas}, null, "Save all the parameters and options in a new file."],
        [{cols:2, label:MenuLabels.exit}, null, "Quit SPECTRA and Exit"]
    ];
    return GetTable(caption, titles, filemenus);
}

function GetRunMenu()
{
    let caption = "Contents of \"Run\" main menu";
    let titles = ["Menu", "Details"];
    let filemenus = [
        [MenuLabels.process, "Create "+CalcProcessLabel+" with the current parameters and options."],
        [MenuLabels.export, "Export the current parameters and options to a file, which can be used as an input file to directly call the solver."],
        [MenuLabels.start, "Start a new calculation, or launch the "+CalcProcessLabel+"."]
    ];
    return GetTable(caption, titles, filemenus);
}

function GetSetupDialog()
{
    let caption = "Setup Dialogs opened by running a submenu of \"Edit\" menu";
    let titles = ["Submenu", "Details"];
    let dlgconts = [
        [MenuLabels.material, [
            "Open a dialog to edit the material available for the filters and absorbers.",
            WriteFigure("editmaterial.png", "Dialog to edit the material for the filters and absorbers."),
            "In SPECTRA, a number of built-in materials are available (gray-painted ones), which cannot be edited.",
            "To add a new material, input its name and density in an empty column, together with the atomic number (Z) and mass ratio (Ratio) of each element constituting the material. The total amount of the mass ratio should be 1. The numbers of columns (materials) and rows (elements) are automatically increased when necessary."
        ]],
        [MenuLabels.unit, [
            "Open a dialog to select the unit of items in the "+GetLink(sections.dataimp, sections.dataimp)+".",
            WriteFigure("unitconf.png", "Dialog to select the unit of items in the data file to be imported."),
            "Note that the selection should be made before importing the data. After importing, change of the unit in this dialog has no effect."
            ], MenuLabels.unit
        ],
        [MenuLabels.accuracy, [
            "Open a dialog to customize the target numerical accuracy. Note that this menu is not available if "+GetQString(DefaultLabel)+" is selected for "+GetLink(ConfigPrmsLabel.accuracy[0], ConfigPrmsLabel.accuracy[0])+" option.",
            "There are a number of parameters to specify the numerical accuracy, according to the numerical method and target item. Refer to the table below.",
            "@accudlg"
            ], MenuLabels.accuracy
        ],
        [MenuLabels.MPI, [
            "Open a dialog to configure the parallel computing. Select a desired scheme in "+GetQString(MPIOptionsLabel.parascheme[0])+" to enable the parallel computing  and input a number of processes (MPI) or threads (Multithread) to launch in "+GetQString(MPIOptionsLabel.processes[0])+" or "+GetQString(MPIOptionsLabel.threads[0])+". Note that MPI (message passing interface) environment should be installed for parallel computing using MPI, and the path to \"mpiexec\" should be set."
        ], MenuLabels.MPI]
    ];
    return GetTable(caption, titles, dlgconts);
}

function GetAccuracyDialog()
{
    let caption = "Configurations to specify the target numerical accuracy.";
    let titles = [{cols:2, label:"Item"}, null, "Details/Example"];
    let dlgconts = [
        [{cols: 2, label: AccuracyOptionsLabel.integlabel[0]}, null, "Step size for integration or discretization of a function. Larger numbers mean  finer steps."],
        [{rows: 4, label: ""}, AccuracyOptionsLabel.accdisctra[0], "Along the longitudinal axis. For example, steps to comupte the electron trajectory in the SR source."],
        [null, AccuracyOptionsLabel.accinobs[0], "Over the transverse (spatial and/or angular) coordinate. For example, convolution with the spatial distribution function of the electron beam."],
        [null, AccuracyOptionsLabel.accineE[0], "Photon energy steps. For example, spectrum of SR emitted by a single electron, which is obtained by FFT."],
        [null, AccuracyOptionsLabel.accinpE[0], "Electron energy steps in  convolution with the energy distribution function of the electron beam."],
        [{cols: 2, label: AccuracyOptionsLabel.rangelabel[0]}, null, "Integration range for integration or discretization of a function. Larger numbers mean broader ranges."],
        [{rows: 4, label: ""}, AccuracyOptionsLabel.acclimtra[0], "Downstream and upstream ends of the longitudinal coordinate."],
        [null, AccuracyOptionsLabel.acclimobs[0], "Transverse range for integration and convolution."],
        [null, AccuracyOptionsLabel.acclimpE[0], "Photon energy range to be taken into account."],
        [null, AccuracyOptionsLabel.acclimeE[0], "Ehoton energy range to be taken into account"],
        [{rows: 6, label: AccuracyOptionsLabel.otherslabel[0]}, AccuracyOptionsLabel.accconvharm[0], "An integer to judge the convergence of harmonics (maximum harmonic number to be taken into account). Larger numbers mean higher harmonics"],
        [null, AccuracyOptionsLabel.accEcorr[0], "Adjust the energy loss of the electron beam to be consistent with the FEL gain.  Available when "+GetLink(ConfigPrmsLabel.fel[0], ConfigPrmsLabel.fel[0], false)+" option is enabled."],
        [null, AccuracyOptionsLabel.accconvMC[0], "A real number to judge the convergence of integration for Monte-Carlo method."],
        [null, AccuracyOptionsLabel.accconvMCcoh[0], "A real number to judge the convergence of integration for coherent raddiation calculation."],
        [null, AccuracyOptionsLabel.acclimMCpart[0], "If checked, limit the number of macroparicles for Monte-Carlo method."],
        [null, AccuracyOptionsLabel.accMCpart[0], "Maximum number of macroparticles (see above)."]
    ];
    return GetTable(caption, titles, dlgconts);
}

function GetPlotlyDialog()
{
    let xyscales = XYScaleOptions.join(", ");
    let plottypes = PlotTypeOptions.join(", ");
    let clmap = ColorMapOptions.join(", ");
    let caption = "Options for the graphical plot";
    let titles = ["Item", "Details", "Available Options"];
    let dlgconts = [
        [{rows: 2, label:PlotOptionsLabel.normalize[0]}, {rows: 2, label: "Select how to normalize the animation plot"}, 
                    ForEachLabel+": y-/z-axis scale is normalized by the maximum value for each slide"],
        [null, null, ByMaxLabel+": y-/z-axis scale is normalized by the maximum value over the whole slides"],
        [PlotOptionsLabel.xscale[0], "Select the scale for x axis", xyscales],
        [PlotOptionsLabel.yscale[0], "Select the scale for y axis", xyscales],
        [PlotOptionsLabel.type[0], "Select the type of the 1D plot", plottypes],
        [PlotOptionsLabel.size[0], "Size of the symbol", "Input a number"],
        [PlotOptionsLabel.width[0], "Width of the line", "Input a number"],
        [{rows:3, label:PlotOptionsLabel.type2d[0]}, {rows:3, label:"Select the type of the 2D plot"}, ContourLabel+": contour plot with a specific color map"],
        [null, null, SurfaceLabel+": surface plot painted with a specific color map"],
        [null, null, SurfaceShadeLabel+": shaded surface plot illuminated by a specific light source"],
        [PlotOptionsLabel.shadecolor[0], "Select the color of the light source to create a shaded surface plot", "Select from the color picker dialog."],
        [PlotOptionsLabel.colorscale[0], "Select the color map. Several built-in options are available but cannot be customized", clmap],
        [PlotOptionsLabel.wireframe[0], "If checked, grid lines are shown on the surface plot", ""]
    ];
    return GetTable(caption, titles, dlgconts);
}

function GetCMDResult()
{
    let caption = "Keys and details of the "+GetQString(CMDResultLabel)+" object";
    let titles = ["Key", "Details", "Symbol", "Unit"];
    let valietms = [
        "",
        MatrixErrLabel+": numerical error in Cholesky expansion", 
        FluxErrLabel+": total amount of the normalized photon flux contained in each coherent mode", 
        WignerErrLabel+": consistency between the original and reconstructed Wigner functions"
    ]
    let validity = WriteListedItem(valietms, false);
    let cmdcont = [
        [MaxOrderLabel, "Maximum order of the Hermite-Gaussian (HG) functions to form the coherent mode", "", ""],
        [WavelengthLabel, "Wavelength of the Wigner function used for CMD ", "$\\lambda$", "m"],
        [FluxCMDLabel, "Total photon flux evaluated from the Wigner function", "$F$", "photons/sec/0.1%b.w."],
        [SrcSizeLabel, "Parameters to define the arguments of HG functions", "$\\sigma$ or $\\sigma_{x,y}$ (1D or 2D)", "m"],
        [OrderLabel, "Indices to define the orders of HG functions for a specific coherent mode", "", ""],
        [CMDErrorLabel, [
            "Validity of the CMD", validity
        ], "", ""],
        [NormFactorLabel, "Coefficient to retrieve the Wigner function from the modal amplitude", "$W_0$", "photons/sec/mm<sup>2</sup>/mrad<sup>2</sup>/0.1%b.w."],
        [AmplitudeReLabel, "Matrix to represent the complex amplitude of HG functions for each coherent mode, real part", "", ""],
        [AmplitudeImLabel, "Imaginary part of the above matrix", "", ""]
    ];
    return GetTable(caption, titles, cmdcont);
}

function GetCMDPostProcess()
{
    let caption = "Objects available by post-processing the CMD results";
    let titles = ["Object Name", "Details"];
    let cmdcont = [
        [CMDModalFluxLabel, "Information about how much flux is contained in each coherent mode."],
        [CMDFieldLabel+"/"+CMDIntensityLabel, "Spatial profile of the complex field amplitude/intensity calculated for each coherent mode. Note that the calculation range and number of points are specified in "+GetLink(CMDParameterLabel, CMDParameterLabel)+"."],
        [CMDCompareIntLabel, "Flux density profile reconstructed from the modal and Wigner functions by projection to the real space (X,Y)"],
        [CMDCompareXLabel, "Wigner function reconstructed from the modal profile, to be compared with the original one to check how the CMD was successful. To facilitate the comparison, both functions are projected on the (X,X') phase space."],
        [CMDCompareYLabel, "Same as the above, but for the (Y,Y') phase space."]
    ];
    return GetTable(caption, titles, cmdcont);
}

function GetFELData()
{
    let caption = "Objects available when "+GetLink(ConfigPrmsLabel.fel[0], ConfigPrmsLabel.fel[0], false)+" option is enabled.";
    let titles = ["Object Name", "Details"];
    let cmdcont = [
        [FELCurrProfile, "Current profile of the electron beam."],
        [FELEtProfile, "Electron density in the E-t (energy-time) phase space."],
        [FELCurrProfileR56, "Current profile of the electron beam after passing through a virtual dispersive section. Available if "+GetLink(ConfigPrmsLabel.R56Bunch[0], ConfigPrmsLabel.R56Bunch[0], false)+" option is enabled."],
        [FELEtProfileR56, "Electron density in the (E-t) phase space after the virtual dispersive section. Available if "+GetLink(ConfigPrmsLabel.R56Bunch[0], ConfigPrmsLabel.R56Bunch[0], false)+" option is enabled."],
        [FELBunchFactor, "Bunch factor of the electron beam."],
        [FELPulseEnergy, "Total energy of the radiation pulse."],
        [FELEfield, "Waveform of the on-axis electric field of radiation in the far-field zone."],
        [FELInstPower, "Temporal profile of the instantaneous radiation power."],
        [FELSpectrum, "Spectrum of the radiation pulse."]
    ];
    return GetTable(caption, titles, cmdcont);
}

function GetWignerRelated()
{
    let caption = "Properties calculated by a mathematical operation of the 4D Wigner Function";
    let titles = ["Property", "Details"];
    let cmdcont = [
        [sections.separa, "In most cases, especially when the electron beam emittance is not too small compared to the optical emittance at the target wavelength, the phase-space density and thus the Wigner function can be separated into two functions $W_x$ and $W_y$. Namely, the Wigner function $W$ can be substituted for by $W_d = W_xW_y/F$, where $F$ is the total photon flux, and the numerical cost for evaluation of the phase-space density is significantly reduced. To evaluate the consistency between the two functions $W$ and $W_d$ and to examine if the above discussions are valid under a specific condition, the separability $\\kappa$ has been introduced, which is defined as \\[\\kappa=1-\\sqrt{\\frac{\\langle(W_d-W)\\rangle^2}{\\langle W^2\\rangle}},\\] where $\\langle f\\rangle$ denotes the average of the function $f$ over the range of interest.", sections.separa],   
        [sections.degcoh, "The degree of spatial coherence $\\zeta$ in SPECTRA is defined as \\[\\zeta=\\left(\\frac{\\lambda}{F}\\right)^2\\int\\!\\!\\!\\!\\int W^2(\\boldsymbol{r},\\boldsymbol{r}')d\\boldsymbol{r}\\boldsymbol{r}',\\] which is actually a spatial average of the degree of spatial coherence $\\mu^2(\\boldsymbol{r}_1,\\boldsymbol{r}_2)$ usually calculated at two different points $\\boldsymbol{r}_1$ and $\\boldsymbol{r}_2$. This is to avoid the complexity of expressing the function by two coordinate variables. Using the two functions $W_x$ and $W_y$, the degree of spatial coherence in the horizontal or vertical direction can be defined in a similar manner.", sections.degcoh]
    ];
    return GetTable(caption, titles, cmdcont);
}

function GetE1scanList()
{
    let caption = "Relation between K<sub>x</sub> and K<sub>y</sub> in &epsilon;<sub>1st</sub> scan.";
    let titles = [SrcPrmsLabel.gaplink[0], "Details"];
    let funcont = [
        [NoneLabel, "K<sub>x</sub>/K<sub>y</sub> is the same as that currently displayed in the GUI, and is kept constant for different values of &epsilon;<sub>1st</sub>."],
        [AutomaticLabel, "K<sub>x</sub>/K<sub>y</sub> is determined by "+GetQString(SrcPrmsLabel.geofactor[0])+"."],
        [ImpGapTableLabel, "K<sub>x</sub>/K<sub>y</sub> is determined by "+GetQString(SrcPrmsLabel.gaptbl[0])+" data imported in "+GetLink(sections.preproc, sections.preproc)+" subpanel."]
    ];
    return GetTable(caption, titles, funcont);
}

function GetReference(refidx)
{
    let reflists = [
        {
            spectrajsr: "T. Tanaka and H. Kitamura, \"SPECTRA - a synchrotron radiation calculation code,\" J. Synchrotron Radiation 8, 1221 (2001)"
        },
        {
            spectrasri: "T. Tanaka and H. Kitamura, \"Recent Progress of the Synchrotron Radiation Calculation Code SPECTRA\", Proc. 9th Int. Conf. Synchrotron Rad. Instrum. (SRI2006), 355"
        },
        {
            spectra11jsr: "T. Tanaka, \"Major upgrade of the synchrotron radiation calculation code SPECTRA,\" J. Synchrotron Radiation 28, 1267 (2021)"
        },
        {
            refwigner: "T. Tanaka, \"Numerical methods for characterization of synchrotron radiation based on the Wigner function method,\" Phys. Rev. ST-AB 17, 060702 (2014)"
        },
        {
            refcmd: "T. Tanaka, \"Coherent mode decomposition using mixed Wigner functions of Hermite-Gaussian beams,\" Optics Letters 42, 1576 (2017)"
        },
        {
            refperr: "R. Walker, \"Interference effects in undulator and wiggler radiation sources\", Nucl. Instrum. Methods Phys. Res., Sect. A 335, 328 (1993)"
        },
        {
            refsegment: "T. Tanaka and H. Kitamura, \"Simple scheme for harmonic suppression by undulator segmentation,\" Journal of Synchrotron Radiation 9, 266 (2002)"
        },
        {
            refsegx: "T. Tanaka and H. Kitamura, \"Production of linear polarization by segmentation of helical undulator,\" Nucl. Instrum. Meth. A490, 583 (2002)"
        },
        {
            refunivperr: "T. Tanaka, \"Universal representation of undulator phase errors,\" Phys. Rev. AB 21, 110704 (2018)"
        },
        {
            refwigprop: "K. J. Kim, \"Characteristics of Synchrotron Radiation,\" in Physics of Particle Accelerators, AIP Conf. Proc. 184 (Am. Inst. Phys., New York, 1989), p. 565."
        }
    ];
    let refol = document.createElement("ol")
    refol.className = "paren";
    for(let j = 0; j < reflists.length; j++){
        let refi = document.createElement("li");
        let keys = Object.keys(reflists[j]);
        refi.innerHTML = reflists[j][keys[0]];
        refi.id = keys[0];
        refol.appendChild(refi);
        refidx[keys[0]] = "["+(j+1).toString()+"]";
    }
    return refol.outerHTML;
}

function ExportHelpFile()
{
    let prmlabels = [AccPrmsLabel, SrcPrmsLabel, ConfigPrmsLabel];
    let espchars = RetrieveAllEscapeChars(prmlabels);
    espchars.push("&uarr;");

    let baseobj = CopyJSON(help_body);
    let data =
    '<!DOCTYPE html>\n<html lang="en">\n<head>\n<title>Reference Manual for SPECTRA '+Version+'</title>\n'
    +'<link rel="stylesheet" type="text/css" href="reference.css">\n'
    +"<script>MathJax = {chtml: {matchFontHeight: false}, tex: { inlineMath: [['$', '$']] }};</script>\n"
    +'<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>\n'
    +'</head>\n<body>\n'
    +'<div style="display: flex;">\n'
    +'<div class="sidemenu">\n'

    data += GetMenu(baseobj);
    data += '</div>\n<div class="main">';

    let cont = "";
    for(let j = 0; j < baseobj.length; j++){
        cont += WriteObject(0, baseobj[j]);
    }

    let ss = GetFldDataFormatTable();

    let contrep = cont 
        .replace("<p>@filemenu</p>", GetFileMenu())
        .replace("<p>@runmenu</p>", GetRunMenu())
        .replace("<p>@setupdlg</p>", GetSetupDialog())
        .replace("<p>@accudlg</p>", GetAccuracyDialog())
        .replace("<p>@plotlyedit</p>", GetPlotlyDialog())
        .replace("<p>@accprm</p>", GetAccPrmList())
        .replace("<p>@srcprm</p>", GetSrcPrmList())
        .replace("<p>@srctype</p>", GetSrcTypesTable())
        .replace("<p>@flddata</p>", GetFldDataFormatTable())
        .replace("<p>@confprm</p>", GetConfigPrmList())
        .replace("<p>@outfile</p>", GetOutputPrmList())
        .replace("<p>@calctype</p>", GetSPECTRAMenuTable(false))
        .replace("<p>@accjson</p>", GetAccPrmTable())
        .replace("<p>@srcjson</p>", GetSrcPrmTable())
        .replace("<p>@confjson</p>", GetConfigPrmTable())
        .replace("<p>@outjson</p>", GetOutFilePrmTable())
        .replace("<p>@preproc</p>", GetPreprocDetailTable())
        .replace("<p>@import</p>", GetImportDetailTable())
        .replace("<p>@cmdresult</p>", GetCMDResult())
        .replace("<p>@cmdpp</p>", GetCMDPostProcess())
        .replace("<p>@felvar</p>", GetFELData())
        .replace("<p>@wigrel</p>", GetWignerRelated())
        .replace("<p>@outitems</p>", GetOutputItems())
        .replace("<p>@reference</p>", referencelist)
        .replace("<p>@e1scan</p>", GetE1scanList())
        .replace("<p>@outdata</p>", GetOutDataInf());

        data += FormatHTML(contrep);

    data += "</div>\n</body>\n";
    data = ReplaceSpecialCharacters(espchars, data);

    let blob = new Blob([data], {type:"text/html"});
    let link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = "reference.html";
    link.click();
    link.remove();
}
