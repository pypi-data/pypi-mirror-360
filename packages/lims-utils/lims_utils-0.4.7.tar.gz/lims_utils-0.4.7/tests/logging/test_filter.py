import pytest

from lims_utils.logging import register_loggers, uvicorn_logger


@pytest.mark.asyncio
async def test_docs_filter(caplog):
    """Should not log message that includes docs as part of the path"""
    register_loggers()
    uvicorn_logger.error("Message %s %s %s", "Arg 1", "Arg 2", "/docs")

    assert not caplog.text


@pytest.mark.asyncio
async def test_docs_filter_custom(caplog):
    """Should not log message that includes URL in ignore list"""
    register_loggers(["/test"])
    uvicorn_logger.error("Message %s %s %s", "Arg 1", "Arg 2", "/test")

    assert not caplog.text


@pytest.mark.asyncio
async def test_docs_no_filter(caplog):
    """Should log message that doesn't include docs as part of the path"""
    register_loggers()
    uvicorn_logger.error("Message %s %s %s", "Arg 1", "Arg 2", "Arg 3")

    assert "Message Arg 1 Arg 2 Arg 3" in caplog.text


@pytest.mark.asyncio
async def test_docs_no_args(caplog):
    """Should log message with no string formatting args"""
    register_loggers()
    uvicorn_logger.error("Message")

    assert "Message" in caplog.text
