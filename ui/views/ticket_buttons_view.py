import discord



class TicketButtonsView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    async def make_ticket(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name="Staff Team")
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                read_message_history=True,
                send_messages=True,
                attach_files=True,
                embed_links=True,
            ),
            interaction.guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            ),
            role: discord.PermissionOverwrite(
                view_channel=True,
                read_message_history=True,
                send_messages=True,
                attach_files=True,
                embed_links=True,
            ),
        }
        message = (
            f"Hey {interaction.user.mention}!\n​\nYou have created a new ticket!\n"
            "**Type:** Kitmap Bundle Ticket\n​\nTo get the best possible support, "
            "please clearly state:```- Your IGN\n- Your Faction Name\n- Faction Size\n"
            "- Discord Link to Faction```\nNOTE: In order to qualify for the faction bundle, "
            "you must have 8 players in your faction (not roster) on the start of the world. "
            "You will have 24 hours from the start of the world to get all 8 members in your faction. "
            "If you cannot get all of your members in time, please let us know!\n​\nNOTE: You must have 8 "
            "**unique** players. Meaning, they must be real players and cannot be alt accounts. "
            "WE WILL BE CHECKING.\n​\nOur Staff Team will be with you shortly"
        )
        category = discord.utils.get(
            interaction.guild.categories, name="Kitmap Bundle Tickets"
        )
        if len(category.channels) >= 50:
            category = discord.utils.get(
                interaction.guild.categories, name="Kitmap Bundle Tickets #2"
            )
        channel = await interaction.guild.create_text_channel(
            name=f"{interaction.user.name}-ticket",
            category=category,
            overwrites=overwrites,
        )
        await interaction.response.send_message(
            content=f"Ticket created! {channel.mention}", ephemeral=True
        )
        embed = discord.Embed(
            title="Kitmap Bundle Ticket", description=message, color=discord.Color.red()
        )
        logo_url = interaction.client.app.embeds.get_logo_url("assets/Logo.png")
        embed.set_footer(text="Minecadia Leader Bot", icon_url=logo_url)
        await channel.send(embed=embed, file=discord.File("assets/Logo.png"))

    @discord.ui.button(
        label="Click here to open a Kitmap Bundle Ticket!",
        style=discord.ButtonStyle.red,
        custom_id="2",
    )
    async def kitmap(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.make_ticket(interaction)
