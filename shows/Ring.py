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
	def __init__(self, rosemodel, color, r, petal, dir, start=0, fade=0.1):
		self.rose = rosemodel
		self.r = r
		self.color = color
		self.p = petal
		self.dir = dir	# 1 or -1
		self.fade = fade
		if self.dir == 1:
			self.d = 0
		else:
			self.d = 10
	
	def draw(self):
		new_fader = Fader(self.rose, self.color, self.r, get_coord((self.p,self.d)), self.fade)
		return new_fader
	
	def move(self):
		if self.d == 5:
			return False
		else:
			self.d += self.dir
			return True

	
class Ring(object):
	def __init__(self, rosemodel):
		self.name = "Ring"        
		self.rose = rosemodel
		self.speed = 0.1
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.clock = 0
		self.bright = randint(0,2)
		self.faders = []	# List that holds Fader objects
		self.arcs = []	# List that holds Arc objects 
		self.max_arcs = 18
	
	def draw_ring(self):
		for r in range(maxRose):
			for y in range(maxDistance):
				for x in range(maxPetal):
					color = changeColor(self.color, (x + r % self.color_grade) * self.color_inc)
					intense = 1.0 - ((maxDistance-y-1) * 0.3)
					self.rose.set_cell((x,y), gradient_wheel(color, intense), r)

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
			
			self.draw_ring()
			self.draw_faders()
			self.draw_arcs()
			self.move_arcs()

			if oneIn(10) or len(self.arcs) < self.max_arcs:
				new_arc = Arc(self.rose, randColorRange(self.color, 200), randRose(),
					randint(0,maxPetal), plusORminus())
				self.arcs.append(new_arc)

			# Change it up!
			if oneIn(40):
				self.color_speed = (self.color_speed % 4) + 1
			if oneIn(4):
				self.color_inc = (self.color_inc % 50) + 1
			if oneIn(100):
				self.color_grade = (self.color_grade % 7) + 2


			# Add a decrease color function
			self.color = changeColor(self.color, 2)
			self.clock += 1

			yield self.speed  	# random time set in init function