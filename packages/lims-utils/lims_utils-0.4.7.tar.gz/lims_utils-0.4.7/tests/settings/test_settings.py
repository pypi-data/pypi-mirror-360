from unittest.mock import patch

import pytest
from pydantic import BaseModel

from lims_utils.settings import Auth, Settings


def new_read_all(_, _1):
    return ""


class Nested(BaseModel):
    nested: Auth


class ExpandedSettings(Settings):
    nested: Nested


@pytest.mark.asyncio
@patch("lims_utils.settings.json.loads")
@patch("lims_utils.settings.Path.read_text", new=new_read_all)
async def test_return_default(mock_json_loads):
    """Should return default values"""
    mock_json_loads.return_value = {"auth": {}, "db": {}}

    settings = Settings()

    assert settings.auth.endpoint == "https://localhost/auth"


@pytest.mark.asyncio
@patch("lims_utils.settings.json.loads")
@patch("lims_utils.settings.Path.read_text", new=new_read_all)
async def test_custom(mock_json_loads):
    """Should return custom values"""
    mock_json_loads.return_value = {
        "auth": {"endpoint": "https://localhost/diff-auth"},
        "db": {"pool": 90},
    }

    settings = Settings()

    assert settings.auth.endpoint == "https://localhost/diff-auth"

    assert settings.db.pool == 90


@pytest.mark.asyncio
@patch("lims_utils.settings.json.loads")
@patch("lims_utils.settings.Path.read_text", new=new_read_all)
async def test_nested(mock_json_loads):
    """Should return nested values"""
    mock_json_loads.return_value = {
        "auth": {"endpoint": "https://localhost/diff-auth"},
        "db": {"pool": 90},
        "nested": {"nested": {"endpoint": "https://localhost/diff-auth"}},
    }

    settings = ExpandedSettings()

    assert settings.nested.nested.endpoint == "https://localhost/diff-auth"

    assert settings.db.pool == 90
