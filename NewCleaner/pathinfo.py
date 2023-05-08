import re, os

# unique exception to represent 'something went wrong parsing the path'
class PathException(Exception):
	pass

# Regular expressions are famously hard to understand, but I do genuinely
# think that this is the clearest way to express the path-parsing code.
# My hope is that be being *very* verbose, it will be clear.

# This code uses the @ symbol as the path separator, in order to work on
# different operating systems, which I'll just call 'sep' for brevity

# Also check out the official documentation for this syntax:
# https://docs.python.org/3/library/re.html#regular-expression-syntax
path_regex = r"""
	^             # match from the beginning of the string

	(?P<prefix>   # the prefix is...
		.*        # anything ('.' is any single character, '*' is 'zero or more')
	) @           # then a path separator

	((?P<year>    # then the year is...
		[0-9]{4}  # 4 digits, 0-9 ([0-9] is 'any single digit', {4} is 'exactly 4 times')
	) @)?         # then a path separator, and a ? indicating that the year is optional

	( (?P<folder> # then the folder is...
		[^@]+     # at least one non-path-separator ([^] is 'non-', + is 'at least one')
	) @)?         # then a path separator, and a ? indicating that the folder is optional

	(?P<station>  # then the station is...
		[a-z]+?   # as few letters as possible ([A-Za-z] is a single letter, + is 'at least one', ? is 'as few as possible')
		2?        # an optional 2
		(_|-)?    # an optional _ or - ('|' is 'or')
	)

	(?P<wg>       # the WG is
		(WG)?     # optionally, WG (this is why that 'as few as possible' is needed, without it, the [a-z] will swallow this too)
	)

	(?P<rate>     # the rate is
		15|60|24  # 15, 60, or 24
	)

	(hr|min|m)?   # optionally, some suffix for hours/minutes
	(?P<extension>
		\.txt|\.dat|\.TXT|\.DAT
	) 			  # .txt or .dat (. is any character, so we need a \. to match an actual .)
	$             # match all the way to the end
"""

# The @ isn't really python syntax, we just replace it with the actual
# os.path.sep value.  re.escape is needed because Windows' path separator
# is the backslash, which is also the escape character in regex.
path_regex = path_regex.replace("@", re.escape(os.path.sep))

# we're using a verbose and case insensitive regex
path_regex = re.compile(path_regex, re.VERBOSE | re.IGNORECASE)

class PathInfo:
	"""
	A parsed filepath
	
	Example usage:
	path = Path("data/2013/winter/elmcreek60.txt")
	path.prefix == "data"
	path.year == "2013
	path.folder == "winter"
	path.station == "elmcreek"
	path.wg == ""
	path.rate == 60
	"""
	def __init__(self, path):
		m = path_regex.match(path)
		if m is None:
			raise PathException("Malformed path: " + path)

		# whether or not station is an updated station with data that should be prioritized
		self.updated_station = "2_" in path or "2-" in path

		self.prefix = m.group('prefix')

		# if year folder exists, cast to an int
		self.year = m.group('year')
		if self.year is not None:
			self.year = int(self.year)

		self.folder = m.group('folder')
		self.station = m.group('station')

		# remove any 2s, underscores, hyphens from station name
		self.station = self.station.replace("2", "")
		self.station = self.station.replace("_", "")
		self.station = self.station.replace("-", "")

		# make station name lowercase
		self.station = self.station.lower()

		self.wg = m.group('wg')
		self.rate = int(m.group('rate'))
		self.extension = m.group('extension').lower()
	
	def render(self):
		# if its an updated station, we want to retain that information in render (with "2_")
		updated_status = ""
		if self.updated_station:
			updated_status = "2_"

		return os.path.join(
			self.prefix,
			str(self.year) if self.year is not None else "",
			self.folder if self.folder is not None else "",
			f"{self.station}{updated_status}{self.wg}{self.rate}{self.extension}"
		)
