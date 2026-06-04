import discord
from discord import ui
import discord as discord_module

from core.loggers import log_tasks
from repositories.faction_repository import FactionRepository
from services.faction_service import FactionService
from utils.embeds import get_embed_logo_url

_faction_repo = FactionRepository()
_faction_svc = FactionService(_faction_repo)

async def _execute(query):
    return await _faction_repo.execute(query)

class AcceptColeaderView(discord.ui.View):
  def __init__(self, user, faction) -> None:
        super().__init__(timeout=None) 
        self.user = user
        self.faction = faction
  
  @discord.ui.button(label="Accept!", style= discord.ButtonStyle.red, custom_id= "pizza")
  async def acceptColeader(self, interaction: discord.Interaction, Button: discord.ui.Button):
    coleader = discord.utils.get(interaction.guild.members, id=self.user)
    await interaction.response.send_message(f"`{interaction.user}` has accepted `{coleader}` to being a coleader!")
    await interaction.message.delete()
    faction = interaction.channel.name.split("-")[0]
    rows = await _execute(f"SELECT * FROM leader_factions WHERE faction_name= '{faction}'")
    channel = discord.utils.get(interaction.guild.channels, id=int(rows[0]['channel_id']))
    if rows[0]['coleader_id_1']:
      await _execute(f"UPDATE leader_factions SET coleader_id_2 = '{self.user}' WHERE faction_name= '{faction}'")
    else:
      await _execute(f"UPDATE leader_factions SET coleader_id_1 = '{self.user}' WHERE faction_name= '{faction}'")
    
    # Give coleader role & change nickname
    coleader_role = discord.utils.get(interaction.guild.roles, name="Faction Coleader")
    await coleader.add_roles(coleader_role)
    new_tag = f"[{faction.title()}] {coleader.name}"
    await coleader.edit(nick=new_tag[:32])
    
    # Adding the coleader to their faction's ticket
    perms = channel.overwrites_for(coleader)
    perms.view_channel = True
    await channel.set_permissions(coleader, overwrite=perms)
    embed = discord.Embed(title="Coleader joined!", description=f"The coleader, `{coleader}` has been accepted as a coleader for this faction! Welcome him to the ticket!", color=discord.Color.red())
    logo_url = get_embed_logo_url("assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await interaction.channel.send(embed=embed, file=discord.File("assets/Logo.png"))
    
    # Sending their acceptance message
    embed = discord.Embed(title="You have been accepted!", color= discord.Color.red(), description= f"Congratulations! You have been accepted as a coleader to the faction `{self.faction}`! Your faction's ticket can be found here-{interaction.channel.mention} - or at the bottom of the `Minecadia Leader` discord.")
    logo_url = get_embed_logo_url("assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    try:
      await self.user.send(embed=embed) # I dont think this works
    except:
      pass
    # Logs
    logs = discord.utils.get(interaction.guild.channels, name="𝖫𝗈𝗀𝗌")
    embed = discord.Embed(title=f"Accepted Coleader", description=f"`Faction` {faction}\n`Coleader` {coleader.mention} ({coleader.id})", color=discord.Color.red())
    logo_url = get_embed_logo_url("assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await logs.send(embed=embed, file=discord.File("assets/Logo.png"))
    
  @discord.ui.button(label="Deny!", style= discord.ButtonStyle.red, custom_id= "pizza2")
  async def denyColeader(self, interaction: discord.Interaction, Button: discord.ui.Button):
    await interaction.response.send_message(f"`{interaction.user}` has denied `{self.user}` from being a coleader!")
    await interaction.message.delete()
    embed = discord.Embed(title="You have been denied!", color= discord.Color.red(), description= f"Sorry, but you have been denied access as a coleader to the faction `{self.faction}`!")
    logo_url = get_embed_logo_url("assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    try:
      channel = await self.user.create_dm() # I dont think this works
      await channel.send(embed=embed)
    except:
      pass
