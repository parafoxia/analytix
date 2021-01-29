import json
import os
import typing as t

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery

from analytix import IncompleteRequest, NoAuthorisedService, ServiceAlreadyExists
from analytix.youtube import YOUTUBE_ANALYTICS_API_SERVICE_NAME, YOUTUBE_ANALYTICS_API_VERSION


class YouTubeService:
    """A YouTube service container to help with authorisation.

    Args:
        secrets (dict | os.PathLike | str]): The filepath to a secrets file or a dictionary of credentials used to authorise a YouTube service.
    """

    __slots__ = ("_service", "_secrets")

    def __init__(self, secrets):
        self._service = None

        if not isinstance(secrets, (os.PathLike, str)):
            self._secrets = secrets
            return

        with open(secrets, "r", encoding="utf-8") as f:
            self._secrets = json.load(f)

    def authorise(self, *scopes, use_console=False):
        """Authorises the YouTube service.

        Args:
            scopes (str *args): A series of string arguments denoting which scopes to use.
            use_console (bool): Whether to use the console authorisation method.

        Raises:
            IncompleteRequest: No scopes were passed.
            ServiceAlreadyExists: A service already exists, and has been authorised.
        """
        if not scopes:
            raise IncompleteRequest("expected 1 or more scopes, got 0")

        if self._service:
            raise ServiceAlreadyExists("an authorised service already exists")

        flow = InstalledAppFlow.from_client_config(
            self._secrets, tuple(f"https://www.googleapis.com/auth/{s}" for s in scopes)
        )
        try:
            credentials = flow.run_local_server(open_browser=True) if not use_console else flow.run_console()
        except OSError:
            print("WARNING: Using console authorisation as server authorisation failed.")
            credentials = flow.run_console()
        self._service = discovery.build(
            YOUTUBE_ANALYTICS_API_SERVICE_NAME, YOUTUBE_ANALYTICS_API_VERSION, credentials=credentials
        )

    def authorize(self, *scopes, use_console=False):
        """An alias to :code:`authorize`."""
        self.authorise(*scopes, use_console)

    def close(self):
        """Closes a YouTube service

        Raises:
            NoAuthorisedService: No authorised service currently exists.
        """
        if not self._service:
            raise NoAuthorisedService("no authorised service currently exists")

        self._service.close()
        self._service = None
