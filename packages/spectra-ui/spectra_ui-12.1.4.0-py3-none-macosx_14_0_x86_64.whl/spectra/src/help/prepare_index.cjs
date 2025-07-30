const fs_node = require("fs-extra");
const path = require("path");
const toml = require("toml");

let idxstr;
try{
    idxstr = fs_node.readFileSync("src/constants.js", "utf8");
}
catch{
	console.log("Error: cannot load constants.js");
	process.exit(-1);
}

let lines = idxstr.split("\n");
let VersionNumber = "0.0.0";
for(const line of lines){
	if(line.includes("Version ")){
		let ist = line.indexOf('"');
		let iend = line.lastIndexOf('"');
		let vernum = line.substring(ist+1, iend);
		if(vernum.length > 0){
			VersionNumber = vernum;
		}
	}
}
if(VersionNumber == "0.0.0"){
	console.log("Error: version number not found");
	process.exit(-1);
}

function ExportTable(object, widths = null)
{
	let lines = [];
	lines.push(".. csv-table:: "+object.caption);
	lines.push("   :header: \""+object.titles.join("\", \"")+"\"");
	if(widths != null){
		lines.push("   :widths: "+widths);
	}
	lines.push("   ")
	for(let j = 0; j < object.data.length; j++){
		let items = object.data[j];
		for(let n = 0; n < items.length; n++){
			if(items[n] == null){
//				items[n] = "&uarr;";
				items[n] = "";
			}
			else{
				items[n] = items[n].
					replaceAll("\\varepsilon", "\\\\varepsilon").
					replaceAll("\\pi", "\\\\pi").
					replaceAll("\\Delta", "\\\\Delta").
					replaceAll("\\lambda", "\\\\lambda").
					replaceAll("\\[", "\\\\[").
					replaceAll("\\]", "\\\\]");
			}
		}
		lines.push("   \""+items.join("\", \"")+"\"");
	}
	return lines;
}

function GetHelpLink(helpurl, category)
{
	let categurl = category.replaceAll(" ", "%20");
	let url = "`"+category+" <"+helpurl+"#"+categurl+">`_";
	return url;
}


