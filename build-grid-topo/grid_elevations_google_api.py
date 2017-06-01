'''
- get the elevations for a collection of lat, lon points via Google map API
- in the case of the grid opo, the points are the centroids of grid cells
- input:     - csv w/ required columns lat,lon
- output:    - csv w/ appended column google_alt
'''

import logging
import pandas as pd
import numpy as np
import simplejson, urllib, json
import requests

import matplotlib.pyplot as plt
import matplotlib as mpl

google_elevation_api_key = "AIzaSyDgZ5S0GfXFdZHX7N9C0q2NuphxyWyey-0"
google_base_api_url = "https://maps.googleapis.com/maps/api/elevation/json?locations="
google_locs_req_batch = {}
node_records_google_alts = {}
num_rows_left = 0

def get_google_alt(row):
    
    global google_locs_req_batch
    global node_records_google_alts
    global num_rows_left
    
    lat = row["lat"]
    lon = row["lon"]
    node_label = row["node_label"]
    node_records_google_alts[node_label] = 'NaN'
    
    google_locs_req_batch[node_label] = (lat, lon)
    num_rows_left -= 1
    
    if len(google_locs_req_batch.values()) == 20 or num_rows_left == 0:
        print num_rows_left
        google_api_url = google_base_api_url
        for i, loc in enumerate(google_locs_req_batch.values()):
            if i < len(google_locs_req_batch) - 1:
                google_api_url += str(loc[0]) + ','  + str(loc[1]) + '|'
            else:
                google_api_url += str(loc[0]) + ','  + str(loc[1]) + '&key='+google_elevation_api_key
        
        print google_api_url

        response = requests.get(google_api_url).json()
        
        #print response
        
        for i, (node_label, loc) in enumerate(google_locs_req_batch.iteritems()):
            result  = response['results'][i]
            google_alt = result["elevation"]

            node_records_google_alts[node_label] = google_alt
                                                   
        google_locs_req_batch = {}
            

logging.basicConfig(format='%(message)s', level='INFO')

'''
the logic is a bit convoluted but works as a first pass;
it creates request batches that stay within google api's (free) requests limits
the limits should be sufficient at least for a few dozen thousands of locations
'''

node_records = pd.read_csv('pop_gridded.csv')

num_rows_left = len(node_records.index)

node_records.apply(get_google_alt, axis = 1)

google_alts = []

for node_label in node_records['node_label']:
    google_alts.append(node_records_google_alts[node_label])
        
node_records['google_alt'] = google_alts

node_records.to_csv('pop_gridded_alts.csv')


node_records = pd.read_csv("pop_gridded_alts.csv")


logging.info("Nodes and altitudes saved in pop_gridded_alts.csv")

points = node_records.as_matrix(["lon", "lat", "pop", "google_alt"]) # convert pop to int for dtk demographisc consumption....

# plot filtered grids and their populations
plt.scatter(points[:,0], points[:,1], s = np.sqrt(points[:,2]), c = points[:,3], cmap = 'coolwarm', vmin = 0, vmax = 600, linewidths = 0)
plt.show()
