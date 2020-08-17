"""
This script crops a polygon to the bounding box of another (vector clipping). 
It iterates through a directory containing shapefiles and clips a supplied
shapefile by all polygons in the directory.

CURRENT STATE
	It accepts the path to
	1. The directory to the shapefile (vector dataset) that should be clipped.
	2. The directory to output the smaller shapefiles.

The current state of this script is tightly coupled to the assumptions made which makes it
impossible to scale the use-case for it. Further development will involve separation of
concerns for all the built-in dependencies and inversion of control for script execution.
"""

import os, glob
import matplotlib.pyplot as plt
import geopandas
import json
import fiona
import pandas
from shapely.geometry import shape 

main_polygon_path = ""
cell_grids_path = ""
cell_grids_id = ""

output_path = ""

grid_cell_chars = []
grid_cell_len = 0

project_crs = "EPSG:4326"

#Read data
collection = list(fiona.open(main_polygon_path,'r'))
poly_frame = pandas.DataFrame(collection)

#Check Geometry
def isvalid(geom):
    try:
        shape(geom)
        return 1
    except:
        return 0
    
poly_frame['isvalid'] = poly_frame['geometry'].apply(lambda x: isvalid(x))
poly_frame = poly_frame[poly_frame['isvalid'] == 1]
collection = json.loads(poly_frame.to_json(orient='records'))

#Convert to geodataframe
main_polygons = geopandas.GeoDataFrame.from_features(collection)
main_polygons.crs = project_crs

for cell_char in grid_cell_chars:
    for index in range(1, grid_cell_len+1):
        cell = cell_char + str(index)
        curr_path = os.path.join(cell_grids_path, cell, cell_grids_id)
        os.chdir(curr_path)
        polygons = glob.glob("*.shp")
        
        for polygon_name in polygons:
            polygon_path = os.path.join(curr_path, polygon_name)
            polygon = geopandas.read_file(polygon_path)
            
            polygon.crs = project_crs
            
            try:
                clipped_poly = geopandas.clip(main_polygons, polygon)
                if not clipped_poly.empty:
                    out_path = os.path.join(output_path, cell, polygon_name)
                    clipped_poly.to_file(out_path)
                    print(cell, polygon_name)
                else:
                    a = 1
            except:
                a = 1
        print("Done with "+cell)
    print("\n---\n\n")
print("done")