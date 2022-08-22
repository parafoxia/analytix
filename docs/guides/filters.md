# What are filters?

## Overview

Filters allow for unwanted data to be omitted, leaving only the relevant data.
This is useful when you only want data for a specific demographic, or in some cases, when setting what type of information you want.
The vast majority of report types do not require you to provide a filter, though many report types can accept multiple filters.

## Retrieving playlist information

Whether to retrieve video or playlist information is controlled through filters.
In order to retrieve playlist information, you must passed the "isCurated" filter with value "1", like so:

```py
filters={"isCurated": "1"}
```

Other filters can be additionally supplied as normal, provided they are supported by playlist report types.

## Other special cases

There are a few other special cases worth keeping in mind:

* The "country" filter must be set to "US" when "province" is passed as a dimension
* The "insightPlaybackLocationType" filter must be set to "EMBEDDED" when "insightPlaybackLocationDetail" is passed as a dimension
* The "insightTrafficSourceType" filter must be set to one of the following when "insightTrafficSourceDetail" is passed as a dimension:
    * ADVERTISING
    * CAMPAIGN_CARD
    * END_SCREEN
    * EXT_URL
    * NOTIFICATION
    * RELATED_VIDEO
    * SUBSCRIBER
    * YT_CHANNEL
    * YT_OTHER_PAGE
    * YT_SEARCH
* The "video" filter cannot accept a comma-separated list of video IDs when "elapsedVideoTimeRatio" is passed as a dimension

## Valid filters

Click on a box to view the filter's possible values.

<details>
    <summary>adType</summary>
    <ul>
        <li>auctionBumperInstream</li>
        <li>auctionDisplay</li>
        <li>auctionInstream</li>
        <li>auctionTrueviewInslate</li>
        <li>auctionTrueviewInstream</li>
        <li>auctionUnknown</li>
        <li>reservedBumperInstream</li>
        <li>reservedClickToPlay</li>
        <li>reservedDisplay</li>
        <li>reservedInstream</li>
        <li>reservedInstreamSelect</li>
        <li>reservedMasthead</li>
        <li>reservedUnknown</li>
        <li>unknown</li>
    </ul>
</details>

<details>
    <summary>ageGroup</summary>
    <ul>
        <li>age13-17</li>
        <li>age18-24</li>
        <li>age25-34</li>
        <li>age35-44</li>
        <li>age45-54</li>
        <li>age55-64</li>
        <li>age65-</li>
    </ul>
</details>

<details>
    <summary>audienceType</summary>
    <ul>
        <li>ORGANIC</li>
        <li>AD_INSTREAM</li>
        <li>AD_INDISPLAY</li>
    </ul>
</details>

<details>
    <summary>channel</summary>
    Any channel ID.
</details>

<details>
    <summary>claimedStatus</summary>
    <ul>
        <li>claimed</li>
    </ul>
</details>

<details>
    <summary>continent</summary>
    <ul>
        <li>002</li>
        <li>019</li>
        <li>142</li>
        <li>150</li>
        <li>009</li>
    </ul>
</details>

<details>
    <summary>country</summary>
    Any <a href="https://www.iso.org/iso-3166-country-codes.html">ISO 3166-1 alpha-3</a> country code.
</details>

<details>
    <summary>day</summary>
    Any day in YYYY-MM-DD format.
</details>

<details>
    <summary>deviceType</summary>
    <ul>
        <li>DESKTOP</li>
        <li>GAME_CONSOLE</li>
        <li>MOBILE</li>
        <li>TABLET</li>
        <li>TV</li>
        <li>UNKNOWN_PLATFORM</li>
    </ul>
</details>

<details>
    <summary>elapsedVideoTimeRatio</summary>
    Any value (to a maximum of two significant figures) between 0.01 and 1 inclusive.
</details>

<details>
    <summary>gender</summary>
    <ul>
        <li>female</li>
        <li>male</li>
        <li>user_specified</li>
    </ul>
</details>

<details>
    <summary>group</summary>
    Any group ID.
</details>

<details>
    <summary>insightPlaybackLocationType</summary>
    <ul>
        <li>BROWSE</li>
        <li>CHANNEL</li>
        <li>EMBEDDED</li>
        <li>EXTERNAL_APP</li>
        <li>MOBILE</li>
        <li>SEARCH</li>
        <li>WATCH</li>
        <li>YT_OTHER</li>
    </ul>
</details>

<details>
    <summary>insightPlaybackLocationDetail</summary>
    <i>Not specified.</i>
</details>

<details>
    <summary>insightTrafficSourceDetail</summary>
    <ul>
        <li>ADVERTISING</li>
        <li>CAMPAIGN_CARD</li>
        <li>END_SCREEN</li>
        <li>EXT_URL</li>
        <li>NOTIFICATION</li>
        <li>RELATED_VIDEO</li>
        <li>SUBSCRIBER</li>
        <li>YT_CHANNEL</li>
        <li>YT_OTHER_PAGE</li>
        <li>YT_SEARCH</li>
    </ul>
</details>

<details>
    <summary>insightTrafficSourceType</summary>
    <ul>
        <li>ADVERTISING</li>
        <li>ANNOTATION</li>
        <li>CAMPAIGN_CARD</li>
        <li>END_SCREEN</li>
        <li>EXT_URL</li>
        <li>NO_LINK_EMBEDDED</li>
        <li>NO_LINK_OTHER</li>
        <li>NOTIFICATION</li>
        <li>PLAYLIST</li>
        <li>PROMOTED</li>
        <li>RELATED_VIDEO</li>
        <li>SHORTS</li>
        <li>SUBSCRIBER</li>
        <li>YT_CHANNEL</li>
        <li>YT_OTHER_PAGE</li>
        <li>YT_PLAYLIST_PAGE</li>
        <li>YT_SEARCH</li>
    </ul>
