#!/usr/bin/env python

import os.path

# Description of the picture
title = "Aiguile du Midi 1"
description = "A picture taken from the Aiguille du Midi."

# File name of the map
mapfile = "map.png"

# File name of the picture
picturefile = "photo.png"

# Dimension of the map (optional if map provided)
dimensions = (1231, 669)

# Expected position of the photographer (optional)
photographer = (381, 669 - 436)

# Summits (as seen from left to right on the picture)
# - Latitude, Longitude coordinates
# - position on the map, in pixels, from left/bottom
# - position on the picture, in any unit, from left
points = [
    ("Aiguille du Triolet",  (45.9169134, 7.0246497), (1084, 669 - 158), 195)),
    ("Aiguille de Talefre",  (45.8999213, 7.0040026), (975, 669 - 285),  290)),
    ("Aiguille de Leschaux", (45.8874995, 7.0069444), (990, 669 - 375),  401)),
    ("Point Walker",         (45.8688259, 6.9879852), (904, 669 - 514),  573)),
    ("Dent du Geant",        (45.8622473, 6.9518381), (713, 669 - 562),  738))
]

# Do not touch that!
names = [i[0] for i in points]
coordinates = [i[1] for i in points]
summits = [i[2] for i in points]
projections = [i[3] for i in points]
picture = os.path.join(os.path.dirname(__file__), picturefile)
map = os.path.join(os.path.dirname(__file__), mapfile)
