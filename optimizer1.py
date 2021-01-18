#!/usr/bin/env python

"""
Algorithm to locate the photographer.
"""

from collections import namedtuple
from math import sqrt, fabs
from scipy.optimize import minimize

from tools import intersection_lines, distance, photographer_area, barycenter


def position_lens(p, summits, alpha):
    """
    Position the lens for:
     - p: a given position of the photographer
     - summits: the position (s1 to sM) of the summits on the map
     - alphas: a couple of parameters, between 0 and 1, that completes
       the definition of the position of the lens in the following way:
         * ps1_ = alpha0 * ps1
         * psM_ = alpha1 * psM
       with s1_ and sM_ the projections of s1 and sM on the picture 
    Return:
     - s1_ to sM_, the projections of all summits on the lens
    """
    if p is None:
        raise RuntimeError("photograper position cannot be None")
    s1, s2toN, sM = summits[0], summits[1:-1], summits[-1]
    # First compute s1_ and sM_ based on alphas, then
    # all the intermediate summit
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
    if photographer is None:
        raise RuntimeError("photographer cannot be None")
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
