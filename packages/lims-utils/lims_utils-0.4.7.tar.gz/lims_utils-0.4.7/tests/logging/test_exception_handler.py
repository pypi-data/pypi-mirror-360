import pytest
from fastapi import HTTPException, Request, status

from lims_utils.logging import log_exception_handler

default_scope = {
    "type": "http",
    "state": {"user": "username"},
    "path": "http://test.ac.uk",
    "headers": {},
}


@pytest.mark.asyncio
async def test_log_format(caplog):
    """Should log message with user provided"""
    request = Request(scope=default_scope)

    await log_exception_handler(
        request,
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failure details"),
    )

    assert "username @ http://test.ac.uk: Failure details" in caplog.text


@pytest.mark.asyncio
async def test_log_format_no_user(caplog):
    """Should log message with no user provided"""
    request = Request(scope={**default_scope, "state": {}})

    await log_exception_handler(
        request,
        HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failure details"),
    )

    assert "Unknown user @ http://test.ac.uk: Failure details" in caplog.text
