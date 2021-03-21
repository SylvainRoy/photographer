#!/usr/bin/env python

"""
Algorithm to locate the photographer.
"""

from collections import namedtuple
from math import fabs, sqrt

import utm
from scipy.optimize import minimize

from tools import barycenter, distance, intersection_lines, photographer_area


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
        raise RuntimeError("photograper position cannot be None")
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
            (1 - rho * alpha) * p[1] + rho * alpha * s1[1],
        )
        sN_ = (
            (1 - rho * (1 - alpha)) * p[0] + rho * (1 - alpha) * sN[0],
            (1 - rho * (1 - alpha)) * p[1] + rho * (1 - alpha) * sN[1],
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
     - the positions of at least three summits on the map
     - the projections of the summits on the picture
    Output:
     - error: the error on the alignment of the summits after optimization
     - alpha/rho: two parameters that define the position of the picture
     - projections: the projections of the summits on the picture
     """
    if photographer is None:
        raise RuntimeError("photographer cannot be None")
    # Compute successive normalized distance between real projections
    deltasref = [abs((i[1] - i[0]) / (projections[-1] - projections[0]))
                 for i in zip(projections[:-1], projections[1:])]

    def errorfun(alpha):
        "Error function to minimize."
        s_ = compute_projection_on_picture(photographer, summits, alpha)
        # If a summit doesn't have any projection (picture // with direction
        # of the summit), return max error.
        if None in s_:
            return 999999
        # Compute successive normalized distance between projections
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
        (0.5,),
        method="Nelder-Mead", #'SLSQP', #"L-BFGS-B",
        #bounds=((0, 1),)
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


PhotographerPosition = namedtuple('PhotographerPosition', ["photographer", "error", "path"])


def find_photograper(summits, projections, init=None):
    """
    Retrieve the position of the photographer.
    Input:
    - summits: list of (x, y) coordinates of the summits on the map
    - projections: distance of the projections of the summits from the left of the picture
    - init: an optional initial position for the search 
    Output:
    - The photographer position
    - The error at the photographer position
    - The optimisation path
    """
    # If no initial position, take the barycenter of the possible of the are
    # where the photographer can be.
    if init is None:
        area = photographer_area(summits)
        init = barycenter(area)

    path = []
    def errorfun(position):
        "Error function to minimize."
        error = optimize_picture(position, summits, projections).error
        path.append(position)
        return error

    # Minimize error function
    res = minimize(
        errorfun,
        init,
        method="Nelder-Mead"
    )
    return PhotographerPosition(photographer=res.x, error=res.fun, path=path)


def find_photograper_wsg84(latlngs, projections, init=None):
    """
    Retrieve the position of the photographer.
    Input:
    - summits: list of (lat, lng) coordinates (WSG84) of the summits on the map
    - projections: distance of the projections of the summits from the left of the picture
    - init: an optional initial position for the search 
    Output:
    - The photographer position
    - The error at the photographer position
    - The optimisation path
    """
    # Convert data from WSG84 to UTM.
    utmdata = [utm.from_latlon(p[0], p[1]) for p in latlngs]
    utmsummits = [(p[0], p[1]) for p in utmdata]
    if init is not None:
        initdata = utm.from_latlon(init[0], init[1])
        utmdata.append(initdata)
        init = (initdata[0], initdata[1])
    # Save UTM zone/letter (and check if it's all in the same zone).
    zone_numbers = set([d[2] for d in utmdata])
    zone_letters = set([d[3] for d in utmdata])
    if len(zone_numbers) != 1 or len(zone_letters) != 1:
        raise("The summits/init are spread over several UTM zones!")
    zone_number = zone_numbers.pop()
    zone_letter = zone_letters.pop()
    # Run the optimizer to find the photograper
    utmphotographer, error, utmpath = find_photograper(utmsummits, projections, init) 
    # Convert back to WSG84
    photographer = utm.to_latlon(utmphotographer[0], utmphotographer[1], zone_number, zone_letter)
    path = [
        utm.to_latlon(p[0], p[1], zone_number, zone_letter)
        for p in utmpath
    ]
    return PhotographerPosition(photographer=photographer, error=error, path=path)


def run(map, summits, projections):
    """
    Run the optimization and display findings on map.
    """
    res = find_photograper(
        summits=summits,
        projections=projections
    )
    # draw on the map
    map.draw_path(res.path, color="blue")
    map.draw_point(res.photographer, name="%.8f" % res.error, color="red")
    return res
