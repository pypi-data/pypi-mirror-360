import functools
import logging
import warnings
from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Dict, List, Optional, Sequence, TypeVar, Union

import discord
from discord import Embed, Interaction
from discord.utils import MISSING, _MissingSentinel
from ModuBotDiscord.config import DiscordConfig

from ..enums import PermissionEnum

T = TypeVar("T", bound=Callable[..., Awaitable[None]])

logger = logging.getLogger(__name__)


async def send_message(
    interaction: Interaction,
    content: Optional[str] = None,
    msg: Optional[str] = None,
    *,
    embed: Union[Embed, _MissingSentinel] = MISSING,
    embeds: Union[List[Embed], _MissingSentinel] = MISSING,
    file: Union[discord.File, _MissingSentinel] = MISSING,
    files: Union[List[discord.File], _MissingSentinel] = MISSING,
    view: Union[discord.ui.View, _MissingSentinel] = MISSING,
    tts: bool = False,
    ephemeral: bool = False,
    allowed_mentions: Union[discord.AllowedMentions, _MissingSentinel] = MISSING,
    suppress_embeds: bool = False,
    silent: bool = False,
    delete_after: Optional[float] = None,
    poll: Union[discord.Poll, _MissingSentinel] = MISSING,
) -> Optional[
    Union[
        discord.interactions.InteractionMessage, discord.webhook.async_.WebhookMessage
    ]
]:
    if msg is not None:
        warnings.warn(
            "`msg` is deprecated, use `content` instead",
            DeprecationWarning,
            stacklevel=2,
        )

        if content is None:
            content = msg

    if interaction.is_expired():
        logger.warning("Interaction is expired. Skipping send_message().")
        return None

    if interaction.response.is_done():
        return await interaction.followup.send(
            content=content,
            embed=embed,
            embeds=embeds,
            file=file,
            files=files,
            view=view,
            tts=tts,
            ephemeral=ephemeral,
            allowed_mentions=allowed_mentions,
            suppress_embeds=suppress_embeds,
            silent=silent,
            poll=poll,
        )

    await interaction.response.send_message(
        content=content,
        embed=embed,
        embeds=embeds,
        file=file,
        files=files,
        view=view,
        tts=tts,
        ephemeral=ephemeral,
        allowed_mentions=allowed_mentions,
        suppress_embeds=suppress_embeds,
        silent=silent,
        delete_after=delete_after,
        poll=poll,
    )

    return await interaction.original_response()


async def send_error(
    interaction: Interaction,
    title: str = "⚠️ An error occurred",
    description: Optional[str] = None,
    msg: Optional[str] = None,
) -> None:
    if msg is not None:
        warnings.warn(
            "`msg` is deprecated, use `title` or `description` instead",
            DeprecationWarning,
            stacklevel=2,
        )
        if description is None:
            description = msg
        else:
            title = msg

    embed: Embed = Embed(title=title, description=description, color=0xFF0000)
    await send_message(interaction, embed=embed, ephemeral=True)


def check_permission(*permissions: PermissionEnum) -> Callable[[T], T]:
    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(interaction: Interaction, *args, **kwargs):
            missing = [
                perm.value
                for perm in permissions
                if not getattr(interaction.user.guild_permissions, perm.value, False)
            ]
            if missing:
                missing_permissions = ", ".join(f"`{m}`" for m in missing)
                await send_error(
                    interaction,
                    title="🚫 Action not allowed",
                    description=f"You are missing the following permissions: {missing_permissions}",
                )
                return None
            return await func(interaction, *args, **kwargs)

        return wrapper

    return decorator


def check_bot_permission(*permissions: PermissionEnum) -> Callable[[T], T]:
    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(interaction: Interaction, *args, **kwargs):
            if not interaction.guild:
                await send_error(
                    interaction,
                    title="🚫 Action not allowed",
                    description="This command can only be used in a server.",
                )
                return None

            bot_permissions = interaction.guild.me.guild_permissions
            missing = [
                perm.value
                for perm in permissions
                if not getattr(bot_permissions, perm.value, False)
            ]
            if missing:
                missing_permissions = ", ".join(f"`{m}`" for m in missing)
                await send_error(
                    interaction,
                    title="🚫 Action not allowed",
                    description=f"The bot is missing the following permissions: {missing_permissions}",
                )
                return None

            return await func(interaction, *args, **kwargs)

        return wrapper

    return decorator


def check_bot_owner() -> Callable[[T], T]:
    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(interaction: Interaction, *args, **kwargs):
            if interaction.user.id != DiscordConfig.OWNER_ID:
                await send_error(
                    interaction,
                    title="🚫 Action not allowed",
                    description="You must be the bot owner to use this command.",
                )
                return None
            return await func(interaction, *args, **kwargs)

        return wrapper

    return decorator


def check_guild_owner() -> Callable[[T], T]:
    def decorator(func: T) -> T:
        @functools.wraps(func)
        async def wrapper(interaction: Interaction, *args, **kwargs):
            if (
                not interaction.guild
                or interaction.user.id != interaction.guild.owner_id
            ):
                await send_error(
                    interaction,
                    title="🚫 Action not allowed",
                    description="You must be the server owner to use this command.",
                )
                return None
            return await func(interaction, *args, **kwargs)

        return wrapper

    return decorator


class BaseCommand(ABC):
    @abstractmethod
    async def register(self, bot: "ModuBotDiscord"):
        pass
