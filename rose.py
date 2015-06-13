"""
Model to communicate with a Rose simulator over a TCP socket

"""

TRI_GEN = 12

NUM_PIXELS = 144

"""
Coordinates: (p,d) = (x,y) = (petal,distance)

Parameters for each Rose: (x,y), corner, direction
Corner: connector attachment is 'L' = Left, 'R' = Right, 'C' = Center
Direction: As viewed from corner, lights go 'L' = Left, 'R' = Right
"""
NUM_BIG_ROSE = 1

BIG_COORD = [ ((0, 0), 'L', 'L') ]

from HelperFunctions import distance
from collections import defaultdict
from color import RGB
from random import choice

def load_roses(model):
    return Rose(model)

class Rose(object):

    """
    Rose coordinates are stored in a hash table.
    Keys are (x,y) coordinate tuples
    Values are (strip, pixel) tuples, sometimes more than one.
    
    Frames implemented to shorten messages:
    Send only the pixels that change color
    Frames are hash tables where keys are (x,y) coordinates
    and values are (r,g,b) colors
    """
    def __init__(self, model):
        self.model = model
        self.cellmap = self.add_strips(BIG_COORD)
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

    def set_cell(self, coord, color):
        # inputs an (x,y) coord
        if self.cell_exists(coord):
            self.next_frame[coord] = color

    def set_cells(self, coords, color):
        for coord in coords:
            self.set_cell(coord, color)

    def set_all_cells(self, color):
        self.set_cells(self.all_cells(), color)

    def clear(self):
        ""
        self.force_frame()
        self.set_all_cells((0,0,0))
        self.go()

    def go(self):
        self.send_frame()
        self.model.go()
        self.update_frame()

    def update_frame(self):
        for coord in self.next_frame:
            self.curr_frame[coord] = self.next_frame[coord]

    def send_frame(self):
        for coord,color in self.next_frame.items():
            # Has the color changed? Hashing to color values
            if self.curr_frame[coord] != color:
                # Hashing to strip, fixture values
                self.model.set_cells(self.cellmap[coord], color)

    def force_frame(self):
        for coord in self.curr_frame:
            self.curr_frame[coord] = (-1,-1,-1)  # Force update

    def init_frames(self):
        for coord in self.cellmap:
            self.curr_frame[coord] = (0,0,0)
            self.next_frame[coord] = (0,0,0)
            
    def get_rand_cell(self):
        return choice(self.all_cells())

    def get_strip_from_coord(self, coord):
        "pulls the first strip that fits a coordinate"
        choices = self.cellmap[coord]
        (strip, fix) = choices[0]
        return strip

    def add_strips(self, coord_table):
        cellmap = defaultdict(list)
        for strip, (big_coord, corner, direction) in enumerate(coord_table):
            cellmap = self.add_strip(cellmap, strip, big_coord, corner, direction)
        return cellmap

    def add_strip(self, cellmap, strip, big_coord, corner, direction):
        """
        Stuff the cellmap with a Rose strip, going row by column
        """

        for i in range(NUM_PIXELS):
            coord = (i/6,i%6)
            fix = self.get_light_from_coord(coord, big_coord, corner, direction)
            cellmap[coord].append((strip, fix))
        
        return cellmap

    def get_light_from_coord(self, coord, big_coord, corner, direction):
        """
        Algorithm to convert (petal,distance) coordinate into an LED number
        Mirrors GetLightFromCoord in the Processing Rose simulator
        cleaner code would not reproduce the algorithm twice
        """
        (p,d) = coord
        p = (((p % 5) * 5) + (p / 5)) % 24  # correct petals to line them up concurrently
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
     
    def six_mirror(self, coord):
        "Returns the six-fold mirror coordinates"
        mirrors = []
        for cell in self.mirror_coords(coord):
            mirrors.append(coord)
            mirrors.append(vert_mirror(coord))

        return mirrors

    def mirror_coords(self, coord):
        "Returns the coordinate with its two mirror coordinates"
        
        mirrors = []
        mirrors.append(coord)
        mirrors.append(self.rotate_left(coord))
        mirrors.append(self.rotate_right(coord))

        return mirrors


    
##
## rose cell primitives
##

def get_big_coord(strip):
    ((big_x, big_y), corner, direction) = BIG_COORD[strip]
    return (big_x, big_y)



def all_centers():
    return [center(strip) for strip in range(NUM_BIG_TRI)]

def corners(strip=0):
    "Returns the 3 corner coordinates of a Rose"
    pad = TRI_GEN-1
    (x,y) = get_base(strip)
    if point_up(get_big_coord(strip)):
        return [(x,y), (x+pad,y+pad), (x+pad+pad,y)]    # L,C,R
    else:
        return [(x,y+pad), (x+pad,y), (x+pad+pad,y+pad)]    # L,C,R

def all_corners():
    "Return the corners of all roses"
    return get_all_func(corners)

