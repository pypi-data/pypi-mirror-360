"use strict";

function leastSquareN(points, dim) {
	if(points.length < dim) {
		return numeric.rep([dim], 0);
	}
	var A = numeric.rep([dim, dim], 0);
	var b = numeric.rep([dim], 0);
	for(var i = 0; i < points.length; i++) {
		for(var j = 0; j < dim; j++) {
			for(var k = 0; k < dim; k++) {
				A[j][k] += Math.pow(points[i][0], 2*(dim-1)-j-k);
			}
		}
		for(var j = 0; j < dim; j++) {
			b[j] += points[i][1]*Math.pow(points[i][0], dim-1-j);;
		}
	}
	var c = numeric.solve(A, b)
	return c;
}

//-------------------------
// create field distribution file for SC3
//-------------------------

function RadLength(Nper, lu, symm)
{
    let L = lu*(symm?1.5:2.0);
    if(Nper > 1){
        L += lu*(Nper-1);
    }
    return L;
}

function GenerateMPField(Nper, lu, K, zini, dzbase, symm, z, bx, by, pfactor, simple = false)
{
    let Bp = K/lu/COEF_K_VALUE;
    let ku = 2.0*Math.PI/lu;
    let L = RadLength(Nper, lu, symm);
    let pointspp = Math.floor(0.5+L/dzbase);
    let dz = L/pointspp;
    let isendfactor = Array.isArray(pfactor);

    let zorg = zini+L/2.0, jsec;
    let bdr, phase, bcoef, zr;
    phase = symm ? 0 : -Math.PI/2.0;
    if(simple){ // -1/2, 1, 1/2
        bdr = [lu/4.0];
        bcoef = [0.5];
    }
    else if(symm && Nper == 1){ // -1/2, 1, 1/2
        bdr = [lu/4.0];
        bcoef = [0.5];
    }
    else{        
        if(Nper > 1){ // -1/4, -3/4, 1,...., 3/4, 1/4
            bdr = [lu/2.0, 0];
            bcoef = [1.0/4.0, 3.0/4.0];
        }
        else{
            bdr = [lu/2.0];
            bcoef = [1.0/3.0];    
        }
    }
    if(Nper > 1){
        for(jsec = 0; jsec < bdr.length; jsec++){
            if(simple){
                bdr[jsec] += (Nper-1)*lu*0.5;
            }
            else if(symm){
                bdr[jsec] += (Nper-1.5)*lu*0.5;
            }
            else{
                bdr[jsec] += (Nper-1)*lu*0.5;
            }
        }
    }
    for(let n = 0; n < pointspp; n++){
        zr = n*dz+zini;
        z.push(zr);
        let br = Bp*Math.cos(ku*(zr-zorg)+phase);
        for(jsec = 0; jsec < bdr.length; jsec++){
            if(Math.abs(zr-zorg) >= bdr[jsec]){
                break;
            }    
        }
        if(jsec < bdr.length){
            if(isendfactor){
                if(zr < zorg){
                    br *= pfactor[0];
                }
                else{
                    br *= pfactor[1];
                }
            }
            else{
                br *= bcoef[jsec];
            }
        }
        by.push(br);
        bx.push(0.0);
    }
    return zr+dz;
}

function GenerateHelicalRetarder(L, K, zini, dzbase, z, bxy)
{
    let lu = L*0.5;
    let ku = 2.0*Math.PI/lu;
    let pointspp = Math.ceil(L/dzbase);
    let dz = L/pointspp;

    let zorg = zini+L/2.0, zr, jsec;

    let phase = [0, -Math.PI/2.0];
    let bdo = [3.0*lu/4.0, lu];
    let bdr = [lu/4.0, lu/2.0];
    let bcoef = [0.5, 1.0/3.0];
    let Bp = K/lu/COEF_K_VALUE;
    for(let n = 0; n < pointspp; n++){
        zr = n*dz+zini;
        z.push(zr);
        for(let j = 0; j < 2; j++){
            let br = Bp*Math.cos(ku*(zr-zorg)+phase[j]);
            if(Math.abs(zr-zorg) >= bdo[j]){
                br = 0;
            }
            else if(Math.abs(zr-zorg) >= bdr[j]){
                br *= bcoef[j];
            }
            bxy[j].push(br);
        }
    }
    return zr+dz;
}

function Smoothing(havgp, tarr, jarr, jnew)
{
    let points = [];
    for(let n = 0; n < tarr.length; n++){
        for(let m = -havgp; m <= havgp; m++){
            let mi = m+n;
            if(mi >= 0 && mi < tarr.length){
                points.push([tarr[mi], jarr[mi]]);
            }
        }
        let a = leastSquareN(points, 4);
        jnew.push(
            ((a[0]*tarr[n]+a[1])*tarr[n]+a[2])*tarr[n]+a[3]
        );
        points.length = 0;
    }
}

function GetPeakPositionsFit(havgp, tarr, jarr, tpeak, jpeak, threshold, skiptr)
{
    let points = [];
    let ncurr = 0;
    for(let n = 1; n < tarr.length-1; n++){
        points.length = 0;
        for(let m = -havgp; m <= havgp; m++){
            let mi = m+n;
            if(mi >= 0 && mi < tarr.length){
                points.push([tarr[mi], jarr[mi]]);
            }
        }
        let a = leastSquareN(points, 3);
        if(a[0] >= 0){
            continue;
        }
        let pkpos = -a[1]/2/a[0];
        let peak = a[2]-a[1]**2/4/a[0];
        peak = GetParabolic(tarr, jarr, pkpos);
        if((pkpos-tarr[n-1])*(pkpos-tarr[n+1]) < 0 
                && peak > threshold && Math.abs(pkpos) > skiptr){
            if(n > ncurr+havgp){
                tpeak.push(pkpos);
                jpeak.push(peak);
                ncurr = n;   
            }
        }
    }
}

