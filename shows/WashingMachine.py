from HelperClasses import*

class WashingMachine(object):
	def __init__(self, sunflower_model):
		self.name = "WashingMachine"        
		self.sunflower = sunflower_model
		self.arcs = []
		self.faders = Faders(self.sunflower)
		self.speed = 0.1
		self.color = randColor()
		          
	def next_frame(self):
		
		while (True):

			if len(self.arcs) < 5 or oneIn(20):
				for s in range(self.sunflower.num_sunflowers):
					new_arc = Arc(sunflower_model=self.sunflower,
								  color=self.color, s=s, p=self.sunflower.rand_spiral(),
								  direct=-1, fade=0.1, death=1.5)
					self.arcs.append(new_arc)

			self.faders.cycle_faders(refresh=True)

			for a in reversed(self.arcs):
				self.faders.add_fader_obj(a.draw())
				if not a.move():
					self.arcs.remove(a)

			self.color = randColorRange(self.color, 5)
			
			yield self.speed  	# random time set in init function