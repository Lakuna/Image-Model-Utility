# Heightmap Generator by Travis Martin
import os.path
from PIL import Image

# Vertex object.
class Vertex:
	def __init__(self, x, y, z, identifier):
		if not isinstance(x, float):
			raise TypeError('x must be a float.')
		if not isinstance(y, float):
			raise TypeError('y must be a float.')
		if not isinstance(z, float):
			raise TypeError('z must be a float.')
		if not isinstance(identifier, int):
			raise TypeError('identifier must be an integer.')

		self.x = x # X in Blender.
		self.y = y # Z in Blender (height).
		self.z = z # Y in Blender.
		self.identifier = identifier

	def __str__(self):
		return '(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ') #' + str(self.identifier)

# Face object.
class Face:
	def __init__(self, vertices):
		if not isinstance(vertices, list):
			raise TypeError('vertices must be a list.')
		for vertex in vertices:
			if not isinstance(vertex, Vertex):
				raise TypeError('vertices must contain only Vertices.')

		self.vertices = vertices

	def __str__(self):
		return(
			'Face' +
			'\n\tX range: ' + str(self.minimum_x()) + ' - ' + str(self.maximum_x()) +
			'\n\tZ range: ' + str(self.minimum_z()) + ' - ' + str(self.maximum_z())
		)

	def maximum_x(self):
		value = self.vertices[0].x
		for vertex in self.vertices:
			if vertex.x > value:
				value = vertex.x
		return value

	def minimum_x(self):
		value = self.vertices[0].x
		for vertex in self.vertices:
			if vertex.x < value:
				value = vertex.x
		return value

	def maximum_z(self):
		value = self.vertices[0].z
		for vertex in self.vertices:
			if vertex.z > value:
				value = vertex.z
		return value

	def minimum_z(self):
		value = self.vertices[0].z
		for vertex in self.vertices:
			if vertex.z < value:
				value = vertex.z
		return value

	def height(self):
		total_height = 0
		for vertex in self.vertices:
			total_height += vertex.y
		return total_height / len(self.vertices)

# Dimension object.
class Dimension:
	def __init__(self, label):
		if not isinstance(label, str):
			raise TypeError('label must be a string.')

		self.label = label
		self.unique_values = []
		self.minimum_value = 0
		self.maximum_value = 0

	def __str__(self):
		return(
			'Dimension [' + self.label + ']' +
			'\n\tUnique values: ' + str(len(self.unique_values)) +
			'\n\tMinimum value: ' + str(self.minimum_value) +
			'\n\tMaximum value: ' + str(self.maximum_value) +
			'\n\tSpan: ' + str(self.span())
		)

	def add_value(self, value):
		if not isinstance(value, float):
			raise TypeError('value must be a float.')

		if not value in self.unique_values:
			self.unique_values.append(value)
			if value < self.minimum_value:
				self.minimum_value = value
			if value > self.maximum_value:
				self.maximum_value = value

	def span(self):
		return self.maximum_value - self.minimum_value

