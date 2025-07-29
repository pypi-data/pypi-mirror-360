Installing the Shady Package
============================

.. admonition:: Summary
	:class: tip
	
	::
	
		python -m pip install shady
		python -m Shady demo showcase
	
	
Shady is a **Python** package. Python is a powerful, intuitive language,
although it can be `difficult to install <https://xkcd.com/1987>`_. Fortunately, it is worth
the one-time effort required to set up.

Out of the box, Shady should work on typical modern Windows and macOS systems
running either Python 2.7 or Python 3.4+. Other systems may be supportable
with a little extra effort.  Real-time performance is optimized on Windows;
anywhere else, your mileage may vary more. See the :doc:`Compatibility`
documentation for more details.

If you already have a Python environment that you use for development
---------------------------------------------------------------------

The primary and recommended way to get Shady is to use the |pip|_ package
manager. You should already have this, if your Python version is reasonably
up-to-date (Python 2 versions 2.7.9 and up, or Python 3 versions 3.4 and up).
If not, see the `pip installation instructions <https://pip.pypa.io/en/stable/installing/>`_.
Assuming you have |pip|_, the following command will install Shady::

	python -m pip install Shady

This will automatically download the latest distribution
from its home at http://pypi.python.org/pypi/shady , and install it.
It will also automatically install the :ref:`recommended third-party packages <PythonRequirements>`
(`numpy`, `pillow`, `matplotlib`, and `ipython`) if you do not already
have them. (If you do not want this to happen, you can explicitly prevent
it by adding the `--no-dependencies` flag.)

Test your Shady installation using the interactive script :doc:`examples/showcase.py <examples_showcase>`::

	python -m Shady demo showcase


If you are new to Python development
------------------------------------

macOS and Linux distributions come with Python included. However, since other parts
of the OS rely on it, your system manages the packages that it contains. Therefore,
for your own development work, it is advisable to have a completely separate
installation of Python. For scientists, the Anaconda_ distribution is a good choice.

On Windows, Python doesn't ship as part of the operating system, but there are
many ways to install it. If you find that you already have a Python installation,
no integral part of the OS itself will be relying on it, but you should still 
double-check that there are no third-party tools or applications that use it, before 
you make any changes. If in doubt then, as for other operating systems, it may be a 
good idea to install a clean separate Python distribution for your development work. 
And again, Anaconda_ is a good choice.

Follow these instructions if you just want to get going with Shady as quickly
as possible and aren't familiar with the many ways to install Python.

#. Install an Anaconda_ distribution of Python. We recommend installing a 64-bit
   **Python 3** (at the time of writing the latest release is 3.7). But if you have
   specific reasons for needing Python 2, Shady is also compatible with Python 2.7.

   **OR:**

   If you want to avoid installing Anaconda_'s giant 3 GB library of
   third-party packages, you can download the 50 MB bare-bones Miniconda_
   version instead, and install Shady's :ref:`recommended third-party packages <PythonRequirements>`
   yourself (see below).

#. Launch the **Anaconda Prompt**, which is simply a command prompt that
   starts off inside your new Python environment.

#. If you installed the bare-bones Miniconda_, install Shady's four basic
   recommended dependencies yourself, using the following command::

      python -m conda install  numpy pillow matplotlib ipython

#. (Optional) If you want to use Shady's video playback and recording features,
   you will need to install one more package, |opencv|_, which (at the
   time of writing) is available via conda for some Python versions::

      python -m conda install  opencv

   but if that is unavailable or reports a conflict, you can fall back to
   using the more standard Python package manager, |pip|_ (note the change
   to the package name)::

      python -m pip install  opencv-python

#. Install Shady, also using |pip|_::

      python -m pip install  Shady

#. That's it! Experience some of Shady's numerous features with the
   interactive script :doc:`examples/showcase.py <examples_showcase>` by typing::

      python -m Shady demo showcase


Using the right Python
----------------------

As explained above, any system may have multiple Python distributions.
And any Python distribution may have multiple "virtual environments"
which are separate silos into which you can install independent sets
of packages. Anaconda_ distributions even have the ability to manage
and switch between different versions of the Python interpreter
itself in different environments.

All of this means that, before you type `python` at a system command
prompt, you should take care to ensure that it will launch the
version/configuration of Python that you intend. (This in turn means
that there is no one-size-fits-all set of instructions for installing
a given Python package, which explains why this page is so long...)

Anaconda distributions come with a script called `activate` that
allows you to deal with this issue. You would call this once at the
beginning of your console session, and it will configure your `PATH`
and other environment variables for the remainder of the session,
such that the Anaconda version of Python answers when you call `python`.
On Windows that looks like::

	> call C:\PATH\TO\ANACONDA\Scripts\activate.bat

and on others::

	$ source /PATH/TO/ANACONDA/bin/activate

By default this puts you in an Anaconda environment called `root`. But
if you have set up other environments, you can pass the name of another
environment to the `activate` script in order to switch to it.

On Windows, the even-simpler way is just to double-click on the shortcut
to the **Anaconda Prompt**, which will open a console window and
perform the `activate` step automatically. We recommend using the
Anaconda Prompt whenever you use Python interactively. 

If you are using a non-Anaconda distribution of Python, you may have
to roll your own solution for configuring the `PATH` variable
appropriately.

Updating your Shady installation
--------------------------------

If you installed with `pip` as above, then the following command is
recommended for updating::

      python -m pip install --upgrade Shady --no-deps

(you can omit `--no-deps` if you don't mind it also upgrading Shady's various
third-party dependencies).



.. _Anaconda: https://www.anaconda.com/download/
.. _Miniconda: https://conda.io/miniconda.html

.. |opencv-python| replace:: `opencv-python`
.. _opencv-python: http://pypi.org/project/opencv-python

.. |opencv| replace:: `opencv`
.. _opencv: http://pypi.org/project/opencv-python

.. |pip| replace:: `pip`
.. _pip: http://pypi.org/project/pip

