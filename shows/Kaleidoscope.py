from random import random, randint, choice

from HelperFunctions import*
	
class Kaleidoscope(object):
	def __init__(self, rosemodel):
		self.name = "Kaleidoscope"        
		self.rose = rosemodel
		self.speed = 0.5
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.density = randint(2,20)
		self.color_speed = randint(4,24)
		self.color_grade = randint(3,8)
		self.clock = 0
		self.bright = randint(0,2)
	
	def draw_chips(self):
		for y in range(maxDistance):
			for x in range(maxPetal):
				if (x+y) % self.color_grade == 0:
					x = (x + self.color_grade) % maxPetal
					y = (y + self.color_speed) % maxDistance
					color = changeColor(self.color, ((y + self.clock) % self.color_grade) * self.color_inc)
					intensity = 1.0 - (0.1 * ((x+y+self.clock) % 8))
					self.rose.set_cell((x,y), gradient_wheel(color, intensity))


	def next_frame(self):
		
		while (True):
			
			self.rose.set_all_cells((0,0,0))
			self.draw_chips()

			# Change it up!
			if oneIn(40):
				self.density = inc(self.density,1,2,20)
			if oneIn(40):
				self.color_speed = inc(self.color_speed,1,1,maxPetal)
			if oneIn(4):
				self.color_inc = inc(self.color_inc,1,1,50)
			if oneIn(100):
				self.color_grade = inc(self.color_grade,1,3,8)

			self.color = changeColor(self.color, 2)
			self.clock += 1

			yield self.speed  	# random time set in init function