from random import random, randint, choice

from HelperFunctions import*
	
class Twist(object):
	def __init__(self, rosemodel):
		self.name = "Twist"        
		self.rose = rosemodel
		self.speed = 0.1
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.ring = randint(0,5)
		self.color_speed = randint(4,24)
		self.color_grade = randint(2,8)
		self.clock = 0

	
	def draw_ring(self):
		for y in range(5,self.ring,-1):
			for x in range(maxPetal):
				color = changeColor(self.color, (x % self.color_grade) * self.color_inc)
				intense = 1.0 - (0.1 * ((maxDistance-y-1) + ((self.clock+x) % self.color_speed)))
				self.rose.set_cell((x,y), gradient_wheel(color, intense))

	def draw_sun(self):
		for y in range(self.ring):
			for x in range(maxPetal):
				color = changeColor(self.color, (x % self.color_grade) * self.color_inc)
				intense = 1.0 - (0.2 * (y + ((self.clock+x) % self.color_speed)))
				self.rose.set_cell((x,y), gradient_wheel(color, intense))


	def next_frame(self):
		
		while (True):
			
			self.draw_sun()
			self.draw_ring()

			# Change it up!
			if oneIn(40):
				self.ring = (self.ring + 1) % maxDistance
			if oneIn(40):
				self.color_speed = (self.ring % maxPetal) + 2
			if oneIn(4):
				self.color_inc = (self.color_inc % 50) + 1
			if oneIn(100):
				self.color_grade = (self.color_grade % 7) + 2


			# Add a decrease color function
			self.color = changeColor(self.color, 2)
			self.clock += 1

			yield self.speed  	# random time set in init function