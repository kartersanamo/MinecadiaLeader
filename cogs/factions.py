from services.permission_service import PermissionService
from discord.ext import commands
import discord

from repositories.faction_repository import FactionRepository
from ui.views.role_buttons_view import RoleButtonsView


class FactionsCog(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self._factions = FactionRepository()

    async def remove_from_ticket(
        self, guild: discord.Guild, user_id: str, channel: discord.TextChannel
    ):
        try:
            user = discord.utils.get(guild.members, id=int(user_id))
            perms = channel.overwrites_for(user)
            perms.view_channel = False
            await channel.set_permissions(user, overwrite=perms)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        rows = await self._factions.find_by_leader(member.id)
        if rows:
            channel = discord.utils.get(
                member.guild.channels, id=int(rows[0]["channel_id"])
            )
            if rows[0]["leader_id"] == member.id:
                category = discord.utils.get(
                    member.guild.categories, name="Archived Channels"
                )
                await channel.edit(category=category)
                embed = discord.Embed(
                    title="Leader left!",
                    description=(
                        f"Uh oh! The leader, `{member.name}` has left the discord, "
                        "so all faction members have been removed from this ticket, "
                        "and the channel has been archived."
                    ),
                    color=discord.Color.red(),
                )
                logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
                embed.set_footer(text="Minecadia Leader Bot", icon_url=logo_url)
                await channel.send(embed=embed)
                await self.remove_from_ticket(member.guild, member.id, channel)
                return
        rows = await self._factions.find_by_coleader_1(member.id)
        if rows:
            channel = discord.utils.get(
                member.guild.channels, id=int(rows[0]["channel_id"])
            )
            embed = discord.Embed(
                title="Coleader left!",
                description=(
                    f"Uh oh! The coleader, `{member.name}` has left the discord, "
                    "and is no longer in this channel anymore."
                ),
                color=discord.Color.red(),
            )
            logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
            embed.set_footer(text="Minecadia Leader Bot", icon_url=logo_url)
            await channel.send(embed=embed, file=discord.File("assets/Logo.png"))
            await self.remove_from_ticket(
                member.guild, rows[0]["coleader_id_1"], channel
            )
            return
        rows = await self._factions.find_by_coleader_2(member.id)
        if rows:
            channel = discord.utils.get(
                member.guild.channels, id=int(rows[0]["channel_id"])
            )
            embed = discord.Embed(
                title="Coleader left!",
                description=(
                    f"Uh oh! The coleader, `{member.name}` has left the discord, "
                    "and is no longer in this channel anymore."
                ),
                color=discord.Color.red(),
            )
            logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
            embed.set_footer(text="Minecadia Leader Bot", icon_url=logo_url)
            await channel.send(embed=embed)
            await self.remove_from_ticket(
                member.guild, rows[0]["coleader_id_2"], channel
            )

    @commands.command()
    async def sendrolerequest(self, ctx):
        if PermissionService.is_admin_ctx(ctx):
            await ctx.message.delete()
            embed = discord.Embed(
                title="Role Request",
                description=(
                    "Click the button below to request roles! It is important to enter "
                    "the information requested precisely as this system is automated. "
                    "Please only request roles for `YOUR` faction with the correct role "
                    "that you have in that faction.\n \nEach faction can only have:"
                    "```- 1 Leader\n- 2 Coleaders```"
                    "Please make a support ticket if you have any questions or run into any issues."
                ),
                color=discord.Color.red(),
            )
            logo_url = self.client.app.embeds.get_logo_url("assets/Logo.png")
            embed.set_footer(text="Minecadia Leader Bot", icon_url=logo_url)
            await ctx.send(
                embed=embed,
                view=RoleButtonsView(),
                file=discord.File("assets/Logo.png"),
            )


# Backward-compatible exports for main.py persistent views
RoleButtons = RoleButtonsView


async def setup(client: commands.Bot) -> None:
    await client.add_cog(FactionsCog(client))
