from discord.ext import commands, tasks
from discord import app_commands, ui
from datetime import date
from typing import Literal
import requests
import discord

class request(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
    self.url = "https://api.telegram.org/botREMOVED/sendMessage"

  @commands.Cog.listener()
  async def on_ready(self):
     self.send_mass_strike_reports.start()

  @tasks.loop(hours = 6)
  async def send_mass_strike_reports(self):
    guild = self.client.get_guild(941608654593998878)
    threads = [f"{thread.name} ({thread.parent.name.split('-')[0]})" for thread in guild.threads if (thread.parent and not thread.locked)]
    telegram_message: str = f"There are {len(threads)} threads open!\n"
    if threads:
        telegram_message += "\n".join(threads)
    payload = {'chat_id': "-1001437784396", 'text': telegram_message}
    requests.post(self.url, json = payload)

  @app_commands.command(name="request", description="Requests support inside of your faction ticket")
  @app_commands.describe(type="The type of request thread to open")
  async def request(self, interaction: discord.Interaction, type:Literal['Strike Report', 'Strike Appeal', 'Inside Dispute', 'Bundle Request', 'Leader Transfer']):
    if interaction.guild is None:
            return await interaction.response.send_message(content="Commands cannot be ran in DMs!", ephemeral=True)
    if interaction.channel.category.id not in [1154577495648124949, 1196515275764408372]:
           return await interaction.response.send_message(content = "Failed! This can only be ran inside of your faction ticket!", ephemeral = True)
    await interaction.response.send_modal(Modal(type))

  @request.error
  async def request_error(self, interaction: discord.Interaction, error):
    await interaction.response.send_message(content=error, ephemeral=True)

class Modal(ui.Modal):
  def __init__(self, category) -> None:
    self.category = category
    self.url = "https://api.telegram.org/botREMOVED/sendMessage"
    
    if self.category == "Strike Report":
      super().__init__(title=self.category, timeout=None, custom_id="11")
      self.add_item(ui.TextInput(label="What faction are you reporting", style=discord.TextStyle.short, placeholder="Their faction name..."))
      self.add_item(ui.TextInput(label="What rule did this faction break", style=discord.TextStyle.short, placeholder="Refer to the rules page..."))
      self.add_item(ui.TextInput(label="Video evidence links", style=discord.TextStyle.short, placeholder="https://youtube.com/..."))
      self.add_item(ui.TextInput(label="Explanation of what happened", style=discord.TextStyle.long, placeholder="Please be as detailed as possible...", max_length=3000))
    elif self.category == "Strike Appeal":
      super().__init__(title=self.category, timeout=None, custom_id="12")
      self.add_item(ui.TextInput(label="Which strike are you appealing?", style=discord.TextStyle.short, placeholder="Which strike is it..."))
    elif self.category == "Inside Dispute":
      super().__init__(title=self.category, timeout=None, custom_id="13")
      self.add_item(ui.TextInput(label="What is the IGN of the insider(s)?", style=discord.TextStyle.short, placeholder="Their IGNs..."))
      self.add_item(ui.TextInput(label="What coordinates & world did this occur?", style=discord.TextStyle.short, placeholder="Overworld (5000, 256, 5000)..."))
      self.add_item(ui.TextInput(label="Video Evidence/Logs (if applicable)", style=discord.TextStyle.short, placeholder="Video evidence/logs is preferred..."))
      self.add_item(ui.TextInput(label="Explanation of what happened", style=discord.TextStyle.long, placeholder="Please be as descriptive as possible...", max_length=3000))
    elif self.category == "Bundle Request":
      super().__init__(title=self.category, timeout=None, custom_id="14")
      self.add_item(ui.TextInput(label="Which IGN will be receiving the bundle?", style=discord.TextStyle.short, placeholder="Which IGN..."))
      self.add_item(ui.TextInput(label="What is your faction size", style=discord.TextStyle.short, placeholder="How many members in your roster..."))
      self.add_item(ui.TextInput(label="Discord link to your faction", style=discord.TextStyle.short, placeholder="discord.gg/minecadia..."))
    elif self.category == "Leader Transfer":
      super().__init__(title=self.category, timeout=None, custom_id="15")
      self.add_item(ui.TextInput(label="Which player has leader right now?", style=discord.TextStyle.short, placeholder="Who has leader..."))
      self.add_item(ui.TextInput(label="Which player needs leader?", style=discord.TextStyle.short, placeholder="Who will get leader..."))
      self.add_item(ui.TextInput(label="What is the reason for transferring?", style=discord.TextStyle.short, placeholder="Leader is afk..."))
    
  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer()
    name_of_thread = f"{self.category} {date.today().month}/{date.today().day}/{date.today().year}"
    message = await interaction.channel.send(f"`{name_of_thread}` Created!")
    thread = await message.create_thread(name=name_of_thread, reason="Via /request")
    desc = f"Hey {interaction.user.mention}!\n \nYou have created a new thread!\n**Type:** {self.category}\n \n"
    telegram_message = f"New {self.category}\nFaction: {interaction.channel.name.split('-')[0]}\nDiscord: {str(interaction.user)}\n \n"
    for item in self.children:
      desc+=f"**{item.label}**\n{item.value}\n \n"
      telegram_message+=f"{item.label}\n{item.value}\n \n"
    desc+= "**One of our staff members will be with you shortly.**"
    embed = discord.Embed(description=desc, color=discord.Color.red())
    embed.set_footer(text="Minecadia Leader Bot", icon_url = "https://i.imgur.com/DagYV3L.png")
    staff_role = discord.utils.get(interaction.guild.roles, name="Staff Team")
    strike_role = discord.utils.get(interaction.guild.roles, name="Strike Team")
    if self.category=="Strike Report" or self.category=="Strike Appeal":
      role = strike_role
    else:
      role = staff_role
    msg = await thread.send(content=role.mention)
    await msg.delete()
    await thread.send(embed=embed)
    
    payload = {'chat_id': "-1001437784396", 'text': telegram_message}
    requests.post(self.url, json = payload)

async def setup(client:commands.Bot) -> None:
  await client.add_cog(request(client))