from datetime import date, datetime
from typing import List, Optional

import pandas as pd
from vito.sas.air.utils.date_utils import to_utc_iso

from cams_ncp_client._base import BaseClient
from cams_ncp_client.schemas.common import Aggregation, ObservationAgg, ObservationHourly, TableData
from cams_ncp_client.utils.pandas_utils import to_dataframe


class ObservationClient(BaseClient):
    """
    Client for managing observation data.

    Example usage:
    >>> from cams_ncp_client.client import CamsNcpApiClient
    >>>
    >>> client = CamsNcpApiClient(base_url="http://localhost:8080")
    >>> observation_client = client.observation
    >>> observations_df: pd.DataFrame = observation_client.find_observations_df(limit=50, station_name="40SA04", quantity_name=["PM10", "PM25"], start_time=datetime(2025, 1, 1))
    """

    def find_observations(self, limit: int = 200, offset: int = 0, order_by: str = "result_time",
                          station_name: Optional[List[str] | str] = None, quantity_name: Optional[List[str] | str] = None,
                          start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
                          ) -> TableData[ObservationHourly]:
        params = {
            "limit": limit,
            "offset": offset,
            "order_by": order_by
        }
        if station_name is not None:
            params["station_name"] = station_name if isinstance(station_name, list) else [station_name]
        if quantity_name is not None:
            params["quantity_name"] = quantity_name if isinstance(quantity_name, list) else [quantity_name]

        if start_time is not None:
            params["start_time"] = to_utc_iso(start_time)
        if end_time is not None:
            params["end_time"] = to_utc_iso(end_time)

        url = self._build_url_public_api( "observation/")
        return self.parse_table_response(self._exec_get(url, params=params), ObservationHourly)


    def find_observations_df(self, order_by: str = "result_time",
                        station_name: Optional[List[str] | str] = None,
                        quantity_name: Optional[List[str] | str] = None,
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        limit: int = 200, max_pages: int = 100) -> pd.DataFrame:
        """
        Find all observations matching the given filters and return as DataFrame.
        This is a convenience wrapper around find_observations() that fetches all pages of results and returns them as a pandas DataFrame.
        Args:
            order_by: Field to order results by
            station_name: Filter by station name
            quantity_name: Filter by quantity name
            start_time: Start time for filtering
            end_time: End time for filtering
            limit: Number of results per page (affects API call efficiency), default is 200
            max_pages: Maximum number of pages to fetch, default is 100
        Returns:
            DataFrame containing all matching observations
        """
        return to_dataframe(
            find_method=self.find_observations,
            limit=limit, max_pages=max_pages,
            order_by=order_by,
            station_name=station_name,
            quantity_name=quantity_name,
            start_time=start_time,
            end_time=end_time)


    def find_observations_agg(self, limit: int = 200, offset: int = 0, order_by: str = "result_time",
                              aggregation: Aggregation = Aggregation.DA,
                              station_name: Optional[List[str] | str] = None,
                              quantity_name: Optional[List[str] | str] = None,
                              start_date: Optional[date] = None, end_date: Optional[date] = None,
                              refresh_view: Optional[bool] = False,
                              ) -> TableData[ObservationAgg]:
        """
        Find all aggregated observations matching the given filters and return as TableData.
        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            order_by: Field to order results by
            aggregation: Aggregation type (e.g., "da", "m1", "m8")
            station_name: Filter by station name
            quantity_name: Filter by quantity name
            start_date: Start date for filtering
            end_date: End date for filtering
            refresh_view: If True, refresh the DB view before returning the data (default is False)
        Returns:
            TableData object containing matching aggregated observations
        """
        params = {
            "limit": limit,
            "offset": offset,
            "order_by": order_by,
            "aggregation": aggregation
        }

        if station_name is not None:
            params["station_name"] = station_name if isinstance(station_name, list) else [station_name]
        if quantity_name is not None:
            params["quantity_name"] = quantity_name if isinstance(quantity_name, list) else [quantity_name]

        if start_date is not None:
            params["start_date"] = start_date.isoformat()
        if end_date is not None:
            params["end_time"] = end_date.isoformat()

        url = self._build_url_public_api("observation/aggregated")
        return self.parse_table_response(self._exec_get(url, params=params), ObservationAgg)

    def find_observations_agg_df(self, order_by: str = "result_time",
                            limit: int = 200, max_pages: int = 100,
                            aggregation: Aggregation = Aggregation.DA,
                            station_name: Optional[List[str] | str] = None,
                            quantity_name: Optional[List[str] | str] = None,
                            start_date: Optional[date] = None,
                            end_date: Optional[date] = None,
                            refresh_view: Optional[bool] = False
                            ) -> pd.DataFrame:
        """
        Find all aggregated observations matching the given filters and return as DataFrame.
        This is a convenience wrapper around find_observations_agg() that fetches all pages of results and returns them as a pandas DataFrame.
        Args:
            limit: Number of results per page request (affects API call efficiency)
            max_pages: Maximum number of pages to fetch, default is 100
            order_by: Field to order results by
            aggregation: Aggregation type (e.g., "da", "m1", "m8")
            station_name: Filter by station name
            quantity_name: Filter by quantity name
            start_date: Start date for filtering
            end_date: End date for filtering
        Returns:
            DataFrame containing all matching observations
        """
        return to_dataframe(
            find_method=self.find_observations_agg,
            limit=limit, max_pages=max_pages,
            order_by=order_by,
            aggregation=aggregation,
            station_name=station_name,
            quantity_name=quantity_name,
            start_date=start_date,
            end_date=end_date,
            refresh_view=refresh_view)


    def create_observation(self, observation_data: ObservationHourly) -> ObservationHourly:
        """
        Create a new observation.
        """
        url = self._build_url_private_api("observation/")
        return self.parse_typed_response(self._exec_post(url, json=observation_data.model_dump(mode="json")), ObservationHourly)

    def create_observations(self, observation_data: List[ObservationHourly]) -> List[ObservationHourly]:
        """
        Create multiple observations in bulk.
        """
        url = self._build_url_private_api("observation/bulk")


        response = self._exec_post(url, json=[obs.model_dump(mode="json") for obs in observation_data])
        return_list = self.parse_list_response(response, ObservationHourly)
        # order by result_time
        return sorted(return_list, key=lambda x: x.result_time)

    def update_aggregations(self) -> dict:
        """
        Update all observation aggregation views in the database.
        """
        url = self._build_url_private_api("observation/update_aggregations")
        return self.parse_typed_response(self._exec_post(url), dict)
