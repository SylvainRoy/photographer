#!/usr/bin/env python

# todo:
#  - optimize mimimization (e.g. x^3)
#  - better handling of situation where the optimization get out of the acceptable zone
#  - real picture!!!

from PIL import Image, ImageDraw
from math import sqrt, fabs
import numpy as np
from scipy.optimize import minimize
import sys


def display(text, activation=True):
    if activation:
        print text


def intersection_lines((x1, y1),(x2, y2), (x3, y3),(x4, y4)):
    """Return the intersection of two lines defined by points."""
    num = 1.0*(x4-x3)*(y1-y3)-(y4-y3)*(x1-x3)
    den = 1.0*(y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)
    if den == 0:
        raise RuntimeError("Lines do not intersect in intersection_lines")
    ua = num / den
    return (x1+ua*(x2-x1), y1+ua*(y2-y1))


def distance((x1, y1), (x2, y2)):
    """Return the distance between two points."""
    return sqrt((x2-x1)**2+(y2-y1)**2)


def dot((x1, y1), (x2, y2)):
    """Return the dot product of two vectors."""
    return 1.0*x1*x2+y1*y2


def barycenter(points):
    """Compute the barycenter of a list of points (that have the same weight)."""
    return (sum([p[0] for p in points])/len(points),
            sum([p[1] for p in points])/len(points))


def photographer_area(summits, mapDimension):
    """Return the list of point that compose the envelop of the area where the photographer can be.
    summits: list of summits (x, y) as seen from left to right on the picture
    mapDimension: dimension (x, y) of the map that contains the summits and the photographer
    """
    corners = [(0,0), 
               (0,mapDimension[1]),
               (mapDimension[0],mapDimension[1]),
               (mapDimension[0],0)]
    # Build list of vectors (summits to summits + corners of the map)
    # Possible points are on the 'right' of these vectors.
    summit2summit = []
    for i in range(0, len(summits)):
        for j in range(i+1, len(summits)):
            summit2summit.append((summits[i], summits[j]))
    borders = [(corners[0], corners[1]),
               (corners[1], corners[2]),
               (corners[2], corners[3]),
               (corners[3], corners[0])]
    vectors = summit2summit + borders
    # Build list of all intersection points
    intersections = set()
    for i in range(0, len(vectors)):
        for j in range(i, len(vectors)):
            try:
                inter = intersection_lines(vectors[i][0],vectors[i][1],
                                           vectors[j][0],vectors[j][1])
                intersections.add(inter)
            except RuntimeError, e:
                pass
    # Filter out all the points that are not acceptable
    envelop = []
    for p in intersections:
        valid = True
        for v in vectors:
            vx = v[1][0]-v[0][0]
            vy = v[1][1]-v[0][1]
            px = p[0]-v[0][0]
            py = p[1]-v[0][1]
            cross = 1.0*vx*py-vy*px
            if cross > 1e-10: # the wonderful world of numerical computation...
                valid = False
                break
        if valid:
            envelop.append(p)
    # Compute barycenter
    bary = barycenter(envelop)
    # Sort points of the (convex) envelop
    pabove = [p for p in envelop if p[1]-bary[1] >=0 ]
    pbelow = [p for p in envelop if p[1]-bary[1] <0 ]
    pabovesorted = sorted(pabove, 
                          key=lambda p: -1.0*(p[0]-bary[0]) / sqrt((p[0]-bary[0])**2+(p[1]-bary[1])**2))
    pbelowsorted = sorted(pbelow, 
                          key=lambda p: 1.0*(p[0]-bary[0]) / sqrt((p[0]-bary[0])**2+(p[1]-bary[1])**2))
    return pabovesorted + pbelowsorted


