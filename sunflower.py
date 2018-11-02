"""
Model to communicate with a Sunflower simulator over a TCP socket

Coordinates: (s,i) = (sunflower, pixel)  = (0-3, 0-72)
"""

from random import choice, randint
from math import ceil

NUM_SUNFLOWERS = 3
NUM_LEDS = 273

ALLOWED_FAMILIES = [8, 13, 21, 34, 55]

DEFAULT_FAMILY = 34  # Starting family

PROCESSING_FAMILY = 21  # Don't Change


def load_sunflowers(model):
    return Sunflower(model)


class Sunflower(object):

    """
    Frames implemented to shorten messages:
    Send only the pixels that change color
    Frames are hash tables where keys are (s,i) coordinates
    and values are (r,g,b) colors
    s,p,d = sunflower, petal, distance (converted to s,i)
    s,i = sunflower, pixel (cellmap keys)
    """
    def __init__(self, model, family=DEFAULT_FAMILY):
        self.model = model
        self.num_spirals = family
        self.num_sunflowers = NUM_SUNFLOWERS
        self.max_dist = int(ceil(float(NUM_LEDS) / self.num_spirals))
        self.cellmap = self.add_all_pixels()
        self.curr_frame = {}
        self.next_frame = {}
        self.init_frames()
        self.brightness = 1.0

    def __repr__(self):
        return "Sunflowers(%s)" % (self.model, self.side)

    def all_cells(self):
        """Return the list of valid coords"""
        return self.cellmap

    def cell_exists(self, coord):
        """Does the (s,i) exist?"""
        return coord in self.cellmap

    def set_cell(self, coord, color):
        """Convert (s,p,d) coord to (s,i) and send out"""
        s, p, d = coord
        i = self.get_pixel((p,d))
        coord = (s,i)
        if self.cell_exists(coord):
            self.next_frame[coord] = color

    def set_cells(self, coords, color):
        """Convert (s,p,d) coords to (s,i) and send out"""
        for coord in coords:
            self.set_cell(coord, color)

    def set_all_cells(self, color):
        for coord in self.all_cells():
            self.next_frame[coord] = color

    def set_cell_all_suns(self, coord, color):
        """coord is (p,d)"""
        p,d = coord
        for s in range(NUM_SUNFLOWERS):
            self.set_cell((s,p,d), color)

    def set_cells_all_suns(self, coords, color):
        """coords are [(p,d)]"""
        for p,d in coords:
            for s in range(NUM_SUNFLOWERS):
                self.set_cell((s, p, d), color)

    def black_cell(self, coord):
        self.set_cell(coord, (0, 0, 0))

    def black_cells(self):
        self.set_all_cells((0, 0, 0))

    def black_all_cells(self):
        self.set_all_cells((0, 0, 0))

    def clear(self):
        self.force_frame()
        self.black_all_cells()
        self.go()

    def go(self, fract=1):
        self.send_frame(fract)
        self.model.go(fract)
        self.update_frame()

    def send_delay(self, delay):
        self.model.send_delay(delay)

    def update_frame(self):
        for coord in self.next_frame:
            self.curr_frame[coord] = self.next_frame[coord]

    def send_frame(self, fract=1):
        for coord, color in self.next_frame.items():
            if fract != 1 or (coord in self.curr_frame and self.curr_frame[coord] != color):  # Has the color changed?
                self.model.set_cell(coord, color)

    def force_frame(self):
        for coord in self.curr_frame:
            self.curr_frame[coord] = (-1,-1,-1)  # Force update

    def init_frames(self):
        for coord in self.cellmap:
            self.curr_frame[coord] = (0,0,0)
            self.next_frame[coord] = (0,0,0)

    def add_all_pixels(self):
        """Return all valid (s,i) coordinates"""
        all_coords = [(s,i) for i in range(NUM_LEDS) for s in range(NUM_SUNFLOWERS)]
        return all_coords

    def get_num_spirals(self):
        return self.num_spirals

    def max_dist(self):
        return ceil(float(self.num_spirals) / NUM_LEDS)

    def is_on_board(self, coord):
        return self.get_pixel(coord) < NUM_LEDS

    def get_pixel(self, coord):
        """Calculate the pixel i from the coordinates depending on the family
           DON'T ALTER! SUCH WORK TO GET DONE CORRECTLY"""
        p, d = coord
        new_p = self.get_spiral_order(p)
        return new_p + (d * self.num_spirals)

    def get_spiral_order(self, i):
        """Convert the spiral i to a clockwise-ordered spiral
           DON'T ALTER! SUCH WORK TO GET DONE CORRECTLY"""
        denominator = PROCESSING_FAMILY if self.num_spirals != 13 else self.num_spirals
        new_i = int(round(i * NUM_LEDS / float(denominator))) % self.num_spirals
        return new_i

    ## The 2 functions below do not work; saving them for reference
    # def get_pixel(self, coord):
    #     """Calculate the pixel i from the coordinates depending on the family"""
    #     p, d = coord
    #     new_p = self.get_spiral_order(p)
    #     return new_p + (d * self.num_spirals)
    #
    # def get_spiral_order(self, i):
    #     """Convert the spiral i to a clockwise-ordered spiral"""
    #     denominator = PROCESSING_FAMILY if self.num_spirals != 13 else self.num_spirals
    #     new_i = int(round(i * NUM_LEDS / float(denominator))) % self.num_spirals
    #     return new_i

    def set_family(self, family):
        if family in ALLOWED_FAMILIES:
            self.num_spirals = family
            self.max_dist = int(ceil(float(NUM_LEDS) / self.num_spirals))

    def set_random_family(self):
        """Set num_spirals to a random spiral family"""
        self.num_spirals = self.get_random_family()
        self.max_dist = int(ceil(float(NUM_LEDS) / self.num_spirals))

    def get_random_family(self):
        return choice(ALLOWED_FAMILIES)

    def set_max_brightness(self, brightness):
        """Set the shows max brightness to 0.0 - 1.0"""
        self.brightness = brightness

    def neighbors(self, coord):
        """Returns a list of the four neighboring tuples at a given coordinate"""
        _lookup = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        (x, y) = coord
        return [(x + dx, y + dy) for dx, dy in _lookup]

    def petal_in_line(self, coord, direction, distance=0):
        """
        Returns the coord and all pixels in the direction
        along the distance
        """
        return [self.petal_in_direction(coord, direction, x) for x in range(distance)]

    def petal_in_direction(self, coord, direction, distance=1):
        """
        Returns the coordinates of the cell in a direction from a given cell.
        Direction is indicated by an integer
        There are 4 directions along curved axes
        """
        for i in range(distance):
            coord = self.petal_nextdoor(coord, direction)
        return coord

    def petal_nextdoor(self, coord, direction):
        """
        Returns the coordinates of the petal cell in the given direction
        Coordinates determined from a lookup table
        """
        _lookup = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        (x, y) = coord
        (dx, dy) = _lookup[(direction % len(_lookup))]

        return (x + dx, y + dy)

    #
    # Common random functions
    #

    # Returns a random neighbor - Neighbor may not be in bounds
    def get_rand_neighbor(self, coord):
        return choice(self.neighbors(coord))

    # Get a random sunflower
    def rand_sun(self):
        return randint(0, NUM_SUNFLOWERS - 1)

    # Get a random arm
    def rand_spiral(self):
        return randint(0, self.num_spirals - 1)

    # Get a random distance
    def rand_dist(self):
        return randint(0, self.max_dist - 1)

    # Get a random cell
    def get_rand_cell(self):
        return (self.rand_spiral(), self.rand_dist())

    #
    # Grouping Functions
    #
    def get_all_radial(self, d):
        return [(p, d) for p in range(self.num_spirals)]

    def get_all_spoke(self, p):
        return [(p, d) for d in range(self.max_dist)]

    def get_petal_sym(self, num, offset=0):
        """Return a symmetric list of petals + offset"""
        sym_type = [1, self.num_spirals / 2, self.num_spirals / 3, self.num_spirals / 4, self.num_spirals / 6, self.num_spirals]
        sym = sym_type[num % len(sym_type)]
        sym = max([1, sym])
        return [((p + offset + self.num_spirals) % self.num_spirals) for p in range(0, self.num_spirals, int(sym))]

    def get_petal_shape(self, size, offset=0):
        return [((p + offset + self.num_spirals) % self.num_spirals, (d + self.max_dist) % self.max_dist)
                for (p, d) in self.get_petal_shape_fixed(size)]

    def get_petal_shape_fixed(self, size):
        return [(size - y, x - y) for x in range(size + 1) for y in range(size + 1)]

    def get_fan_shape(self, size, offset=0):
        return [(((p + offset + self.num_spirals) % self.num_spirals), d) for (p, d) in self.get_fan_shape_fixed(size)]

    def get_fan_shape_fixed(self, size):
        petals = []
        for p in range(size + 1):
            for c in self.get_fan_band_fixed(p):
                petals.append(c)
        return petals

    def get_fan_band(self, size, offset=0):
        return [(((p + offset) % self.num_spirals), d) for (p, d) in self.get_fan_band_fixed(size)]

    def get_fan_band_fixed(self, size):
        return [(p, size) for p in range(size)]