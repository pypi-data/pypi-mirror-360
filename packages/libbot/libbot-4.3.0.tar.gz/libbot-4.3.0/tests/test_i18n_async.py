from pathlib import Path
from typing import Any, List

import pytest
from libbot import i18n


@pytest.mark.asyncio
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
async def test_i18n_get(
    key: str,
    args: List[str],
    locale: str | None,
    expected: Any,
    location_locale: Path,
):
    assert (
        await i18n._(key, *args, locale=locale, locales_root=location_locale)
        if locale is not None
        else await i18n._(key, *args, locales_root=location_locale)
    ) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "key, args, expected",
    [
        ("foo", [], ["bar", "бар"]),
        ("example", ["messages"], ["okay", "окей"]),
        ("nested", ["callbacks", "default"], ["sure", "авжеж"]),
    ],
)
async def test_i18n_in_all_locales(key: str, args: List[str], expected: Any, location_locale: Path):
    assert (await i18n.in_all_locales(key, *args, locales_root=location_locale)) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "key, args, expected",
    [
        ("foo", [], {"en": "bar", "uk": "бар"}),
        ("example", ["messages"], {"en": "okay", "uk": "окей"}),
        ("nested", ["callbacks", "default"], {"en": "sure", "uk": "авжеж"}),
    ],
)
async def test_i18n_in_every_locale(key: str, args: List[str], expected: Any, location_locale: Path):
    assert (await i18n.in_every_locale(key, *args, locales_root=location_locale)) == expected
