from HelperFunctions import*
from sunflower import NUM_SUNFLOWERS

class Flower(object):
	def __init__(self, sunflower_model):
		self.name = "Flower"        
		self.sunflower = sunflower_model
		self.speed = randint(1,5) * 0.2
		self.size = self.sunflower.max_dist - 1
		self.color = randColor()
		self.color_inc = randint(100,200)
		self.color_grade = randint(3,8)
		self.syms = [0,0,0,0,0,0]
		self.clock = 0
	
	def draw_rings(self):
		for s in range(NUM_SUNFLOWERS):
			for y in range(self.sunflower.max_dist - 1, 0, -1):
				for x in self.sunflower.get_petal_sym(self.syms[y % len(self.syms)]):
					color = changeColor(self.color, ((y + s + self.clock) % self.color_grade) * self.color_inc)
					intensity = 1.0 - (0.1 * ((y + self.clock) % 4))
					self.sunflower.set_cells(meld_coords(s, self.sunflower.get_petal_shape(y, x + s)), gradient_wheel(color, intensity))

				if oneIn(10):
					self.syms[y % len(self.syms)] = (self.syms[y % len(self.syms)] + 1) % 7

	def next_frame(self):
		"""Set up distances with random symmetries"""
		for i in range(len(self.syms)):
			self.syms[i % len(self.syms)] = randint(0,7)

		while (True):
			
			self.sunflower.black_cells()
			self.draw_rings()

			# Change it up!
			if oneIn(4):
				self.color_inc = inc(self.color_inc,5,100,200)
			if oneIn(40):
				self.color_grade = inc(self.color_grade,1,2,4)

			self.color = inc(self.color, -1, 0, MAX_COLOR)
			self.clock += 1

			yield self.speed  	# random time set in init function