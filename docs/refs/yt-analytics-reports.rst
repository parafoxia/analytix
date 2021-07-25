YouTube analytics reports reference
###################################

YouTube analytics reports are difficult to work with. To try and combat that, this page goes over all your available options, and how they all fit together.

.. note::

    Content owner reports are not fully supported.

Dimensions
==========

Dimensions are how data is split in a report. For example, when you pass "day" as a dimension, you are telling the API to split the data by day. In doing this, instead of getting a single row containing data for the time period specified, you get a separate row for every day. Using dimensions in this way allow you to see how your channel is fairing over time, in what countries your channel has been most popular, or both simultaneously (amogst other things). Almost all dimensions can be used as filters; the possible values of each dimension are supplied when discussing filters.

.. important::

    The order in which you supply dimensions matters. Make sure you supply them in order of importance.

The list of supported dimensions, sorted in alphabetical order:

- adType
- ageGroup [#f1]_
- audienceType
- channel [#f1]_ [#f2]_
- claimedStatus [#f2]_
- country [#f1]_
- day [#f1]_
- deviceType
- elapsedVideoTimeRatio
- gender [#f1]_
- insightPlaybackLocationDetail
- insightPlaybackLocationType
- insightTrafficSourceDetail
- insightTrafficSourceType
- liveOrOnDemand
- month [#f1]_
- operatingSystem
- playlist
- province
- sharingService [#f1]_
- subscribedStatus
- uploaderType [#f1]_ [#f2]_
- video [#f1]_
- youtubeProduct

.. rubric:: footnotes

.. [#f1] Core dimension (subject to YouTube's deprecation policy)
.. [#f2] Only supported in content owner reports

Metrics
=======

Metrics can be thought of like columns (though they are distinct from columns, as dimensions also count as columns). Any metric you define is a piece of data you want to know. This allows you to slim down reports to just the information you most care about (perhaps the number of views, likes, and comments). Metrics are probably the thing you need to care least about when using analytix, as not specifying any metrics will tell analytix to request information for every available metric.

The list of supported metrics, sorted in order of representation when no metrics are explicitly supplied:

- views [#f3]_
- redViews
- comments [#f3]_
- likes [#f3]_
- dislikes [#f3]_
- videosAddedToPlaylists
- videosRemovedFromPlaylists
- shares [#f3]_
- estimatedMinutesWatched [#f3]_
- estimatedRedMinutesWatched
- averageViewDuration [#f3]_
- averageViewPercentage
- annotationClickThroughRate [#f3]_
- annotationCloseRate [#f3]_
- annotationImpressions
- annotationClickableImpressions
- annotationClosableImpressions
- annotationClicks
- annotationCloses
- cardClickRate
- cardTeaserClickRate
- cardImpressions
- cardTeaserImpressions
- cardClicks
- cardTeaserClicks
- subscribersGained [#f3]_
- subscribersLost [#f3]_
- estimatedRevenue [#f3]_
- estimatedAdRevenue
- grossRevenue
- estimatedRedPartnerRevenue
- monetizedPlaybacks
- playbackBasedCpm
- adImpressions
- cpm
- viewerPercentage [#f3]_
- audienceWatchRatio
- relativeRetentionPerformance
- playlistStarts
- viewsPerPlaylistStart
- averageTimeInPlaylist

.. [#f3] Core metric (subject to YouTube's deprecation policy)

Filters
=======

Filters...filter data (there really isn't a better way to put it!). This is especially useful if, for example, you only care about data from specific a region of the world, or only want to get data from users on a specific device type. Some reports require you to specify a filter, such as all US-centric reports which require you to set the country filter to "US", and playlist reports which require the "isCurated" filter to be set to "1" (this, confusingly, is how you tell the YouTube Analytics API you want data on playlists). All filter values are provided as strings, regardless of whether they are numerical. Casing is also important -- inconsistencies in the casing between filters are not typographical errors.

The table of supported filters and their possible values, sorted in alphabetical order by filter:

.. list-table::
   :widths: 1 5
   :header-rows: 1

   * - Filter
     - Possible values
   * - adType
     - auctionBumperInstream • auctionDisplay • auctionInstream • auctionTrueviewInslate • auctionTrueviewInstream • auctionUnknown • reservedBumperInstream • reservedClickToPlay • reservedDisplay • reservedInstream • reservedInstreamSelect • reservedMasthead • reservedUnknown • unknown
   * - ageGroup
     - age13-17 • age18-24 • age25-34 • age35-44 • age45-54 • age55-64 • age65-
   * - audienceType
     - ORGANIC • AD_INSTREAM • AD_INDISPLAY
   * - channel
     - Any channel ID
   * - claimedStatus
     - claimed
   * - continent
     - 002 • 019 • 142 • 150 • 009
   * - country
     - Any `ISO 3166-1 alpha-3 <https://www.iso.org/iso-3166-country-codes.html>`_ country code
   * - day
     - Any day in YYYY-MM-DD format
   * - deviceType
     - DESKTOP • GAME_CONSOLE • MOBILE • TABLET • TV • UNKNOWN_PLATFORM
   * - elapsedVideoTimeRatio
     - Any value (to a maximum of two significant figures) between 0.01 and 1 inclusive
   * - gender
     - male • female
   * - group
     - Any group ID
   * - insightPlaybackLocationDetail
     - Not specified
   * - insightPlaybackLocationType
     - BROWSE • CHANNEL • EMBEDDED • EXTERNAL_APP • MOBILE • SEARCH • WATCH • YT_OTHER
   * - insightTrafficSourceDetail
     - ADVERTISING • CAMPAIGN_CARD • END_SCREEN • EXT_URL • NOTIFICATION • RELATED_VIDEO • SUBSCRIBER • YT_CHANNEL • YT_OTHER_PAGE • YT_SEARCH
   * - insightTrafficSourceType
     - ADVERTISING • ANNOTATION • CAMPAIGN_CARD • END_SCREEN • EXT_URL • NO_LINK_EMBEDDED • NO_LINK_OTHER • NOTIFICATION • PLAYLIST • PROMOTED • RELATED_VIDEO • SHORTS • SUBSCRIBER • YT_CHANNEL • YT_OTHER_PAGE • YT_PLAYLIST_PAGE • YT_SEARCH
   * - isCurated
     - 1
   * - liveOrOnDemand
     - LIVE • ON_DEMAND
   * - month
     - Any month in YYYY-MM format
   * - operatingSystem
     - ANDROID • BADA • BLACKBERRY • CHROMECAST • DOCOMO • FIREFOX • HIPTOP • IOS • KAIOS • LINUX • MACINTOSH • MEEGO • NINTENDO_3DS • OTHER • PLAYSTATION • PLAYSTATION_VITA • REALMEDIA • SMART_TV • SYMBIAN • TIZEN • WEBOS • WII • WINDOWS • WINDOWS_MOBILE • XBOX
   * - playlist
     - Any playlist ID
   * - province
     - Any `ISO 3166-2 alpha-3 <https://www.iso.org/iso-3166-country-codes.html>`_ subdivision code
   * - sharingService
     - AMEBA • ANDROID_EMAIL • ANDROID_MESSENGER • ANDROID_MMS • BBM • BLOGGER • COPY_PASTE • CYWORLD • DIGG • DROPBOX • EMBED • MAIL • FACEBOOK • FACEBOOK_MESSENGER • FACEBOOK_PAGES • FOTKA • GMAIL • GOO • GOOGLEPLUS • GO_SMS • GROUPME • HANGOUTS • HI5 • HTC_MMS • INBOX • IOS_SYSTEM_ACTIVITY_DIALOG • KAKAO_STORY • KAKAO • KIK • LGE_EMAIL • LINE • LINKEDIN • LIVEJOURNAL • MENEAME • MIXI • MOTOROLA_MESSAGING • MYSPACE • NAVER • NEARBY_SHARE • NUJIJ • ODNOKLASSNIKI • OTHER • PINTEREST • RAKUTEN • REDDIT • SKYPE • SKYBLOG • SONY_CONVERSATIONS • STUMBLEUPON • TELEGRAM • TEXT_MESSAGE • TUENTI • TUMBLR • TWITTER • UNKNOWN • VERIZON_MMS • VIBER • VKONTATKE • WECHAT • WEIBO • WHATS_APP • WYKOP • YAHOO • YOUTUBE_GAMING • YOUTUBE_KIDS • YOUTUBE_MUSIC • YOUTUBE_TV
   * - subContinent
     - 014 • 017 • 015 • 018 • 011 • 029 • 013 • 021 • 005 • 143 • 030 • 034 • 035 • 145 • 151 • 154 • 039 • 155 • 053 • 054 • 057 • 061
   * - subscribedStatus
     - SUBSCRIBED • UNSUBSCRIBED
   * - uploaderType
     - self • thirdParty
   * - video
     - Any video ID
   * - youtubeProduct
     - CORE • GAMING • KIDS • UNKNOWN

Sort options
============

Sort options define how reports are sorted. When passing multiple to a single query, the report is sorted by the first column, then the second column, etc. Most reports can be sorted by any metric in either ascending or descending order, but some only support descending sorts using specific metrics.

For a list of sort options, see the list of metrics -- there are no unique sort options.

Report types
============

Report types are how analytix works out which dimensions, metrics, filters, and sort options can be used at any given time. The report type is worked out automatically based primarily on the dimensions and filters passed to the query, and many report types can overlap. In total, there are 45 different types (not including content owner reports, which are currently not fully supported).
