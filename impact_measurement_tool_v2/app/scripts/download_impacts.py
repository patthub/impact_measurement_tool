# app/scripts/download_impacts.py
"""
Pobiera impacty z RAD-on i zapisuje lokalnie do JSON i/lub CSV.
Nie wymaga MongoDB — działa czysto offline po pobraniu danych.

Użycie:
    # Wszystkie impacty (kindCode=1), zapis do JSON:
    python -m app.scripts.download_impacts --output impacts.json

    # Wszystkie impacty, zapis do CSV:
    python -m app.scripts.download_impacts --output impacts.csv

    # Tylko dla konkretnych instytucji (z pliku):
    python -m app.scripts.download_impacts --institutions-file app/data/institutions.txt --output impacts.json

    # Ograniczenie liczby rekordów (do testów):
    python -m app.scripts.download_impacts --max-records 100 --output test_impacts.json

    # Zmiana kindCode:
    python -m app.scripts.download_impacts --kind-code 2 --output impacts_kind2.json
"""

from __future__ import annotations

import argparse
import json
import csv
import logging
import sys
from pathlib import Path
from typing import List, Optional

from app.connectors.radon import RadonConnector
from app.models import ImpactCaseSchema

logger = logging.getLogger(__name__)


def load_institutions_from_file(path: str) -> List[str]:
    """Wczytuje UUID-y instytucji z pliku (oddzielone przecinkami)."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Nie znaleziono pliku: {file_path}")
    content = file_path.read_text(encoding="utf-8")
    return [item.strip() for item in content.split(",") if item.strip()]


def download_all_impacts(
    connector: RadonConnector,
    kind_code: str = "1",
    page_size: int = 50,
    max_records: Optional[int] = None,
) -> List[ImpactCaseSchema]:
    """Pobiera wszystkie impacty po kindCode."""
    impacts: List[ImpactCaseSchema] = []

    for impact in connector.iter_all_impacts(
        kind_code=kind_code,
        page_size=page_size,
    ):
        impacts.append(impact)

        if len(impacts) % page_size == 0:
            logger.info("Pobrano %d rekordów...", len(impacts))

        if max_records and len(impacts) >= max_records:
            logger.info("Osiągnięto limit %d rekordów.", max_records)
            break

    return impacts


def download_impacts_for_institutions(
    connector: RadonConnector,
    institution_uuids: List[str],
    page_size: int = 50,
    max_records: Optional[int] = None,
) -> List[ImpactCaseSchema]:
    """Pobiera impacty dla listy instytucji (po UUID)."""
    impacts: List[ImpactCaseSchema] = []

    for i, uuid in enumerate(institution_uuids, 1):
        logger.info(
            "Instytucja %d/%d: %s", i, len(institution_uuids), uuid
        )

        for impact in connector.iter_impacts_for_institution(
            institution_uuid=uuid,
            page_size=page_size,
        ):
            impacts.append(impact)

            if max_records and len(impacts) >= max_records:
                logger.info("Osiągnięto limit %d rekordów.", max_records)
                return impacts

        logger.info(
            "Instytucja %s — łącznie pobrano dotychczas %d rekordów.",
            uuid, len(impacts),
        )

    return impacts


def save_json(impacts: List[ImpactCaseSchema], path: Path) -> None:
    """Zapisuje impacty do JSON (bez pola 'raw' — żeby plik nie był ogromny)."""
    data = [impact.model_dump(exclude={"raw"}) for impact in impacts]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Zapisano %d rekordów do %s", len(data), path)


def save_json_full(impacts: List[ImpactCaseSchema], path: Path) -> None:
    """Zapisuje impacty do JSON z pełnym polem 'raw'."""
    data = [impact.model_dump() for impact in impacts]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Zapisano %d rekordów (z raw) do %s", len(data), path)


def save_csv(impacts: List[ImpactCaseSchema], path: Path) -> None:
    """Zapisuje impacty do CSV (bez pola 'raw')."""
    if not impacts:
        logger.warning("Brak danych do zapisania.")
        return

    fieldnames = [
        "source_record_id",
        "institution_name",
        "institution_uuid",
        "evaluation_year",
        "discipline_name",
        "discipline_code",
        "domain_name",
        "domain_code",
        "title_pl",
        "title_en",
        "summary_pl",
        "summary_en",
        "impact_description_pl",
        "impact_description_en",
        "main_conclusion_pl",
        "main_conclusion_en",
        "impact_areas",
        "other_impact_area",
        "is_interdisciplinary",
        "interdisciplinarity_characteristic_pl",
        "interdisciplinarity_characteristic_en",
        "data_source",
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for impact in impacts:
            row = impact.model_dump(exclude={"raw"})
            # impact_areas to lista — zamieniamy na string
            row["impact_areas"] = "; ".join(row.get("impact_areas") or [])
            writer.writerow(row)

    logger.info("Zapisano %d rekordów do %s", len(impacts), path)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Pobierz impacty z RAD-on i zapisz lokalnie (JSON/CSV)."
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Ścieżka pliku wyjściowego (.json lub .csv).",
    )
    parser.add_argument(
        "--institutions-file",
        type=str,
        default=None,
        help="Plik z UUID-ami instytucji. Jeśli nie podano, pobiera wszystkie po kindCode.",
    )
    parser.add_argument(
        "--kind-code",
        type=str,
        default="1",
        help="Wartość kindCode (domyślnie: 1). Używane gdy nie podano --institutions-file.",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=50,
        help="Liczba rekordów na stronę (domyślnie: 50).",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        default=None,
        help="Maksymalna liczba rekordów do pobrania (do testów).",
    )
    parser.add_argument(
        "--include-raw",
        action="store_true",
        help="Dołącz pełne surowe rekordy z API (tylko JSON).",
    )

    args = parser.parse_args()

    output_path = Path(args.output)
    suffix = output_path.suffix.lower()

    if suffix not in (".json", ".csv"):
        print(f"Nieobsługiwany format: {suffix}. Użyj .json lub .csv.")
        sys.exit(1)

    connector = RadonConnector()

    # Pobieranie danych
    if args.institutions_file:
        uuids = load_institutions_from_file(args.institutions_file)
        logger.info("Wczytano %d UUID-ów instytucji.", len(uuids))
        impacts = download_impacts_for_institutions(
            connector=connector,
            institution_uuids=uuids,
            page_size=args.page_size,
            max_records=args.max_records,
        )
    else:
        logger.info("Pobieranie wszystkich impactów (kindCode=%s)...", args.kind_code)
        impacts = download_all_impacts(
            connector=connector,
            kind_code=args.kind_code,
            page_size=args.page_size,
            max_records=args.max_records,
        )

    logger.info("Pobrano łącznie %d impactów.", len(impacts))

    # Zapis
    if suffix == ".json":
        if args.include_raw:
            save_json_full(impacts, output_path)
        else:
            save_json(impacts, output_path)
    elif suffix == ".csv":
        save_csv(impacts, output_path)

    print(f"\nGotowe! Zapisano {len(impacts)} rekordów → {output_path}")


if __name__ == "__main__":
    main()
