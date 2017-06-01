import os
import json
import functools as fun
import itertools as it


from simtools.ModBuilder import ModFn, ModBuilder

from simtools.SetupParser import SetupParser


from dtk.generic.migration import single_roundtrip_params
from dtk.vector.study_sites import configure_site
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.tools.spatialworkflow.SpatialManager import SpatialManager
from dtk.utils.builders.sweep import GenericSweepBuilder
from dtk.vector.species import set_larval_habitat
from dtk.interventions.outbreakindividual import recurring_outbreak
from dtk.interventions.health_seeking import add_health_seeking
from dtk.utils.reports.VectorReport import add_human_migration_report

# scale parameters for all nodes in a spatial simulation (there could be a single node in the spatial sim too)
def set_habs_scale(cb, site, geography, value = None):
    
    temp_h = value[0]
    const_h = value[1]
 
    hab = {'albimanus': {'TEMPORARY_RAINFALL': 1e7 * temp_h, 'CONSTANT': 1e6 * const_h}}
    set_larval_habitat(cb, hab)

    return {'temp_h' : temp_h, 'const_h': const_h}


# scale parameters of multiple nodes in a spatial simulation
def apply_pop_scale_larval_habitats(nodes_params_input_file_path, demographics):
    
    with open(nodes_params_input_file_path, 'r') as np_f:
        nodes_params = json.load(np_f)
    
    for node_item in demographics['Nodes']:
        node_label = node_item['NodeAttributes']['FacilityName']

        const_h = nodes_params[node_label]['const_h']
        temp_h = nodes_params[node_label]['temp_h']
    
        calib_single_node_pop = 7500 # change if needed
        
        
        birth_rate = (float(node_item['NodeAttributes']['InitialPopulation'])/(1000 + 0.0))*0.12329
        node_item['NodeAttributes']['BirthRate'] = birth_rate
        pop_multiplier = float(node_item['NodeAttributes']['InitialPopulation'])/(calib_single_node_pop + 0.0)
        
        const_multiplier = const_h*pop_multiplier
        temp_multiplier = temp_h*pop_multiplier
            
        node_item['NodeAttributes']['LarvalHabitatMultiplier'] = {
                                                                          'TEMPORARY_RAINFALL':temp_multiplier,
                                                                          'CONSTANT':const_multiplier,
                                                                      }

    return demographics


location = 'HPC' #'LOCAL'
setup = SetupParser(location) 
geography = 'Haiti/GriddedHouseholds' # notice geography matches one of the haiti geographies in the dict geographies of dtk/generic/geography.py
site = 'Haiti_gridded_households' # notice site matches (all lower case) one of the study sites (i.e. configure_haiti_gridded_households) in dtk/vector/study_sites.py

prefix = "Haiti_Grand_Anse_test"

num_cores = 24

num_years = 0.1 # run for less than 2 months; just a test


builder = ModBuilder.from_combos(
                                    [ModFn(configure_site, site)],
                                    [ModFn(DTKConfigBuilder.set_param, 'x_Local_Migration', h) for h in [1e-1]],
                                    [ModFn(DTKConfigBuilder.set_param, 'Run_Number', r) for r in range(1,2)]
                                )


cb = DTKConfigBuilder.from_defaults('MALARIA_SIM',
                                    Num_Cores=num_cores,
                                    Simulation_Duration=int(365*num_years))

# migration
cb.update_params(single_roundtrip_params)

# set demographics file name
cb.update_params({'Demographics_Filenames':[os.path.join(geography, prefix + "_demographics.json")]})

# modify the config for the geography of interest
cb.update_params({'Geography': geography})


# Spatial simulation + migration settings
cb.update_params({
                # Match demographics file for constant population size (with exponential age distribution)
                'Birth_Rate_Dependence': 'FIXED_BIRTH_RATE', 
                'Enable_Nondisease_Mortality': 1, 
                'New_Diagnostic_Sensitivity': 0.025, # 40/uL
                #'Vector_Sampling_Type': 'SAMPLE_IND_VECTORS', # individual vector model (required for vector migration)
                #'Mosquito_Weight': 10,
                #'Enable_Vector_Migration': 1, # mosquito migration
                #'Enable_Vector_Migration_Local': 1, # migration rate hard-coded in NodeVector::processEmigratingVectors() such that 50% total leave a 1km x 1km square per day (evenly distributed among the eight adjacent grid cells).
                
                'Local_Migration_Filename': os.path.join(geography, prefix + '_migration.bin'), # note that underscore prior 'migration.bin' is required for legacy reasons that need to be refactored...
                'Enable_Local_Migration':1,
                'Migration_Pattern': 'SINGLE_ROUND_TRIPS', # human migration
                'Local_Migration_Roundtrip_Duration': 2, # mean of exponential days-at-destination distribution
                'Local_Migration_Roundtrip_Probability': 0.95, # fraction that return
                #'Migration_Model': 'NO_MIGRATION', # human migration

                'Enable_Spatial_Output': 1, # spatial reporting
                'Spatial_Output_Channels': ['Infectious_Vectors', 'Adult_Vectors', 'New_Infections','Population', 'Prevalence', 'New_Diagnostic_Prevalence', 'Daily_EIR', 'New_Clinical_Cases', 'Human_Infectious_Reservoir', 'Daily_Bites_Per_Human', 'Land_Temperature','Relative_Humidity', 'Rainfall', 'Air_Temperature']
                })

