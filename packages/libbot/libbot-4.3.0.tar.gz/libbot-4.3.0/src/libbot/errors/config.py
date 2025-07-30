from typing import Any, List, Optional


class ConfigKeyError(Exception):
    """Raised when config key is not found.

    ### Attributes:
        * key (`str | List[str]`): Missing config key.
    """

    def __init__(self, key: str | List[str]) -> None:
        self.key: str | List[str] = key
        super().__init__(
            f"Config key {'.'.join(key) if isinstance(key, list) else key} is missing. Please set in your config file."
        )

    def __str__(self):
        return f"Config key {'.'.join(self.key) if isinstance(self.key, list) else self.key} is missing. Please set in your config file."


class ConfigValueError(Exception):
    """Raised when config key's value is invalid.

    ### Attributes:
        * key (`str | List[str]`): Invalid config key.
        * value (`Optional[Any]`): Key's correct value.
    """

    def __init__(self, key: str | List[str], value: Optional[Any] = None) -> None:
        self.key: str | List[str] = key
        self.value: Optional[Any] = value
        super().__init__(
            f"Config key {'.'.join(key) if isinstance(key, list) else key} has invalid value. {f'Must be {value}. ' if value else ''}Please set in your config file."
        )

    def __str__(self):
        return f"Config key {'.'.join(self.key) if isinstance(self.key, list) else self.key} has invalid value. {f'Must be {self.value}. ' if self.value else ''}Please set in your config file."
