from Cogs.factions import is_staff
from Assets.functions import execute, is_found
from discord.ext import commands
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
    threads_locked_stat = await is_found(interaction.user, "threads_locked")
    await execute(f"UPDATE `statistics` SET `threads_locked` = '{threads_locked_stat + 1}' WHERE `user_ID` = '{interaction.user.id}'")
    embed = discord.Embed(title = "Thread locked!",
                          color= discord.Color.red(),
                          description = f"{interaction.user.mention} has locked this thread.")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = "https://i.imgur.com/DagYV3L.png")
    await interaction.response.send_message(embed = embed)
  
  @lock.error
  async def lock_error(self, interaction: discord.Interaction, error):
    await interaction.response.send_message(content=error, ephemeral=True)
  
async def setup(client:commands.Bot) -> None:
  await client.add_cog(Lock(client))