from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, MessageHandler, TypeHandler, filters

from bot.config import Config, load_config
from bot.db import connect, init_schema
from bot.handlers.weigh_in import (
    skasuvaty_command,
    vaga_command,
    weigh_in_message,
)
from bot.middleware import allowlist_gate

VAGA_COMMAND = filters.Regex(r"^/вага(?:@\w+)?$")
SKASUVATY_COMMAND = filters.Regex(r"^/скасувати(?:@\w+)?$")

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
    application.add_handler(MessageHandler(SKASUVATY_COMMAND, skasuvaty_command), group=0)
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
