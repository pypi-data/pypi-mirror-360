Compatibility
=============

.. admonition:: Summary
	:class: tip

	- We optimize Shady's performance on Windows. It works on other operating
	  systems, but there your mileage will vary more widely.
	  
	- Shady works with Python 2 or 3.
	
	- Recommended third-party packages |numpy|_, |pillow|_, |matplotlib|_,
	  and |ipython|_ are not strictly required, but they improve functionality.
	  By default, they will be installed automatically if you install Shady via
	  `python -m pip install shady`.
	  
	- In addition, |opencv-python|_ allows reading/saving of video files.


Hardware and Operating Systems
------------------------------

Shady was conceived to play a modular role in larger, more complex multi-modal
neuroscience applications. These may include novel human interface devices
and/or specialized neuroscientific equipment, such as eye-trackers and EEG
amplifiers. Manufacturers of such equipment are overwhelmingly more likely
to support Windows than anything else.

Hence, the Windows platform is where we aim to optimize performance, and most
of our experience in doing so has been with Windows 10/11. On other platforms,
it should not be any harder to get Shady running, but it may be harder to
get it to perform really *well*. Therefore, we had better describe our support
for non-Windows platforms as "experimental". However, our experiences so far
(with macos 10.9 through 14.4, and with Ubuntu 24.04 LTS for Desktops) indicate
that both the C++ code and CMake files for the :doc:`accelerator <Accelerator>`, and the Python code
of the rest of the module, are cross-platform compatible.

Shady probably will not work on big-endian hardware. Since most commercial CPUs
are little-endian, at least by default, we have had no opportunity to test it
on big-endian systems and little interest in doing so.


Python and Third-Party Python Packages
--------------------------------------

.. _PythonRequirements:

Scientific software packages in Python have an unfortunate tendency to rely on
a "house of cards" made up of specific versions of other third-party
packages. Somewhere in the hierarchy of dependencies, sooner or later you end
up locked into a legacy version of something you don't want. With this in mind,
we limited Shady's dependencies to a small number of well established, very
widely used, and actively developed general-purpose packages. We test it
with 5-year-old versions of its principal dependencies as well as current
versions. We also take care to ensure that Shady's functionality degrades
gracefully even in their absence.

Shady supports Python versions 2 and 3 (specifically CPython, which is the
standard, most prevalent implementation). Shady doesn't have *hard*
dependencies on third-party packages beyond that. On any CPython
implementation of version 2.7.x, or 3.4 and up, some of Shady's core
functionality should be available. This claim comes with two caveats.

The first caveat is that we are assuming availability of the ShaDyLib
:doc:`accelerator <Accelerator>` which is a compiled binary (dynamic library). Compiled
binaries for 32-bit Windows, 64-bit Windows and 64-bit macOS (10.9+) are
bundled as part of the Shady distribution. If you are using a different
OS (e.g. some flavour of Linux, or macOS version earlier than 10.9) or
if the dynamic library fails to load for any reason (some form of
dynamic-library dependency hell, no doubt) then you may need to (re)compile
the accelerator. *Without* the accelerator, you can still run Shady, but
its timing performance will be more inconsistent and generally worse, and
you will need to install another third-party package named `pyglet <https://pypi.org/project/pyglet>`_
for Shady to use as a graphics backend (`python -m pip install pyglet`).

The second caveat is that there are a few *recommended* third-party packages,
without which Shady's functionality is relatively limited. Without any
third-party packages at all, you can display rectangular or oval patches,
with or without a customizable 2-D carrier signal function, a 2-D contrast
modulation function, a spatial windowing function, colour, and dynamic pixel
noise. You will also have :doc:`powerful tools <MakingPropertiesDynamic>`
for governing the way these properties change over time. The following
third-party packages, if available, add specific extra types of
functionality over and above the core:

    |numpy|_:
	
      - Create or render arbitrary textures defined as pixel arrays.
      - Subtle, powerful improvements to existing functionality---for
        example, dynamic objects like `Shady.Dynamics.Integral` can be
        multi-dimensional (see :doc:`examples/dots4.py <examples_dots4>`).

    |pillow|_:

      - Load texture data from common image formats on disk (also
	    requires `numpy`).
      - Render text stimuli, in a mono-spaced font (also requires `numpy`).
      - Save screen capture data to disk in common image formats.

    |matplotlib|_:

      - Render text stimuli in any of the fonts installed on your system
	    (also requires `numpy` and `pillow`).
      - Plot timing diagnostics and image histograms.

    |opencv-python|_:

      - Requires `numpy`.
      - Save stimulus sequences as movie files.
      - Display stimuli from video files or live camera feeds.
      - Write live camera feeds to disk in common video formats.

    |ipython|_:

      - Improve interactive configuration of Shady stimuli.
      - Improve user experience at the command prompt (e.g. tab completion,
        dynamic object introspection, cross-session command history).

