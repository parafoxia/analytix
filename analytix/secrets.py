import os
from pathlib import Path

if os.name == "nt":
    TOKEN_STORE = Path("%USERPROFILE%/.analytix")
else:
    TOKEN_STORE = Path(f"/home/{os.environ['USER']}/.analytix")

YT_ANALYTICS_TOKEN = "youtube-analytics-token.json"
