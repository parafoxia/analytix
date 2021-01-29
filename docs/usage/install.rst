Installation
============

This will take you through the basic steps to get analytix installed.

.. important::

    Python 3.6 or greater is required.

Install the latest version
--------------------------

You can install the latest version of analytix using the following command:

.. code-block:: bash

    # Linux/macOS
    python3 -m pip install -U analytix

    # Windows
    py -3 -m pip install -U analytix

    # In a virtual environment
    pip install analytix

Install the development version
-------------------------------

You can also install the development version by running the following (this example assumes you're on Linux/macOS):

.. code-block:: bash

    $ git clone https://github.com/parafoxia/analytix
    $ cd analytix
    $ git checkout develop
    $ python3 -m pip install -U .
