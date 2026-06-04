import discord
from discord import ui
import discord as discord_module

from repositories.faction_repository import FactionRepository
from services.faction_service import FactionService
from ui.views.empty_view import EmptyView
from utils.embeds import get_embed_logo_url

_faction_repo = FactionRepository()
_faction_svc = FactionService(_faction_repo)

async def _execute(query):
    return await _faction_repo.execute(query)

class RemoveRolesView(discord.ui.View):
  def __init__(self) -> None:
    super().__init__(timeout= None)
  
  async def log(self, interaction: discord.Interaction, IGN: str, faction: str, role: str, action: str, channel: discord.TextChannel):
    logs = discord.utils.get(interaction.guild.channels, name="𝖫𝗈𝗀𝗌")
    embed = discord.Embed(title=f"Roles {action}", description=f"`User` {interaction.user} ({interaction.user.id})\n`IGN` {IGN}\n`Faction` {faction}\n`Role` {role}\n`Channel` {channel.mention}\n`Invoked` Role Request", color=discord.Color.red())
    embed.set_footer(text="Minecadia Leader Bot", icon_url = "assets/Logo.png")
    await logs.send(embed=embed)
  
  async def remove_from_ticket(self, interaction: discord.Interaction, user_id: str, channel: discord.TextChannel):
    user = discord.utils.get(interaction.guild.members, id=int(user_id))
    perms = channel.overwrites_for(user)
    perms.view_channel = False
    await channel.set_permissions(user, overwrite=perms)
  
  async def update_faction_list(self, interaction):
    rows = await _execute("SELECT faction_name FROM leader_factions")
    channel = discord.utils.get(interaction.guild.channels, name="faction-list")
    if len(rows)!=0:
      faction_list = []
      for row in rows:
        faction_list.append(row['faction_name'])
      string = ", ".join(faction_list)
      count = len(rows)
    else:
      string = "None"
      count = 0
    async for message in channel.history(limit=1, oldest_first=True):
      embed = discord.Embed(title=f"Factions list ({count})", description=f"```{string}```", color=discord.Color.red())
      embed.set_footer(text="Minecadia Leader Bot", icon_url = "assets/Logo.png")
      await message.edit(embed=embed)
  
  @discord.ui.button(emoji= "👍", style= discord.ButtonStyle.red, custom_id= "4")
  async def confirmYes(self, interaction: discord.Interaction, Button: discord.ui.Button):
    # Removing roles & resetting nickname
    leader_role = discord.utils.get(interaction.guild.roles, name="Faction Leader")
    coleader_role = discord.utils.get(interaction.guild.roles, name="Faction Coleader")
    the_role = leader_role if leader_role in interaction.user.roles else coleader_role
    the_ign = interaction.user.display_name.split("] ")[1]
    await interaction.user.edit(nick=interaction.user.name)
    
    # Attempting to gather the channel id
    if coleader_role in interaction.user.roles:
      rows = await _execute(f"SELECT * FROM leader_factions WHERE coleader_id_1= '{interaction.user.id}'")
      if not rows:
        rows = await _execute(f"SELECT * FROM leader_factions WHERE coleader_id_2= '{interaction.user.id}'")
    elif leader_role in interaction.user.roles:
      rows = await _execute(f"SELECT * FROM leader_factions WHERE leader_id= '{interaction.user.id}'")
    channel = discord.utils.get(interaction.guild.channels, id=int(rows[0]['channel_id']))
    the_faction = rows[0]['faction_name']
    
    # logging
    await self.log(interaction, the_ign, the_faction, the_role, "Removed", channel)
    
    # Removing the coleader from the ticket if coleader
    if coleader_role in interaction.user.roles:
      embed = discord.Embed(title="Coleader left!", description=f"Uh oh! The coleader, `{interaction.user.name}` has requested for their roles to be removed, and is no longer in this channel anymore.", color=discord.Color.red())
      logo_url = get_embed_logo_url("assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await channel.send(embed=embed, file=discord.File("assets/Logo.png"))
      await self.remove_from_ticket(interaction, interaction.user.id, channel)
      await self.old_interaction.edit_original_response(content= "Success! Your `Faction Coleader` role has been removed! Your access to view your faction's ticket has also been removed.", view=EmptyView())
      await interaction.response.defer()
    
    # Removing all from the ticket and archiving channel if leader
    elif leader_role in interaction.user.roles:
      category = discord.utils.get(interaction.guild.categories, name= "Archived Channels")
      await channel.edit(category=category)
      embed = discord.Embed(title="Leader left!", description=f"Uh oh! The leader, `{interaction.user.name}` has requested for their roles to be removed, so all faction members have been removed from this ticket, and the channel has been archived.", color= discord.Color.red())
      logo_url = get_embed_logo_url("assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await channel.send(embed=embed, file=discord.File("assets/Logo.png"))
      if rows[0]['coleader_id_1']:
        await self.remove_from_ticket(interaction, rows[0]['coleader_id_1'], channel)
      if rows[0]['coleader_id_2']:
        await self.remove_from_ticket(interaction, rows[0]['coleader_id_2'], channel)
      await self.remove_from_ticket(interaction, rows[0]['leader_id'], channel)
      await self.old_interaction.edit_original_response(content= "Success! Your `Faction Leader` role has been removed! Since you were the leader of the faction, the ticket channel has been archived and hidden from you and your coleaders.", view=EmptyView())
      await _execute(f"DELETE FROM leader_factions WHERE channel_id='{str(channel.id)}'")
      await interaction.response.defer()
      await self.update_faction_list(interaction)
    await interaction.user.remove_roles(the_role)
    
  @discord.ui.button(emoji= "👎", style= discord.ButtonStyle.red, custom_id= "5")
  async def confirmNo(self, interaction: discord.Interaction, Button: discord.ui.Button):
    await self.old_interaction.edit_original_response(content= "Success! Your role has been kept!", view=EmptyView())
    await interaction.response.defer()
