from abc import ABC, abstractmethod
from typing import AsyncIterator

from pydantic import BaseModel


class Event(BaseModel):
    id: str
    topic: str
    type: str
    body: dict


class Consumer(ABC):
    @abstractmethod
    def listen(self) -> AsyncIterator[Event]: ...

    @abstractmethod
    def ack(self, event: Event): ...
