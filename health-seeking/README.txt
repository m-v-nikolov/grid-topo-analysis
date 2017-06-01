- Collection of scripts building health facility catchment area (HFCA) network and determining health seeking rates across a set of grid cells
- "atypical" Python dependencies:
---- networkx
---- geopy


- Example run generating HFCA network

1) python generate_hfcas.py


- Example run generating HFCA network and corresponding health seeking rates per cell

1) python generate_hfcas.py
2) python generate_health_seeking_rates.py


- Example workflow to generate HFCA network and visualize it

1) python generate_hfcas.py
2) copy hfs_network_node_link.json to ./hfca-viz
3) open hfca_net_viewer.html in ./hfca-viz with Firefox