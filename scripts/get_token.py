import json

import requests
from requests_oauthlib import OAuth2Session

SCOPES = (
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
)

with open("./secrets/secrets-tests.json", mode="r", encoding="utf-8") as f:
    secrets = json.load(f)["installed"]

session = OAuth2Session(
    secrets["client_id"],
    redirect_uri=secrets["redirect_uris"][0],
    scope=SCOPES,
)

url, _ = session.authorization_url(secrets["auth_uri"])
code = input(f"Use this link to get your OAuth code: {url}\nCODE > ")
token = session.fetch_token(
    secrets["token_uri"],
    code=code,
    client_secret=secrets["client_secret"],
)
token = token["access_token"]
print(f"\nHere's your token! Paste it into the action input.\n{token}")
