"""
This script generates a virtual raster (geospatial vrt) from selected bands of a raster
and generates a corresponding bat script to reproject the input raster coordinate to
a different one (a process known as projection warping)

CURRENT STATE
	It accepts the path to
	1. The directory to where the virtual rasters are stored (data_dir).
	   Current assumption is that these files will be provided as year, month
	   subfolders on the filesystem. (dir > year_dir > month_dir > {raster files})
	2. The directory to output the selected bands to that will be used to build the
	   virtual raster (input_dir) (current constraint: directory structure MUST
	   match that of data_dir)
	3. The directory to output the generated virtual rasters to (output_dir) 
	   (current constraint: directory structure MUST match that of data_dir)
	4. The directory to output the projection warping script to.
	5. The bands 2,3 and 4 have been explicitly hardcoded as the selected bands
	6. WGS84 CRS have been explicitly hardcoded as the coordinate system to warp to.

The current state of this script is tightly coupled to the assumptions made which makes it
impossible to scale the use-case for it. Further development will involve separation of
concerns for all the built-in dependencies and inversion of control for script execution.
"""
import os, sys, glob, subprocess
from xml.dom import minidom

data_dir = ""
input_dir = ""
output_dir = ""
warper_dir = ""

file_groups = {}

for year in os.listdir(data_dir):
    year_dir = os.path.join(data_dir, year)
    file_groups[year] = {}
    for month in os.listdir(year_dir):
        file_groups[year][month] = {}
        month_dir = os.path.join(year_dir, mnoth)
        for subdir in os.listdir(month_dir):
            dir = os.listdir(os.path.join(month_dir, subdir))[0]
            try:
                xml_file = os.path.join(month_dir, subdir, dir, 'GRANULE', subdir, "*.xml")
                xml_file = glob.glob(xml_file)[0]
                xml_data = minidom.parse(xml_file)
                epsg = xml_data.getElementsByTagName("HORIZONTAL_CS_CODE")[0].firstChild.nodeValue

                dir = os.path.join(month_dir, subdir, dir, 'GRANULE', subdir, 'IMG_DATA')

                file_group = []

                for file in glob.glob(dir+"/*.jp2"):
                    file_name = os.path.basename(file)
                    band = (((file_name.split("."))[0]).split("_"))
                    band = band[len(band)-1]
                    if band in ['B02', 'B03', 'B04']:
                        file_group.append(file)

                file_groups[year][month][subdir] = {"files":file_group, "epsg":epsg}
            except:
                print(".")
            
print("done")

query = []
query_ext = []
for year,year_data in file_groups.items():
    for month,month_data in year_data.items():
        for key,vals in month_data.items():
            val = vals["files"]
            epsg = vals["epsg"]
            text = val[0]+"/n"+val[1]+"/n"+val[2]
            write_inp_dir = os.path.join(input_dir, year, month)
            write_out_dir = os.path.join(output_dir, year, month)
            file_name = os.path.join(write_inp_dir, key+".txt")
            try:
                if (os.path.isdir(os.path.join(input_dir, year))):
                    if (os.path.isdir(write_inp_dir)):
                        a = 1
                    else:
                        os.mkdir(write_inp_dir)
                        os.mkdir(write_out_dir)
                        os.mkdir(os.path.join(write_out_dir, "wgs84"))
                else:
                    os.mkdir(os.path.join(input_dir, year))
                    os.mkdir(write_inp_dir)
                    os.mkdir(os.path.join(output_dir, year))
                    os.mkdir(write_out_dir)
                    os.mkdir(os.path.join(write_out_dir, "wgs84"))
            except:
                a = 1
                
            fh = open(file_name, "w")
            fh.write(text)
            fh.close()

            out_file = os.path.join(write_out_dir, key+".vrt")
            reprojected_file = os.path.join(write_out_dir, "wgs84", key+".tif")
            query.append("gdalbuildvrt -resolution average -separate -r nearest -input_file_list "+file_name+" "+out_file)
            query_ext.append("gdalwarp -s_srs "+epsg+" -t_srs EPSG:4326 -r near -of GTiff "+out_file+" "+reprojected_file)
print("Done")

for i in range(0, len(query)):
    os.system(query[i])
print("Done")

query_text = "";
for i in query_ext:
    query_text += "CALL "+i+"/n"
    
fh = open(warper_dir, "w")
fh.write(query_text)
fh.close()

print("done")