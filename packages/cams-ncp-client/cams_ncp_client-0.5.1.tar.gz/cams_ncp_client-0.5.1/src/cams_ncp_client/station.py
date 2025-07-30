from typing import List, Optional

import pandas as pd

from cams_ncp_client._base import BaseClient
from cams_ncp_client.schemas.common import MeasuringStation, TableData
from cams_ncp_client.utils.pandas_utils import to_dataframe


class StationClient(BaseClient):
    """
    Client for managing measuring stations.

    Example usage:

    >>> client = CamsNcpApiClient(base_url="http://localhost:8080")
    >>> station_client = client.station
    >>> stations_pm25: TableData[MeasuringStation] = station_client.find_stations(quantity="PM25")
    """

    def get_station_by_id(self, station_id: int) -> MeasuringStation:
        """
        Get a measuring station by its ID.

        Args:
            station_id: ID of the station to retrieve

        Returns:
            The MeasuringStation object with the given ID
        """
        url = self._build_url_public_api( "station/id", str(station_id))
        return self.parse_typed_response(self._exec_get(url), MeasuringStation)

    def get_station_by_name(self, station_name: str) -> MeasuringStation:
        """
        Get a measuring station by its name.

        Args:
            station_name: Name of the station to retrieve

        Returns:
            The MeasuringStation object with the given name
        """
        url = self._build_url_public_api( "station/name", station_name)
        return self.parse_typed_response(self._exec_get(url), MeasuringStation)

    def find_stations(self, limit: int = 200, offset: int = 0, order_by: str = "name",
                    quantity: Optional[List[str] | str] = None,
                    name: Optional[List[str] | str] = None,
                    eoi_code: Optional[List[str] | str ] = None,
                    station_type: Optional[List[str] | str] = None,
                    area_type: Optional[List[str] | str] = None
            ) -> TableData[MeasuringStation]:
        """
        Find measuring stations with the given filters.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            order_by: Field to order results by
            quantity: Filter by quantity measured
            name: Filter by station name
            eoi_code: Filter by EOI code
            station_type: Filter by station type
            area_type: Filter by area type

        Returns:
            TableData object containing matching stations``
        """
        params = {
            "limit": limit,
            "offset": offset,
            "order_by": order_by
        }
        if quantity is not None:
            params["quantity"] = quantity if isinstance(quantity, list) else [quantity]
        if name is not None:
            params["name"] = name if isinstance(name, list) else [name]
        if eoi_code is not None:
            params["eoi_code"] = eoi_code if isinstance(eoi_code, list) else [eoi_code]
        if station_type is not None:
            params["station_type"] = station_type if isinstance(station_type, list) else [station_type]
        if area_type is not None:
            params["area_type"] = area_type if isinstance(area_type, list) else [area_type]
        url = self._build_url_public_api( "station/")
        return self.parse_table_response(self._exec_get(url, params=params), MeasuringStation)


    def find_stations_df(self, order_by: str = "name",
                         quantity: Optional[List[str] | str] = None,
                         name: Optional[List[str] | str] = None,
                         eoi_code: Optional[List[str] | str] = None,
                         station_type: Optional[List[str] | str] = None,
                         area_type: Optional[List[str] | str] = None,
                         limit: int = 200, max_pages: int = 100
    ) -> pd.DataFrame:
        """
        Find all measuring stations matching the given filters and return as DataFrame.

        This is a convenience wrapper around find_stations() that fetches all pages
        of results and returns them as a pandas DataFrame.

        Args:
            order_by: Field to order results by
            quantity: Filter by quantity measured
            name: Filter by station name
            eoi_code: Filter by EOI code
            station_type: Filter by station type
            area_type: Filter by area type
            limit: Number of results per page (affects API call efficiency)
            max_pages: Maximum number of pages to fetch, default is 100

        Returns:
            DataFrame containing all matching stations
        """
        return to_dataframe(
            find_method=self.find_stations,
            order_by=order_by,
            quantity=quantity,
            name=name,
            eoi_code=eoi_code,
            station_type=station_type,
            area_type=area_type,
            limit=limit, max_pages=max_pages
        )


    def create_station(self, station_data: MeasuringStation) -> MeasuringStation:
        """
        Create a new measuring station.

        Args:
            station_data: The MeasuringStation object to create

        Returns:
            The created MeasuringStation object
        """
        url = self._build_url_private_api( "station/")
        return self.parse_typed_response(self._exec_post(url, json=station_data.model_dump(mode="json")), MeasuringStation)

    def update_station(self, station_data: MeasuringStation) -> MeasuringStation:
        """
        Update an existing measuring station.

        Args:
            station_data: The MeasuringStation object to update

        Returns:
            The updated MeasuringStation object
        """
        url = self._build_url_private_api( "station/")
        return self.parse_typed_response(self._exec_put(url, json=station_data.model_dump(mode="json")), MeasuringStation)

    def delete_station(self, station_id: int) -> MeasuringStation:
        """
        Delete a measuring station by its ID.

        Args:
            station_id: ID of the station to delete

        Returns:
            The deleted MeasuringStation object
        """
        url = self._build_url_private_api( "station/id", str(station_id))
        return self.parse_typed_response(self._exec_delete(url), MeasuringStation)