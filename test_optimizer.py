#!/usr/bin/env python

import unittest
from math import fabs, sqrt

import optimizer


class TestPositionPicture(unittest.TestCase):

    def test_basic(self):
        res = optimizer.optimize_picture(
            (0, 0),                         # photographer
            [(-10, 10), (0, 10), (10, 10)], # summits
            [-1, 0, 1],                     # projections
        )
        self.assertAlmostEqual(res.projections[0][0], -1, 7)
        self.assertAlmostEqual(res.projections[0][1], 1, 7)
        self.assertAlmostEqual(res.projections[1][0], 0, 7)
        self.assertAlmostEqual(res.projections[1][1], 1, 7)
        self.assertAlmostEqual(res.projections[2][0], 1, 7)
        self.assertAlmostEqual(res.projections[2][1], 1, 7)

    def test_diagonal(self):
        res = optimizer.optimize_picture(
            (100, 100),                             # photographer
            [(100, 400), (400, 400), (300, 100)],   # summits
            [-75 * sqrt(2), 0, 75 * sqrt(2)],       # projections
        )
        self.assertAlmostEqual(res.projections[0][0], 100, 7)
        self.assertAlmostEqual(res.projections[0][1], 250, 7)
        self.assertAlmostEqual(res.projections[1][0], 175, 3)
        self.assertAlmostEqual(res.projections[1][1], 175, 3)
        self.assertAlmostEqual(res.projections[2][0], 250, 2)
        self.assertAlmostEqual(res.projections[2][1], 100, 7)

    def test_error(self):
        # photographer is on a summit!
        res = optimizer.optimize_picture(
            (300, 100),
            [(100, 400), (400, 400), (300, 100)],
            [-106.06601717798213, 0, 106.06601717798213],
        )
        # The projection of the third summit should be on the photographer.
        # And no exception should be thrown.
        # That's all there is too test, really.
        self.assertEqual(res.projections[2][0], 300)
        self.assertEqual(res.projections[2][1], 100)


if __name__ == "__main__":
    unittest.main()
