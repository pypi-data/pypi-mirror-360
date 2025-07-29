from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, TypeAlias

from .models import EmbedObject

TimestampType: TypeAlias = float | int | str | datetime


class AbsDiscordEmbed(ABC):
    """Abstract class that represents a discord embed class."""

    embed: EmbedObject

    @abstractmethod
    def __init__(self, **embed_obj_fields: Any) -> None: ...

    @abstractmethod
    def set_author(self, **author_obj_fields: Any) -> None:
        """sets the author of the embed"""

    @abstractmethod
    def set_footer(self, **footer_obj_fields: Any) -> None:
        """sets the footer of the embed"""

    @abstractmethod
    def add_embed_field(
        self,
        name: str,
        value: str,
        inline: bool = True,
    ) -> None:
        """adds a field to the embed"""

    @abstractmethod
    def set_timestamp(self, timestamp: TimestampType | None = None) -> None:
        """
        Set timestamp of the embed content.
        """


class AbsBaseWebhookClient(ABC):
    @abstractmethod
    def __init__(self, webhook_url: str) -> None: ...

    @abstractmethod
    def add_embed(self, embed: AbsDiscordEmbed) -> None: ...

    @property
    @abstractmethod
    def content(self) -> str | None: ...

    @content.setter
    @abstractmethod
    def content(self, value: str) -> None: ...


class AbsDiscordWebhookClient(AbsBaseWebhookClient):
    @abstractmethod
    def execute(self) -> None: ...


class AbsDiscordWebhookAsyncClient(AbsBaseWebhookClient):
    @abstractmethod
    async def execute(self) -> None: ...
