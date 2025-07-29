from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict, SettingsError

DJANGO_DISCORD_WEBHOOK_URL_KEY = 'LOGCASTER_DISCORD_WEBHOOK_URL'
DJANGO_TELEGRAM_BOT_TOKEN_KEY = 'LOGCASTER_TELEGRAM_BOT_TOKEN'
DJANGO_TELEGRAM_CHAT_ID_KEY = 'LOGCASTER_TELEGRAM_CHAT_ID'


class DiscordEnvironmentVars(BaseSettings):
    webhook_url: str


class TelegramEnvironmentVars(BaseSettings):
    bot_token: str
    chat_id: int


class Environment(BaseSettings):
    discord: DiscordEnvironmentVars | None = None
    telegram: TelegramEnvironmentVars | None = None

    model_config = SettingsConfigDict(
        env_file='.env', extra='ignore', env_nested_delimiter='__'
    )

    @classmethod
    def _get_django_settings(cls) -> Any | None:
        """returns the `django.conf.settings` object if it can be imported"""
        try:
            from django.conf import settings  # noqa: PLC0415

            return settings
        except ImportError:
            return None

    def model_post_init(self, _: Any) -> None:
        """if the discord or telegram is not directly configured,
        try to get it from the django settings. If not found raise
        SettingsError
        """
        if (self.discord is not None) or (self.telegram is not None):
            return

        dj_settings = self._get_django_settings()
        if dj_settings is not None:
            self._configure_django(dj_settings)
            return

        raise SettingsError(
            '\033[31m A Logcaster source must be configured \033[m'
        )

    def get_discord_settings(self) -> DiscordEnvironmentVars:
        """returns the discord settings or raise SettingsError
        if discord is not configured
        """
        if self.discord is None:
            raise SettingsError('discord is not configured')
        return self.discord

    def get_telegram_settings(self) -> TelegramEnvironmentVars:
        """returns the telegram settings or raise SettingsError
        if telegram is not configured
        """
        if self.telegram is None:
            raise SettingsError('telegram is not configured')
        return self.telegram

    def _get_dj_setting(cls, setting_name: str, settings: Any) -> Any:
        return getattr(settings, setting_name, None)

    def _configure_django(self, dj_settings: Any) -> None:
        """
        configure the logcaster environment with the django settings

        Args:
            dj_settings (Any): the django settings object

        Raises:
            SettingsError: if the django settings does not have the
                `LOGCASTER_DISCORD_WEBHOOK_URL` or
                `LOGCASTER_TELEGRAM_BOT_TOKEN` and
                `LOGCASTER_TELEGRAM_CHAT_ID` settings.
        """
        using_telegram = False
        telegram_bot_token: str = self._get_dj_setting(
            DJANGO_TELEGRAM_BOT_TOKEN_KEY, dj_settings
        )
        telegram_chat_id: int = self._get_dj_setting(
            DJANGO_TELEGRAM_CHAT_ID_KEY, dj_settings
        )

        if telegram_bot_token and telegram_chat_id:
            self.telegram = TelegramEnvironmentVars(
                bot_token=telegram_bot_token,
                chat_id=telegram_chat_id,
            )
            using_telegram = True

        elif telegram_bot_token or telegram_chat_id:
            raise SettingsError(
                '\033[31m telegram must have both '
                '`LOGCASTER_TELEGRAM_BOT_TOKEN` '
                'and `LOGCASTER_TELEGRAM_CHAT_ID` provided \033[m'
            )

        discord_wh_url: str = self._get_dj_setting(
            DJANGO_DISCORD_WEBHOOK_URL_KEY, dj_settings
        )
        if discord_wh_url:
            self.discord = DiscordEnvironmentVars(webhook_url=discord_wh_url)
            return

        if not using_telegram:
            raise SettingsError(
                '\033[31m A Logcaster source must be configured \033[m'
            )


__all__ = ['Environment']
