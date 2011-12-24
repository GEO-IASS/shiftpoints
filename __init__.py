# -*- coding: utf-8 -*-

mVersion = "0.0.2"

#******************************************************************************
#
# GenPoints
# ---------------------------------------------------------
# Generate regular points inside polygon
#
# Copyright (C) 2011 Alexander Bruy (alexander.bruy@gmail.com)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/copyleft/gpl.html>. You can also obtain it by writing
# to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.
#
#******************************************************************************

def name():
	return "Point displacement"

def description():
	return "Point displacement plugin"

def category():
	return "Vector"

def version():
	return mVersion

def qgisMinimumVersion():
	return "1.0"

def authorName():
	return "Alexander Bruy"

def icon():
	return "displacement.png"

def classFactory( iface ):
	from displacement import DisplacementPlugin
	return DisplacementPlugin( iface )

