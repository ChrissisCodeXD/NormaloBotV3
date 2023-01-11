import hikari
from enum import Enum
import lightbulb
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
    "permissions": "Permissions"
}

p = hikari.Permissions

permissions = {
    p.BAN_MEMBERS: "Ban Members",
    p.KICK_MEMBERS: "Kick Members",
    p.MANAGE_CHANNELS: "Manage Channels",
    p.ADMINISTRATOR: "Administrator",
    p.MANAGE_GUILD: "Manage Guild",
    p.MANAGE_ROLES: "Manage Roles",
    p.SPEAK: "Speak",
    p.NONE: "None",
    p.MOVE_MEMBERS: "Move Members",
    p.MUTE_MEMBERS: "Mute Members",
    p.DEAFEN_MEMBERS: "Deafen Members",
    p.VIEW_AUDIT_LOG: "View Audit Log",
    p.VIEW_CHANNEL: "View Channel",
    p.VIEW_GUILD_INSIGHTS: "View Guild Insights",
    p.CREATE_INSTANT_INVITE: "Create Instant Invite",
    p.CHANGE_NICKNAME: "Change Nickname",
    p.MANAGE_NICKNAMES: "Manage Nicknames",
    p.PRIORITY_SPEAKER: "Priority Speaker",
    p.USE_APPLICATION_COMMANDS: "Use Application Commands",
    p.USE_EXTERNAL_EMOJIS: "Use External Emojis",
    p.MODERATE_MEMBERS: "Moderate Members",
    p.MANAGE_EMOJIS_AND_STICKERS: "Manage Emojis and Stickers",
    p.CREATE_PUBLIC_THREADS: "Create Public Threads",
    p.CREATE_PRIVATE_THREADS: "Create Private Threads",
    p.SEND_MESSAGES: "Send Messages",
}


def build_select_perms(bot,perm):
    row = bot.rest.build_message_action_row()
    select: hikari.api.SelectMenuBuilder = row.add_select_menu("change_perms_2")
    select.set_placeholder("Select the Permissions")
    select.set_max_values(25)
    select.set_min_values(0)
    for _, i in enumerate(permissions):
        if not perm[1] == "None" and (int(perm[1]) & i) == i:
            select.add_option(str(permissions[i]), str(int(i))).set_is_default(True).add_to_menu()
        else:
            select.add_option(str(permissions[i]), str(int(i))).set_is_default(False).add_to_menu()
    select.add_to_container()

    return [row]


@settings_plugin.listener(hikari.events.InteractionCreateEvent)
async def on_interaction_create(event: hikari.events.InteractionCreateEvent):
    e = event
    if isinstance(e.interaction, hikari.ComponentInteraction):
        i: hikari.ComponentInteraction = e.interaction

        if not i.guild_id: return
        if i.custom_id.startswith("change_perms"):
            author = int(i.message.embeds[0].footer.text.replace("Author: ",""))
            if i.member.id == author:
                cperms = p.NONE
                for per in i.values:
                    cperms |= int(per)
                await i.app.perm_cache.insert_permission(
                    guild_id=i.guild_id,
                    command=i.message.embeds[0].title.split(" ")[1].lower(),
                    permission_type="permissions",
                    permission=int(cperms)
                )
                embed = hikari.Embed(title="`✅` Success",
                                     description="Permissions saved!",
                                     color=src.helper.Color.green().__str__(), timestamp=src.helper.get_time())
                await i.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed=embed,
                                                flags=hikari.MessageFlag.EPHEMERAL)
            else:
                raise PermissionError()

async def build_permission_rows(bot,perm):
    rows: t.list[lightbulb.ActionRow] = []
    row = bot.rest.build_message_action_row()
    buttons = ["roles","permissions", "only_owner","everyone","default"]
    for i in buttons:
        row.add_button(
            hikari.ButtonStyle.PRIMARY,
            i
        ).set_label(i.capitalize().replace("_","")).add_to_container()
    rows.append(row)
    if perm[0] == "roles" or perm[0] == "permissions":
        rows.extend(build_select_perms(bot, perm))
    return rows

async def set_default_perms(ctx,command) -> tuple:
    if command == "permission_settings":
        await ctx.app.perm_cache.insert_permission(
            guild_id=ctx.guild_id,
            command=command,
            permission_type="only_owner"
        )
        return ("only_owner",'None')
    else:
        await ctx.app.perm_cache.insert_permission(
            guild_id=ctx.guild_id,
            command=command,
            permission_type="default"
        )
        return ("default",'None')

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
    perm: tuple = await ctx.app.perm_cache.get_permission(ctx.guild_id, command.name)
    if not perm:
        perm: tuple = await set_default_perms(ctx,command.name)
    perm_str = ""
    perm_str += f"`Permission Type:` **{perm_translation[perm[0]]}**\n"
    if str(perm[1]) != "None":
        perm_str += f"`Permission:` {perm[1]}"

    embed.set_footer(f"Author: {ctx.author.id}")
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


