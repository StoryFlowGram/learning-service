from abc import ABC, abstractmethod
import datetime
from app.domain.entity.card import Card


class CardProtocol(ABC):
    @abstractmethod
    async def add(self, card: Card) -> Card:
        ...

    @abstractmethod
    async def update(self, card: Card) -> Card:
        ...

    @abstractmethod
    async def get_by_id(self, card_id: int, user_id: int) -> Card:
        ...

    @abstractmethod
    async def get_due_for_review(self, user_id: int, limit: int, now: datetime) -> list[Card]:
        ...

    @abstractmethod
    async def get_all_by_user(self, user_id: int) -> list[Card]:
        ...


    @abstractmethod
    async def delete(self, card_id: int, user_id: int) -> None:
        ...

    @abstractmethod
    async def get_by_word_and_user(self, word: str, user_id: int) -> Card:
        ...