function GetEndFactor(lamhat, Lint, lu, K, pol)
{
    let Lhat = Lint/lu;
    let D = ((lamhat-Lhat)/K**2-5.0/8.0)/(4*Lhat-4.5);
    if(D < 0){
        return null;
    }
    let alpha = pol*Math.sqrt(D);

    let lamhatr = Lhat+K**2*(5.0/8.0+alpha**2*(4*Lhat-4.5));

    alpha += 0.5;
    let theta = K/(1500/0.511)*(1-2*alpha);

    return alpha;
}

function GetPoleFactor(lamhat, Lint, lu, K, pol)
{
    let Lhat = Lint/lu;
    let D = ((lamhat-Lhat)/K**2-5.0/8.0)/(Lhat-0.25);
    if(D < 0){
        return null;
    }
    let alpha = pol*Math.sqrt(D);

    let lamhatr = Lhat+K**2*(5.0/8.0+alpha**2*(Lhat-0.25));

    return alpha;
}

function GenerateField4SC3(flip, epret, 
    isempt = false, dbl = false, thresh = 1.5, norsl = 1, norpos = -1, Lchc = 0.3, skiptr = 0)
{
    let eloss = 0;
//    eloss=parseFloat(window.prompt("Input average energy loss/section", "0"));

    let accobj = GUIConf.GUIpanels[AccLabel].JSONObj;
    let gam2 = 1.0/(accobj[AccPrmsLabel.gaminv]*0.001);
    gam2 *= gam2;
    let srcobj = GUIConf.GUIpanels[SrcLabel].JSONObj;
    let segobj = srcobj[SrcPrmsLabel.segprm[0]];
    let symm = srcobj[SrcPrmsLabel.field_str[0]] == SymmLabel;
    let lu = srcobj[SrcPrmsLabel.lu]*0.001; // mm -> m
    let Nrad = srcobj[SrcPrmsLabel.periods];
    let dzbase = lu/100;
    let K = srcobj[SrcPrmsLabel.Kperp];
    let Lrad = RadLength(Nrad, lu, symm);
    let Lret;
    let td;
    if(dbl){
        td = norsl;
    }

    let bunchtype = accobj[AccOptionsLabel.bunchtype[0]];
    let tarr = [], jarr = [], ttmp, jtmp;
    if(bunchtype == CustomCurrent){
        let obj = accobj[AccOptionsLabel.currdata[0]];
        ttmp = CopyJSON(obj.data[0]);
        jtmp = CopyJSON(obj.data[1]);
    }
    else if(bunchtype == CustomEt){
        let obj = accobj[AccOptionsLabel.Etdata[0]];
        ttmp = CopyJSON(obj.data[0]);
        let earr = CopyJSON(obj.data[1]);
        etarr = CopyJSON(obj.data[2]);
        for(let n = 0; n < ttmp.length; n++){
            let jc = 0;
            for(let m = 0; m < earr.length; m++){
                jc += etarr[m*ttmp.length+n]
            }
            jtmp.push(jc);
        }
    }
    else{
        Alert("Bunch profile not valid.");
        return;
    }   

    let havgpoints = 3;
    let jnew = [];
    Smoothing(havgpoints, ttmp, jtmp, jnew);
    let plotid = GetIDFromItem(AccLabel, AccOptionsLabel.currdata[0], -1)+SuffixPlotBody;

    let plobj = document.getElementById(plotid);
    let nplots = plobj.data.length;
    for(let i = 1; i < nplots; i++){
        Plotly.deleteTraces(plotid, 1);
    }

    Plotly.addTraces(plotid, {x:ttmp, y:jnew, name:"Fit Result"});  

    let tpeak = []; 
    let jpeak = [];
    let javg = jtmp.reduce((acc, curr)=>acc+curr)/jtmp.length;
    GetPeakPositionsFit(havgpoints, ttmp, jnew, tpeak, jpeak, javg*thresh, skiptr)
    if(tpeak.length < 2){
        Alert("Number of current peaks is less than 2.");
        return;
    }

    let M = segobj[SegPrmsLabel.segments];
    let iniM = 0;
    if(M < tpeak.length){
        iniM = Math.floor((tpeak.length-M)/2);
        let incr = jpeak[iniM] > jpeak[iniM+M] ? -1 : 1;
        while((incr < 0 && jpeak[iniM] > jpeak[iniM+M]) 
            || (incr > 0 && jpeak[iniM] < jpeak[iniM+M])){
            iniM += incr;
        }
        if(jpeak[iniM] < jpeak[iniM+M+1]){
            iniM++;
        }
    }
    else{
        M = tpeak.length-1;
    }

    let tpick = tpeak.slice(iniM, M+iniM+1);
    let jpick = jpeak.slice(iniM, M+iniM+1);

    if(eloss != 0){
        for(let m = 1; m <= M; m++){
            tpick[M-m] += (tpick[M]-tpick[M-m])*eloss*m*2;
        }
    }

    if(!dbl){
        Plotly.addTraces(plotid, {x:tpick, y:jpick, name:"Peak Positions", mode:"markers",
        marker:{symbol:"circle-open", size:15, color:"black"}});
    }

    if(norpos >= 0){
        let jp = M-norpos;
        if(jp < 1 || jp > tpick.length){
            Alert("Position to tune the slippaeg is out ouf range");
            return;
        }
        let slpos = [[tpick[jp], tpick[jp-1]], [jpick[jp], jpick[jp-1]]];
        Plotly.addTraces(plotid, {x:slpos[0], y:slpos[1], name:"Slippage Tuned", mode:"lines", 
            line:{color:"green"}});
    }        

    let pdelay = segobj[SegPrmsLabel.phi0]/2.0;
    if(pdelay > 1){ // double pulse option
        Lret = segobj[SegPrmsLabel.interval]/2-Lrad;
    }
    else{
        Lret = segobj[SegPrmsLabel.interval]-Lrad;
        pdelay = 0;
    }
    let luret = epret ? Lret/2.0 : Lret/1.5;
    let luretch = Lchc/1.5;
    let Kpret = 0;
    if(pdelay > 1){
        pdelay *= srcobj[SrcPrmsLabel.lambda1]*1e-9;
        Kpret = (pdelay*16*gam2/luret-12)/5;
        if(Kpret < 0){
            Alert("Interval of the double pulse too short.");
            return;    
        }
        Kpret = Math.sqrt(Kpret);
    }

    let z = [], bx = [], by = [], secno = [], raddelay, radpermin, radKmin = 2;

    if(symm && Nrad == 1){
        raddelay = lu*(12+5*K*K)/16/gam2;
    }
    else{
        raddelay = lu/gam2;
        if(Nrad > 1){
            raddelay += lu*7*K*K/32/gam2;
        }
        else{
            raddelay += lu*7*K*K/18/gam2;
        }
    }
    radpermin = lu*(1+radKmin**2/2)/2/gam2/CC*1e15;
    if(Nrad > 1){
        if(symm){
            raddelay += (Nrad-1.5)*lu*(1+K*K/2)/2/gam2;
        }
        else{
            raddelay += (Nrad-1)*lu*(1+K*K/2)/2/gam2;
        }
    }
    if(Kpret > 0){
        raddelay *= 2;
    }

    if(dbl){
        let tmin = (raddelay+pdelay+Lret/2/gam2)/CC*1e15;
        td = Math.abs(td);
        let tpeak2 = Array.from(tpeak, t => t+td);
        let index = [0, tpeak.length-1];
        while(tpeak[index[0]] < tpeak2[0]){
            index[0]++;            
        }
        while(tpeak2[index[1]] > tpeak[tpeak.length-1]){
            index[1]--;            
        }
        let tnew = [tpeak2[0]];
        let jnew = [jpeak[0]];
        let curr = 0;
        let currindex = [index[0], 0]
        let ts = [tpeak, tpeak2];
        do{
            let dt;
            while((dt = ts[curr][currindex[curr]]-tnew[tnew.length-1]) < tmin){
                currindex[curr]++;
                if(currindex[curr] >= tpeak.length){
                    break;
                }
            }
            tnew.push(ts[curr][currindex[curr]]);
            jnew.push(jpeak[currindex[curr]]);
            curr = 1-curr;
            currindex[curr]++;
        } while(currindex[0] < tpeak.length || currindex[1] < index[1]);

        if(M < tnew.length){
            iniM = Math.floor((tnew.length-M)/2);
            let incr = jnew[iniM] > jnew[iniM+M] ? -1 : 1;
            while((incr < 0 && jnew[iniM] > jnew[iniM+M]) 
                || (incr > 0 && jnew[iniM] < jnew[iniM+M])){
                iniM += incr;
            }
            if(jnew[iniM] < jnew[iniM+M+1]){
                iniM++;
            }
        }
        else{
            M = tnew.length-1;
        }    
        tpick = tnew.slice(iniM, M+iniM+1);
        jpick = jnew.slice(iniM, M+iniM+1);

        Plotly.addTraces(plotid, {x:tpick, y:jpick, name:"Peak Positions", mode:"markers",
        marker:{symbol:"circle-open", size:15, color:"black"}});
    }
    else if(dbl){
        let tpick2 = Array.from(tpick, t => t+td);
        let tpall = tpick.concat(tpick2);
        let tdmin = (raddelay+2*Lret/2/gam2)/CC*10**15;
        tpall.sort((a, b) => a-b);
        tpall.push(tpall[tpall.length-1]+tdmin);
        let tnew = [], tplot = [];
        for(let n = 0; n < tpall.length-1; n++){
            let tinv = tpall[n+1]-tpall[n];
            if(tinv < tdmin){
                if(tinv > radpermin){
                    tnew.push([tpall[n], tpall[n+1]]);
                    tplot.push(tpall[n]);
                    tplot.push(tpall[n+1]);
                }
                else{
                    tnew.push((tpall[n+1]+tpall[n])/2);
                    tplot.push((tpall[n+1]+tpall[n])/2);
                }
                n++;    
            }
            else{
                tnew.push(tpall[n]);
                tplot.push(tpall[n]);
            }
        }
        let jplot = Array.from(tplot, t => GetParabolic(tpick, jpick, t));
        Plotly.addTraces(plotid, {x:tplot, y:jplot, name:"Peak Positions", mode:"markers",
        marker:{symbol:"circle-open", size:15, color:"black"}});       
        tpick = tnew;
        M = tpick.length-1;
    }

    let zini = -(M-1)*segobj[SegPrmsLabel.interval]*0.5-Lrad*0.5;
    let simple = false;

    // fill with 0 field at entrace
//    zini -= lu*1.5;
//    zini = GenerateMPField(1, lu, 0, zini, dzbase, true, z, bx, by);   

    let pol = 1, pfactor, Kret, Nradr = Nrad, Kr = K, raddelayr;
    for(let m = 0; m < M; m++){
        let luretr = luret;
        let Lretr = Lret;
        if(m == norpos){
            luretr = luretch;
            Lretr = Lchc;
        } 
        if(isempt){
            let Lint = segobj[SegPrmsLabel.interval];
            pfactor = [];
            for(let i = 1; i >= 0; i--){
                if((i == 1 && m == 0) || (i == 0 && m == M-1)){
                    pfactor.push(0.5);
                    continue;
                }
                let delay = (tpick[M-m+i]-tpick[M-m-1+i])*1e-15*CC;
                let lamhat = delay/(lu/2/gam2);
                let alpha = GetEndFactor(lamhat, Lint, lu, K, (-1)**m);                
                pfactor.push(alpha);
            }
            Kret = 0;
        }
        else{
            let delay, krd = [0,0], krdelay = [0,0];
            for(let j = 0; j < 2; j++){
                if(Array.isArray(tpick[M-m-j])){
                    let tdd = (tpick[M-m-j][1]-tpick[M-m-j][0])*1e-15*CC;
                    krd[j] = tdd-lu/2/gam2;
                    if(krd[j] < 0){
                        Alert("Delay at "+(M-m-j).toString()+"-th twin interval too narrow.");
                        return;    
                    }
                    krd[j] = Math.sqrt(4*gam2*krd[j]/lu);
                    krdelay[j] = lu*(12+5*krd[j]*krd[j])/16/gam2;
                }    
            }
            if(Array.isArray(tpick[M-m]) && Array.isArray(tpick[M-m-1])){
                delay = (tpick[M-m][0]-tpick[M-m-1][1])*1e-15*CC;                
                Nradr = 2;
                simple = true;
                Kr = -krd[0];
                raddelayr = (krdelay[0]+krdelay[1])/2;
            }
            else if(Array.isArray(tpick[M-m])){
                delay = (tpick[M-m][0]-tpick[M-m-1])*1e-15*CC;
                Nradr = 2;
                simple = true;
                Kr = -krd[0];
                raddelayr = (krdelay[0]+raddelay)/2;
            }
            else if(Array.isArray(tpick[M-m-1])){
                delay = (tpick[M-m]-tpick[M-m-1][1])*1e-15*CC;
                Nradr = 1;
                Kr = K;
                raddelayr = (raddelay+krdelay[1])/2;
                simple = false;
            }
            else{
                delay = (tpick[M-m]-tpick[M-m-1])*1e-15*CC;
                Nradr = Nrad;
                raddelayr = raddelay;
                Kr = K;
                simple = false;
            }
            if(m == norpos){
                Kret = delay*norsl-raddelayr-pdelay-Lretr/2/gam2;
            }
            else{
                Kret = delay-raddelayr-pdelay-Lretr/2/gam2;
            }
            if(Kret < 0){
                Alert("Delay at "+(M-m).toString()+"-th interval too narrow.");
                return;    
            }
            if(epret){
                Kret = Math.sqrt(Kret*gam2/luret/(5.0/16.0+7.0/18.0));
            }
            else{
                Kret = Math.sqrt(Kret*gam2/luretr/(5.0/16.0));
            }
        }
        if(flip){
            if(dbl){
                pol = (-1)**(Math.floor(m/2));
            }
            else{
                pol = (-1)**m;
            }

        }
        Kret *= pol;

        // GenerateMPField(Nper, lu, K, zini, dzbase, symm, z, bx, by, pfactor, simple = false)
        if(isempt){
            zini = GenerateMPField(Nradr, lu, Kr, zini, dzbase, symm, z, bx, by, pfactor);
        }
        else{
            zini = GenerateMPField(Nradr, lu, Kr, zini, dzbase, symm, z, bx, by, null, simple);
        }
        if(Kpret > 0){
            zini = GenerateMPField(1, luret, Kpret*pol, zini, dzbase, true, z, bx, by, null);
            zini = GenerateMPField(Nradr, lu, Kr, zini, dzbase, symm, z, bx, by, null);
        }
        if(m < M-1){
            if(epret){
                let bxy = [bx, by];
                zini = GenerateHelicalRetarder(Lret, Kret, zini, dzbase, z, bxy);
            }
            else{
                zini = GenerateMPField(1, luretr, Kret, zini, dzbase, true, z, bx, by, null);
            }
        }
        let nums = z.length-secno.length;
        for(let i = 0; i < nums; i++){
            secno.push(m);
        }
    }

    z.push(zini); bx.push(0); by.push(0); secno.push(M-1);
    let outobj = {
        Output:{dimension:1, titles:["z", "Bx", "By"], 
        units:["m", "T", "T", "-"], data:[z, bx, by]}
    };
    /*
    if(issecno){
        outobj.Output.titles.push("Section");
        outobj.Output.units.push("-");
        data.Output.units.push(secno);
    }*/
    let outres = JSON.stringify(outobj);
    GUIConf.postprocessor.SetImportFiles([{name:"field4sc3.json"}]);
    GUIConf.postprocessor.LoadOutputFile(outres); 
}

