#!/usr/bin/env python

import os.path
from math import sqrt

# Description of the picture
description = """Fake data for testing."""

# Dimension of the map
map = (500, 500)

# Expected position of the photographer (optionnal)
photographer = (100, 100)

# File name of the picture
picturefile = "none"

# Summits (as seen from left to right)
points = [
    ("A", (100, 400), -75*sqrt(2)),
    ("B", (200, 300), -25*sqrt(2)),
    ("C", (400, 400), 0),
    ("D", (400, 250), 25*sqrt(2)),
    ("E", (300, 100), 75*sqrt(2))
    ]

names = [i[0] for i in points]
summits = [i[1] for i in points]
projections = [i[2] for i in points]
picture = os.path.join(os.path.dirname(__file__), picturefile)

