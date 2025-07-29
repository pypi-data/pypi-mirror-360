Managed Properties and Managed Shortcuts
========================================

.. _ManagedProperties:

Managed Properties
------------------

Most properties of a Shady `World` or Shady `Stimulus` are *managed* properties, 
which allows them to be manipulated in a number of powerful ways. Many of them
are simply containers for values that are automatically transferred to the GPU
on each frame, where the shader handles all of the computations required for
drawing.  Managed properties are mediated by descriptors of class `ManagedProperty`.

Managed properties support intelligent assignment. They are all technically arrays,
and you can always assign a `tuple`, `list` or `numpy.ndarray`, or any other
sequence of numeric values. For the sake of syntactic laziness you can also just
assign a single scalar value, if you want that value to be copied automatically
to all elements. For example::

	# Let's assume you have a running World, and that  `stim` is a reference to
	# one of the Stimulus instances that is being rendered by that World.
	
	stim.scale = ( 3, 1 )    # anisometric scaling
	print( stim.scale )
	# --> 3, 1
	
	stim.scale = 4           # isometric scaling in x and y
	print( stim.scale )
	# --> 4, 4
	
	stim.color = 0.5         # a simple way to set color to mid-gray
	print( stim.color )
	# --> 0.5, 0.5, 0.5
	
A property may be addressed by its canonical name, but also by aliases.  These are
provided to allow code to be less verbose, and to ease the burden on one's memory for
arbitrary names. For example, the `.envelopeTranslation` property answers to any of
the following names::

	stim.envelopeTranslation
	stim.position
	stim.pos
	stim.xy
	
Similarly, you don't have to remember which of the following synonyms is correct,
because they all work::

	stim.envelopeRotation
	stim.orientation
	stim.rotation
	stim.angle

Some properties also allow their individual *elements* to be addressed by name (see the
subsection on `Managed Shortcuts`_ below).

The `.Set()` method can be used to set multiple properties or shortcuts at once::

	stim.Set( scale=3, color=0.5 )

The class method `.SetDefault()` allows you to configure the default values of
managed properties for all future `World` or `Stimulus` instances until the
end of the current session::

	Shady.World.SetDefault( anchor=[ -1, -1 ] )
	# Now, all future `World` instances will have the origin of their coordinate systems
	# in the bottom left corner
	                                            
	Shady.Stimulus.SetDefault( color=[ 1, 0, 1 ], angle=30 )
	# Now, all future Stimulus instances will be tinted pink and lean thirty degrees to
	# the left by default when created. How useful.
	
Managed properties also support :doc:`dynamic value assignment <MakingPropertiesDynamic>`. This means that,
rather than simply assigning a static numeric value to the property, you can tell that
property *how* to change its value as a function of time::

	# ...
	def dynamic_scale( t ):
		return ( t % 1, t % 2 )   # ( x, y )
	stim.scale = dynamic_scale
	
	# or equivalently:
	stim.scale = lambda t: ( t % 1, t % 2 )
	
Note that a callable function object, rather than a static numeric value, is being assigned
to the Stimulus's managed `.scale` property. Shady will evaluate this function on every
frame to determine the final property value for drawing. When you query the property
value, for example by saying `print( stim.scale )`, you will still get a numeric result---
whatever the current value is at the time the command is issued.  If you actually wanted
to retrieve the function object, you would say `stim.GetDynamic( 'scale' )` instead.
	
Finally, managed properties can be intelligently copied, shared, and inherited across
stimuli.  The simplest way to share a property between two stimuli is to assign the
stimulus itself::

	# ...
	stim1.color = lambda t: ( t % 10 ) / 10   # dynamic: slowly change from black to white every ten seconds
	stim2.color = stim1   # assign Stimulus instance to share color with
	stim1.ResetClock(); time.sleep( 5 ); print( stim2.color )
	# --> 0.5, 0.5, 0.5   (because five seconds have passed)

Note that sharing is bi-directional, because it causes the properties of both stimuli to
point to the same array of numbers in memory::

	stim2.color = stim1          # first, forge the link
	stim1.color = 1, 0, 1        # then, change the value here...
	print( stim2.color )         # ...and the change is felt here
	# --> 1, 0, 1
	
	stim2.color = 0, 0, 1        # ...and vice versa:
	print( stim1.color )         # turnabout is fair play.
	# --> 0, 0, 1
	
