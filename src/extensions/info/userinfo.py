from src.imports import *
import src

userinfo_plugin = lightbulb.Plugin("info.userinfo")
userinfo_plugin.add_checks(
    lightbulb.checks.guild_only,
    lightbulb.checks.bot_has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES),
    lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_MESSAGES),
)


@userinfo_plugin.command()
@lightbulb.check_exempt(src.helper.mod_check)
@lightbulb.option("user", "User to delete messages from", hikari.Member, required=False)
@lightbulb.command("userinfo", "Clears the Current Channel")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def userinfo(ctx: lightbulb.Context) -> None:
    await ctx.respond(f"Hi!", flags=hikari.MessageFlag.EPHEMERAL)


def load(bot):
    bot.add_plugin(userinfo_plugin)


def unload(bot):
    bot.remove_plugin(userinfo_plugin)
