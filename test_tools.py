#!/usr/bin/env python

import unittest
from math import fabs, sqrt

import tools


class TestDistance(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(tools.distance((0, 0), (1, 0)), 1)
        self.assertEqual(tools.distance((0.0, 0.0), (1.0, 0.0)), 1.0)
        self.assertEqual(tools.distance((0.0, 0.0), (1.0, 0.0)), 1)
        self.assertEqual(tools.distance((0, 0), (1.0, 0.0)), 1)

    def test_slightly_advanced(self):
        self.assertEqual(tools.distance((12, 13), (12, 13)), 0)
        self.assertEqual(tools.distance((12.0, 13.0), (12.0, 13.0)), 0)


class TestIntersectionLines(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(
            tools.intersection_lines((-1.0, -1.0), (1.0, 1.0), (-1.0, 1.0), (1.0, -1.0)),
            (0.0, 0.0),
        )
        self.assertEqual(
            tools.intersection_lines((-1, 0), (1, 0), (0, 1), (0, -1)), (0, 0)
        )
        self.assertEqual(
            tools.intersection_lines((-1.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.0, -1.0)),
            (0.0, 0.0),
        )

    def test_errors(self):
        # (wrong) line defined with same points
        self.assertEqual(
            tools.intersection_lines((1.0, 1.0), (1.0, 1.0), (-1.0, -1.0), (1.0, -1.0)),
            None,
        )
        self.assertEqual(
            tools.intersection_lines((2.0, 1.0), (1.0, 1.0), (-1.0, -1.0), (-1.0, -1.0)),
            None,
        )
        self.assertEqual(
            tools.intersection_lines(
                (-1.0, -1.0), (-1.0, -1.0), (-1.0, -1.0), (-1.0, -1.0)
            ),
            None,
        )
        # Same lines
        self.assertEqual(
            tools.intersection_lines((2.0, 1.0), (1.0, 1.0), (2.0, 1.0), (1.0, 1.0)), None
        )
        # // lines
        self.assertEqual(
            tools.intersection_lines((-1.0, 1.0), (1.0, 1.0), (-1.0, -1.0), (1.0, -1.0)),
            None,
        )


class TestDot(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(tools.dot((0, 1), (0, 1)), 1)
        self.assertEqual(tools.dot((0, 1), (1, 0)), 0)
        self.assertEqual(tools.dot((0, 1), (0, -1)), -1)


class TestBarycenter(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(tools.barycenter([(-1, 0), (1, 0)]), (0, 0))
        self.assertEqual(tools.barycenter([(-1, 0), (1, 0), (0, 1), (0, -1)]), (0, 0))


class TestPhotographerArea(unittest.TestCase):

    def test_basic(self):
        envelop = tools.photographer_area(
            [(100, 400), (200, 300), (400, 400), (400, 250), (300, 100)],
            xmin=0, xmax=500, ymin=0, ymax=500
        )
        self.assertEqual(
            envelop,
            [
                (175.0, 287.5),
                (0.0, 200.0),
                (0.0, 0.0),
                (233.33333333333331, 0.0),
                (300.0, 100.0),
            ],
        )

        envelop = tools.photographer_area(
            [(522, 469), (521, 371), (445, 267), (345, 323), (303, 286)],
            xmin=0, xmax=600, ymin=0, ymax=760
        )
        self.assertEqual(
            envelop,
            [
                (524.969387755102, 760.0),
                (0.0, 760.0),
                (0.0, 516.2),
                (345.0, 323.0),
                (522.1022309389556, 479.0186320176514),
            ],
        )


class TestSummitsSelection(unittest.TestCase):

    def test_basic(self):
        l = [1, 2, 3, 4, 5, 6, 7]
        ll = tools.selections_of_five_summits(l)
        self.assertEqual(len(ll), 21)
        self.assertEqual(ll[0], [0, 1, 2, 3, 4])
        self.assertEqual(ll[20], [2, 3, 4, 5, 6])


class TestProjectOnLens(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(tools.project_on_lens((0, 0), (1, 0), (2, 0)), (1, 0))
        self.assertEqual(tools.project_on_lens((0, 0), (0, 1), (0, 2)), (0, 1))
        self.assertEqual(
            tools.project_on_lens((0.0, 0.0), (0.0, 1.0), (0.0, 2.0)), (0.0, 1.0)
        )
        self.assertEqual(
            tools.project_on_lens((1.0, 1.0), (2.0, 2.0), (3.0, 3.0)), (2.0, 2.0)
        )
        self.assertEqual(
            tools.project_on_lens((1.0, -1.0), (2.0, -2.0), (3.0, -3.0)), (2.0, -2.0)
        )


class TestChangeCoordinate(unittest.TestCase):

    def test_basic(self):
        points = [
            ("Aiguille du Triolet",  (45.9169134, 7.0246497), (1084, 669 - 158), 195),
            ("Aiguille de Talefre",  (45.8999213, 7.0040026), (975, 669 - 285),  290),
            ("Aiguille de Leschaux", (45.8874995, 7.0069444), (990, 669 - 375),  401),
            ("Point Walker",         (45.8688259, 6.9879852), (904, 669 - 514),  573),
            ("Dent du Geant",        (45.8622473, 6.9518381), (713, 669 - 562),  738)
        ]
        utmcoordinates = [p[1] for p in points]
        localcoordinates = [p[2] for p in points]
        utmtolocal, localtoutm = tools.change_coordinate_funs(utmcoordinates, localcoordinates)
        utmcoordinates_ = [localtoutm(utmtolocal(p)) for p in utmcoordinates]
        diffs = [(p[0] - q[0], p[1] - q[1]) for p, q in zip(utmcoordinates, utmcoordinates_)]
        for d in diffs:
            self.assertEqual(abs(d[0]), 0) 
            self.assertEqual(abs(d[1]), 0) 


if __name__ == "__main__":
    unittest.main()
