'''
- estimate density in the area of each point in a collection, using voronoi cells
- can be used to calculate voronoi coefficients of variation to estimate density distribution changes or as in put to density based clustering

- input    - csv w/ required columns lat,lon (e.g. structures_households.csv)  
- output   - csv w/ appended column density (e.g. structures_households_density.csv)
'''

import math
import json
import numpy as np

import pandas as pd

from scipy.spatial import Voronoi, voronoi_plot_2d, Delaunay, ConvexHull 

import matplotlib.pyplot as plt



def PolyArea(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))


if __name__ == '__main__':

        
    node_records = pd.read_csv("structures_households.csv")
    
    points = node_records.as_matrix(["lon", "lat"])
    
    vor = Voronoi(points)
    
    # calculate region density based on voronoi cell size
    # could be useful for clustering based on density
    points_density = []
    
    for ridx in vor.point_region:
        if -1 in vor.regions[ridx]: # exclude infinite regions
            points_density.append(0.0)
            continue
        else:
            polygon = vor.vertices[vor.regions[ridx]]
            area = PolyArea(polygon[:,0], polygon[:,1])
            points_density.append(math.log10(1/(area + 0.0))) # notice the log factor
    
    # store as csv 
    node_records["density"] = points_density
    
    node_records.to_csv("structures_households_density.csv")
    
    voronoi_plot_2d(vor, line_width = 0.1, show_vertices = False, line_alpha = 0.5) 
    plt.show()
    

    # may need to adjust scale depending on density distribution
    plt.scatter(points[:,0], points[:,1], s = 2, c = points_density, cmap = "rainbow", linewidths = 0, vmin = min(points_density), vmax = max(points_density))
    plt.show()
