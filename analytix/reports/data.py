# Copyright (c) 2021-present, Ethan Henderson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__all__ = (
    "COUNTRIES",
    "SUBDIVISIONS",
    "CURRENCIES",
    "DEPRECATED_DIMENSIONS",
    "CORE_DIMENSIONS",
    "CONTENT_OWNER_DIMENSIONS",
    "ALL_DIMENSIONS",
    "VALID_FILTER_OPTIONS",
    "ALL_FILTERS",
    "CORE_METRICS",
    "ALL_METRICS_ORDERED",
    "ALL_METRICS",
    "ALL_VIDEO_METRICS",
    "ALL_PROVINCE_METRICS",
    "SUBSCRIPTION_METRICS",
    "LESSER_SUBSCRIPTION_METRICS",
    "LIVE_PLAYBACK_DETAIL_METRICS",
    "VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS",
    "LOCATION_AND_TRAFFIC_METRICS",
    "ALL_PLAYLIST_METRICS",
    "LOCATION_AND_TRAFFIC_PLAYLIST_METRICS",
    "LOCATION_AND_TRAFFIC_SORT_OPTIONS",
    "TOP_VIDEOS_SORT_OPTIONS",
    "TOP_VIDEOS_EXTRA_SORT_OPTIONS",
    "LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS",
)

COUNTRIES = {
    "AW",
    "AF",
    "AO",
    "AI",
    "AX",
    "AL",
    "AD",
    "AE",
    "AR",
    "AM",
    "AS",
    "AQ",
    "TF",
    "AG",
    "AU",
    "AT",
    "AZ",
    "BI",
    "BE",
    "BJ",
    "BQ",
    "BF",
    "BD",
    "BG",
    "BH",
    "BS",
    "BA",
    "BL",
    "BY",
    "BZ",
    "BM",
    "BO",
    "BR",
    "BB",
    "BN",
    "BT",
    "BV",
    "BW",
    "CF",
    "CA",
    "CC",
    "CH",
    "CL",
    "CN",
    "CI",
    "CM",
    "CD",
    "CG",
    "CK",
    "CO",
    "KM",
    "CV",
    "CR",
    "CU",
    "CW",
    "CX",
    "KY",
    "CY",
    "CZ",
    "DE",
    "DJ",
    "DM",
    "DK",
    "DO",
    "DZ",
    "EC",
    "EG",
    "ER",
    "EH",
    "ES",
    "EE",
    "ET",
    "FI",
    "FJ",
    "FK",
    "FR",
    "FO",
    "FM",
    "GA",
    "GB",
    "GE",
    "GG",
    "GH",
    "GI",
    "GN",
    "GP",
    "GM",
    "GW",
    "GQ",
    "GR",
    "GD",
    "GL",
    "GT",
    "GF",
    "GU",
    "GY",
    "HK",
    "HM",
    "HN",
    "HR",
    "HT",
    "HU",
    "ID",
    "IM",
    "IN",
    "IO",
    "IE",
    "IR",
    "IQ",
    "IS",
    "IL",
    "IT",
    "JM",
    "JE",
    "JO",
    "JP",
    "KZ",
    "KE",
    "KG",
    "KH",
    "KI",
    "KN",
    "KR",
    "KW",
    "LA",
    "LB",
    "LR",
    "LY",
    "LC",
    "LI",
    "LK",
    "LS",
    "LT",
    "LU",
    "LV",
    "MO",
    "MF",
    "MA",
    "MC",
    "MD",
    "MG",
    "MV",
    "MX",
    "MH",
    "MK",
    "ML",
    "MT",
    "MM",
    "ME",
    "MN",
    "MP",
    "MZ",
    "MR",
    "MS",
    "MQ",
    "MU",
    "MW",
    "MY",
    "YT",
    "NA",
    "NC",
    "NE",
    "NF",
    "NG",
    "NI",
    "NU",
    "NL",
    "NO",
    "NP",
    "NR",
    "NZ",
    "OM",
    "PK",
    "PA",
    "PN",
    "PE",
    "PH",
    "PW",
    "PG",
    "PL",
    "PR",
    "KP",
    "PT",
    "PY",
    "PS",
    "PF",
    "QA",
    "RE",
    "RO",
    "RU",
    "RW",
    "SA",
    "SD",
    "SN",
    "SG",
    "GS",
    "SH",
    "SJ",
    "SB",
    "SL",
    "SV",
    "SM",
    "SO",
    "PM",
    "RS",
    "SS",
    "ST",
    "SR",
    "SK",
    "SI",
    "SE",
    "SZ",
    "SX",
    "SC",
    "SY",
    "TC",
    "TD",
    "TG",
    "TH",
    "TJ",
    "TK",
    "TM",
    "TL",
    "TO",
    "TT",
    "TN",
    "TR",
    "TV",
    "TW",
    "TZ",
    "UG",
    "UA",
    "UM",
    "UY",
    "US",
    "UZ",
    "VA",
    "VC",
    "VE",
    "VG",
    "VI",
    "VN",
    "VU",
    "WF",
    "WS",
    "YE",
    "ZA",
    "ZM",
    "ZW",
}

