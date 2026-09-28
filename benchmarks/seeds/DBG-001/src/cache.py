from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Entry:
    value: object
    expires_at: float
    stale_until: float


@dataclass(frozen=True)
class Lookup:
    value: object | None
    state: str
    request_refresh: bool = False


class Cache:
    def __init__(self):
        self._entries = {}
        self.metrics = {"hit": 0, "miss": 0, "stale": 0}

    def put(self, key, value, *, expires_at: float, stale_until: float):
        self._entries[key] = Entry(value, expires_at, stale_until)

    def get(self, key, *, now: float) -> Lookup:
        entry = self._entries.get(key)
        if entry is None:
            self.metrics["miss"] += 1
            return Lookup(None, "miss")
        # Regression: stale-but-servable entries became immediate misses.
        if now >= entry.expires_at:
            self.metrics["miss"] += 1
            return Lookup(None, "miss")
        self.metrics["hit"] += 1
        return Lookup(entry.value, "fresh")
