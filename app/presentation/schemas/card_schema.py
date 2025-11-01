from pydantic import BaseModel, ConfigDict
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
    user_id: int
    word: str
    translation: str
    context: str | None = None

    model_config = ConfigDict(from_attributes=True)


    