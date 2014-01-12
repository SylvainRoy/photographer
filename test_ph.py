#!/usr/bin/env python

import unittest
import ph
from math import fabs, sqrt

class TestDistance(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic(self):
        self.assertEqual(ph.distance((0,0), (1,0)), 1)
        self.assertEqual(ph.distance((.0,.0), (1.0,.0)), 1.0)
        self.assertEqual(ph.distance((.0,.0), (1.0,.0)), 1)
        self.assertEqual(ph.distance((0,0), (1.0,.0)), 1)

    def test_slightly_advanced(self):
        self.assertEqual(ph.distance((12,13), (12,13)), 0)
        self.assertEqual(ph.distance((12.0,13.0), (12.0,13.0)), 0)


class TestIntersectionLines(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic(self):
        self.assertEqual(ph.intersection_lines((-1.,-1.),(1.,1.), (-1.,1.),(1.,-1.)), (0.,0.))
        self.assertEqual(ph.intersection_lines((-1,0),(1,0), (0,1),(0,-1)), (0,0))
        self.assertEqual(ph.intersection_lines((-1.,0.),(1.,0.), (0.,1.),(0.,-1.)), (0.,0.))

    def test_errors(self):
        # (wrong) line defined with same points
        self.assertEqual(ph.intersection_lines((1.,1.),(1.,1.), (-1.,-1.),(1.,-1.)), None)
        self.assertEqual(ph.intersection_lines((2.,1.),(1.,1.), (-1.,-1.),(-1.,-1.)), None)
        self.assertEqual(ph.intersection_lines((-1.,-1.),(-1.,-1.), (-1.,-1.),(-1.,-1.)), None)
        # Same lines
        self.assertEqual(ph.intersection_lines((2.,1.),(1.,1.), (2.,1.),(1.,1.)), None)
        # // lines
        self.assertEqual(ph.intersection_lines((-1.,1.),(1.,1.), (-1.,-1.),(1.,-1.)), None)
        

class TestDot(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic(self):
        self.assertEqual(ph.dot((0,1), (0,1)), 1)
        self.assertEqual(ph.dot((0,1), (1,0)), 0)
        self.assertEqual(ph.dot((0,1), (0,-1)), -1)


class TestProjectOnLens(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic(self):
        self.assertEqual(ph.project_on_lens((0,0), (1,0), (2,0)), (1,0))
        self.assertEqual(ph.project_on_lens((0,0), (0,1), (0,2)), (0,1))
        self.assertEqual(ph.project_on_lens((0.,0.), (0.,1.), (0.,2.)), (0.,1.))
        self.assertEqual(ph.project_on_lens((1.,1.), (2.,2.), (3.,3.)), (2.,2.))
        self.assertEqual(ph.project_on_lens((1.,-1.), (2.,-2.), (3.,-3.)), (2.,-2.))


class TestPositionLens(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic(self):
        res = ph.optimize_lens((0,0),                       # photographer
                               [(-10,10), (0,10), (10,10)], # summits
                               [-1, 0, 1])                  # projections
        self.assert_(fabs(res['lens'][0] - 0) < 10**-7)
        self.assert_(fabs(res['lens'][1] - 1) < 10**-7)
        self.assert_(fabs(res['picture'][0] - 0) < 10**-7)
        self.assert_(fabs(res['picture'][1] - 1) < 10**-7)
        self.assert_(fabs(res['projections'][0][0] - (-1)) < 10**-7)
        self.assert_(fabs(res['projections'][0][1] - 1) < 10**-7)
        self.assert_(fabs(res['projections'][1][0] - 0) < 10**-7)
        self.assert_(fabs(res['projections'][1][1] - 1) < 10**-7)
        self.assert_(fabs(res['projections'][2][0] - 1) < 10**-7)
        self.assert_(fabs(res['projections'][2][1] - 1) < 10**-7)

    def test_diagonal(self):
        res = ph.optimize_lens((100,100),                         # photographer
                               [(100,400), (400,400), (300,100)], # summits
                               [-75*sqrt(2), 0, 75*sqrt(2)])      # projections
        self.assert_(fabs(res['lens'][0] - 175) < 10**-6)
        self.assert_(fabs(res['lens'][1] - 175) < 10**-6)
        self.assert_(fabs(res['picture'][0] - 175) < 10**-6)
        self.assert_(fabs(res['picture'][1] - 175) < 10**-6)
        self.assert_(fabs(res['projections'][0][0] - 100) < 10**-6)
        self.assert_(fabs(res['projections'][0][1] - 250) < 10**-5)
        self.assert_(fabs(res['projections'][1][0] - 175) < 10**-6)
        self.assert_(fabs(res['projections'][1][1] - 175) < 10**-6)
        self.assert_(fabs(res['projections'][2][0] - 250) < 10**-6)
        self.assert_(fabs(res['projections'][2][1] - 100) < 10**-6)

    def test_error(self):
        # photographer is on a summit!
        res = ph.optimize_lens((300, 100),
                               [(100, 400), (400, 400), (300, 100)],
                               [-106.06601717798213, 0, 106.06601717798213])
        self.assert_(fabs(res['lens'][0] - 300) == 0)
        self.assert_(fabs(res['lens'][1] - 100) == 0)
        

class TestBarycenter(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic(self):
        self.assertEqual(ph.barycenter([(-1,0), (1,0)]), (0,0))
        self.assertEqual(ph.barycenter([(-1,0), (1,0), (0,1), (0,-1)]), (0,0))


class TestPhotographerArea(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic(self):
        envelop = ph.photographer_area([(100,400), (200,300), 
                                        (400,400), (400,250),(300,100)],
                                       (500, 500))
        self.assertEqual(envelop,
                         [(175.0, 287.5), (0.0, 200.0), (0.0, 0.0), 
                          (233.33333333333331, 0.0), (300.0, 100.0)])

        envelop = ph.photographer_area([(522, 469), (521, 371), (445, 267), (345, 323), (303, 286)],
                                       (600, 760))
        self.assertEqual(envelop,
                         [(524.969387755102, 760.0), (0.0, 760.0), (0.0, 516.2), (345.0, 323.0), (522.1022309389556, 479.0186320176514)])


class TestSummitsSelection(unittest.TestCase):

    def setUp(self):
        pass

    def test_basic(self):
        l  = [1,2,3,4,5,6,7]
        ll = ph.selections_of_five_summits(l)
        self.assertEqual(len(ll), 21)
        self.assertEqual(ll[0], [0,1,2,3,4])
        self.assertEqual(ll[20], [2,3,4,5,6])


if __name__ == '__main__':
    unittest.main()
