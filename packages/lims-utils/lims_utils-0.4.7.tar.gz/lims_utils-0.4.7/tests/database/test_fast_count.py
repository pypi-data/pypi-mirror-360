from unittest.mock import patch

from sqlalchemy import func, select
from tests.mocks import FakeSession, query_eq

from lims_utils.database import Database, get_session
from lims_utils.tables import Proposal  # type: ignore

query = (
    select(Proposal).filter(Proposal.proposalId == 1).order_by(Proposal.proposalNumber)
)


db = Database()
fs = FakeSession()


@patch.object(fs, "execute")
def test_count(mock_session):
    """Should count by removing order and getting first literal column"""

    mock_session.return_value.scalar_one.return_value = 1
    with get_session(lambda: fs):
        response = db.fast_count(query)
        assert response == 1

    assert query_eq(
        mock_session.call_args.args[0],
        select(func.count(1)).select_from(Proposal).filter(Proposal.proposalId == 1),
    )
