"""
Application init
"""

# Third Party
import requests

__version__ = "0.8.0"
__title__ = "TN-NT Discordbot Cogs"

__package_name__ = "tn-nt-discordbot-cogs"
__package_name_verbose__ = "Terra Nanotech Discordbot Cogs"
__package_name_useragent__ = "Terra-Nanotech-Discordbot-Cogs"
__app_name__ = "tnnt_discordbot_cogs"
__github_url__ = f"https://github.com/ppfeufer/{__package_name__}"
__user_agent__ = (
    f"{__package_name_useragent__}/{__version__} "
    f"(+{__github_url__}) requests/{requests.__version__}"
)
