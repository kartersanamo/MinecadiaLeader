from discord.ext import commands
from services.permission_service import is_staff
from discord import app_commands
import discord


class Lock(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name="lock", description="Locks the /request thread")
  @app_commands.check(is_staff)
  async def lock(self, interaction: discord.Interaction):
    if interaction.guild is None:
      return await interaction.response.send_message(content="Commands cannot be ran in DMs!", ephemeral=True)
    if type(interaction.channel) != discord.Thread:
      return await interaction.response.send_message(content = "Failed! This can only be ran in a /request thread!", ephemeral = True)
    if interaction.channel.locked:
      return await interaction.response.send_message(content = "Failed! This thread has already been locked! Ask an admin if you need this reopened.", ephemeral = True)
    await interaction.channel.edit(locked = True)
    await interaction.client.app.statistics.increment_statistic(
        interaction.user, "threads_locked"
    )
    embed = discord.Embed(title = "Thread locked!",
                          color= discord.Color.red(),
                          description = f"{interaction.user.mention} has locked this thread.")
    logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await interaction.response.send_message(embed = embed, file = discord.File("assets/Logo.png"))
  
  @lock.error
  async def lock_error(self, interaction: discord.Interaction, error):
    await interaction.response.send_message(content=error, ephemeral=True)
  
async def setup(client:commands.Bot) -> None:
  await client.add_cog(Lock(client))