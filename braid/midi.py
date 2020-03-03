#!/usr/bin/env python3

from collections import deque
import sys, time, threading, atexit, queue, rtmidi
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, CONTROLLER_CHANGE, TIMING_CLOCK, SONG_START, SONG_CONTINUE, SONG_STOP
from . import num_args
from .core import driver, tempo, play, stop, clear, pause

log_midi = False

class MidiOut(threading.Thread):

    def __init__(self, interface=0, throttle=0):
        threading.Thread.__init__(self)
        self.daemon = True
        self._interface = interface
        self.throttle = throttle
        self.queue = queue.Queue()
        self.midi = rtmidi.MidiOut()
        available_interfaces = self.scan()
        if available_interfaces:
            if self._interface >= len(available_interfaces):
                print("Interface index %s not available" % self._interface)
                return
            print("MIDI OUT: %s" % available_interfaces[self._interface])
            self.midi.open_port(self._interface)
        else:
            print("MIDI OUT opening virtual interface 'Braid'...")
            self.midi.open_virtual_port('Braid')
        self.start()

    def scan(self):
        available_interfaces = self.midi.get_ports()
        if len(available_interfaces):
            print("MIDI outputs available: %s" % available_interfaces)
        else:
            print("No MIDI outputs available")
        return available_interfaces

    def send_control(self, channel, control, value):
        self.queue.put((channel, (control, value), None))

    def send_note(self, channel, pitch, velocity):
        self.queue.put((channel, None, (pitch, velocity)))

    @property
    def interface(self):
        return self._interface

    @interface.setter
    def interface(self, interface):
        self.__init__(interface=interface, throttle=self.throttle)

    def run(self):
        while True:
            channel, control, note = self.queue.get()
            if control is not None:
                control, value = control
                if type(value) == bool:
                    value = 127 if value else 0
                if log_midi:
                    print("MIDI ctrl %s %s %s" % (channel, control, value))
                channel -= 1
                self.midi.send_message([CONTROLLER_CHANGE | (channel & 0xF), control, value])
            if note is not None:
                pitch, velocity = note
                if log_midi:
                    print("MIDI note %s %s %s" % (channel, pitch, velocity))
                channel -= 1
                if velocity:
                    self.midi.send_message([NOTE_ON | (channel & 0xF), pitch & 0x7F, velocity & 0x7F])
                else:
                    self.midi.send_message([NOTE_OFF | (channel & 0xF), pitch & 0x7F, 0])
            if self.throttle > 0:
                time.sleep(self.throttle)


class MidiIn(threading.Thread):

    def __init__(self, interface=0):
        threading.Thread.__init__(self)
        self.daemon = True
        self._interface = interface
        self.queue = queue.Queue()
        self.midi = rtmidi.MidiIn()
        self.midi.ignore_types(timing=False)
        self.callbacks = {}
        self.threads = []
        self._samples = deque()
        self._last_clock = None
        self.bpm = 120
        available_interfaces = self.scan()
        if available_interfaces:
            if self._interface >= len(available_interfaces):
                print("Interface index %s not available" % self._interface)
                return
            print("MIDI IN: %s" % available_interfaces[self._interface])
            self.midi.open_port(self._interface)
        self.start()

    def scan(self):
        available_interfaces = self.midi.get_ports()
        if 'Braid' in available_interfaces:
            available_interfaces.remove('Braid')
        if len(available_interfaces):
            print("MIDI inputs available: %s" % available_interfaces)
        else:
            print("No MIDI inputs available")
        return available_interfaces

    @property
    def interface(self):
        return self._interface

    @interface.setter
    def interface(self, interface):
        self.__init__(interface=interface)

    def run(self):
        def receive_message(event, data=driver):
            msg, _ = event
            if msg[0] == TIMING_CLOCK:
                data.run()
                self.perform_callbacks()
                now = time.time()
                if self._last_clock is not None:
                    self._samples.append(now - self._last_clock)

                self._last_clock = now

                if len(self._samples) > 24:
                    self._samples.popleft()

                if len(self._samples) >= 2:
                    self.bpm = 2.5 / (sum(self._samples) / len(self._samples))
                    tempo(self.bpm)

            elif msg[0] in (SONG_START, SONG_CONTINUE):
                data.running = True
                for thread in data.threads:
                    if not thread._running:
                        thread._running = True
                        thread._cycles = 0.0
                        thread._last_edge = 0
                        thread._index = -1
            elif msg[0] == SONG_STOP:
                data.running = False
                for thread in data.threads:
                    if thread._running:
                        thread._running = False
                        thread.rest()
            elif msg[0] < 144:
                nop, control, value = msg
                self.queue.put((control, value / 127.0))
            else:
                if len(msg) < 3:
                    return  ## ?
                channel, pitch, velocity = msg
                channel -= 144
                if channel < len(self.threads):
                    thread = self.threads[channel]
                    thread.note(pitch, velocity)
        self.midi.set_callback(receive_message, data=driver)
        while True:
            time.sleep(0.1)

    def perform_callbacks(self):
        while True:
            try:
                control, value = self.queue.get_nowait()
            except queue.Empty:
                return
            if control in self.callbacks:
                if num_args(self.callbacks[control]) > 0:
                    self.callbacks[control](value)
                else:
                    self.callbacks[control]()


    def callback(self, control, f):
        """For a given control message, call a function"""
        self.callbacks[control] = f


midi_out = MidiOut(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
midi_in = MidiIn(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
time.sleep(0.5)
print("MIDI ready")
