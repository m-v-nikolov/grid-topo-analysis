'''
Create a map between node records (altitude, lat, lon, population, node_label) and dtk node ids from a demographics file
The map is actually an array since other scripts downstream require array input...
'''

import pandas as pd
import json

with open("Hispaniola_30arcsec_demographics.json", "r") as d_f: # change as needed
    demo = json.load(d_f)
    
node_records = pd.read_csv("pop_gridded_alts.csv")

    
node_ids_2_node_labels = {}
node_labels_2_node_ids = {}

    
for node in demo["Nodes"]:
    node_ids_2_node_labels[node["NodeID"]] = node["NodeAttributes"]["FacilityName"]
    node_labels_2_node_ids[node["NodeAttributes"]["FacilityName"]] = node["NodeID"] 


points = node_records.as_matrix(['node_label', 'lat', 'lon', 'pop'])

base_map = []

for point in points:
    
    node_id = int(node_labels_2_node_ids[str(int(point[0]))])
    node_label = point[0]
    lat = point[1]
    lon = point[2]
    pop = point[3]
    
    node = {
            "DtkNodeId":node_id,
            "NodeLabel":str(int(node_label)),
            "Latitude":lat,
            "Longitude":lon,
            "Population":pop
            }
    
    base_map.append(node)
    
with open("grid_map.json", "w") as hhs_f:
    json.dump(base_map, hhs_f, indent = 3)