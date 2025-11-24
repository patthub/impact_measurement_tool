from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .entities import EntityType
from .funding import FundingOpportunitySchema


class ImpactDimension(str, Enum):
    """High-level dimension of impact."""

    SCIENTIFIC = "scientific"
    SOCIETAL = "societal"
    POLICY = "policy"
    EDUCATIONAL = "educational"
    ECONOMIC = "economic"
    OTHER = "other"


class ImpactSectionSchema(BaseModel):
    """One section of an impact report."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    content: str
    dimension: Optional[ImpactDimension] = Field(
        default=None,
        description="Which dimension of impact this section belongs to.",
    )


class ImpactReportSchema(BaseModel):
    """
    Impact report for an entity (person, team, institution).

    Contains narrative sections and a list of suggested funding opportunities.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    entity_id: str = Field(
        description="ID of the assessed entity."
    )
    entity_type: EntityType = Field(
        description="person / team / institution"
    )

    # Period covered by this report (optional)
    period_start: Optional[int] = Field(
        default=None,
        description="Start year of the period covered.",
    )
    period_end: Optional[int] = Field(
        default=None,
        description="End year of the period covered.",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this report was generated.",
    )

    sections: List[ImpactSectionSchema] = Field(
        default_factory=list,
        description="Text sections describing different aspects of impact.",
    )

    recommended_funding: List[FundingOpportunitySchema] = Field(
        default_factory=list,
        description="Funding opportunities suggested as relevant for this entity.",
    )
