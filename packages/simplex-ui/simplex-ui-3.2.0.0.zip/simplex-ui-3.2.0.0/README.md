# simplex-ui

simplex-ui is a Python library to interface the FEL simulation code SIMPLEX.

## Details

For details, visit the [simplex-ui homepage](https://spectrax.org/simplex/app/3.2/python/docs/)

## Installation

Use the package manager to install simplex-ui.

```bash
pip install simplex-ui (--user)
```

## Usage

```python
import simplex

# launch SIMPLEX: interactive mode, HTML source in CDN
simplex.Start(mode="i")

# open a parameter file "/path/to/parameter_file"
simplex.Open("/path/to/parameter_file")

# start calculation: output file will be /path/to/data_dir/sample.json
simplex.StartSimulation(folder="/path/to/data_dir", prefix="sample", serial=-1)

# plot gain curve (growth of the pulse energy) in the Post-Processor
simplex.PostProcess.PlotGainCurve("Pulse Energy")

# quit SIMPLEX
simplex.Exit()
```

## Requirement
You need to install a web browser (Chrome, Edge, or Firefox; Safari is not upported) to show parameter lists, graphical plots, and calculation progress. 

## License

[MIT](https://choosealicense.com/licenses/mit/)