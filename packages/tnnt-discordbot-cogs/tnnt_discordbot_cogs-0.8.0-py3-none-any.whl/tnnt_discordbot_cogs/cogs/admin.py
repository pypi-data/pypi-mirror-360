# Standard Library
import logging

# Third Party
import pendulum
from discord import (
    AutocompleteContext,
    CategoryChannel,
    Embed,
    Role,
    TextChannel,
    VoiceChannel,
    option,
)
from discord.commands import SlashCommandGroup
from discord.ext import commands
from discord.ext.commands import Paginator

# Django
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter
from allianceauth.eveonline.tasks import update_character
from allianceauth.services.modules.discord.models import DiscordUser
from allianceauth.services.modules.discord.tasks import update_groups, update_nickname

# Alliance Auth Discord Bot
from aadiscordbot import app_settings
from aadiscordbot.cogs.utils.decorators import sender_is_admin
from aadiscordbot.utils import auth

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(__name__)


class Admin(commands.Cog):
    def __init__(self, bot):
        """
        Initialize the Admin cog

        :param bot:
        :type bot:
        """

        self.bot = bot

    @staticmethod
    def search_characters(ctx: AutocompleteContext):
        """
        Returns a list of characters that begin with the characters entered so far

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        return list(
            EveCharacter.objects.filter(
                character_name__icontains=ctx.value
            ).values_list("character_name", flat=True)[:10]
        )

    admin_commands = SlashCommandGroup(
        "admin", "Server Admin Commands", guild_ids=app_settings.get_all_servers()
    )

    @admin_commands.command(
        name="add_role",
        description="Add a role as read/write to a channel",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def add_role_slash(self, ctx, channel: TextChannel, role: Role):
        """
        Add a role as read/write to a channel …

        :param ctx:
        :type ctx:
        :param channel:
        :type channel:
        :param role:
        :type role:
        :return:
        :rtype:
        """

        await ctx.defer(ephemeral=True)
        await channel.set_permissions(role, read_messages=True, send_messages=True)

        return await ctx.respond(
            f"Set Read/Write `{role.name}` in `{channel.name}`", ephemeral=True
        )

    @admin_commands.command(
        name="add_role_read",
        description="Add a role as read only to a channel",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def add_role_read_slash(self, ctx, channel: TextChannel, role: Role):
        """
        Add a role as read only to a channel …

        :param ctx:
        :type ctx:
        :param channel:
        :type channel:
        :param role:
        :type role:
        :return:
        :rtype:
        """

        await ctx.defer(ephemeral=True)
        await channel.set_permissions(role, read_messages=True, send_messages=False)

        return await ctx.respond(
            f"Set Readonly `{role.name}` in `{channel.name}`", ephemeral=True
        )

    @admin_commands.command(
        name="rem_role",
        description="Remove a role from a channel",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def rem_role_slash(self, ctx, channel: TextChannel, role: Role):
        """
        Remove a role from a channel …

        :param ctx:
        :type ctx:
        :param channel:
        :type channel:
        :param role:
        :type role:
        :return:
        :rtype:
        """

        await ctx.defer(ephemeral=True)
        await channel.set_permissions(role, read_messages=False, send_messages=False)

        return await ctx.respond(
            f"Removed `{role.name}` from `{channel.name}`", ephemeral=True
        )

    @admin_commands.command(
        name="new_channel",
        description="Create a new channel in the specified category and set permissions for the first role",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def new_channel_slash(
        self, ctx, category: CategoryChannel, channel_name: str, first_role: Role
    ):
        """
        Create a new channel in the specified category and set permissions for the first role.

        :param ctx:
        :type ctx:
        :param category:
        :type category:
        :param channel_name:
        :type channel_name:
        :param first_role:
        :type first_role:
        :return:
        :rtype:
        """

        await ctx.defer(ephemeral=True)

        for channel in ctx.guild.channels:  # TODO replace with channel lookup not loop
            if isinstance(channel, (TextChannel, VoiceChannel)):
                if channel.name.lower() == channel_name.lower():
                    if channel.category_id == category.id:
                        return await ctx.respond(
                            f"Channel already exists: <#{channel.id}>"
                        )

        # Create the channel
        channel = await ctx.guild.create_text_channel(
            channel_name.lower(), category=category
        )

        await channel.set_permissions(
            ctx.guild.default_role, read_messages=False, send_messages=False
        )
        await channel.set_permissions(
            first_role, read_messages=True, send_messages=True
        )

        return await ctx.respond(
            f"Created new channel `{channel.name}` and added the `{first_role.name}` role",
            ephemeral=True,
        )

    @admin_commands.command(
        name="promote_to_god",
        description="Set a role as admin",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def promote_role_to_god(self, ctx, role: Role):
        """
        Set a role as admin …

        :param ctx:
        :type ctx:
        :param role:
        :type role:
        :return:
        :rtype:
        """

        await ctx.defer(ephemeral=True)

        perms = role.permissions
        perms.administrator = True

        await role.edit(permissions=perms)

        return await ctx.respond(f"Set `{role.name}` as admin", ephemeral=True)

    @admin_commands.command(
        name="demote_from_god",
        description="Remove admin from a role",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def demote_role_from_god(self, ctx, role: Role):
        """
        Remove admin from a role.

        :param ctx:
        :type ctx:
        :param role:
        :type role:
        :return:
        :rtype:
        """

        await ctx.defer(ephemeral=True)

        perms = role.permissions
        perms.administrator = False

        await role.edit(permissions=perms)

        return await ctx.respond(f"Removed admin from `{role.name}`", ephemeral=True)

    @admin_commands.command(
        name="empty_roles",
        description="Returns a list of all roles in the server",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def empty_roles(self, ctx):
        """
        Returns a list of all roles in the server, including those with no members and those without an auth group.

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        await ctx.defer()

        embed = Embed(title="Server Role Status")
        embed.add_field(name="Total Roles", value=len(ctx.guild.roles))
        empties = []
        no_auth_group = []

        for role_model in ctx.guild.roles:
            if len(role_model.members) == 0:
                empties.append(role_model.name)
            else:
                if not Group.objects.filter(name=role_model.name):
                    no_auth_group.append(role_model.name)

        embed.add_field(name="Empty Groups", value="\n".join(empties), inline=False)
        embed.add_field(
            name="Groups with no Auth Group",
            value="\n".join(no_auth_group),
            inline=False,
        )

        return await ctx.respond(embed=embed)

    @admin_commands.command(
        name="clear_empty_roles",
        description="Deletes all roles in the server that have no members",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def clear_empty_roles(self, ctx):
        """
        Deletes all roles in the server that have no members.

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        await ctx.defer()

        empties = 0
        fails = []

        for role_model in ctx.guild.roles:
            if len(role_model.members) == 0:
                try:
                    await role_model.delete()
                    empties += 1
                except Exception:
                    fails.append(role_model.name)

        await ctx.respond(f"Deleted {empties} Roles.")

        chunks = [fails[x : x + 50] for x in range(0, len(fails), 50)]

        for c in chunks:
            await ctx.respond("\n".join(c))

        return None

    @admin_commands.command(
        name="orphans",
        description="Returns a list of all users in the server that do not have a corresponding DiscordUser in Auth",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def orphans_slash(self, ctx):
        """
        Returns a list of all users in the server that do not have a corresponding DiscordUser in Alliance Auth.

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        await ctx.defer()

        payload = "The following Users cannot be located in Alliance Auth \n"
        member_list = ctx.guild.members

        for member in member_list:
            member_id = member.id

            try:
                discord_exists = DiscordUser.objects.get(uid=member_id)
            except Exception:
                discord_exists = False

            try:
                discord_is_bot = member.bot
            except Exception:
                discord_is_bot = False

            if discord_exists is not False:
                # Nothing to do, the user exists. Move on with your life, dude.
                pass

            elif discord_is_bot is True:
                # Let's also ignore bots here
                pass
            else:
                payload = payload + member.mention + "\n"

        try:
            await ctx.respond(payload)
        except Exception:
            await ctx.respond(payload[0:1999])

    @admin_commands.command(
        name="get_webhooks",
        description="Returns a list of all webhooks in the channel",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def get_webhooks(self, ctx):
        """
        Returns a list of all webhooks in the channel.
        This command will list all webhooks in the current channel, including their names and URLs.

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        await ctx.defer(ephemeral=True)

        hooks = await ctx.channel.webhooks()

        if len(hooks) == 0:
            # name = "{}_webhook".format(ctx.channel.name.replace(" ", "_"))
            # hook = await ctx.channel.create_webhook(name=name)

            return await ctx.respond("No webhooks for this channel.", ephemeral=True)

        else:
            strs = []

            for hook in hooks:
                strs.append(f"{hook.name} - {hook.url}")

            return await ctx.respond("\n".join(strs), ephemeral=True)

    @admin_commands.command(
        name="uptime",
        description="Returns the uptime of the bot",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def uptime(self, ctx):
        """
        Returns the uptime of the bot.

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        try:
            return await ctx.respond(
                pendulum.now(tz="UTC").diff_for_humans(
                    other=self.bot.currentuptime, absolute=True
                ),
                ephemeral=True,
            )
        except AttributeError:
            return await ctx.respond("Still Booting up!", ephemeral=True)

    @admin_commands.command(
        name="versions",
        description="Returns a list of all AA apps and their versions",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def versions(self, ctx):
        """
        Returns a list of all AA apps and their versions.

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        await ctx.defer(ephemeral=True)

        try:
            output = {}
            # Standard Library
            from importlib.metadata import packages_distributions, version

            packages = packages_distributions()

            for _ext, _d in self.bot.extensions.items():
                _e = _ext.split(".")[0]

                if _e in packages:
                    _p = packages[_e][0]

                    if _p not in output:
                        output[_p] = {"version": "Unknown", "extensions": []}

                    output[_p]["version"] = version(_p)
                    output[_p]["extensions"].append(_ext)

            msg = []

            for _p, _d in output.items():
                msg.append(f"## {_p} `{_d['version']}`")

                for _c in _d["extensions"]:
                    msg.append(f"- {_c}")

            return await ctx.respond(
                embed=Embed(title="Loaded Extensions", description="\n".join(msg)),
                ephemeral=True,
            )
        except Exception as e:
            return await ctx.respond(f"Something went wrong! {e}", ephemeral=True)

    @admin_commands.command(
        name="commands",
        description="Returns a list of all commands available to the bot",
        guild_ids=app_settings.get_all_servers(),
    )
    async def command_list(self, ctx):
        """
        Returns a list of all commands available to the bot.

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        await ctx.defer(ephemeral=True)

        helptext = Paginator()
        helptext.add_line(
            "Parent          Command                        "
            "Module                                   "
            "Type"
        )
        helptext.add_line("-" * 110)

        coms = set()

        for command in self.bot.walk_application_commands():
            if isinstance(command, SlashCommandGroup):
                continue

            _parent = f"{command.full_parent_name.ljust(15)}{' ' if command.full_parent_name.rjust else ''}"
            _msg = f"{_parent}{command.name.ljust(30)} {command.module.ljust(40)} {command.__class__.__name__}"

            if _msg not in coms:
                coms.add(_msg)
                helptext.add_line(_msg)
            else:
                pass

        for _str in helptext.pages:
            await ctx.send(_str)

        return await ctx.respond("Done", ephemeral=True)

    @admin_commands.command(
        name="stats",
        description="Returns the bot's task statistics, including uptime, task stats, rate limits, and pending tasks",
        guild_ids=app_settings.get_all_servers(),
    )
    @sender_is_admin()
    async def stats(self, ctx):
        """
        Returns the bot's task statistics, including uptime, task stats, rate limits, and pending tasks.

        :param ctx:
        :type ctx:
        :return:
        :rtype:
        """

        await ctx.defer(ephemeral=True)

        embed = Embed(title="Bot Task Stats!")

        try:
            uptime = pendulum.now(tz="UTC").diff_for_humans(
                other=self.bot.currentuptime, absolute=True
            )

            embed.description = f"Up time: {uptime}"
        except Exception as e:
            logger.debug(f"Up time Fail {e}", stack_info=True)
        try:
            embed.add_field(
                name="Task Stats", value=self.bot.statistics.to_string(), inline=False
            )
        except Exception as e:
            logger.debug(f"Stats Fail {e}", stack_info=True)

        try:
            rate_limits = self.bot.rate_limits.get_rate_limits()

            if rate_limits:
                embed.add_field(name="Rate Limits", value=rate_limits, inline=False)
        except Exception as e:
            logger.debug(f"Rates Fail {e}", stack_info=True)

        try:
            queued_tasks = len(self.bot.tasks)
            pending_tasks = self.bot.pending_tasks.outstanding()

            embed.add_field(
                name="Tasks Pending",
                value=f"```Queued:  {queued_tasks}\nDefered: {pending_tasks}```",
                inline=False,
            )
        except Exception as e:
            logger.debug(f"Tasks Fail {e}", stack_info=True)

        return await ctx.respond("", embed=embed, ephemeral=True)

    @admin_commands.command(
        name="force_sync",
        description="Queue update tasks for a character and all their alts",
        guild_ids=app_settings.get_all_servers(),
    )
    @option(
        name="character",
        description="Search for a Character!",
        autocomplete=search_characters,
    )
    @sender_is_admin()
    async def slash_sync(self, ctx, character: str):
        """
        Queue update tasks for the character and all alts.

        :param ctx:
        :type ctx:
        :param character:
        :type character:
        :return:
        :rtype:
        """

        try:
            char = EveCharacter.objects.get(character_name=character)
            alts = (
                char.character_ownership.user.character_ownerships.all()
                .select_related("character")
                .values_list("character__character_id", flat=True)
            )

            for c in alts:
                update_character.delay(c)

            return await ctx.respond(
                f"Sent tasks to update **{character}**'s characters", ephemeral=True
            )
        except EveCharacter.DoesNotExist:
            return await ctx.respond(
                f"Character **{character}** does not exist in our Auth system",
                ephemeral=True,
            )
        except ObjectDoesNotExist:
            return await ctx.respond(
                f"**{character}** is unlinked unable to update characters",
                ephemeral=True,
            )

    @admin_commands.command(
        name="sync_commands",
        description="Sync the bot's commands with Discord",
        guild_ids=app_settings.get_all_servers(),
    )
    @option(name="force", description="Force Sync Everything")
    @sender_is_admin()
    async def sync_commands(self, ctx, force: bool):
        """
        Sync the bot's commands with Discord.

        :param ctx:
        :type ctx:
        :param force:
        :type force:
        :return:
        :rtype:
        """

        await ctx.defer(ephemeral=True)
        await self.bot.sync_commands(force=force)

        return await ctx.respond("Sync Complete!", ephemeral=True)

    @commands.user_command(name="Group Sync", guild_ids=app_settings.get_all_servers())
    @sender_is_admin()
    async def group_sync_user_context(self, ctx, user):
        """
        Sync the groups for a user

        :param ctx:
        :type ctx:
        :param user:
        :type user:
        :return:
        :rtype:
        """

        auth_user = auth.get_auth_user(user=user, guild=ctx.guild)
        main_character = auth_user.profile.main_character
        update_groups.delay(auth_user.pk)

        return await ctx.respond(
            f"Requested Group Sync for {main_character}",
            ephemeral=True,
        )

    @commands.user_command(
        name="Nickname Sync", guild_ids=app_settings.get_all_servers()
    )
    @sender_is_admin()
    async def nick_sync_user_context(self, ctx, user):
        """
        Sync the nickname for a user

        :param ctx:
        :type ctx:
        :param user:
        :type user:
        :return:
        :rtype:
        """

        auth_user = auth.get_auth_user(user=user, guild=ctx.guild)
        main_character = auth_user.profile.main_character
        update_nickname.delay(auth_user.pk)

        return await ctx.respond(
            f"Requested Nickname Sync for {main_character}",
            ephemeral=True,
        )


def setup(bot):
    """
    Set up the cog

    :param bot:
    :type bot:
    :return:
    :rtype:
    """

    # Unload the Admin cog from `aadiscordbot`, so we can load our own.
    unload_cog(bot=bot, cog_name="Admin")

    # Add the Admin cog to the bot
    bot.add_cog(Admin(bot))
