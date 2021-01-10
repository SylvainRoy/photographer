#!/usr/bin/env python

import os.path

# Description of the picture
title = "Brevent"
description = "A picture supposely taken from the Brevent."

# File name of the map
mapfile = "map-mont-blanc.png"

# File name of the picture
picturefile = "brevent.png"

# Dimension of the map
dimensions = (912, 1078)

# Expected position of the photographer (optionnal)
photographer = (262, 1078 - 213)

# Summits (as seen from left to right on the picture)
# - position on the map, in pixels, from left/bottom
# - position on the picture, in any unit, from left
points = [
    ("Aiguille du Midi",        (553, 1078 - 668),  35.5),
    ("Mont Blanc du Tacul",     (560, 1078 - 857),  45.0),
    ("Mont Maudit",             (488, 1078 - 933),  56.3),
    ("Mont Blanc",              (424, 1078 - 1056), 65.8),
    ("Dome du Gouter",          (298, 1078 - 974),  80.4),
    ("Aiguille du Gouter",      (226, 1078 - 904),  92.3),
    ("Aiguille de Bionnassay",  (153, 1078 - 1028), 97.2)
 ]

# Do not touch that!
names = [i[0] for i in points]
summits = [i[1] for i in points]
projections = [i[2] for i in points]
picture = os.path.join(os.path.dirname(__file__), picturefile)
map = os.path.join(os.path.dirname(__file__), mapfile)
