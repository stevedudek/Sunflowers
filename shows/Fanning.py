from HelperClasses import *
from HelperFunctions import*

class Fan(object):
	def __init__(self, sunflower_model, color, s, petal, fade=0.1):
		self.sunflower = sunflower_model
		self.s = s
		self.color = color
		self.p = petal
		self.d = 0
		self.fade = fade
	
	def draw(self):
		return [Fader(self.sunflower, self.color, meld(self.s, coord), change=self.fade)
				for coord in self.sunflower.get_fan_band(self.d,self.p)]
	
	def move(self):
		self.d += 1
		return (self.d < self.sunflower.max_dist)

	
class Fanning(object):
	def __init__(self, sunflower_model):
		self.name = "Fanning"        
		self.sunflower = sunflower_model
		self.speed = 0.2 + (randint(0,3) * 0.1)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.clock = 0
		self.faders = Faders(self.sunflower)
		self.fans = []	# List that holds Fan objects 
		self.max_fans = 12
	
	def draw_fans(self):
		for a in self.fans:
			for fan in a.draw():
				self.faders.add_fader_obj(fan)

	def move_fans(self):
		for a in self.fans:
			if not a.move():
				self.fans.remove(a)

	def next_frame(self):
		
		while (True):
			
			self.faders.cycle_faders()
			self.draw_fans()
			self.move_fans()

			if len(self.fans) < self.max_fans:
				new_fan = Fan(self.sunflower, randColorRange(self.color, 100),
							  self.sunflower.rand_sun(), randint(0, self.sunflower.num_spirals), 0.3)
				self.fans.append(new_fan)

			self.color = changeColor(self.color, -2)
			self.clock += 1

			yield self.speed  	# random time set in init function