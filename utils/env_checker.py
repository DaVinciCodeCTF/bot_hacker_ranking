import logging
import os

import hvac

logger = logging.getLogger(__name__)

def get_birthday_channel_id():
    if "BIRTHDAY_CHANNEL_ID" not in os.environ:
        raise EnvironmentError("BIRTHDAY_CHANNEL_ID not set in environment variables.")
    return int(os.environ["BIRTHDAY_CHANNEL_ID"])

def retrieve_vault_secret(vault_client: hvac.Client, secret_path: str, secret_name: str) -> str:
    """
    Retrieve a secret from the vault.
    https://hvac.readthedocs.io/en/stable/usage/secrets_engines/kv_v1.html#read-a-secret
    :param vault_client: hvac.Client, vault client
    :param secret_path: str, path to the secret
    :param secret_name: str, name of the secret
    :return: str, secret
    """
    try:
        return vault_client.secrets.kv.v1.read_secret(path=secret_path, mount_point='bot')['data'][secret_name]
    except Exception as e:
        raise ValueError(f'Error while retrieving the secret {secret_name} from the vault: {e}')


def get_dev_mode() -> bool:
    """
    Retrieve the dev mode from the environment variables.
    :return: bool, dev mode
    """
    dev_mode: str | None = os.environ.get('DEV_MODE')
    dev_mode_lower: str = dev_mode.lower()

    if dev_mode_lower not in ['true', 'false']:
        return False
    elif dev_mode_lower == 'true':
        logger.debug('DEVELOPMENT MODE ENABLED')
        return True
    else:
        return False


def get_discord_token(dev_mode: bool) -> str:
    """
    Retrieve the discord token from the environment variables.
    If VAULT_TOKEN is set, it will retrieve the token from the vault.
    :return: str, discord token
    """
    env_var: str | None = 'DEV_DISCORD_TOKEN' if dev_mode else 'DISCORD_TOKEN'

    vault_token: str | None = os.environ.get('VAULT_TOKEN')
    vault_url: str | None = os.environ.get('VAULT_URL')

    if not dev_mode and vault_token and vault_url:
        vault_client = hvac.Client(url=vault_url, token=vault_token, verify=True)
        if vault_client.is_authenticated():
            discord_token = retrieve_vault_secret(
                vault_client=vault_client,
                secret_path='kv',
                secret_name='discord_token'
            )
            if discord_token:
                logger.debug(f'Discord token retrieved from Vault: {discord_token[:10]}...')
                return discord_token

    discord_token: str | None = os.environ.get(env_var)
    if not discord_token:
        raise ValueError(f'{env_var} is not set in the environment variables.')
    logger.debug(f'Discord token retrieved: {discord_token[:10]}...')
    return discord_token


def get_discord_guild_id(dev_mode: bool) -> int:
    """
    Retrieve the discord guild id from the environment variables.
    :return: int, discord guild id
    """
    env_var = 'DEV_DISCORD_GUILD_ID' if dev_mode else 'DISCORD_GUILD_ID'
    discord_guild_id_str: str | None = os.environ.get(env_var)

    if not discord_guild_id_str:
        raise ValueError(f'{env_var} is not set in the environment variables.')

    try:
        discord_guild_id: int | None = int(discord_guild_id_str)
        logger.debug(f'Discord guild id retrieved: {discord_guild_id}')
        return discord_guild_id
    except ValueError:
        raise ValueError(f'{env_var} is not a valid integer.')


def get_discord_channel_id(dev_mode: bool) -> list[int]:
    """
    Retrieve the discord channel id where the bot will send the messages from the environment variables.
    :return: list[str], discord channel id
    """
    env_var: str | None = 'DEV_DISCORD_CHANNEL_ID' if dev_mode else 'DISCORD_CHANNEL_ID'
    discord_channel_id_str: str | None = os.environ.get(env_var)

    if not discord_channel_id_str:
        raise ValueError(f'{env_var} is not set in the environment variables.')

    try:
        discord_channel_ids: list[int] | None = [int(channel_id) for channel_id in discord_channel_id_str.split(',')]
        logger.debug(f'Discord channel ids retrieved: {discord_channel_ids}')
        return discord_channel_ids
    except ValueError:
        raise ValueError(f'{env_var} is not a valid integer.')


def get_organization_name() -> str:
    """
    Retrieve the organization name from the environment variables.
    :return: str, organization name
    """
    organization_name: str | None = os.environ.get('ORGANIZATION_NAME')
    if not organization_name:
        raise ValueError('ORGANIZATION_NAME is not set in the environment variables.')
    logger.debug(f'Organization name retrieved: {organization_name}')
    return organization_name


def get_database_path() -> str:
    """
    Retrieve the database path from the environment variables.
    :return: str, database path
    """
    database_path: str | None = os.environ.get('DATABASE_PATH')
    if not database_path:
        raise ValueError('DATABASE_PATH is not set in the environment variables.')
    logger.debug(f'Database path retrieved: {database_path}')
    return database_path


def get_update_interval() -> int:
    """
    Retrieve the update interval from the environment variables.
    :return: int, update interval
    """
    update_interval_str: str | None = os.environ.get('UPDATE_INTERVAL')
    if not update_interval_str:
        raise ValueError('UPDATE_INTERVAL is not set in the environment variables.')
    try:
        update_interval: int | None = int(update_interval_str)
        logger.debug(f'Update interval retrieved: {update_interval} minutes')
        return update_interval
    except ValueError:
        raise ValueError('UPDATE_INTERVAL is not a valid integer.')


def get_rm_api_key() -> str:
    """
    Retrieve the rm api key from the environment variables.
    If VAULT_TOKEN is set, it will retrieve the token from the vault.
    :return: str, rm api key
    """
    vault_token: str | None = os.environ.get('VAULT_TOKEN')
    vault_url: str | None = os.environ.get('VAULT_URL')

    if vault_token and vault_url:
        vault_client = hvac.Client(url=vault_url, token=vault_token, verify=True)
        if vault_client.is_authenticated():
            rm_api_key = retrieve_vault_secret(
                vault_client=vault_client,
                secret_path='kv',
                secret_name='rootme_token'
            )
            if rm_api_key:
                logger.debug(f'RM API key retrieved from Vault: {rm_api_key[:10]}...')
                return rm_api_key

    rm_api_key: str | None = os.environ.get('RM_API_KEY')
    if not rm_api_key:
        raise ValueError('RM_API_KEY is not set in the environment variables.')

    logger.debug(f'RM API key retrieved: {rm_api_key[:10]}...')
    return rm_api_key
