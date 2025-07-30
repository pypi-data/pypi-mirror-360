"""
"About" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot

Since we don't want to have it branded for "The Initiative" we have to build our own
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

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(name=__name__)


class About(commands.Cog):
    """
    All about me!
    """

    def __init__(self, bot):
        """
        Initialize the About cog.

        :param bot:
        :type bot:
        """

        self.bot = bot

    @commands.slash_command(
        name="about",
        description="All about the bot",
        guild_ids=[int(settings.DISCORD_GUILD_ID)],
    )
    async def about(self, ctx):
        """
        All about the bot

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        await ctx.defer()

        auth_url = get_site_url()
        embed = Embed(title="TN-NT Discord Services")

        try:
            if settings.TNNT_TEMPLATE_ENTITY_ID == 1:
                aa_icon = f"{auth_url}/static/allianceauth/icons/allianceauth.png"
                embed.set_thumbnail(url=aa_icon)
            else:
                if settings.TNNT_TEMPLATE_ENTITY_TYPE == "alliance":
                    embed.set_thumbnail(
                        url=alliance_logo_url(
                            alliance_id=settings.TNNT_TEMPLATE_ENTITY_ID, size=256
                        )
                    )
                elif settings.TNNT_TEMPLATE_ENTITY_TYPE == "corporation":
                    embed.set_thumbnail(
                        url=corporation_logo_url(
                            corporation_id=settings.TNNT_TEMPLATE_ENTITY_ID, size=256
                        )
                    )
        except AttributeError:
            pass

        embed.colour = Color.green()
        embed.description = "This is a multi-functional discord bot tailored specifically for Terra Nanotech."
        embed.add_field(name="Auth Link", value=auth_url, inline=False)
        embed.set_footer(
            text="Developed by Aaron Kable and Ariel Rin, forked for Terra Nanotech by Rounon Dax"
        )

        return await ctx.respond(embed=embed)


def setup(bot):
    """
    Set up the cog

    :param bot:
    :type bot:
    :return:
    :rtype:
    """

    # Unload the About cog from `aadiscordbot`, so we can load our own.
    unload_cog(bot=bot, cog_name="About")

    # Add the About cog to the bot
    bot.add_cog(About(bot))