See :doc:`PropertySharing` for a more in-depth explanation.


.. _ManagedShortcuts:

Managed Shortcuts
-----------------

Some managed properties provide subscripting shortcuts that allow *each element* to
be accessed by name. These are mediated by descriptors of class `ManagedShortcut`.
Examples::
	
	stimulus.Set( xscale=10, red=1, blue=0.5 )   # change horizontal scale, red color channel, and blue color channel
	print( stimulus.scaling )
	# --> 10, 1        # y scaling remains at its previous (default) value
	print( stimulus.color )
	# --> 1, -1, 0.5   # green channel remains at its previous (default) value

	stim.x = 100
	print( stim.x )   # .x is a shortcut for  .envelopeTranslation[0]
	# --> 100
	
	print( stim.envelopeTranslation )
	# --> 100, 0   (y remains at its default value)

The `.Set()` instance method and `.SetDefault()` class method support managed shortcuts
just as they do for managed properties. Also, managed shortcuts support dynamic value
assignment in the same way that full managed property arrays do::

	import time
	stim.y = lambda t: t ** 2
	stim.ResetClock(); time.sleep( 5 ); print( stim.position )
	# --> 100, 25
	
On each frame, dynamics are evaluated for full ManagedProperty arrays first, and then for
ManagedShortcut values.  This allows you to (for example) dynamically control the `.color`
property and then, independently and also dynamically, override just the `.red` channel
value.

Note that shortcuts cannot be shared directly between instances in the way that full
property arrays can. This is because sharing is accomplished by sharing the memory
segment for an entire property array or not at all (See :doc:`PropertySharing` for more
details). If you need to work around this limitation, one way to do so (at the expense
of a few extra CPU cycles per frame) is to use a dynamic value::

	stim2.red = lambda t: stim1.red


Unmanaged Dynamic Properties
----------------------------

Some properties, despite not being managed themselves, support :doc:`dynamic value assignment <MakingPropertiesDynamic>`.
Many such properties affect managed properties *indirectly*. For example, the following
properties of `Stimulus` support dynamics, and indirectly manipulate managed properties:

    `.frame`:
        Changing the value of the `.frame` property causes `.carrierTranslation[0]`
        to change in discrete steps, thereby showing different parts of a texture at
        different times.  This is one way to :doc:`animate multi-frame images <examples_animated-textures>`.

    `.page`:
        This property allows indirect manipulation of multiple properties that affect
        the stimulus carrier texture.  This is another way to :doc:`animate <examples_animated-textures>`.
    
    `.scaledSize`, `.scaledWidth` and `.scaledHeight`:
        These properties allow indirect manipulation of the managed property
        `.envelopeScaling`, dependent on the base `.envelopeSize`, to achieve a target
        size expressed in pixels on screen.
    
    `.points` and `.pointsComplex`:
        These properties allow simultaneous manipulation of `.nPoints` and `.pointsXY`,
        providing a view into the array of points either as a two-column array (`.points`)
        or as a one-dimensional array of complex numbers (`.pointsComplex`).

By contrast:

    `.text`
        supports dynamic value assignment (as a shortcut for assigning `.text.string`),
        but this does not work via indirect manipulation of a managed property.
        
Finally, it's worth noting that a dynamic can be associated with any attribute name at all:
it will still be evaluated, and the result assigned, once per video frame.  However,
newly-created attributes will not support the lazy syntax of dynamic value *assignment*,
so if you do this::

	stim.foo = lambda t: t * 2
	print( stim.foo )
	# --> <function <lambda> at 0x1006dd848>
	
you can see that `stim.foo` really is a lambda object, just as you would expect from
Python's default behavior. The way to create a custom dynamic is with `.SetDynamic()`::

	stim.SetDynamic( 'bar', lambda t: t * 2 )

Then `stim.bar = t * 2` will be performed automatically once per frame while the `World`
is running.


List of Managed Properties for the `World` Class
------------------------------------------------

In each case the first name given is the "canonical" name. Subsequent names, if
any, are aliases.  Names in brackets, if any, indicate managed shortcuts.

{listOfWorldProperties}

List of Managed Properties for the `Stimulus` Class
---------------------------------------------------

In each case the first name given is the "canonical" name. Subsequent names, if
any, are aliases.  Names in brackets, if any, indicate managed shortcuts.

{listOfStimulusProperties}

