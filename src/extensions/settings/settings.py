import hikari

import src
from src.imports import *

settings_plugin = lightbulb.Plugin("settings.settings")
settings_plugin.add_checks(
    lightbulb.checks.guild_only,
    # lightbulb.checks.bot_only
)

perm_translation = {
    "only_owner": "Only owner of the Guild",
    "default": "Default Permissions",
    "roles": "Roles",
    "everyone": "Everyone can use this command",
    "only_bot_owner": "Only the owner of the Bot can use this command!",
    "permissions": "Permissions"
}

perm_buttons = ["roles", "permissions", "only_owner", "everyone", "default"]

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


def build_select_perms(bot, perm):
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


async def build_select_roles(bot, perm, guild: hikari.Guild):
    rows = []
    row = bot.rest.build_message_action_row()
    fetched_roles = await guild.fetch_roles()
    overall_roles = len(fetched_roles)
    fetched_roles = sorted(fetched_roles, key=lambda x: x.position, reverse=True)
    print(overall_roles)
    roles: hikari.api.SelectMenuBuilder = row.add_select_menu("select_roles_0")
    roles.set_placeholder("Select the Roles")
    if overall_roles < 25:
        roles.set_max_values(overall_roles)
    else:
        roles.set_max_values(25)
    roles.set_min_values(0)
    selected_roles = json.loads(perm[1])
    for _, role in enumerate(fetched_roles):
        if _ % 25 == 0 and _ != 0:

            roles.add_to_container()
            rows.append(row)
            row = bot.rest.build_message_action_row()
            print("select_roles_" + str(round(_/25)))
            roles: hikari.api.SelectMenuBuilder = row.add_select_menu("select_roles_" + str(round(_/25)))
            roles.set_placeholder("Select the Roles")
            overall_roles -= 25
            if overall_roles < 25:
                roles.set_max_values(overall_roles)
            else:
                roles.set_max_values(25)
            roles.set_min_values(0)
        if role.id in selected_roles:
            roles.add_option(str(f"@{role.name}"), str(role.id)).set_is_default(True).add_to_menu()
        else:
            roles.add_option(str(f"@{role.name}"), str(role.id)).set_is_default(False).add_to_menu()
    roles.add_to_container()
    rows.append(row)
    return rows


async def build_permission_rows(bot, perm, guild: hikari.Guild):
    rows: t.list[lightbulb.ActionRow] = []
    row = bot.rest.build_message_action_row()

    for i in perm_buttons:
        row.add_button(
            hikari.ButtonStyle.PRIMARY,
            i
        ).set_label(i.capitalize().replace("_", "")).add_to_container()
    rows.append(row)
    if perm[0] == "permissions":
        rows.extend(build_select_perms(bot, perm))
    elif perm[0] == "roles":
        rows.extend(await build_select_roles(bot, perm, guild))
    return rows


async def set_default_perms(guild_id: int, command) -> tuple:
    if command == "permission_settings":
        await settings_plugin.app.perm_cache.insert_permission(
            guild_id=guild_id,
            command=command,
            permission_type="only_owner"
        )
        return ("only_owner", 'None')
    else:
        await settings_plugin.app.perm_cache.insert_permission(
            guild_id=guild_id,
            command=command,
            permission_type="default"
        )
        return ("default", 'None')


async def build_perm_settings_message(command: lightbulb.Command, guild: hikari.Guild, author: hikari.Member):
    embed = hikari.Embed(
        title=f'`💻` {command.name.capitalize()}',
        description=command.description,
        color=src.helper.Color.dark_blue().__str__(),
        timestamp=src.helper.get_time()
    )
    perm: tuple = await settings_plugin.app.perm_cache.get_permission(guild.id, command.name)
    if not perm:
        perm: tuple = await set_default_perms(guild.id, command.name)
    perm_str = ""
    perm_str += f"`Permission Type:` **{perm_translation[perm[0]]}**\n"
    if str(perm[1]) != "None":
        if str(perm[0]) == "roles":
            perm_str += "`Roles:`"
            for role in json.loads(perm[1]):
                perm_str += f" <@&{role}>"
            perm_str += "\n"
        else:
            perm_str += f"`Permission:` {perm[1]}"

    embed.set_footer(f"Author: {author.id}")
    embed.add_field("`🔐` Current Permission", perm_str)

    info_str = ""

    info_str += "**Buttons:** You can switch between diffrent types of permissions:\n"
    info_str += "`Roles` You can select which roles can use this command\n"
    info_str += "`Permissions` You can select the permissions the user needs\n"
    info_str += "`Owner Only` Only the Owner of the Guild can use the command\n"
    info_str += "`Everyone` Everyone can use this command!\n"
    info_str += "`Default` The default permissions are used"

    embed.add_field("`ℹ️` Info", info_str)

    rows = await build_permission_rows(settings_plugin.app, perm, guild)
    return [embed], rows


