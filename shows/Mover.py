from HelperFunctions import*

class Spiro(object):
	def __init__(self, sunflower_model, color, s, life):
		self.sunflower = sunflower_model
		self.s = s
		self.color = color
		self.pos = self.sunflower.get_rand_cell()
		self.dir = randDir()
		self.life = life

	def draw_spiro(self):
		self.sunflower.set_cell(meld(self.s, self.pos), wheel(self.color))

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
		          
	def next_frame(self):
		
		while (True):
			
			while len(self.spiros) < 9 or oneIn(10):
				new_spiro = Spiro(self.sunflower, randColorRange(self.color, 200), self.sunflower.rand_sun(), randint(24, 500))
				self.spiros.append(new_spiro)

			for s in self.spiros:
				s.draw_spiro()
				if s.move_spiro() == False:
					self.spiros.remove(s)
			
			if oneIn(10):
				self.color = randColorRange(self.color, 100)

			yield self.speed