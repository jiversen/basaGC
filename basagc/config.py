#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
""" This file contains config information common to the whole package """
# This file is part of basaGC (https://github.com/cashelcomputers/basaGC),
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
#  Includes code and images from the Virtual AGC Project
# (http://www.ibiblio.org/apollo/index.html) by Ronald S. Burkey
# <info@sandroid.org>

import os

from collections import OrderedDict

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
print(BASE_DIR)
PROGRAM_NAME = "basaGC"
VERSION = "0.5.5"
LICENCE_FILE = BASE_DIR + "/licence"

IMAGES_DIR = BASE_DIR + "/images/"
IP = "127.0.0.1"
PORT = "8085"
URL = "http://" + IP + ":" + PORT + "/telemachus/datalink?"
DISPLAY_UPDATE_INTERVAL = 100
COMP_ACTY_FLASH_DURATION = 50
LOOP_TIMER_INTERVAL = 50

LOG_LEVELS = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]

current_log_level = "DEBUG"

ID_VERBBUTTON = 10
ID_NOUNBUTTON = 11
ID_PLUSBUTTON = 12
ID_MINUSBUTTON = 13
ID_ZEROBUTTON = 0
ID_ONEBUTTON = 1
ID_TWOBUTTON = 2
ID_THREEBUTTON = 3
ID_FOURBUTTON = 4
ID_FIVEBUTTON = 5
ID_SIXBUTTON = 6
ID_SEVENBUTTON = 7
ID_EIGHTBUTTON = 8
ID_NINEBUTTON = 9
ID_CLRBUTTON = 14
ID_PROBUTTON = 15
ID_KEYRELBUTTON = 16
ID_ENTRBUTTON = 17
ID_RSETBUTTON = 18

DIRECTIONS = [
    "prograde",
    "retrograde",
    "normalplus",
    "normalminus",
    "radialplus",
    "radialminus",
]

KEY_IDS = {
    "10": "V",
    "11": "N",
    "12": "+",
    "13": "-",
    "14": "C",
    "15": "P",
    "16": "K",
    "17": "E",
    "18": "R",
}

TELEMACHUS_BODY_IDS = {
    "Kerbol": "0",
    "Kerbin": "1",
    "Mun": "2",
    "Minmus": "3",
    "Moho": "4",
    "Eve": "5",
    "Duna": "6",
    "Ike": "7",
    "Jool": "8",
    "Laythe": "9",
    "Vall": "10",
    "Bop": "11",
    "Tylo": "12",
    "Gilly": "13",
    "Pol": "14",
    "Dres": "15",
    "Eeloo": "16",
}

ALARM_CODES = OrderedDict({
    110: "Error contacting KSP",
    111: "Telemetry not available",
    115: "No burn data loaded",
    120: "No phase angle data available",
    223: "Invalid target selected",
    224: "Orbit not circular",
    225: "Vessel and target orbits inclination too far apart",
    226: "Time of ignition less than 2 minutes in the future",
    310: "Program hasn't been finished yet, watch this space :)",
    410: "Autopilot error",
})

OCTAL_BODY_IDS = {key: str(int(oct(int(value)))) for key, value in
                  TELEMACHUS_BODY_IDS.iteritems()}  # FIXME: abomination
OCTAL_BODY_NAMES = {value: key for key, value in OCTAL_BODY_IDS.iteritems()}

PROGRAM_DESCRIPTION = "basaGC is a implementation of the Apollo Guidance Computer (AGC) for Kerbal Space Program." + (
                      "\n\nbasaGC includes code and images from the Virtual AGC Project ") + (
                      "(http://www.ibiblio.org/apollo/index.html) by Ronald S. Burkey <info@sandroid.org>")

with open(LICENCE_FILE) as f:
    LICENCE = f.readlines()
LICENCE = "".join(LICENCE)

SHORT_LICENCE = "basaGC is free software; you can redistribute it and/or modify it under the terms of the GNU " + (
                "General Public License as published by the Free Software Foundation; either version 2 of the ") + (
                "License, or (at your option) any later version.\n\nThis program is distributed in the hope that ") + (
                "it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of ") + (
                "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for ") + (
                "more details.\n\nYou should have received a copy of the GNU General Public License along with ") + (
                "this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, ") + (
                "Fifth Floor, Boston, MA 02110-1301, USA.")

COPYRIGHT = "(C) 2014 Tim Buchanan (cashelcomputers@gmail.com)"
WEBSITE = "https://github.com/cashelcomputers/basaGC/"
DEVELOPERS = "Tim Buchanan"
ICON = IMAGES_DIR + "icon.png"




