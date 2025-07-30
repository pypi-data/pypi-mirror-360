from __future__ import annotations

import asyncio
import fnmatch
from collections import defaultdict
from collections.abc import AsyncGenerator
from collections.abc import Generator
from typing import Any
from unittest import mock

import pytest


class MockRedis:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.values: dict[str, str] = {}
        self.lists: dict[str, list[str]] = defaultdict(list)
        self.events: dict[str, asyncio.Event] = defaultdict(asyncio.Event)

    async def aclose(self) -> None:
        pass

    async def blpop(
        self,
        keys: list[str],
        timeout: float = 0,
    ) -> list[str] | None:
        result: list[str] = []
        for key in keys:
            if len(self.lists[key]) > 0:
                item = self.lists[key].pop()
                self.events[key].clear()
            else:
                try:
                    await asyncio.wait_for(
                        self.events[key].wait(),
                        timeout=None if timeout == 0 else timeout,
                    )
                except asyncio.TimeoutError:
                    return None
                else:
                    item = self.lists[key].pop()
                    self.events[key].clear()
            result.extend([key, item])
        return result

    async def delete(self, key: str) -> None:  # pragma: no cover
        if key in self.values:
            del self.values[key]
        elif key in self.lists:
            self.lists[key].clear()

    async def exists(self, key: str) -> bool:  # pragma: no cover
        return key in self.values or key in self.lists

    async def get(
        self,
        key: str,
    ) -> str | list[str] | None:
        if key in self.values:
            return self.values[key]
        elif key in self.lists:
            raise NotImplementedError()
        return None

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        items = self.lists.get(key, None)
        if items is None:
            return []
        return items[start:end]

    async def ping(self, **kwargs) -> None:
        pass

    async def rpush(self, key: str, *values: str) -> None:
        for value in values:
            self.lists[key].append(value)
            self.events[key].set()

    async def scan_iter(self, pattern: str) -> AsyncGenerator[str]:
        for key in self.values:
            if fnmatch.fnmatch(key, pattern):
                yield key

    async def set(self, key: str, value: str) -> None:
        self.values[key] = value


@pytest.fixture
def mock_redis() -> Generator[None]:
    redis = MockRedis()
    with mock.patch('redis.asyncio.Redis', return_value=redis):
        yield
