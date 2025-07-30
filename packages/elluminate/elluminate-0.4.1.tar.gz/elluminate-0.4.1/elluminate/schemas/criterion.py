import warnings
from datetime import datetime
from typing import Any

from pydantic import BaseModel, field_validator

from elluminate.schemas.prompt_template import PromptTemplate
from elluminate.schemas.template_variables import TemplateVariables


class Criterion(BaseModel):
    """Rating criterion model."""

    id: int
    criterion_str: str
    label: str | None = None
    prompt_template: PromptTemplate | None = None
    template_variables: TemplateVariables | None = None
    created_at: datetime


class CriterionIn(BaseModel):
    """Input schema for creating a criterion."""

    criterion_str: str
    label: str | None = None


class CreateCriteriaRequest(BaseModel):
    """Request to create a new rating criteria.

    This model intentionally supports two mutually exclusive modes of operation:
    1. Manual Entry Mode:
       - Set criteria with your criteria
       - Used for direct creation of criteria

    2. AI Generation Mode:
       - Leave criteria as None
       - Used for AI-powered generation of criteria

    Either prompt_template_id or criterion_set_id must be provided, but not both.
    """

    prompt_template_id: int | None = None
    criterion_set_id: int | None = None
    template_variables_id: int | None = None
    # Allow both list[str] (old) and list[CriterionIn] (new) for backward compatibility
    criteria: list[CriterionIn] | None = None
    delete_existing: bool = False

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
