"""
"Lookup" cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""

# Standard Library
import csv
import io
import logging

# Third Party
from discord import File
from discord.colour import Color
from discord.commands import SlashCommandGroup, option
from discord.embeds import Embed
from discord.ext import commands

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

# Alliance Auth
from allianceauth.eveonline.evelinks import evewho
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo

# Alliance Auth Discord Bot
from aadiscordbot import app_settings
from aadiscordbot.app_settings import aastatistics_active
from aadiscordbot.cogs.utils.autocompletes import (
    search_characters,
    search_corporations_on_characters,
)
from aadiscordbot.cogs.utils.decorators import (
    is_guild_managed,
    message_in_channels,
    sender_has_any_perm,
)

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(__name__)


class Lookup(commands.Cog):
    """
    All about users!
    """

    def __init__(self, bot):
        """
        Initialize the Lookup cog.

        :param bot:
        :type bot:
        """

        self.bot = bot

    lookup_commands = SlashCommandGroup(
        "lookup", "Server Admin Commands", guild_ids=app_settings.get_all_servers()
    )

    @staticmethod
    def get_csv(input_name):
        """
        Generates a CSV file of all known alts for a given character name.

        :param input_name:
        :type input_name:
        :return:
        :rtype:
        """

        char = EveCharacter.objects.get(character_name=input_name)
        alts = char.character_ownership.user.character_ownerships.all().select_related(
            "character"
        )
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        header = [
            "Character ID",
            "Character Name",
            "Corporation ID",
            "Corporation Name",
            "Alliance ID",
            "Alliance Name",
        ]
        writer.writerow(header)

        for a in alts:
            writer.writerow(
                [
                    a.character.character_id,
                    a.character.character_name,
                    a.character.corporation_id,
                    a.character.corporation_name,
                    a.character.alliance_id,
                    a.character.alliance_name,
                ]
            )

        buffer.seek(0)

        return File(buffer, f"{input_name}_known_alts.csv")

    @staticmethod
    def get_lookup_embed(input_name):
        """
        Generates an embed with information about a character.

        :param input_name:
        :type input_name:
        :return:
        :rtype:
        """

        embed = Embed(title=f"Character Lookup: {input_name}")

        try:
            char = EveCharacter.objects.get(character_name=input_name)

            try:
                main = char.character_ownership.user.profile.main_character
                state = char.character_ownership.user.profile.state.name
                groups = char.character_ownership.user.groups.all().values_list(
                    "name", flat=True
                )

                try:
                    discord_string = f"<@{char.character_ownership.user.discord.uid}>"
                except Exception as e:
                    logger.error(e)

                    discord_string = "unknown"

                if aastatistics_active():
                    alts = (
                        char.character_ownership.user.character_ownerships.all()
                        .select_related("character", "character_stats")
                        .values_list(
                            "character__character_name",
                            "character__corporation_ticker",
                            "character__character_id",
                            "character__corporation_id",
                            "character__character_stats__zk_12m",
                            "character__character_stats__zk_3m",
                        )
                    )
                    zk12 = 0
                    zk3 = 0
                else:
                    alts = (
                        char.character_ownership.user.character_ownerships.all()
                        .select_related("character")
                        .values_list(
                            "character__character_name",
                            "character__corporation_ticker",
                            "character__character_id",
                            "character__corporation_id",
                        )
                    )
                    zk12 = "Not Installed"
                    zk3 = "Not Installed"

                if aastatistics_active():
                    for alt in alts:
                        if alt[4]:
                            zk12 += alt[4]
                            zk3 += alt[5]

                embed.colour = Color.blue()
                embed.description = f"**{char}** is linked to **{main} [{main.corporation_ticker}]** (State: {state})"

                alt_list = [
                    f"[{a[0]}]({evewho.character_url(a[2])}) [[{a[1]}]({evewho.corporation_url(a[3])})]"
                    for a in alts
                ]

                for idx, names in enumerate(
                    [alt_list[i : i + 6] for i in range(0, len(alt_list), 6)]
                ):
                    if idx < 6:
                        embed.add_field(
                            name=f"Linked Characters {idx + 1}",
                            value="\n".join(names),
                            inline=False,
                        )
                    else:
                        embed.add_field(
                            name=f"Linked Characters {idx} **(Discord Limited There are More)**",
                            value="\n".join(names),
                            inline=False,
                        )
                        break

                if len(groups) > 0:
                    embed.add_field(
                        name="Groups", value="\n".join(groups), inline=False
                    )

                if aastatistics_active():
                    embed.add_field(name="12m Kills", value=zk12, inline=True)
                    embed.add_field(name="3m Kills", value=zk3, inline=True)

                embed.add_field(name="Discord Link", value=discord_string, inline=False)

                return embed
            except ObjectDoesNotExist:
                users = char.ownership_records.values("user")
                users = User.objects.filter(id__in=users)
                characters = EveCharacter.objects.filter(
                    ownership_records__user__in=users
                ).distinct()
                embed = Embed(title="Character Lookup")
                embed.colour = Color.blue()

                embed.description = f"**{char}** is unlinked. Searching for any characters linked to known users"
                user_names = [f"{user.username}" for user in users]

                if len(user_names) == 0:
                    user_names = "No user links found"
                else:
                    user_names = ", ".join(user_names)

                embed.add_field(name="Old Users", value=user_names, inline=False)

                alt_list = [
                    f"[{a.character_name}]({evewho.character_url(a.character_id)}) *[[{a.corporation_ticker}]({evewho.corporation_url(a.corporation_id)})]*"
                    for a in characters
                ]

                for idx, names in enumerate(
                    [alt_list[i : i + 6] for i in range(0, len(alt_list), 6)]
                ):
                    if idx < 6:
                        embed.add_field(
                            name=f"Found Characters {idx + 1}",
                            value=", ".join(names),
                            inline=False,
                        )
                    else:
                        embed.add_field(
                            name=f"Found Characters {idx} **( Discord Limited There are More )**",
                            value=", ".join(names),
                            inline=False,
                        )
                        break

                return embed

        except EveCharacter.DoesNotExist:
            embed.colour = Color.red()

            embed.description = (
                f"Character **{input_name}** does not exist in our Auth system"
            )

            return embed

    @staticmethod
    def build_altcorp_embeds(input_name):
        chars = EveCharacter.objects.filter(corporation_name=input_name)

        if chars.count():
            corp_id = 0
            own_ids = [settings.DISCORD_BOT_MEMBER_ALLIANCES]
            alts_in_corp = []
            knowns = 0

            for c in chars:
                corp_id = c.corporation_id

                if c.alliance_id not in own_ids:
                    alts_in_corp.append(c)

            mains = {}

            for a in alts_in_corp:
                try:
                    main = a.character_ownership.user.profile.main_character

                    if main.character_id not in mains:
                        mains[main.character_id] = [main, 0]

                    mains[main.character_id][1] += 1
                    knowns += 1
                except Exception:
                    # logger.error(e)
                    pass

            output = []
            base_string = "[{}]({}) [[{}]({})] has {} character{}"

            for k, m in mains.items():
                output.append(
                    base_string.format(
                        m[0],
                        evewho.character_url(m[0].character_id),
                        m[0].corporation_ticker,
                        evewho.corporation_url(m[0].corporation_id),
                        m[1],
                        "s" if m[1] > 1 else "",
                    )
                )
            embeds = []

            corp_info = EveCorporationInfo.provider.get_corporation(corp_id)

            msg = (
                f"**[[{corp_info.ticker}]({evewho.corporation_url(corp_id)})]** has {corp_info.members} members:\n\n"
                "```diff\n"
                f"+Known Members     : {knowns}\n"
                f"-Unknowns          : {corp_info.members - knowns}```"
            )

            _header = Embed(title=input_name, description=msg)

            embeds.append(_header)

            for strings in [output[i : i + 10] for i in range(0, len(output), 10)]:
                embed = Embed(title=input_name)
                embed.colour = Color.blue()
                embed.description = "\n".join(strings)
                embeds.append(embed)

            return embeds

    @lookup_commands.command(
        name="character",
        description="Looks up a character in the Auth system and returns information about them.",
        guild_ids=app_settings.get_all_servers(),
    )
    @is_guild_managed()
    @sender_has_any_perm(
        [
            "corputils.view_alliance_corpstats",
            "corpstats.view_alliance_corpstats",
            "aadiscordbot.member_command_access",
        ]
    )
    @message_in_channels(settings.ADMIN_DISCORD_BOT_CHANNELS)
    @option(
        "character",
        description="Search for a character",
        autocomplete=search_characters,
    )
    @option("gib_csv", description="Output a CSV of all characters")
    async def slash_lookup(self, ctx, character: str, gib_csv: bool = False):
        """
        Looks up a character in the Auth system and returns information about them.
        Input: a Eve Character Name
        Example: `/lookup character: John Doe gib_csv: True`

        :param ctx:
        :type ctx:
        :param character:
        :type character:
        :param gib_csv:
        :type gib_csv:
        :return:
        :rtype:
        """

        await ctx.defer()

        if gib_csv:
            file = self.get_csv(character)

            return await ctx.respond(embed=self.get_lookup_embed(character), file=file)

        return await ctx.respond(embed=self.get_lookup_embed(character))

    @lookup_commands.command(
        name="corporation",
        description="Looks up a corporation and returns information about its members.",
        guild_ids=app_settings.get_all_servers(),
    )
    @is_guild_managed()
    @sender_has_any_perm(["aadiscordbot.member_command_access"])
    @message_in_channels(settings.ADMIN_DISCORD_BOT_CHANNELS)
    @option(
        "corporation",
        description="Search for a corporation",
        autocomplete=search_corporations_on_characters,
    )
    async def slash_altcorp(self, ctx, corporation: str):
        """
        Gets Auth data about an altcorp

        :param ctx:
        :type ctx:
        :param corporation:
        :type corporation:
        :return:
        :rtype:
        """

        await ctx.defer()

        embeds = self.build_altcorp_embeds(corporation)

        if len(embeds):
            e = embeds.pop(0)

            await ctx.respond(embed=e)

            for e in embeds:
                await ctx.send(embed=e)
        else:
            await ctx.respond("No Members Found!")


def setup(bot):
    """
    Set up the cog

    :param bot:
    :type bot:
    :return:
    :rtype:
    """

    # Unload any other Lookup cog
    unload_cog(bot=bot, cog_name="Lookup")

    # Unload the Members cog from `aadiscordbot`
    unload_cog(bot=bot, cog_name="Members")

    # Add the Lookup cog to the bot
    bot.add_cog(Lookup(bot))
