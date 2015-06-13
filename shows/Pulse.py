from random import random, randint, choice

from HelperFunctions import*
	
class Pulse(object):
	def __init__(self, rosemodel):
		self.name = "Pulse"        
		self.rose = rosemodel
		self.speed = 0.3
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.clock = 0
		self.bright = randint(0,2)
		          
	def next_frame(self):
		
		while (True):
			
			for y in range(maxDistance):
				for x in range(maxPetal):
					color = (self.color + (y * self.color_inc)) % maxColor
					intense = 1.0 - (0.1 * ((x + y + self.clock) % self.color_grade))

					if self.bright == 0:
						self.rose.set_cell((x,y), white_wheel(color, intense))
					else:
						self.rose.set_cell((x,y), gradient_wheel(color, intense))

			# Change it up!
			if oneIn(40):
				self.color_speed = (self.color_speed + 1) % 4
			if oneIn(4):
				self.color_inc = (self.color_inc + 1) % 50
			if oneIn(100):
				self.color_grade += 1
				if self.color_grade >= 8:
					self.color_grade = 2

			self.color = (self.color + self.color_speed) % maxColor
			self.clock += 1

			yield self.speed  	# random time set in init function