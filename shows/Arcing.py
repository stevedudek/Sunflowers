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
		return (self.life >= 0)

class Arc(object):
	def __init__(self, rosemodel, color, petal, dir, start=0, fade=0.1):
		self.rose = rosemodel
		self.color = color
		self.p = petal
		self.dir = dir	# 1 or -1
		self.fade = fade
		if self.dir == 1:
			self.d = 0
		else:
			self.d = 10
	
	def draw(self):
		new_fader = Fader(self.rose, self.color, get_coord((self.p,self.d)), self.fade)
		return new_fader
	
	def move(self):
		self.d += self.dir
		return (self.d >= 0 and self.d <= 10)

	
class Arcing(object):
	def __init__(self, rosemodel):
		self.name = "Arcing"        
		self.rose = rosemodel
		self.speed = 0.2 + (randint(0,3) * 0.1)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.clock = 0
		self.faders = []	# List that holds Fader objects
		self.arcs = []	# List that holds Arc objects 
		self.max_arcs = 10
	
	def draw_faders(self):
		for f in self.faders:
			f.draw()
			if not f.fade():
				self.faders.remove(f)

	def draw_arcs(self):
		for a in self.arcs:
			self.faders.append(a.draw())

	def move_arcs(self):
		for a in self.arcs:
			if not a.move():
				self.arcs.remove(a)

	def next_frame(self):
		
		while (True):
			
			self.draw_faders()
			self.draw_arcs()
			self.move_arcs()

			if len(self.arcs) < self.max_arcs:
				new_arc = Arc(self.rose, randColorRange(self.color, 100),
					randint(0,maxPetal), plusORminus())
				self.arcs.append(new_arc)

			self.color = changeColor(self.color, -2)
			self.clock += 1

			yield self.speed  	# random time set in init function