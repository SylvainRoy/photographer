#!/usr/bin/env python

import os.path

# Description of the picture
title = "Aiguile du Midi 2"
description = "A picture of Chamonix taken from the Aiguille du Midi."

# File name of the map
mapfile = "map.png"

# File name of the picture
picturefile = "photo.png"

# Dimension of the map (optional if map provided)
dimensions = (809, 844)

# Expected position of the photographer (optional)
photographer = (464, 844 - 568)

# Summits (as seen from left to right on the picture)
# - Latitude, Longitude coordinates
# - position on the map, in pixels, from left/bottom
# - position on the picture, in any unit, from left
points = [
    ("River",                     None, (145, 844 - 403), 287),
    ("River end",                 None, (235, 844 - 337), 407),
    ("River - Tunnel Mont Blanc", None, (306, 844 - 407), 413),
    ("Brevent top",               None, (188, 844 - 142), 481),
    ("Brevent middle",            None, (276, 844 - 136), 542),
    ("Brevent bottom",            None, (325, 844 - 230), 553),
    ("Lac Bleu",                  None, (482, 844 - 388), 743),
    ("Forest Corner",             None, (496, 844 - 72),  725)
]

# Do not touch that!
names = [i[0] for i in points]
coordinates = [i[1] for i in points]
summits = [i[2] for i in points]
projections = [i[3] for i in points]
picture = os.path.join(os.path.dirname(__file__), picturefile)
map = os.path.join(os.path.dirname(__file__), mapfile)
