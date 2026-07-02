from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram import Chat, Message, Update, User

from bot.db import connect, init_schema
from bot.handlers.weigh_in import (
    AWAITING_WEIGH_IN_KEY,
    HINT_MESSAGE,
    INVALID_MESSAGE,
    UNDO_EMPTY_MESSAGE,
    UNDO_OK_MESSAGE,
    skasuvaty_command,
    vaga_command,
    weigh_in_message,
)
from bot.repository import (
    get_latest_weigh_in,
    get_or_create_settings,
    insert_weigh_in,
)


def _make_message_update(user_id: int, text: str) -> Update:
    user = User(id=user_id, is_bot=False, first_name="Test")
    message = MagicMock(spec=Message)
    message.reply_text = AsyncMock()
    message.text = text
    message.chat = Chat(id=user_id, type="private")
    message.from_user = user
    return Update(update_id=1, message=message)


@pytest.mark.asyncio
async def test_vaga_command_sets_awaiting_and_sends_hint():
    update = _make_message_update(42, "/вага")
    context = MagicMock()
    context.user_data = {}

    await vaga_command(update, context)

    assert context.user_data[AWAITING_WEIGH_IN_KEY] is True
    update.effective_message.reply_text.assert_awaited_once_with(
        HINT_MESSAGE, parse_mode="Markdown"
    )


@pytest.mark.asyncio
async def test_weigh_in_message_persists_valid_input(tmp_path):
    db_path = str(tmp_path / "bot.db")
    update = _make_message_update(42, "72,4 28,5 32,1 24,8")
    context = MagicMock()
    context.user_data = {AWAITING_WEIGH_IN_KEY: True}
    context.bot_data = {"database_path": db_path}

    conn = connect(db_path)
    init_schema(conn)
    conn.close()

    await weigh_in_message(update, context)

    conn = connect(db_path)
    latest = get_latest_weigh_in(conn, user_id=42)
    conn.close()

    assert context.user_data[AWAITING_WEIGH_IN_KEY] is False
    assert latest is not None
    assert latest.weight_kg == 72.4
    update.effective_message.reply_text.assert_awaited_once()
    assert "Записано" in update.effective_message.reply_text.await_args.args[0]


@pytest.mark.asyncio
async def test_weigh_in_message_invalid_input():
    update = _make_message_update(42, "not valid")
    context = MagicMock()
    context.user_data = {AWAITING_WEIGH_IN_KEY: True}
    context.bot_data = {"database_path": ":memory:"}

    await weigh_in_message(update, context)

    assert context.user_data[AWAITING_WEIGH_IN_KEY] is False
    update.effective_message.reply_text.assert_awaited_once_with(
        INVALID_MESSAGE, parse_mode="Markdown"
    )


@pytest.mark.asyncio
async def test_weigh_in_message_ignored_when_not_awaiting():
    update = _make_message_update(42, "72,4 28,5 32,1 24,8")
    context = MagicMock()
    context.user_data = {}

    await weigh_in_message(update, context)

    update.effective_message.reply_text.assert_not_called()


@pytest.mark.asyncio
async def test_skasuvaty_command_deletes_latest(tmp_path):
    db_path = str(tmp_path / "bot.db")
    conn = connect(db_path)
    init_schema(conn)
    get_or_create_settings(conn, telegram_user_id=42)
    insert_weigh_in(
        conn,
        user_id=42,
        weight_kg=72.4,
        fat_pct=28.5,
        muscle_pct=32.1,
        bmi=24.8,
        recorded_at="2026-07-01T09:00:00+00:00",
    )
    conn.close()

    update = _make_message_update(42, "/скасувати")
    context = MagicMock()
    context.user_data = {AWAITING_WEIGH_IN_KEY: True}
    context.bot_data = {"database_path": db_path}

    await skasuvaty_command(update, context)

    conn = connect(db_path)
    latest = get_latest_weigh_in(conn, user_id=42)
    conn.close()

    assert context.user_data[AWAITING_WEIGH_IN_KEY] is False
    assert latest is None
    update.effective_message.reply_text.assert_awaited_once_with(UNDO_OK_MESSAGE)


@pytest.mark.asyncio
async def test_skasuvaty_command_empty(tmp_path):
    db_path = str(tmp_path / "bot.db")
    conn = connect(db_path)
    init_schema(conn)
    conn.close()

    update = _make_message_update(42, "/скасувати")
    context = MagicMock()
    context.user_data = {}
    context.bot_data = {"database_path": db_path}

    await skasuvaty_command(update, context)

    update.effective_message.reply_text.assert_awaited_once_with(UNDO_EMPTY_MESSAGE)
