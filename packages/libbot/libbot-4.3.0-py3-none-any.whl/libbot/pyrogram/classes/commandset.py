from dataclasses import dataclass
from typing import List

try:
    from pyrogram.types import (
        BotCommand,
        BotCommandScopeAllChatAdministrators,
        BotCommandScopeAllGroupChats,
        BotCommandScopeAllPrivateChats,
        BotCommandScopeChat,
        BotCommandScopeChatAdministrators,
        BotCommandScopeChatMember,
        BotCommandScopeDefault,
    )
except ImportError as exc:
    raise ImportError("You need to install libbot[pyrogram] in order to use this class.") from exc


@dataclass
class CommandSet:
    """Command stored in PyroClient's 'commands' attribute"""

    commands: List[BotCommand]
    scope: (
        BotCommandScopeDefault
        | BotCommandScopeAllPrivateChats
        | BotCommandScopeAllGroupChats
        | BotCommandScopeAllChatAdministrators
        | BotCommandScopeChat
        | BotCommandScopeChatAdministrators
        | BotCommandScopeChatMember
    ) = BotCommandScopeDefault
    language_code: str = ""