SUBDIVISIONS = {
    "US-OH",
    "US-IN",
    "US-OK",
    "US-KS",
    "US-OR",
    "US-KY",
    "US-PA",
    "US-LA",
    "US-AK",
    "US-PR",
    "US-MA",
    "US-AL",
    "US-RI",
    "US-MD",
    "US-AR",
    "US-SC",
    "US-ME",
    "US-AS",
    "US-SD",
    "US-MI",
    "US-AZ",
    "US-TN",
    "US-MN",
    "US-CA",
    "US-TX",
    "US-MO",
    "US-CO",
    "US-UM",
    "US-MP",
    "US-CT",
    "US-UT",
    "US-MS",
    "US-DC",
    "US-VA",
    "US-MT",
    "US-DE",
    "US-VI",
    "US-NC",
    "US-FL",
    "US-VT",
    "US-ND",
    "US-GA",
    "US-WA",
    "US-NE",
    "US-GU",
    "US-WI",
    "US-NH",
    "US-HI",
    "US-WV",
    "US-NJ",
    "US-IA",
    "US-WY",
    "US-NM",
    "US-ID",
    "US-NV",
    "US-IL",
    "US-NY",
}

CURRENCIES = {
    "AED",
    "AFN",
    "ALL",
    "AMD",
    "ANG",
    "AOA",
    "ARS",
    "AUD",
    "AWG",
    "AZN",
    "BAM",
    "BBD",
    "BDT",
    "BGN",
    "BHD",
    "BIF",
    "BMD",
    "BND",
    "BOB",
    "BRL",
    "BSD",
    "BTN",
    "BWP",
    "BYN",
    "BZD",
    "CAD",
    "CDF",
    "CHF",
    "CLP",
    "CNY",
    "COP",
    "CRC",
    "CUC",
    "CUP",
    "CVE",
    "CZK",
    "DJF",
    "DKK",
    "DOP",
    "DZD",
    "EGP",
    "ERN",
    "ETB",
    "EUR",
    "FJD",
    "FKP",
    "GBP",
    "GEL",
    "GHS",
    "GIP",
    "GMD",
    "GNF",
    "GTQ",
    "GYD",
    "HKD",
    "HNL",
    "HRK",
    "HTG",
    "HUF",
    "IDR",
    "ILS",
    "INR",
    "IQD",
    "IRR",
    "ISK",
    "JMD",
    "JOD",
    "JPY",
    "KES",
    "KGS",
    "KHR",
    "KMF",
    "KPW",
    "KRW",
    "KWD",
    "KYD",
    "KZT",
    "LAK",
    "LBP",
    "LKR",
    "LRD",
    "LSL",
    "LYD",
    "MAD",
    "MDL",
    "MGA",
    "MKD",
    "MMK",
    "MNT",
    "MOP",
    "MRO",
    "MUR",
    "MVR",
    "MWK",
    "MXN",
    "MYR",
    "MZN",
    "NAD",
    "NGN",
    "NIO",
    "NOK",
    "NPR",
    "NZD",
    "OMR",
    "PAB",
    "PEN",
    "PGK",
    "PHP",
    "PKR",
    "PLN",
    "PYG",
    "QAR",
    "RON",
    "RSD",
    "RUB",
    "RWF",
    "SAR",
    "SBD",
    "SCR",
    "SDG",
    "SEK",
    "SGD",
    "SHP",
    "SLL",
    "SOS",
    "SRD",
    "SSP",
    "STD",
    "SVC",
    "SYP",
    "SZL",
    "THB",
    "TJS",
    "TMT",
    "TND",
    "TOP",
    "TRY",
    "TTD",
    "TWD",
    "TZS",
    "UAH",
    "UGX",
    "USD",
    "UYU",
    "UZS",
    "VEF",
    "VND",
    "VUV",
    "WST",
    "XAF",
    "XAG",
    "XAU",
    "XBA",
    "XBB",
    "XBC",
    "XBD",
    "XCD",
    "XDR",
    "XOF",
    "XPD",
    "XPF",
    "XPT",
    "XSU",
    "XTS",
    "XUA",
    "XXX",
    "YER",
    "ZAR",
    "ZMW",
    "ZWL",
}

