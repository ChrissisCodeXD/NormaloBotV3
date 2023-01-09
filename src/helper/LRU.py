from collections import OrderedDict
from typing import Generic, Hashable, Optional, TypeVar, Final, NamedTuple, ParamSpec
from collections.abc import Callable
import src

T = TypeVar("T")
P = ParamSpec("P")


class CacheInfo(NamedTuple):
    hits: int
    misses: int
    maxsize: int
    currsize: int


class LruCache(Generic[T]):
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.__cache: OrderedDict[Hashable, T] = OrderedDict()
        self.__hits = 0
        self.__misses = 0
        self.__maxsize: Final = capacity

    def get(self, key: Hashable) -> Optional[T]:
        if key not in self.__cache:
            self.__misses += 1
            return None
        self.__hits += 1
        self.__cache.move_to_end(key)
        return self.__cache[key]

    def insert(self, key: Hashable, value: T) -> None:
        if len(self.__cache) == self.capacity:
            self.__cache.popitem(last=False)
        self.__cache[key] = value
        self.__cache.move_to_end(key)

    def __len__(self) -> int:
        return len(self.__cache)

    def clear(self) -> None:
        self.__cache.clear()

    def cache_info(self) -> CacheInfo:
        return CacheInfo(
            hits=self.__hits,
            misses=self.__misses,
            currsize=len(self.__cache),
            maxsize=self.__maxsize,
        )


class PermissionCache(LruCache):
    def __init__(self, capacity: int, pool: src.database.PoolManager):
        self.__pool: src.database.PoolManager = pool
        super().__init__(capacity)

    async def get_permission(self, guild_id: int, command: str):
        key = f"{guild_id}:{command}"
        value = super().get(key)
        if value:
            return value
        else:
            db: src.database.DB = await self.__pool.getDBHandler("permissions")
            ret = await db.select(guild_id=guild_id, command=command)
            if len(ret) == 0:
                return False
            ret = ret[0]
            key = f"{ret[1]}:{ret[2]}"
            value = (ret[3], ret[4])
            super().insert(key, value)
            return value

    async def insert_permission(self, guild_id: int, command: str, permission_type: str, permission: str = "None") -> None:
        key = f"{guild_id}:{command}"
        value = (permission_type, permission)
        db: src.database.DB = await self.__pool.getDBHandler("permissions")
        await db.insert(guild_id=guild_id, command=command, type=permission_type, permission=permission)
        super().insert(key, value)
