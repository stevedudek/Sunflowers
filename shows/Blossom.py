from random import random, randint, choice

from HelperFunctions import*
	
class Blossom(object):
	def __init__(self, rosemodel):
		self.name = "Blossom"        
		self.rose = rosemodel
		self.speed = 0.3
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.color_decay = 10
		self.grow = True
		self.clock = 0
		self.bright = False
		          
	def next_frame(self):
		
		while (True):

			for y in range(maxDistance):
				for x in range(maxPetal):
					color = changeColor(self.color, (x % self.color_grade) * self.color_inc)
					intense = 1.0 - (y * self.color_decay / 40.0)

					if self.bright:
						self.rose.set_cell((x,y), white_wheel(color, intense))
					else:
						self.rose.set_cell((x,y), gradient_wheel(color, intense))

			# Change it up!
			if oneIn(40):
				self.color_speed = (self.color_speed % 4) + 1
			if oneIn(10):
				self.color_inc = (self.color_inc % 50) + 1
			if oneIn(30):
				self.color_grade = (self.color_grade % 7) + 2
			
			if oneIn(2):
				if self.grow:
					self.color_decay += 1
					if self.color_decay > 30:
						self.grow = False
				else:
					self.color_decay -= 1
					if self.color_decay < 8:
						self.grow = True

			# Add a decrease color function
			self.color = changeColor(self.color, -1)
			self.clock += 1

			yield self.speed  	# random time set in init function