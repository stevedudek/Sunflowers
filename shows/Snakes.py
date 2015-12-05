from HelperFunctions import*
from rose import*

def create_snake_model(rosemodel):
	sm = SnakeModel(rosemodel)
	return sm

class SnakeModel(object):
	def __init__(self, rosemodel):
		# similar to the Rose Model
		# this model contains a dictionary of rose coordinates
		# coordinates are the keys
		# the values are the presence of a snake:
		# 0 = no snake
		# number = snake ID

		self.rose = rosemodel
		self.snakemap = {}	# Dictionary of snake tri

		# Transfer regular trimodel to the snakemmap
		# And clear (set to 0) all of the snake tri

		for coord in self.rose.all_cells():
			self.snakemap[coord] = 0	# No snake

	def get_snake_value(self, coord, default=None):
		"Returns the snake value for a coordinate. Return 'default' if not found"
		return self.snakemap.get(coord, default)

	def put_snake_value(self, coord, snakeID):
		"Puts the snakeID in the snake cell"
		self.snakemap[coord] = snakeID

	def is_open_cell(self, coord):
		"Returns True if the cell is open. Also makes sure tri is on the board"
		return self.rose.cell_exists(coord) and self.get_snake_value(coord) == 0

	def get_valid_directions(self, coord):
		valid = []	# List of valid directions
		for dir in range (0, maxDir):	# Check all six possible directions
			newspot = rose_in_direction(coord, dir, 1)
			if self.is_open_cell(newspot):
				valid.append(dir)
		return valid
	
	def pick_open_cell(self):
		openrose = [coord for coord in self.snakemap if self.is_open_cell(coord)]
		
		if len(openrose) > 0:
			return choice(openrose)
		else:
			 return False	# No cell open!
	
	def remove_snake_path(self, snakeID):
		"In the snake map, changes all tri with snakeID back to 0. Kills the particular snake path"
		for coord in self.snakemap:
			if self.get_snake_value(coord) == snakeID:
				self.put_snake_value(coord, 0)
				## Activate the line below for quite a different effect
				# self.rose.set_cell(coord,[0,0,0]) # Turn path back to black

	def __repr__(self):
		return str(self.lifemap)
        
		
class Snake(object):
	def __init__(self, rosemodel, maincolor, snakeID, startpos):
		self.rose = rosemodel
		self.color = randColorRange(maincolor, 200)
		self.snakeID = snakeID		# Numeric ID
		self.pos = startpos  		# Starting position
		self.dir = randDir()
		self.pathlength = 0
		self.alive = True

	def draw_snake(self):
		self.rose.set_cell(get_coord(self.pos), gradient_wheel(self.color, 1.0 - (self.pathlength/200.0)))
		self.pathlength += 1

	def is_alive(self):
		return self.alive

				
class Snakes(object):
	def __init__(self, rosemodel):
		self.name = "Snakes"        
		self.rose = rosemodel
		self.snakemap = create_snake_model(self.rose)
		self.nextSnakeID = 0
		self.livesnakes = {}	# Dictionary that holds Snake objects. Key is snakeID.
		self.speed = 0.1
		self.maincolor =  randColor()
	
	def count_snakes(self):
		return len([s for s in self.livesnakes.values() if s.is_alive()])

	def next_frame(self):
    	
		self.rose.clear()

		while (True):
			
			# Check how many snakes are in play
			# If no snakes, add one. Otherwise if snakes < 4, add more snakes randomly
			while self.count_snakes() < 3:
				startpos = self.snakemap.pick_open_cell()
				if startpos:	# Found a valid starting position
					self.nextSnakeID += 1
					self.snakemap.put_snake_value(startpos, self.nextSnakeID)
					newsnake = Snake(self.rose, self.maincolor, self.nextSnakeID, startpos)
					self.livesnakes[self.nextSnakeID] = newsnake
				
			for s in self.livesnakes.values():
				if s.alive:
					
					s.draw_snake()	# Draw the snake head
				
					# Try to move the snake
					nextpos = rose_in_direction(s.pos, s.dir, 1)	# Get the coord of where the snake will go
					
					if self.snakemap.is_open_cell(get_coord(nextpos)):	# Is the new spot open?
						s.pos = nextpos		# Yes, update snake position
						self.snakemap.put_snake_value(get_coord(s.pos), s.snakeID)	# Put snake on the virtual snake map
					
					else:
						dirs = self.snakemap.get_valid_directions(get_coord(s.pos))	# Blocked, check possible directions
						if len(dirs) > 0:	# Are there other places to go?
							s.dir = choice(dirs)	# Yes, pick a random new direction
							s.pos = rose_in_direction(s.pos, s.dir, 1)
							self.snakemap.put_snake_value(get_coord(s.pos), s.snakeID)
						else:	# No directions available
							s.alive = False		# Kill the snake
							self.snakemap.remove_snake_path(s.snakeID)	# Snake is killed
				
			yield self.speed  	# random time set in init function