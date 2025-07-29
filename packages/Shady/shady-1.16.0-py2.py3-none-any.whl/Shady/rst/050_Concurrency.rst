Creating a `World`
==================

Shady stimulus displays revolve around an object called the `World`. Most
Shady applications would begin by creating a `World` instance. There are
two ways of designing your application around the `World`: either run
everything in a single thread, or allow Shady's graphical operations to
happen in one thread while continuing to work in another.  The 
multi-threaded way is our preferred approach, particularly as it allows
the programmer to construct and refine stimuli interactively during the
design and implementation of an application.

.. contents:: :local:


Running single-threaded
-----------------------

Here's an example of how you can use Shady in a single-threaded way::

    import Shady

    w = Shady.World( threaded=False )
    # This may (depending on platform) open a window already, but
    # if so it will be inactive.

    s = w.Stimulus(
        signalFunction = Shady.SIGFUNC.SinewaveSignal,
        signalAmplitude = 0.5,
        plateauProportion = 0.0,
        atmosphere = w,
    )
    # create a Stimulus...
    
    s.cx = Shady.Integral( 50 )
    # ...and perform further configuring on it as desired
    
    @w.AnimationCallback
    def EachFrame( self, t ):
        # ...  any code you write here will be called on every
        # frame. The callback can have the prototype `f(self, t)`
        # or just `f(t)`, where `t` is time in seconds since the
        # `World` began. Note that each `Stimulus` instance can
        # have its own animation callback too.
        pass

    w.Run()
    # This is a synchronous call - it returns only when the window closes.
    # It renders stimuli dynamically in the window and allows the window to
    # respond to mouse and keyboard activity (with the default event-handler
    # in place, you can press Q or escape to close the window).

In the above example, `World` construction, rendering, and all animation and
event-handling callbacks happen in the main thread.  You should not try to
type the above commands line-by-line into an interactive prompt, because the
second line may (on some platforms) create a frozen full-screen window that
may then obscures your console window and, because it is not processing events,
may not respond to your attempts to alt-tab away from it.

A slightly different way to organize the above would be to put the
stimulus-initialization code in the `Prepare()` method of a `World`
subclass::

    import Shady

    class MyWorld( Shady.World ):

        def Prepare( self, speed=50 ):
            self.Stimulus(
                signalFunction = Shady.SIGFUNC.SinewaveSignal,
                signalAmplitude = 0.5,
                plateauProportion = 0.0, 
                cx = Shady.Integral( speed ),
                atmosphere = self,
            )
        
        def Animate( self, t ):
            # ... the `.Animate()` method will be used as the
            # animation callback unless you replace it using the 
            # `@w.AnimationCallback` decorator or (equivalently) the
            # `w.SetAnimationCallback()` method.
            pass

    w = MyWorld( threaded=False, speed=16 )
    # The `speed` argument, unrecognized by the constructor, is simply
    # passed through to the `.Prepare()` method (the prototype for
    # which may have any arguments you like after `self`).

    w.Run()
    # As before, because the `World` was created with `threaded=False`,
    # the window will be inactive until you call `.Run()`

Running the Shady engine in a background thread (Windows only)
--------------------------------------------------------------

The following has worked nicely for us on Windows systems::

    import Shady
    w = Shady.World()   # threaded=True is the default
    # the `World` starts rendering and processing events immediately,
    # in a background thread

    w.Stimulus( sigfunc=1, siga=0.5, pp=0, cx=Shady.Integral( 50 ), atmosphere=w )
    # thread-sensitive operations like this are automatically deferred
    # and will be called in the `World`'s rendering thread at the end
    # of the next frame.

    @w.AnimationCallback
    def DoSomething( t ):
        # ... you can set set the animation callback as before, if
        # you need one (with or without the `self` argument)
        pass

In this case, a synchronous call to `w.Run()` is optional: all that would do
is cause your main thread to sleep until the `World` has finished.

