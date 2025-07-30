import asyncio
import logging
import sys
from datetime import datetime, timedelta
from logging import Logger
from os import cpu_count, getpid
from pathlib import Path
from time import time
from typing import Any, Dict, List

from typing_extensions import override

from .command import PyroCommand
from .commandset import CommandSet
from ...i18n import _
from ...i18n.classes import BotLocale
from ...utils import json_read

try:
    import pyrogram
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.schedulers.background import BackgroundScheduler
    from pyrogram.client import Client
    from pyrogram.errors import BadRequest
    from pyrogram.handlers.message_handler import MessageHandler
    from pyrogram.raw.all import layer
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

try:
    from ujson import dumps, loads
except ImportError:
    from json import dumps, loads

logger: Logger = logging.getLogger(__name__)


class PyroClient(Client):
    @override
    def __init__(
            self,
            name: str = "bot_client",
            owner: int | None = None,
            config: Dict[str, Any] | None = None,
            config_path: str | Path = Path("config.json"),
            api_id: int | None = None,
            api_hash: str | None = None,
            bot_token: str | None = None,
            workers: int = min(32, cpu_count() + 4),
            locales_root: str | Path | None = None,
            plugins_root: str = "plugins",
            plugins_exclude: List[str] | None = None,
            sleep_threshold: int = 120,
            max_concurrent_transmissions: int = 1,
            commands_source: Dict[str, dict] | None = None,
            scoped_commands: bool | None = None,
            i18n_bot_info: bool = False,
            scheduler: AsyncIOScheduler | BackgroundScheduler | None = None,
            **kwargs,
    ):
        self.config: Dict[str, Any] = config if config is not None else json_read(config_path)

        super().__init__(
            name=name,
            api_id=self.config["bot"]["api_id"] if api_id is None else api_id,
            api_hash=self.config["bot"]["api_hash"] if api_hash is None else api_hash,
            bot_token=self.config["bot"]["bot_token"] if bot_token is None else bot_token,
            # Workers should be `min(32, cpu_count() + 4)`, otherwise
            # handlers land in another event loop and you won't see them
            workers=self.config["bot"]["workers"] if "workers" in self.config["bot"] else workers,
            plugins=dict(
                root=plugins_root,
                exclude=self.config["disabled_plugins"] if plugins_exclude is None else plugins_exclude,
            ),
            sleep_threshold=sleep_threshold,
            max_concurrent_transmissions=(
                self.config["bot"]["max_concurrent_transmissions"]
                if "max_concurrent_transmissions" in self.config["bot"]
                else max_concurrent_transmissions
            ),
            **kwargs,
        )
        self.owner: int = self.config["bot"]["owner"] if owner is None else owner
        self.commands: List[PyroCommand] = []
        self.commands_source: Dict[str, dict] = (
            self.config["commands"] if commands_source is None else commands_source
        )
        self.scoped_commands: bool = (
            self.config["bot"]["scoped_commands"] if scoped_commands is None else scoped_commands
        )
        self.start_time: float = 0

        self.bot_locale: BotLocale = BotLocale(
            default_locale=self.config["locale"],
            locales_root=(Path("locale") if locales_root is None else locales_root),
        )
        self.default_locale: str = self.bot_locale.default
        self.locales: dict = self.bot_locale.locales

        self._ = self.bot_locale._
        self.in_all_locales = self.bot_locale.in_all_locales
        self.in_every_locale = self.bot_locale.in_every_locale

        self.scheduler: AsyncIOScheduler | BackgroundScheduler | None = scheduler

        self.scopes_placeholders: Dict[str, int] = {"owner": self.owner}

        self.i18n_bot_info: bool = i18n_bot_info

    @override
    async def start(self, register_commands: bool = True, scheduler_start: bool = True) -> None:
        await super().start()

        self.start_time = time()

        logger.info(
            "Bot is running with Pyrogram v%s (Layer %s) and has started as @%s on PID %s.",
            pyrogram.__version__,
            layer,
            self.me.username,
            getpid(),
        )

        if self.i18n_bot_info:
            # Register default bot's info
            try:
                await self.set_bot_info(
                    name=self._("name", "bot"),
                    about=self._("about", "bot"),
                    description=self._("description", "bot"),
                    lang_code="",
                )
                logger.info(
                    "Bot's info for the default locale %s has been updated",
                    self.default_locale,
                )
            except KeyError:
                logger.warning(
                    "Default locale %s has incorrect keys or values in bot section",
                    self.default_locale,
                )

            # Register bot's info for each available locale
            for locale_code in self.locales:
                locale = self.locales[locale_code]

                if "metadata" not in locale or ("codes" not in locale["metadata"]):
                    logger.warning(
                        "Locale %s is missing metadata or metadata.codes key",
                        locale_code,
                    )
                    continue

                for code in locale["metadata"]["codes"]:
                    try:
                        await self.set_bot_info(
                            name=locale["bot"]["name"],
                            about=locale["bot"]["about"],
                            description=locale["bot"]["description"],
                            lang_code=code,
                        )
                        logger.info(
                            "Bot's info for the locale %s has been updated",
                            code,
                        )
                    except KeyError:
                        logger.warning(
                            "Locale %s has incorrect keys or values in bot section",
                            locale_code,
                        )

        # Send a message to the bot's reports chat about the startup
        try:
            await self.send_message(
                chat_id=(
                    self.owner
                    if self.config["reports"]["chat_id"] == "owner"
                    else self.config["reports"]["chat_id"]
                ),
                text=f"Bot started PID `{getpid()}`",
            )
        except BadRequest:
            logger.warning("Unable to send message to report chat.")

        if self.scheduler is None:
            return

        # Schedule the task to register all commands
        if register_commands:
            self.scheduler.add_job(
                self.register_commands,
                trigger="date",
                run_date=datetime.now() + timedelta(seconds=5),
                kwargs={"command_sets": await self.collect_commands()},
            )

        if scheduler_start:
            self.scheduler.start()

    @override
    async def stop(
            self, exit_completely: bool = True, scheduler_shutdown: bool = True, scheduler_wait: bool = True
    ) -> None:
        try:
            await self.send_message(
                chat_id=(
                    self.owner
                    if self.config["reports"]["chat_id"] == "owner"
                    else self.config["reports"]["chat_id"]
                ),
                text=f"Bot stopped with PID `{getpid()}`",
            )
            await asyncio.sleep(0.5)
        except BadRequest:
            logger.warning("Unable to send message to report chat.")

        if self.scheduler is not None and scheduler_shutdown:
            self.scheduler.shutdown(scheduler_wait)

        await super().stop()
        logger.warning("Bot stopped with PID %s.", getpid())

        if exit_completely:
            try:
                sys.exit()
            except SystemExit as exc:
                raise SystemExit("Bot has been shut down, this is not an application error!") from exc

    async def collect_commands(self) -> List[CommandSet] | None:
        """Gather list of the bot's commands

        ### Returns:
            * `List[CommandSet]`: List of the commands' sets.
        """
        command_sets = None

        # If config's bot.scoped_commands is true - more complicated
        # scopes system will be used instead of simple global commands
        if self.scoped_commands:
            scopes = {}
            command_sets = []

            # Iterate through all commands in config
            for command, contents in self.commands_source.items():
                # Iterate through all scopes of a command
                for scope in contents["scopes"]:
                    if dumps(scope) not in scopes:
                        scopes[dumps(scope)] = {"_": []}

                    # Add command to the scope's flattened key in scopes dict
                    scopes[dumps(scope)]["_"].append(BotCommand(command, _(command, "commands")))

                    for locale, string in (self.in_every_locale(command, "commands")).items():
                        if locale not in scopes[dumps(scope)]:
                            scopes[dumps(scope)][locale] = []

                        scopes[dumps(scope)][locale].append(BotCommand(command, string))

            # Iterate through all scopes and its commands
            for scope, locales in scopes.items():
                # Make flat key a dict again
                scope_dict = loads(scope)

                # Replace "owner" in the bot scope with owner's id
                for placeholder, chat_id in self.scopes_placeholders.items():
                    if "chat_id" in scope_dict and scope_dict["chat_id"] == placeholder:
                        scope_dict["chat_id"] = chat_id

                # Create object with the same name and args from the dict
                try:
                    scope_obj = globals()[scope_dict["name"]](
                        **{key: value for key, value in scope_dict.items() if key != "name"}
                    )
                except NameError:
                    logger.error(
                        "Could not register commands of the scope '%s' due to an invalid scope class provided!",
                        scope_dict["name"],
                    )
                    continue
                except TypeError:
                    logger.error(
                        "Could not register commands of the scope '%s' due to an invalid class arguments provided!",
                        scope_dict["name"],
                    )
                    continue

                # Add set of commands to the list of the command sets
                for locale, commands in locales.items():
                    if locale == "_":
                        command_sets.append(CommandSet(commands, scope=scope_obj, language_code=""))
                        continue
                    command_sets.append(CommandSet(commands, scope=scope_obj, language_code=locale))

            logger.info("Registering the following command sets: %s", command_sets)

        else:
            # This part here looks into the handlers and looks for commands
            # in it, if there are any. Then adds them to self.commands
            for handler in self.dispatcher.groups[0]:
                if isinstance(handler, MessageHandler) and (
                        hasattr(handler.filters, "base") or hasattr(handler.filters, "other")
                ):
                    for entry in [handler.filters.base, handler.filters.other]:
                        if hasattr(entry, "commands"):
                            for command in entry.commands:
                                logger.info("I see a command %s in my filters", command)
                                self.add_command(command)

        return command_sets

    def add_command(
            self,
            command: str,
    ) -> None:
        """Add command to the bot's internal commands list

        ### Args:
            * command (`str`)
        """
        self.commands.append(
            PyroCommand(
                command,
                _(command, "commands"),
            )
        )
        logger.info(
            "Added command '%s' to the bot's internal commands list",
            command,
        )

    async def register_commands(self, command_sets: List[CommandSet] | None = None) -> None:
        """Register commands stored in bot's 'commands' attribute"""

        if command_sets is None:
            commands = [
                BotCommand(command=command.command, description=command.description)
                for command in self.commands
            ]

            logger.info("Registering commands %s with a default scope 'BotCommandScopeDefault'", commands)

            await self.set_bot_commands(commands)
            return

        for command_set in command_sets:
            logger.info(
                "Registering command set with commands %s and scope '%s' (%s)",
                command_set.commands,
                command_set.scope,
                command_set.language_code,
            )
            await self.set_bot_commands(
                command_set.commands,
                command_set.scope,
                language_code=command_set.language_code,
            )

    async def remove_commands(self, command_sets: List[CommandSet] | None = None) -> None:
        """Remove commands stored in bot's 'commands' attribute"""

        if command_sets is None:
            logger.info("Removing commands with a default scope 'BotCommandScopeDefault'")
            await self.delete_bot_commands(BotCommandScopeDefault())
            return

        for command_set in command_sets:
            logger.info(
                "Removing command set with scope '%s' (%s)",
                command_set.scope,
                command_set.language_code,
            )
            await self.delete_bot_commands(
                command_set.scope,
                language_code=command_set.language_code,
            )
