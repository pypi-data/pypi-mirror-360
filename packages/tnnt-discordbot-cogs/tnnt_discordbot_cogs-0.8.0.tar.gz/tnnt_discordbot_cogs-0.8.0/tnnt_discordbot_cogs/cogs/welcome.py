"""
"Welcome" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""

# Standard Library
import asyncio
import logging

# Third Party
import discord
from discord.ext import commands

# Django
from django.db.models import Q

# Alliance Auth Discord Bot
from aadiscordbot.app_settings import get_site_url
from aadiscordbot.models import WelcomeMessage
from aadiscordbot.utils.auth import is_user_authenticated

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog
from tnnt_discordbot_cogs.models.setting import Setting

logger = logging.getLogger(__name__)

# Discord Bot Settings
# Channel
WELCOME_CHANNEL_AUTHENTICATED = Setting.get_setting(
    Setting.Field.WELCOME_CHANNEL_AUTHENTICATED.value
).channel
WELCOME_CHANNEL_UNAUTHENTICATED = Setting.get_setting(
    Setting.Field.WELCOME_CHANNEL_UNAUTHENTICATED.value
).channel

# Excluded Roles
WELCOME_ROLES_EXCLUDED = Setting.get_setting(
    Setting.Field.WELCOME_ROLES_EXCLUDED.value
).split(",")


class Welcome(commands.Cog):
    """
    Responds to on_member_join events from discord
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member):
        """
        Responds to on_member_join events from discord

        :param member: discord.Member object representing the new member
        :type member: discord.Member
        :return: None
        :rtype: None
        """

        logger.info(msg=f"{member} joined {member.guild.name}")

        # Default to the system channel if no channel is configured.
        channel = member.guild.system_channel

        try:
            # Give AA a chance to save the UID for a joiner.
            await asyncio.sleep(3)

            authenticated = is_user_authenticated(user=member, guild=member.guild)
        except Exception:
            authenticated = False

        # If the user is authenticated, send a welcome message to the authenticated channel.
        if authenticated:
            if any(role.name in WELCOME_ROLES_EXCLUDED for role in member.roles):
                # If the channel_id is an integer, get the channel object.
                if isinstance(WELCOME_CHANNEL_AUTHENTICATED, int):
                    channel = member.guild.get_channel(WELCOME_CHANNEL_AUTHENTICATED)

                try:
                    message = (
                        WelcomeMessage.objects.filter(
                            Q(Q(guild_id=member.guild.id) | Q(guild_id=None)),
                            authenticated=True,
                        )
                        .order_by("?")
                        .first()
                        .message
                    )
                    message_formatted = message.format(
                        user_mention=member.mention,
                        guild_name=member.guild.name,
                        auth_url=get_site_url(),
                    )

                    await channel.send(content=message_formatted)
                except IndexError:
                    logger.error(
                        msg="No Welcome Message configured for Discordbot Welcome cog"
                    )
                except Exception as e:
                    logger.error(msg=e)
        # If the user is not authenticated, send a welcome message to the unauthenticated channel.
        else:
            # If the channel_id is an integer, get the channel object.
            if isinstance(WELCOME_CHANNEL_UNAUTHENTICATED, int):
                channel = member.guild.get_channel(WELCOME_CHANNEL_UNAUTHENTICATED)

            try:
                message = (
                    WelcomeMessage.objects.filter(
                        Q(Q(guild_id=member.guild.id) | Q(guild_id=None)),
                        unauthenticated=True,
                    )
                    .order_by("?")
                    .first()
                    .message
                )
                message_formatted = message.format(
                    user_mention=member.mention,
                    guild_name=member.guild.name,
                    auth_url=get_site_url(),
                )

                await channel.send(message_formatted)
            except IndexError:
                logger.error(
                    msg="No Welcome Message configured for Discordbot Welcome cog"
                )
            except Exception as e:
                logger.error(msg=e)


def setup(bot):
    """
    Set up the Welcome cog

    :param bot: discord bot
    """

    # Unload the Welcome cog from `aadiscordbot`, so we can load our own.
    unload_cog(bot=bot, cog_name="Welcome")

    # Add the Welcome cog to the bot
    bot.add_cog(Welcome(bot))
