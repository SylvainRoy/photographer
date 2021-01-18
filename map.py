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

    def hot_colorize(self, colorfun):
        """Colorize the map with the error value (it takes time...)."""
        # error for each pizel will be stored in an array
        errors = np.array([0.0] * (self.dimensions[0] * self.dimensions[1]))
        errors = errors.reshape(self.dimensions[0], self.dimensions[1])
        mini, maxi = 99999999999, 0
        # For each pixel, compute the error
        i, percentage, onepercent = 0, 0, self.dimensions[0] * self.dimensions[1] / 100
        for x in range(0, self.dimensions[0]):
            for y in range(0, self.dimensions[1]):
                error = colorfun((x, y))
                errors[x, y] = error
                mini = min(mini, error)
                maxi = max(maxi, error)
                i += 1
                if i > onepercent:
                    percentage += 1
                    i = 0
                    print("colorization: %i %%" % percentage)
        r = (maxi - mini) / 100
        print("error min, max: %f, %f" % (mini, maxi))
        # Colorize map wiht normalized error
        for x in range(0, self.dimensions[0]):
            for y in range(0, self.dimensions[1]):
                c = errors[x, y]
                if c != 0:
                    v = percentage_to_color(r * c)
                    y_ = self.dimensions[1] - y - 1
                    self.draw.point((x, y_), fill=v)
        return self

    def fast_hot_colorize(self, colorfun, incr=10):
        """
        Colorize the map with the error value. (Faster, but still...).
        incr is an unsigned int. incr = 0 means every pixel is computed.
        """
        errors = np.array([0.0] * (self.dimensions[0] * self.dimensions[1]))
        errors = errors.reshape(self.dimensions[0], self.dimensions[1])
        mini, maxi = 99999999999, 0
        # For each pixel, compute the error
        i, percentage, onepercent = 0, 0, self.dimensions[0] * self.dimensions[1] / (100 * (2 * incr + 1)**2)
        for x in range(incr, self.dimensions[0], 2*incr+1):
            for y in range(incr, self.dimensions[1], 2*incr+1):
                error = colorfun((x, y))
                errors[x, y] = error
                mini = min(mini, error)
                maxi = max(maxi, error)
                i += 1
                if i > onepercent:
                    percentage += 1
                    i = 0
                    print("colorization: %i %%" % percentage)
        print("error min, max: %f, %f" % (mini, maxi))
        # Colorize map with normalized error
        for x in range(incr, self.dimensions[0], 2*incr+1):
            for y in range(incr, self.dimensions[1], 2*incr+1):
                c = errors[x, y]
                if c != 0:
                    v = percentage_to_color(100 * (c - mini) / (maxi - mini))
                    y_ = self.dimensions[1] - y - 1
                    for i in range(-incr, incr + 1):
                        for j in range(-incr, incr + 1):
                            if (0 < x + i < self.dimensions[0]) and (0 < y_ + j < self.dimensions[1]):
                                try:
                                    self.draw.point((x + i, y_ + j), fill=v)
                                except:
                                    print(x, i, y_, j, v)
                                    raise
        return self

    def hot_colorize2(self, colorfun):
        """Colorize the map with the error value (it takes time...)."""
        # error for each pizel will be stored in an array
        errors = np.array([0.0] * (self.dimensions[0] * self.dimensions[1]))
        errors = errors.reshape(self.dimensions[0], self.dimensions[1])
        mini, maxi = 99999999999, 0
        # For each pixel, compute the error
        i, percentage, onepercent = 0, 0, self.dimensions[0] * self.dimensions[1] / 100
        for x in range(0, self.dimensions[0]):
            for y in range(0, self.dimensions[1]):
                error = colorfun((x, y))
                errors[x, y] = error
                mini = min(mini, error)
                maxi = max(maxi, error)
                i += 1
                if i > onepercent:
                    percentage += 1
                    i = 0
                    print("colorization: %i %%" % percentage)
        r = (maxi - mini) / 100
        print("error min, max: %f, %f" % (mini, maxi))
        # Colorize map wiht normalized error
        for x in range(0, self.dimensions[0]):
            for y in range(0, self.dimensions[1]):
                c = errors[x, y]
                if c != 0:
                    v = percentage_to_color(100 * (c - mini) / (maxi - mini))
                    #v = percentage_to_color(r * c)
                    y_ = self.dimensions[1] - y - 1
                    self.draw.point((x, y_), fill=v)
        return self