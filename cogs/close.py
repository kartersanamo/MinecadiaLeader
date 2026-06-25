from discord.ext import commands
from services.permission_service import is_staff
from discord import app_commands
from datetime import datetime
import requests
import discord

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
    channel = discord.utils.get(interaction.guild.channels, id=944567150130110494)
    user = None
    for target in interaction.channel.overwrites:
      if isinstance(target, discord.Member) and not target.bot:
        user = target
        break
    if user is None:
      user_name = "Unknown"
      user_id = "0000000000000000000"
    else:
      user_name = user.name
      user_id = user.id
    content = f"Minecadia Leader Bot: Kitmap Bundle Ticket\n - Opened by: {user_name} ({user_id})\n \n---------------------------------------------------------------------------------\n \n"
    async for message in interaction.channel.history(limit=None, oldest_first=True):
      content += f"[{message.created_at.strftime('%a, %b %d, %Y, %I:%M %p')}]\n{message.author.name} : {message.author.id}\n\t{message.content}\n \n"
    content += f"---------------------------------------------------------------------------------\n \n   - Closure Reason: {reason}\n   - Closed By: {interaction.user}\n   - Closed At: {datetime.utcnow().strftime('%a, %b %d, %Y, %I:%M %p')} UTC"
    response = requests.post(
      "https://paste.minecadia.com/documents",
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      data=content.encode("utf-8"),
      timeout=30,
    )
    key = response.json()["key"]
    link = f"https://paste.minecadia.com/{key}"
    embed = discord.Embed(color=discord.Color.red(), title=f"🎟️ {interaction.channel.name} log", description=f"__**Kitmap Bundle Ticket**__\n**Reason:** {reason}\n**Owner:** {user_name} ({user_id})\n**Transcript:** {link}")
    logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await channel.send(embed=embed, file=discord.File("assets/Logo.png"))
    if user is not None:
      try:
        dm_channel = await user.create_dm()
        await dm_channel.send(embed=embed, file=discord.File("assets/Logo.png"))
      except Exception:
        pass
    await interaction.channel.delete()


async def setup(client:commands.Bot) -> None:
  await client.add_cog(close(client))
