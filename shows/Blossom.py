from sunflower import NUM_SUNFLOWERS
from HelperFunctions import*
	
class Blossom(object):
	def __init__(self, sunflower_model):
		self.name = "Blossom"        
		self.sunflower = sunflower_model
		self.speed = 0.1
		self.color = randColor()
		self.color_inc = randint(20,50)
		self.color_speed = randint(1,4)
		self.color_grade = randint(2,8)
		self.color_decay = 2
		self.grow = True
		self.clock = 0
		self.bright = False
		          
	def next_frame(self):
		
		while (True):

			for s in range(NUM_SUNFLOWERS):
				for y in range(self.sunflower.max_dist):
					for x in range(self.sunflower.num_spirals):
						color = changeColor(self.color, ((x + s) % self.color_grade) * self.color_inc)
						intense = 1.0 - ((y + s) * self.color_decay / 40.0)

						if self.bright:
							self.sunflower.set_cell((s,x,y), white_wheel(color, intense))
						else:
							self.sunflower.set_cell((s,x,y), gradient_wheel(color, intense))

			# Change it up!
			if oneIn(40):
				self.color_speed = (self.color_speed % 4) + 1
			if oneIn(10):
				self.color_inc = (self.color_inc % 50) + 1
			if oneIn(30):
				self.color_grade = (self.color_grade % 7) + 2
			
			if oneIn(2):
				if self.grow:
					self.color_decay += 0.1
					if self.color_decay > 3:
						self.grow = False
				else:
					self.color_decay -= 0.1
					if self.color_decay <= 1:
						self.grow = True

			# Add a decrease color function
			self.color = changeColor(self.color, -1)
			self.clock += 1

			yield self.speed  	# random time set in init function