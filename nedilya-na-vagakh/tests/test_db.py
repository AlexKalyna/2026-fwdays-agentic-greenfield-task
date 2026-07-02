from pathlib import Path

from bot.db import connect, init_schema
from bot.repository import (
    DEFAULT_DISPLAY_NAME,
    DEFAULT_REMINDER_TIME,
    DEFAULT_REMINDER_TIMEZONE,
    DEFAULT_REMINDER_WEEKDAY,
    delete_latest_weigh_in,
    get_latest_weigh_in,
    get_or_create_settings,
    insert_weigh_in,
)


def test_schema_creates_tables():
    conn = connect(":memory:")
    init_schema(conn)

    tables = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    assert "user_settings" in tables
    assert "weigh_ins" in tables
    conn.close()


def test_get_or_create_settings_defaults():
    conn = connect(":memory:")
    init_schema(conn)

    settings = get_or_create_settings(conn, telegram_user_id=42)

    assert settings.telegram_user_id == 42
    assert settings.display_name == DEFAULT_DISPLAY_NAME
    assert settings.reminder_time == DEFAULT_REMINDER_TIME
    assert settings.reminder_timezone == DEFAULT_REMINDER_TIMEZONE
    assert settings.reminder_weekday == DEFAULT_REMINDER_WEEKDAY
    assert settings.setup_completed_at is None
    conn.close()


def test_insert_and_fetch_weigh_in():
    conn = connect(":memory:")
    init_schema(conn)
    get_or_create_settings(conn, telegram_user_id=42)

    inserted = insert_weigh_in(
        conn,
        user_id=42,
        weight_kg=72.4,
        fat_pct=28.5,
        muscle_pct=32.1,
        bmi=24.8,
        recorded_at="2026-07-01T09:00:00+00:00",
    )
    latest = get_latest_weigh_in(conn, user_id=42)

    assert latest is not None
    assert latest.id == inserted.id
    assert latest.weight_kg == 72.4
    assert latest.fat_pct == 28.5
    assert latest.muscle_pct == 32.1
    assert latest.bmi == 24.8
    conn.close()


def test_data_survives_restart_simulation(tmp_path: Path):
    db_path = str(tmp_path / "bot.db")

    conn = connect(db_path)
    init_schema(conn)
    get_or_create_settings(conn, telegram_user_id=7)
    insert_weigh_in(
        conn,
        user_id=7,
        weight_kg=70.0,
        fat_pct=27.0,
        muscle_pct=33.0,
        bmi=24.0,
        recorded_at="2026-06-01T09:00:00+00:00",
    )
    conn.close()

    reopened = connect(db_path)
    latest = get_latest_weigh_in(reopened, user_id=7)

    assert latest is not None
    assert latest.weight_kg == 70.0
    reopened.close()


def test_delete_latest_weigh_in_removes_newest():
    conn = connect(":memory:")
    init_schema(conn)
    get_or_create_settings(conn, telegram_user_id=42)

    insert_weigh_in(
        conn,
        user_id=42,
        weight_kg=70.0,
        fat_pct=27.0,
        muscle_pct=33.0,
        bmi=24.0,
        recorded_at="2026-06-01T09:00:00+00:00",
    )
    second = insert_weigh_in(
        conn,
        user_id=42,
        weight_kg=69.0,
        fat_pct=26.0,
        muscle_pct=34.0,
        bmi=23.5,
        recorded_at="2026-07-01T09:00:00+00:00",
    )

    deleted = delete_latest_weigh_in(conn, user_id=42)
    latest = get_latest_weigh_in(conn, user_id=42)

    assert deleted is not None
    assert deleted.id == second.id
    assert latest is not None
    assert latest.weight_kg == 70.0
    conn.close()


def test_delete_latest_weigh_in_when_empty():
    conn = connect(":memory:")
    init_schema(conn)

    deleted = delete_latest_weigh_in(conn, user_id=99)

    assert deleted is None
    conn.close()
