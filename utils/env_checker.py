import logging
import os

logger = logging.getLogger(__name__)


def get_discord_token() -> str:
    """
    Retrieve the discord token from the environment variables.
    :return: str, discord token
    """
    discord_token: str | None = os.environ.get('DISCORD_TOKEN')
    if discord_token is None or discord_token == '':
        raise ValueError('DISCORD_TOKEN is not set in the environment variables.')
    logger.debug(f'Discord token retrieved: {discord_token[:10]}...')
    return discord_token


def get_discord_guild_id() -> int:
    """
    Retrieve the discord guild id from the environment variables.
    :return: int, discord guild id
    """
    discord_guild_id_str: str | None = os.environ.get('DISCORD_GUILD_ID')
    if discord_guild_id_str is None or discord_guild_id_str == '':
        raise ValueError('DISCORD_GUILD_ID is not set in the environment variables.')
    try:
        discord_guild_id: int | None = int(discord_guild_id_str)
    except ValueError:
        raise ValueError('DISCORD_GUILD_ID is not a valid integer.')
    logger.debug(f'Discord guild id retrieved: {discord_guild_id}')
    return discord_guild_id


def get_discord_channel_id() -> list[str]:
    """
    Retrieve the discord channel id where the bot will send the messages from the environment variables.
    :return: list[str], discord channel id
    """
    discord_channel_id: str | None = os.environ.get('DISCORD_CHANNEL_ID')
    if discord_channel_id is None or discord_channel_id == '':
        raise ValueError('DISCORD_CHANNEL_ID is not set in the environment variables.')
    discord_channel_id: list[str] = discord_channel_id.split(',')
    logger.debug(f'Discord channel id retrieved: {", ".join(discord_channel_id)}')
    return discord_channel_id


def get_organization_name(log: bool = True) -> str:
    """
    Retrieve the organization name from the environment variables.
    :return: str, organization name
    """
    organization_name: str | None = os.environ.get('ORGANIZATION_NAME')
    if organization_name is None or organization_name == '':
        raise ValueError('ORGANIZATION_NAME is not set in the environment variables.')
    if log:
        logger.debug(f'Organization name retrieved: {organization_name}')
    return organization_name


def get_database_path() -> str:
    """
    Retrieve the database path from the environment variables.
    :return: str, database path
    """
    database_path: str | None = os.environ.get('DATABASE_PATH')
    if database_path is None or database_path == '':
        raise ValueError('DATABASE_PATH is not set in the environment variables.')
    logger.debug(f'Database path retrieved: {database_path}')
    return database_path


def get_rm_api_key() -> str:
    """
    Retrieve the rm api key from the environment variables.
    :return: str, rm api key
    """
    rm_api_key: str | None = os.environ.get('RM_API_KEY')
    if rm_api_key is None or rm_api_key == '':
        raise ValueError('RM_API_KEY is not set in the environment variables.')
    logger.debug(f'RM api key retrieved: {rm_api_key[:10]}...')
    return rm_api_key
