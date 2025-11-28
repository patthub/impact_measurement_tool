# app/repositories/impact_repository.py

from __future__ import annotations

from datetime import datetime

from app.db.mongo import db
from app.models import ImpactCaseSchema


class ImpactRepository:
    """
    Repozytorium do zapisywania impactów z RAD-on w MongoDB.

    - baza: 'imeto'
    - kolekcja: 'radon_impacts'
    - klucz główny: _id = ImpactCaseSchema.source_record_id (impactUuid/id z RAD-on)
    """

    def __init__(self) -> None:
        self.collection = db["radon_impacts"]

    async def save_one(self, impact: ImpactCaseSchema) -> None:
        """
        Zapisuje (lub aktualizuje) jeden case impactu.
        """
        if not impact.source_record_id:
            raise ValueError("ImpactCaseSchema.source_record_id is required for Mongo _id")

        doc = impact.model_dump()

        # Główny klucz unikalny – oparty o impactUuid/id z RAD-on
        doc["_id"] = impact.source_record_id

        # Wygodna kopia impactUuid na górnym poziomie dokumentu
        doc["impactUuid"] = impact.source_record_id

        # Upewniamy się, że institution_name i institution_uuid są jawnie obecne
        doc["institution_name"] = impact.institution_name
        doc["institution_uuid"] = impact.institution_uuid

        doc["fetched_at"] = datetime.utcnow()

        await self.collection.update_one(
            {"_id": doc["_id"]},
            {"$set": doc},
            upsert=True,
        )
