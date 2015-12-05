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
		self.rose.set_cell(self.pos, wheel(self.color), self.r)
		# self.rose.set_cell(self.pos, gradient_wheel(self.color, self.life), self.r)
	
	def fade(self):
		self.life -= self.decay
		return (self.life >= 0)

class Petal(object):
	def __init__(self, rosemodel, color, r, p, d, dir, life, fade=0.1):
		self.rose = rosemodel
		self.r = r
		self.p = p
		self.d = d
		self.color = color
		self.dir = dir	# 1 or -1
		self.life = life
		self.fade = fade

	def draw(self):
		return [Fader(self.rose, self.color, self.r, c, self.fade) for c in get_petal_shape(self.d, self.p)]
	
	def move(self):
		self.p = (self.p + self.dir + maxPetal) % maxPetal
		self.color = randColorRange(self.color, 10)
		self.life -= 1
		return self.life

	
class YinYang(object):
	def __init__(self, rosemodel):
		self.name = "YinYang"
		self.rose = rosemodel
		self.speed = 0.2
		self.color = randColor()
		self.color_inc = randint(10,20)
		self.clock = 0
		self.faders = []	# List that holds Fader objects
		self.petals = []	# List that holds Petals objects
		self.max_arcs = 18
	
	def draw_faders(self):
		for f in reversed(self.faders):
			f.draw()
			if not f.fade():
				self.faders.remove(f)

	def draw_petals(self):
		for p in self.petals:
			self.faders += p.draw()

	def move_petals(self):
		for p in self.petals:
			if not p.move():
				self.petals.remove(p)

	def next_frame(self):
		
		while (True):

			# Set background to black
			# self.rose.set_all_cells((0,0,0))

			if not self.petals:
				self.color_inc = randint(10,20)
				life = randint(50,200)

				for r in range(maxRose):
					dir = plusORminus()
					fade = (randint(2,6)+r) / 0.1
					color = self.color

					for p in get_petal_sym(0, r + self.clock % maxPetal):
						new_petal = Petal(self.rose, color, r, p, randint(3,maxDistance), dir, life, fade)
						self.petals.append(new_petal)
						color = changeColor(color, self.color_inc)

			self.draw_faders()
			self.draw_petals()
			self.move_petals()

			# Change it up!
			if oneIn(10):
				self.color = randColorRange(self.color, 20)

			self.clock += 1

			yield self.speed