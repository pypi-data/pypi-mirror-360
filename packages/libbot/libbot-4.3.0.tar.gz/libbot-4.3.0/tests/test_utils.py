from typing import Callable

import pytest
from libbot.utils.misc import supports_argument


def func1(foo: str, bar: str):
    """Dummy function with specific arguments"""
    pass


def func2(foo: str):
    """Dummy function with specific arguments"""
    pass


@pytest.mark.parametrize(
    "func, arg_name, result",
    [
        (func1, "foo", True),
        (func2, "bar", False),
    ],
)
def test_supports_argument(func: Callable, arg_name: str, result: bool):
    assert supports_argument(func, arg_name) == result
