from random import random, randint, choice

from HelperFunctions import*
           
class Fader(object):
	def __init__(self, rosemodel, color, pos, decay):
		self.rose = rosemodel
		self.pos = pos
		self.color = color
		self.decay = decay
		self.life = 1.0
	
	def draw(self):
		self.rose.set_cell(self.pos, gradient_wheel(self.color, self.life))
	
	def fade(self):
		self.life -= self.decay
		if self.life >= 0:
			return True
		else:
			return False

        						
class ContraRotater(object):
	def __init__(self, rosemodel):
		self.name = "ContraRotater"        
		self.rose = rosemodel
		self.faders = []	# List that holds Fader objects
		self.speed = 0.5
		self.color = randColor()
		self.trail = 0.2
		self.clock = 0
		          
	def next_frame(self):
		
		while (True):
			
			# Set background to black
			self.rose.set_all_cells((0,0,0))
			
			# Create new faders

			for d in range(maxDistance):
				p = self.clock % maxPetal
				if d % 2:
					p = maxPetal - p  # The contra rotation

				new_fader = Fader(self.rose, self.color, (p,d), self.trail)
				self.faders.append(new_fader)
			
			# Draw the Faders
				
			for f in self.faders:
				f.draw()
				if f.fade() == False:
					self.faders.remove(f)
			
			# Change the colors
			
			if oneIn(100):
				self.color = randColorRange(self.color, 30)
			
			self.clock += 1

			yield self.speed  	# random time set in init function