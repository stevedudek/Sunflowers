from random import random, randint, choice
from HelperFunctions import*

class Fader(object):
	def __init__(self, sunflower_model, color, s):
		self.sunflower = sunflower_model
		self.s = s
		self.pos = self.sunflower.get_rand_cell()
		self.color = color
		self.life = randint(20,100)
	
	def draw(self):
		self.sunflower.set_cell(meld(self.s, self.pos), wheel(self.color))
	
	def move(self):
		self.black()
		self.pos = choice(self.sunflower.neighbors(self.pos))
		self.draw()
		self.life -= 1
		return self.life > 0

	def rotate(self):
		(p, d) = self.pos
		self.pos = (p + 1, d)
		self.draw()

	def rotate_blacken(self, turn):
		(p,d) = self.pos
		self.sunflower.black_cell(meld(self.s, (p + turn, d)))

	def black(self):
		self.sunflower.black_cell(meld(self.s, self.pos))

class Firefly(object):
	def __init__(self, sunflower_model):
		self.name = "Firefly"        
		self.sunflower = sunflower_model
		self.speed = 0.1
		self.color = randColor()
		self.color_inc = randint(50,100)
		self.faders = []	# List that holds Fader objects
		self.max_faders = randint(15,150)
		self.rotate_max = 0
		self.rotate_life = 0
	
	def draw_faders(self):
		for f in self.faders:
			if not f.move():
				f.black()
				self.faders.remove(f)

	def rotate_faders(self):
		if self.rotate_life > 0:
			for f in self.faders:
				f.rotate()
			self.rotate_life -= 1
			if self.rotate_life == 0:
				self.rotate_life = self.rotate_max * -1

		elif self.rotate_life < 0:
			for f in self.faders:
				f.rotate_blacken(self.rotate_life)
		 	self.rotate_life += 1

	def next_frame(self):
		
		while (True):
			
			if len(self.faders) < self.max_faders:
				new_fader = Fader(self.sunflower, randColorRange(self.color, self.color_inc), self.sunflower.rand_sun())
				self.faders.append(new_fader)

			if self.rotate_life:
				self.rotate_faders()
			else:
				self.draw_faders()

			if not self.rotate_life and oneIn(25):
				self.rotate_max = randint(6, max(self.sunflower.num_spirals, 7))
				self.rotate_life = self.rotate_max

			if oneIn(50):
				self.color = changeColor(self.color, self.color_inc)

			yield self.speed