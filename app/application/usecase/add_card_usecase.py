from app.domain.entity.card import Card
from app.application.protocols.uow import IUnitOfWork
from app.application.dto.card_dto import CardDTO
from app.domain.exception.card_exceptions import CardAlreadyExistsException


class AddCardUseCase:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def __call__(self, card: Card):
        async with self.uow:
            check_existing = await self.uow.cards.get_by_word_and_user(
                card.word, 
                card.user_id
            )
            if check_existing:
                raise CardAlreadyExistsException(card.user_id, card.word)
            card_with_id = await self.uow.cards.add(card)       
            
        return CardDTO(
            id=card_with_id.id,
            user_id=card_with_id.user_id,
            word=card_with_id.word,
            translation=card_with_id.translation,
            context=card_with_id.context,
            next_review_at=card_with_id.next_review_at,
            previous_interval=card_with_id.previous_interval.days,
            ease_factor=card_with_id.ease_factor,
            repetitions=card_with_id.repetitions,
            created_at=card_with_id.created_at
            )