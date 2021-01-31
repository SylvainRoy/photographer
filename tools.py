#!/usr/bin/env python

"""
Toolings!
"""

from PIL import Image as PILImage
from PIL import ImageDraw

from math import sqrt


def intersection_lines(a1, a2, b1, b2):
    """
    Return the intersection of two lines defined by points, None if the lines are parallel.
    """
    den = (b2[1] - b1[1]) * (a2[0] - a1[0]) - (b2[0] - b1[0]) * (a2[1] - a1[1])
    if den == 0:
        return None
    num = (b2[0] - b1[0]) * (a1[1] - b1[1]) - (b2[1] - b1[1]) * (a1[0] - b1[0])
    ua = num / den
    return (a1[0] + ua * (a2[0] - a1[0]), a1[1] + ua * (a2[1] - a1[1]))


def distance(a, b):
    """Return the distance between two points."""
    return sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


def dot(u, v):
    """Return the dot product of two vectors."""
    return u[0] * v[0] + u[1] * v[1]


def barycenter(points, weights=None):
    """Compute the barycenter of a list of points (that have the same weight)."""
    if weights is None:
        weights = [1] * len(points)
    sumWeights = sum(weights)
    return (
        sum([p[0] * w for (p, w) in zip(points, weights)]) / sumWeights,
        sum([p[1] * w for (p, w) in zip(points, weights)]) / sumWeights,
    )


def is_valid_location(point, summits):
    """
    Return true if the position 'point' is a valid position for the
    photographer to be. That is, the summits are seen by the photographer 
    in the right order from left to right.
    """
    (x, y) = point
    l = len(summits)
    for i in range(0, l):
        for j in range(i + 1, l):
            (xi, yi) = summits[i]
            (xj, yj) = summits[j]
            cross = (xj - x) * (yi - y) - (yj - y) * (xi - x)
            if cross < 0:
                return False
    return True


def photographer_area(summits, mapDimension):
    """
    Return the envelop (a list of point) of the area where the photograph is located.
    summits: list of summits (x, y) as seen from left to right on the picture
    mapDimension: dimension (x, y) of the map that contains the summits and the photographer
    """
    corners = [
        (0, 0),
        (0, mapDimension[1]),
        (mapDimension[0], mapDimension[1]),
        (mapDimension[0], 0),
    ]
    # Build list of vectors (summits to summits + borders of the map)
    # Possible points are on the 'right' of these vectors.
    summit2summit = []
    for i in range(0, len(summits)):
        for j in range(i + 1, len(summits)):
            summit2summit.append((summits[i], summits[j]))
    borders = [
        (corners[0], corners[1]),
        (corners[1], corners[2]),
        (corners[2], corners[3]),
        (corners[3], corners[0]),
    ]
    vectors = summit2summit + borders
    # Build list of all intersection points between
    # - lines built on two summits
    # - border of the map 
    intersections = set()
    for i in range(0, len(vectors)):
        for j in range(i, len(vectors)):
            inter = intersection_lines(
                vectors[i][0], vectors[i][1], vectors[j][0], vectors[j][1]
            )
            if inter is not None:
                intersections.add(inter)
    # Filter out all the points that are not acceptable
    # (i.e. cross product > 0)
    envelop = []
    for p in intersections:
        valid = True
        for v in vectors:
            vx = v[1][0] - v[0][0]
            vy = v[1][1] - v[0][1]
            px = p[0] - v[0][0]
            py = p[1] - v[0][1]
            cross = vx * py - vy * px
            if cross > 1e-10:  # the wonderful world of numerical computation...
                valid = False
                break
        if valid:
            envelop.append(p)
    if len(envelop) == 0:
        raise RuntimeError(
            "There seems to be no point on the map to take such a picture!"
        )
    # Compute barycenter of envelop
    bary = barycenter(envelop)
    # Sort points (trigo order) of the (convex) envelop
    pabove = [p for p in envelop if p[1] - bary[1] >= 0]
    pbelow = [p for p in envelop if p[1] - bary[1] < 0]
    pabovesorted = sorted(
        pabove,
        key=lambda p: -(p[0] - bary[0])
        / sqrt((p[0] - bary[0]) ** 2 + (p[1] - bary[1]) ** 2),
    )
    pbelowsorted = sorted(
        pbelow,
        key=lambda p: (p[0] - bary[0])
        / sqrt((p[0] - bary[0]) ** 2 + (p[1] - bary[1]) ** 2),
    )
    return pabovesorted + pbelowsorted


