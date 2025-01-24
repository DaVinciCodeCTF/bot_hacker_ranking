from sqlalchemy import Column, Integer, String, Date, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

USERS_TABLE = 'users'
DAILY_USER_DATA_TABLE = 'daily_user_data'


class User(Base):
    """
    User model for the database.
    Used to store the user's data needed for ranking.
    """
    __tablename__ = USERS_TABLE

    discord_id: int = Column(Integer, primary_key=True, index=True, comment='Discord ID of the user')
    username: str = Column(String, index=True, comment='Username of the user visible on the leaderboard')
    active: bool = Column(Integer, default=True, comment='Whether the user is active or not')
    birthday: Date = Column(Date, comment='Birthday of the user')

    # External platform IDs
    htb_id: int = Column(Integer, comment='HackTheBox UID of the user, visible on https://app.hackthebox.com/profile/')
    rm_id: int = Column(Integer, comment='RootMe UID of the user, visible on https://www.root-me.org/user')
    rm_name: str = Column(String, comment='RootMe username of the user, visible on https://www.root-me.org/user')
    thm_id: str = Column(String, comment='TryHackMe username of the user, visible on https://tryhackme.com/profile')

    def __repr__(self):
        return (f'<User(username={self.username}, discord_id={self.discord_id}, birthday={self.birthday},'
                f' htb_id={self.htb_id}, rm_id={self.rm_id}, thm_id={self.thm_id})>')


class DailyUserData(Base):
    """
    DailyUserData model for the database.
    Used to store the daily ranking & score of a user.
    """
    __tablename__ = DAILY_USER_DATA_TABLE

    date: Date = Column(Date, nullable=False, comment='Date of the data entry')
    discord_id: int = Column(Integer, nullable=False, comment='Discord ID of the user')

    # Platform rankings and scores
    htb_rank: int = Column(Integer, comment="User's rank on HackTheBox for the given date")
    htb_score: int = Column(Integer, comment="User's score on HackTheBox for the given date")
    rm_rank: int = Column(Integer, comment="User's rank on RootMe for the given date")
    rm_score: int = Column(Integer, comment="User's score on RootMe for the given date")
    thm_rank: int = Column(Integer, comment="User's rank on TryHackMe for the given date")
    thm_rooms: int = Column(Integer, comment="Number of rooms completed by the user on TryHackMe for the given date")

    __table_args__ = (PrimaryKeyConstraint('date', 'discord_id'),)

    def __repr__(self):
        return (f'<DailyUserData(date={self.date}, discord_id={self.discord_id},'
                f' htb_rank={self.htb_rank}, htb_score={self.htb_score},'
                f' rm_rank={self.rm_rank}, rm_score={self.rm_score}'
                f' thm_rank={self.thm_rank}, thm_rooms={self.thm_rooms})>')