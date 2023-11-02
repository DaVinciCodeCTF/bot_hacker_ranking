import logging

from sqlalchemy.exc import SQLAlchemyError

from database.manager import DatabaseManager
from database.models import User

logger = logging.getLogger(__name__)
SessionLocal = DatabaseManager.get_session_local


def insert_user(user_data: dict) -> User:
    """
    Insert a new user in the database
    :param user_data: dict, data of the user to insert
    :return: User, the inserted user
    """
    with SessionLocal() as db:
        user: User = User(**user_data)
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f'User {user.username} inserted successfully in the database.')
        except SQLAlchemyError:
            db.rollback()
            raise
    return user


def get_user(**kwargs) -> User:
    """
    Retrieve a user from the database based on the given filters
    :param kwargs: Keyword arguments, accepts either discord_id or username
    :return: User, the user
    """
    with SessionLocal() as db:
        filters: list = []
        if 'discord_id' in kwargs:
            filters.append(User.discord_id == kwargs['discord_id'])
        if 'username' in kwargs:
            filters.append(User.username == kwargs['username'])

        if not filters:
            raise ValueError('No valid filter given')

        user: User = db.query(User).filter(*filters).first()
        logger.debug(f'User retrieved from the database: {user}')

    return user


def get_all_users() -> list[User]:
    """
    Retrieve all users from the database
    :return: list[User], all users
    """
    with SessionLocal() as db:
        users = db.query(User).all()
        logger.debug(f'All users retrieved from the database: {len(users)}')
    return users


def update_user(user: User, user_data: dict) -> User:
    """
    Update a user in the database.
    :param user: User, the user to update
    :param user_data: dict, data to update
    :return: User, the updated user
    """
    with SessionLocal() as db:
        try:
            db_user = db.query(User).filter(User.discord_id == user.discord_id).first()
            if not db_user:
                raise ValueError('User not found')

            for key, value in user_data.items():
                setattr(db_user, key, value)

            db.commit()
            db.refresh(db_user)
            logger.info(f'User {db_user.username} updated successfully in the database.')
        except SQLAlchemyError:
            db.rollback()
            raise
    return db_user
