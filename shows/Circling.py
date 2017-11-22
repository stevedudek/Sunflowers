from HelperFunctions import*
from sunflower import*

class Trail(object):
	def __init__(self, sunflower_model, color, intense, s, pos, dir):
		self.sunflower = sunflower_model
		self.s = s
		self.pos = pos
		self.color = color
		self.intense = intense
		self.dir = (dir + 2) % 4
	
	def draw_trail(self):
		self.sunflower.set_cell(meld(self.s, self.pos), gradient_wheel(self.color, self.intense))
	
	def fade_trail(self):	
		self.pos = self.sunflower.petal_in_direction(self.pos, self.dir, 1)
		self.intense -= 0.1
		return self.intense > 0
       		
class Planet(object):
	def __init__(self, sunflower_model, s, pos, color):
		self.sunflower = sunflower_model
		self.s = s
		self.pos = pos
		self.color = randColorRange(color, 50)
		self.dir = randDir()
		self.life = 100
		self.trails = []	# List that holds trails
		self.max_trails = 100
		
	def draw_planet(self):
		self.fade_trails()
		for c in self.sunflower.neighbors(self.pos):
			self.draw_add_trail(self.color, 1, self.s, c)
		self.draw_add_trail(self.color, 1, self.s, self.pos)
	
	def move_planet(self):
		self.pos = self.sunflower.petal_in_direction(self.pos, self.dir, 1)
		if oneIn(4):
			self.dir = turn_right(self.dir)
		self.life -= 1
		return self.life > 0
		
	def draw_add_trail(self, color, intense, s, pos):
		(p,d) = pos
		if self.sunflower.is_on_board((p,d)):
			self.sunflower.set_cell((s,p,d), gradient_wheel(color, intense))
			if len(self.trails) < self.max_trails:
				new_trail = Trail(self.sunflower, color, intense, s, pos, self.dir)
				self.trails.append(new_trail)
	
	def fade_trails(self):
		for t in reversed(self.trails):	# Plot last-in first
			t.draw_trail()
			if t.fade_trail() == False:
				self.trails.remove(t)
			
				
class Circling(object):
	def __init__(self, sunflower_model):
		self.name = "Circling"        
		self.sunflower = sunflower_model
		self.planets = []	# List that holds Planet objects
		self.speed = 0.1
		self.color = randColor()
		          
	def next_frame(self):

		self.sunflower.clear()
			
		while (True):

			if len(self.planets) < 6 and oneIn(20):
				new_planet = Planet(self.sunflower, self.sunflower.rand_sun(), self.sunflower.get_rand_cell(),
									self.color)
				self.planets.append(new_planet)
				self.color = changeColor(self.color, -100)

			for p in self.planets:
				p.draw_planet()
				if not p.move_planet():
					self.planets.remove(p)
			
			yield self.speed