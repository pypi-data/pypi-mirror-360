"""Tracks client."""

import httpx

from .resources.event import EventResource

TRACKS_API_URL = "https://tracks.fluidattacks.com/"


class Tracks:
    """Tracks client."""

    def __init__(self) -> None:
        """Initialize the Tracks client."""
        self.client = httpx.Client(base_url=TRACKS_API_URL)
        self.event = EventResource(self.client)
