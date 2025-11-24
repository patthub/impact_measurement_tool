from __future__ import annotations

from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from .entities import EntityType
from .identifiers import IdentifierSchema
from .beneficiaries import BeneficiarySchema


class ScientificProductType(str, Enum):
    """
    General category of a scientific product.
    Clusters many detailed FaBiO classes into a small set.
    """

    TEXT_PUBLICATION = "text_publication"        # articles, books, chapters, reports…
    DATASET = "dataset"                          # datasets, data files, tables…
    SOFTWARE = "software"                        # code, tools, scripts…
    PRESENTATION = "presentation"                # talks, conference presentations, posters…
    EDUCATIONAL_RESOURCE = "educational_resource" # syllabi, course materials, learning objects…
    MULTIMEDIA = "multimedia"                    # video, audio, images…
    OTHER = "other"


class ScientificProductSchema(BaseModel):
    """
    One scientific product linked to an assessed entity:
    publication, dataset, software, presentation, teaching material, etc.
    This is the main input object for analysis in IMeTo.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    # Who it belongs to
    entity_id: str = Field(
        description="ID of the assessed entity this product belongs to."
    )
    entity_type: EntityType = Field(
        description="person / team / institution"
    )

    # General type + optional detailed FaBiO mapping
    product_type: ScientificProductType = Field(
        description="High-level category of the product."
    )
    fabio_types: List[str] = Field(
        default_factory=list,
        description=(
            "Optional list of FaBiO classes, e.g. 'fabio:JournalArticle', "
            "'fabio:BookChapter'."
        ),
    )

    # Basic metadata
    title: str = Field(
        description="Title or name of the product."
    )
    summary: Optional[str] = Field(
        default=None,
        description="Short abstract or summary, if available.",
    )
    year: Optional[int] = Field(
        default=None,
        description="Year when it was published/created.",
    )
    language: Optional[str] = Field(
        default=None,
        description="Language code, e.g. 'en', 'pl'.",
    )

    identifiers: List[IdentifierSchema] = Field(
        default_factory=list,
        description="DOI, internal IDs, grant numbers, etc.",
    )

    # Text for analysis
    raw_content: Optional[str] = Field(
        default=None,
        description="Full text (or main body) used for analysis.",
    )
    chunks: List[str] = Field(
        default_factory=list,
        description="Text chunks prepared for vector search / LLM.",
    )

    # Who benefits from this product
    beneficiaries: List[BeneficiarySchema] = Field(
        default_factory=list,
        description="Beneficiaries related to this specific product or activity.",
    )
