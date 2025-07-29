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

#: Demonstrates the use of custom color transformations
"""
This script demonstrates the `AddCustomColorTransformation()`
function for transforming pixel intensities and colors in
ways that are more complicated or more subtle than the
standard channel-by-channel gamma or sRGB functions.

The mechanism for defining custom color transformations is
similar to the mechanism for adding custom signal, modulation
or windowing functions (see the `custom-functions` demo).

This demo requires third-party packages `numpy` and `pillow`.
"""#.
if __name__ == '__main__':

	import Shady

	"""
	Parse command-line options:
	"""#:
	cmdline = Shady.WorldConstructorCommandLine()
	cmdline.Help().Finalize()
	Shady.Require( 'numpy', 'Image/PIL.Image:PIL/pillow' ) # die with an informative error if these are missing

	"""
	Define the new color transformation with a snippet
	of GLSL code.  The GLSL function should take in, and
	return, a 4-dimension vector of RGBA values. It can
	be named however you like: the name you use will
	appear, associated with the numeric value assigned
	to this new function, in the `Shady.COLORTRANS`
	namespace.
	
	In common with the definition of novel custom signal,
	modulation and windowing functions (see the
	`custom-functions` demo), this must be done *before*
	the World is created.
	
	The following minimal example simply inverts all
	channels except the alpha, so we will call it
	`PhotoNegative`:
	"""#:
	Shady.AddCustomColorTransformation( """
	
		vec4 PhotoNegative( vec4 color )
		{
			color.rgb = 1.0 - color.rgb;
			return color;
		}
		
	""" )
	
	"""
	More complex transformations can be programmed by
	addressing `color.r`, `color.g` and `color.b`
	separately, or by applying matrix transformations
	to `color.rgb`.  Here are some very simple examples
	that just reorder the color channels:
	"""#:
	Shady.AddCustomColorTransformation("vec4 RGB(vec4 color){ return color.rgba; }")
	Shady.AddCustomColorTransformation("vec4 RBG(vec4 color){ return color.rbga; }")
	Shady.AddCustomColorTransformation("vec4 BGR(vec4 color){ return color.bgra; }")
	Shady.AddCustomColorTransformation("vec4 BRG(vec4 color){ return color.brga; }")
	Shady.AddCustomColorTransformation("vec4 GBR(vec4 color){ return color.gbra; }")
	Shady.AddCustomColorTransformation("vec4 GRB(vec4 color){ return color.grba; }")
	
	"""
	Create a `World`, along with a colored `Stimulus`:
	"""#:
	world = Shady.World( **cmdline.opts )
	alien = world.Stimulus(
		Shady.PackagePath( 'examples/media/alien1.gif' ),
		frame = Shady.Integral( 16 ),
	)
	
	"""
	Apply the new color transformation by setting the
	appropriate property of the Stimulus:
	"""#:
	alien.colorTransformation = Shady.COLORTRANS.PhotoNegative
	
	"""
	Revert to the default value (0, aka
	`NoTransformation`):
	"""#:
	alien.colorTransformation = Shady.COLORTRANS.NoTransformation
	
	"""
	Note that this transformation is independent of
	our usual `.gamma` linearization. If desired, the
	`.gamma` linearization can be still be applied:
	"""#:
	alien.gamma = Shady.Oscillator( 0.25 ) * 1.8 + 2.0
	
	"""
	...and that will also affect the negative-mode
	colors, because the gamma linearization, if any,
	gets applied *after* the custom transformation:
	"""#:
	alien.colorTransformation = Shady.COLORTRANS.GBR
	
	""#>
	Shady.AutoFinish( world )
