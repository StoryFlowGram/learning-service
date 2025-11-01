import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from app.application.protocols.jwt_verifier_protocol import AbstractJwtVerifier
from app.infrastructure.config.settings import Settings

jwt_setting = Settings(".env")

class JWTTokenVerifier(AbstractJwtVerifier):

    def __init__(self):
        self.secret_key = jwt_setting.jwt.JWT_SECRET
        self.algorithm = jwt_setting.jwt.JWT_ALGORITHM


    def verify_token(self, token:str):
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"require_iat": True, "require_sub": True},
            )
            
        except ExpiredSignatureError:
            raise Exception("Токен истёк")
        except InvalidTokenError:
            raise Exception("Невалидный токен")
        return payload
            

    def get_user_id(self, token: str):
        payload = self.verify_token(token)
        return payload["sub"]