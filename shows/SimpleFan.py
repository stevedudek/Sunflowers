from HelperFunctions import*
from sunflower import NUM_SUNFLOWERS
	
class SimpleFan(object):
	def __init__(self, sunflower_model):
		self.name = "SimpleFan"        
		self.sunflower = sunflower_model
		self.speed = 0.2 + (randint(0,5) * 0.1)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_grade = randint(10,20)
		self.sym = randint(1,6)
		self.min_size = int(self.sunflower.max_dist / 2)
		self.size = randint(self.min_size, self.sunflower.max_dist)
		self.clock = 0
	
	def draw_flower(self):
		for s in range(NUM_SUNFLOWERS):
			for i, p in enumerate(self.sunflower.get_petal_sym(self.sym + s, self.clock % self.sunflower.num_spirals)):
				color = changeColor(self.color, ((i * 30) + s + self.clock))
				self.sunflower.set_cells(meld_coords(s, self.sunflower.get_fan_shape(self.size, p)), wheel(color))
				## get_fan_shape() is borked

	def next_frame(self):
		
		while (True):
			
			self.sunflower.black_cells()
			self.draw_flower()

			# Change it up!
			if oneIn(40):
				self.sym = upORdown(self.sym, 1, 1, self.sunflower.max_dist)
			if oneIn(4):
				self.size = upORdown(self.size, 1, self.min_size, self.sunflower.max_dist)
			if oneIn(40):
				self.color_grade = inc(self.color_grade,1,10,20)

			self.color = inc(self.color, -1, 0, MAX_COLOR)
			self.clock += 1

			yield self.speed  	# random time set in init function