# app/repositories/impact_repository.py

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from app.db.mongo import db
from app.models import ImpactCaseSchema

logger = logging.getLogger(__name__)


class ImpactRepository:
    """
    Repozytorium do pracy z kolekcją impactów z RAD-on w MongoDB.

    Domyślna kolekcja: `radon_impacts`.
    """

    def __init__(self, collection_name: str = "radon_impacts") -> None:
        self.collection: AsyncIOMotorCollection = db[collection_name]

    # ================== ZAPIS ==================

    async def save_one(self, impact: ImpactCaseSchema) -> None:
        """
        Zapisuje jeden opis wpływu w trybie upsert.

        Kluczem logicznym jest `impact_uuid` (jeśli istnieje w modelu),
        a jeśli go nie ma – `source_record_id`.

        Dzięki temu ponowny ingest nie duplikuje dokumentów.
        """
        doc: Dict[str, Any] = impact.model_dump()

        # Preferujemy impact_uuid jako klucz, jeśli jest w modelu
        impact_uuid: Optional[str] = doc.get("impact_uuid") or doc.get("impactUuid")
        source_record_id: Optional[str] = doc.get("source_record_id")

        if not impact_uuid and not source_record_id:
            # Ostateczna próba – wyciągnąć z raw, jeśli jest
            raw = doc.get("raw") or {}
            impact_uuid = raw.get("impactUuid") or raw.get("impact_uuid")

        if not impact_uuid and not source_record_id:
            raise ValueError(
                "Nie można zapisać impactu: brak zarówno impact_uuid, jak i source_record_id."
            )

        # Budujemy filtr upsert
        if impact_uuid:
            filter_doc = {"impact_uuid": impact_uuid}
        else:
            filter_doc = {"source_record_id": source_record_id}

        # Usuwamy ewentualne _id z poprzedniego odczytu, żeby MongoDB się nie buntowało
        doc.pop("_id", None)

        result = await self.collection.update_one(
            filter_doc,
            {"$set": doc},
            upsert=True,
        )
        logger.debug(
            "Zapisano impact (upsert) – matched: %s, modified: %s, upserted_id: %s",
            result.matched_count,
            result.modified_count,
            result.upserted_id,
        )

    # ================== ODCZYT – LISTA ==================

    async def list_impacts(
        self,
        skip: int = 0,
        limit: int = 50,
        institution_uuid: Optional[str] = None,
        discipline_code: Optional[str] = None,
    ) -> List[ImpactCaseSchema]:
        """
        Zwraca listę impactów z opcjonalnym filtrowaniem po:
        - institution_uuid
        - discipline_code

        Używane przez endpoint GET /impacts.
        """
        query: Dict[str, Any] = {}

        if institution_uuid:
            query["institution_uuid"] = institution_uuid

        if discipline_code:
            query["discipline_code"] = discipline_code

        cursor = (
            self.collection.find(query)
            .skip(skip)
            .limit(limit)
        )

        docs = await cursor.to_list(length=limit)

        impacts: List[ImpactCaseSchema] = []
        for doc in docs:
            # Usuwamy _id, aby Pydantic nie miał problemu z ObjectId
            doc.pop("_id", None)
            try:
                impacts.append(ImpactCaseSchema.model_validate(doc))
            except Exception as e:
                logger.warning("Nie udało się zmapować dokumentu na ImpactCaseSchema: %s", e)

        return impacts

    # ================== ODCZYT – PO UUID ==================

    async def get_by_impact_uuid(self, impact_uuid: str) -> Optional[ImpactCaseSchema]:
        """
        Zwraca pojedynczy impact na podstawie pola impact_uuid.
        """
        doc = await self.collection.find_one({"impact_uuid": impact_uuid})
        if not doc:
            return None

        doc.pop("_id", None)
        try:
            return ImpactCaseSchema.model_validate(doc)
        except Exception as e:
            logger.error(
                "Błąd walidacji ImpactCaseSchema dla impact_uuid=%s: %s",
                impact_uuid,
                e,
            )
            return None

    # ================== ODCZYT – LICZENIE ==================

    async def count(self, institution_uuid: Optional[str] = None) -> int:
        """
        Zlicza impacty (opcjonalnie tylko dla danej instytucji).
        """
        query: Dict[str, Any] = {}
        if institution_uuid:
            query["institution_uuid"] = institution_uuid

        return await self.collection.count_documents(query)
