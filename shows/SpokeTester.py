from HelperFunctions import*
	
class SpokeTester(object):
	def __init__(self, sunflower_model):
		self.name = "SpokeTester"
		self.sunflower = sunflower_model
		self.speed = 0.2
		self.num = randint(1, 4)
		self.clock = 0
		          
	def next_frame(self):

		while (True):
			
			self.sunflower.black_cells()

			for p in self.sunflower.get_petal_sym(num=self.num, offset=self.clock % self.sunflower.num_spirals):
				self.sunflower.set_cells_all_suns(self.sunflower.get_all_spoke(p), (255, 0, 0))

			if oneIn(10):
				self.num = upORdown(self.num, 1, 1, 4)

			if oneIn(100):
				self.sunflower.set_random_family()

			self.clock += 1

			yield self.speed