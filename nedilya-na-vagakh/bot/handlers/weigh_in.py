from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.db import connect
from bot.parse import ParseError, format_uk_decimal, parse_weigh_in
from bot.repository import (
    delete_latest_weigh_in,
    get_or_create_settings,
    insert_weigh_in,
)

AWAITING_WEIGH_IN_KEY = "awaiting_weigh_in"

HINT_MESSAGE = (
    "Надішли чотири числа: вага (кг), жир (%), м'язи (%), BMI.\n"
    "Приклад: `72,4 28,5 32,1 24,8`"
)
INVALID_MESSAGE = (
    "Не вдалося розпізнати. Надішли чотири числа через пробіл, наприклад: "
    "`72,4 28,5 32,1 24,8`"
)
UNDO_OK_MESSAGE = "Останній запис скасовано."
UNDO_EMPTY_MESSAGE = "Немає записів для скасування."


def _success_message(weight_kg: float, fat_pct: float, muscle_pct: float, bmi: float) -> str:
    return (
        "Записано:\n"
        f"вага - {format_uk_decimal(weight_kg)} кг,\n"
        f"жир - {format_uk_decimal(fat_pct)} %,\n"
        f"м'язи - {format_uk_decimal(muscle_pct)} %,\n"
        f"BMI - {format_uk_decimal(bmi)}"
    )


async def vaga_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data[AWAITING_WEIGH_IN_KEY] = True
    if update.effective_message is not None:
        await update.effective_message.reply_text(HINT_MESSAGE, parse_mode="Markdown")


async def weigh_in_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get(AWAITING_WEIGH_IN_KEY):
        return

    message = update.effective_message
    user = update.effective_user
    if message is None or user is None or message.text is None:
        return

    try:
        parsed = parse_weigh_in(message.text)
    except ParseError:
        context.user_data[AWAITING_WEIGH_IN_KEY] = False
        await message.reply_text(INVALID_MESSAGE, parse_mode="Markdown")
        return

    database_path = context.bot_data["database_path"]
    conn = connect(database_path)
    try:
        get_or_create_settings(conn, user.id)
        insert_weigh_in(
            conn,
            user_id=user.id,
            weight_kg=parsed.weight_kg,
            fat_pct=parsed.fat_pct,
            muscle_pct=parsed.muscle_pct,
            bmi=parsed.bmi,
        )
    finally:
        conn.close()

    context.user_data[AWAITING_WEIGH_IN_KEY] = False
    await message.reply_text(
        _success_message(
            parsed.weight_kg,
            parsed.fat_pct,
            parsed.muscle_pct,
            parsed.bmi,
        )
    )


async def skasuvaty_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    user = update.effective_user
    if message is None or user is None:
        return

    context.user_data[AWAITING_WEIGH_IN_KEY] = False

    database_path = context.bot_data["database_path"]
    conn = connect(database_path)
    try:
        deleted = delete_latest_weigh_in(conn, user.id)
    finally:
        conn.close()

    if deleted is None:
        await message.reply_text(UNDO_EMPTY_MESSAGE)
    else:
        await message.reply_text(UNDO_OK_MESSAGE)
