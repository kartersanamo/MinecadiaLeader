import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)

import logger  # noqa: F401 — configures logging before other imports

from Cogs.tickets import TicketButtons
from Cogs.factions import RoleButtons
from Assets.functions import task, log_tasks, log_commands
from discord.ext import commands
from typing import Literal
import discord
from dotenv import load_dotenv

load_dotenv()

COGS_LIST = [
    "listthreads",
    "embed",
    "request",
    "purge",
    "factions",
    "edit",
    "tickets",
    "close",
    "rename",
    "lock",
    "adminlist",
]


class Client(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("."),
            intents=discord.Intents().all(),
        )
        self.cogslist = COGS_LIST

    @task("Setup Cogs")
    async def setup_cogs(self):
        for ext in self.cogslist:
            log_tasks.info(f"Loaded cog {ext}.py")
            await self.load_extension("Cogs." + ext)
        import sys

        _minecadia = Path(__file__).resolve().parent.parent
        if str(_minecadia) not in sys.path:
            sys.path.insert(0, str(_minecadia))
        from _analytics.register import register_command_tracking

        await register_command_tracking(self)

    @task("Add Views")
    async def add_views(self):
        views = [TicketButtons(), RoleButtons()]
        for view in views:
            log_tasks.info(f"Added view {view.__class__.__name__}")
            self.add_view(view)

    @task("Remove Help")
    async def remove_help(self):
        self.remove_command("help")

    @task("Sync Command Tree")
    async def sync_command_tree(self):
        commands_synced = await self.tree.sync()
        log_tasks.info(
            f"Synced {len(commands_synced)} commands "
            f"{[command.name for command in commands_synced]}"
        )

    @task("Setup Hook")
    async def setup_hook(self):
        await self.setup_cogs()
        await self.add_views()

    @task("Logging in")
    async def on_ready(self):
        await self.remove_help()
        await self.sync_command_tree()
        log_tasks.info(f"Logged in as {client.user} ({client.user.id})")

    async def on_command_error(self, ctx, error):
        log_commands.error(f"Command error: {error}")


client = Client()


@client.tree.command(name="reload", description="Reloads a Cog Class")
async def reload(
    interaction: discord.Interaction,
    cog: Literal[
        "ListThreads",
        "Rename",
        "Embed",
        "Request",
        "Purge",
        "Factions",
        "Edit",
        "Tickets",
        "Close",
        "Lock",
        "AdminList",
    ],
):
    if interaction.user.id == 837793755838939157:
        await client.reload_extension(f"Cogs.{cog.lower()}")
        log_commands.info(
            f"Reloaded cog {cog}.py by {interaction.user} ({interaction.user.id})"
        )
        await interaction.response.send_message(
            f"Successfully reloaded **{cog}.py**", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "You are not permitted to do this!", ephemeral=True
        )


@reload.error
async def reload_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    log_commands.error(f"/{interaction.command.name} error {error}")
    if interaction.response.is_done():
        await interaction.followup.send(content=str(error), ephemeral=True)
    else:
        await interaction.response.send_message(content=str(error), ephemeral=True)


TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Set DISCORD_TOKEN in .env")

if __name__ == "__main__":
    client.run(TOKEN)
