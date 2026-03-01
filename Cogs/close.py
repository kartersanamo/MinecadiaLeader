from Cogs.factions import is_staff
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import requests
import discord
import json

class close(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @app_commands.command(name="close", description="Closes the ticket channel")
  @app_commands.describe(reason="The reason for closing the ticket")
  @app_commands.check(is_staff)
  async def close(self, interaction: discord.Interaction, reason:str):
    if interaction.guild is None:
            return await interaction.response.send_message(content="Commands cannot be ran in DMs!", ephemeral=True)
    category_name = interaction.channel.category.name
    if category_name != "Kitmap Bundle Tickets" and category_name != "Kitmap Bundle Tickets #2":
      return await interaction.response.send_message(content="This is not a ticket channel!", ephemeral=True)
    await interaction.response.defer()
    channel = discord.utils.get(interaction.guild.channels, name="ticket-logs")
    for overwrite in interaction.channel.overwrites:
      if type(overwrite) == discord.member.Member:
        user = overwrite
        user_name = user.name
        user_id = user.id
    if not user:
      user_name = "Unknown"
      user_id = "0000000000000000000"
    content = f"Minecadia Leader Bot: Kitmap Bundle Ticket\n - Opened by: {user_name} ({user_id})\n \n---------------------------------------------------------------------------------\n \n"
    async for message in interaction.channel.history(limit=None, oldest_first=True):
      content += f"[{message.created_at.strftime('%a, %b %d, %Y, %I:%M %p')}]\n{message.author.name} : {message.author.id}\n\t{message.content}\n \n"
    content += f"---------------------------------------------------------------------------------\n \n   - Closure Reason: {reason}\n   - Closed By: {interaction.user}\n   - Closed At: {datetime.utcnow().strftime('%a, %b %d, %Y, %I:%M %p')} UTC"
    content = content.encode("utf-8")
    key = json.loads(requests.post('https://paste.md-5.net/documents', data=content).content)['key']
    link = f"https://paste.md-5.net/{key}"
    embed = discord.Embed(color=discord.Color.red(), title=f"🎟️ {interaction.channel.name} log", description=f"__**Kitmap Bundle Ticket**__\n**Reason:** {reason}\n**Owner:** {user_name} ({user_id})\n**Transcript:** {link}")
    from Assets.functions import get_embed_logo_url
    logo_url = get_embed_logo_url("Assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await channel.send(embed=embed, file=discord.File("Assets/Logo.png"))
    try:
      channel = await user.create_dm()
      await channel.send(embed=embed, file=discord.File("Assets/Logo.png"))
    except:
      pass
    await interaction.channel.delete()

  @close.error
  async def close_error(self, interaction: discord.Interaction, error):
    await interaction.response.send_message(content=error, ephemeral=True)

async def setup(client:commands.Bot) -> None:
  await client.add_cog(close(client))