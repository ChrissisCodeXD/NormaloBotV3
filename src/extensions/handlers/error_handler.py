from src.imports import *
import src

err_plugin = lightbulb.Plugin("error_plugin")


@err_plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event):
    exception = event.exception

    if isinstance(event.exception, lightbulb.errors.NotEnoughArguments):
        if isinstance(event.context, lightbulb.context.prefix.PrefixContext):
            if event.context.invoked_with == "clear":
                return await event.context.respond(
                    f"Please specify the number of messages to clear `e.g. {event.app._prefix__get_class.get_prefix(event.context.guild_id)}clear 10`",
                    delete_after=3
                )

    if isinstance(event.exception, lightbulb.errors.OnlyInGuild):
        return await event.context.respond(
            f"This Command can only be used in Guilds! Sorry \:(",
            delete_after=3
        )

    if isinstance(event.exception, lightbulb.errors.BotOnly):
        return await event.context.respond(
            f"Sorry you are missing the required Permissions!",
            delete_after=3
        )

    if isinstance(exception, lightbulb.NotOwner):
        return await event.context.respond("You are not the owner of this bot.", delete_after=3)

    if isinstance(exception, lightbulb.CommandIsOnCooldown):
        return await event.context.respond(
            f"This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds.",
            delete_after=3)

    if isinstance(exception, lightbulb.errors.CommandNotFound):
        temp = {}
        for i in event.app.prefix_commands:
            temp[str(i)] = src.helper.similar(i, event.context.invoked_with)
        temp = sorted(temp.items(), key=lambda x: x[1], reverse=True)
        return await event.context.respond(
            f"The Command {event.context.invoked_with} does not exist!\nDid you mean {'!'}{temp[0][0]} or {'!'}{temp[1][0]}?",
            delete_after=5)

    if isinstance(exception, lightbulb.NotOwner):
        return await event.context.respond("You are not the owner of this bot.", delete_after=3)

    if isinstance(exception, lightbulb.errors.BotMissingRequiredPermission):
        return await event.context.respond(
            "The bot is missing one or more permissions required in order to run this command", delete_after=3)

    if isinstance(exception, lightbulb.errors.MissingRequiredPermission):
        return await event.context.respond(
            "You are missing one or more permissions required in order to run this command", delete_after=3)

    bot: src.main.NormaloBot = err_plugin.app
    db: src.database.DB = await bot.db.getDBHandler("errors")

    err_id = src.helper.generate_id()
    await db.insert(
        err_id=err_id,
        err_cmd=event.context.invoked_with,
        err_text="".join(traceback.format_exception(event.exception))
    )

    embed = hikari.Embed(
        title=f"Something went wrong. An error report has been created!",
        description=f"(ID: {err_id[:7]}).\nPlease try again or join our support [Server](https://discord.gg/5XzYqztxaA)",
        color=src.helper.Color.red().__str__(),
        timestamp=src.helper.get_time()
    )
    if event.context.interaction:
        pass
        await event.context.respond(
            embed=embed,
            flags=hikari.MessageFlag.EPHEMERAL
        )
    else:
        await event.context.respond(
            embed=embed,
            delete_after=15
        )
    # await Log.send_error_log(event.exception, event.context.invoked_with,err_id)

    raise (event.exception)


def load(bot):
    bot.add_plugin(err_plugin)


def unload(bot):
    bot.remove_plugin(err_plugin)
