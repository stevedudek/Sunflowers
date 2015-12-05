from random import random, randint, choice

from HelperFunctions import*
	
class GearsTwo(object):
	def __init__(self, rosemodel):
		self.name = "GearsTwo"        
		self.rose = rosemodel
		self.speed = 0.5
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_grade = randint(3,8)
		self.syms = [0,0,0,0,0,0]
		self.clock = 0
	
	def draw_rings(self):
		for r in range(maxRose):
			for y in range(maxDistance):
				offset = 0
				for x in get_petal_sym(self.syms[y]+r, offset):
					color = changeColor(self.color, ((y + self.clock + (r*2)) % self.color_grade) * self.color_inc)
					intensity = 1.0 - (0.1 * ((x+y+self.clock) % 8))
					self.rose.set_cell((x,y), gradient_wheel(color, intensity), r)

				if oneIn(10):
					self.syms[y] = (self.syms[y] + 1) % 7

	def next_frame(self):
		"""Set up distances with random symmetries"""
		for i in range(len(self.syms)):
			self.syms[i] = randint(0,7)

		while (True):
			
			self.rose.set_all_cells((0,0,0))
			self.draw_rings()

			# Change it up!
			if oneIn(4):
				self.color_inc = inc(self.color_inc,1,20,50)
			if oneIn(40):
				self.color_grade = inc(self.color_grade,1,2,4)

			self.color = inc(self.color,-1,0,maxColor)
			self.clock += 1

			yield self.speed  	# random time set in init function