from re import match

import httpx

from .abstraction import (
    AbsBaseWebhookClient,
    AbsDiscordEmbed,
    AbsDiscordWebhookAsyncClient,
    AbsDiscordWebhookClient,
)
from .models import WebhookClientPayload


def _check_url(webhook_url: str) -> None:
    if not match(
        r'^https?://discord.com/api/webhooks/[0-9]+/\w+$',
        webhook_url,
    ):
        raise ValueError(
            f'Invalid webhook url: {webhook_url}. '
            'Expected format: https://discord.com/api/webhooks/[id]/[token]'
        )


class DiscordBaseWebhookClient(AbsBaseWebhookClient):
    def __init__(self, webhook_url: str) -> None:
        _check_url(webhook_url)
        self.webhook_url = webhook_url
        self._payload: WebhookClientPayload | None = None

    def add_embed(self, embed: AbsDiscordEmbed) -> None:
        if not isinstance(embed, AbsDiscordEmbed):
            raise ValueError(
                f'Invalid embed type: {type(embed)}. '
                'Expected type: AbsDiscordEmbed'
            )

        if self._payload is None:
            self._payload = WebhookClientPayload(embeds=[embed.embed])
            return

        if self._payload.embeds is None:
            self._payload.embeds = [embed.embed]
            return

        self._payload.embeds.append(embed.embed)

    @property
    def content(self) -> str | None:
        if self._payload is None:
            return None
        return self._payload.content

    @content.setter
    def content(self, value: str) -> None:
        self._payload = WebhookClientPayload(content=value)


class DiscordWebhookClient(AbsDiscordWebhookClient, DiscordBaseWebhookClient):
    def execute(self) -> None:
        if self._payload is None:
            raise ValueError('No payload to send')

        response = httpx.post(
            self.webhook_url,
            json=self._payload.model_dump(),
        )

        response.raise_for_status()

        self._payload = None


class DiscordWebhookAsyncClient(
    AbsDiscordWebhookAsyncClient, DiscordBaseWebhookClient
):
    async def execute(self) -> None:
        if self._payload is None:
            raise ValueError('No payload to send')

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.webhook_url,
                json=self._payload.model_dump(),
            )

        response.raise_for_status()

        self._payload = None
