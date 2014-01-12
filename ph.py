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



def intersection_lines((x1, y1),(x2, y2), (x3, y3),(x4, y4)):
    """Return the intersection of two lines defined by points."""
    den = 1.0*(y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)
    if den == 0:
        return None
    num = 1.0*(x4-x3)*(y1-y3)-(y4-y3)*(x1-x3)
    ua = num / den
    return (x1+ua*(x2-x1), y1+ua*(y2-y1))


def distance((x1, y1), (x2, y2)):
    """Return the distance between two points."""
    return sqrt((x2-x1)**2+(y2-y1)**2)


def dot((x1, y1), (x2, y2)):
    """Return the dot product of two vectors."""
    return 1.0*x1*x2+y1*y2


def barycenter(points, weights=None):
    """Compute the barycenter of a list of points (that have the same weight)."""
    if weights is None:
        weights = [1.]*len(points)
    sumWeights = sum(weights)
    return (sum([p[0]*w for (p,w) in zip(points, weights)])/sumWeights,
            sum([p[1]*w for (p,w) in zip(points, weights)])/sumWeights)


def photographer_area(summits, mapDimension):
    """
    Return the envelop (a list of point) of the area where the photograph is located.
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
            inter = intersection_lines(vectors[i][0],vectors[i][1],
                                       vectors[j][0],vectors[j][1])
            if inter is not None:
                intersections.add(inter)
    # Filter out all the points that are not acceptable
    # (i.e. cross product > 0)
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
    # Compute barycenter of envelop
    bary = barycenter(envelop)
    # Sort points (trigo order) of the (convex) envelop
    pabove = [p for p in envelop if p[1]-bary[1] >=0 ]
    pbelow = [p for p in envelop if p[1]-bary[1] <0 ]
    pabovesorted = sorted(pabove, 
                          key=lambda p: -1.0*(p[0]-bary[0]) / sqrt((p[0]-bary[0])**2+(p[1]-bary[1])**2))
    pbelowsorted = sorted(pbelow, 
                          key=lambda p: 1.0*(p[0]-bary[0]) / sqrt((p[0]-bary[0])**2+(p[1]-bary[1])**2))
    return pabovesorted + pbelowsorted


def project_on_lens(photographer, lens, summit):
    """
    Return the projection of a summit on the lens.
    The center of the lens is in 'lens'. The lens is 'orthogonal' with the photographer.
    """
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


def position_lens(p, summits, alpha):
    """
    Position the lens based on alpha parameter:
      s1_ and sM_ are the projections of s1 and sN on the lens based on alphas.
    Then, compute s2_, ..., sN the projections of s2, ..., sN on the
      (now positioned) lens.
    Return the projections of all summits on the lens
    """
    s1, s2toN, sM = summits[0], summits[1:-1], summits[-1]
    if alpha[0] == 0:
        s1_ = p
        sM_ = ((1-alpha[1])*p[0]+alpha[1]*sM[0],
               (1-alpha[1])*p[1]+alpha[1]*sM[1])
        s2toN_ = [p for x in s2toN]
    elif alpha[1] == 0:
        s1_ = ((1-alpha[0])*p[0]+alpha[0]*s1[0],
               (1-alpha[0])*p[1]+alpha[0]*s1[1])
        sM_ = p
        s2toN_ = [p for x in s2toN]
    else:
        s1_ = ((1-alpha[0])*p[0]+alpha[0]*s1[0],
               (1-alpha[0])*p[1]+alpha[0]*s1[1])
        sM_ = ((1-alpha[1])*p[0]+alpha[1]*sM[0],
               (1-alpha[1])*p[1]+alpha[1]*sM[1])
        s2toN_ = [intersection_lines(s1_,sM_, p,x) for x in s2toN]
    # Build list of projection points
    s_ = [s1_] + s2toN_ + [sM_]
    return s_


def optimize_lens(p, summits, projections):
    """Estimate the position of
     - the position of the lens (ortho with photographer)
     - the position of the photo (middle of the picture)
     based on:
     - the position of the photographer (p)
     - the positions of at least three summits on the map
     - the positions of the summits on the picture (relative to any point of the picture)
     """
    p1, pM = projections[0], projections[-1]
    deltas = []
    for i in range(1, len(projections)):
        deltas.append(fabs(projections[i] - projections[i-1]))
    def error_to_minimize(alpha):
        # Positions lens based on alpha
        s_ = position_lens(p, summits, alpha)
        # Compute the distances of the projections of the summits on lens
        distances = []
        for i in range(1, len(s_)):
            distances.append(distance(s_[i-1], s_[i]))
        # Compute the sum of the errors
        error = 0
        for i in range(0, len(distances)):
            error += (fabs(distances[i] - deltas[i]))**2
        #print "alpha(%.15f, %.15f) = %.15f" % (alpha[0], alpha[1], error)
        return error
    # find the values of alpha that minimise the distances between expected
    # and actual projections of the summits on the lens.
    res = minimize(error_to_minimize, [.5,.5],
                   method='L-BFGS-B',
                   bounds=((0, 1), (0, 1)))
    alpha = res.x
    # (re)compute the position of the summits' projection on the lens
    s_ = position_lens(p, summits, alpha)
    # Compute position of center of picture
    f = 1.0*p1/(pM-p1)
    m = (s_[0][0] - f*(s_[-1][0]-s_[0][0]),
         s_[0][1] - f*(s_[-1][1]-s_[0][1]))
    # Compute position of lens ("in front of" photographer)
    den = (s_[-1][0]-s_[0][0])**2 + (s_[-1][1]-s_[0][1])**2
    r = ((p[0]-s_[0][0])*(s_[-1][0]-s_[0][0])+(p[1]-s_[0][1])*(s_[-1][1]-s_[0][1])) / den
    o = (s_[0][0] + r*(s_[-1][0]-s_[0][0]),
         s_[0][1] + r*(s_[-1][1]-s_[0][1]))
    return {"lens": o,
            "picture": m,
            "projections": s_,
            "error": res.fun}


def optimize_photograper(init, summits, projections, mapDimension, path=None):
    """Return the position where the photograper has taken the picture."""
    # define error function to minimize
    def error_to_minimize(position):
        if path is not None:
            path.append(position)
        res =  optimize_lens(position, summits, projections)
        #print "eval(%f, %f) = %f" % (position[0], position[1], res['error'])
        return res['error']
    # Minimize error function
    res = minimize(error_to_minimize,
                   init,
                   method='L-BFGS-B',
                   bounds=((0, mapDimension[0]), (0, mapDimension[1])))
    return {"photographer": res.x,
            "error": res.fun}


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
    for (delta, name) in zip(deltas, "ABCDEFGHIKLMNOPQRSTUVWXYZ"):
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
        for (summit, name) in zip(self.summits, "ABCDEFGHIKLMNOPQRSTUVWXYZ"):
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
        #t += "(%.1f,%.1f)" % (x, y)
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
        """Draw the photographer on the map."""
        if photographer is None:
            photographer = self.photographer
        if text is None:
            text = "P"
        self.draw_point(photographer, name=text, color=color)
        return self

    def draw_search_path(self, path=None, color=0):
        """Draw path to photographer."""
        if path is None:
            path = self.path
        if path is not None and len(path) > 1:
            for i in range(1, len(path)):
                self.draw_segment(path[i-1], path[i], color=(255,0,0,0))
        return self

    def draw_lens(self, lens=None, color=0):
        """Draw projections of summits on lens."""
        if lens is None:
            lens = self.lens
        if lens is not None:
            for (summit, name) in zip(self.summits, "ABCDEFGHIKLMNOPQRSTUVWXYZ"):
                projection = project_on_lens(photographer, lens, summit)
                self.draw_point(projection, name=name+"'", color=color)
                self.draw_segment(summit, photographer, color=color)
        return self


    def check_location(self, (x, y)):
        """
        Return true if the position is a valid position for the photographer
        That is, summits are seen the in the right order (left to right).
        """
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
        """
        Grey out the region where the photographer cannot be
        since he would not see the summit in the right order.
        """
        for x in range(0, self.dimension[0]):
            for y in range(0, self.dimension[1]):
                if not self.check_location((x, y)):
                    y = self.dimension[1] - y - 1
                    newcolor = tuple([max(i-20, 0)
                                      for i in self.map.getpixel((x, y))])
                    self.draw.point((x, y), fill=newcolor)
        return self

    def hot_colorize(self):
        """Colorize the map with the error value (it takes time...)."""
        errors = np.array([.0]*(self.dimension[0]*self.dimension[1]))
        errors = errors.reshape(self.dimension[0], self.dimension[1])
        mini, maxi = 99999999999, 0
        i, percentage, onepercent = 0, 0, self.dimension[0]*self.dimension[1]/100
        for x in range(0, self.dimension[0]):
            for y in range(0, self.dimension[1]):
                if self.check_location((x, y)):
                    try:
                        error = optimize_lens((x,y),
                                              self.summits,
                                              self.projections)
                        error = error['error']
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
                    if 1 > 3:
                        break
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
        """Draw the area where the photographer can be."""
        envelop = self.photographer_area()
        for i in range(0, len(envelop)):
            self.draw_segment(envelop[i], envelop[(i+1)%len(envelop)])
        return self

    def photographer_area(self):
        """Return the area where the photographer can be."""
        return photographer_area(self.summits, self.dimension)

    def evaluate_photographer_position(self, photographer=None):
        """Return the error associated to the photographer position."""
        if photographer is None:
            photographer = self.photographer
        res = optimize_lens(photographer,
                            self.summits,
                            self.projections)
        return res['error']

    def optimize_photograper(self, init=None, summits=None, projections=None, draw=False, drawPath=False):
        """Position the photographer where the picture was taken."""
        if summits is None:
            summits = self.summits
        if projections is None:
            projections = self.projections
        if init is None:
            # Takes 'middle' of the area where the photographer can be as start of search
            envelop = photographer_area(self.summits, self.dimension)
            init = barycenter(envelop)
        # Find the best position for the photographer starting from barycenter
        self.path = []
        res = optimize_photograper(init=init, 
                                   summits=summits,
                                   projections=projections,
                                   mapDimension=self.dimension,
                                   path=self.path)
        self.photographer = res['photographer']
        error = res['error']
        # Draw photographer and path of the search
        if draw:
            self.draw_photographer(text="%.8f" % error)
        if drawPath:
            self.draw_search_path()
        return res
    
    def multi_optimize_photograper(self, init=None, draw=False, drawPath=False):
        """
        Position the photographer where the picture was taken for all combinations of 5 summits.
        """
        # Takes 'middle' of area where the photographer can be as start of search
        combinations = selections_of_five_summits(self.summits)
        counter = 1
        positions = []
        for comb in combinations:
            print "%i/%i" % (counter, len(combinations))
            counter += 1
            # Find the best position for the photographer
            self.path = []
            res = self.optimize_photograper(
                init=init,
                summits=[data.summits[comb[i]] for i in range(0, 5)],
                projections=[data.projections[comb[i]] for i in range(0, 5)],
                draw=False,
                drawPath=False)
            res['summits_used'] = comb
            positions.append(res)
        sortedPositions = sorted(positions, key=lambda p: p["error"])
        if drawPath:
            self.draw_search_path()
        if draw:
            for (p, t) in zip(sortedPositions, "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                self.draw_photographer(p["photographer"], text=t+"(%f)" % (1./p["error"]))
            bary = barycenter([i['photographer'] for i in sortedPositions],
                              [1./i['error'] for i in sortedPositions])
            print "bary: ", bary
            self.draw_photographer(bary, text="Bary")
        return sortedPositions




if __name__ == "__main__":

    import data.brevent as data
    map = Map(data.map, data.summits, data.projections)

    map.hot_colorize()
    map.draw_photographer_area()
    map.draw_point(data.photographer, "R")

    #map.multi_optimize_photograper(draw=True, drawPath=False)
    map.optimize_photograper(draw=True, drawPath=True)

    map.save("brevent-solved.jpg")
    map.show()
    
