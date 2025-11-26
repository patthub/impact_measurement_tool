# app/connectors/radon.py
# Based on: https://github.com/OPI-PIB/Radon-api/blob/main/Radon_API_Basics_pl.ipynb

from __future__ import annotations

import logging
from typing import Any, Optional, Dict, Iterable

import requests
from requests import RequestException

from app.connectors.base import BaseConnector
from app.models import IdentifierSchema
from app.models import InstitutionEvaluationSchema
from app.models import ImpactCaseSchema, InstitutionImpactSetSchema



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
        Ogólny free-text search – tutaj na razie nieużywane.
        """
        raise NotImplementedError

    def search_by_id(self, identifier: IdentifierSchema, **kwargs: Any) -> list[dict]:
        """
        Wyszukiwanie rekordów po identyfikatorze – do doprecyzowania,
        gdy wybierzesz konkretną encję (employees, projects itd.).
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

    def get_impact_description(
        self,
        institutionName: str,
        result_numbers: int = 10,
        token: str = "",
        timeout: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Pobiera surowe dane z endpointu RAD-on:
        GET /polon/impacts?institutionName=...&resultNumbers=...&token=...

        Zwraca pełną odpowiedź JSON jako dict (klucze typu 'results', 'pagination', 'version').
        """

        url = f"{self.base_url.rstrip('/')}/polon/impacts"

        params: Dict[str, Any] = {
            "institutionName": institutionName,
            "resultNumbers": result_numbers,
        }
        if token:
            params["token"] = token

        try:
            response = requests.get(url, params=params, timeout=timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.exception(
                "Error calling RAD-on impacts for institution %s", institutionName
            )
            return {}

        try:
            data: Dict[str, Any] = response.json()
        except ValueError:
            logger.error("RAD-on impacts returned non-JSON response")
            return {}

        return data
    def get_first_impact_case(
        self,
        institution_name: str,
        result_numbers: int = 10,
        timeout: float = 10.0,
    ) -> Optional[ImpactCaseSchema]:
        """
        Pobiera impacty dla instytucji i zwraca pierwszy case
        zamieniony na ImpactCaseSchema.

        Jeśli nie ma wyników lub coś pójdzie nie tak, zwraca None.
        """
        raw = self.get_impact_description(
            institutionName=institution_name,
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

        return ImpactCaseSchema.from_radon_record(first)

    def get_all_impact_cases(
        self,
        institution_name: str,
        result_numbers: int = 10,
        timeout: float = 10.0,
    ) -> InstitutionImpactSetSchema:
        """
        Pobiera impacty dla instytucji i zwraca cały zestaw
        jako InstitutionImpactSetSchema.
        """
        raw = self.get_impact_description(
            institutionName=institution_name,
            result_numbers=result_numbers,
            timeout=timeout,
        )
        return InstitutionImpactSetSchema.from_radon_response(raw)
    def iter_impacts_for_institution(
        self,
        institution_name: str,
        page_size: int = 50,
        timeout: float = 10.0,
    ) -> Iterable[ImpactCaseSchema]:
        """
        Generator zwracający kolejne ImpactCaseSchema dla jednej instytucji,
        obsługujący paginację po polu 'token' w odpowiedzi RAD-on.
        """
        token = ""

        while True:
            raw = self.get_impact_description(
                institutionName=institution_name,
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
                yield ImpactCaseSchema.from_radon_record(r)

            pagination = raw.get("pagination") or {}
            next_token = pagination.get("token") or ""
            if not next_token or next_token == token:
                break

            token = next_token




