# spectra-ui

spectra-ui is a Python library to interface the synchrotron radiation calculation code SPECTRA.

## Details

For details, visit the [spectra-ui homepage](https://spectrax.org/spectra/app/12.1/python/docs/)

## Installation

Use the package manager to install spectra-ui.

```bash
pip install spectra-ui (--user)
```

## Usage

```python
import spectra

# launch SPECTRA: interactive mode, HTML source in CDN
spectra.Start(mode="i")

# open a parameter file "/path/to/parameter_file"
spectra.Open("/path/to/parameter_file")

# select calculation: Far Field & Ideal Condition::Energy Dependence::Angular Flux Density
spectra.SelectCalculation("far", "energy", "fdensa")

# start calculation: output file will be /path/to/data_dir/sample.json
spectra.StartCalculation(folder="/path/to/data_dir", prefix="sample", serial=-1)

# plot Gaussian-Approximated Brilliance in the Post-Processor
spectra.PostProcess.Plot("GA. Brilliance")

# quit SPECTRA
spectra.Exit()
```

## Requirement
You need to install a web browser (Chrome, Edge, or Firefox; Safari is not upported) to show parameter lists, graphical plots, and calculation progress. 

## License

[MIT](https://choosealicense.com/licenses/mit/)