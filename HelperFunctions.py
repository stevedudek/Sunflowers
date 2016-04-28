from random import random, randint, choice
from math import sqrt
import datetime

#
# Constants
#

maxPetal = 24
maxDistance = 6
maxColor = 1536
maxDir = 6
maxRose = 3
NUM_PIXELS = 144

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

# Get a random rose
def randRose():
	return randint(0, maxRose-1)

# Get a random petal
def randPetal():
	return randint(0, maxPetal-1)

# Get a random distance
def randDistance():
	return randint(0, maxDistance-1)

# Get a random cell
def get_rand_cell():
	return (randPetal(),randDistance())

# Get a random direction
def randDir():
	return randint(0, maxDir-1)

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
	return pedal >= 0 and pedal < 24 and distance >= 0 and distance < 6

# get_coord: convert long (>= 6 and < 0) distance coordinates into in_bounds rose coordinates
def get_coord(coord):
	if in_bounds(coord):
		return coord
	else:
		(petal,dist) = coord
		
		while dist >= 11:
			dist -= 11
			petal += 11

		while dist < -11:
			dist += 11
			petal -= 11

		while dist < 0:
			petal -= 11
			# petal -= (6 - dist)
			dist += 11

		if dist >= 6:
			dist = 10 - dist
			petal -= (5 - dist)

		while petal < 0:
			petal += 24

		petal = petal % 24

		return (petal,dist)

# bound_coord: like get_coord, but lets distances go > 5 or < -5
def bound_coord(coord):
	if in_bounds(coord):
		return coord
	else:
		(petal,dist) = coord
		
		if dist < 0 and dist > -6:
			dist += 11
			petal -= (6 - dist)

		while petal < 0:
			petal += 24

		petal = petal % 24

		return (petal,dist)

#
# Directions
#
maxDir = 4

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

#
# Grouping Functions
#

def get_all_radial(dist):
    return [(petal, dist) for petal in range(maxPetal)]

def get_petal_sym(num,offset=0):
	"""Return a symmetric list of petals + offset"""
	sym_type = [1,2,3,4,6,8,12,24]
	sym = sym_type[num % len(sym_type)]
	return [((p+offset+maxPetal) % maxPetal) for p in range(0,24,sym)]

def get_petal_shape(size,offset=0):
	return [((p+offset+maxPetal) % maxPetal, (d+maxDistance) % maxDistance)
		for (p,d) in get_petal_shape_fixed(size)]

def get_petal_shape_fixed(size):
	petals = []
	for x in range(size+1):
		for y in range(size+1):
			petals.append((size-y,x-y))
	return petals

def get_fan_shape(size,offset=0):
	return [(((p+offset+maxPetal) % maxPetal),d) for (p,d) in get_fan_shape_fixed(size)]

def get_fan_shape_fixed(size):
	petals = []
	for p in range(size+1):
		for c in get_fan_band_fixed(p):
			petals.append(c)
	return petals

def get_fan_band(size, offset=0):
	return [(((p+offset) % maxPetal),d) for (p,d) in get_fan_band_fixed(size)]

def get_fan_band_fixed(size):
	petals = []
	for p in range(size+1):
		petals.append((p,size))
	return petals

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

# Increase color by an amount (can be negative)
def changeColor(color, amount):
	return (maxColor + color + amount) % maxColor

# Wrapper for gradient_wheel in which the intensity is 1.0 (full)
def wheel(color):
	return gradient_wheel(color, 1)

# Picks a color in which one rgb channel is off and the other two channels
# revolve around a color wheel
def gradient_wheel(color, intense):
	saturation = datetime.datetime.today().second * 4	# 0 - 240
	color = color % maxColor  # just in case color is out of bounds
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