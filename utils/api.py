import asyncio
import logging
import os

from dotenv import load_dotenv
from requests import get, Response, RequestException

logger = logging.getLogger(__name__)
load_dotenv()

HTB_API: str = 'https://www.hackthebox.com/api/v4/profile/'
RM_API: str = 'https://api.www.root-me.org/auteurs/'
THM_API: str = 'https://tryhackme.com/api/'
RM_API_KEY: str = os.getenv('RM_API_KEY')
SLEEP_API_REQUEST: float = 0.2
HEADERS: dict = {'User-Agent': 'HackerRanker/1.0'}


async def get_htb_data(htb_id: int) -> dict:
    """
    Get the HackTheBox data of a user
    https://documenter.getpostman.com/view/13129365/TVeqbmeq#a52f369b-eeca-4271-b50c-bc6b00ff0469
    :param htb_id: int, HackTheBox user ID
    :return: dict, HackTheBox data {'htb_rank': int, 'htb_score': int}
    """
    try:
        response: Response = get(HTB_API + str(htb_id), headers=HEADERS)
        await asyncio.sleep(SLEEP_API_REQUEST)
        response.raise_for_status()
        data = response.json()
        if 'profile' not in data:
            logger.warning(f'Couldn\'t get HTB data for {htb_id}. Error: {data}')
            return {}
        else:
            htb_rank: int = int(data['profile']['ranking']) if data['profile']['ranking'] else 0
            htb_score: int = int(data['profile']['points'])
            logger.debug(f'HTB data retrieved for {htb_id}: {htb_rank}, {htb_score}')
            return {'htb_rank': htb_rank, 'htb_score': htb_score}
    except RequestException as e:
        logger.warning(f'Couldn\'t get HTB data for {htb_id}. Error: {e}')
        return {}


async def get_rm_data(rm_id: int, rm_name_check: bool = False) -> dict:
    """
    Get the RootMe data of a user
    https://www.root-me.org/fr/breve/API-api-www-root-me-org
    :param rm_id: int, RootMe user ID
    :param rm_name_check: bool, check if the RootMe is unique
    :return: dict, RootMe data {'rm_rank': int, 'rm_score': int}
    """
    try:
        rm_data: dict = {}
        cookies: dict = {'api_key': RM_API_KEY}
        response: Response = get(RM_API + str(rm_id), headers=HEADERS, cookies=cookies)
        await asyncio.sleep(SLEEP_API_REQUEST)
        data = response.json()
        if 'score' not in data:
            logger.warning(f'Couldn\'t get RM data for {rm_id}. Error: {data}')
            return {}
        else:
            rm_data['rm_rank']: int = int(data['position']) if data['position'] else 0
            rm_data['rm_score']: int = int(data['score'])
            if rm_name_check:
                rm_name: str = data['nom'] + '-' + str(rm_id)
                response: Response = get(f'https://www.root-me.org/{rm_name}', headers=HEADERS, cookies=cookies)
                if response.status_code == 404:
                    rm_name: str = rm_name.split('-')[0]
                rm_data['rm_name']: str = rm_name
            logger.debug(f'RM data retrieved for {rm_id}: {rm_data["rm_rank"]}, {rm_data["rm_score"]}')
            return rm_data
    except RequestException as e:
        logger.warning(f'Couldn\'t get RM score for {rm_id}. Error: {e}')
        return {}


async def get_thm_data(thm_id: str) -> dict:
    """
    Get the TryHackMe data of a user
    https://www.postman.com/gnarlito/workspace/tryhackme-doc/documentation/18269560-b1c3d2f3-f378-4291-9025-1a9fa88a24e0
    :param thm_id: str, TryHackMe user ID
    :return: dict, TryHackMe data {'thm_rank': int, 'thm_rooms': int}
    """
    try:
        response: Response = get(THM_API + 'user/rank/' + thm_id, headers=HEADERS)
        await asyncio.sleep(SLEEP_API_REQUEST)
        response.raise_for_status()
        data_rank = response.json()
        response: Response = get(THM_API + 'no-completed-rooms-public/' + thm_id, headers=HEADERS)
        await asyncio.sleep(SLEEP_API_REQUEST)
        response.raise_for_status()
        data_rooms = response.json()
        if 'userRank' not in data_rank or int(data_rooms) == 0:
            logger.warning(f'Couldn\'t get THM data for {thm_id}. Error: {data_rank} {data_rooms}')
            return {}
        else:
            thm_rank: int = int(data_rank['userRank'])
            thm_rooms: int = int(data_rooms)
            logger.debug(f'THM data retrieved for {thm_id}: {thm_rank}, {thm_rooms}')
            return {'thm_rank': thm_rank, 'thm_rooms': thm_rooms}
    except RequestException as e:
        logger.warning(f'Couldn\'t get THM data for {thm_id}. Error: {e}')
        return {}
