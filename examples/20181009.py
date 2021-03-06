#!/usr/bin/env python3

import sys, os, math
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from braid import *


Kicker = make(
        {'pitch': 64, 'envelope': 49, 'distortion': 50, 'sub': 51, 'body': 52, 'presence': 53, 'pan': 54, 'volume': 55},
        {'pitch': 90, 'envelope': 127, 'distortion': 0, 'sub': 0, 'body': 127, 'presence': 127, 'pan': 64, 'volume': 64}
        )

def note(self, pitch, velocity):
    # midi_out.send_note(self._channel, self._previous_pitch, 0)
    midi_out.send_control(self._channel, 55, midi_clamp(velocity * 127))                
    midi_out.send_note(self._channel, pitch, 127)
    self._previous_pitch = pitch
Kicker.note = note

midi_out.throttle = 2/1000

def pfix(p):
    assert p > 40
    p -= 41
    p *= 3 + 1/3
    p += 1/3
    p = math.floor(p) if p % 1 < .9 else math.ceil(p)
    return p

def k(n=Bb2):    
    def f(t):
        t.channel = 1
        t.pitch = 64
        t.pitch = pfix(n)    
        t.envelope = 64
        t.distortion = 32
        t.sub = 115    
        t.body = 127
        t.presence = 90
        t.velocity = 0.4
        return C1
    return f 

def s(t):
    t.channel = 2
    t.pitch = 64
    t.envelope = 127
    t.distortion = 0        
    t.sub = 0    
    t.body = 0
    t.presence = 127    
    t.velocity = 1.0
    return C1

def h(t):
    t.channel = 3
    t.pitch = 127
    t.envelope = 127
    t.distortion = 0    
    t.sub = 0    
    t.body = 127
    t.presence = 0
    t.velocity = 1.0
    return C1

def hp(t):
    t.channel = 3
    t.pitch = 100
    t.envelope = 127
    t.distortion = 0    
    t.sub = 0    
    t.body = 127
    t.presence = 100
    t.velocity = 0.5
    return C1

t1 = Kicker(1)
t2 = Kicker(2)
t3 = Kicker(3)
t4 = Thread(4)

tempo(120)
t1.pattern = [k(), s, k(), k(), s, k(), (k(), ([k(), s])), (s, (s, [s, 0, 0, s]))]
t2.pattern = [0, (h, [(h, 0), h])] * 4
t3.pattern = hp, 0, s, 0
t3.rate = 4/3

play()
