from random import random, randint, choice

from HelperFunctions import*
           
class Fader(object):
    def __init__(self, rosemodel, color, pos, decay):
	self.rose = rosemodel
	self.pos = pos
	self.color = color
	self.decay = decay
	self.life = 1.0

    # draws all the pixels in the list fed to Fader
    def draw(self):
	self.rose.set_cell(self.pos, gradient_wheel(self.color, self.life))

    # create the decay effect and drop the pixel from the list if black.
    def fade(self):
	self.life -= self.decay
	if self.life >= 0:
	    return True
	else:
	    return False
        						
class Radar(object):
    def __init__(self, rosemodel):
	self.name = "Radar"
	self.rose = rosemodel
	self.faders = []	# List that holds Fader objects
	self.speed = 0.1
	self.color = randColor()
	self.trail = 1.0 / 24.0
	self.symm = 1
	self.clock = 0
		          
    def next_frame(self):

        # Set background to black
        self.rose.set_all_cells((0,0,0))
		
        while (True):

            """
            Create a list of new faders
            ray is just short for self.clock
            r goes 0,2,4 then 1,3,5 then 0,2,4 and 1,3,5 over and over.
            This is so the radar travels around evenly.
            x and y are the coordinates that go into new_faders
            x and y  are based on r and ray
            self.faders collects the pixels that will light up and fade
            """

            ray = self.clock
            if ray % 2 == 0: #even ray
                for r in range(maxDistance/2):
                    x = (ray/2 + r) % maxPetal
                    y = 2*r % maxDistance
                    new_fader = Fader(self.rose, self.color, (x,y), self.trail)
		    self.faders.append(new_fader)
            else: #odd ray
                for r in range(maxDistance/2):
                    x = (ray/2 + r + 1) % maxPetal
                    y = 2*r+1 % maxDistance
                    new_fader = Fader(self.rose, self.color, (x,y), self.trail)
		    self.faders.append(new_fader)

            # Draw the Faders that were selected and collected just above.

            for f in self.faders:
                f.draw()
	        if not f.fade():
                    self.faders.remove(f)

	    # Change the colors and symmetry

	    self.color = randColorRange(self.color, 5)

	    self.clock += 1
            yield self.speed #random time set in init function
