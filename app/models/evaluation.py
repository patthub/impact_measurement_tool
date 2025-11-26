# app/models/evaluation.py

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DisciplineEvaluationSchema(BaseModel):
    """
    Wynik ewaluacji dla jednej dyscypliny w danej instytucji i okresie.
    """

    discipline_name: str = Field(description="Nazwa dyscypliny, np. 'historia'.")
    discipline_code: str = Field(description="Kod dyscypliny, np. 'DS010103N'.")
    domain_name: str = Field(description="Nazwa dziedziny, np. 'dziedzina nauk humanistycznych'.")
    domain_code: str = Field(description="Kod dziedziny, np. 'DZ0101N'.")
    category: str = Field(description="Kategoria ewaluacyjna, np. 'A+', 'A', 'B+'.")


class InstitutionEvaluationSchema(BaseModel):
    """
    Podsumowanie ewaluacji instytucji w danym okresie,
    na podstawie danych z RAD-on / POL-on.
    """

    institution_name: str = Field(description="Nazwa instytucji.")
    institution_uuid: str = Field(description="UUID instytucji z POL-on / RAD-on.")
    evaluation_period: str = Field(description="Okres ewaluacji w formacie 'YYYY-YYYY'.")
    period_start: Optional[int] = Field(
        default=None,
        description="Rok początkowy okresu ewaluacji, np. 2017.",
    )
    period_end: Optional[int] = Field(
        default=None,
        description="Rok końcowy okresu ewaluacji, np. 2021.",
    )

    disciplines: List[DisciplineEvaluationSchema] = Field(
        default_factory=list,
        description="Lista dyscyplin wraz z kategoriami.",
    )

    last_refresh: Optional[datetime] = Field(
        default=None,
        description="Znacznik czasu ostatniej aktualizacji danych (jeśli dostępny).",
    )

    data_source: Optional[str] = Field(
        default=None,
        description="Źródło danych, np. 'POLON'.",
    )

    @classmethod
    def from_radon_record(cls, record: dict) -> "InstitutionEvaluationSchema":
        """
        Utworzenie obiektu InstitutionEvaluationSchema z pojedynczego rekordu RAD-on.

        Zakładamy strukturę:
        {
          "evaluationPeriod": "2017-2021",
          "disciplines": [...],
          "lastRefresh": "1747037717779",
          "institutionName": "...",
          "id": "...",
          "institutionUuid": "...",
          "dataSource": "POLON"
        }
        """
        evaluation_period = record.get("evaluationPeriod", "")
        period_start: Optional[int] = None
        period_end: Optional[int] = None

        if "-" in evaluation_period:
            try:
                start_str, end_str = evaluation_period.split("-", 1)
                period_start = int(start_str)
                period_end = int(end_str)
            except ValueError:
                # jeśli format jest inny, po prostu zostawiamy None
                pass

        disciplines_raw = record.get("disciplines", []) or []
        disciplines: list[DisciplineEvaluationSchema] = []

        for d in disciplines_raw:
            if not isinstance(d, dict):
                continue
            disciplines.append(
                DisciplineEvaluationSchema(
                    discipline_name=d.get("disciplineName", ""),
                    discipline_code=d.get("disciplineCode", ""),
                    domain_name=d.get("domainName", ""),
                    domain_code=d.get("domainCode", ""),
                    category=d.get("category", ""),
                )
            )

        last_refresh_raw = record.get("lastRefresh")
        last_refresh_dt: Optional[datetime] = None
        if last_refresh_raw:
            try:
                # lastRefresh wygląda jak timestamp w milisekundach
                ts_ms = int(str(last_refresh_raw))
                last_refresh_dt = datetime.fromtimestamp(ts_ms / 1000.0)
            except (ValueError, OSError):
                # jeśli format będzie inny, zostawiamy None
                pass

        return cls(
            institution_name=record.get("institutionName", ""),
            institution_uuid=record.get("institutionUuid", ""),
            evaluation_period=evaluation_period,
            period_start=period_start,
            period_end=period_end,
            disciplines=disciplines,
            last_refresh=last_refresh_dt,
            data_source=record.get("dataSource"),
        )
