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


def det(u, v):
    """Return the determinant of two vectors."""
    return u[0] * v[1] - u[1] * v[0] 


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


def filter_points_on_the_right(points, vectors):
    """
    filter the points that are on the right of all the vectors.
    """
    # In a perfect world, the threshold should simply be 0.
    # Numerical computation is not a perfect world.
    threshold = (sum(p[0] for p in points) + sum(p[1] for p in points)) / (2e10 * len(points))
    envelop = []
    for p in points:
        valid = True
        for v in vectors:
            vx, vy = v[1][0] - v[0][0], v[1][1] - v[0][1]
            px, py = p[0] - v[0][0], p[1] - v[0][1]
            cross = vx * py - vy * px
            if cross >= threshold:
                valid = False
                break
        if valid:
            envelop.append(p)
    return envelop


def extrems(origin, points):
    """
    Assuming 'points' are on a line, return the leftmost and rightmost
    points from the perspective of 'origin'.
    """
    # Find the two most extrem points
    dmax = 0
    for p in points:
        for q in points:
            d = distance(p, q)
            if d > dmax:
                dmax = d
                pp, qq = p, q
    op = (pp[0] - origin[0], pp[1] - origin[1])
    oq = (qq[0] - origin[0], qq[1] - origin[1])
    # Order the points
    if det(op, oq) <= 0:
        return pp, qq
    else:
        return qq, pp 


def find_all_intersections(vectors):
    """
    return all vectors intersections.
    """
    intersections = set()
    for i in range(0, len(vectors)):
        for j in range(i, len(vectors)):
            inter = intersection_lines(vectors[i][0], vectors[i][1], vectors[j][0], vectors[j][1])
            if inter is not None:
                intersections.add(inter)
    return list(intersections)


def photographer_area(summits, xmin=None, xmax=None, ymin=None, ymax=None):
    """
    Return the envelop (a list of point) of the area where the photograph is located.
    summits: list of summits coordinates (x, y) in the order they appears on the picture (left to right).
    xmin, ... ymax: the enclosing area of the map.
    """

    # Compute all summit vectors (photographer is on the right of those vectors)
    summit_vectors = []
    for i in range(0, len(summits)):
        for j in range(i + 1, len(summits)):
            summit_vectors.append((summits[i], summits[j]))

    # An enclosing zone is needed to ensure a "closed" area
    if xmin is None:
        # Find all the corners of the area
        intersections = find_all_intersections(summit_vectors)
        envelop = filter_points_on_the_right(intersections + summits, summit_vectors)
        if len(envelop) == 0:
            raise RuntimeError(
                "Such a picture cannot be taken. "
                "Check the location and order of the points on the map and picture."
            )
        # Let's define a square centered on the barycentre and big enough to contain it all.
        bary_summit = barycenter(summits)
        mdist = 2 * max([distance(bary_summit, p) for p in envelop + summits])
        zone = [(bary_summit[0] - mdist, bary_summit[1] - mdist),
                (bary_summit[0] - mdist, bary_summit[1] + mdist),
                (bary_summit[0] + mdist, bary_summit[1] + mdist),
                (bary_summit[0] + mdist, bary_summit[1] - mdist)]
    else:
        zone = [(xmin, ymin), (xmin, ymax), (xmax, ymax), (xmax, ymin)]
    
    # Find all the corners of the area
    zone_vectors = list(zip(zone, zone[1:] + zone[:1]))
    close_vectors = summit_vectors + zone_vectors
    close_intersections = find_all_intersections(close_vectors)
    close_envelop = filter_points_on_the_right(close_intersections, close_vectors)
    if len(close_envelop) == 0:
        raise RuntimeError(
            "Such a picture cannot be taken. "
            "Check the location and order of the points on the map and picture."
        )

    # Sort points (trigo order) of the (convex) envelop of the area
    bary_envelop = barycenter(close_envelop)
    pabovesorted = sorted(
        [p for p in close_envelop if p[1] - bary_envelop[1] >= 0],
        key=lambda p: -(p[0] - bary_envelop[0]) / sqrt((p[0] - bary_envelop[0]) ** 2 + (p[1] - bary_envelop[1]) ** 2),
    )
    pbelowsorted = sorted(
        [p for p in close_envelop if p[1] - bary_envelop[1] < 0],
        key=lambda p: (p[0] - bary_envelop[0]) / sqrt((p[0] - bary_envelop[0]) ** 2 + (p[1] - bary_envelop[1]) ** 2),
    )
    area = pabovesorted + pbelowsorted
    return area


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
    Input: a list of at least two points in the two coordinate system (only the first and last point are used).
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
