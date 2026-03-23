import logging
import time

import requests
import regex as re

import pathlib


from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict

from app.models import IdentifierSchema

class BaseConnector(ABC):
    
    """
    Abstract class for base connector which will be used later on in other, concrete connectors with existing 
    external services.
    
    BaseConnector class is implementing a set of base, abstract methods for data retrieval and parsing.

    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = api_key
        self.base_url = base_url
        
    
    @abstractmethod
    def search(self, query: str, top_k = 10, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        
        Abstract search method with with additional kwargs arguments that 
        may be extended by different connectors 

        Args:
            query (str): query string
            top_k (int, optional): The number of results to return. Defaults to 10.

        Returns:
            List[Dict[str, Any]]: List of results in the form of a dictionary of strings from the search query
        """
        pass
    @abstractmethod
    def search_by_id(self, id: IdentifierSchema, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Abstract method for searching external API by id of the document/entity 
        The id of the doc/entity is passed as an argument and is a class from identifiers.py file

        Args:
            id (IdentifierSchema): id of the document

        Returns:
            List[Dict[str, Any]]: List of results in the form of a dictionary of strings
        """
        pass
    
        
        