def get_selected_role_ids(msg: hikari.Message):
    to_ret = []
    for _, i in enumerate(msg.components):
        if isinstance(i.components[0], hikari.SelectMenuComponent):
            to_ret.append([])
            for opt in i.components[0].options:
                if opt.is_default:
                    to_ret[_-1].append(opt.value)
    return to_ret

@settings_plugin.listener(hikari.events.InteractionCreateEvent)
async def on_interaction_create(event: hikari.events.InteractionCreateEvent):
    e = event
    if isinstance(e.interaction, hikari.ComponentInteraction):
        i: hikari.ComponentInteraction = e.interaction
        if not i.guild_id: return
        author = int(i.message.embeds[0].footer.text.replace("Author: ", ""))
        if i.custom_id.startswith("change_perms"):
            if i.member.id == author:
                command: lightbulb.Command = settings_plugin.app.slash_commands[
                    i.message.embeds[0].title.split(" ")[1].lower()]
                cperms = p.NONE
                for per in i.values:
                    cperms |= int(per)
                await i.app.perm_cache.insert_permission(
                    guild_id=i.guild_id,
                    command=command.name,
                    permission_type="permissions",
                    permission=int(cperms)
                )
                embed = hikari.Embed(title="`✅` Success",
                                     description="Permissions saved!",
                                     color=src.helper.Color.green().__str__(), timestamp=src.helper.get_time())
                await i.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed=embed,
                                                flags=hikari.MessageFlag.EPHEMERAL)
                embeds, rows = await build_perm_settings_message(command, i.get_guild(), i.member)
                await i.edit_message(i.message, embeds=embeds, components=rows)
            else:
                raise PermissionError()

        elif i.custom_id.startswith("select_roles"):
            if i.member.id == author:
                command: lightbulb.Command = settings_plugin.app.slash_commands[
                    i.message.embeds[0].title.split(" ")[1].lower()]
                roles = get_selected_role_ids(i.message)
                roles = [[int(i) for i in roles[_]] for _, rol in enumerate(roles)]
                print(roles)
                act_row = int(i.custom_id.replace("select_roles", "").replace("_", ""))
                role_ids = []
                for _, ro in enumerate(roles):
                    if act_row == _: continue
                    role_ids.extend(ro)
                for r in i.values:
                    r = int(r)
                    role_ids.append(r)

                print(role_ids)

                await i.app.perm_cache.insert_permission(
                    guild_id=i.guild_id,
                    command=command.name,
                    permission_type="roles",
                    permission=json.dumps(role_ids)
                )
                embed = hikari.Embed(title="`✅` Success",
                                     description="Roles saved!",
                                     color=src.helper.Color.green().__str__(), timestamp=src.helper.get_time())
                await i.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed=embed,
                                                flags=hikari.MessageFlag.EPHEMERAL)
                embeds, rows = await build_perm_settings_message(command, i.get_guild(), i.member)
                await i.edit_message(i.message, embeds=embeds, components=rows)
            else:
                raise PermissionError()

        elif i.custom_id in perm_buttons:
            if i.member.id == author:
                perm = ""
                if i.custom_id == "roles":
                    perm = "[]"
                elif i.custom_id == "permissions":
                    perm = "0"
                else:
                    perm = "None"
                command: lightbulb.Command = settings_plugin.app.slash_commands[
                    i.message.embeds[0].title.split(" ")[1].lower()]
                await i.app.perm_cache.insert_permission(
                    guild_id=i.guild_id,
                    command=command.name,
                    permission_type=i.custom_id,
                    permission=perm
                )
                embed = hikari.Embed(title="`✅` Success",
                                     description="Permissions saved!",
                                     color=src.helper.Color.green().__str__(), timestamp=src.helper.get_time())
                await i.create_initial_response(hikari.ResponseType.MESSAGE_CREATE, embed=embed,
                                                flags=hikari.MessageFlag.EPHEMERAL)
                embeds, rows = await build_perm_settings_message(command, i.get_guild(), i.member)
                await i.edit_message(i.message, embeds=embeds, components=rows)
            else:
                raise PermissionError()


@settings_plugin.command()
@lightbulb.check_exempt(src.helper.perm_check)
@lightbulb.option("command", "The Command where you wanna change the permissions", type=str, autocomplete=True)
@lightbulb.command("permission_settings", "settings for who can use which commands")
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
@src.parse_options()
async def permissionSettings(ctx: lightbulb.Context, command: str) -> None:
    command: lightbulb.Command = settings_plugin.app.slash_commands[command]
    embeds, rows = await build_perm_settings_message(command, ctx.get_guild(), ctx.member)
    await ctx.respond(embeds=embeds, components=rows)


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
