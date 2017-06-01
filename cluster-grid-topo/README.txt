- Collection of scripts related to clustering a set of points (in the grid topo case the poitns are cell centroids)
- "atypical" Python dependencies:
---- scipy
---- sklearn
---- ete3

- Example run to visualize density distribution of points

1) python voronoi_household_density.py


- Example run to cluster points

1) python cluster_grid_cells.py


- Cluster dendrogram visualization workflow

1) python cluster_grid_cells.py

2) In the ete dendrogram visualization go to the NW button (show newick string representation) and copy the newick tree string

3) Close the ete browser and let the script finish

4) Open haiti_grid_nw.txt in ./map_cluster_dendrogram and replace it's content with copied string newick tree

5) Copy cell_cluster_map.json in cluster-grid-topo/ to ./map_cluster_dendrogram (replacing the file that's there)

6) Open index.html in ./map_cluster_dendrogram in Firefox and click on the big black dot to start exploring cell clustering patterns over the map along the layers of the dendrogram hierarchy tree 