from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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
    quality: int = Field(..., ge=0, le=5, description="Оцінка якості відповіді (0-5)")


class ForceNotificationRequestSchema(BaseModel):
    card_id: int = Field(default=0, ge=0, description="ID картки для тестового повідомлення")
    word: str = Field(default="test-word", min_length=1, max_length=255)
    translation: str = Field(default="тестовий переклад", min_length=1, max_length=255)


class ForceNotificationResponseSchema(BaseModel):
    status: str
    queue: str
    user_id: int
    card_id: int
    remind_at: datetime


class DueCountResponseSchema(BaseModel):
    due_count: int
    as_of: datetime