function CreateMenuItems()
{
    let data = "";
    for(let n = 0; n < GUIConf.allmenus.length; n++){
        data += n.toString()+"\t"+GUIConf.allmenus[n]+"\n";
    }
    let blob = new Blob([data], {type:"text/plain"});
    let link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = "calc_types.txt";
    link.click();
    link.remove();
}

//-------------------------
// utility functions to generate header file
//-------------------------
const MapCont = "map<string, tuple<int, string>>";
const MapLabel = "const map<string, tuple<int, string>> ";

const SrcTypeLabel = {
    LIN_UND: LIN_UND_Label,
    VERTICAL_UND: VERTICAL_UND_Label,
    HELICAL_UND: HELICAL_UND_Label,
    ELLIPTIC_UND: ELLIPTIC_UND_Label,
    FIGURE8_UND: FIGURE8_UND_Label,
    VFIGURE8_UND: VFIGURE8_UND_Label,
    MULTI_HARM_UND: MULTI_HARM_UND_Label,
    BM: BM_Label,
    WIGGLER: WIGGLER_Label,
    EMPW: EMPW_Label,
    WLEN_SHIFTER: WLEN_SHIFTER_Label,
    FIELDMAP3D: FIELDMAP3D_Label,
    CUSTOM_PERIODIC: CUSTOM_PERIODIC_Label,
    CUSTOM: CUSTOM_Label
};

