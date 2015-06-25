from random import random, randint, choice

from HelperFunctions import*

class Band(object):
	def __init__(self, rosemodel, dist, dir):
		self.rose = rosemodel
		self.color = randColor()
		self.p = 0
		self.d = dist
		self.dir = dir
		self.grade = randint(5,20)
		self.fade = randint(10,20)
		self.speed = randint(1,6)
		self.time = 0
	
	def draw(self):
		for i in range(maxPetal):
			p = (maxPetal + self.p + (i * self.dir * -1)) % maxPetal
			color = changeColor(self.color, i * self.grade)
			intensity = 1.0 - (i * 1.0 / self.fade)
			if intensity < 0:
				intensity = 0

			self.rose.set_cell((p,self.d), gradient_wheel(color,intensity))
	
	def move(self):
		self.time += 1
		if self.time >= self.speed:
			self.time = 0
			self.p = (maxPetal + self.p + self.dir) % maxPetal
			self.color = changeColor(self.color,10)
			
			if oneIn(50):
				self.speed = upORdown(self.speed, 1, 1, 6)
			if oneIn(5):
				self.grade = upORdown(self.grade, 1, 5, 20)
			if oneIn(5):
				self.fade = upORdown(self.fade, 1, 10, 20)
	
class Bands(object):
	def __init__(self, rosemodel):
		self.name = "Bands"        
		self.rose = rosemodel
		self.speed = 0.1
		self.bands = []
		self.clock = 0
	
	def next_frame(self):
		
		for d in range(maxDistance):
			dir = ((d%2)*2)-1 	# -1 or 1
			new_band = Band(self.rose, d, dir)
			self.bands.append(new_band)

		while (True):
			for b in self.bands:
				b.draw()
				b.move()

			self.clock += 1

			yield self.speed