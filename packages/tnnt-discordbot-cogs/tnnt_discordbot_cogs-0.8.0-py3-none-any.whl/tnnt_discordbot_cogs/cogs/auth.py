"""
"Auth" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""

# Standard Library
import logging

# Third Party
from discord.colour import Color
from discord.embeds import Embed
from discord.ext import commands

# Django
from django.conf import settings

# Alliance Auth
from allianceauth.eveonline.evelinks.eveimageserver import (
    alliance_logo_url,
    corporation_logo_url,
)

# Alliance Auth Discord Bot
from aadiscordbot.app_settings import get_site_url

# Terra Nanotech Templates
from tnnt_templates.app_settings import AppSettings

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(__name__)


class Auth(commands.Cog):
    """
    A Collection of Authentication Tools for Alliance Auth
    """

    def __init__(self, bot):
        """
        Initialize the Auth cog.

        :param bot:
        :type bot:
        """

        self.bot = bot

    @commands.slash_command(
        name="auth",
        description="Returns a link to TN-NT Auth",
        guild_ids=[int(settings.DISCORD_GUILD_ID)],
    )
    async def auth(self, ctx):
        """
        Returns a link to TN-NT Auth
        Used by many other Bots and is a common command that users will attempt to run.

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        await ctx.defer()

        auth_url = get_site_url()
        embed = Embed(title="Terra Nanotech Auth")

        try:
            if settings.TNNT_TEMPLATE_ENTITY_ID == 1:
                aa_icon = f"{auth_url}/static/allianceauth/icons/allianceauth.png"

                embed.set_thumbnail(url=aa_icon)
            else:
                entity_type = AppSettings.TNNT_TEMPLATE_ENTITY_TYPE
                entity_id = AppSettings.TNNT_TEMPLATE_ENTITY_ID

                logo_funcs = {
                    "alliance": (alliance_logo_url, "alliance_id"),
                    "corporation": (corporation_logo_url, "corporation_id"),
                }

                if entity_type in logo_funcs:
                    func, arg_name = logo_funcs[entity_type]

                    embed.set_thumbnail(url=func(**{arg_name: entity_id}, size=256))
        except AttributeError:
            pass

        embed.colour = Color.blue()

        embed.description = (
            "All authentication functions for this Discord "
            "server are handled through our Auth system."
        )

        embed.add_field(name="Auth Link", value=auth_url, inline=False)

        return await ctx.respond(embed=embed)


def setup(bot):
    """
    Set up the cog

    :param bot:
    :type bot:
    :return:
    :rtype:
    """

    # Unload the Auth cog from `aadiscordbot`, so we can load our own.
    unload_cog(bot=bot, cog_name="Auth")

    # Add the Auth cog to the bot
    bot.add_cog(Auth(bot))
