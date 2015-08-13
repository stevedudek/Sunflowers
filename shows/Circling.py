from HelperFunctions import*
from rose import*

class Trail(object):
	def __init__(self, rosemodel, color, intense, pos, dir):
		self.rose = rosemodel
		self.pos = pos
		self.color = color
		self.intense = intense
		self.dir = (dir + 2) % 4
	
	def draw_trail(self):
		self.rose.set_cell(get_coord(self.pos), gradient_wheel(self.color, self.intense))
	
	def fade_trail(self):	
		self.pos = rose_in_direction(self.pos, self.dir, 1)
		self.intense *= 0.9
		return self.intense > 0.05		
       		
class Planet(object):
	def __init__(self, rosemodel, pos, color, dir, life):
		self.rose = rosemodel
		self.pos = pos
		self.color = randColorRange(color, 50)
		self.dir = dir
		self.life = life
		self.trails = []	# List that holds trails
		
	def draw_planet(self):
		
		self.fade_trails()
		
		for c in neighbors(get_coord(self.pos)):	
			self.draw_add_trail(self.color, 0.8, c)
		self.draw_add_trail(self.color, 1, self.pos)
	
	def move_planet(self):
		self.pos = rose_in_direction(self.pos, self.dir, 1)
		if oneIn(6):
			self.dir = turn_right(self.dir)
		self.life -= 1
		return self.life > 0
		
	def draw_add_trail(self, color, intense, pos):
		adj_pos = get_coord(pos)
		if self.rose.cell_exists(adj_pos):
			self.rose.set_cell(adj_pos, gradient_wheel(color, intense))
			new_trail = Trail(self.rose, color, intense, pos, self.dir)
			self.trails.append(new_trail)
	
	def fade_trails(self):
		for t in reversed(self.trails):	# Plot last-in first
			t.draw_trail()
			if t.fade_trail() == False:
				self.trails.remove(t)
			
				
class Circling(object):
	def __init__(self, rosemodel):
		self.name = "Circling"        
		self.rose = rosemodel
		self.planets = []	# List that holds Planet objects
		self.speed = 0.05
		self.color = randColor()
		          
	def next_frame(self):
		
		self.rose.clear()
			
		while (True):
			
			if len(self.planets) < 2:
				for p in range(0, maxPetal, 6):
					new_planet = Planet(self.rose, (p,0), self.color, 0, 40)
					self.planets.append(new_planet)
					self.color = changeColor(self.color, -100)

			# Set background to black
			self.rose.set_all_cells((0,0,0))
			
			for p in self.planets:
				p.draw_planet()
				if not p.move_planet():
					self.planets.remove(p)
			
			yield self.speed