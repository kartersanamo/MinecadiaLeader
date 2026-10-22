from discord.ext import commands
from discord import app_commands
import requests
import discord
from core.database import execute


class PurgeConfirmationView(discord.ui.View):
  def __init__(self, cog, interaction: discord.Interaction):
    super().__init__(timeout=60)
    self.cog = cog
    self.source_interaction = interaction

  async def interaction_check(self, interaction: discord.Interaction) -> bool:
    if interaction.user.id != self.source_interaction.user.id:
      await interaction.response.send_message("Only the user who started this purge can respond.", ephemeral=True)
      return False
    return True

  @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger)
  async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
    for child in self.children:
      child.disabled = True
    await interaction.response.defer()
    await self.cog.run_purge(self.source_interaction)
    self.stop()

  @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
  async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
    await interaction.response.edit_message(
      content="Purge cancelled.",
      embed=None,
      view=None,
    )
    self.stop()


class purge(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  async def update_status(self, interaction: discord.Interaction, status: str, color=discord.Color.blurple(), link=None):
    embed = discord.Embed(title="Faction purge", description=status, color=color)
    if link is not None:
      embed.add_field(name="Transcript", value=link, inline=False)
    embed.set_footer(text="Minecadia Leader Bot")
    await interaction.edit_original_response(content=None, embed=embed, view=None)
  
  async def get_all_messages(self, interaction, channel):
    content = ""
    async for message in channel.history(limit=None, oldest_first=True):
          if len(message.embeds)>0:
            try:
              split = message.embeds[0].description.split("\n")
            except Exception:
              split = [" "]
            formatted="\ --- Message Embed ---\n"
            for line in split:
              formatted+= f"\t| {line}\n"
            try:
              dic = message.embeds[0].to_dict()
              footer = dic['footer']
              formatted+=f"\t|\n\t| {footer['text']}\n"
            except Exception:
              pass
            formatted+="\t\ ---------------------"
          else:
            formatted = "[message content unavailable without Message Content intent]"
          content += f"[{message.created_at.strftime('%a, %b %d, %Y, %I:%M %p')}]\n{message.author.name} : {message.author.id}\n\t{formatted}\n \n"
    return content
  
  async def get_faction_info(self, faction_name):
      rows = await execute(f"SELECT * FROM leader_factions WHERE faction_name = '{faction_name}'")
      if rows:
        return rows[0]
      else:
        return "Fail"
      
  @app_commands.command(name="purge", description="Purges all of faction information")
  async def purge(self, interaction: discord.Interaction):
    if interaction.guild is None:
            return await interaction.response.send_message(content="Commands cannot be ran in DMs!", ephemeral=True)
    await interaction.response.send_message(
      "This will delete all faction information, remove faction roles, delete ticket channels, and reset the faction list. Continue?",
      ephemeral=True,
      view=PurgeConfirmationView(self, interaction),
    )

  async def run_purge(self, interaction: discord.Interaction):
    try:
      await self._execute_purge(interaction)
    except Exception as error:
      await self.update_status(
        interaction,
        f"Purge failed: {type(error).__name__}. No further purge steps were run.",
        discord.Color.red(),
      )

  async def _execute_purge(self, interaction: discord.Interaction):
    await self.update_status(interaction, "Starting purge...")
    # Remove everyone's roles & reset nicknames
    await self.update_status(interaction, "Fetching server members...")
    leader_role = discord.utils.get(interaction.guild.roles, name= "Faction Leader")
    coleader_role = discord.utils.get(interaction.guild.roles, name= "Faction Coleader")
    # Use the REST member list rather than the (potentially incomplete)
    # privileged member cache.
    members = [member async for member in interaction.guild.fetch_members(limit=None)]
    await self.update_status(interaction, "Removing faction roles and resetting nicknames...")
    for member in members:
      if leader_role in member.roles:
        await member.remove_roles(leader_role)
        await member.edit(nick=member.name)
      if coleader_role in member.roles:
        await member.remove_roles(coleader_role)
        await member.edit(nick=member.name)
    # Remove all factions from the database
    await self.update_status(interaction, "Deleting faction information from the database...")
    await execute(f"DELETE FROM leader_factions")  
    # Create a paste link with each ticket's (open & archived) information in it
    content = ""
    deleted_channel_count = 0
    await self.update_status(interaction, "Collecting ticket transcripts...")
    for name in ["Faction Tickets", "Faction Tickets #2", "Archived Channels"]:
      category = discord.utils.get(interaction.guild.categories, name=name)
      if category is None:
        continue
      for channel in category.channels:
        faction_info = await self.get_faction_info(channel.name.split('-')[0])
        if faction_info=="Fail":
          faction_info={"faction_name": "N/A", "coleader_id_1": "", "coleader_id_2": "", "leader_id": ""}
        try:
          leader_name = (await interaction.guild.fetch_member(int(faction_info['leader_id']))).name
        except Exception:
          leader_name = "N/A"
        try:
          coleader_1_name = (await interaction.guild.fetch_member(int(faction_info['coleader_id_1']))).name
        except Exception:
          coleader_1_name = "N/A"
        try:
          coleader_2_name = (await interaction.guild.fetch_member(int(faction_info['coleader_id_2']))).name
        except Exception:
          coleader_2_name = "N/A"
        string = f"----------------------------------------------------------\nFaction Name: {faction_info['faction_name']}\nLeader: {leader_name} ({faction_info['leader_id']})\nColeader #1: {coleader_1_name} ({faction_info['coleader_id_1']})\nColeader #2: {coleader_2_name} ({faction_info['coleader_id_2']})\n----------------------------------------------------------\n"
        string += f"Messages Below\n{await self.get_all_messages(interaction, channel)}\n----------------------------------------------------------\nThreads Below\n"
        for thread in channel.threads:
          string+= f"{await self.get_all_messages(interaction, thread)}\n \n"
        content+=string+"\n \n \n"
        string+= "----------------------------------------------------------"
        await channel.delete(reason="via /purge")
        deleted_channel_count += 1
        await self.update_status(interaction, f"Deleted {deleted_channel_count} ticket channel(s)...")
    await self.update_status(interaction, "Uploading the ticket transcript...")
    content = content.encode("utf-8")
    response = requests.post(
      "https://paste.minecadia.com/documents",
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      data=content,
      timeout=30,
    )
    key = response.json()["key"]
    link = f"https://paste.minecadia.com/{key}"
    status = f"Purge completed by `@{interaction.user}`"
    if deleted_channel_count == 0:
      status += " (No ticket channels found to purge.)"
    await self.update_status(interaction, status, discord.Color.green(), link)
    log_channel = interaction.guild.get_channel(941766120082395158)
    if log_channel is not None:
      await log_channel.send(content=f"{status} {link}")
    # Reset the faction list
    await self.update_status(interaction, "Resetting the faction list...", discord.Color.blurple(), link)
    channel = interaction.guild.get_channel(1046530489994973236)
    if channel is not None:
      async for faction_message in channel.history(limit=1, oldest_first=True):
        embed = discord.Embed(title=f"Factions in Season 3 (0)", description=f"```None```", color=discord.Color.red())
        logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
        embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
        await faction_message.edit(embed=embed)
    await self.update_status(interaction, status, discord.Color.green(), link)
    

async def setup(client:commands.Bot) -> None:
  await client.add_cog(purge(client))