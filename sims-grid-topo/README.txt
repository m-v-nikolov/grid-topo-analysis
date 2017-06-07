- Collection of scripts related to running a grid topo simulation on COMPS

- "atypical" Python dependencies:
---- dtk-tools 

- other non-python dependencies
---- Eradication.exe

---- We assume you have access to COMPS and have your user directory in COMPS mapped to an accessible location on your machine (e.g. network drive on windows)
---- Refer to README.txt in each directory of grid-topo-analysis for more info on other package dependencies 
---- For more details check out in-code documentation as needed



=====================================================================================================================

- Example workflow (1) to run a spatial gridded topology malaria sim from scratch (using the area around Moron in Haiti's Grand'Anse department as an example area of interest)

--- go to grid-topo-analysis/build-grid-topo 

--- run

python download_osm_structures.py

------ that caches open street map (OSM) household data locally 

--- run

python build_grid_topo.py

------ that tesselates populated Grand'Anse area from OSM in grid cells
------ filters cells based on a population threshold (e.g. cell with population less than some threshold are excluded)
------ produces a grid network topology representing local (e.g. travel by foot based) connectivity over all grid cells

--- run 

python grid_elevations_google_api.py

------ that assigns an elevation to each each grid cell

--- copy pop_gridded_alts.csv and gridded_households_adj_list.json to grid-topo-analysis/sims-grid-topo/input

--- in grid-topo-analysis/sims-grid-topo/input, run

python grid_topo_larval_habitats.py

------ that generates simulation parameters (i.e. larval habitat scaling factors) dependent on the elevation profile of the geography of interest

--- go to dtk-tools source code directory, in it
--- go to dtk/generic/geography.py
--- to the dict geographies add

"Haiti_gridded_households" :     { "Geography": "Haiti/GriddedHouseholds",
                       "Air_Temperature_Filename":   "Hispaniola_30arcsec_air_temperature_daily.bin",
                       "Land_Temperature_Filename":  "Hispaniola_30arcsec_air_temperature_daily.bin",
                       "Rainfall_Filename":          "Hispaniola_30arcsec_rainfall_daily.bin", 
                       "Relative_Humidity_Filename": "Hispaniola_30arcsec_relative_humidity_daily.bin",
                       "Enable_Climate_Stochasticity": 0, 
                       "Enable_Demographics_Other": 0
                     }


------ Note: this way you can create any other geography for which we have available climate, e.g. 

			"SouthZambia_gridded_households" :     { "Geography": "Zambia/GriddedHouseholds",
					                       "Air_Temperature_Filename":   "Zambia_30arcsec_air_temperature_daily.bin",
					                       "Land_Temperature_Filename":  "Zambia_30arcsec_air_temperature_daily.bin",
					                       "Rainfall_Filename":          "Zambia_30arcsec_rainfall_daily.bin", 
					                       "Relative_Humidity_Filename": "Zambia_30arcsec_relative_humidity_daily.bin",
					                       "Enable_Climate_Stochasticity": 0, 
					                       "Enable_Demographics_Other": 0
				                     } 


