from random import random, randint, choice

from HelperFunctions import*

class Fader(object):
	def __init__(self, rosemodel, color, r, pos, decay, death):
		self.rose = rosemodel
		self.r = r
		self.pos = pos
		self.color = color
		self.decay = decay
		self.life = 1.0
		self.death = death	# Fader doesn't go completely black
	
	def draw(self):
		self.rose.set_cell(self.pos, gradient_wheel(self.color, self.life), self.r)
	
	def fade(self):
		self.life -= self.decay
		return (self.life >= self.death)

class Arc(object):
	def __init__(self, rosemodel, color, r, petal, dir, fade=0.1, death=0.2):
		self.rose = rosemodel
		self.r = r
		self.color = color
		self.p = petal
		self.d = 5
		self.dir = dir
		self.fade = fade
		self.death = death
	
	def draw(self):
		new_fader = Fader(self.rose, self.color, self.r, get_coord((self.p,self.d)), self.fade, self.death)
		return new_fader
	
	def move(self):
		self.d += self.dir
		return (self.d >= 0 and self.d <= 10)

	def get_petal(self):
		return self.p

	def get_color(self):
		return self.color

class Fan(object):
	def __init__(self, rosemodel, color, r, petal, fade=0.1, death=0.2):
		self.rose = rosemodel
		self.r = r
		self.color = color
		self.p = petal
		self.d = 0
		self.dir = 1
		self.fade = fade
		self.death = death
	
	def draw(self):
		faders = []
		for i,cell in enumerate(get_fan_band(self.d, self.p)):
			color = changeColor(self.color, i * -5)
			new_fader = Fader(self.rose, color, self.r, cell, self.fade, self.death)
			faders.append(new_fader)
		return faders
	
	def move(self):
		self.d += self.dir
		return self.d <= 5

	def get_fan_tips(self):
		cells = get_fan_band(5, self.p)
		(p0,d0) = cells[0]
		(px,dx) = cells[-1]
		return [p0,px]

	def get_color(self):
		return self.color
	
class Paint(object):
	def __init__(self, rosemodel):
		self.name = "Paint"        
		self.rose = rosemodel
		self.speed = 0.2
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.clock = 0
		self.faders = []	# List that holds Fader objects
		self.arcs = []	# List that holds Arc objects
		self.fans = []	# List that holds Fan objects
		self.max_arcs = 30
		self.dir = 1 	# 1 or -1 for increasing or decreasing
	
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
				new_petal = upORdown(a.get_petal(),1,0,maxPetal-1)
				new_fan = Fan(self.rose, changeColor(a.get_color(),300), a.r, new_petal)
				self.fans.append(new_fan)
				self.arcs.remove(a)

	def draw_fans(self):
		for f in self.fans:
			for cell in f.draw():
				self.faders.append(cell)

	def move_fans(self):
		for f in self.fans:
			if not f.move():
				if self.dir == 1:
					tips = f.get_fan_tips()
					new_arc = Arc(self.rose, changeColor(f.get_color(),-250), f.r, tips[0], 1)
					self.arcs.append(new_arc)
					new_arc = Arc(self.rose, changeColor(f.get_color(),-250), f.r, tips[1], -1)
					self.arcs.append(new_arc)
					if len(self.arcs) > self.max_arcs:
						self.dir = -1	 
				self.fans.remove(f)

	def next_frame(self):

		while (True):
			
			if len(self.fans) < 2:
				new_fan = Fan(self.rose, self.color, randRose(), randint(0,maxPetal))
				self.fans.append(new_fan)
				self.dir = 1

			self.draw_faders()
			self.draw_arcs()
			self.draw_fans()
			self.move_arcs()
			self.move_fans()

			self.color = changeColor(self.color, -2)
			self.clock += 1

			yield self.speed  	# random time set in init function