from sunflower import NUM_SUNFLOWERS
from math import sin
from HelperFunctions import*
	
class Blossom(object):
	def __init__(self, sunflower_model):
		self.name = "Blossom"        
		self.sunflower = sunflower_model
		self.speed = 0.1
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(50,200)
		self.pulse = randint(4,20)
		self.color_decay = 2
		self.grow = True
		self.clock = 0
		self.bright = False
		self.BRIGHTNESS_MAX = 1
		          
	def next_frame(self):
		
		while (True):

			for s in range(NUM_SUNFLOWERS):
				for y in range(self.sunflower.max_dist):
					for x in range(self.sunflower.num_spirals):
						color = changeColor(self.color, ((x + s) % self.color_grade) * self.color_inc)
						intense = (sin(1.0 - (sin(self.clock / float(self.pulse))) + ((y + s) * self.color_decay / 40.0)) * 2) - 1.0

						if self.bright:
							self.sunflower.set_cell((s,x,y), white_wheel(color, (1 - intense) / self.BRIGHTNESS_MAX))
						else:
							self.sunflower.set_cell((s,x,y), gradient_wheel(color, self.BRIGHTNESS_MAX * intense))

			# Change it up!
			if oneIn(40):
				self.color_speed = (self.color_speed % 4) + 1
			if oneIn(400):
				self.color_inc = (self.color_inc % 50) + 1
			if oneIn(30):
				self.color_grade = (self.color_grade % 7) + 2
			
			# Add a decrease color function
			self.color = changeColor(self.color, -1)
			self.clock += 1

			yield self.speed  	# random time set in init function