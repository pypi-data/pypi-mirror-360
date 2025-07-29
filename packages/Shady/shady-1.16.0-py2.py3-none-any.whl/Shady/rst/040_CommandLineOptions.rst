Command-Line Options
====================

Our :doc:`example scripts <ExampleScripts>` all use the :py:obj:`WorldConstructorCommandLine <Shady.Utilities.WorldConstructorCommandLine>`
utility. This means that when you launch them from the command-line, for example with::

	python -m Shady run custom-functions

or::

	python <path-to-package-installation-location>/Shady/examples/custom-functions.py

then in either case, the demo (here `custom-functions.py`) will support additional
optional command-line arguments. One of these is `--help`, so you can find out what other
arguments are supported. Some of them may be specific to the particular demo. But most of
them are used to determine the arguments that get passed to the `World` constructor. For
example::

	python -m Shady run custom-functions  --screen=2
	
will cause the `custom-functions` example to pass `screen=2` to the `World()` constructor
and hence to run on your second screen (perhaps you would have run
`python -m Shady screens` first, to help you decide on the correct screen number).

One command-line option, `--console`, arises from the `python -m Shady` mechanism itself
rather than the demos and their `WorldConstructorCommandLine()`.  It is supported by the
`run` and `demo` subcommands and determines the level and type of interactivity while
the script is running.

For more details, see:

	* The :py:obj:`World <Shady.World>` class constructor doc.
	* The :py:obj:`WorldConstructorCommandLine <Shady.Utilities.WorldConstructorCommandLine>` utility doc.
	* The :py:obj:`RunShadyScript <Shady.Utilities.RunShadyScript>` utility doc.
	* The output of `python -m Shady help`

