The Binary "Accelerator" Component (`ShaDyLib`)
===============================================

.. admonition:: Summary
	:class: tip

	Shady comes with an "accelerator"---a dynamic library that greatly improves its
	performance. The Shady Python package installation includes pre-built ``.dll``
	files for 32-bit Windows and 64-bit Windows, a ``.dylib`` file for macOS 10.9+,
	and a ``.so`` file for Linux on little-endian-64-bit machines. If your platform
	is not supported by these included binaries, you can build the accelerator
	yourself, from our C++ sources.

Shady works by harnessing the graphics processor (GPU) to perform, in parallel, most
of the pixel-by-pixel operations entailed in signal generation, contrast modulation,
windowing, linearization and dithering.  For most stimulus arrangements, this leaves
relatively little for the CPU to do on each frame: it just has to issue the OpenGL
commands that clear the screen and then, for each stimulus in turn, transfer a small
set of variable values from CPU to GPU.  Nonetheless this may amount to a few hundred
separate operations per frame---we'll call these the "CPU housekeeping" operations
(and we'll consider them separate from the optional further computations that can be
performed between frames to :doc:`animate <MakingPropertiesDynamic>` stimuli).

The CPU housekeeping is performed by an "engine". The earliest versions of Shady
implemented the engine in pure Python. Some of the time, this worked fine, but it was
prone to sporadic frame skips.  So we transitioned to using the "accelerator", which is
a binary engine compiled from C++ and packaged as a dynamic library called ShaDyLib.
Some binary builds of ShaDyLib are included with the Shady Python package: `.dll` files
for 32- and 64-bit Windows, a `.dylib` file for 64-bit macOS 10.9 (Mavericks, 2013) and
up, and a `.so` file for Linux running on little-endian 64-bit systems (compiled on
Ubuntu 24.04 LTS for Desktops). These are used by default where possible.  To make
the corresponding `.so` or `.dylib` file for other systems, you would need to build it
yourself from the C++ sources (see below).

The pure-Python engine is still included (as the `Shady.PyEngine` submodule) and it is
used automatically as a fallback when the accelerator is not available. But it is much
better to use the accelerator (and to attempt to compile the accelerator from source if
the dynamic library for your platform is not already part of Shady). The problem is that
Python, being a high-level dynamic interpreted language, is inefficient for performing
large numbers of simple operations. Relative to the equivalent operations compiled from
C++, Python not only requires extra time but, critically, adds a large amount of
*variability* to the time taken when running on a modern operating system that tends to
perform a lot of sporadic background tasks (the effect of these is especially noticeable
on Windows).  Hence the frequent sporadic frame skips when using the `PyEngine`, which
become much rarer when you use the accelerator.


Windowing and Rendering
-----------------------

These are two separate issues:

Windowing
	is about creating a window and an associated OpenGL context, synchronizing the
	double-buffer flipping with the display hardware's frame updates, and handling
	events such as keyboard and mouse input.
	
Rendering
	is about the OpenGL calls that comprise most of the frame-by-frame CPU
	housekeeping. Rendering is implemented in a windowing-independent way (i.e.
	without reference to the windowing environment or its particular implementation).

The `ShaDyLib` accelerator provides independent implementations of both windowing
(using the `GLFW <http://glfw.org>`_ C library) and rendering. Assuming you have the
accelerator, you have three options:

1. Use the accelerator for both windowing and rendering.  When the accelerator is
   available, this is the default option, and is highly recommended for performance
   reasons.

2. Use a different windowing environment (such as `pyglet`) and still use the
   accelerator for rendering. There is no great advantage to doing this, and there
   are disadvantages here and there (e.g. failure to take full advantage of Mac Retina
   screen resolution).

3. Do not use the accelerator at all. Fall back to the `PyEngine`, which requires a
   third-party package to expose the necessary OpenGL calls. Either `pyglet <https://pypi.org/project/pyglet/>`_  or
   `PyOpenGL <https://pypi.org/project/PyOpenGL/>`_ will work for this (`pyglet` is probably the better choice
   because, in the absence of the accelerator, you will also need it for windowing 
   anyway). As explained above, this option is not recommended if you can avoid it.

The `BackEnd()` function allows you to change the default windowing and rendering
implementations.


Building the Accelerator from Source
------------------------------------

