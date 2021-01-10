#!/usr/bin/env python

"""
Retrieve the position of a photographer on a map based on the coordinates of points from the picture.
"""


import sys
import os
import numpy as np
import datetime

from math import sqrt, fabs
from collections import namedtuple
from scipy.optimize import minimize

from tools import *
from map import Map


def position_lens(p, summits, alpha):
    """
    Position the lens based on alpha parameter:
      s1_ and sM_ are the projections of s1 and sM on the lens based on alphas.
    Then, compute s2_, ..., sN the projections of s2, ..., sN on the
      (now positioned) lens.
    Return the projections of all summits on the lens
    """
    s1, s2toN, sM = summits[0], summits[1:-1], summits[-1]
    if alpha[0] == 0:
        s1_ = p
        sM_ = (
            (1 - alpha[1]) * p[0] + alpha[1] * sM[0],
            (1 - alpha[1]) * p[1] + alpha[1] * sM[1],
        )
        s2toN_ = [p for x in s2toN]
    elif alpha[1] == 0:
        s1_ = (
            (1 - alpha[0]) * p[0] + alpha[0] * s1[0],
            (1 - alpha[0]) * p[1] + alpha[0] * s1[1],
        )
        sM_ = p
        s2toN_ = [p for x in s2toN]
    else:
        s1_ = (
            (1 - alpha[0]) * p[0] + alpha[0] * s1[0],
            (1 - alpha[0]) * p[1] + alpha[0] * s1[1],
        )
        sM_ = (
            (1 - alpha[1]) * p[0] + alpha[1] * sM[0],
            (1 - alpha[1]) * p[1] + alpha[1] * sM[1],
        )
        s2toN_ = [intersection_lines(s1_, sM_, p, x) for x in s2toN]
    # Build list of projection points
    s_ = [s1_] + s2toN_ + [sM_]
    return s_


LensResult = namedtuple('LensResult', ["lens", "picture", "projections", "error"])


def optimize_lens(photographer, summits, projections):
    """
    Optimize the position of the lens for a given position of the photographer.
    Input:
     - the position of the photographer (p)
     - the positions of at least three summits on the map
     - the projections of the summits on the picture
    Output:
     - lens: the position of the middle of the lens (the point on the lens that
        is ortho with photographer)
     - picture: the position of the middle of the picture
     - projections: the corresponding projections on the picture
     - error: the error
     """
    p = photographer
    p1, pM = projections[0], projections[-1]
    deltas = []
    for i in range(1, len(projections)):
        deltas.append(fabs(projections[i] - projections[i - 1]))

    def error_to_minimize(alpha):
        # Positions lens based on alpha
        s_ = position_lens(p, summits, alpha)
        # Compute the distances of the projections of the summits on lens
        distances = []
        for i in range(1, len(s_)):
            distances.append(distance(s_[i - 1], s_[i]))
        # Compute the sum of the errors
        error = 0
        for i in range(0, len(distances)):
            error += (distances[i] - deltas[i]) ** 2
        # print "alpha(%.15f, %.15f) = %.15f" % (alpha[0], alpha[1], error)
        return error

    # find the values of alpha that minimise the distances between expected
    # and actual projections of the summits on the lens.
    res = minimize(
        error_to_minimize,
        [0.5, 0.5],
        method="L-BFGS-B", # "Nelder-Mead",
        bounds=((0, 1), (0, 1))
    )
    alpha = res.x
    # (re)compute the position of the summits' projection on the lens
    s_ = position_lens(p, summits, alpha)
    # Compute position of center of picture
    f = 1.0 * p1 / (pM - p1)
    m = (s_[0][0] - f * (s_[-1][0] - s_[0][0]), s_[0][1] - f * (s_[-1][1] - s_[0][1]))
    # Compute position of lens ("in front of" photographer)
    den = (s_[-1][0] - s_[0][0]) ** 2 + (s_[-1][1] - s_[0][1]) ** 2
    r = (
        (p[0] - s_[0][0]) * (s_[-1][0] - s_[0][0])
        + (p[1] - s_[0][1]) * (s_[-1][1] - s_[0][1])
    ) / den
    o = (s_[0][0] + r * (s_[-1][0] - s_[0][0]), s_[0][1] + r * (s_[-1][1] - s_[0][1]))
    return LensResult(lens=o, picture=m, projections=s_, error=res.fun)


def optimize_photograper(dimensions, summits, projections, init=None):
    """
    Position the photographer where the picture was taken.
    - dimensions: (x, y) dimensions of the map
    - summits: list of summits with their (x, y) coordinates on the map
    - projections: distance of the projections of the summits from the left of the picture
    - init: an optional initial position for the search 
    """
    # If not initial position, take the middle of the possible area
    if init is None:
        envelop = photographer_area(summits, dimensions)
        init = barycenter(envelop)

    # define error function to minimize
    path = []
    def error_to_minimize(position):
        error = optimize_lens(position, summits, projections).error
        path.append(position)
        return error

    # Minimize error function
    res = minimize(
        error_to_minimize,
        init,
        method="Nelder-Mead",
        bounds=((0, dimensions[0]), (0, dimensions[1])),
    )
    photographer = res.x
    error = res.fun
    return photographer, error, path


def run_display_optimize_photograper(map, summits, projections):
    """
    Run the optimization and display findings on map.
    """
    photograper, error, path = optimize_photograper(
        dimensions=map.dimensions,
        summits=data.summits,
        projections=data.projections
    )
    # draw on the map
    map.draw_path(path, color="blue")
    map.draw_point(photograper, name="%.8f" % error, color="red")


def multi_optimize_photograper(dimensions, summits, projections, init=None):
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
        photographer, error, path = optimize_photograper(
            dimensions=dimensions,
            summits=[data.summits[comb[i]] for i in range(0, 5)],
            projections=[data.projections[comb[i]] for i in range(0, 5)],
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


def run_display_multi_optimize_photographer(map, summits, projections):
    """
    Run the optimization and display findings on map.
    """
    positions = multi_optimize_photograper(map.dimensions, summits, project_on_lens)
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


if __name__ == "__main__":

    import data.brevent as data

    map = Map(file=data.map)

    # Colorize the map
    def error(point):
        try:
            return optimize_lens(point, data.summits, data.projections).error
        except:
            return 0
    #map.hot_colorize(error)

    # Draw various things
    for (summit, name) in zip(data.summits, "ABCDEFGHIKLMNOPQRSTUVWXYZ"):
        map.draw_point(summit, name, color="red")
    map.draw_area(photographer_area(data.summits, map.dimensions), color="red")
    map.draw_point(data.photographer, "P", color="red")

    # Find photographer and draw search
    #run_display_multi_optimize_photographer(map, data.summits, data.projections)
    run_display_optimize_photograper(map, data.summits, data.projections)

    # Save and display map
    map.save(
        os.path.join(
            "./out",
            datetime.datetime.now().strftime(
                data.title + "_%y%m%d_%H%M%S.jpg"
            )
        )
    )
    map.show(notebook=False)
