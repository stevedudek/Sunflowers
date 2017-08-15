from HelperFunctions import*
from sunflower import NUM_SUNFLOWERS

class Gears(object):
	def __init__(self, sunflower_model):
		self.name = "Gears"        
		self.sunflower = sunflower_model
		self.speed = 0.5
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.density = randint(2,20)
		self.color_speed = randint(4,24)
		self.color_grade = randint(3,8)
		self.syms = [0,0,0,0,0,0]
		self.clock = 0
		self.bright = randint(0,2)
	
	def draw_rings(self):
		for s in range(NUM_SUNFLOWERS):
			for y in range(self.sunflower.max_dist):
				offset = self.clock % self.sunflower.num_spirals
				if y % 2:
					offset = self.sunflower.num_spirals - offset

				for x in self.sunflower.get_petal_sym(self.syms[y % len(self.syms)], offset):
					color = changeColor(self.color, ((y + self.clock) % self.color_grade) * self.color_inc)
					intensity = 1.0 - (0.05 * ((y + s + self.clock) % ((self.sunflower.max_dist * 2) - 1)))
					self.sunflower.set_cell((s,x,y), gradient_wheel(color, intensity))

				if oneIn(10):
					self.syms[y % len(self.syms)] = (self.syms[y % len(self.syms)] + 1) % 8

	def next_frame(self):
		"""Set up distances with random symmetries"""
		for i in range(len(self.syms)):
			self.syms[i] = randint(0,8)

		while (True):
			
			# self.sunflower.black_cells()
			self.draw_rings()

			# Change it up!
			if oneIn(40):
				self.density = inc(self.density,1,2,20)
			if oneIn(40):
				self.color_speed = inc(self.color_speed, 1, 1, self.sunflower.num_spirals)
			if oneIn(4):
				self.color_inc = inc(self.color_inc,1,1,50)
			if oneIn(100):
				self.color_grade = inc(self.color_grade,1,3,8)

			self.color = changeColor(self.color, 2)
			self.clock += 1

			yield self.speed  	# random time set in init function