As we mentioned above, binaries are included in the Shady download, for 32-bit
Windows, and for 64-bit Windows, macOS and Linux.  Therefore, we hope you will
not need to build the accelerator from source. However, if you need to do so
for any reason (for example to support other operating systems or operating-
system versions, provided they're running on little-endian hardware) then it
should be relatively easy.  ("Should" is every engineer's most heavily loaded
word.)

You can obtain the complete Shady source code from the master git repository
which is hosted on `Bitbucket <{repository}>`_::

	git clone {repository}

Or you can go to that URL with a browser and clickety-clickety-download-unzippety
if you really must. But there are several advantages to installing git and
then managing things with the `git` command from within the `{repo-short}` directory.
For example, it makes it very easy to get our latest updates::

    git pull

or to switch between bleeding-edge code::

    git checkout master && git merge

and the latest released version::

    git checkout origin/release --track    # the first time you switch to `release`
    
    git checkout release && git merge      # subsequent times

Your working-copy of the repository will include a copy of the Shady package itself,
inside the `python` subdirectory. You can "install" this copy as your default Shady
package if you want: first change your working directory so that you're in the
root of the working-copy (i.e. the place that contains `setup.py`) and then call::

	python -m pip install -e .
	
The `-e` flag stands for "editable copy" and this type of "installation" does not
actually copy or move any files. Instead, it merely causes whichever Python
distribution you just invoked to make a permanent record of the location of the
appropriate directory, thereby ensuring that it is found when you say `import Shady`
in subsequent sessions.

Your working-copy of the repository will also include the `accel-src` directory tree
which contains the C++ sources for the accelerator.  To build these, you need to have
`CMake <http://cmake.org>`_ installed (version 3.7+) as well as a C++ compiler.  On
Windows, the compiler we use is Visual C++, installed as part of a free ("Express" or
"Community") edition of Visual Studio 2012 or later. On macOS, we use `gcc` installed
from the "XCode Command Line Tools" package (we don't need the full-blown XCode).

The script `accel-src/devel/build/go.cmd` can be run from a Windows Command Prompt or
from a `bash` command-line (e.g. from the "Terminal" app on macOS) and will run the
entire CMake + build process. If you're on Windows, and either your OS or your Python
distribution is 32-bit, then you need to explicitly say `go.cmd Win32`. Further
details are provided in the comments at the top of the `go.cmd` script.

The accelerator has two third-party depenencies: GLEW and GLFW. GLEW is provided
as source. Binary builds of GLFW are also provided in the repository. If for any
reason you need to rebuild that GLFW library, see the instructions in
`accel-src/devel/glfw/build-notes.txt`

On Linux, we also found it necessary to install various developer tools, libraries
and headers. Here is our script for setting up our development environment for Shady,
on the basis of a fresh installation of Ubuntu 24.x LTS for Desktops::

	sudo apt-get update
	sudo apt-get install \
		git vim cmake g++ bzip2 tar                                         `# essentials for versioning Shady and building ShaDyLib`\
		libglu-dev libxrandr-dev libxi-dev libxcursor-dev libxinerama-dev   `# libraries required for building ShaDyLib`\
		libwayland-dev libx11-dev libxkbcommon-dev libgl-dev libxxf86vm-dev `# more libraries that may be required for building ShaDyLib (needed for to build its dependency libglfw.a anyway)`\
		libudev-dev libtool autotools-dev automake pkg-config curl          `# build tools and libraries required for libusb build (part of dpxmode build)`\
		python-pip  python-tk                                               `# Python 2 basics`\
		python3-pip python3-tk                                              `# Python 3 basics`\
	;
	sudo pip  install numpy matplotlib ipython pillow opencv-python pyglet pyserial   # Python 2 third-party packages
	sudo pip3 install numpy matplotlib ipython pillow opencv-python pyglet pyserial   # Python 3 third-party packages

	# get Shady
	mkdir -p ~/code
	cd ~/code
	git clone https://bitbucket.org/snapproject/shady-gitrepo
	cd shady-gitrepo
	
	# "install" Shady as an editable package 
	sudo pip  install -e .
	sudo pip3 install -e .
	
	# build the accelerator
	./accel-src/devel/build/go.cmd

	# build and incorporate the mode-changer utility for the ViewPixx monitor
	./dpxmode-src/build.cmd
	./dpxmode-src/release.cmd
	
	# In addition, to use Shady on the primary screen, we had to auto-hide the
	# Ubuntu dock (Applications -> Settings -> Dock -> Auto-hide the Dock) and
	# and the top bar (search for and install the "Hide Top Bar" extension)
	

A successfully built shared library will end up in the `accel-src/release/` directory.
What do you do with it then? Well:

* If you are using the repository copy of the Shady Python package (i.e. you have
  performed `python -m pip install -e .` as described above, or you are working in the
  `python` directory next-door to `accel-src` when you start Python) then Shady will
  be smart enough, by default, to look for the accelerator in ``../accel-src/release/``
  and to prefer it over any copy that it finds "bundled" in its own package directory.
  You can also explicitly control which version it prefers, by supplying either
  `acceleration='devel'` or `acceleration='bundled'` as a keyword argument, either to
  `Shady.BackEnd()` or to the `Shady.World()` constructor.

* You can verify which version of the accelerator is being loaded by looking under
  `ShaDyLib` in the output of the `.ReportVersions()` method of an instantiated `World`,
  or failing that the global `Shady.ReportVersions()` function.

* Finally, maybe you would like to move the newly-built shared library into the "bundled"
  location within the accompanying Shady package directory? If so, you can run
  `python accel-src/devel/build/release.cmd`. This will copy all the relevant material
  from `accel-src/release/` into the `python/Shady/accel` subdirectory, and remove the
  dynamic libraries from `accel-src/release/`.
