#!/usr/bin/env python

"""
Algorithm to locate the photographer.
This algorithm relies on multiple execution of another optimizer.
"""

from collections import namedtuple

from optimizer import compute_projection_on_picture
from optimizer import find_photographer as find_photographer_basic
from tools import barycenter, selections_of_five_summits


MetaPhotographerPosition = namedtuple('MetaPhotographer', ["photographer", "error", "details"])


def find_photographer_for_5(summits, projections, init=None):
    """
    Position the photographer where the picture was taken for
    all possible combinations of 5 summits.
    """
    # Takes 'middle' of area where the photographer can be as start of search
    combinations = selections_of_five_summits(summits)
    counter = 0
    details = []
    print("Combinations of summits: ", end="")    
    for comb in combinations:
        counter += 1
        print("%i/%i" % (counter, len(combinations)), end=" ")
        # Find the best position for the photographer
        photographer, error, path, area, init = find_photographer_basic(
            summits=[summits[i] for i in comb],
            projections=[projections[i] for i in comb],
            init=init
        )
        details.append({
            "photographer": photographer,
            "error": error,
            "path": path,
            "summits": summits,
            "projections": projections
        })
    print()
    # Compute barycenter weighted on inverse error
    bary = barycenter(
        points=[i["photographer"] for i in details],
        weights=[1 / i["error"] for i in details]
    )
    error = sum(i["error"] for i in details)
    return MetaPhotographerPosition(photographer=bary, error=error, details=details)


def run(map, summits, projections):
    """
    Run the optimization and display findings on map.
    """
    res = find_photographer_for_5(summits, projections)
    positions = res.details
    sortedPositions = sorted(positions, key=lambda p: p["error"])
    for i,  p in enumerate(sortedPositions):
        map.draw_point(
            point=p["photographer"],
            #name="{}: {}".format(i, 1.0 / p["error"]),
            color="green"
        )
    bary = res.photographer
    map.draw_point(bary, name="Q", color="red")
    return res
