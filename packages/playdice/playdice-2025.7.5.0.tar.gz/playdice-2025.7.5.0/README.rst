playdice
========

Simplistically play dice with the command-line arguments

Example usage
-------------

.. code-block:: bash

    $ dice -h
    usage: dice [-h] [-e EYES] [items ...]

    Play dice with the command-line arguments. When no arguments are given, simulate casting a die.

    positional arguments:
      items            the items to pseudo-randomly select from (default: None)

    options:
      -h, --help       show this help message and exit
      -e, --eyes EYES  the number of eyes of the die (default: 6)
    $ dice
    3
    $ dice a b c
    b

In a folder full of items, one may be pseudo-randomly selected by saying

.. code-block:: bash

    $ dice *
    playdice-2025.7.5.0-py3-none-any.whl

Installation
------------

The `project <https://pypi.org/project/playdice/>`_ is on PyPI, so simply run

.. code-block:: bash

    python -m pip install playdice

or

.. code-block:: bash

    python -m pip install playdice[colour]

for colour support on the terminal.