function FormatCSVString(strobj, crnum, is4enum)
{
    let nitems = 0;
    let ist = 0, bef, aft;
    let ex = /"/g;

    while(true){
        ist = strobj.indexOf(", ", ist);
        if(ist == -1){
            break;
        }
        ist++;

        let target = strobj.substring(0, ist-1);
        let nquat = target.match(ex);
        if(nquat != null){
            if(nquat.length%2 > 0){
                continue;
            };
        }

        nitems++;
        if(nitems%crnum == 0){
            bef = strobj.slice(0, ist-1);
            aft = strobj.slice(ist-1);
            if(is4enum){
                strobj = bef+aft.replace(", ", ",\n\t\t");
                ist +=2 ;    
            }
            else{
                strobj = bef+aft.replace(", ", ",\n\t");
                ist++;    
            }
        }
    }
    return is4enum ? "\t"+strobj : "{\n\t"+strobj+"\n};\n";
}

function FormatCppVector(type)
{
    return "const vector<"+type+"> ";
}

function FormatCppVectorDouble(type)
{
    return "const vector<vector<"+type+">> ";
}

function FormatTuple(label, index, fmt)
{
    return '{"'+label+'", '+"tuple<int, string> ("+index+', "'+fmt+'")}';
}

function FormatConst(labelobj, prefix = "")
{
    let data = "";
    for(let i = 0; i < labelobj.length; i++){
        let keys = Object.keys(labelobj[i]);
        data += prefix+"const string "+keys[0]+" = "+'"'+labelobj[i][keys[0]]+'"'+";\n"
    }
    return data;
}

