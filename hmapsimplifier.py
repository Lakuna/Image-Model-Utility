import os.path
import time
from pathlib import Path
from PIL import Image

# Get heightmap file.
file_path = ""
while True:
	query = input('Heightmap file path: ')
	if not query.endswith('.png'):
		print('Please specify a .png file.')
		continue
	if not os.path.isfile(query):
		print('That file does not exist.')
		continue

	file_path = query
	break

# Get division information from user.
light_point = 0
while True:
	query = input('Light point (exclusive): ')
	try:
		light_point = int(query)
		break
	except:
		print('Input must represent an integer.')
if light_point < 0:
	light_point = 0
if light_point > 256:
	light_point = 256

# Simplify gray pixels in heightmap.
image = Image.open(file_path)
pixels = image.load()
width, height = image.size
for x in range(width):
	for y in range(height):
		r, g, b, a = image.getpixel((x, y))
		if r == g and g == b and a != 0:
			if r > light_point:
				# Light
				pixels[x, y] = (255, 255, 255)
			else:
				# Dark
				pixels[x, y] = (0, 0, 0)
		elif a == 0:
			# Leave transparent pixels as-is.
			pass
		else:
			# Set non-gray pixels to bright red so that they're apparent.
			pixels[x, y] = (255, 0, 0)

# Save image.
output_path = str(Path(__file__).parent.absolute()) + '\\output.png'
image.save(output_path)
