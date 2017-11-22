from HelperFunctions import*
from sunflower import NUM_SUNFLOWERS

class Kaleidoscope(object):
	def __init__(self, sunflower_model):
		self.name = "Kaleidoscope"        
		self.sunflower = sunflower_model
		self.speed = 0.2
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.density = randint(2,20)
		self.color_speed = randint(4,24)
		self.color_grade = randint(1,5)
		self.clock = 0
		self.bright = randint(0,2)
	
	def draw_chips(self):
		for s in range(NUM_SUNFLOWERS):
			for y in range(self.sunflower.max_dist):
				for x in range(self.sunflower.num_spirals):
					x = (x + s + self.color_grade) % self.sunflower.num_spirals
					y = (y + s + self.color_speed) % self.sunflower.max_dist
					color = changeColor(self.color, ((y + s + self.clock) % self.color_grade) * self.color_inc)
					intensity = 1.0 - (0.1 * ((x + y + self.clock) % 15))
					if s % 2:
						intensity = 1 - intensity
					self.sunflower.set_cell((s,x,y), gradient_wheel(color, intensity))


	def next_frame(self):
		
		while (True):
			
			self.sunflower.set_all_cells((0,0,0))
			self.draw_chips()

			# Change it up!
			if oneIn(40):
				self.density = inc(self.density,1,2,20)
			if oneIn(40):
				self.color_speed = inc(self.color_speed, 1, 1, self.sunflower.num_spirals)
			if oneIn(10):
				self.color_inc = inc(self.color_inc,1,20,50)

			self.color = changeColor(self.color, 2)
			self.clock += 1

			yield self.speed  	# random time set in init function