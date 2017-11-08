from HelperFunctions import*
from sunflower import*
        		
class Branch(object):
	def __init__(self, sunflower_model, color, s, pos, dir, life):
		self.sunflower = sunflower_model
		self.color = color
		self.s = s
		self.pos = pos
		self.dir = dir
		self.life = life	# How long the branch has been around
		self.max_brightness = 0.3
		self.sunflower.set_max_brightness(self.max_brightness)

	def draw_branch(self, inversion):
		if inversion:
			ratio = self.life / 10.0 # dark center
		else:
			ratio = 1 - self.life / 40.0 # light center
		
		self.sunflower.set_cell(meld(self.s, self.pos), gradient_wheel(self.color, ratio))
							
		# Random chance that path changes
		if oneIn(3):
			self.dir = turn_left_or_right(self.dir)
	
	def move_branch(self):			
		newspot = self.sunflower.petal_in_direction(self.pos, self.dir, 1)	# Where is the branch going?
		if self.sunflower.is_on_board(newspot) and self.life < 40:	# Is new spot off the board?
			self.pos = newspot	# On board. Update spot
			self.life += 1
			return True
		return False	# Off board. Pick a new direction
				
				
class CenterBranches(object):
	def __init__(self, sunflower_model):
		self.name = "Center Branches"        
		self.sunflower = sunflower_model
		self.livebranches = []	# List that holds Branch objects
		self.speed = 0.05
		self.maincolor =  randColor()	# Main color of the show
		self.inversion = randint(0,1)	# Toggle for effects
		          
	def next_frame(self):
    	
		while (True):
			
			# Add a center branch
			
			if len(self.livebranches) < 20 or oneIn(30):
				
				newbranch = Branch(self.sunflower,
								   self.maincolor,  # color
								   self.sunflower.rand_sun(),  # Rose
					(0,0),  # center
					randDir(),  # Random initial direction
					0)				# Life = 0 (new branch)
				self.livebranches.append(newbranch)
				self.maincolor = (self.maincolor + 40) % MAX_COLOR
				
			for b in self.livebranches:
				b.draw_branch(self.inversion)
				
				# Chance for branching
				if oneIn(20):	# Create a fork
					new_dir = turn_left_or_right(b.dir)
					new_branch = Branch(self.sunflower, b.color, b.s, b.pos, new_dir, b.life)
					self.livebranches.append(new_branch)
					
				if b.move_branch() == False:	# branch has moved off the board
					self.livebranches.remove(b)	# kill the branch
			
			yield self.speed