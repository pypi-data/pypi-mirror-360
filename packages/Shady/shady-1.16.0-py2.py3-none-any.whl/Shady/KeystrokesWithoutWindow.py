"""
The main purpose of this is to provide a way of controlling demos from the keyboard
even when they're in `overlayMode` when the window does not create keyboard or mouse
events.

It requires the third-party package `pynput`.

TODO: It would be nice to invoke this automatically in Shady.Utilities.AutoFinish()
      if we're in overlay mode (provided pynput is available of course - just print a
      message if not). Note that it is currently unclear how we query whether we're in
      overlay mode. Note also: because pynput will deliver events regardless of which
      window is focussed, we should make sure this *only* gets used in overlay mode
      (otherwise the window will *also* deliver keyboard events).
"""
import sys
import time
import weakref

from Shady import DependencyManagement, Rendering, Events  # TODO: remove and replace with relative import below if integrating this into the Shady module
#from .    import DependencyManagement, Rendering, Events

#DependencyManagement.Require( 'pynput.keyboard:pynput' )
keyboard = DependencyManagement.Import( 'pynput.keyboard', packageName='pynput' )
# NB: there's a `pynput.mouse` submodule too

class KeyEvent( Events.GenericEvent ):
	def __init__( self, type, key='', modifiers='', text=None ):
		self.type = type
		self.key = key
		self.modifiers = modifiers
		self.text = text
		self.Standardize()

class KeyListener( object ):
	def __init__( self, world ):
		self.world = weakref.ref( world )
		self.modifiers = set()
		if keyboard:
			self.listener = keyboard.Listener( on_press=self.OnPress, on_release=self.OnRelease )
			world.OnClose( self.Stop )
		else:
			self.listener = None
			print( 'WARNING: cannot listen for keystrokes because %s' % keyboard )

	def Start( self, prompt='Listening for keystrokes...', threaded=False ):
		"""
		Alternatively you can just say `with KeyListener(world): ...`
		if you want to run asynchronously.
		"""
		if self.listener is None: return
		if prompt: print( prompt )
		if threaded:
			if not self.listener.is_alive(): self.listener.start()
			return
		with self: self.Join()

	def Stop( self ):
		if not self.listener: return
		try: self.listener.stop()
		except: pass
		else: self.FlushKeys()
	
	def Join( self ):
		if self.listener:
			self.listener.join()
			self.FlushKeys()
	
	def FlushKeys( self ):
		if sys.platform.lower().startswith( 'win' ):
			import msvcrt
			while msvcrt.kbhit(): msvcrt.getch()
		else:
			import termios
			termios.tcflush(sys.stdin, termios.TCIFLUSH)  # Flush input buffer
			
	def __enter__( self ):
		if self.listener is not None: self.listener.__enter__()
		return self
		
	def __exit__( self, *blx ):
		if self.listener is not None:
			self.FlushKeys()
			return self.listener.__exit__( *blx )
	
	def OnPress( self, key ):
		self.Handle( 'key_press',   key.name if isinstance( key, keyboard.Key ) else key.char if key.char else '' )		

	def OnRelease( self, key ):
		self.Handle( 'key_release', key.name if isinstance( key, keyboard.Key ) else key.char if key.char else '' )		
		if key == keyboard.Key.esc: return False # Stop listener on ESC key release
		
	def Handle( self, eventType, key ):
		world = self.world()
		if not key: return
		translations = dict(
			esc='escape',
			shift='lshift', shift_l='lshift', shift_r='rshift',
			ctrl='lctrl', ctrl_l='lctrl', ctrl_r='rctrl',
			alt='lalt', alt_l='lalt', alt_r='ralt', alt_gr='ralt',
			cmd='lsuper', cmd_l='lsuper', cmd_r='rcmd',
		)
		key = translations.get( key, key ).replace( '_', '' )
		if key in 'lshift rshift lctrl rctrl lalt ralt lsuper rsuper'.split():
			if   eventType == 'key_press': self.modifiers.add( key[ 1: ] )
			elif eventType == 'key_release' and key[ 1: ] in self.modifiers: self.modifiers.remove( key[ 1: ] )
		modifiers = ' '.join( sorted( self.modifiers ) )
		# note that Shady's window-bound events system will give you key='8' followed by text='*'
		# when you press shift + 8 on a US keyboard, whereas this system will give you key='*'
		# followed by text='*' (pynput's key-press and key-release events have .char='*', and a
		# .vk code which would be tediously OS-specific and dependency- hungry to translate).
		event = KeyEvent( type=eventType, key=key.lower(), modifiers=modifiers )
		if world: world._ProcessEvent( event )
		else: print( event )
		if eventType != 'key_press': return
		if modifiers not in [ '', 'alt', 'shift', 'alt shift' ]: return		
		if len( key ) != 1: return
		event = KeyEvent( type='text', key=None, modifiers=modifiers, text=key )
		if world: world._ProcessEvent( event )
		else: print( event )
		
def ListenForKeystrokes( self ): KeyListener( self ).Start()
Rendering.World.ListenForKeystrokes = ListenForKeystrokes
