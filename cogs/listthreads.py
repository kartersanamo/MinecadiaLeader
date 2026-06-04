from discord.ext import commands
from services.permission_service import is_staff
from discord import app_commands
from typing import Literal
import discord

class listthreads(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name="list-threads", description="Lists all of the threads in the discord")
  @app_commands.check(is_staff)
  async def listthreads(self, interaction: discord.Interaction, option: Literal['Locked', 'Unlocked', 'Both'] = 'Unlocked'):
    if interaction.guild is None:
            return await interaction.response.send_message(content="Commands cannot be ran in DMs!", ephemeral=True)
    locked = []
    unlocked = []
    for thread in interaction.guild.threads:
        if thread.parent is None:
          continue
        if thread.locked:
          locked.append(f"{thread.mention} ({thread.parent.name.split('-')[0]})")
        else:
          unlocked.append(f"{thread.mention} ({thread.parent.name.split('-')[0]})")
    embed = discord.Embed(title="Faction Leader Threads", description="Here are all of the threads open right now in the Minecadia Leader Discord...", color=discord.Color.red())
    if len(locked)==0:
      locked = ["None"]
    if len(unlocked)==0:
      unlocked = ["None"]
    if option=="Locked":
      embed.add_field(name="Locked", value="\n".join(locked)[:1024])
    elif option=="Unlocked":
      embed.add_field(name="Unlocked", value="\n".join(unlocked)[:1024])
    else:
      embed.add_field(name="Locked", value="\n".join(locked)[:1024])
      embed.add_field(name="Unlocked", value="\n".join(unlocked)[:1024])
    await interaction.response.send_message(embed=embed)

  #@listthreads.error
  #async def listthreads_error(self, interaction: discord.Interaction, error):
  #  await interaction.response.send_message(content=error, ephemeral=True)

async def setup(client:commands.Bot) -> None:
  await client.add_cog(listthreads(client))