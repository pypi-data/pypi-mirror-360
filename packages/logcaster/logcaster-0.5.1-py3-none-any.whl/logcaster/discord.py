import logging
import sys
from typing import Any, Type

from logcaster.discord_utils.abstraction import (
    AbsDiscordEmbed,
    AbsDiscordWebhookAsyncClient,
    AbsDiscordWebhookClient,
)
from logcaster.discord_utils.discord_client import (
    DiscordWebhookAsyncClient,
    DiscordWebhookClient,
)
from logcaster.discord_utils.discord_embed import DiscordEmbed
from logcaster.exceptions import EmitError
from logcaster.utils import emit_async

from .formatters import BaseFormatter
from .handlers import BaseHandler
from .settings import ENV

__all__ = ['DiscordHandler', 'DiscordFormatter', 'DiscordAsyncHandler']


class DiscordFormatter(BaseFormatter):
    def __init__(self, **kwargs: Any):
        self.author = kwargs.pop('author', 'Logcaster')

        super().__init__(
            kwargs.pop('include_fields', None),
            kwargs.pop('exclude_fields', None),
        )

        self.COLORS = {
            logging.DEBUG: '3498db',  # blue
            logging.INFO: '2ecc71',  # green
            logging.WARNING: 'f1c40f',  # yellow
            logging.ERROR: 'e74c3c',  # red
            logging.CRITICAL: '8e44ad',  # purple
        }

        self.EMOJIS = {
            logging.DEBUG: '\U0001f41b',  # 🐛
            logging.INFO: '\U0001f4ac',  # 💬
            logging.WARNING: '\U000026a0',  # ⚠️
            logging.ERROR: '\U00002757',  # ❗
            logging.CRITICAL: '\U0001f4a5',  # 💥
        }

        self.RESET = '\033[0m'

    def _get_emoji(self, record: logging.LogRecord) -> str:
        return self.EMOJIS.get(record.levelno, '')

    def _get_level_name_with_emoji(self, record: logging.LogRecord) -> str:
        emoji = self._get_emoji(record)
        levelname = f'{emoji} {record.levelname} {emoji}'
        return levelname

    def _get_color(self, record: logging.LogRecord) -> str:
        """return the hex color by the record.levelno attribute"""
        return self.COLORS.get(record.levelno, 'ffffff')

    @classmethod
    def get_embed_class(cls) -> Type[AbsDiscordEmbed]:
        return DiscordEmbed

    def format(self, record: logging.LogRecord) -> AbsDiscordEmbed:  # type: ignore
        embed_cls = self.get_embed_class()
        embed = embed_cls(
            title=self._get_level_name_with_emoji(record),
            description=record.getMessage(),
            color=self._get_color(record),
        )

        embed.set_author(name=self.author)

        embed.set_footer(text='sent by @Logcaster')
        embed.set_timestamp(record.created)

        data = self._get_fields(record)
        [
            embed.add_embed_field(name=field, value=str(value))
            for field, value in data.items()
        ]
        return embed


class DiscordBaseHandler(BaseHandler):
    def get_webhook(
        self,
    ) -> AbsDiscordWebhookClient | AbsDiscordWebhookAsyncClient:
        raise NotImplementedError


class DiscordHandler(DiscordBaseHandler):
    @classmethod
    def get_webhook(cls) -> AbsDiscordWebhookClient:
        settings = ENV.get_discord_settings()
        return DiscordWebhookClient(settings.webhook_url)

    def emit(self, record: logging.LogRecord) -> None:
        webhook = self.get_webhook()

        fmt = self.format(record)
        if isinstance(fmt, AbsDiscordEmbed):
            webhook.add_embed(fmt)
        else:
            webhook.content = fmt

        try:
            webhook.execute()
            sys.stdout.write('logger sent to discord\n')

        except Exception as e:
            sys.stderr.write(
                'fail to sending logging to Discord: %s\n' % str(e)
            )
            sys.stderr.write(f'lost message: {record.getMessage()}')


class DiscordAsyncHandler(DiscordBaseHandler):
    @classmethod
    def get_webhook(cls) -> AbsDiscordWebhookAsyncClient:
        settings = ENV.get_discord_settings()
        return DiscordWebhookAsyncClient(settings.webhook_url)

    async def _emit(self, record: logging.LogRecord) -> None:
        webhook = self.get_webhook()

        fmt = self.format(record)
        if isinstance(fmt, AbsDiscordEmbed):
            webhook.add_embed(fmt)
        else:
            webhook.content = fmt

        try:
            await webhook.execute()
            sys.stdout.write('logger sent to discord\n')

        except Exception as e:
            raise EmitError(f'fail to sending logging to Discord: {e}')

    def emit(self, record: logging.LogRecord) -> None:
        emit_async(self._emit(record))
