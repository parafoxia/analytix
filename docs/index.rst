Documentation
#############

.. image:: https://img.shields.io/pypi/v/analytix.svg
   :alt: PyPI version
   :target: https://pypi.python.org/pypi/analytix/

.. image:: https://img.shields.io/pypi/status/analytix
   :alt: PyPI - Status
   :target: https://pypi.python.org/pypi/analytix/

.. image:: https://pepy.tech/badge/analytix
   :alt: Downloads
   :target: https://pepy.tech/project/analytix

.. image:: https://img.shields.io/github/last-commit/parafoxia/analytix
   :alt: GitHub last commit
   :target: https://github.com/parafoxia/analytix

.. image:: https://img.shields.io/github/license/parafoxia/analytix.svg
   :alt: License
   :target: https://github.com/parafoxia/analytix/blob/main/LICENSE

|

.. image:: https://github.com/parafoxia/analytix/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/parafoxia/analytix/actions/workflows/ci.yml
   :alt: CI

.. image:: https://img.shields.io/readthedocs/analytix
   :alt: Read the Docs
   :target: https://analytix.readthedocs.io/en/latest/index.html

.. image:: https://api.codeclimate.com/v1/badges/8819bdebb2d4aa8dfcb7/maintainability
   :alt: Maintainability
   :target: https://codeclimate.com/github/parafoxia/analytix/maintainability

.. image:: https://api.codeclimate.com/v1/badges/8819bdebb2d4aa8dfcb7/test_coverage
   :alt: Test Coverage
   :target: https://codeclimate.com/github/parafoxia/analytix/test_coverage

|

A simple yet powerful wrapper for the YouTube Analytics API.

.. important::

   These docs are for a release candidate version of analytix. You might be interested in `version 2.2.0's documentation <https://analytix.readthedocs.io/en/v2.2.0.post0/>`_.

What does *analytix* do?
========================

The YouTube Studio provides a fantastic interface where creators can view some incredibly detailed analytics for their channel. However, there's no way to perform programmatical operations on the data to do some proper analysis on it. This is where *analytix* comes in.

The process of analysing data on the YouTube Studio is comprised of two steps:

1. Retrieving the data to be analysed and visualised
2. Presenting that data to the user

*analytix* aims to handle step one as comprehensively as possible, allowing analysts to use tools such as *pandas* and *Matplotlib* to work on the data without having to faff around with Google's offerings.

Features
========

- Pythonic syntax lets you feel right at home
- Dynamic error handling saves hours of troubleshooting, and makes sure only valid requests count toward your API quota
- A clever interface allows you to make multiple requests across multiple sessions without reauthorising
- Extra support allows the native saving of CSV files and conversion to DataFrame objects
- Easy enough for beginners, but powerful enough for advanced users

Contents
========

.. toctree::
    :maxdepth: 1
    :caption: Guides

    guides/console
    guides/dimensions
    guides/filters
    guides/metrics
    guides/sort_options
    guides/report_types

.. toctree::
    :maxdepth: 1
    :caption: Data and functions

    api/analytix
    api/ux
    api/errors
    api/oauth

.. toctree::
    :maxdepth: 1
    :caption: Classes

    api/analytics
    api/async_analytics
    api/reports
    api/secrets
    api/tokens