def project_on_lens(photographer, lens, summit):
    """Return the projection of a summit on the lens"""
    aax = lens[0] - photographer[0]
    aay = lens[1] - photographer[1]
    aac = lens[0]*(photographer[0]-lens[0]) + lens[1]*(photographer[1]-lens[1])
    bbx = summit[1] - photographer[1]
    bby = photographer[0] - summit[0]
    bbc = photographer[0]*(photographer[1]-summit[1]) + photographer[1]*(summit[0]-photographer[0])
    denominator = aax*(bby*aac-aay*bbc) + aay*(aax*bbc-bbx*aac)
    mx = - aac*(bby*aac-aay*bbc) / denominator
    my = - aac*(aax*bbc-bbx*aac) / denominator
    return (mx,my)


def optimize_lens(p, summits, deltas):
    """Estimate the position of
     - the position of the lens (ortho with photographer)
     - the position of the photo (middle of the picture)
     based on:
     - the position of the photographer (p)
     - the positions of three summits on the map summits = [s1, s2, s3]
     - the positions of the three summits on the picture
       deltas = [delta1, delta2, delta3]
       (the 'delta' are relative to the center of the picture)
     """
    s1, s2, s3 = summits[0], summits[1], summits[2] #todo: remove
    os1, os2, os3 = deltas[0], deltas[1], deltas[2] #todo: remove
    delta12 = fabs(os2-os1)
    delta23 = fabs(os3-os2)
    def error_to_minimize(alpha):
        # Compute s1_ and s3_ on [p, s1] and [p, s2] based on alphas
        s1_ = ((1-alpha[0])*p[0]+alpha[0]*s1[0], (1-alpha[0])*p[1]+alpha[0]*s1[1])
        s3_ = ((1-alpha[1])*p[0]+alpha[1]*s3[0], (1-alpha[1])*p[1]+alpha[1]*s3[1])
        # Compute s2_ as intersection of [p, s2] and [s1_, s3_]
        s2_ = intersection_lines(s1_, s3_, p, s2)
        # Compute distance of projections of summits on lens
        dist12_ = distance(s1_, s2_)  # todo: could be replaced by s2_.x - s1_.x
        dist23_ = distance(s2_, s3_)  # todo: could be replaced by s2_.x - s1_.x
        # Then compare them with expected values
        error1 = fabs(dist12_ - delta12)
        error3 = fabs(dist23_ - delta23)
        return error1**2 + error3**2
    res = minimize(error_to_minimize, [.5,.5])
    #res = minimize(error_to_minimize, [.5,.5], options={'disp':True, 'xtol':1e-8})
    # cons = ({'type': 'ineq', 'fun': lambda x: np.array([x[0]])},
    #         {'type': 'ineq', 'fun': lambda x: np.array([1-x[0]])},
    #         {'type': 'ineq', 'fun': lambda x: np.array([x[1]])},
    #         {'type': 'ineq', 'fun': lambda x: np.array([1-x[1]])})
    # res = minimize(error_to_minimize, [.5,.5], 
    #                constraints=cons, 
    #                method="SLSQP", 
    #                options={'disp':True, 'xtol':1e-8})
    alpha = res.x
    # Compute s1_ and s3_ on [p, s1] and [p, s2] based on alphas returned by optimizer
    s1_ = ((1-alpha[0])*p[0]+alpha[0]*s1[0], (1-alpha[0])*p[1]+alpha[0]*s1[1])
    s3_ = ((1-alpha[1])*p[0]+alpha[1]*s3[0], (1-alpha[1])*p[1]+alpha[1]*s3[1])
    # Compute s2_ as intersection of [p, s2] and [s1_, s3_]
    s2_ = intersection_lines(s1_, s3_, p, s2)
    # Compute position of center of picture
    f = 1.0*os1/(os3-os1)
    m = (s1_[0] - f*(s3_[0]-s1_[0]),
         s1_[1] - f*(s3_[1]-s1_[1]))
    # Compute position of lens ("in front of" photographer)
    den = (s3_[0]-s1_[0])**2 + (s3_[1]-s1_[1])**2
    r = ((p[0]-s1_[0])*(s3_[0]-s1_[0])+(p[1]-s1_[1])*(s3_[1]-s1_[1])) / den
    o = (s1_[0] + r*(s3_[0]-s1_[0]),
         s1_[1] + r*(s3_[1]-s1_[1]))
    return {"lens": o,
            "picture": m,
            "projections": (s1_, s2_, s3_)}


def evaluate_photographer_position(position, summits, deltas, verbose=False):
    display("Evaluating position: " + repr(position), verbose)
    position = (position[0], position[1])
    # evaluate lens position for the given photographer position
    res = optimize_lens(position, 
                        [summits[0], summits[2], summits[4]],
                        [deltas[0], deltas[2], deltas[4]])
    lens = res["lens"]
    # if photographer on a summit, then lens will end up being on this summit
    if lens == position:
        raise RuntimeError("Photographer cannot be on a summit!")
    (s0_, s2_, s4_) = res["projections"]
    display("  Estimation of lens position: " + repr(res["lens"]), verbose)
    display("  Estimation of pic position: " + repr(res["picture"]), verbose)
    display("  Projection of A on lens: " + repr(s0_), verbose)
    display("  Projection of C on lens: " + repr(s2_), verbose)
    display("  Projection of E on lens: " + repr(s4_), verbose)
    # Compute expected projections of summits 1 and 3 on lens
    S0S4 = (s4_[0]-s0_[0], s4_[1]-s0_[1])
    alpha1 = 1.0 * (deltas[1]-deltas[0]) / (deltas[4]-deltas[0])
    s1_ = (s0_[0] + alpha1 * S0S4[0], s0_[1] + alpha1 * S0S4[1])
    alpha3 = 1.0 * (deltas[3]-deltas[0]) / (deltas[4]-deltas[0])
    s3_ = (s0_[0] + alpha3 * S0S4[0], s0_[1] + alpha3 * S0S4[1])
    display("  Expected projection of B on lens: " + repr(s1_), verbose)
    display("  Expected projection of D on lens: " + repr(s3_), verbose)
    # Compute actual projections of summits 1 and 3 on lens
    s1__ = project_on_lens(position, lens, summits[1])
    s3__ = project_on_lens(position, lens, summits[3])
    display("  Actual projection of B on lens: " + repr(s1__), verbose)
    display("  Actual projection of D on lens: " + repr(s3__), verbose)
    # Estimate error:
    d1 = distance(s1_, s1__)
    d3 = distance(s3_, s3__)
    error = d1**2 + d3**2
    display("    Estimated error: %f (%f + %f)" % (error, d1, d3), verbose)
    return error


def optimize_photograper(init, summits, deltas, verbose=False, path=None):
    """Return the position where the photograper has taken the picture."""
    # define error function to minimize
    def error_to_minimize(position):
        if path is not None:
            path.append(position)
        error =  evaluate_photographer_position(position, summits, deltas, verbose)
        #print "error(%f, %f) = %f" % (position[0], position[1], error)
        return error
    # Minimize error function
    res = minimize(error_to_minimize, init)
    return (res.x[0], res.x[1])


def simulate_photo(photographer, lens, summits):
    """Return an image simulating the photo""" 
    # Get key values
    photox, photoy, middlex = 501, 200, 251
    (xp, yp) = photographer
    (xo, yo) = lens
    h = sqrt((xo-xp)**2+(yo-yp)**2)
    # Compute summits' positions relative to center of photo
    deltas = []
    for summit in summits:
        (xm, ym) = project_on_lens(photographer, lens, summit)
        delta = ((yo-yp)*(xm-xo)-(xo-xp)*(ym-yo)) / h
        deltas.append(delta)
    # compute coef to get everything to fit in picture
    alpha = (photox - 100)  / (max(deltas) - min(deltas))
    # Build photo
    photo = Image.new('RGBA', (photox, photoy), (255, 255, 255, 0))
    draw = ImageDraw.Draw(photo)
    for (delta, name) in zip(deltas, "ABCDEFGHI"):
        draw.line((middlex+alpha*delta, photoy/2,
                   middlex+alpha*delta+photox/10, photoy), fill=0)
        draw.line((middlex+alpha*delta, photoy/2,
                   middlex+alpha*delta-photox/10, photoy), fill=0)
        draw.text((middlex+alpha*delta+5, photoy/2-10), name, fill=0)
    draw.line((middlex,0,
               middlex,photoy), fill=0)
    draw.text((middlex+10, 10), "center", fill=0)
    return photo


