"use strict";

importScripts("spectra_solver.js");
//importScripts("spectra_solver_debug.js"); // for debugging

function SetOutput(dataname, data)
{
    self.postMessage({data: data, dataname: dataname});
}

Module.onRuntimeInitialized = () => {
    self.addEventListener("message", (msgobj) => {
        try{
            Module.spectra_solver(msgobj.data.serno, msgobj.data.nthread, msgobj.data.data);
            self.postMessage({data: null, dataname: ""});
        }
        catch (e) { // probably memory allocation error
            self.postMessage({data: null, dataname: "Failed to complete the calculation because the memory requirement may be too large. Try with fewer threads."});
        }
        self.close();
    });
    self.postMessage("ready");    
}