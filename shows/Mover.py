from HelperClasses import*

class Spiro(object):
	def __init__(self, sunflower_model, color):
		self.sunflower = sunflower_model
		self.s = self.sunflower.rand_sun()
		self.color = color
		self.pos = self.sunflower.get_rand_cell()
		self.dir = randDir()
		self.life = randint(20, 50)
		self.change = 1.0 / 100

	def draw_spiro(self):
		return Fader(self.sunflower, self.color, meld(self.s, self.pos), change=self.change)

	def move_spiro(self):			
		self.pos = self.sunflower.petal_in_direction(self.pos, self.dir, 1)
		self.color = randColorRange(self.color, 20)
		self.life -= 1
		return self.life > 0

class Mover(object):
	def __init__(self, sunflower_model):
		self.name = "Mover"        
		self.sunflower = sunflower_model
		self.color = randColor()
		self.speed = 0.2
		self.spiros = []
		self.faders = Faders(sunflower_model)
		          
	def next_frame(self):
		
		while (True):
			
			while len(self.spiros) < 9 or oneIn(10):
				new_spiro = Spiro(self.sunflower,
								  randColorRange(self.color, 200))
				self.spiros.append(new_spiro)

			for s in self.spiros:
				self.faders.add_fader_obj(s.draw_spiro())
				if s.move_spiro() == False:
					self.spiros.remove(s)

			self.faders.cycle_faders(refresh=False)

			if oneIn(10):
				self.color = randColorRange(self.color, 100)

			yield self.speed