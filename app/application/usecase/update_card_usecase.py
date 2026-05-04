from app.application.dto.card_dto import CardDTO
from app.application.protocols.uow import IUnitOfWork
from app.domain.exception.card_exceptions import CardNotFoundException
from app.domain.value_object.review_quality_vo import ReviewQuality


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
            return CardDTO.from_entity(updated_card)
