This is a collection of loosely coupled scripts facilitating the generation of grid topologies for EMOD DTK simulations, based on the enumeration of geographical coordinates (e.g. specifying the positions of households, hospitals, etc.).


The scripts are organized in example workflows provided in the documentation of each directory.

The example workflows (e.g. see sims-grid-topo/README.txt) aim at enabling users run spatial malaria simulations on a grid topology of various configurations from scratch.


The workflows enable 
- access to Open Street Maps building structures (e.g. households)
- tesselation/aggregation of structures into a grid, along with creating relevant configurable migration networks
- hierarchical clustering of grid cells according to cells' properties (population density estimate, altitude profile, distance from other cells)
- enabling per-cell heterogeneous health seeking behavior based on cells connectivity and clustering properties
- generation of EMOD-DTK simulation input files (e.g. climate, migration, population based load-balancing) and simulation commissioning to COMPS using dtk-tools, along with the relevant dtk-tools user-space configuration scripts and usage tips


Example workflows assume 
- installed dtk-tools (https://github.com/InstituteforDiseaseModeling/dtk-tools),
- compiled Eradication executable (https://github.com/InstituteforDiseaseModeling/DtkTrunk)
- access to the COMPS environment for running simulations, generating simualtion input files (e.g. climate) 
and storing simulation related input files (e.g. demographics, campaigns)
- related dependencies, as noted in README.txt files in each directory
- currently, excluding the typically required dtk-tools/python dependencies (e.g. pandas, numpy, etc.), these dependencies are 
---- overpass
---- geopy
---- geocoder
---- sklearn
---- scipy
---- urllib
---- requests
---- ete3
---- networkx
- all of the above can be installed via pip 

- Usage/install: clone this repo anywhere locally

- Example workflow (1) in grid-topo-analysis/sims-grid-topo/README.txt should be a good place to start