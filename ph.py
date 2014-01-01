#!/usr/bin/env python

from PIL import Image, ImageDraw
from math import sqrt, fabs
import numpy as np
import sys


def display(text, activation=True):
    if activation:
        print text


def intersection_lines((x1, y1),(x2, y2), (x3, y3),(x4, y4)):
    """Return the intersection of two lines defined by points."""
    num = (x4-x3)*(y1-y3)-(y4-y3)*(x1-x3)
    den = (y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)
    if den == 0:
        if num == 0:
            return (x1, y1)
        else:
            return None
    ua = num / den
    return (x1+ua*(x2-x1), y1+ua*(y2-y1))


def distance((x1, y1), (x2, y2)):
    """Return the distance between two points."""
    return sqrt((x2-x1)**2+(y2-y1)**2)


def dot((x1, y1), (x2, y2)):
    """Return the dot product of two arrays."""
    return 1.0*x1*x2+y1*y2


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


def position_lens(p, s1, s2, s3, os1, os2, os3):
    """Estimate the position of
     - the position of the lens (ortho with photographer)
     - the position of the photo (middle of the picture)
     based on:
     - the position of the photographer (p)
     - the positions of three summits on the map (s1, s2, s3)
     - the positions of the three summits on the picture
       (os1, os2, os3 which are relative to the center)
     """
    # todo:
    #  - detection of convergence before 50 iterations
    delta12 = fabs(os2-os1)
    delta23 = fabs(os3-os2)
    alpha1 = alpha3 = .5
    speed1 = speed3 = .5
    for i in range(0, 50):
        print "\nloop ", i
        print "  alpha1=%f, alpha3=%f" % (alpha1, alpha3)
        print "  speed1=%f, speed3=%f" % (speed1, speed3)
        # Compute s1_ and s3_ on [p, s1] and [p, s2] based on alphas
        s1_ = ((1-alpha1)*p[0]+alpha1*s1[0], (1-alpha1)*p[1]+alpha1*s1[1])
        s3_ = ((1-alpha3)*p[0]+alpha3*s3[0], (1-alpha3)*p[1]+alpha3*s3[1])
        print "  s1_=%s, s3_= %s" % (repr(s1_), repr(s3_))
        # Compute s2_ as intersection of [p, s2] and [s1_, s3_]
        s2_ = intersection_lines(s1_, s3_, p, s2)
        print "  s2_= %s" % (repr(s2_))
        # Compute distance of proj of summits on lens
        dist12_ = distance(s1_, s2_)
        dist23_ = distance(s2_, s3_)
        print "  dist12_=%f (target is %f)" % (dist12_, delta12)
        print "  dist23_=%f (target is %f)" % (dist23_, delta23)
        # Then compare them with expected values
        error1 = fabs(dist12_ - delta12)
        error3 = fabs(dist23_ - delta23)
        print "  error1=%f" % error1
        print "  error3=%f" % error3
        # Update alpha accordingly
        if error1 > error3:
            print "  changing 1"
            if dist12_ > delta12:
                print "    decreasing alpha1"
                alpha1 = alpha1 - speed1
                speed1 = .6 * speed1
                print "    new alpha1: %f, new speed1: %f" % (alpha1, speed1)
            elif dist12_ < delta12:
                print "    increasing alpha1"
                alpha1 = alpha1 + speed1
                speed1 = .6 * speed1
                print "    new alpha1: %f, new speed1: %f" % (alpha1, speed1)
        else:
            print "  changing 3"
            if dist23_ > delta23:
                print "    decreasing alpha3"
                alpha3 = alpha3 - speed3
                speed3 = .6 * speed3
                print "    new alpha3: %f, new speed3: %f" % (alpha3, speed3)
            elif dist23_ < delta23:
                print "    increasing alpha3"
                alpha3 = alpha3 + speed3
                speed3 = .6 * speed3
                print "    new alpha3: %f, new speed3: %f" % (alpha3, speed3)
    print "  s1_=%s, s3_= %s" % (repr(s1_), repr(s3_))
    print "  s2_= %s" % (repr(s2_))
    # Compute position of center of photo
    f = 1.0*os1/(os3-os1)
    m = (s1_[0] - f*(s3_[0]-s1_[0]),
         s1_[1] - f*(s3_[1]-s1_[1]))
    # Compute position of lens ("in front of" photographer)
    den = (s3_[0]-s1_[0])**2 + (s3_[1]-s1_[1])**2
    r = ((p[0]-s1_[0])*(s3_[0]-s1_[0])+(p[1]-s1_[1])*(s3_[1]-s1_[1])) / den
    o = (s1_[0] + r*(s3_[0]-s1_[0]),
         s1_[1] + r*(s3_[1]-s1_[1]))
    print "center of lens (O): %s" % repr(o)
    return {"lens": o,
            "picture": m,
            "projections": (s1_, s2_, s3_)}