DEPRECATED_DIMENSIONS = {
    "7DayTotals",
    "30DayTotals",
}

CORE_DIMENSIONS = {
    "ageGroup",
    "channel",
    "country",
    "day",
    "gender",
    "month",
    "sharingService",
    "uploaderType",
    "video",
}

CONTENT_OWNER_DIMENSIONS = {
    "claimedStatus",
    "uploaderType",
}

ALL_DIMENSIONS = {
    "video",
    "playlist",
    "channel",
    "country",
    "province",
    "day",
    "month",
    "insightPlaybackLocationType",
    "insightPlaybackLocationDetail",
    "liveOrOnDemand",
    "subscribedStatus",
    "youtubeProduct",
    "insightTrafficSourceType",
    "insightTrafficSourceDetail",
    "deviceType",
    "operatingSystem",
    "ageGroup",
    "gender",
    "sharingService",
    "elapsedVideoTimeRatio",
    "audienceType",
    "adType",
    "claimedStatus",
    "uploaderType",
}

VALID_FILTER_OPTIONS = {
    "video": (),
    "playlist": (),
    "channel": (),
    "group": (),
    "country": COUNTRIES,
    "province": SUBDIVISIONS,
    "continent": (
        "002",
        "019",
        "142",
        "150",
        "009",
    ),
    "subContinent": (
        "014",
        "017",
        "015",
        "018",
        "011",
        "029",
        "013",
        "021",
        "005",
        "143",
        "030",
        "034",
        "035",
        "145",
        "151",
        "154",
        "039",
        "155",
        "053",
        "054",
        "057",
        "061",
    ),
    "day": (),
    "month": (),
    "insightPlaybackLocationType": (
        "BROWSE",
        "CHANNEL",
        "EMBEDDED",
        "EXTERNAL_APP",
        "MOBILE",
        "SEARCH",
        "WATCH",
        "YT_OTHER",
    ),
    "insightPlaybackLocationDetail": (),
    "liveOrOnDemand": (
        "LIVE",
        "ON_DEMAND",
    ),
    "subscribedStatus": (
        "SUBSCRIBED",
        "UNSUBSCRIBED",
    ),
    "youtubeProduct": (
        "CORE",
        "GAMING",
        "KIDS",
        "UNKNOWN",
    ),
    "insightTrafficSourceType": (
        "ADVERTISING",
        "ANNOTATION",
        "CAMPAIGN_CARD",
        "END_SCREEN",
        "EXT_URL",
        "NO_LINK_EMBEDDED",
        "NO_LINK_OTHER",
        "NOTIFICATION",
        "PLAYLIST",
        "PROMOTED",
        "RELATED_VIDEO",
        "SHORTS",
        "SUBSCRIBER",
        "YT_CHANNEL",
        "YT_OTHER_PAGE",
        "YT_PLAYLIST_PAGE",
        "YT_SEARCH",
    ),
    "insightTrafficSourceDetail": (
        "ADVERTISING",
        "CAMPAIGN_CARD",
        "END_SCREEN",
        "EXT_URL",
        "NOTIFICATION",
        "RELATED_VIDEO",
        "SUBSCRIBER",
        "YT_CHANNEL",
        "YT_OTHER_PAGE",
        "YT_SEARCH",
    ),
    "deviceType": (
        "DESKTOP",
        "GAME_CONSOLE",
        "MOBILE",
        "TABLET",
        "TV",
        "UNKNOWN_PLATFORM",
    ),
    "operatingSystem": (
        "ANDROID",
        "BADA",
        "BLACKBERRY",
        "CHROMECAST",
        "DOCOMO",
        "FIREFOX",
        "HIPTOP",
        "IOS",
        "KAIOS",
        "LINUX",
        "MACINTOSH",
        "MEEGO",
        "NINTENDO_3DS",
        "OTHER",
        "PLAYSTATION",
        "PLAYSTATION_VITA",
        "REALMEDIA",
        "SMART_TV",
        "SYMBIAN",
        "TIZEN",
        "WEBOS",
        "WII",
        "WINDOWS",
        "WINDOWS_MOBILE",
        "XBOX",
    ),
    "ageGroup": (
        "age13-17",
        "age18-24",
        "age25-34",
        "age35-44",
        "age45-54",
        "age55-64",
        "age65-",
    ),
    "gender": (
        "female",
        "male",
        "user_specified",
    ),
    "sharingService": (
        "AMEBA",
        "ANDROID_EMAIL",
        "ANDROID_MESSENGER",
        "ANDROID_MMS",
        "BBM",
        "BLOGGER",
        "COPY_PASTE",
        "CYWORLD",
        "DIGG",
        "DROPBOX",
        "EMBED",
        "MAIL",
        "FACEBOOK",
        "FACEBOOK_MESSENGER",
        "FACEBOOK_PAGES",
        "FOTKA",
        "GMAIL",
        "GOO",
        "GOOGLEPLUS",
        "GO_SMS",
        "GROUPME",
        "HANGOUTS",
        "HI5",
        "HTC_MMS",
        "INBOX",
        "IOS_SYSTEM_ACTIVITY_DIALOG",
        "KAKAO_STORY",
        "KAKAO",
        "KIK",
        "LGE_EMAIL",
        "LINE",
        "LINKEDIN",
        "LIVEJOURNAL",
        "MENEAME",
        "MIXI",
        "MOTOROLA_MESSAGING",
        "MYSPACE",
        "NAVER",
        "NEARBY_SHARE",
        "NUJIJ",
        "ODNOKLASSNIKI",
        "OTHER",
        "PINTEREST",
        "RAKUTEN",
        "REDDIT",
        "SKYPE",
        "SKYBLOG",
        "SONY_CONVERSATIONS",
        "STUMBLEUPON",
        "TELEGRAM",
        "TEXT_MESSAGE",
        "TUENTI",
        "TUMBLR",
        "TWITTER",
        "UNKNOWN",
        "VERIZON_MMS",
        "VIBER",
        "VKONTATKE",
        "WECHAT",
        "WEIBO",
        "WHATS_APP",
        "WYKOP",
        "YAHOO",
        "YOUTUBE_GAMING",
        "YOUTUBE_KIDS",
        "YOUTUBE_MUSIC",
        "YOUTUBE_TV",
    ),
    "elapsedVideoTimeRatio": tuple(f"{n/100}" for n in range(1, 101)),
    "audienceType": (
        "ORGANIC",
        "AD_INSTREAM",
        "AD_INDISPLAY",
    ),
    "adType": (
        "auctionBumperInstream",
        "auctionDisplay",
        "auctionInstream",
        "auctionTrueviewInslate",
        "auctionTrueviewInstream",
        "auctionUnknown",
        "reservedBumperInstream",
        "reservedClickToPlay",
        "reservedDisplay",
        "reservedInstream",
        "reservedInstreamSelect",
        "reservedMasthead",
        "reservedUnknown",
        "unknown",
    ),
    "claimedStatus": ("claimed",),
    "uploaderType": (
        "self",
        "thirdParty",
    ),
    "isCurated": ("1",),
}

