from sunflower import NUM_SUNFLOWERS
from HelperFunctions import*
	
class Fan(object):
	def __init__(self, sunflower_model):
		self.name = "Fan"        
		self.sunflower = sunflower_model
		self.speed = 0.5 + (randint(0,30) * 0.1)
		self.size = 5
		self.color = randColor()
		self.color_inc = randint(200,500)
		self.color_grade = randint(3,8)
		self.syms = [0,0,0,0,0,0]
		self.clock = 0
	
	def draw_rings(self):
		for s in range(NUM_SUNFLOWERS):
			for d in range(self.sunflower.max_dist-1, 0, -1):
				y = d % len(self.syms)
				for x in self.sunflower.get_petal_sym(self.syms[y] + s):
					color = changeColor(self.color, ((y + s + self.clock) % self.color_grade) * self.color_inc)
					intensity = 1.0 - (0.1 * ((y + s + self.clock) % 8))
					self.sunflower.set_cells(meld_coords(s, self.sunflower.get_fan_shape(d, x)),
											 gradient_wheel(color, intensity))

				if oneIn(10):
					self.syms[y] = (self.syms[y] + 1) % 7

	def next_frame(self):
		"""Set up distances with random symmetries"""
		for i in range(len(self.syms)):
			self.syms[i] = randint(0,7)

		while (True):
			
			self.sunflower.black_cells()
			self.draw_rings()

			# Change it up!
			if oneIn(4):
				self.color_inc = inc(self.color_inc,10,200,500)
			if oneIn(40):
				self.color_grade = inc(self.color_grade,1,2,4)

			self.color = inc(self.color, -1, 0, MAX_COLOR)
			self.clock += 1

			yield self.speed  	# random time set in init function