/*
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
*/

// Simpler (though less well-behaved) fallback algorithm for GLSL versions < 3.3

// The basic 2D-seeded algorithm is of uncertain origin but was found at https://stackoverflow.com/a/4275343/
float random( vec2 co )
{
	float r;
	const vec2  COEFFICIENTS = vec2( 12.9898, 78.233 );    // original magic values: 12.9898, 78.233;
	const float LARGE_FLOAT  = 54000.0;                    // original magic value: 43758.5453;
	
	r = fract( sin( dot( co, COEFFICIENTS ) ) * LARGE_FLOAT );
	
	// jez added this section because very small values are over-represented, for some reason
	const float lowerLimit = 1e-6;  // originally 1e-5
	const float upperLimit = 1.0 - lowerLimit;
	if( r < lowerLimit || r > upperLimit )
	{
		r = fract( sin( dot( co.yx, COEFFICIENTS ) ) * LARGE_FLOAT ); // so give it another try with the seeds swapped
		r = max( lowerLimit, min( upperLimit, r ) ); // then if all else fails, clip the output
	}
	
	// scale to desired output range [-1, +1)
	return 2.0 * ( r - 0.5 );
}

// It's tricky to add a third seed. You can stab around for a third coefficient but very often it will lead to
// visible structure on certain frames.  This is the best I've done so far at subjectively minimizing such effects:
float random( vec3 co )
{		
	float r;
	const vec3  COEFFICIENTS = vec3( 12.9898, 78.233, 1.895 );   // original magic values: 12.9898, 78.233;
	const float LARGE_FLOAT  = 54000.0;                          // original magic value: 43758.5453;
	
	r = fract( sin( dot( co, COEFFICIENTS ) ) * LARGE_FLOAT );
	
	// jez added this section because very small values are over-represented, for some reason
	const float lowerLimit = 1e-6;  // originally 1e-5
	const float upperLimit = 1.0 - lowerLimit;
	if( r < lowerLimit || r > upperLimit )
	{
		r = fract( sin( dot( co.zyx, COEFFICIENTS ) ) * LARGE_FLOAT ); // so give it another try with the seeds swapped
		r = max( lowerLimit, min( upperLimit, r ) ); // then if all else fails, clip the output
	}
	
	// scale to desired output range [-1, +1)
	return 2.0 * ( r - 0.5 );
}
