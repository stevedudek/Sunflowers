from HelperClasses import*
from sunflower import NUM_SUNFLOWERS

class Arc(object):
	def __init__(self, sunflower_model, color, s, p, dir, fade=0.25):
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
		return self.d >= 0 and self.d <= (self.sunflower.max_dist - 1) * 4

	
class Flare(object):
	def __init__(self, sunflower_model):
		self.name = "Flare"        
		self.sunflower = sunflower_model
		self.speed = randint(1,5) * 0.05
		self.sun_color = randColor()
		self.arc_color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,5) * 0.1
		self.color_grade = randint(2,8)
		self.faders = Faders(sunflower_model)
		self.arcs = []	# List that holds Arc objects 
		self.max_arcs = 12
	
	def draw_sun(self):
		for s in range(NUM_SUNFLOWERS):
			for y in range(self.sunflower.max_dist):
				for x in range(self.sunflower.num_spirals):
					color = changeColor(self.sun_color, (x % self.color_grade) * ((s+1) * self.color_inc))
					intense = 0.05 * (1.0 - (float(y) / self.sunflower.max_dist))
					self.sunflower.set_cell((s,x,y), gradient_wheel(color, intense))

	def draw_arcs(self):
		for a in reversed(self.arcs):
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

			if len(self.arcs) < self.max_arcs:
				new_arc = Arc(self.sunflower, randColorRange(self.arc_color, 300), self.sunflower.rand_sun(),
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
			self.sun_color = changeColor(self.sun_color, 5)
			self.arc_color = changeColor(self.arc_color, -10)

			yield self.speed  	# random time set in init function