import unittest
from datetime import datetime, timedelta, timezone

from app.application.usecase.update_card_usecase import ReviewCardUseCase
from app.domain.entity.card import Card
from app.domain.value_object.review_quality_vo import ReviewQuality


class FakeCardRepository:
    def __init__(self, card: Card):
        self._card = card
        self.last_updated_card: Card | None = None

    async def get_by_id(self, card_id: int, user_id: int) -> Card | None:
        if self._card.id == card_id and self._card.user_id == user_id:
            return self._card
        return None

    async def update(self, card: Card) -> Card:
        self.last_updated_card = card
        self._card = card
        return card


class FakeUoW:
    def __init__(self, repo: FakeCardRepository):
        self.cards = repo
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def commit(self):
        self.committed = True

    async def rollback(self):
        return None


class SRSAlgorithmTestCase(unittest.TestCase):
    def test_successful_review_updates_intervals_sm2_style(self):
        card = Card(
            id=1,
            user_id=10,
            word="example",
            translation="приклад",
            context="",
            ease_factor=2.5,
            repetitions=0,
            previous_interval=timedelta(days=0),
        )

        card.update_srs_state(ReviewQuality(value=5))
        self.assertEqual(card.repetitions, 1)
        self.assertEqual(card.previous_interval.days, 1)
        self.assertAlmostEqual(card.ease_factor, 2.6, places=6)

        card.update_srs_state(ReviewQuality(value=5))
        self.assertEqual(card.repetitions, 2)
        self.assertEqual(card.previous_interval.days, 6)
        self.assertAlmostEqual(card.ease_factor, 2.7, places=6)

        card.update_srs_state(ReviewQuality(value=5))
        self.assertEqual(card.repetitions, 3)
        self.assertEqual(card.previous_interval.days, 17)
        self.assertAlmostEqual(card.ease_factor, 2.8, places=6)

    def test_failed_review_resets_repetitions_and_reduces_ease_factor(self):
        card = Card(
            id=2,
            user_id=10,
            word="failure",
            translation="помилка",
            context="",
            ease_factor=2.5,
            repetitions=3,
            previous_interval=timedelta(days=10),
        )

        card.update_srs_state(ReviewQuality(value=1))
        self.assertEqual(card.repetitions, 0)
        self.assertEqual(card.previous_interval.days, 1)
        self.assertAlmostEqual(card.ease_factor, 1.96, places=6)
        self.assertGreater(card.next_review_at, datetime.now(timezone.utc))


class ReviewUseCasePersistenceTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_review_usecase_commits_and_updates_repository(self):
        card = Card(
            id=11,
            user_id=42,
            word="commit",
            translation="коміт",
            context="",
            ease_factor=2.5,
            repetitions=1,
            previous_interval=timedelta(days=6),
        )
        repo = FakeCardRepository(card)
        uow = FakeUoW(repo)
        usecase = ReviewCardUseCase(uow)

        result = await usecase(user_id=42, card_id=11, quality_value=2)

        self.assertTrue(uow.committed)
        self.assertIsNotNone(repo.last_updated_card)
        self.assertEqual(result.repetitions, 0)
        self.assertEqual(result.previous_interval, 1)
        self.assertLess(result.ease_factor, 2.5)


if __name__ == "__main__":
    unittest.main()
