from random import random, randint, choice

from HelperFunctions import*
	
class SimpleFlower(object):
	def __init__(self, rosemodel):
		self.name = "SimpleFlower"        
		self.rose = rosemodel
		self.speed = 0.1#0.5 + (randint(0,5) * 0.1)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_grade = randint(0,3)
		self.sym = randint(0,6)
		self.size = randint(0,5)
		self.clock = 0
	
	def draw_flower(self):
		for r in range(maxRose):
			for i,p in enumerate(get_petal_sym(self.sym, self.clock % maxPetal)):
				color = changeColor(self.color, (i + self.clock + r) * self.color_grade)
				self.rose.set_cells(get_petal_shape(self.size,p), wheel(color), r)

	def next_frame(self):
		
		while (True):
			
			self.rose.set_all_cells((0,0,0))
			self.draw_flower()

			# Change it up!
			if oneIn(40):
				self.sym = upORdown(self.sym, 1, 2, 5)
			if oneIn(20):
				self.size = upORdown(self.size, 1, 2, 5)
			if oneIn(40):
				self.color_grade = inc(self.color_grade,1, 3, 10)

			self.color = inc(self.color,-1,0,maxColor)
			self.clock = (self.clock + 1) % maxPetal

			yield self.speed  	# random time set in init function