This relies on using the binary "ShaDyLib" :doc:`accelerator <Accelerator>` as the `Shady.Rendering.BackEnd()`.
Without the accelerator (using, for example, `pyglet` as the back-end) you
may find that some functionality (such as keyboard and mouse event handling)
does not work properly when the `Shady.World` is in a background thread.

It also relies on Windows.  On other platforms, the graphical toolkit
GLFW, which underlies the ShaDyLib windowing back-end, insists on being in
the main thread (nearly all windowing/GUI toolboxes seem to do this). If
you try to create a `Shady.World` on non-Windows platforms without saying
`threaded=False`, it will automatically revert to `threaded=False` and
issue a warning, together with a reminder that you will have to call
`.Run()` explicitly.  Unless, of course, you use a sneaky workaround,
as described in the next section...


Multi-threaded operation on non-Windows platforms
-------------------------------------------------

It is convenient and readable, and especially conducive to *interactive*
construction of a `World` and its stimuli, to be able to say::

    import Shady
    w = Shady.World()
    # ...

and have the `World` immediately start running in a different thread,
while you continue to issue commands from the main thread to update its
content and behavior.  However, as explained above, you can only do
this on Windows: on other platforms, the `World` will only run in the
main thread.

There is a workaround, implemented in the utility function
`Shady.Utilities.RunShadyScript()`, which is used when you start an
interactive session with the `-m Shady` flag::

    python -m Shady

or when you invoke your python script with the same flag::

    python -m Shady my_script.py

(In the latter case the `run` subcommand is assumed by default, so this
is actually a shorthand for::

    python -m Shady run my_script.py

There are other subcommands you can use, such as `demo`, which allows 
you to run scripts as interactive tutorials if they are specially 
formatted---as many of our :doc:`example scripts <ExampleScripts>` 
are.)

Starting Python with `-m Shady` (or equivalently, calling
`RunShadyScript()` from within Python) starts a queue of operations
in the main thread, to which thread-sensitive `Shady.World` operations
will automatically be directed. It then redirects everything *else*
(either the interactive shell prompt, or the rest of your script) to
a subsidiary thread.

For many intents and purposes, this is just like starting the
`Shady.World` in a background thread: its main advantage is that it
allows you to build and test your `World` interactively on the command
line.  It has its limitations, however. For one thing, you can only
create one `World` per session this way, whereas threaded `World`
instances, on Windows, can be created one after another (you can even
have two running at the same time---although we have no data and only
pessimistic suspicions about their performance in that case).  The
fun also comes to a crashing end when you to try do something else
that requires a solipsistic graphical toolbox, like plotting a
`matplotlib` graph.


.. _gil:

Limitations on multi-threaded performance in Python
---------------------------------------------------

So far, we have found that our multi-threaded `Shady` applications
have generally worked well on Windows. This is largely because
most of the rendering effort is performed on the GPU, and most
of the remaining CPU work is carried out (at least by default
if you have the ShaDyLib :doc:`accelerator <Accelerator>`) in compiled C++ code
rather than Python. Very very little is actually done in Python on
each frame.

However, as soon as your Python code (animation callbacks, dynamic
property assignments, and event handlers) reaches a certain critical
level of complexity, you should be aware of the possibility that
Python itself may cause multi-threaded performance to be significantly
worse than single-threaded. This is because the Python interpreter
itself cannot run in more than one thread at a time, and multi-threading
is actually achieved by deliberately, cooperatively switching between
threads at (approximately) regular intervals, mutexing the entire
Python interpreter and saving/restoring its state on each switch. This
is Python's notorious Global Interpreter Lock or GIL, and a lot has been
written/ranted about it on the Internet, so we will not go into the
details here.  Just be aware that it exists, and that consequently it is
often better to divide concurrent operations between *processes* (e.g.
using the standard `multiprocessing` module) rather than between threads.
You might decide to design your system such that all your `Shady` stuff,
and *only* your `Shady` stuff, runs in a single dedicated process. That
process would then use the tools in `multiprocessing`, or other
inter-process communication methods, to talk to the other parts of the
system.
