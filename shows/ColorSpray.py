from HelperFunctions import*
	
class ColorSpray(object):
	def __init__(self, sunflower_model):
		self.name = "ColorSpray"        
		self.sunflower = sunflower_model
		self.speed = randint(1,10) * 0.1
		self.size = 5
		self.color = randColor()
		self.color_inc = randint(5,10)
		self.color_grade = randint(2,5)
		self.syms = [0,1,2,3]
		self.clock = 0
	
	def draw_rings(self):
		for d in range(self.sunflower.get_max_dist(), 0, -1):
			y = d % len(self.syms)
			for x in self.sunflower.get_petal_sym(self.syms[y]):
				
				color = changeColor(self.color,
					((y + self.clock) % self.color_grade) * 20 * self.color_inc)
				intensity = 1.0 - (0.15 * ((y + self.clock) % 10))
				self.sunflower.set_cells_all_suns(self.sunflower.get_fan_shape(size=d, offset=x),
					gradient_wheel(color, intensity))

			if oneIn(6):
				self.syms[y] = upORdown(self.syms[y], 1, 1, 5)

	def next_frame(self):
		"""Set up distances with random symmetries"""
		self.syms =	[randint(0,7) for i in range(len(self.syms))]

		while (True):
			
			self.draw_rings()

			# Change it up!
			if oneIn(10):
				self.color_inc = inc(self.color_inc,1,5,10)
			if oneIn(40):
				self.color_grade = inc(self.color_grade,1,2,5)

			self.color = changeColor(self.color, 1)
			self.clock += 1

			yield self.speed  	# random time set in init function