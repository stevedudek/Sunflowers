from HelperClasses import*
from sunflower import NUM_SUNFLOWERS

class Arc(object):
	def __init__(self, sunflower_model, s, p, d, decay):
		self.sunflower = sunflower_model
		self.s = s
		self.p = p
		self.d = d
		self.decay = decay
		self.faders = Faders(sunflower_model)	# List that holds Fader objects
		self.direct = plusORminus()

	def move_and_draw(self, color):
		self.faders.cycle_faders(refresh=False)

		for i, leaf in enumerate(self.sunflower.get_fan_band(self.d, self.p)):
			self.faders.add_fader(changeColor(color, (i*4) + (self.d * 30)), meld(self.s, leaf), change=self.decay)

		self.d += 1
		self.p = (self.p + self.direct) % self.sunflower.num_spirals

		if self.d > (self.sunflower.max_dist * 2):
			self.faders.fade_all()
			return False

		return True
   
class WashingMachine(object):
	def __init__(self, sunflower_model):
		self.name = "WashingMachine"        
		self.sunflower = sunflower_model
		self.arcs = []	# List that holds Arc objects
		self.speed = 0.1
		self.color = randColor()
		          
	def next_frame(self):
		
		while (True):

			if len(self.arcs) < 3 or oneIn(20):
				for s in range(NUM_SUNFLOWERS):
					new_arc = Arc(self.sunflower, s, p=self.sunflower.rand_spiral(), d=0, decay=0.1)
					self.arcs.append(new_arc)

			self.sunflower.black_cells()	# Set background to black

			for a in self.arcs:
				if not a.move_and_draw(self.color):
					self.arcs.remove(a)

			self.color = randColorRange(self.color, 5)
			
			yield self.speed  	# random time set in init function