import os, glob
import matplotlib.pyplot as plt
import geopandas
import json
import fiona
import pandas
from shapely.geometry import shape

class geo_p:
    def __init__(self, path_dict):
        self.all_paths = path_dict
    
    def poly_clip(self):
        main_polygon_path = self.all_paths['main_polygon_path']
        cell_grids_path = self.all_paths['cell_grids_path']
        cell_grids_id = self.all_paths['cell_grids_id']
        output_path = self.all_paths['output_path']

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