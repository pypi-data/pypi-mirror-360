from http import HTTPStatus
from typing import List, Optional, Type, TypeVar, Final, Dict

import requests
from vito.sas.air import logger
from vito.sas.air.api_client import RESTclient

from cams_ncp_client.schemas.common import TableData

API_V1: Final[str] = "api/v1"
# PRIVATE_API_V1: Final[str] = "private/v1"
PRIVATE_API_V1: Final[str] = "api/protected/v1"

T = TypeVar('T')


class BaseClient(RESTclient):
    """
    Base client for the CAMS NCP API.
    This class provides methods to build URLs for public and private APIs,
    and to parse responses into specified models.
    It inherits from the RESTclient class, which handles HTTP requests.

    Attributes:
        base_url (str): The base URL for the API.
        session (requests.Session): Session for making HTTP requests.
    """

    def __init__(self, base_url: str, session: Optional[requests.Session] = None):
        super().__init__(base_url, session)

    def _build_url_public_api(self, *parts: str) -> str:
        return self._build_url(API_V1, *parts)

    def _build_url_private_api(self, *parts: str) -> str:
        # Authorization
        return self._build_url(PRIVATE_API_V1, *parts)

    def _base_headers(self) -> Dict[str, str]:
        # call super _base_headers()
        base_headers: dict = super()._base_headers()
        base_headers["Authorization"] = "Bearer TEST_TOKEN_gZ1xB9rT5mQwKa7jYcVN4dPu"
        return base_headers

    def parse_typed_response(self, response: requests.Response, model: Type[T]) -> T:
        """
        Parses a single response into the specified model.
        """
        try:
            if response.status_code >= HTTPStatus.BAD_REQUEST:
                logger.exception(response.text)
            response.raise_for_status()
            response_object = response.json()

            if isinstance(response_object, model):
                return response_object
            return model(**response_object)
        except requests.RequestException as e:
            logger.error(f"HTTP error: {e} | URL: {response.url}")
            raise
        except Exception as e:
            logger.error(f"Response parsing failed: {e} | Response: {response.text}")
            raise

    def parse_table_response(self, response: requests.Response, model: Type[T]) -> TableData[T]:
        """
        Parses a response into a TableData object (of the specified model type)
        """
        try:
            if response.status_code >= HTTPStatus.BAD_REQUEST:
                logger.exception(response.text)
            response.raise_for_status()
            response_json = response.json()

            data = [model(**item) for item in response_json.get("data", [])]
            offset = response_json.get("offset", 0)
            limit = response_json.get("limit", len(data))
            total = response_json.get("total", len(data))

            return TableData(
                data=data,
                offset=offset,
                limit=limit,
                total=total
            )
        except requests.RequestException as e:
            logger.error(f"HTTP error: {e} | URL: {response.url}")
            raise
        except Exception as e:
            logger.error(f"List response parsing failed: {e} | Response: {response.text}")
            raise

    def parse_list_response(self, response: requests.Response, model: Type[T]) -> List[T]:
        """
        Parses a list response into a List of the specified model.
        """
        try:
            if response.status_code >= HTTPStatus.BAD_REQUEST:
                logger.exception(response.text)
            response.raise_for_status()
            return [model(**item) for item in response.json()]
        except requests.RequestException as e:
            logger.error(f"HTTP error: {e} | URL: {response.url}")
            raise
        except Exception as e:
            logger.error(f"List response parsing failed: {e} | Response: {response.text}")
            raise