if(process.argv.length > 2 && process.argv[2] == "-p"){
	let [Major, Minor, Bugfix] = VersionNumber.split(".");
	let vera = VersionNumber;
	if(process.argv.length > 3){
		vera = VersionNumber+process.argv[3];
	}
	try{
		idxstr = fs_node.readFileSync("python/setup.py", "utf8");
	}
	catch{
		console.log("Error: cannot load python/setup.py");
		process.exit(-1);
	}
	lines = idxstr.split("\n");
	for(let n = 0; n < lines.length; n++){
		if(lines[n].includes("version")){
			lines[n] = '    version="'+vera+'",';
		}
	}
	idxstr = lines.join("\n");
	fs_node.writeFileSync("python/setup.py", idxstr);

	try{
		idxstr = fs_node.readFileSync("python/spectra/__init__.py", "utf8");
	}
	catch{
		console.log("Error: cannot load python/spectra/__init__.py");
		process.exit(-1);
	}
	lines = idxstr.split("\n");
	for(let n = 0; n < lines.length; n++){
		if(lines[n].includes("VERSION")){
			let items = lines[n].split("=");
			if(items.length < 3){
				continue;
			}
			let version = items[2].trim();
			let [major, minor] = version.split(".");
			if(major != Major || minor != Minor){
				console.log("Error: version number inconsistent in __init__.py");
				process.exit(-1);
			}
		}
	}
	
	process.exit(0);
}
else if(process.argv.length > 2 && process.argv[2] == "-r"){
	process.chdir("python/dist");
	const files = fs_node.readdirSync("./");
	for(const filename of files){
		if(filename.includes(".whl")){
			let items = filename.split("-");
			items[2] = "py3";
			items[3] = "none"
			let filen = "./"+items.join("-");
			try {
				fs_node.renameSync(filename, filen)	
			}
			catch (e) {
				console.log("Error: cannot rename wheel file");
				process.exit(-1);		
			}	
		}
	}
	process.exit(0);
}
else if(process.argv.length > 2 && process.argv[2] == "-s"){ // rst files

	process.chdir("src");
	idxstr = "Plotly = {Icons: {pencil: ''}}\n\n;"
	idxstr += fs_node.readFileSync("constants.js", "utf8");
	let pystr = fs_node.readFileSync("help/generate_reference.js", "utf8");
	let lines = pystr.split(/[\r\n]/);
	for(let n = 0; n < lines.length; n++){
		lines[n].trimEnd();
	}
	let pyini = lines.indexOf("//----- python -----");
	let pyfin = lines.lastIndexOf("//----- python -----");
	let pylines = lines.slice(pyini+1, pyfin-1);
	let pyss = pylines.join("\n");
	idxstr += pyss.replaceAll("\n\n", "\n");
	idxstr += fs_node.readFileSync("help/generate_python_rst.cjs", "utf8");

	process.chdir("..");
	fs_node.writeFileSync("temp.cjs", idxstr);
	const {
		GetMenuKey, GetMenuCateg, GetParameterKey, GetBrowserIssue, GetPythonOption, GetAccKey, GetUnitKey, GetOutDataInf,
		HelpURL, PySampleURL, Version2Digit,
		AccLabel, SrcLabel, ConfigLabel, OutFileLabel
	} = require("T:/SourceCode11/spectra/12.0/prj/temp.cjs");
	fs_node.unlinkSync("temp.cjs");

	let overview = 
	[
		"Overview of *spectra-ui*",
		"========================",
		"",
		"The python package *spectra-ui* is to operate the synchrotron radiation code `SPECTRA <https://spectrax.org/spectra/>`_ from the python script.",
		"",
		"How it works?",
		"-------------",
		"To save the effort of the software development as much as possible, *spectra-ui* takes advantage of the resource for the desktop version; the diagram shown below explains how *spectra-ui* works as a python script.",
		"",	
		".. figure:: ./spectraui.png",
		"",
		"Diagram of how *spectra-ui* communicates with other software components.",
		"",
		"As a GUI, *spectra-ui* opens the remote repository for the source file with a web browser and communicates with it through *Selenium WebDriver*, a well-known framework to automate the operation in the web brwoser. When necessary, *spectra-ui* invokes the solver (*spectra_solver* or *spectra_solver_nompi*) as a child process and communicates with it (sends a command or receives the status of progress). Upon completion of the child process, *spectra-ui* loads the result and sends it to the browser to be plotted in the *Pre-Processing* or *Post-Processing* tabbled panel. In case the user is offline, the source files, which are downloaded and stored in the local repository when *spectra-ui* is installed, can be used instead. Refer to :ref:`launchopt` about how to enable this option.",
		"",
		"Installation",
		"------------",
		"",
		"*spectra-ui* is available from the Python Package Index (PyPI), and thus can be installed by a standard pip command,",
		"",
		".. code-block::",
		"",
		"   pip install spectra-ui [--user]",
		"",
		"or ",
		"",
		".. code-block::",
		"",
		"   pip3 install spectra-ui [--user]",
		"",
		"on some platforms.",
		"",
		"The [--user] option may be needed when global installation is not allowed. Note that binary packages are available for Windows and Mac OS platforms, but not for Linux distributions because of the too diverse versions of core libraries (glibc). Thus in Linux platforms, the source codes are downloaded and compiled during the installation process. This means that the user should arrange the enviroment for software development before installation, such as the C/C++ compiler, CMake, and MPI (optional), and the installation process may need a bit long time.",
		"",
		"Getting Started",
		"---------------",
		"",
		"The simplest way to get started with *spectra-ui* is to run as a module. If you have \"Chrome\" browser installed in your environment, try,",
		"",
		".. code-block::",
		"",
		"   python -m spectra",
		"",
		"or,",
		"",
		".. code-block::",
		"",
		"   python3 -m spectra",
		"",
		"to launch *spectra-ui* as a GUI mode, in which most of the functions available in the desktop version are supported.",
		"",
		"If you prefer another browser, add an option (for example -e for Edge) to specify it. Refer to :ref:`launchopt` for details of how to launch *spectra-ui* using a preferred browser. Note that \"Chrome\" (or \"Edge\") is recommended because of several issues encountered in other brwosers as summarized below.",
		"",
		...ExportTable(GetBrowserIssue()),
		"",
		"Operation Mode",
		"--------------",
		"",
		"There are three operation modes in *spectra-ui*: GUI, CLI, and interactive ones.",
		"",
		"- The GUI mode mimics the desktop version, and all the operations are done in the GUI (web browser). This mode has been prepared as an alternative to the desktop version in Linux distributions.",
		"",
		"- The CLI (command line interface, or CUI = console user interface) mode is dedicated to the utilization of SPECTRA for a batch job. It can be operated only through the python script, and the GUI is not shown. In this mode, the output file is not imported by the post-processor for visualization, but the data is stored in memory buffer to be processed later on.",
		"",
		"- The interactive mode has both of the capabilities available in the GUI and CLI modes. Namely, it can be operated through the GUI (web browser) and receives commands from the python script.",
		"",
		"To enable each operation mode, refer to the instruction of the function `Start()<spectra.html#spectra.Start>`.",
		"",
		".. _launchopt:",
		"",
		"Launch Options",
		"--------------",
		"",
		...ExportTable(GetPythonOption(), "20, 15, 65"),
		""
	].join("\n");
	fs_node.writeFileSync("python/spectra/docs/overview.rst", overview);

	let prmwidths = "20, 10, 40, 30";

	let parameters = [
		"Keywords for Arguments",
		"======================",
		"",
		"In several functions of *spectra-ui*, a number of arguments should be given to specify the calculation conditions and parameters.",
		"",
		"Specify the Calculation Type",
		"-------------------------------",
		"",
		"Before starting any calculation in *spectra-ui*, the calculation type should be specified by calling \"SelectCalculation()\" function, using a number of keywords summarized below as its arguments.",
		"",
		...ExportTable(GetMenuKey()),
		"",
		"Edit the Parameter",
		"------------------",
		"",
		"After selecting the calculation type, parameters to specify the accelerator/ light source, and numerical conditions may need to be modified, which can be done by calling \"Set()\" function with adequate arguments. For example,",
		"",
		".. code-block::",
		"",
		"   spectra.Set(\"acc\", \"eGeV\", 3)",
		"",
		"means that the electron energy is set to 3 GeV. Refer to the followings for details.",
		"",
		"Parameter category (1st argument)",
		"^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^",
		"",
		"The 1st argument should specify the category of the parameter to be set. It should be given by one of the keywords as summarized below.",
		"",
		...ExportTable(GetMenuCateg()),
		"",
		"Accelerator parameters",
		"^^^^^^^^^^^^^^^^^^^^^^",
		"",
		"Keywords to specify the accelerator parameters are summarized below. They should be used as the 2nd agument. Refer to "+GetHelpLink(HelpURL, AccLabel)+" for more details about each parameter.",
		"",
		...ExportTable(GetParameterKey()[AccLabel], prmwidths),
		"",
		"Light source parameters",
		"^^^^^^^^^^^^^^^^^^^^^^^",
		"",
		"Keywords to specify the light source parameters are summarized below. They should be used as the 2nd agument. Refer to "+GetHelpLink(HelpURL, SrcLabel)+" for more details about each parameter.",
		"",
		...ExportTable(GetParameterKey()[SrcLabel], prmwidths),
		"",
		"Configurations",
		"^^^^^^^^^^^^^^",
		"",
		"Keywords to specify the numerical configurations are summarized below. They should be used as the 2nd agument. Refer to "+GetHelpLink(HelpURL, ConfigLabel)+" for more details about each parameter.",
		"",
		...ExportTable(GetParameterKey()[ConfigLabel], prmwidths),
		"",
		"Output File Settings",
		"^^^^^^^^^^^^^^^",
		"",
		"Keywords to specify the output file are summarized below. They should be used as the 2nd agument. Refer to "+GetHelpLink(HelpURL, OutFileLabel+" Subpanel")+" for more details about each parameter.",
		"",
		...ExportTable(GetParameterKey()[OutFileLabel], prmwidths),
		"",
		"Other parameters",
		"----------------",
		"",
		"Numerical accuracy",
		"^^^^^^^^^^^^^^^^^^",
		"",
		"The numerial accuracy is specified by calling \"SetAccuracy()\". The 1st argument specifies the numerical procedure (integration, discretization, etc.), and should be one of the followings.",
		"",
		...ExportTable(GetAccKey()),
		"",
		"Unit for data import",
		"^^^^^^^^^^^^^^^^^^^^",
		"",
		"To import the data prepared by the user, its unit should be specified by calling \"SetUnit()\". The 1st argment specifies the data type and should be one of the followings.",
		"",
		...ExportTable(GetUnitKey()),
		"",
		"Retrieving the output data",
		"--------------------------",
		"",
		"The output data in SPECTRA is saved as a JSON object, and thus can be retrieved easily by using one of the keys summarized below.",
		"",
		...ExportTable(GetOutDataInf(true))
	];
	parameters = parameters.join("\n")
	fs_node.writeFileSync("python/spectra/docs/parameters.rst", parameters);

	let sampletxt = 
		"Example of python source codes\n==============================\n\nRefer to the following python source codes to get started with spectra-ui."

	sampletxt += "\n\nThe sample files are available `here <"+PySampleURL+">`_ "

	sampletxt +=		
		"In the 1st example, SPECTRA is launched in the interactive mode with the Chrome browser, and the calculations of spectra are repeated at three different transverse positions. Then, the results are plotted to see how the spectral profile changes as the observation position. Finally, the comparative data is exported as an ASCII file.\n\n";

	process.chdir("python/samples");
	const files = fs_node.readdirSync("./");
	for(const filename of files){
		let idx = filename.lastIndexOf(".py");
		if(idx >= 0){
			idxstr = fs_node.readFileSync(filename, "utf8");
			lines = idxstr.split("\n");
			let codes = [];
			let hearderon = false;
			for(let n = 0; n < lines.length; n++){				
				if(lines[n].includes('"""')){
					if(hearderon){
						codes.push("");
						codes.push(".. code-block::");
					}
					hearderon = !hearderon;
				}
				else{					
					if(hearderon){
						if(lines[n].trim() != ""){
							codes.push(lines[n].trimEnd());
						}
					}
					else{
						codes.push("   "+lines[n].trimEnd());
					}
				}
			}
			codes.splice(1, 0, "");
			let sepline = "";
			sepline = sepline.padStart(codes[0].length, "^");
			codes.splice(1, 0, sepline);
			sampletxt += "\n"+codes.join("\n");
		}
	}
	process.chdir("../spectra/docs");
	fs_node.writeFileSync("examples.rst", sampletxt);

	process.chdir("..");
	const { execSync } = require('child_process');
	try {
		const stdout = execSync('sphinx-build ./docs ./docs/_build');
		console.log(`stdout: ${stdout.toString()}`);
	} catch (e) {
		console.log(e);
	}
	idxstr = fs_node.readFileSync("docs/_build/parameters.html", "utf8");
	let idxprm = idxstr.
		replaceAll("<head>", "<head>\n  <script>MathJax = {chtml: {matchFontHeight: false}, tex: { inlineMath: [['$$', '$$']] }};</script>\n  <script id=\"MathJax-script\" async src=\"https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js\"></script>").
		replaceAll("&amp;", "&").
		replaceAll("&lt;", "<").
		replaceAll("&gt;", ">").
		replaceAll("’", "'").
		replaceAll("“", "\"").
		replaceAll("”", "\"");

	fs_node.writeFileSync("docs/_build/parameters.html", idxprm);
	let pydir = "../../../package/"+Version2Digit+"/python/"
	fs_node.copySync("docs/_build", pydir+"docs");

	console.log(process.cwd());
	try {
		pydir = pydir.replaceAll("/", "\\");
		let cmdstr = "Compress-Archive -Path ..\\samples -DestinationPath "+pydir+"samples.zip -Force";
		const stdout = execSync(cmdstr, {shell: "PowerShell.exe"});
	} catch (e) {
		console.log(e);
	}

	process.exit(0);
}

