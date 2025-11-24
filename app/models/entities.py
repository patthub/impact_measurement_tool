from __future__ import annotations

from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .identifiers import IdentifierSchema


class EntityType(str, Enum):
    """What kind of entity is being evaluated."""

    PERSON = "person"
    TEAM = "team"
    INSTITUTION = "institution"


class AssessedEntitySchema(BaseModel):
    """
    Entity being evaluated in IMeTo:
    an individual researcher, a research team, or an institution.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    entity_type: EntityType = Field(
        description="person / team / institution"
    )
    name: str = Field(
        description="Full name, team name, or institution name."
    )
    affiliation: Optional[str] = Field(
        default=None,
        description="Higher-level affiliation, e.g. faculty or institute.",
    )
    identifiers: List[IdentifierSchema] = Field(
        default_factory=list,
        description="Identifiers such as ORCID, POL-on ID, internal IDs, etc.",
    )
