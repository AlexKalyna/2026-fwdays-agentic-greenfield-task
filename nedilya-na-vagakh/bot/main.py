from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, TypeHandler

from bot.config import Config, load_config
from bot.db import connect, init_schema
from bot.middleware import allowlist_gate

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
