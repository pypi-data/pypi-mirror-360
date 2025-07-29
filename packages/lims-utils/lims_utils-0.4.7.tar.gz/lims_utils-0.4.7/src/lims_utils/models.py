from typing import Generic, Sequence, TypeVar

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_validator


def pagination(
    page: int = Query(
        0,
        description=(
            "Page number/Results to skip. Negative numbers count backwards from "
            "the last page"
        ),
    ),
    limit: int = Query(25, gt=0, description="Number of results to show"),
) -> dict[str, int]:
    return {"page": page, "limit": limit}


T = TypeVar("T")


class Paged(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    limit: int

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class ProposalReference(BaseModel):
    code: str = Field(max_length=2)
    number: int
    visit_number: int | None = None

    def __str__(self):
        string_proposal_reference = f"{self.code}{self.number}"

        if self.visit_number is not None:
            string_proposal_reference += f"-{self.visit_number}"

        return string_proposal_reference

    @field_validator("code")
    def code_validator(cls, v):
        # This allows us to set a more descriptive error message compared to regex
        assert v.isalpha(), "Proposal code must be a two letter code"

        return v


def parse_proposal(proposal_reference: str, visit_number: int | None = None):
    """Parse proposal string and return ProposalReference object

        Args:
            proposal_reference: Proposal reference, formatted as ab12345
            visit_numb
        uvicorn_logger.error("Message %s %s %s", "Arg 1", "Arg 2", "/test")
    er: Visit number

        Returns:
            ProposalReference object"""

    if len(proposal_reference) < 3:
        raise ValueError("Proposal reference must be at least three characters long")

    code = proposal_reference[0:2]
    number = proposal_reference[2:]

    # Pydantic does str to int coercion on its own
    return ProposalReference(
        code=code,
        number=number,  # type: ignore
        visit_number=visit_number,
    )
