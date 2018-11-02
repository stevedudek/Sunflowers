from HelperFunctions import *

class PixelTester(object):
    def __init__(self, sunflower_model):
        self.name = "PixelTester"
        self.sunflower = sunflower_model
        self.speed = 1
        self.clock = 0
        self.color = 0

    def next_frame(self):

        family = 34

        self.sunflower.set_family(family)

        while (True):

            self.sunflower.black_cells()

            for p in range(0, self.sunflower.num_spirals, 4):
                for d in range(self.sunflower.max_dist / 2, self.sunflower.max_dist):
                    self.sunflower.set_cell_all_suns((p,d), wheel(changeColor(self.color, (p * 100) + self.clock)))

            self.clock += 1

            yield self.speed