import asyncio
import inspect
from inspect import FrameInfo
from typing import Any, Callable, Optional, Type


class asyncable:
    """Allows to mark a callable able to be async.

    Source: https://itsjohannawren.medium.com/single-call-sync-and-async-in-python-2acadd07c9d6"""

    def __init__(self, method: Callable):
        self.__sync = method
        self.__async = None

    def asynchronous(self, method: Callable) -> "asyncable":
        if not isinstance(method, Callable):
            raise RuntimeError("NOT CALLABLE!!!")

        self.__async = method
        return self

    @staticmethod
    def __is_awaited() -> bool:
        frame: FrameInfo = inspect.stack()[2]

        if not hasattr(frame, "positions"):
            return False

        return (
            frame.positions.col_offset >= 6
            and frame.code_context[frame.index][frame.positions.col_offset - 6 : frame.positions.col_offset]
            == "await "
        )

    def __get__(
        self,
        instance: Type,
        *args,
        owner_class: Optional[Type[Type]] = None,
        **kwargs,
    ) -> Callable:
        if self.__is_awaited():
            if self.__async is None:
                raise RuntimeError(
                    "Attempting to call asyncable with await, but no asynchronous call has been defined"
                )

            bound_method = self.__async.__get__(instance, owner_class)

            if isinstance(self.__sync, classmethod):
                return lambda: asyncio.ensure_future(bound_method(owner_class, *args, **kwargs))

            return lambda: asyncio.ensure_future(bound_method(*args, **kwargs))

        bound_method = self.__sync.__get__(instance, owner_class)

        return lambda: bound_method(*args, **kwargs)

    def __call__(self, *args, **kwargs) -> Any:
        if self.__is_awaited():
            if self.__async is None:
                raise RuntimeError(
                    "Attempting to call asyncable with await, but no asynchronous call has been defined"
                )

            return asyncio.ensure_future(self.__async(*args, **kwargs))

        return self.__sync(*args, **kwargs)
