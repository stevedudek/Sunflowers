from HelperClasses import*
from sunflower import NUM_LEDS

class Sparkles(object):
	def __init__(self, sunflower_model):
		self.name = "Sparkles"        
		self.sunflower = sunflower_model
		self.faders = Faders(sunflower_model)
		self.speed = 0.2
		self.color = randColor()
		self.sparkle_perc = 10
		self.spark_num = 3 * NUM_LEDS * self.sparkle_perc / 100
		self.age = 0.1
		self.clock = 0
	
	def next_frame(self):

		self.sunflower.clear()

		while (True):

			if self.faders.num_faders() < self.spark_num:
				for i in range(2):
					self.faders.add_fader(randColorRange(self.color, 30),
										  meld(self.sunflower.rand_sun(), self.sunflower.get_rand_cell()),
										  change=randint(1,6) / 30.0, intense=0, growing=True)
			self.faders.cycle_faders()
			
			if oneIn(100):
				self.color = randColorRange(self.color, 30)
			
			yield self.speed  	# random time set in init function