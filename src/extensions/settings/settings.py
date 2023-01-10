import hikari
from enum import Enum
from src.imports import *
import src
from typing import Union, Sequence

settings_plugin = lightbulb.Plugin("settings.settings")
settings_plugin.add_checks(
    lightbulb.checks.guild_only,
    #lightbulb.checks.bot_only
)


perm_translation = {
    "only_owner": "Only owner of the Guild",
    "default": "Default Permissions",
    "roles": "Roles",
    "everyone": "Everyone can use this command",
    "only_bot_owner": "Only the owner of the Bot can use this command!",
    "permission": "Permissions"
}


async def build_permission_rows(bot,perm):
    rows: t.list[lightbulb.ActionRow] = []
    row = bot.rest.build_message_action_row()

    row.add_button(
        hikari.ButtonStyle.PRIMARY,
        "roles"
    ).set_label("Roles").add_to_container()

    row.add_button(
        hikari.ButtonStyle.PRIMARY,
        "permissions"
    ).set_label("Permissions").add_to_container()

    row.add_button(
        hikari.ButtonStyle.PRIMARY,
        "ownly_guild"
    ).set_label("Guild Only").add_to_container()

    row.add_button(
        hikari.ButtonStyle.PRIMARY,
        "everyone"
    ).set_label("Everyone").add_to_container()

    row.add_button(
        hikari.ButtonStyle.PRIMARY,
        "default"
    ).set_label("Default").add_to_container()

    rows.append(row)
    return rows

async def set_default_perms(ctx):
    if ctx.command.name == "permission_settings":
        await ctx.app.perm_cache.insert_permission(
            guild_id=ctx.guild_id,
            command=ctx.command.name,
            permission_type="only_owner"
        )
    else:
        await ctx.app.perm_cache.insert_permission(
            guild_id=ctx.guild_id,
            command=ctx.command.name,
            permission_type="default"
        )

@settings_plugin.command()
@lightbulb.check_exempt(src.helper.perm_check)
@lightbulb.option("command","The Command where you wanna change the permissions",type=str,autocomplete=True)
@lightbulb.command("permission_settings", "settings for who can use which commands")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
@src.parse_options()
async def permissionSettings(ctx: lightbulb.Context, command: str) -> None:
    command: lightbulb.Command = settings_plugin.app.slash_commands[command]
    embed = hikari.Embed(
        title=f'`💻` {command.name.capitalize()}',
        description=command.description,
        color=src.helper.Color.dark_blue().__str__(),
        timestamp=src.helper.get_time()
    )
    perm: dict = await ctx.app.perm_cache.get_permission(ctx.guild_id, ctx.command.name)
    if not perm:
        await set_default_perms(ctx)
    perm_str = ""

    perm_str += f"`Permission Type:` **{perm_translation[perm[0]]}**\n"
    if str(perm[1]) != "None":
        perm_str += f"`Permission:` {perm[1]}"

    embed.set_footer(f"Command: {command.name}")
    embed.add_field("`🔐` Current Permission", perm_str)

    info_str = ""

    info_str += "**Buttons:** You can switch between diffrent types of permissions:\n"
    info_str += "`Roles` You can select which roles can use this command\n"
    info_str += "`Permissions` You can select the permissions the user needs\n"
    info_str += "`Owner Only` Only the Owner of the Guild can use the command\n"
    info_str += "`Everyone` Everyone can use this command!\n"
    info_str += "`Default` The default permissions are used"


    embed.add_field("`ℹ️` Info",info_str)

    rows = await build_permission_rows(ctx.app, perm)

    await ctx.respond(embed=embed, flags=hikari.MessageFlag.EPHEMERAL,components=rows)




@permissionSettings.autocomplete("command")
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


