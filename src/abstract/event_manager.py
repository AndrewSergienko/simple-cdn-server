from abc import ABC, abstractmethod
from typing import Callable, Type

from src.domain.events import Event


class AEventManager(ABC):
    @abstractmethod
    async def subscribe(self, event_class: Type[Event], callback: Callable):
        pass

    @abstractmethod
    async def publish(self, context: "AContext", event: Event):  # noqa: F821
        pass
