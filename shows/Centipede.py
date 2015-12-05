from random import random, randint, choice

from HelperFunctions import*
           
class Fader(object):
    def __init__(self, rosemodel, color, pos, decay):
	self.rose = rosemodel
	self.pos = pos
	self.color = color
	self.decay = decay
	self.life = 1.0
	
    def draw(self):
	self.rose.set_cell(self.pos, gradient_wheel(self.color, self.life))
	
    def fade(self):
	self.life -= self.decay
	if self.life >= 0:
	    return True
	else:
	    return False

class Centipede (object):
    def __init__(self, rosemodel):
	self.name = "Centipede"
	self.rose = rosemodel
	self.faders = []	# List that holds Fader objects
	self.speed = 0.1
	self.color = randColor()
	self.trail = 0.5 / 24.0
        self.change = 10
	self.clock = 0
		          
    def next_frame(self):

        # Set background to black
        self.rose.set_all_cells((0,0,0))

        # changetrack is the flag letting the main loop know whether
        # it's time to change tracks, selected by oneIn() below.
        changetrack = 0

        # It will start counterclockwise.  -1 = clockwise.
        # I haven't decided how to implement this yet.
        # direction = 1

        # It will start at (0,3) going up.  Why not?
        x = 0
        y = 3
        parity = 0

        while (True):

            # This decides if it changes tracks or directions.
            # I commented out the changing directions code for now

            #if not oneIn(100): # change directions one in a hundred.
            if oneIn(self.change):      # change tracks this often
                if y > 4:               # Can't get farther from center, so:
                    changetrack -= 1    # move one track towards center
                else:
                    changetrack += choice([-1,1])  # Move one track over

            """  I'm not yet sure how to behave if it changes directions
            else: #oneIn 100 makes it change directions.
                if track <= 2:
                    track += 2
                    direction = -1 * direction
                elif track >= 4:
                    track -= 2
                    direction = -1 * direction
                else:
                    track += choice([-2,2])
                    direction = -1 * direction
            """

            # Create new faders
            # That is, decide which pixels need to be lit and put them
            # in the list self.faders[] so they can be drawn below.
            # Centipede goes zig-zag, up-down.  Parity keeps track of that.

            if parity % 2 == 0:            # Centipede is down
                if changetrack == 0:       # keep regular up-down motion
                    x = (x + 1) % maxPetal
                    y += 1
                    parity += 1
                elif changetrack == 1:     # Go up
                    # print"even up"
                    x = (x + 1) % maxPetal
                    y += 1
                    # parity stays eveb so it can go up twice
                elif changetrack == -1:    # Go down
                    # print"even down"
                    # x stays the same
                    y -= 1
                    # parity stays even so it can go down twice
                # print"even: parity = %s, x = %s, y = %s" % (parity,x,y)
            else:                          # Centipede is up
                if changetrack == 0:       # keep regular up-down motion
                    # x stays the same
                    y -= 1
                    parity += 1
                elif changetrack == 1:
                    # print"odd up"
                    x = (x + 1) % maxPetal
                    y += 1
                    # parity stays odd so it can go up twice
                elif changetrack == -1:
                    # print"odd down"
                    # x stays the same
                    y -= 1
                    # parity stays odd so it can go down twice
                #print"odd: parity = %s, x = %s, y = %s" % (parity,x,y)
            changetrack = 0

            # If y goes negative, let it loop to other side
            if y < 0:
                y = (-1 * y) - 1
                x = (x + maxPetal / 2) % maxPetal

            # This places the coordinates in a fader and appends it to list.
            new_fader = Fader(self.rose, self.color, (x,y), self.trail)
            self.faders.append(new_fader)

            # Draw the Faders

            for f in self.faders:
                f.draw()
	        if not f.fade():
                    self.faders.remove(f)

	    # Change the colors and symmetry

	    self.color = randColorRange(self.color, 5)

	    self.clock += 1
            yield self.speed #random time set in init function
