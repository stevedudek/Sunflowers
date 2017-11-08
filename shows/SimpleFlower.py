from HelperFunctions import*
from sunflower import NUM_SUNFLOWERS

class SimpleFlower(object):
	def __init__(self, sunflower_model):
		self.name = "SimpleFlower"        
		self.sunflower = sunflower_model
		self.speed = 0.1
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_grade = randint(0,3)
		self.sym = randint(0,6)
		self.size = randint(0,5)
		self.clock = 0
	
	def draw_flower(self):
		for s in range(NUM_SUNFLOWERS):
			for i, p in enumerate(self.sunflower.get_petal_sym(self.sym, self.clock % self.sunflower.num_spirals)):
				color = changeColor(self.color, (((i % 2) * 400) + self.clock + s))
				self.sunflower.set_cells(meld_coords(s, self.sunflower.get_petal_shape(self.size,p)), wheel(color))
				## get_petal_shape() is borked
	def next_frame(self):
		
		while (True):
			
			self.sunflower.black_cells()
			self.draw_flower()

			# Change it up!
			if oneIn(40):
				self.sym = upORdown(self.sym, 1, 2, 5)
			if oneIn(20):
				self.size = upORdown(self.size, 1, 1, 5)
			if oneIn(40):
				self.color_grade = inc(self.color_grade,1,0,8)

			self.color = inc(self.color, -1, 0, MAX_COLOR)
			self.clock += 1

			yield self.speed  	# random time set in init function