#!/usr/bin/env python

"""
Retrieve the position of a photographer on a map based on the coordinates
of points from the picture.
"""


import sys
import os
import numpy as np
import datetime

from tools import photographer_area
from map import Map
from optimizer import run

# Change this import to change the test data
import data.aiguillemidi2 as data


if __name__ == "__main__":

    # Create a map and draw basic indications
    map = Map(file=data.map)
    for (summit, name) in zip(data.summits, "ABCDEFGHIKLMNOPQRSTUVWXYZ"):
        map.draw_point(summit, name, color="red")
    map.draw_area(
        photographer_area(data.summits, map.dimensions),
        color="red"
    )
    if data.photographer is not None:
        map.draw_point(data.photographer, "P", color="red")

    # Find photographer and draw search
    run(map, data.summits, data.projections)

    # Save and display map
    map.save(
        os.path.join(
            "./out",
            datetime.datetime.now().strftime(
                data.title + "_%y%m%d_%H%M%S.png"
            )
        )
    )
    map.show(notebook=False)
