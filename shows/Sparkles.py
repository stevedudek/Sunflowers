from random import random, randint, choice, shuffle

from HelperFunctions import*          

class Sparkle(object):
	def __init__(self, rosemodel, color, r, pos, age = 0.25, intense = 0, growing = True):
		self.rose = rosemodel
		self.r = r
		self.pos = pos
		self.color = color
		self.intense = intense
		self.age = age
		self.growing = True
	
	def draw_sparkle(self):
		self.rose.set_cell(self.pos, gradient_wheel(self.color, self.intense), self.r)
	
	def set_black(self):
		self.rose.set_cell(self.pos, (0,0,0), self.r)

	def fade_sparkle(self):
		if self.growing == True:
			self.intense += self.age
			if self.intense >= 1.0:
				self.intense = 1
				self.growing = False
			return True
		else:
			self.intense -= self.age
			return (self.intense > 0)

        						
class Sparkles(object):
	def __init__(self, rosemodel):
		self.name = "Sparkles"        
		self.rose = rosemodel
		self.sparkles = []	# List that holds Sparkle objects
		self.speed = 0.2
		self.color = randColor()
		self.sparkle_perc = 10
		self.spark_num = 3 * NUM_PIXELS * self.sparkle_perc / 100
		self.age = 0.1
		self.clock = 0
	
	def next_frame(self):
		
		while (True):

			while len(self.sparkles) < self.spark_num:
				new_sparkle = Sparkle(self.rose, randColorRange(self.color, 30),
					randRose(), get_rand_cell(),
					randint(1,6)/20.0)
				self.sparkles.append(new_sparkle)
			
			# Set background to black
			#self.rose.set_all_cells((0,0,0))
			
			# Draw the sparkles
				
			for s in self.sparkles:
				s.draw_sparkle()
				if not s.fade_sparkle():
					s.set_black()
					self.sparkles.remove(s)
			
			self.clock += 1

			# self.rose.go()
			
			# Change the colors
			
			if oneIn(100):
				self.color = randColorRange(self.color, 30)
			
			yield self.speed  	# random time set in init function