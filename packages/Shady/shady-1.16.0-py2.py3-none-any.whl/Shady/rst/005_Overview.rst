Overview
========

Shady is a two-dimensional graphics engine and Python programmer's toolkit, designed
to make stimulus display easy in neuroscience---especially vision science.

It enables precise presentation of visual stimuli even on mass-produced screens and
video cards, without additional specialized hardware. It allows you to render arbitrary
stimulus patterns linearly with high dynamic range and high timing precision. It lets
you manipulate them in real time while leaving the CPU maximally free to perform other
time-critical tasks.

At its core, Shady is a customizable, specialized "shader" program, written in `GLSL <https://en.wikipedia.org/wiki/GLSL>`_,
that runs on the graphics processor (GPU). An "engine", compiled from C++, performs the
frame-by-frame `OpenGL <https://en.wikipedia.org/wiki/OpenGL>`_ calls required to drive the shader. The Python package
provides high-level wrappers and an API for controlling the shader via the engine (it
also contains a fallback implementation of the engine in pure Python, but for performance
reasons we do not recommend using this).

Shady provides the following functionality:

* lets you take control of your display screen, ensuring that you have precise
  control over every physical pixel, despite the rescaling tricks modern operating
  systems try to do;

* handles :doc:`gamma-correction and dynamic-range enhancement of stimuli <PreciseControlOfLuminance>` automatically
  and transparently;

* provides simple hooks for injecting your own small segments of GLSL code, to
  define custom signal functions, windowing functions and contrast modulation
  functions, as well as any custom parameters they require;

* eliminates "boilerplate" coding and minimizes the length of your program: it
  takes one line of code to initialize the system, open a full-screen window and
  start the rendering engine, one line to create a stimulus, and (often) only one
  line to define how the stimulus should be animated;

* provides a surrounding ecosystem of:

  - ancillary functions (e.g. functions for computing/converting contrast ratios and
    visual angles)
    
  - high-level diagnostic tools: test patterns, timing performance checks, interactive
    perceptual linearization, image and video capture, ...
    
  - flexible tools for controlling stimulus behavior in time: state machines,
    general-purpose function objects that can be manipulated arithmetically, as well as
    specialized functions that integrate, smooth, oscillate, self-terminate, ...

Shady was conceived to play a modular role in larger, more complex multi-modal
neuroscience applications. As such, it avoids dominating or constraining the user's
programming environment. Rather, it aims to be a "good citizen" in three ways:

* Maximize compatibility: Shady's Python, C++ and GLSL code has been confirmed to run
  correctly on recent versions of Windows, macOS and Ubuntu Linux. Beyond the operating
  system itself, no proprietary software is required to run or to develop with Shady.
  It is fully compatible with both Python 2 and Python 3. It does not *require*
  third-party packages over and above the base Python system. It does leverage a few
  highly prevalent packages (`numpy`, `pillow`, `matplotlib`, `ipython`, `opencv-python`)
  to expand and improve its functionality where possible. However, we have designed Shady
  to be tolerant of variation in these packages' version numbering, and to degrade
  gracefully even in their absence.

* Embrace Windows: support for Windows is not a grudgingly provided afterthought. Windows
  is our primary platform for performance optimization, because it is the platform on
  which we expect to find most prevalent support for specialized neuroscientific hardware
  (eye-trackers, EEG amplifiers, etc.) as well as novel human interface devices.
  Therefore, it is the platform on which we expect to see the greatest development of
  integrated multi-modal neuroscience applications, and hence the place where Shady has
  most to offer, as a modular component of such systems.
 
* Minimize CPU load:  the Shady engine uses the GPU for as much as possible of the
  frame-by-frame stimulus generation and processing, leaving the CPU free for other
  tasks like real-time biosignal processing.

To minimize CPU load, the shader pipeline ensures that the following steps are handled
by the GPU on every frame:

1. Generation of a *carrier* pattern (pre-computed texture, and/or procedurally-generated
   signal, and/or color);
   
2. Translation and/or rotation and/or scaling of the carrier pattern (NB: this may 
   create interpolation artifacts if the carrier contains a pre-computed texture);

3. Contrast effects: overall scaling, and/or spatial windowing, and/or other
   (customizable) spatial modulation functions;
      
4. Repositioning and/or rotation and/or scaling of the complete stimulus (NB: rotation
   and scaling may create interpolation artifacts, in any stimulus);
    
5. Optional addition of dynamic Gaussian or uniform noise;

6. :doc:`Gamma-correction and dynamic-range enhancement <PreciseControlOfLuminance>`, by one of a number of
   possible strategies (some requiring specialized equipment, some not);
    
7. Quantization down to native precision of the graphics card.

See the :doc:`Shady.Documentation.Pipeline <Pipeline>` topic documentation for a more detailed breakdown
of these steps.

