from HelperFunctions import*
	
class RingTester(object):
	def __init__(self, sunflower_model):
		self.name = "RingTester"
		self.sunflower = sunflower_model
		self.speed = 0.05
		self.color = (0,255,0)
		self.clock = 0
		          
	def next_frame(self):
		
		while (True):
			
			self.sunflower.black_cells()
					
			self.sunflower.set_cells_all_suns(self.sunflower.get_all_radial(self.clock % self.sunflower.max_dist),
											  wheel(self.clock * 10 % MAX_COLOR))
			self.clock += 1

			yield self.speed