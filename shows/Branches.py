from HelperFunctions import*
from sunflower import*
        		
class Branch(object):
	def __init__(self, sunflower_model, color, s, pos, dir):
		self.sunflower = sunflower_model
		self.color = color
		self.s = s
		self.pos = pos
		self.dir = dir
		self.life = 0	# How long the branch has been around

	def draw_branch(self):
		self.sunflower.set_cell(meld(self.s, self.pos), gradient_wheel(self.color, 1.0 - (self.life / 20.0)))
	
	def move_branch(self):			
		newspot = self.sunflower.petal_in_direction(self.pos, self.dir, 1)	# Where is the branch going?
		if self.sunflower.is_on_board(newspot) and self.life < 20:	# Is new spot off the board?
			self.pos = newspot	# On board. Update spot
			self.life += 1
			return True
		return False	# Off board. Pick a new direction
				
				
class Branches(object):
	def __init__(self, sunflower_model):
		self.name = "Branches"        
		self.sunflower = sunflower_model
		self.livebranches = []	# List that holds Branch objects
		self.speed = 0.07
		self.maincolor =  randColor()	# Main color of the show
		self.maindir = randDir() # Random initial main direction
		          
	def next_frame(self):
    	
		while (True):
			
			# Check how many branches are in play
			# If no branches, add one. If branches < 10, add more branches randomly
			while len(self.livebranches) < 30 or oneIn(10):
				newbranch = Branch(sunflower_model=self.sunflower,
								   color=randColorRange(self.maincolor, 300),
								   s=self.sunflower.rand_sun(),
								   pos=(self.sunflower.rand_spiral(), self.sunflower.get_max_dist()),
								   dir=self.maindir)  # Random initial direction
				self.livebranches.append(newbranch)
				
			for b in self.livebranches:
				b.draw_branch()
				
				# Chance for branching
				if oneIn(20):	# Create a fork
					new_dir = turn_left_or_right(b.dir)
					new_branch = Branch(self.sunflower, b.color, b.s, b.pos, new_dir)
					self.livebranches.append(new_branch)
					
				if b.move_branch() == False:	# branch has moved off the board
					self.livebranches.remove(b)	# kill the branch
								
			# Infrequently change the dominate direction
			if oneIn(100):
				self.maindir = turn_left_or_right(self.maindir)
			
			yield self.speed  	# random time set in init function