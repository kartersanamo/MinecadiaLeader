from discord.ext import commands
import discord

def is_staff(message):
    names_of_roles = ["*", "Owner", "Management", "Admin", "Developer", "Staff Team"]
    for role_name in names_of_roles:
      role = discord.utils.get(message.guild.roles, name=role_name)
      if role in message.author.roles:
        return True
    return False

class embed(commands.Cog):
  def __init__(self, client: commands.Bot):
    self.client = client
    
  @commands.Cog.listener()
  async def on_message(self, message):
      try:
        if not is_staff(message):
          return
      except:
        return
      split = message.content.split("\n")
      msg = message.content
      footer = False
      title = False
      image = False
      thumbnail = False
      everyone = False
      if "-announcement" in split:
        if is_staff(message):
          msg = msg.replace("-announcement", "")
          if "-footer" in split:
            msg = msg.replace("-footer", "")
            footer = True
          if "-title" in split:
            title_index = split.index("-title")
            title = split[:title_index:][0]
            msg = msg.replace(title, "")
            msg = msg.replace("-title", "")
          if "-thumbnail" in split:
            thumbnail_index = split.index("-thumbnail")
            thumbnail = split[thumbnail_index-1:thumbnail_index:][0]
            msg = msg.replace(thumbnail, "")
            msg = msg.replace("-thumbnail", "")
          if "-image" in split:
            image_index = split.index("-image")
            image = split[image_index-1:image_index:][0]
            msg = msg.replace(image, "")
            msg = msg.replace("-image", "")
          if "-everyone" in split:
            everyone = True
            msg = msg.replace("-everyone", "")
          if title:
            embed = discord.Embed(title=title, description=msg, color=discord.Color.red())
          else:
            embed = discord.Embed(description=msg, color=discord.Color.red())
          if footer:
            embed.timestamp = message.created_at
            embed.set_footer(text=message.author, icon_url=message.author.avatar)
          if image:
            try:
              embed.set_image(url=image)
            except:
              pass
          if thumbnail:
            try:
              embed.set_thumbnail(url=thumbnail)
            except:
              pass
          await message.delete()
          if everyone:
            await message.channel.send(content="@everyone", embed=embed)
          else:
            await message.channel.send(embed=embed)

async def setup(client:commands.Bot) -> None:
  await client.add_cog(embed(client))