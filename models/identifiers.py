from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class IdentifierType(str, Enum):
    """Type of identifier used in the system."""

    DOI = "doi"
    ORCID = "orcid"
    GRANT_ID = "grant_id"
    INTERNAL = "internal"
    OTHER = "other"


class IdentifierSchema(BaseModel):
    """
    One identifier for an entity or a scientific product
    (e.g. DOI, ORCID, internal system ID).
    """

    type: IdentifierType
    value: str
