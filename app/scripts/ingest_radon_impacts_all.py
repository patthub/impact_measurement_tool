# app/scripts/ingest_radon_impacts_all.py

from __future__ import annotations

import argparse
import asyncio
import logging

from app.connectors.radon import RadonConnector
from app.repositories.impact_repository import ImpactRepository
from app.models import ImpactCaseSchema


logger = logging.getLogger(__name__)


async def ingest_all_impacts(
    kind_code: str,
    page_size: int,
) -> None:
    """
    Pobiera wszystkie impacty z RAD-on dla zadanego kindCode
    i zapisuje je do MongoDB.
    """
    connector = RadonConnector()
    repo = ImpactRepository()

    logger.info(
        "Start ingestu impactów dla kindCode=%s (page_size=%d)",
        kind_code,
        page_size,
    )

    count = 0

    async def save_impact(impact: ImpactCaseSchema) -> None:
        nonlocal count

        # Upewniamy się, że mamy institution_uuid (jeśli model go przewiduje),
        # ale w praktyce ImpactCaseSchema.from_radon_record powinien to już zrobić.
        if not getattr(impact, "institution_uuid", None):
            # próbujemy wyciągnąć z raw, jeśli dostępny
            raw = getattr(impact, "raw", None) or {}
            inst_uuid = raw.get("institutionUuid")
            if inst_uuid:
                impact = ImpactCaseSchema.model_copy(
                    impact,
                    update={"institution_uuid": inst_uuid},
                )

        try:
            await repo.save_one(impact)
            count += 1
            if count % page_size == 0:
                logger.info("Zapisano łącznie %d impactów...", count)
        except ValueError as e:
            # np. jeśli source_record_id jest puste i repo nie może wygenerować _id
            logger.warning("Pominięto impact z powodu błędu walidacji: %s", e)

    # iter_all_impacts jest synchronicznym generatorem, ale zapis do Mongo jest async
    for impact in connector.iter_all_impacts(
        kind_code=kind_code,
        page_size=page_size,
    ):
        await save_impact(impact)

    logger.info(
        "Zakończono ingest wszystkich impactów dla kindCode=%s. Łącznie zapisano %d dokumentów.",
        kind_code,
        count,
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Ingest wszystkich impactów z RAD-on (po kindCode) do MongoDB."
    )
    parser.add_argument(
        "--kind-code",
        type=str,
        default="1",
        help="Wartość parametru kindCode (domyślnie: 1).",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=50,
        help="Liczba rekordów pobierana w jednym wywołaniu API RAD-on.",
    )

    args = parser.parse_args()

    await ingest_all_impacts(
        kind_code=args.kind_code,
        page_size=args.page_size,
    )


if __name__ == "__main__":
    asyncio.run(main())
