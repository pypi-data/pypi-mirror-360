import json
import sys
from logging import ERROR, LogRecord
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import httpx
from tabulate import tabulate  # type: ignore

from logcaster.utils import emit_async

from .exceptions import EmitError
from .formatters import BaseFormatter
from .handlers import BaseHandler
from .settings import ENV

__all__ = ['TelegramHandler', 'TelegramFormatter', 'TelegramAsyncHandler']


class TelegramFormatter(BaseFormatter):
    def __init__(
        self,
        include_fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
    ):
        super().__init__()
        self.include_fields = include_fields or []
        self.exclude_fields = exclude_fields or []

    def format(self, record: LogRecord) -> str:
        data = self._get_fields(record)
        table = tabulate(
            data.items(), tablefmt='presto', headers=['field', 'value']
        )
        return f'```\n{table}\n```'


class TelegramHandler(BaseHandler):
    def emit(self, record: LogRecord) -> bool:  # type: ignore
        out = self.format(record)
        conf = ENV.get_telegram_settings()

        data = json.dumps(
            {
                'text': out,
                'chat_id': conf.chat_id,
                'parse_mode': 'MarkdownV2',
            }
        ).encode('utf-8')

        request = Request(
            f'https://api.telegram.org/bot{conf.bot_token}/sendMessage',
            data=data,
            headers={'Content-Type': 'application/json'},
        )

        try:
            urlopen(request)
            sys.stdout.write(
                f'Logging sent to telegram chat id {conf.chat_id}\n'
            )

        except HTTPError as e:
            sys.stdout.write(
                f'error when logging to telegram: {e.read().decode()}\n'
            )
            return False

        except Exception as e:
            sys.stderr.write(f'error when logging to telegram: {str(e)}\n')
            sys.stderr.write(out + '\n')
            return False

        return True


class TelegramAsyncHandler(BaseHandler):
    def __init__(
        self,
        level: int = ERROR,
        httpx_client_params: dict[str, Any] | None = None,
    ):
        super().__init__(level)
        self._httpx_client_params = httpx_client_params or {}

    async def _emit(self, record: LogRecord) -> None:
        out = self.format(record)
        conf = ENV.get_telegram_settings()
        data = {
            'text': out,
            'chat_id': conf.chat_id,
            'parse_mode': 'MarkdownV2',
        }

        async with httpx.AsyncClient(**self._httpx_client_params) as client:
            try:
                response = await client.post(
                    f'https://api.telegram.org/bot{conf.bot_token}/sendMessage',
                    json=data,
                    headers={'Content-Type': 'application/json'},
                )
                response.raise_for_status()
                sys.stdout.write(
                    f'Logging sent to telegram chat id {conf.chat_id}\n'
                )

            except httpx.HTTPError as e:
                raise EmitError(
                    f'error when logging to telegram: {e.request} - {e}'
                )

    def emit(self, record: LogRecord) -> None:
        emit_async(self._emit(record))
