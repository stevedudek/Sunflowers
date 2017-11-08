from HelperFunctions import*
	
class White(object):
	def __init__(self, sunflower_model):
		self.name = "White"
		self.sunflower = sunflower_model
		self.speed = 0.2
		          
	def next_frame(self):

		while (True):

			white_color = (255, 255, 255)
			self.sunflower.set_all_cells(white_color)

			yield self.speed