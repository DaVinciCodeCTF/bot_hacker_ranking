import logging

import sqlalchemy
from sqlalchemy import create_engine, exc
from sqlalchemy.engine import reflection
from sqlalchemy.orm import sessionmaker

from database.models import Base, User

logger = logging.getLogger(__name__)


class DatabaseManager:
    _instance = None
    _session_local = None
    _engine = None

    def __new__(cls, database_path: str = None):
        """
        Singleton pattern, only one instance of DatabaseManager can exist at a time
        :param database_path: str, path to the database
        """
        if cls._instance is None:
            if database_path is None:
                raise ValueError("Database path must be provided for the first instantiation of DatabaseManager")
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._initialize(database_path)
        return cls._instance

    @classmethod
    def _initialize(cls, database_path: str) -> None:
        """
        Initialize the database with the given path
        :param database_path: str, path to the database
        :return: None
        """
        database_url: str = f'sqlite:///{database_path}'
        cls._engine = create_engine(database_url)
        cls._session_local = sessionmaker(bind=cls._engine)
        Base.metadata.create_all(bind=cls._engine)
        logger.info('Database initialized successfully.')

    @classmethod
    def get_session_local(cls) -> sqlalchemy.orm.session.sessionmaker:
        """
        Get the session local, used to interact with the database
        :return: sqlalchemy.orm.session.sessionmaker, the session local
        """
        if cls._session_local is None:
            raise ValueError("DatabaseManager has not been initialized with a database path")
        return cls._session_local()

    @classmethod
    def create_database(cls) -> None:
        """
        Create the database if it does not exist, and create the tables
        :return: None
        """
        try:
            inspector = reflection.Inspector.from_engine(cls._engine)
            existing_tables = inspector.get_table_names()
            Base.metadata.create_all(bind=cls._engine)
            new_tables = inspector.get_table_names()
            created_tables = set(new_tables) - set(existing_tables)
            if created_tables:
                logger.info(f'Database created successfully. Tables created: {", ".join(created_tables)}')
            else:
                logger.debug('Database already exists. No tables were created.')

        except exc.SQLAlchemyError as e:
            logger.error(f'An error occurred while creating the database: {str(e)}')

    @classmethod
    def reset_database(cls) -> None:
        """
        Reset the database, drop all tables and create them again
        WARNING: All data will be lost
        :return: None
        """
        try:
            Base.metadata.drop_all(bind=cls._engine)
            Base.metadata.create_all(bind=cls._engine)
            logger.warning('Database reset successfully. All data has been deleted.')
        except exc.SQLAlchemyError as e:
            logger.error(f'An error occurred while resetting the database: {str(e)}')

    @classmethod
    def fill_database(cls) -> None:
        """
        Fill the database with some data, for testing purposes
        :return: None
        """
        users_data_str: str = """
        discord_id,username,birthday,htb_id,rm_id,thm_id
        """

        users_to_add: list = []
        for user_data in users_data_str.strip().split('\n'):
            discord_id, username,birthday, htb_id, rm_id, thm_id = user_data.split(',')

            user_dict = {
                'discord_id': discord_id,
                'username': username,
                'birthday': birthday if birthday != '""' else None,
                'htb_id': htb_id if htb_id != '""' else None,
                'rm_id': rm_id if rm_id != '""' else None,
                'thm_id': thm_id if thm_id != '""' else None
            }
            users_to_add.append(user_dict)

        with cls._session_local() as db:
            for user in users_to_add:
                db.add(User(**user))
            db.commit()
        logger.info(f'{len(users_to_add)} users added to the database.')