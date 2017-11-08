from HelperFunctions import*
from sunflower import NUM_SUNFLOWERS
	
class Pulse(object):
	def __init__(self, sunflower_model):
		self.name = "Pulse"        
		self.sunflower = sunflower_model
		self.speed = 0.1 * randint(1,5)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(4,8)
		self.clock = 0
		self.bright = randint(0,2)
		          
	def next_frame(self):
		
		while (True):
			for s in range(NUM_SUNFLOWERS):
				for y in range(self.sunflower.max_dist):
					for x in range(self.sunflower.num_spirals):
						color = (self.color + (y * self.color_inc * (s + 1))) % MAX_COLOR
						intense = 1.0 - (0.2 * (((x % 5) + self.clock) % self.color_grade))

						if self.bright == 0:
							self.sunflower.set_cell((s,x,y), white_wheel(color, intense))
						else:
							self.sunflower.set_cell((s,x,y), gradient_wheel(color, intense))

			# Change it up!
			if oneIn(40):
				self.color_speed = (self.color_speed + 1) % 4
			if oneIn(4):
				self.color_inc = (self.color_inc + 1) % 50
			if oneIn(100):
				self.color_grade += 1
				if self.color_grade >= 8:
					self.color_grade = 4

			self.color = (self.color + self.color_speed) % MAX_COLOR
			self.clock += 1

			yield self.speed