Property Sharing
================

Many attributes of a `Shady.World` or `Shady.Stimulus` instance are what we call
:doc:`"managed properties" <ManagedPropertiesAndManagedShortcuts>`. These are stored in arrays (even if they only contain a
single value and otherwise behave like scalars). Many of them are transferred
to the rendering engine on every frame for drawing. By default, every new
`Stimulus` object you create has a fresh new set of managed property arrays
created for it, initialized to their default values. However, it is possible
to force multiple stimuli to share the memory space for their properties,
linking their behavior together at with no extra runtime computational cost.
Sharing properties in this way will cause those stimuli to be linked until you
explicitly unlink them. This allows your program to be less complex and more
CPU-efficient, since you will only have to change the property value of one
stimulus and the change will affect all the others.

The simplest way to share a property between two stimuli is to use the shorthand
convention of assigning an actual `Stimulus` instance to the relevant property
value of another stimulus::

    import Shady
    world = Shady.World( 700, top=100, frame=True )
    stim1 = world.Patch( x=-200, rotation=30 )
    stim2 = world.Stimulus( x=+200, rotation=stim1 )
    # now, any change to either stimulus's rotation will affect both
    stim1.rotation = 45
    print( stim2.rotation )
    # --> 45

This technique is in fact a syntactic shorthand for the
`.ShareProperties` method of the first stimulus::

    stim1.ShareProperties( stim2, 'rotation' )
    # same effect as stim1.rotation=stim2

This more powerful method can be used to share multiple properties at
a time between multiple stimuli::

    import Shady
    world = Shady.World( 700, top=100, frame=True )
    master = world.Stimulus( size=50, y=100 )
    followers = [ world.Stimulus( size=50, x=x ) for x in range( -400, 400, 100 ) ]
    master.ShareProperties( followers, 'rotation', 'scale' )

Note that the name `master` here may be slightly misleading, because
sharing is fully symmetric: any change to the `.rotation`, or `.scale` of
any of the `Stimulus` instances in `followers` will affect the remaining
contents of `followers` *and* our `master`. That said, it may be useful
to designate one stimulus as the master to indicate a convention that
this stimulus should be used to control the others, especially if you
are going to use `dynamic property assignment <MakingPropertiesDynamic>`::

	master.rotation = lambda t: t * 20

`.ShareProperties()` also allows you to set property values at the same time
as sharing them::

    import Shady
    world = Shady.World( 700, top=100, frame=True )
    stim1 = world.Patch( x=-200 )
    stim2 = world.Patch( x=+200 )
    # share color and set that shared color to red
    stim1.ShareProperties( stim2, color=( 1, 0, 0 ) )

If you want a stimulus to stop sharing properties, you can again use the
shorthand of `Stimulus`-instance assignment::

	stim2.color = stim2      # tell `stim2` to "be yourself"
	
...which is really a shortcut for `stim2.MakePropertiesIndependent( 'color' )`.
The `MakePropertiesIndependent` method can also simultaneously change the
value(s) of one or more properties as it unlinks them - here's another example::

    # ...
    stim1.ShareProperties( stim2, position=( -100, 200 ), alpha=0.5, scale=2.5 )
    
    stim1.Set( position=600 )
    print( stim2.position )
    # --> [ 600, 600 ]
    
    print( ( stim1.scale, stim2.scale ) )
    # --> ( 2.5, 2.5 )
    stim2.MakePropertiesIndependent( scale=7 )
    print( ( stim1.scale, stim2.scale ) )
    # --> ( 2.5, 7.0 )
    
    stim2.alpha = 0.3     # still linked
    print( ( stim1.alpha, stim2.alpha ) )
    # --> ( 0.3, 0.3 )

One final warning: property sharing does **not** work with property index
shortcuts, as two stimuli cannot share just part of a full property array.
If you want to share specific property dimensions such as `.x` or `.red`,
but not the other dimensions of that property, you should use a dynamic
function instead to ensure it is continually updated::

    ### WRONG ###
    # ...
    stim2.x = stim1
    # --> ValueError: x is the name of a shortcut, not a fully-fledged
    #     property - cannot link it across objects

    ### RIGHT ###
    # ...
    stim2.x = lambda t: stim1.x   # (although it comes at a small CPU cost)

See the demo script :doc:`examples/sharing.py <examples_sharing>` for more.
