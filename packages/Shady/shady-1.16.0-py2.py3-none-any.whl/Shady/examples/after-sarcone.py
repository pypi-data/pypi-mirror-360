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

#: Dynamic Müller-Lyer illusion adapted from artwork by Gianni Sarcone
"""
This dynamic demo of the Müller-Lyer illusion was adapted from a visual
concept by Gianni A. Sarcone, as expressed in 
https://en.wikipedia.org/wiki/M%C3%BCller-Lyer_illusion#/media/File:Sarcone%E2%80%99s_Pulsating_Star_(Dynamic_M%C3%BCller-Lyer_illusion).gif
The original was released under CC BY-SA-4.0 (correspondence with the
artist under Wikipedia ticket #2021121610010745).
"""#.

import math, cmath

import Shady
Shady.RequireShadyVersion( '1.15.0' ) # needs the fixed .Place() method that finally took account of rotation in 1.14.3, and the ability to make custom (non-accelerated) ManagedProperty instances in 1.15.0

if __name__ == '__main__':
		
	"""
	Parse command-line options that affect `World` construction:
	"""#:
	cmdline = Shady.WorldConstructorCommandLine( fullScreenMode=False, clearColor=0 )
	cmdline.Help().Finalize()
	
	"""
	Create a `World`, spanned by an invisible circle that will act
	as the base for the stimuli:
	"""#:
	w = Shady.World( **cmdline.opts )
	circle = w.Patch( name='circle', size=min( w.size ), pp=1, color=w.clearColor, z=0.2 )
			
	"""
	Create a custom class that defines a single Müller-Lyer arrow.
	"""#:

	from Shady.Utilities import RADIANS_PER_DEGREE
	from Shady.PropertyManagement import ClassWithManagedProperties, ManagedProperty, ManagedShortcut

	@ClassWithManagedProperties._Organize
	class Arrow( Shady.Stimulus ):
	
		# Custom ManagedProperties (dynamic and shareable, but not
		# transferred to the shader):
		frequencyInHz__  = freq  = ManagedProperty(
			default=0.0,  doc="Fin-flapping frequency in Hz",
			accelerate=False, # suppress "the failed to accelerate" warning
		)
		phaseInDegrees__ = phase = ManagedProperty(
			default=90.0, doc="Fin-flapping phase in degrees",
			accelerate=False, # suppress "the failed to accelerate" warning
		)
		
		def __init__( self, world, frequencyInHz=None, phaseInDegrees=None, **kwargs ):
			kwargs.setdefault( 'envelopeSize',    kwargs.pop( 'size',    [ 101, 5 ]  ) )
			kwargs.setdefault( 'backgroundAlpha', kwargs.pop( 'bgalpha', 0.0         ) )
			kwargs.setdefault( 'color',           kwargs.pop( 'fgcolor', [ 1, 0 ,0 ] ) )
			visible = kwargs.pop( 'visible', True )
			finProps = { k : kwargs.pop( k ) for k in list( kwargs ) if k.startswith( 'fin_' ) }
			Shady.Stimulus.__init__( self, world, visible=False, **kwargs )
			if frequencyInHz is not None: self.frequencyInHz = frequencyInHz
			if phaseInDegrees is not None: self.phaseInDegrees = phaseInDegrees
			Flap = lambda t: math.sin(
				self.phaseInDegrees * RADIANS_PER_DEGREE
				+ 2.0 * math.pi * self.frequencyInHz * t
			)
			if self.defaultFin is None:
				self.defaultFin = world.Patch(
					visible=False, z=+0.1,
					envelopeSize=[ 30, 2 ], color=0.5,
				)
			f = self.defaultFin
			finConstruction = dict( visible = False, size=f, color=f, z=f, pp=f, scaling=self )
			self.fin1  = world.Patch(
				anchor = [ -1, 0 ],
				position = lambda t: self.Set( anchor_y=0 ).Place( -1, 0 ),
				rotation = lambda t: self.rotation + 90 + Flap( t ) * 45,
				**finConstruction
			 )
			self.fin2 = world.Patch(
				anchor = self.fin1,
				position = self.fin1,
				rotation = lambda t: self.rotation - 90 - Flap( t ) * 45,
				**finConstruction
			)
			self.fin3 = world.Patch( 
				anchor = [ +1, 0 ],
				position = lambda t: self.Set( anchor_y=0 ).Place( +1, 0 ),
				rotation = self.fin2,
				**finConstruction
			)
			self.fin4 = world.Patch(
				anchor = self.fin3,
				position = self.fin3,
				rotation = self.fin1,
				**finConstruction
			)
			self.Set( **finProps )
			for obj in [ self, self.fin1, self.fin2, self.fin3, self.fin4 ]: obj.visible = True
		
		def Set( self, **props ):
			finProps = { k[ 4: ] : props.pop( k ) for k in list( props ) if k.startswith( 'fin_' ) }
			if getattr( self, 'fin', None ): self.fin1.Set( **finProps )
			return Shady.Stimulus.Set( self, **props )
		
		__defaultFin = [ None ]
		@property
		def defaultFin( self ): return self.__defaultFin[ 0 ]
		@defaultFin.setter
		def defaultFin( self, obj ): self.__defaultFin[ : ] = [ obj ]
	
	"""
	Create a subclass that includes a counterpart arrow
	with every arrow:
	"""#:

	@ClassWithManagedProperties._Organize
	class ArrowPair( Arrow ):
		def __init__( self, world, **kwargs ):
			redArgs  = dict( kwargs )
			blueArgs = dict( kwargs )
			redArgs.setdefault(  'color', [ 1, 0, 0 ] )
			blueArgs.setdefault( 'color', [ 0, 0, 1 ] )
			blueArgs[ 'anchor' ] = -1 * redArgs.setdefault( 'anchor', -1 )
			redArgs.setdefault( 'phaseInDegrees', redArgs.pop( 'phase', -90 ) )
			blueArgs[ 'phaseInDegrees' ] = 180 + redArgs[ 'phaseInDegrees' ]
			Arrow.__init__( self, world, **redArgs )
			self.counterpart = Arrow( world, **blueArgs )
			self.counterpart.fin3.Leave()
			self.counterpart.fin4.Leave()
			self.ShareProperties( 'position rotation scaling pp', self.counterpart )
			
	"""
	Create the arrow pairs:
	"""#:
	radius = 0.5
	skew = 0.0
	pairs = [
		ArrowPair( w,
			rotation = lambda t, theta=theta: circle.rotation + theta - skew,
			position = lambda t, theta=theta: circle.Place( theta, radius, polar=True ),
			scaling = circle,
			pp = 0.8,
			fin_pp = 1.0,
		) for theta in range( 0, 360, 30 )
	]
	counterparts = [ pair.counterpart for pair in pairs ]
	outer, inner = pairs[ 0 ], counterparts[ 0 ]
	outer.ShareProperties( pairs + counterparts, 'freq size pp' )
	outer.ShareProperties( pairs, 'color phase' )
	inner.ShareProperties( counterparts, 'color phase' )
	fin = outer.defaultFin
	
	"""
	Flap the flaps:
	"""#:
	outer.freq = 0.2

	"""
	Spin the wheel:
	"""#:
	circle.rotation = Shady.Integral( 10 ) # degrees per second
	
	"""
	"""#>
	print( "The red lines are the same constant length as the blue lines." )
	Shady.AutoFinish( w )
