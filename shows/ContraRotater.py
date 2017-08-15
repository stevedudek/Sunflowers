from HelperClasses import*
from sunflower import NUM_SUNFLOWERS
           
class ContraRotater(object):
	def __init__(self, sunflower_model):
		self.name = "ContraRotater"        
		self.sunflower = sunflower_model
		self.faders = Faders(self.sunflower)
		self.speed = 0.5
		self.color = randColor()
		self.trail = 0.2
		self.symm = 1
		self.clock = 0
		          
	def next_frame(self):
		
		while (True):
			
			self.sunflower.black_cells()
			
			# Create new faders
			for s in range(NUM_SUNFLOWERS):
				for p in range(self.sunflower.num_spirals):
					for d in range(self.sunflower.max_dist):
						if (p+s) % (self.sunflower.num_spirals / (self.symm + s)) == self.clock % (self.sunflower.num_spirals / self.symm):
							if (d+s) % 2 == 0:
								new_p = self.sunflower.num_spirals - p - 1
							else:
								new_p = p

							self.faders.add_fader(self.color, (s, new_p, d), change=self.trail)
			
			self.faders.cycle_faders()	# Draw the Faders
			
			# Change the colors and symmetry
			
			self.color = randColorRange(self.color, 5)
			
			if oneIn(20):
				self.trail = inc(self.trail, 0.1, 0.1, 0.5) 

			if oneIn(50):
				self.symm = inc(self.symm, 1, 1, 7)

			self.clock += 1

			yield self.speed