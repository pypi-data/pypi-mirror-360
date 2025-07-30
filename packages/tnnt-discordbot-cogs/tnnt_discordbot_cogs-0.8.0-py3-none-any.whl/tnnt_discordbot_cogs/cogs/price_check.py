"""
Market Price Checks cog for discordbot - https://github.com/pvyParts/allianceauth-discordbot
"""

# Standard Library
import locale
import logging

# Third Party
import requests
from discord.colour import Color
from discord.commands import SlashCommandGroup
from discord.embeds import Embed
from discord.ext import commands

# Alliance Auth Discord Bot
from aadiscordbot import app_settings

# Alliance Auth (External Libs)
from eveuniverse.models import EveEntity

# Terra Nanotech Discordbot Cogs
from tnnt_discordbot_cogs import __user_agent__
from tnnt_discordbot_cogs.helper import unload_cog

logger = logging.getLogger(__name__)


class PriceCheck(commands.Cog):
    """
    Price checks on Jita, Amarr, Rens, Hek and Dodixie markets
    """

    imageserver_url = "https://images.evetech.net"

    price_commands = SlashCommandGroup(
        "price", "Server Admin Commands", guild_ids=app_settings.get_all_servers()
    )

    def __init__(self, bot):
        """
        Initialize the PriceCheck cog

        :param bot:
        :type bot:
        """

        self.bot = bot

    @staticmethod
    def _get_plex_market():
        """
        Get the PLEX market data

        :return:
        :rtype:
        """

        return [{"name": "Global PLEX Market", "region_id": 19000001}]

    @staticmethod
    def _get_market_data(market: dict, eve_type_id: str) -> dict | None:
        """
        Get the market data for a specific system and item type
        This method fetches market data from the Fuzzwork API.
        The Fuzzwork API provides aggregated market data for EVE Online.
        https://market.fuzzwork.co.uk/aggregates/

        :param market: The market dictionary containing system ID and name
        :type market: dict
        :param eve_type_id: The EVE type ID of the item to fetch data for
        :type eve_type_id: str
        :return: Market data as a json or None if the request fails
        :rtype: Optional[dict]
        """

        market_system_id = market.get("system_id", None)
        market_region_id = market.get("region_id", None)

        url = "https://market.fuzzwork.co.uk/aggregates/"

        url_params = {
            "region" if market_region_id else "system": market_region_id
            or market_system_id,
            "types": eve_type_id,
        }

        request_headers = {"User-Agent": __user_agent__}

        try:
            response = requests.get(
                url=url, params=url_params, headers=request_headers, timeout=5.00
            )
            response.raise_for_status()

            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch market data: {e}")

            return None

    @classmethod
    def _build_market_price_embed(
        cls, embed: Embed, market: dict, item_name: str, eve_type_id: str
    ) -> None:
        """
        Build the price embed for the selected market

        :param embed:
        :type embed:
        :param market:
        :type market:
        :param item_name:
        :type item_name:
        :param eve_type_id:
        :type eve_type_id:
        :return:
        :rtype:
        """

        market_name = market["name"]
        market_data = cls._get_market_data(market=market, eve_type_id=eve_type_id)

        embed.add_field(
            name=f"{market_name}",
            value=f"Prices for {item_name} on the {market_name}.",
            inline=False,
        )

        if market_data:
            sell_min = market_data[eve_type_id]["sell"]["min"]
            sell_order_count = int(market_data[eve_type_id]["sell"]["orderCount"])
            buy_max = market_data[eve_type_id]["buy"]["max"]
            buy_order_count = int(market_data[eve_type_id]["buy"]["orderCount"])
            thumbnail_url = f"{cls.imageserver_url}/types/{eve_type_id}/icon?size=64"

            # Set the Embed thumbnail
            embed.set_thumbnail(url=thumbnail_url)

            locale.setlocale(category=locale.LC_ALL, locale="")

            # Sell order price
            market_min_sell_order_price = locale.format_string(
                f="%.2f", val=float(sell_min), grouping=True
            )

            sell_orders_string = f"{sell_order_count} Orders"
            if sell_order_count == 0:
                market_min_sell_order_price = "No sell orders found"
                sell_orders_string = "No Orders"

            if 0 < sell_order_count < 2:
                sell_orders_string = f"{sell_order_count} Order"

            embed.add_field(
                name=f"Sell Order Price ({sell_orders_string})",
                value=f"{market_min_sell_order_price} ISK",
                inline=True,
            )

            # Buy order price
            market_max_buy_order_price = locale.format_string(
                f="%.2f", val=float(buy_max), grouping=True
            )

            buy_orders_string = f"{buy_order_count} Orders"
            if buy_order_count == 0:
                market_max_buy_order_price = "No buy orders found"
                buy_orders_string = "No Orders"

            if 0 < buy_order_count < 2:
                buy_orders_string = f"{buy_order_count} Order"

            embed.add_field(
                name=f"Buy Order Price ({buy_orders_string})",
                value=f"{market_max_buy_order_price} ISK",
                inline=True,
            )
        else:
            embed.add_field(
                name="API Error",
                value=(f"Could not not fetch the price for the {market_name} market."),
                inline=False,
            )

    @classmethod
    def _price_check(cls, markets, item_name: str = None) -> Embed:
        """
        Check the price of an item on the specified markets

        :param markets:
        :type markets:
        :param item_name:
        :type item_name:
        :return:
        :rtype:
        """

        if item_name:
            # Special case: PLEX market
            if item_name.lower() == "plex":
                item_name = "PLEX"
                markets = cls._get_plex_market()

            try:
                eve_type = (
                    EveEntity.objects.fetch_by_names_esi([item_name])
                    .filter(category=EveEntity.CATEGORY_INVENTORY_TYPE)
                    .values_list("id", flat=True)
                )

                eve_type_id = str(eve_type[0])
            except (EveEntity.DoesNotExist, IndexError):
                embed = Embed(
                    title=f"Price Lookup for {item_name}",
                    color=Color.orange(),
                )

                embed.add_field(
                    name="Error",
                    value=(
                        f"{item_name} could not be found. "
                        "Are you sure you spelled it correctly?"
                    ),
                    inline=False,
                )
            else:
                embed = Embed(
                    title=f"Price Lookup: {item_name}",
                    color=Color.green(),
                )

                for market in markets:
                    cls._build_market_price_embed(
                        embed=embed,
                        market=market,
                        item_name=item_name,
                        eve_type_id=eve_type_id,
                    )
        else:
            embed = Embed(
                title="Price Lookup",
                color=Color.red(),
            )

            embed.add_field(
                name="Error",
                value=(
                    "You forget to enter an item you want to lookup the price for ..."
                ),
                inline=False,
            )

        return embed

    @price_commands.command(
        name="all_markets",
        description="Check an item price on all major market hubs",
    )
    async def price(self, ctx, item_name: str):
        """
        Check an item price on all major market hubs

        :param ctx:
        :type ctx:
        :param item_name:
        :type item_name:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self._price_check(
                markets=[
                    {"name": "Jita Market", "system_id": 30000142},
                    {"name": "Amarr Market", "system_id": 30002187},
                    {"name": "Rens Market", "system_id": 60004588},
                    {"name": "Hek Market", "system_id": 60005686},
                    {"name": "Dodixie Market", "system_id": 30002659},
                ],
                item_name=item_name,
            ),
            ephemeral=True,
        )

    @price_commands.command(
        name="jita",
        description="Check an item price on Jita market",
    )
    async def jita(self, ctx, item_name: str):
        """
        Check an item price on Jita market

        :param ctx:
        :type ctx:
        :param item_name:
        :type item_name:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self._price_check(
                markets=[{"name": "Jita Market", "system_id": 30000142}],
                item_name=item_name,
            ),
            ephemeral=True,
        )

    @price_commands.command(
        name="amarr",
        description="Check an item price on Amarr market",
    )
    async def amarr(self, ctx, item_name: str):
        """
        Check an item price on Amarr market

        :param ctx:
        :type ctx:
        :param item_name:
        :type item_name:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self._price_check(
                markets=[{"name": "Amarr Market", "system_id": 60008494}],
                item_name=item_name,
            ),
            ephemeral=True,
        )

    @price_commands.command(
        name="rens",
        description="Check an item price on Rens market",
    )
    async def rens(self, ctx, item_name: str):
        """
        Check an item price on Rens market

        :param ctx:
        :type ctx:
        :param item_name:
        :type item_name:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self._price_check(
                markets=[{"name": "Rens Market", "system_id": 60004588}],
                item_name=item_name,
            ),
            ephemeral=True,
        )

    @price_commands.command(
        name="hek",
        description="Check an item price on Hek market",
    )
    async def hek(self, ctx, item_name: str):
        """
        Check an item price on Hek market

        :param ctx:
        :type ctx:
        :param item_name:
        :type item_name:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self._price_check(
                markets=[{"name": "Hek Market", "system_id": 60005686}],
                item_name=item_name,
            ),
            ephemeral=True,
        )

    @price_commands.command(
        name="dodixie",
        description="Check an item price on Dodixie market",
    )
    async def dodixie(self, ctx, item_name: str):
        """
        Check an item price on Dodixie market

        :param ctx:
        :type ctx:
        :param item_name:
        :type item_name:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self._price_check(
                markets=[{"name": "Dodixie Market", "system_id": 30002659}],
                item_name=item_name,
            ),
            ephemeral=True,
        )

    @price_commands.command(
        name="plex",
        description="Check the PLEX price on the global PLEX market",
    )
    async def plex(self, ctx):
        """
        Check the PLEX price on the global PLEX market

        :param ctx:
        :type ctx:
        :param item_name:
        :type item_name:
        :return:
        :rtype:
        """

        return await ctx.respond(
            embed=self._price_check(
                markets=[],  # PLEX market is a special case, so keep it empty, it will be set later in the method
                item_name="PLEX",
            ),
            ephemeral=True,
        )


def setup(bot) -> None:
    """
    Set up the cog

    :param bot:
    :type bot:
    :return:
    :rtype:
    """

    # Unload the PriceCheck cog from `aadiscordbot`, so we can load our own.
    unload_cog(bot=bot, cog_name="PriceCheck")

    # Add the PriceCheck cog to the bot
    bot.add_cog(PriceCheck(bot))
