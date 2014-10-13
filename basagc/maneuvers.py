#!/usr/bin/env python2
# -*- coding: UTF-8 -*-

#  This file is part of basaGC (https://github.com/cashelcomputers/basaGC),
#  copyright 2014 Tim Buchanan, cashelcomputers (at) gmail.com
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
#  Includes code and images from the Virtual AGC Project (http://www.ibiblio.org/apollo/index.html)
#  by Ronald S. Burkey <info@sandroid.org>

import math

from telemachus import get_telemetry
from config import BODIES

def delta_v(departure_altitude, destination_altitude):
    """
    Given a circular orbit at altitude departure_altitude and a target orbit at altitude
    destination_altitude, return the delta-V budget of the two burns required for a Hohmann
    transfer.

    departure_altitude and destination_altitude are in meters above the surface.
    returns a float of the burn delta-v required, positive means prograde, negative means retrograde
    """
    departure_planet_radius = get_telemetry("body_radius", body_number=BODIES["Kerbin"])
    r1 = departure_altitude + departure_planet_radius
    r2 = destination_altitude + departure_planet_radius
    mu = get_telemetry("body_gravitational_parameter", body_number=BODIES["Kerbin"])

    sqrt_r1 = math.sqrt(r1)
    sqrt_r2 = math.sqrt(r2)
    sqrt_2_sum = math.sqrt(2 / (r1 + r2))
    sqrt_mu = math.sqrt(mu)
    dv1 = sqrt_mu / sqrt_r1 * (sqrt_r2 * sqrt_2_sum - 1)
    return dv1


def time_to_transfer(departure_orbit, destination_orbit, grav_param):
    """
    Calculates the time to transfer from one orbit to another,
    :param departure_orbit: departure orbit altitude
    :param destination_orbit: destination orbit altitude
    :param grav_param: orbiting body gravitational parameter
    :return: a float in seconds of the time to transfer
    """
    tH = math.pi * math.sqrt(math.pow(departure_orbit + destination_orbit, 3) / (8 * grav_param))
    return tH

def phase_angle(departure_orbit, destination_orbit, grav_param):

    tH = time_to_transfer(departure_orbit, destination_orbit, grav_param)
    phase_angle = 180 - math.sqrt(grav_param / destination_orbit) * (tH / destination_orbit ) * 180 / math.pi
    return phase_angle