from abc import ABC, abstractmethod


class AbstractJwtVerifier(ABC):

    @abstractmethod
    def verify_token(self, token: str):
        ...

    @abstractmethod
    def get_user_id(self, token: str):
        ...