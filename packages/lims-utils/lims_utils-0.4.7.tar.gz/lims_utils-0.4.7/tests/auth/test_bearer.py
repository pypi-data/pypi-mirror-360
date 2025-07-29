import pytest
from fastapi import HTTPException, Request

from lims_utils.auth import CookieOrHTTPBearer

default_scope = {
    "type": "http",
    "state": {"user": "username"},
    "path": "http://test.ac.uk",
    "headers": {},
}


@pytest.mark.asyncio
async def test_valid_token_in_bearer():
    """Return valid object containing token if it does exist in header"""
    handler = CookieOrHTTPBearer()
    request = Request(
        scope={
            **default_scope,
            "headers": [(b"authorization", b"Bearer token")],
        }
    )

    response = await handler(request)

    assert response.credentials == "token"


@pytest.mark.asyncio
async def test_valid_token_in_cookie():
    """Return valid object containing token if it does exist in cookie"""
    handler = CookieOrHTTPBearer(cookie_key="cookie_key")
    request = Request(
        scope={
            **default_scope,
            "headers": [(b"cookie", b"cookie_key=token")],
        }
    )

    response = await handler(request)

    assert response.credentials == "token"


@pytest.mark.asyncio
async def test_no_valid_token():
    """Raise 401 if no token is present"""
    handler = CookieOrHTTPBearer()
    request = Request(scope=default_scope)

    with pytest.raises(HTTPException):
        await handler(request)
