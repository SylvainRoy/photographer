#!/usr/bin/env python

import os.path

# Description of the picture
title = "New-York"
description = "A picture taken from the statue of Liberty."

# File name of the map
mapfile = "map.png"

# File name of the picture
picturefile = "photo.jpg"

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
    ("High building on the very left",  (40.71357339189967, -74.04457939331341),  (297, 907 - 360),  163),
    ("Ellis Island West",               (40.698034419784015, -74.04355919100264),   (302, 907 - 451),  298),
    ("Big building on the left",        (40.713005039978285, -74.03381594560251),  (345, 907 - 363),  617),
    ("Ellis Island Tip of Triangle",    (40.69837141372243, -74.0382265425586),  (325, 907 - 448),  781),
    ("Empire State Building",           (40.74843545565188, -73.985665002613),   (556, 907 - 158), 1068),
    #("Thin skyscraper",                 (40.76637621595767, -73.98078036629533),  (592, 907 - 62),  1078), # To be fixed or removed.
    ("Freedom Tower",                   (40.71299406191319, -74.01316988147168),  (435, 907 - 363), 1251),
    ("Green roof",                      (40.70697390854156, -74.00967594592247),  (451, 907 - 398), 1555),
]

# Do not touch that!
names = [i[0] for i in points]
coordinates = [i[1] for i in points]
summits = [i[2] for i in points]
projections = [i[3] for i in points]
picture = os.path.join(os.path.dirname(__file__), picturefile)
map = os.path.join(os.path.dirname(__file__), mapfile)
