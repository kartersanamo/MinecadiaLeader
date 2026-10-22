import discord
from discord import app_commands
from discord.ext import commands


class Announcement(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="announcement", description="Post a formatted staff announcement")
    @app_commands.describe(
        message="Announcement text",
        title="Optional title",
        image="Optional image URL",
        thumbnail="Optional thumbnail URL",
        footer="Include the author and timestamp",
        everyone="Mention everyone",
    )
    async def announcement(
        self,
        interaction: discord.Interaction,
        message: str,
        title: str | None = None,
        image: str | None = None,
        thumbnail: str | None = None,
        footer: bool = False,
        everyone: bool = False,
    ) -> None:
        if interaction.guild is None:
            return await interaction.response.send_message(
                "Commands cannot be run in DMs!", ephemeral=True
            )
        staff_roles = {"*", "Owner", "Management", "Admin", "Developer", "Staff Team"}
        if not isinstance(interaction.user, discord.Member) or not any(
            role.name in staff_roles for role in interaction.user.roles
        ):
            return await interaction.response.send_message(
                "You do not have permission to use this command.", ephemeral=True
            )
        embed = discord.Embed(description=message, color=discord.Color.red())
        if title:
            embed.title = title
        if image:
            embed.set_image(url=image)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if footer:
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(
                text=str(interaction.user),
                icon_url=interaction.user.display_avatar.url,
            )
        await interaction.response.send_message("Announcement posted.", ephemeral=True)
        await interaction.channel.send(
            content="@everyone" if everyone else None, embed=embed
        )


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Announcement(client))
