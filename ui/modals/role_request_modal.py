import discord
from discord import ui

from core.loggers import log_tasks
from repositories.faction_repository import FactionRepository
from ui.views.accept_coleader_view import AcceptColeaderView
from services.faction_service import FactionService

_faction_repo = FactionRepository()
_faction_svc = FactionService(_faction_repo)

async def _execute(query):
    return await _faction_repo.execute(query)

class RoleRequestModal(ui.Modal):
  def __init__(self) -> None:
    super().__init__(title="Role Request", timeout=None, custom_id="100")
    self.add_item(ui.TextInput(label="What is your IGN", style=discord.TextStyle.short, placeholder="MeeZoid..."))
    self.add_item(ui.TextInput(label="What is the name of your faction?", style=discord.TextStyle.short, placeholder="My faction name..."))
    self.add_item(ui.TextInput(label="Which role? (Leader or Coleader)", style=discord.TextStyle.short, placeholder="Leader...", min_length=6, max_length=8))
  
  async def update_faction_list(self, interaction):
    rows = await _execute("SELECT faction_name FROM leader_factions")
    channel = discord.utils.get(interaction.guild.channels, name="𝖥𝖺𝖼𝗍𝗂𝗈𝗇-𝖫𝗂𝗌𝗍")
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
      logo_url = interaction.client.app.embeds.get_logo_url("assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await message.edit(embed=embed)

  async def failed(self, interaction: discord.Interaction, IGN: str, faction: str, role: str, error: str):
    logs = discord.utils.get(interaction.guild.channels, name="𝖫𝗈𝗀𝗌")
    embed = discord.Embed(title="Failed to Give Roles", description=f"`User` {interaction.user} ({interaction.user.id})\n`IGN` {IGN}\n`Faction` {faction}\n`Role` {role}\n`Error` {error}\n`Invoked` Role Request", color=discord.Color.red())
    logo_url = interaction.client.app.embeds.get_logo_url("assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await logs.send(embed=embed, file=discord.File("assets/Logo.png"))

  async def log(self, interaction: discord.Interaction, IGN: str, faction: str, role: str, action: str, channel: discord.TextChannel):
    logs = discord.utils.get(interaction.guild.channels, name="𝖫𝗈𝗀𝗌")
    embed = discord.Embed(title=f"Roles {action}", description=f"`User` {interaction.user} ({interaction.user.id})\n`IGN` {IGN}\n`Faction` {faction}\n`Role` {role}\n`Channel` {channel.mention}\n`Invoked` Role Request", color=discord.Color.red())
    logo_url = interaction.client.app.embeds.get_logo_url("assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await logs.send(embed=embed, file=discord.File("assets/Logo.png"))

  async def request_coleader(self, interaction: discord.Interaction, faction: str, IGN: str):
    # Request for the Coleader to join.
    embed = discord.Embed(title="Coleader request!", description=f"The coleader, `{interaction.user}` has requested to join this faction as a coleader! Anyone in this ticket may accept or deny him. Press one of the buttons below to accept/deny him!", color=discord.Color.red())
    logo_url = interaction.client.app.embeds.get_logo_url("assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    accept_view = AcceptColeaderView(interaction.user.id, faction)
    rows = await _execute(f"SELECT * FROM leader_factions WHERE faction_name= '{faction}'")
    channel = discord.utils.get(interaction.guild.channels, id=int(rows[0]['channel_id']))
    await channel.send(embed=embed, view=accept_view)
    
  async def create_faction(self, interaction: discord.Interaction, faction: str, IGN: str):
    # Making the ticket
    strike_team = discord.utils.get(interaction.guild.roles, name="Strike Team")
    admin = discord.utils.get(interaction.guild.roles, name="Admin")
    overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                  interaction.user: discord.PermissionOverwrite(view_channel = True, send_messages = True),
                  admin: discord.PermissionOverwrite(view_channel = True, send_messages = True),
                  strike_team: discord.PermissionOverwrite(view_channel = True, send_messages = True)}
    category = discord.utils.get(interaction.guild.categories, name="Faction Tickets")
    if len(category.channels) == 50:
      category = discord.utils.get(interaction.guild.categories, id=1196515275764408372)
    channel = await interaction.guild.create_text_channel(name=f"{faction}-ticket", category=category, overwrites=overwrites)
    embed1 = discord.Embed(title=f"{faction}'s Faction Ticket", description="Welcome to your faction ticket. This is where you will manage all support relating to your faction specifically. If you would like to make a request, run the command `/request (option)` which will open a thread where you can speak directly to a staff member to help you out. If you have any questions about how this process works, ask a staff member!", color=discord.Color.red())
    embed1.set_thumbnail(url="attachment://Logo.png")
    embed2 = discord.Embed(title = "Faction Admin List", description = "Your admin list is a list of players who can recieve 3 star from a staff member at any time where the current 3 star is not available. Predefining this list saves some time in the future. Run `/admin-list` to edit your faction's admin list!", color = discord.Color.red())
    embed2.add_field(name = "Admin List", value = f"```#1 - None```")
    logo_url = interaction.client.app.embeds.get_logo_url("assets/Logo.png")
    embed2.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await channel.send(embeds = [embed1, embed2], file=discord.File("assets/Logo.png"))
    
    # Adding information to database
    await _execute(f"INSERT INTO leader_factions (faction_name, leader_id, coleader_id_1, coleader_id_2, channel_id) VALUES ('{faction}', '{interaction.user.id}', '', '', '{channel.id}')")
    await self.update_faction_list(interaction)
    
    return channel
  
  async def faction_exists(self, faction: str):
    rows = await _execute(f"SELECT * FROM leader_factions WHERE faction_name = '{faction}'")
    if len(rows)==0:
      return False
    return True
  
  async def two_coleaders(self, faction: str):
    if await self.faction_exists(faction):
      rows = await _execute(f"SELECT * FROM leader_factions WHERE faction_name = '{faction}'")
      return (rows[0]['coleader_id_1'] and rows[0]['coleader_id_2'])

  async def checks(self, interaction: discord.Interaction, faction: str, IGN: str, role: str):
    if role.lower() != "leader" and role.lower() != "coleader":
      await interaction.response.send_message(content="Failed! Enter `Coleader or `Leader` into the `Role` field.", ephemeral=True) 
      await self.failed(interaction, IGN, faction, role, f"The user did not enter `Leader` or `Coleader`.")
    
    elif not await self.faction_exists(faction) and role.lower()=="coleader":
        await interaction.response.send_message(content="Failed! There's no faction registered by this name yet. Please get your faction leader to register your faction first.", ephemeral=True)
        await self.failed(interaction, IGN, faction, role, "The user is trying to be the coleader of a faction that doesn't exist.")
    
    elif await self.two_coleaders(faction) and role.lower()=="coleader":
      await interaction.response.send_message(content="Failed! There's already two coleaders registed for this faction.", ephemeral=True)
      await self.failed(interaction, IGN, faction, role, "The user is trying to be the third coleader in this faction.")
    
    elif await self.faction_exists(faction) and role.lower()=="leader":
      await interaction.response.send_message(content="Failed! There's already a faction registered under this name.", ephemeral=True)
      return await self.failed(interaction, IGN, faction, role, "The user is trying to be the leader of a faction that already exists.")
    
    else:
      return True
    return False
  
  async def on_submit(self, interaction: discord.Interaction):
    if await self.checks(interaction, self.children[1].value, self.children[0].value, self.children[2].value):
      leader_role = discord.utils.get(interaction.guild.roles, name="Faction Leader")
      coleader_role = discord.utils.get(interaction.guild.roles, name="Faction Coleader")
      the_role = leader_role if self.children[2].value.lower()=="leader" else coleader_role

      if the_role==leader_role:
        channel = await self.create_faction(interaction, self.children[1].value, self.children[0].value)
        await interaction.response.send_message(content=f"Successfully given roles!\n**IGN**: {self.children[0].value}\n**Faction**: {self.children[1].value.capitalize()}\n**Role**: {self.children[2].value}\nYour faction's channel can be found here {channel.mention}", ephemeral=True)
        await self.log(interaction, self.children[0].value, self.children[1].value, self.children[2].value, "Given", channel)
        try:
          new_tag = f"[{self.children[1].value.capitalize()}] {self.children[0].value}"
          await interaction.user.edit(nick=new_tag[:32])
          await interaction.user.add_roles(the_role)
        except Exception as e:
          log_tasks.error(f"Failed to update member nick/roles: {e}")

      elif the_role==coleader_role:
        channel = await self.request_coleader(interaction, self.children[1].value, self.children[0].value)
        await interaction.response.send_message(content=f"Successfully requested your coleader role!\nPlease ask a user inside of the `{self.children[1]}` ticket to accept/deny your request. You will be notified through DMs of your acceptance, so please have them enabled!", ephemeral=True)