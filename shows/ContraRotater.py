from random import random, randint, choice

from HelperFunctions import*
           
class Fader(object):
	def __init__(self, rosemodel, color, r, pos, decay):
		self.rose = rosemodel
		self.r = r
		self.pos = pos
		self.color = color
		self.decay = decay
		self.life = 1.0

	def draw(self):
		self.rose.set_cell(self.pos, gradient_wheel(self.color, self.life), self.r)
	
	def fade(self):
		self.life -= self.decay
		return (self.life >= 0)
        						
class ContraRotater(object):
	def __init__(self, rosemodel):
		self.name = "ContraRotater"        
		self.rose = rosemodel
		self.faders = []	# List that holds Fader objects
		self.speed = 0.5
		self.color = randColor()
		self.trail = 0.2
		self.symm = 1
		self.clock = 0
		          
	def next_frame(self):
		
		while (True):
			
			# Set background to black
			self.rose.set_all_cells((0,0,0))
			
			# Create new faders
			for r in range(maxRose):
				for p in range(maxPetal):
					for d in range(maxDistance):
						if (p+r) % (maxPetal / (self.symm+r)) == self.clock % (maxPetal / self.symm):
							if (d+r) % 2 == 0:
								new_p = maxPetal - p - 1
							else:
								new_p = p
							new_fader = Fader(self.rose, self.color, r, (new_p,d), self.trail)
							self.faders.append(new_fader)
			
			# Draw the Faders
				
			for f in self.faders:
				f.draw()
				if not f.fade():
					self.faders.remove(f)
			
			# Change the colors and symmetry
			
			self.color = randColorRange(self.color, 5)
			
			if oneIn(20):
				self.trail = inc(self.trail, 0.1, 0.1, 0.5) 

			if oneIn(50):
				self.symm = inc(self.symm, 1, 1, 7)

			self.clock += 1

			yield self.speed