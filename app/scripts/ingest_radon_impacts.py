# app/scripts/ingest_radon_impacts.py

from __future__ import annotations

import asyncio
import logging

from app.connectors.radon import RadonConnector
from app.repositories.impact_repository import ImpactRepository


logger = logging.getLogger(__name__)


async def ingest_for_institution(institution_name: str, page_size: int = 50) -> None:
    """
    Pobiera wszystkie impacty dla podanej instytucji z RAD-on
    i zapisuje je do MongoDB.
    """
    connector = RadonConnector()
    repo = ImpactRepository()

    count = 0
    logger.info("Start ingestu impactów dla instytucji: %s", institution_name)

    # iter_impacts_for_institution jest synchronicznym generatorem
    for impact in connector.iter_impacts_for_institution(
        institution_name=institution_name,
        page_size=page_size,
    ):
        await repo.save_one(impact)
        count += 1
        if count % page_size == 0:
            logger.info("Zapisano %d impactów dla %s", count, institution_name)

    logger.info("Zakończono ingest. Łącznie %d impactów dla instytucji: %s", count, institution_name)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    # Na początek: jedna instytucja, np. UW
    institution = "Uniwersytet Warszawski"
    await ingest_for_institution(institution_name=institution, page_size=50)


if __name__ == "__main__":
    asyncio.run(main())
