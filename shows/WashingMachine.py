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

class Arc(object):
	def __init__(self, rosemodel, r, d, decay):
		self.rose = rosemodel
		self.r = r
		self.d = d
		self.p = 1
		self.decay = decay
		self.faders = []	# List that holds Fader objects
		self.dir = 1
	
	def draw(self):
		# Draw the Faders		
		for f in self.faders:
			f.draw()
			if not f.fade():
				self.faders.remove(f)

	def move(self, color):
		
		self.p += self.dir

		if (self.p % maxPetal) == 0:
			self.dir *= -1

		if self.p == 12:
			if oneIn(2) == 1:
				self.dir *= -1

		for i,leaf in enumerate(get_fan_band(self.d, self.p)):
			new_fader = Fader(self.rose, changeColor(color, (i*4) + (self.d*30)), self.r, leaf, self.decay)
			self.faders.append(new_fader)
   
class WashingMachine(object):
	def __init__(self, rosemodel):
		self.name = "WashingMachine"        
		self.rose = rosemodel
		self.arcs = []	# List that holds Arc objects
		self.speed = 0.1
		self.color = randColor()

		for r in range(maxRose):
			for d in range(1, maxDistance):
				new_arc = Arc(self.rose, r, d, (1.0 - (d * 0.1)))
				self.arcs.append(new_arc)
		          
	def next_frame(self):
		
		while (True):
			
			# Set background to black
			self.rose.set_all_cells((0,0,0))
			
			for a in self.arcs:
				a.move(self.color)
				a.draw()

			# Change the colors and symmetry
			
			self.color = randColorRange(self.color, 5)
			
			yield self.speed  	# random time set in init function