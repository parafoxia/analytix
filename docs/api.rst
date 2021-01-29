.. currentmodule:: analytix

API Reference
=============

.. seealso::

    This document only outlines the parts of the API designed for you to use. To view the base classes, see the documentation for the :doc:`abstract base classes<./abc>`.

Version Info
------------

.. data:: __version__

    The currently installed analytix version, represented in :pep:`440` format.

Exceptions
----------

.. autoclass:: errors.AnalytixError

.. autoclass:: errors.NoAuthorisedService

.. autoclass:: errors.ServiceAlreadyExists

.. autoclass:: errors.IncompleteRequest

.. autoclass:: errors.InvalidRequest

YouTube
-------

.. autoclass:: youtube.YouTubeService
    :members:

.. autoclass:: youtube.BasicYouTubeAnalytics
    :members:
    :inherited-members:

.. autoclass:: youtube.TimeBasedYouTubeAnalytics
    :members:
    :inherited-members:
