from math import hypot, pi, cos, sin, asin, atan
from HelperFunctions import*

"""
These are a bunch of functions to allow a script to apply physics to the
Rose.  These include mostly a bunch of functions to convert the (petal, dist)
coordinates used in functions like set_cell() to polar (s, theta) or Cartesian
(cartx, carty) coordinates and back which will allow the application of
Newtonian physics.

Polar is (s, theta), cart is (cartx, carty), and simple coordinates are
simple (petal, dist).

There are functions to allow any translation between any coordinate
to any other between simple, polar, and cart (Cartesian).  You can also convert
from any coordinate tuple to any other.

Here's a good place to add functions like anti-aliasing, collision,
Cartesian distance, and force rules.

a_from_b means that the function converts b units to a.

Unfortunately, you have to trust me on the math.  I did a lot of tests. -Ruben
"""

# SIMPLE TO POLAR
# Tested 11 Sep 2015.  Works, but sometimes returns petal = 24.

# usually, you need both coords, but dist <-> s doesn't need petal.
def r_from_dist(dist):
    return abs(sin((pi/14) * (dist + 1)))

def r_from_simple(simple):
    (petal, dist) = simple
    return r_from_dist(dist)

# The petal term is clear; the dist term compensates for the twist you get
# as dist increases; the pi/24 term at the end compensates for simple(0,0)
# not starting at the x=0 axis.  The +2pi%2pi at the end make sure it's > 0.
def theta_from_simple(simple):
    (petal, dist) = simple
    return ((pi/12) * petal - (pi/24) * dist - pi/24 + 2*pi) % (2*pi)

def polar_from_simple(simple):
    (petal, dist) = simple
    s = r_from_dist(dist)
    theta = theta_from_simple(simple)
    return(s, theta)



# CART TO POLAR
# Tested 11 Sep 2015.  WORKS!

def r_from_cart(cart):
    (cartx, carty) = cart
    return hypot(cartx, carty)

def theta_from_cart(cart):
    (x, y) = cart
    if x == 0:
        if y == 0:
            return 0             # This is ok, but could lead to trouble
        elif y > 0:
            return pi / 2
        elif y < 0:
            return 3 * pi / 2
    elif x < 0:                  # Quadrants II and III behave the same
        return atan(y/x) + pi
    elif x > 0:                  # Quadrant IV wants to return negative petal
        if y == 0:               # This is redundant, but safe.  atan(0) = 0.
            return 0.0
        elif y > 0:              # Quadrant I is ok
            return atan(y/x)
        elif y < 0:              # Quadrant IV is QI plus 2pi.
            return atan(y/x) + 2*pi

def polar_from_cart(cart):
    s = r_from_cart(cart)
    theta = theta_from_cart(cart)
    return (s, theta)



# POLAR TO SIMPLE
# Note that it's more efficient to get both at the same time.
# That's because petal_from_polar() calls dist_from_r()
# Tested 6 Sep 2015.  Works!

# usually, you need both coords, but dist <-> s doesn't need petal.
# The -1 term adjusts for the fact that dist=0 is not at the origin.
def dist_from_r(s):
    return (14/pi) * asin(s) - 1

# This is just a wrapper for dist_from_r to keep consistent with other code.
def dist_from_polar(polar):
    (s, theta) = polar
    return dist_from_r(s)

# The dist_from_r term compensates for the twist from increasing dist.
def petal_from_polar(polar):
    (s, theta) = polar
    return ((12/pi) * theta + dist_from_r(s)/2 + 0.5) % self.sunflower.num_spirals

# The dist/2 term compensates for the twist in dist.
def simple_from_polar(polar):
    (s, theta) = polar     # slight efficiency if I break this up.
    dist = dist_from_r(s)  # next line uses this so I do this first
    petal = (12/pi) * theta + dist / 2
    return (petal, dist)


    
# POLAR TO CART
# Tested 11 Sep 2015.  WORKS!

def cartx_from_polar(polar):
    (s, theta) = polar
    return s * cos(theta)

def carty_from_polar(polar):
    (s, theta) = polar
    return s * sin(theta)

def cart_from_polar(polar):
    cartx = cartx_from_polar(polar)
    carty = carty_from_polar(polar)
    return(cartx, carty)



# SIMPLE TO CART
# This uses the polar coord transforms.  Why figure that out twice?
# Tested 11 Sep 2015.  Works!

def cartx_from_simple(simple):
    s = r_from_simple(simple)
    theta = theta_from_simple(simple)
    return s * cos(theta)

def carty_from_simple(simple):
    s = r_from_simple(simple)
    theta = theta_from_simple(simple)
    return s * sin(theta)

def cart_from_simple(simple):
    x = cartx_from_simple(simple)
    y = carty_from_simple(simple)
    return (x,y)



# CART TO SIMPLE
# This just uses polar coords as a middleground.
# These return floats, I think.  The remainder can be used for antialiasing.
# I should probably come up with a version that returns ints.
# Also, check to see if these really handle int <-> floats well.
# x=0 y=0 returns petal = 0.  This should be ok, but keep an eye on it.
# Tested 11 Sep 2015.  Works!

def petal_from_cart(cart):
    polar = polar_from_cart(cart)
    return petal_from_polar(polar)

def dist_from_cart(cart):
    polar = polar_from_cart(cart)
    return dist_from_polar(polar)

def simple_from_cart(cart):
    polar = polar_from_cart(cart)
    return simple_from_polar(polar)



# PHYSICS FUNCTIONS
# Random functions like figuring out distances, forces, collisions
# Add functions here.  I can't wait for antialiasing!!!
# Figure out how to take (petal, dist) as floats, render the rounded off
# pixels, then use remainder to anti-alias.
# Thise are not tested yet.

# This takes cartesian coordinates.  The result is a cartesian distance.
def cart_dist(pos1, pos2):
    (x1, y1) = pos1
    (x2, y2) = pos2
    return hypot((x1-x2), (y1-y2))

# This takes (petal, dist) coordinates.
# The result is still a cartesian distance.
def simp_dist(pos1, pos2):
    (x1, y1) = cart_from_simp(pos1)
    (x2, y2) = cart_from_simp(pos2)
    return hypot((x1-x2),(y1-y2))

""" Try this if regular version doesn't work.
# This is a scaled down trial of the real antialias_particle I want.
# instead of just rendering the cells or returning a list of cells to render,
# This just takes non-integer (petal, dist) and a test coordinate and returns
# the brighness that test_coord should have to be antialiased.
"""

# This is like antialias_particle, but it lets you designate a size.
# It's different enough that I didn't just make aa_particle a wrapper of this.
def antialias_ball(coord, size, color):

    (p, d) = coord
    (x, y) = coord_from_simple((p,d))
    lowx = floor(x)
    highx = ceil(x)
    lowy = floor(y)
    highy = ceil(y)

    for cell in all_cells():
        if cart_dist(coord, cell) < hypot(lowx, lowy) + size:
            set_cell(cell, gradient_wheel(color, 255))
        elif cart_dist(coord, cell) < hypot(highx, highy) + size:
            set_cell(cell, hypot(highx, highy) - cart_dist(coord, cell))
