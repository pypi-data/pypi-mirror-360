
===================
 Built-in Commands
===================

Sideshow comes with one top-level :term:`command`, and some
:term:`subcommands<subcommand>`.

It uses `Typer`_ for the underlying CLI framework.

.. _Typer: https://typer.tiangolo.com/


``sideshow``
------------

This is the top-level command.  Its purpose is to expose subcommands
pertaining to Sideshow.

It is installed to the virtual environment in the ``bin`` folder (or
``Scripts`` on Windows):

.. code-block:: sh

   cd /path/to/venv
   bin/sideshow --help

Defined in: :mod:`sideshow.cli`

.. program-output:: sideshow --help


.. _sideshow-install:

``sideshow install``
--------------------

Install the web app, generating config files based on interactive
prompting.

Defined in: :mod:`sideshow.cli.install`

.. program-output:: sideshow install --help
