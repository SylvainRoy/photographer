#/usr/bin/env python

"""
The class Map contains all basic drawing action on a Map.
"""

import numpy as np
from PIL import Image as PILImage
from PIL import ImageDraw
from matplotlib.pyplot import imshow

from tools import project_on_lens


def percentage_to_color(i):
    """Return a color that goes from white to blue based on a percentage."""
    try:
        i = int(i)
    except:
        i = 0
    return (255 - 255 * i // 100, 255 - 255 * i // 100, 255, 0)


class Map:
    """
    A map on which to draw segments, points, etc.
    """

    def __init__(self, file=None, dimensions=None):
        if file is not None:
            self.map = PILImage.open(file)
            self.dimensions = self.map.size
        elif dimensions is not None:
            self.dimensions = dimensions
            self.map = PILImage.new("RGB", self.dimensions, (255, 255, 255, 0))
        else:
            raise RuntimeError("A Map requires either a file or a size.")
        self.draw = ImageDraw.Draw(self.map)
        self.error_matrix = None
        self.error_min = None
        self.error_max = None

    def copy(self):
        """Return a deep copy of the map"""
        m = Map(self.dimensions)
        m.map = self.map.copy()
        m.draw = ImageDraw.Draw(m.map)
        return m

    def show(self, notebook=True):
        """Display the map"""
        if notebook:
            imshow(np.asarray(self.map))
        else:
            self.map.show()
        return self

    def show_in_notebook(self):
        """Display the map in a notebook."""


    def save(self, filename):
        """Save map in a jpg file"""
        self.map.save(filename)
        return self

    def draw_point(self, point, name="", color=0):
        """Draw a point on the map"""
        (x, y) = point
        y = self.dimensions[1] - y
        self.draw.line((x - 5, y, x + 5, y), fill=color, width=1)
        self.draw.line((x, y - 5, x, y + 5), fill=color, width=1)
        self.draw.text((x + 5, y + 5), name, fill=color)
        return self

    def draw_segment(self, p1, p2, color=0):
        """Draw a segment on the map"""
        self.draw.line(
            (p1[0], self.dimensions[1] - p1[1], p2[0], self.dimensions[1] - p2[1]),
            fill=color,
            width=1,
        )
        return self

    def draw_area(self, points, color=0):
        """Draw a path defined by a list of points."""
        for i in range(0, len(points)):
            self.draw_segment(
                points[i],
                points[(i + 1) % len(points)],
                color
            )
            self.draw_point(points[i], color=color)
        return self

    def draw_path(self, points, color=0):
        """Draw a close area defined by a list of points."""
        for i in range(0, len(points)-1):
            self.draw_segment(
                points[i],
                points[(i + 1)],
                color
            )
            self.draw_point(points[i], color=color)
        self.draw_point(points[i+1], color=color)
        return self

    def draw_lens(self, lens, summits, photographer, color=0):
        """Draw projections of summits on lens."""
        if lens is not None:
            for (summit, name) in zip(summits, "ABCDEFGHIKLMNOPQRSTUVWXYZ"):
                projection = project_on_lens(photographer, lens, summit)
                self.draw_point(projection, name=name + "'", color=color)
                self.draw_segment(summit, photographer, color=color)
        return self

    def grey_out_region(self, testfun):
        """
        Grey out the pixels for which textfun(x, y) is True.
        """
        for x in range(0, self.dimensions[0]):
            for y in range(0, self.dimensions[1]):
                if testfun((x, y)):
                    y = self.dimensions[1] - y - 1
                    newcolor = tuple(
                        [max(i - 20, 0) for i in self.map.getpixel((x, y))]
                    )
                    self.draw.point((x, y), fill=newcolor)
        return self

    def reset_color_matrix(self):
        """Reset the error matrix."""
        self.error_matrix = None
        self.error_max = None
        self.error_min = None
        return self

    def compute_color_matrix(self, colorfun, incr=0):
        """
        Compute, save and return the error matrix for colorfun.
        """
        if self.error_matrix is not None:
            return self.error_matrix, self.error_min, self.error_max

        self.error_matrix = np.zeros(self.dimensions)
        self.error_min, self.error_max = 99999999999, 0

        # For each group of pixels, compute the error, min and max
        percentage, i = 0, 0
        total = len(range(incr, self.dimensions[0], 2*incr+1)) * len(range(incr, self.dimensions[1], 2*incr+1))
        for x in range(incr, self.dimensions[0], 2*incr+1):
            for y in range(incr, self.dimensions[1], 2*incr+1):
                error = colorfun((x, y))
                self.error_matrix[x, y] = error
                self.error_min = min(self.error_min, error)
                self.error_max = max(self.error_max, error)
                i += 1
                if 100 * i / total > percentage:
                    percentage += 1
                    print("%i %%" % percentage)
        print("error min, max: %f, %f" % (self.error_min, self.error_max))
        return self.error_matrix, self.error_min, self.error_max

    def hot_colorize(self, colorfun, incr=0):
        """
        Colorize the map with the error value. (Faster, but still...).
        incr is an unsigned int. The bigger, the faster and the less accurate.
        incr = 0 means every pixel is computed.
        """
        error_matrix, error_min, error_max = self.compute_color_matrix(colorfun, incr)
        # Colorize map with normalized error
        for x in range(incr, self.dimensions[0], 2*incr+1):
            for y in range(incr, self.dimensions[1], 2*incr+1):
                c = error_matrix[x, y]
                v = percentage_to_color(100 * (c - error_min) / (error_max - error_min))
                for i in range(-incr, incr + 1):
                    for j in range(-incr, incr + 1):
                        y_ = self.dimensions[1] - y - 1
                        self.draw.point((x + i, y_ + j), fill=v)
        return self
