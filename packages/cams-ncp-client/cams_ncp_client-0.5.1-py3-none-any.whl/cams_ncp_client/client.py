from typing import Optional

import requests

from cams_ncp_client.cams_file import CamsFileClient
from cams_ncp_client.chimere_file import ChimereFileClient
from cams_ncp_client.ecmwf_file import EcmwfFileClient
from cams_ncp_client.forecast import ForecastClient
from cams_ncp_client.health import HealthClient
from cams_ncp_client.model import ModelClient
from cams_ncp_client.observation import ObservationClient
from cams_ncp_client.quantity import QuantityClient
from cams_ncp_client.station import StationClient


class CamsNcpApiClient:
    """
    Client for interacting with the CAMS NCP API.

    Attributes:
       base_url (str): The base URL for the API.
       session (requests.Session): Session for making HTTP requests.

    Example usage:

    >>>  from vito.sas.air.utils.date_utils import iso_utc_to_datetime
    >>>  client = CamsNcpApiClient(base_url="http://localhost:8080")
    >>>  quantities = client.quantity.get_quantities_df()
    >>>  stations = client.station.find_stations(limit=10, quantity="PM10")
    >>>  observations = client.observation.find_observations(station_name="42N016", start_time=iso_utc_to_datetime("2023-01-01T00:00:00Z"))
    """

    def __init__(self,
            base_url: str,
            session: Optional[requests.Session] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.session = session if session is not None else requests.Session()
        self._station = None
        self._quantity = None
        self._observation = None
        self._forecast = None
        self._model = None
        self._cams_file = None
        self._chimere_file = None
        self._ecmwf_file = None
        self._health = None

    @property
    def station(self) -> StationClient:
        if self._station is None:
            self._station = StationClient(self.base_url, self.session)
        return self._station

    @property
    def quantity(self) -> QuantityClient:
        if self._quantity is None:
            self._quantity = QuantityClient(self.base_url, self.session)
        return self._quantity

    @property
    def observation(self) -> ObservationClient:
        if self._observation is None:
            self._observation = ObservationClient(self.base_url, self.session)
        return self._observation

    @property
    def forecast(self) -> ForecastClient:
        if self._forecast is None:
            self._forecast = ForecastClient(self.base_url, self.session)
        return self._forecast

    @property
    def model(self) -> ModelClient:
        if self._model is None:
            self._model = ModelClient(self.base_url, self.session)
        return self._model

    @property
    def cams_file(self) -> CamsFileClient:
        if self._cams_file is None:
            self._cams_file = CamsFileClient(self.base_url, self.session)
        return self._cams_file


    @property
    def chimere_file(self) -> ChimereFileClient:
        if self._chimere_file is None:
            self._chimere_file = ChimereFileClient(self.base_url, self.session)
        return self._chimere_file


    @property
    def ecmwf_file(self) -> EcmwfFileClient:
        if self._ecmwf_file is None:
            self._ecmwf_file = EcmwfFileClient(self.base_url, self.session)
        return self._ecmwf_file


    @property
    def health(self) -> HealthClient:
        if self._health is None:
            self._health = HealthClient(self.base_url, self.session)
        return self._health


