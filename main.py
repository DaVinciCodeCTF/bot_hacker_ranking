import logging.config

import discord

from bot.core import setup_bot
from database.manager import DatabaseManager
from utils.env_checker import (
    get_discord_token, get_discord_guild_id, get_discord_channel_id,
    get_organization_name, get_database_path, get_rm_api_key
)


def main() -> None:
    """
    Set up the logger, retrieve the environment variables, create the database and run the bot.
    :return: None
    """
    logging.config.fileConfig(fname='logging.conf', disable_existing_loggers=True)
    logger = logging.getLogger('root')

    logger.info('Starting bot...')

    discord_token: str = get_discord_token()
    discord_guild_id: int = get_discord_guild_id()
    discord_channel_id: list[str] = get_discord_channel_id()
    organization_name: str = get_organization_name()
    database_path: str = get_database_path()
    rm_api_key: str = get_rm_api_key()

    DatabaseManager(database_path).create_database()

    bot_instance: discord.Bot = setup_bot(guild_id=discord_guild_id, channel_id=discord_channel_id)
    bot_instance.run(discord_token)


if __name__ == '__main__':
    main()
