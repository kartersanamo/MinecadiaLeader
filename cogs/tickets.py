from services.permission_service import PermissionService
from services.permission_service import is_staff
from discord.ext import commands
from discord import app_commands
import discord

from ui.views.disabled_button_view import DisabledButtonView
from ui.views.ticket_buttons_view import TicketButtonsView


class TicketsCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.command()
    async def sendtickets(self, ctx: commands.Context):
        if PermissionService.is_admin_ctx(ctx):
            await ctx.message.delete()
            embed = discord.Embed(
                title="Request a Bundle!",
                description=(
                    "If you'd like to request a bundle for the upcoming map of Kitmap, "
                    "then please press the button down below. This button will open up a ticket "
                    "for you where you can enter the required information in order to get your bundle!"
                ),
                color=discord.Color.red(),
            )
            logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
            embed.set_footer(text="Minecadia Leader Bot", icon_url=logo_url)
            embed.set_thumbnail(url="attachment://Logo.png")
            await ctx.send(
                embed=embed,
                view=TicketButtonsView(),
                file=discord.File("assets/Logo.png"),
            )

    @app_commands.command(
        name="toggle-tickets", description="Enables/Disables Kitmap Bundle Tickets"
    )
    @app_commands.check(is_staff)
    async def toggletickets(self, interaction: discord.Interaction):
        if interaction.guild is None:
            return await interaction.response.send_message(
                content="Commands cannot be ran in DMs!", ephemeral=True
            )
        channel = discord.utils.get(interaction.guild.channels, name="bundle-request")
        async for message in channel.history(limit=1):
            msg = message
        if message.components[0].children[0].disabled:
            await message.edit(view=TicketButtonsView())
        else:
            await message.edit(view=DisabledButtonView())
        await interaction.response.send_message(
            "Succesfully toggled the kitmap bundles", ephemeral=True
        )

    @toggletickets.error
    async def toggletickets_error(self, interaction: discord.Interaction, error):
        await interaction.response.send_message(content=error, ephemeral=True)


TicketButtons = TicketButtonsView
DisabledButton = DisabledButtonView


async def setup(client: commands.Bot) -> None:
    await client.add_cog(TicketsCog(client))
