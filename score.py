#!/usr/bin/env python

"""
Compute a score for all the examples in data that comes with a known location of the photographer.
"""

import json
from pathlib import Path

import utm

from map import Map
from tools import distance
from optimizer import find_photographer_wsg84


def score(display=False):
    """
    Run all example, display result and compute a globla score.
    """

    num = 0
    total_distance = 0
    
    if display:
        print("-- Cases --")

    # For each example that comes with all needed data
    data = Path("data")
    for example in data.iterdir():

        infojson = example.joinpath('info.json')
        if not infojson.exists():
            continue

        try:

            with infojson.open() as infofile:
                info = json.load(infofile)

                if 'photographer_latlng' not in info:
                    continue

                if display:
                    print(" - ", example.name, end=": ")
                    
                # retrieve real photographer location
                real_latlng = info['photographer_latlng']
                real_easting, real_northing, zone_number, zone_letter = utm.from_latlon(*real_latlng)

                # compute photographer location
                computed_latlng = find_photographer_wsg84(
                    info['latlngs'],
                    [i[0] for i in info['projections']]
                ).photographer
                computed_easting, computed_northing, _, _ = utm.from_latlon(
                    *computed_latlng,
                    force_zone_letter=zone_letter,
                    force_zone_number=zone_number
                )

                delta = int(distance((real_easting, real_northing), (computed_easting, computed_northing)))
                if display:
                    print(delta, "meters")

                num += 1
                total_distance += delta

        except RuntimeError as e:
            if display:
                print(e)
            else:
                raise

    score = int(total_distance / num)

    print("-- Summary --")
    print(num, "cases")
    print("Average error:", score, "meters")


if __name__ == '__main__':
    score(display=True)

