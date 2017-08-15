from sunflower import NUM_SUNFLOWERS
from HelperFunctions import*
	
class FanSweep(object):
	def __init__(self, sunflower_model):
		self.name = "FanSweep"        
		self.sunflower = sunflower_model
		self.speed = 0.2 + (randint(0,5) * 0.1)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_change = randint(10,200)
		self.sym = randint(1,6)
		self.min_size = int(self.sunflower.max_dist / 2)
		self.size = randint(self.min_size, self.sunflower.max_dist)
		self.clock = 0
	
	def draw_flower(self):
		for s in range(NUM_SUNFLOWERS):
			for p in self.sunflower.get_petal_sym(self.sym, self.clock % self.sunflower.num_spirals):
				self.sunflower.set_cells(meld_coords(s, self.sunflower.get_fan_shape(self.size,p)), wheel(self.color))

	def next_frame(self):
		
		while (True):
			
			# self.sunflower.set_all_cells((0,0,0))
			self.draw_flower()

			# Change it up!
			if oneIn(40):
				self.sym = upORdown(self.sym, 1, 1, 5)
			if oneIn(4):
				self.size = upORdown(self.size, 1, self.min_size, self.sunflower.max_dist)
			if oneIn(20):
				self.color_change = upORdown(self.color_change, 10, 20, 50)

			self.color = changeColor(self.color, self.color_change)
			
			self.clock += 1

			yield self.speed  	# random time set in init function