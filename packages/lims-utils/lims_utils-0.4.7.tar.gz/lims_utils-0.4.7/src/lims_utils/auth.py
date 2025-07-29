from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param


@dataclass
class GenericUser:
    """Generic user model, to be used with ISPyB"""

    fedid: str
    id: str
    familyName: str
    title: str
    givenName: str
    permissions: list[str]
    email: str | None = None


class CookieOrHTTPBearer(HTTPBearer):
    """Authentication model class that takes in cookies, and falls back to authorization bearer headers if
    the cookie can't be found"""

    def __init__(
        self,
        *,
        bearerFormat: Optional[str] = None,
        scheme_name: Optional[str] = None,
        description: Optional[str] = None,
        auto_error: bool = True,
        cookie_key: str = "cookie_auth",
    ):
        """
        Cookie/HTTP authorisation header dependency. Extends FastAPIs HTTPBearer.

        Args:
            cookie_key: Cookie key to look for in requests
        """
        super().__init__(
            bearerFormat=bearerFormat,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

        self.cookie_key = cookie_key

    async def __call__(self, request: Request):
        token = request.cookies.get(self.cookie_key)
        if token is not None:
            return HTTPAuthorizationCredentials(scheme="cookie", credentials=token)

        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)

        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
                )

        return await super().__call__(request)