def simulate_photo(dataset, photographer=None, lens=None):
    """Return an image simulating the photo""" 
    # Default param
    if photographer is None: photographer = dataset["r"]["photographer"]
    if lens is None: lens = dataset["r"]["lens"]
    # Get key values
    photox, photoy, middlex = 501, 200, 251
    (xp, yp) = photographer
    (xo, yo) = lens
    h = sqrt((xo-xp)**2+(yo-yp)**2)
    # Compute summits' positions relative to center of photo
    summits = []
    for summit in dataset["q"]["summits"]:
        (xm, ym) = project_on_lens(photographer, lens, summit)
        delta = ((yo-yp)*(xm-xo)-(xo-xp)*(ym-yo)) / h
        summits.append(delta)
    # compute coef to get everything to fit in picture
    alpha = (photox - 100)  / (max(summits) - min(summits))
    # Build photo
    photo = Image.new('RGBA', (photox, photoy), (255, 255, 255, 0))
    draw = ImageDraw.Draw(photo)
    for (delta, name) in zip(summits, "ABCDEFGHI"):
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
    i = int(i)
    return (255-255*i/100, 255-255*i/100, 255, 0)


class Map:

    def __init__(self, dataset):
        self.dataset = dataset
        # Compute map size
        xmax, ymax = 0, 0
        for (x, y) in self.dataset["q"]["summits"] + [self.dataset["r"]["photographer"]]:
            xmax = max(xmax, x)
            ymax = max(ymax, y)
        self.dimension = (xmax+100, ymax+100)
        # Build map
        self.map = Image.new('RGBA', self.dimension, (255, 255, 255, 0))
        self.draw = ImageDraw.Draw(self.map)
        # Draw summits
        for (summit, name) in zip(self.dataset["q"]["summits"], "ABCDEFGHI"):
            self.draw_point(summit, name)

    def copy(self):
        """Return a deep copy of the map"""
        m = Map(self.dataset)
        m.dimension = self.dimension
        m.map = self.map.copy()
        m.draw = ImageDraw.Draw(m.map)
        return m

    def show(self):
        """Display the map"""
        self.map.show()

    def save(self, filename):
        """Save map in a jpg file"""
        self.map.save(filename)

    def draw_point(self, (x, y), name=None):
        """Draw a point on the map"""
        y = self.dimension[1] - y
        self.draw.line((x-5,y, x+5,y), fill=0, width=1)
        self.draw.line((x,y-5, x,y+5), fill=0, width=1)
        if name is not None:
            self.draw.text((x+5, y+5), name, fill=0)
        return self

    def draw_segment(self, (x1, y1), (x2, y2)):
        """Draw a segment on the map"""
        y1 = self.dimension[1] - y1
        y2 = self.dimension[1] - y2
        self.draw.line((x1,y1, x2,y2), fill=0, width=1)
        return self

    def draw_photographer(self, photographer, lens, text=None):
        """Draw the photographer and the projections of the summits on the lens"""
        if text is None:
            text = "photographer"
        # Draw projections of summits on lens
        for (summit, name) in zip(self.dataset["q"]["summits"], "ABCDEFGHI"):
            projection = project_on_lens(photographer, lens, summit)
            self.draw_point(projection, name + "'")
            self.draw_segment(summit, photographer)
        # Draw photographer
        self.draw_point(photographer, text)
        return self

    def check_location(self, (x, y)):
        """Return true if the position is a valid position for the photographer
        That is, summits are seen the in the right order (left to right)."""
        summits = self.dataset["q"]["summits"]
        l = len(summits)
        for i in range(0, l):
            for j in range(i+1, l):
                (xi, yi) = summits[i]
                (xj, yj) = summits[j]
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
        return self.map

    def hot_colorize(self):
        w = Walker(self)
        # Compute errors for each pixel of the map
        errors = np.array([.0]*(self.dimension[0]*self.dimension[1]))
        errors = errors.reshape(self.dimension[0], self.dimension[1])
        mini, maxi = 99999999999, 0
        i, percentage, onepercent = 0, 0, self.dimension[0]*self.dimension[1]/100
        for x in range(0, self.dimension[0]):
            for y in range(0, self.dimension[1]):
                if not self.check_location((x, y)):
                    errors[x, y] = 0
                else:
                    w.position = (x, y)
                    (lens, error) = w.eval_position()
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
        return self.map
        

