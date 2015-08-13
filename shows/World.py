# Very basic show turns on an animated .gif

class World(object):
	def __init__(self, rosemodel):
		self.name = "World"        
		self.rose = rosemodel
		
		self.rose.video("Earth")	# Name of movie

	def next_frame(self):
		
		while (True):
			
			yield 0.1