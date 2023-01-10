import logging
import src
from src.imports import *
from src.helper import PermissionCache

log = logging.getLogger(__name__)
_BotT = t.TypeVar("_BotT", bound="Bot")


class Prefixes:

    def __init__(self, bot):
        self.bot = bot
        self.prefixes = {}
        self.conn = mysql.connector.connect(host=bot.env.get('database_host'), port=3306,
                                            user=bot.env.get('database_user'),
                                            password=bot.env.get('database_password'),
                                            db='s67_NormaloBotTest',
                                            # ssl_ca="D:\\Benutzer\\Dokumente\\python\\normaloBotV3\\src\\data\\cacert-2022-10-11.pem"
                                            )
        self.prefixes = self.get_all_prefixes()

    def select(self, conn, query):
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def insert(self, conn, table, **kwargs):
        # Build the INSERT statement
        keys = ', '.join(kwargs.keys())
        values = ', '.join(['%s'] * len(kwargs))
        stmt = f"INSERT INTO {table} ({keys}) VALUES ({values})"

        # Execute the INSERT statement
        with conn.cursor() as cursor:
            cursor.execute(stmt, list(kwargs.values()))
            conn.commit()

    def update(self, conn, table, where_clause, **kwargs):
        # Build the SET clause of the UPDATE statement
        set_clause = ', '.join([f"{key} = %s" for key in kwargs.keys()])
        stmt = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

        # Execute the UPDATE statement
        with conn.cursor() as cursor:
            cursor.execute(stmt, list(kwargs.values()))
            conn.commit()

    def get_prefix_for_guild(self, guildid: int):
        toret = {}
        result = self.select(self.conn, f'SELECT * FROM prefixes WHERE guild_id = {guildid}')
        for id, guild_id, prefix in result:
            toret[str(guild_id)] = prefix
        return toret

    def get_all_prefixes(self):
        toret = {}
        result = self.select(self.conn, f'SELECT * FROM prefixes')
        for id, guild_id, prefix in result:
            toret[str(guild_id)] = prefix
        return toret

    def get_prefix(self, guild_id):
        if str(guild_id) not in self.prefixes:
            result = self.get_all_prefixes()
            if str(guild_id) not in result:
                result[str(guild_id)] = "!"
                self.insert(self.conn, 'prefixes', guild_id=guild_id, prefix="!")
            self.prefixes = result
        return self.prefixes.get(str(guild_id))

    def get_prefixes(self, bot, msg):
        return self.get_prefix(msg.guild_id)

    def change_prefix(self, guild_id, prefix):
        result = self.get_prefix_for_guild(guild_id)
        if len(result) == 0:
            self.insert(self.conn, 'prefixes', guild_id=guild_id, prefix=prefix)
        else:
            self.update(self.conn, 'prefixes', f"guild_id = {guild_id}", prefix=prefix)
        result = self.get_all_prefixes()
        self.prefixes = result


class NormaloBot(lightbulb.BotApp):
    def __init__(self):
        self.log = log
        self.db = src.database.PoolManager()
        self.env = src.helper.Env()
        self._prefix__get_class = Prefixes(self)
        self._extensions = self.search_all_extensions()
        self.token = token = self.env.get('TOKEN1')
        self.perm_cache = PermissionCache(1000, self.db)
        if src.__beta__:

            super().__init__(
                token=token,
                intents=hikari.Intents.ALL,
                prefix=lightbulb.app.when_mentioned_or("!"),  # self._prefix__get_class.get_prefixes
                default_enabled_guilds=src.__guilds__,
                help_class=src.helper.HelpCommand,
                help_slash_command=True,
                ignore_bots=True,
                case_insensitive_prefix_commands=True,
                owner_ids=[589898942527963157],
                logs={
                    "version": 1,
                    "incremental": True,
                    "loggers": {
                        "hikari": {"level": "INFO"},
                        "lightbulb": {"level": "INFO"},
                    },
                },
            )
        else:
            super().__init__(
                token=token,
                intents=hikari.Intents.ALL,
                prefix=lightbulb.app.when_mentioned_or("!"),  # self._prefix__get_class.get_prefixes
                ignore_bots=True,
                help_class=src.helper.HelpCommand,
                help_slash_command=True,
                case_insensitive_prefix_commands=True,
                owner_ids=[589898942527963157],
                logs={
                    "version": 1,
                    "incremental": True,
                    "loggers": {
                        "hikari": {"level": "INFO"},
                        "lightbulb": {"level": "INFO"},
                    },
                },
            )

    def run(self: _BotT) -> None:
        self.event_manager.subscribe(hikari.StartingEvent, self.on_starting)
        self.event_manager.subscribe(hikari.StartedEvent, self.on_started)
        self.event_manager.subscribe(hikari.StoppingEvent, self.on_stopping)
        self.event_manager.subscribe(hikari.VoiceStateUpdateEvent, self.on_voice_state_update)
        self.event_manager.subscribe(hikari.VoiceServerUpdateEvent, self.on_voice_server_update)

        super().run(
            activity=hikari.Activity(
                name=f"Version 1.0",
                type=hikari.ActivityType.COMPETING,
            )
        )

    def search_all_extensions(self, startpath: str = "./extensions/") -> list:
        extensions = []
        for p in Path(startpath).iterdir():
            p: Path
            if p.is_file() and p.suffix == ".py":
                extension_name = ""
                for part in p.parts:
                    if part == "extensions":
                        continue
                    if part == p.name:
                        extension_name += part[:-3]
                        continue
                    extension_name += f"{part}."
                extensions.append(extension_name)
            elif p.is_dir():
                extensions.extend(self.search_all_extensions(str(p)))
        return extensions

    async def on_starting(self: _BotT, event: hikari.StartingEvent) -> None:

        for ext in self._extensions:
            self.load_extensions(f"src.extensions.{ext}")
            log.info(f"'{ext}' extension loaded")

        await self.db.create()

        cache = sake.redis.RedisCache(
            app=self,
            event_manager=self.event_manager,
            address=self.env.get("REDIS_ADDRESS"),
            password=self.env.get("REDIS_PASSWORD"),
        )
        await cache.open()

    async def on_started(self: _BotT, event: lightbulb.LightbulbStartedEvent) -> None:
        """builder = (
            lavasnek_rs.LavalinkBuilder(int(b64decode(self.token.split(".")[0])), self.token)
            .set_host("127.0.0.1")
        )

        builder.set_start_gateway(False)
        self.lavalink = await builder.build(EventHandler())
        log.info("Created Lavalink instance")

        # self.stdout_channel = await self.rest.fetch_channel(STDOUT_CHANNEL_ID)
        # await self.stdout_channel.send(f"Testing v{__version__} now online!")"""

    async def on_stopping(self: _BotT, event: hikari.StoppingEvent) -> None:
        # This is gonna be fixed.
        # await self.stdout_channel.send(f"Testing v{__version__} is shutting down.")
        ...

    async def on_voice_state_update(self, event: hikari.VoiceStateUpdateEvent) -> None:
        return

    async def on_voice_server_update(self, event: hikari.VoiceServerUpdateEvent) -> None:
        return
