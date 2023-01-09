from src.imports import *


class Hashable:
    def __eq__(self, other):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self):
        return str(
            self.__class__.__name__ + "(" + ", ".join(
                [f"{k}={v!r}" for k, v in self.__dict__.items()]
            ) + ")"
        )


class UserEntry(Hashable):
    user_id: int
    user_name: str
    user_discriminator: str
    user_avatar: str
    user_banner: str
    user_bot: bool


class GuildEntry(Hashable):
    guild_id: int
    guild_name: str
    guild_icon: str
    guild_owner_id: int
    guild_member_count: int
