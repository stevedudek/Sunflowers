"""
Model to communicate with a Rose simulator over a TCP socket

"""
import socket

# "off" color for simulator
SIM_DEFAULT = (188,210,229) # BCD2E5

class SimulatorModel(object):
    def __init__(self, hostname, port=4444, debug=False):
        self.server = (hostname, port)
        self.debug = debug
        self.sock = None

        # list of (strip,pixel) to be sent on the next call to go
        self.dirty = {}

        self.connect()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server)
        # XXX throw an exception if the socket isn't available?

    def __repr__(self):
        return "Rose Model(%s, port=%d, debug=%s)" % (self.server[0], self.server[1], self.debug)

    # Model basics

    def set_cell(self, cell, color):
        "Set a (strip,pixel) coord to a color"
        self.dirty[cell] = color

    def set_cells(self, cells, color):
        "Set all fixtures in a list of coordinates to a color"
        for cell in cells:
            self.set_cell(cell, color)

    def go(self):
        "Send all of the buffered commands"
        for (cell, color) in self.dirty.items():
            (strip, pixel) = cell
            (r,g,b) = self.constrain_color(color)
            
            msg = "%s,%s,%s,%s,%s" % (strip, pixel, r,g,b)
            
            if self.debug:
                print msg
            self.sock.send(msg)
            self.sock.send('\n')

        self.dirty = {}

    def morph(self, fract):
        "send a morph amount, a fract/max_steps (see go.py)"
        msg = "M%s" % (str(int(fract)))

        if self.debug:
            print msg
        self.sock.send(msg)
        self.sock.send('\n')

    def video(self, movie_name):
        "send a movie name to turn on a movie"
        msg = "V{}".format(movie_name)

        if self.debug:
            print msg
        self.sock.send(msg)
        self.sock.send('\n')

    def relay_OSC_cmd(self, cmd, value):
        "Relay to Processing the OSC command"
        msg = "OSC,%s,%s" % (cmd,value)

        if self.debug:
            print msg
        self.sock.send(msg)
        self.sock.send('\n')

    def constrain_color(self, color):
        (r,g,b) = color
        return (self.constrain(r), self.constrain(g), self.constrain(b))

    def constrain(self, value):
        "Keep color values between 0-255 and make whole numbers"
        value = int(value)
        if value < 0: value = 0
        if value > 255: value = 255
        return value