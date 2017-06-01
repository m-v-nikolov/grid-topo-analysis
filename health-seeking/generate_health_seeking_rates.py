'''
Generate health seeking rates:

Once I picked HF i to visit for my clinical episode treatment (using the health seeking protocol in generate_hfcas.py), I determine the probability with which I will actually access care. 
The probability follows a power law on the Euclidean distance from a source grid cell to HF i. We pick a power law exponent of around 2, 
which has been shown in the past to model well various human and animal exploration activities, and models well the distribution of road lengths in various countries.

input:    - json node_link networkx graph representation (e.g. hfs_network_node_link.json) 
output:   - json health seeking rates to nodes (e.g. hs_rates_2_nodes.json) and nodes to health seeking rates (e.g node_2_hs_rate.json) maps

Note: the parameter values used throughout the script for the example geography/clustering do not necessarily result in the most reasonable health seeking rates  
'''

import pandas as pd
import json
import numpy as np
import random
import os
import math

import matplotlib.pyplot as plt

import networkx as nx
from geopy.distance import vincenty
from networkx.readwrite import json_graph




# load network

with open("hfs_network_node_link.json", "r") as nl_f:
    nodes_to_hfs_network_data = json.load(nl_f)
    
G = json_graph.node_link_graph(nodes_to_hfs_network_data)


print "Loaded HFCA network."
print "Num. nodes " + str(G.number_of_nodes())
print "Num. edges " + str(G.number_of_edges())

nodes = G.nodes()

# map between nodes and aggregate health seeking rates (e.g. health seeking rates over all links to health facilities in the HFCA network)
nodes_2_hs_rates = {}

#HS power law drop off parameters
alpha = 2
d_min = 2.25

# HS rate binning (related to specifying health seeking rates in the DTK...)
bin_size = 0.01

# average health seeking rate over all grid cells
avg_hs_rate = 0.0


pops = nx.get_node_attributes(G, 'population')
xs = nx.get_node_attributes(G, 'lon')
ys = nx.get_node_attributes(G, 'lat')


# group nodes by rates
hs_rate_groups = {}

# calculate health seeking rate for each node based on the HFs in its HFCA graph neighborhood, their link weights and distance
for node in nodes:
    hfs = G.neighbors(node)
    hs_rate = 0.0           
    x = xs[node]
    y = ys[node]
    population = pops[node]
    
    for hf in hfs:
        edge_data = G.get_edge_data(node, hf)
        w = edge_data["weight"]
        sx = edge_data["sx"]
        sy = edge_data["sy"]
        tx = edge_data["tx"]
        ty = edge_data["ty"]

        hf_weight = 0.0
        if len(hfs) == 1: # if the node has only one accessible HF, assume that that people would always pick it
           hf_weight = 1.0
        else:
           hf_weight = w
           
        # calcualte distance between the node and the health facility
        d = vincenty((ys[node], xs[node]), (ys[hf], xs[hf])).km
        
        if hf == 200:
            print node
            print d
            print "======================"
        
        # calculate the health seeking rate from the node to this health facility 
        # based on power law on distance and the weight on the link between the node and the HF 
        fractional_hs_rate = 0.9  
        if d > d_min:
           fractional_hs_rate = ((alpha - 1)/d_min)*math.pow(d/(d_min + 0.0), -alpha)

        fractional_hs_rate = fractional_hs_rate * hf_weight   
    
        # sum over all fractional rates to aggregate the total health seeking rate of people living in this node/cell
        hs_rate += fractional_hs_rate
        
    nodes_2_hs_rates[node] = hs_rate
    
    # round up the hs_rate
    hs_rate = int(hs_rate/bin_size)*bin_size
    
    if hs_rate not in hs_rate_groups:
        hs_rate_groups[hs_rate] = [node]
    else:
        hs_rate_groups[hs_rate].append(node)
            
    avg_hs_rate += hs_rate
    

# calculating average health seeking rate in the area may be useful in case there is field data about that
# the parameters of health seeking rates and the construction of the HFCA network could be adjusted to better match the data
  
print "Average health seeking rate in the area " + str(avg_hs_rate/(len(nodes)))


# cache rates
with open("hs_rates_2_nodes.json", "w") as nhr_f:
    json.dump(hs_rate_groups, nhr_f, indent = 3)

with open("node_2_hs_rate.json", "w") as nhr_f:
    json.dump(nodes_2_hs_rates, nhr_f, indent = 3)


# no need to load every time
with open("node_2_hs_rate.json", "r") as nhr_f:
    nodes_2_hs_rates = json.load(nhr_f)


# plot health seeking rates distribution in the area
for node, rate in nodes_2_hs_rates.iteritems():
      node_label = int(node)
      x = xs[node_label]
      y = ys[node_label]
      population = pops[node_label]
      plt.scatter(x, y, s = np.sqrt(population), c = rate, cmap = 'RdYlGn', vmin = 0, vmax = 1, linewidths = 0)
      #plt.text(x, y, node_label)

plt.colorbar()


hospital_records = pd.read_csv("hospitals_node_labeled.csv")
hospital_points = hospital_records.as_matrix(["lon", "lat", "type", "node_label"])

for point in hospital_points:
    lon =  point[0]
    lat =  point[1]
    type =  point[2] 
    node_label = point[3]


    plt.scatter(xs[node_label], ys[node_label], c='red', s = 70, linewidths = 0.5, marker = 'x') # location of cell containing hospital
    plt.text(xs[node_label], ys[node_label], node_label) # hospital node_label

    plt.scatter(lat, lon, c='red', s = 70, linewidths = 0.5) # actual/OSM hospital location

plt.show() 