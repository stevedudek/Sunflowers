from HelperClasses import*

class Arc(object):
	def __init__(self, sunflower_model, color, s, pos):
		self.sunflower = sunflower_model
		self.color = color
		self.s = s
		self.p, self.d = pos
		self.direct = -1
	
	def draw(self):
		return Fader(self.sunflower, self.color, meld(self.s, (self.p,self.d)))

	def move(self):
		self.d += self.direct
		return self.d >= 0 and self.d <= self.sunflower.max_dist - 2

	def get_color(self):
		return self.color

class Fan(object):
	def __init__(self, sunflower_model, color, s, p):
		self.sunflower = sunflower_model
		self.color = color
		self.s = s
		self.p = p
		self.d = 0
		self.direct = 1
	
	def draw(self):
		faders = []
		for i, cell in enumerate(self.sunflower.get_fan_band(self.d, self.p)):
			faders.append(Fader(self.sunflower, self.color, meld(self.s, cell)))
		return faders

	def move(self):
		self.d += self.direct
		return self.d <= self.sunflower.max_dist - 1

	def get_fan_tips(self):
		cells = self.sunflower.get_fan_band(self.sunflower.max_dist - 1, self.p)
		return cells[0], cells[-1]

	def get_color(self):
		return self.color
	
class Mist(object):
	def __init__(self, sunflower_model):
		self.name = "Mist"        
		self.sunflower = sunflower_model
		self.speed = 0.05 + (randint(0,8) * 0.05)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.arcs = []	# List that holds Arc objects
		self.fans = []	# List that holds Fan objects
		self.faders = Faders(self.sunflower)
		self.max_arcs = 48
		self.direct = 1 	# 1 or -1 for increasing or decreasing
	
	def draw_arcs(self):
		self.add_faders([a.draw() for a in self.arcs])

	def move_arcs(self):
		for a in self.arcs:
			if not a.move():
				new_fan = Fan(self.sunflower, changeColor(a.get_color(), 40), a.s, a.p)
				self.fans.append(new_fan)
				self.arcs.remove(a)

	def draw_fans(self):
		self.add_faders(sum([f.draw() for f in self.fans], []))

	def move_fans(self):
		for f in self.fans:
			if not f.move():
				if self.direct == 1:
					tips_a, tips_b = f.get_fan_tips()
					new_arc = Arc(self.sunflower, changeColor(f.get_color(), 60), f.s, tips_a)
					if len(self.arcs) < self.max_arcs:
						self.arcs.append(new_arc)
					new_arc = Arc(self.sunflower, changeColor(f.get_color(), 60), f.s, tips_b)
					if len(self.arcs) < self.max_arcs:
						self.arcs.append(new_arc)
				self.fans.remove(f)

	def add_faders(self, faders):
		[self.faders.add_fader_obj(fader) for fader in faders if fader is not None]

	def next_frame(self):

		while (True):
			
			self.sunflower.black_cells()

			while len(self.fans) < 6:
				new_fan = Fan(self.sunflower,
							  randColorRange(self.color, 100),
							  self.sunflower.rand_sun(),
							  randint(0, self.sunflower.num_spirals))
				self.fans.append(new_fan)
				self.direct = 1

			self.faders.cycle_faders()  # Draw the Faders

			self.draw_arcs()
			self.draw_fans()
			self.move_arcs()
			self.move_fans()

			self.color = changeColor(self.color, -2)

			yield self.speed  	# random time set in init function