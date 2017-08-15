from random import randint
from math import sqrt

#
# Constants
#
MAX_COLOR = 1536
MAX_DIR = 4

#
# Common random functions
#

# Random chance. True if 1 in Number
def oneIn(chance):
	return True if randint(1,chance) == 1 else False

# Return either 1 or -1
def plusORminus():
	return (randint(0,1) * 2) - 1

# Increase or Decrease a counter with a range
def upORdown(value, amount, min, max):
	value += (amount * plusORminus())
	return bounds(value, min, max)

# Increase/Decrease a counter within a range
def inc(value, increase, min, max):
	value += increase
	return bounds(value, min, max)

def bounds(value, min, max):
	if value < min:
		value = max
	if value > max:
		value = min
	return value

# Convert s, (p, d) to (s, p, d)
def meld(s, (p, d)):
	return ((s, p, d))

# Convert s, [(p, d)] to [(s, p, d)]
def meld_coords(s, coords):
	return [(s,p,d) for p,d in coords]

#
# Directions
#


# Get a random direction
def randDir():
	return randint(0, MAX_DIR)

# Return the left direction
def turn_left(dir):
	return (MAX_DIR + dir - 1) % MAX_DIR
	
# Return the right direction
def turn_right(dir):
	return (dir + 1) % MAX_DIR

# Randomly turn left, straight, or right
def turn_left_or_right(dir):
	return (MAX_DIR + dir + randint(-1, 1)) % MAX_DIR


#
# Distance Functions
#
def distance(coord1, coord2):
	(x1,y1) = coord1
	(x2,y2) = coord2
	return sqrt( (x2-x1)*(x2-x1) + (y2-y1)*(y2-y1) )

#
# Color Functions
#

# Pick a random color
def randColor():
	return randint(0, MAX_COLOR - 1)
	
# Returns a random color around a given color within a particular range
# Function is good for selecting blues, for example
def randColorRange(color, window):
	return (MAX_COLOR + color + randint(-window, window)) % MAX_COLOR

# Increase color by an amount (can be negative)
def changeColor(color, amount):
	return (MAX_COLOR + color + amount) % MAX_COLOR

# Wrapper for gradient_wheel in which the intensity is 1.0 (full)
def wheel(color):
	return gradient_wheel(color, 1)

# Picks a color in which one rgb channel is off and the other two channels
# revolve around a color wheel
def gradient_wheel(color, intense):
	saturation = 0
	# saturation = sin(3.14 * datetime.datetime.today().second / 60) * 62
	color = color % MAX_COLOR  # just in case color is out of bounds
	channel = color // 256;
	value = color % 256;

	if channel == 0:
		r = 255
		g = value
		b = saturation
	elif channel == 1:
		r = 255 - value
		g = 255
		b = saturation
	elif channel == 2:
		r = saturation
		g = 255
		b = value
	elif channel == 3:
		r = saturation
		g = 255 - value
		b = 255
	elif channel == 4:
		r = value
		g = saturation
		b = 255
	else:
		r = 255
		g = saturation
		b = 255 - value

	return (r*intense, g*intense, b*intense)
	
# Picks a color in which one rgb channel is ON and the other two channels
# revolve around a color wheel
def white_wheel(color, intense):
	color = color % MAX_COLOR  # just in case color is out of bounds
	channel = color / 256;
	value = color % 256;

	if channel == 0:
		r = 255
		g = value
		b = 255 - value
	elif channel == 1:
		r = 255 - value
		g = 255
		b = value
	elif channel == 2:
		r = value
		g = 255 - value
		b = 255
	elif channel == 3:
		r = 255
		g = value
		b = 255 - value
	elif channel == 4:
		r = 255 - value
		g = 255
		b = value
	else:
		r = value
		g = 255 - value
		b = 255
	
	return (r*intense, g*intense, b*intense)