YOUTUBE_ANALYTICS_API_SERVICE_NAME = "youtubeAnalytics"
YOUTUBE_ANALYTICS_API_VERSION = "v2"
YOUTUBE_ANALYTICS_SCOPES = (
    "yt-analytics.readonly",
    "yt-analytics-monetary.readonly",
)

from .analytics import *
from .service import YouTubeService
