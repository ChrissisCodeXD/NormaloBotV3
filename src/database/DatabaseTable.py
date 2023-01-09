import sqlalchemy.engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BIGINT, BOOLEAN
from sqlalchemy.dialects.mysql import LONGTEXT
import logging

logger = logging.getLogger(__name__)
Base = declarative_base()


class DatabaseTable(Base):
    __abstract__ = True

    def check_table_exists(self):
        table = self.__table__
        return self.__table__.exists(bind=self.__table__.metadata.bind)


class PrefixesTable(DatabaseTable):
    __tablename__ = "prefixes"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BIGINT)
    prefix = Column(String(20))


class UsersTable(DatabaseTable):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(BIGINT)
    user_name = Column(String(200))
    user_discriminator = Column(String(200))
    user_avatar = Column(String(200))
    user_banner = Column(String(200))
    user_bot = Column(BOOLEAN)


class GuildsTable(DatabaseTable):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BIGINT)
    guild_name = Column(String(200))
    guild_icon = Column(String(200))
    guild_owner_id = Column(BIGINT)
    guild_member_count = Column(BIGINT)

class PermissionsTable(DatabaseTable):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    guild_id = Column(BIGINT)
    command = Column(String(200))
    type = Column(String(200))
    permission = Column(LONGTEXT)


def create_all(engine: sqlalchemy.engine.Engine):
    logger.info("Created all tables")
    Base.metadata.create_all(bind=engine)
