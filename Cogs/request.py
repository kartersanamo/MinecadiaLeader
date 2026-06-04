from discord.ext import commands, tasks
from discord import app_commands, ui
from datetime import date
from typing import Literal
import requests
import discord
from utils.embeds import get_embed_logo_url

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
    if len(threads) == 0: return
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
  _CUSTOM_IDS = {
    "Strike Report": "11",
    "Strike Appeal": "12",
    "Inside Dispute": "13",
    "Bundle Request": "14",
    "Leader Transfer": "15",
  }

  def __init__(self, category) -> None:
    self.category = category
    self.url = "https://api.telegram.org/botREMOVED/sendMessage"
    self._modal_field_headings: list[str] = []
    super().__init__(
      title=self.category,
      timeout=None,
      custom_id=self._CUSTOM_IDS[category],
    )

    if self.category == "Strike Report":
      self._add_field("What faction are you reporting", style=discord.TextStyle.short, placeholder="Their faction name...")
      self._add_field("What rule did this faction break", style=discord.TextStyle.short, placeholder="Refer to the rules page...")
      self._add_field("Video evidence links", style=discord.TextStyle.short, placeholder="https://youtube.com/...")
      self._add_field("Explanation of what happened", style=discord.TextStyle.long, placeholder="Please be as detailed as possible...", max_length=3000)
    elif self.category == "Strike Appeal":
      self._add_field("Which strike are you appealing?", style=discord.TextStyle.short, placeholder="Which strike is it...")
    elif self.category == "Inside Dispute":
      self._add_field("What is the IGN of the insider(s)?", style=discord.TextStyle.short, placeholder="Their IGNs...")
      self._add_field("What coordinates & world did this occur?", style=discord.TextStyle.short, placeholder="Overworld (5000, 256, 5000)...")
      self._add_field("Video Evidence/Logs (if applicable)", style=discord.TextStyle.short, placeholder="Video evidence/logs is preferred...")
      self._add_field("Explanation of what happened", style=discord.TextStyle.long, placeholder="Please be as descriptive as possible...", max_length=3000)
    elif self.category == "Bundle Request":
      self._add_field("Which IGN will be receiving the bundle?", style=discord.TextStyle.short, placeholder="Which IGN...")
      self._add_field("What is your faction size", style=discord.TextStyle.short, placeholder="How many members in your roster...")
      self._add_field("Discord link to your faction", style=discord.TextStyle.short, placeholder="discord.gg/minecadia...")
    elif self.category == "Leader Transfer":
      self._add_field("Which player has leader right now?", style=discord.TextStyle.short, placeholder="Who has leader...")
      self._add_field("Which player needs leader?", style=discord.TextStyle.short, placeholder="Who will get leader...")
      self._add_field("What is the reason for transferring?", style=discord.TextStyle.short, placeholder="Leader is afk...")

  def _add_field(self, heading: str, **kwargs) -> None:
    self._modal_field_headings.append(heading)
    self.add_item(ui.TextInput(label=heading, **kwargs))

  async def on_submit(self, interaction: discord.Interaction):
    await interaction.response.defer()
    name_of_thread = f"{self.category} {date.today().month}/{date.today().day}/{date.today().year}"
    message = await interaction.channel.send(f"`{name_of_thread}` Created!")
    thread = await message.create_thread(name=name_of_thread, reason="Via /request")
    desc = f"Hey {interaction.user.mention}!\n \nYou have created a new thread!\n**Type:** {self.category}\n \n"
    telegram_message = f"New {self.category}\nFaction: {interaction.channel.name.split('-')[0]}\nDiscord: {str(interaction.user)}\n \n"
    for heading, item in zip(self._modal_field_headings, self.children):
      if not isinstance(item, ui.TextInput):
        continue
      desc += f"**{heading}**\n{item.value}\n \n"
      telegram_message += f"{heading}\n{item.value}\n \n"
    desc+= "**One of our staff members will be with you shortly.**"
    embed = discord.Embed(description=desc, color=discord.Color.red())
    logo_url = get_embed_logo_url("Assets/Logo.png")
    embed.set_footer(text="Minecadia Leader Bot", icon_url = logo_url)
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