class Walker:

    def __init__(self, map):
        self.map = map
        self.position = (0,0)
    
    def move(self, x, y):
        self.position = (self.position[0]+x, self.position[1]+y)
    
    def eval_position(self, verbose=False):
        display("Showing photographer in %s:" % repr(self.position), verbose)
        # Estimate lens position based on summits 0, 2 and 4
        summits = self.map.dataset["q"]["summits"]
        projs = self.map.dataset["q"]["projections"]
        res = position_lens(self.position,
                            summits[0],
                            summits[2],
                            summits[4],
                            projs[0],
                            projs[2],
                            projs[4])
        lens = res["lens"]
        (s0_, s2_, s4_) = res["projections"]
        display("  Estimation of lens position: " + repr(res["lens"]), verbose)
        display("  Estimation of pic position: " + repr(res["picture"]), verbose)
        display("  Projection of A on lens: " + repr(s0_), verbose)
        display("  Projection of C on lens: " + repr(s2_), verbose)
        display("  Projection of E on lens: " + repr(s4_), verbose)
        # Compute expected projections of summits 1 and 3 on lens
        S0S4 = (s4_[0]-s0_[0],
                s4_[1]-s0_[1])
        alpha1 = 1.0 * (projs[1]-projs[0]) / (projs[4]-projs[0])
        s1_ = (s0_[0] + alpha1 * S0S4[0], s0_[1] + alpha1 * S0S4[1])
        alpha3 = 1.0 * (projs[3]-projs[0]) / (projs[4]-projs[0])
        s3_ = (s0_[0] + alpha3 * S0S4[0], s0_[1] + alpha3 * S0S4[1])
        display("  Expected projection of B on lens: " + repr(s1_), verbose)
        display("  Expected projection of D on lens: " + repr(s3_), verbose)
        # Compute actual projections of summits 1 and 3 on lens
        s1__ = project_on_lens(self.position, lens, summits[1])
        s3__ = project_on_lens(self.position, lens, summits[3])
        display("  Actual projection of B on lens: " + repr(s1__), verbose)
        display("  Actual projection of D on lens: " + repr(s3__), verbose)
        # Estimate error:
        d1 = distance(s1_, s1__)
        d3 = distance(s3_, s3__)
        error = d1 + d3
        display("  Estimated error: %f (%f + %f)" % (error, d1, d3), verbose)
        return (lens, error)


    def show(self, verbose=True):
        m = self.map.copy()
        (lens, error) = self.eval_position(verbose)
        m.draw_photographer(self.position, lens, "Error: %f" % error)
        m.show()



Datasets = [{"q":
              {"summits": [(100,400), (200,300), (400,400), (400,250), (300,100)],
               "projections": [-75*sqrt(2),-25*sqrt(2),0,25*sqrt(2),75*sqrt(2)]
               },
             "r": 
              {"photographer": (100, 100),
               "lens": (175, 175)}}
            ]


def init(i):
    dataset = Datasets[0]
    map = Map(dataset)
    walker = Walker(map)
    return {"dataset": dataset, "map": map, "walker": walker}

def run_tests():
    print position_lens((0,0),
                        (100,400), (400,400), (300,100),
                        -106.06601717798213, 0, 106.06601717798213)


if __name__ == "__main__":
    
    #run_tests()
    #sys.exit(-1)

    d = Datasets[0]
    map = Map(d)

    #map.copy().draw_photographer(d['r']['photographer'], d['r']['lens']).show()
    #simulate_photo(d, d['r']['photographer'], d['r']['lens']).show()

    #map.draw_photographer(d['photographer'], d['lens'])
    #map.grey_out_impossible_region()
    #map.show()

    #w = Walker(map)
    #w.move(100, 100)
    #w.show()

    map.hot_colorize()
    map.draw_photographer(d['r']['photographer'], d['r']['lens'])
    map.show()
