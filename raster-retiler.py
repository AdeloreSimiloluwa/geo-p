"""
This script retiles a raster into smaller sizes.


The current state of this script is tightly coupled to the assumptions made like the 
(x, y) dimensions for retiling for instance which makes it impossible to scale the use-case for it. 
Further development will involve separation of concerns for all the built-in dependencies and 
inversion of control for script execution.
"""

import os, sys, glob
from osgeo import gdal

cropped_rasters_dir = ""
masks_dir = ""
final_data_path = ""

grid_cell_chars = []
grid_cell_len = 0

project_crs = "EPSG:4326"

tile_size_x = 128
tile_size_y = 128

for year_dir in os.listdir(cropped_rasters_dir):
    for month_dir in os.listdir(os.path.join(cropped_rasters_dir, year_dir)):
        for cell_char in grid_cell_chars:
            for _index in range(1, grid_cell_len+1):
                cell = cell_char + str(_index)
                current_raster_dir = os.path.join(cropped_rasters_dir, year_dir, month_dir)
                raster_paths = glob.glob(os.path.join(current_raster_dir, cell, "*.tif"))
                for raster_path in raster_paths:
                    raster_id = os.path.basename(raster_path)
                    current_mask_dir = os.path.join(masks_dir, year_dir, month_dir)
                    mask_path = os.path.join(current_mask_dir, cell, raster_id.replace(".shp.tif", ".tif"))

                    ds = gdal.Open(raster_path)
                    band = ds.GetRasterBand(1)
                    xsize = band.XSize
                    ysize = band.YSize

                    for i in range(0, xsize, tile_size_x):
                        for j in range(0, ysize, tile_size_y):
                            output_filename = cell+"_"+str(i)+"_"+str(j)+"_"+raster_id
                            data_out_path = os.path.join(final_data_path, year_dir, month_dir, "data/")
                            mask_out_path = os.path.join(final_data_path, year_dir, month_dir, "mask/")
                            gen_raster = "gdal_translate -of GTIFF -srcwin " + str(i)+ ", " + str(j) + ", " + str(tile_size_x) + ", " + str(tile_size_y) + " " + raster_path + " " + str(data_out_path) + str(output_filename)
                            gen_mask = "gdal_translate -of GTIFF -srcwin " + str(i)+ ", " + str(j) + ", " + str(tile_size_x) + ", " + str(tile_size_y) + " " + mask_path + " " + str(mask_out_path) + str(output_filename)

                            os.system(gen_raster)
                            os.system(gen_mask)
                            print (year_dir, month_dir, cell, raster_id)
print("done")