from dataclasses import dataclass


@dataclass
class CardDTO:
    id: int
    user_id: int
    question: str
    answer: str
    created_at: str
    updated_at: str