# app/scripts/ingest_radon_impacts.py

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path
from typing import List

from app.connectors.radon import RadonConnector
from app.repositories.impact_repository import ImpactRepository
from app.models import ImpactCaseSchema

logger = logging.getLogger(__name__)


def load_institutions_from_file(path: str) -> List[str]:
    """
    Wczytuje listę UUID-ów instytucji z pliku tekstowego.

    Zakładamy format:
        uuid1,uuid2,uuid3,...

    Spacje wokół elementów są obcinane.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Institutions file not found: {file_path}")

    content = file_path.read_text(encoding="utf-8")
    uuids = [item.strip() for item in content.split(",") if item.strip()]
    return uuids


async def ingest_for_institution(
    institution_uuid: str,
    connector: RadonConnector,
    repo: ImpactRepository,
    page_size: int = 50,
) -> None:
    """
    Pobiera wszystkie impacty dla instytucji wskazanej przez jej UUID
    i zapisuje je do MongoDB.
    """
    logger.info("Start ingestu impactów dla institutionUuid: %s", institution_uuid)

    count = 0

    for impact in connector.iter_impacts_for_institution(
        institution_uuid=institution_uuid,
        page_size=page_size,
    ):
        # Jeśli z jakiegoś powodu w rekordzie nie był ustawiony institution_uuid,
        # uzupełniamy go wartością, po której pytaliśmy.
        if not getattr(impact, "institution_uuid", None):
            impact = ImpactCaseSchema.model_copy(
                impact,
                update={"institution_uuid": institution_uuid},
            )

        await repo.save_one(impact)
        count += 1

        if count % page_size == 0:
            logger.info(
                "Zapisano %d impactów dla institutionUuid: %s",
                count,
                institution_uuid,
            )

    logger.info(
        "Zakończono ingest. Łącznie %d impactów dla institutionUuid: %s",
        count,
        institution_uuid,
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Ingest impactów z RAD-on do MongoDB dla wielu instytucji (po UUID)."
    )
    parser.add_argument(
        "--institutions-file",
        type=str,
        required=True,
        help="Ścieżka do pliku .txt z listą institutionUuid (oddzielonych przecinkami).",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=50,
        help="Liczba rekordów pobierana w jednym wywołaniu API RAD-on.",
    )

    args = parser.parse_args()

    institutions = load_institutions_from_file(args.institutions_file)
    logger.info(
        "Wczytano %d institutionUuid z pliku: %s",
        len(institutions),
        args.institutions_file,
    )

    connector = RadonConnector()
    repo = ImpactRepository()

    for inst_uuid in institutions:
        await ingest_for_institution(
            institution_uuid=inst_uuid,
            connector=connector,
            repo=repo,
            page_size=args.page_size,
        )


if __name__ == "__main__":
    asyncio.run(main())
