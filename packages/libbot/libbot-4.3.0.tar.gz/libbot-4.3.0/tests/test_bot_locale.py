from typing import Any, List

import pytest
from libbot.i18n import BotLocale


@pytest.mark.parametrize(
    "key, args, locale, expected",
    [
        ("foo", [], None, "bar"),
        ("foo", [], "uk", "бар"),
        ("example", ["messages"], None, "okay"),
        ("example", ["messages"], "uk", "окей"),
        ("nested", ["callbacks", "default"], None, "sure"),
        ("nested", ["callbacks", "default"], "uk", "авжеж"),
    ],
)
def test_bot_locale_get(
    key: str,
    args: List[str],
    locale: str | None,
    expected: Any,
    bot_locale: BotLocale,
):
    assert (
        bot_locale._(key, *args, locale=locale) if locale is not None else bot_locale._(key, *args)
    ) == expected


@pytest.mark.parametrize(
    "key, args, expected",
    [
        ("foo", [], ["bar", "бар"]),
        ("example", ["messages"], ["okay", "окей"]),
        ("nested", ["callbacks", "default"], ["sure", "авжеж"]),
    ],
)
def test_i18n_in_all_locales(key: str, args: List[str], expected: Any, bot_locale: BotLocale):
    assert (bot_locale.in_all_locales(key, *args)) == expected


@pytest.mark.parametrize(
    "key, args, expected",
    [
        ("foo", [], {"en": "bar", "uk": "бар"}),
        ("example", ["messages"], {"en": "okay", "uk": "окей"}),
        ("nested", ["callbacks", "default"], {"en": "sure", "uk": "авжеж"}),
    ],
)
def test_i18n_in_every_locale(key: str, args: List[str], expected: Any, bot_locale: BotLocale):
    assert (bot_locale.in_every_locale(key, *args)) == expected
