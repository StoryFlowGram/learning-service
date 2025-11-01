from app.presentation.schemas.card_schema import CardAddRequestSchema
from app.domain.entity.card import Card


def schema_to_domain(schema: CardAddRequestSchema):
    return Card(
        user_id=schema.user_id,
        word=schema.word,
        translation=schema.translation,
        context=schema.context
    )