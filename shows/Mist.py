from random import random, randint, choice

from HelperFunctions import*

class Arc(object):
	def __init__(self, rosemodel, color, petal, dir):
		self.rose = rosemodel
		self.color = color
		self.p = petal
		self.d = 5
		self.dir = dir
	
	def draw(self):
		if randint(1,100) > 10:
			self.rose.set_cell(get_coord((self.p,self.d)), wheel(self.color))
	
	def move(self):
		self.d += self.dir
		return (self.d >= 0 and self.d <= 10)

	def get_petal(self):
		return self.p

	def get_color(self):
		return self.color

class Fan(object):
	def __init__(self, rosemodel, color, petal):
		self.rose = rosemodel
		self.color = color
		self.p = petal
		self.d = 0
		self.dir = 1
	
	def draw(self):
		for i,cell in enumerate(get_fan_band(self.d, self.p)):
			if randint(1,100) > 50:
				color = changeColor(self.color, i * -5)
				self.rose.set_cell(cell, wheel(color))
	
	def move(self):
		self.d += self.dir
		return self.d <= 5

	def get_fan_tips(self):
		cells = get_fan_band(5, self.p)
		(p0,d0) = cells[0]
		(px,dx) = cells[-1]
		return [p0,px]

	def get_color(self):
		return self.color
	
class Mist(object):
	def __init__(self, rosemodel):
		self.name = "Mist"        
		self.rose = rosemodel
		self.speed = 0.2 + (randint(0,8) * 0.05)
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.clock = 0
		self.arcs = []	# List that holds Arc objects
		self.fans = []	# List that holds Fan objects
		self.max_arcs = 16
		self.dir = 1 	# 1 or -1 for increasing or decreasing
	
	def draw_arcs(self):
		for a in self.arcs:
			a.draw()

	def move_arcs(self):
		for a in self.arcs:
			if not a.move():
				new_petal = upORdown(a.get_petal(),1,0,maxPetal-1)
				new_fan = Fan(self.rose, changeColor(a.get_color(),10), new_petal)
				self.fans.append(new_fan)
				self.arcs.remove(a)

	def draw_fans(self):
		for f in self.fans:
			f.draw()

	def move_fans(self):
		for f in self.fans:
			if not f.move():
				if self.dir == 1:
					tips = f.get_fan_tips()
					new_arc = Arc(self.rose, changeColor(f.get_color(),20), tips[0], 1)
					self.arcs.append(new_arc)
					new_arc = Arc(self.rose, changeColor(f.get_color(),20), tips[1], -1)
					self.arcs.append(new_arc)
					if len(self.arcs) > self.max_arcs:
						self.dir = -1	 
				self.fans.remove(f)

	def next_frame(self):

		while (True):
			
			self.rose.set_all_cells((0,0,0))

			if len(self.fans) == 0:
				new_fan = Fan(self.rose, self.color, randint(0,maxPetal))
				self.fans.append(new_fan)
				self.dir = 1

			self.draw_arcs()
			self.draw_fans()
			self.move_arcs()
			self.move_fans()

			self.color = changeColor(self.color, -2)
			self.clock += 1

			yield self.speed  	# random time set in init function