
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class ColumnClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column_index: int = Field(ge=0)

    category: Literal[
        "tattoo_premises",
        "tattoo_practitioners",
        "combined_premises_and_practitioners",
        "other",
        "unknown"
    ]

    description: str


class TableClassification(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columns: list[ColumnClassification]

    metric_type: Literal[
        "active_register_total",
        "new_registrations",
        "applications",
        "other",
        "unknown"
    ]

    review_required: bool = False
    review_reason: str | None = None