--- save and go to dtk/vector/study_sites.py
--- add the function (if it hasn't been defined already)

def configure_haiti_gridded_households(cb):
    set_larval_habitat( cb, {
                             "albimanus":{"TEMPORARY_RAINFALL": 1e7,"CONSTANT": 1e6}
                             })


------- Note: this way you can add any other study site's specific species information; a bit more complex example involving multi-species and multiple habitat types for a Zambian setting:

		
			def configure_southzambia_gridded_households(cb):
			    set_larval_habitat( cb, {
                        		     "arabiensis": {'TEMPORARY_RAINFALL': 1e8, 'CONSTANT': 2e6},
		                             "funestus": {
                	                         "WATER_VEGETATION": 2e7, 
                        	                 "LINEAR_SPLINE": {
                                	                "Capacity_Distribution_Per_Year": {
                                        	        "Times":  [0.0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167, 334.583],
                                                	"Values": [0.0, 0.0, 0.0, 0.0, 0.2, 1.0, 1.0, 1.0, 0.5, 0.2, 0.0, 0.0]
	                                                },
        	                                      "Max_Larval_Capacity": 1e8
                	                          }
                        	    	}
                            })



--- save file


--- in grid-topo-analysis/sims-grid-topo/, run

dtk run haiti_gridded_households_spatial_example.py --hpc


=====================================================================================================================


- Example workflow (2) to run a spatial gridded topology malaria sim from scratch (using the area around Moron in Haiti's Grand'Anse department as an example area of interest);
adding heterogeneous (per-cell) health seeking behavior

--- run example workflow (1) above

--- next, in grid-topo-analysis/build-grid-topo/, run

python download_osm_hospitals.py

--- that caches open street map (OSM) hospital data locally

--- in grid-topo-analysis/build-grid-topo/, run 


python build_grid_topo_w_hospitals.py

------ that tesselates populated Grand'Anse area from OSM in grid cells
------ filters cells based on a population threshold (e.g. cell with population less than some threshold are excluded)
------ produces a grid network topology representing local (e.g. travel by foot based) connectivity over all grid cells
------ places hospitals in cells of the grid
------ notice that due to the addition of health facilities the grid cells set might have changed


--- run

python grid_elevations_google_api.py

------ that assigns an elevation to each each grid cell


--- copy pop_gridded_alts.csv and gridded_households_adj_list.json to grid-topo-analysis/sims-grid-topo/input

--- copy hospitals_node_labeled.csv, pop_gridded_alts.csv in grid-topo-analysis/cluster-grid-topo/


--- in grid-topo-analysis/cluster-grid-topo/ run 

python cluster_grid_cells.py 

------ that generates hierarchical clustering of cells (see README.txt and in-code documentation in grid-topo-analysis/cluster-grid-topo/ for more details)


--- copy grid_cluster_labels.csv from grid-topo-analysis/cluster-grid-topo/ to  grid-topo-analysis/health-seeking/

--- copy gridded_households_adj_list.json and hospitals_node_labeled.csv from grid-topo-analysis/build-grid-topo/ to grid-topo-analysis/health-seeking/


--- in grid-topo-analysis/health-seeking/ run

python generate_hfcas.py

------ that generates health facility catchment area networks placing an edge between each grid cell and health facilities accessible by it; each edge is weighted by a probability indicating preference of individuals in the cell to go to the health facility 


--- in grid-topo-analysis/health-seeking/ run

python generate_health_seeking_rates.py

----- that maps each grid cell to probability that an individual getting sick in that cell would seek care anywhere given the weighted preferences for accessible health facilities and the distance between the cell and the accessible health facilities


--- copy hs_rates_2_nodes.json from grid-topo-analysis/health-seeking/ to grid-topo-analysis/sims-grid-topo/


--- copy Hispaniola_30arcsec_demographics.json from T:\Data_Files\Haiti\GriddedHouseholds\ to grid-topo-analysis/sims-grid-topo/input
(where T:\Data_Files is the folder where your simulation input files are stored from example workflow (1))


--- in grid-topo-analysis/sims-grid-topo/input, run

python generate_grid_map.py

------ that creates a map between node records (altitude, lat, lon, population, node_label) and dtk node ids from a demographics file, used to configure per node/cell health seeking behavior


--- in grid-topo-analysis/sims-grid-topo/input, run

python grid_topo_larval_habitats.py

------ that generates simulation parameters (i.e. larval habitat scaling factors) dependent on the elevation profile of the geography of interest



--- in grid-topo-analysis/sims-grid-topo/, run

dtk run haiti_gridded_households_spatial_example_health_seeking.py --hpc

=====================================================================================================================


- Example workflow (3) to run a spatial gridded topology malaria sim from a csv file cointaining household locations

--- from the household enumeartion csv file, extract a csv with two required columns lat,lon (you could use your original data csv if it has columns lat,lon for each household)

--- name the file structures_households.csv and copy it in grid-topo-analysis/build-grid-topo/

--- run example workflow (1) without the OSM households download step

=====================================================================================================================

- Example workflow (4) to run a spatial gridded topology malaria sim from a csv file containing household locations; assuming no habitat parameter input required

--- from the household enumeration csv file, extract a csv with two required columns lat,lon (you could use your original data csv if it has columns lat,lon for each household; if the file is big it might be better to extract only necessary columns)
--- name the file structures_households.csv and copy it in grid-topo-analysis/build-grid-topo/
--- python build_grid_topo.py

------ that tesselates populated area in grid cells
------ filters cells based on a population threshold (e.g. cell with population less than some threshold are excluded)
------ produces a grid network topology representing local (e.g. travel by foot based) connectivity over all grid cells

--- copy pop_gridded.csv and gridded_households_adj_list.json from grid-topo-analysis/build-grid-topo/ to grid-topo-analysis/sims-grid-topo/input

--- in grid-topo-analysis/sims-grid-topo/, run

dtk run haiti_gridded_households_spatial_example_wo_habs.py --hpc

------ note that the current example setup in haiti_gridded_households_spatial_example_wo_habs.py is for a Haiti topology
------ may need to update geography and site parameters for Zambia grid cell setup 
------ the lines that are relevant for migration haiti_gridded_households_spatial_example_wo_habs.py are  

generate_migration = True, 

------ and

spatial_manager.set_graph_topo_type("small-world-grid")

------ if you don't already have climate files, to generate climate files that are needed for the simulation you can have 

generate_climate = True

------ and uncomment the lines

spatial_manager.set_climate_project_info("IDM-Hispaniola") # setting project name to IDM-Zambia
spatial_manager.set_climate_start_year("2014") # set to whatever year is needed
spatial_manager.set_climate_num_years("1") # set to whatever number is needed

------ In general, the code in dtk-tools that handles migration is in dtk-tools-source-install-path/dtk/tools/migration/MigrationGenerator.py