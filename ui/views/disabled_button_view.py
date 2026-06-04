import discord


class DisabledButtonView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Kitmap Bundle Tickets are currently disabled!",
        row=1,
        style=discord.ButtonStyle.grey,
        custom_id="3",
        disabled=True,
    )
    async def kitmapdisabled(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
