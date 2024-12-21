import logging
from datetime import datetime, timedelta

from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from database.crud_user import get_user, get_active_users
from database.manager import DatabaseManager
from database.models import DailyUserData

SessionLocal = DatabaseManager.get_session_local
logger = logging.getLogger(__name__)


def get_data(discord_id: int, date: datetime.date = datetime.now().date()) -> DailyUserData:
    """
    Get the daily data of a user, date is set to today by default
    :param discord_id: int, discord id of the user
    :param date: datetime.date, date of the data to get
    :return: DailyUserData, daily data of the user
    """
    with SessionLocal() as db:
        daily_user = db.query(DailyUserData).filter_by(discord_id=discord_id, date=date).first()
    return daily_user


def get_data_organization_leaderboard(platform: str, date: datetime.date = datetime.now().date()) -> list[dict]:
    """
    Get the daily leaderboard of the organization members
    Date is set to today by default and users are sorted by their score on the given platform
    :param platform: str, platform to get the ranking from
    :param date: datetime.date, date of the data to get
    :return: list[dict], daily leaderboard of the organization members
    """
    score_key = f'{platform}_score' if platform in ['htb', 'rm'] else f'{platform}_rooms'
    with SessionLocal() as db:
        profiles_ids: dict = {
            user.discord_id: getattr(user, f'{platform}_id' if platform in ['htb', 'thm'] else f'{platform}_name')
            for user in get_active_users()
        }

        discord_ids_list: list[int] = list(profiles_ids.keys())

        organization_leaderboard_raw = (
            db.query(DailyUserData)
            .filter(and_(DailyUserData.date == date, DailyUserData.discord_id.in_(discord_ids_list)))
            .order_by(getattr(DailyUserData, score_key).desc())
            .all()
        )

        organization_leaderboard: list[dict] = [
            {
                'username': get_user(discord_id=user.discord_id).username,
                'platform_rank': index + 1,
                'platform_score': getattr(user, score_key),
                'platform_global_rank': getattr(user, f'{platform}_rank'),
                'score_evolution': _calculate_score_evolution(user, score_key, date),
                'platform_id': profiles_ids.get(user.discord_id)
            }
            for index, user in enumerate(organization_leaderboard_raw) if getattr(user, score_key)
        ]

        logger.debug(f'Organization leaderboard retrieved from the database.')
        for user in organization_leaderboard:
            logger.debug(user)

    return organization_leaderboard


def _calculate_score_evolution(user, score_key, date) -> int:
    """
    Helper function to calculate the score evolution for a user.
    :param user: DailyUserData, user to calculate the score evolution from
    :param score_key: str, attribute to get the score from
    :param date: datetime.date, date of the data to get
    :return: int, score evolution
    """
    thirty_days_ago = date - timedelta(days=30)
    old_data = get_data(user.discord_id, thirty_days_ago)
    if not old_data or not getattr(old_data, score_key):
        with SessionLocal() as db:
            old_data = (
                db.query(DailyUserData)
                .filter(
                    DailyUserData.discord_id == user.discord_id,
                    getattr(DailyUserData, score_key) > 0
                )
                .order_by(DailyUserData.date)
                .first()
            )
    if old_data:
        old_score = getattr(old_data, score_key)
        return getattr(user, score_key) - old_score
    return 0


def get_platform_rank(discord_id: int, date: datetime.date, score_attr: str) -> int:
    """
    Helper function to get the rank for a specific platform.
    :param discord_id: int, discord id of the user
    :param date: datetime.date, date of the data to get
    :param score_attr: str, attribute to get the score from
    :return: int, rank of the user
    """
    with SessionLocal() as db:
        leaderboard = (
            db.query(DailyUserData)
            .filter_by(date=date)
            .filter(getattr(DailyUserData, score_attr) > 0)
            .order_by(getattr(DailyUserData, score_attr).desc())
            .all()
        )
        logger.debug(f'Rank retrieved from the database: {leaderboard}')
    return next((index + 1 for index, user in enumerate(leaderboard) if user.discord_id == discord_id), None)


def get_organization_rank(discord_id: int, date: datetime.date = datetime.now().date()) -> dict:
    """
    Get the daily rank of a user on HackTheBox, RootMe and TryHackMe.
    :param discord_id: int, discord id of the user
    :param date: datetime.date, date of the data to get
    :return: dict, daily rank of the user on HackTheBox, RootMe and TryHackMe
    """
    return {
        'htb_orga_rank': get_platform_rank(discord_id, date, 'htb_score'),
        'rm_orga_rank': get_platform_rank(discord_id, date, 'rm_score'),
        'thm_orga_rank': get_platform_rank(discord_id, date, 'thm_rooms')
    }


def update_data(discord_id: int, daily_data: dict) -> DailyUserData:
    """
    Update the daily data of a user or create it if it doesn't exist
    It will look for the user's data of the current day
    :param discord_id: int, discord id of the user
    :param daily_data: dict, data to update
    :return: DailyUserData, updated daily data
    """
    with SessionLocal() as db:
        daily_user = db.query(DailyUserData).filter_by(discord_id=discord_id, date=datetime.now().date()).first()
        if not daily_user:
            daily_user = DailyUserData(discord_id=discord_id, date=datetime.now().date(), **daily_data)
            db.add(daily_user)
        else:
            for key, value in daily_data.items():
                setattr(daily_user, key, value)
        try:
            db.commit()
            db.refresh(daily_user)
            logger.info(f'Daily data for {discord_id} inserted successfully in the database.')
        except SQLAlchemyError:
            db.rollback()
            raise
    return daily_user
