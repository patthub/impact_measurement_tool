# app/connectors/radon.py
# Based on: https://github.com/OPI-PIB/Radon-api/blob/main/Radon_API_Basics_pl.ipynb

from __future__ import annotations

import logging
from typing import Any, Optional, Dict

import requests
from requests import RequestException

from app.connectors.base import BaseConnector
from app.models import IdentifierSchema
from app.models import InstitutionEvaluationSchema


logger = logging.getLogger(__name__)


class RadonConnector(BaseConnector):
    """
    API connector for the RAD-on open data services.

    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        super().__init__(api_key=api_key, base_url=base_url)

        self.base_url = base_url or "https://radon.nauka.gov.pl/opendata"



    def search(self, query: str, top_k: int = 10, **kwargs: Any) -> list[dict]:
        """
        Search by query - todo
        """
        raise NotImplementedError

    def search_by_id(self, identifier: IdentifierSchema, **kwargs: Any) -> list[dict]:
        """
        Search by identifier - todo

        """
        raise NotImplementedError

    def evaluation_search_raw(
        self,
        institution_name: str,
        result_numbers: int = 10,
        token: str = "",
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """
        RAW request to RAD-on evaluations API.:
        GET /polon/evaluations?institutionName=...&resultNumbers=...&token=...

        Example:
        https://radon.nauka.gov.pl/opendata/polon/evaluations?resultNumbers=10&token=...&institutionName=Uniwersytet%20Warszawski
        """
        url = f"{self.base_url.rstrip('/')}/polon/evaluations"

        params = {
            "institutionName": institution_name,
            "resultNumbers": result_numbers,
        }

        # token jest pusty przy pierwszym wywołaniu
        if token:
            params["token"] = token

        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.exception(
                "Error calling RAD-on evaluations for institution %s", institution_name
            )
            return {}

        try:
            data: Dict[str, Any] = response.json()
        except ValueError:
            logger.error("RAD-on evaluations returned non-JSON response")
            return {}

        return data
    def evaluation_for_institution(
        self,
        institution_name: str,
        result_numbers: int = 10,
        timeout: float = 10.0,
    ) -> Optional[InstitutionEvaluationSchema]:
        """
        Get evaluation for institution
        """
        raw = self.evaluation_search_raw(
            institution_name=institution_name,
            result_numbers=result_numbers,
            timeout=timeout,
        )

        if not isinstance(raw, dict):
            return None

        results = raw.get("results", []) or []
        if not results:
            return None

        first = results[0]
        if not isinstance(first, dict):
            return None

        return InstitutionEvaluationSchema.from_radon_record(first)

if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)

    connector = RadonConnector()

    institution = "Uniwersytet Warszawski"
    print(f"\n=== Test ewaluacji RAD-on dla instytucji: {institution} ===")

    # Krok 1: pobranie surowych danych z API
    raw = connector.evaluation_search_raw(institution_name=institution, result_numbers=10)
    print("\n--- Surowe klucze JSON ---")
    print(list(raw.keys()))

    # Krok 2: zamiana surowego rekordu na Pydantic schema
    from app.models import InstitutionEvaluationSchema

    results = raw.get("results", [])
    if not results:
        print("Brak wyników w API.")
        exit()

    first_record = results[0]
    evaluation = InstitutionEvaluationSchema.from_radon_record(first_record)

    # Krok 3: wypisanie pełnych danych (bez obcinania!)
    print("\n=== Wynik Pydantic ===")
    print(evaluation.model_dump())

    # Krok 4: test funkcji pomocniczych
    print("\n--- Kategorie ---")
    print(evaluation.categories_summary())

    print("\n--- Grupowanie po dziedzinach ---")
    for domain, discs in evaluation.disciplines_by_domain().items():
        print(f"{domain} → {len(discs)} dyscyplin")

    print("\n--- Łączna liczba dyscyplin ---")
    print(evaluation.total_disciplines)
