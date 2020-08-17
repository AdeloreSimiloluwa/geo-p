"""
Most imagery downloads have their entity id's as the folder names. This results 
in a directory path that is too long to work with (on windows especially). 

This script renames all source directories numerically.

"""
import os, sys, glob

data_dir = ""

file_groups = {}

for year in os.listdir(data_dir):
	year_dir = os.path.join(data_dir, year)
	for month in os.listdir(year_dir):
		month_dir = os.path.join(year_dir, month)
		key = 0
		for subdir in os.listdir(month_dir):
		    os.rename(os.path.join(month_dir, subdir), os.path.join(month_dir, str(key)))

		    dir = os.listdir(os.path.join(month_dir, str(key)))[0]
		    os.rename(os.path.join(month_dir, str(key), dir), os.path.join(month_dir, str(key), str(key)))
		    dir = str(key)

		    dir = os.listdir(os.path.join(month_dir, str(key), str(dir), 'GRANULE'))[0]
		    dir = os.path.join(month_dir, str(key), str(key), 'GRANULE', dir)
		    os.rename(dir, os.path.join(month_dir, str(key), str(key), 'GRANULE', str(key)))

		    dir = os.path.join(month_dir, str(key), str(key), 'GRANULE', str(key))

		    print(dir, "\n")

		    key += 1

print("done")