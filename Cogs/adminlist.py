from discord.ext import commands
from discord import app_commands
import discord

def is_staff(message):
    names_of_roles = ["*", "Owner", "Management", "Admin", "Developer", "Staff Team"]
    for role_name in names_of_roles:
      role = discord.utils.get(message.guild.roles, name=role_name)
      if role in message.author.roles:
        return True
    return False

class AdminList(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name = "admin-list", description = "Edit your faction's admin list")
    async def admin_list(self, interaction: discord.Interaction):
        if interaction.guild is None:
            return await interaction.response.send_message(content="Commands cannot be ran in DMs!", ephemeral=True)
        if interaction.channel.category.id not in [1154577495648124949, 1196515275764408372]:
           return await interaction.response.send_message(content = "Failed! This can only be ran inside of your faction ticket!", ephemeral = True)
        embed = discord.Embed(description = "Please enter a list of IGNs **seperated by commas** that can recieve 3 star for your faction at any time upon request.",
                             color = discord.Color.red())
        await interaction.response.send_message(embed = embed, ephemeral = True)
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel
        message = await interaction.client.wait_for('message', check = check)
        await message.delete()
        await interaction.edit_original_response(embeds = [], content = f"Successfully updated your admin list!")
        igns = message.content.replace(' ', '').split(',')
        igns_string = ""
        for index, ign in enumerate(igns):
           igns_string += f"#{index + 1} {ign}\n"
        async for message in interaction.channel.history(limit = 1, oldest_first = True):
           top_embed = message.embeds[0]
           embed = message.embeds[1]
           embed.set_field_at(0, name = "Admin List", value = f"```{igns_string}```")
           await message.edit(embeds = [top_embed, embed])

async def setup(client:commands.Bot) -> None:
  await client.add_cog(AdminList(client))