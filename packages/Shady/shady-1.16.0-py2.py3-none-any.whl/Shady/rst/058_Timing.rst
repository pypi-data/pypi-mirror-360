Precise Control of Timing
=========================

Shady pushes most of the computational burden of drawing onto the graphics
processor. The few remaining necessary CPU operations are performed by an
engine, the default implementation of which is an :doc:`"accelerated" binary
written in C++ <Accelerator>`.  This provides a significant boost in
performance over Python-based engine implementations. Unfortunately,
resources are still limited and it is perfectly possible to overload Shady
and cause its animations fail to keep up with real time. Shady animations
tend to be accurate in the long term, because by design they are all
functions of "wall time" rather than frame number or frame-to-frame "delta".
But an excessive amount of Shady content (or load on the GPU and CPU from
other sources) will make your animations "skip" frames and hence become
uneven in time, and eventually reduce your effective frame rate. Even rare
"frame skips" may be problematic in certain scenarios (e.g. if you are
conducting motion perception experiments) because of the temporally-broad-band
artifacts they introduce.

This document outlines the principal hazards for Shady timing performance,
and describes some tips for avoiding them where possible.

General system settings
-----------------------

* Configure the desired frame rate on the display you will use for Shady.
  (e.g. on Windows 10: right-click on Desktop -> Display settings ->
  Display adapter properties -> "Monitor" tab -> Refresh rate).  At the same
  time, take the opportunity to ensure your screen resolution is set to
  maximum (this is important for displays that consist of discrete physical
  pixels, but does not apply if you are using a cathode ray tube display). 

* If there is a manufacturer-specific control panel for your graphics card,
  (for example, "NVidia Control Panel") then it may expose "vertical sync"
  as an option (possibly also called "vertical blanking" or "VBL"). Ensure
  that this is enabled.

* (Windows) If you have multiple displays, ensure that the screen Shady will
  appear on is selected as the "Main display" in your display settings. We've
  found this is particularly important when running different screens using
  different graphics cards, as it ensures that the correct display's intrinsic
  frame rate is respected. (This does unfortunately mean that the taskbar will
  need to be on the same screen as Shady.)

* Like most applications, Shady runs more smoothly when its window is in the
  foreground and fills the screen. For timing-critical applications, do not use
  a custom window size or a window frame if you want the best performance, and
  always make sure Shady is the focused window (this is easy to forget when
  working with the interactive console).

Vertical sync issues
--------------------

