from HelperFunctions import*
from random import choice

def create_snake_model(sunflower_model):
	return SnakeModel(sunflower_model)

class SnakeModel(object):
	def __init__(self, sunflower_model):
		# similar to the Sunflower Model
		# this model contains a dictionary of sunflower coordinates
		# coordinates are the keys
		# the values are the presence of a snake:
		# 0 = no snake
		# number = snake ID

		self.sunflower = sunflower_model
		self.snakemap = {(s,p,d): 0
						 for s in range(self.sunflower.num_sunflowers)
						 for p in range(self.sunflower.get_num_spirals())
						 for d in range(self.sunflower.get_max_dist())}

	def get_snake_value(self, coord):
		"Returns the snake value for a coordinate. Return False if not found"
		return self.snakemap.get(coord, False)

	def put_snake_value(self, coord, snakeID):
		"Puts the snakeID in the snake cell"
		self.snakemap[coord] = snakeID

	def is_open_cell(self, coord):
		"Returns True if the cell is open and valid"
		return coord in self.snakemap and self.get_snake_value(coord) == 0

	def get_valid_directions(self, coord):
		return [dir for dir in range(MAX_DIR) if self.is_open_cell(self.get_petal_next_door(coord, dir))]
	
	def pick_open_cell(self):
		opencells = [coord for coord in self.snakemap if self.is_open_cell(coord)]
		return choice(opencells) if opencells else None
	
	def remove_snake_path(self, snakeID):
		"In the snake map, changes all cells with snakeID back to 0. Kills the particular snake path"
		for coord in self.snakemap:
			if self.get_snake_value(coord) == snakeID:
				self.put_snake_value(coord, 0)
				## Activate the line below for quite a different effect
				self.sunflower.set_cell(coord,[0,0,0]) # Turn path back to black

	def get_petal_next_door(self, coord, dir):
		s,p,d = coord
		new_p, new_d = self.sunflower.petal_nextdoor((p,d), dir)
		return (s, new_p, new_d)

	def __repr__(self):
		return str(self.lifemap)
        
		
class Snake(object):
	def __init__(self, sunflower_model, maincolor, snakeID, startpos):
		self.sunflower = sunflower_model
		self.color = randColorRange(maincolor, 200)
		self.snakeID = snakeID		# Numeric ID
		self.pos = startpos  		# Starting position
		self.dir = randDir()
		self.pathlength = 0
		self.alive = True

	def draw_snake(self):
		self.sunflower.set_cell(self.pos, gradient_wheel(self.color, (100 - self.pathlength) / 100.0))
		self.pathlength += 1

	def is_alive(self):
		return self.alive

	def get_petal_next_door(self, dir):
		s,p,d = self.pos
		new_p, new_d = self.sunflower.petal_nextdoor((p,d), dir)
		return (s, new_p, new_d)

				
class Snakes(object):
	def __init__(self, sunflowermodel):
		self.name = "Snakes"        
		self.sunflower = sunflowermodel
		self.snakemap = create_snake_model(self.sunflower)
		self.nextSnakeID = 0
		self.livesnakes = {}	# Dictionary that holds Snake objects. Key is snakeID.
		self.speed = 0.1
		self.maincolor =  randColor()
	
	def count_snakes(self):
		return len([s for s in self.livesnakes.values() if s.is_alive()])

	def next_frame(self):
    	
		self.sunflower.clear()

		while (True):
			
			# Check how many snakes are in play
			# If no snakes, add one. Otherwise if snakes < 4, add more snakes randomly
			while self.count_snakes() < 3:
				start_pos = self.snakemap.pick_open_cell()
				if start_pos:	# Found a valid starting position
					self.nextSnakeID += 1
					self.snakemap.put_snake_value(start_pos, self.nextSnakeID)
					newsnake = Snake(self.sunflower, self.maincolor, self.nextSnakeID, start_pos)
					self.livesnakes[self.nextSnakeID] = newsnake
				
			for s in self.livesnakes.values():
				if s.alive:
					
					s.draw_snake()	# Draw the snake head
				
					# Try to move the snake
					nextpos = s.get_petal_next_door(s.dir)	# Get the coord of where the snake will go
					
					if self.snakemap.is_open_cell(nextpos):	# Is the new spot open?
						s.pos = nextpos		# Yes, update snake position
						self.snakemap.put_snake_value(nextpos, s.snakeID)	# Put snake on the virtual snake map
					else:
						dirs = self.snakemap.get_valid_directions(s.pos)	# Blocked, check possible directions

						if dirs:	# Are there other places to go?
							s.dir = choice(dirs)	# Yes, pick a random new direction
							s.pos = s.get_petal_next_door(s.dir)
							self.snakemap.put_snake_value(s.pos, s.snakeID)
						else:	# No directions available
							s.alive = False		# Kill the snake
							self.snakemap.remove_snake_path(s.snakeID)	# Snake is killed
				
			yield self.speed