#!/usr/bin/env python

import os.path

# Description of the picture
title = "Brevent"
description = "A picture supposely taken from the Brevent."

# File name of the map
mapfile = "map-mont-blanc.png"

# File name of the picture
picturefile = "brevent.png"

# Dimension of the map (optional if map provided)
dimensions = (912, 1078)

# Expected position of the photographer (optional)
photographer = (262, 1078 - 213)

# Summits (as seen from left to right on the picture)
# - Latitude, Longitude coordinates
# - position on the map, in pixels, from left/bottom
# - position on the picture, in any unit, from left
points = [
    ("Aiguille du Midi",        None, (553, 1078 - 668),  35.5),
    ("Mont Blanc du Tacul",     None, (560, 1078 - 857),  45.0),
    ("Mont Maudit",             None, (488, 1078 - 933),  56.3),
    ("Mont Blanc",              None, (424, 1078 - 1056), 65.8),
    ("Dome du Gouter",          None, (298, 1078 - 974),  80.4),
    ("Aiguille du Gouter",      None, (226, 1078 - 904),  92.3),
    ("Aiguille de Bionnassay",  None, (153, 1078 - 1028), 97.2)
 ]

# Do not touch that!
names = [i[0] for i in points]
coordinates = [i[1] for i in points]
summits = [i[2] for i in points]
projections = [i[3] for i in points]
picture = os.path.join(os.path.dirname(__file__), picturefile)
map = os.path.join(os.path.dirname(__file__), mapfile)
