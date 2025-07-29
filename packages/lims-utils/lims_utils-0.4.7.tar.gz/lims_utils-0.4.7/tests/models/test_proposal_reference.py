import pytest
from pydantic import ValidationError

from lims_utils.models import ProposalReference, parse_proposal


def test_proposal_reference():
    """Should create proposal reference"""
    proposal_reference = parse_proposal("cm123")

    assert proposal_reference.code == "cm"
    assert proposal_reference.number == 123


def test_proposal_reference_visit_number():
    """Should create proposal reference with visit number"""
    proposal_reference = parse_proposal("cm123", 1)

    assert proposal_reference.code == "cm"
    assert proposal_reference.number == 123
    assert proposal_reference.visit_number == 1


def test_proposal_reference_code_not_alpha():
    """Should raise error if code contains numeric characters"""
    with pytest.raises(ValidationError):
        parse_proposal("c0123")


def test_proposal_reference_number_not_digit():
    """Should raise error if number contains non-numeric characters"""
    with pytest.raises(ValidationError):
        parse_proposal("c01a3", 1)


def test_proposal_reference_too_short():
    """Should raise error if proposal reference is too short"""
    with pytest.raises(ValueError):
        parse_proposal("c", 1)


def test_string():
    """Should provide conversion to string"""
    str(ProposalReference(code="cm", number=1)) == "cm1"


def test_string_with_visit():
    """Should provide conversion to string (with visit number)"""
    str(ProposalReference(code="cm", number=1, visit_number=5)) == "cm1-5"
