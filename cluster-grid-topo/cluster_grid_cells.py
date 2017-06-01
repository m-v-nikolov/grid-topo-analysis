'''
- cluster grid cells based on altitude, household density, geographical distance
- build dendrogram tree (for visualization; can export to networkx graph if needed), in the case of agglomerative clustering
- contains code for clustering based on dbscan as well; agglomerative tends to work better

- input:     - csv with columns node_label,lat,lon,pop,google_alt (e.g. pop_gridded_alts.csv) # could change google_alt easily
- output:    - csv with appended column cluster_label (e.g. grid_cluster_labels.csv)
'''


import math
import json
from collections import defaultdict
import itertools
import logging


import numpy as np
import pandas as pd

from scipy.spatial import Voronoi, voronoi_plot_2d, Delaunay, ConvexHull

from sklearn.neighbors import DistanceMetric
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import DBSCAN, AgglomerativeClustering
from sklearn import metrics
from sklearn.preprocessing import MinMaxScaler
from ete3 import Tree,  NodeStyle, TreeStyle

import matplotlib
import matplotlib.pyplot as plt


def build_Newick_tree(children, n_leaves, X, leaf_labels, spanner):
    """
    get a string version of an agglomerative clustering dendrogram
    """
    return traverse_tree(children, n_leaves, X, leaf_labels, len(children) + n_leaves - 1, spanner)[0]+';'


def traverse_tree(children, n_leaves, X, leaf_labels, nodename, spanner):
  
    node_idx = nodename - n_leaves
    
    if nodename<n_leaves:
        return leaf_labels[node_idx],np.array([X[node_idx]])
    
    else:
        node_children = children[node_idx]
        
        left_branch, left_branch_samples = traverse_tree(children, n_leaves, X, leaf_labels, node_children[0], spanner)
        right_branch, right_branch_samples = traverse_tree(children, n_leaves, X, leaf_labels, node_children[1], spanner)
        
        node = np.vstack((left_branch_samples, right_branch_samples))
        
        left_branch_span = spanner(left_branch_samples)
        right_branch_span = spanner(right_branch_samples)
        
        nodespan = spanner(node)
        
        left_branch_distance = nodespan - left_branch_span
        right_branch_distance = nodespan - right_branch_span
        
        nodename = '({branch0}:{branch0distance},{branch1}:{branch1distance})'.format(branch0 = left_branch, branch0distance = left_branch_distance, branch1 = right_branch, branch1distance = right_branch_distance)
        
        return nodename, node
    


# input:  sklearn cluster model 
def get_cluster_spanner(aggClusterer):
   
    if aggClusterer.linkage == 'ward':
        
        # calculate scale of branches based on distance function (affinity) used in clustering 
        if aggClusterer.affinity == 'euclidean':
            spanner = lambda x: np.log10(max(0.000001, np.sum((x - aggClusterer.pooling_func(x, axis = 0))**2)))
            
    elif aggClusterer.linkage == 'complete':
        
        if aggClusterer.affinity == 'euclidean':
            spanner = lambda x:np.max(np.sum((x[:,None,:]-x[None,:,:])**2,axis = 2))
        
        elif aggClusterer.affinity == 'l1' or aggClusterer.affinity=='manhattan':
            spanner = lambda x:np.max(np.sum(np.abs(x[:,None,:]-x[None,:,:]),axis = 2))
        
        elif aggClusterer.affinity == 'l2':
            spanner = lambda x:np.max(np.sqrt(np.sum((x[:,None,:]-x[None,:,:])**2,axis = 2)))
        
        elif aggClusterer.affinity == 'cosine':
            spanner = lambda x:np.max(np.sum((x[:,None,:]*x[None,:,:]))/(np.sqrt(np.sum(x[:,None,:]*x[:,None,:], axis = 2,keepdims = True))*np.sqrt(np.sum(x[None,:,:]*x[None,:,:], axis = 2, keepdims = True))))
        
        else:
            raise AttributeError('Unknown affinity attribute value {0}.'.format(aggClusterer.affinity))
    
    elif aggClusterer.linkage == 'average':
        
        if aggClusterer.affinity == 'euclidean':
            spanner = lambda x:np.mean(np.sum((x[:,None,:]-x[None,:,:])**2, axis = 2))
            
        elif aggClusterer.affinity == 'l1' or aggClusterer.affinity == 'manhattan':
            spanner = lambda x:np.mean(np.sum(np.abs(x[:,None,:]-x[None,:,:]), axis = 2))
            
        elif aggClusterer.affinity == 'l2':
            spanner = lambda x:np.mean(np.sqrt(np.sum((x[:,None,:]-x[None,:,:])**2, axis = 2)))
            
        elif aggClusterer.affinity == 'cosine':
            spanner = lambda x:np.mean(np.sum((x[:,None,:]*x[None,:,:]))/(np.sqrt(np.sum(x[:,None,:]*x[:,None,:], axis = 2, keepdims = True))*np.sqrt(np.sum(x[None,:,:]*x[None,:,:], axis = 2, keepdims = True))))
            
        else:
            raise AttributeError('Unknown affinity attribute value {0}.'.format(aggClusterer.affinity))
        
    else:
        raise AttributeError('Unknown linkage attribute value {0}.'.format(aggClusterer.linkage))
    
    return spanner


# NOTE: the following clustering parameters are just sample values for a small area in Haiti; 
# the output clusters may or may not be reasonable in the context of health seeking behavior for instance;
# the clustering parameters used for Haiti Gand'Anse and sud region are commented below when differing from the sample ones

