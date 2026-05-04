from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.domain.entity.card import Card


@dataclass
class CardDTO:
    id: int
    user_id: int
    word: str
    translation: str
    context: Optional[str]
    next_review_at: datetime
    previous_interval: int
    ease_factor: float
    repetitions: int
    created_at: Optional[datetime]

    @classmethod
    def from_entity(cls, card: Card) -> CardDTO:
        return cls(
            id=card.id,
            user_id=card.user_id,
            word=card.word,
            translation=card.translation,
            context=card.context,
            next_review_at=card.next_review_at,
            previous_interval=card.previous_interval.days,
            ease_factor=card.ease_factor,
            repetitions=card.repetitions,
            created_at=card.created_at,
        )