ALL_FILTERS = set(VALID_FILTER_OPTIONS.keys())

CORE_METRICS = {
    "annotationClickThroughRate",
    "annotationCloseRate",
    "averageViewDuration",
    "comments",
    "dislikes",
    "estimatedMinutesWatched",
    "estimatedRevenue",
    "likes",
    "shares",
    "subscribersGained",
    "subscribersLost",
    "viewerPercentage",
    "views",
}

ALL_METRICS_ORDERED = (
    "views",
    "redViews",
    "comments",
    "likes",
    "dislikes",
    "videosAddedToPlaylists",
    "videosRemovedFromPlaylists",
    "shares",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
    "annotationClickThroughRate",
    "annotationCloseRate",
    "annotationImpressions",
    "annotationClickableImpressions",
    "annotationClosableImpressions",
    "annotationClicks",
    "annotationCloses",
    "cardClickRate",
    "cardTeaserClickRate",
    "cardImpressions",
    "cardTeaserImpressions",
    "cardClicks",
    "cardTeaserClicks",
    "subscribersGained",
    "subscribersLost",
    "estimatedRevenue",
    "estimatedAdRevenue",
    "grossRevenue",
    "estimatedRedPartnerRevenue",
    "monetizedPlaybacks",
    "playbackBasedCpm",
    "adImpressions",
    "cpm",
    "viewerPercentage",
    "audienceWatchRatio",
    "relativeRetentionPerformance",
    "playlistStarts",
    "viewsPerPlaylistStart",
    "averageTimeInPlaylist",
)