# construct a unit disk graph with radius max_radius (in km) to provide connectivity structure to agglomerative clustering
# (might want to play with the radius) 
max_radius = 0.1  

# larger areas/smaller cell sizes/larger number of cells might benefit from more clusters
n_clusters = 20  

# produces reasonable clustering for Grand"Anse + Sud region 
# max_radius = 0.05  
# n_clusters = 100


connectivity = "radius_neighbors_graph"
#connectivity = "none"
linkage = "ward"


if __name__ == '__main__':
    
    logging.basicConfig(format='%(message)s', level='INFO')
    
    
    
    cell_records = pd.read_csv("pop_gridded_alts.csv")
    
    points = cell_records.as_matrix(["lon", "lat", "pop", "google_alt"])

    points_scaled = MinMaxScaler().fit_transform(points)
    
   
   
    neighborhoods = NearestNeighbors(radius = max_radius, algorithm = 'auto')
    neighborhoods.fit(points_scaled) 
    
    points_distance_matrix = neighborhoods.radius_neighbors_graph(points_scaled, mode = 'distance') # using Euclidean distance metric for now; may need to convert points to cartesian coordinates  

    logging.info("Calculated neighborhood graph")
    
    
    logging.info("Calculating clusters...")    
    model = AgglomerativeClustering(n_clusters = n_clusters, connectivity = points_distance_matrix, linkage = linkage, compute_full_tree = True).fit(points_scaled)
    #model = AgglomerativeClustering(n_clusters = n_clusters, linkage=linkage).fit(points_scaled) # no connectivity structure imposed


    # add labels to csv 
    cell_records["cluster_label"] = model.labels_

    cell_records.to_csv("grid_cluster_labels.csv")
    
    logging.info("Stored clusters to grid_cluster_labels.csv")

    
    logging.info("Building dendrogram tree...")
    cell_2_cluster_label = cell_records.as_matrix(['node_label', 'cluster_label'])


    # build a dendrogram tree (for visualization)
    spanner = get_cluster_spanner(model)
    newick_tree = build_Newick_tree(model.children_, model.n_leaves_, points_scaled, model.labels_, spanner) # leaf_labels is a list of labels for each entry in X
    tree = Tree(newick_tree)
    ts = TreeStyle()
    
    #ts.rotation = 90
    ts.mode = "c"
    ts.arc_start = -180 # 0 degrees = 3 o'clock
    ts.arc_span = 360
    
    cmap = plt.cm.get_cmap('Spectral')

    for l in tree.iter_leaves():
        label = int(l.name)
        c = matplotlib.colors.rgb2hex(cmap(label/(n_clusters + 0.0))[:3])
                
        style = NodeStyle()
        style["fgcolor"] = c
        style["vt_line_color"] = c
        style["hz_line_color"] = c
        
        l.set_style(style)
        
    tree.show(tree_style = ts)   
    
    
    logging.info("Plotting cells colored by cluster...")
    
    # plot cell colored by their cluster label
    markers_available = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd']
    for i, label in enumerate(model.labels_):
        marker = markers_available[label%len(markers_available)]       
        plt.scatter(points[:, 0][i], points[:, 1][i], c=cmap(label/(n_clusters + 0.0)), marker = marker, linewidths = 0)
        #plt.text(points[:, 0][i], points[:, 1][i], s = str(label))

    plt.show()
    
    points = cell_records.as_matrix(["lon", "lat", "pop", "google_alt", "node_label", "cluster_label"]) # convert pop to int for dtk demographisc consumption....


    # store cell records and cluster labels as json (useful for visualization see README.txt)
    cell_cluster_map = []
    for point in points:
        cell_cluster_map.append({   
                                    "NodeLabel": point[4],
                                    "Latitude": point[1],
                                    "Longitude": point[0],
                                    "Population": point[2],
                                    "ClusterLabel": point[5]
        })

    with open("cell_cluster_map.json", "w") as ccm_f:
        json.dump(cell_cluster_map, ccm_f, indent = 3)
        

    
    # plot filtered grids and their populations
    
    logging.info("Plotting cells colored by elevation...")
    plt.scatter(points[:,0], points[:,1], s = np.sqrt(points[:,2]), c = points[:,3], cmap = 'coolwarm', vmin = 0, vmax = 600, linewidths = 0)
    
    plt.show()
    
    
    '''
    # code below should produce clustering based on the DBSCAN algorithm
    # this is just a reference; there could be errors!
    # DBSCAN doesn't require explicti cluster count as input
    
    #db = DBSCAN(eps=0.0001, min_samples=5, metric = 'precomputed').fit(points_distance_matrix)
    #db = DBSCAN(eps=0.01, min_samples=2, metric = 'euclidean').fit(points)
    
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    
    components = db.components_
    
    #print labels
    
    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    
    print('Estimated number of clusters: %d' % n_clusters_)
    
    
    
    unique_labels = set(labels)
    
    colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    for k, col in zip(unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = 'k'
    
        class_member_mask = (labels == k)
    
        xy = points[class_member_mask & core_samples_mask]
        
        
        if len(xy) > 3:
            hull = ConvexHull(xy)
            plt.plot(xy[hull.vertices,0], xy[hull.vertices,1], 'k-', lw=0.5)
        
       
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
                 markeredgecolor=col, markersize=2)
       
       
        xy = points[class_member_mask & ~core_samples_mask]
        plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
                 markeredgecolor=col, markersize=2)
       
        #plt.scatter(components[:,0], components[:,1], s = 50, c = "red", linewidths = 0)
        
    plt.title('Estimated number of clusters: %d' % n_clusters_)
    plt.show()
    '''
