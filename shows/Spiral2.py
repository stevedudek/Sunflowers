from HelperFunctions import*
from math import sin, pi
from sunflower import NUM_SUNFLOWERS

class Spiral2(object):
	def __init__(self, sunflower_model):
		self.name = "Spiral2"        
		self.sunflower = sunflower_model
		self.speed = 2
		self.spacing = randint(2,5)
		self.color1 = randColor()
		self.color2 = changeColor(self.color1, 1000)
		self.clock = 0
		          
	def next_frame(self):
		
		while (True):
			for s in range(NUM_SUNFLOWERS):
				for p in range(self.sunflower.num_spirals):
					for d in range(self.sunflower.max_dist):
						color = self.color1 if (p + self.clock) % self.spacing else self.color2
						intense = (sin(pi * ((d + self.clock) % self.sunflower.max_dist) / (self.sunflower.max_dist + 1)) + 1) / 2.0
						new_d = (d + (2 * s)) % self.sunflower.max_dist
						self.sunflower.set_cell((s, p, new_d), gradient_wheel(color, intense))
					
			self.color1 = changeColor(self.color1, 1)
			self.color2 = changeColor(self.color2, -4)

			if oneIn(40):
				self.spacing = upORdown(self.spacing, 2, 5)

			self.clock += 1

			yield self.speed