import json
import os
import typing as t

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery

from analytix import IncompleteRequest, NoAuthorisedService, ServiceAlreadyExists
from analytix.youtube import (
    YOUTUBE_ANALYTICS_API_SERVICE_NAME,
    YOUTUBE_ANALYTICS_API_VERSION,
    YOUTUBE_ANALYTICS_SCOPES,
)


class YouTubeService:
    """A YouTube service container to help with authorisation.

    Args:
        secrets (dict | os.PathLike | str]): The filepath to a secrets file or a dictionary of credentials used to authorise a YouTube service.

    Parameters:
        active (Resource | None): The currently authorised service. If no service is authorised, this None.
    """

    __slots__ = ("active", "_secrets")

    def __init__(self, secrets):
        self.active = None

        if not isinstance(secrets, (os.PathLike, str)):
            self._secrets = secrets
            return

        with open(secrets, "r", encoding="utf-8") as f:
            self._secrets = json.load(f)

    def authorise(self, use_console=False):
        """Authorises the YouTube service.

        Args:
            use_console (bool): Whether to use the console authorisation method. Defaults to False.

        Raises:
            ServiceAlreadyExists: A service already exists, and has been authorised.
        """
        if self.active:
            raise ServiceAlreadyExists("an authorised service already exists")

        flow = InstalledAppFlow.from_client_config(self._secrets, YOUTUBE_ANALYTICS_SCOPES)

        try:
            if use_console:
                credentials = flow.run_console(
                    authorization_prompt_message="You need to authorise your service. Head to the below address, and enter the code.\n{url}",
                    authorization_code_message="CODE > ",
                )
            else:
                credentials = flow.run_local_server(
                    open_browser=True,
                    authorization_prompt_message="A browser window should have opened. Use this to authenticate your service.",
                    success_message="All done -- you're ready to start pulling reports! You can close this window now.",
                )
        except OSError:
            print("WARNING: Using console authorisation as server authorisation failed.")
            credentials = flow.run_console(
                authorization_prompt_message="You need to authorise your service. Head to the below address, and enter the code.\n{url}",
                authorization_code_message="CODE > ",
            )
        self.active = discovery.build(
            YOUTUBE_ANALYTICS_API_SERVICE_NAME, YOUTUBE_ANALYTICS_API_VERSION, credentials=credentials
        )

    def authorize(self, use_console=False):
        """An alias to :code:`authorise`."""
        self.authorise(use_console)

    def close(self):
        """Closes a YouTube service

        Raises:
            NoAuthorisedService: No authorised service currently exists.
        """
        if not self.active:
            raise NoAuthorisedService("no authorised service currently exists")

        self.active.close()
        self.active = None
