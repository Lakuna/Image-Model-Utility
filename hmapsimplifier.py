import os.path
import time
from pathlib import Path
from PIL import Image

# Progress bar object.
class ProgressBar:
	fill = '█'
	unfill = '-'

	def __init__(self, total_size, description = '', precision = 1, length = 50):
		if not isinstance(total_size, int):
			raise TypeError('total_size must be an integer.')
		description = str(description)
		if not isinstance(precision, int):
			raise TypeError('precision must be an integer.')
		if not isinstance(length, int):
			raise TypeError('length must be an integer.')

		self.i = 0
		self.total_size = total_size
		self.description = description # Displayed before progress bar.
		self.start_time = time.time() # Time elapsed displays after progress bar.
		self.precision = precision # Number of decimals to display.
		self.length = length # Length of full progress bar.
		self.ended = False # Make sure the bar doesn't spam the console if it goes too long.

	def step(self, amount = 1):
		if not isinstance(amount, int):
			raise TypeError('amount must be an integer.')

		self.i += amount
		self.set_progress(self.i)

	def set_progress(self, progress):
		if not isinstance(progress, int):
			raise TypeError('progress must be an integer.')

		if self.ended:
			return
		self.i = progress
		percent = ("{0:." + str(self.precision) + "f}").format(100 * (self.i / float(self.total_size)))
		time_elapsed = ("{:." + str(self.precision) + "f}s").format(time.time() - self.start_time)
		filledLength = int(self.length * self.i // self.total_size)
		bar = ProgressBar.fill * filledLength + ProgressBar.unfill * (self.length - filledLength)
		print('\r%s |%s| %s%% %s' % (self.description, bar, percent, time_elapsed), end = "\r")
		if self.i >= self.total_size:
			self.end()

	def end(self):
		self.ended = True
		print()

# Log object.
class Log:
	# import time
	# from pathlib import Path
	def __init__(self, path = str(Path(__file__).parent.absolute()), file_name = 'log'):
		path = str(path)
		file_name = str(file_name)

		self.path = path + '\\' + file_name + '.txt'
		self.log = open(self.path, 'w')
		self.start_time = time.time()

	def newline(self):
		self.log.write('\n')

	def write(self, text):
		text = str(text)

		self.log.write('[' + ("{:.1f}s").format(time.time() - self.start_time) + ']\t' + text + '\n')

	def close(self):
		self.log.close()

# Make log file.
log = Log()

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
log.write("PNG file path: " + file_path)

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
log.write("Light point: " + str(light_point))

# Choose logging level.
log_level = 0
while True:
	query = input(
			'Log levels in order of speed:' +
			'\n\t0: Minimal information.\tRecommended' +
			'\n\t1: Progress bars.' +
			'\n\t2: Progress bars and color log information.' +
			'\nLog level: '
	)
	try:
		log_level = int(query)
		break
	except:
		print('Input must represent an integer.')
if log_level < 0:
	log_level = 0
if log_level > 2:
	log_level = 2
log.write('Log level: ' + str(log_level))

# Simplify gray pixels in heightmap.
image = Image.open(file_path)
pixels = image.load()
width, height = image.size
if log_level >= 1:
	progress_bar = ProgressBar(width * height, description = 'Coloring:')
for x in range(width):
	for y in range(height):
		r, g, b, a = image.getpixel((x, y))
		if r == g and g == b:
			if r > light_point:
				# Light
				pixels[x, y] = (255, 255, 255)
				if log_level >= 2:
					log.write('Pixel (' + str(x) + ', ' + str(y) + ') is light.')
			else:
				# Dark
				pixels[x, y] = (0, 0, 0)
				if log_level >= 2:
					log.write('Pixel (' + str(x) + ', ' + str(y) + ') is dark.')
		else:
			if log_level >= 2:
				log.write('Pixel (' + str(x) + ', ' + str(y) + ') is not gray.')
		if log_level >= 1:
			progress_bar.step()

# Save image.
output_path = str(Path(__file__).parent.absolute()) + '\\output.png'
image.save(output_path)
log.newline()
log.write('Simplified heightmap saved to ' + output_path)

# Close log file.
log.write('End of program.')
log.close()
