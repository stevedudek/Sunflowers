#!/usr/bin/env python2.7
import sys
import time
import traceback
import Queue
import threading
import signal

import sunflower
import shows
import util

# import cherrypy
import math

SPEED_MULT = 2  # Multiply every delay by this value. Higher = much slower shows

def speed_interpolation(val):
    """
    Interpolation function to map OSC input into ShowRunner speed_x

    Input values range from 0.0 to 1.0
    input 0.5 => 1.0
    input < 0.5 ranges from 10.0 to 1.0
    input > 0.5 ranges from 1.0 to 0.1
    """
    if val == 0.5:
        return 1.0
    elif val < 0.5:
        return low_interp(val)
    else:
        return hi_interp(val)

low_interp = util.make_interpolater(0.0, 0.5, 10.0, 1.0)
hi_interp  = util.make_interpolater(0.5, 1.0, 1.0, 0.1)

class ShowRunner(threading.Thread):
    def __init__(self, model, simulator, queue, max_showtime=1000):
        super(ShowRunner, self).__init__(name="ShowRunner")
        self.model = model
        self.simulator = simulator
        self.queue = queue

        self.running = True
        self.max_show_time = max_showtime
        self.show_runtime = 0

        # map of names -> show ctors
        self.shows = dict(shows.load_shows())
        self.randseq = shows.random_shows()

        # current show object & frame generator
        self.show = None
        self.framegen = None

        # current show parameters

        # video is off at the stop
        self.video = False

        # show speed multiplier - ranges from 0.1 to 10
        # 1.0 is normal speed
        # lower numbers mean faster speeds, higher is slower
        self.speed_x = 1.0

        # brightness - ranges from 5 to 100%
        # 100% is initial value
        self.brightness_x = 100

    def status(self):
        if self.running:
            return "Running: %s (%d seconds left)" % (self.show.name, self.max_show_time - self.show_runtime)
        else:
            return "Stopped"

    def check_queue(self):
        msgs = []
        try:
            while True:
                m = self.queue.get_nowait()
                if m:
                    msgs.append(m)

        except Queue.Empty:
            pass

        if msgs:
            for m in msgs:
                self.process_command(m)

    def process_command(self, msg):
        if isinstance(msg,basestring):
            if msg == "shutdown":
                self.running = False
                print "ShowRunner shutting down"
            elif msg == "clear":
                self.clear()
                time.sleep(0.2)
            elif msg.startswith("run_show:"):
                self.running = True
                show_name = msg[9:]
                self.next_show(show_name)
            elif msg.startswith("inc runtime"):
                self.max_show_time = int(msg.split(':')[1])

        elif isinstance(msg, tuple):
            # osc message
            # ('/1/command', [value])
            print "OSC:", msg

            (addr,val) = msg
            addr = addr.split('/z')[0]
            val = val[0]
            assert addr[0] == '/'
            (ns, cmd) = addr[1:].split('/')
            if ns == '1':
                # control command
                if cmd == 'next':
                    print "next show"
                    self.next_show()
                elif cmd == 'previous':
                    if self.prev_show:
                        self.next_show(self.prev_show.name)
                elif cmd == 'brightness':
                    self.send_OSC_cmd('brightness', int(val))
                    self.brightness_x = val
                    print "setting brightness to:", int(val)
                pass
            elif ns == '2':
                # show command - one of the 7 color buttons
                self.send_OSC_cmd('color', cmd[4:])

        else:
            print "ignoring unknown msg:", str(msg)

    def send_OSC_cmd(self, cmd, value):
        "Dump command to simulator.py"
        self.simulator.relay_OSC_cmd(cmd, value)

    def clear(self):
        self.model.clear()

    def next_show(self, name=None):
        s = None
        if name:
            if name in self.shows:
                s = self.shows[name]
            else:
                print "unknown show:", name

        if not s:
            print "choosing random show"
            s = self.randseq.next()

        self.clear()
        self.prev_show = self.show
        self.show = s(self.model)
        self.show.sunflower.set_random_family()  # Sets a new family random each time a new show starts
        print "next show: {} ({})".format(self.show.name, self.show.sunflower.num_spirals)
        self.framegen = self.show.next_frame()
        self.show_params = hasattr(self.show, 'set_param')
        self.show_runtime = 0

    def get_next_frame(self):
        "return a delay or None"
        try:
            return self.framegen.next()
        except StopIteration:
            return None

    def run(self):
        if not (self.show and self.framegen):
            self.next_show()

        while self.running:
            try:
                self.check_queue()

                delay = self.get_next_frame()   # Get the requested delay time

                if delay:
                    adj_delay = delay * SPEED_MULT

                    # Fade in & fade out shows
                    fade_time = 3  # In seconds. Adjust fade_time here

                    if self.show_runtime < fade_time:
                        fract = float(self.show_runtime) / fade_time
                    elif self.show_runtime > (self.max_show_time - fade_time):
                        fract = float(self.max_show_time - self.show_runtime) / fade_time
                    else:
                        fract = 1   # default: no fade

                    # Send all the next_frame data - don't change lights
                    self.model.go(fract)
                    self.model.send_delay(adj_delay)

                    time.sleep(adj_delay)  # The only delay!

                    self.show_runtime += adj_delay
                    if self.show_runtime > self.max_show_time:
                        print "max show time elapsed, changing shows"
                        self.next_show()
                else:
                    print "show is out of frames, waiting..."
                    time.sleep(2)
                    self.next_show()

            except Exception:
                print "unexpected exception in show loop!"
                traceback.print_exc()
                self.next_show()

