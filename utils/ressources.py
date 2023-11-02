import discord
from discord.ext import commands

emoji_icon_assets = {
    'HTB_logo': 'resources/HTB_logo.png',
    'RM_logo': 'resources/RM_logo.png',
    'THM_logo': 'resources/THM_logo.png',
}


async def setup_emoji(bot: commands.Bot, guild_id: int) -> None:
    guild = bot.get_guild(guild_id)
    if guild is None:
        print(f"Couldn't find the guild with ID {guild_id}")
        return

    for name, path in emoji_icon_assets.items():
        emoji = discord.utils.get(guild.emojis, name=name)
        if emoji is None:
            with open(path, 'rb') as f:
                image = f.read()
            await guild.create_custom_emoji(name=name, image=image)
