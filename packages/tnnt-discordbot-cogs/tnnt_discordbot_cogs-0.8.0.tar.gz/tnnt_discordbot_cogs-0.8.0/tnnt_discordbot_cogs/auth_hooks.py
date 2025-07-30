"""
Hooking into the auth system
"""

# Alliance Auth
from allianceauth import hooks


@hooks.register("discord_cogs_hook")
def register_cogs():
    """
    Registering our discord cogs
    :return:
    :rtype:
    """

    return [
        "tnnt_discordbot_cogs.cogs.about",
        "tnnt_discordbot_cogs.cogs.admin",
        "tnnt_discordbot_cogs.cogs.auth",
        "tnnt_discordbot_cogs.cogs.lookup",
        "tnnt_discordbot_cogs.cogs.models",
        "tnnt_discordbot_cogs.cogs.price_check",
        "tnnt_discordbot_cogs.cogs.recruit_me",
        "tnnt_discordbot_cogs.cogs.welcome",
    ]
