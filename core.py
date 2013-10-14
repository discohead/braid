#!/usr/bin/env python3

import time, threading, queue
from .util import osc, log

class Driver(object):

    def __init__(self):
        self.voices = []
        self.grain = 0.01   # hundredths are nailed by Granu, w/o load. ms are ignored.
        self.t = 0.0
        self.previous_t = 0.0
        self.callbacks = []
        self.running = True

    def start(self, skip=0):
        start_t = time.time() - skip
        last_cue = -1
        while self.running:
            self.t = time.time() - start_t
            if int(self.t) // 15 != last_cue:
                last_cue = int(self.t) // 15
                log.info("/////////////// [%s] %d:%f ///////////////" % (last_cue, self.t // 60.0, self.t % 60.0))                        
            controller.perform_callbacks()
            self._perform_callbacks()
            if not self.running:
                break
            delta_t = self.t - self.previous_t
            for voice in self.voices:
                voice.update(delta_t)
            self.previous_t = self.t                
            time.sleep(self.grain)

    def stop(self):
        self.running = False
        for voice in self.voices:
            voice.end()
        log.info("/////////////// END %d:%f ///////////////" % (self.t // 60.0, self.t % 60.0)) 
        time.sleep(1) # for osc to finish        

    def callback(self, duration, f):
        """After a given duration, call a function"""
        t = self.t + duration
        self.callbacks.append((t, f))        

    def _perform_callbacks(self):
        for c, callback in enumerate(self.callbacks):
            t, f = callback
            if t <= self.t:
                f()
                self.callbacks.remove(callback)


class Synth(threading.Thread):
    """Consume notes and send OSC"""

    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.sender = osc.Sender(5280)
        self.queue = queue.Queue()
        self.start()

    def send(self, address, *params):
        self.queue.put((address, params))

    def run(self):
        while True:
            address, params = self.queue.get()            
            self.sender.send(address, params)


class Controller(object):
    """Receive OSC and perform callbacks"""

    def __init__(self):
        self.callbacks = {}
        self.queue = queue.Queue()
        def message_handler(location, address, data):
            if address != '/braid/control':
                continue
            control, value = data
            self.queue.put(control, value)
        self.receiver = osc.Receiver(5281, message_handler)

    def callback(self, control, f):
        """For a given control message, call a function"""
        self.callbacks[control] = f

    def perform_callbacks(self):
        while True
            try:
                control, value = self.queue.get_nowait()
            except queue.Empty:
                return
            if control in self.callbacks:
                self.callbacks[control](value)


synth = Synth()
controller = Controller()
driver = Driver()


