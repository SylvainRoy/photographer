#!/usr/bin/env python

import os.path

# Description of the picture
description = """A picture supposely taken from the Brevent.
Distance are in mm on a map at 1/25000.
"""

# Dimension of the map
map = (15*40, 19*40)

# Expected position of the photographer (optionnal)
photographer = (9*40+15, 17*40+39)

# File name of the picture
picturefile = "brevent.jpg"

# Summits (as seen from left to right)
points = [
    ("Aiguille du Midi", (13*40+2, 11*40+29), 35.5),
    ("Mont Blanc du Tacul", (13*40+1, 9*40+11), 45.0),
    ("Mont Maudit", (12*40+3, 8*40+12), 56.3),
    ("Mont Blanc", (11*40+5, 6*40+27), 65.8),
    ("Dome du Gouter", (9*40+21, 7*40+33), 80.4),
    ("Aiguille du Gouter", (8*40+25, 8*40+3), 92.3),
    ("Aiguille de Bionnassay", (7*40+23, 7*40+6), 97.2)
    ]

names = [i[0] for i in points]
summits = [i[1] for i in points]
projections = [i[2] for i in points]
picture = os.path.join(os.path.dirname(__file__), picturefile)

