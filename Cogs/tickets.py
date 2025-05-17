from Cogs.factions import is_admin, is_staff
from discord.ext import commands
from discord import app_commands
import discord

class DisabledButton(discord.ui.View):
  def __init__(self) -> None:
      super().__init__(timeout=None)
  
  @discord.ui.button(label = "Kitmap Bundle Tickets are currently disabled!", row = 1, style = discord.ButtonStyle.grey, custom_id = "3", disabled=True)
  async def kitmapdisabled(self, interaction: discord.Interaction, Button: discord.ui.Button):
    await interaction.response.defer()
  
class TicketButtons(discord.ui.View):
    def __init__(self) -> None:
      super().__init__(timeout=None)

    async def make_ticket(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name="Staff Team")
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel = False),
                      interaction.user: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True),
                      interaction.guild.me: discord.PermissionOverwrite(view_channel = True, send_messages = True, read_message_history = True), 
                      role: discord.PermissionOverwrite(view_channel = True, read_message_history = True, send_messages = True, attach_files = True, embed_links = True)}
        message = f"Hey {interaction.user.mention}!\n​\nYou have created a new ticket!\n**Type:** Kitmap Bundle Ticket\n​\nTo get the best possible support, please clearly state:```- Your IGN\n- Your Faction Name\n- Faction Size\n- Discord Link to Faction```\nNOTE: In order to qualify for the faction bundle, you must have 8 players in your faction (not roster) on the start of the world. You will have 24 hours from the start of the world to get all 8 members in your faction. If you cannot get all of your members in time, please let us know!\n​\nNOTE: You must have 8 **unique** players. Meaning, they must be real players and cannot be alt accounts. WE WILL BE CHECKING.\n​\nOur Staff Team will be with you shortly"
        category = discord.utils.get(interaction.guild.categories, name="Kitmap Bundle Tickets")
        if len(category.channels) >= 50:
          category = discord.utils.get(interaction.guild.categories, name="Kitmap Bundle Tickets #2")
        channel = await interaction.guild.create_text_channel(name=f"{interaction.user.name}-ticket", category=category, overwrites=overwrites)
        await interaction.response.send_message(content=f"Ticket created! {channel.mention}", ephemeral=True)
        embed = discord.Embed(title="Kitmap Bundle Ticket", description=message, color=discord.Color.red())
        embed.set_footer(text="Minecadia Leader Bot", icon_url = "https://i.imgur.com/DagYV3L.png")
        await channel.send(embed=embed)

    @discord.ui.button(label = "Click here to open a Kitmap Bundle Ticket!", style = discord.ButtonStyle.red, custom_id = "2")
    async def kitmap(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await self.make_ticket(interaction)

class tickets(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client

  @commands.command()
  async def sendtickets(self, ctx: commands.Context):
    if is_admin(ctx):
      await ctx.message.delete()
      embed = discord.Embed(title="Request a Bundle!", description=f"If you'd like to request a bundle for the upcoming map of Kitmap, then please press the button down below. This button will open up a ticket for you where you can enter the required information in order to get your bundle!", color=discord.Color.red())
      embed.set_footer(text="Minecadia Leader Bot", icon_url = "https://i.imgur.com/DagYV3L.png")
      embed.set_thumbnail(url="https://i.imgur.com/DagYV3L.png")
      await ctx.send(embed=embed, view=TicketButtons())
  
  @app_commands.command(name= "toggle-tickets", description="Enables/Disables Kitmap Bundle Tickets")
  @app_commands.check(is_staff)
  async def toggletickets(self, interaction: discord.Interaction):
    if interaction.guild is None:
            return await interaction.response.send_message(content="Commands cannot be ran in DMs!", ephemeral=True)
    channel = discord.utils.get(interaction.guild.channels, name="bundle-request")
    async for message in channel.history(limit=1):
      msg = message
    if message.components[0].children[0].disabled:
      await message.edit(view=TicketButtons())
    else:
      await message.edit(view=DisabledButton())
    await interaction.response.send_message("Succesfully toggled the kitmap bundles", ephemeral=True)

  @toggletickets.error
  async def toggletickets_error(self, interaction: discord.Interaction, error):
    await interaction.response.send_message(content=error, ephemeral=True)

async def setup(client:commands.Bot) -> None:
  await client.add_cog(tickets(client))