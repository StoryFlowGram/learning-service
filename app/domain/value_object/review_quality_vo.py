from dataclasses import dataclass

@dataclass(frozen=True)
class ReviewQuality:
    value: int

    MIN_VALUE = 0
    MAX_VALUE = 5

    def __post_init__(self):
        if not isinstance(self.value, int) or not (self.MIN_VALUE <= self.value <= self.MAX_VALUE):
            raise ValueError(f"Якість відповіді має бути цілим числом від {self.MIN_VALUE} до {self.MAX_VALUE}.")