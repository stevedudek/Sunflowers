from random import random, randint, choice

from HelperFunctions import*
from rose import rose_in_direction

class Spiro(object):
	def __init__(self, rosemodel, color, r, life):
		self.rose = rosemodel
		self.r = r
		self.color = color
		self.pos = get_rand_cell()
		self.dir = randDir()
		self.life = life

	def draw_spiro(self):
		self.rose.set_cell(get_coord(self.pos), wheel(self.color), self.r)
	
	def move_spiro(self):			
		self.pos = rose_in_direction(self.pos, self.dir, 1)
		if oneIn(20):
			self.color = randColorRange(self.color, 100)
		self.life -= 1
		return self.life > 0

class Mover(object):
	def __init__(self, rosemodel):
		self.name = "Mover"        
		self.rose = rosemodel
		self.color = randColor()
		self.speed = 0.2
		self.spiros = []
		          
	def next_frame(self):
		
		while (True):
			
			while len(self.spiros) < 9 or oneIn(10):
				new_spiro = Spiro(self.rose, self.color, randRose(), randint(24,500))
				self.spiros.append(new_spiro)

			for s in self.spiros:
				s.draw_spiro()
				if s.move_spiro() == False:
					self.spiros.remove(s)
			
			if oneIn(10):
				self.color = randColorRange(self.color, 100)

			yield self.speed