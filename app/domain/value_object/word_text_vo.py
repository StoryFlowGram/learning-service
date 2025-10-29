from dataclasses import dataclass

@dataclass(frozen=True) 
class WordText:
    value: str

    MAX_LENGTH = 255 

    def __post_init__(self):
        if not self.value or not isinstance(self.value, str):
            raise ValueError("Текст слова/перекладу не може бути порожнім.")
        if len(self.value) > self.MAX_LENGTH:
            raise ValueError(f"Текст не може бути довшим за {self.MAX_LENGTH} символів.")

    def __str__(self) -> str:
        return self.value

    def lower(self) -> str:
        return self.value.lower()