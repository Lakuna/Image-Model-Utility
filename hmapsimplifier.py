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

