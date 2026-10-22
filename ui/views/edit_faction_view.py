import discord

from core.database import DatabasePool
from core.loggers import log_tasks
from repositories.faction_repository import FactionRepository
from services.faction_service import FactionService

_repo = FactionRepository()
_faction_svc = FactionService(_repo)

async def execute(query):
    return await DatabasePool.get().execute(query)

class _FactionTextModal(discord.ui.Modal):
    def __init__(self, title: str, label: str, callback, view, *, max_length: int = 100):
      super().__init__(title=title)
      self.callback = callback
      self.view = view
      self.value = discord.ui.TextInput(label=label, max_length=max_length)
      self.add_item(self.value)

    async def on_submit(self, interaction: discord.Interaction):
      await interaction.response.defer()
      await self.callback(interaction, str(self.value))
      await self.view.update_message(interaction)

class EditFactionView(discord.ui.View):
    def __init__(self, client) -> None:
      self.client = client
      super().__init__(timeout=None)
    faction_name:str
    
    async def get_faction_info(self):
      rows = await execute(f"SELECT * FROM leader_factions WHERE faction_name = '{self.faction_name}'")
      if rows:
        return rows[0]
      else:
        return "Fail"
    
    async def send(self, interaction: discord.Interaction):
        await self.update_message(self.data[:self.sep], interaction)

    async def create_embed(self, interaction: discord.Interaction):
        faction_info = await self.get_faction_info()
        if faction_info=="Fail":
          await interaction.edit_original_response(content="Failed! This faction does not exist!")
          return "Fail"
        try:  
          self.leader = faction_info['leader_id']
          self.coleader_1 = faction_info['coleader_id_1']
          self.coleader_2 = faction_info['coleader_id_2']
          self.channel = faction_info['channel_id']
        except Exception:
          pass
        embed = discord.Embed(title=f"Minecadia Leader Faction Editor", description=f"Here's the information on `{self.faction_name}` ...", color=discord.Color.red())
        logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
        embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
        try:
          leader_mention = await interaction.guild.fetch_member(int(faction_info['leader_id'])).mention
        except Exception:
          leader_mention = "N/A"
        try:
          coleader_1_mention =await interaction.guild.fetch_member(int(faction_info['coleader_id_1'])).mention
        except Exception:
          coleader_1_mention = "N/A"
        try:
          coleader_2_mention = await interaction.guild.fetch_member(int(faction_info['coleader_id_2'])).mention
        except Exception:
          coleader_2_mention = "N/A"
        try:
          channel_mention = discord.utils.get(interaction.guild.channels, id=int(faction_info['channel_id'])).mention
        except Exception:
          channel_mention = "N/A"
        embed.add_field(name="Leader", value=f"{leader_mention} ({faction_info['leader_id']})")
        embed.add_field(name="Coleader #1", value=f"{coleader_1_mention} ({faction_info['coleader_id_1']})")
        embed.add_field(name="Coleader #2", value=f"{coleader_2_mention} ({faction_info['coleader_id_2']})")
        embed.add_field(name="Channel", value=f"{channel_mention} ({faction_info['channel_id']})")
        embed.set_thumbnail(url="attachment://Logo.png")
        desc = f"Here's the information on `{self.faction_name}` ..."
        return embed
    
    def update_buttons(self):
        if self.coleader_1:
          if self.coleader_2:
            self.remove_coleader.disabled=False
            self.add_coleader.disabled=True
          else:
            self.add_coleader.disabled=False
            self.remove_coleader.disabled=False
        else:
          if self.coleader_2:
            self.add_coleader.disabled=False
            self.remove_coleader.disabled=False
          else:
            self.add_coleader.disabled=False
            self.remove_coleader.disabled=True
        if self.faction_name:
          self.change_name.disabled=False
          self.swap_leader.disabled=False
          self.archive_faction.disabled=False
    
    async def update_message(self, interaction: discord.Interaction):
      embed = await self.create_embed(interaction)
      if embed=="Fail":
        return
      else:
        self.update_buttons()
        if interaction.message is not None:
          await interaction.message.edit(content="", embed=embed, view=self)
        else:
          await interaction.edit_original_response(content="", embed=embed, view=self)
    
    @discord.ui.button(label="Click here to change the faction!",style=discord.ButtonStyle.grey, row=0, disabled=False, custom_id="change_faction")
    async def change_faction(self, interaction:discord.Interaction, button: discord.ui.Button):
        async def submit(modal_interaction, value):
          self.faction_name = value
        await interaction.response.send_modal(_FactionTextModal("Select faction", "Faction name", submit, self, max_length=100))
    
    @discord.ui.button(label="Swap Leader",style=discord.ButtonStyle.red, row=1, disabled=True, custom_id="swap_leader")
    async def swap_leader(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(_FactionTextModal("Swap leader", "Mention the new leader", self.f_swap_leader, self))
    
    @discord.ui.button(label="Change Name",style=discord.ButtonStyle.red, row=1, disabled=True, custom_id="change_name")
    async def change_name(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(_FactionTextModal("Change faction name", "New faction name", self.f_change_name, self, max_length=10))
        
    @discord.ui.button(label="Add Coleader",style=discord.ButtonStyle.red, row=2, disabled=True, custom_id="add_coleader")
    async def add_coleader(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(_FactionTextModal("Add coleader", "Mention the coleader", self.f_add_coleader, self))

    @discord.ui.button(label="Remove Coleader",style=discord.ButtonStyle.red, row=2, disabled=True, custom_id="remove_coleader")
    async def remove_coleader(self, interaction:discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(_FactionTextModal("Remove coleader", "Mention the coleader", self.f_remove_coleader, self))
    
    @discord.ui.button(label="Archive & remove this faction", style=discord.ButtonStyle.red, row=3, disabled=True, custom_id="archieve_faction")
    async def archive_faction(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.send_message("Successfully archived this channel!", ephemeral=True)
      await self.f_archive_faction(interaction)
      embed = discord.Embed(title="Minecadia Leader Faction Editor", description=f"Here's the information on `Awaiting Faction` ...", color=discord.Color.red())
      logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      embed.add_field(name="Leader", value="...")
      embed.add_field(name="Coleader #1", value="...")
      embed.add_field(name="Coleader #2", value="...")
      embed.add_field(name="Channel", value="...")
      embed.set_thumbnail(url="attachment://Logo.png")
      await interaction.edit_original_response(content="", embed=embed, view=self)
    
    async def f_archive_faction(self, interaction: discord.Interaction):
      faction_info= await self.get_faction_info()
      await execute(f"DELETE FROM leader_factions WHERE faction_name = '{self.faction_name}'")
      channel = discord.utils.get(interaction.guild.channels, id=int(self.channel))
      category = discord.utils.get(interaction.guild.categories, name= "Archived Channels")
      await channel.edit(category=category)
      embed = discord.Embed(title="Faction archived!", color=discord.Color.red(), description=f"The faction `{self.faction_name}` has been archived by a staff member. All faction member's access to view this channel has been denied.")
      logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await channel.send(embed=embed, file=discord.File("assets/Logo.png"))
      for index, val in enumerate([self.leader, self.coleader_1, self.coleader_2]):
        member = await interaction.guild.fetch_member(int(val))
        if index!=0:
          role = discord.utils.get(interaction.guild.roles, name="Faction Coleader")
        else:
          role = discord.utils.get(interaction.guild.roles, name="Faction Leader")
        await self.edit_ticket_perms(interaction, member.id, channel, False)
        await member.remove_roles(role)
        await member.edit(nick=member.name)
      await self.update_faction_list(interaction)
      
    async def edit_database(self, column:str, value:str):
      await execute(f"UPDATE leader_factions SET `{column}` = '{value}' WHERE `faction_name`= '{self.faction_name}'")
    
    async def f_swap_leader(self, interaction: discord.Interaction, value: str):
      channel = discord.utils.get(interaction.guild.channels, id=int(self.channel))
      current_leader = await interaction.guild.fetch_member(int(self.leader))
      try:
        the_id = value.split("<@")[1].split(">")[0]
      except Exception:
        return await interaction.followup.send("Failed! Please make sure you mention a user.", ephemeral=True)
      await self.edit_database('leader_id', the_id)
      await self.edit_ticket_perms(interaction, current_leader.id, channel, False)
      leader = await interaction.guild.fetch_member(int(the_id))
      await self.edit_ticket_perms(interaction, the_id, channel, True)
      embed = discord.Embed(title="Leader swapped!", description=f"The old leader, `{current_leader}` has been swapped in for the new leader, `{leader}` by a staff member. Welcome them to the ticket!", color= discord.Color.red())
      logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await channel.send(embed=embed, file=discord.File("assets/Logo.png"))
      await self.log(interaction, "Leader Swapped", f"`Faction` {self.faction_name}\n`Channel` {channel.mention}\n`Before` {current_leader.mention} ({current_leader.id})\n`After` {leader.mention} ({leader.id})")  
      leader_role = discord.utils.get(interaction.guild.roles, name= "Faction Leader")
      await current_leader.edit(nick=current_leader.name)
      await current_leader.remove_roles(leader_role)
      await leader.edit(nick=f"[{self.faction_name}] {leader.name}")
      await leader.add_roles(leader_role)
    
    async def f_change_name(self, interaction: discord.Interaction, value: str):
      channel = discord.utils.get(interaction.guild.channels, id=int(self.channel))
      if len(value)>10:
        return await interaction.followup.send("Failed! Please enter a faction name that is 10 or less characters.", ephemeral=True)
      await self.edit_database('faction_name', value)
      old_name = self.faction_name
      self.faction_name = value
      embed = discord.Embed(title="Faction name changed!", description=f"The name of this faction has been changed from `{old_name}` to `{self.faction_name}` by a staff member!", color=discord.Color.red())
      logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await channel.send(embed=embed, file=discord.File("assets/Logo.png"))
      leader = await interaction.guild.fetch_member(int(self.leader))
      await channel.edit(name=f"{self.faction_name}-ticket")
      await self.log(interaction, "Faction Name Changed", f"`Leader` {leader.mention} ({leader.id})\n`Channel` {channel.mention}\n`Before` {old_name}\n`After` {self.faction_name}")
      await self.update_faction_list(interaction)
      for val in [self.leader, self.coleader_1, self.coleader_2]:
        try:
          member = await interaction.guild.fetch_member(int(val))
          old_faction = member.nick.split("[")[1].split("]")[0]
          await member.edit(nick=member.nick.replace(old_faction, self.faction_name))
        except Exception as e:
          log_tasks.error(f"Failed to update faction nicknames: {e}")

    async def f_add_coleader(self, interaction: discord.Interaction, value: str):
      channel = discord.utils.get(interaction.guild.channels, id=int(self.channel))
      try:
        the_id = value.split("<@")[1].split(">")[0]
      except Exception:
        return await interaction.followup.send("Failed! Please make sure you mention a user.", ephemeral=True)
      rows = await execute(f"SELECT * FROM leader_factions WHERE `faction_name`= '{self.faction_name}'")
      if rows[0]['coleader_id_1']:
        await self.edit_database('coleader_id_2', the_id)
      else:
        await self.edit_database('coleader_id_1', the_id)
      coleader = await interaction.guild.fetch_member(int(the_id))
      embed = discord.Embed(title="Coleader joined!", description=f"The coleader, `{coleader}` has been added as a coleader for this faction by a staff member! Welcome him to the ticket!", color=discord.Color.red())
      logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await channel.send(embed=embed, file=discord.File("assets/Logo.png"))
      await self.edit_ticket_perms(interaction, the_id, channel, True)
      await self.log(interaction, "Coleader Added", f"`Faction` {self.faction_name}\n`Channel` {channel.mention}\n`Coleader` {coleader.mention} ({coleader.id})")
      coleader_role = discord.utils.get(interaction.guild.roles, name= "Faction Coleader")
      await coleader.edit(nick=f"[{self.faction_name}] {coleader.name}")
      await coleader.add_roles(coleader_role)
      
    async def f_remove_coleader(self, interaction: discord.Interaction, value: str):
      channel = discord.utils.get(interaction.guild.channels, id=int(self.channel))
      try:
        the_id = value.split("<@")[1].split(">")[0]
      except Exception:
        return await interaction.followup.send("Failed! Please make sure you mention a user.", ephemeral=True)
      rows = await execute(f"SELECT * FROM leader_factions WHERE `faction_name`= '{self.faction_name}'")
      if str(rows[0]['coleader_id_1'])==the_id:
        await self.edit_database('coleader_id_1', '')
      elif str(rows[0]['coleader_id_2'])==the_id:
        await self.edit_database('coleader_id_2', '')
      else:
        return await interaction.followup.send(f"Failed! `{value}` is not a coleader of the faction `{self.faction_name}`", ephemeral=True)
      coleader = await interaction.guild.fetch_member(int(the_id))
      embed = discord.Embed(title="Coleader removed!", description=f"Uh oh! The coleader, `{coleader}` has been removed from this faction by a staff member, and is no longer in this channel anymore.", color=discord.Color.red())
      logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await channel.send(embed=embed, file=discord.File("assets/Logo.png"))
      await self.edit_ticket_perms(interaction, the_id, channel, False)
      await self.log(interaction, "Coleader Removed", f"`Faction` {self.faction_name}\n`Channel` {channel.mention}\n`Coleader` {coleader.mention} ({coleader.id})")
      coleader_role = discord.utils.get(interaction.guild.roles, name= "Faction Coleader")
      await coleader.edit(nick=coleader.name)
      await coleader.remove_roles(coleader_role)
      
    async def edit_ticket_perms(self, interaction: discord.Interaction, user_id: str, channel: discord.TextChannel, action):
      try:
        user = await interaction.guild.fetch_member(int(user_id))
        perms = channel.overwrites_for(user)
        perms.view_channel = action
        perms.send_messages = action
        await channel.set_permissions(user, overwrite=perms)
      except Exception as e:
        log_tasks.error(f"Failed to edit ticket permissions: {e}")

    async def log(self, interaction: discord.Interaction, action:str, field:str):
      logs = discord.utils.get(interaction.guild.channels, name="𝖫𝗈𝗀𝗌")
      embed = discord.Embed(title=action, description=f"{field}\n`Invoked` Edit Command", color=discord.Color.red())
      logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
      embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
      await logs.send(embed=embed, file=discord.File("assets/Logo.png"))
    
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
        embed = discord.Embed(title=f"Factions List ({count})", description=f"```{string}```", color=discord.Color.red())
        logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
        embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
        await message.edit(embed=embed)
    