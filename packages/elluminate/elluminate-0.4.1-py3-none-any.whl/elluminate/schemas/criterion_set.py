import warnings
from typing import Any

from pydantic import BaseModel, field_validator

from elluminate.schemas.criterion import Criterion, CriterionIn
from elluminate.schemas.prompt_template import PromptTemplate


class CriterionSet(BaseModel):
    """Criterion set model."""

    id: int
    name: str
    prompt_templates: list[PromptTemplate] | None = None
    criteria: list[Criterion] | None = None


class CreateCriterionSetRequest(BaseModel):
    """Request to create a new criterion set.

    Args:
        name: The name of the criterion set
        criteria: Optional list of criterion strings to create alongside the criterion set

    """

    name: str
    # Allow both list[str] (old) and list[CriterionIn] (new) for backward compatibility
    criteria: list[CriterionIn] | None = None

    @field_validator("criteria", mode="before")
    @classmethod
    def convert_str_criteria(cls, criteria_list: Any) -> Any:
        """Convert list[str] criteria to list[CriterionIn] for backward compatibility."""
        if criteria_list and isinstance(criteria_list[0], str):
            warnings.warn(
                "Support for list[str] criteria is deprecated. Use list[CriterionIn] instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return [CriterionIn(criterion_str=c) for c in criteria_list]
        return criteria_list
