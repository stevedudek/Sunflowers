from random import random, randint, choice

from HelperFunctions import*
	
class Tester(object):
	def __init__(self, rosemodel):
		self.name = "Tester"        
		self.rose = rosemodel
		self.speed = 0.2
		self.color = (0,255,0)
		self.clock = 0
		          
	def next_frame(self):
		
		while (True):
			
			self.rose.set_all_cells((0,0,0))
					
			# Ring tester
			self.rose.set_cells(get_all_radial(self.clock % maxDistance),
				wheel(self.clock * 10 % maxColor))

			self.clock += 1

			yield self.speed