from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ImpactCaseSchema(BaseModel):
    """
    Jeden case impactu (opis wpływu) pobrany z RAD-on / POL-on.

    Model oparty na rzeczywistym JSON-ie z endpointu /polon/impacts.
    """

    # Identyfikacja
    source_record_id: Optional[str] = Field(
        default=None,
        description="ID rekordu impactu w RAD-on (np. 'impactUuid' lub 'id').",
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
    discipline_name: Optional[str] = Field(
        default=None,
        description="Nazwa dyscypliny przypisanej do impactu (pole 'disciplineName').",
    )
    discipline_code: Optional[str] = Field(
        default=None,
        description="Kod dyscypliny (pole 'disciplineCode').",
    )
    domain_name: Optional[str] = Field(
        default=None,
        description="Nazwa dziedziny (pole 'domainName').",
    )
    domain_code: Optional[str] = Field(
        default=None,
        description="Kod dziedziny (pole 'domainCode', jeśli występuje).",
    )

    # Tytuły i streszczenia
    title_pl: Optional[str] = Field(
        default=None,
        description="Tytuł impactu po polsku (pole 'titlePl').",
    )
    title_en: Optional[str] = Field(
        default=None,
        description="Tytuł impactu po angielsku (pole 'titleEn').",
    )

    summary_pl: Optional[str] = Field(
        default=None,
        description="Streszczenie impactu po polsku (pole 'summaryPl').",
    )
    summary_en: Optional[str] = Field(
        default=None,
        description="Streszczenie impactu po angielsku (pole 'summaryEn').",
    )

    # Opisy pełne
    impact_description_pl: Optional[str] = Field(
        default=None,
        description="Pełny opis impactu po polsku (pole 'impactDescriptionPl').",
    )
    impact_description_en: Optional[str] = Field(
        default=None,
        description="Pełny opis impactu po angielsku (pole 'impactDescriptionEn').",
    )

    main_conclusion_pl: Optional[str] = Field(
        default=None,
        description="Główne wnioski po polsku (pole 'mainConclusionPl').",
    )
    main_conclusion_en: Optional[str] = Field(
        default=None,
        description="Główne wnioski po angielsku (pole 'mainConclusionEn').",
    )

    # Obszary impactu
    impact_areas: List[str] = Field(
        default_factory=list,
        description="Lista ogólnych obszarów impactu (pole 'impactArea').",
    )
    other_impact_area: Optional[str] = Field(
        default=None,
        description="Doprecyzowanie obszaru impactu (pole 'otherImpactArea').",
    )

    # Interdyscyplinarność
    is_interdisciplinary: Optional[bool] = Field(
        default=None,
        description="Czy impact jest interdyscyplinarny (pole 'isInterdisciplinary').",
    )
    interdisciplinarity_characteristic_pl: Optional[str] = Field(
        default=None,
        description="Opis interdyscyplinarności po polsku (pole 'interdisciplinarityCharacteristicPl').",
    )
    interdisciplinarity_characteristic_en: Optional[str] = Field(
        default=None,
        description="Opis interdyscyplinarności po angielsku (pole 'interdisciplinarityCharacteristicEn').",
    )

    # Dodatkowe pola pomocnicze
    data_source: Optional[str] = Field(
        default=None,
        description="Źródło danych, np. 'POLON'.",
    )

    # Pełny rekord źródłowy – nic nie ginie
    raw: Dict[str, Any] = Field(
        default_factory=dict,
        description="Pełny, oryginalny rekord z API RAD-on.",
    )

    @classmethod
    def from_radon_record(cls, record: Dict[str, Any]) -> "ImpactCaseSchema":
        """
        Tworzy ImpactCaseSchema z pojedynczego rekordu RAD-on (/polon/impacts).

        Przykładowy rekord zawiera m.in.:
        - impactDescriptionPl, impactDescriptionEn
        - summaryPl, summaryEn
        - titlePl, titleEn
        - mainConclusionPl, mainConclusionEn
        - impactArea (lista), otherImpactArea
        - disciplineName, disciplineCode, domainName, domainCode
        - evaluationYear
        - impactUuid, institutionName, institutionUuid
        """
        # ID – w JSON-ie masz 'impactUuid' + 'institutionUuid' + 'evaluationYear'
        source_record_id = record.get("impactUuid") or record.get("id")

        # Rok ewaluacji – w JSON-ie 'evaluationYear' jest stringiem
        evaluation_year_raw = record.get("evaluationYear")
        evaluation_year: Optional[int] = None
        if evaluation_year_raw is not None:
            try:
                evaluation_year = int(str(evaluation_year_raw))
            except ValueError:
                evaluation_year = None

        # Obszary impactu
        impact_areas_raw = record.get("impactArea") or []
        impact_areas: List[str] = []
        if isinstance(impact_areas_raw, list):
            impact_areas = [str(a) for a in impact_areas_raw]
        else:
            impact_areas = [str(impact_areas_raw)]

        return cls(
            source_record_id=source_record_id,
            institution_name=record.get("institutionName"),
            institution_uuid=record.get("institutionUuid"),
            evaluation_year=evaluation_year,
            discipline_name=record.get("disciplineName"),
            discipline_code=record.get("disciplineCode"),
            domain_name=record.get("domainName"),
            domain_code=record.get("domainCode"),
            title_pl=record.get("titlePl"),
            title_en=record.get("titleEn"),
            summary_pl=record.get("summaryPl"),
            summary_en=record.get("summaryEn"),
            impact_description_pl=record.get("impactDescriptionPl"),
            impact_description_en=record.get("impactDescriptionEn"),
            main_conclusion_pl=record.get("mainConclusionPl"),
            main_conclusion_en=record.get("mainConclusionEn"),
            impact_areas=impact_areas,
            other_impact_area=record.get("otherImpactArea"),
            is_interdisciplinary=record.get("isInterdisciplinary"),
            interdisciplinarity_characteristic_pl=record.get("interdisciplinarityCharacteristicPl"),
            interdisciplinarity_characteristic_en=record.get("interdisciplinarityCharacteristicEn"),
            data_source=record.get("dataSource"),
            raw=record,
        )


class InstitutionImpactSetSchema(BaseModel):
    """
    Zestaw impactów (opisów wpływu) powiązanych z jedną instytucją.
    """

    institution_name: Optional[str] = Field(
        default=None,
        description="Nazwa instytucji, dla której pobrano impacty.",
    )
    cases: List[ImpactCaseSchema] = Field(
        default_factory=list,
        description="Lista case'ów impactu.",
    )

    @classmethod
    def from_radon_response(cls, response: Dict[str, Any]) -> "InstitutionImpactSetSchema":
        """
        Buduje zestaw impactów z pełnej odpowiedzi API RAD-on
        (słownik zawierający m.in. klucz 'results').
        """
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

        return cls(
            institution_name=institution_name,
            cases=cases,
        )
