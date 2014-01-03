#!usr/bin/env python

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
        # lines defined with same points
        self.assertRaises(RuntimeError, ph.intersection_lines, (1.,1.),(1.,1.), (-1.,-1.),(1.,-1.))
        self.assertRaises(RuntimeError, ph.intersection_lines, (2.,1.),(1.,1.), (-1.,-1.),(-1.,-1.))
        # Same lines
        self.assertRaises(RuntimeError, ph.intersection_lines, (2.,1.),(1.,1.), (2.,1.),(1.,1.))
        # // lines
        self.assertRaises(RuntimeError, ph.intersection_lines, (-1.,1.),(1.,1.), (-1.,-1.),(1.,-1.))
        

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
        res = ph.position_lens((0,0),                     # photographer
                               (-10,10), (0,10), (10,10), # summits
                               -1, 0, 1)                  # projections
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
        res = ph.position_lens((100,100),                       # photographer
                               (100,400), (400,400), (300,100), # summits
                               -75*sqrt(2), 0, 75*sqrt(2))      # projections
        self.assert_(fabs(res['lens'][0] - 175) < 10**-5)
        self.assert_(fabs(res['lens'][1] - 175) < 10**-5)
        self.assert_(fabs(res['picture'][0] - 175) < 10**-5)
        self.assert_(fabs(res['picture'][1] - 175) < 10**-5)
        self.assert_(fabs(res['projections'][0][0] - 100) < 10**-5)
        self.assert_(fabs(res['projections'][0][1] - 250) < 10**-5)
        self.assert_(fabs(res['projections'][1][0] - 175) < 10**-5)
        self.assert_(fabs(res['projections'][1][1] - 175) < 10**-5)
        self.assert_(fabs(res['projections'][2][0] - 250) < 10**-5)
        self.assert_(fabs(res['projections'][2][1] - 100) < 10**-5)

    def test_error(self):
        # photographer is on a summit!
        res = ph.position_lens((300, 100),
                               (100, 400), (400, 400), (300, 100),
                               -106.06601717798213, 0, 106.06601717798213)
        self.assert_(fabs(res['lens'][0] - 300) == 0)
        self.assert_(fabs(res['lens'][1] - 100) == 0)
        

if __name__ == '__main__':
    unittest.main()
