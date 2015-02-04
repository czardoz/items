#!/usr/bin/env python
#
# Items - Mongo Project
#
# Copyright (C) 2015 Aniket Panse <aniketpanse@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import collections

EARTH_RADIUS = 6371  # km


class GeoLocation(object):

    def __init__(self, lat, long_):
        self.latitude = float(lat)
        self.longitude = float(long_)  # "long" is a defined class in python, so do not use it as a variable name.


def calculate_distance(location_one, location_two):
    """ Implementation of the Haversine formula
    """

    conversion_factor = math.pi/180.0
    phi1 = (90.0 - location_one.latitude) * conversion_factor
    phi2 = (90.0 - location_two.latitude) * conversion_factor
    theta1 = location_one.longitude * conversion_factor
    theta2 = location_two.longitude * conversion_factor
    cos = (
        math.sin(phi1) * math.sin(phi2) * math.cos(theta1 - theta2) + math.cos(phi1) * math.cos(phi2)
    )
    arc = math.acos(cos)
    return arc * EARTH_RADIUS


def calculate_distance_lightweight(location_one, location_two):
    """ Approximation, refer to:
    https://sites.google.com/a/cs.usfca.edu/cs-107-03-2012-spring/tutorials/distancecalculator
    """

    horizontal_distance = 69.1 * (location_two.latitude - location_one.latitude)
    vertical_distance = 69.1 * (location_two.longitude - location_one.longitude) * \
        math.cos(location_one.latitude/57.3)
    net_distance = math.sqrt(horizontal_distance**2 + vertical_distance**2)
    return net_distance


def nested_update(orig, new_values):
    for key, value in new_values.iteritems():
        if isinstance(value, collections.Mapping):
            r = nested_update(orig.get(key, {}), value)
            orig[key] = r
        else:
            orig[key] = new_values[key]
    return orig