ALL_METRICS = set(ALL_METRICS_ORDERED)

ALL_VIDEO_METRICS = {
    "views",
    "redViews",
    "comments",
    "likes",
    "dislikes",
    "videosAddedToPlaylists",
    "videosRemovedFromPlaylists",
    "shares",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
    "annotationClickThroughRate",
    "annotationCloseRate",
    "annotationImpressions",
    "annotationClickableImpressions",
    "annotationClosableImpressions",
    "annotationClicks",
    "annotationCloses",
    "cardClickRate",
    "cardTeaserClickRate",
    "cardImpressions",
    "cardTeaserImpressions",
    "cardClicks",
    "cardTeaserClicks",
    "subscribersGained",
    "subscribersLost",
    "estimatedRevenue",
    "estimatedAdRevenue",
    "grossRevenue",
    "estimatedRedPartnerRevenue",
    "monetizedPlaybacks",
    "playbackBasedCpm",
    "adImpressions",
    "cpm",
}

ALL_PROVINCE_METRICS = {
    "views",
    "redViews",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
    "annotationClickThroughRate",
    "annotationCloseRate",
    "annotationImpressions",
    "annotationClickableImpressions",
    "annotationClosableImpressions",
    "annotationClicks",
    "annotationCloses",
    "cardClickRate",
    "cardTeaserClickRate",
    "cardImpressions",
    "cardTeaserImpressions",
    "cardClicks",
    "cardTeaserClicks",
}

SUBSCRIPTION_METRICS = {
    "views",
    "redViews",
    "likes",
    "dislikes",
    "videosAddedToPlaylists",
    "videosRemovedFromPlaylists",
    "shares",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
    "annotationClickThroughRate",
    "annotationCloseRate",
    "annotationImpressions",
    "annotationClickableImpressions",
    "annotationClosableImpressions",
    "annotationClicks",
    "annotationCloses",
    "cardClickRate",
    "cardTeaserClickRate",
    "cardImpressions",
    "cardTeaserImpressions",
    "cardClicks",
    "cardTeaserClicks",
}

LESSER_SUBSCRIPTION_METRICS = {
    "views",
    "redViews",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
    "annotationClickThroughRate",
    "annotationCloseRate",
    "annotationImpressions",
    "annotationClickableImpressions",
    "annotationClosableImpressions",
    "annotationClicks",
    "annotationCloses",
    "cardClickRate",
    "cardTeaserClickRate",
    "cardImpressions",
    "cardTeaserImpressions",
    "cardClicks",
    "cardTeaserClicks",
}

LIVE_PLAYBACK_DETAIL_METRICS = {
    "views",
    "redViews",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
}

VIEW_PERCENTAGE_PLAYBACK_DETAIL_METRICS = {
    "views",
    "redViews",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
    "averageViewPercentage",
}

LOCATION_AND_TRAFFIC_METRICS = {
    "views",
    "estimatedMinutesWatched",
}

ALL_PLAYLIST_METRICS = {
    "views",
    "redViews",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "averageViewDuration",
    "playlistStarts",
    "viewsPerPlaylistStart",
    "averageTimeInPlaylist",
}

LOCATION_AND_TRAFFIC_PLAYLIST_METRICS = {
    "views",
    "estimatedMinutesWatched",
    "playlistStarts",
    "viewsPerPlaylistStart",
    "averageTimeInPlaylist",
}

LOCATION_AND_TRAFFIC_SORT_OPTIONS = {
    "views",
    "estimatedMinutesWatched",
}

TOP_VIDEOS_SORT_OPTIONS = {
    "views",
    "redViews",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
}

TOP_VIDEOS_EXTRA_SORT_OPTIONS = {
    "views",
    "redViews",
    "estimatedRevenue",
    "estimatedRedPartnerRevenue",
    "estimatedMinutesWatched",
    "estimatedRedMinutesWatched",
    "subscribersGained",
    "subscribersLost",
}

LOCATION_AND_TRAFFIC_PLAYLIST_SORT_OPTIONS = {
    "views",
    "estimatedMinutesWatched",
    "playlistStarts",
}
