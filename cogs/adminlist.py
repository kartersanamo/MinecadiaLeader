import discord
from discord import app_commands
from discord.ext import commands


class AdminListModal(discord.ui.Modal, title="Update faction admin list"):
    names = discord.ui.TextInput(
        label="Minecraft usernames",
        placeholder="PlayerOne, PlayerTwo, PlayerThree",
        style=discord.TextStyle.paragraph,
        max_length=1000,
    )

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.source_interaction = interaction

    async def on_submit(self, interaction: discord.Interaction) -> None:
        igns = [ign.strip() for ign in str(self.names.value).split(",") if ign.strip()]
        igns_string = "\n".join(f"#{index} {ign}" for index, ign in enumerate(igns, 1))
        await interaction.response.send_message(
            "Successfully updated your admin list!", ephemeral=True
        )
        async for message in interaction.channel.history(limit=1, oldest_first=True):
            if len(message.embeds) < 2:
                return
            embed = message.embeds[1]
            embed.set_field_at(0, name="Admin List", value=f"```{igns_string}```")
            await message.edit(embeds=[message.embeds[0], embed])

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
        await interaction.response.send_modal(AdminListModal(interaction))

async def setup(client:commands.Bot) -> None:
  await client.add_cog(AdminList(client))