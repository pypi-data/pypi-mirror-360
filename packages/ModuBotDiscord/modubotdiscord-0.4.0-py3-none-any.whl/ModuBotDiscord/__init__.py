import importlib
import os
from typing import ClassVar, Type

from ModuBotCore import ModuBotCore

import discord
from discord.ext import commands as discordCommands
from discord.ui import View
from ModuBotDiscord.commands import BaseCommand

from .config import DiscordConfig


class ModuBotDiscord(ModuBotCore, discordCommands.Bot):
    NAME = "ModuBotDiscord"
    CONFIG: ClassVar[Type[DiscordConfig]] = DiscordConfig

    def __init__(self, **kwargs):
        ModuBotCore.__init__(self)

        intents = discord.Intents.default()
        discordCommands.Bot.__init__(
            self, command_prefix="!", intents=intents, **kwargs
        )

        if DiscordConfig.OWNER_ID < 0:
            self.logger.warning(
                "OWNER_ID is not set correctly. Restricted commands may not work as expected."
            )

    def run(self):
        ModuBotCore.run(self)

        discordCommands.Bot.run(self, self.CONFIG.TOKEN)

    async def setup_hook(self) -> None:
        await self._register_all_commands()
        await self._register_all_views()

        synced_commands = await self.tree.sync()
        self.logger.info(
            f"Synchronized {len(synced_commands)} global slash command(s): "
            + ", ".join(cmd.name for cmd in synced_commands)
        )

    async def _register_all_commands(self) -> None:
        for filename in os.listdir("commands"):
            if filename.endswith(".py") and filename != "__init__.py":
                command = importlib.import_module(f"commands.{filename[:-3]}")
                for item in dir(command):
                    obj = getattr(command, item)
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, BaseCommand)
                        and obj is not BaseCommand
                    ):
                        command_instance: BaseCommand = obj()
                        await command_instance.register(self)

    async def _register_all_views(self) -> None:
        for filename in os.listdir("views"):
            if filename.endswith(".py") and filename != "__init__.py":
                view = importlib.import_module(f"views.{filename[:-3]}")
                for item in dir(view):
                    obj = getattr(view, item)
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, View)
                        and obj is not View
                    ):
                        view_instance: View = obj()
                        if view_instance.timeout is None:
                            self.add_view(view_instance)
