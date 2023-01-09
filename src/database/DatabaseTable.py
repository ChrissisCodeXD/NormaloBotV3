import sqlalchemy.engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BIGINT
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

def create_all(engine: sqlalchemy.engine.Engine):
    print("Create all")
    Base.metadata.create_all(bind=engine)