* As per above, ensure that this setting is enabled if your manufacturer-specific
  graphics card settings expose it (as in, for example, the "NVidia Control
  Panel").

* Use the :py:obj:`.SetSwapInterval() <Shady.World.SetSwapInterval>` method if you need to force a `Shady.World`
  to slow down its frame rate (e.g. to drop from 60 to 30 frames per second
  while remaining precisely regular). Note that this only works with the
  "accelerated" engine and only on some platforms/GPUs---see the docstring for
  `.SetSwapInterval()`.

* Use Shady's "tearing test" to check that vertical sync is working: if parts
  of the vertical stripe appear out of sync with the rest, or you can perceive
  torn or ragged edges, vertical sync is probably not functioning. You can
  launch the test from the command line with `python -m Shady tearing` or from
  inside Python with `Shady.TearingTest( world )`.

Optimization
------------

Though it may seem obvious to say it, you can save time between frames by optimizing
any Python code you are using to perform animation updates, aiming to make it
maximally efficient. Ensure that your numerical array operations are vectorized, that
you're not reinventing wheels that Shady can do in its accelerated engine or on the
GPU (e.g. texture color/contrast modulation using a spatial function), and that you
are not computing things unnecessarily. The demo :doc:`dots2 <examples_dots2>` allows you to compare
three different implementations of the same multi-stimulus animation, and to
observe that that `numpy` vectorization ("batch" mode) significantly improves timing
performance.

Below are some more specific tips for analyzing and improving your code.

Diagnostic tools
^^^^^^^^^^^^^^^^	

Frame interval gauge:
	The :py:obj:`Shady.FrameIntervalGauge() <Shady.Utilities.FrameIntervalGauge>` stimulus shows your frame-to-frame interval
	graphically in real time. Each minor grid unit represents 1 millisecond,
	and the red lines are spaced every 10 milliseconds. Ideally, the gauge
	should hover around `1000/f` milliseconds, where `f` is your optimal
	frame rate (e.g. ~16.7 ms for a 60 Hz display). Watch out for spikes,
	which indicate transient performance drops (frame skips). If these spikes
	occur unpredictably, check that your operating system hasn't decided to
	start a system process behind the scenes (Windows is particularly
	obnoxious about this). The gauge itself will have a tiny effect on your
	performance (far less than a text display would, in Shady---see below).
	
	NB: the frame interval gauge requires the third-party package `numpy`
	
Post-hoc timing plots:
	Use the :py:obj:`Shady.PlotTimings() <Shady.World.PlotTimings>` method to show a
	history of Shady's frame-to-frame intervals, along with optional
	additional information about the timings of specific aspects of the
	engine and individual stimuli. The information is enriched if the
	`debugTiming` attribute is set to `True` for your `World` and `Stimulus`
	instances. You can also plot timings from a Shady log file with
	`Shady.Utilities.PlotTimings(logfilename)`---or the same thing can be
	invoked from outside Python with  `python -m Shady timings LOGFILENAME`.

	NB: timing plots require the third-party packages `numpy` and `matplotlib`.

.. DOC-TODO: Screenshots of graphs with and without `world.debugTiming=True`? And a guide to interpreting such plots?

Shady usage tips
^^^^^^^^^^^^^^^^

Stimulus overload:
	Unsurprisingly, drawing too many stimuli at once will slow you down---
	particularly when they overlap, which will require blending operations
	and/or cause Shady to draw the same pixels multiple times. Keep in mind
	that drawing a few large stimuli is faster than drawing more numerous
	smaller stimuli, even if the total number of pixels is the same, due to
	the parallel architecture of GPU computations. If you have reached your
	system's draw limit, consider whether you could:
	
	* combine multiple linked stimuli into one larger stimulus;
	* disable stimuli whenever you expect them to be out of sight---you can
	  disable rendering by setting `.visible=False`, or disable rendering
	  *and* inter- frame property updates by calling `.Leave()`;
	* use other Shady tricks (such as :doc:`property sharing <PropertySharing>`) to reduce the number
	  of update computations per frame;
	* use a single multi-shape `Stimulus` (as exemplified in the demos
	  :doc:`dots1 <examples_dots1>`, :doc:`dots3 <examples_dots3>` and :doc:`dots4 <examples_dots4>`) rather than multiple separate `Stimulus`
	  instances (as in :doc:`dots2 <examples_dots2>`).

Text properties:
	Beware of changing the text properties of your stimuli too often if using
	`Shady.Text` functionality. Shady is smart enough that it does not re-
	compute the pixel values of a text stimulus unless there is an actual
	de-facto change to the text content or style. However, when this *does*
	occur, Shady must re-render the texture on the CPU and send the result to
	the GPU. This is out of step with Shady's usual approach of doing all pixel
	processing on the GPU, and is almost as expensive as creating a new stimulus
	every time you change the text content. One workaround for rapidly switching
	between a number of pre-determined text objects is to create them in advance,
	each as a separate `.page` of the same `Stimulus` instance, and switch
	between them.

Video file playback:
	Similarly, be mindful of the cost of video playback using `Shady.Video`.
	If you're working from a video file, each new frame must be decoded on the
	CPU. In addition, regardless of whether it came from a file or from a live
	camera, the frame must be sent from CPU to GPU. Unfortunately, we currently
	have no workaround for this other than rendering the particular frames you
	need as a multi-frame `Stimulus`, and this may not be feasible for long
	videos. Lowering the video file's resolution, and/or restricting the
	`.video.aperture`, may reduce the impact on performance somewhat.

External operations: 
	Be mindful of the impact of concurrent *non*-Shady CPU and GPU operations,
	both inside and outside of Python.
	
	If a significant number of concurrent operations are being performed *inside*
	the same instance of Python that is running Shady, you should read
	:ref:`the note at the end of Shady.Documentation.Concurrency <gil>` about
	multi-threading in Python---the short version is that you may really want
	to run multiple *processes* of Python, and give Shady its own process, rather
	than using Python's controversial (arguably illusory) multi-threading.

Order of Operations
-------------------

In certain advanced setups, you may wish to configure your system to respond
to the physical state of the screen (for example, by making your Python code
wait until a stimulus has triggered a light sensor stuck to the screen). In
such cases, you may need to know that Shady's engine calls your Python callbacks
to prepare frame `n+1` *before* the preceding frame `n` has been physically
displayed. The explanation is as follows.

At its simplest level of abstraction, the main Shady loop consists of three
operations. Since these are performed in a never-ending cycle, this means that
(up to cyclical reordering) there are two potential orders in which to do them:
	
Order A:

	- A1: Prepare parameters (Python callback)
	- A2: Send draw commands to GPU
	- A3: Display completed frame (swap buffers)

Order B:

	- B1: Send draw commands to GPU
	- B2: Prepare parameters (Python callback)
	- B3: Display completed frame (swap buffers)

While it may seem more intuitive to use order A, Shady actually uses order B.
This is for reasons of efficiency. Sending draw comments (B1) takes very little
time on the CPU, but it initiates a series of potentially time-consuming
operations on the GPU. Displaying the completed frame (B3) must wait until the
GPU has finished. What should we be doing on the CPU in the meantime, while the
GPU is busy? The most efficient use of resources is to have both CPU and GPU
busy at the same time. Hence, the Python callback is called *while* the GPU is
busy drawing, but before the frame is displayed. Therefore, the cycle looks like
this:

	- B1: Send draw commands to GPU for frame 0
	- B2: Prepare parameters for frame 1
	- B3: Display frame 0
	- B1: Send draw commands to GPU for frame 1
	- B2: Prepare parameters for frame 2
	- B3: Display frame 1
	- B1: Send draw commands to GPU for frame 2
	- B2: Prepare parameters for frame 3
	- B3: Display frame 2
	- ...

This means that the Python callback (B2) for frame `n+1` *must return* before
you get to physically see frame `n`.  Provided your callbacks meet their
deadlines, that's usually no problem, but if you specifically intervene to make
a callback return late, or to wait for a physical light signal that is supposed
to originate on frame `n`, then you will see strange effects.  The more
intuitive ordering:

	- A1: Prepare parameters for frame 0
	- A2: Send draw commands to GPU for frame 0
	- A3: Display frame 0
	- A1: Prepare parameters for frame 1
	- A2: Send draw commands to GPU for frame 1
	- A3: Display frame 1
	- A1: Prepare parameters for frame 2
	- A2: Send draw commands to GPU for frame 2
	- A3: Display frame 2
	- ...

...is less efficient: on each frame, we now have to wait for the Python callback
(A1) to finish before we can even start (A2) the GPU operations. CPU and GPU are
now operating in series, not in parallel.

In fact, the assumption we made earlier, i.e. that the "swap buffers" operation
(A3/B3) is synchronous and only returns once the frame is fully composed and
swapped into visibility, is only true for *some* graphics cards/drivers.  For
others, the CPU's "swap buffers" call merely adds yet another instruction to the
GPU's queue, then returns immediately. In the latter case, order A could in
principle be just as efficient as order B (of course, at *some* point the CPU's
OpenGL API calls must wait for the GPU to catch up, and presumably that would
happen, at latest, during the "send draw commands" stage for the subsequent
frame, but so far it's unclear to us whether in general there is a consistent
moment or operation at which this is guaranteed to happen). However, because
of the synchronous behaviour on *some* graphics cards, Shady's strategy is to
try to make this behaviour uniform across as many graphics cards as possible,
by *forcing* A3/B3 to wait synchronously for the vertical blanking interrupt.
So the accelerated Shady engine actually has explicit code for waiting until
the frame has been displayed, and this works on several platforms such as macOS
and NVidia-on-Windows (but can *still* fail on a few---mostly on Linux in our
experience so far). An advantage of this approach is that it makes timing
diagnostics easier to interpret (the CPU can measure a clear "time zero" for
every frame), and the disadvantages are negligible *provided* we stick to order
B.