With the exception of `opencv`, these packages are extremely
prevalent, used in every conceivable type of scientific application,
all around the world.  They will get installed by default when you say
`python -m pip install shady` (although, if you have an Anaconda
installation, you may prefer to first ensure they're installed via
`conda` rather than letting |pip|_ do it).  `opencv` is a more
special-purpose package, so we leave it to you to install it if you
want it.

To install everything in a minimal "Miniconda" environment::

	python -m conda install numpy pillow matplotlib ipython
	python -m pip install shady
	python -m conda install opencv

Depending on versions, `opencv` may or may not be available via
`conda`---if not, you can use `pip`.  If your Python distribution
is not Anaconda-flavored, you can let |pip|_ do everything::

	python -m pip install shady
	python -m pip install opencv-python


Known issues
------------

"Legacy" vs "Modern" OpenGL and random noise generation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Shady is based on `OpenGL <https://opengl.org/about/>`_, and makes extensive use of OpenGL Shading Language (GLSL)
to implement pixel processing in parallel on the graphics card. OpenGL/GLSL come in
two flavours: "modern" means OpenGL version (and corresponding GLSL version) 3.3
and up, whereas "legacy" refers to earlier versions. The drawing commands under the
hood are different in these two different contexts, and the features supported by a
given graphics card may also differ between the two contexts.

Different operating systems and different graphics drivers may handle the schism
differently.  On Windows, it is common for the default OpenGL context to be a
permissive "best-of-both-worlds" setting in which both old and new features are
available.  On macOS, by contrast, you must commit to a given version and cannot
use legacy and modern features within the same program.

Shady is written to be compatible with both.  By default, legacy compatibility
is disabled on non-Windows platforms, where an OpenGL 3.30/GLSL 3.30 context will
be created unless you specify otherwise. This is to improve the quality of the GLSL
random-number generator used for dithering and noise generation.  If for some
reason you need to mix legacy OpenGL code into your stimulus display (as we do in
:doc:`examples/foreign-stimulus.py<examples_foreign-stimulus>`) then you should
create your `Shady.World()` with the constructor argument `legacy=True`, thereby
instructing Shady to revert to the bare bones of OpenGL 2.1/GLSL 1.2. (NB: to add
your own custom OpenGL code, you will need to install either `PyOpenGL <http://pyopengl.sourceforge.net/>`_ or 
`pyglet <https://pypi.org/project/pyglet/>`_ to gain access to the OpenGL API in Python.)

On any system, `legacy=False` makes Shady switch, under the hood, to modern drawing
commands that should be more compatible with future graphics cards. On Windows, you
might not notice any difference.  On other platforms, specifying `legacy=False`
*also* causes the default value of another option, `openglContextVersion`, to be
changed from 0 to 330.

On any system, a non-zero `openglContextVersion` value will force `legacy=False`,
and *also* cause Shady to create an OpenGL context of the specified version (330
requests OpenGL 3.3.0, 410 requests OpenGL 4.1.0, and so on). This will *disable*
support for legacy features: depending on your graphics card and its driver version
you may find, for example, that you no longer have control of the thickness of
lines that you draw, or the smoothing of points. So far in our experience of
typical Shady use-cases, there is no advantage to doing this on Windows systems,
but on macOS this is the price one has to pay for improving the quality of the
random-number generation---macOS users compare::

	python -m Shady noise --legacy=True
	python -m Shady noise --legacy=False



.. |numpy| replace:: `numpy`
.. _numpy: http://pypi.org/project/numpy

.. |pillow| replace:: `pillow`
.. _pillow: http://pypi.org/project/pillow

.. |matplotlib| replace:: `matplotlib`
.. _matplotlib: http://pypi.org/project/matplotlib

.. |ipython| replace:: `ipython`
.. _ipython: http://pypi.org/project/ipython

.. |opencv-python| replace:: `opencv-python`
.. _opencv-python: http://pypi.org/project/opencv-python

.. |pip| replace:: `pip`
.. _pip: http://pypi.org/project/pip

