from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    MessageHandler,
    TypeHandler,
    filters,
)

from bot.config import Config, load_config
from bot.db import connect, init_schema
from bot.handlers.help import dopomoga_command
from bot.handlers.settings import (
    SETTINGS_CALLBACK_PATTERN,
    nalashtuvannya_command,
    settings_callback,
    settings_message,
)
from bot.handlers.views import (
    istoriya_command,
    misyats_command,
    progres_command,
    ves_chas_command,
)
from bot.handlers.weigh_in import (
    skasuvaty_command,
    vaga_command,
    weigh_in_message,
)
from bot.middleware import allowlist_gate

VAGA_COMMAND = filters.Regex(r"^/вага(?:@\w+)?$")
SKASUVATY_COMMAND = filters.Regex(r"^/скасувати(?:@\w+)?$")
DOPOMOGA_COMMAND = filters.Regex(r"^/допомога(?:@\w+)?$")
ISTORIYA_COMMAND = filters.Regex(r"^/історія(?:@\w+)?$")
PROGRES_COMMAND = filters.Regex(r"^/прогрес(?:@\w+)?$")
MISYATS_COMMAND = filters.Regex(r"^/місяць(?:@\w+)?$")
VES_CHAS_COMMAND = filters.Regex(r"^/весь_час(?:@\w+)?$")
NALASHTUVANNYA_COMMAND = filters.Regex(r"^/налаштування(?:@\w+)?$")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def build_application(config: Config) -> Application:
    conn = connect(config.database_path)
    init_schema(conn)
    conn.close()

    application = Application.builder().token(config.bot_token).build()
    application.bot_data["allowed_user_ids"] = config.allowed_user_ids
    application.bot_data["database_path"] = config.database_path

    application.add_handler(TypeHandler(Update, allowlist_gate), group=-1)

    application.add_handler(MessageHandler(VAGA_COMMAND, vaga_command), group=0)
    application.add_handler(
        MessageHandler(SKASUVATY_COMMAND, skasuvaty_command), group=0
    )
    application.add_handler(MessageHandler(DOPOMOGA_COMMAND, dopomoga_command), group=0)
    application.add_handler(MessageHandler(ISTORIYA_COMMAND, istoriya_command), group=0)
    application.add_handler(MessageHandler(PROGRES_COMMAND, progres_command), group=0)
    application.add_handler(MessageHandler(MISYATS_COMMAND, misyats_command), group=0)
    application.add_handler(MessageHandler(VES_CHAS_COMMAND, ves_chas_command), group=0)
    application.add_handler(
        MessageHandler(NALASHTUVANNYA_COMMAND, nalashtuvannya_command), group=0
    )
    application.add_handler(
        CallbackQueryHandler(settings_callback, pattern=SETTINGS_CALLBACK_PATTERN),
        group=0,
    )
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, settings_message, block=False),
        group=0,
    )
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, weigh_in_message, block=False),
        group=0,
    )

    return application


def main() -> None:
    config = load_config()
    application = build_application(config)
    logger.info(
        "Bot starting (allowed users: %d, database: %s)",
        len(config.allowed_user_ids),
        config.database_path,
    )
    application.run_polling()


if __name__ == "__main__":
    main()