</details>

<details>
    <summary>isCurated</summary>
    <ul>
        <li>1</li>
    </ul>
</details>

<details>
    <summary>liveOrOnDemand</summary>
    <ul>
        <li>LIVE</li>
        <li>ON_DEMAND</li>
    </ul>
</details>

<details>
    <summary>month</summary>
    Any day in YYYY-MM format.
</details>

<details>
    <summary>operatingSystem</summary>
    <ul>
        <li>ANDROID</li>
        <li>BADA</li>
        <li>BLACKBERRY</li>
        <li>CHROMECAST</li>
        <li>DOCOMO</li>
        <li>FIREFOX</li>
        <li>HIPTOP</li>
        <li>IOS</li>
        <li>KAIOS</li>
        <li>LINUX</li>
        <li>MACINTOSH</li>
        <li>MEEGO</li>
        <li>NINTENDO_3DS</li>
        <li>OTHER</li>
        <li>PLAYSTATION</li>
        <li>PLAYSTATION_VITA</li>
        <li>REALMEDIA</li>
        <li>SMART_TV</li>
        <li>SYMBIAN</li>
        <li>TIZEN</li>
        <li>WEBOS</li>
        <li>WII</li>
        <li>WINDOWS</li>
        <li>WINDOWS_MOBILE</li>
        <li>XBOX</li>
    </ul>
</details>

<details>
    <summary>playlist</summary>
    Any playlist ID.
</details>

<details>
    <summary>province</summary>
    Any <a href="https://www.iso.org/iso-3166-country-codes.html">ISO 3166-2 alpha-3</a> subdivision code.
</details>

<details>
    <summary>sharingService</summary>
    <ul>
        <li>AMEBA</li>
        <li>ANDROID_EMAIL</li>
        <li>ANDROID_MESSENGER</li>
        <li>ANDROID_MMS</li>
        <li>BBM</li>
        <li>BLOGGER</li>
        <li>COPY_PASTE</li>
        <li>CYWORLD</li>
        <li>DIGG</li>
        <li>DROPBOX</li>
        <li>EMBED</li>
        <li>MAIL</li>
        <li>FACEBOOK</li>
        <li>FACEBOOK_MESSENGER</li>
        <li>FACEBOOK_PAGES</li>
        <li>FOTKA</li>
        <li>GMAIL</li>
        <li>GOO</li>
        <li>GOOGLEPLUS</li>
        <li>GO_SMS</li>
        <li>GROUPME</li>
        <li>HANGOUTS</li>
        <li>HI5</li>
        <li>HTC_MMS</li>
        <li>INBOX</li>
        <li>IOS_SYSTEM_ACTIVITY_DIALOG</li>
        <li>KAKAO_STORY</li>
        <li>KAKAO</li>
        <li>KIK</li>
        <li>LGE_EMAIL</li>
        <li>LINE</li>
        <li>LINKEDIN</li>
        <li>LIVEJOURNAL</li>
        <li>MENEAME</li>
        <li>MIXI</li>
        <li>MOTOROLA_MESSAGING</li>
        <li>MYSPACE</li>
        <li>NAVER</li>
        <li>NEARBY_SHARE</li>
        <li>NUJIJ</li>
        <li>ODNOKLASSNIKI</li>
        <li>OTHER</li>
        <li>PINTEREST</li>
        <li>RAKUTEN</li>
        <li>REDDIT</li>
        <li>SKYPE</li>
        <li>SKYBLOG</li>
        <li>SONY_CONVERSATIONS</li>
        <li>STUMBLEUPON</li>
        <li>TELEGRAM</li>
        <li>TEXT_MESSAGE</li>
        <li>TUENTI</li>
        <li>TUMBLR</li>
        <li>TWITTER</li>
        <li>UNKNOWN</li>
        <li>VERIZON_MMS</li>
        <li>VIBER</li>
        <li>VKONTATKE</li>
        <li>WECHAT</li>
        <li>WEIBO</li>
        <li>WHATS_APP</li>
        <li>WYKOP</li>
        <li>YAHOO</li>
        <li>YOUTUBE_GAMING</li>
        <li>YOUTUBE_KIDS</li>
        <li>YOUTUBE_MUSIC</li>
        <li>YOUTUBE_TV</li>
    </ul>
</details>

<details>
    <summary>subContinent</summary>
    <ul>
        <li>014</li>
        <li>017</li>
        <li>015</li>
        <li>018</li>
        <li>011</li>
        <li>029</li>
        <li>013</li>
        <li>021</li>
        <li>005</li>
        <li>143</li>
        <li>030</li>
        <li>034</li>
        <li>035</li>
        <li>145</li>
        <li>151</li>
        <li>154</li>
        <li>039</li>
        <li>155</li>
        <li>053</li>
        <li>054</li>
        <li>057</li>
        <li>061</li>
    </ul>
</details>

<details>
    <summary>subscribedStatus</summary>
    <ul>
        <li>SUBSCRIBED</li>
        <li>UNSUBSCRIBED</li>
    </ul>
</details>

<details>
    <summary>uploaderType</summary>
    <ul>
        <li>self</li>
        <li>thirdParty</li>
    </ul>
</details>

<details>
    <summary>video</summary>
    Any video ID.
</details>

<details>
    <summary>youtubeProduct</summary>
    <ul>
        <li>CORE</li>
        <li>GAMING</li>
        <li>KIDS</li>
        <li>UNKNOWN</li>
    </ul>
</details>
