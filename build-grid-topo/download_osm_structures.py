"""
- query Open Street Map
- download all available buildings (e.g. households, schools, hospitals, etc.)
within a given (lon, lat) rectangle
- output both csv and json files containing downloaded buildings
see structures_households.json and structures_households.csv for example
"""

import logging

import overpass
import json
import os
import matplotlib.pyplot as plt

log = logging.getLogger(__name__)


properties = dict(hospital='["amenity"]["amenity"~"hospital|pharmacy|doctors"]',
                  school='["amenity"]["amenity"="school"]',
                  building='["building"]["building"!="no"]',
                  )


def query(bbox, feature, properties, mode='skel'):
    """
    :param bbox: bounding box: SWNE
    :param properties: query filter for feature
    :param mode: ids (brief: ids only); skel (concise: ids/children/coordinates); meta (verbose: tags/changes/etc.)
    :param feature: type type of query feature (node, way, rel)
    qt (quadtile) = order for faster results
    center = add center of bounding box
    """
    suffix = '' if feature == 'node' else 'center qt'
    return '%s%s%s;out %s %s;' % (feature, bbox, properties, mode, suffix)


def get_lon_lat(element, type):
    lon, lat = None, None
    location = element.get('center', None) if type == 'way' else element
    try:
        lon, lat = location['lon'], location['lat']
    except (TypeError, KeyError):
        log.debug('Unable to get lat/lon from %s', element)
    return lon, lat


def plot_locations(label, ax, **kwargs):

    for type in ['node', 'way']:
        elements = api.Get(query(bbox, type, properties[label]), responseformat='json')['elements']
        log.info('%s: %d %s', type, len(elements), label)
        lonlats = zip(*[get_lon_lat(e, type) for e in elements])
        if not lonlats:
            lonlats = [], []
        ax.scatter(*lonlats, label=label, **kwargs)
        

def get_locations(label):
    
    locations = {}
    
    for type in ['node', 'way']:    
        locations[type] = api.Get(query(bbox, type, properties[label]), responseformat='json')['elements']
    
    return locations
             

if __name__ == '__main__':

    logging.basicConfig(format='%(message)s', level='INFO')
    output_path = "."
    
    '''
    query OSM for buildings data; need to only do once per data set/area
    '''
    
    #lat lon bounding box fo Grand'anse and Sud in Haiti (change as needed)
    
    x_min = -74.584151
    x_max = -73.784895
    y_min = 18.016106
    y_max = 18.699085
    
    bbox = (y_min, x_min, y_max, x_max)

    logging.info("Downloading data...")
    
    api = overpass.API()
 
    structures = {}
    structures["building"] = get_locations('building') # currently assuming these are mostly households
    #structures["school"] = get_locations('school')
    #structures["hospital"] = get_locations('hospital')
    
    
    # save as json
    with open(os.path.join(output_path, "structures_households.json"), "w") as s_f:
        json.dump(structures, s_f, indent = 3)

    logging.info("Download complete.")

    logging.info("Data saved to structures_households.json")
        
    '''
    can comment the above query code and only work w/ local json once the data is downloaded
    '''
    #with open(os.path.join(output_path, "structures_households.json"), "r") as s_f:
    #    structures = json.load(s_f)
    
    
    # save as csv
    buildings = "id,lat,lon\n"
    for node in structures["building"]["node"]:
        if "lat" in node and "lon" in node:
            buildings += str(node["id"]) + "," # use OSM id; any different unique id would work
            buildings += str(node["lat"]) + ","
            buildings += str(node["lon"]) + "\n" 
            
    
    for way in structures["building"]["way"]:
        if "center" in way:
            buildings += str(way["id"]) + ","
            buildings += str(way["center"]["lat"]) + ","
            buildings += str(way["center"]["lon"]) + "\n"
            
        elif "lat" in way and "lon" in way:
            buildings += str(way["id"]) + ","
            buildings += str(way["lat"]) + ","
            buildings += str(way["lon"]) + "\n"            
            
        
    with open(os.path.join(output_path, "structures_households.csv"), "w") as s_f:
        s_f.write(buildings)
    
    logging.info("Data saved to structures_households.csv")

    # plot downloaded locations

    logging.info("Plotting buildings")
    f, ax = plt.subplots(1, 1, figsize=(12, 8), num="Buildings")

    plot_locations('building', ax=ax, color='k', s=0.3, alpha=0.5)
    #plot_locations('school', ax=ax, color='navy', marker='^', s=100)
    #plot_locations('hospital', ax=ax, color='firebrick', marker='+', s=100, lw=4)

    ax.set(xlim=(bbox[1], bbox[3]), ylim=(bbox[0], bbox[2]), aspect='equal')
    f.set_tight_layout(True)
    
    plt.show()
