from random import random, randint, choice

from HelperFunctions import*

sparkle_perc = 5            

class Sparkle(object):
	def __init__(self, rosemodel, color, pos, intense = 0, growing = True):
		self.rose = rosemodel
		self.pos = pos
		self.color = color
		self.intense = intense
		self.growing = True
	
	def draw_sparkle(self):
		self.rose.set_cell(self.pos, gradient_wheel(self.color, self.intense))
	
	def fade_sparkle(self):
		if oneIn(3):
			if self.growing == True:
				self.intense += 0.25
				if self.intense >= 1.0:
					self.intense = 1
					self.growing = False
				return True
			else:
				self.intense -= 0.25
				if self.intense > 0: return True
				else: return False

        						
class Sparkles(object):
	def __init__(self, rosemodel):
		self.name = "Sparkles"        
		self.rose = rosemodel
		self.sparkles = []	# List that holds Sparkle objects
		self.speed = 0.1
		self.color = randColor()
		self.spark_num = NUM_PIXELS * sparkle_perc / 100
		          
	def next_frame(self):
		
		for i in range (self.spark_num):
			new_sparkle = Sparkle(self.rose, randColorRange(self.color, 30), self.rose.get_rand_cell())
			self.sparkles.append(new_sparkle)	
					
		while (True):
			
			while len(self.sparkles) < self.spark_num:
				new_sparkle = Sparkle(self.rose, randColorRange(self.color, 30), self.rose.get_rand_cell())
				self.sparkles.append(new_sparkle)
			
			# Set background to black
			self.rose.set_all_cells((0,0,0))
			
			# Draw the sparkles
				
			for s in self.sparkles:
				s.draw_sparkle()
				if s.fade_sparkle() == False:
					self.sparkles.remove(s)
			
			# self.rose.go()
			
			# Change the colors
			
			if oneIn(100):
				self.color = randColorRange(self.color, 30)
			
			yield self.speed  	# random time set in init function