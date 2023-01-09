import hikari

import src.database
from src.imports import *

ban_plugin = lightbulb.Plugin("test.test")

ban_plugin.add_checks(
    lightbulb.checks.guild_only,
    lightbulb.checks.bot_has_guild_permissions(hikari.Permissions.BAN_MEMBERS),
    lightbulb.checks.has_guild_permissions(hikari.Permissions.BAN_MEMBERS),
)


@ban_plugin.listener(hikari.StartedEvent)
async def foo(event: hikari.StartedEvent):
    db: src.database.PoolManager = event.app.db
    #await db.create()
    pass
    #print("super")
    #db = await event.app.db.getDBHandler("prefixes")
    #await db.select()

def load(bot):
    bot.add_plugin(ban_plugin)


def unload(bot):
    bot.remove_plugin(ban_plugin)