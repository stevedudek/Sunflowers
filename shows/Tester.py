from random import random, randint, choice

from HelperFunctions import*
	
class Tester(object):
	def __init__(self, rosemodel):
		self.name = "Tester"        
		self.rose = rosemodel
		self.speed = 0.1
		self.color = (0,255,0)
		self.clock = 0
		          
	def next_frame(self):
		
		while (True):
			
			self.rose.set_all_cells((0,0,0))
					
			# All one - color cycle
			#self.rose.set_all_cells(wheel(self.clock % maxColor))
			
			# Ring test
			self.rose.set_cells(get_all_radial(self.clock % maxDistance),
			 wheel(self.clock * 10 % maxColor))

			# Spoke test
			#self.rose.set_cells(get_all_radial(self.clock % 3),
			# wheel(self.clock * 10 % maxColor))

			#d = self.clock % maxDistance
			#p = (self.clock / maxDistance) % maxPetal
			
			#self.rose.set_cell((p,d), self.color)

			self.clock += 1

			yield self.speed