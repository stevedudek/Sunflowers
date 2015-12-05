from random import random, randint, choice

from HelperFunctions import*
	
class SimpleFan(object):
	def __init__(self, rosemodel):
		self.name = "SimpleFan"        
		self.rose = rosemodel
		self.speed = 0.2 + (randint(0,5) * 0.1)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_grade = randint(0,3)
		self.sym = randint(1,6)
		self.size = randint(0,5)
		self.clock = 0
	
	def draw_flower(self):
		for r in range(maxRose):
			for p in get_petal_sym(self.sym+r, self.clock % maxPetal):
				color = changeColor(self.color, (p + r + self.clock) * self.color_grade)
				self.rose.set_cells(get_fan_shape(self.size,p), wheel(color), r)

	def next_frame(self):
		
		while (True):
			
			self.rose.set_all_cells((0,0,0))
			self.draw_flower()

			# Change it up!
			if oneIn(40):
				self.sym = upORdown(self.sym, 1, 1, 5)
			if oneIn(20):
				self.size = upORdown(self.size, 1, 1, 5)
			if oneIn(40):
				self.color_grade = inc(self.color_grade,1,0,8)

			self.color = inc(self.color,-1,0,maxColor)
			self.clock += 1

			yield self.speed  	# random time set in init function