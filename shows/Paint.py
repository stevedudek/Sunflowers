from HelperClasses import*
	
class Paint(object):
	def __init__(self, sunflower_model):
		self.name = "Paint"        
		self.sunflower = sunflower_model
		self.speed = 0.05
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.faders = Faders(self.sunflower)
		self.arcs = []	# List that holds Arc objects
		self.fans = []	# List that holds Fan objects
		self.max_arcs = 30
		self.dir = 1 	# 1 or -1 for increasing or decreasing
	
	def draw_arcs(self):
		for a in self.arcs:
			self.faders.add_fader_obj(a.draw())

	def move_arcs(self):
		for a in self.arcs:
			if not a.move():
				new_petal = upORdown(a.get_petal(), 1, 0, self.sunflower.num_spirals - 1)
				new_fan = Fan(self.sunflower, changeColor(a.get_color(),300), a.s, new_petal)
				self.fans.append(new_fan)
				self.arcs.remove(a)

	def draw_fans(self):
		for f in self.fans:
			for fader_obj in f.draw():
				self.faders.add_fader_obj(fader_obj)

	def move_fans(self):
		for f in self.fans:
			if not f.move():
				if self.dir == 1:
					tips = f.get_fan_tips()
					new_arc = Arc(self.sunflower, changeColor(f.get_color(),-250), f.s, tips[0], 1)
					self.arcs.append(new_arc)
					new_arc = Arc(self.sunflower, changeColor(f.get_color(),-250), f.s, tips[1], -1)
					self.arcs.append(new_arc)
					if len(self.arcs) > self.max_arcs:
						self.dir = -1	 
				self.fans.remove(f)

	def next_frame(self):

		while (True):
			
			if len(self.fans) < 4:
				new_fan = Fan(self.sunflower, self.color, self.sunflower.rand_sun(), randint(0, self.sunflower.num_spirals))
				self.fans.append(new_fan)
				self.dir = 1

			self.faders.cycle_faders(refresh=True)
			self.draw_arcs()
			self.draw_fans()
			self.move_arcs()
			self.move_fans()

			self.color = changeColor(self.color, -2)

			yield self.speed  	# random time set in init function