Making Properties Dynamic
=========================

Individual Properties
---------------------

Many attributes of a `Shady.World` or `Shady.Stimulus` instance are what we call
:doc:`"managed properties" <ManagedPropertiesAndManagedShortcuts>`. A key feature of these properties is the ability to be made
dynamic.  This can be done simply by assigning a function object to the property
instead of a static value or array. The function should take one argument, `t`
(for time, in seconds), and return whatever value (or array of values) you want
that property to have at time `t`. On every frame callback, Shady will run any
dynamic property functions you have assigned using the current `World` time and
update the value of the corresponding properties.

Note that there are multiple ways to create callable objects in Python. The
standard way is to define a function using `def`::

    import Shady
    world = Shady.World( 700, top=100, frame=True )
    
    stim = world.Patch()
    
    def simple_spin( t ):
        return t * 45
        
    stim.rotation = simple_spin # note no parentheses - we are assigning the
                                # function object itself, not its output
                                   
Another way is to specify an anonymous function in-line using `lambda`::

    stim.rotation = lambda t: t * 45
    
Both methods are valid. Just remember that `lambda` functions are restricted
to containing just the single expression you want to return from the function.

Note that `t` is measured in seconds, and by default it is the number of
seconds elapsed since the `World` first started rendering stimuli. So if it
has been a long time since the `World` started, your `Stimulus` will likely
be off the screen in the above example.  One option is to give the `Stimulus`
its own independent "time zero". This can be reset to the current time using
the call::

    stim.ResetClock()

There are no unusual restrictions on your dynamic functions, provided that
they take exactly one argument and return a value or sequence that is
appropriate for the property with which they are associated. (It is also
legal for them to return `None`, in which case the property value is not
changed.) Any Python variables or objects that are accessible in the same
namespace can be used and modified::

    speed = 45
    stim.rotation = lambda t: speed * t
    # ...
    speed *= 2   # doubles the rotation speed
    
Dynamic functions are free to ignore the time variable. You can make the
properties of your stimulus dependent on whatever variables you want::

    import Shady
    world = Shady.World( 700, top=100, frame=True )
    stim1 = world.Patch(
    	pp = 1,
    	x = lambda t: ( t % 1.0 ) * 300,
    )
    
    stim2 = world.Patch(
    	pp = 1,
    	color = [ 1, 0, 0 ],
    	y = lambda _: stim1.x,   # ignores the time input
    )
    
Note that we still have to define our dynamic function with exactly one
argument so that Shady can pass in the stimulus's clock, but name it
`_` as a convention to indicate that this argument is not used.

Note also that the function references `stim1.x` which is itself dynamic.
Whenever you access a managed property, its current *static* value (or
array of values) will be returned, even if the property is
dynamic. If you want to retrieve the actual function object being used
to calculate its dynamics, use the `Shady.Stimulus.GetDynamic` method::

    print( stim1.x )
    # --> 294.8838
    
    print( stim1.GetDynamic( 'x' ) )
    # --> <function __main__.<lambda>(t)>
    
More generally, you can set a Shady property to any callable object that takes
exactly one argument. This includes any instance of a class with a `__call__`
method defined, provided the call takes one argument. The optional `Shady.Dynamics`
submodule offers several useful classes designed to be used as dynamic properties
in Shady, such as the :py:obj:`Integral <Shady.Dynamics.Integral>` for integrating arbitrary functions over time
or the  :py:obj:`Transition <Shady.Dynamics.Transition>` for smoothly transitioning between a start and end value.

NOTE: Be wary when using the same public variable to define multiple dynamics functions
in a row. Because of how functions interact with their namespace in Python, the
*current* (i.e. last set) value of that variable will be used when the dynamics are
evaluated on each Shady frame callback. This includes simple looping variables! If you
want to 'freeze' the value of a public variable when defining a dynamic function, you
will need to separate it from that variable's namespace, e.g. by using a nested function
or by passing the variable to a lambda as a keyword argument::

    ### WRONG ###
    import Shady, math
    world = Shady.World( 700, top=100, frame=True )
    stimuli = []
    amplitudes = [100, 200, 300]
    for amplitude in amplitudes:
        stim = world.Stimulus()
        stim.x = lambda t: amplitude * math.sin( 2 * math.pi * t )
        stimuli.append( stimulus )
    # all three stimuli will use amplitude == 300 when their dynamics are evaluated!

    ### ALSO WRONG ###
    import Shady, math
    world = Shady.World( 700, top=100, frame=True )
    stimuli = []
    amplitudes = [100, 200, 300]
    for i in range( 3 ):
        stim = world.Stimulus()
        stim.x = lambda t: amplitudes[i] * math.sin( 2 * math.pi * t )
        stimuli.append( stimulus )
    # all three stimuli will use i == 2, i.e. amplitudes[2]!
    
    ### RIGHT (nested function) ###
    import Shady, math
    
    def create_oscillation_dynamic( amplitude )
        # the argument `amplitude` is retrieved from a frozen
        # version of the namespace of this function
        return lambda t: amplitude * math.sin( 2 * math.pi * t )
    
    world = Shady.World( 700, top=100, frame=True )
    stimuli = []
    amplitudes = [100, 200, 300]
    for amplitude in amplitudes:
        stim = world.Stimulus()
        stim.x = create_oscillation_dynamic( amplitude )
        stimuli.append( stim )
        
    ### ALSO RIGHT (lambda keyword) ###
    import Shady, math
    
    world = Shady.World( 700, top=100, frame=True )
    stimuli = []
    amplitudes = [100, 200, 300]
    for amplitude in amplitudes:
        stim = world.Stimulus()
        # the variable `amplitude` is similarly frozen as an argument
        stim.x = lambda t, a=amplitude: a * math.sin( 2 * math.pi * t )
        stimuli.append( stim )
    
