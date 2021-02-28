#!/usr/bin/env python

import os.path

# Description of the picture
title = "Osterhfen2"
description = "Picture from the area of Osterhofen."

# File name of the map
mapfile = "map.png"

# File name of the picture
picturefile = "photo2.jpg"

# Dimension of the map (optional if map provided)
dimensions = (1425, 1825)

# Expected position of the photographer (optional)
photographer = (801, 1825 - 1108)
photographerlocation = (47.6934477, 12.0122436)

# Summits (as seen from left to right on the picture)
# - Latitude, Longitude coordinates
# - position on the map, in pixels, from left/bottom
# - position on the picture, in any unit, from left
points = [
    ("A",  (47.6476271, 12.0365671), (641, 1825 - 814),  564),
    ("B",  (47.6650528, 12.017313),  (750, 1825 - 932), 1437),
    ("C",  (47.6735181, 12.0152408), (769, 1825 - 971), 1622),
    ("D",  (47.5686809, 12.0161495), (647, 1825 - 318), 1691),
    ("E",  (47.5395073, 12.0110591), (643, 1825 -  76), 1800),
    ("F",  (47.6357283, 12.0016263), (833, 1825 - 901), 2873),
 ]

# Do not touch that!
names = [i[0] for i in points]
coordinates = [i[1] for i in points]
summits = [i[2] for i in points]
projections = [i[3] for i in points]
picture = os.path.join(os.path.dirname(__file__), picturefile)
map = os.path.join(os.path.dirname(__file__), mapfile)
