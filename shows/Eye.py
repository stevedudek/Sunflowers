# Very basic show turns on an animated .gif

class Eye(object):
	def __init__(self, rosemodel):
		self.name = "Eye"        
		self.rose = rosemodel
		
		self.rose.video("eye")	# Name of movie

	def next_frame(self):
		
		while (True):
			
			yield 0.1