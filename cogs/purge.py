from discord.ext import commands
from discord import app_commands
import json
import requests
import discord
from core.database import execute

class purge(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
  
  async def get_all_messages(self, interaction, channel):
    content = ""
    async for message in channel.history(limit=None, oldest_first=True):
          if len(message.embeds)>0:
            try:
              split = message.embeds[0].description.split("\n")
            except:
              split = [" "]
            formatted="\ --- Message Embed ---\n"
            for line in split:
              formatted+= f"\t| {line}\n"
            try:
              dic = message.embeds[0].to_dict()
              footer = dic['footer']
              formatted+=f"\t|\n\t| {footer['text']}\n"
            except:
              pass
            formatted+="\t\ ---------------------"
          else:
            formatted = message.content
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
    await interaction.response.send_message("Starting to purge all faction information... This will...\n- Delete all faction information in the database\n- Remove everyone's coleader & leader roles\n- Reset everyone's nickname that had a role\n- Create a paste link which consists of each ticket that is open & archived & sends it here\n- Deletes all ticket channels\n- Reset the faction list", ephemeral=True)
    # Remove everyone's roles & reset nicknames
    leader_role = discord.utils.get(interaction.guild.roles, name= "Faction Leader")
    coleader_role = discord.utils.get(interaction.guild.roles, name= "Faction Coleader")
    for member in leader_role.members:
      await member.remove_roles(leader_role)
      await member.edit(nick=member.name)
    for member in coleader_role.members:
      await member.remove_roles(coleader_role)
      await member.edit(nick=member.name)
    # Remove all factions from the database
    await execute(f"DELETE FROM leader_factions")  
    # Create a paste link with each ticket's (open & archived) information in it
    content = ""
    for name in ["Faction Tickets", "Faction Tickets #2", "Archived Channels"]:
      category = discord.utils.get(interaction.guild.categories, name=name)
      for channel in category.channels:
        faction_info = await self.get_faction_info(channel.name.split('-')[0])
        if faction_info=="Fail":
          faction_info={"faction_name": "N/A", "coleader_id_1": "", "coleader_id_2": "", "leader_id": ""}
        try:
          leader_name = discord.utils.get(interaction.guild.members, id=int(faction_info['leader_id'])).name
        except:
          leader_name = "N/A"
        try:
          coleader_1_name = discord.utils.get(interaction.guild.members, id=int(faction_info['coleader_id_1'])).name
        except:
          coleader_1_name = "N/A"
        try:
          coleader_2_name = discord.utils.get(interaction.guild.members, id=int(faction_info['coleader_id_2'])).name
        except:
          coleader_2_name = "N/A"
        string = f"----------------------------------------------------------\nFaction Name: {faction_info['faction_name']}\nLeader: {leader_name} ({faction_info['leader_id']})\nColeader #1: {coleader_1_name} ({faction_info['coleader_id_1']})\nColeader #2: {coleader_2_name} ({faction_info['coleader_id_2']})\n----------------------------------------------------------\n"
        string += f"Messages Below\n{await self.get_all_messages(interaction, channel)}\n----------------------------------------------------------\nThreads Below\n"
        for thread in channel.threads:
          string+= f"{await self.get_all_messages(interaction, thread)}\n \n"
        content+=string+"\n \n \n"
        string+= "----------------------------------------------------------"
        await channel.delete(reason="via /purge")
    content = content.encode("utf-8")
    key = json.loads(requests.post('https://paste.md-5.net/documents', data=content).content)['key']
    link = f"https://paste.md-5.net/{key}"
    await interaction.guild.get_channel(941766120082395158).send(content = f"Purge completed by `@{interaction.user}` {link}")  
    # Reset the faction list
    channel = discord.utils.get(interaction.guild.channels, name="faction-list")
    async for message in channel.history(limit=1, oldest_first=True):
      embed = discord.Embed(title=f"Factions in Season 3 (0)", description=f"```None```", color=discord.Color.red())
      logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await message.edit(embed=embed)
    
  @purge.error
  async def purge_error(self, interaction: discord.Interaction, error):
    await interaction.response.send_message(content=error, ephemeral=True)

async def setup(client:commands.Bot) -> None:
  await client.add_cog(purge(client))