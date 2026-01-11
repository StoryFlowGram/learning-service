from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, timedelta
from typing import Optional



class CardResponseSchema(BaseModel):
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

    model_config = ConfigDict(from_attributes=True)


class CardAddRequestSchema(BaseModel):
    word: str
    translation: str
    context: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CardReviewRequestSchema(BaseModel):
    card_id: int
    quality: int = Field(..., ge=0, le=5, description="Оценка качества ответа (0-5)")