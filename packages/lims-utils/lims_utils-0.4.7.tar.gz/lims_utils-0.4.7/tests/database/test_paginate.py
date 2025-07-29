from unittest.mock import patch

from sqlalchemy import select
from tests.mocks import FakeSession, query_eq

from lims_utils.database import Database, get_session
from lims_utils.tables import Proposal  # type: ignore

query = select(Proposal).filter(Proposal.proposalId == 1)


db = Database()
fs = FakeSession()


@patch.object(fs, "execute")
def test_paginate(mock_session):
    """Should append limits/offset to original query"""

    mock_session.return_value.all.return_value = ["a", "b", "c"]
    with get_session(lambda: fs):
        response = db.paginate(query, 20, 1)
        assert response.items == ["a", "b", "c"]

    assert query_eq(mock_session.call_args.args[0], query.limit(20).offset(20))


@patch.object(fs, "scalars")
def test_paginate_scalar(mock_session):
    """Should append limits/offset to original query (in scalar form)"""

    mock_session.return_value.all.return_value = ["f", "g", "h"]
    with get_session(lambda: fs):
        response = db.paginate(query, 20, 1, scalar=False, precounted_total=3)
        assert response.items == ["f", "g", "h"]

    assert query_eq(mock_session.call_args.args[0], query.limit(20).offset(20))


@patch.object(fs, "execute")
def test_paginate_reverse(mock_session):
    """Should set page counting from last page if passed page is negative"""

    mock_session.return_value.all.return_value = []
    with get_session(lambda: fs):
        response = db.paginate(query, 20, -1, precounted_total=100)
        assert response.page == 4

    assert query_eq(mock_session.call_args.args[0], query.limit(20).offset(80))


def test_total_zero():
    """Should return empty list if total is 0"""

    query = select(Proposal).filter(Proposal.proposalId == 1)

    with get_session(lambda: fs):
        response = db.paginate(query, 20, -1, precounted_total=0)
        assert response.items == []


@patch.object(db, "fast_count")
def test_fast_count(mock_fast_count):
    """Should return count from fast_count method if fast counting is enabled"""

    mock_fast_count.return_value = 150
    with get_session(lambda: fs):
        response = db.paginate(query, 20, -1, slow_count=False)
        assert response.items == ["a", "b", "c"]
        assert response.total == 150
