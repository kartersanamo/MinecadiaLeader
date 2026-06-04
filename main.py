import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)

from Cogs.tickets import TicketButtons
from Cogs.factions import RoleButtons
from Assets.functions import get_data, task, log_tasks

from discord import app_commands
from discord.ext import commands
import discord
from dotenv import load_dotenv

load_dotenv()


COG_FILES = [file.split(".")[0].title() for file in os.listdir("Cogs/") if file.endswith(".py")]


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix = '.', intents = discord.Intents().all())
        self.data: dict = get_data()

    @task("Setup Cogs")
    async def setup_cogs(self):
        for ext in self.cogslist:
            log_tasks.info(f"Loaded cog {ext}.py")
            await self.load_extension("Cogs." + ext)
    
    @task("Register Analytics")
    async def register_analytics(self):
        import sys

        _minecadia = Path(__file__).resolve().parent.parent
        if str(_minecadia) not in sys.path:
            sys.path.insert(0, str(_minecadia))
        from _analytics.register import register_command_tracking

        await register_command_tracking(self)

    @task("Add Views")
    async def add_views(self):
        views: list[discord.ui.View] = [
            TicketButtons(), RoleButtons()
        ]
        for view in views:
            log_tasks.info(f"Added view {view.__class__.__name__}")
            self.add_view(view)

    @task("Update Presence")
    async def update_presence(self):
        presence = self.data["PRESENCE"]
        await client.change_presence(activity = discord.Game(name = presence))
        log_tasks.info(f"Updated the bot's presence to {presence}")

    @task("Remove Help")
    async def remove_help(self):
        self.remove_command("help")

    @task("Sync Command Tree")
    async def sync_command_tree(self):
        commands: list[discord.app_commands.AppCommand] = await self.tree.sync()
        command_list: str = ', '.join([command.name for command in commands])
        log_tasks.info(f"Synced {len(commands)} commands {command_list}")

    @task("Setup Hook")
    async def setup_hook(self):
        await self.setup_cogs()
        await self.register_analytics()
        await self.add_views()

    @task("Logging in")
    async def on_ready(self):
        await self.update_presence()
        await self.remove_help()
        await self.sync_command_tree()
        log_tasks.info(f"Logged in as {client.user} ({client.user.id})")


client = Client()


@task("Leader Reload Command", True)
async def leader_reload_command(interaction: discord.Interaction, cog: str):
    if interaction.guild is None:
        return await interaction.response.send_message(content = "Commands cannot be ran in DMs!", ephemeral = True)
    if cog not in COG_FILES:
        await interaction.response.send_message(f"Invalid cog name **{cog}.py**", ephemeral = True)
        return
    await client.reload_extension(f"Cogs.{cog.lower()}")
    await interaction.response.send_message(f"Successfully reloaded **{cog}.py**", ephemeral = True)

async def cog_autocomplete(_: discord.Interaction, current: str):
    return [
        app_commands.Choice(name = cog, value = cog)
        for cog in COG_FILES if current.lower() in cog.lower()
    ]

@client.tree.command(name = "leader-reload", description = "Reloads a Cog Class")
@app_commands.autocomplete(cog = cog_autocomplete)
async def leaderreload(interaction: discord.Interaction, cog: str):
    await leader_reload_command(interaction, cog)

@leaderreload.error
async def leaderreload_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    await interaction.followup.send(content = error, ephemeral = True) if interaction.response.is_done() else await interaction.response.send_message(content = error, ephemeral = True)

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Set DISCORD_TOKEN in .env")

if __name__ == "__main__":
    client.run(TOKEN)
