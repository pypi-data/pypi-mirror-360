import os
from typing import ClassVar

from ModuBotCore.config import BaseConfig


class DiscordConfig(BaseConfig):
    TOKEN: ClassVar[str] = os.environ.get("DISCORD_TOKEN")
    OWNER_ID: ClassVar[int] = int(os.environ.get("DISCORD_OWNER_ID", 0))