function FormatMaterials(materials)
{
    let data = "";
    let keys = Object.keys(materials);
    for(let i = 0; i < keys.length; i++){
        data += '\t{"'+keys[i]+'", tuple<double, vector<double>> ('+ 
            materials[keys[i]].dens+", {";
        for(let j = 0; j < materials[keys[i]].comp.length; j++){
            if(j > 0){
                data += ", "
            }
            data += materials[keys[i]].comp[j][0]+", "
                +materials[keys[i]].comp[j][1];
        }
        data += "})}";
        if(i < keys.length-1){
            data += ",\n"
        }
    }
    return data;
}

function GenerateHeaderFile()
{
    let data = "";
    data += "// ---------------------------------------------------\n";
    data += "// automatically generated by SPECTRA GUI, do not edit\n";
    data += "// ---------------------------------------------------\n\n";
    data += "#ifndef spectra_input_h\n#define spectra_input_h\n\n";
    data += "#include <string>\n";
    data += "#include <map>\n";
    data += "#include <tuple>\n";
    data += "#include <vector>\n";
    data += "using namespace std;\n\n";

    let scanprms = 4;
    // ScanPrmsLabel.initial, ScanPrmsLabel.final, ScanPrmsLabel.points/ScanPrmsLabel.interv, ScanPrmsLabel.iniser

    let constlabels = [
        {AccLabel:AccLabel}, 
        {SrcLabel:SrcLabel}, 
        {ConfigLabel:ConfigLabel},
        {SimplifiedLabel:SimplifiedLabel},
        {FMaterialLabel:FMaterialLabel},
        {InputLabel:InputLabel},
        {OutputLabel:OutputLabel},
        {OutFileLabel:OutFileLabel},
        {Link2DLabel:Link2DLabel},
        {TypeLabel:TypeLabel},
        {ScanLabel:ScanLabel},
        {BundleScanlabel:BundleScanlabel},
        {OrgTypeLabel:OrgTypeLabel},
        {NumberLabel:NumberLabel},
        {IntegerLabel:IntegerLabel},
        {DataLabel:DataLabel},
        {GridLabel:GridLabel},
        {BoolLabel:BoolLabel},
        {StringLabel:StringLabel},
        {SelectionLabel:SelectionLabel},
        {ArrayLabel:ArrayLabel},
        {TimeLabel:TimeLabel},
        {NormCurrLabel:NormCurrLabel},
        {BeamCurrLabel:BeamCurrLabel},
        {EdevLabel:EdevLabel},
        {ZLabel:ZLabel},
        {BxLabel:BxLabel},
        {ByLabel:ByLabel},
        {GapLabel:GapLabel},
        {EnergyLabel:EnergyLabel},
        {TransmLabel:TransmLabel},
        {PPBetaLabel:PPBetaLabel},
        {PPFDlabel:PPFDlabel},
        {PP1stIntLabel:PP1stIntLabel},
        {PP2ndIntLabel:PP2ndIntLabel},
        {PPPhaseErrLabel:PPPhaseErrLabel},
        {PPRedFlux:PPRedFlux},
        {PPTransLabel:PPTransLabel},
        {PPAbsLabel:PPAbsLabel},
        {ScanPrmItems:scanprms.toString()},
        {CalcStatusLabel:CalcStatusLabel},
        {Fin1ScanLabel:Fin1ScanLabel},
        {ScanOutLabel:ScanOutLabel},
        {ErrorLabel:ErrorLabel},
        {WarningLabel:WarningLabel},
        {DataDimLabel:DataDimLabel},
        {DataTitlesLabel:DataTitlesLabel},
        {UnitsLabel:UnitsLabel},
        {VariablesLabel:VariablesLabel},
        {DetailsLabel:DetailsLabel},
        {RelateDataLabel:RelateDataLabel},
        {ElapsedTimeLabel:ElapsedTimeLabel},
        {CMDResultLabel:CMDResultLabel},
        {CMDModalFluxLabel:CMDModalFluxLabel},
        {CMDFieldLabel:CMDFieldLabel},
        {CMDIntensityLabel:CMDIntensityLabel},
        {CMDCompareIntLabel:CMDCompareIntLabel},
        {CMDCompareXLabel:CMDCompareXLabel},
        {CMDCompareYLabel:CMDCompareYLabel},
        {CMDErrorLabel:CMDErrorLabel},
        {MaxOrderLabel:MaxOrderLabel},
        {WavelengthLabel:WavelengthLabel},
        {SrcSizeLabel:SrcSizeLabel},
        {OrderLabel:OrderLabel},
        {AmplitudeReLabel:AmplitudeReLabel},
        {AmplitudeImLabel:AmplitudeImLabel},
        {AmplitudeVReLabel:AmplitudeVReLabel},
        {AmplitudeVImLabel:AmplitudeVImLabel},
        {AmplitudeIndexReLabel:AmplitudeIndexReLabel},
        {AmplitudeIndexImLabel:AmplitudeIndexImLabel},        
        {NormFactorLabel:NormFactorLabel},
        {FluxCMDLabel:FluxCMDLabel},
        {MatrixErrLabel:MatrixErrLabel},
        {FluxErrLabel:FluxErrLabel},
        {WignerErrLabel:WignerErrLabel},
        {FELCurrProfile:FELCurrProfile},
        {FELEtProfile:FELEtProfile},
        {FELCurrProfileR56:FELCurrProfileR56},
        {FELEtProfileR56:FELEtProfileR56},
        {FELBunchFactor:FELBunchFactor},
        {FELPulseEnergy:FELPulseEnergy},
        {FELEfield:FELEfield},
        {FELInstPower:FELInstPower},
        {FELSpectrum:FELSpectrum},
        {FELSecIdxLabel:FELSecIdxLabel},
        {AccuracyLabel:AccuracyLabel},
        {PartConfLabel:PartConfLabel},
        {SeedWavelLabel:SeedWavelLabel},
        {SeedFluxLabel:SeedFluxLabel},
        {SeedPhaseLabel:SeedPhaseLabel},
        {SProfLabel:SProfLabel},
        {AProfLabel:AProfLabel},
        {BeamSizeLabel:BeamSizeLabel},
        {OptAProfLabel:OptAProfLabel},
        {WignerLabel:WignerLabel},
        {OptWignerLabel:OptWignerLabel},
        {WignerLabelx:WignerLabelx},
        {WignerLabely:WignerLabely},
        {CSDLabel:CSDLabel},
        {CSDLabelx:CSDLabelx},
        {CSDLabely:CSDLabely},
        {DegCohLabel:DegCohLabel},
        {DegCohLabelx:DegCohLabelx},
        {DegCohLabely:DegCohLabely},
        {WigXLabel:WigXLabel},
        {WigXpLabel:WigXpLabel},
        {WigYLabel:WigYLabel},
        {WigYpLabel:WigYpLabel},
        {PrePLabel:PrePLabel},
        {UnitMeter:UnitMeter},
        {UnitMiliMeter:UnitMiliMeter},
        {UnitRad:UnitRad},
        {UnitMiliRad:UnitMiliRad},
        {UnitSec:UnitSec},
        {UnitpSec:UnitpSec},
        {UnitfSec:UnitfSec},
        {UnitGeV:UnitGeV},
        {UnitMeV:UnitMeV},
        {UnitGamma:UnitGamma}
    ];

    data += "// labels for parameters and data import\n"
            +FormatConst(constlabels)+"\n";

    const AccTypeLabel = {
        RING: RINGLabel,
        LINAC: LINACLabel
    };
            
    let acctypelabels = [];
    let acckeys = Object.keys(AccTypeLabel);
    for(let i = 0; i < acckeys.length; i++){
        let obj = {};
        obj[acckeys[i]] = AccTypeLabel[acckeys[i]];
        acctypelabels.push(obj);
    }
    data += "// labels for Accelerator types\n"
            +FormatConst(acctypelabels)+"\n";
            
    let idtypelabels = [];
    let idkeys = Object.keys(SrcTypeLabel);
    for(let i = 0; i < idkeys.length; i++){
        let obj = {};
        obj[idkeys[i]] = SrcTypeLabel[idkeys[i]];
        idtypelabels.push(obj);
    }
    data += "// labels for ID types\n"
            +FormatConst(idtypelabels)+"\n";

    let selections = [
        {AutomaticLabel:AutomaticLabel}, 
        {DefaultLabel:DefaultLabel},
        {NoneLabel:NoneLabel}, 
        {GaussianLabel:GaussianLabel}, 
        {CustomParticle:CustomParticle}, 
        {CustomCurrent:CustomCurrent}, 
        {CustomEt:CustomEt}, 
        {CustomLabel:CustomLabel}, 
        {EntranceLabel:EntranceLabel}, 
        {CenterLabel:CenterLabel}, 
        {ExitLabel:ExitLabel}, 
        {BxOnlyLabel:BxOnlyLabel}, 
        {ByOnlyLabel:ByOnlyLabel}, 
        {BothLabel:BothLabel}, 
        {IdenticalLabel:IdenticalLabel}, 
        {ImpGapTableLabel:ImpGapTableLabel}, 
        {SwapBxyLabel:SwapBxyLabel}, 
        {FlipBxLabel:FlipBxLabel}, 
        {FlipByLabel:FlipByLabel},
        {AntiSymmLabel:AntiSymmLabel},
        {SymmLabel:SymmLabel},
        {FixedSlitLabel:FixedSlitLabel}, 
        {NormSlitLabel:NormSlitLabel}, 
        {GenFilterLabel:GenFilterLabel}, 
        {BPFGaussianLabel:BPFGaussianLabel}, 
        {BPFBoxCarLabel:BPFBoxCarLabel}, 
        {LinearLabel:LinearLabel}, 
        {LogLabel:LogLabel}, 
        {ArbPositionsLabel:ArbPositionsLabel},
        {ObsPointDist:ObsPointDist},
        {ObsPointAngle:ObsPointAngle},
        {OutFormat:OutFormat},
        {JSONOnly:JSONOnly},
        {ASCIIOnly:ASCIIOnly},
        {BothFormat:BothFormat},
        {BinaryOnly:BinaryOnly},
        {XOnly:XOnly},
        {YOnly:YOnly},
        {FELPrebunchedLabel:FELPrebunchedLabel},
        {FELSeedLabel:FELSeedLabel},
        {FELSeedCustomLabel:FELSeedCustomLabel},
        {FELCPSeedLabel:FELCPSeedLabel},
        {FELDblSeedLabel:FELDblSeedLabel},
        {FELReuseLabel:FELReuseLabel},
        {PhaseErrZPole:PhaseErrZPole},
        {PhaseErrZPos:PhaseErrZPos},
        {SingleLabel:SingleLabel},
        {DoubleLabel:DoubleLabel},
        {ThinLensLabel:ThinLensLabel}
    ];
    data += "// labels for selections\n"
        +FormatConst(selections)+"\n";

    let calclabels = {}
    Object.keys(CalcLabels).forEach(type => {
        Object.assign(calclabels, CalcLabels[type]);
    });
    let menuitems = [];
    let menukeys = Object.keys(calclabels);
    for(let i = 0; i < menukeys.length; i++){
        let obj = {};
        obj[menukeys[i]] = calclabels[menukeys[i]];
        menuitems.push(obj);
    }
    data += "// Menu items\nnamespace menu {\n"
            +FormatConst(menuitems, "\t")+"}\n\n";

    data += "// Built-in Filter Materials\n"
            +"const map<string, tuple<double, vector<double>>> FilterMaterials {\n"
            +FormatMaterials(FilterMaterial)+"\n};\n\n"            

    let crnumv = 8, crnums = 4;
    let update = [];
    for(let j = 0; j < UpdateScans.length; j++){
        update.push("\""+UpdateScans[j]+"\"");
    }
    data += "// labels to force update for scan option\n";
    data += FormatCppVector("string")+" UpdateScans "+FormatCSVString(update.join(", "), crnumv, false)+"\n"

    let hdrorg = [
        {enum:[], str:[], strsimp:[], def:[]}, // 0: number
        {enum:[], str:[], strsimp:[], def:[]}, // 1: vector
        {enum:[], str:[], strsimp:[], def:[]}, // 2: boolean
        {enum:[], str:[], strsimp:[], def:[], select:[]}, // 3: selection
        {enum:[], str:[], strsimp:[], def:[]}, // 4: string
        {enum:[], str:[], strsimp:[]} // 5: plottable data
    ];

    let categsufs = {
        [AccLabel]: ["Acc", AccLabelOrder, AccPrmsLabel],
        [SrcLabel]: ["Src", SrcLabelOrder, SrcPrmsLabel],
        [ConfigLabel]: ["Conf", ConfigLabelOrder, ConfigPrmsLabel],
        [OutFileLabel]: ["Outfile", OutputOptionsOrder, OutputOptionsLabel],
        [AccuracyLabel]: ["Accuracy", AccuracyOptionsOrder, AccuracyOptionsLabel],
        [PartConfLabel]: ["PartFormat", ParticleConfigOrder, ParticleConfigLabel],
        [PrePLabel]: ["Preproc", PreProcessPrmOrder, PreProcessPrmLabel]
    };
    let keys = Object.keys(categsufs);

    let suf = ["Prm", "Vec", "Bool", "Sel", "Str", "Data"];
    let ctypes = ["double", "vector<double>", "bool", "string", "string", ""];
    // length of suf & ctypes should be the same

    let simplel = "Simple"
    let headers;
    let defvalues = {};
    let maplabels = [], mapsimples = [];
    for(let n = 0; n < keys.length; n++){
        headers =  CopyJSON(hdrorg);

        DumpObjHeaderOption(categsufs[keys[n]], GUIConf.default[keys[n]], headers);
        headers = ConcatHeaderObjs(suf, ctypes, categsufs[keys[n]][0], simplel, headers, crnumv, crnums, defvalues);
        data += "// "+keys[n]+"\n";
        data += headers+"\n";

        maplabels.push(categsufs[keys[n]][0]);
        mapsimples.push(categsufs[keys[n]][0]+simplel);
    }

    data = data.replaceAll("null", "0");

    data += "// import data format\n";
    data += ExportAsciiFormat();

    let enumkeys = [], keystrs = [];
    for(let j = 0; j < keys.length; j++){
        enumkeys.push(categsufs[keys[j]][0]+"_");
        keystrs.push("\""+keys[j]+"\"");
    }
    enumkeys[0] += " = 0";
    enumkeys.push("Categories");

    data += "// parameter categories\n";
    data += "enum CategoryOrder "+FormatCSVString(enumkeys.join(", "), crnumv, false)+"\n"

    data += FormatCppVector("string")+" CategoryNames "+FormatCSVString(keystrs.join(", "), crnumv, false)+"\n"

    data += FormatCppVector(MapCont)+" ParameterFullNames "+FormatCSVString(maplabels.join(", "), crnumv, false)+"\n";
    data += FormatCppVector(MapCont)+" ParameterSimples "+FormatCSVString(mapsimples.join(", "), crnumv, false)+"\n";

    let defaults = new Array(suf.length);
    for(let n = 0; n < suf.length; n++){
        if(ctypes[n] == ""){
            continue;
        }
        defaults[n] = FormatCppVectorDouble(ctypes[n])+" Default"+suf[n]+" "+FormatCSVString(defvalues[suf[n]].join(", "), crnumv, false);
    } 
    data += defaults.join("\n");

    data += ExportObsoleteLabels(crnums);

    data += "const int JSONIndent = "+JSONIndent+";\n\n";
    
    data += "#endif"

    let blob = new Blob([data], {type:"text/plain"});
    let link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = "spectra_input.h";
    link.click();
    link.remove();
}

