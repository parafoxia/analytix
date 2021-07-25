Installing analytix
###################

This section will go through how to install analytix on your system.

.. important ::

    Python 3.6.0 or greater is required. There is no Python 2 support.

Creating a virtual environment
==============================

A virtual environment allows you to contain a project's dependencies in a way that means no dependencies conflict with other projects. It is recommended that you create a virtual environment when working with analytix. To do this, run the following commands:

Linux/macOS/UNIX
----------------

.. code-block :: bash

    python3 -m venv .venv
    source ./.venv/bin/activate

Windows
-------

.. code-block :: bash

    py -3 -m venv .venv
    .venv\Scripts\activate

Installing the lastest stable version
=====================================

You can install the latest version of analytix by using the following command:

.. code-block :: bash

    pip install analytix

Installing other versions
=========================

To install a specific version (for example, if you want to try the newest development releases or have a project that relies on version 1 of analytix), use the following command:

.. code-block :: bash

    pip install analytix==1.2.2
    # or...
    pip install analytix==2.0.0.dev7
    # etc.

.. warning ::

    Development versions may be unstable, and thus unsuitable for production environments.

Installing from source
======================

You can also install analytix from source if you want to. Using this method, you can pull from a specific branch, like the :code:`develop` or :code:`release/1.2.2` to install a version different from the latest stable one. You can do this using the following command:

.. code-block:: bash

    pip install git+https://github.com/parafoxia/analytix.git@branch_name
