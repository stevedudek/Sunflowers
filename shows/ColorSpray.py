from HelperFunctions import*
	
class ColorSpray(object):
	def __init__(self, sunflower_model):
		self.name = "ColorSpray"        
		self.sunflower = sunflower_model
		self.speed = 0.5 + (randint(0,30) * 0.1)
		self.size = 5
		self.color = randColor()
		self.color_inc = randint(100,1000)
		self.color_grade = randint(6,16)
		self.syms = [0,0,0,0,0,0]
		self.clock = 0
		self.max_brightness = 1.0
		self.sunflower.set_max_brightness(self.max_brightness)
	
	def draw_rings(self):
		for d in range(self.sunflower.max_dist-1, 0, -1):
			y = d % len(self.syms)
			for x in self.sunflower.get_petal_sym(self.syms[y]):
				
				color = changeColor(self.color,
					((y + self.clock) % self.color_grade) * 40 * self.color_inc)
				intensity = 1.0 - (0.1 * ((y+self.clock) % 8))
				self.sunflower.set_cells_all_suns(self.sunflower.get_fan_shape(d,x),
					gradient_wheel(color, intensity))

			if oneIn(10):
				self.syms[y] = (self.syms[y] + 1) % 7

	def next_frame(self):
		"""Set up distances with random symmetries"""
		self.syms =	[randint(0,7) for i in range(len(self.syms))]

		while (True):
			
			self.draw_rings()

			# Change it up!
			self.color_inc = inc(self.color_inc,10,100,1000)
			if oneIn(40):
				self.color_grade = inc(self.color_grade,2,6,16)

			self.color = changeColor(self.color, 10)
			self.clock += 1

			yield self.speed  	# random time set in init function