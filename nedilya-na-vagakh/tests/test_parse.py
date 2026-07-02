import pytest

from bot.parse import ParseError, ParsedWeighIn, parse_weigh_in


def test_parse_space_separated_comma_decimals():
    result = parse_weigh_in("72,4 28,5 32,1 24,8")

    assert result == ParsedWeighIn(72.4, 28.5, 32.1, 24.8)


def test_parse_dot_decimals():
    result = parse_weigh_in("72.4 28.5 32.1 24.8")

    assert result == ParsedWeighIn(72.4, 28.5, 32.1, 24.8)


def test_parse_newline_separated():
    result = parse_weigh_in("72,4\n28,5\n32,1\n24,8")

    assert result == ParsedWeighIn(72.4, 28.5, 32.1, 24.8)


def test_parse_trims_whitespace():
    result = parse_weigh_in("  72,4  28,5  32,1  24,8  ")

    assert result.weight_kg == 72.4


def test_parse_wrong_token_count():
    with pytest.raises(ParseError):
        parse_weigh_in("72,4 28,5")


def test_parse_non_numeric():
    with pytest.raises(ParseError):
        parse_weigh_in("abc def ghi jkl")
