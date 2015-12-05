from random import random, randint, choice

from HelperFunctions import*
	
class Gears(object):
	def __init__(self, rosemodel):
		self.name = "Gears"        
		self.rose = rosemodel
		self.speed = 0.5
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.density = randint(2,20)
		self.color_speed = randint(4,24)
		self.color_grade = randint(3,8)
		self.syms = [0,0,0,0,0,0]
		self.clock = 0
		self.bright = randint(0,2)
	
	def draw_rings(self):
		for r in range(maxRose):
			for y in range(maxDistance):
				offset = self.clock % maxPetal
				if y % 2:
					offset = maxPetal - offset

				for x in get_petal_sym(self.syms[y], offset):
					color = changeColor(self.color, ((y + self.clock) % self.color_grade) * self.color_inc)
					intensity = 1.0 - (0.1 * ((y+r+self.clock) % 11))
					self.rose.set_cell((x,y), gradient_wheel(color, intensity), r)

				if oneIn(10):
					self.syms[y] = (self.syms[y] + 1) % 8

	def next_frame(self):
		"""Set up distances with random symmetries"""
		for i in range(len(self.syms)):
			self.syms[i] = randint(0,8)

		while (True):
			
			#self.rose.set_all_cells((0,0,0))
			self.draw_rings()

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