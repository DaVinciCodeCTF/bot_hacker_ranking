from database.crud_data import update_data
from database.crud_user import get_active_users, deactivate_user, get_deactivated_users, activate_user, delete_user, \
    update_user
from database.models import User, DailyUserData
from utils.api import get_htb_data, get_rm_data, get_thm_data


async def update_daily_data(user: User) -> DailyUserData:
    """
    Update the daily datas of a user by fetching it from the APIs
    :param user: User, user to update
    :return: DailyUserData, updated daily data
    """
    if not any([user.htb_id, user.rm_id, user.thm_id]):
        return user

    daily_data: dict = {}
    user_ids: dict = {'htb': user.htb_id, 'rm': user.rm_id, 'thm': user.thm_id}
    data_fetchers: dict = {'htb': get_htb_data, 'rm': get_rm_data, 'thm': get_thm_data}

    for platform, user_id in user_ids.items():
        if user_id:
            daily_data.update(await data_fetchers[platform](user_id))
            if platform == 'rm':
                user_data: dict = {'rm_name': daily_data.pop('rm_name')}
                update_user(user, user_data)

    return update_data(user.discord_id, daily_data)


async def update_all_daily_data(members_id: list[int], dev_mode: bool) -> None:
    """
    Update the daily datas of all users
    :return: None
    """
    users: list[User] = get_active_users()

    if not dev_mode:
        # Remove users with no ids
        for user in users:
            if not any([user.htb_id, user.rm_id, user.thm_id]):
                users.remove(user)
                delete_user(user)
        # Remove users that are not in the server anymore
        for user in users:
            if user.discord_id not in members_id:
                users.remove(user)
                deactivate_user(user)
        # Check if deactivated users are back in the server
        users_deactivated: list[User] = get_deactivated_users()
        for user in users_deactivated:
            if user.discord_id in members_id:
                users.append(user)
                activate_user(user)

    for user in users:
        await update_daily_data(user)
