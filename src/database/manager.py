import asyncio
import aiomysql
import sqlalchemy.engine
import ssl
import src
from sqlalchemy import create_engine



class DB:

    def __init__(self, tablename: str, pool: aiomysql.Pool):
        self.__table: str = tablename
        self.env: src.helper.Env = src.helper.Env()
        self.pool: aiomysql.Pool = pool

    async def select(self, *args, **kwargs) -> list:
        attribute = kwargs.get("attribute", "*")
        query = f"SELECT {attribute} FROM {self.__table}"
        for _, condition in enumerate(args):
            query += f" {condition}"
            if len(args) - 1 != _:
                query += " AND"
        query += ";"
        pool: aiomysql.Pool = self.pool

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                if kwargs.get("amount"):
                    r = await cur.fetchmany(kwargs.get("amount"))
                else:
                    r = await cur.fetchall()
        return r

    async def insert(self, **kwargs) -> None:
        query = f"INSERT INTO {self.__table} ({', '.join([i for i in kwargs])}) VALUES ({', '.join([kwargs[i] for i in kwargs])});"
        pool: aiomysql.Pool = self.pool

        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                conn.commit()

    async def update(self, where_clause: list = [], **kwargs) -> None:
        query = f"UPDATE {self.__table} SET {', '.join([f'{i} = {kwargs[i]}' for i in kwargs])}"
        if len(where_clause):
            query += " WHERE"
        for _, i in enumerate(where_clause):
            query += f" {i}"
            if len(where_clause) - 1 != _:
                query += " AND"
        query += ";"

        pool: aiomysql.Pool = self.pool
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query)
                conn.commit()


class PoolManager:

    def __init__(self):
        #.ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        #self.ctx.load_verify_locations(
        #    cafile="D:\\Benutzer\\Dokumente\\python\\normaloBotV3\\src\\data\\cacert-2022-10-11.pem")
        self.env: src.helper.Env = src.helper.Env()
        self.host = self.env.get("database_host")
        self.user = self.env.get("database_user")
        self.password = self.env.get("database_password")
        self.databasename = "s67_NormaloBotTest"
        self.pool: aiomysql.Pool = None
        self.__first_init = True
        self.engine: sqlalchemy.engine.Engine = None

    def __del__(self):
        if self.pool:
            self.pool.terminate()

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()

    def terminate(self):
        if self.pool:
            self.pool.terminate()

    def __create_engine(self):
        database_url = f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:3306/{self.databasename}"#?ssl_ca=D:\\Benutzer\\Dokumente\\python\\normaloBotV3\\src\\data\\cacert-2022-10-11.pem"
        self.engine = create_engine(database_url)

    def get_engine(self):
        if not self.engine:
            self.__create_engine()
        return self.engine

    async def create(self):
        loop = asyncio.get_event_loop()

        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
            pool = None
            self.__first_init = False
        if self.__first_init:
            print("first init")
            eng = self.get_engine()
            src.database.create_all(eng)
        pool = await aiomysql.create_pool(host=self.host, port=3306,
                                          user=self.user,
                                          password=self.password,
                                          db=self.databasename, loop=loop,
                                          #ssl=self.ctx
                                          )

        self.pool = pool

    async def getDBHandler(self, tablename: str) -> DB:
        if not self.pool:
            await self.create()

        return DB(tablename, self.pool)
