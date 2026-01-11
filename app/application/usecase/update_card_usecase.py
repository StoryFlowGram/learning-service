from app.application.protocols.uow import IUnitOfWork
from app.domain.entity.card import Card
from app.application.dto.card_dto import CardDTO
from app.domain.exception.card_exceptions import CardNotFoundException


from app.application.protocols.uow import IUnitOfWork
from app.domain.value_object.review_quality_vo import ReviewQuality
from app.domain.exception.card_exceptions import CardNotFoundException
from app.application.dto.card_dto import CardDTO

class ReviewCardUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, user_id: int, card_id: int, quality_value: int) -> CardDTO:
        async with self.uow:
            card = await self.uow.cards.get_by_id(card_id=card_id, user_id=user_id)
            
            if not card:
                raise CardNotFoundException(card_id=card_id, user_id=user_id)

            quality = ReviewQuality(value=quality_value)
            card.update_srs_state(quality)
            updated_card = await self.uow.cards.update(card)
            await self.uow.commit() 
            return CardDTO(
                id=updated_card.id,
                user_id=updated_card.user_id,
                word=updated_card.word,
                translation=updated_card.translation,
                context=updated_card.context,
                next_review_at=updated_card.next_review_at,
                previous_interval=updated_card.previous_interval.days,
                ease_factor=updated_card.ease_factor,
                repetitions=updated_card.repetitions,
                created_at=updated_card.created_at
            )
