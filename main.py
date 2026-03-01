from Cogs.tickets import TicketButtons
from Cogs.factions import RoleButtons
# from Cogs.purge import Confirm
from discord.ext import commands
from typing import Literal
import discord
import json
import os
from dotenv import load_dotenv

load_dotenv()

class Client(commands.Bot):
  def __init__(self):
    super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=discord.Intents().all())

    self.cogslist = ["listthreads", "embed", "request", "purge", "factions", "edit", "tickets", "close", "rename", "lock", "adminlist"]

  async def setup_hook(self):
    for ext in self.cogslist:
      await self.load_extension("Cogs."+ext)
    self.add_view(TicketButtons()) 
    self.add_view(RoleButtons())
    # self.add_view(Confirm())

  async def on_ready(self):
    print(" Logged in as " + self.user.name)
    await self.tree.sync()
    
  async def on_command_error(self, ctx, error):
    print(" Command Error " + str(error))

client = Client()

@client.tree.command(name="reload", description="Reloads a Cog Class")
async def reload(interaction: discord.Interaction, cog:Literal["ListThreads", "Rename", "Embed", "Request", "Purge", "Factions", "Edit", "Tickets", "Close", "Lock", "AdminList"]):
    if interaction.user.id==837793755838939157:
        await client.reload_extension(f"Cogs.{cog.lower()}")
        await interaction.response.send_message(f"Successfully reloaded **{cog}.py**", ephemeral=True) 
    else:
        return await interaction.response.send_message(f"You are not permitted to do this!", ephemeral=True)

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Set DISCORD_TOKEN in .env")

client.run(TOKEN)