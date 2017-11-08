from sunflower import NUM_SUNFLOWERS
from HelperFunctions import*
	
class FanPetal(object):
	def __init__(self, sunflower_model):
		self.name = "FanPetal"        
		self.sunflower = sunflower_model
		self.speed = randint(2,10)
		self.color = randColor()
		self.fan_color = randColor()
		self.petal_color = randColor()
		self.fan_sym = randint(1,6)
		self.petal_sym = randint(1,6)
		self.fan_size = randint(0, self.sunflower.max_dist - 1)
		self.petal_size = randint(0, self.sunflower.max_dist - 1)
		self.clock = 0
		self.max_brightness = 1.0
		self.sunflower.set_max_brightness(self.max_brightness)
	
	def draw_fan(self):
		for s in range(NUM_SUNFLOWERS):
			for p in self.sunflower.get_petal_sym(self.fan_sym + s, self.sunflower.num_spirals - 1 - (self.clock % self.sunflower.num_spirals)):
				color = randColorRange(self.fan_color, 30)
				self.sunflower.set_cells(meld_coords(s, self.sunflower.get_fan_shape(self.fan_size, p)), wheel(color))

	def draw_petal(self):
		for s in range(NUM_SUNFLOWERS):
			for p in self.sunflower.get_petal_sym(self.petal_sym + s, self.clock % self.sunflower.num_spirals):
				color = randColorRange(self.petal_color, 30)
				self.sunflower.set_cells(meld_coords(s, self.sunflower.get_petal_shape(self.petal_size, p)), wheel(color))

	def next_frame(self):
		
		while (True):
			
			self.sunflower.black_cells()

			if self.fan_size > self.petal_size:
				self.draw_fan()
				self.draw_petal()
			else:
				self.draw_petal()
				self.draw_fan()

			# Change it up!
			if oneIn(40):
				self.fan_sym = (7 + self.fan_sym ) % 8
			if oneIn(20):
				self.petal_sym = (7 + self.petal_sym ) % 8

			if oneIn(10):
				self.speed = upORdown(self.speed, 0.5, 2, 10)

			if oneIn(20):
				self.fan_size = (self.fan_size + 1) % self.sunflower.max_dist
			if oneIn(30):
				self.petal_size = (self.petal_size + 1) % self.sunflower.max_dist

			self.fan_color = changeColor(self.fan_color, 10)
			self.petal_color = changeColor(self.petal_color, -15)

			self.clock += 1

			yield self.speed / 10.0 	# random time set in init function