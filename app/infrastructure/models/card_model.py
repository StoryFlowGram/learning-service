from app.infrastructure.database.base import Base
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import String, BigInteger, DateTime, Integer, Float, CheckConstraint, UniqueConstraint, Index, Text



class CardModel(Base):
    __tablename__ = "cards"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    word: Mapped[str] = mapped_column(String)
    translation: Mapped[str] = mapped_column(String)
    context: Mapped[str] = mapped_column(Text)
    next_review_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    previous_interval: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    repetitions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    @validates('word', 'translation', 'context')
    def validate_strings(self, key, value: str):
        if not value or not value.strip():
            raise ValueError(f"{key} Не могут быть пустыми или содержать только пробелы.")
        return value.strip()

    @validates('ease_factor')
    def validate_ease_factor(self, key, value: float):
        if value < 1.3: # потому что минимальный коэффициент усвоения 1.3
            raise ValueError(f"{key} не может быть меньше 1.3")
        return value
    
    @validates('previous_interval', 'repetitions')
    def validate_non_negative(self, key, value: int):
        if value < 0:
            raise ValueError(f"{key} не может быть отрицательным")
        return value
    
    __table_args__ = (
        CheckConstraint(ease_factor >= 1.3, name='check_ease_factor_minimum'),
        CheckConstraint(previous_interval >= 0, name='check_previous_interval_non_negative'),
        CheckConstraint(repetitions >= 0, name='check_repetitions_non_negative'),
        UniqueConstraint('user_id', 'word', name='uix_user_word'),
        Index('ix_user_next_review', 'user_id', 'next_review_at'),
    )
