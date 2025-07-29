from unittest.mock import patch

import pytest
from tests.mocks import FakeSession

from lims_utils.database import Database, get_session

db = Database()
fs = FakeSession()


def test_no_session():
    """Should raise exception if there is no session present"""
    with pytest.raises(Exception):
        db.session


@patch.object(fs, "close")
def test_session(mock_session):
    """Should not raise exception if there is a session present in the context"""

    with get_session(lambda: fs):
        db.session

    assert mock_session.called


@patch.object(fs, "rollback")
def test_rollback(mock_session):
    """Should rollback if unhandled exception occurs whilst in session context"""
    with pytest.raises(Exception):
        with get_session(lambda: fs):
            db.session
            raise Exception

    assert mock_session.called