def percentage_to_color(i):
    """Return a color that goes from white to blue based on a percentage."""
    try:
        i = int(i)
    except:
        i = 0
    return (255-255*i/100, 255-255*i/100, 255, 0)


def selections_of_five_summits(summits):
    out = []
    ll = len(summits)
    for i in range(0, ll-4):
        for j in range(i+1, ll-3):
            for k in range(j+1, ll-2):
                for l in range(k+1, ll-1):
                    for m in range(l+1, ll):
                        out.append([i,j,k,l,m])
    return out


class Map:

    def __init__(self, dimension, summits, projections):
        self.summits = summits
        self.dimension = dimension
        self.projections = projections
        # Build map
        self.map = Image.new('RGBA', self.dimension, (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.map)
        # Draw summits
        for (summit, name) in zip(self.summits, "ABCDEFGHI"):
            self.draw_point(summit, name)
        # Position of photographer and lens
        self.path = None
        self.photographer = (self.dimension[0]/2, self.dimension[1]/2)
        self.lens = None

    def copy(self):
        """Return a deep copy of the map"""
        m = Map(self.dimension, self.summits, self.projections)
        m.map = self.map.copy()
        m.draw = ImageDraw.Draw(m.map)
        m.path = self.path
        m.photographer = self.photographer
        m.lens = self.lens
        return m

    def show(self):
        """Display the map"""
        self.map.show()

    def save(self, filename):
        """Save map in a jpg file"""
        self.map.save(filename)

    def draw_point(self, (x, y), name=None, color=0):
        """Draw a point on the map"""
        t = ""
        if name is not None:
            t = name
        t += "(%.1f,%.1f)" % (x, y)
        y = self.dimension[1] - y
        self.draw.line((x-5,y, x+5,y), fill=color, width=1)
        self.draw.line((x,y-5, x,y+5), fill=color, width=1)
        self.draw.text((x+5, y+5), t, fill=color)
        return self

    def draw_segment(self, (x1, y1), (x2, y2), color=0):
        """Draw a segment on the map"""
        y1 = self.dimension[1] - y1
        y2 = self.dimension[1] - y2
        self.draw.line((x1,y1, x2,y2), fill=color, width=1)
        return self

    def draw_photographer(self, photographer=None, lens=None, color=0, text=None):
        """Draw the photographer and the projections of the summits on the lens.
        Current position of photographer and lens used by default.
        """
        # Draw photographer
        if photographer is None:
            photographer = self.photographer
        if text is None:
            text = "P"
        self.draw_point(photographer, name=text, color=color)
        # Draw projections of summits on lens
        if lens is None:
            if self.lens is not None:
                lens = self.lens
        if lens is not None:
            for (summit, name) in zip(self.summits, "ABCDEFGHI"):
                projection = project_on_lens(photographer, lens, summit)
                self.draw_point(projection, name=name+"'", color=color)
                self.draw_segment(summit, photographer, color=color)
        # Draw path to photographer if any
        if self.path is not None and len(self.path) > 1:
            for i in range(1, len(self.path)):
                self.draw_segment(self.path[i-1], self.path[i], color=(255,0,0,0))
        return self

    def check_location(self, (x, y)):
        """Return true if the position is a valid position for the photographer
        That is, summits are seen the in the right order (left to right)."""
        l = len(self.summits)
        for i in range(0, l):
            for j in range(i+1, l):
                (xi, yi) = self.summits[i]
                (xj, yj) = self.summits[j]
                cross = (xj-x)*(yi-y) - (yj-y)*(xi-x)
                if cross < 0:
                    return False
        return True

    def grey_out_impossible_region(self):
        """Grey out the region where the photographer cannot be
        since he would not see the summit in the right order."""
        for x in range(0, self.dimension[0]):
            for y in range(0, self.dimension[1]):
                if not self.check_location((x, y)):
                    y = self.dimension[1] - y - 1
                    newcolor = tuple([max(i-20, 0)
                                      for i in self.map.getpixel((x, y))])
                    self.draw.point((x, y), fill=newcolor)
        return self

    def hot_colorize(self):
        # Compute errors for each pixel of the map
        errors = np.array([.0]*(self.dimension[0]*self.dimension[1]))
        errors = errors.reshape(self.dimension[0], self.dimension[1])
        mini, maxi = 99999999999, 0
        i, percentage, onepercent = 0, 0, self.dimension[0]*self.dimension[1]/100
        for x in range(0, self.dimension[0]):
            for y in range(0, self.dimension[1]):
                if self.check_location((x, y)):
                    try:
                        error = evaluate_photographer_position(
                            (x,y),
                            self.summits,
                            self.projections)
                    except:
                        error = 0
                    errors[x, y] = error
                    mini = min(mini, error)
                    maxi = max(maxi, error)
                i += 1
                if i > onepercent:
                    percentage += 1
                    i = 0
                    print "%i %%" % percentage
        r = 1.0 * (maxi - mini) / 100.0
        print "error min, max: %f, %f" % (mini, maxi)
        # Colorize map
        for x in range(0, self.dimension[0]):
            for y in range(0, self.dimension[1]):
                c = errors[x, y]
                if c != 0:
                    v = percentage_to_color(r*c)
                    y_ = self.dimension[1] - y - 1
                    self.draw.point((x, y_), fill=v)
        return self

    def draw_photographer_area(self):
        envelop = self.photographer_area()
        for i in range(0, len(envelop)):
            self.draw_segment(envelop[i], envelop[(i+1)%len(envelop)])
        return self

    def photographer_area(self):
        return photographer_area(self.summits, self.dimension)

    def evaluate_photographer_position(self, photographer=None, verbose=False):
        if photographer is None:
            photographer = self.photographer
        return evaluate_photographer_position(photographer,
                                             self.summits,
                                             self.projections,
                                             verbose)

    def optimize_photograper(self, init=None, verbose=False):
        """Position the photographer where the picture was taken."""
        if init is None:
            # Determine area where the photographer can be
            envelop = photographer_area(self.summits, self.dimension)
            # Take the middle of the photographer area
            init = barycenter(envelop)
        # Find the best position for the photographer starting from barycenter
        self.path = []
        self.photographer = optimize_photograper(init, 
                                                 self.summits,
                                                 self.projections,
                                                 verbose,
                                                 self.path)
        self.lens = optimize_lens(self.photographer,
                                  [self.summits[0],
                                   self.summits[2],
                                   self.summits[4]],
                                  [self.projections[0],
                                   self.projections[2],
                                   self.projections[4]])["lens"]
        return self

    
    def multi_optimize_photograper(self, init=None, verbose=False):
        """Position the photographer where the picture was taken for all combination of 5 summits."""
        if init is None:
            # Determine area where the photographer can be
            envelop = photographer_area(self.summits, self.dimension)
            # Take the middle of the photographer area
            init = barycenter(envelop)
        combinations = selections_of_five_summits(self.summits)
        counter = 1
        for comb in combinations:
            print "%i/%i" % (counter, len(combinations))
            counter += 1
            # Find the best position for the photographer
            path = []
            pos = optimize_photograper(
                init,
                [data.summits[comb[i]] for i in range(0, 5)],
                [data.projections[comb[i]] for i in range(0, 5)],
                verbose,
                self.path)
            # Draw photographer
            self.draw_photographer(pos)
            # Draw path to photographer
            for i in range(1, len(self.path)):
                self.draw_segment(self.path[i-1], self.path[i], color=(255,0,0,0))
        return self




if __name__ == "__main__":

    import data.brevent as data
    map = Map(data.map, data.summits, data.projections)

    map.draw_photographer_area()
    map.draw_point(data.photographer, "real")

    #map.multi_optimize_photograper().show()

    print "photographer estimated position: ", map.photographer
    print "error at real position: ", map.evaluate_photographer_position(data.photographer)
    map.show()

    #map.hot_colorize()
    #map.show()
