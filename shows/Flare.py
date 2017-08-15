from HelperClasses import*
from sunflower import NUM_SUNFLOWERS

class Arc(object):
	def __init__(self, sunflower_model, color, s, p, dir, fade=0.1):
		self.sunflower = sunflower_model
		self.color = color
		self.s = s
		self.p = p
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

	
class Flare(object):
	def __init__(self, sunflower_model):
		self.name = "Flare"        
		self.sunflower = sunflower_model
		self.speed = 0.1 + (randint(1,5) * 0.1)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.bright = randint(0,2)
		self.faders = Faders(sunflower_model)
		self.arcs = []	# List that holds Arc objects 
		self.max_arcs = 15
	
	def draw_sun(self):
		for s in range(NUM_SUNFLOWERS):
			for y in range(self.sunflower.max_dist):
				for x in range(self.sunflower.num_spirals):
					color = changeColor(self.color, (x % self.color_grade) * ((s+1) * self.color_inc))
					intense = 1.0 - (float(y) / self.sunflower.max_dist)
					self.sunflower.set_cell((s,x,y), gradient_wheel(color, intense))

	def draw_arcs(self):
		for a in self.arcs:
			self.faders.add_fader_obj(a.draw())

	def move_arcs(self):
		for a in self.arcs:
			if not a.move():
				self.arcs.remove(a)

	def next_frame(self):
		
		while (True):
			
			self.draw_sun()
			self.faders.cycle_faders(refresh=False)
			self.draw_arcs()
			self.move_arcs()

			if oneIn(10) and len(self.arcs) < self.max_arcs:
				new_arc = Arc(self.sunflower, randColorRange(self.color, 200), self.sunflower.rand_sun(),
							  randint(0, self.sunflower.num_spirals), plusORminus())
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

			yield self.speed  	# random time set in init function