from HelperClasses import*
from sunflower import NUM_LEDS

class Sparkles(object):
	def __init__(self, sunflower_model):
		self.name = "Sparkles"        
		self.sunflower = sunflower_model
		self.faders = Faders(sunflower_model)
		self.speed = 0.2
		self.color = randColor()
		self.age = 0.1
		self.clock = 0
	
	def next_frame(self):

		self.sunflower.clear()

		while (True):

			self.faders.add_fader(randColorRange(self.color, 30),
								  meld(self.sunflower.rand_sun(), self.sunflower.get_rand_cell()),
								  change=randint(1,6) / 30.0, intense=0.1, growing=True)
			self.faders.cycle_faders()
			
			self.color = randColorRange(self.color, 50)

			yield self.speed  	# random time set in init function