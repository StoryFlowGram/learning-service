from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional
import math

from app.domain.value_object.review_quality_vo import ReviewQuality

@dataclass
class Card:
    user_id: int
    word: str
    translation: str
    context: Optional[str]

    next_review_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    previous_interval: timedelta = field(default_factory=lambda: timedelta(days=0))
    ease_factor: float = field(default=2.5)
    repetitions: int = field(default=0)
    MIN_EASE_FACTOR: float = 1.3
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    def update_srs_state(self, quality: ReviewQuality):
        if quality.value >= 3:
            self.ease_factor = max(
                self.MIN_EASE_FACTOR,
                self.ease_factor + (0.1 - (5 - quality.value) * (0.08 + (5 - quality.value) * 0.02))
            )

        if quality.value >= 3: 
            if self.repetitions == 0:
                next_interval_days = 1
            elif self.repetitions == 1:
                next_interval_days = 6
            else:
                next_interval_days = math.ceil(self.previous_interval.days * self.ease_factor)
            self.repetitions += 1
            self.previous_interval = timedelta(days=next_interval_days)
        else: 
            self.repetitions = 0
            next_interval_days = 1
            self.previous_interval = timedelta(days=next_interval_days)

        self.next_review_at = datetime.now(timezone.utc) + timedelta(days=next_interval_days)

    def is_due_for_review(self) -> bool:
        return datetime.now(timezone.utc) >= self.next_review_at