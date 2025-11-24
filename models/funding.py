from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class FundingType(str, Enum):
    """General type of funding opportunity."""

    GRANT = "grant"
    FELLOWSHIP = "fellowship"
    INFRASTRUCTURE = "infrastructure"
    NETWORKING = "networking"
    TRAINING = "training"
    OTHER = "other"


class FundingOpportunitySchema(BaseModel):
    """
    One funding opportunity that may be relevant for an assessed entity.
    Returned by IMeTo as a suggestion.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    # Basic info
    title: str = Field(
        description="Name/title of the call or programme."
    )
    funder: Optional[str] = Field(
        default=None,
        description="Funder, e.g. 'NCN', 'European Commission'.",
    )
    programme: Optional[str] = Field(
        default=None,
        description="Programme or scheme, e.g. 'OPUS', 'MSCA Postdoctoral Fellowships'.",
    )
    call_identifier: Optional[str] = Field(
        default=None,
        description="Call code or reference, if available.",
    )

    funding_type: FundingType = Field(
        default=FundingType.GRANT,
        description="General type of funding.",
    )

    # When and where
    deadline: Optional[date] = Field(
        default=None,
        description="Application deadline.",
    )
    country_or_region: Optional[str] = Field(
        default=None,
        description="Main region targeted by the call, e.g. 'PL', 'EU', 'global'.",
    )

    # Budget (optional)
    min_budget: Optional[float] = Field(
        default=None,
        description="Approximate minimum budget, if known.",
    )
    max_budget: Optional[float] = Field(
        default=None,
        description="Approximate maximum budget, if known.",
    )
    currency: Optional[str] = Field(
        default=None,
        description="Currency code, e.g. 'EUR', 'PLN'.",
    )

    # Scope
    description: Optional[str] = Field(
        default=None,
        description="Short description of the call.",
    )
    research_areas: List[str] = Field(
        default_factory=list,
        description="Relevant research areas / fields.",
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Extra keywords that describe this opportunity.",
    )

    # Provenance
    url: Optional[str] = Field(
        default=None,
        description="Link to more information.",
    )
    source_system: Optional[str] = Field(
        default=None,
        description="System that provided this record, e.g. 'HorizonEuropeAPI'.",
    )
    source_record_id: Optional[str] = Field(
        default=None,
        description="ID in the external system.",
    )

    # Why it is suggested
    relevance_score: Optional[float] = Field(
        default=None,
        description="Relevance score for this entity (0–1 or 0–100).",
    )
    relevance_explanation: Optional[str] = Field(
        default=None,
        description="Short explanation why this opportunity was suggested.",
    )
