#!/usr/bin/env python

"""
Algorithm to locate the photographer.
"""

from collections import namedtuple
from math import fabs, sqrt

import utm
from numpy import array
from scipy.optimize import minimize

from tools import barycenter, distance, extrems, intersection_lines, photographer_area
from converter import Converter


def compute_projection_on_picture(photographer, summits, alpha, rho=1):
    """
    Compute the projection of the summits on the picture.
    Input:
     - photographer: a given position of the photographer
     - summits: the positions (s1 to sN) of the summits on the map
     - alpha: a float, between 0 and 1, that controls the angle of the picure
       as follow:
         * ps1_ = alpha * ps1
         * psN_ = (1 - alpha) * psN
       with s1_ and sN_ the projections of s1 and sN on the picture .
     - rho: a float that controls the distance between the picture and
       the photographer
    Output:
     - s1_ to sN_, the projections of all summits on the picture.
    """
    if photographer is None:
        raise RuntimeError("photographer position cannot be None.")
    if not (0 <= alpha <= 1):
        raise RuntimeError("Alpha must be in range 0 <= alpha <= 1.")
    p = photographer
    s1, s2toM, sN = summits[0], summits[1:-1], summits[-1]
    # Compute s1_ and sN_, then all intermediate summits
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
            (1 - rho * alpha) * p[0] + rho * alpha * s1[0],
            (1 - rho * alpha) * p[1] + rho * alpha * s1[1]
        )
        sN_ = (
            (1 - rho * (1 - alpha)) * p[0] + rho * (1 - alpha) * sN[0],
            (1 - rho * (1 - alpha)) * p[1] + rho * (1 - alpha) * sN[1]
        )
        s2toM_ = [intersection_lines(s1_, sN_, p, x) for x in s2toM]
    # Return list of projection points
    return [s1_] + s2toM_ + [sN_]


PicturePosition = namedtuple('PicturePosition', ["projections", "alpha", "rho", "error"])


def optimize_picture(photographer, summits, projections):
    """
    Optimize the position of the picture for a given position of the photographer.
    Input:
     - the position of the photographer (p)
     - the positions of at least three summits on the map (as viewed from left to right)
     - the projections of the summits on the picture (from left to right)
    Output:
     - error: the error on the alignment of the summits after optimization
     - alpha/rho: two parameters that define the position of the picture
     - projections: the projections of the summits on the picture
     """
    if photographer is None:
        raise RuntimeError("photographer cannot be None")

    # Compute successive normalized distance between real projections
    deltasref = [
        (p - projections[0]) / (projections[-1] - projections[0])
        for p in projections
    ]

    def errorfun(alpha):
        "Error function to minimize."
        s_ = compute_projection_on_picture(photographer, summits, alpha[0])
        # If a summit doesn't have any projection (picture // with direction
        # of the summit), return max error.
        if None in s_:
            return 999999
        # Compute successive normalized distance between projections
        left, right = extrems(photographer, s_)
        deltascur = [
            distance(left, p) / distance(left, right)
            for p in s_
        ]
        # Compute the error: normalized sum of square of diff of the normalized distance
        error = sum(
            (cur - ref)**2 for cur, ref in zip(deltascur, deltasref)
        )
        error /= len(deltasref)
        return error

    # find the values of alpha that minimise the distances between expected
    # and actual projections of the summits on the lens.
    res = minimize(
        errorfun,
        (0.5,),
        method='SLSQP',
        bounds=((0, 1),)
    )
    alpha = res.x[0]
    error = res.fun
    # move picture away/closer to have respect scale
    s_ = compute_projection_on_picture(photographer, summits, alpha)
    if distance(s_[1], s_[0]) == 0:
        rho = None
        s__ = [photographer]*5
    else:
        rho = abs(projections[1] - projections[0]) / distance(s_[1], s_[0])
        s__ = compute_projection_on_picture(photographer, summits, alpha, rho)
    return PicturePosition(projections=s__ , alpha=alpha, rho=rho, error=error)


PhotographerPosition = namedtuple('PhotographerPosition', ["photographer", "error", "path", "area", "init"])


def find_photographer(summits, projections, init=None):
    """
    Retrieve the position of the photographer.
    Input:
    - summits: list of (x, y) coordinates of the summits on the map
    - projections: distance of the projections of the summits from the left of the picture
    - init: an optional initial position for the search 
    Output:
    - The 'photographer' position
    - The 'error' at the photographer position
    - The optimisation 'path'
    - The 'area' in which the photographer can be located
    - The 'init' point of the search
    """
    if sorted(projections) != projections:
        raise RuntimeError(
            "The projections and the summit must be in order from left to right."
        )
    # If no initial position, take the barycenter of the possible of the are
    # where the photographer can be.
    area = photographer_area(summits)
    if init is None:
        init = barycenter(area)

    path = []
    def errorfun(position):
        "Error function to minimize."
        error = optimize_picture(tuple(position), summits, projections).error
        path.append(position)
        return error

    # Minimize error function
    res = minimize(
        errorfun,
        init,
        method="Nelder-Mead"
    )

    return PhotographerPosition(photographer=res.x,
                                error=res.fun, 
                                path=path, 
                                area=area, 
                                init=init)


def find_photographer_wsg84(latlngs, projections, init=None):
    """
    Wrapper of find_photographer that uses latlngs in input & output
    instead of x,y coordinates.
    """
    # Convert input from latlng to xy (i.e. WSG84 to UTM).
    conv = Converter(*latlngs[0])
    utmsummits = [conv.from_latlng(*p) for p in latlngs]
    utminit = None
    if init is not None:
        utminit = conv.from_latlng(*init)

    # Run the optimizer to find the photographer.
    utmphotographer, error, utmpath, utmarea, utminit = find_photographer(
        utmsummits, projections, utminit
    ) 

    # Convert output from xy to latlng (i.e. UTM to WSG84).
    photographer = conv.to_latlng(*utmphotographer, strict=False)
    path = [conv.to_latlng(*p, strict=False) for p in utmpath]
    area = [conv.to_latlng(*p) for p in utmarea]
    init = conv.to_latlng(*utminit)

    return PhotographerPosition(photographer=photographer,
                                error=error, 
                                path=path, 
                                area=area, 
                                init=init)
