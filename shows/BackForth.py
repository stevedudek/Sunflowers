from HelperFunctions import*
from HelperClasses import*
from sunflower import*

class Ball(object):
	def __init__(self, sunflower_model, sun, pos, dir, color, change):
		self.sunflower = sunflower_model
		self.color = color
		self.dir = dir
		self.change = change
		self.sun = sun
		self.pos = pos
		self.faders = Faders(self.sunflower)

	def move_and_draw_ball(self):
		self.faders.cycle_faders(refresh=False)

		if oneIn(20):
			self.dir = randDir()

		max_tries = 5
		tries = 0
		while tries < max_tries:
			new_pos = self.sunflower.petal_in_direction(self.pos, self.dir)
			if self.sunflower.is_on_board(new_pos):
				break
			self.dir = randDir()
			tries +=1
		self.pos = new_pos

		if tries > max_tries or oneIn(100):
			self.faders.fade_all()
			return False

		self.faders.add_fader(self.color, meld(self.sun, self.pos), change=self.change)
		return True
		

class BackForth(object):
	def __init__(self, sunflower_model):
		self.name = "BackForth"        
		self.sunflower = sunflower_model
		self.balls = []	# List that holds Ball objects
		self.num_balls = randint(5,20)
		self.speed = 0.2
		self.change_amt = randint(5,25)
		self.color = randColor()

	def next_frame(self):

		while (True):

			while len(self.balls) < 10:
				new_ball = Ball(self.sunflower, self.sunflower.rand_sun(), (self.sunflower.rand_spiral(), 3), 0,
								randColorRange(self.color, 200), 1.0 / self.change_amt)
				self.balls.append(new_ball)

			self.sunflower.black_cells()

			# Move and draw the balls

			for b in self.balls:
				if not b.move_and_draw_ball():
					self.balls.remove(b)
			
			if oneIn(50):
				self.change_amt = upORdown(self.change_amt, 1, 5, 25)
				
			self.color = (self.color + 1) % MAX_COLOR
			
			yield self.speed