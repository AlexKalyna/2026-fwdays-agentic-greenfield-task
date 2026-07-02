from __future__ import annotations

from dataclasses import dataclass


class ParseError(ValueError):
    """Raised when weigh-in input cannot be parsed."""


@dataclass(frozen=True)
class ParsedWeighIn:
    weight_kg: float
    fat_pct: float
    muscle_pct: float
    bmi: float


def parse_weigh_in(text: str) -> ParsedWeighIn:
    tokens = text.strip().split()
    if len(tokens) != 4:
        raise ParseError(f"expected 4 numbers, got {len(tokens)}")

    try:
        values = [float(token.replace(",", ".")) for token in tokens]
    except ValueError as exc:
        raise ParseError("non-numeric value in input") from exc

    return ParsedWeighIn(
        weight_kg=values[0],
        fat_pct=values[1],
        muscle_pct=values[2],
        bmi=values[3],
    )


def format_uk_decimal(value: float) -> str:
    return f"{value:.1f}".replace(".", ",")
