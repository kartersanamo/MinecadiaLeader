import discord


class EmptyView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
