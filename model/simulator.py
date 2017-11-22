"""
Model to communicate with a Sunflower simulator over a TCP socket

"""
import socket

# "off" color for simulator
SIM_DEFAULT = (188,210,229) # BCD2E5

class SimulatorModel(object):
    def __init__(self, hostname, port=4444, debug=False):
        self.server = (hostname, port)
        self.debug = debug
        self.sock = None

        # list of (s, p, d) to be sent on the next call to go
        self.dirty = {}

        self.connect()

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server)
        # XXX throw an exception if the socket isn't available?

    def __repr__(self):
        return "Sunflower Model(%s, port=%d, debug=%s)" % (self.server[0], self.server[1], self.debug)

    # Model basics

    def set_cell(self, cell, color):
        "Set a (s, p, d) coord to a color"
        self.dirty[cell] = color

    def set_cells(self, cells, color):
        "Set all fixtures in a list of coordinates to a color"
        for cell in cells:
            self.set_cell(cell, color)

    def go(self, fract=1):
        "Send all of the buffered commands"
        self.send_start()
        for (cell, color) in self.dirty.items():
            (s, i) = cell
            (r, g, b) = self.constrain_color(color, fract)
            msg = "%s,%s,%s,%s,%s" % (s,i, r,g,b)
            
            if self.debug:
                print msg
            self.sock.send(msg)
            self.sock.send('\n')

        self.dirty = {}

    def send_start(self):
        "send a start signal"
        msg = "X"   # tell processing that commands are coming

        if self.debug:
            print msg
        self.sock.send(msg)
        self.sock.send('\n')

    def send_delay(self, delay):
        "send a morph amount in milliseconds"
        msg = "D%s" % (str(int(delay * 1000)))

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

    def constrain_color(self, color, fract=1):
        (r,g,b) = color
        return (self.constrain(r, fract), self.constrain(g, fract), self.constrain(b, fract))

    def constrain(self, value, fract=1):
        "Keep color values between 0-255 and make whole numbers"
        value = int(value * fract)
        if value < 0: value = 0
        if value > 255: value = 255
        return value