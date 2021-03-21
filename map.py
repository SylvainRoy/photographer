#/usr/bin/env python

"""
The class Map contains all basic drawing action on a Map.
"""

import numpy as np
import utm
from matplotlib.pyplot import imshow
from PIL import Image as PILImage
from PIL import ImageDraw

from tools import project_on_lens


def percentage_to_color(i):
    """Return a color that goes from white to blue based on a percentage."""
    try:
        i = int(i)
    except:
        i = 0
    return (255 - 255 * i // 100, 255 - 255 * i // 100, 255, 255)


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
        self.error_matrixes = {}
        self.alphax = None
        self.alphay = None
        self.Xo = None
        self.Yo = None
        self.zone_number = None
        self.zone_letter = None

    def copy(self):
        """Return a deep copy of the map"""
        m = Map(self.dimensions)
        m.map = self.map.copy()
        m.draw = ImageDraw.Draw(m.map)
        m.error_matrixes = self.error_matrixes
        m.alphax = self.alphax
        m.alphay = self.alphay
        m.Xo = self.Xo
        m.Yo = self.Yo
        m.zone_number = self.zone_number
        m.zone_letter = self.zone_letter
        return m

    def set_latlng(self, xy1, latlng1, xy2, latlng2):
        """
        Return two functions to change the coordinate system of a point.
        Input: a list of at least two points in the two coordinate system (only the first and last point are used).
        """
        easting1, northing1, zone_number1, zone_letter1 = utm.from_latlon(*latlng1)
        easting2, northing2, zone_number2, zone_letter2 = utm.from_latlon(*latlng2)
        if (zone_number1 != zone_number2) or (zone_letter1 != zone_letter2):
            raise RuntimeError("The map is on two utm zones.")
        utm1 = (easting1, northing1)
        utm2 = (easting2, northing2)
        self.alphax = (xy2[0] - xy1[0]) / (utm2[0] - utm1[0])
        self.alphay = (xy2[1] - xy1[1]) / (utm2[1] - utm1[1])
        self.Xo = utm1[0] - xy1[0] / self.alphax
        self.Yo = utm1[1] - xy1[1] / self.alphay
        self.zone_number = zone_number1
        self.zone_letter = zone_letter1
        return self

    def latlng_to_xy(self, latlng):
        """Convert coordinate in (lat,lng) to (x,y) on the map."""
        if self.alphax is None:
            raise RuntimeError("Attempt to convert lat,lng to x,y without prior call to 'set_latlng'.")
        easting, northing, zone_number, zone_letter = utm.from_latlon(*latlng)
        if (zone_number != self.zone_number) or (zone_letter != self.zone_letter):
            raise RuntimeError("The point is not on the same utm zone than the map.")
        x = (easting - self.Xo) * self.alphax
        y = (northing - self.Yo) * self.alphay
        return (x, y)

    def xy_to_latlng(self, xy):
        """Convert coordinate in (x,y) on the map to (lat, lng)."""
        if self.alphax is None:
            raise RuntimeError("Attempt to convert x,y to lat,lng without prior call to 'set_latlng'.")
        easting = xy[0] / self.alphax + self.Xo
        northing = xy[1] / self.alphay + self.Yo
        lat, lng = utm.to_latlon(easting, northing, self.zone_number, self.zone_letter)
        return (lat, lng)

    def show(self, notebook=True):
        """Display the map"""
        if notebook:
            imshow(np.asarray(self.map))
        else:
            self.map.show()
        return self

    def save(self, filename):
        """Save map in a jpg file"""
        self.map.save(filename)
        return self

    def draw_pixel(self, point, color=0):
        """Draw a pixel on the map."""
        (x, y) = point
        y_ = self.dimensions[1] - y
        self.draw.point((x, y_), fill=color)
        return self

    def draw_point(self, point, name="", color=0, latlng=False):
        """Draw a point on the map"""
        if latlng:
            (x, y) = self.latlng_to_xy(point)
        else:
            (x, y) = point
        y = self.dimensions[1] - y
        d = int(min(self.dimensions) / 100)
        self.draw.line((x - d, y, x + d, y), fill=color, width=1)
        self.draw.line((x, y - d, x, y + d), fill=color, width=1)
        self.draw.text((x + d, y + d), name, fill=color)
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
        self.error_matrixes = {}
        return self

    def compute_color_matrix(self, colorfun, incr=0):
        """
        Compute, save and return the error matrix for colorfun.
        """
        # First try to retrieve data from cache
        if (colorfun in self.error_matrixes) and (incr in self.error_matrixes[colorfun]):
            return  self.error_matrixes[colorfun][incr]
        # For each group of pixels, compute the error, min and max
        matrix = np.zeros(self.dimensions)
        error_min, error_max = 99999999999, 0
        percentage, cur = 0, 0
        total = len(range(incr, self.dimensions[0], 2*incr+1)) * len(range(incr, self.dimensions[1], 2*incr+1))
        for x in range(incr, self.dimensions[0], 2*incr+1):
            for y in range(incr, self.dimensions[1], 2*incr+1):
                error = colorfun((x, y))
                for i in range(-incr, incr + 1):
                    for j in range(-incr, incr + 1):
                        if x + i < self.dimensions[0] and y + j < self.dimensions[1]:
                            matrix[x + i, y + j] = error
                error_min = min(error_min, error)
                error_max = max(error_max, error)
                cur += 1
                if 100 * cur / total > percentage:
                    percentage += 1
                    print(f"{percentage}% ", end="")
        print("\nerror min, max: %f, %f" % (error_min, error_max))
        # Save data in cache
        self.error_matrixes.setdefault(colorfun, {})[incr] = (matrix, error_min, error_max)
        return  self.error_matrixes[colorfun][incr]

    def hot_colorize(self, colorfun, transfun=lambda x: x, incr=0):
        """
        Colorize the map with the error value.
        incr is an unsigned int. The bigger, the faster and the less accurate.
        incr = 0 means every pixel is computed.
        """
        (error_matrix, error_min, error_max) = self.compute_color_matrix(colorfun, incr)
        # Colorize map with normalized error
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                err = error_matrix[x, y]
                percentage = 100 * (err - error_min) / (error_max - error_min)
                percentage = max(0, min(100, transfun(percentage)))
                color = percentage_to_color(percentage)
                self.draw_pixel((x, y), color=color)
        return self
