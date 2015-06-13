from random import random, randint, choice
from math import sqrt

#
# Constants
#

maxPetal = 24
maxDistance = 6
maxColor = 1536
maxDir = 6
NUM_PIXELS = 144

#
# Common random functions
#

# Random chance. True if 1 in Number
def oneIn(chance):
	if randint(1,chance) == 1:
		return True
	else:
		return False
		
# Get a random direction
def randDir():
	return randint(0,maxDir)

# Return the left direction
def turn_left(dir):
	return (maxDir + dir - 1) % maxDir
	
# Return the right direction
def turn_right(dir):
	return (dir + 1) % maxDir

# Randomly turn left, straight, or right
def turn_left_or_right(dir):
	return (maxDir + dir + randint(-1,1) ) % maxDir

# Shift petals - for interesting effect, shift=5 is the cosine geometry
def shift_petal(p, shift=5):
	return (((p % shift) * shift) + (p / shift)) % 24

# In Bounds: hack for the Hourglass geometry. Creates a fram
def in_bounds(coord):
	(pedal,distance) = coord
	if pedal >= 0 and pedal < 24 and distance >= 0 and distance < 6:
		return True
	else:
		return False

# get_coord: convert long (>= 6 and < 0) distance coordinates into in_bounds rose coordinates
def get_coord(coord):
	if in_bounds(coord):
		return coord
	else:
		(petal,dist) = coord
		
		dist = dist % 144

		while dist >= 11:
			dist -= 11
			petal += 1

		while dist < 0:
			dist += 11
			petal -= 1

		if dist >=6:
			petal -= (dist-5)
			dist = 10 - dist

		while petal < 0:
			petal += 24

		petal = petal % 24

		return (petal,dist)

#
# Grouping Functions
#

def get_all_radial(dist):
    return [(petal, dist) for petal in range(maxPetal)]

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
	return randint(0,maxColor-1)
	
# Returns a random color around a given color within a particular range
# Function is good for selecting blues, for example
def randColorRange(color, window):
	return (maxColor + color + randint(-window,window)) % maxColor

# Wrapper for gradient_wheel in which the intensity is 1.0 (full)
def wheel(color):
	return gradient_wheel(color, 1)

# Picks a color in which one rgb channel is off and the other two channels
# revolve around a color wheel
def gradient_wheel(color, intense):
	color = color % maxColor  # just in case color is out of bounds
	channel = color / 256;
	value = color % 256;

	if channel == 0:
		r = 255
		g = value
		b = 0
	elif channel == 1:
		r = 255 - value
		g = 255
		b = 0
	elif channel == 2:
		r = 0
		g = 255
		b = value
	elif channel == 3:
		r = 0
		g = 255 - value
		b = 255
	elif channel == 4:
		r = value
		g = 0
		b = 255
	else:
		r = 255
		g = 0
		b = 255 - value
	
	return (r*intense, g*intense, b*intense)
	
# Picks a color in which one rgb channel is ON and the other two channels
# revolve around a color wheel
def white_wheel(color, intense):
	color = color % maxColor  # just in case color is out of bounds
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