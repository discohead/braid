#!/usr/bin/env python3

from collections import deque
import sys, time, threading, queue, __main__, atexit
#from .midi import midi_in

from rtmidi.midiconstants import TIMING_CLOCK, SONG_CONTINUE, SONG_START, SONG_STOP
from rtmidi.midiutil import open_midiinput

LIVECODING = not hasattr(__main__, "__file__")

class MIDIClockReceiver:
    def __init__(self, bpm=None):
        self.bpm = bpm if bpm is not None else 120.0
        self._samples = deque()
        self._last_clock = None

    def __call__(self, event, data=None):
        msg, _ = event

        if msg[0] == TIMING_CLOCK:
            driver.run()
            now = time.time()
            if self._last_clock is not None:
                self._samples.append(now - self._last_clock)

            self._last_clock = now

            if len(self._samples) > 24:
                self._samples.popleft()

            if len(self._samples) >= 2:
                self.bpm = 2.5 / (sum(self._samples) / len(self._samples))
                tempo(self.bpm)

        elif msg[0] in (SONG_CONTINUE, SONG_START):
            play()
        elif msg[0] == SONG_STOP:
            stop()

class Driver(threading.Thread):

    def __init__(self):
        super(Driver, self).__init__()
        self.daemon = True
        self.threads = []
        self.grain = 0.01
        self.t = 0.0
        self.rate = 1.0
        self.previous_t = 0.0
        self.previous_cycles = 0
        self.running = False
        self._cycles = 0.0
        self._triggers = []
        self.start_t = time.time()
        self.midi_in, _ = open_midiinput(10)
        self.midi_in.set_callback(MIDIClockReceiver(120))
        self.midi_in.ignore_types(timing=False)

    def start(self):
        super(Driver, self).start()
        self.start_t = time.time()
        print("-------------> O")
        if not LIVECODING:
            try:
                while self.running:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                driver.stop()

    def run(self):
        self.t = time.time() - self.start_t
        if self.running:
            try:
                #midi_in.perform_callbacks()
                delta_t = self.t - self.previous_t
                self._cycles += delta_t * self.rate
                if int(self._cycles) != self.previous_cycles:
                    self.update_triggers()
                    self.previous_cycles = int(self._cycles)
                for thread in self.threads:
                    c = time.time()
                    try:
                        thread.update(delta_t)
                    except Exception as e:
                        print("\n[Error: \"%s\"]" % e)
                        thread.stop()
                        raise e
                    rc = int((time.time() - c) * 1000)
                    if rc > 1:
                        print("[Warning: update took %dms]\n>>> " % rc, end='')
            except KeyboardInterrupt:
                self.stop()
        self.previous_t = self.t
        #time.sleep(self.grain)

    def trigger(self, f=None, cycles=0, repeat=0):
        if f is None and repeat is False:
            self._triggers = [trigger for trigger in self._triggers if trigger[2] is not True]  # filter repeat=True
        elif f is False:
            self._triggers = []
        else:
            try:
                assert(callable(f))
                if cycles == 0:
                    assert repeat == 0
            except AssertionError as e:
                print("\n[Bad arguments for trigger]")
            else:
                self._triggers.append([f, cycles, repeat, 0])   # last parameter is cycle edges so far                

    def update_triggers(self):
        """Check trigger functions a fire as necessary"""
        updated = False
        for t, trigger in enumerate(self._triggers):
            trigger[3] += 1                             # increment edge
            if trigger[1] - trigger[3] == 0: 
                try:
                    trigger[0]()
                except Exception as e:
                    print("\n[Error: %s]" % e)
                if trigger[2] is True:
                    self.trigger(trigger[0], trigger[1], True)                  # create new trigger with same properties
                else:
                    trigger[2] -= 1
                    if trigger[2] > 0:
                        print("\n[Made new trigger with %s]" % trigger[2])
                        self.trigger(trigger[0], trigger[1], trigger[2] - 1)    # same, but decrement repeats
                self._triggers[t] = None                                         # clear this trigger
                updated = True
        if updated:
            self._triggers = [trigger for trigger in self._triggers if trigger is not None]

    def stop(self):
        self.running = False
        for thread in self.threads:
            if thread._running:
                thread.stop()

def tempo(value=False):
    """Convert to a multiplier of 1hz cycles"""
    if value:
        value /= 60.0
        value /= 4.0
        driver.rate = value
    else:
        return driver.rate * 4.0 * 60.0

def rate(value=False):
    """Cycles in hz"""
    if value:
        driver.rate = value
    else:
        return driver.rate

def play():
    driver.running = True
    if not driver.is_alive():
        driver.start()
    print("[Playing]")
    
def pause():
    driver.running = False
    for thread in driver.threads:
        thread.end()    
    print("[Paused]")

def stop():
    driver.stop()
    print("[Stopped]")

def clear():
    for thread in driver.threads:
        if thread._running:
            thread.stop()
    print("[Cleared]")

def exit_handler():
    driver.stop()
    time.sleep(0.1) # for midi to finish               
    print("\n-------------> X")    
atexit.register(exit_handler)    

driver = Driver()
trigger = driver.trigger

tempo(120)

