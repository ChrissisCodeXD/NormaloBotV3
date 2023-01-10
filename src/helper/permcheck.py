import lightbulb
from src.imports import *



async def perm_check(ctx: lightbulb.Context):
    if ctx.author.id in ctx.app.owner_ids:
        return True
    perm: dict = await ctx.app.perm_cache.get_permission(ctx.guild_id, ctx.command.name)
    if not perm:
        if ctx.command.name == "permission_settings":
            await ctx.app.perm_cache.insert_permission(
                guild_id=ctx.guild_id,
                command=ctx.command.name,
                permission_type="only_owner"
            )
            if ctx.author.id == ctx.get_guild().owner_id:
                return True
        else:
            await ctx.app.perm_cache.insert_permission(
                guild_id=ctx.guild_id,
                command=ctx.command.name,
                permission_type="default"
            )
        return False
    match perm[0]:
        case "roles":
            allowed_roles = json.loads(perm[1])
            for i in ctx.member.role_ids:
                if int(i) in allowed_roles:
                    return True
        case "permission":
            permissions = int(perm[1])
            if (ctx.get_channel().permissions_for(ctx.member) & permissions) == permissions:
                return True
        case "only_owner":
            if ctx.author.id == ctx.get_guild().owner_id:
                return True
        case "everyone":
            return True
        case "only_bot_owner":
            if ctx.author.id in ctx.app.owner_ids:
                return True
        case "default":
            return False
    return False