def osc_listener(q, port=5700):
    "Create the OSC Listener thread"
    print "trying OSC"
    import osc_serve

    listen_address=('0.0.0.0', port)
    print "Starting OSC Listener on %s:%d" % listen_address
    osc = osc_serve.create_server(listen_address, q)
    st = threading.Thread(name="OSC Listener", target=osc.serve_forever)
    st.daemon = True
    return st

class SunServer(object):
    def __init__(self, sun_model, sun_simulator, args):
        self.args = args
        self.sun_model = sun_model
        self.sun_simulator = sun_simulator

        self.queue = Queue.LifoQueue()

        self.osc_thread = None

        self.runner = None

        self.running = False
        self._create_services()

    def _create_services(self):
        # OSC listener
        try:
            self.osc_thread = osc_listener(self.queue)
        except Exception, e:
            print "WARNING: Can't create OSC listener"

        # Show runner
        self.runner = ShowRunner(self.sun_model, self.sun_simulator,
            self.queue, args.max_time)

        if args.shows:
            print "setting show:", args.shows[0]
            self.runner.next_show(args.shows[0])

    def start(self):
        if self.running:
            print "start() called, but sunflower is already running!"
            return

        try:
            if self.osc_thread:
                self.osc_thread.start()
            self.runner.start()
            self.running = True
        except Exception, e:
            print "Exception starting Sunflowers!"
            traceback.print_exc()

    def stop(self):
        if self.running: # should be safe to call multiple times
            try:
                # OSC listener is a daemon thread so it will clean itself up

                # ShowRunner is shut down via the message queue
                self.queue.put("shutdown")

                self.running = False
            except Exception, e:
                print "Exception stopping Sunflowers!"
                traceback.print_exc()

    def go_headless(self, app):
        print "Running without web interface"
        try:
            while True:
                time.sleep(999) # control-c breaks out of time.sleep
        except KeyboardInterrupt:
            print "Exiting on keyboard interrupt"
            self.stop()


    def go_web(self, app):
        "Run with web interface"
        port = 9991
        config = {
            'global': {
                    'server.socket_host': '0.0.0.0',
                    'server.socket_port' : port
                    }
                }

        # cherrypy.quickstart(SunflowerWeb(app),
        #         '/',
        #         config=config)

class SunflowerWeb(object):
    def __init__(self, app):
        self.app = app
        self.runner = self.app.runner
        self.show_names = [s[0] for s in shows.load_shows()]
        self.redirect_home_html = "<script>setTimeout(function(){window.location='/'},3000)</script>"
        pass

    # @cherrypy.expose
    # def index(self):
    #     ret_html = "Shows:<br>"
    #     for i in self.show_names:
    #         ret_html += "<a href=/next_show?show_name=%s > %s </a><br>" % (i,i)
    #
    #     ret_html += """
    #     <form action="/show_time">
    #         <input type='text' name='show_time' value={0}></input>
    #         <input type='submit' value='set show time'></input>
    #     </form>
    #     """.format(int(self.runner.max_show_time))
    #     return ret_html
    #
    # @cherrypy.expose
    # def next_show(self, show_name=None):
    #     self.runner.queue.put("run_show:"+show_name)
    #     self.runner.queue.put("clear")
    #     ret_html = "<a href=/>HOME</a>"
    #     return ret_html + self.redirect_home_html
    #
    # @cherrypy.expose
    # def show_time(self, show_time=float(180)):
    #
    #     self.runner.max_show_time = float(show_time)
    #     ret_html = "this show will run for %s seconds (including time it's already run)" % show_time
    #     return ret_html + self.redirect_home_html
    #
    # @cherrypy.expose
    # def kill(self):
    #     cherrypy.engine.exit()
    #     self.app.stop()
    #     import sys
    #     sys.exit()

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Sunflowers Light Control')

    parser.add_argument('--max-time', type=float, default=float(60),
                        help='Maximum number of seconds a show will run (default 60)')

    # Simulator must run to turn on lights
    # parser.add_argument('--simulator',dest='simulator',action='store_true')

    parser.add_argument('--list', action='store_true', help='List available shows')
    parser.add_argument('shows', metavar='show_name', type=str, nargs='*',
                        help='name of show (or shows) to run')

    args = parser.parse_args()

    if args.list:
        print "Available shows:"
        print ', '.join([s[0] for s in shows.load_shows()])
        sys.exit(0)

    sim_host = "localhost"
    sim_port = 4444

    print "Using Sunfloewr Simulator at %s:%d" % (sim_host, sim_port)

    from model.simulator import SimulatorModel
    model = SimulatorModel(sim_host, port=sim_port)
    full_sunflowers = sunflower.load_sunflowers(model)

    app = SunServer(full_sunflowers, model, args)
    try:
        app.start() # start related service threads
        app.go_headless(app)
        #app.go_web(app)

    except Exception, e:
        print "Unhandled exception running Sunflowers!"
        traceback.print_exc()
    finally:
        app.stop()
