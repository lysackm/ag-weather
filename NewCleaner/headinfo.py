import csv

# try to guess if a row contains data or column headers
def is_data(row):
	# count how many letters and numbers are in the row
	letters = numbers = 0
	for c in "".join(row):
		if c.isdigit():
			numbers += 1
		if c.isalpha():
			letters += 1
	# if it's mostly numbers, it's a data row
	return numbers > letters

class HeadInfo:
	def __init__(self, path):
		self.num_headers = 0
		self.header = None
		self.pre_header = None
		self.num_columns = None
		
		with open(path, "r", newline="") as f:
			it = csv.reader(f) # iterator over csv rows
			
			# try to get the first row
			try:
				row = next(it)
			except StopIteration:
				# if there's no first row, there's nothing
				return
			
			# if the first row was data, there's no headers
			if is_data(row):
				self.num_columns = len(row)
				return
			
			# if this row isn't the pre-header, the file has a partial header,
			# which will error later, so we can assume this
			self.pre_header = row
			self.num_headers += 1
			
			# try to get the second row, hopefully the header
			try:
				row = next(it)
			except StopIteration:
				# the file either has just a pre-header, or just a
				# regular header. either way, it's an error
				#raise Exception('file has only one header: ' + path)
				self.header = self.pre_header
				self.pre_header = None
				return
			
			# same as above, but the file also has some data in it
			if is_data(row):
				#raise Exception('file has partial header: ' + path)
				self.num_columns = len(row)
				self.header = self.pre_header
				self.pre_header = None
				return
			
			self.header = row
			self.num_headers += 1
			
			# try to get the first row of data
			try:
				row = next(it)
			except StopIteration:
				return
			
			# if the file has three headers, that's very weird
			if not is_data(row):
				raise Exception('file has more than two headers')
			
			self.num_columns = len(row)
