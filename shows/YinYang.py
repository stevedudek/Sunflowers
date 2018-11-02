from HelperClasses import*
from sunflower import NUM_SUNFLOWERS

class Petal(object):
	def __init__(self, sunflower_model, color, s, p, d, direct, life, fade=0.1):
		self.sunflower = sunflower_model
		self.s = s
		self.p = p
		self.d = d
		self.color = color
		self.direct = direct	# 1 or -1
		self.life = life
		self.fade = fade

	def draw(self):
		return [Fader(self.sunflower, self.color, meld(self.s, c), change=self.fade)
				for c in self.sunflower.get_petal_shape(self.d, self.p)]
	
	def move(self):
		self.p = (self.p + self.direct + self.sunflower.get_num_spirals()) % self.sunflower.get_num_spirals()
		self.color = randColorRange(self.color, 10)
		self.life -= 1
		return self.life

	
class YinYang(object):
	def __init__(self, sunflower_model):
		self.name = "YinYang"
		self.sunflower = sunflower_model
		self.speed = 0.2
		self.color = randColor()
		self.color_inc = randint(10,20)
		self.clock = 0
		self.faders = Faders(sunflower_model)
		self.petals = []	# List that holds Petals objects
		self.max_petals = 10
		self.max_faders = 1000
	
	def draw_petals(self):
		for p in self.petals:
			for new_fader in p.draw():
				if self.faders.num_faders() < self.max_faders:
					self.faders.add_fader_obj(new_fader)

	def move_petals(self):
		for p in self.petals:
			if not p.move():
				self.petals.remove(p)

	def next_frame(self):
		
		while (True):

			# self.sunflower.black_cells()

			if not self.petals:
				self.color_inc = randint(10,20)
				life = randint(10,50)

				for p in self.sunflower.get_petal_sym(randint(2,4), self.clock % self.sunflower.get_num_spirals()):
					for s in range(NUM_SUNFLOWERS):

						direct = plusORminus()
						fade = 1.0 / (randint(2, 6) + s)
						color = randColorRange(self.color, 100)

						new_petal = Petal(self.sunflower, changeColor(color, self.color_inc), s, p, randint(3, self.sunflower.max_dist), direct, life, fade)
						self.petals.append(new_petal)

			self.faders.cycle_faders()
			self.draw_petals()
			self.move_petals()

			# Change it up!
			self.color = randColorRange(self.color, 50)

			self.clock += 1

			yield self.speed