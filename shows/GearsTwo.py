from HelperFunctions import*
from sunflower import NUM_SUNFLOWERS
	
class GearsTwo(object):
	def __init__(self, sunflower_model):
		self.name = "GearsTwo"        
		self.sunflower = sunflower_model
		self.speed = 0.05
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.syms = [0,0,0]
		self.clock = 0
	
	def draw_rings(self):
		for s in range(NUM_SUNFLOWERS):
			for y in range(self.sunflower.max_dist):
				offset = 0
				for x in self.sunflower.get_petal_sym(self.syms[y % len(self.syms)] + s, offset):
					color = changeColor(self.color, (((x % 3) * 2) + (y * 1.0) + self.clock + (s * 2)) * self.color_inc)
					intensity = 1.0 - (0.05 * ((x + y + (s * 5) + self.clock) % 20))
					self.sunflower.set_cell((s,x,y), gradient_wheel(color, intensity))

				if oneIn(100):
					self.syms[y % len(self.syms)] = upORdown(self.syms[y % len(self.syms)], 1, 2, 6)

	def next_frame(self):
		"""Set up distances with random symmetries"""
		for i in range(len(self.syms)):
			self.syms[i % len(self.syms)] = randint(2,6)

		while (True):
			
			self.sunflower.black_cells()
			self.draw_rings()

			# Change it up!
			if oneIn(4):
				self.color_inc = inc(self.color_inc,1,20,50)

			self.color = inc(self.color, -1, 0, MAX_COLOR)
			self.clock += 1

			yield self.speed  	# random time set in init function