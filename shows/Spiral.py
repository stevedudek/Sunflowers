from HelperFunctions import*
from math import sin, pi
from sunflower import NUM_SUNFLOWERS

class Spiral(object):
	def __init__(self, sunflower_model):
		self.name = "Spiral"        
		self.sunflower = sunflower_model
		self.speed = 1
		self.color1 = randColor()
		self.color2 = randColor()
		self.clock = 0
		          
	def next_frame(self):
		
		while (True):
			for s in range(NUM_SUNFLOWERS):
				for p in range(self.sunflower.get_num_spirals()):
					for d in range(self.sunflower.max_dist):
						color = self.color1 if (p + self.clock) % 2 else self.color2
						intense = (sin(pi * ((d + self.clock) % self.sunflower.max_dist) / (self.sunflower.max_dist + 1)) + 1) / 2
						self.sunflower.set_cell((s, (p+s) % self.sunflower.get_num_spirals(), (d + s) % self.sunflower.max_dist), gradient_wheel(color, intense))
					
			self.color1 = changeColor(self.color1, 1)
			self.color2 = changeColor(self.color2, -4)

			self.clock += 1

			yield self.speed