import pytest

from lims_utils.models import pagination


@pytest.mark.asyncio
async def test_pagination(caplog):
    """Should create pagination model"""
    pagination_model = pagination(page=5, limit=50)

    assert pagination_model["page"] == 5
    assert pagination_model["limit"] == 50
