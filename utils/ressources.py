import logging
import discord
from discord.ext import commands

emoji_icon_assets = {
    'HTB_logo': 'resources/HTB_logo.png',
    'RM_logo': 'resources/RM_logo.png',
    'THM_logo': 'resources/THM_logo.png',
}

logger = logging.getLogger(__name__)


async def setup_emoji(bot: commands.Bot, guild_id: int) -> None:
    guild = bot.get_guild(guild_id)
    if guild is None:
        logger.error(f'Guild {guild_id} not found.')
        return

    for name, path in emoji_icon_assets.items():
        emoji = discord.utils.get(guild.emojis, name=name)
        if emoji is not None:
            continue

        try:
            with open(path, 'rb') as f:
                image = f.read()
            await guild.create_custom_emoji(name=name, image=image)
            logger.info(f'Emoji {name} created.')
        except discord.HTTPException as e:
            # 30008 = Maximum number of emojis reached
            if getattr(e, "code", None) == 30008:
                logger.warning(
                    f'Cannot create emoji {name}: maximum number of emojis reached on guild {guild_id}.'
                )
            else:
                logger.warning(f'Cannot create emoji {name}: {e}')
        except Exception as e:
            logger.warning(f'Unexpected error while creating emoji {name}: {e}')

    logger.info('Emoji setup done.')