function ExportObsoleteLabels(crnum)
{
    let labels = Array.from(PrmTableKeys);
    labels.push(OptionLabel);

    let obslabels = [];
    labels.forEach(prm => {
        obslabels.push('"'+prm+'"');
    });

    let data = FormatCppVector("string")+"ObsoleteLabels "
        +FormatCSVString(obslabels.join(", "), crnum)+"\n"

    return data;
}

function ExportAsciiFormat()
{
    let labels = [
        [CustomCurrent, "currdata"],
        [CustomEt, "Etdata"],
        [CustomField, "fvsz"],
        [CustomPeriod, "fvsz1per"],
        [ImportGapField, "gaptbl"],
        [CustomFilter, "fcustom"],
        [CustomDepth, "depthdata"],
        [SeedSpectrum, "seedspec"]
    ];
    let objs = [[], []];
    for(let i = 0; i < labels.length; i++){
        for(let j = 0; j < labels[i].length; j++){
            let tplc = '{"'+labels[i][j]+'"'+", tuple<int, vector<string>> ("+AsciiFormats[labels[i][0]].dim;
            let strbr = JSON.stringify(AsciiFormats[labels[i][0]].titles);
            let tmp = strbr.replace("[", "").replace("]", "");
            tplc += ", {"+tmp+"})}";
            objs[j].push(tplc);    
        }
    }
    let data = "const map<string, tuple<int, vector<string>>> DataFormat {\n\t"+objs[0].join(",\n\t")+"\n};\n\n";
    data += "const map<string, tuple<int, vector<string>>> DataFormatSimple {\n\t"+objs[1].join(",\n\t")+"\n};\n\n";
    return data;
}

