# Terra Nanotech Discordbot Cogs<a name="terra-nanotech-discordbot-cogs"></a>

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/terra-nanotech/tn-nt-discordbot-cogs/master.svg)](https://results.pre-commit.ci/latest/github/terra-nanotech/tn-nt-discordbot-cogs/master)

A collection of cogs for
[AA-Discordbot](https://github.com/pvyParts/allianceauth-discordbot)

______________________________________________________________________

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=1 -->

- [Terra Nanotech Discordbot Cogs](#terra-nanotech-discordbot-cogs)
  - [Important Information](#important-information)
  - [Install](#install)
  - [Commands](#commands)

<!-- mdformat-toc end -->

______________________________________________________________________

## Important Information<a name="important-information"></a>

These Discord bot COGs are specially tailored for the corporation Terra Nanotech.
They are COGs of apps we use, so they fit our needs.

> **Note**
>
> If you install this app, you need to be aware that there will be
> no support for any kind of issues you might encounter, and you have to figure it out
> on your own.

## Install<a name="install"></a>

```shell
pip install tnnt-discordbot-cogs
```

In `local.py` right after `INSTALLED_APPS`:

```python
# Terra Nanotech Discordbot Cogs
INSTALLED_APPS += ["eveuniverse", "tnnt_discordbot_cogs"]
```

Run DB migrations and restart supervisor.

## Commands<a name="commands"></a>

| Module/Cog                              | Group    | Command             | Description                                                                                                |
| --------------------------------------- | -------- | ------------------- | ---------------------------------------------------------------------------------------------------------- |
| `tnnt_discordbot_cogs.cogs.about`       |          | `about`             | Shows information about the bot                                                                            |
| `tnnt_discordbot_cogs.cogs.admin`       | `admin`  | `add_role`          | Add a role as read/write to a channel                                                                      |
|                                         | `admin`  | `add_role_read`     | Add a role as read only to a channel                                                                       |
|                                         | `admin`  | `clear_empty_roles` | Deletes all roles in the server that have no members                                                       |
|                                         | `admin`  | `commands`          | Returns a list of all slash commands available to the bot                                                  |
|                                         | `admin`  | `demote_from_god`   | Remove admin from a role                                                                                   |
|                                         | `admin`  | `empty_roles`       | Returns a list of all roles in the server, including those with no members and those without an auth group |
|                                         | `admin`  | `force_sync`        | Queue update tasks for a character and all their alts                                                      |
|                                         | `admin`  | `get_webhooks`      | Returns a list of all webhooks in the channel                                                              |
|                                         | `admin`  | `new_channel`       | Create a new channel in the specified category and set permissions for the first role                      |
|                                         | `admin`  | `orphans`           | Returns a list of all users in the server that do not have a corresponding DiscordUser in Auth             |
|                                         | `admin`  | `promote_to_god`    | Set a role as admin                                                                                        |
|                                         | `admin`  | `rem_role`          | Remove a role from a channel                                                                               |
|                                         | `admin`  | `stats`             | Returns the bot's task statistics, including uptime, task stats, rate limits, and pending tasks            |
|                                         | `admin`  | `sync_commands`     | Sync the bot's commands with Discord                                                                       |
|                                         | `admin`  | `uptime`            | Returns the uptime of the bot                                                                              |
|                                         | `admin`  | `versions`          | Returns a list of all AA apps and their versions                                                           |
| `tnnt_discordbot_cogs.cogs.auth`        |          | `auth`              | Returns a link to the TN-NT Auth System                                                                    |
| `tnnt_discordbot_cogs.cogs.lookup`      | `lookup` | `character`         | Looks up a character in the Auth system and returns information about them                                 |
|                                         | `lookup` | `corporation`       | Looks up a corporation and returns information about its members                                           |
| `tnnt_discordbot_cogs.cogs.models`      | `models` | `populate`          | Populate Django Models for all channels in the server                                                      |
| `tnnt_discordbot_cogs.cogs.price_check` | `price`  | `all_markets`       | Check an item price on all major market hubs                                                               |
|                                         | `price`  | `amarr`             | Check an item price on Amarr market                                                                        |
|                                         | `price`  | `dodixie`           | Check an item price on Dodixie market                                                                      |
|                                         | `price`  | `hek`               | Check an item price on Hek market                                                                          |
|                                         | `price`  | `jita`              | Check an item price on Jita market                                                                         |
|                                         | `price`  | `plex`              | Check the PLEX price on the global PLEX market                                                             |
|                                         | `price`  | `rens`              | Check an item price on Rens market                                                                         |
| `tnnt_discordbot_cogs.cogs.recruit_me`  |          | `recruit_me`        | Get hold of a recruiter                                                                                    |
