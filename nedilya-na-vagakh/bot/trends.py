from __future__ import annotations

from enum import StrEnum

from bot.compare import MetricDeltas

STABLE_THRESHOLD = 0.2


class TrendLabel(StrEnum):
    PROGRESS = "прогрес"
    FLUCTUATION = "коливання"
    STABLE = "без змін"


def _display_delta(delta: float) -> float:
    return float(f"{delta:.1f}")


def classify_trend(delta: float, *, invert: bool = False) -> TrendLabel:
    displayed = _display_delta(delta)
    if abs(displayed) < STABLE_THRESHOLD:
        return TrendLabel.STABLE
    if invert:
        return TrendLabel.PROGRESS if displayed > 0 else TrendLabel.FLUCTUATION
    return TrendLabel.PROGRESS if displayed < 0 else TrendLabel.FLUCTUATION


def classify_metric_deltas(deltas: MetricDeltas) -> dict[str, TrendLabel]:
    return {
        "weight": classify_trend(deltas.weight_kg),
        "fat": classify_trend(deltas.fat_pct),
        "muscle": classify_trend(deltas.muscle_pct, invert=True),
        "bmi": classify_trend(deltas.bmi),
    }
