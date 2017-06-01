'''
Assign larval habitats parameters to each nods in a grid topo setup.

The function is a piecewise linear dependence as briefly discussed in vector habitats and population
https://wiki.idmod.org/display/EMOD/2017/02/13/Haiti%3A+gridded+households+topology+analysis

input:     - csv of nodes positions and their elevation w required columns node_label,google_alt,lat,lon  (e.g. pop_gridded_alts.csv); google_alt can easily be changed for different altitude est
output:    - json of nodes to habitats map for each cell in the grid (e.g. grid_habs.json)  
'''

import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt


# would very very likely want to change those
temp_h_zero = 900 # temporary habitat at sea level per 7500
const_h_zero = 3200 # const habitat at sea level per 7500

# this is just an example function; may want to redefine the altitude habitat dependency 
def get_habs_by_alt(alt):
    
    x1 = 0
    y1 = 0
    x2 = 0
    y2 = 0
    
    # very low slope decline with altitude
    if alt >= 0 and alt <= 250:
        x1 = 0
        x2 = 250
        y1 = 1
        y2 = 0.9
    elif alt > 250 and alt <= 400:
        x1 = 201
        x2 = 400
        y1 = 0.9
        y2 = 0.8
    elif alt > 400 and alt <= 500:
        x1 = 301
        x2 = 500
        y1 = 0.8
        y2 = 0.7
    elif alt > 500 and alt <= 600:
        x1 = 401
        x2 = 600
        y1 = 0.7
        y2 = 0.6
    elif alt > 600 and alt < 800:
        x1 = 601
        x2 = 800
        y1 = 0.6
        y2 = 0.5
    else:
        x1 = 801
        x2 = 2000
        y1 = 0.5
        y2 = 0.1
    
    
        
    m = (y2 - y1 + 0.0)/(x2 - x1)
    
    habs = {
                "temp_h" : (m*(alt - x1) + y1)*temp_h_zero,
                "const_h" : (m*(alt - x1) + y1)*const_h_zero
            }
    
    return habs 
    

# nodes altitude incidence altitude category
node_records = pd.read_csv('pop_gridded_alts.csv')

points = node_records.as_matrix(['node_label', 'google_alt', 'lat', 'lon'])


# bounding box for nodes of interest if needed
x_hab_bound_min = -74.0763
x_hab_bound_min = -73.7603
y_hab_bound_max = 18.3072
y_hab_bound_min = 18.0088

gridded_hh_habs = {}

temp_h_vs_alts = []
const_h_vs_alts = []

for point in points:
    
    if not (point[2] > y_hab_bound_min and point[2] < y_hab_bound_min and point[3] > x_hab_bound_min and point[3] < x_hab_bound_max):
        alt = point[1]
        habs = get_habs_by_alt(alt)
        
        temp_h_vs_alts.append([alt, habs["temp_h"]])
        const_h_vs_alts.append([alt, habs["const_h"]])
        
    else:
        habs = {
                "temp_h" : 0.1*temp_h_zero,
                "const_h" : 0.1*const_h_zero
        }
    
    gridded_hh_habs[int(point[0])] = habs
      
temp_h_vs_alts = np.array(sorted(temp_h_vs_alts, key=lambda tup: tup[0]))
const_h_vs_alts = np.array(sorted(const_h_vs_alts, key=lambda tup: tup[0]))

with open("grid_habs.json", "w") as ghh_f:
    json.dump(gridded_hh_habs, ghh_f, indent = 3)

fig = plt.figure(figsize = (13,9)) 
temp_h_plt = plt.plot(temp_h_vs_alts[:,0], temp_h_vs_alts[:,1], label = "Temporary habitat", c = "blue")
const_h_plt = plt.plot(const_h_vs_alts[:,0], const_h_vs_alts[:,1], label = "Constant habitat", c = "red")
plt.xlabel("Elevation [m]")
plt.ylabel("Larval habitat multiplier (prior pop. rescale)")
plt.xlim(min(points[:,1]), max(points[:,1]))
plt.legend()

plt.show()
    
