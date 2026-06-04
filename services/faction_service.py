import discord

from repositories.faction_repository import FactionRepository
from utils.embeds import get_embed_logo_url


class FactionService:
    def __init__(self, repository: FactionRepository | None = None):
        self._repo = repository or FactionRepository()

    async def faction_exists(self, faction: str) -> bool:
        rows = await self._repo.find_by_faction_name(faction)
        return len(rows) != 0

    async def two_coleaders(self, faction: str) -> bool:
        if not await self.faction_exists(faction):
            return False
        rows = await self._repo.find_by_faction_name(faction)
        return bool(rows[0]["coleader_id_1"] and rows[0]["coleader_id_2"])

    async def update_faction_list(self, guild: discord.Guild, channel_name: str = "𝖥𝖺𝖼𝗍𝗂𝗈𝗇-𝖫𝗂𝗌𝗍") -> None:
        rows = await self._repo.all_faction_names()
        channel = discord.utils.get(guild.channels, name=channel_name)
        if channel is None:
            channel = discord.utils.get(guild.channels, name="faction-list")
        if channel is None:
            return
        if len(rows) != 0:
            faction_list = [row["faction_name"] for row in rows]
            string = ", ".join(faction_list)
            count = len(rows)
        else:
            string = "None"
            count = 0
        async for message in channel.history(limit=1, oldest_first=True):
            embed = discord.Embed(
                title=f"Factions list ({count})",
                description=f"```{string}```",
                color=discord.Color.red(),
            )
            logo_url = get_embed_logo_url("assets/Logo.png")
            embed.set_footer(text="Minecadia Leader Bot", icon_url=logo_url)
            await message.edit(embed=embed)
