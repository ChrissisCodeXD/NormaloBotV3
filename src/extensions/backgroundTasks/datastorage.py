import src.main
from src.imports import *
import src

datastorage_plugin = lightbulb.Plugin("backgroundTasks.datastorage")

ttl_cache = TTLCache(maxsize=1000, ttl=600)
logger = logging.getLogger(__name__)


async def guild_already_exists(guild_entry: src.helper.GuildEntry):
    db: src.database.DB = await datastorage_plugin.app.db.getDBHandler("guilds")
    guild_database = (await db.select(guild_id=guild_entry.guild_id))
    return len(guild_database) > 0

async def user_already_exists(user_entry: src.helper.UserEntry):
    db: src.database.DB = await datastorage_plugin.app.db.getDBHandler("users")
    user_database = (await db.select(user_id=user_entry.user_id))
    return len(user_database) > 0

@cached(ttl_cache)
async def changed_guild(guild_entry: src.helper.GuildEntry) -> bool:
    db: src.database.DB = await datastorage_plugin.app.db.getDBHandler("guilds")
    guild_database = (await db.select(guild_id=guild_entry.guild_id))
    if len(guild_database) == 0:
        return True
    guild_database = guild_database[0]
    guild_entry_database = src.helper.GuildEntry()
    guild_entry_database.guild_id = guild_database[1]
    guild_entry_database.guild_name = guild_database[2]
    guild_entry_database.guild_icon = guild_database[3]
    guild_entry_database.guild_owner_id = guild_database[4]
    guild_entry_database.guild_member_count = guild_database[5]

    return guild_entry != guild_entry_database


@cached(ttl_cache)
async def changed_user(user_entry: src.helper.UserEntry) -> bool:
    db: src.database.DB = await datastorage_plugin.app.db.getDBHandler("users")
    user_database = (await db.select(user_id = user_entry.user_id))
    if len(user_database) == 0:
        return True
    user_database = user_database[0]

    user_entry_database = src.helper.UserEntry()
    user_entry_database.user_id = user_database[1]
    user_entry_database.user_name = user_database[2]
    user_entry_database.user_discriminator = user_database[3]
    user_entry_database.user_avatar = user_database[4]
    user_entry_database.user_bot = False if user_database[5] == 0 else True
    toret = user_entry_database != user_entry

    return toret

@tasks.task(m=5, auto_start=True)
async def store_data():
    bot: src.main.NormaloBot = datastorage_plugin.app
    db: src.database.DB = await bot.db.getDBHandler("users")
    db_guild: src.database.DB = await bot.db.getDBHandler("guilds")

    guilds = bot.rest.fetch_my_guilds()
    print(".")
    async for guild in guilds:
        guild: hikari.RESTGuild = await guild.fetch_self()
        if guild is None:
            continue
        guild_entry = src.helper.GuildEntry()
        guild_entry.guild_id = int(guild.id)
        guild_entry.guild_name = str(guild.name)
        guild_entry.guild_icon = str(guild.make_icon_url())
        guild_entry.guild_owner_id = int(guild.owner_id)
        guild_entry.guild_member_count = int(guild.approximate_member_count)

        changed = await changed_guild(guild_entry)
        if changed:
            logger.info(f"Guild {guild_entry.guild_name} changed")
            if await guild_already_exists(guild_entry):
                await db_guild.update(
                    where_clause=[f"guild_id = {guild_entry.guild_id}"],
                    guild_id=guild_entry.guild_id,
                    guild_name=guild_entry.guild_name,
                    guild_icon=guild_entry.guild_icon,
                    guild_owner_id=guild_entry.guild_owner_id,
                    guild_member_count=guild_entry.guild_member_count
                )
            else:
                await db_guild.insert(
                    guild_id=guild_entry.guild_id,
                    guild_name=guild_entry.guild_name,
                    guild_icon=guild_entry.guild_icon,
                    guild_owner_id=guild_entry.guild_owner_id,
                    guild_member_count=guild_entry.guild_member_count
                )

        for i in guild.get_members():
            member: hikari.Member = bot.cache.get_member(guild.id, i)
            if member is None:
                continue
            user = src.helper.UserEntry()
            user.user_id = int(member.id)
            user.user_name = str(member.username)
            user.user_discriminator = str(member.discriminator)
            user.user_avatar = str(member.make_avatar_url())
            user.user_bot = bool(member.is_bot)
            changed = await changed_user(user)
            if changed:
                print(f"User {user.user_name}#{user.user_discriminator} changed")
                bot.log.info(f"User {user.user_name}#{user.user_discriminator} changed")
                if await user_already_exists(user):
                    await db.update(
                        where_clause=[f"user_id = {user.user_id}"],
                        user_id=user.user_id,
                        user_name=user.user_name,
                        user_discriminator=user.user_discriminator,
                        user_avatar=user.user_avatar,
                        user_bot=user.user_bot
                    )
                else:
                    await db.insert(
                        user_id=user.user_id,
                        user_name=user.user_name,
                        user_discriminator=user.user_discriminator,
                        user_avatar=user.user_avatar,
                        user_bot=user.user_bot
                    )




def load(bot):
    bot.add_plugin(datastorage_plugin)


def unload(bot):
    bot.remove_plugin(datastorage_plugin)
