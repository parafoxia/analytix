Understanding sort options
##########################

Overview
========

Sort options control how the report is sorted. This is useful when you want data sorted by a particular metric instead of the default.

Multiple sort options can be used in any given request, though the order matters. For example, if you were to pass these sort options...

.. code-block:: python

    sort_options=["views", "likes", "comments"]

...the report will be sorted by views first, then any remaining identical rows will be sorted by likes, then any still remaining identical rows will be sorted by comments.

By default, all sort options sort in ascending order. To sort in descending order, prefix the name of the sort option with a hyphen (-):

.. code-block:: python

    sort_options=["-views", "-likes", "-comments"]

Ascending and descending sort options can be provided in the same report.

Generally, the list of valid sort options matches the list of metrics, and no sort options need to be provided. However, this is not always the case; in these rare instances, sort options are compulsory, and must be descending. analytix will tell you when this is the case.

Valid sort options
==================

See the :doc:`list of valid metrics <./metrics>`.
