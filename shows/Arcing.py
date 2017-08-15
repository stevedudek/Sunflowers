from HelperClasses import *

class Arc(object):
	def __init__(self, sunflower_model, color, s, p, d, dir, fade):
		self.sunflower = sunflower_model
		self.color = color
		self.s = s
		self.p = p
		self.d = d	# 1 or -1
		self.dir = dir
		self.fade = fade
		if self.dir == 1:
			self.d = 0
		else:
			self.d = (self.sunflower.max_dist - 1) * 2

	def draw(self):
		return Fader(self.sunflower, self.color, (self.s, self.p, self.d), change=self.fade)
	
	def move(self):
		self.d += self.dir
		return self.d >= 0 and self.d <= (self.sunflower.max_dist - 1) * 2

	
class Arcing(object):
	def __init__(self, sunflower_model):
		self.name = "Arcing"        
		self.sunflower = sunflower_model
		self.sunflower.set_random_family()
		self.speed = 0.1 #0.2 + (randint(0,3) * 0.1)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.clock = 0
		self.faders = Faders(sunflower_model)
		self.arcs = []	# List that holds Arc objects
		self.fade_amount = randint(5,20)
		self.max_arcs = 50
	
	def draw_arcs(self):
		for a in self.arcs:
			self.faders.add_fader_obj(a.draw())

	def move_arcs(self):
		for a in self.arcs:
			if not a.move():
				self.arcs.remove(a)

	def next_frame(self):
		
		while (True):
			
			self.faders.cycle_faders()
			self.draw_arcs()
			self.move_arcs()

			if len(self.arcs) < self.max_arcs:
				new_arc = Arc(self.sunflower, randColorRange(self.color, 100),
							  self.sunflower.rand_sun(), self.sunflower.rand_spiral(), self.sunflower.rand_dist(),
							  plusORminus(), 1.0 / self.fade_amount)
				self.arcs.append(new_arc)

			# self.color = changeColor(self.color, -2)
			self.clock += 1

			if oneIn(50):
				self.fade_amount = upORdown(self.fade_amount, 1, 4, 20)

			yield self.speed  	# random time set in init function