Installation
============

This will take you through the basic steps to get analytix installed.

.. important::

    Python 3.7.1 or greater is required.

Install the latest version
--------------------------

It is recommended you install analytix in a virtual environment. To do this, run the following:

.. code-block:: bash

    # Windows
    > py -3.9 -m venv .venv
    > .venv\Scripts\activate
    > pip install analytix

    # Linux\macOS
    $ python3.9 -m venv .venv
    $ source ./.venv/bin/activate
    $ pip install analytix

To install analytix outside of a virtual environment instead, run the following:

.. code-block:: bash

    # Windows
    > py -3.9 -m pip install analytix

    # Linux/macOS
    $ python3.9 -m pip install analytix

Install the development version
-------------------------------

You can also install the development version by running the following (this assumes you're on Linux/macOS):

.. code-block:: bash

    $ git clone https://github.com/parafoxia/analytix
    $ cd analytix
    $ git checkout develop  # Any valid branch name can go here.
    $ python3.9 -m pip install -U .
