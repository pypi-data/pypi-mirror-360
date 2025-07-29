============
Shady {version}
============

Welcome to Shady.  Shady is for programmers who work in neuroscience,
especially vision science. It is a two-dimensional graphics engine and 
Python framework, for generating and presenting psychophysically-accurate
visual stimuli, and for manipulating them in real time with minimal CPU
usage and minimal "boilerplate" coding.  For an outline of Shady's
structure and features, see the ":doc:`auto/Overview`" topic documentation.

.. NB: ignore sphinx's `WARNING: unknown document: auto/Overview` (and others, below) - it's referenced like that because this particular document is "included" in the index.rst, at the parent level


To download and install the Python package:
-------------------------------------------
	
* The short answer: `python -m pip install shady`
* The long answer: see the ":doc:`auto/Installation`" topic documentation.


To get started:
---------------

* To run an interactive tour of the main features: `python -m Shady demo showcase`
* To get more information about that demo (such as the command-line options
  it supports): `python -m Shady help showcase` 
* To see a list of other similar demos: `python -m Shady list`


To learn more:
--------------

* Class and method docstrings---e.g. `help(Shady.World)` or `help(Shady.Screens)`
  from within Python (or better, if you are using IPython: `Shady.World?` etc.)
* For topic documentation: docstrings of objects inside the `Shady.Documentation`
  submodule---e.g. `help(Shady.Documentation.PreciseControlOfLuminance)`
* It's also all on {homepage}


To ask questions:
-----------------

* You can ask programming questions on stackoverflow, using the `[shady]` tag
  (https://stackoverflow.com/questions/tagged/shady )
* If an issue is confirmed to be a technical problem or bug, you can submit
  details at {tracker}


To cite Shady:
--------------

When reporting any study in which you used Shady, please cite:

* {indent[  citation]} ::

      {indent[      bibtex]}
  
  :download:`A pre-print is also available <Hill_Mooney_Ryklin_Prusky_2019_JNeuroscienceMethods.pdf>` on {homepage}
   
