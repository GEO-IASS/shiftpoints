# -*- coding: utf-8 -*-

#******************************************************************************
#
# ShiftPoints
# ---------------------------------------------------------
# Moves overlapped points with same coordinates in a circle around the
# original position.
#
# Copyright (C) 2011-2013 Alexander Bruy (alexander.bruy@gmail.com)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#******************************************************************************

def name():
  return "Shift Points"

def description():
  return "Moves overlapped points in a circle around original position"

def category():
  return "Vector"

def version():
  return "0.2.2"

def qgisMinimumVersion():
  return "1.0.0"

def author():
  return "Alexander Bruy"

def email():
  return "alexander.bruy@gmail.com"

def icon():
  return "icons/shiftpoints.png"

def classFactory(iface):
  from shiftpoints import ShiftPointsPlugin
  return ShiftPointsPlugin(iface)
