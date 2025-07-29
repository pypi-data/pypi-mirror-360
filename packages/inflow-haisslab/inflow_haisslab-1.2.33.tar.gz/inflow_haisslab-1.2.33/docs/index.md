# Inflow 

Is a general purpose python package that regroups various tools (function and classes) to manipulate data.

The rationale between the couple of packages **Inflow** and [**ResearchProjects**](https://haisslab.pages.pasteur.fr/analysis-packages/researchprojects/), is that **all the code that is common to all projects in the team** (reading tiff files, helpers to treat the metadata from the database, dealing with file paths, setting up pipelines...) **should be sitting inside Inflow**, and only such code.

All code that is project specific should be located inside a subpackage of the **ResearchProjects** package. (Sub-packages list can be seen [here](https://gitlab.pasteur.fr/haisslab/analysis-packages/researchprojects/-/tree/main/ResearchProjects) in the form of folders) In Inflow should not belong any code that would have different versions depending on the project it is used for.

This main rule is usefull as functions defined inside Inflow can be used inside ResearchProjects, but not the opposite, to prevent any kind of [circular imports](https://en.wikipedia.org/wiki/Circular_dependency). It also limits code breaking with new updates of the package, because it's easier to maintain backwards compatibility if there is important changes, when you write functions with projects agnosticity in mind in the first place.

<u>For example :</u>

```python 
import Inflow #importing general functions
from ResearchProjects import adaptation #importing project specific functions. 
#Note that this second line internally also imports some tools from Inflow.
#The order of the imports do not matter here. (and should never, if the packages code are correcty written)
```