# Progess bar. Credit to Benjamin Cordier.
def print_progress_bar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
	percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
	filledLength = int(length * iteration // total)
	bar = fill * filledLength + '-' * (length - filledLength)
	print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
	if iteration == total: 
		print()

# Get model file.
file_path = ""
while True:
	query = input('Map file path: ')
	if not query.endswith('.obj'):
		print('Please specify a .obj file.')
		continue
	if not os.path.isfile(query):
		print('That file does not exist.')
		continue

	file_path = query
	break

# Get image scale information from the user.
hmap_width = 0
while True:
	query = input('Heightmap width: ')
	try:
		hmap_width = int(query)
		break
	except:
		print('Input must represent an integer.')

hmap_height = 0
while True:
	query = input('Heightmap height: ')
	try:
		hmap_height = int(query)
		break
	except:
		print('Input must represent an integer.')

# Get total vertices and faces.
total_vertices = 0
total_faces = 0
try:
	with open(file_path, 'r') as file:
		for line in file:
			if line.startswith('v '):
				total_vertices += 1
			elif line.startswith('f '):
				total_faces += 1
except Exception as error:
	print('Error counting vertices and faces [' + str(error) + '].')

# Get vertices.
vertices = {}
try:
	with open(file_path, 'r') as file:
		i = 0
		for line in file:
			line_parts = line.split()
			
			if line_parts[0] == 'v':
				i += 1
				line_parts.pop(0)
				vertex = Vertex(float(line_parts[0]), float(line_parts[1]), float(line_parts[2]), i)
				vertices[i] = vertex
				print_progress_bar(i, total_vertices, prefix='Vertices:', suffix='Complete', length=50)
except Exception as error:
	print('Error getting map file [' + str(error) + '].')

# Get faces.
faces = []
try:
	with open(file_path, 'r') as file:
		i = 0
		for line in file:
			line_parts = line.split()

			if line_parts[0] == 'f':
				i += 1
				line_parts.pop(0)
				face_vertices = []
				for part in line_parts:
					face_vertex = vertices[int(part.split('/')[0])]
					face_vertices.append(face_vertex)
					if face_vertex == None:
						raise Exception("Vertex not found.")
				face = Face(face_vertices)
				faces.append(face)
				print_progress_bar(i, total_faces, prefix='Faces:', suffix='Complete', length=50)
except Exception as error:
	print('Error getting map file [' + str(error) + '].')

# Create dimensions.
x_dim = Dimension('X')
y_dim = Dimension('Y')
z_dim = Dimension('Z')
i = 0
for vertex in vertices.values():
	i += 1
	x_dim.add_value(float(vertex.x))
	y_dim.add_value(float(vertex.y))
	z_dim.add_value(float(vertex.z))
	print_progress_bar(i, len(vertices), prefix='Dimensions:', suffix='Complete', length=50)
for dim in (x_dim, y_dim, z_dim):
	dim.unique_values.sort()

# Find coordinates to generate pixels from.
x_step = x_dim.span() / hmap_width
z_step = z_dim.span() / hmap_height
x_steps = []
for x in range(hmap_width):
	value = x_dim.minimum_value + (x * x_step)
	x_steps.append(value)
	print_progress_bar(x + 1, hmap_width, prefix='X Steps:', suffix='Complete', length=50)
z_steps = []
for z in range(hmap_height):
	value = z_dim.minimum_value + (z * z_step)
	z_steps.append(value)
	print_progress_bar(z + 1, hmap_height, prefix='Z Steps:', suffix='Complete', length=50)

# Get heights for color values.
y_step = y_dim.span() / 255;
height_to_color = {}
for value in range(256):
	height_to_color[y_dim.minimum_value + (y_step * value)] = value
	print_progress_bar(value, 255, prefix='Coloring:', suffix='Complete', length=50)

# Create image.
image = Image.new("RGB", (hmap_width, hmap_height), '#FF0000')

# Set pixel colors.
pixels = image.load()
progress = 0
progress_max = len(x_steps) * len(z_steps)
x_pixel = -1
for x in x_steps:
	x_pixel += 1
	if x_pixel > hmap_width:
		print('Program attempted to exceed width boundary.')
		break

	z_pixel = -1
	for z in z_steps:
		z_pixel += 1
		if z_pixel > hmap_height:
			print('Program attempted to exceed height boundary.')
			break

		# Search for face that contains the specified coordinates.
		progress += 1
		this_face = None
		for face in faces:
			if face.maximum_x() > x and face.minimum_x() < x and face.maximum_z() > z and face.minimum_z() < z:
				this_face = face
				break
		else:
			# Coordinates aren't covered by a face. Leave default color.
			continue
		this_color = 0
		for height in height_to_color:
			if height >= this_face.height():
				this_color = height_to_color[height]
				break
		# print(str(x_pixel) + " - " + str(z_pixel) + " -- " + str(hmap_width) + " - " + str(hmap_height) + " -- " + str(this_color))
		pixels[x_pixel, z_pixel] = (this_color, this_color, this_color)
		print_progress_bar(progress, progress_max, prefix='Pixellating:', suffix='Complete', length=50)

# Show image for user to save.
image.show()
