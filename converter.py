#!/usr/bin/env python

"""
Converter class to ensure a consistent conversion between lat&lng and UTM.
It ensures the same UTM zone is used.
"""

import utm

class Converter:

    def __init__(self, init_latlng):
        _, _, self.zone_number, self.zone_letter = utm.from_latlon(
            *init_latlng
        )

    def from_latlng(self, lat, lng):
        return utm.from_latlon(lat, lng, self.zone_number, self.zone_letter)[:2]

    def to_latlng(self, easting, northing, strict=True):
        return utm.to_latlon(
            easting, northing, self.zone_number, self.zone_letter, strict=strict
        )