try{
    idxstr = fs_node.readFileSync("package.json", "utf8");
}
catch{
	console.log("Error: cannot load package.json");
	process.exit(-1);
}
let pkjobj = JSON.parse(idxstr);
let vernum = "0.0.0";
if(pkjobj.hasOwnProperty("version")){
	vernum = pkjobj.version;
}
if(vernum != VersionNumber){
	console.log("Inconsistent version number in package.json");
	process.exit(-1);
}

try{
    idxstr = fs_node.readFileSync("src-tauri/Cargo.toml", "utf8");
}
catch{
	console.log("Error: cannot load Cargo.toml");
	process.exit(-1);
}
pkjobj = JSON.parse(JSON.stringify(toml.parse(idxstr).package));
vernum = "0.0.0";
if(pkjobj.hasOwnProperty("version")){
	vernum = pkjobj.version;
}
if(vernum != VersionNumber){
	console.log("Inconsistent version number in Cargo.toml");
	process.exit(-1);
}

try{
    idxstr = fs_node.readFileSync("src/spectra.html", "utf8")
}
catch{
	console.log("Error: cannot load spectra.html")
	process.exit(-1);
}

lines = idxstr.split("\n");
let ellines = [];
let tauri = process.argv.length > 2 && process.argv[2] == "-t";
for(let n = 0; n < lines.length; n++){
	if(lines[n].indexOf("generate_reference.js") >= 0){
		continue;
	}
	if(lines[n].indexOf("generate_header.js") >= 0){
		continue;
	}
	if(lines[n].indexOf("numeric-1.2.6.min.js") >= 0){
		continue;
	}
	if(!tauri && lines[n].includes("</body>")){
		ellines.push("    <script>iniFile = \"<?php echo isset($_GET['file']) ? $_GET['file'] : ''; ?>\" </script>");
		ellines.push("    <script>iniBL = \"<?php echo isset($_GET['bl']) ? $_GET['bl'] : ''; ?>\" </script>");
		ellines.push("    <script>iniPP = \"<?php echo isset($_GET['pp']) ? $_GET['pp'] : ''; ?>\" </script>");
	}
	ellines.push(lines[n]);
}
let outstr = ellines.join("\n");

if(tauri){
	outstr = outstr.replaceAll("src=\"", "src=\"/").replaceAll("href=\"", "href=\"/");
}
fs_node.writeFileSync("src/index.html", outstr, "utf8");

process.exit(0);