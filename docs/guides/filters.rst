Understanding filters
#####################

Overview
========

Filters allow for unwanted data to be omitted, leaving only the relevant data. This is useful when you only want data for a specific demographic, or in some cases, when setting what type of information you want. The vast majority of report types do not require you to provide a filter, though many report types can accept multiple filters.

Valid filters
=============

The table of supported filters and their possible values, sorted in alphabetical order by filter:

.. list-table::
   :widths: 1 5
   :header-rows: 1

   * - Filter
     - Possible values
   * - adType
     - * auctionBumperInstream
       * auctionDisplay
       * auctionInstream
       * auctionTrueviewInslate
       * auctionTrueviewInstream
       * auctionUnknown
       * reservedBumperInstream
       * reservedClickToPlay
       * reservedDisplay
       * reservedInstream
       * reservedInstreamSelect
       * reservedMasthead
       * reservedUnknown
       * unknown
   * - ageGroup
     - * age13-17
       * age18-24
       * age25-34
       * age35-44
       * age45-54
       * age55-64
       * age65-
   * - audienceType
     - * ORGANIC
       * AD_INSTREAM
       * AD_INDISPLAY
   * - channel
     - Any channel ID
   * - claimedStatus
     - * claimed
   * - continent
     - * 002
       * 019
       * 142
       * 150
       * 009
   * - country
     - Any `ISO 3166-1 alpha-3 <https://www.iso.org/iso-3166-country-codes.html>`_ country code
   * - day
     - Any day in YYYY-MM-DD format
   * - deviceType
     - * DESKTOP
       * GAME_CONSOLE
       * MOBILE
       * TABLET
       * TV
       * UNKNOWN_PLATFORM
   * - elapsedVideoTimeRatio
     - Any value (to a maximum of two significant figures) between 0.01 and 1 inclusive
   * - gender
     - * female
       * male
       * user_specified [#f4]_
   * - group
     - Any group ID
   * - insightPlaybackLocationDetail
     - Not specified
   * - insightPlaybackLocationType
     - * BROWSE
       * CHANNEL
       * EMBEDDED
       * EXTERNAL_APP
       * MOBILE
       * SEARCH
       * WATCH
       * YT_OTHER
   * - insightTrafficSourceDetail
     - * ADVERTISING
       * CAMPAIGN_CARD
       * END_SCREEN
       * EXT_URL
       * NOTIFICATION
       * RELATED_VIDEO
       * SUBSCRIBER
       * YT_CHANNEL
       * YT_OTHER_PAGE
       * YT_SEARCH
   * - insightTrafficSourceType
     - * ADVERTISING
       * ANNOTATION
       * CAMPAIGN_CARD
       * END_SCREEN
       * EXT_URL
       * NO_LINK_EMBEDDED
       * NO_LINK_OTHER
       * NOTIFICATION
       * PLAYLIST
       * PROMOTED
       * RELATED_VIDEO
       * SHORTS
       * SUBSCRIBER
       * YT_CHANNEL
       * YT_OTHER_PAGE
       * YT_PLAYLIST_PAGE
       * YT_SEARCH
   * - isCurated
     - * 1
   * - liveOrOnDemand
     - * LIVE
       * ON_DEMAND
   * - month
     - Any month in YYYY-MM format
   * - operatingSystem
     - * ANDROID
       * BADA
       * BLACKBERRY
       * CHROMECAST
       * DOCOMO
       * FIREFOX
       * HIPTOP
       * IOS
       * KAIOS
       * LINUX
       * MACINTOSH
       * MEEGO
       * NINTENDO_3DS
       * OTHER
       * PLAYSTATION
       * PLAYSTATION_VITA
       * REALMEDIA
       * SMART_TV
       * SYMBIAN
       * TIZEN
       * WEBOS
       * WII
       * WINDOWS
       * WINDOWS_MOBILE
       * XBOX
   * - playlist
     - Any playlist ID
   * - province
     - Any `ISO 3166-2 alpha-3 <https://www.iso.org/iso-3166-country-codes.html>`_ subdivision code
   * - sharingService
     - * AMEBA
       * ANDROID_EMAIL
       * ANDROID_MESSENGER
       * ANDROID_MMS
       * BBM
       * BLOGGER
       * COPY_PASTE
       * CYWORLD
       * DIGG
       * DROPBOX
       * EMBED
       * MAIL
       * FACEBOOK
       * FACEBOOK_MESSENGER
       * FACEBOOK_PAGES
       * FOTKA
       * GMAIL
       * GOO
       * GOOGLEPLUS
       * GO_SMS
       * GROUPME
       * HANGOUTS
       * HI5
       * HTC_MMS
       * INBOX
       * IOS_SYSTEM_ACTIVITY_DIALOG
       * KAKAO_STORY
       * KAKAO
       * KIK
       * LGE_EMAIL
       * LINE
       * LINKEDIN
       * LIVEJOURNAL
       * MENEAME
       * MIXI
       * MOTOROLA_MESSAGING
       * MYSPACE
       * NAVER
       * NEARBY_SHARE
       * NUJIJ
       * ODNOKLASSNIKI
       * OTHER
       * PINTEREST
       * RAKUTEN
       * REDDIT
       * SKYPE
       * SKYBLOG
       * SONY_CONVERSATIONS
       * STUMBLEUPON
       * TELEGRAM
       * TEXT_MESSAGE
       * TUENTI
       * TUMBLR
       * TWITTER
       * UNKNOWN
       * VERIZON_MMS
       * VIBER
       * VKONTATKE
       * WECHAT
       * WEIBO
       * WHATS_APP
       * WYKOP
       * YAHOO
       * YOUTUBE_GAMING
       * YOUTUBE_KIDS
       * YOUTUBE_MUSIC
       * YOUTUBE_TV
   * - subContinent
     - * 014
       * 017
       * 015
       * 018
       * 011
       * 029
       * 013
       * 021
       * 005
       * 143
       * 030
       * 034
       * 035
       * 145
       * 151
       * 154
       * 039
       * 155
       * 053
       * 054
       * 057
       * 061
   * - subscribedStatus
     - * SUBSCRIBED
       * UNSUBSCRIBED
   * - uploaderType
     - * self
       * thirdParty
   * - video
     - Any video ID
   * - youtubeProduct
     - * CORE
       * GAMING
       * KIDS
       * UNKNOWN

.. [#f4] This value can only be used from 11 Aug 2022.

For more information about what each filter does, look at the `official documentation <https://developers.google.com/youtube/analytics/dimensions#filters>`_.

Important filters
=================

``isCurated``
-------------

To get information on playlists, this value needs to be set to ``1`` (as a string). If this is not provided, information on videos will be collected instead.

.. code-block:: python

    filters={"isCurated": "1"}

Special cases
=============

``country``
-----------

This must be set to one of the following values when ``province`` is provided as a dimension:

* ``US``

``insightPlaybackLocationType``
-------------------------------

This must be set to one of the following values when ``insightPlaybakLocationDetail`` is provided as a dimension:

* ``EMBEDDED``

``insightTrafficSourceType``
----------------------------

This must be set to one of the following values when ``insightTrafficSourceDetail`` is provided as a dimension:

* ``ADVERTISING``
* ``CAMPAIGN_CARD``
* ``END_SCREEN``
* ``EXT_URL``
* ``NOTIFICATION``
* ``RELATED_VIDEO``
* ``SUBSCRIBER``
* ``YT_CHANNEL``
* ``YT_OTHER_PAGE``
* ``YT_SEARCH``

``video``
---------

Normally, this filter can accept a comma-separated list of video IDs. This is not the case when ``elapsedVideoTimeRatio`` is provided as a dimension.
