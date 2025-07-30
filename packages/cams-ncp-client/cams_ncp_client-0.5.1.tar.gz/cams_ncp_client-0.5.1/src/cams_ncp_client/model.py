from typing import List, Optional

import pandas as pd

from cams_ncp_client._base import BaseClient
from cams_ncp_client.schemas.common import ForecastModel
from cams_ncp_client.schemas.common import TableData
from cams_ncp_client.utils.pandas_utils import to_dataframe


class ModelClient(BaseClient):
    """
    Client for managing forecast models.

    Example usage:

    >>> client = CamsNcpApiClient(base_url="http://localhost:8080")
    >>> model_client = client.observation
    >>> cams_models: TableData[ForecastModel] = model_client.find_models(model_type="CAMS")
    """

    def find_models(self, limit: int = 200, offset: int = 0, order_by: str = "name",
                    name: Optional[List[str] | str] = None,
                    description: Optional[List[str] | str] = None,
                    model_type: Optional[List[str] | str] = None,
                    ) -> TableData[ForecastModel]:
        """
        Find all forecast models matching the given filters and return as TableData.
        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            order_by: Field to order results by
            name: Filter by model name
            description: Filter by model description
            model_type: Filter by model type
        Returns:
            TableData object containing matching forecast models
        """
        params = {
            "limit": limit,
            "offset": offset,
            "order_by": order_by
        }
        if name is not None:
            params["name"] = name if isinstance(name, list) else [name]
        if description is not None:
            params["description"] = description if isinstance(description, list) else [description]
        if model_type is not None:
            params["model_type"] = model_type if isinstance(model_type, list) else [model_type]
        url = self._build_url_public_api( "model/")
        return self.parse_table_response(self._exec_get(url, params=params), ForecastModel)

    def find_models_df(self, limit: int = 200, max_pages: int = 100, order_by: str = "name",
                    name: Optional[List[str] | str] = None,
                    description: Optional[List[str] | str] = None,
                    model_type: Optional[List[str] | str] = None,
                    ) -> pd.DataFrame:
        """
        Find all forecast models matching the given filters and return as DataFrame.
        This is a convenience wrapper around find_models() that fetches all pages of results and returns them as a pandas DataFrame.
        Args:
            limit: Number of results per page request (affects API call efficiency)
            max_pages: Maximum number of pages to fetch, default is 100
            order_by: Field to order results by
            name: Filter by model name
            description: Filter by model description
            model_type: Filter by model type
        Returns:
            DataFrame containing all matching forecast models
        """
        return to_dataframe(
            find_method=self.find_models,
            limit=limit, max_pages=max_pages,
            order_by=order_by,
            name=name,
            description=description,
            model_type=model_type
        )

    def get_model_by_id(self, model_id: int) -> ForecastModel:
        """
        Get a forecast model by its ID.
        """
        url = self._build_url_public_api( "model/id", str(model_id))
        return self.parse_typed_response(self._exec_get(url), ForecastModel)

    def get_model_by_name(self, model_name: str) -> ForecastModel:
        """
        Get a forecast model by its name.
        """
        url = self._build_url_public_api( "model/name", model_name)
        return self.parse_typed_response(self._exec_get(url), ForecastModel)

    def create_model(self, model_data: ForecastModel) -> ForecastModel:
        """
        Create a new forecast model.
        """
        url = self._build_url_private_api( "model/")
        return self.parse_typed_response(self._exec_post(url, json=model_data.model_dump(mode="json")), ForecastModel)

    def update_model(self, model_data: ForecastModel) -> ForecastModel:
        """
        Update an existing forecast model.
        Args:
            model_data: ForecastModel object with updated data
        Returns:
            The updated ForecastModel object
        """
        url = self._build_url_private_api( "model/")
        return self.parse_typed_response(self._exec_put(url, json=model_data.model_dump(mode="json")), ForecastModel)

    def delete_model(self, model_id: int) -> ForecastModel:
        """
        Delete a forecast model by its ID.
        Args:
            model_id: ID of the forecast model to delete
        Returns:
            The deleted ForecastModel object
        """
        url = self._build_url_private_api( "model/id", str(model_id))
        return self.parse_typed_response(self._exec_delete(url), ForecastModel)