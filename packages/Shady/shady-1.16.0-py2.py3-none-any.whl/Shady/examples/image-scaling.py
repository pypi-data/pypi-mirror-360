#!/usr/bin/env python
# $BEGIN_SHADY_LICENSE$
# 
# This file is part of the Shady project, a Python framework for
# real-time manipulation of psychophysical stimuli for vision science.
# 
# Copyright (c) 2017-2025 Jeremy Hill, Scott Mooney
# 
# Shady is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/ .
# 
# $END_SHADY_LICENSE$

#: Demonstrates interpolated and non-interpolated image scaling
"""
This demo displays two well-known images whose interpretation
depends on their scaling, and allows you to manipulate scaling
using the `-` and `+` keys.

This demo requires the third-party package `numpy`.
"""#.
if __name__ == '__main__':

	"""
	First deal with the demo's command-line arguments,
	if any:
	"""#:
	import Shady
	cmdline = Shady.WorldConstructorCommandLine()
	cmdline.Help().Finalize()
	Shady.Require( 'numpy' ) # die with an informative error if this is missing
	
	"""
	Create a World:
	"""#:
	w = Shady.World( **cmdline.opts )

	"""
	Here's a familiar pixellated stimulus:
	"""#:
	maxScale = int( min( w.size / [ 28, 18 ] ) )
	s = w.Stimulus( [
		[ 218, 231, 224, 176,  79,  36,  53,  43,  33,  67, 241, 223, 231, 220 ],
		[ 221, 238, 194,  77,  56, 160, 106,  68,  29,  41,  97, 206, 240, 226 ],
		[ 231, 234,  82,  64, 120, 229, 208, 222, 105,  46,  35, 191, 231, 231 ],
		[ 224, 223,  70,  83, 147, 157, 211, 206, 199,  92, 107, 136, 191, 235 ],
		[ 227, 163,  52,  86, 143, 176, 177, 182, 177, 200, 120,  81, 152, 228 ],
		[ 223,  66, 108,  57,  88, 132,  46,  57, 103,  64,  46,  75, 166, 233 ],
		[ 224, 113, 154,  70,  83,  83,  80,  83, 126,  73,  70, 201, 229, 232 ],
		[ 224, 138, 196, 154,  91, 173, 180, 192, 206, 126,  86, 216, 220, 231 ],
		[ 220, 230, 100, 117,  40,  93, 175, 140, 102,  77, 100, 221, 222, 226 ],
		[ 204, 219, 153,  52,  46,  90, 102, 132, 127,  69, 129, 216, 217, 221 ],
		[ 200, 220, 197,  91,  41, 104, 150, 142,  96,  54, 154, 227, 220, 219 ],
		[ 157, 179, 150,  97,  52,  52,  52,  71,  85,  53, 115, 223, 226, 228 ],
		[ 153, 130, 137,  38, 207,  44,  32,  11,  16,  64, 228, 229, 244, 235 ],
		[ 150, 111,  51,  13,  94, 221,  92, 104, 159, 124, 192, 228, 226, 223 ],
		[  72,  52,  57,  54,  41,  39,  22,  35,  77,  71,  69, 205, 223, 226 ],
		[  71,  52,  71,  57,  37,  40,  41, 110,  65,  51,  48,  46,  82, 201 ],
		[  52,  68,  44,  49,  43,  40,  65, 116, 112, 109, 101,  65,  43, 147 ],
		[  83,  29,  25,  18,  52,  42,  38,  75, 228, 237, 225, 156,  39, 218 ],
	],
		linearMagnification = False,
		scale = maxScale,
		pos = w.Place( -1, 0 ),
		anchor=( -1, 0 ),
	)

	"""
	Here's another familiar image:
	"""#:
	s2 = w.Stimulus(
		Shady.EXAMPLE_MEDIA.EinsteinMonroe,
		pos = w.Place( +1, 0 ),
		anchor = ( +1, 0 ),
	)
	
	"""
	The following dynamic property assignment will ensure
	the two images are always scaled to the same height.
	(We cannot use the more-efficient mechanism of property
	sharing here, since `.scaledHeight` is not a fully-
	fledged `ManagedProperty`, but the dynamic will do
	fine.) Since the default value of `.scaledAspectRatio`
	is `'fixed'`, the `.scaledWidth` property will be
	automatically adjusted to preserve aspect ratio.
	"""#:
	s2.scaledHeight = lambda t: s.scaledHeight
	
	"""
	Finally we'll install an event handler for manipulating
	the images via the keyboard:
	"""#:
	@w.EventHandler( slot=-1 )
	def eh( self, event ):
		if event >> "kp[i]":
			s.linearMagnification = not s.linearMagnification
		if event >> "kp[+] ka[+] kp[=] ka[=]":
			s.scale = min( maxScale, round( min( s.scale ) ) + 1 )
		if event >> "kp[-] ka[-]":
			s.scale = max( 1, round( min( s.scale ) ) - 1 )
	
	""#>
	print( """
Press  - / +  to adjust image scaling
Press    I    to toggle linear interpolation on/off in the left image
""")
	Shady.AutoFinish( w )  # tidy up, in case we didn't get here via `python -m Shady`
