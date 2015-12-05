from random import random, randint, choice

from HelperFunctions import*
	
class FanPetal(object):
	def __init__(self, rosemodel):
		self.name = "FanPetal"        
		self.rose = rosemodel
		self.speed = randint(1,3)
		self.color = randColor()
		self.fan_color = randColor()
		self.petal_color = randColor()
		self.fan_sym = randint(1,6)
		self.petal_sym = randint(1,6)
		self.fan_size = randint(0,5)
		self.petal_size = randint(0,5)
		self.clock = 0
	
	def draw_fan(self):
		for r in range(maxRose):
			for p in get_petal_sym(self.fan_sym+r, maxPetal - 1 - (self.clock % maxPetal)):
				color = randColorRange(self.fan_color, 30)
				self.rose.set_cells(get_fan_shape(self.fan_size, p), wheel(color), r)

	def draw_petal(self):
		for r in range(maxRose):
			for p in get_petal_sym(self.petal_sym+r, self.clock % maxPetal):
				color = randColorRange(self.petal_color, 30)
				self.rose.set_cells(get_petal_shape(self.petal_size, p), wheel(color), r)

	def next_frame(self):
		
		while (True):
			
			self.rose.set_all_cells((0,0,0))

			if self.fan_size > self.petal_size:
				self.draw_fan()
				self.draw_petal()
			else:
				self.draw_petal()
				self.draw_fan()

			# Change it up!
			if oneIn(40):
				self.fan_sym = (7 + self.fan_sym ) % 8
			if oneIn(20):
				self.petal_sym = (7 + self.petal_sym ) % 8
			
			if oneIn(20):
				self.fan_size = (self.fan_size + 1) % 6
			if oneIn(30):
				self.petal_size = (self.petal_size + 1) % 6

			self.fan_color = changeColor(self.fan_color, 10)
			self.petal_color = changeColor(self.petal_color, -15)

			self.clock += 1

			yield self.speed  	# random time set in init function