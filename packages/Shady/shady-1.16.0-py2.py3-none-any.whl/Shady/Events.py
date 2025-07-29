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
__all__ = [
	'GenericEvent',
]

import re
import sys
if sys.version < '3': bytes = str
else: unicode = str; basestring = ( unicode, bytes )

def SetDefaults( cls ):
	order = cls._fieldOrder.split()
	d = cls._fieldOrder = {}
	for i, fieldName in enumerate( order ):
		setattr( cls, fieldName, None )
		d[ fieldName ] = i
	return cls
	
@SetDefaults
class GenericEvent( object ):
	
	_fieldOrder = 'type key text button modifiers x y dx dy t'
	
	translations = {
		'enter'    : 'return',
		'space'    : ' ',
		
		'command'  : 'super',     # pyglet on macOS
		'lcommand' : 'lsuper', 
		'rcommand' : 'rsuper', 
		
		'windows'  : 'super',     # pyglet on Windows
		'lwindows' : 'lsuper', 
		'rwindows' : 'rsuper', 
		
		'meta'     : 'super',     # pygame
		'lmeta'    : 'lsuper', 
		'rmeta'    : 'rsuper', 
		
		-1         : 'function',  # needed by ShaDyLibWindowing
	}
	
	def Standardize( self ):		
		self.key = self.translations.get( self.key, self.key )
		self.text = self.translations.get( self.text, self.text )
		self.modifiers = ' '.join( self.translations.get( mod, mod ) for mod in self.modifiers.split() if mod not in ( 'accel', 'option' ) )
		self.abbrev = ''.join( word[ 0 ] for word in self.type.replace( '_unknown', '_?' ).split( '_' ) )
		if   self.abbrev in ( 'kp', 'ka', 'kr', ): self.abbrev += '[' + self.key    + ']'
		elif self.abbrev in ( 't', ):              self.abbrev += '[' + self.text   + ']'
		elif self.abbrev in ( 'mp', 'mr', ):       self.abbrev += '[' + self.button + ']'
		
	def _sortKey( self, item ): k, v = item; return ( self._fieldOrder.get( k, 100 ), k )
	def __repr__( self ): return 'Event(' + ', '.join( [ '%s=%s' % ( k, nice_repr( v ) ) for k, v in sorted( self.__dict__.items(), key=self._sortKey ) ] ) + ')'
	def __rshift__( self, candidates ):
		#return self.abbrev in candidates   # the old way - didn't allow optional encoding of modifiers in candidates
		return EventPattern( candidates ).Matches( self )
	__eq__ = __rshift__

def nice_repr( x ):
	if isinstance( x, float ):
		return '%.3f' % x
	if isinstance( x, str ):
		if unicode is not str: return repr( x )
		encdec = x.encode( 'unicode_escape' ).decode( 'ascii' )
		if encdec == x: return repr( x )
		return "'" + encdec + "'" # this is hacky because quotes and backslashes are unescaped, but in the cases that matters we're only ever dealing with single characters --- quotes and backslashes themselves won't have this problem and will be caught by the previous line
	return repr( x )

class EventPattern( object ):
	pattern = re.compile( r"""
		\s*
		(?P<modifiers_>   ((none|shift|ctrl|alt|super)\+)*     )
		(?P<code>         [^\[\]\s\+]+                         )
		(?P<modifiers>    (\+(none|shift|ctrl|alt|super))*     )
		(?P<argument>     (\[.[^\]]*\]){0,1}                   )
		(\s+|$)
	""", re.VERBOSE | re.IGNORECASE )
	def __init__( self, candidates ):
		self.candidates = []
		self.residue = ''
		if isinstance( candidates, EventPattern ):
			other = candidates
			self.candidates[ : ] = other.candidates
			self.residue = other.residue
		else:
			if not isinstance( candidates, str ): candidates = '\v'.join( candidates )
			self.residue = re.sub( self.pattern, self._ProcessMatch, candidates )
	def _ProcessMatch( self, match ):
		d = match.groupdict()
		d[ 'abbrev' ] = d[ 'code' ].lower() + d[ 'argument' ]
		if d[ 'modifiers' ]:  d[ 'modifiers' ] = sorted( d[ 'modifiers' ].lower().strip( '+' ).split( '+' ) )
		else: d[ 'modifiers' ] = []
		if d[ 'modifiers_' ]: d[ 'modifiers' ] += sorted( d[ 'modifiers_' ].lower().strip( '+' ).split( '+' ) )
		self.candidates.append( d )
		return ''
	def Matches( self, event ):
		event_mods = None
		event_abbrev = event.abbrev
		for candidate in self.candidates:
			if event_abbrev == candidate[ 'abbrev' ]:
				candidate_mods = candidate[ 'modifiers' ]
				if not candidate_mods: return True
				if event_mods is None:
					event_mods = sorted( event.modifiers.split() )
					if not event_mods: event_mods = [ 'none' ]
				if event_mods == candidate_mods: return True
		return False
	def __repr__( self ):
		return 'candidates = [\n%s\n]' % '\n'.join( '    %r' % m for m in self.candidates ) + ( '\nresidue = %r' % self.residue ) if self.residue else ''
