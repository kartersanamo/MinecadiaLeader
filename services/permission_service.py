import discord


class PermissionService:
    _STAFF_ROLES = [
        "Staff Team",
        "Admin",
        "Strike Team",
        "*",
        "Management",
        "Developer",
        "Owner",
    ]
    _ADMIN_ROLES = ["Owner", "Management", "Developer", "*", "Admin"]

    @classmethod
    def is_staff_interaction(cls, interaction: discord.Interaction) -> bool:
        for role_name in cls._STAFF_ROLES:
            role = discord.utils.get(interaction.guild.roles, name=role_name)
            if role in interaction.user.roles:
                return True
        return False

    @classmethod
    def is_staff_message(cls, message: discord.Message) -> bool:
        for role_name in cls._STAFF_ROLES:
            role = discord.utils.get(message.guild.roles, name=role_name)
            if role in message.author.roles:
                return True
        return False

    @classmethod
    def is_admin_ctx(cls, ctx) -> bool:
        for role_name in cls._ADMIN_ROLES:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if role in ctx.author.roles:
                return True
        return False


def is_staff(interaction: discord.Interaction) -> bool:
    return PermissionService.is_staff_interaction(interaction)


def is_staff_m(message: discord.Message) -> bool:
    return PermissionService.is_staff_message(message)


def is_admin(ctx) -> bool:
    return PermissionService.is_admin_ctx(ctx)
