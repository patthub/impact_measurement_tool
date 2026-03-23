# app/models/impact_case.py

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Pojedynczy dowód wpływu (impactEvidence)."""

    description_pl: Optional[str] = Field(
        default=None,
        description="Opis dowodu wpływu po polsku (pole 'descriptionPl').",
    )
    description_en: Optional[str] = Field(
        default=None,
        description="Opis dowodu wpływu po angielsku (pole 'descriptionEn').",
    )


class AchievementItem(BaseModel):
    """Pojedyncze osiągnięcie naukowe (achievements)."""

    bibliographic_description_pl: Optional[str] = Field(
        default=None,
        description="Opis bibliograficzny po polsku (pole 'bibliographicDescriptionPl').",
    )
    bibliographic_description_en: Optional[str] = Field(
        default=None,
        description="Opis bibliograficzny po angielsku (pole 'bibliographicDescriptionEn').",
    )
    summary_pl: Optional[str] = Field(
        default=None,
        description="Streszczenie osiągnięcia po polsku (pole 'summaryPl').",
    )
    summary_en: Optional[str] = Field(
        default=None,
        description="Streszczenie osiągnięcia po angielsku (pole 'summaryEn').",
    )


class ImpactCaseSchema(BaseModel):
    """
    Jeden case impactu (opis wpływu) pobrany z RAD-on / POL-on.

    Pokrywa wszystkie 33 pola zwracane przez endpoint /polon/impacts.
    """

    # Identyfikacja
    impact_uuid: Optional[str] = Field(
        default=None,
        description="UUID impactu w RAD-on (pole 'impactUuid').",
    )
    institution_name: Optional[str] = Field(
        default=None,
        description="Nazwa instytucji, do której przypisany jest impact.",
    )
    institution_uuid: Optional[str] = Field(
        default=None,
        description="UUID instytucji z POL-on / RAD-on.",
    )

    # Ewaluacja / dyscyplina
    evaluation_year: Optional[int] = Field(
        default=None,
        description="Rok ewaluacji (pole 'evaluationYear').",
    )
    discipline_name: Optional[str] = None
    discipline_code: Optional[str] = None
    domain_name: Optional[str] = None
    domain_code: Optional[str] = None

    # Rodzaj
    kind_code: Optional[str] = None
    kind_name: Optional[str] = None
    detailed_kind: Optional[str] = None

    # Tytuły i streszczenia
    title_pl: Optional[str] = None
    title_en: Optional[str] = None
    summary_pl: Optional[str] = None
    summary_en: Optional[str] = None

    # Opisy pełne
    impact_description_pl: Optional[str] = None
    impact_description_en: Optional[str] = None
    main_conclusion_pl: Optional[str] = None
    main_conclusion_en: Optional[str] = None

    # Dowody wpływu (evidence of impact)
    impact_evidence: List[EvidenceItem] = Field(
        default_factory=list,
        description="Lista dowodów wpływu (pole 'impactEvidence').",
    )

    # Osiągnięcia naukowe
    achievements: List[AchievementItem] = Field(
        default_factory=list,
        description="Lista osiągnięć naukowych (pole 'achievements').",
    )

    # Podmiot
    entity_name_pl: Optional[str] = None
    entity_name_en: Optional[str] = None
    entity_role_pl: Optional[str] = None
    entity_role_en: Optional[str] = None

    # Obszary impactu
    impact_areas: List[str] = Field(default_factory=list)
    other_impact_area: Optional[str] = None

    # Interdyscyplinarność
    is_interdisciplinary: Optional[bool] = None
    interdisciplinarity_characteristic_pl: Optional[str] = None
    interdisciplinarity_characteristic_en: Optional[str] = None

    # Metadane
    data_source: Optional[str] = None
    last_refresh: Optional[str] = None

    # Pełny rekord źródłowy
    raw: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_radon_record(cls, record: Dict[str, Any]) -> "ImpactCaseSchema":
        """Tworzy ImpactCaseSchema z pojedynczego rekordu RAD-on."""
        evaluation_year: Optional[int] = None
        evaluation_year_raw = record.get("evaluationYear")
        if evaluation_year_raw is not None:
            try:
                evaluation_year = int(str(evaluation_year_raw))
            except ValueError:
                pass

        impact_areas_raw = record.get("impactArea") or []
        if isinstance(impact_areas_raw, list):
            impact_areas = [str(a) for a in impact_areas_raw]
        else:
            impact_areas = [str(impact_areas_raw)]

        evidence_items: List[EvidenceItem] = []
        for ev in (record.get("impactEvidence") or []):
            if isinstance(ev, dict):
                evidence_items.append(EvidenceItem(
                    description_pl=ev.get("descriptionPl"),
                    description_en=ev.get("descriptionEn"),
                ))

        achievement_items: List[AchievementItem] = []
        for ach in (record.get("achievements") or []):
            if isinstance(ach, dict):
                achievement_items.append(AchievementItem(
                    bibliographic_description_pl=ach.get("bibliographicDescriptionPl"),
                    bibliographic_description_en=ach.get("bibliographicDescriptionEn"),
                    summary_pl=ach.get("summaryPl"),
                    summary_en=ach.get("summaryEn"),
                ))

        return cls(
            impact_uuid=record.get("impactUuid"),
            institution_name=record.get("institutionName"),
            institution_uuid=record.get("institutionUuid"),
            evaluation_year=evaluation_year,
            discipline_name=record.get("disciplineName"),
            discipline_code=record.get("disciplineCode"),
            domain_name=record.get("domainName"),
            domain_code=record.get("domainCode"),
            kind_code=record.get("kindCode"),
            kind_name=record.get("kindName"),
            detailed_kind=record.get("detailedKind"),
            title_pl=record.get("titlePl"),
            title_en=record.get("titleEn"),
            summary_pl=record.get("summaryPl"),
            summary_en=record.get("summaryEn"),
            impact_description_pl=record.get("impactDescriptionPl"),
            impact_description_en=record.get("impactDescriptionEn"),
            main_conclusion_pl=record.get("mainConclusionPl"),
            main_conclusion_en=record.get("mainConclusionEn"),
            impact_evidence=evidence_items,
            achievements=achievement_items,
            entity_name_pl=record.get("entityNamePl"),
            entity_name_en=record.get("entityNameEn"),
            entity_role_pl=record.get("entityRolePl"),
            entity_role_en=record.get("entityRoleEn"),
            impact_areas=impact_areas,
            other_impact_area=record.get("otherImpactArea"),
            is_interdisciplinary=record.get("isInterdisciplinary"),
            interdisciplinarity_characteristic_pl=record.get("interdisciplinarityCharacteristicPl"),
            interdisciplinarity_characteristic_en=record.get("interdisciplinarityCharacteristicEn"),
            data_source=record.get("dataSource"),
            last_refresh=record.get("lastRefresh"),
            raw=record,
        )


class InstitutionImpactSetSchema(BaseModel):
    """Zestaw impactów powiązanych z jedną instytucją."""

    institution_name: Optional[str] = None
    cases: List[ImpactCaseSchema] = Field(default_factory=list)

    @classmethod
    def from_radon_response(cls, response: Dict[str, Any]) -> "InstitutionImpactSetSchema":
        results = response.get("results", []) or []
        cases: List[ImpactCaseSchema] = []
        institution_name: Optional[str] = None

        for r in results:
            if not isinstance(r, dict):
                continue
            case = ImpactCaseSchema.from_radon_record(r)
            cases.append(case)
            if case.institution_name and institution_name is None:
                institution_name = case.institution_name

        return cls(institution_name=institution_name, cases=cases)
