from random import random, randint, choice

from HelperFunctions import*
	
class ColorSpray(object):
	def __init__(self, rosemodel):
		self.name = "ColorSpray"        
		self.rose = rosemodel
		self.speed = 0.5 + (randint(0,30) * 0.1)
		self.size = 5
		self.color = randColor()
		self.color_inc = randint(40,100)
		self.color_grade = randint(6,16)
		self.syms = [0,0,0,0,0,0]
		self.clock = 0
	
	def draw_rings(self):
		for y in range(5,0,-1):
			
			for x in get_petal_sym(self.syms[y]):
				
				color = changeColor(self.color,
					((y + self.clock) % self.color_grade) * self.color_inc)
				intensity = 1.0 - (0.1 * ((y+self.clock) % 8))
				self.rose.set_cells(get_fan_shape(y,x),
					gradient_wheel(color, intensity))

			if oneIn(10):
				self.syms[y] = (self.syms[y] + 1) % 7

	def next_frame(self):
		"""Set up distances with random symmetries"""
		for i in range(len(self.syms)):
			self.syms[i] = randint(0,7)

		while (True):
			
			self.draw_rings()

			# Change it up!
			if oneIn(4):
				self.color_inc = inc(self.color_inc,1,40,100)
			if oneIn(40):
				self.color_grade = inc(self.color_grade,2,6,16)

			self.color = changeColor(self.color, 10)
			self.clock += 1

			yield self.speed  	# random time set in init function