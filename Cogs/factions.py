from discord.ext import commands
from discord import ui
import discord
from core.database import execute
from core.loggers import log_tasks
from utils.embeds import get_embed_logo_url

def is_staff(interaction):
  names_of_roles = ["Staff Team", "Admin", "Strike Team", "*", "Management", "Developer", "Owner"]
  for role_name in names_of_roles:
    role = discord.utils.get(interaction.guild.roles, name=role_name)
    if role in interaction.user.roles:
      return True
  return False

def is_staff_m(message):
  names_of_roles = ["Staff Team", "Admin", "Strike Team", "*", "Management", "Developer", "Owner"]
  for role_name in names_of_roles:
    role = discord.utils.get(message.guild.roles, name=role_name)
    if role in message.author.roles:
      return True
  return False

def is_admin(ctx):
    names_of_roles = ["Owner", "Management", "Developer", "*", "Admin"]
    for role_name in names_of_roles:
      role = discord.utils.get(ctx.guild.roles, name=role_name)
      if role in ctx.author.roles:
        return True
    return False

class factions(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
  
  async def remove_from_ticket(self, guild: discord.Guild, user_id: str, channel: discord.TextChannel):
    try:
      user = discord.utils.get(guild.members, id=int(user_id))
      perms = channel.overwrites_for(user)
      perms.view_channel = False
      await channel.set_permissions(user, overwrite=perms)
    except:
      pass   
  
  @commands.Cog.listener()
  async def on_member_remove(self, member: discord.Member):
    rows = await execute(f"SELECT * FROM `leader_factions` WHERE `leader_id` = '{member.id}'")
    if rows:
      channel = discord.utils.get(member.guild.channels, id=int(rows[0]['channel_id']))
      if rows[0]['leader_id']==member.id:
        category = discord.utils.get(member.guild.categories, name= "Archived Channels")
        await channel.edit(category=category)
        embed = discord.Embed(title="Leader left!", description=f"Uh oh! The leader, `{member.name}` has left the discord, so all faction members have been removed from this ticket, and the channel has been archived.", color= discord.Color.red())
        logo_url = get_embed_logo_url("Assets/Logo.png")
        embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
        await channel.send(embed=embed)
        await self.remove_from_ticket(member.guild, member.id, channel)
        return
    rows = await execute(f"SELECT * FROM `leader_factions` WHERE `coleader_id_1` = '{member.id}'")
    if rows:
      embed = discord.Embed(title="Coleader left!", description=f"Uh oh! The coleader, `{member.name}` has left the discord, and is no longer in this channel anymore.", color= discord.Color.red())
      logo_url = get_embed_logo_url("Assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await channel.send(embed=embed, file=discord.File("Assets/Logo.png"))
      await self.remove_from_ticket(member.guild, rows[0]['coleader_id_1'], channel)
      return
    rows = await execute(f"SELECT * FROM `leader_factions` WHERE `coleader_id_2` = '{member.id}'")
    if rows:
        embed = discord.Embed(title="Coleader left!", description=f"Uh oh! The coleader, `{member.name}` has left the discord, and is no longer in this channel anymore.", color= discord.Color.red())
        logo_url = get_embed_logo_url("Assets/Logo.png")
        embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
        await channel.send(embed=embed)
        await self.remove_from_ticket(member.guild, rows[0]['coleader_id_2'], channel)
        return
    
  @commands.command()
  async def sendrolerequest(self, ctx):
    if is_admin(ctx):
      await ctx.message.delete()
      embed = discord.Embed(title="Role Request", description="Click the button below to request roles! It is important to enter the information requested precisely as this system is automated. Please only request roles for `YOUR` faction with the correct role that you have in that faction.\n \nEach faction can only have:```- 1 Leader\n- 2 Coleaders```Please make a support ticket if you have any questions or run into any issues.", color=discord.Color.red())
      logo_url = get_embed_logo_url("Assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await ctx.send(embed=embed, view=RoleButtons(), file=discord.File("Assets/Logo.png"))
  
class RoleButtons(discord.ui.View):
    def __init__(self)-> None:
      super().__init__(timeout=None)
      
    @discord.ui.button(label = "Request Roles", emoji = "📝", style = discord.ButtonStyle.red, custom_id = "3")
    async def request(self, interaction: discord.Interaction, Button: discord.ui.Button):
      leader_role = discord.utils.get(interaction.guild.roles, name="Faction Leader")
      coleader_role = discord.utils.get(interaction.guild.roles, name="Faction Coleader")
      if leader_role in interaction.user.roles or coleader_role in interaction.user.roles:
        confirm = removeRoles()
        confirm.old_interaction = interaction
        await interaction.response.send_message(content="Failed! You already have a role! Would you like to remove your role?", ephemeral=True, view=confirm)
      else:
        await interaction.response.send_modal(RoleRequest())
  
class empty(discord.ui.View):
  def __init__(self) -> None:
    super().__init__(timeout=None)

class removeRoles(discord.ui.View):
  def __init__(self) -> None:
    super().__init__(timeout= None)
  
  async def log(self, interaction: discord.Interaction, IGN: str, faction: str, role: str, action: str, channel: discord.TextChannel):
    logs = discord.utils.get(interaction.guild.channels, name="𝖫𝗈𝗀𝗌")
    embed = discord.Embed(title=f"Roles {action}", description=f"`User` {interaction.user} ({interaction.user.id})\n`IGN` {IGN}\n`Faction` {faction}\n`Role` {role}\n`Channel` {channel.mention}\n`Invoked` Role Request", color=discord.Color.red())
    embed.set_footer(text="Minecadia Leader Bot", icon_url = "Assets/Logo.png")
    await logs.send(embed=embed)
  
  async def remove_from_ticket(self, interaction: discord.Interaction, user_id: str, channel: discord.TextChannel):
    user = discord.utils.get(interaction.guild.members, id=int(user_id))
    perms = channel.overwrites_for(user)
    perms.view_channel = False
    await channel.set_permissions(user, overwrite=perms)
  
  async def update_faction_list(self, interaction):
    rows = await execute("SELECT faction_name FROM leader_factions")
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
      embed.set_footer(text="Minecadia Leader Bot", icon_url = "Assets/Logo.png")
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
      rows = await execute(f"SELECT * FROM leader_factions WHERE coleader_id_1= '{interaction.user.id}'")
      if not rows:
        rows = await execute(f"SELECT * FROM leader_factions WHERE coleader_id_2= '{interaction.user.id}'")
    elif leader_role in interaction.user.roles:
      rows = await execute(f"SELECT * FROM leader_factions WHERE leader_id= '{interaction.user.id}'")
    channel = discord.utils.get(interaction.guild.channels, id=int(rows[0]['channel_id']))
    the_faction = rows[0]['faction_name']
    
    # logging
    await self.log(interaction, the_ign, the_faction, the_role, "Removed", channel)
    
    # Removing the coleader from the ticket if coleader
    if coleader_role in interaction.user.roles:
      embed = discord.Embed(title="Coleader left!", description=f"Uh oh! The coleader, `{interaction.user.name}` has requested for their roles to be removed, and is no longer in this channel anymore.", color=discord.Color.red())
      logo_url = get_embed_logo_url("Assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await channel.send(embed=embed, file=discord.File("Assets/Logo.png"))
      await self.remove_from_ticket(interaction, interaction.user.id, channel)
      await self.old_interaction.edit_original_response(content= "Success! Your `Faction Coleader` role has been removed! Your access to view your faction's ticket has also been removed.", view=empty())
      await interaction.response.defer()
    
    # Removing all from the ticket and archiving channel if leader
    elif leader_role in interaction.user.roles:
      category = discord.utils.get(interaction.guild.categories, name= "Archived Channels")
      await channel.edit(category=category)
      embed = discord.Embed(title="Leader left!", description=f"Uh oh! The leader, `{interaction.user.name}` has requested for their roles to be removed, so all faction members have been removed from this ticket, and the channel has been archived.", color= discord.Color.red())
      logo_url = get_embed_logo_url("Assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await channel.send(embed=embed, file=discord.File("Assets/Logo.png"))
      if rows[0]['coleader_id_1']:
        await self.remove_from_ticket(interaction, rows[0]['coleader_id_1'], channel)
      if rows[0]['coleader_id_2']:
        await self.remove_from_ticket(interaction, rows[0]['coleader_id_2'], channel)
      await self.remove_from_ticket(interaction, rows[0]['leader_id'], channel)
      await self.old_interaction.edit_original_response(content= "Success! Your `Faction Leader` role has been removed! Since you were the leader of the faction, the ticket channel has been archived and hidden from you and your coleaders.", view=empty())
      await execute(f"DELETE FROM leader_factions WHERE channel_id='{str(channel.id)}'")
      await interaction.response.defer()
      await self.update_faction_list(interaction)
    await interaction.user.remove_roles(the_role)
    
  @discord.ui.button(emoji= "👎", style= discord.ButtonStyle.red, custom_id= "5")
  async def confirmNo(self, interaction: discord.Interaction, Button: discord.ui.Button):
    await self.old_interaction.edit_original_response(content= "Success! Your role has been kept!", view=empty())
    await interaction.response.defer()

class AcceptColeader(discord.ui.View):
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
    rows = await execute(f"SELECT * FROM leader_factions WHERE faction_name= '{faction}'")
    channel = discord.utils.get(interaction.guild.channels, id=int(rows[0]['channel_id']))
    if rows[0]['coleader_id_1']:
      await execute(f"UPDATE leader_factions SET coleader_id_2 = '{self.user}' WHERE faction_name= '{faction}'")
    else:
      await execute(f"UPDATE leader_factions SET coleader_id_1 = '{self.user}' WHERE faction_name= '{faction}'")
    
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
    logo_url = get_embed_logo_url("Assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await interaction.channel.send(embed=embed, file=discord.File("Assets/Logo.png"))
    
    # Sending their acceptance message
    embed = discord.Embed(title="You have been accepted!", color= discord.Color.red(), description= f"Congratulations! You have been accepted as a coleader to the faction `{self.faction}`! Your faction's ticket can be found here-{interaction.channel.mention} - or at the bottom of the `Minecadia Leader` discord.")
    logo_url = get_embed_logo_url("Assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    try:
      await self.user.send(embed=embed) # I dont think this works
    except:
      pass
    # Logs
    logs = discord.utils.get(interaction.guild.channels, name="𝖫𝗈𝗀𝗌")
    embed = discord.Embed(title=f"Accepted Coleader", description=f"`Faction` {faction}\n`Coleader` {coleader.mention} ({coleader.id})", color=discord.Color.red())
    logo_url = get_embed_logo_url("Assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await logs.send(embed=embed, file=discord.File("Assets/Logo.png"))
    
  @discord.ui.button(label="Deny!", style= discord.ButtonStyle.red, custom_id= "pizza2")
  async def denyColeader(self, interaction: discord.Interaction, Button: discord.ui.Button):
    await interaction.response.send_message(f"`{interaction.user}` has denied `{self.user}` from being a coleader!")
    await interaction.message.delete()
    embed = discord.Embed(title="You have been denied!", color= discord.Color.red(), description= f"Sorry, but you have been denied access as a coleader to the faction `{self.faction}`!")
    logo_url = get_embed_logo_url("Assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    try:
      channel = await self.user.create_dm() # I dont think this works
      await channel.send(embed=embed)
    except:
      pass

class RoleRequest(ui.Modal):
  def __init__(self) -> None:
    super().__init__(title="Role Request", timeout=None, custom_id="100")
    self.add_item(ui.TextInput(label="What is your IGN", style=discord.TextStyle.short, placeholder="MeeZoid..."))
    self.add_item(ui.TextInput(label="What is the name of your faction?", style=discord.TextStyle.short, placeholder="My faction name..."))
    self.add_item(ui.TextInput(label="Which role? (Leader or Coleader)", style=discord.TextStyle.short, placeholder="Leader...", min_length=6, max_length=8))
  
  async def update_faction_list(self, interaction):
    rows = await execute("SELECT faction_name FROM leader_factions")
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
      logo_url = get_embed_logo_url("Assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await message.edit(embed=embed)

  async def failed(self, interaction: discord.Interaction, IGN: str, faction: str, role: str, error: str):
    logs = discord.utils.get(interaction.guild.channels, name="𝖫𝗈𝗀𝗌")
    embed = discord.Embed(title="Failed to Give Roles", description=f"`User` {interaction.user} ({interaction.user.id})\n`IGN` {IGN}\n`Faction` {faction}\n`Role` {role}\n`Error` {error}\n`Invoked` Role Request", color=discord.Color.red())
    logo_url = get_embed_logo_url("Assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await logs.send(embed=embed, file=discord.File("Assets/Logo.png"))

  async def log(self, interaction: discord.Interaction, IGN: str, faction: str, role: str, action: str, channel: discord.TextChannel):
    logs = discord.utils.get(interaction.guild.channels, name="𝖫𝗈𝗀𝗌")
    embed = discord.Embed(title=f"Roles {action}", description=f"`User` {interaction.user} ({interaction.user.id})\n`IGN` {IGN}\n`Faction` {faction}\n`Role` {role}\n`Channel` {channel.mention}\n`Invoked` Role Request", color=discord.Color.red())
    logo_url = get_embed_logo_url("Assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await logs.send(embed=embed, file=discord.File("Assets/Logo.png"))

  async def request_coleader(self, interaction: discord.Interaction, faction: str, IGN: str):
    # Request for the Coleader to join.
    embed = discord.Embed(title="Coleader request!", description=f"The coleader, `{interaction.user}` has requested to join this faction as a coleader! Anyone in this ticket may accept or deny him. Press one of the buttons below to accept/deny him!", color=discord.Color.red())
    logo_url = get_embed_logo_url("Assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    accept_view = AcceptColeader(interaction.user.id, faction)
    rows = await execute(f"SELECT * FROM leader_factions WHERE faction_name= '{faction}'")
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
    logo_url = get_embed_logo_url("Assets/Logo.png")
    embed2.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
    await channel.send(embeds = [embed1, embed2], file=discord.File("Assets/Logo.png"))
    
    # Adding information to database
    await execute(f"INSERT INTO leader_factions (faction_name, leader_id, coleader_id_1, coleader_id_2, channel_id) VALUES ('{faction}', '{interaction.user.id}', '', '', '{channel.id}')")
    await self.update_faction_list(interaction)
    
    return channel
  
  async def faction_exists(self, faction: str):
    rows = await execute(f"SELECT * FROM leader_factions WHERE faction_name = '{faction}'")
    if len(rows)==0:
      return False
    return True
  
  async def two_coleaders(self, faction: str):
    if await self.faction_exists(faction):
      rows = await execute(f"SELECT * FROM leader_factions WHERE faction_name = '{faction}'")
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
      
      
async def setup(client:commands.Bot) -> None:
  await client.add_cog(factions(client))