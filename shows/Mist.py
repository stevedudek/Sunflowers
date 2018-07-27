from HelperFunctions import*

class Arc(object):
	def __init__(self, sunflower_model, color, s, p, d):
		self.sunflower = sunflower_model
		self.color = color
		self.s = s
		self.p = p
		self.d = d
		self.direct = 1
	
	def draw(self):
		if randint(1,100) > 10:
			self.sunflower.set_cell(meld(self.s, (self.p,self.d)), wheel(self.color))
	
	def move(self):
		self.d += self.direct
		return self.d >= 0 and self.d <= self.sunflower.max_dist - 2

	def get_petal(self):
		return self.p

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
		for i, cell in enumerate(self.sunflower.get_fan_band(self.d, self.p)):
			if randint(1,100) > 50:
				color = changeColor(self.color, i * -5)
				self.sunflower.set_cell(meld(self.s, cell), wheel(color))
	
	def move(self):
		self.d += self.direct
		return self.d <= self.sunflower.max_dist - 1

	def get_fan_tips(self):
		cells = self.sunflower.get_fan_band(self.sunflower.max_dist - 1, self.p)
		(p0,d0) = cells[0]
		(px,dx) = cells[-1]
		return [p0,px]

	def get_color(self):
		return self.color
	
class Mist(object):
	def __init__(self, sunflower_model):
		self.name = "Mist"        
		self.sunflower = sunflower_model
		self.speed = 0.2 + (randint(0,8) * 0.05)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.arcs = []	# List that holds Arc objects
		self.fans = []	# List that holds Fan objects
		self.max_arcs = 48
		self.direct = 1 	# 1 or -1 for increasing or decreasing
	
	def draw_arcs(self):
		for a in self.arcs:
			a.draw()

	def move_arcs(self):
		for a in self.arcs:
			if not a.move():
				new_petal = upORdown(a.get_petal(), 1, 0, self.sunflower.get_num_spirals() - 1)
				new_fan = Fan(self.sunflower, changeColor(a.get_color(), 40), a.s, new_petal)
				self.fans.append(new_fan)
				self.arcs.remove(a)

	def draw_fans(self):
		for f in self.fans:
			f.draw()

	def move_fans(self):
		for f in self.fans:
			if not f.move():
				if self.direct == 1:
					tips = f.get_fan_tips()
					new_arc = Arc(self.sunflower, changeColor(f.get_color(), 60), f.s, tips[0], 1)
					self.arcs.append(new_arc)
					new_arc = Arc(self.sunflower, changeColor(f.get_color(), 60), f.s, tips[1], -1)
					self.arcs.append(new_arc)
					if len(self.arcs) > self.max_arcs:
						self.direct = -1	 
				self.fans.remove(f)

	def next_frame(self):

		while (True):
			
			self.sunflower.black_cells()

			while len(self.fans) < 6:
				new_fan = Fan(self.sunflower, randColorRange(self.color, 100), self.sunflower.rand_sun(), randint(0, self.sunflower.get_num_spirals()))
				self.fans.append(new_fan)
				self.direct = 1

			self.draw_arcs()
			self.draw_fans()
			self.move_arcs()
			self.move_fans()

			self.color = changeColor(self.color, -2)

			yield self.speed  	# random time set in init function