#!/usr/bin/env python

"""
Algorithm to locate the photographer.
This algorithm relies on multiple execution of another optimizer.
"""

from tools import barycenter, selections_of_five_summits
from optimizer1 import find_photograper as find_photograper_basic
from optimizer1 import project_on_lens

def find_photograper(dimensions, summits, projections, init=None):
    """
    Position the photographer where the picture was taken for
    all possible combinations of 5 summits.
    """
    # Takes 'middle' of area where the photographer can be as start of search
    combinations = selections_of_five_summits(summits)
    counter = 1
    positions = []
    for comb in combinations:
        print("Combinations of summits: %i/%i" % (counter, len(combinations)))
        counter += 1
        # Find the best position for the photographer
        photographer, error, path = find_photograper_basic(
            dimensions=dimensions,
            summits=[summits[comb[i]] for i in range(0, 5)],
            projections=[projections[comb[i]] for i in range(0, 5)],
            init=init
        )
        positions.append({
            "photographer": photographer,
            "error": error,
            "path": path,
            "summits_used": comb
        })
    # todo:
    # - return barycentre of all solution
    # - option: weighted with their inverse error
    return positions


def run(map, summits, projections):
    """
    Run the optimization and display findings on map.
    """
    positions = find_photograper(map.dimensions, summits, project_on_lens)
    sortedPositions = sorted(positions, key=lambda p: p["error"])
    for (p, t) in zip(sortedPositions, "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        map.draw_point(
            point=p["photographer"],
            name=t + "(%f)" % (1.0 / p["error"])
        )
        map.draw_path(p["path"])
    bary = barycenter(
        [i["photographer"] for i in sortedPositions],
        [1.0 / i["error"] for i in sortedPositions],
    )
    map.draw_point(bary, name="Bary")