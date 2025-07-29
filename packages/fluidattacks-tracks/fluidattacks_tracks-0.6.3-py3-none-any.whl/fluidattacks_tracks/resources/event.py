"""Tracks event resource."""

from datetime import datetime
from typing import Literal, NotRequired, TypedDict

from httpx import Client

from fluidattacks_tracks.utils import fire_and_forget


class Event(TypedDict):
    """Tracks event."""

    action: Literal["CREATE", "READ", "UPDATE", "DELETE"]
    author_anonymous: NotRequired[bool]
    author_ip: NotRequired[str]
    author_role: NotRequired[str]
    author_user_agent: NotRequired[str]
    author: str
    date: datetime
    mechanism: Literal[
        "API",
        "FIXES",
        "FORCES",
        "JIRA",
        "MELTS",
        "MIGRATION",
        "RETRIEVES",
        "SCHEDULER",
        "TASK",
        "WEB",
    ]
    metadata: dict[str, object]
    object_id: str
    object: str
    session_id: NotRequired[str]


def _serialize_event(event: Event) -> dict[str, object]:
    """Serialize an event for JSON transmission."""
    return {**dict(event), "date": event["date"].isoformat()}


class EventResource:
    """Tracks event resource."""

    def __init__(self, client: Client) -> None:
        """Initialize the event resource."""
        self.client = client

    @fire_and_forget
    def create(self, event: Event) -> None:
        """Create an event."""
        self.client.post("/event", json=_serialize_event(event))
