Example Scripts
===============

The following example scripts are included as part of the Shady package.
They can be run conventionally like any normal Python script.
Alternatively, you can explore them interactively piece-by-piece with
the `demo` subcommand, like so::

    python -m Shady demo {stem}

From inside Python, this is equivalent to:

.. code:: python

    from Shady import RunShadyScript, PackagePath
    RunShadyScript( PackagePath( '{shortFilePath}' ) )

List of examples
----------------

An annotated version of the full list of examples can be obtained by
typing::

	python -m Shady list

The source code of the examples can be browsed below:

.. toctree::
      
