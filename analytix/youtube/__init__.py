YOUTUBE_ANALYTICS_API_SERVICE_NAME = "youtubeAnalytics"
YOUTUBE_ANALYTICS_API_VERSION = "v2"
YOUTUBE_ANALYTICS_SCOPES = (
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
)

from .analytics import YouTubeAnalytics, YouTubeAnalyticsReport
from .service import YouTubeService
