# app/connectors/radon.py
"""
Connector do API RAD-on (POL-on / RAD-on opendata).

Dokumentacja przykładowa:
- https://radon.nauka.gov.pl/opendata/polon/evaluations
- https://radon.nauka.gov.pl/opendata/polon/impacts
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional

import requests

from app.connectors.base import BaseConnector
from app.models import ImpactCaseSchema, IdentifierSchema

logger = logging.getLogger(__name__)


class RadonConnector(BaseConnector):
    """
    Connector do RAD-on, z funkcjami:
    - pobieranie ewaluacji instytucji,
    - pobieranie opisów wpływu (impacts) po UUID instytucji.

    Dziedziczy po BaseConnector, więc implementuje wymagane metody
    search() i search_by_id(), nawet jeśli są to tylko stuby.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        # base_url bez końcowego /polon – dokładamy w endpointach
        super().__init__(api_key=api_key, base_url=base_url)
        self.base_url = base_url or "https://radon.nauka.gov.pl/opendata"

    # ========= Wymagane metody z BaseConnector =========

    def search(self, query: str, top_k: int = 10, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Ogólne wyszukiwanie (wymagane przez abstrakcyjną klasę BaseConnector).

        W tej chwili nie korzystasz z free-text search w RAD-on, więc metoda
        jest tylko stubbem. Możesz ją zaimplementować później, jeśli będzie
        potrzebna (np. wyszukiwanie instytucji, osób itp.).
        """
        raise NotImplementedError(
            "RadonConnector.search() nie jest obecnie zaimplementowane. "
            "Użyj metod specyficznych, np. get_evaluations() lub iter_impacts_for_institution()."
        )

    def search_by_id(
        self,
        identifier: IdentifierSchema | str,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Wyszukiwanie po identyfikatorze (wymagane przez BaseConnector).

        Również stub – w razie potrzeby można tu dodać logikę wyszukiwania
        np. po identyfikatorze instytucji lub impactUuid.
        """
        raise NotImplementedError(
            "RadonConnector.search_by_id() nie jest obecnie zaimplementowane. "
            "Korzystaj z iter_impacts_for_institution() lub get_evaluations()."
        )

    # ========= EWALUACJE (po nazwie instytucji) =========

    def get_evaluations(
        self,
        institution_name: str,
        result_numbers: int = 10,
        token: str = "",
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Pobiera dane ewaluacyjne dla instytucji po nazwie (institutionName).

        Używane pomocniczo – ingest impactów robimy po UUID instytucji.
        """
        url = f"{self.base_url.rstrip('/')}/polon/evaluations"

        params: Dict[str, Any] = {
            "institutionName": institution_name,
            "resultNumbers": result_numbers,
        }

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
            return response.json()
        except ValueError:
            logger.error("RAD-on evaluations returned non-JSON response")
            return {}

    # ========= IMPACTY (po UUID instytucji) =========

    def get_impact_description(
        self,
        institution_uuid: str,
        result_numbers: int = 10,
        token: str = "",
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Pobiera opisy wpływu (impacts) wyszukując po UUID instytucji
        (parametr institutionUuid w RAD-on).
        """
        url = f"{self.base_url.rstrip('/')}/polon/impacts"

        params: Dict[str, Any] = {
            "institutionUuid": institution_uuid,
            "resultNumbers": result_numbers,
        }

        if token:
            params["token"] = token

        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.exception(
                "Error calling RAD-on impacts for institutionUuid %s", institution_uuid
            )
            return {}

        try:
            data: Dict[str, Any] = response.json()
        except ValueError:
            logger.error("RAD-on impacts returned non-JSON response")
            return {}

        return data

    def iter_impacts_for_institution(
        self,
        institution_uuid: str,
        page_size: int = 50,
        timeout: float = 10.0,
    ) -> Iterable[ImpactCaseSchema]:
        """
        Generator zwracający kolejne ImpactCaseSchema dla jednej instytucji,
        identyfikowanej przez UUID (institutionUuid).

        Obsługuje paginację po polu 'token' w odpowiedzi RAD-on.
        """
        token = ""

        while True:
            raw = self.get_impact_description(
                institution_uuid=institution_uuid,
                result_numbers=page_size,
                token=token,
                timeout=timeout,
            )

            if not isinstance(raw, dict):
                break

            results = raw.get("results", []) or []
            if not results:
                break

            for r in results:
                if not isinstance(r, dict):
                    continue
                # Mapowanie surowego rekordu RAD-on na Twój model domenowy
                yield ImpactCaseSchema.from_radon_record(r)

            pagination = raw.get("pagination") or {}
            next_token = pagination.get("token") or ""
            if not next_token or next_token == token:
                break

            token = next_token


if __name__ == "__main__":
    # Prosty test ręczny – wstaw jakiś znany institutionUuid
    logging.basicConfig(level=logging.INFO)
    connector = RadonConnector()

    test_uuid = "511d4dfc-574e-4801-af14-e99dc24f8209"  # np. UW, jeśli taki masz
    data = connector.get_impact_description(institution_uuid=test_uuid, result_numbers=1)

    print("Klucze odpowiedzi impacts:", list(data.keys()))
    results = data.get("results") or []
    if results:
        first = results[0]
        print("Przykładowy surowy rekord impactu (pierwszy) – klucze:")
        print(first.keys())
