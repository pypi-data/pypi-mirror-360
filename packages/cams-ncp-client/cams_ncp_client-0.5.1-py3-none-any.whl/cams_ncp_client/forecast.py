from datetime import datetime, date
from typing import List, Optional
from typing import Literal

import pandas as pd
from vito.sas.air.utils.date_utils import to_utc_iso

from cams_ncp_client._base import BaseClient
from cams_ncp_client.schemas.common import Aggregation
from cams_ncp_client.schemas.common import ForecastHourly, ForecastAgg
from cams_ncp_client.schemas.common import TableData
from cams_ncp_client.utils.pandas_utils import to_dataframe


class ForecastClient(BaseClient):
    """
    Client for managing forecasts.

    Example usage:

    >>> client = CamsNcpApiClient(base_url="http://localhost:8080")
    >>> forecast_client = client.forecast
    >>> mos_forecast_hourly_df: pd.DataFrame = forecast_client.find_forecasts_df(quantity_name="PM25", model_name="MOS", base_time_start=datetime(2025, 4, 1), horizon_days=[1, 2])
    """

    def find_forecasts(self, limit: int = 200, offset: int = 0, order_by: str = "forecast_time",
                       station_name: Optional[List[str] | str] = None,
                       quantity_name: Optional[List[str] | str] = None,
                       model_name: Optional[List[str] | str] = None,
                       base_time_start: Optional[datetime] = None,
                       base_time_end: Optional[datetime] = None,
                       forecast_time_start: Optional[date] = None,
                       forecast_time_end: Optional[date] = None,
                       horizon_days: Optional[List[int] | int] = None
                       ) -> TableData[ForecastHourly]:
        """
        Find all forecasts matching the given filters and return as TableData.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            order_by: Field to order results by
            station_name: Filter by station name
            quantity_name: Filter by quantity name
            model_name: Filter by model name
            base_time_start: Start time for filtering
            base_time_end: End time for filtering
            forecast_time_start: Start date for filtering
            forecast_time_end: End date for filtering
            horizon_days: Filter by horizon days

        Returns:
            TableData object containing matching forecasts
        """
        params = {
            "limit": limit,
            "offset": offset,
            "order_by": order_by
        }

        if station_name is not None:
            params["station_name"] = station_name if isinstance(station_name, list) else [station_name]
        if quantity_name is not None:
            params["quantity_name"] = quantity_name if isinstance(quantity_name, list) else [quantity_name]
        if model_name is not None:
            params["model_name"] = model_name if isinstance(model_name, list) else [model_name]

        if base_time_start is not None:
            params["base_time_start"] = to_utc_iso(base_time_start)
        if base_time_end is not None:
            params["base_time_end"] = to_utc_iso(base_time_end)
        if forecast_time_start is not None:
            params["forecast_time_start"] = forecast_time_start.isoformat()
        if forecast_time_end is not None:
            params["forecast_time_end"] = forecast_time_end.isoformat()

        if horizon_days is not None:
            params["horizon_days"] = horizon_days if isinstance(horizon_days, list) else [horizon_days]

        url = self._build_url_public_api("forecast")

        return self.parse_table_response(self._exec_get(url, params=params), ForecastHourly)

    def find_forecasts_df(self, limit: int = 200, max_pages: int = 100, order_by: str = "forecast_time",
                       station_name: Optional[List[str] | str] = None,
                       quantity_name: Optional[List[str] | str] = None,
                       model_name: Optional[List[str] | str] = None,
                       base_time_start: Optional[datetime] = None,
                       base_time_end: Optional[datetime] = None,
                       forecast_time_start: Optional[date] = None,
                       forecast_time_end: Optional[date] = None,
                       horizon_days: Optional[List[int] | int] = None
                       ) -> pd.DataFrame:
        """
        Find all forecasts matching the given filters and return as DataFrame.
        This is a convenience wrapper around find_forecasts() that fetches all pages of results and returns them as a pandas DataFrame.

        Args:
            limit: Number of results per page request (affects API call efficiency)
            max_pages: Maximum number of pages to fetch
            order_by: Field to order results by
            station_name: Filter by station name
            quantity_name: Filter by quantity name
            model_name: Filter by model name
            base_time_start: Start time for filtering
            base_time_end: End time for filtering
            forecast_time_start: Start date for filtering
            forecast_time_end: End date for filtering
            horizon_days: Filter by horizon days

        Returns:
            DataFrame containing all matching forecasts
        """
        return to_dataframe(
            find_method=self.find_forecasts,
            limit=limit, max_pages=max_pages,
            order_by=order_by,
            station_name=station_name,
            quantity_name=quantity_name,
            model_name=model_name,
            base_time_start=base_time_start,
            base_time_end=base_time_end,
            forecast_time_start=forecast_time_start,
            forecast_time_end=forecast_time_end,
            horizon_days=horizon_days)

    def find_forecasts_agg(self, limit: int = 200, offset: int = 0, order_by: str = "forecast_time",
                              aggregation: Literal["da", "m1", "m8"] = "da",
                              station_name: Optional[List[str] | str] = None,
                              quantity_name: Optional[List[str] | str] = None,
                              model_name: Optional[List[str] | str] = None,
                              base_time_start: Optional[datetime] = None,
                              base_time_end: Optional[datetime] = None,
                              forecast_time_start: Optional[date] = None,
                              forecast_time_end: Optional[date] = None,
                              horizon_days: Optional[List[int] | int] = None,
                              refresh_view: Optional[bool] = False,
                              ) -> TableData[ForecastAgg]:
        """
        Find all aggregated forecasts matching the given filters and return as TableData.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            order_by: Field to order results by
            aggregation: Aggregation type (e.g., "da", "m1", "m8")
            station_name: Filter by station name
            quantity_name: Filter by quantity name
            model_name: Filter by model name
            base_time_start: Start time for filtering
            base_time_end: End time for filtering
            forecast_time_start: Start date for filtering
            forecast_time_end: End date for filtering
            horizon_days: Filter by horizon days
            refresh_view: bool. If True, refresh the DB view before returning the data (default is False)

        Returns:
            TableData object containing matching aggregated forecasts
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
        if model_name is not None:
            params["model_name"] = model_name if isinstance(model_name, list) else [model_name]

        if base_time_start is not None:
            params["base_time_start"] = to_utc_iso(base_time_start)
        if base_time_end is not None:
            params["base_time_end"] = to_utc_iso(base_time_end)
        if forecast_time_start is not None:
            params["forecast_time_start"] = forecast_time_start.isoformat()
        if forecast_time_end is not None:
            params["forecast_time_end"] = forecast_time_end.isoformat()

        if horizon_days is not None:
            params["horizon_days"] = horizon_days if isinstance(horizon_days, list) else [horizon_days]
        if refresh_view is not None:
            params["refresh_view"] = refresh_view

        url = self._build_url_public_api( "forecast/aggregated")
        return self.parse_table_response(self._exec_get(url, params=params), ForecastAgg)

    def find_forecasts_agg_df(self, limit: int = 200, max_pages: int = 100, order_by: str = "forecast_time",
                              aggregation: Aggregation = Aggregation.DA,
                              station_name: Optional[List[str] | str] = None,
                              quantity_name: Optional[List[str] | str] = None,
                              model_name: Optional[List[str] | str] = None,
                              base_time_start: Optional[datetime] = None,
                              base_time_end: Optional[datetime] = None,
                              forecast_time_start: Optional[date] = None,
                              forecast_time_end: Optional[date] = None,
                              horizon_days: Optional[List[int] | int] = None,
                              refresh_view: Optional[bool] = False
                              ) -> pd.DataFrame:
        """
        Find all aggregated forecasts matching the given filters and return as DataFrame.
        This is a convenience wrapper around find_forecasts_agg() that fetches all pages of results and returns them as a pandas DataFrame.

        Args:
            limit: Number of results per page request (affects API call efficiency)
            max_pages: Maximum number of pages to fetch (default is 100)
            order_by: Field to order results by
            aggregation: Aggregation type (e.g., "da", "m1", "m8")
            station_name: Filter by station name
            quantity_name: Filter by quantity name
            model_name: Filter by model name
            base_time_start: Start time for filtering
            base_time_end: End time for filtering
            forecast_time_start: Start date for filtering
            forecast_time_end: End date for filtering
            horizon_days: Filter by horizon days
            refresh_view: bool. If True, refresh the DB view before returning the data (default is False)
        Returns:
            DataFrame containing all matching aggregated forecasts
        """
        return to_dataframe(
            find_method=self.find_forecasts_agg,
            limit=limit, max_pages=max_pages,
            order_by=order_by,
            aggregation=aggregation,
            station_name=station_name,
            quantity_name=quantity_name,
            model_name=model_name,
            base_time_start=base_time_start,
            base_time_end=base_time_end,
            forecast_time_start=forecast_time_start,
            forecast_time_end=forecast_time_end,
            horizon_days=horizon_days,
            refresh_view=refresh_view
        )

    def create_forecast(self, forecast_data: ForecastHourly) -> ForecastHourly:
        """
        Create a new forecast.
        """
        url = self._build_url_private_api( "forecast/")
        return self.parse_typed_response(self._exec_post(url, json=forecast_data.model_dump(mode="json")), ForecastHourly)

    def create_forecasts(self, forecast_data: List[ForecastHourly]) -> List[ForecastHourly]:
        """
        Create multiple forecasts in bulk.

        Args:
            forecast_data: List of ForecastHourly objects to create

        Returns:
            List of created ForecastHourly objects
        """
        url = self._build_url_private_api( "forecast/bulk")
        response = self._exec_post(url, json=[fc.model_dump(mode="json") for fc in forecast_data])
        return_list = self.parse_list_response(response, ForecastHourly)
        return sorted(return_list, key=lambda x: x.forecast_time)

    def create_forecasts_upsert_only(self, forecast_data: List[ForecastHourly]) -> bool:
        """
        Create multiple forecasts in bulk.

        Args:
            forecast_data: List of ForecastHourly objects to create

        Returns:
            True if more than 0 forecasts were upserted, False otherwise
        """
        url = self._build_url_private_api("forecast/bulk_upsert_only")
        response = self._exec_post(url, json=[fc.model_dump(mode="json") for fc in forecast_data])
        return self.parse_typed_response(response, bool)

    def create_forecasts_agg(self, forecast_data: List[ForecastAgg]) -> List[ForecastAgg]:
        """
        Create multiple daily forecasts in bulk.
        Args:
            forecast_data: List of ForecastAgg objects to create

        Returns:
            List of created ForecastAgg objects
        """
        url = self._build_url_private_api("forecast/aggregated/bulk")
        response = self._exec_post(url, json=[fc.model_dump(mode="json") for fc in forecast_data])
        return_list = self.parse_list_response(response, ForecastAgg)
        return sorted(return_list, key=lambda x: x.forecast_time)

    def delete_forecast(self, forecast_id: int) -> ForecastHourly:
        """
        Delete a forecast by its ID.

        Args:
            forecast_id: ID of the forecast to delete

        Returns:
            The deleted ForecastHourly object
        """
        url = self._build_url_private_api( f"forecast/{forecast_id}")
        return self.parse_typed_response(self._exec_delete(url), ForecastHourly)

    def update_aggregations(self) -> dict:
        """
        Update all forecast aggregation views in the database.
        """
        url = self._build_url_private_api("forecast/update_aggregations")
        return self.parse_typed_response(self._exec_post(url), dict)
