# Standard Library
import logging

# Third Party
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.utils import get as du_get

# Django
from django.core.exceptions import ObjectDoesNotExist

# Alliance Auth Discord Bot
from aadiscordbot.cogs.utils.decorators import sender_is_admin
from aadiscordbot.models import Channels, Servers

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(__name__)


class Models(commands.Cog):
    """
    Django Model Population and Maintenance
    """

    def __init__(self, bot):
        self.bot = bot

    model_commands = SlashCommandGroup(
        "models",
        "Django Model Population",
    )

    @classmethod
    def channel_name(cls, channel):
        """
        Constructs a channel name with its category if available.

        Example:
        `#channel_name` for a channel without a category
        `Category » #channel_name` for a channel within a category

        :param channel: The channel object to get the name from.
        :type channel: discord.abc.GuildChannel
        :return: The formatted channel name, including its category if it exists.
        :rtype: str
        """

        category = du_get(channel.guild.categories, id=channel.category_id)

        channel_name = channel.name
        if channel.type.name != "category":
            channel_name = (
                f"{category.name} » #{channel.name}" if category else f"#{channel.name}"
            )

        return channel_name

    @model_commands.command(
        name="populate",
        description="Populate Django Models for all channels in the server",
    )
    @sender_is_admin()
    async def populate_models(self, ctx):
        """
        Populates Django Models for every Channel in the Discord server.

        :param ctx: The context of the command, which includes the guild information.
        :type ctx: discord.Interaction
        :return: A response indicating the population status of the models.
        :rtype: discord.InteractionResponse
        """

        await ctx.respond(
            "Populating Models, this might take a while on large servers",
            ephemeral=True,
        )

        try:
            Servers.objects.update_or_create(
                server=ctx.guild.id, defaults={"name": ctx.guild.name}
            )
        except Exception as e:
            logger.error(e)

        server = Servers.objects.get(server=ctx.guild.id)

        # Loop through all channels in the guild and update or create entries in the Channels model
        for channel in ctx.guild.channels:
            try:
                # Skip categories
                if channel.type.name != "category":
                    Channels.objects.update_or_create(
                        channel=channel.id,
                        defaults={"name": self.channel_name(channel), "server": server},
                    )
            except Exception as e:
                logger.error(e)

        return await ctx.followup.send(
            f"Django Models Populated for {ctx.guild.name}", ephemeral=True
        )

    @commands.Cog.listener("on_guild_channel_delete")
    async def on_guild_channel_delete(self, channel):
        """
        Marks a channel as deleted in the database when it is deleted in Discord.

        :param channel: The channel object that was deleted.
        :type channel: discord.abc.GuildChannel
        :return: None
        :rtype: None
        """

        try:
            # Instead of marking as deleted, we delete the entry from the database
            # Uncomment the following lines if you want to mark the channel as deleted instead of deleting it

            # deleted_channel = Channels.objects.get(channel=channel.id)
            # deleted_channel.deleted = True
            # deleted_channel.save()

            Channels.objects.get(channel=channel.id).delete()
        except ObjectDoesNotExist:
            # this is fine
            pass
        except Exception as e:
            logger.error(e)

    @commands.Cog.listener("on_guild_channel_create")
    async def on_guild_channel_create(self, channel):
        """
        Creates a new channel entry in the database when a channel is created in Discord.

        :param channel: The channel object that was created.
        :type channel: discord.abc.GuildChannel
        :return: None
        :rtype: None
        """

        try:
            Channels.objects.create(
                channel=channel.id,
                name=self.channel_name(channel),
                server=Servers.objects.get(server=channel.guild.id),
            )
        except Exception as e:
            logger.error(e)

    @commands.Cog.listener("on_guild_channel_update")
    async def on_guild_channel_update(self, before_channel, after_channel):
        """
        Updates the channel name in the database when a channel is updated in Discord.

        :param before_channel: The channel object before the update.
        :type before_channel: discord.abc.GuildChannel
        :param after_channel: The channel object after the update.
        :type after_channel: discord.abc.GuildChannel
        :return: None
        :rtype: None
        """

        try:
            Channels.objects.update_or_create(
                channel=after_channel.id,
                defaults={"name": self.channel_name(after_channel)},
            )

            # Update all subchannels of the category if the updated channel is a category
            if after_channel.type.name == "category":
                for subchannel in (
                    channel
                    for channel in after_channel.guild.channels
                    if channel.type.name != "category"
                    and channel.category_id == after_channel.id
                ):
                    Channels.objects.update_or_create(
                        channel=subchannel.id,
                        defaults={"name": self.channel_name(subchannel)},
                    )

        except Exception as e:
            logger.error(e)

    @commands.Cog.listener("on_guild_update")
    async def on_guild_update(self, before_guild, after_guild):
        """
        Updates the server name in the database when a guild is updated in Discord.

        :param before_guild: The guild object before the update.
        :type before_guild: discord.Guild
        :param after_guild: The guild object after the update.
        :type after_guild: discord.Guild
        :return: None
        :rtype: None
        """

        if before_guild.name == after_guild.name:
            pass
        else:
            try:
                Servers.objects.update_or_create(
                    server=after_guild.id, defaults={"name": after_guild.name}
                )
            except Exception as e:
                logger.error(e)


def setup(bot):
    """
    Setup function to add the Models cog to the bot.

    :param bot: The bot instance to which the cog will be added.
    :type bot: discord.ext.commands.Bot
    :return: None
    :rtype: None
    """

    # Unload the Models cog from `aadiscordbot`, so we can load our own.
    unload_cog(bot=bot, cog_name="Models")

    # Add the Models cog to the bot
    bot.add_cog(Models(bot))