# some default required parameters
cb.update_params({"Vector_Migration_Base_Rate": 0.5,
                  "Default_Geography_Initial_Node_Population": 1000, 
                  "Default_Geography_Torus_Size": 10
                  })

cb.set_param("Enable_Demographics_Builtin", 0)
cb.set_param("Valid_Intervention_States", [])
#cb.set_param("Enable_Memory_Logging", 1)

# multi-core load balance settings
cb.update_params({'Load_Balance_Filename': os.path.join(geography, prefix + '_loadbalance_' +str(num_cores) + 'procs.bin')})
#recurring_outbreak(cb, outbreak_fraction = 0.01, tsteps_btwn=180)
#recurring_outbreak(cb, outbreak_fraction = 0.005, tsteps_btwn=180)



'''
# track migration of people (this can generate really big files by default use with care
cb.update_params({
                  "Report_Event_Recorder": 1,
                  "Listed_Events": ["Immigrating", "Emigrating"],
                  "Report_Event_Recorder_Events":["Immigrating", "Emigrating"],
                  "Report_Event_Recorder_Ignore_Events_In_List" : 0
                  })
'''


'''
# various log levels allowing different levels of output verbsity per class
# to reduce output (and stdout sise) escalate debug level over DEBUG, INFO, WARNING, and ERROR (error resulting in the least output)
# use LogLevel_Memory set to DEBUG to see simulation memory footprint on each core (CPU)


cb.update_params({
                    "logLevel_VectorHabitat": "ERROR",
                    "logLevel_NodeVector": "ERROR",
                    "logLevel_JsonConfigurable": "ERROR",

                    "logLevel_MosquitoRelease": "ERROR",
                    "logLevel_VectorPopulationIndividual": "ERROR",

                    "logLevel_NodeEventContext": "WARNING",  # UnregisterIndividualEventObserver
                    "logLevel_SimulationEventContext": "ERROR",  # Discarding old event for t=...
                    "logLevel_NodeLevelHealthTriggeredIV": "WARNING",  # NLHTI is listenting to ... events
                    "logLevel_StandardEventCoordinator": "WARNING",  # UpdateNodes distributed ... intervention to ...

                    "logLevel_SimulationEventContext": "WARNING",
                    "logLevel_JsonConfigurable": "WARNING",
                    "logLevel_NodeLevelHealthTriggeredIV": "WARNING",
                    "logLevel_Memory": "DEBUG"
                  })
'''


exp_name = prefix + "_base"


# Working directory is current dir for now
working_dir = os.path.abspath('.')
input_path = os.path.join(working_dir,"input")
output_dir = os.path.join(working_dir,"output")
population_input_file = 'pop_gridded_alts.csv' # see format in dtk.tools.spatialworkflow.DemographicsGenerator
nodes_params_input_file = "grid_habs.json"
migration_matrix_input_file = "gridded_households_adj_list.json"


# Create the spatial_manager
spatial_manager = SpatialManager(
                                     location,
                                     cb, 
                                     setup, 
                                     geography, 
                                     exp_name, 
                                     working_dir, 
                                     input_path, 
                                     sim_data_input_root = 'T:\\Data_Files', # assuming the input files will reside on COMPS user's directory (e.g. \\idmppfil01\idm\home\user_name) which is mapped to T as a network drive; change if necessary 
                                     population_input_file = population_input_file,
                                     migration_matrix_input_file = migration_matrix_input_file,  
                                     output_dir = output_dir, 
                                     log = True, 
                                     num_cores = num_cores, 
                                     
                                     update_demographics = fun.partial(apply_pop_scale_larval_habitats, os.path.join(input_path, nodes_params_input_file)),
                                     generate_climate = True,
                                     generate_migration = True,
                                     generate_load_balancing = True,
                                     generate_immune_overlays = False
                                 )




# set demographics parameters
spatial_manager.set_demographics_type("static")
spatial_manager.set_res_in_arcsec("custom")
spatial_manager.set_climate_project_info("IDM-Hispaniola")
spatial_manager.set_climate_start_year("2014")
spatial_manager.set_climate_num_years("1")
spatial_manager.set_graph_topo_type("small-world-grid")

# see spatialworkflow.SpatialManager for other configurable options


spatial_manager.run()

run_sim_args =  {'config_builder': cb,
                 'exp_name': exp_name,
                 'exp_builder': builder}
