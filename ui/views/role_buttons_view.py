import discord

from ui.modals.role_request_modal import RoleRequestModal
from ui.views.remove_roles_view import RemoveRolesView

class RoleButtonsView(discord.ui.View):
    def __init__(self)-> None:
      super().__init__(timeout=None)
      
    @discord.ui.button(label = "Request Roles", emoji = "📝", style = discord.ButtonStyle.red, custom_id = "3")
    async def request(self, interaction: discord.Interaction, Button: discord.ui.Button):
      leader_role = discord.utils.get(interaction.guild.roles, name="Faction Leader")
      coleader_role = discord.utils.get(interaction.guild.roles, name="Faction Coleader")
      if leader_role in interaction.user.roles or coleader_role in interaction.user.roles:
        confirm = RemoveRolesView()
        confirm.old_interaction = interaction
        await interaction.response.send_message(content="Failed! You already have a role! Would you like to remove your role?", ephemeral=True, view=confirm)
      else:
        await interaction.response.send_modal(RoleRequestModal())
  