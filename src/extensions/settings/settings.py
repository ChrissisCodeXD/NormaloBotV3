import hikari

from src.imports import *
import src
from typing import Union, Sequence

settings_plugin = lightbulb.Plugin("settings.settings")
settings_plugin.add_checks(
    lightbulb.checks.guild_only,
    lightbulb.checks.bot_only
)




@settings_plugin.command()
@lightbulb.check_exempt(src.helper.perm_check)
@lightbulb.option("command","The Command where you wanna change the permissions",type=str,autocomplete=True)
@lightbulb.command("permission_settings", "settings for who can use which commands")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def permissionSettings(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(
        title="Permission Settings",
        description="Here you can set which roles can use which commands",
        color=src.helper.Color.dark_blue().__str__(),
        timestamp=src.helper.get_time()
    )

@command.autocomplete("command")
async def command_autocomplete(
        opt: hikari.AutocompleteInteractionOption, inter: hikari.AutocompleteInteraction
) -> Union[str, Sequence[str], hikari.CommandChoice, Sequence[hikari.CommandChoice]]:
    toret = []
    for command_name in settings_plugin.app.slash_commands:
        if command_name.startswith(opt.value):
            toret.append(command_name)
    return toret



def load(bot):
    bot.add_plugin(settings_plugin)

def unload(bot):
    bot.remove_plugin(settings_plugin)