def project_on_lens(photographer, lens, summit):
    """
    Return the projection of a summit on the lens.
    The center of the lens is in 'lens'. The lens is 'orthogonal' with the photographer.
    """
    aax = lens[0] - photographer[0]
    aay = lens[1] - photographer[1]
    aac = lens[0] * (photographer[0] - lens[0]) + lens[1] * (photographer[1] - lens[1])
    bbx = summit[1] - photographer[1]
    bby = photographer[0] - summit[0]
    bbc = photographer[0] * (photographer[1] - summit[1]) + photographer[1] * (
        summit[0] - photographer[0]
    )
    denominator = aax * (bby * aac - aay * bbc) + aay * (aax * bbc - bbx * aac)
    mx = -aac * (bby * aac - aay * bbc) / denominator
    my = -aac * (aax * bbc - bbx * aac) / denominator
    return (mx, my)


def simulate_photo(photographer, lens, summits):
    """
    Return an image simulating the photo
    """
    # Get key values
    photox, photoy, middlex = 501, 200, 251
    (xp, yp) = photographer
    (xo, yo) = lens
    h = sqrt((xo - xp) ** 2 + (yo - yp) ** 2)
    # Compute summits' positions relative to center of photo
    deltas = []
    for summit in summits:
        (xm, ym) = project_on_lens(photographer, lens, summit)
        delta = ((yo - yp) * (xm - xo) - (xo - xp) * (ym - yo)) / h
        deltas.append(delta)
    # compute coef to get everything to fit in picture
    alpha = (photox - 100) / (max(deltas) - min(deltas))
    # Build photo
    photo = PILImage.new("RGBA", (photox, photoy), (255, 255, 255, 0))
    draw = ImageDraw.Draw(photo)
    for (delta, name) in zip(deltas, "ABCDEFGHIKLMNOPQRSTUVWXYZ"):
        draw.line(
            (
                middlex + alpha * delta,
                photoy / 2,
                middlex + alpha * delta + photox / 10,
                photoy,
            ),
            fill=0,
        )
        draw.line(
            (
                middlex + alpha * delta,
                photoy / 2,
                middlex + alpha * delta - photox / 10,
                photoy,
            ),
            fill=0,
        )
        draw.text((middlex + alpha * delta + 5, photoy / 2 - 10), name, fill=0)
    draw.line((middlex, 0, middlex, photoy), fill=0)
    draw.text((middlex + 10, 10), "center", fill=0)
    return photo


def selections_of_five_summits(summits):
    """
    Return all combination of indexes of 5 summits.
    """
    out = []
    ll = len(summits)
    for i in range(0, ll - 4):
        for j in range(i + 1, ll - 3):
            for k in range(j + 1, ll - 2):
                for l in range(k + 1, ll - 1):
                    for m in range(l + 1, ll):
                        out.append([i, j, k, l, m])
    return out


def change_coordinate_funs(utm_coord, local_coord):
    """
    Return two functions to change the coordinate system of a point.
    Input: a list of at list two points in the two coordinate system.
    """
    alphax = (local_coord[-1][0] - local_coord[0][0]) / (utm_coord[-1][0] - utm_coord[0][0])
    alphay = (local_coord[-1][1] - local_coord[0][1]) / (utm_coord[-1][1] - utm_coord[0][1])
    Xo = utm_coord[0][0] - local_coord[0][0] / alphax
    Yo = utm_coord[0][1] - local_coord[0][1] / alphay
    def utmtolocal(p):
        return ((p[0] - Xo) * alphax, (p[1] - Yo) * alphay) 
    def localtoutm(p):
        return (p[0] / alphax + Xo, p[1] / alphay + Yo)
    return utmtolocal, localtoutm
