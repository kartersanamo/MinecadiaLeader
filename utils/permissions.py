import discord


def is_staff(interaction: discord.Interaction) -> bool:
    names_of_roles = [
        "Staff Team",
        "Admin",
        "Strike Team",
        "*",
        "Management",
        "Developer",
        "Owner",
    ]
    for role_name in names_of_roles:
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role in interaction.user.roles:
            return True
    return False


def is_staff_m(message: discord.Message) -> bool:
    names_of_roles = [
        "Staff Team",
        "Admin",
        "Strike Team",
        "*",
        "Management",
        "Developer",
        "Owner",
    ]
    for role_name in names_of_roles:
        role = discord.utils.get(message.guild.roles, name=role_name)
        if role in message.author.roles:
            return True
    return False


def is_admin(ctx) -> bool:
    names_of_roles = ["Owner", "Management", "Developer", "*", "Admin"]
    for role_name in names_of_roles:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role in ctx.author.roles:
            return True
    return False
