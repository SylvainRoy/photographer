#!/usr/bin/env python

"""
Algorithm to locate the photographer.
"""

from collections import namedtuple
from math import sqrt, fabs
from scipy.optimize import minimize

from tools import intersection_lines, distance, photographer_area, barycenter


def compute_projection_on_picture(photographer, summits, alpha):
    """
    Compute the projection of the summits on the picture.
     - photographer: a given position of the photographer (called 'p' in below)
     - summits: the position (s1 to sN) of the summits on the map
     - alpha: a float, between 0 and 1 that completes the definition of
       the position of the picture in the following way:
         * ps1_ = alpha * ps1
         * psN_ = (1 - alpha) * psN
       with s1_ and sN_ the projections of s1 and sN on the picture .
    Return:
     - s1_ to sN_, the projections of all summits on the lens.
    """
    if photographer_area is None:
        raise RuntimeError("photograper position cannot be None")
    p = photographer
    s1, s2toM, sN = summits[0], summits[1:-1], summits[-1]
    # First compute s1_ and sN_ based on alpha, then
    # all the intermediate summit
    if alpha == 0:
        s1_ = p
        sN_ = sN
        s2toM_ = [p for x in s2toM]
    elif alpha == 1:
        s1_ = s1
        sN_ = p
        s2toM_ = [p for x in s2toM]
    else:
        s1_ = (
            (1 - alpha) * p[0] + alpha * s1[0],
            (1 - alpha) * p[1] + alpha * s1[1],
        )
        sN_ = (
            alpha * p[0] + (1 - alpha) * sN[0],
            alpha * p[1] + (1 - alpha) * sN[1],
        )
        s2toM_ = [intersection_lines(s1_, sN_, p, x) for x in s2toM]
    # Build list of projection points
    s_ = [s1_] + s2toM_ + [sN_]
    return s_


LensResult = namedtuple('LensResult', ["lens", "picture", "projections", "error"])

def optimize_picture(photographer, summits, projections):
    """
    Optimize the position of the picture for a given position of the photographer.
    Input:
     - the position of the photographer (p)
     - the positions of at least three summits on the map
     - the projections of the summits on the picture
    Output:
     - lens: the position of the middle of the lens (the point on the picture that
        is ortho with the photographer)
     - picture: the position of the middle of the picture
     - projections: the corresponding projections on the picture
     - error: the error
     """
    if photographer is None:
        raise RuntimeError("photographer cannot be None")
    p = photographer
    p1, pN = projections[0], projections[-1]
 
    # Compute successive normalized distance between real projections
    deltasref = [abs((i[1] - i[0]) / (projections[-1] - projections[0]))
                 for i in zip(projections[:-1], projections[1:])]

    def errorfun(alpha):
        s_ = compute_projection_on_picture(p, summits, alpha)
        # Compute successive normalized distance between current projections
        deltascur = [distance(i[1], i[0]) / distance(s_[-1], s_[0])
                     for i in zip(s_[:-1], s_[1:])]
        # Compute the error: normalized sum of square of diff of the distance
        error = sum(
            (cur - ref)**2 for cur, ref in zip(deltascur, deltasref)
        )
        error /= len(deltasref)
        return error

    # find the values of alpha that minimise the distances between expected
    # and actual projections of the summits on the lens.
    res = minimize(
        errorfun,
        (0.5),
        method="Nelder-Mead", # "L-BFGS-B",
        #bounds=((0, 1))
    )
    alpha = res.x
    # (re)compute the position of the summits' projection on the lens
    s_ = compute_projection_on_picture(p, summits, alpha)
    # Compute position of center of picture
    f = p1 / (pN - p1)
    m = (s_[0][0] - f * (s_[-1][0] - s_[0][0]), s_[0][1] - f * (s_[-1][1] - s_[0][1]))
    # Compute position of lens ("in front of" photographer)
    den = (s_[-1][0] - s_[0][0]) ** 2 + (s_[-1][1] - s_[0][1]) ** 2
    r = (
        (p[0] - s_[0][0]) * (s_[-1][0] - s_[0][0])
        + (p[1] - s_[0][1]) * (s_[-1][1] - s_[0][1])
    ) / den
    o = (s_[0][0] + r * (s_[-1][0] - s_[0][0]), s_[0][1] + r * (s_[-1][1] - s_[0][1]))
    return LensResult(lens=o, picture=m, projections=s_, error=res.fun)


def find_photograper(dimensions, summits, projections, init=None):
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
    def errorfun(position):
        error = optimize_picture(position, summits, projections).error
        path.append(position)
        return error

    # Minimize error function
    res = minimize(
        errorfun,
        init,
        method="Nelder-Mead",
        #bounds=((0, dimensions[0]), (0, dimensions[1])),
    )
    photographer = res.x
    error = res.fun
    return photographer, error, path


def run(map, summits, projections):
    """
    Run the optimization and display findings on map.
    """
    photograper, error, path = find_photograper(
        dimensions=map.dimensions,
        summits=summits,
        projections=projections
    )
    # draw on the map
    map.draw_path(path, color="blue")
    map.draw_point(photograper, name="%.8f" % error, color="red")
