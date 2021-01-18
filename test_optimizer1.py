#!/usr/bin/env python

import unittest
from math import fabs, sqrt

import optimizer1


class TestPositionLens(unittest.TestCase):

    def test_basic(self):
        res = optimizer1.optimize_lens(
            (0, 0),  # photographer
            [(-10, 10), (0, 10), (10, 10)],  # summits
            [-1, 0, 1],
        )  # projections
        self.assertTrue(fabs(res.lens[0] - 0) < 10 ** -7)
        self.assertTrue(fabs(res.lens[1] - 1) < 10 ** -7)
        self.assertTrue(fabs(res.picture[0] - 0) < 10 ** -7)
        self.assertTrue(fabs(res.picture[1] - 1) < 10 ** -7)
        self.assertTrue(fabs(res.projections[0][0] - (-1)) < 10 ** -7)
        self.assertTrue(fabs(res.projections[0][1] - 1) < 10 ** -7)
        self.assertTrue(fabs(res.projections[1][0] - 0) < 10 ** -7)
        self.assertTrue(fabs(res.projections[1][1] - 1) < 10 ** -7)
        self.assertTrue(fabs(res.projections[2][0] - 1) < 10 ** -7)
        self.assertTrue(fabs(res.projections[2][1] - 1) < 10 ** -7)

    def test_diagonal(self):
        res = optimizer1.optimize_lens(
            (100, 100),  # photographer
            [(100, 400), (400, 400), (300, 100)],  # summits
            [-75 * sqrt(2), 0, 75 * sqrt(2)],  # projections
        )
        self.assertTrue(fabs(res.lens[0] - 175) < 10 ** -6)
        self.assertTrue(fabs(res.lens[1] - 175) < 10 ** -6)
        self.assertTrue(fabs(res.picture[0] - 175) < 10 ** -6)
        self.assertTrue(fabs(res.picture[1] - 175) < 10 ** -6)
        self.assertTrue(fabs(res.projections[0][0] - 100) < 10 ** -6)
        self.assertTrue(fabs(res.projections[0][1] - 250) < 10 ** -5)
        self.assertTrue(fabs(res.projections[1][0] - 175) < 10 ** -6)
        self.assertTrue(fabs(res.projections[1][1] - 175) < 10 ** -6)
        self.assertTrue(fabs(res.projections[2][0] - 250) < 10 ** -6)
        self.assertTrue(fabs(res.projections[2][1] - 100) < 10 ** -6)

    def test_error(self):
        # photographer is on a summit!
        res = optimizer1.optimize_lens(
            (300, 100),
            [(100, 400), (400, 400), (300, 100)],
            [-106.06601717798213, 0, 106.06601717798213],
        )
        self.assertTrue(fabs(res.lens[0] - 300) == 0)
        self.assertTrue(fabs(res.lens[1] - 100) == 0)


if __name__ == "__main__":
    unittest.main()
