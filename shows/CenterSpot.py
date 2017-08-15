from HelperFunctions import*
from sunflower import NUM_SUNFLOWERS

class CenterSpot(object):
	def __init__(self, sunflower_model):
		self.name = "CenterSpot"        
		self.sunflower = sunflower_model
		self.speed = 0.5
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.clock = 0
		self.bright = randint(0,2)
	
	def draw_ring(self):
		for s in range(NUM_SUNFLOWERS):
			for y in range(self.sunflower.max_dist-1, self.color_speed, -1):
				for x in range(self.sunflower.num_spirals):
					color = changeColor(self.color, ((x+s) % self.color_grade) * self.color_inc)
					intense = 1.0 - (0.1 * ((self.sunflower.max_dist - y - 1) + ((self.clock + x + s) % self.color_speed)))
					self.sunflower.set_cell((s,x,y), gradient_wheel(color, intense))

	def draw_sun(self):
		for s in range(NUM_SUNFLOWERS):
			for y in range(self.color_speed):
				for x in range(self.sunflower.num_spirals):
					color = changeColor(self.color, ((x+s) % self.color_grade) * self.color_inc)
					intense = 1.0 - (0.2 * ((y+s) + ((self.clock+x+s) % self.color_speed)))
					self.sunflower.set_cell((s,x,y), gradient_wheel(color, intense))

	def next_frame(self):
		
		while (True):
			
			self.draw_sun()
			self.draw_ring()

			# Change it up!
			if oneIn(40):
				self.color_speed = (self.color_speed % 4) + 1
			if oneIn(4):
				self.color_inc = (self.color_inc % 50) + 1
			if oneIn(100):
				self.color_grade = (self.color_grade % 7) + 2


			# Add a decrease color function
			self.color = changeColor(self.color, 2)
			self.clock += 1

			yield self.speed  	# random time set in init function