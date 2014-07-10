from random import randint, choice, random

class Scale(list):

    """Allows for specifying scales by degree, up to one octave below and two octaves above"""
    """Any number of scale steps is supported, but for MAJ: """
    """ -1, -2, -3, -4, -5, -6, -7, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14"""
    """use the +- OCT convention otherwise"""

    def __init__(self, *args):
        list.__init__(self, *args)

    def __getitem__(self, degree):
        if not ((type(degree) == int or degree == R) and degree != 0):
            raise ScaleError(degree)
        octave_shift = 0
        if degree == R:
            degree = list.__getitem__(self, randint(0, len(self) - 1))
        if degree > len(self) * 2 or degree < 0 - len(self):
            raise ScaleError(degree)
        if degree < 0:
            degree = abs(degree)
            octave_shift -= 12
        if degree > len(self):
            octave_shift += ((degree - 1) // len(self)) * 12
        degree = ((degree - 1) % len(self)) + 1
        semitone = list.__getitem__(self, degree - 1)
        semitone += octave_shift
        return semitone

    def rotate(self, steps):
        l = list(self)
        scale = l[steps:] + l[:steps]
        scale = [degree - scale[0] for degree in scale]
        scale = [(degree + 12) if degree < 0 else degree for degree in scale]
        return Scale(scale)

    def add(self, degree, steps):
        """Just returns original degree if result is invalid, which may be surprising"""
        if steps < 0:
            return self.subtract(degree, abs(steps))
        assert(steps > -1)
        self[degree] # check validity
        if degree > 0:
            return degree if degree + steps > len(self) * 2 else degree + steps
        else:
            d = abs((degree - steps) + len(self)) if degree - steps < 0 - len(self) else degree - steps
            return d if d < len(self) * 2 else degree

    def subtract(self, degree, steps):
        """Just returns original degree if result is invalid, which may be surprising"""
        if steps < 0:
            return self.add(degree, abs(steps))        
        assert(steps > -1)
        self[degree] # check validity
        if degree < 0:
            return degree if degree + steps > -1 else degree + steps
        else:
            if degree - steps < 0 - len(self):
                return degree
            else:
                return (0 - len(self)) + abs(degree - steps) if degree - steps < 1 else degree - steps
            

class ScaleError(Exception):
    def __init__(self, degree):
        self.degree = degree
    def __str__(self):
        return repr("Illegal scale degree '%s'" % self.degree)

K = 36
S = 38
H = 42

C0 = 12
Db0 = 13
D0 = 14
Eb0 = 15
E0 = 16
F0 = 17
Gb0 = 18
G0 = 19
Ab0 = 20
A0 = 21
Bb0 = 22
B0 = 23

C1 = 24
Db1 = 25
D1 = 26
Eb1 = 27
E1 = 28
F1 = 29
Gb1 = 30
G1 = 31
Ab1 = 32
A1 = 33
Bb1 = 34
B1 = 35

C2 = 36
Db2 = 37
D2 = 38
Eb2 = 39
E2 = 40
F2 = 41
Gb2 = 42
G2 = 43
Ab2 = 44
A2 = 45
Bb2 = 46
B2 = 47

C3 = 48
Db3 = 49
D3 = 50
Eb3 = 51
E3 = 52
F3 = 53
Gb3 = 54
G3 = 55
Ab3 = 56
A3 = 57
Bb3 = 58
B3 = 59

C = C4 = 60
Db = Db4 = 61
D = D4 = 62
Eb = Eb4 = 63
E = E4 = 64
F = F4 = 65
Gb = Gb4 = 66
G = G4 = 67
Ab = Ab4 = 68
A = A4 = 69
Bb = Bb4 = 70
B = B4 = 71

C5 = 72
Db5 = 73
D5 = 74
Eb5 = 75
E5 = 76
F5 = 77
Gb5 = 78
G5 = 79
Ab5 = 80
A5 = 81
Bb5 = 82
B5 = 83

C6 = 84
Db6 = 85
D6 = 86
Eb6 = 87
E6 = 88
F6 = 89
Gb6 = 90
G6 = 91
Ab6 = 92
A6 = 93
Bb6 = 94
B6 = 95

C7 = 96
Db7 = 97
D7 = 98
Eb7 = 99
E7 = 100
F7 = 101
Gb7 = 102
G7 = 103
Ab7 = 104
A7 = 105
Bb7 = 106
B7 = 107

C8 = 108
Db8 = 109
D8 = 110
Eb8 = 111
E8 = 112
F8 = 113
Gb8 = 114
G8 = 115
Ab8 = 116
A8 = 117
Bb8 = 118
B8 = 119

# western modes / chords

ION = MAJ = Scale([0, 2, 4, 5, 7, 9, 11])

DOR = ION.rotate(1)

PRG = SUSb9 = ION.rotate(2)

LYD = ION.rotate(3)

MYX = DOM = ION.rotate(4)

AOL = ION.rotate(5)

LOC = ION.rotate(6)

MIN = Scale([0, 2, 3, 5, 7, 8, 11])

BLU = Scale([0, 3, 5, 6, 7, 10])

# PEN = Scale([])

# chromatic

CHR = Scale([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])


# gamelan

SDR = Scale([0, 2, 5, 7, 9])

PLG = Scale([0, 1, 3, 6, 7, 8, 10])


# personal

JAM = Scale([0, 2, 3, 5, 6, 7, 10, 11])


#

R = 'R'         # random
Z = 'REST'      # rest
P = 'PREV'      # previous note

OCT = 12


