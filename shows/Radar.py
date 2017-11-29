from HelperClasses import*
from sunflower import NUM_SUNFLOWERS

class Radar(object):
    def __init__(self, sunflower_model):
        self.name = "Radar"
        self.sunflower = sunflower_model
        self.faders = Faders(sunflower_model)
        self.speed = 0.1
        self.color = randColor()
        self.color_gradient = randint(20, 50)
        self.trail = 1.5 / self.sunflower.num_spirals
        self.symm = 1
        self.clock = 0
		          
    def next_frame(self):

        self.sunflower.black_cells()
		
        while (True):

            """
            Create a list of new faders
            ray is just short for self.clock
            s goes 0,2,4 then 1,3,5 then 0,2,4 and 1,3,5 over and over.
            This is so the radar travels around evenly.
            x and y are the coordinates that go into new_faders
            x and y  are based on s and ray
            self.faders collects the pixels that will light up and fade
            """

            ray = self.clock
            if ray % 2 == 0: #even ray
                for s in range((self.sunflower.max_dist/2) + 1):
                    x = (ray/2 + s) % self.sunflower.num_spirals
                    y = 2*s % self.sunflower.max_dist
                    for sun in range(NUM_SUNFLOWERS):
                        self.faders.add_fader(changeColor(self.color, y * self.color_gradient), (sun, x, y), self.trail)
            else: #odd ray
                for s in range((self.sunflower.max_dist/2) + 1):
                    x = (ray/2 + s + 1) % self.sunflower.num_spirals
                    y = 2*s+ 1 % self.sunflower.max_dist
                    for sun in range(NUM_SUNFLOWERS):
                        self.faders.add_fader(changeColor(self.color, y * self.color_gradient), (sun, x, y), self.trail)


            # Draw the Faders that were selected and collected just above.

            self.faders.cycle_faders(refresh=False)

	        # Change the colors and symmetry

            self.color = randColorRange(self.color, 5)

            self.clock += 1
            yield self.speed #random time set in init function
