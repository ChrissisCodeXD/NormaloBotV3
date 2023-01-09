import hikari

from src.imports import *
import src

settings_plugin = lightbulb.Plugin("settings.settings")
settings_plugin.add_checks(
    lightbulb.checks.guild_only,
    lightbulb.checks.bot_only
)

@settings_plugin.command()
@lightbulb.check_exempt(src.helper.perm_check)
@lightbulb.command("permission_settings", "settings for who can use which commands")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def permissionSettings(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(
        title="Permission Settings",
        description="Here you can set which roles can use which commands",
        color=src.helper.Color.dark_blue().__str__(),
        timestamp=src.helper.get_time()
    )




def load(bot):
    bot.add_plugin(settings_plugin)

def unload(bot):
    bot.remove_plugin(settings_plugin)


