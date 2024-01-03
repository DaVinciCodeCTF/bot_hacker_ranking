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
        if not user and 'username' in kwargs:
            logger.info(f'User @{kwargs["username"]} not found in the database.')
        elif not user and 'discord_id' in kwargs:
            logger.info(f'User #{kwargs["discord_id"]} not found in the database.')

    return user


def get_active_users() -> list[User]:
    """
    Retrieve active users from the database
    :return: list[User], all users
    """
    with SessionLocal() as db:
        users = db.query(User).filter(User.active == 1).all()
        logger.debug(f'Active users retrieved from the database: {len(users)}')
    return users


def get_deactivated_users() -> list[User]:
    """
    Retrieve deactivated users from the database
    :return: list[User], all users
    """
    with SessionLocal() as db:
        users = db.query(User).filter(User.active == 0).all()
        logger.debug(f'Deactivated users retrieved from the database: {len(users)}')
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


def deactivate_user(user: User) -> User:
    """
    Deactivate a user in the database.
    :param user: User, the user to deactivate
    :return: User, the deactivated user
    """
    with SessionLocal() as db:
        try:
            db_user = db.query(User).filter(User.discord_id == user.discord_id).first()
            if not db_user:
                raise ValueError('User not found')

            db_user.active = False
            db.commit()
            db.refresh(db_user)
            logger.info(f'User {db_user.username} deactivated successfully in the database.')
        except SQLAlchemyError:
            db.rollback()
            raise
    return db_user


def activate_user(user: User) -> User:
    """
    Activate a user in the database.
    :param user: User, the user to activate
    :return: User, the activated user
    """
    with SessionLocal() as db:
        try:
            db_user = db.query(User).filter(User.discord_id == user.discord_id).first()
            if not db_user:
                raise ValueError('User not found')

            db_user.active = True
            db.commit()
            db.refresh(db_user)
            logger.info(f'User {db_user.username} activated successfully in the database.')
        except SQLAlchemyError:
            db.rollback()
            raise
    return db_user


def delete_user(user: User) -> None:
    """
    Delete a user in the database.
    :param user: User, the user to delete
    :return: None
    """
    with SessionLocal() as db:
        try:
            db_user = db.query(User).filter(User.discord_id == user.discord_id).first()
            if not db_user:
                raise ValueError('User not found')

            db.delete(db_user)
            db.commit()
            logger.info(f'User {db_user.username} deleted successfully from the database.')
        except SQLAlchemyError:
            db.rollback()
            raise
