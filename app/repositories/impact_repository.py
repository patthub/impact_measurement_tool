# app/repositories/impact_repository.py

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from app.db.mongo import db
from app.models import ImpactCaseSchema


class ImpactRepository:
    """
  
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
        doc["_id"] = impact.source_record_id
        doc["fetched_at"] = datetime.utcnow()

        # Motor jest asynchroniczny → trzeba await
        await self.collection.update_one(
            {"_id": doc["_id"]},
            {"$set": doc},
            upsert=True,
        )

    async def save_many(self, impacts: Iterable[ImpactCaseSchema]) -> None:
        """

        """
        for impact in impacts:
            await self.save_one(impact)
