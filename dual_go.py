#!/usr/bin/env python2.7
import sys
import time
import traceback
import threading

import sunflower
import shows

#
#  Dual Shows running that fade into each other
#    Enabled by two instances of the ShowRunner object
#    SunServer's self.channel is now self.channels
#
#  Cleaning up go.py Nov 2018
#
#  ripping out OSC controller, queue
#

# import cherrypy  # Removing OSC

NUM_CHANNELS = 2  # Dual channels
SHOW_TIME = 30  # Time of shows in seconds
FADE_TIME = 10  # Fade In + Out times in seconds
SPEED_MULT = 4 # Multiply every delay by this value. Higher = much slower shows


class ShowRunner(threading.Thread):
    def __init__(self, model, simulator, max_showtime=1000, channel=0):
        super(ShowRunner, self).__init__(name="ShowRunner")
        self.model = model
        self.simulator = simulator
        self.running = True
        self.max_show_time = max_showtime
        self.show_runtime = 0
        self.time_since_reset = 0
        self.channel = channel
        self.lock = threading.Lock()  # Prevent overlapping messages

        # map of names -> show constructors
        self.shows = dict(shows.load_shows())
        self.randseq = shows.random_shows()

        # current show object & frame generator
        self.show = None
        self.framegen = None
        self.prev_show = None
        self.show_params = None

    def clear(self):
        self.model.clear()

    def next_show(self, name=None):
        s = None
        if name:
            if name in self.shows:
                s = self.shows[name]
            else:
                print ("unknown show: {}".format(name))

        if not s:
            print ("choosing random show")
            s = next(self.randseq)

        self.clear()
        self.prev_show = self.show
        self.show = s(self.model)
        self.framegen = self.show.next_frame()
        self.show_params = hasattr(self.show, 'set_param')
        self.time_since_reset = 0
        if self.channel == 0:
            self.show_runtime = 0  # Don't reset other channels' clocks

        print ("next show for channel {}: {}".format(self.channel, self.show.name))

    def get_next_frame(self):
        """return a delay or None"""
        try:
            return self.framegen.next()
        except StopIteration:
            return None

    def run(self):
        if not (self.show and self.framegen):
            self.next_show()

        while self.running:
            try:
                delay = self.get_next_frame()  # float

                # # Print python heap size
                # megabytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1000000
                # if megabytes > 30:
                #     print "Using: {}Mb".format(megabytes)

                # print "{}: {}".format(self.simulator.channel, self.show_runtime)

                adj_delay = delay * SPEED_MULT

                intensity = self.get_intensity()

                # LOCK: Send all the next_frame data - don't change lights
                with self.lock:
                    self.model.send_intensity(intensity)
                    if intensity > 0:
                        self.model.go()
                        self.model.send_delay(adj_delay)

                time.sleep(adj_delay)  # The only delay!

                self.show_runtime += adj_delay
                self.time_since_reset += adj_delay

                if self.show_runtime >= self.max_show_time and self.time_since_reset > FADE_TIME:
                    print ("max show time elapsed, changing shows")
                    self.next_show()

            except Exception:
                print ("unexpected exception in show loop!")
                traceback.print_exc()
                self.next_show()

    def stop(self):
        self.running = False

    def get_intensity(self):
        """Return a 0-255 intensity (off -> on) depending on where
           show_runtime is along towards max_show_time"""
        if self.show_runtime <= FADE_TIME:
            intensity = 255 * self.show_runtime / FADE_TIME
        elif self.show_runtime <= self.max_show_time / 2.0:
            intensity = 255
        elif self.show_runtime <= (self.max_show_time / 2.0) + FADE_TIME:
            intensity = 255 * (FADE_TIME - (self.show_runtime - (self.max_show_time / 2.0))) / FADE_TIME
        else:
            intensity = 0
        return int(round(intensity))


class SunServer(object):
    def __init__(self, sun_model, sun_simulator, args):
        self.args = args
        self.sun_model = sun_model
        self.sun_simulator = sun_simulator
        self.runner = None
        self.running = False
        self._create_services()

    def _create_services(self):
        """Set up the ShowRunners and launch the first shows"""
        self.runner = ShowRunner(self.sun_model,
                                 self.sun_simulator,
                                 args.max_time,
                                 self.sun_simulator.get_channel())

        if args.shows:
            named_show = args.shows[0]
            print ("setting show: ".format(named_show))
            self.runner.next_show(named_show)

    def start(self):
        try:
            self.runner.start()
            self.running = True
        except Exception as e:
            print ("Exception starting Triangles!")
            traceback.print_exc()

    def stop(self):
        if self.running:  # should be safe to call multiple times
            try:
                self.running = False
                self.runner.stop()
            except Exception as e:
                print ("Exception stopping Triangles! {}".format(e))
                traceback.print_exc()


if __name__ == '__main__':
    # Simulator must run in Processing to turn on lights
    import argparse

    parser = argparse.ArgumentParser(description='Sunflower Light Control')
    parser.add_argument('--max-time', type=float, default=float(SHOW_TIME),
                        help='Maximum number of seconds a show will run (default {})'.format(SHOW_TIME))
    parser.add_argument('--list', action='store_true', help='List available shows')
    parser.add_argument('shows', metavar='show_name', type=str, nargs='*',
                        help='name of show (or shows) to run')

    args = parser.parse_args()

    if args.list:
        print ("Available shows:")
        print (', '.join([s[0] for s in shows.load_shows()]))
        sys.exit(0)

    sim_host = "localhost"
    sim_port = 4444  # base port number

    print ("Using Sunflower Simulator at {}:{}-{}".format(sim_host, sim_port, sim_port + NUM_CHANNELS - 1))

    from model.simulator import SimulatorModel
    # Get ready for DUAL channels
    # Each channel (app) has its own ShowRunner and SimulatorModel
    channels = []  # array of channel objects
    for i in range(NUM_CHANNELS):
        model = SimulatorModel(sim_host, i, port=sim_port+i)
        full_sunflower = sunflower.load_sunflowers(model)
        channels.append(SunServer(full_sunflower, model, args))

    try:
        for channel in channels:
            channel.start()  # start related service threads

        while True:
            # Force channel 1 out of phase with channel 2 by 50%
            channels[1].runner.show_runtime = (channels[0].runner.show_runtime + (SHOW_TIME / 2.0)) % SHOW_TIME
            time.sleep(1)

    except KeyboardInterrupt:
        for channel in channels:
            channel.stop()
        print ("Exiting on keyboard interrupt")

    finally:
        for channel in channels:
            channel.stop()