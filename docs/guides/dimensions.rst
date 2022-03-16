Understanding dimensions
########################

Overview
========

Dimensions provide a means to split data into smaller parts. This is useful when you wish to see how your channel is performing over time, or compare the statistics for one attribute against those for another. Most report types require at least one dimension to be provided, and some report types can accept more.

Here is some example data:

.. list-table::
   :widths: 1 3 3 3
   :header-rows: 1

   * -
     - views
     - likes
     - comments
   * - 1
     - 1 000 000
     - 100 000
     - 20 000

This data contains four columns (the ID column, and three metrics), and one row. This row represents the cumulative data over the course of twelve months. While this is useful if you want to know the totals, there is not a lot we can take from it. To remedy this, we can use the "month" dimension. After doing so, the data looks like this:

.. list-table::
   :widths: 1 3 3 3 3
   :header-rows: 1

   * -
     - month
     - views
     - likes
     - comments
   * - 1
     - 2021-01
     - 92 961
     - 12 460
     - 1 232
   * - 2
     - 2021-02
     - 32 947
     - 7 434
     - 2 124
   * - 3
     - 2021-03
     - 25 949
     - 4 006
     - 217
   * - 4
     - 2021-04
     - 196 356
     - 14 541
     - 2 169
   * - 5
     - 2021-05
     - 89 804
     - 3 145
     - 1 467
   * - 6
     - 2021-06
     - 66 140
     - 10 087
     - 2 509
   * - 7
     - 2021-07
     - 43 045
     - 13 448
     - 1 156
   * - 8
     - 2021-08
     - 156 670
     - 10 972
     - 2 480
   * - 9
     - 2021-09
     - 52 414
     - 3 035
     - 2 240
   * - 10
     - 2021-10
     - 142 657
     - 11 400
     - 1 716
   * - 11
     - 2021-11
     - 93 453
     - 8 334
     - 2 602
   * - 12
     - 2021-12
     - 7 604
     - 1 138
     - 88

As you can see, doing this has added an extra column (month), as well as split the original row into twelve separate ones. Using this, we can see that our channel performed the best in April, and the worst in December. It might be worth seeing what sort of content was put out in April (as well as August and November), and trying to do more of that going forward.

For report types that allow it, we can even split the data further; lets add "subscribedStatus" as a dimension (the below data has been truncated for brevity):

.. list-table::
   :widths: 1 3 3 3 3 3
   :header-rows: 1

   * -
     - month
     - subscribedStatus
     - views
     - likes
     - comments
   * - 1
     - 2021-01
     - SUBSCRIBED
     - 32 725
     - 5 768
     - 35
   * - 2
     - 2021-01
     - UNSUBSCRIBED
     - 60 236
     - 6 692
     - 1 197
   * - 3
     - 2021-02
     - SUBSCRIBED
     - 7 601
     - 1 274
     - 633
   * - 4
     - 2021-02
     - UNSUBSCRIBED
     - 25 346
     - 6 160
     - 1 491
   * - 5
     - 2021-03
     - SUBSCRIBED
     - 6 360
     - 343
     - 95
   * - 6
     - 2021-03
     - UNSUBSCRIBED
     - 19 509
     - 3 663
     - 122
   * - ...
     - ...
     - ...
     - ...
     - ...
     - ...

Each month now has two rows, and the metrics for subscribed and unsubscribed viewers are now viewable. This data shows that our channel is being viewed by more unsubscribed viewers than subscribed ones, which is to be expected with any channel with at least a few thousand subscribers. January received a lot more likes from subscribed viewers than other months, so it might be worth looking at why that was.

Valid dimensions
================

Below is a list of available dimensions. While this list is sorted alphabetically, the order in which you supply dimensions **does** matter; make sure you supply them in order of importance.

* adType
* ageGroup [#f1]_
* audienceType
* channel [#f1]_ [#f2]_
* claimedStatus [#f2]_
* country [#f1]_
* day [#f1]_
* deviceType
* elapsedVideoTimeRatio
* gender [#f1]_
* insightPlaybackLocationDetail
* insightPlaybackLocationType
* insightTrafficSourceDetail
* insightTrafficSourceType
* liveOrOnDemand
* month [#f1]_
* operatingSystem
* playlist
* province
* sharingService [#f1]_
* subscribedStatus
* uploaderType [#f1]_ [#f2]_
* video [#f1]_
* youtubeProduct

.. rubric::

.. [#f1] Core dimension (subject to YouTube's deprecation policy)
.. [#f2] Only supported in content owner reports

For more information about what each dimension does, look at the `official documentation <https://developers.google.com/youtube/analytics/dimensions#Dimensions>`_.
