from HelperFunctions import*
from rose import*
        		
class Branch(object):
	def __init__(self, rosemodel, color, r, pos, dir, life):
		self.rose = rosemodel
		self.color = color
		self.r = r
		self.pos = pos
		self.dir = dir
		self.life = life	# How long the branch has been around

	def draw_branch(self, inversion):
		if inversion:
			ratio = self.life/10.0 # dark center
		else:
			ratio = 1 - self.life/40.0 # light center
		
		self.rose.set_cell(get_coord(self.pos), gradient_wheel(self.color, ratio), self.r)
							
		# Random chance that path changes
		if oneIn(3):
			self.dir = turn_left_or_right(self.dir)
	
	def move_branch(self):			
		newspot = rose_in_direction(self.pos, self.dir, 1)	# Where is the branch going?
		if is_on_board(newspot) and self.life < 40:	# Is new spot off the board?
			self.pos = newspot	# On board. Update spot
			self.life += 1
			return True
		return False	# Off board. Pick a new direction
				
				
class CenterBranches(object):
	def __init__(self, rosemodel):
		self.name = "Center Branches"        
		self.rose = rosemodel
		self.livebranches = []	# List that holds Branch objects
		self.speed = 0.05
		self.maincolor =  randColor()	# Main color of the show
		self.inversion = randint(0,1)	# Toggle for effects
		          
	def next_frame(self):
    	
		while (True):
			
			# Add a center branch
			
			if len(self.livebranches) < 20 or oneIn(30):
				
				newbranch = Branch(self.rose,
					self.maincolor, # color
					randRose(),		# Rose
					(0,0), 			# center
					randDir(), 		# Random initial direction
					0)				# Life = 0 (new branch)
				self.livebranches.append(newbranch)
				self.maincolor = (self.maincolor + 50) % maxColor
				
			for b in self.livebranches:
				b.draw_branch(self.inversion)
				
				# Chance for branching
				if oneIn(20):	# Create a fork
					new_dir = turn_left_or_right(b.dir)
					new_branch = Branch(self.rose, b.color, b.r, b.pos, new_dir, b.life)
					self.livebranches.append(new_branch)
					
				if b.move_branch() == False:	# branch has moved off the board
					self.livebranches.remove(b)	# kill the branch
			
			yield self.speed