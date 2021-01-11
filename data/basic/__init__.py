#!/usr/bin/env python

import os.path
from math import sqrt

# Description of the picture
title = "Fake data"
description = """Fake data for testing."""

# Dimension of the map
map = (500, 500)

# Expected position of the photographer (optionnal)
photographer = (100, 100)

# File name of the picture
picturefile = "none"

# Summits (as seen from left to right)
points = [
    ("A", None, (100, 400), -75*sqrt(2)),
    ("B", None, (200, 300), -25*sqrt(2)),
    ("C", None, (400, 400), 0),
    ("D", None, (400, 250), 25*sqrt(2)),
    ("E", None, (300, 100), 75*sqrt(2))
]

# Do not touch that!
names = [i[0] for i in points]
coordinates = [i[1] for i in points]
summits = [i[2] for i in points]
projections = [i[3] for i in points]
picture = os.path.join(os.path.dirname(__file__), picturefile)
map = os.path.join(os.path.dirname(__file__), mapfile)
