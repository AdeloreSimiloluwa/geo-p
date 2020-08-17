"""
This script crops a raster to the bounding box of a polygon
It iterates through a directory containing geospatial raster data and clips
them with all polygons in a supplied directory.


The current state of this script is tightly coupled to the assumptions made which makes it
impossible to scale the use-case for it. Further development will involve separation of
concerns for all the built-in dependencies and inversion of control for script execution.
"""

import rasterio
from rasterio import features
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
import json
import geopandas
import os, glob
import pycrs
from shapely.geometry import mapping, Point, Polygon
from shapely.ops import cascaded_union

import numpy as np
import cv2
import matplotlib.pyplot as plt

raster_dir = ""
labels_dir = ""
cell_grids_path = ""
cell_grids_id = ""

cropped_rasters_dir = ""

grid_cell_chars = []
grid_cell_len = 0

project_crs = "EPSG:4326"

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

def check_intersect(raster_file, shape_file):
    import ogr, gdal

    raster = gdal.Open(raster_file)
    vector = ogr.Open(shape_file)

    # Get raster geometry
    transform = raster.GetGeoTransform()
    pixelWidth = transform[1]
    pixelHeight = transform[5]
    cols = raster.RasterXSize
    rows = raster.RasterYSize

    xLeft = transform[0]
    yTop = transform[3]
    xRight = xLeft+cols*pixelWidth
    yBottom = yTop+rows*pixelHeight

    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(xLeft, yTop)
    ring.AddPoint(xLeft, yBottom)
    ring.AddPoint(xRight, yBottom)
    ring.AddPoint(xRight, yTop)
    ring.AddPoint(xLeft, yTop)
    rasterGeometry = ogr.Geometry(ogr.wkbPolygon)
    rasterGeometry.AddGeometry(ring)
    
    # Get vector geometry
    layer = vector.GetLayer()
    feature = layer.GetFeature(0)
    vectorGeometry = feature.GetGeometryRef()
    return rasterGeometry.Intersect(vectorGeometry)

    for year_dir in os.listdir(raster_dir):
    for month_dir in os.listdir(os.path.join(raster_dir, year_dir)):
        data_dir = os.path.join(raster_dir, year_dir, month_dir, "wgs84/")
        raster_files = glob.glob(data_dir+"*.tif")

        for file in raster_files:
            file_name = os.path.basename(file)
            with rasterio.open(file) as src:
                src_meta = src.meta.copy()
                src_affine = src_meta.get("transform")

                for cell_char in grid_cell_chars:
                    for _index in range(1, grid_cell_len+1):
                        cell = cell_char + str(_index)
                        curr_path = os.path.join(labels_dir, cell)
                        labels = glob.glob(os.path.join(curr_path, "*.shp"))
                        if (len(labels) > 0):
                            for label in labels:
                                label_name = os.path.basename(label)
                                label_path = os.path.join(cell_grids_path, cell, cell_grids_id, label_name)
                                label_polygon = geopandas.read_file(label_path)

                                data_intersect = check_intersect(file, label_path)

                                if data_intersect == True:
                                    coords = getFeatures(label_polygon)
                                    out_img, out_transform = mask(src, coords, crop=True)
                                    out_meta = src.meta.copy()
                                    out_meta.update({"driver": "GTiff",
                                      "height": out_img.shape[1],
                                      "width": out_img.shape[2],
                                      "transform": out_transform
                                    })
                                    save_dir = os.path.join(cropped_rasters_dir, year_dir, month_dir)
                                    label_name = label_name.replace(".shp", "")
                                    with rasterio.open(os.path.join(save_dir, cell, label_name+".tif"), "w", **out_meta) as dest:
                                        dest.write(out_img)
                                    print(year_dir, month_dir, file_name, cell)
                       
print("done")
