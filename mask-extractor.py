"""
This script extracts raster annotations masks from raster data. It accepts the directories
to vector clipped geospatial data and clipped raster datasets, iterates
through them and generates corresponding raster masks.


The current state of this script is tightly coupled to the assumptions made which makes it
impossible to scale the use-case for it. Further development will involve separation of
concerns for all the built-in dependencies and inversion of control for script execution.
"""

import os, glob

import rasterio
from rasterio.plot import reshape_as_image
import rasterio.mask
from rasterio.features import rasterize

import pandas as pd
import geopandas as gpd
from shapely.geometry import mapping, Point, Polygon
from shapely.ops import cascaded_union

import numpy as np
import cv2
import matplotlib.pyplot as plt

labels_dir = ""
cropped_rasters_dir = ""
output_dir = ""

grid_cell_chars = []
grid_cell_len = 0

project_crs = "EPSG:4326"

def perform_masking(src, train_df, out_path):
    def poly_from_utm(polygon, transform):
        poly_pts = []

        poly = cascaded_union(polygon)

        for i in np.array(poly.exterior.coords):

            # Convert polygons to the image CRS
            poly_pts.append(~transform * tuple(i)[:2])

        # Generate a polygon object
        new_poly = Polygon(poly_pts)
        return new_poly

    poly_shp = []
    im_size = (src.meta['height'], src.meta['width'])
    for num, row in train_df.iterrows():
        if row['geometry'].geom_type == 'Polygon':
            poly = poly_from_utm(row['geometry'], src.meta['transform'])
            poly_shp.append(poly)
        else:
            for p in row['geometry']:
                poly = poly_from_utm(p, src.meta['transform'])
                poly_shp.append(poly)


    mask = rasterize(shapes=poly_shp, out_shape=im_size, all_touched=False)

    mask = mask.astype("uint16")

    bin_mask_meta = src.meta.copy()
    bin_mask_meta.update({'count': 1})
    
    with rasterio.open(out_path, 'w', **bin_mask_meta) as dst:
        dst.write(mask * 255, 1)

for year_dir in os.listdir(cropped_rasters_dir):
    for month_dir in os.listdir(os.path.join(cropped_rasters_dir, year_dir)):
        for cell_char in grid_cell_chars:
            for _index in range(1, grid_cell_len+1):
                cell = cell_char + str(_index)
                curr_month_dir = os.path.join(cropped_rasters_dir, year_dir, month_dir)
                raster_paths = glob.glob(os.path.join(curr_month_dir, cell, "*.tif"))
                for raster_path in raster_paths:
                    raster_id = os.path.basename(raster_path)
                    with rasterio.open(raster_path, "r") as src:
                        raster_img = src.read()
                        raster_meta = src.meta

                    raster_id = raster_id.replace(".tif", "")
                    shape_path = os.path.join(labels_dir, cell, raster_id+".shp")
                    train_df = gpd.read_file(shape_path)
                    current_out_dir = os.path.join(output_dir, year_dir, month_dir)
                    out_path = os.path.join(current_out_dir, cell, raster_id.replace(".shp", ".tif"))
                    perform_masking(src, train_df, out_path)
                    print(year_dir, month_dir, cell, raster_id)