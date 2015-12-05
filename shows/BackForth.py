from HelperFunctions import*
from rose import*

class Sparkle(object):
	def __init__(self, rosemodel, color, r, pos, life):
		self.rose = rosemodel
		self.r = r
		self.pos = pos
		self.color = color
		self.intense = 1.0
		self.life = life
	
	def draw_sparkle(self):
		self.rose.set_cell(self.pos, gradient_wheel(self.color, self.intense), self.r)
	
	def fade_sparkle(self):
		self.intense -= 1.0 / self.life
		if self.intense > 0:
			return True
		else:
			return False

class Ball(object):
	def __init__(self, rosemodel, r, pos, dir, color, life):
		self.rose = rosemodel
		self.color = color
		self.r = r
		self.pos = pos		
		self.dir = dir
		self.life = life
		self.sparkles = []	# List that holds Sparkle objects

		new_sparkle = Sparkle(self.rose, self.color, self.r, get_coord(self.pos), self.life)
		self.sparkles.append(new_sparkle)

	def draw_ball(self):
		
		# Draw the sparkles
		for s in self.sparkles:
			s.draw_sparkle()
			if s.fade_sparkle() == False:
				self.sparkles.remove(s)

	def move_ball(self):

		if oneIn(50):
			self.dir = randDir()

		self.pos = rose_in_direction(self.pos, self.dir)

		new_sparkle = Sparkle(self.rose, self.color, self.r, get_coord(self.pos), self.life)
		self.sparkles.append(new_sparkle)
		

class BackForth(object):
	def __init__(self, rosemodel):
		self.name = "BackForth"        
		self.rose = rosemodel
		self.balls = []	# List that holds Ball objects
		self.num_balls = 20
		self.time = 0
		self.speed = 0.02
		self.life = randint(5,25)
		self.color = randColor()

	def next_frame(self):

		# Set up the balls

		line = rose_in_line((0,5), 1, maxPetal)
			
		for i in range(self.num_balls):
			new_ball = Ball(self.rose, randRose(), choice(line), 0, randColorRange(self.color, 200), self.life)
			self.balls.append(new_ball)

		while (True):
			
			# Set background to black
			self.rose.set_all_cells((0,0,0))

			# Move and draw the balls

			for b in self.balls:
				b.move_ball()
				b.draw_ball()
			
			if oneIn(50):
				self.life = (self.life + 1) % 20
				
			self.time += 1
			
			self.color = (self.color + 1) % maxColor					
			
			yield self.speed