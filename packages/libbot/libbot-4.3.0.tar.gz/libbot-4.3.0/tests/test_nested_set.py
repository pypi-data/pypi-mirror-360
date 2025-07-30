from typing import Any, Dict, List

import pytest
from libbot.utils.misc import nested_delete, nested_set


@pytest.mark.parametrize(
    "target, value, path, create_missing, expected",
    [
        ({"foo": "bar"}, "rab", ["foo"], True, {"foo": "rab"}),
        ({"foo": "bar"}, {"123": 456}, ["foo"], True, {"foo": {"123": 456}}),
        (
            {"foo": {"bar": {}}},
            True,
            ["foo", "bar", "test"],
            True,
            {"foo": {"bar": {"test": True}}},
        ),
        (
            {"foo": {"bar": {}}},
            True,
            ["foo", "bar", "test"],
            False,
            {"foo": {"bar": {}}},
        ),
    ],
)
def test_nested_set_valid(
    target: Dict[str, Any],
    value: Any,
    path: List[str],
    create_missing: bool,
    expected: Any,
):
    assert (nested_set(target, value, *path, create_missing=create_missing)) == expected


@pytest.mark.parametrize(
    "target, value, path, create_missing, expected",
    [
        (
            {"foo": {"bar": {}}},
            True,
            ["foo", "bar", "test1", "test2"],
            False,
            KeyError,
        ),
    ],
)
def test_nested_set_invalid(
    target: Dict[str, Any],
    value: Any,
    path: List[str],
    create_missing: bool,
    expected: Any,
):
    with pytest.raises(expected):
        assert (nested_set(target, value, *path, create_missing=create_missing)) == expected


@pytest.mark.parametrize(
    "target, path, expected",
    [
        ({"foo": "bar"}, ["foo"], {}),
        ({"foo": "bar", "bar": "foo"}, ["bar"], {"foo": "bar"}),
        (
            {"foo": {"bar": {}}},
            ["foo", "bar"],
            {"foo": {}},
        ),
    ],
)
def test_nested_delete(
    target: Dict[str, Any],
    path: List[str],
    expected: Any,
):
    assert (nested_delete(target, *path)) == expected
