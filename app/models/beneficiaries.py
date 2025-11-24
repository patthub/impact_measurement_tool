from __future__ import annotations

from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class BeneficiaryCategory(str, Enum):
    """Who benefits (or could benefit) from the activity or product."""

    GENERAL_PUBLIC = "general_public"
    STUDENTS = "students"
    EDUCATORS = "educators"
    POLICY_MAKERS = "policy_makers"
    PUBLIC_ADMINISTRATION = "public_administration"
    CULTURAL_INSTITUTIONS = "cultural_institutions"
    BUSINESS = "business"
    NGOS = "ngos"
    HEALTHCARE_SECTOR = "healthcare_sector"
    INTERNAL_INSTITUTION = "internal_institution"
    OTHER = "other"


class BeneficiarySchema(BaseModel):
    """
    A group or organisation that benefits from a scientific product or activity.
    Can be very general (e.g. 'general public') or more specific.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    category: BeneficiaryCategory = Field(
        description="High-level group, e.g. students, policy makers."
    )

    label: Optional[str] = Field(
        default=None,
        description="Short label, e.g. 'Ministry of Education', 'Local NGOs'.",
    )

    description: Optional[str] = Field(
        default=None,
        description="Optional short description of this beneficiary group.",
    )

    geography: Optional[str] = Field(
        default=None,
        description="Scope: local, regional, national, EU, global, etc.",
    )

    is_intended: bool = Field(
        default=True,
        description="True if this is a target group; False if identified after the fact.",
    )
