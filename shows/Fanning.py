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

	def black(self):
		self.rose.set_cell(self.pos, (0,0,0))

class Fan(object):
	def __init__(self, rosemodel, color, petal, fade=0.1):
		self.rose = rosemodel
		self.color = color
		self.p = petal
		self.d = 0
		self.fade = fade
	
	def draw(self):
		faders = []
		for c in get_fan_band(self.d,self.p):
			new_fader = Fader(self.rose, self.color, c, self.fade)
			faders.append(new_fader)
		return faders
	
	def move(self):
		self.d += 1
		return (self.d < 6)

	
class Fanning(object):
	def __init__(self, rosemodel):
		self.name = "Fanning"        
		self.rose = rosemodel
		self.speed = 0.2 + (randint(0,3) * 0.1)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.clock = 0
		self.faders = []	# List that holds Fader objects
		self.fans = []	# List that holds Fan objects 
		self.max_fans = 4
	
	def draw_faders(self):
		for f in self.faders:
			f.draw()
			if not f.fade():
				f.black()
				self.faders.remove(f)

	def draw_fans(self):
		for a in self.fans:
			for f in a.draw():
				self.faders.append(f)

	def move_fans(self):
		for a in self.fans:
			if not a.move():
				self.fans.remove(a)

	def next_frame(self):
		
		while (True):
			
			self.draw_faders()
			self.draw_fans()
			self.move_fans()

			if len(self.fans) < self.max_fans:
				new_fan = Fan(self.rose, randColorRange(self.color, 100),
					randint(0,maxPetal), 0.3)
				self.fans.append(new_fan)

			self.color = changeColor(self.color, -2)
			self.clock += 1

			yield self.speed  	# random time set in init function