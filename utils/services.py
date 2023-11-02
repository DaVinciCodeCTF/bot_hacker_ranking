from database.crud_data import update_data
from database.crud_user import get_all_users
from database.models import User, DailyUserData
from utils.api import get_htb_data, get_rm_data, get_thm_data


async def update_daily_data(user: User) -> DailyUserData:
    """
    Update the daily datas of a user by fetching it from the APIs
    :param user: User, user to update
    :return: DailyUserData, updated daily data
    """
    if user.htb_id is None and user.rm_id is None and user.thm_id is None:
        return user
    daily_data: dict = {}
    if user.htb_id:
        htb_data: dict = await get_htb_data(user.htb_id)
        daily_data.update(htb_data)
    if user.rm_id:
        rm_data: dict = await get_rm_data(user.rm_id)
        daily_data.update(rm_data)
    if user.thm_id:
        thm_data: dict = await get_thm_data(user.thm_id)
        daily_data.update(thm_data)
    return update_data(user.discord_id, daily_data)


async def update_all_daily_data() -> None:
    """
    Update the daily datas of all users
    :return: None
    """
    users: list[User] = get_all_users()
    for user in users:
        await update_daily_data(user)
