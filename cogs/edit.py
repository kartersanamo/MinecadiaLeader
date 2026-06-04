from discord.ext import commands
from discord import app_commands
import discord

from ui.views.edit_faction_view import EditFactionView
from utils.embeds import get_embed_logo_url
from utils.permissions import is_staff


class EditCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="edit", description="Allows server admins to edit faction information")
    @app_commands.check(is_staff)
    @app_commands.describe(faction="The faction to edit")
    async def edit(self, interaction: discord.Interaction, faction: str = None):
        if interaction.guild is None:
            return await interaction.response.send_message(
                content="Commands cannot be ran in DMs!", ephemeral=True
            )
        embed = discord.Embed(
            title="Minecadia Leader Faction Editor",
            description="Here's the information on `Awaiting Faction` ...",
            color=discord.Color.red(),
        )
        logo_url = get_embed_logo_url("assets/Logo.png")
        embed.set_footer(text="Minecadia Leader Bot", icon_url=logo_url)
        embed.add_field(name="Leader", value="...")
        embed.add_field(name="Coleader #1", value="...")
        embed.add_field(name="Coleader #2", value="...")
        embed.add_field(name="Channel", value="...")
        embed.set_thumbnail(url="attachment://Logo.png")
        the_view = EditFactionView(self.client)
        await interaction.response.send_message(
            embed=embed, ephemeral=True, view=the_view, file=discord.File("assets/Logo.png")
        )
        if faction:
            the_view.faction_name = faction
            await the_view.update_message(interaction)

    @edit.error
    async def edit_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(content=error, ephemeral=True)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(EditCog(client))
