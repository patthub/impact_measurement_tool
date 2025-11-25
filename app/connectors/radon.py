#Based on: https://github.com/OPI-PIB/Radon-api/blob/main/Radon_API_Basics_pl.ipynb

import requests

import logging

from .base import BaseConnector




logger = logging.getLogger(__name__)

class RadonConnector(BaseConnector):
    """
    API connector for Radon database
    Radon API source code and documentation: https://github.com/OPI-PIB/Radon-api/blob/main/Radon_API_Basics_pl.ipynb
    Args:
        BaseConnector (_type_): _description_
    """
# Podstawowe zapytanie do usługi pracownicy
response = requests.get("https://radon.nauka.gov.pl/opendata/polon/employees", params={'resultNumbers': 1})
print(response.json()['results'][0]['personalData'])




