from HelperClasses import*
from sunflower import NUM_SUNFLOWERS
           
class ContraRotater(object):
	def __init__(self, sunflower_model):
		self.name = "ContraRotater"        
		self.sunflower = sunflower_model
		self.faders = Faders(self.sunflower, max_faders=3000)
		self.speed = 0.3
		self.color = randColor()
		self.trail = 0.5
		self.symm = 1
		self.clock = 0
		          
	def next_frame(self):
		
		while (True):
			
			self.sunflower.black_cells()
			
			# Create new faders
			for s in range(NUM_SUNFLOWERS):
				for p in range(self.sunflower.num_spirals):
					for d in range(self.sunflower.max_dist):
						if p % (self.sunflower.num_spirals / self.symm) == self.clock % (self.sunflower.num_spirals / self.symm):
							self.faders.add_fader(self.color, (s, self.sunflower.num_spirals - p - 1, d), change=self.trail)
							self.faders.add_fader(changeColor(self.color, (self.clock * 10)), (s, p, d), change=self.trail)
			
			self.faders.cycle_faders()	# Draw the Faders

			# Change the colors and symmetry
			
			self.color = randColorRange(self.color, 5)
			
			if oneIn(50):
				self.symm = upORdown(self.symm, 1, 1, 4)

			self.clock += 1

			yield self.speed