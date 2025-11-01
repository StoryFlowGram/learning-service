from app.domain.entity.card import Card
from app.infrastructure.models.card_model import CardModel
from datetime import timedelta


def orm_to_domain(orm: CardModel):
    return Card(
        id=orm.id,
        user_id=orm.user_id,
        word=orm.word,
        translation=orm.translation,
        context=orm.context,
        next_review_at=orm.next_review_at,
        previous_interval=timedelta(days=orm.previous_interval),
        ease_factor=orm.ease_factor,
        repetitions=orm.repetitions,
        created_at=orm.created_at
    )


def domain_to_orm(domain: Card):
    return CardModel(
        user_id=domain.user_id,
        word=domain.word,
        translation=domain.translation,
        context=domain.context,
        next_review_at=domain.next_review_at,
        previous_interval=domain.previous_interval.days,
        ease_factor=domain.ease_factor,
        repetitions=domain.repetitions
    )