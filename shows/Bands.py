from HelperFunctions import*
from sunflower import NUM_SUNFLOWERS

class Band(object):
	def __init__(self, sunflower_model, s, dist, dir, color):
		self.sunflower = sunflower_model
		self.color = randColor()
		self.s = s
		self.p = 0
		self.d = dist
		self.dir = dir
		self.color = color
		self.grade = randint(10,30)
		self.fade = randint(10,20)
		self.speed = randint(1,6)
		self.time = 0
	
	def draw(self):
		for i in range(self.sunflower.get_num_spirals()):
			p = (self.sunflower.get_num_spirals() + self.p + (i * self.dir * -1)) % self.sunflower.get_num_spirals()
			color = changeColor(self.color, i * self.grade)
			intensity = 1.0 - (i * 1.0 / self.fade)
			if intensity < 0:
				intensity = 0

			self.sunflower.set_cell((self.s, p, self.d), gradient_wheel(color,intensity))
	
	def move(self):
		self.time += 1
		if self.time >= self.speed:
			self.time = 0
			self.p = (self.sunflower.get_num_spirals() + self.p + self.dir) % self.sunflower.get_num_spirals()
			self.color = changeColor(self.color,10)
			
			if oneIn(50):
				self.speed = upORdown(self.speed, 1, 1, 6)
			if oneIn(5):
				self.grade = upORdown(self.grade, 1, 5, 20)
			if oneIn(5):
				self.fade = upORdown(self.fade, 1, 10, 20)
	
class Bands(object):
	def __init__(self, sunflower_model):
		self.name = "Bands"        
		self.sunflower = sunflower_model
		self.speed = 0.1
		self.bands = []
		self.clock = 0
		self.color = randColor()
	
	def next_frame(self):
		for s in range(NUM_SUNFLOWERS):
			for d in range(self.sunflower.max_dist):
				dir = ((d%2)*2)-1 	# -1 or 1
				new_band = Band(self.sunflower, s, d, dir, self.color)
				self.bands.append(new_band)

		while (True):
			for b in self.bands:
				b.draw()
				b.move()

			self.color = changeColor(self.color, 10)
			self.clock += 1

			yield self.speed