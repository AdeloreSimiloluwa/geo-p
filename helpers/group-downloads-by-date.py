"""
This script sorts downloaded satellite imagery into a time series
directory structure by parsing the entity-id of the raw download to 
determine the date of collection.

"""
import os, sys, glob
from dateutil.parser import parse
from datetime import datetime
import shutil

data_dirs = [
    
]
group_output_dir = ""

file_groups = {}

for data_dir in data_dirs:
    for subdir in os.listdir(os.path.join(data_dir)):
        dir_parts = subdir.split("_")
        for part in dir_parts:
            try:
                date = parse(part, fuzzy=False)
                year_dir = os.path.join(group_output_dir, str(date.year))
                month_dir = os.path.join(year_dir, str(date.month))
                
                if (os.path.isdir(year_dir)):
                    if (os.path.isdir(month_dir)):
                        print("-")
                    else:
                        os.mkdir(month_dir)
                else:
                    os.mkdir(year_dir)
                    os.mkdir(month_dir)
                shutil.move(os.path.join(data_dir, subdir), month_dir)
                print(".")
            except:
                continue

print("done")