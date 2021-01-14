#!/usr/bin/env python

import os.path

# Description of the picture
title = "New-York"
description = "A picture taken from the statue of Liberty."

# File name of the map
mapfile = "map.png"

# File name of the picture
picturefile = "photo.png"

# Dimension of the map (optional if map provided)
dimensions = (814, 907)

# Expected position of the photographer (optional)
photographer = None
photographerlocation = None

# Summits (as seen from left to right on the picture)
# - Latitude, Longitude coordinates
# - position on the map, in pixels, from left/bottom
# - position on the picture, in any unit, from left
points = [
    ("Thin skyscraper",                 (40.7650619, -73.9773295),  (592, 907 - 62),  1078),
    ("Empire State Building",           (40.7483735, -73.985603),   (556, 907 - 158), 1068),
    ("Freedom Tower",                   (40.7131094, -74.0130809),  (435, 907 - 363), 1251),
    ("High building on the very left",  (40.7136346, -74.0446077),  (297, 907 - 360), 163),
    ("Big building on the left",        (40.7130429, -74.0340377),  (345, 907 - 363), 619),
    ("Green roof",                      (40.7109769, -74.0034396),  (451, 907 - 398), 1555),
    ("Ellis Island Tip of Triangle",    (40.6980437, -74.0393193),  (325, 907 - 448), 781),
    ("Ellis Island West",               (40.697827, -74.043181),    (302, 907 - 451), 297),
]

# Do not touch that!
names = [i[0] for i in points]
coordinates = [i[1] for i in points]
summits = [i[2] for i in points]
projections = [i[3] for i in points]
picture = os.path.join(os.path.dirname(__file__), picturefile)
map = os.path.join(os.path.dirname(__file__), mapfile)
