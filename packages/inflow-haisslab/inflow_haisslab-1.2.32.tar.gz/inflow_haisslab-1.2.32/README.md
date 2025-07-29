# [Inflow](https://haisslab.pages.pasteur.fr/analysis-packages/Inflow/)
Core package for analysis, and pipelining utilities in the Haiss Lab  
Find the documentation for the functions of this package in a searchable website here : https://haisslab.pages.pasteur.fr/analysis-packages/Inflow/

## Requirements
Inflow requires python 3.7 or later, and is tested on Windows 10.

## Installing
Installing the package via pip typically takes a few seconds.  To install, activate your developpement environment :
```
conda activate <myenvironment>
```
If you don't have an environment or conda installed, [follow these instructions](https://gitlab.pasteur.fr/haisslab/analysis-packages/how-to-start/-/blob/main/README.md)  
Then run the Inflow install using :
```
pip install git+https://gitlab.pasteur.fr/haisslab/analysis-packages/Inflow.git
```

**NB**:  
This package is still under active development, for the best experience please regularly update the package by running :  
```
pip install --force-reinstall --no-deps -U git+https://gitlab.pasteur.fr/haisslab/analysis-packages/Inflow.git
```
For dev environment (expect bugs), use this one :
```
pip install --force-reinstall --no-deps git+https://gitlab.pasteur.fr/haisslab/analysis-packages/Inflow.git@dev
```

This  will force the reinstallation of the package, without the need to do a `pip uninstall Inflow` first, and without reinstalling the dependancies like numpy etc (hence faster).


For **pre-realeases environment** (dev after minimal testing, please don't hesitate to report bugs), use this one :  
```
pip install --force-reinstall --no-deps -U git+https://gitlab.pasteur.fr/haisslab/analysis-packages/Inflow.git@pre-releases
```

## Usage

```python
import Inflow
Inflow.load.tdms("mytdmsfile.tdms").
```

 
