from HelperFunctions import*
from sunflower import NUM_SUNFLOWERS
	
class Twist(object):
	def __init__(self, sunflower_model):
		self.name = "Twist"        
		self.sunflower = sunflower_model
		self.speed = 0.06
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.ring = randint(0,5)
		self.color_speed = randint(10,24)
		self.color_grade = randint(2,8)
		self.clock = 0

	
	def draw_ring(self):
		for s in range(NUM_SUNFLOWERS):
			for y in range(self.sunflower.max_dist -1, self.ring, -1):
				for x in range(self.sunflower.num_spirals):
					color = changeColor(self.color, (x % self.color_grade) * self.color_inc)
					intense = 1.0 - (0.2 * (((self.sunflower.max_dist - y - 1) + ((self.clock + x) % self.color_speed)) % 10))
					self.sunflower.set_cell((s,x,y), gradient_wheel(color, intense))

	def draw_sun(self):
		for s in range(NUM_SUNFLOWERS):
			for y in range(self.ring):
				for x in range(self.sunflower.num_spirals):
					color = changeColor(self.color, (x % self.color_grade) * self.color_inc)
					intense = 1.0 - (0.2 * ((y + s + ((self.clock + x) % self.color_speed)) % (self.color_inc / 2)))
					self.sunflower.set_cell((s, (x+(3*s)) % self.sunflower.num_spirals, y), gradient_wheel(color, intense))


	def next_frame(self):
		
		while (True):
			
			self.draw_ring()
			self.draw_sun()

			# Change it up!
			if oneIn(40):
				self.ring = upORdown(self.ring, 1, 1, 5)
			if oneIn(4):
				self.color_inc = upORdown(self.color_inc, 2, 20, 50)
			if oneIn(100):
				self.color_grade = upORdown(self.color_grade, 1, 2, 8)


			# Add a decrease color function
			self.color = changeColor(self.color, 2)
			self.clock += 1

			yield self.speed  	# random time set in init function