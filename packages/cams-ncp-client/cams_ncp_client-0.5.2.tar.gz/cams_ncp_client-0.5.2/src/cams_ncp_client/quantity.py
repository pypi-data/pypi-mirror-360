from typing import List

import pandas as pd

from cams_ncp_client._base import BaseClient
from cams_ncp_client.schemas.common import Quantity
from cams_ncp_client.utils.pandas_utils import pydantic_data_to_dataframe


class QuantityClient(BaseClient):
    """
    Client for managing quantities (pollutants).

    Example usage:

    >>> client = CamsNcpApiClient(base_url="http://localhost:8080")
    >>> quantity_client = client.quantity
    >>> quantities: List[Quantity] = quantity_client.get_quantities()
    """

    def get_quantities(self) -> List[Quantity]:
        """
        Returns:
            List of all the Quantity objects in the database.
        """
        url = self._build_url_public_api( "quantity/")
        return self.parse_list_response(self._exec_get(url, params={}), Quantity)

    def get_quantities_df(self) -> pd.DataFrame:
        """
        Returns:
            Pandas DataFrame with all the Quantity objects in the database.
        """
        return pydantic_data_to_dataframe(self.get_quantities())

    # def get_quantities(self, limit: int = 200, offset: int = 0, order_by: str = "name") -> List[Quantity]:
    #     """
    #     Get a list of quantities with optional pagination and ordering.
    #     Args:
    #         limit: Maximum number of results to return
    #         offset: Number of results to skip
    #         order_by: Field to order results by
    #     """
    #     params = {
    #         "limit": limit,
    #         "offset": offset,
    #         "order_by": order_by
    #     }
    #     url = self._build_url_public_api( "quantity/")
    #     return self.parse_list_response(self._exec_get(url, params=params), Quantity)

    def get_quantity_by_name(self, quantity_name: str) -> Quantity:
        """
        Get a quantity by its name.

        Args:
            quantity_name: Name of the quantity to retrieve

        Returns:
            The Quantity object with the specified name
        """
        url = self._build_url_public_api( "quantity/name", quantity_name)
        return self.parse_typed_response(self._exec_get(url), Quantity)

    def create_quantity(self, quantity_data: Quantity) -> Quantity:
        """
        Create a new quantity.

        Args:
            quantity_data: Quantity object to create

        Returns:
            The created Quantity object
        """
        url = self._build_url_private_api( "quantity/")
        return self.parse_typed_response(self._exec_post(url, json=quantity_data.model_dump(mode="json")), Quantity)

    def upsert_quantity(self, quantity_data: Quantity) -> Quantity:
        """
        Create or update a quantity.
        Args:
            quantity_data: Quantity object to create or update

        Returns:
            The created or updated Quantity object
        """
        url = self._build_url_private_api( "quantity/")
        return self.parse_typed_response(self._exec_put(url, json=quantity_data.model_dump(mode="json")), Quantity)

    def delete_quantity(self, quantity_id: int) -> Quantity:
        """
        Delete a quantity by its ID.

        Args:
            quantity_id: ID of the quantity to delete

        Returns:
            The deleted Quantity object
        """
        url = self._build_url_private_api( "quantity/id", str(quantity_id))
        return self.parse_typed_response(self._exec_delete(url), Quantity)