def left_corner(strip=0):
    return corners(strip)[0]

def all_left_corners():
    return [left_corner(strip) for strip in range(NUM_BIG_TRI)]

def edge(strip=0):
    "Returns the edge pixel coordinates of a Rose"
    "Uses the 3 corners to draw each linear edge"

    corns = corners(strip)
    width = row_width(0)-1

    if point_up(get_big_coord(strip)):
        return tri_in_line(corns[0],1,width) + tri_in_line(corns[1],5,width) + tri_in_line(corns[2],3,width)
    else:
        return tri_in_line(corns[0],5,width) + tri_in_line(corns[1],1,width) + tri_in_line(corns[2],3,width)

def all_edges():
    "Return all the edge pixels"
    return get_all_func(edge)

def neighbors(coord):
    "Returns a list of the three tris neighboring a tuple at a given coordinate"
    (x,y) = coord

    if (x+y) % 2 == 0:  # Even
        neighbors = [ (1, 0), (0, -1), (-1, 0) ]    # Point up
    else:
        neighbors = [ (1, 0), (0, 1), (-1, 0) ]     # Point down

    return [(x+dx, y+dy) for (dx,dy) in neighbors]

def tri_in_line(coord, direction, distance=0):
    """
    Returns the coord and all pixels in the direction
    along the distance
    """
    return [tri_in_direction(coord, direction, x) for x in range(distance)]

def tri_in_direction(coord, direction, distance=1):
    """
    Returns the coordinates of the tri in a direction from a given tri.
    Direction is indicated by an integer
    There are 6 directions along hexagonal axes

     2  /\  1
     3 |  | 0
     4  \/  5

    """
    for i in range(distance):
        coord = tri_nextdoor(coord, direction)
    return coord

def tri_nextdoor(coord, direction):
    """
    Returns the coordinates of the adjacent tri in the given direction
    Even (point up) and odd (point down) tri behave different
    Coordinates determined from a lookup table
    """
    _evens = [ (1, 0), (1, 0), (-1, 0), (-1, 0), (0, -1), (0, -1) ]
    _odds  = [ (1, 0), (0, 1), (0, 1), (-1, 0), (-1, 0), (1, 0) ]

    direction = direction % 6

    (x,y) = coord

    if (x+y) % 2 == 0:  # Even
        (dx,dy) = _evens[direction]
    else:
        (dx,dy) = _odds[direction]

    return (x+dx, y+dy)

def get_rand_neighbor(coord):
    """
    Returns a random neighbors
    Neighbor may not be in bounds
    """
    return choice(neighbors(coord))

def clock(coord, center):
    "Returns the clockwise cell"
    neighs = neighbors(coord)
    closest = near_neighbor(coord, center)

    for i in range(3):
        if closest == neighs[i]:
            return neighs[(i+2) % 3]

    print "can't find a clock cell"

def counterclock(coord, center):
    "Returns the counterclockwise cell"
    neighs = neighbors(coord)
    closest = near_neighbor(coord, center)

    for i in range(3):
        if closest == neighs[i]:
            return neighs[(i+1) % 3]

    print "can't find a counterclock cell"

def near_neighbor(coord, center):
    "Returns the neighbor of coord that is closest to center"
    best_coord  = coord
    min_dist = 1000

    for c in neighbors(coord):
        dist = distance(c, center)
        if dist < min_dist:
            best_coord = c
            min_dist = dist

    return best_coord

def get_ring(center, size):
    "Returns a list of coordinates that make up a centered ring"
    size = 1 + (2*size) # For hex shape

    t = tri_in_direction(center, 4, size)
    results = []
    for i in range(6):
        for j in range(size):
            results.append(t)
            t = tri_nextdoor(t,i)
    return results

def tri_shape(start, size):
    """
    Returns a list of coordinates that make up a rose
    Rose's left corner will be the 'start' pixel
    start's location will determine whether rose points up or down
    """
    size = 2 * (size-1)

    # Clockwise addtion
    if point_up(start):
        return (tri_in_line(start,1,size) +
            tri_in_line( tri_in_direction(start,1,size), 5,size) +
            tri_in_line( tri_in_direction(start,0,size), 3,size))
    else:
        return (tri_in_line(start,0,size) +
            tri_in_line( tri_in_direction(start,0,size), 4,size) +
            tri_in_line( tri_in_direction(start,5,size), 2,size))

def nested_roses(start):
    """
    Return a list of lists of coordinates,
    A list of concentric roses with the largest first
    with each rose centered in the middle
    Rose's left corner will be the 'start' pixel
    """
    left_corn = start

    cells = []
    for size in range(TRI_GEN, 0, -3):
        cells.append(tri_shape(left_corn,size))
        if point_up(start):
            left_corn = tri_in_direction( tri_in_direction(left_corn,1,2), 0,2)
        else:
            left_corn = tri_in_direction( tri_in_direction(left_corn,5,2), 0,2)

    return cells