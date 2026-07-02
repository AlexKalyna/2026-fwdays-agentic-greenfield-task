from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from bot.models import UserSettings, WeighIn

DEFAULT_DISPLAY_NAME = "Оленка"
DEFAULT_REMINDER_TIME = "09:00"
DEFAULT_REMINDER_TIMEZONE = "Europe/Kyiv"
DEFAULT_REMINDER_WEEKDAY = 6


def _row_to_settings(row: sqlite3.Row) -> UserSettings:
    return UserSettings(
        telegram_user_id=row["telegram_user_id"],
        display_name=row["display_name"],
        reminder_time=row["reminder_time"],
        reminder_timezone=row["reminder_timezone"],
        reminder_weekday=row["reminder_weekday"],
        setup_completed_at=row["setup_completed_at"],
    )


def _row_to_weigh_in(row: sqlite3.Row) -> WeighIn:
    return WeighIn(
        id=row["id"],
        user_id=row["user_id"],
        recorded_at=row["recorded_at"],
        weight_kg=row["weight_kg"],
        fat_pct=row["fat_pct"],
        muscle_pct=row["muscle_pct"],
        bmi=row["bmi"],
    )


def get_or_create_settings(
    conn: sqlite3.Connection, telegram_user_id: int
) -> UserSettings:
    row = conn.execute(
        "SELECT * FROM user_settings WHERE telegram_user_id = ?",
        (telegram_user_id,),
    ).fetchone()

    if row is not None:
        return _row_to_settings(row)

    conn.execute(
        """
        INSERT INTO user_settings (
            telegram_user_id,
            display_name,
            reminder_time,
            reminder_timezone,
            reminder_weekday
        ) VALUES (?, ?, ?, ?, ?)
        """,
        (
            telegram_user_id,
            DEFAULT_DISPLAY_NAME,
            DEFAULT_REMINDER_TIME,
            DEFAULT_REMINDER_TIMEZONE,
            DEFAULT_REMINDER_WEEKDAY,
        ),
    )
    conn.commit()

    created = conn.execute(
        "SELECT * FROM user_settings WHERE telegram_user_id = ?",
        (telegram_user_id,),
    ).fetchone()
    assert created is not None
    return _row_to_settings(created)


def insert_weigh_in(
    conn: sqlite3.Connection,
    user_id: int,
    weight_kg: float,
    fat_pct: float,
    muscle_pct: float,
    bmi: float,
    recorded_at: str | None = None,
) -> WeighIn:
    timestamp = recorded_at or datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        """
        INSERT INTO weigh_ins (
            user_id, recorded_at, weight_kg, fat_pct, muscle_pct, bmi
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, timestamp, weight_kg, fat_pct, muscle_pct, bmi),
    )
    conn.commit()

    row = conn.execute(
        "SELECT * FROM weigh_ins WHERE id = ?",
        (cursor.lastrowid,),
    ).fetchone()
    assert row is not None
    return _row_to_weigh_in(row)


def get_latest_weigh_in(
    conn: sqlite3.Connection, user_id: int
) -> WeighIn | None:
    row = conn.execute(
        """
        SELECT * FROM weigh_ins
        WHERE user_id = ?
        ORDER BY recorded_at DESC, id DESC
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()

    if row is None:
        return None
    return _row_to_weigh_in(row)


def delete_latest_weigh_in(
    conn: sqlite3.Connection, user_id: int
) -> WeighIn | None:
    latest = get_latest_weigh_in(conn, user_id)
    if latest is None:
        return None

    conn.execute("DELETE FROM weigh_ins WHERE id = ?", (latest.id,))
    conn.commit()
    return latest
