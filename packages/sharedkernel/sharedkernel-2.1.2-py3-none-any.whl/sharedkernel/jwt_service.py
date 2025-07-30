import jwt
import time
from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sharedkernel.exception.exception import UnAuthorizedException
from sharedkernel.objects import JwtModel


class JWTBearer(HTTPBearer):

    def __init__(self,jwt_config:JwtModel, auto_error: bool = True):
        self.jwt_config=jwt_config
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        try:
            credentials: HTTPAuthorizationCredentials = await super(
                JWTBearer, self
            ).__call__(request)

            decoded_token = self.verify(credentials.credentials)
            request.state.decoded_token = decoded_token

        except:
            raise UnAuthorizedException()       


    def verify(self, token: str) -> dict:
            decoded_token = jwt.decode(
            jwt= token.replace("Bearer","").strip(),
            key= self.jwt_config.secret_key,
            algorithms= self.jwt_config.algorithms,
            audience= self.jwt_config.audience,
            issuer= self.jwt_config.issuer
            )

            if decoded_token["exp"] < time.time():
                raise UnAuthorizedException()
            
            return decoded_token
