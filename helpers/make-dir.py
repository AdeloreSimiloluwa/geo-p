import os

base_dir = ""
_chars = [];

for _char in _chars:
	for i in range(1, 5):
		os.mkdir(os.path.join(base_dir, _char+str(i)))

print("done")