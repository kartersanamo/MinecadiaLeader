from typing import Literal

import discord
import requests
from discord.ext import commands, tasks
from discord import app_commands

from ui.modals.request_modal import RequestModal


class RequestCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.url = (
            "https://api.telegram.org/botREMOVED/sendMessage"
        )

    @commands.Cog.listener()
    async def on_ready(self):
        self.send_mass_strike_reports.start()

    @tasks.loop(hours=6)
    async def send_mass_strike_reports(self):
        guild = self.client.get_guild(941608654593998878)
        threads = [
            f"{thread.name} ({thread.parent.name.split('-')[0]})"
            for thread in guild.threads
            if (thread.parent and not thread.locked)
        ]
        if len(threads) == 0:
            return
        telegram_message: str = f"There are {len(threads)} threads open!\n"
        if threads:
            telegram_message += "\n".join(threads)
        payload = {"chat_id": "-1001437784396", "text": telegram_message}
        requests.post(self.url, json=payload)

    @app_commands.command(
        name="request", description="Requests support inside of your faction ticket"
    )
    @app_commands.describe(type="The type of request thread to open")
    async def request(
        self,
        interaction: discord.Interaction,
        type: Literal[
            "Strike Report",
            "Strike Appeal",
            "Inside Dispute",
            "Bundle Request",
            "Leader Transfer",
        ],
    ):
        if interaction.guild is None:
            return await interaction.response.send_message(
                content="Commands cannot be ran in DMs!", ephemeral=True
            )
        if interaction.channel.category.id not in [
            1154577495648124949,
            1196515275764408372,
        ]:
            return await interaction.response.send_message(
                content="Failed! This can only be ran inside of your faction ticket!",
                ephemeral=True,
            )
        await interaction.response.send_modal(RequestModal(type))



async def setup(client: commands.Bot) -> None:
    await client.add_cog(RequestCog(client))
