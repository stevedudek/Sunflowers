from HelperClasses import*
from sunflower import NUM_SUNFLOWERS

class Ring(object):
	def __init__(self, sunflower_model):
		self.name = "Ring"        
		self.sunflower = sunflower_model
		self.speed = 0.05
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(5,10)
		self.ring_coeff = randint(4,10)
		self.bright = randint(0,2)
		self.faders = Faders(sunflower_model)
		self.arcs = []	# List that holds Arc objects 
		self.max_arcs = 20
	
	def draw_ring(self):
		for s in range(NUM_SUNFLOWERS):
			for y in range(self.sunflower.max_dist):
				for x in range(self.sunflower.num_spirals):
					color = changeColor(self.color, (x + s % self.color_grade) * self.color_inc)
					intense = (self.ring_coeff * 0.1) - (0.15 * ((self.sunflower.max_dist - y - 1) % 10))
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
			
			self.draw_ring()
			self.faders.cycle_faders(refresh=False)
			self.draw_arcs()
			self.move_arcs()

			if oneIn(10) or len(self.arcs) < self.max_arcs:
				new_arc = Arc(self.sunflower, randColorRange(self.color, 200), self.sunflower.rand_sun(),
							  randint(0, self.sunflower.num_spirals), plusORminus(), fade=0.2)
				self.arcs.append(new_arc)

			# Change it up!
			if oneIn(10):
				self.color_inc = upORdown(self.color_inc, 1, 20, 50)
			if oneIn(100):
				self.color_grade = upORdown(self.color_grade, 1, 5, 10)

			self.color = changeColor(self.color, 2)

			yield self.speed