from typing import Optional

class CardException(Exception):
    pass

class CardNotFoundException(CardException):
    def __init__(self, card_id: Optional[int] = None, user_id: Optional[int] = None, word: Optional[str] = None):
        if card_id: 
            super().__init__(f"Картка з ID {card_id} не знайдена.")
        elif user_id and word:
            super().__init__(f"Картка для користувача {user_id} зі словом '{word}' не знайдена.")
        else:
            super().__init__("Картка не знайдена.")
        self.card_id = card_id
        self.user_id = user_id
        self.word = word

class CardAlreadyExistsException(CardException):
    def __init__(self, user_id: int, word: str):
        super().__init__(f"Картка для користувача {user_id} зі словом '{word}' вже існує.")
        self.user_id = user_id
        self.word = word

class InvalidReviewQualityError(CardException, ValueError):
    def __init__(self, value: int):
        super().__init__(f"Неприпустиме значення якості відповіді: {value}. Очікується 0-5.")
        self.value = value
    