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


class TestDet(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(tools.det((1, 0), (0, 1)), 1)
        self.assertEqual(tools.det((1, 0), (0, -1)), -1)
        self.assertEqual(tools.det((1, 0), (1, 0)), 0)
        self.assertEqual(tools.det((2, 0), (0, 1)), 2)


class TestBarycenter(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(tools.barycenter([(-1, 0), (1, 0)]), (0, 0))
        self.assertEqual(tools.barycenter([(-1, 0), (1, 0), (0, 1), (0, -1)]), (0, 0))


class TestExtrems(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(tools.extrems(
                            (0,0),
                            [(-2, 1),(-1, 1),(0, 1),(1, 1),(2, 1)]
                         ),
                         ((-2, 1), (2, 1))
        )
        self.assertEqual(tools.extrems(
                            (0,0),
                            [(-2, -1),(-1, -1),(0, -1),(1, -1),(2, -1)]
                         ),
                         ((2, -1), (-2, -1))
        )
        self.assertEqual(tools.extrems(
                            (0,0),
                            [(-1, 1),(-2, 1),(0, 1),(1, 1),(2, 1)]
                         ),
                         ((-2, 1), (2, 1))
        )
        self.assertEqual(tools.extrems(
                            (0,0),
                            [(-2, -1),(-1, -1),(2, -1),(0, -1),(1, -1)]
                         ),
                         ((2, -1), (-2, -1))
        )
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

        envelop = tools.photographer_area(
            [(200, 350), (200, 400), (300, 400), (350, 350)]
        )
        self.assertEqual(
            envelop,
            [(350.0, 350.0),
             (200.0, 350.0),
             (200.0, 192.99725276798705),
             (444.50274723201295, 192.99725276798705),
             (444.5027472320129, 255.49725276798708)],
        )
        
        envelop = tools.photographer_area(
            [(200, 400), (230, 300), (270, 300), (300, 400)]
        )
        self.assertEqual(
            envelop,
            [(250.0, 233.33333333333331),
             (215.0, 116.6666666666666),
             (285.0, 116.66666666666663)],
        )

        envelop = tools.photographer_area(
            [(200, 400), (300, 400)])
        self.assertEqual(
            envelop,
            [(350.0, 400.0), (150.0, 400.0), (150.0, 300.0), (350.0, 300.0)],
        )

        envelop = tools.photographer_area(
            [(200, 400), (300, 300), (350, 400)]
        )
        self.assertEqual(
            envelop,
            [(300.0, 300.0),
             (243.5805865477583, 187.1611730955166),
             (412.8388269044834, 187.16117309551657)]
        )

        envelop = tools.photographer_area(
            [(200, 400), (300, 490), (350, 400)]
        )
        self.assertEqual(
            envelop,
            [(350.0, 400.0),
             (200.0, 400.0),
             (106.19559659218105, 315.57603693296295),
             (106.19559659218103, 252.86226325884772),
             (431.7431870784179, 252.86226325884775)],
        )
    
    def test_examples(self):

        # Statueofliberty
        envelop = tools.photographer_area(
            [[315, 938],
             [326, 719],
             [430, 929],
             [382, 724],
             [940, 1425],
             [1086, 1610],
             [648, 929],
             [686, 844]]
        )
        self.assertEqual(
            envelop,
            [(305.2060523274141, 396.0258484816644),
             (335.68434244536695, 526.1935458604214),
             (329.4006880531624, 651.2953923961304),
             (230.2507880910683, 525.6602451838879),
             (-299.79920589903577, -544.6330119115144)],
        )

        # Statue of liberty from lat&lng with one point removed
        # This case used to generate a bug due to the high values of x, y.
        envelop = tools.photographer_area(
            [(580699.7382771571, 4507400.68664104),
             (580804.6916304922, 4505676.703058445),
             (581609.581410255, 4507347.541329558),
             (581254.816163511, 4505719.029647791),
             (585631.31816891, 4511326.417595701),
             (583353.5087769624, 4507365.711354206),
             (583656.1661844028, 4506700.757532055)]
        )
        self.assertEqual(
            envelop,
            [(580552.5460644213, 4502495.334343305),
             (580900.9928142795, 4504094.841645178),
             (580834.8707532529, 4505180.975094324),
             (580132.1676092467, 4504280.63753346),
             (572666.3251361174, 4488782.59588373)],
        )

        # Brevent
        envelop = tools.photographer_area(
            [[553, 410],
             [560, 221],
             [488, 145],
             [424, 22],
             [298, 104],
             [226, 174],
             [153, 50]],
            xmin=0, xmax=672, ymin=0, ymax=492
        )
        self.assertEqual(
            envelop,
            [(413.2096774193549, 492.0),
             (0.0, 492.0),
             (0.0, 393.72222222222223),
             (226.0, 174.0)]
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
