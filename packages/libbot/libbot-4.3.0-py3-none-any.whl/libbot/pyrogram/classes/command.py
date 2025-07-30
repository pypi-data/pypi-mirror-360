from dataclasses import dataclass


@dataclass
class PyroCommand:
    """Command stored in PyroClient's 'commands' attribute"""

    command: str
    description: str
