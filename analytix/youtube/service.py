import json
import logging
import os

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery

from analytix.errors import InvalidScopes
from analytix.youtube import (
    YOUTUBE_ANALYTICS_API_SERVICE_NAME,
    YOUTUBE_ANALYTICS_API_VERSION,
    YOUTUBE_ANALYTICS_SCOPES,
)


class Service:
    __slots__ = (
        "_client_id",
        "_project_id",
        "_auth_uri",
        "_token_uri",
        "_auth_provider_x509_cert_url",
        "_client_secret",
        "_redirect_uris",
        "scopes",
        "authorised",
    )

    def __init__(self, scopes, **kwargs):
        self._client_id = kwargs.get("client_id")
        self._project_id = kwargs.get("project_id")
        self._auth_uri = kwargs.get(
            "auth_uri", "https://accounts.google.com/o/oauth2/auth"
        )
        self._token_uri = kwargs.get(
            "token_uri", "https://oauth2.googleapis.com/token"
        )
        self._auth_provider_x509_cert_url = kwargs.get(
            "auth_provider_x509_cert_url"
        )
        self._client_secret = kwargs.get("client_secret")
        self._redirect_uris = kwargs.get("redirect_uris")
        self.scopes = scopes
        self.authorised = None

    def __str__(self):
        return self._project_id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        if self.authorised:
            self.close()

    @property
    def _secrets(self):
        return {
            "installed": {k[1:]: getattr(self, k) for k in self.__slots__[:-2]}
        }

    @property
    def name(self):
        return self._project_id

    @classmethod
    def from_file(cls, path, *, scopes="all"):
        if not os.path.isfile(path):
            raise FileNotFoundError(
                "you must provide a valid path to a secrets file"
            )

        with open(path, mode="r", encoding="utf-8") as f:
            secrets = json.load(f)

        logging.debug("Loaded secrets from file")
        return cls(cls._resolve_scopes(scopes), **secrets["installed"])

    @classmethod
    def from_dict(cls, secrets, *, scopes="all"):
        return cls(cls._resolve_scopes(scopes), **secrets["installed"])

    @staticmethod
    def _resolve_scopes(scopes):
        if scopes == "all":
            scopes = YOUTUBE_ANALYTICS_SCOPES
        else:
            if not isinstance(scopes, (tuple, list, set)):
                raise InvalidScopes(
                    f"expected tuple, list, or set of scopes, got {type(scopes).__name__}"
                )
            diff = set(scopes) - set(YOUTUBE_ANALYTICS_SCOPES)
            if diff:
                raise InvalidScopes(
                    f"one or more scopes you provided are invalid ({', '.join(diff)})"
                )
        return scopes

    def _get_credentials_using_console(self, flow):
        return flow.run_console(
            authorization_prompt_message=(
                "You need to authorise your service. "
                "Head to the below address, and enter the code.\n{url}"
            ),
            authorization_code_message="CODE > ",
        )

    def _get_credentials_using_server(self, flow, *, open_browser=True):
        return flow.run_local_server(
            open_browser=open_browser,
            authorization_prompt_message=(
                "A browser window should have opened. "
                "Use this to authenticate your service."
            ),
            success_message=(
                "All done -- you're ready to start pulling reports! "
                "You can close this window now."
            ),
        )

    def authorise(self, *, use_code=False):
        # TODO: Look up about non-local servers.

        flow = InstalledAppFlow.from_client_config(self._secrets, self.scopes)

        if use_code:
            credentials = self._get_credentials_using_console(flow)
        else:
            try:
                credentials = self._get_credentials_using_server(
                    flow, open_browser=True
                )
            except OSError:
                # Server auth can fail sometimes, especially if the previous session crashed.
                logging.error(
                    "Server authorisation failed; using console verification instead"
                )
                credentials = self._get_credentials_using_console(flow)

        self.authorised = discovery.build(
            YOUTUBE_ANALYTICS_API_SERVICE_NAME,
            YOUTUBE_ANALYTICS_API_VERSION,
            credentials=credentials,
        )
        logging.info("Service successfully authorised")

    authorize = authorise

    def close(self):
        self.authorised.close()
        logging.info("Service closed")
