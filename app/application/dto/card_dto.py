from dataclasses import dataclass
from datetime import datetime
from typing import Optional

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