from random import random, randint, choice

from HelperFunctions import*
	
class CenterSpot(object):
	def __init__(self, rosemodel):
		self.name = "CenterSpot"        
		self.rose = rosemodel
		self.speed = 0.5 + (randint(0,10) * 0.1)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.clock = 0
		self.bright = randint(0,2)
	
	def draw_ring(self):
		for r in range(maxRose):
			for y in range(5,self.color_speed,-1):
				for x in range(maxPetal):
					color = changeColor(self.color, ((x+r) % self.color_grade) * self.color_inc)
					intense = 1.0 - (0.1 * ((maxDistance-y-1) + ((self.clock+x+r) % self.color_speed)))
					self.rose.set_cell((x,y), gradient_wheel(color, intense), r)

	def draw_sun(self):
		for r in range(maxRose):
			for y in range(self.color_speed):
				for x in range(maxPetal):
					color = changeColor(self.color, ((x+r) % self.color_grade) * self.color_inc)
					intense = 1.0 - (0.2 * ((y+r) + ((self.clock+x+r) % self.color_speed)))
					self.rose.set_cell((x,y), gradient_wheel(color, intense), r)

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