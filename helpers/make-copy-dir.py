import os

base_dir = ""
copy_dir = ""

_chars = [];

for base_path in os.listdir(copy_dir):
	os.mkdir(os.path.join(base_dir, base_path))
	for path in os.listdir(os.path.join(copy_dir, base_path)):
		os.mkdir(os.path.join(base_dir, base_path, path))
		for _char in _chars:
			for i in range(1, 5):
				os.mkdir(os.path.join(base_dir, base_path, path, _char+str(i)))

print("done")