function DumpObjHeaderOption(categobjs, obj, hdrdata)
{
    let categ = categobjs[0];
    let orders = categobjs[1];
    let labels = categobjs[2];

    let hdridx, isstr, fmt;
    for(let i = 0; i < orders.length; i++){
        isstr = false;
        if(orders[i] == SeparatorLabel){
            continue;
        }
        let label = labels[orders[i]][1];
        if(label == SimpleLabel){
            continue;
        }
        else if(label == null){
            continue;
        }
        else if(Array.isArray(label)){
            if(label[0] == null){
                continue;
            }
        }
        if(label == PlotObjLabel){
            hdridx = 5; // data
            fmt = DataLabel;
        }
        else if(label == GridLabel){
            hdridx = 5; // data
            fmt = GridLabel;
        }
        else if(Array.isArray(label)){
            if(labels[orders[i]].length > 2 && labels[orders[i]][2] == SelectionLabel){
                hdridx = 3; // selection
                let brac = [];
                for(let j = 0; j < label.length; j++){
                    brac.push('"'+label[j]+'"');
                }
                hdrdata[hdridx].select.push(brac);
                isstr = true;
                fmt = SelectionLabel;    
            }
            else{
                hdridx = 1; // vertor
                fmt = ArrayLabel;
            }
        }
        else if(typeof label == "boolean"){
            hdridx = 2; // boolean
            fmt = BoolLabel;
        }
        else{
            if(typeof obj[label] == "object"){
                console.log("Invalid format for "+labels[orders[i]][0]);
                continue;
            }
            if(typeof label == "number"){
                hdridx = 0; // number
                fmt = NumberLabel;
            }
            else{
                hdridx = 4; // string
                fmt = StringLabel;
                isstr = true;
            }
        }
        let prmname = orders[i];
        if(prmname == "type"){
            prmname = categ+prmname;
        }
        hdrdata[hdridx].enum.push(prmname+"_");
        hdrdata[hdridx].str.push(FormatTuple(labels[orders[i]][0], prmname+"_", fmt));
        hdrdata[hdridx].strsimp.push(FormatTuple(prmname, prmname+"_", fmt));

        if(label == FileLabel 
                || label == FolderLabel){
            hdrdata[hdridx].def.push('""');
        }
        else if(hdridx != 5){
            if(isstr){
                hdrdata[hdridx].def.push('"'+obj[labels[orders[i]][0]].toString()+'"');
            }
            else if(fmt == ArrayLabel){
                hdrdata[hdridx].def.push(obj[labels[orders[i]][0]]);
            }
            else{
                hdrdata[hdridx].def.push(obj[labels[orders[i]][0]].toString());
            }
        }
    }
}

