from discord.ext import commands
from services.permission_service import is_staff
from discord import app_commands
import discord

class rename(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name="rename", description="Renames the ticket channel")
  @app_commands.describe(name="The name to rename the ticket to")
  @app_commands.check(is_staff)
  async def rename(self, interaction: discord.Interaction, name:str):
    if interaction.guild is None:
            return await interaction.response.send_message(content="Commands cannot be ran in DMs!", ephemeral=True)
    old_name = interaction.channel.name
    if interaction.channel.category.name=="Kitmap Bundle Tickets" or interaction.channel.category.name=="Kitmap Bundle Tickets #2" or type(interaction.channel) == discord.Thread:
      try:
        await interaction.channel.edit(name=name)
        if type(interaction.channel) == discord.Thread:
           await interaction.response.send_message(content=f"Successfully changed the channel name from **{old_name}** to **{name.replace(' ', '-')}**", ephemeral = True)
        await interaction.response.send_message(content=f"Successfully changed the channel name from **{old_name}** to **{name.replace(' ', '-')}**")
      except:
        await interaction.response.send_message(content=f"Failed! This name contains words not allowed by discord", ephemeral=True)
  
  @rename.error
  async def rename_error(self, interaction: discord.Interaction, error):
    await interaction.response.send_message(content=error, ephemeral=True)
  
async def setup(client:commands.Bot) -> None:
  await client.add_cog(rename(client))