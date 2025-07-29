from datetime import datetime, timezone
from typing import Any

from .abstraction import AbsDiscordEmbed, TimestampType
from .models import (
    EmbedAuthorObject,
    EmbedFieldObject,
    EmbedFooterObject,
    EmbedObject,
)


class DiscordEmbed(AbsDiscordEmbed):
    def __init__(self, **embed_obj_fields: Any) -> None:
        embed_data = embed_obj_fields or {'title': '', 'description': ''}
        self.embed = EmbedObject(**embed_data)

    def add_embed_field(
        self,
        name: str,
        value: Any,
        inline: bool = True,
    ) -> None:
        self.embed.fields.append(
            EmbedFieldObject(name=name, value=value, inline=inline)
        )

    def set_author(self, **author_obj_fields: Any) -> None:
        self.embed.author = EmbedAuthorObject(**author_obj_fields)

    def set_footer(self, **footer_obj_fields: Any) -> None:
        self.embed.footer = EmbedFooterObject(**footer_obj_fields)

    def set_timestamp(self, timestamp: TimestampType | None = None) -> None:
        """
        Set timestamp of the embed content.
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        elif isinstance(timestamp, float) or isinstance(timestamp, int):
            timestamp = datetime.fromtimestamp(
                timestamp, timezone.utc
            ).replace(tzinfo=None)

        if not isinstance(timestamp, str):
            timestamp = timestamp.isoformat()

        self.timestamp = timestamp