function ConcatHeaderObjs(suf, ctypes, categ, simplel, hdrdata, crnumv, crnums, defvalues)
{
    let enumcont = [];
    let strcont = [];
    let strsimcont = [];
    let defconts = [];
    let defcont;
    let tmp;

    let label = MapLabel+categ;
    let nlabel = "Num"+categ;
    let deflabel = "Def"+categ;
    let types = [];
    for(let n = 0; n < ctypes.length; n++){
        types.push(FormatCppVector(ctypes[n]));

    }
    let numlabels = [];
    let defs = [];
    for(let i = 0; i < suf.length; i++){
        numlabels.push(nlabel+suf[i]);
        defs.push(types[i]+deflabel+suf[i]+" ");
        if(!defvalues.hasOwnProperty(suf[i])){
            defvalues[suf[i]] = [];
        }
        defvalues[suf[i]].push(deflabel+suf[i]);
    }

    for(let n = 0; n < hdrdata.length; n++){
        if(hdrdata[n].enum.length == 0){
            if(n < 5){
                defconts.push(defs[n]+"{};\n");
            }
            continue;
        }
        hdrdata[n].enum[0] += " = 0";
        hdrdata[n].enum.push(numlabels[n]);

        tmp = hdrdata[n].enum.join(", ");
        enumcont.push(FormatCSVString(tmp, crnumv, true));

        strcont.push(hdrdata[n].str.join(",\n\t"));
        strsimcont.push(hdrdata[n].strsimp.join(",\n\t"));

        if(hdrdata[n].hasOwnProperty("def")){
            let crnum = n == 0 || n == 1 || n == 2 ? crnumv : crnums;
            if(n == 1){
                let tmpbra = [];
                for(let i = 0; i < hdrdata[n].def.length; i++){
                    tmpbra.push("{"+hdrdata[n].def[i][0]+", "+hdrdata[n].def[i][1]+"}");
                }
                tmp = tmpbra.join(", ");
                defcont = defs[n]+FormatCSVString(tmp, crnum*2, false);
            }
            else{
                tmp = hdrdata[n].def.join(", ");
                defcont = defs[n]+FormatCSVString(tmp, crnum, false);
            }
            defconts.push(defcont);
        }
    }

    enumcont = "enum "+categ+"Index {\n"+enumcont.join(",\n")+"\n};\n";

    let strf = label+" {\n\t"+strcont.join(",\n\t")+"\n};\n";
    let strsimf = label+simplel+" {\n\t"+strsimcont.join(",\n\t")+"\n};\n";

    let data = [enumcont, strf, strsimf, defconts.join("\n")];
    return data.join("\n");
}