Also note that properties of your `World` instance can be made
dynamic using all of the methods described above. For example, to
create a world whose background color oscillates between black and
white::

    import math
    import Shady
    world = Shady.World( clearColor=lambda t: 0.5 + 0.5 * math.sin( 2 * math.pi * t ) )

The world's dynamics will be updated before any of the stimuli it contains,
and its stimuli are updated according to their draw order (i.e. `.z`).
Stimuli with the same `z`-value will be drawn in the order they were
created.

The Animate Method
------------------

As the behavior of your stimulus grows more complex and its
properties become more interdependent, you may begin to find that relying
on individual property dynamics becomes unwieldy. In this case, you will
likely want to use the stimulus's `Animate()` method, which is evaluated
before any property dynamics on each Shady frame callback.

The only practical difference between the `Animate()` method and
any dynamic properties is that `Animate()` takes a `self` argument,
which makes it easier to refer to the stimulus in your logic (e.g.
for checking and modifying its state). The function does not need
to return any value, which means that you will most likely want to
create it using the standard `def`. Once created, pass the function
object to the `.SetAnimationCallback()` method to properly bind it to
the stimulus::

    import Shady, math, time
    world = Shady.World( 700, top=100, frame=True )
    ball = world.Patch( color=[1, 0, 0 ], pp=1 )
    
    ball.is_bouncing = False
    ball.bounce_t0 = None

    def bounce( self, t ):
        if self.is_bouncing:
            if self.bounce_t0 is None:
                self.bounce_t0 = t
                # Note use of `_t` in the lambda to distinguish it from the bounce() argument `t`.
                self.y = lambda _t: 100 * abs( math.sin( 2 * math.pi * (_t - self.bounce_t0 ) ) )
        else:
            if self.bounce_t0 is not None:
                self.bounce_t0 = None
                self.y = 0

    ball.SetAnimationCallback( bounce )   # again, note that function object is assigned
    ball.is_bouncing = True   # set it back to False to stop the bounce

This example is a little more complex than any of the examples in
the previous section, but that's exactly why the `Animate()` method
is useful. The `bounce()` function assigns a bouncing dynamic to
the stimulus's y-coordinate whenever `is_bouncing` is set to `True`,
making sure that the stimulus only starts bouncing at that moment.
It abruptly resets the y-coordinate to zero whenever `is_bouncing`
is set to False. (The optional `Shady.Dynamics` submodule contains a
`StateMachine` class that makes it easier to switch your stimuli
between different modes of behavior like this.)

If your animation callback has two arguments (i.e. a `self` as well
as just a `t`) then you *must* use the `.SetAnimationCallback()` helper
to properly bind your function as the `.Animate()` method of the
instance, so that Python knows that the Stimulus instance should be
passed in as the `self` argument. The following will **not** work::

    ### WRONG ###
    # ...
    stim.Animate = bounce

If your callback has only one argument, it is interpreted as time
`t`---in this case, you can use `.SetAnimationCallback()` or just
directly assign `stim.Animate = func`.

As with dynamics, instances of the `World` class can have an
`.Animate()` method set in the exact same way as instances of
the `Stimulus` class.

Note that that `Stimulus` and `World` instances provide have an
attribute `AnimationCallback` which can be used as a decorator,
as a syntactic alternative to calling `.SetAnimationCallback()`::

    @stim.AnimationCallback
    def bounce( self, t ):
        # ...

Order of Dynamic Evaluations
----------------------------

Shady evaluates property dynamics and `Animate()` methods in the
following order on each frame:

    1. `World.Animate()`
    
    2. `World` dynamic properties
    
    3. Each `Stimulus` (sorted first by `.z` and second by time of
       creation):
       
          a. `Stimulus.Animate()`
          b. Stimulus dynamic properties

For each `World` or `Stimulus` instance, the dynamics are evaluated
in a fixed order relative to each other. The order may seem arbitrary.
It is not recommended to make dynamic properties that use the values
of other dynamic properties, thereby relying on an assumption that
certain dynamics are evaluated before others in a given frame. If
you need to do this, a clearer approach would be to use the `Animate()`
method to set the properties procedurally in the order you need
them calculated.
