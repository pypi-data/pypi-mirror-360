# Logcaster
A package to send loggings to discord, telegram and whatever other location with the proposal of easily implements observability to small and lower coast applications

<p align="center">🛠🔧 Project in development process 🔧🛠</p>

- [Quick Start](#quick-start)
- [Usage](#usage)
- [Contributing](#contributing)

### Available sources
- Discord
- Telegram

### Features
- [x] easy to use.
- [x] natively supported by the built-in python logging package.
- [x] 'async' support.


### Quick-start
Requirements
- [python](https://pyton.org) `>=3.10,<4.0`
- [poetry](https://python-poetry.org) `>=2.0.0,<3.0.0`

#### Install
```sh
# by defaults supports telegram setup
poetry add logcaster
```

#### Configure
Once installed, you need only set the environment vars (see: [.env example file](https://github.com/LeandroDeJesus-S/logcaster/blob/main/.env-example))
```bash
# .env
DISCORD__WEBHOOK_URL=https://discord.com/api/webhooks/<webhook.id>/<token>
TELEGRAM__BOT_TOKEN=<you bot token>
TELEGRAM__CHAT_ID=<the chat id that bot will send logs>
```

#### Usage
```py
import logging

from logcaster.discord import DiscordFormatter, DiscordHandler
from logcaster.telegram import TelegramFormatter, TelegramHandler

logger = logging.getLogger(__name__)

dc_fmt = DiscordFormatter()
dc_hdl = DiscordHandler(level=logging.ERROR)

dc_hdl.setFormatter(dc_fmt)
logger.addHandler(dc_hdl)

tg_fmt = TelegramFormatter()
tg_hdl = TelegramHandler(level=logging.CRITICAL)

tg_hdl.setFormatter(tg_fmt)
logger.addHandler(tg_hdl)


logger.error('This will be sent to Discord only!')
logger.critical('This will be sent to both Telegram and Discord!')
```

**Note**: The default level is setting up to ERROR, it's highly recommended don't set a lower level, cause each emitted logging will make a request to the given source.

### Filtering fields
```python
dc_hdl.setFormatter(
    DiscordFormatter(include_fields=('asctime', 'levelname', 'msg'))
)
logger.critical('This will send only the included fields to Discord!')

tg_hdl.setFormatter(TelegramFormatter(exclude_fields=['asctime', 'levelname']))
logger.critical(
    'This will send all fields except the excluded ones to Telegram!'
)
```

### using async handler
```python
from logcaster.telegram import TelegramAsyncHandler
logger.addHandler(TelegramAsyncHandler())
```

#### Django example
```py
# settings.py
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "telegram_fmt": {
            "class": "logcaster.telegram.TelegramFormatter",
        },
        "discord_fmt": {
            "class": "logcaster.discord.DiscordFormatter",
            "exclude_fields": ['funcName', 'lineno'],
        }
    },
    "handlers": {
        "telegram": {
            "class": "logcaster.telegram.TelegramHandler",
        },
        "discord": {
            "class": "logcaster.discord.DiscordHandler",
            "exclude_fields": ['funcName', 'lineno'],
        }
    },
    "loggers": {
        "logcaster": {
            "handlers": ["telegram", "discord"],
            "formatters": ["telegram_fmt", "discord_fmt"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
```

### Contributing
1. [Fork this repo](https://github.com/LeandroDeJesus-S/logcaster/fork)

2. Clone your fork to your local machine:
   ```bash
   git clone https://github.com/<your-username>/logcaster.git
   cd logcaster
   ```

3. Configure the upstream address to be able to fetch updates
    ```bash
    git remote add upstream https://github.com/LeandroDeJesus-S/logcaster.git
    ```

4. Create a new brach to write your changes:
   ```sh
   git checkout -b feature/feature-name
   ```

5. After make any changes be sure that the code is properly formatted and anything is broken:
    ```sh
    poetry run mypy ./logcaster
    poetry run ruff check ./logcaster
    poetry run ruff format ./logcaster
    poetry run pytest ./tests

    # or using make
    make check
    ```

6. Having finished your changes, send a pull request with a good description about your work.
