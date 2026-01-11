from app.presentation.schemas.card_schema import CardAddRequestSchema
from app.domain.entity.card import Card


def schema_to_domain(schema: CardAddRequestSchema, user_id: int):
    return Card(
        user_id=user_id,
        word=schema.word,
        translation=schema.translation,
        context=schema.context
    )