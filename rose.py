"""
Model to communicate with a Rose simulator over a TCP socket

"""

"""
Coordinates: (p,d) = (x,y) = (petal,distance)  = (0-23, 0-5)

"""

NUM_PIXELS = 144
NUM_PETALS = 24
NUM_BIG_ROSE = 3

ALL_ROSES = 9

import time
from HelperFunctions import get_coord
from collections import defaultdict
from random import choice

def load_roses(model):
    return Rose(model)

class Rose(object):

    """
    Rose coordinates are stored in a hash table.
    Keys are (r,p,d) coordinate triples
    Values are (strip, pixel) triples
    
    Frames implemented to shorten messages:
    Send only the pixels that change color
    Frames are hash tables where keys are (r,p,d) coordinates
    and values are (r,g,b) colors
    """
    def __init__(self, model):
        self.model = model
        self.cellmap = self.add_strips()
        self.curr_frame = {}
        self.next_frame = {}
        self.init_frames()

    def __repr__(self):
        return "Roses(%s)" % (self.model, self.side)

    def all_cells(self):
        "Return the list of valid coords"
        return list(self.cellmap.keys())

    def cell_exists(self, coord):
        return self.cellmap[coord]

    def set_cell(self, coord, color, r=ALL_ROSES):
        (p,d) = coord
        if self.cell_exists((0,p,d)):
            if r == ALL_ROSES:
                for r in range(NUM_BIG_ROSE):
                    self.next_frame[(r,p,d)] = color
            else:
                self.next_frame[(0,p,d)] = color

    def set_cells(self, coords, color, r=ALL_ROSES):
        for coord in coords:
            self.set_cell(coord, color, r)

    def set_all_cells(self, color):
        for c in self.all_cells():
            self.next_frame[c] = color

    def clear(self):
        self.force_frame()
        self.set_all_cells((0,0,0))
        self.go()

    def go(self):
        self.send_frame()
        self.model.go()
        self.update_frame()

    def send_delay(self, delay):
        self.model.send_delay(delay)

    def update_frame(self):
        for coord in self.next_frame:
            self.curr_frame[coord] = self.next_frame[coord]

    def send_frame(self):
        for coord,color in self.next_frame.items():
            if self.curr_frame[coord] != color: # Has the color changed? Hashing to color values
                self.model.set_cells(self.cellmap[coord], color)

    def force_frame(self):
        for coord in self.curr_frame:
            self.curr_frame[coord] = (-1,-1,-1)  # Force update

    def init_frames(self):
        for coord in self.cellmap:
            self.curr_frame[coord] = (0,0,0)
            self.next_frame[coord] = (0,0,0)

    def add_strips(self):
        cellmap = defaultdict(list)
        for strip in range(NUM_BIG_ROSE):
            cellmap = self.add_strip(cellmap, strip)
        return cellmap

    def add_strip(self, cellmap, strip):
        """
        Stuff the cellmap with a Rose strip, going row by column
        """
        for i in range(NUM_PIXELS):
            petal = i//6
            distance = i%6
            fix = self.get_light_from_coord((petal,distance))
            cellmap[(strip, petal, distance)].append((strip, fix))
        
        return cellmap

    def get_light_from_coord(self, coord):
        """
        Algorithm to convert (petal,distance) coordinate into an LED number
        Mirrors GetLightFromCoord in the Processing Rose simulator
        cleaner code would not reproduce the algorithm twice
        """
        (p,d) = coord
        #p = (((p % 5) * 5) + (p / 5)) % 24  # correct petals to line them up concurrently
        LED = (((5-d)/2)*48) + (p*2) + ((d+1)%2);
      
        if d == 2 or d == 3:    # Middle two rings of LEDs 48-95
            LED = LED+1         # Shift the ring due to wiring
            if LED >= 96:
                LED -= 48
        if d <= 1:              # Inner two rings of LEDs 96-143
            LED = LED+4         # Shift the ring due to wiring
            if LED >= 144:
                LED -= 48
        
        return LED


    
##
## rose cell primitives
##

def is_on_board(coord):
    (p,d) = coord
    return (p < 6 and p > -6)

def neighbors(coord):
    "Returns a list of the four neighboring tuples at a given coordinate"
    (x,y) = coord

    neighbors = [ (0, 1), (1, -1), (0, -1), (-1, 1) ]

    return [get_coord((x+dx, y+dy)) for (dx,dy) in neighbors]

def rose_in_line(coord, direction, distance=0):
    """
    Returns the coord and all pixels in the direction
    along the distance
    """
    return [rose_in_direction(coord, direction, x) for x in range(distance)]

def rose_in_direction(coord, direction, distance=1):
    """
    Returns the coordinates of the cell in a direction from a given cell.
    Direction is indicated by an integer
    There are 4 directions along curved axes
    """
    for i in range(distance):
        coord = rose_nextdoor(coord, direction)
    return coord

def rose_nextdoor(coord, direction):
    """
    Returns the coordinates of the rose cell in the given direction
    Coordinates determined from a lookup table
    """
    _lookup = [ (0, 1), (-1, -1), (0, -1), (1, 1) ]

    (x,y) = coord
    (dx,dy) = _lookup[(direction % 4)]
    
    return (x+dx, y+dy)

def get_rand_neighbor(coord):
    """
    Returns a random neighbors
    Neighbor may not be in bounds
    """
    return choice(neighbors(coord))
