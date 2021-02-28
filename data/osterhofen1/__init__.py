#!/usr/bin/env python

import os.path

# Description of the picture
title = "Osterhfen1"
description = "Picture from the area of Osterhofen."

# File name of the map
mapfile = "map.png"

# File name of the picture
picturefile = "photo.jpg"

# Dimension of the map (optional if map provided)
dimensions = (1992, 1440)

# Expected position of the photographer (optional)
photographer = (118, 1440 - 106)
photographerlocation = (47.6936172, 12.0120771)

# Summits (as seen from left to right on the picture)
# - Latitude, Longitude coordinates
# - position on the map, in pixels, from left/bottom
# - position on the picture, in any unit, from left
points = [
    ("A",  (47.5616417, 12.3238219), (1826, 1440 - 1170), 1578),
    ("B",  (47.5586216, 12.3047467), (1756, 1440 - 1212), 1698),
    ("C",  (47.5609407, 12.273977),  (1629, 1440 - 1203), 1795),
    ("D",  (47.5546868, 12.2912554), (1692, 1440 - 1272), 1822),
    ("E",  (47.6478753, 12.0971038), ( 564, 1440 -  480), 2009),
    ("F",  (47.6528517, 12.0833429), ( 499, 1440 -  446), 2148),
    ("G",  (47.6472724, 12.0870046), ( 500, 1440 -  475), 2230),
    ("H",  (47.675739,  12.0426313), ( 279, 1440 -  261), 2246)
 ]

# Do not touch that!
names = [i[0] for i in points]
coordinates = [i[1] for i in points]
summits = [i[2] for i in points]
projections = [i[3] for i in points]
picture = os.path.join(os.path.dirname(__file__), picturefile)
map = os.path.join(os.path.dirname(__file__), mapfile)
