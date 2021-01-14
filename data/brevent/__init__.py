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
photographerlocation = (45.9338534, 6.837519)

# Summits (as seen from left to right on the picture)
# - Latitude, Longitude coordinates
# - position on the map, in pixels, from left/bottom
# - position on the picture, in any unit, from left
points = [
    ("Aiguille du Midi",        (45.8793106, 6.8874243), (553, 1078 - 668),  35.5),
    ("Mont Blanc du Tacul",     (45.8566202, 6.8878189), (560, 1078 - 857),  45.0),
    ("Mont Maudit",             (45.8479158, 6.8749911), (488, 1078 - 933),  56.3),
    ("Mont Blanc",              (45.8326218, 6.8651749), (424, 1078 - 1056), 65.8),
    ("Dome du Gouter",          (45.8428166, 6.8434424), (298, 1078 - 974),  80.4),
    ("Aiguille du Gouter",      (45.8508455, 6.831278), (226, 1078 - 904),  92.3),
    ("Aiguille de Bionnassay",  (45.8357347, 6.8184001), (153, 1078 - 1028), 97.2)
 ]

# Do not touch that!
names = [i[0] for i in points]
coordinates = [i[1] for i in points]
summits = [i[2] for i in points]
projections = [i[3] for i in points]
picture = os.path.join(os.path.dirname(__file__), picturefile)
map = os.path.join(os.path.dirname(__file__), mapfile)
