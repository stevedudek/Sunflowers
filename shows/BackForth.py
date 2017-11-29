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

	def draw_ball(self):
		return Fader(self.sunflower, self.color, meld(self.sun, self.pos), change=self.change)

	def move_ball(self):

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
			return False

		return True
		

class BackForth(object):
	def __init__(self, sunflower_model):
		self.name = "BackForth"        
		self.sunflower = sunflower_model
		self.balls = []	# List that holds Ball objects
		self.num_balls = randint(5,20)
		self.speed = 0.2
		self.change_amt = randint(5, 20)
		self.color = randColor()
		self.faders = Faders(self.sunflower)

	def next_frame(self):

		while (True):

			while len(self.balls) < 10:
				new_ball = Ball(self.sunflower, self.sunflower.rand_sun(), (self.sunflower.rand_spiral(), 3), 0,
								randColorRange(self.color, 200), 1.0 / self.change_amt)
				self.balls.append(new_ball)

			self.faders.cycle_faders(refresh=True)

			for b in self.balls:
				self.faders.add_fader_obj(b.draw_ball())
				if not b.move_ball():
					self.balls.remove(b)
			
			if oneIn(50):
				self.change_amt = upORdown(self.change_amt, 1, 5, 20)
				
			self.color = (self.color + 1) % MAX_COLOR
			
			yield self.speed