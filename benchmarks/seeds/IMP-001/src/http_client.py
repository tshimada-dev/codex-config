from __future__ import annotations

from dataclasses import dataclass
import time


class Cancelled(Exception):
    pass


@dataclass
class Response:
    status: int
    headers: dict[str, str]
    body: str = ""


class Transport:
    def send(self, method: str, url: str, *, body=None) -> Response:
        raise NotImplementedError


class Client:
    def __init__(self, transport: Transport, *, max_attempts: int = 3, sleeper=time.sleep):
        self.transport = transport
        self.max_attempts = max_attempts
        self.sleeper = sleeper

    def request(self, method: str, url: str, *, body=None, cancelled=lambda: False) -> Response:
        # Existing behavior: one attempt only.
        if cancelled():
            raise Cancelled()
        return self.transport.send(method, url, body=body)
