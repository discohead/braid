#!/usr/bin/env python3

from braid import *

# degrees per year from 1987 to 2012
bachelors = 32710.00, 33004.00, 34386.00, 35957.00, 38084.00, 43982.00, 45252.00, 46518.00, 46327.00, 46698.00, 47566.00, 49591.00, 51739.00, 55970.00, 48132.00, 51848.00, 56667.00, 74127.00, 78004.00, 80368.00, 82457.00, 85116.00, 86760.00, 87155.00, 89318.00, 91222.00
masters = 8061.00, 7524.00, 7606.00, 8049.00, 7528.00, 8773.00, 8984.00, 9462.00, 9567.00, 9704.00, 10007.00, 6610.00, 10905.00, 10390.00, 10827.00, 10998.00, 11437.00, 12350.00, 12628.00, 13011.00, 13146.00, 13568.00, 14257.00, 14296.00, 14863.00, 15929.00
doctors = 771.00, 716.00, 740.00, 827.00, 799.00, 864.00, 828.00, 973.00, 1012.00, 1006.00, 1006.00, 1095.00, 1078.00, 1089.00, 347.00, 1087.00, 1271.00, 1261.00, 1252.00, 1365.00, 1342.00, 1197.00, 840.00, 1572.00, 1618.00, 1693.00

bachelors_f = signal_from_timeseries(bachelors)
masters_f = signal_from_timeseries(masters)
doctors_f = signal_from_timeseries(doctors)

plot(bachelors_f, color="red")
plot(masters_f, color="blue")
plot(doctors_f, color="green")
show_plots()


tempo(132)

DURATION = 30

FIT = Scale([0, 2, 4, 5, 7, 9, 10])
FIT2 = Scale([0, 2, 4, 7, 9, 12, 14, 16, 19])

def h(v):
    step = math.floor(v.ref() * v.steps) + 1
    return step

bv = Voice(1)
bv.steps = 6                    # regular python attribute
bv.add('ref')                   # new tweenable braid param
bv.chord.set((C2, FIT))         # existing braid param
bv.ref.tween(1.0, 4, bachelors_f, repeat=True, flip=False)    # create a reference tween
bv.set([h, (h, [h, h]), h, 0, h, (h, [h, h]), 0, h])

mv = Voice(2)
mv.steps = 18
mv.chord.set((C4, FIT2))
mv.add('ref')
mv.ref.tween(1.0, 8, masters_f, repeat=True, flip=False)
mv.set([(h, [h, h]), h, 0, h, (h, [h, h]), 0, h, h])

dv = Voice(3)
dv.steps = 10
dv.chord.set((C4, FIT2))
dv.add('ref')
dv.ref.tween(1.0, 16, doctors_f, repeat=True, flip=False)
dv.set([h, h, (h, [h, h]), h, 0, h, (h, [h, h]), 0])

kick = Drums()
snare = Drums()
hat = Drums()
kick.set([1, 1, 1, 1])
snare.set([0, [2, 0, 0, (0, 2, 0.7)], 0, [2, 0, 0, (0, 2, 0.7)]])
hat.set([(0, [5, 5]), [5, 5], (0, [5, 5]), [5, 5]] * 2)


mv.mute.set(True)
kick.mute.set(True)
snare.mute.set(True)
hat.mute.set(True)

on_t(0, lambda: hat.mute.set(False))
on_t(0, lambda: bv.mute.set(False))
bv.velocity.set(0.0)
def fade_bass():
    bv.velocity.tween(1.0, 8.0)
on_t(1, fade_bass)
on_t(8, lambda: kick.mute.set(False))
on_t(15, lambda: snare.mute.set(False))

on_t(32, lambda: mv.mute.set(False))
##
def fade_bass_down():
    bv.velocity.tween(0.0, 8.0)
on_t(48, fade_bass_down)
on_t(48, lambda: snare.mute.set(True))
on_t(48, lambda: hat.mute.set(True))

dv.velocity.set(0.0)
def fade_dv():
    dv.velocity.tween(1.0, 8.0)
on_t(50, fade_dv)

on_t(68, lambda: hat.mute.set(False))

def bv_loud():
    bv.velocity.set(1.0)
on_t(74, bv_loud)    
on_t(74, lambda: bv.mute.set(False))
on_t(74, lambda: snare.mute.set(False))
on_t(74, lambda: dv.mute.set(False))


play()
