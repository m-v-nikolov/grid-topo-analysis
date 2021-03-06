- Collection of scripts building a grid topology based on a layer of buildings (e.g. Open Street Map households, hospitals, schools)
- "atypical" Python dependencies:
---- overpass
---- geopy
---- geocoder
---- descartes
---- sklearn
---- scipy
---- urllib
---- requests

- Example run generating grid topo:

--- basic grid topo based on households locations

1) python download_osm_structures.py
2) python build_grid_topo.py


--- basic grid topo based on households locations; grid cells/household locations filtered by geojson shapes (e.g. only include grid cells/households whose coordinates are within a set of shapefiles)

1) python download_osm_structures.py
2) python build_grid_topo_filter_by_shape.py


- Example run generating grid topo along with a layer of hospitals (or other structures, e.g. schools, community health workers)

1) python download_osm_structures.py
2) python download_osm_hospitals.py
3) python build_grid_topo_w_hospitals.py

- Example run generating grid topo with a layer of hospitals (or other structures, e.g. schools, community health workers) along with grid cells altitudes

1) python download_osm_structures.py
2) python download_osm_hospitals.py
3) python build_grid_topo_w_hospitals.py
4) python grid_elevations_google_api.py


